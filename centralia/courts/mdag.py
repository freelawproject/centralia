"""Office of the Attorney General of Maryland ('mdag').

THIS IS NOT A COURT'S PAPER and it carries no court's furniture: there is no
banner, no docket, no caption, no panel, no `v.`, and nothing is appealed
from anywhere. What page 1 carries is the front of an OPINION IN A BOUND
VOLUME — `Opinions of the Attorney General of Maryland` — and every one of
the 42 records in this corpus prints it the same way:

    ┌────────────────────────────────────────────────────────────────┐
    │ 64                                        [108 Op. Att'y       │  the volume's
    │                                                                │  RUNNING HEAD,
    │                       ENVIRONMENT                              │  a TOPIC, centred
    │                                                                │
    │ NOISE REGULATION – AGRICULTURE – WHETHER "DEER                 │  the CATCHLINE:
    │      CANNONS" ARE EXEMPT FROM MARYLAND'S STATEWIDE             │  subject terms and
    │      NOISE REGULATION UNDER THE EXEMPTION FOR                  │  the QUESTION,
    │      "AGRICULTURAL FIELD MACHINERY"                            │  bold caps, first
    │                                                                │  line at the rail
    │                       May 17, 2023                             │  the DATE, centred
    │                                                                │
    │ The Honorable Earl F. Hance, President                         │  the REQUESTING
    │ Board of County Commissioners of Calvert County                │  OFFICIAL: name
    │                                                                │  over office, at
    │     The Board of County Commissioners for Calvert County has   │  the rail
    │ asked for our opinion on whether a farmer's use of a "deer     │  …and the opinion
    └────────────────────────────────────────────────────────────────┘

and closes, pages later, with the office's own signature — the Attorney
General, the Assistant Attorney General who prepared it, and the Chief
Counsel for Opinions and Advice.

THE CONTRACT — `volume cover`. Three landmarks in fixed order, each read by
GEOMETRY and none by wording:

  * THE TOPIC is the only row that is BOLD, CENTRED on the page axis, and
    standing clear RIGHT of the text rail. The catchline under it is bold
    too, but its first line begins AT the rail — so one test separates them
    and no word is matched.
  * THE CATCHLINE is the run of bold rows that follows, ending at the first
    row the volume did not set in bold. Its runover lines are indented 22-27
    points from the rail, which is this paper's paragraph indent, so the
    block reads as one unit and is emitted as one.
  * THE ADDRESSEE BLOCK is the run of rows set AT THE RAIL below the date.
    It ends where the opinion begins, and the page says where that is: the
    body's first line is INDENTED (rail + 22.4-27.4pt on every record), and
    an addressee line never is. Two officials are addressed on five records
    and three on two, so the block is grouped by its own leading — a gap of
    two leadings opens a new addressee, one leading continues the last.

DISPATCH: the topic row over a rail-set bold catchline. A record that does
not print that pair is not this paper and this reader returns NOTHING.

THE DATE IS OPTIONAL and its absence is a fact of the corpus, not a hedge:
`108oag108` prints none (its reduced-scale twin,
`maryland_attorney_general_opinion_108oag108`, prints 'September 21, 2023'
in the same place). The walk steps over the gap rather than failing.

THE RUNNING HEAD IS THE CITATION, and it is SPLIT ACROSS THE OPENING. The
verso carries `<folio>  [108 Op. Att'y` and the recto `Gen. 3]  <folio>`;
put together they are the opinion's volume cite, `108 Op. Att'y Gen. 3` —
stated nowhere else in the document. It is read before it is dropped.

…AND CORE CANNOT LEARN IT. `repeated_top_keys` counts the pages a key prints
on and admits it at 40% of them; an alternating head can never reach half,
so `Gen. 3]` sat at 7 pages of 18 against a floor of 7.2 and stayed in the
stream on every odd page of the corpus — rendered as an underlined heading
above the first paragraph, 165 stray fragments over 42 files. This court
declares its own stationery instead, by the test ohioctcl arrived at
independently: a piece of a head-band row whose SIBLING core already calls
furniture (the folio, always printed opposite it) is the same furniture —
plus the shape of the head itself, because on 23 rows of 947 the volume let
the head sink onto the first line of a display list and pdfio returned it
glued to the text ('Gen. 3] 3. chocolate;'). A glued row is left alone: half
a line cannot be claimed, and a stray fragment is better than a lost list
item.

THE PAPER IS AN OPINION, AND THE COURT SAYS SO. `classify_doc_type` returns
UNKNOWN on all 42 records — the series prints no doc-type heading, because
the volume's title is the heading — and an UNKNOWN document is assembled as
an ORDER. v1 called 37 of them opinions (the upgrade core makes when a
writing turns out to be signed) and 5 orders, and those 5 were the whole of
this court's v1 diff. The type is declared through `doc_type_final` instead
of inferred, which is what that seam is for.

WHAT THIS FILE DOES NOT DO. The footnotes, the paragraphing, the section
headings ('I', 'Background', 'Conclusion') and the closing signature are all
core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

MDAG = register(CourtProfile(
    "mdag", "Office of the Attorney General of Maryland",
    # ONE PAPER, ONE WRITING. An opinion of the Attorney General is the
    # office speaking with one voice: there is no bench, so there is nothing
    # to concur in or dissent from, and a record that comes back as two
    # writings has been split at one of its own numbered part headings.
    single_writing=True,
    # MEASURED on the corpus: the body's first line leaves the rail by 22.4pt
    # on the 432pt sheet and 27.4pt on the 612pt one. The catchline's runover
    # uses the same indent, which is why the cover reads as prose to a walk
    # that does not know this paper.
    para_indent_min=20.0,
))

# ---------------------------------------------------------------------------
# The volume's stationery, declared. Both halves of the running head, and the
# months the date row can name — a closed vocabulary, not an open one.
# ---------------------------------------------------------------------------
_HEAD_RECTO = re.compile(r"^Gen\.\s*(\d+)\]$")
_HEAD_VERSO = re.compile(r"^\[\s*(\d+)\s*Op\.\s*Att['’]?y$")
_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")
_DATE = re.compile(r"^(?:%s)\s+\d{1,2},\s+\d{4}$" % "|".join(_MONTHS))

# The head band: the volume sets its head at 9.4% of the sheet, and lets it
# sink to 12.7% where the page opens on a display list.
_HEAD_BAND = 0.17
# The page axis, and how far off it a centred row may sit.
_AXIS_TOL = 18.0
# A row is AT THE RAIL when it starts within this of the measured body x0.
_RAIL_TOL = 3.0
# Bounds, so no state runs away: the longest catchline in the corpus is 8
# rows and the longest addressee block 6.
_MAX_CATCHLINE = 12
_MAX_ADDRESSEE = 10


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, core's furniture removed, grouped by baseline.
    A row is a list of pieces: the volume justifies its catchline and pdfio
    returns 'INTERSTATE ' / 'MEDICAL ' / 'LICENSURE ' / 'COMPACT' as four
    pieces of one line (109oag73)."""
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


