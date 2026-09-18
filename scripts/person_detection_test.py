import time

from core.camera import Camera
from core.perception import PersonDetector


def main():
    camera = Camera(width=640, height=480)
    detector = PersonDetector()

    try:
        print("Starting camera...")
        camera.start()

        print("Warming up...")
        time.sleep(2)

        print("Capturing frame...")
        frame = camera.capture_frame()

        print("Running person detection...")
        detections = detector.detect(frame)

        print(f"People detected: {len(detections)}")

        for index, detection in enumerate(detections, start=1):
            print(
                f"Person {index}: "
                f"x={detection['x']}, "
                f"y={detection['y']}, "
                f"width={detection['width']}, "
                f"height={detection['height']}, "
                f"confidence={detection['confidence']:.2f}"
            )

    finally:
        print("Stopping camera...")
        camera.stop()
        camera.close()

        print("Person detection test complete.")


if __name__ == "__main__":
    main()
