import os
import time
from dotenv import load_dotenv
load_dotenv()

from core.audio import PipeWireAudioInput
from core.audio_pipeline import AudioPipeline
from core.event_bus import EventBus
from core.events import EventTypes
from core.voice import SarvamSpeechToText
from core.voice_pipeline import VoicePipeline


def main():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    event_bus = EventBus()

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

    def handle_speech_started(event):
        print("\n🎤 SPEECH STARTED")

    def handle_speech_ended(event):
        segment = event.data["segment"]

        duration = (
            sum(len(chunk) for chunk in segment)
            / 16000
        )

        print(
            f"\n🛑 SPEECH ENDED "
            f"({duration:.2f}s)"
        )

        print("Sending segment to Sarvam...")

        result = voice_pipeline.process(
            segment
        )

        print(
            "\n🧠 TRANSCRIPT:"
        )
        print(
            result["transcription"]["text"]
        )

    def handle_text(event):
        print(
            "\n📨 TEXT_RECEIVED EVENT:"
        )
        print(
            event.data["text"]
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
    print("DESKBOT REAL VOICE TEST")
    print("=" * 50)
    print()
    print("Listening continuously...")
    print("Speak normally.")
    print("Silence is processed locally.")
    print("Sarvam is called ONLY after speech ends.")
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

