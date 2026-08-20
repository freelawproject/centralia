"""California Court of Appeal ('calctapp') — the publisher's other paper.

THE CONTRACT. Every one of the Court of Appeal's slips sets ONE cover, and
the cover's load-bearing element is a DRAWN CAPTION BOX: a vertical rule
down the middle of the caption band with the box's head and foot rules
ENDING at it.  That is ca9's shape, not va's whitespace gutter, and the
answer is measured rather than assumed — over the 42-record corpus the
vertical rule is drawn on 41 covers and the 42nd (colonial_manor, the
Appellate Division of the Los Angeles Superior Court) draws the foot rule
and types the divider as a stacked ``)`` instead.  Nothing about the two
columns is inferred from what the rows say:

    Filed 7/30/26                              the clerk's stamp, 10pt over
                                               a 13pt body — the ONLY date
                                               this court prints
              CERTIFIED FOR PUBLICATION        the publication flag
    IN THE COURT OF APPEAL OF THE STATE OF CALIFORNIA
              THIRD APPELLATE DISTRICT         the masthead: court, district,
                        (Butte)                division, county
    ────────────────────────────────┐          the box HEAD rule, ending AT
    AQUALLIANCE et al.,             │ C102382  the divider
        Plaintiffs and Appellants,  │
                                    │ (Super. Ct. No. 22CV00321)
            v.                      │
    VINA GROUNDWATER SUSTAINABILITY │ O P I N I O N
    AGENCY et al.,                  │
        Defendants and Appellants.  │
    ────────────────────────────────┘          the box FOOT rule

    APPEAL from a judgment of the Superior Court of Butte County, Tamara
    L. Mosbarger, Judge.  Affirmed.            the ORIGIN RECITAL

    Law Office of Adam Keats, … for Plaintiffs and Appellants.
    Paris Kincaid & Wasiewski, … for Defendant and Appellant Vina …
                                               the APPEARANCES

TWO DOCKETS, AND THEY ARE DIFFERENT THINGS.  ``C102382`` is this court's
own docket and goes to ``docket_number``; ``(Super. Ct. No. 22CV00321)``
is the trial court's and goes to ``lower_court_docket`` with the superior
court named in ``lower_court``.  They stand one above the other in the
same column and are told apart by FORM — the Court of Appeal's docket is
one district letter and five or six digits (``A``–``H``; consolidated
appeals join them with a slash, ``A170988/A172221``), and it is the
LEADING run of the right stack.  Everything after that run and before the
paper's own name is the court below.

THE RIGHT STACK IS THREE RUNS, IN THIS ORDER on all 42 covers: the
docket(s), the origin, and the paper's own name (``OPINION`` / ``O P I N
I O N`` / ``ORDER MODIFYING OPINION`` / ``AND DENYING REHEARING`` / ``[NO
CHANGE IN JUDGMENT]``).  The name is read as a CLOSED VOCABULARY of what
this court calls its own papers — the same class of closed role
vocabulary as a party status or a bench title — and never as a title
matched against a phrase.

THE STACKS ARE NOT ROW-PAIRED.  citizens_against_marketplace interleaves
them (party at 306.0, origin at 308.4, both at 324.0, party at 349.2,
party and title at 370.9, title at 386.7, party at 392.6 …) and kumar
sets its right column a half-line off its left throughout.  Pairing them
would pad the short column with blank tinted rows and, worse, thread a
docket between two party rows — the defect va was fixed for.  So the
caption is emitted as a ``CaptionBlock`` of two independent stacks, with
the drawn rule as its rail.

TWO CLOSURES, dispatched on WHAT STANDS UNDER THE BOX — not on the
district, the flag, or the paper's name:

  'recited cover' (27 of 42) — the origin recital and the appearances are
      printed under the box.  The recital opens on the court's own closed
      recital vocabulary ('APPEAL from', 'APPEALS from', 'ORIGINAL
      PROCEEDING(S)'); each appearance is a first-line-indented paragraph
      whose closing sentence carries an appearance cue ('… for Plaintiffs
      and Appellants.', 'No appearance for the Minor.', '… as Amici
      Curiae on behalf of …').  The block may run onto the page after the
      cover (osborne, mata) and it may be closed by a typed rule the
      court centres under it (isaacson, linson, osborne).

  'bare cover' (15 of 42) — the box closes the cover and the body
      starts under it.  The First and Sixth Districts print the origin
      and the appearances on a REPORTER'S DOCKET SHEET at the very back
      instead, and that sheet is claimed here as endmatter for the same
      reason cal's is: left in the stream its label grid reads as opinion
      prose and its last appearance reads as a conformed signature, so
      beale came back authored by 'Kelsey Linnett, Supervising Deputy
      Attorney General'.

      Eleven records print such a sheet. The rest set a bare cover
      because the paper is an ORDER stapled in FRONT of the opinion it
      modifies (bates, citizens, colonial_manor) and has nothing under
      its box at all — the name in the right column is what says so, and
      'THE COURT:' opens the writing.

The ORDER is a PAYLOAD, not a contract — ca6's rule. The box is what
dispatch reads; what the paper calls itself is what it carries. It is
declared as ``doc_type_final`` (ORDER when the right column names one,
OPINION otherwise) because nine unpublished records classify UNKNOWN in
core and their single writing then types 'order'.

WHERE THE READER STOPS, and what it does not touch.  At the appearances,
or at the foot of the box where there are none.  A record may staple a
second document with its OWN full cover (bates prints the order first and
the opinion's cover on page 2; kumar prints the opinion first and the
publication order on page 29): only the FIRST cover is claimed, because
the second stands inside a writing and nothing is ever taken out of an
assembled writing.  The unpublished-opinion notice ('California Rules of
Court, rule 8.1115(a) …', set at 8pt between two full-measure rules) is a
notice and is recorded as ``Dropped``; the clerk's stamp is NOT dropped,
because on this court it is the only date printed anywhere and it is the
row ``decision_date`` comes from.

WHAT ELSE THE BOX DRAWS. Where the court sets a case TITLE over the
parties ('In re B.S., a Person Coming Under / the Juvenile Court Law.',
'Conservatorship of the Person and Estate of R.R.') it draws the HEAD
rule between the two, so the band is read as two blocks with the fence
re-emitted between them — a reader that claims a fenced block owes the
page its fences. A band with nothing on the right of the divider is
rendered as ONE column, because a rail drawn against an empty column is
a claim the page did not make. The title rows go to ``short_case_name``
and the party rows are what ``case_name`` is built from; joined
wholesale, conservatorship_of_r.r. read 'Conservatorship of the Person
and Estate of R.R. SHASTA COUNTY PUBLIC GUARDIAN, as v. R.R.'

WHAT THIS COURT NEEDS THAT ``cal.py`` DOES NOT EXPRESS.  Three things,
recorded here because they are the finding and not an accident: (1) the
caption is TWO COLUMNS around a drawn rule, where cal's is a single
centred stack — no part of cal's stack walk transfers; (2) there is no
release date and no authorship summary at all, so the FILE STAMP is the
date of record; (3) the court prints a district and a county in its
masthead, and Criteria has no field for either, so they stay inside
``court`` as the masthead prints them and are not invented as keys.

A KNOWN DEFECT THIS READER TRIGGERS AND CANNOT FIX. On
``in_re_mccowen`` the modification order stapled BEHIND the opinion
loses its writing whole (135 words). Core splits a stapled paper into
parts (``pipeline.py::_attached_documents``) and this reader runs on each
part's own cover, which is right; but the order's writing then measures
under 900 characters, and ``resolve/assemble.py::_announces`` (~1720)
deletes a short writing that names a LATER writing's author — and this
order necessarily does, because what it orders is that the concurrence
of RAPHAEL, J. be attached. The veto that should have saved it tests the
literal string 'IT IS ORDERED' and this court writes 'IT IS THEREFORE
ORDERED' / 'IT IS FURTHER ORDERED'. Reported with an exact patch; not
worked around here, because working around it would mean not reading a
cover that reads correctly.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import get_profile

# calctapp's profile is declared in courts/__init__.py (byline style
# 'abbrev' — this court signs at the END, 'CHUNG, J.' over a 'WE CONCUR:'
# roster). It is read here, not re-registered: `register` rejects a
# duplicate court id.
CALCTAPP = get_profile("calctapp")

STYLE_RECITED = "recited cover"
STYLE_BARE = "bare cover"

# ---- calctapp's declared facts (measured over the 42-record corpus) ------
# THE DIVIDER. A vertical rule inside the caption band, between the left
# text edge and the right measure. Measured x over the corpus: 293.2 to
# 368.7 on a 612pt page — it moves with the length of the longest party
# name, which is exactly why it is read and not assumed.
_DIV_MIN, _DIV_MAX = 200.0, 470.0
# The shortest divider drawn (people_v._bankers, 9.8pt over two rows) —
# below this a vertical stroke is a glyph artefact, not a rail.
_DIV_MIN_HEIGHT = 8.0
# A row belongs to the right column when its box starts at or after the
# divider. The slack absorbs the box's own hairline width and the cells
# the court sets flush against the rule (people_v._bankers: 315.4 against
# a 314.6 rule).
_COL_SLACK = 8.0
# A box rule (head or foot) starts at the body rail and ENDS at the
# divider. Measured |x1 - divider| over the corpus: 0.0 on 41 covers and
# 7.2 on conservatorship_of_r.r., whose head rule stops short.
_RULE_END = 10.0
_RAIL_SLACK = 12.0
# THE TYPE STEP that names the stationery. Measured on all 42 records:
# the body is 13.0pt, the clerk's stamp 10.0-10.1pt, and the
# uncertified-opinion notice 8.0pt. Two steps, so two thresholds, and the
# window between them (9.0-11.0) is empty across the corpus.
_STAMP_STEP = 2.0
_NOTICE_STEP = 4.0
# THE PARAGRAPH RAIL. The recital and every appearance open on a
# first-line indent of 36pt (72 -> 108) or 36pt at the 108 rail (108 ->
# 144) and wrap back to the rail; a continuation stands AT the rail.
_INDENT_MIN = 12.0

# THIS COURT'S OWN DOCKET: one district letter and five or six digits.
# A, B, C, D, E, F, G, H are the six districts and their divisions'
# prefixes; consolidated appeals join them with a slash.
# The Second District's Division Six prefixes its own docket with the
# division's ordinal ('2d Civ. No. B348229'); the prefix is stationery and
# the docket underneath it is the same form.
_DOCKET = re.compile(
    r"^(?:\d+(?:st|nd|rd|th|d)\s+Civ\.\s*)?(?:No\.\s*)?"
    r"[A-H]\d{5,6}(?:\s*/\s*(?:[A-H])?\d{5,6})*$")
# The Appellate Division of a superior court numbers its own cases
# instead ('No. 24APLC00316'); it is still the LEADING run of the stack,
# which is what tells it from the trial court's number below it.
_DIV_DOCKET = re.compile(r"^No\.\s*[0-9A-Z][0-9A-Z\-]{5,}$")
# 'Filed 7/30/26', 'Filed 6/30/26; Certified for Publication 7/22/26
# (order attached)', or the bare '7/24/26' osborne stamps.
_STAMP_DATE = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4})")
_TYPED_RULE = re.compile(r"^[_\-–—]{5,}$")
# A GLYPH DINKUS closes the block too ('* * * * * *' — husband), and it is
# TYPED CONTENT, not a rule: never promote glyphs to something the page
# did not draw. Kept literal and centred, where the page set it.
_DINKUS = re.compile(r"^[*·•∗ ]{3,}$")

# THE PUBLICATION FLAG is read as a row whose every word belongs to this
# closed vocabulary — not as a phrase. The corpus prints four forms
# ('CERTIFIED FOR PUBLICATION' x24, 'NOT TO BE PUBLISHED IN OFFICIAL
# REPORTS' x6, 'NOT TO BE PUBLISHED IN THE OFFICIAL REPORTS' x4,
# 'CERTIFIED FOR PARTIAL PUBLICATION*' x2) and the vocabulary also takes
# the forms it does not ('NOT CERTIFIED FOR PUBLICATION', 'CERTIFIED FOR
# PUBLICATION IN PART', 'ORDERED PUBLISHED').
_PUB_WORDS = frozenset((
    "certified", "not", "to", "be", "publish", "published", "publication",
    "partial", "part", "in", "the", "official", "reports", "for", "of",
    "opinion", "ordered", "order", "and", "modifying", "modified",
    "precedent", "precedential", "designated", "pursuant", "rule",
))
_UNPUB_WORDS = ("not to be published", "not certified", "not for publication",
                "not designated")

# WHAT THE PAPER CALLS ITSELF — the closed vocabulary of this court's own
# document names, as it sets them in the caption's right column. Read as
# a whole-row word test, so 'O P I N I O N' (letter-spaced on the Fourth
# District's slips) and 'ORDER DENYING PETITION / FOR REHEARING AND /
# MODIFYING OPINION / [NO CHANGE IN JUDGMENT]' are all one run.
_TITLE_WORDS = frozenset((
    "opinion", "opinions", "order", "orders", "modifying", "modified",
    "certifying", "denying", "granting", "rehearing", "petition",
    "publication", "judgment", "change", "no", "and", "for", "in",
    "part", "the", "of", "dismissing", "appeal", "transfer", "remand",
    "unmodified", "attached", "vacating", "amending", "amended",
    "certified", "published", "on", "after", "review",
    # the letter-spaced form: each glyph stands as its own 'word'
    "o", "p", "i", "n",
))

# THE ORIGIN RECITAL's openers — the court's own closed form for stating
# where the case came from. All 29 recited covers open on one of these.
_RECITAL_OPENERS = ("appeal from", "appeals from", "original proceeding",
                    "original proceedings", "proceedings from",
                    "petition for writ", "appeal and cross-appeal from",
                    "appeals from a", "on appeal from")
# WHO TRIED IT, and WHAT WAS DONE. The recital closes on the trial
# judge's title and then the disposition, in that order, on every record.
_BENCH = ("judge", "referee", "commissioner", "judge pro tempore",
          "temporary judge")
_RECITAL_TAIL = re.compile(
    r"(?P<name>[^;]{2,90}?),\s*(?:" + "|".join(_BENCH)
    + r")s?\.\s*(?P<disp>.*)$", re.IGNORECASE)
# Where the JUDGE'S NAME starts inside that run. The recital names the
# tribunal first and the judge second, and the two are separated either by
# a sentence stop or by the county the tribunal sits in — 'APPEAL from an
# order of the Superior Court of San Bernardino County, Wilfred J.
# Schneider, Jr., Judge.' Taking the last comma-delimited chunk instead
# credited the appeal to 'Jr'.
# A period after a single capital is an INITIAL, not a sentence stop:
# cutting there credited 'APPEAL from a judgment of the Superior Court of
# Butte County, Tamara L. Mosbarger, Judge.' to a judge called
# 'Mosbarger'.
# CASE-SENSITIVE ON PURPOSE: under `re.I` the `[A-Z]` in the lookbehind
# matches a lower-case letter too, so the guard never fired and the whole
# recital came back as the judge's name ('ORIGINAL PROCEEDING in Mandate.
# Stay issued. Petition granted. Kendall Hannon' — nuanmanee).
_JUDGE_CUT = re.compile(r"(?:\b[Cc]ount(?:y|ies)[.,]\s+|(?<![A-Z])\.\s+|;\s+)")
# THE TRIBUNAL, as the recital names it.
_TRIBUNAL = re.compile(
    r"(?i)\b(?:the\s+)?((?:Superior|Appellate|Municipal|Juvenile|Justice)"
    r"\s+Court[^,.;]*)")

# PARTY STATUS — a closed role vocabulary, used only to read the case NAME
# out of the left stack. A party name is never read by wording.
_STATUS_WORDS = frozenset((
    "plaintiff", "plaintiffs", "defendant", "defendants", "appellant",
    "appellants", "respondent", "respondents", "petitioner", "petitioners",
    "appellee", "appellees", "objector", "objectors", "movant", "movants",
    "intervener", "interveners", "intervenor", "intervenors", "amicus",
    "amici", "curiae", "conservatee", "minor", "minors",
    "real", "party", "parties", "interest", "claimant", "claimants",
    "cross-appellant", "cross-appellants", "cross-respondent",
    "cross-respondents", "cross-complainant", "cross-defendant",
    "and", "the", "in", "as", "etc", "or", "by", "et", "al",
))
# THE APPEARANCE CUE. Each entry states who was represented, and it does
# so in the entry's LAST sentence — which is what keeps a body paragraph
# that merely says 'plaintiff' from reading as an appearance.
# 'as Amicus Curiae' is the form when the appearance is an amicus's own
# ('… Deputy Attorneys General, for Department of Water Resources as
# Amicus Curiae.' — aqualliance's last entry, which read as body prose
# because the status stood after 'as' and not after 'for').
_APPEARANCE = re.compile(
    r"\b(?:for|of|as|behalf of)\s+(?:the\s+)?"
    r"(?:plaintiff|defendant|appellant|appellee|respondent|petitioner|"
    r"objector|movant|interven|amicus|amici|minor|real\s+part|cross-|"
    r"conservat|claimant)", re.IGNORECASE)
_NO_APPEARANCE = re.compile(r"^no appearance\b", re.IGNORECASE)
_PRO_PER = re.compile(r"in pro\.? per\.?|self-represented|in propria persona",
                      re.IGNORECASE)

# THE REPORTER'S DOCKET SHEET — the trailing label grid. Its labels are a
# closed vocabulary the Reporter owns, and the only wording the endmatter
# reader tests.
_SHEET_LABEL = re.compile(
    r"^(Trial Court|Trial Judge|Judges?|Superior Court No\.?|Counsel|"
    r"Attorneys? for\b[^:]*|County|Court)\s*:", re.IGNORECASE)
_SHEET_TRIAL = re.compile(r"^Trial Court\s*:\s*(.*)$", re.IGNORECASE)
_SHEET_JUDGE = re.compile(r"^Trial Judge\s*:\s*(.*)$", re.IGNORECASE)
_SHEET_NO = re.compile(r"^Superior Court No\.?\s*:\s*(.*)$", re.IGNORECASE)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _ink_x0(line) -> float:
    """Where the row's INK starts, not where its box does. The right
    column's cells are padded with the spaces the court typed to place
    them ('      B351810'), and the render sets headmatter rows
    `white-space:pre-wrap` — measuring from x0 and keeping the spaces
    counts the same gap twice."""
    xs = [c["x0"] for c in (line.chars or []) if (c.get("text") or "").strip()]
    return min(xs) if xs else line.x0


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[^\w’'\-]+", _norm(text).lower()) if w]


def _all_in(text: str, vocab) -> bool:
    ws = _words(text)
    return bool(ws) and all(w in vocab for w in ws)


def _is_publication(text: str) -> bool:
    """A publication flag: every word in the closed publication
    vocabulary, and the row actually says something about publishing."""
    ws = _words(text)
    if not ws or not _all_in(text, _PUB_WORDS):
        return False
    return any(w.startswith("publi") for w in ws)


def _names_an_order(text: str) -> bool:
    """Does the paper call itself an ORDER? Its own name is the only
    heading a stapled order prints."""
    return any(w in ("order", "orders") for w in _words(text))


def _names_an_order(text: str) -> bool:
    """Does the paper call itself an ORDER? On a stapled modification or
    rehearing order the caption's right column is the only place it
    says so."""
    return any(w in ("order", "orders") for w in _words(text))


def _is_title(text: str) -> bool:
    return _all_in(text, _TITLE_WORDS) and any(
        w in ("opinion", "opinions", "order", "orders", "o")
        for w in _words(text))


def _is_docket(text: str) -> bool:
    t = _norm(text).strip("()[] ")
    return bool(_DOCKET.match(t) or _DIV_DOCKET.match(t))


def _is_status(text: str) -> bool:
    t = _norm(text).rstrip(".,;: ")
    return bool(t) and _all_in(t, _STATUS_WORDS)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".,").lower() in ("v", "vs")


# --------------------------------------------------------------------------
# the page's own bounds
# --------------------------------------------------------------------------

def _note_top(pm, body_size: float) -> float:
    """Where this page's footnote zone opens. Below it stand the
    assignment note ('* Pursuant to California Rules of Court, rules
    8.1105 and 8.1110 …') and the statutory-reference notes, which are
    footnotes and not the reader's to claim."""
    tops = [l.top for l in pm.lines
            if l.plain.strip() and l.top > pm.height * 0.5
            and (_TYPED_RULE.match(_norm(l.plain))
                 or ((l.size or 99) <= body_size - 1.5
                     and set(_norm(l.plain)) <= set("*†‡§¶0123456789 .")))]
    return min(tops) if tops else float("inf")


def _rows(pm, finder, body_size: float) -> list:
    out = [l for l in pm.lines
           if l.plain.strip() and l.top < _note_top(pm, body_size)
           and not finder.kind(pm, l)]
    out.sort(key=lambda l: (l.top, l.x0))
    return out


# --------------------------------------------------------------------------
# the drawn caption box
# --------------------------------------------------------------------------

class _Box:
    """The caption box the cover draws: its divider, its two fence rules
    and the band they enclose."""

    def __init__(self, divider, rail, v_rule, head, foot, top, bottom):
        self.divider = divider
        self.rail = rail                  # '|' drawn, ')' typed, None
        self.v_rule = v_rule
        self.head = head
        self.foot = foot
        self.top = top
        self.bottom = bottom


def _find_box(pm, rows: list, body_x0: float) -> _Box | None:
    """Read the box, or return None.

    THE DIVIDER IS THE PARSER. A vertical rule inside the caption band is
    taken first; where the page drew only the foot rule, the rule's own
    RIGHT END is the divider — the fence stops at the middle of the box,
    which is the same thing the vertical says. No rail, no claim."""
    verts = [v for v in pm.v_rules
             if _DIV_MIN < v.x < _DIV_MAX
             and (v.bottom - v.top) >= _DIV_MIN_HEIGHT]
    verts.sort(key=lambda v: -(v.bottom - v.top))
    fences = [h for h in pm.h_rules
              if h.x0 <= body_x0 + _RAIL_SLACK and _DIV_MIN < h.x1 < _DIV_MAX]
    if verts:
        divider, v_rule = verts[0].x, verts[0]
    elif fences:
        fences.sort(key=lambda h: -h.x1)
        divider, v_rule = fences[0].x1, None
    else:
        return None

    box = sorted((h for h in fences if abs(h.x1 - divider) <= _RULE_END),
                 key=lambda h: h.top)
    right = [l for l in rows if _ink_x0(l) >= divider - _COL_SLACK]
    if v_rule is not None:
        right = [l for l in right
                 if v_rule.top - 6.0 <= l.top <= v_rule.bottom + 6.0]
    if not right:
        return None
    # THE RULE SPANS THE BAND, so it is the rule that says where the band
    # starts. Measured from the right column's own first row instead,
    # citizens_against_marketplace lost its two opening party rows to the
    # masthead: it sets 'CITIZENS AGAINST / MARKETPLACE' 24pt above the
    # first cell in the right column, and the vertical rule covers both.
    top = v_rule.top if v_rule is not None else min(l.top for l in right)
    head = foot = None
    if len(box) >= 2:
        head, foot = box[0], box[-1]
    elif box:
        # ONE rule: it is the head when caption rows stand below it and the
        # foot when none do. conservatorship_of_r.r. draws only the head
        # (between the case title and the parties); colonial_manor draws
        # only the foot.
        foot = box[0] if box[0].top > max(l.top for l in right) else None
        head = None if foot is not None else box[0]
    bottom = foot.top if foot is not None else (
        v_rule.bottom if v_rule is not None else max(l.top for l in right) + 20)
    if v_rule is not None and bottom < v_rule.bottom:
        bottom = v_rule.bottom
    # THE TYPED RAIL. colonial_manor draws no vertical and stacks a ')'
    # down the middle instead; it is the rail the page set, and the cells
    # keep their own text once it is taken off them.
    rail = "|" if v_rule is not None else None
    if rail is None and sum(
            1 for l in right if _norm(l.plain).startswith(")")) >= 2:
        rail = ")"
    return _Box(divider, rail, v_rule, head, foot, top, bottom)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, body_size, body_x0):
        self.model = model
        self.geom = geom
        self.body_size = body_size
        self.body_x0 = body_x0
        self.items: list = []
        self.attorneys: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.origin: dict = {}
        # The caption's PARTY rows — the ones below the box's head rule.
        # Held on the context and not in `crit`: `setattr` accepts any
        # name, so a working key parked in the criteria dict attaches to
        # the record silently and never serializes.
        self.party_rows: list[str] = []

    def _line(self, line, role: str, align: str, trim: bool) -> m.HmLine:
        text = line_markup(line)
        return m.HmLine(
            text=text.strip() if trim else text,
            prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), italic=bool(line.all_emphasized),
            role=role)

    def row(self, line, role: str, align: str = "L") -> None:
        self.items.append(self._line(line, role, align, False))
        self.consumed.add(line.id)

    def cell(self, line, role: str, text: str | None = None) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock.
        The column places the cell, so the padding the court typed to
        place it is not content and is trimmed off."""
        self.consumed.add(line.id)
        row = self._line(line, role, "L", True)
        if text is not None:
            row.text = text
        return row

    def caption(self, page: int, left: list, right: list, box: _Box,
                ids: list) -> None:
        # THE TWO STACKS ARE NOT ROW-PAIRED — see the module docstring.
        # `rail` is the divider the page actually drew, and `fp` records
        # the measurement the reader dispatched on, so the label and the
        # reproduction cannot disagree.
        if not left and not right:
            return
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=box.rail,
            rail_rows=len(right) if box.rail == ")" else 0,
            style_id="ruled-box" if box.rail == "|" else (
                "paren-rail" if box.rail == ")" else "open-box"),
            fp={"rail": box.rail, "divider_x": round(box.divider, 1)},
            prov=m.Prov(page, tuple(sorted(ids)))))

    def rule(self, h_rule, page: int, width: float) -> None:
        """One of the box's own fences, re-emitted where the page drew it.
        A reader that claims a fenced block owes the page its fences —
        core draws them in `read_headmatter`, and that pass only runs on
        rows a reader left behind."""
        span = "full" if h_rule.x1 >= 0.85 * width else "left"
        self.items.append(m.Rule(prov=m.Prov(page), span=span))

    def typed_rule(self, line) -> None:
        self.items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                 span="center", typed=True))
        self.consumed.add(line.id)

    def endmatter(self, line, role: str) -> None:
        self.attorneys.append(self._line(line, role, "L", True))
        self.consumed.add(line.id)

    def drop(self, line, kind: str) -> None:
        self.dropped.append(m.Dropped(text=_norm(line.plain),
                                      prov=m.Prov(line.page, (line.id,)),
                                      kind=kind))
        self.consumed.add(line.id)

    def result(self, anchor_ids=(), doc_type=None):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "dropped": self.dropped,
                "consumed": self.consumed, "anchor_ids": list(anchor_ids),
                "doc_type_final": doc_type}


@decider("headmatter.read", court="calctapp")
def read_headmatter_calctapp(model, geom, **_):
    """Read calctapp's cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = geom.body_size if geom else 13.0
    body_x0 = geom.body_x0 if geom else 72.0
    finder = FurnitureFinder(model, body_x0, body_size)
    page1 = model.pages[0]
    rows = _rows(page1, finder, body_size)
    if not rows:
        return NOTHING
    box = _find_box(page1, rows, body_x0)
    if box is None:
        return NOTHING                       # no rail, no claim

    ctx = _Ctx(model, geom, body_size, body_x0)
    band = [l for l in rows if box.top - 2.0 <= l.top <= box.bottom + 1.0]
    if not band:
        return NOTHING
    above = [l for l in rows if l.top < box.top - 2.0]
    below = [l for l in rows if l.top > box.bottom + 1.0]

    if not _read_masthead(ctx, above, page1, body_size):
        return NOTHING
    _read_box(ctx, band, box, page1)

    # THE DISPATCH: what stands under the box.
    if below and _opens_recital(below[0]):
        style = STYLE_RECITED
        _read_recital(ctx, below, finder, page1.number)
    else:
        style = STYLE_BARE
    ctx.crit["headmatter_style"] = style
    _read_sheet(ctx, model, finder, body_size)
    _case_name(ctx)
    # WHAT KIND OF PAPER THIS IS, declared because the reader read the
    # caption cell that says so. Nine unpublished records classify UNKNOWN
    # in core (`classify_doc_type` has no cue for 'NOT TO BE PUBLISHED IN
    # THE OFFICIAL REPORTS') and their single writing then types `order`;
    # the declaration is the fact that fixes them, once core applies it
    # before assembly (patch-queue item 7 — today it lands at
    # `pipeline.py:1880`, long after `assemble` ran).
    doc_type = (m.DocType.ORDER
                if _names_an_order(ctx.crit.get("title") or "")
                else m.DocType.OPINION)
    return ctx.result(doc_type=doc_type)


