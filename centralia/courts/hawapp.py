"""Intermediate Court of Appeals of the State of Hawaiʻi ('hawapp').

THE CONTRACT, and how it differs from its sibling. The ICA sets the same cover
as the Supreme Court — same 12pt Courier, same landmarks in the same order,
same '(By: …)' roster, same closing band — and **draws no fence at all**.
Measured over the 30-record corpus / 240 pages: `v_rules == 0` on every page
but three (one footnote's table on `yang_1`), and NOT ONE record draws a
horizontal rule that passes the fence test its sibling dispatches on (>= 0.62
of the sheet, on the page axis, below the stamp band, not an underline). haw's
'ruled cover' therefore never applies here, and haw's `open cover` — zoning by
stand-off and stopping at the underlined row — is the ONLY branch.

    'unfenced cover' (30 of 30):

    NOT FOR PUBLICATION IN WEST'S HAWAIʻI …   the reporter's advisory
    ┌ Electronically Filed        ┐           the e-filing stamp, a COLUMN
    │ Intermediate Court of Appeals│          pinned right of the 0.55 mark
    │ CAAP-26-0000399 / 27-JUL-2026│
    └ 08:40 AM / Dkt. 11 ORD      ┘
                  NO. CAAP-26-0000399         the docket
        IN THE INTERMEDIATE COURT OF APPEALS  the masthead
              OF THE STATE OF HAWAIʻI
                                              (---o0o--- on a published one)
              A.B., Plaintiff-Appellee,       the caption
                        v.
              R.L., Defendant-Appellant.
      APPEAL FROM THE FAMILY COURT OF …       the origin
              (CASE NO. 1FDV-25-000114)
                                              (docket / date / ALL-CAPS
                                               roster here on a published one)
        ORDER AND ORDER DISMISSING APPEAL     the TITLE, UNDERLINED
        ───────────────────────────────
    (By: Nakasone, Chief Judge, McCullen and Guidry, JJ.)   its roster
    Upon review of the record, it appears that:             the body

THE ZONES ARE MEASURED, NOT ORDERED. Nothing is drawn between them, so the
only mark the page gives is the stand-off: the cover is single-spaced (the
smallest pitch it sets, 11.87–13.68pt on 12pt type) and the zone gaps run
20.9–42.8pt. **1.5 of the block's own leading separates them on all 30** —
1.5, not haw's 2.0, because `state_v._kealoha` sets its zone gap at exactly
24.0 on a 12.0 leading and a 2.0 threshold merges its origin into its caption,
reading 'APPEAL FROM THE CIRCUIT COURT' as a party.

THE CAPTION IS THE RUN FROM THE FIRST PIVOT ZONE TO THE LAST. A consolidated
caption stands in two or three zones with its own stand-off between them
(`yang_1` sets 27.24pt between the foreclosure caption and the counterclaim
one; `century_campus` puts a zone holding nothing but 'and' between them), and
each names a pivot. Taking only the first zone files the rest as origin.

THE PIVOT MAY CLOSE A ROW instead of standing alone. 'v.' is its own row on 22
records and the tail of the plaintiff's row on 8 ('HYE JA CHOI,
Plaintiff-Appellant, v.', 'STATE OF HAWAIʻI, Plaintiff-Appellee, v.'), so the
pivot is read as a row that IS the pivot or ENDS on it.

WHERE THE READER STOPS: at the first UNDERLINED row centred on the page axis
below the stamp band — the court rules that row to its own measure, to the
decimal, on all 30 records (`x0`/`x1` agree within 0.3pt). Nothing else on the
sheet passes: the advisory's full-bleed rule stands in the top tenth, the
footnote separator is the court's 144pt rule at the body rail, and a citation
underline inside body prose is set at the rail, not on the axis.

…AND WHICH OF THE TWO IT IS DECIDES WHO OWNS IT — the finding this port
inherits from haw. A BYLINE anchors the writing it signs and is left exactly
where it stands ('OPINION OF THE COURT BY HIRAOKA, J.', the two published
`deutsche_bank` records). A TITLE names the PAPER, so it is the cover's last
landmark and is CLAIMED, together with the '(By: …)' roster beneath it, which
names the bench that decided and is apparatus by the same reasoning. Both are
returned as `anchor_ids` so core can hand the title back if the claim ever
cost a record its writing.

THE RUN BENEATH THE TITLE IS FOUND BY LEADING, measured against the ROW'S OWN
type size and never against `geom.body_size` — which on `choi_v._wireless_city`
is read off the e-filing stamp (`body_x0=144.0`) and on
`powell_v._century_square` off the corrected attorney credit (`body_x0=112.0`).
Measured over the 28 records that print a roster: it stands 11.87–13.68pt
below the title, 0.99–1.14 of the type size, and the body's first row stands
18.0–27.4pt down, 1.50 and up. 1.40 separates them with room on both sides.
Second, independent check: the court parenthesises the roster, so a run that
does not open '(' and close ')' claims nothing.

THE FURNITURE IS CLAIMED, and on this court that is not a choice — it is
what the reading stands on. Left unclaimed, the reporter's advisory and the
e-filing stamp are the FIRST unread rows on page 1, and where a reader has
claimed the headmatter core reads an unread row as the writing's. So the
writing opened at the top of the sheet, its span covered the whole cover, and
the bisection invariant put every claimed row back into it
(`invariant.reunited: headmatter row p1` eleven times on `muller`, and the
same on 29 of the 30). Core records both correctly on the 30 BASELINE renders
(30 `status`, 42 `stamp`) precisely because there is no claim there to suspend
the pass — measured after the change, the removed box is UNCHANGED
(running-head 32, folio 29, status 30, stamp 42), so this is one owner and not
the double-accounting of queue item 46.

The advisory is identified on page 1 as the row standing above the stamp
COLUMN (no cover row on any of the 30 records stands there) and then by
IDENTITY on later pages. A top-BAND threshold cannot do the second job:
`yang_1` sets its page-2 origin row at top 74.0 on a 792pt sheet, inside any
band wide enough to hold the advisory. For the same reason the stop test
carries NO top-band floor — one put `yang_1`'s page-2 'MEMORANDUM OPINION'
(top 128.3) out of reach and cost that record its whole reading.

THE CLOSING BAND is the sibling's, to the point: one printed block in two
columns, the appearances left and the conformed signatures right, page-
interleaved, under an attestation the court sets at the 144pt paragraph
indent. 23 of 30 records label the left column ('On the briefs:' / 'On the
brief:'); the other 7 print signatures alone. It is claimed WHOLE where it
names an appearance — the columns are read as columns, so a row pdfio welded
('AOAO Century Square, Hawaiiana /s/ Sonja M.P. McCullen', `powell_1`) is cut
at the glyph and each half filed under its own column — and returned under the
`signature` key where it does not.

*** TWO THINGS HAW'S BAND WALK CANNOT DO HERE. *** First, haw walks up from
the first signature over rows that stand OFF the body rail and stops at the
first row AT the rail as body prose. hawapp's band OPENS at the rail, with the
label 'On the briefs:', so that walk stops one row short and the attestation
and the label both fall outside the band — measured on `century_campus`, where
the band would have begun below its own first two rows. So the walk here
admits two things and nothing else: a row at the rail that is the court's own
label for its appearances, and a row off the rail that states a date. Anything
else at the rail is prose and ends the walk, and the step is 50pt where haw
needed 40 (`powell_1` sets 48.0 between its label and its attestation).

Second, THE ATTESTATION IS THE BAND'S HEAD AND IS EXEMPT FROM ITS PITCH.
`powell_1` sets 48.0pt between 'DATED: …' and 'On the briefs:' and 12.0pt
everywhere inside the stack below it, so one gap test over the whole band
closed it after its own first row and left 14 appearances unclaimed. The walk
has already proved the attestation belongs; the pitch test governs the STACK.

WHAT IS REPORTED, NOT TAKEN:

  * **pdfio WELDS the docket to the e-filing stamp where the two abut.** The
    cover's docket ends at x1=374.4 and the stamp's column starts at 372.0, so
    on `maui_tomorrow` and `muller` one line comes back as
    'NO. CAAP-25-0000012Dkt. 71 OAWST' / 'NO. CAAP-26-0000319D kt. 25 OGMD'.
    haw's fix — sorting the stamp column out BEFORE grouping visual rows —
    cannot reach this, because the weld is at the LINE level, not the row
    level. The row is emitted verbatim as the docket (its printed form is a
    fact and a court file may not invent provenance for half a line) and
    `docket_number` is parsed off the leading match, so the criterion is
    clean either way.
  * queue item 32's ʻokina shapes are ALL present here and none is this
    reader's. Counted over page 1 of the 30 records: `HAWAIʻI` (U+02BB) on
    16 and correct; `HAWAI‘I` (U+2018) on 10, `HAWAI#I` on 7, `HAWAI I` (the
    glyph dropped to a space) on 2 and `HAWAI(cid:35)I` on 1, none of them.
    The rendered shapes are IDENTICAL to the 30 baseline renders, so nothing
    here is this reader's.
  * queue items 30 and 41 are closed locally, the way nine courts have closed
    41: `criteria.attorneys` is set by this reader off the left column,
    because core mines it from `.text` and a `CaptionBlock` has none.
  * queue item 65's sibling: `criteria.judges` is set here too, off the
    conformed signatures reconciled against the roster — core fills it only
    from a LABELLED roster and the reader's claim means core's pass never
    sees this one.
  * queue item 31: the attestation states WHERE the court signed ('DATED:
    Honolulu, Hawaiʻi, July 30, 2026.') and `Criteria` has no place field, so
    it survives only as the row's own printed text.
  * **A NEW ONE, and it is the same family as items 48/56/62: a full SENTENCE
    is read as a doc-type heading.** `heading_doc_type('Judgment and Writ are
    affirmed.')` returns JUDGMENT, so on `mola_v._lopez-ruiz` the ruling that
    CLOSES the summary disposition anchors a second writing and the record
    comes back `[order 4 blocks] [majority 3 blocks]`. `assemble.py:1023`
    already carries the guard for exactly this shape (the mass murray /
    gorbatova note) but reaches it through `_is_dispo_line`, whose `_DISPO`
    is a closed list of two-word phrases — 'judgment affirmed' is in it and
    'judgment and writ are affirmed' is not. 1 of 30 records; identical
    reading with the decider popped except that the anchor does not fire
    there, so the claim EXPOSES it rather than causing it. Reported with a
    patch; `mola_v._lopez-ruiz` is therefore NOT offered as a sentinel.

WHAT THIS READER DOES NOT REACH. The court names the trial judge in its own
footnote 1 ('The Honorable Michelle N. Comeau presided.') on 17 records, and
`criteria.lower_court_judge` is empty on all 30. The row is a FOOTNOTE hanging
off the writing's first sentence, not a cover landmark, so the reader stops
above it; taking it would mean reaching into an assembled writing.
"""

