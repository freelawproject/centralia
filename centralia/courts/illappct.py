"""Appellate Court of Illinois ('illappct').

Everything unique to illappct lives here. It imports core, never another
court file, and no other court file imports it.

THE PUBLISHER IS THE SAME AS ill's — the Illinois Official Reports — so the
paper opens the same way and the FIRST ROW IS THE COURT'S OWN
PUBLIC-DOMAIN CITATION, not a docket:

    2026 IL App (1st) 252082          the CITATION -> Criteria.citation
                     FIFTH DIVISION   the division, flush right
                         July 17, 2026
                IN THE                \\
      APPELLATE COURT OF ILLINOIS      >  the masthead, centred
            FIRST DISTRICT            /
    No. 1-25-2082                     the DOCKET -> Criteria.docket_number
    4310-4322 N. CLARENDON …    )  Appeal from the      the caption, fenced
    ASSOCIATION, an Illinois …  )  Circuit Court of     by the BRACE RAIL

`YYYY IL App (Nth) NNNNNN[-U|-B]` and `No. N-NN-NNNN` are DIFFERENT THINGS.
ill shipped for a month with its `2025 IL 130862` row tagged `docket`, so
every cover printed two dockets and `Criteria.citation` — the field
model.py:242 exists for exactly this row — stayed empty on all 50 files.
Here the citation also carries the paper's publication status in its own
suffix (`-U` is a Rule 23 order), which is why it is read as a form and not
as a string.

TWO LAYOUT CONTRACTS, and the page declares which one before a word is read.

    'braced cover' (38 of 42). THE RAIL IS NOT DRAWN: the court types it,
    a COLUMN of ')' characters at one x, 8 to 33 glyphs tall. Measured over
    the corpus the column sits anywhere from x=308 to x=374 — it is a
    per-record measurement, never a threshold — and it is what tells the
    two halves of the caption apart: left of it the parties, right of it
    the origin (`Appeal from the / Circuit Court of / Cook County.`), the
    trial number and the trial judge. Nothing is decided by wording:
    membership is decided glyph by glyph by which side of the measured
    column a character's x0 falls on. The rail's own glyphs are shed.

    The rail is also why the caption cannot be read a piece at a time. The
    court sets left cell, rail and right cell as three pieces of one
    baseline when the gaps are wide and as ONE piece when they are not
    ('OWNERS, and NON-RECORD CLAIMANTS, )'), so a whole-piece test puts
    the origin in the party column on one record and not on the next.

    'ruled ladder' (4 of 42 — the Second District). No rail at all: the
    caption is CENTRED, and the zones are fenced by THREE DRAWN RULES of
    396pt centred on the page axis at the body rail. The rules are the
    parser: above the first, the identifiers; between the first and the
    second, the masthead; between the second and the third, the caption;
    below the third, the announcement. Read by wording this record looks
    like an unfenced ill cover; read by its rules it is unambiguous.

    Neither a rail nor a ladder, and the record is not one of these papers:
    the reader returns NOTHING and core's shared walk has it.

WHY THE HEAD BAND IS READ ONE PIECE AT A TIME. Three of the five districts
lay a marginal block on its OWN baseline grid beside the identifiers — the
Fourth District's clerk stamp ('FILED / August 11, 2026 / Carla Bender /
4th District Appellate / Court, IL'), the Fifth District's 7pt advisory
('NOTICE / Decision filed 08/11/26. The text of this decision may be
changed …'). The grids collide: pdfio hands back 'This order was filed
under' (7pt), 'NO. 5-26-0428' (12pt) and 'text of this decision may be'
(7pt) as ONE row, and joining them by baseline destroys the docket. So

  * a piece OFF THE PAGE'S BODY SIZE in the head band is the other grid —
    it is marginal furniture, recorded as `Dropped`, never read;
  * in the head band each piece is its own row. Two grids at the SAME size
    still collide (the Fifth District's 'Rule 23 Order filed' stamp stands
    at the body rail beside the centred citation on one baseline), and no
    head-band row in the corpus needs two pieces joined.

  Inside the CAPTION the opposite holds: the pieces of one baseline are the
  two cells and the rail, and they must be grouped.

WHERE THE READER STOPS. At the ANNOUNCEMENT — the court's own statement of
who wrote and who concurred ('JUSTICE MIKVA delivered the judgment of the
court, with opinion.' / 'Justices Rochford and Reyes concurred …'). The
whole run belongs to the writing and the reader does not take it; it is
READ for the panel and left exactly where the page put it. The run is
found by its opening BENCH TITLE — a closed role vocabulary — rather than
by parsing the byline, because the court sets a footnote mark on the
author's name ('JUSTICE CLARKE∗ delivered …', people_v._lee) and core's
byline grammar does not survive it.

HOW FAR THE BLOCK RUNS. Usually page 1, but a caption naming every unit
owner of a condominium tower runs to page 4 (pepper_construction: 153 party
rows against six in the origin column). The walk is bounded by the
announcement, not by the page.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

# THE PROFILE IS NOT REGISTERED HERE. illappct's CourtProfile still lives in
# `courts/__init__.py`; registering a second one raises, so the reader reads
# the declared facts off the registry instead of restating them.
ILLAPPCT = get_profile("illappct")

STYLE_BRACED = "braced cover"
STYLE_LADDER = "ruled ladder"

# ---- illappct's declared facts (measured over the 42-record corpus) -------
# THE BRACE RAIL. A rail is a COLUMN — glyphs stacked at one x — not a count
# of ')' anywhere on the page. Corpus: 8 to 33 glyphs, x from 308 to 374.
_RAIL_GLYPH = ")"
_RAIL_FLOOR = 6
_RAIL_TOL = 3.0
# The rail's own measure and the clearance either side of it.
_RAIL_WIDTH = 4.0
_RAIL_GUTTER = 2.0
# THE SECOND DISTRICT'S LADDER: three drawn rules, 396.0-396.7pt wide,
# centred on the page axis to a tenth of a point, at the body rail.
_LADDER_MEASURE = (390.0, 402.0)
_LADDER_AXIS = 6.0
_LADDER_FLOOR = 3
# A DRAWN RULE the court uses as a fence anywhere else in the block. The
# 26-37pt rects are the boxes round the Fourth and Fifth Districts' NOTICE
# labels and are not fences; a 144pt rule at the foot is a footnote
# separator and is below the reader's end anyway.
_FENCE_MIN = 200.0
# TWO GRIDS, ONE SIZE EACH. Anything off the page's body size in the head
# band is the marginal stamp/advisory, laid on its own baselines.
_SIZE_TOL = 0.6
# Off-grid pieces further apart than this in x are two different marginal
# blocks (the Fifth District sets one at each margin).
_STAMP_GAP = 120.0
# One visual row: pieces sharing a baseline to this tolerance.
_BASELINE_TOL = 2.5
# HOW FAR THE BLOCK MAY RUN. pepper_construction's caption reaches page 4.
_MAX_PAGES = 6

# THE PUBLIC-DOMAIN CITATION. 'YYYY IL App (Nth) NNNNNN', with the
# districts numbered one through five, and a suffix that names the paper:
# '-U' a Rule 23 order (not precedential), '-B' a supplemental opinion.
# Illinois abbreviates its own ordinals '1st, 2d, 3d, 4th, 5th' — the
# reporter's form, not the printer's, and '(2nd)' never appears.
_CITE = re.compile(r"^(\d{4})\s+IL\s+App\s+\(\s*(\d)\s*(?:st|nd|rd|d|th)\s*\)"
                   r"\s+([\w‐-―-]+)$", re.I)
_UNPUB_SUFFIX = "u"
# THE DOCKET. 'No. 1-25-2082' / 'NO. 4-25-0384' / 'Nos. 1-23-1476 and
# 1-23-2101 (cons.)' / 'NOS. 4-26-0403, 4-26-0405, … cons.' Read as the
# SEQUENCE of appeals it names: a consolidation is companion appeals, not
# one number with a comma in it.
_DOCKET_LEAD = re.compile(r"^NOS?\.\s+(.*)$", re.I)
_APPEAL_NO_LEAD = re.compile(r"^Appeal\s+NOS?\.\s+(.*)$", re.I)
_CONS = re.compile(r"\(?\bcons\.?\)?\.?$", re.I)
# A DOCKET NUMBER on this court is 'D-YY-NNNN' — the district, the year of
# filing and the sequence. Nothing else is accepted as one.
_DOCKET_NUM = re.compile(r"^\d[‐-―-]\d{2}[‐-―-]\d{3,5}$")
# THE DIVISION / DISTRICT the panel sits in, flush right in the top band or
# centred in the masthead. A closed ordinal vocabulary.
_ORD = (r"(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|"
        r"TENTH|ELEVENTH|TWELFTH)")
_DIVISION = re.compile(rf"^{_ORD}\s+(?:DIVISION|DISTRICT)$", re.I)
# THE MASTHEAD names the court, and this court's name is a DECLARED FACT of
# the paper, not an open vocabulary read out of the page. Geometry cannot
# take it here: the masthead is centred and so are the citation, the docket
# and the release date, the docket falls BELOW the masthead on twelve
# records and ABOVE it on the rest, and two records print no masthead at
# all — a 'contiguous centred run' test is defeated by the corpus.
_MASTHEAD_KEY = "APPELLATE COURT"
_MASTHEAD_LEAD = "IN THE"
_MASTHEAD_TAIL = re.compile(
    rf"^(?:OF\s+ILLINOIS|{_ORD}\s+(?:JUDICIAL\s+)?DISTRICT|\d{{4}})$", re.I)
# THE RELEASE ROW. A closed set of leaders, and a date. The Fifth District
# prints its filing history as two entries in the margin ('Rule 23 Order
# filed' / a date / 'Motion to publish granted' / a date), so a leader may
# stand alone on its row with the date beneath it.
_MONTHS = (r"(?:January|February|March|April|May|June|July|August|"
           r"September|October|November|December)")
_DATE = re.compile(rf"{_MONTHS}\s+\d{{1,2}},?\s+\d{{4}}")
_SHORT_DATE = re.compile(r"\b(\d{2})/(\d{2})/(\d{2})\b")
_MONTH_NAMES = ("January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November",
                "December")
_DATE_LEADS = ("rule 23 order filed", "motion to publish granted",
               "opinion filed:", "opinion filed", "order filed",
               "opinion:", "filed:", "filed")
_MOTION_LEAD = "motion to publish granted"
# THE RULE 23 NOTICE set at body size (the Second and Third Districts print
# it in the text face; the Fourth and Fifth set it in the margin, where the
# size test already takes it). A notice is a RUN: it opens on its cue and
# closes on its own sentence.
_NOTICE_CUE = "notice:"
# THE PAPER FLAGGING ITSELF. A closed vocabulary of one entry so far.
_FLAGS = ("corrected", "corrected opinion", "modified opinion")
# A TYPED RULE — the Third and Fifth Districts fence with underscores.
_TYPED_RULE = re.compile(r"^_{8,}$")
# BENCH TITLES — the closed vocabulary that opens the announcement run and,
# inside it, every name run. Longest first so 'Presiding Justice' wins.
_BENCH = ("Presiding Justices", "Presiding Justice", "Chief Justices",
          "Chief Justice", "Justices", "Justice")
# THE ORIGIN COLUMN'S GRAMMAR, all closed leads.
_ORIGIN_LEAD = re.compile(r"^(?:On\s+)?Appeal\s+from\b|^Petition\s+for\b|"
                          r"^Direct\s+Appeal\b", re.I)
_HONORABLE = re.compile(r"^(?:The\s+)?Honorable\b", re.I)
_PRESIDING = re.compile(r"\bJudge[,\s].*presiding\.?$", re.I)
# PARTY STATUS is a finite role vocabulary; a party NAME is never read by
# wording. Illinois compounds the trial and appellate roles with a hyphen.
_ROLES = frozenset((
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "movant", "movants", "claimant",
    "claimants", "counterplaintiff", "counterplaintiffs",
    "counterdefendant", "counterdefendants", "crossappellant",
    "crossappellants", "crossappellee", "crossappellees"))
_ROLE_MODS = frozenset(("cross", "counter", "third", "party", "and"))
_RECUSED = "took no part"
# THE COURT MARKS A NAME. The Fifth District hangs a footnote on the author
# and on a concurring justice ('JUSTICE CLARKE∗ delivered …', 'Justices
# Hackett∗ and Clarke∗∗ concurred …') to explain a substitution on the
# panel. The marks are apparatus on a NAME, so they come off before the name
# is read — left on, they defeat core's byline grammar and put 'Clarke∗∗' on
# the roster.
_MARKS = "*∗†‡§¶"
# A NAME MAY BE INITIALS. 'Justice D.B. Walker' ends its first token in a
# period, and a run that closes on any terminal period reads the surname as
# 'D.B' and drops 'Walker'.
_INITIALS = re.compile(r"^(?:[A-Z]\.)+$")


def _unmark(text: str) -> str:
    """``text`` with the court's footnote marks stripped."""
    return "".join(ch for ch in text if ch not in _MARKS)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the piece and the visual row
