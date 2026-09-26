from core.action_executor import ActionExecutor
from core.decision_engine import DecisionEngine
from core.event_bus import EventBus
from core.events import Event, EventTypes
from core.world_model import WorldModel


def publish(event_bus, event_type, data=None):
    event_bus.publish(
        Event(
            type=event_type,
            data=data or {},
            timestamp=None,
        )
    )


def test_owner_return_flows_from_event_to_action():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(event_bus, world, cooldown_seconds=0.0)
    ActionExecutor(event_bus)

    responses = []
    event_bus.subscribe(EventTypes.TEXT_RESPONSE, responses.append)

    publish(event_bus, EventTypes.USER_RETURNED)

    assert len(responses) == 1
    assert responses[0].data["text"] == "Hey, you're back."


def test_unknown_person_curiosity_flows_to_expression_and_question():
    event_bus = EventBus()
    world = WorldModel(event_bus)
    DecisionEngine(event_bus, world, cooldown_seconds=0.0)
    ActionExecutor(event_bus)

    responses = []
    displays = []

    event_bus.subscribe(EventTypes.TEXT_RESPONSE, responses.append)
    event_bus.subscribe(EventTypes.DISPLAY_REQUESTED, displays.append)

    publish(event_bus, EventTypes.UNKNOWN_PERSON_ENTERED)
    publish(event_bus, EventTypes.CURIOSITY_TRIGGERED)

    assert len(displays) == 1
    assert displays[0].data["expression"] == "curious"

    assert len(responses) == 1
    assert "Who are you?" in responses[0].data["text"]
