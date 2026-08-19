"""Michigan Court of Appeals ('michctapp').

Everything unique to michctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT — 'ruled cover' (42 of 42). The Court of Appeals files ONE
paper, and page 1 is stationery until the byline. Its zones are fenced by
DRAWN RULES in two invariant measures, and the measure names the zone:

    If this opinion indicates that it is "FOR PUBLICATION," it is …    the
    revision until final publication in the Michigan Appeals Reports.  notice
    ══════════════════════════════════ (470.9pt at x0=70.6)         the FENCE
              STATE OF MICHIGAN            the court naming itself,
              COURT OF APPEALS             bold, 14pt, on the page axis
    ───────────────── (262.0pt at x0=72.0)                           a SHELF
    PEOPLE OF THE STATE OF MICHIGAN,   UNPUBLISHED     the caption, in TWO
         Plaintiff-Appellee,           July 22, 2026     COLUMNS — parties
    v                                  12:01 PM          left at the rail,
    BRETT LEE COOLEY,                  No. 372849        the clerk's data
         Defendant-Appellant.          Kalamazoo Circuit Court   flush right
    ───────────────── (262.7pt at x0=71.3)   LC No. 2023-001680-FH
    Before:  RICK, P.J., and MURRAY and BORRELLO, JJ.          the panel
    PER CURIAM.                                    …and the writing starts

THE DISPATCH is a single question about page 1: does it draw the FENCE (a
rule across the WHOLE measure, in the top fifth of the sheet) over at least
one SHELF (a rule at the body rail, a little over half the measure)? Both,
and this is the paper; either missing, and the record gets NOTHING. The
three measures never collide — the fence is 470.9pt, a shelf is
257.4-262.7pt, and the footnote separator this court draws at the SAME
rail is 144.0pt. Measure first, then the rail.

WHERE EACH ZONE ENDS. The notice ends at the FENCE — it is the same two
sentences on every sheet the court files, so it is recorded as
`Dropped(kind="notice")` rather than reprinted. The masthead ends at the
FIRST shelf. Each caption band ends at the NEXT shelf or at the foot of
its page, whichever comes first: a band may run over (in_re_implementing
carries 200 township appellants from page 1 to page 2 before its closing
shelf) and a consolidation prints one band per docket (craig_schubiner).
The reader ends at the first byline, always, and the panel row is the only
thing standing between the last shelf and it.

THE CAPTION IS A COLUMN QUESTION. Nothing in it is read by wording:
  * left of x=365 is the party stack, right of it is the clerk's data —
    the clerk's column starts at x0=395.8 on every record and the party
    stack never reaches past x1=333;
  * AT THE RAIL is a party (or the pivot, or the clerk's 'and'); indented
    72pt from the rail is that party's STATUS label;
  * the clerk's column is ORDERED — the publication flag and the release
    stamp stand above the docket, and everything below the docket belongs
    to the court that tried the case. 'No.' opens the docket and 'LC No.'
    the number the court below gave it; both are closed structural forms,
    never a name.

WHAT THE READER DOES NOT TOUCH. michctapp files each separate writing as
its own PDF (patricia_lesko_v._supreme_felons_inc_1 is the dissent to
patricia_lesko_v._supreme_felons_inc), so no record in the corpus reprints
its caption over an interior writing and the reader never reaches into one.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import find_date
from . import get_profile

STYLE_COVER = "ruled cover"

# ---- michctapp's declared facts (measured over the 42-record corpus) -----
# THE FENCE under the publication notice: a rule across the whole measure
# (470.9pt at x0=70.6 on all 42), in the top fifth of the sheet.
_FENCE_WIDTH = 400.0
_FENCE_BAND = 0.20
# A SHELF: the caption's own rule, at the body rail, a little over half the
# measure (257.4-262.7pt over the corpus). The footnote separator this court
# draws at the SAME rail is 144.0pt, so the measure separates them outright.
_SHELF = (230.0, 300.0)
_SHELF_RAIL = 40.0
# THE CAPTION'S COLUMN DIVIDE.
_COL_X = 365.0
# A STATUS LABEL is indented 72pt from the caption's own rail (144.0 under
# a 72.0 rail, 148.6 under a 76.6 rail).
_INDENT_MIN = 40.0
# Rows on the same BASELINE are one row of the block. craig_schubiner sets
# a left cell one point below its right-hand neighbour.
_ROW_TOL = 3.0
# HOW FAR THE COVER MAY RUN before the reader gives up on finding a byline.
_MAX_COVER_PAGES = 4

# 'No. 372849' / 'Nos. 370051; 371977' — the docket, in the clerk's column.
_DOCKET = re.compile(r"^Nos?\.\s*(.+)$")
# 'LC No. 2023-001680-FH' / 'LC Nos. 25-051320-NA;' — the number the court
# BELOW gave the case. Tested first: it is a 'No.' too.
_LOWER_DOCKET = re.compile(r"^LC\s+Nos?\.\s*(.*)$", re.I)
# …and its continuation row, a bare number standing under that label.
_BARE_NUMBER = re.compile(r"^[\dA-Za-z][\dA-Za-z-]*[;,.]?$")
# The pivot: 'v' alone at the rail. This court sets no period, and sets it
# capital on three records.
_PIVOT = re.compile(r"^v\.?$", re.I)
# 'and' — the conjunction the clerk stands between two groups of parties.
_AND = "and"
# 'Before:  RICK, P.J., and MURRAY and BORRELLO, JJ.' — the panel, stated
# as a structural form (the word Before over the roster), never a name.
_PANEL = re.compile(r"^Before\b\s*:?\s*(.+)$", re.I)
# The bench TITLES the roster sets after each name — a finite role
# vocabulary. Spacing is not reliable ('BOONSTRA, P .J.,' on one record),
# so the test closes up the token's periods and spaces first.
_TITLES = frozenset(("J", "JJ", "PJ", "CJ", "P", "CJJ"))
# Generational suffixes, so 'FELTON, JR.' is one judge and not two.
_SUFFIXES = frozenset(("JR", "SR", "II", "III", "IV"))
# The release stamp's clock row, set under the date — a stamp, not a date.
_TIME = re.compile(r"^\d{1,2}:\d{2}\s*[AP]\.?M\.?$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _flat(tok: str) -> str:
    return tok.replace(".", "").replace(" ", "").upper()


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _fence(pm):
    """The rule the court draws under its publication notice."""
    for r in sorted(pm.h_rules, key=lambda r: r.top):
        if r.width >= _FENCE_WIDTH and r.top < pm.height * _FENCE_BAND:
            return r
    return None


def _shelves(pm, rail: float) -> list:
    """The caption's own rules on one page, top first."""
    return sorted((r for r in pm.h_rules
                   if _SHELF[0] <= r.width <= _SHELF[1]
                   and r.x0 <= rail + _SHELF_RAIL),
                  key=lambda r: r.top)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The page models, the emit buffer, and what the walk has learned."""

    def __init__(self, model, geom, finder):
        self.model = model
        self.geom = geom
        self.finder = finder
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def lines(self, page_no: int) -> list:
        """Content rows of one page; furniture is left for core to drop."""
        pm = self.pages[page_no]
        return [l for l in sorted(pm.lines, key=lambda l: (l.top, l.x0))
                if l.plain.strip() and not self.finder.kind(pm, l)]

    def row(self, line, role: str, align: str = "L",
            rel: float = 0.0) -> m.HmLine:
        self.consumed.add(line.id)
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role)

    def emit(self, line, role: str, align: str = "L",
             rel: float = 0.0) -> None:
        self.items.append(self.row(line, role, align, rel))

    def rule(self, page_no: int) -> None:
        # A DRAWN rule has no line of its own. `pipeline` sorts the block
        # back into the page's order and gives an id-less item the position
        # of the row AFTER it — which is exactly where a shelf stands.
        self.items.append(m.Rule(prov=m.Prov(page_no), span="left"))

    def drop(self, lines: list, kind: str) -> None:
        if not lines:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(_norm(l.plain) for l in lines)[:1200],
            prov=m.Prov(lines[0].page, tuple(l.id for l in lines)),
            kind=kind))
        self.consumed.update(l.id for l in lines)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

class _Parties:
    """The parties, gathered as the caption prints them: a name wraps over
    as many rail rows as it needs and is closed by the STATUS label indented
    under it; the pivot turns the collection over to the other side; and
    once the second side has closed, the document is named. That last rule
    is what a consolidation needs — craig_schubiner restates the whole
    caption for its second docket, and without it the case name reads twice
    over."""

    def __init__(self):
        self.left: list = []
        self.right: list = []
        self._side = self.left
        self._pivot = False
        self._done = False

    def party(self, text: str) -> None:
        if not self._done:
            self._side.append(text)

    def status(self) -> None:
        if self._pivot and self.right:
            self._done = True

    def pivot(self) -> None:
        if not self._done:
            self._pivot = True
            self._side = self.right


def _record_docket(ctx: _Ctx, printed: str) -> None:
    hit = _DOCKET.match(printed)
    value = _norm(hit.group(1)) if hit else _norm(printed)
    for part in re.split(r"\s*[;,]\s*|\s+and\s+", value):
        part = part.strip(" .")
        if not part or not re.fullmatch(r"[\dA-Za-z][\dA-Za-z-]*", part):
            continue
        if ctx.crit.get("docket_number") is None:
            ctx.crit["docket_number"] = part
        elif part != ctx.crit["docket_number"] \
                and part not in ctx.crit.get("other_dockets", []):
            ctx.crit.setdefault("other_dockets", []).append(part)


def _record_lower_docket(ctx: _Ctx, printed: str) -> None:
    for part in re.split(r"\s*[;,]\s*", _norm(printed)):
        part = part.strip(" .")
        if part and re.fullmatch(r"[\dA-Za-z][\dA-Za-z-]*", part) \
                and part not in ctx.crit.get("lower_court_docket", []):
            ctx.crit.setdefault("lower_court_docket", []).append(part)


def _publication(flags: list) -> str | None:
    """'FOR PUBLICATION' / 'UNPUBLISHED', and an unpublished slip the court
    later APPROVED FOR PUBLICATION (cms_energy, dandre_bell — the second
    stamp is the operative one)."""
    joined = " ".join(flags).upper()
    if "APPROVED FOR PUBLICATION" in joined:
        return "published"
    if "UNPUBLISHED" in joined:
        return "unpublished"
    if "FOR PUBLICATION" in joined:
        return "published"
    return None


def _panel_names(roster: str) -> list:
    """'RICK, P.J., and MURRAY and BORRELLO, JJ.' -> three judges. The bench
    TITLES are a closed role vocabulary and the generational SUFFIXES are
    another; everything else on the row is a name."""
    out: list = []
    for piece in re.split(r",\s*|\s+and\s+", roster):
        name = piece.strip(" .")
        if not name:
            continue
        flat = _flat(name)
        if flat in _TITLES:
            continue
        if flat in _SUFFIXES and out:
            out[-1] += ", " + name
            continue
        out.append(name)
    return out


class _Clerk:
    """The clerk's column, read by ORDER rather than by wording: the
    publication flag and the release stamp stand above the docket, and
    everything below the docket belongs to the court that tried the case."""

    def __init__(self):
        self.seen_docket = False
        self.seen_lower_docket = False
        self.flags: list = []
        # The run a PAD cell continues. The clerk's column runs on across a
        # band boundary (craig_schubiner's second docket opens under the
        # first band's LC number), so the role that fills an empty cell is
        # the document's last, not the band's first.
        self.last = "publication"

    def role(self, ctx: _Ctx, text: str) -> str:
        self.last = self._role(ctx, text)
        return self.last

    def _role(self, ctx: _Ctx, text: str) -> str:
        if _LOWER_DOCKET.match(text):
            _record_lower_docket(ctx, _LOWER_DOCKET.match(text).group(1))
            self.seen_lower_docket = True
            return "lower-court"
        if self.seen_lower_docket and _BARE_NUMBER.match(text):
            _record_lower_docket(ctx, text)   # a wrapped second LC number
            return "lower-court"
        if _DOCKET.match(text):
            _record_docket(ctx, text)
            self.seen_docket = True
            return "docket"
        if self.seen_docket:
            prev = ctx.crit.get("lower_court")
            if not prev:
                ctx.crit["lower_court"] = text
            elif text not in prev:
                ctx.crit["lower_court"] = f"{prev}, {text}"
            return "lower-court"
        if _TIME.match(text):
            return "date"
        value = find_date(text)
        if value:
            if ctx.crit.get("decision_date") is None:
                ctx.crit["decision_date"] = value
            return "date"
        if text.upper() == text and any(c.isalpha() for c in text):
            self.flags.append(text)
            return "publication"
        return "case-info"


# --------------------------------------------------------------------------
# one caption band -> one CaptionBlock
# --------------------------------------------------------------------------

def _pad(page_no: int, role: str) -> m.HmLine:
    """An EMPTY cell is still a row of the block — the two columns are
    paired by BASELINE, and a row printed on one side only still occupies
    a row. It carries the run's role so the margin label does not restart."""
    return m.HmLine(text="", prov=m.Prov(page_no), role=role)