def _all_rows(pm) -> list[list]:
    """Every inked row, furniture included — what the stationery pass walks."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self) -> None:
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, row: list, role: str, align) -> None:
        parts = sorted(row, key=lambda l: l.x0)
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
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, parts: list, kind: str) -> None:
        parts = sorted(parts, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts)),
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        # WHAT KIND OF PAPER THIS IS, declared. `classify_doc_type` returns
        # UNKNOWN on every record of this corpus — the series prints no
        # doc-type heading anywhere, because the volume's title is the
        # heading — and an UNKNOWN document whose writing carries no byline
        # is typed an ORDER. This is not an order: it is an opinion of the
        # Attorney General, which is what the volume it is bound in is
        # called and what each record says of itself in its first paragraph.
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor,
                "doc_type_final": m.DocType.OPINION}


def _stationery(ctx: _Ctx, model, finder) -> tuple[str | None, str | None]:
    """Drop the volume's running head wherever it stands, and read the
    citation off it.

    Two tests, both required. THE SHAPE: the piece is one of the two halves
    this volume prints, alone on its own line — a half glued to body text is
    not claimed, because the claim is by line and half a line cannot be
    given back. THE SIBLING: core already calls something else on that row
    furniture (the folio, printed opposite the head on every page), which is
    the evidence that the row is the head band and not the type block."""
    vol = start = None
    for pm in model.pages:
        for row in _all_rows(pm):
            if min(p.top for p in row) > pm.height * _HEAD_BAND:
                continue
            kinds = [finder.kind(pm, p) for p in row]
            if not any(kinds):
                continue                    # no folio: not the head band
            stale = []
            for part, kind in zip(row, kinds):
                text = _norm(part.plain)
                recto = _HEAD_RECTO.match(text)
                verso = _HEAD_VERSO.match(text)
                if recto:
                    start = start or recto.group(1)
                elif verso:
                    vol = vol or verso.group(1)
                else:
                    continue
                # READ FIRST, DROP SECOND — and drop only what core left.
                # Core takes the verso half from page 2 on (its key clears
                # the repeat floor); reading the cite off the pieces it
                # already removed is how the volume number survives.
                if kind is None:
                    stale.append(part)
            for part in stale:
                ctx.drop([part], "running-head")
    return vol, start


def _addressees(groups: list[list[str]]) -> list[str]:
    """Who asked. Each group is one official: the name row, then the office
    row(s) under it. The name is the group's first row."""
    return [g[0] for g in groups if g]


