"""Dump a PDF page's text lines with their font/geometry metadata.

A quick lens for figuring out a court's layout: for each text line it prints the
position (top, x0), font size, alignment (C/L/R), bold flag, and font name, then
the text — plus the horizontal rules on the page (caption dividers / footnote
separators) which the extractors key off.

Usage:
    uv run python tests/inspect.py <pdf>                  # page 1 (name or path)
    uv run python tests/inspect.py king_v._schwert        # found under assets/
    uv run python tests/inspect.py <pdf> -p 3             # page 3 (1-based)
    uv run python tests/inspect.py <pdf> -p 1-3           # pages 1..3
    uv run python tests/inspect.py <pdf> -p all           # every page
    uv run python tests/inspect.py <pdf> --chars          # per-CHAR dump too
    uv run python tests/inspect.py <pdf> --geom           # every rect/line (H/V/box)
    uv run python tests/inspect.py --court kan            # page 1 of every kan file
    uv run python tests/inspect.py --court kan -p 2       # page 2 of every kan file

The bare filename is resolved under assets/. By default the dump is the raw
pdfplumber line clustering; pass --court <id> to run that court's page_lines()
(margin filtering, caption column split, running-header drop) so the dump
matches what the extractor actually sees — and, with no file given, --court
dumps the page for every PDF in assets/<court>/.
"""

from __future__ import annotations

import os
import sys

# This file is named inspect.py, which shadows the stdlib `inspect` that
# pdfminer imports. When run as a script, its own directory lands on sys.path[0]
# and wins — so drop the script dir from sys.path before importing pdfplumber.
# (`restatement` is an installed package, so it still imports fine.)
_here = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _here]

from collections import Counter, defaultdict


def _resolve(arg: str) -> str:
    """Accept a full path, or just a file name to find under assets/.

    Tries, in order: the path as given; assets/**/<name>; assets/**/<name>.pdf;
    then a substring match assets/**/*<name>*.pdf.
    """
    import glob

    if os.path.isfile(arg):
        return arg
    root = os.path.join(os.path.dirname(_here), "assets")
    name = arg if arg.endswith(".pdf") else arg + ".pdf"
    for pat in (
        os.path.join(root, "**", os.path.basename(name)),
        os.path.join(root, "**", f"*{os.path.basename(arg)}*.pdf"),
    ):
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            if len(hits) > 1:
                print(f"(matched {len(hits)}; using {hits[0]})", file=sys.stderr)
            return hits[0]
    raise SystemExit(f"no PDF found for {arg!r} (looked under {root})")


def _parse_pages(spec: str, n: int) -> list[int]:
    if spec == "all":
        return list(range(n))
    if "-" in spec:
        a, b = spec.split("-", 1)
        return [i - 1 for i in range(int(a), int(b) + 1) if 1 <= i <= n]
    return [int(spec) - 1]


def _align(x0: float, x1: float, pw: float) -> str:
    cx = (x0 + x1) / 2
    if x0 > 100 and abs(cx - pw / 2) < 25 and (x1 - x0) < pw * 0.55:
        return "C"
    if x0 > pw * 0.6:
        return "R"
    return "L"


def _line_meta(chars: list) -> tuple[float, str, bool]:
    """Modal size + font, and whether the line is bold — mirrors the extractors."""
    sizes = Counter(round(c.get("size", 0), 1) for c in chars)
    fonts = Counter((c.get("fontname") or "") for c in chars)
    size = sizes.most_common(1)[0][0]
    font = fonts.most_common(1)[0][0]
    return size, font.split("+")[-1], "Bold" in font


def _rules(page) -> list:
    """Thin, wide horizontal rules (rects + vector lines), top-sorted."""
    out = []
    for r in page.rects:
        if r["height"] < 2.5 and (r["x1"] - r["x0"]) > 40:
            out.append((r["top"], r["x0"], r["x1"]))
    for ln in page.lines:
        if abs(ln["y1"] - ln["y0"]) < 2.5 and abs(ln["x1"] - ln["x0"]) > 40:
            out.append((ln["top"], min(ln["x0"], ln["x1"]), max(ln["x0"], ln["x1"])))
    return sorted(out)


def _kind(x0, top, x1, bottom) -> str:
    """Tag a drawn object by shape: H-rule (thin + wide), V-rule (thin +
    tall), dot (tiny), or box (everything else) — the geometry a footnote
    separator / caption rail / box edge is keyed off."""
    w, h = x1 - x0, bottom - top
    if h < 2.5 and w >= 2.5:
        return "H"
    if w < 2.5 and h >= 2.5:
        return "V"
    if w < 2.5 and h < 2.5:
        return "·"
    return "box"


