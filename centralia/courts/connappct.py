r"""Connecticut Appellate Court ('connappct').

Everything unique to connappct lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile stays
registered in courts/__init__.py (with `front_matter=('syllabus',)`), where
it was already declared as 'Same Law Journal slip format as the Supreme
Court' — which the paper bears out.

THE PUBLISHER IS THE SAME ONE. The Commission on Official Legal Publications
sets the Appellate Court's advance release exactly as it sets the Supreme
Court's, down to the point size and the rail:

    ┌─ page 1 ───────────────────────────────────────────────────────────┐
    │      ****************************************************  10pt    │
    │      The "officially released" date that appears near the …        │
    │      All opinions are subject to modification and technical …      │
    │      … the latest version is to be considered authoritative.       │
    │      ****************************************************  10pt    │
    └────────────────────────────────────────────────────────────────────┘
    ┌─ page 2 ───────────────────────────────────────────────────────────┐
    │                    State v. Bey             8pt — running head     │
    │     STATE OF CONNECTICUT v. HENNY JORDAN BEY  11pt — the caption   │
    │                    (AC 48215)               11pt — the docket      │
    │           Elgo, Clark and Westbrook, Js.     8pt — the panel       │
    │                     Syllabus                 8pt — the Reporter's  │
    │ The plaintiff in error, A Co., a bail bonds …    precis, 8pt       │
    │  Argued November 20, 2025—officially released July 21, 2026  8pt   │
    │                 Procudural History           8pt — sic            │
    │   Writ of error from the decision of the Superior Court … 11pt     │
    │   William B. Westcott, for the plaintiff in error.        11pt     │
    │                     Opinion                  8pt                  │
    └────────────────────────────────────────────────────────────────────┘

THE TYPE SAYS WHOSE WORDS THEY ARE, which is the whole parser: the court's
own text — caption, docket, procedural history, appearances, opinion — is
11pt, and everything the REPORTER adds around it is 8pt (running head, panel
roster, syllabus and its heading, the argued/released line, the section
labels, the footnotes). The asterisk rule that fences the notice is 10pt.
Nothing here is keyed to a page number or a row index.

WHAT THE 44-FILE CORPUS ACTUALLY IS. The hypothesis going in was Connecticut's
two papers — the advance release slip and the bound CONNECTICUT LAW JOURNAL
extract — with the `_1`/`_2` filename suffix marking the extracts, as it does
on conn. MEASURED: all 44 records open on the asterisk-fenced notice on page
1, and not one prints a repeated reporter-citation head. Each of the twelve
`_N` files is the SAME advance release again — six byte-identical to their
partner (`deutsche_bank_ag_v._vik`, `gaynor_v._gilman`, `in_re_probate_appeal_
of_sharp`, `milenkovic_v._milenkovic`, `n._g._v._d._s.`, `65-99_burban…`) and
four a corrected re-issue of it, same length, same caption, differing only in
a footnote's text (`mccullough_v._rocky_hill`, `state_v._brozynski`,
`state_v._fluker`, `state_v._washington`) — or the separate opinion released
beside it (`crossen_v._diehl_1`). Not one is the Journal's printing, so this
corpus is ONE paper, read by one walk: 44 slips, 0 extracts.

THE JOURNAL BRANCH IS STILL HERE, and deliberately: the same publisher sets
the Appellate Reports in the bound volume with the identical three running
heads, and its reporter citation is '240 Conn. App. 505' — a TWO-WORD
abbreviation, which is why the cite-head shape admits an optional second
abbreviated token. It is found by REPETITION (the same line less its digits,
at the same baseline, in the top quarter of two or more pages), never by
wording, and the row is DROPPED with its cite kept as `criteria.citation`,
because a line printed identically on thirty pages cannot be any one page's
content. No record in this corpus reaches that branch; it was verified against
the Supreme Court's Journal extracts, which are the same printing.

WHICH PAPER THIS IS, IS A LANDMARK QUESTION — and the landmark is the RULE,
never the wording. 'Connecticut Law Journal' is a phrase the NOTICE itself
prints four times and the OTHER paper prints across every page, so a
notice-word list keyed on it drops a whole caption page as furniture (it cost
conn its caption, panel, history, appearances and the first 35 lines of a per
curiam on one record). The notice is the run that FOLLOWS `^\*{6,}$` on page 1
and it is dropped, not tinted: none of it is the court's writing and it is
printed identically on all 44 records.

THE LIGATURE BREAKS IN THE BOUND PRINTING. The Journal's fonts set 'ffi' as
one glyph and the extractor recovers it as 'offi cially' ('fi led',
'certifi ed'), so the released-date landmark needs both spellings or the date
row misfiles as syllabus or panel on every extract.

TWO THINGS THE APPELLATE COURT DOES THAT THE SUPREME COURT DOES NOT:

1. IT DOES NOT ALWAYS LABEL THE OPINION. `freitag_v._commissioner_of_
   correction` runs counsel straight into 'PER CURIAM.  The respondent, the
   Commissioner' with no centred 'Opinion' between them. A walk that ends
   only at that label reads the per curiam's first page as the counsel block
   and then fails its own gate, so the walk ends at the label OR AT THE FIRST
   BYLINE, parsed with this court's own declared grammar (abbreviated titles).
   The byline is not claimed — it is where the writing begins, and core opens
   it there.

2. IT MISSPELLS ITS OWN HEADING. `state_v._bey` prints 'Procudural History'.
   The heading is a landmark, so the test admits the Reporter's keying slip
   ('Pro…ral History') rather than one exact spelling; without that, bey's
   history and appearances read as syllabus and the paper's own disposition
   never reaches `criteria.history`.

THE FOOTNOTE ZONE IS NOT THE BLOCK, even where it stands inside it. This
court stars its anonymised captions and its release dates, and the notes land
at the foot of the CAPTION page while the block runs on to the next sheet
(`n._g._v._d._s.` sets '*In accordance with our policy …' at 0.74 of page 2
with the syllabus continuing on page 3). Those rows are the court's own
footnotes, core reads them from the page's footnote zone, and a reader that
claimed them would publish them twice. So a row that OPENS A FOOTNOTE — core's
own `detect_label`, the test the footnote subsystem uses — in the Reporter's
8pt below the page's top third ENDS THE PAGE for this walk: not claimed, not
dropped, left where it belongs. Everything below it on that page is note text
by construction, because a footnote zone is the foot of its page.

THE CLAIM MUST BE CONTIGUOUS, and that is why the syllabus IS claimed here.
Connecticut prints no byline above its precis, so core opens a writing on the
CAPTION ROW itself; core's bisection invariant then pulls every row inside
that writing's span back into it, and a reader that claimed the caption and
skipped the precis publishes an EMPTY headmatter. The walk therefore runs
from the caption to the opinion without a gap, and the precis rows take the
`syllabus` role — the court's front matter read in place.

A SLIP WITH NO CAPTION IS A SEPARATE OPINION, NOT A FAILURE.
`crossen_v._diehl_1` is the advance release of a concurrence-in-part and
dissent-in-part alone: the notice page, then 'ELGO, J., concurring in part
and dissenting in part.' on page 2. There is no caption, no docket and no
precis to read, and the whole of its headmatter is the notice, recorded as
dropped — which is what v1's baseline shows for it too (an empty headmatter).
Forcing a caption that is not printed would be the misreading.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import detect_label, line_markup
from ..resolve.furniture import FurnitureFinder

_MAX_PAGES = 6
# The court's own type against the Reporter's. Measured over all 44 records:
# 11pt for the court, 8pt for everything the Reporter adds, 10pt for the
# asterisk rule that fences the notice.
_COURT_SIZE_MIN = 10.5

_ASTERISKS = re.compile(r"^\*{6,}$")
# '(AC 48215)' / '(AC 48812, AC 48835)' — the Appellate Court's own docket,
# and the Supreme Court's 'SC' where a record carries both.
_DOCKET = re.compile(
    r"^\((?:SC|AC)\s*\d+[\s,;]*(?:(?:SC|AC)?\s*\d+)*\)$", re.I)
# The panel roster: a list of names closing in 'Js.' or 'J.'
_ROSTER = re.compile(r"\bJs?\.\s*$")
_SYLLABUS_HEAD = re.compile(r"^Syllabus$", re.I)
# 'Argued November 20, 2025—officially released July 21, 2026'
#
# THE LIGATURE IS BROKEN IN THE BOUND PRINTING — 'offi cially' — so the
# landmark carries both spellings (see the module docstring).
_OFFICIALLY = r"of\s?f\s?i\s?c\s?ially"
_ARGUED_RELEASED = re.compile(
    r"^(?:Argued|Submitted)\s+(.+?)[—–-]\s*" + _OFFICIALLY
    + r"\s+released\s+(.+)$", re.I)
_RELEASED_ONLY = re.compile(
    r"^" + _OFFICIALLY + r"\s+released\s+(.+)$", re.I)
# A FOOTNOTE MARK RIDES THE DATE. The Reporter stars the released date where
# it notes that the slip date is the operative one ('July 16, 2026**'), and
# the star is not part of the date.
_DATE_MARK = "*†‡∗⁎﹡＊ "
# 'Procedural History' heads the band beneath it and belongs to that band.
# THE SPELLING IS THE REPORTER'S, NOT A CONTRACT: state_v._bey prints
# 'Procudural History'. The landmark is the heading, so the keying slip is
# admitted rather than the file being lost to it.
_HISTORY_HEAD = re.compile(r"^Pro\w{2,8}ral History$", re.I)
# 'Opinion' is the paper naming ITSELF, and it is where the writing begins.
_OPINION_HEAD = re.compile(r"^Opinion$", re.I)
# The bound volume's page number, standing alone above the block.
_FOLIO = re.compile(r"^\d{1,4}$")
# A paragraph OPENS a step in from the Reporter's rail: 184.0 against 174.0.
_INDENT_MIN = 6.0
# A footnote zone is the FOOT of its page: the earliest label measured over
# the 44 records stands at 0.39 of the sheet, and the block's own rows above
# it run from 0.21. The floor only keeps a stray raised glyph in the caption
# band from ending the page.
_FOOT_ZONE_MIN = 0.30

# ---- the bound volume's running head ---------------------------------
# '240 Conn. App. 505' / '354 Conn. 151' — volume, reporter, first page. A
# SHAPE, not a name: two numbers around an abbreviation of one or two words
# (the Appellate Reports are 'Conn. App.'). Accepted as a running head only
# where the SAME line stands at the SAME baseline on two or more pages, the
# measurement that separates a head from a citation filling a short line.
_REPORTER_CITE = re.compile(
    r"^(\d{1,4})\s+([A-Z][A-Za-z]{1,11}\.(?:\s*[A-Z][A-Za-z]{1,11}\.)?)"
    r"\s+(\d{1,4})$")
# Every head on those pages stands in the top quarter of the sheet; the
# body's own first row is at 0.237, so the zone alone does not identify a
# head — the repetition does.
_HEAD_ZONE = 0.25
_HEAD_TOL = 1.5         # the head's baseline is invariant to a tenth
# The head is a SHORT row of a 264pt measure; a full-measure line of prose
# can never be one, whatever it says.
_HEAD_MEASURE_MAX = 0.5

# THE PANEL, printed and parsed. The roster can run over two rows and only
# the last closes in 'Js.', so the printed form is the rows joined. The bench
# titles are a closed vocabulary — 'C. J.', 'J.', 'Js.' — and taking them out
# leaves the names.
_BENCH_TITLE = re.compile(r",?\s*(?:C\.\s*J\.|Js\.|J\.)(?=,|\s|$)")

# THE WALK'S OTHER END. The court's own byline grammar, as registered for
# this court in courts/__init__.py: abbreviated titles ('CLARK, J.',
# 'CRADLE, C. J.', 'PER CURIAM.', 'ELGO, J., concurring in part and
# dissenting in part.'). Verified against the appearances it must NOT take:
# 'Adam J. Cohen, for the appellee (defendant).' and 'Hope J. Estrella,
# deputy assistant public defender,' both parse as None.
_BYLINE = BylineGrammar(style="abbrev")

# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is `docket_number`
# (a string) plus `other_dockets` (the rest), and an argued date belongs in
# `submitted`, which the render labels 'argued/submitted'. Written under an
# invented name they attach by setattr and never serialize.


def _norm(text: str) -> str:
    return " ".join(text.split())


def _digitless(text: str) -> str:
    """A repetition key: the line without its numbers, so a head that counts
    the volume's pages ('240 Conn. App. 505' / '506') still matches itself."""
    return "".join(c for c in text if not c.isdigit()).strip()


