"""Supreme Court of North Carolina ('nc').

Everything unique to nc lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'filed slip', printed 50 times out of 50.

North Carolina draws nothing, fences nothing, and sets its whole front
matter in ONE type size (12pt on a 612x792 page, 72pt body rail). There is
no masthead in display type, no rule pair, no box. What the court does
instead is set each band of the block on its OWN horizontal position, and
that indent ladder is the entire parser:

    ┌ 306.0 — the PAGE AXIS ─────────────────────────────────────────────┐
    │ IN THE SUPREME COURT OF NORTH CAROLINA   the masthead (156.9-455.1)│
    │ No. 103PA24                              the docket                │
    │ Filed 12 December 2025                   the release date          │
    └────────────────────────────────────────────────────────────────────┘
      STATE OF NORTH CAROLINA          77.1 — the CAPTION RAIL, and its
              v.                      149.1 — the pivot, standing alone
      GEORGE LEE ALLISON               77.1
        On discretionary review pursuant to N.C.G.S. § 7A-31 of a …
      unpublished decision of the Court of Appeals, No. COA23-635 …
      … Heard in the Supreme Court on 22 April 2025.
                    108.0 opens it, 72.0 carries it — THE ORIGIN
        Jeff Jackson, Attorney General, by Michael T. Henry, Special …
        General, for the State-appellee.
                    108.0 opens it, 108.0 carries it — THE APPEARANCES
        BERGER, Justice.               108.0 — and the writing starts

FOUR POSITIONS, FOUR BANDS, and each one is named by where it sits, never
by where it comes in the block:

  * THE PAGE AXIS (|row centre - 306| <= 6pt) carries the three rows the
    court sets for itself: the masthead — the same engraving at the same
    measure, 156.9-455.1, on every one of the 50 records — the docket
    ('No. 103PA24' / 'Nos. 75A24-1 and 139A24-1'), and the release date
    ('Filed 12 December 2025', day first). Each is read by its own
    landmark, so a record that printed them in another order still reads.

  * THE CAPTION RAIL is the body rail plus 5.1pt (77.1). Nothing else in
    the document begins there — the caption is the only band nc indents by
    a fraction of an em — and a caption row that wraps wraps to the SAME
    rail. The pivot ('v.') stands alone, indented to 148.3-149.1, and a
    consolidated caption prints two or three of them.

  * THE PARAGRAPH INDENT (body rail + 36pt = 108.0) opens the two prose
    bands AND the byline, so the indent alone cannot name them. What names
    them is where the paragraph's own WRAPS go, and the type it is set in:

        the ORIGIN — how the appeal got here, what was decided below, who
        tried it, and when this Court heard it — is set ROMAN and
        DOUBLE-SPACED (28.8pt), and its runover returns to the BODY RAIL;

        the APPEARANCES are set ITALIC and SINGLE-SPACED (14.4pt), and
        their runover stays at the INDENT — a block indent, not a first-
        line one.

    The two tests are independent and they agree on all 50 records: a
    paragraph that LEAVES the indent is the origin; one that KEEPS it is
    counsel. Neither is read by wording, and neither depends on the origin
    coming first (it does, on all 50, but that is not what decides).

  * THE BYLINE also stands at 108.0 and ends the reader. Every record in
    the corpus has one ('BERGER, Justice.' / 'NEWBY, Chief Justice.' /
    'PER CURIAM.'), so the reader is never unbounded.

THE DISPATCH is the top of page 1: three axis-centred rows — this court
naming itself, a 'No.'/'Nos.' docket, a 'Filed <d Month yyyy>' — and a
caption band at the caption rail under them. A record that does not print
all four is not this paper and gets NOTHING.

WHAT THE READER INHERITS. Where a long caption or a long counsel block
carries the block onto page 2 (8 records), that page opens with a two-row
running head — the short case name in caps over a 10pt 'Opinion of the
Court'. Core's repeat floor cannot see it on a two-page slip, so
'Opinion of the Court' rendered as a HEADING inside howard_v._maxisiq's
opinion. Any axis-centred row in the top band of a page after the first is
inside this reader's region, and it is dropped and RECORDED as a running
head. The footnote separator (a drawn 144pt rect at the body rail) cuts
the page: nothing below it is headmatter.

A DRAWN RULE INSIDE THE BLOCK IS RE-EMITTED. langley_v._autocraft_inc.
consolidates two appeals and separates their captions with a 460pt rect
across the measure; a total claim would otherwise silence it.

nc PRINTS NO headnote band, no syllabus, no panel roster and no
disposition in its headmatter: the judgment is the last line of the
writing, where the court puts it.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# nc signs its lead opinion NAME-FIRST ('BERGER, Justice.' / 'NEWBY, Chief
# Justice.' / 'PER CURIAM.') and every separate writing TITLE-FIRST
# ('Justice EARLS dissenting.' / 'Chief Justice NEWBY concurring in part and
# dissenting in part.'). Declared prose-only, the reversed form matched
# nothing and 22 of the 50 records came back with ONE writing where the
# court printed two to five — every concurrence and dissent in the corpus
# was swallowed by the majority it followed.
NC = register(CourtProfile(
    "nc", "Supreme Court of North Carolina",
    byline=BylineGrammar(style="prose", titles=("Justice", "Chief Justice"),
                         also_reversed=True,
                         rev_titles=("Chief Justice", "Justice")),
))

STYLE_SLIP = "filed slip"

# ---- nc's declared facts (measured over all 50 records) ------------------
# THE PAGE AXIS. The masthead, the docket and the release date are the only
# rows the court centres; measured, every one of them sits within 1.5pt of
# the axis, and no other headmatter row comes within 60pt of it.
_AXIS_TOL = 6.0
# THE CAPTION RAIL: body rail + 5.1pt. gvest sets two of its four caption
# blocks 0.8pt left of it, so the band is read with a point and a half of
# slack either way.
_CAPTION_RAIL = 5.1
_RAIL_TOL = 1.6
# THE PARAGRAPH INDENT: body rail + 36pt. It opens the origin, every
# counsel entry, and the byline.
_INDENT = 36.0
_INDENT_TOL = 1.5
# THE PIVOT stands between the two — 148.3-149.1 on a 72pt rail (rail +
# 76.3 to +77.1). Anything at the rail or the indent is read as its band.
_PIVOT_MIN = 40.0
_PIVOT_MAX = 100.0
# WRAP vs NEW ELEMENT. The court sets one leading at 14.4pt and the next
# element one full body line lower (28.8pt). 20pt separates them with 5.6pt
# of clearance on either side.
_WRAP_PITCH = 20.0
# THE FOOTNOTE SEPARATOR: a drawn rect 144.0pt wide, at the body rail.
# Nothing below it on that page is headmatter.
_SEP_MEASURE = (138.0, 150.0)
_SEP_RAIL = 3.0
# THE CONSOLIDATION DIVIDER (langley): a rect across the measure, 460.1pt,
# between two consolidated captions. Told from the footnote separator by
# its width, and from an underline by neither ending on a row.
_DIVIDER_MIN = 300.0
# THE RUNNING HEAD occupies the top band of every page after the first.
_HEAD_BAND = 0.13
# HOW FAR THE BLOCK MAY RUN. hoke's 15-party caption carries its counsel
# and its byline to page 2; nothing in the corpus needs a third.
_MAX_PAGES = 3

# 'IN THE SUPREME COURT OF NORTH CAROLINA' — this court's own engraving,
# set at the same measure on all 50. The row is matched on the court it
# names, never on a party or a case.
_MASTHEAD = "in the supreme court of north carolina"
# 'No. 103PA24' / 'Nos. 75A24-1 and 139A24-1' — the docket band. nc numbers
# an appeal <seq><letters><yy>[-<n>]: 103PA24, 96A01-3, 142A12, 32PA23-2.
_DOCKET_ROW = re.compile(r"^Nos?\.\s+\S")
_DOCKET = re.compile(r"\b\d{1,3}[A-Z]{1,3}\d{2}(?:-\d{1,2})?\b")
# 'Filed 12 December 2025' — nc labels its release date and sets the day
# first. The month is a closed vocabulary; nothing else is read out of it.
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_FILED = re.compile(r"^Filed\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\.?$")
# The pivot, and the caption's own connective — a caption row that is only
# 'and' joins two parties on the same side (hoke prints four of them).
_PIVOT = re.compile(r"^v(?:s)?\.?$", re.I)
_CONNECTIVE = re.compile(r"^and$", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. nc sets the status lower-case at the END of the party it
# belongs to ('…, plaintiff-intervenor', '…, realigned defendant') or on a
# row of its own where the party ran to the measure.
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "appellant",
    "appellants", "appellee", "appellees", "petitioner", "petitioners",
    "respondent", "respondents", "intervenor", "intervenors", "movant",
    "amicus", "amici", "curiae", "realigned", "counterclaim", "substitute",
    "trustee", "third-party", "cross", "and", "et", "al", "a", "minor",
    "guardian", "ad", "litem", "the", "of", "heirs",
)
# 'No. COA23-635' — the number the COURT OF APPEALS gave the case, and the
# only lower-court number nc prints in a fixed form.
_COA_DOCKET = re.compile(r"\bCOA\s?\d{2}-\d{3,4}\b")
# WHO TRIED IT. 'Judge' is a bench title, not a name; the name is the run of
# capitalised tokens after it ('Judge Jacqueline D. Grant in Superior
# Court', 'Judge Adam M. Conrad, Special Superior Court Judge for Complex
# Business Cases').
_TRIAL_JUDGE = re.compile(
    r"\bby\s+(?:Chief\s+)?(?:Business\s+Court\s+)?Judge\s+"
    r"((?:[A-Z][A-Za-z.'’\-]*(?:\s+(?:Jr\.|Sr\.|III|II|IV))?)"
    r"(?:\s+[A-Z][A-Za-z.'’\-]*){0,4})")
# THE TRIBUNAL BELOW, in the two forms nc's own court system prints. A
# closed vocabulary of this state's trial divisions — never a court read
# out of open wording.
_TRIAL_COURT = re.compile(
    r"\b(Superior|District)\s+Court,\s+([A-Z][A-Za-z.\-]*(?:\s+[A-Z][A-Za-z.\-]*)?)"
    r"\s+County\b")
_COURT_OF_APPEALS = "court of appeals"
_COA_NAME = "North Carolina Court of Appeals"
# 'Heard in the Supreme Court on 22 April 2025.' — the argument date, and
# 'calendared … but determined on the record and briefs without oral
# argument' — the submission. Both are statements this Court makes about
# its own sitting, in the one form it prints them.
_HEARD = re.compile(r"Heard in the Supreme Court on\s+"
                    r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})")
_CALENDARED = re.compile(r"calendared for argument in the Supreme Court on\s+"
                         r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})")
_NO_ARGUMENT = "without oral argument"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_masthead(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD


def _filed_value(text: str) -> str | None:
    """'Filed 12 December 2025' -> 'December 12, 2025', or None."""
    mm = _FILED.match(_norm(text))
    if mm is None or mm.group(2).lower() not in _MONTHS:
        return None
    return f"{mm.group(2)} {int(mm.group(1))}, {mm.group(3)}"


def _dockets(text: str) -> list[str]:
    return _DOCKET.findall(_norm(text))


def _is_status(text: str) -> bool:
    bare = _norm(text).strip(".,;: ").lower()
    words = [w for w in re.split(r"[\s/,-]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


def _strip_status(text: str) -> str:
    """Drop the trailing status clause from a party statement. The status is
    the tail of lower-case role words after the last comma."""
    out = _norm(text).rstrip(" ,;.")
    while "," in out:
        head, _, tail = out.rpartition(",")
        if not _is_status(tail):
            break
        out = head.rstrip(" ,;.")
    return out


# --------------------------------------------------------------------------
# the page's own marks
# --------------------------------------------------------------------------

def _footnote_cut(pm, body_x0: float) -> float:
    """Where this page's footnotes begin — the top of the 144pt separator nc
    draws at the body rail."""
    tops = [r.top for r in pm.h_rules
            if _SEP_MEASURE[0] <= r.width <= _SEP_MEASURE[1]
            and abs(r.x0 - body_x0) <= _SEP_RAIL]
    return min(tops) if tops else float("inf")


def _dividers(pm, cut: float) -> list[float]:
    """The consolidation dividers this page draws above its footnote cut."""
    return sorted(r.top for r in pm.h_rules
                  if r.width >= _DIVIDER_MIN and r.top < cut)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="nc")
def read_headmatter_nc(model, geom, **_):
    """Read North Carolina's filed slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    page1 = model.pages[0]
    # THE ROWS, in page order, with same-row pieces rejoined. hoke's counsel
    # entry is justified wide enough that pdfio splits it at its own gap
    # ('plaintiff-intervenor/realigned-defendant-appellee' | 'Charlotte-
    # Mecklenburg'), and half a row is not a band.
    rows: list[tuple] = []
    marks: list[tuple] = []
    for pm in model.pages[:_MAX_PAGES]:
        cut = _footnote_cut(pm, 72.0)
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or line.top >= cut:
                continue
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        for key in order:
            rows.append((pm, groups[key]))
        for top in _dividers(pm, cut):
            marks.append((pm.number, top))
    if len(rows) < 6:
        return NOTHING

    # THE LADDER IS READ OFF THE PAGE, not off `geom`. Four of the fifty
    # records are two pages or one, and on those the document's dominant
    # left edge is the PARAGRAPH INDENT (hill, howard, shively, in_re_b.m.t.
    # all measure body_x0=108.0) or the CAPTION RAIL (in_re_godfrey, 77.0);
    # state_v._reel yields no geometry at all. Trusting it left those five
    # records unread. The rail is instead the leftmost left edge on page 1
    # that carries BOTH of the ladder's other rungs above it.
    lefts = sorted({round(g[0].x0, 1) for pm, g in rows
                    if pm.number == 1 and g[0].x0 < pm.width / 2})
    if not lefts:
        return NOTHING
    body_x0 = None
    for cand in (lefts[0], round(lefts[0] - _CAPTION_RAIL, 1)):
        if any(abs(x - (cand + _CAPTION_RAIL)) <= _RAIL_TOL for x in lefts) \
                and any(abs(x - (cand + _INDENT)) <= _INDENT_TOL
                        for x in lefts):
            body_x0 = cand
            break
    if body_x0 is None:
        return NOTHING
    rail = body_x0 + _CAPTION_RAIL
    indent = body_x0 + _INDENT
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE DISPATCH: three axis-centred rows at the head of page 1 — the
    # court naming itself, its docket, its release date — over a caption
    # band at the caption rail.

    def centred(group) -> bool:
        mid = (group[0].x0 + max(l.x1 for l in group)) / 2
        return abs(mid - page1.width / 2) <= _AXIS_TOL

    head = [g for pm, g in rows if pm.number == 1][:3]
    if len(head) < 3:
        return NOTHING
    texts = [_norm(" ".join(l.plain for l in g)) for g in head]
    if not (_is_masthead(texts[0]) and centred(head[0])
            and _DOCKET_ROW.match(texts[1]) and centred(head[1])
            and _filed_value(texts[2]) and centred(head[2])):
        return NOTHING
    if not any(abs(g[0].x0 - rail) <= _RAIL_TOL
               for pm, g in rows if pm.number == 1):
        return NOTHING

    ctx = _Ctx(model, geom, body_size, rail)
    parser = BylineParser(NC.byline)
    band = "axis"          # axis | caption | origin | counsel
    caption: list[str] = []
    origin: list[str] = []
    counsel: list[str] = []
    dockets: list[str] = []
    pending: list = []     # the rows of the element being assembled
    pending_role = ""
    prev_page = prev_top = None
    stopped = False

    def flush():
        nonlocal pending, pending_role
        if pending:
            ctx.emit(pending, pending_role)
            text = _norm(" ".join(_norm(" ".join(l.plain for l in g))
                                  for g in pending))
            if pending_role == "caption":
                caption.append(text)
            elif pending_role == "lower-court":
                origin.append(text)
            elif pending_role == "counsel":
                counsel.append(text)
        pending, pending_role = [], ""

    def open_element(group, role):
        nonlocal pending, pending_role
        flush()
        pending, pending_role = [group], role

    for pm, group in rows:
        # A DRAWN DIVIDER RENDERS WHERE THE PAGE DRAWS IT.
        while marks and (marks[0][0] < pm.number
                         or (marks[0][0] == pm.number
                             and marks[0][1] < group[0].top)):
            flush()
            ctx.rule(marks.pop(0)[0])
        text = _norm(" ".join(l.plain for l in
                              sorted(group, key=lambda l: l.x0)))
        x0 = group[0].x0
        top = group[0].top

        # THE RUNNING HEAD is the top band of any page after the first. It
        # is furniture wherever core's repeat floor happens to see it.
        if pm.number > 1 and top <= pm.height * _HEAD_BAND:
            flush()
            ctx.drop(group, "running-head")
            continue
        if finder.kind(pm, group[0]):
            flush()
            ctx.drop(group, finder.kind(pm, group[0]))
            continue

        wrap = (prev_page == pm.number and prev_top is not None
                and (top - prev_top) <= _WRAP_PITCH)
        prev_page, prev_top = pm.number, top

        if band == "axis":
            if _is_masthead(text):
                ctx.crit.setdefault("court", text)
                ctx.emit([group], "court")
                continue
            if _DOCKET_ROW.match(text):
                dockets.extend(_dockets(text))
                ctx.emit([group], "docket")
                continue
            value = _filed_value(text)
            if value is not None:
                ctx.crit.setdefault("decision_date", value)
                ctx.emit([group], "date")
                continue
            band = "caption"

        # THE BYLINE ENDS THE READER, wherever it stands.
        if abs(x0 - indent) <= _INDENT_TOL and parser.parse(text) is not None:
            stopped = True
            break

        if abs(x0 - rail) <= _RAIL_TOL:
            band = "caption"
            if wrap and pending_role == "caption":
                pending.append(group)
            else:
                open_element(group, "caption")
            continue
        if (_PIVOT.match(text) or _CONNECTIVE.match(text)) and \
                _PIVOT_MIN <= (x0 - body_x0) <= _PIVOT_MAX:
            band = "caption"
            open_element(group, "caption")
            continue
        if abs(x0 - indent) <= _INDENT_TOL:
            # THE INDENT OPENS BOTH PROSE BANDS; the TYPE says which. Roman
            # is the origin, italic the appearances — and the wraps say the
            # same thing from the other side (see the module docstring).
            italic = all(l.all_emphasized for l in group)
            if italic:
                band = "counsel"
                if wrap and pending_role == "counsel":
                    pending.append(group)
                else:
                    open_element(group, "counsel")
            else:
                band = "origin"
                open_element(group, "lower-court")
            continue
        if abs(x0 - body_x0) <= _INDENT_TOL and pending_role in (
                "lower-court", "counsel"):
            pending.append(group)          # the origin's runover
            continue
        # A ROW AT NO POSITION THIS PAPER USES is not this paper's. Leave it
        # to core rather than tint it with a role that would be a guess.
        flush()
        band = "unknown"
    flush()
    if not stopped:
        return NOTHING          # every slip in the corpus signs its opinion
    if not caption or not dockets:
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_SLIP
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    _origin(ctx, origin)
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    # THIS COURT PUBLISHES EVERY SLIP IT FILES. North Carolina's unpublished
    # regime (App. R. 30(e)) belongs to the COURT OF APPEALS; the Supreme
    # Court reports all of its opinions and prints no publication flag at
    # all. Declared here because core reads status out of PROSE and the
    # origin describes the decision UNDER REVIEW — '…of a unanimous,
    # unpublished decision of the Court of Appeals…' stamped 6 of these 50
    # published opinions 'unpublished' (core-patch-queue #10). The same
    # declaration, for the same reason, is on alaskactapp.
    ctx.crit["publication_status"] = "published"
    return ctx.result()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, body_size, rail):
        self.model = model
        self.geom = geom
        self.body_size = body_size
        self.rail = rail
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, groups: list, role: str):
        """One element — a row, or a row and its wraps — as ONE styled line.

        nc sets its origin and each counsel entry as a FLOWING paragraph and
        lets it wrap; reproduced row by row the block reads as a column of
        justified fragments. The wraps are joined, and every line id they
        came from is joined with them."""
        parts = [l for g in groups for l in sorted(g, key=lambda l: l.x0)]
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        centred = role in ("court", "docket", "date")
        rel = 0.0
        if role == "caption":
            rel = round(max(0.0, first.x0 - self.rail), 1)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centred else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str):
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int):
        prev = next((i for i in reversed(self.items)
                     if isinstance(i, m.HmLine)), None)
        self.items.append(m.Rule(
            prov=prev.prov if prev is not None else m.Prov(page),
            span="full"))

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party statements either side of the
    FIRST pivot — never by joining the caption wholesale. A consolidated
    caption prints a second and a third pivot (gvest's counterclaim, langley's
    companion appeal); the lead case is the one the first pivot divides."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen = 0
    for row in rows:
        row = row.rstrip("*†‡∗⁎ ")
        if _PIVOT.match(row):
            seen += 1
            if seen > 1:
                break
            side = right
            continue
        if _CONNECTIVE.match(row) or _is_status(row):
            continue
        side.append(_strip_status(row))
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


