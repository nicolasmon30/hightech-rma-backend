"""add_cascade_delete_to_password_reset_tokens

Revision ID: 65ebc19c1011
Revises: be89ee339157
Create Date: 2025-12-12 22:01:05.338049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65ebc19c1011'
down_revision: Union[str, None] = 'be89ee339157'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar la constraint existente
    op.drop_constraint(
        'password_reset_tokens_user_id_fkey',
        'password_reset_tokens',
        type_='foreignkey'
    )
    
    # Crear la nueva constraint con CASCADE
    op.create_foreign_key(
        'password_reset_tokens_user_id_fkey',
        'password_reset_tokens',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Revertir a la constraint sin CASCADE
    op.drop_constraint(
        'password_reset_tokens_user_id_fkey',
        'password_reset_tokens',
        type_='foreignkey'
    )
    
    op.create_foreign_key(
        'password_reset_tokens_user_id_fkey',
        'password_reset_tokens',
        'users',
        ['user_id'],
        ['id']
    )
