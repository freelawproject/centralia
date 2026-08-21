"""United States Court of International Trade ('cit').

Everything unique to cit lives here. It imports core, never another court
file, and no other court file imports it.

THE PAPER. cit issues a numbered slip-opinion series, and every record in
the corpus opens the same way: the court's own slip number, then its name,
then a caption whose right-hand column carries the bench and the court
number, then what the paper calls itself, a bracketed statement of what the
court did, the day it was issued, the appearances, and the judge's byline.
Nothing else stands on the cover.

    Slip Op. 26-46                          the slip number — the court's
                                            own citation, not a docket
    UNITED STATES COURT OF INTERNATIONAL TRADE
    ─────────────────────────────────┐      the caption box's HEAD RULE
    ALOHA PENCIL COMPANY, LLC,       │
          Plaintiff,                 │  Before: Mark A. Barnett, Chief Judge
    v.                               │
    UNITED STATES,                   │  Court No. 25-00102
          Defendant,                 │
    and                              │
    CHINA FIRST PENCIL CO., LTD.,    │
          Defendant-Intervenors.     │
    ─────────────────────────────────┘      the FOOT RULE closes it
              OPINION AND ORDER             underlined, on the page axis
    [Granting Defendant's motion to dismiss …]
                          Dated: May 6, 2026
    Mark B. Lehnardt, Davis & Leiman, of Washington, DC, for Plaintiff …
    …
    Barnett, Chief Judge:  Plaintiff Aloha Pencil Company, LLC …

THREE PAPERS, ONE COVER. The court sets that cover on three kinds of stock,
and each states the caption's zones with a different drawing. The DISPATCH
is the drawing, never the wording:

  1. `ruled caption box` (26 of 31). A drawn VERTICAL rule with a drawn
     horizontal across its head and another across its foot — three strokes
     of one figure, exactly ca9's box. The horizontals run from the body
     rail to the vertical and stop there, so the figure is a backwards C
     and the caption's right-hand column is open to the measure. Left of
     the rule: the parties. Right of it: the bench and the court number.
     A CONSOLIDATED record stacks two cases inside one rule and shelves
     them apart with a third horizontal at the same measure (oregon), and a
     caption naming forty Canadian lumber producers runs the box over three
     pages (govt_of_canada).

  2. `typed colon rail` (2 of 31). The same cover typed rather than drawn:
     a row of underscores opens the caption, a column of ':' glyphs stands
     where the vertical would be, and a row of underscores ending in ':'
     closes it. Nothing is drawn at all.

  3. `reporter's measure` (3 of 31). The bound-volume setting: a 4.5-inch
     measure centred on the page, everything centred within it, and three
     short rules 145pt wide on the page axis fencing the zones — banner,
     then the court number, then the caption. cafc's contract exactly: the
     band between two fences is the court's own front matter, and the band
     under the last fence is where the writing begins.

WHAT IS AND IS NOT A RULE. The court underlines the paper's own name and
every lead attorney's name, and those underlines are drawn strokes like the
box is. They are told apart the way ca5 and ca1 tell them apart: A DRAWN
RULE WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT IS AN UNDERLINE, NOT A
FENCE. The box's head and foot span from the body rail to the vertical and
match no row; the reporter's fences are 145pt on the page axis and match no
row either.

THE DATE IS THE APPEARANCES' OPENING FENCE. cit gives its appearances no
label — an entry opens on counsel's name (underlined on the drawn stock,
italic on the typed and bound stock) and runs into the firm block for that
party — so something on the page has to say where they begin, and it is the
'Dated:' row: over the corpus every record that prints appearances prints
that row above them, and the one record that prints no date (neimenggu, a
JUDGMENT) prints no appearances either and opens its writing directly under
its title. Without that fence the reader would have read the judgment's
first paragraph as an appearance.

THE READER ENDS AT THE BYLINE — 'Barnett, Chief Judge:', 'Restani, Judge:'
— which cit sets with the opinion's first sentence running on from it. It
stands on page 1 (5 records), page 2 (24), page 3 or 4 (the two longest
captions). Where the paper carries no byline at all the reader stops at the
first row it cannot name, and the title it claimed goes to `anchor_ids` so
core can hand it back to open the writing.
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

# cit is one judge signing in prose with a TITLE-CASE surname — 'Barnett,
# Chief Judge:', 'Choe-Groves, Judge:' — and the opinion's first sentence
# runs on from the colon. Three-judge panels sit on the constitutional
# cases (oregon), so `single_writing` is NOT declared: a dissent here would
# be a real separate writing.
CIT = register(CourtProfile(
    "cit", "United States Court of International Trade",
    byline=BylineGrammar(
        style="prose",
        titles=("Chief Judge", "Senior Judge", "Judge"),
        allow_titlecase_name=True),
))

STYLE_RULED_BOX = "ruled caption box"
STYLE_COLON_RAIL = "typed colon rail"
STYLE_REPORTER = "reporter's measure"

# ---- cit's declared facts (measured over the corpus, not tuned) ---------
# THE BOX. Its vertical stands between 0.44 and 0.58 of the measure (297.2
# at the narrowest, 341.8 at the widest, on a 612pt page) and runs at least
# 130pt down; its head and foot run from the body rail to the vertical, so
# they are at least 200pt wide. Nothing else on the page draws a horizontal
# that long: the widest counsel underline in the corpus is 468pt but it
# COINCIDES with the row above it, which is what disqualifies it.
_BOX_VRULE_BAND = (0.40, 0.62)
_BOX_VRULE_MIN_H = 100.0
_BOX_RULE_MIN_W = 180.0
# HOW CLOSE THE STROKES OF ONE FIGURE COME. The court draws the box as three
# separate rects and does not always join them: measured over the corpus the
# vertical starts flush with the head on 23 records and 7.0pt below it on the
# other 3 (toyo, ningxia, qatar — the same chambers template). 12pt admits
# that gap; the nearest thing it could reach instead is a SHELF, and a shelf
# is never less than 100pt from the head because a caption stands between.
_BOX_JOIN = 12.0
# THE REPORTER'S FENCE: 145pt wide (144.2-145.4 measured), centred on the
# 612pt axis. The bound-volume setting draws nothing else.
_FENCE_WIDTH = (130.0, 160.0)
_FENCE_OFF_AXIS = 20.0
# AN UNDERLINE IS A RULE WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT. cit
# underlines the paper's name and every lead attorney's name; the tolerance
# is the stroke's own overhang.
_UNDERLINE_TOL = 4.0
_UNDERLINE_DROP = 22.0
# HOW FAR THE COVER MAY RUN. The longest caption in the corpus fills three
# pages and states its appearances on the fourth (govt_of_canada); six is
# two more than that, and the walk ends at the byline either way.
_MAX_PAGES = 6
# A WRAP IS ONE LEADING BELOW ITS OWN FIRST ROW. cit sets the cover on the
# body's own leading and stands the next statement a full paragraph below
# it, so 1.4 leadings separates a continuation from a new statement.
_WRAP_LEAD = 1.45
# The bracketed statement of what the court did runs to five rows at the
# most (american_brass_rod); eight is the bound.
_DISPOSITION_MAX_ROWS = 8
# A visual row is what the page printed on one line; pdfio splits a
# justified row at wide gaps and at the caption's vertical.
_ROW_BAND = 2.5
# THE TYPED RAIL IS A COLUMN. Its ':' glyphs stand within 24pt of one x
# (measured: 288.0-330.3 on ban_me_thuot, where the court indents the glyph
# by one tab on the rows that carry a party); a colon further off is the
# court's own punctuation.
_RAIL_COLUMN_TOL = 24.0

# THE COURT NAMES ITSELF on one row on the drawn and typed stock and on two
# in the bound setting. A closed set — the court's own name, never a test on
# anything it says about a case.
_BANNER = ("united states court of international trade",
           "united states", "court of international trade")
# THE SLIP NUMBER: 'Slip Op. 26-46'. It is the court's own published
# citation for the opinion, not a docket.
# (the court sets it 'Slip Op. 26-46' and, on one record, 'Slip Op. 26 - 54'
# with the rule spaced out — it is one short row either way)
_SLIP_OP = re.compile(r"^Slip\s+Op(?:inion)?\.?\s+(\S.{0,28})$", re.I)
# THE COURT NUMBER, as the caption's right-hand column and the running head
# print it: 'Court No. 25-00102', 'Consol. Court No. 23-00187',
# 'Court No. 26-01472-3JP', 'Ct. No. 25-00005'.
_COURT_NO = re.compile(
    r"^((?:Consol(?:idated)?\.?\s+)?(?:Court|Ct)\.?\s+Nos?\.\s*.+?)\s*$", re.I)
# THE DAY THE PAPER ISSUED. cit prints one label and one only.
_DATED = re.compile(r"^Dated:\s*(.+?)\.?\s*$", re.I)
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# WHAT THE PAPER CALLS ITSELF — a closed vocabulary of the labels cit sets
# alone, centred, and underlined on the page axis. Never a test on prose.
_LABEL_TITLE = (
    "OPINION", "OPINION AND ORDER", "ORDER", "ORDER AND OPINION",
    "JUDGMENT", "AMENDED OPINION", "CORRECTED OPINION", "MEMORANDUM",
    "MEMORANDUM AND ORDER", "SLIP OPINION", "OPINION AND JUDGMENT",
    "ERRATA", "PUBLIC VERSION", "AMENDED JUDGMENT",
)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. cit hyphenates its statuses ('Defendant-Intervenors') and
# qualifies them ('Consolidated Plaintiffs').
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "intervenor",
    "intervenors", "petitioner", "petitioners", "respondent", "respondents",
    "consolidated", "movant", "movants", "applicant", "applicants",
    "amicus", "amici", "appellant", "appellants", "appellee", "appellees",
)
_TITLE_WORDS = ("judge", "judges", "chief", "senior", "justice", "justices")
# A CORPORATE SUFFIX IS PART OF THE PARTY'S NAME, and cit sets it after a
# comma ('TOYO KOHAN CO., LTD.,', 'ALOHA PENCIL COMPANY, LLC,'). Cutting the
# name at its first comma renamed the plaintiff. A closed vocabulary of
# forms of incorporation — never a test on the name itself.
_CORP_SUFFIX = (
    "inc", "inc.", "llc", "l.l.c.", "llp", "l.l.p.", "ltd", "ltd.", "co",
    "co.", "corp", "corp.", "plc", "pllc", "p.c.", "l.p.", "lp", "n.a.",
    "s.a.", "s.a.s.", "a.s.", "a/s", "gmbh", "b.v.", "n.v.", "s.p.a.",
    "pvt", "pvt.", "jsc", "ulc", "ag", "sdn", "bhd", "de", "c.v.",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _flat_label(text: str) -> str:
    return _norm(text).rstrip(".:").upper()


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") in _BANNER


def _join(texts, vocab: set | None = None) -> str:
    """Join the rows of one band the way the page reads it.

    cit justifies its appearances and breaks on a hyphen at the row end;
    which hyphen it is cannot be seen in the row, so the DOCUMENT'S OWN
    VOCABULARY decides — the same discriminator core uses to join a wrapped
    paragraph, so the criteria and the rendered body cannot disagree about
    a broken word."""
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
                    if ch.isalpha() or ch in "’'":
                        word.append(ch)
                    else:
                        break
                head = piece.split()[0].strip(
                    "“”\"'’‘()[]{}.,;:!?")
                if word and ("".join(reversed(word)) + head).lower() in vocab:
                    out = out[:-1] + piece
                    continue
            out += piece
        else:
            out += " " + piece
    return out


def _ends_sentence(text: str) -> bool:
    flat = _norm(text).rstrip()
    while flat and flat[-1] in FOOTNOTE_LABEL_CHARS:
        flat = flat[:-1].rstrip()
    return flat.endswith((".", ":", "!", "?", "]"))


def _panel_names(text: str) -> list:
    """The judges named in a 'Before: …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test."""
    body = _norm(text)
    if body.lower().startswith("before"):
        body = body[len("before"):].lstrip(": ")
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        # The stop is NOT stripped here: 'Jr.' is a generational suffix and
        # the court prints it with its period.
        piece = chunk.strip()
        if not piece:
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            words = [w.strip(".,;").lower() for w in name.split()]
            if all(w in _TITLE_WORDS for w in words):
                continue
            # A trailing bench word rides on the last judge's name
            # ('Timothy C. Stanceu, Judges'); strip it, keep the name.
            while words and words[-1] in _TITLE_WORDS:
                name = " ".join(name.split()[:-1]).rstrip(",")
                words = words[:-1]
            if not name:
                continue
            # A GENERATIONAL SUFFIX is part of the judge's name, not another
            # judge, and the court prints its stop ('Joseph A. Laroski,
            # Jr., Judge') — so the name keeps the form the page set.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _sides(rows: list):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale —
    the status labels, the joiners and the pivot are apparatus, not names.
    A party that wraps over rows is joined back together, because cit sets
    a forty-name roll of exporters in a column two inches wide."""
    left: list = []
    right: list = []
    side = left
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        first = flat.split()[0].rstrip(".").lower()
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            continue
        bare = flat.rstrip(",. ").lower()
        if bare in ("and", "et al", "and,"):
            continue
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or w in ("and", "the", "of")
                         or not w for w in words):
            continue
        side.append(flat)
    def _name(rows_: list) -> str:
        if not rows_:
            return ""
        # The FIRST party named is the side's name; the rest of the roll is
        # the other producers joined into the same case.
        text = _join(rows_)
        head = text[:120]
        cut = 0
        while True:
            nxt = text.find(",", cut + 1)
            if nxt < 0 or nxt >= 120:
                break
            tail = text[nxt + 1:].lstrip()
            word = tail.split()[0].rstrip(",").lower() if tail.split() else ""
            if word in _CORP_SUFFIX:
                cut = nxt + 1 + len(tail) - len(tail.lstrip()) \
                    + len(tail.split()[0])
                continue
            head = text[:nxt]
            break
        else:
            head = text[:cut] if cut else head
        if cut and cut >= len(head):
            head = text[:cut]
        return head.strip().rstrip(",")
    return _name(left), _name(right)


# --------------------------------------------------------------------------
# a VISUAL ROW is what the page printed on one line
# --------------------------------------------------------------------------

def _visual_rows(lines: list) -> list:
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


# --------------------------------------------------------------------------
# the three drawings — the dispatch
# --------------------------------------------------------------------------

def _underlines(pm) -> set:
    """The rules on ``pm`` that UNDERLINE the row above them.

    A drawn stroke whose ends coincide with a printed row a line-height
    above it is that row's underline, not a fence. cit underlines what the
    paper calls itself and every lead attorney's name."""
    out = set()
    for rule in pm.h_rules:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            drop = rule.top - line.top
            if not (0 < drop <= _UNDERLINE_DROP):
                continue
            if abs(line.x0 - rule.x0) <= _UNDERLINE_TOL \
                    and abs(line.x1 - rule.x1) <= _UNDERLINE_TOL:
                out.add(id(rule))
                break
    return out


