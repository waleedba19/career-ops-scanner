"""Regression tests for state_sync reliability fixes (Phase 1).

  1a. >1 MiB state files restored as EMPTY bytes (Contents API omits content).
  1b. download/upload failures exited 0 (silent green) — now exit nonzero.

Network is mocked; no credentials needed. Run: python -m unittest test_state_sync -v
"""

import base64
import json
import os
import runpy
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import state_sync


def _resp(payload: dict):
    m = mock.MagicMock()
    m.read.return_value = json.dumps(payload).encode("utf-8")
    m.status = 200
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


def _resp_bytes(data: bytes):
    m = mock.MagicMock()
    m.read.return_value = data
    m.status = 200
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


def _http_404():
    return urllib.error.HTTPError("u", 404, "Not Found", {}, None)


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)
        os.environ["GITHUB_ACTIONS"] = "true"
        os.environ["GITHUB_TOKEN"] = "test-token"
        os.environ["GITHUB_REPOSITORY"] = "owner/repo"
        self._orig_files = state_sync.STATE_FILES
        self._orig_out = state_sync.OUTPUT_DIR
        self._tmp = Path("test_state_sync_tmp")
        self._tmp.mkdir(parents=True, exist_ok=True)
        state_sync.OUTPUT_DIR = self._tmp
        self.addCleanup(self._restore)

    def _restore(self):
        os.environ.clear()
        os.environ.update(self._env)
        state_sync.STATE_FILES = self._orig_files
        state_sync.OUTPUT_DIR = self._orig_out
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_large_file_restored_via_download_url(self):
        """1a: a >1 MiB file must restore intact via download_url, not empty."""
        big = json.dumps({"seen": ["x" * 100] * 30000}).encode("utf-8")
        self.assertGreater(len(big), 1_000_000)
        state_sync.STATE_FILES = ["smart_seen.json"]

        def fake_urlopen(req, timeout=0):
            url = getattr(req, "full_url", req)
            if "contents/state/" in url:
                return _resp({"encoding": "none", "content": "",
                              "download_url": "https://raw.example/smart_seen.json"})
            return _resp_bytes(big)

        with mock.patch.object(state_sync.urllib.request, "urlopen", side_effect=fake_urlopen):
            restored = state_sync.download_state()

        dest = self._tmp / "smart_seen.json"
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_bytes(), big, "large file must restore byte-for-byte")
        self.assertGreater(dest.stat().st_size, 1_000_000)
        self.assertEqual(restored, 1)


    def test_download_never_clobbers_good_state_with_empty(self):
        """1a: empty content + no download_url -> keep local, report failure."""
        good = json.dumps({"a": 1}).encode("utf-8")
        dest = self._tmp / "smart_seen.json"
        dest.write_bytes(good)
        state_sync.STATE_FILES = ["smart_seen.json"]

        def fake_urlopen(req, timeout=0):
            return _resp({"encoding": "base64", "content": ""})  # empty, no download_url

        with mock.patch.object(state_sync.urllib.request, "urlopen", side_effect=fake_urlopen):
            restored = state_sync.download_state()

        self.assertEqual(dest.read_bytes(), good, "must not overwrite good local state with empty")
        self.assertEqual(restored, -1, "hard failure must be reported")

    def test_missing_remote_file_is_not_a_failure(self):
        """First-run 404 is tolerated, not a failure."""
        state_sync.STATE_FILES = ["smart_seen.json"]
        with mock.patch.object(state_sync.urllib.request, "urlopen", side_effect=_http_404()):
            restored = state_sync.download_state()
        self.assertEqual(restored, 0)

    def test_corrupt_content_fails_and_preserves_local(self):
        """1b: invalid JSON from remote fails loudly, leaves local intact."""
        good = json.dumps({"keep": True}).encode("utf-8")
        dest = self._tmp / "smart_seen.json"
        dest.write_bytes(good)
        state_sync.STATE_FILES = ["smart_seen.json"]
        bad = base64.b64encode(b"not json {{{").decode("ascii")

        def fake_urlopen(req, timeout=0):
            return _resp({"encoding": "base64", "content": bad})

        with mock.patch.object(state_sync.urllib.request, "urlopen", side_effect=fake_urlopen):
            restored = state_sync.download_state()

        self.assertEqual(restored, -1)
        self.assertEqual(dest.read_bytes(), good)


class ExitCodeTests(unittest.TestCase):
    """1b: __main__ must exit nonzero on failure (was always 0)."""

    def setUp(self):
        self._env = dict(os.environ)
        os.environ["GITHUB_ACTIONS"] = "true"
        os.environ["GITHUB_TOKEN"] = "t"
        os.environ["GITHUB_REPOSITORY"] = "o/r"
        self._orig_out = state_sync.OUTPUT_DIR
        self.addCleanup(self._restore)

    def _restore(self):
        os.environ.clear()
        os.environ.update(self._env)
        state_sync.OUTPUT_DIR = self._orig_out

    def _run_main(self, argv, urlopen_side_effect):
        # Patch urlopen (not download_state) so runpy's fresh exec of __main__
        # still uses our mock; drive success/failure via the network layer.
        with mock.patch.object(state_sync.urllib.request, "urlopen",
                               side_effect=urlopen_side_effect), \
             mock.patch.object(sys, "argv", ["state_sync.py", argv]):
            with self.assertRaises(SystemExit) as cm:
                runpy.run_path(str(Path(state_sync.__file__)), run_name="__main__")
            return cm.exception.code

    def test_download_success_exits_0(self):
        # All 13 state files 404 (first run) -> tolerated -> exit 0.
        self.assertEqual(self._run_main("download", _http_404()), 0)

    def test_download_failure_exits_1(self):
        # A non-404 error (401) is a hard failure -> exit 1.
        err = urllib.error.HTTPError("u", 401, "Unauthorized", {}, None)
        self.assertEqual(self._run_main("download", err), 1)

    def test_upload_failure_exits_1(self):
        # runpy re-execs the module, resetting OUTPUT_DIR to <repo>/output — so
        # write the fixture there. A 500 on every PUT -> upload_state -1 -> exit 1.
        out = Path(state_sync.__file__).parent / "output"
        out.mkdir(exist_ok=True)
        probe = out / "smart_seen.json"
        created = not probe.exists()
        probe.write_text("{}")
        err = urllib.error.HTTPError("u", 500, "Server Error", {}, None)
        try:
            self.assertEqual(self._run_main("upload", err), 1)
        finally:
            if created:
                probe.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
