"""add_missing_columns

Revision ID: 006_missing_cols
Revises: 005_segments
Create Date: 2026-03-29

Adds columns that exist in SQLAlchemy models but were never migrated
to the production PostgreSQL database:
- users.reset_token, users.reset_token_expiry
- companies.plan_tier
- subscriptions.pending_plan_key, pending_plan_name, pending_amount
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006_missing_cols"
down_revision: Union[str, None] = "005_segments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_column_if_not_exists(table: str, column_name: str, column_type: sa.types.TypeEngine, **kwargs):
    """Add a column only if it doesn't already exist (safe for re-runs)."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :col"
        ),
        {"table": table, "col": column_name},
    ).fetchone()
    if not result:
        op.add_column(table, sa.Column(column_name, column_type, **kwargs))


def upgrade() -> None:
    # users table
    _add_column_if_not_exists("users", "reset_token", sa.String(), nullable=True)
    _add_column_if_not_exists("users", "reset_token_expiry", sa.DateTime(), nullable=True)

    # companies table
    _add_column_if_not_exists("companies", "plan_tier", sa.String(), nullable=True)

    # subscriptions table
    _add_column_if_not_exists("subscriptions", "pending_plan_key", sa.String(), nullable=True)
    _add_column_if_not_exists("subscriptions", "pending_plan_name", sa.String(), nullable=True)
    _add_column_if_not_exists("subscriptions", "pending_amount", sa.Integer(), nullable=True)


def downgrade() -> None:
    op.drop_column("subscriptions", "pending_amount")
    op.drop_column("subscriptions", "pending_plan_name")
    op.drop_column("subscriptions", "pending_plan_key")
    op.drop_column("companies", "plan_tier")
    op.drop_column("users", "reset_token_expiry")
    op.drop_column("users", "reset_token")
