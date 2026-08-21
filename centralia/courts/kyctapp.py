"""Kentucky Court of Appeals ('kyctapp').

Everything unique to kyctapp lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — the same paper its Supreme Court prints (see ky.py), set in a
smaller display type and closed by a rule the court TYPES rather than draws.

    ┌────────────────────────────────────────────────────────────────────┐
    │            RENDERED:  AUGUST 7, 2026; 10:00 A.M.                   │  the release
    │                  NOT TO BE PUBLISHED                               │  publication
    │            Commonwealth of Kentucky          22pt — the masthead,   │
    │                 Court of Appeals             two rows, not one      │
    │                NO. 2026-CA-0080-ME           the docket             │
    │ J.C. AND R.C.                                        APPELLANTS    │  the caption,
    │            APPEAL FROM LAWRENCE FAMILY COURT                       │  roles flushed
    │ v.         HONORABLE ADAM O'BRYAN, JUDGE                           │  right, courts
    │            ACTION NO. 21-J-00001-003                               │  below centred
    │ COMMONWEALTH OF KENTUCKY,                            APPELLEES     │
    │                        OPINION                    what it is        │
    │                      AFFIRMING                    what it did       │
    │                    ** ** ** ** **   <- the rule, in TYPE            │
    │ BEFORE:  ECKERLE, L. JONES, AND KAREM, JUDGES.    who sat           │
    │ KAREM, JUDGE:  J.C. and R.C. are the grandparents …  the writing     │
    └────────────────────────────────────────────────────────────────────┘

---- kyctapp's declared facts (measured over all 42 records) ---------------

THE MASTHEAD IS TWO ROWS AND THE ONLY TYPE ABOVE THE MEASURE. 'Commonwealth
of Kentucky' over 'Court of Appeals', 22pt against a 14pt paper, on 42 of 42
— and NOTHING else on any cover is set above body size, so the dispatch is
the size and the words together and never an ordinal. The court's name is
also printed as a PARTY on 13 records ('COMMONWEALTH OF KENTUCKY,' at body
size, 14pt); the size is what tells the masthead from the litigant.

THE BLOCK IS THREE ZONES, exactly as ky's is: the parties at the left rail
(x0 72-75), their ROLE flushed to the right margin on the same printed line,
and the court below CENTRED on the page axis between one party group and the
next. So a row is read PIECE BY PIECE and never joined, or the role welds
onto the end of the party's name.

WHAT CLOSES THE BLOCK IS A RULE THE COURT TYPES: '** ** ** ** **', centred,
on 42 of 42. It is a Rule and not a Divider — the page really does print it —
so it renders, and it renders as typed.

BELOW THE RULE the court prints who sat ('BEFORE: …, JUDGES.', 42 of 42,
which may WRAP onto a second row) and then signs, and the signature opens the
writing. The walk therefore ends at the byline, which is the one row it must
never claim.

THE BLOCK MAY RUN ONTO PAGE 2. commonwealth_of_kentucky_v._kendall_daugherty
consolidates two appeals and its title band, rule and roster all print on the
second sheet, so the walk is bounded at two pages and not one.

THE TITLE BAND IS ONE ROW OR TWO, and the court writes it four ways —
measured over the 42: 'OPINION' over its disposition (36), 'MEMORANDUM
OPINION AFFIRMING' entire (a paper that names itself and disposes in one
row), 'OPINION AND ORDER' over 'AFFIRMING', and 'OPINION DISMISSING APPEAL'
over 'AND REMANDING' — a disposition that WRAPS. So the band is read as
'every centred row from the one naming the paper down to the typed rule',
the first row being the title and the rest the disposition. Nine distinct
dispositions appear; none is a closed set worth writing down.

'FROM MONTGOMERY CIRCUIT COURT' — with no 'APPEAL' in front of it — is how
one record states its origin, so the leader is optional. Read as a party it
put a court in the caption.

COUNSEL IS PRINTED AT THE END, under its own labels, in TWO COLUMNS over a
whitespace gutter: 'BRIEFS FOR APPELLANTS:' at the rail against 'BRIEFS FOR
APPELLEE …:' at x0 302. Emitted in printed-row order the two columns
interleave and every printed row makes two rendered ones (wva's lesson), so
the block is emitted COLUMN BY COLUMN, which is also the order it is read in.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

KYCTAPP = PROFILES["kyctapp"]
STYLE = "flush-role cover"

_MASTHEAD_1 = re.compile(r"^Commonwealth of Kentucky$", re.I)
_MASTHEAD_2 = re.compile(r"^Court of Appeals$", re.I)
# 22pt on every cover against a 14pt measure; the litigant of the same name
# is set at the measure.
_DISPLAY_MIN = 18.0
_AXIS_TOL = 10.0
# HOW FAR THE BLOCK MAY RUN, measured by the page its typed rule prints on:
# p1 on 29 records, p2 on 5, p3 on 4, p4 on 1 and p7 on 3 — the prison cases
# consolidate a dozen appeals and set a docket, a caption and a court below
# for every one of them. Bounded at two pages the walk stopped mid-caption on
# 8 records and their title, roster and disposition went unread. The BYLINE is
# the real terminator; this is only the backstop that keeps a mis-dispatch
# from eating a document.
_MAX_PAGES = 8

_RENDERED = re.compile(r"^RENDERED:\s*(.+)$", re.I)
_PUBLICATION = re.compile(r"^(?:NOT\s+)?TO BE PUBLISHED$", re.I)
# 'NO. 2026-CA-0080-ME' / 'NOS. 2025-CA-1147-MR AND 2025-CA-1148-MR'
_DOCKET = re.compile(
    r"^NOS?\.\s*\d{4}-CA-\d{4}(?:-[A-Z]{1,3})?"
    r"(?:\s*(?:,|AND|&)\s*(?:NOS?\.\s*)?\d{4}-CA-\d{4}(?:-[A-Z]{1,3})?)*\.?$",
    re.I)
_PARTY_ROLE = re.compile(
    r"^(?:APPELLANT|APPELLEE|MOVANT|RESPONDENT|PETITIONER|CROSS-APPELLANT"
    r"|CROSS-APPELLEE|REAL PARTY IN INTEREST|INTERVENOR|AMICUS CURIAE"
    r"|APPELLANT/CROSS-APPELLEE|APPELLEE/CROSS-APPELLANT)S?$", re.I)
_PIVOT = re.compile(r"^V\.?$|^VS\.?$", re.I)
# Where the case came from. The leader is OPTIONAL — one record opens on
# 'FROM MONTGOMERY CIRCUIT COURT'.
_ORIGIN = re.compile(
    r"^(?:APPEAL|ORIGINAL ACTION|PETITION FOR REVIEW|ON REVIEW|REVIEW)?\s*"
    r"FROM\s+[A-Z].*\b(?:COURT|BOARD|COMMISSION|CABINET|COMMONWEALTH)\b",
    re.I)
_LOWER_JUDGE = re.compile(r"^HONORABLE\b", re.I)
_LOWER_NO = re.compile(
    r"^(?:ACTION|CASE|INDICTMENT|CIVIL ACTION|CLAIM|FILE)\s+NOS?\.", re.I)
# The paper names itself, and the row is centred.
_TITLE = re.compile(r"^(?:MEMORANDUM\s+)?OPINION\b", re.I)
# The rule the court TYPES.
_TYPED_RULE = re.compile(r"^(?:\*+\s*)+\*+$")
_PANEL = re.compile(r"^BEFORE\s*:", re.I)
_JOINT = re.compile(r"^AND$", re.I)
# The closing appearances.
_COUNSEL_LABEL = re.compile(
    r"^(?:BRIEFS?|COUNSEL|ATTORNEYS?|NO BRIEF|ORAL ARGUMENT)\b", re.I)
_CLOSING_PAGES = 3
_COUNSEL_ROW_MAX = 70
# THE ROLE COLUMN IS NOT AT A FIXED MEASURE. Bucketed over every role row on
# every cover, x0 falls at 450 on 107 rows, 400 on 8 and 300 on 7 — so a
# 0.60-of-the-sheet gutter (367pt) drops the 7 that start at 300, and
# 'APPELLEES' was read as another party's NAME and filed in the left column.
# The role WORD is a closed set, so it can carry the decision by itself; all
# the position has to say is that the row is not at the rail, which a party
# name always is.
_ROLE_CLEAR_OF_RAIL = 60.0


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="kyctapp")
def read_headmatter_kyctapp(model, geom, **_):
    """Read the Court of Appeals' cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = geom.body_size if geom and geom.body_size else 14.0
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(KYCTAPP.byline)

    rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
        rows.extend(_rows(pm, finder))
    if len(rows) < 4:
        return NOTHING

    # THE DISPATCH: the two-row masthead in display type, in the opening rows
    # — never at a fixed index, because the two stamps above it are set on
    # some records at the axis and on others flush right.
    mast = None
    for idx, group in enumerate(rows[:6]):
        text = _norm(" ".join(l.plain for l in group))
        if not (_MASTHEAD_1.match(text)
                and (group[0].size or 0.0) >= _DISPLAY_MIN):
            continue
        nxt = _norm(" ".join(l.plain for l in rows[idx + 1])) \
            if idx + 1 < len(rows) else ""
        if _MASTHEAD_2.match(nxt):
            mast = idx
            break
    if mast is None:
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    below: list[str] = []
    dispo: list[str] = []
    panel: list[str] = []
    in_title = False
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        width = model.pages[first.page - 1].width
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - width / 2) <= _AXIS_TOL

        # THE SIGNATURE ENDS THE WALK and is never claimed: it opens the
        # writing, and a reader that takes it leaves the document with no
        # author and no opinion.
        if parser.parse(text) is not None and not _PANEL.match(text):
            break

        rendered = _RENDERED.match(text)
        if rendered:
            ctx.crit.setdefault("decision_date", _norm(rendered.group(1)))
            ctx.emit(pieces, "date", centre=centred)
            continue
        if _PUBLICATION.match(text):
            ctx.crit.setdefault(
                "publication_status",
                "unpublished" if text.upper().startswith("NOT")
                else "published")
            ctx.emit(pieces, "publication", centre=centred)
            continue
        if (_MASTHEAD_1.match(text) or _MASTHEAD_2.match(text)) \
                and (first.size or 0.0) >= _DISPLAY_MIN:
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            _dk = [t.strip(" .") for t in re.split(r",|\bAND\b|&", text, flags=re.I)
                   if t.strip(" .")]
            _dk = [re.sub(r"^NOS?\.\s*", "", t, flags=re.I) for t in _dk]
            if not ctx.crit.get("docket_number"):
                ctx.crit["docket_number"] = _dk[0]
                if _dk[1:]:
                    ctx.crit["other_dockets"] = _dk[1:]
            else:
                ctx.crit.setdefault("other_dockets", []).extend(_dk)
            ctx.emit(pieces, "docket")
            continue
        # THE TITLE BAND opens on the row that names the paper and runs to
        # the typed rule; the first row is the title, the rest the
        # disposition — 'OPINION DISMISSING APPEAL' wraps onto 'AND
        # REMANDING', and 'MEMORANDUM OPINION AFFIRMING' says both at once.
        if centred and _TITLE.match(text):
            in_title = True
            ctx.emit(pieces, "title")
            _rest = _TITLE.sub("", text, count=1).strip(" ,.")
            if _rest:
                dispo.append(_rest)
            continue
        if _TYPED_RULE.match(text):
            in_title = False
            ctx.rule(pieces)
            continue
        if in_title and centred:
            dispo.append(text)
            ctx.emit(pieces, "disposition")
            continue
        if _PANEL.match(text) or (panel and not centred
                                  and text.rstrip(".").upper().endswith(
                                      "JUDGES")):
            # 'BEFORE: THOMPSON, CHIEF JUDGE; CALDWELL AND A. JONES,' wraps
            # onto 'JUDGES.' — one roster, two printed rows.
            panel.append(text)
            ctx.emit(pieces, "panel", centre=False)
            continue
        if panel:
            # THE ROSTER CLOSES THE BLOCK, and it has to — the signature
            # cannot be relied on to do it, because the court does not always
            # sign. crystal_blair-lewis prints 'MEMORANDUM OPINION AFFIRMING'
            # over the rule, names who sat, and then simply begins, so a walk
            # that stops only at a byline ran on into the opinion and claimed
            # its first pages as caption rows. Who sat is the last thing the
            # court prints before it speaks.
            break
        if _JOINT.match(text) and not centred:
            # The consolidation joint between two docket-and-caption pairs.
            ctx.flush_caption()
            ctx.emit(pieces, "case-info", centre=False)
            continue

        # A ROW IN THREE ZONES, read piece by piece.
        for piece in pieces:
            one = _norm(piece.plain)
            if not one:
                continue
            right = piece.x0 > body_x0 + _ROLE_CLEAR_OF_RAIL
            mid = (piece.x0 + piece.x1) / 2
            middle = (piece.x0 > body_x0 + 20.0
                      and abs(mid - width / 2) <= 60.0)
            if right and _PARTY_ROLE.match(one):
                ctx.cap_right(piece)
                continue
            if _ORIGIN.match(one) or _LOWER_JUDGE.match(one) \
                    or _LOWER_NO.match(one) or middle:
                below.append(one)
                if _LOWER_NO.match(one):
                    ctx.crit.setdefault("lower_court_docket", []).append(
                        re.sub(r"^(?:ACTION|CASE|INDICTMENT|CIVIL ACTION"
                               r"|CLAIM|FILE)\s+NOS?\.\s*", "", one,
                               flags=re.I).strip(" ."))
                elif _ORIGIN.match(one):
                    ctx.crit.setdefault("lower_court", one)
                ctx.flush_caption()
                ctx.emit([piece], "lower-court")
                continue
            if _PIVOT.match(one):
                ctx.cap_left(piece)
                continue
            caption.append(one)
            ctx.cap_left(piece)
    ctx.flush_caption()

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("parties", caption[:8])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
    if dispo:
        ctx.crit.setdefault("disposition", " ".join(dispo).strip(" ,."))
    if panel:
        ctx.crit.setdefault(
            "judges", re.sub(r"^BEFORE\s*:\s*", "", " ".join(panel),
                             flags=re.I).strip(" ."))
    _read_closing_counsel(ctx, model, finder)
    ctx.crit["headmatter_style"] = STYLE
    return ctx.result()


