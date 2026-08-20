"""Washington Court of Appeals ('washctapp').

Everything unique to washctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT. The three Divisions file one paper between them: a slip whose
front matter is a MASTHEAD over a TWO-COLUMN CAPTION held by a DIVIDER. The
court sets the divider two ways and nothing else in this file dispatches on
anything else:

    ruled rail (37 of 42) — ONE tall vertical rule with caption text on both
    sides of it, at x 292-317 on a 612pt page, its foot met by a horizontal
    of half the measure that ENDS AT the rule:

        IN THE COURT OF APPEALS OF THE STATE OF WASHINGTON      the banner
                            DIVISION II                         the division
        VIRGINIA P. SHOGREN,          │  No.  60736-1-II          the docket
                     Appellant,       │                            
              v.                      │  PUBLISHED OPINION        the title
        WASHINGTON STATE BAR …        │
                     Respondents.     │
        ─────────────────────────────╴  the fence, ending AT the rail
        VELJACIC, C.J. — Virginia P. Shogren appeals …        the opinion

    paren rail (5 of 42) — Division III sets the same caption with the
    divider TYPED, a stacked ')' at x 312, and fences it not at all:

        STATE OF WASHINGTON,   )  No.  40700-4-III
                               )
                  Respondent,  )
                               )
              v.               )  PUBLISHED OPINION

Measured over the corpus: 37 records draw exactly one tall vertical in the
rail band and 5 draw none at all — Division III types its column instead.
No record draws both, and no record draws none of either.

THREE THINGS THE DIVIDER DECIDES, and the wording never does:

  * COLUMN MEMBERSHIP IS DECIDED GLYPH BY GLYPH. Whether pdfio broke a
    caption row at its column gap is an accident of how wide that gap
    happened to be; shogren sets 'WASHINGTON ' / 'STATE ' / 'BAR' as three
    runs of ONE printed row and a whole-line test files the third in the
    right column (v1 does exactly that, and prints 'BAR' twice).

  * THE FENCE IS THE CAPTION'S OWN, and what identifies it is its RIGHT END
    reaching the rail — not its width. The footnote separator the same page
    draws at the same left margin stops 80pt short of the rail; the
    heading underline starts 200pt right of the margin. A consolidated
    record is FENCED CASE BY CASE (aiden sets three cases in one band and
    rules between them), and one caption too long for its page carries the
    rail onto the next (rosalinda).

  * A RAIL IS A COLUMN WITH A CONSTANT PITCH. teamsters' opening paragraph
    prints '(County)' whose ')' lands 0.3pt from the rail's own x, 30pt
    under its last glyph; taken as a rail glyph it drove the caption band
    193pt into the opinion and claimed six paragraphs of prose. The rail is
    read as the longest run of glyphs whose STEP holds the stack's own
    median, which the prose paren misses by 2x.

THE MASTHEAD. Above the caption stand the court's own banner and, in
Divisions II and III, the division it sits in. Division II sets that label
CENTRED ON THE PAGE AXIS but at the caption's own first baseline, so it
straddles the rail — and burney sets the party cell hard against it, with no
gap at all ('FREDERICK BURNEY, individually, DIVISION II' arrives as one
run). What separates them is TYPE SIZE: the masthead is set one step larger
than the caption (14pt against 12pt) on all 12 records that collide, and
ball's row splits the same way into three — party, division, docket. So the
size, not the column and not the gap, is what takes the label out; and the
corroboration is that a caption never crosses its own divider, which every
one of those labels does.

Division ONE prints its label as an ordinary right-column cell instead, and
it is read there, by the same closed vocabulary.

THE STAMP. Divisions II and III stamp page 1 at the top right — Division II
'Filed / Washington State / Court of Appeals / Division Two / <date>',
Division III 'FILED / <date> / In the Office of the Clerk of Court / WA
State Court of Appeals, Division III'. Division One stamps nothing.
Measured over the corpus, page 1 prints NOTHING above the caption but the
banner, the division and those stamps. They are furniture and are recorded
as Dropped — but the date they carry is the only place this paper states
when it was filed, so `decision_date` is read from the row that is dropped.

THE READER STOPS AT THE FENCE — or, where the court set none, at the foot of
the divider itself, and in either case never below the first row of body
prose. Washington prints nothing between its caption and its first byline:
no appearance roster, no 'Before' line, no summary. So there is no counsel
block and no panel block to read here, and none is invented.

THE PUBLICATION ORDER STAPLED AHEAD OF ITS OPINION (5 records: aiden, burns,
l.g., salvo, pulte). The court grants a motion to publish and files the
order and the now-published opinion as one PDF — and the opinion carries its
OWN front block, banner and caption and fence, on a later page. Measured by
the banner this document printed on page 1: 5 of 42 records print it twice,
and none prints it three times.

That second block belongs to the writing BELOW it, and left in the stream
every one of its rows falls into the writing ABOVE — which is what put a
whole reprinted caption at the foot of the publication order in burns and
l.g. It is read with page 1's own measured rule — a divider in the page's
top band, the banner ABOVE it with nothing but the division between the two,
the fence closing the band, and nothing over the banner but the clerk's
stamp in the page's top 18%. The banner is compared against the row THIS
document printed on page 1, never against a wording list. A threshold on the
block's own first row is the wrong test and was the wrong test: burns opens
its second cover at 0.29 of the page.

Two of the five never reach that test. CORE ALREADY CUTS THEM IN TWO:
`pipeline._attached_documents` starts a new stapled document at a page
carrying both the banner and a filing stamp, which is aiden's page 3 and
pulte's page 2 (Division One stamps nothing, so burns, l.g. and salvo stay
whole). Each part is then read on its own, and this reader reads each part's
cover as that part's headmatter. Two consequences it has to survive:

  * A STAPLED PART IS NUMBERED FROM ITS OWN FIRST PAGE. `pm.number` is
    1..n within the part and every prov is shifted by the part's offset
    afterwards, but `Line.page` still holds the number of the PDF it was
    read from. Every page test here therefore reads the PAGE's number.
    Read off the line, part 2 of aiden matched no row at all and the reader
    declined it silently; and a prov built from it would be shifted twice.

  * A PART MAY NOT BE ABLE TO STATE ITS OWN MEASURE. aiden's first part is
    the order — two pages, one of them nothing but its cover — and
    `geometry.measure` reads body_x0=497.0, right_x1=525.9 off the filing
    stamp: a 28.9pt 'measure' against which every caption row is
    full-measure body prose. The prose backstop is skipped rather than
    trusted when the measure comes back narrower than half the page.

OWNERSHIP: IT IS DROPPED, not moved. A writing's `caption` field is filled
by assembly, which runs AFTER this reader, so a court file cannot hand rows
to a writing that does not exist yet — a reader can only subtract. And there
is nothing in the block the document does not already print: the same court,
the same division, the same parties, the same docket, all of which render
whole in the headmatter at the head of the document. So the rows are claimed
and recorded as `Dropped` — attested, never silently deleted — in the kinds
the page itself distinguishes: the clerk's stamp as `stamp`, exactly as page
1's is, the reprinted block as `superfluous`.

WHAT THIS COURT DOES NOT DO. It prints no per-writing docket head. Measured
over every page after the first, in all 42 records: 344 rows carry a docket
this document's page 1 printed, core's furniture pass sweeps 339 of them as
running heads, and the 5 it leaves are the docket CELLS of the five second
covers above — set 50 to 125pt right of the page axis, in a
caption column, not centred over a byline. wash's second form does not occur
here and nothing is written to look for it.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace
from statistics import median

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# washctapp's profile is registered in the shared table; this file owns its
# reader only. The reader never parses a byline — its claim is closed by the
# caption's own fence — so it needs no grammar of its own.

STYLE_RULED_RAIL = "ruled-rail caption"
STYLE_PAREN_RAIL = "paren-rail caption"

# ---- washctapp's declared facts (measured over the corpus, not tuned) ----
# THE DIVIDER'S COLUMN. Measured, the rail stands at x 292.3 to 316.7 on a
# 612pt page — 0.478 to 0.518 of the measure. The window is what keeps an
# ordinary parenthesis in the body ('RCW 9.94A.525(1)(b)') out of the rail:
# prose parentheses land wherever the line breaks, and a column of five of
# them at one x inside this window is the divider and nothing else.
_RAIL_BAND = (0.42, 0.62)
# …and the divider OPENS THE PAGE'S FRONT MATTER. Measured, the rail's top
# runs 0.187 (ball) to 0.414 (feekes) of the page. Half the page is a wide
# margin on that, and it is what keeps a column of parentheses deep in a
# body table from ever reading as a caption.
_RAIL_TOP_MAX = 0.45
# A RAIL IS A COLUMN, not a count of glyphs anywhere on the page. Measured
# here the shortest typed rail runs 9 glyphs and the tallest 11.
_PAREN_FLOOR = 5
# …but a caption that WRAPS THE PAGE carries fewer glyphs onto the next one.
# There the column is already proved, so two is enough.
_PAREN_CONT_FLOOR = 2
# A glyph belongs to the rail when it stands in the rail's own column.
_RAIL_WINDOW = 6.0
# A RAIL HOLDS ITS OWN PITCH. The typed rail's step is the leading (14.9pt
# in a 13pt face, invariant to 0.2pt within a document); the nearest prose
# ')' that shares its column stands 2.0x that step below its last glyph
# (teamsters). 1.75 is inside that gap.
_PITCH_BREAK = 1.75
# THE DRAWN DIVIDER: one vertical spanning the caption band. Measured 84.9
# (abbe) to 546.1pt (rosalinda) tall. Shorter than this is not a divider.
_VRULE_MIN_H = 80.0
# THE FENCE: a horizontal anchored on the left margin whose right end
# reaches the divider. Measured, the fence starts within 5pt of the body
# rail (71.3 against a 72.0 rail, 89.3 against 90.0, 84.4 against 90.0 —
# aiden's boxed first case starts 4.7pt LEFT of it) and ends at the rail
# (x1 - rail_x = 0.0 on 36 of 37 drawn records). What it is NOT: the
# footnote separator this court draws at the same left margin, 234pt wide
# against a rail at 311 — it stops 77pt short.
_FENCE_X0_MAX = 18.0
_FENCE_REACH = 10.0
# HOW FAR BELOW THE RAIL a fence may still be the one that closes it.
_FENCE_DROP = 30.0
# THE MASTHEAD IS SET ONE TYPE STEP LARGER than the caption, and that is
# what separates the division label from a party cell printed hard against
# it. Measured on all 12 collisions: 14.0pt against 12.0pt.
_SIZE_STEP = 1.0
# A MEASURE NARROWER THAN HALF THE PAGE IS NOT A MEASURE. Core cuts a
# stapled PDF into parts and measures each one on its own (`pipeline.py:
# _attached_documents`), and aiden's first part — the publication order, two
# pages, one of them nothing but its cover — measures body_x0=497.0,
# right_x1=525.9 off the filing stamp: a 28.9pt 'measure' against which
# every caption row is full-measure prose. The prose backstop is skipped
# rather than trusted when the document cannot state its own measure.
_MIN_MEASURE = 0.5
# BODY PROSE runs the full measure AT the body rail. No caption cell and no
# masthead row ever reaches it — measured, the widest row inside a band is
# 0.72 of the measure and it is centred. One such row and the band is over.
_PROSE_INK = 0.85
# How far the front matter may run. Two pages is more than any washctapp
# record needs; the longest consolidated caption (rosalinda) uses two.
_MAX_PAGES = 3
# A caption's CONTINUATION opens the next page's top band.
_TOP_BAND = 0.25
# …and the CLERK'S STAMP occupies the page's top 18% — 35.6 to 143.2 of
# 792, measured over the 22 records that print one. 0.25 leaves a line of
# margin on that, and it is only ever asked of a page that already carries a
# divider under a repeat of this document's own banner.
_STAMP_TOP_MAX = 0.25
# THE PAGE'S OWN AXIS. The banner and the division label centre within
# 0.2pt of it (305.85 and 306.0 against 306.0); the nearest stamp row
# centres 146pt off it, and Division III's 176pt off.
_AXIS_TOL = 40.0
# THE PAPER'S OWN LABELS, set in the caption's right column. Closed
# vocabularies, all of them: the court's own docket opener, the division it
# sits in, and what the paper calls itself.
_DOCKET_OPENERS = ("no.", "nos.", "no ", "cause no.")
_DIVISION = re.compile(r"^DIVISION(ONE|TWO|THREE|I|II|III)\.?$")
_TITLE_OPENERS = ("published", "unpublished", "order", "opinion", "amended",
                  "corrected", "substituted")
# PUBLICATION STATUS is what the paper calls ITSELF, and only that. 'ORDER
# GRANTING MOTION TO PUBLISH AND PUBLISHING OPINION' names an act of the
# court, not the status of this paper, and aiden's own opinion cover still
# reads UNPUBLISHED under it — so the status is read from an exact label.
_STATUS = {"PUBLISHED OPINION": "published",
           "UNPUBLISHED OPINION": "unpublished"}
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Za-z]{3,9})\.?\s*(\d{1,2}),\s*(\d{4})")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant",
    "applicants", "cross", "third", "party", "interest", "in", "of",
    "and", "the", "pro", "se", "below", "deceased",
)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_banner(text: str) -> bool:
    """The court naming itself: 'IN THE COURT OF APPEALS OF THE STATE OF
    WASHINGTON'. All 42 records print it, once above the caption."""
    low = _norm(text).lower().rstrip(".")
    return "court of appeals of the state of washington" in low


