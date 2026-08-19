"""New Jersey Superior Court, Appellate Division ('njsuperctappdiv').

THE CONTRACT — one paper, printed 42 times out of 42: the SHOULDERED
MASTHEAD. Unlike its Supreme Court (`nj`), which fences a centred ladder,
the Appellate Division sets its masthead in the page's RIGHT SHOULDER and
hangs a caption at the body rail beneath it, then indents everything the
Clerk records to a rail of its own:

    RECORD IMPOUNDED                        a notice, above everything
    NOT FOR PUBLICATION WITHOUT THE         the advisory, likewise ABOVE
    APPROVAL OF THE APPELLATE DIVISION      the masthead

                        SUPERIOR COURT OF NEW JERSEY    THE MASTHEAD, in
                        APPELLATE DIVISION              the right shoulder
                        DOCKET NOS. A-3362-23           (x0 = 288.1 on a
                                    A-3391-23           612pt page, on all
                                    A-3710-23           42 records), its
                                                        extra dockets set
    NEW JERSEY DIVISION OF                              flush right under
    CHILD PROTECTION AND         APPROVED FOR           the first
    PERMANENCY,                  PUBLICATION            ← the CLERK'S STAMP,
         Plaintiff-Respondent,   June 16, 2026            10pt bold, pinned
    v.                           APPELLATE DIVISION       right of centre and
    H.V.,                                                 INTERLEAVED with
         Defendant-Respondent.                            the party rows
    _________________________    a FENCE closing the caption
    Argued April 14, 2026 – Decided June 16, 2026    THE RECORD BAND, at
    Before Judges Sumners, Susswein and Augostini.   its own 144pt rail:
    On appeal from the Superior Court of New         dates, bench, origin,
    Jersey, Chancery Division, Family Part, …        appearances, in that
    Meredith Alexis Pollock, Deputy Public Defender, order
    argued the cause for appellant I.V. …
    The opinion of the court was delivered by        …and the writing opens

THE DISPATCH IS THE SHOULDER, NOT THE WORDING. `SUPERIOR COURT OF NEW
JERSEY` is printed by this court, by its Supreme Court, and by every trial
division below it — the fact that identifies THIS paper is that the row
stands in the page's right half with `APPELLATE DIVISION` directly under it
at the same rail. Measured over all 42 records the rail is x0 = 288.1 to the
tenth of a point; the caption below it opens at 72 and the record band at
144, so the three zones are three rails and nothing is read by its words.

THREE RAILS, THREE ZONES.

* the SHOULDER (x0 >= half the page) is the masthead: the court, its
  division, and the dockets. The extra dockets of a consolidated appeal are
  set flush right beneath the first (x0 = 386.7), still in the shoulder;
* the BODY RAIL (72, statuses indented to 108 or 144) is the caption,
  closed by a FENCE the court sets two different ways — TYPED as a run of
  underscores (33 records) or DRAWN as a 213-216pt rect (7), and on two
  records not at all. The fence is decoration here, not the band mark: it
  is emitted where the page sets it and nothing is read from its absence;
* the RECORD RAIL (144.0) is what the Clerk records. It opens on the DATE
  ROW and runs to the byline.

THE DATE ROW IS ONE ROW, NOT A GRID. This is where the Appellate Division
parts company with the Supreme Court: `nj` sets 'Argued' over its date in
one column and 'Decided' over its date in another, a 2x2 cell that reads
row-wise as two bare labels (the `split-label` defect on 31 of its 50
records). The Appellate Division sets the same two events on ONE line
divided by a dash — 'Argued April 14, 2026 – Decided June 16, 2026' — so
there is no grid to read column-wise and no split label to fold back. The
dash is not always the same glyph (en dash, figure dash, plain hyphen) and
the label is not always one word ('Argued on March 4, 2026'), so the row is
split on the dash and each half read as label-then-date.

THE RECORD BAND KEEPS THE PAGE'S ORDER, and its order is fixed: the date
row, the bench, the origin, the appearances. Each is a PARAGRAPH — 16.1pt
leading inside one, 32.2pt between — and a paragraph is named by its first
row from a closed vocabulary of LABELS ('Before' + Judge/Judges; an origin
opening 'On ' + lower case), never by anything read out of a party's or a
firm's name. A row that opens no paragraph inherits the role above it,
which is what carries a bench roster or an origin across a page break
(dcpp_v._h.v. runs its origin from page 5 onto page 6). Once the
appearances start, no later paragraph is re-labelled: counsel prose says
'On the brief' often enough to be dangerous.

THE FURNITURE THIS BLOCK INHERITS, all of it recorded as Dropped:

* everything ABOVE the masthead on the cover page — 'RECORD IMPOUNDED',
  the advisory, and on an unpublished slip the 9.5pt precedent notice
  ('This opinion shall not "constitute precedent…"'). Position identifies
  them: no caption content ever stands above the masthead;
* the CLERK'S STAMP — 10pt bold against the caption's 14pt, right of
  centre, and printed BETWEEN the party rows so that pdfio hands it back
  fused into them ('individually, APPROVED FOR PUBLICATION'). It is shed
  piece by piece, by SIZE, from inside the row it fell into — exactly as
  ca6 sheds its rail corners. Keyed on size and not on the phrase, because
  one record prints 'APPROVD FOR PUBLICATION' and another
  'A PPROV ED FOR PUBLICATION';
* the FOOTNOTE ZONE, which on a counsel page interrupts the record band. Its
  separator is this court's own invariant: a DRAWN rule exactly 144.0pt wide
  at the body rail. The caption fence, when drawn, is 213-216pt at the same
  rail — width alone tells them apart, and nothing below the 144pt rule is
  read, claimed or allowed to end the reader.

A record that does not print the shoulder gets NOTHING.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile           # noqa: F401  (profile lives in
from ..pdfio.rules import is_typed_rule      # courts/__init__.py — see below)
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

# THE PROFILE for this court is registered in `courts/__init__.py` beside
# the other state courts and is NOT re-registered here: `register()` raises
# on a duplicate id, which would break the import for every court in the
# package. Nothing in this reader needs a declared CourtProfile fact.

STYLE_SHOULDER = "shouldered masthead"

# ---- njsuperctappdiv's declared facts (measured over all 42 records) -----
# THE SHOULDER. The masthead's rail is x0 = 288.1 on a 612pt page on every
# record in the corpus. What is DECLARED is weaker than the measurement and
# survives a page size change: the masthead stands in the page's right half.
_SHOULDER_FRAC = 0.45
# THE RECORD RAIL, at 144.0 on every record — twice the body rail. A row of
# the record band never leaves it; the byline that ends the band is set at
# 72 ('PER CURIAM') or 108 ('The opinion of the court was delivered by').
_RECORD_RAIL = (138.0, 152.0)
_RECORD_RAIL_MIN = 136.0
# THE CLERK'S STAMP: 10pt bold against a 14pt caption, and the only text
# under 12pt anywhere below the masthead. Measured 9.0-10.0 on the stamp,
# 9.5-11.0 on the notices above the masthead, 14.0 everywhere else.
_STAMP_MAX_SIZE = 11.5
# THE FOOTNOTE SEPARATOR, this court's invariant: 144.0pt at the body rail.
# The caption fence, DRAWN, is 213-216pt at the same rail.
_FOOT_RULE_W = (142.0, 146.0)
_FENCE_RULE_W = (200.0, 232.0)
_RULE_RAIL = 6.0
# HOW FAR THE BLOCK MAY RUN. dcpp_v._h.v. consolidates fourteen appeals and
# carries its captions from page 1 to page 5 and its appearances to page 9;
# nothing in the corpus needs more.
_MAX_PAGES = 10

_BANNER = "superior court of new jersey"
_DIVISION = "appellate division"
# THE DOCKET, printed as a labelled row and continued as bare numbers under
# it: 'DOCKET NOS. A-3362-23' / 'A-3391-23' / … One record prints
# 'DOCKET NO.  A- 1378-23', so the number's own spacing is normalized.
_DOCKET_LABEL = re.compile(r"^DOCKET\s+NOS?\.\s*(.*)$", re.I)
_DOCKET_BARE = re.compile(r"^[A-Z]{1,3}-\s?\d{3,6}-\d{2}[A-Z\d]*\.?$")
# THE DATE ROW's events, as a closed vocabulary of what a court DOES to a
# case. The label is used only to file the date under the right criterion;
# the pairing itself is positional (label, then its date, one per half).
_HEARD = ("argued", "reargued", "submitted", "resubmitted", "considered")
_DECIDED = ("decided", "filed", "opinion filed", "remanded")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# The dash the court divides the two events with — en dash, figure dash,
# em dash or a plain hyphen, all four in the corpus.
_DASH = re.compile(r"\s[–—‒-]\s")
_EVENT_HEAD = re.compile(
    r"^(argued|reargued|submitted|resubmitted|considered|decided|telephonically)\b",
    re.I)
# THE BENCH LABEL, closed: 'Before Judges X, Y and Z.' / 'Before Judge X.'
_BENCH = re.compile(r"^Before\s+Judges?\b", re.I)
# THE ORIGIN, which always opens on 'On' followed by lower case: 'On appeal
# from the Superior Court of New Jersey,' / 'On appeal from an interlocutory
# order of …' / 'On appeal from the New Jersey Department of …'.
_ORIGIN = re.compile(r"^On\s+[a-z]")
# The number the court BELOW gave the case, as the origin states it.
_LOWER_NO = re.compile(
    r"(?:Docket|Indictment|Accusation|Complaint|Agency|Municipal Appeal)"
    r"\s+Nos?\.\s*([A-Z]{0,3}-?[\d][\w./-]*(?:\s+and\s+[A-Z]{0,3}-?[\d][\w./-]*)*)")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. (Shared in spirit with nj's reader — same state, same labels.)
_STATUS_WORDS = {
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "movant",
    "movants", "amicus", "amici", "curiae", "applicant", "applicants",
    "claimant", "claimants", "complainant", "cross", "third", "party",
    "counterclaimant", "counterdefendant", "and", "the", "et", "al",
    "in", "interest", "real", "parties", "a", "an", "of",
}
_PIVOT = re.compile(r"^v\.?$", re.I)
# THE WRAPPED BYLINE's first row. Matched by its SHAPE ('The opinion …
# delivered by') so a dropped word in the source still matches — v1 found
# 'The opinion the court was delivered by' in this corpus.


def _is_intro(text: str) -> bool:
    low = _norm(text).lower()
    return low.startswith("the opinion") and low.endswith("delivered by")


def _byline_next(stream: list, idx: int) -> bool:
    """True when the next inked row of the stream signs the opinion."""
    from . import get_profile
    from ..resolve.bylines import BylineParser
    for row in stream[idx:idx + 2]:
        if not row.parts:
            continue
        parser = BylineParser(get_profile("njsuperctappdiv").byline)
        return parser.parse(row.text) is not None
    return False


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _BANNER


def _is_division(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _DIVISION


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w for w in re.split(r"[\s/,-]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


def _is_date(text: str) -> bool:
    mm = _DATE.search(_norm(text))
    return bool(mm) and mm.group(1).split()[0].lower().rstrip(".") in _MONTHS


def _join(rows: list[str]) -> str:
    """Join caption rows the way the page reads them: a row broken at a
    hyphen the name already carries keeps the hyphen and loses the space."""
    out = ""
    for row in rows:
        row = _norm(row)
        if not row:
            continue
        out = row if not out else (out + row if out.endswith("-")
                                   else out + " " + row)
    return out


# --------------------------------------------------------------------------
# the page, as rows
# --------------------------------------------------------------------------

def _foot_top(pm) -> float | None:
    """The top of this page's footnote zone: the court's own 144.0pt rule at
    the body rail. Nothing at or below it is read."""
    tops = [r.top for r in pm.h_rules
            if _FOOT_RULE_W[0] <= r.width <= _FOOT_RULE_W[1]
            and abs(r.x0 - 72.0) <= _RULE_RAIL]
    return min(tops) if tops else None


def _drawn_fences(pm) -> list[float]:
    """The tops of the fences this page DRAWS — 213-216pt at the body rail.
    A page that types its fence instead draws none, and vice versa."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_RULE_W[0] <= r.width <= _FENCE_RULE_W[1]
                  and abs(r.x0 - 72.0) <= _RULE_RAIL)


