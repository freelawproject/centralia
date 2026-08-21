"""Tax Court of New Jersey ('njtaxct').

A TRIAL court, and it prints a trial court's paper — nothing it sets
resembles either New Jersey appellate corpus, so nothing here is inherited
from them. This file imports core and no other court file, and no other
court file imports it.

THREE PAPERS, dispatched on a LANDMARK each, counted over all 42 records:

  1. THE COLON-RAIL PLEADING BOX (26 records outright, and the second page
     of all 8 notice covers, so 34 in all) — the caption is a pleading box: a TYPED rule at the body
     rail, sometimes closed with an 'x' ('------…------x') and sometimes set
     in underscores; a ':' rail down the middle at x 288-324; the parties
     and their statuses left of it; and right of it the court naming itself,
     the docket, 'Civil Action' / 'OPINION', and the reporter's stamp
     ('Approved for Publication / In the New Jersey / Tax Court Reports').
     Below the box: 'Decided[:] <date>', the appearances, and a byline in
     the court's own abbreviated title — 'NOVIN, J.T.C.',
     'BEDRIN MURRAY, J.T.C.', 'SUNDAR, P.J.T.C.*'.

     THE RAIL IS NOT LOAD-BEARING and this court proves it: two records
     (648-652_raymond_boulevard, kishan_corp) set the same box with NO rail
     at all — the same two columns over whitespace. So the box OPENS on
     either landmark: the typed rule, or the court naming itself in the
     RIGHT column. What identifies the right column is which side of the
     rail a piece sits on where a rail exists, and a declared 300pt divider
     on a 612pt page where none does; never what the piece says.

  2. THE LETTER OPINION (8 records) — the judge's own stationery (the court
     centred, the judge and the courthouse in 8-9pt either side of it), the
     publication notice, a centred date, the addressees at the body rail,
     'Re: <case>' over 'Docket No. …', and a salutation. The salutation
     OPENS THE LETTER, so the reader stops above it and never claims it.

  3. THE CORRECTED-OPINION NOTICE COVER (8 records) — 'Corrected Opinion
     Notice' centred under the Tax Court Management Office's stationery,
     the addressees, 'From:', 'Re:', 'Docket number:', and a numbered list
     of what was corrected. It is a COVER, not the paper: the opinion's own
     box stands on page 2, so the cover is read as page 1 and the walk then
     continues into paper 1 or 2.

WHAT THE NOTICES MEAN, both ways. 'NOT FOR PUBLICATION WITHOUT (THE)
APPROVAL OF THE TAX COURT COMMITTEE ON OPINIONS' is the standing caveat
every record carries; the reporter's stamp beside the caption is the
opposite fact. The stamp WINS where both are printed — a record stamped
'Approved for Publication / In the New Jersey / Tax Court Reports' is
published however the page opens. Neither is a removal: both are the
`publication` role, printed where the page prints them.

WHAT THIS FILE DOES NOT DO. It reads the block above the writing and
nothing else. The footnotes, the paragraphing and the byline PARSE are
core's; the abbreviated titles the byline is written in ('J.T.C.',
'P.J.T.C.') are declared on the profile below, because DEFAULT_ABBREV
stops at 'J.' and without them every one of this court's bylines read as
body prose — 648-652_raymond_boulevard came back with no writing at all
and 236 rows of opinion piled into the headmatter.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import DEFAULT_ABBREV, BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

NJTAXCT = CourtProfile(
    "njtaxct", "Tax Court of New Jersey",
    # ONE PAPER, ONE WRITING: a tax court judge rules alone, so there is no
    # second writing to concur in or dissent from.
    single_writing=True,
    # THE COURT'S OWN ABBREVIATED TITLES, over DEFAULT_ABBREV. Two-word
    # surnames are set in caps beside them ('BEDRIN MURRAY, J.T.C.').
    byline=BylineGrammar(
        style="abbrev",
        abbrev_titles=(("P.J.T.C.", "Presiding Judge of the Tax Court"),
                       ("J.T.C.", "Judge of the Tax Court")) + DEFAULT_ABBREV,
    ),
)
PROFILES[NJTAXCT.court_id] = NJTAXCT


# --------------------------------------------------------------------------
# declared facts — this court's numbers, on this court's paper
# --------------------------------------------------------------------------

_DIVIDER_NO_RAIL = 300.0    # the two columns over whitespace, on a 612pt page
_RAIL_SHED = 6.0            # a ':' this close to the rail column IS the rail
_RAIL_BAND_MAX = 120.0      # wider than this is not one rail (two columns of
                            # colons occur — city_of_new_brunswick sets both)
_MAX_PAGES = 4              # the box may open on page 2 behind a cover

# ---- what the page says about itself --------------------------------------

_COURT_NAME = "TAX COURT OF NEW JERSEY"
_COURT_LABEL = "Tax Court of New Jersey"
_MGMT_OFFICE = "TAX COURT MANAGEMENT OFFICE"
_NOT_FOR_PUB = re.compile(r"^NOT FOR PUBLICATION\b", re.I)
_COMMITTEE = "TAX COURT COMMITTEE ON OPINIONS"
_REPORTER_STAMP = "TAX COURT REPORTS"
# THE REPORTER'S STAMP IS PULLED OUT OF THE BOX (the user, 2026-08-21). It is
# not the court's caption — it is the Committee's mark dropped on top of one,
# and it overprints the pleading box rather than occupying a rung of it. Its
# FACT is still read (`publication_status` becomes 'published'); only the rows
# are removed, and they are attested as `stamp` in Removed rather than
# discarded.
#
# TYPE SIZE FINDS IT, not wording, because the wording is not reliably there.
# The stamp's glyphs interleave with the line beside them, so
# one_main_st_edgewater reads 'Appro:v ed for :P u:blication' and
# 'TIna xth Ceo Nuret w R eJeprosretys' — which is 'In the New Jersey' and
# 'Tax Court Reports' printed on one shared baseline and read alternately.
# zivkovic prints the same three lines cleanly, which is what proves the
# de-interleaving. No phrase test survives that; the SIZE does.
#
# MEASURED over all 42 records: exactly 3 carry any row inside the caption
# band whose size differs from the band's own dominant size, and in all three
# those rows are this stamp (10.0/11.0/23.0 against a 14.0 box). Every other
# record's box is one size throughout, so the test cannot fire where there is
# no stamp.
_STAMP_SIZE_TOL = 1.0
_COVER_TITLE = "corrected opinion notice"
# 'Opinion corrected 1/28/25 – pg. 3 …' / 'Corrected February 28, 2025-
# judges not participating.' — the correction note the corrected opinion
# carries on its OWN first page, under the notice.
_CORRECTION = re.compile(r"^(?:Opinion\s+corrected|Corrected)\b", re.I)

# A TYPED RULE: dashes or underscores at the body rail, with or without the
# pleading 'x' that closes it, and with or without a rail colon spliced in
# ('_______________________________:___________________________________').
_TYPED_RULE = re.compile(r"^[-_]{8,}[-_:x]*$", re.I)

_DECIDED = re.compile(
    r"^(Decided|Submitted|Argued|Reargued|Filed|Revised)\s*:?\s+(.+?)\s*$",
    re.I)
_DATE_CRIT = {"decided": "decision_date", "filed": "decision_date",
              "revised": "decision_date", "submitted": "submitted",
              "argued": "submitted", "reargued": "submitted"}
_BARE_DATE = re.compile(
    r"^(?:Date\s*:\s*)?(?:January|February|March|April|May|June|July|August"
    r"|September|October|November|December)\s+\d{1,2},\s+\d{4}\.?$")
# 'DOCKET NO.: 010531-2022' / 'DOCKET NOS. 000052-2025' / 'Docket No.
# 000092-2021' / 'Docket Number: 009966-2023' / 'Docket number: 007430-2022'
_DOCKET = re.compile(r"^DOCKET\s*(?:NOS?\.?|NUMBERS?)\s*:?\s*(.+)$", re.I)
# a bare number continuing a docket stack (' 000054-2025')
_DOCKET_TAIL = re.compile(r"^\d{6}\s?-\s?\d{4}(?:,?\s*et\s+al\.?)?[.,;]?$")
_RE_LINE = re.compile(r"^RE\s*:\s*(.*)$", re.I)
_FROM_LINE = re.compile(r"^From\s*:", re.I)
_SALUTATION = re.compile(
    r"^(?:Dear\b.*|Counsel|Counselors?|Parties"
    r"|Ladies\s+and\s+Gentlemen)\s*[:,]\s*$", re.I)
# What the right column may call the paper.
# 'Civil Action' is deliberately absent: it is the KIND OF ACTION, not what
# the paper calls itself. It reads as `case-info`, which is what the role
# vocabulary has for caption apparatus that is none of the named things.
_TITLES = frozenset(("OPINION", "OPINION AND ORDER", "ORDER",
                     "MEMORANDUM OPINION"))
_CASE_INFO = re.compile(r"^(?:Civil\s+Action|CIVIL\s+ACTION)$")
_STATUS = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Intervenors?|Third[- ]Party\s+\w+|Movants?)"
    r"(?:\s*/\s*\w+)?[,.]?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# THE BYLINE, in the court's own abbreviated title. This is the STOP, not
# the parse — core's grammar reads it, with the titles declared above. A
# footnote mark ('SUNDAR, P.J.T.C.*') is part of the row.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z’'\-]+\s+){0,2}[A-Z][A-Za-z’'\-]+,\s*"
    r"(?:P\.)?J\.T\.C\.\s*[*†]?\s*\d{0,2}\s*[.:]?$")
# The appearances name themselves — used only to VOUCH for a block the walk
# already bracketed between the dates and the byline.
_COUNSEL = re.compile(
    r"\b(?:Esq\.|Esquire|LLP|LLC|PLLC|P\.C\.|P\.A\.|Attorney|Attorneys"
    r"|Deputy\s+Attorney\s+General|for\s+plaintiffs?|for\s+defendants?"
    r"|self-represented|pro\s+se)\b", re.I)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _plain(group) -> str:
    return _norm(" ".join(l.plain for l in group))


def _ink_x0(line) -> float:
    """The x of the line's first INKED char. pdfio keeps space glyphs, so a
    justified row's leading spaces put `x0` a whole column to the left of
    anything the reader can see — which is how a right-column
    'DOCKET NO: 010387-2025' read as part of the party's name."""
    xs = [c["x0"] for c in line.chars if (c.get("text") or "").strip()]
    return min(xs) if xs else line.x0


