class EventBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    def publish(self, event):
        handlers = self.handlers.get(event.type, [])

        if not handlers:
            return

        for handler in handlers:
            handler(event)
