"""Supreme Court of Iowa ('iowa').

THE CONTRACT — one paper, printed 50 times out of 50: the RULED COVER.

Iowa draws its whole front matter with two rule MEASURES, and the measure
names the section. Both are centred on the page axis to within a tenth of a
point; nothing on this cover is identified by its wording or by its ordinal.

    In the Iowa Supreme Court        the masthead: 14pt bold over a 12pt body
    ─────────────────────────        a SHORT rule (362.9pt) opens the docket…
    No. 25–0366                      …the number this court gave the case…
    Submitted February 11, 2026—     …and when it was heard and released
        Filed May 1, 2026
    ─────────────────────────        …and a second SHORT rule closes it
    Bart Richmond,                   the caption: a party, bold…
       Appellee,                     …its status, roman…
       vs.                           …the pivot…
    Jefferson County Attorney,       …and the other side
       Appellant.
    ═════════════════════════        a LONG rule (470.9pt) closes the caption
        Appeal from the Iowa District Court for Jefferson County,
        Jeffrey Farrell, judge.                      the origin
        A county attorney appeals … Affirmed.        the précis, its
                                                     disposition set BOLD
        McDermott, J., delivered the opinion of      who wrote it and who
        the court, in which all justices joined.     joined — the DELIVERY
        Chauncey T. Moulding, … for appellant.       the appearances
        …
    McDermott, Justice.                              …and the writing starts

THE TWO MEASURES, measured over all 50 records: the SHORT rule is 362.9pt
(x=124.6–487.5) and there are exactly two of them on every page 1; the LONG
rule is 470.9pt (x=70.6–541.5) and there is at least one. Both sit on the
page axis to 0.06pt. A CONSOLIDATION repeats the LONG rule once per extra
caption group — 5th_and_walnut draws two, with the third-party caption
between them — so the caption band is 'everything between the second short
rule and the LAST long rule', and the long rules inside it are group
separators, not the end of anything.

THE CAPTION IS CENTRED, ROW BY ROW, ON THE PAGE AXIS. Measured over the
corpus, every row in the band centres within 0.07pt of it, including the
26-name party list in leonora_streeter and the wrapped corporate roll in
michelle_bunce. Rows long enough to fill the measure read as left-aligned to
a shared test and rendered as indents; the cover DECLARES its alignment
instead, which is the ala rule ('a party list long enough to fill the
measure is still a centred caption row').

BELOW THE LAST LONG RULE THE PAGE LEAVES THE AXIS and sets prose to the body
measure: every paragraph opens at x0=108.0 and every continuation sits at
x0=72.0 — 267 openers and 349 continuations over the corpus, with no third
value. So the prose band is read as PARAGRAPHS, not rows, and each paragraph
is asked once what it is:

  - the ORIGIN, while the band has printed nothing else yet, by a closed
    leader vocabulary ('Appeal from', 'On review from', 'Certified question
    from'). The leaders are anchored at the paragraph's start and the state
    closes at the first paragraph that does not match — without that,
    leroy_cole's précis ('Interlocutory appeal from an order granting the
    defendants' motion to compel arbitration') reads as a second origin.
  - the DELIVERY, by its own landmark: 'delivered the opinion of the court',
    'announced the judgment of the court', or the whole paragraph reading
    'Per curiam.'. It is both things at once — who wrote and who joined —
    and it is tagged `panel`, which is the call ariz's joining summary
    already settled.
  - the APPEARANCES: every paragraph after the delivery, to the byline.
  - the PRÉCIS otherwise, with its DISPOSITION set in bold. A row whose
    every alphanumeric glyph is bold is the disposition; a row that carries
    the précis and the judgment together is the précis (bart_richmond's
    '§ 80F.1(25). Affirmed.'). midwestone prints no précis at all and its
    one paragraph is bold throughout — disposition, whole.

THE READER ENDS AT THE BYLINE, and the byline is three things at once: it
parses, it stands at the body rail (x0=72.0, where no paragraph opens), and
it is BOLD (no appearance in the corpus is). All three are needed because
melinda_williams prints 'Per curiam.' in the DELIVERY slot — indented, roman
— above its appearances, and signs the writing 'Per Curiam.' at the rail on
the next page. Keyed on the parse alone, the reader stopped at the delivery
line and the appearances were swallowed into the per-curiam opinion.

WHERE THERE IS NO DELIVERY PARAGRAPH THE PROSE BAND IS NOT CLAIMED. When
the justices split 3–3 the appeal is 'affirmed by operation of law' under
Iowa Code § 602.4107 and the court says so in an unsigned order printed
straight under the closing rule (patty_a._thorington) — there is no
delivery, no appearance, and no byline anywhere in the document. That band
is the WRITING, not headmatter, so the claim stops at the closing rule and
core assembles what follows. The cover above it is read exactly as it is on
every other record.

A record that does not draw both measures on page 1, or whose first row is
not the masthead, is not this paper and gets NOTHING.

iowa's profile stays in the shared table in `courts/__init__.py`; this file
owns the reader only.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

STYLE_COVER = "ruled cover"

# ---- iowa's declared facts (measured over all 50 records) ----------------
# THE TWO MEASURES. 100 short rules over the corpus, every one 362.9pt wide
# at x=124.6–487.5; 51 long rules, every one 470.9pt at x=70.6–541.5. Both
# centre on the 612pt page's axis to 0.06pt.
_SHORT_MEASURE = (348.0, 378.0)
_LONG_MEASURE = (455.0, 488.0)
_AXIS_TOL = 6.0
# THE MASTHEAD: 14pt bold over a 12pt body — the only row on the cover set
# above body size.
_MASTHEAD_SIZE = 13.0
# THE PROSE BAND'S OWN GRID: openers at x0=108.0, continuations at x0=72.0,
# with no third value anywhere in the corpus. Half of 36 separates them.
_PARA_INDENT = 18.0
_RAIL_TOL = 2.0
# HOW FAR THE COVER MAY RUN. patrick_willhoite carries eight appearances
# onto page 2 and signs on page 3; nothing in the corpus needs a fifth page.
_MAX_PAGES = 5

# 'No. 25–0366' / 'No. 24–1886' — this court's own number, en-dashed.
_DOCKET = re.compile(r"^Nos?\.\s*(\d{2}\s*[-‑–—]\s*\d{3,4}[A-Z]?)\.?$")
# 'Submitted February 11, 2026—Filed May 1, 2026' — the cover states both
# dates in one row, joined by an em dash, each under its own label.
_SUBMITTED_FILED = re.compile(
    r"^Submitted\s+(.+?)\s*[-‑–—]\s*Filed\s+(.+?)\.?$", re.I)
# 'Scott County No. LACE 133201' — where the cover prints the number the
# court BELOW gave the case instead of the hearing dates.
_LOWER_NO = re.compile(r"\bNos?\.\s*(\S.*)$")

# THE ORIGIN LEADERS: a closed vocabulary of the ways this court states
# where a case came from, anchored at the paragraph's start. Never a court
# NAME — 'Appeal from the Iowa District Court for Polk County' and 'Appeal
# from the Iowa Workers' Compensation Commissioner' are the same leader.
_ORIGIN_LEADERS = (
    "appeal from", "appeals from", "on appeal from",
    "appeal and cross-appeal from", "cross-appeal from",
    "on review from", "review from", "on further review from",
    "certified question from", "certified questions from",
    "on certified question from", "on certiorari to",
    "on writ of certiorari to", "certiorari to",
)
# WHO TRIED IT, as the origin's last comma group says. A closed bench
# vocabulary — the ROLE is read, never the name.
_BENCH_TAIL = re.compile(
    r"\b(?:chief\s+)?(?:district\s+)?(?:associate\s+)?(?:probate\s+)?"
    r"(?:senior\s+)?(?:business\s+specialty\s+court\s+)?judges?$", re.I)

# THE DELIVERY PARAGRAPH'S OWN LANDMARK. 48 of 50 records print the first
# form; willhoite adds the second for a fractured court; melinda_williams
# prints the third and nothing else.
_DELIVERED = re.compile(
    r"delivered the opinion of the court"
    r"|announced the judgment of the court", re.I)
_PER_CURIAM = re.compile(r"^per\s+curiam\.?$", re.I)

# THE BENCH ABBREVIATIONS Iowa sets in its delivery line, and the roster
# grammar that reads them: one or more surnames, then the abbreviation that
# names their office. Read as prose the same line yields a judge called
# 'the' and another called 'all'.
_ROSTER = re.compile(
    r"([A-Z][A-Za-z’'\-]+"
    r"(?:\s*,\s*(?:and\s+)?[A-Z][A-Za-z’'\-]+)*"
    r"(?:\s+and\s+[A-Z][A-Za-z’'\-]+)?)"
    r"\s*,\s*(C\.J\.|JJ\.|J\.)")
_AUTHOR = re.compile(r"^([A-Z][A-Za-z’'\-]+)\s*,\s*(?:C\.J\.|J\.)\s*,")

# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Iowa stacks its roles with hyphens ('Third-Party-Plaintiff
# Appellant', 'Intervenor-Appellee').
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "movant",
    "amicus", "amici", "curiae", "cross", "third", "party", "and", "the",
    "co", "counter", "claimant", "guardian", "conservator", "trustee",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row — pdfio splits a justified row at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold",
                 "all_bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = any(bool(p.bold) for p in self.pieces)
        self.all_bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def chars(self) -> list:
        out = []
        for p in self.pieces:
            out.extend(p.chars)
        return out

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + " " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order."""
    rows: list = []
    for pm in model.pages[:max_pages]:
        buckets: dict = {}
        order: list = []
        loose: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            if line.row is not None:
                if line.row not in buckets:
                    buckets[line.row] = []
                    order.append(line.row)
                buckets[line.row].append(line)
            else:
                loose.append(line)
        groups = [buckets[k] for k in order]
        # pdfio leaves `row` unset on pages it did not have to split; fall
        # back to a baseline test, which is what `row` encodes anyway.
        for line in loose:
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
# the page's own marks
# --------------------------------------------------------------------------

