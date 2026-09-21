from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.state import DeskbotState, StateController


def test_initial_state_is_idle():
    state = StateController()

    assert state.get_state() == DeskbotState.IDLE


def test_speech_started_sets_listening():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.SPEECH_STARTED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.LISTENING


def test_text_received_sets_thinking():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RECEIVED,
            data={"text": "Hello"},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.THINKING


def test_voice_response_waits_for_speaking_started():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "Hello",
                "response_mode": "voice_and_display",
            },
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.IDLE

    event_bus.publish(
        Event(
            type=EventTypes.SPEAKING_STARTED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.SPEAKING

def test_display_only_sets_happy():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "The answer is 42",
                "response_mode": "display_only",
            },
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.HAPPY


def test_unknown_person_sets_curious():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.UNKNOWN_PERSON_ENTERED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.CURIOUS


def test_user_returned_sets_happy():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.USER_RETURNED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.HAPPY


def test_user_left_sets_idle():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.USER_LEFT,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.IDLE

def test_speaking_ended_returns_to_idle():
    event_bus = EventBus()
    state = StateController(event_bus)

    event_bus.publish(
        Event(
            type=EventTypes.SPEAKING_STARTED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.SPEAKING

    event_bus.publish(
        Event(
            type=EventTypes.SPEAKING_ENDED,
            data={},
            timestamp=None,
        )
    )

    assert state.get_state() == DeskbotState.IDLE
