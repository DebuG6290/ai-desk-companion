import time
from pathlib import Path

import cv2

from core.camera import Camera
from core.perception import FaceDetector
from core.identity import FaceRecognizer


SAMPLE_DIR = Path("data/identity/samples")
SAMPLE_COUNT = 15

MIN_FACE_SIZE = 70
MIN_BLUR_SCORE = 40
MIN_BRIGHTNESS = 40
MAX_BRIGHTNESS = 220


def preprocess_face(frame, face):
    x = face["x"]
    y = face["y"]
    w = face["width"]
    h = face["height"]

    if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:
        return None, "face too small"

    face_image = frame[
        y:y + h,
        x:x + w,
    ]

    if face_image.size == 0:
        return None, "empty crop"

    gray = cv2.cvtColor(
        face_image,
        cv2.COLOR_BGR2GRAY,
    )

    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F,
    ).var()

    brightness = gray.mean()

    if blur_score < MIN_BLUR_SCORE:
        return None, f"too blurry ({blur_score:.1f})"

    if brightness < MIN_BRIGHTNESS:
        return None, f"too dark ({brightness:.1f})"

    if brightness > MAX_BRIGHTNESS:
        return None, f"too bright ({brightness:.1f})"

    gray = cv2.resize(
        gray,
        (160, 160),
    )

    return gray, None


def clear_old_samples():
    SAMPLE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for file in SAMPLE_DIR.glob("sample_*.jpg"):
        file.unlink()


def main():
    clear_old_samples()

    camera = Camera(
        width=640,
        height=480,
    )

    detector = FaceDetector()

    samples = []

    try:
        camera.start()

        print()
        print("==============================")
        print("Deskbot Face Enrollment")
        print("==============================")
        print()
        print("We will capture 15 good-quality samples.")
        print()
        print("Move naturally between captures.")
        print()
        print("Suggested variation:")
        print("  1-3   : look straight")
        print("  4-5   : slight left")
        print("  6-7   : slight right")
        print("  8-9   : slightly up/down")
        print("  10-11 : a little farther")
        print("  12-13 : a little closer")
        print("  14    : slight smile")
        print("  15    : normal position")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)

        while len(samples) < SAMPLE_COUNT:

            frame = camera.capture_frame()

            faces = detector.detect(frame)

            if len(faces) == 0:
                print("No face detected.")
                time.sleep(0.3)
                continue

            if len(faces) > 1:
                print("Multiple faces detected. Please be alone.")
                time.sleep(0.3)
                continue

            face = faces[0]

            face_image, reason = preprocess_face(
                frame,
                face,
            )

            if face_image is None:
                print(f"Rejected: {reason}")
                time.sleep(0.3)
                continue

            sample_number = len(samples) + 1

            output_path = (
                SAMPLE_DIR
                / f"sample_{sample_number:02d}.jpg"
            )

            cv2.imwrite(
                str(output_path),
                face_image,
            )

            samples.append(face_image)

            print(
                f"Captured sample "
                f"{sample_number}/{SAMPLE_COUNT}"
            )

            # Give the user time to naturally change position.
            time.sleep(1.0)

        print()
        print("==============================")
        print("All samples captured.")
        print("==============================")
        print()

        print("Training LBPH recognizer...")

        recognizer = FaceRecognizer()

        recognizer.train(samples)

        print()
        print("Training complete.")
        print(
            f"Model saved to: {recognizer.model_path}"
        )
        print()
        print("Enrollment successful.")

    finally:
        camera.stop()
        camera.close()


if __name__ == "__main__":
    main()
