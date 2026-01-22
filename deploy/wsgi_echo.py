from urllib.parse import parse_qs
import io

def _read_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length <= 0:
        return b""
    return environ["wsgi.input"].read(length)

def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    qs = environ.get("QUERY_STRING", "")
    get_params = {k: v for k, v in parse_qs(qs, keep_blank_values=True).items()}
    post_params = {}
    body = b""
    if method == "POST":
        body = _read_body(environ)
        ctype = (environ.get("CONTENT_TYPE") or "").split(";", 1)[0].strip().lower()
        if ctype in ("application/x-www-form-urlencoded", ""):
            try:
                post_params = {k: v for k, v in parse_qs(body.decode("utf-8", "replace"), keep_blank_values=True).items()}
            except Exception:
                post_params = {}
    out = []
    out.append(f"method={method}")
    out.append("get=" + str(get_params))
    out.append("post=" + str(post_params))
    out.append("body_bytes=" + str(len(body)))
    payload = ("\n".join(out) + "\n").encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(payload)))])
    return [payload]
