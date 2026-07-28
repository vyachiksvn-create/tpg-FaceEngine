"""init

Revision ID: 001
Revises: 
Create Date: 2026-07-28 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(255), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_table(
        "photos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("identity_id", sa.Integer, sa.ForeignKey("identities.id"), nullable=True, index=True),
        sa.Column("file_path", sa.String(1024), unique=True, nullable=False),
        sa.Column("sha256", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("thumbnail_path", sa.String(1024), nullable=True),
        sa.Column("is_primary", sa.Boolean, default=False),
    )
    op.create_table(
        "embeddings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.id"), nullable=False, index=True),
        sa.Column("embedding_vector", sa.LargeBinary, nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )
    op.create_table(
        "import_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("file_path", sa.String(1024), nullable=False, index=True),
        sa.Column("sha256", sa.String(64), nullable=True, index=True),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("imported_at", sa.DateTime, nullable=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.id"), nullable=True),
    )
    op.create_table(
        "quality_checks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.id"), nullable=False, index=True),
        sa.Column("blur_score", sa.Float, nullable=True),
        sa.Column("face_size", sa.Integer, nullable=True),
        sa.Column("yaw_angle", sa.Float, nullable=True),
        sa.Column("pitch_angle", sa.Float, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("is_good_quality", sa.Boolean, nullable=True),
        sa.Column("checked_at", sa.DateTime, default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("quality_checks")
    op.drop_table("import_logs")
    op.drop_table("embeddings")
    op.drop_table("photos")
    op.drop_table("identities")
