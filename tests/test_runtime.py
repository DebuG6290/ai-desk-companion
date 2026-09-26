import numpy as np
import pytest

from core.event_bus import EventBus
from core.runtime import DeskbotRuntime


class FakeCamera:
    def __init__(self):
        self.started = False
        self.closed = False
        self.frames = 0

    def start(self):
        self.started = True

    def capture_frame(self):
        self.frames += 1
        return np.zeros((10, 10, 3), dtype=np.uint8)

    def stop(self):
        self.started = False

    def close(self):
        self.closed = True


class FakePerception:
    def detect(self, frame):
        return [], []


class FakeIdentityPresence:
    def __init__(self):
        self.calls = 0

    def update(self, frame, faces):
        self.calls += 1
        return {}


class FakeAudioPipeline:
    def __init__(self):
        self.started = False
        self.stopped = False
        self.calls = 0

    def start(self):
        self.started = True

    def process_once(self):
        self.calls += 1
        return None

    def stop(self):
        self.stopped = True


class FakeDisplay:
    def __init__(self):
        self.started = False
        self.stopped = False
        self.debug_tracker = None

    def attach_debug_tracker(self, tracker):
        self.debug_tracker = tracker

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


def build_runtime():
    return DeskbotRuntime(
        camera=FakeCamera(),
        perception=FakePerception(),
        identity_presence=FakeIdentityPresence(),
        audio_pipeline=FakeAudioPipeline(),
        event_bus=EventBus(),
        browser_display=FakeDisplay(),
        camera_interval=0.0,
    )


def test_runtime_start_starts_components():
    runtime = build_runtime()

    runtime.start()

    assert runtime.running is True
    assert runtime.camera.started is True
    assert runtime.audio_pipeline.started is True
    assert runtime.browser_display.started is True
    assert runtime.browser_display.debug_tracker is runtime.debug_tracker

    runtime.stop()


def test_runtime_processes_camera_and_audio():
    runtime = build_runtime()
    runtime.start()

    runtime.process_once()

    assert runtime.camera.frames == 1
    assert runtime.identity_presence.calls == 1
    assert runtime.audio_pipeline.calls == 1

    runtime.stop()


def test_runtime_stop_stops_and_closes_components():
    runtime = build_runtime()

    runtime.start()
    runtime.stop()

    assert runtime.running is False
    assert runtime.audio_pipeline.stopped is True
    assert runtime.camera.closed is True
    assert runtime.browser_display.stopped is True


def test_runtime_requires_start_before_processing():
    runtime = build_runtime()

    with pytest.raises(RuntimeError):
        runtime.process_once()
