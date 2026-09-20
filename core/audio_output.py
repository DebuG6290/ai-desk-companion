import os
import subprocess
import tempfile
from abc import ABC, abstractmethod


class AudioOutput(ABC):
    @abstractmethod
    def play(self, audio):
        pass


class FakeAudioOutput(AudioOutput):
    def __init__(self):
        self.last_audio = None

    def play(self, audio):
        self.last_audio = audio


class PipeWireAudioOutput(AudioOutput):
    def play(self, audio):
        if not audio:
            return

        fd, path = tempfile.mkstemp(suffix=".wav")

        try:
            with os.fdopen(fd, "wb") as file:
                file.write(audio)

            result = subprocess.run(
                ["pw-play", path],
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"pw-play failed with code {result.returncode}"
                )

        finally:
            if os.path.exists(path):
                os.remove(path)
