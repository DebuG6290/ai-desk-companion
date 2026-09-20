from datetime import datetime

from core.events import Event, EventTypes


class VoicePipeline:
    def __init__(
        self,
        speech_to_text,
        speaker_recognizer=None,
        event_bus=None,
    ):
        self.speech_to_text = speech_to_text
        self.speaker_recognizer = speaker_recognizer
        self.event_bus = event_bus

    def process(self, audio_segment):
        if not audio_segment:
            return None

        speaker = None

        if self.speaker_recognizer is not None:
            speaker = self.speaker_recognizer.identify(
                audio_segment
            )

            if speaker["identity"] == "OWNER":
                voice_event = EventTypes.OWNER_VOICE_DETECTED
            else:
                voice_event = EventTypes.UNKNOWN_VOICE_DETECTED

            if self.event_bus is not None:
                self.event_bus.publish(
                    Event(
                        type=voice_event,
                        data={
                            "identity": speaker["identity"],
                            "confidence": speaker["confidence"],
                        },
                        timestamp=datetime.now(),
                    )
                )

        transcription = self.speech_to_text.transcribe(
            audio_segment
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                Event(
                    type=EventTypes.TEXT_RECEIVED,
                    data={
                        "text": transcription["text"],
                        "confidence": transcription["confidence"],
                    },
                    timestamp=datetime.now(),
                )
            )

        return {
            "speaker": speaker,
            "transcription": transcription,
        }
