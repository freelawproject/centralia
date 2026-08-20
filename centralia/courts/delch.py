"""Court of Chancery of the State of Delaware ('delch').

Everything unique to delch lives here. It imports core, never another court
file, and no other court file imports it — not `del.py`, whose section-rail
Delaware is a different paper, and not `delsuperct.py`, which prints the
same two formats and keeps its own copy of the reading.

THE COURT PUBLISHES TWO PAPERS, and it says which by its MASTHEAD. Counted
over all 42 records, page 1, first inked row:

    IN THE COURT OF CHANCERY OF THE STATE OF DELAWARE     27   the CAPTION
    COURT OF CHANCERY / OF THE / STATE OF DELAWARE        15   the LETTER

There is no third form and no record that prints neither.

FORMAT 1 — THE CAPTIONED PAPER (27 records). A two-column box under the
one-line masthead, a bold centred title, the court's own dates, the
appearances, and the byline that opens the writing:

    ┌─────────────────────────────────────────────────────────────────┐
    │      IN THE COURT OF CHANCERY OF THE STATE OF DELAWARE          │
    │  SHALOMYAH BOWERS,          )                                   │
    │                             )                                   │
    │       Plaintiff,            )                                   │
    │                             )                                   │
    │     v.                      )                                   │
    │                             )  C.A. No. 2026-0006-DH            │
    │  BLACK LIVES MATTER GLOBAL  )                                   │
    │  NETWORK FOUNDATION, INC.,  )                                   │
    │       Defendant.            )                                   │
    │                                                                 │
    │                        REPORT                                   │  bold, centred
    │                 Report: July 13, 2026                           │  the court's dates
    │             Date Submitted: April 20, 2026                       │
    │  Rebecca L. Butcher, … LANDIS RATH & COBB LLP, Wilmington,      │  the appearances
    │  Delaware; … Attorneys for Plaintiff Shalomyah Bowers.          │
    │  WILL, Vice Chancellor                                          │  …and the writing
    └─────────────────────────────────────────────────────────────────┘

THE DIVIDER COMES TWO WAYS AND THE PAGE SAYS WHICH — the ca6 standard: read
the drawn mark, never the wording. Measured over the 27 captioned records,
page 1, the split is total and there is no record that has both or neither:

    typed ')' column      17 records   x0 296.8-356.5, mode per record
    drawn vertical rect   10 records   x  278.8-324.8, one rect per page

Both sit within 28pt of the 306pt page axis, so the mark is the rail
wherever it was found and the columns split at ITS x, not at the axis.

THE GLYPH IS NOT ALWAYS A PIECE OF ITS OWN. pdfio returns
`') C.A. No. 2026-0006-DH'` as ONE line beginning at the rail
(shalomyah_bowers), and elsewhere glues it to the END of the left column.
So the rail is located from the ')' CHARS, the row is split at that x, and
the glyph is shed by its COLUMN — never by its character, because a ')'
that closes real text is not in the rail's column. (This is the del.py
lesson, restated: testing for a bare glyph found the column and skipped
every row that carried the docket.)

THE BOX CAN SPAN TWO PAGES. `advent_international` names 47 party entities:
its box runs the whole of page 1, closes at top 492.7 on page 2, and its
byline stands at the FOOT of page 3 (top 692.0) with the appearances between
them. A reader that looked only at page 1 read the record as NOTHING —
there is no docket, no title and no date on that page. So the walk runs to
the byline, over as many as three pages, and the box closes where its rail
stops.

THE RIGHT COLUMN CARRIES ONE TENANT: this court's own docket, and no 'Court
Below' row (contrast del, where the court below stands in the same column).
It is written four ways —

    C.A. No. 2026-0006-DH              the ordinary form
    Consolidated C.A. No. / 2021-0447-KSJM   LABEL and NUMBER on two rows
    Cr. ID No. …  /  I.D. No. …        the criminal forms
    C.A. No. N25C-12-001 KMM / CCLD    a trailing complex-litigation tag

— so a right-hand row that is a bare identifier continues the docket above
it rather than opening a role of its own.

FORMAT 2 — THE LETTER RULING (15 records). The court writes on its own
letterhead, and the letterhead is THREE COLUMNS on shared rows: the officer
at the left, the masthead centred, the courthouse address at the right.
pdfio splits them, so the parts are read as LINES, not as rows:

    ┌─────────────────────────────────────────────────────────────────┐
    │                    COURT OF CHANCERY                            │  court
    │  KATHALEEN ST. JUDE MCCORMICK      OF THE   LEONARD L. WILLIAMS │  author │ court │
    │  CHANCELLOR               STATE OF DELAWARE  500 N. KING STREET │  letterhead
    │                                          WILMINGTON, DE 19801   │
    │                      August 11, 2026                            │  date
    │  Tonya Frazier              Claudetta Frazier                   │  the addressees,
    │  518 Lafayette Boulevard    607 N. Washington Street            │  two columns
    │  Wilmington, DE 19801       Milford, DE 19963                   │
    │  Re:  Tonya Frazier v. Michael Frazier and Claudetta Frazier,   │  caption
    │       C.A No. 2025-0431-CCB (KSJM)                              │  docket
    │  Dear Parties:                                                  │  …and the letter
    └─────────────────────────────────────────────────────────────────┘

THE SALUTATION OPENS THE BODY, which is the v1 reading and the only one the
page supports: the letter IS the opinion, and it is signed at its foot
('/s/ Kathaleen St. Jude McCormick'). The corpus writes the salutation five
ways — 'Dear Counsel:', 'Dear Counsel,', 'Dear Parties:', 'Dear Ms.
Carlisle and Counsel:', and the bare 'Counsel:' — so it is matched on its
opening word, not on a fixed string. Everything above it is headmatter;
nothing below it is touched.

THE COURTHOUSE ADDRESS IS DROPPED as letterhead (the vt.py precedent): it
is the stationery, not the ruling. It is dropped, never deleted — the
coverage oracle sees it accounted for.

WHAT THIS FILE DOES NOT DO. It reads the block above the writing and
nothing else: the byline grammar (Chancery abbreviates 'V.C.', 'C.' and
'M.' and signs in title case as well as caps), the conformed '/s/'
signature that authors an unsigned order, the footnote zones and the
paragraphing are all core's, and are configured on the profile in
courts/__init__.py.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# ---- what the mastheads say ------------------------------------------------

_MAST_BOX = re.compile(
    r"^IN THE COURT OF CHANCERY (?:OF|FOR) THE STATE OF DELAWARE$", re.I)
# The letterhead's own rows, spaces squeezed out: 'OFTHE' and
# 'STATEOFDELAWARE' come back unspaced on some records (tonya_frazier).
_MAST_LETTER = "COURTOFCHANCERY"
_MAST_LETTER_TAIL = ("OFTHE", "STATEOFDELAWARE")
_COURT_NAME = "Court of Chancery of the State of Delaware"

# ---- the captioned paper --------------------------------------------------

_RAIL_GLYPH = ")"
_RAIL_WINDOW = 6.0          # a char this close to the rail's x IS the rail
_RAIL_OFF_AXIS = 60.0       # …and the rail stands this close to the axis
_RAIL_FLOOR = 2             # in_re_swervepay's whole box is two rows
# The caption's own leading is 14-16pt; a gap wider than this is not the
# next row of the same rail.
_RAIL_GAP_MAX = 60.0
_MAX_PAGES = 3              # advent's byline stands on page 3

# THE DOCKET, four ways (see the docstring). The label is matched without
# its punctuation because the court writes both 'C.A. No.' and 'C.A No.'.
_DOCKET_BODY = (
    r"(?:Consolidated\s+|Coordinated\s+|Lead\s+|Master\s+)?"
    r"(?:C\.\s?A\.?|Cr\.\s?A\.?|Cr\.\s?ID|I\.?\s?D\.?|Civil\s+Action|Case|File)"
    r"\s*(?:Nos?\.?|ID)\s*")
_DOCKET = re.compile(rf"^{_DOCKET_BODY}(.*)$", re.I)
# THE SAME LABEL, WHEREVER IT STANDS. A 'Re:' block runs its case name on
# and the docket rides the last line ('Securities LLC, C.A. No.
# 2025-1133-DG'), so that row needs the unanchored form — and only that row
# gets it, because unanchored the label matches a citation in prose too.
_DOCKET_ANY = re.compile(rf"\b{_DOCKET_BODY}(\S.*)$", re.I)
# A bare identifier under a docket continues it: '2021-0447-KSJM', 'CCLD'.
_DOCKET_TAIL = re.compile(r"^[0-9A-Z][0-9A-Za-z().\- /]{2,40}$")
# The court's own dates. 'Report:' and 'Final Report:' date a magistrate's
# report, which is the only date some of those records print.
_DATE_LABEL = re.compile(
    r"^(?:Date\s+(?:of\s+)?)?(Submitted|Decided|Argued|Reargued|Revised"
    r"|Corrected|Filed|Final\s+Report|Draft\s+Report|Report)\s*:\s*(.+)$",
    re.I)
_DATE_CRIT = {"decided": "decision_date", "submitted": "submitted",
              "argued": "submitted", "reargued": "submitted",
              "report": "decision_date", "final report": "decision_date",
              "draft report": "decision_date", "revised": "decision_date",
              "corrected": "decision_date", "filed": "decision_date"}
_DISPO = re.compile(
    r"\b(GRANTED|DENIED|AFFIRMED|REVERSED|VACATED|REMANDED|DISMISSED"
    r"|MODIFIED|SUSTAINED|OVERRULED)\b")
# The appearances name themselves. A runover row need not, so the block is
# closed by its LAST landmark and the sentence it leaves unfinished.
# THE APPEARANCES NAME THEMSELVES — a firm, an 'Esquire', or who counsel
# appears for. 'pro se' and 'Wilmington, Delaware' are NOT on this list: an
# order's own first paragraph says 'pro se Motion for Sentence Modification'
# and would have been read as a roster.
_COUNSEL = re.compile(
    r"\b(?:Esquire|Esq\.|LLP|PLLC|P\.A\.|LLC|Attorneys?\s+for"
    r"|Counsel\s+for|Appearing\s+for|Attorney\s+for)\b")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_STATUS = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Counterclaim[- ]\w+|Nominal\s+\w+|Intervenors?)"
    r"(?:\s+Below)?[,.]?$", re.I)
# 'WILL, Vice Chancellor' / 'LASTER, V.C.' / 'Cook, V.C.' / 'McCORMICK, C.'
# / 'WRIGHT, M.' / 'Miller, J.' — caps and title case both, and the period
# is optional. This is the STOP, not the parse: core's grammar reads it.
_BYLINE = re.compile(
    r"^(?:Mc|Mac|St\.\s?)?[A-Z][A-Za-z’'\-]+(?:\s+[A-Z][A-Za-z’'\-]+)?"
    # A GENERATION IS PART OF THE NAME: 'HUME, IV, M.' is one byline, and
    # read without this it was not a byline at all — the walk ran past it
    # and the appearances above it were never closed.
    r"(?:,\s*(?:Jr\.|Sr\.|II|III|IV|V))?"
    r",\s*"
    r"(?:V\.\s?C\.|C\.|M\.|J\.|Vice\s+Chancellor|Chancellor"
    r"|Magistrate(?:\s+in\s+Chancery)?|Master(?:\s+in\s+Chancery)?"
    r"|Judge|Justice)\s*[.:]?$")

# ---- the letter ruling ----------------------------------------------------

# The officer's title, as the letterhead prints it.
_BENCH_TITLE = re.compile(
    r"^(?:CHANCELLOR|VICE\s+CHANCELLOR|MAGISTRATE\s+IN\s+CHANCERY"
    r"|MASTER\s+IN\s+CHANCERY|RESIDENT\s+JUDGE|JUDGE|COMMISSIONER)$", re.I)
_TITLE_CASE = {
    "CHANCELLOR": "Chancellor",
    "VICE CHANCELLOR": "Vice Chancellor",
    "MAGISTRATE IN CHANCERY": "Magistrate in Chancery",
    "MASTER IN CHANCERY": "Master in Chancery",
    "RESIDENT JUDGE": "Resident Judge",
    "JUDGE": "Judge",
    "COMMISSIONER": "Commissioner",
}
_LETTER_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_RE_LINE = re.compile(r"^Re\s*:\s*(.*)$", re.I)
_SALUTATION = re.compile(r"^(?:Dear\b.*|Counsel|Parties|Ladies\s+and\s+Gentlemen)\s*[:,]?$")
_LETTERHEAD_ROW = re.compile(
    r"JUSTICE\s+CENTER|COURTHOUSE|KING\s+STREET|THE\s+GREEN|MARKET\s+STREET"
    r"|WILMINGTON,\s+DE|DOVER,\s+DE|GEORGETOWN,\s+DE|SUITE|Telephone|\(302\)",
    re.I)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    return "".join((text or "").split()).upper()


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _typed_rail(pm) -> dict | None:
    """The ')' column, or None.

    A rail is a COLUMN — glyphs stacked at one x — not a count of parens
    anywhere on the page, and it is SEEDED from the glyphs that stand at a
    line's own edge. The rail's ')' is always alone on its line, or glued to
    one end of it (') C.A. No. 2026-0006-DH' opens a line; 'CAMDEN FOLEY and
    SAMUEL )' closes one); a parenthesis inside prose ('(the "Motion")') is
    not. Once the column is known, membership is by column, grown outward
    one contiguous step at a time so a prose paren further down the page is
    still barred by the gap bound (the moctapp reading).
    """
    edge = []
    for line in pm.lines:
        inked = [c for c in line.chars if (c.get("text") or "").strip()]
        for c in (inked[:1] + inked[-1:]):
            if (c.get("text") or "") == _RAIL_GLYPH:
                edge.append(c)
    if len(edge) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in edge).most_common(1)[0]
    if abs(x - pm.width / 2) > _RAIL_OFF_AXIS:
        return None
    seed = sorted((c for c in edge if abs(c["x0"] - x) <= 3.0),
                  key=lambda c: c["top"])
    if len({round(c["top"], 1) for c in seed}) < _RAIL_FLOOR:
        return None
    column = sorted((c for line in pm.lines for c in line.chars
                     if (c.get("text") or "") == _RAIL_GLYPH
                     and abs(c["x0"] - x) <= 3.0),
                    key=lambda c: c["top"])
    run = [c for c in column
           if seed[0]["top"] - 0.5 <= c["top"] <= seed[-1]["top"] + 0.5]
    for ch in reversed([c for c in column if c["top"] < run[0]["top"]]):
        if run[0]["top"] - ch["top"] > _RAIL_GAP_MAX:
            break
        run.insert(0, ch)
    for ch in [c for c in column if c["top"] > run[-1]["top"]]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    return {"glyph": _RAIL_GLYPH, "x": float(x),
            "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _drawn_rail(pm) -> dict | None:
    """The drawn vertical divider, or None. One rect per page, on the axis."""
    best = None
    for v in pm.v_rules:
        if v.height < 24.0 or abs(v.x - pm.width / 2) > _RAIL_OFF_AXIS:
            continue
        if best is None or v.height > best.height:
            best = v
    if best is None:
        return None
    return {"glyph": "│", "x": float(best.x),
            "top": float(best.top), "bottom": float(best.bottom)}


def _rail(pm) -> dict | None:
    """The caption's divider on ``pm``: typed first, drawn second. The two
    are exclusive over this corpus; where a page somehow drew both, the
    typed glyphs are the ones the columns are actually set against."""
    return _typed_rail(pm) or _drawn_rail(pm)


def _shed(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    if rail["glyph"] != _RAIL_GLYPH:
        return line
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == _RAIL_GLYPH
                    and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the rail, or None. Split
    CHAR BY CHAR: whether pdfio already broke the row at its column gap is
    an accident of how wide the gap happened to be."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------

def _rows_raw(pm) -> list[list]:
    """Every inked row of the page, furniture included.

    THE LETTERHEAD IS FURNITURE TO CORE AND CONTENT TO THIS COURT. Core's
    FurnitureFinder reads the officer's name and the courthouse address as
    page apparatus and removes both — on intel_corp it took ids 3-7, so the
    officer who wrote the letter never reached the reader and the letterhead
    band read as three masthead rows and nothing else. The letter branch
    therefore walks the raw rows and hands back what it does not want: page
    1 of a letter carries no running head to confuse it.
    """
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, furniture removed, grouped by baseline."""
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