def _read_closing_counsel(ctx, model, finder) -> None:
    """The appearances the court prints at the END, in two columns.

        BRIEFS FOR APPELLANTS:          BRIEFS FOR APPELLEE
                                        COMMONWEALTH OF KENTUCKY, CABINET
        Jacob Thomas Moak               FOR HEALTH AND FAMILY SERVICES:
        Prestonsburg, Kentucky
                                        R. Jason Greer
                                        Louisa, Kentucky

    Emitted in printed-row order those two columns interleave, and one
    printed row becomes two rendered ones. So the gutter is MEASURED — the
    widest recurring gap between the rail and the second column — and each
    column is emitted whole, top to bottom, which is the order the block is
    read in.
    """
    pages = model.pages[-_CLOSING_PAGES:] if len(model.pages) > _CLOSING_PAGES \
        else model.pages
    lines: list = []
    for pm in pages:
        lines.extend(l for l in sorted(pm.lines, key=lambda l: (l.top, l.x0))
                     if l.plain.strip() and not finder.kind(pm, l))
    if not lines:
        return
    rail = min(l.x0 for l in lines)

    def _is_prose(line) -> bool:
        """A row of the court's own writing: it opens on the paragraph indent,
        or it fills the measure. An appearance is a short row at a column."""
        return (line.x0 > rail + 6.0
                and abs(line.x0 - rail) < 120.0) \
            or len(_norm(line.plain)) > _COUNSEL_ROW_MAX

    start = None
    for i, line in enumerate(lines):
        if not _COUNSEL_LABEL.match(_norm(line.plain)):
            continue
        if any(_is_prose(l) for l in lines[i:]):
            continue
        start = i
        break
    if start is None:
        return
    block = lines[start:]
    # THE GUTTER, measured on the block itself: the second column opens at
    # the smallest x0 that stands clear of the rail by more than a tab.
    seconds = sorted({round(l.x0, 1) for l in block if l.x0 > rail + 100.0})
    gutter = seconds[0] if seconds else None
    def _row(line):
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role="counsel")

    left = [l for l in block if gutter is None or l.x0 < gutter - 1.0]
    right = [l for l in block if gutter is not None and l.x0 >= gutter - 1.0]
    ctx.consumed.update(l.id for l in block)
    if left and right:
        # THE PAGE SETS TWO COLUMNS, so the block is ONE two-column object —
        # the same structure the caption uses — over the whitespace gutter
        # the page leaves. Emitted as a flat list of rows it renders as one
        # tall column and the appellant's counsel reads as the appellee's.
        ctx.attorneys.append(m.CaptionBlock(
            left=[_row(l) for l in left], right=[_row(l) for l in right],
            rail=None, prov=m.Prov(block[0].page, (block[0].id,))))
        return
    for line in left or right:
        ctx.attorneys.append(_row(line))


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
        self._left: list = []
        self._right: list = []
        self.attorneys: list = []

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        if role != "caption":
            self.flush_caption()
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

    def rule(self, group: list) -> None:
        """The court TYPED a rule, so it renders as one."""
        self.flush_caption()
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    # ---- the paired caption ----------------------------------------------
    def _row(self, line, role: str):
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role)

    def cap_left(self, line) -> None:
        self._left.append(self._row(line, "caption"))
        self.consumed.add(line.id)

    def cap_right(self, line) -> None:
        self._right.append(self._row(line, "caption"))
        self.consumed.add(line.id)

    def flush_caption(self) -> None:
        if self._left and self._right:
            self.items.append(m.CaptionBlock(
                left=list(self._left), right=list(self._right), rail=None,
                prov=self._left[0].prov))
        else:
            self.items.extend(self._left or self._right)
        self._left, self._right = [], []

    def result(self) -> dict:
        self.flush_caption()
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