# --------------------------------------------------------------------------

class _Row:
    """One row of the reader's own making: the pieces it groups together.

    In the head band a row is ONE piece (two baseline grids collide there);
    in the caption a row is every piece on one baseline (the two cells and
    the rail between them)."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda p: p.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)

    @property
    def text(self) -> str:
        return _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _pieces(model, finder, body_size: float) -> tuple:
    """(on-grid pieces, off-grid pieces) over the pages the block may span,
    in the page's own order, furniture removed."""
    on: list = []
    off: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            (on if abs((line.size or 0.0) - body_size) <= _SIZE_TOL
             else off).append(line)
    return on, off


def _bench_lead(text: str) -> bool:
    """Does this row open the court's announcement? The test is the BENCH
    TITLE it opens on — a closed role vocabulary — and not a byline parse:
    people_v._lee sets a footnote mark on the author's name ('JUSTICE
    CLARKE∗ delivered …') and core's grammar returns None for it."""
    toks = _norm(text).split()
    for title in _BENCH:
        want = title.upper().split()
        got = [w.strip(",.:;" + _MARKS).upper() for w in toks[:len(want)]]
        if got == want:
            return True
    return False


def _split_at_bench(pieces: list) -> tuple:
    """(the block's pieces, the announcement's pieces). The announcement is
    the writing's; the reader reads it and leaves it."""
    for i, line in enumerate(pieces):
        if _bench_lead(line.plain):
            return pieces[:i], pieces[i:]
    return pieces, []