def _is_division(text: str) -> bool:
    """'DIVISION ONE' / 'DIVISION  II' / 'DIVISION THREE' — the court naming
    the division it sits in. Matched on the SPACE-FREE form: pdfio breaks
    Division II's label at the rail it straddles ('DIVISI' + 'ON  II'), so
    the word spacing of the row as delivered is an accident of where the
    rule was drawn, not something the page said."""
    flat = re.sub(r"\s+", "", _norm(text).upper())
    return _DIVISION.match(flat) is not None


def _is_typed_rule(text: str) -> bool:
    """A fence the court TYPED rather than drew: a run of underscores,
    sometimes carrying the rail's own glyph at its right end.

    Measured, washctapp never types its fence — it draws all 37 and leaves
    Division III's 5 unfenced. The 16 underscore runs in the corpus are all
    signature lines on a LAST page, and the nearest one to a fence
    (boyce's 'JUDGE' rule, x 72.0-291.3 under a rail at 312.3) is still
    10.7pt short of the reach test. Kept because the sibling court types the
    same fence the same way, and a typed rule that DOES reach the rail is
    the fence whatever drew it."""
    flat = _norm(text).rstrip(")")
    return len(flat) >= 8 and set(flat) <= set("_")


def _find_date(text: str) -> str | None:
    """The date the clerk's stamp states, as printed. The MONTH is a closed
    vocabulary and the two Divisions set it in different case ('June 30,
    2026' / 'JULY 21, 2026'), so the match is case-insensitive and the
    printed form is what is kept."""
    mm = _DATE.search(_norm(text))
    if mm is None or mm.group(1).lower() not in _MONTHS:
        return None
    return _norm(mm.group(0))


