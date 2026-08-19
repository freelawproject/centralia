"""Supreme Court of Rhode Island ('ri').

Everything unique to ri lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Rhode Island prints its identity at a RIGHT-HAND RAIL, sets
the caption in two columns divided by a stacked ':' , and ends the document
with the Clerk's COVER SHEET: a label/value grid fenced by drawn rules,
which is this court's ENDMATTER and not its headmatter.

An OPINION (36 of 50 records) fronts the paper with a cover page carrying
the Reporter's notice, and then REPRINTS the whole identity block on page 2
above the roster and the title:

    ┌─ page 1 ───────────────────────────────────────────────────────────┐
    │                                            Supreme Court   masthead│
    │                                            No. 2021-314-M.P. docket│
    │                                            (PM 00-4624)    below   │
    │                                            (Dissent begins on P 20)│
    │                Gary Tassone       :                                │
    │                       v.          :        the caption, two columns│
    │           State of Rhode Island.  :        divided by a ':' rail   │
    │                                                                    │
    │        NOTICE:  This opinion is subject to formal revision          │
    │        before publication in the Rhode Island Reporter. …   the     │
    │        … Email opinionanalyst@courts.ri.gov, of any …       notice, │
    │        … corrections may be made before the opinion is      EIGHT  │
    │        published.                                           rows   │
    ├─ page 2 ───────────────────────────────────────────────────────────┤
    │                                            Supreme Court           │
    │                                            No. 2021-314-M.P.       │
    │                                            (PM 00-4624)     the    │
    │                Gary Tassone       :                         SAME   │
    │                       v.          :                         block, │
    │           State of Rhode Island.  :                         again  │
    │ Present:  Suttell, C.J., Goldberg, Robinson, …  JJ.    the roster  │
    │                        O P I N I O N                   the title   │
    │ Justice Goldberg, for the Court.  The petitioner … the paper begins │
    ├─ last page ────────────────────────────────────────────────────────┤
    │                   STATE OF RHODE ISLAND                            │
    │                SUPREME COURT – CLERK'S OFFICE          the clerk's  │
    │                   Licht Judicial Complex …             own banner   │
    │                   OPINION COVER SHEET                              │
    │ ─────────────────────── drawn rule ───────────────────────────────  │
    │ Title of Case      Gary Tassone v. State of Rhode Island.          │
    │ ─────────────────────── drawn rule ───────────────────────────────  │
    │ Case Number        No. 2021-314-M.P.  /  (PM 00-4624)              │
    │ ─────────────────────── drawn rule ───────────────────────────────  │
    │ Date Opinion Filed March 19, 2026                                  │
    │ … Justices / Written By / Source of Appeal / Judicial Officer …     │
    │ … Attorney(s) on Appeal   For Petitioner: … ── For Respondent: …    │
    └────────────────────────────────────────────────────────────────────┘

An ORDER (14 of 50) prints no notice and no roster: page 1 runs masthead,
docket, caption, 'O R D E R', and then the prose.

THE NOTICE IS EIGHT ROWS, MEASURED ON ALL 36 OPINION RECORDS, every one of
them at x0=144.0 (the caption's own rows are elsewhere), opening 'NOTICE:
This opinion is subject to formal revision' and closing on its own sentence
— '… before the opinion is published.' Where the last line wraps early the
closing row reads 'corrections may be made before the opinion is published.'
(11 records) instead of 'made before the opinion is published.' (25). It is
the Reporter's standing request for corrections, not a word of the court's,
so it is DROPPED WHOLE, `kind="notice"`.

Core drops it only in HALF: `pipeline.py` groups the notice inside the
caption segment, its opening row carries the two cue words and the tail rows
carry one, and the adjacency rescue reunites the pieces on most records but
not all — on 16 of 50 the surviving tail ('typographical or other formal
errors in order that corrections may be…') opened a PHANTOM WRITING that
also swallowed the page-2 identity block. Dropping the run whole here is
what removes that phantom.

THE IDENTITY RAIL SAYS 'THIS CASE', THE CAPTION SAYS 'THESE PARTIES'.
Everything above the caption sits at one right-hand rail — measured x0 351.0
to 427.0 over the 50 records, always right of the 306pt page axis, and the
masthead sets it. Each row there is read by its OWN form, never by an
ordinal, because the rail carries between two and four rows:

  'Supreme Court'            the court naming itself      → court
  'No. 2024-104-C.A.'        the appeal's own number      → docket
  '(P1/22-3059BG)'           the number downstairs        → lower-court
  '(Dissent begins on Page 33)'  the Reporter's locator   → case-info

The last two are told apart by CASE, not by wording: a docket carries no run
of two lower-case letters ('(A.A. 22-213)', '(K1/16-229A)', '(No. 24-1040)',
'(KC 21-1031)' — 42 forms over the corpus); a locator always does ('begins',
'Page'). The locator wraps to a second row on state_v._isaiah_pinkerton
('(Concurrence and dissent' / 'begins on Page 30)'), which is why the rail's
rows are never counted.

THE CAPTION'S DIVIDER IS THE PARSER. The page stacks a ':' between the two
columns; the band it spans is the caption, what stands left of it is the
parties and what stands right of it is that party group's docket —
asa_s._davis (two consolidated appeals) prints 'No. 2024-10-M.P.' and 'No.
2024-87-M.P.' in the RIGHT column beside their own party groups, and no
docket at the rail at all. Column membership is decided by which side of the
divider a row sits on, never by what the row says.

pdfio returns the glyph three ways and all three are handled: as its own
line at the divider's x (48 records); glued to the END of the party row
('Travelers Property Casualty Company :' — roberge, brill, flynn); or, on
in_the_matter_of_joseph_molina_flynn, as the ONLY form on the record, so the
divider's x is read off that row's right edge.

A CAPTION ROW MAY WRAP BELOW THE LAST DIVIDER GLYPH. roberge's defendant
runs 'Travelers Property Casualty Company :' / 'of America.', and the wrap
carries no glyph — treating the last glyph as the band's floor closed the
caption one row early and left the notice below an unclaimed row. A row
entirely LEFT of the divider, within a single leading of the caption's last
row, is that row's wrap (the notice below it stands 80pt clear).

THE TITLE IS THE ANCHOR. 'O P I N I O N' (36 records) and 'O R D E R' (14)
are letter-spaced on the page axis and the court's prose begins on the row
below. The reader claims the title and reports its line ids as
`anchor_ids`, so that an unsigned order which can only open on that heading
gets it back rather than losing its writing.

AN UNRECOGNIZED ROW ENDS THE REGION — it is never skipped. A hole inside a
claim lets core open a writing on the unclaimed row and the bisection
invariant then pulls the claimed rows into it, which renders the headmatter
EMPTY. So the front walk stops at the first row it cannot name, and
everything below is core's.

THE COVER SHEET IS A RULED LABEL GRID, and the band is the unit of meaning.
Measured on all 50 records: nine full-measure drawn rules on the 36 opinion
covers and eight on the 14 order covers (x0 68.9, x1 538.8 or 550.6), each
fencing exactly ONE band, the label bold at x0=74.0 and the values at
x0=270.8 — 386 labels and 688 value rows over the corpus, every one of them
in one of those two columns and no third column used. The label NAMES the
band, and the vocabulary is the clerk's own form (SU-CMS-02A for an opinion,
02B for an order), invariant over the corpus: Title of Case, Case Number,
Date Opinion Filed / Date Order Filed, Justices, Written By (opinions only),
Source of Appeal, Judicial Officer from Lower Court, Attorney(s) on Appeal.
Every cover prints its whole set and nothing else — 36×8 + 14×7 = 386, which
is the label count exactly. A tenth, SHORT rule (x0 265.8, one per sheet)
divides the two appearances inside the attorneys band; it is drawn in the
value column only, and drawn as such.

THE LABEL IS NOT ON ITS VALUE'S ROW. The clerk sets each label CENTRED in
its band, so it lands level with whichever value row happens to be at the
band's middle: BELOW the first row of a two-row band ('No. 2024-396-Appeal.'
then 'Case Number' then '(KC 21-1031)'), and on 10 records below the short
rule that divides the appearances ('Attorney(s) on Appeal' beside 'For
Defendant:'). 45 of the 50 covers set at least one label off its value's
row, so pairing by row order reads the sheet wrong on 90% of the corpus.
The pairing is by COLUMN and by BAND — the label of a band is the row in the
label column between that band's fences, whatever it is level with, and the
short rule divides the value column only, never the band.

THE SHEET IS THE ENDMATTER. The clerk prints it BELOW every writing, on its
own last page, and `sections.py` declares `attorneys` (order 15) for counsel
a court prints below its writings — rendered with the headmatter's own
renderer, which is what a label/value grid needs. So the reader returns the
sheet as `attorneys`, not as headmatter items: one CaptionBlock per band,
the label in the left column and the band's value rows in the right, with
the page's own fences drawn between them. Read into the headmatter instead
(what this file did until 2026-08-19) the last page of the slip published
above the first page of the paper, interleaved with the caption it repeats.

'OPINION COVER SHEET' names THIS SHEET, not the document — the paper calls
itself 'O P I N I O N' on page 2 — so it is `case-info`, not `title`. The
clerk's letterhead above the first fence (STATE OF RHODE ISLAND / SUPREME
COURT – CLERK'S OFFICE / Licht Judicial Complex / 250 Benefit Street /
Providence, RI 02903) is KEPT, deliberately, as the endmatter's own heading:
it is what the page prints at the head of the sheet and it says who issued
it. The form number at its foot ('SU-CMS-02A (revised November 2022)') is
the Clerk's stationery, not the case's, and is dropped as a stamp — present
on 40 of the 50 covers, absent from the other 10.

Core already routes the cover page out of assembly (`pipeline.py`,
`_COVER_TITLES`, which names ri) and into the headmatter span. What this
reader adds is the READING of it — the panel, the date filed, the author,
the court below and its judge, and the appearances, each off its own band —
and its PLACEMENT, below the writings where the clerk printed it.

WHAT THE SHEET CONTRIBUTES TO THE CRITERIA, and nothing invented: Case
Number → `docket_number` / `other_dockets` / `lower_court_docket` (told
apart by form, as at the rail), Date Opinion|Order Filed →
`decision_date`, Justices → `judges` (as printed) and `panel` (parsed),
Title of Case → `case_name`, Source of Appeal → `lower_court`, Judicial
Officer from Lower Court → `lower_court_judge`, Attorney(s) on Appeal →
`attorneys`. 'N/A' is not a court and not a judge (the four attorney-
discipline matters print it), so it is rendered and not recorded. WRITTEN BY
HAS NO CRITERIA FIELD — `Criteria` has no author — so it renders with role
`author` and is reported, not smuggled in under another name.

ONE CORE DEFECT SHOWS THROUGH HERE, unchanged by this reader and REPORTED,
not patched: on 8 of the 50 records the cover sheet's first drawn fence
reads as a FOOTNOTE SEPARATOR, so every band below it is appended to the
last writing's last footnote (american_express, footnote 5: 'No.
2024-396-Appeal. Case Number (KC 21-1031) Date Opinion Filed …' — 19 of the
27 lines this reader claims on that page, published a second time). The
zones are measured in `pipeline.py` step 6, BEFORE the reader runs in step
8, and a claim is subtracted only from `segments_by_page`, never from
`zone_lines_by_page` — so no reader can take those lines back. Identical
with this file's decider popped, on the same 8 records: american_express,
asa_s._davis, estate_of_louis_campagnone, in_re_e.g.s, jay_patel_v._mancini,
robert_schmidt, the_providence_community_health_centers, william_fairhurst.
The fix belongs beside the subtraction that already exists, and is stated
here so it is not rediscovered:

    for _pg, _ls in list(zone_lines_by_page.items()):
        _keep = [l for l in _ls if l.id not in _claimed]
        if _keep:
            zone_lines_by_page[_pg] = _keep
        else:
            zone_lines_by_page.pop(_pg)
            zone_tops.pop(_pg, None)
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# ── the front region ──────────────────────────────────────────────────────
# The court names itself in two words and nothing else on the page does.
_MASTHEAD = re.compile(r"^Supreme Court$")
# 'No. 2024-396-Appeal.' / 'No. 2021-314-M.P.' / 'No. 2024-104-C.A.' — the
# three suffixes measured over the corpus (appeal, miscellaneous petition,
# criminal appeal). The number KEEPS its final period: stripping it as
# sentence punctuation also took the abbreviation's ('2021-314-M.P').
_DOCKET = re.compile(r"^No\.\s*(\d{4}-\d+-[A-Za-z.]+)$")
_PAREN = re.compile(r"^\((.+)\)$")
# A DOCKET CARRIES NO WORDS. Two consecutive lower-case letters separate the
# Reporter's locator ('(Dissent begins on Page 20)') from the number
# downstairs ('(P1/22-3059BG)', '(No. 24-1040)', '(A.A. 22-213)') — 42
# docket forms and 6 locator forms over the 50 records, no overlap.
_HAS_WORD = re.compile(r"[a-z]{2}")
_PIVOT = re.compile(r"^v\.?$")
# 'Present:  Suttell, C.J., Goldberg, Robinson, Lynch Prata, and Long, JJ.'
# — one row on all 36 opinion records, never wrapped, and always the row
# above the title.
_PRESENT = re.compile(r"^Present:\s*(.*)$", re.I)
_NOTICE_OPEN = re.compile(r"^NOTICE\b", re.I)
# THE NOTICE CLOSES ON ITS OWN SENTENCE, not on a row count (8 rows on all
# 36 records today, and the size gives no signal — the notice is set in the
# body's own 14pt).
_NOTICE_CLOSE = re.compile(r"opinion is published\.\s*$", re.I)
_NOTICE_MAX = 14
# The paper's own name, letter-spaced on the page axis.
_TITLES = {"OPINION", "ORDER"}
# The divider glyph the page stacks between the caption's columns.
_RAIL = ":"
# THE IDENTITY RAIL is right of the page axis on every record (masthead x0
# 351.0-427.0 on a 612pt page); the caption's left column never reaches it.
_RAIL_MIN_FRAC = 0.55
# A caption row's wrap is one leading below its own row; the notice below
# the caption stands 80pt clear (roberge: 268.6 → 284.6 wrap, 365.2 notice).
_WRAP_GAP_MAX = 24.0
# BENCH WORDS are a closed vocabulary: what is left of a roster row after
# the titles are removed is the people.
_BENCH = {"c.j.", "c.j", "j.", "j", "jj.", "jj", "cj.", "cj", "c. j."}

# ── the cover sheet ───────────────────────────────────────────────────────
_COVER_TITLE = re.compile(r"^(?:OPINION|ORDER) COVER SHEET$")
# The clerk's own banner, above the first fence.
_CLERK = ("STATE OF RHODE ISLAND", "SUPREME COURT", "LICHT JUDICIAL",
          "250 BENEFIT STREET", "PROVIDENCE, RI")
# The Clerk's stationery number at the foot of the sheet.
_FORM = re.compile(r"^SU-CMS-\d+[A-Z]?\s*\(revised", re.I)
_LABEL_X0 = 74.0
_VALUE_X0 = 270.8
_COL_TOL = 4.0
# A FENCE IS FULL MEASURE (x0 68.9 on all 50 covers); a rule that starts
# right of this is drawn in the value column only and fences nothing.
_FENCE_X_FRAC = 0.2
# THE LABEL NAMES THE BAND. The clerk's form prints these eight and no
# others (measured: all 50 covers; 'Written By' and 'Date Opinion Filed'
# only on the 36 opinions, 'Date Order Filed' only on the 14 orders).
_BANDS = {
    "title of case": "caption",
    "case number": "docket",
    "date opinion filed": "date",
    "date order filed": "date",
    "justices": "panel",
    "written by": "author",
    "source of appeal": "lower-court",
    "judicial officer from lower court": "lower-court",
    "attorney(s) on appeal": "counsel",
}

# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the appeal's number is
# `docket_number` (a string) plus `other_dockets`, the number downstairs is
# `lower_court_docket` (a list), and a date the court heard the case belongs
# in `submitted`. Written under any other name they are attached by setattr
# and never serialize.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="ri")
def read_headmatter_ri(model, geom, **_):
    """Read Rhode Island's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE DISPATCH: the court's own two-word masthead, at the identity rail,
    # in the top band of page 1. No masthead, no contract — and the cover
    # sheet alone is not this paper.
    page1 = model.pages[0]
    rows1 = _rows(page1, finder)
    if _masthead_at(rows1, page1) is None:
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    for pm in model.pages[:2]:
        rows = _rows(pm, finder)
        mast = _masthead_at(rows, pm)
        if mast is None:
            # Page 2 does not reprint the block: the front region was page 1
            # (every order record).
            break
        # THE BLOCK IS PRINTED TWICE and it is the same caption both times:
        # the rows are reproduced from both pages, the criterion is taken
        # from the first page that carried it.
        page_caption: list[str] = []
        ended = _front_page(ctx, pm, rows, mast, page_caption)
        if not caption:
            caption = page_caption
        if ended:
            break                       # the title: the paper begins

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("caption", caption)
        parties = [t for t in caption if not _PIVOT.match(t)]
        if parties:
            ctx.crit.setdefault("parties", parties)
            ctx.crit.setdefault("case_name", " v. ".join(parties[:2])
                                if len(parties) >= 2 else parties[0])

    # THE CLERK'S COVER SHEET, which names itself. Core keeps this page out
    # of assembly already; the reading of it is this file's.
    for pm in model.pages:
        if _is_cover(pm):
            _cover_sheet(ctx, pm, finder)
            break

    # THE ROSTER, parsed once, from the cleanest of the two places the paper
    # prints it.
    roster = ctx.roster.get("justices") or ctx.roster.get("present") or ""
    if roster:
        ctx.crit.setdefault("panel_line", _norm(roster))
        # `judges` is the roster AS A STRING — the field the casebody
        # exports as <judges>. `panel` is the same fact parsed into people
        # and `panel_line` is the row as the front page printed it; the
        # cover sheet's copy is the clean one (page 2 of gary_tassone breaks
        # a glyph pair and prints 'Sutte ll').
        ctx.crit.setdefault("judges", _norm(roster))
        panel = _people(roster)
        if panel:
            ctx.crit["panel"] = panel
    ctx.crit.setdefault("court", "Supreme Court of Rhode Island")
    ctx.crit["headmatter_style"] = "rail, colon caption and cover sheet"
    return ctx.result()


