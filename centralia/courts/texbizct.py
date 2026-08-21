"""The Business Court of Texas ('texbizct').

Everything unique to texbizct lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is carried
in this file (the `mass.py` pattern) and registered into `PROFILES` below.

WHAT THIS COURT IS. A trial court created in 2024 — a specialist business
docket sitting in eleven numbered divisions across the state. It is NOT the
Supreme Court of Texas, and it does not print that court's paper: there is no
panel, no roster of appearances, no argued/decided pair, no lower court. A
single judge decides a motion and files a memorandum opinion. What it DOES
print is a cover sheet, and it prints one for every writing it files.

IS THIS AN ECF FILING? No. The section-rail caption is the same shape the
federal Texas district courts set (`centralia/districts/ecf.py`, the glyph
rail), and the rail's glyph — '§' — is the Texas state-court convention both
lanes inherited. But NOTHING ELSE of the ECF pleading order is here: no
CM/ECF header stamp fielded across the top of every page, no
'IN THE UNITED STATES DISTRICT COURT FOR THE …' masthead, no asterisk band
closing the caption, no 'Civil Action No.'. Instead the court prints its own
public-domain citation above the masthead, a state-court clerk's FILED stamp
where it prints one, and it fences the paper's title between two TYPED RULES
of box-drawing characters. The shared ECF reader would find none of its
landmarks, so this file reads the cover itself.

THE COVER — one sheet, 612x792, 12–13pt Courier, body rail at x0=72:

    FILED IN                          the clerk's stamp, flush right in the
    BUSINESS COURT OF TEXAS           top band; on 14 of 42 records only,
    BEVERLY CRUMLEY, CLERK            and pure furniture -> Dropped
    ENTERED
    4/8/2026

              2026 Tex. Bus. 35       the court's own PUBLIC-DOMAIN CITATION,
                                      centred, always the first row of type
                                      under the stamp -> criteria.citation

        The Business Court of Texas,  the masthead: the court, then its
              Eleventh Division       DIVISION, two centred rows

    M. BROWN,                    §    the caption: two columns split by a
        Plaintiff,               §    stacked '§' RAIL. Left, the parties and
    v.                           §  Cause No. 25-BC11B-0099
    EXXON MOBIL CORPORATION,     §    their status; right, the cause number
        Defendant.               §    and nothing else.

    ═══════════════════════════════   a TYPED RULE of box-drawing characters
            Syllabus*                 the paper's TITLE, centred
    ═══════════════════════════════   and the closing rule

    This opinion addresses …          and the writing begins

TWO PAPERS, and THE TITLE BAND'S FENCE names them (42 records, 36/6, nothing
left over):

  * 'fenced title' (36) — the title stands between two typed '═' rules. This
    is the court's current cover and every division except the Eighth sets
    it.

  * 'bare title' (6) — no rules are typed at all; the title is a lone BOLD
    CENTRED row standing in the whitespace under the caption
    ('MEMORANDUM OPINION'). The Eighth Division's chambers set this, and so
    do the four records that reach us as SCANS.

A record printing neither a masthead nor a rail is not this paper and gets
NOTHING.

A SYLLABUS IS A SECTION OF ITS OWN, AND NINE RECORDS PRINT ONE (revised
2026-08-21, the user: 'it has a syllabus that should be identified').
Court staff write a precis, the court hangs a footnote on it disclaiming it
('This syllabus is provided for the convenience of the reader; it is not part
of the opinion and should not be cited or relied upon as legal authority'),
and it is headmatter — role `syllabus` — not the opinion's opening words.

The word stands in one of two places, and both are read:

    the FENCED TITLE       4   bnsf, brown, dk_trading, gosecure
    a heading BELOW it     5   enosis, jeremiah, kampmann, mesquite, pradera
                               (the fence holds 'OPINION' or 'OPINION & ORDER'
                               and 'Syllabus' is set italic under it)

Unclaimed, the precis did far more damage than one untinted block: it is the
first unclaimed prose in the document, so assembly opened the WRITING on it,
the writing's span then began on page 1, and core's 'a writing is never
bisected' invariant reunited everything this reader had claimed on page 2 —
the second cover's citation, masthead and title — into that writing.
bnsf_railway rendered '2026 Tex. Bus. 8 / The Business Court of Texas, /
First Division / Opinion and Order Entering Final Judgment' as body prose in
the middle of its own opinion, and carried two footnotes both labelled 1.
Claimed, the writing's first line moves to page 2, the second cover survives
by itself, and the syllabus's note becomes a headmatter footnote because
core attaches notes by page ownership.

THE COVER IS PER-WRITING, NOT PER-DOCUMENT. Six records print the cover
TWICE: once over a staff-written 'Syllabus' and again, overleaf, over the
opinion the syllabus describes (brown_v._exxon_mobil, bnsf_railway,
enosis_investments — where the second cover is on page 3, not page 2 —
gosecure, jeremiah_counsel, dk_trading). The second cover is not a running
head and it is not a repeat of the first: it is the next writing's own cover
sheet, with its own title. So the reader looks for a cover on every one of
the first three pages and reads each one it finds, in place. Read as
front matter only, the second cover's title was left unclaimed and the
`Syllabus` band above it became the document's only writing.

FOUR RECORDS ARE SCANS. `local_marketing_v._bennett`, `may_v._ineos`,
`plains_pipeline_v._arrowhead` and `stratton_v._hogan` come back from pdfio
with `image_area == 1.00` — a FULL-BLEED RASTER of the whole sheet with an
OCR text layer over it, which is why the render puts an `image` chip on them.
They are not born-digital: the type sizes jitter by a tenth of a point from
row to row and the OCR mangles a word here and there ('Plaint·iff', 'ROBERTS.
MAY' for 'ROBERT S. MAY'). The layout survives that intact — the rail is
still a column of '§' and the masthead is still two centred rows — so they
are read like any other bare-title record, and the raster is left to core's
image handling. Nothing is corrected: an OCR error is what the page says.

WHAT THIS READER DECLINES. On two records the party list is long enough to
fill page 1 by itself — fischer_v._fischer names fourteen defendants and
may_v._ineos_usa_oil__gas (a scan) names twenty — so the caption box runs to
the foot of the sheet and the TITLE BAND STANDS OVERLEAF, without a masthead
above it to say it is a cover. This reader does not follow it there: the
title band's own fence is not enough to tell a title from a section heading
on a page that prints no cover, so the row is left unclaimed and core makes
it the writing's heading, which is where it belongs anyway. `criteria.title`
is the only thing lost, and nothing is mis-tagged to gain it.

WHAT IS NOT HERE. No counsel block: this court does not print appearances on
the cover at all (checked over all 42). No panel: a single judge signs. No
dates in the front matter: the clerk's stamp carries the filing date and it
is furniture. So this reader emits six roles — `citation`, `court`, `caption`/`docket`
(inside the block), `title` and `syllabus` — and drops the stamp.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# --------------------------------------------------------------------------
# the court
# --------------------------------------------------------------------------

TEXBIZCT = CourtProfile(
    "texbizct", "The Business Court of Texas",
    # ONE PAPER, ONE WRITING: a trial court is one judge ruling on a motion,
    # so there is no second writing to concur in or dissent from. The six
    # syllabus records print two SECTIONS, not two opinions — the syllabus is
    # court staff's precis and says so in its own footnote.
    single_writing=True,
    # The judge signs in the reversed form: the name over the office.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("Judge, Business Court of Texas",
                                     "Judge", "Presiding Judge")),
)
PROFILES[TEXBIZCT.court_id] = TEXBIZCT

STYLE_FENCED = "texbizct cover, fenced title"
STYLE_BARE = "texbizct cover, bare title"

# --------------------------------------------------------------------------
# the landmarks — each one MEASURED, and none of them a case's words
# --------------------------------------------------------------------------

# The masthead. The court sets its name in title case in most divisions and
# in full caps in the Eighth, and the trailing comma is a typographic choice
# ('The Business Court of Texas,' / 'THE BUSINESS COURT OF TEXAS'), so the
# match is on the court's name alone and the case is ignored.
_MASTHEAD = re.compile(r"^THE\s+BUSINESS\s+COURT\s+OF\s+TEXAS\s*,?$", re.I)
# The division row that stands under it. A closed vocabulary: eleven numbered
# divisions — but the chambers write the number BOTH WAYS, as an ordinal word
# ('Eleventh Division') and as a numeral ('1st Division',
# dallas_sports_club_v._dse_hockey_arena). Read only as words, the numeral
# form fell through to the box branch and was tinted `caption` — a party row
# that is not a party, which is worse than an untagged row.
_DIVISION = re.compile(
    r"^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth"
    r"|Eleventh|\d{1,2}(?:st|nd|rd|th))\s+Division\s*,?$", re.I)
# The court's own public-domain citation. The reporter's abbreviation is
# still settling: most records print '2026 Tex. Bus. 35' and two print
# '2026 Tex. Bus. Ct. 47' (both synergy_thermogen records), so the 'Ct.' is
# optional.
#
# THE YEAR MAY BE TWO DIGITS. Re-measured over all 42 (2026-08-21): 41 print a
# citation in the top rows of page 1 and exactly ONE abbreviates the year —
# dallas_sports_group_v._dse_hockey_club prints '26 Tex. Bus. 36'. (The older
# note here said four records printed no citation at all and named this one
# among them; that was wrong.) Requiring four digits was not a missing
# criterion but a missing CLAIM, and the cost was the whole cover: the
# citation is the first row of page 1, so unclaimed it was the document's
# first unclaimed prose, assembly opened the writing ON it, and the
# 'a writing is never bisected' invariant then pulled this reader's masthead,
# caption box, title AND the syllabus band into that writing as body prose —
# the same damage this file already records for an unclaimed syllabus, from a
# different row.
_CITATION = re.compile(
    r"^(\d{2,4}\s+Tex\.\s*Bus\.(?:\s*Ct\.)?\s*\d+)\s*$", re.I)
# The clerk's FILED stamp. Two cues, and it is a RUN: the run opens on
# 'FILED IN' and the rows under it name the court, the clerk, the action and
# the date. Identified as a run in the TOP BAND, never row by row — 'BUSINESS
# COURT OF TEXAS' alone is also the masthead.
_STAMP_OPEN = re.compile(r"^(FILED IN|E-?FILED)\b", re.I)
_STAMP_ROWS = re.compile(
    r"^(BUSINESS COURT OF TEXAS|[A-Z][A-Za-z.\s]+,\s*(DEPUTY )?CLERK"
    r"|ENTERED|FILED|ACCEPTED|\d{1,2}/\d{1,2}/\d{4}"
    r"|\d{1,2}/\d{1,2}/\d{4}\s+\d.*)$", re.I)
# The right column's only tenant: the cause number the Business Court
# assigns. '25-BC11B-0099' — two-digit year, 'BC', the division, a letter for
# the judge, the sequence. Read as a labelled number so a division that
# labels it 'Cause Number' or 'Case No.' is still read.
_CAUSE = re.compile(
    r"^(?:Cause|Case)\s*(?:No\.?|Number)\s*[:.]?\s*(\S.*)$", re.I)
# The typed rule: a run of box-drawing horizontals and nothing else.
_TYPED_RULE = re.compile(r"^[═=─—_]{8,}$")
# The pivot, on its own row in the party column.
_PIVOT = re.compile(r"^v\s*\.?\s*$|^vs\s*\.?\s*$", re.I)
# A party's STATUS — a closed role vocabulary, and the reason a status row is
# not mistaken for a party name. Texas trial-court practice sets these and
# their counter- and third-party compounds.
_STATUS = re.compile(
    r"^(Plaintiffs?|Defendants?|Petitioners?|Respondents?|Intervenors?"
    r"|Relators?|Counter-?(Plaintiffs?|Defendants?|Claimants?)"
    r"|Third-?Party\s+(Plaintiffs?|Defendants?)|Cross-?(Plaintiffs?"
    r"|Defendants?)|Movants?|Appellants?|Appellees?)\b", re.I)
# The paragraph mark the body opens on. This court numbers every paragraph,
# so the first '¶' is the end of the cover as surely as a byline is.
_PARA = re.compile(r"^¶\s*\d+")
# …AND ON A SCAN THE GLYPH IS GONE. The four rastered records set the same
# mark and the OCR renders it a different way every time — '<jf 1', 'ljf2',
# '9[4', 'Cj[l', '912' — so a pattern that reads the CHARACTER cannot stop the
# walk on them. What is invariant is the POSITION: this court hangs the number
# in the left margin, and measured over all 42 records only 20 rows on pages
# 1-3 stand at x0 < 50 — every single one of them a paragraph mark, on the
# four scans and on dk_trading. The cover itself never reaches out there; its
# party column starts at 66 and its body rail at 65.
#
# Both existing guards missed these. `_PARA` cannot match '<jf'; and the mark
# shares a BASELINE with the first line of its paragraph, so `_rows` groups
# the two and the group — x0 29.5 out to 540 — has its centre within 21pt of
# the page axis and reads as CENTRED. local_marketing_v._bennett therefore ran
# the walk on past its title and published the opinion's whole opening
# paragraph as title rows, leaving the writing to begin mid-sentence at
# "parties' briefing and oral argument" (the user, 2026-08-21).
_MARGIN_X_MAX = 50.0
_MARGIN_MARK = re.compile(r"^\S{0,6}?[\dlIiO]{1,3}$")


def _opens_margin_mark(pieces: list) -> bool:
    """True when a row's leftmost piece is a margin paragraph number."""
    lead = pieces[0]
    if lead.x0 >= _MARGIN_X_MAX:
        return False
    # The OCR puts a space inside the mark as readily as not ('<jf 1' beside
    # 'ljf2'), so the glyphs are closed up before the shape is read.
    text = "".join((lead.plain or "").split())
    return bool(text) and len(text) <= 8 and bool(_MARGIN_MARK.match(text))

