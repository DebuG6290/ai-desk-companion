from core.actions import ActionIntents, ActionTypes
from core.events import Event, EventTypes
from datetime import datetime


class ActionExecutor:
    """
    Converts high-level action requests into capability events.

    It does not contain behaviour policy. It only maps an approved intent
    to the capability needed to carry it out.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._subscribe()

    def _subscribe(self):
        self.event_bus.subscribe(
            EventTypes.ACTION_REQUESTED,
            self._handle_action,
        )

    def _handle_action(self, event):
        action_type = event.data.get("action_type")
        intent = event.data.get("intent")

        if action_type == ActionTypes.IGNORE:
            return

        if intent == ActionIntents.GREET_OWNER:
            self._request_speech("Hey, you're back.")

        elif intent == ActionIntents.NOTICE_UNKNOWN_PERSON:
            self._request_expression("curious")

        elif intent == ActionIntents.ASK_UNKNOWN_PERSON_TO_INTRODUCE:
            self._request_speech(
                "Hey, I don't think we've met. Who are you?"
            )

    def _request_speech(self, text):
        self.event_bus.publish(
            Event(
                type=EventTypes.TEXT_RESPONSE,
                data={
                    "text": text,
                    "response_mode": "voice_and_display",
                    "source": "action_executor",
                },
                timestamp=datetime.now(),
            )
        )

    def _request_expression(self, expression):
        self.event_bus.publish(
            Event(
                type=EventTypes.DISPLAY_REQUESTED,
                data={
                    "expression": expression,
                    "source": "action_executor",
                },
                timestamp=datetime.now(),
            )
        )
