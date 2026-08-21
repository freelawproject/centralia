"""United States Court of Appeals for the Second Circuit ('ca2').

Everything unique to ca2 lives here. It imports core, never another court
file, and no other court file imports it.

ca2's headmatter is a LAYOUT CONTRACT, not a shape to be guessed at. The
court prints its sections in named styles, and each style says where the
sections are and what marks their edges. This file reads the style it knows
and returns NOTHING for the rest — recording nothing beats publishing a
misreading.

    'stated-term order' — the summary order, and the en banc denial that
        shares its skeleton:

            25-1830-cv Brooks v. Bright Horizons   running head
            UNITED STATES COURT OF APPEALS         centered banner
            FOR THE SECOND CIRCUIT
            SUMMARY ORDER                          centered title
            At a stated term ...                   recital, carrying the date
            Present:                               opens the roster
                WILLIAM J. NARDINI, ...            the panel
                Circuit Judges.
            ______________________                 OPENS the caption
            AMANDA BROOKS,                         caption rail, caps
                Plaintiff-Appellant,               indented + italic: status
                v.  25-1830-cv                     centered: pivot + docket
            BRIGHT HORIZONS ..., INC., ...         the other side, wrapped
                Defendants-Appellees.
            ______________________                 CLOSES it, opens counsel
            For Plaintiff-Appellant: NAME ...      one entry per party

The typed rules are the state transitions, and the caption is read BY COLUMN
— a party name sits on the caption's own left rail, a status label is
indented and italic, the pivot row is centered. Text shape cannot do this
work: ca2 sets party names in caps on one record and title case on the next,
and a shared row-shape walk files the defendants under counsel.

The reader claims HEADMATTER ONLY. Everything from its last landmark down —
the writing, its bylines, its footnotes, its paragraphs — is left to core.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import (furniture_key, gutter_column_ids,
                                 repeated_top_keys)
from ..resolve.headmatter import recital_date
from . import register

register(CourtProfile(
    "ca2", "United States Court of Appeals for the Second Circuit",
    byline=BylineGrammar(style="prose",
                         titles=("Circuit Judge", "Judge", "District Judge",
                                 "Justice", "J.")),
))

STYLE_STATED_TERM = "stated-term order"

_RULE = re.compile(r"^[_\-–—]{6,}$")
_DOCKET = re.compile(r"\b(\d{2}-\d{3,5}(?:-[a-z]{2})?)\b")
_PIVOT_ROW = re.compile(r"^v[s]?\.?(?:\s|$)", re.I)
_RUNNING = re.compile(r"^\d{2}-\d{3,5}(?:-[a-z]{2})?$")
_FOLIO = re.compile(r"^[\-–—\s\[\(]*\d{1,3}[\-–—\s\]\)]*$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _italic(line) -> bool:
    """Every inked glyph set in an italic face."""
    inked = [c for c in line.chars if (c.get("text") or "").strip()]
    if not inked:
        return False
    return all("italic" in (c.get("fontname") or "").lower()
               or "oblique" in (c.get("fontname") or "").lower()
               for c in inked)


def _rail(caption_rows) -> float:
    return min(l.x0 for l, _ in caption_rows)


def _opens_caps(text: str, least: int = 2) -> bool:
    """The row OPENS with a run of caps tokens — a party NAME.

    A party row need not be caps throughout: the name is, but the descriptor
    that follows it is not ('RONALD E. POWELL, as Trustee of The United Food
    & Commercial Workers Union…', 'ARTHUR PROVENCHER, individually and on
    behalf of all similarly situated individuals,'). Requiring the whole row
    skipped every appellant on those records."""
    run = 0
    for token in text.split():
        letters = [c for c in token if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            run += 1
            if run >= least:
                return True
            continue
        break
    return False


def _is_caps(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


STYLE_LADDER = "engraved ladder"          # …and its plain / numbered kin

_DATE_LABEL = re.compile(
    r"\b(argued|submitted|decided|filed|amended|reargued)\s*:?\s*"
    r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})", re.I)
_TERM_ROW = re.compile(r"\bterm\b", re.I)
_BARE_DOCKET = re.compile(
    r"^(?:docket\s+)?(?:nos?\.)?\s*\d{2}-\d{2,5}"
    r"(?:-[a-z]{2})?(?:\s*\([A-Z]{1,3}\))?"
    r"(?:[,;]\s*\d{2}-\d{2,5}(?:-[a-z]{2})?(?:\s*\([A-Z]{1,3}\))?)*\.?$",
    re.I)
_ORIGIN_OPENER = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "cross-appeals from", "petition for review", "petitions for review",
    "on petition for review", "on petitions for review", "on remand from",
    "review of", "appeal by",
)
_NOTICE_CUES = (
    "do not have precedential effect", "summary order",
    "federal rule of appellate procedure", "local rule 32.1",
    "electronic database", "must serve a copy", "not represented by counsel",
    "is permitted and is governed",
)
_BENCH = ("judge", "judges", "circuit", "district", "senior", "chief",
          "magistrate", "bankruptcy", "and")
_BYLINE_TAIL = re.compile(
    r"(circuit|district|chief|senior|magistrate)\s+judges?\s*:$"
    r"|^per curiam", re.I)


def _docket_label(text: str) -> str:
    bare = text.strip()
    if bare.lower().startswith("docket "):
        bare = bare[7:].strip()
    return bare if bare.lower().startswith(("no.", "nos.")) else f"No. {bare}"


def _roster_closed(text: str) -> bool:
    """The roster ends on the bench title that names the office, terminated
    by a period — which a footnote mark may follow ('District Judge.*')."""
    bare = text.rstrip().rstrip("*†‡∗0123456789").rstrip()
    return "judge" in text.lower() and bare.endswith(".")


_SUFFIX = ("jr", "sr", "ii", "iii", "iv")


def _roster_names(roster: str) -> list[str]:
    """The judges named in a roster.

    A plain split returns the roster's connectives and bench words as judges
    of their own — a judge called 'Circuit', another called 'and', and on an
    en banc bench a judge called 'Chief Judge'. A generational SUFFIX is not
    a judge either: 'RAYMOND J. LOHIER, JR.' is one name the comma happens
    to divide, so the suffix goes back onto the name above it."""
    out: list[str] = []
    for chunk in re.split(r",| and | AND |&", roster):
        bare = chunk.strip().rstrip(",.").strip().rstrip("*†‡∗").strip(" .,")
        if not bare:
            continue
        if bare.strip(".").lower() in _SUFFIX:
            if out:
                out[-1] = f"{out[-1]}, {bare}"
            continue
        words = [w.strip(" .,").lower() for w in bare.split()]
        if any(w in _BENCH for w in words):
            continue
        out.append(bare)
    return out


_STATUS_WORDS = ("plaintiff", "plaintiffs", "defendant", "defendants",
                 "petitioner", "petitioners", "respondent", "respondents",
                 "appellant", "appellants", "appellee", "appellees",
                 "intervenor", "intervenors", "movant", "movants",
                 "applicant", "applicants", "debtor", "debtors",
                 "consolidated", "cross")


def _is_status_label(text: str) -> bool:
    """A row that names a party's ROLE rather than a party.

    The ladder sets these italic, but NUMBERED PAPER sets them roman
    ('Plaintiff-Appellant,' under the party it belongs to), so italics alone
    left the status inside the party name. The vocabulary is closed — every
    word of the row is a role word — which no party name is."""
    bare = text.strip().rstrip("*†‡∗0123456789").strip(" ,.;")
    if not bare or len(bare) > 60:
        return False
    parts = [p for chunk in bare.split() for p in chunk.split("-")]
    return bool(parts) and all(
        p.strip(" ,.;").lower() in _STATUS_WORDS + ("and", "the")
        for p in parts)


# An appearance names a FIRM or an office; a caption row names a party. Both
# open in caps, so caps alone cannot tell a lead attorney from a lead
# plaintiff (havlish's consolidated caption pulled its own tail into the
# appearances).
_FIRM = re.compile(
    r"\b(LLP|L\.L\.P\.|LLC|L\.L\.C\.|PLLC|P\.C\.|P\.A\.|Esq\.?"
    r"|on the brief|School of Law|Attorney General|United States Attorney"
    r"|Assistant United States Attorney|Office of|Department of Justice)\b")

_DISPO_WORDS = ("affirmed", "reversed", "vacated", "remanded", "dismissed",
                "denied", "granted", "modified", "enforced", "withdrawn")


def _is_disposition(text: str) -> bool:
    """'AFFIRMED IN PART, VACATED IN PART, AND REMANDED.' — the court's own
    disposition, set in caps at the foot of its summary. A caps run is what
    identifies a lead attorney, so without this the disposition opens the
    appearances block and takes the end of the summary with it."""
    bare = " ".join(text.split()).rstrip(".").lower()
    if not bare or len(bare) > 120:
        return False
    words = [w.strip(",.;") for w in bare.replace("/", " ").split()]
    return bool(words) and any(w in _DISPO_WORDS for w in words) and all(
        w in _DISPO_WORDS or w in ("in", "part", "and", "the", "is", "are",
                                   "it", "so", "ordered", "case", "cause",
                                   "judgment", "order", "petition", "appeal",
                                   "hereby", "as", "to", "with", "for", "of")
        for w in words)


def _tail_kind(text: str) -> str:
    """A COUNSEL entry announces itself — the lead attorney's name is set in
    caps, or the block is headed by the party it acts for. Everything else
    between the roster and the appearances is the court's own summary."""
    body = text.strip()
    if _is_disposition(body):
        return "summary"
    if body.upper().startswith("FOR ") and ":" in body[:48]:
        return "counsel"
    run = []
    for token in body.replace(",", " ").split():
        letters = [c for c in token if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            run.append(token)
        else:
            break
    return "counsel" if len(run) >= 2 else "summary"


def _closes_party(text: str) -> bool:
    """A caption row ends a party rather than wrapping."""
    plain = re.sub(r"<[^>]+>", "", text).strip()
    if plain.strip(" —–-").rstrip(".").lower() in ("v", "vs", "against",
                                                   "versus"):
        return True
    return plain.endswith((",", ".", ";"))


@decider("headmatter.read", court="ca2")
def read_headmatter_ca2(model, geom, **_):
    """Read ca2's headmatter in whichever style it is set, or NOTHING."""
    if not model.pages:
        return NOTHING
    page = model.pages[0]
    # …and the window is generous because the block can run several pages
    # on a consolidated record (petersen's appearances end on page 5). What
    # stops the reader is its LANDMARKS, not the page count.
    # The counsel block RUNS ON past the page break — one entry per party,
    # and a consolidated record's caption can fill a page by itself, so the
    # appearances land two pages later (powell prints them on page 3). The
    # reader spans the opening pages and lets its LANDMARKS stop it: the
    # caption ends at prose, the tail ends at a byline.
    # NUMBERED PAPER prints a line-number gutter down the left margin, and
    # those numerals are stationery, not text: read as rows they land inside
    # the caption ('9 Plaintiff-Appellant, 10', 'MARK 12 HAMILTON'). Core
    # measures the column — five or more short numeric rows sharing a right
    # edge and spanning the page — so the reader drops it before it walks.
    _gutter: set[int] = set()
    for pm in model.pages[:8]:
        _gutter |= gutter_column_ids(pm)
    # RUNNING HEADS: core measures them — a line printed in the top band on
    # two or more pages. Matching their WORDING instead missed every form
    # the court uses ('23-258 (L); 23-354 (L) Havlish v. Taliban; Aliganga
    # v. Taliban'), and each one then rendered as a headmatter row.
    _top_keys = repeated_top_keys(model, geom.body_size if geom else None)
    lines = [l for pm in model.pages[:8] for l in pm.lines
             if l.plain.strip() and l.id not in _gutter]
    lines.sort(key=lambda l: (l.page, l.top, l.x0))
    texts = [_norm(l.plain) for l in lines]
    # THE STYLE IS NAMED FOR ITS RECITAL, not for its title. 'At a stated
    # term of the United States Court of Appeals for the Second Circuit,
    # held at …' opens the summary order AND the en banc denial that shares
    # its skeleton — bench roster above a rule-fenced caption. Keying on the
    # words 'SUMMARY ORDER' instead read every en banc denial as a ladder,
    # and the ladder, which expects term → dates → docket → caption, never
    # opened the caption at all.
    # The RECITAL identifies the style on its own. Requiring a typed rule
    # as well sent every record that prints none to the ladder reader
    # (rosellini: recital, PRESENT:, SUMMARY ORDER — and not one rule).
    _stated = any(t.lower().startswith("at a stated term") for t in texts[:24])
    if _stated or (any(t.upper() == "SUMMARY ORDER" for t in texts[:12])
                   and any(_RULE.match(t) for t in texts[:40])):
        return _read_stated_term(page, lines, texts, geom, _top_keys)
    return _read_ladder(page, lines, texts, geom, _top_keys)


def _caption_rail(lines) -> float:
    """The left rail of the caption band — the column the party names hold.

    The band opens at the first typed rule and closes at the next. Within it
    the italic status labels and the centered versus row are indented off the
    rail, so the rail is the minimum x0 among the rows that are neither.
    Measured INSIDE the band, never across the headmatter: the recital runs
    to the page margin while the caption may be inset, and a headmatter-wide
    minimum puts every party on the wrong side of the column test.
    """
    band, seen_rule = [], False
    for line in lines:
        text = _norm(line.plain)
        if _RULE.match(text):
            if seen_rule:
                break
            seen_rule = True
            continue
        if not seen_rule or not text:
            continue
        if _italic(line):
            continue
        first = text.split()[0].rstrip(".").lower() if text.split() else ""
        if first in ("v", "vs"):
            continue
        band.append(line.x0)
    if band:
        return min(band)
    return min((l.x0 for l in lines), default=0.0)


def _origin_row(text: str):
    """The tribunal being reviewed, which ca2 stacks above its own banner:

        BIA                  <- the Board of Immigration Appeals
        Straus, IJ           <- the immigration judge
        A209 866 562/563     <- the alien registration number

    A summary order prints no 'On Appeal from' line at all, so this block is
    the ONLY statement of where the case came from — and read as nothing at
    all it leaves three rows of the headmatter unidentified.
    """
    bare = _norm(text)
    if not bare or len(bare) > 40:
        return None
    if bare in ("BIA", "NAC", "AC"):
        return ("lower_court", bare)
    if bare.endswith(", IJ") or bare.endswith(" IJ"):
        return ("lower_court_judge", bare)
    head = bare.split()
    if head and head[0].startswith("A") and head[0][1:].isdigit():
        return ("other_dockets", bare)
    return None


def _counsel_label(text: str) -> bool:
    """'For Plaintiff-Appellant:' — a counsel entry announces its party."""
    head = text.strip()
    if head[:4].lower() != "for ":
        return False
    if ":" in head[:60]:
        return True
    return any(r in head[:90].lower() for r in _STATUS_WORDS)


def _versus_docket(line, text: str, rail: float):
    """The docket off a centered versus row ('v. 25-1830-cv'), or None.

    Returns '' for a bare 'v.' with no docket beside it, so the caller still
    knows the row was the hinge and not a party."""
    bare = text.rstrip(".").strip()
    if bare.lower() in ("v", "vs", "-v-", "- v. -", "- v -"):
        return ""
    first = text.split()[0].rstrip(".").lower() if text.split() else ""
    if first not in ("v", "vs"):
        return None
    if line.x0 <= rail + 6:
        return None
    parts = text.split(None, 1)
    tail = parts[1].strip() if len(parts) > 1 else ""
    if not tail:
        return ""
    return tail if tail.lower().startswith("no.") else f"No. {tail}"


def _wide_gaps(line, min_gap: float = 8.0):
    """Where each wide intra-row gap ends — candidate column starts."""
    chars = [c for c in (line.chars or ()) if (c.get("text") or "").strip()]
    chars.sort(key=lambda c: c.get("x0", 0))
    return [b.get("x0", 0) for a, b in zip(chars, chars[1:])
            if b.get("x0", 0) - a.get("x1", 0) >= min_gap]


def _counsel_gutter(lines):
    """The x of the gutter running through the counsel block, or None.

    A gutter is a vertical band every row steps across at the same place, and
    a row attests to it in one of TWO ways: it either LEAPS the gutter with a
    gap wider than any word space, or — once the label column has run out of
    words — simply BEGINS at the far side. Counting only the leaps found the
    gutter on 6 of 21 rows and rejected it; the 13 rows that start on it are
    the same evidence. Accepted only when a quarter of the rows agree, so a
    single-column block (most records) yields None.
    """
    if not lines:
        return None
    rail = min(l.x0 for l in lines)
    votes: dict[int, int] = {}
    seen: dict[int, list[float]] = {}
    for line in lines:
        cands = list(_wide_gaps(line))
        if line.x0 > rail + 20:
            cands.append(line.x0)
        for x in cands:
            b = round(x / 4) * 4
            votes[b] = votes.get(b, 0) + 1
            seen.setdefault(b, []).append(x)
    if not votes:
        return None
    bucket = max(votes, key=lambda k: votes[k])
    if votes[bucket] < max(2, len(lines) // 4):
        return None
    # The bucket gathers the votes; the CUT must fall on the column's true
    # left edge, or every row loses its opening letter to the label.
    return min(seen[bucket]) - 0.5


def _cut_at(line, boundary: float) -> tuple[str, str]:
    from ..pdfio.text import plain_text
    left = [c for c in (line.chars or ()) if c.get("x0", 0) < boundary]
    right = [c for c in (line.chars or ()) if c.get("x0", 0) >= boundary]
    return _norm(plain_text(left)), _norm(plain_text(right))


def _read_counsel_block(lines) -> list[str]:
    """The counsel block as one string per entry.

    ca2 sets counsel in TWO COLUMNS — the party the entry acts for on the
    left, the attorney and firm on the right. pdfplumber reports each ROW as
    one line, so reading rows in order weaves the columns together ('For
    Debtor-Appellant Julia F. Jeffrey L. Herzberg, Jeffrey Soussis:
    Herzberg, PC, Hauppauge, NY.'). The gutter is measured off the block and
    used to cut every row in two; each column is then read down its own
    length. Records that set counsel in ONE column are read straight down.
    """
    if not lines:
        return []
    gutter = _counsel_gutter(lines)
    if gutter is None:
        entries: list[str] = []
        for line in lines:
            text = _norm(line.plain)
            if not text:
                continue
            if _counsel_label(text) or not entries:
                entries.append(text)
            else:
                entries[-1] = f"{entries[-1]} {text}"
        return entries
    entries, label, body = [], [], []

    def flush():
        head = " ".join(label).strip().rstrip(":").strip()
        tail = " ".join(body).strip()
        if head or tail:
            entries.append(f"{head}: {tail}" if head and tail else head or tail)

    for line in lines:
        left, right = _cut_at(line, gutter)
        if left and _counsel_label(left):
            flush()
            label, body = [], []
        if left:
            label.append(left)
        if right:
            body.append(right)
    flush()
    return entries


def _read_stated_term(page, lines, texts, geom, _top_keys=frozenset()):
    """Dissect a summary-order / en banc-denial headmatter.

    A faithful port of the old engine's reader. The skeleton is fixed and
    every section is announced by something the page itself draws or prints:

        25-1830-cv Brooks v. Bright Horizons   running head
        UNITED STATES COURT OF APPEALS         centered banner
        SUMMARY ORDER                          centered title
        At a stated term ...                   recital, carrying the date
        Present:                               opens the roster
            WILLIAM J. NARDINI, ...            the panel
        ______________________                 OPENS the caption
        AMANDA BROOKS,                         caption rail, caps
            Plaintiff-Appellant,               indented + italic: the status
            v.  25-1830-cv                     centered: the hinge + docket
        ______________________                 CLOSES it, opens counsel
        For Plaintiff-Appellant: NAME ...      one entry per party

    The caption is read BY COLUMN — a name sits on the caption's own rail, a
    status label is indented and italic, the versus row is centered. That is
    what a text-shape walk cannot do, and why it files the defendants under
    counsel.
    """
    crit: dict = {"headmatter_style": STYLE_STATED_TERM,
                  "publication_status": "non-precedential"}
    # Declared for the FINISHED record, applied after assembly: the heading
    # 'SUMMARY ORDER' is what anchors the unsigned writing.
    doc_type = m.DocType.OPINION
    items: list = []
    consumed: set[int] = set()
    head_lines: list = []
    notice: list = []
    recital: list[str] = []
    recital_lines: list = []
    banner: list[str] = []
    panel: list[str] = []
    roster: list[str] = []
    counsel_lines: list = []
    caption_rows: list[str] = []
    sides: list[list[str]] = [[], []]
    side = 0
    docket_from_caption: str | None = None
    state = "court"
    fn_open = False
    fn_first = False
    fn_lines: list = []
    notice_open = False
    notice_size = None
    saw_rule = False
    anchor_ids: list = []
    cols: list = [None, None]
    rail = _caption_rail(lines)
    page_mid = page.width / 2

    def _hm(line, text, center=False, role=""):
        # A caption set in TWO COLUMNS keeps its whitespace: the case runs
        # down the left, the docket and the panel's own name sit to the
        # right, and stacking them flush loses which belongs to which. The
        # offset from the caption's rail is carried on the row and rendered
        # as one — the page's own spacing, not an invented indent.
        rel = 0.0
        if role in ("caption", "lower-court") and not center \
                and line.x0 > rail + 24:
            rel = min(line.x0 - rail, (page.width or 612.0) * 0.5)
        items.append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align.CENTER if center else m.Align.LEFT,
            x0=line.x0, size=line.size or 0.0, rel=rel, role=role))

    for index, line in enumerate(lines):
        text = _norm(line.plain)
        low = text.lower()
        centered = abs((line.x0 + line.x1) / 2 - page_mid) < 25
        italic = _italic(line)
        indented = line.x0 > rail + 20

        if _RULE.match(text):
            # The first rule OPENS the caption; the next closes it and opens
            # the counsel block. A rule while the caption is open only closes
            # it once a party has been seen — consolidated appeals stack
            # captions.
            consumed.add(line.id)
            saw_rule = True
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            if state in ("court", "panel", "after_panel"):
                state = "caption"
            elif state == "caption":
                state = "caption_or_counsel"
            continue

        # Furniture the reader claims: folios, repeated running heads, the
        # citation notice, and footnote apparatus (which core attaches).
        # A folio may be dressed ('- 4 -', '[3]') — it is furniture either
        # way, and undressed it rides into the counsel block as an entry.
        if _FOLIO.match(text.strip()):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # A RUNNING HEAD names the case in the top band, in whatever form
        # the court dresses it ('23-258 (L); 23-354 (L) Havlish v. Taliban;
        # Aliganga v. Taliban'), so an equality test on the short name misses
        # every consolidated record.
        if (crit.get("short_case_name")
                and line.top / (page.height or 792.0) <= 0.22
                and crit["short_case_name"].split(" v")[0].strip() in text):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if crit.get("short_case_name") and text == crit["short_case_name"]:
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if (line.top / (page.height or 792.0) <= 0.22
                and furniture_key(text) in _top_keys):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # …and a docket-shaped row is a RUNNING HEAD only at the top of a
        # page. Mid-page it is the caption's own docket, printed in the
        # right-hand column beside the case ('26-90048-am' over 'ORDER OF /
        # GRIEVANCE PANEL'), and eating it there steals it from the caption.
        # A row in the TOP BAND that carries both a docket and a versus is a
        # running head whatever its form — consolidated records list several
        # ('23-258 (L); 23-354 (L) Havlish v. Taliban; Aliganga v. Taliban').
        if (line.top / (page.height or 792.0) <= 0.22
                and _DOCKET.search(text) and re.search(r"\bv\.?\s", text)
                and len(text) < 120):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if _RUNNING.match(text) and line.top / (page.height or 792.0) <= 0.22:
            # The running head states the docket — read it here, because the
            # furniture skip runs before the banner state and would
            # otherwise throw away the only place a summary order prints it
            # (and leave the short case name beside it stranded).
            if not crit.get("docket_number"):
                crit["docket_number"] = _docket_label(text)
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # THE NOTICE IS A RUN, NOT A LINE. Two cues identify it, but its
        # middle and last lines carry one or none ('CITE EITHER THE FEDERAL
        # APPENDIX OR AN ELECTRONIC DATABASE…', '…ANY PARTY NOT REPRESENTED
        # BY COUNSEL.'), so a per-line test drops the opening and leaves the
        # rest standing. Once opened it runs until a landmark ends it.
        # …and the run follows the TYPE SIZE, not the words. The notice is
        # set in its own size, and its closing lines carry no cue at all
        # ('REPRESENTED BY COUNSEL.' — the 'not' is on the line above), so a
        # cue-per-line test strips the block and leaves its tail standing.
        # The size that opened the run is what ends it.
        _cues = sum(1 for cue in _NOTICE_CUES if cue in low)
        if _cues >= 2 and notice_size is None:
            notice_size = line.size or 0.0
        # …and the run CLOSES ON ITS OWN SENTENCE. Size alone cannot end it:
        # brooks sets the notice in the same 12pt as the banner and the
        # recital, so a size-only run swallowed the recital, the roster and
        # the caption behind it. A notice line that ends in a period ends
        # the notice; one that does not is still mid-sentence.
        _open_sentence = bool(notice) and not notice[-1][1].rstrip().endswith(".")
        if _cues >= 2 or (notice_size is not None
                          and abs((line.size or 0.0) - notice_size) <= 0.4
                          and (_cues >= 1 or (notice_open and _open_sentence))):
            notice_open = True
            notice.append((line, text))
            consumed.add(line.id)
            continue
        notice_open = False
        # (A SECTION SYMBOL IS NOT A FOOTNOTE MARK: '§ 1983. This claim
        # arose from the Officers' arrest…' opens a paragraph of the court's
        # summary, and reading it as a note skipped it and every line that
        # continued it.)
        # FOOTNOTE APPARATUS is CLAIMED and recorded, not merely passed
        # over: passed over, core places it back into the headmatter and the
        # note renders twice — once as a row and once as the footnote. Core
        # reads its notes from the page, not from these segments, so the
        # footnote itself is unaffected.
        _bare_mark = text.strip(" .") in ("*", "†", "‡")
        if _bare_mark or text.lstrip()[:1] in ("*", "†", "‡"):
            fn_open = True
            # A mark ALONE on its row opens a note whose first word is
            # capitalised ('*' / 'The Clerk of Court is instructed to amend
            # the official caption to conform'), so the row after it belongs
            # to the note whatever its case — the lower-case rule only
            # governs the rows after that.
            fn_first = _bare_mark
            fn_lines.append(line)
            consumed.add(line.id)
            continue
        if fn_open:
            if fn_first or text[:1].islower():
                fn_first = False
                fn_lines.append(line)
                consumed.add(line.id)
                continue
            fn_open = False

        _org = _origin_row(text)
        # ca2 STACKS THE TRIBUNAL ABOVE ITS OWN BANNER, so this is read in
        # every state — the rows sit at the very top of page 1, before the
        # court names itself.
        if _org:
            _k, _v = _org
            if _k == "other_dockets":
                crit.setdefault("other_dockets", []).append(_v)
            else:
                crit.setdefault(_k, _v)
            consumed.add(line.id)
            _hm(line, text, role="lower-court")
            continue

        if state == "court":
            if index < 4 and not crit.get("docket_number") \
                    and _DOCKET.search(text) and len(text) < 90:
                mm = _DOCKET.search(text)
                crit["docket_number"] = f"No. {mm.group(1)}"
                rest = text[mm.end():].strip(" .,;")
                if rest:
                    crit["short_case_name"] = rest
                consumed.add(line.id)
                head_lines.append(line)
                continue
            if (index < 5 and crit.get("docket_number")
                    and not crit.get("short_case_name")
                    and " v" in low and len(text) < 90):
                crit["short_case_name"] = text
                consumed.add(line.id)
                head_lines.append(line)
                continue
            # The RECITAL is tested BEFORE the banner: it opens by naming
            # this very court, so the banner test matches it too and
            # swallowed the whole recital into `court`. It runs to three
            # lines and states the date only on the last.
            if low.startswith("at a stated term") or recital:
                if recital and text.rstrip().endswith(".") is False \
                        and not recital[-1].rstrip().endswith("."):
                    pass
                if not recital or not recital[-1].rstrip().endswith("."):
                    recital.append(text)
                    recital_lines.append(line)
                    consumed.add(line.id)
                    continue
            if text.upper() == "SUMMARY ORDER":
                # CLAIMED. Left in the stream it anchors the writing at the
                # TOP of the headmatter, and everything below — caption,
                # panel, counsel — is then inside that writing's span and
                # gets reunited into it (cicchiello: 44 rows read, 5 left,
                # an opinion opening 'SUMMARY ORDER'). The body anchors on
                # its own first prose once the reader has claimed the block.
                crit["title"] = "SUMMARY ORDER"
                consumed.add(line.id)
                anchor_ids.append(line.id)   # …and it can anchor a writing
                _hm(line, text, center=True, role="title")
                continue
            # 'Present:' stands alone or carries its first judge inline.
            if low.rstrip(":") == "present":
                state = "panel"
                consumed.add(line.id)
                _hm(line, text, role="panel")
                continue
            if low.startswith("present:"):
                state = "panel"
                rest = text.split(":", 1)[1].strip()
                if rest and _is_caps(rest):
                    panel.append(rest.rstrip(","))
                roster.append(text)
                consumed.add(line.id)
                _hm(line, text, role="panel")
                continue
            if (centered and len(text) < 50 and _is_caps(text)
                    and any(w in low for w in ("court", "circuit", "appeals"))):
                banner.append(text)
                consumed.add(line.id)
                _hm(line, text, center=True, role="court")
                continue
            consumed.add(line.id)
            _hm(line, text, center=centered)
            continue

        if state == "panel":
            # The roster closes on its italic bench title ('Circuit
            # Judges.') — but only when that title ENDS it. A Chief Judge
            # listed first carries her own title mid-roster, and the
            # trailing comma says more judges follow.
            consumed.add(line.id)
            _hm(line, text, role="panel")
            # The roster closes on the bench title that names the office —
            # italic on most records, roman on some (rosellini sets 'Circuit
            # Judges.' upright, and gating on italics left the roster open
            # to the foot of the document, 46 rows deep).
            if "judge" in low and not text.rstrip().endswith(","):
                roster.append(text)
                state = "after_panel"
                continue
            if italic and "judge" in low:
                roster.append(text)
                continue
            if _is_caps(text):
                panel.append(text.rstrip(","))
                roster.append(text)
            continue

        if state == "after_panel":
            # A rule normally opens the caption; where the court draws none,
            # the caption simply follows the roster, and it opens on the same
            # positive evidence the ladder uses — a caps party name or an
            # italic status label. Without this the rows after the panel are
            # consumed unread.
            if italic or _is_caps(text) or _opens_caps(text):
                state = "caption"
            else:
                consumed.add(line.id)
                _hm(line, text)
                continue

        if state == "caption_or_counsel":
            # An entry announces itself by its PARTY LABEL ('For
            # Plaintiff-Appellant:') or by its LEAD ATTORNEY set in caps
            # ('MATTHEW D. MCGILL, Gibson, Dunn & Crutcher LLP,'). Testing
            # only the label sent havlish's whole appearances block back
            # into the caption — sixty rows of it.
            state = ("counsel" if (_counsel_label(text)
                                   or (_tail_kind(text) == "counsel"
                                       and _FIRM.search(text)))
                     else "caption")

        if state == "caption":
            # A COUNSEL LABEL CLOSES THE CAPTION. The second rule normally
            # does it, but a record that draws no rules at all (rosellini)
            # would otherwise run the caption through the appearances and
            # into the body.
            if _counsel_label(text):
                state = "counsel"
            else:
                versus = _versus_docket(line, text, rail)
                if versus is not None:
                    if versus:
                        docket_from_caption = (
                            f"{docket_from_caption}; {versus}"
                            if docket_from_caption else versus)
                    caption_rows.append(text)
                    side = 1
                    consumed.add(line.id)
                    _hm(line, text, center=centered, role="caption")
                    continue
                if indented and italic:
                    caption_rows.append(text)
                    consumed.add(line.id)
                    _hm(line, text, center=centered, role="caption")
                    continue
                if line.x0 <= rail + 6:
                    # A party name wraps across as many rows as it needs; each
                    # continuation returns to the same rail, so fold it into the
                    # name above rather than starting a new party.
                    if caption_rows and not _closes_party(caption_rows[-1]):
                        caption_rows[-1] = f"{caption_rows[-1]} {text}"
                        if sides[side]:
                            sides[side][-1] = f"{sides[side][-1]} {text}"
                        else:
                            sides[side].append(text)
                    else:
                        caption_rows.append(text)
                        sides[side].append(text)
                    consumed.add(line.id)
                    _hm(line, text, center=centered, role="caption")
                    continue
                # A CONSOLIDATED appeal lists its remaining dockets flush right
                # under the versus row, each tagged with its role.
                consumed.add(line.id)
                _hm(line, text, center=centered, role="caption")
                continue

        if state == "counsel":
            # THE COUNSEL BLOCK ENDS AT THE COURT'S OWN PROSE. The original
            # needs no bound here because it walks a headmatter span the
            # extractor already delimited; this reader walks raw pages, so
            # without a stop the appearances run to the end of the document
            # and take every writing with them (carroll: 1342 headmatter
            # rows, one writing left). An entry sets its label at the rail
            # and its appearance in the gutter column — a full-measure row
            # of prose AT the rail is the writing's first line.
            # The block is a GUTTER: the party label at the rail, the
            # appearance in its own column. A row that belongs to neither
            # column is the writing's, and that is what ends the block —
            # measured off the block itself, since the indent varies by
            # record. (A prose test alone stops too early: an entry's own
            # continuation is prose.)
            # A SAME-ROW PIECE continues its row whatever its x0. The last
            # entry is often set with wide inter-word gaps, and pdfplumber
            # reports each gap as a new line ('…for Michael' / 'DiGiacomo,' /
            # 'United' / 'States' / 'Attorney for the Western District…'),
            # so a column test reads the pieces as rows outside the gutter
            # and ends the block in the middle of the last appearance.
            _same_row = (counsel_lines
                         and abs(line.top - counsel_lines[-1].top) < 2
                         and line.page == counsel_lines[-1].page)
            # A block with no party labels never sets a label column, so the
            # gutter test above can never fire and nothing ends the
            # appearances (havlish's entries open on the attorney's name and
            # ran straight into the per curiam). The columns the block
            # ITSELF uses are the bound: a prose row outside all of them is
            # the writing's.
            if (not _same_row and counsel_lines
                    and any(c.islower() for c in text) and len(text) > 60
                    and not _counsel_label(text)
                    and all(abs(line.x0 - l.x0) > 6 for l in counsel_lines)):
                break
            if not _same_row:
                if _counsel_label(text) and cols[0] is None:
                    cols[0] = line.x0
                elif cols[0] is not None and cols[1] is None \
                        and line.x0 > cols[0] + 40:
                    cols[1] = line.x0
                if counsel_lines and cols[1] is not None and not any(
                        abs(line.x0 - c) <= 6 for c in cols if c is not None):
                    break
                # …and a row sitting IN the label column that is not a label
                # and reads as prose is the writing's first line: the body
                # opens at the same measure the labels do ('Appeal from a
                # judgment of the United States District Court…' at x0 108).
                if (counsel_lines and cols[0] is not None
                        and abs(line.x0 - cols[0]) <= 6
                        and not _counsel_label(text)
                        and any(c.islower() for c in text) and len(text) > 60):
                    break
            if counsel_lines and cols[1] is None and line.x0 <= rail + 6 \
                    and not _counsel_label(text) \
                    and any(c.islower() for c in text) and len(text) > 60:
                break
            counsel_lines.append(line)
            consumed.add(line.id)
            _hm(line, text, role="counsel")
            continue

    if recital:
        crit["decision_date"] = recital_date(_norm(" ".join(recital))) or None
    if banner:
        crit["court"] = _norm(" ".join(banner))
    if panel:
        crit["panel"] = panel
        crit["panel_line"] = _norm(" ".join(roster)) or None
        crit["judges"] = crit.get("panel_line")
    if docket_from_caption and not crit.get("docket_number"):
        crit["docket_number"] = docket_from_caption
    if caption_rows:
        crit["caption"] = caption_rows
        left = _norm(" ".join(sides[0])).rstrip(",. ")
        right = _norm(" ".join(sides[1])).rstrip(",. ")
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
    entries = _read_counsel_block(counsel_lines)
    if entries:
        crit["attorneys"] = " ".join(entries)[:2000]

    dropped = [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                         kind="running-head") for l in head_lines]
    dropped += [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                          kind="footnote") for l in fn_lines]
    if recital_lines:
        dropped.append(m.Dropped(
            text=_norm(" ".join(recital))[:1200],
            prov=m.Prov(recital_lines[0].page,
                        tuple(l.id for l in recital_lines)),
            kind="recital"))
    if notice:
        dropped.append(m.Dropped(
            text=_norm(" ".join(t for _, t in notice))[:1200],
            prov=m.Prov(notice[0][0].page, tuple(l.id for l, _ in notice)),
            kind="notice"))
    if not (caption_rows or panel):
        return NOTHING
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": doc_type}


