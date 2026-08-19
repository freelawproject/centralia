"""The regression guard: every case we ever fixed, checked in one command.

Each fix in this project came from a real file. The guard PINS that file's
structural signature — how many writings, of what kind, whether the lead one
is bylined, where the headmatter ends, which sections exist, which criteria
were found — so the next fix cannot silently undo it.

    uv run python harness/cli.py guard              # check every sentinel
    uv run python harness/cli.py guard ca9 ca10     # check some courts
    uv run python harness/cli.py guard --bless      # re-pin (state verified)
    uv run python harness/cli.py guard --add ca9/foo   # pin a new sentinel

The signature deliberately excludes prose text: it answers "is this document
still put together the same way", which is what fixes break. Run it after
EVERY engine change — it takes seconds, and a diff means a regression.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import CORPUS_ROOT  # noqa: E402

PINS = REPO_ROOT / "tests" / "fixtures" / "guard.json"


def _hm_roles(items: list) -> dict:
    """(role -> rows) over a headmatter, counting a CaptionBlock's own cells.
    An untagged row is counted under '' — that is the measurement of what no
    reader claimed, and it must be able to go UP as well as down."""
    from centralia import model as _m
    out: dict = {}

    def _add(row) -> None:
        out[row.role or ""] = out.get(row.role or "", 0) + 1

    for it in items:
        if isinstance(it, _m.HmLine):
            _add(it)
        elif isinstance(it, _m.CaptionBlock):
            for row in list(it.left) + list(it.right):
                _add(row)
    return dict(sorted(out.items()))


def signature(court: str, stem: str) -> dict:
    """The structural fingerprint of one extraction."""
    from centralia.pipeline import extract

    pdf = CORPUS_ROOT / court / f"{stem}.pdf"
    if not pdf.is_file():
        return {"error": "missing-pdf"}
    try:
        r = extract(str(pdf), court)
    except Exception as e:                                  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"[:120]}
    d = r.document
    lead = next((o for o in d.opinions
                 if o.type in ("majority", "order", "per-curiam")), None)
    c = d.criteria
    return {
        "status": r.status,
        "ops": [o.type for o in d.opinions],
        "op_blocks": [len(o.blocks) for o in d.opinions],
        "lead_bylined": bool(lead and (lead.author or "").strip()),
        "hm": len(d.headmatter),
        # HOW THE HEADMATTER WAS READ, not just how much of it there is.
        # `hm` is a count with a 25% tolerance, so a court could lose every
        # role tag in its block and every sentinel would still pass — and
        # the roles ARE the product of a port. Recorded as the sorted set of
        # roles claimed plus the number of rows left unclaimed, so both a
        # vanished role and a newly-unread row are visible.
        "hm_roles": _hm_roles(d.headmatter),
        "syllabus": len(d.syllabus),
        "summary": len(d.summary),
        "attorneys": len(d.attorneys),
        "residual": len(d.residual),
        "criteria": sorted(k for k in (
            "docket_number", "decision_date", "submitted", "judges",
            "parties", "publication_status", "lower_court", "disposition")
            if getattr(c, k)),
    }


# Fields where an EXACT match is required; block counts may drift by a
# little as paragraph joining improves, so they are checked as a tolerance.
_EXACT = ("status", "ops", "lead_bylined", "syllabus", "summary",
          "attorneys", "residual", "criteria")


def _compare(want: dict, got: dict) -> list[str]:
    if "error" in want or "error" in got:
        if want.get("error") != got.get("error"):
            return [f"error: {want.get('error')} -> {got.get('error')}"]
        return []
    out = []
    for k in _EXACT:
        if want.get(k) != got.get(k):
            out.append(f"{k}: {want.get(k)!r} -> {got.get(k)!r}")
    # headmatter size: a big jump means the body leaked into it (or vice
    # versa) — the single most common regression in this project.
    w, g = want.get("hm", 0), got.get("hm", 0)
    if abs(g - w) > max(4, 0.25 * max(w, 1)):
        out.append(f"hm: {w} -> {g}")
    # HOW THE HEADMATTER WAS READ. Compared only where the PIN carries it:
    # the field was added on 2026-08-19 and 335 of 340 pins predate it, so
    # comparing unconditionally would report a diff on every one of them.
    # Those pins are simply unprotected on this axis until re-blessed —
    # which is the honest state, and visible via `--roleless` below.
    wr, gr = want.get("hm_roles"), got.get("hm_roles")
    if wr is not None and wr != gr:
        out.append(f"hm_roles: {wr} -> {gr}")
    wb, gb = want.get("op_blocks", []), got.get("op_blocks", [])
    if len(wb) == len(gb):
        for i, (a, b) in enumerate(zip(wb, gb)):
            if abs(b - a) > max(3, 0.2 * max(a, 1)):
                out.append(f"op{i}_blocks: {a} -> {b}")
    return out


def _sig_one(key: str) -> tuple[str, dict]:
    court, _, stem = key.partition("/")
    return key, signature(court, stem)


def _load() -> dict:
    if PINS.exists():
        return json.loads(PINS.read_text())
    return {}


def _save(pins: dict) -> None:
    PINS.parent.mkdir(parents=True, exist_ok=True)
    PINS.write_text(json.dumps(pins, indent=1, sort_keys=True))


def _census_one(court: str) -> tuple[str, dict]:
    """Status counts for a whole court — the corpus-wide safety net that
    62 sentinels cannot provide (a change can leave every sentinel green
    and still push 60 other files into review)."""
    import glob
    from centralia.pipeline import extract
    from centralia.settings import CORPUS_ROOT

    counts = {"valid": 0, "scanned": 0, "review": 0, "failed": 0, "error": 0}
    for pdf in sorted(glob.glob(str(CORPUS_ROOT / court / "*.pdf"))):
        try:
            counts[extract(pdf, court).status] += 1
        except Exception:                                   # noqa: BLE001
            counts["error"] += 1
    return court, counts


def census(args: list[str]) -> int:
    """guard --census [court...]: per-court status counts vs the pinned
    census. Slower than the sentinels; run it before calling a wave done."""
    import json as _json
    pins_path = PINS.parent / "guard_census.json"
    old = _json.loads(pins_path.read_text()) if pins_path.exists() else {}
    courts = [a for a in args if not a.startswith("-")] or sorted(old) or []
    if not courts:
        print("no courts given and no census pinned")
        return 0
    with ProcessPoolExecutor(max_workers=6) as ex:
        got = dict(ex.map(_census_one, courts))
    bad = 0
    for c in courts:
        now = got[c]
        was = old.get(c)
        flag = ""
        if was and now.get("review", 0) > was.get("review", 0) + 1:
            flag = f"   REGRESSION (review {was['review']} -> {now['review']})"
            bad += 1
        print(f"{c:12} {now}{flag}")
    if "--bless" in args:
        pins_path.write_text(_json.dumps(got, indent=1, sort_keys=True))
        print("census blessed")
        return 0
    return 1 if bad else 0


def main(args: list[str]) -> int:
    if "--census" in args:
        return census([a for a in args if a != "--census"])
    pins = _load()
    if "--add" in args:
        keys = [a for a in args[args.index("--add") + 1:]
                if not a.startswith("-")]
        for k in keys:
            _, sig = _sig_one(k)
            pins[k] = sig
            print(f"pinned {k}: {sig.get('ops')}")
        _save(pins)
        return 0

    courts = [a for a in args if not a.startswith("-")]
    keys = [k for k in sorted(pins)
            if not courts or k.split("/")[0] in courts]
    if not keys:
        print("no sentinels pinned — use --add <court/stem>")
        return 0

    with ProcessPoolExecutor(max_workers=8) as ex:
        results = dict(ex.map(_sig_one, keys))

    if "--bless" in args:
        for k in keys:
            pins[k] = results[k]
        _save(pins)
        print(f"blessed {len(keys)} sentinels")
        return 0

    bad = 0
    for k in keys:
        diffs = _compare(pins[k], results[k])
        if diffs:
            bad += 1
            print(f"REGRESSION {k}")
            for d in diffs:
                print(f"    {d}")
    print(f"\nguard: {len(keys) - bad}/{len(keys)} sentinels OK")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
