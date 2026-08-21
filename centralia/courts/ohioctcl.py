"""Ohio Court of Claims ('ohioctcl').

Everything unique to ohioctcl lives here. It imports core, never another
court file, and no other court file imports it — `ohio.py` (the Supreme
Court's slip) and `ohioctapp.py` (the twelve appellate districts) were both
READ as models for this port, same publisher and same public-domain cite
scheme, and neither is touched.

ONE PRINT SHOP, ONE CONTRACT. Unlike ohioctapp — where twelve districts set
twelve papers and the caption's divider had to name four of them — the Court
of Claims composes every paper in Columbus, and the cover is invariant over
all 30 records:

    [Cite as Bankston v. Cuyahoga Cty. Prosecutor's Office, 2026-Ohio-1718.]
                    IN THE COURT OF CLAIMS OF OHIO      12pt bold, on axis
    ANGELIQUE BANKSTON        │  Case No. 2025-00983PQ
        Requester             │  Judge Lisa L. Sadler
    v.                        │  DECISION AND ENTRY
    CUYAHOGA COUNTY PROSECUTOR'S ────────────────────   (an UNDERLINE)
    OFFICE                    │
        Respondent            │
    ─────────────────────────────────────────────────  the CLOSER, 468pt
    {¶1} Requester, a self-represented litigant, has filed written …

'railed cover' — THE DIVIDER IS DRAWN, AND SO IS ITS FOOT. The dispatch is
one measured pair of marks, never a word:

  * a DRAWN VERTICAL RULE on the page axis — measured x 304.9-309.1 on a
    612pt page (0.498-0.505 of the measure), height 138.0-165.6pt;
  * a DRAWN FULL-MEASURE HORIZONTAL RULE whose top coincides with that
    rail's FOOT — measured 468.3-468.8pt wide, and on all 30 records the
    two agree to within 0.1pt.

The pair is an upside-down T, which is also the fingerprint core's own
`caption band` sniffer already names for this court (`data-style=
"upside-down-t"`), reached independently — so the geometry is not this
reader's invention, only its dispatch. Both marks are required: the rail
alone would admit any ruled table, and the closer alone any court that
fences its front matter. A record that draws neither gets NOTHING, and
core's shared walk reads it instead.

The closer is what makes this court cheap to read: it states where the
front matter ENDS. Every one of the 30 records opens its body on the
paragraph marker immediately below it ({¶1}, measured 22.9-23.6pt down),
so the reader needs no byline test, no prose test and no counsel bound. It
claims page 1 down to the closer and stops. Later pages carry a three-row
running head ('Case No. 2025-00983PQ' / '-5-' / 'DECISION & ENTRY') and the
last page a clerk's stamp pair ('Filed April 8, 2026' / 'Sent to S.C.
Reporter 5/11/26'); core's furniture pass already knows all five, and this
reader never reaches them.

THREE ZONES, EACH FOUND BY THE PAIR:

  * ABOVE THE RAIL'S HEAD, exactly two rows on all 30 records — the
    bracketed cite instruction at 10pt in the top margin and the court
    naming itself at 12pt bold on the axis. Measured: the banner's foot
    stands 30pt or more clear of the rail's head, so a 6pt pad on the band
    cannot reach it;
  * BETWEEN THE HEAD AND THE CLOSER, the caption — split at the rail,
    glyph by glyph, and filed by which side of the drawn line a piece sits
    on (ca6's rule, ohioctapp's four dispatches, the same reading here);
  * the closer itself, re-emitted as a `Rule`: a reader that claims the
    block inherits the duty to draw the marks core would have drawn.

THE BRACKETED CITE LINE IS THE CITATION, AND THE BRACKETS STAY. '2026-Ohio-
1718' is the court's public-domain citation and goes in `citation`; 'Case
No. 2025-00983PQ' is the number this court gave the case and goes in
`docket_number`. Stored the other way round the cite displaces a real value
and every cover prints two dockets — which is what `ill` was doing until
2026-08-20. The row is EMITTED verbatim, role `citation`, not stripped and
not dropped, for ohioctapp's reason: it is the only place this paper prints
its citation at all. `ohio`'s slip can afford to record its bracket as
apparatus because that paper sets the cite on a row of its own; this one
does not. The Reporter's short form of the case name is read out of the
same row into `short_case_name`.

THE RIGHT-HAND STACK HAS THREE TENANTS, AND TWO OF THEM ANSWER TO A LABEL.
'Case No.' is the docket. 'Judge' / 'Magistrate' / 'Special Master' is the
bench — role `panel`, because that is who sat; the officers are read into
`panel` and `judges` and the rows kept as printed in `panel_line`. The cell
that answers to NO label is the paper's own name, and over the corpus that
is exactly what it is: 'DECISION', 'DECISION AND ENTRY', 'DECISION AND ENTY'
(sic, clyde), 'ENTRY', 'JUDGMENT ENTRY', 'ENTRY GRANTING DEFENDANT'S / MOTION
FOR SUMMARY JUDGMENT', 'REPORT AND RECOMMENDATION', 'SUPPLEMENTAL REPORT AND
/ RECOMMENDATION', 'RECOMMENDATION FOR DISMISSAL'. Role `title`.

A LABELLED ROW IS A NEW RUNG WHATEVER THE PITCH SAYS. Two records (burson,
maxey) name both the judge and the magistrate, and the court sets the second
officer on the very NEXT line — 13.8pt under the first, which is exactly the
pitch it uses for a WRAP ('SUPPLEMENTAL REPORT AND' / 'RECOMMENDATION',
13.8pt; 'ENTRY GRANTING DEFENDANT'S' / 'MOTION FOR SUMMARY JUDGMENT',
13.8pt). Pitch alone therefore publishes one officer called 'Judge Lisa L.
Sadler Magistrate Gary Peterson'. So the label wins over the pitch, and the
pitch decides only the unlabelled rows (ohioctapp reached the same rule from
the other end, where an origin recital wrapped into a docket).

THE PAPER'S OWN NAME TYPES THE PAPER. `classify_doc_type` runs before this
reader and reads the same row off the page, and it disagrees with itself
across the corpus: 'DECISION' came back `order` while 'DECISION AND ENTRY'
came back `opinion`, and both 'SUPPLEMENTAL REPORT AND RECOMMENDATION' and
'RECOMMENDATION FOR DISMISSAL' came back `opinion` next to eight plain
'REPORT AND RECOMMENDATION's typed `report-and-recommendation`. The reader
claims that row, so it declares the type: RECOMMENDATION → RR, DECISION →
OPINION, ENTRY → ORDER. Four records move (brown-austin and suchernick_0623
to RR, burson and nw_ohio to OPINION) and 26 are confirmed.

WHAT THIS READER DELIBERATELY DOES NOT DO:

  * IT DOES NOT NAME AN AUTHOR. The determinations are signed at the FOOT
    of the last page, in a conformed signature core reads as body prose
    ('LISA L. SADLER' / 'Judge'; 'SARAH PIERCE' / 'Special Master'), and a
    headmatter reader may not reach into a writing. The caption's first
    bench row IS the signer on all 30 records — measured — so an
    `announced_author` would be right 30 times; it is still withheld,
    because on burson and maxey the caption names TWO officers and only one
    signs, so the rule would be 'the first of them', which is a guess
    dressed as a reading. `authorless` is not a defect here (the owner's
    ruling, 2026-08-19): a tribunal that prints unsigned determinations
    means to. What the document needs is an ENDMATTER seam
    (`docs/core-patch-queue.md` item 39) — reported, not worked around.
  * IT CALLS A SPECIAL MASTER A SEAT ON THE BENCH, and that is a declared
    modelling choice rather than an oversight. `Criteria` has `panel`,
    `judges` and `panel_line` and no field for a court's other officers, so
    a report signed by 'Special Master Sarah Pierce' records
    `panel=['Sarah Pierce']` and `judges='Sarah Pierce'` — she is who sat.
    The OFFICE is not lost: `panel_line` keeps the rows exactly as the page
    prints them ('Judge Lisa L. Sadler; Magistrate Gary Peterson'), which
    is the only place the distinction can live until `Criteria` grows a
    field for it.
  * IT EMITS NO COUNSEL AND NO DATE. This court prints neither in its
    front matter: no appearances anywhere on the cover (so queue item 41,
    `criteria.attorneys` unreachable for a reader that keeps counsel in the
    block, does NOT manifest here), and the only date on the paper is the
    clerk's 'Filed' stamp on the last page, which is furniture. Inventing
    `decision_date` from it would state a fact the front matter does not.
  * IT DOES NOT REDRAW THE UNDERLINE UNDER THE PAPER'S OWN NAME. The court
    rules the title cell, and pdfio's underline quirk already tags those
    glyphs '<u>…</u>', so the emphasis is reproduced in the markup. Emitted
    as a `Rule` as well it would print twice. The test is ca1's and ca5's:
    a rule whose ends coincide with the ink of the row above it is
    emphasis, not a fence (measured here to 0.1pt on x0 and x1, and 30 of
    30 title cells carry one).
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES, register

# No shared entry exists for 'ohioctcl' today, so this is the only
# declaration site. The pop is insurance of the kind ohio, ala, ariz and
# ohioctapp all carry: if the shared table ever gains one, a missed edit
# there must not raise 'duplicate profile' and take the whole package down.
PROFILES.pop("ohioctcl", None)
OHIOCTCL = register(CourtProfile(
    "ohioctcl", "Ohio Court of Claims",
    # NO BYLINE GRAMMAR IS DECLARED, and that is measured rather than
    # skipped. The court signs 'LISA L. SADLER' over 'Judge' at the foot of
    # the last page — a stacked conformed signature, not a byline, and no
    # grammar in resolve/bylines.py parses a name and its title on two
    # lines. The reversed form that WOULD parse the caption's 'Judge Lisa L.
    # Sadler' would also fire on every 'Judge' in the court's own prose and
    # open phantom writings, so the default stands.
    rollout="migrated",
))

STYLE_RAILED = "railed cover"

# ---- ohioctcl's declared facts (measured over all 30 records) ------------
# THE DRAWN RAIL: x 304.9-309.1 on a 612pt page, height 138.0-165.6.
_MID_LO, _MID_HI = 0.44, 0.56
_RAIL_MIN_HEIGHT = 100.0
# THE CLOSER: a drawn horizontal 468.3-468.8pt wide (0.765-0.766 of the
# measure) whose top coincides with the rail's foot to within 0.1pt on all
# 30 records. The tolerance is 3pt, which is the width of the rule itself
# plus slack, and far short of the 22.9pt that separates the closer from the
# first body row.
_CLOSER_MEASURE = 0.6
_CLOSER_TOL = 3.0
# The band's head. The first caption row stands 1.7-1.8pt BELOW the rail's
# head and the banner's foot 30pt or more above it, so the pad is generous
# at 6 and still cannot reach the banner.
_BAND_PAD_TOP = 6.0
# A WRAP inside a caption cell sits within this multiple of its own type
# size of the row above; a new rung sits a blank line further down.
# Measured: wraps 13.8pt, rungs 27.6pt, type 12.0pt.
_CAP_PITCH = 1.35
# An underline's ends coincide with the ink of the row above it, this close.
_UL_GAP = 6.0
_UL_END = 6.0
# THE HEAD BAND. Every page after the first carries a three-piece running
# head on ONE visual row at top 37.8, and no body row on any page of any
# record opens above 73.8 — so the band is unambiguous at 60.
_HEAD_BAND = 60.0
# The banner is centred on the page axis to within 10pt (measured: its
# mid-point is 306.0 on a 612pt page, every record).
_CENTRED_TOL = 10.0

# THE CITE-AS INSTRUCTION. Its second capture is the court's own
# public-domain citation, its first the Reporter's short case name.
_CITE_AS = re.compile(
    r"^\[\s*Cite as\s+(.+?),\s*(\d{4}-Ohio-\d+)\s*\.?\s*\]$", re.I)
_CITE_OPEN = re.compile(r"^\[\s*Cite as\b", re.I)
# THE COURT NAMING ITSELF. One form, on all 30 records; the trailing
# 'OF OHIO' is optional against the day the compositor drops it.
_BANNER = re.compile(r"^IN THE COURT OF CLAIMS(?:\s+OF OHIO)?$", re.I)
# THE RIGHT STACK'S TWO LABELS. Everything else in that stack is the
# paper's own name.
_DOCKET_LAB = re.compile(r"^\(?\s*Case\s*Nos?\.\s*\S", re.I)
_BENCH_LAB = re.compile(
    r"^(?:Judge|Magistrate|Special\s+Master|Acting\s+Judge)\s+\S", re.I)
_BENCH_TITLE = re.compile(
    r"^(?:Judge|Magistrate|Special\s+Master|Acting\s+Judge)\s+", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME never is. This
# court sets the status on its own caption row, indented under the party.
_STATUS = re.compile(
    r"^\(?\s*(?:Cross[-\s]*)?"
    r"(?:Requesters?|Respondents?|Plaintiffs?|Defendants?|Petitioners?"
    r"|Relators?|Movants?|Claimants?|Appellants?|Appellees?|Intervenors?)"
    r"[A-Za-z\s\-/,.()\]]*$", re.I)
_PIVOT = re.compile(r"^-?\s*(?:v|vs)\.?\s*-?$", re.I)
_CONNECTOR = re.compile(r"^(?:and|&|et al\.?|,)$", re.I)
# The paragraph marker the body opens on, kept as a belt-and-braces bound:
# the closer already ends the block on all 30 records.
_PARA = re.compile(r"^\{\s*¶")
# WHAT THE PAPER CALLS ITSELF, TYPED. A closed vocabulary of the court's own
# paper names, tested in this order because 'RECOMMENDATION FOR DISMISSAL'
# is a recommendation and not an entry, and 'ENTRY GRANTING DEFENDANT'S
# MOTION FOR SUMMARY JUDGMENT' is an entry and not a decision.
_TYPE_BY_NAME = (
    (re.compile(r"RECOMMENDATION", re.I), m.DocType.RR),
    (re.compile(r"DECISION", re.I), m.DocType.OPINION),
    (re.compile(r"ENTRY", re.I), m.DocType.ORDER),
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _rows(pm):
    """This page's rows, in page order, each as its list of pieces.

    Grouped by pdfio's own row key so a row the extractor split at the
    vertical rule comes back whole — the caption is then split at the DRAWN
    RAIL, glyph by glyph, and not where the column gap happened to be wide
    enough (ca6's lesson, ohioctapp's implementation)."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not (line.plain or "").strip():
            continue
        key = line.row if line.row is not None else round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the drawn rail, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


