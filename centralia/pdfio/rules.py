"""Drawn-rule collection: collect small, merge by y, THEN size-filter.

A full-width rule drawn as short strips otherwise reads as disjoint halves,
and a pleading rail drawn as a triple stroke reads as three rails. The same
visual rule may be a hairline RECT, a vector LINE, or a thin embedded IMAGE —
all three are collected.

`is_typed_rule` is the single definition of a rule TYPED as characters; the
segmentation, the caption fingerprint and the footnote resolver all defer to
it so they cannot disagree about what a rule is.
"""

from __future__ import annotations

from .model import DrawnRule, VRule

# Glyphs a typed horizontal rule is built from.
RULE_GLYPHS = "_-—–"
# A typed footnote separator admits the underscore and true dashes but NOT
# ASCII hyphen-minus: a run of '-' is how plain-text tables and ASCII dividers
# are drawn, and admitting one as a zone boundary is a guess.
TYPED_SEP_GLYPHS = "_-=—–―‒"
TYPED_SEP_ADMIT_GLYPHS = "_—–―‒"


def is_typed_rule(text: str, glyphs: str = RULE_GLYPHS) -> bool:
    """True if ``text`` is a horizontal rule TYPED as characters: a run of
    rule glyphs, optionally spaced out, optionally capped with an ``x`` at
    either end (the typewriter-era pleading-box corner:
    '-------------------x')."""
    t = (text or "").strip()
    if t[-1:] in ("x", "X"):
        t = t[:-1].rstrip()
    if t[:1] in ("x", "X"):
        t = t[1:].lstrip()
    if not t or any(c not in glyphs and c != " " for c in t):
        return False
    return sum(1 for c in t if c in glyphs) >= 4


def _merge_h_segments(pieces: list[tuple[float, float, float, str]],
                      page_no: int) -> list[DrawnRule]:
    """pieces: (top, x0, x1, source). Collect EVERY thin piece small, merge
    abutting chains at one y, THEN let consumers size-filter — a full-width
    rule drawn as short strips must never read as two disjoint halves."""
    pieces = sorted(pieces, key=lambda p: (round(p[0], 0), p[1]))
    merged: list[list] = []  # [top, x0, x1, source, strokes]
    for top, x0, x1, src in pieces:
        hit = None
        for m in merged:
            if abs(m[0] - top) < 2.5 and x0 <= m[2] + 6.0 and x1 >= m[1] - 6.0:
                hit = m
                break
        if hit is None:
            merged.append([top, x0, x1, src, 1])
        else:
            hit[1] = min(hit[1], x0)
            hit[2] = max(hit[2], x1)
            hit[4] += 1
            hit[0] = min(hit[0], top)
    return [DrawnRule(page=page_no, top=m[0], x0=m[1], x1=m[2],
                      source=m[3], strokes=m[4]) for m in merged]


def _merge_v_segments(pieces: list[tuple[float, float, float, str]],
                      page_no: int) -> list[VRule]:
    """pieces: (x, top, bottom, source). Chain y-stacked segments of ONE
    vertical (a 150pt rule drawn as five 30pt pieces). The x tolerance is
    deliberately tight (0.9pt): twin rails drawn ~1.4pt apart must SURVIVE as
    two rules — the caption fingerprint reads twin-ness as a style facet."""
    pieces = sorted(pieces, key=lambda p: (round(p[0], 0), p[1]))
    merged: list[list] = []  # [x, top, bottom, source, strokes]
    for x, top, bottom, src in pieces:
        hit = None
        for m in merged:
            if abs(m[0] - x) < 0.9 and top <= m[2] + 6.0 and bottom >= m[1] - 6.0:
                hit = m
                break
        if hit is None:
            merged.append([x, top, bottom, src, 1])
        else:
            hit[1] = min(hit[1], top)
            hit[2] = max(hit[2], bottom)
            hit[4] += 1
    return [VRule(page=page_no, x=m[0], top=m[1], bottom=m[2],
                  source=m[3], strokes=m[4]) for m in merged]


def collect_rules(page, page_no: int):
    """All drawn rules on a page + a diagonal flag. Collection thresholds are
    deliberately SMALL; significance filtering (is this wide enough to be a
    divider? a separator?) belongs to the resolver that consumes the rule,
    with the document's own evidence in hand.

    Returns (h_rules, v_rules, has_diagonal)."""
    h_pieces: list[tuple[float, float, float, str]] = []
    v_pieces: list[tuple[float, float, float, str]] = []
    diagonal = False
    for r in page.rects:
        w = r["x1"] - r["x0"]
        h = r.get("height", r["bottom"] - r["top"])
        if h < 2.5 and w >= 2.5:
            h_pieces.append((r["top"], r["x0"], r["x1"], "rect"))
        elif w < 2.5 and h >= 8:
            v_pieces.append((r["x0"], r["top"], r["bottom"], "rect"))
    for ln in page.lines:
        w = abs(ln["x1"] - ln["x0"])
        h = abs(ln["bottom"] - ln["top"])
        if h < 2.5 and w >= 2.5:
            h_pieces.append((ln["top"], min(ln["x0"], ln["x1"]),
                             max(ln["x0"], ln["x1"]), "line"))
        elif w < 2.5 and h >= 8:
            v_pieces.append((ln["x0"], min(ln["top"], ln["bottom"]),
                             max(ln["top"], ln["bottom"]), "line"))
        elif w > 30 and h > 10:
            diagonal = True   # X-capped pleading box caps
    # A third way to draw the same rule: a FILLED PATH, which pdfplumber
    # returns in page.curves. The old chain never looked there and whole
    # documents lost every footnote (ca2/provencher rules its notes with a
    # 143.9pt curve; alnd 197568 draws thin curves on 15 of 22 pages).
    for c in getattr(page, "curves", None) or []:
        w = c["x1"] - c["x0"]
        h = abs(c.get("height", c["bottom"] - c["top"]))
        if h < 2.5 and w >= 2.5:
            h_pieces.append((c["top"], c["x0"], c["x1"], "curve"))
        elif w < 2.5 and h >= 8:
            # A path draws VERTICALS too. Reading curves for horizontals only
            # made bap10/james_perry's caption divider invisible, and with no
            # rail its court reader returned NOTHING for a cover it owns.
            v_pieces.append((c["x0"], min(c["top"], c["bottom"]),
                             max(c["top"], c["bottom"]), "curve"))
    for img in page.images:
        w = img.get("width", 0) or (img["x1"] - img["x0"])
        h = img.get("height", 0) or (img["bottom"] - img["top"])
        if h < 5 and w >= 6:
            h_pieces.append((img["top"], img["x0"], img["x1"], "image"))
    return (_merge_h_segments(h_pieces, page_no),
            _merge_v_segments(v_pieces, page_no),
            diagonal)
