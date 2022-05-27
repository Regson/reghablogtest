"""add about author field

Revision ID: f3edc2f8b269
Revises: b2a295341b8a
Create Date: 2022-02-15 21:56:36.199593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3edc2f8b269'
down_revision = 'b2a295341b8a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_author', sa.Text(length=450), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'about_author')
    # ### end Alembic commands ###