from dataclasses import dataclass
from datetime import datetime


class EventTypes:
    USER_RETURNED = "USER_RETURNED"
    USER_LEFT = "USER_LEFT"

    PERSON_PRESENT = "PERSON_PRESENT"
    PERSON_ABSENT = "PERSON_ABSENT"

    UNKNOWN_PERSON_ENTERED = "UNKNOWN_PERSON_ENTERED"

    SPEECH_DETECTED = "SPEECH_DETECTED"
    TAP_DETECTED = "TAP_DETECTED"


@dataclass
class Event:
    type: str
    data: dict
    timestamp: datetime
