"""Family Court of the State of New York ('nyfamct').

ONE RECORD. This court's corpus is a single PDF —
`matter_of_jahmarion_b.` (13pp) — so everything below is an OBSERVATION of
one instance, not a contract measured over a corpus. The file is written to
say so: every branch is guarded by a landmark it can actually see on the
page, and where the landmark is absent the reader returns NOTHING and lets
core's shared walk have the record. A reader that claims confidently from
one page is worse than one that declines.

TWO PAPERS ARE BOUND INTO ONE PDF, and they are not the same document.

    ┌─ page 1 · THE REPORTER'S COVER ─────────────────────────────────────┐
    │  a DRAWN BOX, 288.8pt wide, centred on the page axis (160.7-449.5   │
    │  on a 612pt page), divided into cells by 9 horizontal rules:        │
    │     ┌───────────────────────────────────────┐                       │
    │     │        Matter of Jahmarion B.         │  bold — the case name │
    │     ├───────────────────────────────────────┤                       │
    │     │       2026 NY Slip Op 30509(U)        │  the reporter's cite  │
    │     ├───────────────────────────────────────┤                       │
    │     │           February 19, 2026           │  decided              │
    │     ├───────────────────────────────────────┤                       │
    │     │      Family Court, Kings County       │  court and county     │
    │     ├───────────────────────────────────────┤                       │
    │     │ Docket Number: Docket No. E23191-25   │  labelled             │
    │     ├───────────────────────────────────────┤                       │
    │     │         Judge: Alan Beckoff           │  labelled             │
    │     ├───────────────────────────────────────┤                       │
    │     │ Cases posted with a "30000" identifier… the reporter's        │
    │     │ This opinion is uncorrected and not     CAVEAT — two cells    │
    │     │ selected for official publication.      of it                 │
    │     └───────────────────────────────────────┘                       │
    │  and, alone in the foot margin at top=780.8 in 9pt type, the        │
    │  browser's print footer: 'file:///LRB-ALB-FS1/…_FAM.html[02/24/…]'  │
    └─────────────────────────────────────────────────────────────────────┘

The cover is a web page printed to PDF — the footer names the HTML file it
was rendered from — which is why its fields arrive as a DRAWN TABLE rather
than as typography. That box is the dispatch: two vertical rules straddling
the page axis with five or more horizontals stacked between them. Nothing
here is found by searching for the words 'NY Slip Op'; the citation pattern
is required as a SECOND cue so a stray ruled table on some other paper
cannot be mistaken for this cover.

THE CAVEAT IS TWO STATEMENTS, AND THE BOX PARTS THEM. What looks like six
rows of one boilerplate block is a republication provenance note ('Cases
posted with a "30000" identifier … eCourts Service.') followed by a
PUBLICATION STATUS ('This opinion is uncorrected and not selected for
official publication.'). The reporter sets them in two different cells and
draws its rule between them at top=198.7; the page's leading says the same
thing a second time — 13.5pt inside a statement, 18.0pt across the break.
So the first is furniture, recorded as `Dropped(kind='notice')`, and the
second stays on the page as a headmatter row with role `publication` and is
read into `publication_status='unpublished'`. It is exactly what the '(U)'
suffix on '2026 NY Slip Op 30509(U)' says in shorthand; two independent
printed cues agree.

Core would not have found it. `pipeline.py:912-917`'s `_UNPUB` vocabulary
has 'not certified for publication' and 'not for publication' but not 'not
selected for official publication', so before this reader the record
carried no publication status at all. `pipeline.py:1588` guards its
re-application with `publication_status is None`, so the court's own answer
is not overwritten — measured, not assumed.

CORROBORATION FROM THE NEXT DESK. This court has ONE record, but the cover
is the New York State Reporter's, not the court's, and the sibling port of
`nycivct` measured four of them (2023 and 2026). Every number agrees to
0.1pt across all five: the box's rules (H at 32.2/50.2/68.2/86.2/104.2/
122.2/140.2/198.7/230.2, V at 160.7/163.0/447.2/449.5), the six field rows
(38.4/56.2/74.2/92.2/110.2/128.2, all 12.0pt, the first bold and the only
bold row on the page), and the caveat rows (146.2/159.7/173.2/186.7/204.7/
218.2). The reporter's stationery is therefore MEASURED, not observed once
— it is only what sits BELOW it, this court's own e-filed decision, that
rests on a single record. Two NY courts now read the same cover from two
files by deliberate choice; if `nysurct` and `nysupct` confirm it again, the
cover is worth extracting into one shared module and this file should give
its half up.

    ┌─ page 2 · THE COURT'S OWN PLEADING PAPER ───────────────────────────┐
    │                          At a Term of the Family Court of the       │
    │                          State of New York, held in and for the     │
    │                          County of Kings, at 330 Jay Street,        │
    │                          Brooklyn, New York on the 19th day of      │
    │                          February 2026.          ← the RECITAL,     │
    │  P R E S E N T:                                    right of the     │
    │  Hon. Alan Beckoff                                 page axis        │
    │  ------------------------------------------x  ← the TOP FENCE      │
    │  In the Matter of                :  Docket No: E23191-25            │
    │                                  :             E1278-26             │
    │        JAHMARION B.,             :  DECISION ON MOTION              │
    │  A Person Alleged to be          :                                  │
    │  A Juvenile Delinquent,          :                                  │
    │            Respondent.           :                                  │
    │  ------------------------------------------x  ← the BOTTOM FENCE   │
    │  Elsie Tan, Assistant Corporation Counsel, for the Presentment Ag…  │
    │  Robert J. Epstein for Respondent Jahmarion B.                      │
    │  Beckoff, J:                                  ← the BYLINE, the end │
    └─────────────────────────────────────────────────────────────────────┘

THE FENCE IS THE PARSER. The court types its caption box the typewriter way
— a run of hyphens capped with an 'x' at the corner — and types it TWICE, at
top=216.3 and top=361.3, both running x=72.0 to x=330.8. Those two rows do
three jobs at once and no wording is consulted for any of them:

  * they BOUND the caption: what stands between them is the caption band;
  * their RIGHT END, 330.8, is the caption's column split. The parties stand
    left of it (x1 <= 330.8); the docket cell and the paper's own name stand
    right of it (x0 = 360.1, 432.1). Membership is by side of a typed line;
  * everything ABOVE the top fence is the convening matter, and everything
    BELOW the bottom fence is the appearance block.

Inside that box the court also sets a COLON RAIL — ':' glyphs at x=324.1,
just inside the fence's right end — which is the glyph this paper draws its
divider with, so it is what the CaptionBlock records. Only two colons appear
on this record (rows 232.4 and 345.1), which is too few to call a column on
its own; the rail is therefore CONFIRMED by the fence rather than measured
independently, and where no colon stands in that window the block records a
whitespace gutter instead.

THE READER ENDS AT THE BYLINE, and the byline is parsed with this court's
own grammar, never matched as text. 'Beckoff, J:' is a title-case surname
with an UNDOTTED abbreviated title and a colon — core's DEFAULT_ABBREV
carries 'J.' only, so the row parsed as nothing and the opinion assembled
unbylined. The profile below declares the undotted form and, because a
Family Court judge is a JUDGE, expands the abbreviations to 'Judge' rather
than to the default 'Justice'. As a second bound the reader also stops at
BODY PROSE — a full-measure row at the paragraph indent, rail+36.0pt
(x=108.0 against a rail of 72.0, 14pt type) — so a record that prints no
byline cannot let the walk run into the opinion.

WHAT ONE RECORD CANNOT ESTABLISH. The cover box, its cell order, the caveat
wording and the typed fence are each seen ONCE. The reader therefore treats
every field as optional: a cell it cannot name is tagged `case-info` rather
than guessed at, the page-2 head is read only if the fence pair is actually
typed, and the cover alone is a legitimate (partial) claim. `parties` is
left unset — this is an 'In the Matter of' proceeding with no pivot, and
inventing a party split from one caption would be a guess dressed as a
reading.

PRIVACY. A Family Court record names a child. Only what the published PDF
prints is recorded, and the PDF itself prints the initialised form
('Jahmarion B.'). Nothing is expanded, inferred or looked up.

CORE DEFECTS MET (reported, not patched). The one that touches this record
is the missing undotted abbrev title, worked around by declaring it on the
profile — which is where a court fact belongs. Two more are recorded
because a sibling NY court hit them and this court will when its corpus
grows: `resolve/bylines.py:782-783` fails a HYPHENATED surname (it strips
only periods and apostrophes before `isalpha()`, while `is_caps_name` at
line 128 strips '-' correctly), and `pipeline.py:912-917`'s publication
vocabulary, above. Neither bites 'Beckoff, J:'.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..pdfio.rules import is_typed_rule
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# ---- the profile ---------------------------------------------------------
# ONE JUDGE, ONE WRITING. Family Court is a trial court: a single judge
# hears and decides, so there is no panel to concur in or dissent from.
#
# THE BYLINE. 'Beckoff, J:' — a title-case surname, an UNDOTTED 'J', a
# colon. `allow_titlecase_name` admits the name; the abbrev table below
# admits the undotted title AND expands it correctly: the bench of the
# Family Court of the State of New York is styled JUDGE, not Justice, so
# core's default expansion would have printed the wrong office. Ordered
# longest-first so 'C.J.' cannot be eaten by 'J.'.
_NY_FAMILY_ABBREV = (
    ("C.J.", "Chief Judge"),
    ("C. J.", "Chief Judge"),
    ("A.J.", "Administrative Judge"),
    ("S.J.", "Supervising Judge"),
    ("J.", "Judge"),
    ("J:", "Judge"),
)
NYFAMCT = register(CourtProfile(
    "nyfamct", "Family Court of the State of New York",
    byline=BylineGrammar(style="abbrev", allow_titlecase_name=True,
                         abbrev_titles=_NY_FAMILY_ABBREV),
    single_writing=True,
    # 14pt type, a half-inch first-line indent: 36.0pt off the rail.
    para_indent_min=18.0,
    rollout="migrated",
))

STYLE_COVER = "reporter cover"
STYLE_FENCE = "reporter cover + pleading fence"

# ---- nyfamct's declared facts (ONE record — observations, not a corpus) --

# THE COVER BOX, page 1. Its verticals run y=32.2-233.3 (h=201.0) and
# y=34.5-231.0 (h=196.5); its left and right edges are x=160.7 and x=449.5,
# so it is 288.8pt wide on a 612pt page and its centre (305.1) sits 0.9pt
# left of the axis.
_BOX_MIN_H = 100.0          # a box edge, not a caption divider
_BOX_TOP_BAND = 140.0       # …and it starts in the head of the page
_BOX_MIN_W = 180.0
_BOX_AXIS_TOL = 20.0        # centred on the page axis
_BOX_EDGE_PAD = 6.0         # a cell rule reaches the box's own edges
_BOX_RULE_MEASURE = 0.75    # …and runs most of its width
_BOX_MIN_ROWS = 5           # five stacked rules => at least four cells
# The browser's print footer, alone in the foot margin below the box.
_FOOT_BAND = 0.92           # fraction of the page height

# THE FENCE, page 2. Two typed rules of identical measure, x=72.0-330.8.
_FENCE_TOL = 3.0            # the two fences agree on both ends within this
_FENCE_MIN_W = 120.0
# The column split is the fence's own right end; a piece starting at or
# beyond it is in the right column (observed: 360.1 and 432.1 against
# 330.8, so there is 29pt of daylight and the tolerance need not be tight).
_COL_PAD = 0.0
# The colon rail stands just inside that right end (324.1 against 330.8).
_RAIL_GLYPH = ":"
_RAIL_WINDOW = 24.0
_RAIL_FLOOR = 2             # only two colons on this record — see docstring

# THE CLOSE. Body prose is a full-measure row at the paragraph indent,
# rail + 36.0pt (observed: x0=108.0 against a rail of 72.0).
_PARA_INDENT = 36.0
_PARA_TOL = 3.0
_BODY_MEASURE = 0.75
_RAIL_TOL = 3.0

# ---- what the cover's cells say (labels and patterns, never names) -------

# The New York State Reporter's own identifier. '(U)' is its unpublished
# flag; the reader does not read the flag, it reads the sentence below.
_SLIPOP = re.compile(r"^\d{4}\s+N\.?\s*Y\.?\s+Slip\s+Op\s+\d+\s*\(?[A-Z]?\)?$",
                     re.I)
_DOCKET_LABEL = re.compile(
    r"^(?:Docket|File|Index|Case)\s*(?:Numbers?|Nos?\.?)\s*:?\s*(\S.*)$", re.I)
# …and the label may be printed twice ('Docket Number: Docket No. E23191-25').
_DOCKET_INNER = re.compile(
    r"^(?:Docket|File|Index|Case)\s*(?:Numbers?|Nos?\.?)\s*:?\s*", re.I)
_JUDGE_LABEL = re.compile(r"^Judge\s*:\s*(\S.*)$", re.I)
_HON = re.compile(r"^(?:Hon(?:orable)?\.?)\s+(\S.*)$", re.I)
_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},\s+\d{4}$", re.I)
# The reporter's caveat: it OPENS on the republication sentence and CLOSES
# on its own full stop. Two cues, as a notice always has.
_NOTICE_OPEN = re.compile(r"^Cases\s+posted\s+with\b", re.I)
_NOTICE_STATUS = re.compile(
    r"not\s+selected\s+for\s+official\s+publication", re.I)

# ---- what the pleading paper says ---------------------------------------

# 'P R E S E N T:' — letter-spaced, so matched on its letters alone.
_PRESENT = re.compile(r"^P\W*R\W*E\W*S\W*E\W*N\W*T\W*:?\s*$", re.I)
# WHAT THE PAPER CALLS ITSELF: the court's own names for its own papers.
# A closed vocabulary, and the only place a row here is read by its words.
_TITLE_OPENERS = (
    "decision", "order", "opinion", "judgment", "memorandum", "findings",
    "amended", "corrected", "fact-finding", "dispositional",
)
# A docket cell in the caption's right column: labelled, or a bare number
# in the same column beneath one.
_CAPTION_DOCKET = re.compile(
    r"^(?:Docket|File|Index|Case)\s*(?:Numbers?|Nos?\.?)\s*:?\s*(\S.*)$", re.I)
_DOCKET_SHAPE = re.compile(r"^[A-Z]{0,3}[-/]?\d{3,7}[-/]\d{2,4}[A-Z]?$")


# HOW MUCH INK MAKES A PAGE READABLE. A scanned page behind the cover
# returns a handful of characters (matter_of_field, in the Surrogate's
# corpus, gives 4 a page); a typed pleading head gives hundreds. Below this
# there is no second paper to read and none to lose.
_SCAN_INK = 120


def _norm(text: str) -> str:
    return " ".join((text or "").split())


# --------------------------------------------------------------------------
# the page, measured
# --------------------------------------------------------------------------

def _raw_rows(pm) -> list[list]:
    """Every inked row of the page, grouped by baseline, FURNITURE INCLUDED.

    The cover's fields sit inside a drawn box in the top 240pt of page 1,
    which is exactly where core's stamp and running-head rules look; the
    reader reads the raw rows so it can place them and record whatever it
    does not place."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (round(l.top, 1), l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _cover_box(pm):
    """The reporter's cover, or None: two verticals straddling the page axis
    with `_BOX_MIN_ROWS` horizontals stacked between them.

    Returns (x0, x1, [row edge tops]) — the box, and the rules that cut it
    into cells."""
    verts = [v for v in pm.v_rules
             if v.height >= _BOX_MIN_H and v.top <= _BOX_TOP_BAND]
    if len(verts) < 2:
        return None
    x0 = min(v.x for v in verts)
    x1 = max(v.x for v in verts)
    if x1 - x0 < _BOX_MIN_W:
        return None
    if abs((x0 + x1) / 2.0 - pm.width / 2.0) > _BOX_AXIS_TOL:
        return None
    edges = sorted(h.top for h in pm.h_rules
                   if h.x0 >= x0 - _BOX_EDGE_PAD
                   and h.x1 <= x1 + _BOX_EDGE_PAD
                   and h.width >= (x1 - x0) * _BOX_RULE_MEASURE)
    # A rule whose ends coincide with the row above it is an UNDERLINE, not
    # a cell edge — the measure test above already excludes this record's
    # 30pt link underline at top=168.8, and it is stated here so the reason
    # is on the page rather than in the arithmetic.
    if len(edges) < _BOX_MIN_ROWS:
        return None
    return x0, x1, edges