def _read_ladder(page, lines, texts, geom, _top_keys=frozenset()):
    """Dissect a published-opinion headmatter — the 'ladder' family.

    Four short rules rung the page into zones and everything between them is
    centered (numbered paper sets the same sections flush left, over a
    line-number gutter, with typed rules instead of drawn ones — one layout,
    one reader):

        24-1510  Adidas America, Inc. v. Thom Browne     running head
        United States Court of Appeals / for the Second Circuit
        ─────────
        August Term 2025                                 the term…
        Argued: October 28, 2025  Decided: April 29, 2026  …and its dates
        No. 24-1510                                      the docket
        ─────────
        ADIDAS AMERICA, INC., ADIDAS AG,                 caption: parties
            Plaintiffs-Appellants,                       …statuses italic
        v.                                               …the hinge
        ─────────
        On Appeal from the United States District Court  the origin: court…
        No. 21-cv-5615                                   …its docket…
        Jed S. Rakoff, Judge.                            …and the trial judge
        ─────────
        Before: CABRANES, PARK, and ROBINSON, Circuit Judges.
        <the court's own case summary>
        ADAM H. CHARNES, Kilpatrick …                    counsel, indented

    The ladder is the style's LOOK, not its spine. The group draws its rules
    at four widths, doubles one, catches a footnote separator among them, and
    two records draw none at all — so counting rungs mis-zones the page. The
    sections are found by their own LANDMARKS in the order the style prints
    them, with geometry settling what a landmark cannot.
    """
    crit: dict = {"headmatter_style": STYLE_LADDER}
    items: list = []
    attorneys: list = []
    summary_rows: list = []
    consumed: set[int] = set()
    banner: list[str] = []
    panel: list[str] = []
    origin: list[str] = []
    counsel_rows: list = []
    caption_rows: list = []
    head_lines: list = []
    notice: list = []
    notice_open = False
    notice_size = None
    saw_rule = False
    fn_first = False
    fn_lines: list = []
    sides: list[list[str]] = [[], []]
    side = 0
    state = "head"
    counsel_open = False
    fn_open = False
    wrap_run = 0
    body_rail = min((l.x0 for l in lines), default=72.0)

    def _hm(line, text, center=False, role=""):
        # A caption set in TWO COLUMNS keeps its whitespace: the case runs
        # down the left, the docket and the panel's own name sit to the
        # right, and stacking them flush loses which belongs to which. The
        # offset from the caption's rail is carried on the row and rendered
        # as one — the page's own spacing, not an invented indent.
        rel = 0.0
        if role == "caption" and not center and line.x0 > body_rail + 24:
            rel = min(line.x0 - body_rail, (page.width or 612.0) * 0.5)
        items.append(m.HmLine(
            text=text, prov=m.Prov(line.page, (line.id,)),
            align=m.Align.CENTER if center else m.Align.LEFT,
            x0=line.x0, size=line.size or 0.0, rel=rel, role=role))

    page_mid = page.width / 2
    for index, line in enumerate(lines):
        text = _norm(line.plain)
        low = text.lower()
        centered = abs((line.x0 + line.x1) / 2 - page_mid) < 25
        italic = _italic(line)

        # A typed rule CLOSES the section it ends. Numbered paper rules its
        # caption top and bottom and rules the origin off the dates below —
        # without closing here the caption collected everything after it.
        if _RULE.match(text):
            consumed.add(line.id)
            saw_rule = True
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            if state == "caption" and caption_rows:
                state = "tail"
            elif state == "origin" and origin:
                state = "tail"
            continue

        # The writing's own byline ends the headmatter, whatever state we are
        # in — the reader must never reach into an opinion.
        if _BYLINE_TAIL.search(text) and (counsel_rows or summary_rows):
            break

        # THE RUNNING HEAD opens the page and is furniture, but it states
        # the docket and the court's own short case name. It is not always
        # the first row: cruz prints the FOLIO above it ('1' / '24-1147' /
        # 'Cruz v. Banks'), so an index test misses the head entirely and
        # leaves all three rows rendering as headmatter.
        # A FOLIO or a repeated RUNNING HEAD prints on every page the
        # reader spans, not just the first. Left in, they stack up inside
        # the headmatter as stray numerals and case-name rows.
        # A folio may be dressed ('- 4 -', '[3]') — it is furniture either
        # way, and undressed it rides into the counsel block as an entry.
        if _FOLIO.match(text.strip()):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if crit.get("short_case_name") and _norm(text) == crit["short_case_name"]:
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if (line.top / (page.height or 792.0) <= 0.22
                and furniture_key(text) in _top_keys):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # …and a docket-shaped row is a RUNNING HEAD only at the top of a
        # page. Mid-page it is the caption's own docket, printed in the
        # right-hand column beside the case ('26-90048-am' over 'ORDER OF /
        # GRIEVANCE PANEL'), and eating it there steals it from the caption.
        # A row in the TOP BAND that carries both a docket and a versus is a
        # running head whatever its form — consolidated records list several
        # ('23-258 (L); 23-354 (L) Havlish v. Taliban; Aliganga v. Taliban').
        if (line.top / (page.height or 792.0) <= 0.22
                and _DOCKET.search(text) and re.search(r"\bv\.?\s", text)
                and len(text) < 120):
            consumed.add(line.id)
            head_lines.append(line)
            continue
        if _RUNNING.match(text) and line.top / (page.height or 792.0) <= 0.22:
            # The running head states the docket — read it here, because the
            # furniture skip runs before the banner state and would
            # otherwise throw away the only place a summary order prints it
            # (and leave the short case name beside it stranded).
            if not crit.get("docket_number"):
                crit["docket_number"] = _docket_label(text)
            consumed.add(line.id)
            head_lines.append(line)
            continue
        # THE CITATION NOTICE is publisher apparatus wherever it prints and
        # whatever state the reader is in, and its run follows the TYPE SIZE
        # it is set in — its closing lines carry no cue of their own.
        _cues = sum(1 for cue in _NOTICE_CUES if cue in low)
        if _cues >= 2 and notice_size is None:
            notice_size = line.size or 0.0
        # …and the run CLOSES ON ITS OWN SENTENCE. Size alone cannot end it:
        # brooks sets the notice in the same 12pt as the banner and the
        # recital, so a size-only run swallowed the recital, the roster and
        # the caption behind it. A notice line that ends in a period ends
        # the notice; one that does not is still mid-sentence.
        _open_sentence = bool(notice) and not notice[-1][1].rstrip().endswith(".")
        if _cues >= 2 or (notice_size is not None
                          and abs((line.size or 0.0) - notice_size) <= 0.4
                          and (_cues >= 1 or (notice_open and _open_sentence))):
            notice_open = True
            notice.append((line, text))
            consumed.add(line.id)
            continue
        notice_open = False
        # FOOTNOTE APPARATUS, in ANY state — the ladder tested it only in
        # its tail, so a note printed beside the origin ('* The Clerk of
        # Court is respectfully directed to amend the official case caption
        # as set forth above.') was read as part of the lower court.
        _bare_mark = text.strip(" .") in ("*", "†", "‡")
        if _bare_mark or text.lstrip()[:1] in ("*", "†", "‡"):
            fn_open = True
            # A mark ALONE on its row opens a note whose first word is
            # capitalised ('*' / 'The Clerk of Court is instructed to amend
            # the official caption to conform'), so the row after it belongs
            # to the note whatever its case — the lower-case rule only
            # governs the rows after that.
            fn_first = _bare_mark
            fn_lines.append(line)
            consumed.add(line.id)
            continue
        if fn_open:
            if fn_first or text[:1].islower():
                fn_first = False
                fn_lines.append(line)
                consumed.add(line.id)
                continue
            fn_open = False
        if index < 4 and state == "head":
            if text.strip().isdigit() and len(text.strip()) <= 3:
                consumed.add(line.id)
                head_lines.append(line)
                continue
            if not crit.get("docket_number") and _DOCKET.search(text) \
                    and len(text) < 90:
                mm = _DOCKET.search(text)
                crit["docket_number"] = f"No. {mm.group(1)}"
                rest = text[mm.end():].strip(" .,;")
                if rest:
                    crit["short_case_name"] = rest
                consumed.add(line.id)
                head_lines.append(line)
                continue
            if crit.get("docket_number") and not crit.get("short_case_name") \
                    and " v" in low and len(text) < 90:
                crit["short_case_name"] = text
                consumed.add(line.id)
                head_lines.append(line)
                continue

        # The masthead runs to three lines as often as two ('In the' /
        # 'United States Court of Appeals' / 'for the Second Circuit').
        if state == "head" and (
                low in ("in the",)
                or ("court of appeals" in low or "second circuit" in low)
                and len(text) < 60):
            banner.append(text)
            consumed.add(line.id)
            _hm(line, text, center=centered, role="court")
            continue

        if state in ("head", "front") and _TERM_ROW.search(low) and any(
                t.strip(",.").isdigit() and len(t.strip(",.")) == 4
                for t in low.split()):
            crit["term"] = text
            state = "front"
            consumed.add(line.id)
            _hm(line, text, center=centered, role="date")
            continue

        # The sitting dates may share a row and may be parenthesised. Tested
        # in ANY state: barrett prints them BELOW the origin, and gated to
        # the front they fell through to the tail, where an all-caps row
        # reads as a counsel entry and opened the appearances block.
        found = _DATE_LABEL.findall(text)
        if found:
            for label, value in found:
                key = label.lower()
                value = value.strip().rstrip(".")
                if key in ("decided", "filed", "amended"):
                    crit["decision_date"] = value
                elif key in ("argued", "submitted", "reargued"):
                    crit["submitted"] = value
            if state in ("head", "front"):
                state = "front"
            consumed.add(line.id)
            _hm(line, text, center=centered, role="date")
            continue

        # The APPELLATE docket stands alone before the caption; the district
        # court's own looks the same but comes after the origin opener, so
        # the STATE — not the shape — tells them apart.
        if state in ("head", "front") and _BARE_DOCKET.match(text):
            crit["docket_number"] = _docket_label(text)
            state = "front"
            consumed.add(line.id)
            _hm(line, text, center=centered, role="docket")
            continue

        # THE ORIGIN IS STATED ONCE, AND ABOVE THE PANEL. The court's own
        # summary opens with the very same words, so the bound is the roster:
        # everything the court says about where the case came from is printed
        # above it.
        if not origin and not panel and low.startswith(_ORIGIN_OPENER):
            state = "origin"
            origin.append(text)
            consumed.add(line.id)
            _hm(line, text, role="lower-court")
            continue

        # The panel label may be LETTER-SPACED ('B e f o r e:'), which no
        # prefix test on the printed text can match.
        if "".join(low.split()).startswith("before") and (
                "judge" in low or ":" in text):
            crit["panel_line"] = text
            roster = text.split(":", 1)[1].strip() if ":" in text else text
            panel.extend(_roster_names(roster))
            state = "tail" if _roster_closed(text) else "panel"
            consumed.add(line.id)
            _hm(line, text, role="panel")
            continue

        if state == "panel":
            crit["panel_line"] = f"{crit.get('panel_line','')} {text}".strip()
            panel.extend(_roster_names(text))
            if _roster_closed(text):
                state = "tail"
            consumed.add(line.id)
            _hm(line, text, role="panel")
            continue

        if state == "origin":
            origin.append(text)
            consumed.add(line.id)
            _hm(line, text, role="lower-court")
            continue

        # NOTHING ABOVE THE MASTHEAD IS CAPTION: the running head sits up
        # there, and read as a party it opened the caption before the
        # masthead and swallowed the term, the dates and the docket.
        if state == "head" and not banner:
            if not crit.get("short_case_name"):
                crit["short_case_name"] = text
            consumed.add(line.id)
            head_lines.append(line)
            continue

        # The caption opens on POSITIVE evidence — a party name in caps or an
        # italic status label. Falling into it on any unrecognised line meant
        # one stray row captured the rest of the headmatter.
        if state in ("head", "front"):
            if not (italic or _is_caps(text)
                    or _is_caps(text.split(",")[0])):
                continue
            state = "caption"

        if state == "caption":
            # A CAPTION IS NOT PROSE — the same bound the stated-term reader
            # needs. The old engine could do without it because its readers
            # walk a headmatter span the extractor has already delimited;
            # this one walks raw page lines, so every state carries its own
            # end. Without it the caption ran to the foot of the document
            # (rosellini swallowed the order, the clerk's signature and a
            # footnote) and the writing lost its start.
            _wide = (line.x1 - line.x0) >= 0.7 * (
                geom.column if geom else 300.0)
            # …and BODY PROSE STARTS AT THE RAIL. A caption's own wraps are
            # indented from it (vidal sets its defendant list at 80-95
            # against a body rail of 72), so width and case alone break the
            # caption in the middle of a party list.
            _at_rail = line.x0 <= min(l.x0 for l in lines) + 6
            _open_party = _opens_caps(text)
            # A party row WRAPS as far as the measure takes it — powell
            # sets one party across ten rows — so the run is not capped;
            # what ends it is a row that closes the party.
            _mid_wrap = (bool(caption_rows)
                         and not _closes_party(
                             caption_rows[-1] if isinstance(
                                 caption_rows[-1], str)
                             else caption_rows[-1][1]))
            # …and only where NO RULE will close the caption. A record that
            # fences its caption with typed rules needs no prose bound, and
            # applying one cuts a wrapped party list in half (campbell's
            # defendants run seven rows at the body rail, each continuation
            # opening lower-case).
            if (not saw_rule
                    and _wide and _at_rail and any(c.islower() for c in text)
                    and len(text) > 60
                    and not _open_party and not _mid_wrap):
                break
            wrap_run = 0 if _closes_party(text) else wrap_run + 1
            consumed.add(line.id)
            _hm(line, text, center=centered, role="caption")
            bare = text.strip().strip("—–-").strip().rstrip(".").strip().lower()
            if bare in ("v", "vs", "against", "versus"):
                caption_rows.append(text)     # the hinge is KEPT as printed
                side = 1
                continue
            if italic or _is_status_label(text):
                caption_rows.append(text)     # a status names the role
                continue
            if caption_rows and not _closes_party(caption_rows[-1]):
                caption_rows[-1] = f"{caption_rows[-1]} {text}"
                if sides[side]:
                    sides[side][-1] = f"{sides[side][-1]} {text}"
                else:
                    sides[side].append(text)
            else:
                caption_rows.append(text)
                sides[side].append(text)
            continue

        # ---- past the panel: the court's summary, then counsel ----
        # Counsel is set INDENTED past the body rail, and how far varies by
        # record, so the indent is measured off the document's own rail. The
        # kind test still has to agree: the summary's first lines are
        # indented that far too, and are told apart by the all-caps lead
        # attorney a counsel entry opens with.
        # A counsel entry is opened by its PARTY LABEL, which sits at the
        # rail ('For Defendant-Appellee:') with the appearance beside it in
        # the gutter column. Requiring the indent missed every label and
        # left them — and their entries — in the court's summary.
        is_label = low.startswith("for ") and ":" in text[:48]
        if counsel_open or is_label or (line.x0 >= body_rail + 20
                                        and _tail_kind(text) == "counsel"):
            _hm(line, text, role="counsel")
            if is_label or not counsel_rows:
                counsel_rows.append(([line], text))
            else:
                # A merged continuation keeps ITS OWN line in the entry's
                # provenance — dropping it consumed the line without placing
                # it, and every such line came back as residual content.
                ls, t0 = counsel_rows[-1]
                counsel_rows[-1] = (ls + [line], f"{t0} {text}")
            counsel_open = True
            consumed.add(line.id)
            continue
        if state == "tail":
            # A LONE FOOTNOTE MARK ends the headmatter's own rows: what
            # follows is note apparatus, and core already attaches it as a
            # headmatter footnote. Claimed here as well, it renders twice —
            # once as a note and once as a stray summary row ('*' / 'The
            # Clerk of Court is instructed to amend the official caption…').
            # …a SYMBOL mark only. A bare digit is a folio or a body
            # footnote reference as often as a note opener, and breaking on
            # it ended the headmatter partway through the court's summary.
            # FOOTNOTE APPARATUS IS SKIPPED, NOT STOPPED AT. The mark may
            # stand alone or lead the note's own text ('* The Clerk of Court
            # is respectfully directed to amend the official caption…').
            # Claimed, it renders twice — once here and once as the footnote
            # it is; stopped at, the court's summary below it is lost. So it
            # is passed over, together with its continuation rows, and core
            # attaches it as the headmatter footnote it is.
            if (text.strip(" .") in ("*", "†", "‡")
                    or text.lstrip()[:1] in ("*", "†", "‡")):
                fn_open = True
                continue
            if fn_open:
                if text[:1].islower():
                    continue          # the note wraps
                fn_open = False
            summary_rows.append((line, text))
            consumed.add(line.id)
            _hm(line, text, role="summary")

    if banner:
        crit["court"] = _norm(" ".join(banner))
    if panel:
        crit["panel"] = panel
        crit["judges"] = crit.get("panel_line")
    if origin:
        # The origin names three things and wraps between them: the COURT
        # ('On Appeal from the United States District Court' / 'for the
        # Southern District of New York'), then its OWN docket, then who
        # tried it ('Jed S. Rakoff, Judge.'). The docket and the judge share
        # a row as often as not, so the docket row is cut at its first comma
        # and whatever follows joins the judge.
        court_rows, low_docket, judge = [], None, []
        for row in origin:
            rl = row.lower()
            if rl.startswith("no.") or any(k in rl for k in
                                           ("-cv-", "-cr-", "-md-", "-mc-")):
                head, sep, tail = row.partition(",")
                low_docket = (head if sep else row).strip()
                if tail.strip():
                    judge.append(tail.strip())
                continue
            # A row that IS a bench title continues the judge above it
            # ('… Geoffrey W. Crawford,' / 'District Judge.'); a row that
            # ENDS in one names the judge outright ('Jed S. Rakoff, Judge.').
            _rt = rl.rstrip(".").strip()
            if _rt in ("judge", "district judge", "chief judge",
                       "senior judge", "chief district judge",
                       "magistrate judge") or judge or re.search(
                       r",\s*(?:u\.?s\.?\s*)?(?:chief\s+|senior\s+|"
                       r"district\s+|magistrate\s+|circuit\s+)*judges?\.?$",
                       rl):
                judge.append(row)
                continue
            court_rows.append(row)
        crit["lower_court"] = _norm(" ".join(court_rows))
        if low_docket:
            crit["other_dockets"] = [low_docket]
        if judge:
            crit["lower_court_judge"] = _norm(" ".join(judge)).rstrip(".")
    if caption_rows:
        crit["caption"] = caption_rows
        left = _norm(" ".join(sides[0])).rstrip(",. ")
        right = _norm(" ".join(sides[1])).rstrip(",. ")
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
    # Counsel and the court's own summary are printed in the headmatter and
    # stay there (rendered above, line by line, where the page puts them);
    # only their MEANING is lifted into criteria.
    if counsel_rows:
        crit["attorneys"] = " ".join(t for _, t in counsel_rows)[:2000]
    summary: list = []
    if not (caption_rows or panel or crit.get("docket_number")):
        return NOTHING            # not a ladder — leave it to core
    dropped = [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                         kind="running-head") for l in head_lines]
    dropped += [m.Dropped(text=_norm(l.plain), prov=m.Prov(l.page, (l.id,)),
                          kind="footnote") for l in fn_lines]
    if notice:
        dropped.append(m.Dropped(
            text=_norm(" ".join(t for _, t in notice))[:1200],
            prov=m.Prov(notice[0][0].page, tuple(l.id for l, _ in notice)),
            kind="notice"))
    return {"criteria": crit, "items": items, "attorneys": attorneys,
            "summary": summary, "dropped": dropped, "consumed": consumed}
