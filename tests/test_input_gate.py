from core.input_gate import InputGate


def test_empty_input_is_rejected():
    gate = InputGate()

    result = gate.evaluate("")

    assert result["accepted"] is False
    assert result["reason"] == "empty"


def test_short_input_is_rejected():
    gate = InputGate()

    result = gate.evaluate("a")

    assert result["accepted"] is False


def test_repeated_garbage_is_rejected():
    gate = InputGate()

    result = gate.evaluate("the the the the")

    assert result["accepted"] is False
    assert result["reason"] == "repeated_words"


def test_normal_sentence_is_accepted():
    gate = InputGate()

    result = gate.evaluate(
        "I have an important meeting tomorrow"
    )

    assert result["accepted"] is True
