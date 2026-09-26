from core.perception import Perception


class FakePersonDetector:
    def detect(self, frame):
        return [{"type": "person"}]


class FakeFaceDetector:
    def detect(self, frame):
        return [{"type": "face"}]


def test_perception_combines_detectors():
    perception = Perception(
        person_detector=FakePersonDetector(),
        face_detector=FakeFaceDetector(),
    )

    people, faces = perception.detect("frame")

    assert people == [{"type": "person"}]
    assert faces == [{"type": "face"}]