# --------------------------------------------------------------------------
# the dispatch: the drawn rail and the drawn foot that closes it
# --------------------------------------------------------------------------

def _cover(pm):
    """This page's railed cover — (rail, closer) — or (None, None).

    Both marks are required and they must AGREE: the rail's foot is the
    closer's top. The rail alone would admit any ruled table and the closer
    alone any court that fences its front matter; the pair is printed on all
    30 records of this corpus and states both of the block's bounds."""
    best = None
    for v in (pm.v_rules or []):
        if not (pm.width * _MID_LO <= v.x <= pm.width * _MID_HI):
            continue
        if (v.bottom - v.top) < _RAIL_MIN_HEIGHT:
            continue
        for r in (pm.h_rules or []):
            if r.width < pm.width * _CLOSER_MEASURE:
                continue
            if abs(r.top - v.bottom) > _CLOSER_TOL:
                continue
            if best is None or (v.bottom - v.top) > (best[0].bottom
                                                     - best[0].top):
                best = (v, r)
    return best if best else (None, None)


def _is_underline(pm, r) -> bool:
    """A rule whose ends coincide with the INK of the row above it is
    emphasis, not a fence — ca1's and ca5's test. This court underlines the
    paper's own name on all 30 records (and both of its rows where the name
    wraps), and pdfio's quirk has already tagged those glyphs '<u>', so the
    emphasis is in the markup and drawing it again would print it twice."""
    for line in pm.lines:
        if abs(r.top - line.bottom) > _UL_GAP:
            continue
        ink = [c for c in line.chars if (c.get("text") or "").strip()]
        if not ink:
            continue
        x0 = min(c["x0"] for c in ink)
        x1 = max(c.get("x1", c["x0"]) for c in ink)
        if abs(r.x0 - x0) <= _UL_END and abs(r.x1 - x1) <= _UL_END + 2.0:
            return True
    return False


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ohioctcl")
def read_headmatter_ohioctcl(model, geom, **_):
    """Read ohioctcl's railed cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    rail, closer = _cover(pm)
    if rail is None:
        return NOTHING
    body_size = geom.body_size if geom and geom.body_size else 12.0
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0

    ctx = _Ctx(geom, body_size)
    walk = _Walk(ctx, rail, closer, body_size)
    walk.page(pm)
    walk.flush()
    # A READER THAT CLAIMS A REGION INHERITS ITS FURNITURE — and this
    # court's running head is made OUT OF the cover the reader just took.
    finder = FurnitureFinder(model, body_x0, body_size)
    for later in model.pages[1:]:
        walk.stale_head(later, finder)

    # THE CRITERIA ARE BUILT BEFORE THEY ARE JUDGED. `finish()` is what
    # reads the walk's collected cells into `citation` and `docket_number`;
    # asking for them first refuses every record just read correctly (wyo
    # shipped that inversion and lost all 50 of its own records).
    walk.finish()
    if not ctx.crit.get("citation") and not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result(walk.anchor, walk.doc_type())


class _Walk:
    """The classifier. Page 1 only, bounded above by the rail's head and
    below by the drawn closer at its foot."""

    def __init__(self, ctx, rail, closer, body_size):
        self.ctx = ctx
        self.mid = rail.x
        self.head = rail.top - _BAND_PAD_TOP
        self.foot = closer.top
        self.rail = rail
        self.closer = closer
        self.body_size = body_size
        self.anchor: list[int] = []
        # the pending caption stacks, flushed at the foot of the band
        self.left: list = []
        self.right: list = []
        self.cap_ids: list[int] = []
        # the right stack's last tenant: its top, its text and its role,
        # which is what tells a wrap from a new rung
        self.r_top: float | None = None
        self.r_text = ""
        self.r_role: str | None = None
        self.wrapped = False
        self.cap_page = 1
        # the printed forms, kept beside the parsed ones
        self.banner: list[str] = []
        self.cap_rows: list[str] = []
        self.cite: tuple[str, str] | None = None
        self.dockets: list[str] = []
        self.bench: list[str] = []
        self.titles: list[str] = []

    # -- one page -------------------------------------------------------
    def page(self, pm) -> None:
        for row in _rows(pm):
            top = min(p.top for p in row)
            bottom = max(p.bottom for p in row)
            text = _norm(" ".join(p.plain for p in row))
            if not text:
                continue
            # THE CLOSER STATES WHERE THE FRONT MATTER ENDS. Nothing at or
            # below it belongs to this reader — the body opens on the
            # paragraph marker 22.9-23.6pt under it on all 30 records.
            if top >= self.foot or _PARA.match(text):
                break
            if bottom <= self.head:
                self._above(pm, row, text)
                continue
            self._caption(pm, row)
        self.flush()
        # A READER THAT CLAIMS THE BLOCK RE-EMITS ITS FENCES. Core draws
        # them in `read_headmatter`, and that pass only runs on rows the
        # reader left behind, so a total claim silences it (ca4's rule).
        if not _is_underline(pm, self.closer):
            self.ctx.rule(pm.number, span="full")

    # -- the furniture the claim inherits -------------------------------
    def stale_head(self, pm, finder) -> None:
        """The running head core's repeat floor cannot learn.

        Every page after the first carries this court's head as ONE visual
        row of three pieces — the docket, the folio, and the paper's own
        name ('Case No. 2025-00959PQ' / '-2-' / 'JUDGMENT ENTRY'). Core
        learns a head by REPETITION, so on a TWO-page record each piece is
        printed exactly once and the third piece — the only one whose text
        is not a number — is left in the stream. Measured over the corpus:
        core names all three on the 23 records of three pages or more and
        only the first two on the seven records of two pages
        (`docs/core-patch-queue.md` item 6 is the same defect from the
        other end).

        Left there it is not merely an unread row: it is a DOCTYPE HEADING
        in the court's own words, and with the page-1 title claimed it
        becomes the FIRST one in the document, so assembly opens a second
        writing on it and the paper is bisected — five records did exactly
        that on the first pass.

        The test is structural and needs no wording: a piece of a head-band
        row whose SIBLINGS core already calls furniture is the same
        furniture. It fires only where core's own pass came up short, so
        nothing is recorded twice (queue item 46)."""
        for row in _rows(pm):
            if min(p.top for p in row) >= _HEAD_BAND:
                continue
            kinds = [finder.kind(pm, p) for p in row]
            stale = [p for p, k in zip(row, kinds) if k is None]
            if stale and any(kinds) and len(stale) < len(row):
                self.ctx.drop(stale, "running-head")

    # -- above the rail's head ------------------------------------------
    def _above(self, pm, row, text: str) -> None:
        """The two rows every record prints over its caption: the bracketed
        cite instruction and the court naming itself. Anything else stays
        unclaimed — an untagged row is honest and measurable, and core's
        shared walk will place it."""
        if _CITE_OPEN.match(text):
            self.ctx.emit(row, "citation", pm)
            mm = _CITE_AS.match(text)
            if mm and self.cite is None:
                self.cite = (mm.group(1), mm.group(2))
            return
        if _BANNER.match(text):
            self.banner.append(text)
            self.ctx.emit(row, "court", pm, centred=True)
            return

    # -- the caption ----------------------------------------------------
    def _caption(self, pm, row) -> None:
        """One caption row, split at the drawn rail and filed by side."""
        l_cells, r_cells = [], []
        for line in row:
            for side, bucket in ((_side(line, self.mid, "L"), l_cells),
                                 (_side(line, self.mid, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left_text = _norm(" ".join(c.plain for c in l_cells))
        right_text = _norm(" ".join(c.plain for c in r_cells))
        self.cap_page = pm.number
        role = self._right_role(row, right_text) if r_cells else "caption"
        self.left.append(self.ctx.cell(l_cells, "caption", pm)
                         if l_cells else self.ctx.blank(pm))
        self.right.append(self.ctx.cell(r_cells, role, pm)
                          if r_cells else self.ctx.blank(pm))
        self.cap_ids.extend(l.id for l in row)
        self.ctx.consumed.update(l.id for l in row)
        if left_text:
            self.cap_rows.append(left_text)
        if right_text:
            self._file_right(role, right_text)
            if role == "title":
                self.anchor.extend(l.id for l in r_cells)
            self.r_top = min(p.top for p in row)
            self.r_text = right_text
            self.r_role = role

    def _right_role(self, row, text: str) -> str:
        """What a right-hand cell is, by the LABEL the court printed on it.

        The stack holds the docket and the bench, each labelled, and one
        cell that carries no label at all. That cell is the paper's own
        name, on all 30 records.

        A LABELLED ROW IS A NEW RUNG WHATEVER THE PITCH SAYS: burson and
        maxey set 'Magistrate Gary Peterson' 13.8pt under 'Judge Lisa L.
        Sadler', which is exactly the pitch this court uses for a WRAP, so
        pitch alone publishes one officer with two names and two titles."""
        top = min(p.top for p in row)
        size = max((p.size or 0.0) for p in row) or self.body_size
        wrap = (self.r_top is not None
                and 0 < top - self.r_top <= size * _CAP_PITCH)
        labelled = bool(_DOCKET_LAB.match(text) or _BENCH_LAB.match(text))
        if wrap and self.r_role and not labelled:
            self.wrapped = True
            return self.r_role
        self.wrapped = False
        if _DOCKET_LAB.match(text):
            return "docket"
        if _BENCH_LAB.match(text):
            return "panel"
        return "title"

    def _put(self, bucket: list, text: str) -> None:
        """File one row's text, JOINED to the row above it where it
        wrapped. Provenance merges with it — the cell's own line ids are
        already in `cap_ids`."""
        if self.wrapped and bucket:
            prev = bucket[-1]
            bucket[-1] = (prev + text) if prev.endswith("-") \
                else f"{prev} {text}"
            return
        bucket.append(text)

    def _file_right(self, role: str, text: str) -> None:
        # A DOCKET AND AN OFFICER ARE EACH A WHOLE STATEMENT, never joined
        # to the one above: this court stacks two officers on consecutive
        # lines, and joining them made one judge out of two.
        if role == "docket":
            self.dockets.append(text)
        elif role == "panel":
            self.bench.append(text)
        elif role == "title":
            self._put(self.titles, text)

    def flush(self) -> None:
        """Close the pending caption block."""
        if not self.left and not self.right:
            return
        while self.left and not _strip_tags(self.left[-1].text).strip() \
                and not _strip_tags(self.right[-1].text).strip():
            self.left.pop()
            self.right.pop()
        if self.left:
            self.ctx.caption(self.cap_page, self.left, self.right,
                             self.cap_ids)
        self.left, self.right, self.cap_ids = [], [], []

    # -- the parsed forms ------------------------------------------------
    def finish(self) -> None:
        crit = self.ctx.crit
        crit["headmatter_style"] = STYLE_RAILED
        if self.cite:
            crit["citation"] = self.cite[1]
            if self.cite[0]:
                crit["short_case_name"] = _norm(self.cite[0])
        if self.banner:
            crit["court"] = ", ".join(self.banner)
        if self.cap_rows:
            crit["caption"] = self.cap_rows[:40]
            names = _party_names(self.cap_rows)
            if names:
                crit["parties"] = names[:8]
            pivot = _case_name(self.cap_rows)
            if pivot:
                crit["case_name"] = pivot
        nums = _numbers(self.dockets)
        if nums:
            crit["docket_number"] = nums[0]
            if nums[1:]:
                crit["other_dockets"] = nums[1:]
        if self.bench:
            crit["panel_line"] = "; ".join(self.bench)
            seat = [n for n in (_BENCH_TITLE.sub("", b).strip(" .,")
                                for b in self.bench) if n]
            if seat:
                crit["panel"] = seat
                crit["judges"] = ", ".join(seat)
        if self.titles:
            crit["title"] = _norm(" ".join(self.titles))

    def doc_type(self):
        """THE PAPER'S OWN NAME TYPES THE PAPER — see the docstring."""
        name = _norm(" ".join(self.titles))
        for rx, kind in _TYPE_BY_NAME:
            if rx.search(name):
                return kind
        return None


