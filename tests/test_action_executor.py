from core.action_executor import ActionExecutor
from core.event_bus import EventBus
from core.events import Event, EventTypes


def publish(event_bus, event_type, data=None):
    event_bus.publish(
        Event(
            type=event_type,
            data=data or {},
            timestamp=None,
        )
    )


def test_greet_owner_requests_voice_response():
    event_bus = EventBus()
    ActionExecutor(event_bus)

    responses = []
    event_bus.subscribe(
        EventTypes.TEXT_RESPONSE,
        responses.append,
    )

    publish(
        event_bus,
        EventTypes.ACTION_REQUESTED,
        {
            "action_type": "EXPRESS",
            "intent": "GREET_OWNER",
        },
    )

    assert len(responses) == 1
    assert responses[0].data["text"] == "Hey, you're back."
    assert responses[0].data["response_mode"] == "voice_and_display"


def test_unknown_person_requests_curiosity_expression():
    event_bus = EventBus()
    ActionExecutor(event_bus)

    displays = []
    event_bus.subscribe(
        EventTypes.DISPLAY_REQUESTED,
        displays.append,
    )

    publish(
        event_bus,
        EventTypes.ACTION_REQUESTED,
        {
            "action_type": "EXPRESS",
            "intent": "NOTICE_UNKNOWN_PERSON",
        },
    )

    assert len(displays) == 1
    assert displays[0].data["expression"] == "curious"


def test_introduction_request_becomes_voice_response():
    event_bus = EventBus()
    ActionExecutor(event_bus)

    responses = []
    event_bus.subscribe(
        EventTypes.TEXT_RESPONSE,
        responses.append,
    )

    publish(
        event_bus,
        EventTypes.ACTION_REQUESTED,
        {
            "action_type": "ASK",
            "intent": "ASK_UNKNOWN_PERSON_TO_INTRODUCE",
        },
    )

    assert len(responses) == 1
    assert "Who are you?" in responses[0].data["text"]


def test_ignore_action_does_nothing():
    event_bus = EventBus()
    ActionExecutor(event_bus)

    responses = []
    displays = []

    event_bus.subscribe(EventTypes.TEXT_RESPONSE, responses.append)
    event_bus.subscribe(EventTypes.DISPLAY_REQUESTED, displays.append)

    publish(
        event_bus,
        EventTypes.ACTION_REQUESTED,
        {
            "action_type": "IGNORE",
            "intent": "anything",
        },
    )

    assert responses == []
    assert displays == []
