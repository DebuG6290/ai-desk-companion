import os

from dotenv import load_dotenv

from core.audio import PipeWireAudioInput
from core.audio_output import PipeWireAudioOutput
from core.audio_pipeline import AudioPipeline
from core.browser_display import BrowserDisplay
from core.display_controller import DisplayController
from core.event_bus import EventBus
from core.events import EventTypes
from core.llm import SarvamLLM
from core.llm_pipeline import LLMPipeline
from core.state import StateController
from core.tts import SarvamTextToSpeech
from core.tts_pipeline import TTSPipeline
from core.voice import SarvamSpeechToText
from core.voice_pipeline import VoicePipeline


load_dotenv()


def main():
    api_key = os.getenv(
        "SARVAM_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is not set"
        )

    event_bus = EventBus()

    # -------------------------
    # DISPLAY
    # -------------------------

    browser_display = BrowserDisplay(
        host="0.0.0.0",
        port=8080,
    )

    browser_display.start()

    display_controller = DisplayController(
        browser_display
    )

    StateController(
        event_bus=event_bus,
        display_controller=display_controller,
    )

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
    # TTS
    # -------------------------

    tts = SarvamTextToSpeech(
        api_key=api_key,
        model="bulbul:v3",
        speaker="shubh",
        language_code="en-IN",
        pace=1.0,
        speech_sample_rate=24000,
    )

    audio_output = PipeWireAudioOutput(
        event_bus=event_bus,
    )

    TTSPipeline(
        tts=tts,
        audio_output=audio_output,
        event_bus=event_bus,
    )

    # -------------------------
    # Events
    # -------------------------

    def handle_speech_started(event):
        print(
            "\n🎤 SPEECH STARTED"
        )

    def handle_speech_ended(event):
        segment = event.data[
            "segment"
        ]

        print(
            "\n🛑 SPEECH ENDED"
        )

        print(
            "Sending audio to Sarvam STT..."
        )

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
            "\n📨 TEXT_RECEIVED:",
            event.data["text"],
        )

    def handle_response(event):
        print(
            "\n🤖 DESKBOT:",
            event.data["text"],
        )

        print(
            "🔊 Sending response to TTS..."
        )

    def handle_speaking_started(event):
        print(
            "\n🔊 SPEAKING STARTED"
        )

    def handle_speaking_ended(event):
        print(
            "\n🔇 SPEAKING ENDED"
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

    event_bus.subscribe(
        EventTypes.SPEAKING_STARTED,
        handle_speaking_started,
    )

    event_bus.subscribe(
        EventTypes.SPEAKING_ENDED,
        handle_speaking_ended,
    )

    # -------------------------
    # AUDIO INPUT
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

    # -------------------------
    # START
    # -------------------------

    print(
        "=" * 60
    )

    print(
        "DESKBOT EMBODIED VOICE LOOP"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Browser:"
    )

    print(
        "http://192.168.1.33:8080"
    )

    print()

    print(
        "MIC"
    )

    print(
        " ↓"
    )

    print(
        "VAD"
    )

    print(
        " ↓"
    )

    print(
        "Sarvam STT"
    )

    print(
        " ↓"
    )

    print(
        "Input Gate"
    )

    print(
        " ↓"
    )

    print(
        "105B"
    )

    print(
        " ↓"
    )

    print(
        "Sarvam TTS"
    )

    print(
        " ↓"
    )

    print(
        "🔊 boAt Speaker"
    )

    print()

    print(
        "Press Ctrl+C to stop."
    )

    print(
        "=" * 60
    )

    pipeline.start()

    try:
        while True:
            pipeline.process_once()

    except KeyboardInterrupt:
        print(
            "\nStopping..."
        )

    finally:
        pipeline.stop()
        browser_display.stop()


if __name__ == "__main__":
    main()
