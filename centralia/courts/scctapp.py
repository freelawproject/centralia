"""The South Carolina Court of Appeals ('scctapp').

Everything unique to scctapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py.

WHICH SHAPE IS THIS? A DRAWN MARK — but a HORIZONTAL one, and there is no
second caption column at all. Measured over all 28 records, 6 pages each:
the only rules these pages draw are

    97.2pt at centre 306.0   140 of them — the BAND FENCE, on the page axis
   144.0pt at centre 144.0    74 of them — the footnote separator (x0=72)
   216.2pt at centre 252.1     1 of them — an UNDERLINE (hoffman p2), whose
                               ends coincide with the block-quote heading
                               'LAND USE AND BUILDING TYPE:' printed 11pt
                               above it at exactly 144.0-360.2

VERTICAL RULES, CORPUS-WIDE: ZERO — counted, not assumed. No typed `)` or
`:` column either: no row anywhere in the 28 records consists of rail glyphs
alone. The caption is ONE column standing at a single rail, x0 = 144.0 on
every party row of every record, and its wraps stand at that same 144.0
rather than being indented from it. So no divider is invented and NO
`CaptionBlock` is emitted — the iowactapp/nmctapp ruling, for the same
reason: the page does not draw one. Naming the shape is the finding, and the
shape is sc's: a DRAWN HORIZONTAL FENCE LADDER, no second column.

What the page DOES draw is the fence, and the fence is the parser. This is
its sibling court's contract exactly (see `sc.py`) — same publisher, same
ladder, same three positions — with the masthead naming a different court
and one band the Supreme Court never prints:

    ┌────────────────────────────────────────────────────────────────────┐
    │ THIS OPINION HAS NO PRECEDENTIAL VALUE.  IT SHOULD NOT BE          │
    │    CITED OR RELIED ON AS PRECEDENT IN ANY PROCEEDING   the notice,  │
    │       EXCEPT AS PROVIDED BY RULE 268(d)(2), SCACR.    7 records     │
    │                                                                    │
    │              THE STATE OF SOUTH CAROLINA        the masthead,      │
    │                 In The Court of Appeals         two rows, centred  │
    │                                                                    │
    │      The State, Respondent,                     the caption, at    │
    │      v.                                         the RAIL (x0=144)  │
    │      Barry Wayne Jones, Appellant.                                 │
    │                                                                    │
    │      Appellate Case No. 2022-000046             the DOCKET, last   │
    │                                                 row at the rail    │
    │                    ─────────────                a DRAWN fence      │
    │             Appeal From Edgefield County        the origin         │
    │      Walton J. McLeod, IV, Circuit Court Judge  …and its judge     │
    │                    ─────────────                                   │
    │                 Opinion No. 6147                the CITATION       │
    │      Heard March 11, 2025 – Filed June 10, 2026     the dates      │
    │                    ─────────────                                   │
    │                     AFFIRMED                    the disposition    │
    │                    ─────────────                                   │
    │      Senior Appellate Defender Lara Mary Caudy, of   counsel, at   │
    │      Columbia, for Appellant.                        the rail      │
    │                    ─────────────                                   │
    │ MCDONALD, J.: An Edgefield County jury convicted …  the writing,   │
    │                                                 at the BODY RAIL   │
    └────────────────────────────────────────────────────────────────────┘

THE FENCE GATE. On the axis within 6pt AND 85-140pt wide, which is sc's own
gate unchanged. Here the measure is a single value, 97.2pt, on all 140
fences; the gate is left wider than the measurement because the two things
it must exclude are far outside it either way — the footnote separator is
162pt off the axis, and the one underline is 54pt off it. Test the axis
first, the measure second.

THE RAIL SAYS 'CASE', THE AXIS SAYS 'PAPER', THE BODY RAIL SAYS 'WRITING'.
Three positions, measured on all 28 records and invariant:

  x0 = 144.0   the caption rail — parties, the docket row, and counsel;
  centred      everything the court says ABOUT the paper — masthead, the
               notice, origin, opinion number, dates, disposition;
  x0 =  72.0   the body rail — nothing in the headmatter stands there
               except the notice's FIRST row (x0=72.7, and it is above the
               masthead, so the walk has not opened yet when it passes),
               and the byline that opens the writing always does
               ('MCDONALD, J.:', 'PER CURIAM:', 'GEATHERS, J.:').

That last fact ends the reader and needs no byline vocabulary at all.

'UP' MEANS UNPUBLISHED, AND THE COURT SAYS SO TWICE. Seven of the 28 records
print a three-row precedential notice ABOVE the masthead, and those same
seven — and only those — number themselves '2026-UP-38x' and label the row
'Unpublished Opinion No.'. The other 21 carry a bare serial (6128-6156);
one of them says 'Published Opinion No. 6142' out loud. Two independent
signals, agreeing on all 28, so `publication_status` is written from either:
the notice, the 'Published'/'Unpublished' word, or a '####-UP-###' number.
The notice's rows take the `publication` role — it is the publication flag
this court prints, not furniture, and v1 renders it inside the headmatter
too. It is a RUN and it closes on its own sentence: bold, capitals, centred
on the axis, ending at the first row that ends in a period ('SCACR.').

CITATION IS NOT THE DOCKET, AND THIS COURT PRINTS BOTH. The trap that cost
`ill` its whole corpus (commit 03e8652). Two numbers, two positions, two
roles:

  'Appellate Case No. 2022-000046'  at the RAIL — identifies the APPEAL.
                                    -> role `docket`, `docket_number`
  'Opinion No. 6147' / 'Unpublished Opinion No. 2026-UP-389'  CENTRED, in
                                    its own fenced band — identifies the
                                    PAPER, and is what a South Carolina
                                    slip opinion is cited by before its
                                    S.E.2d cite exists.
                                    -> role `citation`, `citation`

Both are court-assigned and serial and they look alike to a text test; only
their POSITION and their labels separate them, and both are printed on all
28 records. The citation is stored as the row prints it, exactly as sc
stores 'Opinion No. 28325', because the label is part of the designation —
and because the court itself typed 'Opinion No. Op. 6138' on hoffman, which
a number-only field would silently normalise away.

CASE, NOT CAPS, SEPARATES THE ORIGIN FROM THE POSTURE — sc's rule, kept
because it costs nothing and this corpus does not exercise it: all 28
records print an origin band ('Appeal From Edgefield County' / 'Appeal From
The Administrative Law Court') and none prints a capitals-only posture. An
origin band always carries at least one mixed-case row because it names a
person; a posture band is capitals throughout.

THE CLAIM IS TOTAL OR IT IS NOTHING. Every row from the notice down to the
first body-rail row must land in a band this contract names. An
unrecognised row is not a licence to guess and not a licence to leave a
HOLE either — a hole lets core open a writing on the unclaimed row, and the
bisection invariant then pulls the claimed rows into it and the headmatter
renders empty. So an unrecognised row aborts the whole claim and core's
shared walk gets the record intact.

CORE ITEMS CLOSED HERE, NOT PATCHED (docs/core-patch-queue.md):

  item 41  `criteria.attorneys` is unreachable for a reader that keeps
           counsel in the headmatter. Closed the way five courts closed it
           today: this reader writes `crit["attorneys"]` itself from the
           rows it tagged `counsel`.
  item 6   a running head below core's repeat floor — not reachable here:
           these pages print no running head and no folio at all, on any
           page of any of the 28 records. Checked, not assumed. Nothing in
           the claimed region is furniture, so nothing survives it as a
           doctype heading (the ohioctcl shape does not occur).
  item 52  `conformed_signature_author` cannot read a bare judicial title —
           not reachable here either: this court BYLINES, it does not sign.
           All 28 records open their writing at the body rail with
           'NAME, J.:' or 'PER CURIAM:', and all 28 come back with an
           author. `authorless` never arises.

RECORDS DECLINED: NONE. All 28 match the contract and all 28 are read whole
(561 of 561 rendered headmatter rows tagged, no residual content, no dropped
rows). A record that did not match would return NOTHING and core's shared
walk would have it, which is the better outcome than a forced reading.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# --- the masthead ---------------------------------------------------------
# Two rows, centred, 14.0pt, on all 28 records. The words the court prints
# about itself are the landmark; the size is not (14.0pt is also the body
# size on every page of this corpus). Four records set the second row with
# doubled spaces ('In  The  Court  of  Appeals'), which is why every row is
# normalised before it is matched.
_MAST_STATE = re.compile(r"^THE STATE OF SOUTH CAROLINA$")
_MAST_COURT = re.compile(r"^In The Court of Appeals$")

# --- the closed labels ----------------------------------------------------
# 'Appellate Case No. 2022-000046' — the last row at the rail in the
# identity band, on all 28 records. THE DOCKET.
_DOCKET = re.compile(r"^Appellate Case Nos?\.\s*(.+)$", re.I)
# 'Opinion No. 6147' / 'Unpublished Opinion No. 2026-UP-389' /
# 'Published Opinion No. 6142' / 'Opinion No. Op. 6138' (the court's own
# typo, hoffman). THE CITATION, and the landmark the ladder is read from.
_OPINION_NO = re.compile(
    r"^(Published|Unpublished)?\s*Opinion No\.\s*(\S.*?)\s*$", re.I)
# A South Carolina UNPUBLISHED opinion number: year, 'UP', serial.
_UP_NUMBER = re.compile(r"\b\d{4}-UP-\d+\b", re.I)
# 'Heard March 11, 2025 – Filed June 10, 2026' /
# 'Submitted July 1, 2026 – Filed July 29, 2026'. The separator is an EN
# DASH on all 28; a hyphen is accepted for safety.
_DATES = re.compile(
    r"^(Heard|Submitted|Reheard|Resubmitted|Argued)\s+(.+?)\s*[–—-]\s*"
    r"Filed\s+(.+?)\s*$", re.I)
# 'Withdrawn, Substituted, and Refiled February 11, 2026' — the third row of
# the opinion-number band on a substituted opinion (both scherbas, hoffman,
# whetstone).
_REFILED = re.compile(
    r"^(Withdrawn|Substituted|Refiled)\b.*?Refiled\s+(.+?)\s*$", re.I)
# 'Appeal From Edgefield County' / 'Appeal from Richland County' /
# 'Appeal From The Administrative Law Court'.
_APPEAL_FROM = re.compile(r"^Appeal\s+[Ff]rom\b")

# --- the precedential notice ---------------------------------------------
# The publication flag, printed as three centred bold rows ABOVE the
# masthead on the 7 unpublished records. Its first row is the landmark; the
# run closes on its own sentence.
_NOTICE = re.compile(r"^THIS OPINION HAS NO PRECEDENTIAL VALUE\b")

# --- the three measured positions ----------------------------------------
# THE CAPTION RAIL: x0 = 144.0 exactly on all 28 records, for every party
# row, every party-row WRAP, the docket row and every counsel row. 72pt
# inside the body rail.
_RAIL = 144.0
_RAIL_TOL = 3.0
# THE BODY RAIL ends the reader. Measured x0 = 72.0 on all 28 records.
#
# IT IS MEASURED HERE, NOT TAKEN FROM `geom`, for sc's reason: core derives
# `body_x0` from the commonest left edge of the full-measure lines, and on a
# record whose headmatter is long and whose opinion is short the caption and
# counsel rows at the CAPTION rail can outvote the prose. `geom` is used
# only where it agrees the body rail is well inside the caption rail.
_BODY_RAIL = 72.0
_BODY_TOL = 10.0
# A centred row's mid-point against the page's. The masthead measures
# 305.95-306.0, the notice 305.85-306.05, the dates and dispositions 306.0.
_AXIS_TOL = 12.0

# --- the fence ------------------------------------------------------------
# See the module docstring: on the axis AND narrow. The measure is 97.2pt on
# all 140 fences; the gate is sc's, unchanged, and what it must exclude sits
# far outside it either way.
_FENCE_AXIS_TOL = 6.0
_FENCE_W_MIN = 85.0
_FENCE_W_MAX = 140.0

# The headmatter never runs past page 2 in this corpus (barringer sets a
# 20-row consolidated caption and reaches its counsel on page 2; altamont
# sets a 19-row caption and does the same). Six is the bound, as for sc; a
# record whose byline is not found inside it is not read at all.
_MAX_PAGES = 6

# PARTY STATUS IS A CLOSED VOCABULARY, party NAMES are not. Used only to
# trim the status label off a party group when building `case_name` — never
# to decide what a row IS.
_STATUS = re.compile(
    r",\s*(?:(?:Third-Party|Fourth-Party)\s+)?"
    r"(?:Petitioners?|Respondents?|Appellants?|Appellees?|Plaintiffs?"
    r"|Defendants?|Intervenors?|Movants?|Claimants?"
    r"|Petitioner-Respondents?|Respondent-Petitioners?"
    r"|Respondent-Intervenors?|Intervenors?-Respondents?"
    r"|Appellant-Respondents?|Respondent-Appellants?)"
    r"\s*[,.;]", re.I)
# The caption's pivot row, printed alone at the rail ('v.'), and the row
# that joins consolidated captions ('AND' — barringer).
_PIVOT = re.compile(r"^v\.$", re.I)
_JOINER = re.compile(r"^and$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_caps(text: str) -> bool:
    """The row is set in capitals — at least one cased letter and no
    lower-case one. This is the origin/posture discriminator and the
    disposition test, so digits, apostrophes and punctuation must not spoil
    it ('AFFIRMED IN PART, REVERSED IN PART')."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and not any(c.islower() for c in letters)


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is `docket_number`
# plus `other_dockets`, and a heard/argued date belongs in `submitted`.
# Written under invented names they attach by setattr and never serialize.


