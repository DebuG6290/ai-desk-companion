from abc import ABC, abstractmethod


class DisplayRenderer(ABC):
    @abstractmethod
    def render(self, state):
        pass


class ConsoleDisplay(DisplayRenderer):
    """
    Simple display implementation for testing.
    Later this interface can be replaced by a browser
    or physical SPI display.
    """

    STATE_EMOJIS = {
        "idle": "😌",
        "listening": "👀",
        "thinking": "🤔",
        "speaking": "🙂",
        "curious": "🧐",
        "happy": "😊",
    }

    def render(self, state):
        state_name = state.value

        emoji = self.STATE_EMOJIS.get(
            state_name,
            "🙂",
        )

        print()
        print("┌────────────────────┐")
        print(f"│        {emoji}         │")
        print("│                    │")
        print(f"│     {state_name.upper():<10}     │")
        print("└────────────────────┘")

        return {
            "state": state_name,
            "emoji": emoji,
        }
