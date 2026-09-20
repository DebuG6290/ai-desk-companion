from core.speech import SpeechSegmenter
from core.vad import VoiceActivityDetector


def test_speech_starts_after_required_chunks():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    segmenter = SpeechSegmenter(
        vad=vad,
        required_speech_chunks=2,
        required_silence_chunks=3,
    )

    silence = [0.0] * 100
    speech = [0.1] * 100

    assert segmenter.process(speech)["event"] is None

    result = segmenter.process(speech)

    assert result["event"] == "SPEECH_STARTED"

def test_speech_ends_after_required_silence():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    segmenter = SpeechSegmenter(
        vad=vad,
        required_speech_chunks=1,
        required_silence_chunks=2,
        min_speech_chunks=1,
    )

    speech = [0.1] * 100
    silence = [0.0] * 100

    assert (
        segmenter.process(speech)["event"]
        == "SPEECH_STARTED"
    )

    assert segmenter.process(silence)["event"] is None

    result = segmenter.process(silence)

    assert result["event"] == "SPEECH_ENDED"
    assert result["segment"] is not None


def test_silence_does_not_create_speech():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    segmenter = SpeechSegmenter(
        vad=vad,
        required_speech_chunks=2,
    )

    silence = [0.0] * 100

    assert segmenter.process(silence)["event"] is None
    assert segmenter.process(silence)["event"] is None

def test_speech_ends_after_required_silence():
    vad = VoiceActivityDetector(
        threshold=0.02
    )

    segmenter = SpeechSegmenter(
        vad=vad,
        required_speech_chunks=1,
        required_silence_chunks=2,
        min_speech_chunks=1,
    )

    speech = [0.1] * 100
    silence = [0.0] * 100

    assert (
        segmenter.process(speech)["event"]
        == "SPEECH_STARTED"
    )

    assert segmenter.process(silence)["event"] is None

    result = segmenter.process(silence)

    assert result["event"] == "SPEECH_ENDED"
    assert result["segment"] is not None
def test_reset_clears_segment():
    vad = VoiceActivityDetector()

    segmenter = SpeechSegmenter(
        vad=vad
    )

    segmenter.process([0.1] * 100)
    segmenter.reset()

    assert segmenter.state == "SILENCE"
    assert segmenter.segment == []
