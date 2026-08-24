"""North Carolina Business Court ('ncbizct') — the Superior Court Division's
designated forum for Complex Business Cases.

Everything unique to ncbizct lives here. It imports core, never another
court file, and no other court file imports it. The Supreme Court of North
Carolina is `courts/nc.py` and the Court of Appeals is `courts/ncctapp.py`;
this court shares their publisher and NONE of their layout, because it is
not an appellate court. It is a TRIAL court sitting by county, so its front
matter is a county caption and not an appellate one.

THE CONTRACT — 'county caption', printed 42 times out of 42.

    Auto Provisions, LLC v. G1.34 Holdings, LLC, 2026 NCBC 40.   <- 36.1, the
                                                                   CITATION
    STATE OF NORTH CAROLINA        ¦ IN THE GENERAL COURT OF JUSTICE
                                   ¦ SUPERIOR COURT DIVISION
    WAKE COUNTY                    ¦ 24CV010060-910
                                   │  <- the DRAWN divider starts here
      AUTO PROVISIONS, LLC and     │ ORDER AND OPINION ON
      RECON PARTNERS, LLC,         │ PLAINTIFFS' MOTIONS FOR
              Plaintiffs and       │ SUMMARY JUDGMENT
      v.    Counterclaim Defendants│
      G1.34 HOLDINGS, LLC,         │
              Counterclaim Plaintiff.
    ───────────────────────────────┘  <- and the L closes the caption
    1. THIS MATTER is before the Court following the 2 October 2025 …

THE DIVIDER IS AN L, AND IT IS DRAWN. Measured over all 42: a vertical rect
whose FOOT meets a horizontal rect that ENDS at the vertical's own x (within
2pt vertically, 3pt horizontally). The vertical sits at 0.446-0.507 of the
page width (272.9-310.4 on 612pt); the horizontal runs 203.0-239.0pt from
6.1pt left of the caption rail to the vertical. cadieu_tree_experts draws
the third side too — a head rule at the vertical's top — so on that one
record the figure is a closed box; the other 41 print the L. NOTHING is
matched against text to decide which side of the caption a row is on: the
vertical's x IS the column boundary.

  * THE TWO COLUMNS ARE TWO STACKS, NOT PAIRED ROWS. The left column is
    set on a 12.0pt leading and the right on 14.4pt, and only 57 of the
    corpus's 158 right-hand rows share a top with a left-hand one — so each
    column is flowed on its own and nothing is padded. Pairing them by row
    would print 447 blank tinted cells across the corpus and assert a
    row-for-row correspondence the page does not set. (wyo settled this for
    the same geometry: a drawn rule, two stacks.)

  * ABOVE the vertical the court draws NOTHING, and the same two columns
    carry the MASTHEAD BAND: the state and the county on the left, the court
    and its division and THIS COURT'S OWN FILE NUMBER on the right. The
    boundary is not guessed there either — it is the drawn vertical's x,
    extended upward, and it is checked: on all 42 every masthead piece lies
    wholly on one side of it. So the masthead renders as a caption block
    with an OPEN gutter and the parties as one with a DRAWN rail, because
    that is what the page prints.

  * The only rows that CROSS the divider are the citation rows above the
    masthead — which is how we know they are not part of the two-column
    zone at all.

THE FOUR LANDMARKS, in this order on all 42, are the dispatch:

    left  'STATE OF NORTH CAROLINA'
    right 'IN THE GENERAL COURT OF JUSTICE'
    right 'SUPERIOR COURT DIVISION'
    left  '<X> COUNTY' or 'COUNTY OF <X>'   right  the file number

A record that does not print all four, on the right side of the drawn
divider, in that order, is not this paper and gets NOTHING. Core's shared
walk already reads this court's caption tolerably (it finds the drawn rail
by itself); a confident misreading would be worse than that.

THE FILE NUMBER IS THIS COURT'S DOCKET, NOT A LOWER COURT'S. '24CV010060-910'
is a Superior Court file number: <yy>CV[S]<seq>-<county code>, the 'S' on
filings docketed before the 2023 renumbering. THIS COURT IS THE FORUM OF
FIRST INSTANCE — a Business Court judge is a Superior Court judge, the case
starts here, and there is no court below. `lower_court`,
`lower_court_docket` and `lower_court_judge` are therefore LEFT UNSET on
every record: the page prints no such thing and inventing one would be a
guess dressed as a fact. (Two records name an appeal in their own title —
'ORDER AND OPINION DISMISSING PLAINTIFF'S APPEAL' — but that is an appeal
FROM this court, not to it.)

THE CITATION IS NOT THE DOCKET. Every one of the 42 opens with its own
public-domain reporter cite at the rail, above the masthead, wrapping to a
second row when the case name is long (2 records): 'Brock v. Kyryk, 2026
NCBC 62.' The '2026 NCBC 62' goes to `Criteria.citation` and NEVER to
`docket_number` — conflating the two is the error that cost `ill` its whole
corpus (commit 03e8652). What stands before the cite is the court's own
SHORT form of the case name, and it is kept as `short_case_name`.

THE PAPER'S OWN NAME stands in the right column, bold italic, below the
divider's head: 'ORDER AND OPINION ON PLAINTIFFS' MOTIONS FOR SUMMARY
JUDGMENT'. It is `Criteria.title`, and its opening word is what sets
`doc_type` — the paper names itself and nothing else needs to infer it.
Two records add '[Public]' with a footnote reference in the same column.
That is about SEALING, not publication — its footnote reads 'The Court's
Order was provisionally filed under seal … the Court now files its Order …
in the public record' — so the row is read as `publication` and the
criterion is not taken from it.

`publication_status` comes from the OPINION NUMBER instead. This court
assigns 'YYYY NCBC NN' only to what it publishes; its unpublished work is
cited 'YYYY NCBC LEXIS NN', which is how these very opinions cite it
('Ehmann v. Medflow, Inc., 2017 NCBC LEXIS 88'). The number is printed on
all 42, so all 42 are 'published' — a printed fact, not an inference. It
also closes core-patch-queue **item 10** here: core reads status out of
prose, and fs_med_supplies came back 'unpublished' off a parenthetical
about ANOTHER decision ('*3-4 (2019) (unpublished)').

WHERE THE APPEARANCES ARE, AND WHY THEY ARE MOSTLY NOT HEADMATTER. Unlike
its appellate cousins this court sets its appearance block INSIDE the
opinion, under the three introductory paragraphs and above the byline:

    1. THIS MATTER is before the Court following …
    2. Pursuant to Rule 56 …
    3. For the reasons set forth herein, the Court GRANTS in part …
        Michael Best & Friedrich LLP by Justin G. May …, for Plaintiff …
    Robinson, Chief Judge.
    I. INTRODUCTION

Nothing is ever taken out of an assembled writing, so on the 40 records
that print it there the block STAYS in the opinion. Its text is still a
fact about the case, and `criteria.attorneys` is filled from it by READING
— never by consuming a line. That closes core-patch-queue **item 41** in
this court's own file the way four other courts closed it: a reader that
returns criteria replaces them wholesale, so any `attorneys` core's
leftover walk would have found is lost unless the reader states it.

On 2 records (best_logistics, wright_v_lorusso) the block stands DIRECTLY
under the closing rule, ahead of any prose. There it IS front matter, and
there it is claimed, with role `counsel`.

The appearance band is identified by TYPE and POSITION, never by wording:
all-italic, NOT bold, standing 18-80pt in from the caption rail (measured
23.9-68.9 over the corpus — the court uses five different indents). It is
bounded below by the first CENTRED BOLD row, which is the opinion's first
section heading ('I. INTRODUCTION', 'BACKGROUND'); without that bound the
scan runs on into the italic block quotations deep in the body.

WHAT ELSE IS READ WITHOUT BEING CLAIMED. All 42 sign off 'SO ORDERED, this
[the] 23rd day of April, 2026.' above a conformed '/s/' and the judge's
Business Court title. That sentence is the only place the paper states its
own date, and it is inside the writing; `decision_date` is read from the
LAST such sentence in the document and the line is left exactly where the
court put it.

HOW THIS READING DIFFERS FROM THE OLD ENGINE'S, deliberately. There is no
`baseline/ncbizct.json`, so `v1diff` is vacuous on this court and the check
was made by row-diffing the two rendered headmatters. 23 of the 42 reproduce
v1's rows exactly; the 19 that differ differ in four named ways, and the row
multiset accounts for every one:

  * 13 rows where THE PIVOT SHARES ITS BASELINE WITH A STATUS. The court
    sets 'v. ' at the rail and the party above's status at the indent on ONE
    line to save a line; v1 printed them as two rows, which puts the status
    UNDER the pivot it stands beside. We keep the line the court set.
  * 8 rows where AN APPEARANCE ENTRY'S WRAPS ARE JOINED into the one
    flowing entry it is (the convention every ported court follows; row by
    row an appearance reads as a column of justified fragments).
  * 2 rows v1 DROPPED: the typed underscore rule inside moore_v_brooks's
    left column, which divides the main action from the crossclaim action.
    A claim is total, so it is kept and rendered.
  * `&quot;` where v1 wrote a bare quotation mark — escaping, not content.

WHAT THIS COURT DOES NOT PRINT: no panel roster (one judge is assigned and
one judge signs), no headnotes, no syllabus, no disposition band, no
release-date row, no publication flag, and no lower court. Those criteria
stay unset, which is a statement, not a gap.

CORE OBSERVATIONS (diagnosed, NOT patched here — see notes/core-patch-queue.md):
  * item 41 — `criteria.attorneys` unreachable through the leftover walk;
    closed locally, as above.
  * NEW: core types 32 of these 42 papers 'order' and 10 'majority' from the
    same masthead. The paper's own name is 'ORDER AND OPINION' on all 42,
    which is why `doc_type_final` is stated here rather than inferred.
  * NEW, AND THE ONE FILE THIS READER MAKES WORSE — hart_v_dwm_advisors_llc
    comes back with TWO orders where core alone found one. Not this file's
    reading: `assemble.py`'s doc-type-heading anchor (the `if not starts`
    scan, ~line 1004) accepts a SHORT LOWER-CASE PROSE LINE as a heading.
    hart's page 2 opens with the tail of paragraph 3 — 'judgment are deemed
    admitted.").', 32 chars, 189pt wide — which `heading_doc_type` types
    JUDGMENT; the `headmatter_claimed` rule at ~line 1105 then prepends
    `_body0` and keeps that anchor, so one order is split at the page break.
    Core alone never reaches the line, because the FIRST heading it finds is
    the caption's own 'ORDER AND OPINION GRANTING' and the caption-band rule
    sends the body to the first segment below it — a row this reader has
    claimed. The existing `_wide` guard catches a full-measure prose line
    but not a paragraph's LAST line, which is short by definition. Exact
    patch, one line:

        _wide = _col > 100 and (line.x1 - line.x0) >= 0.8 * _col
        # A HEADING DOES NOT OPEN IN LOWER CASE.
        dt = (None if _wide or len(head) >= 80 or head[:1].islower()
              else heading_doc_type(head))

    Measured over the corpus, hart is the ONLY record with such a line, so
    the patch moves this court by exactly one file. NOT applied here.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from . import register

# The profile carries the court's NAME and nothing else. The byline grammar
# is deliberately left at core's default: this court's mid-order 'Robinson,
# Chief Judge.' row stands BELOW three numbered paragraphs, and declaring
# 'Judge' as a byline title would move every writing's start behind them.
# Core already recovers all 42 authors from the conformed '/s/' signature.
NCBIZCT = register(CourtProfile(
    "ncbizct", "North Carolina Business Court", rollout="migrated"))

STYLE_COUNTY = "county caption"

# ---- ncbizct's declared facts (measured over all 42 records) --------------
# THE DRAWN L. The vertical rect sits at 0.446-0.507 of the page width; the
# horizontal rect that closes it is 203.0-239.0pt wide and ENDS at the
# vertical's x. The band is deliberately generous either side of what was
# measured, because the figure is identified by its SHAPE, not its size.
_DIV_X_MIN, _DIV_X_MAX = 0.38, 0.60
_L_FOOT_DY = 2.5          # |h.top - v.bottom| for the corner to be a corner
_L_FOOT_DX = 3.0          # |h.x1 - v.x|
_CLOSE_W_MIN, _CLOSE_W_MAX = 170.0, 280.0
# COLUMN MEMBERSHIP. A piece is left of the divider or right of it; 1pt of
# slack absorbs the rect's own stroke. A piece that STRADDLES it belongs to
# neither column, and the only rows in the corpus that do are the citation
# rows above the masthead — which is the evidence that they stand outside
# the two-column zone.
_SIDE_TOL = 1.0
# THE MASTHEAD SITS ABOVE THE DIVIDER'S HEAD. Measured, the file-number row
# stands 16.9-41.2pt above it and the first party row 1.3-18.0pt below it,
# so the two bands never touch. The cut is taken at the FILE-NUMBER ROW
# (a landmark) rather than at the rule, because the rule is what proves the
# columns and the landmark is what names the band.
# THE CAPTION RAIL is measured INSIDE the caption band: this court sets its
# caption 3.1pt right of the body rail (75.1 against 72.0) and its body
# prose reaches 72.0 on page 1, so a rail measured across the page is the
# body's and not the caption's.
# THE APPEARANCE INDENT: 23.9-68.9pt in from the caption rail, five distinct
# values over the corpus, so it is read as a BAND and never as a rung.
_APP_IN_MIN, _APP_IN_MAX = 18.0, 80.0
# THE STATUS INDENT inside the left column. Measured: a status label stands
# 36.0-108.0pt in from the caption rail; a party statement stands within
# 4.3pt of it (chalk sets its nominal parties 4.3pt in). 20pt sits between
# them with 15.7pt of clearance either side. The indented PIVOT (35.3-40.3pt
# on 6 records) is tested before this, so it never reads as a status.
_STATUS_IN = 20.0
# A CENTRED BOLD ROW is the opinion's first section heading and bounds the
# appearance scan. 'DENIED in part.' is bold italic too and stands AT the
# rail, so the axis is what tells them apart.
_AXIS_TOL = 60.0
# HOW FAR THE APPEARANCE BLOCK MAY RUN: onto page 3 (chalk_v_chalk), never
# further.
_APP_PAGES = 3
# THE FOOTNOTE SEPARATOR: a drawn rect 144pt wide at the body rail. Nothing
# below it on its page is front matter or an appearance.
_SEP_W = (138.0, 150.0)
_SEP_RAIL = 6.0
# THE RUNNING HEAD, on a page the appearance block carries onto.
_HEAD_BAND = 0.075

# --- the four landmarks. Closed vocabularies: the court naming itself, its
# division, and the word 'COUNTY'. No party and no case is ever read by
# wording.
_STATE = "state of north carolina"
_GCJ = "in the general court of justice"
_DIVISION = "superior court division"
_COUNTY = re.compile(r"^(?:COUNTY\s+OF\s+[A-Z][A-Z\s.'-]*|[A-Z][A-Z\s.'-]*\s+COUNTY)$")
# '24CV010060-910' / '24CVS004823-640' / '24CV054 195-590' (one record's
# kerning opens a gap the extractor keeps). <yy>CV[S]<sequence>-<county
# code>: a Superior Court file number, which for this forum IS the docket.
_FILE_NO = re.compile(r"^(\d{2}\s?CVS?\s?\d[\d\s]*-\d{3})\.?$")
# 'Auto Provisions, LLC v. G1.34 Holdings, LLC, 2026 NCBC 40.' — the court's
# own public-domain cite, and the short case name that precedes it.
_CITE = re.compile(r"^(?P<name>.+?),\s*(?P<cite>\d{4}\s+NCBC\s+\d{1,3})\.?$")
# '[Public]' / '[Public]1' — the paper stating that THIS is the public
# version of an order first entered under seal.
_PUBLIC = re.compile(r"^\[(?:Public|Redacted|Sealed)\]\s*\d*$", re.I)
# 'SO ORDERED, this the 23rd day of April, 2026.' — the one place the paper
# states its own date, printed above the conformed signature on all 42.
# One record letter-spaces the decretal word ('S O ORDERED, this 8th day of
# July 2026.'), so the cue tolerates a space inside it.
_SO_ORDERED = re.compile(
    r"\bS\s?O\s+ORDERED\b.*?\bthis\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)"
    r"\s+day\s+of\s+([A-Z][a-z]+),?\s+(\d{4})")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# REPRESENTATION MARKS: verbs and labels, never a firm or a person's name.
# An italic row at the indent that carries none of these is not an
# appearance (chalk's block quotations are set the same way).
_APP_MARKS = (" by ", ", by ", "for plaintiff", "for defendant",
              "for the plaintiff", "for the defendant", "for plaintiffs",
              "for defendants", "for nominal", "for third-party",
              "for crossclaim", "for counterclaim", "pro se",
              "unrepresented", "for intervenor", "for movant",
              "for petitioner", "for respondent")
# THE PIVOT and the caption's own connective.
_PIVOT = re.compile(r"^v(?:s)?\.?$", re.I)
_CONNECTIVE = re.compile(r"^and$", re.I)
# A typed rule the court sets INSIDE the left column to divide the main
# action from a crossclaim action (moore_v_brooks).
_TYPED_RULE = re.compile(r"^_{6,}$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. This court's statuses are trial-court statuses, and it prints
# them at the end of the party or on rows of their own ('Plaintiffs and' /
# 'Counterclaim Defendants,').
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
    "petitioners", "respondent", "respondents", "intervenor", "intervenors",
    "movant", "movants", "counterclaimant", "counterclaimants",
    "counterclaim", "counterclaim-", "crossclaim", "cross-claim",
    "third-party", "nominal", "deceased", "decedent", "trustee",
    "co-trustee", "custodian", "executor", "guardian", "ad", "litem",
    "minor", "individually", "derivatively", "and", "et", "al", "a", "an",
    "the", "of", "on", "behalf", "unrepresented", "realigned",
    "substitute",
)
_TRAILING = re.compile(r"^(?P<head>.*),\s*(?P<tail>[^,]+?)[.,;]?\s*$")
# THE STATUS NOUNS. cadieu_tree_experts sets its status labels AT the caption
# rail instead of indented from it, so on that one record the label arrives
# as part of the party row and has to come off the tail of the joined
# statement ('… and JAKE CADIEU Third-Party Defendants.'). A trailing run of
# up to three status words is dropped only when one of them is a status
# NOUN — 'and', 'of' and 'the' are status vocabulary too, and a party whose
# name ends in one of those has not stated its status.
_STATUS_NOUNS = frozenset((
    "plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
    "petitioners", "respondent", "respondents", "intervenor", "intervenors",
    "movant", "movants", "counterclaimant", "counterclaimants",
    "counterclaim", "crossclaim", "cross-claim",
))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _join_wrap(rows: list) -> str:
    """Join a column's rows into the statement they are. A ROW THAT ENDS IN
    A HYPHEN ENDS IN THE COMPOUND'S OWN hyphen: this court breaks a wrapped
    party or firm name only where it already printed one ('ASHLEY-' /
    'NICOLE RUSSELL', 'DEANNE TOAL-' / 'BROTHERS', 'JESSIE RUIZ-' /
    'JACOBS'), never at a syllable, so the two halves close up. A double
    hyphen is a dash and keeps its space."""
    out = ""
    for row in rows:
        row = _norm(row)
        if not row:
            continue
        if not out:
            out = row
        elif out.endswith("-") and not out.endswith("--"):
            out = out + row
        else:
            out = out + " " + row
    return out


def _is_status(text: str) -> bool:
    bare = _norm(text).strip(".,;:/ ").lower()
    words = [w for w in re.split(r"[\s/,]+", bare) if w]
    return bool(words) and all(w.strip(".-") in _STATUS_WORDS for w in words)


def _strip_status(text: str) -> str:
    out = _norm(text)
    while True:
        mm = _TRAILING.match(out)
        if mm is None or not _is_status(mm.group("tail")):
            break
        out = mm.group("head")
    while True:
        words = out.split()
        for n in (3, 2, 1):
            tail = words[-n:]
            if len(words) <= n or not tail:
                continue
            if not all(w.strip(".,;:").lower() in _STATUS_WORDS
                       for w in tail):
                continue
            if not any(w.strip(".,;:").lower() in _STATUS_NOUNS
                       for w in tail):
                continue
            out = " ".join(words[:-n]).rstrip(" ,;")
            break
        else:
            break
    return out.rstrip(" ,;")


# --------------------------------------------------------------------------
# the page's own marks
# --------------------------------------------------------------------------

def _find_L(pm):
    """The drawn divider and the rule that closes it, or None.

    A vertical rect near the page's middle whose FOOT coincides with the
    END of a horizontal rect: an L. Returned with the head rule too, where
    the court draws the third side (1 record of 42)."""
    for v in sorted(pm.v_rules, key=lambda v: -v.height):
        if not (_DIV_X_MIN * pm.width <= v.x <= _DIV_X_MAX * pm.width):
            continue
        for h in pm.h_rules:
            if abs(h.top - v.bottom) > _L_FOOT_DY:
                continue
            if abs(h.x1 - v.x) > _L_FOOT_DX:
                continue
            if not (_CLOSE_W_MIN <= h.width <= _CLOSE_W_MAX):
                continue
            head = next((r for r in pm.h_rules
                         if abs(r.top - v.top) <= _L_FOOT_DY
                         and abs(r.x1 - v.x) <= _L_FOOT_DX
                         and _CLOSE_W_MIN <= r.width <= _CLOSE_W_MAX), None)
            return v, h, head
    return None


def _footnote_cut(pm, rail: float) -> float:
    """Where this page's footnotes begin — the top of the 144pt separator
    the court draws at the body rail."""
    tops = [r.top for r in pm.h_rules
            if _SEP_W[0] <= r.width <= _SEP_W[1]
            and abs(r.x0 - rail) <= _SEP_RAIL]
    return min(tops) if tops else float("inf")


def _rowgroups(lines):
    """The page's lines gathered into VISUAL ROWS. pdfio splits a row at
    column gaps and at the divider, so a row arrives in pieces and a third
    of a row is not a band."""
    groups: dict = {}
    order: list = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = line.row if line.row is not None else round(line.top)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ncbizct")
def read_headmatter_ncbizct(model, geom, **_):
    """Read the Business Court's county caption, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    found = _find_L(pm)
    if found is None:
        return NOTHING
    div, close, head_rule = found

    zone = [l for l in pm.lines if l.plain.strip() and l.top < close.top]
    if len(zone) < 8:
        return NOTHING
    rail = min(l.x0 for l in zone)          # measured INSIDE the band
    rows = _rowgroups(zone)

    def side(line) -> str:
        if line.x1 <= div.x + _SIDE_TOL:
            return "L"
        if line.x0 >= div.x - _SIDE_TOL:
            return "R"
        return "-"                          # straddles: not in a column

    def text(pieces) -> str:
        return _norm(" ".join(p.plain for p in pieces))

    # THE FOUR LANDMARKS, in order, each on its declared side of the drawn
    # divider. This is the dispatch; a paper that does not print them is
    # not this paper.
    i_state = i_div = i_file = None
    file_no = None
    for i, group in enumerate(rows):
        left = [p for p in group if side(p) == "L"]
        right = [p for p in group if side(p) == "R"]
        lt, rt = text(left).lower().rstrip("."), text(right)
        if i_state is None and lt == _STATE and rt.lower() == _GCJ:
            i_state = i
            continue
        if i_state is not None and i_div is None \
                and rt.lower().rstrip(".") == _DIVISION and not left:
            i_div = i
            continue
        if i_div is not None and i_file is None:
            mm = _FILE_NO.match(rt)
            if mm and _COUNTY.match(text(left).rstrip(". ")):
                i_file = i
                file_no = re.sub(r"\s+", "", mm.group(1))
                break
    if i_state is None or i_div is None or i_file is None:
        return NOTHING
    if not any(rows[j] for j in range(i_file + 1, len(rows))):
        return NOTHING                      # a caption with no parties

    ctx = _Ctx()

    # THE CITATION stands above the masthead, at the rail, and CROSSES the
    # divider — which is how we know it is not one of the two columns. Its
    # wrap (2 records) is joined into the one row the court means it to be.
    cite_rows = rows[:i_state]
    citation = short_name = None
    if cite_rows:
        joined = _norm(" ".join(text(g) for g in cite_rows))
        mm = _CITE.match(joined)
        if mm is not None:
            citation = _norm(mm.group("cite"))
            short_name = _norm(mm.group("name"))
        ctx.emit([p for g in cite_rows for p in g], "citation")

    # THE MASTHEAD BAND: the same two columns, an OPEN gutter (the court
    # draws nothing up here), the boundary taken from the drawn rule below.
    mast = _column_block(ctx, rows[i_state:i_file + 1], side, div, rail,
                         pm.number, rail_glyph=None,
                         left_role="court", right_role=("court", "docket"),
                         file_no=file_no)
    if mast is None:
        return NOTHING
    ctx.items.append(mast)

    # cadieu_tree_experts draws the third side of the box.
    if head_rule is not None:
        ctx.items.append(m.Rule(prov=m.Prov(pm.number), span="left"))

    # THE PARTY BAND: the same two columns with the DRAWN rail between
    # them — parties left, the paper's own name right.
    body = _column_block(ctx, rows[i_file + 1:], side, div, rail,
                         pm.number, rail_glyph="|",
                         left_role="caption", right_role=("title",),
                         file_no=None)
    if body is None:
        return NOTHING
    ctx.items.append(body)
    ctx.items.append(m.Rule(prov=m.Prov(pm.number), span="left"))

    # THE APPEARANCES. Read wherever the court sets them; CLAIMED only when
    # they stand directly under the closing rule, because everything below
    # the first prose row belongs to the writing.
    entries, claim = _appearances(model, rail, close.top)
    if claim:
        for entry in entries:
            ctx.emit([p for g in entry for p in g], "counsel")

    crit: dict = {"headmatter_style": STYLE_COUNTY,
                  "docket_number": file_no}
    if citation:
        crit["citation"] = citation
        # THE OPINION NUMBER IS THE PAPER'S OWN STATEMENT THAT IT IS
        # PUBLISHED. This court assigns a 'YYYY NCBC NN' number only to what
        # it publishes; its unpublished work is cited 'YYYY NCBC LEXIS NN'
        # (this corpus's own opinions cite it that way — 'Ehmann v. Medflow,
        # Inc., 2017 NCBC LEXIS 88'). So the printed number is a fact about
        # THIS paper, not an inference, and stating it also closes
        # core-patch-queue #10 here: core reads status out of prose, and
        # fs_med_supplies came back 'unpublished' from a parenthetical about
        # ANOTHER decision ('*3-4 (2019) (unpublished)') on page 2. The
        # pipeline only fills `publication_status` where the reader left it
        # unset, so declaring it is what stops the guess.
        crit["publication_status"] = "published"
    if short_name:
        crit["short_case_name"] = short_name
    crit["court"] = _norm(" ".join(
        text([p for p in g if side(p) == "R"])
        for g in rows[i_state:i_file]))
    caption = [text([p for p in g if side(p) == "L"])
               for g in rows[i_file + 1:]
               if any(side(p) == "L" for p in g)]
    caption = [c for c in caption if c]
    if caption:
        crit["caption"] = caption
    party_rows = [[(p.x0, _norm(p.plain)) for p in g if side(p) == "L"]
                  for g in rows[i_file + 1:]]
    _name(crit, [r for r in party_rows if r and any(t for _x, t in r)], rail)
    title = _join_wrap([
        text([p for p in g if side(p) == "R"
              and not _PUBLIC.match(p.plain.strip())])
        for g in rows[i_file + 1:]])
    doc_type = None
    if title:
        crit["title"] = title
        # THE PAPER NAMES ITSELF. 'ORDER AND OPINION …' / 'AMENDED ORDER AND
        # OPINION …' / 'AMENDED SECOND ORDER AND OPINION …' — the word that
        # names the instrument stands in the first three, after at most two
        # amendment words.
        _opening = [w.strip(",'’") for w in title.split()[:3]]
        doc_type = (m.DocType.ORDER if "ORDER" in _opening
                    else m.DocType.OPINION if "OPINION" in _opening
                    else None)
    if entries:
        crit["attorneys"] = _norm(" ".join(
            _join_wrap([text(g) for g in entry]) for entry in entries)
        )[:4000]
    date = _signature_date(model)
    if date:
        crit["decision_date"] = date
    return {"criteria": crit, "items": ctx.items, "attorneys": [],
            "dropped": ctx.dropped, "consumed": ctx.consumed,
            "anchor_ids": [], "doc_type_final": doc_type}


