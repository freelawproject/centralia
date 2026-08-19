"""Supreme Court of the State of Hawaiʻi ('haw').

THE CONTRACT. Hawaiʻi prints ONE cover, in two papers that share every
landmark and differ only in what stands below the caption. Nothing on it
changes size — the whole document, masthead to signature, is 12pt Courier —
so the page is read by its RULES and by the order of its landmarks, never by
type.

    'ruled cover' (48 of 50) — the caption stands between a FENCE PAIR
    spanning the body measure and centred on the page axis. The court draws
    that fence as a RECT on 31 records (466–472pt) and TYPES it as a run of
    underscores on 17 (425–461pt); the two are the same fence, and the
    fingerprint in resolve/captions.py sees only the typed half, which is why
    33 of 50 haw records classify as nothing at all.

    THE ORDER (30 records):                 THE PUBLISHED OPINION (12):

    ┌ Electronically Filed …┐  the red      *** FOR PUBLICATION IN WEST'S …
    │ Supreme Court         │  e-filing     ┌ Electronically Filed … ┐
    │ SCWC-24-0000674  …    ┘  stamp        └ … Dkt. 22 OP           ┘
    SCWC-24-0000674   the docket…           IN THE SUPREME COURT OF …
    IN THE SUPREME COURT OF …  …masthead    ---o0o---     the court's device
    ══════════════════  a FENCE             ══════════════════
    STATE OF HAWAIʻI,          the          JK,
      Respondent/Plaintiff-Appellee,        Appellant,
    vs.                        caption      vs.
    RUSTY MAKUE,                            HK; NS; and CHILD SUPPORT …
      Petitioner/Defendant-Appellant.       Appellees.
    ══════════════════  …and its pair       ══════════════════
                                            SCAP-24-0000673   the docket
    CERTIORARI TO THE INTERMEDIATE …        APPEAL FROM THE FAMILY COURT …
    (CAAP-24-0000674; CASE NO. 1FFC-…)      (CASE NO. 1FPA-24-0000203)
                                            May 18, 2026        the date
                                            DEVENS, C.J., McKENNA, … JJ.,
                                            AND CIRCUIT JUDGE MALINAO, …
    ORDER REJECTING APPLICATION …           OPINION OF THE COURT BY McKENNA,
    ──────────────────  UNDERLINED          ──────────────────  UNDERLINED
    (By: McKenna, Acting C.J., …)           I. Introduction

    'open cover' (1 of 50 — state_v._wilhelm, an ICA summary disposition
    filed into this corpus) draws NO fence. Its zones stand apart by a 44pt
    stand-off against a 14.8pt leading, and the zone holding the pivot row
    is the caption. Everything else reads the same.

THE DISPATCH is a single question about page 1: does the page set a fence
PAIR — a rule at least 0.62 of the measure, centred on the page axis to
within 10pt, below the stamp band, and not an underline? Two of them makes
the ruled cover; none, with a pivot zone and an underlined row below it,
makes the open cover; anything else is not this paper and gets NOTHING
(m.s._v._l.s. is a bare dissent whose page 1 opens on its byline — there is
no cover on it to read).

WHERE THE READER STOPS: at the first UNDERLINED ROW below the caption. Both
papers rule the row that opens their writing — the order's title
('ORDER REJECTING APPLICATION FOR WRIT OF CERTIORARI', 'ORDER', 'AMENDED¹
ORDER …') and the opinion's byline ('OPINION OF THE COURT BY McKENNA, J.') —
and the court draws that rule to the row's own measure, to the point. So one
geometric test ends the reader on every record, and neither the title nor the
'(By: <panel>)' roster beneath it is taken out of the writing it opens. Their
text is still READ (into `title`, `panel`, `decision_date`) — reading is not
claiming.

AN UNDERLINE IS NOT A FENCE, and on this court the difference is 3pt of x.
'AMENDED¹ ORDER REJECTING APPLICATION FOR WRIT OF CERTIORARI' is 422.9pt
wide and centred on the axis to the decimal — a fence by every measure except
that the row above it has exactly the same ends. The publication banner is
underlined too, at 459–468pt. Both are refused by the same test: a rule whose
ends coincide with the row above it is that row's underline.

THE CLOSING BAND. Hawaiʻi prints its appearances BELOW the writings, in the
left column of a two-column band whose right column holds the conformed
signatures — ONE printed block in two columns, on the last page of 12 of the
50 records:

    Emily M. Hills,              /s/ Vladimir P. Devens
    Jongwook P. Kim,
    ACLU of Hawaiʻi              /s/ Sabrina S. McKenna
    Makia Minerbi,
    Legal Aid Society of Hawaiʻi /s/ Todd W. Eddins   ← one row, not two
    for appellant JK

It is claimed whole, and the COLUMN says what each row is: at the body rail
an appearance, in the signature column the bench that decided. It is not
`counsel_after_writings` — see the note on the profile below.

WHAT THE READER DOES NOT TOUCH: the disposition's own title, the '(By:
<panel>)' roster, and everything below them. WHAT IT CLAIMS BESIDE THE COVER:
the red e-filing stamp and the reporter's publication banner. A reader that
takes the region inherits its furniture, and core misses both on this court —
the stamp whenever pdfplumber breaks its first row ('Electronically F iled',
jk_v._hk), the banner whenever a writing anchors above it (state_v._wilhelm).

WHY NOT `counsel_after_writings`. Measured, with the flag on: core's trailing
harvest reaches only part of the band (it works on assembled BLOCKS, and
whether a signature row lands in a writing's blocks or in its signature block
varies file to file), and its clerk's-distribution veto — which fires on the
bare token 'dated:' — removes 'DATED: Honolulu, Hawaiʻi, May 4, 2026.' and the
five conformed signatures under it from all 38 orders in the corpus, into the
Removed box. The flag must stay OFF for haw.
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

STYLE_RULED = "ruled cover"
STYLE_OPEN = "open cover"

# ---- haw's declared facts (measured over the 50-record corpus) ----------
# THE BODY RAIL is 72.0pt on every record. Declared, not measured, because
# the one-page orders carry no full-measure body paragraph and DocGeometry
# measures their rail off the e-filing STAMP instead (body_x0=452.0 on 30
# of 50 records) — a rail that is 380pt right of every line of text.
_BODY_X0 = 72.0
_RAIL_TOL = 6.0
# THE FENCE: a rule spanning the body measure, centred on the page axis.
# Drawn as a rect on 31 records (466.5–471.1pt) and typed as underscores on
# 17 (424.8–461.0pt); 0.62 of the 612pt sheet takes both and refuses every
# title underline but one, which the underline test then refuses.
_FENCE_MIN_W = 0.62
_FENCE_AXIS = 10.0
# …and it stands BELOW the stamp band. The publication banner's underline
# is the same measure at 6% of the sheet; the lowest fence in the corpus
# sits at 26%.
_FENCE_TOP_MIN = 0.15
# AN UNDERLINE'S ENDS COINCIDE WITH THE ROW ABOVE IT, to 3pt, within one
# leading.
_UNDER_TOL = 3.0
_UNDER_REACH = 18.0
# THE COVER IS CENTRED ON THE PAGE AXIS — every row of it, on every record.
_AXIS_TOL = 8.0
# THE E-FILING STAMP: six short rows pinned in the page's top quarter,
# right of its 0.55 mark. No content row on any cover stands there.
_STAMP_BAND = 0.25
_STAMP_X = 0.55
# THE PUBLICATION BANNER stands in the top tenth and is core's to drop.
_BANNER_BAND = 0.10
# HOW FAR THE COVER MAY RUN: in_re_tax_appeal's consolidated caption carries
# its origin to the foot of page 1 and rules its title on page 2.
_MAX_PAGES = 3
# THE CLOSING BAND's rows stand one leading apart; 40pt separates the
# roster from the footnote zone below it (choi p26).
_BAND_GAP = 40.0

# 'SCWC-24-0000674' / 'NO. CAAP-24-0000597' / 'SCWC—25-0000393' (the court
# sets an em dash on one record) / 'SCWC-25-00000524' (and five zeros on
# another). This court's own docket and no other: a bare number inside the
# caption ('1CTX-24-0000241') opens with a digit and is not one.
_DOCKET = re.compile(r"^(?:NO\.\s*)?[A-Z]{2,5}[-‑–—]\d{2}[-‑–—]\d{4,9}$")
# The number a court BELOW gave the case, in every form haw prints:
# 'CAAP-24-0000674', '1FFC-23-0000136', '2CCV-21-0000286(1)',
# '1:23-cv-00104-JMS-KJM', 'SUP 220210001', '2DTA-21-00171'.
_LOWER_DOCKET = re.compile(
    r"\b[0-9]?[A-Z]{2,5}[-‑]\d{2}[-‑]\d{3,9}(?:\(\d\))?"
    r"|\b\d{1,2}:\d{2}[-‑][a-z]{2}[-‑]\d{3,6}(?:[-‑][A-Z]{2,4})*\b"
    r"|\bSUP\s+\d{6,12}\b"
    r"|\b1CC\d{6,9}\b")
# THE COURT'S DEVICE, printed between the masthead and the caption of a
# published opinion: '---o0o---' / '---oOo---'.
_ORNAMENT = re.compile(r"^[-–—oO0]{5,}$")
# A TYPED FENCE is a row of underscores and nothing else.
_TYPED_RULE = re.compile(r"^_{12,}$")
# THE PIVOT, on its own row. 'vs.' on 47 records, 'v.' on the ICA's.
_PIVOT = ("v", "vs")
# A PARTY STATUS row: every alphabetic token is a role word. Hawaiʻi stacks
# them ('Respondent/Defendant/Counterclaimant/', 'Third-Party
# Plaintiff-Appellee,', 'Petitioners/Appellants-Appellants.'), so the row is
# read as the set of roles it names, never as a phrase.
_ROLE_WORDS = frozenset("""
plaintiff plaintiffs defendant defendants appellant appellants appellee
appellees petitioner petitioners respondent respondents cross third party
counterclaim counterclaimant counterclaimants intervenor intervenors
interested successor amicus amici curiae and
""".split())
# THE BENCH VOCABULARY — the finite set of ways this court names a seat.
# Used to tell a panel row from an origin row, and to read the roster.
_BENCH_TITLES = ("c.j.", "j.", "jj.", "v.c.j.", "chief judge",
                 "associate judge", "judge", "judges", "justice",
                 "justices", "acting c.j.")
# …and the single-word half of it, for the question 'is this row a bench
# roster at all'. Tested as WHOLE TOKENS: the court closes every seat with
# a comma ('DEVENS, C.J., McKENNA, EDDINS, AND GINOZA, JJ.,'), so a
# substring test for ' c.j. ' finds nothing on any panel row in the corpus.
_BENCH_TOKENS = frozenset(t for t in _BENCH_TITLES if " " not in t)
_BENCH_LEADERS = ("intermediate court of appeals associate judge",
                  "circuit court judge", "circuit judge", "district judge",
                  "chief judge", "associate judge", "judge")
# What a roster says ABOUT a seat, never a name.
_ROSTER_NOISE = ("assigned by reason of vacancy", "recused", "joins",
                 "joined", "dissenting", "concurring", "with whom",
                 "in place of", "by reason of vacancy", "presiding")
# The court's own statement of the day it decided ('DATED: Honolulu,
# Hawaiʻi, May 4, 2026.'), printed inside the order it signs.
_DATED = "dated:"


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _alpha_tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^A-Za-z]+", text) if t]


def _is_status_row(text: str) -> bool:
    toks = _alpha_tokens(text)
    return bool(toks) and all(t.lower() in _ROLE_WORDS for t in toks)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in _PIVOT


def _is_docket(text: str) -> bool:
    return bool(_DOCKET.match(_norm(text)))


def _has_bench(text: str) -> bool:
    return any(t.strip(",;:()").lower() in _BENCH_TOKENS
               for t in _norm(text).split())


def _lower_dockets(text: str) -> list[str]:
    return [_norm(t) for t in _LOWER_DOCKET.findall(text)]


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its column gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "bottom", "x0", "x1", "size",
                 "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.bottom = max(p.bottom for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(lines: list) -> list:
    """Group lines into the visual rows the page printed."""
    buckets: dict = {}
    loose: list = []
    for line in lines:
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
    rows = [_Row(g) for g in groups]
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _is_underline(rule, pm) -> bool:
    """A rule whose ends coincide with the row above it is that row's
    underline, not a fence — the general test ca1 and ca5 arrived at, and
    the only thing that separates haw's 422.9pt title underline from its
    424.8pt typed fence."""
    return any(rule.top - _UNDER_REACH <= l.top <= rule.top
               and abs(l.x0 - rule.x0) <= _UNDER_TOL
               and abs(l.x1 - rule.x1) <= _UNDER_TOL
               for l in pm.lines if l.plain.strip())


def _drawn_fences(pm) -> list:
    out = []
    for r in pm.h_rules:
        if r.width < _FENCE_MIN_W * pm.width:
            continue
        if r.top < _FENCE_TOP_MIN * pm.height:
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        if _is_underline(r, pm):
            continue
        out.append(r.top)
    return sorted(out)


def _is_typed_fence(row: _Row, pm) -> bool:
    if not _TYPED_RULE.match(row.text.replace(" ", "")):
        return False
    if row.x1 - row.x0 < _FENCE_MIN_W * pm.width:
        return False
    return abs((row.x0 + row.x1) / 2 - pm.width / 2) <= _FENCE_AXIS


def _underlined_row(row: _Row, pm) -> bool:
    """The row the page RULES — the order's title, the opinion's byline."""
    return any(row.top < r.top <= row.bottom + 6
               and abs(r.x0 - row.x0) <= _UNDER_TOL
               and abs(r.x1 - row.x1) <= _UNDER_TOL
               for r in pm.h_rules)


# --------------------------------------------------------------------------
# the roster
# --------------------------------------------------------------------------

def _roster_names(text: str) -> list[str]:
    """The seats a Hawaiʻi roster names, in order.

    '(By: Devens, C.J., McKenna, Eddins, and Ginoza, JJ., and Circuit Judge
    Souza, in place of Ginoza, J., recused, and Circuit Judge Malinao,
    assigned by reason of vacancy)' names five judges; read by splitting on
    punctuation it also names 'in place of Ginoza', 'recused' and 'assigned
    by reason of vacancy'. So the walk carries a closed vocabulary: a TITLE
    closes the names standing before it, a LEADER opens a titled name, and
    a clause ABOUT a seat is skipped whole."""
    body = _norm(text)
    if body.lower().startswith("(by:") or body.lower().startswith("(by "):
        body = body.split(":", 1)[-1] if ":" in body[:5] else body[4:]
    body = body.strip().lstrip("(").rstrip(")").strip()
    out: list[str] = []
    pending: list[str] = []
    skipping = False
    for raw in re.split(r"[,;]|\s+and\s+", body, flags=re.I):
        tok = raw.strip().strip(",;() ")
        if not tok:
            continue
        low = tok.lower()
        if skipping:
            # 'in place of Ginoza, J., recused' — the clause runs to its
            # own closing word.
            if "recused" in low:
                skipping = False
            continue
        if low.startswith("in place of"):
            skipping = True
            continue
        if any(low.startswith(n) or low == n for n in _ROSTER_NOISE):
            if low.startswith("with whom"):
                tok = tok[len("with whom"):].strip()
                low = tok.lower()
            else:
                continue
        # 'Ginoza JJ.' — the court drops the comma on two records. Tested
        # AFTER the title itself, or 'Acting C.J.' reads as a judge called
        # Acting.
        if low not in _BENCH_TITLES:
            for title in ("jj.", "c.j.", "j.", "v.c.j."):
                if low.endswith(" " + title):
                    pending.append(tok[: -len(title)].strip())
                    tok, low = title, title
                    break
        if low in _BENCH_TITLES:
            out.extend(p for p in pending if p)
            pending = []
            continue
        lead = next((l for l in _BENCH_LEADERS if low.startswith(l)), None)
        if lead:
            name = tok[len(lead):].strip()
            for noise in _ROSTER_NOISE:
                idx = name.lower().find(noise)
                if idx > 0:
                    name = name[:idx].strip()
            if name:
                out.append(name)
            continue
        pending.append(tok)
    out.extend(p for p in pending if p)
    seen: set = set()
    names: list[str] = []
    for n in out:
        n = n.strip(" .,")
        if n and n.lower() not in seen:
            seen.add(n.lower())
            names.append(n)
    return names


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom):
        self.model = model
        self.geom = geom
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.attorneys: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, centre: bool = True) -> None:
        pm = self.pages[row.page]
        ok = centre and abs((row.x0 + row.x1) / 2 - pm.width / 2) <= _AXIS_TOL
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align.CENTER if ok else m.Align.LEFT,
            x0=row.x0, size=row.size, role=role))
        self.consumed.update(row.ids)

    def counsel(self, line, role: str = "counsel") -> None:
        self.attorneys.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            role=role))
        self.consumed.add(line.id)

    def rule(self, page: int, ids: tuple = (), typed: bool = False) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids), typed=typed,
                                 span="full"))
        self.consumed.update(ids)

    def drop(self, rows: list, kind: str) -> None:
        if not rows:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(r.text for r in rows)[:1200],
            prov=m.Prov(rows[0].page,
                        tuple(i for r in rows for i in r.ids)),
            kind=kind))
        for r in rows:
            self.consumed.update(r.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "dropped": self.dropped,
                "consumed": self.consumed, "anchor_ids": [],
                "doc_type_final": None}


@decider("headmatter.read", court="haw")
def read_headmatter_haw(model, geom, **_):
    """Read one of haw's two covers, or NOTHING."""
    if not model.pages:
        return NOTHING
    finder = FurnitureFinder(model, _BODY_X0,
                             geom.body_size if geom else 12.0)
    ctx = _Ctx(model, geom)

    # --- the cover's own rows, furniture set aside -----------------------
    rows: list = []
    stamp: list = []
    banner: list = []
    for pm in model.pages[:_MAX_PAGES]:
        content: list = []
        stamped: list = []
        for line in pm.lines:
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            # THE STAMP IS A COLUMN, and it is sorted out BEFORE the rows
            # are grouped. The cover's docket sits within 3pt of the
            # stamp's last line on 8 records, so pdfio gives the two ONE
            # visual row; grouped first, the docket reads as neither
            # ('SCWC-23-0000412  Dkt. 11 OGAC') and both are lost.
            if (line.top < _STAMP_BAND * pm.height
                    and line.x0 > _STAMP_X * pm.width):
                stamped.append(line)
            else:
                content.append(line)
        stamp.extend(_visual_rows(stamped))
        for row in _visual_rows(content):
            if (pm.number == 1
                    and row.top < _BANNER_BAND * pm.height
                    and row.x1 - row.x0 >= 0.5 * pm.width):
                banner.append(row)
            else:
                rows.append(row)
    if not rows:
        return NOTHING

    page1 = model.pages[0]
    p1 = [r for r in rows if r.page == 1]
    fences = [("drawn", t, None) for t in _drawn_fences(page1)]
    fences += [("typed", r.top, r) for r in p1 if _is_typed_fence(r, page1)]
    fences.sort(key=lambda f: f[1])

    if len(fences) >= 2:
        out = _read_cover(ctx, rows, fences[:2], STYLE_RULED)
    else:
        out = _read_cover(ctx, rows, None, STYLE_OPEN)
    if out is NOTHING:
        return NOTHING
    ctx.drop(stamp, "stamp")
    # THE PUBLICATION BANNER is core's notice drop everywhere else, and
    # core reaches it at SEGMENT level — but on a record whose writing
    # anchors above it (state_v._wilhelm's summary disposition takes its
    # byline from the conformed signature six pages later) the banner is
    # inside the writing before that pass runs, the writing's span then
    # covers the whole cover, and core's bisection invariant puts every row
    # this reader placed back into it. A reader that claims the region
    # inherits its furniture; the STATUS it states is core's to record and
    # core reads it off the page, not off this claim.
    ctx.drop(banner, "status")
    _read_closing_band(ctx, model, finder)
    return ctx.result()