from __future__ import annotations

import re

from .. import model as m
from ..classify import heading_doc_type
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import find_date
from . import get_profile

STYLE_UNFENCED = "unfenced cover"

# ---- hawapp's declared facts (measured over the 30-record corpus) --------
# THE BODY RAIL is 72.0pt on 22 records and 77.4pt on 8 (the press that sets
# the closing band tight). Declared, not measured: DocGeometry reads
# body_x0=144.0 off choi_v._wireless_city's e-filing stamp and 112.0 off
# powell_v._century_square's corrected attorney credit.
_BODY_X0 = 72.0
_RAIL_TOL = 6.0
# THE COURT FENCES NOTHING. Kept as the dispatch's negative half: a page that
# DOES set a fence pair is haw's paper, not this one, and gets NOTHING.
_FENCE_MIN_W = 0.62
_FENCE_AXIS = 10.0
_FENCE_TOP_MIN = 0.15
# AN UNDERLINE'S ENDS COINCIDE WITH THE ROW ABOVE IT. 0.3pt is the largest
# disagreement in the corpus (elizares, mola — the double-spaced press).
_UNDER_TOL = 3.0
_UNDER_REACH = 18.0
# THE COVER IS CENTRED ON THE PAGE AXIS — every row of it, on every record.
# The widest miss is 0.45pt (maui_tomorrow's title, 122.4-489.5).
_AXIS_TOL = 8.0
# THE E-FILING STAMP: a COLUMN of five or six short rows pinned right of the
# page's 0.55 mark, in its top quarter. x0=372.0 on all 30 records.
_STAMP_BAND = 0.25
_STAMP_X = 0.55
# THE REPORTER'S ADVISORY stands ABOVE the stamp column on page 1 (24.4-51.4
# against the stamp's 95.5) and nothing else on any cover does.
_ADVISORY_CLEAR = 20.0
_ADVISORY_BAND = 0.08
# HOW FAR THE COVER MAY RUN: yang_1's consolidated caption fills page 1 and
# rules its title on page 2.
_MAX_PAGES = 3
# THE ZONE GAP. The cover's own leading is the smallest pitch it sets
# (11.87-13.68pt); its zone gaps run 20.88-42.78. 1.5 takes every gap and no
# leading — state_v._kealoha sets 24.0 against a 12.0 leading, so haw's 2.0
# merges its origin into its caption.
_ZONE_LEAD = 1.5
# …and a pitch under this is not a line step but one visual row pdfio split.
_MIN_PITCH = 4.0
# THE COVER IS SINGLE-SPACED AND THE WRITING IS NOT. The roster stands
# 0.99-1.14 of the row's own type size below the title; the body's first row
# 1.50 and up. Measured against the ROW'S size, never geom.body_size.
_APPARATUS_LEAD = 1.40
# HOW LONG THE ROSTER MAY RUN: three rows on mount_jr._v._apao, never more.
_ROSTER_ROWS = 4
# THE CLOSING BAND's rows stand one leading apart; the widest step inside one
# is 27.4pt (ricci) and 40pt clears the footnote zone and the folio below it.
_BAND_GAP = 40.0
# …and the walk UP to its head takes at most this many rows, one step each.
# 48.0pt separates powell_1's label from its attestation.
_ATTEST_STEP = 50.0
_ATTEST_STEPS = 4