def _cells(rows: list[list], box) -> list[list[list]]:
    """The box's rows, bucketed into the cells its rules cut."""
    x0, x1, edges = box
    out: list[list[list]] = [[] for _ in range(len(edges) - 1)]
    for group in rows:
        top = min(l.top for l in group)
        if top < edges[0] or top > edges[-1]:
            continue
        if min(l.x0 for l in group) < x0 - _BOX_EDGE_PAD:
            continue
        for i in range(len(edges) - 1):
            if edges[i] <= top < edges[i + 1]:
                out[i].append(group)
                break
    return out


def _fences(rows: list[list]) -> tuple | None:
    """The typed pleading fence PAIR, or None. Two rows of rule glyphs of
    the same measure; the first two found are the caption's own."""
    found = []
    for group in rows:
        if len(group) != 1:
            continue
        line = group[0]
        if line.x1 - line.x0 < _FENCE_MIN_W:
            continue
        if is_typed_rule(_norm(line.plain)):
            found.append(line)
    for i in range(len(found) - 1):
        a, b = found[i], found[i + 1]
        if abs(a.x0 - b.x0) <= _FENCE_TOL and abs(a.x1 - b.x1) <= _FENCE_TOL:
            return a, b
    return None


def _rail_x(band: list[list], split: float) -> float | None:
    """The colon rail: ':' glyphs standing just inside the fence's right
    end. Fewer than `_RAIL_FLOOR` and the block records a whitespace
    gutter instead of a glyph it cannot vouch for."""
    xs = []
    for group in band:
        for line in group:
            for c in line.chars:
                if (c.get("text") or "") != _RAIL_GLYPH:
                    continue
                if split - _RAIL_WINDOW <= c["x0"] <= split + _FENCE_TOL:
                    xs.append(c["x0"])
    if len(xs) < _RAIL_FLOOR:
        return None
    return sum(xs) / len(xs)


