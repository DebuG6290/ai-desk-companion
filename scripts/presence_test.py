import time

from core.camera import Camera
from core.perception import PersonDetector
from core.presence import PresenceManager


def main():
    camera = Camera(width=640, height=480)
    detector = PersonDetector()
    presence = PresenceManager()

    try:
        print("Starting camera...")
        camera.start()

        print("Warming up...")
        time.sleep(2)

        print("Presence monitoring started.")
        print("Press Ctrl+C to stop.")

        while True:
            frame = camera.capture_frame()

            detections = detector.detect(frame)
            person_detected = len(detections) > 0

            event = presence.update(person_detected)

            if event:
                print(
                    f"EVENT: {event} | "
                    f"people_detected={len(detections)}"
                )

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping presence monitor...")

    finally:
        camera.stop()
        camera.close()

        print("Presence test complete.")


if __name__ == "__main__":
    main()
