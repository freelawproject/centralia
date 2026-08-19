"""Supreme Court of Connecticut ('conn').

Everything unique to conn lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py (with `front_matter=('syllabus',)`).

THE CONTRACT — Connecticut publishes the REPORTER'S advance release, and it
reads like a page of the bound volume rather than like a slip. Page 1 is
nothing but the Reporter's notice; the paper starts on page 2 under a running
head fenced by two rules.

    ┌─ page 1 ───────────────────────────────────────────────────────────┐
    │      ****************************************************           │
    │      The "officially released" date that appears near the …          │  the notice,
    │      All opinions are subject to modification and technical …       │  the whole
    │      … the latest version is to be considered authoritative.        │  page
    └────────────────────────────────────────────────────────────────────┘
    ┌─ page 2 ───────────────────────────────────────────────────────────┐
    ├──────────────────────── rule ──────────────────────────────────────┤
    │                       State v. Bard             8pt running head   │
    ├──────────────────────── rule ──────────────────────────────────────┤
    │          STATE OF CONNECTICUT v. KEVIN BARD     11pt — the caption │
    │                       (SC 21016)                11pt — the docket  │
    │        Mullins, C. J., and McDonald, D'Auria, Ecker,               │
    │            Alexander, Dannehy and Bright, Js.    8pt — the panel   │
    │                        Syllabus                  8pt — the         │
    │ The defendant was charged with … (8pt)                Reporter's   │
    │                                                                    │
    │      Argued March 5—officially released May 5, 2026   the dates    │
    │                    Procedural History                              │
    │     Substitute information charging the defendant with … (11pt)    │
    └────────────────────────────────────────────────────────────────────┘

THE TYPE SAYS WHOSE WORDS THEY ARE. The court's own text — the caption, the
docket, the opinion — is 11pt; everything the REPORTER adds around it is 8pt:
the running head, the panel roster, the syllabus and its heading, the
argued/released line, the 'Procedural History' heading and the footnotes.
That one measurement is the whole parser, and it is why nothing here is keyed
to a page number or a row index.

WHAT FOLLOWS THE PRECIS IS STILL THE BLOCK. Between the syllabus and the
writing the Reporter prints a 'Procedural History' heading, one paragraph of
history closing on the court's disposition, and then the appearances:

    Procedural History
        Action challenging, inter alia, the defendant's determination that
        certain revisions to the town charter … from which the plaintiff
        appealed to this court. Reversed; further proceedings.
        John B. Kennelly, for the appellant (plaintiff).
        Jesse A. Langer, with whom, on the brief, were Rich-
    ard D. Carella and Brian C. Hoeing, for the appellee (defendant).
    Opinion

All of it is headmatter, and left unclaimed it was not merely untagged — core
made the caption, the precis, the history and the appearances into a writing
of their own, an `order` of 69 blocks standing ahead of the real majority.
The history and the appearances are prose on the SAME indent, so what tells
them apart is that the history is ONE paragraph: paragraph openings are
counted, and the first is the history while every one after it is an
appearance. The court's closing disposition sentence is not relied on.

THE CLAIM MUST BE CONTIGUOUS, and that is why the syllabus IS claimed here.
Connecticut prints no byline above its précis, so core opens a writing on the
CAPTION ROW itself — measured on `amadasun_v._armstrong_town_clerk_of_south_
windsor`, op0 began at 'HARRISON AMADASUN v. BONNIE ARMSTRONG,' on page 2 —
and core's bisection invariant then pulls every row inside that writing's span
back into it. A reader that claimed the caption and skipped the précis had all
four of its rows absorbed and published an EMPTY headmatter on 36 of 50
records. So the walk runs from the caption to the 'Procedural History'
heading without a gap, and the précis rows take the `syllabus` role — the
court's front matter read in place, exactly as kan's 852 numbered points are.

'Procedural History' HEADS THE COURT'S OWN TEXT. The 11pt prose beneath it is
the history the court writes, so the heading is where the block ends and the
paper begins.

THE OTHER PAPER: THE BOUND REPORTER. Connecticut publishes the SAME case
twice, and the companion file (the `_1` / `_2` suffix) is the CONNECTICUT LAW
JOURNAL printing — an extract of the bound volume, with no Reporter's notice
and no page 1 of its own. It reads the same from the caption down; what
differs is everything ABOVE the caption, which is three running heads:

    ┌─ page 1 (of an extract that begins at the volume's page 151) ───────┐
    │ February 10, 2026   CONNECTICUT LAW JOURNAL      Page 3   7.5pt     │ the Journal's
    │   354 Conn. 151        FEBRUARY, 2026            151     10.8pt     │ three heads
    │           Del Rio v. Amazon.com Services, Inc.            8pt       │
    │      JAVIER DEL RIO ET AL. v. AMAZON.COM                 11pt       │ the caption
    │             SERVICES, INC., ET AL.                                  │
    │                   (SC 21109)                             11pt       │ the docket
    │        Mullins, C. J., and McDonald, D'Auria, Ecker,       8pt       │ the panel
    │            Alexander, Dannehy and Bright, Js.                       │
    │                      Syllabus                             8pt       │
    └────────────────────────────────────────────────────────────────────┘

THE MIDDLE HEAD CARRIES THE CITATION AND IS STILL A HEAD. '354 Conn. 151' is
the reporter citation — volume, reporter, first page — and it is printed on
EVERY page of the extract, swapping rails with the folio as the volume's
recto and verso alternate. Printed identically thirty times it cannot be this
page's content, so the row is dropped as a running head and the cite it
carries is kept as `criteria.citation`, the field the model added for a
court-printed cite. The row is FOUND by repetition, not by wording: the same
cite-shaped line, at the same baseline, on two or more pages. That baseline
then names the row on every page, which is how the bare folio ('152') that
core's furniture finder cannot see — it stands inside the body measure — is
still accounted for.

WHICH PAPER THIS IS, IS A LANDMARK QUESTION. The slip opens with the
asterisk rule of the Reporter's notice; the Journal extract prints the
reporter's running head. Neither present, the reader returns NOTHING and
core's generic walk has it. The two branches then share ONE walk, because
from the caption down the two papers are the same paper.

A SLIP WITH NO CAPTION IS A SEPARATE OPINION, NOT A FAILURE. Four records
here are the advance release of a dissent or a concurrence alone: the notice
page, then a byline on page 2 and nothing else. There is no caption, no
docket and no precis to read, and the whole of their headmatter is the
notice. The claim is the notice, recorded as dropped — which is what leaves
the render honest rather than leaving the asterisk rule standing alone as the
document's entire front matter.

THE NOTICE NAMES ITSELF. It opens with a rule of asterisks and every line of
it stands in the Reporter's measure (x0 174-186) on page 1 alone. It is
dropped, not tinted: none of it is the court's writing, and it is printed
identically on all 50 records.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MAX_PAGES = 6
_AXIS_TOL = 30.0        # the Reporter's measure is narrow and centred
# The court's own type against the Reporter's. Measured over 50 records:
# 11pt for the court, 8pt for everything the Reporter adds, 10pt for the
# asterisk rule that opens the notice.
_COURT_SIZE_MIN = 10.5

_ASTERISKS = re.compile(r"^\*{6,}$")
# '(SC 21016)' / '(AC 46012)' / '(SC 21016, SC 21017)'
_DOCKET = re.compile(r"^\((?:SC|AC)\s*\d+[\s,;]*(?:(?:SC|AC)?\s*\d+)*\)$", re.I)
# The panel roster: a list of names closing in 'Js.' or 'J.'
_ROSTER = re.compile(r"\bJs?\.\s*$")
_SYLLABUS_HEAD = re.compile(r"^Syllabus$", re.I)
# 'Argued March 5—officially released May 5, 2026'
#
# THE LIGATURE IS BROKEN IN THE BOUND PRINTING. The Journal extract's fonts
# set 'ffi' as a single glyph and the extractor recovers it as 'offi cially'
# ('fi led', 'certifi ed', 'affi rming' likewise) — measured on all eight
# extracts. The slip's fonts do not, so the same landmark needs both
# spellings; written with only the closed one, the released date went
# unrecorded on every extract and the row read as 'syllabus' or as 'panel'
# instead of as the date it is.
_OFFICIALLY = r"of\s?f\s?i\s?c\s?ially"
_ARGUED_RELEASED = re.compile(
    r"^(?:Argued|Submitted)\s+(.+?)[—–-]\s*" + _OFFICIALLY
    + r"\s+released\s+(.+)$", re.I)
_RELEASED_ONLY = re.compile(
    r"^" + _OFFICIALLY + r"\s+released\s+(.+)$", re.I)
# A FOOTNOTE MARK RIDES THE DATE. The Reporter stars the released date where
# it notes a release-date correction ('February 17, 2026*'), and the star is
# not part of the date.
_DATE_MARK = "*\u2020\u2021\u2217\u204e\ufe61\uff0a "
_PIVOT = re.compile(r"\sv\.\s", re.I)
# 'Procedural History' heads the band beneath it and belongs to that band.
_HISTORY_HEAD = re.compile(r"^Procedural History$", re.I)
# 'Opinion' is the paper naming ITSELF, and it is where the writing begins.
_OPINION_HEAD = re.compile(r"^Opinion$", re.I)
# The bound volume's page number, standing alone above the block.
_FOLIO = re.compile(r"^\d{1,4}$")
# A paragraph OPENS a step in from the Reporter's rail: 184.0 against 174.0.
_INDENT_MIN = 6.0

# ---- the bound volume's running head ---------------------------------
# '354 Conn. 151' / '234 Conn. App. 56' — volume, reporter, first page. A
# SHAPE, not a name: three tokens, two of them numbers, the middle one an
# abbreviation. It is accepted as a running head only where the SAME line
# stands at the SAME baseline on two or more pages, which is the measurement
# that separates a head from a citation that happens to fill a short line.
_REPORTER_CITE = re.compile(
    r"^(\d{1,4})\s+([A-Z][A-Za-z]{1,11}\.(?:\s*[A-Z][A-Za-z]{1,11}\.)?)"
    r"\s+(\d{1,4})$")
# Every head on these pages stands in the top quarter of the sheet: 108.5,
# 150.5 and 169.4 against 792. The body's own first row is at 187.5 (0.237),
# so the zone alone does not identify a head — the repetition does.
_HEAD_ZONE = 0.25
_HEAD_TOL = 1.5         # the head's baseline is invariant to a tenth
# The head is a SHORT row: 71pt of a 264pt measure. A full-measure line of
# prose can never be one, whatever it says.
_HEAD_MEASURE_MAX = 0.5

# THE PANEL, printed and parsed. The roster runs over two rows and only the
# LAST of them closes in 'Js.', so the printed form is the rows joined. The
# bench titles are a closed vocabulary — 'C. J.', 'J.', 'Js.' — and taking
# them out leaves the names.
_BENCH_TITLE = re.compile(r",?\s*(?:C\.\s*J\.|Js\.|J\.)(?=,|\s|$)")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


def _digitless(text: str) -> str:
    """A repetition key: the line without its numbers, so a head that counts
    the volume's pages ('354 Conn. 151' / '152') still matches itself."""
    return "".join(c for c in text if not c.isdigit()).strip()


