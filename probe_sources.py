#!/usr/bin/env python3
"""
probe_sources.py — find out which candidate job sources actually work *from here*.

Reads source_candidates.json, hits every candidate once (concurrently, politely),
classifies the response, and writes:

    output/source_probe.json   machine-readable results
    output/source_probe.md     human report (+ ready-to-paste config snippets)

Status classes
    ok          responded with >=1 parseable job / item
    empty       responded 200 but nothing parseable (wrong parser, or genuinely no jobs)
    blocked     403 / 429 / 999 / captcha or challenge page  → do not scrape from this IP
    not_found   404 / 410 (slug or endpoint is wrong)
    needs_key   candidate needs a secret that is not in the environment
    error       DNS / TLS / timeout / other transport error

Usage
    python probe_sources.py                          # everything
    python probe_sources.py --group aggregator-keyed --group linkedin
    python probe_sources.py --only greenhouse:agency,ashby:deel
    python probe_sources.py --concurrency 6 --timeout 15

Never raises; exit code is 0 unless --fail-on-empty is given and nothing at all worked.
Designed to run both locally and in the "Probe Sources" GitHub Actions workflow —
the runner's datacenter IP is what production sees, so that is the result that matters.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import aiohttp
except ImportError:  # pragma: no cover
    print("aiohttp missing: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent
CANDIDATES = ROOT / "source_candidates.json"
OUT_DIR = ROOT / "output"
OUT_JSON = OUT_DIR / "source_probe.json"
OUT_MD = OUT_DIR / "source_probe.md"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.6",
}

BLOCK_MARKERS = (
    "captcha", "cf-browser-verification", "just a moment", "access denied", "verify you are human",
    "challenge-platform", "px-captcha", "are you a human", "unusual traffic", "authwall",
    "request blocked", "attention required", "enable javascript and cookies to continue",
    "/sorry/index", "bot detection", "datadome",
)

PLACEHOLDER_RE = re.compile(r"\{([A-Z][A-Z0-9_]+)\}")


# ────────────────────────────────────────────────────────────────────────────
# Item counters — one small extractor per adapter. They only need to answer
# "how many job-like things came back?", not fully normalize jobs.
# ────────────────────────────────────────────────────────────────────────────

def _json(body: str):
    try:
        return json.loads(body)
    except Exception:
        return None


def _first_list(d, keys):
    if isinstance(d, list):
        return d
    if isinstance(d, dict):
        for k in keys:
            v = d.get(k)
            if isinstance(v, list):
                return v
            if isinstance(v, dict):
                inner = _first_list(v, keys)
                if inner:
                    return inner
    return []


def count_items(adapter: str, body: str, content_type: str) -> tuple[int, list[str]]:
    """Return (count, sample_titles)."""
    b = body or ""
    ct = (content_type or "").lower()
    titles: list[str] = []

    if adapter in ("greenhouse",):
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "lever":
        d = _json(b)
        jobs = d if isinstance(d, list) else []
        titles = [j.get("text", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "ashby":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "workable":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "smartrecruiters":
        d = _json(b)
        jobs = _first_list(d, ["content"])
        titles = [j.get("name", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "recruitee":
        d = _json(b)
        jobs = _first_list(d, ["offers"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter in ("remotive",):
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "jobicy":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("jobTitle", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "remoteok":
        d = _json(b)
        jobs = [j for j in (d or []) if isinstance(j, dict) and j.get("position")] if isinstance(d, list) else []
        titles = [j.get("position", "") for j in jobs]
    elif adapter == "himalayas":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "arbeitnow":
        d = _json(b)
        jobs = _first_list(d, ["data"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "jsearch":
        d = _json(b)
        jobs = _first_list(d, ["data"])
        titles = [j.get("job_title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "adzuna":
        d = _json(b)
        jobs = _first_list(d, ["results"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "jooble":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "careerjet":
        d = _json(b)
        jobs = _first_list(d, ["jobs"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "reliefweb":
        d = _json(b)
        jobs = _first_list(d, ["data"])
        titles = [(j.get("fields") or {}).get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "freelancer_api":
        d = _json(b)
        jobs = _first_list(d, ["result", "projects"])
        titles = [j.get("title", "") for j in jobs if isinstance(j, dict)]
    elif adapter == "linkedin_guest":
        # guest endpoint returns an HTML fragment of <li> cards
        titles = [re.sub(r"\s+", " ", t).strip() for t in re.findall(
            r'class="base-search-card__title[^"]*"[^>]*>([\s\S]*?)</h3>', b, re.I)]
        if not titles:
            titles = re.findall(r'<a[^>]+class="base-card__full-link"[^>]*>\s*<span[^>]*>([\s\S]*?)</span>', b, re.I)
            titles = [re.sub(r"\s+", " ", t).strip() for t in titles]
    elif adapter in ("rss", "teamtailor_rss"):
        items = re.findall(r"<item>[\s\S]*?</item>", b)
        for it in items:
            m = re.search(r"<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?</title>", it)
            titles.append((m.group(1) if m else "").strip())
        if not items:  # Atom
            titles = re.findall(r"<entry>[\s\S]*?<title[^>]*>([\s\S]*?)</title>", b)
    elif adapter == "personio_xml":
        titles = re.findall(r"<position>[\s\S]*?<name>([\s\S]*?)</name>", b)
    elif adapter == "json_jobs":
        d = _json(b)
        jobs = _first_list(d, ["jobs", "results", "data", "postings", "offers", "items"])
        titles = [(j.get("title") or j.get("name") or j.get("jobTitle") or "") for j in jobs if isinstance(j, dict)]
    else:  # html — look for JSON-LD JobPosting first, then job-ish anchors
        ld = re.findall(r'"@type"\s*:\s*"JobPosting"', b)
        if ld:
            titles = re.findall(r'"@type"\s*:\s*"JobPosting"[\s\S]{0,400}?"title"\s*:\s*"([^"]{3,120})"', b)
            if not titles:
                titles = ["JobPosting"] * len(ld)
        else:
            anchors = re.findall(r'<a[^>]+href="[^"]*(?:/job|/jobs/|/careers/|/position|/vacan|/opening|/projects/|/offers/)[^"]*"[^>]*>([\s\S]*?)</a>', b, re.I)
            titles = [re.sub(r"<[^>]+>", "", a).strip() for a in anchors]
            titles = [t for t in titles if 4 <= len(t) <= 120]

    titles = [t for t in titles if t]
    return len(titles), titles[:3]


# ────────────────────────────────────────────────────────────────────────────
# Probe
# ────────────────────────────────────────────────────────────────────────────

def fill_placeholders(s: str, env: dict) -> tuple[str, list[str]]:
    missing = []

    def rep(m):
        k = m.group(1)
        v = env.get(k, "")
        if not v:
            missing.append(k)
        return v

    return PLACEHOLDER_RE.sub(rep, s), missing


async def probe_one(session: aiohttp.ClientSession, cand: dict, env: dict, timeout: int, sem: asyncio.Semaphore) -> dict:
    res = {
        "id": cand["id"], "name": cand["name"], "group": cand["group"], "adapter": cand["adapter"],
        "confidence": cand.get("confidence", "guess"), "suggested_tier": cand.get("suggested_tier", 2),
        "status": "", "http": 0, "latency_ms": 0, "items": 0, "sample": [], "detail": "",
    }
    needs = list(cand.get("needs_key") or [])
    url, missing = fill_placeholders(cand["url"], env)
    hdrs = dict(HEADERS)
    for k, v in (cand.get("headers") or {}).items():
        v2, miss2 = fill_placeholders(v, env)
        hdrs[k] = v2
        missing += miss2
    missing = sorted(set(missing) | {k for k in needs if not env.get(k)})
    if missing:
        res.update(status="needs_key", detail="missing secret(s): " + ", ".join(missing))
        return res
    res["url"] = re.sub(r"(app_key|app_id|affid|appname)=([^&]+)", r"\1=***", url)

    async with sem:
        t0 = time.time()
        try:
            method = (cand.get("method") or "GET").upper()
            kwargs = dict(headers=hdrs, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True, ssl=False)
            if method == "POST":
                kwargs["json"] = cand.get("body") or {}
            async with session.request(method, url, **kwargs) as r:
                body = await r.text(errors="ignore")
                res["http"] = r.status
                res["latency_ms"] = int((time.time() - t0) * 1000)
                ct = r.headers.get("content-type", "")
                low = body[:12000].lower()
                if r.status in (403, 429, 999, 503) or any(m in low for m in BLOCK_MARKERS):
                    res.update(status="blocked", detail=f"HTTP {r.status}" + (" + challenge page" if any(m in low for m in BLOCK_MARKERS) else ""))
                    return res
                if r.status in (404, 410):
                    res.update(status="not_found", detail=f"HTTP {r.status}")
                    return res
                if r.status == 401:
                    res.update(status="needs_key", detail="HTTP 401 — key rejected or required")
                    return res
                if r.status >= 400:
                    res.update(status="error", detail=f"HTTP {r.status}")
                    return res
                n, sample = count_items(cand["adapter"], body, ct)
                res.update(items=n, sample=sample, detail=f"{len(body)} bytes, {ct.split(';')[0]}")
                res["status"] = "ok" if n > 0 else "empty"
                return res
        except asyncio.TimeoutError:
            res.update(status="error", detail=f"timeout >{timeout}s", latency_ms=int((time.time() - t0) * 1000))
        except Exception as e:  # DNS, TLS, connection reset …
            res.update(status="error", detail=f"{type(e).__name__}: {str(e)[:90]}", latency_ms=int((time.time() - t0) * 1000))
        return res


def load_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k.isupper()}
    # convenience: derive REED_API_KEY_B64 from REED_API_KEY if given
    if env.get("REED_API_KEY") and not env.get("REED_API_KEY_B64"):
        env["REED_API_KEY_B64"] = base64.b64encode((env["REED_API_KEY"] + ":").encode()).decode()
    return env


# ────────────────────────────────────────────────────────────────────────────
# Report
# ────────────────────────────────────────────────────────────────────────────

def _slug_from_id(cid: str) -> str:
    return cid.split(":", 1)[1] if ":" in cid else cid


def render_md(results: list[dict], meta: dict) -> str:
    by_status = Counter(r["status"] for r in results)
    lines = []
    lines.append(f"# Source probe — {meta['ran_at']}\n")
    lines.append(f"_Ran from: {meta['where']} · {len(results)} candidates · concurrency {meta['concurrency']} · timeout {meta['timeout']}s_\n")
    lines.append("| status | count | meaning |")
    lines.append("|---|---:|---|")
    meaning = {
        "ok": "responded with parseable jobs → **can be added**",
        "empty": "200 but nothing parsed → wrong parser or no jobs right now",
        "blocked": "403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route",
        "not_found": "404/410 → slug or endpoint is wrong",
        "needs_key": "add the secret and re-run",
        "error": "DNS/TLS/timeout",
    }
    for s in ("ok", "empty", "blocked", "not_found", "needs_key", "error"):
        if by_status.get(s):
            lines.append(f"| {s} | {by_status[s]} | {meaning[s]} |")
    lines.append("")

    ok = [r for r in results if r["status"] == "ok"]
    ok_new = [r for r in ok if r["group"] != "baseline"]
    lines.append(f"## Answer: **{len(ok_new)} new sources responded with jobs** (+{len([r for r in ok if r['group']=='baseline'])} baseline references)\n")

    groups = defaultdict(list)
    for r in results:
        groups[r["group"]].append(r)
    order = ["baseline", "precision-queries", "aggregator-keyed", "linkedin", "freelance", "ats-language-ai", "ats-lsp",
             "ats-edtech", "ats-mena", "remote-boards", "translation-boards", "esl-boards", "un-ngo", "mena-boards",
             "academic-editing-watchers", "major-platforms-blocked"]
    for g in order + [g for g in groups if g not in order]:
        if g not in groups:
            continue
        rs = sorted(groups[g], key=lambda r: ({"ok": 0, "empty": 1, "needs_key": 2, "blocked": 3, "not_found": 4, "error": 5}[r["status"]], -r["items"]))
        c = Counter(r["status"] for r in rs)
        lines.append(f"## {g}  <sub>ok {c.get('ok',0)} · empty {c.get('empty',0)} · blocked {c.get('blocked',0)} · not_found {c.get('not_found',0)} · needs_key {c.get('needs_key',0)} · error {c.get('error',0)}</sub>\n")
        lines.append("| status | id | items | http | ms | sample / detail |")
        lines.append("|---|---|---:|---:|---:|---|")
        for r in rs:
            icon = {"ok": "✅", "empty": "⚪", "blocked": "⛔", "not_found": "❓", "needs_key": "🔑", "error": "💥"}[r["status"]]
            sample = "; ".join(s[:45] for s in r["sample"]) if r["sample"] else r["detail"]
            sample = sample.replace("|", "\\|")
            lines.append(f"| {icon} {r['status']} | `{r['id']}` | {r['items']} | {r['http'] or ''} | {r['latency_ms'] or ''} | {sample[:140]} |")
        lines.append("")

    # ── ready-to-paste config ──
    lines.append("## Ready-to-paste config (only boards that answered with jobs)\n")
    for adapter, var in (("greenhouse", "GREENHOUSE_COMPANIES"), ("lever", "LEVER_COMPANIES"),
                         ("ashby", "ASHBY_COMPANIES"), ("workable", "WORKABLE_COMPANIES"),
                         ("smartrecruiters", "SMARTRECRUITERS_COMPANIES"), ("recruitee", "RECRUITEE_COMPANIES"),
                         ("teamtailor_rss", "TEAMTAILOR_COMPANIES")):
        rows = [r for r in ok if r["adapter"] == adapter and r["group"].startswith("ats")]
        if rows:
            lines.append(f"```python\n# {var} additions — {len(rows)} boards")
            for r in rows:
                nm = r["name"].split(" (")[0].split(" — ")[0].split(" via ")[0]
                lines.append(f'    ("{nm}", "{_slug_from_id(r["id"])}"),   # {r["items"]} jobs')
            lines.append("```\n")
    feeds = [r for r in ok if r["adapter"] in ("rss", "json_jobs", "teamtailor_rss") and not r["group"].startswith("ats") and r["group"] != "baseline"]
    if feeds:
        lines.append("```json\n// source_registry.json additions")
        for r in feeds:
            lines.append(json.dumps({"url": r.get("url", ""), "source_name": _slug_from_id(r["id"]), "type": "rss" if "rss" in r["adapter"] else "json"}) + ",")
        lines.append("```\n")
    keyed = [r for r in results if r["status"] == "needs_key"]
    if keyed:
        secrets = sorted({k.strip() for r in keyed for k in r["detail"].split(":")[-1].split(",")})
        lines.append("## Secrets to add for the keyed aggregators\n")
        lines.append("Settings → Secrets and variables → Actions → New repository secret: " + ", ".join(f"`{s}`" for s in secrets if s and s.isupper()) + "\n")
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

async def main_async(args) -> int:
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    cands = doc["candidates"]
    if args.group:
        cands = [c for c in cands if c["group"] in set(args.group)]
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        cands = [c for c in cands if c["id"] in wanted]
    if not cands:
        print("no candidates selected")
        return 0
    env = load_env()
    sem = asyncio.Semaphore(args.concurrency)
    conn = aiohttp.TCPConnector(ssl=False, limit=args.concurrency * 2)
    async with aiohttp.ClientSession(connector=conn) as session:
        results = await asyncio.gather(*[probe_one(session, c, env, args.timeout, sem) for c in cands])
    results = list(results)

    where = "github-actions" if os.getenv("GITHUB_ACTIONS") == "true" else "local"
    meta = {"ran_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "where": where,
            "concurrency": args.concurrency, "timeout": args.timeout}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"meta": meta, "results": results}, indent=1, ensure_ascii=False), encoding="utf-8")
    md = render_md(results, meta)
    OUT_MD.write_text(md, encoding="utf-8")

    # console summary
    c = Counter(r["status"] for r in results)
    print(f"\nProbe done: {len(results)} candidates from {where}")
    print("  " + "  ".join(f"{k}={v}" for k, v in sorted(c.items())))
    for r in sorted(results, key=lambda r: (r["status"] != "ok", -r["items"])):
        icon = {"ok": "OK ", "empty": "   ", "blocked": "BLK", "not_found": "404", "needs_key": "KEY", "error": "ERR"}[r["status"]]
        print(f"  {icon} {r['id']:<40} {r['items']:>4} items  {r['http'] or '':>3}  {r['detail'][:60]}")
    print(f"\nReport: {OUT_MD}")

    # GitHub Actions job summary
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            Path(summary).write_text(md, encoding="utf-8")
        except Exception:
            pass
    if args.fail_on_empty and not c.get("ok"):
        return 2
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--group", action="append", help="only these groups (repeatable)")
    p.add_argument("--only", help="comma-separated candidate ids")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--timeout", type=int, default=15)
    p.add_argument("--fail-on-empty", action="store_true")
    args = p.parse_args()
    sys.exit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
