"""TPG Core: event bus, workspace, profiles, plugins, history, decisions, jobs, backup."""

from feature.core.decision import DecisionEngine, DecisionResult, Candidate
from feature.core.events import DOMAIN_EVENTS, Event, EventBus, EventPriority, Handler, AsyncHandler, IService, Subscription
from feature.core.history import HistoryEntry, HistoryManager, ActionType
from feature.core.jobs import Job, JobManager, JobStatus
from feature.core.backup import BackupManager
from feature.core.plugin import PluginDescriptor, PluginManager, RecognitionPlugin, SearchPlugin
from feature.core.profile import ProfileConfig, ProfileManager, ProfileSnapshot
from feature.core.workspace import Workspace, WorkspaceManager, WorkspacePaths, WorkspaceStatus

__all__ = [
    "DOMAIN_EVENTS",
    "Event",
    "EventBus",
    "EventPriority",
    "Handler",
    "AsyncHandler",
    "IService",
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
    "Job",
    "JobManager",
    "JobStatus",
    "BackupManager",
]