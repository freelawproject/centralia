"""Supreme Court of the State of Arizona ('ariz').

THE CONTRACT — one paper, printed 50 times out of 50: the ENGRAVED SLIP.

Arizona names itself at the head of every slip in two rows — a 12pt 'IN THE'
over an 18pt 'SUPREME COURT OF THE STATE OF ARIZONA' — and then FENCES every
section of the headmatter with a rule ~108pt wide centred on the page axis.
The fence is the section mark; the LANDMARK inside each band says what the
band is. No band is identified by its ordinal, because the band count varies
(4 to 6 fences on page 1) and a band may run across a page turn:

    IN THE                                     the masthead, 12pt
    SUPREME COURT OF THE STATE OF ARIZONA      …and its 18pt second row
    ─────────                                  a fence ON THE AXIS
    STATE OF ARIZONA,                          the caption: a party, bold…
         Appellee,                             …its status, italic…
    v.                                         …the pivot…
    JOHN LOGAN BROWN,
         Appellant.
    ─────────
    No.  CR-24-0143-PR                         the docket…
    Filed October 7, 2025                      …and the release date
    ─────────
    Appeal from the Superior Court in Pima County   the origin…
    The Honorable Brenden J. Griffin, Judge         …who tried it…
    No.  CR20220381-001                            …its number…
    REVERSED AND REMANDED                          …the disposition
    Memorandum of the Court of Appeals, Division Two  …the history
    No. 2 CA-CR 23-0138
    VACATED IN PART, AFFIRMED IN PART
    ─────────
    COUNSEL:                                   the appearances, labelled
    Kristin K. Mayes, Arizona Attorney General, …
    ─────────
    JUSTICE BEENE authored the Opinion of the Court, in which VICE CHIEF
    JUSTICE LOPEZ and JUSTICES BOLICK, MONTGOMERY, KING and
    BERCH (Retired)* joined.  CHIEF JUSTICE TIMMER dissented.
    ─────────
    JUSTICE BEENE, Opinion of the Court:        …and the writing starts

WHY THE LAST BAND MATTERS. The joining summary is the row core lost. It is
not a byline — it is the Court stating who wrote and who joined — but it
parses as one ('JUSTICE BEENE authored…' reads as a reversed byline), and
core, having no place for it, dropped it from the document on all 50 records
and opened a phantom authorless writing on four of them (henke, perez,
pointe_16, joel_carson). Reading it here as `summary`/`panel` puts the text
back and takes the phantom away. Its rows are the ONLY headmatter rows set
at the body rail beside counsel, and it is found by its own landmark —
'authored the Opinion of the Court', present on every record in the corpus —
never by position.

THE BANDS ARE NOT THE PARSER; THE LANDMARKS ARE. A band may hold two
sections (in_re_mh2023-004502 sets counsel and the summary inside one fence
pair) and a section may hold two bands (contreras fences the trial court and
the Court of Appeals separately). So the walk is a state machine over rows in
page order, and the fences are re-emitted where the page draws them.

A record that does not name the court in its first two rows, or that draws
fewer than three fences on page 1, is not this paper and gets NOTHING.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineGrammar, BylineParser, is_caps_name
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

STYLE_SLIP = "engraved slip"

# ---- ariz's declared facts (measured over all 50 records) ----------------
# THE FENCE. 253 fences over the corpus, every one of them 93.6-113.2pt wide.
# 49 records centre it on the page axis to within half a point; state_farm
# sets its whole headmatter 18pt left of the axis and its fences with it.
_FENCE_MEASURE = (88.0, 118.0)
_FENCE_AXIS = 24.0
# The FOOTNOTE separator is the same court's other rule, and it is told apart
# by where it STARTS, not by its width: 144pt at the BODY RAIL (x0=108) where
# a fence starts at x0=252. abortion_access types the same separator as a
# 150pt underscore run at the same rail.
_SEP_MIN = 100.0
_SEP_RAIL = 4.0
# THE MASTHEAD: 18pt over a 12pt body — the only row on page 1 above 15pt.
_MASTHEAD_SIZE = 15.0
# HOW FAR THE BLOCK MAY RUN. joel_carson consolidates two special actions and
# carries its origin onto page 2 and its byline onto page 3; nothing in the
# corpus needs a fourth page.
_MAX_PAGES = 4
# A SUMMARY CONTINUES ON THE NEXT LINE. Inside the joining summary the rows
# sit one leading apart (14.4-15.2pt on a 15pt lead); the byline below it
# stands 30pt clear. 1.35x the lead separates a wrap from a new element.
_SUMMARY_WRAP = 1.35

_MASTHEAD_TOP = "in the"
_MASTHEAD = "supreme court of the state of arizona"
_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# 'No.  CR-24-0143-PR' / 'CV-24-0167-AP/EL' / 'No. SB-24-0007-AP' — THIS
# court's own docket, which is what the fenced docket band holds. The
# tribunal below numbers its cases differently ('CR20220381-001',
# '1 CA-CV 23-0661') and those are read in the origin band instead.
_DOCKET = re.compile(r"^(?:Nos?\.\s*)?[A-Z]{2}-\d{2}-\d{3,4}(?:-[A-Z]+"
                     r"(?:/[A-Z]+)?)?\.?$")
_CONSOLIDATED = re.compile(r"^\(?consolidated\)?\.?$", re.I)
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december",
           "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep",
           "oct", "nov", "dec")
# 'Filed October 7, 2025' — Arizona labels its release date, and prints the
# SAME shape again in the origin band for the decision below.
_FILED = re.compile(r"^Filed\s+([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})\.?$")
# The appearances are labelled, once, in the band that holds them.
_COUNSEL_LABEL = re.compile(r"^COUNSEL:?$")
# THE JOINING SUMMARY's own landmark. 50 of 50 records print it; the court
# varies only the case of 'Opinion'.
_SUMMARY = re.compile(r"authored the opinion of the court", re.I)
# Who tried it, as the origin band says.
_HONORABLE = re.compile(r"^The Honorable\b", re.I)
# The number the court BELOW gave the case, in the two forms Arizona prints:
# labelled bare, or labelled by the tribunal that assigned it.
_LOWER_DOCKET = re.compile(r"^(?:[A-Za-z. ]{0,24})?Nos?\.\s*\S", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Arizona stacks its roles with a slash ('Plaintiff/Appellant') and
# spells out the special-action and compensation roles in full.
_STATUS_WORDS = (
    "appellant", "appellee", "petitioner", "respondent", "plaintiff",
    "defendant", "intervenor", "movant", "amicus", "amici", "applicant",
    "claimant", "complainant", "employee", "employer", "carrier", "judge",
    "insurance", "real", "party", "in", "interest", "cross", "and", "the",
    "et", "al", "counter", "counterclaimant", "counterdefendant",
    "third", "garnishee", "creditor", "debtor", "conservator", "ward",
    "parties", "intervention", "propria", "persona", "adult", "an", "a",
)
# The bench titles Arizona uses in its joining summary, longest first.
_PANEL_TITLES = ("VICE CHIEF JUSTICE", "CHIEF JUSTICE", "JUSTICES",
                 "JUSTICE", "JUDGES", "JUDGE")
# ariz signs the lead opinion title-led and CAPS ('JUSTICE BEENE, Opinion of
# the Court:') and its separate writings abbreviated ('TIMMER, C.J.,
# Dissenting.'). Both forms end this reader; the profile's own grammar is a
# strict subset, so the walk stops no later than assembly's byline does.
_BYLINE = BylineGrammar(style="abbrev", also_reversed=True,
                        rev_titles=("VICE CHIEF JUSTICE", "CHIEF JUSTICE",
                                    "JUSTICE"))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _tight(text: str) -> str:
    """A NUMBER'S OWN HYPHEN CARRIES NO SPACE. Two of Arizona's slips stack
    six literal space glyphs on one point inside the docket, and the one that
    survives deduplication reads as a separator ('No.  CV- 24-0013-PR' /
    'No.  CV2022- 092441'). pdftotext sets neither; the page sets neither."""
    return re.sub(r"\s*-\s*", "-", _norm(text))


def _is_masthead_top(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD_TOP


def _is_masthead(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD


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


def _filed_value(text: str) -> str | None:
    """'Filed October 7, 2025' -> 'October 7, 2025', or None."""
    mm = _FILED.match(_norm(text))
    if mm is None or mm.group(1).lower().rstrip(".") not in _MONTHS:
        return None
    return f"{mm.group(1)} {mm.group(2)}, {mm.group(3)}"


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
    """Where this page's footnotes begin — the top of the separator Arizona
    sets AT THE BODY RAIL, drawn (144pt) or typed (a 150pt underscore run).
    Everything below it is a note and belongs to core's footnote pass, not
    to the headmatter."""
    tops = [r.top for r in pm.h_rules
            if r.width >= _SEP_MIN and abs(r.x0 - body_x0) <= _SEP_RAIL]
    tops += [l.top for l in pm.lines
             if _TYPED_RULE.match(_norm(l.plain))
             and abs(l.x0 - body_x0) <= _SEP_RAIL
             and (l.x1 - l.x0) >= _SEP_MIN]
    return min(tops) if tops else float("inf")


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ariz")
def read_headmatter_ariz(model, geom, **_):
    """Read Arizona's fenced slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    lead = (geom.lead if geom and geom.lead else 15.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS, in page order, with same-row pieces rejoined. A justified
    # summary line split at its wide gap put 'JUSTICE BOLICK, joined by
    # JUSTICE' on a row of its own, and that half-row parses as a byline
    # (gordonowen).
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
    # THE DISPATCH: the court names itself in two rows, over a page-1 stack
    # of axis fences. Nothing is matched against a case's own wording.
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
        if ended:
            break                     # a content row past the closing fence
        text = _norm(" ".join(l.plain for l in group))

        if state == "court":
            if _is_masthead_top(text) or _is_masthead(text):
                if _is_masthead(text):
                    ctx.crit.setdefault("court", text)
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
                dockets.append(_tight(text).rstrip("."))
                ctx.emit(group, "docket")
                continue
            state = "origin"

        if state == "origin":
            if _COUNSEL_LABEL.match(text):
                state = "counsel"
                ctx.emit(group, "counsel")
                continue
            if _SUMMARY.search(text):
                state = "summary"
            else:
                origin.append(text)
                ctx.emit(group, "lower-court")
                continue

        if state == "counsel":
            if _SUMMARY.search(text):
                state = "summary"
            elif parser.parse(text) is not None:
                break                 # a byline always ends the reader
            else:
                counsel.append(text)
                ctx.emit(group, "counsel")
                prev_bottom, prev_page = group[0].top, page
                continue

        if state == "summary":
            # A SUMMARY ROW IS A WRAP OF THE ONE ABOVE IT. Bounded by the
            # page's own leading, so a byline lookalike inside the summary
            # ('PELANDER (Retired),* dissented.') stays in the summary and
            # the real byline below the blank line ends the reader.
            if summary and (prev_page != page
                            or top - prev_bottom > _SUMMARY_WRAP * lead):
                ended = True
                continue
            summary.append(text)
            # THE WHOLE BLOCK IS THE PANEL. It is both things at once — who
            # sat, and who wrote what — but the first row was tinted `panel`
            # and its continuations `summary`, so one statement rendered as
            # two different kinds of row. The user's call, 2026-08-19: panel,
            # even though it is a bit of both. The `summary` criterion is
            # unaffected; this is the row's role, not its content.
            ctx.emit(group, "panel")
            prev_bottom, prev_page = group[0].top, page
            continue
        prev_bottom, prev_page = group[0].top, page

    if not summary or not dockets:
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
        self.crit: dict = {}

    def emit(self, group: list, role: str):
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

    def rule(self, page: int):
        # A FENCE RENDERS WHERE THE PAGE DRAWS IT. Core re-sorts the block by
        # the source position of each item's provenance, so a rule carrying
        # none sorts to the end; it takes the prov of the row it stands under
        # and stays put (a stable sort keeps it after that row).
        prev = next((i for i in reversed(self.items)
                     if isinstance(i, m.HmLine)), None)
        self.items.append(m.Rule(
            prov=prev.prov if prev is not None else m.Prov(page),
            span="center"))

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": [], "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        # A FOOTNOTE MARK IS NOT PART OF A NAME. Arizona calls its note off
        # the party itself ('STEVE MONTENEGRO, ET AL.,*').
        row = row.rstrip("*†‡∗⁎ ")
        if _is_pivot(row):
            if seen_pivot:
                break                 # a consolidated slip: the LEAD case
            side = right
            seen_pivot = True
            continue
        if _is_status(row):
            continue
        side.append(row)
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
    below, this Court's disposition, and the history under it.

    Two rows may be one statement. Arizona sets its origin and its
    disposition to the measure and lets both wrap ('Appeal of Hearing Panel
    Opinion and Disciplinary Order from the' / 'Office of the Presiding
    Disciplinary Judge'; 'AFFIRMED IN PART, REVERSED IN PART, REMANDED WITH'
    / 'INSTRUCTIONS'), so consecutive rows of the same kind are joined
    before anything is read out of them."""
    def is_caps(row: str) -> bool:
        # A DISPOSITION IS ALL WORDS. Arizona sets its judgment in bold caps
        # and its numbers in roman, so a caps row carrying a DIGIT is a
        # docket continuation, not a judgment ('Nos. CV2024-019846' wraps to
        # 'CV2024-019880' — read as caps it became the disposition).
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
    judge: str | None = None
    lower: list[str] = []
    disposition: str | None = None
    history: list[str] = []
    opened = False                    # past the leading origin statement?
    was_docket = False                # the row above was a case number
    for row, caps in merged:
        if caps:
            # A BOLD ALL-CAPS ROW IS A DISPOSITION. The first one is this
            # Court's judgment on the appeal; a second belongs to the
            # decision the Court of Appeals made, and reads as history.
            opened = True
            if disposition is None:
                disposition = row.rstrip(".")
            else:
                history.append(row)
            continue
        if _HONORABLE.match(row):
            opened = True
            judge = judge or row
            continue
        if _LOWER_DOCKET.match(row) or (was_docket and any(
                c.isdigit() for c in row) and row == row.upper()):
            opened = True
            was_docket = True
            lower.append(_tight(row).rstrip("."))
            continue
        was_docket = False
        if opened:
            history.append(row)
        else:
            court.append(row)
    if court:
        ctx.crit["lower_court"] = _norm(" ".join(court))
    if judge:
        ctx.crit["lower_court_judge"] = judge
    if lower:
        ctx.crit["lower_court_docket"] = lower
    if disposition:
        ctx.crit["disposition"] = disposition
    if history:
        ctx.crit["history"] = _norm(" ".join(history))


def _panel(line: str) -> list[str]:
    """The bench, from the joining summary. A TITLE is a closed vocabulary
    and a NAME is an all-caps token — 'JUSTICES BOLICK, BEENE, MONTGOMERY,
    KING and CRUZ' is five people, and 'BRUTINEL (RETIRED)' is one."""
    out: list[str] = []
    tokens = line.replace(",", " , ").split()
    i = 0
    while i < len(tokens):
        title = None
        for cand in _PANEL_TITLES:
            words = cand.split()
            if [t.upper() for t in tokens[i:i + len(words)]] == words:
                title = cand
                i += len(words)
                break
        if title is None:
            i += 1
            continue
        # every all-caps token until a word that is not a name
        while i < len(tokens):
            tok = tokens[i]
            if tok in (",", "&") or tok.lower() == "and":
                i += 1
                continue
            if any([t.upper() for t in tokens[i:i + len(c.split())]]
                   == c.split() for c in _PANEL_TITLES):
                break                 # the next title opens its own run
            bare = tok.strip("*†‡.,;:0123456789")
            if bare.startswith("(") or not is_caps_name(bare, max_tokens=1):
                break
            if bare and bare not in out:
                out.append(bare)
            i += 1
    return out
