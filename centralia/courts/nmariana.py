"""Supreme Court of the Commonwealth of the Northern Mariana Islands
('nmariana').

Everything unique to nmariana lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py; this module adds the reader only, so
importing it can never raise a duplicate profile.

THE CONTRACT — an engraved slip cover, centred on the page axis, on a letter
sheet. The court's own e-filing stamp is set in the top right corner and
core already identifies it as a stamp; the running head on pages 2..n is
core's too. Everything between them is this reader's.

    ┌─ page 1 ────────────────────────────────────────────────────────┐
    │                                       E-FILED          8pt      │
    │                                       CNMI SUPREME COURT  stamp │
    │                                       Filing ID: 78716320       │
    │                             IN THE                    12.0  ┐   │
    │                        Supreme Court                  20.0  │   │
    │                             OF THE                     9.5  │THE│
    │      Commonwealth of the Northern Mariana Islands     20.0  ┘MAST│
    │  ANAKS OCEAN VIEW HILL SAIPAN HOMEOWNERS' ASSN, LTD., 11.0  ┐   │
    │                     Petitioner-Appellant,             11.0  │THE│
    │                             v.                        11.0  │CAP│
    │                   PERRY INOS JR., ET AL.,             11.0  │TION│
    │                    Respondent-Appellees,              11.0  │   │
    │                             AND                        9.0  │   │
    │                 ATKINS KROLL SAIPAN, INC.,            11.0  │   │
    │                    Applicant-Appellee.                11.0  ┘   │
    │            Supreme Court No. 2024-SCC-0011-CIV        11.0  DOCKET│
    │                        SLIP OPINION                   11.0  TITLE│
    │                     Cite as: 2026 MP 1                11.0  CITE │
    │                   Decided March 13, 2026              11.0  DATE │
    │           CHIEF JUSTICE ALEXANDRO C. CASTRO           11.0  ┐    │
    │      JUSTICE PRO TEMPORE ROBERT J. TORRES, JR.        11.0  │BENCH│
    │      JUSTICE PRO TEMPORE F. PHILIP CARBULLIDO         11.0  ┘    │
    │              Superior Court No. 22-0103-CV            11.0  ┐ORIGIN│
    │     Judge Pro Tempore David A. Wiseman, Presiding     11.0  ┘     │
    └─────────────────────────────────────────────────────────────────┘

THE ROW SEQUENCE IS THE READING, and it is the same on all 32 records:
masthead, caption, docket, title, cite, date, a three-judge bench, the
origin. Every row is classified by ITS OWN vocabulary rather than by an
ordinal, so the six records that set an extra caption row need no special
case — and neither does `maratita_v._chcc`, which CONSOLIDATES two appeals
and prints the caption/docket pair twice. The caption band therefore closes
at the CITATION, not at the first docket. What the sequence is used for
is the CLOSE: `Cite as:`, `Decided`, a bench and an origin must all be
found, or the record is handed back to core whole.

    Cite as: …                32/32        a three-judge bench   32/32
    Decided …                 32/32        Supreme Court No. …   32/32

TWO PAPERS SIGN THE SAME COVER. 28 records print 'SLIP OPINION'; the other
4 are orders and print their own title instead ('ORDER DENYING MOTION FOR
STAY OF MANDATE; DENYING MOTION TO RECONSIDER ORDER DENYING PETITION FOR
REHEARING', across two rows). Both are the paper naming itself, so both take
`title` — a reader keyed to the words 'SLIP OPINION' would have left the
orders' titles unclaimed directly above the citation, which is where an
unclaimed row opens a phantom writing.

THE TEXT LAYER WELDS WORDS TOGETHER, and every pattern here is built to
survive it. Four rows in the corpus lose a space: 'Decided June25, 2025',
'JUSTICEPRO TEMPORE ROBERTJ. TORRES, JR.', 'JUSTICE PRO TEMPOREWESLEY
M.BOGDAN' and 'PresidingJudge Joseph N. Camacho, Presiding'. The bench and
origin patterns therefore make every internal space optional; keyed to the
printed spacing they would have lost a judge from the panel and an origin
from its record.

ONE RECORD COMES FROM THE NINTH CIRCUIT, not the Superior Court: a certified
question whose cover prints 'UNITED STATES COURT OF APPEALS, NINTH CIRCUIT'
and 'D.C. No. 1:09-CV-00023' between its two dockets. Both rows are the
court below naming itself, so both take `lower-court` — the origin band is
not a fixed pair of rows, it is whatever names the tribunal underneath.

WHAT THIS READER DOES NOT TOUCH. The byline that opens page 2 ('C.J.
CASTRO:') is left in the stream: core opens the majority on it.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

STYLE_COVER = "engraved slip cover"

# ---- nmariana's declared facts (measured over all 32 records) ------------
# THE MASTHEAD: 'Supreme Court' and 'Commonwealth of the Northern Mariana
# Islands' at 20.0pt over an 11.0pt body, with 'IN THE' (11-12pt) and 'OF
# THE' (9.0-9.5pt) set between them. Nothing else on the cover is above 12pt.
_MASTHEAD_SIZE = 15.0
_MASTHEAD_WORDS = re.compile(r"^(?:IN\s+THE|OF\s+THE)$", re.I)
# THE COURT'S OWN DOCKET, and the only row that carries it.
_DOCKET = re.compile(r"^Supreme\s+Court\s+No\.?\s*(?P<docket>[\w\-/]+)", re.I)
# THE PAPER NAMING ITSELF: 'SLIP OPINION' on 28 records, an ORDER title on
# the other 4. An order's title is set in capitals and may run to two rows.
_SLIP = re.compile(r"^SLIP\s+OPINION$")
_ORDER_TITLE = re.compile(r"^(?:ORDER|OPINION|JUDGMENT|AMENDED)\b[A-Z\s;,'’.\-]*$")
_TITLE_WRAP = re.compile(r"^[A-Z][A-Z\s;,'’.\-]*$")
# THE CITE and THE DATE, the two rows that close the apparatus. 'June25'
# welded is why the space before the day is optional.
_CITE = re.compile(r"^Cite\s+as:\s*(?P<cite>.+?)\.?$", re.I)
_DATE = re.compile(r"^Decided\s+(?P<date>[A-Z][a-z]+\s*\d{1,2},\s*\d{4})\.?$")
# THE BENCH. Every internal space optional — see the module docstring on the
# welded text layer.
_BENCH = re.compile(r"^(?:CHIEF\s*JUSTICE|ASSOCIATE\s*JUSTICE"
                    r"|JUSTICE\s*(?:PRO\s*TEMPORE)?)\s*[A-Z]")
# THE ORIGIN: the tribunal below, and who sat in it. 'Presiding' closes the
# judge's row on all 32; the Ninth Circuit record names a federal court and
# a district docket instead.
_ORIGIN = re.compile(r"^(?:Superior\s+Court\b|(?:Presiding\s*|Associate\s*"
                     r"|Chief\s*)?Judge\b|UNITED\s+STATES\s+COURT\b"
                     r"|D\.\s?C\.\s+No\.)", re.I)
# THE CAPTION IS FENCED, AND THE FENCE IS DRAWN. This court rules a line
# above its caption and another below it, and the parties stand between them.
# MEASURED on all 32 records: every one prints two rules of exactly 322.0pt on
# page 1 and nothing else on the page comes near that measure.
#
# The fence is what tells a court that IS a party from the court BELOW. On an
# original-jurisdiction petition the respondent is the trial court itself —
# in_re_commonwealth is captioned 'IN RE COMMONWEALTH … Petitioner, v. SUPERIOR
# COURT OF THE COMMONWEALTH OF THE NORTHERN MARIANA ISLANDS, Respondent,' — so
# `_ORIGIN`, which reads a row opening 'Superior Court', took the respondent
# for the origin and cut the party in half: the name went to `lower-court` and
# its own wrapped continuation 'ISLANDS,' stayed `caption` (the user,
# 2026-08-21). Inside the fence a court name is a PARTY; the origin this record
# really has is printed below the fence, where it was read correctly all along
# ('Superior Court Criminal Action No. 22-0183' / 'Presiding Judge Roberto C.
# Naraja').
_FENCE_MIN_W = 250.0
# THE PIVOT and the party STATUS labels, for reading the caption's parties.
_PIVOT = re.compile(r"^v\.?$", re.I)
_JOINER = re.compile(r"^AND$", re.I)
_STATUS = re.compile(r"^(?:[A-Z][a-z]+-)?(?:Appellants?|Appellees?"
                     r"|Petitioners?|Respondents?|Plaintiffs?|Defendants?"
                     r"|Applicants?|Intervenors?|Real\s+Part(?:y|ies))\b",
                     re.I)


@decider("headmatter.read", court="nmariana")
def read_headmatter_nmariana(model, geom, **_):
    """Read the engraved slip cover on page 1, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 108.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 10:
        return NOTHING
    # The drawn fence around the caption — see _FENCE_MIN_W.
    _wide = sorted((r for r in getattr(page1, "h_rules", [])
                    if (r.x1 - r.x0) > _FENCE_MIN_W), key=lambda r: r.top)
    fence = (_wide[0].top, _wide[1].top) if len(_wide) >= 2 else None

    def in_fence(group) -> bool:
        return fence is not None and fence[0] < group[0].top < fence[1]
    # ---- the dispatch: the masthead, at a size nothing else on the cover
    # reaches, with the court's name in it.
    mast = [i for i, g in enumerate(rows)
            if (g[0].size or 0.0) >= _MASTHEAD_SIZE]
    if not mast:
        return NOTHING
    last_mast = mast[-1]
    if not any("Supreme Court" in _text(rows[i]) for i in mast):
        return NOTHING

    ctx = _Ctx()
    # ---- the masthead: the court naming itself, connectors included ------
    for group in rows[:last_mast + 1]:
        text = _norm(_text(group))
        if (group[0].size or 0.0) >= _MASTHEAD_SIZE \
                or _MASTHEAD_WORDS.match(text):
            ctx.emit(group, "court")
        else:
            return NOTHING      # something stands inside the masthead
    ctx.crit["court"] = " ".join(
        _norm(_text(rows[i])) for i in mast)

    # ---- every row below it, classified by its own vocabulary -----------
    cap_rows: list[str] = []
    bench: list[str] = []
    seen = {"docket": False, "cite": False, "date": False, "origin": False}
    idx = last_mast + 1
    while idx < len(rows):
        group = rows[idx]
        text = _norm(_text(group))
        docket = _DOCKET.match(text)
        cite = _CITE.match(text)
        date = _DATE.match(text)
        if docket:
            ctx.emit(group, "docket")
            if seen["docket"]:
                ctx.crit.setdefault("other_dockets", []).append(
                    _norm(docket.group("docket")))
            else:
                ctx.crit["docket_number"] = _norm(docket.group("docket"))
            seen["docket"] = True
        elif cite:
            ctx.emit(group, "citation")
            ctx.crit["citation"] = _norm(cite.group("cite"))
            seen["cite"] = True
        elif date:
            ctx.emit(group, "date")
            ctx.crit["decision_date"] = _norm(date.group("date"))
            seen["date"] = True
        elif _BENCH.match(text):
            ctx.emit(group, "panel")
            bench.append(text)
        elif _ORIGIN.match(text) and not in_fence(group):
            ctx.emit(group, "lower-court")
            _origin(ctx, text)
            seen["origin"] = True
        elif _SLIP.match(text) or (seen["docket"] and not seen["cite"]
                                  and _ORDER_TITLE.match(text)):
            # THE PAPER'S NAME, which an order wraps across two rows.
            ctx.emit(group, "title")
            title = text
            while idx + 1 < len(rows):
                nxt = _norm(_text(rows[idx + 1]))
                if _CITE.match(nxt) or _DOCKET.match(nxt) \
                        or _BENCH.match(nxt) or not _TITLE_WRAP.match(nxt):
                    break
                idx += 1
                ctx.emit(rows[idx], "title")
                title = title.rstrip() + " " + nxt
            ctx.crit.setdefault("title", title)
        elif not seen["cite"]:
            # ABOVE THE CITATION AND NAMED BY NOTHING ELSE: the caption.
            # NOT 'above the docket' — maratita_v._chcc CONSOLIDATES two
            # appeals and prints caption/docket TWICE, so the second
            # caption stands below the first docket and a docket boundary
            # refused the whole record.
            cap_rows.append(text)
            ctx.emit(group, "caption")
        else:
            # NO CATCH-ALL. An unidentified row below the docket would either
            # be mis-tinted or leave a hole in the claim, and both are worse
            # than handing the record back to core whole.
            return NOTHING
        idx += 1

    if not (cap_rows and all(seen.values()) and len(bench) >= 2):
        return NOTHING
    ctx.crit["caption"] = cap_rows
    ctx.crit["panel_line"] = "; ".join(bench)
    ctx.crit["panel"] = [_bench_name(b) for b in bench]
    ctx.crit["judges"] = "; ".join(ctx.crit["panel"])
    _parties(ctx, cap_rows)
    ctx.crit["headmatter_style"] = STYLE_COVER
    return ctx.result()


