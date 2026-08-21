"""Supreme Court of Ohio ('ohio').

Everything unique to ohio lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Ohio sets ONE front-matter anatomy and prints it on two
papers. Both stack the same rows on the page axis and close the block with
a TYPED underscore rule; what tells them apart is a single DRAWN mark:

    'reporter's slip' (45 of 50) — the court draws a 44-46pt rule under the
    word NOTICE, on the page axis, at top 162 of 792. That underline is the
    only rule the slip draws above its footnotes, and it appears on every
    slip and on no clerk's entry:

        [Until this opinion appears in the Ohio Official …      10pt, in the
        v. Turner, Slip Opinion No. 2026-Ohio-1996.]            top margin
        NOTICE                                                  12pt, centred
        ────────                                    a DRAWN 44pt underline
        This slip opinion is subject to formal revision …   the advisory,
        … before the opinion is published.                  at its own inset
        SLIP OPINION NO. 2026-OHIO-1996          the CITATION, bold, on axis
        THE STATE OF OHIO, APPELLANT, v. TURNER, APPELLEE.  the case name
        [Until this opinion appears in the Ohio Official Reports advance
        may be cited as State v. Turner, Slip Opinion No. 2026-Ohio-1996.]
                                   the reporter's citation ADVISORY, recorded
        Criminal law—Juvenile law—When a juvenile court transfers …
        … unaddressed assignments of error.        the reporter's HEADNOTES
        (No. 2024-1242—Submitted June 3, 2025—Decided June 3, 2026.)
        APPEAL from the Court of Appeals for Cuyahoga County,   the origin
        No. 111808, 2023-Ohio-2874.                            and its number
        __________________            a TYPED 108pt rule ON THE AXIS
        DETERS, J., authored the opinion of the court, which KENNEDY, C.J.,
        and DEWINE, HAWKINS, and SHANAHAN, JJ., joined.  FISCHER, J., …
        DETERS, J.                    …and the writing starts

    "clerk's entry" (5 of 50) — the resignations, the retirement and the
    reinstatement. NO rule is drawn on page 1 at all, and the advisory is
    not printed; the block opens straight on the bold banner and the same
    typed rule closes it. There is no roster above the body — the entry is
    unsigned, the paragraph marker opens it, and the vote is printed at the
    FOOT of the last page, inside the entry:

        [Cite as In re Resignation of Yerman, 2026-Ohio-1883.]   10pt head
        IN RE RESIGNATION OF YERMAN.                             bold banner
        [Cite as In re Resignation of Yerman, 2026-Ohio-1883.]  the CITATION,
                                        the only place this paper prints one
        Attorneys at law—Resignation with disciplinary action pending—…
        (No. 2026-0541—Submitted May 1, 2026—Decided May 26, 2026.)
        ON APPLICATION FOR RETIREMENT OR RESIGNATION             the posture
        PURSUANT TO GOV.BAR R. VI(11).
        _________________
        {¶ 1} Respondent, John William Yerman Jr., …             the body

THE DISPATCH IS THE DRAWN UNDERLINE, not the word above it. 'NOTICE' is
the obvious thing to key on and it is the wrong thing: the advisory's own
prose repeats the phrase, and a court that reworded the heading would take
the whole corpus with it. Measured over the 50 records the underline is
44.1-45.5pt wide, centred on the page axis to within 1pt, and drawn on 45
of 45 slips and 0 of 5 entries.

EACH ZONE IS FOUND BY ITS OWN LANDMARK, never by its ordinal:

  * the running head is the TOP BAND — every page carries one (the bracketed
    cite on page 1, 'SUPREME COURT OF OHIO' / '<Month> Term, <year>'
    alternating after it), all of them alone above top 100 while the body
    block never opens above 110. Page 1's is unique text, so core's
    repetition test cannot learn it; the reader claims it and RECORDS it. On
    later pages core's furniture pass already knows it, and the reader steps
    over those rows without claiming them;
  * the advisory ends at the first BOLD row — it carries no bold anywhere,
    and the reporter's banner below it is bold throughout;
  * the caption block ends at the first NON-bold row — the slip number, the
    case name and the bracketed cite form are bold, and everything under them
    is not. Inside it, a row belongs to the BRACKET when it opens one (a
    delimiter, not a phrase) and to the case name otherwise;
  * WHAT THE BRACKET IS, THE PAPER SAYS. On the slip the citation stands on
    its own row above the case name ('SLIP OPINION NO. 2026-OHIO-1996') and
    the bracket below is the reporter's citation ADVISORY — apparatus that
    states no fact the citation does not, so it is recorded as a notice. On
    the clerk's entry there is no slip-number row and the bracket IS the cite
    form, and the only citation that paper prints. Either row is a CITATION
    and not the court naming itself: 'ohio' keeps 'No. 2026-0541' — the
    number THIS court gave the case — in `docket_number`, so the cite has to
    go in `citation` or it displaces a real value (which is what ill was
    doing when it stored its neutral cite as the docket);
  * BELOW THE CAPTION, THREE ZONES IN ANY ORDER. The docket row is the one
    the court parenthesises, and it closes on its own ')'. The HEADNOTES are
    told from the origin by their FACE: the Reporter of Decisions' subject
    list is the one run of front matter Ohio sets in ITALIC and the origin is
    roman. Reading them by position instead — headnotes, then docket, then
    origin, as 49 records print them — read the whole 20-row headnote band of
    ctr_for_media as its origin, because that record sets its docket FIRST.
    The band stays where the page sets it: it is a list of TOPICS, not a
    précis, and the headmatter renders whole, so it is never lifted into a
    summary section the way v1 lifted it;
  * the origin ends at the TYPED RULE — 102-120pt of underscores centred on
    the page axis, drawn at least once on all 50 records;
  * the roster ends at the byline, at the paragraph marker, or at a SECOND
    typed rule (posan closes a two-part roster with one).

WHAT THE READER DOES NOT TOUCH. Counsel: Ohio prints its appearances at
the FOOT of the last page, below the writings and between two more typed
rules — that is endmatter, not headmatter, and this reader never reaches
it. Footnotes: the walk stops at each page's footnote separator (a drawn
144pt rule at the body rail), so jones's note 1 — printed beside the
roster — stays with core's footnote pass.

A record that draws neither the underline nor a page-1 typed rule is not
one of these papers and gets NOTHING.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES, register

# Ohio signs its lead opinion and its separate writings in the same
# abbreviated form ('DETERS, J.' / 'BRUNNER, J., concurring in judgment
# only.'), and its unsigned dispositions 'Per Curiam.' in title case. This
# is the grammar the court has always carried, moved here beside its
# reader; nothing about it changes.
#
# The shared table in courts/__init__.py registers 'ohio' too, and its entry
# is meant to come out when this module is imported (ala and ariz did the
# same). Superseding it here rather than depending on that deletion keeps a
# missed edit from raising 'duplicate profile' and taking the whole package
# — every other court included — down with it.
PROFILES.pop("ohio", None)
OHIO = register(CourtProfile(
    "ohio", "Supreme Court of Ohio",
    byline=BylineGrammar(style="abbrev"),
    front_matter=("syllabus",),
))

STYLE_SLIP = "reporter's slip"
STYLE_ENTRY = "clerk's entry"

# ---- ohio's declared facts (measured over all 50 records) ----------------
# THE NOTICE UNDERLINE: 45 drawn rules over the corpus, every one 44.1-45.5pt
# wide, centred on the page axis to within 1.0pt, at top 161.9-162.3 of 792.
_UNDERLINE_MEASURE = (34.0, 60.0)
_UNDERLINE_AXIS = 12.0
_UNDERLINE_BAND = 0.35
# THE CAPTION FENCE: the typed underscore rule that closes the origin.
# 102.0-120.0pt wide, centred on the axis (x0 246.1-255.1 on a 612pt page).
_FENCE_MEASURE = (80.0, 140.0)
_FENCE_AXIS = 16.0
# THE FOOTNOTE SEPARATOR is the court's OTHER rule and is told apart by
# where it STARTS: 144pt at the body rail (x0=108) against a fence at 252.
_SEP_MIN = 100.0
_SEP_RAIL = 6.0
# THE RUNNING HEAD'S BAND. Page 1's head sets at top 37.6-60.5 (it wraps to
# three rows on the longest case names); continuation heads sit at 37.8. The
# body block never opens above 109.7 on any page in the corpus, and page 1's
# first content row is at 151.2.
_HEAD_BAND = 100.0
# HOW FAR THE BLOCK MAY RUN. yost and ctr_for_media carry a 20-row catchline
# onto page 2 and their roster with it; nothing needs a fourth page.
_MAX_PAGES = 4

# A TYPED RULE is a run of six or more underscores or dashes — the whole
# U+2010..U+2015 dash block, plus the ASCII hyphen.
_TYPED_RULE = re.compile("^[_\u2010-\u2015-]{6,}$")
# Ohio's paragraph label. It is the document's own printed mark and it opens
# the body on every record in the corpus — including the unsigned entries,
# which carry no byline at all.
_PARA_MARK = "{¶"
# The reporter's slip number, the one row above the case name. Set in CAPS,
# and case matters: the bracketed citation form below the case name closes on
# the same words in title case ('Slip Opinion No. 2026-Ohio-1270.]'), which
# read case-insensitively tagged the bracket's last row as the banner on
# seven records.
_SLIP_NO = re.compile(r"^SLIP OPINION NO\.\s")
# THE COURT'S OWN PUBLIC-DOMAIN CITATION, wherever the front matter prints
# it. It is a CITATION and not the court naming itself: read as the masthead
# role it looked like 'SUPREME COURT OF OHIO', and read as a docket it would
# displace 'No. 2026-0541', which is the number this court gave the case.
# Matched case-insensitively because the same cite is set three ways on one
# page — CAPS on the slip-number row ('2026-OHIO-2065'), title case in the
# bracketed cite form and in the running head — and normalized to the form
# the Reporter of Decisions publishes.
_NEUTRAL_CITE = re.compile(r"\b(\d{4})-Ohio-(\d+)\b", re.I)
# THE DOCKET ROW, as the court parenthesises it. The dash between its cells
# is set as an em dash on most records and as a HORIZONTAL BAR (U+2015) on
# posan and mcintyre — the same cell separator, a different glyph.
_DOCKET_ROW = re.compile(r"^\(Nos?\.\s")
# The CELL SEPARATOR is a DASH, never a hyphen: Ohio's own docket numbers are
# hyphenated ('2024-1242'), and splitting on the hyphen took the number apart
# and left the docket criterion unset on all 50 records.
_DASHES = "—–―‒"
_CASE_NO = re.compile(r"\b(\d{4}-[0-9A-Za-z]{3,6})\b")
_SUBMITTED = re.compile(r"^(?:Submitted|Argued)\s+(.+)$", re.I)
_DECIDED = re.compile(r"^(?:Decided|Filed)\s+(.+)$", re.I)
# THE ORIGIN'S OWN NUMBERS, as the origin row prints them: the tribunal's
# docket ('No. 111808', 'Nos. 22-549-EL-BGN and 22-550-EL-BTX') and the
# court-below citation ('2023-Ohio-2874').
_LOWER_NOS = re.compile(r"\bNos?\.\s*([^.;]+?)(?=[.;]|$)")
_OHIO_CITE = re.compile(r"\b(\d{4}-Ohio-\d+)\b")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Ohio sets its statuses inline, comma-separated, after the name,
# and stacks them ('APPELLANTS AND CROSS-APPELLEES'). The fiduciary and
# officer abbreviations ('EXR.', 'DIR.', 'ADMR.') are roles too.
_STATUS_WORDS = {
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "relator", "relators",
    "plaintiff", "plaintiffs", "defendant", "defendants", "intervenor",
    "intervenors", "cross", "and", "et", "al", "etc", "the", "d.b.a",
    "dba", "aka", "a.k.a", "exr", "exrs", "admr", "admrs", "dir",
    "trustee", "trustees", "guardian", "warden", "clerk", "judge",
    "supt", "supt.", "auditor", "treasurer", "sheriff", "commr", "commrs",
    "individually", "in", "his", "her", "their", "official", "capacity",
    "appellant/cross-appellee", "appellee/cross-appellant", "nka", "fka",
}
# The bench titles Ohio abbreviates in its roster, plus the acting form.
_ROSTER_TITLES = {"J", "JJ", "C.J", "CJ", "ACTING", "P.J"}
# THE HEADNOTES' FACE. 'Catchline' is the printer's name for this band and is
# kept as the internal one; the ROLE it renders under is `headnotes`, because
# what the band holds is the Reporter of Decisions' subject list.
# The reporter's topical subject line is the ONE run of
# front matter Ohio sets in plain ITALIC; the docket row, the origin and the
# roster are roman. Measured over the 50 records: 489 non-bold rows above the
# fence, 336 of them wholly italic, 153 of them wholly roman, and 5 mixed —
# a case name inside the catchline is set roman inside the italic ('balancing
# of Penn Cent. Transp. Co. v. New York City factors weighs', 0.46). No roman
# row in the corpus carries any italic at all, so the cut sits at 0.25.
_CATCHLINE_ITALIC = 0.25
# The disposition Ohio states in the catchline's LAST dash-separated clause.
# A closed vocabulary, because the four retirement entries close their
# catchline on a rule citation instead ('—Gov.Bar R. VI(11)(C).') and that is
# not a disposition.
_DISPOSITION_WORDS = (
    "affirmed", "reversed", "vacated", "remanded", "dismissed", "denied",
    "granted", "overruled", "sustained", "reinstated", "stayed", "modified",
    "disqualified", "suspended", "disbarred", "withdrawn", "allowed",
    "quashed", "disbarment", "reprimand", "suspension", "writ", "writs",
    "sanction", "judgment", "dismissal",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _join(rows: list) -> str:
    """Rows joined as one statement. A WRAP AT A HYPHEN CARRIES NO SPACE:
    the utility dockets break mid-token ('Nos. 22-507-GA-AIR, 22-508-' /
    'GA-ALT'), and a blind join published '22-508- GA-ALT'."""
    out = ""
    for row in rows:
        row = _norm(row)
        if not out:
            out = row
        elif out.endswith("-"):
            out += row
        else:
            out += " " + row
    return out


# --------------------------------------------------------------------------
# the page's own marks
# --------------------------------------------------------------------------

def _notice_underline(pm) -> float | None:
    """The top of the DRAWN rule Ohio sets under the word NOTICE, or None.

    This is the dispatch: 44-46pt on the page axis in the page's top third.
    The footnote separator is four times as wide and starts at the body
    rail, so neither measure reaches the other."""
    for r in pm.h_rules:
        if not (_UNDERLINE_MEASURE[0] <= r.width <= _UNDERLINE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _UNDERLINE_AXIS:
            continue
        if r.top > pm.height * _UNDERLINE_BAND:
            continue
        return r.top
    return None


def _italic_fraction(group: list) -> float:
    """How much of a row's LETTERING is italic.

    Judged on letters only: Ohio leaves the em dashes between the
    catchline's topics, its statute numbers and its parentheses in the roman
    face, and counting those read a wholly italic catchline as mixed."""
    letters = 0
    italic = 0
    for line in group:
        for ch in (line.chars or []):
            t = ch.get("text") or ""
            if not t.isalpha():
                continue
            letters += 1
            font = ch.get("fontname") or ""
            if "Italic" in font or "Oblique" in font:
                italic += 1
    return italic / letters if letters else 0.0


def _is_fence(line, page_width: float) -> bool:
    """A TYPED underscore rule centred on the page axis — the mark Ohio
    closes its caption with, and closes a two-part roster with."""
    if not _TYPED_RULE.match(_norm(line.plain)):
        return False
    if not (_FENCE_MEASURE[0] <= (line.x1 - line.x0) <= _FENCE_MEASURE[1]):
        return False
    return abs((line.x0 + line.x1) / 2 - page_width / 2) <= _FENCE_AXIS


def _footnote_cut(pm, body_x0: float) -> float:
    """Where this page's footnotes begin — the drawn 144pt separator Ohio
    sets AT THE BODY RAIL. jones prints note 1 beside the roster."""
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

@decider("headmatter.read", court="ohio")
def read_headmatter_ohio(model, geom, **_):
    """Read Ohio's slip or its clerk's entry, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    underline = _notice_underline(page1)
    style = STYLE_SLIP if underline is not None else STYLE_ENTRY

    # THE ROWS, in page order, with same-row pieces rejoined.
    rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
        cut = _footnote_cut(pm, body_x0)
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or line.top >= cut:
                continue
            if pm.number > 1 and finder.kind(pm, line):
                continue          # core's furniture pass records these
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        rows.extend(groups[k] for k in order)
    if len(rows) < 5:
        return NOTHING

    ctx = _Ctx(model, geom, pages, body_size)

    # THE TOP MARGIN. Every page carries a running head; page 1's is unique
    # text, so core's repetition test never learns it. Claimed and RECORDED
    # — a reader that takes a region inherits its furniture.
    head, rest = [], []
    for group in rows:
        if group[0].top < _HEAD_BAND:
            head.append(group)
        else:
            rest.append(group)
    rows = rest
    if not rows:
        return NOTHING
    for group in head:
        ctx.drop(group, "running-head")

    # THE ADVISORY. It carries no bold anywhere and the reporter's banner
    # below it is bold throughout, so the first bold row on page 1 closes
    # it. On the clerk's entry there is no advisory and the first bold row
    # is the banner itself.
    first_bold = next((i for i, g in enumerate(rows)
                       if g[0].page == 1 and all(l.all_bold for l in g)), None)
    if first_bold is None:
        return NOTHING
    if style is STYLE_SLIP:
        if first_bold == 0:
            return NOTHING        # an underline with nothing under it
        for group in rows[:first_bold]:
            ctx.drop(group, "notice")
    elif first_bold != 0:
        return NOTHING            # the entry opens ON its banner
    rows = rows[first_bold:]

    parser = BylineParser(OHIO.byline)
    caption: list[str] = []
    cite_row: list[str] = []
    bracket: list[str] = []
    catchline: list[str] = []
    docket_row: list[str] = []
    origin: list[str] = []
    roster: list[str] = []
    state = "caption"
    in_bracket = False
    in_docket = False
    fenced = False

    for group in rows:
        pm = pages[group[0].page]
        text = _norm(" ".join(l.plain for l in group))
        bold = all(l.all_bold for l in group)

        if _is_fence(group[0], pm.width):
            ctx.rule(group)
            if state != "roster":
                state = "roster"
                fenced = True
                continue
            break                 # the second fence closes a two-part roster

        if state == "caption":
            if bold:
                # THE BRACKET OUTRANKS THE BANNER: once the citation form is
                # open, every row belongs to it until the bracket closes.
                #
                # WHAT THE BRACKET IS depends on the paper, and the paper is
                # named by the DRAWN underline, not by the bracket's wording.
                # On the slip it is the reporter's citation ADVISORY ('[Until
                # this opinion appears in the Ohio Official Reports advance
                # sheets, it may be cited as …]') — reporter apparatus that
                # states no fact about the case beyond the cite the slip-
                # number row above it already carries, so it is RECORDED as a
                # notice, not printed. On the clerk's entry there is no slip-
                # number row and the bracket IS the cite form ('[Cite as In
                # re Resignation of Yerman, 2026-Ohio-1883.]'), which is the
                # only place that paper prints the citation at all.
                #
                # Either way the rows are CLAIMED. They are exactly what core
                # used to mis-read: the cite form wraps to a short centred
                # bold third row ('Slip Opinion No. 2026-Ohio-1487.]') that
                # reads as a writing's own title and opened a phantom
                # authorless majority which swallowed the catchline, the
                # docket, the origin and the roster on four records. Recording
                # them keeps them out of core's hands as surely as printing
                # them did.
                if in_bracket or text.startswith("["):
                    in_bracket = not text.rstrip().endswith("]")
                    bracket.append(text)
                    if style is STYLE_SLIP:
                        ctx.drop(group, "notice")
                    else:
                        ctx.emit(group, "citation", centred=True)
                    continue
                if _SLIP_NO.match(text):
                    cite_row.append(text)
                    ctx.emit(group, "citation", centred=True)
                    continue
                caption.append(text)
                ctx.emit(group, "caption", centred=True)
                continue
            state = "zones"

        if state == "zones":
            # THREE ZONES, EACH FOUND BY ITS OWN LANDMARK — never by its
            # ordinal. Ohio normally sets the catchline above the docket row
            # and prints them the other way round on ctr_for_media, so a
            # fixed order reads that record's whole catchline as the origin.
            if in_docket:
                docket_row.append(text)
                ctx.emit(group, "docket", centred=True)
                in_docket = ")" not in text and len(docket_row) < 3
                continue
            if _DOCKET_ROW.match(text):
                docket_row.append(text)
                ctx.emit(group, "docket", centred=True)
                in_docket = ")" not in text
                continue
            if _italic_fraction(group) >= _CATCHLINE_ITALIC:
                catchline.append(text)
                # HEADNOTES, not a summary. This band is the Reporter of
                # Decisions' subject list — a run of dash-separated topics
                # closing on the judgment ('Attorneys—Misconduct—Violations
                # of the Rules of Professional Conduct—Respondent's
                # objections overruled—Public reprimand.'). It states the
                # case's topics; it does not précis the case, and a précis is
                # a different thing. It stays HERE, in the page's own order,
                # rather than being lifted into a section: the headmatter
                # renders whole.
                ctx.emit(group, "headnotes")
                continue
            origin.append(text)
            ctx.emit(group, "lower-court", centred=True)
            continue

        if state == "roster":
            if text.startswith(_PARA_MARK):
                break             # the entry's body opens on its own marker
            if bold and parser.parse(text) is not None:
                break             # a byline always ends the reader
            roster.append(text)
            ctx.emit(group, "panel")
            continue
        break

    # A record that never fenced its caption is not one of these papers.
    if not fenced or not docket_row:
        return NOTHING

    ctx.crit["headmatter_style"] = style
    _citation(ctx, cite_row or bracket)
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)
    _docket(ctx, " ".join(docket_row))
    if catchline:
        _disposition(ctx, catchline)
    if origin:
        _origin(ctx, origin)
    if roster:
        line = _norm(" ".join(roster))
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
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centred: bool = False):
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        pm = self.pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        # ALIGNMENT IS A PROPERTY OF THE BLOCK. Ohio centres its whole
        # caption on the page axis, and its full-measure rows reach both
        # margins — measured one row at a time they read as left-aligned
        # and the block prints ragged. Inside the caption band the axis is
        # the measurement; the catchline and the roster are set to the
        # measure and keep their own.
        cx = (first.x0 + max(p.x1 for p in parts)) / 2
        if centred and abs(cx - pm.width / 2) <= 10.0:
            align = m.Align.CENTER
            rel = 0.0
        else:
            align = m.Align(line_alignment(
                first, pm.width, self.geom,
                banner_center_min_size=self.body_size + 2.0))
            rel = 0.0
            if align is m.Align.LEFT and self.geom \
                    and first.x0 > self.geom.body_x0 + 12:
                rel = min(first.x0 - self.geom.body_x0, pm.width * 0.6)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str):
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:1200],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def rule(self, group: list):
        # A FENCE RENDERS WHERE THE PAGE TYPES IT. Core re-sorts the block by
        # the source position of each item's provenance, so the rule carries
        # the line ids it was typed with and stays put.
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# what the zones say
# --------------------------------------------------------------------------

