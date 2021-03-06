"""Add foreign key

Revision ID: b2a295341b8a
Revises: cfd44b3faf45
Create Date: 2022-02-04 15:36:41.821867

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b2a295341b8a'
down_revision = 'cfd44b3faf45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('poster_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'posts', 'users', ['poster_id'], ['id'])
    op.drop_column('posts', 'author')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('author', mysql.VARCHAR(length=200), nullable=False))
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_column('posts', 'poster_id')
    # ### end Alembic commands ###
