"""Supreme Court of the State of Kansas ('kan').

THE CONTRACT. Kansas sets ONE masthead and then decides, by the size of the
type under it, which of TWO papers this is. Nothing is drawn on the page —
over the 50-record corpus the court prints not a single rule, horizontal or
vertical — so every boundary here is leading, measure and type SIZE.

THE MASTHEAD BLOCK is the same on all 50 records: a run of rows CENTRED ON
THE PAGE AXIS and standing clear of the paragraph indent, opening on the
court naming itself and closing on the paper's own title.

    IN THE SUPREME COURT OF THE STATE OF KANSAS   the banner, on the axis
    No. 123,647                                   the docket…
      128,517                                     …and its consolidations,
                                                  ranged under the number
    STATE OF KANSAS,                              the caption: a party…
        Appellee,                                 …its status, ITALIC…
    v.                                            …the pivot…
    ANTHONY DARRYL ALLEN,
        Appellant.
    SYLLABUS BY THE COURT                         …and the paper's title

THE TITLE IS THE LAST ROW OF THE BLOCK, and it is read as a title only
where it stands CLEAR of the caption — the gap above it is wider than any
leading inside the caption (measured: 30-45pt against a 15pt caption
leading, never closer than 1.5x). A block whose last row is not all-caps
and clear has no title, and the run is all caption.

WHERE THE BLOCK ENDS is the same question twice. The caption's own rows are
centred and start at x0>=110; the page's content starts at the RAIL (72) or
the PARAGRAPH INDENT (108) and never between. So the block closes at the
first row set at or left of the indent — geometry, with the caption's own
consolidated-docket rows (ranged under the number, 14.5pt off the axis)
still inside it.

THE TYPE STEP NAMES THE PAPER. Kansas sets its body at 13pt and the
Reporter's apparatus a full step down at 11pt:

    'reported slip' (45 of 50) — an 11pt apparatus stands between the
    syllabus and the writing. It is ONE recital paragraph followed by the
    appearances, both opening at the indent and wrapping to the rail:

        SYLLABUS BY THE COURT             …the title, and beneath it
        1.                                the syllabus by the court, at
        The Sixth Amendment to the …      BODY size — numbered points of
        …                                 law, the court's own headnotes
        Review of the judgment of the     the recital, at 11pt: history,
        Court of Appeals in 62 Kan. …     the court below and its judge,
        Appeal from Johnson District      when it was argued, when the
        Court; TIMOTHY MCCARTHY, judge.   opinion was filed, and what
        Opinion filed June 5, 2026. …     this court did
        Adam Sokoloff, of The Sokoloff    the appearances, one paragraph
        Law Firm, … for appellant.        per side
        The opinion of the court was      the recital Kansas prints over
        delivered by                      every authored opinion…
        STANDRIDGE, J.: Mother appeals…   …and the writing starts

    'court order' (5 of 50) — NO apparatus at any size. The order's body
    opens at the paragraph indent directly under the title and runs to the
    signature; there is no syllabus, no appearance, and no byline. The
    reader claims the block and stops at the title.

        ORDER OF DISBARMENT               the title…
        The court admitted respondent …   …and the order itself starts

THE DISPATCH is therefore two questions, both about the page and neither
about a case's wording: does row 1 name this court, and is there a row set
a full type step below the body within the first four pages? Yes/yes is the
slip; yes/no is the order; anything else is not this paper and gets
NOTHING.

WHERE THE SYLLABUS GOES. Kansas publishes a syllabus by the court — the
numbered points of law under 'SYLLABUS BY THE COURT' — and it is printed in
the middle of the headmatter, between the caption and the Reporter's
recital. It STAYS THERE, tagged `headnotes`: it is the court's own subject
list, and the headmatter renders whole and in the page's order. Lifting it
into a section (which is what the old engine did) reorders the page and
puts the recital that follows it above it. Core's own syllabus inference
never fired on this court in any case — it keys on a bare 'SYLLABUS'
heading opening a page, and Kansas labels 'SYLLABUS BY THE COURT' a third
of the way down the caption page — so it was mis-routing the RECITAL to the
syllabus section instead. No `syllabus.pages` decider is registered: the
extent is a row range inside one page, which that seam cannot express.

WHAT THE READER DOES NOT TOUCH. The folio at the page foot is core's
furniture. The order's body is the writing's, from its first paragraph —
core was reading the first three paragraphs of every disbarment order as
headmatter and opening the writing in the middle of it (in_re_edwards).
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# kan's CourtProfile is registered in courts/__init__.py (with the
# 'syllabus' front-matter declaration applied there); this module adds the
# reader only, so importing it twice can never raise a duplicate profile.

STYLE_SLIP = "reported slip"
STYLE_ORDER = "court order"

# ---- kan's declared facts (measured over all 50 records) -----------------
# THE PAPER. 612x792 on every record; the body rail at 72.0 and the
# paragraph indent at 108.0, to the point, on all 50. Nothing in the
# corpus opens a content row anywhere between them, which is what lets the
# indent close the centred masthead block.
_RAIL = 72.0
_INDENT = 108.0
# THE AXIS. A caption row is centred on the page axis; the widest one in the
# corpus (savage_v._timsah's trustee row, 391pt on a 612pt page) is centred
# to 0.05pt, so WIDTH is no part of the test. The tolerance is set by the
# consolidated docket instead: state_v._ruff ranges '128,440' and '128,880'
# under the first number, 14.6pt right of the axis.
_AXIS = 22.0
# HOW FAR A CENTRED ROW STANDS FROM THE INDENT. The block's own rows start
# at 110.4 (savage) and above; content starts at 72.0 or 108.0.
_CLEAR = 2.0
# THE TITLE STANDS CLEAR OF THE CAPTION. Kansas leads its caption at 15pt
# and its pivot at 30pt, and drops 30-45pt before the title — never less
# than 1.5x the caption's own widest leading.
_TITLE_CLEAR = 1.25
# THE TYPE STEP. Body 13pt, apparatus 11pt. Measured over the corpus the
# apparatus is the FIRST row this court sets below 11.5pt on any of the
# first four pages; no footnote precedes it on any record.
_SMALL = 11.5
# A folio is 6-10pt wide; an apparatus row runs the measure.
_SMALL_MIN_WIDTH = 40.0
# HOW FAR THE BLOCK MAY RUN. state_v._butler carries its syllabus to page 3
# and its apparatus with it; nothing in the corpus needs a fourth page.
_MAX_PAGES = 4

_BANNER = "in the supreme court of the state of kansas"
# THIS court's own docket, and the bar docket the discipline papers carry.
_DOCKET = re.compile(r"^(?:Bar\s+Docket\s+)?Nos?\.\s*[\d,]+\.?$", re.I)
# A consolidation is ranged UNDER the first number, with no label.
_DOCKET_MORE = re.compile(r"^\d{1,3},\d{3}\.?$")
# THE RECITAL Kansas prints over every authored opinion. It is the last row
# of the headmatter and the only body-size row below the apparatus that is
# not a byline.
_DELIVERED = re.compile(r"^the opinion of the court was delivered by:?$", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Kansas sets its statuses in italic on the party captions and
# roman on the 'In the Matter of' ones.
_STATUS_WORDS = {
    "appellant", "appellee", "petitioner", "respondent", "plaintiff",
    "defendant", "intervenor", "movant", "amicus", "amici", "applicant",
    "claimant", "complainant", "cross", "and", "the", "et", "al",
    "counterclaimant", "counterdefendant", "third", "party", "garnishee",
    "trustee", "trustees", "a", "an", "minor", "child", "children",
    "in", "her", "his", "their", "official", "capacity", "individually",
}
_PIVOT = re.compile(r"^v[s]?\.?$", re.I)
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"
# THE RECITAL'S OWN LABELS — the Reporter's fixed apparatus, printed the
# same way on every record, never a case's wording. They are located by
# their OPENING, and each clause runs to the next label, because the
# sentence they close is full of abbreviations that end in a period ('62
# Kan. App. 2d 802, 522 P.3d 355 (2022).') and a period is no boundary.
_LABELS = (
    ("history", re.compile(r"Review of the judgment of the Court of Appeals"
                           r"\b")),
    ("origin", re.compile(r"(?:Appeal|Cross-appeal|Appeal and cross-appeal)"
                          r" from\b|Original (?:proceeding|action)\b")),
    ("submitted", re.compile(r"(?:Oral argument held|Submitted without oral"
                             r" argument|Submitted on the briefs)\b")),
    ("filed", re.compile(r"Opinion filed\b")),
)
_RE_OPINION_FILED = re.compile(r"Opinion filed\s+" + _DATE + r"\.?")
_RE_APPEAL_FROM = re.compile(r"^Appeal from\s+([^;]+?);\s*(.+?),\s*judges?\.",
                             re.S)
# kan signs 'STEGALL, J.:' / 'ROSEN, C.J.:' / 'PER CURIAM:'.
_BYLINE = BylineGrammar(style="abbrev")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _BANNER


def _is_caps(text: str) -> bool:
    t = _norm(text)
    return bool(t) and t == t.upper() and any(c.isalpha() for c in t)


def _is_status(text: str) -> bool:
    """A caption row that is nothing but role words. Kansas prints the
    plural for a multi-party side ('Appellees.', 'Appellants,'), so the
    vocabulary is matched with and without its 's'."""
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w.strip(".") for w in re.split(r"[\s/,-]+", bare) if w.strip(".")]
    return bool(words) and all(
        w in _STATUS_WORDS or w.rstrip("s") in _STATUS_WORDS for w in words)


# A GENERATIONAL SUFFIX IS PART OF THE NAME, and so is an initial. Both end
# in a period the caption's own comma-and-period tail must not take
# ('TERRY D. HORTON, JR.,' -> 'TERRY D. HORTON, JR.'; 'In the Interest of
# K.R.,' -> 'In the Interest of K.R.').
_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}


_INITIALS = re.compile(r"(?:[A-Za-z]\.)+$")


def _tidy(name: str) -> str:
    name = _norm(name).rstrip(", ")
    if not name.endswith("."):
        return name
    last = re.split(r"[\s,]+", name)[-1]
    if _INITIALS.match(last):
        return name                       # 'K.R.' — an initialism
    if "".join(c for c in last if c.isalpha()).lower() in _SUFFIXES:
        return name                       # 'JR.' — a generational suffix
    return name[:-1].rstrip(", ")


def _centred(line, page_width: float) -> bool:
    """A masthead row: centred on the page axis and clear of the indent."""
    cx = (line.x0 + line.x1) / 2
    return (abs(cx - page_width / 2) <= _AXIS
            and line.x0 >= _INDENT + _CLEAR)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="kan")
def read_headmatter_kan(model, geom, **_):
    """Read Kansas's centred masthead and the apparatus under it, or
    NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    # in_re_trummel's measured body comes back 11.0 (its apparatus and its
    # footnotes outweigh a short opinion); the court's own body is 13pt on
    # every record, and the step this reader follows is declared, not
    # measured.
    body_size = max(body_size, 13.0)
    finder = FurnitureFinder(model, _RAIL, body_size)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            # THE FOLIO IS THE ONLY FURNITURE THIS COURT PRINTS — no
            # running head, no running foot, no stamp anywhere in the
            # corpus. Only the folio is stepped over here, deliberately:
            # core's corner-stamp rule (a short reduced-type row in the
            # page's top fifth, left of 0.35 width) takes Kansas's 11pt
            # counsel continuations for stamps — 'appellant.' closing the
            # first appearance on state_v._allen p3 — and a row taken as
            # furniture is a row nobody places.
            if finder.kind(pm, line) == "folio":
                continue
            rows.append(line)
    if len(rows) < 4:
        return NOTHING

    # THE DISPATCH, first half: row 1 names this court.
    if not _is_banner(rows[0].plain):
        return NOTHING

    # THE MASTHEAD BLOCK: the leading run of centred rows.
    block: list = []
    for line in rows:
        if not _centred(line, pages[line.page].width):
            break
        block.append(line)
    if len(block) < 3 or block[0].page != 1:
        return NOTHING

    # THE DISPATCH, second half: is there an apparatus a full type step
    # below the body? Its presence names the paper.
    small = [l for l in rows
             if (l.size or 0) <= _SMALL
             and (l.x1 - l.x0) >= _SMALL_MIN_WIDTH]
    style = STYLE_SLIP if small else STYLE_ORDER

    ctx = _Ctx(pages, geom)
    parser = BylineParser(_BYLINE)

    # ---- the block: banner, docket, caption, title -----------------------
    # WHICH ROWS ARE THE DOCKET is settled first, because the caption band
    # begins where the docket ends and the title is measured against the
    # caption's own leading.
    kinds: list[str] = ["caption"] * len(block)
    kinds[0] = "court"
    in_docket = False
    for i in range(1, len(block)):
        text = _norm(block[i].plain)
        if _DOCKET.match(text) or (in_docket and _DOCKET_MORE.match(text)):
            kinds[i] = "docket"
            in_docket = True
        else:
            in_docket = False
    first_caption = next((i for i, k in enumerate(kinds)
                          if k == "caption"), len(block))
    title_at = _title_index(block, first_caption)
    if title_at is not None:
        kinds[title_at] = "title"

    caption: list[str] = []
    dockets: list[str] = []
    for line, kind in zip(block, kinds):
        text = _norm(line.plain)
        if kind == "court":
            ctx.crit["court"] = text
        elif kind == "title":
            ctx.crit["title"] = text
            ctx.anchor.append(line.id)
        elif kind == "docket":
            dockets.append(text.rstrip("."))
        else:
            caption.append(text)
        ctx.emit(line, kind, centred=True)

    if dockets:
        ctx.crit["docket_number"] = _docket_value(dockets[0])
        if len(dockets) > 1:
            ctx.crit["other_dockets"] = [_docket_value(d) for d in dockets[1:]]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)

    if style is STYLE_ORDER:
        # NOTHING BELOW THE TITLE IS THE HEADMATTER'S. The order's body opens
        # at the paragraph indent under it and belongs to the writing whole.
        ctx.crit["headmatter_style"] = STYLE_ORDER
        return ctx.result()

    # ---- the syllabus by the court, at body size -------------------------
    i = len(block)
    while i < len(rows):
        line = rows[i]
        if (line.size or 0) <= _SMALL:
            break
        if parser.parse(_norm(line.plain)) is not None:
            break                         # a byline always ends the reader
        ctx.emit(line, "headnotes")
        i += 1

    # ---- the Reporter's apparatus, a full type step down -----------------
    recital: list = []
    counsel: list[list] = []
    entry: list | None = None
    while i < len(rows):
        line = rows[i]
        if (line.size or 0) > _SMALL:
            break
        opens = line.x0 >= _INDENT - 1.0
        if not recital:
            # THE FIRST PARAGRAPH IS THE COURT'S RECITAL, on all 45 slips:
            # where the case came from, who tried it, when it was argued and
            # filed, and what this court did. The appearances follow it, one
            # paragraph a side. A paragraph OPENS at the indent and WRAPS to
            # the rail, so the run below the opener is its own.
            recital.append(line)
            ctx.emit(line, "case-info")
            i += 1
            while i < len(rows) and (rows[i].size or 0) <= _SMALL \
                    and rows[i].x0 < _INDENT - 1.0:
                recital.append(rows[i])
                ctx.emit(rows[i], "case-info")
                i += 1
            continue
        if opens or entry is None:
            entry = [line]
            counsel.append(entry)
        else:
            entry.append(line)
        ctx.emit(line, "counsel")
        i += 1

    # ---- the recital over the byline -------------------------------------
    if i < len(rows) and _DELIVERED.match(_norm(rows[i].plain)):
        ctx.emit(rows[i], "case-info")

    if not recital:
        return NOTHING                    # not the paper this contract names

    ctx.crit["headmatter_style"] = STYLE_SLIP
    _recital(ctx, _norm(" ".join(_norm(l.plain) for l in recital)))
    if counsel:
        ctx.crit["attorneys"] = _norm(
            " ".join(_norm(l.plain) for e in counsel for l in e))[:4000]
    return ctx.result()


