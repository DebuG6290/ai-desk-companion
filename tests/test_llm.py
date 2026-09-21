import json

from core.llm import FakeLLM, SarvamLLM


def test_fake_llm():
    llm = FakeLLM(
        text="Hello Deskbot"
    )

    result = llm.generate(
        [{"role": "user", "content": "Hi"}]
    )

    assert result["text"] == "Hello Deskbot"
    assert result["should_respond"] is True
    assert result["response_mode"] == "voice_and_display"


def test_sarvam_llm_parses_structured_response():
    llm = SarvamLLM.__new__(
        SarvamLLM
    )

    content = json.dumps(
        {
            "relevant": True,
            "addressed_to_deskbot": True,
            "needs_response": True,
            "response_mode": "voice_and_display",
            "response": "Good luck with your meeting!",
        }
    )

    result = llm._parse_response(
        content
    )

    assert result["text"] == (
        "Good luck with your meeting!"
    )

    assert result["should_respond"] is True

    assert result["relevant"] is True

    assert result["addressed_to_deskbot"] is True

    assert result["needs_response"] is True

    assert result["response_mode"] == (
        "voice_and_display"
    )


def test_sarvam_llm_parses_ignore_response():
    llm = SarvamLLM.__new__(
        SarvamLLM
    )

    content = json.dumps(
        {
            "relevant": False,
            "addressed_to_deskbot": False,
            "needs_response": False,
            "response_mode": "ignore",
            "response": "",
        }
    )

    result = llm._parse_response(
        content
    )

    assert result["text"] == ""

    assert result["should_respond"] is False

    assert result["response_mode"] == "ignore"

def test_plain_text_fallback():
    llm = SarvamLLM.__new__(
        SarvamLLM
    )

    result = llm._parse_response(
        "That sounds like a great project!"
    )

    assert result["text"] == (
        "That sounds like a great project!"
    )

    assert result["should_respond"] is True

    assert result["needs_response"] is True

    assert result["response_mode"] == (
        "voice_and_display"
    )