def _cell(parts: list, role: str, page: int):
    """One column's cell on one row — the empty one keeps its place."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                        role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="delch")
def read_headmatter_delch(model, geom, **_):
    """Read Chancery's captioned box or its letter ruling, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 4:
        return NOTHING
    head = [_norm(" ".join(l.plain for l in g)) for g in rows[:6]]
    if any(_MAST_BOX.match(t) for t in head):
        return _read_captioned(model, geom, finder)
    if any(_squeeze(l.plain) == _MAST_LETTER
           for g in rows[:6] for l in g):
        return _read_letter(model, geom, finder)
    return NOTHING


def _read_captioned(model, geom, finder) -> dict:
    """The box, the title, the dates, the appearances — to the byline."""
    page1 = model.pages[0]
    rail = _rail(page1)
    if rail is None:
        return NOTHING              # no divider: not a caption this court set
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0

    ctx = _Ctx()
    left: list = []
    right: list = []
    right_plain: list[str] = []
    caption_rows: list[str] = []
    box_ids: set[int] = set()
    box_page = page1.number
    band = "box"

    # THE WALK RUNS TO THE BYLINE, over as many as three pages, so the
    # stream is built first: advent's box closes on page 2 and its
    # appearances end on page 3.
    stream: list = []
    for pm in model.pages[:_MAX_PAGES]:
        page_rail = rail if pm.number == page1.number else _rail(pm)
        for group in _rows(pm, finder):
            stream.append((pm, page_rail, sorted(group, key=lambda l: l.x0)))

    # THE APPEARANCES STAND BETWEEN THE COURT'S DATES AND THE BYLINE, and
    # nothing else stands there — so the block is bracketed by the byline
    # rather than recognised row by row. Read row by row it broke three
    # ways: a first row whose firm carries its 'LLP' on the NEXT line
    # (ashok_mayya), and a PRO SE party's own appearance, which names no
    # firm at all ('Gwendolyn Colston, Camden-Wyoming, Delaware; Plaintiff'
    # / 'Gregory M. Palumbo; Pro se.'). Each left one row unclaimed above
    # the writing, and an unclaimed row there does not stay in the
    # headmatter — it opens a phantom writing of its own.
    byline_at = None
    for i, (_pm, _pr, pieces) in enumerate(stream):
        text = _norm(" ".join(l.plain for l in pieces))
        if _BYLINE.match(text) and len(text) < 48:
            byline_at = i
            break

    mast_seen = False
    consumed_to = -1
    tail_head = False
    for i, (pm, page_rail, pieces) in enumerate(stream):
        if i <= consumed_to:
            continue
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        centred = abs((pieces[0].x0 + max(l.x1 for l in pieces)) / 2
                      - pm.width / 2) <= 20.0

        if _MAST_BOX.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            mast_seen = True
            continue
        if not mast_seen:
            # An e-filing stamp above the masthead ('EFiled: Apr 29 2026
            # 09:55AM EDT', 'Filing ID 79335656'): the clerk, not the court.
            ctx.drop(pieces, "stamp")
            continue
        if _BYLINE.match(text) and len(text) < 48:
            break                                   # the writing begins

        if band == "box" and page_rail is not None \
                and pieces[0].top <= page_rail["bottom"] + 1.0:
            # ONE PRINTED ROW, TWO STACKS: both sides keep their place even
            # when one is blank, so the columns stay level.
            l_cells, r_cells = [], []
            for line in pieces:
                bare = _shed(line, page_rail)
                if bare is None:
                    continue
                for want, bucket in (("L", l_cells), ("R", r_cells)):
                    part = _side(bare, page_rail["x"], want)
                    if part is not None:
                        bucket.append(part)
            left.append(_cell(l_cells, "caption", pm.number))
            right.append(_cell(r_cells, _right_role(r_cells), pm.number))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
            caption_rows.append(_norm(" ".join(c.plain for c in l_cells)))
            box_ids.update(l.id for l in pieces)
            continue
        if band == "box":
            band = "tail"
            tail_head = True

        # THE CASE'S NUMBERING STANDS WITH THE BOX. A coordinated filing
        # names the other docket it applies to on a row of its own, directly
        # under the box ('THIS FILING APPLIES TO COORDINATED C.A. No.
        # 2022-1087-JTL'). Read only while the tail is still at its head, so
        # a docket CITED further down in prose is not mistaken for one.
        if tail_head and len(text) < 120:
            other = _DOCKET_ANY.search(text)
            if other:
                value = _norm(other.group(1))
                if value != ctx.crit.get("docket_number"):
                    ctx.crit.setdefault("other_dockets", []).append(value)
                ctx.emit(pieces, "docket", centre=centred)
                continue

        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(_norm(dated.group(1)).lower())
            if key:
                ctx.crit.setdefault(key, _norm(dated.group(2)))
            ctx.emit(pieces, "date", centre=centred)
            tail_head = False
            continue
        if pieces[0].all_bold and centred and len(text) < 90:
            ctx.crit.setdefault("title", text)
            ctx.emit(pieces, "title")
            # AN UNSIGNED ORDER OPENS ON ITS TITLE. Claimed and not
            # released, 'ORDER' leaves the document with no anchor at all,
            # so its ids are offered back to the stream.
            ctx.anchor.extend(p.id for p in pieces)
            tail_head = False
            continue
        # THE APPEARANCES ARE A PARAGRAPH, NOT A ROW. Its runover rows carry
        # no landmark of their own ('Bowers.' under '…for Plaintiff
        # Shalomyah'), and its FIRST row carries none either
        # ('Rebecca L. Butcher, … LANDIS RATH & COBB', whose 'LLP' is on the
        # next line). Read row by row, that first row was left unclaimed —
        # and an unclaimed row above the writing does not stay in the
        # headmatter, it opens a phantom writing of its own. So the unit is
        # the paragraph: contiguous rows at the block's own single leading,
        # taken when the paragraph NAMES an appearance and stands
        # unindented at the measure.
        if byline_at is not None:
            # Between the dates and the byline: the appearances, whole.
            ctx.emit(pieces, "counsel", centre=False)
            continue
        # NO BYLINE TO BRACKET WITH — an order signed at its foot. Here the
        # appearances have to name themselves, and the unit is the printed
        # paragraph: contiguous rows at the block's own single leading,
        # taken when the paragraph names an appearance and stands
        # unindented at the measure (an order's body indents its first
        # line, and says 'pro se' as readily as any roster does).
        para = _paragraph(stream, i, body_size)
        if _is_appearance(stream, para, body_x0):
            for j in range(para[0], para[1] + 1):
                ctx.emit(stream[j][2], "counsel", centre=False)
            consumed_to = para[1]
            continue
        if _DISPO.search(text) and len(text) < 160:
            ctx.crit.setdefault("disposition", text)
            ctx.emit(pieces, "disposition", centre=centred)
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if left:
        # The rail runs a few rows past the last words; ca6 trims the empty
        # tail pairs and so does this.
        while left and not _text_of(left[-1]) and not _text_of(right[-1]):
            left.pop()
            right.pop()
            right_plain.pop()
            caption_rows.pop()
    if not left:
        return NOTHING

    block = m.CaptionBlock(
        left=left, right=right, rail=rail["glyph"], rail_rows=len(left),
        style_id=("parenthetical-box" if rail["glyph"] == _RAIL_GLYPH
                  else "ruled-box"),
        fp={"rail": rail["glyph"], "mid_x": round(rail["x"], 1)},
        prov=m.Prov(box_page, tuple(sorted(box_ids))))
    head = [i for i in ctx.items if getattr(i, "role", "") == "court"]
    ctx.items = head + [block] + [i for i in ctx.items if i not in head]
    ctx.consumed.update(box_ids)

    docket = _docket_of(right_plain)
    if not docket:
        return NOTHING              # no docket read: the box was not read
    ctx.crit["docket_number"] = docket
    sides = _sides(caption_rows)
    if sides:
        ctx.crit.setdefault("parties", list(sides))
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    return ctx.result()


