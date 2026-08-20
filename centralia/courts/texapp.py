"""Texas Court of Appeals ('texapp').

Everything unique to texapp lives here. It imports core, never another
court file, and no other court file imports it.

WHAT THIS COURT IS. 'texapp' is not one court. It is FIFTEEN intermediate
courts of appeals filing under one id, and each district sets its own
template. Over the 30-record corpus seven distinct papers appear, and no
two of them agree on where the docket, the masthead or the banner stands:

    2nd  Fort Worth   'In the / Court of Appeals / Second Appellate
                       District of Texas / at Fort Worth', typed '_' fences
    3rd  Austin       'TEXAS COURT OF APPEALS, THIRD DISTRICT, AT AUSTIN'
    4th  San Antonio  'Fourth Court of Appeals / San Antonio, Texas', and
                       the BANNER stands ABOVE the docket
    5th  Dallas       an e-filed motion stapled in front of the paper
    1st  Houston      'In The / Court of Appeals / For The / First District
                       of Texas', typed '—' fences
    11th Eastland     'In The / Eleventh Court of Appeals' at 36pt, typed
                       '_' fences, a release stamp at the head of the page
    13th Corpus Christi–Edinburg
                      the DOCKET first, then the masthead, then a caption
                      set in two columns

THE CONTRACT — 'centered stack'. What they DO agree on is the shape of the
block: page 1 is a stack of CENTERED rows, and every row in it is one of a
small number of landmarks, in whatever order the district prints them:

    Opinion filed July 30, 2026              the release stamp, at the rail
    In The                                   the masthead…
    Eleventh Court of Appeals                 …which names the district
    __________                               a typed fence
    No. 11-26-00023-CR                       the docket
    __________                               and its other fence
    ALBERT LEE MOORE III, Appellant          the caption: a party…
    V.                                        …the pivot…
    THE STATE OF TEXAS, Appellee              …and the other side
    On Appeal from the 91st District Court   the origin, which OPENS on a
    Eastland County, Texas                    closed vocabulary and RUNS to
    Trial Court Cause No. 24903               the next landmark
    M E M O R A N D U M   O P I N I O N      the banner
                                             …and the writing begins

So the reader is a LANDMARK WALK, not a zone walk: each row is identified
by its own evidence and the caption is what is left between the landmarks.
The first row it cannot identify ends the claim, and a record whose first
content row is not a landmark is not this paper and gets NOTHING — which
is how the two Dallas records, whose page 1 is a docketing statement and a
motion for extension of time, are declined.

HOW THIS COURT NAMES ITS AUTHOR — the registry said `byline=none`, and
that is wrong. texapp names its author FOUR ways, and three of them are
readable:

    ANNOUNCED, title first   'Memorandum Opinion by Justice Fonseca'
                             (13th; 8 records) — a heading, so
                             `opinion_by_headings=True`
    ANNOUNCED, name first    'Opinion by:  Adrian A. Spears II, Justice'
                             (4th; 2 records) — the label carries a colon
                             and core's `_opinion_by` cannot see past it,
                             so the reader claims the row and hands the
                             name back in `announced_author`
    SIGNED, prose            '________ / Maggie Ellis, Justice' over a
                             signature rule (3rd) — an ordinary prose
                             byline once `allow_titlecase_name` is on
    SIGNED, stacked caps     'W. BRUCE WILLIAMS' / 'JUSTICE' on two rows
                             (11th; 9 records) — NO single-row grammar can
                             parse this and the reader does not pretend to;
                             those majorities stay unauthored and that is
                             reported, not hidden.

The 1st district's papers are PER CURIAM and core already types them so.

WHAT THE READER DOES NOT TOUCH. The announcement row of the 13th district
parses as a byline on its own, so the reader stops above it and lets the
writing own it. 'Do not publish. See TEX. R. APP. P. 47.2(b).' is printed
at the foot of the LAST page, inside the writing — the reader reads the
publication status off it and claims nothing, exactly as tex reads its
release trailer.

texapp prints NO appearance of counsel anywhere in the corpus.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES

STYLE = "centered stack"

# ---- the profile ---------------------------------------------------------
# THE REGISTRY SAID `none`. It is not none: see the module docstring. A
# PROSE grammar with the court's own bench word takes all three readable
# forms — 'Memorandum Opinion by Justice Fonseca' (heading),
# 'Maggie Ellis, Justice' (signature) — and `allow_titlecase_name` is what
# admits the signature, because this court signs in title case. Measured
# over the corpus: no panel row, no roster row and no 'Judge Presiding'
# row in any of the seven templates parses as a byline under it.
_TEXAPP = CourtProfile(
    "texapp", "Texas Court of Appeals",
    byline=BylineGrammar(style="prose",
                         titles=("Justice", "Chief Justice"),
                         opinion_by_headings=True,
                         allow_titlecase_name=True),
)
PROFILES[_TEXAPP.court_id] = _TEXAPP
_PARSER = BylineParser(_TEXAPP.byline)

# ---- texapp's declared facts (measured over the 30-record corpus) --------
# A ROW IS ON THE PAGE AXIS within this much of the page's centre. The
# 13th's two-column caption rows land within a point of the axis too, which
# is why the axis is never asked to name a zone here — only to tell a
# centred landmark from body prose.
_AXIS_TOL = 8.0
# A FENCE IS A ROW OF ONE GLYPH REPEATED, centred: ten '_' in the 11th,
# twelve '—' in the 1st, twenty-seven '_' in the 2nd, sixty in the 13th.
_FENCE_MIN_GLYPHS = 5
# HOW FAR THE BLOCK MAY RUN. Every record's whole headmatter is on page 1.
_MAX_PAGES = 1

# THE DOCKET. 'No. 11-26-00023-CR' / 'NO.  03-25-00606-CV' /
# 'NUMBER 13-25-00287-CR' / 'Nos. 04-25-00282-CR, …, and 04-25-00288-CR'.
# The OPENER is a closed vocabulary and the TOKEN is this court's own
# fourteen-character docket; a row that opens like a docket but numbers
# something else ('NO. D-1-GN-18-006562, THE HONORABLE AMY CLARK MEACHUM,
# JUDGE PRESIDING' — the 3rd district's trial-court line) is not one.
_DOCKET_ROW = re.compile(r"^(?:Nos?|NOS?|Numbers?|NUMBERS?)\.?\s+(.+?)\.?$")
_DOCKET = re.compile(r"^\d{2}-\d{2}-\d{5}-[A-Z]{2}$")
# THE RELEASE STAMP, at the rail above the masthead: 'Opinion filed July
# 30, 2026' (11th) / 'Opinion issued July 23, 2026' (1st).
_STAMP = re.compile(
    r"^Opinions?\s+(?:filed|issued|delivered)\s*:?\s*(.+?)\.?$", re.I)
# THE HANDED-DOWN LINE, at the rail below the roster (4th, 3rd):
# 'Delivered and Filed: July 22, 2026' / 'Filed:   July 17, 2026'.
_FILED = re.compile(
    r"^(?:Delivered\s+and\s+Filed|Delivered|Filed|Opinion\s+Delivered)"
    r"\s*:\s*(.+?)\.?$", re.I)
# THE MASTHEAD names the district. Fifteen courts, and each names itself
# with 'Court of Appeals' or with '<ordinal> District of Texas'; 'In The'
# and 'For The' are the connectives that stack it.
_MAST_WORDS = ("COURTOFAPPEALS", "DISTRICTOFTEXAS")
_MAST_JOIN = ("INTHE", "FORTHE", "OFTEXAS")
# THE ORIGIN OPENS on a closed vocabulary of the ways a court names where
# the case came from, and RUNS to the next landmark. Nothing here is a
# court NAME or a county NAME — those are read as the run's continuation.
_ORIGIN_OPEN = re.compile(
    r"^(?:On\s+Appeal\s+from|From\s+the|On\s+Petition\s+for|"
    r"On\s+Motion\s+for|On\s+Remand|On\s+Abatement|On\s+Review|"
    r"Original\b.*\bProceeding|Appeal\s+from)\b", re.I)
# THE TRIAL COURT'S OWN NUMBER, inside the origin run.
_TC_NUMBER = re.compile(
    r"^Trial\s+Court\s+(?:Cause\s+)?(?:Case\s+)?Nos?\.\s*(.+?)\.?$", re.I)
# THE PANEL. 'Before Justices Silva, Peña, and Fonseca' / 'Before Chief
# Justice Tijerina and Justices West and Cron' / 'Before Kerr, Bassel, and
# Walker, JJ.' / 'Sitting:  Rebeca C. Martinez, Chief Justice' / 'Panel
# consists of: Bailey, C.J.,'. A closed vocabulary of BENCH openers.
_PANEL = re.compile(r"^(?:Before\b|Sitting\s*:|Panel\s+consists\s+of\b)",
                    re.I)
# THE ANNOUNCEMENT the reader CLAIMS: the 4th district's label carries a
# colon and the name precedes the title, which core's heading parser
# cannot see. The 13th's ('Memorandum Opinion by Justice Cron') parses on
# its own and is deliberately NOT matched here — the writing owns it.
_ANNOUNCE = re.compile(
    r"^(?:\w+\s+)*Opinions?\s+by\s*(:)?\s*(.+?)\.?$", re.I)
# THE ANNOUNCEMENT THE WRITING OWNS. Without the colon the row parses as a
# byline on its own ('Memorandum Opinion by Justice Cron'), and the 2nd
# district's 'Per Curiam Memorandum Opinion' types the paper per curiam —
# so any TITLE-CASE row that ends on the word 'Opinion' ends the reader.
_ANN_OWNED = re.compile(r"\bOpinion$")
# THE TRIAL JUDGE, inside the origin run: 'Honorable M. Patrick Maguire,
# Judge Presiding' — a closed BENCH vocabulary, never a name test.
_TRIAL_JUDGE = re.compile(
    r"^(?:The\s+)?Honorable\s+(.+?),?\s+Judge\s+Presiding\.?$", re.I)
# WHAT THE COURT DID, stated in the headmatter (4th district, at the rail,
# all caps). A closed vocabulary of dispositions; a row of these words and
# nothing else.
_DISPO_WORDS = {
    "AFFIRMED", "REVERSED", "REMANDED", "RENDERED", "DISMISSED", "VACATED",
    "MODIFIED", "GRANTED", "DENIED", "IN", "PART", "AND", "AS", "WITHOUT",
    "PREJUDICE", "MOTION", "TO", "DISMISS", "APPEAL", "WRIT", "OF",
    "MANDAMUS", "CONDITIONALLY", "ABATED", "REFORMED", "SET", "ASIDE",
    "PETITION", "FOR", "THE", "IS", "COURT", "OPINION", "WITHDRAWN",
}
# THE BANNER: what the paper calls itself, letterspaced or not. Squashed
# of all spaces, it is one of these; nothing is matched loosely.
_BANNERS = {
    "OPINION", "MEMORANDUMOPINION", "SUBSTITUTEMEMORANDUMOPINION",
    "SUBSTITUTEOPINION", "CORRECTEDMEMORANDUMOPINION", "AMENDEDOPINION",
    "AMENDEDMEMORANDUMOPINION", "OPINIONONREHEARING",
    "MEMORANDUMOPINIONONREHEARING", "CONCURRINGOPINION",
    "DISSENTINGOPINION", "PERCURIAMOPINION", "OPINIONANDORDER",
    "ORDER", "MEMORANDUMOPINIONANDJUDGMENT", "OPINIONANDJUDGMENT",
    "SUPPLEMENTALMEMORANDUMOPINION", "SUPPLEMENTALOPINION",
    "OPINIONONREMAND", "MEMORANDUMOPINIONONREMAND",
}
# 'Do not publish.  See TEX. R. APP. P. 47.2(b).' — printed at the foot of
# the last page, INSIDE the writing. Read, never claimed.
_NOPUB = re.compile(r"^Do\s+not\s+publish\b", re.I)
# THE PIVOT, on its own row: 'V.' in the 11th and 1st, 'v.' everywhere else.
_PIVOT = re.compile(r"^v\.?$", re.I)
# A PARTY STATUS is a closed role vocabulary and names no party.
_STATUS = re.compile(
    r"^(?:Appellants?|Appellees?|Relators?|Respondents?|Petitioners?|"
    r"Cross-Appellants?|Cross-Appellees?|Real\s+Party\s+in\s+Interest|"
    r"Intervenors?)[,.]?$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squash(text: str) -> str:
    """The row's letters and digits, upper-cased, with everything else
    dropped — which is how a letterspaced banner
    ('M E M O R A N D U M   O P I N I O N') and a plain one
    ('MEMORANDUM OPINION') read as the same landmark."""
    return "".join(c for c in text.upper() if c.isalnum())


# --------------------------------------------------------------------------
# the visual row
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline. The
    13th district sets its caption in two columns and pdfio reports the
    party and its status as two pieces of one row; joining them here is
    what keeps the status beside the party it labels."""

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
        self.text = _norm("  ".join(p.plain.strip() for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def glyphs(self) -> list:
        return [c.get("text") or "" for p in self.pieces for c in p.chars
                if (c.get("text") or "").strip()]

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder) -> list:
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        buckets: dict = {}
        loose: list = []
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
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
        rows.extend(_Row(g) for g in groups)
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _on_axis(row: _Row, page_width: float) -> bool:
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


def _is_fence(row: _Row, page_width: float) -> bool:
    glyphs = row.glyphs
    if len(glyphs) < _FENCE_MIN_GLYPHS or len(set(glyphs)) != 1:
        return False
    if glyphs[0].isalnum():
        return False
    return _on_axis(row, page_width)


def _dockets(text: str) -> list:
    mm = _DOCKET_ROW.match(_norm(text))
    if not mm:
        return []
    parts = [p.strip() for p in re.split(r"[,;&]|\band\b", mm.group(1))
             if p.strip()]
    return parts if parts and all(_DOCKET.match(p) for p in parts) else []


def _docket_tail(text: str) -> list:
    """A docket list that WRAPS: the 4th district carries seven of them
    onto a second row with no opener."""
    parts = [p.strip() for p in re.split(r"[,;&]|\band\b", _norm(text))
             if p.strip()]
    return parts if parts and all(_DOCKET.match(p) for p in parts) else []


def _is_masthead(text: str) -> bool:
    sq = _squash(text)
    return sq in _MAST_JOIN or any(w in sq for w in _MAST_WORDS)


def _is_banner(text: str) -> bool:
    return _squash(text) in _BANNERS


def _is_dispo(text: str) -> bool:
    words = [w for w in re.split(r"[^A-Za-z]+", text) if w]
    return bool(words) and all(w.upper() in _DISPO_WORDS and w.isupper()
                               for w in words)


def _nopub(model) -> str | None:
    """'Do not publish.' at the foot of the last page — inside the writing,
    so it is read and never claimed."""
    for pm in reversed(model.pages):
        for line in pm.lines:
            if _NOPUB.match(_norm(line.plain)):
                return "Do not publish"
    return None


def _case_name(rows: list) -> tuple:
    """(parties, case_name) from the caption rows, built from the party
    names either side of the pivot — never by joining the caption
    wholesale. A STATUS names no party."""
    left: list = []
    right: list = []
    side = left
    for text in rows:
        flat = _norm(text)
        if side is left and _PIVOT.match(flat):
            side = right
            continue
        parts = [p for p in re.split(r"\s{2,}", flat) if p.strip()]
        for part in parts:
            if _STATUS.match(part.strip()):
                continue
            side.append(part.strip())
    lhs = _norm(" ".join(left)).rstrip(",; ")
    rhs = _norm(" ".join(right)).rstrip(",; ")
    if lhs and rhs:
        return [lhs, rhs], f"{lhs} v. {rhs}"
    return ([lhs], lhs) if lhs else ([], None)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom):
        self.model = model
        self.pages = {pm.number: pm for pm in model.pages}
        self.body_x0 = geom.body_x0 if geom else 72.0
        self.right_x1 = geom.right_x1 if geom else 540.0
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str) -> None:
        pm = self.pages[row.page]
        align = "C" if _on_axis(row, pm.width) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span="center"))
        self.consumed.update(row.ids)

    def result(self, announced=None):
        out = {"criteria": self.crit, "items": self.items, "attorneys": [],
               "dropped": self.dropped, "consumed": self.consumed,
               "anchor_ids": [], "doc_type_final": None}
        if announced:
            out["announced_author"] = announced
        return out


