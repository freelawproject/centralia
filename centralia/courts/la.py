"""Supreme Court of Louisiana ('la').

Everything unique to la lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — a la record is TWO DOCUMENTS bound together. Page 1 is the
Clerk's NEWS RELEASE sheet, set flush at the sheet's own 36pt margin with a
two-column entry beneath it. The opinion's own headmatter does not begin
until page 2, where the court names itself and sets everything CENTRED on
the page axis down to the byline.

    ┌─ page 1 ── the CLERK's sheet ──────────────────────────────┐
    │ FOR IMMEDIATE NEWS RELEASE          NEWS RELEASE #031      │ 36.0
    │ FROM: CLERK OF SUPREME COURT OF LOUISIANA                  │ 36.0
    │ The Opinions handed down on the 27th day of June, 2025 …    │ 36.0
    │ BY McCallum, J.:                                           │ 36.0
    │ 2024-C-00808  23RD PSALM TRUCKING, L.L.C. VS. MADISON …    │ 41.8
    │               JURY (Parish of Madison)      the index      │ 172.2
    │                                                            │
    │               AFFIRMED. SEE OPINION.        disposition    │
    │                                                            │
    │               Weimer, C.J., dissents and …  the bench      │
    │               Crain, J., concurs.                          │
    ├─ page 2 ── the COURT's paper ──────────────────────────────┤
    │             SUPREME COURT OF LOUISIANA      the masthead   │
    │                No. 2024-C-00808             the docket     │
    │            23RD PSALM TRUCKING, L.L.C.                     │
    │                       VS.                   the caption    │
    │            MADISON PARISH POLICE JURY                      │
    │   On Writ of Certiorari to the Court of …   the origin     │
    │ McCALLUM, J.                                the writing    │
    └────────────────────────────────────────────────────────────┘

WHAT THE NEWS-RELEASE SHEET IS, AND WHAT IS DONE WITH IT. It is not the
court's paper and it is not about this case alone: it names its author
('FROM: CLERK OF SUPREME COURT OF LOUISIANA'), it is numbered in its own
series ('NEWS RELEASE #031'), and its sentence is a PLURAL pointing at a
list — 'The Opinions handed down on the 27th day of June, 2025 are as
follows:' — even where the record that was cut out of it holds one case.
Its own instruction to its reader is to go and read the paper ('SEE
OPINION.'). So the sheet is DROPPED BY DEFAULT, and only the parts of it
that state something the court's own paper does not are read:

  * the release header, the 'BY <justice>, J.:' index heading and the
    two-column index entry (docket, case name, parish) are DROPPED as
    'news-release'. Every identifier in them is printed again on page 2 in
    the court's own setting, and there BETTER: on a consolidated record the
    sheet's index carries one number where the paper carries both (belaire —
    sheet '2025-C-00156', paper 'No. 2025-C-00151 c/w No. 2025-C-00156'), so
    the criteria are taken from page 2 and never from the sheet.
  * the DISPOSITION part is read (`disposition`). What the court did is
    stated nowhere else in the front matter.
  * the BENCH part is read (`panel`) — both the ad hoc / pro tempore sitting
    notes ('Retired Judge John Conery, appointed Justice ad hoc, sitting for
    Chief Justice Weimer, recused.') and the vote lines ('Crain, J.,
    concurs.'). A justice who concurred or dissented WITHOUT writing
    separately is named nowhere else in the record; dropping these rows
    would destroy the only statement of the vote.
  * the handing-down DATE is harvested out of the dropped sentence into
    `decision_date` — the date is a fact, the sentence around it is the
    Clerk's ('… are as follows:' refers to the list, not to this document).

CLAIMING PAGE 1 IS ALSO WHAT KEEPS THE WRITINGS HONEST. Unclaimed, the
sheet's 'PER CURIAM:' index heading opens a writing, and six records came
back reporting a PHANTOM per-curiam opinion whose body was the index entry
(justin_irwin, gary_crockett, state_ex_rel._darrell_j._robinson,
state_of_louisiana_v._brhian_thomas, …_dionte_bracken, …_leonidas_lowry);
on two more the whole document became one `order` beginning 'FOR IMMEDIATE
NEWS RELEASE' (in_re_judge_donald_chick_foret, …_donald_briggs_iii).

THE SHEET'S GEOMETRY, MEASURED on all 50 records. The header stands at the
sheet's rail, x0 = 36.0 exactly. The entry opens on the row that carries a
docket-shaped token in a left index column (x0 41.8, 42.1 or 47.5 — set by
the widest docket of the release day) beside the matter column (x0 172.2 →
185.6, likewise per-record, so it is read off the row and never fixed). The
leading inside a part of the entry is 13.8pt and BETWEEN parts 27.2-29.0pt
(2x), which is what separates the index from the disposition from the
bench — never an ordinal, because the sitting notes fall before the
disposition on some records (evangelia_bilalis, ike_spears) and after it on
others (kelly_o._orgeron, state_of_louisiana_v._maya_jones).

THE ONE PART THAT RUNS ON. vinton_harbor sets its disposition at 13.8 from
the case name, inside the first part. So in the FIRST part the index run
closes on the parish parenthesis — the entry's name always ends either at
'(Parish of …)' or at the part's end — and anything after it is the
disposition run, which must close on the sheet's own 'SEE OPINION.' /
'SEE PER CURIAM.' sentence. Where neither landmark is present the part is
dropped whole rather than split on a guess.

PAGE 2 IS READ BY THE AXIS AND THE RAIL. Every row of the court's own block
is centred on the page axis (measured: mid-point 304.1-306.4 against a
306.0 axis on all 50 records) and the byline stands at the body rail
(x0 = 71.8-72.2). The rhythm is 16.1pt inside an element and 32.2pt between
elements, which is how the origin's wrap ('Parish of Orleans Civil',
'Civil') is told from a new element. The masthead is the DISPATCH landmark
and it is found by search, never by page number.

THE BYLINE ENDS THE READER: 'McCALLUM, J.', 'WEIMER, C.J.', 'Guidry, J.',
'PER CURIAM', 'PENZATO, Justice Pro Tempore*', 'WEIMER, Chief Justice.1'.
The trailing asterisk is often a symbol-font glyph (U+F02A), so the mark is
stripped before the row is tested.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

STYLE = "clerk's-release + centred cover"

# ---------------------------------------------------------------- page 1 ---
# The Clerk's sheet names itself in its first two rows and its author in the
# third; measured identically on all 50 records.
_RELEASE = re.compile(r"^FOR IMMEDIATE NEWS RELEASE\b", re.I)
_CLERK = re.compile(r"^FROM:\s*CLERK OF SUPREME COURT OF LOUISIANA", re.I)
# 'The Opinions handed down on the 27th day of June, 2025 are as follows:'
# ('The Opinion … is as follows:' where the day released one case.)
_HANDED = re.compile(
    r"^The Opinions?\s+handed down on\s+(?:the\s+)?(.+?)\s+(?:is|are)\s+as\s+"
    r"follows", re.I)
_DAY_OF = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)\s+day of\s+([A-Za-z]+),?\s+(\d{4})$")
# '2024-C-00808' / '2025-KK-00471' / '2025-B-00537' — the index column's
# token, which is what OPENS the entry.
_INDEX_DOCKET = re.compile(r"^\d{4}-[A-Z]{1,3}-\d{3,6}$")
_INDEX_COL_MAX = 130.0          # the index column: x0 41.8-47.5, measured
# The sheet's parts are separated by DOUBLE leading: 13.8pt inside a part,
# 27.2-29.0pt between parts.
_PART_GAP = 20.0
# The sheet closes each disposition by sending its reader to the paper.
_SEE = re.compile(r"\bSEE\s+(?:OPINION|PER CURIAM|ORDER)\s*\.?$", re.I)
# THE BENCH, in the sheet's two forms. A vote line names a justice and a
# bench title before the verb ('Weimer, C.J., dissents …', 'Crain, J.,
# concurs.', 'Dupont, A.H.J., additionally concurs …'); an assignment note
# opens on a bench word and carries an assignment word.
_VOTE = re.compile(
    r"^[A-Z][A-Za-z'’\-]+,\s*(?:C\.J\.|JJ?\.|A\.H\.J\.)\s*,", re.I)
_SITTING = re.compile(
    r"^(?:Retired\s+Judge|Chief\s+Justice|Justice|Judge)\b.*"
    r"\b(?:ad\s+hoc|[Pp]ro\s+[Tt]empore|recused|sitting|heard this case)\b")

# ---------------------------------------------------------------- page 2 ---
_MASTHEAD = re.compile(r"^SUPREME COURT OF LOUISIANA$")
_MASTHEAD_SIZE_MIN = 13.0       # 14-16pt on the paper; 12pt on the sheet
_AXIS_TOL = 12.0                # measured spread 304.1-306.4 on a 306 axis
_ELEMENT_GAP = 20.0             # 16.1pt inside an element, 32.2pt between
_MAX_PAGES = 4                  # the masthead is on page 2 of all 50
# 'No. 2024-C-00808' / 'NO. 2025-B-0537' / 'NUMBER 2024-C-00676'
_DOCKET = re.compile(r"^(?:Nos?\.|NUMBER)\s*(.+)$", re.I)
# The consolidation glue, printed between two docket rows and again between
# two halves of a caption; the BAND decides which it is.
_CW = re.compile(r"^(?:c/w|C/W|CONSOLIDATED WITH)$", re.I)
_PIVOT = re.compile(r"^(?:VS\.?|VERSUS|V\.)$", re.I)
# Where the case came from. Louisiana prints one of these, or names the
# tribunal below outright, or (in a bar matter) the kind of proceeding.
_ORIGIN = re.compile(
    r"^(?:ON\s+(?:WRIT|APPEAL|SUPERVISORY|CERTIFIED|DIRECT|REMAND)"
    r"|On\s+(?:Writ|Appeal|Supervisory\s+Writ|Certified|Direct|Remand|"
    r"Application|Reconsideration))\b", re.I)
_TRIBUNAL = re.compile(
    r"^(?:Judiciary Commission of Louisiana|Louisiana Attorney Disciplinary"
    r" Board|Office of Disciplinary Counsel)$", re.I)
# What KIND of matter this is, and on what posture it comes — apparatus the
# caption carries that is neither the court below nor the parties.
_PROCEEDING = re.compile(
    r"^(?:ATTORNEY|JUDICIAL)\s+DISCIPLINARY\s+PROCEEDINGS?$", re.I)
_POSTURE = re.compile(
    r"^ON\s+(?:FIRST\s+|SECOND\s+|THIRD\s+)?REHEARING(?:\s+GRANTED)?$", re.I)
# 'McCALLUM, J.' / 'WEIMER, C.J.' / 'Guidry, J.' / 'PER CURIAM' /
# 'PENZATO, Justice Pro Tempore*' / 'WEIMER, Chief Justice.1'
_BYLINE = re.compile(
    r"^(?:PER CURIAM|[A-Z][A-Za-z'’\-]+,\s*(?:C\.?\s*J\.?|JJ?\.?"
    r"|Chief\s+Justice|Justice(?:\s+Pro\s+Tempore|\s+ad\s+hoc)?))$")
# The reference mark on a byline: a digit, an asterisk, or the symbol-font
# glyph Louisiana's asterisk actually is (U+F02A).
_MARK = re.compile(r"[\s.,:;*†‡\d]+$")

# WHICH FURNITURE CALLS TO HONOUR. Louisiana gives EVERY separate writing its
# own cover page, so the masthead, the docket and the first caption row
# repeat at the same coordinates on 3-8 pages of a record and core's
# `repeated_top_keys` reads the COVER's own masthead as a running head — on
# dwayne_williams and state_of_louisiana_v._leonidas_lowry that left the
# reader with no docket at all and it returned NOTHING. On this paper the
# repeated top band IS the paper, so only furniture that cannot be the
# court's writing is skipped, and the sheet's release number (which the
# finder calls a 'stamp') is kept so it is dropped with the header row it
# shares a line with.
_FURNITURE_SKIP = frozenset(("folio", "running-foot", "gutter", "filler"))

# ------------------------------------------------- the reprinted covers ---
# HOW FAR A REPRINTED COVER MAY RUN. Measured over all 50 records: every one
# of the 88 candidate pages carries its writing's byline on the SAME page, so
# a run is one page. Two pages of headroom, and a run that reaches the cap
# without meeting a byline is not this shape and nothing is claimed.
_REPRINT_PAGES = 3
# A COVER ROW IS CENTRED; PROSE IS NOT — but prose is JUSTIFIED to the full
# measure, so its mid-point lands on the axis too. Measured: the widest cover
# row is 0.76 of the sheet (the origin, and a long party row) and the body
# runs 72.0-540.2 = 0.765 with its first line indented to 108.0. So a run is
# ABORTED on a row that is full measure AND either opens on the paragraph
# indent or opens lower-case — no prose can be inside a claimed run.
_PROSE_WIDTH = 0.74
_PARA_INDENT = 108.0
_INDENT_TOL = 4.0
# THE BODY RAIL, measured: every byline in the corpus stands at 71.8-72.2 and
# no cover row does.
_RAIL = 72.0
_RAIL_TOL = 6.0
# HOW MANY ROWS A COVER MAY HOLD. Measured: 6 on most reprints and 7 where
# the origin wraps (vinton_harbor page 23). Three rows of headroom, and a run
# that outgrows it is not a cover.
_MAX_COVER_ROWS = 10


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="la")
def read_headmatter_la(model, geom, **_):
    """Read Louisiana's block — the Clerk's sheet and the court's cover."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE DISPATCH: the masthead, on whatever page the court set it. Never a
    # page number — page 1 is the Clerk's sheet, and a record that lost it
    # would put the paper on page 1.
    cover = None
    for pm in model.pages[:_MAX_PAGES]:
        for row in _rows(pm, finder):
            text = _norm(" ".join(l.plain for l in row))
            if _MASTHEAD.match(text) \
                    and (row[0].size or 0.0) >= _MASTHEAD_SIZE_MIN:
                cover = pm
                break
        if cover is not None:
            break
    if cover is None:
        return NOTHING

    ctx = _Ctx()
    # The sheet, where the court set one above the cover.
    for pm in model.pages:
        if pm.number >= cover.number:
            break
        _read_release(ctx, pm, finder)
    _read_cover(ctx, cover, finder)
    if not ctx.crit.get("docket_number"):
        return NOTHING
    # …and the cover the court reprints over every separate writing below.
    _read_reprints(ctx, model, cover, (ctx.crit.get("court") or "").upper(),
                   finder)
    ctx.crit["headmatter_style"] = STYLE
    return ctx.result()


