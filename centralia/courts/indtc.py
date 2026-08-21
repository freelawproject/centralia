"""Indiana Tax Court ('indtc').

Everything unique to indtc lives here. It imports core, never another court
file, and no other court file imports it — not `ind.py` and not
`indctapp.py`, whose RULED COVER this court does not print. Indiana's two
appellate courts engrave their name over a fenced cover and set the case
below it; the Tax Court fences its cover too, but it fences FIVE BANDS and
it puts the appearances FIRST.

THE CONTRACT — one paper, printed 41 times out of 41, and the page draws its
own structure. Full-measure rules at the body rail cut the cover into bands,
and each band is entered on its own landmark:

    ┌─────────────────────────────────────────────────────────────────────┐
    │ ATTORNEY FOR PETITIONERS:      ATTORNEYS FOR RESPONDENTS:           │ the APPEARANCES,
    │ ──────────────────────        ─────────────────────────             │ two columns, each
    │ JAMES P. FENTON               THEODORE E. ROKITA                    │ head underlined by
    │ ATTORNEY AT LAW               ATTORNEY GENERAL OF INDIANA           │ its own rule
    │ Fort Wayne, IN                J. DEREK ATWOOD                       │
    ├─────────────────────── fence ───────────────────────────────────────┤
    │                        IN THE                                       │ the court names
    │                   INDIANA TAX COURT                                 │ itself, 20pt
    ├─────────────────────── fence ───────────────────────────────────────┤
    │ ALICE LUEBKE, TINA HUGHES,      )                                   │ the CAPTION, two
    │      Petitioners,               )                                   │ columns over a
    │      v.                         )   Cause No. 24T-TA-00007          │ TYPED ')' rail…
    │ INDIANA DEPARTMENT OF LOCAL     )                                   │
    │ GOVERNMENT FINANCE, …,          )                                   │
    │      Respondents.               )                                   │
    │        ON APPEAL FROM A FINAL DETERMINATION OF                      │ …and the origin
    │        THE DEPARTMENT OF LOCAL GOVERNMENT FINANCE                   │ under it
    ├─────────────────────── fence ───────────────────────────────────────┤
    │                    FOR PUBLICATION                                  │ what the paper is
    │                  September 13, 2024                                 │ …and when
    ├─────────────────────── fence ───────────────────────────────────────┤
    │ WELCH, Special J.                                    the writing     │
    └─────────────────────────────────────────────────────────────────────┘

MEASURED OVER ALL 41 RECORDS:

  * THE FENCE is 468.0-468.2pt (16 records draw one at 459.0) and every one
    starts at x0 72.0 — which is also this court's measured body rail, so
    the fence needs no declared position the way indctapp's does. Every
    record draws at least two on page 1.
  * THE BANDS ARE NOT COUNTED. A record that fences three times and one that
    fences five both read, because each band is entered on its LANDMARK: the
    masthead by the court's own name, the caption by the rail it draws, the
    origin by 'ON APPEAL FROM', the publication flag by what it says, and the
    date by being a date. That is ind's rule and coloctapp's, and the reason
    for it is the same — a role indexed off a band ORDINAL is wrong the first
    time a court fences once more.
  * THE APPEARANCES COME FIRST, above the first fence, and they are TWO
    COLUMNS: heads at x0 72.0 and 306.0-324.0, each underlined by a rule of
    its own (197.4pt at 72.0, 192.0pt at 315.0). pdfio returns some rows
    fused (x0 72.0 reaching x1 511.4 — both columns on one line), so the
    split is CHAR BY CHAR at the gutter the rows themselves measure, and the
    block is published as a CaptionBlock with `rail=None`, which is what the
    model means by a whitespace gutter (the guam reading).
  * THE RAIL IS TYPED AND ITS COLUMN MOVES: x 324 on 29 records, 306 on 9,
    311 on 2, 315 on 1. So it is FOUND, never declared — the column its
    glyphs stack in, grown outward one contiguous step at a time so a
    parenthesis in the caption's own prose cannot extend it (the moctapp
    reading).
  * WHAT THE PAPER IS: 'FOR PUBLICATION' on 30 records, 'NOT FOR
    PUBLICATION' on 10. One record prints neither and is read without one.
  * THE COURT SIGNS 'MCADAM, J.' (31), 'BAKER, Special J.' (2) and 'WELCH,
    Special J.' (1); 38 of the 41 sign on page 1. The profile registered in
    courts/__init__.py already reads all three forms — measured, not
    assumed — so nothing about the byline is declared here. The reader stops
    at it.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

# ---- the page's own marks --------------------------------------------------

# THE FENCE: full measure at the body rail. The appearance-head underlines
# are the other rules this court draws and they are half the measure or less,
# so nothing between the two is ever drawn.
_FENCE_MIN = 450.0
_FENCE_RAIL = 3.0
_MAX_PAGES = 2

_RAIL_GLYPH = ")"
_RAIL_FLOOR = 3
_RAIL_WINDOW = 6.0
_RAIL_OFF_AXIS = 60.0
# The caption's leading is 13.8pt; a gap wider than this is not the next row
# of the same rail.
_RAIL_GAP_MAX = 60.0

_MAST_TOP = "INTHE"
_MAST_NAME = "INDIANATAXCOURT"
_COURT_NAME = "Indiana Tax Court"

# THE CASE'S NUMBER, in the right column of the box.
# THE LABEL IS EITHER WORD. This court writes 'Cause No.' on some covers
# and 'Case No.' on the rest -- the same number, the same column, the
# same paper.
# THE APPEARANCE COLUMNS' GUTTER: the right column stands at the page's
# axis (306.1-324.0 over the corpus, against a 612pt page) and the left
# column's ink stops short of it. A row that opens within _AXIS_SLACK of the
# axis is the right column's; the split stands _GUTTER_MARGIN before the
# leftmost of them.
_AXIS_SLACK = 6.0
_GUTTER_MARGIN = 6.0
_CAUSE = re.compile(r"^Ca(?:us|s)e\s+Nos?\.?\s*(\S.*)$", re.I)
# WHERE IT CAME FROM. A closed vocabulary of the ways this court states it —
# never a tribunal NAME, which the caption also carries.
_ORIGIN = re.compile(
    r"^ON\s+(?:APPEAL|PETITION|REVIEW|CERTIFICATION)\b"
    r"|^ORIGINAL\s+TAX\s+APPEAL\b", re.I)
_PUBLICATION = re.compile(r"^(NOT\s+FOR\s+PUBLICATION|FOR\s+PUBLICATION)\.?$",
                          re.I)
_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s*\d{4}\.?$", re.I)
# The appearance block's own heads name the party represented and close on a
# colon ('ATTORNEYS FOR RESPONDENT:', 'PETITIONER APPEARING PRO SE:').
_APPEAR_HEAD = re.compile(
    r"^(?:ATTORNEYS?\s+FOR\b|(?:PETITIONERS?|RESPONDENTS?)\s+APPEARING\b"
    r"|ATTORNEYS?\s+AT\s+LAW\b)", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)


def _IS_CAPS(text: str) -> bool:
    """The row is set in CAPITALS. The court's titles are; the opinion's
    prose, which shares the cover's last band with them, is not."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)