def _band(ctx: _Ctx, rows: list, rail: float, clerk: _Clerk,
          parties: _Parties, caption: list, title: bool = False) -> None:
    """One band of the caption as a CaptionBlock. Column membership is
    decided by which side of x=365 a row sits on; nothing is inferred from
    what a row says.

    `title` marks a MATTER-TITLE band — the 'In re …' the clerk sets in a
    band of its own ABOVE a party caption (in_re_nielsen_estate,
    in_re_llh, in_re_implementing). It is caption apparatus, not a party,
    and fed to `_Parties` it prepends the matter to the plaintiff's side."""
    groups: list = []
    for line in rows:
        if groups and abs(line.top - groups[-1][0]) <= _ROW_TOL:
            groups[-1][1].append(line)
        else:
            groups.append((line.top, [line]))
    page_no = rows[0].page
    left_cells: list = []
    right_cells: list = []
    r_role = clerk.last
    l_role = "case-info" if title else "caption"
    for _top, group in groups:
        for line in sorted(group, key=lambda l: l.x0):
            text = _norm(line.plain)
            if line.x0 >= _COL_X:
                r_role = clerk.role(ctx, text)
                right_cells.append(ctx.row(line, r_role, "R"))
                continue
            caption.append(text)
            if title:
                left_cells.append(ctx.row(line, l_role, "L"))
                continue
            if line.x0 > rail + _INDENT_MIN:
                left_cells.append(ctx.row(line, "caption", "L",
                                          rel=line.x0 - rail))
                parties.status()
                continue
            left_cells.append(ctx.row(line, "caption", "L"))
            if _PIVOT.match(text):
                parties.pivot()
            elif text.lower().strip(" ,") != _AND:
                parties.party(text)
        while len(left_cells) < len(right_cells):
            left_cells.append(_pad(page_no, l_role))
        while len(right_cells) < len(left_cells):
            right_cells.append(_pad(page_no, r_role))
    ctx.items.append(m.CaptionBlock(
        left=left_cells, right=right_cells, rail=None,
        rail_rows=len(left_cells), style_id=STYLE_COVER,
        fp={"rail": "open", "mid_x": _COL_X},
        prov=m.Prov(page_no, tuple(l.id for l in rows))))


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