def _title_index(block: list, first_caption: int) -> int | None:
    """The paper's own title: the LAST row of the block, all-caps, standing
    clear of the CAPTION by more than any leading inside the caption.

    Measured inside the caption band, never across the block — Kansas drops
    the same 45pt between the docket and the caption as between the caption
    and the title, so a whole-block maximum ties with the very gap it is
    supposed to prove (state_v._allen: 44.7 against 44.9)."""
    if len(block) < 3 or first_caption >= len(block) - 1:
        return None
    last = block[-1]
    if not _is_caps(_norm(last.plain)):
        return None
    gaps = [block[k].top - block[k - 1].top
            for k in range(first_caption + 1, len(block))]
    if not gaps:
        return None
    above, inside = gaps[-1], gaps[:-1]
    if inside and above < _TITLE_CLEAR * max(inside):
        return None
    return len(block) - 1


def _docket_value(text: str) -> str:
    return re.sub(r"^(?:Bar\s+Docket\s+)?Nos?\.\s*", "", text, flags=re.I)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, pages, geom):
        self.pages = pages
        self.geom = geom
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.anchor: list[int] = []

    def emit(self, line, role: str, centred: bool = False) -> None:
        rel = 0.0
        if not centred and line.x0 > _RAIL + 1.0:
            rel = line.x0 - _RAIL
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align("C" if centred else "L"),
            x0=line.x0, size=line.size or 0.0, bold=bool(line.all_bold),
            rel=rel, role=role))
        self.consumed.add(line.id)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": [], "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# what the block and the recital say
