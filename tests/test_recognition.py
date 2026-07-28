from __future__ import annotations

import numpy as np
import pytest

from feature.recognition.engine import FaceDetection, InsightFaceRecognitionEngine, RecognitionEngine
from feature.config import ConfigManager


class TestRecognitionEngine:
    @pytest.fixture
    def config(self):
        ConfigManager.reset()
        config = ConfigManager.get_instance()
        config.recognition.engine = "insightface"
        config.recognition.model = "buffalo_l"
        config.recognition.use_gpu = False
        return config

    def test_create_engine(self, config):
        engine = RecognitionEngine(config)
        assert engine is not None

    def test_detect_faces(self, config):
        engine = RecognitionEngine(config)
        engine.load_model()
        image = np.zeros((640, 640, 3), dtype=np.uint8)
        faces = engine.detect_faces(image)
        assert isinstance(faces, list)
        engine.unload_model()