def _is_colons(text: str) -> bool:
    t = (text or "").strip()
    return bool(t) and set(t) <= {":"}


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------

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


def _rail_band(rows) -> tuple[float, float] | None:
    """The ':' rail as a COLUMN BAND, measured from the colon cells alone.

    A cell whose whole text is ':' is a rail cell wherever it stands; the
    band is the span those cells occupy. Two colon columns occur on this
    paper (city_of_new_brunswick sets one at 288 and another at 324), which
    is why this is a band and not a single x — but a span wider than
    `_RAIL_BAND_MAX` is not one rail and is refused.
    """
    xs = [l.x0 for group in rows for l in group if _is_colons(l.plain)]
    if len(xs) < 3:
        return None
    lo, hi = min(xs), max(xs)
    if hi - lo > _RAIL_BAND_MAX:
        # keep the densest column only
        x, _n = Counter(round(v) for v in xs).most_common(1)[0]
        lo = hi = float(x)
    return lo - _RAIL_SHED, hi + _RAIL_SHED


def _shed_rail(line, band):
    """``line`` without the rail's own colons, or None when it WAS the rail.

    Identified by COLUMN, never by character: 'DOCKET NO: 010387-2025'
    carries a colon of its own, 40pt right of the band, and keeps it.
    """
    if band is None:
        return line
    lo, hi = band
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == ":" and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _cell(parts, role, page):
    """One column's cell on one row — the empty one keeps its place."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(page), role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}
        self.counsel: list[str] = []

    def emit(self, group, role, centre=False):
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

    def drop(self, group, kind: str) -> None:
        """Removed, and ATTESTED — the Removed box shows it, so a reader can
        see what came out and disagree."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def rule(self, group):
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="left", typed=True))
        self.consumed.update(p.id for p in parts)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="njtaxct")
