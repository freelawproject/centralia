"""Armed Services Board of Contract Appeals ('asbca').

NOT A COURT. The Board is an agency tribunal that hears a contractor's
appeal from a contracting officer's final decision under the Contract
Disputes Act, and its cover says so in every line: there is no plaintiff
and no defendant, there is no `v.`, and the case is named for ONE party.
Reading it as a court caption is the first mistake available, and
`criteria.parties` is rendered `" v. ".join(...)` at render/html.py:307 —
so the only safe thing to put there is the single party the page names.

**ONE CONTRACT, PRINTED 32 TIMES OUT OF 32.** There is no style split here
the way afcca or ca6 have one; the Board sets one cover and varies only
what it puts in the cells.

    ┌───────────────────────────────────────────────────────────────────┐
    │      ARMED SERVICES BOARD OF CONTRACT APPEALS      the BANNER     │
    │                                                                   │
    │  Appeal of -            )                         the OPENER      │
    │                         )                                         │
    │  Accu-Aire Mechanical,  ) ASBCA No. 64204         party / DOCKET  │
    │  LLC                    )                                         │
    │  Under Contract No.     )                         the INSTRUMENT  │
    │    FA3016-19-C-A085     )                                         │
    │                                                                   │
    │  APPEARANCES FOR THE APPELLANT:  Johnathan M. Bailey, Esq.        │
    │                                  Kristin E. Zachman, Esq.         │
    │                                  Cokinos-Young                    │
    │                                  San Antonio, TX     the ROSTER   │
    │  APPEARANCES FOR THE GOVERNMENT: Caryl A. Potter, III, Esq.       │
    │                                  Air Force Deputy Chief Trial …   │
    │                                                                   │
    │      OPINION BY ADMINISTRATIVE JUDGE MCNULTY      the TITLE       │
    │      ───────────────────────────────────────      (UNDERLINED)    │
    │  The parties have resolved their dispute …        (the paper)     │
    └───────────────────────────────────────────────────────────────────┘

THE RAIL IS THE PARSER, ca6's rule applied to the Board's glyph. The cover
stacks a `)` column down the middle of the caption — 5 glyphs on 21
records, 6 on 8, 8 on one and 9 on one, at x0 = 300 / 314 / 316 / 318 /
320 / 328 / 330 / 332 / 339 depending on how the page is set. Its x is
measured, never assumed, and NOTHING is decided by what a row says: the
band the column spans IS the caption, what stands above it is the banner,
what stands below it is the roster. A page that draws no such column is
not this contract and the reader returns NOTHING.

    THE COLUMN IS A CONTIGUOUS RUN, and the run is what ends it. The rows
    step 14.9-15.0pt. vision_distributors closes a body sentence with a
    `)` that lands 358pt below the caption in the very same column, and
    left in the stack it stretched the caption's band over eight
    paragraphs of the opinion. So the column ends at the first vertical
    step of more than three of its own rows (45.0pt) — afcca's measure,
    and the same headroom holds here.

THE BANNER IS THE ROW ABOVE THE RAIL, and it is read by POSITION, not by
its words. It is set at BODY SIZE and it is not bold — there is no type
signal to find it with — so the landmark is the rail: the LAST row above
the column is the Board naming itself, on all 32. Anything above THAT is
the protective-order notice the Board stamps on a redacted release
(wild_hare_haulers prints three rows of it), which is furniture and is
recorded `Dropped`.

THE TITLE IS THE ROW THE PAGE UNDERLINES. The Board rules its own title —
a drawn rect 10.4pt under the row whose ENDS COINCIDE WITH IT (within 4pt
at both ends, on all 32). That is the general test for an underline rather
than a fence, and here it is also the boundary: the roster runs from the
foot of the rail to the first underlined row, and the underlined row and
everything after it belong to the writing. The reader does not claim it —
it is the writing's own head and its anchor — but it READS it, because it
is the only place the paper names itself and the only place the author is
announced.

    'ORDER OF DISMISSAL' (17), 'DISMISSAL ORDER' (1) — an order.
    'OPINION BY ADMINISTRATIVE JUDGE MCNULTY' (14) — an opinion, and the
    author is ANNOUNCED there and signed nowhere core can see: the
    signature block is a name row over 'Administrative Judge' over
    'Armed Services Board' / 'of Contract Appeals', and
    `conformed_signature_author` knows 'administrative law judge' but not
    'Administrative Judge'. So the announcement is handed to core, which
    parses it with the grammar declared below and credits the lead writing
    — only where the document prints no byline of its own.

WHAT THE LEFT COLUMN STATES, in the order the Board prints it: the OPENER
('Appeal of -', 'Appeals of -', 'Petition of -'), the party's name over as
many rows as it takes, and the INSTRUMENT ('Under Contract No. …', with
its task-order and delivery-order continuations indented beneath it). The
opener and the instrument are LABELS, not names — the same kind of closed
vocabulary as core's own `No.` / `Docket No.` openers — and they are the
only two words this reader matches. Everything between them is the party,
whatever it is called.

WHAT THE RIGHT COLUMN STATES: the docket, and only ever the docket.
'ASBCA No. 64204', 'ASBCA Nos. 63510, 64085', 'ASBCA No. 63471-ADR' (an
alternative-dispute-resolution proceeding), 'ASBCA No. 63710-EAJA' (a fee
application), 'ASBCA No. 64581-PET' (a petition to direct a decision), and
the seven-appeal stacks that wrap onto three further rows. The first is
`docket_number` and the rest are `other_dockets`.

THE CONTRACT IS NOT A DOCKET AND NOT A LOWER COURT. Core was reading
`W912ER-25-P-0004` out of the instrument row as tyd_services' docket
number. There is no criteria key for the instrument an appeal arises
under — `lower_court_docket` means the number the tribunal BELOW gave the
case, and a contract number is not that — so the instrument rows are
tagged `case-info` and render verbatim in place, which is where the record
of them belongs.

THE DECISION DATE IS NOT ON THE COVER. The Board dates its papers at the
foot, over the signature ('Dated:  April 29, 2026'), and the certification
repeats it. The row belongs to the writing and is not claimed; it is read
for `criteria.decision_date`, which core otherwise leaves empty on all 32.
"""

