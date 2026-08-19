"""United States Court of Appeals for the Federal Circuit ('cafc').

Everything unique to cafc lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'typed fence bands'. cafc prints ONE cover, and it types a
short rule between every section of it. The rule is the zone boundary, so
the BAND is the unit of meaning and no row has to be guessed at:

    Case: 25-1811  Document: 19  Page: 1  Filed: …   the ECF stamp (furniture)
    NOTE:  This order is nonprecedential.            the notice (a Drop)
    United States Court of Appeals                   the banner, 25pt
    for the Federal Circuit
    ______________________                  a TYPED rule, 132pt, x0=240
    ELIZABETH G. BRADLEY, DENNY W. BRANHAM,          the caption: parties…
          Plaintiffs
    v.                                               …the pivot
    UNITED STATES,
          Defendant-Appellant                        …and their status
    ______________________
    2025-1811                                        the docket, printed BARE
    ______________________
    Appeal from the United States Court of Federal   the origin
    Claims in No. 1:19-cv-00400-DAT, Judge David A. Tapp.
    ______________________
    ON MOTION                                        the paper's own name
    ______________________
    Before PROST, Circuit Judge.                     the roster
    O R D E R                                        the WRITING's heading
    Upon consideration of the United States's …

and on a merits opinion the same cover states its date and its appearances:

    ______________________
    Decided:  May 19, 2026                           the date
    ______________________
    JOSEPH DIEDRICH, Husch Blackwell LLP, …          the appearances
    ______________________
    Before CHEN, CUNNINGHAM, and STARK, Circuit Judges.
    CHEN, Circuit Judge.  A.L.M. Holding Company …   the first byline

TWO MEASUREMENTS DO ALL OF THE WORK.

  1. THE FENCE. 507 of them across the corpus, every one 132.0pt wide with
     x0 at 240 (239 where the court re-set the page), centered on the 612pt
     axis, typed as underscores. 99 of the 100 records open one directly
     under the banner and carry between 4 and 9 in all; the hundredth is a
     scanned cover with no text on it at all, and it gets NOTHING. The
     count is taken over the WHOLE cover, not over page 1 — a caption
     naming forty Chinese exporters fills page 1 by itself and states its
     docket, its origin and its dates on page 2.

  2. WHETHER THE COURT CLOSED THE BAND. A band fenced above AND below is
     the court's own front matter, whatever it says. The band under the LAST
     fence is open, and that is where the writing begins. This settles the
     court's own labels outright: over the corpus 'ON MOTION' (14),
     'JUDGMENT' (4), 'ON PETITION' (3), 'ON PETITION AND MOTION' (1),
     'ON PETITION FOR REHEARING EN BANC' (1) and 'ERRATA' (1) are ALWAYS
     fence-closed and are headmatter; 'O R D E R' (16) is NEVER fence-closed
     and is always the heading of the order it opens. Nothing is decided by
     which word is printed — the same word, fenced, would be read as the
     paper's name and, unfenced, left standing for the writing.

cafc reviews the district courts, the Court of Federal Claims, the Court of
International Trade, the ITC, the PTAB, the MSPB and the Veterans Court, so
its origin statement takes many forms; they are all one band between two
fences, and the band is read whole.

The appearances name the lead counsel and then the firm block for the party,
and cafc sets EVERY ATTORNEY'S NAME IN SMALL CAPS — a 9.5pt run inside a
12pt row, uppercase throughout. That is a typeface fact, not a wording test,
and it is what tells an appearance from the prose of an order where the
court left the roster unfenced.

The reader claims HEADMATTER ONLY. It stops at the first byline, and where
the paper carries no byline it stops at the writing's own heading; a second
25pt banner deeper in the document opens a separate writing's cover
(cafc reprints the whole cover above an en banc concurrence) and is never
reached, because a writing is never read into.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import learn_vocabulary, line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import FOOTNOTE_LABEL_CHARS, line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop cafc used to sit in, so nothing about its bylines
# changes by being moved here.
CAFC = register(CourtProfile(
    "cafc", "United States Court of Appeals for the Federal Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_TYPED_FENCE = "typed fence bands"

# ---- cafc's declared facts (measured over the corpus, not tuned) ---------
# THE FENCE: '______________________' — 22 underscores, 132.0pt wide, x0=240
# on a 612pt page (239 on the pages the court re-set), centered on the axis.
# Measured on all 507 fences in the corpus; no other width occurs.
_FENCE_WIDTH = (120.0, 145.0)
_FENCE_OFF_AXIS = 25.0
_FENCE_GLYPHS = "_"
# THE BANNER is set at 25pt against a 12pt body — the largest type on the
# page by a factor of two. A SECOND banner is a separate writing's own cover
# (range_of_motion reprints it above the concurrence on page 4 and above the
# dissent on page 13); the reader never reaches into a writing, so the rows
# stop at the second banner.
_BANNER_OVER_BODY = 6.0
# THE RUNNING HEAD's band: 'BRADLEY v. US' opposite '2', set at 11pt with its
# baseline at top 74-76 while the body never opens above 119. Core recognizes
# a head by REPETITION, which needs pages to repeat on — 26 of the 100
# records run to one or two pages, and there the reader must know its own
# court's stationery.
_HEAD_BAND_MAX = 100.0
# How far the cover may run. The appearances wrap the page on 12 records,
# and on a trade case naming thirty exporters and their counsel the caption
# fills page 1 by itself and the roster lands on page 4 (linyi). Five pages
# is one more than the longest cover in the corpus; a second cover inside
# the window is cut at its own banner, and the walk ends at the byline
# either way.
_MAX_PAGES = 5
# A WRAP IS ONE LEADING BELOW ITS OWN FIRST ROW. cafc sets its body on a
# 14pt leading and puts a fresh statement a full paragraph (21pt) below the
# one above it, so 1.35 leadings separates a continuation from a new
# statement everywhere on the cover.
_WRAP_LEAD = 1.35
# SMALL CAPS: cafc sets every attorney's name — and every judge's — in small
# caps, which arrive as a 9.5pt run inside a 12pt row, uppercase throughout.
# It is a TYPEFACE choice, and it is the mark of an appearance.
_SMALLCAP_MIN_GLYPHS = 2

# The docket, printed BARE and centered under the caption: '2025-1317',
# '2024-1509, 2024-1709', '2026-1904, 26-1905' (the court drops the century
# on the second number of a consolidation), and 'Appeal No. 2025-1081' on an
# errata sheet.
_DOCKET_BARE = re.compile(
    r"^(?:Appeal\s+Nos?\.\s*)?\d{2,4}-\d{2,5}"
    r"(?:\s*[,;/]\s*(?:\d{2,4}-)?\d{2,5})*\.?$", re.I)
# A TYPED RULE that is not the fence: the dashed row a consolidated caption
# sets between the two appeals it joins.
_TYPED_DASHES = re.compile(r"^[-–—]{6,}$")
# THE COURT'S OWN SECTION LABELS. A closed vocabulary of labels cafc prints
# alone on a centred row — never a test on anything it says about a case.
# Read through _squeeze, because the court letter-spaces 'O R D E R'.
_LABEL_TITLE = (
    "ON MOTION", "ON MOTIONS", "ON PETITION", "ON PETITION AND MOTION",
    "ON PETITION AND MOTIONS", "ON MOTION AND PETITION",
    "ON PETITION FOR REHEARING EN BANC", "ON PETITIONS FOR REHEARING EN BANC",
    "ON PETITION FOR PANEL REHEARING", "ON REHEARING", "ON REMAND",
    "JUDGMENT", "ERRATA", "ORDER", "OPINION", "AMENDED OPINION",
    "CORRECTED OPINION", "NOTICE", "ON MOTION TO DISMISS",
)
# ORIGIN OPENERS — how cafc names the tribunal it is reviewing. The forum
# itself is never read by wording; only the opener is, and it is the court's
# own closed set.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "petition for review", "petitions for review",
    "on petition for review", "on petitions for review",
    "on petition for writ", "on petitions for writ",
    "on petition for a writ", "petition for writ", "petition for a writ",
    "on remand from", "review of", "on review of", "appeal of", "appeals of",
    "on application for", "application for",
)
# THE DATE LABELS cafc prints. It states one — 'Decided:' — but the family
# is kept whole so a variant band still reads as the date band.
_DATE_LABELS = ("decided and filed", "argued and submitted", "reargued",
                "argued", "submitted", "decided", "amended", "filed",
                "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_BARE_DATE_ROW = re.compile(
    r"^[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}\.?$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "party-in-interest",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# THE PUBLICATION NOTICE cafc stamps above its banner. Two forms, one
# meaning; it is a notice, so it is recorded as a Drop and its meaning is
# kept as criteria.
_NOTE_PREFIX = "note:"
_NONPRECEDENTIAL = "nonprecedential"
# The paper's own flag where the court prints it in the date band
# ('Nonprecedential Opinion' on an errata sheet).
_FLAG_ROW = re.compile(r"^(?:Non-?precedential|Precedential)\s+"
                       r"(?:Opinion|Order|Disposition)\.?$", re.I)
# THE LOWER TRIBUNAL'S OWN NUMBER, as cafc's origin band prints it:
# 'in No. 1:24-cv-00363-JPM', 'in Nos. IPR2021-01266, IPR2021-01239',
# 'in Investigation No. 337-TA-1276'.
_LOWER_DOCKET = re.compile(
    r"\bin\s+(?:Investigation|Interference|Reexamination|Appeal|Case|"
    r"Application|Inquiry)?\s*Nos?\.\s*(.+?)"
    r"(?=,\s*(?:Chief\s+|Senior\s+|Acting\s+|Presiding\s+|Magistrate\s+|"
    r"District\s+|Circuit\s+|Administrative\s+)*Judges?\b|\.\s*$|$)",
    re.I | re.S)
# THE TRIAL JUDGE, named the way cafc names one: title FIRST, then the name,
# and several of them where a panel below decided it ('Chief Judge Michael
# P. Allen, Judge Margaret C. Bartley, Judge Scott Laurer.'). The bench words
# are a closed vocabulary.
_LOWER_JUDGE = re.compile(
    r"(?:^|[,;]\s*)((?:Chief\s+|Senior\s+|Acting\s+|Presiding\s+|"
    r"Magistrate\s+|District\s+|Circuit\s+|Administrative\s+"
    r"(?:Patent\s+)?)*Judges?\s+[A-Z].*)$", re.S)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    """'O R D E R' -> 'ORDER'. cafc letter-spaces the heading of every order
    it issues; it is the same label."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _join(texts: list, vocab: set | None = None) -> str:
    """Join the rows of one band the way the page reads.

    cafc justifies its measure and breaks on a hyphen at the row end, and
    the hyphen is sometimes the word's ('Bart-' 'ley') and sometimes the
    token's ('1:20-cv-00110-' 'JPB'). Which one it is cannot be seen in the
    row, so the DOCUMENT'S OWN VOCABULARY decides — the same discriminator
    core uses to join a wrapped paragraph, so the criteria and the rendered
    body can never disagree about a broken word. Unproved, the hyphen stays
    and the wrap is welded ('non-' + 'compete' -> 'non-compete')."""
    out = ""
    for piece in texts:
        piece = _norm(piece)
        if not piece:
            continue
        if not out:
            out = piece
            continue
        if out.endswith(("-", "–", "—")):
            if vocab:
                word = []
                for ch in reversed(out[:-1]):
                    if ch.isalpha() or ch in "\u2019'":
                        word.append(ch)
                    else:
                        break
                head = piece.split()[0].strip(
                    "\u201c\u201d\"'\u2019\u2018()[]{}.,;:!?")
                if word and ("".join(reversed(word)) + head).lower() in vocab:
                    out = out[:-1] + piece
                    continue
            out += piece
        else:
            out += " " + piece
    return out


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("united states court of appeals",
                   "for the federal circuit",
                   "united states court of appeals for the federal circuit")