def _rows(pieces: list, group: bool) -> list:
    """Pieces as rows — one per piece, or grouped by baseline."""
    if not group:
        return [_Row([p]) for p in pieces]
    out: list = []
    cur: list = []
    for p in sorted(pieces, key=lambda l: (l.page, l.top, l.x0)):
        if cur and cur[0].page == p.page \
                and abs(cur[0].top - p.top) <= _BASELINE_TOL:
            cur.append(p)
        else:
            if cur:
                out.append(_Row(cur))
            cur = [p]
    if cur:
        out.append(_Row(cur))
    return out


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _rail(pieces: list) -> dict | None:
    """The brace rail over ``pieces``: {'x', 'n'}, or None.

    A rail is a COLUMN of ')' at one x. It is measured over the block's own
    pieces — never over the page — because page 1 carries body prose below
    the announcement and its statutory citations close with the same
    glyph."""
    glyphs = [c for p in pieces for c in p.chars
              if (c.get("text") or "") == _RAIL_GLYPH]
    if len(glyphs) < _RAIL_FLOOR:
        return None
    counts: dict = {}
    for c in glyphs:
        counts[round(c["x0"])] = counts.get(round(c["x0"]), 0) + 1
    x = max(counts, key=lambda k: (counts[k], -k))
    stack = [c for c in glyphs if abs(c["x0"] - x) < _RAIL_TOL]
    if len(stack) < _RAIL_FLOOR:
        return None
    return {"x": float(x), "n": len(stack)}


def _ladder(page) -> list:
    """The Second District's fence tops, or []. Three drawn rules in one
    invariant measure, centred on the page axis."""
    tops = sorted(r.top for r in page.h_rules
                  if _LADDER_MEASURE[0] <= r.x1 - r.x0 <= _LADDER_MEASURE[1]
                  and abs((r.x0 + r.x1) / 2 - page.width / 2) <= _LADDER_AXIS)
    return tops if len(tops) >= _LADDER_FLOOR else []


def _fences(model, pages: set, lo: float, hi: float, end) -> list:
    """(page, top) for every drawn rule the court uses as a fence inside the
    claimed band and OUTSIDE the caption's own vertical extent — a rule that
    crosses the caption divides two consolidated captions and has no place
    in a two-column block."""
    out: list = []
    for pm in model.pages:
        if pm.number not in pages:
            continue
        for r in pm.h_rules:
            if r.x1 - r.x0 < _FENCE_MIN:
                continue
            if (pm.number, r.top) >= end:
                continue              # below the reader's end: the writing's
            if pm.number == 1 and lo <= r.top <= hi:
                continue
            out.append((pm.number, r.top))
    return out


