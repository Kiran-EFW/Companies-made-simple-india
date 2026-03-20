"""create missing tables and add company columns

Revision ID: 004_missing_tables
Revises: 003_complete
Create Date: 2026-03-20

Creates the 15 tables that only existed via Base.metadata.create_all()
and adds employee_count / incorporation_date to the companies table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_missing_tables"
down_revision: Union[str, None] = "003_complete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Add new columns to companies ─────────────────────────────────────
    with op.batch_alter_table("companies") as batch_op:
        batch_op.add_column(sa.Column("employee_count", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("incorporation_date", sa.DateTime(), nullable=True))

    # ── stakeholder_profiles (must come before deal_shares, investor_interests) ──
    op.create_table(
        "stakeholder_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("stakeholder_type", sa.String(), nullable=True),
        sa.Column("entity_name", sa.String(), nullable=True),
        sa.Column("entity_type", sa.String(), nullable=True),
        sa.Column("pan_number", sa.String(), nullable=True),
        sa.Column("is_foreign", sa.Boolean(), default=False),
        sa.Column("dashboard_access_token", sa.String(), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_stakeholder_profiles_id", "stakeholder_profiles", ["id"])
    op.create_index("ix_stakeholder_profiles_email", "stakeholder_profiles", ["email"])

    # ── service_requests ─────────────────────────────────────────────────
    op.create_table(
        "service_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("service_key", sa.String(), nullable=False),
        sa.Column("service_name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("platform_fee", sa.Integer(), nullable=False),
        sa.Column("government_fee", sa.Integer(), default=0),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id"), nullable=True),
        sa.Column("is_paid", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_service_requests_id", "service_requests", ["id"])
    op.create_index("ix_service_requests_service_key", "service_requests", ["service_key"])

    # ── subscriptions ────────────────────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_key", sa.String(), nullable=False),
        sa.Column("plan_name", sa.String(), nullable=False),
        sa.Column("interval", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("razorpay_subscription_id", sa.String(), nullable=True),
        sa.Column("razorpay_plan_id", sa.String(), nullable=True),
        sa.Column("current_period_start", sa.DateTime(), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_subscriptions_id", "subscriptions", ["id"])
    op.create_index("ix_subscriptions_razorpay_subscription_id", "subscriptions", ["razorpay_subscription_id"])

    # ── accounting_connections ───────────────────────────────────────────
    op.create_table(
        "accounting_connections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("zoho_org_id", sa.String(), nullable=True),
        sa.Column("zoho_org_name", sa.String(), nullable=True),
        sa.Column("zoho_access_token", sa.Text(), nullable=True),
        sa.Column("zoho_refresh_token", sa.Text(), nullable=True),
        sa.Column("zoho_token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("tally_host", sa.String(), nullable=True),
        sa.Column("tally_port", sa.Integer(), nullable=True),
        sa.Column("tally_company_name", sa.String(), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("last_sync_status", sa.String(), nullable=True),
        sa.Column("last_sync_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_accounting_connections_id", "accounting_connections", ["id"])

    # ── esop_plans ───────────────────────────────────────────────────────
    op.create_table(
        "esop_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("plan_name", sa.String(), nullable=False),
        sa.Column("pool_size", sa.Integer(), nullable=False),
        sa.Column("pool_shares_allocated", sa.Integer(), default=0),
        sa.Column("default_vesting_months", sa.Integer(), default=48),
        sa.Column("default_cliff_months", sa.Integer(), default=12),
        sa.Column("default_vesting_type", sa.String(), nullable=True),
        sa.Column("exercise_price", sa.Float(), nullable=False),
        sa.Column("exercise_price_basis", sa.String(), nullable=True),
        sa.Column("effective_date", sa.DateTime(), nullable=True),
        sa.Column("expiry_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("board_resolution_date", sa.DateTime(), nullable=True),
        sa.Column("board_resolution_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("shareholder_resolution_date", sa.DateTime(), nullable=True),
        sa.Column("shareholder_resolution_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("plan_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("dpiit_recognized", sa.Boolean(), default=False),
        sa.Column("dpiit_recognition_number", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_esop_plans_id", "esop_plans", ["id"])

    # ── esop_grants ──────────────────────────────────────────────────────
    op.create_table(
        "esop_grants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("esop_plans.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("grantee_name", sa.String(), nullable=False),
        sa.Column("grantee_email", sa.String(), nullable=False),
        sa.Column("grantee_employee_id", sa.String(), nullable=True),
        sa.Column("grantee_designation", sa.String(), nullable=True),
        sa.Column("grant_date", sa.DateTime(), nullable=False),
        sa.Column("number_of_options", sa.Integer(), nullable=False),
        sa.Column("exercise_price", sa.Float(), nullable=False),
        sa.Column("vesting_months", sa.Integer(), nullable=False),
        sa.Column("cliff_months", sa.Integer(), nullable=False),
        sa.Column("vesting_type", sa.String(), nullable=True),
        sa.Column("vesting_start_date", sa.DateTime(), nullable=False),
        sa.Column("options_exercised", sa.Integer(), default=0),
        sa.Column("options_lapsed", sa.Integer(), default=0),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("grant_letter_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("acceptance_signature_request_id", sa.Integer(), sa.ForeignKey("signature_requests.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_esop_grants_id", "esop_grants", ["id"])

    # ── funding_rounds ───────────────────────────────────────────────────
    op.create_table(
        "funding_rounds",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("round_name", sa.String(), nullable=False),
        sa.Column("instrument_type", sa.String(), nullable=True),
        sa.Column("pre_money_valuation", sa.Float(), nullable=True),
        sa.Column("post_money_valuation", sa.Float(), nullable=True),
        sa.Column("price_per_share", sa.Float(), nullable=True),
        sa.Column("target_amount", sa.Float(), nullable=True),
        sa.Column("amount_raised", sa.Float(), default=0.0),
        sa.Column("valuation_cap", sa.Float(), nullable=True),
        sa.Column("discount_rate", sa.Float(), nullable=True),
        sa.Column("interest_rate", sa.Float(), nullable=True),
        sa.Column("maturity_months", sa.Integer(), nullable=True),
        sa.Column("esop_pool_expansion_pct", sa.Float(), default=0.0),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("term_sheet_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("sha_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("ssa_document_id", sa.Integer(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("sha_signature_request_id", sa.Integer(), sa.ForeignKey("signature_requests.id"), nullable=True),
        sa.Column("ssa_signature_request_id", sa.Integer(), sa.ForeignKey("signature_requests.id"), nullable=True),
        sa.Column("allotment_date", sa.DateTime(), nullable=True),
        sa.Column("allotment_completed", sa.Boolean(), default=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_funding_rounds_id", "funding_rounds", ["id"])

    # ── conversion_events (must come before round_investors) ─────────────
    op.create_table(
        "conversion_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("funding_round_id", sa.Integer(), sa.ForeignKey("funding_rounds.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("trigger_round_id", sa.Integer(), sa.ForeignKey("funding_rounds.id"), nullable=True),
        sa.Column("conversion_price", sa.Float(), nullable=False),
        sa.Column("conversion_method", sa.String(), nullable=False),
        sa.Column("interest_accrued", sa.Float(), default=0.0),
        sa.Column("principal_amount", sa.Float(), nullable=False),
        sa.Column("total_conversion_amount", sa.Float(), nullable=False),
        sa.Column("shares_issued", sa.Integer(), nullable=False),
        sa.Column("price_per_share_used", sa.Float(), nullable=False),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_conversion_events_id", "conversion_events", ["id"])

    # ── round_investors ──────────────────────────────────────────────────
    op.create_table(
        "round_investors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("funding_round_id", sa.Integer(), sa.ForeignKey("funding_rounds.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("investor_name", sa.String(), nullable=False),
        sa.Column("investor_email", sa.String(), nullable=True),
        sa.Column("investor_type", sa.String(), default="angel"),
        sa.Column("investor_entity", sa.String(), nullable=True),
        sa.Column("investment_amount", sa.Float(), nullable=False),
        sa.Column("shares_allotted", sa.Integer(), default=0),
        sa.Column("share_type", sa.String(), default="equity"),
        sa.Column("committed", sa.Boolean(), default=False),
        sa.Column("funds_received", sa.Boolean(), default=False),
        sa.Column("documents_signed", sa.Boolean(), default=False),
        sa.Column("shares_issued", sa.Boolean(), default=False),
        sa.Column("shareholder_id", sa.Integer(), sa.ForeignKey("shareholders.id"), nullable=True),
        sa.Column("converted", sa.Boolean(), default=False),
        sa.Column("conversion_event_id", sa.Integer(), sa.ForeignKey("conversion_events.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_round_investors_id", "round_investors", ["id"])

    # ── company_members ──────────────────────────────────────────────────
    op.create_table(
        "company_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("invite_email", sa.String(), nullable=False),
        sa.Column("invite_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("invite_status", sa.String(), nullable=False),
        sa.Column("invite_token", sa.String(), nullable=True, unique=True),
        sa.Column("invited_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("din", sa.String(), nullable=True),
        sa.Column("designation", sa.String(), nullable=True),
        sa.Column("permissions", sa.String(), nullable=True),
        sa.Column("invite_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("company_id", "invite_email", name="uq_company_invite_email"),
    )
    op.create_index("ix_company_members_id", "company_members", ["id"])
    op.create_index("ix_company_members_company_id", "company_members", ["company_id"])
    op.create_index("ix_company_members_user_id", "company_members", ["user_id"])
    op.create_index("ix_company_members_invite_email", "company_members", ["invite_email"])
    op.create_index("ix_company_members_invite_token", "company_members", ["invite_token"])

    # ── deal_shares ──────────────────────────────────────────────────────
    op.create_table(
        "deal_shares",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("investor_profile_id", sa.Integer(), sa.ForeignKey("stakeholder_profiles.id"), nullable=False),
        sa.Column("shared_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_deal_shares_id", "deal_shares", ["id"])
    op.create_index("ix_deal_shares_company_id", "deal_shares", ["company_id"])
    op.create_index("ix_deal_shares_investor_profile_id", "deal_shares", ["investor_profile_id"])

    # ── messages ─────────────────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sender_type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_messages_id", "messages", ["id"])
    op.create_index("ix_messages_company_id", "messages", ["company_id"])

    # ── investor_interests ───────────────────────────────────────────────
    op.create_table(
        "investor_interests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("investor_profile_id", sa.Integer(), sa.ForeignKey("stakeholder_profiles.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("investor_name", sa.String(), nullable=True),
        sa.Column("investor_email", sa.String(), nullable=True),
        sa.Column("investor_entity", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_investor_interests_id", "investor_interests", ["id"])

    # ── valuations ───────────────────────────────────────────────────────
    op.create_table(
        "valuations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("valuation_date", sa.DateTime(), nullable=True),
        sa.Column("fair_market_value", sa.Float(), nullable=False),
        sa.Column("total_enterprise_value", sa.Float(), nullable=False),
        sa.Column("report_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("prepared_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_valuations_id", "valuations", ["id"])

    # ── ca_assignments ───────────────────────────────────────────────────
    op.create_table(
        "ca_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ca_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("assigned_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(), default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_ca_assignments_id", "ca_assignments", ["id"])


def downgrade() -> None:
    op.drop_table("ca_assignments")
    op.drop_table("valuations")
    op.drop_table("investor_interests")
    op.drop_table("messages")
    op.drop_table("deal_shares")
    op.drop_table("company_members")
    op.drop_table("round_investors")
    op.drop_table("conversion_events")
    op.drop_table("funding_rounds")
    op.drop_table("esop_grants")
    op.drop_table("esop_plans")
    op.drop_table("accounting_connections")
    op.drop_table("subscriptions")
    op.drop_table("service_requests")
    op.drop_table("stakeholder_profiles")

    with op.batch_alter_table("companies") as batch_op:
        batch_op.drop_column("incorporation_date")
        batch_op.drop_column("employee_count")