def _running_heads(model, body_x0: float, right_x1: float):
    """`(baselines, citation)` — the tops the paper prints a head on, and the
    reporter citation one of them carries. `(set(), None)` where there is no
    reporter head, which is what says this is not the Journal's extract.

    A HEAD IS FOUND BY REPETITION, never by wording: the same line, less its
    digits, standing at the same baseline in the top zone of two or more
    pages. That is the only test that reaches all three of this paper's
    heads, because core's furniture finder reads the pages against the
    document's dominant type and a three-page extract is dominated by the
    Reporter's 8pt.
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


def _opens_footnote(line, pm) -> bool:
    """Is this row the first line of the page's FOOTNOTE ZONE?

    core's own `detect_label` — the test the footnote subsystem itself uses
    for 'this line starts a new note' — reads all three shapes this court
    sets: a raised numeral ('1The plaintiff…'), a body-size star ('*In
    accordance with the spirit…') and a solid double star ('**July 16, 2026,
    the date that…'). It is asked only of the Reporter's 8pt, below the top
    third, so a raised mark riding a caption or a date cannot end the page.
    """
    return (bool(detect_label(line))
            and (line.size or 0.0) < _COURT_SIZE_MIN
            and line.top >= pm.height * _FOOT_ZONE_MIN)


@decider("headmatter.read", court="connappct")
def read_headmatter_connappct(model, geom, **_):
    """Read the Appellate Court's block — the advance release slip or the Law
    Journal's bound extract, one walk under two landmarks — or NOTHING."""
    if len(model.pages) < 2:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 174.0)
    right_x1 = (geom.right_x1 if geom and geom.right_x1 else 438.15)
    finder = FurnitureFinder(model, body_x0, body_size)
    byline = BylineParser(_BYLINE)

    ctx = _Ctx()
    # ---- WHICH OF THE TWO PAPERS IS THIS? -------------------------------
    # The slip opens on the Reporter's notice, whole, on page 1; the Law
    # Journal extract opens on the bound volume's running head. Each is a
    # landmark the paper always prints; a record printing neither is not this
    # publisher's and core's walk has it.
    #
    # THE NOTICE IS ITS RULE, not its wording — see the module docstring.
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
    # THE BLOCK STARTS AT THE TOP OF ITS PAGE. The page is the first one
    # after the notice that carries the court's docket, and the block's first
    # row is that page's first row — the running head above it is furniture
    # and is already gone. Found by landmark, never by page number.
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
    counsel: list[str] = []
    dockets: list[str] = []
    paras = 0
    stopped = False
    band = "caption"        # caption | syllabus | history | counsel
    panel: list[str] = []
    for pm in model.pages[caption_pm.number - 1:_MAX_PAGES]:
        for group in _rows(pm, finder):
            text = _norm(" ".join(l.plain for l in group))
            if not text:
                continue
            first = group[0]
            # THE HEADS THE CLAIM INHERITS. On the extract, core's furniture
            # finder takes the Journal's date/name band and the case-name
            # head but not the citation head — that row stands INSIDE the
            # body measure and its folio changes on every page. Named by its
            # measured baseline and recorded, never skipped: an unrecorded
            # row a reader passed over comes back as residual.
            if any(abs(first.top - t) <= _HEAD_TOL for t in heads):
                ctx.drop(group, "running-head")
                continue
            if _FOLIO.match(text):
                ctx.drop(group, "folio")
                continue
            if _opens_footnote(first, pm):
                # THE FOOT OF THE PAGE IS THE COURT'S FOOTNOTES, and core
                # reads them from the page's footnote zone. Not claimed and
                # not dropped — claiming them would publish them twice.
                break
            if (first.size or 0.0) >= _COURT_SIZE_MIN and byline.parse(text):
                # THE FIRST BYLINE ENDS THE READER. Left unlabelled by the
                # Reporter on a per curiam ('PER CURIAM.  The respondent, the
                # Commissioner'), this is the only landmark the paper always
                # sets. Not consumed: the writing opens here.
                # ASKED OF THE COURT'S OWN TYPE ONLY. A byline is 11pt like
                # every other line the court writes, so the Reporter's 8pt —
                # where a precis sentence could one day read as a byline — can
                # never end the walk.
                stopped = True
                break
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
                # them is that the history is ONE paragraph: every paragraph
                # opens at 184.0 and runs over at 174.0, the first is the
                # procedural history (closing on the court's disposition —
                # 'Writ of error denied.', 'Affirmed.') and every paragraph
                # after it is one appearance. Counting paragraph OPENINGS is
                # what tells them apart; the closing sentence is not relied
                # on. A page break never ends a paragraph, so the count runs
                # across the sheet (bey's history opens on page 2 and its
                # appearances stand on page 3).
                if first.x0 >= body_x0 + _INDENT_MIN:
                    paras += 1
                if paras >= 2:
                    band = "counsel"
                if band == "counsel":
                    counsel.append(text)
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
                dockets.extend(t.strip() for t in
                               text.strip("()").replace(";", ",").split(",")
                               if t.strip())
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
            # sets in this band above the precis. THE ROSTER IS READ IN THE
            # CAPTION BAND AND NOWHERE ELSE: this is the walk's last resort,
            # so anything the Reporter sets in 8pt that no landmark claimed
            # arrives here, and taking it into the panel criterion would put
            # a released date among the judges.
            if band == "caption":
                panel.append(text)
            ctx.emit(group, "panel")
        if stopped:
            break

    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption[:4])
    if dockets:
        # A CONSOLIDATED RECORD PRINTS ITS DOCKETS AS SEPARATE ROWS
        # (majkut_v._majkut sets '(AC 48812)' and '(AC 48835)' one under the
        # other), so the rows are collected and split rather than the first
        # row alone being read.
        ctx.crit.setdefault("docket_number", dockets[0])
        if dockets[1:]:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if panel:
        # THE PRINTED FORM BESIDE THE PARSED FORM. The roster can span two
        # rows and only the second closes in 'Js.', so the line is the rows
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
    if counsel:
        # THE APPEARANCES STAY WHERE THE PAPER PRINTS THEM — inside the
        # block, as `counsel` rows — and are STATED in the criteria box as
        # well. Nothing is lifted out of the headmatter: core copies counsel
        # into `criteria.attorneys` only from a separate attorneys section or
        # from blocks it MOVED, so a reader that (rightly) keeps the
        # appearances in place leaves the document with no machine-readable
        # counsel at all — 8 of these 44 records, and all 50 of the Supreme
        # Court's. The rows are the reading; this is the same reading, said
        # in the field the model has for it.
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    # THE GATE COMES LAST, and it judges what the walk actually populated —
    # never a value the walk has not reached yet.
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
