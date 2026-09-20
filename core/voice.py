import io
import wave
from abc import ABC, abstractmethod

from sarvamai import SarvamAI


class SpeechToText(ABC):
    @abstractmethod
    def transcribe(self, audio_segment):
        pass


class SpeakerRecognizer(ABC):
    @abstractmethod
    def identify(self, audio_segment):
        pass


class FakeSpeechToText(SpeechToText):
    def __init__(self, text="hello deskbot"):
        self.text = text

    def transcribe(self, audio_segment):
        return {
            "text": self.text,
            "confidence": 1.0,
        }


class FakeSpeakerRecognizer(SpeakerRecognizer):
    def __init__(self, identity="OWNER"):
        self.identity = identity

    def identify(self, audio_segment):
        return {
            "identity": self.identity,
            "confidence": 1.0,
        }


class SarvamSpeechToText(SpeechToText):
    """
    Sarvam STT adapter.

    Input:
        list of chunks containing normalized float samples [-1, 1]

    Output:
        transcript + API metadata
    """

    def __init__(
        self,
        api_key,
        model="saaras:v3",
        mode="codemix",
        sample_rate=16000,
    ):
        if not api_key:
            raise ValueError("Sarvam API key is required")

        self.client = SarvamAI(
            api_subscription_key=api_key
        )

        self.model = model
        self.mode = mode
        self.sample_rate = sample_rate

    def _build_wav(self, audio_segment):
        pcm_data = bytearray()

        for chunk in audio_segment:
            for sample in chunk:
                sample = max(-1.0, min(1.0, sample))

                value = int(sample * 32767)

                pcm_data.extend(
                    value.to_bytes(
                        2,
                        byteorder="little",
                        signed=True,
                    )
                )

        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(pcm_data)

        wav_buffer.seek(0)

        return wav_buffer

    def transcribe(self, audio_segment):
        if not audio_segment:
            return {
                "text": "",
                "confidence": 0.0,
            }

        wav_file = self._build_wav(audio_segment)

        response = self.client.speech_to_text.transcribe(
            file=wav_file,
            model=self.model,
            mode=self.mode,
        )

        return {
            "text": response.transcript,
            "confidence": 1.0,
        }