def _shed_rail(line, rail_x: float | None):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    if rail_x is None:
        return line
    lo, hi = rail_x - _FENCE_TOL, rail_x + _FENCE_TOL
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
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, finder):
        self.model = model
        self.finder = finder
        self.items: list = []
        self.dropped: list = []
        self.consumed: set = set()
        self.anchor: list = []
        self.crit: dict = {}

    # -- emitting ---------------------------------------------------------

    def _hm(self, pieces, role: str, align: m.Align) -> m.HmLine:
        text = ""
        for part in pieces:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = pieces[0]
        return m.HmLine(
            text=text.strip(),
            prov=m.Prov(first.page, tuple(p.id for p in pieces)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in pieces), role=role)

    def row(self, pieces, role: str, align: m.Align = m.Align.LEFT) -> None:
        if not pieces:
            return
        self.items.append(self._hm(pieces, role, align))
        self.consumed.update(p.id for p in pieces)

    def cell(self, pieces, role: str) -> m.HmLine:
        self.consumed.update(p.id for p in pieces)
        return self._hm(pieces, role, m.Align.LEFT)

    def blank(self, page: int, role: str) -> m.HmLine:
        return m.HmLine(text="", prov=m.Prov(page), role=role)

    def rule(self, line, page: int) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, (line.id,)),
                                 span="full", typed=True))
        self.consumed.add(line.id)

    def caption(self, page, left, right, rail, ids, split) -> None:
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=rail, rail_rows=len(left),
            style_id="typed-fence" if rail is None else "colon-rail",
            fp={"rail": rail, "split": round(split, 1),
                "fence_measure": round(split, 1)},
            prov=m.Prov(page, tuple(sorted(ids)))))

    def drop(self, pieces, kind: str, pm=None) -> None:
        """Record furniture. Where core's FurnitureFinder already classified
        a row the pipeline publishes its own Dropped for it, so recording it
        again would list the same row twice (the vtsuperct reading)."""
        if not pieces:
            return
        if self.finder is not None and pm is not None:
            mine = [p for p in pieces if not self.finder.kind(pm, p)]
            self.consumed.update(p.id for p in pieces)
            pieces = mine
            if not pieces:
                return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in pieces))[:600],
            prov=m.Prov(pieces[0].page, tuple(p.id for p in pieces)),
            kind=kind))
        self.consumed.update(p.id for p in pieces)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="nyfamct")