def _is_note(text: str) -> bool:
    """'NOTE:  This disposition is nonprecedential.' — the court's own
    publication notice, stamped above the banner."""
    low = _norm(text).lower()
    return low.startswith(_NOTE_PREFIX) and _NONPRECEDENTIAL in low


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _small_caps(line) -> bool:
    """Does this row set a name in SMALL CAPS?

    cafc sets every attorney's and every judge's name in small caps, which
    arrive as a run at 9.5pt inside a 12pt row, uppercase throughout. It is
    the mark of an appearance, and it is a TYPEFACE fact — never a test on
    what the row says. (The old engine measured the same thing to stop the
    size step from cutting a counsel entry in half mid-word.)"""
    chars = [c for c in (line.chars or ()) if (c.get("text") or "").strip()]
    if not chars:
        return False
    sizes = {round(c.get("size", 0), 1) for c in chars}
    if len(sizes) < 2:
        return False
    full = max(sizes)
    small = [c.get("text", "") for c in chars
             if round(c.get("size", 0), 1) < full]
    letters = [t for t in small if t.isalpha()]
    if len(letters) < _SMALLCAP_MIN_GLYPHS:
        return False
    return all(t.isupper() for t in letters)


def _labelled_dates(text: str) -> dict:
    """{'decided': 'May 19, 2026'}. A date row is SHORT — 'filed' inside
    prose is an ordinary English word."""
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
        # 'May 19, 2026' is part of the date, so the value is a SLICE of the
        # row, never a re-join of its tokens.
        mm = re.search(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
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
    if bool(_labelled_dates(flat)) and any(low.startswith(lab)
                                           for lab in _DATE_LABELS):
        return True
    # A BARE DATE IS STILL THE DATE BAND: an errata sheet states the day it
    # was issued with no label at all.
    return bool(_BARE_DATE_ROW.match(flat)
                and flat.split()[0].lower().rstrip(".") in _MONTHS)


def _bare(text: str) -> str:
    """A roster fragment stripped of its apparatus — trailing stops, colons
    and the footnote mark cafc rides on a visiting judge's title."""
    flat = _norm(text)
    while flat and (flat[-1] in ".*: " or flat[-1] in FOOTNOTE_LABEL_CHARS):
        flat = flat[:-1]
    return flat.strip()


def _bare_words(text: str) -> list:
    return [w.strip(".,;:*†‡\u00a7'\u2019\"()0123456789").lower()
            for w in text.split()]


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    The designation clause a visiting judge carries ('… sitting by
    designation.') names nobody, so the roster ends where it begins."""
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
        piece = _bare(chunk)
        if not piece:
            continue
        # A BENCH WORD ANYWHERE IN THE FRAGMENT MAKES IT A TITLE, and the
        # fragment has to be stripped of its apparatus before the word can
        # be seen: cafc footnotes the visiting judge on the roster's last
        # fragment ('Circuit Judges.1', 'District Judge.†'), and a raw
        # comparison read those as two more judges.
        if any(w in _TITLE_WORDS for w in _bare_words(piece)):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = _bare(part)
            if name.lower().startswith("and "):
                name = _bare(name[4:])
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not another
            # judge.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _split_origin(text: str):
    """(lower docket, trial judge) out of cafc's origin band.

    'Appeal from the United States Court of Federal Claims in No.
    1:19-cv-00400-DAT, Judge David A. Tapp.' — the tribunal's own number
    follows 'in No(s).' and the judge is the clause that OPENS on a bench
    word, because cafc puts the title first."""
    flat = _norm(text).rstrip()
    judge = None
    jm = _LOWER_JUDGE.search(flat)
    if jm:
        judge = _norm(jm.group(1)).rstrip(".")
    docket = None
    dm = _LOWER_DOCKET.search(flat)
    if dm:
        docket = _norm(dm.group(1)).rstrip(".,")
    return docket, judge


def _is_fence(line, page_width: float) -> bool:
    """The court's typed section rule: a run of underscores 132pt wide,
    centered on the page axis. Width is the fact — a longer typed run is a
    consolidated caption's own divider or a signature line."""
    text = line.plain.strip()
    if len(text) < 6 or any(c not in _FENCE_GLYPHS for c in text):
        return False
    width = line.x1 - line.x0
    if not (_FENCE_WIDTH[0] <= width <= _FENCE_WIDTH[1]):
        return False
    return abs((line.x0 + line.x1) / 2 - page_width / 2) <= _FENCE_OFF_AXIS


# --------------------------------------------------------------------------
# a VISUAL ROW is what the page printed on one line
# --------------------------------------------------------------------------
# cafc justifies its measure, and pdfio breaks a justified line at a wide
# inter-word gap ('defendants-appellees.' | 'Also represented by RAYMOND'
# arrive as two runs of one printed row). Read as separate rows they render
# as a phantom indent halfway across the page and split an appearance
# mid-sentence. Pieces that share a baseline are ONE row.
_ROW_BAND = 2.0


def _visual_rows(lines: list) -> list:
    """``lines`` (page order) grouped into printed rows."""
    out: list = []
    for line in lines:
        if out and out[-1][0].page == line.page \
                and abs(out[-1][0].top - line.top) <= _ROW_BAND:
            out[-1].append(line)
        else:
            out.append([line])
    for row in out:
        row.sort(key=lambda l: l.x0)
    return out


def _plain(row: list) -> str:
    text = ""
    for line in row:
        piece = _norm(line.plain)
        if not piece:
            continue
        text = (text + "  " + piece) if text else piece
    return text


def _markup(row: list) -> str:
    text = ""
    for line in row:
        piece = line_markup(line)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    return text


@decider("headmatter.read", court="cafc")
def read_headmatter_cafc(model, geom, **_):
    """Read cafc's typed-fence-band headmatter, or NOTHING.

    NOTHING is returned for anything that is not the contract above: core's
    shared walk places those rows unidentified, which is a smaller error than
    a confident misreading."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 144.0
    body_size = geom.body_size if geom else 12.0
    lead = (geom.lead if geom and geom.lead else 14.0)
    vocab = learn_vocabulary(model)
    banner_min = body_size + _BANNER_OVER_BODY
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CAFC.byline)
    pages = {pm.number: pm for pm in model.pages}

    lines: list = []
    head_lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: cafc's CM/ECF
            # overlay ('Case: 25-1811  Document: 19  Page: 1  Filed: …') and
            # the running head. Core measures and records what it can; the
            # reader steps over those and records the rest itself.
            if finder.kind(pm, line):
                continue
            if pm.number > 1 and line.top < _HEAD_BAND_MAX:
                head_lines.append(line)
                continue
            lines.append(line)
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    if not lines:
        return NOTHING                    # a scanned cover carries no text
    rows = _visual_rows(lines)
    if not any(_is_banner(_plain(r)) for r in rows[:6]):
        return NOTHING                    # cafc always names itself first

    # A SECOND BANNER OPENS A SEPARATE WRITING'S COVER. cafc reprints the
    # whole cover above an en banc concurrence and again above the dissent;
    # those pages are inside writings and the reader never reaches into one.
    seen_banner = False
    for i, row in enumerate(rows):
        if (row[0].size or 0.0) >= banner_min and _is_banner(_plain(row)):
            if seen_banner and i and not _is_banner(_plain(rows[i - 1])):
                rows = rows[:i]
                break
            seen_banner = True

    def is_fence(row) -> bool:
        return len(row) == 1 and _is_fence(row[0], pages[row[0].page].width)

    # THE COVER IS FENCED. Page 1 always opens one — the rule directly under
    # the banner — and the cover carries at least three in all; a caption
    # naming forty Chinese exporters fills page 1 by itself and states its
    # docket, origin and dates on page 2 (fusong, linyi), so the count is
    # taken over the whole cover, not over page 1.
    if not any(is_fence(r) and r[0].page == 1 for r in rows):
        return NOTHING                    # not the typed-fence contract
    if len([r for r in rows if is_fence(r)]) < 3:
        return NOTHING

    # ---- bands: what the court fenced ------------------------------------
    bands: list = []                      # [[row, …], …]
    fences: list = []                     # the fence row that CLOSES band i
    cur: list = []
    for row in rows:
        if is_fence(row):
            bands.append(cur)
            fences.append(row[0])
            cur = []
        else:
            cur.append(row)
    bands.append(cur)
    fences.append(None)                   # the trailing band is open

    crit: dict = {"headmatter_style": STYLE_TYPED_FENCE}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    # NO ANCHOR IS EVER CLAIMED. cafc's own heading over a writing
    # ('O R D E R') stands under the LAST fence, and the reader stops there
    # — so the anchor an unsigned writing needs is never taken away and
    # never has to be given back.
    anchor_ids: list = []
    banner_rows: list = []
    caption_groups: list = [[]]
    origin_bands: list = []
    panel_rows: list = []
    counsel_rows: list = []
    lower_dockets: list = []
    dockets: list = []
    dates: dict = {}
    notice_rows: list = []

    def emit(row: list, role: str, rel_from: float = 0.0):
        first = row[0]
        pm = pages[first.page]
        align = line_alignment(first, pm.width, geom,
                               banner_center_min_size=banner_min)
        rel = 0.0
        if rel_from and align == "L" and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=_markup(row), prov=m.Prov(first.page,
                                           tuple(l.id for l in row)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(l.all_bold for l in row), rel=rel, role=role))
        consumed.update(l.id for l in row)

    def fence(line):
        """THE FENCE ITSELF RENDERS. It is the court's own section mark, not
        furniture, and core only draws the marks a reader left behind."""
        items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                            typed=True, span="full"))
        consumed.add(line.id)

    def take_docket(text: str):
        flat = _norm(text).rstrip(".")
        low = flat.lower()
        if low.startswith("appeal no"):
            flat = flat.split(".", 1)[1].strip() if "." in flat else flat
        dockets.append(flat)

    # ---- the closed bands: the court said where each one ends ------------
    seen_tail = counsel_closed = False
    for idx, band in enumerate(bands[:-1]):
        closing = fences[idx]
        texts = [_plain(r) for r in band]
        head = texts[0] if texts else ""
        low = head.lower()
        kind = None
        if not band:
            kind = "empty"
        elif all(_is_note(t) or _is_banner(t) or _FLAG_ROW.match(t)
                 or (r[0].size or 0.0) >= banner_min
                 for t, r in zip(texts, band)):
            kind = "court"
        elif _DOCKET_BARE.match(head):
            # A NEW DOCKET OPENS A NEW CASE, and the case starts with its
            # caption — on an errata sheet inside the same band, because
            # the court states the errata's own date above the docket and
            # the caption under it. The tail flag falls back with it;
            # left standing, the caption read as the appearances.
            kind = "docket"
            seen_tail = False
        elif _origin_opener(head):
            kind = "lower-court"
            seen_tail = True
        elif _is_date_row(head) or _FLAG_ROW.match(head):
            kind = "date"
            seen_tail = True
        elif _squeeze(head) in _LABEL_TITLE:
            # THE COURT'S OWN LABEL, and the court FENCED it — this is the
            # paper's name, not the writing's heading.
            kind = "title"
            seen_tail = True
        elif low.startswith("before"):
            kind = "panel"
            seen_tail = True
        elif seen_tail:
            # THE BAND AFTER THE COURT'S OWN TAIL IS THE APPEARANCES. cafc
            # gives them no label at all — an entry opens on the lead
            # counsel's name and runs into the firm block for that party —
            # so the fence is what says where they are. The court CLOSED
            # this one, and what stands under that closing fence is the
            # writing, never more of the roster.
            kind = "counsel"
            counsel_closed = True
        else:
            # EVERYTHING BETWEEN THE BANNER AND THE TAIL IS THE CAPTION —
            # not only the rows that look like parties. A wrapped roll of
            # forty exporters looks like prose and the 'v.' says nothing
            # for itself; cafc puts nothing else in that span.
            kind = "caption"

        band_origin = None
        for row in band:
            text = _plain(row)
            # A CONSOLIDATED RECORD JOINS TWO APPEALS, and cafc types a row
            # of dashes between them — 100pt wider than the fence and drawn
            # in a different glyph, so it is not a section boundary. What
            # follows it is the next appeal's caption, wherever inside a
            # band the court put it (in_re_byrd sets the second caption
            # under the first appeal's origin, inside the origin's fence).
            if _TYPED_DASHES.match(text):
                caption_groups.append([])
                kind = "caption"
                emit(row, "caption")
                continue
            # A FENCED LABEL NAMES THE PAPER wherever in a closed band the
            # court set it: the errata sheet prints 'ERRATA' under the date
            # it was issued, inside the date's own fence.
            if _squeeze(text) in _LABEL_TITLE:
                crit.setdefault("title", _squeeze(text))
                emit(row, "title")
                continue
            if kind == "court":
                if _is_note(text):
                    notice_rows.append(row)
                    crit.setdefault("publication_status", "unpublished")
                    continue
                if _FLAG_ROW.match(text):
                    crit.setdefault(
                        "publication_status",
                        "unpublished" if text.lower().startswith("non")
                        else "published")
                elif _is_banner(text):
                    banner_rows.append(text)
                emit(row, "court")
            elif kind == "docket":
                if _DOCKET_BARE.match(text):
                    take_docket(text)
                    emit(row, "docket")
                else:
                    caption_groups[-1].append(text)
                    emit(row, "caption")
            elif kind == "caption":
                caption_groups[-1].append(text)
                emit(row, "caption")
            elif kind == "lower-court":
                if band_origin is None:
                    band_origin = []
                    origin_bands.append(band_origin)
                band_origin.append(text)
                emit(row, "lower-court")
            elif kind == "date":
                if _FLAG_ROW.match(text):
                    crit.setdefault(
                        "publication_status",
                        "unpublished" if text.lower().startswith("non")
                        else "published")
                    emit(row, "court")
                else:
                    dates.update(_labelled_dates(text))
                    emit(row, "date")
            elif kind == "panel":
                panel_rows.append(text)
                emit(row, "panel")
            elif kind == "counsel":
                counsel_rows.append(text)
                emit(row, "counsel", rel_from=body_x0)
        if closing is not None:
            fence(closing)

    # ---- the trailing band: where the writing begins ---------------------
    # Nothing under the last fence is closed, so it is read ROW BY ROW and
    # the walk ends at the first thing that belongs to the writing: its
    # byline, or — where the paper carries none — the heading the court
    # types over it ('O R D E R').
    tail = bands[-1]
    state = "tail"
    roster_read = False
    i = 0
    while i < len(tail):
        row = tail[i]
        text = _plain(row)
        low = text.lower()

        def run_on(j: int) -> int:
            """How far a statement WRAPS.

            Two things end it, and both are on the page. A statement in
            cafc's cover ends on a full stop — with a footnote mark riding
            on the stop, which is not part of it. And a wrap is ONE LEADING
            below its own first row; the court sets a fresh statement a
            paragraph apart (davis prints 'Before LOURIE and HUGHES,
            Circuit Judges, and / FREEMAN, District Judge.†' one leading
            apart and its byline a paragraph below, and the byline parses
            as a roster row exactly like the row above it)."""
            k = j
            while k + 1 < len(tail):
                here, nxt = tail[k], tail[k + 1]
                if _ends_sentence(_plain(here)):
                    break
                if _opens_landmark(_plain(nxt)):
                    break
                if nxt[0].page != here[0].page:
                    break
                if nxt[0].top - here[0].top > _WRAP_LEAD * lead:
                    break
                k += 1
            return k

        if _squeeze(text) in _LABEL_TITLE:
            break                         # the writing's own heading
        if parser.parse(text) is not None and not low.startswith("before"):
            break                         # the first byline ends the reader
        if low.startswith("before"):
            end = run_on(i)
            for r2 in tail[i:end + 1]:
                panel_rows.append(_plain(r2))
                emit(r2, "panel")
            # THE ROSTER CLOSES THE COVER. cafc states who sat last, under
            # the appearances, so nothing below it is an appearance — the
            # en banc denial states which judge concurred and which
            # dissented in rows that name judges in small caps exactly as
            # an appearance names counsel, and those belong to the writings
            # they announce.
            state = "tail"
            roster_read = True
            i = end + 1
            continue
        if _origin_opener(text):
            end = run_on(i)
            origin_bands.append([])
            for r2 in tail[i:end + 1]:
                origin_bands[-1].append(_plain(r2))
                emit(r2, "lower-court")
            state = "tail"
            i = end + 1
            continue
        if _DOCKET_BARE.match(text):
            take_docket(text)
            emit(row, "docket")
            i += 1
            continue
        if _is_date_row(text):
            dates.update(_labelled_dates(text))
            emit(row, "date")
            i += 1
            continue
        # THE APPEARANCES, where the court left them unfenced. An entry
        # OPENS on a name set in small caps; its continuation rows carry
        # none, so the roster runs on until the next landmark. A roster the
        # court already CLOSED with a fence does not reopen here — what
        # stands under that fence is the writing.
        if state == "counsel" or (not counsel_closed and not roster_read
                                  and seen_tail
                                  and any(_small_caps(l) for l in row)):
            state = "counsel"
            counsel_rows.append(text)
            emit(row, "counsel", rel_from=body_x0)
            i += 1
            continue
        break                             # a row this contract does not name

    # ---- what the block says ---------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    caption_rows = [t for g in caption_groups for t in g]
    if caption_rows:
        crit["caption"] = caption_rows
        # THE PARTIES ARE THE LEAD CASE'S. A consolidated record prints one
        # caption per appeal; joining them all yields a case name that names
        # four sides and belongs to none of them.
        lead_case = next((g for g in caption_groups if g), caption_rows)
        sides = _sides(lead_case, vocab=vocab)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            # A MANDAMUS PETITION HAS ONE SIDE ('IN RE UNITED STATES, /
            # Petitioner'). One party is still the parties.
            one = _sides(lead_case, vocab=vocab, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one
    # THE ORIGIN IS THE LEAD APPEAL'S. A consolidated record states one
    # origin per appeal; joined together they name four tribunals and belong
    # to none of them. The rest contribute their dockets and nothing else.
    for n, band in enumerate(origin_bands):
        printed = _join(band, vocab)
        if not printed:
            continue
        lower_docket, judge = _split_origin(printed)
        if n == 0:
            crit["lower_court"] = printed
            if judge:
                crit["lower_court_judge"] = judge
        if lower_docket:
            lower_dockets.append(lower_docket)
    if dockets:
        crit["docket_number"] = dockets[0]
    # A CONSOLIDATED RECORD STATES THE SAME LOWER NUMBER TWICE — once under
    # the appeal and once under the petition it was joined with. It is one
    # docket; the order it was printed in is kept.
    others: list = []
    for value in dockets[1:] + lower_dockets:
        if (value and value not in others
                and value != crit.get("docket_number")):
            others.append(value)
    if others:
        crit["other_dockets"] = others
    if panel_rows:
        printed = _join(panel_rows, vocab)
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _join(counsel_rows, vocab)[:4000]
    for label, value in dates.items():
        if label in ("decided", "decided_and_filed", "filed", "amended",
                     "entered"):
            crit.setdefault("decision_date", value)
        elif label in ("submitted", "argued_and_submitted"):
            crit.setdefault("submitted", value)

    # A CLAIM MUST BE TOTAL. The notice the court stamps over its banner is
    # a notice, so it is recorded as a Drop; and so is every running head
    # the reader stepped over.
    #
    # THE STATIONERY IS THE COURT'S, on every page the reader looked at.
    # Core recognizes a running head by REPETITION, which needs pages to
    # repeat on; 26 of the 100 records run to one or two pages, and there
    # the head is printed once and core cannot see it. Left standing it
    # became the order's opening paragraph ('BRADLEY v. US'). Nothing else
    # stands in that band: measured over the corpus the head bottoms out at
    # 89.8 and no page-2 row of content opens above 118.2, so the reader
    # can claim the band on any page it scanned without reaching into a
    # writing — a head is never a writing's content.
    for row in notice_rows:
        dropped.append(m.Dropped(
            text=_plain(row), prov=m.Prov(row[0].page,
                                          tuple(l.id for l in row)),
            kind="notice"))
        consumed.update(l.id for l in row)
    for line in head_lines:
        dropped.append(m.Dropped(
            text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
            kind="running-head"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _ends_sentence(text: str) -> bool:
    """Does this row end its statement?

    A FOOTNOTE MARK RIDES ON THE FULL STOP and is not part of it: cafc
    footnotes the visiting judge on the roster's last row ('FREEMAN,
    District Judge.†', 'STARK, Circuit Judges.1'), and a row read as
    unterminated ran the roster on into the byline below it. The mark
    characters are core's, so the two subsystems cannot disagree about what
    a reference looks like."""
    flat = _norm(text).rstrip()
    while flat and flat[-1] in FOOTNOTE_LABEL_CHARS:
        flat = flat[:-1].rstrip()
    return flat.endswith((".", ":", "!", "?"))


def _opens_landmark(text: str) -> bool:
    """Does ``text`` open a section of its own? The wrap rule needs this: a
    statement the court left unterminated still ends where the next landmark
    starts."""
    low = _norm(text).lower()
    return bool(low.startswith("before")
                or _origin_opener(text)
                or _DOCKET_BARE.match(_norm(text))
                or _is_date_row(text)
                or _squeeze(text) in _LABEL_TITLE)


def _sides(caption_rows: list, vocab: set | None = None,
           one_sided: bool = False):
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
        # A STATUS LABEL is hyphenated on this court's paper
        # ('Plaintiff-Appellant'), so the hyphen separates roles the way a
        # space does elsewhere. A party NAME that carries one survives,
        # because every word has to be a status word for the row to be one.
        words = [w.strip(",.;–-/ ")
                 for w in bare.replace("–", " ").replace("-", " ")
                             .replace("/", " ").split()]
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
    # incorporated under ('MIDWEST ENGINEERED COMPONENTS, INC.'), and
    # stripping it renames the party.
    if one_sided:
        return _join(left + right, vocab).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_join(left, vocab).rstrip(", "),
            _join(right, vocab).rstrip(", "))
