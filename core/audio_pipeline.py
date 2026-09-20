from datetime import datetime

from core.events import Event, EventTypes
from core.speech import SpeechSegmenter
from core.vad import VoiceActivityDetector


class AudioPipeline:
    def __init__(
        self,
        audio_input,
        event_bus,
        vad=None,
        segmenter=None,
    ):
        self.audio_input = audio_input
        self.event_bus = event_bus

        self.vad = vad or VoiceActivityDetector()

        self.segmenter = segmenter or SpeechSegmenter(
            vad=self.vad,
            required_speech_chunks=5,
            required_silence_chunks=15,
            min_speech_chunks=7,
            pre_roll_chunks=3,
        )

    def start(self):
        self.audio_input.start()

    def process_once(self):
        samples = self.audio_input.read_chunk()

        if samples is None:
            return None

        result = self.segmenter.process(samples)

        # Low-level speech detection.
        # This may happen many times during one utterance.
        if result["speech"]:
            self.event_bus.publish(
                Event(
                    type=EventTypes.SPEECH_DETECTED,
                    data={
                        "rms": result["rms"],
                    },
                    timestamp=datetime.now(),
                )
            )

        # High-level speech state transition.
        # SPEECH_STARTED should happen exactly once
        # for each speech segment.
        if result["event"] == EventTypes.SPEECH_STARTED:
            self.event_bus.publish(
                Event(
                    type=EventTypes.SPEECH_STARTED,
                    data={
                        "rms": result["rms"],
                    },
                    timestamp=datetime.now(),
                )
            )

        # Speech has ended.
        elif result["event"] == EventTypes.SPEECH_ENDED:
            self.event_bus.publish(
                Event(
                    type=EventTypes.SPEECH_ENDED,
                    data={
                        "rms": result["rms"],
                        "segment": result["segment"],
                    },
                    timestamp=datetime.now(),
                )
            )

        return result

    def stop(self):
        self.audio_input.stop()
