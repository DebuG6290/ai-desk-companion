from datetime import datetime
from threading import Lock
import time

from core.actions import ActionIntents, ActionPriorities, ActionTypes
from core.events import Event, EventTypes


class DecisionEngine:
    """
    Minimal deterministic behaviour layer.

    It decides what kind of action should happen, but does not execute
    capabilities such as TTS, display, or camera operations.
    """

    def __init__(
        self,
        event_bus,
        world_model,
        cooldown_seconds=30.0,
    ):
        self.event_bus = event_bus
        self.world_model = world_model
        self.cooldown_seconds = cooldown_seconds

        self._lock = Lock()
        self._last_action_time = {}

        self._subscribe()

    def _subscribe(self):
        self.event_bus.subscribe(
            EventTypes.USER_RETURNED,
            self._user_returned,
        )
        self.event_bus.subscribe(
            EventTypes.UNKNOWN_PERSON_ENTERED,
            self._unknown_person_entered,
        )
        self.event_bus.subscribe(
            EventTypes.CURIOSITY_TRIGGERED,
            self._curiosity_triggered,
        )

    def _user_returned(self, event):
        self._request_action(
            action_type=ActionTypes.EXPRESS,
            intent=ActionIntents.GREET_OWNER,
            priority=ActionPriorities.NORMAL,
            reason="Owner returned.",
        )

    def _unknown_person_entered(self, event):
        self._request_action(
            action_type=ActionTypes.EXPRESS,
            intent=ActionIntents.NOTICE_UNKNOWN_PERSON,
            priority=ActionPriorities.NORMAL,
            reason="An unknown person entered the scene.",
        )

    def _curiosity_triggered(self, event):
        snapshot = self.world_model.snapshot()

        if snapshot.deskbot_state == "speaking":
            return

        if snapshot.conversation_active:
            return

        if not snapshot.unknown_person_present:
            return

        self._request_action(
            action_type=ActionTypes.ASK,
            intent=ActionIntents.ASK_UNKNOWN_PERSON_TO_INTRODUCE,
            priority=ActionPriorities.NORMAL,
            reason="Unknown person remained present long enough to trigger curiosity.",
        )

    def _request_action(
        self,
        action_type,
        intent,
        priority,
        reason,
    ):
        now = time.monotonic()

        with self._lock:
            last_time = self._last_action_time.get(intent)

            if (
                last_time is not None
                and now - last_time < self.cooldown_seconds
            ):
                return False

            self._last_action_time[intent] = now

        snapshot = self.world_model.snapshot()

        self.event_bus.publish(
            Event(
                type=EventTypes.ACTION_REQUESTED,
                data={
                    "action_type": action_type,
                    "intent": intent,
                    "priority": priority,
                    "reason": reason,
                    "world": {
                        "presence": snapshot.presence,
                        "identity": snapshot.identity,
                        "unknown_person_present": (
                            snapshot.unknown_person_present
                        ),
                        "conversation_active": (
                            snapshot.conversation_active
                        ),
                        "deskbot_state": snapshot.deskbot_state,
                    },
                },
                timestamp=datetime.now(),
            )
        )

        return True
