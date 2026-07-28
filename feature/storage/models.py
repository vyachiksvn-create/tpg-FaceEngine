from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    LargeBinary,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column

Base = declarative_base()


class ImportStatus(str, Enum):
    PENDING = "pending"
    IMPORTED = "imported"
    DUPLICATE = "duplicate"
    ERROR = "error"
    REJECTED = "rejected"


class Identity(Base):
    __tablename__ = "identities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    original_folder_name: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="identity", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Identity(id={self.id}, display_name='{self.display_name}')>"


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("identities.id"), nullable=True, index=True
    )
    file_path: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    thumbnail_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    identity: Mapped["Identity | None"] = relationship("Identity", back_populates="photos")
    embeddings: Mapped[list["Embedding"]] = relationship("Embedding", back_populates="photo", cascade="all, delete-orphan")
    quality_checks: Mapped[list["QualityCheck"]] = relationship("QualityCheck", back_populates="photo", cascade="all, delete-orphan")
    import_logs: Mapped[list["ImportLog"]] = relationship("ImportLog", back_populates="photo")

    __table_args__ = (
        Index("idx_photos_identity_id", "identity_id"),
        Index("idx_photos_sha256", "sha256"),
    )

    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, file_path='{self.file_path}')>"


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"), nullable=False, index=True)
    embedding_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    photo: Mapped["Photo"] = relationship("Photo", back_populates="embeddings")

    def get_vector(self) -> np.ndarray:
        return np.frombuffer(self.embedding_vector, dtype=np.float32)

    def set_vector(self, vector: np.ndarray) -> None:
        self.embedding_vector = vector.astype(np.float32).tobytes()

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, photo_id={self.photo_id}, model='{self.model_name}')>"


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[ImportStatus] = mapped_column(
        SQLEnum(ImportStatus), default=ImportStatus.PENDING, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    photo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("photos.id"), nullable=True
    )

    photo: Mapped["Photo | None"] = relationship("Photo", back_populates="import_logs")

    __table_args__ = (
        Index("idx_import_logs_status", "status"),
        Index("idx_import_logs_sha256", "sha256"),
    )

    def __repr__(self) -> str:
        return f"<ImportLog(id={self.id}, file_path='{self.file_path}', status={self.status})>"


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id"), nullable=False, index=True
    )
    blur_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    face_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yaw_angle: Mapped[float | None] = mapped_column(Float, nullable=True)
    pitch_angle: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_good_quality: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    photo: Mapped["Photo"] = relationship("Photo", back_populates="quality_checks")

    def __repr__(self) -> str:
        return (
            f"<QualityCheck(id={self.id}, photo_id={self.photo_id}, "
            f"blur={self.blur_score}, good={self.is_good_quality})>"
        )