"""
CareerOps API Server — FastAPI (if available) else stdlib http.server fallback
Endpoints:
  GET /api/health          — system health
  GET /api/metrics         — Prometheus text
  GET /api/jobs            — fresh_matches_history (query: limit, category, min_score)
  GET /api/stats           — evolution + source performance
  GET /api/scan/history    — scan_history_acum
  POST /api/apply          — mark applied {url, status}
  GET /dashboard or /      — redirect to dashboard
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent
STATE_DIR = ROOT / "state"
OUTPUT_DIR = ROOT / "output"

# Auth: if CAREEROPS_API_KEY is set, ALL endpoints require it (the data is
# personal job-search data). Writes additionally require the key. If unset we
# stay open but bind loopback-only by default (see __main__) — never expose an
# unauthenticated instance on a public interface.
API_KEY = os.getenv("CAREEROPS_API_KEY", "")
ALLOWED_STATUS = {"Applied", "Maybe", "Rejected", "Interview", "Offer"}


def _constant_eq(a: str, b: str) -> bool:
    """Constant-time compare to avoid timing attacks on the API key."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode("utf-8"), b.encode("utf-8")):
        result |= x ^ y
    return result == 0


def _extract_key(headers, payload_key: str = "") -> str:
    """Pull the key from X-API-Key header, Authorization: Bearer, or payload."""
    auth = headers.get("authorization", "") if headers else ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    if headers and headers.get("x-api-key"):
        return headers.get("x-api-key").strip()
    return (payload_key or "").strip()


def _authorized(headers, payload_key: str = "") -> bool:
    """True if no key is configured (open local mode) or the presented key matches."""
    if not API_KEY:
        return True
    return _constant_eq(_extract_key(headers, payload_key), API_KEY)

def _load_json(p: Path, fallback):
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except: pass
    return fallback

def health_payload():
    p = OUTPUT_DIR / "health.json"
    if p.exists():
        try: return json.loads(p.read_text())
        except: pass
    return {"status":"unknown","health_score":0}

# ── Try FastAPI ──────────────────────────────────────────────────────────
try:
    from fastapi import FastAPI, Query, Request
    from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    app = FastAPI(title="CareerOps API", version="2.0")

    def _unauthorized():
        return JSONResponse({"error": "unauthorized — set X-API-Key header"}, status_code=401)

    @app.get("/api/health")
    def api_health(request: Request):
        if not _authorized(request.headers):
            return _unauthorized()
        return health_payload()

    @app.get("/api/ready")
    def api_ready(request: Request):
        """Readiness: 200 only if a scan produced fresh data recently.

        Liveness (/api/health) only proves the HTTP server is up. This proves the
        scanner actually ran and wrote state within the staleness window.
        """
        if not _authorized(request.headers):
            return _unauthorized()
        hp = health_payload()
        generated = hp.get("generated_at", "")
        stale_after_h = float(os.getenv("CAREEROPS_SCAN_STALE_H", "30"))
        try:
            from datetime import datetime, timezone
            age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(generated.replace("Z", "+00:00"))).total_seconds() / 3600
        except Exception:
            age_h = None
        if age_h is None:
            return JSONResponse({"ready": False, "reason": "no scan data"}, status_code=503)
        if age_h > stale_after_h:
            return JSONResponse({"ready": False, "reason": f"scan data stale ({age_h:.1f}h old)", "age_hours": round(age_h, 1)}, status_code=503)
        return {"ready": True, "age_hours": round(age_h, 1), "status": hp.get("status")}

    @app.get("/api/metrics")
    def api_metrics(request: Request):
        if not _authorized(request.headers):
            return _unauthorized()
        from metrics import metrics_text_from_disk
        return PlainTextResponse(metrics_text_from_disk(), media_type="text/plain")

    @app.get("/api/jobs")
    def api_jobs(request: Request, limit: int = Query(50, ge=1, le=200), min_score: int = Query(0, ge=0, le=100), category: str = Query(None)):
        if not _authorized(request.headers):
            return _unauthorized()
        data = _load_json(STATE_DIR / "fresh_matches_history.json", _load_json(OUTPUT_DIR / "fresh_matches_history.json", []))
        if category:
            data = [j for j in data if j.get("category","").lower()==category.lower()]
        if min_score:
            data = [j for j in data if j.get("score",0) >= min_score]
        return {"total": len(data), "jobs": data[:limit]}

    @app.get("/api/stats")
    def api_stats(request: Request):
        if not _authorized(request.headers):
            return _unauthorized()
        evo = _load_json(STATE_DIR / "evolution_brain.json", {})
        src = _load_json(STATE_DIR / "source_performance.json", {})
        return {"evolution": evo, "sources": src, "health": health_payload()}

    @app.get("/api/scan/history")
    def api_scan_history(request: Request, limit: int = 20):
        if not _authorized(request.headers):
            return _unauthorized()
        hist = _load_json(STATE_DIR / "scan_history_acum.json", [])
        return {"total": len(hist), "history": hist[-limit:]}

    @app.post("/api/apply")
    def api_apply(payload: dict, request: Request):
        if not _authorized(request.headers, payload.get("api_key", "")):
            return JSONResponse({"error": "unauthorized — valid API key required"}, status_code=401)
        url = payload.get("url", "")
        status = payload.get("status", "Applied")
        if not url:
            return JSONResponse({"error": "url required"}, status_code=400)
        if not url.startswith(("http://", "https://")):
            return JSONResponse({"error": "invalid url"}, status_code=400)
        if status not in ALLOWED_STATUS:
            return JSONResponse({"error": f"invalid status — allowed: {sorted(ALLOWED_STATUS)}"}, status_code=400)
        try:
            from excel_generator import mark_applied
            mark_applied(url, status)
            return {"ok": True}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/")
    def root():
        return RedirectResponse("/dashboard/")

    # mount dashboard static if exists
    if (ROOT / "dashboard" / "static").exists():
        app.mount("/dashboard/static", StaticFiles(directory=str(ROOT / "dashboard" / "static")), name="dash-static")

    def run(host="127.0.0.1", port=8001):
        uvicorn.run(app, host=host, port=port, log_level="info")

