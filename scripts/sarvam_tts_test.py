import os

from dotenv import load_dotenv

from core.tts import SarvamTextToSpeech


load_dotenv()


def main():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    tts = SarvamTextToSpeech(
        api_key=api_key,
        model="bulbul:v3",
        speaker="shubh",
        language_code="en-IN",
        pace=1.0,
        speech_sample_rate=24000,
    )

    text = (
        "Hello! I am Deskbot. "
        "Nice to finally talk to you."
    )

    print("=" * 50)
    print("DESKBOT REAL TTS TEST")
    print("=" * 50)
    print()
    print("Generating speech...")

    result = tts.synthesize(text)

    audio = result["audio"]

    print(
        f"Received audio: {len(audio)} bytes"
    )

    with open(
        "/tmp/deskbot_tts.wav",
        "wb",
    ) as file:
        file.write(audio)

    print(
        "Saved: /tmp/deskbot_tts.wav"
    )


if __name__ == "__main__":
    main()
