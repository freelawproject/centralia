#!/usr/bin/env python3
"""Rebuild the ``assets/`` test corpus from ``scripts/corpus.txt``.

The corpus is ~10,000 PDFs and ~3 GB, so it is not in git. This script pulls
every one of them back from CourtListener's public storage, where they came
from. **No API token is needed** — storage is public; only regenerating the
manifest needs one.

It is safe to re-run: a file already on disk is skipped, so an interrupted
run picks up where it stopped, and a later run adds only what the manifest
gained.

Usage:
    python scripts/fetch_corpus.py                 # the whole corpus
    python scripts/fetch_corpus.py ala conn cacd   # only these courts
    python scripts/fetch_corpus.py --workers 16    # more parallel downloads
    python scripts/fetch_corpus.py --list          # what's here, what's missing
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

RETRIES = 6      # attempts per file before a throttled download is given up on
BACKOFF = 2.0    # seconds, doubled per retry, capped at 120

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MANIFEST = ROOT / "scripts" / "corpus.txt"
MARKS = ROOT / "output" / "notes" / "marks.json"
# Tiers the reviewer uses, worst to best. 'yay' is the sign-off that gates a
# court's release; anything below it is a file someone still has doubts about.
GOOD = ("yay",)


def marks() -> dict[str, str]:
    """{court/stem: mark} — the reviewer's verdicts, which ship WITH the repo.

    The manifest deliberately does not carry these. A mark changes whenever
    someone reviews another file, and a copy of a moving list is a lie with a
    timestamp on it; marks.json is tracked precisely so there is one place to
    ask. Absent (a partial checkout) -> everything is simply unmarked."""
    if not MARKS.is_file():
        return {}
    try:
        return json.loads(MARKS.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - an unreadable marks file is not fatal
        return {}


def entries(courts: list[str]) -> list[tuple[str, str, str]]:
    """(court, filename, url) rows of the manifest, optionally filtered."""
    if not MANIFEST.is_file():
        sys.exit(f"no manifest at {MANIFEST} — run scripts/build_corpus_manifest.py")
    keep = set(courts)
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        court, name, url = line.split("\t")
        if not keep or court in keep:
            rows.append((court, name, url))
    return rows


def download(url: str, out: Path) -> str:
    """Fetch one PDF. Returns 'ok', 'skip' or an error string.

    Storage rate-limits by IP, and a fresh clone asking for ten thousand files
    WILL be throttled — a 429 here is the normal case, not the exception, and
    treating it as a failure would leave a new developer with a corpus full of
    holes and no idea why. Back off and ask again."""
    if out.exists() and out.stat().st_size > 0:
        return "skip"
    data = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "centralia-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503):
                return f"! {out.name}: {exc}"
            # Honor Retry-After when storage sends one, else exponential.
            wait = exc.headers.get("Retry-After")
            delay = float(wait) if (wait or "").isdigit() else BACKOFF * (2 ** attempt)
            time.sleep(min(delay, 120))
        except Exception as exc:  # noqa: BLE001 - a blip; try again, then report
            if attempt == RETRIES - 1:
                return f"! {out.name}: {exc}"
            time.sleep(BACKOFF)
    if data is None:
        return f"! {out.name}: still throttled after {RETRIES} tries"
    # A few courts (the 7th Circuit among them) prepend a metadata line before
    # the '%PDF' marker; the readers need the file to start at the marker.
    if not data.startswith(b"%PDF"):
        idx = data.find(b"%PDF")
        if idx < 0:
            return f"! {out.name}: not a PDF ({len(data)} bytes)"
        data = data[idx:]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return "ok"


def head(url: str) -> int:
    """Status for one URL, retrying past a rate limit. 0 means never answered."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "centralia-fetch/1.0"})
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503):
                return exc.code
            wait = exc.headers.get("Retry-After")
            delay = float(wait) if (wait or "").isdigit() else BACKOFF * (2 ** attempt)
            time.sleep(min(delay, 120))
        except Exception:  # noqa: BLE001 - a blip; try again
            time.sleep(BACKOFF)
    return 0


