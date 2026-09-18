from core.curiosity import CuriosityManager


def test_unknown_does_not_trigger_immediately():
    manager = CuriosityManager(
        curiosity_delay=5.0
    )

    assert manager.update("UNKNOWN") is False


def test_known_person_does_not_trigger():
    manager = CuriosityManager(
        curiosity_delay=0.0
    )

    assert manager.update("YOU") is False


def test_unknown_triggers_after_delay():
    manager = CuriosityManager(
        curiosity_delay=0.0
    )

    assert manager.update("UNKNOWN") is False
    assert manager.update("UNKNOWN") is True


def test_curiosity_does_not_repeat_during_cooldown():
    manager = CuriosityManager(
        curiosity_delay=0.0,
        cooldown=30.0,
    )

    manager.update("UNKNOWN")

    assert manager.update("UNKNOWN") is True
    assert manager.update("UNKNOWN") is False


def test_returning_to_known_person_resets_unknown():
    manager = CuriosityManager(
        curiosity_delay=0.0
    )

    manager.update("UNKNOWN")
    assert manager.update("UNKNOWN") is True

    manager.update("YOU")

    assert manager.update("UNKNOWN") is False