def _running_heads(model, body_x0: float, right_x1: float):
    """`(baselines, citation)` — the tops the paper prints a head on, and the
    reporter citation one of them carries. `(set(), None)` where there is no
    reporter head, which is what says this is not the Journal's extract.

    A HEAD IS FOUND BY REPETITION, never by wording: the same line, less its
    digits, standing at the same baseline in the top zone of two or more
    pages. That is the only test that reaches all three of this paper's
    heads, because core's own furniture finder reads the pages against the
    document's dominant type and a three-page extract is dominated by the
    Reporter's 8pt — on `walton_v._walton_1` it takes the folio and leaves
    the Journal's date line and the case-name line standing.

    The citation head is the one whose line is the reporter's own shape —
    volume, reporter, page — inside half the measure. It is a head like the
    others; what makes it worth naming is that the cite is a criterion.
    """
    measure = max(right_x1 - body_x0, 1.0)
    seen: dict = {}
    for pm in model.pages:
        for line in pm.lines:
            text = _norm(line.plain)
            if not text or line.top > pm.height * _HEAD_ZONE:
                continue
            key = (round(line.top, 1), _digitless(text))
            pages, _t, narrow = seen.get(key, (set(), text, False))
            pages.add(pm.number)
            seen[key] = (pages, _t,
                         narrow or (_REPORTER_CITE.match(text) is not None
                                    and line.x1 - line.x0
                                    <= measure * _HEAD_MEASURE_MAX))
    tops = {t for (t, _k), (pgs, _x, _n) in seen.items() if len(pgs) >= 2}
    cite = None
    best = 1
    for (top, _k), (pgs, text, narrow) in seen.items():
        if narrow and len(pgs) > best:
            cite, best = text, len(pgs)
    return (tops, cite) if cite else (set(), None)