def _zones(rows: list) -> list:
    """The cover's own blocks. The open cover fences nothing — it sets a
    44pt stand-off against a 14.8pt leading, and that gap is the only mark
    it gives. The LEADING is the smallest pitch the block sets, not the
    median: a two-row masthead stands 28pt apart on the one record that
    prints one, and a median taken over the whole cover puts the split
    right through it."""
    pitches = sorted(b.top - a.top for a, b in zip(rows, rows[1:])
                     if b.page == a.page and b.top > a.top)
    if not pitches:
        return [rows]
    lead = pitches[0]
    out: list = [[rows[0]]]
    for prev, row in zip(rows, rows[1:]):
        if row.page != prev.page or row.top - prev.top > lead * 2.0:
            out.append([])
        out[-1].append(row)
    return out


def _read_cover(ctx: _Ctx, rows: list, fences, style: str):
    """HEAD, CAPTION, TAIL — bounded by the fence pair where the page draws
    one, by the pivot's own zone where it does not, and ended on every
    record by the first UNDERLINED row."""
    head: list = []
    caption: list = []
    tail: list = []
    stop: _Row | None = None
    if fences is not None:
        f1, f2 = fences[0][1], fences[1][1]
        for row in rows:
            pm = ctx.pages[row.page]
            if row.page == 1 and (fences[0][2] is row or fences[1][2] is row):
                continue                      # the typed fence itself
            if _underlined_row(row, pm) and (row.page > 1 or row.top > f2):
                stop = row
                break
            if row.page == 1 and row.top < f1:
                head.append(row)
            elif row.page == 1 and row.top < f2:
                caption.append(row)
            else:
                tail.append(row)
        if not (head and caption):
            return NOTHING
    else:
        # THE STOP COMES FIRST on the open cover: the cover is the run of
        # rows above the row the page rules, and the zoning is measured
        # inside that run — never across the body prose below it.
        pm1 = ctx.pages[1]
        cover: list = []
        for row in rows:
            if row.page != 1:
                break
            if row.top > _FENCE_TOP_MIN * pm1.height \
                    and _underlined_row(row, pm1):
                stop = row
                break
            cover.append(row)
        if stop is None or not cover:
            return NOTHING
        zones = _zones(cover)
        pivot_zone = next((i for i, z in enumerate(zones)
                           if any(_is_pivot(r.text) for r in z)), None)
        if pivot_zone is None or pivot_zone == 0:
            return NOTHING
        for i, zone in enumerate(zones):
            for row in zone:
                (head if i < pivot_zone else
                 caption if i == pivot_zone else tail).append(row)
        if not (head and caption):
            return NOTHING
    if stop is None:
        return NOTHING

    # --- HEAD: the docket, the masthead, the court's device -------------
    masthead: list = []
    for row in head:
        if _is_docket(row.text):
            _record_docket(ctx, row.text)
            ctx.emit(row, "docket")
        elif _ORNAMENT.match(row.text.replace(" ", "")):
            ctx.emit(row, "court")
        else:
            masthead.append(row.text)
            ctx.emit(row, "court")
    if masthead:
        ctx.crit["court"] = " ".join(masthead)

    # --- the fence, the caption, the fence ------------------------------
    if fences is not None:
        ctx.rule(1, fences[0][2].ids if fences[0][2] else (),
                 typed=fences[0][0] == "typed")
    for row in caption:
        ctx.emit(row, "caption")
    if fences is not None:
        ctx.rule(1, fences[1][2].ids if fences[1][2] else (),
                 typed=fences[1][0] == "typed")
    ctx.crit["caption"] = [r.text for r in caption]
    _read_parties(ctx, caption)

    # --- TAIL: the docket, the origin, the date, the bench --------------
    origin: list = []
    panel: list = []
    for row in tail:
        if _is_docket(row.text):
            _record_docket(ctx, row.text)
            ctx.emit(row, "docket")
        elif find_date(row.text) and len(row.text) <= 40:
            ctx.crit.setdefault("decision_date", find_date(row.text))
            ctx.emit(row, "date")
        elif _has_bench(row.text):
            panel.append(row.text)
            ctx.emit(row, "panel")
        else:
            origin.append(row.text)
            ctx.emit(row, "lower-court")
    _record_origin(ctx, origin)

    # --- what the page states below the stop, READ but never claimed ----
    ctx.crit["headmatter_style"] = style
    if not BylineParser(get_profile("haw").byline).parse(stop.text):
        ctx.crit["title"] = stop.text.rstrip(".")
    if not panel:
        panel = _roster_below(ctx, stop)
    if panel:
        ctx.crit["panel_line"] = " ".join(panel)
        names = _roster_names(" ".join(panel))
        if names:
            ctx.crit["panel"] = names
    if "decision_date" not in ctx.crit:
        dated = _dated_line(ctx.model)
        if dated:
            ctx.crit["decision_date"] = dated
    return None


