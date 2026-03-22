"""add_segment_column_and_new_entity_types

Revision ID: 005_segments
Revises: 9980fb1ad567
Create Date: 2026-03-22

Adds:
- 'nidhi' and 'producer_company' values to the entitytype enum
- 'customersegment' enum type with 7 values
- 'segment' column (nullable) on the companies table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_segments"
down_revision: Union[str, None] = "9980fb1ad567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new values to the existing entitytype enum
    # PostgreSQL requires ALTER TYPE ... ADD VALUE for enum extension
    op.execute("ALTER TYPE entitytype ADD VALUE IF NOT EXISTS 'nidhi'")
    op.execute("ALTER TYPE entitytype ADD VALUE IF NOT EXISTS 'producer_company'")

    # 2. Create the customersegment enum type
    customersegment = sa.Enum(
        "micro_business",
        "sme",
        "startup",
        "non_profit",
        "nidhi",
        "producer",
        "enterprise",
        name="customersegment",
    )
    customersegment.create(op.get_bind(), checkfirst=True)

    # 3. Add segment column to companies table
    op.add_column(
        "companies",
        sa.Column(
            "segment",
            sa.Enum(
                "micro_business",
                "sme",
                "startup",
                "non_profit",
                "nidhi",
                "producer",
                "enterprise",
                name="customersegment",
                create_type=False,
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    # 1. Drop segment column
    op.drop_column("companies", "segment")

    # 2. Drop customersegment enum type
    sa.Enum(name="customersegment").drop(op.get_bind(), checkfirst=True)

    # Note: PostgreSQL does not support removing individual enum values.
    # The 'nidhi' and 'producer_company' values remain in the entitytype
    # enum after downgrade.  A full enum rebuild would be needed to remove
    # them, but this is safe — unused values don't cause issues.
