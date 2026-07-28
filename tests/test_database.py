from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from feature.config import ConfigManager
from feature.storage.database import DatabaseManager
from feature.storage.models import Base, Identity, Photo, Embedding, ImportLog, ImportStatus


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        ConfigManager.reset()
        config = ConfigManager.get_instance()
        config.paths.workspace = tmpdir
        config.paths.logs = str(Path(tmpdir) / "logs")
        config.paths.thumbnails = str(Path(tmpdir) / "thumbnails")
        config.create_workspace(config.paths)
        db = DatabaseManager.get_instance(f"sqlite:///{tmpdir}/test.db")
        db.init_db(create_tables=True)
        yield db
        DatabaseManager.reset()
        ConfigManager.reset()


class TestDatabase:
    def test_init_db(self, temp_db):
        assert temp_db.engine is not None

    def test_create_identity(self, temp_db):
        with temp_db.get_session() as session:
            identity = Identity(full_name="Test Person")
            session.add(identity)
            session.commit()
            assert identity.id is not None

    def test_create_photo(self, temp_db):
        with temp_db.get_session() as session:
            identity = Identity(full_name="Test Person")
            session.add(identity)
            session.flush()
            photo = Photo(
                identity_id=identity.id,
                file_path="/test/photo.jpg",
                sha256="abc123",
            )
            session.add(photo)
            session.commit()
            assert photo.id is not None

    def test_create_embedding(self, temp_db):
        import numpy as np
        with temp_db.get_session() as session:
            identity = Identity(full_name="Test Person")
            session.add(identity)
            session.flush()
            photo = Photo(
                identity_id=identity.id,
                file_path="/test/photo.jpg",
                sha256="abc123",
            )
            session.add(photo)
            session.flush()
            embedding = Embedding(
                photo_id=photo.id,
                model_name="test_model",
            )
            embedding.set_vector(np.array([0.1, 0.2, 0.3], dtype=np.float32))
            session.add(embedding)
            session.commit()
            vector = embedding.get_vector()
            assert np.allclose(vector, [0.1, 0.2, 0.3])

    def test_import_log(self, temp_db):
        with temp_db.get_session() as session:
            log = ImportLog(file_path="/test/photo.jpg", sha256="abc123", status=ImportStatus.IMPORTED)
            session.add(log)
            session.commit()
            assert log.id is not None
