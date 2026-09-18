from datetime import datetime

import cv2

from core.events import Event, EventTypes
from core.identity import FaceRecognizer, IdentitySmoother
from core.presence import PresenceManager, PresenceState


class IdentityPresenceManager:
    def __init__(
        self,
        event_bus,
        confidence_threshold=75.0,
        identity_required_frames=3,
        present_required_frames=3,
        absent_required_frames=5,
    ):
        self.event_bus = event_bus

        self.recognizer = FaceRecognizer(
            confidence_threshold=confidence_threshold
        )

        self.identity_smoother = IdentitySmoother(
            required_frames=identity_required_frames
        )

        self.presence_manager = PresenceManager(
            required_present_frames=present_required_frames,
            required_absent_frames=absent_required_frames,
        )

        self.last_identity = "UNKNOWN"

    def preprocess_face(self, frame, face):
        x = face["x"]
        y = face["y"]
        w = face["width"]
        h = face["height"]

        face_image = frame[
            y:y + h,
            x:x + w,
        ]

        if face_image.size == 0:
            return None

        gray = cv2.cvtColor(
            face_image,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.resize(
            gray,
            (160, 160),
        )

        return gray

    def update(self, frame, faces):
        detected = len(faces) > 0

        presence_event = self.presence_manager.update(
            detected
        )

        if presence_event == "PERSON_ABSENT":
            self.identity_smoother.reset()
            self.last_identity = "UNKNOWN"

            self.event_bus.publish(
                Event(
                    type=EventTypes.USER_LEFT,
                    data={},
                    timestamp=datetime.now(),
                )
            )

            return {
                "presence": PresenceState.ABSENT.value,
                "identity": "UNKNOWN",
                "event": EventTypes.USER_LEFT,
            }

        if not faces:
            return {
                "presence": self.presence_manager.state.value,
                "identity": self.last_identity,
                "event": presence_event,
            }

        # V1 assumes one relevant face.
        face = faces[0]

        face_image = self.preprocess_face(
            frame,
            face,
        )

        if face_image is None:
            return {
                "presence": self.presence_manager.state.value,
                "identity": self.last_identity,
                "event": presence_event,
            }

        prediction = self.recognizer.predict(
            face_image
        )

        identity = self.identity_smoother.update(
            prediction["identity"]
        )

        identity_changed = (
            identity != self.last_identity
        )

        self.last_identity = identity

        event_type = None

        if identity_changed:

            if identity == "YOU":
                event_type = EventTypes.USER_RETURNED

            elif identity == "UNKNOWN":
                event_type = EventTypes.UNKNOWN_PERSON_ENTERED

            if event_type:
                self.event_bus.publish(
                    Event(
                        type=event_type,
                        data={
                            "identity": identity,
                            "distance": prediction["confidence"],
                        },
                        timestamp=datetime.now(),
                    )
                )

        return {
            "presence": self.presence_manager.state.value,
            "identity": identity,
            "distance": prediction["confidence"],
            "event": event_type or presence_event,
        }
