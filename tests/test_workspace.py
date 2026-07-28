from __future__ import annotations

import pytest

from feature.core.workspace import WorkspaceManager, WorkspaceStatus


class TestWorkspaceManager:
    def test_create_workspace(self, tmp_path):
        mgr = WorkspaceManager(tmp_path)
        ws = mgr.create("test")
        assert ws.name == "test"
        assert ws.status == WorkspaceStatus.READY
        assert ws.paths.database.endswith("faces.db")

    def test_activate_workspace(self, tmp_path):
        mgr = WorkspaceManager(tmp_path)
        mgr.create("alpha")
        mgr.create("beta")
        ws = mgr.activate("beta")
        assert ws.is_active is True
        assert mgr.active.name == "beta"

    def test_list_workspaces(self, tmp_path):
        mgr = WorkspaceManager(tmp_path)
        mgr.create("alpha")
        mgr.create("beta")
        names = [ws.name for ws in mgr.list_workspaces()]
        assert "alpha" in names
        assert "beta" in names

    def test_delete_workspace(self, tmp_path):
        mgr = WorkspaceManager(tmp_path)
        mgr.create("alpha")
        mgr.create("beta")
        mgr.activate("alpha")
        mgr.delete("beta")
        assert len(mgr.list_workspaces()) == 1