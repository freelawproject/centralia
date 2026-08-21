"""Court of Common Pleas of the State of Delaware ('delctcompl').

Everything unique to delctcompl lives here. It imports core, never another
court file, and no other court file imports it — not `delsuperct.py`, not
`delch.py`, not `del.py`, whose Delaware papers this court sets in its own
hand and whose code this file copies without touching.

THE CORPUS IS A STACK OF SCANS. Measured over all 42 records, every page:
**41 records carry ZERO text characters on ZERO pages** — they are
photocopies with no OCR layer, and there is nothing to read. The old engine
said so and stopped there (`GenericExtractor` plus a warning), and core here
already grades them `scanned` and drops the page images. This file does not
touch them: no masthead, no claim.

ONE RECORD OF THE 42 HAS A TEXT LAYER, and only on its cover
(`vrns_ii_llc_v._joseph_desmarias`: 32 inked rows on page 1, pages 2-13
image-only). So the reader has exactly one paper to read, and it reads the
one it can measure.

THE PAPER — a typed cover sheet, 14pt, on a 618x797 page:

    ┌────────────────────────────────────────────────────────────────┐
    │   IN THE COURT OF COMMON PLEAS FOR THE STATE OF                │  masthead,
    │      DELA WARE IN AND FOR NEW CASTLE COUNTY                    │  two rows
    │  VRNS II, LLC,          )                                      │
    │                         )                                      │
    │     v.                  )  C.A. No: CPU4-22-002095             │  the docket,
    │                         )                                      │  right column
    │  JOSEPH DESMARIAS,      )                                      │
    │     Defendant.          )                                      │
    │            Submitted: April 8, 2025                            │  the dates,
    │            Decided: June 9, 2025                               │  centred
    │  John R. Weaver Jr., Esquire   Robert C. McDonald, Esquire     │  appearances,
    │  2409 Landside Drive           1523 Concord Pike, Suite 400    │  TWO COLUMNS
    │  Wilmington, DE 19810          Wilmington, DE 19803            │  over a
    │  (302) 655-7371                (302) 888-2900                  │  gutter with
    │  Attorney for Plaintiff        Attorney for Defendant          │  nothing in it
    │              DECISION AFTER TRIAL                              │  the paper's name
    │  Danberg, C.J.                                                 │  the byline
    └────────────────────────────────────────────────────────────────┘

THE DIVIDER IS TYPED, and it is the caption's whole geometry: a ')' column
at x0 312.3-313.0 on a page whose axis is 309.0, stacked over 11 baselines.
Column membership is decided by which side of that column a character sits
on, char by char — pdfio reports `column-gap-split: split 10 rows at column
gaps`, so whether a row arrived whole or already broken is an accident of
how wide its gutter happened to be, never a fact to read.

TWO REASONS THIS FILE EXISTS AT ALL, both defects in the unread reading:

  * THE PHONE NUMBER WAS THE DOCKET. Core read `(302) 655-7371` as
    `docket_number` and `(302) 888-2900` as `other_dockets`, while the
    actual number — `C.A. No: CPU4-22-002095`, printed in the right column
    of the box — went unrecorded. A docket read anywhere on the page is a
    guess; this court prints it in ONE cell, and that is where it is taken
    from.
  * THE SUBMISSION DATE WAS LOST. `Submitted: April 8, 2025` stands beside
    `Decided:` in the same two-row grid and only the second was recorded.

THE MASTHEAD WRAPS AND OCR BREAKS ITS WORDS ('DELA WARE'), so the landmark
is the FIRST row only — `(IN) THE COURT OF COMMON PLEAS …` — and the second
row is taken as the masthead's continuation by position, not by spelling. A
record whose page 1 has no such row is not this paper and gets NOTHING,
which is every one of the 41 scans.

WHAT THIS FILE DOES NOT DO. The byline grammar ('Danberg, C.J.'), the
paragraphing, the footnotes and the scanned-source warning are core's. It
reads the cover down to the byline and stops there.
"""

from __future__ import annotations

import re
from collections import Counter

from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

DELCTCOMPL = CourtProfile(
    "delctcompl", "Court of Common Pleas of the State of Delaware",
)
PROFILES[DELCTCOMPL.court_id] = DELCTCOMPL

STYLE_BOX = "parenthetical-box cover"