def _strip_status(side: str) -> str:
    """A party's name, with its trailing ROLE chunks removed.

    Ohio sets the caption as one sentence and hangs the roles off the name
    in comma-separated chunks ('HOSKINS, EXR., APPELLEE,'). Only chunks made
    ENTIRELY of role words come off, so 'AWMS WATER SOLUTIONS, L.L.C.' keeps
    its corporate form."""
    chunks = [c.strip() for c in side.split(",") if c.strip()]
    while len(chunks) > 1:
        words = [w for w in re.split(r"[\s/]+", chunks[-1].lower()) if w]
        if words and all(w.strip(".") in _STATUS_WORDS for w in words):
            chunks.pop()
            continue
        break
    return ", ".join(c for c in chunks if c).strip(" ,")


def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the pivot.

    Ohio's pivot is an italic 'v.' set inside the bold banner; it may fall
    anywhere in the sentence, including across a wrap."""
    whole = _norm(" ".join(rows))
    # A FOOTNOTE MARK IS NOT PART OF A NAME. jones calls its note off the
    # party's own status ('GALLOWAY, WARDEN, APPELLEE.1').
    whole = re.sub(r"\.\s*[0-9*\u2020\u2021\u2217]{1,2}$", ".", whole)
    if whole.endswith("."):
        whole = whole[:-1]        # the sentence's period, not an initial's
    parts = re.split(r"\s+v(?:s)?\.\s+", whole, maxsplit=1)
    if len(parts) == 2:
        one, two = _strip_status(parts[0]), _strip_status(parts[1])
        if one and two:
            ctx.crit["parties"] = [one, two]
            ctx.crit["case_name"] = f"{one} v. {two}"
            return
    bare = _strip_status(whole)
    if bare:
        ctx.crit["parties"] = [bare]
        ctx.crit["case_name"] = bare


def _citation(ctx: _Ctx, rows: list) -> None:
    """The court's own public-domain citation, as the front matter prints it.

    Preferred from the slip-number row ('SLIP OPINION NO. 2026-OHIO-2065')
    and taken from the bracketed cite form where — as on every clerk's entry
    — the court sets no slip-number row. Published in the Reporter's own
    form: the year, the reporter name in title case, and the sequence
    number."""
    for row in rows:
        mm = _NEUTRAL_CITE.search(_norm(row))
        if mm:
            ctx.crit["citation"] = f"{mm.group(1)}-Ohio-{mm.group(2)}"
            return


def _docket(ctx: _Ctx, text: str) -> None:
    """'(No. 2024-1242—Submitted June 3, 2025—Decided June 3, 2026.)' — one
    parenthesised row holding this court's number and both of its dates,
    the cells separated by a dash."""
    inner = _norm(text).strip()
    if inner.startswith("("):
        inner = inner[1:]
    inner = inner.rstrip(")").rstrip()
    cells = [c.strip(" .") for c in re.split(f"[{_DASHES}]", inner)
             if c.strip(" .")]
    if not cells:
        return
    nums = _CASE_NO.findall(cells[0])
    if nums:
        ctx.crit["docket_number"] = f"No. {nums[0]}"
        if nums[1:]:
            ctx.crit["other_dockets"] = list(nums[1:])
    for cell in cells[1:]:
        sm = _SUBMITTED.match(cell)
        if sm:
            ctx.crit["submitted"] = sm.group(1).strip(" .")
            continue
        dm = _DECIDED.match(cell)
        if dm:
            ctx.crit["decision_date"] = dm.group(1).strip(" .")


def _origin(ctx: _Ctx, rows: list) -> None:
    """The origin band: the posture Ohio sets in caps and, where there is a
    tribunal below, its name and its numbers.

    An ORIGINAL action in this court names no tribunal at all ('IN
    MANDAMUS.'), so the statement is kept as printed and only the numbers
    are read out of it."""
    whole = _join(rows)
    numbers: list[str] = []
    for mm in _LOWER_NOS.finditer(whole):
        for piece in re.split(r",|\band\b", mm.group(1)):
            piece = piece.strip(" .,")
            if piece:
                numbers.append(piece)
    numbers += [c for c in _OHIO_CITE.findall(whole) if c not in numbers]
    if numbers:
        ctx.crit["lower_court_docket"] = numbers
    stated = whole
    cut = _LOWER_NOS.search(stated)
    if cut:
        stated = stated[:cut.start()]
    stated = stated.strip(" ,.")
    if stated:
        ctx.crit["lower_court"] = stated


def _disposition(ctx: _Ctx, rows: list) -> None:
    """The judgment, as the catchline's LAST clause states it.

    Ohio's reporter writes the catchline as one sentence of dash-separated
    topics and closes it on the disposition ('…—Court of appeals\u2019
    judgment reversed, convictions reinstated, and cause remanded…'). The
    dash is the separator and the HYPHEN is not: the catchline hyphenates
    freely ('mandatory- or discretionary-bindover')."""
    whole = _join(rows)
    cells = [c.strip(" .") for c in re.split(f"[{_DASHES}]", whole)
             if c.strip(" .")]
    if not cells:
        return
    last = cells[-1]
    words = {re.sub(r"[’']s$", "", w.strip(".,;:()’'")).lower()
             for w in last.split()}
    if any(w in words for w in _DISPOSITION_WORDS):
        ctx.crit["disposition"] = last


def _panel(line: str) -> list[str]:
    """The judges the roster names, in the order it names them.

    A name is an ALL-CAPS chunk; where the court spells a visiting judge in
    full ('MARK C. MILLER, J., of the Third District Court of Appeals') the
    SURNAME is the last capitalised word of the chunk. The bench titles are
    a closed vocabulary and are never names."""
    # A MIDDLE INITIAL IS NOT A SENTENCE END. Ohio spells a visiting judge
    # in full ('MARK C. MILLER, J.'), and splitting on '. ' cut the forename
    # off from the surname and published 'MARK' as a member of the court.
    line = re.sub(r"\b[A-Z]\.\s+(?=[A-Z])", "", line)
    out: list[str] = []
    for chunk in re.split(r"[,;.]\s+|\)\s*", line):
        # WHO SAT, NOT WHO WAS REPLACED. A visiting judge's clause names the
        # justice they stood in for ('MARK C. MILLER, J., of the Third
        # District Court of Appeals, sat for BRUNNER, J.'), and that justice
        # is precisely the one who did NOT decide the case.
        low = chunk.lower()
        if "sat for" in low or "sitting for" in low:
            continue
        words = [w.strip(".,;:()") for w in chunk.split()]
        caps = [w for w in words
                if len(w) >= 2 and w.isupper() and w.isalpha()
                and w not in _ROSTER_TITLES]
        if caps and caps[-1] not in out:
            out.append(caps[-1])
    return out
