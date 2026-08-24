#!/usr/bin/env python3
"""Resolve every PDF in ``assets/`` back to its public CourtListener storage URL.

This is the MAINTAINER side of the corpus handoff: it writes
``scripts/corpus.txt``, the manifest ``scripts/fetch_corpus.py`` replays so a
new developer can rebuild the 3 GB test corpus, which is too big for git.

CourtListener stores a PDF in one of two shapes, and most of the corpus needs
no lookup at all to find it:

1. RECAP filings are named ``gov.uscourts.<court>.<pacer_id>.<entry>.<attach>.pdf``
   and the name spells the whole path:
   ``recap/gov.uscourts.<court>.<pacer_id>/<name>``. Free.
2. Opinion PDFs live at ``pdf/YYYY/MM/DD/<slug>.pdf`` where the date is the day
   CourtListener took the file in — which, for a scraped court, is the day the
   opinion was released. We already hold that date for many documents in
   ``db.sqlite3`` (``library_document.decision_date``), so the URL can be built
   and confirmed with a HEAD request. Free, and no token.
3. Whatever is left — scanned courts that never yielded a date, dates that miss
   by a day — falls back to the Opinions API, paged newest-first per court.
   Order on ``-id``, never ``-date_created``: the latter is unindexed and a
   single page can take 90 seconds where ``-id`` takes 3.

Only step 3 needs ``CL_API_TOKEN`` (repo-root ``.env`` or the environment);
downloading needs nothing, because storage is public.

The manifest is its own cache: a re-run reads ``corpus.txt`` back and works only
on what is not in it, so an interrupted run resumes cheaply and a later one
picks up only what the corpus has gained. ``--refresh`` ignores it and resolves
everything from scratch.

Usage:
    python scripts/build_corpus_manifest.py              # every court
    python scripts/build_corpus_manifest.py ala conn     # just these
    python scripts/build_corpus_manifest.py --no-api     # free passes only
    python scripts/build_corpus_manifest.py --refresh    # ignore the cache
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "output"
DB = ROOT / "db.sqlite3"
MANIFEST = ROOT / "scripts" / "corpus.txt"
UNRESOLVED = ROOT / "scripts" / "corpus-unresolved.txt"

API = "https://www.courtlistener.com/api/rest/v4"
STORAGE = "https://storage.courtlistener.com/"
PAGE_CAP = 120            # pages per court, 20 records each
DRY_PAGES = 20            # give up on a court after this many pages with no new match
DATE_SLACK = 2            # days either side of the recorded date to probe
RENDERED_DATES = 3        # dates to lift off a rendered page before giving up on it
RETRY_429 = 5             # HEAD attempts before a throttled probe is called a miss
BACKOFF = 2.0             # seconds, doubled per retry

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")

# ``decision_date`` is written by whichever reader found it, so it arrives in
# whatever shape the document printed: 'June 13, 2025' from an opinion's release
# line, '05/12/26' from a district court's filing stamp.
DATE_FORMATS = ("%B %d, %Y", "%b %d, %Y", "%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d")


# ------------------------------------------------------------------------ auth
def token() -> str | None:
    for key in ("CL_API_TOKEN", "COURTLISTENER_API_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    env = ROOT / ".env"
    if env.is_file():
        for raw in env.read_text(encoding="utf-8").splitlines():
            k, _, v = raw.strip().partition("=")
            if k.strip() in ("CL_API_TOKEN", "COURTLISTENER_API_TOKEN"):
                return v.strip().strip("'\"")
    return None


def get_json(url: str, tok: str, tries: int = 3) -> dict:
    req = urllib.request.Request(
        url, headers={"Authorization": f"Token {tok}", "User-Agent": "centralia-manifest/1.0"}
    )
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - the API stalls under load
            if attempt == tries - 1:
                print(f"  ! {exc} on {url[:80]}", file=sys.stderr)
                return {}
    return {}


def exists(url: str) -> bool:
    """Is there a file at this storage URL? A HEAD — no body is fetched.

    A 404 is an answer: no such file. A 429 is NOT — it is storage asking us to
    slow down, and reading it as 'missing' quietly turns a throttled run into a
    manifest with holes in it. Back off and ask again; only a real 4xx counts."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "centralia-manifest/1.0"})
    for attempt in range(RETRY_429):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status == 200
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503):
                return False
            time.sleep(BACKOFF * (2 ** attempt))
        except Exception:  # noqa: BLE001 - a network blip, not an answer
            time.sleep(BACKOFF)
    print(f"  ! still throttled after {RETRY_429} tries: {url[:70]}", file=sys.stderr)
    return False


