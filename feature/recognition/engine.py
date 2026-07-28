from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from loguru import logger


@dataclass
class FaceDetection:
    bbox: np.ndarray
    kps: np.ndarray
    det_score: float
    landmark_3d: np.ndarray | None = None


@dataclass
class FaceEmbedding:
    vector: np.ndarray
    model_name: str


class BaseRecognitionEngine(ABC):
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> list[FaceDetection]:
        pass

    @abstractmethod
    def get_embedding(self, image: np.ndarray, face: FaceDetection) -> np.ndarray:
        pass

    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def unload_model(self) -> None:
        pass


class InsightFaceRecognitionEngine(BaseRecognitionEngine):
    def __init__(self, config: Any) -> None:
        self.config = config
        self.model_name = config.recognition.model
        self.ctx_id = 0 if config.recognition.use_gpu else -1
        self._app: FaceAnalysis | None = None
        self._prepared = False

    def load_model(self) -> None:
        if self._prepared:
            return
        logger = self._get_logger()
        logger.info(f"Загрузка модели InsightFace: {self.model_name}")
        self._app = FaceAnalysis(
            name=self.model_name,
            allowed_modules=["detection", "recognition"],
            providers=["CPUExecutionProvider"] if self.ctx_id == -1 else ["CUDAExecutionProvider"],
        )
        self._app.prepare(ctx_id=self.ctx_id, det_size=(640, 640))
        self._prepared = True
        logger.info("Модель InsightFace загружена")

    def unload_model(self) -> None:
        if self._app:
            del self._app
            self._app = None
            self._prepared = False
            logger = self._get_logger()
            logger.info("Модель InsightFace выгружена")

    def detect_faces(self, image: np.ndarray) -> list[FaceDetection]:
        if not self._prepared:
            self.load_model()
        assert self._app is not None
        faces = self._app.get(image)
        result = []
        for face in faces:
            detection = FaceDetection(
                bbox=face.bbox,
                kps=face.kps,
                det_score=face.det_score,
                landmark_3d=getattr(face, "landmark_3d", None),
            )
            result.append(detection)
        return result

    def get_embedding(self, image: np.ndarray, face: FaceDetection) -> np.ndarray:
        if not self._prepared:
            self.load_model()
        assert self._app is not None
        faces = self._app.get(image)
        for f in faces:
            if np.allclose(f.bbox, face.bbox):
                return f.normed_embedding
        raise ValueError("Лицо не найдено в изображении")

    def _get_logger(self) -> Any:
        return logger


class RecognitionEngine:
    def __init__(self, config: Any) -> None:
        self.config = config
        self._engine: BaseRecognitionEngine | None = None

    def _get_engine(self) -> BaseRecognitionEngine:
        if self._engine is None:
            engine_type = self.config.recognition.engine
            if engine_type == "insightface":
                self._engine = InsightFaceRecognitionEngine(self.config)
            else:
                raise ValueError(f"Неподдерживаемый движок распознавания: {engine_type}")
            self._engine.load_model()
        return self._engine

    def detect_faces(self, image: np.ndarray) -> list[FaceDetection]:
        return self._get_engine().detect_faces(image)

    def get_embedding(self, image: np.ndarray, face: FaceDetection) -> np.ndarray:
        return self._get_engine().get_embedding(image, face)

    def load_model(self) -> None:
        self._get_engine().load_model()

    def unload_model(self) -> None:
        if self._engine:
            self._engine.unload_model()
            self._engine = None