# 'NO. CAAP-26-0000399' / 'CAAP-24-0000480'. This court's own docket and no
# other: a bare number inside the caption opens with a digit and is not one.
# The trailing guard is `(?!\d)` and not `\b`, because pdfio WELDS the
# stamp's own row onto the end of it ('NO. CAAP-26-0000319D kt. 25 OGMD')
# and a word boundary refuses the whole match there.
_DOCKET = re.compile(r"^(?:NO\.\s*)?[A-Z]{2,5}[-‐‑–—]\d{2}"
                     r"[-‐‑–—]\d{4,9}(?!\d)")
# The number a court BELOW gave the case, in every form hawapp prints:
# '1FDV-25-000114', '3DTC-24-219562', '1CC161001671', '1PC151001478',
# '2CCV-23-0000007'.
_LOWER_DOCKET = re.compile(
    r"\b[0-9]?[A-Z]{2,5}[-‐‑]\d{2}[-‐‑]\d{3,9}(?:\(\d\))?"
    r"|\b\d[A-Z]{2,4}\d{6,10}\b"
    r"|\b\d{1,2}:\d{2}[-‐‑][a-z]{2}[-‐‑]\d{3,6}"
    r"(?:[-‐‑][A-Z]{2,4})*\b")
# THE COURT'S DEVICE, printed between masthead and caption of a published
# opinion: '---o0o---'.
_ORNAMENT = re.compile(r"^[-–—oO0]{5,}$")
# THE PIVOT. 'v.' on every record; 'vs.' because the sibling prints it.
_PIVOT = ("v", "vs")
# A PARTY STATUS row: every alphabetic token is a role word. Hawaiʻi stacks
# them, so the row is read as the set of roles it names, never as a phrase.
# The full set the ICA prints, taken off the corpus's own status rows:
# 'Plaintiffs/Counterclaim Defendants/Cross-claimants-Appellees,',
# 'Counterclaimant/Cross-Claimant/Third-Party Plaintiff/', 'Real Party in
# Interest-Appellee,', 'Defendant/Cross-claim Defendant-'. `claim` and
# `claimant` are in it because the court hyphenates 'Cross-claim' and
# 'Cross-claimant' — without them `_is_status_row` refused the row and
# 'GERALD K. MOUNT, JR. and JANE R. MOUNT' came back with
# 'Plaintiffs/Counterclaim Defendants/Cross-claimants-Appellees' inside it.
_ROLE_WORDS = frozenset("""
plaintiff plaintiffs defendant defendants appellant appellants appellee
appellees petitioner petitioners respondent respondents cross third party
counterclaim counterclaimant counterclaimants claim claims claimant
claimants intervenor intervenors interested successor amicus amici curiae
real in interest and
""".split())
# THE BENCH VOCABULARY — the finite set of ways this court names a seat.
# 'presiding judge' is a TITLE here and not a note about one: the ICA seats a
# presiding judge on every three-judge panel it convenes.
_BENCH_TITLES = ("c.j.", "j.", "jj.", "v.c.j.", "chief judge",
                 "presiding judge", "associate judge", "judge", "judges",
                 "justice", "justices", "acting c.j.")
_BENCH_TOKENS = frozenset(t for t in _BENCH_TITLES if " " not in t)
_BENCH_LEADERS = ("intermediate court of appeals associate judge",
                  "circuit court judge", "circuit judge", "district judge",
                  "chief judge", "presiding judge", "associate judge", "judge")
# What a roster says ABOUT a seat, never a name. 'for the court' is this
# court's own note on a single-judge order of correction.
_ROSTER_NOISE = ("assigned by reason of vacancy", "recused", "joins",
                 "joined", "dissenting", "concurring", "with whom",
                 "by reason of vacancy", "for the court")
# A clause about a seat runs from here to its own closing word.
_ROSTER_SKIP_OPEN = "in place of"
_ROSTER_SKIP_CLOSE = ("recused", "vacancy")
# The court's own statement of the day it signed.
_DATED = "dated"
# THE COURT'S LABEL FOR ITS APPEARANCES. Printed on 23 of 30 records and on
# every record that names one; the other 7 print signatures alone.
_COUNSEL_LABEL = ("on the brief", "on the briefs")
_COUNSEL_MARKS = _COUNSEL_LABEL + (
    "for appellant", "for appellee", "for petitioner", "for respondent",
    "for plaintiff", "for defendant", "self-represented", "pro se")
# THE CONFORMED SIGNATURE GLYPH: 88 of them over the 30 records, on every one.
_SIG_GLYPH = "/s/"
# RETURN THE BAND FOR `Document.signature`? Queue item 29 landed on
# 2026-08-20, so the key has a writer and haw ships with this on.
_EMIT_SIGNATURE_SECTION = True


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _alpha_tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^A-Za-z]+", text) if t]


def _is_status_row(text: str) -> bool:
    toks = _alpha_tokens(text)
    return bool(toks) and all(t.lower() in _ROLE_WORDS for t in toks)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in _PIVOT


def _pivot_at(text: str) -> bool:
    """The pivot on its own row, or closing one.

    'HYE JA CHOI, Plaintiff-Appellant, v.' is the same landmark as a bare
    'v.' — 8 of the 30 records set it that way — and reading only the bare
    form leaves those covers with no caption zone at all."""
    body = _norm(text)
    if _is_pivot(body):
        return True
    head, sep, tail = body.rpartition(",")
    return bool(sep) and bool(head.strip()) and _is_pivot(tail)