def read_headmatter_nyfamct(model, geom, **_):
    """Read the reporter's cover and, where the court typed one, the
    pleading head below it. NOTHING for anything else."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    if pm.ink_chars == 0:
        return NOTHING                      # a pure scan: nothing to read
    box = _cover_box(pm)
    if box is None:
        return NOTHING                      # no cover: not this paper
    rows = _raw_rows(pm)
    cells = _cells(rows, box)
    if not any(cells):
        return NOTHING
    # THE SECOND CUE. A ruled table alone is not the reporter's cover; the
    # cover always states the citation the Reporter assigned this opinion.
    if not any(_SLIPOP.match(_norm(" ".join(l.plain for l in g)))
               for cell in cells for g in cell):
        return NOTHING

    finder = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 12.0)
    ctx = _Ctx(model, finder)
    _read_cover(ctx, pm, cells, box)

    # THE SECOND PAPER IS PART OF THE CLAIM, not an optional improvement to
    # it. A court reader's items REPLACE the headmatter whole
    # (`pipeline.py:1564`), so a claim that stops at the foot of the cover
    # does not leave the pleading head where core had it — it re-classifies
    # it as BODY, and the decision opens on its own caption mangled into
    # prose. Where the page behind the cover carries a text layer and its
    # head cannot be read, the WHOLE claim is withdrawn and core keeps the
    # record; where that page is a bare scan there is no second paper's
    # headmatter to lose, and the cover claim stands alone.
    style = STYLE_COVER
    if len(model.pages) > 1:
        page2 = model.pages[1]
        if _read_pleading(ctx, page2):
            style = STYLE_FENCE
        elif page2.ink_chars >= _SCAN_INK:
            return NOTHING
    ctx.crit["headmatter_style"] = style
    return ctx.result()


# ---- page 1: the reporter's cover ----------------------------------------

def _read_cover(ctx: _Ctx, pm, cells, box) -> None:
    """The box's cells, in the order the cover prints them.

    Labelled and patterned cells name themselves; the two that do not (the
    case name and the court) are taken POSITIONALLY, first and next, and a
    cell that is neither is tagged `case-info` rather than guessed at."""
    unlabelled = 0
    in_notice = False
    notice: list = []
    for cell in cells:
        if not cell:
            continue
        pieces = [l for g in cell for l in g]
        text = _norm(" ".join(l.plain for l in pieces))
        if in_notice or _NOTICE_OPEN.match(text):
            # THE CAVEAT IS TWO STATEMENTS, AND THE BOX PARTS THEM. The
            # reporter sets the republication provenance ('Cases posted
            # with a "30000" identifier … eCourts Service.') in one cell
            # and the publication status ('This opinion is uncorrected and
            # not selected for official publication.') in the NEXT, and
            # draws its cell rule between them at top=198.7. The page's
            # LEADING says the same thing twice over — 13.5pt inside a
            # statement, 18.0pt across the break — so the split is measured
            # two independent ways and they agree.
            #
            # The first is furniture and is recorded as a notice. The
            # second is a REAL PUBLICATION STATUS and stays on the page as
            # a headmatter row.
            in_notice = True
            if _NOTICE_STATUS.search(text):
                ctx.row(pieces, "publication", m.Align.CENTER)
                ctx.crit.setdefault("publication_status", "unpublished")
            else:
                notice.extend(pieces)
            continue
        if _SLIPOP.match(text):
            ctx.row(pieces, "citation", m.Align.CENTER)
            ctx.crit.setdefault("citation", text)
            continue
        mo = _DOCKET_LABEL.match(text)
        if mo:
            ctx.row(pieces, "docket", m.Align.CENTER)
            value = _norm(_DOCKET_INNER.sub("", _norm(mo.group(1))))
            if value:
                ctx.crit.setdefault("docket_number", value)
            continue
        mo = _JUDGE_LABEL.match(text)
        if mo:
            ctx.row(pieces, "panel", m.Align.CENTER)
            name = _norm(mo.group(1))
            ctx.crit.setdefault("judges", name)
            ctx.crit.setdefault("panel", [name])
            continue
        if _DATE.match(text):
            ctx.row(pieces, "date", m.Align.CENTER)
            ctx.crit.setdefault("decision_date", text)
            continue
        # The two cells the cover does not label. Their ORDER is all this
        # record can vouch for: the case name first, the court next.
        if unlabelled == 0:
            ctx.row(pieces, "caption", m.Align.CENTER)
            ctx.crit.setdefault("case_name", text)
        elif unlabelled == 1:
            ctx.row(pieces, "court", m.Align.CENTER)
            ctx.crit.setdefault("court", text)
        else:
            ctx.row(pieces, "case-info", m.Align.CENTER)
        unlabelled += 1

    if notice and _norm(notice[-1].plain).endswith("."):
        # READ, THEN RECORDED. The caveat states this paper's publication
        # status in prose; the status is kept and the run is recorded as a
        # notice, which is what the headmatter does with a notice.
        if _NOTICE_STATUS.search(_norm(" ".join(l.plain for l in notice))):
            ctx.crit.setdefault("publication_status", "unpublished")
        ctx.drop(notice, "notice", pm)
    elif notice:
        # It opened and never closed: not a notice this reader recognizes.
        # Placed as apparatus rather than removed — a row nobody can name
        # is still a row the page printed.
        for line in notice:
            ctx.row([line], "case-info", m.Align.CENTER)

    # The browser's print footer, alone in the foot margin below the box.
    foot = [l for l in pm.lines
            if l.plain.strip() and l.top >= pm.height * _FOOT_BAND]
    if foot:
        ctx.drop(foot, "running-foot", pm)


# ---- page 2: the court's own pleading paper ------------------------------

def _read_pleading(ctx: _Ctx, pm) -> bool:
    """The head the court itself typed. True when the fence pair was there
    and the head was read; False leaves the page to core's shared walk."""
    rows = _raw_rows(pm)
    fence = _fences(rows)
    if fence is None:
        return False
    top_rule, bot_rule = fence
    split = top_rule.x1 + _COL_PAD
    # THE RAIL IS THE FENCE'S OWN LEFT END. The page's smallest x0 is not
    # it: the NYSCEF page stamp '[* 1]' sets at x0=1.0 in the foot margin,
    # and measured that way the appearance block was outside its own column
    # and the reader stopped at the fence.
    rail_x0 = top_rule.x0

    above = [g for g in rows if min(l.top for l in g) < top_rule.top]
    band = [g for g in rows
            if top_rule.top < min(l.top for l in g) < bot_rule.top]
    below = [g for g in rows if min(l.top for l in g) > bot_rule.top]

    _read_convening(ctx, pm, above)
    ctx.rule(top_rule, pm.number)
    _read_caption(ctx, pm, band, split)
    ctx.rule(bot_rule, pm.number)
    _read_counsel(ctx, pm, below, rail_x0)
    return True


