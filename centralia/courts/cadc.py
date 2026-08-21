"""United States Court of Appeals for the District of Columbia Circuit ('cadc').

Everything unique to cadc lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'a rule on the page axis'. cadc divides its headmatter with
a short rule centred on the page's own axis (x0=288, x1=324 on a 612pt
page). It DRAWS that rule on its long papers and TYPES it on its short
order sheet, and which of the two it uses names the paper:

    fenced bands (73 of 100) — a 36.0pt filled rect, dead-centre, drawn
    BETWEEN sections (three of them on 57 records, four on 16). Two
    settings share the contract, and both are read the same way because
    the fence, not the setting, says where a section ends:

      the argued opinion (58)             the judgment / order (15)

        United States Court of Appeals      United States Court of Appeals
        FOR THE DISTRICT OF COLUMBIA …      FOR THE DISTRICT OF COLUMBIA …
        ──────  a DRAWN 36pt fence          ──────
        Argued Feb 5, 2026  Decided …       No. 24-5165   September Term, 2025
        No. 24-5199        the docket       FILED ON: JULY 28, 2026
        ADELE E. RUPPE,    the parties,     ACCURACY IN MEDIA, ET AL.,
              APPELLANT    centred                APPELLEES
        v.                                  v.
        MARCO RUBIO, …                      UNITED STATES DEPARTMENT OF …
              APPELLEE                            APPELLEES
        ──────                              ──────
        Appeal from the United States …     Appeal from the United States …
        for the District of Columbia        for the District of Columbia
        (No. 1:17-cv-02823)                 (No. 1:14-cv-01589)
        ──────                              ──────
        Kevin E. Byrnes argued the cause    Before: WALKER and CHILDS, …
        … the appearances, unlabelled       J U D G M E N T
        Before: WILKINS, RAO and PAN, …     This appeal was considered …
        Opinion for the Court filed by …
        RAO, Circuit Judge: …  the byline

    typed-rule order (26) — no drawn rule anywhere. The divider is TYPED,
    an underscore run on the same axis, and the court prints it once,
    INSIDE the docket row, between the docket and the term:

        United States Court of Appeals
        FOR THE DISTRICT OF COLUMBIA CIRCUIT
        No. 26-5034   ____________   September Term, 2025
                       1:25-cv-03581-UNA   the tribunal below, flush right
        Filed On: June 10, 2026
        Timothy R. Petrozzi,               the caption, at the LEFT rail
              Appellant
        v.
        Muriel Bowser, Mayor, et al.,
              Appellees
        ------------------------------     a wall between consolidated cases
        ON APPEAL FROM THE UNITED STATES DISTRICT COURT
        FOR THE DISTRICT OF COLUMBIA
        BEFORE: Pillard, Rao, and Childs, Circuit Judges
        J U D G M E N T                    the anchor of an unsigned writing

A record that draws neither divider is not this contract and gets NOTHING
(the NLRB's own two-column proposed judgment, which this court adopts and
dockets on the Board's paper, is the one such record in the corpus).

The reader claims HEADMATTER ONLY. It stops at the first byline, and where
the court signs nothing it stops ABOVE the title it would have signed —
'J U D G M E N T' is the only thing an unsigned judgment can anchor on, and
a title read is worth less than a writing kept.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop cadc used to sit in, so nothing about its bylines
# changes by being moved here.
CADC = register(CourtProfile(
    "cadc", "United States Court of Appeals for the D.C. Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_FENCED = "fenced bands"          # the divider is DRAWN, between sections
STYLE_TYPED_ORDER = "typed-rule order"  # the divider is TYPED, on the docket row

# ---- cadc's declared facts (measured over the corpus, not tuned) ---------
# THE DRAWN FENCE: a filled rect 36.0pt wide whose midpoint is the page
# axis. Measured over all 100 records: 229 rects and 3 curves at exactly
# x0=288.0 w=36.0, and 3 at w=34.0. A rule that spans the measure is an
# underline (the 90.8pt curve under 'J U D G M E N T', the 295pt rect under
# a sealed-copy stamp) or a footnote separator, and is not a fence.
_FENCE_WIDTH = (30.0, 45.0)
_FENCE_OFF_AXIS = 6.0
# THE TYPED DIVIDER: an underscore run on the same axis, 80.5pt wide
# (265.7-346.2). It arrives as one cell on 25 records and as two abutting
# cells on one (heritage_foundation), so it is recognised per CELL and the
# row it sits in is the docket row, not a row of its own.
_TYPED_OFF_AXIS = 16.0
_TYPED_RULE = re.compile(r"^[_]{4,}$")
# THE CONSOLIDATED-CASE WALL: a hyphen run the order sheet types at the
# LEFT RAIL between two captions ('------------------------------', 118pt
# at x0=72). Same glyph class, different axis, different meaning — so the
# axis it sits on decides how it renders.
_TYPED_WALL = re.compile(r"^[-–—]{4,}$")
# ONE PRINTED ROW: cadc sets the docket and the term, and 'Argued …' and
# 'Decided …', side by side at the same baseline. Two lines within this of
# each other are one row of the page and are read as one. Measured: the
# widest same-row split in the corpus is 1.7pt (patsy's docket beside its
# trial number).
_ROW_TOL = 2.0
# THE TRIBUNAL'S OWN NUMBER is set flush with the RIGHT EDGE OF THE DOCKET
# ROW, in the masthead's own right column ('1:25-cv-03581-UNA',
# 'FAA-24-ODRA-00969', 'SEC-2023-47', 'DOD-03/03/2026 Order'). Its FORM
# varies by agency and cannot be read by wording; where it sits does not.
# The reference is the docket row the court just printed, never the
# document's body measure — an order sheet whose body is a narrow-measure
# opinion further in measures a rail 84pt short of its own masthead.
# Measured: the term cell ends at x1=540.03 and the tribunal's number at
# 539.89-540.03 on all 26 order sheets.
_FLUSH_RIGHT_SLOP = 4.0
# How far the block may run. Measured over the corpus: 56 records finish on
# page 1, 37 on page 2, five on page 3 (patsy_widakuswara states three
# consolidated captions before its roster; fairholme prints a table of
# contents) and jane_doe_v._todd_blanche on page 4. The walk always ends on
# a landmark — the cap is a bound, not the thing that stops it.
_MAX_PAGES = 4

_DOCKET_ROW = re.compile(r"^(?:Case\s+)?Nos?\.\s*\d{2}-\d{2,5}", re.I)
_CONSOLIDATED = re.compile(r"^Consolidated with\b", re.I)
# '(No. 1:17-cv-02823)' — the trial number the origin band states under the
# court it names.
_PAREN_DOCKET = re.compile(r"^\(Nos?\.\s*[^)]+\)$", re.I)
_TERM_CELL = re.compile(r"^\w+\s+Term,\s*\d{4}\.?$", re.I)
# THE OPINION'S OWN TABLE OF CONTENTS, printed between the disposition row
# and the byline on a long consolidated record (fairholme, the one in the
# corpus). Read by its DOT LEADER — a typographic landmark that cannot
# occur in prose — never by what its entries say.
_DOT_LEADER = re.compile(r"\.{6,}")
# A district court's own number, as cadc prints it beside the appeal's:
# a chamber, a colon, the year, the case type, the number.
_TRIAL_TYPES = ("-cv-", "-cr-", "-mc-", "-md-", "-ms-", "-sc-", "-mj-")

# ORIGIN OPENERS — how cadc names the tribunal it is reviewing, in the
# roman form the opinion sets and the caps form the order sheet prints. A
# closed vocabulary of the court's own openers; a party NAME is never read
# by wording.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from", "on cross-appeal from",
    "petition for review", "petitions for review",
    "on petition for", "on petitions for",
    "on remand from", "on review of", "review of",
    "on application for", "on writ of", "on petition of",
    "on motion for", "on certified question",
)
# …and the REHEARING posture, which shares the origin band and is history,
# not a tribunal.
_REHEARING = ("on petition for rehearing", "on petitions for rehearing")
# THE DATE LABELS cadc prints, longest first so 'Argued and Submitted' wins
# over 'Argued'. 'Filed On' is the order sheet's; 'Argued'/'Decided' the
# opinion's.
_DATE_LABELS = ("argued and submitted", "argued en banc", "submitted on briefs",
                "reargued", "argued", "submitted", "decided", "reissued",
                "filed on", "filed", "amended", "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. cadc sets them in caps on the opinion and in title case on the
# order sheet, so the test is on the lowered word.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "amicus",
    "amici", "movant", "movants", "applicant", "applicants", "claimant",
    "claimants", "debtor", "debtors", "party-in-interest",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# THE COURT'S OWN PAPER NAMES, letter-spaced on the page ('J U D G M E N T')
# and squeezed back before they are recognised. A closed vocabulary of
# labels the court prints alone on a centred row.
_PAPER_TITLES = ("JUDGMENT", "ORDER", "OPINION", "PERCURIAM", "MANDATE",
                 "AMENDEDJUDGMENT", "AMENDEDORDER", "ORDERANDJUDGMENT",
                 "SUPPLEMENTALORDER")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    """'J U D G M E N T' -> 'JUDGMENT'. cadc letter-spaces the name of the
    paper; it is the same word."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("united states court of appeals",
                   "for the district of columbia circuit",
                   "united states court of appeals for the district of "
                   "columbia circuit")


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_rehearing(text: str) -> bool:
    return _norm(text).lower().startswith(_REHEARING)