# --------------------------------------------------------------------------
# what the rows say
# --------------------------------------------------------------------------

def _numbers(rows: list[str]) -> list[str]:
    """The case numbers a labelled row carries, with the label removed."""
    out: list[str] = []
    for row in rows:
        body = re.sub(r"^\(?\s*Case\s*Nos?\.\s*", "", _norm(row), flags=re.I)
        body = body.strip(" ,.;()")
        if not body or body.lower().startswith(("no.", "nos.")):
            continue
        for piece in re.split(r";|,\s*(?=\d)|\band\b", body):
            piece = piece.strip(" ,.;()")
            if piece and piece not in out:
                out.append(piece)
    return out


def _party_names(rows: list[str]) -> list[str]:
    """The party names, built from the rows a status label does NOT close.

    Joining the caption wholesale yields 'ANGELIQUE BANKSTON Requester v.
    CUYAHOGA COUNTY PROSECUTOR'S OFFICE Respondent'; splitting per row
    yields two halves of one respondent, because this court wraps a long
    party name onto the next line ('CUYAHOGA COUNTY PROSECUTOR'S' /
    'OFFICE')."""
    names: list[str] = []
    run: list[str] = []
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        if _CONNECTOR.match(flat) or _PIVOT.match(flat) or _STATUS.match(flat):
            if run:
                names.append(_norm(" ".join(run)).strip(" ,;:"))
                run = []
            continue
        run.append(flat)
    if run:
        names.append(_norm(" ".join(run)).strip(" ,;:"))
    return [n for n in names if n]


