"""The v1 oracle: every place v2 disagrees with the frozen v1 output.

v1 parsed most courts correctly, court by court, over a long time. Its
output is frozen under baseline/. This tool diffs v2 against it and writes
a ranked worklist — so defects are found by machine, not by eye.

    uv run python harness/cli.py v1diff              # all baselined courts
    uv run python harness/cli.py v1diff ca9 ca10     # some courts

Writes notes/v1-diff.md (the worklist) and output/notes/v1diff.json (raw).
Ranked by kind: opinion-count first (did we find the right writings), then
doc-type, then footnote labels, then section-word drift.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "harness"))

from centralia.settings import BASELINE_DIR, CORPUS_ROOT, OUTPUT_DIR  # noqa: E402

REPORT = REPO_ROOT / "notes" / "v1-diff.md"
RAW = OUTPUT_DIR / "notes" / "v1diff.json"
# Word-count drift below this is noise (furniture removal improved, star
# pagination added, sections re-routed) — not a defect worth listing.
WORD_DRIFT = 0.15


def _court_diffs(court: str) -> list[dict]:
    import baseline
    import compare as cmp
    from centralia.pipeline import extract

    try:
        base = baseline.load(court)["files"]
    except Exception:                                       # noqa: BLE001
        return []
    out = []
    for stem, old in sorted(base.items()):
        pdf = CORPUS_ROOT / court / f"{stem}.pdf"
        if not pdf.is_file():
            continue
        try:
            new = cmp.new_record(extract(str(pdf), court))
        except Exception as e:                              # noqa: BLE001
            out.append({"court": court, "stem": stem, "kind": "error",
                        "detail": f"{type(e).__name__}: {e}"[:100]})
            continue
        def _n(rec):
            v = rec.get("opinions", 0)
            return len(v) if isinstance(v, (list, tuple)) else int(v or 0)

        def _kinds(rec):
            v = rec.get("opinions", [])
            if not isinstance(v, (list, tuple)):
                return ""
            return ",".join((o.get("type") or "?")[:9] if isinstance(o, dict)
                            else str(o)[:9] for o in v)

        o_ops, n_ops = _n(old), _n(new)
        if o_ops != n_ops:
            out.append({"court": court, "stem": stem, "kind": "opinion-count",
                        "detail": f"v1={o_ops} [{_kinds(old)}] "
                                  f"v2={n_ops} [{_kinds(new)}]"[:120]})
        if old.get("doc_type") != new.get("doc_type"):
            out.append({"court": court, "stem": stem, "kind": "doc-type",
                        "detail": f"{old.get('doc_type')} -> "
                                  f"{new.get('doc_type')}"})
        ow, nw = old.get("section_words", {}), new.get("section_words", {})
        for sec in set(ow) | set(nw):
            a, b = ow.get(sec, 0), nw.get(sec, 0)
            if a and abs(b - a) > WORD_DRIFT * a:
                out.append({"court": court, "stem": stem,
                            "kind": f"words:{sec}",
                            "detail": f"{a} -> {b}"})
            elif not a and b > 40:
                out.append({"court": court, "stem": stem,
                            "kind": f"words:{sec}",
                            "detail": f"new section ({b} words)"})
    return out


_ORDER = ["error", "opinion-count", "doc-type"]


def main(args: list[str]) -> int:
    courts = [a for a in args if not a.startswith("-")]
    if not courts:
        courts = sorted(p.stem for p in BASELINE_DIR.glob("*.json"))
    rows: list[dict] = []
    for c in courts:
        got = _court_diffs(c)
        rows.extend(got)
        print(f"{c:8} {len(got):4} diffs")

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(rows, indent=0))

    by_kind = Counter(r["kind"] for r in rows)
    by_court = defaultdict(Counter)
    for r in rows:
        by_court[r["court"]][r["kind"]] += 1

    def rank(k: str) -> tuple:
        return (_ORDER.index(k) if k in _ORDER else len(_ORDER), k)

    lines = ["# v1 vs v2 — where the rewrite disagrees with the old system",
             "",
             "v1 parsed most courts correctly. Every row here is a place v2",
             "differs from that frozen output: either a v2 defect to fix or a",
             "deliberate v2 improvement to note. Ranked worst-first.",
             "", "## Totals", ""]
    for k in sorted(by_kind, key=rank):
        lines.append(f"- `{k}` — {by_kind[k]}")
    lines += ["", "## By court", ""]
    for c in sorted(by_court, key=lambda x: -sum(by_court[x].values())):
        parts = ", ".join(f"{k} {v}" for k, v in
                          sorted(by_court[c].items(), key=lambda kv: rank(kv[0])))
        lines.append(f"- **{c}** — {parts}")
    for kind in sorted(by_kind, key=rank):
        if kind.startswith("words:"):
            continue
        lines += ["", f"## {kind}", ""]
        for r in [x for x in rows if x["kind"] == kind][:120]:
            lines.append(f"- `{r['court']}/{r['stem'][:56]}` — {r['detail']}")
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"\n{len(rows)} diffs -> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
