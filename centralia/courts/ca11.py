"""United States Court of Appeals for the Eleventh Circuit ('ca11').

Everything unique to ca11 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'fenced bands'. ca11 types its headmatter's section marks:
a run of underscores 140.1pt wide, set at x0=235.9 on a 612pt page — dead
on the page axis — in the body face at 14pt. It types 460 of them across
the corpus and every one of them is that rule; it types nothing else that
looks like one. The fences come in PAIRS, and a pair is a BAND:

    FOR PUBLICATION                          the publication flag (core drops
                                             it; the fact goes to criteria)
    In the                                   18pt ┐
    United States Court of Appeals           24pt ├ the banner, above the
    For the Eleventh Circuit                 18pt ┘ first fence
    ____________________                     ← fence: the band OPENS
    No. 24-13309                             the docket band…
    Non-Argument Calendar                    …and the calendar it was set on
    ____________________                     ← fence: the band CLOSES
    ABIGAIL JEAN MARBUT,                     the caption stands BETWEEN bands
                       Plaintiff-Appellant   …its statuses flush RIGHT
    versus
    MATTHEW PHILLIPS,
      in his individual capacity,            …its descriptors indented, 12pt
                    Defendants-Appellees,
    ____________________                     ← fence
    Appeal from the United States District   the origin band
    Court for the Northern District of Georgia
    D.C. Docket No. 1:22-cv-00776-VMC
    ____________________                     ← fence
    Before WILLIAM PRYOR, Chief Judge, …     the roster, BELOW the last fence
    WILLIAM PRYOR, Chief Judge:              the first byline — the reader
                                             stops here and never goes deeper

The fence is the parser, and the parity of the fences is the zone system:

  * ABOVE the first fence stands the masthead — the publication flag and
    the three banner rows, and nothing else on any of the 101 typeset
    records. A masthead row this contract cannot name means the cover is
    not the one described here, and the whole reading is withdrawn.
  * INSIDE a pair stands a BAND, and the BAND is the unit of meaning, not
    the row: its first row says whether it is the DOCKET band ('No. …') or
    the ORIGIN band ('Appeal from …', 'Petition for Review of …'), and
    every row under that first one belongs to whatever the band is. That
    is what keeps 'for the Northern District of Georgia' — which names no
    court by itself — from having to be recognized on its own.
  * BETWEEN a band's close and the next band's open stands the CAPTION,
    and it is read BY COLUMN: a row at the body rail (x0=126.0) is a party
    name, a row whose right edge reaches the measure (x1=486) is that
    party's STATUS, and a row indented off the rail is its descriptor.
    Nothing in the caption is read by what it says.
  * BELOW the last fence stands the roster, which wraps until it ends on a
    full stop, and under the roster the first byline. The reader stops
    there.

A consolidated appeal simply repeats the cycle — docket band, caption,
origin band, docket band, caption, origin band … — up to thirteen times
(union_pacific runs its headmatter to page 7). Nothing about the walk
changes; the fences keep counting.

ca11's own FURNITURE inside the region is equally invariant: pages 2+ set a
three-piece running head — folio, opinion name, docket — on one row at
top=102.6, on 466 of 466 pages measured, and the page's next row never
starts above 129. Core learns that head by repetition, which fails at both
ends: on a two-page slip it prints once and is not learned (its pieces rode
into gilmore's caption), and on a long consolidated record the 12pt origin
band repeats in the same top band and IS learned (ismael_perez and
union_pacific lost their 'Appeal from …' rows to it). Inside the region
this reader uses ca11's own band instead, and records what it cuts.

A record that types no fence is not this contract and gets NOTHING: core's
shared walk places those rows unidentified, which is a smaller error than a
confident misreading.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import FOOTNOTE_LABEL_CHARS, line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop ca11 used to sit in, so nothing about its bylines
# changes by being moved here.
CA11 = register(CourtProfile(
    "ca11", "United States Court of Appeals for the Eleventh Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_FENCED_BANDS = "fenced bands"

# ---- ca11's declared facts (measured over the corpus, not tuned) ---------
# THE FENCE. 460 typed rules over 101 typeset records, every one of them
# 140.1pt wide at x0=235.9 on a 612pt page and set in the 14pt body face.
# The only other underscore run the court types is the caption's own 'In
# re:' divider, 245.2pt wide and starting AT the body rail — a different
# rule with a different job, and the width tells them apart.
_UNDERSCORES = re.compile(r"^_{4,}$")
_FENCE_WIDTH = (134.0, 146.0)
_FENCE_OFF_AXIS = 4.0
# THE RUNNING HEAD BAND. Pages 2+ set '2 | Opinion of the Court | 24-13309'
# as one row at top=102.6 — 466 of 466 pages measured, always three pieces —
# and the first row of text under it never stands above 129.6.
_HEAD_BAND = 115.0
# THE TYPE BLOCK. Nothing the court itself sets prints above 95pt; the
# e-filing overlay ('USCA11 Case: … Page: 1 of 21') sits at 27.5 and is
# core's to drop, not this reader's to claim.
_TYPE_TOP = 95.0
# How far the block may run. union_pacific consolidates thirteen petitions
# and closes its last band on page 7; no fence anywhere in the corpus
# prints below that.
_MAX_PAGES = 10
# THE CAPTION'S COLUMNS, measured inside the caption band: the party rail is
# the document's own body rail (x0=126.0 on every record), a STATUS label is
# flush to the measure (x1=486.0-486.2 against a right_x1 of 486.0-486.3),
# and a descriptor is indented 9-11pt off the rail at 12pt.
_RAIL_TOL = 1.5
_FLUSH_TOL = 4.0
_STATUS_MIN_INDENT = 40.0

# THE BANNER, in the three rows ca11 sets it in. A closed vocabulary of the
# court naming ITSELF — never a test on anything a record says about a case.
_BANNER_ROWS = ("in the", "united states court of appeals",
                "for the eleventh circuit")
# THE PUBLICATION FLAG. Read on its stem so both forms answer alike, the
# NOT- form first because the other is its own suffix. The ROW is left in
# the stream: core drops a standalone publication banner and records the
# fact, and doing it twice would drop it twice.
_UNPUBLISHED = "not for publication"
_PUBLISHED = "for publication"
# THE DOCKET BAND. A consolidated appeal prints every docket in one cell
# ('Nos. 24-11398; 25-11185'), and the court sets the calendar it was heard
# on under it.
_DOCKET_TAIL = r"(?:\s*[;,/]\s*(?:\d{2}-)?\d{2,5})*"
_DOCKET = re.compile(r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$",
                     re.I)
_CALENDAR = re.compile(r"^(?:Non-Argument|Argument)\s+Calendar\.?$", re.I)
# THE ORIGIN BAND opens on the court's own statement of what it is
# reviewing.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "petition for review", "petitions for review",
    "on petition for review", "on petitions for review",
    "petition for writ", "petitions for writ",
    "on remand from", "on review of", "review of",
    "application for", "on application for",
)
# THE LOWER TRIBUNAL'S OWN NUMBER, in the forms the origin band prints it:
# 'D.C. Docket No. 1:22-cv-00776-VMC', 'Bkcy. No. 2:21-bk00123FM',
# 'Agency No. A206-841-611'.
_LOWER_DOCKET = re.compile(
    r"^(?:D\.?C\.?\s+Docket|Bkcy\.?|Bankruptcy|Agency|Docket|Nos?)\b"
    r".*\bNos?\.|^Nos?\.", re.I)
# THE ROSTER. ca11 opens it with one word and closes it on a full stop.
_ROSTER_OPEN = "before"
_ROSTER_END = (".", ":")
# BENCH WORDS — a finite role vocabulary, so a roster yields judges and not
# a judge called 'Circuit'.
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
_SUFFIXES = ("JR", "SR", "II", "III", "IV")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") in _BANNER_ROWS


def _is_flag(text: str) -> str | None:
    low = _norm(text).lower().rstrip(".")
    if low.startswith(_UNPUBLISHED):
        return "unpublished"
    if low.startswith(_PUBLISHED):
        return "published"
    return None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_caps(text: str) -> bool:
    """Is the row set in the caps ca11 gives every party NAME?

    The court sets its parties in full capitals and their descriptors in
    sentence case ('an agency of the State of Georgia,'). On most of the
    corpus the two are already different COLUMNS — the descriptor is
    indented and a step smaller — but one template (gilmore) sets both at
    the rail in the body face, and there the case of the type is the only
    thing that still separates a party from the clause qualifying it. The
    case of a row is a fact of the typesetting, not a reading of what it
    says."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.75


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test."""
    body = _norm(text)
    at = body.lower().find("sitting by")
    if at > 0:
        body = body[:at].rstrip(" ,")
    if body.lower().startswith(_ROSTER_OPEN):
        body = body[len(_ROSTER_OPEN):]
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*:† ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*:† ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not another
            # judge.
            if names and name.rstrip(".").upper() in _SUFFIXES:
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _terminated(text: str) -> bool:
    """Has the court's statement ENDED on this row?

    ca11 closes its roster on a full stop — and hangs the visiting judge's
    footnote mark AFTER it ('District Judge.\u2217'), so the mark is stripped
    before the stop is read. Left in, the roster ran on and swallowed the
    byline under it, and the document lost its author."""
    flat = _norm(text).rstrip()
    while flat and flat[-1] in FOOTNOTE_LABEL_CHARS:
        flat = flat[:-1].rstrip()
    return flat.endswith(_ROSTER_END)


def _dehyphenate(rows: list) -> str:
    """Join a wrapped statement the way the page reads it: ca11 breaks
    'Cir-' / 'cuit Judges.' across the roster's two rows, and joining those
    on a space invents a word."""
    out = ""
    for row in rows:
        piece = _norm(row)
        if not out:
            out = piece
        elif out.endswith("-"):
            out = out[:-1] + piece
        else:
            out = out + " " + piece
    return out


# --------------------------------------------------------------------------
# the fence — ca11's section mark, and the dispatch
# --------------------------------------------------------------------------

def _is_fence(line, page_width: float) -> bool:
    """Is ``line`` one of the court's typed section rules?"""
    if not _UNDERSCORES.match(_norm(line.plain)):
        return False
    width = line.x1 - line.x0
    if not (_FENCE_WIDTH[0] <= width <= _FENCE_WIDTH[1]):
        return False
    return abs((line.x0 + line.x1) / 2 - page_width / 2) <= _FENCE_OFF_AXIS


