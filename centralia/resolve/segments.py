"""Line grouping: lines -> typed segments (notice/blockquote/body/single/
spaced), measured-first.

Gap bands derive from the DOCUMENT's own leading whenever it was measurable
(0.45/0.85/1.5 x lead — the constants are only the fallback for documents too
small to measure). Every consumer reads the SAME bands: disagreement at band
edges is what used to shred segments (cafc's 14pt lead ON the old band edge).

Blockquote-by-geometry (a both-margins-indented multi-line run is one quote,
whatever its leading) is ON by default — the old system kept it off only for
the Alabama byte-fidelity lock, which is gone.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Callable

from ..geometry import DocGeometry, line_alignment
from ..pdfio.model import Line
from ..pdfio.rules import is_typed_rule

# Fallback constants (floors of the old system) — used only with no measured
# lead. A body line whose x0 exceeds rail + PARA_INDENT_MIN starts a
# paragraph; INDENT_STEP is one typographic indent stop.
GAP_TIGHT_MAX = 16.0
GAP_SINGLE_MAX = 22.0
GAP_DOUBLE_MAX = 40.0
PARA_INDENT_MIN = 28.0
INDENT_STEP = 36.0
DEFAULT_RAIL = 72.0


@dataclass(frozen=True)
class GapBands:
    tight: float
    single: float
    double: float

    def bucket(self, gap: float | None) -> str | None:
        if gap is None:
            return None
        if gap < self.tight:
            return "tight"
        if gap < self.single:
            return "single"
        if gap < self.double:
            return "double"
        return "boundary"


def gap_bands(geom: DocGeometry | None) -> GapBands:
    lead = geom.lead if geom else None
    if lead and lead <= GAP_SINGLE_MAX:
        return GapBands(0.45 * lead, 0.85 * lead, 1.5 * lead)
    return GapBands(GAP_TIGHT_MAX, GAP_SINGLE_MAX, GAP_DOUBLE_MAX)


@dataclass
class Segment:
    page: int
    lines: list[Line]
    kind: str        # notice | blockquote | body | single | spaced |
                     # separator | table


class Segmenter:
    def __init__(self, geom: DocGeometry | None, page_width: float,
                 is_author_line: Callable[[str], bool] | None = None,
                 para_indent_min: float = 12.0,
                 tables: dict[int, list] | None = None):
        # The DRAWN tables of each page (pdfio.TableGrid), by page number.
        # A court that rules a grid has already said what its cells are:
        # the lines inside one are read as a table, and the prose above and
        # below it never joins across it.
        self.tables = tables or {}
        self.geom = geom
        self.page_width = page_width
        self.bands = gap_bands(geom)
        self.is_author_line = is_author_line or (lambda text: False)
        self.rail = max(DEFAULT_RAIL, geom.body_x0) if geom else DEFAULT_RAIL
        self.para_indent_min = para_indent_min
        self.right_edge = (min(page_width - DEFAULT_RAIL, geom.right_x1)
                           if geom else page_width - DEFAULT_RAIL)

    # ---- per-line signals --------------------------------------------------

    def _zone(self, prev_top, top, next_top) -> str:
        gb = self.bands.bucket((top - prev_top) if prev_top is not None else None)
        ga = self.bands.bucket((next_top - top) if next_top is not None else None)
        for want in ("tight", "single", "double"):
            if gb == want or ga == want:
                return want
        return "isolated"

    def _deep_indent_flags(self, lines: list[Line]) -> list[bool]:
        """Is this line a BLOCK-QUOTE left edge (vs a first-line indent)?
        A quote holds its edge for >=2 consecutive lines; a lone deep line is
        a paragraph opening. Boundary measured from the document's own body
        column."""
        deep_x = self.rail + 1.5 * INDENT_STEP
        raw = [l.x0 >= deep_x for l in lines]
        out = []
        for i, d in enumerate(raw):
            if d:
                d = any(0 <= j < len(lines) and raw[j]
                        and abs(lines[j].x0 - lines[i].x0) <= 3
                        for j in (i - 1, i + 1))
            out.append(d)
        return out

    def is_indented_blockquote(self, seg: list[Line]) -> bool:
        """Multi-line, indented on BOTH margins, consistent flush-left edge
        (>=2 lines share it — rejects centered headings), left edge modest
        (< 40% of the page — rejects signatures)."""
        if len(seg) < 2:
            return False
        left_min = self.rail + PARA_INDENT_MIN
        x0s = [l.x0 for l in seg]
        x1s = [l.x1 for l in seg]
        if not (left_min <= min(x0s) <= self.page_width * 0.4
                and max(x1s) <= self.right_edge - 24):
            return False
        edge = min(x0s)
        return sum(1 for x in x0s if abs(x - edge) <= 3) >= 2

    def _is_quote_like(self, seg: list[Line]) -> bool:
        """Wholly inside the quote measure — also accepts one-line and
        heading-bearing segments so a quoted statute keeps one container."""
        if not seg:
            return False
        quote_left = self.rail + 1.5 * PARA_INDENT_MIN
        quote_right = self.right_edge - 24
        left = min(l.x0 for l in seg)
        if left > self.page_width * 0.4:
            return False
        if all(l.all_bold for l in seg):
            return False
        return left >= quote_left and max(l.x1 for l in seg) <= quote_right

    def _hanging_marker(self, lines: list[Line], i: int) -> bool:
        """Is this line the MARKER of a hanging-indent row — the page's own
        paragraph mark?

        A court that numbers its paragraphs sets the number at the rail and
        the paragraph's first line out beyond it, one visual row split at a
        column-wide gap ('¶1' x0=108 x1=125 beside its text at x0=180 —
        ariz; '{6' x0=72 x1=87 beside its text at x0=109 — the same layout
        through virginislands' OCR). Vertical space is NOT a reliable mark
        of it: ariz leaves 8pt extra above the row and virginislands leaves
        none, so on the second the whole page reads as one continuous flow
        and every numbered paragraph joins the one above it. The ROW's own
        shape is the mark, so measure that instead — a narrow piece AT the
        rail with the row's next piece set out an indent from it.
        """
        line = lines[i]
        if line.row is None or (i and lines[i - 1].row == line.row):
            return False
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt is None or nxt.row != line.row:
            return False
        return (line.x1 - line.x0 <= INDENT_STEP
                and abs(line.x0 - self.rail) <= INDENT_STEP / 2
                and nxt.x0 >= line.x1 + 12.0
                and nxt.x0 >= self.rail + PARA_INDENT_MIN)

    # ---- segmentation ------------------------------------------------------

    def _page_bands(self, lines: list[Line]) -> GapBands:
        """Per-PAGE leading, measured on the page's own leftmost recurring
        rail, taking the LARGEST recurring gap — a stapled decision sets each
        writing to its own measure, and a counsel/footnote block leads
        tighter and can outnumber body on a page (ca2/waldman; ca9 memos
        fragmented at 10–17 blocks/page under document-wide bands)."""
        from collections import Counter
        rail_counts = Counter(round(l.x0) for l in lines
                              if l.width > 100)
        if not rail_counts:
            return self.bands
        rail = min(x for x, n in rail_counts.items() if n >= 2) \
            if any(n >= 2 for n in rail_counts.values()) else None
        if rail is None:
            return self.bands
        on_rail = sorted((l for l in lines if abs(round(l.x0) - rail) <= 3),
                         key=lambda l: l.top)
        gaps = Counter()
        for a, b in zip(on_rail, on_rail[1:]):
            g = round(b.top - a.top)
            if 5 < g < 60:
                gaps[g] += 1
        recurring = [g for g, n in gaps.items() if n >= 3]
        # A recurring gap far beyond the rail's own type size is PARAGRAPH
        # SPACING, not leading — conn's 8pt apparatus blocks recur at ~28pt
        # breaks, and reading that as the page's lead reclassified the 11pt
        # opinion under it as reduced-type notice.
        sizes = [l.size for l in on_rail if l.size]
        if sizes:
            cap = 1.9 * median(sizes)
            recurring = [g for g in recurring if g <= cap]
        if not recurring:
            return self.bands
        lead = float(max(recurring))
        if lead <= GAP_SINGLE_MAX * 2:
            return GapBands(0.45 * lead, 0.85 * lead, 1.5 * lead)
        return self.bands

    def segment_page(self, lines: list[Line], page: int) -> list[Segment]:
        lines = sorted((l for l in lines if l.plain.strip()),
                       key=lambda l: (l.top, l.x0))
        if not lines:
            return []
        page_bands = self._page_bands(lines) if page > 1 else self.bands
        saved = self.bands
        self.bands = page_bands
        try:
            grids = [g for g in (self.tables.get(page) or ())
                     if any(g.holds(l) for l in lines)]
            if grids:
                return self._segment_around_tables(lines, page, grids)
            return self._segment_page_inner(lines, page)
        finally:
            self.bands = saved

    def _segment_around_tables(self, lines: list[Line], page: int,
                               grids: list) -> list[Segment]:
        """One segment per drawn table, the page's prose segmented in the
        runs BETWEEN them.

        The cells are not paragraphs and the grid is not leading: read as
        prose, a two-column assets table came out as 16 blocks — every cell
        its own paragraph, every stub head an h3, in reading order down one
        column and then the other (ncctapp/ahdi, the user, 2026-08-20)."""
        held: dict[int, list[Line]] = {}
        prose: list[Line] = []
        for line in lines:
            for i, g in enumerate(grids):
                if g.holds(line):
                    held.setdefault(i, []).append(line)
                    break
            else:
                prose.append(line)
        bands = sorted(((grids[i].top, grids[i].bottom, i) for i in held),
                       key=lambda b: b[0])
        out: list[Segment] = []
        run: list[Line] = []
        k = 0
        for line in prose:
            while k < len(bands) and line.top >= bands[k][1]:
                if run:
                    out.extend(self._segment_page_inner(run, page))
                    run = []
                out.append(Segment(page, held[bands[k][2]], "table"))
                k += 1
            run.append(line)
        if run:
            out.extend(self._segment_page_inner(run, page))
        while k < len(bands):
            out.append(Segment(page, held[bands[k][2]], "table"))
            k += 1
        return out

    def _segment_page_inner(self, lines: list[Line], page: int) -> list[Segment]:
        # Pieces of ONE VISUAL ROW share a baseline and contribute a ZERO
        # gap between them; measured per list neighbour that reads 'tight'
        # against the row leading below and broke the segment after every
        # marker-plus-text row ('¶1' beside its paragraph's first line —
        # ariz). A row's zone is a property of the ROW, so measure it from
        # the distinct baselines, not from the sorted line list.
        zones = []
        tops = sorted({l.top for l in lines})
        _prev = {t: (tops[k - 1] if k else None) for k, t in enumerate(tops)}
        _next = {t: (tops[k + 1] if k + 1 < len(tops) else None)
                 for k, t in enumerate(tops)}
        for line in lines:
            zones.append(self._zone(_prev[line.top], line.top,
                                    _next[line.top]))
        deep = self._deep_indent_flags(lines)

        segments: list[list[Line]] = []
        current: list[Line] = []
        prev_i = None
        prev_size = prev_align = prev_top = prev_zone = None
        for i, line in enumerate(lines):
            size = line.size
            align = line_alignment(line, self.page_width, self.geom)
            sep = is_typed_rule(line.plain)
            zone = zones[i]
            if sep:
                if current:
                    segments.append(current)
                    current = []
                segments.append([line])
                prev_size, prev_align, prev_top, prev_zone = (
                    size, align, line.top, None)
                prev_i = i
                continue
            if current:
                gap = line.top - prev_top
                big_gap = gap > self.bands.double
                size_changed = abs(size - prev_size) >= 1.0
                # Only a line bold THROUGHOUT is structural; a bold case name
                # inside a citation is prose.
                bold_changed = line.all_bold != current[-1].all_bold
                align_changed = align != prev_align
                if {prev_align, align} == {"C", "L"}:
                    # A short line reads 'centered' by drift; only a line well
                    # RIGHT of the paragraph's own margin is a real heading.
                    suspect = line if align == "C" else current[-1]
                    neighbour = current[-1] if align == "C" else line
                    above = [l.x0 for l in current if l is not suspect]
                    para_left = (max(self.rail, min(above)) if above
                                 else neighbour.x0)
                    align_changed = suspect.x0 > para_left + 2 * INDENT_STEP
                zone_changed = prev_zone is not None and zone != prev_zone
                col_changed = line.col != current[-1].col
                author_break = self.is_author_line(line.plain.strip())
                prev_deep = bool(prev_i is not None and deep[prev_i])
                this_deep = bool(deep[i])
                indent_changed = prev_deep != this_deep
                if prev_deep and this_deep:
                    align_changed = False
                # A PIECE OF THE SAME VISUAL ROW continues its row. pdfio
                # already identified the pieces it split out of one row
                # (`Line.row`, shared by the pieces of that row), so this is
                # its measurement, not a tolerance. Every TYPOGRAPHIC test
                # below reads a row's own pieces as a change of element — a
                # bold '¶1' beside its paragraph's first line came back as
                # its own segment and rendered as a heading (ariz: 2,706 of
                # them; arizctapp: 1,345). The COLUMN break and the byline
                # break still stand: a rule-split row is two columns, and a
                # byline piece opens a writing wherever it sits.
                same_row = (line.row is not None
                            and line.row == current[-1].row)
                if same_row:
                    big_gap = size_changed = bold_changed = False
                    align_changed = zone_changed = indent_changed = False
                # The row's own shape opens the element the page marks.
                marker = self._hanging_marker(lines, i)
                if (big_gap or size_changed or bold_changed or align_changed
                        or zone_changed or col_changed or author_break
                        or indent_changed or marker):
                    segments.append(current)
                    current = []
            current.append(line)
            prev_i = i
            prev_size, prev_align, prev_top, prev_zone = (
                size, align, line.top, zone)
        if current:
            segments.append(current)
        return [Segment(page, seg, self.classify(seg)) for seg in segments]

    def classify(self, seg: list[Line]) -> str:
        """notice / blockquote / body / single / spaced / separator."""
        if len(seg) == 1 and is_typed_rule(seg[0].plain):
            return "separator"
        if self._is_quote_like(seg):
            return "blockquote"
        if len(seg) == 1:
            if seg[0].plain.strip() in ("...", "…", ". . ."):
                return "blockquote"   # omitted portion inside a quote
            return "single"
        # Same-top row-split pieces contribute ZERO gaps — that's a column
        # split, not leading ('WILKINS, Circuit Judge:' | 'Congress affirmed
        # the' share a row and read as reduced-leading notice otherwise).
        gaps = [g for g in (b.top - a.top for a, b in zip(seg, seg[1:]))
                if g > 2.0]
        if not gaps:
            return "single"
        med = median(gaps)
        if med < self.bands.tight:
            kind = "notice"
        elif med < self.bands.single:
            kind = "blockquote"
        elif med < self.bands.double:
            kind = "body"
        else:
            kind = "spaced"
        if kind in ("notice", "body") and self.is_indented_blockquote(seg):
            kind = "blockquote"
        return kind
