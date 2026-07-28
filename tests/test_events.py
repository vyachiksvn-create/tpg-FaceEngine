from __future__ import annotations

import pytest

from feature.core.events import Event, EventBus, EventPriority


class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(handler, event_type="test")
        bus.publish(Event(event_type="test", payload={"value": 42}))
        assert len(received) == 1
        assert received[0].payload["value"] == 42

    def test_unsubscribe(self):
        bus = EventBus()
        received = []

        def handler(event: Event) -> None:
            received.append(event)

        sub_id = bus.subscribe(handler, event_type="test")
        bus.publish(Event(event_type="test"))
        assert len(received) == 1
        bus.unsubscribe(sub_id)
        bus.publish(Event(event_type="test"))
        assert len(received) == 1

    def test_once_subscription(self):
        bus = EventBus()
        received = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(handler, event_type="test", once=True)
        bus.publish(Event(event_type="test"))
        bus.publish(Event(event_type="test"))
        assert len(received) == 1

    def test_priority(self):
        bus = EventBus()
        order = []

        def low(event: Event) -> None:
            order.append("low")

        def high(event: Event) -> None:
            order.append("high")

        bus.subscribe(low, event_type="test", priority=EventPriority.LOW)
        bus.subscribe(high, event_type="test", priority=EventPriority.HIGH)
        bus.publish(Event(event_type="test"))
        assert order == ["high", "low"]

    def test_filter_by_type(self):
        bus = EventBus()
        received = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(handler, event_type="type_a")
        bus.publish(Event(event_type="type_b"))
        assert len(received) == 0