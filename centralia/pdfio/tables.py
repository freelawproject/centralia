"""Ruled-table recovery: the grid the PDF DRAWS, read off the collected rules.

A table is proved by INK, never by alignment. pdfplumber's ``find_tables``
reads an indented blockquote as a two-column table (four of them on one page
of ncctapp/ahdi) and reads a spanning sub-head as an extra column edge; both
are guesses about text position. What a court actually draws is a box with
rules inside it, and `collect_rules` has already merged every piece of every
rule on the page. Intersecting those rules gives the cells exactly.

The reading is deliberately narrow: at least two columns AND two rows, both
bounded by drawn rules, with ink in two different columns. Everything else
stays prose. A one-column ruled box is a boxed notice, not a table; a pair
of rules with nothing between them is a caption fence.
"""

from __future__ import annotations

from statistics import median

from .model import DrawnRule, TableGrid, VRule

# A vertical shorter than one line of type is a tick or a mark, not a box
# edge. Two rules within EDGE_MERGE of each other are one rule drawn twice
# (every rule in ncctapp's grid is a double stroke).
MIN_V_HEIGHT = 12.0
EDGE_MERGE = 3.0
# Narrower than this is not a column, shorter than this is not a row: both
# are the double-stroke of one rule that survived the merge.
MIN_COL_WIDTH = 18.0
MIN_ROW_HEIGHT = 5.0
# A row of a table is a line of type or a few; a band this tall is a fenced
# region of the page — a caption box, a pleading frame — not a table row.
MAX_ROW_HEIGHT = 150.0
MAX_MEDIAN_ROW = 70.0
# Share of the box's height a rule must run to count as a column edge.
FULL_EDGE = 0.7
# A horizontal rule belongs to a box when it runs most of the box's width.
H_SPAN_MIN = 0.55
MIN_H_WIDTH = 40.0


def _merge(values: list[float]) -> list[float]:
    """Collapse rules drawn twice at one position into one edge."""
    out: list[float] = []
    for v in sorted(values):
        if out and v - out[-1] <= EDGE_MERGE:
            continue
        out.append(v)
    return out


def _v_groups(v_rules: list[VRule]) -> list[list[VRule]]:
    """Verticals that share a vertical extent are edges of ONE box."""
    groups: list[list[VRule]] = []
    for v in sorted((r for r in v_rules if r.bottom - r.top >= MIN_V_HEIGHT),
                    key=lambda r: (r.top, r.x)):
        for g in groups:
            top = min(r.top for r in g)
            bottom = max(r.bottom for r in g)
            overlap = min(bottom, v.bottom) - max(top, v.top)
            if overlap >= 0.6 * min(bottom - top, v.bottom - v.top):
                g.append(v)
                break
        else:
            groups.append([v])
    return groups


def _rows_and_cols(group: list[VRule], h_rules: list[DrawnRule]):
    """The drawn edges of one box: (col_edges, row_edges) or None."""
    vx = _merge([v.x for v in group])
    top = min(v.top for v in group)
    bottom = max(v.bottom for v in group)
    span = max(vx) - min(vx)
    if span <= MIN_COL_WIDTH:
        return None
    # A COLUMN RULE RUNS THE HEIGHT OF THE BOX. Two of them must, or this is
    # not a box: a vector SIGNATURE is a bundle of thin strokes, and its
    # bounding pair plus the typed '____' rule beneath it measured as a 3x4
    # grid holding the judge's name (ilnd/477258 p36 — no table on the page
    # at all).
    if sum(1 for v in group
           if v.bottom - v.top >= FULL_EDGE * (bottom - top)) < 2:
        return None
    band = [h for h in h_rules
            if top - 4.0 <= h.top <= bottom + 4.0
            and h.width >= MIN_H_WIDTH
            and h.x0 >= min(vx) - 6.0 and h.x1 <= max(vx) + 6.0
            and (min(h.x1, max(vx)) - max(h.x0, min(vx))) >= H_SPAN_MIN * span]
    if len(band) < 3:
        return None
    x0 = min(min(vx), min(h.x0 for h in band))
    x1 = max(max(vx), max(h.x1 for h in band))
    col_edges = _merge([x0, x1] + vx)
    row_edges = _merge([h.top for h in band])
    if len(col_edges) < 3 or len(row_edges) < 3:
        return None
    heights = [b - a for a, b in zip(row_edges, row_edges[1:])]
    widths = [b - a for a, b in zip(col_edges, col_edges[1:])]
    if min(widths) < MIN_COL_WIDTH or min(heights) < MIN_ROW_HEIGHT:
        return None
    if max(heights) > MAX_ROW_HEIGHT or median(heights) > MAX_MEDIAN_ROW:
        return None
    return tuple(col_edges), tuple(row_edges)


def _cell_of(grid: TableGrid, x0: float, x1: float, top: float,
             bottom: float) -> tuple[int, int] | None:
    """Which cell a text line sits in, by its own left edge and baseline."""
    mid_y = (top + bottom) / 2
    row = col = None
    for i, (a, b) in enumerate(zip(grid.row_edges, grid.row_edges[1:])):
        if a - 2.0 <= mid_y < b:
            row = i
            break
    x_probe = x0 + 1.0
    for i, (a, b) in enumerate(zip(grid.col_edges, grid.col_edges[1:])):
        if a <= x_probe < b:
            col = i
            break
    if row is None or col is None:
        return None
    return row, col


def find_grids(h_rules: list[DrawnRule], v_rules: list[VRule],
               raw_lines: list[dict], page: int) -> list[TableGrid]:
    """Ruled tables on one page, top-down. ``raw_lines`` are the page's text
    lines as dicts (pre-Line); a grid survives only with ink in two columns
    and two rows — a fence with prose beside it is not a table."""
    out: list[TableGrid] = []
    for group in _v_groups(v_rules):
        found = _rows_and_cols(group, h_rules)
        if found is None:
            continue
        col_edges, row_edges = found
        grid = TableGrid(page=page, col_edges=col_edges, row_edges=row_edges)
        cells = set()
        for ln in raw_lines:
            if not "".join((c.get("text") or "") for c in
                           (ln.get("chars") or ())).strip():
                continue
            where = _cell_of(grid, float(ln["x0"]), float(ln["x1"]),
                             float(ln["top"]), float(ln["bottom"]))
            if where is not None:
                cells.add(where)
        if len({c for _, c in cells}) < 2 or len({r for r, _ in cells}) < 2:
            continue
        out.append(grid)
    return sorted(out, key=lambda g: g.top)


def row_edge_rects(grids: list[TableGrid], rects: list) -> set[int]:
    """Ids of the hairline rects that are a grid's own ROW RULES.

    A cell's bottom border sits exactly where an underline sits, so the
    underline pass tagged every cell of ncctapp's assets table underlined.
    A border is not emphasis: the rules that draw a table are withheld from
    that pass."""
    out: set[int] = set()
    if not grids:
        return out
    for r in rects:
        if r.get("height", 0) >= 2:
            continue
        for g in grids:
            if (g.x0 - 6.0 <= r["x0"] and r["x1"] <= g.x1 + 6.0
                    and any(abs(r["top"] - y) <= EDGE_MERGE
                            for y in g.row_edges)):
                out.add(id(r))
                break
    return out
