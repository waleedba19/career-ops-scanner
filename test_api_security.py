"""Phase 2 API security + behavior tests.

Covers:
  2a. /api/apply requires the API key (when CAREEROPS_API_KEY is set),
      validates url scheme and status whitelist.
  2b. /api/metrics renders from the persisted metrics.json snapshot.
      /api/ready returns 503 on stale/no data, 200 on fresh data.

Uses FastAPI TestClient when available; skips cleanly otherwise.
Run:  python -m unittest test_api_security -v
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import api_server

try:
    from fastapi.testclient import TestClient
    _HAS_FASTAPI = hasattr(api_server, "app")
except Exception:
    _HAS_FASTAPI = False

FRESH = {
    "status": "healthy", "health_score": 90, "total_fetched": 1200,
    "total_matches": 42, "total_errors": 0, "sources_up": 10,
    "generated_at": "2999-01-01T00:00:00+00:00",  # far future => always fresh
}
STALE = {**FRESH, "generated_at": "2000-01-01T00:00:00+00:00"}


@unittest.skipUnless(_HAS_FASTAPI, "FastAPI not importable")
class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)
        os.environ["CAREEROPS_API_KEY"] = "test-secret-key"
        api_server.API_KEY = "test-secret-key"
        # Point output/state at a temp dir with controlled health/metrics data.
        self._tmp = Path(tempfile.mkdtemp(prefix="co_api_"))
        self._orig_out = api_server.OUTPUT_DIR
        self._orig_state = api_server.STATE_DIR
        api_server.OUTPUT_DIR = self._tmp
        api_server.STATE_DIR = self._tmp
        (self._tmp / "health.json").write_text(json.dumps(FRESH))
        self.addCleanup(self._restore)

    def _restore(self):
        os.environ.clear()
        os.environ.update(self._env)
        api_server.API_KEY = os.environ.get("CAREEROPS_API_KEY", "")
        api_server.OUTPUT_DIR = self._orig_out
        api_server.STATE_DIR = self._orig_state
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _client(self):
        return TestClient(api_server.app)

    # --- 2a: write endpoint auth + validation ---
    def test_apply_rejected_without_key(self):
        r = self._client().post("/api/apply", json={"url": "https://x.co/j/1", "status": "Applied"})
        self.assertEqual(r.status_code, 401)

    def test_apply_rejected_with_wrong_key(self):
        r = self._client().post("/api/apply", json={"url": "https://x.co/j/1"},
                                headers={"X-API-Key": "wrong"})
        self.assertEqual(r.status_code, 401)

    def test_apply_rejects_bad_url_and_status_with_key(self):
        c = self._client()
        h = {"X-API-Key": "test-secret-key"}
        self.assertEqual(c.post("/api/apply", json={"url": "ftp://bad"}, headers=h).status_code, 400)
        self.assertEqual(c.post("/api/apply", json={"url": "https://x.co/1", "status": "Hacked"}, headers=h).status_code, 400)

    def test_reads_require_key_when_set(self):
        self.assertEqual(self._client().get("/api/health").status_code, 401)
        self.assertEqual(self._client().get("/api/health", headers={"X-API-Key": "test-secret-key"}).status_code, 200)

    # --- 2b: readiness reflects scan freshness ---
    def test_ready_fresh(self):
        r = self._client().get("/api/ready", headers={"X-API-Key": "test-secret-key"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ready"])

    def test_ready_stale(self):
        (self._tmp / "health.json").write_text(json.dumps(STALE))
        r = self._client().get("/api/ready", headers={"X-API-Key": "test-secret-key"})
        self.assertEqual(r.status_code, 503)
        self.assertFalse(r.json()["ready"])

    # --- 2b: metrics read from disk snapshot ---
    def test_metrics_from_disk(self):
        import metrics
        orig = metrics.METRICS_FILE
        metrics.METRICS_FILE = self._tmp / "metrics.json"
        metrics.METRICS_FILE.write_text(json.dumps({"health": FRESH, "run": {}}))
        try:
            r = self._client().get("/api/metrics", headers={"X-API-Key": "test-secret-key"})
            self.assertEqual(r.status_code, 200)
            self.assertIn("careerops_fetched_total 1200", r.text)
            self.assertIn("careerops_matches_total 42", r.text)
        finally:
            metrics.METRICS_FILE = orig


class HelperTests(unittest.TestCase):
    """Auth helper semantics (no FastAPI needed)."""

    def test_no_key_configured_is_open(self):
        orig = api_server.API_KEY
        api_server.API_KEY = ""
        try:
            self.assertTrue(api_server._authorized({}, ""))
        finally:
            api_server.API_KEY = orig

    def test_constant_eq(self):
        self.assertTrue(api_server._constant_eq("abc", "abc"))
        self.assertFalse(api_server._constant_eq("abc", "abd"))
        self.assertFalse(api_server._constant_eq("abc", "abcd"))


if __name__ == "__main__":
    unittest.main()
