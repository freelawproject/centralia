"""Court of Appeals of Virginia ('vactapp').

THE MEASUREMENT FIRST, because naming the shape IS the finding.

**vactapp draws NOT ONE VERTICAL RULE.** Page 1 of all 30 corpus records
carries zero; 29 of the 30 whole documents carry zero across every page
(``daniel_c._lavering`` has three, deep inside a table on a later page).
There is no rail, no rail glyph, no typed fence, and — unlike its sibling
``va``, where the whitespace gutter itself was the divider — no second
stack either: every caption row is CENTRED on the caption's own axis, and
the only rows that leave that axis are the roster, the argument note and
the counsel block, none of which is row-paired with anything.  So no
second column is invented.  One column is the honest reading.

WHAT IT DRAWS INSTEAD IS A LADDER OF HORIZONTAL RULES IN TWO MEASURES, and
the MEASURE names the zone (the ca5 rule, arrived at again):

  * THE CAPTION FENCE — 201.6pt wide, invariant to a tenth of a point over
    the whole corpus, centred on the page axis (x = 204.0-405.6, centre
    304.8 on a 612pt page).  It comes in a run of 3 (a single record) or 5
    (a consolidated pair), and consecutive fences SHARE an edge, so n
    fences enclose n-1 cells.  The cells alternate: docket, parties,
    docket, parties.
  * THE SHELF — the full measure, 467.2pt at the text margin (72.0-540.0).
    Exactly two, always below the last fence.  The first closes the roster
    zone and opens the origin; the second closes the counsel block and
    opens the announcement.

Two more drawn things on the same page are NOT structure, and the test is
the one ca5 and ca1 both needed — a rule whose ends coincide with the row
above it is an UNDERLINE:

  * the 135.8-226.3pt rect under the announced author's name — its width
    is not a measure at all, it is the NAME's, and its x-extent matches the
    row's to a fifth of a point ('JUDGE DAVID BERNHARD' 228.1-380.0
    against a rect at 228.1-379.8); pdfio already renders it as ``<u>``;
  * the 144.0pt rect at the left margin near the foot, which is the
    court's FOOTNOTE separator and belongs to the footnote zone.

    COURT OF APPEALS OF VIRGINIA          the masthead, above the ladder
    ───────────────                       fence
    Record No. 0501-25-4                    cell: the docket
    ───────────────                       fence
    BELAAL KHAN                             cell: the parties…
    v.                                      …the pivot…
    CYNTHIA MCALISTER, IN HER …             …and the other side
    ───────────────                       fence
    Present: Judges Beales, Raphael …     the roster, at the rail
    Argued at Arlington, Virginia         where it was heard
                 Opinion Issued May 5, 2026    the date, FLUSH RIGHT
    ─────────────────────────────────     SHELF
    FROM THE CIRCUIT COURT OF LOUDOUN …   the origin, on the caption axis
    James P. Fisher, Judge                who tried it, same axis
    Annette Kay Rubin (…), for appellant. the counsel block, at the rail
    Laurie L. Kirkland (…), for appellee.
    ─────────────────────────────────     SHELF
    PUBLISHED OPINION BY                  the announcement label
    JUDGE DAVID BERNHARD                  …and the author it labels
    Belaal Khan challenges the circuit …  the body, indented 36pt

THE DISPATCH IS THE FENCE RUN, not the banner and not the wording.  A page
with two or more 201.6pt axis-centred rules and two shelves below them is
this contract; ``COURT OF APPEALS OF VIRGINIA`` is a payload the geometry
already accounts for (and it is set at 14pt on 28 records and at the body's
12pt on two — ``logan_antigone`` and ``patrick_brian_stambler`` — so size
is not the landmark either).

THE SECOND PAPER (1 of 30) is the clerk's own list, ``cases_appealed_to_
supreme_court_of_virginia``: a dated notice of which published opinions
have been appealed on to the Supreme Court.  It draws NOTHING — zero rules
of any measure, zero bold rows — and opens on a LABELLED date at the body
rail instead of the court's name.  Its three opening rows are its
headmatter and the numbered list below them is its body; what it is not is
a ruling, so the reader types it a NOTICE.  Nothing else in the corpus
prints no rule, so the two contracts cannot be confused.

WHERE THE COUNSEL BLOCK ENDS AND HOW IT DIVIDES.  It ends at the second
shelf.  Inside it the court sets an appearance's own WRAP at the block's
single leading (13.8pt) and opens the next appearance a full double space
below (25.7-25.8pt) — measured on every multi-entry record in the corpus,
with no value in between.  Splitting on that gap is what keeps two
appearances from fusing into one attorneys string (review-backlog:
'vactapp counsel pairs fused into one attorneys block').

WHAT THE READER CANNOT DO ALONE.  The majority carries NO byline: like va,
this court ANNOUNCES its author above the body instead of signing the
writing, and the headmatter renders whole so the row cannot be lifted out.
The reader reports the announcement in ``announced_author`` and core signs
the lead writing from it — but only if the profile's grammar can read
``JUDGE DAVID BERNHARD``, and as registered it cannot (style 'prose' with
title-case titles).  See the port report: `rev_titles` +
`also_reversed=True` is the missing declared fact.  Until it lands the
majority stays unauthored, which is not a defect — it is what the paper
prints.
"""

