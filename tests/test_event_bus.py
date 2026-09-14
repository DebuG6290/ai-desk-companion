from datetime import datetime

from core.event_bus import EventBus
from core.events import Event, EventTypes


def test_event_handler_is_called():
    event_bus = EventBus()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe(EventTypes.USER_RETURNED, handler)

    event = Event(
        type=EventTypes.USER_RETURNED,
        data={},
        timestamp=datetime.now(),
    )

    event_bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].type == EventTypes.USER_RETURNED
    assert received_events[0].data == {}


def test_unhandled_event_does_not_crash():
    event_bus = EventBus()

    event = Event(
        type=EventTypes.TAP_DETECTED,
        data={},
        timestamp=datetime.now(),
    )

    event_bus.publish(event)

def test_multiple_handlers_are_called():
    event_bus = EventBus()

    calls = []

    def handler_one(event):
        calls.append("handler_one")

    def handler_two(event):
        calls.append("handler_two")

    event_bus.subscribe(EventTypes.USER_RETURNED, handler_one)
    event_bus.subscribe(EventTypes.USER_RETURNED, handler_two)

    event = Event(
        type=EventTypes.USER_RETURNED,
        data={},
        timestamp=datetime.now(),
    )

    event_bus.publish(event)

    assert calls == ["handler_one", "handler_two"]
