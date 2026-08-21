"""United States Court of Appeals for the Ninth Circuit ('ca9').

Everything unique to ca9 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'ruled caption box'. ca9 DRAWS its caption's column
divider: a vertical rule with a horizontal rule across its head and
another across its foot. Those three strokes are the whole zone system,
and they are identical on both of the court's papers:

    published slip (41 of 102) — the reporter measure, a 396x612 sheet
    set 12pt on a 54pt rail:

        FOR PUBLICATION                              the publication flag
        UNITED STATES COURT OF APPEALS               the banner, 14pt bold
        FOR THE NINTH CIRCUIT
        ─────────────────────────┐                   the box: top rule…
        3PAK LLC, doing business │  No. 24-7139      …and the divider
        as Oma Bap; HUGO         │
             Plaintiffs -        │  D.C. No.         the court below's
             Appellants,         │  2:23-cv-00540-   own number, wrapped
        v.                       │  TSZ
        CITY OF SEATTLE,         │  OPINION          what the paper IS
             Defendant-Appellee. │
        ─────────────────────────┘                   …and the foot rule
        Appeal from the United States District Court   the origin
        for the Western District of Washington
        Thomas S. Zilly, District Judge, Presiding
        Argued and Submitted November 18, 2025         the dates…
        Seattle, Washington                            …and where
        Filed May 5, 2026
        Before: M. Margaret McKeown, Richard A. Paez, and     the roster
        Roopali H. Desai, Circuit Judges.
        Opinion by Judge McKeown                       who wrote what
        SUMMARY*                       the staff summary — core's section
        …
        COUNSEL                        the appearances — headmatter again
        Angelo J. Calfo (argued) and Tyler S. Weaver, Angeli & Calfo …
        OPINION                        the writing's own anchor: left alone
        McKEOWN, Circuit Judge:        ← the reader stops

    memorandum (61 of 102) — letter paper, 14pt on a 72pt rail, with the
    clerk's filing stamp set in the top right corner:

        NOT FOR PUBLICATION                     FILED
        UNITED STATES COURT OF APPEALS          JUN 12 2026
        FOR THE NINTH CIRCUIT                   MOLLY C. DWYER, CLERK
        ─────────────────────────┐              U.S. COURT OF APPEALS
        ALFREDO SILVA-PALOMARES; │  No. 16-72588
             Petitioners,        │  Agency Nos. A206-373-927
        v.                       │       A206-373-929
        TODD BLANCHE, Acting     │  MEMORANDUM*
        Attorney General,        │
        ─────────────────────────┘
        On Petition for Review of an Order of the
        Board of Immigration Appeals
        Submitted February 11, 2026**
        San Francisco, California
        Before:  S.R. THOMAS and MILLER, Circuit Judges, and BLUMENFELD,***
        District Judge.
        <the disposition runs straight in, unsigned>

The dispatch is the BOX, not the flag beside it: over the whole corpus
101 of 102 records draw it, and the one that does not draws the same two
horizontal rules as a filled path, which pdfio collects while dropping
the vertical it was paired with — so the divider is read off the rules'
own right end, which is where the vertical stands on every record that
has one. A record that draws neither gets NOTHING.

The reader claims HEADMATTER ONLY. It stops at the first byline, at the
label the court prints over that byline, and at the first row this
contract does not name. The one section it steps OVER without claiming is
the staff summary the profile declares as front matter: core assembles
that into its own section, and the reader picks the walk back up at the
appearances printed under it — which are headmatter, and which a reader
that simply stopped at the summary would leave for the writing below to
swallow.
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
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop ca9 used to sit in, so nothing about its bylines
# changes by being moved here. `front_matter` likewise: ca9 prints a staff
# summary ('SUMMARY**') that is expressly not part of the opinion.
CA9 = register(CourtProfile(
    "ca9", "United States Court of Appeals for the Ninth Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings
        # ('R. NELSON, J., concurring:' — ca9 sets the full title only on
        # the majority).
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
    front_matter=("summary",),
))

STYLE_RULED_BOX = "ruled caption box"

# ---- ca9's declared facts (measured over the corpus, not tuned) ----------
# THE DIVIDER is a drawn vertical. It stands between a third and five
# sixths of the way across the sheet on every record (242.4/396 = 0.61 on
# the reporter measure, 327.9/612 = 0.54 on letter) and it is as tall as
# the caption — never a hairline artefact.
_DIVIDER_MIN_H = 40.0
_DIVIDER_BAND = (0.30, 0.85)
# THE HEAD AND FOOT RULES that close the box. 188pt on the reporter sheet,
# 256pt on letter; 100pt clears every stray tick and admits both.
_BOX_RULE_MIN_W = 100.0
# How far a rule's end may sit from the divider's own end before the two
# are not the same drawing. Measured: the foot rule overhangs the left
# margin by 0.7pt and meets the divider exactly.
_BOX_RULE_JOIN = 12.0
_BAND_PAD = 6.0
# THE CLERK'S STAMP is a right-hand column, not a wording: 'FILED' at
# x0=473 on a 612pt sheet, the date under it, the clerk's name and office
# under that. 0.72 of the measure clears the banner (x0=184) by a mile.
_STAMP_X0 = 0.72
# The stamp's own date, which is the day the court filed the paper. Read
# out before the stamp is recorded as furniture.
_STAMP_DATE = re.compile(
    r"\b([A-Z][a-z]{2,8}\.?\s+\d{1,2},?\s+\d{4})\b")
# CENTRED means EQUAL SIDE MARGINS, measured on the row itself. ca9 sets
# its origin, its dates and its descriptors on the page axis and its
# roster flush left, and a shared alignment test reads a centred row whose
# left edge is under 100pt as left-aligned instead.
_CENTER_TOL = 6.0
# THE HEADMATTER IS SET SOLID and its statements are separated by a full
# extra line: one leading is 1.15x the type size on both papers (13.8 on
# the 12pt reporter sheet, 16.1 on the 14pt memorandum) and the stand-off
# between statements is exactly twice that (27.6 / 32.2). So a gap over
# 1.5 type sizes opens a new BAND, and nothing in between ever occurs.
#
# The leading is taken from the TYPE, not from the page's smallest gap: a
# footnote mark and its own text share a baseline (1.1pt apart), the two
# caption columns are set on a half-leading offset from each other (6.8pt
# apart), and one record sets its party column double. All three read as
# 'the leading' to a measurement made over rows alone.
_BAND_GAP = 1.5
# How far the headmatter may run. The published slip's roster lands on
# page 2, its staff summary runs on from there, and the appearances that
# close the front matter land as deep as page 7; eight pages reaches
# every record's counsel block.
_MAX_PAGES = 8
# A running head sits in the top band of a continuation page.
_HEAD_BAND_MAX = 60.0

# THE FOOTNOTE SEPARATOR is a drawn rule at the body's own left margin,
# and it is always NARROWER than the rules that close the caption box —
# 144pt against the box's 188pt (reporter) or 256pt (letter). Reading it
# by measure alone would take the box's foot rule with it; reading it
# relative to the box the same record drew cannot.
_SEP_MARGIN = 4.0
_SEP_NARROWER = 8.0
# …and a separator stands in the lower part of its page. A rule in the
# top third is the running head's, not a note's.
_SEP_MIN_DEPTH = 0.35

_TYPED_RULE = re.compile(r"^[_\-–—]{4,}$")

# THE COURT'S OWN DOCKET, as the caption's right column prints it:
# 'No. 24-7139', 'No.  20-36024', 'Nos. 21-70168/21-70670'.
_DOCKET_CELL = re.compile(
    r"^Nos?\.\s*\d{2}-\d{2,6}(?:[/,;]\s*(?:\d{2}-)?\d{2,6})*\.?$", re.I)
# THE TRIBUNAL BELOW states its own number under a label of its own:
# 'D.C. No.', 'Agency No.', 'Agency Nos. A206-373-927', 'EPA Nos.',
# 'BIA No.'. Anything carrying 'No.'/'Nos.' that is not the court's own
# docket is the number below.
_LOWER_CELL = re.compile(r"\bNos?\.", re.I)
# WHAT THE PAPER IS, printed in the caption's right column. A closed
# vocabulary of the words ca9 builds that label from — it sets 'ORDER AND
# / AMENDED / OPINION' over three rows, so the label is a RUN of rows
# every one of whose words is in the vocabulary.
_LABEL_WORDS = frozenset((
    "OPINION", "ORDER", "MEMORANDUM", "AMENDED", "SUBSTITUTE",
    "SUBSTITUTED", "CORRECTED", "REVISED", "SUPERSEDING", "JUDGMENT",
    "DISPOSITION", "PER", "CURIAM", "AND", "EN", "BANC", "SECOND",
))

# HOW ca9 NAMES THE TRIBUNAL IT REVIEWS. Openers only — what follows is
# the tribunal's own name, which is never read by wording.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "appeal of", "appeals of",
    "on petition for review", "on petitions for review",
    "petition for review", "petitions for review",
    "on petition for a writ", "on petition for writ",
    "petition for a writ", "petition for writ",
    "petitions for a writ", "petitions for writ",
    "on remand from", "on review of", "review of",
    "on application for", "application for",
    "on request for", "request for",
    "on certification from", "certification from",
    "on petition for rehearing", "on petitions for rehearing",
    "d.c. no", "agency no",
)
_REHEARING = ("on petition for rehearing", "on petitions for rehearing")
# THE DATE LABELS ca9 prints, longest first so 'Argued and Submitted'
# wins over 'Submitted'.
_DATE_LABELS = ("argued and submitted en banc", "argued and submitted",
                "submitted en banc", "reargued and resubmitted",
                "resubmitted", "reargued", "argued", "submitted",
                "decided and filed", "decided", "filed", "amended",
                "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# WHO WROTE WHAT, printed under the roster on the published slip:
# 'Opinion by Judge McKeown;' / 'Concurrence by Judge R. Nelson' /
# 'Partial Concurrence and Partial Dissent by Judge BEA.' / 'Order;' /
# 'Per Curiam Opinion'. A closed vocabulary of the kinds ca9 names.
_DESCRIPTOR_OPENERS = (
    "opinion by", "amended opinion by", "concurrence by", "dissent by",
    "partial concurrence and partial dissent by", "partial concurrence by",
    "partial dissent by", "concurrence and dissent by",
    "concurrence and partial dissent by",
    "per curiam opinion", "per curiam", "order;", "opinion;", "order",
    "opinion", "judgment",
)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. ca9 spaces the hyphen ('Plaintiffs - Appellants,'), so the
# hyphen separates roles the way a space does.
_STATUS_WORDS = frozenset((
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "intervenors", "amicus", "amici", "movant", "movants",
    "applicant", "applicants", "claimant", "claimants", "creditor",
    "creditors", "trustee", "trustees", "objector", "objectors",
    "counterclaimant", "counterdefendant", "garnishee", "garnishees",
))
_STATUS_GLUE = frozenset((
    "and", "the", "in", "of", "party", "parties", "real", "interest",
    "cross", "third", "pro", "se", "counter", "-", "",
))
_TITLE_WORDS = ("judge", "judges", "justice", "justices")

_PUBLISHED = "for publication"
_UNPUBLISHED = "not for publication"

# THE COURT'S OWN SECTION LABELS on the published slip, each set alone
# on a centred bold row between the drawn fences.
_LABEL_COUNSEL = ("COUNSEL", "APPEARANCES")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _bare(text: str) -> str:
    """The row without the footnote mark the court hangs on it
    ('MEMORANDUM*', 'February 11, 2026**')."""
    return _norm(text).rstrip("*†‡∗⁎﹡＊ ")


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("united states court of appeals",
                   "for the ninth circuit",
                   "united states court of appeals for the ninth circuit")


def _is_flag(text: str) -> str | None:
    low = _norm(text).lower().rstrip(".")
    if low.startswith(_UNPUBLISHED):
        return "unpublished"
    if low.startswith(_PUBLISHED):
        return "published"
    return None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_label_cell(text: str) -> bool:
    """Is this right-column cell part of the paper's own name?"""
    flat = _bare(text).rstrip(".:;")
    if not flat or len(flat) > 40:
        return False
    words = [w.strip(".,;:") for w in flat.upper().split()]
    return bool(words) and all(w in _LABEL_WORDS for w in words if w)


