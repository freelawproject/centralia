"""Texas Court of Criminal Appeals ('texcrimapp').

Everything unique to texcrimapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT — 'double-rule cassette' (40 of 42 records).

Texas's criminal court prints the SAME cassette its civil sibling does — a
masthead, then a fenced DOCKET band, then the caption, then a fenced ORIGIN
band, then the byline — and it fences the two bands with rules centred on
the page axis in TWO invariant measures, the MEASURE naming the band:

    SHORT  110-160pt around THIS court's docket
    LONG   350-500pt around where the case came from

    IN THE COURT OF CRIMINAL APPEALS            the masthead
    OF TEXAS
    ───────────────                             the SHORT fence, on the axis
    NO. PD-0510-25                              …around the docket…
    ───────────────                             …and one under it
    THE STATE OF TEXAS                          the caption: a party…
    v.                                          …the pivot…
    GRADY JACK BARBER, Appellee                 …the other side, with status
    ───────────────────────────────────────     the LONG fence…
    ON APPELLEE'S PETITION FOR DISCRETIONARY    …around the origin…
    REVIEW / FROM THE NINTH COURT OF APPEALS    …which wraps…
    LIBERTY COUNTY
    ───────────────────────────────────────     …and one under it
    Schenck, P.J., filed a dissenting opinion   …and the writing begins

WHAT THE FENCE IS MADE OF, AND WHY IT DOES NOT MATTER. 37 records DRAW the
four rules (pdfio reports them as `rect` on the Word-generated slips and as
`curve` on the WordPerfect ones); 3 records — the court's new 2026 template,
identical to the Supreme Court of Texas's — TYPE them out of a single
repeated U+2550. Both are the same fence: on the page axis, in one of the
court's two measures. The reader tests THAT and re-emits either as a rule,
so nothing of the layout depends on which tool set the page.

    drawn  short 139.6-144.7  long 359.9-482.3      (37 records)
    typed  short 119.1        long 386.8            ( 3 records)

THE DISPATCH is the fence, never the wording, and never the masthead: 39 of
the 42 records set the masthead at 18pt over a 14pt body, but lambert sets
it at body size, so a size test would misroute it. Page 1 must carry a SHORT
pair and a LONG pair, in that order, on the axis. A record that fences
neither is not this paper and gets NOTHING.

THE SAME MEASURE OFF THE AXIS MEANS SOMETHING ELSE. jordan draws its
footnote separator at 143.9pt — the SHORT measure to a tenth of a point —
at x0=72, 162pt off the axis. The axis test takes it out. And A RULE WHOSE
ENDS COINCIDE WITH THE ROW ABOVE IT IS AN UNDERLINE, NOT A FENCE: every
record underscores its 'O P I N I O N' banner, and on barber (156.1pt) and
montgomery_2 (158.8pt) that underline lands inside the SHORT window. It is
rejected because it starts and ends where the banner does.

WHERE THE READER STOPS. At the second LONG fence. Everything below it is
the writing's — including the byline, which on this court is an ANNOUNCEMENT
that runs on for three or four rows naming who joined and what else was
filed ('PARKER, J., delivered the opinion of the Court in which /
RICHARDSON, NEWELL, WALKER, and MCCLURE, JJ., joined. MCCLURE, J., / filed a
concurring opinion…'). The reader takes none of it. Core had been pulling
the first row or two of that announcement INTO the headmatter on five
records (barber, barber_1, montgomery, montgomery_3, wenzel), which left
those writings unsigned; stopping at the fence returns them.

THE TWO RECORDS THIS READER DOES NOT CLAIM. dora and montgomery_1 print the
identical row sequence with NO fences at all — the bands are separated by
white space only. That is a different contract and this reader returns
NOTHING for it rather than guess which band a row belongs to.

texcrimapp prints NO appearance of counsel anywhere in the corpus, and the
whole headmatter is on page 1 of every record: over 42 documents and 400+
pages there is not one on-axis rule in either measure on any page but the
first.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES, get_profile, register

# texcrimapp's profile: an abbreviated-title byline over a surname
# ('PARKER, J., delivered the opinion of the Court…' / 'Schenck, P.J., filed
#  a dissenting opinion…' / 'Per curiam.').
#
# THE SURNAME IS SET EITHER WAY. This court's slips come off two templates
# and one of them sets the byline surname in TITLE CASE — 'Schenck, P.J.,'
# / 'Finley, J.,' beside the other's 'PARKER, J.,'. Without
# `allow_titlecase_name` five records (barber, barber_1, montgomery,
# montgomery_3, wenzel) assembled with no author at all; the old engine
# knew this and said so in its own docstring ("The surname may be all-caps
# ('PARKER') or title-case ('Schenck')"). No false positive appears
# anywhere in the corpus — the court's body prose never opens '<Word>, J.,'.
#
# NOTE FOR WHOEVER WIRES THIS FILE IN: `courts/__init__.py` still registers
# a texcrimapp profile of its own, WITHOUT that flag. This file replaces it
# in place rather than raising a duplicate, so the import is safe either
# way — but the block in `__init__.py` should be deleted when the import is
# added, so there is one declaration site.
_TEXCRIMAPP_PROFILE = CourtProfile(
    "texcrimapp", "Texas Court of Criminal Appeals",
    byline=BylineGrammar(style="abbrev", accept_delivered=True,
                         allow_titlecase_name=True),
)
if "texcrimapp" in PROFILES:
    PROFILES["texcrimapp"] = _TEXCRIMAPP_PROFILE
else:
    register(_TEXCRIMAPP_PROFILE)
TEXCRIMAPP = get_profile("texcrimapp")

STYLE = "double-rule cassette"
# The same cassette with the ink left off — see `_bands_by_leading`.
STYLE_BARE = "whitespace cassette"

# ---- texcrimapp's declared facts (measured over the 42-record corpus) ----
# THE FENCE MEASURES. 160 fences over the corpus: 80 short and 80 long.
_SHORT_FENCE = (110.0, 160.0)
_LONG_FENCE = (350.0, 500.0)
# wenzel sets its short pair 7.5pt left of the axis; every other fence in
# the corpus is centred to a tenth of a point.
_AXIS_TOL = 10.0
# A TYPED FENCE IS A ROW OF ONE GLYPH REPEATED. Twelve on the short rule,
# thirty-nine on the long.
_FENCE_MIN_GLYPHS = 6
# AN UNDERLINE STARTS AND ENDS WHERE THE ROW ABOVE IT DOES, and stands
# within one line of it.
_UNDERLINE_TOL = 4.0
_UNDERLINE_GAP = 30.0
# THE WHOLE HEADMATTER IS ON PAGE 1 — see the module docstring.
_MAX_PAGES = 1
# THE ORIGIN BAND IS SET TIGHT. Every record in the corpus sets the
# caption at the body's own 34pt lead and the origin band at HALF of it
# (16.8-19.5pt). 0.7 sits between the two with room on both sides.
_TIGHT_LEAD = 0.7

# 'NO. PD-0510-25' / 'NOS. PD-0581-22 & PD-0582-22'. The docket's own
# comma is INSIDE the number ('WR-97,593-01'), so a docket row is split on
# the conjunction only — never on the comma.
_DOCKET_ROW = re.compile(r"^Nos?\.\s*(.+)$", re.I)
_DOCKET_SPLIT = re.compile(r"\s*(?:&|;|\band\b)\s*", re.I)
_DOCKET = re.compile(r"^[A-Z]{2,3}[-‑][\d,]+(?:[-‑]\d+)?$")
# THE FOOT — 'Delivered: May 21, 2026' over 'Do not publish'. Two closed
# role vocabularies: a FILING VERB with a dated value, and a PUBLICATION
# DIRECTIVE. They corroborate a block the geometry has already found; see
# `_read_foot` for the measurement that finds it.
_FOOT_DATE = re.compile(r"^(?:Delivered|Filed|Issued|Entered)\s*:\s*(.+?)\.?$",
                        re.I)
_FOOT_PUBLISH = {"publish": "published", "do publish": "published",
                 "do not publish": "unpublished",
                 "not for publication": "unpublished"}
# THE DIRECTIVE ROW IS A STUB. Over the corpus it measures 0.089-0.189 of
# the measure; 0.30 leaves half again the room. The DATE row above it is
# NOT constrained — the newer template sets it as a tab-out label/value pair
# ('FILED:' at the rail, the date at x=288) and it reaches 0.838 there
# against 0.22-0.47 on the older one, so any bound tight enough to mean
# something would cut the newer template out.
_FOOT_MAX_MEASURE = 0.30
_FOOT_RAIL = 1.5
_FOOT_SIZE_TOL = 0.6

# THE CAUSE the court below gave the case, where the origin band names it.
_CAUSE = re.compile(r"\bCAUSE\s+NOS?\.\s*(\S+(?:\s*\(\d+\))?)", re.I)
# PARTY STATUS is a closed role vocabulary — never a party name. It follows
# the name after a comma on the party's own row.
_STATUS = ("appellant", "appellants", "appellee", "appellees",
           "applicant", "applicants", "relator", "relators",
           "respondent", "respondents", "petitioner", "petitioners",
           "real party in interest", "real parties in interest")
# THE PIVOT is a row of its own; this court sets it 'v.' and 'V.'.
_PIVOT = re.compile(r"^v\.?$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def glyphs(self) -> list:
        """The row's inked glyphs, as the text layer hands them back."""
        return [c.get("text") or "" for p in self.pieces for c in p.chars
                if (c.get("text") or "").strip()]

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _page_rows(pm, finder) -> list:
    """One page's content rows, furniture removed, in the page's own order.

    A READER THAT CLAIMS A REGION INHERITS ITS FURNITURE — and must not lose
    its own landmarks to it, which is why a row that measures as one of this
    court's typed fences is kept whatever else it also looks like.
    """
    buckets: dict = {}
    loose: list = []
    for line in pm.lines:
        if not line.plain.strip():
            continue
        if finder.kind(pm, line) and not _typed_fence(_Row([line]), pm.width):
            continue
        if line.row is not None:
            buckets.setdefault(line.row, []).append(line)
        else:
            loose.append(line)
    groups = list(buckets.values())
    for line in sorted(loose, key=lambda l: (l.top, l.x0)):
        for g in groups:
            if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                g.append(line)
                break
        else:
            groups.append([line])
    return sorted((_Row(g) for g in groups), key=lambda r: (r.top, r.x0))


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows over the first `max_pages` pages, in the page's order."""
    rows: list = []
    for pm in model.pages[:max_pages]:
        rows.extend(_page_rows(pm, finder))
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _on_axis(x0: float, x1: float, page_width: float) -> bool:
    return abs((x0 + x1) / 2 - page_width / 2) <= _AXIS_TOL


