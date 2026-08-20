"""Superior Court of the State of Delaware ('delsuperct').

Everything unique to delsuperct lives here. It imports core, never another
court file, and no other court file imports it — not `del.py`, whose
section-rail Delaware is a different paper, and not `delch.py`, whose two
formats this court prints in its own hand and whose code this file copies
without touching.

THE COURT PUBLISHES TWO PAPERS, and it says which by its MASTHEAD. Counted
over all 42 records, page 1, first inked row:

    IN THE SUPERIOR COURT OF THE STATE OF DELAWARE        38   the CAPTION
    IN THE SUPERIOR COURT FOR THE STATE OF DELAWARE        1   (aclu_v._martin)
    THE SUPERIOR COURT OF THE STATE OF DELAWARE            1   (state_v._tamba)
    SUPERIOR COURT / of the / STATE OF DELAWARE             2   the LETTER

'IN' and 'OF' are not load-bearing — the same masthead, set three ways — so
the row is matched with both words optional. The letterhead is the same
three-row stationery the Court of Chancery writes on, at 18pt.

THE DIVIDER IS TYPED, AND IT IS THE ONLY ONE THIS COURT DRAWS. Measured over
all 42 records, EVERY page: **VERTICAL RULES CORPUS-WIDE = 3** — none of them
on a caption page, and 40 of the 42 records type a ')' column instead (x0
296.8-360.0, within 54pt of the 306pt axis). The two that type none are the
two letters. So there is one branch here where delch has two, and the
absence is measured, not assumed.

    ┌─────────────────────────────────────────────────────────────────┐
    │      IN THE SUPERIOR COURT OF THE STATE OF DELAWARE             │
    │  STATE OF DELAWARE,         )                                   │
    │                             )                                   │
    │     v.                      )  ID No. 2201008017                │  the docket,
    │                             )                                   │  in the right
    │  CHARLES J DESTAFNEY,       )                                   │  column
    │     Defendant.              )                                   │
    │                                                                 │
    │                Submitted:  May 12, 2026                         │  the dates, with
    │                Decided:  August 5, 2026                         │  no 'Date' prefix
    │      Upon Consideration of Defendant's                           │  WHAT WAS DECIDED,
    │      Motion to Dismiss … Forum Non Conveniens:                   │  centred, over as
    │                    DENIED.                                       │  many rows as it
    │             MEMORANDUM OPINION AND ORDER                          │  takes — then the
    │  Brian M. Rostocki, … REED SMITH LLP, Wilmington, Delaware;      │  paper's name, the
    │  Miller, J.                                                       │  appearances, the
    └─────────────────────────────────────────────────────────────────┘  byline

WHAT WAS DECIDED IS A BLOCK, NOT A LINE. This court states the motion before
it and its ruling in a centred stack of up to four rows, and the ruling is
the bold last row of the stack:

    Upon The ArcLight Entities' / Motion for Partial Summary Judgment /
    on Coverage for Pre-Tender Defense Costs, / **DENIED.**
    On Appeal from the Industrial Accident Board, / **REVERSED.**
    Upon appeal of Industrial Accident Board Decision – Affirmed

So a bold centred row is NOT automatically the paper's name: 'DENIED.' is
bold, centred and short, and read as a title it takes the row the court set
aside for its holding. A row that is a disposition WORD and nothing else is
the disposition; 'MEMORANDUM OPINION AND ORDER' is the title.

THE DOCKET IS WRITTEN NINE WAYS in the right column, and a record can print
two of them (state_v._tamba sets 'I.D. No. 2201002905' over 'Cr. A. Nos.
IN22-02-0864, etc.'):

    C.A. No. / C.A. No.: / Civ. A. No. / Cr. A. No(s). / Crim. ID No.
    I.D. No(s). / ID No(s). / No.

The first is the docket; the rest are `other_dockets`, which is what they
are — the same case's other numbers, not a case alongside. A trailing judge
tag ('N25C-12-001 KMM', '… SKR CCLD') is part of the number as printed.

ONLY 13 OF THE 42 RECORDS SIGN ON PAGE 1 OR 2 ('Miller, J.',
'GREEN-STREETT, J.', 'RENNIE, J.', 'Adams, J.', … — caps and title case
both). The other 27 are orders that sign at their foot with a conformed
'/s/', which is core's to read. That matters for the appearances: where a
byline stands, it BRACKETS the roster (nothing else stands between the
court's dates and it); where none does, the roster has to name itself.

FORMAT 2 — THE LETTER RULING (2 records: msg_network_inc, state_v._clark).
The same stationery, the same reading as Chancery's letters: officer at the
left, masthead centred, courthouse at the right; the dates; the addressees
in two columns; 'RE: State v. Clark, I.D. No. 2509003414'; and the
salutation, which opens the letter. state_v._clark writes the bare
'Counsel:'.

WHAT THIS FILE DOES NOT DO. It reads the block above the writing and nothing
else: the byline grammar, the conformed '/s/' that authors an unsigned
order, the footnotes and the paragraphing are core's, and are configured on
the profile in courts/__init__.py.
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
    r"^(?:IN\s+)?THE SUPERIOR COURT (?:OF|FOR|IN AND FOR)?\s*"
    r"THE STATE OF DELAWARE$", re.I)
# The letterhead's own rows, spaces squeezed out: 'OFTHE' and
# 'STATEOFDELAWARE' come back unspaced on some records (tonya_frazier).
_MAST_LETTER = "SUPERIORCOURT"
_MAST_LETTER_TAIL = ("OFTHE", "STATEOFDELAWARE")
_COURT_NAME = "Superior Court of the State of Delaware"

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
    r"(?:C\.\s?A\.?|Civ\.\s?A\.?|Cr\.\s?A\.?|Cr(?:im)?\.\s?ID"
    r"|I\.?\s?D\.?|Civil\s+Action|Case|File)"
    r"\s*(?:Nos?\.?:?|ID)\s*")
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
# A ROW THAT IS A DISPOSITION AND NOTHING ELSE — the ruling at the foot of
# the court's centred stack. Two words at most, so 'Plaintiff's Motion for
# Summary Judgment is DENIED' (a sentence of the body) is not one.
_DISPO_WORDS = frozenset(
    ("granted", "denied", "affirmed", "reversed", "vacated", "remanded",
     "dismissed", "modified", "sustained", "overruled", "quashed", "stayed",
     "withdrawn", "deferred"))
_DISPO_FILLER = frozenset(("in", "part", "and", "but", "&", "as", "moot"))
# The stack's other rows: what was moved for, or where the case came from.
_UPON = re.compile(
    r"^(?:Upon|On|Re:?\s|Motion|Cross[- ]Motion|Defendants?|Plaintiffs?"
    r"|Appellants?|Appellees?|Petition|Application)\b")
# WHERE THE CASE CAME FROM is an APPEAL or a certified question — that is
# what `history` means. 'Upon Review' was on this list and is not one of
# them: what this court reviews is a paper filed in the case in front of it,
# and both records that print the row say so ('Upon Review of the Affidavit
# of Merit' — johnson_v._bayhealth_medical_center, and boyington…, whose row
# carries its own ruling, 'Upon Review of the Affidavit of Merit –
# REJECTED'). Read as an origin, each recorded an affidavit as the court
# below. The three genuine ones all name the appeal: 'Upon Appeal of Chief
# Deputy Attorney General', 'On Appeal from the Industrial Accident Board,',
# 'Upon appeal of Industrial Accident Board Decision – Affirmed'.
_ORIGIN = re.compile(r"^(?:Upon\s+[Aa]ppeal|On\s+[Aa]ppeal"
                     r"|Upon\s+[Cc]ertification)\b")
_DISPO = re.compile(
    r"\b(GRANTED|DENIED|AFFIRMED|REVERSED|VACATED|REMANDED|DISMISSED"
    r"|MODIFIED|SUSTAINED|OVERRULED)\b")
# THE RULING AT THE END OF THE STATEMENT — 'Judgment, GRANTED.', 'Motion to
# Dismiss: DENIED.', 'GRANTED in part, DENIED in part.' Anchored on the end
# so a ruling word INSIDE a sentence that runs on past it ('the Motion is
# DENIED as to Count II because …') is not one. Same vocabulary as
# `_DISPO_WORDS`, spelled out because this one has to match in order.
_RULING_TAIL = re.compile(
    r"\b(?:GRANTED|DENIED|AFFIRMED|REVERSED|VACATED|REMANDED|DISMISSED"
    r"|MODIFIED|SUSTAINED|OVERRULED|QUASHED|STAYED|WITHDRAWN|DEFERRED)"
    r"(?:\s+(?:in|and|but|as)\s+(?:part|moot))*\s*[.;]?\s*$")
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
    r"(?:J\.|R\.\s?J\.|P\.\s?J\.|C\.|Resident\s+Judge"
    r"|President\s+Judge|Judge|Commissioner|Justice)"
    # A byline may carry a FOOTNOTE MARK ('WINSTON, J.1' — sitting by
    # designation), which is part of the row and not part of the title.
    r"\s*\d{0,2}\s*[.:]?$")

# ---- the letter ruling ----------------------------------------------------

# The officer's title, as the letterhead prints it.
_BENCH_TITLE = re.compile(
    r"^(?:RESIDENT\s+JUDGE|PRESIDENT\s+JUDGE|JUDGE|COMMISSIONER"
    r"|MASTER)$", re.I)
_TITLE_CASE = {
    "RESIDENT JUDGE": "Resident Judge",
    "PRESIDENT JUDGE": "President Judge",
    "JUDGE": "Judge",
    "COMMISSIONER": "Commissioner",
    "MASTER": "Master",
}
_LETTER_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_RE_LINE = re.compile(r"^Re\s*:\s*(.*)$", re.I)
_SALUTATION = re.compile(r"^(?:Dear\b.*|Counsel|Parties|Ladies\s+and\s+Gentlemen)\s*[:,]?$")
_LETTERHEAD_ROW = re.compile(
    r"JUSTICE\s+CENTER|COURTHOUSE|KING\s+STREET|THE\s+GREEN|MARKET\s+STREET"
    r"|WILMINGTON,\s+DE|DOVER,\s+DE|GEORGETOWN,\s+DE|SUITE|Telephone"
    r"|\(302\)|County\s+Court", re.I)


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


def _rail(pm) -> dict | None:
    """The caption's divider on ``pm``. THERE IS ONLY ONE KIND HERE: over all
    42 records and every page this court draws 3 vertical rules in total and
    none of them on a caption page, so the typed ')' column is the divider
    or there is none. delch's drawn-rect branch is deliberately absent — a
    branch for a shape the court does not print is a guess dressed as a
    reading."""
    return _typed_rail(pm)


def _shed(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
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

@decider("headmatter.read", court="delsuperct")
def read_headmatter_delsuperct(model, geom, **_):
    """Read the Superior Court's captioned box or its letter, or NOTHING."""
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
    right_x1 = geom.right_x1 if geom and geom.right_x1 else page1.width - 72.0

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
    in_stack = False
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
        # WHAT WAS DECIDED IS A BLOCK, AND ITS RULING IS BOLD. A row that
        # is a disposition WORD and nothing else ('DENIED.', 'REVERSED.')
        # is that ruling — read as the paper's name it takes the row the
        # court set aside for its holding, and 'MEMORANDUM OPINION AND
        # ORDER' then has nowhere to go.
        if _is_dispo_only(text):
            ctx.crit.setdefault("disposition", text.rstrip("."))
            ctx.emit(pieces, "disposition", centre=centred)
            tail_head = False
            continue
        # The rest of the stack states the motion, or where the case came
        # from: 'Upon Consideration of Defendant's / Motion to Dismiss …' /
        # 'On Appeal from the Industrial Accident Board,'. The origin row is
        # `lower-court` and is recovered into `history`; the motion row is
        # the disposition's own statement.
        # …and, like the rows that continue it, the stack's OPENING row must
        # not reach the measure: an order's first sentence begins 'On this
        # 22nd day of July, 2026, upon consideration of …' and spans to the
        # right margin, which `_UPON` matches word for word.
        if (_UPON.match(text) and len(text) < 160
                and max(l.x1 for l in pieces) < right_x1 - 18.0):
            if _ORIGIN.match(text):
                ctx.crit.setdefault("history", text)
                ctx.emit(pieces, "lower-court", centre=centred)
            else:
                ctx.crit.setdefault("motion", text)
                ctx.emit(pieces, "disposition", centre=centred)
            tail_head = False
            in_stack = True
            continue
        # THE STACK RUNS ON, and its middle rows open on a word no landmark
        # can name — 'on Coverage for Pre-Tender Defense Costs,' /
        # 'Regarding Pre-Tender Defense Costs'. They are centred, set in
        # from the measure, and not bold: the appearances below stand FLUSH
        # at the measure and the paper's name is bold, so neither can be
        # confused with them. Left out of the stack they were tinted
        # `counsel` on 3 rows of arclight alone.
        # …and it must not REACH THE MEASURE. A body paragraph's first line
        # is indented too, and spans to the right margin, which puts its
        # centre within a few points of the page axis — 'centred' on the
        # test above. A stack row stops well short of it.
        if (in_stack and centred and not pieces[0].all_bold
                and pieces[0].x0 > body_x0 + 12.0 and len(text) < 160
                and max(l.x1 for l in pieces) < right_x1 - 18.0):
            ctx.emit(pieces, "disposition", centre=True)
            continue
        # WHAT WAS DECIDED, FOUND BY ITS RULING. The two tests above name
        # the block by how it OPENS — 'Upon', 'On', 'Motion' — and by
        # standing short of the measure, and this court writes it two ways
        # that answer to neither:
        #
        #   starbuck_v._google_llc   'Google LLC's Motion to Dismiss:'
        #                            '**DENIED.**'
        #   stansbury_v._helm-…      '*Upon Consideration of Defendant
        #                             Universal Protection Service, LLC
        #                             d/b/a Allied Universal Security
        #                             Services Motion for Summary
        #                             Judgment*, **GRANTED.**'
        #
        # The first opens on the movant's NAME, so no opener list reaches
        # it. The second is a sentence set to the full measure (x1 534.6
        # against a 540.1 rail) in two runs of italic, closing on its bold
        # ruling — the measure guard that keeps an order's own first
        # sentence out is exactly what rejects it. Both were read as
        # APPEARANCES, which is what stands next in the paper (the user,
        # 2026-08-20: 'upon consideration is not counsel... its a summary';
        # 'google llc motion to dismiss should be part of DENIED and marked
        # as disposition').
        #
        # So this test does not look at how the block opens. It reads the
        # PARAGRAPH the court set and asks whether it CLOSES ON A RULING —
        # a row that is a disposition and nothing else, or a sentence whose
        # last word is one. That is the block's own definition, and it is
        # why the two tests above stay: where a row names an ORIGIN it is
        # `history`, and only what nothing else has claimed reaches here.
        decided = _decided_para(stream, i, body_size)
        if decided is not None:
            start, end = decided
            joined = _norm(" ".join(
                l.plain for j in range(start, end + 1)
                for l in stream[j][2]))
            ruling = _norm(" ".join(l.plain for l in stream[end][2]))
            for j in range(start, end + 1):
                ctx.emit(stream[j][2], "disposition",
                         centre=_is_centred(stream[j], 20.0))
            # THE MOTION IS THE STATEMENT WITHOUT ITS RULING. Kept whole,
            # `motion` reads '… Motion for Summary Judgment, GRANTED.' and
            # says the same thing twice.
            ctx.crit.setdefault(
                "motion", _RULING_TAIL.sub("", joined).strip(" ,.;:"))
            _tail = _RULING_TAIL.search(ruling)
            ctx.crit.setdefault(
                "disposition",
                ruling.rstrip(".") if _is_dispo_only(ruling)
                else _tail.group(0).strip(" .;"))
            consumed_to = end
            in_stack = False
            tail_head = False
            continue
        # THE PAPER'S NAME NEVER REACHES THE MEASURE. It is a centred word
        # or two ('ORDER', 'MEMORANDUM OPINION AND ORDER'), and this test
        # asked only that the row be bold, centred and short — which a
        # NUMBERED BODY PARAGRAPH also is, because pdfio splits its marker
        # off at the column gap and the marker is bold: johnson_v._bayhealth
        # _medical_center opened '**1.**  This matter involves a medical
        # negligence suit filed by Dawn Johnson', 71 characters, its centre
        # 18pt off the axis — and the first line of the order's first
        # paragraph became the paper's title, leaving the paragraph to open
        # on '("Plaintiff") against Bayhealth' (the user, 2026-08-20: 'this
        # one takest he first line and puts it in teh ehedmatter'). A
        # paragraph spans the measure; the name stops well short of it.
        if pieces[0].all_bold and centred and len(text) < 90 \
                and max(l.x1 for l in pieces) < right_x1 - 18.0:
            ctx.crit.setdefault("title", text)
            ctx.emit(pieces, "title")
            in_stack = False
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
            in_stack = False
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
        # THE BLOCK ENDS WHERE THE WRITING BEGINS, and on an order that
        # signs at its foot there is no byline up here to end it. Every part
        # of this block stands short of the measure — masthead, caption
        # cells, dates, the decided stack, the paper's name — and the two
        # things that span it are the appearances, tested above, and the
        # writing. So a row that reaches the measure and is neither is the
        # order talking, and the walk is over.
        #
        # Left running, it read three more pages of prose against every
        # landmark it has: state_v._brown took its `disposition` from page
        # 3 ('of an illegal sentence must and hereby is DENIED. Defendant's
        # request') and its `motion` from the sentence after it, and
        # state_v._destafney took a bold 'DENIED.' off its last page — real
        # rulings, read from the body, in a block that never stated one.
        # (Where a byline DOES stand up here the appearances branch above
        # claims every row to it, so this is unreachable — which is why it
        # cannot leave a recognised roster unclaimed.)
        if max(l.x1 for l in pieces) >= right_x1 - 18.0:
            break
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
        style_id="parenthetical-box",
        fp={"rail": rail["glyph"], "mid_x": round(rail["x"], 1)},
        prov=m.Prov(box_page, tuple(sorted(box_ids))))
    head = [i for i in ctx.items if getattr(i, "role", "") == "court"]
    ctx.items = head + [block] + [i for i in ctx.items if i not in head]
    ctx.consumed.update(box_ids)

    dockets = _docket_of(right_plain)
    if not dockets:
        return NOTHING              # no docket read: the box was not read
    ctx.crit["docket_number"] = dockets[0]
    if dockets[1:]:
        ctx.crit["other_dockets"] = dockets[1:]
    sides = _sides(caption_rows)
    if sides:
        ctx.crit.setdefault("parties", list(sides))
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    return ctx.result()


