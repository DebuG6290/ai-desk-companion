import time

from core.camera import Camera
from core.perception import FaceDetector


def main():
    camera = Camera(width=640, height=480)
    detector = FaceDetector()

    try:
        print("Starting camera...")
        camera.start()

        print("Warming up...")
        time.sleep(2)

        print("Capturing frame...")
        frame = camera.capture_frame()

        print(f"Frame shape: {frame.shape}")

        print("Running face detection...")
        detections = detector.detect(frame)

        print(f"Faces detected: {len(detections)}")

        for index, detection in enumerate(detections, start=1):
            print(
                f"Face {index}: "
                f"x={detection['x']}, "
                f"y={detection['y']}, "
                f"width={detection['width']}, "
                f"height={detection['height']}"
            )

    finally:
        print("Stopping camera...")
        camera.stop()
        camera.close()

        print("Face detection test complete.")


if __name__ == "__main__":
    main()