def _measure(width: float) -> str | None:
    """'short' | 'long' | None — a fence named by its MEASURE."""
    if _SHORT_FENCE[0] <= width <= _SHORT_FENCE[1]:
        return "short"
    if _LONG_FENCE[0] <= width <= _LONG_FENCE[1]:
        return "long"
    return None


def _typed_fence(row: _Row, page_width: float) -> str | None:
    """The fence the court TYPES: one glyph repeated, on the axis, in one of
    the two measures. Read as glyphs, so a row whose font map was lost reads
    the same as one whose was not."""
    glyphs = row.glyphs
    if len(glyphs) < _FENCE_MIN_GLYPHS or len(set(glyphs)) != 1:
        return None
    if glyphs[0].isalnum():
        return None                       # a repeated LETTER is not a rule
    if not _on_axis(row.x0, row.x1, page_width):
        return None
    return _measure(row.x1 - row.x0)


def _is_underline(rule, rows: list) -> bool:
    """A rule that starts and ends where the row above it does is an
    UNDERLINE the court set as emphasis, not a fence it set as structure."""
    above = [r for r in rows
             if r.top < rule.top and rule.top - r.top <= _UNDERLINE_GAP]
    if not above:
        return False
    near = max(above, key=lambda r: r.top)
    return (abs(near.x0 - rule.x0) <= _UNDERLINE_TOL
            and abs(near.x1 - rule.x1) <= _UNDERLINE_TOL)


