"""Oregon Tax Court ('ortc').

Everything unique to ortc lives here. It imports core, never another court
file, and no other court file imports it.

TWO PAPERS, AND THE PAGE SIZE NAMES THEM. Measured over all 42 records of
/assets/ortc, this court's corpus splits exactly in two and nothing is left
over:

  20 records  THE OREGON TAX REPORTS ADVANCE SHEET — a 396x612 half-measure
              reporter leaf, ruled under its page head, 301.5pt type block,
              masthead 'IN THE OREGON TAX COURT' / 'REGULAR DIVISION'
              centred on the block's own axis. THIS FILE READS THAT PAPER.

  22 records  THE COURT'S OWN FILING — a 612x792 sheet whose caption is set
              in two columns against a STACKED ')' rail at x0 297-310, over
              'IN THE OREGON TAX COURT' / 'MAGISTRATE DIVISION' (or
              'REGULAR DIVISION') and a subject line ('Property Tax',
              'Income Tax', 'Local Business Tax'). THIS FILE DECLINES THAT
              PAPER and returns NOTHING for it: its rail is a two-column
              contract of the ca6 family and it has not been measured here.
              Declined by name: covenant_presbyterian_church, d._kahl,
              deras, e._kahl, godware, goodsell, holmes_family_trust,
              lewis, multitude_of_mercies_foundation, n._kahl, pugsley,
              rev._div._v._lsg_sky_chefs, ringo, sandor, secrest,
              seeley_v._dept._of_rev., seeley_v._portland_public_schools,
              skadsen, sp_260_limited_partnership, willey, woolum,
              yves_teirlynck_and_tea_teirlynck_revocable_trust.

THE ADVANCE-SHEET CONTRACT, which is Oregon's reporter setting and the same
frame `or` reads for the Supreme Court — the same 301.5pt measure, the same
alternating 45.0/49.5 rail, the same rule at top 49.1 — but a DIFFERENT
ladder, because this is a trial court sitting one judge:

    ┌──────────────────────────────────────────────────────────────────┐
    │ No. 4          June 2, 2022                  87     the page head│
    ├───────────────── DRAWN RULE, top 49.1, 301.5pt ──────────────────┤
    │              IN THE OREGON TAX COURT                the masthead │
    │                 REGULAR DIVISION                                 │
    │                                                                  │
    │                Natasha K. DUNNE,                                 │
    │                     Plaintiff,                      the caption,  │
    │                        v.                           centred on   │
    │              DEPARTMENT OF REVENUE,                 the block's  │
    │                 State of Oregon,                    own axis     │
    │                    Defendant,                                    │
    │                       and                                        │
    │            DOUGLAS COUNTY ASSESSOR,                              │
    │                Defendant-Intervenor.                             │
    │                    (TC 5440)                        the docket   │
    │                                                                  │
    │  On Defendant-Intervenor Douglas County Assessor's (the county's) │
    │ motion to compel Plaintiff to allow an inspection …  the REPORTER'S│
    │ … The court granted the county's motion to compel …  SUMMARY, 8pt │
    │                                                                  │
    │   Oral argument on Defendant-Intervenor's motion to               │
    │ compel discovery was held remotely on June 1, 2022.  the sitting  │
    │   Paul E. Meyer, Douglas County Counsel, Roseburg, …  counsel     │
    │   Natasha K. Dunne, Plaintiff, filed a response …                 │
    │   Decision rendered June 2, 2022.                    the date     │
    │      ROBERT T. MANICKE, Judge.                       the writing  │
    └──────────────────────────────────────────────────────────────────┘

THE DRAWN RULE IS THE PAGE'S OWN MEASURE, and it is the dispatch. Every
page of all 20 reporter records draws exactly one rule at top 49.1 running
the full 301.5pt measure — x0 49.5 on the opening recto, 45.0 on a verso.
It gives the reader three facts it never has to guess: the RAIL (its x0),
the AXIS (x0 + 150.75), and the foot of the PAGE HEAD (everything above
it). Page width / 2 is the wrong axis and reads every caption row as an
indent, because the type block is offset by the binding margin and the
offset changes side every leaf. The 22 court-filing records draw no such
rule on a 396pt page, so the same test both frames one paper and refuses
the other.

CENTRED IS A MEASURED FACT. A row's offset from the axis is
(x0 + x1) / 2 - axis, and over the 20 records every masthead, caption and
docket row lands within 0.1pt of it. A justified ladder wrap fills the
measure exactly and so shares the axis — ink WIDTH separates them, but only
just: the widest centred row is d.e._shaw's 298.9pt party wrap ('Benson
Creek Windfarm, LLC; Durbin Creek Windfarm, LLC;') against a justified
wrap's 301.5pt. So width is a guard, not the boundary, and the boundary is
the DOCKET ROW: every one of the 20 records prints '(TC nnnn)' as the last
centred row, and the caption closes on it. Nothing below it is ever read as
caption whatever it measures.

THE REPORTER'S SUMMARY IS 8pt AND IT IS PART OF THE BLOCK. Between the
docket and the ladder the advance sheet sets a precis of what the court
did, at 8pt against the paper's 11pt, first line indented 15.0pt and
runovers at the rail. It is NOT a footnote: the page's footnote apparatus
is the same 8pt but stands below a 58.5pt separator rule at the foot, which
is under the byline and therefore below where this reader ever reaches. The
summary is claimed with the role `summary`, which is what it is — the
Reporter of Decisions' work, printed in the headmatter.

THE LADDER IS READ RUNG BY RUNG. A rung OPENS at 15.0pt in and CONTINUES at
the rail, and its role is decided from the opener alone and never revised —
a wrap says nothing about what its rung is. Two rungs and only two carry a
role other than counsel, and each is named by its own opener (measured over
all 20 records, which they partition with nothing ambiguous):

  the sitting  'Oral argument on … was held …' (10) | 'Submitted on …' (7)
               | 'Trial was held …' (2) | 'Submitted on Defendant's
               Statement of Attorney Fees.' (1) — how the matter came on
               and when, which is `criteria.submitted`.
  the date     'Decision rendered <date>.' (16) | 'Decision for Defendant
               rendered <date>.' (4) — the filing date, which is
               `criteria.decision_date`.
  counsel      everything else in the ladder. Every counsel rung on this
               paper opens on a person's name.

THERE IS NO PANEL AND NO ORIGIN. The Tax Court is a court of first
instance sitting one judge, so the advance sheet prints neither a roster
nor an 'On review from …' rung, and tagging a row `panel` or
`lower-court` would be a claim the paper does not make. All 20 records are
signed 'ROBERT T. MANICKE, Judge.'

THE BYLINE ENDS THE READER, at the BODY INDENT. Every one of the 20 records
sets it at dx 42.0 — Oregon's paragraph indent, twice anything the ladder
uses — so the reader stops on the geometry and the words are only a
belt-and-braces second test. 19 records sign on page 1 and
dept._of_rev._v._wakefield on page 2, so the walk is bounded at three
pages. Nothing below the byline is claimed, which is what leaves core the
anchor it opens the writing on.

THE PAGE HEAD IS THE REPORTER'S, NOT THE COURT'S. Above the rule the
advance sheet prints three pieces on one row — the folio, the FILING DATE
and the advance sheet's own serial ('No. 4'). pdfio orders them by x0 and
the order changes with the leaf, so they are told apart by shape, never by
position. Core knows the folio; it cannot know the other two, which are
content by every test it has and render as untagged rows of the block.
They are dropped here as the page head they are, and the date is harvested
into `criteria.decision_date`.

THE CITE AND THE SHORT NAME COME OUT OF THE RUNNING HEAD, which is the only
place the advance sheet prints them: rectos read 'Cite as 25 OTR 87 (2022)'
and versos 'Dunne v. Dept. of Rev.'. Both are furniture and neither gets a
row — a role would say the block prints something it does not — but
'25 OTR 87' is the reporter citation and it goes into `criteria.citation`,
the short form into `criteria.short_case_name`.

THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
has no `docket` field and no `argued` field: the docket is `docket_number`
plus `other_dockets`, and a date the matter was argued or submitted belongs
in `submitted`. Written under any other name they are attached by setattr
and never serialized.

WIRING. This file is not yet imported by centralia/courts/__init__.py; a
`from . import ortc` line is still needed there for the profile and the
decider to register.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from . import PROFILES

# THE BYLINE IS SIGNED BY A JUDGE, NOT A JUSTICE. All 20 advance-sheet
# records sign 'ROBERT T. MANICKE, Judge.' and the 22 court filings close
# 'This document was signed by Magistrate …' — 'Judge' is the title this
# court's bench actually prints, and with the default prose vocabulary
# ('Justice') the author of every record came back empty and the writing
# was typed `order` off a missing heading instead of `majority`.
ORTC = CourtProfile(
    "ortc", "Oregon Tax Court",
    byline=BylineGrammar(style="prose",
                         titles=("Judge", "Magistrate", "Justice")),
)
PROFILES[ORTC.court_id] = ORTC

STYLE_ADVANCE_SHEET = "advance-sheet"

# ---------------------------------------------------------------------------
# The paper, measured over the 20 advance-sheet records of /assets/ortc.
# ---------------------------------------------------------------------------
# The page-head rule: exactly one per page, top 49.1, x0 45.0/49.5, always
# 301.5pt wide. The 22 court-filing records draw nothing like it.
_PAGE_WIDTH = 396.0
_PAGE_WIDTH_TOL = 4.0
_RULE_TOP = 49.1
_RULE_TOP_TOL = 2.5
_MEASURE = 301.5
_AXIS_FROM_RAIL = _MEASURE / 2          # 150.75
# A CENTRED ROW IS A SHORT ROW ON THE AXIS. Every masthead/caption/docket row
# is within 0.1pt of the axis. The width guard has to admit d.e._shaw's
# 298.9pt party wrap and refuse a 301.5pt justified ladder wrap; it is a
# guard only, because the caption's real bound is the docket row.
_AXIS_TOL = 4.0
_CENTRED_WIDTH_MAX = 300.0
# The ladder: an opener stands 15.0pt in from the rail, a wrap at the rail.
# The BODY indent is 42.0pt, and the byline is the only row set there.
_INDENT = 15.0
_LADDER_X_MAX = 25.0
# The paper is 11pt; the reporter's summary and its footnote apparatus are
# both 8pt. Nothing the ladder prints is under 11pt.
_BODY_SIZE_MIN = 10.5
# 19 records sign on page 1, one on page 2. Nothing needs a fourth page.
_MAX_PAGES = 3
# Real blank bands in the block: 28.0pt under the masthead and 21.0pt under
# the docket row. Every step inside a band is 9.0-18.0pt.
_GAP_MIN = 20.0
# Pieces the page set on ONE row: only the page head does this (folio, date
# and serial, 80-100pt apart). A justified line never leaves that much.
_SAME_ROW_SPLIT = 20.0

_MASTHEAD_1 = re.compile(r"^IN THE OREGON TAX COURT$", re.I)
_MASTHEAD_2 = re.compile(r"^(REGULAR|MAGISTRATE)\s+DIVISION$", re.I)

# The page head's two content pieces are the FILING DATE and the advance
# sheet's own serial for this opinion ('No. 4' — not a docket, and there is
# no criteria field for it). Only the date is read; both are dropped.
_HEAD_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_FOLIO = re.compile(r"^\d{1,4}$")
_HEAD_SERIAL = re.compile(r"^No\.\s*\d+$", re.I)

# The running heads — the only place the advance sheet prints the reporter
# citation and the case's short name.
_CITE_HEAD = re.compile(r"^Cite as\s+(\d+\s+OTR\s+\d+)\s*\(\d{4}\)$", re.I)

# THE DOCKET is one parenthesised group of Tax Court numbers, centred as the
# caption's last row: '(TC 5440)', '(TC 5406 & 5407)'.
_DOCKET_ROW = re.compile(r"^\(\s*(TC|OTC)\s+([0-9A-Za-z&,;\s]+?)\s*\)$", re.I)

# The caption's own closed vocabularies: the pivot, the connector and the
# party STATUS labels. No party or court NAME is ever read by wording.
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_CONNECTOR = re.compile(r"^and$", re.I)
_PARTY_WORD = (r"Plaintiffs?|Defendants?|Petitioners?|Respondents?"
               r"|Appellants?|Appellees?|Relators?|Movants?|Intervenors?"
               r"|Claimants?")
_STATUS = re.compile(
    rf"^(?:(?:{_PARTY_WORD})|Third-Party\s+(?:{_PARTY_WORD}))"
    rf"(?:\s*-\s*(?:Adverse\s+Party|{_PARTY_WORD}))?"
    r"(?:\s+(?:on\s+Review|Below))?\s*[,.;]?$", re.I)

# THE SITTING RUNG — how the matter came on, and when. Measured openers over
# all 20 records; nothing else in the ladder opens on any of these words,
# because every counsel rung opens on a person's name.
_SITTING = re.compile(
    r"^(?:Oral\s+argument|Argument|Submitted|Trial\s+was\s+held"
    r"|Trial|Hearing\s+was\s+held|Hearing)\b", re.I)
# THE DATE RUNG — 'Decision rendered <date>.' / 'Decision for Defendant
# rendered on <date>.'
_DECISION = re.compile(r"^(?:Decision|Order|Judgment)\b", re.I)
_DATE_VALUE = re.compile(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})")
_MOTION = re.compile(
    r"\b(cross-motions?\s+for\s+(?:partial\s+)?summary\s+judgment"
    r"|motions?\s+for\s+(?:partial\s+)?summary\s+judgment"
    r"|motions?\s+for\s+reconsideration|motion\s+for\s+reconsideration"
    r"|motion\s+to\s+dismiss|dispositive\s+motion"
    r"|motion\s+to\s+compel|motion\s+for\s+stay\s+of\s+payment"
    r"|statement\s+of\s+attorney\s+fees)\b", re.I)

# THE BYLINE. All 20 records sign 'ROBERT T. MANICKE, Judge.' The geometry
# (dx 42.0, the body indent) is the primary test; this is the second.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z’'\-]*(?:\s+[A-Z]\.)*"
    r"(?:\s+[A-Z][A-Za-z’'\-]*)*,\s*"
    r"(?:Judge|Magistrate|Presiding\s+Magistrate|J\.|C\.\s*J\.)"
    r"|PER\s+CURIAM)\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _page_frame(pm) -> tuple[float, float, float] | None:
    """(rail, axis, head_foot) from the page's own drawn rule, or None.

    None is the refusal: a 396pt leaf that draws no 301.5pt rule at top
    49.1 is not this paper, and neither is a 612pt sheet."""
    if abs(pm.width - _PAGE_WIDTH) > _PAGE_WIDTH_TOL:
        return None
    for rule in pm.h_rules:
        if abs(rule.top - _RULE_TOP) <= _RULE_TOP_TOL \
                and abs((rule.x1 - rule.x0) - _MEASURE) <= 6.0:
            return rule.x0, rule.x0 + _AXIS_FROM_RAIL, rule.top
    return None


@decider("headmatter.read", court="ortc")
def read_headmatter_ortc(model, geom, **_):
    """Read the Oregon Tax Reports advance-sheet block, or NOTHING."""
    if not model.pages:
        return NOTHING
    # THE DISPATCH, part one: the page's own drawn measure. This is what
    # refuses the 22 court-filing records without reading a word of them.
    frame1 = _page_frame(model.pages[0])
    if frame1 is None:
        return NOTHING

    rows: list[tuple] = []          # (page, rail, axis, head_foot, [lines])
    for pm in model.pages[:_MAX_PAGES]:
        frame = _page_frame(pm)
        if frame is None:
            continue
        rail, axis, head_foot = frame
        for group in _rows(pm):
            rows.append((pm, rail, axis, head_foot, group))
    if len(rows) < 8:
        return NOTHING

    # THE DISPATCH, part two: the two-row masthead below page 1's rule.
    # Never an ordinal — the page head is three pieces on one row and pdfio
    # orders them by x0, so the masthead's index moves with the leaf.
    mast = None
    for idx, (pm, _rail, _axis, head_foot, group) in enumerate(rows[:8]):
        if pm.number != 1 or group[0].top <= head_foot:
            continue
        if _MASTHEAD_1.match(_norm(" ".join(l.plain for l in group))):
            mast = idx
            break
    if mast is None:
        return NOTHING

    ctx = _Ctx()
    # THE RUNNING HEADS, read across EVERY page and never claimed. A verso
    # head is the folio at the rail and the short case name flush right; a
    # recto head is the citation at the rail and the folio flush right. So
    # the short name is the piece at the RIGHT MARGIN that is not a folio.
    for pm in model.pages:
        frame = _page_frame(pm)
        if frame is None:
            continue
        rail, _axis, head_foot = frame
        right = rail + _MEASURE
        for line in pm.lines:
            if line.top > head_foot:
                continue
            head = _norm(line.plain)
            if not head:
                continue
            cite = _CITE_HEAD.match(head)
            if cite:
                ctx.crit.setdefault("citation", _norm(cite.group(1)))
            elif (pm.number > 1 and abs(line.x1 - right) <= 4.0
                  and not _FOLIO.match(head)):
                ctx.crit.setdefault("short_case_name", head)

    caption_rows: list[str] = []     # the printed caption, verbatim
    party_rows: list[str] = []       # one entry per party GROUP
    party_heads: list[str] = []      # each group's FIRST row — the name
    party_buf: list[str] = []        # the group being read
    pivot_at: int | None = None      # index into party_rows
    dockets: list[str] = []          # this court's numbers, in printed order
    rungs: list[list] = []           # [role, whole printed text] per rung
    band = "head"                    # head | caption | post
    prev_top: float | None = None
    prev_page: int | None = None
    summary_open = False

    def _flush_party() -> None:
        """A PARTY GROUP IS THE ROWS DOWN TO ITS STATUS LABEL. The reporter
        sets the party's name, then its residence or state beneath it, then
        the label ('DEPARTMENT OF REVENUE,' / 'State of Oregon,' /
        'Defendant,') — one party, three rows."""
        if party_buf:
            party_rows.append(_norm(" ".join(party_buf)))
            party_heads.append(party_buf[0])
            party_buf.clear()

    for idx, (pm, rail, axis, head_foot, group) in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        x1 = max(l.x1 for l in pieces)
        width = x1 - first.x0
        dx = first.x0 - rail
        centred = (abs((first.x0 + x1) / 2 - axis) <= _AXIS_TOL
                   and width <= _CENTRED_WIDTH_MAX)

        # THE PAGE HEAD, by the rule the page draws under it. On page 1 it
        # is the advance sheet's dateline and serial, which core cannot know
        # and leaves as untagged rows; on later pages it is the running
        # head, which core already drops and the pre-pass above has read.
        if first.top <= head_foot:
            if pm.number == 1:
                if _HEAD_DATE.match(text):
                    ctx.crit.setdefault("decision_date", text)
                ctx.drop(pieces, "running-head")
            continue

        # THE BYLINE ENDS THE READER: the body indent first, the words
        # second. It is never on the axis, so a caption row shaped like one
        # cannot end the reader early.
        if idx > mast and not centred:
            if dx > _LADDER_X_MAX or _BYLINE.match(text):
                break

        # The paper's own blank bands, kept as rhythm.
        if prev_top is not None and prev_page == pm.number \
                and first.top - prev_top >= _GAP_MIN:
            ctx.gap()
        prev_top, prev_page = first.top, pm.number

        if band == "head":
            if idx == mast or (idx == mast + 1 and _MASTHEAD_2.match(text)):
                ctx.crit["court"] = _norm(
                    (ctx.crit.get("court", "") + " " + text))
                ctx.emit(pieces, "banner", centre=True)
                if idx > mast:
                    band = "caption"
                continue
            band = "caption"

        # ---- the reporter's SUMMARY: the 8pt run between docket and ladder
        if first.size and first.size < _BODY_SIZE_MIN:
            if band == "post":
                summary_open = True
                ctx.emit(pieces, "summary", centre=False, rel=dx)
                continue
            # 8pt above the docket row is not something this paper prints.
            return NOTHING

        # ---- the caption band, closed by the DOCKET ROW ------------------
        if band == "caption":
            if centred:
                docket = _DOCKET_ROW.match(text)
                if docket:
                    _flush_party()
                    _read_dockets(docket, dockets)
                    ctx.emit(pieces, "docket", centre=True)
                    band = "post"
                    continue
                caption_rows.append(text)
                if _PIVOT.match(text):
                    _flush_party()
                    if pivot_at is None:
                        pivot_at = len(party_rows)
                elif _STATUS.match(text) or _CONNECTOR.match(text):
                    _flush_party()
                else:
                    party_buf.append(text)
                    if text.endswith("."):
                        _flush_party()
                ctx.emit(pieces, "caption", centre=True)
                continue
            # No docket row: the caption ran out at a row off the axis.
            _flush_party()
            band = "post"

        # ---- the ladder: rung by rung, each by its own opener ------------
        # A rung OPENS on the 15pt indent and CONTINUES at the rail. Its
        # role is decided from the opener alone and never revised, because a
        # wrap says nothing about what its rung is.
        if summary_open or dx >= _INDENT - 5.0 or not rungs:
            summary_open = False
            role = "counsel"
            if _SITTING.match(text):
                role = "date"
            elif _DECISION.match(text):
                role = "date"
            rungs.append([role, text])
        else:
            rungs[-1][1] = _norm(rungs[-1][1] + " " + text)
        ctx.emit(pieces, rungs[-1][0], centre=False, rel=dx)

    # A CLAIM THAT NEVER LEFT THE MASTHEAD IS NOT A READING.
    _flush_party()
    if band != "post" or not rungs or not ctx.items:
        return NOTHING

    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if dockets[1:]:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows)
    if party_rows:
        ctx.crit.setdefault("parties", party_rows)
        name = _case_name(party_heads, pivot_at)
        if name:
            ctx.crit.setdefault("case_name", name)

    # ---- the rungs, parsed once each is whole -------------------------
    counsel = [t for role, t in rungs if role == "counsel"]
    for role, text in rungs:
        if role != "date":
            continue
        found = _DATE_VALUE.search(text)
        if _DECISION.match(text):
            if found:
                ctx.crit["decision_date"] = _norm(found.group(1))
            ctx.crit.setdefault("disposition", text.rstrip("."))
        else:
            if found:
                ctx.crit.setdefault("submitted", _norm(found.group(1)))
            ctx.crit.setdefault("history", text[:2000])
            motion = _MOTION.search(text)
            if motion:
                ctx.crit.setdefault("motion", _norm(motion.group(1)))
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    ctx.crit.setdefault("headmatter_style", STYLE_ADVANCE_SHEET)
    return ctx.result()


# ---------------------------------------------------------------------------
# the parsed forms, kept beside the printed ones
# ---------------------------------------------------------------------------

def _read_dockets(match, mine: list[str]) -> None:
    """'(TC 5440)' / '(TC 5406 & 5407)' — the court's own number, and the
    companion appeals consolidated into it."""
    court = match.group(1).upper()
    for piece in re.split(r"[&,;]", match.group(2)):
        piece = _norm(piece)
        if piece:
            mine.append(f"{court} {piece}")


def _case_name(parties: list[str], pivot_at: int | None) -> str | None:
    """'X v. Y', from the party either side of the pivot — never from the
    caption rows joined wholesale."""
    if pivot_at is None or pivot_at <= 0 or pivot_at >= len(parties):
        return None
    left = parties[0].rstrip(",;. ")
    right = parties[pivot_at].rstrip(",;. ")
    if not left or not right:
        return None
    return f"{left} v. {right}"


# ---------------------------------------------------------------------------
# rows, and the emit buffer
# ---------------------------------------------------------------------------

def _rows(pm) -> list[list]:
    """One group per printed row, EXCEPT where the page set two things far
    apart on one row — which on this paper only the page head does."""
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
    out: list[list] = []
    for key in order:
        row = sorted(groups[key], key=lambda l: l.x0)
        chunk = [row[0]]
        for piece in row[1:]:
            if piece.x0 - chunk[-1].x1 > _SAME_ROW_SPLIT:
                out.append(chunk)
                chunk = [piece]
            else:
                chunk.append(piece)
        out.append(chunk)
    return out


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True,
             rel: float = 0.0) -> None:
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
            bold=all(bool(p.all_bold) for p in parts),
            rel=0.0 if centre else round(rel, 1), role=role))
        self.consumed.update(p.id for p in parts)

    def gap(self, lines: int = 1) -> None:
        self.items.append(m.Gap(lines=lines))

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
