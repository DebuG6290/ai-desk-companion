import base64
from abc import ABC, abstractmethod

from sarvamai import SarvamAI


class TextToSpeech(ABC):
    @abstractmethod
    def synthesize(self, text):
        pass


class FakeTextToSpeech(TextToSpeech):
    def __init__(self, audio_data=b"fake-audio"):
        self.audio_data = audio_data

    def synthesize(self, text):
        return {"audio": self.audio_data}


class SarvamTextToSpeech(TextToSpeech):
    def __init__(
        self,
        api_key,
        model="bulbul:v3",
        speaker="shubh",
        language_code="en-IN",
        pace=1.0,
        speech_sample_rate=24000,
    ):
        if not api_key:
            raise ValueError("Sarvam API key is required")

        self.client = SarvamAI(api_subscription_key=api_key)
        self.model = model
        self.speaker = speaker
        self.language_code = language_code
        self.pace = pace
        self.speech_sample_rate = speech_sample_rate

    def synthesize(self, text):
        if not text:
            return {"audio": b""}

        response = self.client.text_to_speech.convert(
            text=text,
            model=self.model,
            speaker=self.speaker,
            language_code=self.language_code,
            pace=self.pace,
            speech_sample_rate=self.speech_sample_rate,
            output_audio_codec="wav",
        )

        audio_base64 = response.audios[0]

        if isinstance(audio_base64, str):
            audio = base64.b64decode(audio_base64)
        else:
            audio = audio_base64

        return {"audio": audio}