def _is_dispo_only(text: str) -> bool:
    """A row that is a disposition and NOTHING else — the ruling at the foot
    of the court's centred stack. Tested by TOKEN, not by alternation: this
    court rules on two things at once ('GRANTED in part, DENIED in part.')
    and an alternation spelling out every pairing would still miss the next
    one. The filler list stops at 'in part' and the conjunctions on purpose —
    admit 'motion' and 'the Motion is DENIED', a sentence of the writing,
    becomes a disposition."""
    toks = [x.strip(",.;:()").lower() for x in _norm(text).split()]
    toks = [x for x in toks if x]
    if not toks or len(toks) > 10:
        return False
    return (any(x in _DISPO_WORDS for x in toks)
            and all(x in _DISPO_WORDS or x in _DISPO_FILLER for x in toks))


def _is_centred(row: tuple, tol: float) -> bool:
    """Is this stream row set on its page's axis?"""
    pm, _rail, pieces = row
    return abs((pieces[0].x0 + max(l.x1 for l in pieces)) / 2
               - pm.width / 2) <= tol


def _decided_para(stream: list, i: int,
                  body_size: float) -> tuple[int, int] | None:
    """The paragraph at ``stream[i]``, if it is a statement of WHAT WAS
    DECIDED — that is, if it CLOSES ON A RULING.

    The court states each thing it decides as one printed paragraph and puts
    the ruling last, so the ruling is the landmark and the opening word is
    not. Two forms, measured: a centred stack whose last row is the ruling
    alone ('Google LLC's Motion to Dismiss:' / 'DENIED.'), and a sentence
    run to the measure whose last words are it ('… Motion for Summary
    Judgment, GRANTED.').

    THREE THINGS KEEP THIS OFF THE WRITING, which also rules on motions and
    also says GRANTED:
      * it is a PARAGRAPH by this court's own leading, at most four rows —
        the docstring's count of the stack;
      * the ruling must be the paragraph's LAST WORDS, not a word inside a
        sentence that runs on past it;
      * and only rows nothing else has claimed reach here, which is after
        the dates and before the appearances.
    An order's own first sentence ('On this 22nd day of July, 2026, upon
    consideration of … it appears to the Court that') is a four-row
    paragraph in exactly this position and is refused by the second test:
    it does not end on a ruling."""
    start, end = _paragraph(stream, i, body_size)
    # A statement of what was decided names the motion AND rules on it, so
    # it is never one row. (A one-row form — 'Upon appeal of Industrial
    # Accident Board Decision – Affirmed' — opens on a word the tests above
    # already know, and is claimed there.)
    if end == start or end - start > 3:
        return None
    last = _norm(" ".join(l.plain for l in stream[end][2]))
    return (start, end) if (_is_dispo_only(last)
                            or _RULING_TAIL.search(last)) else None


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


