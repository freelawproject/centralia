"""Supreme Court of the State of Washington ('wash').

Everything unique to wash lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Washington files one paper and only one: a clerk-stamped slip
opinion whose front matter is a two-column caption held by a DIVIDER, closed
by a FENCE of half the body measure that ends AT that divider. Every one of
the 50 records in the corpus prints it, and nothing else stands between the
fence and the opinion's first byline — no appearance roster, no panel line,
no summary. The court sets the divider two ways, and the way it is set is
the only thing this file dispatches on:

    paren rail (33 of 50) — a stacked ')' at x 288-345 on a 612pt page:

        FILE / IN CLERK'S OFFICE / SUPREME COURT, STATE OF …    the stamps
        THIS OPINION WAS FILED FOR RECORD AT 8 A.M. ON …        (two of them)
        IN THE SUPREME COURT OF THE STATE OF WASHINGTON         the banner
        STATE OF WASHINGTON,          )                         the caption:
                     Respondent,      )  No. 103058-4             docket
              v.                      )  En Banc                  panel
        DUSTIN GENE ABRAMS            )  Filed: April 30, 2026    date
                     Petitioner.      )
        ─────────────────────────────╴  the fence: 252pt, ending AT the rail
        MADSEN, J.P.T.*—At issue in this case is whether RCW …  the opinion

    ruled rail (17 of 50) — the same caption with the divider DRAWN: one
    tall vertical rule at the same x, caption text on both sides of it,
    and the same half-measure fence closing the band at its foot.

        In the Matter of the Disciplinary Proceeding │ No. 202272-3
        Against                                      │ EN BANC
        SHAKESPEAR N. FEYISSA,                       │ Filed: June 11, 2026
        Lawyer (Bar No. 33747).                      │
        ────────────────────────────────────────────╴

Three consequences of reading the divider rather than the words:

  * COLUMN MEMBERSHIP IS DECIDED GLYPH BY GLYPH, not line by line. Whether
    pdfio broke a caption row at its column gap is an accident of how wide
    that gap happened to be — branson sets 'individually and on behalf of
    all others similarly )' as ONE run and ') No. 103394-0' as another, and
    a whole-line test puts the rail in whichever column it lands in.

  * THE FENCE IS THE CAPTION'S OWN, and the court types it as often as it
    draws it ('_______________________________________)' — buck, calloway,
    korsakas and eight more). Both forms end at the rail, which is what
    tells the fence from the 144pt footnote separator the same page prints
    at the same left margin.

  * A CONSOLIDATED RECORD IS FENCED CASE BY CASE, and a caption too long
    for one page carries the rail onto the next (j.m.i. sets three cases in
    one band; scott runs its band onto page 2 and fences it there).

THE STAMPS. Page 1 carries two clerk's stamps above the banner — a box at
the left ('FILE / IN CLERK'S OFFICE / SUPREME COURT, STATE OF WASHINGTON /
<date>') and free text at the right ('THIS OPINION WAS FILED FOR RECORD AT
8 A.M. ON / <date> / <clerk> / SUPREME COURT CLERK'). They are furniture and
are recorded as Dropped, never rendered as headmatter.

THE READER STOPS AT THE FENCE — or, where the court set none, at the foot of
the divider itself. Washington prints nothing between its caption and its
first byline, so the claim ends where the caption's own band ends and
everything below it — byline, opinion, footnotes — is core's. That bound is
GEOMETRIC, which is what lets the reader be right about a record whose first
byline core cannot yet parse ('PER CURIAM1— As explained below …'): a byline
test as the stop would have run the claim through the whole per-curiam
opinion.

WHAT THIS FILE DOES NOT DO. wash prints no appearance roster and no 'Before'
line — 'En Banc' is the whole of what it says about its bench — so there is
no counsel block and no panel block to read, and none is invented.

THE FRONT MATTER A SEPARATE WRITING PRINTS OVER ITSELF. A wash paper that
carries more than one writing sets each of them on a fresh page under its
own front matter, and that front matter belongs to the writing BELOW it.
Assembly anchors a writing at its byline, so left in the stream every one
of those rows falls into the writing ABOVE — which is what put a whole
reprinted caption, columns fused across the rule, at the foot of the per
curiam in a_better_richland_v._chilton. The court sets it two ways:

    THE WHOLE BLOCK AGAIN (2 records) — the clerk's two stamps, the banner,
    the caption in its rail and the fence, printed exactly as page 1 prints
    them. The GEOMETRY is page 1's, so it is read with page 1's measured
    rule: a divider in the page's top 45%, the banner as the last row above
    it, the fence closing the band. Nothing is matched against wording; the
    banner is compared against the row THIS document printed on page 1.

    THE WRITING'S OWN HEAD (57 rows on 38 records) — the docket alone, set
    CENTRED on the page's text block above the byline, under the page's
    running head:

        State v. Abrams                          <- the page's running head
                     No. 103058-4                <- the writing's own head
        JOHNSON, J. (concurrence)—While I agree …

    The centred row is identified by its geometry and by carrying a docket
    THIS document's own page-1 caption printed. Measured over the corpus,
    the row under every one of them is a separate writing's byline — 54 of
    54 in the sample where the head sits within 13.5pt of that axis, and
    the nearest row that is NOT a head stands 44pt off it.

AND THE CONTINUATION PAGE'S RUNNING HEAD, for the same reason: where the
caption ran onto page 2, core's late sweep leaves that page's running head
standing (it sweeps pages 3-74 and stops at a page the reader claimed), and
assembly opens a one-row ORDER on it — scott_v._amazon.com_inc. Recorded as
the `running-head` it is.

OWNERSHIP: ALL OF IT IS DROPPED, not moved. The reprint introduces the writing
that follows, so it must stop being the previous writing's body; and it
states nothing the document does not already print — the same court, the
same parties, the same docket, the same sitting, the same filing date, all
of which render whole in the headmatter at the head of the document, and
the head row is the docket criterion itself. There is nowhere better to put
it: a writing's `caption` field is filled by assembly, which runs after
this reader, so a court file cannot hand rows to a writing that does not
exist yet. So the rows are claimed and recorded as `Dropped` — attested,
never silently deleted — in the kinds the page itself distinguishes: the
clerk's stamps as `stamp`, exactly as page 1's are, the running head as
`running-head`, and the reprinted caption and head as `superfluous`.
Nothing court-WRITTEN is inside either block: the reprint holds no
full-measure row at the body rail, and the head run holds nothing but the
running head and the docket.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# wash's profile is registered in the shared table; this file owns its
# reader only. The reader never parses a byline — its claim is closed by
# the caption's own fence — so it needs no grammar of its own.

STYLE_PAREN_RAIL = "paren-rail caption"
STYLE_RULED_RAIL = "ruled-rail caption"

# ---- wash's declared facts (measured over the corpus, not tuned) --------
# THE DIVIDER'S COLUMN. Washington sets the caption's second column at one
# of five x positions — 288, 305, 308, 321, 342 on a 612pt page — which is
# 0.47 to 0.56 of the measure. The window is what keeps an ordinary
# parenthesis in the body ('RCW 9.94A.640(2)(e)') out of the rail: prose
# parentheses land wherever the line breaks, and a column of five of them
# at one x inside this window is the divider and nothing else.
_RAIL_BAND = (0.42, 0.62)
# …and the divider OPENS THE PAGE'S FRONT MATTER: page 1 sets the caption
# under the banner and nothing else above it. Measured, the rail starts at
# 0.20 to 0.29 of the page. Half the page is a wide margin on that, and it
# is what keeps a column of parentheses deep in a body table from ever
# reading as a caption.
_RAIL_TOP_MAX = 0.45
# A RAIL IS A COLUMN, not a count of glyphs anywhere on the page. Measured
# here the shortest rail runs 5 glyphs (in_re_recall_of_lauser) and the
# tallest 23 (anderson).
_PAREN_FLOOR = 5
# …but a caption that WRAPS THE PAGE carries fewer glyphs onto the next
# one. There the column is already proved, so two is enough.
_PAREN_CONT_FLOOR = 2
# A glyph belongs to the rail when it stands in the rail's own column. The
# rail's x0 varies by 0.3pt within a document and the nearest other ink on
# those rows is 25pt away.
_RAIL_WINDOW = 6.0
# THE DRAWN DIVIDER: one vertical rule spanning the caption band. Measured
# 96 to 511pt tall. A rule shorter than this is not a caption divider.
_VRULE_MIN_H = 80.0
# THE FENCE: a horizontal of HALF the body measure, anchored on the left
# margin and ending AT the divider — 216 to 270pt over the corpus. What
# identifies it is not its width but its RIGHT END: the 144pt footnote
# separator wash draws at the same left margin stops well short of the
# rail, and the 471pt appendix rule runs past the page's own text measure.
_FENCE_X0_MAX = 80.0
_FENCE_REACH = 10.0      # how near the rail the fence's right end must come
# HOW FAR BELOW THE RAIL a fence may still be the one that closes it. The
# court sets the fence on the rail's last row or within a line of it.
_FENCE_DROP = 30.0
# How far the front matter may run. Two pages is more than any wash record
# needs; the longest consolidated caption (scott) uses exactly two.
_MAX_PAGES = 3
# A caption's CONTINUATION opens the next page's top band.
_TOP_BAND = 0.25

# ---- the front matter a SEPARATE WRITING prints over itself ------------
# BODY PROSE runs the full measure at the body rail, and none is ever
# inside a reprinted block — measured, the widest row in one is the banner
# at 0.70 of the measure and it is centred, not at the rail. One
# full-measure row at the rail and the block is not this shape.
_PROSE_INK = 0.85
# THE WRITING'S OWN HEAD is CENTRED — on the page's own text block, not on
# the paper: a writing set on a wider measure (abrams' second concurrence,
# x0=108) centres its head on that measure, 18pt right of the page axis.
# Measured over every short docket row in a page's upper half, a head
# stands 0 to 13.5pt off that axis and the nearest row that is NOT one
# stands 44pt off (the docket cell of a reprinted caption) or 194pt off
# (luv's left-margin running head). 20pt is inside that gap.
_HEAD_AXIS_TOL = 20.0
# …and it stands in the page's UPPER HALF, above the byline. Measured
# 0.14 to 0.46 of the page.
_HEAD_TOP_MAX = 0.50
# WHAT MAY STAND ABOVE IT is the page's own running head, and nothing
# else: measured over the corpus, 0 to 2 rows, every one of them in the
# top 14% of the page and none wider than 0.72 of the measure. A row
# outside those bounds is not the head's furniture and is left where it
# is — that is what refuses a page whose previous writing is still
# running, since body prose reaches the full measure.
_HEAD_ABOVE_TOP = 0.18
_HEAD_ABOVE_INK = 0.80
_HEAD_ABOVE_MAX = 2
# A head row states a docket and nothing else.
_HEAD_MAX_CHARS = 60
# THE PAGE'S OWN MEASURE, read off the rows that reach it. 0.9 admits the
# byline row, which a paragraph indent shortens by one step.
_AXIS_INK = 0.90
# A DOCKET CARRIES A NUMBER. Washington's shortest is six digits
# ('202272-3'); five is the floor a page number could never reach.
_DOCKET_DIGITS = 5

# THE PAPER'S OWN LABELS, set in the caption's right column. Closed
# vocabularies, all of them: the court's own docket opener, the sitting it
# announces, and the clerk's filing line.
_DOCKET_OPENERS = ("no.", "nos.", "no ", "cause no.")
_EN_BANC = ("en banc", "en banc.")
_FILED_OPENERS = ("filed:", "filed")
# THE CERTIFYING COURT, as wash names it at the head of a certified
# question's caption. A closed set of openers, and the run ends on the
# court's own connector — the word 'IN' that introduces the parties.
_CERT_OPENER = "certification from"
# …and the certifying court's OWN case number, which wash sets in its
# right column under its own docket ('(certified 2:24-cv-01589-LK)').
_CERT_DOCKET = "certified"
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s*\d{1,2},\s+\d{4})")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant",
    "applicants", "cross", "third", "party", "interest", "in", "of",
    "and", "the", "pro", "se", "below",
)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_banner(text: str) -> bool:
    """The court naming itself: 'IN THE SUPREME COURT OF THE STATE OF
    WASHINGTON'. Applied only ABOVE the caption band, which is what keeps
    'CERTIFICATION FROM THE UNITED STATES DISTRICT COURT …' out of it."""
    low = _norm(text).lower().rstrip(".")
    return low.startswith("in the supreme court") and "washington" in low


def _is_typed_rule(text: str) -> bool:
    """The court types its fence as often as it draws it. The typed form is
    a run of underscores, sometimes carrying the rail's own glyph at its
    right end ('_______________________________________)')."""
    flat = _norm(text).rstrip(")")
    return len(flat) >= 8 and set(flat) <= set("_")


def _find_date(text: str) -> str | None:
    """The date the clerk's line states, as printed. The MONTH is a closed
    vocabulary and the clerk sometimes sets it tight against the day
    ('Filed: January15, 2026' — magana-arevalo), so the month is read as
    the row's leading run of letters, not as its first word."""
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    got = _norm(mm.group(1))
    head = re.match(r"[A-Za-z]+", got)
    return got if head and head.group(0).lower() in _MONTHS else None