def _paragraph(stream: list, i: int, body_size: float) -> tuple[int, int]:
    """The printed paragraph ``stream[i]`` opens: contiguous rows on one
    page set at the block's own single leading. The appearances are set
    single (16.1pt over a 14pt measure) inside a double-spaced paper, so the
    leading alone closes the paragraph — and a page break closes it too."""
    lead = 1.4 * (body_size or 12.0)
    end = i
    while end + 1 < len(stream):
        pm, _r, pieces = stream[end]
        nxt_pm, _r2, nxt = stream[end + 1]
        if nxt_pm.number != pm.number:
            break
        if nxt[0].top - pieces[0].top > lead:
            break
        end += 1
    return (i, end)


def _is_appearance(stream: list, para: tuple[int, int],
                   body_x0: float) -> bool:
    """Does this paragraph NAME an appearance? It must say so — a firm, an
    'Esquire', or who it appears for — and it must stand unindented at the
    measure, which is what tells it from the body of an order (whose first
    line is indented half an inch and which says 'pro se' as readily as any
    roster does)."""
    first = stream[para[0]][2][0]
    if first.x0 > body_x0 + 2.0:
        return False
    joined = _norm(" ".join(l.plain for j in range(para[0], para[1] + 1)
                            for l in stream[j][2]))
    return bool(_COUNSEL.search(joined))


