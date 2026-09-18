from core.presence import PresenceManager, PresenceState


def test_initial_state_is_absent():
    manager = PresenceManager()

    assert manager.state == PresenceState.ABSENT


def test_presence_requires_multiple_frames():
    manager = PresenceManager(required_present_frames=3)

    assert manager.update(True) is None
    assert manager.update(True) is None

    assert manager.update(True) == "PERSON_PRESENT"
    assert manager.state == PresenceState.PRESENT


def test_presence_does_not_repeat():
    manager = PresenceManager(required_present_frames=3)

    manager.update(True)
    manager.update(True)
    manager.update(True)

    assert manager.update(True) is None
    assert manager.state == PresenceState.PRESENT


def test_absence_requires_multiple_frames():
    manager = PresenceManager(
        required_present_frames=1,
        required_absent_frames=3,
    )

    assert manager.update(True) == "PERSON_PRESENT"

    assert manager.update(False) is None
    assert manager.update(False) is None

    assert manager.update(False) == "PERSON_ABSENT"
    assert manager.state == PresenceState.ABSENT


def test_detection_before_presence_threshold_resets_absence():
    manager = PresenceManager(
        required_present_frames=1,
        required_absent_frames=3,
    )

    manager.update(True)

    manager.update(False)
    manager.update(False)

    assert manager.update(True) is None
    assert manager.state == PresenceState.PRESENT