def _fences(pm, rows: list) -> list:
    """(top, measure, typed_row_or_None) for every fence page 1 sets, in
    order.

    A DRAWN rule carries no line ids and is re-emitted as a rule of its own;
    a TYPED one IS a row, so it carries its own ids and the reader consumes
    them — the glyphs never reach the page as text.
    """
    found: list = []
    for rule in pm.h_rules:
        if not _on_axis(rule.x0, rule.x1, pm.width):
            continue                      # the axis first…
        kind = _measure(rule.width)       # …the measure second
        if kind and not _is_underline(rule, rows):
            found.append((rule.top, kind, None))
    for row in rows:
        kind = _typed_fence(row, pm.width)
        if kind:
            found.append((row.top, kind, row))
    found.sort(key=lambda f: f[0])
    return found


def _dockets(text: str) -> list:
    """The dockets a fenced row names, in order, or [] when it names none."""
    mm = _DOCKET_ROW.match(_norm(text))
    if not mm:
        return []
    parts = [p.strip() for p in _DOCKET_SPLIT.split(mm.group(1)) if p.strip()]
    return parts if parts and all(_DOCKET.match(p) for p in parts) else []


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

def _strip_status(text: str) -> str:
    """'GRADY JACK BARBER, Appellee' -> 'GRADY JACK BARBER'. The status is a
    closed role vocabulary; the name is never read by wording."""
    flat = _norm(text).rstrip(",; ")
    head, sep, tail = flat.rpartition(",")
    if sep and tail.strip().lower().rstrip(".") in _STATUS:
        return head.strip().rstrip(",; ")
    return flat


