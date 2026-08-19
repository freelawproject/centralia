"""Supreme Court of Rhode Island ('ri').

Everything unique to ri lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Rhode Island prints its identity at a RIGHT-HAND RAIL, sets
the caption in two columns divided by a stacked ':' , and ends the document
with the Clerk's COVER SHEET: a label/value grid fenced by drawn rules.

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
covers and eight on the 14 order covers (x0 69.0, x1 539.0 or 551.0), each
fencing exactly ONE band, the label bold at x0=74.0 and the values at
x0=270.8. The label NAMES the band, and the vocabulary is the clerk's own
form (SU-CMS-02A for an opinion, 02B for an order), invariant over the
corpus: Title of Case, Case Number, Date Opinion Filed / Date Order Filed,
Justices, Written By (opinions only), Source of Appeal, Judicial Officer
from Lower Court, Attorney(s) on Appeal. A tenth, SHORT rule (x0 266.0)
divides the two appearances inside the attorneys band; it is drawn in the
value column only, and drawn as such.

'OPINION COVER SHEET' names THIS SHEET, not the document — the paper calls
itself 'O P I N I O N' on page 2 — so it is `case-info`, not `title`. The
form number at the foot ('SU-CMS-02A (revised November 2022)') is the
Clerk's stationery and is dropped.

Core already routes the cover page out of assembly and into the headmatter
(`pipeline.py`, `_COVER_TITLES`, which names ri). What this reader adds is
the READING of it: the panel, the date filed, the author, the court below
and its judge, and the appearances, each off its own band.

ONE CORE DEFECT SHOWS THROUGH HERE, unchanged by this reader and REPORTED,
not patched: on 7 of the 50 records the cover sheet's first drawn fence
reads as a FOOTNOTE SEPARATOR, so the bands below it are appended to the
last writing's last footnote (american_express, footnote 5: 'No.
2024-396-Appeal. Case Number (KC 21-1031) Date Opinion Filed …'). The
footnote zones are measured in `pipeline.py` before any reader runs and a
claim is subtracted only from `segments_by_page`, so no reader can take
those lines back — identical with this file's decider popped. Consequence
worth knowing: on those 7 records the affected bands render twice, once
tagged here and once inside that footnote.
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
    """THE BAND IS THE UNIT OF MEANING: the drawn fences cut the sheet into
    bands, each holding exactly one label, and the label names the band."""
    fences = sorted(r.top for r in pm.h_rules if r.x0 < pm.width * 0.2)
    # THE SHORT RULE (x0 266.0, measured on all 50 covers) divides the two
    # appearances inside the attorneys band: it is drawn in the value column
    # only, so it fences nothing.
    drawn = sorted([(t, "full") for t in fences]
                   + [(r.top, "right") for r in pm.h_rules
                      if r.x0 >= pm.width * 0.2])
    if not fences:
        return
    rows = _rows(pm, finder)
    # the label of each band, by the band's index
    labels: dict[int, str] = {}
    for group in rows:
        for line in group:
            text = _norm(line.plain)
            if abs(line.x0 - _LABEL_X0) <= _COL_TOL and not _FORM.match(text):
                labels[_band_of(line.top, fences)] = text.lower()
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        # A DRAWN RULE ABOVE THIS ROW, drawn before it. An item with no line
        # provenance inherits the position of the row AFTER it (pipeline's
        # headmatter sort), so a rule emitted here lands where it is drawn.
        while drawn and drawn[0][0] < min(l.top for l in pieces):
            ctx.items.append(m.Rule(prov=m.Prov(pm.number),
                                    span=drawn.pop(0)[1]))
        if _FORM.match(text):
            ctx.drop(pieces, "stamp")   # the Clerk's stationery number
            continue
        band = _band_of(min(l.top for l in pieces), fences)
        if band == 0:
            # ABOVE THE FIRST FENCE: the Clerk's own banner, and the sheet's
            # name. 'OPINION COVER SHEET' names THIS SHEET, not the paper —
            # the paper called itself 'O P I N I O N' on page 2 — so it is
            # apparatus, not a title.
            if _COVER_TITLE.match(text):
                ctx.emit(pieces, "case-info", align=m.Align.CENTER)
            elif text.upper().startswith(_CLERK):
                ctx.emit(pieces, "court", align=m.Align.CENTER)
            continue
        role = _BANDS.get(labels.get(band, ""))
        if role is None:
            continue                    # a band this form does not print
        _cover_band(ctx, pieces, text, role, labels.get(band, ""))
    for _top, span in drawn:            # a fence below the sheet's last row
        ctx.items.append(m.Rule(prov=m.Prov(pm.number), span=span))


def _cover_band(ctx, pieces, text: str, role: str, label: str) -> None:
    """One row of a named band: the value carries the criterion, the label
    row carries only the name of the band."""
    value = _norm(" ".join(l.plain for l in pieces
                           if abs(l.x0 - _VALUE_X0) <= _COL_TOL))
    if role == "docket":
        # The band holds BOTH numbers, one per row: the appeal's own and the
        # one downstairs, in parentheses.
        paren = _PAREN.match(value) if value else None
        if paren and not _HAS_WORD.search(paren.group(1)):
            ctx.crit.setdefault("lower_court_docket", [])
            if _norm(paren.group(1)) not in ctx.crit["lower_court_docket"]:
                ctx.crit["lower_court_docket"].append(_norm(paren.group(1)))
            ctx.emit(pieces, "lower-court")
            return
        docket = _DOCKET.match(value) if value else None
        if docket:
            _add_docket(ctx, _norm(docket.group(1)))
        ctx.emit(pieces, "docket")
        return
    if value:
        if role == "caption":
            # THE TITLE OF CASE WRAPS, and on a consolidated record the band
            # holds TWO of them (asa_s._davis) — the rows are joined, never
            # replaced, or the criterion keeps only the last line printed
            # ('Company of America.' on cynthia_a._roberge).
            # (accumulated OUTSIDE `crit`: an undeclared criteria key is
            # attached by setattr and never serializes.)
            ctx.roster["title"] = _norm(
                ctx.roster.get("title", "") + " " + value)
            ctx.crit["case_name"] = ctx.roster["title"]
        elif role == "date":
            ctx.crit.setdefault("decision_date", value)
        elif role == "panel":
            # THE BAND'S VALUE WRAPS ('… Lynch Prata, and' / 'Long, JJ.'),
            # so the roster is parsed once the whole band is in — parsed per
            # row it yields a justice called 'and'.
            ctx.roster["justices"] = _norm(
                ctx.roster.get("justices", "") + " " + value)
        elif role == "lower-court" and value.upper() != "N/A":
            key = "lower_court_judge" if label.startswith("judicial") \
                else "lower_court"
            ctx.crit.setdefault(key, value)
        elif role == "counsel":
            ctx.crit["attorneys"] = _norm(
                (ctx.crit.get("attorneys") or "") + " " + value)[:4000]
    ctx.emit(pieces, role)


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


def _row(parts: list, role: str) -> m.HmLine:
    """One column's cell of a caption row — an HmLine that is NOT emitted
    into the flow: the CaptionBlock carries it."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(1), role="")
    first = parts[0]
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
            else piece
    return m.HmLine(text=_strip_rail(text),
                    prov=m.Prov(first.page, tuple(p.id for p in parts)),
                    align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
                    bold=all(bool(p.all_bold) for p in parts), role=role)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: set[int] = set()
        self.roster: dict = {}
        self.crit: dict = {}

    def emit(self, group: list, role: str, align=m.Align.LEFT) -> None:
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
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": sorted(self.anchor), "doc_type_final": None}
