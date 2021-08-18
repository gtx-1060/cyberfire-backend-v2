"""Initial

Revision ID: 0e78fec9c169
Revises: 
Create Date: 2021-08-18 23:12:27.516450

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e78fec9c169'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('damagers_association_table',
    sa.Column('stage_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stage_id'], ['stages.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_table('kills_association_table',
    sa.Column('stage_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stage_id'], ['stages.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ondelete='CASCADE')
    )
    op.drop_constraint('squads_user_id_fkey', 'squads', type_='foreignkey')
    op.create_foreign_key(None, 'squads', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('stages', 'damage_leaders')
    op.drop_column('stages', 'kill_leaders')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stages', sa.Column('kill_leaders', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.add_column('stages', sa.Column('damage_leaders', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'squads', type_='foreignkey')
    op.create_foreign_key('squads_user_id_fkey', 'squads', 'users', ['user_id'], ['id'])
    op.drop_table('kills_association_table')
    op.drop_table('damagers_association_table')
    # ### end Alembic commands ###