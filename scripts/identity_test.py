import time
from threading import Lock, Thread

import cv2
from flask import Flask, Response

from core.camera import Camera
from core.perception import FaceDetector
from core.identity import FaceRecognizer


app = Flask(__name__)

camera = Camera(width=640, height=480)
face_detector = FaceDetector()
recognizer = FaceRecognizer(
    confidence_threshold=70.0
)

frame_lock = Lock()
latest_frame = None

running = True


def prepare_face(frame, face):
    x = face["x"]
    y = face["y"]
    w = face["width"]
    h = face["height"]

    face_image = frame[
        y:y + h,
        x:x + w,
    ]

    if face_image.size == 0:
        return None

    gray = cv2.cvtColor(
        face_image,
        cv2.COLOR_BGR2GRAY,
    )

    gray = cv2.resize(
        gray,
        (160, 160),
    )

    return gray


def process_camera():
    global latest_frame

    camera.start()

    print("Warming up camera...")
    time.sleep(2)

    print("Identity debugger started.")

    while running:
        frame = camera.capture_frame()

        faces = face_detector.detect(frame)

        debug_frame = frame.copy()

        cv2.putText(
            debug_frame,
            f"Faces: {len(faces)}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        for face in faces:

            x = face["x"]
            y = face["y"]
            w = face["width"]
            h = face["height"]

            face_image = prepare_face(
                frame,
                face,
            )

            if face_image is None:
                continue

            result = recognizer.predict(
                face_image
            )

            identity = result["identity"]
            distance = result["confidence"]

            if identity == "YOU":
                box_color = (0, 255, 0)
            else:
                box_color = (0, 0, 255)

            cv2.rectangle(
                debug_frame,
                (x, y),
                (x + w, y + h),
                box_color,
                2,
            )

            label = (
                f"{identity} "
                f"distance={distance:.1f}"
            )

            cv2.putText(
                debug_frame,
                label,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2,
                cv2.LINE_AA,
            )

        success, encoded = cv2.imencode(
            ".jpg",
            debug_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80],
        )

        if success:
            with frame_lock:
                latest_frame = encoded.tobytes()

        time.sleep(0.05)

    camera.stop()
    camera.close()


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deskbot Identity Debugger</title>

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

        <h1>Deskbot Identity Debugger</h1>

        <img src="/video">

        <p>
            Green = YOU
            &nbsp;&nbsp;&nbsp;
            Red = UNKNOWN
        </p>

        <p>
            Lower LBPH distance = better match
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
    print("Deskbot Identity Debugger")
    print("===================================")
    print()
    print("Open on your laptop:")
    print()
    print("http://deskbot.local:5001")
    print()
    print("Press Ctrl+C to stop.")
    print("===================================")

    try:
        app.run(
            host="0.0.0.0",
            port=5001,
            threaded=True,
        )

    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    main()
