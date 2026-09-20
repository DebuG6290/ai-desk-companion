from collections import deque

from core.events import EventTypes


class SpeechState:
    SILENCE = "SILENCE"
    SPEECH = "SPEECH"


class SpeechSegmenter:
    def __init__(
        self,
        vad,
        required_speech_chunks=5,
        required_silence_chunks=15,
        min_speech_chunks=7,
        pre_roll_chunks=3,
    ):
        self.vad = vad

        # Assuming ~100 ms audio chunks:
        #
        # 5 chunks  = ~500 ms sustained speech to start
        # 15 chunks = ~1.5 sec sustained silence to end
        # 7 chunks  = ~700 ms minimum utterance
        #
        # This is intentionally conservative. We want:
        # one natural sentence -> one Sarvam call.

        self.required_speech_chunks = required_speech_chunks
        self.required_silence_chunks = required_silence_chunks
        self.min_speech_chunks = min_speech_chunks

        self.state = SpeechState.SILENCE

        self.speech_chunks = 0
        self.silence_chunks = 0

        self.segment = []

        self.pre_roll = deque(
            maxlen=pre_roll_chunks
        )

    def process(self, samples):
        result = self.vad.process(samples)

        # -------------------------------------------------
        # STATE: SILENCE
        # -------------------------------------------------
        if self.state == SpeechState.SILENCE:

            if result["speech"]:
                self.speech_chunks += 1
                self.silence_chunks = 0

                self.pre_roll.append(samples)

                # Do NOT start speech until sustained speech
                # has been detected.
                if (
                    self.speech_chunks
                    >= self.required_speech_chunks
                ):
                    self.state = SpeechState.SPEECH

                    self.segment = list(
                        self.pre_roll
                    )

                    self.pre_roll.clear()

                    return {
                        "event": EventTypes.SPEECH_STARTED,
                        "segment": None,
                        "speech": True,
                        "rms": result["rms"],
                    }

            else:
                # Noise/silence before speech.
                self.speech_chunks = 0
                self.silence_chunks = 0

                self.pre_roll.append(samples)

            return {
                "event": None,
                "segment": None,
                "speech": False,
                "rms": result["rms"],
            }

        # -------------------------------------------------
        # STATE: SPEECH
        # -------------------------------------------------
        if self.state == SpeechState.SPEECH:

            self.segment.append(samples)

            if result["speech"]:
                # Speech continues.
                self.silence_chunks = 0

            else:
                # Potential end of utterance.
                self.silence_chunks += 1

                # A short pause is NOT enough.
                if (
                    self.silence_chunks
                    < self.required_silence_chunks
                ):
                    return {
                        "event": None,
                        "segment": None,
                        "speech": True,
                        "rms": result["rms"],
                    }

                # -----------------------------------------
                # Speech has actually ended.
                # -----------------------------------------
                trailing_silence = (
                    self.required_silence_chunks
                )

                if len(self.segment) > trailing_silence:
                    completed_segment = self.segment[
                        :-trailing_silence
                    ]
                else:
                    completed_segment = []

                enough_audio = (
                    len(completed_segment)
                    >= self.min_speech_chunks
                )

                # Reset state BEFORE returning.
                self.state = SpeechState.SILENCE
                self.speech_chunks = 0
                self.silence_chunks = 0
                self.segment = []
                self.pre_roll.clear()

                if not enough_audio:
                    return {
                        "event": None,
                        "segment": None,
                        "speech": False,
                        "rms": result["rms"],
                    }

                return {
                    "event": EventTypes.SPEECH_ENDED,
                    "segment": completed_segment,
                    "speech": False,
                    "rms": result["rms"],
                }

        return {
            "event": None,
            "segment": None,
            "speech": False,
            "rms": result["rms"],
        }

    def reset(self):
        self.state = SpeechState.SILENCE
        self.speech_chunks = 0
        self.silence_chunks = 0
        self.segment = []
        self.pre_roll.clear()
