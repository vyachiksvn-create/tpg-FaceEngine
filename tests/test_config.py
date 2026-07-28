from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from feature.config import ConfigManager


@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.dump(
            {
                "version": "1.0",
                "paths": {"workspace": "/tmp/test_workspace"},
                "profiles": {
                    "default": {
                        "name": "Default",
                        "recognition": {"engine": "insightface", "model": "buffalo_l"},
                    }
                },
                "active_profile": "default",
            },
            f,
        )
        return Path(f.name)


class TestConfigManager:
    def test_load_config(self, temp_config_file):
        ConfigManager.reset()
        config = ConfigManager.get_instance(temp_config_file)
        assert config.version == "1.0"
        assert config.active_profile == "default"
        assert "default" in config.profiles
        ConfigManager.reset()

    def test_default_config(self):
        ConfigManager.reset()
        config = ConfigManager.get_instance()
        assert config.version == "1.0"
        assert "default" in config.profiles
        ConfigManager.reset()

    def test_active_profile(self, temp_config_file):
        ConfigManager.reset()
        config = ConfigManager.get_instance(temp_config_file)
        profile = config.active
        assert profile.name == "Default"
        assert profile.recognition.engine == "insightface"
        ConfigManager.reset()

    def test_save_config(self, temp_config_file):
        ConfigManager.reset()
        config = ConfigManager.get_instance(temp_config_file)
        config.save_config(config, temp_config_file)
        with open(temp_config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["version"] == "1.0"
        ConfigManager.reset()

    def test_create_workspace(self, temp_config_file):
        ConfigManager.reset()
        config = ConfigManager.get_instance(temp_config_file)
        config.create_workspace(config.paths)
        assert Path("/tmp/test_workspace").exists()
        ConfigManager.reset()
