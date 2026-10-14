"""Giao diện web (stdlib, không cần framework)."""
import base64
import hmac
import io
import json
import mimetypes
import os
import re
import select
import socket
import sys
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from ..core import config, testcases
from . import jobs

STATIC = Path(__file__).parent / "static"
JOBS = jobs.JobManager()
SAFE = re.compile(r"^[\w\-. ]+$")


AUTH_USER = os.environ.get("AUTH_USER", "")
AUTH_PASS = os.environ.get("AUTH_PASS", "")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authorized(self):
        """Basic Auth nếu có AUTH_USER/AUTH_PASS (bắt buộc khi public qua tunnel)."""
        if not (AUTH_USER and AUTH_PASS):
            return True
        h = self.headers.get("Authorization", "")
        try:
            user, _, pw = base64.b64decode(h.split(" ", 1)[1]).decode().partition(":")
        except Exception:
            user = pw = ""
        ok = hmac.compare_digest(user, AUTH_USER) & hmac.compare_digest(pw, AUTH_PASS)
        if not ok:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Khan AutoTest"')
            self.send_header("Content-Length", "0")
            self.end_headers()
        return ok

    def _send(self, code, body, ctype="application/json", headers=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") or ctype == "application/json" else ""))
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, download=None):
        if not path.is_file():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        h = {"Content-Disposition": f'attachment; filename="{download}"'} if download else None
        self._send(200, path.read_bytes(), ctype, h)

    def _json_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def _vnc_proxy(self):
        """Chuyển tiếp /vnc/* (HTTP + WebSocket) tới noVNC nội bộ, để xem trực tiếp được qua tunnel
        chỉ mở cổng giao diện. Đã qua Basic Auth ở do_GET."""
        port = int(os.environ.get("VNC_PORT") or 0)
        if not port:
            return self._send(404, {"error": "noVNC chưa bật"})
        try:
            up = socket.create_connection(("127.0.0.1", port), timeout=5)
        except OSError:
            return self._send(502, {"error": "noVNC không phản hồi"})
        path = self.path[len("/vnc"):] or "/"
        lines = [f"{self.command} {path} HTTP/1.1"]
        upgrade = any(k.lower() == "upgrade" for k in self.headers)
        for k, v in self.headers.items():
            if k.lower() == "connection" and not upgrade:
                continue
            lines.append(f"{k}: {v}")
        if not upgrade:
            lines.append("Connection: close")
        up.sendall(("\r\n".join(lines) + "\r\n\r\n").encode())
        up.settimeout(None)
        cl = self.connection
        cl.settimeout(None)
        socks = [cl, up]
        try:
            while True:
                r, _, _ = select.select(socks, [], [], 3600)
                if not r:
                    break
                for s in r:
                    data = s.recv(65536)
                    if not data:
                        return
                    (up if s is cl else cl).sendall(data)
        except OSError:
            pass
        finally:
            up.close()
            self.close_connection = True

    def do_GET(self):
        if not self._authorized():
            return
        u = urlparse(self.path)
        p, q = u.path, parse_qs(u.query)
        if p.startswith("/vnc/"):
            return self._vnc_proxy()
        try:
            if p == "/":
                return self._file(STATIC / "index.html")
            if p == "/theme.css":
                return self._file(STATIC / "theme.css")
            if p == "/api/files":
                fs = sorted(f.name for f in config.TESTCASE_DIR.iterdir() if f.suffix.lower() in (".csv", ".xlsx", ".json"))
                return self._send(200, {"files": fs, "defaults": config.DEFAULTS,
                                        "scenarios": testcases.SCENARIOS, "modes": testcases.MODES,
                                        "vnc": os.environ.get("VNC_PORT") or None})
            if p == "/api/testcases":
                f = q.get("file", [""])[0]
                if not SAFE.match(f):
                    return self._send(400, {"error": "tên file không hợp lệ"})
                tcs = testcases.load(config.TESTCASE_DIR / f)
                return self._send(200, {"testcases": tcs, "errors": testcases.validate(tcs)})
            if p == "/api/status":
                return self._send(200, JOBS.snapshot())
            if p == "/api/history":
                return self._send(200, jobs.history())
            if p == "/api/template":
                return self._file(config.TESTCASE_DIR / "khan_full.xlsx", "mau_testcase.xlsx")
            m = re.match(r"^/runs/([\w]+)/(.+)$", p)
            if m:
                rid, rel = m.group(1), unquote(m.group(2))
                if rel == "all.zip":
                    return self._zip(rid)
                target = (config.RUNS_DIR / rid / rel).resolve()
                if config.RUNS_DIR.resolve() not in target.parents:
                    return self._send(403, {"error": "forbidden"})
                dl = f"{rid}_{target.name}" if q.get("dl") else None
                return self._file(target, dl)
            self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _zip(self, rid):
        d = config.RUNS_DIR / rid
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in d.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(d))
        self._send(200, buf.getvalue(), "application/zip", {"Content-Disposition": f'attachment; filename="{rid}.zip"'})

    def do_POST(self):
        if not self._authorized():
            return
        u = urlparse(self.path)
        try:
            if u.path == "/api/run":
                b = self._json_body()
                s = b.get("settings", {})
                if not SAFE.match(b.get("file", "")):
                    return self._send(400, {"error": "tên file không hợp lệ"})
                rid = JOBS.start(b["file"], b.get("ids") or [], s)
                return self._send(200, {"run_id": rid})
            if u.path == "/api/stop":
                JOBS.stop()
                return self._send(200, {"ok": True})
            if u.path == "/api/upload":
                name = parse_qs(u.query).get("name", [""])[0]
                if not SAFE.match(name) or Path(name).suffix.lower() not in (".csv", ".xlsx", ".json"):
                    return self._send(400, {"error": "Chỉ nhận file .csv/.xlsx/.json với tên hợp lệ"})
                n = int(self.headers.get("Content-Length") or 0)
                dest = config.TESTCASE_DIR / name
                dest.write_bytes(self.rfile.read(n))
                try:
                    errs = testcases.validate(testcases.load(dest))
                except Exception as e:
                    dest.unlink(missing_ok=True)
                    return self._send(400, {"error": f"File không đọc được: {e}"})
                return self._send(200, {"name": name, "errors": errs})
            self._send(404, {"error": "not found"})
        except (RuntimeError, ValueError) as e:
            self._send(400, {"error": str(e)})
        except Exception as e:
            self._send(500, {"error": str(e)})


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"Khan Academy AutoTest GUI: http://{host}:{port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        JOBS.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
