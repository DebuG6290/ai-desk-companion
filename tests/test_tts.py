from core.tts import FakeTextToSpeech


def test_fake_tts():
    tts = FakeTextToSpeech(
        audio_data=b"test-audio"
    )

    result = tts.synthesize(
        "Hello Deskbot"
    )

    assert result["audio"] == b"test-audio"
