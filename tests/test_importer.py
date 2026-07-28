from __future__ import annotations

from pathlib import Path

import pytest

from feature.import_.importer import compute_sha256, save_thumbnail


class TestImporter:
    def test_compute_sha256(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        sha256 = compute_sha256(test_file)
        assert len(sha256) == 64
        assert sha256 == "b94d27b9934d3e08a52e52d7da7dabfade5f0c38"

    def test_save_thumbnail(self, tmp_path):
        from PIL import Image
        test_image = tmp_path / "test.jpg"
        Image.new("RGB", (512, 512), color="red").save(test_image)
        thumb_path = tmp_path / "thumb.jpg"
        save_thumbnail(test_image, thumb_path, size=128)
        assert thumb_path.exists()
        img = Image.open(thumb_path)
        assert max(img.size) <= 128
