import os

from dotenv import load_dotenv

from core.llm import SarvamLLM


load_dotenv()


def main():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    model = os.getenv(
        "SARVAM_LLM_MODEL",
        "sarvam-105b-conversations",
    )

    max_tokens = int(
        os.getenv(
            "SARVAM_LLM_MAX_TOKENS",
            "256",
        )
    )

    llm = SarvamLLM(
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        reasoning_effort=None,
    )

    messages = [
        {
            "role": "user",
            "content": "Hello Deskbot. Introduce yourself in a short, friendly way.",
        }
    ]

    print("=" * 50)
    print("DESKBOT REAL LLM TEST")
    print("=" * 50)
    print()
    print(f"Model: {model}")
    print(f"Max tokens: {max_tokens}")
    print("Reasoning: OFF")
    print()
    print("Sending request...")
    print()

    result = llm.generate(messages)

    print("🧠 DESKBOT:")
    print(result["text"])


if __name__ == "__main__":
    main()
