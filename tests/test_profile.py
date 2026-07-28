from __future__ import annotations

import pytest

from feature.core.profile import ProfileConfig, ProfileManager


class TestProfileManager:
    def test_save_and_load(self, tmp_path):
        mgr = ProfileManager(tmp_path / "profiles")
        profile = ProfileConfig(
            name="test",
            description="Test profile",
            recognition={"engine": "insightface", "threshold": 0.7},
        )
        mgr.save(profile)
        loaded = mgr.load("test")
        assert loaded.name == "test"
        assert loaded.recognition["threshold"] == 0.7

    def test_list_profiles(self, tmp_path):
        mgr = ProfileManager(tmp_path / "profiles")
        mgr.save(ProfileConfig(name="alpha"))
        mgr.save(ProfileConfig(name="beta"))
        names = mgr.list_profiles()
        assert "alpha" in names
        assert "beta" in names

    def test_duplicate(self, tmp_path):
        mgr = ProfileManager(tmp_path / "profiles")
        mgr.save(ProfileConfig(name="original"))
        dup = mgr.duplicate("original", "copy")
        assert dup.name == "copy"
        assert "copy" in mgr.list_profiles()

    def test_export_import(self, tmp_path):
        mgr = ProfileManager(tmp_path / "profiles")
        profile = ProfileConfig(name="export_test", recognition={"model": "buffalo_l"})
        mgr.save(profile)
        export_path = tmp_path / "export.json"
        mgr.export_profile("export_test", export_path)
        assert export_path.exists()
        imported = mgr.import_profile(export_path)
        assert imported.recognition["model"] == "buffalo_l"

    def test_compare(self, tmp_path):
        mgr = ProfileManager(tmp_path / "profiles")
        mgr.save(ProfileConfig(name="a", recognition={"threshold": 0.5}))
        mgr.save(ProfileConfig(name="b", recognition={"threshold": 0.7}))
        diff = mgr.compare("a", "b")
        assert "recognition.threshold" in diff