def _measure(geom) -> tuple[float, float]:
    """The body rail and the measure, as the document sets them."""
    x0 = geom.body_x0 if geom else 72.0
    x1 = geom.right_x1 if geom else 540.0
    return x0, max(x1 - x0, 1.0)


def _is_prose(line, geom) -> bool:
    """Body prose: the FULL MEASURE at the body rail."""
    x0, measure = _measure(geom)
    return (line.x0 <= x0 + 2.0
            and (line.x1 - line.x0) >= _PROSE_INK * measure)


# --------------------------------------------------------------------------
# the divider — washctapp's caption contract, and the dispatch
# --------------------------------------------------------------------------

def _paren_rail(pm, size: float, at_x: float | None = None) -> dict | None:
    """The typed ')' divider on ``pm``: {'x','top','bottom'}, or None.

    ``at_x`` asks for the CONTINUATION of a rail an earlier page proved.

    The stack is cut at its own PITCH: a prose ')' that happens to share the
    rail's column is 2x the leading away from the rail's last glyph, and
    taken in it drove teamsters' band into the opinion."""
    from collections import Counter

    lo, hi = pm.width * _RAIL_BAND[0], pm.width * _RAIL_BAND[1]
    chars = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == ")" and lo <= c["x0"] <= hi]
    floor = _PAREN_CONT_FLOOR if at_x is not None else _PAREN_FLOOR
    if at_x is not None:
        stack = [c for c in chars if abs(c["x0"] - at_x) <= _RAIL_WINDOW]
        x = at_x
    else:
        if len(chars) < floor:
            return None
        x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
        stack = [c for c in chars if abs(c["x0"] - x) <= _RAIL_WINDOW]
    if len(stack) < floor:
        return None
    stack.sort(key=lambda c: c["top"])
    steps = [b["top"] - a["top"] for a, b in zip(stack, stack[1:])]
    pitch = median(steps) if steps else (size or 12.0)
    runs: list = [[stack[0]]]
    for c in stack[1:]:
        if c["top"] - runs[-1][-1]["top"] <= max(pitch, 1.0) * _PITCH_BREAK:
            runs[-1].append(c)
        else:
            runs.append([c])
    best = max(runs, key=len)
    if len(best) < floor:
        return None
    return {"x": float(x), "top": min(c["top"] for c in best),
            "bottom": max(c["bottom"] for c in best)}


