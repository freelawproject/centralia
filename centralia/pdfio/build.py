"""One pass: PDF file -> PdfModel. The only place pdfplumber is touched.

Per page: char-level quirk repairs (in place, before clustering), rotated-text
capture, line clustering with real space glyphs kept, baseline merges, splits
at vertical rules and at column-wide gaps, underline tagging, drawn-rule
collection, and the raw counts triage needs (ink, cid, image area).

No margins are cut here and nothing is dropped: furniture is a semantic
decision that belongs to the furniture resolver, which sees these lines like
every other consumer.
"""

from __future__ import annotations

import pdfplumber

from . import quirks
from .model import ImageRef, Line, PageModel, PdfModel
from .rules import collect_rules
from .text import inferred_space_gap

# A vertical rule must be at least this tall to split a line into columns —
# shorter verticals are box corners and character-box artifacts.
_SPLIT_VRULE_MIN_H = 30.0
# A same-row gap at least this wide (and 4x the line's own word gap) separates
# two visual columns pdfplumber merged onto one baseline.
_COLUMN_GAP_MIN = 18.0


def _text_lines(source) -> list:
    """``extract_text_lines`` keeping real space chars (tightly tracked fonts
    set word gaps under any fixed threshold: Connecticut's ~1.4pt), and
    cutting ROTATED glyphs — sideways text is a figure axis title or a stamp,
    never a sentence, and read in line order it comes out mirrored."""
    try:
        source = source.filter(lambda o: o.get("upright", True) is not False)
    except Exception:
        pass
    return source.extract_text_lines(keep_blank_chars=True)


def _split_at_vrules(raw_lines: list, v_rules: list, event) -> list:
    """Split a clustered line whose chars span a tall vertical rule — the
    caption-column divider or a pleading gutter. Without this the two columns
    merge into one unreadable row."""
    tall = [v for v in v_rules if v.height >= _SPLIT_VRULE_MIN_H]
    if not tall:
        return raw_lines
    out = []
    n_split = 0
    for ln in raw_lines:
        chars = ln.get("chars") or []
        cuts = sorted({v.x for v in tall
                       if v.top - 2 <= ln["top"] <= v.bottom + 2
                       and any(c["x1"] <= v.x - 0.5 for c in chars)
                       and any(c["x0"] >= v.x + 0.5 for c in chars)})
        if not cuts:
            out.append(ln)
            continue
        buckets: list[list] = [[] for _ in range(len(cuts) + 1)]
        for c in chars:
            mid = (c["x0"] + c["x1"]) / 2
            for i, x in enumerate(cuts):
                if mid < x:
                    buckets[i].append(c)
                    break
            else:
                buckets[-1].append(c)
        pieces = [b for b in buckets if any((c.get("text") or "").strip() for c in b)]
        if len(pieces) < 2:
            out.append(ln)
            continue
        n_split += 1
        for i, b in enumerate(pieces):
            piece = dict(ln)
            piece["chars"] = b
            piece["x0"] = min(c["x0"] for c in b)
            piece["x1"] = max(c["x1"] for c in b)
            piece["text"] = "".join(c.get("text") or "" for c in b)
            piece["_col"] = ("L", "R")[i] if len(pieces) == 2 else None
            piece["_row"] = id(ln)
            out.append(piece)
    if n_split:
        event("vrule-column-split", f"split {n_split} rows at vertical rules")
    return out


def _split_wide_gaps(raw_lines: list, event) -> list:
    """Split a visual row at a column-wide x-gap — two caption columns held by
    whitespace alone (the Open Range), a stamp beside a banner, a rail glyph
    between columns. The threshold is measured against the line's own word
    gap so justified prose never qualifies."""
    out = []
    n_split = 0
    for ln in raw_lines:
        chars = sorted(ln.get("chars") or [], key=lambda c: c["x0"])
        printable = [c for c in chars if (c.get("text") or "").strip()]
        if len(printable) < 2:
            out.append(ln)
            continue
        gap_floor = max(_COLUMN_GAP_MIN, 4.0 * inferred_space_gap(chars))
        cuts = []
        for a, b in zip(printable, printable[1:]):
            if (b["x0"] - a["x1"]) >= gap_floor:
                cuts.append((a["x1"] + b["x0"]) / 2)
        # A LEADING NUMERAL fragment (stationery line number, margin folio)
        # splits at a much smaller gap: '1   that omits such hearing…' is
        # the draft paper's line number welded to the text (ca2). Digits
        # only, ≤3 of them, gap ≥ 8pt — a citation year is 4 digits and a
        # section number sits flush.
        lead = []
        for c in printable:
            if (c.get("text") or "").isdigit():
                lead.append(c)
            else:
                break
        if 0 < len(lead) <= 3 and len(lead) < len(printable):
            nxt = printable[len(lead)]
            gap = nxt["x0"] - lead[-1]["x1"]
            cut_at = (lead[-1]["x1"] + nxt["x0"]) / 2
            page_w = ln.get("_page_width") or 612.0
            # MARGIN fragments only: the stationery number starts far left
            # of any text rail ('583 P.3d 553' opens a CITATION at the note
            # rail and must stay whole).
            if (gap >= 12.0 and lead[0]["x0"] <= 0.1 * page_w
                    and cut_at not in cuts):
                cuts.append(cut_at)
                cuts.sort()
        if not cuts:
            out.append(ln)
            continue
        buckets: list[list] = [[] for _ in range(len(cuts) + 1)]
        for c in chars:
            mid = (c["x0"] + c["x1"]) / 2
            for i, x in enumerate(cuts):
                if mid < x:
                    buckets[i].append(c)
                    break
            else:
                buckets[-1].append(c)
        pieces = [b for b in buckets if any((c.get("text") or "").strip() for c in b)]
        if len(pieces) < 2:
            out.append(ln)
            continue
        n_split += 1
        row_key = ln.get("_row") or id(ln)
        for b in pieces:
            piece = dict(ln)
            piece["chars"] = b
            piece["x0"] = min(c["x0"] for c in b)
            piece["x1"] = max(c["x1"] for c in b)
            piece["text"] = "".join(c.get("text") or "" for c in b)
            piece["_row"] = row_key
            piece.setdefault("_col", None)
            out.append(piece)
    if n_split:
        event("column-gap-split", f"split {n_split} rows at column gaps")
    return out