def _roster_below(ctx: _Ctx, stop: _Row) -> list[str]:
    """The '(By: <panel>)' roster an order prints under its title. It is the
    WRITING's opening apparatus and stays there; what it says is still a
    fact about this document."""
    pm = ctx.pages[stop.page]
    below = sorted((l for l in pm.lines
                    if l.top > stop.top and l.plain.strip()),
                   key=lambda l: l.top)
    run: list[str] = []
    for line in below[:6]:
        text = _norm(line.plain)
        if not run and not text.lower().startswith(("(by:", "(by ")):
            if run:
                break
            continue
        run.append(text)
        if text.endswith(")"):
            break
    return run


def _dated_line(model) -> str | None:
    for pm in model.pages:
        for line in pm.lines:
            text = _norm(line.plain)
            if text.lower().startswith(_DATED):
                return find_date(text)
    return None


def _record_docket(ctx: _Ctx, text: str) -> None:
    docket = _norm(text)
    if docket.upper().startswith("NO."):
        docket = docket[3:].strip()
    if "docket_number" not in ctx.crit:
        ctx.crit["docket_number"] = docket
    elif docket != ctx.crit["docket_number"]:
        ctx.crit.setdefault("other_dockets", []).append(docket)


def _record_origin(ctx: _Ctx, rows: list) -> None:
    """The origin, split into what the court BELOW is and what it numbered.

    Hawaiʻi states the route in prose ('CERTIORARI TO THE INTERMEDIATE COURT
    OF APPEALS', 'APPEAL FROM THE FAMILY COURT OF THE FIRST CIRCUIT',
    'ORIGINAL PROCEEDING') and then parenthesises every number the case
    carried below it."""
    prose = [r for r in rows if not r.startswith("(")]
    if prose:
        ctx.crit["lower_court"] = " ".join(prose)
    numbers: list[str] = []
    for row in rows:
        for dk in _lower_dockets(row):
            if dk not in numbers:
                numbers.append(dk)
    if numbers:
        ctx.crit["lower_court_docket"] = numbers


