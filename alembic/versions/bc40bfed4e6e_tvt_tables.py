"""tvt tables

Revision ID: bc40bfed4e6e
Revises: 0e78fec9c169
Create Date: 2021-08-25 01:28:40.882324

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = 'bc40bfed4e6e'
down_revision = '0e78fec9c169'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tvt_tournaments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.UnicodeText(), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('state', ENUM('PAUSED', 'REGISTRATION', 'IS_ON', 'FINISHED', name='tournamentstates', create_type=False), nullable=True),
    sa.Column('rewards', sa.PickleType(), nullable=True),
    sa.Column('stream_url', sa.String(), nullable=True),
    sa.Column('game', ENUM('APEX', 'FORTNITE', 'COD_WARZONE', 'VALORANT', 'CSGO', name='games', create_type=False), nullable=True),
    sa.Column('img_path', sa.Text(), nullable=True),
    sa.Column('max_squads', sa.SmallInteger(), nullable=True),
    sa.Column('start_date', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tvt_tournaments_id'), 'tvt_tournaments', ['id'], unique=False)
    op.create_table('tvt_stages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('state', ENUM('WAITING', 'IS_ON', 'FINISHED', name='stagestates', create_type=False), nullable=True),
    sa.Column('title', sa.UnicodeText(), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.Column('index', sa.SmallInteger(), nullable=True),
    sa.ForeignKeyConstraint(['tournament_id'], ['tvt_tournaments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tvt_stages_id'), 'tvt_stages', ['id'], unique=False)
    op.create_table('tvt_tournament_association',
    sa.Column('tournaments_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tournaments_id'], ['tvt_tournaments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_table('tvt_matches',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stage_id', sa.Integer(), nullable=True),
    sa.Column('placement', sa.SmallInteger(), nullable=True),
    sa.ForeignKeyConstraint(['stage_id'], ['tvt_stages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tvt_matches_id'), 'tvt_matches', ['id'], unique=False)
    op.create_table('tvt_stats',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.SmallInteger(), nullable=False),
    sa.Column('proof_path', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('arrival_id', sa.Integer(), nullable=True),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['arrival_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['match_id'], ['tvt_matches.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tournament_id'], ['tvt_tournaments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('arrival_id', 'match_id', name='uix_tvtstats2'),
    sa.UniqueConstraint('user_id', 'match_id', name='uix_tvtstats1')
    )
    op.create_index(op.f('ix_tvt_stats_id'), 'tvt_stats', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tvt_stats_id'), table_name='tvt_stats')
    op.drop_table('tvt_stats')
    op.drop_index(op.f('ix_tvt_matches_id'), table_name='tvt_matches')
    op.drop_table('tvt_matches')
    op.drop_table('tvt_tournament_association')
    op.drop_index(op.f('ix_tvt_stages_id'), table_name='tvt_stages')
    op.drop_table('tvt_stages')
    op.drop_index(op.f('ix_tvt_tournaments_id'), table_name='tvt_tournaments')
    op.drop_table('tvt_tournaments')
    # ### end Alembic commands ###