def _case_name(rows: list) -> tuple:
    """(parties, case_name) from the caption rows, built from the party names
    either side of the pivot — never by joining the caption wholesale."""
    left: list = []
    right: list = []
    side = left
    pivoted = False
    for row in rows:
        flat = _norm(row.text)
        if side is left and _PIVOT.match(flat):
            side = right
            pivoted = True
            continue
        side.append(flat)
    lhs = _strip_status(" ".join(left))
    rhs = _strip_status(" ".join(right))
    if pivoted and lhs and rhs:
        return [lhs, rhs], f"{lhs} v. {rhs}"
    return ([lhs], lhs) if lhs else ([], None)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model):
        self.model = model
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.endmatter: list = []

    def emit(self, row: _Row, role: str) -> None:
        pm = self.pages[row.page]
        align = "C" if _on_axis(row.x0, row.x1, pm.width) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def rule(self, page: int, row: _Row | None) -> None:
        self.items.append(m.Rule(
            prov=m.Prov(page, row.ids if row else ()),
            typed=row is not None, span="center"))
        if row is not None:
            self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.endmatter,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _bands_by_fence(fences: list, rows: list) -> dict:
    """band -> rows, split by the four fences. The fence IS the parser."""
    tops = [t for t, _k, _r in fences]
    fence_rows = {id(r) for _t, _k, r in fences if r is not None}
    bands: dict = {"court": [], "docket": [], "caption": [], "lower-court": []}
    for row in rows:
        if id(row) in fence_rows or row.top > tops[3]:
            continue
        if row.top < tops[0]:
            bands["court"].append(row)
        elif row.top < tops[1]:
            bands["docket"].append(row)
        elif row.top < tops[2]:
            bands["caption"].append(row)
        else:
            bands["lower-court"].append(row)
    return bands