# ── the front region ──────────────────────────────────────────────────────

def _masthead_at(rows: list[list], pm) -> int | None:
    """The index of the masthead row, or None. It stands in the first three
    rows of the page and right of the page axis — 'Supreme Court' also
    occurs in the Clerk's banner, centred, which is a different thing."""
    for idx, group in enumerate(rows[:3]):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD.match(text) \
                and min(l.x0 for l in group) >= pm.width * _RAIL_MIN_FRAC:
            return idx
    return None


def _front_page(ctx, pm, rows: list[list], mast: int,
                caption: list[str]) -> bool:
    """Walk one front page. True when the paper's own title was reached."""
    rail_x, band_top, band_bot = _rail_of(rows, pm)
    left: list = []
    right: list = []
    box_ids: set[int] = set()
    ended = False
    idx = mast
    while idx < len(rows):
        pieces = sorted(rows[idx], key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            idx += 1
            continue
        top = min(l.top for l in pieces)

        # THE NOTICE, dropped whole — a run, closing on its own sentence.
        if _NOTICE_OPEN.match(text):
            idx = _drop_notice(ctx, rows, idx)
            continue
        # THE CAPTION: the band the divider spans, plus a wrap immediately
        # below it that carries no glyph.
        if rail_x is not None and (
                band_top - 1.0 <= top <= band_bot + 1.0
                or (left and top - band_bot <= _WRAP_GAP_MAX
                    and max(l.x1 for l in pieces) <= rail_x + 2.0
                    and not _landmark(text))):
            _cap_row(ctx, pieces, rail_x, left, right, caption)
            box_ids.update(l.id for l in pieces)
            band_bot = max(band_bot, top)
            idx += 1
            continue
        if _MASTHEAD.match(text):
            ctx.emit(pieces, "court", align=m.Align.RIGHT)
            idx += 1
            continue
        docket = _DOCKET.match(text)
        if docket:
            _add_docket(ctx, _norm(docket.group(1)))
            ctx.emit(pieces, "docket", align=m.Align.RIGHT)
            idx += 1
            continue
        # THE RAIL'S PARENTHETICAL MAY WRAP: state_v._isaiah_pinkerton sets
        # '(Concurrence and dissent' / 'begins on Page 30)' as two rows, and
        # the second closes the first. Read as one row, or the walk ends on
        # a row it cannot name and the notice below it stays for core.
        if text.startswith("(") and not text.endswith(")"):
            pieces, text, idx = _paren_run(rows, idx, pm)
        paren = _PAREN.match(text)
        if paren:
            # A NUMBER OR A LOCATOR — told apart by case, not by wording.
            if _HAS_WORD.search(paren.group(1)):
                ctx.emit(pieces, "case-info", align=m.Align.RIGHT)
            else:
                _add_lower(ctx, _norm(paren.group(1)))
                ctx.emit(pieces, "lower-court", align=m.Align.RIGHT)
            idx += 1
            continue
        present = _PRESENT.match(text)
        if present:
            # THE PRINTED FORM AND THE PARSED FORM ARE BOTH FACTS, and the
            # roster is printed twice — here and in the cover sheet's
            # 'Justices' band. The parse is taken from ONE of them (the
            # cover sheet, which is set clean; page 2 of gary_tassone breaks
            # a glyph pair and prints 'Sutte ll').
            ctx.crit.setdefault("panel_line", text)
            ctx.roster.setdefault("present", present.group(1))
            ctx.emit(pieces, "panel")
            idx += 1
            continue
        if text.replace(" ", "").upper() in _TITLES:
            ctx.crit.setdefault("title", text.replace(" ", "").upper())
            ctx.emit(pieces, "title", align=m.Align.CENTER)
            ctx.anchor.update(l.id for l in pieces)
            ended = True
            break
        # AN UNRECOGNIZED ROW ENDS THE REGION. Skipping it would leave a
        # hole in the claim, and a hole is what lets core open a writing
        # inside the headmatter.
        break

    # THE CAPTION BLOCK, placed where the page prints it.
    if left:
        while left and not _text_of(left[-1]) and not _text_of(right[-1]):
            left.pop()
            right.pop()
        # THE RIGHT COLUMN IS UNUSED ON 49 OF 50 RECORDS — the page draws the
        # divider and sets nothing beyond it. An empty cell is not a row of
        # the paper, so an all-empty column is dropped rather than rendered
        # as a stack of blanks (and counted as rows nobody read). Where the
        # page DOES use it the pairs are kept, so the columns stay level.
        if not any(_text_of(r) for r in right):
            right = []
        ctx.items.append(m.CaptionBlock(
            left=left, right=right, rail=_RAIL, rail_rows=len(left),
            style_id="colon-rail",
            fp={"rail": _RAIL, "mid_x": round(rail_x or 0.0, 1)},
            prov=m.Prov(pm.number, tuple(sorted(box_ids)))))
        ctx.consumed.update(box_ids)
    return ended


def _rail_of(rows: list[list], pm):
    """The divider's x and the band it spans, or (None, 0, 0).

    Read off the DRAWN glyph three ways: as its own line, glued to the end
    of a party row, or — on joseph_molina_flynn, the only record with no
    bare glyph at all — off the right edge of the row that carries it."""
    # THE CAPTION CANNOT REACH PAST THE PAPER'S OWN TITLE. Bounding the
    # search matters because prose ends in a colon too: page 2 of
    # cynthia_a._roberge sets 'Rules of Appellate Procedure:' inside the
    # majority's first paragraph, and read as a welded divider it dragged
    # the roster, the title and the byline into the caption — 'a mis-tagged
    # row is worse than an untagged one', and this one cost the writing its
    # author.
    zone = rows
    for i, g in enumerate(rows):
        text = _norm(" ".join(l.plain for l in g))
        if _NOTICE_OPEN.match(text) or _PRESENT.match(text) \
                or text.replace(" ", "").upper() in _TITLES:
            zone = rows[:i]
            break
    bare = [l for g in zone for l in g if _norm(l.plain) == _RAIL]
    if bare:
        rail_x = min(l.x0 for l in bare)
    else:
        rail_x = None
    # …and a welded glyph must stand in the divider's OWN column.
    welded = []
    for g in zone:
        text = _norm(" ".join(l.plain for l in g))
        if not text.endswith(_RAIL) or any(_norm(l.plain) == _RAIL for l in g):
            continue
        edge = max(l.x1 for l in g)
        if rail_x is None:
            if not pm.width * 0.45 <= edge <= pm.width * 0.60:
                continue                # in_the_matter_of_joseph_molina_flynn
            rail_x = edge - 6.0         # is the only record with no bare glyph
        elif abs(edge - rail_x) > 24.0:
            continue
        welded.append(g)
    if rail_x is None or rail_x < pm.width * 0.3:
        return None, 0.0, 0.0
    tops = [l.top for l in bare] + [min(l.top for l in g) for g in welded]
    return rail_x, min(tops), max(tops)


def _cap_row(ctx, pieces, rail_x, left, right, caption) -> None:
    """ONE PRINTED ROW, TWO STACKS — split at the divider, which belongs to
    neither column. Both sides keep their place even when one is blank, so
    the pairs stay level in the grid (ca6's rule)."""
    l_parts = [l for l in pieces
               if l.x0 < rail_x - 1.5 and _norm(l.plain) != _RAIL]
    r_parts = [l for l in pieces
               if l.x0 >= rail_x - 1.5 and _norm(l.plain) != _RAIL]
    left.append(_row(l_parts, "caption"))
    text = _strip_rail(_norm(" ".join(l.plain for l in l_parts)))
    if text:
        caption.append(text)
    # THE RIGHT COLUMN IS THE CASE'S OWN NUMBERS, where the page uses it at
    # all: a consolidated record sets each appeal's docket beside its party
    # group (asa_s._davis) instead of at the identity rail. Read by form.
    r_text = _strip_rail(_norm(" ".join(l.plain for l in r_parts)))
    role = "caption"
    if r_text:
        docket = _DOCKET.match(r_text)
        paren = _PAREN.match(r_text)
        if docket:
            _add_docket(ctx, _norm(docket.group(1)))
            role = "docket"
        elif paren and not _HAS_WORD.search(paren.group(1)):
            _add_lower(ctx, _norm(paren.group(1)))
            role = "lower-court"
        elif paren:
            role = "case-info"
        else:
            role = ""                   # a cell at no position this paper
            #                             uses — left untagged, not guessed
    right.append(_row(r_parts, role))


def _strip_rail(text: str) -> str:
    """The glyph off whichever side pdfio glued it to. It is the drawn
    divider, not a word of either column."""
    return text.strip().rstrip(_RAIL).strip()


def _drop_notice(ctx, rows: list[list], idx: int) -> int:
    """THE NOTICE IS A RUN and it closes on its own sentence."""
    run: list = []
    stop = idx
    for j in range(idx, min(idx + _NOTICE_MAX, len(rows))):
        pieces = sorted(rows[j], key=lambda l: l.x0)
        run.extend(pieces)
        stop = j + 1
        if _NOTICE_CLOSE.search(_norm(" ".join(l.plain for l in pieces))):
            break
    ctx.drop(run, "notice")
    return stop


def _paren_run(rows: list[list], idx: int, pm):
    """A parenthetical at the identity rail, however many rows it takes.
    Bounded twice: the rows must stay at the RAIL (right of 0.55 of the
    measure, where nothing else on the page stands) and the run ends on the
    row that closes the bracket."""
    pieces = sorted(rows[idx], key=lambda l: l.x0)
    last = idx
    for j in range(idx + 1, len(rows)):
        nxt = sorted(rows[j], key=lambda l: l.x0)
        if min(l.x0 for l in nxt) < pm.width * _RAIL_MIN_FRAC:
            break
        pieces = pieces + nxt
        last = j
        if _norm(" ".join(l.plain for l in nxt)).endswith(")"):
            break
    return pieces, _norm(" ".join(l.plain for l in pieces)), last


def _landmark(text: str) -> bool:
    """A row the front walk reads as something OTHER than the caption."""
    return bool(_MASTHEAD.match(text) or _DOCKET.match(text)
                or _PAREN.match(text) or _PRESENT.match(text)
                or _NOTICE_OPEN.match(text)
                or text.replace(" ", "").upper() in _TITLES)


def _add_docket(ctx, number: str) -> None:
    """The first number is the docket; a consolidated record's companions
    are `other_dockets` (asa_s._davis prints two, in the caption's right
    column). The identity block is printed on two pages, so every number
    arrives twice — the second sighting is the same fact, not another one."""
    crit = ctx.crit
    if not crit.get("docket_number"):
        crit["docket_number"] = number
    elif number != crit["docket_number"] \
            and number not in crit.setdefault("other_dockets", []):
        crit["other_dockets"].append(number)


def _add_lower(ctx, number: str) -> None:
    """The number the court BELOW gave the case — `lower_court_docket`, not
    `other_dockets`, which is companion APPEALS."""
    below = ctx.crit.setdefault("lower_court_docket", [])
    if number not in below:
        below.append(number)


def _people(text: str) -> list[str]:
    """The roster's people: what is left when the BENCH WORDS come off.
    'Suttell, C.J., Goldberg, Robinson, Lynch Prata, and Long, JJ.' is five
    justices, not seven comma-separated tokens."""
    out: list[str] = []
    for piece in text.replace(" and ", ", ").split(","):
        one = _norm(piece).strip()
        if one.lower().startswith("and "):
            one = one[4:].strip()
        bare = one.rstrip(".")
        if not one or one.lower() in _BENCH or bare.lower() in _BENCH \
                or one.lower() == "and":
            continue
        if bare not in out:
            out.append(bare)
    return out


# ── the cover sheet ───────────────────────────────────────────────────────

def _is_cover(pm) -> bool:
    """The sheet NAMES ITSELF in its own heading — the same test core uses
    to keep the page out of assembly."""
    first = sorted((l for l in pm.lines if l.plain.strip()),
                   key=lambda l: l.top)[:6]
    return any(_COVER_TITLE.match(_norm(l.plain)) for l in first)


def _cover_sheet(ctx, pm, finder) -> None:
    """THE BAND IS THE UNIT OF MEANING: the drawn full-measure fences cut
    the sheet into bands, each holding exactly ONE label, and the label
    names the band.

    THE LABEL IS NOT ON ITS VALUE'S ROW. The clerk sets the label CENTRED in
    its band, so it lands level with whatever value row happens to be at the
    band's middle — under the first value row on a two-row band ('No.
    2024-396-Appeal.' / 'Case Number' / '(KC 21-1031)'), and on 10 records
    below the SHORT rule that divides the two appearances. Measured over the
    50 covers: 45 records set at least one label off its value's row. So the
    pairing is by COLUMN (label x0 74.0, value x0 270.8, invariant on all
    688 value rows and all 386 labels) and by BAND, never by row order.

    The sheet is emitted as ENDMATTER — one CaptionBlock per band, the label
    in the left column and the band's value rows in the right, with the
    page's own fences drawn between them. It is not headmatter: the clerk
    prints it BELOW every writing, on its own last page, and `sections.py`
    renders `attorneys` there.
    """
    fences = sorted(r.top for r in pm.h_rules
                    if r.x0 < pm.width * _FENCE_X_FRAC)
    if not fences:
        return
    # THE SHORT RULE (x0 265.8, one per sheet on all 50 covers) is drawn in
    # the VALUE COLUMN ONLY: it divides the two appearances inside the
    # attorneys band and fences no band of its own.
    shorts = sorted(r.top for r in pm.h_rules
                    if r.x0 >= pm.width * _FENCE_X_FRAC)
    head: dict[float, list] = {}
    label: dict[int, list] = {}
    value: dict[int, dict[float, list]] = {}
    stray: dict[int, dict[float, list]] = {}
    for line in sorted((l for l in pm.lines if l.plain.strip()),
                       key=lambda l: (l.top, l.x0)):
        if finder.kind(pm, line):
            continue
        if _FORM.match(_norm(line.plain)):
            ctx.drop([line], "stamp")   # the Clerk's stationery number
            continue
        band = _band_of(line.top, fences)
        if band == 0:
            head.setdefault(round(line.top, 1), []).append(line)
        elif abs(line.x0 - _LABEL_X0) <= _COL_TOL:
            label.setdefault(band, []).append(line)
        elif abs(line.x0 - _VALUE_X0) <= _COL_TOL:
            value.setdefault(band, {}).setdefault(
                round(line.top, 1), []).append(line)
        else:
            # A CELL AT NO COLUMN THIS FORM USES. Claimed and placed — an
            # unclaimed row inside the sheet is a hole, and a hole is what
            # lets core read the grid as prose — but left UNTAGGED, which is
            # the honest measurement. None on the 50 records today.
            stray.setdefault(band, {}).setdefault(
                round(line.top, 1), []).append(line)

    # ABOVE THE FIRST FENCE: the clerk's own letterhead and the sheet's
    # name. KEPT, deliberately, as the endmatter's own heading — they are
    # what the page prints at the head of the sheet and they say who issued
    # it (the stationery number at its foot is the form's, and is dropped).
    # 'OPINION COVER SHEET' names THIS SHEET, not the document — the paper
    # calls itself 'O P I N I O N' on page 2 — so it is `case-info`, never
    # `title`.
    for top in sorted(head):
        pieces = sorted(head[top], key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        role = "case-info" if _COVER_TITLE.match(text) else \
            ("court" if text.upper().startswith(_CLERK) else "")
        ctx.emit(pieces, role, align=m.Align.CENTER, into=ctx.end)

    # THE BANDS, top to bottom, each under the fence the page draws above
    # it. The band below the LAST fence holds only the form number, so that
    # fence renders as the rule that closes the sheet.
    for band in range(1, len(fences) + 1):
        ctx.end.append(m.Rule(prov=m.Prov(pm.number)))
        # the band's rows IN THE PAGE'S ORDER, whichever column they came
        # from: a stray cell appended after the values would publish the
        # band out of the order the clerk set it in.
        by_top: dict = {}
        for src in (value.get(band) or {}, stray.get(band) or {}):
            for top, ls in src.items():
                by_top.setdefault(top, []).extend(ls)
        rows = [sorted(by_top[t], key=lambda l: l.x0) for t in sorted(by_top)]
        if not rows:
            continue
        name = _norm(" ".join(l.plain for l in label.get(band, []))).lower()
        role = _BANDS.get(name)
        top_edge = fences[band - 1]
        bot_edge = fences[band] if band < len(fences) else None
        cuts = [s for s in shorts if s > top_edge
                and (bot_edge is None or s < bot_edge)]
        first = True
        for sub in _sub_bands(rows, cuts):
            if not first:
                # the short rule, drawn where the page draws it: in the
                # value column only.
                ctx.end.append(m.Rule(prov=m.Prov(pm.number), span="right"))
            _cover_band(ctx, pm, label.get(band, []) if first else [],
                        sub, role or "", name)
            first = False


def _sub_bands(rows: list[list], cuts: list[float]) -> list[list[list]]:
    """The band's value rows, split where the SHORT rule divides them. The
    label belongs to the BAND, so it stays with the first part however the
    value column is divided (10 records set 'Attorney(s) on Appeal' below
    the rule that separates the two appearances)."""
    out: list[list[list]] = [[]]
    for row in rows:
        top = min(l.top for l in row)
        while cuts and cuts[0] < top:
            cuts = cuts[1:]
            if out[-1]:
                out.append([])
        out[-1].append(row)
    return [part for part in out if part]


def _cover_band(ctx, pm, label: list, rows: list[list], role: str,
                name: str) -> None:
    """One band of the grid: the label in the left column, the band's value
    rows in the right. The VALUES carry the criteria; the label carries only
    the name of the band.

    ONE LABEL, N VALUE ROWS — and the two columns of a CaptionBlock are two
    STACKS, not table rows, so the band needs no padding cells to stay
    level: the label heads its column and the values fill theirs. Padding
    them level would publish 302 empty rows over the corpus that no reader
    can tag, which reads as unread headmatter and is not what an empty cell
    means here.
    """
    left: list = []
    right: list = []
    ids: set[int] = set()
    if label:
        left.append(_row(label, role, strip=False))
        ids.update(l.id for l in label)
    for row in rows:
        right.append(_row(row, _cover_value(ctx, row, role, name),
                          strip=False))
        ids.update(l.id for l in row)
    ctx.end.append(m.CaptionBlock(
        left=left, right=right, rail=None, rail_rows=0,
        style_id="cover-grid",
        fp={"label_x0": _LABEL_X0, "value_x0": _VALUE_X0},
        prov=m.Prov(pm.number, tuple(sorted(ids)))))
    ctx.consumed.update(ids)


def _cover_value(ctx, row: list, role: str, name: str) -> str:
    """ONE VALUE ROW: the criterion it carries, and the role it renders as.
    A band's rows are not all the same thing — the 'Case Number' band sets
    the appeal's own number on one row and the number downstairs on the
    next — so the role is decided per row, inside the band the label named.
    """
    value = _norm(" ".join(l.plain for l in row))
    if not value:
        return ""
    if role == "docket":
        paren = _PAREN.match(value)
        if paren and not _HAS_WORD.search(paren.group(1)):
            _add_lower(ctx, _norm(paren.group(1)))
            return "lower-court"
        docket = _DOCKET.match(value)
        if docket:
            _add_docket(ctx, _norm(docket.group(1)))
        return "docket"
    if role == "caption":
        # THE TITLE OF CASE WRAPS, and on a consolidated record the band
        # holds TWO of them (asa_s._davis) — the rows are joined, never
        # replaced, or the criterion keeps only the last line printed
        # ('Company of America.' on cynthia_a._roberge).
        # (accumulated OUTSIDE `crit`: an undeclared criteria key is
        # attached by setattr and never serializes.)
        ctx.roster["title"] = _norm(ctx.roster.get("title", "") + " " + value)
        ctx.crit["case_name"] = ctx.roster["title"]
    elif role == "date":
        ctx.crit.setdefault("decision_date", value)
    elif role == "panel":
        # THE BAND'S VALUE WRAPS ('… Lynch Prata, and' / 'Long, JJ.'), so
        # the roster is parsed once the whole band is in — parsed per row it
        # yields a justice called 'and'.
        ctx.roster["justices"] = _norm(
            ctx.roster.get("justices", "") + " " + value)
    elif role == "lower-court" and value.upper() != "N/A":
        key = "lower_court_judge" if name.startswith("judicial") \
            else "lower_court"
        ctx.crit.setdefault(key, value)
    elif role == "counsel":
        ctx.crit["attorneys"] = _norm(
            (ctx.crit.get("attorneys") or "") + " " + value)[:4000]
    return role


def _band_of(top: float, fences: list[float]) -> int:
    return sum(1 for f in fences if f < top)


# ── the emit buffer ───────────────────────────────────────────────────────

def _rows(pm, finder) -> list[list]:
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


def _text_of(row) -> str:
    return _norm(getattr(row, "text", "") or "")


def _row(parts: list, role: str, strip: bool = True) -> m.HmLine:
    """One column's cell of a two-column row — an HmLine that is NOT emitted
    into the flow: the CaptionBlock carries it.

    `strip` takes the caption's rail glyph off the cell. It is OFF for the
    cover sheet, whose own values end in a colon the page means: stripped,
    'For Plaintiff:' publishes as 'For Plaintiff'."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(1), role="")
    first = parts[0]
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
            else piece
    return m.HmLine(text=_strip_rail(text) if strip else text.strip(),
                    prov=m.Prov(first.page, tuple(p.id for p in parts)),
                    align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
                    bold=all(bool(p.all_bold) for p in parts), role=role)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        # THE ENDMATTER: what the clerk prints BELOW every writing. Its own
        # list, because it is its own section (`sections.py`, order 15) and
        # merging it into the headmatter's would publish the last page of
        # the slip above the first page of the paper.
        self.end: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: set[int] = set()
        self.roster: dict = {}
        self.crit: dict = {}

    def emit(self, group: list, role: str, align=m.Align.LEFT,
             into: list | None = None) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        dest = self.items if into is None else into
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        dest.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: (l.top, l.x0))
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:1200],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.end,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": sorted(self.anchor), "doc_type_final": None}