def _docket_of(right_plain: list[str]) -> list[str]:
    """The dockets as the right column writes them, in printed order.

    A record can number itself twice — state_v._tamba sets 'I.D. No.
    2201002905' over 'Cr. A. Nos. IN22-02-0864, etc.' — and both are THIS
    case, so the first is the docket and the rest are `other_dockets`. A
    bare identifier row continues the number above it ('C.A. No.
    N25C-12-001 KMM' / 'CCLD'), which is how the court prints a
    complex-litigation tag."""
    found: list[str] = []
    for text in right_plain:
        text = _norm(text)
        if not text:
            continue
        hit = _DOCKET.match(text)
        if hit:
            value = _norm(hit.group(1))
            if value:
                found.append(value)
            continue
        if found and _DOCKET_TAIL.match(text):
            found[-1] = _norm(f"{found[-1]} {text}")
    return found


def _read_letter(model, geom, finder) -> dict:
    """The letterhead, the addressees and the 'Re:' block — to the
    salutation, which is where the letter itself begins."""
    ctx = _Ctx()
    pm = model.pages[0]
    rows = _rows_raw(pm)
    officer, name_id, title_id = _officer(pm, rows)
    # THE LETTERHEAD ENDS WHERE THE COURTHOUSE ADDRESS ENDS. It is the only
    # thing this page sets in the RIGHT column, so its last line closes the
    # band — and the band cannot be closed by the dates instead, because
    # this court prints the ADDRESSEES ABOVE them (state_v._clark: officer
    # 171-208, addressees 254-302, 'Submitted:' 335) where Chancery prints
    # them below. Closed on the dates, all ten addressee lines were dropped
    # as stationery, and the two blocks share a city ('Dover, DE 19901') so
    # no wording can tell them apart.
    head_bottom = max(
        (l.bottom for g in rows for l in g
         if l.x0 > pm.width * 0.55 and l.top < pm.height * 0.45),
        default=0.0)
    band = "letterhead"
    saw_salutation = False
    names: list[str] = []
    dockets: list[str] = []
    re_last = "name"
    appear: list = []

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
            if appear:
                ctx.items.append(_addressees(appear))
                appear = []
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
            # THE ADDRESSEES ARE TWO COLUMNS, and joining them fuses two
            # firms into one row ('Richard I. G. Jones, Jr. Sarah R.
            # Martin'). They are collected and published as a block over an
            # undrawn gutter instead — see `_addressees`.
            appear.append(_split(pieces, pm.width / 2))
            ctx.consumed.update(l.id for l in pieces)
            continue

        if band == "letterhead" and pieces[0].top > head_bottom + 1.0:
            # Below the stationery: the addressees, whom the letter is to,
            # in two columns over an undrawn gutter.
            band = "addressees"
            appear.append(_split(pieces, pm.width / 2))
            ctx.consumed.update(l.id for l in pieces)
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

    if appear:
        ctx.items.append(_addressees(appear))
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


