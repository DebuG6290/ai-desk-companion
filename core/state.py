from enum import Enum
from threading import Lock


class DeskbotState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    CURIOUS = "curious"
    HAPPY = "happy"


class StateController:
    def __init__(self, event_bus=None, display_controller=None):
        self._state = DeskbotState.IDLE
        self._lock = Lock()
        self.display_controller = display_controller

        if event_bus is not None:
            self._subscribe(event_bus)

        self._render()

    def _subscribe(self, event_bus):
        from core.events import EventTypes

        event_bus.subscribe(
            EventTypes.SPEECH_STARTED,
            self._speech_started,
        )

        event_bus.subscribe(
            EventTypes.TEXT_RECEIVED,
            self._text_received,
        )

        event_bus.subscribe(
            EventTypes.TEXT_RESPONSE,
            self._text_response,
        )

        event_bus.subscribe(
            EventTypes.SPEAKING_STARTED,
            self._speaking_started,
        )

        event_bus.subscribe(
            EventTypes.SPEAKING_ENDED,
            self._speaking_ended,
        )

        event_bus.subscribe(
            EventTypes.UNKNOWN_PERSON_ENTERED,
            self._unknown_person,
        )

        event_bus.subscribe(
            EventTypes.CURIOSITY_TRIGGERED,
            self._curiosity_triggered,
        )

        event_bus.subscribe(
            EventTypes.USER_RETURNED,
            self._user_returned,
        )

        event_bus.subscribe(
            EventTypes.USER_LEFT,
            self._user_left,
        )

    def set_state(self, state):
        if not isinstance(state, DeskbotState):
            raise ValueError("state must be a DeskbotState")

        with self._lock:
            self._state = state

        self._render()

    def get_state(self):
        with self._lock:
            return self._state

    def get_state_name(self):
        return self.get_state().value

    def _render(self):
        if self.display_controller is not None:
            self.display_controller.update(self.get_state())

    def _speech_started(self, event):
        self.set_state(DeskbotState.LISTENING)

    def _text_received(self, event):
        self.set_state(DeskbotState.THINKING)

    def _text_response(self, event):
        response_mode = event.data.get(
            "response_mode",
            "voice_and_display",
        )

        if response_mode == "voice_and_display":
            # Stay in THINKING until actual audio playback begins.
            return

        self.set_state(DeskbotState.HAPPY)

    def _speaking_started(self, event):
        self.set_state(DeskbotState.SPEAKING)

    def _speaking_ended(self, event):
        self.set_state(DeskbotState.IDLE)

    def _unknown_person(self, event):
        self.set_state(DeskbotState.CURIOUS)

    def _curiosity_triggered(self, event):
        self.set_state(DeskbotState.CURIOUS)

    def _user_returned(self, event):
        self.set_state(DeskbotState.HAPPY)

    def _user_left(self, event):
        self.set_state(DeskbotState.IDLE)
