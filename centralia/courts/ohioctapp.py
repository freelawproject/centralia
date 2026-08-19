"""Ohio Court of Appeals ('ohioctapp').

Everything unique to ohioctapp lives here. It imports core, never another
court file, and no other court file imports it — ohio.py was READ as the
model for this port (same publisher, same public-domain cite scheme) and is
not touched.

THE COURT IS TWELVE PRINT SHOPS. Ohio's intermediate court sits in twelve
appellate districts and each district sets its own paper; eight of them are
in this corpus. What they share is the top of the page — a bracketed
CITE-AS instruction in the margin, then a centred masthead naming the
court, the district and (usually) the county — and what they share below it
is a LADDER of the same labelled rungs in whatever order the district likes
them: the docket, the trial court's number, the origin recital, the paper's
own name, the judgment, the date, the bench, the appearances.

What actually differs between districts is ONE thing: how the caption's two
columns are divided. So that is the dispatch, and it yields four contracts:

  'colon rail' (25 of 42 — districts 1, 2, 4, 10, 12). The divider is
  TYPED: a column of ':' glyphs, one per caption row, stacked at a single x
  (measured 288.1–306.4 over the corpus, ±1.6pt within a record). This is
  ca6's stacked ')' in another glyph, and it is read the same way — the
  rail is a COLUMN, the colons standing in it are shed from whichever cell
  they landed in, and which side of it a row sits on decides what the row
  is:

      [Cite as State v. Avery, 2026-Ohio-2848.]     10pt, top margin
                IN THE COURT OF APPEALS OF OHIO     the masthead…
                  SECOND APPELLATE DISTRICT         …the district…
                        CLARK COUNTY                …and the county
      STATE OF OHIO          :                      the rail, typed
          Appellee           :   C.A. No. 2025-CA-50
      v.                     :   Trial Court Case No. 24-CR-729(A)
      EDWIN ARTHUR AVERY     :   (Criminal Appeal from Common Pleas Court)
          Appellant          :   FINAL JUDGMENT ENTRY & OPINION
                    . . . . . . . . . . .   a TYPED dotted divider
      Pursuant to the opinion of this court rendered on July 24, 2026, …

  'drawn rail' (6 — district 5). The Fifth draws the divider: one vertical
  rule in the caption band, measured x 291.1–316.7, height 138.5–429.4.
  Nothing else on the page is drawn except the underline beneath the
  paper's own name, whose ends coincide with the row above it — an
  underline, not a fence, by the test ca5 and ca1 both needed.

  'open gutter' (8 — district 6). No rail is drawn and none is typed: the
  gutter is white space, and the measured x0 of the right-hand stack IS the
  divider (va's case). Measured over the eight records the right stack
  starts at 247.6, 297.9 or 324.1 and no left-stack piece begins past
  113.5 — a gutter of 134pt with nothing in it. The band is closed by the
  court's own '* * * * *' rule, which it types above and below the
  appearances.

  'centred ladder' (3 — district 7). There is NO second column and no
  divider to reproduce: the Seventh centres its parties on the page axis
  (measured: every caption row's mid-point within 0.2pt of 306.0 on a
  612pt page) and stacks the ladder underneath, fencing the paper's own
  name between a PAIR of drawn rules of one invariant measure — 286.0pt at
  x0=165.3, on the axis, on all three records. One column is the honest
  reading, so this style emits centred rows and no CaptionBlock at all
  (va's convening order, same reasoning: a stack that is not there must not
  be invented).

A record that shows none of the four is not one of these papers and gets
NOTHING — core's shared walk is a smaller error than a confident
misreading.

THE BRACKETED CITE LINE IS A CITATION, NOT A DOCKET. Every record opens
with '[Cite as State v. Avery, 2026-Ohio-2848.]' at 10pt in the top margin.
'2026-Ohio-2848' is the court's PUBLIC-DOMAIN CITATION and goes in
`citation`; the number this court gave the appeal ('C.A. No. 2025-CA-50',
'No. 26AP-52', 'APPEAL NO. C-250280') goes in `docket_number` and the trial
court's in `lower_court_docket`. Stored the other way round — which is what
ill was doing until 2026-08-20 — the cite displaces a real value and every
cover prints two dockets.

THE BRACKETS STAY. The row is claimed and EMITTED verbatim, role
`citation`, not stripped and not dropped: it is the only place this paper
prints its citation at all (unlike ohio's slip, which sets the cite on its
own row and can afford to record the bracket as apparatus), and the
headmatter renders whole. The Reporter's short form of the case name is
read out of it into `short_case_name`. On a LATER page the same line is a
running head and is recorded as `Dropped(kind="running-head")` — a reader
that claims a region inherits its furniture.

THE MASTHEAD IS THREE ROWS, NOT A STRING. 'IN THE COURT OF APPEALS OF
OHIO' or 'IN THE OHIO COURT OF APPEALS' or 'IN THE COURT OF APPEALS', then
'<ORDINAL> APPELLATE DISTRICT' (with or without ' OF OHIO'), then
'<NAME> COUNTY' (with or without ', OHIO') — and the Tenth prints no county
row at all. All three are read as rows, role `court`, and joined into the
`court` criterion as printed. There is no district field and no county
field on `Criteria`, and inventing one would attach it by setattr and never
serialize, so the printed masthead carries them.

THE PAPER NAMES ITSELF, AND THE NAME IS NEVER MATCHED AS A PHRASE. Inside
the caption's right-hand stack every cell but one answers to a printed
LABEL — a docket label, a trial-court label, an origin recital, a date, a
judgment, a calendar designation. The cell that answers to none is the
paper's own name, and over the corpus that is exactly what it is: 'Opinion
And Judgment Entry', 'Opinion & Judgment Entry', 'FINAL JUDGMENT ENTRY &'
+ 'OPINION', 'DECISION AND JUDGMENT', 'DECISION AND' + 'JUDGMENT ENTRY',
'OPINION AND' + 'JUDGMENT ENTRY', 'JUDGMENT ENTRY'. Below the caption the
same row is found by its FACE instead — letter-spaced ('D E C I S I O N',
'O P I N I O N') or bold and centred ('OPINION AND JUDGMENT ENTRY') — and
it is `title` either way.

THE JUDGMENT ENTRY'S ORDER IS CLAIMED, DELIBERATELY. Districts 1 and 2
print the FINAL JUDGMENT ENTRY as a paper of its own ahead of the opinion,
and under its caption they set the operative order in full measure: 'For
the reasons set forth in the Opinion filed this date, the judgment of the
trial court is affirmed… the mandate be sent to the trial court for
execution under App.R. 27.' Core already places those rows in the
headmatter — that is not changed here; the reader only says what they are,
role `disposition`, and reads the first sentence into `disposition`. Two
reasons it is claimed rather than left: the paper's OWN name says what the
run is ('JUDGMENT ENTRY'), so the reading rests on a printed landmark; and
an untagged row lying between the last tagged row and the first writing is
moved INTO that writing by `pipeline.py` (`court.body_reclaimed`), so
leaving the order untagged would not leave it where the page prints it. The
run is bounded at both ends by printed marks: it opens at the first
full-measure row below a judgment-entry caption and closes at 'For the
court,' (district 2's conformed signature) or 'To the clerk:' (district 1's
journalization box) or the first byline.

WHERE THE BLOCK ENDS: the first paragraph marker ('{¶1}', '{¶ 1}') or the
first byline at the body rail. The byline is matched by THIS COURT'S OWN
PRINTED FORM (`_BYLINE`) and not only by core's grammar, because core cannot
parse the title-case form six of the eight districts use — and a reader that
walks past its own stopping mark does not stop, it mis-files: 'Baldwin, J.'
came out tagged as counsel, one row under the appearances it was continuing.
Both stopping tests run only OUTSIDE the signature and journal runs, because
'ROBERT G. HANSEMAN, JUDGE' and 'LEWIS, P.J., and HUFFMAN, J., concur.' and
'Administrative Judge' all have a byline's shape and none of them opens a
writing.

EVERY RUN IS BOUNDED BY ITS OWN PAGE — the entry's order, the conformed
signature, the journalization box. Each opens on a printed landmark and the
page's foot closes it; carried across the page break, the journal run tagged
quinlan-hall's whole REPRINTED opinion cover, byline included, as
journalization. What the First sets on the next page instead answers to two
printed forms of its own ('By:______', 'Administrative Judge').

WHAT SEPARATES A WRAP FROM A NEW RUNG IS THE PITCH. Every district sets a
continuation on the very next line and leaves a blank line before a new
rung: measured, the wrap pitch is 13.1–15.3pt and the rung pitch
24.0–29.9pt against type of 11.5–13pt. Read by wording instead, 'Case
Nos. 2025-4005, 2025-4006,' — the four trial-court numbers wrapped out of
in_re_m.m.a.'s
origin recital — parses as this court's own docket, and 'FINAL JUDGMENT
ENTRY &' parses as a continuation of the origin above it, which is how the
whole judgment-entry family lost its title on the first pass.

A RAIL COLON STANDS FREE. The typed rail is told from a label's own colon by
whether the glyph stands clear of the word before it: measured, a label's
colon touches its word (0.0–0.6pt) and a rail colon is set 3.3pt clear at
the tightest. Without that test cme_fed's 'Argued:' — whose colon happens to
fall 0.5pt from the rail's column — extended the caption band 148pt down
the page and split the court's own name, its date and its counsel block
across the rail.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES, register

# The shared table in courts/__init__.py registers 'ohioctapp' too, and the
# `_FRONT_MATTER` pass there gives it ('syllabus',). Superseding the entry
# here rather than deleting it there keeps a missed edit from raising
# 'duplicate profile' and taking the whole package down with it (ohio, ala
# and ariz do the same), and the front matter is re-declared because that
# table has already been applied by the time this module is imported.
PROFILES.pop("ohioctapp", None)
OHIOCTAPP = register(CourtProfile(
    "ohioctapp", "Ohio Court of Appeals",
    # THE BYLINE GRAMMAR IS LEFT EXACTLY AS THE SHARED REGISTRY SET IT, and
    # that is a measured decision, not an omission. Six of the eight
    # districts here sign in TITLE CASE ('Baldwin, J.', 'Hess, J.',
    # 'King, P.J.', 'Gormley, J.', 'Popham, J.,'), so `allow_titlecase_name`
    # looks obviously right: with it, 9 records that come back as an
    # unauthored 'order' gain their real author. It also opens 27 PHANTOM
    # writings, because the same rule then takes the conformed roster every
    # district prints at the FOOT of the opinion — 'Thomas J. Osowik, P.J.',
    # 'Gene A. Zmuda, J.', 'Hoffman, P.J. and', 'Gormley, J. concur.' — and
    # each becomes a majority of its own. Measured with the reader popped:
    # 45 writings without the flag, 72 with. The discriminator exists (v1
    # required a title-case byline to be a BARE SURNAME consuming its WHOLE
    # line) but it lives in resolve/bylines.py, which this port does not
    # own, so it is reported as a core patch instead of half-applied here.
    byline=BylineGrammar(style="abbrev"),
    front_matter=("syllabus",),
))

# The four layout contracts, named for the divider each one prints.
STYLE_COLON = "colon rail"
STYLE_DRAWN = "drawn rail"
STYLE_OPEN = "open gutter"
STYLE_AXIS = "centred ladder"

# ---- ohioctapp's declared facts (measured over all 42 records) -----------
# THE TYPED RAIL. Colon glyphs stacked in one column: x 288.1–306.4 over the
# corpus, and within a record every colon's centre lies inside 1.6pt. The
# bucket is 8pt wide, which keeps 'In the Matter of:' (x≈161) and
# 'APPEARANCES:' (x≈352) out of it, and the column must carry at least three
# glyphs to count as a rail.
_RAIL_BUCKET = 8.0
_RAIL_MIN_ROWS = 3
# Where a divider may stand at all: measured 247.6–341.8 on a 612pt page.
_MID_LO, _MID_HI = 0.34, 0.62
# A colon belongs to the rail when it stands in the rail's own column AND
# stands clear of the word before it. Measured: a label's colon touches its
# word (gap 0.0-0.6pt) and a rail colon is set clear of the party name by
# 3.3pt at the tightest (hsbc's justified 'Legatees, Administrators, and
# Executors:' where the colon is 33pt clear).
_RAIL_WINDOW = 10.0
_COLON_CLEAR = 2.0
# THE DRAWN RAIL (district 5): x 291.1–316.7, height 138.5–429.4. Nothing
# else on the page draws a vertical at all, so the window plus a height
# floor takes the rail and only it.
_RULE_MIN_HEIGHT = 40.0
# The caption band is the divider's own extent, opened a little at each end:
# krichbaum sets its first party row 12.4pt ABOVE the head of the drawn rail
# and mayle sets 'BEFORE:' 15.4pt below its foot, so the pads are asymmetric
# and both are measured.
_BAND_PAD_TOP = 20.0
_BAND_PAD_BOTTOM = 12.0
# THE OPEN GUTTER (district 6): the right stack starts at 247.6, 297.9 or
# 324.1 and no left-stack piece begins past 113.5. A piece at or past this
# fraction of the measure is in the right stack; the divider is half an em
# to its left.
_OPEN_RIGHT_MIN = 0.36
_OPEN_MID_BACK = 6.0
# THE CENTRED LADDER (district 7): every caption row's mid-point lies within
# 0.2pt of the page axis, and the paper's own name is fenced between two
# drawn rules of 286.0pt at x0=165.3.
_AXIS_TOL = 4.0
_FENCE_MEASURE = (270.0, 300.0)
_FENCE_AXIS = 14.0
# A CENTRED ROW IS A SHORT ROW: a counsel entry reaching both margins has
# its mid-point on the axis too, so centring is only ever read together
# with a width bound (nh's lesson, reused).
_CENTRED_WIDTH_MAX = 0.74
_CENTRED_TOL = 10.0
# How far the front matter may run. District 1 reprints its whole cover for
# the opinion on page 3 and finishes the appearances there; nothing in the
# corpus needs a fifth page.
_MAX_PAGES = 5
# A WRAP inside a caption cell sits within this multiple of its own type
# size of the row above; a new rung sits a blank line further down.
# Measured: wraps 13.1–15.3pt, rungs 24.0–29.9pt, type 11.5–13pt.
_CAP_PITCH = 1.35
# A row is BODY PROSE when its ink reaches this much of the measure. The
# judgment entry's order runs 92–99% and its short closing lines 23–47%,
# which is why the run continues by state rather than by width.
_PROSE_MEASURE = 0.72
# A ladder run continues while the next row keeps the run's own left edge…
_RUN_EDGE_TOL = 3.5
# …and stands no further below it than this many leadings.
_RUN_GAP_LEADS = 2.2

# THE CITE-AS INSTRUCTION, the one row every record prints above its
# masthead. Its second capture is the court's own public-domain citation.
_CITE_AS = re.compile(
    r"^\[\s*Cite as\s+(.+?),\s*(\d{4}-Ohio-\d+)\s*\.?\s*\]$", re.I)
_CITE_OPEN = re.compile(r"^\[\s*Cite as\b", re.I)
# THE MASTHEAD, in the three forms the districts print it.
_MASTHEAD = re.compile(
    r"^IN THE\s+(?:OHIO\s+)?COURT OF APPEALS(?:\s+OF OHIO)?$", re.I)
_DISTRICT = re.compile(
    r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH"
    r"|ELEVENTH|TWELFTH)\s+APPELLATE DISTRICT(?:\s+OF OHIO)?$", re.I)
_COUNTY = re.compile(r"^[A-Z][A-Za-z .'\-]{2,20}\s+COUNTY(?:\s*,\s*OHIO)?$",
                     re.I)
# A TYPED DIVIDER is a row of nothing but rule glyphs — the Second's dotted
# '. . . . . . . . . . .', the Sixth's '* * * * *', the Twelfth's
# '____________' and the Fourth's 466pt underscore fence.
_TYPED_DIVIDER = re.compile(r"^[.•*_\-‐-―\s]{7,}$")
_TYPED_INK = set(".•*_-‐‑‒–—―")
# THE PAPER'S OWN FIELD LABELS. Each is a label this court prints, never a
# value read by wording.
_DOCKET_LAB = re.compile(
    r"^(?:C\.\s*A\.\s*Nos?\.|Case\s*Nos?\.|Appeal\s*Nos?\.|Nos?\."
    r"|Court of Appeals\s*Nos?\.)\s*\S", re.I)
_DOCKET_ANY = re.compile(
    r"(?:C\.\s*A\.\s*Nos?\.|Case\s*Nos?\.|Appeal\s*Nos?\.|"
    r"Court of Appeals\s*Nos?\.)\s*\S", re.I)
_LOWER_LAB = re.compile(
    r"^(?:\(?\s*)(?:Trial\s*(?:Court)?\s*(?:Case)?\s*Nos?\.|Trial\s*Nos?\."
    r"|C\.\s*P\.\s*C\.\s*Nos?\.)\s*", re.I)
# 'Appeal from the Fairfield County Court of…', '(Criminal Appeal from
# Common Pleas', 'APPEALS from the Franklin County…', 'Civil Appeal From:',
# 'CIVIL APPEAL FROM CLERMONT COUNTY…'. The recital always names the act
# and the direction; the tribunal is never read by wording.
_ORIGIN = re.compile(r"^\(?\s*(?:[A-Za-z]+\s+)?APPEALS?\s+FROM\b", re.I)
_DATE_LAB = re.compile(
    r"^(?:Date of Judgment(?:\s*Entry)?(?:\s*on Appeal)?|Decided"
    r"|Rendered\s+on|Dated|Filed|RELEASED)\s*:?\s*(.*)$", re.I)
_BARE_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_DISPO_LAB = re.compile(
    r"^(?:JUDGMENT|Judgment(?:\s+Appealed\s+From\s+Is)?)\s*:\s*(.*)$", re.I)
# App.R. 11.1 — the court's own calendar designations, a closed set.
_CALENDAR = re.compile(
    r"^\(?\s*(?:REGULAR|ACCELERATED|EXPEDITED)\s+CALENDAR\s*\)?$", re.I)
# What the paper says it is acting on, where it is acting on a filing rather
# than an appeal ('Motion for Reconsideration').
_MOTION = re.compile(r"^(?:Motion|Application|Petition)\b.{0,60}$")
_PANEL_LAB = re.compile(r"^BEFORE\s*:", re.I)
_APPEAR_LAB = re.compile(r"^APPEARANCES?\b", re.I)
# A REPRESENTATION CLAUSE, which is what makes a row counsel. Names and
# firms are never read by wording; the clause is.
_COUNSEL_CUE = re.compile(
    r"\bfor\s+(?:the\s+)?(?:appell|plaintiff|defendant|petitioner|respondent"
    r"|relator|cross-appell|state\b)|\bpro\s+se\b|\bAttorney\s+for\b"
    r"|^On\s+brief\s*:|^Argued\s*:|\bguardian\s+ad\s+litem\b"
    r"|\bNo\s+Response\s+Filed\b"
    # …and the BAR'S OWN DESIGNATIONS, which is what the first line of an
    # entry carries when the representation clause falls on its second
    # ('Paul A. Dobson, Wood County Prosecuting Attorney, and' / 'Kristofer
    # Kristofferson, Assistant Prosecuting Attorney, for appellee.'). A
    # closed vocabulary of offices, never a name.
    r"|\bProsecut(?:or|ing)\b|\bEsq\.|\bAtty\.|\bPublic Defender\b"
    r"|\bAttorney General\b|\bLaw Offices?\b|\bL\.?P\.?A\.?\b",
    re.I)
# The Second's conformed signature and the First's journalization box: two
# printed landmarks, each opening a run that reaches the foot of its page.
_SIG_OPEN = re.compile(r"^For the court\s*,?$", re.I)
_JOURNAL_OPEN = re.compile(r"^To the clerk\s*:?$", re.I)
# …and the two rows the box prints under it, one of which the First sets on
# the NEXT page. Matched as printed forms rather than carried across the
# page break by state: a run that outlives its page swallowed the whole
# opinion cover below it, byline included.
_JOURNAL_LINE = re.compile(r"^(?:Enter upon the journal|Journalized)\b", re.I)
_SIGN_RULE = re.compile(r"^(?:By|Signed)\s*:?\s*_{3,}\s*$", re.I)
_SIGN_TITLE = re.compile(
    r"^(?:Administrative|Presiding|Chief)\s+Judge\s*$", re.I)
_PARA = re.compile(r"^\{\s*¶")
# THE BYLINE, as this court's own paper sets it — a BARE SURNAME, a comma,
# and an abbreviated bench title, occupying the WHOLE line. The reader needs
# this in its own right: `resolve/bylines.py` cannot parse the title-case
# form six of the eight districts use ('Baldwin, J.', 'Hess, J.'), and a
# reader that walks past its own stopping mark tags the byline as the last
# thing it was reading (bath published 'Baldwin, J.' as counsel).
#
# The surname is ONE token by construction, and that is what keeps the three
# byline-shaped impostors out: the conformed signature 'ROBERT G. HANSEMAN,
# JUDGE', the panel's sign-off 'Thomas J. Osowik, P.J.' and the concur
# roster 'LEWIS, P.J., and HUFFMAN, J., concur.' — v1 reached the same rule
# from the other end (`_name_ok`, `_byline_split`).
_BYLINE = re.compile(
    r"^(?:PER CURIAM|[A-Z][A-Za-z'’\-]{1,20},\s*"
    r"(?:P\.\s*J|C\.\s*J|A\.\s*J|J|JJ|Judge)\s*\.?)\s*[,.:]?$")
# A judgment-entry paper says so in its own name; that is what licenses the
# operative-order reading below the caption.
_ENTRY_NAME = re.compile(r"JUDGMENT ENTRY", re.I)
# The disposition words the entry's first sentence closes on — a closed
# vocabulary, because the sentence may instead recite what was heard.
_DISPO_WORDS = (
    "affirmed", "reversed", "vacated", "remanded", "dismissed", "denied",
    "granted", "overruled", "sustained", "modified", "stayed", "withdrawn",
)
# PARTY STATUS is a closed role vocabulary; a party NAME never is. Ohio's
# districts set the status on its own caption row, hyphenated
# ('Plaintiff-Appellee,') or plain ('Appellee', 'Defendant - Appellant').
_STATUS = re.compile(
    r"^\(?\s*(?:Third-Party\s+)?(?:Cross[-\s]*)?"
    r"(?:Plaintiffs?|Defendants?|Appellants?|Appellees?|Petitioners?"
    r"|Respondents?|Relators?|Intervenors?|Movants?)"
    r"[A-Za-z\s\-/,.()\]]*$", re.I)
_PIVOT = re.compile(r"^-?\s*(?:v|vs)\.?\s*-?$", re.I)
_CONNECTOR = re.compile(r"^(?:and|&|et al\.?|,)$", re.I)
# The bench, as the roster prints it: full names in title case, separated by
# ';' or ',', closing on the title 'Judges'.
_PANEL_TITLE = re.compile(r"^(?:Judges?|JJ|J|P\.J|C\.J|A\.J)\.?$", re.I)
_PANEL_NAME = re.compile(
    r"^(?:[A-Z][A-Za-z.'’\-]*\s+){1,3}[A-Z][A-Za-z.'’\-]+$")

_ROLE_CONTINUES = {
    "lower-court", "counsel", "panel", "disposition", "title", "date",
    "case-info", "docket", "caption",
}


def _is_open(text: str) -> bool:
    """Does this cell leave its statement unfinished? A trailing comma,
    hyphen, ampersand or slash, or a parenthesis it never closed. That — and
    only that — lets a LABELLED row still be the wrap of the row above it
    ('Case Nos. 2025-4005, 2025-4006,' / '2025-4007, and 2025-4008')."""
    t = text.rstrip()
    if t.endswith((",", "-", "&", "/", ";")) or t.count("(") > t.count(")"):
        return True
    # …and a cell that ends on a bare LABEL WORD is waiting for its value:
    # the Fifth wraps 'Appeal from the Court of Common Pleas, Case' /
    # 'No. 25CR03-0042', and read as a closed statement the second row is a
    # labelled docket row and the trial court's number was published as a
    # companion appeal of this court's.
    return bool(re.search(r"\b(?:Case|Trial|Court|Nos?|Appeal)$", t, re.I))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


# --------------------------------------------------------------------------
# the page's own dividers — the dispatch
# --------------------------------------------------------------------------

def _free_colons(line) -> list:
    """The colons in ``line`` that stand FREE — the line's first ink glyph,
    or one the compositor set clear of the word before it.

    This is what tells a rail glyph from a label's own punctuation. cme's
    appearances print 'Menge, for appellee. Argued: Neil C. Sander.' and the
    colon in 'Argued:' happens to fall 0.5pt from the caption rail's own
    column, which extended the caption band 148pt down the page and split
    the court's name, its date and its counsel block across the rail."""
    ink = sorted((c for c in (line.chars or [])
                  if (c.get("text") or "").strip()), key=lambda c: c["x0"])
    out = []
    prev = None
    for ch in ink:
        if (ch.get("text") or "") == ":" and (
                prev is None
                or ch["x0"] - prev.get("x1", prev["x0"]) >= _COLON_CLEAR):
            out.append(ch)
        prev = ch
    return out