def _tidy(text: str) -> str:
    """Close a party name. A trailing period after a CAPITAL is a
    generational suffix, not a full stop ('WILLIAM MEDEIROS, JR.')."""
    out = text.rstrip(" ,;")
    if out.endswith(".") and not (len(out) >= 2 and out[-2].isupper()):
        out = out[:-1]
    return out.rstrip(" ,;")


def _side_name(rows: list[str]) -> str:
    """One side of the pivot, as the party names the court printed there —
    never the whole side joined, which drags every status label in with it.

    A status may stand on a row of its own ('Petitioners/Plaintiffs-
    Appellants,') or close the name's own row ('M.S., Respondent/Plaintiff-
    Appellee,'); both are the same closed role vocabulary."""
    out: str = ""
    broke = False
    for row in rows:
        text = _norm(row).strip()
        if not text or _is_status_row(text):
            # A STATUS ROW SEPARATES TWO PARTIES. 'BRANDY BLAS,' /
            # 'Petitioner/Defendant-Appellee,' / 'and' / 'THOMAS BLAS,
            # SR.,' names two respondents; dropped silently, the two names
            # close up into one ('BRANDY BLAS THOMAS BLAS, SR.').
            broke = broke or bool(out)
            continue
        bare = _tidy(text)
        head, sep, tail = bare.rpartition(",")
        if sep and head.strip() and _is_status_row(tail):
            text = head.strip()
        # The row's OWN punctuation survives the join: a party list set
        # over four rows separates its parties with the comma each row
        # ends on, and stripping them read 'a minor TRISHA BOUCHER'.
        if not out:
            out = text
        elif broke and not out.rstrip().endswith((",", ";")):
            out += "; " + text
        else:
            out += " " + text
        broke = False
    return _tidy(_norm(out))