# --------------------------------------------------------------------------
# page 1 — the Clerk's news-release sheet
# --------------------------------------------------------------------------

def _read_release(ctx, pm, finder) -> None:
    """Drop the Clerk's sheet, reading the disposition and the bench out of
    it and harvesting the handing-down date."""
    rows = _rows(pm, finder)
    if not rows:
        return
    # THE SHEET NAMES ITSELF, and only a page that does is claimed as one:
    # 'FOR IMMEDIATE NEWS RELEASE' over 'FROM: CLERK OF SUPREME COURT OF
    # LOUISIANA', both at the sheet's own 36.0 rail on all 50 records.
    head = [_norm(" ".join(l.plain for l in row)) for row in rows[:4]]
    if not any(_RELEASE.match(t) or _CLERK.match(t) for t in head):
        return
    # THE ENTRY OPENS on the row carrying a docket in the index column.
    start = None
    for i, row in enumerate(rows):
        if any(_INDEX_DOCKET.match(_norm(p.plain)) and p.x0 <= _INDEX_COL_MAX
               for p in row):
            start = i
            break
    if start is None:
        # Not this sheet: drop nothing and leave the page to core.
        return
    # The header, above the entry: the release's own name, the Clerk's name,
    # the handing-down sentence and the by-author index heading.
    for row in rows[:start]:
        text = _norm(" ".join(l.plain for l in row))
        handed = _HANDED.match(text)
        if handed:
            ctx.crit.setdefault("decision_date", _date(handed.group(1)))
        ctx.drop(row, "news-release")

    entry = rows[start:]
    # The matter column's x0 is set per record by the widest docket of the
    # release day (172.2-185.6 measured), so it is read off the opening row.
    opener = sorted(entry[0], key=lambda l: l.x0)
    matter_x0 = opener[1].x0 if len(opener) > 1 else opener[0].x0
    edge = matter_x0 - 20.0

    parts: list[list] = []
    prev_top = None
    for row in entry:
        top = min(l.top for l in row)
        if prev_top is None or top - prev_top > _PART_GAP:
            parts.append([])
        parts[-1].append(row)
        prev_top = top

    for idx, part in enumerate(parts):
        if idx == 0:
            _release_entry(ctx, part, edge)
            continue
        first = _matter_text(part[0], edge)
        if _VOTE.match(first) or _SITTING.match(first):
            for row in part:
                ctx.emit(row, "panel", centre=False)
            continue
        # THE DISPOSITION CLOSES ON ITS OWN SENTENCE, and the sentence
        # wraps: 'AFFIRMED IN PART; REVERSED IN PART; REMANDED. SEE' /
        # 'OPINION.' (bruce_a._okrepki). So the closer is looked for in the
        # part's joined text, never in its last row alone.
        if _SEE.search(_part_text(part, edge)):
            _disposition(ctx, part, edge)
            continue
        # A PART THIS SHEET'S GRAMMAR DOES NOT NAME stays the Clerk's, and
        # is recorded as dropped rather than parked on a role.
        for row in part:
            ctx.drop(row, "news-release")


