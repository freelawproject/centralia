"""Supreme Court of Georgia ('ga').

Everything unique to ga lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACTS. Georgia prints THREE papers and each one names itself by
HOW IT SETS ITS OWN NAME. Nothing is decided by what a case is called:

    'engraved cover' (48 of 50) — the slip opinion and the disciplinary
    opinion share one cover. The court engraves its name in TWO rows on
    the page axis, a 14pt 'In the' over an 18pt 'Supreme Court of
    Georgia', both above the 12pt body; under it the zones are told
    apart by TYPE SIZE, not by order — the docket and the caption at
    body size (12pt), the provenance at 10pt:

        NOTICE: This opinion is subject to modification …   the 8pt
                                          advisory, claimed and dropped
        In the                                    the masthead, 14pt
        Supreme Court of Georgia                  …and its 18pt row
        No. S26A0240                              the docket, 12pt
        Hailu Abebe                               the caption: a party…
        v.                                        …the pivot…
        The State                                 …and the other side
        On Appeal from the Superior Court of Henry County   10pt origin…
        No. 2020-SU-CR-0838-DR                    …and its number
        Decided: May 19, 2026                     the release, 10pt
        BETHEL, Justice.                          …and the writing starts

    THE 10pt BAND IS THE PROVENANCE ZONE and it always closes the block.
    A disciplinary cover prints no origin at all (six records: docket,
    one 'In the Matter of …' row, the date), and a consolidation repeats
    the docket-and-caption pair around a bare centred 'and' (bennett).
    Both fall out of the size walk; neither needs its own rule.

    'typed cover' (1 of 50) — the same court, set on the DOUBLE-SPACED
    disciplinary template. There is no engraving: the court names itself
    in ONE row at the body rail, at body size, and the docket is printed
    as a LEADER on the caption row rather than above it:

        In the Supreme Court of Georgia           15pt, AT THE RAIL
        Decided: April 21, 2026                   centred under it
        S26Y0093. IN THE MATTER OF DARRYL J. FERGUSON.   docket + caption
        PER CURIAM.                               …and the writing starts

    'order list' (1 of 50) — the clerk's certiorari order. The court's
    name is set in CAPS at a stationery indent with the case number
    stacked directly under it at the SAME indent, and the release date
    stands alone FLUSH RIGHT beside them:

        SUPREME COURT OF GEORGIA                  15pt caps, x0=153
        Case No. S25C1294                         …the docket, x0=153
                                     May 5, 2026  …the date, flush right
        The Honorable Supreme Court met pursuant to adjournment.
        The following order was passed:           the convening recital
        AMY WADE JOHNSON v. CITY OF VIDALIA.      the caption
        The Supreme Court today denied the petition …   THE ORDER, which
        All the Justices concur.                  belongs to the writings

    THE ORDER IS NOT HEADMATTER. The reader stops at the caption row, so
    the disposition and its concurrence line assemble as the court's own
    per curiam order. Read the other way — which is what both engines did
    — the whole order rendered as headmatter and the document carried a
    lone separate concurrence with nothing to concur in.

THE DISPATCH is one question about page 1: WHERE the court sets its own
name, and at what size.  Two axis-centred rows above body size opens the
engraved cover; one row at the body rail at body size opens the typed
cover; a caps row over a 'Case No.' row at a shared indent opens the
order list. Over 50 records the three tests are exclusive and total.

THE FURNITURE THE CLAIM INHERITS. The reporter's advisory ('NOTICE: This
opinion is subject to modification …') is printed ABOVE the masthead in
five 8pt rows on 48 of 50 records and nowhere else; two records print
nothing there and nothing else ever does. The reader claims it and
records it as a notice, because core's notice peel runs only on rows a
reader left behind AND runs after assembly: left behind, the advisory
became the first blockquote of the majority on all 48 covers, and the
invariant that never bisects a writing then pulled the entire headmatter
into it. The order list's convening recital is dropped the same way core
drops ca2's ('At a stated term of the United States Court of Appeals…').

ga prints NO appearance of counsel anywhere in the corpus — no roster, no
'Attorneys for', on any page of any record — so a missing counsel section
here is the paper, not a defect.

KNOWN CORE DEFECT, NOT REPAIRED HERE. Three covers print the argued and
decided dates either side of an EM DASH set from a SymbolMT subset with
no ToUnicode ('Argued: December 9, 2025 (cid:127) Decided: May 19,
2026'), and abebe sets two thin spaces from a Times subset the same way
('Criminal Cases(cid:3031)§(cid:3031)1.32.15'). Both are recoverable
from the embedded outline and the repair belongs in pdfio, not here; the
DATES are read correctly regardless, because the separator is taken as
'whatever stands between the two labels'.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# ga's profile is registered in the shared table; this file owns its
# headmatter contract. (When the registration is lifted out of
# courts/__init__.py it belongs here, beside the reader — as ala's does.)
GA: CourtProfile = PROFILES["ga"]

STYLE_ENGRAVED = "engraved cover"
STYLE_TYPED = "typed cover"
STYLE_ORDER = "order list"

# ---- ga's declared facts (measured over all 50 records) ------------------
# THE ENGRAVED MASTHEAD: 14pt over 18pt on a 12pt body — the only rows on
# any cover above body size, and invariant to the tenth of a point across
# 48 records.
_MASTHEAD_MIN = 16.0
# THE PROVENANCE BAND is set two points UNDER the body (10pt against 12pt).
# The band, not the row order, is what separates the origin and the release
# date from the caption above them.
_SMALL_MAX = 11.0
# EVERY ROW OF THE ENGRAVED COVER IS CENTRED ON THE PAGE AXIS — measured
# over the 48 covers, the worst row's midpoint sits 1.3pt off 306.0. A row
# that leaves the axis is not part of this cover, and the walk declines
# rather than reading it as a caption.
_AXIS_TOL = 6.0
# HOW FAR THE BLOCK MAY RUN. All three papers close on page 1 and all three
# walks are bounded there — bennett consolidates two appeals under two
# dockets and still signs on page 1. A record whose block ran past it would
# have no byline inside the bound, and a walk that does not reach a byline
# declines rather than guessing where the block ended.
_MAX_PAGES = 1
# A row is AT THE RAIL when it starts on the body's left edge (the typed
# cover sets its masthead there; the engraved cover never does).
_RAIL_TOL = 2.0
# HOW FAR DOWN THE MASTHEAD MAY STAND. The reporter's advisory is five rows
# and the court names itself directly under it; nothing else intervenes.
_HEAD_WINDOW = 8

# THIS COURT'S OWN DOCKET: 'S26A0240' (appeal), 'S26Y0954' (discipline),
# 'S25G0922' (certiorari granted), 'S25C1294' (certiorari petition) — the
# term year, the docket letter, the sequence. Never a number from below.
_DOCKET_ROW = re.compile(r"^(?:Case\s+)?Nos?\.\s*(S\d{2}[A-Z]\d{4})\.?$")
# The docket printed as a LEADER on the typed cover's caption row.
_DOCKET_LEAD = re.compile(r"^(S\d{2}[A-Z]\d{4})\.\s+(.+)$")
# A NUMBER FROM BELOW, as the provenance band labels it ('No. 21CR1610',
# 'No. A24A1853'). Read only inside that band, under an origin row.
_LOWER_DOCKET = re.compile(r"^Nos?\.\s*(.+?)\.?$")
# THE ORIGIN LEADERS: the closed set of ways this court states where the
# case came from. Never a court NAME.
_ORIGIN_LEADERS = ("on appeal from", "on writ of certiorari from",
                   "on certification from", "on certified question from",
                   "on application for", "on remand from")
# THE DATE LABELS the provenance band prints, and the separator between
# them when both appear on one row. The separator is an em dash that three
# records set from a subset font pdfio cannot decode, so it is taken as
# 'whatever is not a label and not a date' rather than matched.
_DATE_ROW = re.compile(
    r"(Argued|Decided|Submitted|Reargued|Resubmitted)\s*:\s*"
    r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})")
# THE ORDER LIST prints its release date UNLABELLED and flush right.
_MONTH_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},\s+\d{4}\.?$")
# The consolidation joint: a bare 'and' between two docket-and-caption
# pairs. A closed structural word, not a party name.
_JOINT = re.compile(r"^and$", re.I)
# ga signs prose ('BETHEL, Justice.' / 'PETERSON, Chief Justice.') and per
# curiam. Both end the reader.
_BYLINE = BylineGrammar(style="prose",
                        titles=("Justice", "Chief Justice",
                                "Presiding Justice"))

# The order list's masthead, and the recital under it. The masthead is
# found by its SHAPE — a caps row with the case number stacked at the same
# indent — and only then confirmed to be this court naming itself.
_COURT_NAME = "supreme court of georgia"
_RECITAL = ("the honorable supreme court met",
            "the following order was passed")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _caps_caption(text: str) -> bool:
    """A caption set on ONE row: the parties in caps either side of a pivot
    the court sets in lower case."""
    parts = re.split(r"(?<=\s)vs?\.\s", _norm(text))
    if len(parts) != 2:
        return False
    return all(p.strip() and p == p.upper() for p in parts)


def _dates(text: str) -> list[tuple[str, str]]:
    """[('Argued', 'December 9, 2025'), ('Decided', 'May 19, 2026')]."""
    return [(mm.group(1), _norm(mm.group(2)).rstrip(","))
            for mm in _DATE_ROW.finditer(_norm(text))]


def _opens_origin(text: str) -> bool:
    low = _norm(text).lower()
    return any(low.startswith(lead) for lead in _ORIGIN_LEADERS)


# --------------------------------------------------------------------------
# the rows
# --------------------------------------------------------------------------

class _Ctx:
    """What the three walks share: the page models and the emit buffer."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, align: str | None = None) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        pm = self.pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        if align is None:
            align = line_alignment(first, pm.width, self.geom,
                                   banner_center_min_size=self.body_size + 1.0)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts),
            italic=all(bool(getattr(p, "all_italic", False)) for p in parts),
            role=role))
        self.consumed.update(p.id for p in parts)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _rows(model, finder, max_pages: int) -> list[list]:
    """Content rows in page order, same-row pieces rejoined, furniture out.

    A justified row split at a wide gap is one row of the page: read
    piecewise, the right-hand piece leaves the axis and reads as a new
    element."""
    out: list[list] = []
    for pm in model.pages[:max_pages]:
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        out.extend(groups[k] for k in order)
    return out