def _is_docket(text: str) -> bool:
    return bool(_DOCKET.match(_norm(text)))


def _has_bench(text: str) -> bool:
    return any(t.strip(",;:()").lower() in _BENCH_TOKENS
               for t in _norm(text).split())


def _lower_dockets(text: str) -> list[str]:
    return [_norm(t) for t in _LOWER_DOCKET.findall(text)]


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its column gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "bottom", "x0", "x1", "size",
                 "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.bottom = max(p.bottom for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(lines: list) -> list:
    """Group lines into the visual rows the page printed."""
    buckets: dict = {}
    loose: list = []
    for line in lines:
        if line.row is not None:
            buckets.setdefault(line.row, []).append(line)
        else:
            loose.append(line)
    groups = list(buckets.values())
    for line in sorted(loose, key=lambda l: (l.top, l.x0)):
        for g in groups:
            if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                g.append(line)
                break
        else:
            groups.append([line])
    rows = [_Row(g) for g in groups]
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _is_underline(rule, pm) -> bool:
    """A rule whose ends coincide with the row above it is that row's
    underline, not a fence."""
    return any(rule.top - _UNDER_REACH <= l.top <= rule.top
               and abs(l.x0 - rule.x0) <= _UNDER_TOL
               and abs(l.x1 - rule.x1) <= _UNDER_TOL
               for l in pm.lines if l.plain.strip())


def _drawn_fences(pm) -> list:
    """The fence pair haw dispatches on. **Empty on all 30 hawapp records** —
    kept so the dispatch is a measurement of this page and not an assumption
    about the court."""
    out = []
    for r in pm.h_rules:
        if r.width < _FENCE_MIN_W * pm.width:
            continue
        if r.top < _FENCE_TOP_MIN * pm.height:
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        if _is_underline(r, pm):
            continue
        out.append(r.top)
    return sorted(out)


def _underlined_row(row: _Row, pm) -> bool:
    """The row the page RULES to its own measure — the order's title, the
    opinion's byline. The rule sits at the baseline, inside the row's own box.
    """
    return any(row.top < r.top <= row.bottom + 6
               and abs(r.x0 - row.x0) <= _UNDER_TOL
               and abs(r.x1 - row.x1) <= _UNDER_TOL
               for r in pm.h_rules)


def _on_axis(row: _Row, pm) -> bool:
    return abs((row.x0 + row.x1) / 2 - pm.width / 2) <= _AXIS_TOL


# --------------------------------------------------------------------------
# the roster
# --------------------------------------------------------------------------

def _roster_names(text: str) -> list[str]:
    """The seats a Hawaiʻi roster names, in order.

    '(By: McCullen, Presiding Judge, Guidry, J., and Circuit Court Judge Costa
    in place of Nakasone, C.J., Leonard, Hiraoka, and Wadsworth, JJ.,
    recused)' seats THREE judges and recuses four; read by splitting on
    punctuation it seats six. So the walk carries a closed vocabulary: a TITLE
    closes the names standing before it, a LEADER opens a titled name, and a
    clause ABOUT a seat is skipped whole — including where the clause opens
    INSIDE a leader's own token, which is the case haw's version cannot see."""
    body = _norm(text)
    low0 = body.lower()
    if low0.startswith("(by:") or low0.startswith("(by "):
        body = body.split(":", 1)[-1] if ":" in body[:5] else body[4:]
    body = body.strip().lstrip("(").rstrip(")").strip()
    out: list[str] = []
    pending: list[str] = []
    skipping = False
    for raw in re.split(r"[,;]|\s+and\s+", body, flags=re.I):
        tok = raw.strip().strip(",;() ")
        if not tok:
            continue
        low = tok.lower()
        if skipping:
            if any(c in low for c in _ROSTER_SKIP_CLOSE):
                skipping = False
            continue
        # A CLAUSE ABOUT A SEAT MAY OPEN INSIDE THE TOKEN THAT NAMES ONE.
        # 'Circuit Court Judge Costa in place of Nakasone' both seats Costa
        # and opens the recusal clause; haw's version reads the leader and
        # leaves `skipping` off, so the four recused judges are seated.
        cut = low.find(_ROSTER_SKIP_OPEN)
        if cut >= 0:
            tok = tok[:cut].strip().strip(",;() ")
            low = tok.lower()
            skipping = True
            if not tok:
                continue
        if any(low.startswith(n) or low == n for n in _ROSTER_NOISE):
            if low.startswith("with whom"):
                tok = tok[len("with whom"):].strip()
                low = tok.lower()
            else:
                continue
        # 'Ginoza JJ.' — the court drops the comma on some records. Tested
        # AFTER the title itself, or 'Acting C.J.' reads as a judge called
        # Acting.
        if low not in _BENCH_TITLES:
            for title in ("jj.", "c.j.", "j.", "v.c.j."):
                if low.endswith(" " + title):
                    pending.append(tok[: -len(title)].strip())
                    tok, low = title, title
                    break
        if low in _BENCH_TITLES:
            out.extend(p for p in pending if p)
            pending = []
            continue
        lead = next((l for l in _BENCH_LEADERS if low.startswith(l)), None)
        if lead:
            name = tok[len(lead):].strip()
            for noise in _ROSTER_NOISE:
                idx = name.lower().find(noise)
                if idx > 0:
                    name = name[:idx].strip()
            if name:
                out.append(name)
            continue
        pending.append(tok)
    out.extend(p for p in pending if p)
    seen: set = set()
    names: list[str] = []
    for n in out:
        n = n.strip(" .,")
        # A NAME IS CAPITALISED. Everything else on a roster row is a note
        # about a seat, and the vocabulary above cannot be complete.
        if n and n[0].isupper() and n.lower() not in seen:
            seen.add(n.lower())
            names.append(n)
    return names


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom):
        self.model = model
        self.geom = geom
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.attorneys: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.anchor: list = []
        self.doc_type: object = None
        self.signature: list = []

    def emit(self, row: _Row, role: str, centre: bool = True) -> None:
        pm = self.pages[row.page]
        ok = centre and _on_axis(row, pm)
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align.CENTER if ok else m.Align.LEFT,
            x0=row.x0, size=row.size, role=role))
        self.consumed.update(row.ids)

    def drop(self, rows: list, kind: str) -> None:
        if not rows:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(r.text for r in rows)[:1200],
            prov=m.Prov(rows[0].page,
                        tuple(i for r in rows for i in r.ids)),
            kind=kind))
        for r in rows:
            self.consumed.update(r.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "dropped": self.dropped,
                "signature": self.signature,
                "consumed": self.consumed, "anchor_ids": list(self.anchor),
                "doc_type_final": self.doc_type}