from __future__ import annotations

import re
from collections import Counter

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

STYLE = "asbca parenthetical rail cover"

# ---- the Board's declared facts (measured over all 32 records) -----------
# THE RAIL. A ')' column down the middle of the caption. 5 glyphs on 21
# records, 6 on 8, 8 on efs_ebrex, 9 on constellation; never fewer than 5.
_RAIL_GLYPH = ")"
_RAIL_FLOOR = 4
_RAIL_WINDOW = 4.5
# The column's rows step 14.9-15.0pt; 45.0 is three of them, which is 30pt
# clear of the widest real step and 313pt clear of the nearest stray.
_RAIL_GAP = 45.0
# THE UNDERLINE. A drawn rule whose ends coincide with the row above it.
# Measured on all 32: the drop is 10.3-10.5pt and both ends agree to 0.1pt.
_UNDER_DROP = 22.0
_UNDER_TOL = 4.0
# THE OPENER of the left column — 'Appeal of -' (20), 'Appeals of -' (11),
# 'Petition of -' (1). A closed label vocabulary, never a name.
_OPENER = re.compile(r"^(Appeals?|Petitions?|Applications?)\s+of\b", re.I)
# THE INSTRUMENT the appeal arises under — 'Under Contract No. …',
# 'Under Contract Nos. …'. The other label, and the last one.
_INSTRUMENT = re.compile(r"^Under\s+Contract\b", re.I)
# THE DOCKET, as the right column prints it.
_DOCKET_ROW = re.compile(r"^ASBCA\s+Nos?\.\s*(.+)$", re.I)
_DOCKET_TOKEN = re.compile(r"^\d{4,6}(?:-[A-Z]{2,4})?$")
# WHAT THE PAPER CALLS ITSELF, and who it says wrote it.
_OPINION_BY = re.compile(r"^OPINION\s+BY\s+(.+?)\s*$", re.I)
# …AND THE ANNOUNCEMENT MAY CARRY THE RULE IT WAS DECIDED UNDER on the very
# same printed row: 'OPINION BY ADMINISTRATIVE JUDGE STINSON UNDER BOARD
# RULE 12.3'. Every other record sets that clause on a row of its own
# ('PURSUANT TO BOARD RULE 12.2', 'ON THE GOVERNMENT’S MOTION FOR SUMMARY
# JUDGMENT'), and those rows belong to the writing. The clause openers are
# a closed vocabulary; a surname is never one of them.
_RULE_CLAUSE = re.compile(r"\s+(?:UNDER|PURSUANT\s+TO|ON|UPON|IN)\s+.*$",
                          re.I)
