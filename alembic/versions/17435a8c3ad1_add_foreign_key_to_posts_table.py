"""add foreign-key to posts table

Revision ID: 17435a8c3ad1
Revises: b8348e69bda9
Create Date: 2023-03-20 19:15:45.030853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17435a8c3ad1'
down_revision = 'b8348e69bda9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table="posts", referent_table="user", local_cols=[
                          'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    op.drop_constraint('post_users_fk', table_name="posts")
    op.drop_column('posts', 'owner_id')
    pass