def _release_entry(ctx, part, edge) -> None:
    """The first part: the index entry (docket, case name, parish), and on
    one record (vinton_harbor) the disposition run behind it at single
    leading."""
    # The index run closes on the parish parenthesis.
    close = None
    for i, row in enumerate(part):
        if _matter_text(row, edge).endswith(")"):
            close = i
            break
    if close is None:
        # No parish: the whole part is the index — unless a disposition is
        # hiding in it, in which case there is no landmark to split on and
        # the part is dropped whole rather than split on a guess.
        # (Measured: no record of the 50 takes this branch with a
        # disposition inside the part.)
        for row in part:
            ctx.drop(row, "news-release")
        return
    for row in part[:close + 1]:
        ctx.drop(row, "news-release")
    rest = part[close + 1:]
    if not rest:
        return
    if _SEE.search(_part_text(rest, edge)):
        _disposition(ctx, rest, edge)
        return
    for row in rest:
        ctx.drop(row, "news-release")


def _disposition(ctx, part, edge) -> None:
    said: list[str] = []
    for row in part:
        said.append(_matter_text(row, edge))
        ctx.emit(row, "disposition", centre=False)
    ctx.crit.setdefault("disposition", _norm(" ".join(said)))


def _part_text(part, edge) -> str:
    return _norm(" ".join(_matter_text(row, edge) for row in part))


