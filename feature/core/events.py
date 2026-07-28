from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Coroutine, Protocol, Sequence


class EventPriority(int, Enum):
    LOW = 10
    NORMAL = 50
    HIGH = 100
    CRITICAL = 200


@dataclass
class Event:
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: float = field(default_factory=time.time)
    source: str | None = None
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: str | None = None


Handler = Callable[[Event], None]
AsyncHandler = Callable[[Event], Coroutine[None, None, None]]
HandlerLike = Handler | AsyncHandler


@dataclass
class Subscription:
    handler: HandlerLike
    event_type: str | None = None
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False


class IService(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...


class EventBus:
    def __init__(self) -> None:
        self._subscriptions: list[Subscription] = []

    def subscribe(
        self,
        handler: HandlerLike,
        event_type: str | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
    ) -> str:
        sub = Subscription(
            handler=handler,
            event_type=event_type,
            priority=priority,
            once=once,
        )
        self._subscriptions.append(sub)
        self._subscriptions.sort(key=lambda s: s.priority.value, reverse=True)
        return f"sub_{id(sub)}"

    def unsubscribe(self, subscription_id: str) -> bool:
        target_id = int(subscription_id.split("_")[-1])
        for i, sub in enumerate(self._subscriptions):
            if id(sub) == target_id:
                self._subscriptions.pop(i)
                return True
        return False

    def publish(self, event: Event) -> list[Event]:
        handled: list[Event] = []
        remaining: list[Subscription] = []

        for sub in self._subscriptions:
            if sub.event_type is None or sub.event_type == event.event_type:
                try:
                    sub.handler(event)
                except Exception as exc:
                    from loguru import logger
                    logger.error(f"Event handler error: {exc}")
                if sub.once:
                    handled.append(event)
                else:
                    remaining.append(sub)
            else:
                remaining.append(sub)

        self._subscriptions = remaining
        return handled

    def clear(self) -> None:
        self._subscriptions.clear()


DOMAIN_EVENTS = {
    "workspace.opened",
    "workspace.closed",
    "workspace.created",
    "workspace.deleted",
    "profile.changed",
    "photo.imported",
    "photo.removed",
    "photo.updated",
    "identity.created",
    "identity.updated",
    "identity.merged",
    "recognition.finished",
    "search.finished",
    "import.started",
    "import.finished",
    "import.progress",
    "backup.created",
    "history.recorded",
}