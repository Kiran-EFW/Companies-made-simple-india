"""Complete schema — add all remaining tables and missing columns.

Revision ID: 003_complete
Revises: 002_ops_backend
Create Date: 2026-03-15

Adds missing columns to existing tables:
  - users: role, is_active
  - companies: priority, assigned_to
  - directors: dpin, dsc_status, dsc_class

Creates new tables:
  - notifications, notification_preferences
  - admin_logs, internal_notes
  - compliance_tasks
  - shareholders, share_transactions
  - legal_documents
  - statutory_registers, register_entries
  - meetings
  - data_room_folders, data_room_files, data_room_share_links, data_room_access_logs
  - signature_requests, signatories, signature_audit_logs
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_complete"
down_revision: Union[str, None] = "002_ops_backend"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ══════════════════════════════════════════════════════════
    # PART 1 — Add missing columns to existing tables
    # ══════════════════════════════════════════════════════════

    # ── users: add role & is_active ───────────────────────────
    user_role_enum = sa.Enum(
        "user", "admin", "super_admin", "cs_lead", "ca_lead",
        "filing_coordinator", "customer_success",
        name="userrole",
    )
    op.add_column("users", sa.Column("role", user_role_enum, server_default="user", nullable=False))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False))

    # ── companies: add priority & assigned_to ─────────────────
    company_priority_enum = sa.Enum("normal", "urgent", "vip", name="companypriority")
    op.add_column("companies", sa.Column("priority", company_priority_enum, server_default="normal"))
    op.add_column(
        "companies",
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )

    # ── directors: add dpin, dsc_status, dsc_class ────────────
    dsc_status_enum = sa.Enum(
        "pending", "processing", "obtained", "failed", "expired",
        name="dscstatus",
    )
    op.add_column("directors", sa.Column("dpin", sa.String(), nullable=True))
    op.add_column("directors", sa.Column("dsc_status", dsc_status_enum, server_default="pending"))
    op.add_column("directors", sa.Column("dsc_class", sa.Integer(), nullable=True))

    # ══════════════════════════════════════════════════════════
    # PART 2 — Create new tables
    # ══════════════════════════════════════════════════════════

    # ── notifications ─────────────────────────────────────────
    notification_type_enum = sa.Enum(
        "status_update", "document_request", "payment", "compliance",
        "system", "admin_message", "task_assigned", "escalation",
        "document_verified", "document_rejected",
        name="notificationtype",
    )
    notification_channel_enum = sa.Enum(
        "in_app", "email", "sms", "whatsapp",
        name="notificationchannel",
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("action_url", sa.String(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("0"), nullable=True),
        sa.Column("channel", notification_channel_enum, server_default="in_app"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # ── notification_preferences ──────────────────────────────
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("email_enabled", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("sms_enabled", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("whatsapp_enabled", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("in_app_enabled", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("status_updates", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("payment_alerts", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("compliance_reminders", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("marketing", sa.Boolean(), server_default=sa.text("0")),
    )
    op.create_index("ix_notification_preferences_id", "notification_preferences", ["id"])

    # ── admin_logs ────────────────────────────────────────────
    op.create_table(
        "admin_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_admin_logs_id", "admin_logs", ["id"])

    # ── internal_notes ────────────────────────────────────────
    op.create_table(
        "internal_notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_internal_notes_id", "internal_notes", ["id"])

    # ── compliance_tasks ──────────────────────────────────────
    compliance_task_type_enum = sa.Enum(
        "inc_20a", "bank_account", "first_board_meeting", "auditor_appointment",
        "gst_registration", "dpiit_registration", "pf_registration",
        "esi_registration", "llp_agreement", "share_allotment",
        "aoc_4", "mgt_7", "mgt_7a", "dir_3_kyc", "adt_1_renewal",
        "form_11", "form_8",
        "board_meeting_q1", "board_meeting_q2", "board_meeting_q3", "board_meeting_q4", "agm",
        "gstr_1", "gstr_3b", "gstr_9",
        "tds_return_q1", "tds_return_q2", "tds_return_q3", "tds_return_q4", "form_16",
        "itr_filing",
        "advance_tax_q1", "advance_tax_q2", "advance_tax_q3", "advance_tax_q4",
        name="compliancetasktype",
    )
    compliance_task_status_enum = sa.Enum(
        "upcoming", "due_soon", "overdue", "in_progress", "completed", "not_applicable",
        name="compliancetaskstatus",
    )
    op.create_table(
        "compliance_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("task_type", compliance_task_type_enum, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("completed_date", sa.DateTime(), nullable=True),
        sa.Column("status", compliance_task_status_enum, server_default="upcoming"),
        sa.Column("form_data", sa.JSON(), nullable=True),
        sa.Column("filing_reference", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_compliance_tasks_id", "compliance_tasks", ["id"])
    op.create_index("ix_compliance_tasks_company_id", "compliance_tasks", ["company_id"])
    op.create_index("ix_compliance_tasks_due_date", "compliance_tasks", ["due_date"])

    # ── shareholders ──────────────────────────────────────────
    share_type_enum = sa.Enum("equity", "preference", name="sharetype")
    op.create_table(
        "shareholders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("pan_number", sa.String(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("share_type", share_type_enum, server_default="equity"),
        sa.Column("face_value", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("paid_up_value", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("date_of_allotment", sa.DateTime(), nullable=True),
        sa.Column("is_promoter", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_shareholders_id", "shareholders", ["id"])
    op.create_index("ix_shareholders_company_id", "shareholders", ["company_id"])

    # ── share_transactions ────────────────────────────────────
    transaction_type_enum = sa.Enum("allotment", "transfer", "buyback", name="transactiontype")
    op.create_table(
        "share_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("transaction_type", transaction_type_enum, nullable=False),
        sa.Column(
            "from_shareholder_id", sa.Integer(),
            sa.ForeignKey("shareholders.id"), nullable=True,
        ),
        sa.Column(
            "to_shareholder_id", sa.Integer(),
            sa.ForeignKey("shareholders.id"), nullable=True,
        ),
        sa.Column("shares", sa.Integer(), nullable=False),
        sa.Column("price_per_share", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("form_reference", sa.String(), nullable=True),
        sa.Column("transaction_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_share_transactions_id", "share_transactions", ["id"])
    op.create_index("ix_share_transactions_company_id", "share_transactions", ["company_id"])

    # ── legal_documents ───────────────────────────────────────
    op.create_table(
        "legal_documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("template_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="draft"),
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column("clauses_config", sa.JSON(), nullable=True),
        sa.Column("generated_html", sa.Text(), nullable=True),
        sa.Column("generated_content", sa.JSON(), nullable=True),
        sa.Column("parties", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_legal_documents_id", "legal_documents", ["id"])
    op.create_index("ix_legal_documents_company_id", "legal_documents", ["company_id"])

    # ── statutory_registers ───────────────────────────────────
    op.create_table(
        "statutory_registers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("register_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_statutory_registers_id", "statutory_registers", ["id"])
    op.create_index("ix_statutory_registers_company_id", "statutory_registers", ["company_id"])

    # ── register_entries ──────────────────────────────────────
    op.create_table(
        "register_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "register_id", sa.Integer(),
            sa.ForeignKey("statutory_registers.id"), nullable=False,
        ),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("entry_number", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.DateTime(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_register_entries_id", "register_entries", ["id"])
    op.create_index("ix_register_entries_register_id", "register_entries", ["register_id"])

    # ── meetings ──────────────────────────────────────────────
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("meeting_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("meeting_number", sa.Integer(), nullable=True),
        sa.Column("meeting_date", sa.DateTime(), nullable=False),
        sa.Column("venue", sa.String(), nullable=True),
        sa.Column("is_virtual", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("virtual_link", sa.String(), nullable=True),
        # Notice
        sa.Column("notice_date", sa.DateTime(), nullable=True),
        sa.Column("notice_html", sa.Text(), nullable=True),
        # Agenda & Minutes
        sa.Column("agenda_items", sa.JSON(), nullable=True),
        sa.Column("minutes_html", sa.Text(), nullable=True),
        sa.Column("minutes_signed", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("minutes_signed_date", sa.DateTime(), nullable=True),
        sa.Column("minutes_signed_by", sa.String(), nullable=True),
        # Attendance
        sa.Column("attendees", sa.JSON(), nullable=True),
        sa.Column("quorum_present", sa.Boolean(), server_default=sa.text("1")),
        # Resolutions
        sa.Column("resolutions", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), server_default="scheduled"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_meetings_id", "meetings", ["id"])
    op.create_index("ix_meetings_company_id", "meetings", ["company_id"])
    op.create_index("ix_meetings_meeting_date", "meetings", ["meeting_date"])

    # ── data_room_folders ─────────────────────────────────────
    op.create_table(
        "data_room_folders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "parent_id", sa.Integer(),
            sa.ForeignKey("data_room_folders.id"), nullable=True,
        ),
        sa.Column("folder_type", sa.String(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_data_room_folders_id", "data_room_folders", ["id"])
    op.create_index("ix_data_room_folders_company_id", "data_room_folders", ["company_id"])

    # ── data_room_files ───────────────────────────────────────
    op.create_table(
        "data_room_files",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column(
            "folder_id", sa.Integer(),
            sa.ForeignKey("data_room_folders.id"), nullable=False,
        ),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), server_default="0"),
        sa.Column("mime_type", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        # Data retention
        sa.Column("retention_category", sa.String(), nullable=True),
        sa.Column("retention_until", sa.DateTime(), nullable=True),
        # Version tracking
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column(
            "previous_version_id", sa.Integer(),
            sa.ForeignKey("data_room_files.id"), nullable=True,
        ),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_data_room_files_id", "data_room_files", ["id"])
    op.create_index("ix_data_room_files_company_id", "data_room_files", ["company_id"])
    op.create_index("ix_data_room_files_folder_id", "data_room_files", ["folder_id"])

    # ── data_room_share_links ─────────────────────────────────
    op.create_table(
        "data_room_share_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("share_token", sa.String(), unique=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        # Access control
        sa.Column("folder_ids", sa.JSON(), nullable=True),
        sa.Column("file_ids", sa.JSON(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        # Expiry & tracking
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("max_downloads", sa.Integer(), nullable=True),
        sa.Column("download_count", sa.Integer(), server_default="0"),
        sa.Column("last_accessed", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_data_room_share_links_id", "data_room_share_links", ["id"])
    op.create_index(
        "ix_data_room_share_links_share_token",
        "data_room_share_links", ["share_token"], unique=True,
    )

    # ── data_room_access_logs ─────────────────────────────────
    op.create_table(
        "data_room_access_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "share_link_id", sa.Integer(),
            sa.ForeignKey("data_room_share_links.id"), nullable=True,
        ),
        sa.Column(
            "file_id", sa.Integer(),
            sa.ForeignKey("data_room_files.id"), nullable=True,
        ),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("accessed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_data_room_access_logs_id", "data_room_access_logs", ["id"])
    op.create_index(
        "ix_data_room_access_logs_company_id",
        "data_room_access_logs", ["company_id"],
    )

    # ── signature_requests ────────────────────────────────────
    op.create_table(
        "signature_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "legal_document_id", sa.Integer(),
            sa.ForeignKey("legal_documents.id"), nullable=False,
        ),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("document_html", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), server_default="draft"),
        sa.Column("signing_order", sa.String(), server_default="parallel"),
        # Completion
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("signed_document_html", sa.Text(), nullable=True),
        sa.Column("certificate_html", sa.Text(), nullable=True),
        # Expiry
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        # Reminders
        sa.Column("reminder_interval_days", sa.Integer(), server_default="3"),
        sa.Column("last_reminder_sent", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_signature_requests_id", "signature_requests", ["id"])
    op.create_index("ix_signature_requests_company_id", "signature_requests", ["company_id"])

    # ── signatories ───────────────────────────────────────────
    op.create_table(
        "signatories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "signature_request_id", sa.Integer(),
            sa.ForeignKey("signature_requests.id"), nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("designation", sa.String(), nullable=True),
        sa.Column("signing_order", sa.Integer(), server_default="1"),
        # Secure access
        sa.Column("access_token", sa.String(), unique=True, nullable=False),
        # Signing status
        sa.Column("status", sa.String(), server_default="pending"),
        sa.Column("signature_type", sa.String(), nullable=True),
        sa.Column("signature_data", sa.Text(), nullable=True),
        sa.Column("signature_font", sa.String(), nullable=True),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        # Decline
        sa.Column("decline_reason", sa.Text(), nullable=True),
        sa.Column("declined_at", sa.DateTime(), nullable=True),
        # Verification
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        # OTP
        sa.Column("otp_code", sa.String(), nullable=True),
        sa.Column("otp_verified", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("otp_sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_signatories_id", "signatories", ["id"])
    op.create_index(
        "ix_signatories_access_token", "signatories", ["access_token"], unique=True,
    )
    op.create_index(
        "ix_signatories_signature_request_id",
        "signatories", ["signature_request_id"],
    )

    # ── signature_audit_logs ──────────────────────────────────
    op.create_table(
        "signature_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "signature_request_id", sa.Integer(),
            sa.ForeignKey("signature_requests.id"), nullable=False,
        ),
        sa.Column(
            "signatory_id", sa.Integer(),
            sa.ForeignKey("signatories.id"), nullable=True,
        ),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_signature_audit_logs_id", "signature_audit_logs", ["id"])
    op.create_index(
        "ix_signature_audit_logs_request_id",
        "signature_audit_logs", ["signature_request_id"],
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("signature_audit_logs")
    op.drop_table("signatories")
    op.drop_table("signature_requests")
    op.drop_table("data_room_access_logs")
    op.drop_table("data_room_share_links")
    op.drop_table("data_room_files")
    op.drop_table("data_room_folders")
    op.drop_table("meetings")
    op.drop_table("register_entries")
    op.drop_table("statutory_registers")
    op.drop_table("legal_documents")
    op.drop_table("share_transactions")
    op.drop_table("shareholders")
    op.drop_table("compliance_tasks")
    op.drop_table("internal_notes")
    op.drop_table("admin_logs")
    op.drop_table("notification_preferences")
    op.drop_table("notifications")

    # Remove added columns from existing tables
    op.drop_column("directors", "dsc_class")
    op.drop_column("directors", "dsc_status")
    op.drop_column("directors", "dpin")
    op.drop_column("companies", "assigned_to")
    op.drop_column("companies", "priority")
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")

    # Drop enum types (PostgreSQL only, no-op on SQLite)
    sa.Enum(name="transactiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sharetype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="compliancetaskstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="compliancetasktype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="notificationchannel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="notificationtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="dscstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="companypriority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