# ---- the masthead ---------------------------------------------------------
# 'IN THE COURT OF COMMON PLEAS FOR THE STATE OF' — the row that names the
# court. 'IN' and 'FOR THE STATE OF' are optional because the row wraps and
# the wrap point is the court's choice, not ours.
_MAST = re.compile(r"^(?:IN\s+)?THE COURT OF COMMON PLEAS\b", re.I)
# The masthead's own second row: the state and the county, which OCR breaks
# ('DELA WARE'). Matched with spaces squeezed out.
_MAST_TAIL = re.compile(r"^DELAWAREIN(?:AND)?FOR\w+COUNTY$", re.I)

# ---- the caption box ------------------------------------------------------

_RAIL_GLYPH = ")"
_RAIL_WINDOW = 6.0          # a char this close to the column's x IS the rail
_RAIL_OFF_AXIS = 60.0       # …and the column stands this close to the axis
_RAIL_FLOOR = 3             # three stacked glyphs before it is a column
_RAIL_GAP_MAX = 60.0        # the box's leading is 14-19pt; wider is not it

# THE DOCKET as this court writes it: 'C.A. No: CPU4-22-002095'. The colon
# and the period are both allowed because the court types both.
_DOCKET = re.compile(
    r"^(?:C\.\s?A\.?|Civ\.\s?A\.?|Cr\.\s?A\.?|Cr(?:im)?\.\s?ID"
    r"|I\.?\s?D\.?|Case|File|JP)\s*(?:Nos?\.?:?|ID)\s*(\S.*)$", re.I)
# The court's own dates, in the label grid beneath the box.
_DATE = re.compile(
    r"^(Submitted|Decided|Argued|Reargued|Heard|Filed|Revised)\s*:\s*(.+)$",
    re.I)
_DATE_CRIT = {"submitted": "submitted", "argued": "submitted",
              "reargued": "submitted", "heard": "submitted",
              "decided": "decision_date", "filed": "decision_date",
              "revised": "decision_date"}
# THE APPEARANCES NAME THEMSELVES. 'pro se' is on this list because this is
# a court of small claims and half its appearances are a party's own; it is
# safe here because the walk never reaches the body — the byline closes it.
_COUNSEL = re.compile(
    r"\b(?:Esquire|Esq\.|LLP|PLLC|P\.A\.|LLC|Attorneys?\s+for"
    r"|Counsel\s+for|Appearing\s+for|Attorney\s+for|Pro\s+[Ss]e)\b")
_STATUS = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Garnishees?|Counterclaim[- ]\w+|Intervenors?)"
    r"(?:\s+Below)?(?:[-/]\w+)?[,.]?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# The paper names itself in bold caps on the axis: 'DECISION AFTER TRIAL',
# 'ORDER', 'OPINION AND ORDER', 'MEMORANDUM OPINION'.
_TITLE = re.compile(
    r"^(?:DECISION|OPINION|ORDER|MEMORANDUM|JUDGMENT|FINDINGS|TRIAL)\b"
    r"[A-Z ,.'&/-]*$")
# 'Danberg, C.J.' / 'WELCH, J.' / 'Smalls, C.J.' — the STOP, not the parse.
_BYLINE = re.compile(
    r"^(?:Mc|Mac|St\.\s?)?[A-Z][A-Za-z’'\-]+(?:\s+[A-Z][A-Za-z’'\-]+)?"
    r"(?:,\s*(?:Jr\.|Sr\.|II|III|IV|V))?,\s*"
    r"(?:C\.\s?J\.|J\.|Judge|Commissioner|Chief\s+Judge)\s*\d{0,2}\s*[.:]?$")

_MAX_PAGES = 3


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    return "".join((text or "").split()).upper()


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The ')' column, or None.

    A rail is a COLUMN — glyphs stacked at one x — and it is SEEDED from the
    glyphs standing at a line's own edge, because the rail's ')' is always
    alone on its row or glued to one end of it. A parenthesis inside prose
    is not one. Membership is then by column, grown outward one contiguous
    step at a time so a prose paren further down the page is barred by the
    gap bound.
    """
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
                     and abs(c["x0"] - x) <= 3.0),
                    key=lambda c: c["top"])
    run = [c for c in column
           if seed[0]["top"] - 0.5 <= c["top"] <= seed[-1]["top"] + 0.5]
    if not run:
        return None
    for ch in reversed([c for c in column if c["top"] < run[0]["top"]]):
        if run[0]["top"] - ch["top"] > _RAIL_GAP_MAX:
            break
        run.insert(0, ch)
    for ch in [c for c in column if c["top"] > run[-1]["top"]]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    return {"glyph": _RAIL_GLYPH, "x": float(x),
            "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _side(line, mid: float, want: str):
    """The part of ``line`` on one side of ``mid``, or None. Split CHAR BY
    CHAR (the ca6 reading): whether pdfio already broke the row at its column
    gap is an accident of how wide the gap happened to be."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


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


