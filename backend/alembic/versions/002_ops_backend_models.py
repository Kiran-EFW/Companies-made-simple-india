"""Add ops backend models — filing_tasks, verification_queue, escalation_rules, escalation_logs.
Also adds staff hierarchy columns to users table.

Revision ID: 002_ops_backend
Revises: 001_initial
Create Date: 2026-03-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_ops_backend"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Add staff hierarchy columns to users ──────────────
    op.add_column("users", sa.Column("department", sa.String(), nullable=True))
    op.add_column("users", sa.Column("seniority", sa.String(), nullable=True))
    op.add_column("users", sa.Column("reports_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))

    # ── filing_tasks ──────────────────────────────────────
    op.create_table(
        "filing_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(), default="normal"),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), default="unassigned"),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("task_metadata", sa.JSON(), nullable=True),
        sa.Column("escalation_level", sa.Integer(), default=0),
        sa.Column("escalated_at", sa.DateTime(), nullable=True),
        sa.Column("escalated_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("parent_task_id", sa.Integer(), sa.ForeignKey("filing_tasks.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_filing_tasks_company_id", "filing_tasks", ["company_id"])
    op.create_index("ix_filing_tasks_assigned_to", "filing_tasks", ["assigned_to"])
    op.create_index("ix_filing_tasks_status", "filing_tasks", ["status"])
    op.create_index("ix_filing_tasks_due_date", "filing_tasks", ["due_date"])

    # ── verification_queue ────────────────────────────────
    op.create_table(
        "verification_queue",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False, unique=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("decision", sa.String(), default="pending"),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("checklist", sa.JSON(), nullable=True),
        sa.Column("ai_confidence_score", sa.Integer(), nullable=True),
        sa.Column("ai_flags", sa.JSON(), nullable=True),
        sa.Column("queued_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_verification_queue_company_id", "verification_queue", ["company_id"])
    op.create_index("ix_verification_queue_reviewer_id", "verification_queue", ["reviewer_id"])

    # ── escalation_rules ──────────────────────────────────
    op.create_table(
        "escalation_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("trigger_type", sa.String(), nullable=False),
        sa.Column("threshold_hours", sa.Integer(), nullable=False),
        sa.Column("escalate_to_role", sa.String(), nullable=True),
        sa.Column("escalate_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(), default="notify"),
        sa.Column("task_type_filter", sa.JSON(), nullable=True),
        sa.Column("entity_type_filter", sa.JSON(), nullable=True),
        sa.Column("priority_filter", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # ── escalation_logs ───────────────────────────────────
    op.create_table(
        "escalation_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("escalation_rules.id"), nullable=False),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("escalated_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("escalated_to_role", sa.String(), nullable=True),
        sa.Column("action_taken", sa.String(), nullable=False),
        sa.Column("is_resolved", sa.Boolean(), default=False),
        sa.Column("resolved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_escalation_logs_is_resolved", "escalation_logs", ["is_resolved"])


def downgrade() -> None:
    op.drop_table("escalation_logs")
    op.drop_table("escalation_rules")
    op.drop_table("verification_queue")
    op.drop_table("filing_tasks")
    op.drop_column("users", "reports_to")
    op.drop_column("users", "seniority")
    op.drop_column("users", "department")
