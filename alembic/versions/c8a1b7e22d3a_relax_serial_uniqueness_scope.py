"""relax serial uniqueness to be per-RMA (rma_id, serial_number)

Revision ID: c8a1b7e22d3a
Revises: e39f2e2ef90f
Create Date: 2025-11-17 05:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a1b7e22d3a'
down_revision: Union[str, None] = '3cc9df7ffb9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the unique index on serial_number if it exists
    try:
        op.drop_index('ix_rma_items_serial_number', table_name='rma_items')
    except Exception:
        # Some DBs may have it as a constraint; attempt to drop constraint by name
        try:
            op.drop_constraint('ix_rma_items_serial_number', 'rma_items', type_='unique')
        except Exception:
            pass

    # Create a non-unique index on serial_number for lookups
    op.create_index('ix_rma_items_serial_number', 'rma_items', ['serial_number'], unique=False)

    # Create composite unique constraint (rma_id, serial_number)
    op.create_unique_constraint('uq_rmaitem_rma_serial', 'rma_items', ['rma_id', 'serial_number'])


def downgrade() -> None:
    # Drop composite unique constraint
    try:
        op.drop_constraint('uq_rmaitem_rma_serial', 'rma_items', type_='unique')
    except Exception:
        pass

    # Drop non-unique index and recreate unique index
    try:
        op.drop_index('ix_rma_items_serial_number', table_name='rma_items')
    except Exception:
        pass

    op.create_index('ix_rma_items_serial_number', 'rma_items', ['serial_number'], unique=True)
