"""Supreme Court of Guam ('guam').

Everything unique to guam lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THIS COURT PRINTS ONE PAPER, and prints it the same way 32 times out of 32.
Every record opens `IN THE SUPREME COURT OF GUAM`, names itself `OPINION`,
gives its own citation, and signs on the page after the appearances:

    ┌─────────────────────────────────────────────────────────────────┐
    │              IN THE SUPREME COURT OF GUAM                       │  court
    │                                                                 │
    │                   PEOPLE OF GUAM,                               │  the CAPTION,
    │                  Plaintiff-Appellee,                            │  one column,
    │                         v.                                      │  centred on the
    │                   AJ MUNA TOVES,                                │  page axis
    │                 Defendant-Appellant.                            │
    │                                                                 │
    │           Supreme Court Case No. CRA24-005                      │  docket
    │           Superior Court Case No. CF0510-22                     │  the court below's
    │                                                                 │
    │                       OPINION                                    │  title
    │                Cite as: 2024 Guam 14                            │  citation
    │                                                                 │
    │        Appeal from the Superior Court of Guam                    │  lower court
    │      Argued and submitted on October 21, 2024                    │  submitted
    │                   Hagåtña, Guam                                  │  …and its SEAT
    │                                                                 │
    │  Appearing for Defendant-Appellant:  Appearing for Plaintiff-…   │  the APPEARANCES,
    │  Stephen P. Hattori, Esq.            Nathan M. Tennyson, Esq.    │  two columns with
    │  Public Defender                     Acting Deputy Attorney …    │  nothing drawn
    │  ─────────────────────────── page 2 ─────────────────────────    │  between them
    │  BEFORE: ROBERT J. TORRES, Chief Justice; F. PHILIP CARBULLIDO, │  panel
    │  Associate Justice and KATHERINE A. MARAMAN, Associate Justice.  │
    │  TORRES, C.J.:                                                  │  …and the writing
    └─────────────────────────────────────────────────────────────────┘

Counted over all 32 records: 32 mastheads, 32 `OPINION`s, 32 `Cite as:` rows,
32 `Appeal from the Superior Court of Guam`, 32 `BEFORE:` rosters, 32 'Argued
and submitted on …' dates, 32 Supreme Court numbers, 31 Superior Court
numbers (an original petition has none) and 31 'Hagåtña, Guam' seats. There
is no second format and no exception to plan around — which is why this
reader recognises rows and never guesses: a row this paper does not print is
left to core.

THE CAPTION IS ONE COLUMN, and no second column is invented (the iowactapp /
nmctapp / scctapp ruling). Its party names are set 14pt bold on the page
axis, its status labels 12pt beneath them, and its connectives are the same
14pt bold as the names ('v.', 'and'). Nothing is drawn anywhere on the page.

THE APPEARANCES ARE TWO COLUMNS WITH NOTHING BETWEEN THEM, and the gutter is
measured, not assumed: over the 176 appearance lines of the corpus the left
column sets x0 72.1-116.8 and the right x0 311.5-343.9, so the page axis
(306.0) separates them. It has to separate them CHAR BY CHAR, though —
`guam_waterworks` returns 'Appearing for Real Party in Interest-Appellant:
Appearing for Petitioner-Appellee:' as ONE run reaching x1 489.2, and a
whole-line test files the second heading in the first column (the ca6
lesson). The block is published as a CaptionBlock with `rail=None`, which is
what the model means by a whitespace gutter, so the renderer sets the two
rosters side by side as the page does and the casebody reads down one column
and then the other.

THE APPEARANCES CAN RUN PAST PAGE 1 — three records (`guam_waterworks`,
`kamlesh_k._hemlani`, `sh_enterprises`) carry them onto page 2 and sign on
page 3 — so the walk runs to the byline over as many as three pages.

THE PANEL IS TWO ROWS and the second has no landmark ('Associate Justice;
and KATHERINE A. MARAMAN, Associate Justice.'), so the roster is taken as a
BLOCK: from 'BEFORE:' to the byline. The bench sits in four combinations
across the corpus and one record seats a Justice Pro Tempore, so nothing is
matched against a roll of names.

WHAT THIS FILE DOES NOT DO. The byline grammar ('TORRES, C.J.:',
'CARBULLIDO, P.J.:', 'MARAMAN, J.:', 'PER CURIAM:' — 31 signed and one per
curiam), the bracketed paragraph numbers this court writes ('[1]'), the
footnotes and the paragraphing are all core's.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(r"^IN THE SUPREME COURT OF GUAM$", re.I)
_MAX_PAGES = 3
_AXIS_TOL = 24.0

# The two numbers, each by its own court's name. The colon is optional —
# 'Supreme Court Case No.: CVA25-014' occurs twice.
_OWN_NO = re.compile(r"^Supreme Court Case Nos?\.?:?\s*(.+)$", re.I)
_BELOW_NO = re.compile(
    r"^(?:Consolidated\s+)?Superior Court Case Nos?\.?:?\s*(.+)$", re.I)
# '(consolidated with CRA23-009)' — this court's OTHER appeal, printed under
# its own number in parentheses.
_ALSO_NO = re.compile(
    r"^\(?(?:consolidated|coordinated)\s+with\s+(.+?)\)?$", re.I)
# A RUNOVER of case numbers: the court below's list can need a second row
# ('CF0097-86; CF0194-90; CF0214-91; CF0570-96'). Bare numbers only — a row
# of prose cannot match.
_BARE_NOS = re.compile(
    r"^[A-Z]{1,3}\d{3,6}-\d{2}(?:\s*[;,]\s*[A-Z]{1,3}\d{3,6}-\d{2})*"
    r"[;,]?$")
_TITLE = re.compile(r"^(OPINION|ORDER|DISSENTING OPINION"
                    r"|CONCURRING OPINION)$", re.I)
_CITE = re.compile(r"^Cite as:\s*(.+)$", re.I)
# 'Appeal from the Superior Court of Guam' — and the forms an original
# proceeding uses instead.
_ORIGIN = re.compile(
    r"^(?:Appeal|Appeals|Petition|Original\s+Petition|Certified\s+Question"
    r"|On\s+certification|Writ)\b", re.I)
_SUBMITTED = re.compile(
    r"^(Argued and submitted|Submitted|Argued|Reargued)\b[^,]*?\s+on\s+(.+)$",
    re.I)
# The court's seat, printed under the date it sat.
# The court's seat, printed under the date it sat — or how it sat, when it
# sat remotely ('Via Zoom video conference', people_of_guam_v._jared_john_
# santos).
_SEAT = re.compile(r"^(?:Hag[aå]t[nñ]a,\s*Guam|Via\s+\S.{2,40})$", re.I)
_APPEARING = re.compile(r"^Appearing for\b", re.I)
_PANEL = re.compile(r"^BEFORE\b", re.I)
# 'TORRES, C.J.:' / 'CARBULLIDO, P.J.:' / 'MARAMAN, J.:' / 'PER CURIAM:'.
# The STOP, not the parse: core's grammar reads it.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-zÑñ’'\-]+(?:\s+[A-Z][A-Za-zÑñ’'\-]+)?,\s*"
    r"(?:C\.\s?J\.|P\.\s?J\.|A\.\s?J\.|J\.)|PER CURIAM)\s*[:.]?$")
_PIVOT = re.compile(r"^(?:v\.?|vs\.?|and)$", re.I)
_STATUS_WORDS = frozenset(
    ("plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
     "petitioners", "respondent", "respondents", "appellant", "appellants",
     "appellee", "appellees", "cross", "third", "party", "real", "in",
     "interest", "deceased", "and", "the", "of", "intervenor", "intervenors",
     "nominal", "movant", "objector", "trustee", "pro", "se", "counter",
     "counterclaimant", "counterdefendant"))


def _norm(text: str) -> str:
    return " ".join((text or "").split())


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


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the gutter, or None. Split
    CHAR BY CHAR: whether pdfio broke the row at its column gap is an
    accident of how wide the gap happened to be."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _cell(parts: list, page: int):
    """One column's cell on one row — the empty one keeps its place."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                        role="counsel")
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role="counsel")


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
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

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


