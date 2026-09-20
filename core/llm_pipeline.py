from datetime import datetime

from core.events import Event, EventTypes


class LLMPipeline:
    def __init__(
        self,
        llm,
        event_bus=None,
    ):
        self.llm = llm
        self.event_bus = event_bus

        if self.event_bus is not None:
            self.event_bus.subscribe(
                EventTypes.TEXT_RECEIVED,
                self._handle_text_received,
            )

    def _handle_text_received(self, event):
        text = event.data.get("text", "")

        if not text:
            return

        self.process(text)

    def process(self, text):
        if not text:
            return None

        messages = [
            {
                "role": "user",
                "content": text,
            }
        ]

        response = self.llm.generate(messages)

        if self.event_bus is not None:
            self.event_bus.publish(
                Event(
                    type=EventTypes.TEXT_RESPONSE,
                    data={
                        "text": response["text"],
                    },
                    timestamp=datetime.now(),
                )
            )

        return response