# --------------------------------------------------------------------------
# the head band's shapes
# --------------------------------------------------------------------------

def _cite(text: str) -> dict | None:
    mm = _CITE.match(_norm(text))
    if not mm:
        return None
    tail = mm.group(3)
    parts = re.split(r"[‐-―-]", tail)
    suffix = parts[-1].lower() if len(parts) > 1 else ""
    return {"text": _norm(text), "district": int(mm.group(2)),
            "unpublished": suffix == _UNPUB_SUFFIX}


def _dockets(text: str, lead=_DOCKET_LEAD) -> list:
    """The appeals a 'No(s).' row names, in order, or []."""
    mm = lead.match(_norm(text))
    if not mm:
        return []
    rest = _CONS.sub("", mm.group(1).strip().rstrip(".")).strip()
    rest = re.sub(r"\band\b", ",", rest, flags=re.I)
    out = [p.strip().rstrip(".") for p in rest.split(",") if p.strip()]
    return out if out and all(_DOCKET_NUM.match(p) for p in out) else []


def _dated(text: str) -> tuple:
    """(lead, date) for a release row, or (None, None). A row may carry the
    leader alone; the date then stands on the row beneath it."""
    flat = _norm(text).rstrip(".")
    low = flat.lower()
    lead = next((d for d in _DATE_LEADS if low.startswith(d)), None)
    rest = flat[len(lead):].strip(": ") if lead else flat
    mm = _DATE.search(rest)
    if mm and _norm(rest) == _norm(mm.group(0)):
        return lead, _norm(mm.group(0))
    if lead and not rest:
        return lead, None
    return (None, None)


# --------------------------------------------------------------------------
# the caption's grammar
# --------------------------------------------------------------------------

def _outer(text: str) -> str:
    """The caption without a trailing top-level parenthetical — Illinois
    prints the appealing party's own sub-caption inside one ('In re A.B., a
    Minor, (The People … v. G.J., Respondent-Appellant).')."""
    flat = _norm(text).rstrip(".")
    if not flat.endswith(")"):
        return flat
    depth = 0
    for i in range(len(flat) - 1, -1, -1):
        if flat[i] == ")":
            depth += 1
        elif flat[i] == "(":
            depth -= 1
            if depth == 0:
                return flat[:i].strip().rstrip(",") or flat
    return flat


def _is_role(tag: str) -> bool:
    """Is this comma-separated segment a party STATUS label and nothing
    else? Illinois compounds the trial and appellate roles with a hyphen
    ('Plaintiff and Counterdefendant-Appellee'), and a caption that wraps
    inside the compound breaks it across two rows, so the segment is read as
    a set of role words rather than enumerated whole."""
    parts = [p for p in re.split(r"[-‐-―\s]+", tag.strip()) if p]
    return bool(parts) and all(p in _ROLES or p in _ROLE_MODS for p in parts)


def _strip_role(side: str) -> str:
    """A party name with its STATUS labels taken off — from anywhere in the
    run, not only its tail: an 'In re MARRIAGE OF X, Petitioner-Appellant,
    and Y, Respondent-Appellee.' caption carries one in the middle."""
    segs = [seg.strip() for seg in _norm(side).split(",")]
    keep = [seg for seg in segs
            if seg and not _is_role(seg.strip(".,").lower())
            and seg.strip(".,").lower() != "et al"]
    out = ""
    for seg in keep:
        if not out:
            out = seg
        elif seg.lower().startswith("and ") or out.endswith(" and"):
            out = f"{out} {seg}"
        else:
            out = f"{out}, {seg}"
    return out.strip().strip(".,").strip()


def _sides(text: str) -> tuple | None:
    """The party names either side of the caption's pivot. The pivot is a
    free-standing 'v.', so an abbreviation inside a name cannot be it."""
    parts = re.split(r"(?<=[\s\w.,;)’])\s+v\.?\s+", text, maxsplit=1)
    if len(parts) != 2:
        return None
    left, right = _strip_role(parts[0]), _strip_role(parts[1])
    return (left, right) if left and right else None


def _origin(rows: list) -> dict:
    """The origin column read as the court below: where the case came from,
    what number it carried there, and who tried it.

    Three closed leads do the work — an appeal-from clause opens the origin,
    'No.'/'Circuit No.' opens the trial number, 'Honorable' opens the judge
    and a 'Judge, presiding.' clause closes him. 'Appeal No.' is the number
    of THIS appeal, which the Third District prints here and nowhere else.
    """
    out = {"court": [], "docket": [], "judge": [], "appeal": []}
    state = "court"
    for text in rows:
        flat = _norm(text)
        if not flat:
            continue
        appeal = _dockets(flat, _APPEAL_NO_LEAD)
        if appeal:
            out["appeal"].extend(appeal)
            state = "docket"
            continue
        if _HONORABLE.match(flat) or _PRESIDING.search(flat) \
                or (state == "judge"
                                      and not _DOCKET_LEAD.match(flat)):
            out["judge"].append(flat)
            state = "closed" if _PRESIDING.search(flat) else "judge"
            continue
        if _DOCKET_LEAD.match(flat) or re.match(r"^Circuit\s+NOS?\.", flat,
                                                re.I):
            out["docket"].append(flat)
            state = "docket"
            continue
        if state == "court":
            out["court"].append(flat)
            continue
        if state == "docket":
            # a wrapped trial number ('Nos. 23JA427' / ' 23JA428')
            out["docket"].append(flat)
    return out


# --------------------------------------------------------------------------
# the announcement — read, never claimed
# --------------------------------------------------------------------------

