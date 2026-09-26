from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.world_model import WorldModel


def publish(event_bus, event_type, data=None):
    event_bus.publish(
        Event(
            type=event_type,
            data=data or {},
            timestamp=None,
        )
    )


def test_world_model_tracks_owner_return():
    event_bus = EventBus()
    world = WorldModel(event_bus)

    publish(
        event_bus,
        EventTypes.USER_RETURNED,
        {"distance": 48.0},
    )

    snapshot = world.snapshot()

    assert snapshot.presence == "PRESENT"
    assert snapshot.identity == "YOU"
    assert snapshot.identity_confidence == 48.0
    assert snapshot.unknown_person_present is False


def test_world_model_tracks_unknown_person():
    event_bus = EventBus()
    world = WorldModel(event_bus)

    publish(
        event_bus,
        EventTypes.UNKNOWN_PERSON_ENTERED,
        {"distance": 88.0},
    )

    snapshot = world.snapshot()

    assert snapshot.presence == "PRESENT"
    assert snapshot.identity == "UNKNOWN"
    assert snapshot.unknown_person_present is True
    assert snapshot.identity_confidence == 88.0


def test_world_model_tracks_conversation_lifecycle():
    event_bus = EventBus()
    world = WorldModel(event_bus)

    publish(event_bus, EventTypes.SPEECH_STARTED)

    assert world.snapshot().conversation_active is True

    publish(
        event_bus,
        EventTypes.TEXT_RECEIVED,
        {"text": "hello"},
    )

    assert world.snapshot().conversation_active is True

    publish(event_bus, EventTypes.USER_LEFT)

    snapshot = world.snapshot()

    assert snapshot.presence == "ABSENT"
    assert snapshot.conversation_active is False
