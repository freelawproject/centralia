"""Fetch fresh test PDFs per court from CourtListener.

Pulls recent opinions for a court (one at a time, newest first), downloads
the PDF into ``assets/<court>/``, and runs the court's extractor + audit on
it — so each court can be exercised against documents it was never tuned
on.

Usage:
    # one new PDF for one court
    uv run python -m restatement.fetch tenncrimapp

    # N new PDFs
    uv run python -m restatement.fetch tenncrimapp --n 3

    # every registered court, one each (skips courts with no CL mapping)
    uv run python -m restatement.fetch --all

Authentication: set COURTLISTENER_API_TOKEN in the environment (an FLP
token raises the rate limits). Without a token the public anonymous rate
limits apply.

The court id is used as the CourtListener court id directly — the registry
ids were chosen to match CL's ids ('tenncrimapp', 'scotus', 'iand', ...).
Use ``--cl-court`` to override where they differ.
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


def _request(url: str) -> dict:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _headers() -> dict:
    h = {"User-Agent": "restatement-fetch/1.0"}
    token = os.environ.get("COURTLISTENER_API_TOKEN")
    if token:
        h["Authorization"] = f"Token {token}"
    return h


def _slug(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        elif ch in " /":
            out.append("_")
    return "".join(out).strip("_") or "opinion"


def fetch_court(court_id: str, cl_court: str | None = None, n: int = 1) -> list:
    """Download up to ``n`` recent PDF opinions for ``court_id`` that aren't
    already in assets/<court_id>/. Returns the new file paths."""
    cl = cl_court or court_id
    dest = Path("assets") / court_id
    dest.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in dest.glob("*.pdf")}

    params = urllib.parse.urlencode(
        {
            "cluster__docket__court": cl,
            "order_by": "-date_created",
            "fields": "id,download_url,local_path,absolute_url",
            "page_size": 20,
        }
    )
    url = f"{API}/opinions/?{params}"
    new_files: list = []
    while url and len(new_files) < n:
        data = _request(url)
        for op in data.get("results", []):
            if len(new_files) >= n:
                break
            pdf_url = None
            local = op.get("local_path") or ""
            if local.endswith(".pdf"):
                pdf_url = f"https://storage.courtlistener.com/{local}"
            elif (op.get("download_url") or "").endswith(".pdf"):
                pdf_url = op["download_url"]
            if not pdf_url:
                continue
            name = _slug(
                (op.get("absolute_url") or f"op_{op['id']}").rstrip("/").rsplit(
                    "/", 1
                )[-1]
            ) + ".pdf"
            if name in have:
                continue
            out = dest / name
            try:
                req = urllib.request.Request(pdf_url, headers=_headers())
                with urllib.request.urlopen(req, timeout=120) as resp:
                    out.write_bytes(resp.read())
            except Exception as exc:
                print(f"  ! {pdf_url}: {exc}", file=sys.stderr)
                continue
            new_files.append(out)
            have.add(name)
            print(f"  + {out}")
        url = data.get("next") if len(new_files) < n else None
    return new_files


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
        except Exception as exc:
            print(f"  {p.name}: EXTRACTION ERROR {exc}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("court", nargs="?", help="registry court id")
    ap.add_argument("--cl-court", help="CourtListener court id override")
    ap.add_argument("--n", type=int, default=1, help="PDFs to fetch")
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
        print(f"== {cid}")
        try:
            new = fetch_court(cid, cl_court=args.cl_court, n=args.n)
        except Exception as exc:
            print(f"  ! fetch failed: {exc}", file=sys.stderr)
            continue
        if not new:
            print("  (nothing new)")
            continue
        if not args.no_check:
            check(cid, new)


if __name__ == "__main__":
    main()