def _bench_names(text: str) -> list:
    """Every judicial surname an announcement names, in order.

    'Presiding Justice Cates and Justice Vaughan concurred in the judgment
    and opinion.' -> two names. A run opens on a BENCH TITLE and closes on
    the statement's verb — the first lower-case word that is not a
    connector — or on the NEXT bench title, which the outer scan then picks
    up (without that, 'and Justice Vaughan' rides along inside the first
    run and the roster gains a justice called 'Justice Vaughan')."""
    names: list = []
    toks = _norm(text).split()
    titles = {t.upper() for t in _BENCH}
    i = 0
    while i < len(toks):
        title = None
        for t in _BENCH:
            n = len(t.split())
            got = [w.strip(",.:;" + _MARKS).upper() for w in toks[i:i + n]]
            if got == t.upper().split():
                title, i = t, i + n
                break
        if title is None:
            i += 1
            continue
        run: list = []
        while i < len(toks):
            tok = toks[i]
            bare = tok.strip(",.:;" + _MARKS)
            if bare.upper() in titles or " ".join(
                    w.strip(",.:;").upper() for w in toks[i:i + 2]) in titles:
                break
            if bare.lower() == "and":
                run.append(tok)
                i += 1
                continue
            if not bare or not bare[:1].isupper():
                break
            run.append(tok)
            i += 1
            if tok.endswith((".", ":", ";")) \
                    and not _INITIALS.match(bare + "."):
                break
        for part in re.split(r",|\band\b", " ".join(run)):
            nm = _unmark(part).strip().strip(".,:;").strip()
            if nm and nm[:1].isupper():
                names.append(nm)
    return names


