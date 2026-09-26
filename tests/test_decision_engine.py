from core.actions import ActionIntents, ActionTypes
from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.decision_engine import DecisionEngine
from core.world_model import WorldModel


def publish(event_bus, event_type, data=None):
    event_bus.publish(
        Event(
            type=event_type,
            data=data or {},
            timestamp=None,
        )
    )


def test_owner_return_requests_greeting():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(
        event_bus=event_bus,
        world_model=world,
    )

    actions = []

    event_bus.subscribe(
        EventTypes.ACTION_REQUESTED,
        actions.append,
    )

    publish(event_bus, EventTypes.USER_RETURNED)

    assert len(actions) == 1
    assert actions[0].data["action_type"] == ActionTypes.EXPRESS
    assert actions[0].data["intent"] == ActionIntents.GREET_OWNER


def test_unknown_person_entry_requests_notice():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(
        event_bus=event_bus,
        world_model=world,
    )

    actions = []
    event_bus.subscribe(
        EventTypes.ACTION_REQUESTED,
        actions.append,
    )

    publish(event_bus, EventTypes.UNKNOWN_PERSON_ENTERED)

    assert len(actions) == 1
    assert actions[0].data["action_type"] == ActionTypes.EXPRESS
    assert (
        actions[0].data["intent"]
        == ActionIntents.NOTICE_UNKNOWN_PERSON
    )


def test_curiosity_requests_introduction_question():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(
        event_bus=event_bus,
        world_model=world,
        cooldown_seconds=0.0,
    )

    actions = []
    event_bus.subscribe(
        EventTypes.ACTION_REQUESTED,
        actions.append,
    )

    publish(event_bus, EventTypes.UNKNOWN_PERSON_ENTERED)
    publish(event_bus, EventTypes.CURIOSITY_TRIGGERED)

    assert len(actions) == 2
    assert actions[-1].data["action_type"] == ActionTypes.ASK
    assert (
        actions[-1].data["intent"]
        == ActionIntents.ASK_UNKNOWN_PERSON_TO_INTRODUCE
    )


def test_curiosity_does_not_interrupt_active_conversation():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(
        event_bus=event_bus,
        world_model=world,
        cooldown_seconds=0.0,
    )

    actions = []
    event_bus.subscribe(
        EventTypes.ACTION_REQUESTED,
        actions.append,
    )

    publish(event_bus, EventTypes.UNKNOWN_PERSON_ENTERED)
    publish(event_bus, EventTypes.SPEECH_STARTED)
    publish(event_bus, EventTypes.CURIOSITY_TRIGGERED)

    assert len(actions) == 1