# --------------------------------------------------------------------------
# the stamp, the flag, the notice and the masthead
# --------------------------------------------------------------------------

def _read_masthead(ctx: _Ctx, above: list, pm, body_size: float) -> bool:
    """Everything above the box: the clerk's stamp, the publication flag,
    the uncertified-opinion notice, and the masthead itself.

    THE STAMP IS NOT DROPPED. cal drops its file stamp because a centred
    release date stands below it; this court prints no other date
    anywhere on the cover, so the stamp is the date of record and it is
    emitted where the clerk put it."""
    if not above:
        return False
    masthead: list = []
    for line in above:
        size = line.size or body_size
        if size <= body_size - _NOTICE_STEP:
            ctx.drop(line, "notice")     # the Rules-of-Court notice
            continue
        if size <= body_size - _STAMP_STEP:
            continue                     # the stamp — `_read_stamp` has it
        text = _norm(line.plain)
        if _is_publication(text):
            ctx.row(line, "publication", "C")
            low = text.lower()
            ctx.crit.setdefault(
                "publication_status",
                "unpublished" if any(u in low for u in _UNPUB_WORDS)
                else "published")
            continue
        masthead.append(line)
    if not masthead:
        return False
    _read_stamp(ctx, pm, masthead[0].top, body_size)
    for line in masthead:
        ctx.row(line, "court", "C")
    # AS THE PAGE PRINTS IT. The masthead carries the court, its
    # appellate DISTRICT, its DIVISION and the COUNTY the appeal came
    # from; Criteria has a field for none of those but `court`, so they
    # stay here rather than being invented as keys.
    ctx.crit["court"] = _norm(" ".join(l.plain for l in masthead))
    return True


