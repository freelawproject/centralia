"""The Supreme Court of South Carolina ('sc').

Everything unique to sc lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — A DRAWN FENCED LADDER. South Carolina names itself twice at
the top of the page, sets the parties and the appellate case number at a
rail 72pt inside the body rail, and then DRAWS a short horizontal rule
between every remaining section. The rules are the parser: each one closes a
band, and the band — not the row — is the unit of meaning.

    ┌────────────────────────────────────────────────────────────────────┐
    │              THE STATE OF SOUTH CAROLINA        the masthead,      │
    │                 In The Supreme Court            two rows, centred  │
    │                                                                    │
    │      Alexis Jones, Respondent,                  the caption, at    │
    │      v.                                         the RAIL (x0=144)  │
    │      Progressive Northern Insurance Company, Petitioner.           │
    │                                                                    │
    │      Appellate Case No. 2025-000943             the docket, last   │
    │                                                 row at the rail    │
    │                    ─────────────                a DRAWN fence      │
    │        ON WRIT OF CERTIORARI TO THE COURT OF APPEALS   posture     │
    │                    ─────────────                                   │
    │             Appeal from Chester County          the origin         │
    │        Brian M. Gibbons, Circuit Court Judge    …and its judge     │
    │                    ─────────────                                   │
    │                Opinion No. 28325                the paper's number │
    │      Heard February 10, 2026 – Filed April 22, 2026     the dates  │
    │                    ─────────────                                   │
    │                     REVERSED                    the disposition    │
    │                    ─────────────                                   │
    │      John Robert Murphy and Megan Noelle Walker, both of  counsel, │
    │      Murphy & Grantland, P.A., of Columbia, for Petitioner.  at    │
    │      …                                                    the rail │
    │                    ─────────────                                   │
    │ JUSTICE JAMES: In this case, we address …       the writing, at    │
    │                                                 the BODY RAIL      │
    └────────────────────────────────────────────────────────────────────┘

THE FENCE IS A MEASURED GLYPH, NOT A WIDTH. Over all 50 records the fence
is a drawn rule centred on the page axis (centre 306.0 on a 612pt page;
308.4 on the one wrapped certification band, luce) in three measures —
92.4pt, 97.2pt and 132.1pt. Nothing else on these pages is both on the axis
and that narrow: the footnote separator is 144.0pt wide at centre 144.0
(x0=72, sixty of them across the corpus), the signature lines on the order
cover are 251.6pt at centre 387.2, and the two 324.0pt rules that ARE on the
axis are three times too wide. So the gate is: on the axis within 6pt AND
85–140pt wide.

THE RAIL SAYS 'CASE', THE AXIS SAYS 'PAPER', AND THE BODY RAIL SAYS
'WRITING'. Three positions, measured on all 50 records and invariant:

  x0 = 144.0   the caption rail — parties, the docket row, and counsel;
  centred      everything the court says ABOUT the paper — masthead,
               posture, origin, opinion number, dates, disposition;
  x0 =  72.0   the body rail — nothing in the headmatter stands there, and
               the byline that opens the writing always does ('JUSTICE
               JAMES:', 'CHIEF JUSTICE KITTREDGE:', 'PER CURIAM:').

That last fact is what ends the reader, and it needs no byline vocabulary at
all. The narrowest centred headmatter row measured is x0=109.1 ('ON
CERTIFICATION FROM THE UNITED STATES DISTRICT', luce), 37pt clear of the
body rail.

CASE, NOT CAPS, SEPARATES THE ORIGIN FROM THE POSTURE. Two kinds of band
stand between the docket and the opinion number, and their ORDER is not a
discriminator: an original-jurisdiction record prints only the posture, and
a direct appeal prints only the origin, so 'the band before the opinion
number' is sometimes one and sometimes the other. What separates them is
TYPE CASE. The posture is set entirely in capitals ('ON WRIT OF
CERTIORARI', 'IN THE COURT'S ORIGINAL JURISDICTION', 'IN THE ORIGINAL
JURISDICTION', 'CERTIFIED QUESTION'); an origin band always carries at
least one mixed-case row, because it names a person ('Appeal from
Charleston County' / 'George M. McFaddin, Jr., Circuit Court Judge';
'Ralph King Anderson, III'; 'Mary Geiger Lewis, United States District
Judge'). Tagging by position instead put "IN THE COURT'S ORIGINAL
JURISDICTION" — a statement that there IS no court below — under
`lower-court` on three records.

Inside an origin band the tribunal is the first row plus any capitalised
continuation of it (luce wraps 'ON CERTIFICATION FROM THE UNITED STATES
DISTRICT / COURT FOR THE DISTRICT OF SOUTH CAROLINA' over two rows), and
every remaining row is a judge — murdaugh names two.

'Opinion No. 28325' TAKES THE `citation` ROLE. It is not the docket: the
docket is the 'Appellate Case No. 2025-000943' row at the rail, and the two
numbers are different things (the appellate case number identifies the
APPEAL, the opinion number identifies the PAPER and is what a South Carolina
slip opinion is cited by before its S.E.2d cite exists). Serial and
court-assigned — 28291 through 28339 over these 50 records — it is the only
neutral identifier this court prints, so it is recorded as `citation` rather
than parked on `case-info`.

THE ORDER COVER IS A DIFFERENT PAPER AND IS DELIBERATELY UNCLAIMED. One
record (state_v._john_joseph_erb) opens on a rehearing order whose masthead
is a single 22pt row, 'The Supreme Court of South Carolina', and whose
ladder holds an 'ORDER' band, body prose, five 's/' signature lines and a
place-and-date — then starts the whole contract again on page 2 with the
substituted opinion. This reader dispatches on the two-row masthead
('THE STATE OF SOUTH CAROLINA' over 'In The Supreme Court') and on an
'Opinion No.' band, so that record returns NOTHING and core keeps the
reading it already had. Claiming page 1 and stopping at the order's prose
would have left page 2's second headmatter inside the order's writing.

THE CLAIM IS TOTAL OR IT IS NOTHING. Every row between the masthead and the
first body-rail row must land in a band this contract names; a row that does
not is not a licence to guess, and it is not a licence to leave a HOLE
either — a hole lets core open a writing on the unclaimed row, and the
bisection invariant then pulls the claimed rows into it and the headmatter
renders empty. So an unrecognised row aborts the whole claim.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# --- the masthead ---------------------------------------------------------
# Two rows, centred, on all 49 records this contract covers. The type size
# steps with the paper — 14.0pt on the appeals, 15.0pt on the attorney and
# judicial discipline opinions — so the size is not the landmark; the words
# the court prints about itself are.
_MAST_STATE = re.compile(r"^THE STATE OF SOUTH CAROLINA$")
_MAST_COURT = re.compile(r"^In The Supreme Court$")

# --- the closed labels ----------------------------------------------------
# 'Appellate Case No. 2025-000943' — the last row at the rail in the
# identity band, on all 49 records.
_DOCKET = re.compile(r"^Appellate Case Nos?\.\s*(.+)$", re.I)
# 'Opinion No. 28325' — the landmark the ladder is read from.
_OPINION_NO = re.compile(r"^Opinion No\.\s*(\S+)\s*$", re.I)
# 'Heard February 10, 2026 – Filed April 22, 2026' /
# 'Submitted June 23, 2025 – Filed July 30, 2025'. The separator is an EN
# DASH on every record measured; a hyphen is accepted for safety.
_DATES = re.compile(
    r"^(Heard|Submitted|Reheard|Resubmitted|Argued)\s+(.+?)\s*[–—-]\s*"
    r"Filed\s+(.+?)\s*$", re.I)
# 'Withdrawn, Substituted, and Refiled November 26, 2025' — the third row of
# the opinion-number band on a substituted opinion (erb page 2).
_REFILED = re.compile(
    r"^(Withdrawn|Substituted|Refiled)\b.*?Refiled\s+(.+?)\s*$", re.I)
# 'Appeal from Chester County' / 'Appeal From Orangeburg County' /
# 'Appeal from the Administrative Law Court'.
_APPEAL_FROM = re.compile(r"^Appeal\s+[Ff]rom\b")

# --- the three measured positions ----------------------------------------
# THE CAPTION RAIL: x0 = 144.0 exactly on all 49 records, for the party
# rows, the docket row and every counsel row. 72pt inside the body rail.
_RAIL = 144.0
_RAIL_TOL = 3.0
# THE BODY RAIL ends the reader. Measured: x0 = 72.0 on all 50 records, and
# no headmatter row stands within 37pt of it (the closest is x0=109.1,
# luce's wrapped certification row).
#
# IT IS MEASURED HERE, NOT TAKEN FROM `geom`. Core derives `body_x0` from the
# most common left edge of the full-measure lines, and on a record whose
# opinion is three paragraphs long the caption and counsel rows at the
# CAPTION rail outvote the prose: city_of_charleston_v._city_of_north_-
# charleston (2 pages) measures body_x0 = 144.0, which ended the reader on
# the first party row and cost the whole claim. On
# estate_of_william_pratt_v._amisub_of_sc_inc. core returns no geometry at
# all. So `geom` is used only when it agrees that the body rail is well
# inside the caption rail.
_BODY_RAIL = 72.0
_BODY_TOL = 10.0
# A centred row's mid-point against the page's. The masthead measures
# 305.7–306.0, the dates and dispositions 306.0, luce's certification band
# 299.4–308.4.
_AXIS_TOL = 12.0

# --- the fence ------------------------------------------------------------
# See the module docstring: on the axis AND narrow. The three measures are
# 92.4pt (52 rules), 97.2pt (203) and 132.1pt (1, luce); the things this
# gate must exclude are the 144.0pt footnote separator at centre 144.0 and
# the 251.6pt signature lines at centre 387.2 on the order cover.
_FENCE_AXIS_TOL = 6.0
_FENCE_W_MIN = 85.0
_FENCE_W_MAX = 140.0

# The headmatter never runs past page 5 (john_a._tibbs sets a 91-row caption
# over three pages and reaches its counsel on page 4). Six is the bound; a
# record whose byline is not found inside it is not read at all.
_MAX_PAGES = 6

# PARTY STATUS IS A CLOSED VOCABULARY, party NAMES are not. Used only to
# trim the status label off a party group when building `case_name` — never
# to decide what a row IS.
_STATUS = re.compile(
    r",\s*(?:(?:Third-Party|Fourth-Party)\s+)?"
    r"(?:Petitioners?|Respondents?|Appellants?|Appellees?|Plaintiffs?"
    r"|Defendants?|Intervenors?|Movants?|Claimants?"
    r"|Petitioner-Respondents?|Respondent-Petitioners?"
    r"|Respondent-Intervenors?|Intervenors?-Respondents?"
    r"|Appellant-Respondents?|Respondent-Appellants?)"
    r"\s*[,.;]", re.I)
# The caption's pivot row, printed alone at the rail ('v.'), and the row
# that joins consolidated captions ('And' / 'AND' / 'and').
_PIVOT = re.compile(r"^v\.$", re.I)
_JOINER = re.compile(r"^and$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_caps(text: str) -> bool:
    """The row is set in capitals — measured as: it holds at least one
    cased letter and no lower-case one. This is the origin/posture
    discriminator, so apostrophes, digits and punctuation must not spoil it
    ("IN THE COURT'S ORIGINAL JURISDICTION")."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and not any(c.islower() for c in letters)


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is `docket_number`
# (a string) plus `other_dockets` (the rest), and a heard/argued date belongs
# in `submitted`. Written under invented names they are attached by setattr
# and never serialize — read as read, reported as nothing.


