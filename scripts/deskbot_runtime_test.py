import os

from dotenv import load_dotenv

from core.action_executor import ActionExecutor
from core.audio import PipeWireAudioInput
from core.audio_output import PipeWireAudioOutput
from core.audio_pipeline import AudioPipeline
from core.browser_display import BrowserDisplay
from core.camera import Camera
from core.decision_engine import DecisionEngine
from core.display_controller import DisplayController
from core.event_bus import EventBus
from core.identity_presence import IdentityPresenceManager
from core.llm import SarvamLLM
from core.llm_pipeline import LLMPipeline
from core.perception import Perception
from core.runtime import DeskbotRuntime
from core.state import StateController
from core.tts import SarvamTextToSpeech
from core.tts_pipeline import TTSPipeline
from core.voice import SarvamSpeechToText
from core.voice_pipeline import VoicePipeline
from core.world_model import WorldModel


load_dotenv()


def main():
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise RuntimeError("SARVAM_API_KEY is not set")

    event_bus = EventBus()

    # State + browser display.
    browser_display = BrowserDisplay(
        host="0.0.0.0",
        port=8080,
    )
    display_controller = DisplayController(browser_display)
    StateController(
        event_bus=event_bus,
        display_controller=display_controller,
    )

    # World model + behaviour.
    world_model = WorldModel(event_bus)
    DecisionEngine(
        event_bus=event_bus,
        world_model=world_model,
    )
    ActionExecutor(event_bus)

    # Voice.
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
    LLMPipeline(
        llm=llm,
        event_bus=event_bus,
    )

    tts = SarvamTextToSpeech(
        api_key=api_key,
        model="bulbul:v3",
        speaker="shubh",
        language_code="en-IN",
        pace=1.0,
        speech_sample_rate=24000,
    )
    TTSPipeline(
        tts=tts,
        audio_output=PipeWireAudioOutput(event_bus=event_bus),
        event_bus=event_bus,
    )

    def handle_speech_started(event):
        print("\n🎤 SPEECH STARTED")

    def handle_speech_ended(event):
        print("\n🛑 SPEECH ENDED")
        result = voice_pipeline.process(
            event.data["segment"]
        )
        if result:
            print(
                "\n🧠 TRANSCRIPT:",
                result["transcription"]["text"],
            )

    def handle_text(event):
        print("\n📨 TEXT_RECEIVED:", event.data["text"])

    def handle_response(event):
        print("\n🤖 DESKBOT:", event.data["text"])

    def handle_action(event):
        print(
            "\n⚙️ ACTION:",
            event.data.get("intent"),
        )

    def handle_display(event):
        print(
            "\n🖥️ DISPLAY:",
            event.data.get("expression"),
        )

    event_bus.subscribe(
        "SPEECH_STARTED",
        handle_speech_started,
    )
    event_bus.subscribe(
        "SPEECH_ENDED",
        handle_speech_ended,
    )
    event_bus.subscribe(
        "TEXT_RECEIVED",
        handle_text,
    )
    event_bus.subscribe(
        "TEXT_RESPONSE",
        handle_response,
    )
    event_bus.subscribe(
        "ACTION_REQUESTED",
        handle_action,
    )
    event_bus.subscribe(
        "DISPLAY_REQUESTED",
        handle_display,
    )

    camera = Camera(
        width=640,
        height=480,
    )
    perception = Perception()
    identity_presence = IdentityPresenceManager(
        event_bus=event_bus,
    )

    audio = PipeWireAudioInput(
        target=89,
        sample_rate=16000,
        channels=1,
        chunk_samples=1600,
    )
    audio_pipeline = AudioPipeline(
        audio_input=audio,
        event_bus=event_bus,
    )

    runtime = DeskbotRuntime(
        camera=camera,
        perception=perception,
        identity_presence=identity_presence,
        audio_pipeline=audio_pipeline,
        event_bus=event_bus,
        browser_display=browser_display,
        camera_interval=0.1,
    )

    print("=" * 60)
    print("DESKBOT INTEGRATED RUNTIME")
    print("=" * 60)
    print("Browser: http://192.168.1.33:8080")
    print()
    print("CAMERA → PERCEPTION → IDENTITY → WORLD MODEL")
    print("MIC → VAD → STT → LLM → TTS")
    print("                 ↓")
    print("        DECISION ENGINE")
    print("                 ↓")
    print("          ACTION EXECUTOR")
    print()
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    runtime.run_forever()


if __name__ == "__main__":
    main()