# WHO WROTE WHAT — cadc announces it in a row of its own under the roster,
# and the row always OPENS with the court's own formula. It reads like a
# byline and names a judge like a roster, so without a test of its own it
# ends the reader one section early. Closed vocabulary of openers, because
# the tail varies ('… filed by Circuit Judge RAO.', '… filed PER CURIAM.',
# '… by Senior Circuit Judge ROGERS.', and a wrap onto the next row).
_DISPOSITION_OPENERS = (
    "opinion for the court", "opinion of the court", "opinion concurring",
    "opinion dissenting", "concurring opinion", "dissenting opinion",
    "separate opinion", "per curiam opinion", "statement of circuit judge",
)


def _is_disposition(text: str) -> bool:
    low = _norm(text).lower()
    return len(low) <= 140 and low.startswith(_DISPOSITION_OPENERS)


def _is_trial_docket(text: str) -> bool:
    """'1:25-cv-03581-UNA' — the court BELOW, not this appeal."""
    bare = _norm(text)
    if " " in bare or ":" not in bare:
        return False
    return any(kind in bare.lower() for kind in _TRIAL_TYPES)


def _labelled_dates(text: str) -> dict:
    """{'argued': 'February 5, 2026', 'decided': 'July 31, 2026'}.

    cadc sets one label per cell and up to two cells per row. A date row is
    SHORT — 'filed' inside prose is an ordinary English word."""
    if len(text) > 120:
        return {}
    low = text.lower()
    hits = []
    for label in _DATE_LABELS:
        at = low.find(label)
        if at < 0:
            continue
        if at and low[at - 1].isalnum():
            continue
        hits.append((at, label))
    if not hits:
        return {}
    hits.sort(key=lambda p: (p[0], -len(p[1])))
    picked: list = []
    for at, label in hits:
        if picked and at < picked[-1][0] + len(picked[-1][1]):
            continue
        picked.append((at, label))
    out: dict = {}
    for i, (at, label) in enumerate(picked):
        end = picked[i + 1][0] if i + 1 < len(picked) else len(text)
        seg = text[at + len(label):end]
        # A DATE VALUE IS READ IN THE FORM THE PAGE SET IT — the comma in
        # 'July 31, 2026' is part of the date, so the value is a SLICE of
        # the row, never a re-join of its tokens.
        mm = re.search(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
                       r"|[A-Z]{3,9}\s+\d{1,2},?\s+\d{4}"
                       r"|\d{1,2}\s+[A-Z][a-z]+\.?\s+\d{4})", seg)
        if mm is None:
            continue
        first = mm.group(1).split()[0].strip(".,").lower()
        if first not in _MONTHS and not first.isdigit():
            continue
        out[label.replace(" ", "_")] = _norm(mm.group(1))
    return out