# --------------------------------------------------------------------------
# the divider — wash's caption contract, and the dispatch
# --------------------------------------------------------------------------

def _paren_rail(pm, at_x: float | None = None) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None.

    ``at_x`` asks for the CONTINUATION of a rail an earlier page proved."""
    from collections import Counter

    lo, hi = pm.width * _RAIL_BAND[0], pm.width * _RAIL_BAND[1]
    chars = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == ")" and lo <= c["x0"] <= hi]
    if at_x is not None:
        stack = [c for c in chars if abs(c["x0"] - at_x) <= _RAIL_WINDOW]
        if len(stack) < _PAREN_CONT_FLOOR:
            return None
        return {"x": float(at_x), "top": min(c["top"] for c in stack),
                "bottom": max(c["bottom"] for c in stack)}
    if len(chars) < _PAREN_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    stack = [c for c in chars if abs(c["x0"] - x) <= _RAIL_WINDOW]
    if len(stack) < _PAREN_FLOOR:
        return None
    return {"x": float(x), "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _ruled_rail(pm, at_x: float | None = None) -> dict | None:
    """The DRAWN divider: a tall vertical with caption text on both sides.

    A divider has to DIVIDE. Washington draws no box around its caption —
    the one vertical it sets IS the column split — but a court that boxed
    its caption would offer a left border of the same height, and only the
    rule with ink on both sides of it is the divider."""
    lo, hi = pm.width * _RAIL_BAND[0], pm.width * _RAIL_BAND[1]
    tall = [r for r in pm.v_rules
            if r.height >= _VRULE_MIN_H and lo <= r.x <= hi
            and (at_x is None or abs(r.x - at_x) <= _RAIL_WINDOW)]
    if not tall:
        return None
    if at_x is not None:
        # A CONTINUATION NEED NOT DIVIDE. The page before it proved the
        # column, and a caption that wrapped carries only its LEFT stack
        # onto the next page — j.m.i. and scott both run their party lists
        # over and print nothing to the right of the rule there. Requiring
        # ink on both sides again lost those pages their caption.
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


def _fences(pm, rail_x: float, rows: list) -> list:
    """Tops of the caption fence on ``pm`` — the half-measure rule wash
    closes its caption with and repeats between consolidated cases, DRAWN
    or TYPED. Both are identified by their right end reaching the rail."""
    out = [r.top for r in pm.h_rules
           if r.x0 <= _FENCE_X0_MAX and r.x1 >= rail_x - _FENCE_REACH]
    for line in rows:
        if (line.page == pm.number and _is_typed_rule(line.plain)
                and line.x0 <= _FENCE_X0_MAX
                and line.x1 >= rail_x - _FENCE_REACH):
            out.append(line.top)
    return sorted(set(out))


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.
    Split GLYPH BY GLYPH — see the module docstring."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _shed_rail(line, rail_x: float, glyph: str | None):
    """``line`` with the divider's own glyphs removed, or None when the line
    WAS the divider. The glyph is identified by its COLUMN, never by its
    character — the ')' that closes '(Bar No. 33747)' stays."""
    if glyph is None:
        return line
    lo, hi = rail_x - _RAIL_WINDOW, rail_x + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == glyph and lo <= c["x0"] <= hi)]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    if len(kept) == len(line.chars):
        return line
    return _replace(line, chars=kept)


def _unfence(line, fence_tops: list):
    """``line`` with any underline the CAPTION FENCE put on it cleared.

    A drawn rule whose ends coincide with the row above is an underline; a
    252pt rule anchored on the left margin under a 76pt row set at x=180 is
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