def _walk(ctx: _Ctx, fence):
    """Pass one: name every row on the cover without placing any of it. The
    caption's RAIL is measured INSIDE the caption, so the bands have to be
    collected before a single cell can be built."""
    parser = BylineParser(get_profile("michctapp").byline)
    plan: list = []            # ('rule'|'court'|'band'|'panel', payload)
    band: list = []
    opened = False
    signed = False
    last = min(len(ctx.model.pages), _MAX_COVER_PAGES)
    for page_no in range(1, last + 1):
        pm = ctx.pages[page_no]
        rail = ctx.geom.body_x0 if ctx.geom else 72.0
        shelves = [r for r in _shelves(pm, rail)
                   if page_no > 1 or r.top > fence.top]
        for line in ctx.lines(page_no):
            if page_no == 1 and line.top < fence.top:
                continue
            text = _norm(line.plain)
            # THE SHELF the page drew above this row closes the band.
            while shelves and shelves[0].top < line.top:
                shelves.pop(0)
                if band:
                    plan.append(("band", band))
                    band = []
                plan.append(("rule", page_no))
                opened = True
            if not opened:
                # THE COURT NAMES ITSELF between the fence and the first
                # shelf, bold on the page axis. Nothing else stands there,
                # and a record that puts something else there is not this
                # contract.
                if not (line.all_bold and abs((line.x0 + line.x1) / 2
                                              - pm.width / 2) <= 14.0):
                    return None, False
                plan.append(("court", line))
                continue
            hit = _PANEL.match(text)
            # …and the roster it opens must NAME A BENCH: the row carries at
            # least one of the court's own title abbreviations. Without that
            # test a party whose name begins 'Before' would read as a panel,
            # and a mis-tagged row is worse than an untagged one.
            if hit and any(_flat(t) in _TITLES
                           for t in re.split(r"[,\s]+", hit.group(1))):
                if band:
                    plan.append(("band", band))
                    band = []
                plan.append(("panel", line))
                continue
            if parser.parse(text) is not None:
                signed = True
                break
            band.append(line)
        else:
            # A BAND ENDS AT THE FOOT OF ITS PAGE too, so a caption that
            # runs over renders as one block per sheet and the page break
            # stays visible.
            if band:
                plan.append(("band", band))
                band = []
            continue
        break
    if band:
        plan.append(("band", band))
    return plan, signed


