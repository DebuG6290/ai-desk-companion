import math


class VoiceActivityDetector:
    def __init__(
        self,
        threshold=0.02,
    ):
        self.threshold = threshold

    def calculate_rms(self, samples):
        if not samples:
            return 0.0

        mean_square = sum(
            sample * sample
            for sample in samples
        ) / len(samples)

        return math.sqrt(mean_square)

    def is_speech(self, samples):
        rms = self.calculate_rms(samples)
        return rms >= self.threshold

    def process(self, samples):
        rms = self.calculate_rms(samples)
        speech = rms >= self.threshold

        return {
            "speech": speech,
            "rms": rms,
        }