def _read_convening(ctx: _Ctx, pm, above) -> None:
    """Above the fence: the RECITAL right of the page axis, the bench at the
    rail. Side of the axis decides; no row is read by its words."""
    axis = pm.width / 2.0
    for group in above:
        right = [l for l in group if l.x0 >= axis]
        left = [l for l in group if l.x0 < axis]
        if right:
            ctx.row(right, "court", m.Align.LEFT)
        if not left:
            continue
        text = _norm(" ".join(l.plain for l in left))
        ctx.row(left, "panel", m.Align.LEFT)
        mo = _HON.match(text)
        if mo and not _PRESENT.match(text):
            # 'Hon. …' — the honorific is a closed vocabulary, and the row
            # under 'P R E S E N T:' is the only place this paper names the
            # judge who sat.
            name = _norm(mo.group(1)).rstrip(",")
            ctx.crit["judges"] = name
            ctx.crit["panel"] = [name]


def _read_caption(ctx: _Ctx, pm, band, split: float) -> None:
    """The caption box. The fence's right end splits the columns; the colon
    rail, where the page sets one, is the divider the block records."""
    rail_x = _rail_x(band, split)
    left: list = []
    right: list = []
    ids: set = set()
    caption_rows: list[str] = []
    right_rows: list[tuple[str, str]] = []
    for group in band:
        l_cells, r_cells = [], []
        for line in group:
            shed = _shed_rail(line, rail_x)
            if shed is None:
                ids.add(line.id)
                ctx.consumed.add(line.id)
                continue
            (r_cells if shed.x0 >= split else l_cells).append(shed)
        for piece in l_cells + r_cells:
            ids.add(piece.id)
        if not l_cells and not r_cells:
            continue
        left.append(ctx.cell(l_cells, "caption") if l_cells
                    else ctx.blank(pm.number, "caption"))
        if l_cells:
            caption_rows.append(_norm(" ".join(p.plain for p in l_cells)))
        if r_cells:
            role, value = _right_role(_norm(" ".join(p.plain
                                                     for p in r_cells)),
                                      right_rows)
            right.append(ctx.cell(r_cells, role))
            right_rows.append((role, value))
        else:
            right.append(ctx.blank(pm.number, "case-info"))
    while left and not _plain(left[-1]) and not _plain(right[-1]):
        left.pop()
        right.pop()
    if not left and not right:
        return
    ctx.caption(pm.number, left, right,
                _RAIL_GLYPH if rail_x is not None else None, ids, split)
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows)
    for role, value in right_rows:
        if role == "title":
            ctx.crit.setdefault("title", value)
        elif role == "docket" and value:
            if "docket_number" not in ctx.crit:
                ctx.crit["docket_number"] = value
            elif value != ctx.crit["docket_number"]:
                ctx.crit.setdefault("other_dockets", []).append(value)