def _read_stamp(ctx: _Ctx, pm, masthead_top: float, body_size: float) -> None:
    """THE CLERK'S STAMP, claimed off the page and not off the filtered
    rows. Core's furniture finder recognizes it (`kind == 'stamp'`) and on
    28 of the 42 records it is therefore never offered to the reader — so
    the date was recorded on 14 records and dropped on 28, which is one
    court reading its own stationery two ways. It is read here from the
    page's own rows above the masthead: on this court it is the ONLY date
    printed anywhere, and it also carries the publication order that
    changed the paper's status after filing ('Filed 6/30/26; Certified
    for Publication 7/22/26 (order attached)') on the six records that
    print no flag at all."""
    stamp = [l for l in pm.lines
             if l.plain.strip() and l.top < masthead_top - 2.0
             and (l.size or body_size) <= body_size - _STAMP_STEP
             and l.id not in ctx.consumed]
    stamp.sort(key=lambda l: (l.top, l.x0))
    joined = " ".join(_norm(l.plain) for l in stamp).lower()
    for line in stamp:
        ctx.row(line, "date", "L")
        mm = _STAMP_DATE.search(_norm(line.plain))
        if mm and "decision_date" not in ctx.crit:
            ctx.crit["decision_date"] = mm.group(1)
    if "publication_status" not in ctx.crit and (
            "publication" in joined or "pub." in joined
            or "published" in joined):
        ctx.crit["publication_status"] = (
            "unpublished" if any(u in joined for u in _UNPUB_WORDS)
            else "published")


