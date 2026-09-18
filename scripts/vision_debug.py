import time
from datetime import datetime
from pathlib import Path
from threading import Lock, Thread

import cv2
from flask import Flask, Response

from core.camera import Camera
from core.perception import PersonDetector, FaceDetector


app = Flask(__name__)

camera = Camera(width=640, height=480)
person_detector = PersonDetector()
face_detector = FaceDetector()

frame_lock = Lock()
latest_frame = None

running = True

people_count = 0
face_count = 0
presence = "ABSENT"

last_presence = "ABSENT"

DETECTION_DIR = Path("logs/detections")
DETECTION_DIR.mkdir(parents=True, exist_ok=True)


def process_camera():
    global latest_frame
    global people_count
    global face_count
    global presence
    global last_presence

    camera.start()

    print("Warming up camera...")
    time.sleep(2)

    print("Vision debugger started.")

    while running:
        frame = camera.capture_frame()

        # Detect people
        people = person_detector.detect(frame)

        # Detect faces
        faces = face_detector.detect(frame)

        people_count = len(people)
        face_count = len(faces)

        # A detected person OR face means someone is visually present.
        presence = (
            "PRESENT"
            if people_count > 0 or face_count > 0
            else "ABSENT"
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        # Picamera2 RGB888 returns an OpenCV-compatible BGR array.
        # Do NOT convert RGB -> BGR again.
        # ---------------------------------------------------------
        debug_frame = frame.copy()

        # Draw person boxes
        for person in people:
            x = person["x"]
            y = person["y"]
            w = person["width"]
            h = person["height"]

            cv2.rectangle(
                debug_frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2,
            )

            label = f"PERSON {person['confidence']:.2f}"

            cv2.putText(
                debug_frame,
                label,
                (x, max(y - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        # Draw face boxes
        for face in faces:
            x = face["x"]
            y = face["y"]
            w = face["width"]
            h = face["height"]

            cv2.rectangle(
                debug_frame,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2,
            )

            cv2.putText(
                debug_frame,
                "FACE",
                (x, max(y - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                1,
                cv2.LINE_AA,
            )

        # Debug information
        cv2.putText(
            debug_frame,
            f"Presence: {presence}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            debug_frame,
            f"People: {people_count}  Faces: {face_count}",
            (10, 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------------------------------
        # Save ONLY when presence changes.
        # This gives us useful event frames instead of duplicates.
        # ---------------------------------------------------------
        if presence != last_presence:
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )[:-3]

            output_path = (
                DETECTION_DIR
                / f"{presence.lower()}_{timestamp}.jpg"
            )

            cv2.imwrite(
                str(output_path),
                debug_frame,
            )

            print(
                f"PRESENCE CHANGE: "
                f"{last_presence} -> {presence}"
            )

            print(
                f"Saved debug frame: {output_path}"
            )

            last_presence = presence

        # Encode frame for browser
        success, encoded = cv2.imencode(
            ".jpg",
            debug_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80],
        )

        if success:
            with frame_lock:
                latest_frame = encoded.tobytes()

        # Small delay to avoid unnecessarily hammering the Pi.
        time.sleep(0.05)

    camera.stop()
    camera.close()


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deskbot Vision Debugger</title>

        <style>
            body {
                background: #111;
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
            }

            img {
                max-width: 90%;
                border: 2px solid #555;
            }
        </style>
    </head>

    <body>

        <h1>Deskbot Vision Debugger</h1>

        <img src="/video">

        <p>
            Green = Person
            &nbsp;&nbsp;&nbsp;
            Blue = Face
        </p>

    </body>
    </html>
    """


@app.route("/video")
def video():
    def generate():
        while running:
            with frame_lock:
                frame = latest_frame

            if frame is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

            time.sleep(0.05)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def main():
    thread = Thread(
        target=process_camera,
        daemon=True,
    )

    thread.start()

    print()
    print("===================================")
    print("Deskbot Vision Debugger")
    print("===================================")
    print("Open on your laptop:")
    print()
    print("http://deskbot.local:5000")
    print()
    print("Press Ctrl+C to stop.")
    print("===================================")
    print()

    try:
        app.run(
            host="0.0.0.0",
            port=5000,
            threaded=True,
        )

    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    main()
