"""song comment

Revision ID: 3120d5f8e1c7
Revises: d38f7e35fcd5
Create Date: 2025-05-05 16:04:53.736316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3120d5f8e1c7'
down_revision: Union[str, None] = 'd38f7e35fcd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('songs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('songs', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###
