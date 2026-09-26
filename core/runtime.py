import time


class DeskbotRuntime:
    """
    Composition root for the integrated Deskbot prototype.

    Components own their capabilities. Runtime owns lifecycle and the
    camera/audio polling loop.
    """

    def __init__(
        self,
        camera,
        perception,
        identity_presence,
        audio_pipeline,
        event_bus,
        browser_display=None,
        camera_interval=0.1,
    ):
        self.camera = camera
        self.perception = perception
        self.identity_presence = identity_presence
        self.audio_pipeline = audio_pipeline
        self.event_bus = event_bus
        self.browser_display = browser_display
        self.camera_interval = camera_interval

        self.running = False
        self._last_camera_time = 0.0

    def start(self):
        if self.running:
            return

        if self.browser_display is not None:
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
            self.identity_presence.update(frame, faces)
            self._last_camera_time = now

        return self.audio_pipeline.process_once()

    def run_forever(self):
        self.start()

        try:
            while self.running:
                self.process_once()
        except KeyboardInterrupt:
            pass
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
