"""empty message

Revision ID: 161ebff178d4
Revises: 6270fa98b39e
Create Date: 2024-07-12 22:17:46.509029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '161ebff178d4'
down_revision = '6270fa98b39e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
