"""Arizona Court of Appeals ('arizctapp').

THE CONTRACT — one paper, printed 42 times out of 42: the DIVISIONAL SLIP.
It is the Supreme Court's engraved slip (see ariz.py) set by a two-division
intermediate court, and it differs from its parent in four measurable ways:
the masthead is THREE rows and names the division, the fence is twice as
wide and its measure names the division that drew it, the last fenced band
is opened by the paper's own NAME, and the byline is letter-spaced.

    NOTICE: NOT FOR OFFICIAL PUBLICATION.              8pt, 3 rows, and only
    UNDER ARIZONA RULE OF THE SUPREME COURT 111(c)…    on a memorandum
    AND MAY BE CITED ONLY AS AUTHORIZED BY RULE.       decision

    IN THE                                     the masthead, 12pt
    ARIZONA COURT OF APPEALS                   …its 18pt second row…
    DIVISION ONE                               …and the division, 12pt bold
    ────────────────                           a fence ON THE AXIS
    STATE OF ARIZONA, Petitioner,              the caption…
    v.                                         …its pivot…
    ENRIQUE AGUIRRE, Respondent.
    No. 1 CA-SA 26-0176                        …this court's docket…
    FILED 07-28-2026                           …and the release date
    ────────────────
    Petition for Special Action from the Superior Court in Maricopa County
    No.  CV 2026-000755                        the origin: where it came
    The Honorable Susanna C. Pineda, Judge     from, who tried it, its
    JURISDICTION ACCEPTED; RELIEF DENIED       number below, the judgment
    ────────────────
    COUNSEL                                    the appearances, labelled
    Arizona Attorney General's Office, Phoenix
    By Rebecca Banes, Edward F. Novak, Jennifer Rethemeier (argued)
    Co-Counsel for Petitioner
    ────────────────
    OPINION                                    THE PAPER'S OWN NAME…
    Judge D. Andrew Gaona delivered the opinion of the Court, in which
    Presiding Judge David B. Gass1 and Judge Anni Hill Foster joined.
    ────────────────
    G A O N A, Judge:                          …and the writing starts

THE FENCE MEASURE NAMES THE DIVISION. 210 fences over the corpus: 187.9pt
on the 31 Division One records (two of them draw one at 187.8) and 180.0pt
on the 11 Division Two records, every one centred on the page axis to
within a point. The court's own footnote separator is 144pt AT THE BODY
RAIL — told apart by where it STARTS, exactly as in ariz.

THE LAST BAND IS FOUND BY THE PAPER'S NAME, NOT BY A VERB. ariz reads its
closing band off the joining summary's landmark ('authored the Opinion of
the Court'); this court writes that sentence six different ways ('delivered
the opinion of the Court', 'authored…', 'issued…', "delivered the Court's
decision in which"), and prints instead a bold centred row naming the paper
— OPINION on the 32 published slips, MEMORANDUM DECISION on the 10
unpublished ones (the same 10 that head the page with the NOTICE), and on
nothing else in the block. That row is both the band's landmark and the
document's publication status; the summary verb is kept only as a fallback
for a record that omits it.

THE CAPTION MAY CARRY ITS OWN DIVIDER. A probate slip recites the estate,
rules a row of typed underscores under it, and then names the parties
(dineen_shibata). The rule is a caption row and renders as one, and it
RESETS the party side — without that the estate's decedent reads as the
first plaintiff.

A record that does not name the court in its first rows, or that draws
fewer than three axis fences on page 1, is not this paper and gets NOTHING.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, furniture_key
from ..resolve.evidence import NOTHING, decider

STYLE_SLIP = "divisional slip"

# ---- arizctapp's declared facts (measured over all 42 records) -----------
# THE FENCE. 210 fences over the corpus: 187.9pt on Division One (153),
# 180.0pt on Division Two (55), and 187.8pt on two rules of the odd Division
# One variant. Every one of them is centred on the page axis to within a
# point.
_FENCE_MEASURE = (172.0, 196.0)
_FENCE_AXIS = 18.0
# The FOOTNOTE separator is the same court's other rule and is told apart by
# where it STARTS, not by its width: 144pt at the BODY RAIL (x0=108) where a
# fence starts at x0=212 (Div One) or x0=216 (Div Two).
_SEP_MIN = 100.0
_SEP_RAIL = 4.0
# THE MASTHEAD: 18pt over a 12pt body — the only row on page 1 above 15pt.
_MASTHEAD_SIZE = 15.0
# HOW FAR THE BLOCK MAY RUN. The longest headmatter in the corpus (m.k.,
# nine sets of counsel for six tribes) carries its closing band onto page 2;
# nothing needs a third.
_MAX_PAGES = 3
# A SUMMARY CONTINUES ON THE NEXT LINE: inside the joining summary the rows
# sit one leading apart (14.7-15.1pt on a 15pt lead), and the fence below it
# stands 27pt clear. 1.35x the lead separates a wrap from a new element.
_SUMMARY_WRAP = 1.35

_MASTHEAD_TOP = "in the"
_MASTHEAD = "arizona court of appeals"
_DIVISION = re.compile(r"^division\s+[a-z]+$", re.I)
# The caption's own divider, and the typed form of the footnote separator.
_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# 'No. 1 CA-SA 26-0176' / 'No. 2 CA-CV 2025-0219' / 'No. 1 CA-CV 25-0606 PB'
# — THIS court's own docket. Its shape is the ' CA-' infix, which the
# tribunals below never print ('CV2023-096192', 'S1300PO202480096',
# 'LC2018000461001DT'), so the two are never confused.
_DOCKET = re.compile(r"^(?:(?:Nos?\.|and)\s*)?\d\s*CA-[A-Z]{2}\s")
_CONSOLIDATED = re.compile(r"^\(?consolidated\)?\.?$", re.I)
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# Arizona labels its release date, and the two divisions spell it
# differently: Division One numbers it ('FILED 07-28-2026', and 'FILED
# 8-11-2026' when the month is one digit), Division Two writes it out
# ('Filed June 11, 2026'). One fact, printed twice; recorded once.
_FILED_WORDS = re.compile(r"^Filed\s+([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})\.?$",
                          re.I)
_FILED_DIGITS = re.compile(r"^Filed\s+(\d{1,2})-(\d{1,2})-(\d{4})\.?$", re.I)
# The appearances are labelled, once, in the band that holds them. A slip
# with a self-represented party labels them APPEARANCES instead.
_COUNSEL_LABEL = re.compile(r"^(?:COUNSEL|APPEARANCES)\s*:?$")
# THE PAPER'S OWN NAME — a closed vocabulary, because it is the court's own
# word for what it issued and not a case's wording. Bold, centred, and the
# only such row below the counsel band.
_PAPER_NAMES = frozenset((
    "OPINION", "MEMORANDUM DECISION", "DECISION", "DECISION ORDER",
    "OPINION AND ORDER", "MEMORANDUM DECISION AND ORDER",
    "SUPPLEMENTAL OPINION", "AMENDED OPINION",
    "AMENDED MEMORANDUM DECISION", "ORDER",
))
_UNPUBLISHED = ("MEMORANDUM DECISION", "AMENDED MEMORANDUM DECISION",
                "MEMORANDUM DECISION AND ORDER")
# The joining summary's fallback landmark, in the six forms the court writes
# it. Used only where the paper did not name itself.
_SUMMARY = re.compile(
    r"\b(?:opinion|decision)\s+of\s+the\s+court\b"
    r"|\bcourt[’']s\s+(?:opinion|decision)\b", re.I)
# Who tried it, as the origin band says.
_HONORABLE = re.compile(r"^The Honorable\b", re.I)
# The number the court BELOW gave the case, labelled bare or labelled by the
# tribunal that assigned it ('Cochise County Cause No. S0200CV202600232').
_LOWER_DOCKET = re.compile(r"^(?:[A-Za-z. ]{0,26})?Nos?\.\s*\S", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Arizona stacks its roles with a slash ('Plaintiff/Appellant/
# Cross-Appellee') and spells the self-represented role out in full.
_STATUS_WORDS = frozenset((
    "appellant", "appellee", "petitioner", "respondent", "plaintiff",
    "defendant", "intervenor", "intervenors", "movant", "amicus", "amici",
    "applicant", "claimant", "complainant", "employee", "employer",
    "carrier", "judge", "real", "party", "in", "interest", "cross", "and",
    "the", "et", "al", "counter", "counterclaimant", "counterdefendant",
    "third", "garnishee", "creditor", "debtor", "conservator", "ward",
    "parties", "intervention", "propria", "persona", "adult", "an", "a",
    "curiae", "deceased", "minor", "father", "mother", "pro", "se",
    "guardian", "personal", "representative", "trustee", "estate", "of",
    "by", "through", "his", "her", "next", "friend", "state", "or",
))
# THE BENCH TITLES this court prints in its joining summary, longest first.
_PANEL_TITLES = ("Acting Vice Chief Judge", "Acting Presiding Judge",
                 "Acting Chief Judge", "Vice Chief Judge", "Chief Judge",
                 "Presiding Judge", "Judges", "Judge")
# Words that close a name run inside the summary. A judge's name is a run of
# capitalised tokens; the sentence's own words are lower-case, so the run
# ends on the first of them.
_PANEL_STOP = frozenset(("and", "in", "which", "joined", "concurred",
                         "dissented", "filed", "specially", "from", "a",
                         "the", "of", "delivered", "authored", "issued",
                         "wrote", "part", "result", "opinion", "decision",
                         "also", "concurring", "dissenting"))
# arizctapp signs name-first and LETTER-SPACED ('M O R S E, Judge:' /
# 'V Á S Q U E Z, Presiding Judge:'); core folds the spaced run before
# parsing. Both the lead byline and the separate writings take this form,
# so the walk stops no later than assembly's byline does.
#
# NOTE (reported, not applied): the profile in courts/__init__.py declares
# titles=('Judge', 'Presiding Judge', 'Chief Judge') and omits 'Vice Chief
# Judge', which three records sign with; and core's spaced-run fold in
# resolve/bylines.py is ASCII-only, so 'V Á S Q U E Z' and 'O’ N E I L' do
# not fold. The grammar below is the one this reader assumes.
_BYLINE = BylineGrammar(style="prose",
                        titles=("Judge", "Presiding Judge", "Chief Judge",
                                "Vice Chief Judge"))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _tight(text: str) -> str:
    """A NUMBER'S OWN HYPHEN CARRIES NO SPACE — the same dead-space stack
    ariz found inside its dockets."""
    return re.sub(r"\s*-\s*", "-", _norm(text))


def _is_masthead_top(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD_TOP


def _is_masthead(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD


def _is_division(text: str) -> bool:
    return bool(_DIVISION.match(_norm(text)))


def _is_rule_row(text: str) -> bool:
    return bool(_TYPED_RULE.match(_norm(text)))


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w for w in re.split(r"[\s/,-]+", bare) if w]
    return bool(words) and all(
        w.strip(".") in _STATUS_WORDS or w.strip(".").rstrip("s")
        in _STATUS_WORDS for w in words)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _paper_name(text: str, centred: bool) -> str | None:
    """The paper's own name, or None.

    IT IS THE VOCABULARY THAT DECIDES, NOT THE FACE. The row is bold on 40
    of the 42 records; the two that draw their fence at 187.8pt instead of
    187.9 set both this row AND their disposition in a face pdfio does not
    read as bold (gregorwicz, york), so a bold test loses the band on
    exactly the records whose typesetting is already the odd one. The name
    is a CLOSED vocabulary — the court's own word for what it issued, never
    a case's wording — and it is the only row in the block that can equal
    one, so the vocabulary alone is the test. The geometry kept is the one
    that always holds: the row is centred, never at the body rail.
    """
    if not centred:
        return None
    bare = _norm(text).rstrip(".:").upper()
    return bare if bare in _PAPER_NAMES else None


def _filed_value(text: str) -> str | None:
    """'FILED 07-28-2026' / 'Filed June 11, 2026' -> 'July 28, 2026'."""
    txt = _norm(text)
    mm = _FILED_WORDS.match(txt)
    if mm is not None and mm.group(1).lower().rstrip(".") in _MONTHS:
        month = mm.group(1)
        return f"{month[0].upper()}{month[1:].lower()} " \
               f"{int(mm.group(2))}, {mm.group(3)}"
    mm = _FILED_DIGITS.match(txt)
    if mm is not None and 1 <= int(mm.group(1)) <= 12:
        return (f"{_MONTHS[int(mm.group(1)) - 1].capitalize()} "
                f"{int(mm.group(2))}, {mm.group(3)}")
    return None


# --------------------------------------------------------------------------
# the page's own marks — fences, and the footnote separator that is not one
# --------------------------------------------------------------------------

def _fences(pm) -> list[float]:
    """The tops of the section fences this page draws, in page order."""
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        out.append(r.top)
    return sorted(out)


def _footnote_cut(pm, body_x0: float) -> float:
    """Where this page's footnotes begin — the top of the 144pt separator
    Arizona sets AT THE BODY RAIL. Everything below it is a note."""
    tops = [r.top for r in pm.h_rules
            if r.width >= _SEP_MIN and abs(r.x0 - body_x0) <= _SEP_RAIL]
    tops += [l.top for l in pm.lines
             if _is_rule_row(l.plain) and abs(l.x0 - body_x0) <= _SEP_RAIL
             and (l.x1 - l.x0) >= _SEP_MIN]
    return min(tops) if tops else float("inf")


def _head_keys(model, body_size: float) -> set[str]:
    """THE RUNNING HEAD THIS COURT PRINTS, learned on its own terms.

    Every page after the first carries a two-row head — the short case name
    over the name of the writing below it ('CERVANTES v. STATE' / 'Opinion
    of the Court'). Both rows are set at BODY SIZE, and the second one
    CHANGES with the writing, so on a record carrying separate opinions it
    prints on fewer than 40% of the pages and core's document-wide floor
    never learns it (cervantes: 5 of 32). It is furniture all the same: a
    row repeated in the top band of two or more pages, none of which is
    page 1. Only rows inside this reader's own region are dropped on it.
    """
    counts: dict[str, int] = {}
    for pm in model.pages:
        if pm.number == 1:
            continue
        seen: set[str] = set()
        for line in pm.lines:
            if line.top / pm.height > 0.12 or not line.plain.strip():
                continue
            key = furniture_key(line.plain.strip())
            if key and key not in seen:
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
    return {k for k, n in counts.items() if n >= 2}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="arizctapp")
def read_headmatter_arizctapp(model, geom, **_):
    """Read the Arizona Court of Appeals' divisional slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    lead = (geom.lead if geom and geom.lead else 15.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    head_keys = _head_keys(model, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS, in page order, with same-row pieces rejoined (ariz's guard:
    # a justified line split at its wide gap reads as two rows, and half a
    # summary row parses as a byline).
    rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
        cut = _footnote_cut(pm, body_x0)
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or line.top >= cut:
                continue
            if finder.kind(pm, line):
                continue
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        rows.extend(groups[k] for k in order)
    if len(rows) < 6:
        return NOTHING

    # THE NOTICE stands above the masthead, in 8pt on a 12pt body, and says
    # what the paper is not. It is the block's furniture: recorded as
    # Dropped, never rendered as headmatter.
    head = 0
    while head < len(rows) and not _is_masthead_top(rows[head][0].plain):
        head += 1
    notice_rows = rows[:head]
    notice = [l for g in notice_rows for l in g]
    if notice and any((l.size or body_size) > body_size - 2.0
                      for l in notice):
        return NOTHING                # something above the masthead we
                                      # cannot name; leave it to core
    rows = rows[head:]

    # THE DISPATCH: the court names itself in two rows over a page-1 stack
    # of axis fences. Nothing is matched against a case's own wording.
    if len(rows) < 6:
        return NOTHING
    if not (_is_masthead_top(rows[0][0].plain)
            and _is_masthead(rows[1][0].plain)
            and (rows[1][0].size or 0) >= _MASTHEAD_SIZE):
        return NOTHING
    if len(_fences(page1)) < 3:
        return NOTHING

    stream: list = []
    for group in rows:
        stream.append((group[0].page, group[0].top, "row", group))
    for pm in model.pages[:_MAX_PAGES]:
        for top in _fences(pm):
            stream.append((pm.number, top, "fence", None))
    stream.sort(key=lambda t: (t[0], t[1]))

    ctx = _Ctx(model, geom, pages, body_size)
    for group in notice_rows:
        ctx.drop(group, "notice")
    parser = BylineParser(_BYLINE)
    state = "court"
    caption: list[str] = []
    dockets: list[str] = []
    origin: list[str] = []
    counsel: list[str] = []
    summary: list[str] = []
    prev_bottom: float | None = None
    prev_page: int | None = None
    ended = False

    for page, top, kind, group in stream:
        if kind == "fence":
            if state == "summary":
                ctx.rule(page)
                ended = True          # the last band is closed; only the
                continue              # byline may follow
            ctx.rule(page)
            if state == "court":
                state = "caption"
            continue
        text = _norm(" ".join(l.plain for l in group))
        # A RUNNING HEAD INSIDE THE BLOCK. The closing band may fall on
        # page 2, and the head above it is this court's furniture wherever
        # it prints. Dropped, never placed — and it is also the last thing
        # that can stand between the closing fence and the byline.
        if page > 1 and furniture_key(text) in head_keys:
            ctx.drop(group, "running-head")
            continue
        if ended:
            break                     # a content row past the closing fence

        if state == "court":
            if (_is_masthead_top(text) or _is_masthead(text)
                    or _is_division(text)):
                if _is_masthead(text):
                    ctx.crit.setdefault("court", text)
                elif _is_division(text):
                    ctx.crit["court"] = _norm(
                        f"{ctx.crit.get('court', '')}, {text}").lstrip(", ")
                ctx.emit(group, "court")
                continue
            state = "caption"

        if state == "caption":
            if _DOCKET.match(_tight(text)) or _filed_value(text):
                state = "docket"
            else:
                caption.append(text)
                ctx.emit(group, "caption")
                continue

        if state == "docket":
            value = _filed_value(text)
            if value is not None:
                ctx.crit.setdefault("decision_date", value)
                ctx.emit(group, "date")
                continue
            if _DOCKET.match(_tight(text)) or _CONSOLIDATED.match(text):
                dockets.extend(_dockets(text))
                ctx.emit(group, "docket")
                continue
            state = "origin"

        if state == "origin":
            if _COUNSEL_LABEL.match(text):
                state = "counsel"
                ctx.emit(group, "counsel")
                continue
            if _paper_name(text, group[0].x0 > body_x0 + 12.0):
                state = "title"
            else:
                origin.append(text)
                ctx.emit(group, "lower-court")
                continue

        if state == "counsel":
            if _paper_name(text, group[0].x0 > body_x0 + 12.0):
                state = "title"
            elif _SUMMARY.search(text):
                state = "summary"
            elif parser.parse(text) is not None:
                break                 # a byline always ends the reader
            else:
                counsel.append(text)
                ctx.emit(group, "counsel")
                prev_bottom, prev_page = group[0].top, page
                continue

        if state == "title":
            name = _paper_name(text, True) or ""
            ctx.crit["title"] = name
            ctx.crit.setdefault(
                "publication_status",
                "unpublished" if name in _UNPUBLISHED else "published")
            ctx.emit(group, "title", anchor=True)
            prev_bottom, prev_page = group[0].top, page
            state = "summary"
            continue

        if state == "summary":
            # A SUMMARY ROW IS A WRAP OF THE ONE ABOVE IT, bounded by the
            # page's own leading — so a byline lookalike inside the summary
            # stays in the summary, and the fence below it ends the band.
            if summary and (prev_page != page
                            or top - prev_bottom > _SUMMARY_WRAP * lead):
                ended = True
                continue
            summary.append(text)
            ctx.emit(group, "summary" if summary[1:] else "panel")
            prev_bottom, prev_page = group[0].top, page
            continue
        prev_bottom, prev_page = group[0].top, page

    if not dockets or not (summary or counsel):
        return NOTHING                # not the paper this contract names

    ctx.crit["headmatter_style"] = STYLE_SLIP
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)
    _origin(ctx, origin)
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    if summary:
        line = _norm(" ".join(summary))
        ctx.crit["panel_line"] = line
        panel = _panel(line)
        if panel:
            ctx.crit["panel"] = panel
    return ctx.result()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.anchor_ids: list[int] = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, anchor: bool = False):
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        pm = self.pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        align = line_alignment(first, pm.width, self.geom,
                               banner_center_min_size=self.body_size + 2.0)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)
        if anchor:
            self.anchor_ids.extend(p.id for p in parts)

    def drop(self, group: list, kind: str):
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts)),
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int):
        # A FENCE RENDERS WHERE THE PAGE DRAWS IT. Core re-sorts the block
        # by the source position of each item's provenance, so a rule
        # carrying none sorts to the end; it takes the prov of the row it
        # stands under and stays put.
        prev = next((i for i in reversed(self.items)
                     if isinstance(i, m.HmLine)), None)
        self.items.append(m.Rule(
            prov=prev.prov if prev is not None else m.Prov(page),
            span="center"))

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor_ids, "doc_type_final": None}


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _dockets(text: str) -> list[str]:
    """The docket band names one case or several. A consolidated slip lists
    them across two rows ('Nos. 2 CA-JV 2025-0038, 2 CA-JV 2025-0039,' /
    'and 2 CA-JV 2025-0040 (Consolidated)'), so each row yields every
    number it carries rather than one."""
    body = re.sub(r"^(?:Nos?\.|and)\s*", "", _tight(text), flags=re.I)
    body = re.sub(r"\(consolidated\)\.?$", "", body, flags=re.I).strip()
    out = [p.strip(" .") for p in re.split(r",|\s+and\s+", body)]
    return [p for p in out if p]


