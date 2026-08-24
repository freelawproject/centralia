"""Court of Appeals of Iowa ('iowactapp').

THE CONTRACT — one paper, printed 30 times out of 30: the TYPED-FENCE LADDER.

The Iowa appellate courts share a publisher, and the sibling reader
(`iowa.py`, the Supreme Court's `ruled cover`) reads the same seven sections
in the same order. The difference is the fence: the Supreme Court DRAWS its
rules in two invariant measures, and the Court of Appeals TYPES them, as a
row of underscores centred on the page axis. So the measure that names a
section upstairs is replaced here by the section's ORDER between typed
fences, and every one of the seven bands still carries its own landmark.

    IN THE COURT OF APPEALS OF IOWA        the masthead: 18pt bold over a
    _______________                        14pt body, then FENCE 1…
    No. 25-1351                            …the number this court gave it…
    Filed May 13, 2026                     …and the day it came out
    _______________                        FENCE 2
    Auston David Herman,                   the caption: a party, BOLD…
    Plaintiff–Appellee,                    …its status, roman…
    v.                                     …the pivot, roman…
    Holly Noel Morrison,                   …the other side, BOLD…
    Defendant–Appellant.                   …and its status
    _______________                        FENCE 3
    Appeal from the Iowa District Court    the origin, by a closed leader
        for Keokuk County,                 vocabulary…
    The Honorable Crystal S. Cronk, Judge. …and who tried it
    _______________                        FENCE 4
    AFFIRMED                               the judgment, set BOLD and CAPS
    _______________                        FENCE 5
    Diana L. Miller of Whitfield & Eddy    the appearances
        P.L.C., … attorneys for appellant.
    _______________                        FENCE 6
    Considered without oral argument       how it was submitted…
    by Tabor, C.J., and Chicchelly and     …who sat…
        Sandy, JJ.
    Opinion by Sandy, J.                   …and who the court says wrote it
                                           (the writing signs itself on p. 2)

THE FENCE COUNT IS INVARIANT: exactly six typed underscore rows on page 1 of
all 30 records, 125.9–127.0pt wide, set at the body size, centred on the page
axis. No record draws a single h_rule or v_rule anywhere on page 1, and pdfio
assigns no column to any row. The reader that claims the block inherits the
job of drawing its fences, so each underscore row is consumed and re-emitted
as ``m.Rule(typed=True)`` where the page types it.

**THERE IS NO SECOND COLUMN, SO NO CaptionBlock IS EMITTED.** Measured over
the corpus: all 761 content rows on the 30 page 1s centre on the page axis to
within 1.5pt — the widest miss is 1.48pt, on a row reading 'attorney for
appellant.' — and the pivot `v.` stands alone on its own centred row rather
than beside anything. A caption rail is a thing a court DRAWS; this court
draws none, and inventing a column the page does not draw is worse than a
flat read. Same call va.py makes for its nine convening orders and
ohioctapp.py for its three centred-ladder districts. Every row therefore
emits centred, and the caption is a stack, not a grid.

THE CAPTION'S OWN GRAMMAR IS TYPOGRAPHIC, and it reads no name:

  - a PARTY NAME is set BOLD, and a name too long for the measure wraps in
    bold. Over the corpus every party-name row is bold and every status,
    pivot and group label is roman, without exception.
  - A BOLD ROW CONTINUES THE BOLD ROW ABOVE IT WHEN IT IS WITHIN ONE
    LEADING-STEP OF IT. The bold-to-bold steps inside the caption band come
    in two clusters and nothing between: wraps at 18.0pt (12) and 21.0pt (2),
    new elements at 25.4pt (6), 26.6, 26.7 and 36.0pt. `_ELEMENT_STEP`
    (23.0pt) separates them with 2pt of clearance on each side. Without it
    'In re the Marriage of Jessica M. Kirkpatrick and Kristopher K.' /
    'Kirkpatrick' reads as two parties, and 'In the Interest of F.M., Minor
    Child,' / 'T.M., Mother,' reads as one.
  - a ROMAN row is a STATUS when every word of it is in the closed status
    vocabulary, the PIVOT when it reads `v.`, and CAPTION APPARATUS
    otherwise — which is what 'Upon the Petition of' (4) and 'And Concerning'
    (4) are. Nothing roman is ever a party.

THE PIVOT DECIDES WHAT THE FIRST ELEMENT IS, structurally and with no
wording read at all. 17 records print `v.` and 13 do not. Where the band
prints a pivot, its first bold element is a PARTY and the case name is built
from the party names either side. Where it prints none, the band's first bold
element is the case's own TITLE ('In the Interest of F.M., Minor Child', 'In
re the Detention of Joseph Matthew Smith', 'In re the Marriage of Brooke Duke
and Katelyn Dawson') and that title IS the case name; `And Concerning` is a
group label in that form, not a pivot. An in-rem caption names one matter, so
`parties` carries the matter alone and the appealing party stays auditable in
`criteria.caption`, which keeps every caption row verbatim.

THE PANEL BAND SAYS THREE THINGS and each is read by its own landmark, never
by its ordinal: a row opening `Opinion by` / `Dissent by` is what the court
ANNOUNCES about authorship (role `author`); a row opening `by` is the roster;
anything else in the band is the submission statement ('Considered without
oral argument', 25; 'Heard at oral argument', 5), which goes to
`criteria.submitted`. A JUDGE WHO TAKES NO PART IS NOT ON THE PANEL, and the
clause stands on either of the last two rows ('by Greer, P.J., Schumacher,
J., and Doyle, S.J. Sandy, J., takes no part.'; 'Opinion by Chicchelly, J.
Bower, S.J., takes no part.'), so it is cut out of the text the roster
grammar sees while the printed row is kept whole.

THE READER CLAIMS PAGE 1 AND NOTHING ELSE. Every writing in the corpus signs
itself at the body rail on page 2 ('SANDY, Judge.'), so the announced author
is a headmatter fact and not a byline; it is handed to core as
`announced_author`, which core applies ONLY to a lead writing that carries no
byline of its own — a safety net that never fires over this corpus and would
be right if it did. Its row ids are handed over as `anchor_ids` too: core
lifted 'Opinion by Greer, P.J.' out of huntley's headmatter and used it as
the majority's anchor heading, and if a total claim ever leaves a document
with no writing, that row is the one to give back.

WHERE EACH BAND LANDS IN `Criteria`, with the printed form kept beside the
parsed one wherever the two differ:

    band 0  court
    band 1  docket_number (+ other_dockets), decision_date
    band 2  caption (rows, verbatim), case_name, parties
    band 3  lower_court, lower_court_judge — and `history`, which is the
            band as PRINTED, because `lower_court` is only the tribunal
            once the route leader has been stripped off it
    band 4  disposition, as printed and in caps
    band 5  attorneys
    band 6  submitted (the submission statement), judges (the roster as
            printed, its recusal clause included), panel (the names, that
            clause excluded), panel_line (the whole band as printed)

A record that does not type six fences on page 1, or whose first row is not
the masthead, or whose first fenced band does not state a docket, is not this
paper and gets NOTHING — core's shared walk already places these rows
centred and draws the typed fences, so the fallback is a good one.

iowactapp's profile stays in the shared table in `courts/__init__.py`; this
file owns the reader only.

CORE DEFECTS MET, NOT PATCHED (see `notes/core-patch-queue.md`):
  * item 41 — `criteria.attorneys` is unreachable for a reader that keeps
    counsel inside the headmatter. Closed here the way connappct closed it,
    by setting the key in the reader's own criteria dict.
  * item 34 (`triage`'s document-wide CID test) does not manifest: every
    page of all 30 records reports `cid_chars == 0`.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE_LADDER = "typed-fence ladder"

# ---- iowactapp's declared facts (measured over all 30 records) -----------
# THE TYPED FENCE. Six per page 1, every one of them; 125.9-127.0pt wide,
# set at the body size, centred on the page axis to 0.3pt.
_FENCE = re.compile(r"^_{5,}$")
_FENCES_EXPECTED = 6
_FENCE_MEASURE = (118.0, 134.0)
_AXIS_TOL = 6.0
# THE MASTHEAD: 18.0pt bold over a 13.8-14.0pt body — the only row on the
# cover set above body size, on all 30 records.
_MASTHEAD_SIZE = 16.0
# THE CAPTION'S LEADING-STEP. Bold-to-bold steps inside the caption band are
# 18.0/21.0 for a WRAP and 25.4/26.6/26.7/36.0 for a NEW element; half-way
# between the clusters, with 2pt of clearance either side.
_ELEMENT_STEP = 23.0
# HOW FAR THE COVER RUNS. Page 1, always: the sixth fence is followed by the
# panel band and the folio, and page 2 opens with the writing's own byline.
_MAX_PAGES = 1

# 'No. 25-1351' — this court's own number. Written for the consolidated form
# the corpus does not yet print ('Nos. 25-1351 and 25-1352'), so a second
# docket lands in `other_dockets` rather than being silently joined into the
# first. The shape is required, not just the label: a fenced band holds
# nothing else, and a loose match here would swallow a lower court's number.
_ONE_DOCKET = r"\d{2}\s*[-‐–—]\s*\d{3,4}[A-Z]?"
_DOCKET = re.compile(
    rf"^Nos?\.\s*({_ONE_DOCKET}"
    rf"(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+){_ONE_DOCKET})*)\.?$", re.I)
_SPLIT_DOCKETS = re.compile(r"\s*(?:,\s*and\s+|,\s*|\s+and\s+)\s*")
# 'Filed May 13, 2026' — the only date the cover states.
_FILED = re.compile(r"^Filed\s+(.+?)\.?$", re.I)

# THE ORIGIN LEADERS: a closed vocabulary of the ways this court states where
# a case came from, anchored at the paragraph's start. Never a court NAME —
# 'Appeal from the Iowa District Court for Polk County' and 'Certiorari from
# the Iowa District Court for Black Hawk County' are the same leader.
_ORIGIN_LEADERS = (
    "appeal from", "appeals from", "on appeal from",
    "appeal and cross-appeal from", "cross-appeal from",
    "certiorari from", "on certiorari to", "certiorari to",
    "on writ of certiorari to", "writ of certiorari to",
    "review from", "on review from", "on further review from",
    "certified question from", "certified questions from",
    "petition for review from", "judicial review from",
    "on judicial review from",
)
# 'The Honorable Crystal S. Cronk, Judge.' / '…, Judges.' — 30 of 30. The
# court's OWN separator is the comma and the last group is the bench ROLE;
# what stands between the honorific and the role is the judge.
_JUDGE_ROW = re.compile(
    r"^The\s+Honorable\s+(.+?)\s*,\s*"
    r"(?:chief\s+)?(?:district\s+)?(?:associate\s+)?(?:senior\s+)?"
    r"(?:retired\s+)?judges?\s*\.?$", re.I)

# THE PANEL BAND'S THREE LANDMARKS.
_ANNOUNCE = re.compile(
    r"\b(?:opinion|dissent|concurrence|special\s+concurrence)\s+by\s+", re.I)
_ROSTER_ROW = re.compile(r"^by\s+", re.I)
# 'Sandy, J., takes no part.' — a judge who takes no part is not on the
# panel, and the clause rides on either of the band's last two rows.
_NO_PART = re.compile(
    r"\b([A-Z][A-Za-z’'\-]+)\s*,\s*"
    r"(?:C\.J\.|P\.J\.|S\.J\.|JJ\.|J\.)\s*,\s*takes\s+no\s+part\s*\.?", re.I)
# THE BENCH ABBREVIATIONS this court sets, and the roster grammar that reads
# them: one or more surnames, then the abbreviation that names their office.
# Read as prose the same row yields a judge called 'and' and one called 'by'.
_OFFICE = r"C\.J\.|P\.J\.|S\.J\.|JJ\.|J\."
_NAME = r"[A-Z][A-Za-z’'\-]+"
_ROSTER = re.compile(
    rf"({_NAME}"
    rf"(?:\s*,\s*(?:and\s+)?{_NAME})*"
    rf"(?:\s+and\s+{_NAME})?)"
    rf"\s*,\s*(?:{_OFFICE})")
_AUTHORED = re.compile(
    rf"\b(opinion|dissent|concurrence)\s+by\s+({_NAME})\s*,\s*({_OFFICE})",
    re.I)

# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. This court stacks its roles with an en dash ('Third-Party-Plaintiff
# Appellant', 'Intervenor–Appellee') and, on one record, an ASCII hyphen.
_STATUS_WORDS = frozenset((
    "appellant", "appellants", "appellee", "appellees", "applicant",
    "applicants", "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants", "intervenor",
    "intervenors", "movant", "movants", "amicus", "amici", "curiae",
    "claimant", "claimants", "guardian", "conservator", "trustee",
    # the ways this court STACKS a role, and nothing else — a vocabulary
    # that admits 'state' or 'of' to make a row parse has stopped being a
    # ROLE vocabulary and started being a bag of words.
    "cross", "third", "party", "co", "counter", "and",
))
# The publisher sets ligatures as single glyphs ('Plaintiﬀ,', 'Law Oﬃce'),
# so a vocabulary lookup has to see the letters the page means.
_LIGATURES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
    "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st",
}


def _norm(text: str) -> str:
    return " ".join(text.split())


def _delig(text: str) -> str:
    for lig, plain in _LIGATURES.items():
        text = text.replace(lig, plain)
    return text


# --------------------------------------------------------------------------
# the visual row — pdfio splits a justified row at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold",
                 "all_bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = any(bool(p.bold) for p in self.pieces)
        self.all_bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def flat(self) -> str:
        return _delig(self.text)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + " " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order.

    The folio is the only furniture this cover carries and core's finder sees
    it on all 30 records; it is left in the stream unclaimed so core records
    it as the `Dropped` it is."""
    rows: list = []
    for pm in model.pages[:max_pages]:
        buckets: dict = {}
        order: list = []
        loose: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            if line.row is not None:
                if line.row not in buckets:
                    buckets[line.row] = []
                    order.append(line.row)
                buckets[line.row].append(line)
            else:
                loose.append(line)
        groups = [buckets[k] for k in order]
        # pdfio leaves `row` unset on pages it did not have to split; fall
        # back to a baseline test, which is what `row` encodes anyway.
        for line in loose:
            for g in groups:
                if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                    g.append(line)
                    break
            else:
                groups.append([line])
        rows.extend(_Row(g) for g in groups)
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


