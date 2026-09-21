from core.events import Event, EventTypes


class TTSPipeline:
    def __init__(
        self,
        tts,
        audio_output,
        event_bus=None,
    ):
        self.tts = tts
        self.audio_output = audio_output
        self.event_bus = event_bus

        if self.event_bus is not None:
            self.event_bus.subscribe(
                EventTypes.TEXT_RESPONSE,
                self._handle_text_response,
            )

    def _handle_text_response(self, event):
        text = event.data.get(
            "text",
            "",
        )

        response_mode = event.data.get(
            "response_mode",
            "voice_and_display",
        )

        if not text:
            return

        if response_mode != "voice_and_display":
            return

        self.process(text)

    def process(self, text):
        if not text:
            return None

        result = self.tts.synthesize(
            text
        )

        audio = result.get(
            "audio",
            b"",
        )

        if audio:
            self.audio_output.play(
                audio
            )

        return result