def _read_announcement(rows: list, parser) -> tuple:
    """(author, panel_line, panel) from the court's own statements.

    The rows are NOT claimed: they belong to the writing, and nothing is
    ever taken out of an assembled writing. The run ends at the bold
    'OPINION' / 'ORDER' heading or at the first numbered paragraph."""
    stmts: list = []
    for row in rows:
        if row.bold or row.text.startswith("¶"):
            break
        if _TYPED_RULE.match(row.text.replace(" ", "")):
            break                         # the Third District's foot fence
        if stmts and _bench_lead(row.text):
            stmts.append([row])
        elif stmts:
            stmts[-1].append(row)         # a wrapped statement
        else:
            stmts.append([row])
    if not stmts:
        return None, None, []
    texts = [_norm(" ".join(r.text for r in s)) for s in stmts]
    panel: list = []
    for text in texts:
        if _RECUSED in text.lower():
            continue
        for nm in _bench_names(text):
            if nm not in panel:
                panel.append(nm)
    author = None
    lead = parser.parse(_unmark(texts[0]))
    if lead is not None:
        author = f"{lead.title} {lead.name}".strip()
    elif panel:
        author = panel[0]
    return author, (" ".join(texts[1:]) or None), panel


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, geom=None, width: float = 612.0):
        self.geom = (geom, width)
        self.items: list = []
        # WHERE EACH ITEM CAME FROM, parallel to `items`. A drawn rule owns
        # no line of its own, and the pipeline merges a court's items with
        # core's leftovers BY LINE ID — an id-less item goes to the foot of
        # the block. So a fence is provenanced by the row it closes, which
        # is where the page draws it, and the tie holds this order.
        self.pos: list = []
        self.dropped: list = []
        self.consumed: set = set()
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align=None) -> None:
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=align if align is not None else _align(row, self.geom),
            x0=row.x0, size=row.size, bold=row.bold, role=role))
        self.pos.append((row.page, row.top))
        self.consumed.update(row.ids)

    def cell(self, parts: list, role: str) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock."""
        self.consumed.update(p.id for p in parts)
        text = ""
        for p in sorted(parts, key=lambda l: l.x0):
            piece = line_markup(p)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(text=text, prov=m.Prov(parts[0].page,
                                               tuple(p.id for p in parts)),
                        align=m.Align.LEFT, x0=parts[0].x0,
                        size=parts[0].size or 0.0, role=role)

    def typed_rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids), typed=True))
        self.pos.append((row.page, row.top))
        self.consumed.update(row.ids)

    def block(self, item, page: int, top: float) -> None:
        self.items.append(item)
        self.pos.append((page, top))

    def fence(self, page: int, top: float) -> None:
        """A DRAWN rule, placed after the last item above it and given that
        item's provenance."""
        at = 0
        prov = m.Prov(page)
        for i, where in enumerate(self.pos):
            if where <= (page, top):
                at = i + 1
                item = self.items[i]
                if getattr(item, "prov", None) is not None:
                    prov = item.prov
        self.items.insert(at, m.Rule(prov=prov))
        self.pos.insert(at, (page, top))

    def drop(self, parts: list, kind: str) -> None:
        parts = sorted(parts, key=lambda p: (p.top, p.x0))
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="illappct")
def read_headmatter_illappct(model, geom, **_):
    """Read one of illappct's two papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    on, off = _pieces(model, finder, body_size)
    if not on:
        return NOTHING
    block, tail = _split_at_bench(on)
    if not tail or not block:
        return NOTHING                    # no announcement: not this paper

    rail = _rail(block)
    ladder = _ladder(page1)
    if rail is not None:
        style, zones = STYLE_BRACED, None
    elif ladder:
        style, zones = STYLE_LADDER, ladder
    else:
        return NOTHING                    # neither contract: core's walk

    ctx = _Ctx(geom, page1.width)
    parser = BylineParser(ILLAPPCT.byline)
    pages = {p.page for p in block}
    end = (tail[0].page, tail[0].top)     # the reader's end, page and top
    # THE MARGINAL GRID. Off-size pieces above the reader's end are the
    # clerk's stamp / the advisory — recorded, never read. They are
    # clustered by COLUMN so each marginal block reads as one entry and the
    # two the Fifth District sets, one at each margin, stay apart.
    for run in _stamp_runs(off, tail):
        ctx.drop(run, "stamp")
    stamped = _stamp_date(model, body_size, tail[0])

    if style == STYLE_BRACED:
        ok = _read_braced(ctx, model, block, rail, pages, end)
    else:
        ok = _read_ladder(ctx, model, block, zones, pages, end)
    if not ok:
        return NOTHING

    # THE CRITERIA ARE BUILT BEFORE THEY ARE GATED (wyo shipped its docket
    # gate one line above the call that populates it and refused all 50 of
    # its own correctly-read records).
    ctx.crit["headmatter_style"] = style
    # THE FOURTH AND FIFTH DISTRICTS DATE ONLY THE STAMP. The clerk's stamp
    # ('FILED / August 11, 2026 / Carla Bender / 4th District Appellate /
    # Court, IL') and the Fifth District's advisory ('Decision filed
    # 08/11/26.') carry the release date and the head band carries none. The
    # stamp is still `Dropped` — it is READ, not claimed, exactly as the
    # announcement below the block is.
    if stamped and "decision_date" not in ctx.crit:
        ctx.crit["decision_date"] = stamped
    author, line, panel = _read_announcement(_rows(tail, False), parser)
    if author:
        ctx.crit["judges"] = author
    if line:
        ctx.crit["panel_line"] = line
    if panel:
        ctx.crit["panel"] = panel
    if not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result()


def _stamp_runs(off: list, tail: list) -> list:
    """The off-grid pieces above the reader's end, grouped into the blocks
    the page laid them out as.

    The bound is the announcement's own position, page AND top: a caption
    that runs to page 4 puts the announcement there, and an off-size line
    BELOW it is the writing's footnote, not the clerk's stamp."""
    end = (tail[0].page, tail[0].top)
    keep = [p for p in off if (p.page, p.top) < end]
    # THE MARGINAL BLOCKS ARE COLUMNS. The Fifth District sets two
    # advisories, one at each margin; the Fourth sets one stamp whose rows
    # differ in x0 by 45pt. Clustering on a gap wider than any one block
    # keeps each block whole and never merges two.
    out: list = []
    for page in sorted({p.page for p in keep}):
        rows = sorted((p for p in keep if p.page == page),
                      key=lambda p: p.x0)
        cluster: list = []
        for p in rows:
            if cluster and p.x0 - cluster[-1].x0 > _STAMP_GAP:
                out.append(sorted(cluster, key=lambda q: q.top))
                cluster = []
            cluster.append(p)
        if cluster:
            out.append(sorted(cluster, key=lambda q: q.top))
    return out


def _stamp_date(model, body_size: float, stop) -> str | None:
    """The release date the marginal block carries, or None.

    READ, NOT CLAIMED — and read off the page rather than off what this
    reader dropped, because core's own furniture sweep takes most of these
    lines first and a line only has to be accounted for ONCE. The Fourth
    District sets the date long ('FILED / August 11, 2026'); the Fifth sets
    it short ('Decision filed 08/11/26.'), written out here so the field
    reads the same on every record of the court.
    """
    lines = [l for pm in model.pages[:1] for l in pm.lines
             if l.plain.strip()
             and abs((l.size or 0.0) - body_size) > _SIZE_TOL
             and (l.page, l.top) < (stop.page, stop.top)]
    for line in lines:
        mm = _DATE.search(_norm(line.plain))
        if mm:
            return _norm(mm.group(0))
    for line in lines:
        mm = _SHORT_DATE.search(_norm(line.plain))
        if mm:
            mo, day, yr = (int(x) for x in mm.groups())
            if 1 <= mo <= 12:
                return f"{_MONTH_NAMES[mo - 1]} {day}, {2000 + yr}"
    return None


# ---- the head band -------------------------------------------------------

def _read_head(ctx: _Ctx, rows: list) -> bool:
    """The identifiers and the masthead, each row read by its own shape.

    Returns False when a row is a shape this court does not print — a
    confident misreading is worse than core's shared walk."""
    cite = None
    dockets: list = []
    dates: list = []
    mast: list = []
    notice: list = []
    i = 0
    while i < len(rows):
        row = rows[i]
        flat = row.text
        low = flat.lower()
        if notice:
            notice.append(row)
            if flat.endswith("."):
                ctx.drop([p for r in notice for p in r.pieces], "notice")
                notice = []
            i += 1
            continue
        if _TYPED_RULE.match(flat.replace(" ", "")):
            ctx.typed_rule(row)
            i += 1
            continue
        if low.startswith(_NOTICE_CUE):
            notice = [row]
            if flat.endswith("."):
                ctx.drop(row.pieces, "notice")
                notice = []
            i += 1
            continue
        got = _cite(flat)
        if got is not None:
            cite = got
            ctx.emit(row, "citation")
            i += 1
            continue
        found = _dockets(flat)
        if found:
            dockets.extend(found)
            ctx.emit(row, "docket")
            i += 1
            continue
        lead, when = _dated(flat)
        if lead is not None or when is not None:
            if lead and when is None and i + 1 < len(rows):
                nxt = rows[i + 1]
                _l2, w2 = _dated(nxt.text)
                if _l2 is None and w2:
                    dates.append((lead, w2))
                    ctx.emit(row, "date")
                    ctx.emit(nxt, "date")
                    i += 2
                    continue
            dates.append((lead, when))
            ctx.emit(row, "date")
            i += 1
            continue
        if _DIVISION.match(flat):
            mast.append(row)
            ctx.emit(row, "court")
            i += 1
            continue
        if _MASTHEAD_KEY in flat.upper() or flat.upper() == _MASTHEAD_LEAD:
            mast.append(row)
            ctx.emit(row, "court")
            i += 1
            continue
        if mast and _MASTHEAD_TAIL.match(flat):
            mast.append(row)
            ctx.emit(row, "court")
            i += 1
            continue
        if low.strip(".") in _FLAGS:
            ctx.emit(row, "publication")
            i += 1
            continue
        return False
    if notice:
        ctx.drop([p for r in notice for p in r.pieces], "notice")
    if cite is None:
        return False
    ctx.crit["citation"] = cite["text"]
    ctx.crit["publication_status"] = ("unpublished" if cite["unpublished"]
                                      else "published")
    if dockets:
        ctx.crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            ctx.crit["other_dockets"] = dockets[1:]
    for lead, when in dates:
        if when is None:
            continue
        if lead == _MOTION_LEAD:
            ctx.crit["motion"] = f"{lead.capitalize()} {when}"
        elif "decision_date" not in ctx.crit:
            ctx.crit["decision_date"] = when
    # THE COURT NAMES ITSELF in the masthead; the division/district rows are
    # the same act. The printed rows stay where the page put them and the
    # parsed name is kept beside them.
    # A BARE YEAR in the masthead is the TERM the court sits in, not part of
    # its name; the DIVISION is, and it is printed in the top band where the
    # masthead cannot reach it. Two records print no masthead at all, and
    # then the court's name is the one fact the profile already declares.
    named = [r.text for r in mast
             if (_MASTHEAD_KEY in r.text.upper()
                 or r.text.upper() == _MASTHEAD_LEAD
                 or (_MASTHEAD_TAIL.match(r.text) and not r.text.isdigit()))
             and not r.text.upper().endswith("DIVISION")]
    div = [r.text for r in mast if r.text.upper().endswith("DIVISION")]
    court = _norm(" ".join(named))
    if court.upper().startswith(_MASTHEAD_LEAD + " "):
        court = court[len(_MASTHEAD_LEAD) + 1:]
    if not any(_MASTHEAD_KEY in n.upper() for n in named):
        court = ", ".join(x for x in (ILLAPPCT.court_label, court) if x)
    ctx.crit["court"] = ", ".join(x for x in ([court] + div) if x) \
        or ILLAPPCT.court_label
    return True