def _drawn_boxes(pm) -> list:
    """The caption boxes drawn on ``pm``, top-first.

    A box is a VERTICAL rule with a horizontal across its head and another
    across its foot: three strokes of one figure. An interior horizontal at
    the same measure is a SHELF — a consolidated record stacks two cases
    inside one figure and shelves them apart."""
    skip = _underlines(pm)
    lo, hi = pm.width * _BOX_VRULE_BAND[0], pm.width * _BOX_VRULE_BAND[1]
    rules = [r for r in pm.h_rules
             if r.width >= _BOX_RULE_MIN_W and id(r) not in skip]
    out: list = []
    for v in pm.v_rules:
        if v.height < _BOX_VRULE_MIN_H or not lo < v.x < hi:
            continue
        heads = [r for r in rules if abs(r.top - v.top) <= _BOX_JOIN
                 and r.x1 >= v.x - _BOX_JOIN]
        feet = [r for r in rules if abs(r.top - v.bottom) <= _BOX_JOIN
                and r.x1 >= v.x - _BOX_JOIN]
        if not (heads and feet):
            continue
        top = min(r.top for r in heads)
        bottom = max(r.top for r in feet)
        shelves = sorted(r.top for r in rules
                         if top + _BOX_JOIN < r.top < bottom - _BOX_JOIN
                         and r.x1 >= v.x - _BOX_JOIN)
        out.append({"x": float(v.x), "top": top, "bottom": bottom,
                    "shelves": shelves, "page": pm.number})
    out.sort(key=lambda b: b["top"])
    return out