@decider("headmatter.read", court="sc")
def read_headmatter_sc(model, geom, **_):
    """Read South Carolina's fenced ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = _BODY_RAIL
    if geom and geom.body_x0 and geom.body_x0 < _RAIL - 24.0:
        body_x0 = geom.body_x0
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width

    # THE WALK: rows and fences interleaved in page order, each row carrying
    # the index of the band it fell in. A page's unspent fences are flushed
    # at the page break, or richard_a._butts — whose disposition is the last
    # thing on page 1 and whose closing fence is the last rule on it — reads
    # its counsel as part of the disposition band.
    band = 0
    rows: list[tuple[int, list]] = []          # (band index, row pieces)
    fences: list[tuple[int, int]] = []         # (band index closed, page)
    stopped = False
    for pm in model.pages[:_MAX_PAGES]:
        pending = sorted(_fence_tops(pm, width))
        for group in _rows(pm, finder):
            top = min(l.top for l in group)
            while pending and pending[0] < top:
                pending.pop(0)
                band += 1
                fences.append((band, pm.number))
            if min(l.x0 for l in group) <= body_x0 + _BODY_TOL:
                stopped = True                 # the writing begins
                break
            rows.append((band, group))
        if stopped:
            break
        for _ in pending:                      # flush this page's fences
            band += 1
            fences.append((band, pm.number))
    if not stopped:
        return NOTHING

    # THE DISPATCH: the two-row masthead at the head of the identity band.
    # Never an ordinal — it is the landmark every other role is anchored to.
    head = [i for i, (b, g) in enumerate(rows[:4])
            if b == 0 and _MAST_STATE.match(_norm(_text(g)))]
    if not head:
        return NOTHING
    mast_at = head[0]
    mast = [mast_at]
    if mast_at + 1 < len(rows) and rows[mast_at + 1][0] == 0 \
            and _MAST_COURT.match(_norm(_text(rows[mast_at + 1][1]))):
        mast.append(mast_at + 1)
    if len(mast) != 2:
        return NOTHING

    by_band: dict[int, list[int]] = {}
    for i, (b, _g) in enumerate(rows):
        by_band.setdefault(b, []).append(i)

    # THE SECOND LANDMARK: the band holding 'Opinion No. …'. Everything
    # before it is identity, posture and origin; everything after it is
    # disposition and counsel. A record with no such band is not this
    # contract (the rehearing-order cover) and is left to core.
    num_band = None
    for b in sorted(by_band):
        if b == 0:
            continue
        if any(_OPINION_NO.match(_norm(_text(rows[i][1])))
               for i in by_band[b]):
            num_band = b
            break
    if num_band is None:
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    counsel: list[str] = []

    for b in sorted(by_band):
        idxs = by_band[b]
        texts = [_norm(_text(rows[i][1])) for i in idxs]
        if b == 0:
            if not _identity(ctx, rows, idxs, texts, mast, caption, width):
                return NOTHING
        elif b < num_band:
            # POSTURE (all capitals) or ORIGIN (names a judge, so at least
            # one mixed-case row). See the module docstring.
            if all(_is_caps(t) for t in texts):
                for i, t in zip(idxs, texts):
                    ctx.emit(rows[i][1], "case-info", width)
                ctx.crit.setdefault("history", " ".join(texts))
            elif not _origin(ctx, rows, idxs, texts, width):
                return NOTHING
        elif b == num_band:
            if not _paper(ctx, rows, idxs, texts, width):
                return NOTHING
        else:
            # After the opinion number the ladder holds exactly two kinds of
            # band, and each is told by POSITION: the disposition is centred
            # on the axis, counsel stands at the caption rail.
            if all(_at_rail(rows[i][1]) for i in idxs):
                for i, t in zip(idxs, texts):
                    ctx.emit(rows[i][1], "counsel", width, centre=False)
                    counsel.append(t)
            elif all(_centred(rows[i][1], width) and _is_caps(t)
                     for i, t in zip(idxs, texts)):
                for i in idxs:
                    ctx.emit(rows[i][1], "disposition", width)
                ctx.crit.setdefault("disposition", " ".join(texts))
            else:
                return NOTHING
        # A READER THAT CLAIMS THE BLOCK RE-EMITS ITS FENCES — core draws
        # them only on rows a reader left behind. The fence that OPENS the
        # next band is the one that closes this one, and the last band's
        # closer is the rule between counsel and the byline.
        for _b, page in fences:
            if _b == b + 1:
                ctx.rule(page)
    if not ctx.crit.get("docket_number") or not caption:
        return NOTHING
    ctx.crit["caption"] = caption
    parties = _parties(caption)
    if parties:
        ctx.crit["parties"] = parties
        ctx.crit["case_name"] = _case_name(caption)
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    ctx.crit["headmatter_style"] = "sc drawn fenced ladder"
    return ctx.result()


# --------------------------------------------------------------------------
# the bands
# --------------------------------------------------------------------------

def _identity(ctx, rows, idxs, texts, mast, caption,
              width) -> bool:  # noqa: C901
    """The masthead, the parties and the appellate case number — the band
    above the first fence. The masthead rows are the ones the dispatch
    found; every other row in the band stands at the caption rail, and the
    docket is the one that names itself."""
    said = dict(zip(idxs, texts))
    for i, text in zip(idxs, texts):
        group = rows[i][1]
        if i in mast:
            ctx.emit(group, "court", width)
            continue
        if not _at_rail(group):
            return False
        docket = _DOCKET.match(text)
        if docket:
            # A CONSOLIDATED CAPTION PRINTS ONE NUMBER PER CASE, each on its
            # own row after its own parties (state_v._quinterris_carmichael
            # carries 2025-001214 and 2025-001215). The first is the
            # docket, the rest are companion appeals — written with
            # `setdefault` alone the second was read and then discarded.
            # 'Appellate Case Nos. 2023-000392 and 2024-000576' (murdaugh):
            # the separator is a conjunction, not always a comma.
            parts = [p.strip() for p in
                     re.split(r",|\band\b", docket.group(1)) if p.strip()]
            if ctx.crit.get("docket_number"):
                ctx.crit.setdefault("other_dockets", [])
                ctx.crit["other_dockets"].extend(parts)
            else:
                ctx.crit["docket_number"] = parts[0]
                if parts[1:]:
                    ctx.crit["other_dockets"] = parts[1:]
            ctx.emit(group, "docket", width, centre=False)
            continue
        caption.append(text)
        ctx.emit(group, "caption", width, centre=False)
    ctx.crit.setdefault("court", " ".join(said[i] for i in mast))
    return True


def _origin(ctx, rows, idxs, texts, width) -> bool:
    """The court below and its judge. The tribunal is the first row plus any
    capitalised continuation of it (luce wraps its certification recital
    over two rows); every remaining row names a judge (murdaugh names
    two)."""
    if not _APPEAL_FROM.match(texts[0]) and not _is_caps(texts[0]):
        return False
    cut = 1
    while cut < len(texts) and _is_caps(texts[cut]):
        cut += 1
    for i in idxs:
        ctx.emit(rows[i][1], "lower-court", width)
    ctx.crit.setdefault("lower_court", " ".join(texts[:cut]))
    if texts[cut:]:
        ctx.crit.setdefault("lower_court_judge", "; ".join(texts[cut:]))
    return True


def _paper(ctx, rows, idxs, texts, width) -> bool:
    """The band the ladder is read from: the court's own opinion number and
    the two dates it prints about the paper."""
    for i, text in zip(idxs, texts):
        group = rows[i][1]
        number = _OPINION_NO.match(text)
        if number:
            ctx.crit.setdefault("citation", text)
            ctx.emit(group, "citation", width)
            continue
        dated = _DATES.match(text)
        if dated:
            ctx.crit.setdefault("submitted", _norm(dated.group(2)))
            ctx.crit.setdefault("decision_date", _norm(dated.group(3)))
            ctx.emit(group, "date", width)
            continue
        refiled = _REFILED.match(text)
        if refiled:
            ctx.crit.setdefault("history", text)
            ctx.emit(group, "date", width)
            continue
        return False
    return True


# --------------------------------------------------------------------------
# the caption, parsed beside its printed form
# --------------------------------------------------------------------------

def _groups(caption: list[str]) -> list[list[str]]:
    """The caption's party groups: the rows between the pivot rows ('v.')
    and the consolidation joiners ('And'). A bare 'v.' row is the ordinary
    multi-row caption and must not be folded into its neighbours."""
    out: list[list[str]] = [[]]
    for row in caption:
        if _PIVOT.match(row) or _JOINER.match(row):
            out.append([])
            continue
        out[-1].append(row)
    return [g for g in out if g]


def _join(rows: list[str]) -> str:
    """A party group's rows as one string. A row that ends in a HYPHEN is a
    word broken at the caption's measure and closes up ('Intervenors-' /
    'Respondents.' — climer), which matters because the status label the
    trim looks for is the broken word."""
    out = ""
    for row in rows:
        if out.endswith("-"):
            out += row
        elif out:
            out += " " + row
        else:
            out = row
    return out


def _trim(text: str) -> str:
    """A party group down to its NAME: the printed run up to the first party
    status label. Joining the rows wholesale yields 'Isle of Palms Pest
    Control, Inc., SPM Management Company, Inc. and Terminix Service, Inc.,
    Defendants, Of which …'."""
    hit = _STATUS.search(text)
    return (text[:hit.start()] if hit else text).rstrip(" ,.;")


