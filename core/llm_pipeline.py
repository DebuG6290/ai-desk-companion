from datetime import datetime

from core.events import Event, EventTypes
from core.conversation import ConversationManager
from core.input_gate import InputGate


class LLMPipeline:
    def __init__(
        self,
        llm,
        event_bus=None,
        conversation_manager=None,
        input_gate=None,
    ):
        self.llm = llm
        self.event_bus = event_bus

        self.conversation = (
            conversation_manager
            or ConversationManager()
        )

        self.input_gate = (
            input_gate
            or InputGate()
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

        gate_result = self.input_gate.evaluate(
            text
        )

        if not gate_result["accepted"]:
            print(
                f"\n🚫 INPUT GATE: "
                f"{gate_result['reason']}"
            )

            return {
                "text": "",
                "should_respond": False,
                "relevant": False,
                "addressed_to_deskbot": False,
                "needs_response": False,
                "response_mode": "ignore",
                "gate_accepted": False,
                "gate_reason": gate_result["reason"],
            }

        print(
            "\n✅ INPUT GATE: accepted"
        )

        self.conversation.add_user_message(
            text
        )

        messages = (
            self.conversation.get_messages()
        )

        result = self.llm.generate(
            messages
        )

        result["gate_accepted"] = True
        result["gate_reason"] = "accepted"

        response_text = result.get(
            "text",
            "",
        )

        should_respond = result.get(
            "should_respond",
            False,
        )

        response_mode = result.get(
            "response_mode",
            "ignore",
        )

        if should_respond and response_text:
            self.conversation.add_assistant_message(
                response_text
            )

            if self.event_bus is not None:
                self.event_bus.publish(
                    Event(
                        type=EventTypes.TEXT_RESPONSE,
                        data={
                            "text": response_text,
                            "response_mode": response_mode,
                            "relevant": result.get(
                                "relevant",
                                False,
                            ),
                            "addressed_to_deskbot": result.get(
                                "addressed_to_deskbot",
                                False,
                            ),
                            "needs_response": result.get(
                                "needs_response",
                                False,
                            ),
                        },
                        timestamp=datetime.now(),
                    )
                )

        return result