def _ruled_rail(pm, at_x: float | None = None) -> dict | None:
    """The DRAWN divider: a tall vertical with caption text on both sides.

    A divider has to DIVIDE. This court draws no box around its caption —
    the one vertical it sets IS the column split — but aiden boxes the first
    case of a consolidated stack, and only the rule with ink on both sides
    of it is the divider."""
    lo, hi = pm.width * _RAIL_BAND[0], pm.width * _RAIL_BAND[1]
    tall = [r for r in pm.v_rules
            if r.height >= _VRULE_MIN_H and lo <= r.x <= hi
            and (at_x is None or abs(r.x - at_x) <= _RAIL_WINDOW)]
    if not tall:
        return None
    if at_x is not None:
        # A CONTINUATION NEED NOT DIVIDE: the page before it proved the
        # column, and a caption that wrapped carries only its LEFT stack
        # onto the next page (rosalinda prints nothing right of the rule
        # there).
        r = max(tall, key=lambda r: r.height)
        return {"x": float(r.x), "top": r.top, "bottom": r.bottom}

    def divides(rule) -> bool:
        left = right = False
        for line in pm.lines:
            if not (rule.top - 2 <= line.top <= rule.bottom + 2):
                continue
            for c in line.chars:
                if not (c.get("text") or "").strip():
                    continue
                if c["x1"] <= rule.x - 2:
                    left = True
                elif c["x0"] >= rule.x + 2:
                    right = True
        return left and right

    for rule in sorted(tall, key=lambda r: -r.height):
        if divides(rule):
            return {"x": float(rule.x), "top": rule.top, "bottom": rule.bottom}
    return None


def _fences(pm, rail_x: float, rows: list, body_x0: float,
            pno_of: dict) -> list:
    """Tops of the caption fence on ``pm`` — the rule this court closes its
    caption with and repeats between consolidated cases, DRAWN or TYPED.
    Both are identified by their right end reaching the rail."""
    out = [r.top for r in pm.h_rules
           if r.x0 <= body_x0 + _FENCE_X0_MAX and r.x1 >= rail_x - _FENCE_REACH]
    for line in rows:
        if (pno_of.get(line.id) == pm.number and _is_typed_rule(line.plain)
                and line.x0 <= body_x0 + _FENCE_X0_MAX
                and line.x1 >= rail_x - _FENCE_REACH):
            out.append(line.top)
    return sorted(set(out))


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _sub(line, keep: list):
    """``line`` carrying only ``keep``'s glyphs, or None where none are ink."""
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _cap_size(lines: list) -> float:
    """THE CAPTION'S OWN TYPE, read off the band. Measured over the corpus it
    is 12.0pt in Divisions I and II and 13.0 in Division III, and it is
    always the band's dominant size by an order of magnitude (78-830 glyphs
    against the 10 of a division label)."""
    from collections import Counter

    tally = Counter()
    for line in lines:
        for c in line.chars:
            if (c.get("text") or "").strip():
                tally[round(c.get("size") or 0.0, 1)] += 1
    return tally.most_common(1)[0][0] if tally else 0.0


def _masthead_chars(line, cap_size: float) -> list:
    """The glyphs on ``line`` the page set LARGER than the caption.

    Measured over all 42 records: the only run inside a caption band set
    above the band's own type is Division II's division label — 10 glyphs at
    14.0pt against a 12.0pt caption, on all 12 records that print it there,
    and nothing else anywhere in the corpus. That is what separates the
    label from a party cell printed hard against it: burney sets 'FREDERICK
    BURNEY, individually,' and 'DIVISION II' with NO gap between them, so
    no column test and no run-gap test can tell them apart, and ball glues
    the docket on the other side of it as well. (A dagger footnote mark is
    set SMALLER — 8.0pt — and stays in the cell where the page put it.)"""
    if cap_size <= 0:
        return []
    return [c for c in line.chars
            if (c.get("text") or "").strip()
            and round(c.get("size") or 0.0, 1) >= cap_size + _SIZE_STEP]


def _shed_rail(chars: list, rail_x: float, glyph: str | None) -> list:
    """``chars`` with the divider's own glyphs removed. The glyph is
    identified by its COLUMN, never by its character — the ')' that closes
    '(consolidated with Nos. …)' stays."""
    if glyph is None:
        return chars
    lo, hi = rail_x - _RAIL_WINDOW, rail_x + _RAIL_WINDOW
    return [c for c in chars
            if not ((c.get("text") or "") == glyph and lo <= c["x0"] <= hi)]