def _trim(row: str) -> str:
    """Drop the caption's own punctuation without docking an abbreviation.

    A NAME'S OWN PERIOD IS PART OF IT. Trailing commas and semicolons are
    the caption's, but the final stop belongs to the party on five records
    ('IN RE DEPENDENCY AS TO A.G.', 'JUDICIAL WATCH, INC.', 'KIMMINAU LAW
    FIRM, P.C.', '…FRIEDLANDER, P.A.'). The difference is the letter before
    it: an abbreviation's is a CAPITAL, a sentence's is not.
    """
    row = row.rstrip(" ,;")
    while row.endswith(".") and len(row) > 1 and not row[-2].isupper():
        row = row[:-1].rstrip(" ,;")
    return row


def _strip_status(row: str) -> str:
    """A party and its role share a row on this court's slips ('STATE OF
    ARIZONA, Petitioner,'). The role is a closed vocabulary and the name is
    never read by wording, so the trailing comma-clauses are tested one at
    a time and dropped only while they are roles."""
    row = _trim(row)
    while True:
        cut = row.rfind(",")
        if cut < 0:
            return row
        if not _is_status(row[cut + 1:]):
            return row
        row = _trim(row[:cut])


def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        row = row.rstrip("*†‡∗⁎ ")
        if _is_rule_row(row):
            # THE CAPTION'S OWN DIVIDER closes the recital above it: the
            # estate's decedent is not the first plaintiff.
            del side[:]
            continue
        if _is_pivot(row):
            if seen_pivot:
                break                 # a consolidated slip: the LEAD case
            side = right
            seen_pivot = True
            continue
        if row.rstrip().endswith(":"):
            continue                  # 'In re the Matter of:' — a lead-in
        if _norm(row).rstrip(",.").lower() == "and":
            if side:
                side.append("and")
            continue
        if _is_status(row):
            continue
        bare = _strip_status(row)
        if bare:
            side.append(bare)
    while left and left[-1] == "and":
        left.pop()
    while right and right[-1] == "and":
        right.pop()
    if seen_pivot and left and right:
        one, two = (_norm(" ".join(left)).rstrip(", "),
                    _norm(" ".join(right)).rstrip(", "))
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _norm(" ".join(left + right)).rstrip(", ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


def _origin(ctx: _Ctx, rows: list) -> None:
    """The origin band: where the case came from, who tried it, its number
    below, and this Court's disposition.

    Two rows may be one statement — the court sets its disposition to the
    measure and lets it wrap ('AFFIRMED IN PART;' / 'VACATED IN PART AND
    REMANDED'; 'REVIEW GRANTED; RELIEF GRANTED IN PART AND DENIED IN' /
    'PART') — so consecutive rows of the same kind are joined before
    anything is read out of them."""
    def is_caps(row: str) -> bool:
        # A DISPOSITION IS ALL WORDS: the judgment is set in bold caps and
        # the numbers in roman, so a caps row carrying a DIGIT is a docket
        # continuation, not a judgment.
        return (bool([c for c in row if c.isalpha()])
                and row == row.upper()
                and not any(c.isdigit() for c in row))

    merged: list[tuple[str, bool]] = []
    for row in rows:
        caps = is_caps(row)
        if merged and merged[-1][1] and caps:
            merged[-1] = (f"{merged[-1][0]} {row}", True)
            continue
        merged.append((row, caps))

    court: list[str] = []
    judges: list[str] = []
    lower: list[str] = []
    disposition: str | None = None
    history: list[str] = []
    opened = False                    # past the leading origin statement?
    for row, caps in merged:
        if caps:
            opened = True
            if disposition is None:
                disposition = row.rstrip(".")
            else:
                history.append(row)
            continue
        if _HONORABLE.match(row):
            # TWO JUDGES MAY HAVE TRIED IT — one took the ruling under
            # review and another the judgment (gregorwicz, nunez). Both are
            # facts of the origin and neither replaces the other.
            opened = True
            judges.append(row.rstrip("."))
            continue
        if _LOWER_DOCKET.match(row):
            opened = True
            lower.append(_tight(row).rstrip("."))
            continue
        if opened:
            history.append(row)
        else:
            court.append(row)
    if court:
        ctx.crit["lower_court"] = _norm(" ".join(court))
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)
    if lower:
        ctx.crit["lower_court_docket"] = lower
    if disposition:
        ctx.crit["disposition"] = disposition
    if history:
        ctx.crit["history"] = _norm(" ".join(history))