def _is_body(ctx: _Ctx, row: _Row, page_width: float) -> bool:
    """BODY PROSE: ONE piece, set at the rail or the paragraph indent, and
    running the full measure.

    THE AXIS CANNOT BE ASKED THIS QUESTION. A justified block at the rail
    is centred on the page axis to a tenth of a point, so an axis test
    calls every body row a centred landmark. What tells them apart is the
    PIECE COUNT: the 13th district's caption sets the party at the rail and
    its status flush right, which pdfio reports as two pieces of one row
    with a 190pt gutter between them, and prose is never set that way.

    NOR IS THE MEASURE ENOUGH ON ITS OWN. A long caption row and a long
    trial-court line both run the full measure at the rail — the 11th's
    'INDEPENDENT EXECUTOR OF THE ESTATE OF CHARLES' and the 3rd's 'NO.
    D-1-GN-18-006562, THE HONORABLE AMY CLARK MEACHUM, JUDGE PRESIDING' —
    and taking either for prose broke the claim mid-caption and left the
    trial-court line to open a second, phantom writing. Six of the seven
    templates set the whole block BOLD and the body roman, and every one of
    them sets those long rows in CAPITALS, so prose is the row that is
    neither: unbolded, and carrying at least one lower-case letter.
    """
    if len(row.pieces) > 1 or row.bold:
        return False
    if not any(c.islower() for c in row.text):
        return False
    return (row.x0 >= ctx.body_x0 - 1.0
            and row.x1 >= ctx.right_x1 - 14.0)