def _unfence(line, fence_tops: list):
    """``line`` with any underline the CAPTION FENCE put on it cleared.

    A drawn rule whose ends coincide with the row above is an underline; a
    239pt rule anchored on the left margin under a 76pt cell set at x=221 is
    not. pdfio tags by vertical proximity alone, so the caption's closing
    fence arrives as an underline on whatever row it happens to follow. The
    fence is structure — it renders as the rule the page drew, once."""
    if not fence_tops or not line.chars:
        return line
    base = max(c["bottom"] for c in line.chars)
    if not any(-2.5 <= (t - base) <= 6.0 for t in fence_tops):
        return line
    if not any(c.get("_underline") for c in line.chars):
        return line
    kept = []
    for c in line.chars:
        if c.get("_underline"):
            c = dict(c)
            c.pop("_underline", None)
        kept.append(c)
    return _replace(line, chars=kept)


def _cell(parts: list, pm, role: str):
    """One column's cell on one printed row, from the runs that fell in it."""
    parts = sorted(parts, key=lambda l: l.x0)
    text = ""
    for p in parts:
        piece = line_markup(p)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(pm.number, tuple(dict.fromkeys(
            p.id for p in parts))),
        align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
        bold=all(p.all_bold for p in parts), role=role)


def _caption_block(rows: list, rail_x: float, glyph: str | None, pm,
                   style_id: str, cap_size: float):
    """One caption case as a CaptionBlock, plus each column's plain text.
    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned."""
    left, right, left_plain, right_plain = [], [], [], []
    for row in rows:
        l_parts, r_parts = [], []
        for line in row:
            big = {id(c) for c in _masthead_chars(line, cap_size)}
            kept = [c for c in _shed_rail(line.chars, rail_x, glyph)
                    if id(c) not in big]
            for want_left in (True, False):
                part = _sub(line, [c for c in kept
                                   if (((c["x0"] + c.get("x1", c["x0"])) / 2
                                        < rail_x) is want_left)])
                if part is not None:
                    (l_parts if want_left else r_parts).append(part)
        left.append(_cell(l_parts, pm, "caption") if l_parts
                    else m.HmLine(text="", prov=m.Prov(pm.number),
                                  role="caption"))
        right.append(_cell(r_parts, pm, "caption") if r_parts
                     else m.HmLine(text="", prov=m.Prov(pm.number),
                                   role="caption"))
        left_plain.append(_norm(" ".join(p.plain for p in l_parts)))
        right_plain.append(_norm(" ".join(p.plain for p in r_parts)))
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: the rows that
    # held nothing but a rail glyph are empty on both sides, and left
    # standing they render as phantom blank rows at the block's foot.
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted({l.id for row in rows for l in row}))
    block = m.CaptionBlock(
        left=left, right=right, rail=glyph or "|", rail_rows=len(left),
        style_id=style_id,
        fp={"rail": glyph or "drawn", "mid_x": rail_x},
        prov=m.Prov(pm.number, ids))
    return block, left_plain, right_plain


