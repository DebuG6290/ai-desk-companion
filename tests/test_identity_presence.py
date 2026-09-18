from datetime import datetime

from core.event_bus import EventBus
from core.events import EventTypes
from core.identity import IdentitySmoother


def test_identity_smoother_requires_multiple_frames():
    smoother = IdentitySmoother(
        required_frames=3
    )

    assert smoother.update("UNKNOWN") == "UNKNOWN"

    assert smoother.update("YOU") == "UNKNOWN"
    assert smoother.update("YOU") == "UNKNOWN"

    assert smoother.update("YOU") == "YOU"


def test_identity_smoother_does_not_repeat_identity():
    smoother = IdentitySmoother(
        required_frames=3
    )

    smoother.update("YOU")
    smoother.update("YOU")
    smoother.update("YOU")

    assert smoother.update("YOU") == "YOU"


def test_event_bus_handles_user_returned():
    event_bus = EventBus()

    received = []

    def handler(event):
        received.append(event)

    event_bus.subscribe(
        EventTypes.USER_RETURNED,
        handler,
    )

    event_bus.publish(
        type(
            "Event",
            (),
            {
                "type": EventTypes.USER_RETURNED,
                "data": {},
                "timestamp": datetime.now(),
            },
        )()
    )

    assert len(received) == 1
    assert received[0].type == EventTypes.USER_RETURNED