def _is_front_matter(text: str) -> bool:
    """The heading of a section the court publishes AHEAD of the opinion
    and the profile declares ('SUMMARY**'). It is not the reader's: core
    assembles it into its own section, and the reader steps over it to
    reach the appearances printed under it."""
    return _bare(text).lower().rstrip(":") in CA9.front_matter


def _is_counsel_label(text: str) -> bool:
    return _bare(text).upper().rstrip(":") in _LABEL_COUNSEL


def _is_descriptor(text: str) -> bool:
    low = _bare(text).lower().rstrip(".;")
    if len(low) > 80:
        return False
    return low.startswith(_DESCRIPTOR_OPENERS)


def _opens_landmark(text: str) -> bool:
    """Does this row open a section of its own? The page-break rule
    needs it: a statement the court left unfinished still ends where the
    next landmark starts."""
    return bool(_origin_opener(text) or _is_date_row(text)
                or _norm(text).lower().startswith("before")
                or _is_descriptor(text) or _is_front_matter(text)
                or _is_counsel_label(text) or _is_label_cell(text))


def _labelled_dates(text: str) -> dict:
    """{'argued_and_submitted': 'November 18, 2025', 'filed': 'May 5, 2026'}.

    ca9 sets one label per centred row. A date row is SHORT — 'filed'
    inside prose is an ordinary English word."""
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
        # 'May 5, 2026' is part of the date, so the value is a SLICE of
        # the row, never a re-join of its tokens.
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
    return bool(_labelled_dates(flat)) and any(
        low.startswith(lab) for lab in _DATE_LABELS)


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    The designation clause a visiting judge carries names nobody, so the
    roster ends where it begins."""
    flat = _bare(text)
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
        piece = chunk.strip().strip(".*†‡: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in re.split(r"\band\b", piece, flags=re.I):
            name = part.strip().strip(".*†‡: ").strip()
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


def _trial_judge(text: str):
    """'Thomas S. Zilly, District Judge, Presiding' — the judge is the
    clause that ENDS on a bench word, and ca9 closes it with 'Presiding'."""
    flat = _bare(text)
    mm = re.match(r"^([A-Z][^,]*(?:,\s*(?:Jr|Sr|II|III|IV)\.?)?)"
                  r",\s*(?:Chief\s+|Senior\s+|Acting\s+)?"
                  r"(?:U\.?S\.?\s+)?(?:District|Circuit|Magistrate|"
                  r"Bankruptcy|Senior\s+District)\s+Judge,?\s*"
                  r"(?:Presiding)?\.?$", flat)
    return _norm(mm.group(1)) if mm else None


# --------------------------------------------------------------------------
# the box — ca9's caption divider, and the dispatch
# --------------------------------------------------------------------------

def _boxes(pm) -> list:
    """The caption boxes drawn on ``pm``, top-first.

    A box is a VERTICAL rule with a horizontal rule across its head and
    another across its foot: three strokes of one drawing. The vertical
    is the divider, the horizontals give the band."""
    out = []
    lo, hi = pm.width * _DIVIDER_BAND[0], pm.width * _DIVIDER_BAND[1]
    rules = [r for r in pm.h_rules if r.width >= _BOX_RULE_MIN_W]
    for v in pm.v_rules:
        if v.height < _DIVIDER_MIN_H or not lo < v.x < hi:
            continue
        heads = [r for r in rules
                 if abs(r.top - v.top) <= _BOX_RULE_JOIN
                 and r.x1 >= v.x - _BOX_RULE_JOIN]
        feet = [r for r in rules
                if abs(r.top - v.bottom) <= _BOX_RULE_JOIN
                and r.x1 >= v.x - _BOX_RULE_JOIN]
        if not (heads and feet):
            continue
        out.append({"x": float(v.x),
                    "top": min(r.top for r in heads),
                    "bottom": max(r.top for r in feet),
                    "x0": min(r.x0 for r in heads + feet),
                    "x1": max(r.x1 for r in heads + feet),
                    "page": pm.number})
    # ONE BAND IS ONE BOX. The order form draws its divider as a TWIN
    # rule (x=323.7 and x=337.4 between the same two horizontals); both
    # are the same column boundary, and read as two boxes the caption
    # renders twice and the docket is recorded twice. The left rail is
    # the boundary the columns are set against.
    out.sort(key=lambda b: (b["top"], b["x"]))
    kept: list = []
    for box in out:
        if kept and box["top"] < kept[-1]["bottom"] \
                and box["bottom"] > kept[-1]["top"]:
            continue
        kept.append(box)
    return kept


def _rule_pair_box(pm) -> list:
    """The same box read off its HORIZONTAL rules alone.

    One record in the corpus draws the whole box as a filled path, and
    pdfio collects a filled path only as a horizontal — so the divider is
    missing while both rules survive. Every drawn box in the corpus ends
    its head and foot rules exactly AT the divider, so the rules' shared
    right end is where the vertical stands. Only used when the page draws
    no divider at all, and only where a second column really is set past
    that end."""
    rules = sorted((r for r in pm.h_rules
                    if r.width >= _BOX_RULE_MIN_W
                    and r.x1 < pm.width - 60.0),
                   key=lambda r: r.top)
    for i, head in enumerate(rules):
        for foot in rules[i + 1:]:
            if abs(head.x0 - foot.x0) > 4.0 or abs(head.x1 - foot.x1) > 4.0:
                continue
            if foot.top - head.top < _DIVIDER_MIN_H:
                continue
            band = [l for l in pm.lines if l.plain.strip()
                    and head.top - _BAND_PAD <= l.top <= foot.top + _BAND_PAD]
            if len(band) < 4:
                continue
            if not any(l.x0 > head.x1 + 2.0 for l in band):
                continue
            return [{"x": float(head.x1), "top": head.top, "bottom": foot.top,
                     "x0": min(head.x0, foot.x0),
                     "x1": max(head.x1, foot.x1), "page": pm.number}]
    return []


def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _align(line, pm, geom, body_size: float) -> m.Align:
    """CENTRED IS EQUAL SIDE MARGINS. ca9 sets its origin, dates and
    descriptors on the page axis at the body's own size, and a width-capped
    test reads them as left-aligned because their left edge is inside
    100pt."""
    room = pm.width - line.x1
    if (abs(line.x0 - room) <= _CENTER_TOL
            and (line.x1 - line.x0) < pm.width * 0.78):
        return m.Align.CENTER
    return m.Align(line_alignment(line, pm.width, geom,
                                  banner_center_min_size=body_size + 1.0))


# --------------------------------------------------------------------------
# the caption box, column by column
# --------------------------------------------------------------------------

def _caption(box_lines: list, box: dict, pm, geom, body_size: float):
    """One caption box as a CaptionBlock, plus its two columns' text.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned. Sides
    split at the divider itself, glyph by glyph: whether pdfio already
    broke a row at the vertical is an accident of how the split fell."""
    mid = box["x"]
    rows: list[list] = []
    for line in sorted(box_lines, key=lambda l: (l.top, l.x0)):
        if rows and abs(rows[-1][0].top - line.top) <= 2.5:
            rows[-1].append(line)
        else:
            rows.append([line])
    if not rows:
        return None, [], []

    def cell(cells: list, role: str):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text,
            prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=_align(first, pm, geom, body_size),
            x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    left, right = [], []
    left_plain, right_plain = [], []
    right_tops: list = []
    for row in rows:
        l_cells, r_cells = [], []
        for line in row:
            for side, bucket in ((_side(line, mid, "L"), l_cells),
                                 (_side(line, mid, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left.append(cell(l_cells, "caption") if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number),
                                  role="caption"))
        right.append(cell(r_cells, "caption") if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number),
                                   role="caption"))
        # THE CRITERIA READ THE PAGE'S OWN TEXT, never the markup: joining
        # the rendered form back into a scalar double-escapes every
        # ampersand the caption prints.
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
        right_tops.append(min((c.top for c in r_cells), default=0.0))
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop()
        right.pop()
        left_plain.pop()
        right_plain.pop()
        right_tops.pop()
    # A CAPTION THAT RUNS OVER THE PAGE opens a fresh box with the parties
    # alone in it — the docket and the label were stated once, in the box
    # on page 1. A right column of nothing but blank cells is not a
    # column: it renders as one empty row per party, and on the longest
    # captions in the corpus that doubles the block.
    if not any(_strip_tags(r.text).strip() for r in right):
        right = []
        right_plain = [""] * len(left_plain)
        right_tops = [0.0] * len(left_plain)
    block = m.CaptionBlock(
        left=left, right=right, rail="|", rail_rows=len(left),
        style_id="backwards-c",
        fp={"rail": "drawn", "rail_band": (box["top"], box["bottom"]),
            "mid_x": mid},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in box_lines))))
    return block, left_plain, list(zip(right, right_plain, right_tops))


def _right_groups(cells: list) -> list:
    """The right column's stack, split into the GROUPS the page sets.

    Each group is (kind, [rows]). The column carries three things and
    ca9 names each of them: the court's own docket, the number the case
    carries below (under its own 'No.' label, wrapped over as many rows as
    the column is narrow), and what the paper IS. A row that names none of
    them continues whatever group is open — a docket broken over two rows
    carries no label of its own, and an agency's NAME wraps under its
    number."""
    groups: list = []
    for row, flat, top in cells:
        if not flat:
            continue
        if _is_label_cell(flat):
            kind = "label"
        elif _DOCKET_CELL.match(flat):
            kind = "docket"
        elif _LOWER_CELL.search(flat):
            kind = "lower"
        else:
            kind = None
        if kind is None:
            if groups and groups[-1][0] != "label":
                groups[-1][1].append((row, flat, top))
                continue
            kind = "other"
        if groups and groups[-1][0] == kind == "label":
            groups[-1][1].append((row, flat, top))
            continue
        groups.append((kind, [(row, flat, top)]))
    return groups


def _join_lower(texts: list) -> str:
    """'D.C. No.' / '2:23-cv-00540-' / 'TSZ' -> 'D.C. No. 2:23-cv-00540-TSZ'.

    A docket broken over two rows KEEPS ITS HYPHEN, and the column is
    narrow enough to split one. What follows the label is a LIST when its
    members are numbers (one per petitioner on a family's case) and a
    continuation when they are words (the agency's own name)."""
    merged: list = []
    for text in texts:
        if merged and merged[-1].endswith(("-", "–", "—")):
            merged[-1] += text
        else:
            merged.append(text)
    head, rest = merged[0], merged[1:]
    label, first = head, ""
    for marker in ("Nos.", "No.", "Nos", "No"):
        at = head.find(marker)
        if at >= 0:
            label, first = head[:at + len(marker)], head[at + len(marker):]
            break
    out = _norm(label)
    parts = [p for p in [_norm(first)] + rest if p]
    for part in parts:
        if out.endswith((".", ":")) or not any(c.isdigit() for c in part):
            out = f"{out} {part}"
        else:
            out = f"{out}; {part}"
    return _norm(out)


def _sides(caption_rows: list):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale —
    the status labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat or _TYPED_RULE.match(flat):
            continue
        head = flat.split()[0].rstrip(".").lower()
        if head in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. ").lower()
        # A STATUS LABEL is spaced-hyphenated on this court's paper
        # ('Plaintiffs - Appellants,'), so the hyphen separates roles the
        # way a space does. A party NAME that carries one survives,
        # because EVERY word has to be a status word for the row to be
        # one.
        words = [w.strip(",.;–-/ ")
                 for w in bare.replace("–", " ").replace("-", " ")
                              .replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or w in _STATUS_GLUE
                         for w in words):
            continue
        if flat.lower().startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    if not (left and right and seen_pivot):
        return None
    # THE COMMA is the caption's own apparatus — it leads to the status
    # row below. The FULL STOP is not: it ends the abbreviation the party
    # is incorporated under, and stripping it renames the party.
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ca9")
def read_headmatter_ca9(model, geom, **_):
    """Read ca9's ruled-caption-box headmatter, or NOTHING.

    NOTHING is returned for anything that is not the contract above:
    core's shared walk places those rows unidentified, which is a smaller
    error than a confident misreading."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    if not _boxes(page1) and not _rule_pair_box(page1):
        return NOTHING                    # no drawn caption box: not ca9's

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CA9.byline)

    rows: list = []                       # content lines, in page order
    head_lines: list = []                 # the running head, page by page
    stamp_column: list = []               # the clerk's stamp, furniture and all
    boxes_by_page: dict = {}
    for pm in model.pages[:_MAX_PAGES]:
        found = _boxes(pm) or (_rule_pair_box(pm) if pm.number == 1 else [])
        boxes_by_page[pm.number] = found
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: ca9's one-row
            # running head ('2  3PAK LLC V. CITY OF SEATTLE') and the foot
            # folio. Core measures and records those; the reader steps
            # over them rather than claiming them twice — and takes the
            # head core could not see, because a reader that claims a
            # region inherits its furniture.
            if pm.number == 1 and line.x0 >= pm.width * _STAMP_X0 \
                    and found and line.top < found[0]["top"]:
                stamp_column.append(line)
            if finder.kind(pm, line):
                continue
            if pm.number > 1 and line.top < _HEAD_BAND_MAX:
                head_lines.append(line)
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for l in rows[:10]):
        return NOTHING                    # ca9 always names itself

    crit: dict = {"headmatter_style": STYLE_RULED_BOX}
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
    stamp_lines: list = []                # the stamp rows the reader claims
    dates: dict = {}
    dockets: list[str] = []
    lower_dockets: list[str] = []
    titles: list[str] = []

    def emit(line, role: str, pm):
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=_align(line, pm, geom, body_size),
            x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    # ---- the masthead: everything page 1 prints above the first box -----
    first_box = boxes_by_page.get(1) or []
    if not first_box:
        return NOTHING
    head_top = first_box[0]["top"]
    for line in rows:
        if line.page != 1 or line.top >= head_top - _BAND_PAD:
            continue
        # THE CLERK'S STAMP IS A COLUMN, not a wording: 'FILED', the date,
        # the clerk's name and her office, all set flush right of the
        # banner. It is the court's filing apparatus, so it is read out
        # and then recorded as furniture.
        if line.x0 >= page1.width * _STAMP_X0:
            stamp_lines.append(line)
            consumed.add(line.id)
            continue
        text = _norm(line.plain)
        flag = _is_flag(text)
        if flag:
            crit.setdefault("publication_status", flag)
            emit(line, "court", page1)
        elif _is_banner(text):
            banner_rows.append(text)
            emit(line, "court", page1)
        else:
            # An unread masthead row means this is not the cover the
            # contract describes; core reads the whole document instead.
            return NOTHING

    band_max = body_size * _BAND_GAP      # a taller gap ends the band
    box_w = first_box[0]["x1"] - first_box[0]["x0"]

    def notes_top(pm) -> float:
        """Where this page's footnotes begin, or the page's foot.

        A reader that claims a region does NOT claim the notes under it:
        the marks belong to the rows above and core attaches them. What
        the reader has to do is not mistake a note for the row that ends
        the headmatter."""
        tops = [r.top for r in pm.h_rules
                if abs(r.x0 - body_x0) <= _SEP_MARGIN
                and r.width <= box_w - _SEP_NARROWER
                and r.top > pm.height * _SEP_MIN_DEPTH]
        return min(tops) if tops else float(pm.height)

    # ---- the walk: boxes and bands, in the order the page sets them ----
    stop = False
    state = "bands"
    carry: tuple | None = None            # (role, page) of the last band
    for pm in model.pages[:_MAX_PAGES]:
        if stop:
            break
        page_rows = [l for l in rows if l.page == pm.number]
        if not page_rows:
            continue
        for box in boxes_by_page.get(pm.number, []):
            band = (box["top"] - _BAND_PAD, box["bottom"] + _BAND_PAD)
            box_lines = [l for l in page_rows if band[0] <= l.top <= band[1]]
            if not box_lines:
                continue
            block, cap_left, cap_right = _caption(box_lines, box, pm, geom,
                                                  body_size)
            if block is None:
                continue
            # THE BOX'S OWN RULES render where the page draws them: a
            # reader that claims the region inherits the court's drawing,
            # and core only draws it for rows the reader left behind.
            span = "full" if box["x1"] >= pm.width * 0.8 else "left"
            items.append(m.Rule(prov=m.Prov(pm.number), span=span))
            items.append(block)
            items.append(m.Rule(prov=m.Prov(pm.number), span=span))
            consumed.update(block.prov.line_ids)
            caption_rows.extend(t for t in cap_left if t)
            for kind, group in _right_groups(cap_right):
                texts = [t for _r, t, _p in group]
                if kind == "docket":
                    dockets.append(_norm(" ".join(texts)).rstrip("."))
                    for r, _t, _p in group:
                        r.role = "docket"
                elif kind == "lower":
                    lower_dockets.append(_join_lower(texts))
                    for r, _t, _p in group:
                        r.role = "lower-court"
                elif kind == "label":
                    titles.append(_bare(" ".join(texts)).upper())
                    for r, _t, _p in group:
                        r.role = "title"
                else:
                    caption_rows.extend(texts)

        # ---- the bands below (and between) the boxes -------------------
        boxed = [(b["top"] - _BAND_PAD, b["bottom"] + _BAND_PAD)
                 for b in boxes_by_page.get(pm.number, [])]
        notes = notes_top(pm)
        free = [l for l in page_rows
                if l.id not in consumed and l.top < notes
                and not any(t <= l.top <= b for t, b in boxed)]
        if not free:
            continue
        # THE BAND IS THE UNIT OF MEANING, not the row: ca9 sets one
        # leading inside a statement and a full line between statements,
        # and the caption box measured that leading.
        bands: list = [[free[0]]]
        for a, b in zip(free, free[1:]):
            if (b.top - a.top) <= band_max:
                bands[-1].append(b)
            else:
                bands.append([b])
        for at, bd in enumerate(bands):
            first = _norm(bd[0].plain)
            printed = _norm(" ".join(_norm(l.plain) for l in bd))
            # A BAND INTERRUPTED BY THE PAGE BREAK continues at the top of
            # the next page: williams sets 'Submitted November 20, 2025*'
            # as the last row of page 1 and the place it was submitted at
            # as the first row of page 2. The continuation is recognized
            # by where the court set it — centred, at the top of the next
            # page, under a band that centres — never by reading the name
            # of a city.
            if (state == "bands" and at == 0 and carry is not None
                    and carry[0] in ("lower-court", "date")
                    and carry[1] == pm.number - 1
                    and not _opens_landmark(first)
                    and all(_align(l, pm, geom, body_size) is m.Align.CENTER
                            for l in bd)):
                if carry[0] == "date":
                    dates.update(_labelled_dates(_bare(printed)))
                else:
                    origin_rows.append(printed)
                for line in bd:
                    emit(line, carry[0], pm)
                carry = (carry[0], pm.number)
                continue
            # A BYLINE ENDS THE READER, always and everywhere.
            if any(parser.parse(_norm(l.plain)) for l in bd) \
                    and not _is_descriptor(first):
                stop = True
                break
            # THE COURT'S OWN FRONT MATTER is stepped over, not claimed.
            # Between the roster and the opinion the published slip prints
            # a staff summary and then the appearances; core assembles the
            # summary into the section the profile declares, and the
            # reader picks the walk back up at the appearances — which are
            # headmatter, and which a reader that stopped at the summary
            # would leave for the writing below it to swallow.
            if state == "front":
                if _is_counsel_label(first):
                    state = "counsel"
                    counsel_rows.append(printed)
                    for line in bd:
                        emit(line, "counsel", pm)
                continue
            if state == "counsel":
                # THE APPEARANCES END at the court's own fence — the label
                # it prints over the writing ('OPINION', 'ORDER'), which
                # is left standing as that writing's anchor.
                if _is_label_cell(first):
                    stop = True
                    break
                counsel_rows.append(printed)
                for line in bd:
                    emit(line, "counsel", pm)
                continue
            if _is_front_matter(first):
                state = "front"
                continue
            if _origin_opener(first):
                (history_rows if first.lower().startswith(_REHEARING)
                 else origin_rows).append(printed)
                for line in bd:
                    emit(line, "lower-court", pm)
                    judge = _trial_judge(line.plain)
                    if judge:
                        crit.setdefault("lower_court_judge", judge)
                carry = ("lower-court", pm.number)
                continue
            if _is_date_row(first):
                # THE VENUE RIDES WITH THE DATE. ca9 sets the place of
                # argument on the row under it, inside the same band.
                dates.update(_labelled_dates(_bare(printed)))
                for line in bd:
                    emit(line, "date", pm)
                carry = ("date", pm.number)
                continue
            if first.lower().startswith("before"):
                panel_rows.append(printed)
                for line in bd:
                    emit(line, "panel", pm)
                carry = ("panel", pm.number)
                continue
            # WHO WROTE WHAT is one statement per row, and the longest
            # of them wraps ('Partial Concurrence and Partial Dissent by
            # Judge S.R. / Thomas'). The band opens on a kind the court
            # names; its remaining rows are that band's, whatever they
            # say — which is the same rule every other band here follows.
            if _is_descriptor(first):
                for line in bd:
                    emit(line, "summary", pm)
                carry = ("summary", pm.number)
                continue
            stop = True               # a row this contract does not name
            break

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if titles:
        crit["title"] = titles[0]
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(caption_rows)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    if dockets:
        crit["docket_number"] = dockets[0]
        if dockets[1:]:
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
    # WHO WROTE WHAT is recorded by TAGGING the rows the court sets it on,
    # not by inventing a criterion for it. `disposition` is the ruling the
    # court made ('AFFIRMED IN PART, REVERSED IN PART, and REMANDED.'),
    # which core reads off the writing's own close; writing 'Opinion by
    # Judge McKeown' into that field would replace a fact with a different
    # one, and the model declares no field of its own for authorship.
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    for label, value in dates.items():
        if label in ("filed", "amended", "decided", "decided_and_filed",
                     "entered"):
            crit.setdefault("decision_date", value)
        else:
            crit.setdefault("submitted", value)

    # ---- the clerk's stamp: read, then recorded -------------------------
    # The DATE is read off the whole column, furniture rows included —
    # core recognizes 'JUN 12 2026' as a stamp and drops it before the
    # reader ever sees it, and the day the court filed the paper is the
    # one fact that column carries.
    stamp_text = _norm(" ".join(
        _norm(l.plain) for l in sorted(stamp_column, key=lambda l: l.top)))
    if stamp_text:
        hit = _STAMP_DATE.search(stamp_text)
        if hit:
            crit.setdefault("decision_date", _norm(hit.group(1)))
    if stamp_lines:
        stamp_lines.sort(key=lambda l: (l.top, l.x0))
        dropped.append(m.Dropped(
            text=_norm(" ".join(_norm(l.plain) for l in stamp_lines)),
            prov=m.Prov(stamp_lines[0].page,
                        tuple(l.id for l in stamp_lines)),
            kind="stamp"))

    # A CLAIM MUST BE TOTAL: the head rows the reader stepped over are
    # recorded, not silently swallowed — and only for the pages the claim
    # actually reached, so a head on a page the writing owns is untouched.
    last = max((l.page for l in rows if l.id in consumed), default=1)
    for line in head_lines:
        if line.page > last:
            continue
        dropped.append(m.Dropped(
            text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
            kind="running-head"))
        consumed.add(line.id)

    if not caption_rows:
        return NOTHING

    # WHAT THE PAPER IS, the court states in its own caption. A memorandum
    # disposition is the panel's decision of the appeal — unsigned, but an
    # opinion — and without the label an unbylined writing types as an
    # order by default.
    doc_type_final = None
    if titles:
        head = titles[0]
        if "ORDER" in head and "OPINION" not in head:
            doc_type_final = m.DocType.ORDER
        elif "OPINION" in head or "MEMORANDUM" in head:
            doc_type_final = m.DocType.OPINION

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": doc_type_final}