@decider("headmatter.read", court="hawapp")
def read_headmatter_hawapp(model, geom, **_):
    """Read the ICA's unfenced cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    # A PAGE THAT FENCES ITS CAPTION IS THE SUPREME COURT'S PAPER, not this
    # one. Measured: no hawapp record draws one, and the record that did
    # would be haw's 'ruled cover' filed into the wrong corpus.
    if len(_drawn_fences(model.pages[0])) >= 2:
        return NOTHING
    finder = FurnitureFinder(model, _BODY_X0,
                             geom.body_size if geom else 12.0)
    ctx = _Ctx(model, geom)
    rows, advisory, stamp = _cover_rows(model, finder)
    if not rows:
        return NOTHING
    if _read_cover(ctx, rows) is NOTHING:
        return NOTHING
    # A READER THAT CLAIMS THE REGION INHERITS ITS FURNITURE, and on this
    # court that is not optional. Left unclaimed, the advisory and the
    # e-filing stamp are the FIRST unread rows on page 1 — and where a reader
    # claimed the headmatter, core reads an unread row as the writing's. So
    # the writing opened at the top of the sheet, its span covered the whole
    # cover, and the bisection invariant put all eleven claimed rows back
    # into it ('invariant.reunited: headmatter row p1' x11, muller). Core
    # records both correctly on the 30 BASELINE renders (30 `status`, 42
    # `stamp`) precisely because there is no claim there to suspend the pass.
    ctx.drop(advisory, "status")
    ctx.drop(stamp, "stamp")
    _read_closing_band(ctx, model, finder)
    _read_signature_band(ctx, model, finder)
    return ctx.result()


def _cover_rows(model, finder) -> list:
    """The cover's own rows, the furniture LEFT WHERE IT IS.

    Core already records the advisory, its per-page repeat, the e-filing stamp
    and the folio on all 30 records (30 `status`, 24 `running-head`, 42
    `stamp`, 29 `folio` over the baseline renders), so claiming them here
    would produce exactly the double-accounting of queue item 46. They are
    skipped, and the walk simply does not own them.

    THE ADVISORY IS IDENTIFIED BY POSITION ONCE and by IDENTITY thereafter:
    on page 1 it is the row standing above the stamp column (nothing else on
    any of the 30 covers does), and its text is then matched on later pages.
    A top-BAND threshold cannot do the second job — yang_1's page-2 origin row
    stands at top 74.0 on a 792pt sheet, inside any band wide enough to hold
    the advisory."""
    seen: set = set()
    out: list = []
    ad_rows: list = []
    st_rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        content: list = []
        advisory: list = []
        stamped: list = []
        stamp_top = min((l.top for l in pm.lines
                         if l.plain.strip()
                         and l.top < _STAMP_BAND * pm.height
                         and l.x0 > _STAMP_X * pm.width), default=None)
        head_cut = (stamp_top - _ADVISORY_CLEAR if stamp_top is not None
                    else _ADVISORY_BAND * pm.height)
        for line in pm.lines:
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            text = _norm(line.plain)
            if pm.number == 1 and line.top < head_cut:
                seen.add(text)
                advisory.append(line)
                continue
            if text in seen:
                advisory.append(line)
                continue
            if (line.top < _STAMP_BAND * pm.height
                    and line.x0 > _STAMP_X * pm.width):
                stamped.append(line)          # the e-filing stamp column
                continue
            content.append(line)
        out.extend(_visual_rows(content))
        ad_rows.extend(_visual_rows(advisory))
        st_rows.extend(_visual_rows(stamped))
    return out, ad_rows, st_rows


def _zones(rows: list) -> list:
    """The cover's own blocks. Nothing is drawn between them, so the LEADING
    is the only mark: it is the smallest genuine pitch the block sets (a pitch
    under _MIN_PITCH is one visual row pdfio split, not a line step), and a
    gap of more than 1.5 of it opens a new zone."""
    pitches = sorted(b.top - a.top for a, b in zip(rows, rows[1:])
                     if b.page == a.page and b.top - a.top > _MIN_PITCH)
    if not pitches:
        return [rows]
    lead = pitches[0]
    out: list = [[rows[0]]]
    for prev, row in zip(rows, rows[1:]):
        if row.page != prev.page or row.top - prev.top > lead * _ZONE_LEAD:
            out.append([])
        out[-1].append(row)
    return out


def _read_cover(ctx: _Ctx, rows: list):
    """HEAD, CAPTION, TAIL — ended by the first UNDERLINED row on the axis,
    and zoned by the stand-off inside the run above it."""
    stop: _Row | None = None
    cover: list = []
    below: list = []
    for i, row in enumerate(rows):
        pm = ctx.pages[row.page]
        # NO TOP-BAND FLOOR. The advisory and the stamp are already out of
        # `rows`, so the only rule left in the top band belongs to nothing —
        # and a floor put yang_1's page-2 'MEMORANDUM OPINION' (top 128.3 on
        # a 792pt sheet) out of reach, which cost that record its whole
        # reading. The cover being non-empty is the guard that remains.
        if _on_axis(row, pm) and _underlined_row(row, pm):
            stop = row
            below = rows[i + 1:]
            break
        cover.append(row)
    if stop is None or not cover:
        return NOTHING

    zones = _zones(cover)
    pivots = [i for i, z in enumerate(zones)
              if any(_pivot_at(r.text) for r in z)]
    if not pivots or pivots[0] == 0:
        return NOTHING
    first, last = pivots[0], pivots[-1]
    head = [r for z in zones[:first] for r in z]
    caption = [r for z in zones[first:last + 1] for r in z]
    tail = [r for z in zones[last + 1:] for r in z]
    if not (head and caption):
        return NOTHING

    # --- HEAD: the docket, the masthead, the court's device ---------------
    masthead: list = []
    for row in head:
        if _is_docket(row.text):
            _record_docket(ctx, row.text)
            ctx.emit(row, "docket")
        elif _ORNAMENT.match(row.text.replace(" ", "")):
            ctx.emit(row, "court")
        else:
            masthead.append(row.text)
            ctx.emit(row, "court")
    if masthead:
        ctx.crit["court"] = " ".join(masthead)

    # --- the caption ------------------------------------------------------
    for row in caption:
        ctx.emit(row, "caption")
    ctx.crit["caption"] = [r.text for r in caption]
    _read_parties(ctx, caption)

    # --- TAIL: the docket, the origin, the date, the bench ---------------
    origin: list = []
    panel: list = []
    for row in tail:
        if _is_docket(row.text):
            _record_docket(ctx, row.text)
            ctx.emit(row, "docket")
        elif find_date(row.text) and len(row.text) <= 40:
            ctx.crit.setdefault("decision_date", find_date(row.text))
            ctx.emit(row, "date")
        elif _has_bench(row.text):
            panel.append(row.text)
            ctx.emit(row, "panel")
        else:
            origin.append(row.text)
            ctx.emit(row, "lower-court")
    _record_origin(ctx, origin)

    # --- the stop row: whose is it? --------------------------------------
    ctx.crit["headmatter_style"] = STYLE_UNFENCED
    if not BylineParser(get_profile("hawapp").byline).parse(stop.text):
        # A TITLE NAMES THE PAPER, so it is the cover's last landmark and the
        # headmatter's last row — with the roster the court prints beneath it.
        ctx.crit["title"] = stop.text.rstrip(".")
        ctx.emit(stop, "title")
        ctx.anchor.extend(stop.ids)
        _dt = heading_doc_type(stop.text)
        if _dt in (m.DocType.ORDER, m.DocType.OPINION):
            ctx.doc_type = _dt
        roster = _apparatus_below(stop, below)
        for row in roster:
            ctx.emit(row, "panel")
        if roster and not panel:
            panel = [r.text for r in roster]
    if panel:
        ctx.crit["panel_line"] = " ".join(panel)
        names = _roster_names(" ".join(panel))
        if names:
            ctx.crit["panel"] = names
    if "decision_date" not in ctx.crit:
        dated = _dated_line(ctx.model)
        if dated:
            ctx.crit["decision_date"] = dated
    return None


def _apparatus_below(stop: _Row, below: list) -> list:
    """The '(By: <panel>)' roster the court prints under its own title.

    TWO tests, and the row must pass both. GEOMETRY first: the run keeps the
    cover's single leading (<= 1.40 of the row's own type size) where the
    body below it is set on 1.50 and up. Then the court's own FENCE: hawapp
    parenthesises the roster on all 28 records that print one, and a run that
    does not close is not this object and nothing is claimed."""
    run: list = []
    prev = stop
    for row in below[:_ROSTER_ROWS]:
        if row.page != prev.page:
            break
        size = max(prev.size or 0.0, row.size or 0.0) or 12.0
        if row.top - prev.top > size * _APPARATUS_LEAD:
            break
        run.append(row)
        prev = row
    if not run or not run[0].text.startswith("("):
        return []
    close = next((i for i, r in enumerate(run)
                  if r.text.rstrip().endswith(")")), None)
    return run[:close + 1] if close is not None else []


def _dated_line(model) -> str | None:
    for pm in model.pages:
        for line in pm.lines:
            text = _norm(line.plain)
            if text.lower().startswith(_DATED):
                got = find_date(text)
                if got:
                    return got
    return None


def _record_docket(ctx: _Ctx, text: str) -> None:
    """The docket, parsed off the leading match.

    pdfio WELDS the docket to the e-filing stamp where the two abut
    ('NO. CAAP-25-0000012Dkt. 71 OAWST' — maui_tomorrow, muller: the docket
    ends at x1=374.4 and the stamp column starts at 372.0). The row keeps its
    printed form, because a court file may not invent provenance for half a
    line; the CRITERION takes only the docket."""
    mo = _DOCKET.match(_norm(text))
    docket = mo.group(0) if mo else _norm(text)
    if docket.upper().startswith("NO."):
        docket = docket[3:].strip()
    if "docket_number" not in ctx.crit:
        ctx.crit["docket_number"] = docket
    elif docket != ctx.crit["docket_number"]:
        ctx.crit.setdefault("other_dockets", []).append(docket)


def _record_origin(ctx: _Ctx, rows: list) -> None:
    """The origin, split into what the court BELOW is and what it numbered.

    The ICA states the route in prose ('APPEAL FROM THE FAMILY COURT OF THE
    FIRST CIRCUIT', 'HONOLULU DIVISION') and parenthesises every number the
    case carried below it. A lower-court number is NEVER `other_dockets` —
    that bucket is companion appeals, and conflating the two cost ill its
    whole corpus (commit 03e8652)."""
    prose = [r for r in rows if not r.startswith("(")]
    if prose:
        ctx.crit["lower_court"] = " ".join(prose)
    numbers: list[str] = []
    for row in rows:
        for dk in _lower_dockets(row):
            if dk not in numbers:
                numbers.append(dk)
    if numbers:
        ctx.crit["lower_court_docket"] = numbers


def _tidy(text: str) -> str:
    """Close a party name. A trailing period after a CAPITAL is a
    generational suffix, not a full stop ('GERALD K. MOUNT, JR.')."""
    out = text.rstrip(" ,;")
    if out.endswith(".") and not (len(out) >= 2 and out[-2].isupper()):
        out = out[:-1]
    return out.rstrip(" ,;")


def _side_name(rows: list[str]) -> str:
    """One side of the pivot, as the party names the court printed there."""
    out: str = ""
    broke = False
    for row in rows:
        text = _norm(row).strip()
        if not text or _is_status_row(text):
            broke = broke or bool(out)
            continue
        # A ROW MAY CLOSE ON MORE THAN ONE STATUS. 'MARGARET APAO,
        # Defendant-Appellant, and' carries two ('Defendant-Appellant' and
        # the conjunction), and stripping one left 'MARGARET APAO,
        # Defendant-Appellant' standing in `parties`. `_tidy` is applied to
        # the TEST and not to `text`, so the row's OWN list separator
        # survives where nothing is stripped — flattened onto `text` it took
        # the semicolons out of 'SCOTT C.H. YANG; KEITH YANG; WELLS FARGO
        # BANK, N.A.;' and ran three defendants together.
        while True:
            head, sep, tail = _tidy(text).rpartition(",")
            if not (sep and head.strip() and _is_status_row(tail)):
                break
            text = head.strip()
        if not out:
            out = text
        elif broke and not out.rstrip().endswith((",", ";")):
            out += "; " + text
        else:
            out += " " + text
        broke = False
    return _tidy(_norm(out))


def _read_parties(ctx: _Ctx, caption: list) -> None:
    """The parties either side of the FIRST pivot.

    The row that carries the pivot may carry a party too ('HYE JA CHOI,
    Plaintiff-Appellant, v.'), so it is split at the pivot rather than
    dropped — dropped, choi's caption names one party and no case."""
    texts = [r.text for r in caption]
    cut = next((i for i, t in enumerate(texts) if _pivot_at(t)), None)
    if cut is not None:
        # THE CASE NAME IS THE PARTIES EITHER SIDE OF THE **FIRST** PIVOT. A
        # consolidated caption prints four of them (yang_1: the foreclosure,
        # the counterclaim, the cross-claim and the third-party claim), and
        # everything after the first pivot joined wholesale reads as one
        # 600-character defendant with three 'v.'s inside it. `caption`
        # still carries every row verbatim.
        nxt = next((j for j in range(cut + 1, len(texts))
                    if _pivot_at(texts[j])), len(texts))
        head_rows = list(texts[:cut])
        tail_rows = list(texts[cut + 1:nxt])
        if not _is_pivot(texts[cut]):
            lead, _sep, _piv = _norm(texts[cut]).rpartition(",")
            if lead.strip():
                head_rows.append(lead.strip())
        left = _side_name(head_rows)
        right = _side_name(tail_rows)
        if left and right:
            ctx.crit["parties"] = [left, right]
            ctx.crit["case_name"] = f"{left} v. {right}"
            return
    whole = _side_name(texts)
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


# --------------------------------------------------------------------------
# the closing band
# --------------------------------------------------------------------------

def _conformed_lines(pm, lines: list) -> list:
    """Every line on the page that carries a conformed signature.

    Tested for the glyph ANYWHERE, not at the start: pdfio welds a wide
    appearance to the signature beside it ('AOAO Century Square, Hawaiiana
    /s/ Sonja M.P. McCullen' — powell_1), and a start-only test loses that
    seat from the bench."""
    return [l for l in lines if _SIG_GLYPH in _norm(l.plain)]


def _band_top(lines: list, sig_top: float, sig_x0: float,
              rail: float) -> tuple:
    """Where the closing band OPENS, and which row is the attestation.

    The walk goes UP from the first conformed signature, at most
    _ATTEST_STEPS rows and one _ATTEST_STEP per step, and admits exactly two
    things: the court's own LABEL for its appearances, standing at the body
    rail, and a row OFF the rail and LEFT of the signature column that states
    a DATE. Anything else at the rail is body prose and ends the walk.

    haw's version admits only the second, because haw's band has no label —
    and here that stops the walk one row short on the 23 records that print
    'On the briefs:', leaving the label and the attestation outside their own
    band (century_campus: the band would open below its own first two rows).

    FIRST, not best: a disposition's last sentence carries dates of its own,
    and any rule that searched for the closest date rather than stopping at
    the first row that is not the band's would reach them."""
    above = sorted((l for l in lines if l.top < sig_top - 1.0),
                   key=lambda l: -l.top)
    top = sig_top
    attest = None
    prev = sig_top
    for line in above[:_ATTEST_STEPS]:
        if prev - line.top > _ATTEST_STEP:
            break
        text = _norm(line.plain)
        if line.x0 <= rail:
            if any(text.lower().startswith(lb) for lb in _COUNSEL_LABEL):
                top = line.top
                prev = line.top
                continue
            break
        if line.x0 >= sig_x0 - 1.0:
            break
        if find_date(text):
            attest = line
            top = line.top
            break
        prev = line.top
    return top, attest


def _read_closing_band(ctx: _Ctx, model, finder) -> None:
    """The two-column band the court prints below its writings: the
    appearances left, the conformed signatures right.

    It is ONE printed block in two columns — the page interleaves them row by
    row — and it is claimed WHOLE, the way haw claims its own. Claiming only
    the counsel column leaves the signature rows lying between rows that stay
    in the writing, and core's bisection invariant then puts the head of the
    block back.

    A record whose band names NO appearance is a signature block alone (7 of
    the 30) and is left to `_read_signature_band`."""
    pm = model.pages[-1]
    lines = [l for l in pm.lines
             if l.plain.strip() and not finder.kind(pm, l)]
    sigs = _conformed_lines(pm, lines)
    starts = [l for l in sigs if _norm(l.plain).startswith(_SIG_GLYPH)]
    if not starts:
        return
    sig_x0 = min(l.x0 for l in starts)
    if sig_x0 < pm.width * 0.35:
        return
    rail = _BODY_X0 + _RAIL_TOL
    top, attest = _band_top(lines, min(l.top for l in sigs), sig_x0, rail)
    band: list = []
    stack: list = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if line.top < top - 0.5:
            continue
        # THE ATTESTATION IS THE BAND'S HEAD AND IS EXEMPT FROM ITS PITCH.
        # powell_1 sets 48.0pt between 'DATED: …' and 'On the briefs:' and
        # 12.0pt everywhere inside the stack below it, so a single gap test
        # over the whole band closed it after its own first row and left 14
        # appearances unclaimed. The walk in `_band_top` has already proved
        # the attestation belongs; the pitch test governs the STACK.
        if line is attest:
            band.append(line)
            continue
        if stack and line.top - max(b.top for b in stack) > _BAND_GAP:
            break
        # A BAND ROW STANDS IN ONE OF THE BAND'S OWN COLUMNS. The folio
        # stands between them (x0=302.4 against a rail of 78 and a signature
        # column of 324) and on a one-page order there is no repeat for core
        # to learn it from.
        if not (line.x0 <= rail or line.x0 >= sig_x0 - 2.0):
            continue
        band.append(line)
        stack.append(line)
    if not band:
        return
    joined = " ".join(_norm(l.plain) for l in band
                      if l.x0 <= rail).lower()
    if not any(mk in joined for mk in _COUNSEL_MARKS):
        return
    left_rows: list = []
    right_rows: list = []
    if attest is not None and attest in band:
        # IT SPANS BOTH COLUMNS, so it is neither of them: emitted ahead of
        # the block as the band's own head, tagged `date` for what it states.
        band = [l for l in band if l is not attest]
        ctx.attorneys.append(m.HmLine(
            text=line_markup(attest), prov=m.Prov(attest.page, (attest.id,)),
            align=m.Align.LEFT, x0=attest.x0, size=attest.size or 0.0,
            role="date"))
        ctx.consumed.add(attest.id)
    for line in band:
        left = line.x0 <= rail
        text = line_markup(line)
        role = "counsel" if left else "panel"
        # A ROW THE PAGE GLUED still belongs to both columns. The glyph says
        # where the second column starts, so the row is split THERE and each
        # half filed under its own column.
        cut = text.find(_SIG_GLYPH, 1)
        if left and cut > 0:
            _l, _r = text[:cut].rstrip(), text[cut:].strip()
            if _l and _r:
                left_rows.append(m.HmLine(
                    text=_l, prov=m.Prov(line.page, (line.id,)),
                    align=m.Align.LEFT, x0=line.x0,
                    size=line.size or 0.0, role="counsel"))
                right_rows.append(m.HmLine(
                    text=_r, prov=m.Prov(line.page, (line.id,)),
                    align=m.Align.LEFT, x0=line.x0,
                    size=line.size or 0.0, role="panel"))
                ctx.consumed.add(line.id)
                continue
        (left_rows if left else right_rows).append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            role=role))
        ctx.consumed.add(line.id)
    if left_rows and right_rows:
        ctx.attorneys.append(m.CaptionBlock(
            left=left_rows, right=right_rows, rail=None,
            prov=m.Prov(band[0].page)))
    else:
        ctx.attorneys.extend(left_rows or right_rows)
    # THE APPEARANCES ARE A CRITERION (queue items 30 and 41). Core mines
    # `criteria.attorneys` off each item's `.text` and a `CaptionBlock` has
    # none, so a two-column band publishes nothing at all. The court read the
    # columns, so the court states which one is counsel: the LEFT.
    if left_rows:
        # PLAIN TEXT, not markup. `line_markup` has already escaped the row
        # ('City &amp; County of Honolulu'), and a criterion is escaped again
        # on its way into the render — so the printed ampersand came out
        # '&amp;amp;'. The criterion carries what the page says.
        from ..audit import strip_tags as _st, unescape_xml as _ux
        ctx.crit["attorneys"] = " ".join(
            t for t in (_norm(_ux(_st(r.text))) for r in left_rows) if t
        )[:2000]