_STATUS_WORDS = frozenset(
    ("plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
     "petitioners", "respondent", "respondents", "appellant", "appellants",
     "appellee", "appellees", "counterclaim", "counterclaimant",
     "counterdefendant", "nominal", "intervenor", "intervenors", "below",
     "movant", "movants", "objector", "objectors", "cross", "third", "party",
     "and", "pro", "se", "the", "of", "in", "interest", "claimant",
     "claimants", "garnishee", "trustee"))


def _sides(caption_rows: list[str]) -> tuple[str, str] | None:
    """The two party names either side of the pivot — built from the party
    NAMES, never by joining the caption wholesale (the ca6 reading): the
    status labels and the pivot are apparatus, not names."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        if _PIVOT.match(flat):
            side = right
            seen_pivot = True
            continue
        words = [w.strip(",.;-/ ").lower()
                 for w in flat.replace("-", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    if not (left and right and seen_pivot):
        return None
    # THE COMMA is the caption's apparatus — it leads to the status row
    # below. The FULL STOP is not: it ends the abbreviation the party is
    # incorporated under ('ADVENT INTERNATIONAL PE ADVISORS, S.C.').
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _right_role(cells: list) -> str:
    """What the right column is saying on this row."""
    text = _norm(" ".join(c.plain for c in cells))
    if not text:
        return "caption"
    if _DOCKET.match(text) or _DOCKET_TAIL.match(text):
        return "docket"
    return "case-info"


def _docket_of(right_plain: list[str]) -> str | None:
    """The docket as the right column writes it — label and number over two
    rows joined, a trailing complex-litigation tag kept."""
    value = None
    for text in right_plain:
        text = _norm(text)
        if not text:
            continue
        hit = _DOCKET.match(text)
        if hit:
            if value is None:
                value = _norm(hit.group(1))
            continue
        if value is not None and _DOCKET_TAIL.match(text):
            value = _norm(f"{value} {text}")
    return value or None


def _read_letter(model, geom, finder) -> dict:
    """The letterhead, the addressees and the 'Re:' block — to the
    salutation, which is where the letter itself begins."""
    ctx = _Ctx()
    pm = model.pages[0]
    rows = _rows_raw(pm)
    officer, name_id, title_id = _officer(pm, rows)
    band = "letterhead"
    saw_salutation = False
    names: list[str] = []
    dockets: list[str] = []
    re_last = "name"

    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        if band != "letterhead" and _SALUTATION.match(text):
            saw_salutation = True
            break                                   # the letter begins
        centred = abs((pieces[0].x0 + max(l.x1 for l in pieces)) / 2
                      - pm.width / 2) <= 24.0

        # THE DATES CLOSE THE LETTERHEAD, and the court writes them two ways
        # — a bare date under the masthead ('August 11, 2026') and the
        # labelled pair the captioned paper uses ('Date Submitted: July 22,
        # 2026' / 'Final Report: July 2, 2026'). Reading only the bare form
        # left the letterhead open on 6 of the 15 letters, and with it open
        # nothing below was ever read.
        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(_norm(dated.group(1)).lower())
            if key:
                ctx.crit.setdefault(key, _norm(dated.group(2)))
            ctx.emit(pieces, "date", centre=centred)
            band = "addressees"
            continue
        if _LETTER_DATE.match(text):
            ctx.crit.setdefault("decision_date", text)
            ctx.emit(pieces, "date", centre=centred)
            band = "addressees"
            continue

        hit = _RE_LINE.match(text)
        if hit:
            band = "re"
            names.append("")
            _dk, _rest = _re_row(ctx, _norm(hit.group(1)), names, dockets)
            re_last = "docket" if _dk else "name"
            ctx.emit(pieces, "caption", centre=False)
            continue
        if band == "re":
            # THE 'Re:' BLOCK IS NAME-THEN-NUMBER, AND IT REPEATS. A
            # consolidated letter names two cases and numbers each
            # (centene_corporation: 'C.A. No. 2025-0619-MAA' and 'C.A. No.
            # 2025-0802-MAA'), while a long name simply runs on
            # ('…and J.P. Morgan' / 'Securities LLC, C.A. No.
            # 2025-1133-DG'). A name row AFTER a number row opens a new
            # case; otherwise it continues the one above it.
            if re_last == "docket" and not _DOCKET_ANY.search(text):
                names.append("")
            _dk, _rest = _re_row(ctx, text, names, dockets)
            re_last = "docket" if _dk else "name"
            ctx.emit(pieces, "docket" if (_dk and not _rest) else "caption",
                     centre=False)
            continue
        if band == "addressees":
            ctx.emit(pieces, "counsel", centre=False)
            continue

        # THE LETTERHEAD IS THREE COLUMNS ON SHARED ROWS, so its parts are
        # read as LINES: the officer at the left, the masthead centred, the
        # courthouse address at the right.
        for line in pieces:
            one = _norm(line.plain)
            if _squeeze(one) == _MAST_LETTER \
                    or _squeeze(one) in _MAST_LETTER_TAIL:
                ctx.crit.setdefault("court", _COURT_NAME)
                ctx.emit([line], "court")
            elif line.id in (name_id, title_id):
                ctx.emit([line], "author", centre=False)
            elif finder.kind(pm, line):
                continue        # core already accounts for it; leave it be
            else:
                # The stationery: the courthouse, its street, its telephone.
                # Dropped, never deleted — the coverage oracle sees it
                # accounted for (the vt.py precedent).
                ctx.drop([line], "letterhead")

    if not saw_salutation:
        # WITHOUT THE SALUTATION THE BLOCK HAS NO END, and a claim whose end
        # is a guess would take the letter's first paragraphs with it.
        return NOTHING
    if officer:
        ctx.crit.setdefault("judges", ", ".join(officer))
    return ctx.result()


def _re_row(ctx, text: str, names: list[str],
            dockets: list[str]) -> tuple[bool, bool]:
    """One row of the 'Re:' block: take the docket wherever it stands and
    add what remains to the case name being built. Returns (the row carried
    a docket, the row said something besides it) — the first tells the next
    row whether it opens a new case, the second whether this row is the
    number alone."""
    text = _norm(text)
    hit = _DOCKET_ANY.search(text)
    rest = _norm(text[:hit.start()]).rstrip(",") if hit else text
    if rest:
        if not names:
            names.append("")
        names[-1] = _norm(f"{names[-1]} {rest}").strip()
        # THE FIRST CASE NAMED IS THE CASE. A consolidated letter names a
        # second, and there is one `case_name` — the caption rows carry
        # both verbatim, which is where the second one is auditable.
        if names[0]:
            ctx.crit["case_name"] = names[0].rstrip(",")
    if hit:
        value = _norm(hit.group(1))
        if value not in dockets:
            dockets.append(value)
            if "docket_number" not in ctx.crit:
                ctx.crit["docket_number"] = value
            else:
                ctx.crit.setdefault("other_dockets", []).append(value)
    return bool(hit), bool(rest)


def _officer(pm, rows: list) -> tuple[list[str], int | None, int | None]:
    """Who signs the stationery: the title stands alone in the left column
    and the name is the nearest left-column line ABOVE it.

    Not 'the row above' — the letterhead's three columns are set at
    different baselines, so the row between them is as often a line of the
    courthouse address (yanan_sun sets 'LOREN MITCHELL' at top 123.8 and
    'MAGISTRATE IN CHANCERY' at 137.4 with two address rows in between)."""
    left = sorted((l for g in rows for l in g if l.x0 < pm.width * 0.4),
                  key=lambda l: l.top)
    title = next((l for l in left if _BENCH_TITLE.match(_norm(l.plain))), None)
    if title is None:
        return [], None, None
    name = None
    for line in left:
        if line.top >= title.top:
            break
        one = _norm(line.plain)
        if _squeeze(one) == _MAST_LETTER or _squeeze(one) in _MAST_LETTER_TAIL:
            continue
        if _LETTERHEAD_ROW.search(one):
            continue
        name = line
    who = _norm(title.plain)
    # 'MAGISTRATE IN CHANCERY'.title() is 'Magistrate In Chancery' — the
    # court's own style capitalizes the office, not the preposition.
    who = _TITLE_CASE.get(who.upper(), who.title() if who.isupper() else who)
    officer = ([_norm(name.plain)] if name is not None else []) + [who]
    return officer, (name.id if name is not None else None), title.id
