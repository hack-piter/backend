"""unq path and logs

Revision ID: f69f8415369e
Revises: 6680a2abb009
Create Date: 2024-10-12 13:57:42.777967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f69f8415369e'
down_revision: Union[str, None] = '6680a2abb009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM video;')
    op.create_table('video_log',
    sa.Column('video_id', sa.Uuid(), nullable=False),
    sa.Column('exception', sa.String(length=255), nullable=False),
    sa.Column('attempt', sa.Integer(), nullable=False),
    sa.Column('is_looped', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_log_id'), 'video_log', ['id'], unique=False)
    op.create_unique_constraint(None, 'video', ['path'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'video', type_='unique')
    op.drop_index(op.f('ix_video_log_id'), table_name='video_log')
    op.drop_table('video_log')
    # ### end Alembic commands ###