def _caption_block(rows: list, rail_x: float, glyph: str | None, pm,
                   style_id: str):
    """One caption case as a CaptionBlock, plus each column's plain text.
    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned."""
    def cell(cells: list, role: str):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    left, right, left_plain, right_plain = [], [], [], []
    for row in rows:
        l_cells, r_cells = [], []
        for line in row:
            shed = _shed_rail(line, rail_x, glyph)
            if shed is None:
                continue
            for side, bucket in ((_side(shed, rail_x, "L"), l_cells),
                                 (_side(shed, rail_x, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left.append(cell(l_cells, "caption") if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number),
                                  role="caption"))
        right.append(cell(r_cells, "caption") if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number),
                                   role="caption"))
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: the rows that
    # held nothing but a rail glyph are empty on both sides, and left
    # standing they render as phantom blank rows at the block's foot.
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted(l.id for row in rows for l in row))
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
    # incorporated under ('WEST COAST SERVICING, INC.').
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _docket_tail(text: str) -> bool:
    """Does ``text`` CONTINUE the docket cell above it? A docket wrap
    carries no prose — '(consolidated with' / 'No. 103312-5)' / '(cons. w/
    103673-6)'. Every word is a number, a court's own abbreviation, or the
    conjunction that joins them."""
    flat = _norm(text)
    core = re.sub(r"[()]", " ", flat).strip()
    if not core:
        return True
    words = [w.strip(".,/") for w in core.split()]
    return all(any(ch.isdigit() for ch in w)
               or w.lower() in ("no", "nos", "consolidated", "cons", "with",
                                "w", "and", "&")
               for w in words if w)


