#!/usr/bin/env python3
"""
MoA API Service — 对外开放接口
只开放给开发者调用，不碰隐私
"""
import os, sys, json, time, hmac, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import moa

API_KEYS_FILE = Path.home() / ".openclaw" / "workspace" / "moa" / "api_keys.json"
USAGE_FILE = Path.home() / ".openclaw" / "workspace" / "moa" / "api_usage.jsonl"
HOST = "0.0.0.0"
PORT = 18791
NL = chr(10)

# 收费定价
PRICING = {
    "chat": 0.01,      # 1分钱一次
    "vision": 0.05,    # 5分钱一次
    "code": 0.02,      # 2分钱一次
}


def load_keys():
    if API_KEYS_FILE.exists():
        return json.loads(API_KEYS_FILE.read_text())
    keys = {"keys": {}, "total_revenue": 0.0}
    API_KEYS_FILE.write_text(json.dumps(keys, indent=2))
    return keys


def save_keys(k):
    API_KEYS_FILE.write_text(json.dumps(k, indent=2, ensure_ascii=False))


def generate_key(owner, deposit=0):
    """生成一个新 API Key"""
    keys = load_keys()
    api_key = hashlib.sha256((owner + str(time.time())).encode()).hexdigest()[:32]
    keys["keys"][api_key] = {
        "owner": owner,
        "created": time.time(),
        "balance": deposit,
        "total_used": 0,
        "active": True,
    }
    keys["total_revenue"] = keys.get("total_revenue", 0) + deposit
    save_keys(keys)
    return api_key


def verify_key(api_key):
    """验证 API Key 并返回用户信息"""
    keys = load_keys()
    info = keys["keys"].get(api_key)
    if not info:
        return None
    if not info.get("active", True):
        return None
    return info


def deduct(api_key, amount):
    """扣除费用"""
    keys = load_keys()
    info = keys["keys"].get(api_key)
    if not info:
        return False
    if info["balance"] < amount:
        return False
    info["balance"] -= amount
    info["total_used"] = info.get("total_used", 0) + amount
    save_keys(keys)
    return True


def log_usage(api_key, endpoint, cost):
    """记录使用"""
    entry = {"t": time.time(), "key": api_key[:8], "ep": endpoint, "cost": cost}
    with open(str(USAGE_FILE), "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + NL)


class MoAAPIHandler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _auth(self):
        key = self.headers.get("Authorization", "").replace("Bearer ", "")
        if not key:
            key = self.headers.get("X-API-Key", "")
        info = verify_key(key)
        if not info:
            self._json({"error": "invalid api key"}, 401)
            return None
        return key, info

    def do_GET(self):
        p = self.path.split("?")[0].rstrip("/")
        if p == "/":
            self._json({
                "service": "MoA API",
                "docs": "/docs",
                "pricing": PRICING,
                "endpoints": {
                    "POST /v1/chat": "Send message, cost: ¥0.01",
                    "POST /v1/code": "Generate code, cost: ¥0.02",
                }
            })
        elif p == "/docs":
            self._json({
                "usage": "Add Header: Authorization: Bearer YOUR_KEY",
                "chat": {"method": "POST", "path": "/v1/chat", "body": '{"q":"hello"}', "cost": "¥0.01"},
                "code": {"method": "POST", "path": "/v1/code", "body": '{"q":"write a script"}', "cost": "¥0.02"},
                "balance": "GET /v1/balance to check your balance",
            })
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        auth = self._auth()
        if not auth:
            return
        api_key, info = auth
        cl = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(cl).decode()) if cl else {}
        except:
            self._json({"error": "bad json"}, 400)
            return

        path = self.path.rstrip("/")
        
        if path == "/v1/chat":
            q = data.get("q", data.get("message", ""))
            if not q:
                self._json({"error": "no query"}, 400); return
            cost = PRICING["chat"]
            if not deduct(api_key, cost):
                self._json({"error": "insufficient balance"}, 402); return
            try:
                r = moa.rr(q)
                log_usage(api_key, "chat", cost)
                self._json({"q": q[:100], "r": str(r)[:500], "cost": cost, "balance": info["balance"]})
            except Exception as e:
                self._json({"error": str(e)}, 500)

        elif path == "/v1/code":
            q = data.get("q", data.get("prompt", data.get("message", "")))
            if not q:
                self._json({"error": "no query"}, 400); return
            cost = PRICING["code"]
            if not deduct(api_key, cost):
                self._json({"error": "insufficient balance"}, 402); return
            try:
                r = moa.rr(q)
                log_usage(api_key, "code", cost)
                self._json({"q": q[:100], "r": str(r)[:1000], "cost": cost, "balance": info["balance"]})
            except Exception as e:
                self._json({"error": str(e)}, 500)

        elif path == "/v1/balance":
            self._json({"balance": info["balance"], "total_used": info.get("total_used", 0)})

        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *a): pass


def main():
    server = HTTPServer((HOST, PORT), MoAAPIHandler)
    print()
    print("  MoA API Service")
    print("  " + "=" * 40)
    print("  Public API: http://" + HOST + ":" + str(PORT))
    print("  Pricing: ¥0.01/chat, ¥0.02/code")
    print()
    print("  Generate a key:")
    print(f"    python3 -c 'from api_service import generate_key; print(generate_key(\"user\", 10))'")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("  Stopped")
        server.server_close()


if __name__ == "__main__":
    main()
