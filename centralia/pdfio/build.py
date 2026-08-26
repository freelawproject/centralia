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

from collections import Counter

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
# A TWO-COLUMN BODY. How many rows must carry prose on BOTH sides of one
# gutter before the page is read down its columns instead of across them.
# Six is the floor because a CAPTION is also two pieces at a steady cut —
# party name against docket, either side of the rail — and no caption has
# six rows whose right-hand cell is as long as its left.
_COLUMN_ROWS_MIN = 6
# TEXT CONVERTED TO OUTLINES. How many glyph-sized filled paths must stand
# on one baseline before the run is called a row of drawn text. Twelve is a
# short line and far more than any rule, box corner or bullet draws.
_OUTLINE_ROW_MIN = 12
# Both cells must reach this much of the page's own half-measure. Measured
# on ncmd/…100664.528.0: its columns run 219pt and 216pt against a
# half-measure of 234 (94%), while the caption's widest right-hand cell is
# a lone rail glyph at 7%.
_COLUMN_CELL_FILL = 0.55


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


def _outlined_rows(curves: list) -> int:
    """Rows of TEXT DRAWN AS OUTLINES, which no text layer holds.

    A chambers that flattens its headings to vector paths leaves nothing to
    extract: the glyphs arrive as small filled curves, twelve to sixty of
    them on a shared baseline, and every text-layer reader — poppler
    included — returns blank where the words are. Counted so the document
    can SAY so instead of publishing with no court and no title.
    """
    marks = [c for c in curves
             if c.get("fill")
             and 0.8 <= (c["x1"] - c["x0"]) <= 40.0
             and 2.0 <= (c["bottom"] - c["top"]) <= 30.0]
    if len(marks) < _OUTLINE_ROW_MIN:
        return 0
    baselines: dict = {}
    for c in marks:
        baselines.setdefault(round(c["bottom"] / 3.0), []).append(c)
    return sum(1 for run in baselines.values()
               if len(run) >= _OUTLINE_ROW_MIN)


def _row_pieces(chars: list, page_w: float) -> list[list]:
    """One visual row's chars, cut into column pieces.

    WIDEST GAP FIRST, THEN MEASURE AGAIN. The threshold is measured against
    the line's own word gap — but a row that spans two columns has two word
    gaps in it, and one figure cannot stand for both. ncmd sets a 216pt
    justified column beside an unjustified one, so a row of
    ncmd/…100104.24.0 came in with a 36.3pt gutter, three 26pt
    justification stretches and 8.6pt spaces, while `inferred_space_gap`
    read the LEFT column's 3.12pt and put the floor at 18: all four gaps
    cleared it and the citation came apart into one piece per word, leaving
    'v.' alone on its own line to be promoted to a heading (the user,
    2026-08-25: 'it used the v. to split new lines? like its headmatter or
    somethign?').
    Cutting only at the widest gap and re-measuring each piece gives the
    justified column its own floor — 4 x 8.6 = 34.4pt, which its 26pt
    stretches do not reach — and leaves every row that has one cut to make
    splitting exactly as it did before.
    """
    printable = [c for c in chars if (c.get("text") or "").strip()]
    if len(printable) < 2:
        return [chars]
    # AN ASTERISK BAND IS ALL GAP. A chambers that closes its caption with
    # '*   *   *   *   *' sets those asterisks a column-width apart by
    # design, so every one of its own gaps clears the floor and the row came
    # apart into one line per asterisk — twelve of them on
    # mdd/…417774.108.0. Shredded, the band is no longer the band: the ECF
    # reader's closer test (`_is_asterisk_band`) never matches a lone '*',
    # the caption runs on to its 55% ceiling, and the shards come back as
    # caption cells and party text (the user, 2026-08-25: 'the astericks
    # rail should be repsected in teh heamdatter as a full line acorss').
    # A row that is nothing but asterisks has no columns to find.
    if len(printable) >= 3 and all(
            (c.get("text") or "") == "*" for c in printable):
        return [chars]

    gap_floor = max(_COLUMN_GAP_MIN, 4.0 * inferred_space_gap(chars))
    widest, cut_at = 0.0, None
    for a, b in zip(printable, printable[1:]):
        gap = b["x0"] - a["x1"]
        if gap >= gap_floor and gap > widest:
            widest, cut_at = gap, (a["x1"] + b["x0"]) / 2

    if cut_at is None:
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
            # MARGIN fragments only: the stationery number starts far left
            # of any text rail ('583 P.3d 553' opens a CITATION at the note
            # rail and must stay whole).
            if (nxt["x0"] - lead[-1]["x1"] >= 12.0
                    and lead[0]["x0"] <= 0.1 * page_w):
                cut_at = (lead[-1]["x1"] + nxt["x0"]) / 2

    if cut_at is None:
        return [chars]
    left = [c for c in chars if (c["x0"] + c["x1"]) / 2 < cut_at]
    right = [c for c in chars if (c["x0"] + c["x1"]) / 2 >= cut_at]
    if not any((c.get("text") or "").strip() for c in left) \
            or not any((c.get("text") or "").strip() for c in right):
        return [chars]
    return _row_pieces(left, page_w) + _row_pieces(right, page_w)


