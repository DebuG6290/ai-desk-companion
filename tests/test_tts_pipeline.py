from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.tts import FakeTextToSpeech
from core.tts_pipeline import TTSPipeline
from core.audio_output import FakeAudioOutput


def test_voice_response_triggers_tts():
    event_bus = EventBus()

    tts = FakeTextToSpeech(
        audio_data=b"test-audio"
    )

    audio_output = FakeAudioOutput()

    TTSPipeline(
        tts=tts,
        audio_output=audio_output,
        event_bus=event_bus,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "Hello Deskbot",
                "response_mode": "voice_and_display",
            },
            timestamp=None,
        )
    )

    assert audio_output.last_audio == (
        b"test-audio"
    )


def test_display_only_does_not_trigger_tts():
    event_bus = EventBus()

    tts = FakeTextToSpeech(
        audio_data=b"test-audio"
    )

    audio_output = FakeAudioOutput()

    TTSPipeline(
        tts=tts,
        audio_output=audio_output,
        event_bus=event_bus,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "The answer is 42",
                "response_mode": "display_only",
            },
            timestamp=None,
        )
    )

    assert audio_output.last_audio is None


def test_ignore_does_not_trigger_tts():
    event_bus = EventBus()

    tts = FakeTextToSpeech(
        audio_data=b"test-audio"
    )

    audio_output = FakeAudioOutput()

    TTSPipeline(
        tts=tts,
        audio_output=audio_output,
        event_bus=event_bus,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={
                "text": "",
                "response_mode": "ignore",
            },
            timestamp=None,
        )
    )

    assert audio_output.last_audio is None