# --------------------------------------------------------------------------
# the closing SIGNATURE band — the court's attestation and the bench that
# signed it. `Document.signature` gained its writer with queue item 29.
# --------------------------------------------------------------------------

def _sig_names(text: str) -> list[str]:
    """The names one printed row conforms. The glyph is the separator, and
    whatever stands BEFORE the first one belongs to the other column."""
    pieces = _norm(text).split(_SIG_GLYPH)
    return [p.strip(" ,;.") for p in pieces[1:] if p.strip(" ,;.")]


def _conformed(model, finder) -> list:
    out: list = []
    for pm in model.pages:
        for line in pm.lines:
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            if _SIG_GLYPH in _norm(line.plain):
                out.append(line)
    out.sort(key=lambda l: (l.page, l.top, l.x0))
    return out


def _signing_bench(signers: list[str], panel: list[str]) -> list[str]:
    """The signing bench, reconciled with the roster above it.

    The roster names a seat by SURNAME ('Nakasone, Chief Judge') and the
    signature names it in FULL ('/s/ Karen T. Nakasone'), so the two are
    matched on the surname and emitted in the ROSTER'S order — the order the
    court seats them in, which is also the order it signs in on all 30
    records. A run that matches NO seat is not this court's bench and yields
    nothing; a signer who matches no seat while others do IS kept."""
    def key(name: str) -> str:
        toks = [t for t in name.replace("’", "'").split() if t]
        return toks[-1].strip(".,;").casefold() if toks else ""

    used: set = set()
    out: list[str] = []
    for seat in panel:
        want = key(seat)
        if not want:
            continue
        for i, name in enumerate(signers):
            if i not in used and key(name) == want:
                out.append(name)
                used.add(i)
                break
    if not out:
        return []
    out.extend(n for i, n in enumerate(signers) if i not in used)
    return out