# THE APPEARANCE LABEL. 'APPEARANCE FOR THE APPELLANT:' /
# 'APPEARANCES FOR THE GOVERNMENT:' / '… FOR THE PETITIONER:'. Read only to
# confirm the roster band is a roster — membership is decided by position.
_APPEARANCE = re.compile(r"^APPEARANCES?\s+FOR\b", re.I)
# THE DATE THE BOARD PUTS ON THE PAPER, at the foot over the signature.
_DATED = re.compile(r"^Dated:\s*(.+?)\s*$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile ---------------------------------------------------------
# THE BENCH IS 'ADMINISTRATIVE JUDGE' AND NOTHING ELSE. Every signature in
# the corpus reads '<NAME>' / 'Administrative Judge' / (optionally
# 'Chairman' | 'Acting Chairman' | 'Vice Chairman' | 'Acting Vice
# Chairman') / 'Armed Services Board' / 'of Contract Appeals'. The Recorder
# ('PAULLA K. GATES-LEWIS' / 'Recorder, Armed Services Board of Contract
# Appeals') certifies the copy and is never an author, so 'Recorder' is not
# a title here.
#
# REVERSED, because the announcement is title-first: the cover prints
# 'OPINION BY ADMINISTRATIVE JUDGE MCNULTY' and the reader hands core the
# tail as printed. The prose form would have to be synthesized, and it
# cannot carry 'D’ALESSANDRIS' — core's prose `_NAME` admits no apostrophe,
# where the reversed parser does.
register(CourtProfile(
    "asbca",
    "Armed Services Board of Contract Appeals",
    byline=BylineGrammar(
        style="reversed",
        rev_titles=("ADMINISTRATIVE JUDGE", "ADMINISTRATIVE JUDGES")),
    rollout="migrated",
))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="asbca")
def read_headmatter_asbca(model, geom, **_):
    """Read an ASBCA cover — banner, parenthetical caption, roster — or
    NOTHING.

    The claim stops at the underlined title, which is the writing's own
    head. Nothing below it is touched: the body, the signature band, the
    Recorder's certification and the footnote zones are assembled exactly
    as they are for any other tribunal."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    pm = model.pages[0]

    rail = _rail(pm)
    if rail is None:
        return NOTHING

    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(pm, finder)
    if len(rows) < 6:
        return NOTHING

    title_row = _title_row(pm, rail["bottom"])
    if title_row is None:
        return NOTHING
    cut = title_row.top - 1.0

    above, box, roster = [], [], []
    for g in rows:
        top = g[0].top
        if top < rail["top"] - 2.0:
            above.append(g)
        elif top <= rail["bottom"] + 2.0:
            box.append(g)
        elif top < cut:
            roster.append(g)
    if not above or not box or not roster:
        return NOTHING
    # THE ROSTER MUST SAY IT IS ONE. Position found the band; this is the
    # gate that says the band is what the contract expects there.
    if not any(_APPEARANCE.match(_norm(" ".join(l.plain for l in g)))
               for g in roster):
        return NOTHING

    ctx = _Ctx()

    # 1 — the banner is the LAST row above the rail; the rest is the
    #     protective-order notice, which is furniture.
    for g in above[:-1]:
        ctx.drop(g, "notice")
    banner = above[-1]
    ctx.emit(banner, "court", centre=True)
    ctx.crit["court"] = _norm(" ".join(l.plain for l in banner))

    # 2 — the caption box, split at the rail's own column.
    block, left_txt, right_txt = _box(box, rail, pm, ctx)
    if block is None:
        return NOTHING
    ctx.items.append(block)
    _read_left(ctx, left_txt)
    _read_right(ctx, right_txt)

    # 3 — the roster, every row of it, as the page prints it.
    # THE ROSTER'S HANGING INDENT is the page's own grouping: the label
    # stands at the body rail and every entry under it is set 262-286pt in,
    # in the caption's right column. Reproduced, or the block reads as a
    # flat list and the two appearances run together.
    counsel: list[str] = []
    for g in roster:
        first = min(g, key=lambda l: l.x0)
        rel = (min(first.x0 - body_x0, pm.width * 0.6)
               if first.x0 > body_x0 + 12 else 0.0)
        ctx.emit(g, "counsel", centre=False, rel=rel)
        counsel.append(_norm(" ".join(
            line.plain for line in sorted(g, key=lambda l: l.x0))))
    joined = " ".join(t for t in counsel if t)
    if joined:
        ctx.crit["attorneys"] = joined[:2000]

    # 4 — what the title states. READ, never claimed: the row is the
    #     writing's head and its anchor.
    title = _norm(title_row.plain)
    announced, doc_type = None, None
    if title:
        ctx.crit["title"] = title
        by = _OPINION_BY.match(title)
        if by:
            announced = _norm(_RULE_CLAUSE.sub("", by.group(1)))
            doc_type = m.DocType.OPINION
        elif "ORDER" in title.upper():
            doc_type = m.DocType.ORDER

    # 5 — the date the Board put on the paper, at the foot over the
    #     signature. Not on the cover, and not claimed.
    dated = _dated(model)
    if dated:
        ctx.crit["decision_date"] = dated

    ctx.crit["headmatter_style"] = STYLE
    out = ctx.result(doc_type)
    if announced:
        # ANNOUNCED, NEVER SIGNED. Core parses it with the grammar declared
        # above and credits the lead writing — only where the document
        # prints no byline of its own, which it never does.
        out["announced_author"] = announced
    return out


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The caption's ')' column, or None.

    Read as ca6 and afcca read theirs: the most common x0 among the page's
    ')' glyphs, kept only when enough of them stack there in one contiguous
    run. A ')' that closes real text is not in the column and cannot reach
    the floor."""
    paren = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if len(paren) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in paren).most_common(1)[0]
    stack = [c for c in paren if abs(c["x0"] - x) < _RAIL_WINDOW]
    tops = sorted({round(c["top"], 1) for c in stack})
    if not tops:
        return None
    runs: list[list[float]] = [[tops[0]]]
    for t in tops[1:]:
        if t - runs[-1][-1] > _RAIL_GAP:
            runs.append([])
        runs[-1].append(t)
    band = max(runs, key=len)
    stack = [c for c in stack
             if band[0] - 0.5 <= round(c["top"], 1) <= band[-1] + 0.5]
    if len(stack) < _RAIL_FLOOR:
        return None
    return {"x": float(x), "glyph": _RAIL_GLYPH,
            "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _title_row(pm, rail_bottom: float):
    """The first row below the rail that the page UNDERLINES.

    A drawn rule whose ends coincide with the row above it is an underline,
    not a fence — the general test, and here it names the title."""
    for line in sorted(pm.lines, key=lambda l: l.top):
        if line.top <= rail_bottom or not line.plain.strip():
            continue
        for rule in pm.h_rules:
            if (0.0 < rule.top - line.top < _UNDER_DROP
                    and abs(rule.x0 - line.x0) <= _UNDER_TOL
                    and abs(rule.x1 - line.x1) <= _UNDER_TOL):
                return line
    return None


def _rows(pm, finder) -> list[list]:
    """The visual rows of page 1, grouped by printed row.

    Furniture core already tagged is neither claimed nor consumed: core has
    routed it, and a reader that took it would report it twice."""
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


def _dated(model) -> str | None:
    """'Dated:  April 29, 2026' — the first one the document prints."""
    for pm in model.pages:
        for line in sorted(pm.lines, key=lambda l: l.top):
            hit = _DATED.match(_norm(line.plain))
            if hit:
                return _norm(hit.group(1))
    return None


# --------------------------------------------------------------------------
# the caption box
# --------------------------------------------------------------------------

def _box(box: list, rail: dict, pm, ctx):
    """The caption as a CaptionBlock, paired by printed row.

    Sides split AT THE RAIL, glyph by glyph — whether pdfio broke a row at
    its column gap is an accident of how wide the gap happened to be, and a
    whole-line test would put a cell on the wrong side of the column."""
    mid = rail["x"]
    left, right, left_txt, right_txt = [], [], [], []
    seen_instrument = False
    for g in box:
        l_cells, r_cells = [], []
        for line in g:
            shed = _shed_rail(line, rail)
            if shed is None:
                continue                      # the line WAS the rail
            lo = _side(shed, mid, "L")
            hi = _side(shed, mid, "R")
            if lo is not None:
                l_cells.append(lo)
            if hi is not None:
                r_cells.append(hi)
        lt = _norm(" ".join(c.plain for c in sorted(l_cells,
                                                    key=lambda c: c.x0)))
        rt = _norm(" ".join(c.plain for c in sorted(r_cells,
                                                    key=lambda c: c.x0)))
        if _INSTRUMENT.match(lt):
            seen_instrument = True
        left.append(_cell(l_cells, pm,
                          "case-info" if seen_instrument else "caption"))
        right.append(_cell(r_cells, pm, "docket"))
        left_txt.append(lt)
        right_txt.append(rt)
        ctx.consumed.update(l.id for l in g)
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: once the
    # glyphs are gone the rows that held nothing else are empty on BOTH
    # sides, and left standing they render as phantom blank rows.
    while left and not left_txt[-1] and not right_txt[-1]:
        left.pop(), right.pop(), left_txt.pop(), right_txt.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted(l.id for g in box for l in g))
    return (m.CaptionBlock(
        left=left, right=right, rail=rail["glyph"], rail_rows=len(left),
        style_id="parenthetical-box",
        fp={"rail": rail["glyph"], "rail_band": (rail["top"], rail["bottom"]),
            "mid_x": mid},
        prov=m.Prov(pm.number, ids)), left_txt, right_txt)


