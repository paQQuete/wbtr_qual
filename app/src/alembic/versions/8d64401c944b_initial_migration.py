"""initial migration

Revision ID: 8d64401c944b
Revises: 
Create Date: 2023-07-29 22:32:04.864877

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8d64401c944b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE SCHEMA IF NOT EXISTS content;
    ALTER ROLE app SET search_path TO content,public;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")
    op.create_table('users',
                    sa.Column('username', sa.String(length=100), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('password_hash', sa.String(length=512), nullable=False),
                    sa.Column('first_name', sa.String(length=255), nullable=True),
                    sa.Column('last_name', sa.String(length=255), nullable=True),
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='content'
                    )
    op.create_index(op.f('ix_content_users_email'), 'users', ['email'], unique=True, schema='content')
    op.create_index(op.f('ix_content_users_username'), 'users', ['username'], unique=True, schema='content')
    op.create_table('refresh_tokens',
                    sa.Column('refresh_token', sa.String(), nullable=False),
                    sa.Column('useragent', sa.String(), nullable=False),
                    sa.Column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['content.users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('useragent', 'user_id', name='ua_user_uniq_constr'),
                    schema='content'
                    )

def downgrade() -> None:
    op.drop_table('refresh_tokens', schema='content')
    op.drop_index(op.f('ix_content_users_username'), table_name='users', schema='content')
    op.drop_index(op.f('ix_content_users_email'), table_name='users', schema='content')
    op.drop_table('users', schema='content')