def _rules(pm, measure) -> list:
    """The tops of this page's rules in one MEASURE, on the page axis."""
    out = []
    for r in pm.h_rules:
        if not (measure[0] <= r.width <= measure[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _AXIS_TOL:
            continue
        out.append(r.top)
    return sorted(out)


# --------------------------------------------------------------------------
# what the bands say
# --------------------------------------------------------------------------

def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w for w in re.split(r"[\s/,\-]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _case_name(ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the
    caption's own pivot row — never by joining the caption wholesale."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for text in rows:
        if _is_pivot(text):
            if seen_pivot:
                break                 # a consolidation: the LEAD case only
            side = right
            seen_pivot = True
            continue
        if _is_status(text):
            continue
        side.append(text)
    if seen_pivot and left and right:
        one = _norm(" ".join(left)).rstrip(",; ")
        two = _norm(" ".join(right)).rstrip(",; ")
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _norm(" ".join(left + right)).rstrip(",; ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


def _origin_leader(text: str) -> bool:
    low = _norm(text).lower()
    return any(low.startswith(lead) for lead in _ORIGIN_LEADERS)


def _read_origin(ctx, text: str) -> None:
    """'Appeal from the Iowa District Court for Wayne County, Dustria A.
    Relph (motion to quash) and Elisabeth Reynoldson (summary judgment and
    trial), judges.' — the tribunal, who tried it, and the office they hold.

    The court's OWN separator is the comma, and the last group is the bench
    ROLE; what stands between it and the tribunal is the judge. A statement
    with no bench group ('On review from the Iowa Court of Appeals.') names
    no judge and is recorded whole as history."""
    flat = _norm(text).rstrip(".")
    parts = [p.strip() for p in flat.split(",") if p.strip()]
    if len(parts) >= 3 and _BENCH_TAIL.search(parts[-1]):
        court = parts[0]
        judge = ", ".join(parts[1:-1])
    elif len(parts) == 2 and _BENCH_TAIL.search(parts[-1]):
        court, judge = parts[0], None
    else:
        court, judge = flat, None
    for lead in _ORIGIN_LEADERS:
        if court.lower().startswith(lead):
            court = court[len(lead):].strip()
            break
    court = re.sub(r"^the\s+", "", court, flags=re.I).strip()
    if court:
        prev = ctx.crit.get("lower_court")
        ctx.crit["lower_court"] = f"{prev}; {court}" if prev else court
    if judge and not ctx.crit.get("lower_court_judge"):
        ctx.crit["lower_court_judge"] = judge


def _roster(line: str) -> list:
    """The bench the delivery line names, in the order it names them."""
    out: list[str] = []
    for names, _office in _ROSTER.findall(line):
        for name in re.split(r"\s*,\s*|\s+and\s+", names):
            # 'Waterman, Oxley, and McDermott' — the comma split runs first
            # and leaves the conjunction glued to the last name.
            name = re.sub(r"^and\s+", "", name.strip().strip(","))
            if name and name not in out:
                out.append(name)
    return out


def _bold_tail(rows: list) -> str:
    """The DISPOSITION: the run of bold glyphs the précis closes on.

    Iowa sets its judgment in bold at the end of the same paragraph that
    states the précis ('… under Iowa Code § 80F.1(25). **Affirmed.**'), so
    the disposition is a run inside a row, not a row of its own. Walked back
    from the end, it stops at the first roman ALPHANUMERIC glyph;
    punctuation is routinely left roman inside a bold passage and does not
    vote."""
    chars: list = []
    for i, row in enumerate(rows):
        if i:
            chars.append((" ", True))
        for c in row.chars:
            t = c.get("text") or ""
            if not t:
                continue
            chars.append((t, "Bold" in (c.get("fontname") or "")))
    keep: list[str] = []
    for t, bold in reversed(chars):
        if any(ch.isalnum() for ch in t) and not bold:
            break
        keep.append(t)
    tail = _norm("".join(reversed(keep)))
    # The walk back stops on a roman LETTER, so it carries the roman
    # punctuation that stood between the précis and the judgment ('). '
    # before 'Affirmed.'); the judgment opens on its own first word.
    tail = re.sub(r"^[^0-9A-Za-z]+", "", tail).rstrip()
    return tail.rstrip(".") if any(ch.isalpha() for ch in tail) else ""


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, body_x0: float):
        self.body_x0 = body_x0
        self.items: list = []
        self.consumed: set = set()
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str = "L") -> None:
        rel = 0.0
        if align == "L":
            rel = round(row.x0 - self.body_x0, 1)
            if abs(rel) < 0.5:
                rel = 0.0
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.all_bold, rel=rel, role=role))
        self.consumed.update(row.ids)

    def rule(self, page: int) -> None:
        # A RULE RENDERS WHERE THE PAGE DRAWS IT. Core sorts the block by
        # each item's source position, and an item with no line provenance
        # inherits the row it stands beside — so a rule carries none and
        # keeps its emitted place.
        self.items.append(m.Rule(prov=m.Prov(page), span="full"))

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": [], "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