# --------------------------------------------------------------------------
# the two columns
# --------------------------------------------------------------------------

def _column_block(ctx, groups, side, div, rail, page, rail_glyph,
                  left_role, right_role, file_no):
    """One band of the caption as a CaptionBlock — TWO STACKS, not rows.

    Column membership is decided by which side of the DRAWN divider a piece
    sits on and by nothing else. The two columns are NOT row-paired: the
    left column is set on a 12.0pt leading and the right on 14.4pt, and
    only 57 of the corpus's 158 right-hand rows share a top with a
    left-hand one. Padding the short column to match would print 447 blank
    tinted rows across the corpus and claim a row-for-row correspondence
    the page does not set, so each column is flowed on its own (the
    convention wyo settled on for the same geometry)."""
    left: list = []
    right: list = []
    straddle = False
    for group in groups:
        l_cells = [p for p in group if side(p) == "L"]
        r_cells = [p for p in group if side(p) == "R"]
        if any(side(p) == "-" for p in group):
            straddle = True
        if l_cells:
            left.append(ctx.cell(l_cells, left_role, rail, page))
        if r_cells:
            r_text = _norm(" ".join(p.plain for p in r_cells))
            role = right_role[0]
            if file_no is not None and _FILE_NO.match(r_text):
                role = right_role[-1]
            elif _PUBLIC.match(r_text):
                role = "publication"
            right.append(ctx.cell(r_cells, role, div.x, page))
    if straddle or not (left and right):
        # A PIECE THAT SITS ON THE DIVIDER belongs to neither column, and a
        # band with only one column is not this court's two-column band.
        return None
    ids = tuple(sorted(p.id for g in groups for p in g))
    return m.CaptionBlock(
        left=left, right=right, rail=rail_glyph,
        rail_rows=max(len(left), len(right), 1), style_id=STYLE_COUNTY,
        fp={"rail": rail_glyph or "open", "mid_x": round(div.x, 1),
            "div_band": (round(div.top, 1), round(div.bottom, 1))},
        prov=m.Prov(page, ids))


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()

    def cell(self, pieces: list, role: str, rail: float, page: int):
        """One column cell — the row's pieces on this side of the divider,
        rejoined, with every line id they came from."""
        pieces = sorted(pieces, key=lambda p: p.x0)
        markup = ""
        for p in pieces:
            piece = line_markup(p)
            markup = piece if not markup.strip() \
                else markup.rstrip() + " " + piece.lstrip()
        self.consumed.update(p.id for p in pieces)
        first = pieces[0]
        return m.HmLine(
            text=markup, prov=m.Prov(first.page, tuple(p.id for p in pieces)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in pieces),
            italic=all(bool(p.all_emphasized) for p in pieces),
            rel=round(max(0.0, first.x0 - rail), 1), role=role)

    def emit(self, pieces: list, role: str):
        if not pieces:
            return
        pieces = sorted(pieces, key=lambda p: (p.top, p.x0))
        markup = ""
        for p in pieces:
            piece = line_markup(p)
            markup = piece if not markup.strip() \
                else markup.rstrip() + " " + piece.lstrip()
        first = pieces[0]
        self.items.append(m.HmLine(
            text=markup, prov=m.Prov(first.page, tuple(p.id for p in pieces)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in pieces),
            italic=all(bool(p.all_emphasized) for p in pieces),
            role=role))
        self.consumed.update(p.id for p in pieces)


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _name(crit: dict, rows: list, rail: float) -> None:
    """The parties, read off the left column's own rows and PIECES.

    Three geometric facts do all of the work, and no party name is ever read
    by wording:

      * A ROW'S LEADING PIECE NAMES THE ROW. The party statements stand at
        the caption rail; their STATUS labels stand 36-108pt in from it
        ('Plaintiffs and', 'Nominal Defendant.'). It has to be the LEADING
        piece, because pdfio splits a wide party row at its own gaps and
        cadieu's 'WIEDNER | F/N/A | STEPHANIE' would otherwise read as two
        statuses; the piece that opens the row is what says what the row is.

      * THE PIVOT IS THE PIVOT WHEREVER IT STANDS. This court sets 'v.' at
        the rail on 36 records and 35-40pt in on 6, and on 8 records it
        shares its baseline with the status label above the party below it
        ('v. ' at 75.1 beside 'Plaintiffs, ' at 183.1) — so the pivot is
        tested before the indent is, and the rest of its row is the status
        it sits beside.

      * A STATUS CLOSES ITS PARTY. The next statement at the rail is a NEW
        party group, which is what separates chalk's plaintiffs from its
        nominal plaintiffs without a connective between them. A group also
        ends at the caption's own standalone 'and' (a defendant and a
        nominal defendant) and at the typed underscore rule moore_v_brooks
        sets between two actions in one caption.

    The statement is joined FIRST and status-stripped ONCE: applied row by
    row the strip eats into a wrapped name — 'BRONSON, individually and' /
    'derivatively on behalf of' is a name's second and third lines, and the
    third is nothing but status vocabulary."""
    groups: list[list[str]] = [[]]
    pivot_at = None
    closed = False
    for row in rows:
        lead = row[0]
        text = _norm(" ".join(p for _x, p in row))
        lead_text = _norm(lead[1])
        if _TYPED_RULE.match(lead_text):
            groups.append([])
            closed = False
            continue
        if _PIVOT.match(lead_text.rstrip("*†‡ ")):
            if pivot_at is None:
                pivot_at = len(groups)
            groups.append([])
            closed = False
            continue
        if lead[0] - rail > _STATUS_IN:
            closed = True                   # a status label of its own
            continue
        if _CONNECTIVE.match(lead_text):
            groups.append([])
            closed = False
            continue
        if closed:
            groups.append([])
            closed = False
        groups[-1].append(text.rstrip("*†‡ "))
    named: list[str] = []
    right_first = None
    for i, g in enumerate(groups):
        if not g:
            continue
        value = _strip_status(_join_wrap(g))
        if not value:
            continue
        if pivot_at is not None and i >= pivot_at and right_first is None:
            right_first = len(named)
        named.append(value)
    if not named:
        return
    crit["parties"] = named
    if right_first:
        crit["case_name"] = f"{named[0]} v. {named[right_first]}"
    else:
        crit["case_name"] = named[0]


