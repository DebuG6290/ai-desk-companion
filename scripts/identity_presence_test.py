import time

from core.camera import Camera
from core.event_bus import EventBus
from core.events import EventTypes
from core.identity_presence import IdentityPresenceManager
from core.perception import FaceDetector


def main():
    camera = Camera(
        width=640,
        height=480,
    )

    detector = FaceDetector()
    event_bus = EventBus()

    manager = IdentityPresenceManager(
        event_bus=event_bus,
        confidence_threshold=75.0,
        identity_required_frames=3,
        present_required_frames=3,
        absent_required_frames=5,
    )

    def on_user_returned(event):
        print()
        print(">>> EVENT: USER_RETURNED")
        print(f"    data: {event.data}")
        print()

    def on_unknown_entered(event):
        print()
        print(">>> EVENT: UNKNOWN_PERSON_ENTERED")
        print(f"    data: {event.data}")
        print()

    def on_user_left(event):
        print()
        print(">>> EVENT: USER_LEFT")
        print()

    event_bus.subscribe(
        EventTypes.USER_RETURNED,
        on_user_returned,
    )

    event_bus.subscribe(
        EventTypes.UNKNOWN_PERSON_ENTERED,
        on_unknown_entered,
    )

    event_bus.subscribe(
        EventTypes.USER_LEFT,
        on_user_left,
    )

    camera.start()

    print()
    print("==============================")
    print("Deskbot Identity Integration")
    print("==============================")
    print()
    print("Press Ctrl+C to stop.")
    print()

    last_status = None

    try:
        while True:
            frame = camera.capture_frame()

            faces = detector.detect(frame)

            result = manager.update(
                frame,
                faces,
            )

            status = (
                result["presence"],
                result["identity"],
            )

            if status != last_status:
                distance = result.get(
                    "distance",
                    None,
                )

                print(
                    f"Presence: {result['presence']} | "
                    f"Identity: {result['identity']} | "
                    f"Distance: {distance}"
                )

                last_status = status

            time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        print("Stopping Deskbot identity test...")

    finally:
        camera.stop()
        camera.close()


if __name__ == "__main__":
    main()
