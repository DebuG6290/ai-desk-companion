from dataclasses import dataclass
from datetime import datetime
from threading import Lock


@dataclass
class WorldSnapshot:
    presence: str
    identity: str
    identity_confidence: float | None
    unknown_person_present: bool
    conversation_active: bool
    deskbot_state: str
    last_event_type: str | None
    last_event_timestamp: datetime | None
    last_interaction_timestamp: datetime | None


class WorldModel:
    """
    Tracks what is true about Deskbot's current environment.

    WorldModel is ephemeral state. It is intentionally not a memory store.
    """

    def __init__(self, event_bus=None):
        self._lock = Lock()

        self.presence = "ABSENT"
        self.identity = "UNKNOWN"
        self.identity_confidence = None
        self.unknown_person_present = False
        self.conversation_active = False
        self.deskbot_state = "idle"

        self.last_event_type = None
        self.last_event_timestamp = None
        self.last_interaction_timestamp = None

        if event_bus is not None:
            self._subscribe(event_bus)

    def _subscribe(self, event_bus):
        from core.events import EventTypes

        subscriptions = {
            EventTypes.PERSON_PRESENT: self._person_present,
            EventTypes.PERSON_ABSENT: self._person_absent,
            EventTypes.USER_RETURNED: self._user_returned,
            EventTypes.USER_LEFT: self._user_left,
            EventTypes.UNKNOWN_PERSON_ENTERED: self._unknown_entered,
            EventTypes.SPEECH_STARTED: self._speech_started,
            EventTypes.SPEECH_ENDED: self._speech_ended,
            EventTypes.TEXT_RECEIVED: self._text_received,
            EventTypes.TEXT_RESPONSE: self._text_response,
            EventTypes.SPEAKING_STARTED: self._speaking_started,
            EventTypes.SPEAKING_ENDED: self._speaking_ended,
        }

        for event_type, handler in subscriptions.items():
            event_bus.subscribe(event_type, handler)

    def _record_event(self, event):
        with self._lock:
            self.last_event_type = event.type
            self.last_event_timestamp = event.timestamp

    def _person_present(self, event):
        self._record_event(event)
        with self._lock:
            self.presence = "PRESENT"

    def _person_absent(self, event):
        self._record_event(event)
        with self._lock:
            self.presence = "ABSENT"
            self.identity = "UNKNOWN"
            self.identity_confidence = None
            self.unknown_person_present = False
            self.conversation_active = False

    def _user_returned(self, event):
        self._record_event(event)
        with self._lock:
            self.presence = "PRESENT"
            self.identity = "YOU"
            self.identity_confidence = self._distance_as_confidence(event)
            self.unknown_person_present = False
            self.last_interaction_timestamp = event.timestamp

    def _user_left(self, event):
        self._person_absent(event)

    def _unknown_entered(self, event):
        self._record_event(event)
        with self._lock:
            self.presence = "PRESENT"
            self.identity = "UNKNOWN"
            self.identity_confidence = self._distance_as_confidence(event)
            self.unknown_person_present = True

    def _speech_started(self, event):
        self._record_event(event)
        with self._lock:
            self.conversation_active = True
            self.last_interaction_timestamp = event.timestamp

    def _speech_ended(self, event):
        self._record_event(event)

    def _text_received(self, event):
        self._record_event(event)
        with self._lock:
            self.conversation_active = True
            self.last_interaction_timestamp = event.timestamp

    def _text_response(self, event):
        self._record_event(event)
        with self._lock:
            self.conversation_active = True
            self.last_interaction_timestamp = event.timestamp

    def _speaking_started(self, event):
        self._record_event(event)
        with self._lock:
            self.deskbot_state = "speaking"

    def _speaking_ended(self, event):
        self._record_event(event)
        with self._lock:
            self.deskbot_state = "idle"

    @staticmethod
    def _distance_as_confidence(event):
        value = event.data.get("confidence")
        if value is None:
            value = event.data.get("distance")
        if value is None:
            return None
        return float(value)

    def set_deskbot_state(self, state):
        with self._lock:
            self.deskbot_state = state

    def end_conversation(self):
        with self._lock:
            self.conversation_active = False

    def snapshot(self):
        with self._lock:
            return WorldSnapshot(
                presence=self.presence,
                identity=self.identity,
                identity_confidence=self.identity_confidence,
                unknown_person_present=self.unknown_person_present,
                conversation_active=self.conversation_active,
                deskbot_state=self.deskbot_state,
                last_event_type=self.last_event_type,
                last_event_timestamp=self.last_event_timestamp,
                last_interaction_timestamp=self.last_interaction_timestamp,
            )
