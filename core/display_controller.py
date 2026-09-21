from core.state import DeskbotState
from core.display import DisplayRenderer


class DisplayController:
    def __init__(
        self,
        display: DisplayRenderer,
    ):
        self.display = display
        self.current_state = None

    def update(self, state):
        if not isinstance(state, DeskbotState):
            raise ValueError(
                "state must be a DeskbotState"
            )

        if state == self.current_state:
            return

        self.current_state = state

        return self.display.render(state)
