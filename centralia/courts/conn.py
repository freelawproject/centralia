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
_NOTICE_WORDS = re.compile(
    r"officially released|subject to modification|Connecticut Law Journal"
    r"|advance release version|considered authoritative"
    r"|Connecticut Reports|Connecticut Appellate Reports", re.I)
# '(SC 21016)' / '(AC 46012)' / '(SC 21016, SC 21017)'
_DOCKET = re.compile(r"^\((?:SC|AC)\s*\d+[\s,;]*(?:(?:SC|AC)?\s*\d+)*\)$", re.I)
# The panel roster: a list of names closing in 'Js.' or 'J.'
_ROSTER = re.compile(r"\bJs?\.\s*$")
_SYLLABUS_HEAD = re.compile(r"^Syllabus$", re.I)
# 'Argued March 5—officially released May 5, 2026'
_ARGUED_RELEASED = re.compile(
    r"^(?:Argued|Submitted)\s+(.+?)[—–-]\s*officially released\s+(.+)$", re.I)
_RELEASED_ONLY = re.compile(r"^officially released\s+(.+)$", re.I)
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


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="conn")
def read_headmatter_conn(model, geom, **_):
    """Read Connecticut's advance release block, or NOTHING."""
    if len(model.pages) < 2:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 174.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    ctx = _Ctx()
    # ---- page 1: the Reporter's notice, whole ---------------------------
    for group in _rows(model.pages[0], finder):
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        if _ASTERISKS.match(text) or _NOTICE_WORDS.search(text) \
                or ctx.dropped:
            ctx.drop(group, "notice")
    if not ctx.dropped:
        return NOTHING          # no notice page: not this paper

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
    caption_pm = caption_idx = None
    for pm in model.pages[1:_MAX_PAGES]:
        rows = _rows(pm, finder)
        if not any(_DOCKET.match(_norm(" ".join(l.plain for l in g)))
                   for g in rows):
            continue
        caption_pm = pm
        for idx, group in enumerate(rows):
            text = _norm(" ".join(l.plain for l in group))
            # The Reporter's folio stands alone at the head of the page.
            if not text or _FOLIO.match(text):
                continue
            caption_idx = idx
            break
        break
    if caption_pm is None:
        return NOTHING

    caption: list[str] = []
    history: list[str] = []
    paras = 0
    stopped = False
    band = "caption"        # caption | syllabus | history | counsel
    pages = [pm for pm in model.pages[caption_pm.number - 1:_MAX_PAGES]]
    for pi, pm in enumerate(pages):
        rows = _rows(pm, finder)
        if pi == 0:
            rows = rows[caption_idx:]
        for group in rows:
            text = _norm(" ".join(l.plain for l in group))
            if not text:
                continue
            first = group[0]
            if _FOLIO.match(text):
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
                ctx.crit.setdefault("panel_line", text)
                ctx.emit(group, "panel")
                continue
            if (first.size or 0.0) >= _COURT_SIZE_MIN:
                caption.append(text)
                ctx.emit(group, "caption")
                continue
            # A ROSTER'S FIRST LINE ends in a comma, not in 'Js.' — it is
            # still the roster, and it is the only other thing the Reporter
            # sets in this band above the précis.
            ctx.emit(group, "panel")
        if stopped:
            break

    if not ctx.crit.get("docket_number") or not stopped:
        return NOTHING
    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption[:4])
    if history:
        ctx.crit.setdefault("history", " ".join(history)[:2000])
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
