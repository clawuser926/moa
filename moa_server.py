#!/usr/bin/env python3
"""MoA Server — 微信小弟的 API 接口"""
import os, sys, json, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))

HOST = "127.0.0.1"
PORT = 18790
LOG_FILE = Path.home() / ".openclaw" / "workspace" / "moa" / "server_logs.jsonl"
server_start = time.time()


def log_call(ep, p, r, d):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    e = {"t": time.time(), "ep": ep, "p": str(p)[:50], "dur": round(d, 2), "ok": str(r).count("error") == 0}
    with open(str(LOG_FILE), "a") as f:
        f.write(json.dumps(e, ensure_ascii=False) + chr(10))


class MoAHandler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        p = self.path.split("?")[0].rstrip("/")
        if p == "":
            self._json({"endpoints": {"/chat?q=x": "chat", "/status": "status", "/logs?n=10": "logs"}})
        elif p == "/status":
            self._json(self._status())
        elif p == "/chat":
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            if not q:
                self._json({"error": "?q= required"}, 400)
                return
            t0 = time.time()
            r = self._chat(q)
            log_call("chat", q, r, time.time() - t0)
            self._json({"q": q[:200], "r": r, "t": round(time.time() - t0, 2)})
        elif p == "/logs":
            from urllib.parse import urlparse, parse_qs
            n = int(parse_qs(urlparse(self.path).query).get("n", [10])[0])
            self._json({"logs": self._logs(n)})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        cl = int(self.headers.get("Content-Length", 0))
        if cl == 0:
            self._json({"error": "no body"}, 400)
            return
        try:
            data = json.loads(self.rfile.read(cl).decode("utf-8"))
        except:
            self._json({"error": "bad json"}, 400)
            return
        path = self.path.rstrip("/")
        if path == "/chat":
            q = data.get("q", data.get("query", data.get("message", "")))
            if not q:
                self._json({"error": "no query"}, 400)
                return
            t0 = time.time()
            r = self._chat(q)
            log_call("chat", q, r, time.time() - t0)
            self._json({"q": q[:200], "r": r, "t": round(time.time() - t0, 2)})
        elif path == "/vision":
            img = data.get("image", data.get("path", ""))
            if not img:
                self._json({"error": "no image"}, 400)
                return
            t0 = time.time()
            r = self._vision(img, data.get("prompt", ""))
            log_call("vision", img, r, time.time() - t0)
            self._json({"img": img, "r": r, "t": round(time.time() - t0, 2)})
        else:
            self._json({"error": "not found"}, 404)

    def _chat(self, q):
        try:
            import moa
            return moa.rr(q) or "(empty)"
        except Exception as e:
            return "[Chat Error] " + str(e)

    def _vision(self, img, prompt=""):
        try:
            from vision_agent import handle_image
            return handle_image(img, prompt) or "(empty)"
        except Exception as e:
            return "[Vision Error] " + str(e)

    def _status(self):
        try:
            from knowledge_hub import scan_models, scan_skills, scan_apis, vision_ready
            return {"models": scan_models(), "skills": len(scan_skills()), "apis": len(scan_apis()), "vision": vision_ready(), "uptime": round(time.time() - server_start)}
        except Exception as e:
            return {"error": str(e)}

    def _logs(self, n=10):
        if not LOG_FILE.exists():
            return []
        all_lines = LOG_FILE.read_text().strip().split(chr(10))
        if not all_lines:
            return []
        return [json.loads(l) for l in all_lines[-n:]]

    def log_message(self, fmt, *args):
        pass


def main():
    s = HTTPServer((HOST, PORT), MoAHandler)
    print("=" * 60)
    print("  MoA Server: http://{}:{}".format(HOST, PORT))
    print("=" * 60)
    print("  GET  /chat?q=xxx     Chat")
    print("  POST /chat {q}       Chat (JSON)")
    print("  POST /vision {image} Vision")
    print("  GET  /status         Status")
    print("  GET  /logs?n=10      Logs")
    print()
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print("Stopped")
        s.server_close()

if __name__ == "__main__":
    main()
