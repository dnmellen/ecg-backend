"""Add FK Signal

Revision ID: 4e8fcb030194
Revises: c02de0f9d5e4
Create Date: 2024-02-04 02:48:16.258105+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4e8fcb030194"
down_revision: Union[str, None] = "c02de0f9d5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("ecg_signal", sa.Column("ecg_id", sa.UUID(), nullable=False))
    op.create_foreign_key(None, "ecg_signal", "ecg", ["ecg_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "ecg_signal", type_="foreignkey")
    op.drop_column("ecg_signal", "ecg_id")
    # ### end Alembic commands ###
