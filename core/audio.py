import math
import subprocess


class AudioInput:
    def start(self):
        raise NotImplementedError

    def read_chunk(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class FakeAudioInput(AudioInput):
    def __init__(self, chunks=None):
        self.chunks = chunks or []
        self.index = 0
        self.started = False

    def start(self):
        self.index = 0
        self.started = True

    def read_chunk(self):
        if not self.started:
            raise RuntimeError("Audio input is not started")

        if self.index >= len(self.chunks):
            return None

        amplitude = self.chunks[self.index]
        self.index += 1

        return amplitude

    def stop(self):
        self.started = False


class PipeWireAudioInput(AudioInput):
    """
    Real microphone input using PipeWire's pw-record.

    The output is converted into normalized float samples so that
    the existing VAD/SpeechSegmenter can continue working unchanged.
    """

    def __init__(
        self,
        target=89,
        sample_rate=16000,
        channels=1,
        chunk_samples=1600,
    ):
        self.target = target
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_samples = chunk_samples

        self.process = None
        self.started = False

        self.bytes_per_sample = 2
        self.chunk_bytes = (
            self.chunk_samples
            * self.channels
            * self.bytes_per_sample
        )

    def start(self):
        if self.started:
            return

        command = [
            "pw-record",
            "--target",
            str(self.target),
            "--rate",
            str(self.sample_rate),
            "--channels",
            str(self.channels),
            "--format",
            "s16",
            "--raw",
            "-",
        ]

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

        self.started = True

    def read_chunk(self):
        if not self.started or self.process is None:
            raise RuntimeError("Audio input is not started")

        raw = self.process.stdout.read(self.chunk_bytes)

        if not raw:
            return None

        sample_count = len(raw) // 2

        samples = []

        for i in range(sample_count):
            value = int.from_bytes(
                raw[i * 2:i * 2 + 2],
                byteorder="little",
                signed=True,
            )

            samples.append(value / 32768.0)

        return samples

    def stop(self):
        if not self.started:
            return

        process = self.process

        if process is None:
            self.started = False
            return

        try:
            process.terminate()

            try:
                process.wait(timeout=0.5)

            except subprocess.TimeoutExpired:
                process.kill()

                try:
                    process.wait(timeout=0.5)

                except subprocess.TimeoutExpired:
                    pass

        finally:
            if process.stdout is not None:
                process.stdout.close()

            self.process = None
            self.started = False


def generate_sine_amplitude(
    amplitude,
    samples=160,
):
    return [
        amplitude
        * math.sin(
            2 * math.pi * i / samples
        )
        for i in range(samples)
    ]
