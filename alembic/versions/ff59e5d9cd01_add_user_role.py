"""add user role

Revision ID: ff59e5d9cd01
Revises: 80ac06ea809c
Create Date: 2026-10-08 14:14:16.743999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff59e5d9cd01'
down_revision: Union[str, Sequence[str], None] = '80ac06ea809c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('role', sa.String(), nullable=True)
    )
    op.execute("UPDATE users SET role = 'customer' WHERE role IS NULL")
    op.alter_column('users', 'role', nullable=False)


def downgrade():
    op.drop_column('users', 'role')