def _stamp_runs(line) -> list:
    """The stamp text ``line`` actually prints, as separate rows.

    Washington's two page-1 stamps are set 9pt apart in a 9.4pt face, and
    pdfio's interleaved-baselines pass merges two of the right stamp's rows
    into one run of alternating glyphs ('FTOHRIS R OEPCIONRIODN A WT A8S A
    F.MIL.E ODN' is 'THIS OPINION WAS FILED' laid through 'FOR RECORD AT 8
    A.M. ON'). Recorded that way the Dropped box is unreadable. Cluster the
    row's glyphs back onto their own baselines — the chars carry them — and
    record what the page printed."""
    chars = [c for c in line.chars if (c.get("text") or "")]
    if not chars:
        return []
    tops = sorted({round(c["top"], 1) for c in chars})
    groups: list = []
    for t in tops:
        if groups and t - groups[-1][-1] <= 2.0:
            groups[-1].append(t)
        else:
            groups.append([t])
    if len(groups) < 2:
        return [_norm(line.plain)]
    out = []
    for g in groups:
        lo, hi = g[0] - 0.5, g[-1] + 0.5
        run = sorted((c for c in chars if lo <= c["top"] <= hi),
                     key=lambda c: c["x0"])
        text = _norm("".join(c.get("text") or "" for c in run))
        if text:
            out.append(text)
    return out


