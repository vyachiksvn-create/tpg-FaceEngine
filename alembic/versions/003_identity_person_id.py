"""Add person_id, quality_score, representative_photo_id, health_score

Revision ID: 003
Revises: 002
Create Date: 2026-07-28 14:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('identities', sa.Column('person_id', sa.String(32), unique=True, nullable=True))
    op.add_column('identities', sa.Column('representative_photo_id', sa.Integer, nullable=True))
    op.add_column('identities', sa.Column('health_score', sa.Float, nullable=True))
    op.create_index('idx_identities_person_id', 'identities', ['person_id'])
    op.create_index('idx_identities_representative_photo_id', 'identities', ['representative_photo_id'])
    op.add_column('photos', sa.Column('quality_score', sa.Float, nullable=True))
    op.create_index('idx_photos_quality_score', 'photos', ['quality_score'])


def downgrade() -> None:
    op.drop_index('idx_photos_quality_score')
    op.drop_column('photos', 'quality_score')
    op.drop_index('idx_identities_representative_photo_id')
    op.drop_index('idx_identities_person_id')
    op.drop_column('identities', 'health_score')
    op.drop_column('identities', 'representative_photo_id')
    op.drop_column('identities', 'person_id')