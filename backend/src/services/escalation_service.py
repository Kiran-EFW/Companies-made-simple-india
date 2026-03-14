"""Escalation service — runs rule-based checks and creates escalation logs."""

import logging
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.filing_task import FilingTask, FilingTaskStatus
from src.models.verification_queue import VerificationQueue, VerificationDecision
from src.models.escalation_rule import (
    EscalationRule,
    EscalationLog,
    EscalationTrigger,
    EscalationAction,
)
from src.models.user import User, UserRole
from src.models.notification import NotificationType

logger = logging.getLogger(__name__)


class EscalationService:
    """Evaluates escalation rules and takes action on overdue/stale items."""

    def run_escalation_check(self, db: Session) -> int:
        """Run all active escalation rules. Returns number of new escalations created."""
        rules = db.query(EscalationRule).filter(EscalationRule.is_active == True).all()
        total_escalations = 0

        for rule in rules:
            try:
                count = self._evaluate_rule(db, rule)
                total_escalations += count
            except Exception:
                logger.exception("Error evaluating escalation rule %d (%s)", rule.id, rule.name)

        if total_escalations > 0:
            db.commit()
            logger.info("Escalation check complete: %d new escalations", total_escalations)

        return total_escalations

    def _evaluate_rule(self, db: Session, rule: EscalationRule) -> int:
        """Evaluate a single rule and create escalation logs for matches."""
        trigger = rule.trigger_type
        if isinstance(trigger, EscalationTrigger):
            trigger = trigger.value

        handler = {
            EscalationTrigger.FILING_TASK_OVERDUE.value: self._check_filing_task_overdue,
            EscalationTrigger.FILING_TASK_STALE.value: self._check_filing_task_stale,
            EscalationTrigger.DOCUMENT_REVIEW_PENDING.value: self._check_document_review_pending,
            EscalationTrigger.SLA_BREACH.value: self._check_filing_task_overdue,  # Same logic
        }.get(trigger)

        if not handler:
            return 0

        return handler(db, rule)

    def _check_filing_task_overdue(self, db: Session, rule: EscalationRule) -> int:
        """Find filing tasks past their due_date by threshold_hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=rule.threshold_hours)

        query = db.query(FilingTask).filter(
            FilingTask.due_date != None,
            FilingTask.due_date < cutoff,
            FilingTask.status.in_([
                FilingTaskStatus.UNASSIGNED,
                FilingTaskStatus.ASSIGNED,
                FilingTaskStatus.IN_PROGRESS,
                FilingTaskStatus.WAITING_ON_CLIENT,
                FilingTaskStatus.WAITING_ON_GOVERNMENT,
            ]),
        )

        query = self._apply_task_filters(query, rule)
        tasks = query.all()
        count = 0

        # Batch-load already-escalated task IDs to avoid N+1 queries
        task_ids = [t.id for t in tasks]
        already_escalated = self._batch_already_escalated(db, rule.id, "filing_task", task_ids)

        for task in tasks:
            if task.id in already_escalated:
                continue
            self._execute_escalation(db, rule, "filing_task", task.id, task.company_id)
            task.escalation_level = (task.escalation_level or 0) + 1
            task.escalated_at = datetime.now(timezone.utc)
            count += 1

        return count

    def _check_filing_task_stale(self, db: Session, rule: EscalationRule) -> int:
        """Find tasks not updated for threshold_hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=rule.threshold_hours)

        query = db.query(FilingTask).filter(
            FilingTask.updated_at < cutoff,
            FilingTask.status.in_([
                FilingTaskStatus.ASSIGNED,
                FilingTaskStatus.IN_PROGRESS,
            ]),
        )

        query = self._apply_task_filters(query, rule)
        tasks = query.all()
        count = 0

        # Batch-load already-escalated task IDs to avoid N+1 queries
        task_ids = [t.id for t in tasks]
        already_escalated = self._batch_already_escalated(db, rule.id, "filing_task", task_ids)

        for task in tasks:
            if task.id in already_escalated:
                continue
            self._execute_escalation(db, rule, "filing_task", task.id, task.company_id)
            task.escalation_level = (task.escalation_level or 0) + 1
            task.escalated_at = datetime.now(timezone.utc)
            count += 1

        return count

    def _check_document_review_pending(self, db: Session, rule: EscalationRule) -> int:
        """Find documents in review queue past threshold."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=rule.threshold_hours)

        items = (
            db.query(VerificationQueue)
            .filter(
                VerificationQueue.decision == VerificationDecision.PENDING,
                VerificationQueue.queued_at < cutoff,
            )
            .all()
        )

        count = 0

        # Batch-load already-escalated item IDs to avoid N+1 queries
        item_ids = [i.id for i in items]
        already_escalated = self._batch_already_escalated(db, rule.id, "verification_queue", item_ids)

        for item in items:
            if item.id in already_escalated:
                continue
            self._execute_escalation(db, rule, "verification_queue", item.id, item.company_id)
            count += 1

        return count

    def _apply_task_filters(self, query, rule: EscalationRule):
        """Apply optional scope filters from the rule."""
        if rule.task_type_filter:
            query = query.filter(FilingTask.task_type.in_(rule.task_type_filter))
        if rule.priority_filter:
            query = query.filter(FilingTask.priority.in_(rule.priority_filter))
        return query

    def _batch_already_escalated(
        self, db: Session, rule_id: int, target_type: str, target_ids: List[int]
    ) -> set:
        """Batch-check which targets already have unresolved escalations for this rule.

        Returns a set of target_ids that are already escalated, replacing N individual
        queries with a single IN-clause query.
        """
        if not target_ids:
            return set()
        return set(
            row[0] for row in
            db.query(EscalationLog.target_id)
            .filter(
                EscalationLog.rule_id == rule_id,
                EscalationLog.target_type == target_type,
                EscalationLog.target_id.in_(target_ids),
                EscalationLog.is_resolved == False,
            )
            .all()
        )

    def _already_escalated(
        self, db: Session, rule_id: int, target_type: str, target_id: int
    ) -> bool:
        """Check if this target was already escalated by this rule and not resolved."""
        return (
            db.query(EscalationLog)
            .filter(
                EscalationLog.rule_id == rule_id,
                EscalationLog.target_type == target_type,
                EscalationLog.target_id == target_id,
                EscalationLog.is_resolved == False,
            )
            .first()
            is not None
        )

    def _execute_escalation(
        self,
        db: Session,
        rule: EscalationRule,
        target_type: str,
        target_id: int,
        company_id: Optional[int],
    ) -> EscalationLog:
        """Create escalation log entry and optionally reassign."""
        action = rule.action
        if isinstance(action, EscalationAction):
            action = action.value

        # Determine who to escalate to
        escalate_to_user_id = rule.escalate_to_user_id
        if not escalate_to_user_id and rule.escalate_to_role:
            # Find a user with the matching role (compare as string since role is enum)
            try:
                target_role = UserRole(rule.escalate_to_role)
            except ValueError:
                target_role = rule.escalate_to_role
            user = (
                db.query(User)
                .filter(User.role == target_role, User.is_active == True)
                .first()
            )
            if user:
                escalate_to_user_id = user.id

        log = EscalationLog(
            rule_id=rule.id,
            target_type=target_type,
            target_id=target_id,
            company_id=company_id,
            escalated_to_user_id=escalate_to_user_id,
            escalated_to_role=rule.escalate_to_role,
            action_taken=action,
        )
        db.add(log)

        # Reassign if action requires it
        if action in (EscalationAction.REASSIGN.value, EscalationAction.NOTIFY_AND_REASSIGN.value):
            if target_type == "filing_task" and escalate_to_user_id:
                task = db.query(FilingTask).filter(FilingTask.id == target_id).first()
                if task:
                    task.assigned_to = escalate_to_user_id
                    task.escalated_to = escalate_to_user_id
                    task.escalated_at = datetime.now(timezone.utc)

        # Send notification
        if action in (EscalationAction.NOTIFY.value, EscalationAction.NOTIFY_AND_REASSIGN.value,
                      EscalationAction.ESCALATE_TO_LEAD.value):
            if escalate_to_user_id:
                self._send_escalation_notification(db, escalate_to_user_id, rule, target_type, target_id, company_id)

        return log

    def _send_escalation_notification(
        self,
        db: Session,
        user_id: int,
        rule: EscalationRule,
        target_type: str,
        target_id: int,
        company_id: Optional[int],
    ) -> None:
        """Send in-app notification for escalation."""
        try:
            from src.services.notification_service import notification_service
            notification_service.send_notification(
                db=db,
                user_id=user_id,
                type=NotificationType.ESCALATION,
                title=f"Escalation: {rule.name}",
                message=f"Auto-escalation triggered for {target_type} #{target_id}. Rule: {rule.name}",
                company_id=company_id,
                metadata={
                    "rule_id": rule.id,
                    "target_type": target_type,
                    "target_id": target_id,
                },
            )
        except Exception:
            logger.exception("Failed to send escalation notification")

    def resolve_escalation(
        self,
        db: Session,
        escalation_id: int,
        resolved_by: int,
        notes: Optional[str] = None,
    ) -> Optional[EscalationLog]:
        """Mark an escalation as resolved and reset the target's escalation level."""
        log = db.query(EscalationLog).filter(EscalationLog.id == escalation_id).first()
        if not log:
            return None
        log.is_resolved = True
        log.resolved_by = resolved_by
        log.resolved_at = datetime.now(timezone.utc)
        log.resolution_notes = notes

        # Reset the target's escalation state if it was a filing task
        if log.target_type == "filing_task":
            task = db.query(FilingTask).filter(FilingTask.id == log.target_id).first()
            if task:
                # Check if there are still other unresolved escalations for this task
                other_open = (
                    db.query(EscalationLog)
                    .filter(
                        EscalationLog.target_type == "filing_task",
                        EscalationLog.target_id == log.target_id,
                        EscalationLog.id != escalation_id,
                        EscalationLog.is_resolved == False,
                    )
                    .count()
                )
                if other_open == 0:
                    task.escalation_level = 0
                    task.escalated_at = None
                    task.escalated_to = None

        db.commit()
        db.refresh(log)
        return log

    def seed_default_rules(self, db: Session) -> List[EscalationRule]:
        """Create default escalation rules if none exist."""
        existing = db.query(EscalationRule).count()
        if existing > 0:
            return []

        defaults = [
            EscalationRule(
                name="Filing task pending > 24h",
                trigger_type=EscalationTrigger.FILING_TASK_STALE,
                threshold_hours=24,
                escalate_to_role="cs_lead",
                action=EscalationAction.NOTIFY,
            ),
            EscalationRule(
                name="Document review pending > 12h",
                trigger_type=EscalationTrigger.DOCUMENT_REVIEW_PENDING,
                threshold_hours=12,
                escalate_to_role="cs_lead",
                action=EscalationAction.NOTIFY,
            ),
            EscalationRule(
                name="Filing task overdue > 48h",
                trigger_type=EscalationTrigger.FILING_TASK_OVERDUE,
                threshold_hours=48,
                escalate_to_role="cs_lead",
                action=EscalationAction.NOTIFY_AND_REASSIGN,
            ),
            EscalationRule(
                name="SLA breach — critical",
                trigger_type=EscalationTrigger.SLA_BREACH,
                threshold_hours=72,
                escalate_to_role="admin",
                action=EscalationAction.ESCALATE_TO_LEAD,
                priority_filter=["high", "urgent"],
            ),
        ]
        for rule in defaults:
            db.add(rule)
        db.commit()
        return defaults


# Module-level singleton
escalation_service = EscalationService()