def _read_left(ctx, left_txt: list[str]) -> None:
    """The opener, the party, the instrument — in the order printed.

    The party is everything BETWEEN the two labels, joined across its own
    wraps. Nothing about the party is read by wording."""
    rows = [t for t in left_txt if t]
    if rows:
        ctx.crit["caption"] = rows[:40]
    opener, start = "", 0
    for i, t in enumerate(rows):
        if _OPENER.match(t):
            opener, start = t.rstrip(" -–—").rstrip(), i + 1
            break
    end = len(rows)
    for i in range(start, len(rows)):
        if _INSTRUMENT.match(rows[i]):
            end = i
            break
    party = _norm(" ".join(rows[start:end])).rstrip(",;")
    if party:
        # ONE PARTY. There is no adversary in an 'Appeal of —' caption, and
        # a second element here would render as 'X v. Y' and assert one.
        ctx.crit["parties"] = [party]
        ctx.crit["case_name"] = f"{opener} {party}" if opener else party


def _read_right(ctx, right_txt: list[str]) -> None:
    """'ASBCA No. 64204' / 'ASBCA Nos. 63510, 64085' and the numbers that
    wrap beneath them."""
    numbers: list[str] = []
    for t in right_txt:
        if not t:
            continue
        hit = _DOCKET_ROW.match(t)
        body = hit.group(1) if hit else t
        for piece in body.replace(";", ",").split(","):
            tok = piece.strip().rstrip(".")
            if _DOCKET_TOKEN.match(tok):
                numbers.append(tok)
    if not numbers:
        return
    ctx.crit["docket_number"] = numbers[0]
    if numbers[1:]:
        ctx.crit["other_dockets"] = numbers[1:]


