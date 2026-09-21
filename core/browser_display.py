from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading


class BrowserDisplay:
    def __init__(
        self,
        host="0.0.0.0",
        port=8080,
    ):
        self.host = host
        self.port = port

        self._state = "idle"
        self._lock = threading.Lock()

        self._server = None
        self._thread = None

    def start(self):
        display = self

        class Handler(BaseHTTPRequestHandler):

            def do_GET(self):
                if self.path == "/":
                    self._send_html()
                    return

                if self.path == "/state":
                    self._send_state()
                    return

                self.send_response(404)
                self.end_headers()

            def _send_html(self):
                body = display._build_html().encode(
                    "utf-8"
                )

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8",
                )

                self.send_header(
                    "Content-Length",
                    str(len(body)),
                )

                self.end_headers()

                self.wfile.write(body)

            def _send_state(self):
                with display._lock:
                    state = display._state

                body = json.dumps(
                    {"state": state}
                ).encode("utf-8")

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "application/json",
                )

                self.send_header(
                    "Content-Length",
                    str(len(body)),
                )

                self.end_headers()

                self.wfile.write(body)

            def log_message(
                self,
                format,
                *args,
            ):
                return

        self._server = ThreadingHTTPServer(
            (self.host, self.port),
            Handler,
        )

        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )

        self._thread.start()

    def render(self, state):
        with self._lock:
            self._state = state.value

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def _build_html(self):
        return """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>Deskbot</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;

    width: 100%;
    height: 100%;

    overflow: hidden;

    background: #000;

    font-family: Arial, sans-serif;
}

#deskbot {
    width: 100vw;
    height: 100vh;

    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    position: relative;
}


/* =========================
   FACE
   ========================= */

.face {
    width: 70vw;
    max-width: 420px;

    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 45px;
}


/* =========================
   EYES
   ========================= */

.eyes {
    display: flex;

    align-items: center;

    justify-content: center;

    gap: 70px;

    width: 100%;
}

.eye {
    width: 55px;
    height: 80px;

    background: white;

    border-radius: 50%;

    position: relative;

    transition:
        width 0.25s ease,
        height 0.25s ease,
        transform 0.25s ease;
}

.pupil {
    position: absolute;

    width: 25px;
    height: 38px;

    background: #222;

    border-radius: 50%;

    left: 50%;
    top: 50%;

    transform:
        translate(-50%, -50%);

    transition:
        transform 0.25s ease;
}


/* =========================
   BROWS
   ========================= */

.brows {
    position: absolute;

    top: -35px;

    display: flex;

    gap: 75px;
}

.brow {
    width: 50px;
    height: 12px;

    border-top: 7px solid white;

    border-radius: 50%;
}


/* =========================
   MOUTH
   ========================= */

.mouth {
    width: 95px;
    height: 25px;

    border-bottom:
        7px solid white;

    border-radius: 0 0 50% 50%;

    transition:
        width 0.2s ease,
        height 0.2s ease,
        border 0.2s ease;
}


/* =========================
   STATE LABEL
   ========================= */

#state {
    position: absolute;

    bottom: 7vh;

    color: white;

    font-size: 22px;

    font-weight: bold;

    letter-spacing: 2px;
}


/* =========================
   IDLE
   ========================= */

.idle .eye {
    width: 50px;
    height: 75px;
}

.idle .mouth {
    width: 90px;
    height: 22px;
}


/* =========================
   LISTENING
   ========================= */

.listening .eye {
    width: 60px;
    height: 88px;
}

.listening .pupil {
    transform:
        translate(-50%, -50%)
        scale(1.05);
}

.listening .mouth {
    width: 55px;
    height: 5px;

    border-bottom: 6px solid white;
}


/* =========================
   THINKING
   ========================= */

.thinking .pupil {
    transform:
        translate(-50%, -75%);
}

.thinking .brow:first-child {
    transform:
        rotate(-12deg);
}

.thinking .brow:last-child {
    transform:
        rotate(12deg);
}

.thinking .mouth {
    width: 65px;
    height: 5px;

    border-bottom: 6px solid white;

    border-radius: 50%;
}


/* =========================
   SPEAKING
   ========================= */

.speaking .mouth {
    width: 70px;
    height: 35px;

    border:
        6px solid white;

    border-radius: 50%;

    animation:
        speakingMouth
        0.35s
        ease-in-out
        infinite alternate;
}

@keyframes speakingMouth {

    from {
        height: 20px;
        width: 65px;
    }

    to {
        height: 50px;
        width: 75px;
    }
}


/* =========================
   CURIOUS
   ========================= */

.curious .eye:first-child {
    transform:
        translateY(5px)
        rotate(-5deg);
}

.curious .eye:last-child {
    transform:
        translateY(-8px)
        rotate(5deg);
}

.curious .pupil {
    transform:
        translate(
            -35%,
            -65%
        );
}

.curious .brow:first-child {
    transform:
        rotate(-15deg)
        translateY(-4px);
}

.curious .brow:last-child {
    transform:
        rotate(15deg)
        translateY(4px);
}

.curious .mouth {
    width: 12px;
    height: 12px;

    border:
        6px solid white;

    border-radius: 50%;
}


/* =========================
   HAPPY
   ========================= */

.happy .eye {
    width: 70px;
    height: 35px;

    background: transparent;

    border-top:
        8px solid white;

    border-radius: 50%;

    transform:
        translateY(15px);
}

.happy .pupil {
    display: none;
}

.happy .brow {
    display: none;
}

.happy .mouth {
    width: 105px;
    height: 55px;

    border:
        7px solid white;

    border-top: none;

    border-radius:
        0 0 60px 60px;
}


/* =========================
   RESPONSIVE
   ========================= */

@media (max-width: 600px) {

    .face {
        gap: 35px;
    }

    .eyes {
        gap: 45px;
    }

    .eye {
        width: 42px;
        height: 62px;
    }

    .pupil {
        width: 20px;
        height: 30px;
    }

    #state {
        font-size: 17px;
    }
}

</style>

</head>


<body>

<div id="deskbot">

    <div
        id="face"
        class="face idle"
    >

        <div class="eyes">

            <div class="eye">

                <div class="pupil"></div>

            </div>

            <div class="eye">

                <div class="pupil"></div>

            </div>

        </div>

        <div class="brows">

            <div class="brow"></div>

            <div class="brow"></div>

        </div>

        <div class="mouth"></div>

    </div>

    <div id="state">
        IDLE
    </div>

</div>


<script>

let currentState = "idle";


async function updateState() {

    try {

        const response =
            await fetch("/state");

        const data =
            await response.json();

        const newState =
            data.state;

        if (newState === currentState) {
            return;
        }

        currentState = newState;

        const face =
            document.getElementById("face");

        face.className =
            "face " + newState;

        document
            .getElementById("state")
            .innerText =
            newState.toUpperCase();

    }

    catch (error) {

        console.log(
            "Display connection error:",
            error
        );

    }
}


setInterval(
    updateState,
    100
);

updateState();

</script>

</body>

</html>
"""