@decider("headmatter.read", court="scctapp")
def read_headmatter_scctapp(model, geom, **_):
    """Read the Court of Appeals' fenced ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = _BODY_RAIL
    if geom and geom.body_x0 and geom.body_x0 < _RAIL - 24.0:
        body_x0 = geom.body_x0
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width

    blocks, pre = _blocks(model, finder, body_x0, width)
    if not blocks or blocks[0]["page"] != 1:
        return NOTHING

    ctx = _Ctx()
    # THE PROLOGUE IS THE NOTICE OR THE CLAIM IS OFF. Rows above the first
    # masthead are read before the ladder, because they are above the first
    # fence and outside every band.
    if not _notice(ctx, pre, width):
        return NOTHING

    caption: list[str] = []
    counsel: list[str] = []
    for blk in blocks:
        if not _read_block(ctx, blk, caption, counsel, width):
            return NOTHING
        ctx.close_block()

    # POPULATE BEFORE GATING. wyo shipped its `docket_number` gate one line
    # ABOVE the call that fills it and refused 50 correctly-read records;
    # the gate belongs here, after every band has been walked.
    if not ctx.crit.get("docket_number") or not caption:
        return NOTHING
    ctx.crit["caption"] = caption
    parties = _parties(caption)
    if parties:
        ctx.crit["parties"] = parties
        ctx.crit["case_name"] = _case_name(caption)
    if counsel:
        # ITEM 41, closed in the file that owns the reading: counsel stays
        # in the headmatter where the page prints it, and its text is
        # copied to the criterion here because core cannot reach it.
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    ctx.crit["headmatter_style"] = "scctapp drawn fenced ladder"
    return ctx.result()


def _blocks(model, finder, body_x0: float, width: float):
    """The record's cover block, and the rows above its masthead.

    A block OPENS on the masthead and CLOSES on the first row at the body
    rail — the byline that begins the writing. The walk is written per-block
    the way sc's is, because the shape allows a second cover (sc's erb
    prints two papers); no record in this corpus does, and a second block
    would be read on its own terms rather than folded into the first.
    """
    blocks: list[dict] = []
    pre: list[list] = []
    cur: dict | None = None
    band = 0
    for pm in model.pages[:_MAX_PAGES]:
        pending = sorted(_fence_tops(pm, width))
        for group in _rows(pm, finder):
            top = min(l.top for l in group)
            while pending and pending[0] < top:
                pending.pop(0)
                band += 1
                if cur is not None:
                    cur["fences"].append((band, pm.number))
            if cur is None:
                text = _norm(_text(group))
                if not _MAST_STATE.match(text):
                    if not blocks and pm.number == 1:
                        pre.append(group)
                    continue
                band = 0
                cur = {"rows": [], "fences": [], "page": pm.number,
                       "closed": False}
                blocks.append(cur)
            if min(l.x0 for l in group) <= body_x0 + _BODY_TOL:
                cur["closed"] = True     # the writing begins
                cur = None
                continue
            cur["rows"].append((band, group))
        if cur is not None:
            for _ in pending:            # flush this page's fences
                band += 1
                cur["fences"].append((band, pm.number))
    return [b for b in blocks if b["closed"] and b["rows"]], pre


def _notice(ctx, pre: list[list], width: float) -> bool:
    """The precedential notice, or nothing above the masthead at all.

    A RUN that closes on its own sentence (the lesson's rule). Four cues,
    and CAPITALS IS NOT ONE OF THEM: its first row is the landmark, every
    row is BOLD and centred on the page axis, and the run ends at the first
    row that ends in a period. The caps test that reads the rest of this
    ladder would reject the notice's own last row — the court cites its rule
    by subdivision, 'EXCEPT AS PROVIDED BY RULE 268(d)(2), SCACR.', and that
    lower-case 'd' is a citation, not a change of voice. Weakening
    `_is_caps` instead would weaken the origin/posture and disposition
    discriminators, so the run carries its own membership test.

    21 of the 28 records print nothing above the masthead; the 7 that do
    print exactly these three rows. Anything else up there is unread, and
    unread above a claim is a hole, so it aborts.
    """
    if not pre:
        return True
    texts = [_norm(_text(g)) for g in pre]
    if not _NOTICE.match(texts[0]):
        return False
    for i, (group, text) in enumerate(zip(pre, texts)):
        if not (_centred(group, width)
                and all(bool(l.all_bold) for l in group)):
            return False
        ctx.emit(group, "publication", width)
        if text.endswith("."):
            if i != len(pre) - 1:
                return False        # the notice closed; something follows
            break
    else:
        return False                # the run never closed its sentence
    ctx.crit["publication_status"] = "unpublished"
    return True


def _read_block(ctx, blk, caption, counsel, width) -> bool:  # noqa: C901
    """Classify one cover block band by band, or fail the whole claim."""
    rows = blk["rows"]
    fences = blk["fences"]

    # THE DISPATCH: the two-row masthead at the head of the identity band.
    # Never an ordinal — it is the landmark every other role is anchored to.
    first = _norm(_text(rows[0][1]))
    if not _MAST_STATE.match(first):
        return False
    if not (len(rows) > 1 and rows[1][0] == 0
            and _MAST_COURT.match(_norm(_text(rows[1][1])))):
        return False
    mast = [0, 1]

    by_band: dict[int, list[int]] = {}
    for i, (b, _g) in enumerate(rows):
        by_band.setdefault(b, []).append(i)

    # THE SECOND LANDMARK: the band holding the opinion number. Everything
    # before it is identity, posture and origin; everything after it is
    # disposition and counsel. A block with no such band is not an opinion
    # cover, and this court prints no other kind of cover in this corpus, so
    # the claim is withdrawn rather than guessed at.
    num_band = None
    for b in sorted(by_band):
        if b == 0:
            continue
        if any(_OPINION_NO.match(_norm(_text(rows[i][1])))
               for i in by_band[b]):
            num_band = b
            break
    if num_band is None:
        return False

    for b in sorted(by_band):
        idxs = by_band[b]
        texts = [_norm(_text(rows[i][1])) for i in idxs]
        if b == 0:
            if not _identity(ctx, rows, idxs, texts, mast, caption, width):
                return False
        elif b < num_band:
            # POSTURE (all capitals) or ORIGIN (names a judge, so at least
            # one mixed-case row). See the module docstring.
            if all(_is_caps(t) for t in texts):
                for i in idxs:
                    ctx.emit(rows[i][1], "case-info", width)
                _history(ctx, " ".join(texts))
            elif not _origin(ctx, rows, idxs, texts, width):
                return False
        elif b == num_band:
            if not _paper(ctx, rows, idxs, texts, width):
                return False
        else:
            # After the opinion number the ladder holds exactly two kinds of
            # band, and each is told by POSITION: the disposition is centred
            # on the axis, counsel stands at the caption rail.
            if all(_at_rail(rows[i][1]) for i in idxs):
                for i, t in zip(idxs, texts):
                    ctx.emit(rows[i][1], "counsel", width, centre=False)
                    counsel.append(t)
            elif all(_centred(rows[i][1], width) and _is_caps(t)
                     for i, t in zip(idxs, texts)):
                for i in idxs:
                    ctx.emit(rows[i][1], "disposition", width)
                ctx.crit.setdefault("disposition", " ".join(texts))
            else:
                return False
        # A READER THAT CLAIMS THE BLOCK RE-EMITS ITS FENCES — core draws
        # them only on rows a reader left behind. The fence that OPENS the
        # next band is the one that closes this one, and the last band's
        # closer is the rule between counsel and the byline.
        for _b, page in fences:
            if _b == b + 1:
                ctx.rule(page)
    return True


# --------------------------------------------------------------------------
# the bands
# --------------------------------------------------------------------------

def _identity(ctx, rows, idxs, texts, mast, caption,
              width) -> bool:  # noqa: C901
    """The masthead, the parties and the appellate case number — the band
    above the first fence. The masthead rows are the ones the dispatch
    found; every other row in the band stands at the caption rail, and the
    docket is the one that names itself."""
    said = dict(zip(idxs, texts))
    for i, text in zip(idxs, texts):
        group = rows[i][1]
        if i in mast:
            ctx.emit(group, "court", width)
            continue
        if not _at_rail(group):
            return False
        docket = _DOCKET.match(text)
        if docket:
            # A CONSOLIDATED CAPTION CAN PRINT ONE NUMBER PER CASE. None in
            # this corpus does — barringer consolidates two estate actions
            # under the single number 2025-000076 — but the split is kept
            # because the form is the publisher's and sc exercises it.
            parts = [p.strip() for p in
                     re.split(r",|\band\b", docket.group(1)) if p.strip()]
            for part in parts:
                if not ctx.crit.get("docket_number"):
                    ctx.crit["docket_number"] = part
                elif part != ctx.crit["docket_number"] \
                        and part not in ctx.crit.setdefault(
                            "other_dockets", []):
                    ctx.crit["other_dockets"].append(part)
            ctx.emit(group, "docket", width, centre=False)
            continue
        # A caption row and its wraps all stand at 144.0, so the printed
        # form is kept row by row and the parsing is done separately.
        #
        # THE DEDUPE IS ACROSS COVERS, NOT WITHIN ONE. sc suppresses a
        # repeated caption row because a record that prints two covers
        # prints the same caption twice and would otherwise report four
        # parties in a two-party appeal. Applied WITHIN a cover the same
        # test destroys a consolidated caption: barringer joins two estate
        # actions with 'AND' and prints 'In the Matter of the Estate of Paul
        # Brandon Barringer, II' / 'Hampton Barringer Luzak, Appellant,' /
        # 'v.' once per action, and suppressing the second set left the
        # joined-on case with a respondent and no petitioner. So the
        # bookkeeping is per block, and `criteria.caption` stays verbatim
        # for the cover it belongs to.
        if text not in ctx.seen_caption:
            caption.append(text)
        ctx.block_caption.append(text)
        ctx.emit(group, "caption", width, centre=False)
    ctx.crit.setdefault("court", " ".join(said[i] for i in mast))
    return True


def _history(ctx, text: str) -> None:
    """The paper's procedural history ACCUMULATES: a substituted opinion
    prints both how the case arrived and what happened to the earlier paper
    ('Withdrawn, Substituted, and Refiled February 11, 2026'). Under
    `setdefault` the first silently discards the second."""
    have = ctx.crit.get("history")
    if not have:
        ctx.crit["history"] = text
    elif text not in have:
        ctx.crit["history"] = f"{have}; {text}"


def _origin(ctx, rows, idxs, texts, width) -> bool:
    """The court below and its judge. The tribunal is the first row plus any
    capitalised continuation of it; every remaining row names a judge
    ('Walton J. McLeod, IV, Circuit Court Judge', 'Jan B. Bromell Holmes,
    Family Court Judge', 'Ralph King Anderson, III, Administrative Law
    Judge')."""
    if not _APPEAL_FROM.match(texts[0]) and not _is_caps(texts[0]):
        return False
    cut = 1
    while cut < len(texts) and _is_caps(texts[cut]):
        cut += 1
    for i in idxs:
        ctx.emit(rows[i][1], "lower-court", width)
    ctx.crit.setdefault("lower_court", " ".join(texts[:cut]))
    if texts[cut:]:
        ctx.crit.setdefault("lower_court_judge", "; ".join(texts[cut:]))
    return True


def _paper(ctx, rows, idxs, texts, width) -> bool:
    """The band the ladder is read from: the court's own opinion NUMBER —
    which is the citation, not the docket — and the dates it prints about
    the paper."""
    for i, text in zip(idxs, texts):
        group = rows[i][1]
        number = _OPINION_NO.match(text)
        if number:
            ctx.crit.setdefault("citation", text)
            _publication(ctx, number.group(1), number.group(2))
            ctx.emit(group, "citation", width)
            continue
        dated = _DATES.match(text)
        if dated:
            ctx.crit.setdefault("submitted", _norm(dated.group(2)))
            ctx.crit.setdefault("decision_date", _norm(dated.group(3)))
            ctx.emit(group, "date", width)
            continue
        refiled = _REFILED.match(text)
        if refiled:
            _history(ctx, text)
            ctx.emit(group, "date", width)
            continue
        return False
    return True


def _publication(ctx, word: str | None, number: str) -> None:
    """The publication flag, from the opinion-number row.

    The notice above the masthead already said it on the 7 unpublished
    records; this is the second, independent signal, and the two agree on
    all 28. `setdefault` semantics: the notice wins where both are printed,
    because the notice is the court's own sentence about the paper.
    """
    if _UP_NUMBER.search(number) or (word and word.lower() == "unpublished"):
        ctx.crit.setdefault("publication_status", "unpublished")
    else:
        ctx.crit.setdefault("publication_status", "published")


# --------------------------------------------------------------------------
# the caption, parsed beside its printed form
# --------------------------------------------------------------------------

def _groups(caption: list[str]) -> list[list[str]]:
    """The caption's party groups: the rows between the pivot rows ('v.')
    and the consolidation joiners ('AND'). A bare 'v.' row is the ordinary
    multi-row caption and must not be folded into its neighbours."""
    out: list[list[str]] = [[]]
    for row in caption:
        if _PIVOT.match(row) or _JOINER.match(row):
            out.append([])
            continue
        out[-1].append(row)
    return [g for g in out if g]


def _join(rows: list[str]) -> str:
    """A party group's rows as one string. A row that ends in a HYPHEN is a
    word broken at the caption's measure and closes up, which matters
    because the status label the trim looks for is the broken word."""
    out = ""
    for row in rows:
        if out.endswith("-"):
            out += row
        elif out:
            out += " " + row
        else:
            out = row
    return out


def _trim(text: str) -> str:
    """A party group down to its NAME: the printed run up to the first party
    status label. Joining the rows wholesale yields 'Glenfield Capital, LLC,
    d/b/a Glen 1441, LLC; Colliers International South Carolina, Inc.; tk
    Elevator Corporation; and Sizemore, Inc., Respondents.'"""
    hit = _STATUS.search(text)
    if hit:
        # THE CUT IS ALREADY EXACT — do not then strip punctuation off it.
        # sc's `_trim` rstrips ' ,.;' unconditionally, and on a corporate
        # party that costs the abbreviation its period: 'AKPA Chemical US,
        # Inc., Appellant,' cut at the label gives 'AKPA Chemical US, Inc.'
        # and the strip turned it into 'AKPA Chemical US, Inc'. Same for
        # 'Citibank N.A.'. Where no label was found the row is a whole
        # printed sentence and its closing stop does come off.
        return text[:hit.start()]
    return text.rstrip(" ,.;")


def _parties(caption: list[str]) -> list[str]:
    return [_trim(_join(g)) for g in _groups(caption)][:8]


def _case_name(caption: list[str]) -> str:
    """'X v. Y', built from the party names either side of the FIRST pivot.
    With no pivot the caption is a single style ('In the Matter of …')."""
    left: list[str] = []
    right: list[str] | None = None
    for row in caption:
        if _PIVOT.match(row):
            if right is None:
                right = []
                continue
            break
        if _JOINER.match(row):
            break
        (left if right is None else right).append(row)
    head = _trim(_join(left))
    if not right:
        return head
    return f"{head} v. {_trim(_join(right))}"


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------

def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


def _at_rail(group: list) -> bool:
    return abs(min(l.x0 for l in group) - _RAIL) <= _RAIL_TOL


def _centred(group: list, width: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


def _fence_tops(pm, width: float) -> list[float]:
    """The band fences this page draws: on the page axis and narrow. See the
    module docstring for what the gate excludes and why the axis is tested
    before the measure."""
    out = []
    for rule in pm.h_rules:
        span = rule.x1 - rule.x0
        if not _FENCE_W_MIN <= span <= _FENCE_W_MAX:
            continue
        if abs((rule.x0 + rule.x1) / 2 - width / 2) > _FENCE_AXIS_TOL:
            continue
        out.append(rule.top)
    return out


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
        # Caption rows already seen on an EARLIER cover of the same record
        # (see `_identity`); rows repeated inside one cover are kept.
        self.seen_caption: set[str] = set()
        self.block_caption: list[str] = []

    def close_block(self) -> None:
        self.seen_caption.update(self.block_caption)
        self.block_caption = []

    def emit(self, group: list, role: str, width: float,
             centre: bool | None = None) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        if centre is None:
            centre = _centred(group, width)
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

    def rule(self, page: int) -> None:
        # A DRAWN rule, not a typed one: it carries no line ids, so it is
        # re-emitted for the render and consumes nothing.
        self.items.append(m.Rule(prov=m.Prov(page), typed=False,
                                 span="center"))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
