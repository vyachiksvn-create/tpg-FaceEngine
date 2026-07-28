r"""Alpha Local Test Runner.

Запуск тестов против D:\Base (копия боевой базы).
Использование:
    python scripts/alpha_local_test.py --known "D:\Base" --unknown "D:\Base\x" --workspace "D:\FaceEngine_Test\Workspace"
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from feature.config import ConfigManager
from feature.core import EventBus, WorkspaceManager
from feature.recognition.engine import RecognitionEngine
from feature.recognition.pipeline import RecognitionPipeline
from feature.search.index import FaissIndex
from feature.storage.archive_builder import ArchiveBuilder, ArchiveBuildResult
from feature.storage.database import DatabaseManager


@dataclass
class TestMetrics:
    known_photos: int = 0
    unknown_photos: int = 0
    import_time_s: float = 0.0
    search_time_s: float = 0.0
    avg_search_ms: float = 0.0
    errors: int = 0
    no_face: int = 0
    duplicates: int = 0


class AlphaLocalTest:
    def __init__(self, known_path: Path, unknown_path: Path, workspace_path: Path) -> None:
        self.known_path = Path(known_path)
        self.unknown_path = Path(unknown_path)
        self.workspace_path = Path(workspace_path)
        self.metrics = TestMetrics()

    def run(self) -> TestMetrics:
        logger.info("=== Alpha 0.1 Local Test ===")
        self._prepare_workspace()
        self._count_photos()
        self._run_import()
        self._run_recognition()
        self._print_report()
        return self.metrics

    def _prepare_workspace(self) -> None:
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        ConfigManager.reset()
        config = ConfigManager.get_instance()
        config.paths.workspace = str(self.workspace_path)
        config.paths.base_photos = str(self.known_path)
        config.paths.incoming = str(self.unknown_path)
        config.paths.logs = str(self.workspace_path / "Logs")
        config.paths.thumbnails = str(self.workspace_path / "Thumbnails")
        config.paths.backup = str(self.workspace_path / "Backup")
        config.paths.temp = str(self.workspace_path / "Temp")
        DatabaseManager.get_instance().init_db(create_tables=True)
        logger.info(f"Workspace prepared: {self.workspace_path}")

    def _count_photos(self) -> None:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        self.metrics.known_photos = sum(
            1 for p in self.known_path.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        )
        self.metrics.unknown_photos = sum(
            1 for p in self.unknown_path.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        )
        logger.info(f"Known: {self.metrics.known_photos}, Unknown: {self.metrics.unknown_photos}")

    def _run_import(self) -> None:
        logger.info("=== Import Known ===")
        t0 = time.perf_counter()
        builder = ArchiveBuilder(
            known_path=self.known_path,
            workspace_path=self.workspace_path,
        )
        try:
            result = builder.run()
            self.metrics.import_time_s = time.perf_counter() - t0
            self.metrics.errors = result.errors
            self.metrics.duplicates = result.skipped
            logger.info(f"Imported: {result.imported}, Skipped: {result.skipped}, Errors: {result.errors}")
            logger.info(f"Import time: {self.metrics.import_time_s:.1f}s")
        except Exception as exc:
            logger.error(f"Import failed: {exc}")
            self.metrics.errors += 1

    def _run_recognition(self) -> None:
        logger.info("=== Recognition Unknown ===")
        config = ConfigManager.get_instance()
        engine = RecognitionEngine(config)
        faiss = FaissIndex(dimension=512)
        pipeline = RecognitionPipeline(engine, faiss)
        t0 = time.perf_counter()
        times = []
        unknown_files = [
            p for p in self.unknown_path.rglob("*")
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        for photo_path in unknown_files[:100]:
            try:
                result = pipeline.process_photo(photo_path)
                if result.status == "no_faces":
                    self.metrics.no_face += 1
                elif result.status == "error":
                    self.metrics.no_face += 1
                elif result.status == "found":
                    times.append(result.processing_time_ms)
            except Exception as exc:
                logger.error(f"Recognition failed for {photo_path}: {exc}")
                self.metrics.errors += 1
        self.metrics.search_time_s = time.perf_counter() - t0
        self.metrics.avg_search_ms = sum(times) / len(times) if times else 0.0
        logger.info(f"Processed: {len(unknown_files)}, No face: {self.metrics.no_face}, Errors: {self.metrics.errors}")
        logger.info(f"Avg search: {self.metrics.avg_search_ms:.1f}ms, Total: {self.metrics.search_time_s:.1f}s")

    def _print_report(self) -> None:
        print("\n" + "=" * 60)
        print("ALPHA 0.1 TEST REPORT")
        print("=" * 60)
        print(f"Known photos: {self.metrics.known_photos}")
        print(f"Unknown photos: {self.metrics.unknown_photos}")
        print(f"Import time: {self.metrics.import_time_s:.1f}s")
        print(f"Search time: {self.metrics.search_time_s:.1f}s")
        print(f"Avg search: {self.metrics.avg_search_ms:.1f}ms" if times else "Avg search: n/a (no matches)")
        print(f"No face: {self.metrics.no_face}")
        print(f"Errors: {self.metrics.errors}")
        print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Alpha 0.1 Local Test Runner")
    parser.add_argument("--known", type=str, default=r"D:\Base", help="Path to known persons")
    parser.add_argument("--unknown", type=str, default=r"D:\Base\x", help="Path to unknown photos")
    parser.add_argument("--workspace", type=str, default=r"D:\FaceEngine_Test\Workspace", help="Workspace path")
    args = parser.parse_args()

    test = AlphaLocalTest(
        known_path=Path(args.known),
        unknown_path=Path(args.unknown),
        workspace_path=Path(args.workspace),
    )
    test.run()


if __name__ == "__main__":
    main()