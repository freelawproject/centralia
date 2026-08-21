"""Office of the Attorney General of Texas ('texag').

THIS IS NOT A COURT'S PAPER, and nothing in it answers to a court caption.
There are no parties, no docket, no panel and no court below. A Texas
Attorney General opinion is a LETTER: the Attorney General writes back to
the official who asked him a question, on the office's own letterhead, and
signs it `Very truly yours,`. The reader below reads that letter's cover and
nothing else.

WHAT THE COVER IS. Page one sets six things, always in this order:

    ┌─────────────────────────────────────────────┐
    │                 KEN PAXTON                  │  the LETTERHEAD:
    │          ATTORNEY GENERAL OF TEXAS          │  a 14pt name over
    │                 (the seal)                  │  a ~7.8pt title
    │                                             │
    │               February 5, 2025              │  the DATE, centred
    │                                             │
    │  The Honorable Charles Schwertner           │  the REQUESTOR,
    │  Chair, Senate Cttee on Business & Commerce │  flush at the body
    │  Texas State Senate                         │  rail: name, office,
    │  Post Office Box 12068                      │  body, and the
    │  Austin, Texas 78711-2068                   │  postal address
    │                                             │
    │      Opinion No. KP-0480                    │  the OPINION NUMBER,
    │                                             │  bold, set in 36pt
    │      Re: Whether House Bill 1763 and …      │  the QUESTION, at the
    │      codified in chapter 1369 of the …      │  same 36pt indent,
    │      … circumstances (RQ-0539-KP)           │  closing with the
    │                                             │  REQUEST number
    │  Dear Senator Schwertner:                   │  the SALUTATION —
    │                                             │  the letter begins
    │      You ask about the enforceability of …  │
    └─────────────────────────────────────────────┘

THE LANDMARK IS THE INDENT, NOT THE WORDING. Everything the letter says TO
its addressee is set flush at the body rail; everything that identifies the
OPINION — its number and the question it answers — is set in 36pt from that
rail, and its runovers are set in with it. That 36pt ledger is the contract,
and it holds on 41 of the 42 records at x0 = 108.0 exactly against a 72.0
body rail. The forty-second (KP-0506) has a raster page one with no text
layer at all; there is no cover to read, so the reader declines it and
claims only the closing band.

WHERE THE COVER ENDS IS A GAP, NOT A WORD. Inside the `Re:` block the rows
sit one leading apart (13.8pt on a 14.0pt lead). Between the cover's
elements the page stands off 22.8–41.7pt — 1.6× the leading at the tightest.
So the question block ends at the first row that is either out of the ledger
indent or more than 1.5 leadings below its predecessor, and the reader stops
there. That matters because the salutation is not universal: KP-0489 writes
`Director Martin:` with no `Dear`, and the two opinions the Attorney General
issued on his own motion (KP-0505 'Diversity, Equity, and Inclusion',
KP-0516 'Social Security Numbers Required for Occupational Licenses') address
nobody at all and open on ordinary body prose straight after the `Re:` row.
A reader keyed on 'Dear' would have run those two into the body.

THE LETTERHEAD IS USUALLY A PICTURE. Only 14 of the 42 records set
`KEN PAXTON` / `ATTORNEY GENERAL OF TEXAS` in type; on the other 28 it is
raster only and the cover opens on the date. So the letterhead is read where
it is set in type and never required — a row above the date, centred on the
page axis, at a size that is not the body's.

THE SALUTATION IS THE LETTER'S FIRST WORD, and it stays in the letter. Core
places it, as the old engine did: on page one the reader claims down to the
last row of the `Re:` block and no further.

HOW THE LETTER CLOSES, and why half of it is claimed. Every one of the 42
records ends the same way, and the closing rail is as invariant as the
ledger indent — `Very truly yours,` sets at x0 = 288.0 on the last page of
all 42:

    ┌─────────────────────────────────────────────┐
    │                    Very truly yours,        │  the CLOSE and
    │                    (the signature, in ink)  │  the SIGNATURE:
    │                    KEN PAXTON               │  the letter's own
    │                    Attorney General of Texas│  last words, at
    │                                             │  the closing rail
    │  BRENT WEBSTER                              │
    │  First Assistant Attorney General           │  the OFFICE'S
    │  LESLEY FRENCH                              │  IMPRINT: the
    │  Chief of Staff                             │  officers who
    │  D. FORREST BRUMBAUGH                       │  reviewed the
    │  Deputy Attorney General for Legal Counsel  │  opinion, back at
    │  JOSHUA C. FIVESON                          │  the BODY rail
    │  Chair, Opinion Committee                   │
    └─────────────────────────────────────────────┘

The rail tells the two apart, and the distinction is real: what stands at
the closing rail the Attorney General wrote and signed, and it stays in his
letter. What returns to the body rail below his title is the OFFICE'S
imprint — the First Assistant, the Chief of Staff, the Opinion Committee —
and those officers did not write the letter. That block is handed over as
the document's signature band.

The ink of the handwritten signature leaves 32 stray glyph rows in the text
layer across nine records ('~ •. .', '.£ f', '(tf r'), set at 0.9-28.1pt and
at neither rail. They rendered as body paragraphs and, once, as a section
heading reading 't'. They are ink, not text, and they are recorded as
dropped.

WHO SIGNED IS REPORTED, NOT INFERRED. The pair at the closing rail is the
signer, and it goes into `criteria.judges` as printed. Core credits the
writing separately, and on KP-0505 it credits the wrong officer: its
`conformed_signature_author` reads the last FOURTEEN lines of the raw page
model, and this office's imprint is twelve to fourteen lines long, so on
that record — the longest, and the one carrying an extra Deputy First
Assistant pair — the window opens BELOW the Attorney General and the first
name/office pair it meets is 'BRENT WEBSTER, First Assistant Attorney
General'. Claiming the imprint cannot cure it: that reader walks
`model.pages`, which a claim does not touch. It is recorded here as a core
defect rather than worked around.

WHAT THIS FILE DOES NOT DO. The footnotes, the paragraphing, the bold
section headings this office writes, the `S U M M A R Y` it closes with and
the byline are all core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

register(CourtProfile(
    "texag", "Office of the Attorney General of Texas",
    # One officer answers one question. There is no bench here to concur in
    # or dissent from, so a record that came back with two writings would
    # have been split, not read.
    single_writing=True,
    rollout="migrated",
))

# THE LEDGER INDENT: how far the opinion's own identification is set in from
# the body rail. A declared fact of this office's stationery — 108.0 against
# a 72.0 rail on 41 of 42 records, never anything else.
_LEDGER_INDENT = 36.0
_INDENT_TOL = 6.0
# A row is centred on the page axis when its own midpoint is within this of
# the page's. The date sets 55-95pt wide on a 612pt page, so the tolerance is
# generous without reaching the rail.
_AXIS_TOL = 40.0
# A GAP THIS MANY LEADINGS BELOW THE ROW ABOVE OPENS A NEW ELEMENT. Measured
# on the corpus: within a block 13.8pt on a 14.0pt lead (1.0x), between
# blocks 22.8-41.7pt (1.63x-2.98x).
_BLOCK_GAP = 1.5

# 'Opinion No. KP-0480'. The number's letters are the Attorney General's
# initials, so the prefix is not a closed vocabulary — the shape is.
_OPINION_NO = re.compile(r"^Opinion\s+No\.\s*([A-Z]{2}-\d{3,4})\s*$", re.I)
# 'Re: …' — the question, opening the ledger's second element.
_RE_LINE = re.compile(r"^Re\s*:\s*(.*)$", re.I)
# '(RQ-0539-KP)' — the REQUEST this opinion answers, printed at the end of
# the question.
_REQUEST_NO = re.compile(r"\((RQ-\d{3,4}-[A-Z]{2})\)\s*$")
# THE CLOSING RAIL: where this office sets its complimentary close, its
# signature and its title. 288.0 exactly on the last page of all 42 records
# — a declared fact of the stationery, like the ledger indent.
_CLOSING_RAIL = 288.0
_RAIL_TOL = 1.5
# 'Very truly yours,' — the close, and the only landmark the band needs. The
# text layer splits its first word on three records ('V ery truly yours,').
_CLOSE = re.compile(r"^V\s?ery\s+truly\s+yours\s*,?$", re.I)

_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")
_DATE = re.compile(r"^(?:%s)\s+\d{1,2},\s+\d{4}$" % "|".join(_MONTHS))
# 'The Honorable', 'Mr.', 'Ms.', 'Colonel' — the requestor's line of address.
# A closed courtesy vocabulary, used only to say WHICH of the address rows
# is the person's name; the office, the street and the city are read by
# position, never by wording.
_COURTESY = re.compile(
    r"^(?:The\s+Honorable|Honorable|Mr\.|Mrs\.|Ms\.|Miss|Dr\.|Colonel|Col\.|"
    r"Chief|Judge|Justice|General|Major|Captain|Sheriff|Reverend)\s+\S",
    re.I)


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


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}
        # THE CLOSING BAND, for `Document.signature`. Held apart from
        # `items` because it is not headmatter: it closes the letter rather
        # than opening it, and it renders after the writing.
        self.signature: list = []

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

    def sign_row(self, group: list, centre: bool = False) -> None:
        """One printed row of the closing band, kept where the page set it.
        Not `emit`: that appends to the headmatter, and this row closes the
        letter rather than opening it."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.signature.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role="signature"))
        self.consumed.update(p.id for p in parts)

    def drop_row(self, group: list, kind: str) -> None:
        """A row consumed and RECORDED rather than placed."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(p.plain.strip() for p in parts)[:200],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "signature": self.signature,
                "anchor_ids": self.anchor, "doc_type_final": None}


@decider("headmatter.read", court="texag")
def read_headmatter_texag(model, geom, **_):
    """Read the Attorney General's letterhead cover and the office's closing
    imprint, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    lead = (geom.lead if geom and geom.lead else 14.0) or 14.0
    ledger = body_x0 + _LEDGER_INDENT
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    # THE LANDMARK. Without the opinion number set in the ledger there is no
    # cover of this shape, and core's shared walk is the better reading.
    # KP-0506 draws its whole first page as a raster and has no cover to
    # read at all; the letter it closes is still this office's.
    landmark = None
    for i, group in enumerate(rows):
        text = _norm(" ".join(l.plain for l in group))
        if _OPINION_NO.match(text) \
                and abs(group[0].x0 - ledger) <= _INDENT_TOL:
            landmark = i
            break

    ctx = _Ctx()
    if landmark is None:
        _read_signature(ctx, model, finder, body_x0, body_size)
        return ctx.result() if ctx.signature else NOTHING
    ctx.crit["headmatter_style"] = "ag-letterhead"
    ctx.crit["court"] = "Office of the Attorney General of Texas"

    # --- above the number: the letterhead, the date, the requestor --------
    date_at = None
    for i, group in enumerate(rows[:landmark]):
        text = _norm(" ".join(l.plain for l in group))
        if _DATE.match(text):
            date_at = i
            break
    address: list[str] = []
    for i, group in enumerate(rows[:landmark]):
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        x0 = group[0].x0
        x1 = max(l.x1 for l in group)
        centred = abs((x0 + x1) / 2 - page1.width / 2) <= _AXIS_TOL
        if i == date_at:
            ctx.crit["decision_date"] = text
            ctx.emit(group, "date", centre=True)
            continue
        if (date_at is None or i < date_at) and centred \
                and abs((group[0].size or 0.0) - body_size) > 1.0:
            # THE LETTERHEAD, where it is set in type: the office naming
            # itself, above the date, at a size that is not the body's.
            ctx.emit(group, "court", centre=True)
            continue
        if abs(x0 - body_x0) <= _INDENT_TOL and (
                date_at is not None and i > date_at):
            # THE REQUESTOR'S ADDRESS, flush at the rail under the date.
            address.append(text)
            ctx.emit(group, "caption")
            continue
        # A row at no position this stationery uses is left to core rather
        # than tinted with a role that would be a guess.
    if address:
        ctx.crit["caption"] = list(address)
        # WHO ASKED: the first row of the address, which a courtesy title
        # marks as a person. Their office, their street and their city stay
        # in `caption` — this is a letter, and there is no court below to
        # file them under.
        who = address[0]
        if _COURTESY.match(who) or len(address) > 1:
            ctx.crit["parties"] = [who]

    # --- the ledger: the opinion number, then the question ----------------
    group = rows[landmark]
    number = _OPINION_NO.match(_norm(" ".join(l.plain for l in group)))
    ctx.crit["docket_number"] = number.group(1).upper()
    ctx.crit["title"] = _norm(" ".join(l.plain for l in group))
    ctx.emit(group, "docket")
    # The number is also the only row an unsigned letter could open on, so
    # it is offered back if the claim would leave no writing.
    ctx.anchor.extend(l.id for l in group)

    question: list[str] = []
    prev_top = max(l.top for l in group)
    for group in rows[landmark + 1:]:
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        top = min(l.top for l in group)
        gap = top - prev_top
        in_ledger = abs(group[0].x0 - ledger) <= _INDENT_TOL
        if not question:
            # The question opens on 'Re:' and on nothing else.
            if not (in_ledger and _RE_LINE.match(text)):
                break
        elif not in_ledger or gap > lead * _BLOCK_GAP:
            break                 # the block closed; the letter begins
        question.append(text)
        ctx.emit(group, "summary")
        prev_top = max(l.top for l in group)

    if question:
        subject = _norm(" ".join(question))
        subject = _RE_LINE.match(subject).group(1).strip()
        request = _REQUEST_NO.search(subject)
        if request:
            ctx.crit["other_dockets"] = [request.group(1)]
            subject = _REQUEST_NO.sub("", subject).strip()
        ctx.crit["case_name"] = subject[:300]

    _read_signature(ctx, model, finder, body_x0, body_size)
    return ctx.result()


