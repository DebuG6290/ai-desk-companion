import time
import cv2

from core.debug import DebugTracker


class DeskbotRuntime:
    """Composition root for the integrated Deskbot prototype."""

    def __init__(
        self,
        camera,
        perception,
        identity_presence,
        audio_pipeline,
        event_bus,
        browser_display=None,
        debug_tracker=None,
        camera_interval=0.1,
    ):
        self.camera = camera
        self.perception = perception
        self.identity_presence = identity_presence
        self.audio_pipeline = audio_pipeline
        self.event_bus = event_bus
        self.browser_display = browser_display
        self.debug_tracker = debug_tracker or DebugTracker()
        self.camera_interval = camera_interval

        self.running = False
        self._last_camera_time = 0.0
        self._frame_count = 0
        self._last_log_time = 0.0

        self._subscribe_debug_events()

    def _subscribe_debug_events(self):
        from core.events import EventTypes

        for event_type in (
            EventTypes.USER_RETURNED,
            EventTypes.USER_LEFT,
            EventTypes.UNKNOWN_PERSON_ENTERED,
            EventTypes.CURIOSITY_TRIGGERED,
            EventTypes.SPEECH_STARTED,
            EventTypes.SPEECH_ENDED,
            EventTypes.TEXT_RECEIVED,
            EventTypes.TEXT_RESPONSE,
            EventTypes.SPEAKING_STARTED,
            EventTypes.SPEAKING_ENDED,
            EventTypes.ACTION_REQUESTED,
            EventTypes.DISPLAY_REQUESTED,
        ):
            self.event_bus.subscribe(
                event_type,
                lambda event, et=event_type: self._record_event(et, event),
            )

    def _record_event(self, event_type, event):
        self.debug_tracker.record_event(event_type, event.data)

        if event_type == "ACTION_REQUESTED":
            self.debug_tracker.update_decision(event.data)
            self.debug_tracker.update_action(event.data)

    def start(self):
        if self.running:
            return

        if self.browser_display is not None:
            self.browser_display.attach_debug_tracker(self.debug_tracker)
            self.browser_display.start()

        self.camera.start()
        self.audio_pipeline.start()
        self.running = True
        self._last_camera_time = 0.0

    def process_once(self):
        if not self.running:
            raise RuntimeError("DeskbotRuntime is not started")

        now = time.monotonic()

        if (
            self._last_camera_time == 0.0
            or now - self._last_camera_time >= self.camera_interval
        ):
            frame = self.camera.capture_frame()
            people, faces = self.perception.detect(frame)
            result = self.identity_presence.update(frame, faces)

            self._frame_count += 1
            self.debug_tracker.update_camera(
                people=people,
                faces=faces,
                frame_count=self._frame_count,
            )

            snapshot = self._get_world_snapshot()
            if snapshot is not None:
                self.debug_tracker.update_world(snapshot)
                self.debug_tracker.update_state(snapshot.deskbot_state)

            debug_frame = frame.copy()
            for face in faces:
                x, y = face["x"], face["y"]
                w, h = face["width"], face["height"]
                cv2.rectangle(
                    debug_frame,
                    (x, y),
                    (x + w, y + h),
                    (255, 255, 255),
                    2,
                )

            identity = result.get("identity", "UNKNOWN")
            distance = result.get("distance")
            label = identity
            if distance is not None:
                label = f"{identity} | distance {distance:.1f}"

            if faces:
                x, y = faces[0]["x"], faces[0]["y"]
                cv2.putText(
                    debug_frame,
                    label,
                    (x, max(25, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            ok, encoded = cv2.imencode(".jpg", debug_frame)
            if ok and self.browser_display is not None:
                self.browser_display.update_camera_image(
                    encoded.tobytes()
                )

            if now - self._last_log_time >= 2.0:
                print(
                    f"[CAMERA] frame={self._frame_count} "
                    f"people={len(people)} faces={len(faces)} "
                    f"identity={result.get('identity')} "
                    f"distance={result.get('distance')}"
                )
                self._last_log_time = now

            self._last_camera_time = now

        return self.audio_pipeline.process_once()

    def _get_world_snapshot(self):
        for handler in getattr(self.event_bus, "handlers", {}).get(
            "ACTION_REQUESTED", []
        ):
            owner = getattr(handler, "__self__", None)
            if owner is not None and hasattr(owner, "world_model"):
                return owner.world_model.snapshot()
        return None

    def run_forever(self):
        self.start()
        try:
            while self.running:
                self.process_once()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop()

    def stop(self):
        if not self.running:
            return

        self.running = False
        try:
            self.audio_pipeline.stop()
        finally:
            try:
                self.camera.stop()
            finally:
                self.camera.close()
                if self.browser_display is not None:
                    self.browser_display.stop()