def _read(ctx: _Ctx, fence):
    # THE NOTICE: the two sentences the court prints above the fence on
    # every sheet it files. Recorded, never reprinted.
    ctx.drop([l for l in ctx.lines(1) if l.top < fence.top], "notice")

    plan, signed = _walk(ctx, fence)
    if plan is None:
        return NOTHING
    bands = [rows for kind, rows in plan if kind == "band"]
    # THE RAIL, measured inside the caption and nowhere else.
    rail = min((l.x0 for rows in bands for l in rows if l.x0 < _COL_X),
               default=None)
    if rail is None:
        return NOTHING

    # A BAND BEFORE THE PIVOT IS THE MATTER'S TITLE. Where the caption
    # states a pivot at all, the bands standing above the one that states
    # it are what the clerk called the matter ('In re ESTATE OF NEAL D.
    # NIELSEN.'), not a party to it.
    pivot_at = next((i for i, rows in enumerate(bands)
                     if any(_PIVOT.match(_norm(l.plain)) and l.x0 < _COL_X
                            and l.x0 <= rail + _INDENT_MIN for l in rows)),
                    None)
    titles = set(range(pivot_at)) if pivot_at is not None else set()

    masthead: list = []
    caption: list = []
    matter: list = []
    parties = _Parties()
    clerk = _Clerk()
    seen = 0
    for kind, payload in plan:
        if kind == "rule":
            ctx.rule(payload)
        elif kind == "court":
            masthead.append(_norm(payload.plain))
            ctx.emit(payload, "court", "C")
        elif kind == "panel":
            roster = _norm(_PANEL.match(_norm(payload.plain)).group(1))
            ctx.crit["panel_line"] = _norm(payload.plain)
            ctx.crit["judges"] = roster
            ctx.crit["panel"] = _panel_names(roster)
            ctx.emit(payload, "panel")
        else:
            before = len(caption)
            _band(ctx, payload, rail, clerk, parties, caption,
                  title=seen in titles)
            if seen in titles:
                matter.extend(caption[before:])
            seen += 1
    if not (signed and masthead and caption):
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_COVER
    ctx.crit["court"] = " ".join(masthead)
    ctx.crit["caption"] = caption
    status = _publication(clerk.flags)
    if status:
        ctx.crit["publication_status"] = status
    a = _norm(" ".join(parties.left)).rstrip(",; ")
    b = _norm(" ".join(parties.right)).rstrip(",; ")
    if a and b:
        ctx.crit["parties"] = [a, b]
        ctx.crit["case_name"] = f"{a} v {b}"
    elif a:
        ctx.crit["parties"] = [a]
        ctx.crit["case_name"] = a
    # …and where the clerk TITLED the matter, that title is what the court
    # calls the case, whatever the parties beneath it are called.
    if matter:
        ctx.crit["case_name"] = _norm(" ".join(matter)).rstrip(" .")
        if not ctx.crit.get("parties"):
            ctx.crit["parties"] = [ctx.crit["case_name"]]
    return ctx.result()


# --------------------------------------------------------------------------
# the decider
# --------------------------------------------------------------------------

@decider("headmatter.read", court="michctapp")
def read_headmatter_michctapp(model, geom, **_):
    """Read michctapp's ruled cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm1 = model.pages[0]
    fence = _fence(pm1)
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    if fence is None or not _shelves(pm1, body_x0):
        return NOTHING
    ctx = _Ctx(model, geom, FurnitureFinder(model, body_x0, body_size))
    return _read(ctx, fence)