def _parties(caption: list[str]) -> list[str]:
    return [_trim(_join(g)) for g in _groups(caption)][:8]


def _case_name(caption: list[str]) -> str:
    """'X v. Y', built from the party names either side of the FIRST pivot.
    With no pivot the caption is a single style ('In the Matter of …')."""
    left: list[str] = []
    right: list[str] | None = None
    for row in caption:
        if _PIVOT.match(row):
            if right is None:
                right = []
                continue
            break
        if _JOINER.match(row):
            break
        (left if right is None else right).append(row)
    head = _trim(_join(left))
    if not right:
        return head
    return f"{head} v. {_trim(_join(right))}"


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------

def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


def _at_rail(group: list) -> bool:
    return abs(min(l.x0 for l in group) - _RAIL) <= _RAIL_TOL


def _centred(group: list, width: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


def _fence_tops(pm, width: float) -> list[float]:
    """The band fences this page draws: on the page axis and narrow. See the
    module docstring for what the gate excludes."""
    out = []
    for rule in pm.h_rules:
        span = rule.x1 - rule.x0
        if not _FENCE_W_MIN <= span <= _FENCE_W_MAX:
            continue
        if abs((rule.x0 + rule.x1) / 2 - width / 2) > _FENCE_AXIS_TOL:
            continue
        out.append(rule.top)
    return out


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

    def emit(self, group: list, role: str, width: float,
             centre: bool | None = None) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        if centre is None:
            centre = _centred(group, width)
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

    def rule(self, page: int) -> None:
        # A DRAWN rule, not a typed one: it carries no line ids, so it is
        # re-emitted for the render and consumes nothing.
        self.items.append(m.Rule(prov=m.Prov(page), typed=False,
                                 span="center"))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