def _sides(rows: list):
    """The party names either side of the 'v.' pivot, built from the party
    NAMES — never by joining the caption wholesale, because the status
    labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side, seen = left, False
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        head = flat.split()[0].rstrip(".").lower()
        if head in ("v", "vs") and len(flat) <= 6:
            side, seen = right, True
            continue
        if set(flat) <= set("_-–— )") and len(flat) >= 3:
            continue          # the court's own typed fence, not a name
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    # THE COMMA is the caption's own apparatus, leading to the status row
    # under it; the FULL STOP is not — it ends the abbreviation a party is
    # incorporated under ('TRIPLE M CONSTRUCTION, LLC.').
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _docket_tail(text: str) -> bool:
    """Does ``text`` CONTINUE the docket cell above it? A docket wrap carries
    no prose — '(consolidated with Nos. 60331-4-II and' / '60335-7-II)'.
    Every word is a number, a court's own abbreviation, or the conjunction
    that joins them."""
    flat = _norm(text)
    core = re.sub(r"[()]", " ", flat).strip()
    if not core:
        return True
    words = [w.strip(".,/") for w in core.split()]
    return all(any(ch.isdigit() for ch in w)
               or w.lower() in ("no", "nos", "consolidated", "cons", "with",
                                "w", "and", "&")
               for w in words if w)


# --------------------------------------------------------------------------
# the front block a stapled OPINION prints over the ORDER that published it
# --------------------------------------------------------------------------

def _reprint_block(pm, rows, find_rail, banner: str | None, geom, size,
                   body_x0, pno_of: dict, sane: bool):
    """The WHOLE front block, printed again to open the stapled opinion.

    Page 1's own contract, applied to a later page: a divider in the top
    band, the court's banner as the last row above it, the caption's fence
    closing the band under it, and no body prose anywhere in it. The banner
    is the row THIS document printed on page 1, never a wording list.
    Returns ``{'stamps', 'banner', 'band', 'rail_x'}`` or None."""
    if banner is None:
        return None
    r = find_rail(pm)
    if r is None or r["top"] > pm.height * _RAIL_TOP_MAX:
        return None
    page_rows = [l for l in rows if pno_of[l.id] == pm.number]
    if not page_rows:
        return None
    top = r["top"] - 6.0
    fs = _fences(pm, r["x"], rows, body_x0, pno_of)
    close = [t for t in fs if t >= r["bottom"] - _FENCE_DROP]
    bottom = (close[0] if close else r["bottom"]) + 2.0
    above = [l for l in page_rows if l.top < top]
    band = [l for l in page_rows if top <= l.top <= bottom]
    if not above or not band:
        return None
    # THE BLOCK OPENS THE PAGE: no part of the writing above it is printed
    # here. `above` already holds every non-furniture row over the rail, and
    # what may stand there is the clerk's stamp and nothing else — measured,
    # the stamp occupies the page's top 18% (35.6 to 143.2 of 792). A
    # threshold on the BLOCK's own first row would be the wrong test and was
    # the wrong test: burns sets its second banner at 0.29 of the page and a
    # top-band rule on it refused the very block it was written for.
    if any(l.top > pm.height * _STAMP_TOP_MAX for l in above
           if not _is_banner(l.plain) and not _is_division(l.plain)):
        return None
    # THE BANNER, AND WHAT THE COURT PRINTS UNDER IT. Nothing may stand
    # between the banner and the caption but the division the court sits in
    # — aiden's second cover sets 'IN THE COURT OF APPEALS …' over 'DIVISION
    # II' over the caption, so a rule that wants the banner as the LAST row
    # above the rail refuses the block it is looking for.
    found = [i for i, l in enumerate(above)
             if _is_banner(l.plain) and _norm(l.plain).upper() == banner]
    if not found:
        return None
    at = found[-1]
    if not all(_is_division(l.plain) for l in above[at + 1:]):
        return None
    if sane and any(_is_prose(l, geom) for l in above + band):
        return None
    return {"stamps": above[:at], "banner": above[at],
            "masthead": above[at + 1:], "band": band, "rail_x": r["x"]}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="washctapp")
def read_headmatter_washctapp(model, geom, **_):
    """Read washctapp's caption-divider headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0, measure = _measure(geom)
    size = (geom.body_size if geom else 12.0) or 12.0
    sane = measure >= _MIN_MEASURE * page1.width

    rail = _paren_rail(page1, size)
    if rail is not None and rail["top"] > page1.height * _RAIL_TOP_MAX:
        rail = None               # too deep in the page to be a caption
    if rail is not None:
        style, glyph, style_id = STYLE_PAREN_RAIL, ")", "parenthetical-box"
        find_rail = lambda pm, at_x=None: _paren_rail(pm, size, at_x)  # noqa: E731
    else:
        rail = _ruled_rail(page1)
        if rail is None or rail["top"] > page1.height * _RAIL_TOP_MAX:
            return NOTHING        # no caption divider: not this court's paper
        style, glyph, style_id = STYLE_RULED_RAIL, None, "ruled-rail"
        find_rail = _ruled_rail

    finder = FurnitureFinder(model, body_x0, size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see. Furniture — the running head each page
    # after the first restates, the bare centred folio — is core's and is
    # passed over here, so it can never be mistaken for a caption row. It is
    # not re-recorded either: core's furniture pass runs BEFORE this reader
    # and drops what it takes outright, so a second record would put the
    # same running head in the Removed box twice.
    # …and the list runs the WHOLE document, not just the front pages: the
    # same furniture test decides what the stapled opinion's own front block
    # is, many pages down.
    # A STAPLED PART IS NUMBERED FROM ITS OWN FIRST PAGE. Core cuts a PDF
    # that staples two filings into parts and processes each with local page
    # numbering (`pm.number` 1..n), then shifts every prov page by the
    # part's offset — but `Line.page` keeps the number of the PDF it was
    # read from. So the page a row is on is the PAGE's number, never the
    # line's: read off the line, part 2 of aiden matched no row at all
    # ('page 1' never occurs in it) and the reader silently declined, and a
    # prov built from it would be shifted twice.
    rows: list = []
    pno_of: dict = {}
    for pm in model.pages:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            pno_of[line.id] = pm.number
            rows.append(line)
    rows.sort(key=lambda l: (pno_of[l.id], l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BANDS. The caption occupies the divider's own vertical span, closed
    # by the fence the court sets under it and never reaching the court's own
    # prose — and a caption too long for one page runs onto the next, where
    # the court sets the divider again and fences it there.
    bands: dict = {}
    fences: dict = {}
    for pm in model.pages[:_MAX_PAGES]:
        if pm.number > 1:
            # A CAPTION CONTINUES ONLY WHERE IT RAN OUT OF PAGE. Anything
            # printed under the previous page's fence closed the caption
            # there, and a divider on the next page is then some other
            # page's punctuation.
            prev = bands.get(pm.number - 1)
            if prev is None or any(pno_of[l.id] == pm.number - 1
                                   and l.top > prev[1] for l in rows):
                break
            r = find_rail(pm, rail["x"])
        else:
            r = rail
        if r is None:
            break
        fs = _fences(pm, r["x"], rows, body_x0, pno_of)
        close = [t for t in fs if t >= r["bottom"] - _FENCE_DROP]
        bottom = close[0] if close else r["bottom"]
        # …AND NEVER PAST THE COURT'S OWN PROSE. Measured, this never
        # fires: on all 42 records the fence or the rail closes the band
        # above the first prose row. It is the backstop for a rail read
        # wrong, and it is written down because a rail WAS read wrong —
        # teamsters' '(County)' drove the band 193pt into the opinion until
        # the rail's own pitch cut it.
        prose = [l.top for l in rows
                 if pno_of[l.id] == pm.number and r["top"] < l.top <= bottom
                 and _is_prose(l, geom)] if sane else []
        if prose:
            bottom = min(prose) - 2.0
        bands[pm.number] = (r["top"] - 6.0, bottom + 2.0)
        fences[pm.number] = [t for t in fs if r["top"] < t <= bottom + 1]

    if 1 not in bands:
        return NOTHING

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    stamp_lines: list = []
    banner_rows: list = []
    division_rows: list = []
    caption_rows: list = []
    right_rows: list = []
    parties: list = []
    case_name: str | None = None

    def emit(parts, role: str):
        """One HEADMATTER ROW, from the one or more runs the page set on that
        baseline."""
        parts = sorted(parts, key=lambda l: l.x0)
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(dict.fromkeys(
                p.id for p in parts))),
            align=m.Align("C" if role == "court" else "L"),
            x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role))
        consumed.update(p.id for p in parts)

    # ---- the masthead: everything page 1 prints above the caption -------
    # THE MASTHEAD STANDS ON THE PAGE'S OWN AXIS and the stamp does not:
    # measured over the corpus the banner and the division label centre
    # within 0.2pt of it, and the nearest stamp row centres 146pt off it.
    # That distinction has to be made, because Division II's stamp names the
    # division too ('Filed / Washington State / Court of Appeals / Division
    # Two / <date>') and read by its wording alone it renders as the court's
    # own masthead on 17 records.
    axis = page1.width / 2
    top_of_caption = bands[1][0]
    for line in rows:
        if pno_of[line.id] != 1 or line.top >= top_of_caption:
            continue
        on_axis = abs((line.x0 + line.x1) / 2 - axis) <= _AXIS_TOL
        if on_axis and _is_banner(line.plain):
            banner_rows.append(_norm(line.plain))
            emit([line], "court")
        elif on_axis and _is_division(line.plain):
            division_rows.append(_norm(line.plain))
            emit([line], "court")
        else:
            # EVERYTHING ELSE ABOVE THE CAPTION IS THE CLERK'S STAMP —
            # furniture, recorded, never rendered as front matter. Measured
            # over the corpus, page 1 prints nothing else there.
            stamp_lines.append(line)

    # ---- the caption ----------------------------------------------------
    for pno, (top, bottom) in sorted(bands.items()):
        pm = pages[pno]
        band_lines = [l for l in rows
                      if pno_of[l.id] == pno and top <= l.top <= bottom]
        if not band_lines:
            continue
        fence_tops = fences.get(pno) or []
        visual: list = []
        for line in sorted(band_lines, key=lambda l: (l.top, l.x0)):
            line = _unfence(line, fence_tops)
            if visual and abs(visual[-1][0].top - line.top) <= 2:
                visual[-1].append(line)
            else:
                visual.append([line])
        # A GLYPH SET LARGER THAN THE CAPTION IS THE MASTHEAD'S, NOT THE
        # CAPTION'S — Division II centres its division label on the page
        # axis at the caption's own first baseline, so it straddles the rail
        # and, in burney and ball, abuts the cells either side of it with no
        # gap at all. The caption does not cross its own divider; nor does
        # it change type in the middle of a row. A larger run that is NOT
        # that label is a shape this file has not measured, and the whole
        # record is declined rather than forced through the contract.
        cap_size = _cap_size(band_lines)
        for row in visual:
            big = [(l, _masthead_chars(l, cap_size)) for l in row]
            big = [(l, cs) for l, cs in big if cs]
            if not big:
                continue
            # ONE PRINTED ROW IS ONE ROW even where the rule it straddles
            # made pdfio deliver it as two: the glyphs are gathered back onto
            # one line so the label reads as the page set it, and every id
            # they came from is claimed.
            chars = sorted((c for _l, cs in big for c in cs),
                           key=lambda c: c["x0"])
            whole = _replace(big[0][0], chars=chars,
                             x0=min(c["x0"] for c in chars),
                             x1=max(c.get("x1", c["x0"]) for c in chars))
            if not _is_division(whole.plain):
                return NOTHING
            division_rows.append(_norm(whole.plain))
            consumed.update(l.id for l, _cs in big)
            items.append(m.HmLine(
                text=line_markup(whole), prov=m.Prov(
                    pno, tuple(dict.fromkeys(l.id for l, _cs in big))),
                align=m.Align("C"), x0=whole.x0, size=whole.size or 0.0,
                bold=whole.all_bold, role="court"))
        # A consolidated caption is FENCED CASE BY CASE; each fenced group is
        # one caption and the rule between them renders where the page sets
        # it.
        groups: list = [[]]
        cuts = list(fence_tops)
        for row in visual:
            while cuts and row[0].top > cuts[0]:
                cuts.pop(0)
                groups.append([])
            groups[-1].append(row)
        head_prov = m.Prov(pno, tuple(l.id for l in visual[0]))
        for group in groups:
            if not group:
                continue
            block, lp, rp = _caption_block(group, rail["x"], glyph, pm,
                                           style_id, cap_size)
            if block is None:
                continue
            items.append(block)
            consumed.update(block.prov.line_ids)
            caption_rows.extend(t for t in lp if t)
            tops = [g[0].top for g in group][:len(block.right)]
            right_rows.extend(
                (r, t, y) for r, t, y in zip(block.right, rp, tops) if t)
            sides = _sides(lp)
            for s in sides:
                if s and s not in parties:
                    parties.append(s)
            if case_name is None and len(sides) == 2:
                case_name = f"{sides[0]} v. {sides[1]}"
            elif case_name is None and len(sides) == 1:
                case_name = sides[0]
        # A RULE RENDERS WHERE THE PAGE DRAWS IT — it carries the provenance
        # of the row it follows, so the merge by position puts it back
        # between the cases it separates.
        for t in fence_tops:
            above = [l for l in band_lines if l.top < t]
            prov = m.Prov(pno, tuple(l.id for l in above[-3:])) if above \
                else head_prov
            items.append(m.Rule(prov=prov, span="left"))

    if not caption_rows and not right_rows:
        return NOTHING

    # ---- what the caption's right column says ----------------------------
    # A LABEL STACK, and every label in it is the court's own closed
    # vocabulary: the number this court gave the case, the division it sits
    # in, and what the paper calls itself. A row that opens none of them
    # continues the one above it or stays caption.
    prev_role = None
    docket_cells: list = []
    title_cells: list = []
    for row, flat, _y in right_rows:
        low = flat.lower().lstrip("(")
        if low.startswith(_DOCKET_OPENERS) and any(c.isdigit() for c in flat):
            row.role = "docket"
            docket_cells.append(flat)
        elif _is_division(flat):
            row.role = "court"
            if _norm(flat) not in division_rows:
                division_rows.append(_norm(flat))
        elif low.startswith(_TITLE_OPENERS):
            row.role = "publication" if _norm(flat).upper() in _STATUS \
                else "title"
            title_cells.append(flat)
        elif prev_role == "docket" and _docket_tail(flat):
            # A DOCKET CELL MAY WRAP: '(consolidated with Nos. 60331-4-II
            # and' / '60335-7-II)' is one number stated over two rows.
            row.role = "docket"
            if docket_cells:
                docket_cells[-1] = f"{docket_cells[-1]} {flat}"
        elif prev_role in ("title", "publication") and title_cells:
            # …AND SO MAY THE PAPER'S OWN NAME: 'ORDER GRANTING MOTION' /
            # 'TO PUBLISH, AND' / 'WITHDRAWING AND' / 'SUBSTITUTING OPINION'
            # is one title set over four rows.
            row.role = prev_role
            title_cells[-1] = f"{title_cells[-1]} {flat}"
        else:
            row.role = "caption"
        prev_role = row.role
    if docket_cells:
        crit["docket_number"] = docket_cells[0]
        if docket_cells[1:]:
            crit["other_dockets"] = docket_cells[1:]
    if title_cells:
        crit["title"] = _norm(title_cells[0])
        status = _STATUS.get(crit["title"].upper())
        if status:
            crit["publication_status"] = status

    # ---- what the block says --------------------------------------------
    if banner_rows or division_rows:
        crit["court"] = _norm(" ".join(banner_rows + division_rows))
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name

    # ---- the furniture of a CONTINUATION page ---------------------------
    # A CAPTION THAT RAN OUT OF PAGE carries on under the next page's
    # running head, and a reader that claims a region inherits its
    # furniture. Core's late sweep stops at a page the reader claimed, so
    # what stands in the top band above a continued band is recorded here.
    for pno, (top, _bottom) in sorted(bands.items()):
        if pno == 1:
            continue
        for line in rows:
            if pno_of[line.id] != pno or line.id in consumed:
                continue
            if line.top >= top or line.top > pages[pno].height * _TOP_BAND:
                continue
            dropped.append(m.Dropped(
                text=_norm(line.plain), prov=m.Prov(pno, (line.id,)),
                kind="running-head"))
            consumed.add(line.id)

    # ---- the front block the STAPLED OPINION prints over itself ---------
    # Claimed, not moved — see the module docstring. The scan starts below
    # the last page the caption itself used, so a caption that ran onto page
    # 2 is never read twice.
    banner = _norm(banner_rows[0]).upper() if banner_rows else None
    scan = [l for l in rows if l.id not in consumed]
    for pm in model.pages[max(bands):]:
        block = _reprint_block(pm, scan, find_rail, banner, geom, size,
                               body_x0, pno_of, sane)
        if block is None:
            continue
        # THE CLERK'S STAMP is the same furniture page 1 prints, so it is
        # recorded the same way, one Dropped per printed row.
        for line in block["stamps"]:
            dropped.append(m.Dropped(
                text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
                kind="stamp"))
            consumed.add(line.id)
        # THE CAPTION, recorded COLUMN BY COLUMN. Even an attestation never
        # joins across the drawn rule — reading order across it is the very
        # defect this claim removes.
        cols: list = []
        for line in block["band"]:
            for want_left in (True, False):
                part = _sub(line, [c for c in line.chars
                                   if (((c["x0"] + c.get("x1", c["x0"])) / 2
                                        < block["rail_x"]) is want_left)])
                if part is not None:
                    cols.append((want_left, part))
        printed = " ".join(
            [_norm(l.plain) for l in [block["banner"]] + block["masthead"]]
            + [_norm(p.plain) for left, p in cols if left]
            + [_norm(p.plain) for left, p in cols if not left])
        claimed = [block["banner"]] + block["masthead"] + block["band"]
        dropped.append(m.Dropped(
            text=printed[:1200],
            prov=m.Prov(pm.number, tuple(l.id for l in claimed)),
            kind="superfluous"))
        consumed.update(l.id for l in claimed)

    # ---- a claim must be TOTAL ------------------------------------------
    # THE CLERK'S STAMP, one Dropped per row the page printed — and the DATE
    # it carries, which is the only place this paper states when it was
    # filed.
    for line in stamp_lines:
        text = _norm(line.plain)
        got = _find_date(text)
        if got and "decision_date" not in crit:
            crit["decision_date"] = got
        dropped.append(m.Dropped(
            text=text, prov=m.Prov(line.page, (line.id,)), kind="stamp"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