def _is_fence(row: _Row, page_width: float) -> bool:
    """A TYPED RULE IS STRUCTURE: a run of underscores in the invariant
    measure, centred on the page axis."""
    if not _FENCE.match(row.text):
        return False
    if not (_FENCE_MEASURE[0] <= row.x1 - row.x0 <= _FENCE_MEASURE[1]):
        return False
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _is_status(text: str) -> bool:
    bare = _norm(_delig(text)).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w for w in re.split(r"[\s/,\-‐–—]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _caption_elements(rows: list) -> list:
    """The caption band, read as ELEMENTS.

    Returns ``(kind, text, rows)`` in the page's order, where kind is
    ``name`` (a bold run, wraps merged), ``status``, ``pivot`` or
    ``apparatus``. Nothing roman is ever a name and no name is ever read by
    wording; a wrap is decided by the leading-step alone."""
    out: list = []
    for row in rows:
        if row.bold:
            if (out and out[-1][0] == "name"
                    and row.top - out[-1][2][-1].top < _ELEMENT_STEP):
                out[-1][2].append(row)          # a wrap of the name above
                continue
            out.append(["name", "", [row]])
            continue
        if _is_pivot(row.text):
            out.append(["pivot", row.text, [row]])
        elif _is_status(row.text):
            out.append(["status", row.text, [row]])
        else:
            out.append(["apparatus", row.text, [row]])
    for el in out:
        if el[0] == "name":
            el[1] = _norm(" ".join(r.text for r in el[2])).rstrip(",; ")
    return [(k, t, rs) for k, t, rs in out]


def _read_caption(ctx, rows: list) -> None:
    """The case's name and its parties, from the caption's own structure."""
    els = _caption_elements(rows)
    names = [t for k, t, _ in els if k == "name" and t]
    pivot_at = next((i for i, (k, _, _) in enumerate(els)
                     if k == "pivot"), None)
    if pivot_at is not None:
        left = [t for k, t, _ in els[:pivot_at] if k == "name" and t]
        # A SECOND PIVOT IS A CONSOLIDATION: the LEAD case only.
        rest = els[pivot_at + 1:]
        stop = next((i for i, (k, _, _) in enumerate(rest)
                     if k == "pivot"), len(rest))
        right = [t for k, t, _ in rest[:stop] if k == "name" and t]
        if left and right:
            one = _norm(" ".join(left)).rstrip(",; ")
            two = _norm(" ".join(right)).rstrip(",; ")
            ctx.crit["parties"] = [one, two]
            ctx.crit["case_name"] = f"{one} v. {two}"
            return
    # NO PIVOT, SO THE FIRST ELEMENT IS THE CASE'S OWN TITLE. An in-rem
    # caption names one matter; the party who appeals stays auditable in
    # `criteria.caption`, which keeps every row verbatim.
    if names:
        ctx.crit["parties"] = [names[0]]
        ctx.crit["case_name"] = names[0]


def _origin_leader(text: str) -> str | None:
    low = _norm(_delig(text)).lower()
    for lead in _ORIGIN_LEADERS:
        if low.startswith(lead):
            return lead
    return None


def _read_origin(ctx, text: str) -> None:
    """'Appeal from the Iowa District Court for Keokuk County,' — the leader
    is stripped and the tribunal recorded. The leader is not thrown away: an
    appeal and a certiorari petition are not the same route, and the band is
    kept whole in `history` beside the parsed tribunal."""
    lead = _origin_leader(text)
    flat = _norm(_delig(text)).rstrip(",. ")
    if lead:
        flat = flat[len(lead):].strip()
    flat = re.sub(r"^the\s+", "", flat, flags=re.I).strip().rstrip(",. ")
    if flat:
        prev = ctx.crit.get("lower_court")
        ctx.crit["lower_court"] = f"{prev}; {flat}" if prev else flat


def _roster(text: str) -> list:
    """The bench the roster row names, in the order it names them."""
    out: list = []
    for names in _ROSTER.findall(text):
        for name in re.split(r"\s*,\s*|\s+and\s+", names):
            # 'Chicchelly and Sandy' — the comma split runs first and can
            # leave the conjunction glued to the last name.
            name = re.sub(r"^and\s+", "", name.strip().strip(","))
            if name and name not in out:
                out.append(name)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self) -> None:
        self.items: list = []
        self.consumed: set = set()
        self.crit: dict = {}
        self.anchor_ids: list = []
        self.announced: str | None = None

    def emit(self, row: _Row, role: str) -> None:
        # EVERY ROW ON THIS COVER IS CENTRED ON THE PAGE AXIS — measured,
        # 761 of 761, worst miss 1.48pt. So none of them carries a `rel`.
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align("C"), x0=row.x0, size=row.size,
            bold=row.all_bold, rel=0.0, role=role))
        self.consumed.update(row.ids)

    def fence(self, row: _Row) -> None:
        """A reader that claims the block inherits the job of drawing its
        fences. The court TYPED this rule; it is re-emitted where the page
        types it rather than dropped or left standing as text."""
        self.items.append(m.Rule(
            prov=m.Prov(row.page, row.ids), span="full", typed=True))
        self.consumed.update(row.ids)

    def result(self) -> dict:
        out = {"criteria": self.crit, "items": self.items, "attorneys": [],
               "dropped": [], "consumed": self.consumed,
               "anchor_ids": self.anchor_ids, "doc_type_final": None}
        if self.announced:
            out["announced_author"] = self.announced
        return out