from __future__ import annotations

import re

from .. import model as m
from ..audit import strip_tags, unescape_xml
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# NOTE: vactapp's CourtProfile is still registered in `courts/__init__.py`.
# It needs one more declared fact before core can sign the announced author
# (see the module docstring); that edit is reported, not made here.

STYLE_LADDER = "fenced caption ladder"
STYLE_CLERK_LIST = "clerk's appeal list"

# ---- vactapp's declared facts (measured over all 30 records) -------------
# THE CAPTION FENCE. 201.6pt on a 612pt page, centred on the axis. Over the
# corpus every one of the 97 fences measures 201.6 to within 0.05pt and
# centres at 304.8 (304.1 on logan_antigone, whose press run sits 0.7pt
# left). Nothing else on the page is within 40pt of that measure.
_FENCE_W = 201.6
_FENCE_W_SLACK = 4.0
_FENCE_AXIS_SLACK = 20.0
# THE SHELF: the full measure at the text margin, 467.2pt. Two per record.
_SHELF_MIN = 400.0
# THE COUNSEL BLOCK'S OWN TWO LEADINGS. A wrap inside one appearance is
# 13.8pt; the next appearance opens 25.7-25.8pt below. No gap in the corpus
# falls between them, so the threshold is the midpoint.
_COUNSEL_WRAP_MAX = 20.0
# THE RAIL. Counsel is set hard on it (x0 = 72.0 exactly on every one of
# the corpus's 74 counsel rows); the origin recital never is (its shallowest
# start is 79.7 on julianne_post's two-city circuit court).
_RAIL_SLACK = 2.0
# HOW FAR THE LADDER MAY RUN. The deepest announcement in the corpus is at
# top=583.5 (sabrina_g._knott, a consolidated pair with four appearances);
# a shelf below 0.88 of the page is not this paper's second shelf.
_SHELF_MAX_FRAC = 0.88
# THE PARAGRAPH INDENT the court opens its body on: 36pt off a 72pt rail.
# Nothing in the announcement comes within 80pt of it.
_INDENT = 36.0
# THE CLERK'S LIST opens on a LABEL and a date at the body rail.
_DATE_LABEL = re.compile(r"^(DATE|DATED)\s*:", re.IGNORECASE)

_RECORD_NO = re.compile(r"Record\s+No\.\s*([0-9]{4}-[0-9]{2}-[0-9])",
                        re.IGNORECASE)
_DOCKET_ROW = re.compile(r"^Record\s+Nos?\.", re.IGNORECASE)
_PIVOT = re.compile(r"^(v\.?|vs\.?)$", re.IGNORECASE)
_ROSTER_LABEL = re.compile(r"^PRESENT\s*:", re.IGNORECASE)
_ANNOUNCE = re.compile(
    r"^(PUBLISHED|UNPUBLISHED)?\s*OPINION\s+BY\s*:?$", re.IGNORECASE)
