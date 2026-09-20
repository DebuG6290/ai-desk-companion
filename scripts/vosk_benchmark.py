import json
import time
import wave

from vosk import Model, KaldiRecognizer


MODEL_PATH = "models/vosk-model-small-hi-0.22"
AUDIO_PATH = "/tmp/deskbot_mic_test_2_16k.wav"


print("Loading Vosk model...")
load_start = time.perf_counter()

model = Model(MODEL_PATH)

load_time = time.perf_counter() - load_start

print(f"Model loaded in {load_time:.2f} seconds")
print()


with wave.open(AUDIO_PATH, "rb") as wf:

    sample_rate = wf.getframerate()
    channels = wf.getnchannels()

    print(f"Audio sample rate: {sample_rate} Hz")
    print(f"Audio channels: {channels}")
    print(f"Audio duration: {wf.getnframes() / sample_rate:.2f} seconds")
    print()

    recognizer = KaldiRecognizer(
        model,
        sample_rate,
    )

    recognizer.SetWords(True)

    processing_start = time.perf_counter()

    while True:

        data = wf.readframes(4000)

        if not data:
            break

        recognizer.AcceptWaveform(data)

    processing_time = time.perf_counter() - processing_start

    result = json.loads(
        recognizer.FinalResult()
    )


audio_duration = (
    wf.getnframes() / sample_rate
)

print("===== VOSK RESULT =====")
print()

print("Transcript:")
print(result.get("text", ""))

print()
print("===== PERFORMANCE =====")
print()

print(f"Model load time : {load_time:.2f} sec")
print(f"Processing time : {processing_time:.2f} sec")
print(f"Audio duration  : {audio_duration:.2f} sec")

if audio_duration > 0:
    realtime_factor = (
        processing_time / audio_duration
    )

    print(
        f"Realtime factor : {realtime_factor:.2f}x"
    )

    if realtime_factor < 1:
        print(
            "Result: Faster than real-time"
        )
    else:
        print(
            "Result: Slower than real-time"
        )
