from core.event_bus import EventBus


def test_subscribe_and_publish():
    bus = EventBus()
    received = []

    bus.subscribe("TEST", received.append)

    from core.events import Event
    bus.publish(Event(type="TEST", data={"value": 1}, timestamp=None))

    assert len(received) == 1
    assert received[0].data["value"] == 1


def test_publishing_without_handlers_is_safe():
    bus = EventBus()
    bus.publish(
        __import__("core.events", fromlist=["Event"]).Event(
            type="UNKNOWN",
            data={},
            timestamp=None,
        )
    )