def _matter_text(row, edge) -> str:
    return _norm(" ".join(l.plain for l in sorted(row, key=lambda l: l.x0)
                          if l.x0 >= edge))


def _date(phrase: str) -> str:
    """'the 27th day of June, 2025' -> 'June 27, 2025'; anything else is
    kept as the sheet printed it."""
    said = _norm(phrase)
    hit = _DAY_OF.match(said)
    if hit:
        return f"{hit.group(2)} {int(hit.group(1))}, {hit.group(3)}"
    return said


# --------------------------------------------------------------------------
# page 2 — the court's own cover
# --------------------------------------------------------------------------

def _read_cover(ctx, pm, finder) -> None:
    """Read the cover from the masthead to the byline."""
    rows = _rows(pm, finder)
    band = "top"                # top | docket | caption | origin
    caption: list[str] = []
    below: list[str] = []
    dockets: list[str] = []
    prev_top = None
    for row in rows:
        pieces = sorted(row, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        top = min(l.top for l in pieces)
        gap = None if prev_top is None else top - prev_top
        prev_top = top
        first = pieces[0]
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - pm.width / 2) <= _AXIS_TOL

        if band == "top":
            if _MASTHEAD.match(text):
                ctx.crit.setdefault("court", text)
                ctx.emit(pieces, "court")
                band = "docket"
            continue
        # THE BYLINE ENDS THE READER: at the rail, and naming a justice or
        # the court itself.
        bare = _MARK.sub("", text)
        if first.x0 <= 72.0 + 6.0 and _BYLINE.match(bare):
            break
        if not centred:
            break                       # the paper's prose has begun
        docket = _DOCKET.match(text)
        if docket and band == "docket":
            dockets.append(_norm(docket.group(1)))
            ctx.emit(pieces, "docket")
            continue
        if _CW.match(text) and band == "docket":
            ctx.emit(pieces, "docket")
            continue
        if _POSTURE.match(text) or _PROCEEDING.match(text):
            ctx.emit(pieces, "case-info")
            band = "origin"
            continue
        if _ORIGIN.match(text) or _TRIBUNAL.match(text):
            below.append(text)
            ctx.emit(pieces, "lower-court")
            band = "origin"
            continue
        if band == "origin":
            # The origin's own wrap, at single leading. A NEW element after
            # the origin that names no landmark is left to core rather than
            # tinted as the court below.
            if gap is not None and gap <= _ELEMENT_GAP:
                below.append(text)
                ctx.emit(pieces, "lower-court")
                continue
            break
        # THE BAND BETWEEN THE DOCKET AND THE ORIGIN IS THE CAPTION: the
        # parties, their pivot and the consolidation glue.
        band = "caption"
        caption.append(text)
        ctx.emit(pieces, "caption")

    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if len(dockets) > 1:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if caption:
        ctx.crit.setdefault("caption", caption)
        sides: list[list[str]] = [[]]
        for row in caption:
            if _PIVOT.match(row) or _CW.match(row):
                sides.append([])
                continue
            sides[-1].append(row)
        named = [" ".join(s) for s in sides if s]
        if named:
            ctx.crit.setdefault("parties", named)
            if len(named) > 1:
                ctx.crit.setdefault("case_name",
                                    f"{named[0]} v. {named[1]}")
            else:
                ctx.crit.setdefault("case_name", named[0])
    if below:
        ctx.crit.setdefault("lower_court", " ".join(below))


