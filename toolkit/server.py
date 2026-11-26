import json, os, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import scoring, report
ROOT = os.path.join(os.path.dirname(__file__), "..")
def _load(*p): return json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))
UI = open(os.path.join(os.path.dirname(__file__), "ui.html"), "rb").read()

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, obj, ct="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == "/": return self._send(200, UI, "text/html")
        if self.path == "/api/questions": return self._send(200, scoring.QUESTIONS)
        if self.path == "/api/sample": return self._send(200, _load("examples", "sample_inventory.json"))
        m = re.match(r"^/api/preset/(overconfident|honest_partial)$", self.path)
        if m: return self._send(200, _load("examples", f"answers_{m.group(1)}.json"))
        self._send(404, {"error": "not found"})
    def do_POST(self):
        if self.path != "/api/assess": return self._send(404, {"error": "not found"})
        try:
            b = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)))
            inv = b.get("inventory") or _load("examples", "sample_inventory.json")
            res = scoring.assess(b.get("answers", {}), inv)
            self._send(200, {"summary": res["summary"], "domains": res["domains"], "roadmap": res["roadmap"][:10], "html": report.render(res)})
        except (KeyError, ValueError, TypeError) as e: self._send(400, {"error": f"invalid input: {e!r} (inventory needs policy, resources, iam, accounts)"})

def serve(port=8081): return ThreadingHTTPServer(("0.0.0.0", port), H)