except ImportError:
    # ── Fallback: stdlib server ──────────────────────────────────────────
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import urllib.parse

    class Handler(BaseHTTPRequestHandler):
        def _authed(self, payload_key: str = "") -> bool:
            return _authorized(self.headers, payload_key)

        def _deny(self):
            self.send_json({"error": "unauthorized — set X-API-Key header"}, 401)

        def do_GET(self):
            parsed = urlparse(self.path)
            if not self._authed():
                self._deny(); return
            if parsed.path in ("/api/health","/health"):
                self.send_json(health_payload())
            elif parsed.path in ("/api/ready", "/ready"):
                hp = health_payload()
                generated = hp.get("generated_at", "")
                stale_after_h = float(os.getenv("CAREEROPS_SCAN_STALE_H", "30"))
                try:
                    from datetime import datetime, timezone
                    age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(generated.replace("Z", "+00:00"))).total_seconds() / 3600
                except Exception:
                    age_h = None
                if age_h is None:
                    self.send_json({"ready": False, "reason": "no scan data"}, 503)
                elif age_h > stale_after_h:
                    self.send_json({"ready": False, "reason": "scan data stale", "age_hours": round(age_h, 1)}, 503)
                else:
                    self.send_json({"ready": True, "age_hours": round(age_h, 1), "status": hp.get("status")})
            elif parsed.path == "/api/metrics":
                try:
                    from metrics import metrics_text_from_disk
                    txt = metrics_text_from_disk()
                except: txt = "careerops_health_score 0\n"
                self.send_text(txt, "text/plain")
            elif parsed.path == "/api/jobs":
                qs = parse_qs(parsed.query)
                limit = int(qs.get("limit",["50"])[0]); min_score=int(qs.get("min_score",["0"])[0]); cat=qs.get("category",[None])[0]
                data = _load_json(STATE_DIR / "fresh_matches_history.json", _load_json(OUTPUT_DIR / "fresh_matches_history.json", []))
                if cat: data=[j for j in data if j.get("category","").lower()==cat.lower()]
                if min_score: data=[j for j in data if j.get("score",0)>=min_score]
                self.send_json({"total":len(data),"jobs":data[:limit]})
            elif parsed.path == "/api/stats":
                evo=_load_json(STATE_DIR/"evolution_brain.json",{}); src=_load_json(STATE_DIR/"source_performance.json",{})
                self.send_json({"evolution":evo,"sources":src,"health":health_payload()})
            elif parsed.path == "/":
                self.send_response(302); self.send_header("Location","/dashboard/"); self.end_headers()
            else:
                self.send_response(404); self.end_headers(); self.wfile.write(b'{"error":"not found"}')

        def do_POST(self):
            parsed=urlparse(self.path)
            if parsed.path=="/api/apply":
                length=int(self.headers.get("Content-Length",0)); body=self.rfile.read(length) if length else b'{}'
                try: payload=json.loads(body)
                except: payload={}
                if not self._authed(payload.get("api_key", "")):
                    self._deny(); return
                url=payload.get("url",""); status=payload.get("status","Applied")
                if not url: self.send_json({"error":"url required"},400); return
                if not url.startswith(("http://","https://")): self.send_json({"error":"invalid url"},400); return
                if status not in ALLOWED_STATUS: self.send_json({"error":"invalid status"},400); return
                try:
                    from excel_generator import mark_applied
                    mark_applied(url,status); self.send_json({"ok":True})
                except Exception as e: self.send_json({"error":str(e)},500)
            else: self.send_response(404); self.end_headers()

        def send_json(self, obj, code=200):
            b=json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
        def send_text(self, txt, ctype="text/plain", code=200):
            b=txt.encode(); self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
        def log_message(self, fmt,*a): print(fmt% a)

    def run(host="127.0.0.1", port=8001):
        print(f"CareerOps API (stdlib) on http://{host}:{port}")
        HTTPServer((host,port), Handler).serve_forever()

if __name__ == "__main__":
    import os
    # Loopback-only by default. Set CAREEROPS_API_HOST=0.0.0.0 AND
    # CAREEROPS_API_KEY together to expose it (compose binds 127.0.0.1 anyway).
    run(host=os.getenv("CAREEROPS_API_HOST","127.0.0.1"), port=int(os.getenv("CAREEROPS_API_PORT","8001")))