def verify(rows: list, sample: int | None, workers: int) -> None:
    """Confirm the manifest points at files that are really there.

    Downloads nothing — a HEAD per URL. Run this from a network storage will
    talk to: from a throttled one every answer is 429, which this reports as
    'unanswered' rather than silently calling the file dead."""
    check = rows
    if sample and sample < len(rows):
        step = len(rows) / sample          # a spread, not the first N of one court
        check = [rows[int(i * step)] for i in range(sample)]
    print(f"verifying {len(check)} of {len(rows)} manifest urls")

    counts, dead, lock = Counter(), [], Lock()

    def work(row):
        court, name, url = row
        status = head(url)
        with lock:
            counts[status] += 1
            if status != 200:
                dead.append(f"{court}\t{name}\t{status}\t{url}")
            done = sum(counts.values())
            if done % 100 == 0:
                print(f"  {done}/{len(check)}  ({counts[200]} ok, {len(dead)} not)")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, check))

    print(f"\n  200 ok        {counts[200]}")
    for status in sorted(k for k in counts if k != 200):
        label = {404: "missing", 403: "forbidden", 0: "unanswered (rate limited?)"}
        print(f"  {status or '  -'} {label.get(status, 'other'):<26} {counts[status]}")
    if dead:
        out = ROOT / "scripts" / "corpus-dead.txt"
        out.write_text("# manifest urls that did not answer 200.\n"
                       "# columns: court<TAB>filename<TAB>status<TAB>url\n"
                       + "\n".join(sorted(dead)) + "\n")
        print(f"\nwrote {out.relative_to(ROOT)}: {len(dead)} urls")
        if counts[0]:
            print("some never answered — that is throttling, not a dead link. "
                  "Re-run from a network storage will talk to.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("courts", nargs="*", help="court ids (default: every court)")
    # Deliberately modest: storage throttles by IP, and more workers just means
    # hitting that wall sooner. Raise it only if you know you are whitelisted.
    ap.add_argument("--workers", type=int, default=4, help="parallel downloads")
    ap.add_argument("--list", action="store_true", help="report coverage, download nothing")
    ap.add_argument("--verify", action="store_true",
                    help="HEAD every manifest URL and report the dead ones, "
                         "downloading nothing (writes scripts/corpus-dead.txt)")
    ap.add_argument("--sample", type=int, metavar="N",
                    help="with --verify, check a spread of N urls instead of all")
    ap.add_argument("--approved", action="store_true",
                    help="only files the reviewer signed off (marked 'yay') — "
                         "the known-good subset, and a smaller download")
    args = ap.parse_args()

    rows = entries(args.courts)
    mk = marks()
    if args.approved:
        before = len(rows)
        rows = [r for r in rows if mk.get(f"{r[0]}/{r[1][:-4]}") in GOOD]
        print(f"--approved: {len(rows)} of {before} files are signed off")

    if args.list:
        have, miss, ok, bad = Counter(), Counter(), Counter(), Counter()
        for court, name, _ in rows:
            (have if (ASSETS / court / name).exists() else miss)[court] += 1
            mark = mk.get(f"{court}/{name[:-4]}")
            if mark in GOOD:
                ok[court] += 1
            elif mark:
                bad[court] += 1
        for court in sorted(set(have) | set(miss)):
            flag = f"  {bad[court]} MARKED BAD" if bad[court] else ""
            print(f"  {court:<16} {have[court]:>5} present, {miss[court]:>5} missing, "
                  f"{ok[court]:>5} signed off{flag}")
        print(f"\n{sum(have.values())} of {len(rows)} files present; "
              f"{sum(ok.values())} signed off, {sum(bad.values())} marked bad, "
              f"{len(rows) - sum(ok.values()) - sum(bad.values())} unreviewed")
        return

    if args.verify:
        verify(rows, args.sample, args.workers)
        return

    todo = [(c, n, u) for c, n, u in rows if not (ASSETS / c / n).exists()]
    print(f"{len(rows)} files in the manifest, {len(todo)} to download")

    counts, lock = Counter(), Lock()

    def work(row):
        court, name, url = row
        result = download(url, ASSETS / court / name)
        with lock:
            counts[result if result in ("ok", "skip") else "fail"] += 1
            done = sum(counts.values())
            if result.startswith("!"):
                print(f"  {result}", file=sys.stderr)
            elif done % 100 == 0:
                print(f"  {done}/{len(todo)}  ({counts['ok']} downloaded, {counts['fail']} failed)")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, todo))

    print(f"\ndownloaded {counts['ok']}, skipped {counts['skip']}, failed {counts['fail']}")
    if counts["fail"]:
        print("failures are usually documents that left public storage, or a rate "
              "limit that outlasted the retries — re-run to pick up what is missing; "
              "files already on disk are skipped. The readers do not depend on any "
              "single file.")


if __name__ == "__main__":
    main()
