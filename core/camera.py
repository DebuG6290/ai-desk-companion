from picamera2 import Picamera2


class Camera:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.camera = Picamera2()
        self.started = False

    def start(self):
        if self.started:
            return

        config = self.camera.create_preview_configuration(
            main={
                "size": (self.width, self.height),
                "format": "RGB888",
            }
        )

        self.camera.configure(config)
        self.camera.start()
        self.started = True

    def capture_frame(self):
        if not self.started:
            raise RuntimeError("Camera is not started")

        return self.camera.capture_array()

    def stop(self):
        if not self.started:
            return

        self.camera.stop()
        self.started = False

    def close(self):
        self.camera.close()