def _read_signature_band(ctx: _Ctx, model, finder) -> None:
    """Read the closing band: the criteria it states, and the band itself.

    TWO OWNERS, ONE BAND. Where the court set appearances beside the
    signatures, `_read_closing_band` has claimed the whole printed block and
    those rows are consumed; this pass then reads only the NAMES off them.
    Where it printed signatures alone (7 records) the band is unclaimed, and
    it is read here into `Document.signature`."""
    signers: list[str] = []
    for line in _conformed(model, finder):
        signers.extend(_sig_names(line.plain))
    if not signers:
        return
    bench = _signing_bench(signers, ctx.crit.get("panel") or [])
    if bench:
        # THE PRINTED FORM BESIDE THE PARSED ONE, as `panel_line` stands
        # beside `panel`: `judges` is who signed, in full, in seat order.
        # Core fills this field only from a LABELLED roster it walks itself
        # (queue item 65) and the claim means it never sees this one.
        ctx.crit["judges"] = ", ".join(bench)
    if not _EMIT_SIGNATURE_SECTION:
        return

    rail = _BODY_X0 + _RAIL_TOL
    for run in _sig_runs(model, finder, ctx.consumed):
        pm = ctx.pages[run[0].page]
        lines = [l for l in pm.lines
                 if l.plain.strip() and not finder.kind(pm, l)
                 and l.id not in ctx.consumed]
        sig_x0 = min(l.x0 for l in run)
        _top, attest = _band_top(lines, run[0].top, sig_x0, rail)
        band = ([attest] if attest is not None else []) + list(run)
        # A LABEL UNDER A SEAT IS PART OF THE SEAT ('Chief Judge',
        # 'Associate Judge'): a short row in the signature column, no
        # further from the run than the band's own gap.
        lo = min(l.top for l in band)
        hi = max(l.top for l in band)
        ids = {l.id for l in band}
        for line in lines:
            if line.id in ids or line.x0 < sig_x0 - 2.0:
                continue
            if lo - _BAND_GAP <= line.top <= hi + _BAND_GAP:
                band.append(line)
        band.sort(key=lambda l: (l.top, l.x0))
        # FLOW BLOCKS, not HmLines: SectionSpec('signature', …, 'flow', …)
        # renders through `_render_blocks`, which raises on an HmLine. One
        # Paragraph per printed row, right-aligned on the ones the page set
        # right of the measure — the same shape core's own signature lift
        # produces, so whichever carries the band reads identically.
        for line in band:
            ctx.signature.append(m.Paragraph(
                text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
                continuation=True,
                align="" if line is attest else "right"))
            ctx.consumed.add(line.id)


def _sig_runs(model, finder, consumed: set) -> list:
    """The conformed RUNS the document prints, each a stack of signatures on
    one page no more than _BAND_GAP apart."""
    runs: list = []
    cur: list = []
    for line in _conformed(model, finder):
        if line.id in consumed:
            continue
        if not _norm(line.plain).startswith(_SIG_GLYPH):
            continue
        if cur and (line.page != cur[-1].page
                    or line.top - cur[-1].top > _BAND_GAP):
            runs.append(cur)
            cur = []
        cur.append(line)
    if cur:
        runs.append(cur)
    return runs
