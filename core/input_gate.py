import re


class InputGate:
    """
    Cheap local filter between STT and the main LLM.

    Returns:
        accepted: whether the input should continue
        reason: why it was accepted/rejected
    """

    def __init__(
        self,
        min_length=2,
        max_repeated_words=3,
    ):
        self.min_length = min_length
        self.max_repeated_words = max_repeated_words

    def evaluate(self, text):
        if not text:
            return {
                "accepted": False,
                "reason": "empty",
            }

        text = text.strip()

        if len(text) < self.min_length:
            return {
                "accepted": False,
                "reason": "too_short",
            }

        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        words = cleaned.split()

        if not words:
            return {
                "accepted": False,
                "reason": "no_words",
            }

        # Reject obvious STT repetition:
        # "the the the the"
        if len(words) >= 4:
            for i in range(len(words) - self.max_repeated_words + 1):
                window = words[i:i + self.max_repeated_words]

                if len(set(window)) == 1:
                    return {
                        "accepted": False,
                        "reason": "repeated_words",
                    }

        return {
            "accepted": True,
            "reason": "accepted",
            "text": text,
        }