def _split_wide_gaps(raw_lines: list, event) -> list:
    """Split a visual row at a column-wide x-gap — two caption columns held by
    whitespace alone (the Open Range), a stamp beside a banner, a rail glyph
    between columns. The threshold is measured against the line's own word
    gap so justified prose never qualifies; see `_row_pieces`, which applies
    it one cut at a time so a row spanning two differently-set columns is
    judged by each column's own spacing."""
    out = []
    n_split = 0
    for ln in raw_lines:
        chars = sorted(ln.get("chars") or [], key=lambda c: c["x0"])
        pieces = _row_pieces(chars, float(ln.get("_page_width") or 612.0))
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


def _column_order(raw: list, event) -> list:
    """Reading order for a page whose BODY is set in two columns.

    THE PAGE SORTS BY (top, x0), which is the reading order of every page
    that has one column and the wrong one for a page that has two: the rows
    interleave and the prose comes back alternating between the columns —
    ncmd/…100664.528.0 read 'This matter comes before the Court /
    Amendment. United States ex rel. / on pending motions to seal filed at /
    Oberg v. Nelnet, Inc., 105 F.4th 161,' (the user, 2026-08-25: 'ncmd
    likes to sometimes publish two column opinions').

    The evidence is the page's own: the wide-gap splitter has already cut
    each row at its gutter, so a two-column page arrives as a stack of
    two-piece rows agreeing on one cut, each piece carrying most of a
    half-measure of prose. Where they do, the columns are emitted one after
    the other; a row that SPANS the gutter — the masthead, the paper's name,
    a full-measure heading — belongs to neither, so it closes the pair of
    columns above it and opens the next. That keeps a page that turns
    two-column halfway down in its own order, and leaves every one-column
    page exactly as it was.
    """
    rows: dict = {}
    for ln in raw:
        key = ln.get("_row")
        if key is not None:
            rows.setdefault(key, []).append(ln)
    pairs = []
    for pieces in rows.values():
        if len(pieces) != 2:
            continue
        a, b = sorted(pieces, key=lambda l: l["x0"])
        pairs.append(((a["x1"] + b["x0"]) / 2.0, a, b))
    if len(pairs) < _COLUMN_ROWS_MIN:
        return raw
    half = (max(l["x1"] for l in raw) - min(l["x0"] for l in raw)) / 2.0
    # THE GUTTER IS WHERE NOTHING IS WRITTEN, and it is not the middle of
    # any one row's gap: a row whose left cell ends early — the last line of
    # a paragraph — or whose right cell is indented moves that midpoint,
    # and clustering on it scattered ncmd/…102848.20.0's page 1 across
    # x275–x344 with only four rows in the mode, so the page read across the
    # gutter while pages 2–4 of the same order read down it. The column
    # edges are what hold still: the question to ask is which x EVERY wide
    # two-piece row leaves empty.
    wide_rows = [(a, b) for _c, a, b in pairs
                 if (a["x1"] - a["x0"]) >= _COLUMN_CELL_FILL * half
                 and (b["x1"] - b["x0"]) >= _COLUMN_CELL_FILL * half]
    if len(wide_rows) < _COLUMN_ROWS_MIN:
        return raw
    best_x, wide = None, []
    for x in sorted({round(b["x0"]) for _a, b in wide_rows}):
        hit = [(a, b) for a, b in wide_rows if a["x1"] <= x <= b["x0"]]
        if len(hit) > len(wide):
            best_x, wide = float(x), hit
    if best_x is None or len(wide) < _COLUMN_ROWS_MIN:
        return raw
    gutter = best_x

    # …AND WHAT THE ROW-BY-ROW SPLIT OVERCUT. `_row_pieces` judges one row
    # at a time against its own word gap, which cannot separate a gutter
    # from JUSTIFICATION: ncmd sets a 216pt column whose words are pushed
    # apart with explicit offsets rather than space glyphs, so the measured
    # space stays 3.12pt while the rendered stretch reaches 26pt — three
    # times a normal space and two-thirds of the real gutter. Row by row
    # there is nothing to tell them apart, and 'See Nemet Chevrolet, Ltd. v.
    # Consumeraffairs.com, Inc.' came apart into one piece per word with
    # 'v.' left alone on a line and promoted to a heading (the user,
    # 2026-08-25: 'it used the v. to split new lines? like its headmatter or
    # somethign?'). The gutter is a page fact, and the page has just stated
    # it: a two-column row has exactly two cells, so anything more is
    # justification and is put back.
    fused: dict = {}
    for pieces in rows.values():
        if len(pieces) < 3:
            continue
        for side in (0, 1):
            group = [p for p in pieces
                     if ((p["x0"] + p["x1"]) / 2 < gutter) == (side == 0)]
            if len(group) < 2:
                continue
            group.sort(key=lambda l: l["x0"])
            cs = sorted((c for p in group for c in (p.get("chars") or [])),
                        key=lambda c: c["x0"])
            whole = dict(group[0])
            whole["chars"] = cs
            whole["x0"] = min(c["x0"] for c in cs)
            whole["x1"] = max(c["x1"] for c in cs)
            whole["text"] = "".join(c.get("text") or "" for c in cs)
            fused[id(group[0])] = whole
            for p in group[1:]:
                fused[id(p)] = None
    if fused:
        raw = [fused.get(id(ln), ln) if id(ln) in fused else ln
               for ln in raw]
        raw = [ln for ln in raw if ln is not None]
        event("column-refuse",
              f"{sum(1 for v in fused.values() if v is None)} shards "
              f"put back into their column")

    ordered: list = []
    lefts: list = []
    rights: list = []

    def _flush() -> None:
        ordered.extend(lefts)
        ordered.extend(rights)
        lefts.clear()
        rights.clear()

    for ln in raw:                       # already in (top, x0) order
        if ln["x1"] <= gutter:
            lefts.append(ln)
        elif ln["x0"] >= gutter:
            rights.append(ln)
        else:
            _flush()
            ordered.append(ln)
    _flush()
    event("two-column",
          f"{len(wide)} rows read down a gutter at x{gutter:.0f}")
    return ordered


