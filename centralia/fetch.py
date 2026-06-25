"""Fetch fresh test PDFs per court from CourtListener.

For each court, pull recent documents that aren't already in
``assets/<court>/``, download them, and run the court's extractor + audit so
the court can be exercised against documents it was never tuned on. We pull
*whatever is new* — orders, notices, minute entries, opinions, every document
type — not just opinions: the extractor should handle anything a docket
throws at it, so broadening the sample with non-opinion filings is the point.

Source per court (auto-detected, override with ``--source``):
  * Federal trial/appellate courts (PACER/RECAP — asset names
    ``gov.uscourts.*``) -> the RECAP search (``type=rd``). These are the real
    filed PDFs, named exactly as the existing corpus
    (``gov.uscourts.caed.488656.4.0.pdf``).
  * State courts -> the Opinions API (one cluster opinion per file).
The source is inferred from the existing asset names, falling back to the
extractor family (``DistrictBase`` / a circuit base -> RECAP).

Usage:
    uv run python -m centralia.fetch caed            # 1 new document
    uv run python -m centralia.fetch caed --n 5      # 5 new documents
    uv run python -m centralia.fetch --all --n 1     # one per court
    uv run python -m centralia.fetch md --source opinions
    uv run python -m centralia.fetch caed --no-check  # skip extract+audit

Authentication: the SEARCH step needs ``COURTLISTENER_API_TOKEN`` in the
environment (an FLP token; raises the rate limits). The PDF *download* itself
is from public storage and needs no token. The registry court id is used as
the CourtListener court id directly (they were chosen to match — 'caed',
'scotus', 'tenncrimapp', ...); use ``--cl-court`` where they differ.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://www.courtlistener.com/api/rest/v4"
STORAGE = "https://storage.courtlistener.com/"

# CourtListener API token env var names, in order of preference. The token is
# read from the environment or a repo-root ``.env`` file (KEY=VALUE lines).
_TOKEN_KEYS = ("CL_API_TOKEN", "COURTLISTENER_API_TOKEN")


def _load_dotenv() -> None:
    """Load simple KEY=VALUE lines from a ``.env`` at the repo root (and cwd)
    into ``os.environ`` without overriding existing values. Quotes around the
    value are stripped; '#' comment lines are ignored. No dependency."""
    roots = {Path(__file__).resolve().parent.parent, Path.cwd()}
    for root in roots:
        env = root / ".env"
        if not env.is_file():
            continue
        for raw in env.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val


def _token() -> str | None:
    _load_dotenv()
    for k in _TOKEN_KEYS:
        if os.environ.get(k):
            return os.environ[k]
    return None


# --------------------------------------------------------------------------- net
def _headers() -> dict:
    h = {"User-Agent": "centralia-fetch/1.0"}
    token = _token()
    if token:
        h["Authorization"] = f"Token {token}"
    return h


def _request(url: str) -> dict:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _storage_url(filepath_local: str) -> str:
    """A RECAP ``filepath_local`` ('recap/gov.uscourts.caed.../...pdf') as a
    public storage URL."""
    return STORAGE + filepath_local.lstrip("/")


def _download(url: str, out: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=_headers())
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
    except Exception as exc:  # noqa: BLE001 - report and skip
        print(f"  ! {url}: {exc}", file=sys.stderr)
        return False
    if not data.startswith(b"%PDF"):
        # Some courts (e.g. the 7th Circuit) prepend a one-line metadata header
        # ('Cas:..:Cap:USA v ...') before the '%PDF' marker. Strip any leading
        # bytes so a clean PDF lands on disk (pdfplumber needs the real start).
        idx = data.find(b"%PDF")
        if idx < 0:
            print(f"  ! {url}: not a PDF (got {len(data)} bytes)", file=sys.stderr)
            return False
        data = data[idx:]
    out.write_bytes(data)
    return True


# ------------------------------------------------------------------------- slug
def _slug(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        elif ch in " /":
            out.append("_")
    return "".join(out).strip("_") or "document"


# ----------------------------------------------------------------- source pick
def _detect_source(court_id: str) -> str:
    """'recap' or 'opinions', inferred from the existing asset filenames
    (a court already populated with 'gov.uscourts.*' PDFs is RECAP), falling
    back to the extractor family for an empty court."""
    dest = Path("assets") / court_id
    names = [p.name for p in dest.glob("*.pdf")] if dest.exists() else []
    if any(n.startswith("gov.uscourts.") for n in names):
        return "recap"
    if names:
        return "opinions"
    try:
        from .courts._district import DistrictBase
        from .registry import get_extractor

        ext = get_extractor(court_id)
        if isinstance(ext, DistrictBase):
            return "recap"
        if any("Circuit" in c.__name__ for c in type(ext).__mro__):
            return "recap"
    except Exception:  # noqa: BLE001 - registry miss -> default below
        pass
    return "opinions"


# ----------------------------------------------------------------- result iter
def _recap_results(cl_court: str):
    """Yield RECAP document records (newest filed first) for ``cl_court``."""
    params = urllib.parse.urlencode(
        {
            "type": "rd",
            "court": cl_court,
            "available_only": "on",
            "order_by": "entry_date_filed desc",
        }
    )
    url = f"{API}/search/?{params}"
    while url:
        data = _request(url)
        for r in data.get("results", []):
            yield r
        url = data.get("next")


def _opinion_results(cl_court: str):
    """Yield opinion records (newest created first) for ``cl_court``."""
    params = urllib.parse.urlencode(
        {
            "cluster__docket__court": cl_court,
            "order_by": "-date_created",
            "fields": "id,download_url,local_path,absolute_url",
            "page_size": 20,
        }
    )
    url = f"{API}/opinions/?{params}"
    while url:
        data = _request(url)
        for r in data.get("results", []):
            yield r
        url = data.get("next")


def _recap_target(r: dict):
    """(name, url) for a RECAP record, or None if it has no fetchable PDF."""
    fp = r.get("filepath_local") or ""
    if not fp.endswith(".pdf"):
        return None
    return Path(fp).name, _storage_url(fp)


def _opinion_target(r: dict):
    """(name, url) for an opinion record, or None when it has no PDF.

    Case-law opinions are often text-only (no PDF) — those are skipped. When an
    opinion IS backed by a PDF it is usually a RECAP document
    ('recap/gov.uscourts.<court>.<docket>.<entry>.pdf'); keep that
    'gov.uscourts.*' name so the file matches the federal corpus convention.
    Any other stored PDF is named from the case slug."""
    local = r.get("local_path") or ""
    if local.endswith(".pdf"):
        # The stored-PDF basename already follows the corpus convention for
        # both kinds of opinion: recap-backed ('gov.uscourts.<court>...pdf')
        # and the court's own slip PDF ('crawford_v._salve_regina_univ.pdf').
        return Path(local).name, _storage_url(local)
    if (r.get("download_url") or "").endswith(".pdf"):
        stem = (r.get("absolute_url") or f"op_{r.get('id')}").rstrip("/").rsplit(
            "/", 1
        )[-1]
        return _slug(stem) + ".pdf", r["download_url"]
    return None


# ------------------------------------------------------------------- downloads
def download_targets(court_id: str, targets, n: int) -> list:
    """Download up to ``n`` (name, url) pairs into assets/<court_id>/, skipping
    any name already present. ``targets`` is an iterable of (name, url).
    Returns the new file paths. Shared by the live REST path and by callers
    that supply pre-resolved targets (e.g. an MCP-sourced sample)."""
    dest = Path("assets") / court_id
    dest.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in dest.glob("*.pdf")}
    new: list = []
    for name, url in targets:
        if len(new) >= n:
            break
        if not name or name in have:
            continue
        out = dest / name
        if _download(url, out):
            new.append(out)
            have.add(name)
            print(f"  + {out}")
    return new


def fetch_court(
    court_id: str,
    cl_court: str | None = None,
    n: int = 1,
    source: str | None = None,
) -> list:
    """Download up to ``n`` recent documents for ``court_id`` not already in
    assets/<court_id>/. Returns the new file paths."""
    cl = cl_court or court_id
    # Default to the case-law OPINIONS collection (the curated court decisions,
    # which for federal courts carry RECAP-stored PDFs) rather than the raw
    # RECAP docket dump; pass source='recap' to pull every docket filing.
    src = source or "opinions"
    if src == "recap":
        targets = (t for r in _recap_results(cl) if (t := _recap_target(r)))
    else:
        targets = (t for r in _opinion_results(cl) if (t := _opinion_target(r)))
    return download_targets(court_id, targets, n)


# ----------------------------------------------------------------------- audit
def check(court_id: str, paths: list) -> None:
    """Run the extractor + audit on the new files and report."""
    from .audit import audit_coverage, format_report
    from .registry import get_extractor

    for p in paths:
        ex = get_extractor(court_id)
        try:
            doc = ex.extract(str(p))
            res = audit_coverage(doc, str(p), extractor=ex)
            ops = ", ".join(op.type for op in doc.opinions) or "none"
            print(f"  {p.name}: {doc.doc_type}, opinions: {ops}")
            print("  " + format_report(p.name, res, limit=5))
        except Exception as exc:  # noqa: BLE001 - report, keep going
            print(f"  {p.name}: EXTRACTION ERROR {exc}")


# ------------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("court", nargs="?", help="registry court id")
    ap.add_argument("--cl-court", help="CourtListener court id override")
    ap.add_argument("--n", type=int, default=1, help="new documents to fetch")
    ap.add_argument(
        "--to",
        type=int,
        help="fill each court UP TO this many total PDFs (downloads only the "
        "shortfall; overrides --n)",
    )
    ap.add_argument(
        "--source",
        choices=("recap", "opinions"),
        help="document source (default: opinions / case law)",
    )
    ap.add_argument("--all", action="store_true", help="one per registered court")
    ap.add_argument("--no-check", action="store_true", help="skip extract+audit")
    args = ap.parse_args()

    if args.all:
        from .registry import EXTRACTORS

        courts = sorted(EXTRACTORS)
    elif args.court:
        courts = [args.court]
    else:
        ap.error("give a court id or --all")

    for cid in courts:
        src = args.source or "opinions"
        if args.to is not None:
            have = len(list((Path("assets") / cid).glob("*.pdf")))
            n = max(0, args.to - have)
            print(f"== {cid}  ({src})  have {have}, need {n} to reach {args.to}")
            if n == 0:
                continue
        else:
            n = args.n
            print(f"== {cid}  ({src})")
        try:
            new = fetch_court(cid, cl_court=args.cl_court, n=n, source=args.source)
        except Exception as exc:  # noqa: BLE001 - report, keep going
            print(f"  ! fetch failed: {exc}", file=sys.stderr)
            continue
        if not new:
            print("  (nothing new)")
            continue
        if not args.no_check:
            check(cid, new)


if __name__ == "__main__":
    main()
