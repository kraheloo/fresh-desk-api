"""recreate_acls_table

Revision ID: d9292f775855
Revises: 52e991b23f4d
Create Date: 2026-01-04 17:24:01.049148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9292f775855'
down_revision: Union[str, Sequence[str], None] = '52e991b23f4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
