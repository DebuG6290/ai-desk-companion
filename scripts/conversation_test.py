import os

from dotenv import load_dotenv

from core.conversation import ConversationManager
from core.llm import SarvamLLM


load_dotenv()


def main():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    llm = SarvamLLM(
        api_key=api_key,
        model=os.getenv(
            "SARVAM_LLM_MODEL",
            "sarvam-105b-conversations",
        ),
        max_tokens=int(
            os.getenv(
                "SARVAM_LLM_MAX_TOKENS",
                "256",
            )
        ),
        reasoning_effort=None,
    )

    conversation = ConversationManager()

    turns = [
        "I have an important exam tomorrow.",
        "I'm feeling pretty nervous about it.",
    ]

    print("=" * 50)
    print("DESKBOT CONVERSATION CONTEXT TEST")
    print("=" * 50)

    for user_text in turns:
        print(f"\n👤 YOU: {user_text}")

        conversation.add_user_message(
            user_text
        )

        response = llm.generate(
            conversation.get_messages()
        )

        conversation.add_assistant_message(
            response["text"]
        )

        print(f"🤖 DESKBOT: {response['text']}")

    print("\n" + "=" * 50)
    print("FINAL CONTEXT")
    print("=" * 50)

    for message in conversation.get_messages():
        print(
            f"{message['role'].upper()}: "
            f"{message['content']}"
        )


if __name__ == "__main__":
    main()
