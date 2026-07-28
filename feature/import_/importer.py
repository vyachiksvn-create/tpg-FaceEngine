from __future__ import annotations

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np
from loguru import logger
from PIL import Image, ImageOps

from feature.config import ConfigManager
from feature.storage.database import DatabaseManager, get_session
from feature.storage.identity_parser import IdentityParser
from feature.storage.models import (
    Embedding,
    Identity,
    ImportLog,
    ImportStatus,
    Photo,
    QualityCheck,
)
from feature.recognition.engine import RecognitionEngine


@dataclass
class ImportProgress:
    total: int = 0
    processed: int = 0
    imported: int = 0
    skipped: int = 0
    errors: int = 0
    current_file: str = ""

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.processed / self.total) * 100

    @property
    def eta_seconds(self) -> float | None:
        if self.processed == 0:
            return None
        return (self.total - self.processed) / self.processed


def compute_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_thumbnail(image_path: Path, thumbnail_path: Path, size: int = 256) -> None:
    try:
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85)
    except Exception as e:
        logger.warning(f"Не удалось создать миниатюру {image_path}: {e}")


def assess_quality(image: np.ndarray, face_box: tuple[int, int, int, int]) -> dict[str, Any]:
    x1, y1, x2, y2 = face_box
    face_crop = image[y1:y2, x1:x2]

    if face_crop.size == 0:
        return {"blur_score": 0.0, "face_size": 0, "yaw_angle": 0.0, "pitch_angle": 0.0, "confidence": 0.0}

    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    face_size = max(x2 - x1, y2 - y1)

    return {
        "blur_score": blur_score,
        "face_size": face_size,
        "yaw_angle": 0.0,
        "pitch_angle": 0.0,
        "confidence": 1.0,
    }


def process_single_image(
    image_path: Path,
    config: Any,
    recognition_engine: RecognitionEngine,
    progress_callback: Callable[[ImportProgress], None] | None = None,
) -> ImportLog:
    sha256 = compute_sha256(image_path)
    log = ImportLog(file_path=str(image_path), sha256=sha256, status=ImportStatus.PENDING)

    with get_session() as session:
        existing = session.query(ImportLog).filter_by(sha256=sha256).first()
        if existing:
            if existing.status == ImportStatus.IMPORTED and existing.photo_id:
                log.status = ImportStatus.DUPLICATE
                log.photo_id = existing.photo_id
                logger.debug(f"Дубликат: {image_path}")
                return log
            elif existing.status == ImportStatus.ERROR:
                session.delete(existing)
                session.commit()

        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError("Не удалось прочитать изображение")

            height, width = image.shape[:2]

            faces = recognition_engine.detect_faces(image)
            if not faces:
                log.status = ImportStatus.REJECTED
                log.error_message = "Лица не обнаружены"
                logger.warning(f"Лица не обнаружены: {image_path}")
                return log

            thumbnail_rel = None
            if config.import_.save_thumbnails:
                thumb_dir = Path(config.paths.thumbnails)
                thumb_dir.mkdir(parents=True, exist_ok=True)
                thumbnail_name = f"{sha256[:16]}.jpg"
                thumbnail_path = thumb_dir / thumbnail_name
                save_thumbnail(image_path, thumbnail_path, config.gui.thumbnail_size)
                thumbnail_rel = str(thumbnail_path)

            primary_face = faces[0]
            bbox = primary_face.bbox.astype(int)
            quality_data = assess_quality(image, tuple(bbox))

            if config.import_.quality_check:
                qc = QualityCheck(
                    blur_score=quality_data.get("blur_score"),
                    face_size=quality_data.get("face_size"),
                    yaw_angle=quality_data.get("yaw_angle"),
                    pitch_angle=quality_data.get("pitch_angle"),
                    confidence=quality_data.get("confidence"),
                    is_good_quality=quality_data.get("blur_score", 0) > config.quality.max_blur_threshold,
                )
            else:
                qc = None

            folder_name = image_path.parent.name
            display_name, extra_metadata = IdentityParser.parse_folder_name(folder_name)
            metadata_json = IdentityParser.build_metadata_json(extra_metadata)
            identity = Identity(
                display_name=display_name,
                original_folder_name=folder_name,
                metadata_json=metadata_json,
            )
            session.add(identity)
            session.flush()

            photo = Photo(
                identity_id=identity.id,
                file_path=str(image_path),
                sha256=sha256,
                width=width,
                height=height,
                thumbnail_path=thumbnail_rel,
                is_primary=True,
            )
            session.add(photo)
            session.flush()

            embedding_vector = recognition_engine.get_embedding(image, primary_face)
            embedding = Embedding(
                photo_id=photo.id,
                model_name=config.recognition.model,
            )
            embedding.set_vector(embedding_vector)
            session.add(embedding)

            if qc:
                qc.photo_id = photo.id
                session.add(qc)

            log.status = ImportStatus.IMPORTED
            log.imported_at = datetime.utcnow()
            log.photo_id = photo.id

            logger.debug(f"Импортировано: {image_path}")

        except Exception as e:
            log.status = ImportStatus.ERROR
            log.error_message = str(e)
            logger.error(f"Ошибка импорта {image_path}: {e}")

        session.add(log)
        session.commit()

    return log


class PhotoImporter:
    def __init__(self, config: Any = None) -> None:
        self.config = config or ConfigManager.get_instance()
        self.recognition_engine = RecognitionEngine(self.config)
        self.db = DatabaseManager.get_instance()

    def import_folder(
        self,
        folder_path: Path,
        progress_callback: Callable[[ImportProgress], None] | None = None,
        stop_event: Any = None,
    ) -> ImportProgress:
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Каталог не найден: {folder_path}")

        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        image_files = [
            p for p in folder_path.rglob("*")
            if p.is_file() and p.suffix.lower() in image_extensions
        ]
        total = len(image_files)
        logger.info(f"Найдено изображений для импорта: {total}")

        progress = ImportProgress(total=total)

        with ThreadPoolExecutor(max_workers=self.config.performance.import_threads) as executor:
            future_to_file = {
                executor.submit(
                    process_single_image, img, self.config, self.recognition_engine, progress_callback
                ): img
                for img in image_files
            }

            for future in as_completed(future_to_file):
                if stop_event and stop_event.is_set():
                    logger.info("Импорт прерван пользователем")
                    break

                img = future_to_file[future]
                try:
                    log = future.result()
                    if log.status == ImportStatus.IMPORTED:
                        progress.imported += 1
                    elif log.status == ImportStatus.DUPLICATE:
                        progress.skipped += 1
                    elif log.status in (ImportStatus.ERROR, ImportStatus.REJECTED):
                        progress.errors += 1
                except Exception as e:
                    logger.error(f"Ошибка обработки {img}: {e}")
                    progress.errors += 1

                progress.processed += 1
                progress.current_file = str(img)
                if progress_callback:
                    progress_callback(progress)

        logger.info(
            f"Импорт завершен: {progress.imported} импортировано, "
            f"{progress.skipped} пропущено, {progress.errors} ошибок"
        )
        return progress

    def import_single(self, image_path: Path) -> ImportLog:
        return process_single_image(image_path, self.config, self.recognition_engine)