def _centred(group: list, width: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


def _claim_advisory(ctx: _Ctx, rows: list, start: int) -> bool:
    """Claim the reporter's advisory printed ABOVE the masthead, and record
    it as the notice it is.

    A READER THAT CLAIMS A REGION INHERITS ITS FURNITURE. Core's notice peel
    runs only on rows a reader left behind, and it runs AFTER assembly —
    left behind alone, the five advisory rows became the first blockquote of
    the majority on all 48 covers, and the invariant that never bisects a
    writing then pulled the whole headmatter into it (0 headmatter rows,
    'invariant.reunited' nine times).

    Measured over the corpus: 48 covers print exactly these five rows above
    the masthead and two print nothing; no record prints anything else
    there. The band is set UNDER body size (8pt against 12pt or 15pt), and a
    band that is not is not this advisory — the claim is declined rather
    than guessed at.
    """
    band = [g for g in rows[:start] if g[0].page == 1]
    if not band:
        return True
    if any(max((l.size or 0.0) for l in g) >= ctx.body_size for g in band):
        return False
    text = " ".join(_norm(" ".join(l.plain for l in g)) for g in band)
    ids = tuple(l.id for g in band for l in g)
    ctx.dropped.append(m.Dropped(text=text[:1200],
                                 prov=m.Prov(band[0][0].page, ids),
                                 kind="notice"))
    ctx.consumed.update(ids)
    return True


# --------------------------------------------------------------------------
# the dispatch
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ga")
def read_headmatter_ga(model, geom, **_):
    """Read one of Georgia's three papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 126.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(model, finder, _MAX_PAGES)
    if len(rows) < 4:
        return NOTHING
    pages = {pm.number: pm for pm in model.pages}
    ctx = _Ctx(model, geom, pages, body_size)

    p1 = [g for g in rows if g[0].page == 1]
    # THE ENGRAVED MASTHEAD: two consecutive axis-centred rows above body
    # size, the second of them naming the court.
    big = [i for i, g in enumerate(p1)
           if max((l.size or 0.0) for l in g) >= _MASTHEAD_MIN]
    if big:
        i = big[0]
        if (i > 0 and len(big) == 1
                and _norm(" ".join(l.plain for l in p1[i])).lower()
                == _COURT_NAME
                and _centred(p1[i], page1.width)
                and _centred(p1[i - 1], page1.width)):
            return _read_engraved(ctx, rows, i - 1)
        return NOTHING
    # NO ROW ABOVE BODY SIZE. The typed cover names the court in one row at
    # the rail; the order list sets a caps row over its 'Case No.' row at a
    # shared stationery indent. Both sit UNDER the reporter's advisory, so
    # the window has to clear it — the advisory is five rows.
    for i, g in enumerate(p1[:_HEAD_WINDOW]):
        text = _norm(" ".join(l.plain for l in g))
        if text.lower() != f"in the {_COURT_NAME}":
            continue
        if abs(min(l.x0 for l in g) - body_x0) <= _RAIL_TOL:
            return _read_typed(ctx, rows, i)
        return NOTHING
    for i, g in enumerate(p1[:_HEAD_WINDOW]):
        text = _norm(" ".join(l.plain for l in g))
        if text.lower().rstrip(".") != _COURT_NAME or text != text.upper():
            continue
        if i + 1 >= len(p1):
            return NOTHING
        nxt = p1[i + 1]
        if (_DOCKET_ROW.match(_norm(" ".join(l.plain for l in nxt)))
                and abs(min(l.x0 for l in nxt) - min(l.x0 for l in g))
                <= _RAIL_TOL):
            return _read_order(ctx, rows, i)
        return NOTHING
    return NOTHING


# --------------------------------------------------------------------------
# the engraved cover
# --------------------------------------------------------------------------

def _read_engraved(ctx: _Ctx, rows: list, start: int):
    """The slip and disciplinary cover: masthead, then the size walk."""
    if not _claim_advisory(ctx, rows, start):
        return NOTHING
    parser = BylineParser(_BYLINE)
    page1 = ctx.pages[1]
    dockets: list[str] = []
    groups: list[list[str]] = []        # caption rows, one list per case
    origin: list[str] = []
    lower: list[str] = []
    signed = False
    state = "court"
    for group in rows[start:]:
        if group[0].page != 1:
            break
        text = _norm(" ".join(l.plain for l in group))
        size = max((l.size or 0.0) for l in group)
        if parser.parse(text) is not None:
            signed = True
            break
        if state == "court":
            if size >= _MASTHEAD_MIN or text.lower() == "in the":
                if size >= _MASTHEAD_MIN:
                    ctx.crit["court"] = text
                ctx.emit(group, "court", "C")
                continue
            state = "case"
        # THE PROVENANCE BAND closes the block: once the type drops under
        # the body, no caption row follows it on any of the 48 covers.
        if size <= _SMALL_MAX:
            state = "provenance"
        if state == "case":
            if not _centred(group, page1.width):
                return NOTHING
            mm = _DOCKET_ROW.match(text)
            if mm is not None:
                dockets.append(mm.group(1))
                groups.append([])
                ctx.emit(group, "docket", "C")
                continue
            if not groups:
                return NOTHING          # the docket always opens a case
            if _JOINT.match(text):
                ctx.emit(group, "caption", "C")
                continue
            groups[-1].append(text)
            ctx.emit(group, "caption", "C")
            continue
        if state == "provenance":
            if _opens_origin(text):
                origin.append(text)
                ctx.emit(group, "lower-court", "C")
                continue
            found = _dates(text)
            if found:
                for label, value in found:
                    if label.lower() == "decided":
                        ctx.crit.setdefault("decision_date", value)
                    else:
                        ctx.crit.setdefault("submitted", value)
                ctx.emit(group, "date", "C")
                continue
            mm = _LOWER_DOCKET.match(text)
            if mm is not None and origin:
                lower.append(_norm(mm.group(1)))
                ctx.emit(group, "lower-court", "C")
                continue
            return NOTHING              # an unread row inside the block
    if not (signed and dockets and any(groups)):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_ENGRAVED
    _record(ctx, dockets, groups, origin, lower)
    return ctx.result()


def _record(ctx: _Ctx, dockets: list, groups: list, origin: list,
            lower: list) -> None:
    """What the cover said, in the criteria."""
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    caption = [t for g in groups for t in g]
    if caption:
        ctx.crit["caption"] = caption
    lead = next((g for g in groups if g), [])
    _name(ctx, lead)
    if origin:
        ctx.crit["lower_court"] = _norm(" ".join(origin))
    if lower:
        ctx.crit["lower_court_docket"] = lower


def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, from the party names either side of the pivot —
    never by joining the caption wholesale."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen = False
    for row in rows:
        if _is_pivot(row):
            side = right
            seen = True
            continue
        side.append(row)
    if not seen and len(rows) == 1:
        # A caption set on ONE row carries its pivot inside it.
        parts = re.split(r"(?<=\s)vs?\.\s", _norm(rows[0]))
        if len(parts) == 2:
            left, right, seen = [parts[0]], [parts[1]], True
    if seen and left and right:
        one, two = (_norm(" ".join(left)).rstrip(", "),
                    _norm(" ".join(right)).rstrip(", "))
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _norm(" ".join(left + right)).rstrip(", ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


# --------------------------------------------------------------------------
# the typed cover
# --------------------------------------------------------------------------

def _read_typed(ctx: _Ctx, rows: list, start: int):
    """The double-spaced disciplinary cover: the court's name at the rail,
    the release date under it, and the docket printed as the caption's
    leader."""
    if not _claim_advisory(ctx, rows, start):
        return NOTHING
    parser = BylineParser(_BYLINE)
    docket = None
    caption: list[str] = []
    signed = False
    for group in rows[start:]:
        if group[0].page != 1:
            break
        text = _norm(" ".join(l.plain for l in group))
        if parser.parse(text) is not None:
            signed = True
            break
        if group is rows[start]:
            ctx.crit["court"] = text.removeprefix("In the ")
            ctx.emit(group, "court")
            continue
        found = _dates(text)
        if found and docket is None:
            for label, value in found:
                if label.lower() == "decided":
                    ctx.crit.setdefault("decision_date", value)
                else:
                    ctx.crit.setdefault("submitted", value)
            ctx.emit(group, "date")
            continue
        mm = _DOCKET_LEAD.match(text)
        if mm is not None and docket is None:
            docket = mm.group(1)
            caption.append(_norm(mm.group(2)).rstrip("."))
            ctx.emit(group, "caption")
            continue
        return NOTHING                  # an unread row inside the block
    if not (signed and docket and caption):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_TYPED
    _record(ctx, [docket], [caption], [], [])
    return ctx.result()


# --------------------------------------------------------------------------
# the order list
# --------------------------------------------------------------------------

def _read_order(ctx: _Ctx, rows: list, start: int):
    """The clerk's certiorari order: masthead, docket, date, the convening
    recital, and the caption. THE ORDER ITSELF IS THE WRITING and the
    reader stops above it."""
    if not _claim_advisory(ctx, rows, start):
        return NOTHING
    docket = None
    caption: list[str] = []
    date = None
    recital: list[list] = []
    for group in rows[start:]:
        if group[0].page != 1:
            break
        text = _norm(" ".join(l.plain for l in group))
        if group is rows[start]:
            ctx.crit["court"] = text
            ctx.emit(group, "court")
            continue
        mm = _DOCKET_ROW.match(text)
        if mm is not None and docket is None:
            docket = mm.group(1)
            ctx.emit(group, "docket")
            continue
        if date is None and _MONTH_DATE.match(text):
            date = text.rstrip(".")
            ctx.crit["decision_date"] = date
            ctx.emit(group, "date")
            continue
        low = text.lower()
        if any(low.startswith(cue) for cue in _RECITAL):
            # THE CONVENING RECITAL IS APPARATUS, not a row of the
            # headmatter — core drops ca2's ('At a stated term of the United
            # States Court of Appeals…') and this is the same furniture in
            # Georgia's words. Recorded, never silently cut.
            recital.append(group)
            continue
        # THE CAPTION is the caps row under the recital, and it closes the
        # block: what follows is the order the court passed. The court sets
        # its PIVOT in lower case inside that row ('AMY WADE JOHNSON v. CITY
        # OF VIDALIA.'), so the caps test is made on the row WITHOUT the
        # pivot — read whole, the row is not upper case and the caption was
        # missed, the walk broke on it, and the claim was declined.
        if not caption and _caps_caption(text):
            caption.append(text.rstrip("."))
            ctx.emit(group, "caption")
            continue
        break
    if not (docket and caption):
        return NOTHING
    if recital:
        ids = tuple(l.id for g in recital for l in g)
        ctx.dropped.append(m.Dropped(
            text=" ".join(_norm(" ".join(l.plain for l in g))
                          for g in recital)[:400],
            prov=m.Prov(recital[0][0].page, ids), kind="recital"))
        ctx.consumed.update(ids)
    ctx.crit["headmatter_style"] = STYLE_ORDER
    _record(ctx, [docket], [caption], [], [])
    return ctx.result()


# --------------------------------------------------------------------------
# the clerk's office: what ga prints as a PICTURE
# --------------------------------------------------------------------------
# Measured over all 50 records, exactly ONE carries a graphic at all, and it
# is an order list — the paper that is an extract from the court's minutes.
# That paper prints two, and both are the clerk's:
#
#     72x72pt   at the left margin, over the masthead      the court's seal
#     335x149pt below the last row of the order            the certificate
#                                                          (seal, attestation
#                                                           and signature)
#
# Core reads a graphic's role off its geometry, and both of these fail the
# tests that would place them. The seal stands UNDER the reporter's advisory
# instead of above all the type, so it is not a masthead; the certificate is
# not on the document's LAST page — a justice's concurrence follows on pages
# 2-6 — so it is not a signing stamp. Both fell through to the figure test,
# were cropped, and were planted inside the order as though the court had
# printed an exhibit. The user, 2026-08-20: "needs to drop the stamp the
# court seal and the clerk signature in the order."
#
# Bounded so that a real exhibit would still be one: only a graphic in the
# MASTHEAD BAND (at or above the first row set at the measure — the advisory
# above it is set 4pt under the body) or BELOW THE LAST ROW OF TYPE on its
# page is claimed. A graphic between them is not the clerk's, and the answer
# is NOTHING — core decides.
_SEAL_MAX = 120.0            # pt a side; the seal measures 72x72


@decider("image.role", court="ga")
def image_role_ga(page=None, image=None, geom=None, **_):
    """ga prints no figures. Every graphic on its pages is the clerk's."""
    if page is None or image is None:
        return NOTHING
    rows = [l for l in page.lines if l.plain.strip()]
    if not rows:
        return NOTHING
    body_size = geom.body_size if geom else 12.0
    head = min((l.top for l in rows if (l.size or 0.0) >= body_size - 0.5),
               default=None)
    if (head is not None and image.top <= head
            and max(image.x1 - image.x0, image.bottom - image.top)
            <= _SEAL_MAX):
        return "the court's seal"
    if image.top > max(l.top for l in rows):
        return "the clerk's certificate"
    return NOTHING
