import cv2


class PersonDetector:
    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(
            cv2.HOGDescriptor_getDefaultPeopleDetector()
        )

    def detect(self, frame):
        boxes, weights = self.hog.detectMultiScale(
            frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
        )

        detections = []

        for box, weight in zip(boxes, weights):
            x, y, width, height = box

            detections.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(width),
                    "height": int(height),
                    "confidence": float(weight),
                }
            )

        return detections


class FaceDetector:
    def __init__(self):
        cascade_path = (
            "/usr/share/opencv4/haarcascades/"
            "haarcascade_frontalface_default.xml"
        )

        self.cascade = cv2.CascadeClassifier(cascade_path)

        if self.cascade.empty():
            raise RuntimeError(
                f"Failed to load face cascade: {cascade_path}"
            )

    def detect(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
        )

        detections = []

        frame_height, frame_width = gray.shape

        for x, y, width, height in faces:

            # Light geometry guardrail only.
            aspect_ratio = width / height

            if aspect_ratio < 0.60 or aspect_ratio > 1.50:
                continue

            # Reject extremely large accidental detections.
            area_ratio = (
                width * height
            ) / (
                frame_width * frame_height
            )

            if area_ratio > 0.80:
                continue

            detections.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(width),
                    "height": int(height),
                }
            )

        return detections


class Perception:
    """
    Combined perception facade used by the integrated runtime.

    It keeps person and face detection as separate capabilities while
    exposing one stable detect(frame) interface to the runtime.
    """

    def __init__(self, person_detector=None, face_detector=None):
        self.person_detector = person_detector or PersonDetector()
        self.face_detector = face_detector or FaceDetector()

    def detect(self, frame):
        people = self.person_detector.detect(frame)
        faces = self.face_detector.detect(frame)
        return people, faces