class _Row:
    """One visual row of the page, with the Clerk's stamp shed from it.

    The stamp is printed BETWEEN the party rows and pdfio hands it back as
    extra pieces of the row it overlaps. Splitting by SIZE inside the row
    leaves the caption its own words and the stamp its own provenance."""

    __slots__ = ("parts", "stamp", "page", "top")

    def __init__(self, parts: list):
        body = [p for p in parts if (p.size or 99) > _STAMP_MAX_SIZE]
        stamp = [p for p in parts if (p.size or 99) <= _STAMP_MAX_SIZE]
        # A row set ENTIRELY in the small size is not a caption row with a
        # stamp fused into it — it is the stamp (or a notice) outright.
        self.parts = body
        self.stamp = stamp
        self.page = parts[0].page
        self.top = parts[0].top

    @property
    def text(self) -> str:
        return _norm(" ".join(p.plain for p in self.parts))

    @property
    def x0(self) -> float:
        return min(p.x0 for p in self.parts)

    @property
    def x1(self) -> float:
        return max(p.x1 for p in self.parts)


def _rows_of(pm, finder, foot_top) -> list[_Row]:
    """The page's visual ROWS above the footnote zone, same-row pieces kept
    together — the stamp and a justified counsel line both arrive split."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        if foot_top is not None and line.top >= foot_top - 2.0:
            continue
        key = line.row if line.row is not None else round(line.top)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [_Row(sorted(groups[k], key=lambda l: l.x0)) for k in order]


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="njsuperctappdiv")
def read_headmatter_njsuperctappdiv(model, geom, **_):
    """Read the Appellate Division's shouldered masthead, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    cover = model.pages[0]
    shoulder = cover.width * _SHOULDER_FRAC
    rows = _rows_of(cover, finder, _foot_top(cover))

    # THE DISPATCH: the court naming itself IN THE RIGHT SHOULDER, with its
    # division directly under it at the same rail. Neither row alone is the
    # landmark — the trial divisions print the first and the Supreme Court
    # prints it centred.
    start = None
    for i, row in enumerate(rows[:-1]):
        if (row.parts and rows[i + 1].parts
                and _is_banner(row.text) and _is_division(rows[i + 1].text)
                and row.x0 >= shoulder
                and abs(rows[i + 1].x0 - row.x0) <= 2.0):
            start = i
            break
    if start is None:
        return NOTHING
    rail = rows[start].x0

    ctx = _Ctx(model, geom, pages, body_size)

    # EVERYTHING ABOVE THE MASTHEAD IS FURNITURE. No caption content ever
    # stands there; what does is 'RECORD IMPOUNDED', the advisory, and the
    # precedent notice. They are grouped by contiguity AND by type size, so
    # an 11pt advisory and a 9.5pt notice stay two separate notices.
    above: list[list] = []
    for row in rows[:start]:
        prev = above[-1][-1] if above else None
        if (prev is not None and row.top - prev.top <= 26.0
                and abs((row.parts + row.stamp)[0].size
                        - (prev.parts + prev.stamp)[0].size) <= 1.0):
            above[-1].append(row)
        else:
            above.append([row])
    for group in above:
        ctx.drop(group, "notice")

    # THE STREAM: rows from the masthead on, in page order, bounded.
    stream: list[_Row] = list(rows[start:])
    for pm in model.pages[1:_MAX_PAGES]:
        stream.extend(_rows_of(pm, finder, _foot_top(pm)))

    caption: list[str] = []
    dockets: list[str] = []
    bench: list[str] = []
    origin: list[str] = []
    counsel: list[str] = []
    date_row: str | None = None
    state = "shoulder"
    role = ""
    prev: _Row | None = None
    stamp_run: list = []
    pending: list[float] = []
    seen_page: int | None = None

    for idx, row in enumerate(stream):
        # THE CLERK'S STAMP IS A RUN, not a row: three (sometimes four) rows
        # of it are fused into three different caption rows, and dropped one
        # by one they read as three unrelated stamps. It closes at the first
        # row that carries none of it.
        if row.stamp:
            stamp_run.append(row)
        elif stamp_run:
            ctx.drop(stamp_run, "stamp", stamp_only=True)
            stamp_run = []
        if not row.parts:
            continue

        # A DRAWN FENCE renders where the page draws it, and this court
        # draws some of its fences and types the rest. Each is emitted as
        # the walk passes its top; the typed ones ARE rows of the page.
        if row.page != seen_page:
            seen_page = row.page
            pending = _drawn_fences(pages[row.page]) \
                if state != "shoulder" else []
        while pending and pending[0] < row.top:
            pending.pop(0)
            ctx.rule(row.page)

        text = row.text
        if state == "shoulder":
            if row.x0 >= shoulder:
                mm = _DOCKET_LABEL.match(text)
                if mm:
                    dockets.extend(_dockets(mm.group(1)))
                    ctx.emit(row, "docket")
                elif _DOCKET_BARE.match(text):
                    dockets.extend(_dockets(text))
                    ctx.emit(row, "docket")
                else:
                    ctx.emit(row, "court")
                prev = row
                continue
            state = "caption"
            pending = [t for t in _drawn_fences(pages[row.page])
                       if t > row.top]

        if state == "caption":
            # THE RECORD BAND OPENS ON THE DATE ROW, at its own rail. That
            # is the only thing that closes the caption: this court sets a
            # party STATUS at the record rail too (walter_j._dirkin), so the
            # rail alone would cut the caption in half.
            if (_RECORD_RAIL[0] <= row.x0 <= _RECORD_RAIL[1]
                    and _EVENT_HEAD.match(text) and _is_date(text)):
                state = "record"
            elif is_typed_rule(text):
                ctx.rule(row.page, typed=True, row=row)
                prev = row
                continue
            else:
                caption.append(text)
                ctx.emit(row, "caption")
                prev = row
                continue

        # THE RECORD BAND. It ends at the first row that leaves its rail —
        # the byline, at 72 ('PER CURIAM') or 108.
        if row.x0 < _RECORD_RAIL_MIN:
            # …except that this court WRAPS its byline. 'The opinion of the
            # court was delivered by' is set on one row and 'SUSSWEIN,
            # J.A.D.' on the next, and only the second is a byline core can
            # parse. Left behind, the introduction is a segment of its own
            # below a claimed headmatter, and core's rule that such a row
            # belongs to the writing opened a PHANTOM WRITING holding
            # nothing but the announcement — on 27 of the 42 records. The
            # announcement is the court naming its author, so it is claimed
            # as one, and the writing opens on the signature itself.
            if _is_intro(text) and _byline_next(stream, idx + 1):
                ctx.emit(row, "author")
            break
        opens = (prev is None or prev.page != row.page
                 or row.top - prev.top > 24.0)
        if opens:
            if date_row is None and _EVENT_HEAD.match(text) and _is_date(text):
                role = "date"
                date_row = text
            elif not counsel and _BENCH.match(text):
                role = "panel"
            elif not counsel and _ORIGIN.match(text):
                role = "lower-court"
            else:
                role = "counsel"
        elif role == "":
            role = "counsel"
        if role == "panel":
            bench.append(text)
        elif role == "lower-court":
            origin.append(text)
        elif role == "counsel":
            counsel.append(text)
        ctx.emit(row, role)
        prev = row

    if stamp_run:
        ctx.drop(stamp_run, "stamp", stamp_only=True)
    if not (caption and dockets and date_row):
        return NOTHING          # not the paper this contract names

    ctx.crit["headmatter_style"] = STYLE_SHOULDER
    ctx.crit["court"] = "Superior Court of New Jersey, Appellate Division"
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    _dates(ctx, date_row)
    if bench:
        line = _norm(" ".join(bench))
        ctx.crit["panel_line"] = line
        ctx.crit["panel"] = _panel(line)
        # …and the roster as the page states it, minus its own label — the
        # printed form and the parsed list are both facts.
        ctx.crit["judges"] = re.sub(r"^Before\s+", "", line, flags=re.I)
    if origin:
        whole = _norm(" ".join(origin))
        ctx.crit["lower_court"] = whole
        below = _lower_dockets(whole)
        if below:
            ctx.crit["lower_court_docket"] = below
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    return ctx.result()