# Read a glyph's orientation off its MATRIX rather than pdfplumber's
# `upright`. Named so the two readings can be compared on one corpus.
ROTATION_FROM_MATRIX = True


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
    #
    # ORIENTATION IS THE MATRIX, NOT `upright`. pdfplumber decides `upright`
    # from the matrix's VERTICAL terms alone, so a glyph turned a quarter
    # turn about the other axis still answers True: cand sets its pleading
    # paper's margin legend sideways — 'United States District Court' and
    # 'Northern District of California' interleaved down the left edge — and
    # every one of its 61 glyphs reported upright. This test never fired,
    # and the fragments went into line assembly, where they WELD to the
    # pleading paper's line numbers ('uoC rof 13', 'cC 14', 'tatS siD 16')
    # and from there into the middle of the court's own sentences: '… the
    # motion i t la cC 14 requests the sealing of Exhibits G, K and Q' (the
    # user, 2026-08-25: 'needs to remove the sidebar numebrs and sideways
    # text'). Measured: 23 of cand's 27 records carry the legend.
    # A quarter turn puts the horizontal scale at zero and the shear at one,
    # so both terms are required — a degenerate all-zero matrix is not
    # evidence of anything and passes.
    def _sideways(c) -> bool:
        mx = c.get("matrix")
        if not mx or len(mx) < 2 or not ROTATION_FROM_MATRIX:
            return c.get("upright", True) is False
        return abs(mx[0]) < 0.01 and abs(mx[1]) > 0.01

    rot = [c for c in chars if _sideways(c)]
    if rot:
        pm.rotated_text = "".join((c.get("text") or "") for c in rot).strip()
        pm.event("rotated-text", f"{len(rot)} sideways glyphs captured")
        # …AND TAKEN OUT OF THE STREAM. Capturing them was only ever half of
        # it: left in `chars` they reach `extract_text_lines` below and are
        # read as body text. `pm.rotated_text` is the surfaced record — see
        # pipeline, which files it as a `Dropped` of kind 'rotated' — so
        # nothing is lost by removing them here.
        _rot_ids = {id(c) for c in rot}
        chars[:] = [c for c in chars if id(c) not in _rot_ids]

    pm.h_rules, pm.v_rules, pm.has_diagonal = collect_rules(page, page_no)
    pm.outlined_rows = _outlined_rows(page.curves)
    if pm.outlined_rows:
        pm.event("outlined-text",
                 f"{pm.outlined_rows} row(s) drawn as outlines, no text layer")

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
    # A FORM'S CHECKBOX FIRST, so a square is never mistaken for a bar.
    _ticks = quirks.insert_checkbox_glyphs(page.rects, page.curves, raw,
                                           pm.event, skip=_cell_rects)
    quirks.insert_redaction_boxes(page.rects, raw, pm.event,
                                  skip=_cell_rects | _ticks)
    # …and the bar that is a GLYPH rather than a rect (see convert_bar_glyphs).
    quirks.convert_bar_glyphs(raw, pm.event)
    # A FILLED-IN BLANK is a rule of '_' with the answer typed on top of it.
    # After the splits on purpose: the rule glyphs hold the row together, and
    # removing them first would open a column-wide gap where the unused tail
    # of the blank used to be.
    quirks.fill_rule_glyphs(raw, pm.event)

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
    raw = _column_order(raw, pm.event)
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
