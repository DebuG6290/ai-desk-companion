from core.event_bus import EventBus
from core.events import Event, EventTypes


def test_action_requested_event_can_be_published():
    event_bus = EventBus()
    received = []

    event_bus.subscribe(
        EventTypes.ACTION_REQUESTED,
        received.append,
    )

    event_bus.publish(
        Event(
            type=EventTypes.ACTION_REQUESTED,
            data={
                "action_type": "EXPRESS",
                "intent": "GREET_OWNER",
            },
            timestamp=None,
        )
    )

    assert len(received) == 1
    assert received[0].type == EventTypes.ACTION_REQUESTED