def _bench_name(row: str) -> str:
    """'JUSTICE PRO TEMPORE ROBERT J. TORRES, JR.' -> the name, office
    stripped. The welded forms lose their space, so the office is removed by
    a pattern that does not need one."""
    name = re.sub(r"^(?:CHIEF\s*JUSTICE|ASSOCIATE\s*JUSTICE"
                  r"|JUSTICE\s*(?:PRO\s*TEMPORE)?)\s*", "", row)
    return _norm(name).rstrip(".").strip()


def _origin(ctx, text: str) -> None:
    """The tribunal below, and its docket where the row carries one."""
    dock = re.search(r"No\.?\s*([\w\-:/]+)", text)
    if dock and not re.match(r"^(?:Presiding|Associate|Chief)?\s*Judge",
                             text, re.I):
        ctx.crit.setdefault("lower_court_docket", []).append(
            _norm(dock.group(1)))
        ctx.crit.setdefault("lower_court", text)
    else:
        judge = re.sub(r"^(?:Presiding\s*|Associate\s*|Chief\s*)?Judge"
                       r"(?:\s*Pro\s*Tempore)?\s*", "", text, flags=re.I)
        judge = re.sub(r",?\s*Presiding\.?$", "", judge, flags=re.I)
        if judge.strip():
            ctx.crit.setdefault("lower_court_judge", _norm(judge))


def _parties(ctx, cap_rows: list[str]) -> None:
    """The caption's party NAMES: the rows that are neither a status label,
    the pivot, nor the joiner the court sets between two respondents."""
    names = [r for r in cap_rows
             if not (_STATUS.match(r) or _PIVOT.match(r) or _JOINER.match(r))]
    if names:
        ctx.crit["parties"] = [n.rstrip(",") for n in names]
        sides = [n.rstrip(",") for n in names]
        if len(sides) >= 2:
            ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


def _rows(pm, finder) -> list[list]:
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


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}

