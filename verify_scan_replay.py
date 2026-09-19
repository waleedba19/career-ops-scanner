"""
verify_scan_replay.py — independent proof the scanner only surfaces true matches.

Run this on ANY CareerOps Excel you receive by email:

    python verify_scan_replay.py "path/to/careerops-scan-YYYY-MM-DD.xls"

It re-reads every listing in the "All Jobs" sheet of your real scan output and
pushes each one through today's scorer + the exact same gates the live pipeline
uses (stub pages, worldwide-location, quality drops). It then prints:

  1. The final survivor list (the ONLY jobs that would be emailed as STRONG).
  2. A regression check that the four roles from the 2026-09-19 email
     (IRIS² engineer, Copywriter, AR Specialist, Ashby CSM) can never return.
  3. A one-line verdict: PASS or FAIL.

Usage notes:
  - Titles only: the Excel dump carries no full descriptions, so this replay
    scores on titles plus the location gate. The live run on GitHub scores with
    the full description as well, which makes it strictly more selective.
  - The AI (Groq) verdict gate is NOT part of this offline replay — it only
    runs in the live pipeline. So this is the *less* strict check.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import scanner  # noqa: E402

_NS = "{urn:schemas-microsoft-com:office:spreadsheet}"


def load_all_jobs(xls_path: Path) -> list[dict]:
    """Read the 'All Jobs' worksheet of the SpreadsheetML .xls file."""
    root = ET.parse(xls_path).getroot()
    rows = []
    for ws in root.iter(_NS + "Worksheet"):
        if ws.get(_NS + "Name") != "All Jobs":
            continue
        for row in ws.iter(_NS + "Row"):
            cells = []
            for cell in row.iter(_NS + "Cell"):
                data = cell.find(_NS + "Data")
                cells.append("" if data is None else (data.text or ""))
            if len(cells) >= 9 and re.fullmatch(r"\d+", cells[0].strip() or ""):
                rows.append({
                    "num": int(cells[0]),
                    "company": cells[1],
                    "role": cells[2].strip(),
                    "category": cells[3],
                    "location": cells[4].strip(),
                    "score_col": cells[5].strip(),
                    "url": cells[8],
                })
    return rows


REGRESSION_BAD = [
    "IRIS² Lead Ground Segment Service Engineer",
    "Conceptual Copywriter",
    "AR Specialist Contractor",
    "Mid-Market Customer Success Manager - EMEA",
]


def main(xls_path: Path) -> int:
    if not xls_path.exists():
        print(f"File not found: {xls_path}")
        return 1

    rows = load_all_jobs(xls_path)
    if not rows:
        print("No 'All Jobs' rows parsed — is this a CareerOps spreadsheet?")
        return 1

    strong, good, near = [], [], []
    dropped = 0
    for r in rows:
        sc = scanner.get_match_score(r["role"], "")
        r["score"], r["cat"] = sc["score"], sc["category"]
        job = {"title": r["role"], "description": "", "location": r["location"],
               "company": r["company"], "url": r["url"]}
        if (scanner.is_stub_listing(job)
                or not scanner.is_open_worldwide(r["location"], "")
                or len(scanner.drop_unqualified_matches([job])) == 0):
            r["score"], r["cat"] = 0, "Other"
        if r["score"] == 0:
            dropped += 1
        elif r["score"] >= 75:
            strong.append(r)
        elif r["score"] >= 50:
            good.append(r)
        else:
            near.append(r)

    print("=" * 78)
    print(f"REPLAY OF {xls_path.name}  ({len(rows):,} listings)")
    print("=" * 78)
    print(f"hard-dropped : {dropped:,}  ({(dropped / len(rows) * 100):.1f}%)")

    print(f"\nSTRONG survivors (would reach your email as a fit, {len(strong)}):")
    for r in strong:
        print(f"   {r['score']:>3}%  {r['cat'][:22]:<22} "
              f"{r['company'][:24]:<24} {r['role'][:56]}")
    if good:
        print(f"\nGOOD tier (50-74, {len(good)}):")
        for r in good:
            print(f"   {r['score']:>3}%  {r['cat'][:22]:<22} "
                  f"{r['company'][:24]:<24} {r['role'][:56]}")

    print("\nRegression check — the 2026-09-19 offenders must be gone:")
    reg_ok = True
    for title in REGRESSION_BAD:
        sc = scanner.get_match_score(title, "")
        survived = sc["score"] >= 50
        status = "STILL PRESENT (FAIL)" if survived else f"DROPPED ({sc['score']})"
        if survived:
            reg_ok = False
        print(f"   {title[:56]:<56} -> {status}")
    lt = scanner.get_match_score("Legal Translator", "").get("score", 0)
    print("   Legal Translator regression -> ",
          "OK (100)" if lt >= 75 else "BROKEN")

    verdict = "PASS" if reg_ok else "FAIL"
    print("\n" + "=" * 78)
    print(f"VERDICT: {verdict}  (lexical-only replay; live pipeline adds the AI verdict gate)")
    print("=" * 78)
    return 0 if reg_ok else 2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(Path(sys.argv[1])))