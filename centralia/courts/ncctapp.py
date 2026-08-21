"""Court of Appeals of North Carolina ('ncctapp').

Everything unique to ncctapp lives here. It imports core, never another
court file, and no other court file imports it. The Supreme Court of North
Carolina is `courts/nc.py`; the two courts share a publisher and the same
FOUR-POSITION indent ladder, but they are different papers and nothing is
imported across.

THE CONTRACT — 'filed slip', printed 42 times out of 42.

Like its Supreme Court, this court draws nothing, fences nothing, and sets
its whole front matter in ONE type size (12pt on a 612x792 page, 72pt body
rail). What it does instead is set each band on its OWN horizontal
position, and that ladder is the entire parser:

    ┌ 306.0 — the PAGE AXIS ─────────────────────────────────────────────┐
    │ An unpublished opinion of the North Carolina Court of Appeals …    │
    │ … Rule 30(e)(3) …          the Rule 30(e)(3) NOTICE, 11pt, at the  │
    │                            rail, ABOVE the masthead — 15 of 42    │
    │ IN THE COURT OF APPEALS OF NORTH CAROLINA   the masthead, 149.1-   │
    │ Nos. COA24-344, COA24-638                   462.8 on all 42       │
    │ Filed 20 May 2026                           the release date      │
    └────────────────────────────────────────────────────────────────────┘
      Mecklenburg County, No. 22CVD008584-590   72.0 — WHO TRIED IT and
      STEPHANIE AHDI, Plaintiff,                72.0 — the CAPTION RAIL
                  v.                           144.0 — the pivot, alone
      MASOUD AHDI, Defendant.                   72.0
        Appeal by defendant from orders entered 31 May 2023 … by Judge
      Karen D. McCallum in District Court, Mecklenburg County.  Heard in
      the Court of Appeals 8 April 2025.
                    108.0 opens it, 72.0 carries it — THE ORIGIN
        Hamilton Stephens Steele & Martin, PLLC, by Kyle A. Frost …, for
        plaintiff-appellee.
                    108.0 opens it, 108.0 carries it — THE APPEARANCES
        STROUD, Judge.             108.0 — and the writing starts

THE FOUR POSITIONS, each band named by where it sits and never by where it
comes in the block:

  * THE PAGE AXIS (|row centre - 306| <= 6pt) carries the three rows the
    court sets for itself, in this order on all 42: the masthead, the
    docket ('No. COA25-648' / 'Nos. COA24-344, COA24-638' / 'No. COA 25-790'
    — the court sometimes spaces the prefix — / 'No. COA23-487-2', a second
    hearing of one appeal), and the release date, DAY FIRST.

  * THE BODY RAIL (72.0) carries TWO different bands, told apart by what
    the first of them prints and not by their order:

      THE TRIBUNAL BELOW is ONE row carrying TWO facts — 'Mecklenburg
      County, No. 22CVD008584-590' — the county (or 'Property Tax
      Commission' / 'N.C. State Bar', 2 records) and the TRIAL court's own
      file number. That number is NOT this court's docket: the docket is
      the axis-centred COA number above it, and conflating the two prints
      two dockets on the cover. The trailing '-590' is the county's code,
      and '008584-590' a SPAN of numbers, not a hyphenated single docket;
      it is kept exactly as printed. A consolidated trial file prints
      'Nos. …, …' and wraps to a second rail row (5 records, up to five
      numbers).

      THE CAPTION follows it at the same rail. There is NO second column
      and NO rail, drawn or typed: the parties stand full measure at 72.0
      and the pivot 'v.' stands ALONE, centred at 144.0-153.8 on every one
      of the 33 records that print one — so NO CaptionBlock is emitted and
      no column is invented. The 9 records with no pivot are 'IN THE
      MATTER OF' / 'IN RE:' matters, which print one party and no pivot at
      all. fazzi_v._lebowitz sets its 19-row party list on a HALF measure
      (72.0-324.0) and centres its 'and' on that column's own axis at
      198.0 — a narrower measure for one caption, still one column.

  * THE PARAGRAPH INDENT opens the two prose bands AND the byline, so the
    indent alone cannot name them. What names them is the MEASURE of the
    opening row and where the paragraph's own WRAPS go:

        the ORIGIN — how the appeal got here, who tried it, and when this
        Court heard it — opens FULL MEASURE (its first row reaches the
        right edge on all 42) and its runover returns to the BODY RAIL;
        it is set ROMAN and DOUBLE-SPACED (28.8pt);

        the APPEARANCES are set ITALIC, open at the indent and KEEP it;
        they are SINGLE-SPACED (14.4pt) inside an entry and one full body
        line apart (28.8pt) between entries — so within the counsel band
        the pitch names the element, while the origin's identical 28.8pt
        is a wrap because it is at the RAIL.

    The indent is 108.0 on 41 records and 90.0 on ahdi, so it is read as
    'indented from the rail', not as a fixed rung.

  * THE BYLINE also stands at the indent and ends the reader. All 42 sign
    ('STROUD, Judge.' / 'DILLON, Chief Judge.' / 'PER CURIAM.', 7
    records), so the reader is never unbounded. It is tested only on a
    ROMAN row SHORT enough to be a signature, because a counsel entry
    stands at the same indent.

THE DISPATCH is the top of page 1: three axis-centred rows in order — this
court naming itself, a 'No.'/'Nos.' docket, a 'Filed <d Month yyyy>' — with
a row at the body rail under them. A record that does not print all four is
not this paper and gets NOTHING; core's shared walk is better than forcing
a paper through a contract it does not match.

WHAT THE READER INHERITS.

  THE RULE 30(e)(3) NOTICE. 15 of the 42 are unpublished, and those print
  a three-row 11pt notice at the rail ABOVE the masthead. It is the only
  thing on the page smaller than the body, it is a notice and not a
  reading, so it is dropped and RECORDED (kind='notice') — and its
  presence, the paper's own statement about itself, is what sets
  `publication_status`. Its ABSENCE sets 'published'. Declaring the value
  matters because core reads status out of prose (core-patch-queue #10)
  and this court's own origin band discusses published and unpublished
  decisions below.

  THE RUNNING HEAD. One record (fazzi) carries its counsel and byline to
  page 2, which opens with the short case name in caps over a 10pt
  'Opinion of the Court'. Any axis-centred row in the top band of a page
  after the first is inside this reader's region, and it is dropped and
  recorded as a running head.

  THE FOOTNOTE SEPARATOR: a drawn rect 144.0pt wide at the body rail.
  Nothing below it on that page is headmatter. The court also draws a
  228.4pt rule at 191.8 and a 67.1pt rule at 290.4 — those are UNDERLINES
  under a section heading, they are off the rail and the wrong measure,
  and they always stand below the byline.

ncctapp PRINTS NO panel roster, no headnote band, no syllabus and no
disposition in its headmatter: three judges hear the appeal and only the
author signs, so there is no `panel` row to read. An unpublished opinion is
often unsigned ('PER CURIAM.'), which is a signature and not a defect.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

STYLE_SLIP = "filed slip"

# ---- ncctapp's declared facts (measured over all 42 records) -------------
# THE PAGE AXIS. The masthead, the docket and the release date are the only
# rows the court centres; measured, every one sits within 0.2pt of the axis.
_AXIS_TOL = 6.0
# THE BODY RAIL and THE PARAGRAPH INDENT. The rail is 72.0 on all 42 (the
# caption shares it with the tribunal row — unlike nc, this court does not
# indent its caption by a fraction of an em). The indent is the rail + 36
# on 41 records and the rail + 18 on ahdi, so it is read as a BAND.
_RAIL_TOL = 1.6
_INDENT_MIN = 12.0
_INDENT_MAX = 60.0
# THE PIVOT stands alone between the two — 144.0 on a 72pt rail. fazzi's
# half-measure caption centres its 'and' at 187.6 on that column's own
# axis, so the band runs to rail + 130 and admits only a SHORT row.
_INNER_MIN = 20.0
_INNER_MAX = 130.0
_INNER_MAX_CHARS = 40
# WRAP vs NEW ELEMENT. One leading is 14.4pt and the next element stands
# one full body line lower (28.8pt anywhere, 26.4-27.3pt from the tribunal
# row into the caption). 20pt separates them with 5.6pt of clearance below
# and 6.4pt above.
_WRAP_PITCH = 20.0
# A SIGNATURE'S MEASURE. The longest byline in the corpus is 'CARPENTER,
# Judge.' at 121.2pt of type; the shortest counsel entry that opens at the
# indent is 197.1pt ('Mark L. Hayes for caveators-appellees.'). 160pt sits
# between them, and the test is only ever applied to a ROMAN row.
_SIG_MEASURE = 160.0
# THE FOOTNOTE SEPARATOR: a drawn rect 144.0pt wide at the body rail.
_SEP_MEASURE = (138.0, 150.0)
_SEP_RAIL = 3.0
# THE RUNNING HEAD occupies the top band of every page after the first
# ('FAZZI V. LEBOWITZ' at 37.6, 'Opinion of the Court' at 63.6 of 792).
_HEAD_BAND = 0.11
# HOW FAR THE BLOCK MAY RUN. fazzi's 19-row party list carries its counsel
# and its byline to page 2; nothing in the corpus needs a third.
_MAX_PAGES = 2

# 'IN THE COURT OF APPEALS OF NORTH CAROLINA' — this court's own engraving,
# set at the same measure (149.1-462.8) on all 42. The row is matched on
# the court it names, never on a party or a case.
_MASTHEAD = "in the court of appeals of north carolina"
# 'No. COA25-648' / 'Nos. COA24-344, COA24-638' / 'No. COA 25-790' /
# 'No. COA23-487-2'. This court numbers an appeal COA<yy>-<seq>, the year
# it was docketed first; a second hearing of the same appeal takes a
# '-2' tail. The prefix is printed with and without a space and is
# normalized to the court's own closed-up form.
_DOCKET_ROW = re.compile(r"^Nos?\.\s+\S")
_DOCKET = re.compile(r"\bCOA\s?\d{2}-\d{1,4}(?:-\d)?\b")
# 'Filed 20 May 2026' — the release date, labelled, DAY FIRST. The month is
# a closed vocabulary; nothing else is read out of the row.
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_FILED = re.compile(r"^Filed\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\.?$")
# 'An unpublished opinion of the North Carolina Court of Appeals does not
# constitute controlling legal authority. … Rule 30(e)(3) …' — the notice,
# identified as the only band on the page set SMALLER than the body and
# standing ABOVE the masthead. The wording is not what finds it; the two
# cues below only confirm what the geometry already said.
_NOTICE_CUES = ("unpublished opinion", "rule 30(e)(3)")
# 'Mecklenburg County, No. 22CVD008584-590' — one row, two facts. The head
# is the tribunal as printed, the tail is that tribunal's own file number
# or numbers, kept verbatim.
_BELOW_ROW = re.compile(r"^(?P<head>.{2,60}?),\s+Nos?\.\s+(?P<rest>\S.*)$")
# The pivot, and the caption's own connective — a caption row that is only
# 'and' joins two groups of parties on the same side (fazzi).
_PIVOT = re.compile(r"^v(?:s)?\.?$", re.I)
_CONNECTIVE = re.compile(r"^and$", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. This court sets the status at the END of the party it belongs to
# ('…, Plaintiff,' / '…, Attorney, Defendant.') or on a row of its own
# ('Deceased,' under each estate in in_re_atkinson). Generational suffixes
# are deliberately ABSENT: ', JR.' is part of a name, ', TRUSTEE' is not.
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "appellant",
    "appellants", "appellee", "appellees", "petitioner", "petitioners",
    "respondent", "respondents", "intervenor", "intervenors", "movant",
    "amicus", "amici", "curiae", "caveator", "caveators", "propounder",
    "propounders", "deceased", "decedent", "attorney", "trustee",
    "co-trustee", "guardian", "ad", "litem", "minor", "child", "children",
    "individually", "and", "et", "al", "a", "an", "the", "of", "heirs",
    "wife", "husband", "spouse", "third-party", "cross", "realigned",
    "substitute", "counterclaim",
)
# WHO TRIED IT. 'Judge' is a bench title, not a name; the name is the run
# of capitalised tokens after it, with a generational suffix if the court
# printed one ('Judge S. Thomas Currin, II, in Johnston County Superior
# Court'). A lower-case word ends the run, which is how 'in', 'and' and
# 'respectively' stay out of it. 'and Judge' opens a second name where two
# judges entered the orders under appeal ('by Judge Ashley Watlington-Simms
# and Judge Angela C. Foster, respectively', in_re_k.r.); a bare 'and' does
# not, so nothing else in the paragraph reaches this.
_TRIAL_JUDGE = re.compile(
    r"\b(?:by|and)\s+(?:Chief\s+)?Judge\s+"
    r"((?:[A-Z][A-Za-z.'’\-]*)(?:\s+[A-Z][A-Za-z.'’\-]*){0,4}"
    r"(?:,\s+(?:Jr\.|Sr\.|III|II|IV))?)")
# THE TRIBUNAL BELOW, in the two forms this state's trial divisions are
# printed in ('in District Court, Mecklenburg County' and 'in Mecklenburg
# County District Court'). A closed vocabulary of the divisions, never a
# court read out of open wording.
_TRIAL_COURT_A = re.compile(
    r"\bin\s+(Superior|District)\s+Court,\s+"
    r"([A-Z][A-Za-z.\-]*(?:\s+[A-Z][A-Za-z.\-]*)?)\s+County\b")
_TRIAL_COURT_B = re.compile(
    r"\bin\s+([A-Z][A-Za-z.\-]*(?:\s+[A-Z][A-Za-z.\-]*)?)\s+County\s+"
    r"(Superior|District)\s+Court\b")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_masthead(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD


def _filed_value(text: str) -> str | None:
    """'Filed 20 May 2026' -> 'May 20, 2026', or None."""
    mm = _FILED.match(_norm(text))
    if mm is None or mm.group(2).lower() not in _MONTHS:
        return None
    return f"{mm.group(2)} {int(mm.group(1))}, {mm.group(3)}"


def _dockets(text: str) -> list[str]:
    """The COA numbers this row prints, in printed order, closed up."""
    return [d.replace("COA ", "COA") for d in _DOCKET.findall(_norm(text))]


def _is_status(text: str) -> bool:
    bare = _norm(text).strip(".,;: ").lower()
    words = [w for w in re.split(r"[\s/,]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


# The trailing status clause of a party statement: everything after the
# LAST comma, with the sentence's own punctuation. Matched rather than
# rpartitioned so that what is KEPT keeps its punctuation — rstrip('.')
# turns 'ROBERT WESLEY ATKINSON, SR.,' into '… SR' and 'JAMES NELSON, JR.,
# TRUSTEE, Appellant,' into '… JR', and a generational suffix is part of a
# name.
_TRAILING = re.compile(r"^(?P<head>.*),\s*(?P<tail>[^,]+?)[.,;]?\s*$")


def _strip_status(text: str) -> str:
    """Drop the trailing status clauses from a party statement."""
    out = _norm(text)
    while True:
        mm = _TRAILING.match(out)
        if mm is None or not _is_status(mm.group("tail")):
            break
        out = mm.group("head")
    return out.rstrip(" ,;")


# --------------------------------------------------------------------------
# the page's own marks
# --------------------------------------------------------------------------

def _footnote_cut(pm, body_x0: float) -> float:
    """Where this page's footnotes begin — the top of the 144pt separator
    the court draws at the body rail. Its section-heading underlines are a
    different measure at a different position and are not this."""
    tops = [r.top for r in pm.h_rules
            if _SEP_MEASURE[0] <= r.width <= _SEP_MEASURE[1]
            and abs(r.x0 - body_x0) <= _SEP_RAIL]
    return min(tops) if tops else float("inf")


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ncctapp")
def read_headmatter_ncctapp(model, geom, **_):
    """Read the Court of Appeals of North Carolina's filed slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    page1 = model.pages[0]
    right_x1 = (geom.right_x1 if geom and getattr(geom, "right_x1", None)
                else page1.width - 72.0)

    # THE ROWS, in page order, with same-row pieces rejoined. fazzi's party
    # list is set wide enough that pdfio splits one of its rows at its own
    # gaps ('TERRI ' | 'EISENHAUER, ' | 'Individually,'), and a third of a
    # row is not a band.
    rows: list[tuple] = []
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
    if len(rows) < 6:
        return NOTHING

    # THE LADDER IS READ OFF THE PAGE. The rail is the leftmost left edge
    # on page 1's left half that carries an INDENTED rung above it; on all
    # 42 that is 72.0 and `geom.body_x0` agrees, but geom is measured over
    # the whole document and a short slip can outvote its own body.
    lefts = sorted({round(g[0].x0, 1) for pm, g in rows
                    if pm.number == 1 and g[0].x0 < pm.width / 2})
    if not lefts:
        return NOTHING
    rail = lefts[0]
    if not any(_INDENT_MIN <= x - rail <= _INDENT_MAX for x in lefts):
        return NOTHING

    def centred(group) -> bool:
        mid = (group[0].x0 + max(l.x1 for l in group)) / 2
        return abs(mid - page1.width / 2) <= _AXIS_TOL

    def flat(group) -> str:
        return _norm(" ".join(l.plain for l in
                              sorted(group, key=lambda l: l.x0)))

    # THE DISPATCH. Page 1 opens with the masthead — under the Rule 30(e)(3)
    # notice where the court prints one — followed by the docket and the
    # release date, all three on the axis, and a row at the rail below them.
    p1 = [g for pm, g in rows if pm.number == 1]
    mast = None
    for i, group in enumerate(p1[:5]):
        if _is_masthead(flat(group)) and centred(group):
            mast = i
            break
    if mast is None or len(p1) < mast + 5:
        return NOTHING
    if not (_DOCKET_ROW.match(flat(p1[mast + 1])) and centred(p1[mast + 1])
            and _filed_value(flat(p1[mast + 2])) and centred(p1[mast + 2])):
        return NOTHING
    if not any(abs(g[0].x0 - rail) <= _RAIL_TOL for g in p1[mast + 3:]):
        return NOTHING
    # THE NOTICE stands above the masthead, set smaller than the body, and
    # says what it is. Anything else up there is not this paper.
    notice = p1[:mast]
    if notice:
        joined = " ".join(flat(g) for g in notice).lower()
        if not all(max(l.size or 0.0 for l in g) < body_size - 0.5
                   for g in notice) \
                or not any(cue in joined for cue in _NOTICE_CUES):
            return NOTHING

    ctx = _Ctx(model)
    finder = FurnitureFinder(model, rail, body_size)
    parser = BylineParser(get_profile("ncctapp").byline)
    band = "notice"        # notice | axis | below | caption | origin | counsel
    caption: list[str] = []
    origin: list[str] = []
    counsel: list[str] = []
    dockets: list[str] = []
    below: list[str] = []
    pending: list = []     # the rows of the element being assembled
    pending_role = ""
    prev_page = prev_top = None
    stopped = False

    def flush():
        nonlocal pending, pending_role
        if pending:
            ctx.emit(pending, pending_role, rail)
            text = _norm(" ".join(flat(g) for g in pending))
            if pending_role == "caption":
                caption.append(text)
            elif pending_role == "counsel":
                counsel.append(text)
            elif pending_role == "lower-court":
                dest = below if band in ("below", "caption") else origin
                dest.append(text)
        pending, pending_role = [], ""

    def open_element(group, role):
        nonlocal pending, pending_role
        flush()
        pending, pending_role = [group], role

    for pm, group in rows:
        text = flat(group)
        x0 = group[0].x0
        x1 = max(l.x1 for l in group)
        top = group[0].top

        # THE RUNNING HEAD is the top band of any page after the first. It
        # is furniture wherever core's repeat floor happens to see it.
        if pm.number > 1 and top <= pm.height * _HEAD_BAND:
            flush()
            ctx.drop(group, "running-head")
            continue
        kind = finder.kind(pm, group[0])
        if kind:
            flush()
            ctx.drop(group, kind)
            continue

        wrap = (prev_page == pm.number and prev_top is not None
                and (top - prev_top) <= _WRAP_PITCH)
        prev_page, prev_top = pm.number, top

        if band == "notice":
            # Dropped and RECORDED: a notice is not a reading, and the
            # paper's statement about itself is kept as a criterion.
            if any(g is group for g in notice):
                ctx.drop(group, "notice")
                continue
            band = "axis"
        if band == "axis":
            if _is_masthead(text):
                ctx.crit.setdefault("court", text)
                ctx.emit([group], "court", rail)
                continue
            if _DOCKET_ROW.match(text) and centred(group):
                dockets.extend(_dockets(text))
                ctx.emit([group], "docket", rail)
                continue
            value = _filed_value(text)
            if value is not None and centred(group):
                ctx.crit.setdefault("decision_date", value)
                ctx.emit([group], "date", rail)
                continue
            band = "below"

        # THE BYLINE ENDS THE READER. Tested only on a ROMAN row at the
        # indent short enough to be a signature — a counsel entry stands
        # at the same indent and would otherwise be read as one.
        if _INDENT_MIN <= x0 - rail <= _INDENT_MAX \
                and not all(l.all_emphasized for l in group) \
                and (x1 - x0) <= _SIG_MEASURE \
                and parser.parse(text) is not None:
            stopped = True
            break

        if abs(x0 - rail) <= _RAIL_TOL:
            if band == "origin":
                pending.append(group)       # the origin's runover
                continue
            if band == "below" and wrap and pending_role == "lower-court":
                pending.append(group)       # a consolidated trial file
                continue
            if band == "below" and _BELOW_ROW.match(text) and not below:
                open_element(group, "lower-court")
                continue
            band = "caption"
            if wrap and pending_role == "caption":
                pending.append(group)
            else:
                open_element(group, "caption")
            continue

        if _INDENT_MIN <= x0 - rail <= _INDENT_MAX:
            italic = all(l.all_emphasized for l in group)
            full = x1 >= right_x1 - 2.0
            if band == "counsel" or italic:
                # THE APPEARANCES keep the indent; the pitch names the
                # element, 14.4pt inside an entry and 28.8pt between them.
                band = "counsel"
                if wrap and pending_role == "counsel":
                    pending.append(group)
                else:
                    open_element(group, "counsel")
                continue
            if full and band in ("below", "caption"):
                # THE ORIGIN opens full measure and returns to the rail.
                band = "origin"
                open_element(group, "lower-court")
                continue
        if _INNER_MIN <= x0 - rail <= _INNER_MAX and band == "caption" \
                and len(text) <= _INNER_MAX_CHARS:
            # THE PIVOT, a status on a row of its own, or the caption's own
            # connective — indented from the rail, and short.
            open_element(group, "caption")
            continue
        # A ROW AT NO POSITION THIS PAPER USES is not this paper's. Leave
        # it to core rather than tint it with a role that would be a guess.
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
    # THE NOTICE IS THE PAPER'S OWN STATEMENT ABOUT ITSELF, and its absence
    # is a statement too: this court publishes what it does not mark.
    ctx.crit["publication_status"] = "unpublished" if notice else "published"
    _name(ctx, caption)
    _origin(ctx, below, origin)
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    return ctx.result()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model):
        self.model = model
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, groups: list, role: str, rail: float):
        """One element — a row, or a row and its wraps — as ONE styled line.

        The origin and each counsel entry are set as FLOWING paragraphs and
        let wrap; reproduced row by row the block reads as a column of
        justified fragments. The wraps are joined, and every line id they
        came from is joined with them."""
        parts = [l for g in groups for l in sorted(g, key=lambda l: l.x0)]
        if not parts:
            return
        first = parts[0]
        text = ""
        prev_plain = ""
        for part in parts:
            piece = line_markup(part)
            if not text.strip():
                text = piece
            elif prev_plain.rstrip().endswith("-") \
                    and not prev_plain.rstrip().endswith("--"):
                # A HYPHEN AT THE END OF A ROW IS THE COMPOUND'S OWN. This
                # court breaks a wrapped line only at a hyphen it already
                # printed ('for defendant-' / 'appellant.', 'and as Co-' /
                # 'Trustee of the Rebecca L. Lebowitz Living Trust') — all
                # 9 in the corpus are party-status or trustee compounds,
                # and none is a syllable break. Joined with a space they
                # render as 'defendant- appellant'.
                text = text.rstrip() + piece.lstrip()
            else:
                text = text.rstrip() + " " + piece.lstrip()
            prev_plain = part.plain
        centred = role in ("court", "docket", "date")
        rel = 0.0
        if role == "caption":
            rel = round(max(0.0, first.x0 - rail), 1)
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

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party statements either side of the
    pivot — never by joining the caption wholesale. The 9 'IN THE MATTER OF'
    records print no pivot at all, and there the whole caption IS the name."""
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
        if _is_status(row) and not _CONNECTIVE.match(row):
            continue
        if _CONNECTIVE.match(row):
            # The caption's own connective joins two groups of parties on
            # ONE side. Between a plaintiff and a defendant it says nothing
            # the pivot has not already said and is dropped; where the
            # court prints no pivot at all it is the only thing holding the
            # two estates of in_re_atkinson together.
            side.append(row.lower())
            continue
        side.append(_strip_status(row))
    if seen and left and right:
        one, two = (_norm(" ".join(w for w in left
                                   if not _CONNECTIVE.match(w))).rstrip(", "),
                    _norm(" ".join(w for w in right
                                   if not _CONNECTIVE.match(w))).rstrip(", "))
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _norm(" ".join(left + right)).rstrip(", ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


def _origin(ctx: _Ctx, below: list, rows: list) -> None:
    """The two bands that say where the case came from: the tribunal row,
    which prints the court below and ITS file numbers, and the origin
    paragraph, which is the procedural history in prose."""
    for row in below:
        mm = _BELOW_ROW.match(_norm(row))
        if mm is None:
            continue
        # THE TRIAL COURT'S OWN NUMBERS, kept exactly as printed: the tail
        # is a comma-separated run, and '008584-590' is a span of numbers
        # and a county code, not a hyphenated single docket.
        nums = [n.strip(" .") for n in mm.group("rest").split(",")]
        nums = [n for n in nums if n]
        if nums:
            ctx.crit["lower_court_docket"] = nums
        ctx.crit.setdefault("lower_court", mm.group("head").strip())
        break
    if not rows:
        return
    text = _norm(" ".join(rows))
    ctx.crit["history"] = text[:2000]
    # WHICH DIVISION TRIED IT. The tribunal row names the county; the origin
    # names the division sitting in it, in either of the two forms this
    # court prints. Where it names neither, the row's own head stands.
    ta = _TRIAL_COURT_A.search(text)
    tb = _TRIAL_COURT_B.search(text)
    if ta:
        ctx.crit["lower_court"] = f"{ta.group(1)} Court, {ta.group(2)} County"
    elif tb:
        ctx.crit["lower_court"] = f"{tb.group(2)} Court, {tb.group(1)} County"
    judges = [_norm(j).rstrip(",") for j in _TRIAL_JUDGE.findall(text)]
    seen: list[str] = []
    for j in judges:
        if j not in seen:
            seen.append(j)
    if seen:
        ctx.crit["lower_court_judge"] = "; ".join(seen)
