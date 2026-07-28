from __future__ import annotations

from click.testing import CliRunner
import pytest

from feature.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path


class TestCLI:
    def test_cli_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "feature" in result.output

    def test_cli_init(self, runner, temp_workspace):
        config_path = temp_workspace / "config.yaml"
        result = runner.invoke(main, [
            "--config", str(config_path),
            "init",
            "--base-photos", str(temp_workspace / "photos"),
            "--incoming", str(temp_workspace / "incoming"),
        ])
        assert result.exit_code == 0
        assert config_path.exists()
