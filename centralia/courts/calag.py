"""Office of the Attorney General of California ('calag') — the COLON-RAIL
LETTERHEAD. Not a court: an opinion SERIES issued by an executive officer.

Everything unique to calag lives here. It imports core, never another court
file, and no other court file imports it.

WHAT THE COVER ACTUALLY IS. There is no caption, no parties, no docket in
the judicial sense, no panel and no byline anywhere in the document. What
page 1 prints is a LETTERHEAD over a two-column table, fenced twice:

    ┌───────────────────────────────────────────────────────────────────┐
    │           TO BE PUBLISHED IN THE OFFICIAL REPORTS   the notice     │
    │                                                                    │
    │             OFFICE OF THE ATTORNEY GENERAL          the office     │
    │                   State of California                              │
    │                                                                    │
    │                      ROB BONTA                      the OFFICER    │
    │                   Attorney General                  who signs      │
    │                                                                    │
    │                   _______________                   the letterhead │
    │                                                     divider, TYPED │
    │                              :                                     │
    │   OPINION                    :                      the RAIL — a   │
    │                              :   No. 24-501         column of ':'  │
    │        of                    :                      glyphs at one  │
    │                              :   April 2, 2025      x, with the    │
    │   ROB BONTA                  :                      paper's own    │
    │   Attorney General           :                      name, its      │
    │                              :                      officers, its  │
    │   CATHERINE BIDART           :                      number and its │
    │   Deputy Attorney General    :                      date           │
    │                                                                    │
    │ ═════════════════════════════════════════  the BOUNDARY, drawn     │
    │                                                                    │
    │ The HONORABLE MONIQUE LIMÓN, MEMBER OF THE STATE SENATE, has        │
    │ requested an opinion on a question relating to affordable housing.  │
    │                                                                    │
    │              QUESTION PRESENTED AND CONCLUSION                     │
    └───────────────────────────────────────────────────────────────────┘

THE RAIL IS THE DISPATCH, exactly as it is for pasuperct, pa and del: a
column of ':' glyphs at one x, found by the x of its own column and never
by a character count. Measured over all 42 records the rail column holds
10-13 glyphs and sits at x0 294.5 (39), 287.3 (1), 304.2 (1) or 333.5 (1)
— the office re-tabs it per document, so it is measured per record. No
rival ':' column on any of the 42 pages holds more than ONE glyph, which
is what makes the floor of 5 unmissable. No rail, no claim.

THE BLOCK IS FENCED TWICE, and the two fences are told apart by WHERE THEY
STAND relative to the rail, never by how they are drawn:

- the LETTERHEAD DIVIDER stands ABOVE the rail's first row. It is TYPED, a
  run of underscores centred on the page axis, 98pt (40 records), 162pt
  (untitled_3) or 228pt (untitled_4) wide.
- the BOUNDARY stands BELOW the rail's last row and runs the full measure.
  41 records DRAW it (a 468.2pt rect at y 385.1, once at 384.1, once at
  430.0 where a third officer is named, and 461.9pt on untitled_3); the
  1998 Lungren opinion (untitled_4) TYPES it instead, 420pt of underscores
  on a 612pt page. Either way it is the last row of the headmatter, and
  everything below it is the opinion.

Both fences are re-emitted: core draws them in `read_headmatter`, and that
pass only runs on rows a reader left behind, so a total claim has to draw
its own.

THE CLOSED VOCABULARY OF THIS PAPER. Counted over all 42 covers, the head
band prints six rows and no others: the publication notice (40 'TO BE
PUBLISHED IN THE OFFICIAL REPORTS', 2 '…OFFICIAL RECORDS'), 42 'OFFICE OF
THE ATTORNEY GENERAL', 42 'State of California', the officer's ALL-CAPS
name and the officer's title, then the divider. The rail's LEFT column
prints 42 'OPINION', 42 'of', the officer's name and title, and the
preparing deputy's name and title — 42 'Deputy Attorney General', once
also 'Senior Assistant Attorney General' (24-802, a three-officer cover
whose boundary is 45pt lower to fit). The RIGHT column prints exactly two
rows: 'No. <number>' and the issue date. There is no third tenant.

WHO SIGNS IT. The officer is not read by name and not read against a roll
of Attorneys General — the office changes and one record is signed by an
acting deputy. The rule is POSITIONAL: an ALL-CAPS row directly above a
mixed-case row whose text ends in 'Attorney General'. 40 covers are ROB
BONTA, one FRANCESCA R. GESSNER (Acting Chief Deputy Attorney General,
recusal — 23-601, which hangs a footnote off her title inside the caption)
and one DANIEL E. LUNGREN (1998). Reported to core as `announced_author`:
this paper carries no byline for core to build a writing from, and without
it every one of the 42 opinions came back unauthored.

WHAT THIS FILE DOES NOT DO. The requesting official's sentence ('The
HONORABLE … has requested an opinion on …') stands BELOW the boundary and
is the opinion's own first paragraph — the fence says so, and nothing is
lifted out of a writing. The question-presented / conclusion structure,
the footnotes and the paragraphing are all core's.

Corpus split over the 42 records: 42 `colon-rail letterhead`, 0 NOTHING;
within it 41 with a DRAWN boundary and 1 (untitled_4, 1998) with a TYPED
one.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

CALAG = register(CourtProfile(
    "calag", "Office of the Attorney General of California",
    # THE PAPER CARRIES NO BYLINE. The officer is announced on the cover
    # and this grammar exists only so core can parse that announcement
    # ('ROB BONTA, Attorney General') back into a name and a title. The
    # titles are the offices this series is signed from, as a closed list;
    # a prose sentence about the Attorney General cannot match, because the
    # prose parser requires an ALL-CAPS name before the comma.
    byline=BylineGrammar(
        style="prose",
        titles=("Attorney General",
                "Acting Attorney General",
                "Chief Deputy Attorney General",
                "Acting Chief Deputy Attorney General",
                "Senior Assistant Attorney General",
                "Deputy Attorney General")),
    # ONE OFFICER, ONE OPINION. There is no bench here, so there is nothing
    # to concur in or dissent from: a record that comes back as two
    # writings has been split, not read.
    single_writing=True,
    rollout="migrated",
))

STYLE = "colon-rail letterhead"

# --------------------------------------------------------------------------
# the rail — declared facts of THIS paper, measured over its own corpus
# --------------------------------------------------------------------------

_RAIL_GLYPH = ":"
# ca6's rail window: a glyph belongs to the rail when it stands in the
# rail's own COLUMN, never because of what character it is.
_RAIL_WINDOW = 3.0
# The 42 covers hold 10-13 glyphs in their rail column; no rival ':' column
# on any of them holds more than one.
_RAIL_FLOOR = 5
# A fence spans the MEASURE. The drawn boundary runs 461.9-468.2pt and the
# typed one 420pt, all on 612pt pages; the letterhead divider runs 98-228pt.
# The two are told apart by their side of the rail, so this floor only has
# to exclude ordinary prose and the 144pt footnote separator.
_FENCE_MEASURE = 0.6
# The letterhead divider, TYPED: a row of underscores and nothing else.
_TYPED_RULE = re.compile(r"^_{4,}$")
_AXIS_TOL = 24.0

# --------------------------------------------------------------------------
# the landmarks — a closed vocabulary, never a name read by wording
# --------------------------------------------------------------------------

# The office naming itself, over the two rows it sets it in.
_OFFICE = re.compile(
    r"^(?:OFFICE OF THE ATTORNEY GENERAL|State of California)$", re.I)
# The publication notice this series prints on every cover ('REPORTS' on 40,
# 'RECORDS' on 2).
_NOTICE = re.compile(r"^TO BE PUBLISHED IN THE OFFICIAL "
                     r"(?:REPORTS|RECORDS)\.?$", re.I)
# An OFFICE this series is signed from — the mixed-case row under a name.
# A closed list: the title is apparatus, the name is not read at all.
_TITLE_ROW = re.compile(
    r"^(?:Acting\s+)?(?:Chief\s+Deputy|Senior\s+Assistant|Deputy|Supervising"
    r"|Assistant)?\s*Attorney\s+General$", re.I)
# An ALL-CAPS officer name: 'ROB BONTA', 'FRANCESCA R. GESSNER',
# 'RYAN B. McCARROLL', 'MANUEL M. MEDEIROS'.
_NAME_ROW = re.compile(r"^[A-Z][A-Za-z.'’\- ]{3,40}$")
# What the paper calls itself, and the connective under it.
_PAPER = re.compile(r"^OPINION$", re.I)
_OF = re.compile(r"^of$")
# The right column's two tenants, each by its own landmark.
_NUMBER = re.compile(r"^Nos?\.\s*(\S.*?)\.?$")
_DATE = re.compile(
    r"^((?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4})\.?$", re.I)


# THE CRITERIA FIELD NAMES ARE THE MODEL'S — `Criteria` in centralia/model.py
# declares every one of them. A key written under an invented name is
# attached by setattr and never serializes: read as read, reported as
# nothing.


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _plain(row) -> str:
    """A visual row's text, with the superscript footnote mark the caption
    can hang on an officer's title left in place (23-601)."""
    return _norm(" ".join(l.plain for l in row))