def _panel(line: str) -> list[str]:
    """The bench, from the joining summary. A TITLE is a closed vocabulary
    and a NAME is the run of capitalised tokens after it — 'Presiding Judge
    David B. Gass1 and Judge Anni Hill Foster joined' is two people, and
    the footnote call on the first one is not part of his name."""
    out: list[str] = []
    tokens = line.replace(",", " , ").replace(".", ". ").split()
    i = 0
    while i < len(tokens):
        title = None
        for cand in _PANEL_TITLES:
            words = cand.split()
            if [t.lower() for t in tokens[i:i + len(words)]] == \
                    [w.lower() for w in words]:
                title = cand
                i += len(words)
                break
        if title is None:
            i += 1
            continue
        name: list[str] = []
        while i < len(tokens):
            tok = tokens[i]
            if tok in (",", "&", ";"):
                break
            bare = tok.strip("*†‡.,;:0123456789")
            # A MIDDLE INITIAL IS NOT A WORD. 'Judge Samuel A. Thumma' —
            # the initial reduces to 'A', which reads as the article and
            # cut the surname off the name ('Samuel'). One letter is never
            # a stop word.
            if not bare or not bare[0].isupper() or (
                    len(bare) > 1 and bare.lower() in _PANEL_STOP):
                break
            if any([t.lower() for t in tokens[i:i + len(c.split())]]
                   == [w.lower() for w in c.split()] for c in _PANEL_TITLES):
                break                 # the next title opens its own run
            name.append(tok.strip("*†‡,;:").rstrip("0123456789"))
            i += 1
        # A SUFFIX'S OWN PERIOD IS PART OF THE NAME ('James B. Morse Jr.');
        # the sentence's own stop never reaches here, because the words that
        # end the summary's clauses are the run's terminators.
        full = _norm(" ".join(name)).rstrip(" ,;")
        if full and full not in out:
            out.append(full)
    return out