@decider("headmatter.read", court="guam")
def read_headmatter_guam(model, geom, **_):
    """Read Guam's centred caption and its two-column appearances, or
    NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    stream: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for group in _rows(pm, finder):
            stream.append((pm, sorted(group, key=lambda l: l.x0)))
    if not stream:
        return NOTHING
    if not any(_MASTHEAD.match(_norm(" ".join(l.plain for l in g)))
               for _pm, g in stream[:4]):
        return NOTHING

    ctx = _Ctx()
    caption_rows: list[str] = []
    appear: list = []           # (page, left parts, right parts)
    band = "head"
    mast_seen = False
    last_no = None

    for pm, pieces in stream:
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        centred = abs((pieces[0].x0 + max(l.x1 for l in pieces)) / 2
                      - pm.width / 2) <= _AXIS_TOL

        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            mast_seen = True
            band = "caption"
            continue
        if not mast_seen:
            continue
        if _BYLINE.match(text) and len(text) < 34:
            break                                   # the writing begins

        # THE APPEARANCES, once opened, run to the roster: their rows are a
        # roster's rows and carry no landmark of their own.
        if _APPEARING.match(text):
            band = "appearances"
        if band == "appearances" and not _PANEL.match(text):
            mid = pm.width / 2
            l_parts, r_parts = [], []
            for line in pieces:
                for want, bucket in (("L", l_parts), ("R", r_parts)):
                    part = _side(line, mid, want)
                    if part is not None:
                        bucket.append(part)
            appear.append((pm.number, l_parts, r_parts))
            ctx.consumed.update(l.id for l in pieces)
            continue

        # THE ROSTER IS A BLOCK: 'BEFORE: …' and the row under it, which
        # says 'Associate Justice; and KATHERINE A. MARAMAN, Associate
        # Justice.' and would be claimed by nothing.
        if _PANEL.match(text) or band == "panel":
            band = "panel"
            if "panel_line" in ctx.crit:
                ctx.crit["panel_line"] = _norm(
                    f"{ctx.crit['panel_line']} {text}")
            else:
                ctx.crit["panel_line"] = text
            ctx.emit(pieces, "panel", centre=False)
            continue

        own = _OWN_NO.match(text)
        if own:
            band = "case-info"
            numbers = _numbers(own.group(1))
            ctx.crit.setdefault("docket_number", numbers[0])
            if numbers[1:]:
                ctx.crit.setdefault("other_dockets", numbers[1:])
            ctx.emit(pieces, "docket", centre=centred)
            last_no = "own"
            continue
        below = _BELOW_NO.match(text)
        if below:
            band = "case-info"
            ctx.crit.setdefault("lower_court_docket",
                                _numbers(below.group(1)))
            ctx.emit(pieces, "lower-court", centre=centred)
            last_no = "below"
            continue
        also = _ALSO_NO.match(text)
        if also and band == "case-info":
            ctx.crit.setdefault("other_dockets", []).extend(
                _numbers(also.group(1)))
            ctx.emit(pieces, "docket", centre=centred)
            continue
        if last_no == "below" and _BARE_NOS.match(text):
            ctx.crit.setdefault("lower_court_docket", []).extend(
                _numbers(text))
            ctx.emit(pieces, "lower-court", centre=centred)
            continue
        if _TITLE.match(text):
            band = "case-info"
            ctx.crit.setdefault("title", text)
            ctx.emit(pieces, "title")
            # An unsigned paper would have to open on this row; offered
            # back, the headmatter loses one row instead of the document
            # losing its writing.
            ctx.anchor.extend(p.id for p in pieces)
            continue
        cite = _CITE.match(text)
        if cite:
            ctx.crit.setdefault("citation", _norm(cite.group(1)))
            ctx.emit(pieces, "citation")
            continue
        if _ORIGIN.match(text) and len(text) < 120:
            ctx.crit.setdefault("lower_court", text)
            ctx.emit(pieces, "lower-court", centre=centred)
            continue
        sub = _SUBMITTED.match(text)
        if sub:
            ctx.crit.setdefault("submitted", _norm(sub.group(2)))
            ctx.emit(pieces, "date", centre=centred)
            continue
        if _SEAT.match(text):
            # The court's SEAT, which is what `court` covers — its name, its
            # division, where it sits.
            ctx.emit(pieces, "court", centre=centred)
            continue

        if band == "caption" and centred:
            caption_rows.append(text)
            ctx.emit(pieces, "caption")
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if appear:
        ctx.items.append(_appearances(appear))
    sides = _sides(caption_rows)
    if sides:
        ctx.crit.setdefault("parties", list(sides))
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    elif caption_rows:
        ctx.crit.setdefault("parties", [_norm(" ".join(caption_rows))[:300]])
    if "docket_number" not in ctx.crit:
        return NOTHING              # no number read: the block was not read
    return ctx.result()


def _numbers(text: str) -> list[str]:
    """The case numbers a row lists, however it separates them: this court
    writes both 'CM0432-22, CF0095-23' and 'CF0239-85; CF0058-86; …'."""
    return [n.strip() for n in re.split(r"[;,]", _norm(text)) if n.strip()]


def _appearances(rows: list) -> m.CaptionBlock:
    """The two rosters as the page sets them: side by side, over a gutter
    nothing is drawn in."""
    left, right = [], []
    page = rows[0][0]
    ids: set[int] = set()
    for pg, l_parts, r_parts in rows:
        left.append(_cell(l_parts, pg))
        right.append(_cell(r_parts, pg))
        ids.update(p.id for p in l_parts + r_parts)
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    return m.CaptionBlock(
        left=left, right=right, rail=None, rail_rows=len(left),
        style_id="open-gutter", fp={"rail": None},
        prov=m.Prov(page, tuple(sorted(ids))))


def _sides(caption_rows: list[str]) -> tuple[str, str] | None:
    """The two party names either side of the pivot — built from the party
    NAMES, never by joining the caption wholesale (the ca6 reading): the
    status labels and the pivot are apparatus, not names."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        if _PIVOT.match(flat):
            if flat.lower() != "and":
                side = right
                seen_pivot = True
            continue
        words = [w.strip(",.;-/ ").lower()
                 for w in flat.replace("-", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))
