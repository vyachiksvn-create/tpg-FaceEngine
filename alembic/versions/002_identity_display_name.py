"""identity display name and metadata

Revision ID: 002
Revises: 001
Create Date: 2026-07-28 13:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('identities', sa.Column('display_name', sa.String(255), nullable=True))
    op.add_column('identities', sa.Column('original_folder_name', sa.String(1024), nullable=True))
    op.add_column('identities', sa.Column('metadata_json', sa.Text, nullable=True))
    op.create_index('idx_identities_display_name', 'identities', ['display_name'])


def downgrade() -> None:
    op.drop_index('idx_identities_display_name')
    op.drop_column('identities', 'metadata_json')
    op.drop_column('identities', 'original_folder_name')
    op.drop_column('identities', 'display_name')