def _appearances(model, rail: float, close_top: float):
    """The appearance block, and whether it stands in the FRONT MATTER.

    Identified by type and position: all-italic, not bold, 18-80pt in from
    the caption rail. Bounded below by the first CENTRED BOLD row — the
    opinion's own first section heading — because past it the same setting
    is a block quotation. Returns (entries, claimable); ``claimable`` is
    True only where the block is the first thing under the closing rule."""
    entries: list[list] = []
    current: list = []
    first_after = None
    stop = False
    prev_top = prev_page = None
    for pm in model.pages[:_APP_PAGES]:
        if stop:
            break
        cut = _footnote_cut(pm, rail)
        for group in _rowgroups([l for l in pm.lines if l.top < cut]):
            if pm.number == 1 and group[0].top < close_top:
                continue
            if pm.number > 1 and group[0].top <= pm.height * _HEAD_BAND \
                    and len(group) == 1 and len(group[0].plain.strip()) <= 40:
                continue                    # a folio or a running head
            x0 = min(p.x0 for p in group)
            x1 = max(p.x1 for p in group)
            bold = all(p.all_bold for p in group)
            if bold and abs((x0 + x1) / 2 - pm.width / 2) <= _AXIS_TOL:
                stop = True                 # the first section heading
                break
            if first_after is None:
                first_after = (pm.number, group[0].top)
            italic = all(p.all_emphasized for p in group) and not bold
            if italic and _APP_IN_MIN <= x0 - rail <= _APP_IN_MAX:
                wrap = (prev_page == pm.number and prev_top is not None
                        and group[0].top - prev_top <= 20.0)
                if current and wrap:
                    current.append(group)
                else:
                    if current:
                        entries.append(current)
                    current = [group]
                prev_page, prev_top = pm.number, group[0].top
                continue
            if current:
                entries.append(current)
                current = []
            prev_page = prev_top = None
    if current:
        entries.append(current)
    # A run with no representation mark in it is not an appearance.
    entries = [e for e in entries
               if any(mk in _norm(" ".join(p.plain for g in e for p in g)).lower()
                      for mk in _APP_MARKS)]
    claim = bool(entries and first_after
                 and entries[0][0][0].page == first_after[0]
                 and abs(entries[0][0][0].top - first_after[1]) < 0.5)
    return entries, claim


def _signature_date(model) -> str | None:
    """'SO ORDERED, this the 23rd day of April, 2026.' — the last one in the
    document, which is the signature's. The line is READ, never claimed:
    it stands inside the writing and nothing is taken out of a writing."""
    out = None
    for pm in model.pages:
        for line in pm.lines:
            mm = _SO_ORDERED.search(_norm(line.plain))
            if mm and mm.group(2).lower() in _MONTHS:
                out = f"{mm.group(2)} {int(mm.group(1))}, {mm.group(3)}"
    return out