def build_page(page, page_no: int, id_start: int) -> PageModel:
    pm = PageModel(number=page_no, width=float(page.width),
                   height=float(page.height))

    chars = page.chars
    # FIRST: a lying /Descent moves a whole face down the page, and every
    # later repair (and pdfplumber's own 3pt row clustering) reads `top`.
    quirks.normalize_font_descent(chars, pm.event)
    quirks.drop_white_glyphs(chars, pm.event)
    quirks.decode_cid_glyphs(chars, pm.event)
    quirks.drop_micro_glyphs(chars, pm.event)
    quirks.drop_overstruck(chars, pm.event)
    quirks.snap_displaced_fragments(chars, pm.event)

    # Rotated glyphs: furniture by orientation, surfaced not disappeared.
    # Assembled in the PDF's own char order — sorted by position, sideways
    # text mirrors ('Thousands' -> 'sdnasuohT').
    rot = [c for c in chars if c.get("upright", True) is False]
    if rot:
        pm.rotated_text = "".join((c.get("text") or "") for c in rot).strip()
        pm.event("rotated-text", f"{len(rot)} sideways glyphs captured")

    pm.h_rules, pm.v_rules, pm.has_diagonal = collect_rules(page, page_no)

    raw = _text_lines(page)
    raw = quirks.merge_interleaved(raw, pm.event)
    raw = _split_at_vrules(raw, pm.v_rules, pm.event)
    raw = _split_wide_gaps(raw, pm.event)
    quirks.tag_underlined_chars(page.rects, raw)

    # A superscript footnote marker raises a line's measured top (~1.5pt at
    # 13pt leading), which shrinks the gap above it below the tight band and
    # splits the paragraph at the marker (ca3 then DISCARDED the fragment).
    # A line's top is where its dominant-size glyphs sit.
    for ln in raw:
        printable = [c for c in (ln.get("chars") or [])
                     if (c.get("text") or "").strip()]
        if len(printable) < 3:
            continue
        from collections import Counter as _Counter
        sizes = _Counter(round(c.get("size", 0) or 0, 1) for c in printable)
        mode = sizes.most_common(1)[0][0]
        dom_tops = [c["top"] for c in printable
                    if round(c.get("size", 0) or 0, 1) >= mode - 0.5]
        if dom_tops:
            true_top = min(dom_tops)
            if true_top - ln["top"] > 0.5:
                ln["top"] = true_top

    raw.sort(key=lambda l: (l["top"], l["x0"]))
    row_ids: dict = {}
    for i, ln in enumerate(raw):
        row = ln.get("_row")
        if row is not None:
            row = row_ids.setdefault(row, len(row_ids))
        pm.lines.append(Line(
            id=id_start + i, page=page_no,
            x0=float(ln["x0"]), x1=float(ln["x1"]),
            top=float(ln["top"]), bottom=float(ln["bottom"]),
            chars=ln.get("chars") or [],
            col=ln.get("_col"), row=row,
        ))

    upright = [c for c in chars if c.get("upright", True) is not False]
    pm.ink_chars = sum(1 for c in upright if (c.get("text") or "").strip())
    pm.cid_chars = sum(1 for c in upright
                       if (c.get("text") or "").startswith("(cid:"))
    area = pm.width * pm.height or 1.0
    covered = 0.0
    for img in page.images:
        w = max(0.0, min(img["x1"], pm.width) - max(img["x0"], 0.0))
        h = max(0.0, min(img["bottom"], pm.height) - max(img["top"], 0.0))
        covered += w * h
        pm.images.append(ImageRef(page=page_no, x0=img["x0"], x1=img["x1"],
                                  top=img["top"], bottom=img["bottom"],
                                  name=str(img.get("name") or "")))
    pm.image_area = min(covered / area, 1.0)
    return pm


def build_pdf(path: str) -> PdfModel:
    model = PdfModel(path=str(path))
    with pdfplumber.open(path) as pdf:
        next_id = 0
        for i, page in enumerate(pdf.pages, start=1):
            pm = build_page(page, i, next_id)
            next_id += len(pm.lines)
            model.pages.append(pm)
    return model
