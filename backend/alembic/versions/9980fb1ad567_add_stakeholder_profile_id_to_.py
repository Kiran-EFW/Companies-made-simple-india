"""add_stakeholder_profile_id_to_shareholders

Revision ID: 9980fb1ad567
Revises: 003_complete
Create Date: 2026-03-19 23:04:13.900921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9980fb1ad567'
down_revision: Union[str, None] = '003_complete'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("shareholders") as batch_op:
        batch_op.add_column(
            sa.Column("stakeholder_profile_id", sa.Integer(), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_shareholders_stakeholder_profile_id",
            "stakeholder_profiles",
            ["stakeholder_profile_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("shareholders") as batch_op:
        batch_op.drop_constraint("fk_shareholders_stakeholder_profile_id", type_="foreignkey")
        batch_op.drop_column("stakeholder_profile_id")
