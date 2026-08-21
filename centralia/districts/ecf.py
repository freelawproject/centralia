"""THE CM/ECF PLEADING ORDER — the paper the federal district courts share.

A federal district court is not a publisher with a house style; it is a
building full of chambers, each with its own Word template. What every one of
those templates prints is the same five things, in the same order, and the
templates differ only in what they DRAW between the caption's two columns. So
the contract is named for the paper and dispatched on the divider, and the
divider is MEASURED, never read:

    the ECF overlay            the top band, on every page: a fielded stamp
                               CM/ECF prints over the court's own sheet,
                               sometimes wrapping to a second row
                               ('Case: 2:25-cv-00171-DLB-CJS  Doc #: 8
                                Filed: 05/20/26  Page: 1 of 19 - Page' /
                                'ID#: 132')
    the masthead               the leading run of CENTRED rows: the court,
                               the district, the division, the seat
    the caption band           parties, status, pivot, docket, title — two
                               columns, split at whatever the chambers drew
                               between them
    the closer                 a typed ASTERISK BAND ('* * * * * *') on the
                               page axis, or, where a chambers types none,
                               the caption box's own FOOT RULE
    the body                   everything below the closer, core's

Three dividers are read here, all measured on page 1:

    GLYPH RAIL — a stacked ')' between the columns:

        CELLMARK, INC.,             )
              Plaintiff,            ) Civil Action No. 2:24-cv-00181-SCM-CJS
        v.                          )
                                    )        MEMORANDUM OPINION
        ROBERT WEBSTER, et al.,     )              AND ORDER
              Defendants.           )
                    ***   ***   ***   ***

    DRAWN RAIL — a DRAWN vertical stroke, closed at its foot by a drawn
    horizontal that stops AT the stroke (captions.py calls the shape 'Old
    Faithful'):

        HEALTHCARE JUSTICE COALITION,   │  CASE NO. 5:25-cv-386-KKC
              Plaintiff,                │
        v.                              │  OPINION & ORDER
        UNITED HEALTHCARE OF            │  ────────────────
        KENTUCKY, et al.,               │
              Defendants.               │
        ────────────────────────────────┘   the foot rule = the closer

    FLUSH-RIGHT STATUS — nothing is drawn at all. The party stands at the
    body rail and its STATUS is set flush right; the docket opens the band on
    its own row and the title shares the pivot's row:

        CIVIL ACTION NO. 25-171-DLB-CJS
        LINDA MOORE                                        PLAINTIFF
        v.            MEMORANDUM OPINION AND ORDER

Every number below is a MEASUREMENT with a default taken from kyed's 25
records, the first district read. A court whose chambers measure differently
overrides the fact in its own file and says what it measured; a court that
draws something no other court draws writes that in its own file. Nothing is
inherited and no district file imports another.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..resolve.evidence import NOTHING

# WHY A RECORD WAS REFUSED. NOTHING is the honest answer, but it is also
# silent, and a court whose corpus answers NOTHING is a court whose facts
# have not been measured yet — so each refusal names the gate it failed.
# Diagnostic only: the return value is NOTHING either way, and nothing in
# the pipeline reads `LAST_REFUSAL`.
LAST_REFUSAL: list = []


def _refuse(gate: str):
    LAST_REFUSAL.append(gate)
    del LAST_REFUSAL[:-1]
    return NOTHING

from ..resolve.footnotes import line_markup
from ..resolve.furniture import (FurnitureFinder, _looks_like_efiling_stamp,
                                 is_folio_text)

_RAIL_STATUS_TAIL = True

STYLE_GLYPH_RAIL = "ecf order, glyph rail"
STYLE_DRAWN_RAIL = "ecf order, drawn rail"
STYLE_FLUSH_STATUS = "ecf order, flush-right status"
# THE TYPED BOX. The Second Circuit's districts fence the caption instead of
# dividing it: a typed rule of hyphens closed by an 'X' stands above the
# parties and another below them, the masthead is set FLUSH LEFT above the
# first, and the columns are split by the whitespace gutter alone.
#
#     UNITED STATES DISTRICT COURT
#     SOUTHERN DISTRICT OF NEW YORK
#     -----------------------------------------------X
#     SILVIO R. ILLESCAS,
#                         Petitioner,        ORDER
#            -against-              17 Civ. 5385 (VB) (AEK)
#     THOMAS GRIFFIN,
#                         Respondent.
#     -----------------------------------------------X
STYLE_TYPED_BOX = "ecf order, typed box"
# THE DRAWN BOX. Northern New York's chambers rule the caption instead of
# typing it: two horizontal strokes at the body rail, stopping well short of
# the measure, one directly under the masthead and one under the last party.
# Nothing is drawn between the columns and nothing typed marks the band, so
# the strokes answer the same three questions the typed fence does. Measured
# on nynd, where 16 of 24 records were refused outright for want of it.
STYLE_DRAWN_BOX = "ecf order, drawn box"
# THE CENTRED FENCE. A chambers that names no court on its sheet and rules
# its caption with short strokes on the page axis instead — see
# `_centre_fence`.
STYLE_CENTRE_FENCE = "ecf order, centred fence"

# THE DOCKET, in every form the chambers write it: 'CIVIL ACTION NO.
# 25-171-DLB-CJS', 'CRIMINAL ACTION NO. 26-196-DLB', 'Case No.:
# 5:25-cv-00086-KKC', 'Civil Action No. 2:24-cv-00181-SCM-CJS', 'Civil No.
# 3:25-cv-00042-GFVT', 'No. 6:25-CV-109-HAI'.
# 'CIV.' and 'CR.' are how a chambers abbreviates what it is trying: hid
# writes 'CIV. NO. 20-00187 HG-WRP', and spelling only the long forms threw
# that docket away and left a page-ID stamp to be read as one instead.
DOCKET_RE = re.compile(
    r"^(?:"
    # what is being tried, then the number — and the word 'number' itself is
    # optional once the kind of action has been said: 'CIVIL ACTION
    # 25-0531-WS-N' (alsd) names the docket without ever writing 'No.'
    r"(?:civ(?:il)?|crim(?:inal)?|cr|misc(?:ellaneous)?)\.?\s+"
    r"(?:(?:a|act(?:ion)?)\.?\s+)?"
    r"(?:(?:nos?\.?|numbers?)\s*:?\s*)?"
    r"|"
    # …or the number word alone: 'Case No.', 'No.', 'NUMBER'
    r"(?:case\s+)?(?:nos?\.?|numbers?)\s*:?\s*"
    r")(\S.*)$", re.I)

# THE TITLE is a closed vocabulary of the words a district court names its
# own paper with, tested on the row's LETTERS so that neither the wrap
# ('MEMORANDUM OPINION' / 'AND ORDER') nor the letter-spacing one chambers
# uses ('O PIN I ON AND ORDER') hides it. Nothing about the case is read.
TITLE_WORDS = (
    "memorandum", "opinion", "order", "and", "judgment", "report",
    "recommendation", "adopting", "decision", "ruling", "findings", "fact",
    "conclusions", "law", "decree", "amended", "corrected", "supplemental",
    "initial", "screening", "review", "notice", "entry", "the", "of", "on",
    # A magistrate names the paper after the officer who wrote it —
    # 'REPORT AND RECOMMENDATION OF THE MAGISTRATE JUDGE' (measured on almd:
    # 5 of 50 records, and the reason the spelling test failed on them).
    "magistrate", "judge", "recommended", "disposition", "application",
    "leave", "granting", "denying", "adopting", "in", "part",
    # A CHAMBERS MAY NAME THE PAPER FOR HOW SHORT IT IS. nhd heads its
    # social-security dispositions 'SUMMARY ORDER'; unknown as a title, the
    # row did not close the caption band, so the box ran on past it and took
    # the opinion's own first line into the caption with it — the writing
    # then opened mid-sentence on 'Administration's denial of her
    # applications …' (the user, 2026-08-21, on nhd/scott_v._ssa).
    "summary",
)
# The words a wrapped title fragment may OPEN with. 'AND ORDER' opening a
# column is an unread row, not a paper name.
TITLE_OPENERS = ("memorandum", "opinion", "order", "judgment", "report",
                 "findings", "ruling", "decision", "notice", "amended",
                 "corrected", "recommendation",
                 # Measured on the refused records: ared calls its paper a
                 # 'RECOMMENDED DISPOSITION', and one chambers titles an
                 # 'APPLICATION FOR LEAVE TO …'.
                 "recommended", "application", "summary",
                 # A MAGISTRATE NAMES THE PAPER AFTER HIMSELF FIRST:
                 # "MAGISTRATE JUDGE'S REPORT AND RECOMMENDATION" (arwd).
                 # The word already stood in `title_words`; it could not
                 # OPEN a title, so the row fell through to the judge-cell
                 # test and was read as the bench.
                 "magistrate")
# PARTY STATUS is a finite role vocabulary; a party NAME is never read by
# wording. A district sets the status in caps flush right on one template and
# in title case under the party on the others.
STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
    "petitioners", "respondent", "respondents", "movant", "movants",
    "claimant", "claimants", "intervenor", "intervenors", "debtor",
    "debtors", "appellant", "appellants", "appellee", "appellees",
    "garnishee", "garnishees", "applicant", "applicants", "amicus", "amici",
)
STATUS_GLUE = ("and", "the", "third", "party", "cross", "in", "interest",
               "of", "pro", "se", "counter")
# '-against-' is the Second Circuit districts' pivot; the hyphens are the
# court's own typography, not part of the word.
PIVOTS = ("v", "vs", "versus", "against")


@dataclass(frozen=True)
class EcfPaper:
    """What one district court's chambers were MEASURED to draw.

    Every default is kyed's measurement. Override a field only with a number
    you took off that court's own pages, and say in the court file what you
    measured it on."""

    # THE OVERLAY BAND: 12% of the height (95pt on a 792pt sheet) holds the
    # stamp and its wrapped tail and stands clear of the earliest masthead
    # row (kyed: stamp at top 13.0, tail at 25.0, earliest masthead 60.4).
    overlay_band: float = 0.12
    # THE CLOSER BAND. kyed's asterisk band lands between 267.0 and 328.4 on
    # a 792pt page (34%-42%); the caption's foot rule between 267.8 and
    # 326.7. 55% of the height clears both by a wide margin and still stands
    # above the first body row on every record.
    closer_band: float = 0.55
    # THE ASTERISK BAND is typed, so its pitch varies by chambers ('* * * *',
    # '***   ***', '* *  * *'). Five asterisks is the floor: no caption cell
    # in the corpus carries more than one.
    asterisk_floor: int = 5
    # THE GLYPH RAIL. ')' occurs in ordinary prose and inside party names
    # ('ENFORCEMENT ("ICE"), et al.'), so it counts as a divider only as a
    # COLUMN — four or more stacked within 3pt of one x. Measured: the
    # shortest rail in kyed is 9 glyphs.
    rail_chars: str = ")]:*§}|"
    rail_floor: int = 4
    rail_column: float = 3.0
    # A glyph belongs to the rail when it stands in the rail's own column.
    # The rail cell is ~7pt wide (')' at 307.6-311.6, with a trailing space
    # to 314.6); 12pt clears the cell and reaches nothing else on the row.
    rail_window: float = 12.0
    # THE DRAWN RAIL. A stroke at least 25pt tall standing between 35% and
    # 75% of the measure. Measured: x = 304.6-317.8 on a 612pt page
    # (50%-52%), heights 131-197pt. The band bound keeps a table border on a
    # later page out.
    drawn_min_h: float = 25.0
    drawn_x: tuple[float, float] = (0.35, 0.75)
    # THE FOOT RULE closes the drawn-rail caption: a drawn horizontal from
    # the body rail ENDING at the rail's own x. Both ends are the test — a
    # rule that ends short of the rail is the title's UNDERLINE, and a rule
    # spanning the whole measure is a footnote separator.
    foot_rule_end: float = 12.0
    # THE PAPER'S OWN NAME, as the court prints it at the head of the sheet.
    # The masthead is the court naming ITSELF, which is the one place a name
    # may be read — and it is read on 'DISTRICT COURT' alone, because a
    # district's own line can carry a typo ('EASTEN DISTRICT OF KENTUCKY').
    court_name: str = "district court"
    # THE VOCABULARIES, shared by reference — never by inheritance.
    docket_re: re.Pattern = DOCKET_RE
    title_words: tuple[str, ...] = TITLE_WORDS
    title_openers: tuple[str, ...] = TITLE_OPENERS
    status_words: tuple[str, ...] = STATUS_WORDS
    status_glue: tuple[str, ...] = STATUS_GLUE
    pivots: tuple[str, ...] = PIVOTS
    # A LONE PIECE in an undrawn row is placed by where it starts: the status
    # cell and the title both begin far right of the rail, the party and the
    # pivot both begin on it.
    lone_piece_reach: float = 40.0
    # THE CENTRED FENCE: three short strokes on the page axis, standing in
    # for a masthead this paper never prints. Measured on all three records
    # that draw it (paed/658030, txed/243348, txed/245820) — every stroke is
    # x 288.0-324.0 on a 612pt sheet: 36pt wide, centred on 306.0 within a
    # tenth of a point. The floors are set well outside those numbers and
    # still far inside anything else drawn on a district sheet: a footnote
    # separator on the same records runs 144pt from x 162.
    centre_fence_max_w: float = 80.0
    centre_fence_axis: float = 20.0
    centre_fence_min: int = 3
    centre_fence_band: float = 0.55
    # HOW FAR BELOW THE BOX the appearances may reach before the reader stops
    # looking. Measured on ord: the longest roster runs 7 rows.
    counsel_max_rows: int = 16
    # THE PLEADING-PAPER LINE NUMBERS: how far left they stand, and how long
    # a run has to be before it is the paper's rail rather than a caption
    # cell that happens to be a numeral (measured on cand: 28 numerals at
    # x0 68-74 of a 612pt page, one per typed line).
    line_number_x: float = 0.16
    line_number_floor: int = 8
    # HOW FAR DOWN THE SHEET the masthead may stand. The stamp above it can
    # run to five rows (alnd's 'FILED / 2026 May-11 PM 03:10 / U.S. DISTRICT
    # COURT / N.D. OF ALABAMA'), so the band is generous — but not so
    # generous that a body line naming the court could be mistaken for it.
    masthead_band: float = 0.35
    # HOW DEEP A DRAWN BOX MAY REACH. A caption is normally done by half way
    # down the sheet, but a CONSOLIDATED caption is not: akd stacks two cases
    # in one box whose drawn rail runs to 644 of a 792pt page (81%), and a
    # band capped at the closer's 55% cut the second case off — the parties
    # of one of the two consolidated actions simply vanished. The rail says
    # where its own box ends; this is only the limit on believing it.
    box_band: float = 0.90
    # …and the rail has to START at the caption, or a table's border further
    # down the page would be read as the caption's divider.
    rail_head_slack: float = 40.0
    # A CONSOLIDATED CAPTION RUNS ON. Where a court hears actions together it
    # stacks their captions in one box, and the box does not always fit the
    # sheet: akd closes page one's box at its foot rule and OPENS ANOTHER at
    # the top of page two, at the same divider x, holding the third action.
    # Read page one alone, that action's parties simply do not exist. The
    # continuation is recognised by the rail starting inside the top margin.
    carry_top: float = 0.14
    # THE DRAWN FENCE. nynd's strokes are 247-288pt wide and end at 319-367
    # of a measure that reaches 533 — 0.64-0.72 of it. 120pt is well under
    # the narrowest stroke and well over any underline in the band; 0.9 of
    # the measure keeps a full-width header rule out.
    fence_min_w: float = 120.0
    # …AND HOW FAR ACROSS IT MAY REACH. nynd's strokes stop at 0.64-0.72 of
    # the measure, but mnd and wiwd rule the box at the FULL measure (72.0 to
    # 526.0 of a column ending at 526) — held to 0.90 their edges were not
    # the box, no closer was found and 6 records were refused. A rule ABOVE
    # the masthead cannot be the box's top whatever its width (see the
    # `_box` filter in the walk), which is what a header rule would be.
    fence_max_reach: float = 1.02
    # ONE EDGE, DRAWN TWICE. dcd rules its box with a thick stroke that
    # arrives as two rects 2.9pt apart, so a 2pt join read the box's top as
    # both its top AND its foot: the band closed 2.9pt below where it opened,
    # came back empty, and the record was refused (united_states_v._li). 7pt
    # is over half a body line and far under any caption's depth — dcd's own
    # top and foot stand 111pt apart.
    fence_join: float = 7.0


DEFAULT = EcfPaper()


# --------------------------------------------------------------------------
# the vocabularies, read off a row
# --------------------------------------------------------------------------

def _spells_court(text: str, court_name: str) -> bool:
    """Does this row name the court — READ WITHOUT ITS SPACES?

    An OCR'd sheet moves the spaces without losing a letter: ohsd's cover
    prints 'IN THE UNITED STATES DISTRICTC OURT' and 'WESTERND IVISION-
    CINCINNATI'. Tested word-for-word the row does not name any court, so the
    masthead anchor was never found and the record — 12 headmatter rows, a
    whole caption — came back unread. The LETTERS are what the page states;
    where the scanner put the space between them is not.
    """
    flat = "".join((text or "").split()).lower()
    return "".join(court_name.split()).lower() in flat


# TYPOGRAPHIC LIGATURES ARE PRESENTATION, NOT SPELLING. A chambers setting
# its sheet in a text font ships 'Plaintiﬀ,' as U+FB00 rather than two f's,
# and every closed vocabulary here is spelled in ASCII — so the status word
# did not match, and the party name came back as 'Rothwell, Plaintiﬀ' with
# its status glued on (paed/658030, txed/245820; txed/243348 says
# 'Petitioner,' and was already right, which is what identified the cause).
# U+FB00-FB06 are presentation forms of ASCII pairs and fold with no loss.
_LIGATURES = str.maketrans({"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
                            "\ufb03": "ffi", "\ufb04": "ffl",
                            "\ufb05": "st", "\ufb06": "st"})


def _norm(text: str) -> str:
    return " ".join(text.translate(_LIGATURES).split())


def _letters(text: str) -> str:
    """The row's letters, lower-cased, '&' spelled out — the form the title
    vocabulary is tested against."""
    return re.sub(r"[^a-z]", "", _norm(text).lower().replace("&", "and"))


def _title_spelling(text: str, facts: EcfPaper):
    """The paper-name words ``text`` spells, or None.

    Segmentation, not a word split, because one chambers' template loses its
    word breaks in the PDF ('O PIN I ON AND ORDER'): the vocabulary that
    recognizes the row is the only thing that can spell it. A wrap fragment
    ('AND ORDER', '&') answers with its words; a party name ('ROBERT
    WEBSTER, et al.') answers None."""
    key = _letters(text)
    if not key or len(key) < 3:
        return None
    back: list = [None] * (len(key) + 1)
    reach = [True] + [False] * len(key)
    for i in range(len(key)):
        if not reach[i]:
            continue
        for word in facts.title_words:
            if key.startswith(word, i) and not reach[i + len(word)]:
                reach[i + len(word)] = True
                back[i + len(word)] = (i, word)
    if not reach[len(key)]:
        return None
    words: list[str] = []
    at = len(key)
    while at:
        at, word = back[at]
        words.append(word)
    return list(reversed(words))


def _is_title_row(text: str, facts: EcfPaper) -> bool:
    return _title_spelling(text, facts) is not None


def _title_text(text: str, facts: EcfPaper) -> str:
    """The title as the criterion should carry it: the page's own form where
    the page set usable word breaks, and the vocabulary's spelling where it
    did not."""
    flat = _norm(text)
    tokens = [t.strip(",.;:") for t in
              flat.upper().replace("&", " AND ").split()]
    tokens = [t for t in tokens if t]
    if tokens and all(t.lower() in facts.title_words for t in tokens):
        return flat.upper()
    spelling = _title_spelling(flat, facts)
    return " ".join(w.upper() for w in spelling) if spelling else flat.upper()


def _is_status_row(text: str, facts: EcfPaper) -> bool:
    """Is the row APPARATUS rather than a party? Every word has to be a
    status word, so a party carrying one ('DEFENDANT SERVICES, INC.')
    survives."""
    words = [w.strip(",.;:-–/() ").lower()
             for w in _norm(text).replace("-", " ").replace("/", " ").split()]
    words = [w for w in words if w]
    if not words:
        return False
    return all(w in facts.status_words or w in facts.status_glue
               for w in words)


# The words a court leaves in lower case inside its paper's own name.
CONNECTIVES = ("and", "of", "the", "on", "to", "for", "in", "a", "an",
               "upon", "with", "re", "as")


def _paper_case(text: str) -> bool:
    """Is the row set the way a court sets its paper's NAME — capitals, with
    only connectives allowed in lower case?

    The closed title vocabulary cannot spell a title that names the CASE
    ('AMENDED OPINION ON HYUNDAI'S MOTION FOR SUMMARY JUDGMENT', 'ORDER
    DENYING MOTION FOR RECONSIDERATION'), and refusing to read case words is
    deliberate. So the row is recognised by its OPENER and its CASE instead:
    what makes it the paper's name is that the court set it in capitals under
    a word that names a paper. A bold body sentence ('This case is before the
    court on plaintiff Kristin') fails on the very first word."""
    words = [w for w in re.split(r"[^A-Za-z]+", _norm(text)) if w]
    if not words:
        return False
    # CAPITALS OR TITLE CASE. Most chambers shout the paper's name; nvd sets
    # it 'Order Dismissing and / Closing Case', and read as neither a title
    # nor a docket it was tinted as though the parties were called that.
    def _named(w: str) -> bool:
        return w.isupper() or (w[:1].isupper() and w[1:].islower())
    return all(_named(w) or w.lower() in CONNECTIVES for w in words)


def _is_title_head(text: str, facts: EcfPaper) -> bool:
    """Does the row OPEN a paper name?"""
    if not _letters(text).startswith(facts.title_openers):
        return False
    # A NAMED JUDGE IS NOT A PAPER. 'Magistrate Judge John Smith' opens on a
    # title word and is set in the court's own capitals, so `_paper_case`
    # accepts it — the same veto `_is_title_tail` already keeps.
    flat = _norm(text)
    if _JUDGE_CELL.match(flat) or _HON_CELL.match(flat) \
            or _BY_LINE.match(flat):
        return False
    return _is_title_row(text, facts) or _paper_case(text)


# A SECTION HEADING, not the title's wrap. The court's first heading stands
# in the same capitals as its title and, on one almd record, at the same line
# pitch ('MEMORANDUM OPINION AND ORDER' / 'I. INTRODUCTION'). What separates
# them is the ENUMERATOR the court sets on its sections and never on its
# paper's name.
_ENUMERATED = re.compile(r"^\s*(?:[IVXLC]+|[0-9]{1,2}|[A-Z])\s*[.)]\s+\S")


def _is_title_tail(text: str, facts: EcfPaper) -> bool:
    """Does the row CONTINUE one? A title wraps ('ORDER DENYING MOTION FOR' /
    'RECONSIDERATION')."""
    flat = _norm(text)
    if _ENUMERATED.match(flat) or _BY_LINE.match(flat) \
            or _JUDGE_CELL.match(flat) or _HON_CELL.match(flat):
        return False
    return _is_title_row(text, facts) or _paper_case(text)


def _letter_spaced(text: str) -> bool:
    """Is the row set LETTER BY LETTER? One chambers stretches its paper's
    name across the measure ('R  E  P  O  R  T   A  N  D   R  E  C  O  M  M
    E  N  D  A  T  I  O  N' — arwd), and the gaps arrive as spaces: the row
    renders as loose capitals nobody can read. Measured as a proportion so
    that an ordinary title carrying one initial is untouched."""
    toks = _norm(text).split()
    if len(toks) < 6:
        return False
    singles = sum(1 for t in toks if len(t.strip(".,;:'\u2019")) <= 1)
    return singles >= len(toks) * 0.6


def _is_docket_label(text: str) -> bool:
    """A docket heading whose number wrapped to the row below it.

    Every part of the heading is optional except that SOMETHING of it is
    said: 'CIVIL ACTION NO.' and '2:25cv236-MHT' as two rows (almd), and
    'CIVIL ACTION' alone over its number (ksd), where reading the label as a
    party put 'CIVIL ACTION' in the caption."""
    flat = _norm(text).rstrip(":.")
    if not flat:
        return False
    return bool(re.fullmatch(
        r"(?:civ(?:il)?|crim(?:inal)?|cr|misc(?:ellaneous)?)\.?"
        r"(?:\s+(?:a|act(?:ion)?)\.?)?(?:\s+(?:nos?\.?|numbers?))?"
        r"|(?:case\s+)?(?:nos?\.?|numbers?)", flat, re.I))


def _bare_docket(text: str) -> bool:
    """A docket NUMBER standing alone under its label."""
    flat = _norm(text)
    return bool(len(flat) <= 40 and re.search(r"\d", flat)
                and re.fullmatch(r"[0-9][0-9A-Za-z:().,\-\s/]*", flat))


# A DOCKET WITH NO LABEL. Not every chambers writes 'No.' before its case
# number: iasd sets a bare '3:24-cv-00027-WPK' in the caption's right column,
# which read as a party name. The federal case number is specific enough to
# be recognised on its own — year or division, the two-to-four letter nature
# of suit, the sequence, and the judges' initials.
# Two spellings of the same number. Most chambers hyphenate every part
# ('3:24-cv-00027-WPK'); ared's clerk runs it together and hangs the judge's
# initials off the end with a space ('3:25CV00024 JM').
# The division prefix ('1:') is optional — nywd writes '22-cv-905-MAV'.
_CASE_NUMBER = re.compile(
    r"^(?:"
    # the usual order — year, nature of suit, sequence: '3:24-cv-00027-WPK',
    # and ned's unpadded '8:26CV59'
    r"(?:[0-9]{1,2}\s*:\s*)?[0-9]{2}\s*(?:-\s*[a-z]{2,4}\s*-\s*|[a-z]{2,4})"
    r"[0-9]{2,6}"
    r"|"
    # …and the reverse, where the clerk leads with what is being tried:
    # 'CV 124-115' (gasd), 'CR 425-021'
    r"[a-z]{2,4}\s*[-\s]\s*[0-9]{2,4}\s*-\s*[0-9]{2,6}"
    r")"
    # …AND THE INITIALS MAY BE BRACKETED, once or twice. The Second Circuit's
    # districts write '1:23-cv-01599 (AMN/PJE)' and '25-CV-9876 (LTS)', and
    # spelling only the hyphenated and spaced forms left those rows to be
    # tinted 'case info' with no docket criterion read at all.
    r"(?:\s*(?:[-\s]\s*[A-Za-z]{1,6}(?:\s*[-/]\s*[A-Za-z]{1,12})?"
    r"|\(\s*[A-Za-z]{1,6}(?:\s*/\s*[A-Za-z]{1,12})?\s*\)))*$", re.I)


# THE PUBLIC-DOMAIN CITATION. A district that numbers its published
# opinions prints the number in the caption's right column, under the
# docket: 'Opinion No. 2025 DNH 058' (nhd). It is a CITATION, not a docket
# and not the paper's name — unroled, it rendered as an anonymous caption
# cell and the criterion went unfilled.
_OPINION_CITE = re.compile(r"^opinion\s+nos?\.?\s*:?\s*(\S.*)$", re.I)

# WHAT THE CLERK HANGS OFF THE DOCKET: '[WO]' and '(WO)' (a written opinion,
# almd), '(KLEEH)' (the judge's initials, wvnd), 'SECTION "O"' (the division,
# laed). Case information, not a party and not the paper's name.
# WHAT WAS DEMANDED. 'JURY DEMAND' / 'DEMAND FOR JURY TRIAL' stands in the
# caption's right column beside the parties (alsd) — case information the
# clerk records, not a party to the case and not the paper's name.
_JURY = re.compile(
    r"^(?:demand\s+for\s+(?:trial\s+by\s+)?jury(?:\s+trial)?"
    r"|jury\s+(?:trial\s+)?demand(?:ed)?"
    r"|trial\s+by\s+jury\s+demanded)\.?$", re.I)

_CASE_FLAG = re.compile(
    r"^(?:[(\[]\s*[A-Za-z0-9 .\-/]{1,14}\s*[)\]]"
    r"|section\s+[\u201c\"']?[A-Za-z0-9]{1,3}[\u201d\"']?)\.?$", re.I)

# WHO THE CASE IS ASSIGNED TO. A district clerk stacks the judges under the
# docket in the caption's right column — 'Chief Judge William L. Campbell,
# Jr.' over 'Magistrate Judge Luke A. Evans' (tnmd), 'JUDGE ALEXANDER C. VAN
# HOOK' over 'MAGISTRATE JUDGE LEBLANC' (lawd). Tinted as caption, those rows
# claim to be parties to the case; they are the bench.
# The bench is named three ways and only one of them puts a name after the
# word: 'Chief Judge William L. Campbell, Jr.' (tnmd), the OFFICE alone under
# the signature rule ('United States District Judge' — 24 records), and the
# parenthesised assignment the clerk hangs off the docket ('(Chief Judge
# Brann)'). All three were falling through to 'caption'.
# THE COURT'S OWN NAME, CAUGHT IN THE CAPTION'S FIRST ROW. Some chambers
# set the division or the seat at the same height as the first party, so the
# masthead walk — which advances row by row — stops above it and the row's
# pieces are joined into one caption cell ('N ICK McCULLAR, NORTHERN
# DIVISION' — ared). The division is not a party; it is the last line of the
# court naming itself.
_DIVISION = re.compile(
    r"^(?:[A-Z][A-Za-z.\- ]{0,24}\s+)?division$|^at\s+[A-Z][A-Za-z .\-]{2,24}$",
    re.I)


_JUDGE_CELL = re.compile(
    r"^[(\[]?\s*(?:the\s+)?(?:hon(?:ou?rable)?\.?\s+)?"
    r"(?:chief\s+|senior\s+|acting\s+|presiding\s+)?"
    r"(?:u\.?\s?s\.?\s+|united\s+states\s+)?"
    r"(?:district\s+|magistrate\s+|circuit\s+|bankruptcy\s+)*"
    # …BUT A POSSESSIVE NAMES THE PAPER, NOT THE BENCH. arwd titles its
    # paper "MAGISTRATE JUDGE'S REPORT AND RECOMMENDATION", and the office
    # words plus `judges?\b` swallowed it whole: the row was tinted 'panel'
    # and the court's own paper name was listed as a member of the bench
    # (the user, 2026-08-20: 'the panel is not panel its title'). A judge
    # cell says WHO — 'Magistrate Judge Daniel J. Stewart'; the apostrophe
    # says WHOSE, and what follows it is the thing owned.
    r"judges?(?![\u2019']s)\b\s*(.*?)\s*[)\]]?$", re.I)
# …and a fourth way, with no office at all: 'Hon. Matthew F. Leitman',
# 'Honorable Hala Y. Jarbou' (mied, miwd). The courtesy title is the whole
# signal, so it is required — a bare name is a party.
_HON_CELL = re.compile(
    r"^[(\[]?\s*hon(?:ou?rable|\.)\s+(\S.*?)\s*[)\]]?$", re.I)
# WHO WROTE IT, where the chambers says so under the paper's name:
# 'MEMORANDUM OPINION' / 'BY: HON. THOMAS T. CULLEN' (vawd). Set in the same
# capitals as the title, it read as the title's second line and the judge's
# name became part of what the paper is called.
_BY_LINE = re.compile(
    r"^by\s*:?\s+(?:the\s+)?(?:hon(?:ou?rable)?\.?\s+)?(\S.*)$", re.I)
# THE DATE THE PAPER WAS ENTERED, where the chambers sets it in the caption
# rather than over the signature ('March 6, 2026' — njd).
_DATE_CELL = re.compile(
    r"^(?:dated?\s*:?\s*)?"
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
    r"\s+\d{1,2},?\s+\d{4})\.?$", re.I)


def _unlabelled_docket(text: str) -> bool:
    return bool(_CASE_NUMBER.match(_norm(text)))


def _is_pivot_row(text: str, facts: EcfPaper) -> bool:
    flat = _norm(text).rstrip(".").strip("-–— ").lower()
    return flat in facts.pivots


# WHERE THE MASTHEAD STOPS. The masthead is the court naming itself — the
# court, the district, the division, the seat — and nothing else. But the row
# under it is centred too on many districts, and it is not the court: it is
# the judge who wrote the paper ('District Judge S. Kato Crews' — cod), the
# docket ('Case No. 24-cv-20123' — flsd), the clerk's own label ('CIVIL
# ACTION FILE' — gand), or the paper's name. Read into the masthead, each of
# those was reported as part of the court's NAME.
_JUDGE = re.compile(r"\b(?:judge|justice|magistrate)\b", re.I)

# WHO HAS THE CASE, as the sheet names them under the masthead: 'District
# Judge S. Kato Crews' (cod), 'Judge Robert E. Blackburn', 'Magistrate Judge
# N. Reid Neureiter', 'Honorable Philip A. Brimmer, Chief District Judge'.
# The designation must OPEN or CLOSE the row and a name must stand beside it,
# so the papers whose NAME carries the word ('REPORT AND RECOMMENDATION OF
# THE UNITED STATES MAGISTRATE JUDGE') can never match: those neither open on
# the office nor end on a person.
_OFFICE = (r"(?:The\s+)?(?:Honorable\s+|Hon\.\s+)?"
           r"(?:Chief\s+|Senior\s+|Acting\s+|Visiting\s+)?"
           r"(?:United\s+States\s+|U\.?\s?S\.?\s+)?"
           r"(?:District\s+|Magistrate\s+|Circuit\s+|Bankruptcy\s+)?"
           r"(?:Judge|Justice)")
_NAME = (r"(?:[A-Z][A-Za-z'\u2019.\-]*\s+){0,3}"
         r"[A-Z][A-Za-z'\u2019.\-]+")
_JUDGE_ROW = re.compile(
    rf"^(?:{_OFFICE}\s+{_NAME}|{_NAME},\s*{_OFFICE})\.?$")


def _is_judge_row(text: str) -> bool:
    """Does this row name the judge the case is assigned to?"""
    flat = _norm(text).strip()
    return bool(flat) and _JUDGE_ROW.match(flat) is not None


_DISTRICT_OF = re.compile(
    r"^(?:for\s+the\s+|in\s+the\s+)?"
    r"(?:eastern|western|northern|southern|central|middle)?\s*"
    r"district\s+of\s+\S", re.I)


def _names_court(text: str, facts: "EcfPaper") -> bool:
    """Is the row part of the court's OWN NAME?

    Where a chambers sets the masthead flush left and draws nothing and types
    nothing, this is the only thing that says where the run ends: the rows
    that go on naming the court, and then the first party. Two rows on nyed
    and nysd — 'UNITED STATES DISTRICT COURT' and the district under it."""
    flat = _norm(text)
    if _spells_court(flat, facts.court_name):
        return True
    return bool(_DIVISION.match(flat) or _DISTRICT_OF.match(flat))


def _ends_masthead(text: str, facts: "EcfPaper") -> bool:
    """Is this centred row something OTHER than the court naming itself?"""
    flat = _norm(text)
    if not flat:
        return False
    # THE RAIL'S FIRST GLYPH. A caption whose divider opens a row above the
    # first party puts a lone ')' on the page axis, and reading it as a
    # masthead row moves the band's ceiling BELOW the first party — hid lost
    # its opening caption row and its docket that way.
    if len(flat) <= 2 and set(flat) <= set(facts.rail_chars):
        return True
    if _JUDGE.search(flat):
        return True
    if _docket_value(flat, facts) is not None or _is_docket_label(flat):
        return True
    if _is_title_head(flat, facts):
        return True
    return False


# THE APPEARANCES, where a district prints them: a run of paragraphs under
# the caption box, each one a roster of firms and addresses CLOSED by who
# they appeared for — '… Seattle, WA 98101. Attorneys for Plaintiff.' The
# closer is the only reliable landmark: the roster itself is addresses and
# names, indistinguishable from prose, and the paragraph wraps so the phrase
# is split across rows ('… 98101. Attorneys for' / 'Plaintiff.'). So the
# JOINED text of the run is tested, never a single row.
# THE PERIOD IS OPTIONAL. nynd closes each side of its roster with 'Attorneys
# for Plaintiffs' and 'Attorney for Defendants' and sets no full stop on
# either, so the run was trimmed away to nothing and 18 rows of roster opened
# the writing.
_APPEARANCE_END = re.compile(
    r"\b(?:attorneys?|counsel|appearances?)\s+(?:for|on\s+behalf\s+of)\s+"
    r"[^.]{0,80}\.?\s*$", re.I)
# THE BYLINE ENDS THE HEADMATTER. 'IMMERGUT, District Judge.' opens the
# writing and belongs to core's byline machinery, which types the writing and
# names its author from it — claiming it here would take the author away.
_BYLINE_HEAD = re.compile(
    r"^[A-Z][A-Za-z.'\u2019\- ]{1,44},\s+"
    r"(?:U\.?\s?S\.?\s+|United\s+States\s+)?"
    r"(?:Senior\s+|Chief\s+|Acting\s+)?"
    r"(?:District|Circuit|Magistrate|Bankruptcy|Chief)\s+Judge\b")


# THE OFFICE, ALONE ON ITS ROW. A district judge signs in the reversed form —
# the name over the office — and where a chambers prints that announcement
# UNDER its appearances block, `_BYLINE_HEAD` cannot see it: that pattern
# wants 'STEWART, Magistrate Judge' on one row, and nynd sets 'DANIEL J.
# STEWART' over 'United States Magistrate Judge' on two.
_OFFICE_ROW = re.compile(
    r"^(?:u\.?\s?s\.?\s+|united\s+states\s+)?"
    r"(?:senior\s+|chief\s+|acting\s+|presiding\s+)?"
    r"(?:district|circuit|magistrate|bankruptcy)\s+judge\.?$", re.I)


def _is_name_row(text: str, facts: "EcfPaper") -> bool:
    """Could the row be a person's name and nothing else? Deliberately loose,
    because the row that FOLLOWS it — a bare office — is what carries the
    proof; this only has to refuse an address, a status and a paper name."""
    flat = _norm(text).rstrip(",.")
    if not flat or any(ch.isdigit() for ch in flat):
        return False
    words = flat.split()
    if not (1 < len(words) <= 6):
        return False
    if _is_status_row(flat, facts) or _is_title_head(flat, facts):
        return False
    return all(w[:1].isupper() or not w[:1].isalpha() for w in words)


def _is_typed_rule(text: str) -> bool:
    """A typed fence: a run of hyphens, closed by an 'X' where the chambers
    types one. Not a drawn rule and not a title underline — the court typed
    it as text, so it arrives as a row."""
    flat = _norm(text)
    if len(flat) < 20:
        return False
    body = flat.rstrip("Xx ")
    # EVERY DASH THE WORD PROCESSOR MIGHT HAVE PUT THERE. nyed types its
    # '-----X' with U+2011 NON-BREAKING HYPHENS, and set against four
    # codepoints the whole fence read as ordinary text: the masthead was
    # never accepted, and nyed/532720 came back with 29 unread rows. Also
    # U+2010 (hyphen), U+2012 (figure dash) and U+2015 (horizontal bar),
    # which the same templates reach for.
    return bool(body) and set(body) <= {
        "-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014",
        "\u2015", "_"}


_CID = re.compile(r"\(cid:(\d+)\)")


def _decode_cid_docket(value: str):
    """A docket whose subset font lost its ToUnicode map, decoded — but only
    where the decoding PROVES ITSELF.

    `pdfio.quirks.decode_cid_glyphs` recovers these with the common TrueType
    +29 ordering and deliberately refuses a font too small to prove it: ndd
    writes 'Case No. 1:26-(cid:70)(cid:89)-128' and the two glyphs give no
    vowel to test, so the literals stand and the docket reads as garbage.
    Wrong-but-plausible prose would be worse than garbage — but a DOCKET is
    not prose. +29 turns those two into 'cv', which completes a federal case
    number, and that shape is the proof. Anything that does not land on a
    case number keeps its literals."""
    if "(cid:" not in value:
        return None
    try:
        out = _CID.sub(lambda mm: chr(int(mm.group(1)) + 29), value)
    except ValueError:
        return None
    if not out.isprintable():
        return None
    return out if _CASE_NUMBER.match(_norm(out)) else None


def _cid_markup(line, facts: EcfPaper):
    """The row's markup with a lost ToUnicode map decoded, or None.

    `_decode_cid_docket` proves the +29 ordering from the case number it
    completes, and records the decoded docket as the criterion — but the row
    the page RENDERS was still built from the raw glyphs, so ndd/…72274.9.0
    stated 'Case No. 1:26-cv-128' in its criteria and printed 'Case No.
    1:26-(cid:70)(cid:89)-128' in its headmatter (the user, 2026-08-21). The
    proof is good for both or for neither.
    """
    plain = line.plain or ""
    if "(cid:" not in plain:
        return None
    try:
        fixed = _CID.sub(lambda mm: chr(int(mm.group(1)) + 29), plain)
    except ValueError:
        return None
    if not fixed.isprintable() or "(cid:" in fixed:
        return None
    if _docket_value(_norm(fixed), facts) is None:
        return None            # it does not land on a case number: no proof
    try:
        return _CID.sub(lambda mm: chr(int(mm.group(1)) + 29),
                        line_markup(line))
    except ValueError:
        return None


def _docket_value(text: str, facts: EcfPaper):
    """The docket the row states, or None. A number is required: 'No.' alone
    heads nothing, and 'Notice of…' is not a docket."""
    flat = _norm(text)
    if len(flat) > 90:
        return None
    mm = facts.docket_re.match(flat)
    if mm is None:
        return None
    value = _norm(mm.group(1)).rstrip(".,")
    _fixed = _decode_cid_docket(value)
    if _fixed is not None:
        return _fixed
    if not any(c.isdigit() for c in value):
        return None
    # THE FEDERAL CASE NUMBER: year, nature of suit, sequence, and the
    # judges' initials the clerk hangs off the end — '26-cv-20232-BLOOM/
    # Elfenbein' (flsd), '1:23-CV-1376-TWT' (gand). The initials are words,
    # so the prose test below reads them as prose and threw the docket away.
    if re.search(r"\d+\s*[-:]\s*[a-z]{2,4}\s*[-:]\s*\d+", value, re.I):
        return value
    if re.search(r"[a-z]{4}", value) and not re.search(r"\d[-:]\d", value) \
            and not re.search(r"\d{2}-\d", value):
        return None                        # prose that merely opens 'No…'
    return value


def _is_asterisk_band(text: str, facts: EcfPaper) -> bool:
    flat = text.strip()
    return (bool(flat) and set(flat) <= {"*", " "}
            and flat.count("*") >= facts.asterisk_floor)


def _looks_like_overlay(text: str) -> bool:
    """A row standing ABOVE the masthead: the CM/ECF stamp, its wrapped tail
    ('ID#: 712', '1102'), or an e-filing badge. Short, fielded, numeric —
    never a sentence."""
    flat = _norm(text)
    if not flat:
        return True
    if _looks_like_efiling_stamp(flat) or is_folio_text(flat):
        return True
    # The stamp wraps where the district's name is long, and its tail is a
    # fragment of the folio it was cut out of: cod's stamp ends '… USDC
    # Colorado pg 1' and wraps to 'of 14'.
    # 'Pageid#: 4114' (vawd) has no word boundary before the ID, so a
    # \bID pattern misses it and the stamp's tail was read as the first row
    # of the court's own masthead.
    if len(flat) <= 40 and (re.search(r"(?:\bID|page\s?id)#?\s*[:.]",
                                      flat, re.I)
                            or re.fullmatch(r"(?:pg\s*)?\d*\s*of\s*\d+",
                                            flat, re.I)
                            or re.fullmatch(r"[\d\s.,#:-]+", flat)
                            or flat.upper() in ("E-FILED", "FILED",
                                                "ENTERED", "RECEIVED")):
        return True
    return False


# --------------------------------------------------------------------------
# the divider and the closer — measured, then dispatched on
# --------------------------------------------------------------------------

def _line_number_rail(lines: list, page_width: float,
                      facts: "EcfPaper") -> set:
    """The ids of a PLEADING PAPER's line numbers.

    The 9th Circuit's districts print their orders on numbered pleading
    paper: a rail of bare numerals down the left margin, one per typed line,
    running the whole height of the sheet. They are the paper's furniture,
    not the court's text — but they are not the ECF stamp either, so the
    overlay walk stops at the first one and the masthead is never reached.
    Measured as a RUN, never one numeral at a time: eight or more bare
    numerals standing left of the measure, ASCENDING down the page."""
    cand = [l for l in lines
            if l.x0 < page_width * facts.line_number_x
            and re.fullmatch(r"\d{1,2}", l.plain.strip())]
    if len(cand) < facts.line_number_floor:
        return set()
    cand.sort(key=lambda l: l.top)
    run, best = [], []
    for line in cand:
        n = int(line.plain.strip())
        if run and n != int(run[-1].plain.strip()) + 1:
            if len(run) > len(best):
                best = run
            run = []
        run.append(line)
    if len(run) > len(best):
        best = run
    if len(best) < facts.line_number_floor:
        return set()
    return {l.id for l in best}


def _on_axis(line, page_width: float, body_x0: float = 0.0,
             column: float | None = None) -> bool:
    """Is the row's midpoint on the page axis? The masthead is the court
    naming ITSELF and one chambers sets it wide — 'IN THE DISTRICT COURT OF
    THE UNITED STATES FOR THE' spans 96-516 of a 612pt page, which core's
    `line_alignment` calls full-measure justified prose and therefore 'L'.
    Core is right for prose and wrong for this row, so the paper measures its
    own masthead rather than asking core to loosen a rule that protects every
    other court.

    A ROW THAT STARTS AT THE BODY RAIL IS NOT CENTRED, however its midpoint
    falls. A caption's first row often carries BOTH columns and the rail
    between them ('JASON SCUTT, an individual, on ) CIV. NO. 20-00187 HG-WRP'
    — hid), and such a row is wide enough to sit on the axis by accident: it
    was read as a third masthead row, which put the parties inside the
    court's name and left the docket to be guessed at from a page-ID stamp."""
    if line.x0 <= body_x0 + 12:
        return False
    # THE AXIS IS THE MEASURE'S, NOT THE PAGE'S. Pleading paper moves the
    # whole text column right to leave the line-number rail its margin, and
    # the court centres its masthead on the COLUMN: cand sets it at midpoint
    # 338 on a 612pt sheet whose centre is 306. Judged against the page, the
    # masthead is not centred, the anchor is never found, and the record is
    # refused — 63 records across azd, cand and caed, every one of them.
    axis = (body_x0 + column / 2) if column else page_width / 2
    return abs((line.x0 + line.x1) / 2 - axis) < 25


def _standing_alone(line, at: int) -> bool:
    """Is the character at ``at`` the only ink on its own patch of the row?

    A DIVIDER GLYPH STANDS ALONE. ')' is also ordinary punctuation, and an
    undrawn court's caption band reaches down into its own prose — where
    '(Doc. 1)', '(RDM)' and '(“CEO”)' stack four deep at nearly one x often
    enough to fake a rail. Measured on dcd: nine of 32 records were claimed
    as glyph-rail captions on the strength of body parentheses, and the rest
    were lost because the false rail moved the caption's foot into the
    opinion. What separates the divider from the punctuation is that nothing
    is written against it."""
    chars = line.chars
    before = (chars[at - 1].get("text") or "") if at > 0 else " "
    after = (chars[at + 1].get("text") or "") if at + 1 < len(chars) else " "
    return not before.strip() and not after.strip()


def _glyph_rail(lines: list, facts: EcfPaper) -> dict | None:
    """A stacked column of one rail glyph, or None."""
    best = None
    for glyph in facts.rail_chars:
        chars = [c for l in lines for i, c in enumerate(l.chars)
                 if (c.get("text") or "") == glyph and _standing_alone(l, i)]
        if len(chars) < facts.rail_floor:
            continue
        x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
        stack = [c for c in chars if abs(c["x0"] - x) < facts.rail_column]
        if len(stack) < facts.rail_floor:
            continue
        found = {"glyph": glyph, "x": float(x), "n": len(stack),
                 "top": min(c["top"] for c in stack),
                 "bottom": max(c["bottom"] for c in stack)}
        if best is None or found["n"] > best["n"]:
            best = found
    return best


def _drawn_rail(pm, band: tuple, facts: EcfPaper) -> dict | None:
    """The chambers' drawn column divider, or None."""
    for v in pm.v_rules:
        if v.height < facts.drawn_min_h:
            continue
        if not (pm.width * facts.drawn_x[0] <= v.x
                <= pm.width * facts.drawn_x[1]):
            continue
        if v.bottom < band[0] or v.top > band[1]:
            continue
        return {"glyph": None, "x": float(v.x), "top": v.top,
                "bottom": v.bottom}
    return None


def _underlined_by(line, r) -> bool:
    """Is ``r`` this row's underline? The relation `_underlined` tests, read
    from the rule's side so a fence can be told from an emphasis.

    Bounded at BOTH ends rather than matched exactly: a chambers underlines
    the NAME and not the comma after it, so nhd's rule under 'United States
    of America,' stops 7pt short of the row's ink and an exact test missed
    it. What an underline may not do is run PAST the row — that is what
    tells it from a box edge, which is drawn to the box's own width whatever
    happens to stand above it.
    """
    if not line.size or not line.plain.strip():
        return False
    lo = line.top + line.size * 0.5
    hi = line.top + line.size + 6.0
    if not (lo <= r.top <= hi):
        return False
    if r.x0 > line.x0 + 4 or r.x1 > line.x1 + 6:
        return False
    return r.x1 >= line.x0 + 0.9 * (line.x1 - line.x0)


def _underlined(pm, line) -> bool:
    """Does the court UNDERLINE this row? A drawn horizontal beginning and
    ending with the row's own ink, struck through its descender band, is the
    chambers' emphasis on it — the same statement bold makes. nysd sets its
    paper's name in the caption's right column in plain roman and underlines
    it ('MEMORANDUM &' over a rule at 414.0-517.0 against the row's own
    414.0-516.9), so a test for bold or centring could not see the title at
    all and the record was refused for having no closer."""
    if not line.size:
        return False
    lo = line.top + line.size * 0.5
    hi = line.top + line.size + 6.0
    for r in pm.h_rules:
        if not (lo <= r.top <= hi):
            continue
        if r.x0 <= line.x0 + 4 and r.x1 >= line.x1 - 4:
            return True
    return False


def _stroke_next(fence: list, stroke) -> float:
    """The top of the stroke below ``stroke``, or the page's foot — the
    bound of the run this stroke opens."""
    for other in fence:
        if other.top > stroke.top:
            return other.top
    return float("inf")


def _centre_fence(pm, facts: EcfPaper) -> list:
    """The short strokes a chambers rules its caption with ON THE PAGE AXIS.

    A paper that never names its court has no masthead for the walk to
    anchor on, and `_drawn_fence` cannot see these strokes either — it wants
    a rule that STARTS at the body rail, and these start halfway across the
    sheet. What they are is a fence of their own: three identical strokes
    centred on the axis, the docket between the first two, the party stack
    between the second and third, and the paper's title or its opening
    paragraph below the third.

    Measured on the three records in the corpus that draw it — paed/658030,
    txed/243348 and txed/245820, two courts sharing one chambers template
    (the paed record is a transferred order signed by a Texas judge) — every
    stroke of all three is x 288.0-324.0 on a 612pt sheet. Swept over all
    2,217 district records, nothing else in the corpus draws this shape.

    Returned in page order, or [] where the page does not draw it."""
    axis = pm.width / 2
    out = [r for r in sorted(pm.h_rules, key=lambda r: r.top)
           if (r.x1 - r.x0) <= facts.centre_fence_max_w
           and abs((r.x0 + r.x1) / 2 - axis) <= facts.centre_fence_axis
           and r.top <= pm.height * facts.centre_fence_band]
    if len(out) < facts.centre_fence_min:
        return []
    # ONE FENCE, ONE STROKE WIDTH. The strokes are the same rule drawn three
    # times; a page whose short centred marks disagree about their width is
    # showing something else (a column of dashes, a struck-through cell).
    w0 = out[0].x1 - out[0].x0
    if any(abs((r.x1 - r.x0) - w0) > 2.0 for r in out):
        return []
    return out


def _drawn_fence(pm, body_x0: float, measure: float, facts: EcfPaper) -> list:
    """The horizontal strokes a chambers RULES its caption box with.

    Told from every other drawn horizontal by three measurements: it starts
    at the body rail, it stops short of the measure (a rule that runs the
    whole column is a header or a footer, not a caption's edge), and it is
    long enough not to be an underline. nynd draws 79.2-367.2 on a sheet
    whose measure ends at 533."""
    out = []
    for r in sorted(pm.h_rules, key=lambda r: r.top):
        # AN UNDERLINE IS NOT AN EDGE, however long it is. The width bound
        # below was the only thing keeping them out, and it cannot: nhd
        # underlines every party name in its caption, and those rules run
        # 137-259pt — well past any floor a real box edge has to clear.
        # Two of them were read as the box's top and bottom, which made a
        # band ONE ROW deep; the caption came back holding 'and State of New
        # Hampshire' alone and the three rows under it — the rest of the
        # parties, the pivot and the docket — were read as the appearances
        # of counsel. The relation is already named above: a stroke that
        # begins and ends with a row's own ink, struck through its descender
        # band, belongs to that row.
        # …EXCEPT UNDER THE PAPER'S OWN NAME. A chambers that underlines its
        # title draws the only strokes on the sheet, and the box test has
        # always used them: ncmd sets 'ORDER AND MEMORANDUM OPINION' / 'OF
        # UNITED STATES MAGISTRATE JUDGE' underlined and nothing else, and
        # excluding those two refused the record outright. What nhd
        # underlines is its PARTY NAMES, which no box edge ever sits under.
        if any(_underlined_by(line, r) and not _is_title_row(
                _norm(line.plain), facts) for line in pm.lines):
            continue
        # THE BOX'S FOOT MAY STAND DEEP. Searched only to the closer band,
        # mnd/202185's box — whose caption names enough parties to push the
        # foot past 55% of the sheet — showed only its TOP and was not a box
        # at all. The box's TOP is still pinned to the masthead by `_box` in
        # the walk, which is what keeps a header rule out.
        if r.top >= pm.height * facts.box_band:
            continue
        if r.x0 > body_x0 + 8:
            continue
        if r.width < facts.fence_min_w:
            continue
        if r.x1 > body_x0 + measure * facts.fence_max_reach:
            continue
        if out and abs(r.top - out[-1].top) <= facts.fence_join:
            continue                       # the same stroke, drawn twice
        out.append(r)
    return out


def _foot_rule(pm, band: tuple, rail: dict | None, body_x0: float,
               facts: EcfPaper):
    """The caption box's FOOT: a drawn horizontal from the body rail to the
    divider, standing BELOW the divider it closes.

    Where a chambers draws the whole box rather than just its foot, the same
    test matches the box's TOP rule — and taking that one puts the caption's
    foot above its own parties, so the band comes back empty and the record
    is refused. Measured on dcd, which draws all four sides: 23 of 32 records
    were lost this way. The foot is the rule the rail ENDS on."""
    if rail is None:
        return None
    mid = rail["x"]
    floor = rail.get("bottom")
    for r in sorted(pm.h_rules, key=lambda r: r.top):
        if not (band[0] <= r.top <= band[1]):
            continue
        if r.x0 > body_x0 + 8:
            continue                       # starts inside the measure
        if floor is not None and r.top < floor - 2:
            continue                       # the box's top, not its foot
        if abs(r.x1 - mid) <= facts.foot_rule_end:
            return r
    return None


def _rail_chars(line, rail, facts: EcfPaper) -> list:
    lo = rail["x"] - facts.rail_window
    hi = rail["x"] + facts.rail_window
    return [c for c in line.chars
            if (c.get("text") or "") == rail["glyph"] and lo <= c["x0"] <= hi]


def _shed_rail(line, rail, facts: EcfPaper):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character: a ')' closing real text
    is not in the rail's column."""
    if rail is None or rail["glyph"] is None:
        return line
    drop = {id(c) for c in _rail_chars(line, rail, facts)}
    if not drop:
        return line
    kept = [c for c in line.chars if id(c) not in drop]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept,
                    x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` lying one side of the divider, or None. Split
    glyph by glyph: whether pdfio already broke a row at its column gap is an
    accident of how wide the gap happened to be, and one chambers sets
    ')Civil Action No. 2:24-cv-00181-SCM-CJS' as a single run."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _sides(caption_rows: list, facts: EcfPaper, one_sided: bool = False):
    """The party names either side of the pivot, built from the NAMES —
    never by joining the caption wholesale, which yields 'CIVIL ACTION NO.
    25-171-DLB-CJS LINDA MOORE'."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        if _is_pivot_row(flat, facts):
            side = right
            seen = True
            continue
        if _is_status_row(flat, facts):
            continue
        head = flat.split(None, 1)
        if head and head[0].rstrip(".").lower() in facts.pivots:
            side = right
            seen = True
            flat = _norm(head[1]) if len(head) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

def read_ecf(model, geom, facts: EcfPaper = DEFAULT, **_):
    """Read one district court's ECF pleading order, or NOTHING.

    NOTHING is the honest answer for a record that is not this paper — a
    court whose corpus answers NOTHING often is a court whose facts have not
    been measured yet, not a court core should be left to guess at."""
    if not model.pages:
        return _refuse("no-lines")
    pm = model.pages[0]
    pw, ph = pm.width, pm.height
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    live = [l for l in pm.lines if l.plain.strip()]
    live.sort(key=lambda l: (l.top, l.x0))
    if not live:
        return _refuse("no-live")
    numbers = _line_number_rail(live, pw, facts)
    if numbers:
        live = [l for l in live if l.id not in numbers]
        if not live:
            return _refuse("all-line-numbers")


    def align(line) -> str:
        return line_alignment(line, pw, geom,
                              banner_center_min_size=body_size + 2.0)

    measure = getattr(geom, "column", None) if geom else None
    # THE MEASURE, WHERE CORE COULD NOT TAKE IT. `geometry.measure` returns
    # None on a short pleading-paper record — cacd/980704 is two pages, and
    # most of what is on them is the line-number rail — and the fallbacks
    # then put the body rail at 72 and the axis at the PAGE's centre, 306 on
    # a 612pt sheet. But pleading paper moves the whole text column right to
    # leave the rail its margin: that record's column is centred on 340, so
    # the masthead stood 34pt off an axis it was never set to and the record
    # was refused for not naming its court. The rail is already known here,
    # so the column is measurable without core: the modal left edge of what
    # remains, out to the widest right edge.
    if geom is None and numbers:
        _lefts = Counter(round(l.x0) for l in live)
        body_x0 = float(_lefts.most_common(1)[0][0])
        measure = max(l.x1 for l in live) - body_x0

    def centred(line) -> bool:
        return align(line) == "C" or _on_axis(line, pw, body_x0, measure)

    # ---- the masthead is the ANCHOR, and the overlay is what stands above
    # it ------------------------------------------------------------------
    # The overlay was once read forwards, row by row, each row having to LOOK
    # like a stamp. That cannot be spelled: every district's clerk stamps its
    # own way ('E-FILED / Wednesday, 05 August, 2026 10:38:56 AM / Clerk,
    # U.S. District Court, ILCD', 'FILED / 2026 May-11 PM 03:10 / U.S.
    # DISTRICT COURT / N.D. OF ALABAMA'), and a stamp row that failed the
    # spelling ended the walk and lost the record — measured on ilcd, alnd,
    # scd and tnwd, 109 records between them, every one refused.
    #
    # So the masthead is found FIRST, by what only it can be: a CENTRED row
    # in which the court names itself. Everything above it is the overlay,
    # whatever it says. The masthead may open with a row that names no court
    # ('IN THE' — ilcd), so the run is walked BACK from the anchor over
    # contiguous centred rows — stopping at the stamp's own wrapped tail
    # ('ID#: 132' is centred and would otherwise be read as the masthead's
    # first row, which cost kyed 14 of its 25 records).
    dfence = _drawn_fence(pm, body_x0, measure or (pw * 0.76), facts)
    anchor = None
    named = [k for k, line in enumerate(live)
             if line.top <= ph * facts.masthead_band
             and not _looks_like_overlay(line.plain)
             and _spells_court(line.plain, facts.court_name)]
    for k in named:
        if centred(live[k]):
            anchor = k
            break
    left_set = False
    if anchor is None:
        # A FENCED COURT SETS ITS MASTHEAD FLUSH LEFT. The Second Circuit's
        # districts do not centre anything: the court, the district and the
        # '-----X' that opens the caption all stand at the body rail. There
        # the fence, not the centring, is what says 'this row is the
        # masthead' — so a left-set name is accepted only when a typed rule
        # stands under it.
        # …AND A DRAWN STROKE SAYS IT AS WELL AS A TYPED ONE. nynd sets
        # 'UNITED STATES DISTRICT COURT' at the body rail and RULES the box
        # under it instead of typing underscores; with only the typed test
        # here, the centring gate refused the row and 16 of 24 records came
        # back unread.
        for k in named:
            if any(_is_typed_rule(l.plain) and l.top > live[k].top
                   and l.top < ph * facts.closer_band for l in live[k + 1:]) \
                    or any(r.top > live[k].top for r in dfence):
                anchor = k
                left_set = True
                break
    open_left = False
    if anchor is None:
        # …AND SOME CHAMBERS DRAW NOTHING AT ALL. nysd and nyed set the
        # masthead at the body rail and mark the caption with neither a rule
        # nor a fence nor a rail — so neither the centring gate nor the
        # fenced fallback above will take it, and the record is refused for
        # never naming its court. What stands in for the fence there is
        # POSITION: the row names the court, it stands at the rail, and
        # nothing but the clerk's stamp is above it. Where that is the
        # evidence, the masthead's run has to end on the court's own name
        # too — see `open_left` in the walk below.
        for k in named:
            if live[k].x0 > body_x0 + 12:
                continue
            if any(not _looks_like_overlay(l.plain) for l in live[:k]):
                continue
            anchor = k
            left_set = True
            open_left = True
            break
    cfence: list = []
    if anchor is None:
        # …AND SOME PAPERS NEVER NAME THEIR COURT AT ALL. The sheet opens on
        # the clerk's stamp and goes straight into a caption fenced by short
        # strokes on the page axis. There is no masthead to anchor on and
        # none to walk back over, so the fence itself is the anchor: what
        # stands above its first stroke is the overlay, and the caption is
        # what stands between the first stroke and the last.
        cfence = _centre_fence(pm, facts)
        if not cfence:
            return _refuse("no-masthead-anchor")                 # the court never names itself
    # THE BOX'S TOP IS THE STROKE BELOW THE COURT'S NAME. `_drawn_fence` will
    # not judge which strokes are the box — it cannot, since it runs before
    # the masthead is found — and once full-measure strokes were allowed in
    # (mnd, wiwd) it began returning page-border rules too. txed rules its
    # sheet at 71.9 AND 114.7, both 72.0-539.9, with the masthead at 91.2
    # between them: the walk broke on the FIRST of them, above the masthead,
    # and the record was refused for having no masthead at all.
    dbelow = [] if cfence else [r for r in dfence
                                if r.top > live[anchor].top]
    mast_at = (next((k for k, l in enumerate(live) if l.top > cfence[0].top),
                    len(live))
               if cfence else anchor)
    while (mast_at > 0 and centred(live[mast_at - 1])
           and not _looks_like_overlay(live[mast_at - 1].plain)
           # …AND NEVER BACK OVER A TYPED RULE. cacd rules the sheet ABOVE
           # its own name; walked into the masthead run, the rule then ENDED
           # that run at its first row and the record was refused for having
           # no masthead (cacd/1021353).
           and not _is_typed_rule(live[mast_at - 1].plain)):
        mast_at -= 1
    overlay = live[:mast_at]

    # ---- is the caption FENCED rather than divided? ---------------------
    # Two typed rules in the top band are the box, and they answer three
    # questions at once: where the masthead ends, where the caption band
    # begins, and what closes it. They are looked for FIRST because a fenced
    # court sets its masthead flush left, which the centred-masthead gate
    # below would refuse.
    fence = [l for l in live[mast_at:]
             if l.top < ph * facts.closer_band and _is_typed_rule(l.plain)]

    # ---- the masthead: the run of CENTRED rows the anchor sits in -------
    band_hi = ph * facts.closer_band

    # The masthead run, once: the court naming itself and nothing under it.
    # Where the court sets it flush left the run cannot be measured by
    # centring — it ends where the fence opens the caption.
    mast = []
    j = mast_at
    side: list = []
    while j < len(live) and not cfence:
        line = live[j]
        # A TYPED RULE IS NEVER THE COURT'S NAME. wyd centres the box's top
        # edge — '__________________________________' at x 204-408 on a
        # 612pt sheet — so the centring test took it as a third masthead row
        # and the record reported the court as 'IN THE UNITED STATES DISTRICT
        # COURT / FOR THE DISTRICT OF WYOMING / ______'.
        if _is_typed_rule(line.plain):
            break
        if left_set:
            if dbelow and line.top > dbelow[0].top:
                break
            if open_left and mast and not _names_court(line.plain, facts):
                break
        elif not centred(line):
            # A STAMP IN THE MARGIN DOES NOT END THE MASTHEAD. vawd's clerk
            # sets '6/30/2026' out at the right edge on the SAME ROW as 'IN
            # THE UNITED STATES DISTRICT COURT'; read as the end of the run,
            # it left the district and the division to be read as parties.
            if mast and abs(line.top - mast[-1].top) <= 2.5:
                side.append(line)
                j += 1
                continue
            break
        if mast and _ends_masthead(line.plain, facts):
            break
        mast.append(line)
        j += 1
    if not mast and not cfence:
        return _refuse("masthead-empty")

    # THE ASSIGNED JUDGE IS NAMED, NOT CAPTIONED. Several districts print the
    # judge who holds the case as a third centred line under the masthead
    # ('District Judge S. Kato Crews' — cod). Ending the masthead is right —
    # it is not the court's name — but it is not the caption either: handed
    # to the caption band, its x0 fell right of the gutter, so it stood in
    # the box's RIGHT column against an empty party cell, labelled 'caption'
    # (the user, 2026-08-20: 'it had judge with the court in the third line
    # of the headmatter, it now moved it to the right side but labeled in
    # caption'). It is a centred row of its own and is emitted as one.
    bench: list = []
    while j < len(live) and centred(live[j]) and _is_judge_row(live[j].plain):
        bench.append(live[j])
        j += 1

    # THE BOX OPENS DIRECTLY UNDER THE MASTHEAD, and that is what makes it
    # the caption's box rather than some other typed rule on the page. cod
    # fences its TITLE in the same hyphens, halfway down the sheet — read as
    # the caption's box, the fence put every party into the masthead and the
    # record came back with no caption at all.
    boxed = (not cfence and len(fence) >= 2
             and j < len(live) and fence[0] is live[j])
    # THE DRAWN BOX IS RECOGNISED THE SAME WAY: two strokes, the first of
    # them standing directly under the masthead run. A typed fence wins where
    # a court has both — nynd underlines its own typed rules, so the drawn
    # strokes there are the underlines and not the box.
    # …and the band it makes has to be able to HOLD a caption: two strokes
    # less than one line of type apart are one edge however they were drawn,
    # and reading them as a box refuses the record outright.
    _box = [] if cfence else [r for r in dfence
                              if r.top >= mast[-1].top
                              and r.top <= ph * facts.box_band]
    dboxed = (not boxed and len(_box) >= 2
              and _box[0].top <= mast[-1].bottom + facts.rail_head_slack
              and _box[1].top - _box[0].top >= body_size)
    if cfence:
        # THE FIRST STROKE OPENS THE CAPTION AND THE LAST CLOSES IT. What
        # falls between them is the docket and the party stack; the strokes
        # in between divide the two and are furniture of the fence, recorded
        # with the rest of it.
        closer = None
        band_lo = cfence[0].top
        band_hi = cfence[-1].top
        cap_band = (band_lo, band_hi)
    elif boxed:
        j += 1
        band_lo = fence[0].bottom
        closer = fence[1]
        cap_band = (band_lo, closer.top)
    elif dboxed:
        closer = None
        band_lo = _box[0].top
        band_hi = _box[1].top
        cap_band = (band_lo, band_hi)
    else:
        band_lo = (bench[-1] if bench else mast[-1]).bottom
        # ONE RULE STILL OPENS THE BAND. A box whose foot stands below the
        # closer band has only its TOP edge inside it, so `fence` holds a
        # single row and the box is not recognised — but that row is still
        # where the caption begins, and left in the band it renders as a
        # caption cell made of underscores (wyd, 10 of 10 records).
        if j < len(live) and _is_typed_rule(live[j].plain):
            band_lo = live[j].bottom
            j += 1

        # A DRAWN BOX DECLARES ITS OWN DEPTH. Measured before the closer, so
        # that a caption reaching past the closer band is still read whole.
        deep = None
        for v in pm.v_rules:
            if v.height < facts.drawn_min_h:
                continue
            if not (pw * facts.drawn_x[0] <= v.x <= pw * facts.drawn_x[1]):
                continue
            if v.top > band_lo + facts.rail_head_slack:
                continue
            if v.bottom > ph * facts.box_band:
                continue
            if deep is None or v.bottom > deep:
                deep = v.bottom
        # A GLYPH RAIL DECLARES ITS DEPTH THE SAME WAY. rid stacks a long
        # caption down to y 623 of a 792pt page and the band, capped at the
        # closer's 55%, cut it in half. The rail must START at the caption
        # or a column of body punctuation could pass for one.
        gdeep = _glyph_rail(
            [l for l in live[j:]
             if band_lo - 2 <= l.top <= ph * facts.box_band], facts)
        if (gdeep is not None
                and gdeep["top"] <= band_lo + facts.rail_head_slack
                and gdeep["bottom"] > (deep or 0)):
            deep = gdeep["bottom"]
        if deep is not None and deep > band_hi:
            band_hi = deep + 2

        # ---- the closer -------------------------------------------------
        closer = None
        for line in live[j:]:
            if line.top > band_hi:
                break
            if _is_asterisk_band(line.plain, facts):
                closer = line
                break
        cap_band = (band_lo, closer.top if closer else band_hi)

    # ---- the divider ----------------------------------------------------
    in_band = [l for l in live[j:]
               if l.top >= cap_band[0] and l.top <= cap_band[1] + 2
               and l is not closer and l not in fence]
    if not in_band:
        return _refuse("band-empty")
    rail = _glyph_rail(in_band, facts) or _drawn_rail(pm, cap_band, facts)
    mid = rail["x"] if rail else None
    foot = _foot_rule(pm, (cap_band[0], band_hi), rail, body_x0, facts)
    if closer is None and not dboxed:
        if foot is not None:
            cap_band = (band_lo, foot.top)
            in_band = [l for l in in_band if l.top < foot.top]
        elif rail is None:
            # NOTHING IS DRAWN AND NOTHING IS TYPED. The caption simply ends
            # and the paper's own name stands under it, alone on its row and
            # on the page axis — that title row IS the closer. Measured on
            # ared (32 of 33 records), flmd and mnd, which set no rail, no
            # asterisk band and no rule of any kind.
            # A LONG CAPTION PUSHES THE TITLE PAST THE CLOSER BAND. ared
            # names fourteen defendants and its 'ORDER' lands at 469 of a
            # 792pt page — 59%, past the 55% the band allows — so the search
            # stopped above it and the record was refused outright. The
            # title's own test is strong enough to look deeper: alone on its
            # row, opening a paper name, set in the court's own emphasis.
            deep_hi = ph * facts.box_band
            title_row = None
            for line in live[j:]:
                if line.top > deep_hi:
                    break
                if any(o is not line and abs(o.top - line.top) <= 2.5
                       for o in live[j:]):
                    continue               # shares its row: a caption cell
                flat = _norm(line.plain)
                if _is_title_head(flat, facts) \
                        and not _is_status_row(flat, facts) \
                        and (line.all_bold or centred(line)
                             or _underlined(pm, line)):
                    title_row = line
                    break
            if title_row is None:
                # THE BODY IS THE CLOSER. Some chambers mark the end of the
                # caption with nothing whatever: no rail, no rule, no
                # asterisks, and the paper's name set in the caption's own
                # right column beside the pivot rather than under it
                # ('DECISION AND ORDER' — nywd). What ends the caption there
                # is the opinion: the first row that runs the FULL MEASURE
                # and stands alone, which no caption cell ever does.
                column = getattr(geom, "column", 0.0) or (pw * 0.76)
                body_row = None
                for line in live[j:]:
                    if line.top > band_hi:
                        break
                    if line.top <= band_lo:
                        continue
                    if any(o is not line and abs(o.top - line.top) <= 2.5
                           for o in live[j:]):
                        continue           # a two-column row is the caption
                    if (line.x1 - line.x0) >= 0.82 * column:
                        body_row = line
                        break
                if body_row is None:
                    # THE LAST STATUS ROW IS THE FOOT. ord draws nothing,
                    # types nothing, sets the paper's name in the caption's
                    # RIGHT COLUMN halfway down the block (so the title test
                    # cannot take it without cutting off the defendants
                    # below it), and prints no full-measure row on page 1 at
                    # all — its counsel roster is a column of short lines.
                    # Four records were refused for having no closer.
                    #
                    # But a caption ends by saying what its last party IS.
                    # 'Defendants.' / 'Plaintiffs,' is a closed vocabulary
                    # (`_is_status_row` demands every word be one), and
                    # nothing below a caption is a bare status word — ord's
                    # own roster ends 'Attorneys for Plaintiff', which is
                    # not one. Tried last, so no court that closes any other
                    # way is touched.
                    last_status = None
                    for line in live[j:]:
                        if line.top > deep_hi:
                            break
                        if line.top <= band_lo:
                            continue
                        if _is_status_row(_norm(line.plain), facts):
                            last_status = line
                    if last_status is None:
                        return _refuse("no-closer-at-all")
                    cap_band = (band_lo, last_status.bottom + 1)
                    in_band = [l for l in live[j:]
                               if band_lo <= l.top <= last_status.top + 2.5
                               and l is not closer and l not in fence]
                else:
                    cap_band = (band_lo, body_row.top - 2)
                    in_band = [l for l in in_band if l.top < body_row.top - 1]
            else:
                cap_band = (band_lo, title_row.top - 2)
                in_band = [l for l in live[j:]
                           if band_lo <= l.top < title_row.top - 1
                           and l is not closer and l not in fence]
        elif rail is not None:
            # THE RAIL'S OWN FOOT is the third closer. Most chambers type
            # neither an asterisk band nor draw a box: the rail simply STOPS,
            # and the paper's name stands under it. Measured on almd, where
            # 48 of 50 records close this way and nothing is drawn on the
            # page at all. The band therefore ends where the rail ends — not
            # at the closer band, which would swallow the title and the
            # opening paragraphs into the caption.
            cap_band = (band_lo, rail["bottom"])
            in_band = [l for l in in_band if l.top <= rail["bottom"] + 1]
            # …AND THE STATUS ROW THE RAIL STOPS SHORT OF. A chambers types
            # the rail beside every row it means to divide and then sets the
            # last party's status under it without one — tned closes
            # 'CORRECTIONS, et al.,  )' / '  )' / 'Defendants.', where the
            # final row carries no glyph at all. Left outside, the caption's
            # own closing status was read as an APPEARANCE OF COUNSEL (the
            # user, 2026-08-21: 'defendants is not counsel its part of the
            # caption'). A STATUS is a closed vocabulary and nothing below a
            # caption is a bare status word, so the row is admitted on what
            # it says — within one line of the rail's foot, and one row only.
            _below = sorted((l for l in (live[j:] if _RAIL_STATUS_TAIL else [])
                             if rail["bottom"] + 1 < l.top
                             <= rail["bottom"] + 2.2 * (body_size or 12.0)),
                            key=lambda l: l.top)
            for _l in _below[:1]:
                if _is_status_row(_norm(_l.plain), facts):
                    in_band.append(_l)
                    cap_band = (band_lo, _l.bottom)
        else:
            return _refuse("no-closer-no-rail")                 # no closer, no rail: not this paper
        if not in_band:
            return _refuse("band-empty-after-closer")
    if cfence:
        style = STYLE_CENTRE_FENCE
    elif boxed and rail is None:
        style = STYLE_TYPED_BOX
    elif dboxed and rail is None:
        style = STYLE_DRAWN_BOX
    elif rail is None:
        style = STYLE_FLUSH_STATUS
    elif rail["glyph"] is None:
        style = STYLE_DRAWN_RAIL
    else:
        style = STYLE_GLYPH_RAIL

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list[int] = []

    # ---- the overlay is recorded, never rendered ------------------------
    # A claim must be TOTAL: a row the reader steps over is placed or
    # recorded. Core sees the stamp's first row by repetition and misses its
    # wrapped tail ('ID#: 132' rendered as an unread headmatter row, and
    # 'ID#: 16633' was read as the docket); a reader that claims the region
    # inherits its furniture.
    for line in pm.lines:
        if line.id in numbers:
            consumed.add(line.id)
    for line in overlay:
        # Core's furniture pass already surfaced what it could SEE by
        # repetition (the stamp's first row, a bare-numeral tail read as a
        # folio); recording those again puts the same row in `removed`
        # twice. Only what core missed is recorded here — the id is consumed
        # either way, so the claim stays total.
        if finder.kind(pm, line) is None:
            dropped.append(m.Dropped(text=_norm(line.plain),
                                     prov=m.Prov(1, (line.id,)),
                                     kind="stamp"))
        consumed.add(line.id)

    def emit(line, role: str, text: str | None = None):
        if text is None:
            text = _cid_markup(line, facts)
        items.append(m.HmLine(
            text=text if text is not None else line_markup(line),
            prov=m.Prov(1, (line.id,)),
            align=m.Align(align(line)), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    for line in side:                  # margin stamps beside the masthead
        if finder.kind(pm, line) is None:
            dropped.append(m.Dropped(text=_norm(line.plain),
                                     prov=m.Prov(1, (line.id,)),
                                     kind="stamp"))
        consumed.add(line.id)

    # THE BOX'S OWN EDGES. The reader steps over the fence rows — they are
    # neither the court's name nor a caption cell — but stepping over is not
    # CLAIMING. Unconsumed, ctd's '------------' closer came back as CONTENT
    # residual on 11 of its 31 records, which put every one of them on the
    # review worklist with nothing whatever to fix. Recorded here, the same
    # way the title walk records the rule it steps over.
    for _edge in fence + ([closer] if closer is not None else []):
        if _edge.id in consumed:
            continue
        dropped.append(m.Dropped(text=_norm(_edge.plain),
                                 prov=m.Prov(1, (_edge.id,)), kind="rule"))
        consumed.add(_edge.id)

    court_rows: list[str] = []
    for line in mast:
        court_rows.append(_norm(line.plain))
        emit(line, "court")
    for line in bench:
        # 'author', NOT 'judge'. The role vocabulary is closed — the render
        # tints exactly the roles it declares, and a made-up one renders
        # untinted and unlabelled. And the declared name is the right one
        # anyway: this row is the court announcing WHO WROTE the paper, which
        # is what minn's right-hand column does with 'Hudson, C.J.' (the user,
        # 2026-08-20: 'isnt it suppoesd to be author? not judge?').
        emit(line, "author")
    if bench:
        crit["judges"] = "; ".join(_norm(l.plain).rstrip(".") for l in bench)

    # ---- the caption that runs on to the next page ----------------------
    carried: list = []
    if mid is not None and len(model.pages) > 1:
        pm2 = model.pages[1]
        cont = None
        for v in pm2.v_rules:
            if v.height < facts.drawn_min_h or abs(v.x - mid) > 3.0:
                continue
            if v.top > pm2.height * facts.carry_top:
                continue
            cont = v
            break
        if cont is None and rail is not None and rail["glyph"] is not None:
            # A TYPED RAIL CARRIES BY ITS OWN GLYPHS. There is nothing drawn
            # to look for, so the proof is the rail itself: the same glyph,
            # in the same column, resuming inside the next page's top margin
            # (rid runs one caption over two pages this way).
            g2 = _glyph_rail([l for l in pm2.lines if l.plain.strip()], facts)
            if (g2 is not None and g2["glyph"] == rail["glyph"]
                    and abs(g2["x"] - mid) <= facts.rail_column
                    and g2["top"] <= pm2.height * facts.carry_top):
                cont = type("_R", (), {"bottom": g2["bottom"], "x": g2["x"]})()
        if cont is not None:
            foot2 = None
            for r in sorted(pm2.h_rules, key=lambda r: r.top):
                if r.top < cont.bottom - 2 or r.x0 > body_x0 + 8:
                    continue
                if abs(r.x1 - mid) <= facts.foot_rule_end:
                    foot2 = r
                    break
            stop = foot2.top if foot2 is not None else cont.bottom
            carried = [l for l in pm2.lines
                       if l.plain.strip() and l.top <= stop + 1]
            in_band = in_band + carried

    # ---- the court's own name, where it shares the caption's first row --
    if in_band:
        _first_top = min(l.top for l in in_band)
        for line in list(in_band):
            if abs(line.top - _first_top) > 2.5:
                continue
            if not _on_axis(line, pw, body_x0, measure):
                continue
            _f = _norm(line.plain)
            if len(_f) <= 2 and set(_f) <= set(facts.rail_chars):
                continue                   # the rail's own glyph, not a name
            # THE COURT'S OWN FACE is the signal, not the word. ared sets
            # 'NORTHERN DIVISION' in TimesNewRomanPS-BoldMT — the masthead's
            # face — while the party beside it is TimesNewRomanPSMT. A row
            # wearing the court's type at the court's size, centred on the
            # measure, is the court still naming itself. The wording is kept
            # only as a second route, for a chambers that changes face.
            _same_face = (mast and line.font == mast[0].font
                          and abs(line.size - mast[0].size) < 0.6)
            if not (_same_face or _DIVISION.match(_norm(line.plain))):
                continue
            court_rows.append(_norm(line.plain))
            emit(line, "court")
            in_band.remove(line)

    # ---- the caption band, row by visual row ---------------------------
    rows: list[list] = []
    rail_only: list = []
    # A TITLE STANDING INSIDE A CAPTION ROW. Where a chambers sets three
    # cells — party, paper's name, status — the block has only two columns
    # to put them in, and whichever way the row is cut the title fuses to a
    # neighbour ('DOES, et al. ORDER' — ared, where the party's trailing
    # spaces leave a 1.8pt gap to the title and 130pt to the status). The
    # paper's name is not caption content at all, so it is lifted out of the
    # row before the columns are measured.
    mid_titles: list = []
    if mid is None:
        for line in list(in_band):
            row_mates = [o for o in in_band
                         if o is not line and abs(o.top - line.top) <= 2.5]
            if len(row_mates) < 2:
                continue
            flat = _norm(line.plain)
            if _is_title_head(flat, facts) and not _is_status_row(flat, facts):
                mid_titles.append(line)
                in_band.remove(line)
                # …AND THE TITLE'S OWN WRAP GOES WITH IT. arwd sets 'REPORT
                # AND RECOMMENDATION' on the same typed row as the last
                # party and its status, and wraps 'OF THE UNITED STATES
                # MAGISTRATE JUDGE' onto the row below — alone there, it
                # stayed in the band and was tinted 'case info' beside an
                # empty party cell. The wrap is recognised the same way the
                # closer's is: alone on its row, at the paper's own pitch,
                # in the court's emphasis, continuing a title.
                prev = line
                for nxt in sorted((o for o in in_band if o.top > prev.top),
                                  key=lambda o: o.top):
                    if any(o is not nxt and abs(o.top - nxt.top) <= 2.5
                           for o in in_band):
                        break
                    if nxt.top - prev.bottom > (nxt.size or 12.0) * 0.75:
                        break
                    if not (nxt.all_bold or centred(nxt)):
                        break
                    if not _is_title_tail(_norm(nxt.plain), facts):
                        break
                    mid_titles.append(nxt)
                    in_band.remove(nxt)
                    prev = nxt

    for line in sorted(in_band, key=lambda l: (l.page, l.top, l.x0)):
        shed = _shed_rail(line, rail, facts)
        if shed is None:
            # THE PIECE WAS THE RAIL. It is still a line the reader took out
            # of the stream, so it is consumed here: left behind, the naked
            # glyphs opened the writing with six paragraphs reading ') )'.
            # The CaptionBlock's own `rail` reproduces them.
            rail_only.append(line)
            continue
        if rows and rows[-1][0].page == shed.page \
                and abs(rows[-1][0].top - shed.top) <= 2.5:
            rows[-1].append(shed)
        else:
            rows.append([shed])
    if not rows:
        return _refuse("no-caption-rows")
    for line in rail_only:
        consumed.add(line.id)

    def cell(parts: list, side: str = "L"):
        parts = sorted(parts, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = _cid_markup(p, facts) or line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align(first)), x0=first.x0,
            size=first.size or 0.0,
            bold=all(p.all_bold for p in parts),
            # THE DIVIDER ALREADY SAID WHAT THIS IS. The parties stand LEFT
            # of the rail; the right column holds what the clerk records
            # about the case — the docket, the paper's name, the bench, the
            # date, the flags. So the right column's default is case-info,
            # and the forms below only REFINE it. Defaulting it to 'caption'
            # made every cell no rule happened to name claim to be a party,
            # and turned every new form into a regex nobody should need.
            role="caption" if side == "L" else "case-info")

    def blank():
        return m.HmLine(text="", prov=m.Prov(1), role="caption")

    left: list = []
    right: list = []
    left_plain: list[str] = []
    right_plain: list[str] = []
    for row in rows:
        l_parts: list = []
        r_parts: list = []
        if mid is not None:
            for line in row:
                for side, bucket in ((_side(line, mid, "L"), l_parts),
                                     (_side(line, mid, "R"), r_parts)):
                    if side is not None:
                        bucket.append(side)
        else:
            # NO DIVIDER IS DRAWN, so the columns are the row's own PIECES:
            # pdfio split this row at the whitespace gutter the chambers
            # typed, and the first piece stands at the body rail while the
            # rest stand out to the right. A lone piece is placed by where it
            # starts — the status cell and the title both begin far right of
            # the rail, and the party and the pivot both begin on it.
            # THE COLUMNS PART AT THE WIDEST GAP IN THE ROW, not after the
            # first piece. A caption row can carry three pieces — the pivot,
            # the party's STATUS indented under it, and the paper's name out
            # in the right column ('V.' / 'Plaintiffs,' / 'DECISION AND
            # ORDER' — nywd) — and taking everything after the first piece
            # as the right column glued the status to the title, so the
            # title was never recognised. For a two-piece row this is the
            # same split as before.
            ordered = sorted(row, key=lambda l: l.x0)
            if cfence:
                # THE CENTRED FENCE DIVIDES TOP FROM BOTTOM, not left from
                # right. This caption is one centred stack — every row is a
                # lone piece on the page axis, so the x0 test below would
                # send the party names into the right-hand column and tint
                # them 'case info' beside empty party cells. What the middle
                # stroke separates is the DOCKET above it from the party
                # stack below it, which is the only division this paper
                # draws.
                (r_parts if ordered[0].top < cfence[1].top
                 else l_parts).extend(ordered)
            elif len(ordered) >= 2:
                cut = max(range(len(ordered) - 1),
                          key=lambda i: ordered[i + 1].x0 - ordered[i].x1)
                l_parts = ordered[:cut + 1]
                r_parts = ordered[cut + 1:]
            elif (ordered[0].x0 <= body_x0 + facts.lone_piece_reach
                  or _is_pivot_row(ordered[0].plain, facts)
                  or _is_status_row(ordered[0].plain, facts)):
                # THE PIVOT AND THE STATUS BELONG TO THE PARTIES. Placed by
                # x0 alone, a chambers that indents 'v.' or 'Plaintiff,'
                # further than the reach put them in the right column, where
                # the docket and the paper's name live — 25 records showed a
                # bare 'v.' filed under the docket's column.
                l_parts = [ordered[0]]
            else:
                r_parts = [ordered[0]]
        left.append(cell(l_parts, "L") if l_parts else blank())
        right.append(cell(r_parts, "R") if r_parts else blank())
        for p in l_parts + r_parts:
            consumed.add(p.id)
        left_plain.append(_norm(" ".join(p.plain for p in l_parts)))
        right_plain.append(_norm(" ".join(p.plain for p in r_parts)))

    # ---- what each cell IS ---------------------------------------------
    caption_rows: list[str] = []
    title_parts: list[str] = []
    for line in mid_titles:
        _flat = _norm(line.plain)
        _said = _title_text(_flat, facts)
        emit(line, "title", _said if _letter_spaced(_flat) else None)
        title_parts.append(_said)
        anchor_ids.append(line.id)
    for column, texts in ((left, left_plain), (right, right_plain)):
        open_title = False
        want_docket = False
        for cellrow, flat in zip(column, texts):
            if not flat:
                open_title = False
                continue
            if want_docket:
                # THE LABEL WAS ON ITS OWN ROW; this is its number.
                want_docket = False
                if _bare_docket(flat):
                    cellrow.role = "docket"
                    if crit.get("docket_number"):
                        crit.setdefault("other_dockets", []).append(_norm(flat))
                    else:
                        crit["docket_number"] = _norm(flat)
                    open_title = False
                    continue
            if _JURY.match(flat):
                cellrow.role = "case-info"
                open_title = False
                continue
            if _CASE_FLAG.match(flat) and not _JUDGE_CELL.match(flat):
                cellrow.role = "case-info"
                open_title = False
                continue
            _by = _BY_LINE.match(flat)
            if _by:
                cellrow.role = "author"
                if not crit.get("judges"):
                    crit["judges"] = _norm(_by.group(1))
                open_title = False
                continue
            _bench = _JUDGE_CELL.match(flat) or _HON_CELL.match(flat)
            if _bench:
                cellrow.role = "panel"
                # THE OFFICE ALONE NAMES NOBODY. 'United States District
                # Judge' standing under a signature rule is the bench's
                # title, not a member of it — tinted, never listed.
                if _bench.group(1).strip():
                    crit.setdefault("panel", []).append(_norm(flat))
                open_title = False
                continue
            _date = _DATE_CELL.match(flat)
            if _date:
                cellrow.role = "date"
                if not crit.get("decision_date"):
                    crit["decision_date"] = _norm(_date.group(1))
                open_title = False
                continue
            _cite = _OPINION_CITE.match(flat)
            if _cite and any(ch.isdigit() for ch in _cite.group(1)):
                cellrow.role = "citation"
                if not crit.get("citation"):
                    crit["citation"] = _norm(_cite.group(1))
                open_title = False
                continue
            if _unlabelled_docket(flat):
                cellrow.role = "docket"
                if not crit.get("docket_number"):
                    crit["docket_number"] = _norm(flat)
                else:
                    crit.setdefault("other_dockets", []).append(_norm(flat))
                open_title = False
                continue
            if _is_docket_label(flat):
                cellrow.role = "docket"
                want_docket = True
                open_title = False
                continue
            docket = _docket_value(flat, facts)
            if docket is not None:
                cellrow.role = "docket"
                if crit.get("docket_number"):
                    crit.setdefault("other_dockets", []).append(docket)
                else:
                    crit["docket_number"] = docket
                open_title = False
                continue
            # THE TITLE WRAPS, and its fragments are only the title where
            # they CONTINUE one: 'AND ORDER' opening a column would be an
            # unread row, not a paper name.
            if not _is_status_row(flat, facts) \
                    and (_is_title_head(flat, facts)
                         or (open_title and _is_title_tail(flat, facts))):
                cellrow.role = "title"
                title_parts.append(_title_text(flat, facts))
                anchor_ids.extend(cellrow.prov.line_ids)
                open_title = True
                continue
            open_title = False
            if column is left:
                caption_rows.append(_norm(flat))
            elif _is_status_row(flat, facts):
                # THE STATUS IS THE PARTY'S OWN, wherever it is set. A
                # flush-right template puts 'PLAINTIFF' out at the measure's
                # edge, and it is caption content there just as it is when
                # it sits indented under the name.
                cellrow.role = "caption"
    # THE RAIL'S OWN RUN is not the caption's rhythm: rows that held only
    # the divider are empty on both sides and render as phantom blanks.
    def _bare(row) -> bool:
        return not re.sub(r"<[^>]+>", "", row.text or "").strip()
    while left and _bare(left[-1]) and _bare(right[-1]):
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    if cfence:
        # REPRODUCE THE PAGE, DO NOT RESTRUCTURE IT. This caption has no
        # columns and no divider: it is one centred stack, fenced by three
        # strokes, with the DOCKET ON TOP — between the first stroke and the
        # second — and the parties below. Published as a CaptionBlock it
        # came out as two columns either side of a rail the page never
        # draws, the docket moved BELOW the parties because a right-hand
        # column renders after a left-hand one, and the three strokes
        # appeared nowhere at all — neither drawn nor recorded (the user,
        # 2026-08-21: 'the format isnt matching the pdf').
        #
        # The columns above still do the reading — they are what tells a
        # docket from a party and fills `parties` and `case_name` — but the
        # ITEMS are emitted here in the page's own order instead.
        _seen: set[int] = set()
        for _stroke in cfence:
            items.append(m.Rule(prov=m.Prov(1, ()), span="center"))
            for _cell in (c for c in right + left if not _bare(c)):
                if id(_cell) in _seen:
                    continue
                _at = min((l.top for l in in_band
                           if l.id in (_cell.prov.line_ids or ())),
                          default=None)
                if _at is None or _at > _stroke_next(cfence, _stroke):
                    continue
                _cell.align = m.Align.CENTER
                items.append(_cell)
                _seen.add(id(_cell))
    else:
        items.append(m.CaptionBlock(
            left=left, right=right,
            rail=(rail["glyph"] if rail else None), rail_rows=len(left),
            style_id=None,
            fp={"rail": rail["glyph"] if rail else None, "mid_x": mid,
                "band": cap_band},
            prov=m.Prov(1, tuple(sorted(l.id for l in in_band)))))

    # ---- the closer, and the foot rule the box draws --------------------
    # A DRAWN RULE WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT IS AN
    # UNDERLINE, not a fence: every chambers underscores its title, and
    # those rules are emphasis and are not re-emitted. The foot rule reaches
    # from the body rail to the divider and IS the box's border.
    if boxed:
        consumed.add(fence[0].id)
    if foot is not None:
        items.append(m.Rule(prov=m.Prov(1, ()), span="left"))
    if closer is not None:
        items.append(m.Rule(prov=m.Prov(1, (closer.id,)), typed=True,
                            span="left" if boxed else "center"))
        consumed.add(closer.id)

    # ---- the title the chambers set BELOW the box ----------------------
    # Where the rail's own foot is the closer, the paper's name is not in the
    # box's right column: it stands under the box, bold, on its own row or
    # two. The run is bold AND spells a title, row by row, because bold alone
    # runs straight on into the first heading ('I. INTRODUCTION') and, on one
    # almd record, into a bold quoted citation.
    # THE TITLE STANDS BELOW THE BOX far more often than it stands inside
    # it, and this scan used to run only where the caption had NO closer at
    # all. Every court that draws its box a foot rule was therefore never
    # looked at below it: measured, 28 of akd's 31 records, 27 of dcd's 32,
    # 23 of ctd's 31 — 243 records across the lane with no title read, on
    # pages that print one in bold under the caption. The scan now runs
    # wherever the box did not name the paper itself.
    # ---- the appearances the court prints under its caption -------------
    # Unclaimed, these become the opinion's FIRST PARAGRAPH: v1 renders this
    # court's roster as body prose, and so did we — 32 rows of headmatter
    # reported unread on one ord record. A run is claimed only once it has
    # said who it appeared for; anything after the last such phrase is left
    # alone, so a court that prints no roster loses nothing.
    counsel: list = []
    signer: tuple | None = None
    if not crit.get("attorneys"):
        floor2 = cap_band[1]
        if closer is not None:
            floor2 = max(floor2, closer.bottom)
        if foot is not None:
            floor2 = max(floor2, foot.top)
        _seen: set = set()
        _run = [l for l in live[j:]
                if l.id not in consumed and l.top > floor2 + 1]
        for _k, line in enumerate(_run):
            flat = _norm(line.plain)
            if _BYLINE_HEAD.match(flat):
                break
            # THE PAPER'S NAME IS NOT A ROSTER ROW. This walk now runs BEFORE
            # the title scan (nynd prints its title below the roster), and
            # for the far commoner order — box, title, body — the title
            # stands first in this run and would be swallowed as counsel.
            if _is_title_head(flat, facts) and not _is_status_row(flat, facts):
                break
            # …OR THE OFFICER SIGNS OVER HIS OFFICE, on two rows. nynd closes
            # its appearances block with 'DANIEL J. STEWART' over 'United
            # States Magistrate Judge' and then prints the paper's name below
            # that. Neither row could end the roster, so the roster was never
            # closed and the whole tail — roster, announcement AND title —
            # opened the writing as its first three paragraphs.
            _nxt = _run[_k + 1] if _k + 1 < len(_run) else None
            if _nxt is not None and _OFFICE_ROW.match(_norm(_nxt.plain)) \
                    and _is_name_row(flat, facts):
                signer = (line, _nxt)
                break
            # THE CAP COUNTS TYPED ROWS, NOT PIECES. A two-column roster is
            # split at its column gap, so nynd's nine typed rows arrive as
            # eighteen line objects and a 16-piece cap cut the roster in
            # half — before the byline that actually ends it.
            _seen.add(round(line.top))
            if len(_seen) > facts.counsel_max_rows:
                break
            counsel.append(line)
        # A ROSTER HAS SAID WHO IT APPEARED FOR when it states the party's own
        # status: nynd's pro se plaintiff appears as 'HELEN REBEKAH GARBER' /
        # 'Plaintiff, Pro Se' / 'Port Ewen, New York 12466', which names its
        # party as plainly as 'Attorneys for Plaintiff.' does and matches no
        # 'for'-phrase at all. Where neither is present the run is still
        # trimmed from the end, so a court printing no roster loses nothing.
        if not any(_is_status_row(_norm(l.plain), facts) for l in counsel):
            while counsel and not _APPEARANCE_END.search(
                    _norm(" ".join(l.plain for l in counsel))):
                counsel.pop()              # only what NAMED its party is kept
    if counsel:
        for line in counsel:
            emit(line, "counsel")
        crit["attorneys"] = _norm(" ".join(l.plain for l in counsel))[:4000]
    if signer is not None:
        for line in signer:
            emit(line, "author")
        if not crit.get("judges"):
            crit["judges"] = _norm(signer[0].plain).rstrip(".")

    if not title_parts:
        _floor = cap_band[1]
        if closer is not None:
            _floor = max(_floor, closer.bottom)
        if foot is not None:
            _floor = max(_floor, foot.top)
        # THE TITLE MAY STAND BELOW THE ROSTER. nynd prints APPEARANCES, the
        # roster, the officer's announcement and only THEN
        # 'REPORT-RECOMMENDATION and ORDER' — so this scan, run from the
        # box's foot, broke on 'APPEARANCES:' (bold, and no paper's name) and
        # the title was never read on any of the court's 24 records. Run
        # after the roster instead, from below whatever it claimed.
        if counsel:
            _floor = max(_floor, max(l.bottom for l in counsel))
        if signer is not None:
            _floor = max(_floor, signer[1].bottom)
        prev = None
        for line in live[j:]:
            if line.top <= _floor + 1:
                continue
            # A TYPED RULE IS NOT A TITLE, AND NOT A REASON TO STOP LOOKING.
            # wyd closes its box with a row of em dashes 0.03pt BELOW the
            # rail's own foot, so the floor left it standing: neither bold
            # nor centred, it broke the scan on its first candidate and the
            # paper's three-row name — 'ORDER AFFIRMING AND ADOPTING THE
            # MAGISTRATE JUDGE'S REPORT AND …' — opened the writing as three
            # paragraphs instead (the user, 2026-08-20: 'headmatter extends
            # to the title of the document'). The rule is the box talking;
            # it is recorded so the claim stays total, and stepped over.
            if _is_typed_rule(line.plain):
                if line.id not in consumed:
                    dropped.append(m.Dropped(
                        text=_norm(line.plain), prov=m.Prov(1, (line.id,)),
                        kind="rule"))
                    consumed.add(line.id)
                continue
            if not (line.all_bold or centred(line)
                    or _underlined(pm, line)):
                break
            flat = _norm(line.plain)
            if prev is None:
                if not (_is_title_head(flat, facts)
                        and not _is_status_row(flat, facts)):
                    break
            else:
                # THE PARAGRAPH BREAK ENDS THE TITLE. A wrapped title sits at
                # the paper's own line pitch under its first row (measured on
                # almd: 16.0pt on a 14pt page); the body opens a paragraph
                # below it (31.7pt). Bold alone runs straight on into a bold
                # opening sentence.
                if line.top - prev.bottom > (line.size or 12.0) * 0.75:
                    break
                if not _is_title_tail(flat, facts):
                    break
            _said = _title_text(flat, facts)
            emit(line, "title", _said if _letter_spaced(flat) else None)
            title_parts.append(_said)
            anchor_ids.append(line.id)
            prev = line


    # ---- what the block says -------------------------------------------
    if court_rows:
        crit["court"] = _norm(" ".join(court_rows))
    if title_parts:
        crit["title"] = _norm(" ".join(title_parts))
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(caption_rows, facts)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            one = _sides(caption_rows, facts, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one

    out = {"criteria": crit, "items": items, "attorneys": [],
           "dropped": dropped, "consumed": consumed,
           "anchor_ids": anchor_ids, "doc_type_final": None}
    # …AND THE ROW CREDITS THE WRITING, not just the block. Naming the judge
    # under the masthead is this paper's way of announcing who wrote the
    # order, so it is reported as `announced_author` — the contract core
    # already reads (pipeline.py :2050), which credits the lead writing ONLY
    # when no signature outranks it. Measured on cod: 22 of 22 records reach
    # the end of the pipeline with no author on the lead writing, and 18 of
    # them print this row. A court whose own byline grammar cannot parse its
    # announcement is unaffected — core drops the value.
    if bench:
        out["announced_author"] = _norm(bench[0].plain)
    return out
