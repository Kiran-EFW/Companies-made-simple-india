"""Performance and workload service — team metrics, leaderboard, workload balancing."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from src.models.user import User, UserRole
from src.models.filing_task import FilingTask, FilingTaskStatus
from src.models.verification_queue import VerificationQueue, VerificationDecision
from src.models.escalation_rule import EscalationLog

logger = logging.getLogger(__name__)

# Statuses considered "active" for workload calculations
_ACTIVE_STATUSES = [
    FilingTaskStatus.ASSIGNED,
    FilingTaskStatus.IN_PROGRESS,
    FilingTaskStatus.WAITING_ON_CLIENT,
    FilingTaskStatus.WAITING_ON_GOVERNMENT,
    FilingTaskStatus.UNDER_REVIEW,
]


class PerformanceService:
    """Calculates workload, performance metrics, and team stats."""

    def get_team_workload(self, db: Session) -> Dict[str, Any]:
        """Get per-user workload breakdown for all staff.

        Uses aggregated queries instead of per-user loops to avoid N+1 problems.
        Replaces 4*N+1 queries with 3 queries (staff, task counts, review counts).
        """
        staff = (
            db.query(User)
            .filter(User.role != UserRole.USER, User.is_active == True)
            .all()
        )

        now = datetime.now(timezone.utc)

        # Single aggregated query for all task counts grouped by assigned_to
        task_counts = (
            db.query(
                FilingTask.assigned_to,
                func.count(case(
                    (FilingTask.status.in_(_ACTIVE_STATUSES), 1)
                )).label("active"),
                func.count(case(
                    (FilingTask.status == FilingTaskStatus.COMPLETED, 1)
                )).label("completed"),
                func.count(case(
                    (and_(
                        FilingTask.due_date != None,
                        FilingTask.due_date < now,
                        FilingTask.status.notin_([
                            FilingTaskStatus.COMPLETED,
                            FilingTaskStatus.CANCELLED,
                        ]),
                    ), 1)
                )).label("overdue"),
            )
            .filter(FilingTask.assigned_to.isnot(None))
            .group_by(FilingTask.assigned_to)
            .all()
        )

        # Build lookup dicts from aggregated results
        task_map: Dict[int, Dict[str, int]] = {}
        for row in task_counts:
            task_map[row.assigned_to] = {
                "active": row.active,
                "completed": row.completed,
                "overdue": row.overdue,
            }

        # Single aggregated query for pending review counts grouped by reviewer
        review_counts = (
            db.query(
                VerificationQueue.reviewer_id,
                func.count().label("pending"),
            )
            .filter(
                VerificationQueue.decision == VerificationDecision.PENDING,
                VerificationQueue.reviewer_id.isnot(None),
            )
            .group_by(VerificationQueue.reviewer_id)
            .all()
        )

        review_map: Dict[int, int] = {row.reviewer_id: row.pending for row in review_counts}

        # Assemble results from lookup dicts (no extra queries)
        team = []
        total_active = 0
        total_overdue = 0

        for user in staff:
            counts = task_map.get(user.id, {"active": 0, "completed": 0, "overdue": 0})
            pending_reviews = review_map.get(user.id, 0)

            dept = user.department.value if user.department else None
            sen = user.seniority.value if user.seniority else None

            team.append({
                "user_id": user.id,
                "user_name": user.full_name,
                "department": dept,
                "seniority": sen,
                "active_tasks": counts["active"],
                "completed_tasks": counts["completed"],
                "overdue_tasks": counts["overdue"],
                "pending_reviews": pending_reviews,
            })

            total_active += counts["active"]
            total_overdue += counts["overdue"]

        unassigned = (
            db.query(FilingTask)
            .filter(FilingTask.status == FilingTaskStatus.UNASSIGNED)
            .count()
        )

        return {
            "team": team,
            "unassigned_tasks": unassigned,
            "total_active": total_active,
            "total_overdue": total_overdue,
        }

    def get_user_metrics(
        self,
        db: Session,
        user_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get performance metrics for a specific user over a period."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Tasks completed in period
        completed_tasks = (
            db.query(FilingTask)
            .filter(
                FilingTask.assigned_to == user_id,
                FilingTask.status == FilingTaskStatus.COMPLETED,
                FilingTask.completed_at != None,
                FilingTask.completed_at >= since,
            )
            .all()
        )

        tasks_completed = len(completed_tasks)

        # Average turnaround (assigned_at -> completed_at)
        turnaround_hours = []
        sla_met = 0
        for t in completed_tasks:
            if t.assigned_at and t.completed_at:
                delta = (t.completed_at - t.assigned_at).total_seconds() / 3600.0
                turnaround_hours.append(delta)
                if t.due_date and t.completed_at <= t.due_date:
                    sla_met += 1

        avg_turnaround = (
            sum(turnaround_hours) / len(turnaround_hours) if turnaround_hours else 0.0
        )
        sla_pct = (sla_met / tasks_completed * 100.0) if tasks_completed > 0 else 100.0

        # Docs reviewed in period
        docs_reviewed = (
            db.query(VerificationQueue)
            .filter(
                VerificationQueue.reviewer_id == user_id,
                VerificationQueue.reviewed_at != None,
                VerificationQueue.reviewed_at >= since,
            )
            .count()
        )

        # Escalations
        escalations_received = (
            db.query(EscalationLog)
            .filter(
                EscalationLog.escalated_to_user_id == user_id,
                EscalationLog.created_at >= since,
            )
            .count()
        )
        escalations_resolved = (
            db.query(EscalationLog)
            .filter(
                EscalationLog.resolved_by == user_id,
                EscalationLog.resolved_at != None,
                EscalationLog.resolved_at >= since,
            )
            .count()
        )

        return {
            "user_id": user_id,
            "user_name": user.full_name,
            "period": f"last_{days}_days",
            "tasks_completed": tasks_completed,
            "avg_turnaround_hours": round(avg_turnaround, 1),
            "sla_compliance_pct": round(sla_pct, 1),
            "documents_reviewed": docs_reviewed,
            "escalations_received": escalations_received,
            "escalations_resolved": escalations_resolved,
        }

    def get_all_staff_metrics(
        self,
        db: Session,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get performance metrics for all staff members.

        Uses batch-aggregated queries instead of calling get_user_metrics per user,
        reducing N*5 queries down to 5 total queries.
        """
        staff = (
            db.query(User)
            .filter(User.role != UserRole.USER, User.is_active == True)
            .all()
        )
        if not staff:
            return []

        staff_ids = [u.id for u in staff]
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Batch: completed tasks with turnaround data (need assigned_at, completed_at, due_date)
        completed_tasks = (
            db.query(FilingTask)
            .filter(
                FilingTask.assigned_to.in_(staff_ids),
                FilingTask.status == FilingTaskStatus.COMPLETED,
                FilingTask.completed_at != None,
                FilingTask.completed_at >= since,
            )
            .all()
        )

        # Group completed tasks by user for turnaround/SLA calculations
        completed_by_user: Dict[int, list] = {uid: [] for uid in staff_ids}
        for t in completed_tasks:
            if t.assigned_to in completed_by_user:
                completed_by_user[t.assigned_to].append(t)

        # Batch: docs reviewed counts
        review_counts = (
            db.query(
                VerificationQueue.reviewer_id,
                func.count().label("cnt"),
            )
            .filter(
                VerificationQueue.reviewer_id.in_(staff_ids),
                VerificationQueue.reviewed_at != None,
                VerificationQueue.reviewed_at >= since,
            )
            .group_by(VerificationQueue.reviewer_id)
            .all()
        )
        review_map: Dict[int, int] = {row.reviewer_id: row.cnt for row in review_counts}

        # Batch: escalations received
        esc_received = (
            db.query(
                EscalationLog.escalated_to_user_id,
                func.count().label("cnt"),
            )
            .filter(
                EscalationLog.escalated_to_user_id.in_(staff_ids),
                EscalationLog.created_at >= since,
            )
            .group_by(EscalationLog.escalated_to_user_id)
            .all()
        )
        esc_recv_map: Dict[int, int] = {row.escalated_to_user_id: row.cnt for row in esc_received}

        # Batch: escalations resolved
        esc_resolved = (
            db.query(
                EscalationLog.resolved_by,
                func.count().label("cnt"),
            )
            .filter(
                EscalationLog.resolved_by.in_(staff_ids),
                EscalationLog.resolved_at != None,
                EscalationLog.resolved_at >= since,
            )
            .group_by(EscalationLog.resolved_by)
            .all()
        )
        esc_res_map: Dict[int, int] = {row.resolved_by: row.cnt for row in esc_resolved}

        # Assemble per-user metrics from pre-loaded data
        results = []
        for user in staff:
            uid = user.id
            user_completed = completed_by_user.get(uid, [])
            tasks_completed = len(user_completed)

            turnaround_hours = []
            sla_met = 0
            for t in user_completed:
                if t.assigned_at and t.completed_at:
                    delta = (t.completed_at - t.assigned_at).total_seconds() / 3600.0
                    turnaround_hours.append(delta)
                    if t.due_date and t.completed_at <= t.due_date:
                        sla_met += 1

            avg_turnaround = (
                sum(turnaround_hours) / len(turnaround_hours) if turnaround_hours else 0.0
            )
            sla_pct = (sla_met / tasks_completed * 100.0) if tasks_completed > 0 else 100.0

            results.append({
                "user_id": uid,
                "user_name": user.full_name,
                "period": f"last_{days}_days",
                "tasks_completed": tasks_completed,
                "avg_turnaround_hours": round(avg_turnaround, 1),
                "sla_compliance_pct": round(sla_pct, 1),
                "documents_reviewed": review_map.get(uid, 0),
                "escalations_received": esc_recv_map.get(uid, 0),
                "escalations_resolved": esc_res_map.get(uid, 0),
            })

        return results


# Module-level singleton
performance_service = PerformanceService()