def _rows(pm, finder) -> list[list]:
    """Page ``pm``'s visual rows, grouped by top, furniture removed. pdfio
    returns the rail glyph as its own piece on most rows and glued to the
    cell beside it on others (': ' + 'No. 24-501'), so the ROW is the unit."""
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


def _rail(pm) -> float | None:
    """The x of the table's typed divider on ``pm``, or None. A rail is a
    COLUMN: ':' glyphs stacked at one x, measured per record because the
    office re-tabs the table per document."""
    cols = Counter(round(c["x0"], 1) for l in pm.lines for c in l.chars
                   if (c.get("text") or "") == _RAIL_GLYPH)
    if not cols:
        return None
    x, _n = cols.most_common(1)[0]
    stack = sum(n for k, n in cols.items() if abs(k - x) <= _RAIL_WINDOW)
    if stack < _RAIL_FLOOR:
        return None
    return float(x)


def _rail_chars(line, rail_x: float) -> list:
    return [c for c in line.chars
            if (c.get("text") or "") == _RAIL_GLYPH
            and abs(c["x0"] - rail_x) <= _RAIL_WINDOW]


def _is_rail(group: list, rail_x: float) -> bool:
    return any(_rail_chars(l, rail_x) for l in group)


def _shed_rail(line, rail_x: float):
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. Identified by COLUMN, never by character."""
    rails = {id(c) for c in _rail_chars(line, rail_x)}
    if not rails:
        return line
    kept = [c for c in line.chars if id(c) not in rails]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept,
                    x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` on one side of the rail, or None. Split GLYPH BY
    GLYPH: pdfio returns ': ' fused to the docket beside it, and a
    whole-line test files that docket in the left column."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

@decider("headmatter.read", court="calag")
def read_headmatter_calag(model, geom, **_):
    """Read the Attorney General's colon-rail letterhead, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(pm, finder)
    if len(rows) < 8:
        return NOTHING
    rail_x = _rail(pm)
    if rail_x is None:
        return NOTHING
    railed = [_is_rail(g, rail_x) for g in rows]
    if not any(railed):
        return NOTHING
    first_rail = railed.index(True)
    last_rail = len(railed) - 1 - railed[::-1].index(True)

    # THE BOUNDARY: the first full-measure fence BELOW the rail's last row.
    # Drawn on 41 covers, typed on one; the side of the rail is what tells
    # it from the letterhead divider above, and the measure is what tells
    # it from the footnote separator further down the page.
    rail_bottom = max(l.top for l in rows[last_rail])
    fence_y = None
    fence_row = None
    for rule in sorted(pm.h_rules, key=lambda r: r.top):
        if rule.top > rail_bottom and rule.width >= pm.width * _FENCE_MEASURE:
            fence_y = rule.top
            break
    for idx in range(last_rail + 1, len(rows)):
        group = rows[idx]
        if not _TYPED_RULE.match(_plain(group).replace(" ", "")):
            continue
        span = max(l.x1 for l in group) - min(l.x0 for l in group)
        if span >= pm.width * _FENCE_MEASURE:
            if fence_y is None or group[0].top < fence_y:
                fence_y, fence_row = group[0].top, idx
            break
    if fence_y is None:
        return NOTHING              # no fence: the block has no end

    ctx = _Ctx()
    officer = ""                    # 'ROB BONTA, Attorney General'
    office: list[str] = []          # the two rows the office names itself in
    officers: list[str] = []        # every officer the cover names
    docket = None
    date = None
    paper = None

    # ---- the letterhead, above the rail ---------------------------------
    head = [(i, rows[i]) for i in range(first_rail)]
    for pos, (idx, group) in enumerate(head):
        text = _plain(group)
        if not text:
            continue
        if _TYPED_RULE.match(text.replace(" ", "")):
            ctx.rule(pm.number, group, span="center", typed=True)
            continue
        if _NOTICE.match(text):
            ctx.crit.setdefault("publication_status", "published")
            ctx.emit(group, "publication")
            continue
        if _OFFICE.match(text):
            office.append(text)
            ctx.emit(group, "court")
            continue
        # THE SIGNING OFFICER, read POSITIONALLY: an ALL-CAPS row directly
        # above a mixed-case row naming one of this series' offices. Never
        # against a roll of names — the office changes, and one record is
        # signed by an acting deputy.
        nxt = _plain(head[pos + 1][1]) if pos + 1 < len(head) else ""
        if (_NAME_ROW.match(text) and text == text.upper()
                and _TITLE_ROW.match(_strip_mark(nxt))):
            officer = f"{text}, {_strip_mark(nxt)}"
            ctx.emit(group, "author")
            continue
        if _TITLE_ROW.match(_strip_mark(text)) and officer:
            ctx.emit(group, "author")
            continue
        # A row at no position this cover uses is left to core rather than
        # tinted with a role that would be a guess.

    # ---- the rail's table ------------------------------------------------
    left: list = []
    right: list = []
    ids: set[int] = set()
    pending_name = None
    for idx in range(first_rail, last_rail + 1):
        group = sorted(rows[idx], key=lambda l: l.x0)
        ids.update(l.id for l in group)
        l_cells, r_cells = [], []
        for line in group:
            shed = _shed_rail(line, rail_x)
            if shed is None:
                continue            # the line WAS the rail
            for part, bucket in ((_side(shed, rail_x, "L"), l_cells),
                                 (_side(shed, rail_x, "R"), r_cells)):
                if part is not None:
                    bucket.append(part)
        if l_cells:
            text = _norm(" ".join(c.plain for c in l_cells))
            bare = _strip_mark(text)
            if _PAPER.match(text):
                role = "title"
                paper = text.upper()
            elif _OF.match(text):
                role = "title"
            elif _TITLE_ROW.match(bare):
                role = "author"
                if pending_name:
                    officers.append(f"{pending_name}, {bare}")
                    pending_name = None
            elif _NAME_ROW.match(text) and text == text.upper():
                role = "author"
                pending_name = text
            else:
                role = "case-info"
            left.append(_cell(l_cells, role, pm))
        if r_cells:
            text = _norm(" ".join(c.plain for c in r_cells))
            hit = _NUMBER.match(text)
            got = _DATE.match(text)
            if hit:
                role = "docket"
                docket = docket or _norm(hit.group(1))
            elif got:
                role = "date"
                date = date or _norm(got.group(1))
            else:
                role = "case-info"
            right.append(_cell(r_cells, role, pm))
    if left or right:
        ctx.caption(pm.number, left, right, sum(railed), ids)

    # ---- the boundary ----------------------------------------------------
    if fence_row is not None:
        ctx.rule(pm.number, rows[fence_row], span="full", typed=True)
    else:
        ctx.items.append(m.Rule(prov=m.Prov(pm.number), span="full"))

    # --- WHAT THE PAGE SAID, populated BEFORE it is judged ----------------
    # (wyo shipped its docket gate one line above the walk that fills it and
    # refused all 50 of its own correctly-read records.)
    if paper:
        ctx.crit["title"] = paper
    if docket:
        ctx.crit["docket_number"] = docket
    if date:
        ctx.crit["decision_date"] = date
    # THE OFFICE AS PRINTED, built from the rows it printed — never from a
    # constant, which would survive the office changing its own letterhead
    # and report a name the page does not carry.
    if office:
        ctx.crit["court"] = ", ".join(office)
    # WHO IS RESPONSIBLE FOR THE PAPER, in the model's own field for it.
    # There is no bench here, so `panel` is deliberately left empty — an
    # executive officer is not a panel of anything — and `judges` carries
    # the officers the cover names, the one who signs and the one who
    # prepared it, as printed.
    if officers:
        ctx.crit["judges"] = "; ".join(officers)
    if not officer and officers:
        officer = officers[0]

    # --- the gates: what this contract REQUIRES to have been read ---------
    if not (left and right):
        return NOTHING              # the rail carried no table
    if not docket:
        return NOTHING              # no opinion number: the table was unread
    ctx.crit["headmatter_style"] = STYLE
    out = ctx.result()
    # THE PAPER NAMES ITSELF 'OPINION' inside the rail, and that is the only
    # place it does. Left to core the document classifies UNKNOWN — the body
    # opens on the requesting official's sentence, not on a doc-type heading
    # — and its single unsigned writing typed `order`. Declared here (after
    # assembly, which is where core applies it, so the anchor that finds the
    # body is never removed) it is the opinion it says it is.
    out["doc_type_final"] = m.DocType.OPINION
    # THE OFFICER IS ANNOUNCED, NEVER SIGNED. Core parses it with this
    # court's own grammar and credits the lead writing — only where the
    # document prints no byline of its own, which it never does.
    if officer:
        out["announced_author"] = officer
    return out