def _is_date_row(text: str) -> bool:
    flat = _norm(text)
    if len(flat) > 120:
        return False
    low = flat.lower()
    return bool(_labelled_dates(flat)) and any(
        low.startswith(lab) for lab in _DATE_LABELS)


def _is_roster(text: str) -> bool:
    low = _norm(text).lower()
    return low.rstrip(":") == "before" or low.startswith(("before:", "before "))


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test. The
    designation clause a visiting judge carries names nobody, so the roster
    ends where it begins."""
    flat = _norm(text)
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    body = flat
    for opener in ("before:", "before"):
        if body.lower().startswith(opener):
            body = body[len(opener):]
            break
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*: ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not
            # another judge.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        first = flat.split()[0].rstrip(".").lower() if flat.split() else ""
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. ").lower()
        words = [w.strip(",.;–-/ ")
                 for w in bare.replace("–", " ").replace("-", " ")
                             .replace("/", " ").split()]
        # A STATUS row is a role label, not a party ('APPELLANTS',
        # 'Petitioner/Cross-Respondent'). Closed vocabulary. 'et al.' is
        # NOT in it: cadc wraps 'United States Department of Education, et'
        # onto a row of its own reading 'al.,', and dropping that row
        # renamed the appellee.
        if words and all(
                w in _STATUS_WORDS or w in ("and", "supporting", "the", "-",
                                            "third", "party", "pro", "se",
                                            "cross", "in", "interest", "of")
                or not w for w in words):
            continue
        if flat.lower().startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    # THE COMMA is the caption's own apparatus — it leads to the status row
    # below. The FULL STOP is not: it ends the abbreviation the party is
    # incorporated under ('CITIBANK, N.A.'), and stripping it renames the
    # party.
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the divider — cadc's dispatch
# --------------------------------------------------------------------------

def _fences(model) -> dict:
    """Where each page drew its section fences: {page: [tops]}.

    cadc's fence is a short rule centred on the page axis, drawn BETWEEN two
    headmatter rows. A rule that spans the measure is an underline or a
    footnote separator and is not a fence."""
    out: dict = {}
    for pm in model.pages:
        tops = [r.top for r in pm.h_rules
                if _FENCE_WIDTH[0] <= r.width <= _FENCE_WIDTH[1]
                and abs((r.x0 + r.x1) / 2 - pm.width / 2) <= _FENCE_OFF_AXIS]
        if tops:
            out[pm.number] = sorted(tops)
    return out


def _typed_divider(pm):
    """The order sheet's TYPED divider on ``pm`` — an underscore run on the
    page axis — or None."""
    for line in pm.lines:
        if not _TYPED_RULE.match(_norm(line.plain)):
            continue
        if abs((line.x0 + line.x1) / 2 - pm.width / 2) <= _TYPED_OFF_AXIS:
            return line
    return None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

_MAST, _CASE, _ORIGIN, _COUNSEL, _PANEL, _CONTENTS = 0, 1, 2, 3, 4, 5


@decider("headmatter.read", court="cadc")
def read_headmatter_cadc(model, geom, **_):
    """Read cadc's axis-divided headmatter, or NOTHING.

    NOTHING is returned for anything that is not one of the two contracts
    above: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    fences = _fences(model)
    if fences.get(1):
        # THE MASTHEAD IS THE BAND ABOVE THE FIRST FENCE. Verified over the
        # corpus: on 72 of the 73 fenced records nothing but the two banner
        # rows stands there, and on the 73rd it is the sealed-copy stamp
        # this court prints over a redacted opinion — masthead either way.
        style = STYLE_FENCED
        mast_bottom = fences[1][0]
    else:
        typed = _typed_divider(page1)
        if typed is None:
            return NOTHING              # neither divider: not cadc's paper
        style = STYLE_TYPED_ORDER
        mast_bottom = typed.top - 1.0

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    wrap_max = 1.8 * (geom.lead if geom and geom.lead else 14.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CADC.byline)
    pages = {pm.number: pm for pm in model.pages}

    # ---- the page's own rows, furniture stepped over --------------------
    # THE MASTHEAD IS NOT FURNITURE ON PAGE 1. The order sheet reprints its
    # banner and its docket row at the head of every continuation page, so
    # the repetition sweep reads page 1's own 'FOR THE DISTRICT OF COLUMBIA
    # CIRCUIT' as a running head and deletes the court's name from the one
    # place it is the masthead. Above the first divider, page 1 keeps what
    # it prints.
    kept: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line) and not (
                    pm.number == 1 and line.top <= mast_bottom):
                continue
            kept.append(line)
    if not kept:
        return NOTHING
    kept.sort(key=lambda l: (l.page, l.top, l.x0))

    rows: list = []                     # [page, top, [cells left-to-right]]
    for line in kept:
        if rows and rows[-1][0] == line.page \
                and abs(line.top - rows[-1][1]) <= _ROW_TOL:
            rows[-1][2].append(line)
        else:
            rows.append([line.page, line.top, [line]])
    if not any(_is_banner(_norm(c.plain)) for _p, _t, cs in rows[:4]
               for c in cs):
        return NOTHING                  # cadc always names itself first

    def band_of(page: int, top: float) -> tuple:
        return (page, sum(1 for t in fences.get(page, ()) if t < top))

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list[int] = []
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    history_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    disposition_rows: list[str] = []
    lower_dockets: list[str] = []
    dockets: list[str] = []
    dates: dict = {}

    def emit(cells: list, role: str) -> None:
        parts = sorted(cells, key=lambda c: c.x0)
        pm = pages[parts[0].page]
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        align = line_alignment(first, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        rel = 0.0
        if align == "L" and first.x0 > body_x0 + 12:
            rel = min(first.x0 - body_x0, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        consumed.update(p.id for p in parts)

    def cell_text(cells: list) -> str:
        return _norm("  ".join(_norm(c.plain)
                               for c in sorted(cells, key=lambda c: c.x0)))

    def opens_landmark(text: str) -> bool:
        return bool(_is_banner(text) or _squeeze(text) in _PAPER_TITLES
                    or _is_roster(text) or _is_disposition(text)
                    or _DOCKET_ROW.match(text) or _CONSOLIDATED.match(text)
                    or _is_date_row(text) or _origin_opener(text)
                    or _PAREN_DOCKET.match(text))

    def wraps(a: list, b: list) -> bool:
        """Is row ``b`` the continuation of row ``a``, or the next element?

        A WRAP IS MEASURABLE. cadc sets its headmatter on a 14pt leading and
        stands the next element off at twice that: every roster and
        disposition wrap in the corpus falls at 13.8-14.2pt and every fresh
        element at 27.6pt or more. A continuation also keeps the type size —
        the sealed-opinion placeholder ('OPINION UNDER SEAL', 28pt against
        the 12pt body) stands where a roster wrap would and is not one.
        """
        ta, sa = a[1], (a[2][0].size or 0.0)
        tb, sb = b[1], (b[2][0].size or 0.0)
        return (b[0] == a[0] and 0 < tb - ta <= wrap_max
                and abs(sb - sa) <= 0.6)

    def run_on(j: int) -> int:
        """How many rows this statement WRAPS onto. cadc ends each of its
        tail statements on a full stop and starts the next on its own row;
        an unterminated row is not licence to swallow the next SECTION, so
        a row that OPENS a landmark of its own ends the wrap whatever the
        row above it ended on."""
        k = j
        while (k + 1 < len(rows)
               and not cell_text(rows[k][2]).rstrip().endswith(
                   (".", ":", "!", "?"))
               and band_of(*rows[k + 1][:2]) == band_of(*rows[k][:2])
               and wraps(rows[k], rows[k + 1])
               and not opens_landmark(cell_text(rows[k + 1][2]))):
            k += 1
        return k

    def claimable_title(at: int) -> bool:
        """Is the label row at ``rows[at]`` the headmatter's, or the
        writing's anchor?

        cadc prints 'J U D G M E N T' over a judgment nobody signs and
        'O R D E R' over an order nobody signs. Where the writing under the
        label opens on a byline the label is headmatter; where it does not,
        the label is the only thing that writing can anchor on, and claiming
        it costs the document its writing."""
        for k in range(at + 1, len(rows)):
            return parser.parse(cell_text(rows[k][2])) is not None
        return False

    zone = _MAST
    mast_right = None                   # the docket row's own right edge
    origin_band = None
    last_band = None
    seen_caption = False
    i = 0
    while i < len(rows):
        page, top, cells = rows[i]
        band = band_of(page, top)
        # THE FENCE ITSELF RENDERS. A reader that claims the region inherits
        # the court's own section marks, and core only draws them for rows
        # the reader left behind. It carries the provenance of the row above
        # it so the merge-by-position keeps it where the page drew it.
        if last_band is not None and band != last_band:
            if band[0] == last_band[0] and items:
                items.append(m.Rule(prov=items[-1].prov, span="center"))
            # THE BAND UNDER THE ORIGIN IS THE APPEARANCES. cadc announces
            # nothing about them — an entry opens on the advocate's name
            # ('Kevin E. Byrnes argued the cause…') — so the band is
            # delimited rather than recognised: after the origin, before the
            # roster, and nothing else is ever there.
            if zone == _ORIGIN:
                zone = _COUNSEL
        last_band = band

        # THE TYPED DIVIDER AND THE CONSOLIDATION WALL are rules, not text:
        # they are pulled out of the row they were typed in and rendered
        # where the page typed them.
        rule_ids = {id(c) for c in cells
                    if _TYPED_RULE.match(_norm(c.plain))
                    or _TYPED_WALL.match(_norm(c.plain))}
        if rule_ids:
            rule_cells = [c for c in cells if id(c) in rule_ids]
            cells = [c for c in cells if id(c) not in rule_ids]
            mid = sum((c.x0 + c.x1) / 2 for c in rule_cells) / len(rule_cells)
            span = "center" \
                if abs(mid - pages[page].width / 2) <= _TYPED_OFF_AXIS \
                else "left"
            items.append(m.Rule(
                prov=m.Prov(page, tuple(c.id for c in rule_cells)),
                typed=True, span=span))
            consumed.update(c.id for c in rule_cells)
            if not cells:
                i += 1
                continue

        text = cell_text(cells)
        sq = _squeeze(text)

        # ---- the masthead: what page 1 prints above the divider ---------
        if page == 1 and top <= mast_bottom:
            if _is_banner(text):
                banner_rows.append(text)
            emit(cells, "court")
            i += 1
            continue

        # ---- the landmarks, in the order the court prints them ----------
        if _is_banner(text):
            emit(cells, "court")
            i += 1
            continue
        if sq in _PAPER_TITLES:
            if not claimable_title(i):
                break
            crit.setdefault("title", sq)
            emit(cells, "title")
            anchor_ids.append(cells[0].id)
            i += 1
            continue
        if _is_roster(text):
            end = run_on(i)
            for j in range(i, end + 1):
                panel_rows.append(cell_text(rows[j][2]))
                emit(rows[j][2], "panel")
            zone = _PANEL
            i = end + 1
            continue
        if _is_disposition(text):
            end = run_on(i)
            for j in range(i, end + 1):
                disposition_rows.append(cell_text(rows[j][2]))
                emit(rows[j][2], "summary")
            zone = _PANEL
            i = end + 1
            continue
        if _DOCKET_ROW.match(text) and zone < _COUNSEL:
            # THE DOCKET ROW carries the appeal's number, the court's term
            # and — on the order sheet's consolidated pages — the trial
            # number beside it. Each cell is what it is.
            mast_right = max(c.x1 for c in cells)
            for c in sorted(cells, key=lambda c: c.x0):
                one = _norm(c.plain)
                if _TERM_CELL.match(one):
                    continue
                if _is_trial_docket(one):
                    lower_dockets.append(one)
                elif _DOCKET_ROW.match(one):
                    dockets.append(one.rstrip("."))
            emit(cells, "docket")
            zone = _CASE
            i += 1
            continue
        if _CONSOLIDATED.match(text) and zone < _COUNSEL:
            # THE CONSOLIDATED ROLL WRAPS. advanced_energy states twenty
            # numbers over four rows; read row by row, the last three fell
            # through to the caption and joined the case name.
            end = run_on(i)
            for j in range(i, end + 1):
                one = cell_text(rows[j][2])
                for num in re.findall(r"\b\d{2}-\d{3,5}\b", one):
                    dockets.append(num)
                emit(rows[j][2], "docket")
            zone = max(zone, _CASE)
            i = end + 1
            continue
        if _is_date_row(text) and zone <= _CASE:
            dates.update(_labelled_dates(text))
            emit(cells, "date")
            zone = max(zone, _CASE)
            i += 1
            continue
        if _PAREN_DOCKET.match(text):
            lower_dockets.append(text.strip("()"))
            emit(cells, "lower-court")
            i += 1
            continue
        # THE TRIBUNAL'S OWN NUMBER, read by WHERE IT SITS: one cell, flush
        # to the right margin, printed above the caption. Its form is the
        # agency's ('FAA-24-ODRA-00969', 'SEC-2023-47', 'DOD-03/03/2026
        # Order') and no vocabulary covers it.
        if (not seen_caption and zone <= _CASE and len(cells) == 1
                and mast_right is not None
                and abs(cells[0].x1 - mast_right) <= _FLUSH_RIGHT_SLOP
                and len(text) <= 40):
            lower_dockets.append(text)
            emit(cells, "lower-court")
            i += 1
            continue
        # THE TABLE OF CONTENTS opens on a dot leader and runs to the
        # byline. It is the opinion's front matter, printed inside the span
        # this reader claims, and leaving it behind published it as a
        # writing of its own ('I. Background ……… 5' chipped as an order).
        if zone >= _PANEL and _DOT_LEADER.search(text):
            emit(cells, "contents")
            zone = _CONTENTS
            i += 1
            continue
        if _is_rehearing(text) and zone <= _ORIGIN:
            end = run_on(i)
            history_rows.append(_norm(" ".join(
                cell_text(rows[j][2]) for j in range(i, end + 1))))
            for j in range(i, end + 1):
                emit(rows[j][2], "lower-court")
            zone = _ORIGIN
            origin_band = band
            i = end + 1
            continue
        if _origin_opener(text) and zone <= _ORIGIN:
            emit(cells, "lower-court")
            origin_rows.append(text)
            zone = _ORIGIN
            origin_band = band
            i += 1
            continue

        # ---- a row that names nothing belongs to the open section -------
        if parser.parse(text) is not None:
            break                       # THE FIRST BYLINE ENDS THE READER
        if zone == _ORIGIN and band == origin_band:
            origin_rows.append(text)
            emit(cells, "lower-court")
        elif zone == _CASE:
            seen_caption = True
            caption_rows.append(text)
            emit(cells, "caption")
        elif zone == _COUNSEL:
            counsel_rows.append(text)
            emit(cells, "counsel")
        elif zone == _CONTENTS:
            emit(cells, "contents")
        else:
            break                       # a row this contract does not name
        i += 1

    if not caption_rows and not dockets:
        return NOTHING

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(caption_rows)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            # A MANDAMUS PETITION HAS ONE SIDE ('IN RE: DONALD J. TRUMP, ET
            # AL., / PETITIONERS'). One party is still the parties.
            one = _sides(caption_rows, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit.setdefault("other_dockets", []).extend(dockets[1:])
    if lower_dockets:
        crit.setdefault("other_dockets", []).extend(lower_dockets)
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    if history_rows:
        crit["history"] = _norm(" ".join(history_rows))
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if disposition_rows:
        crit["disposition"] = _norm(" ".join(disposition_rows))
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    for label, value in dates.items():
        if label in ("decided", "filed_on", "filed", "amended", "entered",
                     "reissued"):
            crit.setdefault("decision_date", value)
        elif label in ("submitted", "submitted_on_briefs",
                       "argued_and_submitted"):
            crit.setdefault("submitted", value)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}
