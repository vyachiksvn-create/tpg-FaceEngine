"""Minimal Operator Desktop MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from feature.desktop.operator import OperatorDesktop


class MainWindow(QMainWindow):
    def __init__(self, desktop: OperatorDesktop) -> None:
        super().__init__()
        self.desktop = desktop
        self.setWindowTitle("TPG FaceEngine — Operator Desktop")
        self.resize(1024, 768)

        central = QWidget()
        layout = QVBoxLayout(central)

        self.photo_label = QLabel("Фото")
        self.photo_label.setFixedSize(400, 400)
        self.photo_label.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.photo_label)

        self.candidates_text = QTextEdit("Кандидаты")
        layout.addWidget(self.candidates_text)

        self.explanation_text = QTextEdit("Почему выбран?")
        layout.addWidget(self.explanation_text)

        buttons = QWidget()
        button_layout = QVBoxLayout(buttons)
        self.confirm_btn = QPushButton("Подтвердить")
        self.new_btn = QPushButton("Новый человек")
        self.skip_btn = QPushButton("Пропустить")
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.skip_btn)
        layout.addWidget(buttons)

        self.setCentralWidget(central)

    def load_photo(self, photo_path: Path) -> None:
        pixmap = QPixmap(str(photo_path))
        if pixmap.isNull():
            pixmap = QPixmap(400, 400)
            pixmap.fill()
        self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), aspectMode=1))