def _strip_mark(text: str) -> str:
    """A title with the superscript footnote reference taken off it. 23-601
    hangs note 1 on 'Acting Chief Deputy Attorney General' inside the
    caption; the mark belongs to the row, not to anybody's office."""
    return re.sub(r"[\d*†‡]+$", "", _norm(text)).strip()


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def _cell(cells: list, role: str, pm):
    cells = sorted(cells, key=lambda l: l.x0)
    if not cells:
        return m.HmLine(text="", prov=m.Prov(pm.number), align=m.Align.LEFT,
                        role=role)
    text = ""
    for part in cells:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
            else piece
    return m.HmLine(
        text=text.strip(), prov=m.Prov(cells[0].page,
                                       tuple(c.id for c in cells)),
        align=m.Align.LEFT, x0=cells[0].x0, size=cells[0].size or 0.0,
        bold=all(bool(c.all_bold) for c in cells), role=role)


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
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.items.append(m.HmLine(
            text=text.strip(), prov=m.Prov(first.page,
                                           tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def caption(self, page: int, left: list, right: list, rail_rows: int,
                ids: set) -> None:
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=_RAIL_GLYPH,
            rail_rows=max(len(left), len(right), 1), style_id="colon-rail",
            fp={"rail": _RAIL_GLYPH, "rail_rows": rail_rows},
            prov=m.Prov(page, tuple(sorted(ids)))))
        self.consumed.update(ids)

    def rule(self, page: int, parts: list, span: str = "full",
             typed: bool = False) -> None:
        """A fence the page TYPED, re-emitted where it stands — a reader
        that claims the block inherits the job of drawing its fences."""
        self.items.append(m.Rule(
            prov=m.Prov(page, tuple(p.id for p in parts)),
            span=span, typed=typed))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