_ISSUED = re.compile(
    r"^(?:Opinion|Order|Judgment)\s+(?:Issued|Rendered|Filed)\s+(.+?)\.?$",
    re.IGNORECASE)
# The origin recital and the procedural posture: both leave the rail, both
# are set in capitals, and they say different things — 'FROM …' names the
# court below, 'UPON A REHEARING' names what this proceeding IS.
_FROM = re.compile(r"^FROM\s+(THE\s+)?\S", re.IGNORECASE)
_UPON = re.compile(r"^UPON\s+\S", re.IGNORECASE)
# THE BENCH WORDS of the roster — a finite role vocabulary, never a name.
# 'Present: Judges Athey, Raphael and Senior Judge Petty' yields three
# judges; without the vocabulary it yields one called 'Senior Judge Petty'.
_BENCH = ("judges", "judge", "chief", "senior", "associate", "justices",
          "justice", "the", "and")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


_FN_MARK = re.compile(r"<footnotemark>.*?</footnotemark>", re.DOTALL)


def _clean(markup: str) -> str:
    """The row's words with the footnote apparatus removed — a criterion
    states the fact, not the reference to a note about it.

    `strip_tags` drops the TAGS and keeps their content, which is right for
    prose and wrong for a reference mark: it left the trial judge as 'Daniel
    T. Lopez, Judge1' and made a party of 'CARLOS M. BROWN, RECTOR,
    UNIVERSITY OF VIRGINIA1'. The mark is deleted, not stripped."""
    return _norm(unescape_xml(strip_tags(_FN_MARK.sub("", markup or ""))))


def _is_caps(text: str) -> bool:
    t = _norm(text)
    return bool(t) and t == t.upper() and any(c.isalpha() for c in t)


def _roster_names(printed: str) -> list[str]:
    """The surnames in 'Present: Chief Judge Decker, Judges Malveaux and
    Duffan'. A bench word is a ROLE, never a name."""
    body = re.sub(r"^PRESENT\s*:\s*", "", _norm(printed), flags=re.IGNORECASE)
    out: list[str] = []
    for tok in re.split(r",|\band\b", body):
        words = [w for w in tok.replace(".", " ").split()
                 if w.lower() not in _BENCH]
        name = " ".join(words).strip(" .,")
        if name and name[:1].isupper():
            out.append(name)
    return out


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, body_size):
        self.geom = geom
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.dropped: list = []
        self.anchor: list[int] = []

    def row(self, line, role: str, align: str = "L", rel: float = 0.0):
        # ``align`` is DECLARED, never measured per row. Measured, this
        # court's caption comes apart: 'CYNTHIA MCALISTER, IN HER PERSONAL
        # AND INDIVIDUAL CAPACITY' spans 102.9-504.6 — dead centre on the
        # caption's own axis — and reads as LEFT with a 30.9pt indent (both
        # engines render it that way today), so one centred cell of a
        # centred caption came out ragged inside its own fence.
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role, rel=rel))
        self.consumed.add(line.id)

    def rule(self, page: int) -> None:
        # A READER THAT CLAIMS THE BLOCK RE-EMITS THE FENCES. Core draws
        # them in `read_headmatter`, and that pass only sees rows a reader
        # left behind — a total claim silences it, and the ladder that
        # names every zone would vanish from the render.
        self.items.append(m.Rule(prov=m.Prov(page), span="full"))

    def result(self, doc_type=None, announced=None):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": doc_type,
                # WHO THE PAGE SAYS WROTE IT. Reported, never lifted: the
                # row stays in the headmatter where the court prints it.
                "announced_author": announced}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="vactapp")