# ---- the braced cover ----------------------------------------------------

def _read_braced(ctx: _Ctx, model, block: list, rail: dict,
                 pages: set, end) -> bool:
    """The rail decides everything: the caption opens at the first piece
    that carries a rail glyph and closes at the announcement."""
    # THE CAPTION OPENS at the first baseline the rail governs — one that
    # carries a rail glyph, or one whose content STRADDLES the column. The
    # Third District sets the caption's first row without a brace
    # ('CITY OF WHEATON,' beside 'Appeal from the Circuit Court', the rail
    # starting on the row beneath), so a glyph-only test leaves the party
    # row above the caption and the head band cannot account for it.
    first = None
    for row in _rows(block, True):
        if _governed(row, rail):
            first = (row.page, row.top)
            break
    if first is None:
        return False
    head = [p for p in block if (p.page, p.top) < first]
    body = [p for p in block if (p.page, p.top) >= first]
    if not _read_head(ctx, _rows(head, False)):
        return False
    # A TYPED RULE inside the caption band closes it; the Third and Fifth
    # Districts fence the caption top and bottom with underscores.
    cap: list = []
    for row in _rows(body, True):
        if _TYPED_RULE.match(row.text.replace(" ", "")):
            ctx.typed_rule(row)
            continue
        cap.append(row)
    if not cap:
        return False
    left, right, l_plain, r_plain, ids = _split_rail(ctx, cap, rail)
    if not left:
        return False
    ctx.block(m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH,
        rail_rows=max(len(left), len(right), 1),
        style_id="brace-rail",
        fp={"rail": _RAIL_GLYPH, "rail_x": rail["x"], "rail_n": rail["n"]},
        prov=m.Prov(cap[0].page, tuple(sorted(ids)))),
        cap[0].page, cap[0].top)
    _read_fences(ctx, model, pages, cap, end)
    _caption_criteria(ctx, l_plain, r_plain)
    return True


def _align(row: _Row, geom_width) -> m.Align:
    """The page's own alignment for this row, measured on its INK.

    A piece the court pads with spaces reports an x0 that is not where its
    text starts — the Fifth District's 'IN THE' arrives as nineteen blanks
    and six letters, and read on the piece's own extent a row centred on the
    page axis to a tenth of a point reads flush left.
    """
    geom, width = geom_width
    piece = row.pieces[0]
    inked = [c for c in piece.chars if (c.get("text") or "").strip()]
    if len(row.pieces) > 1 or not inked:
        return m.Align.LEFT
    if len(inked) != len(piece.chars):
        piece = _replace(piece, chars=inked,
                         x0=min(c["x0"] for c in inked),
                         x1=max(c.get("x1", c["x0"]) for c in inked))
    return m.Align(line_alignment(piece, width, geom))


def _governed(row: _Row, rail: dict) -> bool:
    """Is this baseline inside the rail's caption?

    Either it draws the rail, or it sets content on both sides of the
    column WITH THE COLUMN ITSELF CLEAR. The clearance is what tells a
    two-cell row from a centred masthead row long enough to run through the
    rail's x — 'APPELLATE COURT OF ILLINOIS' spans x=214-397 on a record
    whose rail stands at 369, and a bare both-sides test read it as the
    caption's first row on every First District cover."""
    left = right = False
    clear = True
    for p in row.pieces:
        for c in p.chars:
            t = c.get("text") or ""
            if not t.strip():
                continue
            if t == _RAIL_GLYPH and abs(c["x0"] - rail["x"]) < _RAIL_TOL:
                return True
            x1 = c.get("x1", c["x0"])
            if x1 <= rail["x"] - _RAIL_GUTTER:
                left = True
            elif c["x0"] >= rail["x"] + _RAIL_WIDTH:
                right = True
            else:
                clear = False
    return left and right and clear


