"""Supreme Court of the State of Delaware ('del').

Everything unique to del lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

WHY THIS FILE IS IMPORTED THE LONG WAY. The court id is 'del', and `del` is
a Python keyword: `del.py` is a perfectly legal FILENAME but `from . import
del` is a syntax error. So the file keeps the name every other court file
has — `centralia/courts/<court>.py`, the convention the porting docs state —
and courts/__init__.py reaches it with `importlib.import_module` instead.
Oregon ('or') has the same problem and the same answer.

THE CONTRACT — Delaware is the SECTION-RAIL caption, drawn with '§'. The
court sets a two-column box under a centred masthead and rules the middle
with a section sign on every row:

    ┌────────────────────────────────────────────────────────────────────┐
    │        IN THE SUPREME COURT OF THE STATE OF DELAWARE                │
    │ ACW CORPORATION (a.k.a.        §                                   │
    │ ARBY'S) and EASTERN            §   No.  302, 2019                  │
    │ ALLIANCE INS. CO., as …        §                                   │
    │ SHANARA DEVON WATERS,          §   Court Below:  Superior Court    │
    │                                §   of the State of Delaware        │
    │      Plaintiffs Below,         §                                   │
    │      Appellants,               §   C.A. No. N18C-02-004            │
    │                                §                                   │
    │      v.                        §                                   │
    │ CHRISTOPHER ROBERT             §                                   │
    │ MAXWELL, and DONEGAL …         §                                   │
    │      Defendants Below,         §                                   │
    │      Appellees.                §                                   │
    │                                                                    │
    │              Submitted:  September 9, 2020                         │
    │              Decided:  November 18, 2020                           │
    │ Before SEITZ, Chief Justice; VALIHURA, VAUGHN, TRAYNOR, …          │
    │ MONTGOMERY-REEVES, constituting the Court en Banc.                 │
    │ Upon appeal from the Superior Court.  AFFIRMED.                    │
    │ Scott R. Mondell, Esquire, … for Appellants …                      │
    │ VAUGHN, Justice:                                                   │
    └────────────────────────────────────────────────────────────────────┘

THE RAIL IS READ FROM THE DRAWN GLYPH, not from the wording — the standard
this repo already keeps for two-column captions (ca6 is the model). The
box's rows are PAIRED: each printed row contributes one line to the left
stack and one to the right, so a row with nothing on its right still holds
its place and the two columns stay level. Trailing empty pairs are trimmed,
as ca6 trims them, because the rail runs a few rows past the last words.

WHAT STANDS IN THE RIGHT COLUMN is the case's numbering, not a party: the
court's own docket ('No. 302, 2019'), the court below and its number ('Court
Below: Superior Court', 'C.A. No. N18C-02-004'). Each is read by its own
landmark, since a certified question prints 'Certification of Question of
Law' there instead and a Rule 42 appeal prints nothing at all.

'Upon appeal from the Superior Court.  AFFIRMED.' IS ONE PRINTED LINE and it
says two things — where the case came from and what this court did. A row can
carry one role, so it is read as `disposition` where it names a disposition
and as `lower-court` otherwise; the origin is still recovered into
`criteria.history` either way, so nothing is lost by the choice.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(
    r"^IN THE SUPREME COURT OF THE STATE OF DELAWARE$", re.I)
_RAIL_GLYPH = "§"
_AXIS_TOL = 14.0
_RAIL_WINDOW = 6.0          # a glyph this close to the rail's x IS the rail
_RAIL_GAP_MAX = 60.0        # …and the next row of the same rail is this near
_MAX_PAGES = 2

# The right column's tenants. THE DOCKET'S LABEL VARIES and its number is
# not always one number: 'No. 302, 2019' is the ordinary form, but the court
# also writes 'Nos. 284 and 372, 2025' for a consolidated appeal
# (pachis_zander) and 'C.A. No. 509, 2025' for a certified one
# (new_castle_county). Read as `\d+,\s*\d{4}` alone, both records returned
# NOTHING — no docket read means the box was not read — and the user marked
# them failing. The number is now anything that opens on a digit and carries
# the four-digit year this court's docket always ends in.
_DOCKET = re.compile(
    r"^(?:C\.\s?A\.\s*)?Nos?\.\s*(\d[^,]*,\s*\d{4}\b.*)$", re.I)
# 'Court Below:  Superior Court' and 'Court Below—Superior Court' — the
# court punctuates it both ways, so the label is matched without its
# punctuation.
_COURT_BELOW = re.compile(r"^(?:Court Below|Certification of Question"
                          r"|Case Below|Court below)\b", re.I)
# 'C.A. No. N18C-02-004' / 'Cr. ID Nos. 2403010012 A/B (K)' / 'I.D. No. …'
_BELOW_NO = re.compile(
    r"^(?:C\.A\.|Cr\.\s*A\.|Cr\.\s*ID|I\.D\.|File|Case)\s*(?:Nos?\.|ID)", re.I)
# The dates, centred beneath the box.
_DATE_LABEL = re.compile(
    r"^(Submitted|Decided|Argued|Reargued|Revised|Corrected):\s*(.+)$", re.I)
_DATE_CRIT = {"decided": "decision_date", "submitted": "submitted",
              "argued": "submitted", "reargued": "submitted"}
_PANEL = re.compile(r"^Before\b|constituting the Court", re.I)
_ORIGIN = re.compile(r"^Upon (?:appeal|report|certification|petition)", re.I)
_DISPO = re.compile(
    r"\b(AFFIRMED|REVERSED|VACATED|REMANDED|DISMISSED|MODIFIED|DENIED"
    r"|GRANTED|CERTIFIED|ANSWERED|SUSPENDED|DISBARRED)\b")
# The appearances name themselves.
_COUNSEL = re.compile(
    r"\b(?:Esquire|Esq\.|for Appellant|for Appellee|for Petitioner"
    r"|for Respondent|for the State|pro se|Deputy Attorney General)\b", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# 'VAUGHN, Justice:' / 'SEITZ, Chief Justice:' / 'PER CURIAM:'
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z'’\-]+(?:-[A-Z][A-Za-z'’\-]+)?,\s*"
    r"(?:Chief\s+)?Justice\s*:?|PER CURIAM\s*:?)$")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="del")
def read_headmatter_del(model, geom, **_):
    """Read Delaware's section-rail box, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 6:
        return NOTHING
    # THE MASTHEAD IS FOUND, NOT INDEXED. Chancery-style e-filing stamps
    # print above it on some records ('EFiled: Apr 29 2026 09:55AM EDT' /
    # 'Filing ID 79335656' / 'Case Number Multi-Case' —
    # `in_re_the_aes_corporation_and_owens_`), and requiring row 0 read that
    # record as NOTHING.
    mast = next((i for i, g in enumerate(rows[:6])
                 if _MASTHEAD.match(_norm(" ".join(l.plain for l in g)))), None)
    if mast is None:
        return NOTHING

    # THE RAIL IS THE DRAWN GLYPH. Its column is the one x position where the
    # court sets a bare '§'. The glyph is not always a piece of its own: on
    # `best_v._state` pdfio returns '§ No. 369, 2025' and '§ Court
    # Below—Superior Court' as SINGLE lines beginning at the rail, and on
    # `camden_foley_v._session_corp.` it comes back glued to the END of the
    # left column ('CAMDEN FOLEY and SAMUEL §'). Testing for a bare glyph
    # found the rail's own column but skipped every row that carried the
    # numbering, which is where the docket is — 39 of 50 records read as
    # NOTHING. So the rail is located from the bare glyphs and the row is
    # then split at that x, with the glyph stripped off whichever side it
    # came attached to.
    rail = _rail(page1)
    if rail is None:
        return NOTHING
    mid = rail["x"]
    # THE BOX ENDS AT THE LAST RAIL. A row of the left column and the '§'
    # beside it do not always share a top — pdfio returns them as separate
    # rows — so a row carrying no glyph does NOT mean the box has closed.
    # Treating it that way shut the box on the party's first line and the
    # docket, printed two rows further down, was never collected: 15 of 50
    # records read as NOTHING. The box is the band the rail spans — the band
    # the RAIL'S OWN COLUMN spans, and no further. Taken as the last line
    # anywhere on the page holding a '§', a footnote's statutory citation
    # closed the box at the foot of the sheet: aim_ventura cites 'Del. Const.
    # art. IV, § 12' at top 695.2, and the box swallowed the dates, the
    # panel, the 'ORDER' heading and the first four paragraphs of the
    # writing, all tinted `caption`.
    box_bottom = rail["bottom"]

    ctx = _Ctx()
    left: list = []
    right: list = []
    right_plain: list[str] = []
    caption: list[str] = []
    below: list[str] = []
    box_ids: set[int] = set()
    box_page = page1.number
    band = "box"          # box | tail | counsel
    for idx, group in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL

        if idx < mast:
            ctx.drop(pieces, "stamp")
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _BYLINE.match(text):
            break                       # the paper begins

        if band == "box" and first.top <= box_bottom + 1.0:
            # ONE PRINTED ROW, TWO STACKS. Both sides keep their place even
            # when one of them is blank, or the columns drift apart. The
            # split is at the RAIL's x, so a line that opens with the glyph
            # belongs to the right column whatever else it carries.
            # …AND THE SPLIT IS CHAR BY CHAR. Whether pdfio broke a row at
            # its column gap is an accident of how wide the gap happened to
            # be: 'OF THE BAR OF THE SUPREME §  No. 177, 2026' arrives as
            # ONE run beginning at the left margin, and by the row's own x0
            # the docket was filed in the PARTY column — so the right column
            # held nothing, and the record read as NOTHING (the ca6 lesson,
            # which this reader had for the rail's own glyph but not for the
            # cells either side of it).
            l_parts, r_parts = [], []
            for line in pieces:
                bare = _shed(line, rail)
                if bare is None:
                    continue
                for want, bucket in (("L", l_parts), ("R", r_parts)):
                    part = _side(bare, mid, want)
                    if part is not None:
                        bucket.append(part)
            left.append(_row(l_parts, "caption"))
            right.append(_row(r_parts, _right_role(r_parts)))
            box_ids.update(l.id for l in pieces)
            for part in l_parts:
                one = _norm(part.plain)
                if one and not _PIVOT.match(one):
                    caption.append(one)
            r_text = _strip_rail(_norm(" ".join(l.plain for l in r_parts)))
            if r_text:
                right_plain.append(r_text)
            continue
        if band == "box":
            band = "tail"

        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(dated.group(1).lower())
            if key:
                ctx.crit.setdefault(key, _norm(dated.group(2)))
            ctx.emit(pieces, "date", centre=centred)
            continue
        if _PANEL.search(text):
            ctx.crit.setdefault("panel_line", text)
            # THE ROSTER IS ALSO THE ANSWER TO 'WHO SAT'. Core reads `judges`
            # off this row itself; claimed by this reader it no longer can,
            # and a court reader that improves the block must not cost the
            # document a criterion it already had (boulden_v._state lost its
            # judges exactly that way). `panel_line` is the row as printed,
            # `judges` the bench without its 'Before' label and its closing
            # clause.
            bench = re.sub(r"^Before\s+", "", text, flags=re.I)
            bench = re.sub(r",?\s*constituting the Court.*$", "", bench,
                           flags=re.I).rstrip(" ,.")
            if bench:
                ctx.crit.setdefault("judges", bench)
            ctx.emit(pieces, "panel", centre=False)
            continue
        if _ORIGIN.match(text):
            below.append(text)
            ctx.emit(pieces, "disposition" if _DISPO.search(text)
                     else "lower-court", centre=False)
            continue
        if _COUNSEL.search(text) or band == "counsel":
            band = "counsel"
            ctx.emit(pieces, "counsel", centre=False)
            continue
        if _DISPO.search(text) and len(text) < 120:
            ctx.emit(pieces, "disposition", centre=centred)
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    # THE BOX, placed where the page prints it — ahead of everything the
    # court sets beneath it.
    if left:
        # The rail runs a few rows past the last words; ca6 trims the empty
        # tail pairs and so does this.
        while left and not _text_of(left[-1]) and not _text_of(right[-1]):
            left.pop()
            right.pop()
        block = m.CaptionBlock(
            left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
            style_id="section-rail",
            fp={"rail": _RAIL_GLYPH, "mid_x": round(mid, 1)},
            prov=m.Prov(box_page, tuple(sorted(box_ids))))
        head = [i for i in ctx.items if getattr(i, "role", "") == "court"]
        ctx.items = head + [block] + [i for i in ctx.items if i not in head]
        ctx.consumed.update(box_ids)

    docket = next((_DOCKET.match(t) for t in right_plain if _DOCKET.match(t)),
                  None)
    if docket is None:
        return NOTHING
    ctx.crit["docket_number"] = _norm(docket.group(1))
    if caption:
        ctx.crit.setdefault("parties", caption[:8])
    _hist = [t for t in right_plain if _COURT_BELOW.match(t)
             or _BELOW_NO.match(t)] + below
    if _hist:
        ctx.crit.setdefault("history", " ".join(_hist)[:2000])
    return ctx.result()