def _read_signature(ctx, model, finder, body_x0: float, body_size: float
                    ) -> None:
    """The letter's closing band: the complimentary close, the Attorney
    General's signature, and the office's imprint under it.

    Opens at the close on the last page. Below it the CLOSING RAIL carries
    what the Attorney General signed and the BODY RAIL the officers who
    reviewed the opinion; a row at neither rail — or at a size this office
    sets no text in — is the ink of the handwritten signature, consumed and
    recorded rather than placed."""
    page = model.pages[-1]
    rows = _rows(page, finder)
    close = next((i for i, g in enumerate(rows)
                  if _CLOSE.match(_norm(" ".join(l.plain for l in g)))
                  and abs(g[0].x0 - _CLOSING_RAIL) <= _RAIL_TOL), None)
    if close is None:
        return
    ctx.sign_row(rows[close], centre=True)
    signer: list[str] = []
    for group in rows[close + 1:]:
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        x0 = group[0].x0
        typed = abs((group[0].size or 0.0) - body_size) <= 1.0
        if typed and abs(x0 - _CLOSING_RAIL) <= _RAIL_TOL:
            ctx.sign_row(group, centre=True)
            signer.append(text)
            continue
        if typed and abs(x0 - body_x0) <= _RAIL_TOL:
            ctx.sign_row(group)
            continue
        ctx.drop_row(group, "signature-ink")
    # WHO SIGNED: the name and the office it names, both at the closing rail.
    if len(signer) >= 2:
        ctx.crit["judges"] = f"{signer[0]}, {signer[1]}"