# --------------------------------------------------------------------------
# the box
# --------------------------------------------------------------------------

def _read_box(ctx: _Ctx, band: list, box: _Box, pm) -> None:
    """The caption band, as two stacks either side of the drawn divider.

    The head rule splits the band where the court draws it: what stands
    above it is the case TITLE ('In re B.S., a Person Coming Under / the
    Juvenile Court Law.', 'Conservatorship of the Person and Estate of
    R.R.') and what stands below it is the parties. Both are caption and
    both are set in the same two columns, so each becomes its own block
    with the fence re-emitted between them — a reader that claims a
    fenced block owes the page its fences.

    THE RIGHT STACK IS READ IN ONE PASS OVER THE WHOLE BAND, not once per
    group: in_re_j.l. sets its docket and its origin ABOVE the head rule
    and its parties below, so a state machine restarted per group read the
    parties' first right-hand cell as a second docket."""
    cut = box.head.top if box.head is not None else None
    groups = [[l for l in band if cut is not None and l.top < cut],
              [l for l in band if cut is None or l.top >= cut]]

    # ---- the right stack: docket(s), then the court below, then the name
    right_role: dict[int, str] = {}
    right_text: dict[int, str] = {}
    dockets: list[str] = []
    origin: list[str] = []
    title: list[str] = []
    state = "docket"
    for line in band:
        if _ink_x0(line) < box.divider - _COL_SLACK:
            continue
        text = _norm(line.plain)
        if box.rail == ")":
            text = text.lstrip(") ").strip()
            if not text:
                right_role[line.id] = ""      # the rail glyph alone
                continue
        if state == "docket" and not _is_docket(text):
            state = "origin"
        if state != "title" and _is_title(text):
            state = "title"
        right_role[line.id] = {"docket": "docket", "origin": "lower-court",
                               "title": "title"}[state]
        right_text[line.id] = text
        (dockets if state == "docket"
         else origin if state == "origin" else title).append(text)

    # ---- the two stacks, group by group, in the page's own order
    title_rows: list[str] = []
    party_rows: list[str] = []
    for gi, group in enumerate(groups):
        if not group:
            continue
        if gi == 1 and box.head is not None:
            ctx.rule(box.head, pm.number, pm.width)
        left, cells, ids, plain = [], [], [], []
        for line in group:
            ids.append(line.id)
            role = right_role.get(line.id)
            if role is None:
                plain.append(line)
                (title_rows if gi == 0 and cut is not None
                 else party_rows).append(_norm(line.plain))
            elif role == "":
                ctx.consumed.add(line.id)     # the typed rail, nothing else
            else:
                cells.append(ctx.cell(line, role, right_text[line.id]))
        if cells:
            for line in plain:
                left.append(ctx.cell(line, "caption"))
            ctx.caption(pm.number, left, cells, box, ids)
        else:
            # ONE COLUMN IS THE HONEST READING of a band with nothing on
            # the right. in_re_b.s. sets its case title above the head
            # rule and puts no cell beside it; rendered as a two-column
            # block that band drew a rail against an empty column.
            for line in plain:
                ctx.row(line, "caption", "L")
    if box.foot is not None:
        ctx.rule(box.foot, pm.number, pm.width)

    if title_rows or party_rows:
        ctx.crit["caption"] = title_rows + party_rows
    # THE PRINTED FORM BESIDE THE PARSED ONE. The rows above the head rule
    # are the court's own name for the case ('In re B.S., a Person Coming
    # Under the Juvenile Court Law.'); the rows below it are the parties,
    # and it is those the case name is built from.
    if title_rows:
        ctx.crit["short_case_name"] = _norm(" ".join(title_rows)).rstrip(",")
    ctx.party_rows = party_rows
    if dockets:
        ctx.crit["docket_number"] = dockets[0].strip("()[] ")
        if len(dockets) > 1:
            ctx.crit["other_dockets"] = [d.strip("()[] ") for d in dockets[1:]]
    if title:
        ctx.crit["title"] = _norm(" ".join(title))
    if origin:
        _read_origin(ctx, origin)


