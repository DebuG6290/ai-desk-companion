from enum import Enum


class PresenceState(Enum):
    ABSENT = "ABSENT"
    PRESENT = "PRESENT"


class PresenceManager:
    def __init__(
        self,
        required_present_frames=3,
        required_absent_frames=5,
    ):
        self.state = PresenceState.ABSENT

        self.required_present_frames = required_present_frames
        self.required_absent_frames = required_absent_frames

        self.present_frames = 0
        self.absent_frames = 0

    def update(self, detected):
        if detected:
            self.present_frames += 1
            self.absent_frames = 0

            if (
                self.state == PresenceState.ABSENT
                and self.present_frames >= self.required_present_frames
            ):
                self.state = PresenceState.PRESENT
                self.present_frames = 0

                return "PERSON_PRESENT"

        else:
            self.absent_frames += 1
            self.present_frames = 0

            if (
                self.state == PresenceState.PRESENT
                and self.absent_frames >= self.required_absent_frames
            ):
                self.state = PresenceState.ABSENT
                self.absent_frames = 0

                return "PERSON_ABSENT"

        return None
