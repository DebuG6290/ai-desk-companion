import os
import subprocess
import tempfile
from abc import ABC, abstractmethod


class AudioOutput(ABC):
    @abstractmethod
    def play(self, audio):
        pass


class FakeAudioOutput(AudioOutput):
    def __init__(self, event_bus=None):
        self.last_audio = None
        self.event_bus = event_bus

    def play(self, audio):
        self.last_audio = audio


class PipeWireAudioOutput(AudioOutput):
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def play(self, audio):
        if not audio:
            return

        fd, path = tempfile.mkstemp(suffix=".wav")

        try:
            with os.fdopen(fd, "wb") as file:
                file.write(audio)

            if self.event_bus is not None:
                from core.events import Event, EventTypes

                self.event_bus.publish(
                    Event(
                        type=EventTypes.SPEAKING_STARTED,
                        data={},
                        timestamp=None,
                    )
                )

            result = subprocess.run(
                ["pw-play", path],
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "pw-play failed with code "
                    f"{result.returncode}"
                )

        finally:
            if self.event_bus is not None:
                from core.events import Event, EventTypes

                self.event_bus.publish(
                    Event(
                        type=EventTypes.SPEAKING_ENDED,
                        data={},
                        timestamp=None,
                    )
                )

            if os.path.exists(path):
                os.remove(path)
