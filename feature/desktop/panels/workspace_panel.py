"""Desktop: Workspace Panel"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feature.core import EventBus, WorkspaceManager


class WorkspacePanel:
    def __init__(self, event_bus: "EventBus", workspace_mgr: "WorkspaceManager") -> None:
        self.event_bus = event_bus
        self.workspace_mgr = workspace_mgr

    def list_workspaces(self) -> list[str]:
        return [ws.name for ws in self.workspace_mgr.list_workspaces()]

    def switch_workspace(self, name: str) -> None:
        self.workspace_mgr.activate(name)