@decider("headmatter.read", court="iowa")
def read_headmatter_iowa(model, geom, **_):
    """Read Iowa's ruled cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0

    # THE DISPATCH: both measures, on the axis, on page 1.
    shorts = _rules(page1, _SHORT_MEASURE)
    longs = _rules(page1, _LONG_MEASURE)
    if len(shorts) < 2 or not longs:
        return NOTHING

    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if len(rows) < 6:
        return NOTHING
    head = rows[0]
    if not (head.page == 1 and head.top < shorts[0]
            and head.size >= _MASTHEAD_SIZE and head.bold):
        return NOTHING

    ctx = _Ctx(body_x0)
    parser = BylineParser(get_profile("iowa").byline)

    # ---- the cover, down to the rule that closes the caption -------------
    # THE RULES ARE PART OF THE BLOCK, so they walk in the stream with the
    # rows and render where the page draws them.
    cap_open, cap_close = shorts[1], longs[-1]
    stream = [(r.top, 0, r) for r in rows
              if r.page == 1 and r.top <= cap_close]
    stream += [(t, -1, None) for t in shorts[:2] + longs]
    stream.sort(key=lambda s: (s[0], s[1]))

    caption: list[str] = []
    groups: list[list] = [[]]         # one per caption the cover carries
    dockets: list[str] = []
    dated = False
    for top, kind, row in stream:
        if kind < 0:
            ctx.rule(1)
            # A LONG RULE INSIDE THE CAPTION BAND SEPARATES CASES. 5th_and_
            # walnut sets the appeal and the third-party action under one
            # docket, each with its own parties; joined, the case name read
            # '… v. City of Des Moines, City of Des Moines'.
            if cap_open < top < cap_close:
                groups.append([])
            continue
        if top < shorts[0]:                           # the masthead band
            ctx.crit.setdefault("court", row.text)
            ctx.emit(row, "court", "C")
            continue
        if top < cap_open:                            # the fenced docket
            mm = _DOCKET.match(row.text)
            if mm:
                dockets.append(_norm(mm.group(1)))
                ctx.emit(row, "docket", "C")
                continue
            sf = _SUBMITTED_FILED.match(row.text)
            if sf:
                ctx.crit.setdefault("submitted", _norm(sf.group(1)))
                ctx.crit.setdefault("decision_date", _norm(sf.group(2)))
                dated = True
                ctx.emit(row, "date", "C")
                continue
            # THE COURT BELOW'S OWN NUMBER, where the cover prints it in
            # place of the hearing dates ('Scott County No. LACE 133201').
            ln = _LOWER_NO.search(row.text)
            if ln:
                ctx.crit.setdefault("lower_court_docket",
                                    []).append(_norm(ln.group(1)))
                ctx.emit(row, "lower-court", "C")
                continue
            return NOTHING            # the fenced band holds nothing else
        caption.append(row.text)                      # the caption band
        groups[-1].append(row.text)
        ctx.emit(row, "caption", "C")
    if not (dockets and caption):
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_COVER
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _case_name(ctx, next((g for g in groups if g), caption))

    # ---- the prose band, read as paragraphs ------------------------------
    # THE BAND IS SET TO THE BODY MEASURE, so its unit is the paragraph:
    # openers at x0=108.0, continuations at x0=72.0, no third value in the
    # corpus. A BYLINE opens no paragraph — it stands at the rail — so it is
    # cut out into one of its own, or it joins the appearance above it and
    # the reader has no place to stop.
    band = [r for r in rows if (r.page > 1 or r.top > cap_close)]
    paras: list[list] = []
    signed: list[bool] = []
    for row in band:
        by = (abs(row.x0 - body_x0) <= _RAIL_TOL and row.bold
              and parser.parse(row.text) is not None)
        if by or row.x0 >= body_x0 + _PARA_INDENT or not paras:
            paras.append([row])
            signed.append(by)
        else:
            paras[-1].append(row)
    texts = [_norm(" ".join(r.text for r in para)) for para in paras]
    # THE DELIVERY PARAGRAPH IS THE PROSE BAND'S OWN LANDMARK, and without
    # one this band is a writing, not headmatter (the evenly-divided order).
    delivery = next(
        (i for i, t in enumerate(texts)
         if _DELIVERED.search(t) or _PER_CURIAM.match(t)), None)
    end = next((i for i in range(len(paras))
                if signed[i] and delivery is not None and i > delivery), None)
    if delivery is None or end is None:
        # THE COVER ALONE. The claim stops at the rule that closes the
        # caption and core assembles what follows, which is what the page
        # means where it prints no delivery line: patty_a._thorington's
        # unsigned 'affirmed by operation of law' order is the WRITING.
        return ctx.result()

    state = "origin"
    counsel: list[str] = []
    summary_rows: list = []
    for i in range(end):
        para, text = paras[i], texts[i]
        if i == delivery:
            ctx.crit["panel_line"] = text
            names = _roster(text)
            if names:
                ctx.crit["panel"] = names
            for row in para:
                ctx.emit(row, "panel")
            state = "counsel"
            continue
        if state == "counsel":
            counsel.append(text)
            for row in para:
                ctx.emit(row, "counsel")
            continue
        if state == "origin" and _origin_leader(text):
            _read_origin(ctx, text)
            for row in para:
                ctx.emit(row, "lower-court")
            continue
        state = "summary"
        # A ROW SET BOLD THROUGHOUT IS THE JUDGMENT, not the précis.
        for row in para:
            ctx.emit(row, "disposition" if row.all_bold else "summary")
        summary_rows.extend(para)

    if summary_rows:
        tail = _bold_tail(summary_rows)
        if tail:
            ctx.crit["disposition"] = tail
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    return ctx.result()