def _read_parties(ctx: _Ctx, caption: list) -> None:
    texts = [r.text for r in caption]
    pivots = [i for i, t in enumerate(texts) if _is_pivot(t)]
    if pivots:
        left = _side_name(texts[:pivots[0]])
        right = _side_name(texts[pivots[0] + 1:])
        if left and right:
            ctx.crit["parties"] = [left, right]
            ctx.crit["case_name"] = f"{left} v. {right}"
            return
    whole = _side_name(texts)
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


# --------------------------------------------------------------------------
# the closing band
# --------------------------------------------------------------------------

_COUNSEL_MARKS = ("for appellant", "for appellee", "for petitioner",
                  "for respondent", "for plaintiff", "for defendant",
                  "on the brief", "on the briefs", "pro se")


def _read_closing_band(ctx: _Ctx, model, finder) -> None:
    """The two-column band the court prints below its writings: the
    appearances left, the conformed signatures right.

    It is ONE printed block in two columns — the page interleaves them row
    by row — and it is claimed WHOLE. Claiming only the counsel column
    leaves the roster's rows lying between the signature rows that stay in
    the writing, and core's bisection invariant (a row filed elsewhere
    inside a writing's span belongs to that writing) then puts the head of
    the roster back: measured over the 12 records that print a band, a
    left-column-only claim survived intact on 3 and lost 1–6 rows on the
    other 9, because whether a signature row lands in the writing's blocks
    or in its signature block varies file to file. The invariant compares
    positions and not COLUMNS, and beside is not inside — but the band is
    one block either way, so it is read as one.

    The band opens at the first conformed signature and closes where the
    page next stands off by more than a couple of leadings (choi sets a
    footnote below it). A record whose band names no appearance is a
    signature block alone (every one-page order) and is not claimed."""
    pm = model.pages[-1]
    lines = [l for l in pm.lines
             if l.plain.strip() and not finder.kind(pm, l)]
    sigs = [l for l in lines if _norm(l.plain).startswith("/s/")]
    if not sigs:
        return
    sig_x0 = min(l.x0 for l in sigs)
    if sig_x0 < pm.width * 0.35:
        return
    top = min(l.top for l in sigs) - 6
    band: list = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if line.top < top:
            continue
        if band and line.top - max(b.top for b in band) > _BAND_GAP:
            break
        band.append(line)
    joined = " ".join(_norm(l.plain) for l in band
                      if l.x0 <= _BODY_X0 + _RAIL_TOL).lower()
    if not any(mk in joined for mk in _COUNSEL_MARKS):
        return
    for line in band:
        # THE COLUMN SAYS WHICH IT IS. The appearances stand at the body
        # rail; the seats stand in the signature column, and what they
        # name is the bench that decided ('/s/ Karen T. Nakasone' over
        # 'Chief Judge'). Two rows in the corpus set the two columns close
        # enough that pdfio could not split them ('Legal Aid Society of
        # Hawaiʻi /s/ Todd W. Eddins'); a row the page glued is read as
        # the appearance it opens with rather than torn in half.
        left = line.x0 <= _BODY_X0 + _RAIL_TOL
        ctx.counsel(line, "counsel" if left else "panel")
