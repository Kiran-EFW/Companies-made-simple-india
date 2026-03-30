"""add_skipped_columns

Revision ID: 007_skipped_cols
Revises: 006_missing_cols
Create Date: 2026-03-30

Idempotently adds columns from migrations that were skipped when the
production PostgreSQL database was stamped at 005_segments (because it
had been bootstrapped by create_all, not alembic):

From 9980fb1ad567:
- shareholders.stakeholder_profile_id

From 005_segments:
- companies.segment  (+ customersegment enum type)
- entitytype enum values: nidhi, producer_company

From 006 type fixes:
- companies.plan_tier was added as VARCHAR but model expects plantier enum
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_skipped_cols"
down_revision: Union[str, None] = "006_missing_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :col"
        ),
        {"table": table, "col": column_name},
    ).fetchone()
    return result is not None


def _add_column_if_not_exists(table: str, column_name: str, column_type, **kwargs):
    """Add a column only if it doesn't already exist."""
    if not _column_exists(table, column_name):
        op.add_column(table, sa.Column(column_name, column_type, **kwargs))


def _enum_type_exists(name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = :name"),
        {"name": name},
    ).fetchone()
    return result is not None


def _create_enum_if_not_exists(name: str, values: list[str]):
    """Create a PostgreSQL enum type if it doesn't already exist."""
    if not _enum_type_exists(name):
        enum = sa.Enum(*values, name=name)
        enum.create(op.get_bind())


def _add_enum_value_if_not_exists(enum_name: str, value: str):
    """Add a value to an existing PostgreSQL enum type if not present."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid "
            "WHERE t.typname = :ename AND e.enumlabel = :val"
        ),
        {"ename": enum_name, "val": value},
    ).fetchone()
    if not result:
        conn.execute(
            sa.text(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{value}'")
        )


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # Ensure required enum types exist
    # ------------------------------------------------------------------
    _create_enum_if_not_exists("customersegment", [
        "micro_business", "sme", "startup", "non_profit",
        "nidhi", "producer", "enterprise",
    ])
    _create_enum_if_not_exists("plantier", [
        "launch", "grow", "scale",
    ])

    # Add enum values that may be missing from entitytype
    _add_enum_value_if_not_exists("entitytype", "nidhi")
    _add_enum_value_if_not_exists("entitytype", "producer_company")

    # ------------------------------------------------------------------
    # shareholders.stakeholder_profile_id (from 9980fb1ad567)
    # ------------------------------------------------------------------
    _add_column_if_not_exists(
        "shareholders", "stakeholder_profile_id",
        sa.Integer(), nullable=True,
    )
    # Add FK if it doesn't exist
    fk_exists = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.table_constraints "
            "WHERE constraint_name = 'fk_shareholders_stakeholder_profile_id' "
            "AND table_name = 'shareholders'"
        ),
    ).fetchone()
    if not fk_exists and _column_exists("shareholders", "stakeholder_profile_id"):
        try:
            op.create_foreign_key(
                "fk_shareholders_stakeholder_profile_id",
                "shareholders", "stakeholder_profiles",
                ["stakeholder_profile_id"], ["id"],
            )
        except Exception:
            pass  # FK may exist under an auto-generated name

    # ------------------------------------------------------------------
    # companies.segment (from 005_segments)
    # ------------------------------------------------------------------
    _add_column_if_not_exists(
        "companies", "segment",
        sa.Enum(
            "micro_business", "sme", "startup", "non_profit",
            "nidhi", "producer", "enterprise",
            name="customersegment", create_type=False,
        ),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Fix companies.plan_tier: 006 created it as VARCHAR, but the model
    # uses Enum(PlanTier).  If it's VARCHAR, drop and re-create as enum.
    # If it doesn't exist yet, create it properly.
    # ------------------------------------------------------------------
    if _column_exists("companies", "plan_tier"):
        # Check if it's currently varchar vs enum
        col_type = conn.execute(
            sa.text(
                "SELECT data_type, udt_name FROM information_schema.columns "
                "WHERE table_name = 'companies' AND column_name = 'plan_tier'"
            ),
        ).fetchone()
        if col_type and col_type[0] == "character varying":
            # It's VARCHAR from the old migration — convert to enum
            op.execute(
                "ALTER TABLE companies ALTER COLUMN plan_tier "
                "TYPE plantier USING plan_tier::plantier"
            )
    else:
        op.add_column(
            "companies",
            sa.Column(
                "plan_tier",
                sa.Enum("launch", "grow", "scale", name="plantier", create_type=False),
                nullable=True,
            ),
        )


def downgrade() -> None:
    op.drop_column("companies", "segment")
    op.drop_column("shareholders", "stakeholder_profile_id")
    sa.Enum(name="plantier").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="customersegment").drop(op.get_bind(), checkfirst=True)
