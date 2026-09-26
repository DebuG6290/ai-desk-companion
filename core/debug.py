from collections import deque
from datetime import datetime
import json
import threading


class DebugTracker:
    """Small in-memory observability layer for the prototype."""

    def __init__(self, max_events=100):
        self._lock = threading.Lock()
        self._events = deque(maxlen=max_events)
        self._camera = {
            "people": [],
            "faces": [],
            "frame_count": 0,
            "fps": 0.0,
            "timestamp": None,
        }
        self._state = "idle"
        self._world = {}
        self._decision = None
        self._action = None

    def record_event(self, event_type, data=None):
        with self._lock:
            self._events.append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": event_type,
                    "data": data or {},
                }
            )

    def update_camera(self, people, faces, frame_count, fps=0.0):
        with self._lock:
            self._camera = {
                "people": people,
                "faces": faces,
                "frame_count": frame_count,
                "fps": round(float(fps), 1),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

    def update_state(self, state):
        with self._lock:
            self._state = state

    def update_world(self, snapshot):
        with self._lock:
            self._world = {
                "presence": snapshot.presence,
                "identity": snapshot.identity,
                "identity_confidence": snapshot.identity_confidence,
                "unknown_person_present": snapshot.unknown_person_present,
                "conversation_active": snapshot.conversation_active,
                "deskbot_state": snapshot.deskbot_state,
                "last_event_type": snapshot.last_event_type,
            }

    def update_decision(self, data):
        with self._lock:
            self._decision = dict(data)

    def update_action(self, data):
        with self._lock:
            self._action = dict(data)

    def snapshot(self):
        with self._lock:
            return {
                "camera": dict(self._camera),
                "state": self._state,
                "world": dict(self._world),
                "decision": dict(self._decision) if self._decision else None,
                "action": dict(self._action) if self._action else None,
                "events": list(self._events),
            }


def json_safe(value):
    return json.loads(json.dumps(value, default=str))