# --------------------------------------------------------------------------

def _read_reprints(ctx, model, cover, banner, finder) -> None:
    """Claim the cover Louisiana reprints over EVERY separate writing.

    Each separate writing opens on a fresh page that repeats the whole
    cover — masthead, docket, caption, origin — above its byline
    (vinton_harbor prints it on pages 19, 21, 23 and 24). Left unclaimed
    those rows render as the writing's first content, which is what the
    reviewer saw. A reader's `consumed` set is subtracted from the segment
    stream BEFORE assembly (pipeline.py:474-484), so claiming them here is
    not reaching into a writing: the rows never enter one.

    Recorded as `Dropped(kind="superfluous")`, the kind core already uses
    for cover apparatus a court prints twice — every row is a verbatim
    repeat of the cover that renders whole at the head of the document, so
    nothing court-written is lost and core still mines the drop for
    criteria. One `Dropped` PER PAGE: a `Dropped` carries a single page in
    its prov.
    """
    if not banner:
        return
    parser = BylineParser(get_profile("la").byline)
    page_no = cover.number + 1
    while page_no <= len(model.pages):
        block = _reprint_block(model, page_no, banner, finder, parser)
        if not block:
            page_no += 1
            continue
        for page in sorted({l.page for l in block}):
            ctx.drop([l for l in block if l.page == page], "superfluous")
        page_no = max(l.page for l in block) + 1