def read_headmatter_njtaxct(model, geom, **_):
    """Read the Tax Court's box, its letter or its notice cover — or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    stream: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for group in _rows(pm, finder):
            stream.append((pm, sorted(group, key=lambda l: l.x0)))
    if len(stream) < 5:
        return NOTHING

    ctx = _Ctx()
    ctx.crit["court"] = _COURT_LABEL

    # THE COVER, where the court printed one. It names itself in the top
    # third of page 1, over the Management Office's stationery.
    at = 0
    page1 = model.pages[0].number
    head = [(_plain(g)).lower() for pm, g in stream[:8] if pm.number == page1]
    if any(t == _COVER_TITLE for t in head):
        at = _read_cover(ctx, stream, body_x0, body_size)
        if at is None:
            return NOTHING

    # …then the paper itself. The box opens on the typed rule or on the
    # court naming itself in the right column; the letter opens on nothing
    # at all, which is what identifies it.
    band, box_at = _find_box(stream, at, body_x0)
    if box_at is not None:
        return _read_box(ctx, stream, at, box_at, band, geom)
    return _read_letter(ctx, stream, at, body_x0, body_size)


# ---- the cover ------------------------------------------------------------

def _read_cover(ctx, stream, body_x0, body_size) -> int | None:
    """Page 1's 'Corrected Opinion Notice'. Returns the index page 2 starts
    at, or None where the cover is the whole paper (there is none such in
    this corpus, but a cover with nothing behind it is not this contract)."""
    page1 = stream[0][0].number
    seen_re = False
    for i, (pm, group) in enumerate(stream):
        if pm.number != page1:
            return i
        text = _plain(group)
        low = text.lower()
        up = text.upper()
        if low == _COVER_TITLE:
            ctx.emit(group, "title", centre=True)
            ctx.crit.setdefault("title", text)
            ctx.anchor.extend(l.id for l in group)
        elif up.startswith(_COURT_NAME) or _MGMT_OFFICE in up \
                or (group[0].size or 0) < body_size - 1.5:
            ctx.emit(group, "court", centre=True)
        elif _NOT_FOR_PUB.match(text) or _COMMITTEE in up:
            ctx.emit(group, "publication", centre=True)
            ctx.crit.setdefault("publication_status", "unpublished")
        elif _BARE_DATE.match(text):
            ctx.emit(group, "date", centre=True)
        elif _RE_LINE.match(text):
            seen_re = True
            ctx.emit(group, "docket")
            ctx.crit.setdefault("case_name", _RE_LINE.match(text).group(1))
        elif _DOCKET.match(text):
            seen_re = True
            _take_docket(ctx, group, _DOCKET.match(text).group(1))
        elif _FROM_LINE.match(text):
            seen_re = True
            ctx.emit(group, "case-info")
        elif not seen_re:
            ctx.emit(group, "counsel")
            ctx.counsel.append(text)
        else:
            ctx.emit(group, "summary")
    return None


# ---- the box --------------------------------------------------------------

def _find_box(stream, start, body_x0):
    """(rail band, index the box opens at) — or (band, None) for a letter."""
    page = stream[start][0].number if start < len(stream) else None
    rows = [g for pm, g in stream[start:] if pm.number == page]
    band = _rail_band(rows)
    div = (band[1] if band else _DIVIDER_NO_RAIL)
    for i in range(start, len(stream)):
        pm, group = stream[i]
        if pm.number != page:
            break
        text = _plain(group)
        if _TYPED_RULE.match(text):
            return band, i
        # THE COURT NAMING ITSELF IN THE RIGHT COLUMN opens the box just as
        # the typed rule does — two records set no rule at all, and the
        # opening row carries the left party and the rail beside it, so the
        # test is on the PIECE, never on the row.
        if any(_ink_x0(l) >= div and l.plain.strip().lstrip(": ").upper()
               .startswith(_COURT_NAME) for l in group):
            return band, i
        if _SALUTATION.match(text) or _RE_LINE.match(text):
            break
    return band, None


def _read_box(ctx, stream, start, box_at, band, geom):
    """The pleading box, the dates, the appearances — to the byline."""
    page = stream[box_at][0].number
    div = (band[1] if band else _DIVIDER_NO_RAIL)
    body_size = geom.body_size if geom and geom.body_size else 12.0

    # THE APPEARANCES ARE BRACKETED BY THE BYLINE, and nothing else stands
    # between the court's dates and it — the same reading delsuperct needed,
    # for the same reason: a runover row ('Jr., LLC).') names nothing.
    byline_at = None
    for i in range(box_at, len(stream)):
        if _BYLINE.match(_plain(stream[i][1])):
            byline_at = i
            break

    # The box's OWN dominant type size, measured from the box itself — the
    # cover sets 14.0 where `geom.body_size` reports the opinion's 12.0.
    _box_sizes = Counter(
        round(l.size, 1)
        for i in range(box_at, byline_at if byline_at is not None else len(stream))
        for l in stream[i][1] if l.plain.strip() and l.size)
    box_size = _box_sizes.most_common(1)[0][0] if _box_sizes else body_size

    left, right, caption_rows, rail_rows = [], [], [], 0
    box_ids: set[int] = set()
    state = "head"
    published = False
    for i in range(start, len(stream)):
        pm, group = stream[i]
        if byline_at is not None and i >= byline_at:
            break
        text = _plain(group)
        up = text.upper()
        if _REPORTER_STAMP in up:
            published = True

        if state in ("head", "box") and i < box_at:
            if _NOT_FOR_PUB.match(text) or _COMMITTEE in up:
                ctx.emit(group, "publication", centre=True)
                ctx.crit.setdefault("publication_status", "unpublished")
            elif _CORRECTION.match(text):
                ctx.emit(group, "case-info", centre=True)
            elif up.startswith(_COURT_NAME) or _MGMT_OFFICE in up \
                    or (group[0].size or 0) < body_size - 1.5:
                ctx.emit(group, "court", centre=True)
            else:
                ctx.emit(group, "case-info", centre=True)
            continue

        if state != "counsel" and _DECIDED.match(text):
            state = "counsel"
            mo = _DECIDED.match(text)
            ctx.emit(group, "date")
            key = _DATE_CRIT.get(mo.group(1).lower())
            if key:
                ctx.crit.setdefault(key, mo.group(2).rstrip("."))
            continue

        if state == "counsel":
            ctx.emit(group, "counsel")
            ctx.counsel.append(text)
            continue

        # inside the box
        if _TYPED_RULE.match(text):
            state = "box"
            if left or right:
                _flush(ctx, left, right, band, caption_rows, rail_rows,
                       box_ids, page)
                left, right, caption_rows, rail_rows = [], [], [], 0
                box_ids = set()
            ctx.rule(group)
            continue
        state = "box"
        # THE STAMP COMES OUT FIRST. Right of the divider and off the box's
        # own type size — see _STAMP_SIZE_TOL. Read the fact, remove the rows.
        _stamp = [l for l in group
                  if l.size and abs(l.size - box_size) > _STAMP_SIZE_TOL
                  and _ink_x0(l) >= div]
        if _stamp and len(_stamp) == len([l for l in group if l.plain.strip()]):
            published = True
            ctx.drop(group, "stamp")
            continue
        lcell, rcell, rail_hit = [], [], False
        for line in group:
            if any(l is line for l in _stamp):
                published = True
                ctx.drop([line], "stamp")
                continue
            shed = _shed_rail(line, band)
            if shed is None:
                rail_hit = True
                box_ids.add(line.id)
                continue
            box_ids.add(line.id)
            if _is_colons(shed.plain):
                rail_hit = True
                continue
            (rcell if _ink_x0(shed) >= div else lcell).append(shed)
        if rail_hit:
            rail_rows += 1
        if not lcell and not rcell:
            ctx.consumed.update(l.id for l in group)
            continue
        left.append(_cell(lcell, "caption", pm.number))
        rtext = _norm(re.sub(r"<[^>]+>", "", _cell(rcell, "", pm.number).text))
        role = "caption"
        if rtext:
            role = _right_role(ctx, rtext, rcell)
        right.append(_cell(rcell, role, pm.number))
        ltext = _norm(re.sub(r"<[^>]+>", "", left[-1].text))
        if ltext:
            caption_rows.append(ltext)
        ctx.consumed.update(l.id for l in group)

    if left or right:
        _flush(ctx, left, right, band, caption_rows, rail_rows, box_ids, page)

    if published:
        ctx.crit["publication_status"] = "published"
    if ctx.counsel:
        ctx.crit["attorneys"] = " ".join(ctx.counsel)
    ctx.crit["headmatter_style"] = "colon-rail box"
    out = ctx.result()
    out["doc_type_final"] = m.DocType.OPINION
    return out


def _right_role(ctx, rtext, rcell) -> str:
    """What the right column is saying on this row."""
    up = rtext.upper()
    if up.startswith(_COURT_NAME):
        return "court"
    mo = _DOCKET.match(rtext)
    if mo:
        _take_docket(ctx, None, mo.group(1))
        return "docket"
    if _DOCKET_TAIL.match(rtext):
        _take_docket(ctx, None, rtext)
        return "docket"
    if _REPORTER_STAMP in up or up.startswith("APPROVED FOR PUBLICATION") \
            or up == "IN THE NEW JERSEY":
        return "publication"
    if up in _TITLES:
        ctx.crit.setdefault("title", rtext)
        if rcell:
            ctx.anchor.extend(l.id for l in rcell)
        return "title"
    if _CASE_INFO.match(rtext):
        return "case-info"
    return "case-info"


def _take_docket(ctx, group, value: str) -> None:
    value = _norm(value).rstrip(".,;")
    if not value:
        return
    if ctx.crit.get("docket_number") is None:
        ctx.crit["docket_number"] = value
    else:
        others = ctx.crit.setdefault("other_dockets", [])
        if value not in others and value != ctx.crit["docket_number"]:
            others.append(value)
    if group is not None:
        ctx.emit(group, "docket")


def _flush(ctx, left, right, band, caption_rows, rail_rows, box_ids, page):
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=":" if band else None,
        rail_rows=rail_rows, style_id="colon-rail",
        prov=m.Prov(page, tuple(sorted(box_ids)))))
    if caption_rows:
        ctx.crit.setdefault("caption", []).extend(caption_rows)
        _parties(ctx, caption_rows)


def _parties(ctx, rows) -> None:
    """The parties either side of the pivot, built from the party NAMES.

    A party may run over two or three rows ('ESTATE OF MICHAEL R.' /
    'MONIHAN AND' / 'HOLLY P. MONIHAN,'), so a name accumulates until a
    status label or the pivot closes it — joining the rows wholesale yields
    'ESTATE … Plaintiffs, v. DIRECTOR …'.
    """
    sides: list[list[str]] = [[]]
    buf: list[str] = []
    for row in rows:
        t = row.strip()
        if _PIVOT.match(t):
            if buf:
                sides[-1].append(_norm(" ".join(buf)).rstrip(",")); buf = []
            sides.append([])
            continue
        if _STATUS.match(t):
            if buf:
                sides[-1].append(_norm(" ".join(buf)).rstrip(",")); buf = []
            continue
        buf.append(t)
    if buf:
        sides[-1].append(_norm(" ".join(buf)).rstrip(","))
    sides = [s for s in sides if s]
    if len(sides) == 2:
        a, b = " and ".join(sides[0]), " and ".join(sides[1])
        ctx.crit.setdefault("parties", [a, b])
        ctx.crit.setdefault("case_name", f"{a} v. {b}")


# ---- the letter -----------------------------------------------------------

def _read_letter(ctx, stream, start, body_x0, body_size):
    """The stationery, the date, the addressees and the 'Re:' — to the
    salutation, which OPENS the letter and is never claimed."""
    page = stream[start][0].number
    seen_date = seen_re = False
    took = 0
    for i in range(start, len(stream)):
        pm, group = stream[i]
        if pm.number != page:
            break
        text = _plain(group)
        up = text.upper()
        if _SALUTATION.match(text):
            break
        if _NOT_FOR_PUB.match(text) or _COMMITTEE in up:
            ctx.emit(group, "publication", centre=True)
            ctx.crit.setdefault("publication_status", "unpublished")
        elif not seen_date and (up.startswith(_COURT_NAME)
                               or (group[0].size or 0) < body_size - 1.5):
            ctx.emit(group, "court", centre=True)
        elif _BARE_DATE.match(text):
            seen_date = True
            ctx.emit(group, "date", centre=True)
            ctx.crit.setdefault(
                "decision_date", re.sub(r"^Date\s*:\s*", "", text).rstrip("."))
        elif _RE_LINE.match(text):
            seen_re = True
            ctx.emit(group, "docket")
            ctx.crit.setdefault("case_name", _norm(_RE_LINE.match(text).group(1)))
        elif _DOCKET.match(text):
            seen_re = True
            _take_docket(ctx, group, _DOCKET.match(text).group(1))
        elif seen_re:
            # past the 'Re:' block the letter has begun — the reader stops.
            break
        elif seen_date:
            ctx.emit(group, "counsel")
            ctx.counsel.append(text)
        else:
            ctx.emit(group, "court", centre=True)
        took += 1
    if not seen_re:
        return NOTHING
    if ctx.counsel:
        ctx.crit["attorneys"] = " ".join(ctx.counsel)
    ctx.crit["headmatter_style"] = "letter opinion"
    out = ctx.result()
    out["doc_type_final"] = m.DocType.OPINION
    return out