def _split_rail(ctx: _Ctx, cap: list, rail: dict) -> tuple:
    """The caption's two stacks, split glyph by glyph at the measured column
    with the rail's own glyphs shed.

    THE TWO STACKS ARE NOT ROW-PAIRED, and this is the one place illappct
    parts company with ca6. ca6's columns are paired data — a docket
    answering to the party row beside it. Here the right column is one
    independent block (origin, trial number, trial judge) set beside a party
    list of any length, and where it starts vertically is a layout choice
    and not a correspondence: pepper_construction's 155 party rows would
    pair with 145 blank cells, and marchi and reyes set the two columns on
    DIFFERENT baseline grids altogether, so there is nothing to pair with.
    Each column is therefore collected on its own and the renderer flows
    them side by side, which is how the court sets them.
    """
    left: list = []
    right: list = []
    l_plain: list = []
    r_plain: list = []
    ids: list = []
    for row in cap:
        l_parts: list = []
        r_parts: list = []
        for p in row.pieces:
            ids.append(p.id)
            for want, bucket in (("L", l_parts), ("R", r_parts)):
                side = _side(p, rail, want)
                if side is not None:
                    bucket.append(side)
        ctx.consumed.update(p.id for p in row.pieces)
        for parts, stack, plains, role in (
                (l_parts, left, l_plain, "caption"),
                (r_parts, right, r_plain, "lower-court")):
            flat = _norm(" ".join(p.plain for p in parts))
            # A CELL THAT IS ONLY RAIL IS NOT A CELL. The court's rail
            # wobbles a few points off its own column on a long caption
            # (pepper_construction types one brace 3.2pt right of the other
            # 150), so a glyph outside the shed window lands in a cell with
            # nothing else in it and renders as a lone ')' in the origin.
            # Read as text it carries nothing, so it is emitted as nothing —
            # its ids are consumed either way.
            if not flat.strip(_RAIL_GLYPH + " "):
                continue
            stack.append(ctx.cell(parts, role))
            plains.append(flat)
    return left, right, l_plain, r_plain, ids


def _side(line, rail: dict, want: str):
    """The part of ``line`` on one side of the rail, the rail's own glyphs
    shed. Membership is a glyph's x0 against the measured column — never a
    whole-piece test: the court sets cell, rail and cell as three pieces
    when the gaps are wide and as one piece when they are not."""
    keep = []
    for c in line.chars:
        t = c.get("text") or ""
        if t == _RAIL_GLYPH and abs(c["x0"] - rail["x"]) < _RAIL_TOL:
            continue
        if (c["x0"] < rail["x"]) == (want == "L"):
            keep.append(c)
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


# ---- the Second District's ruled ladder ---------------------------------

def _read_ladder(ctx: _Ctx, model, block: list, tops: list,
                 pages: set, end) -> bool:
    """The three rules ARE the parser: identifiers, masthead, caption."""
    head = [p for p in block if p.page == 1 and p.top < tops[1]]
    cap = [p for p in block if p.page == 1 and tops[1] < p.top
           and (len(tops) < 3 or p.top < tops[2])]
    if not head or not cap:
        return False
    if len(block) != len(head) + len(cap):
        return False                      # something outside every zone
    if not _read_head(ctx, _rows(head, False)):
        return False
    # THE CAPTION IS CENTRED and one column, so the origin is read off the
    # rows themselves: the parties above, the court below beneath them,
    # divided by the appeal-from clause that opens the origin.
    rows = _rows(cap, True)
    cut = next((i for i, r in enumerate(rows)
                if _ORIGIN_LEAD.match(r.text)), len(rows))
    parties = rows[:cut]
    origin = rows[cut:]
    if not parties:
        return False
    for row in parties:
        ctx.emit(row, "caption")
    for row in origin:
        ctx.emit(row, "lower-court")
    _read_fences(ctx, model, pages, rows, end)
    _caption_criteria(ctx, [r.text for r in parties],
                      [r.text for r in origin])
    return True


# ---- what the caption says ----------------------------------------------

def _read_fences(ctx: _Ctx, model, pages: set, cap: list, end) -> None:
    lo = min(r.top for r in cap if r.page == 1) if any(
        r.page == 1 for r in cap) else 0.0
    hi = max(r.top for r in cap if r.page == 1) if any(
        r.page == 1 for r in cap) else 0.0
    for page, top in _fences(model, pages, lo, hi, end):
        ctx.fence(page, top)


def _caption_criteria(ctx: _Ctx, left: list, right: list) -> None:
    rows = [r for r in left if r]
    ctx.crit["caption"] = rows
    flat = _norm(" ".join(rows))
    sides = _sides(_outer(flat))
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    elif flat:
        # 'In re MARRIAGE OF …' — a caption with no pivot is ONE party, and
        # inventing a second from the conjunction names a respondent the
        # page does not.
        ctx.crit["parties"] = [_strip_role(_outer(flat))]
        ctx.crit["case_name"] = _strip_role(_outer(flat))
    origin = _origin([r for r in right if r])
    if origin["court"]:
        ctx.crit["lower_court"] = _norm(" ".join(origin["court"]))
    if origin["docket"]:
        ctx.crit["lower_court_docket"] = [_norm(d) for d in origin["docket"]]
    if origin["judge"]:
        ctx.crit["lower_court_judge"] = _norm(" ".join(origin["judge"]))
    # THE THIRD DISTRICT prints the appeal's own number in the origin column
    # ('Appeal No. 3-25-0429') and nowhere else, so the docket may only be
    # known once the caption has been read.
    if origin["appeal"] and not ctx.crit.get("docket_number"):
        ctx.crit["docket_number"] = origin["appeal"][0]
        if len(origin["appeal"]) > 1:
            ctx.crit["other_dockets"] = origin["appeal"][1:]