def _typed_box(pm) -> list:
    """The same cover TYPED: a row of underscores opens the caption, a
    column of ':' stands where the vertical would be, and a row of
    underscores ending in ':' closes it."""
    typed = [l for l in pm.lines
             if l.plain.strip() and set(l.plain.strip()) <= {"_"}
             and len(l.plain.strip()) >= 10]
    closer = [l for l in pm.lines
              if l.plain.strip() and set(l.plain.strip()) <= {"_", ":"}
              and l.plain.strip().count("_") >= 10 and ":" in l.plain]
    if not typed:
        return []
    colons = [l for l in pm.lines if l.plain.strip().strip(": ") == ""
              and ":" in l.plain]
    if len(colons) < 4:
        return []
    top = min(l.top for l in typed)
    bottom = max((l.top for l in closer), default=max(l.top for l in colons))
    if bottom <= top:
        return []
    xs = sorted(l.x0 for l in colons)
    return [{"x": xs[len(xs) // 2], "top": top - 1.0, "bottom": bottom + 1.0,
             "shelves": [], "page": pm.number, "rail": ":"}]


def _fences(pm) -> list:
    """The bound setting's typed zone rules: 145pt on the page axis, and
    never an underline."""
    skip = _underlines(pm)
    out = []
    for r in pm.h_rules:
        if id(r) in skip:
            continue
        if not (_FENCE_WIDTH[0] <= r.width <= _FENCE_WIDTH[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_OFF_AXIS:
            continue
        out.append(r.top)
    return sorted(out)


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

@decider("headmatter.read", court="cit")
def read_headmatter_cit(model, geom, **_):
    """Read cit's cover, or NOTHING.

    NOTHING is returned for anything that is not one of the three papers
    above: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    lead = (geom.lead if geom and geom.lead else 14.0)
    vocab = learn_vocabulary(model)
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CIT.byline)
    pages = {pm.number: pm for pm in model.pages}
    scanned = model.pages[:_MAX_PAGES]

    lines: list = []
    for pm in scanned:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            lines.append(line)
    if not lines:
        return NOTHING
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    by_page: dict = {}
    for line in lines:
        by_page.setdefault(line.page, []).append(line)

    # THE COURT NAMES ITSELF FIRST. Without that row this is not cit's
    # cover and the reader has nothing to say.
    first_rows = _visual_rows(by_page.get(1, []))[:5]
    if not any(_is_banner(_plain(r)) for r in first_rows):
        return NOTHING

    # ---- the dispatch: which drawing states the caption's zones ---------
    boxes: list = []
    style = None
    page1 = pages[1]
    drawn = _drawn_boxes(page1)
    if drawn:
        style = STYLE_RULED_BOX
        boxes = list(drawn)
        # THE CAPTION MAY RUN OVER THE PAGE. It does so only where the box
        # reaches the page's foot; the next page then opens its own box at
        # the head of the measure.
        pageno = 1
        while boxes and boxes[-1]["bottom"] > pages[pageno].height * 0.85 \
                and pageno + 1 in pages and pageno + 1 <= len(scanned):
            pageno += 1
            nxt = _drawn_boxes(pages[pageno])
            if not nxt or nxt[0]["top"] > pages[pageno].height * 0.20:
                break
            boxes.extend(nxt)
    else:
        typed = _typed_box(page1)
        if typed:
            style = STYLE_COLON_RAIL
            boxes = typed
    fences: list = []
    if style is None:
        fences = _fences(page1)
        if len(fences) >= 2:
            style = STYLE_REPORTER
    if style is None:
        return NOTHING

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list = []
    banner_rows: list = []
    caption_rows: list = []
    panel_groups: list = []
    counsel_rows: list = []
    disposition_rows: list = []
    dockets: list = []
    dates: list = []
    slip: list = []

    def emit(row: list, role: str, rel_from: float = 0.0):
        first = row[0]
        pm = pages[first.page]
        align = line_alignment(first, pm.width, geom,
                               banner_center_min_size=body_size + 1.0)
        rel = 0.0
        if rel_from and align == "L" and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=_markup(row), prov=m.Prov(first.page,
                                           tuple(l.id for l in row)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(l.all_bold for l in row), rel=rel, role=role))
        consumed.update(l.id for l in row)
        return items[-1]

    def _read_masthead(row: list):
        """The rows the court prints above its caption: the slip number it
        publishes the opinion under, and its own name."""
        text = _plain(row)
        if _SLIP_OP.match(text):
            slip.append(_norm(text))
            emit(row, "citation")
        elif _is_banner(text):
            banner_rows.append(text)
            emit(row, "court")
        else:
            emit(row, "case-info")

    def cell(cells: list, role: str, pm):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align(line_alignment(
                first, pm.width, geom,
                banner_center_min_size=body_size + 1.0)),
            x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    def caption_block(band_lines: list, box: dict, pm):
        """One caption band as a CaptionBlock, cells PAIRED BY VISUAL ROW.

        Column membership is decided by which side of the drawing a cell
        sits on — never by what the cell says. The rail's own glyphs ARE
        the rail on the typed stock, not content."""
        mid = box["x"]
        rail = box.get("rail")
        rows: list = []
        for line in sorted(band_lines, key=lambda l: (l.top, l.x0)):
            if rail and line.plain.strip().strip(rail + " _") == "":
                consumed.add(line.id)
                continue
            if rows and abs(rows[-1][0].top - line.top) <= _ROW_BAND:
                rows[-1].append(line)
            else:
                rows.append([line])
        cells_l: list = []
        cells_r: list = []
        left_plain, right_plain = [], []
        for row in rows:
            l_cells = [l for l in row if (l.x0 + l.x1) / 2 < mid]
            r_cells = [l for l in row if l not in l_cells]
            if rail:
                l_cells = [_strip_rail(l, rail, mid) for l in l_cells]
                r_cells = [_strip_rail(l, rail, mid) for l in r_cells]
                l_cells = [l for l in l_cells if l is not None]
                r_cells = [l for l in r_cells if l is not None]
            if not l_cells and not r_cells:
                continue
            cells_l.append(l_cells)
            cells_r.append(r_cells)
            left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
        # THE RIGHT COLUMN IS NOT MORE CAPTION. It carries the bench and the
        # court number, and a cell is named for what it is — the block still
        # renders as the page set it, but nothing in it goes unread.
        roles_r = ["caption"] * len(right_plain)
        open_role = None
        for k, text in enumerate(right_plain):
            if not text:
                open_role = None
                continue
            if _COURT_NO.match(text):
                roles_r[k] = open_role = "docket"
            elif text.lower().startswith("before"):
                roles_r[k] = open_role = "panel"
            elif open_role and right_plain[k - 1].rstrip().endswith(","):
                roles_r[k] = open_role
            else:
                open_role = None
        left = [cell(c, "caption", pm) if c
                else m.HmLine(text="", prov=m.Prov(pm.number), role="caption")
                for c in cells_l]
        right = [cell(c, roles_r[k], pm) if c
                 else m.HmLine(text="", prov=m.Prov(pm.number),
                               role=roles_r[k])
                 for k, c in enumerate(cells_r)]
        # THE RIGHT COLUMN CARRIES THE BENCH AND THE COURT NUMBER, and it is
        # read as such wherever in the column the court set it. A caption
        # that runs over the page opens a box with the parties alone in it;
        # a column of empty cells is not a column and renders as one blank
        # row per party.
        # ONE BOX, ONE ROSTER. A consolidated record sets one box per case
        # and states the SAME bench in each of them; joined together they
        # read as six judges sitting twice. The column's own landmarks close
        # the roster: a THREE-JUDGE bench wraps to a second row and the
        # court leaves the first ending in a comma, so the comma is what
        # says the statement runs on — never mere adjacency, which swallowed
        # the court number sitting two rows below it.
        bench: list = []
        for text in right_plain:
            if not text:
                continue
            mm = _COURT_NO.match(text)
            if mm:
                if bench:
                    panel_groups.append(list(bench))
                    bench = []
                dockets.append(mm.group(1))
                continue
            if text.lower().startswith("before"):
                if bench:
                    panel_groups.append(list(bench))
                bench = [text]
                continue
            if bench and bench[-1].rstrip().endswith(","):
                bench.append(text)
        if bench:
            panel_groups.append(bench)
        caption_rows.extend(t for t in left_plain if t)
        if not any(right_plain):
            right = []
        block = m.CaptionBlock(
            left=left, right=right, rail=rail or "|", rail_rows=len(left),
            style_id="backwards-c" if not rail else "colon-rail",
            fp={"rail": rail or "drawn", "mid_x": mid,
                "rail_band": (box["top"], box["bottom"])},
            prov=m.Prov(pm.number, tuple(sorted(l.id for l in band_lines))))
        items.append(block)
        consumed.update(l.id for l in band_lines)

    def _strip_rail(line, rail: str, mid: float):
        """Drop the rail's own glyphs out of a cell.

        On the typed stock the ':' column rides on the party rows themselves
        ('Plaintiffs,  :'), so the glyph has to come out — but only where it
        IS the rail. A colon anywhere else on the row is the court's own
        punctuation ('Before: Richard K. Eaton, Judge'), and stripping by
        GLYPH rather than by POSITION took that one too. The rail is a
        column: a glyph belongs to it when it stands at the column's x.""" 
        keep = [c for c in line.chars
                if not ((c.get("text") or "").strip() == rail
                        and abs((c["x0"] + c.get("x1", c["x0"])) / 2 - mid)
                        <= _RAIL_COLUMN_TOL)
                and (c.get("text") or "") != ""]
        if not any((c.get("text") or "").strip() for c in keep):
            return None
        if len(keep) == len(line.chars):
            return line
        from dataclasses import replace as _replace
        return _replace(line, chars=keep,
                        x0=min(c["x0"] for c in keep),
                        x1=max(c.get("x1", c["x0"]) for c in keep))

    # ---- the zones ------------------------------------------------------
    tail_rows: list = []
    if style in (STYLE_RULED_BOX, STYLE_COLON_RAIL):
        box_pages = {b["page"] for b in boxes}
        first_box = boxes[0]
        for pm in scanned:
            page_lines = by_page.get(pm.number, [])
            if not page_lines:
                continue
            here = [b for b in boxes if b["page"] == pm.number]
            if not here:
                if pm.number < max(box_pages, default=1):
                    continue
                tail_rows.extend(_visual_rows(page_lines))
                continue
            for line in page_lines:
                if pm.number == first_box["page"] \
                        and line.top < first_box["top"]:
                    continue                      # the banner, read below
                if any(b["top"] <= line.top <= b["bottom"] for b in here):
                    continue                      # the caption, read below
                if line.top > here[-1]["bottom"]:
                    tail_rows.append([line])
            # the banner rows above the first box
            if pm.number == first_box["page"]:
                for row in _visual_rows([l for l in page_lines
                                         if l.top < first_box["top"]]):
                    _read_masthead(row)
            for box in here:
                edges = [box["top"]] + list(box["shelves"]) + [box["bottom"]]
                for lo_, hi_ in zip(edges, edges[1:]):
                    band = [l for l in page_lines if lo_ <= l.top <= hi_]
                    if band:
                        caption_block(band, box, pm)
                    if hi_ != box["bottom"]:
                        items.append(m.Rule(prov=m.Prov(pm.number),
                                            span="left"))
        tail_rows = _visual_rows([l for row in tail_rows for l in row])
    else:
        # THE BOUND SETTING FENCES ITS ZONES. A band closed above and below
        # is the court's own front matter, whatever it says; the band under
        # the last fence is where the writing begins.
        page_lines = by_page.get(1, [])
        edges = [0.0] + fences + [page1.height]
        for i, (lo_, hi_) in enumerate(zip(edges, edges[1:])):
            band = [l for l in page_lines if lo_ < l.top <= hi_]
            rows = _visual_rows(band)
            closed = i < len(fences)
            if not closed:
                tail_rows.extend(rows)
                continue
            for row in rows:
                text = _plain(row)
                if not caption_rows and (_SLIP_OP.match(text)
                                         or _is_banner(text)):
                    # 'UNITED STATES' is this court's name ABOVE the caption
                    # and the defendant's name INSIDE it. Position decides.
                    _read_masthead(row)
                elif _COURT_NO.match(text):
                    dockets.append(_COURT_NO.match(text).group(1))
                    emit(row, "docket")
                elif text.lower().startswith("before"):
                    panel_groups.append([text])
                    emit(row, "panel")
                else:
                    caption_rows.append(text)
                    emit(row, "caption")
            items.append(m.Rule(prov=m.Prov(1), span="center"))
        for pm in scanned[1:]:
            tail_rows.extend(_visual_rows(by_page.get(pm.number, [])))

    # ---- the tail: title, disposition, date, appearances, byline --------
    seen_dated = False
    i = 0
    while i < len(tail_rows):
        row = tail_rows[i]
        text = _plain(row)
        low = text.lower()
        parsed = parser.parse(text)
        if parsed is not None and text[:parsed.end].rstrip().endswith(":"):
            break                       # the first byline ends the reader
        if _flat_label(text) in _LABEL_TITLE:
            crit.setdefault("title", _flat_label(text))
            item = emit(row, "title")
            anchor_ids.extend(item.prov.line_ids)
            i += 1
            continue
        if text.startswith("["):
            end = i
            while end < len(tail_rows) and end - i < _DISPOSITION_MAX_ROWS:
                if _plain(tail_rows[end]).rstrip().endswith("]"):
                    break
                end += 1
            for r2 in tail_rows[i:end + 1]:
                disposition_rows.append(_plain(r2))
                emit(r2, "disposition")
            i = end + 1
            continue
        dm = _DATED.match(text)
        if dm:
            dates.append(_norm(dm.group(1)))
            emit(row, "date")
            seen_dated = True
            i += 1
            continue
        if low.startswith("before"):
            end = _run_on(tail_rows, i, lead)
            panel_groups.append([_plain(r2) for r2 in tail_rows[i:end + 1]])
            for r2 in tail_rows[i:end + 1]:
                emit(r2, "panel")
            i = end + 1
            continue
        if _COURT_NO.match(text):
            dockets.append(_COURT_NO.match(text).group(1))
            emit(row, "docket")
            i += 1
            continue
        if _is_section_head(row, pages[row[0].page]):
            break                      # the writing's own first heading
        if seen_dated:
            # THE APPEARANCES. cit labels them not at all — the date above
            # them is the fence, and the byline below them is the end.
            counsel_rows.append(text)
            emit(row, "counsel", rel_from=body_x0)
            i += 1
            continue
        break                          # a row this contract does not name

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _join(banner_rows)
    if slip:
        crit["citation"] = slip[0]
    if caption_rows:
        crit["caption"] = caption_rows
        first, second = _sides(caption_rows)
        if first and second:
            crit["parties"] = [first, second]
            crit["case_name"] = f"{first} v. {second}"
        elif first:
            crit["parties"] = [first]
            crit["case_name"] = first
    if dockets:
        crit["docket_number"] = dockets[0]
        others = []
        for value in dockets[1:]:
            if value != dockets[0] and value not in others:
                others.append(value)
        if others:
            crit["other_dockets"] = others
    rosters: list = []
    for group in panel_groups:
        printed = _join(group, vocab)
        if printed and printed not in rosters:
            rosters.append(printed)
    if rosters:
        printed = "; ".join(rosters)
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if disposition_rows:
        printed = _join(disposition_rows, vocab).strip()
        crit["disposition"] = printed.strip("[]").strip()
    if dates:
        crit["decision_date"] = dates[0]
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _join(counsel_rows, vocab)[:4000]

    # A CLAIM MUST BE TOTAL. The reader steps over the court's stationery
    # rather than claiming it: core's furniture pass already measured the
    # running head and the folio and recorded both as removals, and a second
    # record of the same row would report it twice.
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _is_section_head(row: list, pm) -> bool:
    """A row the court set as a HEADING of its own writing ('BACKGROUND',
    'JURISDICTION AND STANDARD OF REVIEW'): capitals, alone, centred on the
    page axis. It bounds the appearances on a paper that carries no byline
    at all — nothing in an appearance is ever set that way."""
    text = _plain(row)
    letters = [c for c in text if c.isalpha()]
    if not letters or not all(c.isupper() for c in letters):
        return False
    if len(text) > 60:
        return False
    first = row[0]
    last = row[-1]
    return abs((first.x0 + last.x1) / 2 - pm.width / 2) <= 30.0


def _run_on(rows: list, i: int, lead: float) -> int:
    """How far a statement WRAPS. It ends on a full stop, at a page turn,
    or a full paragraph below its own first row."""
    k = i
    while k + 1 < len(rows):
        here, nxt = rows[k], rows[k + 1]
        if _ends_sentence(_plain(here)):
            break
        if nxt[0].page != here[0].page:
            break
        if nxt[0].top - here[0].top > _WRAP_LEAD * lead:
            break
        k += 1
    return k