def _case_name(rows: list[str]) -> str | None:
    """'X v. Y', from the party names either side of the printed pivot."""
    above: list[str] = []
    below: list[str] = []
    side = above
    for row in rows:
        if _PIVOT.match(_norm(row)):
            if below:
                break
            side = below
            continue
        side.append(row)
    one, two = _party_names(above), _party_names(below)
    if not one or not two:
        return None
    return f"{one[0]} v. {two[0]}"


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where on the page it came from."""

    def __init__(self, geom, body_size):
        self.geom = geom
        self.body_size = body_size
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def _line(self, parts: list, role: str, align, rel=0.0) -> m.HmLine:
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role)

    def emit(self, group: list, role: str, pm, centred: bool = False) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        cx = (first.x0 + max(p.x1 for p in parts)) / 2
        rel = 0.0
        if centred and abs(cx - pm.width / 2) <= _CENTRED_TOL:
            align = m.Align.CENTER
        else:
            align = m.Align(line_alignment(
                first, pm.width, self.geom,
                banner_center_min_size=self.body_size + 2.0))
            if align is m.Align.LEFT and self.geom \
                    and first.x0 > self.geom.body_x0 + 12:
                rel = min(first.x0 - self.geom.body_x0, pm.width * 0.6)
        self.items.append(self._line(parts, role, align, rel))
        self.consumed.update(p.id for p in parts)

    def cell(self, parts: list, role: str, pm) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock."""
        parts = sorted(parts, key=lambda l: l.x0)
        self.consumed.update(p.id for p in parts)
        return self._line(parts, role, m.Align.LEFT)

    @staticmethod
    def blank(pm) -> m.HmLine:
        return m.HmLine(text="", prov=m.Prov(pm.number), role="caption")

    def caption(self, page: int, left: list, right: list, ids) -> None:
        # THE TWO STACKS ARE ROW-PAIRED, because this court pairs them: the
        # docket stands beside the first party, the bench beside its status
        # and the paper's own name beside the pivot, on 27 of the 30
        # records. Where the compositor staggers them (nw_ohio sets its
        # right stack between the left's rows) the pairing reproduces the
        # stagger, blanks and all — which is what the page prints. v1
        # stacked the two columns independently and lost it.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail="|",
            rail_rows=max(len(left), 1),
            style_id=STYLE_RAILED,
            fp={"rail": "drawn"},
            prov=m.Prov(page, tuple(sorted(set(ids))))))

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:600],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int, span: str = "full") -> None:
        self.items.append(m.Rule(prov=m.Prov(page), span=span))

    def result(self, anchor: list, doc_type) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": anchor, "doc_type_final": doc_type}
