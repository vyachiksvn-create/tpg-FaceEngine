"""Pre-import archive validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ArchiveHealthReport:
    total_folders: int = 0
    total_photos: int = 0
    corrupted: int = 0
    too_small: int = 0
    duplicates: int = 0
    no_face: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    is_healthy: bool = True

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("ARCHIVE DOCTOR REPORT")
        print("=" * 60)
        print(f"Folders:    {self.total_folders}")
        print(f"Photos:     {self.total_photos}")
        print(f"Corrupted:  {self.corrupted}")
        print(f"Too small:  {self.too_small}")
        print(f"Duplicates: {self.duplicates}")
        print(f"No face:    {self.no_face}")
        if self.warnings:
            print("-" * 60)
            print("Warnings:")
            for w in self.warnings:
                print(f"  ⚠ {w}")
        if self.errors:
            print("-" * 60)
            print("Errors:")
            for e in self.errors:
                print(f"  ✗ {e}")
        print("-" * 60)
        status = "READY" if self.is_healthy else "NOT READY"
        print(f"Status: {status}")
        print("=" * 60 + "\n")


class ArchiveDoctor:
    def __init__(self, min_face_size: int = 80, min_file_size_bytes: int = 1024) -> None:
        self.min_face_size = min_face_size
        self.min_file_size_bytes = min_file_size_bytes
        self.report = ArchiveHealthReport()

    def check(self, known_path: Path) -> ArchiveHealthReport:
        self.report = ArchiveHealthReport()
        if not known_path.exists() or not known_path.is_dir():
            self.report.errors.append(f"Path not found: {known_path}")
            self.report.is_healthy = False
            return self.report

        folders = [
            p for p in known_path.rglob("*")
            if p.is_dir() and p.name.lower() not in {"x", "unknown"}
        ]
        if not folders:
            folders = [known_path]
        self.report.total_folders = len(folders)

        files = [
            p for d in folders
            for p in d.rglob("*")
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        self.report.total_photos = len(files)

        for file_path in files:
            try:
                if not file_path.exists():
                    self.report.corrupted += 1
                    self.report.errors.append(f"Missing file: {file_path}")
                    continue
                if file_path.stat().st_size < self.min_file_size_bytes:
                    self.report.corrupted += 1
                    self.report.errors.append(f"Empty or too small: {file_path}")
                    continue
            except Exception as exc:
                self.report.corrupted += 1
                self.report.errors.append(f"Cannot access: {file_path}: {exc}")

        if self.report.corrupted > 0:
            self.report.is_healthy = False

        self.report.print()
        return self.report
