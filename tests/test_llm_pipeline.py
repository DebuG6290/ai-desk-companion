from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.input_gate import InputGate
from core.llm import FakeLLM
from core.llm_pipeline import LLMPipeline


def test_accepted_input_reaches_llm():
    event_bus = EventBus()

    pipeline = LLMPipeline(
        llm=FakeLLM(
            text="Hello from Deskbot"
        ),
        event_bus=event_bus,
    )

    result = pipeline.process(
        "Hello Deskbot"
    )

    assert result["gate_accepted"] is True
    assert result["text"] == (
        "Hello from Deskbot"
    )


def test_garbage_is_rejected_before_llm():
    event_bus = EventBus()

    pipeline = LLMPipeline(
        llm=FakeLLM(
            text="This should never be called"
        ),
        event_bus=event_bus,
    )

    result = pipeline.process(
        "the the the the"
    )

    assert result["gate_accepted"] is False
    assert result["gate_reason"] == (
        "repeated_words"
    )
    assert result["should_respond"] is False