_RAIL_GLYPH = "§"
_RAIL_WINDOW = 8.0        # a glyph this close to the rail's x IS the rail
_RAIL_GAP_MAX = 60.0      # …and the next row of the same rail is this near
_RAIL_MIN_ROWS = 3        # fewer stacked glyphs than this is not a rail
_AXIS_TOL = 26.0          # centred on the page axis, at this court's measure
_COVER_PAGES = 3          # the second cover is never later than page 3
_TOP_BAND = 110.0         # the stamp's band, in points from the sheet's head
_TITLE_ROWS_MAX = 6       # the longest title the court prints is four rows
# THE TITLE THAT NAMES A PRECIS. 6 of the 42 records print a 'Syllabus' cover
# over the opinion's own; the footnote mark the court hangs on the word is
# part of the row, so the match is on its opening.
# No \b after the word: the footnote mark is a DIGIT welded to it
# ('Syllabus1'), and a word boundary between 's' and '1' does not exist.
_SYLLABUS_TITLE = re.compile(r"^Syllabus", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The caption's rail on ``pm``: {'x', 'top', 'bottom'}, or None.

    A rail is a COLUMN of '§' — glyphs stacked at one x — grown outward one
    contiguous step at a time, so a section sign standing somewhere else on
    the page (a footnote's 'Tex. Gov't Code § 25A.004') is barred by the gap
    bound however close its x happens to fall. Delaware's reader arrived at
    the same test independently; this is the same paper's divider.
    """
    chars = [c for line in pm.lines for c in line.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if not chars:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    column = sorted((c for c in chars if abs(c["x0"] - x) <= 4.0),
                    key=lambda c: c["top"])
    if len(column) < _RAIL_MIN_ROWS:
        return None
    run = [column[0]]
    for ch in column[1:]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    if len(run) < _RAIL_MIN_ROWS:
        return None
    return {"x": float(x), "top": min(c["top"] for c in run),
            "bottom": max(c["top"] for c in run)}


def _shed(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == _RAIL_GLYPH
                    and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the rail, or None.

    THE SPLIT IS CHAR BY CHAR, not by the row's own x0 — whether pdfio broke a
    row at its column gap is an accident of how wide the gap happened to be.
    simpson_v._simson returns 'BOBBY R. SIMPSON and HARDBALL §' as one run
    reaching from the party column across the rail, and may_v._ineos (a scan)
    returns 'ROBERTS. MAY, FOXBOROUGH ENERGY §' the same way. By the row's x0
    both would file the rail's glyph in the party column."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _strip_rail(text: str) -> str:
    """The glyph off whichever side pdfio glued it to. It is the drawn
    divider, not a word of either column."""
    text = text.strip()
    while text.startswith(_RAIL_GLYPH):
        text = text[len(_RAIL_GLYPH):].lstrip()
    while text.endswith(_RAIL_GLYPH):
        text = text[:-len(_RAIL_GLYPH)].rstrip()
    return text


def _rows(pm, finder) -> list[list]:
    """The page's rows, each a list of the same-baseline pieces."""
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


def _box_close(rows: list, rail: dict) -> float:
    """THE BOX'S LAST ROW IS NOT ALWAYS ITS LAST '§'.

    The rail is drawn BESIDE the party stack, and this court's chambers
    routinely set the stack's closing status row one pitch BELOW the last
    glyph: 'Defendants.' stands at 385.9 on yaun_v._battle__sands_energy
    where the rail's last glyph is at 379.7, and 'Defendants' at 407.2 on
    dallas_sports_club where it is at 395.2. Closed at the glyph, that row
    fell out of the box, sat at the party indent so it was not centred, and
    ENDED THE WALK — so the title band below it was never reached and seven
    records lost their `title`.

    Measured in the box's OWN PITCH (the smallest gap between the rail's
    rows): the row below the last glyph stands ONE pitch down where it is the
    stack's closing status, and the typed '═' rule the court fences the title
    with stands further. So a row belongs to the box when it follows within
    one and a half pitches AND stands wholly left of the rail's column — the
    same two questions the split inside the box asks, and no wording either
    time.
    """
    tops = sorted({round(g[0].top, 1) for g in rows
                   if rail["top"] - 1.0 <= g[0].top <= rail["bottom"] + 1.0})
    gaps = [b - a for a, b in zip(tops, tops[1:]) if b - a > 1.0]
    pitch = min(gaps) if gaps else 16.0
    bottom = rail["bottom"]
    for group in rows:
        top = group[0].top
        if top <= bottom + 1.0:
            continue
        if top - bottom > pitch * 1.5:
            break
        if max(l.x1 for l in group) >= rail["x"]:
            break               # it reaches the rail's column: not the stack
        bottom = top
    return bottom, pitch


def _row(parts: list, role: str):
    """One printed row of a caption column, as an HmLine. Provenance
    survives the merge: every piece's id goes into the Prov."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(1), align=m.Align.LEFT, role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=_strip_rail(text),
        prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from. A claim must be TOTAL:
    every id in `consumed` is in an item, a block, or a Dropped."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.anchor: list[int] = []

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

    def rule(self, group: list) -> None:
        """A TYPED rule the court set as a fence — drawn by the render, not
        printed as forty box-drawing characters of text."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="texbizct")
def read_headmatter_texbizct(model, geom, **_):
    """Read the Business Court's cover sheet(s), or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    ctx = _Ctx()
    styles: list[str] = []
    read_any = False
    for pm in model.pages[:_COVER_PAGES]:
        style = _read_cover(pm, ctx, finder, first=not read_any)
        if style is None:
            # A page without a cover ends the search only if we already have
            # one: the second cover stands on page 3 on enosis_investments,
            # with a page of syllabus prose between.
            continue
        styles.append(style)
        read_any = True
    if not read_any:
        return NOTHING
    # THE TITLE MAY STAND OVERLEAF, and now it is followed there.
    #
    # This reader used to decline it: where the party list fills page 1 by
    # itself the caption box runs to the foot of the sheet and the title band
    # is printed on the next page, with no masthead above it to say it is a
    # cover, and 'the title band's own fence is not enough to tell a title
    # from a section heading on a page that prints no cover'. True of a fence
    # found anywhere — but not of a fence that OPENS the page: measured over
    # all 42 records, fischer_v._fischer is the ONLY one whose page 2 opens on
    # a typed rule, and its band holds exactly the title ('MEMORANDUM OPINION
    # AND ORDER GRANTING IN PART AND DENYING IN PART RECEIVER PARTIES' AMENDED
    # RULE 91a MOTION TO DISMISS'). A section heading never opens a page under
    # a rule, because the rule would have closed the section above it.
    #
    # Gated on the cover having found NO title of its own, so it can only ever
    # fill a hole the walk already left. may_v._ineos runs its twenty-defendant
    # list over the same way, but its page 2 does not open on a rule — the OCR
    # broke the '═' run — so it keeps no title, which is the honest answer for
    # a scan (the user's note, 2026-08-21).
    if not ctx.crit.get("title") and len(model.pages) > 1:
        if not _read_box_overleaf(model.pages[0], model.pages[1], ctx, finder):
            _read_overleaf_title(model.pages[1], ctx, finder)
    ctx.crit.setdefault("headmatter_style", styles[0])
    return ctx.result()


def _read_box_overleaf(p1, pm, ctx: _Ctx, finder) -> bool:
    """The caption box CONTINUED on the next page. True when it read one.

    A party list long enough to fill page 1 does not end there: the box runs
    over, and the rows overleaf still carry the rail. may_v._ineos_usa_oil__gas
    names twenty defendants and page 2 opens
    'EXECUTOR OF THE ESTATE OF MARK A. §' / 'DOPPS, DECEASED, §' /
    'Defendants §' before its title — the closing rows of the caption, and the
    party status that ends it. Left behind they went to the writing, which then
    opened on 'DOPPS, DECEASED, § Defendants § MEMORANDUM OPINION AND ORDER'
    (the user, 2026-08-21: "defendants is part of the case caption").

    THE RAIL IS WHAT CARRIES OVER, and it is the whole test: the continuation
    is claimed only when page 2 stacks the same glyph in the SAME COLUMN as
    page 1's box (within the rail window) and page 1's own box ran to the foot
    of its sheet. A page that merely prints a '§' somewhere cannot qualify,
    and neither can a second COVER — that has a masthead of its own, which
    `_read_cover` has already claimed by the time this is asked.
    """
    r1, r2 = _rail(p1), _rail(pm)
    if r1 is None or r2 is None:
        return False
    if abs(r2["x"] - r1["x"]) > _RAIL_WINDOW:
        return False
    # Page 1's box must actually have run out of sheet: its rail reaches the
    # foot. Measured on may_v._ineos the last glyph sits at 0.86 of the page.
    if r1["bottom"] < p1.height * 0.80:
        return False
    # THE BOX'S OWN ROWS COME FROM THE PAGE, NOT FROM `_rows`. A row the rail
    # spans is inside the caption and cannot be a page head — but it is the
    # TOPMOST row of the sheet, so core reads it as one: 'EXECUTOR OF THE
    # ESTATE OF MARK A. §' at top 52.4 is classified `running-head` and never
    # reached this reader, which claimed the two rows under it and left the
    # party's name behind. Inside the rail's band the rail is the authority.
    band_rows: dict = {}
    for line in pm.lines:
        if not line.plain.strip():
            continue
        if r2["top"] - 1.0 <= line.top <= r2["bottom"] + 1.0:
            band_rows.setdefault(round(line.top, 1), []).append(line)
    rows = [sorted(band_rows[k], key=lambda l: l.x0) for k in sorted(band_rows)]
    rows += [g for g in _rows(pm, finder)
             if g[0].top > r2["bottom"] + 1.0]
    if not rows:
        return False
    mid = r2["x"]
    box_bottom, pitch = _box_close(rows, r2)
    left: list = []
    right: list = []
    box_ids: set[int] = set()
    parties: list[str] = []
    title_rows: list[list] = []
    band = "box"
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        top = pieces[0].top
        span0, span1 = pieces[0].x0, max(l.x1 for l in pieces)
        centred = abs((span0 + span1) / 2 - pm.width / 2) <= _AXIS_TOL
        if band == "box" and top <= box_bottom + 1.0:
            l_parts, r_parts = [], []
            for line in pieces:
                bare = _shed(line, r2)
                if bare is None:
                    continue
                for want, bucket in (("L", l_parts), ("R", r_parts)):
                    part = _side(bare, mid, want)
                    if part is not None:
                        bucket.append(part)
            if not l_parts and not r_parts:
                box_ids.update(l.id for l in pieces)
                continue
            left.append(_row(l_parts, "caption"))
            right.append(_row(r_parts, "caption"))
            box_ids.update(l.id for l in pieces)
            for part in l_parts:
                one = _norm(part.plain).rstrip(",")
                if one and not _PIVOT.match(one) and not _STATUS.match(one):
                    parties.append(one)
            continue
        band = "title"
        # the title band, on the same terms the cover reads its own
        if _TYPED_RULE.match(text):
            ctx.rule(pieces)
            if title_rows:
                break
            continue
        if _PARA.match(text) or _opens_margin_mark(pieces) or not centred:
            break
        title_rows.append(pieces)
        if len(title_rows) >= _TITLE_ROWS_MAX:
            break
    if not left:
        return False
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    if not left:
        return False
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
        style_id="section-rail",
        fp={"rail": _RAIL_GLYPH, "mid_x": round(mid, 1)},
        prov=m.Prov(pm.number, tuple(sorted(box_ids)))))
    ctx.consumed.update(box_ids)
    if parties:
        ctx.crit.setdefault("parties", [])
        ctx.crit["parties"] = list(ctx.crit["parties"]) + parties
    for pieces in title_rows:
        ctx.emit(pieces, "title")
        ctx.anchor.extend(p.id for p in pieces)
    if title_rows:
        ctx.crit.setdefault("title", _norm(" ".join(
            _norm(" ".join(l.plain for l in sorted(g, key=lambda l: l.x0)))
            for g in title_rows)))
    return True


def _read_overleaf_title(pm, ctx: _Ctx, finder) -> None:
    """The title band on a page that opens on a typed rule. See the caller."""
    rows = _rows(pm, finder)
    if not rows:
        return
    flat = [_norm(" ".join(l.plain for l in g)) for g in rows]
    if not _TYPED_RULE.match(flat[0]):
        return
    title_rows: list = []
    closed = None
    for i in range(1, min(len(rows), _TITLE_ROWS_MAX + 3)):
        text = flat[i]
        if not text:
            continue
        if _TYPED_RULE.match(text):
            closed = rows[i]
            break
        if _PARA.match(text):
            break
        title_rows.append(rows[i])
    # BOTH RULES OR NOTHING. An unclosed band is not a fence, and claiming it
    # would take the writing's first paragraphs for a title.
    if closed is None or not title_rows:
        return
    ctx.rule(rows[0])
    for pieces in title_rows:
        ctx.emit(pieces, "title")
        ctx.anchor.extend(p.id for p in pieces)
    # BOTH RULES ARE THE BAND'S. Claiming only the opening one left the
    # closing '═' run as the writing's first paragraph.
    ctx.rule(closed)
    ctx.crit.setdefault("title", _norm(" ".join(
        _norm(" ".join(l.plain for l in sorted(g, key=lambda l: l.x0)))
        for g in title_rows)))


def _read_syllabus(pm, ctx: _Ctx, rows: list, at: int, titled: bool) -> None:
    """The precis, and where it ends.

    WHERE THE WORD 'SYLLABUS' STANDS IS NOT FIXED. On four records it IS the
    fenced title, so the band opens the moment the fence closes. On
    jeremiah_counsel the fence holds 'OPINION AND ORDER' and the word stands
    BELOW it as the section's own heading, with the precis under that — so
    `titled` says whether the fence already named it, and a 'Syllabus' row
    found here names it too. Keyed to the fenced title alone, that record's
    syllabus stayed in the writing.

    WHAT ENDS THE BAND IS THE COURT'S NOTE ABOUT IT, and the note is told
    from the precis by TYPE SIZE — measured against the precis's OWN first
    row, never the page's commonest size. The cover, the precis and the note
    are three sizes, and they are not the same three on every record:
    bnsf sets 13.8 / 13.8 / 12.0, dk_trading 13.0 / 12.0 / 11.0. Measured
    against the page's modal size, dk_trading's precis read as the note and
    the whole band was refused.

    The note itself is left alone: it sits in the page's footnote zone, which
    is core's, and claiming it here would publish it twice.
    """
    band: float | None = None
    for group in rows[at:]:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text or _TYPED_RULE.match(text):
            continue                    # the title band's own closing rule
        size = round(pieces[0].size or 0.0, 1)
        if band is None:
            if _SYLLABUS_TITLE.match(text):
                # The section names itself here rather than in the fence.
                ctx.emit(pieces, "title")
                titled = True
                continue
            if not titled:
                return                  # this cover carries no syllabus
            band = size
        elif size < band - 0.5:
            break                       # the court's note about it: core's
        ctx.emit(pieces, "syllabus", centre=False)


def _read_cover(pm, ctx: _Ctx, finder, first: bool) -> str | None:
    """Read one cover sheet off page ``pm``, in place. Returns the style
    name, or None when this page prints no cover.

    THE DISPATCH IS THE LANDMARK PAIR, never a title: the masthead naming
    the court and the '§' RAIL beneath it. Either alone is not the cover —
    a footnote citing 'Tex. Gov't Code § 25A.004' stacks no column, and the
    masthead's words appear inside the clerk's stamp as well.
    """
    rows = _rows(pm, finder)
    if len(rows) < 4:
        return None
    mast = None
    for i, group in enumerate(rows):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD.match(text) and group[0].top > _TOP_BAND:
            mast = i
            break
    if mast is None:
        return None
    rail = _rail(pm)
    if rail is None or rail["top"] < rows[mast][0].top:
        return None
    mid = rail["x"]

    # THE BOX IS THE BAND THE RAIL'S OWN COLUMN SPANS, and one pitch past its
    # foot (see `_box_close`). A row of the party column and the '§' beside it
    # do not always share a top, so a row carrying no glyph does not mean the
    # box has closed.
    box_bottom, pitch = _box_close(rows, rail)

    left: list = []
    right: list = []
    parties: list[str] = []
    cause: str | None = None
    box_ids: set[int] = set()
    band = "head" if first else "cover"
    title_rows: list[list] = []

    for idx, group in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        top = pieces[0].top
        span0, span1 = pieces[0].x0, max(l.x1 for l in pieces)
        centred = abs((span0 + span1) / 2 - pm.width / 2) <= _AXIS_TOL

        # --- above the masthead: the stamp and the citation ---------------
        if idx < mast:
            # THE CITATION AND THE STAMP CAN SHARE A BASELINE. The stamp is
            # set flush right and the citation on the page axis, and on
            # crain_v._northern the clerk's date lands on the citation's own
            # line: pdfio returns them as two pieces of one row
            # ('2026 Tex. Bus. 11' + '3/11/2026'). Read as a joined row it
            # matched neither pattern, so the citation was dropped as part of
            # the stamp. The pieces are therefore judged ONE AT A TIME.
            cite = [p for p in pieces if _CITATION.match(_norm(p.plain))]
            if cite:
                if first:
                    ctx.crit.setdefault(
                        "citation", _norm(cite[0].plain))
                ctx.emit(cite, "citation")
                rest = [p for p in pieces if p not in cite]
                if rest and top <= _TOP_BAND:
                    ctx.drop(rest, "stamp")
                continue
            if top <= _TOP_BAND and (_STAMP_OPEN.match(text)
                                     or _STAMP_ROWS.match(text)):
                ctx.drop(pieces, "stamp")
                continue
            # Anything else above the masthead is at no position this paper
            # uses; left to core rather than tinted with a guess.
            continue

        if _MASTHEAD.match(text) or _DIVISION.match(text):
            if first:
                prior = ctx.crit.get("court")
                ctx.crit["court"] = f"{prior}, {text}" if prior else text
            ctx.emit(pieces, "court")
            continue

        # --- the box ------------------------------------------------------
        # THE BOX HAS A HEAD AS WELL AS A FOOT. Bounded only below, the
        # branch took every row standing between the masthead and the rail's
        # first glyph — which is where an unrecognized masthead row stands
        # ('1st Division') — and filed it in the party column.
        if band != "title" and rail["top"] - pitch <= top <= box_bottom + 1.0:
            l_parts, r_parts = [], []
            for line in pieces:
                bare = _shed(line, rail)
                if bare is None:
                    continue
                for want, bucket in (("L", l_parts), ("R", r_parts)):
                    part = _side(bare, mid, want)
                    if part is not None:
                        bucket.append(part)
            r_text = _strip_rail(_norm(" ".join(l.plain for l in r_parts)))
            got = _CAUSE.match(r_text)
            left.append(_row(l_parts, "caption"))
            right.append(_row(r_parts, "docket" if got else "caption"))
            box_ids.update(l.id for l in pieces)
            for part in l_parts:
                one = _norm(part.plain).rstrip(",")
                if one and not _PIVOT.match(one) and not _STATUS.match(one):
                    parties.append(one)
            if got and cause is None:
                cause = _norm(got.group(1))
            band = "box"
            continue
        if band == "box":
            band = "title"

        # --- the title band ----------------------------------------------
        if band != "title":
            continue
        if _TYPED_RULE.match(text):
            ctx.rule(pieces)
            # The closing rule ends the cover. The opening one does not.
            if title_rows:
                break
            continue
        if _PARA.match(text) or _opens_margin_mark(pieces) or not centred:
            break               # the writing has begun
        title_rows.append(pieces)
        if len(title_rows) >= _TITLE_ROWS_MAX:
            break
    else:
        idx = len(rows)

    if not left:
        return None
    fenced = any(isinstance(i, m.Rule) for i in ctx.items[-4:])

    # THE BOX, placed where the page prints it. The rail runs a few rows past
    # the last words, and those empty pairs are trimmed (ca6's rule).
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    if not left:
        return None
    block = m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
        style_id="section-rail",
        fp={"rail": _RAIL_GLYPH, "mid_x": round(mid, 1)},
        prov=m.Prov(pm.number, tuple(sorted(box_ids))))
    # The block goes in ahead of the title band and the rules, and behind the
    # citation and the masthead — the page's own order, never appended.
    head = [i for i in ctx.items
            if getattr(i, "role", "") in ("citation", "court")
            or isinstance(i, m.CaptionBlock)]
    ctx.items = head + [block] + [i for i in ctx.items if i not in head]
    ctx.consumed.update(box_ids)

    # THE TITLE, and it is also the writing's anchor: an unsigned memorandum
    # opinion has nothing else to open on, so its ids go to `anchor_ids` for
    # core's rescue pass.
    for pieces in title_rows:
        ctx.emit(pieces, "title")
        ctx.anchor.extend(p.id for p in pieces)
    # A SYLLABUS IS NOT THE OPINION, AND THE TITLE BAND SAYS WHICH PAPER THIS
    # IS. Where the fenced title reads 'Syllabus' the prose under it is court
    # staff's precis — it says so in its own footnote ('This syllabus is
    # provided for the convenience of the reader; it is not part of the
    # opinion and should not be cited or relied upon as legal authority') —
    # and it belongs to the headmatter, tagged, not to the writing.
    #
    # Unclaimed it did far more damage than one untinted block. The syllabus
    # is the first unclaimed prose in the document, so assembly opened the
    # writing ON it; the writing's span then started on page 1, and core's
    # 'a writing is never bisected' invariant reunited everything this reader
    # had claimed on page 2 — the SECOND cover's citation, masthead and title
    # — into that writing as paragraphs. bnsf_railway rendered '2026 Tex.
    # Bus. 8 / The Business Court of Texas, / First Division / Opinion and
    # Order Entering Final Judgment' as body prose in the middle of its own
    # opinion. Claiming the syllabus moves the writing's first line to page
    # 2 and the second cover survives by itself.
    _read_syllabus(pm, ctx, rows, idx, titled=bool(title_rows) and bool(
        _SYLLABUS_TITLE.match(_norm(" ".join(
            l.plain for g in title_rows for l in g)))))
    if title_rows and first:
        ctx.crit.setdefault("title", _norm(" ".join(
            _norm(" ".join(l.plain for l in sorted(g, key=lambda l: l.x0)))
            for g in title_rows)))
    if first:
        if cause:
            ctx.crit.setdefault("docket_number", cause)
        elif parties:
            pass
        if parties:
            ctx.crit.setdefault("parties", parties[:8])
            ctx.crit.setdefault("caption", [_text_of(r) for r in left
                                            if _text_of(r)][:12])
    elif cause and not ctx.crit.get("docket_number"):
        ctx.crit["docket_number"] = cause
    return STYLE_FENCED if fenced else STYLE_BARE
