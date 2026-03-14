"""Initial schema — create all tables.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-14

Creates: users, companies, directors, documents, payments,
         stamp_duty_config, dsc_pricing, tasks, agent_logs
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── companies ──────────────────────────────────────
    entity_type_enum = sa.Enum(
        "private_limited", "opc", "llp", "section_8",
        "sole_proprietorship", "partnership", "public_limited",
        name="entitytype",
    )
    plan_tier_enum = sa.Enum("launch", "grow", "scale", name="plantier")
    company_status_enum = sa.Enum(
        "draft", "entity_selected", "payment_pending", "payment_completed",
        "documents_pending", "documents_uploaded", "documents_verified",
        "name_pending", "name_reserved", "name_rejected",
        "dsc_in_progress", "dsc_obtained",
        "filing_drafted", "filing_under_review", "filing_submitted",
        "mca_processing", "mca_query",
        "incorporated", "bank_account_pending", "bank_account_opened",
        "inc20a_pending", "fully_setup",
        name="companystatus",
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("entity_type", entity_type_enum, nullable=False),
        sa.Column("plan_tier", plan_tier_enum, nullable=True),
        sa.Column("proposed_names", sa.JSON(), nullable=True),
        sa.Column("approved_name", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("authorized_capital", sa.Integer(), nullable=True),
        sa.Column("num_directors", sa.Integer(), nullable=True),
        sa.Column("status", company_status_enum, nullable=True),
        sa.Column("pricing_snapshot", sa.JSON(), nullable=True),
        sa.Column("cin", sa.String(), nullable=True),
        sa.Column("pan", sa.String(), nullable=True),
        sa.Column("tan", sa.String(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_companies_id", "companies", ["id"])

    # ── directors ──────────────────────────────────────
    op.create_table(
        "directors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("pan_number", sa.String(), nullable=True),
        sa.Column("aadhaar_number", sa.String(), nullable=True),
        sa.Column("din", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.String(), nullable=True),
        sa.Column("has_dsc", sa.Boolean(), nullable=True, default=False),
        sa.Column("dsc_expiry", sa.DateTime(), nullable=True),
        sa.Column("is_nominee", sa.Boolean(), nullable=True, default=False),
        sa.Column("is_designated_partner", sa.Boolean(), nullable=True, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_directors_id", "directors", ["id"])

    # ── documents ──────────────────────────────────────
    document_type_enum = sa.Enum(
        "aadhaar", "pan_card", "passport", "utility_bill",
        "bank_statement", "photo", "address_proof", "other",
        name="documenttype",
    )
    verification_status_enum = sa.Enum(
        "pending", "ai_verified", "team_verified", "rejected",
        name="verificationstatus",
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("director_id", sa.Integer(), sa.ForeignKey("directors.id"), nullable=True),
        sa.Column("doc_type", document_type_enum, nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=True),
        sa.Column("verification_status", verification_status_enum, nullable=True),
        sa.Column("extracted_data", sa.String(), nullable=True),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_documents_id", "documents", ["id"])

    # ── payments ───────────────────────────────────────
    payment_status_enum = sa.Enum(
        "created", "paid", "failed", "refunded",
        name="paymentstatus",
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("razorpay_order_id", sa.String(), nullable=False),
        sa.Column("razorpay_payment_id", sa.String(), nullable=True),
        sa.Column("razorpay_signature", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("status", payment_status_enum, nullable=True),
        sa.Column("receipt_number", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_payments_id", "payments", ["id"])
    op.create_index("ix_payments_razorpay_order_id", "payments", ["razorpay_order_id"])

    # ── stamp_duty_config ──────────────────────────────
    op.create_table(
        "stamp_duty_config",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("moa_fixed", sa.Float(), nullable=True),
        sa.Column("aoa_fixed", sa.Float(), nullable=True),
        sa.Column("aoa_percentage", sa.Float(), nullable=True),
        sa.Column("aoa_min", sa.Float(), nullable=True),
        sa.Column("aoa_max", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_stamp_duty_config_id", "stamp_duty_config", ["id"])
    op.create_index("ix_stamp_duty_config_state", "stamp_duty_config", ["state"])

    # ── dsc_pricing ────────────────────────────────────
    op.create_table(
        "dsc_pricing",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vendor", sa.String(), nullable=False),
        sa.Column("dsc_type", sa.String(), nullable=False),
        sa.Column("validity_years", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("token_price", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_dsc_pricing_id", "dsc_pricing", ["id"])

    # ── tasks ──────────────────────────────────────────
    task_status_enum = sa.Enum(
        "pending", "running", "completed", "failed",
        "waiting_on_user", "waiting_on_team",
        name="taskstatus",
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("status", task_status_enum, nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])

    # ── agent_logs ─────────────────────────────────────
    op.create_table(
        "agent_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("level", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_agent_logs_id", "agent_logs", ["id"])


def downgrade() -> None:
    op.drop_table("agent_logs")
    op.drop_table("tasks")
    op.drop_table("dsc_pricing")
    op.drop_table("stamp_duty_config")
    op.drop_table("payments")
    op.drop_table("documents")
    op.drop_table("directors")
    op.drop_table("companies")
    op.drop_table("users")

    # Drop enum types (PostgreSQL only, no-op on SQLite)
    sa.Enum(name="taskstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="paymentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="verificationstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="documenttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="companystatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="plantier").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="entitytype").drop(op.get_bind(), checkfirst=True)
