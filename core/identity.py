from pathlib import Path

import cv2
import numpy as np


class FaceRecognizer:
    def __init__(
        self,
        model_path="data/identity/lbph.yml",
        confidence_threshold=70.0,
    ):
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        self.trained = False

        if self.model_path.exists():
            self.load()

    def train(self, face_images):
        """
        Train LBPH using face images belonging to the primary user.
        """

        if not face_images:
            raise ValueError(
                "No face images supplied for training"
            )

        # OpenCV LBPH expects labels as a NumPy array.
        labels = np.ones(
            len(face_images),
            dtype=np.int32,
        )

        self.recognizer.train(
            face_images,
            labels,
        )

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.recognizer.write(
            str(self.model_path)
        )

        self.trained = True

    def load(self):
        self.recognizer.read(
            str(self.model_path)
        )

        self.trained = True

    def predict(self, face_image):
        """
        Returns:
        {
            "identity": "YOU" or "UNKNOWN",
            "confidence": float
        }
        """

        if not self.trained:
            raise RuntimeError(
                "Face recognizer is not trained"
            )

        if face_image is None:
            raise ValueError(
                "Face image cannot be None"
            )

        if len(face_image.shape) != 2:
            raise ValueError(
                "Face image must be grayscale"
            )

        label, confidence = self.recognizer.predict(
            face_image
        )

        if (
            label == 1
            and confidence <= self.confidence_threshold
        ):
            identity = "YOU"
        else:
            identity = "UNKNOWN"

        return {
            "identity": identity,
            "confidence": float(confidence),
        }
class IdentitySmoother:
    def __init__(self, required_frames=3):
        self.required_frames = required_frames

        self.current_identity = "UNKNOWN"
        self.candidate_identity = None
        self.candidate_count = 0

    def update(self, identity):
        if identity == self.current_identity:
            self.candidate_identity = None
            self.candidate_count = 0

            return self.current_identity

        if identity != self.candidate_identity:
            self.candidate_identity = identity
            self.candidate_count = 1

        else:
            self.candidate_count += 1

        if self.candidate_count >= self.required_frames:
            self.current_identity = identity
            self.candidate_identity = None
            self.candidate_count = 0

        return self.current_identity

    def reset(self):
        self.current_identity = "UNKNOWN"
        self.candidate_identity = None
        self.candidate_count = 0
