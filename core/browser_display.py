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
        self._debug_tracker = None
        self._camera_jpeg = None
        self._lock = threading.Lock()

        self._server = None
        self._thread = None

    def attach_debug_tracker(self, tracker):
        self._debug_tracker = tracker

    def update_camera_image(self, jpeg_bytes):
        with self._lock:
            self._camera_jpeg = jpeg_bytes

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

                if self.path == "/debug":
                    self._send_debug()
                    return

                if self.path == "/camera.jpg":
                    self._send_camera()
                    return

                self.send_response(404)
                self.end_headers()

            def _send_html(self):
                body = display._build_html().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self._safe_write(body)

            def _send_state(self):
                with display._lock:
                    state = display._state

                body = json.dumps({"state": state}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self._safe_write(body)

            def _send_debug(self):
                tracker = display._debug_tracker
                data = tracker.snapshot() if tracker else {}
                body = json.dumps(data, default=str).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self._safe_write(body)

            def _send_camera(self):
                with display._lock:
                    image = display._camera_jpeg

                if not image:
                    self.send_response(404)
                    self.end_headers()
                    return

                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(image)))
                self.end_headers()
                self._safe_write(image)

            def _safe_write(self, body):
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, format, *args):
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
        return r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Deskbot Debug</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;background:#080808;color:#fff;font-family:Arial,sans-serif}
#app{width:100%;height:100%;display:flex;gap:24px;padding:24px;overflow:auto}
#left{flex:1;min-width:420px;display:flex;flex-direction:column;gap:16px;align-items:center;justify-content:center}
#right{width:390px;display:flex;flex-direction:column;gap:12px}
.card{border:1px solid #333;border-radius:12px;background:#111;padding:14px}
.title{font-size:13px;letter-spacing:2px;color:#aaa;margin-bottom:10px}
#camera{width:100%;max-width:640px;border-radius:10px;background:#000;display:block}
#facePanel{width:100%;max-width:420px;height:260px;display:flex;align-items:center;justify-content:center}
.face{width:260px;display:flex;flex-direction:column;align-items:center;gap:28px}
.eyes{display:flex;gap:60px}.eye{width:42px;height:62px;background:#fff;border-radius:50%;position:relative}.pupil{width:19px;height:29px;background:#222;border-radius:50%;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}.brows{position:absolute;display:flex;gap:65px;margin-top:-120px}.brow{width:42px;border-top:6px solid #fff;border-radius:50%}.mouth{width:80px;height:22px;border-bottom:6px solid #fff;border-radius:0 0 50% 50%}
#state{font-size:18px;letter-spacing:3px;text-align:center}
.row{display:flex;justify-content:space-between;gap:10px;padding:4px 0}.label{color:#888}.value{font-weight:bold;text-align:right;word-break:break-word}
#events{height:270px;overflow:auto;font-family:monospace;font-size:12px}.event{padding:4px 0;border-bottom:1px solid #222}.muted{color:#777}
</style>
</head>
<body>
<div id="app">
<div id="left">
  <div class="card" style="width:100%;max-width:640px">
    <div class="title">LIVE CAMERA</div>
    <img id="camera" alt="camera">
  </div>
  <div class="card" id="facePanel">
    <div>
      <div class="face">
        <div class="eyes"><div class="eye"><div class="pupil"></div></div><div class="eye"><div class="pupil"></div></div></div>
        <div class="brows"><div class="brow"></div><div class="brow"></div></div>
        <div class="mouth"></div>
      </div>
      <div id="state">IDLE</div>
    </div>
  </div>
</div>
<div id="right">
  <div class="card"><div class="title">WORLD</div><div id="world"></div></div>
  <div class="card"><div class="title">DECISION</div><div id="decision">-</div></div>
  <div class="card"><div class="title">ACTION</div><div id="action">-</div></div>
  <div class="card"><div class="title">EVENT LOG</div><div id="events"></div></div>
</div>
</div>
<script>
function row(k,v){return '<div class="row"><span class="label">'+k+'</span><span class="value">'+(v ?? '-')+'</span></div>'}

async function refresh(){
 try{
  const d=await (await fetch('/debug?x='+Date.now(), {cache:'no-store'})).json();
  const w=d.world||{};
  document.getElementById('world').innerHTML=
    row('STATE',d.state?.toUpperCase())+
    row('PRESENCE',w.presence)+
    row('IDENTITY',w.identity)+
    row('DISTANCE',w.identity_confidence)+
    row('UNKNOWN',w.unknown_person_present)+
    row('CONVERSATION',w.conversation_active)+
    row('CAM FPS',d.camera?.fps);
  document.getElementById('decision').textContent=d.decision?JSON.stringify(d.decision):'-';
  document.getElementById('action').textContent=d.action?JSON.stringify(d.action):'-';
  document.getElementById('events').innerHTML=(d.events||[]).slice().reverse().map(e=>'<div class="event"><b>'+e.time+'</b> '+e.type+' <span class="muted">'+JSON.stringify(e.data)+'</span></div>').join('');
  const state=d.state||'idle';
  document.getElementById('state').textContent=state.toUpperCase();
  document.getElementById('facePanel').querySelector('.face').className='face '+state;
 }catch(e){}
}

const camera=document.getElementById('camera');
let previousObjectUrl=null;

async function loadCameraFrame(){
 try{
   const response=await fetch('/camera.jpg?x='+Date.now(), {cache:'no-store'});
   if(!response.ok) throw new Error('camera HTTP '+response.status);

   const blob=await response.blob();
   const objectUrl=URL.createObjectURL(blob);

   camera.onload=()=>{
     if(previousObjectUrl) URL.revokeObjectURL(previousObjectUrl);
     previousObjectUrl=objectUrl;
     setTimeout(loadCameraFrame, 100);
   };

   camera.onerror=()=>{
     URL.revokeObjectURL(objectUrl);
     setTimeout(loadCameraFrame, 250);
   };

   camera.src=objectUrl;
 }catch(e){
   setTimeout(loadCameraFrame, 250);
 }
}

loadCameraFrame();
setInterval(refresh,250);
refresh();
</script>
</body>
</html>
'''