def _read_origin(ctx: _Ctx, rows: list[str]) -> None:
    """The court below, from the run under the docket.

    ITS NAME AND ITS NUMBER STAND IN ONE STATEMENT, parenthesised and
    wrapped wherever the column runs out ('(Los Angeles County' / 'Super.
    Ct. No.' / '25STCP01327'). The parentheses are what group it, so the
    run is re-split on paren depth before anything is read — pipitone
    prints TWO groups and prints them the other way round ('(Super. Ct.
    No. 22CV0676)' over '(San Luis Obispo County)'), and joined blind that
    read as one number called '22CV0676) (San Luis Obispo County'.

    The only wording read is the Reporter's own abbreviation for a
    superior-court number, which is a LABEL and not a name."""
    groups: list[str] = []
    depth = 0
    for row in rows:
        if depth <= 0 or not groups:
            groups.append(row)
        else:
            # A NUMBER WRAPS ON ITS OWN HYPHEN. '(Super. Ct. No. 37-2022-'
            # over '00029915-CU-MM-CTL)' is one number; joined with a
            # space it came back as '37-2022- 00029915-CU-MM-CTL'.
            sep = "" if groups[-1].rstrip().endswith("-") else " "
            groups[-1] = _norm(groups[-1]) + sep + _norm(row) \
                if sep == "" else _norm(groups[-1] + " " + row)
        depth += row.count("(") - row.count(")")
    names: list[str] = []
    numbers: list[str] = []
    for group in groups:
        flat = _norm(group).strip("()[] ")
        mm = re.search(r"(?i)\b(?:super\.?\s*ct\.?|superior court)\s*nos?\.?\s*",
                       flat)
        if mm is None:
            # A bare 'No. <number>' group is the trial court's number
            # under its name (colonial_manor: 'Santa Monica Trial Court'
            # over 'No. 24SMUD00651').
            if re.match(r"^Nos?\.\s*\S+$", flat):
                numbers.append(re.sub(r"^Nos?\.\s*", "", flat))
            else:
                names.append(flat)
            continue
        head = _norm(flat[:mm.start()]).rstrip(",; ")
        if head:
            names.append(head)
        # A COMMA-TAIL TOO SHORT TO BE A NUMBER is a suffix on the one
        # before it: 'Nos. N22-1955, N23-0770' is two cases, but
        # 'No. DK08393B,C' is one case with two children.
        for part in re.split(r"[,;]", flat[mm.end():]):
            part = part.strip()
            if not part:
                continue
            if numbers and len(part) <= 2:
                numbers[-1] = f"{numbers[-1]},{part}"
            else:
                numbers.append(part)
    if names:
        ctx.crit["lower_court"] = "; ".join(names)
    if numbers:
        ctx.crit["lower_court_docket"] = numbers


