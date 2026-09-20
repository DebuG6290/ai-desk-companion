class ConversationManager:
    """
    Maintains short-term conversational context.

    This is NOT long-term memory.
    Context exists only for the current runtime session.
    """

    def __init__(
        self,
        max_messages=10,
        system_prompt=None,
    ):
        self.max_messages = max_messages

        self.system_prompt = system_prompt or (
            "You are Deskbot, a small personal desk companion. "
            "You are friendly, curious, playful, and conversational. "
            "Keep responses concise and natural. "
            "Do not pretend to have physical abilities you do not have."
        )

        self.messages = []

    def add_user_message(self, text):
        if not text:
            return

        self.messages.append(
            {
                "role": "user",
                "content": text,
            }
        )

        self._trim()

    def add_assistant_message(self, text):
        if not text:
            return

        self.messages.append(
            {
                "role": "assistant",
                "content": text,
            }
        )

        self._trim()

    def get_messages(self):
        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            *self.messages,
        ]

    def clear(self):
        self.messages = []

    def _trim(self):
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[
                -self.max_messages:
            ]