def _origin(ctx: _Ctx, rows: list) -> None:
    """The origin band: one prose statement of how the case got here. What
    can be read out of it in a CLOSED form is read; the rest stands as the
    procedural history, which is what the paragraph is."""
    if not rows:
        return
    text = _norm(" ".join(rows))
    ctx.crit["history"] = text[:2000]
    # THE TRIBUNAL WHOSE DECISION IS UNDER REVIEW. On a discretionary
    # review or a dissent-based appeal that is the Court of Appeals; on a
    # direct appeal it is the trial division that entered the order.
    if _COURT_OF_APPEALS in text.lower():
        ctx.crit["lower_court"] = _COA_NAME
    else:
        tc = _TRIAL_COURT.search(text)
        if tc:
            ctx.crit["lower_court"] = f"{tc.group(1)} Court, {tc.group(2)} County"
    judge = _TRIAL_JUDGE.search(text)
    if judge:
        ctx.crit["lower_court_judge"] = _norm(judge.group(1)).rstrip(",")
    coa = [_norm(d).replace("COA ", "COA") for d in _COA_DOCKET.findall(text)]
    if coa:
        ctx.crit["lower_court_docket"] = coa
    # HOW THIS COURT TOOK IT UP: heard, or determined on the record.
    heard = _HEARD.search(text)
    if _NO_ARGUMENT in text.lower():
        cal = _CALENDARED.search(text)
        if cal:
            ctx.crit["submitted"] = _norm(cal.group(1))
    elif heard:
        # nc states the argument date and nothing else about the sitting;
        # there is no `argued` criterion, and `submitted` would be a lie.
        pass