def _is_inner_rule(line, body_x0: float) -> bool:
    """The caption's OWN divider — the rule the court types between an 'In
    re:' cell and the adversary caption under it. It starts at the body rail
    and runs far wider than a fence, so the two never have to be told apart
    by where they fall in the walk."""
    return (_UNDERSCORES.match(_norm(line.plain)) is not None
            and abs(line.x0 - body_x0) <= _RAIL_TOL
            and (line.x1 - line.x0) > _FENCE_WIDTH[1])


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ca11")
def read_headmatter_ca11(model, geom, **_):
    """Read ca11's fenced-band headmatter, or NOTHING."""
    if not model.pages or geom is None:
        return NOTHING                    # a scan measures no geometry
    body_x0 = geom.body_x0 or 126.0
    right_x1 = geom.right_x1 or 486.0
    body_size = geom.body_size or 14.0
    pages = {pm.number: pm for pm in model.pages}
    parser = BylineParser(CA11.byline)

    # ---- the region, and the furniture it carries ------------------------
    finder = FurnitureFinder(model, body_x0, body_size)
    rows: list = []
    heads: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if line.top < _TYPE_TOP:
                continue                  # the e-filing overlay: core's
            if pm.number > 1 and line.top <= _HEAD_BAND:
                # THE RUNNING HEAD. Core measures and records the pieces it
                # recognizes; those are already gone from the stream and
                # claiming them would record them twice. What is left is
                # what its repetition test could not reach — a two-page
                # slip prints this head exactly once — and that is this
                # reader's to cut.
                if finder.kind(pm, line) is None:
                    heads.append(line)
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    heads.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    fences = [i for i, l in enumerate(rows)
              if _is_fence(l, pages[l.page].width)]
    if len(fences) < 2 or rows[fences[0]].page != 1 or len(fences) % 2:
        return NOTHING                    # no paired fence: not ca11's cover

    # ---- where the claim ends: the roster below the last fence -----------
    tail = fences[-1] + 1
    end = fences[-1]
    if tail < len(rows) and _norm(rows[tail].plain).lower().startswith(
            _ROSTER_OPEN):
        end = tail
        # THE ROSTER WRAPS until it ends on a full stop — but an
        # unterminated row is not licence to swallow the writing under it.
        # A BYLINE ENDS THE READER wherever it stands.
        while (end + 1 < len(rows)
               and not _terminated(rows[end].plain)
               and parser.parse(_norm(rows[end + 1].plain)) is None):
            end += 1
    # …and nothing between the first fence and the last one may be a byline
    # either: on this paper the court signs BELOW its roster, so one found
    # inside the bands means the walk mis-read the page and the record is
    # left to core.
    for i in range(fences[0], fences[-1] + 1):
        if parser.parse(_norm(rows[i].plain)) is not None:
            return NOTHING

    crit: dict = {"headmatter_style": STYLE_FENCED_BANDS}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    banner_rows: list[tuple[float, str]] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    lower_dockets: list[str] = []
    panel_rows: list[str] = []
    left_names: list[str] = []
    right_names: list[str] = []
    pivot_seen = False

    def emit(line, role: str, align: str | None = None):
        pm = pages[line.page]
        a = align or line_alignment(line, pm.width, geom,
                                    banner_center_min_size=body_size + 2.0)
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(a), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    def rule(line):
        items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                            typed=True, span="full"))
        consumed.add(line.id)

    # ---- the masthead: everything the page prints above the first fence --
    for line in rows[:fences[0]]:
        text = _norm(line.plain)
        flag = _is_flag(text)
        if flag:
            # THE FLAG IS A NOTICE, not a headmatter row: core drops a
            # standalone publication banner and keeps the fact in criteria,
            # and this reader does the same in its own claim. Leaving the
            # row behind instead is not neutral — it would be the only
            # unclaimed row on page 1, and assembly reads a lone heading
            # above the body as the opening of a writing, which pulled the
            # whole block back out of the headmatter.
            crit.setdefault("publication_status", flag)
            dropped.append(m.Dropped(
                text=text, prov=m.Prov(line.page, (line.id,)),
                kind="status"))
            consumed.add(line.id)
            continue
        if _is_banner(text):
            banner_rows.append((line.size or 0.0, text))
            emit(line, "court")
            continue
        return NOTHING                    # a cover this contract cannot name
    if len(banner_rows) < 2:
        return NOTHING                    # ca11 always names itself

    # ---- the bands, the captions, and the roster, in the page's order ----
    inside = False
    band_kind = ""
    region = -1                           # which caption stands here
    fence_at = set(fences)
    for i in range(fences[0], end + 1):
        line = rows[i]
        text = _norm(line.plain)
        if i in fence_at:
            rule(line)
            inside = not inside
            band_kind = ""
            if not inside:
                # A CONSOLIDATED APPEAL repeats the whole cycle — docket
                # band, caption, origin band — once per case, and the case
                # this record is filed under is the FIRST. Later captions
                # are printed facts and stay in the block; read into the
                # parties they turned 'UNITED STATES v. ANGELO MARTINEZ'
                # into a list of every co-defendant's caption.
                region += 1
            continue
        if i > fences[-1]:
            panel_rows.append(text)
            emit(line, "panel")
            continue
        if inside:
            # THE BAND IS THE UNIT OF MEANING: its first row says what the
            # band is, and every row under it belongs to that band.
            if not band_kind:
                if _DOCKET.match(text):
                    band_kind = "docket"
                elif _origin_opener(text) or _LOWER_DOCKET.match(text):
                    band_kind = "origin"
                else:
                    return NOTHING        # a band this contract cannot name
            if band_kind == "docket":
                if _DOCKET.match(text):
                    if crit.get("docket_number"):
                        crit.setdefault("other_dockets", []).append(
                            text.rstrip("."))
                    else:
                        crit["docket_number"] = text.rstrip(".")
                elif not _CALENDAR.match(text):
                    return NOTHING
                emit(line, "docket")
            else:
                if _LOWER_DOCKET.match(text):
                    lower_dockets.append(text)
                else:
                    origin_rows.append(text)
                emit(line, "lower-court")
            continue
        # ---- the caption, read by column ---------------------------------
        if _is_inner_rule(line, body_x0):
            # THE CAPTION'S OWN DIVIDER separates the bankruptcy cell ('In
            # re: GREGORY BRIAN MYERS, Debtor.') from the adversary caption
            # under it. The parties are the ones the court sets BELOW it.
            rule(line)
            if region == 0:
                left_names.clear()
                right_names.clear()
                pivot_seen = False
            continue
        caption_rows.append(text)
        if line.x1 >= right_x1 - _FLUSH_TOL \
                and line.x0 > body_x0 + _STATUS_MIN_INDENT:
            emit(line, "caption", align="R")     # the party's STATUS
        elif abs(line.x0 - body_x0) <= _RAIL_TOL:
            emit(line, "caption", align="L")     # a party NAME, or the pivot
            if region != 0:
                continue
            if text.lower().rstrip(".,").strip() in ("versus", "v", "vs"):
                pivot_seen = True
            elif _is_caps(text):
                side = right_names if pivot_seen else left_names
                # THE SAME NAME TWICE IS ONE PARTY: catarino sues both as a
                # surviving child and for the estate, and the court sets the
                # name once for each capacity.
                if text not in side:
                    side.append(text)
        elif line.x0 > body_x0:
            emit(line, "caption", align="L")     # the party's descriptor
        else:
            return NOTHING                # a caption row outside every column

    # ---- what the block says ---------------------------------------------
    # THE BANNER'S OWN TYPE says which of its rows names the court: ca11
    # sets 'United States Court of Appeals' at 24pt and hangs 'In the' over
    # it at 18. The name is the largest row and everything under it.
    if banner_rows:
        top = max(size for size, _ in banner_rows)
        at = next(i for i, (size, _) in enumerate(banner_rows) if size == top)
        crit["court"] = _norm(" ".join(t for _, t in banner_rows[at:]))
    if caption_rows:
        crit["caption"] = caption_rows
        left = _norm(" ".join(left_names)).rstrip(", ")
        right = _norm(" ".join(right_names)).rstrip(", ")
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
        elif left or right:
            crit["parties"] = [left or right]
            crit["case_name"] = left or right
    if origin_rows:
        crit["lower_court"] = _dehyphenate(origin_rows)
    for printed in lower_dockets:
        crit.setdefault("other_dockets", []).append(printed.rstrip(","))
    if panel_rows:
        printed = _dehyphenate(panel_rows)
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith(_ROSTER_OPEN):
            roster = roster[len(_ROSTER_OPEN):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names

    # ---- the furniture the region carried --------------------------------
    # A READER THAT CLAIMS A REGION INHERITS ITS FURNITURE. Everything cut
    # is recorded, so consumed still means placed or recorded.
    last = (rows[end].page, rows[end].top)
    for line in heads:
        if (line.page, line.top) > last:
            continue
        text = _norm(line.plain)
        dropped.append(m.Dropped(
            text=text, prov=m.Prov(line.page, (line.id,)),
            kind="folio" if text.isdigit() else "running-head"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
