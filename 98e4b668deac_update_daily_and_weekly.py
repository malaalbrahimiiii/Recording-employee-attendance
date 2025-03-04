"""update daily and weekly

Revision ID: 98e4b668deac
Revises: f26724f1b909
Create Date: 2025-02-22 14:43:22.763258

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '98e4b668deac'
down_revision = 'f26724f1b909'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weeklyattendance',
    sa.Column('weekly_attendance_hours', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('dailyattendance', sa.Column('daily_attendance_hours', sa.Integer(), nullable=False))
    op.drop_column('dailyattendance', 'total_attendance_hours')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dailyattendance', sa.Column('total_attendance_hours', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('dailyattendance', 'daily_attendance_hours')
    op.drop_table('weeklyattendance')
    # ### end Alembic commands ###
