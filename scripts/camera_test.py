import time
from pathlib import Path

from core.camera import Camera


OUTPUT_FILE = Path("camera_test.jpg")


def main():
    camera = Camera(width=640, height=480)

    try:
        print("Starting camera...")
        camera.start()

        print("Warming up camera...")
        time.sleep(2)

        print("Capturing frame...")
        frame = camera.capture_frame()

        print(f"Frame captured!")
        print(f"Frame shape: {frame.shape}")
        print(f"Frame type: {frame.dtype}")

        # Save the frame using Picamera2's JPEG encoder.
        camera.camera.capture_file(str(OUTPUT_FILE))

        print(f"Image saved to: {OUTPUT_FILE.resolve()}")

    finally:
        print("Stopping camera...")
        camera.stop()
        camera.close()

        print("Camera test complete.")


if __name__ == "__main__":
    main()