def _case_name(ctx: _Ctx) -> None:
    """The case name, built from the party names either side of the pivot
    — never by joining the caption wholesale.

    A CONSOLIDATED or three-sided caption repeats the shape (greely
    stacks plaintiff / v. / defendant-respondent / defendant-appellant;
    osborne adds real parties in interest), so the name closes on the
    STATUS row that follows the second side: everything under it is
    another party to the same appeal, not the respondent."""
    rows = ctx.party_rows or ctx.crit.get("caption") or []
    left, right, seen = [], [], False
    for text in rows:
        if _is_pivot(text):
            seen = True
            continue
        if _is_status(text):
            if seen and right:
                break
            continue
        (right if seen else left).append(text)
    if seen and left and right:
        a = _norm(" ".join(left)).rstrip(", ")
        b = _norm(" ".join(right)).rstrip(", ")
        ctx.crit["parties"] = [a, b]
        ctx.crit["case_name"] = f"{a} v. {b}"
        return
    one = _norm(" ".join(t for t in rows if not _is_status(t))).rstrip(", ")
    if one:
        ctx.crit["parties"] = [one]
        ctx.crit["case_name"] = one


# --------------------------------------------------------------------------
# the recital and the appearances
# --------------------------------------------------------------------------

def _opens_recital(line) -> bool:
    return _norm(line.plain).lower().startswith(_RECITAL_OPENERS)


