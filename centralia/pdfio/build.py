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
from .tables import find_grids, row_edge_rects
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
                       and any(c["x0"] >= v.x + 0.5 for c in chars)
                       # A RULE THAT PASSES THROUGH A GLYPH IS NOT DIVIDING
                       # THE ROW. A column divider runs down whitespace; where
                       # it crosses a letter's own box the row is not two
                       # cells, and cutting it lands mid-word. oked's
                       # 28692.970.0 closes its caption rule at y249.62 and
                       # sets 'OPINION AND ORDER' at y251.40 — inside the +2
                       # slack, crossing the 'A' of 'AND' (x297.3-305.9 over
                       # a rule at x305.57), so the title read as 'OPINION A'
                       # / 'ND ORDER' on two rows (the user, 2026-08-22).
                       and not any(c["x0"] < v.x < c["x1"]
                                   and (c.get("text") or "").strip()
                                   for c in chars)})
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


def build_page(page, page_no: int, id_start: int,
               mac_fonts=frozenset()) -> PageModel:
    pm = PageModel(number=page_no, width=float(page.width),
                   height=float(page.height))

    chars = page.chars
    # FIRST: a lying /Descent moves a whole face down the page, and every
    # later repair (and pdfplumber's own 3pt row clustering) reads `top`.
    quirks.normalize_font_descent(chars, pm.event)
    quirks.drop_white_glyphs(chars, pm.event)
    quirks.decode_cid_glyphs(chars, pm.event, mac_fonts)
    # AFTER the decode, never before: the decode drops the .notdef high
    # bytes a two-byte code arrives with, and the order pass must lay out
    # the glyphs that are left.
    quirks.restore_zero_advance_order(chars, pm.event)
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

    # A DRAWN table is read here, in the one pass, because its own rules
    # change how the page reads twice over: the lines inside it are cells
    # rather than paragraphs, and its cell borders are not underlines.
    pm.tables = find_grids(pm.h_rules, pm.v_rules, raw, page_no)
    if pm.tables:
        pm.event("table", ", ".join(
            f"{g.n_rows}x{g.n_cols} at y{g.top:.0f}" for g in pm.tables))
    _cell_rects = row_edge_rects(pm.tables, page.rects)
    quirks.tag_underlined_chars(page.rects, raw, skip=_cell_rects)

    # A HIGHLIGHTER'S FILL is emphasis the text layer does not carry — read it
    # back onto the glyphs standing on it, so `<mark>` survives into the
    # rendering the way `<u>` does.
    _n_hl = quirks.tag_highlighted_chars(page.rects, raw)
    if _n_hl:
        pm.event("highlight", f"{_n_hl} rows carry a highlighter's fill")

    # A REDACTION is drawn, not written — read it back into its line. Runs
    # after the splits on purpose: a blacked-out name always touches the words
    # beside it, so it never needs to make a column, and injecting it earlier
    # could only ever invent one.
    quirks.insert_redaction_boxes(page.rects, raw, pm.event, skip=_cell_rects)
    # …and the bar that is a GLYPH rather than a rect (see convert_bar_glyphs).
    quirks.convert_bar_glyphs(raw, pm.event)

    # A stacked one-glyph column is a RAIL. Tagged here so nothing downstream
    # has to re-measure it — the footnote resolver in particular, which would
    # otherwise read a '§' rail glyph as a note's label.
    quirks.tag_rail_glyphs(raw, pm.event)

    # A superscript footnote marker raises a line's measured top (~1.5pt at
    # 13pt leading), which shrinks the gap above it below the tight band and
    # splits the paragraph at the marker (ca3 then DISCARDED the fragment).
    # A line's top is where its dominant-size glyphs sit.
    # …BUT NOT FOR A PIECE SPLIT OUT OF A ROW. `_row` marks the pieces of
    # one visual line, and their SHARED top is what keeps them in reading
    # order. Recomputing each piece's own top reorders them: Colorado numbers
    # its paragraphs in the left margin ('¶ 10' at x0 57.6, 12pt, against a
    # 14pt body indented to 108.0), the wide-gap split makes the marker a
    # piece of its paragraph's first row, and its 12pt glyphs sit 1.6pt lower
    # than the 14pt text. Re-topped, the marker sorted AFTER the text it
    # opens and rendered mid-sentence — 'Following a forcible entry and
    # detainer hearing, the court ¶ 11 found that tenant was …' (the user,
    # 2026-08-20). 45 of the 62 blocks of one record were spliced that way.
    #
    # The case this pass exists for is a WHOLE line whose measured top a
    # superscript raised, which carries no `_row` and is untouched by this.
    for ln in raw:
        if ln.get("_row") is not None:
            continue
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
    pm.fonts = {c.get("fontname") or "" for c in upright}
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
        # WHOSE ORDERING, ASKED ONCE FOR THE WHOLE PAPER. A subset font
        # addressed by glyph id has to prove itself before its text is
        # rewritten, and the proof is words — which one page may not have.
        # texapp's docketing statement proves its font on page 1 and carries
        # too little prose to prove it again on pages 2-9; pasuperct/holbrook
        # has exactly one broken page and it reads 'J-S15004-26 / - 23 - /
        # Date: 7/29/2026'. See `quirks.mac_ordered_fonts`.
        mac_fonts = quirks.mac_ordered_fonts(p.chars for p in pdf.pages)
        next_id = 0
        for i, page in enumerate(pdf.pages, start=1):
            pm = build_page(page, i, next_id, mac_fonts)
            next_id += len(pm.lines)
            model.pages.append(pm)
    return model