def _split(pieces: list, mid: float) -> tuple:
    """One printed row of the addressee block, as its two columns."""
    left, right = [], []
    for line in pieces:
        for want, bucket in (("L", left), ("R", right)):
            part = _side(line, mid, want)
            if part is not None:
                bucket.append(part)
    return (pieces[0].page, left, right)


def _addressees(rows: list) -> m.CaptionBlock:
    """The two addressee columns as the page sets them: side by side over a
    gutter nothing is drawn in (`rail=None` — what the model means by a
    whitespace gutter). Joined into single rows instead, the two firms the
    letter is addressed to were fused word by word: 'Richard I. G. Jones,
    Jr. Sarah R. Martin' / 'BERGER MCDERMOTT LLP Bryan T. Reed'. The split
    is CHAR BY CHAR at the page axis, which the columns clear on every
    record (left x0 63.8-90.9, right x0 302.4-362.0)."""
    left, right = [], []
    ids: set[int] = set()
    page = rows[0][0]
    for pg, l_parts, r_parts in rows:
        left.append(_cell(l_parts, "counsel", pg))
        right.append(_cell(r_parts, "counsel", pg))
        ids.update(p.id for p in l_parts + r_parts)
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    return m.CaptionBlock(
        left=left, right=right, rail=None, rail_rows=len(left),
        style_id="open-gutter", fp={"rail": None},
        prov=m.Prov(page, tuple(sorted(ids))))


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