# --------------------------------------------------------------------------
# rows and cells
# --------------------------------------------------------------------------

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


def _cell(parts: list, role: str, page: int):
    """One column's cell on one row — the empty one keeps its place."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                        role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = False) -> None:
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

    def block(self, blk, ids) -> None:
        self.items.append(blk)
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


def _sides(caption_rows: list[str]) -> tuple[str, str] | None:
    """The two party names either side of the pivot — built from the party
    NAMES, never by joining the caption wholesale (the ca6 reading): the
    status labels and the pivot are apparatus, not names."""
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
        if _STATUS.match(flat):
            continue
        side.append(flat.rstrip(","))
    if not seen or not left or not right:
        return None
    return " ".join(left), " ".join(right)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="delctcompl")
def read_headmatter_delctcompl(model, geom, **_):
    """Read the Court of Common Pleas' typed cover, or NOTHING.

    NOTHING is the answer for 41 of the 42 records, and it is the right one:
    a scan with no text layer prints no masthead, so there is no paper here
    to read and core's own scanned-source handling is the whole reading.
    """
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 6:
        return NOTHING
    if not any(_MAST.match(_norm(" ".join(l.plain for l in g)))
               for g in rows[:4]):
        return NOTHING              # not this court's cover
    rail = _rail(page1)
    if rail is None:
        return NOTHING              # no divider: not a caption this court set

    ctx = _Ctx()
    ctx.crit["headmatter_style"] = STYLE_BOX
    ctx.crit["court"] = DELCTCOMPL.court_label

    # THE WALK RUNS TO THE BYLINE, over as many as three pages, so the
    # stream is built first and the byline located in it: the appearances
    # are bracketed by it rather than recognised row by row.
    stream: list = []
    for pm in model.pages[:_MAX_PAGES]:
        page_rail = rail if pm.number == page1.number else _rail(pm)
        for group in _rows(pm, finder):
            stream.append((pm, page_rail, sorted(group, key=lambda l: l.x0)))

    byline_at = None
    for i, (_pm, _pr, pieces) in enumerate(stream):
        text = _norm(" ".join(l.plain for l in pieces))
        if _BYLINE.match(text) and len(text) < 48:
            byline_at = i
            break

    box_left: list = []
    box_right: list = []
    box_ids: set[int] = set()
    caption_rows: list[str] = []
    app_rows: list = []             # (page, left parts, right parts)
    mast_seen = False
    title_rows: list[str] = []
    dockets: list[str] = []

    for i, (pm, page_rail, pieces) in enumerate(stream):
        if byline_at is not None and i >= byline_at:
            break
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue

        # --- the masthead, above the box ---------------------------------
        if not mast_seen and _MAST.match(text):
            ctx.emit(pieces, "court", centre=True)
            mast_seen = True
            continue
        if mast_seen and not box_left and _MAST_TAIL.match(_squeeze(text)):
            ctx.emit(pieces, "court", centre=True)
            continue

        # --- the box: every row inside the rail's own span ----------------
        # A ROW IS IN THE BOX WHEN IT OVERLAPS THE RAIL'S BAND — the
        # rail's own extent is measured from its GLYPHS and a glyph's top
        # sits 2.4pt below its line's ('VRNS II, LLC,' at 139.8 against the
        # ')' beside it at 142.2), so a baseline test with a small tolerance
        # loses the box's first row. Read as an appearance instead, that row
        # took the plaintiff's name out of the caption and put a bare ')' in
        # the roster.
        in_box = (page_rail is not None
                  and pieces[0].top < page_rail["bottom"]
                  and getattr(pieces[0], "bottom", pieces[0].top)
                  > page_rail["top"])
        if in_box:
            mid = page_rail["x"] + _RAIL_WINDOW
            l_parts, r_parts = [], []
            for line in pieces:
                bare = _shed(line, page_rail)
                if bare is None:
                    box_ids.add(line.id)
                    continue
                box_ids.add(line.id)
                lp = _side(bare, mid, "L")
                rp = _side(bare, mid, "R")
                if lp is not None:
                    l_parts.append(lp)
                if rp is not None:
                    r_parts.append(rp)
            box_left.append(_cell(l_parts, "caption", pm.number))
            box_right.append(_cell(r_parts, "docket", pm.number))
            if l_parts:
                caption_rows.append(_norm(" ".join(p.plain for p in l_parts)))
            # THE DOCKET IS TAKEN FROM ITS CELL, never from the page: the
            # phone numbers in the appearances below match no docket label,
            # and core reading one as `docket_number` is exactly what this
            # branch exists to correct.
            r_text = _norm(" ".join(p.plain for p in r_parts))
            hit = _DOCKET.match(r_text)
            if hit:
                dockets.append(_norm(hit.group(1)) or r_text)
            continue

        # --- the dates ----------------------------------------------------
        hit = _DATE.match(text)
        if hit:
            key = _DATE_CRIT.get(hit.group(1).lower())
            if key and not ctx.crit.get(key):
                ctx.crit[key] = _norm(hit.group(2)).rstrip(".")
            ctx.emit(pieces, "date", centre=True)
            continue

        # --- the appearances: two columns over an empty gutter ------------
        if page_rail is not None and _COUNSEL.search(text):
            mid = pm.width / 2
            l_parts = [p for p in (_side(l, mid, "L") for l in pieces)
                       if p is not None]
            r_parts = [p for p in (_side(l, mid, "R") for l in pieces)
                       if p is not None]
            app_rows.append((pm.number, l_parts, r_parts))
            continue
        # A runover of the block above: the address rows carry no landmark
        # of their own, so they belong to the block they continue.
        if app_rows and len(text) < 90 and not _TITLE.match(text):
            mid = pm.width / 2
            l_parts = [p for p in (_side(l, mid, "L") for l in pieces)
                       if p is not None]
            r_parts = [p for p in (_side(l, mid, "R") for l in pieces)
                       if p is not None]
            app_rows.append((pm.number, l_parts, r_parts))
            continue

        # --- what the paper calls itself ---------------------------------
        if _TITLE.match(text):
            title_rows.append(text)
            ctx.emit(pieces, "title", centre=True)
            ctx.anchor.extend(l.id for l in pieces)
            continue

        # Anything else above the byline is caption apparatus this court
        # prints and we have not named — tagged, not silently swallowed.
        ctx.emit(pieces, "case-info", centre=False)

    if not box_left:
        return NOTHING              # the box was never read

    # --- publish the box, in the page's own order --------------------------
    while box_left and not _text_of(box_left[-1]) and not _text_of(box_right[-1]):
        box_left.pop()
        box_right.pop()
    if not box_left:
        return NOTHING
    at = len(ctx.items)
    for j, row in enumerate(ctx.items):
        if getattr(row, "role", "") == "court":
            at = j + 1
    ctx.items.insert(at, m.CaptionBlock(
        left=box_left, right=box_right, rail=_RAIL_GLYPH,
        rail_rows=len(box_left), style_id="parenthetical-box",
        fp={"rail": _RAIL_GLYPH, "x": rail["x"]},
        prov=m.Prov(page1.number, tuple(sorted(box_ids)))))
    ctx.consumed.update(box_ids)

    # --- publish the appearances -----------------------------------------
    if app_rows:
        left, right = [], []
        ids: set[int] = set()
        for pg, l_parts, r_parts in app_rows:
            left.append(_cell(l_parts, "counsel", pg))
            right.append(_cell(r_parts, "counsel", pg))
            ids.update(p.id for p in l_parts + r_parts)
        while left and not _text_of(left[-1]) and not _text_of(right[-1]):
            left.pop()
            right.pop()
        ctx.block(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id="open-gutter", fp={"rail": None},
            prov=m.Prov(app_rows[0][0], tuple(sorted(ids)))), ids)
        # THE ROSTER IS COPIED, NOT MOVED: the appearances render inside the
        # headmatter where the court printed them, and `attorneys` is the
        # queryable copy.
        cols = [" ".join(_text_of(c) for c in col if _text_of(c))
                for col in (left, right)]
        text = "  ".join(c for c in cols if c.strip())
        if text.strip():
            ctx.crit["attorneys"] = _norm(text)

    # --- the parsed forms, beside the printed ones ------------------------
    if caption_rows:
        ctx.crit["caption"] = [r for r in caption_rows if r]
        pair = _sides(caption_rows)
        if pair:
            ctx.crit["parties"] = [pair[0], pair[1]]
            ctx.crit["case_name"] = f"{pair[0]} v. {pair[1]}"
    if dockets:
        ctx.crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            ctx.crit["other_dockets"] = dockets[1:]
    if title_rows:
        ctx.crit["title"] = title_rows[0]
    return ctx.result()
