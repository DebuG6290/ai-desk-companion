import time


class CuriosityManager:
    def __init__(
        self,
        curiosity_delay=5.0,
        cooldown=30.0,
    ):
        self.curiosity_delay = curiosity_delay
        self.cooldown = cooldown

        self.unknown_since = None
        self.last_triggered = None

    def update(self, identity):
        now = time.monotonic()

        # No unknown person currently present.
        if identity != "UNKNOWN":
            self.unknown_since = None
            return False

        # Start tracking an unknown person.
        if self.unknown_since is None:
            self.unknown_since = now
            return False

        # Still within the curiosity delay.
        if now - self.unknown_since < self.curiosity_delay:
            return False

        # Prevent repeated reactions.
        if (
            self.last_triggered is not None
            and now - self.last_triggered < self.cooldown
        ):
            return False

        self.last_triggered = now

        return True

    def reset(self):
        self.unknown_since = None
