from core.audio import (
    FakeAudioInput,
    generate_sine_amplitude,
)
from core.audio_pipeline import AudioPipeline
from core.event_bus import EventBus
from core.events import EventTypes
from core.vad import VoiceActivityDetector


def test_vad_detects_silence():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    samples = [0.0] * 100

    result = vad.process(samples)

    assert result["speech"] is False
    assert result["rms"] == 0.0


def test_vad_detects_speech():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    samples = generate_sine_amplitude(
        amplitude=0.1
    )

    result = vad.process(samples)

    assert result["speech"] is True
    assert result["rms"] > 0.02


def test_fake_audio_input():
    audio = FakeAudioInput(
        chunks=[
            [0.0] * 10,
            [0.1] * 10,
        ]
    )

    audio.start()

    first = audio.read_chunk()
    second = audio.read_chunk()
    third = audio.read_chunk()

    assert first == [0.0] * 10
    assert second == [0.1] * 10
    assert third is None

    audio.stop()


def test_audio_pipeline_emits_speech_event():
    event_bus = EventBus()

    received = []

    def handler(event):
        received.append(event)

    event_bus.subscribe(
        EventTypes.SPEECH_STARTED,
        handler,
    )

    audio = FakeAudioInput(
        chunks=[
            [0.0] * 100,
            [0.1] * 100,
            [0.1] * 100,
            [0.1] * 100,
            [0.1] * 100,
            [0.1] * 100,
        ]
    )

    pipeline = AudioPipeline(
        audio_input=audio,
        event_bus=event_bus,
    )

    pipeline.start()

    silence = pipeline.process_once()

    speech_results = [
        pipeline.process_once()
        for _ in range(5)
    ]

    pipeline.stop()

    assert silence["speech"] is False

    assert any(
        result["event"] == EventTypes.SPEECH_STARTED
        for result in speech_results
    )

    assert len(received) == 1
    assert received[0].type == EventTypes.SPEECH_STARTED
