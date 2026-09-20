from core.event_bus import EventBus
from core.events import EventTypes
from core.llm import FakeLLM
from core.llm_pipeline import LLMPipeline
from datetime import datetime

from core.events import Event


def test_fake_llm():
    llm = FakeLLM(
        text="Hello from Deskbot."
    )

    result = llm.generate(
        [
            {
                "role": "user",
                "content": "Hello Deskbot",
            }
        ]
    )

    assert result["text"] == "Hello from Deskbot."


def test_llm_pipeline_returns_response():
    llm = FakeLLM(
        text="I am doing great!"
    )

    pipeline = LLMPipeline(
        llm=llm,
    )

    result = pipeline.process(
        "How are you?"
    )

    assert result["text"] == "I am doing great!"


def test_llm_pipeline_emits_text_response():
    event_bus = EventBus()

    received = []

    def handler(event):
        received.append(event)

    event_bus.subscribe(
        EventTypes.TEXT_RESPONSE,
        handler,
    )

    llm = FakeLLM(
        text="Nice to meet you."
    )

    pipeline = LLMPipeline(
        llm=llm,
        event_bus=event_bus,
    )

    result = pipeline.process(
        "Hello"
    )

    assert result["text"] == "Nice to meet you."

    assert len(received) == 1
    assert received[0].type == EventTypes.TEXT_RESPONSE
    assert received[0].data["text"] == "Nice to meet you."

def test_llm_pipeline_reacts_to_text_received():
    event_bus = EventBus()

    received = []

    def handler(event):
        received.append(event)

    event_bus.subscribe(
        EventTypes.TEXT_RESPONSE,
        handler,
    )

    llm = FakeLLM(
        text="Yes, I heard you."
    )

    LLMPipeline(
        llm=llm,
        event_bus=event_bus,
    )

    event_bus.publish(
        Event(
            type=EventTypes.TEXT_RECEIVED,
            data={
                "text": "Hello Deskbot",
                "confidence": 1.0,
            },
            timestamp=datetime.now(),
        )
    )

    assert len(received) == 1
    assert received[0].type == EventTypes.TEXT_RESPONSE
    assert received[0].data["text"] == "Yes, I heard you."