@decider("headmatter.read", court="texapp")
def read_headmatter_texapp(model, geom, **_):
    """Read texapp's centered stack, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    pw = page1.width
    finder = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 12.0)
    rows = [r for r in _visual_rows(model, finder) if r.page == 1]
    if not rows:
        return NOTHING

    ctx = _Ctx(model, geom)
    mast: list = []
    caption: list = []
    origin: list = []
    dockets: list = []
    announced = None
    prev = ""                      # the role given to the row above
    seat = False                   # the masthead's one unlabelled seat row
    started = False                # a landmark has identified the head
    seen_origin = False
    seen_banner = False

    for row in rows:
        text = _norm(row.text)
        # --- the fences, in any state ---
        if _is_fence(row, pw):
            ctx.rule(row)
            prev = "rule"
            continue
        # --- the release stamp, at the rail above the masthead ---
        if not started:
            mm = _STAMP.match(text)
            if mm:
                ctx.crit.setdefault("decision_date", _norm(mm.group(1)))
                ctx.emit(row, "date")
                prev = "date"
                continue
        # --- the docket ---
        found = _dockets(text)
        if found:
            dockets.extend(found)
            ctx.emit(row, "docket")
            prev = "docket"
            started = True
            continue
        if prev == "docket" and not seen_origin:
            tail = _docket_tail(text)
            if tail:
                dockets.extend(tail)
                ctx.emit(row, "docket")
                continue
        # --- the banner ---
        if _is_banner(text):
            ctx.crit.setdefault("title", _norm(text))
            ctx.emit(row, "title")
            prev = "title"
            started = True
            seen_banner = True
            continue
        # --- the masthead, and its own continuation ---
        # ON THE AXIS, always. Dallas staples an e-filed motion in front of
        # the paper and its caption's right column reads 'IN THE COURT OF
        # APPEALS' — the court's own name, in the middle of a two-column
        # caption row that is 13pt off the axis. The axis takes it out.
        if _is_masthead(text) and _on_axis(row, pw):
            mast.append(text)
            ctx.emit(row, "banner")
            prev = "banner"
            started = True
            continue
        # THE SEAT, and it is ONE ROW. Four of the seven templates print
        # where the court sits under its name — 'at Fort Worth',
        # 'San Antonio, Texas', 'CORPUS CHRISTI – EDINBURG' — and a place
        # name cannot be read from a vocabulary, so it is taken by
        # adjacency instead. UNBOUNDED, that adjacency ran the masthead
        # through the whole caption and the whole origin of every 13th
        # district record: nine rows came out `banner` and the claim was
        # withdrawn for having no caption. The court prints one seat row.
        if prev == "banner" and not seat and _on_axis(row, pw):
            seat = True
            mast.append(text)
            ctx.emit(row, "banner")
            continue
        # --- nothing has identified the head of the page: not this paper ---
        if not started:
            return NOTHING
        # --- the announcement, and the one the WRITING owns ---
        mm = _ANNOUNCE.match(text)
        if mm:
            # THE COURT ANNOUNCES, IT DOES NOT SIGN — and core cannot use
            # the announcement where it stands: measured with the reader
            # popped, all 10 of the announcing records came back with an
            # unauthored majority. So the reader claims the row and hands
            # the name back, exactly as va does. WHICH FORM parses is the
            # court's business, not core's: 'Memorandum Opinion by Justice
            # Cron' parses whole, while the 4th district's label carries a
            # colon and only its TAIL parses ('Adrian A. Spears II,
            # Justice'). The reader hands back whichever the court's own
            # grammar reads.
            whole = _PARSER.parse(text)
            announced = text if whole is not None else _norm(mm.group(2))
            ctx.emit(row, "author")
            prev = "author"
            continue
        if _ANN_OWNED.search(text) and any(c.islower() for c in text):
            break
        # --- the origin, which OPENS on a vocabulary and RUNS ---
        if _ORIGIN_OPEN.match(text):
            seen_origin = True
            origin.append(text)
            ctx.emit(row, "lower-court")
            prev = "lower-court"
            continue
        mm = _TC_NUMBER.match(text)
        if mm:
            seen_origin = True
            ctx.crit.setdefault("lower_court_docket", _norm(mm.group(1)))
            ctx.emit(row, "lower-court")
            prev = "lower-court"
            continue
        mm = _TRIAL_JUDGE.match(text)
        if mm and seen_origin:
            ctx.crit.setdefault("lower_court_judge", _norm(mm.group(1)))
            ctx.emit(row, "lower-court")
            prev = "lower-court"
            continue
        # --- the bench, and its own roster continuation ---
        if _PANEL.match(text):
            ctx.crit.setdefault("panel_line", text)
            ctx.emit(row, "panel")
            prev = "panel"
            continue
        if prev == "panel" and not _is_body(ctx, row, pw) \
                and row.x0 > ctx.body_x0 + 2.0:
            ctx.emit(row, "panel")
            continue
        # --- the day it was handed down ---
        mm = _FILED.match(text)
        if mm:
            ctx.crit["decision_date"] = _norm(mm.group(1))
            ctx.emit(row, "date")
            prev = "date"
            continue
        # --- what the court did ---
        if (seen_banner or seen_origin) and _is_dispo(text):
            ctx.crit.setdefault("disposition", text)
            ctx.emit(row, "disposition")
            prev = "disposition"
            continue
        # --- THE ORIGIN RUN'S OWN CONTINUATION, tried LAST. The court below
        # is named on rows this reader must not read by wording ('Eastland
        # County, Texas', 'County Court at Law of Hood County, Texas'), so
        # the run carries them — but only after every other landmark has
        # been offered the row. Tried first, the run swallowed the 4th
        # district's whole trailing block: its announcement, its roster,
        # its filing date and its disposition all came out `lower-court`.
        if prev == "lower-court" and not _is_body(ctx, row, pw):
            origin.append(text)
            ctx.emit(row, "lower-court")
            continue
        # --- the caption is what is left between the landmarks ---
        # AFTER THE MASTHEAD, never before it. Every one of the seven
        # templates prints the district's name above the parties; a record
        # whose parties stand above any masthead is a stapled filing, not
        # this court's paper.
        if mast and not (seen_origin or _is_body(ctx, row, pw)):
            caption.append(text)
            ctx.emit(row, "caption")
            prev = "caption"
            continue
        # --- the first row no landmark identifies ends the claim ---
        break

    if not (dockets and caption and mast):
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE
    ctx.crit["court"] = _norm(" ".join(mast))
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    parties, name = _case_name(caption)
    if parties:
        ctx.crit["parties"] = parties
    if name:
        ctx.crit["case_name"] = name
    if origin:
        ctx.crit["lower_court"] = _norm(" ".join(origin))
    nopub = _nopub(model)
    if nopub:
        ctx.crit["publication_status"] = nopub
    return ctx.result(announced)


# --------------------------------------------------------------------------
# image.role — the seal on the masthead
# --------------------------------------------------------------------------
# THE COURT PRINTS ITS SEAL ON THE MASTHEAD, and 27 of the 30 records carry
# it: one graphic on page 1, square, on the page axis, above the type. The
# whole class, measured:
#
#     size      69-91pt, and square to within a point (76x76, 71x71, 91x91)
#     centre    305.6-308.1 against the 306.0 axis of a 612pt sheet
#     top       72.0-96.1 of 792 — a frac of 0.0909 to 0.1214
#
# CORE'S SEAL TEST IS BOUNDED AT 0.08 OF THE HEIGHT, and every one of these
# is past it — the same margin that put mo's seal inside its writing. Here
# it split the court down the middle: 14 records sent the seal to the head
# of the headmatter and 14 CROPPED AND PLANTED IT IN THE OPINION, as though
# this court had printed an exhibit. And the split is not geometric, so no
# tightening of a frac would fix it: `top=85.8` goes to the headmatter on
# horacio_almendariz and into the body on ameripol_synpol, one point apart
# (the user, 2026-08-20: 'tex app needs to pull the logo seal').
#
# So the court answers for its own stationery. A square graphic on the axis
# above the type, on page 1, is the seal — there is no other graphic like it
# in the corpus, and this court prints no figures at all: the only records
# with a second image are the two the reader already declines, where the
# 5th District staples an e-filed form in front of the paper.
_SEAL_SPAN = (60.0, 100.0)      # the measured 69-91, with a point either way
_SEAL_SQUARE = 0.08             # 71x71 and 70x69 — square, not merely boxy
_SEAL_AXIS_TOL = 6.0            # measured 2.1 off the axis at worst
_SEAL_BAND = 0.15               # measured 0.1214 at the lowest


@decider("image.role", court="texapp")
def image_role_texapp(page=None, image=None, **_):
    """The masthead seal. Every other graphic is left to core."""
    if page is None or image is None or page.number != 1:
        return NOTHING
    w, h = image.x1 - image.x0, image.bottom - image.top
    if not (_SEAL_SPAN[0] <= w <= _SEAL_SPAN[1]
            and _SEAL_SPAN[0] <= h <= _SEAL_SPAN[1]):
        return NOTHING
    if abs(w - h) > _SEAL_SQUARE * max(w, h):
        return NOTHING
    if abs((image.x0 + image.x1) / 2 - page.width / 2) > _SEAL_AXIS_TOL:
        return NOTHING
    if image.top / page.height > _SEAL_BAND:
        return NOTHING
    return "seal"
