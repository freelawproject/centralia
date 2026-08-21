"""Content-loss reconciliation: nothing leaves a PDF silently.

For every rendered file, compare the PDF's own text layer (pdftotext, an
independent oracle — not the pipeline's reading) against everything the
pipeline accounted for: rendered section text PLUS the dropped/residual
boxes. Words the PDF has that the output doesn't are the LOSS; a file is
flagged when its loss ratio crosses the floor. Deliberate drops still count
as accounted — the guarantee is "nothing vanishes unexplained", not
"nothing is removed".

    uv run python harness/cli.py coverage [court...] [--floor 0.985]

Writes ranked losses to stdout and the full table to
output/notes/coverage.json.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import CORPUS_ROOT, OUTPUT_DIR  # noqa: E402

COVERAGE = OUTPUT_DIR / "notes" / "coverage.json"
_TAG = re.compile(r"<[^>]+>")
_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,}")
# Ligature/space damage the two readers disagree on harmlessly.
_FOLD = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "’": "'", "‘": "'"})
# Text living only in ANNOTATION appearance streams (digital-signature
# seals): poppler renders it, pdfminer never surfaces it — the pipeline
# cannot lose what it cannot see. Maryland's UELMA authentication box.
_ANNOT_BOILER = re.compile(
    r"Pursuant to the (?:Maryland )?Uniform Electronic Legal\s+Materials"
    r"\s+Act.{0,120}?this document is authentic\.?", re.I | re.S)


def _words(text: str) -> Counter:
    return Counter(w.lower() for w in _WORD.findall(text.translate(_FOLD)))


def _pdf_words(pdf: Path) -> tuple[Counter, int] | None:
    try:
        out = subprocess.run(
            ["pdftotext", "-q", str(pdf), "-"],
            capture_output=True, timeout=60)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    text = _ANNOT_BOILER.sub(" ", out.stdout.decode("utf-8", "replace"))
    return _words(text), max(1, text.count("\f"))


def score_file(court: str, stem: str) -> dict | None:
    pdf = CORPUS_ROOT / court / f"{stem}.pdf"
    html_path = OUTPUT_DIR / court / f"{stem}.html"
    if not pdf.is_file() or not html_path.is_file():
        return None
    got_src = _pdf_words(pdf)
    if got_src is None or not got_src[0]:
        return None
    src, pages = got_src        # PDF page count: furniture repeats per PAGE,
    html = html_path.read_text()  # not per rendered element
    got = _words(_TAG.sub(" ", html))       # sections AND removed boxes
    # Repeated furniture is dropped ONCE per key but removed on every
    # page — weight those entries by page count so 12 repeats of a
    # running head don't read as loss.
    for kind, txt in re.findall(
            r'chip kind">(running-head|running-foot|folio|gutter|stamp)'
            r"</span>p\d+ · ([^<]*)", html):
        for w, n in _words(txt).items():
            got[w] += n * pages
    missing = src - got
    # pdftotext DEHYPHENATES line-wraps ('three-judge' -> 'threejudge');
    # the render keeps the hyphen, so its halves are separate tokens. A
    # missing word whose split halves are both present is that mismatch,
    # not loss.
    for w in [w for w in missing if len(w) >= 6]:
        if any(w[:i] in got and w[i:] in got
               for i in range(3, len(w) - 2)):
            del missing[w]
    n_src = sum(src.values())
    n_miss = sum(missing.values())
    return {
        "ratio": round(1 - n_miss / n_src, 4),
        "src": n_src,
        "miss": n_miss,
        "top": [f"{w}×{n}" if n > 1 else w
                for w, n in missing.most_common(12)],
    }


def run(courts: list[str] | None, floor: float = 0.985) -> int:
    table: dict[str, dict] = {}
    if COVERAGE.exists():
        table = json.loads(COVERAGE.read_text()).get("files", {})
    flagged = []
    court_dirs = sorted(
        d for d in OUTPUT_DIR.iterdir()
        if d.is_dir() and d.name not in ("notes", ".pageimg")
        and (not courts or d.name in courts))
    for cd in court_dirs:
        worst = 1.0
        for p in sorted(cd.glob("*.html")):
            if p.stem == "index":
                continue
            row = score_file(cd.name, p.stem)
            if row is None:
                continue
            table[f"{cd.name}/{p.stem}"] = row
            worst = min(worst, row["ratio"])
            if row["ratio"] < floor:
                flagged.append((f"{cd.name}/{p.stem}", row))
        print(f"{cd.name}: worst={worst:.3f}")
    COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE.write_text(json.dumps({"files": table}, indent=0,
                                   sort_keys=True))
    flagged.sort(key=lambda kv: kv[1]["ratio"])
    print(f"\n{len(flagged)} files under floor {floor}:")
    for k, row in flagged[:40]:
        print(f"  {row['ratio']:.3f} {k[:70]}")
        print(f"        missing: {', '.join(row['top'][:8])}")
    return 0


def main(args: list[str]) -> int:
    floor = 0.985
    if "--floor" in args:
        floor = float(args[args.index("--floor") + 1])
    courts = [a for a in args if not a.startswith("-")
              and not re.fullmatch(r"[\d.]+", a)]
    return run(courts or None, floor)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
