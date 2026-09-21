from core.display import ConsoleDisplay
from core.display_controller import DisplayController
from core.state import DeskbotState


def test_display_controller_renders_state():
    display = ConsoleDisplay()
    controller = DisplayController(display)

    result = controller.update(
        DeskbotState.LISTENING
    )

    assert result["state"] == "listening"
    assert result["emoji"] == "👀"


def test_display_controller_skips_duplicate_state():
    display = ConsoleDisplay()
    controller = DisplayController(display)

    first = controller.update(
        DeskbotState.IDLE
    )

    second = controller.update(
        DeskbotState.IDLE
    )

    assert first is not None
    assert second is None
