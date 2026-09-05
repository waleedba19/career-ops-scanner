"""CareerOps Dashboard — standalone, no heavy deps, serves UI + API"""
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent.parent
STATE_DIR = ROOT / "state"
OUTPUT_DIR = ROOT / "output"

TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

def load_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback

def health_payload():
    # Prefer output/health.json (fresh from last scan), fallback to computed
    p = OUTPUT_DIR / "health.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except:
            pass
    # Fallback: compute from state
    try:
        evo = load_json(STATE_DIR / "evolution_brain.json", {})
        return {
            "status": "unknown",
            "health_score": 0,
            "total_fetched": evo.get("total_jobs_scanned", 0),
            "total_matches": evo.get("total_matches", 0),
            "sources_up": 0,
            "sources_total": 0,
            "tier_cap": 2,
            "generated_at": "",
        }
    except:
        return {"status": "unknown", "health_score": 0}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Dashboard
        if path in ("/", "/dashboard", "/dashboard/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TEMPLATE.encode())
            return

        # Health
        if path in ("/api/health", "/health"):
            self.send_json(health_payload())
            return

        # Metrics (Prometheus)
        if path in ("/api/metrics", "/metrics"):
            try:
                from metrics import prometheus_text
                txt = prometheus_text()
            except Exception:
                h = health_payload()
                txt = f"careerops_health_score {h.get('health_score',0)}\n"
            self.send_text(txt, "text/plain; version=0.0.4")
            return

        # Jobs
        if path == "/api/jobs":
            limit = int(qs.get("limit", ["50"])[0])
            min_score = int(qs.get("min_score", ["0"])[0])
            category = qs.get("category", [None])[0]
            data = load_json(STATE_DIR / "fresh_matches_history.json", load_json(OUTPUT_DIR / "fresh_matches_history.json", []))
            if category:
                data = [j for j in data if j.get("category","").lower() == category.lower()]
            if min_score:
                data = [j for j in data if j.get("score",0) >= min_score]
            # Sort by score desc
            try:
                data = sorted(data, key=lambda x: x.get("score",0), reverse=True)
            except:
                pass
            self.send_json({"total": len(data), "jobs": data[:limit]})
            return

        # Stats
        if path == "/api/stats":
            evo = load_json(STATE_DIR / "evolution_brain.json", load_json(OUTPUT_DIR / "evolution_brain.json", {}))
            src = load_json(STATE_DIR / "source_performance.json", load_json(OUTPUT_DIR / "source_performance.json", {}))
            self.send_json({"evolution": evo, "sources": src, "health": health_payload()})
            return

        # Scan history
        if path == "/api/scan/history":
            limit = int(qs.get("limit", ["20"])[0])
            hist = load_json(STATE_DIR / "scan_history_acum.json", load_json(OUTPUT_DIR / "scan_history_acum.json", []))
            if isinstance(hist, dict):
                hist = hist.get("history", [])
            self.send_json({"total": len(hist), "history": hist[-limit:]})
            return

        # Fallback
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/apply":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(body)
            except:
                payload = {}
            url = payload.get("url", "")
            status = payload.get("status", "Applied")
            if not url:
                self.send_json({"error": "url required"}, 400)
                return
            try:
                from excel_generator import mark_applied
                mark_applied(url, status)
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return
        self.send_response(404)
        self.end_headers()

    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def send_text(self, txt, ctype="text/plain", code=200):
        b = txt.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, fmt, *a):
        print(fmt % a)

def run(host="0.0.0.0", port=8000):
    print(f"✅ CareerOps Dashboard live → http://{host}:{port}  (API + UI)")
    print(f"   Health: http://{host}:{port}/api/health   Metrics: http://{host}:{port}/api/metrics")
    HTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    import os
    run(host=os.getenv("CAREEROPS_DASH_HOST", "0.0.0.0"), port=int(os.getenv("CAREEROPS_DASH_PORT", "8000")))
