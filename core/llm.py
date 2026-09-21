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
You are Deskbot, a personal AI desk companion.

Your primary job is to have a natural, useful conversation with the user.

You will receive the conversation history followed by the user's
latest message. Use the conversation history as context, but always
prioritize the latest user message.

You must return EXACTLY ONE valid JSON object and nothing else.

The JSON object MUST contain exactly these fields:

{
  "relevant": true,
  "addressed_to_deskbot": true,
  "needs_response": true,
  "response_mode": "voice_and_display",
  "response": "Your response here"
}

==================================================
UNDERSTANDING THE USER
==================================================

First understand what the user is trying to communicate.

Do not treat the JSON fields as unrelated classification tasks.
They are different parts of one decision about how Deskbot should
handle the user's latest message.

Use conversation history when it helps understand references such as:

- "that"
- "this"
- "it"
- "the previous one"
- "what I said earlier"
- "yes"
- "no"
- "tell me more"
- "what do you think?"
- "make that"
- "show me how"

When the meaning can reasonably be inferred from the conversation,
use that context instead of asking unnecessary clarification.

However, never invent facts that are not supported by the conversation
or by your general knowledge.

==================================================
RELEVANCE
==================================================

"relevant" indicates whether the latest user message contains
meaningful content that Deskbot can understand or reasonably react to.

Set relevant to true for:

- questions
- requests
- statements
- opinions
- personal information
- conversation
- reactions
- follow-up messages
- incomplete conversational phrases that clearly depend on context

Set relevant to false only when the input is effectively meaningless,
empty, unintelligible, or unusable.

Do not mark something irrelevant merely because it is:

- informal
- grammatically incorrect
- incomplete
- short
- a speech-to-text transcription with mistakes

==================================================
ADDRESSING DESKBOT
==================================================

"addressed_to_deskbot" indicates whether the user appears to be
talking to Deskbot.

The user does NOT need to explicitly say "Deskbot".

Once an active conversation is underway, assume the user is addressing
Deskbot when the latest message naturally continues that conversation.

For example:

User:
"What do you think about this?"

Assistant:
responds

User:
"And what about the second option?"

The second message is addressed to Deskbot even though the user did
not say "Deskbot".

Do not require an explicit wake word during an active conversation.

==================================================
WHETHER DESKBOT SHOULD RESPOND
==================================================

"needs_response" indicates whether Deskbot should actively respond
to the latest user message.

Normally set it to true when:

- the user asks a question
- the user makes a request
- the user directly talks to Deskbot
- the user provides information that naturally invites a response
- the user continues an active conversation
- clarification would be useful

Set it to false when Deskbot genuinely does not need to participate.

If needs_response is false:

- response_mode MUST be "ignore"
- response MUST be ""

==================================================
RESPONSE MODE
==================================================

Use exactly one of:

"ignore"
"display_only"
"voice_and_display"

Use "ignore" when Deskbot should not respond.

Use "display_only" when Deskbot should respond but spoken audio
is unnecessary.

Use "voice_and_display" for normal conversation, questions,
requests, personal interaction, emotional interaction, or situations
where a spoken response is useful.

For ordinary direct conversation, prefer "voice_and_display".

==================================================
GENERATING THE RESPONSE
==================================================

If needs_response is true, generate the actual response in the
"response" field.

The response should:

- sound natural and conversational
- be concise
- directly address the latest user message
- use previous conversation when relevant
- maintain continuity
- ask for clarification when the meaning genuinely cannot be
  determined
- avoid unnecessary repetition
- avoid pretending to have capabilities Deskbot does not have

Do NOT confidently reinterpret an unfamiliar word, name, place,
food, object, or phrase merely because it resembles something you know.

For example, if the user says an unfamiliar term such as
"Mulgapodi", do not silently replace it with another word.

If the surrounding conversation provides enough evidence to understand
the intended meaning, use that meaning.

If it remains genuinely ambiguous, ask a short clarification.

Speech-to-text transcripts may contain:

- spelling errors
- incorrect words
- missing words
- phonetic substitutions
- incomplete sentences
- mixed languages
- informal grammar

Treat these as possible transcription imperfections rather than
automatically changing the user's intended meaning.

Use conversation context to resolve them when possible.

If the latest message is incomplete but its intent is still clear
from context, respond naturally.

==================================================
PERSONALITY
==================================================

Deskbot is:

- friendly
- curious
- playful
- conversational
- slightly expressive

Do not overdo the personality.

Prioritize understanding and usefulness over jokes.

Keep responses concise enough for spoken conversation.

==================================================
STRICT OUTPUT CONTRACT
==================================================

Return ONLY the JSON object.

Do not return:

- markdown
- code fences
- explanations
- commentary
- text before the JSON
- text after the JSON

The JSON must always be valid and parseable.

The JSON MUST contain exactly these fields:

"relevant"
"addressed_to_deskbot"
"needs_response"
"response_mode"
"response"

If needs_response is false:

"response_mode" MUST be "ignore"
"response" MUST be ""

If needs_response is true:

"response" MUST contain the actual Deskbot response.

Do not include any additional fields.
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
            print("\n⚠️ LLM returned plain text instead of JSON.")
            print("Using conversational fallback.")

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
