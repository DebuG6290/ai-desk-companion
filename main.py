from datetime import datetime

from core.logger import logger
from core.events import Event
from core.event_bus import EventBus


def handle_user_returned(event):
    logger.info(f"Handler received event: {event.type}")


def main():
    logger.info("Deskbot is starting...")

    event_bus = EventBus()

    event_bus.subscribe("USER_RETURNED", handle_user_returned)

    event = Event(
        type="USER_RETURNED",
        data={},
        timestamp=datetime.now(),
    )

    event_bus.publish(event)

    logger.info("Deskbot is alive!")


if __name__ == "__main__":
    main()