def _colon_rail(pm, near: float | None = None) -> float | None:
    """The x of this page's TYPED colon rail, or None.

    A rail is a COLUMN, so the glyphs are bucketed by where they stand and
    the largest bucket wins. ``near`` pins the search to the rail page 1
    measured: the same record sets it at the same x on every page, and a
    body page that happens to stack three colons is not this court's
    caption."""
    buckets: dict[int, list[float]] = {}
    for line in pm.lines:
        for ch in _free_colons(line):
            x = (ch["x0"] + ch.get("x1", ch["x0"])) / 2
            if not (pm.width * _MID_LO <= x <= pm.width * _MID_HI):
                continue
            if near is not None and abs(x - near) > _RAIL_WINDOW:
                continue
            buckets.setdefault(int(round(x / _RAIL_BUCKET)), []).append(x)
    if not buckets:
        return None
    best = max(buckets.values(), key=len)
    if len(best) < _RAIL_MIN_ROWS:
        return None
    return sorted(best)[len(best) // 2]


def _drawn_rail(pm, near: float | None = None):
    """The caption's DRAWN divider on this page, or None."""
    rails = [v for v in (pm.v_rules or [])
             if pm.width * _MID_LO <= v.x <= pm.width * _MID_HI
             and (v.bottom - v.top) >= _RULE_MIN_HEIGHT
             and (near is None or abs(v.x - near) <= _RAIL_WINDOW)]
    if not rails:
        return None
    return max(rails, key=lambda v: v.bottom - v.top)


def _fence_tops(pm) -> list[float]:
    """The tops of the Seventh's rule pair — 286pt on the page axis."""
    out = []
    for r in (pm.h_rules or []):
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        out.append(r.top)
    return sorted(out)



def _star_tops(pm) -> list[float]:
    """The tops of the Sixth's typed star rule, which fences its
    appearances above and below and so closes the caption."""
    return sorted(min(p.top for p in row) for row in _rows(pm)
                  if set(_norm(" ".join(p.plain for p in row)).split())
                  == {"*"})


def _rows(pm):
    """This page's rows, in page order, each as its list of pieces.

    Grouped by pdfio's own row key so a row the extractor split at a
    vertical rule or a column gap comes back whole — the caption is then
    split at the DIVIDER, glyph by glyph, and not where the gap happened to
    be wide enough (ca6's lesson)."""
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
    """The part of ``line`` lying on one side of the divider, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _shed_rail(line, mid: float):
    """``line`` with the rail's own colons removed, or None when the line
    WAS the rail. The glyph is identified by its COLUMN, never by its
    character: a ':' closing 'In the Matter of:' is not in the rail's
    column and stays where the court typed it."""
    rail = {id(c) for c in _free_colons(line)
            if abs((c["x0"] + c.get("x1", c["x0"])) / 2 - mid)
            <= _RAIL_WINDOW}
    if not rail:
        return line
    kept = [c for c in line.chars if id(c) not in rail]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    x0 = min(c["x0"] for c in kept)
    x1 = max(c.get("x1", c["x0"]) for c in kept)
    return _replace(line, chars=kept, x0=x0, x1=x1)


def _dispatch(pm):
    """Which of the four contracts this paper prints, or (None, None).

    Tried divider first, divider second: a typed rail, then a drawn one,
    then the page axis, then a measured gutter. Nothing is decided from a
    title or a district name — the district only tells us which shop set
    the page, and the shops change."""
    colon = _colon_rail(pm)
    if colon is not None:
        return STYLE_COLON, colon
    rail = _drawn_rail(pm)
    if rail is not None:
        return STYLE_DRAWN, rail.x
    body = [r for r in _rows(pm) if not _is_masthead_row(r)]
    fences = _fence_tops(pm)
    if len(fences) >= 2:
        band = [r for r in body if max(p.bottom for p in r) < fences[0]]
        if len(band) >= 3 and all(_row_centred(r, pm) for r in band):
            return STYLE_AXIS, None
    # THE OPEN GUTTER. The right stack is found from the PIECES a row is set
    # in, never from where the row starts: the Sixth sets both stacks on one
    # visual row, so every row's own x0 is its LEFT column's and the right
    # column is invisible to a whole-row test (which is how eight records
    # went unread on the first pass).
    stars = _star_tops(pm)
    if len(stars) >= 2:
        band = [r for r in body if max(p.bottom for p in r) < stars[0]]
        right = [p.x0 for r in band for p in r
                 if p.x0 >= pm.width * _OPEN_RIGHT_MIN]
        if len(right) >= 2:
            return STYLE_OPEN, min(right) - _OPEN_MID_BACK
    return None, None


def _is_masthead_row(row) -> bool:
    t = _norm(" ".join(p.plain for p in row))
    return bool(_CITE_AS.match(t) or _MASTHEAD.match(t)
                or _DISTRICT.match(t) or _COUNTY.match(t))



def _row_centred(row, pm) -> bool:
    x0 = min(p.x0 for p in row)
    x1 = max(p.x1 for p in row)
    return (abs((x0 + x1) / 2 - pm.width / 2) <= _AXIS_TOL
            and (x1 - x0) <= pm.width * _CENTRED_WIDTH_MAX)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ohioctapp")
def read_headmatter_ohioctapp(model, geom, **_):
    """Read one of ohioctapp's four papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    style, mid = _dispatch(page1)
    if style is None:
        return NOTHING
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    lead = geom.lead if geom and geom.lead else body_size * 2.2
    finder = FurnitureFinder(model, body_x0, body_size)

    ctx = _Ctx(geom, body_size)
    walk = _Walk(ctx, style, mid, geom, body_x0, body_size, lead)
    for pm in model.pages[:_MAX_PAGES]:
        if walk.done:
            break
        walk.page(pm, finder)
    walk.flush()

    # THE CRITERIA ARE BUILT BEFORE THEY ARE JUDGED. `finish()` is what
    # reads the walk's collected cells into `docket_number` and `citation`;
    # asking for them first would refuse every record just read correctly
    # (wyo shipped that inversion and lost all 50 of its own records).
    walk.finish()
    if not ctx.crit.get("citation") and not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result(walk.anchor)


class _Walk:
    """The classifier. One page at a time; the caption band by its divider,
    everything else by its own printed landmark."""

    def __init__(self, ctx, style, mid, geom, body_x0, body_size, lead):
        self.ctx = ctx
        self.style = style
        self.mid = mid
        self.geom = geom
        self.body_x0 = body_x0
        self.body_size = body_size
        self.lead = lead
        self.done = False
        self.anchor: list[int] = []
        self.parser = BylineParser(OHIOCTAPP.byline)
        # the pending caption stacks, flushed at the foot of each band
        self.left: list = []
        self.right: list = []
        self.cap_ids: list[int] = []
        self.cap_page = 1
        # the right stack's last tenant: its top, its text and its role, which
        # is what tells a wrap from a new rung
        self.r_top: float | None = None
        self.r_text = ""
        self.r_role: str | None = None
        # the run the ladder is inside, and where it sits
        self.run: str | None = None
        self.run_x0 = 0.0
        self.run_bottom = 0.0
        # the pitch anchor: the top of the row the run last placed, and the
        # top and type size of the row now being read
        self.run_top: float | None = None
        self.row_top = 0.0
        self.row_size = 0.0
        # whether the row just placed WRAPPED the one above it, so the parsed
        # forms can join the two instead of filing three fragments
        self.wrapped = False
        self.state = "head"      # head | ladder | order | signature | journal
        # the printed forms, kept beside the parsed ones
        self.masthead: list[str] = []
        self.cap_rows: list[str] = []
        self.cite: tuple[str, str] | None = None
        self.cite_open = False
        self.cite_rows: list = []
        self.cite_text = ""
        self.dockets: list[str] = []
        self.lower_nos: list[str] = []
        self.origin: list[str] = []
        self.dates: list[str] = []
        self.dispo: list[str] = []
        self.order: list[str] = []
        self.counsel: list[str] = []
        self.panel: list[str] = []
        self.titles: list[str] = []
        # THE PAPER'S OWN NAME IS THE FIRST RUN. Districts 1 and 2 print two
        # covers, the judgment entry's and the opinion's, and joining both
        # published a title of 'FINAL JUDGMENT ENTRY & OPINION OPINION'.
        self.title_run: list[str] = []
        self.title_done = False

    # -- one page -------------------------------------------------------
    def page(self, pm, finder) -> None:
        # THE SIGNATURE, THE JOURNAL BOX AND THE ENTRY'S ORDER ARE BOUNDED BY
        # THEIR PAGE. Each of the three opens on a printed landmark and the
        # page's foot is its close; carried into the next page, the journal
        # run tagged quinlan-hall's whole reprinted opinion cover — its
        # origin, its appearances and its byline — as journalization.
        if self.state in ("signature", "journal", "order"):
            self.state = "ladder"
            self.run = self.run_top = None
        band = self._band(pm)
        stream: list = []
        for row in _rows(pm):
            stream.append((min(p.top for p in row), 0, row))
        for r in (pm.h_rules or []):
            if not self._is_underline(pm, r):
                stream.append((r.top, 1, r))
        stream.sort(key=lambda t: (t[0], t[1]))
        for top, kind, item in stream:
            if self.done:
                break
            if kind == 1:
                self.flush()
                self.ctx.rule(pm.number, span=(
                    "right" if item.x0 > pm.width / 2 - 20.0 else "center"))
                continue
            if band and band[0] <= top <= band[1]:
                self._caption(pm, item)
                continue
            self.flush()
            self._ladder(pm, item, finder)
        self.flush()

    def _band(self, pm):
        """The caption band on this page, or None: the divider's own extent
        (the typed and drawn rails) or the run the court's own marks close
        (the open gutter and the centred ladder)."""
        if self.style is STYLE_COLON:
            x = _colon_rail(pm, near=self.mid)
            if x is None:
                return None
            tops = [(l.top, l.bottom) for l in pm.lines
                    if any(abs((c["x0"] + c.get("x1", c["x0"])) / 2 - x)
                           <= _RAIL_WINDOW for c in _free_colons(l))]
            if not tops:
                return None
            return (min(t for t, _ in tops) - _BAND_PAD_TOP,
                    self._extend(pm, max(b for _, b in tops), x))
        if self.style is STYLE_DRAWN:
            rail = _drawn_rail(pm, near=self.mid)
            if rail is None:
                return None
            return (rail.top - _BAND_PAD_TOP,
                    self._extend(pm, rail.bottom, rail.x))
        if pm.number != 1:
            return None
        rows = [r for r in _rows(pm) if not _is_masthead_row(r)]
        # THE COURT'S OWN MARK CLOSES THE BAND — the Sixth's star rule, the
        # Seventh's first fence. Bounding it by 'everything down the page
        # that could be a caption row' instead swallowed the appearances.
        if self.style is STYLE_OPEN:
            close = _star_tops(pm)
        else:
            close = _fence_tops(pm)
        if not close:
            return None
        band = [r for r in rows if max(p.bottom for p in r) < close[0]]
        if self.style is STYLE_AXIS:
            band = [r for r in band if _row_centred(r, pm)]
        if not band:
            return None
        return (min(min(p.top for p in r) for r in band) - 2.0,
                max(max(p.bottom for p in r) for r in band) + 2.0)

    def _extend(self, pm, bottom: float, mid: float) -> float:
        """The band's foot, followed past the last rail glyph.

        The rail stops where the party column stops, and on the longer
        papers the right stack runs on below it — state_v._cox sets 'FINAL
        JUDGMENT ENTRY &' and 'OPINION' 14 and 28pt under its last colon.
        A row is still the caption's while it lies ENTIRELY right of the
        divider (min x0, not the mid-point: the dotted divider below is
        centred on the page axis and its mid-point reads as right-hand),
        it is not a typed divider, and it stands within a leading and a half
        of the row above it."""
        stop = float("inf")
        for row in _rows(pm):
            top = min(p.top for p in row)
            if top <= bottom:
                continue
            text = _norm(" ".join(p.plain for p in row))
            if not text or (_TYPED_DIVIDER.match(text)
                            and set(text.replace(" ", "")) <= _TYPED_INK) \
                    or min(p.x0 for p in row) <= mid \
                    or top - bottom > self.lead * 1.6:
                stop = top
                break
            bottom = max(p.bottom for p in row)
        # THE PAD MAY NOT REACH THE ROW THAT CLOSED THE BAND. state_v._cox
        # types its dotted divider 1.9pt under the last title row, so a flat
        # 12pt pad pulled the divider into the caption and split it at the
        # rail — half of it filed as a party, half as the paper's own name.
        return min(bottom + _BAND_PAD_BOTTOM, stop - 1.0)

    def _is_underline(self, pm, r) -> bool:
        """A rule whose ends coincide with the row above it is emphasis, not
        a fence — ca1's and ca5's test, and the Fifth, Fourth, Sixth and
        Twelfth all need it for the underline under the paper's own name.

        MEASURED AGAINST THE ROW'S INK, never its line box: the Sixth sets
        its right-hand column with a leading space, so the line begins 76pt
        left of the ink and of the rule, and a line-box test read that
        underline as a fence and cut the caption block in two."""
        for line in pm.lines:
            if abs(r.top - line.bottom) > 6.0:
                continue
            ink = [c for c in line.chars if (c.get("text") or "").strip()]
            if not ink:
                continue
            x0 = min(c["x0"] for c in ink)
            x1 = max(c.get("x1", c["x0"]) for c in ink)
            if abs(r.x0 - x0) <= 6.0 and abs(r.x1 - x1) <= 8.0:
                return True
        return False

    # -- the caption ----------------------------------------------------
    def _caption(self, pm, row) -> None:
        """One caption row, split at the divider and filed by side."""
        self.cap_page = pm.number
        if self.style is STYLE_AXIS:
            # No divider, no second stack: the Seventh centres one column.
            text = _norm(" ".join(p.plain for p in row))
            if not text:
                return
            self.cap_rows.append(text)
            self.ctx.emit(row, "caption", pm, centred=True)
            return
        mid = self.mid
        pieces = []
        for line in row:
            shed = _shed_rail(line, mid) if self.style is STYLE_COLON else line
            if shed is not None:
                pieces.append(shed)
        if not pieces:
            self.cap_ids.extend(l.id for l in row)
            self.ctx.consumed.update(l.id for l in row)
            return
        l_cells, r_cells = [], []
        for line in pieces:
            for side, bucket in ((_side(line, mid, "L"), l_cells),
                                 (_side(line, mid, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left_text = _norm(" ".join(c.plain for c in l_cells))
        right_text = _norm(" ".join(c.plain for c in r_cells))
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
            self.r_top = min(p.top for p in row)
            self.r_text = right_text
            self.r_role = role

    def _right_role(self, row, text: str) -> str:
        """What a right-hand cell is, by the LABEL the court printed on it.

        The stack holds the docket, the trial court's number, the origin
        recital, the date, the judgment and the calendar designation — each
        labelled — and one cell that carries no label at all. That cell is
        the paper's own name, on all 42 records.

        WHAT SEPARATES A NEW RUNG FROM A WRAP IS THE PITCH, not the wording.
        Every district sets a continuation on the VERY NEXT line and leaves a
        blank line before a new rung: measured over the corpus the wrap pitch
        is 13.1–15.3pt and the rung pitch 24.0–29.9pt, against type of
        11.5–13pt. Read by wording instead, 'Case Nos. 2025-4005,
        2025-4006,' — the four trial-court numbers wrapped out of
        in_re_m.m.a.'s origin recital — parses as this court's own docket,
        and 'FINAL JUDGMENT ENTRY &' parses as a continuation of the origin
        above it (which is how the whole judgment-entry family lost its
        title on the first pass)."""
        top = min(p.top for p in row)
        size = max((p.size or 0.0) for p in row) or self.body_size
        wrap = (self.r_top is not None
                and 0 < top - self.r_top <= size * _CAP_PITCH)
        labelled = any(rx.match(text) for rx in (
            _ORIGIN, _LOWER_LAB, _DOCKET_LAB, _DATE_LAB, _DISPO_LAB,
            _CALENDAR, _BARE_DATE))
        if wrap and self.r_role and (not labelled or _is_open(self.r_text)):
            self.wrapped = True
            return self.r_role
        self.wrapped = False
        if _ORIGIN.match(text) or _LOWER_LAB.match(text):
            return "lower-court"
        if _DOCKET_LAB.match(text):
            return "docket"
        if _DATE_LAB.match(text) or _BARE_DATE.match(text):
            return "date"
        if _DISPO_LAB.match(text):
            return "disposition"
        if _CALENDAR.match(text):
            return "case-info"
        return "title"

    def _put(self, bucket: list, text: str) -> None:
        """File one row's text, JOINED to the row above it where it wrapped.

        A wrap carries no space at a hyphen: the Second breaks its trial
        docket mid-token ('Trial Court Case Nos. 2024 CR' / '01611/2; …')."""
        if self.wrapped and bucket:
            prev = bucket[-1]
            bucket[-1] = (prev + text) if prev.endswith("-") \
                else f"{prev} {text}"
            return
        bucket.append(text)

    def _name_paper(self, text: str) -> None:
        if self.title_done:
            return
        self._put(self.title_run, text)

    def _file_right(self, role: str, text: str) -> None:
        if role != "title" and self.title_run:
            self.title_done = True
        # A DOCKET LIST IS NOT A STATEMENT: the Sixth sets its two
        # consolidated appeal numbers on consecutive lines, and joining them
        # made one docket out of two.
        if role == "docket":
            self.dockets.append(text)
        elif role == "lower-court":
            if _ORIGIN.match(text) or self.origin:
                self._put(self.origin, text)
            elif self.wrapped and self.lower_nos \
                    and not re.search(r"\d$", self.lower_nos[-1]):
                # A WRAP THAT BROKE MID-NUMBER is joined; one that broke
                # AFTER a whole number is a second number. The Second wraps
                # 'Trial Court Case Nos. 2024 CR' / '01611/2; …' and the
                # Sixth stacks two complete trial numbers, and only the
                # trailing digit tells the two apart.
                self._put(self.lower_nos, text)
            else:
                self.lower_nos.append(text)
        elif role == "date":
            self.dates.append(text)
        elif role == "disposition":
            self._put(self.dispo, text)
        elif role == "title":
            self._put(self.titles, text)
            self._name_paper(text)

    def flush(self) -> None:
        """Close the pending caption block."""
        if not self.left and not self.right:
            return
        # THE RAIL'S OWN RUN IS NOT THE CAPTION'S RHYTHM: a row that held
        # only the divider is empty on both sides once the glyph is shed,
        # and left standing it renders as a phantom blank row (ca6).
        while self.left and not _strip_tags(self.left[-1].text).strip() \
                and not _strip_tags(self.right[-1].text).strip():
            self.left.pop()
            self.right.pop()
        if self.left:
            self.ctx.caption(self.cap_page, self.left, self.right,
                             self._rail_glyph(), self.cap_ids)
        self.left, self.right, self.cap_ids = [], [], []

    def _rail_glyph(self) -> str | None:
        if self.style is STYLE_COLON:
            return ":"
        if self.style is STYLE_DRAWN:
            return "|"
        return None

    # -- everything outside the caption band ----------------------------
    def _ladder(self, pm, row, finder) -> None:
        text = _norm(" ".join(p.plain for p in row))
        if not text:
            return
        first = row[0]
        x0 = min(p.x0 for p in row)
        x1 = max(p.x1 for p in row)
        measure = (self.geom.right_x1 - self.body_x0) if self.geom \
            and self.geom.right_x1 else pm.width * 0.78
        wide = (x1 - x0) >= measure * _PROSE_MEASURE
        centred = _row_centred(row, pm) or (
            abs((x0 + x1) / 2 - pm.width / 2) <= _CENTRED_TOL
            and (x1 - x0) <= pm.width * _CENTRED_WIDTH_MAX)

        # THE CITE-AS LINE, claimed before the furniture pass can take it:
        # page 1's is the only place this paper prints its citation, and a
        # later page's is the running head. IT MAY WRAP — the Tenth sets it
        # flush right and breaks it at the reporter's own hyphen ('2026-' /
        # 'Ohio-3081.]'), so the run is closed by the BRACKET and not by the
        # row, and joined without a space at that hyphen.
        if self.cite_open or _CITE_OPEN.match(text):
            self.cite_rows.append(row)
            self.cite_text = (self.cite_text + text) \
                if self.cite_text.endswith("-") \
                else (self.cite_text + " " + text).strip()
            self.cite_open = not text.rstrip().endswith("]")
            if self.cite_open:
                return
            mm = _CITE_AS.match(_norm(self.cite_text))
            for part in self.cite_rows:
                if pm.number == 1 and self.cite is None:
                    self.ctx.emit(part, "citation", pm)
                else:
                    self.ctx.drop(part, "running-head")
            if pm.number == 1 and self.cite is None and mm:
                self.cite = (mm.group(1), mm.group(2))
            elif pm.number == 1 and self.cite is None:
                self.cite = ("", "")
            self.cite_rows, self.cite_text = [], ""
            return
        if pm.number > 1 and finder.kind(pm, row[0]):
            return                       # core's furniture pass records it

        # THE BLOCK ENDS at the paragraph marker or at a byline — and the
        # byline test is only ever run OUTSIDE the signature and journal
        # runs, where 'ROBERT G. HANSEMAN, JUDGE' and 'Administrative
        # Judge' have a byline's shape and open nothing.
        if _PARA.match(text):
            self.done = True
            return
        if self.state not in ("signature", "journal") and self._byline(text,
                                                                      x0, x1,
                                                                      measure):
            self.done = True
            return

        if _TYPED_DIVIDER.match(text) and set(text.replace(" ", "")) \
                <= _TYPED_INK:
            self.ctx.rule_row(row, pm)
            # THE SIXTH FENCES ITS APPEARANCES BETWEEN TWO STAR RULES, so
            # the first one opens the band and the second closes it. That is
            # the only bound those entries have: their first line carries the
            # office and the representation clause falls on the second.
            if self.style is STYLE_OPEN and text.replace(" ", "") \
                    and set(text.replace(" ", "")) == {"*"}:
                self.state = "counsel" if self.state != "counsel" else "ladder"
            self.run = self.run_top = None
            return

        if self.state == "head":
            if _MASTHEAD.match(text) or _DISTRICT.match(text) \
                    or _COUNTY.match(text):
                self.masthead.append(text)
                self.ctx.emit(row, "court", pm, centred=True)
                return
        if _MASTHEAD.match(text) or _DISTRICT.match(text) \
                or _COUNTY.match(text):
            # A reprinted cover's masthead (district 1 sets one on page 3).
            self.ctx.emit(row, "court", pm, centred=True)
            return

        if _JOURNAL_LINE.match(text):
            self.ctx.emit(row, "case-info", pm)
            self.run = self.run_top = None
            return
        if _SIGN_RULE.match(text) or _SIGN_TITLE.match(text):
            self.ctx.emit(row, "author", pm)
            self.run = self.run_top = None
            return
        if _SIG_OPEN.match(text):
            self.state = "signature"
            self.ctx.emit(row, "author", pm)
            self.run = self.run_top = None
            return
        if _JOURNAL_OPEN.match(text):
            self.state = "journal"
            self.ctx.emit(row, "case-info", pm)
            self.run = self.run_top = None
            return
        if self.state == "signature":
            # The conformed signature, then the concur roster below it.
            role = "panel" if re.search(r"\bconcur", text, re.I) else "author"
            if role == "panel":
                self.panel.append(text)
            self.ctx.emit(row, role, pm)
            return
        if self.state == "journal":
            self.ctx.emit(row, "case-info", pm)
            return

        self.row_top = min(p.top for p in row)
        self.row_size = max((p.size or 0.0) for p in row)
        role = self._rung(text, pm, row, centred, wide, x0)
        if role is None:
            return                       # left for core's shared walk
        self._file_rung(role, text)
        self.ctx.emit(row, role, pm, centred=centred and role != "counsel")
        self.run, self.run_x0 = role, x0
        self.run_bottom = max(p.bottom for p in row)
        self.run_top = self.row_top
        if role == "title":
            self.anchor.extend(p.id for p in row)

    def _rung(self, text, pm, row, centred, wide, x0) -> str | None:
        """Which rung of the ladder this row is, by its own landmark."""
        self.wrapped = False
        if _PANEL_LAB.match(text):
            self.state = "ladder"
            return "panel"
        if _APPEAR_LAB.match(text):
            self.state = "ladder"
            return "counsel"
        if _DISPO_LAB.match(text):
            self.state = "ladder"
            return "disposition"
        if _ORIGIN.match(text):
            self.state = "ladder"
            return "lower-court"
        if _DATE_LAB.match(text) or _BARE_DATE.match(text):
            self.state = "ladder"
            return "date"
        if _CALENDAR.match(text):
            return "case-info"
        if _COUNSEL_CUE.search(text):
            if self.state != "counsel":
                self.state = "ladder"
            return "counsel"
        if self.state == "counsel":
            return "counsel"
        # A WRAP OF THE ORIGIN RECITAL, by the same pitch the caption uses.
        # The Twelfth and the Seventh both set the tribunal, its division and
        # its case number on three consecutive lines, and read row by row the
        # second is an all-caps centred row (so, the paper's own name) and
        # the third is this court's docket.
        wrap = (self.run_top is not None
                and 0 < self.row_top - self.run_top
                <= (self.row_size or self.body_size) * _CAP_PITCH)
        if wrap and self.run == "lower-court":
            self.wrapped = True
            return "lower-court"
        if _DOCKET_ANY.search(text) and len(text) <= 60 and not wide:
            return "docket"
        if wrap and self.run in _ROLE_CONTINUES:
            self.wrapped = True
            return self.run
        # THE JUDGMENT ENTRY'S OPERATIVE ORDER. Licensed by the paper's own
        # name and bounded by the marks above; see the module docstring.
        if self.state == "order":
            return "disposition"
        # …and it may only OPEN below the caption of a paper that named
        # itself a judgment entry, and only where nothing of the ladder has
        # been reached yet: districts 1 and 2 print no appearances and no
        # bench above the byline on the entry page, and every other district
        # prints no prose there at all.
        if wide and self.cap_rows and self._is_entry() \
                and not self.counsel and not self.panel:
            self.state = "order"
            return "disposition"
        # THE PAPER'S OWN NAME, below the caption, found by its FACE: letter
        # spaced or bold, centred, and short.
        if centred and not wide and (
                self._letterspaced(text)
                or all(bool(p.all_bold) for p in row)
                or (row[0].size or 0) > self.body_size + 0.5
                # 'OPINION' on the axis, roman and at body size — the Fifth
                # sets the paper's name that way between the appearances and
                # the byline. Caps and short, and every other rung of the
                # ladder has already been tested above it.
                or (text.isupper() and len(text) <= 40)):
            return "title"
        if _MOTION.match(text) and centred:
            return "case-info"
        # A RUN ALSO CONTINUES while the next row keeps its left edge (or the
        # axis) and stands within two leadings of it.
        if self.run in _ROLE_CONTINUES:
            near = abs(x0 - self.run_x0) <= _RUN_EDGE_TOL or (
                centred and self.run in ("lower-court", "title", "date",
                                         "panel", "disposition", "case-info"))
            if near and min(p.top for p in row) - self.run_bottom \
                    <= self.lead * _RUN_GAP_LEADS:
                self.wrapped = True
                return self.run
        return None

    def _is_entry(self) -> bool:
        return any(_ENTRY_NAME.search(t) for t in self.titles) or \
            any(_ENTRY_NAME.search(t) for t in self.cap_rows)

    @staticmethod
    def _letterspaced(text: str) -> bool:
        """'D  E  C  I  S  I  O  N' — the court tracks its own name out."""
        toks = text.split()
        return len(toks) >= 4 and sum(1 for t in toks if len(t) == 1) \
            >= len(toks) * 0.8

    def _byline(self, text, x0, x1, measure) -> bool:
        """A byline ends the reader — at the body rail, short, and either the
        court's own printed form or one core's grammar recognizes."""
        if abs(x0 - self.body_x0) > 40.0:
            return False
        if (x1 - x0) > measure * 0.55:
            return False
        if _BYLINE.match(text):
            return True
        return self.parser.parse(text) is not None

    def _file_rung(self, role: str, text: str) -> None:
        if role != "title" and self.title_run:
            self.title_done = True
        if role == "panel":
            self._put(self.panel, text)
        elif role == "counsel":
            self._put(self.counsel, text)
        elif role == "lower-court":
            self._put(self.origin, text)
        elif role == "date":
            self.dates.append(text)
        elif role == "disposition":
            self._put(self.order if self.state == "order"
                      else self.dispo, text)
        elif role == "title":
            self._put(self.titles, text)
            self._name_paper(text)
        elif role == "docket":
            self.dockets.append(text)

    # -- the parsed forms ------------------------------------------------
    def finish(self) -> None:
        crit = self.ctx.crit
        crit["headmatter_style"] = self.style
        if self.cite and self.cite[1]:
            crit["citation"] = self.cite[1]
            if self.cite[0]:
                crit["short_case_name"] = _norm(self.cite[0])
        if self.masthead:
            crit["court"] = ", ".join(self.masthead)
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
        low = _numbers(self.lower_nos) + _numbers(
            [t for t in self.origin if _DOCKET_ANY.search(t)])
        if low:
            crit["lower_court_docket"] = low
        if self.origin:
            stated = _norm(" ".join(self.origin)).strip("() ,")
            cut = re.search(r"\b(?:Case|Trial)\s*Nos?\.", stated, re.I)
            if cut:
                stated = stated[:cut.start()].strip("() ,-")
            if stated:
                crit["lower_court"] = stated
        if self.dates:
            crit["decision_date"] = _date_value(self.dates[0])
        if self.dispo:
            val = _dispo_value(self.dispo)
            if val:
                crit["disposition"] = val
        elif self.order:
            val = _order_value(self.order)
            if val:
                crit["disposition"] = val
        if self.counsel:
            crit["attorneys"] = _norm(" ".join(self.counsel))[:4000]
        if self.panel:
            line = _norm(" ".join(self.panel))
            crit["panel_line"] = line
            seat = _panel_names(line)
            if seat:
                crit["panel"] = seat
                crit["judges"] = ", ".join(seat)
        if self.title_run:
            crit["title"] = _norm(" ".join(self.title_run))


# --------------------------------------------------------------------------
# what the rungs say
# --------------------------------------------------------------------------

def _numbers(rows: list[str]) -> list[str]:
    """The case numbers a labelled row carries, with the label removed."""
    out: list[str] = []
    for row in rows:
        # THE LABEL IS OPTIONAL: the Tenth prints its docket as a bare
        # 'No. 26AP-52', and a pattern that required the label word dropped
        # the number entirely and left the criterion unset on four records.
        # THE LABEL MAY STAND ANYWHERE IN THE ROW. The Second heads its
        # opinion paper with the COUNTY before the label ('MONTGOMERY C.A.
        # Nos. 30681; 30682; 30683'), and anchoring the strip at the row's
        # head published that whole string as a companion docket.
        body = re.sub(
            r"^.*?\(?\s*(?:(?:C\.\s*A\.|Case|Appeal|Trial(?:\s*Court)?"
            r"|Court of Appeals|C\.\s*P\.\s*C\.)\s*"
            r"(?:Court\s*)?(?:Case\s*)?)?Nos?\.\s*", "", _norm(row),
            flags=re.I)
        body = _unwrap(body)
        if not body or body.lower().startswith(("no.", "nos.")):
            continue
        for piece in re.split(r";|,\s*(?=\d)|\band\b", body):
            piece = _unwrap(piece)
            if piece and piece not in out:
                out.append(piece)
    return out


def _unwrap(text: str) -> str:
    """Trim a number of its punctuation, PARENTHESES BALANCED. The Second's
    trial dockets carry their own bracket ('24-CR-729(A)') and a blind strip
    of '()' published '24-CR-729(A'."""
    t = text.strip(" ,.;")
    changed = True
    while changed and t:
        changed = False
        if t.startswith("(") and t.count("(") > t.count(")"):
            t, changed = t[1:].strip(" ,.;"), True
        if t.endswith(")") and t.count(")") > t.count("("):
            t, changed = t[:-1].strip(" ,.;"), True
    return t


def _date_value(text: str) -> str:
    mm = _DATE_LAB.match(_norm(text))
    if mm and mm.group(1).strip(" .:"):
        return mm.group(1).strip(" .:")
    return _norm(text).strip(" .:")


def _dispo_value(rows: list[str]) -> str | None:
    whole = _norm(" ".join(rows))
    mm = _DISPO_LAB.match(whole)
    val = (mm.group(1) if mm else whole).strip(" .;")
    return val or None


def _order_value(rows: list[str]) -> str | None:
    """The judgment the entry's order states, from its FIRST sentence.

    The rest of the run is the mandate's own machinery (costs, service on
    the clerk, App.R. 27), which states no disposition."""
    whole = _norm(" ".join(rows))
    for sentence in re.split(r"(?<=\.)\s+", whole):
        words = {w.strip(".,;:()’'").lower() for w in sentence.split()}
        if any(w in words for w in _DISPO_WORDS):
            return sentence.strip()
    return None


def _party_names(rows: list[str]) -> list[str]:
    """The party names, built from the rows a status label does NOT close.

    Joining the caption wholesale yields 'STATE OF OHIO Appellee v. EDWIN
    ARTHUR AVERY Appellant'."""
    names: list[str] = []
    run: list[str] = []
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        # A CONNECTOR IS NOT A NAME: the First stacks co-parties with a bare
        # 'and' on its own row, and joined into the run it published a party
        # called 'and TOM HALL'.
        if _CONNECTOR.match(flat) or _PIVOT.match(flat) \
                or _STATUS.match(flat) or _CALENDAR.match(flat):
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


def _panel_names(line: str) -> list[str]:
    """The judges the roster names, in the order it names them.

    The names are full and in title case ('William B. Hoffman; Craig R.
    Baldwin; David M. Gormley, Judges'), so the BENCH TITLES are the closed
    vocabulary and everything else that reads as a personal name is a
    judge."""
    line = re.sub(r"^(?:BEFORE|Before)\s*:\s*", "", _norm(line))
    line = re.sub(r"^For the court\s*,?\s*", "", line, flags=re.I)
    out: list[str] = []
    for chunk in re.split(r"[;,]|\band\b", line):
        chunk = chunk.strip(" .:")
        if not chunk or _PANEL_TITLE.match(chunk):
            continue
        if chunk.lower().startswith("concur"):
            continue
        chunk = re.sub(r"\s+(?:concur\w*)$", "", chunk, flags=re.I).strip()
        if _PANEL_NAME.match(chunk) and chunk not in out:
            out.append(chunk)
    return out


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

    def _line(self, parts: list, role: str, pm, align, rel=0.0) -> m.HmLine:
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
        self.items.append(self._line(parts, role, pm, align, rel))
        self.consumed.update(p.id for p in parts)

    def cell(self, parts: list, role: str, pm) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock."""
        parts = sorted(parts, key=lambda l: l.x0)
        self.consumed.update(p.id for p in parts)
        return self._line(parts, role, pm, m.Align.LEFT)

    @staticmethod
    def blank(pm) -> m.HmLine:
        return m.HmLine(text="", prov=m.Prov(pm.number), role="caption")

    def caption(self, page: int, left: list, right: list, rail, ids) -> None:
        # THE TWO STACKS ARE ROW-PAIRED, because this court pairs them: the
        # docket, the paper's name and the origin each stand beside the party
        # row the compositor set them against, and every district in the
        # corpus keeps that alignment.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=rail,
            rail_rows=max(len(left), 1),
            fp={"rail": rail or "gutter"},
            prov=m.Prov(page, tuple(sorted(set(ids))))))

    def rule(self, page: int, span: str = "center") -> None:
        self.items.append(m.Rule(prov=m.Prov(page), span=span))

    def rule_row(self, group: list, pm) -> None:
        """A TYPED divider renders where the page types it, carrying the line
        ids it was typed with so core's positional merge keeps it put."""
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:600],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def result(self, anchor: list) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": anchor, "doc_type_final": None}
