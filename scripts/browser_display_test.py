import time

from core.browser_display import BrowserDisplay
from core.state import DeskbotState


def main():
    display = BrowserDisplay()

    display.start()

    print("=" * 50)
    print("DESKBOT BROWSER DISPLAY")
    print("=" * 50)
    print()
    print("Open on your laptop:")
    print()
    print("http://192.168.1.33:8080")
    print()
    print("Changing states...")
    print("Press Ctrl+C to stop.")
    print()

    states = [
        DeskbotState.IDLE,
        DeskbotState.LISTENING,
        DeskbotState.THINKING,
        DeskbotState.SPEAKING,
        DeskbotState.CURIOUS,
        DeskbotState.HAPPY,
    ]

    try:
        while True:
            for state in states:
                print(
                    "STATE:",
                    state.value,
                )

                display.render(state)

                time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        display.stop()


if __name__ == "__main__":
    main()