def dump_geometry(page) -> None:
    """Every rect and vector line on the page with full coordinates, sorted
    top→left, each tagged H/V/box — so a footnote separator (a thin H rect
    in the lower page) is distinguishable from caption-box edges and rails.
    The 'H' rows are exactly the candidates a footnote-separator rule sees."""
    pw, ph = page.width, page.height

    def rows(objs, label, x1k="x1", botk="bottom"):
        items = []
        for o in objs:
            x0, x1 = o["x0"], o[x1k]
            top, bottom = o["top"], o.get(botk, o["top"])
            if x1 < x0:
                x0, x1 = x1, x0
            items.append((top, x0, x1, bottom))
        items.sort()
        if not items:
            return
        print(f"  -- {label} ({len(items)}) --")
        for top, x0, x1, bottom in items:
            k = _kind(x0, top, x1, bottom)
            # fraction of page width the object spans (the full/half tell)
            frac = (x1 - x0) / pw
            print(
                f"     {k:3} top={top:6.1f} x0={x0:6.1f} x1={x1:6.1f} "
                f"bot={bottom:6.1f} w={x1 - x0:6.1f} h={bottom - top:5.1f} "
                f"({frac:.0%} pw, top {top / ph:.0%})"
            )

    print(f"  ============ geometry  (page {pw:.0f} x {ph:.0f}) ============")
    rows(page.rects, "rects")
    rows(page.lines, "lines", x1k="x1", botk="bottom")


def dump_page(page, pageno: int, *, chars=False, court_lines=None, geom=False) -> None:
    pw = page.width

    # lines = page.extract_text_lines(use_text_flow=True)
    # print(lines)
    # for line in lines:
    #     print(line['text'])
    # print(page.objects)
    # for c in page.objects:
    #     # if c["text"] in "()" or c["text"].startswith(("Ara", "J")):
    #     print(c)
            # print(f"{c']!r:10} top={c['top']:7.2f} "
            #     f"size={c.get('size',0):5.2f} "
            #     f"font={(c.get('fontname') or '').split('+')[-1]:20} "
            #     f"matrix={c.get('matrix')}")


    # return
    print(f"=== page {pageno + 1}  ({pw:.0f} x {page.height:.0f}) ===")
    lines = court_lines if court_lines is not None else page.extract_text_lines()
    lines = [l for l in lines if l.get("chars")]
    
    # The page's single-line spacing: the modal gap between consecutive tops. A
    # gap bigger than that is a line break (paragraph / section gap).
    gaps = [round(lines[i]["top"] - lines[i - 1]["top"]) for i in range(1, len(lines))]
    line_h = Counter(g for g in gaps if g > 0).most_common(1)[0][0] if gaps else 0
    prev_top = None
    for l in lines:
        ch = l["chars"]
        gap = None if prev_top is None else l["top"] - prev_top
        if gap is not None and line_h and gap > line_h * 1.4:
            print(f"  · · · gap {gap:.1f}  ({gap / line_h:.1f}× the {line_h}pt line) · · ·")
        prev_top = l["top"]
        size, font, bold = _line_meta(ch)
        a = _align(l["x0"], l["x1"], pw)
        b = "B" if bold else " "
        text = (l.get("text") or "").strip()
        print(
            f"  top={l['top']:6.1f} x0={l['x0']:6.1f} x1={l['x1']:6.1f} "
            f"sz={size:4.1f} {a}{b} {font[:24]:24} | {text[:60]}"
        )
        if chars:
            for c in ch:
                if c.get("text", "").isspace():
                    continue
                print(
                    f"        char x0={c['x0']:6.1f} top={c['top']:6.1f} "
                    f"sz={c.get('size', 0):4.1f} "
                    f"{(c.get('fontname') or '').split('+')[-1][:22]:22} | {c.get('text')!r}"
                )
    if geom:
        dump_geometry(page)
    else:
        rules = _rules(page)
        if rules:
            print("  -- horizontal rules (top, x0, x1, width) --")
            for top, x0, x1 in rules:
                print(f"     top={top:6.1f} x0={x0:6.1f} x1={x1:6.1f} w={x1 - x0:6.1f}")


def main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Dump a PDF page's line metadata.")
    ap.add_argument(
        "pdf",
        nargs="?",
        help="path, or just a file name to find under assets/. "
        "Omit it and pass --court to dump every file in that court.",
    )
    ap.add_argument(
        "-p", "--page", default="1", help="N, N-M, or 'all' (1-based; default 1)"
    )
    ap.add_argument("--chars", action="store_true", help="also dump per-char metadata")
    ap.add_argument(
        "--geom",
        action="store_true",
        help="dump every rect and vector line (full coords, tagged "
        "H/V/box) instead of just horizontal rules — the geometry a "
        "footnote separator / caption rail keys off",
    )
    ap.add_argument(
        "--court",
        help="run this court's page_lines(); also, with no file, "
        "dumps every PDF in assets/<court>/",
    )
    args = ap.parse_args(argv)

    import glob

    import pdfplumber

    ex = None
    if args.court:
        from restatement.registry import get_extractor

        ex = get_extractor(args.court)

    if args.pdf:
        files = [_resolve(args.pdf)]
    elif args.court:
        root = os.path.join(os.path.dirname(_here), "assets", args.court)
        files = sorted(glob.glob(os.path.join(root, "*.pdf")))
        if not files:
            raise SystemExit(f"no PDFs under {root}")
    else:
        ap.error("give a PDF (name or path), or --court <id> to dump a whole court")

    for fp in files:
        if len(files) > 1:
            print(f"\n########## {os.path.basename(fp)} ##########")
        with pdfplumber.open(fp) as pdf:
            for i in _parse_pages(args.page, len(pdf.pages)):
                page = pdf.pages[i]
                court_lines = ex.page_lines(page) if ex is not None else None
                dump_page(
                    page, i, chars=args.chars, court_lines=court_lines,
                    geom=args.geom,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
