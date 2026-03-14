"""Performance and workload service — team metrics, leaderboard, workload balancing."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case

from src.models.user import User, UserRole
from src.models.filing_task import FilingTask, FilingTaskStatus
from src.models.verification_queue import VerificationQueue, VerificationDecision
from src.models.escalation_rule import EscalationLog

logger = logging.getLogger(__name__)


class PerformanceService:
    """Calculates workload, performance metrics, and team stats."""

    def get_team_workload(self, db: Session) -> Dict[str, Any]:
        """Get per-user workload breakdown for all staff."""
        staff = (
            db.query(User)
            .filter(User.role != UserRole.USER, User.is_active == True)
            .all()
        )

        team = []
        total_active = 0
        total_overdue = 0
        now = datetime.now(timezone.utc)

        for user in staff:
            active = (
                db.query(FilingTask)
                .filter(
                    FilingTask.assigned_to == user.id,
                    FilingTask.status.in_([
                        FilingTaskStatus.ASSIGNED,
                        FilingTaskStatus.IN_PROGRESS,
                        FilingTaskStatus.WAITING_ON_CLIENT,
                        FilingTaskStatus.WAITING_ON_GOVERNMENT,
                        FilingTaskStatus.UNDER_REVIEW,
                    ]),
                )
                .count()
            )
            completed = (
                db.query(FilingTask)
                .filter(
                    FilingTask.assigned_to == user.id,
                    FilingTask.status == FilingTaskStatus.COMPLETED,
                )
                .count()
            )
            overdue = (
                db.query(FilingTask)
                .filter(
                    FilingTask.assigned_to == user.id,
                    FilingTask.due_date != None,
                    FilingTask.due_date < now,
                    FilingTask.status.notin_([
                        FilingTaskStatus.COMPLETED,
                        FilingTaskStatus.CANCELLED,
                    ]),
                )
                .count()
            )
            pending_reviews = (
                db.query(VerificationQueue)
                .filter(
                    VerificationQueue.reviewer_id == user.id,
                    VerificationQueue.decision == VerificationDecision.PENDING,
                )
                .count()
            )

            dept = user.department.value if user.department else None
            sen = user.seniority.value if user.seniority else None

            team.append({
                "user_id": user.id,
                "user_name": user.full_name,
                "department": dept,
                "seniority": sen,
                "active_tasks": active,
                "completed_tasks": completed,
                "overdue_tasks": overdue,
                "pending_reviews": pending_reviews,
            })

            total_active += active
            total_overdue += overdue

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

        # Average turnaround (assigned_at → completed_at)
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
        """Get performance metrics for all staff members."""
        staff = (
            db.query(User)
            .filter(User.role != UserRole.USER, User.is_active == True)
            .all()
        )
        return [self.get_user_metrics(db, u.id, days) for u in staff]


# Module-level singleton
performance_service = PerformanceService()