@decider("headmatter.read", court="iowactapp")
def read_headmatter_iowactapp(model, geom, **_):
    """Read the Court of Appeals' typed-fence ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 94.0
    body_size = geom.body_size if geom else 14.0

    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if len(rows) < 8:
        return NOTHING

    # ---- THE DISPATCH: six typed fences, and a masthead above the first ---
    fences = [i for i, r in enumerate(rows) if _is_fence(r, page1.width)]
    if len(fences) != _FENCES_EXPECTED:
        return NOTHING
    if fences[0] != 1:
        return NOTHING                       # the masthead is the only row
    head = rows[0]                           # standing above fence 1
    if not (head.size >= _MASTHEAD_SIZE and head.bold):
        return NOTHING

    bands: list = []
    prev = 0
    for i in fences:
        bands.append(rows[prev:i])
        prev = i + 1
    bands.append(rows[prev:])

    # THE FIRST FENCED BAND STATES THE DOCKET, or this is not the paper. It
    # is the one identifier the ladder cannot be read without, and it is
    # populated HERE — before anything gates on it.
    dockets: list = []
    filed: str | None = None
    for row in bands[1]:
        mm = _DOCKET.match(row.flat)
        if mm:
            dockets.extend(_norm(d) for d in
                           _SPLIT_DOCKETS.split(mm.group(1)) if d.strip())
            continue
        if _FILED.match(row.flat):
            filed = _norm(_FILED.match(row.flat).group(1))
    if not dockets:
        return NOTHING

    ctx = _Ctx()
    ctx.crit["headmatter_style"] = STYLE_LADDER
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if filed:
        ctx.crit["decision_date"] = filed

    # ---- band 0: the masthead -------------------------------------------
    for row in bands[0]:
        ctx.crit.setdefault("court", row.text)
        ctx.emit(row, "court")
    ctx.fence(rows[fences[0]])

    # ---- band 1: the identifiers ----------------------------------------
    for row in bands[1]:
        ctx.emit(row, "docket" if _DOCKET.match(row.flat) else "date")
    ctx.fence(rows[fences[1]])

    # ---- band 2: the caption --------------------------------------------
    caption = bands[2]
    if not caption:
        return NOTHING
    ctx.crit["caption"] = [r.text for r in caption]
    _read_caption(ctx, caption)
    for row in caption:
        ctx.emit(row, "caption")
    ctx.fence(rows[fences[2]])

    # ---- band 3: where the case came from --------------------------------
    origin = bands[3]
    if not origin or not _origin_leader(origin[0].text):
        return NOTHING            # the band is named by its leader, or not
    for row in origin:
        if _origin_leader(row.text):
            _read_origin(ctx, row.text)
        else:
            jm = _JUDGE_ROW.match(row.flat)
            if jm and not ctx.crit.get("lower_court_judge"):
                ctx.crit["lower_court_judge"] = _norm(jm.group(1))
        ctx.emit(row, "lower-court")
    # KEEP THE PRINTED FORM BESIDE THE PARSED FORM: the band states the
    # route as well as the tribunal, and `lower_court` carries only the
    # tribunal once the leader is stripped off it.
    ctx.crit["history"] = _norm(" ".join(_delig(r.text) for r in origin))
    ctx.fence(rows[fences[3]])

    # ---- band 4: what the court DID --------------------------------------
    for row in bands[4]:
        if row.all_bold and not ctx.crit.get("disposition"):
            ctx.crit["disposition"] = _norm(_delig(row.text)).rstrip(".")
        ctx.emit(row, "disposition")
    ctx.fence(rows[fences[4]])

    # ---- band 5: the appearances -----------------------------------------
    # THE HEADMATTER RENDERS WHOLE: counsel printed inside the block stays
    # inside it, and its text is copied into `criteria.attorneys` — which
    # core cannot do for a reader that obeys the invariant (queue item 41).
    counsel = bands[5]
    for row in counsel:
        ctx.emit(row, "counsel")
    if counsel:
        ctx.crit["attorneys"] = _norm(
            " ".join(_delig(r.text) for r in counsel))[:2000]
    ctx.fence(rows[fences[5]])

    # ---- band 6: how it was submitted, who sat, who wrote ----------------
    printed: list = []
    for row in bands[6]:
        flat = _norm(_delig(row.text))
        printed.append(flat)
        if _ANNOUNCE.search(flat):
            by = _AUTHORED.search(flat)
            if by and ctx.announced is None:
                # NOT a byline. Every writing in the corpus signs itself at
                # the body rail on page 2, so this is what the court
                # ANNOUNCES, handed to core on its own channel: core signs
                # the lead writing from it only where the document prints no
                # byline of its own, which always outranks an announcement.
                ctx.announced = f"{_norm(by.group(2))}, {by.group(3)}"
            ctx.anchor_ids.extend(row.ids)
            ctx.emit(row, "author")
            continue
        if _ROSTER_ROW.match(flat):
            # THE ROSTER AS PRINTED. `judges` is the field the criteria box
            # shows, and the field alaska/bap1 fill with the same thing. The
            # leading `by` is the submission sentence's connective, not part
            # of the roster, and the row's own period stays on it.
            ctx.crit.setdefault(
                "judges", _ROSTER_ROW.sub("", flat, count=1).strip())
            ctx.emit(row, "panel")
            continue
        ctx.crit.setdefault("submitted", flat.rstrip("."))
        ctx.emit(row, "panel")
    if printed:
        # KEEP THE PRINTED FORM BESIDE THE PARSED FORM. `panel_line` is the
        # band as the page sets it, recusal clause included; only the text
        # the roster GRAMMAR sees has the clause cut out of it, because a
        # judge who takes no part is not on the panel.
        line = _norm(" ".join(printed))
        ctx.crit["panel_line"] = line
        names = _roster(_NO_PART.sub(" ", line))
        if names:
            ctx.crit["panel"] = names

    return ctx.result()