def _reprint_block(model, page_no, banner, finder, parser) -> list:
    """The reprinted cover that OPENS on ``page_no``, or [].

    GEOMETRY IDENTIFIES IT, not wording: the page's first content row is
    centred on the axis AND is the very row THIS document's own lead cover
    printed as the court naming itself. The run then closes at the next
    BYLINE — the same landmark that ends the lead walk — which stands at
    the body rail while every cover row is centred.

    THE ROW COUNT IS NOT FIXED and no top coordinate is keyed on: page 23
    of vinton_harbor wraps its origin onto a second row ('Parish of
    Calcasieu') that the other three covers fit on one line, and sets the
    whole cover 32pt higher.
    """
    pages = {pm.number: pm for pm in model.pages}
    pm = pages.get(page_no)
    if pm is None:
        return []
    rows = _rows(pm, finder)
    if not rows:
        return []
    head = sorted(rows[0], key=lambda l: l.x0)
    mid = (head[0].x0 + max(l.x1 for l in head)) / 2
    if abs(mid - pm.width / 2) > _AXIS_TOL:
        return []
    if _norm(" ".join(l.plain for l in head)).upper() != banner:
        return []
    block: list = []
    last = min(page_no + _REPRINT_PAGES, len(model.pages))
    for page in range(page_no, last + 1):
        for row in _rows(pages[page], finder):
            pieces = sorted(row, key=lambda l: l.x0)
            text = _norm(" ".join(l.plain for l in pieces))
            x1 = max(l.x1 for l in pieces)
            width = (x1 - pieces[0].x0) / pm.width
            centred = abs((pieces[0].x0 + x1) / 2 - pm.width / 2) <= _AXIS_TOL
            # THE RAIL CLOSES THE COVER, and the AXIS says which rail row is
            # the byline: every cover row is centred, and a byline is set
            # from the rail to wherever its words end (mid-point 163-289
            # against the 306 axis on vinton_harbor's four reprints). The
            # origin row starts at 74.9 on page 19 of that record — inside
            # the rail's tolerance — and it is the axis, not the rail alone,
            # that keeps it in the cover where it belongs.
            if pieces[0].x0 <= _RAIL + _RAIL_TOL and not centred:
                if _is_byline(text, parser):
                    return block      # the writing starts HERE, not above
                return []
            if width >= _PROSE_WIDTH \
                    and (abs(pieces[0].x0 - _PARA_INDENT) <= _INDENT_TOL
                         or text[:1].islower()):
                return []             # prose: NOT this shape, claim nothing
            block.extend(pieces)
            if len({l.top for l in block}) > _MAX_COVER_ROWS:
                return []             # too long to be a cover
    return []