def _right_role(text: str, seen) -> tuple[str, str]:
    """What a right-column cell is. A labelled or number-shaped cell is a
    docket; a cell opening on one of the court's own names for its own
    papers is the title; anything else is caption apparatus."""
    mo = _CAPTION_DOCKET.match(text)
    if mo:
        return "docket", _norm(mo.group(1))
    if _DOCKET_SHAPE.match(text.rstrip(".,")) \
            and any(r == "docket" for r, _ in seen):
        return "docket", text.rstrip(".,")
    first = text.split()[0].lower().rstrip(":.,") if text.split() else ""
    if first in _TITLE_OPENERS:
        return "title", text
    return "case-info", text


def _read_counsel(ctx: _Ctx, pm, below, rail: float) -> None:
    """Below the fence: the appearances, and then the byline, which ends the
    reader. Bounded twice — the byline this court's grammar parses, and
    BODY PROSE at the paragraph indent."""
    parser = BylineParser(NYFAMCT.byline)
    measure = max((l.x1 for g in below for l in g), default=pm.width) - rail
    counsel: list[str] = []
    for group in below:
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        if parser.parse(text) is not None:
            break                            # the byline: the reader stops
        if len(group) == 1 and _is_body(group[0], rail, measure):
            break                            # body prose: the reader stops
        if abs(min(l.x0 for l in group) - rail) > _RAIL_TOL:
            break                            # outside the block's column
        ctx.row(group, "counsel", m.Align.LEFT)
        counsel.append(text)
    if counsel:
        # COUNSEL PRINTED IN THE HEADMATTER STAYS THERE — the rows are
        # placed above; only their MEANING is copied into criteria.
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])


def _is_body(line, rail: float, measure: float) -> bool:
    if abs(line.x0 - (rail + _PARA_INDENT)) > _PARA_TOL:
        return False
    return measure > 0 and (line.x1 - line.x0) >= _BODY_MEASURE * measure


def _plain(row: m.HmLine) -> str:
    return re.sub(r"<[^>]+>", "", row.text or "").strip()
