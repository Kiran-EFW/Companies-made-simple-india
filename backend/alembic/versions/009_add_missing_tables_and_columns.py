"""add_missing_tables_and_columns

Revision ID: 009_missing_tbl_col
Revises: 008_cascade_idx
Create Date: 2026-04-09

Adds:
- share_issuance_workflows table (entirely missing from migrations)
- meetings: resolution_votes, notice_document_id,
  minutes_signature_request_id, filing_status columns
- esop_plans: approval_state column
- funding_rounds: checklist_state column
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "009_missing_tbl_col"
down_revision: Union[str, None] = "008_cascade_idx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    """Check if a column already exists (idempotent adds)."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    return table in inspector.get_table_names()


def upgrade() -> None:
    # ── Create share_issuance_workflows table ────────────────────────
    if not _table_exists("share_issuance_workflows"):
        op.create_table(
            "share_issuance_workflows",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("issuance_type", sa.String, default="fresh_allotment"),
            sa.Column("status", sa.String, default="draft"),
            # Pre-check
            sa.Column("authorized_capital", sa.Float, nullable=True),
            sa.Column("proposed_shares", sa.Integer, nullable=True),
            sa.Column("share_type", sa.String, default="equity"),
            sa.Column("face_value", sa.Float, default=10.0),
            sa.Column("issue_price", sa.Float, nullable=True),
            # Board Resolution
            sa.Column("board_resolution_document_id", sa.Integer, sa.ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("board_resolution_signature_request_id", sa.Integer, sa.ForeignKey("signature_requests.id", ondelete="SET NULL"), nullable=True),
            sa.Column("board_resolution_signed", sa.Boolean, default=False),
            sa.Column("board_resolution_date", sa.DateTime, nullable=True),
            # Shareholder Approval
            sa.Column("shareholder_resolution_required", sa.Boolean, default=False),
            sa.Column("shareholder_resolution_document_id", sa.Integer, sa.ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("shareholder_resolution_signature_request_id", sa.Integer, sa.ForeignKey("signature_requests.id", ondelete="SET NULL"), nullable=True),
            sa.Column("shareholder_approved", sa.Boolean, default=False),
            # Filings
            sa.Column("filing_status", sa.JSON, nullable=True),
            # Allottees
            sa.Column("allottees", sa.JSON, nullable=True),
            # Fund tracking
            sa.Column("total_amount_expected", sa.Float, default=0.0),
            sa.Column("total_amount_received", sa.Float, default=0.0),
            sa.Column("fund_receipts", sa.JSON, nullable=True),
            # Allotment
            sa.Column("allotment_date", sa.DateTime, nullable=True),
            sa.Column("allotment_board_resolution_id", sa.Integer, sa.ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True),
            # Post-allotment
            sa.Column("share_certificates_generated", sa.Boolean, default=False),
            sa.Column("pas3_document_id", sa.Integer, sa.ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("pas3_filed", sa.Boolean, default=False),
            sa.Column("pas3_filing_date", sa.DateTime, nullable=True),
            sa.Column("register_of_members_updated", sa.Boolean, default=False),
            # Wizard state
            sa.Column("wizard_state", sa.JSON, nullable=True),
            sa.Column("entity_type", sa.String, nullable=True),
            # Timestamps
            sa.Column("created_at", sa.DateTime, nullable=True),
            sa.Column("updated_at", sa.DateTime, nullable=True),
        )

    # ── Add missing columns to meetings ──────────────────────────────
    if _table_exists("meetings"):
        if not _column_exists("meetings", "resolution_votes"):
            op.add_column("meetings", sa.Column("resolution_votes", sa.JSON, nullable=True))
        if not _column_exists("meetings", "notice_document_id"):
            op.add_column("meetings", sa.Column("notice_document_id", sa.Integer, sa.ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True))
        if not _column_exists("meetings", "minutes_signature_request_id"):
            op.add_column("meetings", sa.Column("minutes_signature_request_id", sa.Integer, sa.ForeignKey("signature_requests.id", ondelete="SET NULL"), nullable=True))
        if not _column_exists("meetings", "filing_status"):
            op.add_column("meetings", sa.Column("filing_status", sa.JSON, nullable=True))

    # ── Add missing column to esop_plans ─────────────────────────────
    if _table_exists("esop_plans"):
        if not _column_exists("esop_plans", "approval_state"):
            op.add_column("esop_plans", sa.Column("approval_state", sa.JSON, nullable=True))

    # ── Add missing column to funding_rounds ─────────────────────────
    if _table_exists("funding_rounds"):
        if not _column_exists("funding_rounds", "checklist_state"):
            op.add_column("funding_rounds", sa.Column("checklist_state", sa.JSON, nullable=True))

    # ── Create audit_trail table ─────────────────────────────────────
    if not _table_exists("audit_trail"):
        op.create_table(
            "audit_trail",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("entity_type", sa.String, nullable=False, index=True),
            sa.Column("entity_id", sa.Integer, nullable=False),
            sa.Column("action", sa.String, nullable=False),
            sa.Column("changes", sa.JSON, nullable=True),
            sa.Column("metadata", sa.JSON, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        )


def downgrade() -> None:
    # Drop added columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "funding_rounds" in existing_tables:
        try:
            op.drop_column("funding_rounds", "checklist_state")
        except Exception:
            pass

    if "esop_plans" in existing_tables:
        try:
            op.drop_column("esop_plans", "approval_state")
        except Exception:
            pass

    if "meetings" in existing_tables:
        for col in ["filing_status", "minutes_signature_request_id", "notice_document_id", "resolution_votes"]:
            try:
                op.drop_column("meetings", col)
            except Exception:
                pass

    if "share_issuance_workflows" in existing_tables:
        op.drop_table("share_issuance_workflows")

    if "audit_trail" in existing_tables:
        op.drop_table("audit_trail")