def _panel_names(text: str) -> list[str]:
    """The roster's names, the bench titles taken out."""
    out = []
    for part in re.split(r",|\band\b", _BENCH_TITLE.sub(",", text)):
        name = part.strip(" .,;")
        if name:
            out.append(name)
    return out


@decider("headmatter.read", court="conn")
def read_headmatter_conn(model, geom, **_):
    """Read Connecticut's block — the advance release slip or the Law
    Journal's bound extract, one walk under two landmarks — or NOTHING."""
    if len(model.pages) < 2:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 174.0)
    right_x1 = (geom.right_x1 if geom and geom.right_x1 else 438.6)
    finder = FurnitureFinder(model, body_x0, body_size)

    ctx = _Ctx()
    # ---- WHICH OF THE TWO PAPERS IS THIS? -------------------------------
    # The slip opens on the Reporter's notice, whole, on page 1. The Law
    # Journal extract opens on the bound volume's running head. Each is a
    # landmark the paper always prints; a record printing neither is not
    # Connecticut's and core's walk has it.
    #
    # THE NOTICE IS ITS RULE. It was first written as 'the asterisk rule OR a
    # line of the notice's wording', and the wording included 'Connecticut
    # Law Journal' — which is what the OTHER paper prints across the top of
    # every page. On `walton_v._walton_1` that matched the running head in
    # the first row of page 1 and the cascade below it then dropped the
    # caption, the panel, the history, the appearances and the first
    # thirty-five lines of the per curiam opinion as 'notice'. The landmark
    # is the RULE, and the notice is what follows it.
    opened = False
    for group in _rows(model.pages[0], finder):
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        if not opened and not _ASTERISKS.match(text):
            continue
        opened = True
        ctx.drop(group, "notice")
    slip = opened
    heads: set = set()
    if not slip:
        heads, cite = _running_heads(model, body_x0, right_x1)
        if not cite:
            return NOTHING      # neither notice nor reporter head
        ctx.crit["citation"] = cite
    # The slip's own paper begins on the page AFTER the notice; the extract
    # begins on its first.
    _first = 1 if slip else 0

    # ---- the paper's own opening -----------------------------------------
    # THE CAPTION is the first row the COURT sets — 11pt, centred, carrying
    # the pivot — anywhere in the pages after the notice. Found by landmark,
    # never by page: a consolidated record runs the notice onto a second
    # page.
    # THE BLOCK STARTS AT THE TOP OF ITS PAGE. The page is the first one
    # after the notice that carries the court's docket, and the block's first
    # row is that page's first row — the running head above it is furniture
    # and is already gone.
    #
    # This was first written as 'the first 11pt centred row carrying the
    # pivot, in caps', and the caps test is WRONG: the court sets the pivot
    # lower-case, so 'HARRISON AMADASUN v. BONNIE ARMSTRONG,' is not equal to
    # its own upper-case form. The caption's first line therefore went
    # unclaimed, core opened a writing ON it, and that writing's span then
    # swallowed all 64 rows this reader had claimed — an empty headmatter on
    # 23 of 50 records, with the claim intact and every row 'reunited' into
    # the opinion. A claim with a hole at the top is worse than no claim.
    caption_pm = None
    for pm in model.pages[_first:_MAX_PAGES]:
        if any(_DOCKET.match(_norm(" ".join(l.plain for l in g)))
               for g in _rows(pm, finder)):
            caption_pm = pm
            break
    if caption_pm is None:
        # NO DOCKET IS NOT ALWAYS A MISREADING. On the slip it means the
        # paper is a separate opinion released alone: notice, then a byline.
        # The notice is the whole of its headmatter and the claim is that,
        # recorded as dropped. On the extract it would mean a shape this
        # reader has not measured, so the claim is withdrawn.
        return ctx.result() if slip else NOTHING

    caption: list[str] = []
    history: list[str] = []
    paras = 0
    stopped = False
    band = "caption"        # caption | syllabus | history | counsel
    panel: list[str] = []
    pages = [pm for pm in model.pages[caption_pm.number - 1:_MAX_PAGES]]
    for pm in pages:
        for group in _rows(pm, finder):
            text = _norm(" ".join(l.plain for l in group))
            if not text:
                continue
            first = group[0]
            # THE HEADS THE CLAIM INHERITS. Core's furniture finder takes
            # the Journal's date/name/folio band and the case-name head, but
            # not the citation head — the row stands INSIDE the body measure
            # and its folio changes on every page. Named by its measured
            # baseline and recorded, never skipped: an unrecorded row a
            # reader passed over comes back as residual.
            if any(abs(first.top - t) <= _HEAD_TOL for t in heads):
                ctx.drop(group, "running-head")
                continue
            if _FOLIO.match(text):
                ctx.drop(group, "folio")
                continue
            if _OPINION_HEAD.match(text):
                # THE PAPER NAMES ITSELF. Everything below is the writing.
                ctx.emit(group, "title")
                stopped = True
                break
            if _HISTORY_HEAD.match(text):
                # A HEADING THAT NAMES A BAND belongs to that band, so this
                # is read as `lower-court` and not as `title`.
                band = "history"
                paras = 0
                ctx.emit(group, "lower-court")
                continue
            if band in ("history", "counsel"):
                # BOTH BANDS ARE PROSE ON THE SAME INDENT, and what separates
                # them is that the history is ONE paragraph. Measured on
                # `amadasun_v._armstrong…` and `state_v._bard`: every
                # paragraph here opens at 184.0 and runs over at 174.0, the
                # first is the procedural history (closing on the court's
                # disposition — 'Reversed; further proceedings.', 'Affirmed.')
                # and every paragraph after it is one appearance. Counting
                # paragraph OPENINGS is what tells them apart; the closing
                # sentence's wording is not relied on.
                if first.x0 >= body_x0 + _INDENT_MIN:
                    paras += 1
                if paras >= 2:
                    band = "counsel"
                if band == "counsel":
                    ctx.emit(group, "counsel", centre=False)
                else:
                    history.append(text)
                    ctx.emit(group, "lower-court", centre=False)
                continue
            both = _ARGUED_RELEASED.match(text) or _RELEASED_ONLY.match(text)
            if both:
                g = both.groups()
                if len(g) == 2:
                    ctx.crit.setdefault("submitted",
                                        _norm(g[0]).rstrip(_DATE_MARK))
                    ctx.crit.setdefault("decision_date",
                                        _norm(g[1]).rstrip(_DATE_MARK))
                else:
                    ctx.crit.setdefault("decision_date",
                                        _norm(g[0]).rstrip(_DATE_MARK))
                ctx.emit(group, "date")
                continue
            if _SYLLABUS_HEAD.match(text):
                band = "syllabus"
                ctx.emit(group, "syllabus")
                continue
            if _DOCKET.match(text):
                _dk = [t.strip() for t in
                       text.strip("()").replace(";", ",").split(",")
                       if t.strip()]
                ctx.crit.setdefault("docket_number", _dk[0])
                if _dk[1:]:
                    ctx.crit.setdefault("other_dockets", _dk[1:])
                ctx.emit(group, "docket")
                continue
            if band == "syllabus":
                ctx.emit(group, "syllabus", centre=False)
                continue
            if _ROSTER.search(text) and (first.size or 0.0) < _COURT_SIZE_MIN:
                if band == "caption":
                    panel.append(text)
                ctx.emit(group, "panel")
                continue
            if (first.size or 0.0) >= _COURT_SIZE_MIN:
                caption.append(text)
                ctx.emit(group, "caption")
                continue
            # A ROSTER'S FIRST LINE ends in a comma, not in 'Js.' — it is
            # still the roster, and it is the only other thing the Reporter
            # sets in this band above the précis.
            # THE ROSTER IS READ IN THE CAPTION BAND AND NOWHERE ELSE.
            # This is the walk's last resort, so anything the Reporter sets
            # in 8pt that no landmark claimed arrives here; taking it into
            # the panel criterion put 'Argued December 3, 2025—offi cially
            # released March 10, 2026' among walton's justices.
            if band == "caption":
                panel.append(text)
            ctx.emit(group, "panel")
        if stopped:
            break

    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption[:4])
    if panel:
        # THE PRINTED FORM BESIDE THE PARSED FORM. The roster spans two rows
        # and only the second closes in 'Js.', so the line is the rows
        # joined — recorded whole as `judges` and `panel_line`, and split on
        # the bench titles into `panel`.
        line = " ".join(panel)
        ctx.crit.setdefault("panel_line", line)
        ctx.crit.setdefault("judges", line)
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    if history:
        ctx.crit.setdefault("history", " ".join(history)[:2000])
    # THE GATE COMES LAST, and it judges what the walk actually populated.
    if not ctx.crit.get("docket_number") or not stopped:
        return NOTHING
    return ctx.result()


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

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
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

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
