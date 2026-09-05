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
    from fastapi import FastAPI, Query
    from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    app = FastAPI(title="CareerOps API", version="2.0")

    @app.get("/api/health")
    def api_health():
        return health_payload()

    @app.get("/api/metrics")
    def api_metrics():
        from metrics import prometheus_text
        return PlainTextResponse(prometheus_text(), media_type="text/plain")

    @app.get("/api/jobs")
    def api_jobs(limit: int = Query(50, ge=1, le=200), min_score: int = Query(0, ge=0, le=100), category: str = Query(None)):
        data = _load_json(STATE_DIR / "fresh_matches_history.json", _load_json(OUTPUT_DIR / "fresh_matches_history.json", []))
        if category:
            data = [j for j in data if j.get("category","").lower()==category.lower()]
        if min_score:
            data = [j for j in data if j.get("score",0) >= min_score]
        return {"total": len(data), "jobs": data[:limit]}

    @app.get("/api/stats")
    def api_stats():
        evo = _load_json(STATE_DIR / "evolution_brain.json", {})
        src = _load_json(STATE_DIR / "source_performance.json", {})
        return {"evolution": evo, "sources": src, "health": health_payload()}

    @app.get("/api/scan/history")
    def api_scan_history(limit: int = 20):
        hist = _load_json(STATE_DIR / "scan_history_acum.json", [])
        return {"total": len(hist), "history": hist[-limit:]}

    @app.post("/api/apply")
    def api_apply(payload: dict):
        url = payload.get("url",""); status = payload.get("status","Applied")
        if not url: return JSONResponse({"error":"url required"}, status_code=400)
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

    def run(host="0.0.0.0", port=8001):
        uvicorn.run(app, host=host, port=port, log_level="info")

except ImportError:
    # ── Fallback: stdlib server ──────────────────────────────────────────
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import urllib.parse

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/api/health","/health"):
                self.send_json(health_payload())
            elif parsed.path == "/api/metrics":
                try:
                    from metrics import prometheus_text
                    txt = prometheus_text()
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
                url=payload.get("url",""); status=payload.get("status","Applied")
                if not url: self.send_json({"error":"url required"},400); return
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

    def run(host="0.0.0.0", port=8001):
        print(f"CareerOps API (stdlib) on http://{host}:{port}")
        HTTPServer((host,port), Handler).serve_forever()

if __name__ == "__main__":
    import os
    run(host=os.getenv("CAREEROPS_API_HOST","0.0.0.0"), port=int(os.getenv("CAREEROPS_API_PORT","8001")))