def _paragraphs(rows: list, body_x0: float) -> list:
    """The rows below the box, grouped as the page sets them: an entry
    opens on a first-line indent and wraps back to the rail."""
    out: list[list] = []
    rail = min((_ink_x0(l) for l in rows), default=body_x0)
    for line in rows:
        indent = _ink_x0(line) - rail
        if not out or indent > _INDENT_MIN:
            out.append([])
        out[-1].append(line)
    return out


def _is_appearance(text: str) -> bool:
    """An appearance states who was represented, and states it in its
    CLOSING sentence. That is what keeps a body paragraph mentioning
    'plaintiff' from reading as one (chemical_toxin's first paragraph
    opens 'Plaintiff filed a complaint against defendants …')."""
    flat = _norm(text)
    if _NO_APPEARANCE.match(flat):
        return True
    tail = re.split(r"(?<=[.])\s+", flat)
    last = tail[-1] if tail[-1].strip() else (tail[-2] if len(tail) > 1 else "")
    return bool(_APPEARANCE.search(last) or _PRO_PER.search(last))


def _read_recital(ctx: _Ctx, below: list, finder, page: int) -> None:
    """The origin recital and the appearances under the box.

    Bounded on both sides: it opens on the recital's own closed form and
    it ends at the first paragraph that is not an appearance. The block
    may run onto the page after the cover — the appearances there are
    read the same way, so a body paragraph on that page ends the walk
    exactly as one on the cover does — and the court may close it with a
    typed rule centred under the last entry."""
    rows = list(below)
    if page < len(ctx.model.pages):
        rows += _rows(ctx.model.pages[page], finder, ctx.body_size)
    paras = _paragraphs(rows, ctx.body_x0)
    counsel: list[str] = []
    state = "recital"
    for para in paras:
        text = _norm(" ".join(l.plain for l in para))
        if state == "recital":
            if not _opens_recital(para[0]):
                break
            for line in para:
                ctx.row(line, "lower-court")
            _recital_criteria(ctx, text)
            state = "counsel"
            continue
        if len(para) == 1 and _TYPED_RULE.match(_norm(para[0].plain)):
            ctx.typed_rule(para[0])         # the court's own closing rule
            break
        if len(para) == 1 and _DINKUS.match(_norm(para[0].plain)):
            ctx.row(para[0], "case-info", "C")
            break
        if not _is_appearance(text):
            break
        for line in para:
            ctx.row(line, "counsel")
        counsel.append(text)
    if counsel:
        ctx.crit["attorneys"] = " ".join(counsel)[:2000]