# --------------------------------------------------------------------------
# the front matter a SEPARATE WRITING prints over itself
# --------------------------------------------------------------------------

def _measure(geom) -> tuple[float, float]:
    """The body rail and the measure, as the document sets them."""
    x0 = geom.body_x0 if geom else 72.0
    x1 = geom.right_x1 if geom else 540.0
    return x0, max(x1 - x0, 1.0)


def _is_prose(line, geom) -> bool:
    """Body prose: the FULL MEASURE at the body rail. A caption cell is a
    column and a head row is short; neither ever reaches this."""
    x0, measure = _measure(geom)
    return (line.x0 <= x0 + 2.0
            and (line.x1 - line.x0) >= _PROSE_INK * measure)


def _text_axis(pm, page_rows) -> float:
    """The middle of the page's OWN text block — the axis its head is
    centred on.

    Measured from the page's WIDEST rows, not from the document's rail: a
    separate writing may be set on its own measure (abrams' second
    concurrence runs x0=108 to x1=537.6) and it centres its head on that
    measure, 18pt right of the paper's axis. The page axis is the
    fallback, for a page too short to show a measure."""
    if not page_rows:
        return pm.width / 2
    widest = max((l.x1 - l.x0) for l in page_rows)
    body = [l for l in page_rows if (l.x1 - l.x0) >= _AXIS_INK * widest]
    return (min(l.x0 for l in body) + max(l.x1 for l in body)) / 2


def _docket_key(text: str) -> str:
    """A docket's IDENTITY is its number, not its setting. The court prints
    the same one as 'No. 202,258-8' in the caption and 'No. 202258-8' at
    the head of a separate writing, and sets it tight ('No.104342-2') as
    often as loose, so what is compared is the run of digits and hyphens.
    '' where the row states no number."""
    key = re.sub(r"[^0-9-]", "", _norm(text)).strip("-")
    return key if sum(c.isdigit() for c in key) >= _DOCKET_DIGITS else ""