_STATUS_WORDS = frozenset(
    ("petitioner", "petitioners", "respondent", "respondents", "appellant",
     "appellants", "appellee", "appellees", "intervenor", "intervenors",
     "and", "the", "of", "et", "al", "deceased", "party", "in", "interest"))


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    return "".join((text or "").split()).upper()


def _fences(pm) -> list[float]:
    """The tops of the cover fences this page draws, in page order."""
    return sorted(r.top for r in pm.h_rules
                  if r.width >= _FENCE_MIN and abs(r.x0 - 72.0) <= _FENCE_RAIL)


def _rail(pm) -> dict | None:
    """The caption's typed rail: the column its ')' glyphs stack in.

    Seeded from the glyphs standing at a line's own EDGE — a rail glyph is
    alone on its line or glued to one end of it — then grown outward through
    the column one contiguous step at a time, so a parenthesis inside the
    caption's prose is barred by the gap bound."""
    edge = []
    for line in pm.lines:
        inked = [c for c in line.chars if (c.get("text") or "").strip()]
        for c in (inked[:1] + inked[-1:]):
            if (c.get("text") or "") == _RAIL_GLYPH:
                edge.append(c)
    if len(edge) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in edge).most_common(1)[0]
    if abs(x - pm.width / 2) > _RAIL_OFF_AXIS:
        return None
    seed = sorted((c for c in edge if abs(c["x0"] - x) <= 3.0),
                  key=lambda c: c["top"])
    if len({round(c["top"], 1) for c in seed}) < _RAIL_FLOOR:
        return None
    column = sorted((c for line in pm.lines for c in line.chars
                     if (c.get("text") or "") == _RAIL_GLYPH
                     and abs(c["x0"] - x) <= 3.0), key=lambda c: c["top"])
    run = [c for c in column
           if seed[0]["top"] - 0.5 <= c["top"] <= seed[-1]["top"] + 0.5]
    for ch in reversed([c for c in column if c["top"] < run[0]["top"]]):
        if run[0]["top"] - ch["top"] > _RAIL_GAP_MAX:
            break
        run.insert(0, ch)
    for ch in [c for c in column if c["top"] > run[-1]["top"]]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    return {"x": float(x), "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _shed(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == _RAIL_GLYPH
                    and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` on one side of a divider, or None. Split CHAR BY
    CHAR: whether pdfio broke the row at its column gap is an accident of how
    wide the gap happened to be."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, furniture removed, grouped by baseline."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, pages):
        self.pages = pages
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int) -> None:
        """A fence renders where the page draws it — a reader that claims a
        fenced block owes the page its fences."""
        prov = self.items[-1].prov if self.items else m.Prov(page, ())
        self.items.append(m.Rule(prov=prov, typed=False, span="full"))

    def cell(self, parts: list, role: str, page: int):
        parts = sorted(parts, key=lambda l: l.x0)
        if not parts:
            return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                            role=role)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def columns(self, rows: list, role: str, style: str) -> None:
        """Two columns over an undrawn gutter, paired by the printed row.

        The gutter is MEASURED, not assumed — but measured as the RIGHT
        COLUMN'S OWN RAIL, not as the widest gap between the x0s the rows
        cluster on. Some rows arrive FUSED (both heads set on one line
        opening at the left rail), so a fused row contributes only its left
        x0 and the widest cluster gap fell mid-word: the split cut 'ATTORNEY
        FOR PETITIONERS:' into 'ATTORNEY FOR PE' and 'TITIONERS: …'. Every
        row of the right column opens right of the page's axis and no ink of
        the left column reaches it, so the leftmost of those rails is the
        gutter. The split itself is char by char, for the fused rows."""
        axis = self.pages[rows[0][0]].width / 2
        rights = [l.x0 for _pg, grp in rows for l in grp
                  if l.x0 >= axis - _AXIS_SLACK]
        if not rights:
            for _pg, grp in rows:      # one column: the page set no gutter
                self.emit(grp, role, centre=False)
            return
        mid = min(rights) - _GUTTER_MARGIN
        left, right = [], []
        ids: set[int] = set()
        for pg, grp in rows:
            l_side, r_side = [], []
            for line in grp:
                for want, bucket in (("L", l_side), ("R", r_side)):
                    part = _side(line, mid, want)
                    if part is not None:
                        bucket.append(part)
            left.append(self.cell(l_side, role, pg))
            right.append(self.cell(r_side, role, pg))
            ids.update(l.id for l in grp)
        while left and not _text_of(left[-1]) and not _text_of(right[-1]):
            left.pop()
            right.pop()
        if not left:
            return
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id=style, fp={"rail": None, "mid_x": round(mid, 1)},
            prov=m.Prov(rows[0][0], tuple(sorted(ids)))))
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


@decider("headmatter.read", court="indtc")
def read_headmatter_indtc(model, geom, **_):
    """Read the Tax Court's fenced cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    fences = _fences(page1)
    if len(fences) < 2:
        return NOTHING            # not the paper this contract names
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(get_profile("indtc").byline)
    pages = {pm.number: pm for pm in model.pages}

    rows = _rows(page1, finder)
    if not any(_squeeze(_norm(" ".join(l.plain for l in g))) == _MAST_NAME
               for g in rows):
        return NOTHING            # the court does not name itself here

    rail = _rail(page1)
    ctx = _Ctx(pages)
    appear: list = []
    box: list = []
    rail_ids: set[int] = set()
    caption_rows: list[str] = []
    right_plain: list[str] = []
    origin: list[str] = []
    origin_band = None
    title: list[str] = []
    appearing = False
    last_band = None
    for group in rows:
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        first = group[0]
        # THE FENCES SEGMENT, and a band is the number of fences still below
        # a row — so the appearances' band is the highest and the writing's
        # is 0. Tested the other way round the cover reads inside out.
        band = sum(1 for f in fences if f > first.top)
        if last_band is not None and band != last_band:
            ctx.rule(page1.number)
        last_band = band
        centred = abs((first.x0 + max(l.x1 for l in group)) / 2
                      - page1.width / 2) <= 24.0

        if parser.parse(text) is not None and len(text) < 40:
            break                                 # the writing begins

        if _squeeze(text) in (_MAST_TOP, _MAST_NAME):
            appearing = False     # the masthead closes the counsel columns
            ctx.crit.setdefault("court", _COURT_NAME)
            ctx.emit(group, "court")
            continue
        # THE APPEARANCES ARE ENTERED BY THEIR OWN LANDMARK, never by being
        # above the first fence. On 40 covers the fences bracket the masthead
        # and the counsel columns do stand above them; on the rehearing order
        # there are no appearances at all and the fences bracket the TITLE,
        # so an index would have swallowed the masthead and the whole caption
        # into a counsel block.
        if _APPEAR_HEAD.match(text):
            appearing = True
        if appearing:
            appear.append((first.page, group))
            continue
        if rail is not None and rail["top"] - 1.0 <= first.top \
                <= rail["bottom"] + 1.0:
            l_cells, r_cells = [], []
            for line in group:
                bare = _shed(line, rail)
                if bare is None:
                    # THE LINE WAS THE RAIL and nothing else. It is spoken
                    # for by the block's ``rail`` — but it must still be
                    # CLAIMED, or core finds an unread row inside the cover
                    # and opens a writing on it.
                    rail_ids.add(line.id)
                    continue
                for want, bucket in (("L", l_cells), ("R", r_cells)):
                    part = _side(bare, rail["x"], want)
                    if part is not None:
                        bucket.append(part)
            box.append((first.page, l_cells, r_cells))
            caption_rows.append(_norm(" ".join(c.plain for c in l_cells)))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
            continue
        mm = _CAUSE.match(text)
        if mm and centred:
            # THE REHEARING ORDER SETS THE NUMBER CENTRED above the caption
            # instead of in the rail's right column. Same number, same paper.
            numbers = [n.strip() for n in re.split(r"[;,]", mm.group(1))
                       if n.strip()]
            if numbers:
                ctx.crit.setdefault("docket_number", numbers[0])
                if numbers[1:]:
                    ctx.crit.setdefault("other_dockets", numbers[1:])
            ctx.emit(group, "docket", centre=True)
            continue
        if _ORIGIN.match(text):
            origin.append(text)
            origin_band = band
            ctx.emit(group, "lower-court", centre=centred)
            continue
        if origin and centred and band == origin_band \
                and not _PUBLICATION.match(text) and not _DATE.match(text):
            # THE ORIGIN RUNS ON: 'ON APPEAL FROM A FINAL DETERMINATION OF' /
            # 'THE DEPARTMENT OF LOCAL GOVERNMENT FINANCE'. The wrap names
            # the tribunal and nothing else on this cover stands where it
            # stands — IN THE ORIGIN'S OWN BAND. Unbounded, the wrap rule
            # reached across the next fence and took the TITLE below it.
            origin.append(text)
            ctx.emit(group, "lower-court", centre=centred)
            continue
        if _PUBLICATION.match(text):
            ctx.crit.setdefault(
                "publication_status",
                "unpublished" if text.upper().startswith("NOT")
                else "published")
            ctx.emit(group, "publication", centre=centred)
            continue
        if _DATE.match(text):
            ctx.crit.setdefault("decision_date", text.rstrip("."))
            ctx.emit(group, "date", centre=centred)
            continue
        if band and centred and _IS_CAPS(text):
            # WHAT THE PAPER IS CALLED. Five records set a title over the
            # writing — 'ORDER ON PARTIES\u2019 CROSS-MOTIONS FOR SUMMARY
            # JUDGMENT', 'ORDER GRANTING RESPONDENT\u2019S MOTION TO DISMISS',
            # 'FINAL DECISION ON REHEARING' / 'PURSUANT TO INDIANA APPELLATE
            # RULE 63(B)' — and no landmark above claimed them, so core
            # opened the writing THERE and the publication flag and the date
            # printed BELOW it were carried into the opinion's first
            # paragraph. Read on three marks the corpus measures together
            # and nothing else on this cover carries: ALL CAPS, CENTRED, and
            # INSIDE A FENCED BAND. The band is what keeps it off the
            # opinion's own centred all-caps headings ('FACTS AND PROCEDURAL
            # HISTORY'), which stand below the last fence, in band 0.
            title.append(text)
            ctx.emit(group, "title", centre=True)
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if appear:
        ctx.columns(appear, "counsel", "open-gutter")
    if box:
        _emit_box(ctx, box, rail, page1)
        ctx.consumed.update(rail_ids)
    if not box:
        return NOTHING            # the caption is what this cover is for

    cause = next((mm.group(1) for t in right_plain
                  for mm in [_CAUSE.match(t)] if mm), None)
    if cause:
        numbers = [n.strip() for n in re.split(r"[;,]", cause) if n.strip()]
        ctx.crit["docket_number"] = numbers[0]
        if numbers[1:]:
            ctx.crit["other_dockets"] = numbers[1:]
    if origin:
        ctx.crit.setdefault("lower_court", " ".join(origin)[:2000])
    if title:
        ctx.crit.setdefault("title", _norm(" ".join(title)))
    sides = _sides(caption_rows)
    if sides:
        ctx.crit.setdefault("parties", list(sides))
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    if caption_rows:
        ctx.crit.setdefault("caption", [r for r in caption_rows if r])
    ctx.crit["headmatter_style"] = "fenced bands"
    return ctx.result()


def _emit_box(ctx: _Ctx, box: list, rail, page1) -> None:
    """The caption, as the page sets it: two columns paired by printed row,
    over the rail the court typed."""
    left, right = [], []
    ids: set[int] = set()
    for pg, l_cells, r_cells in box:
        left.append(ctx.cell(l_cells, "caption", pg))
        right.append(ctx.cell(r_cells, _right_role(r_cells), pg))
        ids.update(c.id for c in l_cells + r_cells)
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    if not left:
        return
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
        style_id="parenthetical-box",
        fp={"rail": _RAIL_GLYPH, "mid_x": round(rail["x"], 1) if rail else 0},
        prov=m.Prov(box[0][0], tuple(sorted(ids)))))
    ctx.consumed.update(ids)


def _right_role(cells: list) -> str:
    text = _norm(" ".join(c.plain for c in cells))
    if not text:
        return "caption"
    if _CAUSE.match(text):
        return "docket"
    return "case-info"


def _sides(caption_rows: list[str]) -> tuple[str, str] | None:
    """The two party names either side of the pivot — built from the party
    NAMES, never by joining the caption wholesale (the ca6 reading)."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        if _PIVOT.match(flat):
            side = right
            seen = True
            continue
        words = [w.strip(",.;-/ ").lower()
                 for w in flat.replace("-", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    if not (left and right and seen):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))
