"""seed_initial_user

Revision ID: 220c960a97d9
Revises: 64c4a23a1940
Create Date: 2026-01-03 09:48:21.873495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.core.config import settings
from app.core.security import get_password_hash


# revision identifiers, used by Alembic.
revision: str = '220c960a97d9'
down_revision: Union[str, Sequence[str], None] = '64c4a23a1940'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users = sa.table('users',
        sa.column('id', sa.Integer),
        sa.column('email', sa.String),
        sa.column('hashed_password', sa.String),
        sa.column('is_active', sa.Boolean),
    )
    
    op.bulk_insert(users, [
        {
            'email': settings.FIRST_SUPERUSER,
            'hashed_password': get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            'is_active': True
        }
    ])


def downgrade() -> None:
    op.execute(f"DELETE FROM users WHERE email = '{settings.FIRST_SUPERUSER}'")
