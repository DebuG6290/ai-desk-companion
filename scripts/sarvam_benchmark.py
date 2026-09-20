import os
import time

from sarvamai import SarvamAI


AUDIO_PATH = "/tmp/deskbot_mic_test_2_16k.wav"


api_key = os.getenv("SARVAM_API_KEY")

if not api_key:
    raise RuntimeError(
        "SARVAM_API_KEY is not set"
    )


print("Connecting to Sarvam...")

client = SarvamAI(
    api_subscription_key=api_key
)

print("Uploading audio...")

start_time = time.perf_counter()

with open(AUDIO_PATH, "rb") as audio_file:

    response = client.speech_to_text.transcribe(
        file=audio_file,
        model="saaras:v3",
        mode="codemix",
    )

elapsed = time.perf_counter() - start_time


print()
print("===== SARVAM RESULT =====")
print()

print("Transcript:")
print(response.transcript)

print()
print("===== PERFORMANCE =====")
print()

print(f"API time       : {elapsed:.2f} sec")
print("Audio duration : 23.10 sec")

print()

if elapsed < 23.10:
    print("Result: Faster than real-time")
else:
    print("Result: Slower than real-time")