def _rail(pm) -> dict | None:
    """The caption's rail on ``pm``: {'x', 'top', 'bottom'}, or None.

    A rail is a COLUMN of '§' — glyphs stacked at one x — grown outward one
    contiguous step at a time, so a section sign standing somewhere else on
    the page (a footnote's 'art. IV, § 12') is barred by the gap bound
    however close its x happens to fall."""
    chars = [c for line in pm.lines for c in line.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if not chars:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    column = sorted((c for c in chars if abs(c["x0"] - x) <= 3.0),
                    key=lambda c: c["top"])
    if not column:
        return None
    run = [column[0]]
    for ch in column[1:]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    return {"x": float(x), "top": min(c["top"] for c in run),
            "bottom": max(c["top"] for c in run)}


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
    """The part of ``line`` lying on one side of the rail, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _strip_rail(text: str) -> str:
    """The glyph off whichever side pdfio glued it to. It is the drawn
    divider, not a word of either column."""
    text = text.strip()
    while text.startswith(_RAIL_GLYPH):
        text = text[len(_RAIL_GLYPH):].lstrip()
    while text.endswith(_RAIL_GLYPH):
        text = text[:-len(_RAIL_GLYPH)].rstrip()
    return text


def _right_role(parts: list) -> str:
    """What the right column is saying on this row. Each tenant by its own
    landmark; a runover line keeps company with `lower-court`, which is what
    the column carries whenever it is not the docket."""
    text = _strip_rail(_norm(" ".join(l.plain for l in parts)))
    if not text:
        return "caption"
    if _DOCKET.match(text):
        return "docket"
    return "lower-court"


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


def _row(parts: list, role: str):
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(1), align=m.Align.LEFT, role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    text = _strip_rail(text)
    return m.HmLine(
        text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _rows(pm, finder) -> list[list]:
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


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
