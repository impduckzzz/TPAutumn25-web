from pathlib import Path
import time

BASE = Path(__file__).resolve().parents[1]
STATIC = BASE / "static"

def application(environ, start_response):
    path = (environ.get("PATH_INFO") or "/").lstrip("/")
    if path == "" or path == "dynamic":
        payload = (str(time.time()) + "\n").encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(payload)))])
        return [payload]
    file_path = STATIC / path
    if file_path.is_file():
        data = file_path.read_bytes()
        start_response("200 OK", [("Content-Type", "application/octet-stream"), ("Content-Length", str(len(data)))])
        return [data]
    payload = b"not found\n"
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(payload)))])
    return [payload]
