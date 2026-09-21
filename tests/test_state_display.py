from core.display import ConsoleDisplay
from core.display_controller import DisplayController
from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.state import DeskbotState, StateController


def test_event_changes_display_state():
    event_bus = EventBus()

    display = ConsoleDisplay()

    display_controller = DisplayController(
        display
    )

    StateController(
        event_bus=event_bus,
        display_controller=display_controller,
    )

    event_bus.publish(
        Event(
            type=EventTypes.SPEECH_STARTED,
            data={},
            timestamp=None,
        )
    )

    assert (
        display_controller.current_state
        == DeskbotState.LISTENING
    )


def test_response_waits_for_actual_speaking():
    event_bus = EventBus()

    display = ConsoleDisplay()

    display_controller = DisplayController(
        display
    )

    StateController(
        event_bus=event_bus,
        display_controller=display_controller,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "Hello!",
                "response_mode": "voice_and_display",
            },
            timestamp=None,
        )
    )

    assert (
        display_controller.current_state
        == DeskbotState.IDLE
    )

    event_bus.publish(
        Event(
            type=EventTypes.SPEAKING_STARTED,
            data={},
            timestamp=None,
        )
    )

    assert (
        display_controller.current_state
        == DeskbotState.SPEAKING
    )

    event_bus.publish(
        Event(
            type=EventTypes.SPEAKING_ENDED,
            data={},
            timestamp=None,
        )
    )

    assert (
        display_controller.current_state
        == DeskbotState.IDLE
    )