def _bands_by_leading(rows: list, lead: float, parser) -> dict | None:
    """The same cassette with the ink left off — dora and montgomery_1.

    Two records print the identical row sequence and draw nothing at all, so
    the bands are separated by white space only. Three landmarks stand in for
    the fences, and none of them reads a court or a party by wording:

      * the DOCKET row names itself in the court's own docket vocabulary,
        and there is exactly one of it;
      * the BYLINE closes the block, as it does on every other record;
      * between them, the ORIGIN BAND IS THE TIGHT-SET RUN AT THE FOOT. The
        caption is set at the body's 34pt lead, the origin at half of it.

    That last rule is not a guess: replayed over the 40 records that DO fence
    their bands, it reproduces the fence's own verdict — the same caption and
    the same origin — on 40 of 40. Where it cannot see a tight run of at
    least two rows under a caption of at least one, it declines.
    """
    dockets = [r for r in rows if _dockets(r.text)]
    if len(dockets) != 1:
        return None
    di = rows.index(dockets[0])
    if di < 1:
        return None                       # the masthead opens the paper
    bi = next((i for i in range(di + 1, len(rows))
               if parser.parse(rows[i].text)), None)
    if bi is None:
        return None                       # nothing closes the block
    mid = rows[di + 1:bi]
    if len(mid) < 2:
        return None
    j = len(mid) - 1
    while j > 0 and (mid[j].top - mid[j - 1].top) < _TIGHT_LEAD * lead:
        j -= 1
    if j < 1 or len(mid) - j < 2:
        return None                       # no caption, or no tight run
    return {"court": rows[:di], "docket": [rows[di]],
            "caption": mid[:j], "lower-court": mid[j:]}


