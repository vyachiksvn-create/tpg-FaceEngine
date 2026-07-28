"""TPG Core: event bus, workspace, profiles, plugins, history, decisions."""

from feature.core.decision import DecisionEngine, DecisionResult, Candidate
from feature.core.events import Event, EventBus, EventPriority, Handler, AsyncHandler, Subscription
from feature.core.history import HistoryEntry, HistoryManager, ActionType
from feature.core.plugin import PluginDescriptor, PluginManager, RecognitionPlugin, SearchPlugin
from feature.core.profile import ProfileConfig, ProfileManager, ProfileSnapshot
from feature.core.workspace import Workspace, WorkspaceManager, WorkspacePaths, WorkspaceStatus

__all__ = [
    "Event",
    "EventBus",
    "EventPriority",
    "Handler",
    "AsyncHandler",
    "Subscription",
    "Workspace",
    "WorkspaceManager",
    "WorkspacePaths",
    "WorkspaceStatus",
    "ProfileConfig",
    "ProfileManager",
    "ProfileSnapshot",
    "PluginDescriptor",
    "PluginManager",
    "RecognitionPlugin",
    "SearchPlugin",
    "HistoryEntry",
    "HistoryManager",
    "ActionType",
    "DecisionEngine",
    "DecisionResult",
    "Candidate",
]