def _reprint_block(pm, rows, find_rail, banner: str | None, geom):
    """The WHOLE front block, printed again to open a separate writing.

    Page 1's own contract, applied to a later page: a divider in the top
    band, the court's banner as the last row above it, the caption's fence
    closing the band under it. The banner is the row THIS document printed
    on page 1, never a wording list. Returns
    ``{'stamps', 'banner', 'band', 'rail_x'}`` or None.
    """
    if banner is None:
        return None
    r = find_rail(pm)
    if r is None or r["top"] > pm.height * _RAIL_TOP_MAX:
        return None
    page_rows = [l for l in rows if l.page == pm.number]
    if not page_rows:
        return None
    top = r["top"] - 6.0
    fs = _fences(pm, r["x"], rows)
    close = [t for t in fs if t >= r["bottom"] - _FENCE_DROP]
    bottom = (close[0] if close else r["bottom"]) + 2.0
    above = [l for l in page_rows if l.top < top]
    band = [l for l in page_rows if top <= l.top <= bottom]
    if not above or not band:
        return None
    # THE BLOCK OPENS THE PAGE. Its first row stands in the top band, so
    # no part of the writing above it is printed here.
    if above[0].top > pm.height * _TOP_BAND:
        return None
    if _norm(above[-1].plain).upper() != banner:
        return None
    if any(_is_prose(l, geom) for l in above + band):
        return None
    return {"stamps": above[:-1], "banner": above[-1], "band": band,
            "rail_x": r["x"]}


