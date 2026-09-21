from abc import ABC, abstractmethod
import json

from sarvamai import SarvamAI


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages):
        pass


class FakeLLM(LLMProvider):
    def __init__(self, text="Hello! I am Deskbot."):
        self.text = text

    def generate(self, messages):
        return {
            "text": self.text,
            "should_respond": True,
            "relevant": True,
            "addressed_to_deskbot": True,
            "needs_response": True,
            "response_mode": "voice_and_display",
        }


class SarvamLLM(LLMProvider):
    """
    Sarvam LLM adapter.

    The model performs two jobs in ONE API call:

    1. Decide whether Deskbot should respond.
    2. If needed, generate the response and choose the response mode.

    Normal output:

        {
            "text": "...",
            "should_respond": True,
            "relevant": True,
            "addressed_to_deskbot": True,
            "needs_response": True,
            "response_mode": "voice_and_display",
        }

    If the model ignores the JSON instruction and returns normal
    conversational text, that text is used as a safe fallback.
    """

    VALID_RESPONSE_MODES = {
        "ignore",
        "display_only",
        "voice_and_display",
    }

    def __init__(
        self,
        api_key,
        model="sarvam-105b-conversations",
        max_tokens=256,
        reasoning_effort=None,
    ):
        if not api_key:
            raise ValueError("Sarvam API key is required")

        self.client = SarvamAI(
            api_subscription_key=api_key
        )

        self.model = model
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort

    def generate(self, messages):
        if not messages:
            return {
                "text": "",
                "should_respond": False,
                "relevant": False,
                "addressed_to_deskbot": False,
                "needs_response": False,
                "response_mode": "ignore",
            }

        structured_messages = self._build_structured_messages(
            messages
        )

        response = self.client.chat.completions(
            model=self.model,
            messages=structured_messages,
            max_tokens=self.max_tokens,
            reasoning_effort=self.reasoning_effort,
        )

        content = response.choices[0].message.content

        return self._parse_response(content)

    def _build_structured_messages(self, messages):
        system_instruction = """
You are Deskbot, a small personal desk companion.

You must BOTH:

1. Decide whether Deskbot should respond to the user's latest input.
2. If a response is needed, generate that response.

Return ONLY a valid JSON object.

Use exactly these fields:

{
  "relevant": true,
  "addressed_to_deskbot": true,
  "needs_response": true,
  "response_mode": "voice_and_display",
  "response": "Your response here"
}

Definitions:

relevant:
True when the user's input contains meaningful information,
a request, a question, a personal statement, or something
Deskbot could reasonably react to.

addressed_to_deskbot:
True when the user appears to be talking to Deskbot.
The user does NOT have to explicitly say "Deskbot".

needs_response:
True only when Deskbot should actively respond.
Not every meaningful statement requires a response.

response_mode:

"ignore"
Use when Deskbot should not respond.

"display_only"
Use when Deskbot should respond but speaking is unnecessary.

"voice_and_display"
Use for direct conversation, questions, emotional interaction,
personal interaction, explicit requests, or situations where
spoken interaction is useful.

If needs_response is false:
- response_mode must be "ignore"
- response must be an empty string

If needs_response is true:
- response must contain the actual concise Deskbot response

Keep responses natural and concise.
Do not invent physical actions or capabilities.
Do not include markdown outside the JSON.
Return ONLY JSON.
""".strip()

        structured_messages = [
            {
                "role": "system",
                "content": system_instruction,
            }
        ]

        structured_messages.extend(messages)

        return structured_messages

    def _parse_response(self, content):
        if not content:
            return {
                "text": "",
                "should_respond": False,
                "relevant": False,
                "addressed_to_deskbot": False,
                "needs_response": False,
                "response_mode": "ignore",
            }

        content = content.strip()

        try:
            result = json.loads(content)

        except json.JSONDecodeError:
            print(
                "\n⚠️ LLM returned plain text instead of JSON."
            )
            print(
                "Using conversational fallback."
            )

            return {
                "text": content,
                "should_respond": True,
                "relevant": True,
                "addressed_to_deskbot": True,
                "needs_response": True,
                "response_mode": "voice_and_display",
            }

        if not isinstance(result, dict):
            raise ValueError(
                "LLM returned JSON that is not an object"
            )

        required_fields = {
            "relevant",
            "addressed_to_deskbot",
            "needs_response",
            "response_mode",
            "response",
        }

        missing = required_fields - result.keys()

        if missing:
            raise ValueError(
                f"LLM response is missing fields: {missing}"
            )

        response_mode = result["response_mode"]

        if response_mode not in self.VALID_RESPONSE_MODES:
            raise ValueError(
                f"Invalid response mode: {response_mode}"
            )

        needs_response = bool(
            result["needs_response"]
        )

        response_text = result.get(
            "response",
            "",
        )

        if response_text is None:
            response_text = ""

        response_text = str(
            response_text
        ).strip()

        if not needs_response:
            response_mode = "ignore"
            response_text = ""

        return {
            "text": response_text,
            "should_respond": needs_response,
            "relevant": bool(
                result["relevant"]
            ),
            "addressed_to_deskbot": bool(
                result["addressed_to_deskbot"]
            ),
            "needs_response": needs_response,
            "response_mode": response_mode,
        }