def _read_foot(ctx: _Ctx, model, geom) -> list:
    """The delivery-and-publication foot, as ENDMATTER — or [].

    Every record closes on the same two rows, and they are the court's
    record of what it did with the paper, not a sentence of the opinion:

        Delivered: May 21, 2026
        Do not publish

    THE MEASUREMENT FINDS THEM, the wording only corroborates. They are two
    ADJACENT rows, both at the BODY RAIL (a body paragraph opens 36pt in from
    it, so neither is a paragraph opening), both at BODY SIZE (which keeps
    the footnote zone out — this court sets its notes a full step smaller),
    the lower one a stub well short of the measure, and nothing at body size
    follows them on the page. A paragraph's ragged tail is short once; it is never short
    twice running at the rail.

    The STAND-OFF is not the landmark, and it was worth checking: over the
    42 records the clear space above the block measures 33.7, 50.1, 50.8,
    67.4, 67.7, 69.2, 101.1 and 117.1pt against a 34pt lead. Seven records
    set it at the ordinary lead, so a stand-off test would miss all seven.

    They are returned in the reader's `attorneys` channel, which the pipeline
    feeds to the ENDMATTER section — one HmLine per printed row, so the line
    break the page set survives. Welded into the last paragraph they read
    as 'consistent with this opinion. Delivered: May 21, 2026 Do not
    publish'. And BECAUSE THE CLAIM TAKES THE ROW, the reader states the
    publication status the row carries; core reads that status off pages 1-2
    only, and on a two-page per curiam this row IS page 2.
    """
    body_size = geom.body_size if geom else 14.0
    body_x0 = geom.body_x0 if geom else 72.0
    measure = ((geom.right_x1 - body_x0) if geom and geom.right_x1
               else 468.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    best: list = []
    for pm in model.pages:
        rows = [r for r in _page_rows(pm, finder)
                if abs(r.size - body_size) <= _FOOT_SIZE_TOL]
        for i in range(len(rows) - 1):
            top, bot = rows[i], rows[i + 1]
            if i + 2 != len(rows):
                continue                  # nothing at body size follows
            if any(abs(r.x0 - body_x0) > _FOOT_RAIL for r in (top, bot)):
                continue
            if bot.x1 - bot.x0 > _FOOT_MAX_MEASURE * measure:
                continue
            dated = _FOOT_DATE.match(top.text)
            status = _FOOT_PUBLISH.get(
                _norm(bot.text).rstrip(".").lower())
            if not dated or not status:
                continue
            if not any(ch.isdigit() for ch in dated.group(1)):
                continue                  # a date carries a number
            best = [(top, "date", dated.group(1).strip()),
                    (bot, "publication", status)]
    if not best:
        return []
    out: list = []
    for row, role, value in best:
        out.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align("L"), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        ctx.consumed.update(row.ids)
        if role == "date":
            ctx.crit["decision_date"] = value
        else:
            ctx.crit["publication_status"] = value
    return out


@decider("headmatter.read", court="texcrimapp")
def read_headmatter_texcrimapp(model, geom, **_):
    """Read texcrimapp's cassette, fenced or bare, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    lead = (geom.lead if geom and geom.lead else 0.0) or 4.0 * body_size / 1.6
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING

    fences = _fences(page1, rows)
    kinds = [k for _t, k, _r in fences]
    # THE CASSETTE: a SHORT pair around the docket, then a LONG pair around
    # the origin. A record that fences PART of it is not a paper this reader
    # knows, and it gets NOTHING rather than a half-reading.
    if kinds == ["short", "short", "long", "long"]:
        style = STYLE
        bands = _bands_by_fence(fences, rows)
    elif not kinds:
        style = STYLE_BARE
        bands = _bands_by_leading(rows, lead, BylineParser(TEXCRIMAPP.byline))
    else:
        return NOTHING
    if bands is None:
        return NOTHING
    # EACH BAND MUST HOLD WHAT THE CASSETTE SAYS IT HOLDS. A band left empty
    # means the reader has mis-read the paper.
    if not all(bands[b] for b in ("court", "docket", "caption",
                                  "lower-court")):
        return NOTHING
    dockets: list = []
    for row in bands["docket"]:
        found = _dockets(row.text)
        if not found:
            return NOTHING                # the short pair holds a docket
        dockets.extend(found)

    # A CLAIM MUST BE TOTAL: every row above the block's last row is placed.
    ctx = _Ctx(model)
    placed = {id(r): b for b, rs in bands.items() for r in rs}
    last = max(r.top for rs in bands.values() for r in rs)
    fence_rows = {id(r) for _t, _k, r in fences if r is not None}
    # A TYPED fence is re-emitted as the RULE it is, so its glyphs never
    # reach the page as text; a DRAWN one is re-emitted because the shared
    # walk that would otherwise draw it no longer sees these rows at all.
    events = [(t, 0, ("fence", r)) for t, _k, r in fences]
    events += [(r.top, 1, ("row", r)) for r in rows
               if r.top <= last and id(r) not in fence_rows]
    for _t, _o, (what, row) in sorted(events, key=lambda e: (e[0], e[1])):
        if what == "fence":
            ctx.rule(page1.number, row)
            continue
        band = placed.get(id(row))
        if band is None:
            return NOTHING                # an unplaced row inside the block
        ctx.emit(row, band)

    ctx.crit["headmatter_style"] = style
    ctx.crit["court"] = _norm(" ".join(r.text for r in bands["court"]))
    ctx.crit["docket_number"] = f"No. {dockets[0]}"
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = [f"No. {d}" for d in dockets[1:]]
    ctx.crit["caption"] = [r.text for r in bands["caption"]]
    parties, name = _case_name(bands["caption"])
    if parties:
        ctx.crit["parties"] = parties
    if name:
        ctx.crit["case_name"] = name
    origin = _norm(" ".join(r.text for r in bands["lower-court"]))
    if origin:
        ctx.crit["lower_court"] = origin
    cause = _CAUSE.search(origin)
    if cause:
        ctx.crit["lower_court_docket"] = [_norm(cause.group(1)).rstrip(".,")]
    ctx.endmatter = _read_foot(ctx, model, geom)
    return ctx.result()