# --------------------------------------------------------------------------

def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        row = row.rstrip("*†‡ ")
        if _PIVOT.match(row):
            if seen_pivot:
                break
            side, seen_pivot = right, True
            continue
        if _is_status(row):
            continue
        side.append(row)
    if seen_pivot and left and right:
        one, two = _tidy(" ".join(left)), _tidy(" ".join(right))
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _tidy(" ".join(left + right))
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


def _recital(ctx: _Ctx, text: str) -> None:
    """The Reporter's recital, read by its own printed labels.

    'Review of the judgment of the Court of Appeals in 62 Kan. App. 2d 802,
    522 P.3d 355 (2022). Appeal from Johnson District Court; TIMOTHY
    MCCARTHY, judge. Oral argument held March 29, 2024. Opinion filed June
    5, 2026. Judgment of the Court of Appeals … is affirmed in part and
    reversed in part. Judgment of the district court is affirmed.'
    """
    marks = []
    for name, rx in _LABELS:
        mm = rx.search(text)
        if mm is not None:
            marks.append((mm.start(), name))
    marks.sort()
    if not marks:
        ctx.crit["disposition"] = text.rstrip()
        return
    parts: dict[str, str] = {}
    for k, (start, name) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(text)
        parts[name] = _norm(text[start:end])

    if "history" in parts:
        ctx.crit["history"] = parts["history"].rstrip()
    origin = parts.get("origin", "")
    if origin:
        mm = _RE_APPEAL_FROM.match(origin)
        if mm is not None:
            ctx.crit["lower_court"] = _norm(mm.group(1))
            ctx.crit["lower_court_judge"] = _norm(mm.group(2))
            rest = _norm(origin[mm.end():])
            if rest:
                # 'Appeal from … ; JUDGE, judge. Affirmed.' — a one-line
                # recital states the judgment right here.
                parts["tail"] = rest
        else:
            # AN ORIGINAL PROCEEDING HAS NO COURT BELOW. 'Original
            # proceeding in discipline.' / 'Original action in quo
            # warranto.' says how the case reached this court, which is
            # history, not a tribunal.
            head, _, tail = origin.partition(".")
            ctx.crit.setdefault("history", _norm(head) + ".")
            if _norm(tail):
                parts["tail"] = _norm(tail)
    if "submitted" in parts:
        ctx.crit["submitted"] = parts["submitted"].rstrip(". ")
    disposition = [parts.get("tail", "")]
    filed = parts.get("filed", "")
    if filed:
        mm = _RE_OPINION_FILED.match(filed)
        if mm is not None and mm.group(1).split()[0].lower() in _MONTHS:
            ctx.crit["decision_date"] = _norm(mm.group(1))
            disposition.append(_norm(filed[mm.end():]))
        else:
            disposition.append(filed)
    rest = _norm(" ".join(d for d in disposition if d))
    if rest:
        # WHAT IS LEFT IS THE DISPOSITION — what the court DID, as the
        # recital states it ('Affirmed.' / 'Published censure.' / 'Judgment
        # of the Court of Appeals … is affirmed in part and reversed in
        # part.').
        ctx.crit["disposition"] = rest
