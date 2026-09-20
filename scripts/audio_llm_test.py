import os

from dotenv import load_dotenv

from core.audio import PipeWireAudioInput
from core.audio_pipeline import AudioPipeline
from core.event_bus import EventBus
from core.events import EventTypes
from core.llm import SarvamLLM
from core.llm_pipeline import LLMPipeline
from core.voice import SarvamSpeechToText
from core.voice_pipeline import VoicePipeline


load_dotenv()


def main():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    event_bus = EventBus()

    # -------------------------
    # STT
    # -------------------------

    stt = SarvamSpeechToText(
        api_key=api_key,
        model="saaras:v3",
        mode="codemix",
    )

    voice_pipeline = VoicePipeline(
        speech_to_text=stt,
        speaker_recognizer=None,
        event_bus=event_bus,
    )

    # -------------------------
    # LLM
    # -------------------------

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

    LLMPipeline(
        llm=llm,
        event_bus=event_bus,
    )

    # -------------------------
    # Events
    # -------------------------

    def handle_speech_started(event):
        print("\n🎤 SPEECH STARTED")

    def handle_speech_ended(event):
        segment = event.data["segment"]

        print("\n🛑 SPEECH ENDED")
        print("Sending audio to Sarvam STT...")

        result = voice_pipeline.process(
            segment
        )

        print("\n🧠 TRANSCRIPT:")
        print(result["transcription"]["text"])

    def handle_text(event):
        print(
            "\n📨 TEXT_RECEIVED:",
            event.data["text"],
        )

    def handle_response(event):
        print(
            "\n🤖 DESKBOT:",
            event.data["text"],
        )

    event_bus.subscribe(
        EventTypes.SPEECH_STARTED,
        handle_speech_started,
    )

    event_bus.subscribe(
        EventTypes.SPEECH_ENDED,
        handle_speech_ended,
    )

    event_bus.subscribe(
        EventTypes.TEXT_RECEIVED,
        handle_text,
    )

    event_bus.subscribe(
        EventTypes.TEXT_RESPONSE,
        handle_response,
    )

    # -------------------------
    # Audio
    # -------------------------

    audio = PipeWireAudioInput(
        target=89,
        sample_rate=16000,
        channels=1,
        chunk_samples=1600,
    )

    pipeline = AudioPipeline(
        audio_input=audio,
        event_bus=event_bus,
    )

    print("=" * 50)
    print("DESKBOT EARS → BRAIN TEST")
    print("=" * 50)
    print()
    print("Speak normally.")
    print("Speech → STT → LLM → response")
    print()
    print("Press Ctrl+C to stop.")
    print()

    pipeline.start()

    try:
        while True:
            pipeline.process_once()

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()