# --------------------------------------------------------------------------
# the parsed forms, each kept beside the printed one
# --------------------------------------------------------------------------

def _dockets(text: str) -> list[str]:
    """The docket numbers in one masthead row. 'A- 1378-23' is one number
    the court spaced out, not two."""
    out: list[str] = []
    for piece in re.split(r"[,;]|\s+and\s+", _norm(text)):
        piece = re.sub(r"(?<=-)\s+|\s+(?=-)", "", _norm(piece)).rstrip(".")
        if piece:
            out.append(piece)
    return out


def _dates(ctx, row: str) -> None:
    """The date row, split at the dash the court divides its two events
    with. Each half is a LABEL and the date it introduces — read in that
    order, never by searching the row for a word."""
    halves = _DASH.split(_norm(row))
    for half in halves:
        mm = _DATE.search(half)
        if not mm or mm.group(1).split()[0].lower().rstrip(".") not in _MONTHS:
            continue
        label = half[:mm.start()].strip().lower().rstrip(":., ")
        value = mm.group(1).rstrip(".")
        if any(label.startswith(w) for w in _HEARD):
            ctx.crit["submitted"] = value
        elif any(label.startswith(w) for w in _DECIDED):
            ctx.crit["decision_date"] = value


def _panel(line: str) -> list[str]:
    """The bench, from 'Before Judges Gooden Brown, Rose and Torregrossa-
    O'Leary.' The LABEL is the closed vocabulary; every name is what stands
    between the separators, so a two-word or hyphenated surname survives."""
    body = re.sub(r"^Before\s+Judges?\s*", "", _norm(line), flags=re.I)
    body = body.rstrip(". ")
    out: list[str] = []
    for piece in re.split(r"\s*,\s*|\s+and\s+", body):
        piece = _norm(piece).rstrip(",. ")
        if piece:
            out.append(piece)
    return out


