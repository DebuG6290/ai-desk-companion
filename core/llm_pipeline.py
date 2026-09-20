from datetime import datetime

from core.events import Event, EventTypes
from core.conversation import ConversationManager


class LLMPipeline:
    def __init__(
        self,
        llm,
        event_bus=None,
        conversation_manager=None,
    ):
        self.llm = llm
        self.event_bus = event_bus

        self.conversation = (
            conversation_manager
            or ConversationManager()
        )

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

        self.conversation.add_user_message(
            text
        )

        messages = (
            self.conversation.get_messages()
        )

        response = self.llm.generate(
            messages
        )

        response_text = response["text"]

        self.conversation.add_assistant_message(
            response_text
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                Event(
                    type=EventTypes.TEXT_RESPONSE,
                    data={
                        "text": response_text,
                    },
                    timestamp=datetime.now(),
                )
            )

        return response
