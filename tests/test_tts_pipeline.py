from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.tts import FakeTextToSpeech
from core.tts_pipeline import TTSPipeline
from core.audio_output import FakeAudioOutput


def test_tts_pipeline_responds_to_text_response():
    event_bus = EventBus()

    tts = FakeTextToSpeech(audio_data=b"test-audio")
    audio_output = FakeAudioOutput()

    TTSPipeline(
        tts=tts,
        audio_output=audio_output,
        event_bus=event_bus,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RESPONSE,
            data={"text": "Hello Deskbot"},
            timestamp=None,
        )
    )

    assert audio_output.last_audio == b"test-audio"
