"""Desktop Runner: launch Operator Desktop MVP."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from feature.config import ConfigManager
from feature.desktop.main_window import MainWindow
from feature.desktop.operator import OperatorDesktop
from feature.recognition.engine import RecognitionEngine
from feature.search.index import FaissIndex
from feature.storage.database import DatabaseManager


def main() -> None:
    app = QApplication(sys.argv)
    workspace = Path(r"D:\FaceEngine_Test\Workspace")
    db_path = workspace / "storage" / "faces.db"
    DatabaseManager.get_instance(f"sqlite:///{db_path}")
    config = ConfigManager.get_instance()
    engine = RecognitionEngine(config)
    engine.load_model()
    faiss = FaissIndex(dimension=512)
    desktop = OperatorDesktop(engine=engine, faiss=faiss)
    window = MainWindow(desktop)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