def _is_byline(text: str, parser) -> bool:
    """Is this row one of the forms Louisiana signs a writing with?

    THREE GRAMMARS, because the court uses three and the shared parser is
    deliberately narrower than the paper. It takes the participle forms
    ('WEIMER, C.J., concurring in part and dissenting in part.',
    'PENZATO, Justice Pro Tempore, concurring.') and the bare ones
    ('McCALLUM, J.'), but NOT the finite-verb form the court also signs
    with ('Hughes, J., concurs in part and dissents in part.' — vinton_harbor
    page 21, 'GRIFFIN, J., dissents and assigns reasons.' —
    state_ex_rel._darrell_j._robinson page 8), which the la profile keeps out
    of the grammar on purpose so the Clerk's vote lines are not read as
    bylines. That form is the same printed shape as those vote lines, so it
    is recognized here by the very pattern that reads them (`_VOTE`), and
    only ever to CLOSE a run — never to open a writing.
    """
    bare = _MARK.sub("", text)
    return (parser.parse(text) is not None
            or parser.parse(bare) is not None
            or _BYLINE.match(bare) is not None
            or _VOTE.match(text) is not None)


def _rows(pm, finder) -> list[list]:
    """The page's rows, furniture removed, pieces of one printed line kept
    together (Louisiana's justified rows come apart at wide word gaps)."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() \
                or finder.kind(pm, line) in _FURNITURE_SKIP:
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