def _writing_head(pm, rows, dockets: set, geom) -> list:
    """The head a separate writing prints over itself on ``pm``: the
    document's own docket set CENTRED above the byline, plus the running
    head standing over it. [] where the page prints no such row."""
    page_rows = [l for l in rows if l.page == pm.number]
    axis = _text_axis(pm, page_rows)
    _x0, measure = _measure(geom)
    for i, line in enumerate(page_rows):
        if line.top > pm.height * _HEAD_TOP_MAX:
            break
        flat = _norm(line.plain)
        if len(flat) > _HEAD_MAX_CHARS:
            continue
        if not flat.lower().lstrip("( ").startswith(_DOCKET_OPENERS):
            continue
        if _docket_key(flat) not in dockets:
            continue
        if abs((line.x0 + line.x1) / 2 - axis) > _HEAD_AXIS_TOL:
            continue
        # WHAT STANDS OVER IT is the page's running head or nothing.
        over = page_rows[:i]
        if (len(over) <= _HEAD_ABOVE_MAX
                and all(o.top <= pm.height * _HEAD_ABOVE_TOP
                        and (o.x1 - o.x0) <= _HEAD_ABOVE_INK * measure
                        for o in over)):
            return over + [line]
        return [line]
    return []


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="wash")
def read_headmatter_wash(model, geom, **_):
    """Read wash's caption-divider headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _paren_rail(page1)
    if rail is not None and rail["top"] > page1.height * _RAIL_TOP_MAX:
        rail = None               # too deep in the page to be a caption
    if rail is not None:
        style, glyph, style_id = STYLE_PAREN_RAIL, ")", "parenthetical-box"
        find_rail = _paren_rail
    else:
        rail = _ruled_rail(page1)
        if rail is None or rail["top"] > page1.height * _RAIL_TOP_MAX:
            return NOTHING        # no caption divider: not wash's paper
        style, glyph, style_id = STYLE_RULED_RAIL, None, "ruled-rail"
        find_rail = _ruled_rail

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see. Furniture — the running head each page
    # after the first restates, the bare centred folio, and whatever part
    # of the page-1 stamp zone core's own pass recognizes — is core's and
    # is passed over here, so it can never be mistaken for a caption row.
    # It is not re-recorded either: core's furniture pass runs BEFORE this
    # reader and drops what it takes outright, so a second record would
    # put the same running head in the Removed box twice. What that pass
    # leaves in the stamp zone is claimed below as the stamp it is.
    # …and the list runs the WHOLE document, not just the front pages: the
    # same furniture test decides what a separate writing's own front
    # matter is, many pages down.
    rows: list = []
    for pm in model.pages:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BANDS. The caption occupies the divider's own vertical span,
    # closed by the fence the court sets under it — and a caption too long
    # for one page runs onto the next, where the court sets the divider
    # again and fences it there.
    bands: dict = {}
    fences: dict = {}
    for pm in model.pages[:_MAX_PAGES]:
        if pm.number > 1:
            # A CAPTION CONTINUES ONLY WHERE IT RAN OUT OF PAGE. Anything
            # printed under the previous page's fence closed the caption
            # there, and a divider on the next page is then some other
            # page's punctuation.
            prev = bands.get(pm.number - 1)
            if prev is None or any(l.page == pm.number - 1 and l.top > prev[1]
                                   for l in rows):
                break
            r = find_rail(pm, at_x=rail["x"])
        else:
            r = rail
        if r is None:
            break
        fs = _fences(pm, r["x"], rows)
        close = [t for t in fs if t >= r["bottom"] - _FENCE_DROP]
        bottom = close[0] if close else r["bottom"]
        bands[pm.number] = (r["top"] - 6.0, bottom + 2.0)
        fences[pm.number] = [t for t in fs if r["top"] < t <= bottom + 1]
        # NO CLOSING FENCE MEANS THE CAPTION RAN OUT OF PAGE, which is
        # exactly when it continues — scott's band reaches y=676 of 792
        # with its last two cases still to set. What ends the walk is the
        # test above: a row printed BELOW the band closed the caption on
        # that page, and there is nothing to continue.

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    stamp_lines: list = []
    banner_rows: list = []
    caption_rows: list = []
    right_rows: list = []
    parties: list = []
    case_name: str | None = None

    def emit(row, role: str):
        """One HEADMATTER ROW, from the one or more line objects the page
        set on that baseline."""
        parts = sorted(row if isinstance(row, list) else [row],
                       key=lambda l: l.x0)
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align("C" if role == "court" else "L"),
            x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role))
        consumed.update(p.id for p in parts)

    # ---- the masthead: everything page 1 prints above the caption -------
    top_of_caption = bands.get(1, (10 ** 6, 0))[0]
    for line in rows:
        if line.page != 1 or line.top >= top_of_caption:
            continue
        if _is_banner(line.plain):
            banner_rows.append(_norm(line.plain))
            emit(line, "court")
        else:
            # EVERYTHING ELSE ABOVE THE BANNER IS THE CLERK'S STAMP —
            # furniture, recorded, never rendered as front matter.
            stamp_lines.append(line)

    # ---- the caption ----------------------------------------------------
    for pno, (top, bottom) in sorted(bands.items()):
        pm = pages[pno]
        band_lines = [l for l in rows
                      if l.page == pno and top <= l.top <= bottom]
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
        # A consolidated caption is FENCED CASE BY CASE; each fenced group
        # is one caption and the rule between them renders where the page
        # sets it.
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
                                           style_id)
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
        # A RULE RENDERS WHERE THE PAGE DRAWS IT — it carries the
        # provenance of the row it follows, so the merge by position puts
        # it back between the cases it separates.
        for t in fence_tops:
            above = [l for l in band_lines if l.top < t]
            prov = m.Prov(pno, tuple(l.id for l in above[-3:])) if above \
                else head_prov
            items.append(m.Rule(prov=prov, span="left"))

    if not caption_rows and not right_rows:
        return NOTHING

    # ---- what the caption's columns say ---------------------------------
    # THE RIGHT COLUMN is a label stack, and every one of its labels is
    # the court's own closed vocabulary: the number this court gave the
    # case, the sitting it announces, and the clerk's filing line. A row
    # that opens none of them continues the one above it or stays caption.
    prev_role = None
    docket_cells: list = []
    for row, flat, _y in right_rows:
        low = flat.lower().lstrip("(")
        if low.startswith(_DOCKET_OPENERS) and any(c.isdigit() for c in flat):
            row.role = "docket"
            docket_cells.append(flat)
        elif low.rstrip(".") in _EN_BANC:
            row.role = "panel"
            crit.setdefault("panel_line", _norm(flat))
        elif low.startswith(_FILED_OPENERS) and _find_date(flat):
            row.role = "date"
            crit.setdefault("decision_date", _find_date(flat))
        elif low.startswith(_CERT_DOCKET) and flat.startswith("("):
            # THE CERTIFYING COURT'S OWN NUMBER, not this court's and not a
            # companion appeal — the case downstairs, stated upstairs.
            row.role = "lower-court"
            crit.setdefault("lower_court_docket", []).append(flat.strip("()"))
        elif prev_role == "docket" and _docket_tail(flat):
            # A DOCKET CELL MAY WRAP: '(consolidated with' / 'No.
            # 103312-5)' is one number stated over three rows.
            row.role = "docket"
            if docket_cells:
                docket_cells[-1] = f"{docket_cells[-1]} {flat}"
        else:
            row.role = "caption"
        prev_role = row.role
    # AN UNBALANCED CLOSING PAREN IN A DOCKET CELL IS THE CAPTION'S OWN
    # GLYPH, not part of the number: ellis prints a second ')' 95pt right
    # of its rail on the docket row and nothing after it.
    docket_cells = [c.rstrip(" )") if ")" in c and "(" not in c else c
                    for c in docket_cells]
    if docket_cells:
        crit["docket_number"] = docket_cells[0]
        if docket_cells[1:]:
            crit["other_dockets"] = docket_cells[1:]

    # THE LEFT COLUMN of a certified question opens on the certifying
    # court, and the court's own connector ('… WASHINGTON IN') ends it.
    for block in [i for i in items if isinstance(i, m.CaptionBlock)]:
        origin: list = []
        spoke = closed = 0
        for cell in block.left:
            flat = _norm(_strip_tags(cell.text))
            if not flat:
                # THE RAIL'S OWN RHYTHM sets a blank row between the
                # court's, both before the statement and inside it. It
                # neither opens the run nor ends it.
                if origin:
                    origin.append(cell)
                continue
            if not spoke and not flat.lower().startswith(_CERT_OPENER):
                break
            origin.append(cell)
            spoke += 1
            if flat.rstrip(".").upper().endswith(" IN") or flat.upper() == "IN":
                closed = 1
                break
            if spoke >= 6:
                break     # no connector: this is not the court's statement
        if closed and spoke >= 2:
            for cell in origin:
                cell.role = "lower-court"
            printed = _norm(" ".join(_strip_tags(c.text) for c in origin))
            crit.setdefault("lower_court", printed.rstrip(" IN").rstrip())

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name

    # ---- the furniture of a CONTINUATION page ---------------------------
    # A CAPTION THAT RAN OUT OF PAGE carries on under the next page's
    # running head, and a reader that claims a region inherits its
    # furniture. Core's late sweep leaves that head standing on a page the
    # reader claimed — scott's 'Ruth Scott et al. v. Amazon.com, Inc., No.
    # 103730-9' is swept from pages 3-74 and survives on page 2, where
    # assembly then opens a one-row ORDER on it — so what stands in the
    # top band above a continued band is recorded here.
    for pno, (top, _bottom) in sorted(bands.items()):
        if pno == 1:
            continue
        for line in rows:
            if line.page != pno or line.id in consumed:
                continue
            if line.top >= top or line.top > pages[pno].height * _TOP_BAND:
                continue
            dropped.append(m.Dropped(
                text=_norm(line.plain), prov=m.Prov(pno, (line.id,)),
                kind="running-head"))
            consumed.add(line.id)

    # ---- what a SEPARATE WRITING prints over itself ---------------------
    # Claimed, not moved — see the module docstring. The scan starts below
    # the last page the caption itself used, so a caption that ran onto
    # page 2 is never read twice.
    banner = _norm(banner_rows[0]).upper() if banner_rows else None
    dockets = {_docket_key(c) for c in docket_cells}
    dockets |= {_docket_key(t) for _r, t, _y in right_rows
                if _norm(t).lower().lstrip("( ").startswith(_DOCKET_OPENERS)}
    dockets.discard("")
    scan = [l for l in rows if l.id not in consumed]
    for pm in model.pages[max(bands) if bands else 1:]:
        block = _reprint_block(pm, scan, find_rail, banner, geom)
        if block is not None:
            # THE CLERK'S STAMPS are the same furniture page 1 prints, so
            # they are recorded the same way, one Dropped per printed row.
            for line in block["stamps"]:
                for text in _stamp_runs(line):
                    dropped.append(m.Dropped(
                        text=text, prov=m.Prov(line.page, (line.id,)),
                        kind="stamp"))
                consumed.add(line.id)
            # THE CAPTION, recorded COLUMN BY COLUMN. Even an attestation
            # never joins across the drawn rule — reading order across it
            # is the very defect this claim removes.
            band = block["band"]
            left = [_side(l, block["rail_x"], "L") for l in band]
            right = [_side(l, block["rail_x"], "R") for l in band]
            printed = " ".join(
                _norm(l.plain) for l in
                [block["banner"]] + [c for c in left if c is not None]
                + [c for c in right if c is not None])
            claimed = [block["banner"]] + band
            dropped.append(m.Dropped(
                text=printed[:1200],
                prov=m.Prov(pm.number, tuple(l.id for l in claimed)),
                kind="superfluous"))
            consumed.update(l.id for l in claimed)
            continue
        head = _writing_head(pm, scan, dockets, geom)
        if head:
            dropped.append(m.Dropped(
                text=" ".join(_norm(l.plain) for l in head)[:1200],
                prov=m.Prov(pm.number, tuple(l.id for l in head)),
                kind="superfluous"))
            consumed.update(l.id for l in head)

    # ---- a claim must be TOTAL ------------------------------------------
    # THE CLERK'S STAMPS: two of them, and each is one Dropped row per line
    # the page actually printed.
    for line in stamp_lines:
        for text in _stamp_runs(line):
            dropped.append(m.Dropped(
                text=text, prov=m.Prov(line.page, (line.id,)), kind="stamp"))
        consumed.add(line.id)
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
