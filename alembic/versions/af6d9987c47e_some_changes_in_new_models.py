"""some changes in new models

Revision ID: af6d9987c47e
Revises: bc40bfed4e6e
Create Date: 2021-08-27 17:37:11.700964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af6d9987c47e'
down_revision = 'bc40bfed4e6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tvt_matches', sa.Column('finished', sa.Boolean(), nullable=True))
    op.add_column('tvt_matches', sa.Column('index', sa.SmallInteger(), nullable=False))
    op.drop_column('tvt_matches', 'placement')
    op.drop_column('tvt_stages', 'title')
    op.drop_column('tvt_stages', 'description')
    op.drop_constraint('tvt_stats_match_id_fkey', 'tvt_stats', type_='foreignkey')
    op.create_foreign_key(None, 'tvt_stats', 'tvt_matches', ['match_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tvt_stats', type_='foreignkey')
    op.create_foreign_key('tvt_stats_match_id_fkey', 'tvt_stats', 'tvt_matches', ['match_id'], ['id'], ondelete='CASCADE')
    op.add_column('tvt_stages', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tvt_stages', sa.Column('title', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tvt_matches', sa.Column('placement', sa.SMALLINT(), autoincrement=False, nullable=True))
    op.drop_column('tvt_matches', 'index')
    op.drop_column('tvt_matches', 'finished')
    # ### end Alembic commands ###