# --------------------------------------------------------------------------
# the rail's arithmetic (ca6 / afcca, unchanged)
# --------------------------------------------------------------------------

def _cell(cells: list, pm, role: str) -> m.HmLine:
    if not cells:
        return m.HmLine(text="", prov=m.Prov(pm.number, ()), role=role)
    parts = sorted(cells, key=lambda l: l.x0)
    text = ""
    for p in parts:
        piece = line_markup(p)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _rail_chars(line, rail) -> list:
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    return [c for c in line.chars
            if (c.get("text") or "") == rail["glyph"] and lo <= c["x0"] <= hi]


def _shed_rail(line, rail):
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. The glyph is identified by its COLUMN, never by its
    character."""
    ids = {id(c) for c in _rail_chars(line, rail)}
    if not ids:
        return line
    kept = [c for c in line.chars if id(c) not in ids]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, kept)


def _side(line, mid: float, want: str):
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, keep)


def _replace(line, chars: list):
    import dataclasses
    return dataclasses.replace(
        line, chars=chars,
        x0=min(c["x0"] for c in chars),
        x1=max(c.get("x1", c["x0"]) for c in chars))


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = False,
             rel: float = 0.0) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self, doc_type=None) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type}


# --------------------------------------------------------------------------
# WHERE THE BOARD'S SIGNATURE BEGINS
# --------------------------------------------------------------------------
#
#     … the Board makes a monetary award to appellant in the amount of
#     $10,000.  This amount is inclusive of Contract Disputes Act interest.
#
#     Dated:  April 29, 2026                 the DATE LINE closes the decision
#                            CHRISTOPHER M. MCNULTY      the signing column,
#                            Administrative Judge        at x 334 of a 612pt
#                            Armed Services Board        sheet
#                            of Contract Appeals
#     (Signatures continued)
#     I concur                I concur                   the other judges,
#     J. REID PROUTY          DAVID D. D'ALESSANDRIS     two columns
#     …
#     I certify that the foregoing is a true copy of the Opinion and Decision
#     of the Armed Services Board of Contract Appeals in ASBCA No. 64204 …
#     Dated:  April 29, 2026                 the Recorder signs in turn
#                            PAULLA K. GATES-LEWIS
#
# Every one of those rows rendered as a paragraph of the decision, so each
# appeal ended in a page of names and offices (the user, 2026-08-21: 'the
# signatures … clogging up the end … could be wrapped up in a signature
# section and put at the end').
#
# THE DATE LINE IS THE BOUNDARY, and it is found from the BOTTOM. These are
# contract appeals and they quote dated correspondence, so the FIRST 'Dated:'
# on the page is usually somewhere in the findings — measured over the
# corpus, 18 of the 32 records have body prose after it. The one that closes
# the decision is the LAST date line with nothing but signing after it.

_DATE_LINE = re.compile(
    r"^DATED\s*:?\s*(?:this\s+)?\S.*\d{4}\.?$", re.I)
_SIGNING = re.compile(
    r"^(?:I\s+concur|\(Signatures?\s+continued\)|Recorder\b)", re.I)
# THE RECORDER'S CERTIFICATE, which wraps over three rows at the body rail —
# the one piece of ordinary prose inside the signing run.
_CERTIFY = re.compile(r"^I\s+certify\s+that\s+the\s+foregoing", re.I)
# The offices the Board's members sign under — a closed vocabulary, and the
# only prose that stands between one signature and the next.
_OFFICE = re.compile(
    r"^(?:Administrative\s+Judge|Acting\s+(?:Vice\s+)?Chairman"
    r"|Vice\s+Chairman|Chairman|Armed\s+Services\s+Board"
    r"|of\s+Contract\s+Appeals|Recorder,?\s+Armed\s+Services\s+Board)",
    re.I)
# A NAME set in capitals, alone on its row: 'CHRISTOPHER M. MCNULTY'.
_SIGNER = re.compile(r"^[A-Z][A-Z.'’\- ]{3,40}$")
# A FOOTNOTE'S OPENING ROW: its label, then its text.
_NOTE_OPENER = re.compile(r"^\d{1,2}\s+\S")


@decider("signature.opens", court="asbca")
def signature_opens_asbca(model=None, geom=None, **_):
    """(page, top) of the date line that closes the decision, or NOTHING."""
    if not model or not model.pages:
        return NOTHING
    finder = FurnitureFinder(model,
                             geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 13.0)
    rows = []
    for pm in model.pages:
        for line in pm.lines:
            text = " ".join((line.plain or "").split())
            if not text or finder.kind(pm, line):
                continue      # the folio and the running foot are not the run
            rows.append((pm.number, line.top, text, line.x0, pm.width))
    rows.sort(key=lambda r: (r[0], r[1]))

    def closes(at: int) -> bool:
        """Is everything below rows[at] the signing and nothing else?"""
        certifying = False
        noting = None
        for _pg, _top, text, x0, width in rows[at + 1:]:
            # A NOTE PRINTED UNDER THE SIGNATURES IS STILL A NOTE. The Board
            # signs partway down the page and the page's own footnote runs
            # below the block — kiewitphelps and dsme_construction both do
            # it. The note is the writing's, lifted by the footnote pass,
            # and it says nothing about where the decision stopped.
            if noting == _pg:
                continue
            if _NOTE_OPENER.match(text) and _top > 0.75 * 792.0:
                noting = _pg
                continue
            if _CERTIFY.match(text):
                certifying = True       # its wrap belongs to it
                continue
            if _DATE_LINE.match(text):
                certifying = False
                continue
            if certifying:
                continue
            if (_SIGNING.match(text) or _OFFICE.match(text)
                    or _SIGNER.match(text) or x0 > width * 0.5):
                continue
            return False
        return True

    # THE HIGHEST date line with nothing but signing below it. Read from the
    # top, the first one that qualifies is the Board's; a 'Dated:' quoted in
    # the findings cannot qualify, because the decision goes on after it.
    # (The run holds two — the Board signs and the Recorder signs again
    # under the certificate — and the decision stops at the upper one.)
    for i, row in enumerate(rows):
        if _DATE_LINE.match(row[2]) and closes(i):
            return (row[0], row[1])
    return NOTHING