def read_headmatter_vactapp(model, geom, **_):
    """Read vactapp's fenced ladder or the clerk's list, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    width = pm.width or 612.0
    height = pm.height or 792.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [l for l in pm.lines
            if l.plain.strip() and not finder.kind(pm, l)]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING

    fences = sorted((r for r in pm.h_rules
                     if abs(r.width - _FENCE_W) <= _FENCE_W_SLACK
                     and abs((r.x0 + r.x1) / 2.0 - width / 2.0)
                     <= _FENCE_AXIS_SLACK),
                    key=lambda r: r.top)
    if len(fences) >= 2:
        return _read_ladder(model, pm, rows, fences, body_x0, height)
    # THE PAGE'S OWN LEFT MARGIN, not `geom.body_x0`. On the clerk's list
    # the numbered entries are indented two steps and outnumber everything
    # else, so the document geometry measures the body rail at 144.0 — the
    # date label at the real 72.0 margin then reads as OFF the rail and the
    # notice was declined. The leftmost row on the page is the margin.
    left_margin = min(l.x0 for l in rows)
    if not any(r.width >= 60 for r in pm.h_rules) \
            and not any(l.all_bold for l in rows[:6]) \
            and _DATE_LABEL.match(_norm(rows[0].plain)) \
            and abs(rows[0].x0 - left_margin) <= _RAIL_SLACK:
        return _read_clerk_list(model, pm, rows, left_margin)
    return NOTHING          # not this court's paper: core's walk is better


def _read_ladder(model, pm, rows, fences, body_x0, height):
    """The contract: masthead, fenced caption table, roster, origin,
    counsel, announcement."""
    shelves = sorted((r for r in pm.h_rules
                      if r.width >= _SHELF_MIN and r.top > fences[-1].top
                      and r.top <= height * _SHELF_MAX_FRAC),
                     key=lambda r: r.top)
    if len(shelves) < 2:
        return NOTHING          # the ladder always has both its shelves
    top_fence, last_fence = fences[0].top, fences[-1].top
    shelf0, shelf1 = shelves[0].top, shelves[1].top

    ctx = _Ctx(model, None, 12.0)
    ctx.crit["headmatter_style"] = STYLE_LADDER
    ctx.crit["court"] = "Court of Appeals of Virginia"

    # ---- the masthead: everything above the ladder ----------------------
    mast = [l for l in rows if l.top < top_fence]
    for line in mast:
        ctx.row(line, "court", align="C")

    # ---- the caption table: n fences enclose n-1 cells ------------------
    # A CELL IS THE UNIT OF MEANING, NOT THE ROW (the ca4 rule). Ask once
    # per cell what it holds: a 'Record No.' cell is the docket, anything
    # else is the parties. That is also what reads a CONSOLIDATED caption
    # in order — logan_antigone stacks docket / parties / docket / parties
    # for an appeal and its cross-appeal, and each pair is one case.
    cells: list[tuple[str, list]] = []
    for i in range(len(fences) - 1):
        lo, hi = fences[i].top, fences[i + 1].top
        held = [l for l in rows if lo < l.top < hi]
        if not held:
            continue
        kind = "docket" if _DOCKET_ROW.match(_norm(held[0].plain)) \
            else "caption"
        cells.append((kind, held))
    if not cells:
        return NOTHING
    ctx.rule(pm.number)
    for kind, held in cells:
        for line in held:
            ctx.row(line, kind, align="C")
        ctx.rule(pm.number)
    _dockets(ctx, cells)
    _case_name(ctx, cells)
    ctx.crit["caption"] = [_clean(line_markup(l))
                           for _k, held in cells for l in held]

    # ---- the roster zone: who sat, where it was heard, when it issued ---
    for line in [l for l in rows if last_fence < l.top < shelf0]:
        text = _norm(line.plain)
        if _ROSTER_LABEL.match(text):
            ctx.row(line, "panel")
            ctx.crit["panel_line"] = text
            ctx.crit.setdefault("judges", text)
            names = _roster_names(text)
            if names:
                ctx.crit["panel"] = names
            continue
        im = _ISSUED.match(text)
        if im:
            # FLUSH RIGHT, and declared so: the row is ragged left and the
            # date is the only thing on it.
            ctx.row(line, "date", align="R")
            ctx.crit.setdefault("decision_date", _norm(im.group(1)))
            continue
        # 'Argued at Williamsburg, Virginia' / 'Argued by videoconference'
        # — caption apparatus that is neither roster nor date.
        ctx.row(line, "case-info")
        ctx.crit.setdefault("submitted", text)
    ctx.rule(pm.number)

    # ---- the band between the shelves: the origin, then the counsel -----
    # THE RAIL DIVIDES THEM. Counsel is set hard on the body rail; the
    # origin recital and the trial judge are centred on the caption axis
    # and never reach it. The first rail row opens the counsel block and
    # everything above it in the band is the origin — so the split is
    # ordered as well as measured, and no row falls through.
    band = [l for l in rows if shelf0 < l.top < shelf1]
    cut = next((i for i, l in enumerate(band)
                if abs(l.x0 - body_x0) <= _RAIL_SLACK), len(band))
    _origin(ctx, band[:cut])
    _counsel(ctx, band[cut:])
    ctx.rule(pm.number)

    # ---- the announcement: the label, and the author it labels ----------
    announced = _announcement(ctx, [l for l in rows if l.top > shelf1],
                              body_x0)
    return ctx.result(m.DocType.OPINION, announced)


def _dockets(ctx, cells) -> None:
    """Every 'Record No.' the caption fences. The first is this appeal;
    the rest are the cases consolidated with it — never a citation, which
    this court does not print here at all."""
    records: list[str] = []
    for kind, held in cells:
        if kind != "docket":
            continue
        for line in held:
            for mm in _RECORD_NO.finditer(_clean(line_markup(line))):
                if mm.group(1) not in records:
                    records.append(mm.group(1))
    if records:
        ctx.crit["docket_number"] = f"Record No. {records[0]}"
        if records[1:]:
            ctx.crit["other_dockets"] = [f"Record No. {r}"
                                         for r in records[1:]]


def _case_name(ctx, cells) -> None:
    """The LEAD case's name, built from the party names either side of the
    pivot — never by joining the caption wholesale. A consolidated record
    fences each case separately, so the first party cell is the lead."""
    party_cells = [held for kind, held in cells if kind == "caption"]
    if not party_cells:
        return
    rows = [_clean(line_markup(l)) for l in party_cells[0]]
    piv = next((i for i, t in enumerate(rows) if _PIVOT.match(t)), None)
    if piv is None:
        whole = _norm(" ".join(rows)).rstrip(",")
        if whole:
            ctx.crit["parties"] = [whole]
            ctx.crit["case_name"] = whole
        return
    one = _norm(" ".join(rows[:piv])).rstrip(",")
    two = _norm(" ".join(rows[piv + 1:])).rstrip(",")
    sides = [s for s in (one, two) if s]
    if sides:
        ctx.crit["parties"] = sides
        ctx.crit["case_name"] = " v. ".join(sides)


def _origin(ctx, band) -> None:
    """Where the matter came from, what it came ON, and who tried it.

    Three things stand here and CASE tells the first two from the third:
    the origin recital and the procedural posture are set in capitals
    ('FROM THE CIRCUIT COURT OF ALBEMARLE COUNTY', 'UPON A REHEARING'),
    the trial judge is not ('Cheryl V. Higgins, Judge'). A recital may
    wrap, and its wrap is capitals too, so it joins the row it continues.
    """
    court_rows: list[str] = []
    posture: list[str] = []
    judges: list[str] = []
    target = None
    for line in band:
        text = _clean(line_markup(line))
        if not _is_caps(text):
            ctx.row(line, "lower-court", align="C")
            judges.append(text)
            target = None
            continue
        if _UPON.match(text):
            ctx.row(line, "case-info", align="C")
            posture.append(text)
            target = posture
            continue
        if _FROM.match(text) or target is None:
            ctx.row(line, "lower-court", align="C")
            court_rows.append(text)
            target = court_rows
            continue
        ctx.row(line, "lower-court" if target is court_rows
                else "case-info", align="C")
        target.append(text)
    if court_rows:
        ctx.crit["lower_court"] = _norm(" ".join(court_rows)).rstrip(".")
    if judges:
        ctx.crit["lower_court_judge"] = _norm(" ".join(judges))
    if posture:
        ctx.crit["history"] = _norm(" ".join(posture)).rstrip(".")


def _counsel(ctx, band) -> None:
    """The appearances, one HmLine per printed row — and DIVIDED, because
    two appearances are two facts. The block sets a wrap at 13.8pt and
    opens the next appearance 25.8pt down; nothing in the corpus falls
    between, so the gap is the divider (review-backlog: 'vactapp counsel
    pairs fused into one attorneys block')."""
    entries: list[list[str]] = []
    prev = None
    for line in band:
        ctx.row(line, "counsel")
        text = _clean(line_markup(line))
        if prev is None or line.top - prev > _COUNSEL_WRAP_MAX:
            entries.append([text])
        else:
            entries[-1].append(text)
        prev = line.top
    if entries:
        # ITEM 41: `criteria.attorneys` has only two sources in core, and a
        # reader that leaves counsel where the page prints it reaches
        # neither — so the appearances render perfectly and are stated
        # nowhere machine-readable. Closed locally, as nine other courts
        # already do, pending the queued patch.
        ctx.crit["attorneys"] = "\n\n".join(
            _norm(" ".join(e)) for e in entries)[:4000]


def _announcement(ctx, tail, body_x0) -> str | None:
    """The label and the name it labels, and nothing below them.

    The announcement is the last thing above the body: two BOLD rows well
    inside the measure (x0 = 191.8-257.4 over the corpus), the second of
    which is the author. The run ends at the first row that is not both —
    the body's opening line is not bold, and a bold row that starts at the
    rail or at the paragraph indent is the body's own heading, not a third
    line of the announcement. Weight alone would take it.
    """
    label = None
    author = None
    for line in tail:
        if not line.all_bold or line.x0 <= body_x0 + _INDENT + _RAIL_SLACK:
            break
        text = _clean(line_markup(line))
        if _ANNOUNCE.match(text):
            ctx.row(line, "title", align="C")
            # ANCHOR, NOT PAYLOAD. `classify.heading_doc_type` reads this
            # label as a doc-type heading (queue item 48), which is what
            # opens the unsigned majority; claimed away it could leave the
            # document with no writing, so the id is offered back.
            ctx.anchor.append(line.id)
            label = text
            up = text.upper()
            if up.startswith("UNPUBLISHED"):
                ctx.crit["publication_status"] = "unpublished"
            elif up.startswith("PUBLISHED"):
                ctx.crit["publication_status"] = "published"
            continue
        if label is None:
            break               # a bold row before the label is not ours
        # ITEM 65: `criteria.judges` comes from the LABELLED roster and from
        # nothing else. The announced author is not the bench — filed there
        # (as the sibling court does) the two become indistinguishable, and
        # this court prints a real roster twelve rows above.
        ctx.row(line, "author", align="C")
        ctx.anchor.append(line.id)
        if author is None:
            author = text
    return author


def _read_clerk_list(model, pm, rows, body_x0):
    """The clerk's dated notice of which published opinions have been
    appealed on to the Supreme Court of Virginia.

    It draws nothing at all, sets nothing bold, and opens on a LABELLED
    date at the body rail — the three measurements that tell it from the
    court's own paper, all of which the ladder records have. Its headmatter
    is the date and the sentence announcing what the list holds; the
    numbered list itself is the notice's body and is left where it is.
    """
    ctx = _Ctx(model, None, 12.0)
    ctx.crit["headmatter_style"] = STYLE_CLERK_LIST
    ctx.crit["court"] = "Court of Appeals of Virginia"
    for line in rows[:8]:
        text = _clean(line_markup(line))
        if abs(line.x0 - body_x0) <= _RAIL_SLACK and _DATE_LABEL.match(text):
            ctx.row(line, "date")
            ctx.crit.setdefault(
                "decision_date", _norm(text.split(":", 1)[1]))
            continue
        # The notice's own statement of what follows, ending on the colon
        # that introduces the list. Anything after that is the list.
        ctx.row(line, "summary")
        if text.rstrip().endswith(":"):
            break
    return ctx.result(m.DocType.NOTICE)