def _recital_criteria(ctx: _Ctx, text: str) -> None:
    """THE TRIBUNAL, WHO TRIED IT and WHAT WAS DONE, from the recital as
    printed — 'APPEAL from a judgment of the Superior Court of Butte
    County, Tamara L. Mosbarger, Judge.  Affirmed.'

    The recital is the fuller statement of the court below than the
    caption's own parenthesised number is, so it is the one `lower_court`
    keeps; the caption's number stays in `lower_court_docket`."""
    mm = _TRIBUNAL.search(text)
    if mm is not None:
        ctx.crit["lower_court"] = _norm(mm.group(1)).rstrip(".,;")
    mm = _RECITAL_TAIL.search(text)
    if mm is None:
        return
    # The judge's name runs from the last sentence stop (or from the
    # county the tribunal sits in) to the bench title.
    run = mm.group("name")
    cuts = list(_JUDGE_CUT.finditer(run))
    name = _norm(run[cuts[-1].end():] if cuts else run).strip(",; ")
    if name and name[:1].isupper():
        ctx.crit.setdefault("lower_court_judge", name)
    disp = _norm(mm.group("disp"))
    if disp:
        ctx.crit.setdefault("disposition", disp)


# --------------------------------------------------------------------------
# the Reporter's docket sheet — the endmatter
# --------------------------------------------------------------------------

def _sheet_page(model, finder, body_size: float) -> int | None:
    """The trailing page the Reporter's docket sheet occupies, or None.

    THE LABEL GRID NAMES ITSELF. The sheet is the LAST page and it opens
    on the Reporter's own labels ('Trial Court:', 'Trial Judge:',
    'Counsel:', 'Attorneys for Plaintiff and Appellant:'). It is never
    page 1 — page 1 is the court's cover — and a page that carries any
    row the labels do not account for above them is the writing's last
    page, not the sheet."""
    if len(model.pages) < 2:
        return None
    pm = model.pages[-1]
    rows = [l for l in pm.lines if l.plain.strip() and not finder.kind(pm, l)]
    if not rows:
        return None
    labels = sum(1 for l in rows if _SHEET_LABEL.match(_norm(l.plain)))
    if labels >= 2:
        return pm.number
    # A SHEET WITHOUT LABELS. The Second District's Division Six sets the
    # same matter unlabelled — the trial judge, the court he sits in, a
    # typed rule, then the appearances (pipitone). Two appearances and
    # nothing longer than a caption row above them is that sheet, and an
    # ordinary last page of a writing has no appearance on it at all.
    paras = _paragraphs(rows, min((_ink_x0(l) for l in rows), default=72.0))
    hits = sum(1 for para in paras
               if _is_appearance(_norm(" ".join(l.plain for l in para))))
    if hits >= 2 and all(
            _is_appearance(_norm(" ".join(l.plain for l in para)))
            or _TYPED_RULE.match(_norm(para[0].plain))
            or len(_norm(" ".join(l.plain for l in para))) <= 60
            for para in paras):
        return pm.number
    return None


def _read_sheet(ctx: _Ctx, model, finder, body_size: float) -> None:
    """Claim the sheet whole and render it as endmatter.

    Every row is emitted — the claim is total, so nothing is taken out of
    the document that is not put back where a reader can see it — and
    what the sheet states about the trial court and the appearances is
    copied into criteria only where the cover left the field empty."""
    page = _sheet_page(model, finder, body_size)
    if page is None:
        return
    pm = model.pages[page - 1]
    rows = sorted((l for l in pm.lines
                   if l.plain.strip() and not finder.kind(pm, l)),
                  key=lambda l: (l.top, l.x0))
    counsel: list[str] = []
    state = "grid"
    for line in rows:
        text = _norm(line.plain)
        low = text.lower()
        if low.startswith("counsel") or low.startswith("attorneys for") \
                or low.startswith("attorney for"):
            state = "counsel"
        if state == "counsel":
            ctx.endmatter(line, "counsel")
            if not text.rstrip().endswith(":"):
                counsel.append(text)
            continue
        mm = _SHEET_TRIAL.match(text) or _SHEET_NO.match(text)
        if mm:
            ctx.endmatter(line, "lower-court")
            ctx.origin.setdefault("court", _norm(mm.group(1)))
            continue
        mm = _SHEET_JUDGE.match(text)
        if mm:
            ctx.endmatter(line, "lower-court")
            if _norm(mm.group(1)):
                ctx.crit.setdefault("lower_court_judge", _norm(mm.group(1)))
            continue
        ctx.endmatter(line, "case-info")
    if ctx.origin.get("court"):
        ctx.crit.setdefault("lower_court", ctx.origin["court"])
    if counsel and not ctx.crit.get("attorneys"):
        ctx.crit["attorneys"] = " ".join(counsel)[:2000]