@decider("headmatter.read", court="mdag")
def read_headmatter_mdag(model, geom, **_):
    """Read the volume's cover — topic, catchline, date, addressee — or
    NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = geom.body_x0 if geom and geom.body_x0 else 72.0
    right = geom.right_x1 if geom and getattr(geom, "right_x1", None) \
        else page1.width - rail
    lead = geom.lead if geom and geom.lead else 13.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, rail, body_size)

    rows = _rows(page1, finder)
    if not rows:
        return NOTHING

    def x0(row):
        return min(p.x0 for p in row)

    def x1(row):
        return max(p.x1 for p in row)

    def centred(row):
        return abs((x0(row) + x1(row)) / 2 - page1.width / 2) <= _AXIS_TOL

    def bold(row):
        return all(bool(p.all_bold) for p in row)

    # ---- the topic: bold, centred, clear right of the rail ---------------
    # Anything above it must be the volume's head — page 1 carries one on 34
    # of 42 records, and core lets page 1's top band through because on a
    # court's paper that band is the banner.
    idx = 0
    while idx < len(rows) and not (
            bold(rows[idx]) and centred(rows[idx])
            and x0(rows[idx]) > rail + 10):
        if min(p.top for p in rows[idx]) > page1.height * _HEAD_BAND:
            return NOTHING              # a full row where no head can be
        idx += 1
    if idx >= len(rows) or idx + 1 >= len(rows):
        return NOTHING
    topic = rows[idx]
    # ---- the catchline: bold, and its first row AT the rail --------------
    if not (bold(rows[idx + 1]) and abs(x0(rows[idx + 1]) - rail) <= _RAIL_TOL):
        return NOTHING                  # no catchline: not this paper

    ctx = _Ctx()
    vol, start = _stationery(ctx, model, finder)
    if vol and start:
        ctx.crit["citation"] = f"{vol} Op. Att’y Gen. {start}"

    # THE TOPIC is the volume's subject term, and the catchline under it the
    # subject terms and the question. One apparatus, set in one face by the
    # same hand — the reporter's, not the office's — so both carry the role
    # the model reserves for a reporter's subject matter.
    ctx.emit(topic, "headnotes", m.Align.CENTER)
    ctx.anchor.extend(p.id for p in topic)

    i = idx + 1
    taken = 0
    while i < len(rows) and bold(rows[i]) and taken < _MAX_CATCHLINE:
        ctx.emit(rows[i], "headnotes", m.Align.LEFT)
        i += 1
        taken += 1

    # ---- the date, when the volume printed one ---------------------------
    if i < len(rows) and centred(rows[i]) \
            and _DATE.match(_norm(" ".join(p.plain for p in rows[i]))):
        ctx.crit["decision_date"] = _norm(
            " ".join(p.plain for p in rows[i]))
        ctx.emit(rows[i], "date", m.Align.CENTER)
        i += 1

    # ---- the addressee block: at the rail, until the body's indent -------
    groups: list[list[str]] = []
    prev_top = None
    taken = 0
    while i < len(rows) and taken < _MAX_ADDRESSEE:
        row = rows[i]
        if abs(x0(row) - rail) > _RAIL_TOL:
            break                       # the body's first line is INDENTED
        if x1(row) >= right - 8:
            break                       # …and a full-measure row is prose
        text = _norm(" ".join(p.plain for p in row))
        top = min(p.top for p in row)
        if prev_top is None or top - prev_top > lead * 1.5:
            groups.append([text])
        else:
            groups[-1].append(text)
        prev_top = top
        ctx.emit(row, "caption", m.Align.LEFT)
        i += 1
        taken += 1

    # WHO ASKED — AND NOT AS `parties`. This paper has no parties and no
    # adversity: the render joins `criteria.parties` with ' v. '
    # (render/html.py), so the two officials of 109oag32 came back as
    # 'Jan L. Williams, Ph.D., CPA v. Christopher E. Dorsey' and the three
    # of 110oag82 as a three-way suit. The addressee block is recorded
    # VERBATIM in `caption` — the criterion whose contract is 'rows, as
    # printed' — and the officials' names in `case_name`, separated the way
    # the page separates them, by standing apart.
    if groups:
        ctx.crit["caption"] = [row for g in groups for row in g]
        ctx.crit["case_name"] = "; ".join(_addressees(groups))
    ctx.crit["headmatter_style"] = "volume cover"
    return ctx.result()
