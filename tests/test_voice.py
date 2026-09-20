from core.event_bus import EventBus
from core.events import EventTypes
from core.voice import (
    FakeSpeakerRecognizer,
    FakeSpeechToText,
)
from core.voice_pipeline import VoicePipeline


def test_owner_voice_and_text_are_processed():
    event_bus = EventBus()

    events = []

    def handler(event):
        events.append(event)

    event_bus.subscribe(
        EventTypes.OWNER_VOICE_DETECTED,
        handler,
    )

    event_bus.subscribe(
        EventTypes.TEXT_RECEIVED,
        handler,
    )

    pipeline = VoicePipeline(
        speech_to_text=FakeSpeechToText(
            text="hello deskbot"
        ),
        speaker_recognizer=FakeSpeakerRecognizer(
            identity="OWNER"
        ),
        event_bus=event_bus,
    )

    result = pipeline.process(
        ["fake audio"]
    )

    assert result["speaker"]["identity"] == "OWNER"
    assert result["transcription"]["text"] == "hello deskbot"

    assert len(events) == 2
    assert events[0].type == EventTypes.OWNER_VOICE_DETECTED
    assert events[1].type == EventTypes.TEXT_RECEIVED


def test_unknown_voice_is_detected():
    event_bus = EventBus()

    events = []

    event_bus.subscribe(
        EventTypes.UNKNOWN_VOICE_DETECTED,
        lambda event: events.append(event),
    )

    pipeline = VoicePipeline(
        speech_to_text=FakeSpeechToText(),
        speaker_recognizer=FakeSpeakerRecognizer(
            identity="UNKNOWN"
        ),
        event_bus=event_bus,
    )

    pipeline.process(
        ["fake audio"]
    )

    assert len(events) == 1
    assert events[0].type == EventTypes.UNKNOWN_VOICE_DETECTED


def test_empty_audio_is_ignored():
    event_bus = EventBus()

    pipeline = VoicePipeline(
        speech_to_text=FakeSpeechToText(),
        speaker_recognizer=FakeSpeakerRecognizer(),
        event_bus=event_bus,
    )

    assert pipeline.process([]) is None