def _lower_dockets(text: str) -> list[str]:
    """The number(s) the court below gave the case, as the origin states."""
    out: list[str] = []
    for mm in _LOWER_NO.finditer(text):
        for piece in re.split(r"\s+and\s+", mm.group(1)):
            piece = _norm(piece).rstrip(",.; ")
            if piece and piece not in out:
                out.append(piece)
    return out


def _name(ctx, rows: list[str]) -> None:
    """The case's name, built from the party names either side of the FIRST
    pivot — never by joining the caption wholesale, and never past the
    second caption of a consolidated release."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        if is_typed_rule(row):
            continue
        if _PIVOT.match(row):
            if seen_pivot:
                break
            side = right
            seen_pivot = True
            continue
        if _is_status(row):
            if seen_pivot and right:
                break            # the second party's status closes the name
            continue
        side.append(row)
    if seen_pivot and left and right:
        one = _join(left).rstrip(", ")
        two = _join(right).rstrip(", ")
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _join(left + right).rstrip(", ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str) -> None:
        parts = row.parts
        first = parts[0]
        pm = self.pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) \
                if text.strip() else piece
        # EVERY ZONE OF THIS BLOCK IS FLUSH LEFT TO ITS OWN RAIL — the
        # shoulder to 288, the caption to 72, the record band to 144 — and
        # the offset from the body rail is the indent the page prints. A
        # justified counsel line spans 144-467 and reads as CENTRED to a
        # page-wide test, which is the ca5/nj defect: measured that way, 12
        # of a 23-row appearance block render centred and the block comes
        # apart.
        rel = 0.0
        if self.geom:
            rel = max(0.0, min(first.x0 - self.geom.body_x0, pm.width * 0.6))
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, rows: list, kind: str, stamp_only: bool = False) -> None:
        """Record furniture — and record it whole: a claim that consumes a
        line without placing it puts the file in review."""
        parts: list = []
        for row in rows:
            parts.extend(row.stamp if stamp_only else row.stamp + row.parts)
        if not parts:
            return
        text = _norm(" ".join(p.plain for p in
                              sorted(parts, key=lambda p: (p.top, p.x0))))
        if not text:
            return
        self.dropped.append(m.Dropped(
            text=text[:1200],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int, typed: bool = False,
             row: _Row | None = None) -> None:
        # A TYPED rule IS a line of the page and carries its own provenance;
        # a DRAWN one has none and borrows the row above it, because core
        # re-sorts the block by provenance and a rule carrying none sorts to
        # the end.
        pm = self.pages[page]
        if row is not None:
            prov = m.Prov(page, tuple(p.id for p in row.parts))
            self.consumed.update(p.id for p in row.parts)
            span = ("full" if (row.x1 - row.x0) > pm.width * 0.4
                    else "left" if row.x1 < pm.width / 2
                    else "right" if row.x0 > pm.width / 2 else "full")
        else:
            prev = next((i for i in reversed(self.items)
                         if isinstance(i, m.HmLine)), None)
            prov = prev.prov if prev is not None else m.Prov(page)
            span = "left"
        self.items.append(m.Rule(prov=prov, span=span, typed=typed))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
