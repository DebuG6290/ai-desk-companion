from abc import ABC, abstractmethod

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
        }


class SarvamLLM(LLMProvider):
    """
    Sarvam LLM adapter.

    Input:
        messages = list of chat messages

    Output:
        response text + API metadata
    """

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
            }

        response = self.client.chat.completions(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            reasoning_effort=self.reasoning_effort,
        )

        return {
            "text": response.choices[0].message.content,
        }
