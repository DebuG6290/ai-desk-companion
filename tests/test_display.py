from core.display import ConsoleDisplay
from core.state import DeskbotState


def test_console_display_idle():
    display = ConsoleDisplay()

    result = display.render(
        DeskbotState.IDLE
    )

    assert result["state"] == "idle"
    assert result["emoji"] == "😌"


def test_console_display_listening():
    display = ConsoleDisplay()

    result = display.render(
        DeskbotState.LISTENING
    )

    assert result["state"] == "listening"
    assert result["emoji"] == "👀"


def test_console_display_thinking():
    display = ConsoleDisplay()

    result = display.render(
        DeskbotState.THINKING
    )

    assert result["state"] == "thinking"
    assert result["emoji"] == "🤔"