# ------------------------------------------------------------------- the names
def recap_url(name: str) -> str:
    """'gov.uscourts.cacd.1002267.10.0.pdf' -> its storage URL. The docket
    directory is the first four dot-fields of the name."""
    return f"{STORAGE}recap/{'.'.join(name.split('.')[:4])}/{name}"


def wanted(court: str) -> tuple[set[str], set[str]]:
    """(recap names, opinion names) sitting in assets/<court>/."""
    names = {p.name for p in (ASSETS / court).glob("*.pdf")}
    recap = {n for n in names if n.startswith("gov.uscourts.")}
    return recap, names - recap


def already_resolved() -> dict[tuple[str, str], str]:
    """{(court, filename): url} from a manifest written by an earlier run.

    This is the whole cache. A per-court json sidecar said the same thing in 240
    files that had to be ignored by git and could drift from the manifest they
    fed; the manifest already carries court, filename and url per line, so it
    can answer 'do I still need this one?' by itself."""
    if not MANIFEST.is_file():
        return {}
    out: dict[tuple[str, str], str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            court, name, url = parts
            out[(court, name)] = url
    return out


def recorded_dates() -> dict[tuple[str, str], date]:
    """{(court, stem): date} from the ingest DB, for every date it could parse."""
    if not DB.is_file():
        return {}
    out: dict[tuple[str, str], date] = {}
    con = sqlite3.connect(DB)
    rows = con.execute(
        "select court_id, stem, decision_date from library_document "
        "where decision_date is not null and decision_date != ''"
    )
    for court, stem, raw in rows:
        for fmt in DATE_FORMATS:
            try:
                out[(court, stem)] = datetime.strptime(raw.strip(), fmt).date()
                break
            except ValueError:
                continue
    con.close()
    return out


def rendered_dates(court: str, stem: str) -> list[date]:
    """Dates printed on the rendered page, in the order they appear.

    The ingest DB only carries ``decision_date`` for the courts whose readers
    lift one, which leaves most opinions blank — but the release date is right
    there in the document's own text for nearly all of them, and it is almost
    always the FIRST date on the page. Read it back out of ``output/``."""
    page = OUTPUT / court / f"{stem}.html"
    if not page.is_file():
        return []
    text = re.sub(r"<style.*?</style>", "", page.read_text(errors="replace"), flags=re.S)
    text = html_mod.unescape(re.sub(r"<[^>]+>", " ", text))
    out: list[date] = []
    for match in re.finditer(rf"(?:{MONTHS})\s+\d{{1,2}},?\s+\d{{4}}", text):
        for fmt in ("%B %d, %Y", "%B %d %Y"):
            try:
                day = datetime.strptime(match.group(0), fmt).date()
            except ValueError:
                continue
            if day not in out:
                out.append(day)
            break
        if len(out) >= RENDERED_DATES:
            break
    return out


# ------------------------------------------------------------- pass 2: by date
def by_date(court: str, names: set[str], dates: dict) -> dict[str, str]:
    """Build 'pdf/Y/M/D/<name>' from a date we already hold and confirm it with
    a HEAD — no API, no token.

    Candidates in order of how much they are trusted: the date the reader
    recorded, then the dates printed on the rendered page, then a couple of
    days either side of the recorded one. A court's own release date and the
    day CourtListener took the file in usually agree, but a weekend or a slow
    scrape can put them a day or two apart."""
    found: dict[str, str] = {}

    def probe(name: str) -> tuple[str, str] | None:
        stem = name[:-4]
        recorded = dates.get((court, stem))
        candidates: list[date] = [recorded] if recorded else []
        candidates += rendered_dates(court, stem)
        if recorded:
            candidates += [recorded + timedelta(days=off)
                           for n in range(1, DATE_SLACK + 1) for off in (n, -n)]
        seen: set[date] = set()
        for day in candidates:
            if day in seen:
                continue
            seen.add(day)
            url = f"{STORAGE}pdf/{day.year:04d}/{day.month:02d}/{day.day:02d}/{name}"
            if exists(url):
                return name, url
        return None

    with ThreadPoolExecutor(max_workers=16) as pool:
        for hit in pool.map(probe, sorted(names)):
            if hit:
                found[hit[0]] = hit[1]
    return found


# -------------------------------------------------------------- pass 3: by API
def by_api(court: str, names: set[str], tok: str) -> dict[str, str]:
    """Page the court's opinions newest-first, matching stored basenames.
    Stops when everything is placed, when the pages run dry, or when
    ``DRY_PAGES`` go by without a new match (the sign of a court whose
    CourtListener id differs from ours, or of files long since aged out)."""
    params = urllib.parse.urlencode(
        {"cluster__docket__court": court, "order_by": "-id",
         "fields": "id,local_path", "page_size": 20}
    )
    url = f"{API}/opinions/?{params}"
    found: dict[str, str] = {}
    dry = 0
    for _ in range(PAGE_CAP):
        if not url or dry >= DRY_PAGES:
            break
        data = get_json(url, tok)
        before = len(found)
        for rec in data.get("results", []):
            local = rec.get("local_path") or ""
            if local.endswith(".pdf"):
                name = local.rsplit("/", 1)[-1]
                if name in names and name not in found:
                    found[name] = STORAGE + local.lstrip("/")
        dry = 0 if len(found) > before else dry + 1
        if len(found) == len(names):
            break
        url = data.get("next")
    return found


# ------------------------------------------------------------------- per court
def court_manifest(court: str, dates: dict, tok: str | None,
                   known: dict[tuple[str, str], str]) -> dict[str, str]:
    recap, opinions = wanted(court)
    out = {n: recap_url(n) for n in recap}
    if not opinions:
        print(f"  {court:<16} {len(recap):>4} recap")
        return out

    # What an earlier run already placed, straight out of the manifest.
    found = {n: known[(court, n)] for n in opinions if (court, n) in known}

    todo = opinions - found.keys()
    n_date = 0
    if todo:
        hit = by_date(court, todo, dates)
        n_date, found, todo = len(hit), {**found, **hit}, todo - hit.keys()
    n_api = 0
    if todo and tok:
        hit = by_api(court, todo, tok)
        n_api, found, todo = len(hit), {**found, **hit}, todo - hit.keys()

    miss = f", {len(todo)} UNRESOLVED" if todo else ""
    print(f"  {court:<16} {len(recap):>4} recap  {len(found):>4} opinions "
          f"(+{n_date} by date, +{n_api} by api){miss}")
    return {**out, **found}


# -------------------------------------------------------------------- assembly
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("courts", nargs="*", help="court ids (default: every court in assets/)")
    ap.add_argument("--refresh", action="store_true",
                    help="resolve everything again, ignoring the existing manifest")
    ap.add_argument("--no-api", action="store_true", help="skip the API fallback")
    ap.add_argument("--workers", type=int, default=6, help="courts resolved in parallel")
    args = ap.parse_args()

    tok = None if args.no_api else token()
    if not tok and not args.no_api:
        print("no CL_API_TOKEN found — running the free passes only", file=sys.stderr)
    dates = recorded_dates()
    courts = args.courts or sorted(d.name for d in ASSETS.iterdir() if d.is_dir())
    print(f"resolving {len(courts)} courts, {len(dates)} recorded dates on hand\n")

    # --refresh forgets only the courts being run. Forgetting everything would
    # mean `--refresh ala` quietly dropped the other 240 courts from the file.
    known = already_resolved()
    if args.refresh:
        known = {k: v for k, v in known.items() if k[0] not in set(courts)}
    if known:
        print(f"{len(known)} already in {MANIFEST.name} — resolving only the rest")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = dict(zip(courts, pool.map(
            lambda c: court_manifest(c, dates, tok, known), courts)))

    # Write EVERY court, not just the ones this run touched. The manifest is the
    # whole corpus; assembling it from `courts` alone meant `build ala` replaced
    # 10,046 lines with 467 and called that a rebuild.
    lines, unresolved = [], []
    for court in sorted(d.name for d in ASSETS.iterdir() if d.is_dir()):
        recap, opinions = wanted(court)
        found = results.get(court, {})
        for name in sorted(recap | opinions):
            url = found.get(name) or known.get((court, name))
            if url:
                lines.append(f"{court}\t{name}\t{url}")
            else:
                unresolved.append(f"{court}\t{name}")

    MANIFEST.write_text(
        "# The centralia test corpus: every PDF under assets/, as a public\n"
        "# CourtListener storage URL. The corpus is ~3 GB, so it lives here as\n"
        "# a list of links rather than in git.\n"
        "#\n"
        "#   rebuild the corpus:  python scripts/fetch_corpus.py\n"
        "#   rebuild this file:   python scripts/build_corpus_manifest.py\n"
        "#\n"
        "# columns: court<TAB>filename<TAB>url\n" + "\n".join(lines) + "\n"
    )
    print(f"\nwrote {MANIFEST.relative_to(ROOT)}: {len(lines)} files")
    if unresolved:
        UNRESOLVED.write_text(
            "# assets/ PDFs no CourtListener storage URL was found for.\n"
            "# columns: court<TAB>filename\n" + "\n".join(unresolved) + "\n"
        )
        print(f"wrote {UNRESOLVED.relative_to(ROOT)}: {len(unresolved)} unresolved")


if __name__ == "__main__":
    main()
