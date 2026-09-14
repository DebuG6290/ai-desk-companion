from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    type: str
    data: dict
    timestamp: datetime
