"""THE headmatter reader — one, replacing the old system's five.

Reads the caption pages into typed HmItems (styled rows + CaptionBlock built
from the same fingerprint the classifier stored) and extracts the Criteria
core fields (docket_number, decision_date, parties — the v1 rollout gate).
Panel/counsel/history readers grow here in later phases, per family, and they
PUBLISH ONCE: there is no second representation to keep in sync.

Field evidence is positional and shape-based (string-prefix cues, no regex):
a docket is a short digit-bearing token row near the banner or in the caption
right column; a decision date is a month-name date on a dated row
('Decided:', 'Filed:', '(Filed: …)', or a bare date line); parties are the
caption's own rows around the 'v.' pivot.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .. import model as m
from ..geometry import DocGeometry, line_alignment
from ..pdfio.model import Line, PageModel
from .evidence import Trace

_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")


def _is_typed_rule_row(text: str) -> bool:
    from ..pdfio.rules import is_typed_rule
    return is_typed_rule(text)

_DOCKET_OPENERS = ("no.", "nos.", "case no.", "docket no.", "case:",
                   "case number:", "docket entry no.")
# Short reporter-style docket prefixes (DA 25-0040, SC 21050, A-1234-23).
_DOCKET_BARE_MAX = 24


def _clean(text: str) -> str:
    return " ".join(text.split())


# 'on the 9th day of June, two thousand twenty-six.' — ca2 spells the year
# out in its convening recital, the ONLY statement of a summary order's
# date. Ported lesson from centralia v1.
_ONES = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
         "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}


def _spelled_year(words: list[str]) -> int | None:
    total = seen = 0
    for word in words:
        w = word.strip(".,").lower()
        if w == "thousand":
            total = (total or 1) * 1000
            seen = 1
        elif w in _ONES:
            total += _ONES[w]
            seen = 1
        elif "-" in w and w.split("-")[0] in _TENS:
            tens, _, ones = w.partition("-")
            total += _TENS[tens] + _ONES.get(ones, 0)
            seen = 1
        elif w in _TENS:
            total += _TENS[w]
            seen = 1
    return total if seen and total >= 1000 else None


def recital_date(text: str) -> str | None:
    """'June 10, 2026' out of a convening recital ('…on the 10th day of
    June, two thousand twenty-six.'), or None."""
    tokens = text.replace(",", " ").split()
    for i, token in enumerate(tokens):
        if token.lower() != "day" or i + 2 >= len(tokens):
            continue
        if tokens[i + 1].lower() != "of":
            continue
        month = tokens[i + 2].strip(".,")
        day = ""
        for back in range(i - 1, -1, -1):
            digits = "".join(c for c in tokens[back] if c.isdigit())
            if digits:
                day = digits
                break
        year = _spelled_year(tokens[i + 3:])
        if month and day and year:
            return f"{month} {day}, {year}"
    return None


def find_date(text: str) -> str | None:
    """A month-name date inside ``text`` ('March 31, 2026'), or a numeric
    date ('03/31/2026'). Returned as printed."""
    t = _clean(text)
    low = t.lower()
    for month in _MONTHS:
        i = low.find(month)
        while i != -1:
            # month must start a word
            if i == 0 or not low[i - 1].isalpha():
                rest = t[i:]
                words = rest.replace(",", ", ").split()
                if len(words) >= 2:
                    take = []
                    for w in words[:3]:
                        take.append(w)
                        # a footnote MARK may ride the year ('2026*' — conn
                        # stars its released date); a BRACKET closes it
                        # ('[June 11, 2026]' — scotus sets its decision date
                        # in brackets); and an em dash may weld the next
                        # word to it ('2026—Decided', the scotus cover's
                        # argued-and-decided row), which hides the FIRST
                        # date of the row behind the second.
                        core = w.rstrip(",.;)]*†‡")
                        if not (core.isdigit() and len(core) == 4):
                            core = core.split("—")[0].split("–")[0]
                            if core.isdigit() and len(core) == 4:
                                take[-1] = core
                        if len(take) >= 2 and core.isdigit() \
                                and len(core) == 4:
                            return _clean(" ".join(take)).rstrip(".,;)]*†‡")
            i = low.find(month, i + 1)
    for tok in t.replace(")", " ").split():
        parts = tok.split("/")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            return tok
    return None


def looks_like_docket(text: str) -> str | None:
    """The docket number as printed, or None. Anchored openers ('No. 24-1770',
    'Case No. 3:20-cv-00187-SLG'), a short bare digit-hyphen token row
    ('DA 25-0040', '24-1770'), or the same in parens ('(SC 21050)')."""
    t = _clean(text)
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1].strip()
    # A caption cell may carry its RAIL glyph (': No. 1422 MDA 2025' —
    # pa's colon rail welds onto the cell).
    t = t.lstrip(":│┃| ").strip()
    # 'J-S18042-26' is pa/pasuperct's SESSION calendar number, printed in
    # the corner of every page — never the docket ('No. 1422 MDA 2025').
    if re.match(r"^J-[A-Z]{0,2}\d", t):
        return None
    low = t.lower()
    # A DATE ROW is never a docket ('FILED: JULY 31 2026' — all-caps
    # tokens with a digit tail pass the bare shape otherwise).
    if low.startswith(("filed", "decided", "argued", "entered",
                       "submitted", "dated")):
        return None
    for opener in _DOCKET_OPENERS:
        if low.startswith(opener):
            value = t[len(opener):].strip(" :")
            if any(c.isdigit() for c in value):
                # The row may run on into dates ('No. 25–332. Argued
                # December 8, 2025—Decided June 29, 2026' — scotus):
                # the docket ends where the apparatus begins.
                return re.split(r"\s+(?:Argued|Decided|Filed|Submitted)\b|—",
                                t)[0].rstrip(". ")
    if len(t) <= _DOCKET_BARE_MAX and any(c.isdigit() for c in t):
        # 'SPECIAL TERM, 2025' names the term (ala), never the docket —
        # nor does a bare month-year row ('MARCH, 2026' — conn).
        if re.search(r"\bterm\b", low):
            return None
        if any(tok.strip(".,").lower() in _MONTHS for tok in t.split()):
            return None
        toks = t.split()
        if not toks:
            return None
        core = toks[-1]
        digits = sum(c.isdigit() for c in core)
        if digits >= 4 and ("-" in core or core.isdigit()
                            # compact letter-prefixed form ('C102382' —
                            # calctapp)
                            or re.fullmatch(r"[A-Z]{1,2}\d{5,}", core)) \
                and all(tok.isupper() or any(c.isdigit() for c in tok)
                        for tok in toks):
            return t
    return None


# A judicial-title token, the evidence that a row is a BENCH ROSTER
# ('STANFILL, C.J., and MEAD…, JJ.' / 'Before Elrod, Chief Judge…').
_ROSTER_TITLE = re.compile(
    r"(?:C\.?\s?J\.?|J\.?J\.?|P\.?\s?J\.?|A\.?\s?R\.?\s?J\.?|J\.|"
    r"Chief\s+(?:Justice|Judge)|Circuit\s+Judges?|District\s+Judges?|"
    r"Justices?|Judges?)(?=[\s,.:]|$)")

_DATE_LABELS = frozenset({"argued", "decided", "submitted", "filed",
                          "heard", "reargued", "decision", "entered"})

_DATE_ROW_OPENERS = ("decided", "filed", "(filed", "dated", "opinion filed",
                     "decided and filed", "entered", "notice: this opinion",
                     "opinion issued", "issued")


def roster_names(roster: str) -> list[str]:
    """The judges a roster line names, one per entry.

    The roster is one printed string and the panel is a list, and both are
    facts: 'STANFILL, C.J., and MEAD, CONNORS, LAWRENCE, DOUGLAS, LIPEZ, and
    TAUB, JJ.' is seven judges. Splits on commas and 'and', drops the titles
    ('C.J.', 'JJ.', 'A.R.J.'), and keeps a generational suffix WITH the name
    it belongs to — split naively, 'HORTON, A.R.J.' is fine but 'RUSSELL,
    JR.' becomes a judge called 'Jr.'

    A COURT THAT READS ITS OWN ROSTER USES THIS. Lifted out of
    `read_headmatter` (where it was inline) so a court reader fills
    `criteria.panel` by the same rule core does instead of by a second one:
    me printed a 'Panel:' row on 48 of its 50 records, tinted it correctly,
    and left `panel` and `judges` empty on every one of them."""
    names = [n.removeprefix("and ").strip(" .")
             for n in (p.strip() for p in re.split(r",\s*|\s+and\s+", roster))
             if n and n.removeprefix("and ").strip()
             and not _ROSTER_TITLE.fullmatch(
                 n.removeprefix("and ").strip().rstrip("., "))]
    out: list[str] = []
    for n in names:
        if n.rstrip(".").upper() in ("JR", "SR", "II", "III", "IV") and out:
            out[-1] += ", " + n
        else:
            out.append(n)
    return out


def date_row_value(text: str) -> str | None:
    """The decision date from a dated row. Anchored on the row's opener or a
    bare MONTH-NAME date line ('June 12, 2026' under the caption). 'Submitted'
    /'Argued' rows are argument dates; a bare NUMERIC date is an e-filing
    stamp, never a decision date."""
    t = _clean(text)
    low = t.lower()
    # 'Argued November 5, 2025—officially released March 3, 2026': the
    # RELEASE date is the decision date; the argument date is not.
    if "officially released" in low:
        tail = t[low.index("officially released") + len("officially released"):]
        return find_date(tail)
    # 'Argued December 8, 2025—Decided June 29, 2026' (scotus): the row
    # carries both; the DECIDED date is the decision date.
    if "decided" in low and len(t) < 120:
        d = find_date(t[low.index("decided"):])
        if d:
            return d
    if low.startswith("submitted") or low.startswith("argued"):
        return None
    if "term" in low:
        return None   # 'September Term, 2025' names the term, not a decision
    date = find_date(t)
    if date is None:
        return None
    if any(low.startswith(op) for op in _DATE_ROW_OPENERS):
        return date
    if "/" in date:
        return None
    if low.rstrip(".") == date.lower() and len(date.split()) >= 3:
        # a bare MONTH-YEAR row names conn's term, not a decision day
        return date
    return None


# Rows that END a party side ('Plaintiffs and Appellees,'), never party text.
_STATUS_WORDS = ("plaintiff", "defendant", "appellant", "appellee",
                 "petitioner", "respondent", "intervenor", "movant",
                 "claimant", "cross-appellant", "cross-appellee", "debtor",
                 "amicus", "amici",
                 # A SIDE THE CAPTION NAMES WITHOUT A ROLE WORD. 'Interested
                 # Party.' is apparatus, not a party's name, and unread as
                 # such it welded into the name — ca10's
                 # universitas_education and cafc's nvlsp published
                 # 'Interested Party - Appellant' as a party (the user,
                 # 2026-08-24: 'the other is the interested party is the
                 # same thing its part of caption'). 'Miscellaneous' is the
                 # district form of the same thing (insd).
                 "interested", "miscellaneous")
_PIVOTS = ("v.", "vs.", "v", "vs", "against")
_ORIGIN_OPENERS = ("appeal from", "on appeal from", "appeal by", "on petition",
                   "petition for", "on writ", "certiorari", "on remand",
                   "on rehearing", "original proceeding", "on review")
_COURT_WORDS = ("court", "appeals", "supreme", "district", "circuit",
                "tribunal", "judicial")


def _is_pivot(text: str) -> bool:
    return _clean(text).lower().rstrip(".,") in [p.rstrip(".") for p in _PIVOTS]


def _is_status_row(text: str) -> bool:
    t = _clean(text).lower().rstrip(".,;)")
    if not t or len(t) > 60:
        return False
    core = t.split("-")[-1] if t.startswith(("-", "–")) else t
    words = core.replace("/", " ").replace(",", " ").split()
    hits = sum(1 for w in words for s in _STATUS_WORDS if w.rstrip("s()") .startswith(s))
    return hits >= 1 and hits >= max(1, len(words) - 2)


def _is_banner_row(text: str) -> bool:
    """The court's own masthead — requires a court word, so a party named
    'STATE OF MONTANA' never reads as a banner."""
    t = _clean(text).lower()
    if len(t) >= 70:
        return False
    if (t.startswith(("in the", "united states", "supreme court",
                      "for the", "state of", "commonwealth"))
            and any(w in t for w in _COURT_WORDS)):
        return True
    # A state-name-led masthead ('MAINE SUPREME JUDICIAL COURT') carries
    # TWO court words; a party named 'STATE OF MONTANA' carries none.
    return sum(1 for w in _COURT_WORDS if w in t) >= 2


def _is_origin_row(text: str) -> bool:
    return _clean(text).lower().startswith(_ORIGIN_OPENERS)


def read_parties(rows: list[str], trace: Trace) -> list[str]:
    """Party sides from caption rows, bounded structurally: a side runs from
    the previous boundary to its STATUS row; the 'v.' pivot separates sides;
    banner / docket / citation / origin / date rows never join a party."""
    from ..audit import strip_tags, unescape_xml
    rows = [unescape_xml(strip_tags(r)) for r in rows]
    # A caption row may END on the pivot, the second side setting on the
    # row below ('CISCO SYSTEMS, INC., ET AL., PETITIONERS v.' / 'DOE I,
    # ET AL.' — scotus wraps its caption at the measure): those two rows
    # are one statement, and read apart neither one carries a pivot, so the
    # caption reports no parties at all.
    _rejoined: list[str] = []
    _k = 0
    while _k < len(rows):
        _t = _clean(rows[_k])
        # …only when the row carries a PARTY as well as the pivot. A row
        # that is nothing but 'v.' is the ordinary multi-row caption, and
        # joining it away leaves no pivot for the reader to split on — every
        # court that stacks its caption lost its parties.
        if (_k + 1 < len(rows) and len(_t.split()) > 1
                and re.search(r"\bv[s]?\.?$", _t, re.I)):
            _rejoined.append(f"{_t} {_clean(rows[_k + 1])}")
            _k += 2
        else:
            _rejoined.append(rows[_k])
            _k += 1
    rows = _rejoined
    if not any(_is_pivot(r) for r in rows):
        # A single-ROW caption: 'STATE OF CONNECTICUT v. ANTHONY V.*' — the
        # pivot lives inside one row. Split the first row that carries it.
        for row in rows:
            t = _clean(row)
            for pivot in (" v. ", " vs. ", " V. "):
                if pivot in t and len(t) < 120 and not _is_banner_row(t):
                    a, _, b = t.partition(pivot)
                    return [a.strip(), b.strip()]
        return []
    sides: list[str] = []
    current: list[str] = []

    def close():
        nonlocal current
        if current:
            sides.append(_clean(" ".join(current)))
            current = []

    for row in rows:
        t = _clean(row)
        if not t:
            continue
        if _is_origin_row(t):
            close()
            break     # everything after the origin is origin/counsel matter
        if _is_pivot(t) or _is_status_row(t):
            close()
            continue
        if (_is_banner_row(t) or looks_like_docket(t)
                or date_row_value(t) or _is_citation_row(t)):
            continue
        # Caption APPARATUS rows (me's label grid, rosters) are not parties.
        if re.match(r"^(?:decision|docket|argued|decided|submitted|panel|"
                    r"present|before|citation|case no|opinion issued|"
                    r"reporter of decisions)\b\s*:?", t,
                    re.IGNORECASE):
            continue
        # A COUNSEL row inside the caption band is an appearance, never a
        # party ('Matthew McNicoll, assistant appellate defender, of
        # Concord, orally, for the' — nh).
        lowt = t.lower()
        if any(cue in lowt for cue in
               (", for the", "on the brief", "orally,", "attorney general",
                "appellate defender", "argued the cause")):
            continue
        # A parenthesized DOCKET LIST ('(CAAP-23-0000674; 1CCV-20-0000138)'
        # — haw stacks the lower courts' numbers over the caption) is
        # apparatus, never a party.
        inner = t.strip()
        if inner.startswith("(") and inner.endswith(")"):
            toks = [x.strip() for x in re.split(r"[;,]", inner[1:-1])
                    if x.strip()]
            if toks and all(
                    sum(c.isdigit() for c in x) >= 4
                    and re.fullmatch(r"[A-Za-z0-9./ -]+", x) for x in toks):
                continue
        current.append(t)
    close()
    # A CONSOLIDATED caption repeats each party under every docket block
    # (ca9 devas prints DEVAS/CC-DEVAS/ANTRIX three times): one party is
    # one side, however many blocks name it.
    _seen_sides: set[str] = set()
    _uniq = []
    for _sd in sides:
        _k = " ".join(_sd.split()).rstrip(",.").lower()
        if _k not in _seen_sides:
            _seen_sides.add(_k)
            _uniq.append(_sd)
    sides = _uniq
    if sides:
        trace.event("criteria.parties", f"{len(sides)} sides")
    return sides


def _is_citation_row(text: str) -> bool:
    """A neutral citation row ('2025 MT 64', '2026 VT 12', '2025 MT64')."""
    toks = _clean(text).split()
    if not (2 <= len(toks) <= 4) or not (toks[0].isdigit() and len(toks[0]) == 4):
        return False
    return all(len(t) <= 6 and (t.isdigit() or t.isupper()) for t in toks[1:])


@dataclass
class HeadmatterResult:
    items: list = field(default_factory=list)          # list[m.HmItem]
    criteria: m.Criteria = field(default_factory=m.Criteria)


def _hm_line(line: Line, pm: PageModel, geom: DocGeometry | None,
             strip_rail: str = "", indent_rel: bool = False) -> m.HmLine:
    from .footnotes import line_markup
    # A MASTHEAD spans the measure and still is centered — 'SUPREME COURT OF
    # THE UNITED STATES' is set 15pt against an 11pt body, edge to edge, so
    # the width cap that keeps justified body lines left-aligned catches it
    # too. Enlarged type on the page axis is the court's own banner.
    align = {"L": m.Align.LEFT, "C": m.Align.CENTER, "R": m.Align.RIGHT}[
        line_alignment(line, pm.width, geom,
                       banner_center_min_size=(geom.body_size + 2.0)
                       if geom else None)]
    text = line_markup(line)
    rel = 0.0
    if (indent_rel and align is m.Align.LEFT and geom
            and line.x0 > geom.body_x0 + 12):
        # A HANGING INDENT is the caption's grouping ('APPELLEES' set
        # 108pt in under its party block — cadc); reproduce it.
        rel = min(line.x0 - geom.body_x0, pm.width * 0.6)
    if strip_rail:
        # A cell's EDGE rail glyph belongs to the RAIL, not the text:
        # trailing ('Petitioner, │') and leading (': No. 12 WAP 2024' —
        # pa welds the colon rail onto each right cell's front).
        text = text.rstrip()
        while text and text[-1] in strip_rail:
            text = text[:-1].rstrip()
        text = text.lstrip()
        while text and text[0] in strip_rail:
            text = text[1:].lstrip()
    return m.HmLine(
        text=text,                # inline bold/italic carried in the markup
        prov=m.Prov(pm.number, (line.id,)),
        align=align, x0=line.x0, size=line.size,
        bold=line.all_bold, italic=False, rel=rel,
    )


def _paired_caption_block(box_lines: list[Line], sig: dict,
                          style_id: str | None, pm: PageModel,
                          geom: DocGeometry | None) -> m.CaptionBlock:
    """One caption box, cells PAIRED BY VISUAL ROW: the docket cell sits
    beside its own party row, with empty cells padding the shorter side so
    the columns stay aligned when rendered as two stacks."""
    rail = sig.get("rail")
    if rail is None and sig.get("vmid"):
        rail = "|"
    mid = sig.get("mid_x") or pm.width / 2
    if rail and rail != "|" and sig.get("rail_band"):
        # For a glyph rail, sides split at the rail column itself.
        rail_chars = [c for l in box_lines for c in l.chars
                      if (c.get("text") or "").strip() == rail]
        if rail_chars:
            mid = sorted(c["x0"] for c in rail_chars)[len(rail_chars) // 2]
    rail_glyphs = (rail or "") + "│┃|"
    rows: list[list[Line]] = []
    for line in sorted(box_lines, key=lambda l: (l.top, l.x0)):
        # The rail's own glyph rows ARE the rail, not cell content.
        if rail and rail != "|" and line.plain.strip().strip(rail_glyphs + " ") == "":
            continue
        if rows and abs(rows[-1][0].top - line.top) <= 2:
            rows[-1].append(line)
        else:
            rows.append([line])
    def _cells_line(cells: list[Line]) -> m.HmLine:
        # ALL of a row's cells on one side join into its line — taking only
        # the first silently lost label/value pairs that both sit left of
        # mid (Maine's 'Docket:  PUC-25-60' vanished this way).
        strip = rail_glyphs if rail and rail != "|" else ""
        parts = [_hm_line(c, pm, geom, strip)
                 for c in sorted(cells, key=lambda l: l.x0)]
        base = parts[0]
        if len(parts) == 1:
            return base
        text = base.text
        for p in parts[1:]:
            text = (text.rstrip() + "  " + p.text.lstrip()) if text.strip() \
                else p.text
        return m.HmLine(
            text=text,
            prov=m.Prov(pm.number, tuple(
                i for p in parts for i in p.prov.line_ids)),
            align=base.align, x0=base.x0, size=base.size,
            bold=all(p.bold for p in parts), italic=False)

    left, right = [], []
    for row in rows:
        l_cells = [l for l in row
                   if (l.col or ("L" if (l.x0 + l.x1) / 2 < mid else "R")) == "L"]
        r_cells = [l for l in row if l not in l_cells]
        if not l_cells and not r_cells:
            continue
        left.append(_cells_line(l_cells) if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number)))
        right.append(_cells_line(r_cells) if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number)))
    # A caption row is claimed WHOLE. Where the left cell hugs the rail
    # ('COMMONWEALTH OF PENNSYLVANIA :') the band can admit the right cell
    # and leave its twin behind — the text is captured as a party but the
    # line reads as lost. Own every line on the rows this block spans.
    _claimed = {l.id for l in box_lines}
    _tops = [l.top for l in box_lines]
    for _l in pm.lines:
        if _l.id not in _claimed and any(abs(_l.top - t) < 2 for t in _tops):
            _claimed.add(_l.id)
    return m.CaptionBlock(
        left=left, right=right, rail=rail,
        rail_rows=len(left), style_id=style_id, fp=dict(sig),
        prov=m.Prov(pm.number, tuple(sorted(_claimed))),
    )


def _build_caption_items(band_lines: list[Line], sig: dict,
                         style_id: str | None, pm: PageModel,
                         geom: DocGeometry | None) -> list:
    """The caption band as typed items. A stacked multi-case caption (akd's
    two boxes) is split at its drawn SHELF rules into one CaptionBlock per
    case, with the shelf emitted as a real Rule between them."""
    band = sig.get("band") or (0.0, pm.height)
    shelves = sorted(r.top for r in pm.h_rules
                     if band[0] < r.top <= band[1] + 8 and r.width >= 60)
    ordered = sorted(band_lines, key=lambda l: (l.top, l.x0))
    groups: list[list[Line]] = []
    cur: list[Line] = []
    crossed: list[bool] = []
    si = 0
    for line in ordered:
        advanced = False
        while si < len(shelves) and line.top > shelves[si]:
            si += 1
            advanced = True
        if advanced and cur:
            groups.append(cur)
            crossed.append(True)
            cur = []
        cur.append(line)
    if cur:
        groups.append(cur)
        crossed.append(si < len(shelves))   # a shelf closes the last box
    items: list = []
    # The banner may sit inside the measured band ('STATE OF MICHIGAN' /
    # 'COURT OF APPEALS' — michctapp): a LEADING row spanning both columns
    # is page-wide furniture of the caption, not a cell — casting it into
    # cap-left renders it centered on half the measure.
    mid0 = sig.get("mid_x") or pm.width / 2
    for group in groups:
        while group and group[0].x0 < mid0 - 40 and group[0].x1 > mid0 + 40:
            items.append(_hm_line(group.pop(0), pm, geom))
    groups = [g for g in groups if g]
    for group, shelf_after in zip(groups, crossed):
        items.append(_paired_caption_block(group, sig, style_id, pm, geom))
        if shelf_after:
            items.append(m.Rule(prov=m.Prov(pm.number), span="left"))
    return items


def read_headmatter(pages: list[tuple[PageModel, list[Line]]],
                    sig: dict, style_id: str | None,
                    geom: DocGeometry | None, trace: Trace,
                    court_id: str = "",
                    caption_wraps: bool = False) -> HeadmatterResult:
    """``pages``: (PageModel, content lines) for the headmatter span, furniture
    already removed by the caller. The caption band comes from the SAME
    signature the classifier stored."""
    result = HeadmatterResult()
    crit = result.criteria
    _positions: dict[int, tuple] = {}
    band = sig.get("band") or (60.0, 0.0)
    # A glyph-rail caption's band is the RAIL's own measured extent — the
    # default anchor band swallows the banner above it (ca6's ')' rail).
    if sig.get("rail") and sig.get("rail_band") and not sig.get("vmid") \
            and not sig.get("typed_band"):
        rb = sig["rail_band"]
        band = (rb[0] - 6, rb[1] + 6)

    # A CONSOLIDATED caption may RUN ON to the next page (ca9's devas
    # stacks one docket block per case across two pages): the run-on page
    # continues the caption when it carries docket cells and party/status
    # rows and no body prose has begun.
    _cap_pages = {1}
    if len(pages) > 1:
        for _pm2, _lines2 in pages[1:]:
            if _pm2.number - 1 not in _cap_pages:
                break
            _txts = [" ".join(l.plain.split()) for l in _lines2
                     if l.plain.strip()]
            if not _txts:
                break
            _dockets = sum(1 for t in _txts if looks_like_docket(t)
                           or t.lower().startswith("d.c. no"))
            _status = sum(1 for t in _txts
                          if t.rstrip(",.").lower() in
                          ("petitioner", "respondent", "petitioners",
                           "respondents", "appellant", "appellee",
                           "appellants", "appellees", "and"))
            _long = sum(1 for t in _txts if len(t) > 90)
            if _dockets >= 1 and _status >= 1 and _long == 0:
                _cap_pages.add(_pm2.number)
            else:
                break

    caption_lines: list[Line] = []
    _plain_rows: list[tuple] = []   # (pm, line, item) — rail-box rescue
    _label_cells: list[tuple] = []  # (x0, x1, top, label) — label grids
    _roster_buf: list[str] = []     # multi-row 'PRESENT:' roster (ca2)
    prev_text = ""
    # The caption page is the FIRST page of the headmatter span, which is
    # page 1 only where the court captions its cover. scotus prints the
    # caption at the head of each WRITING, so its span opens mid-document.
    _first_page = pages[0][0].number if pages else 1
    for pm, lines in pages:
        in_caption = pm.number in _cap_pages
        _rows = sorted(lines, key=lambda l: (l.top, l.x0))

        def _wrapped(ix: int, text: str) -> str:
            """``text`` plus the rows it WRAPS onto.

            A caption row is one statement however many lines the measure
            takes to set it ('ON WRIT OF CERTIORARI TO THE UNITED STATES
            COURT OF' / 'APPEALS FOR THE SEVENTH CIRCUIT' names one court,
            and reading the first line alone reports a court that does not
            exist). What separates a WRAP from the next element is how the
            page is set, not what the words say: a wrap keeps the same type
            SIZE and a tight leading, while the next element changes size,
            or stands off. scotus sets its caption 11pt on a 13.4 lead and
            its origin row 9pt on 11.1, then stands '[May 14, 2026]' off by
            17 — so size plus leading reads the block exactly, and no list
            of phrases has to.
            """
            out = text
            cur = _rows[ix]
            k = ix + 1
            while k < len(_rows) and not out.rstrip().endswith(
                    (".", ":", ";", "!", "?")):
                nxt, prv = _rows[k], _rows[k - 1]
                cand = _clean(nxt.plain)
                size = nxt.size or (geom.body_size if geom else 11.0)
                if (not cand or nxt.page != cur.page
                        or abs(size - (cur.size or size)) > 0.4
                        or not 0 < nxt.top - prv.top <= 1.5 * size):
                    break
                out = f"{out} {cand}"
                k += 1
            return out

        for _ix, line in enumerate(_rows):
            text = _clean(line.plain)
            if not text:
                continue
            pair = f"{prev_text} {text}".strip()
            prior, prev_text = prev_text, text
            prior_label = prior.rstrip(": ").lower()
            # A LABEL GRID pairs by COLUMN, not reading order ('Argued |
            # Decided' row above 'November 3 | December 4' — nj): a label
            # cell overhead in the same column outranks the sequential
            # prior.
            bare = text.strip().rstrip(":").lower()
            if bare in _DATE_LABELS and len(text.strip()) <= 14:
                _label_cells.append((line.x0 - 24, line.x1 + 24,
                                     line.top, bare))
            else:
                cx = (line.x0 + line.x1) / 2
                for lx0, lx1, ltop, lab in reversed(_label_cells):
                    if lx0 <= cx <= lx1 and 0 < line.top - ltop <= 2.0 * (
                            geom.lead if geom else 20.0):
                        prior_label = lab
                        break
            # --- criteria evidence (publish once) ---
            docket = looks_like_docket(text)
            if docket and (line.col == "R" or line.top < band[0]
                           or pm.number == _first_page
                           # conn's '(SC 21196)' prints under the caption
                           # on the page AFTER the slip cover
                           or text.strip().startswith("(")):
                if crit.docket_number is None:
                    crit.docket_number = docket
                    trace.event("criteria.docket_number",
                                f"p{pm.number}: {docket!r}")
                elif (docket != crit.docket_number
                      and docket not in crit.other_dockets):
                    crit.other_dockets.append(docket)
            # A bare date under an 'Argued:'/'Submitted:' LABEL is the
            # argument date (me's caption grid splits label and value into
            # separate lines) — decision_date must not take it.
            if prior_label in ("argued", "submitted", "heard",
                               "argued and submitted", "oral argument"):
                if crit.submitted is None:
                    d = find_date(text)
                    if d:
                        crit.submitted = d
                        trace.event("criteria.submitted",
                                    f"p{pm.number}: {d!r}")
            elif crit.decision_date is None:
                date = (find_date(text)
                        if prior_label in ("decided", "decision", "filed")
                        else date_row_value(text))
                if date:
                    crit.decision_date = date
                    trace.event("criteria.decision_date",
                                f"p{pm.number}: {date!r}")
            # The BENCH: a 'Panel:'/'Present:'/'Before' roster names the
            # judges — raw string to judges, split names to panel. ca2
            # stacks one judge per row under 'PRESENT:', closing on the
            # 'Circuit Judges.' title row — accumulate the run.
            if crit.judges is None:
                roster = None
                if prior_label in ("panel", "present", "before", "justices",
                                   "judges", "en banc") and _ROSTER_TITLE.search(text):
                    roster = text
                else:
                    low0 = text.lower()
                    for opener in ("before:", "before ", "present:",
                                   "panel:"):
                        if not low0.startswith(opener):
                            continue
                        if _ROSTER_TITLE.search(text):
                            roster = text[len(opener):].strip()
                        else:
                            _roster_buf.append(text[len(opener):].strip())
                        break
                    else:
                        # a bare 'Before' opener starts a WRAPPED roster
                        # (ca1 centers 'Before' / names / 'Circuit
                        # Judges.' on three rows)
                        if not _roster_buf and low0.rstrip(":") == "before":
                            _roster_buf.append("")
                        elif _roster_buf:
                            _nm_only = text.strip().rstrip(",.")
                            _nm_only = (_nm_only.replace(" ", "")
                                        .replace(",", "").replace("and", "")
                                        .replace("-", "").replace("'", ""))
                            if len(text) <= 70 and (
                                    _ROSTER_TITLE.search(text)
                                    or _nm_only.isalpha()
                                    or text.strip().isupper()):
                                _roster_buf.append(text.strip())
                                if _ROSTER_TITLE.search(text):
                                    roster = " ".join(_roster_buf)
                                    _roster_buf.clear()
                            else:
                                _roster_buf.clear()
                if roster:
                    crit.judges = roster.strip()
                    crit.panel = roster_names(roster)
                    trace.event("criteria.judges", f"p{pm.number}")
            if crit.lower_court is None and _is_origin_row(text) \
                    and 10 < len(text) < 220:
                from ..audit import strip_tags, unescape_xml
                crit.lower_court = unescape_xml(strip_tags(
                    _wrapped(_ix, text)))
                trace.event("criteria.lower_court", f"p{pm.number}")
            # The disposition band: 'CLAY, J., delivered the opinion of the
            # court in which…' (ca6) / 'Opinion for the Court filed by
            # Circuit Judge RAO.' (cadc) / '…by published opinion. Judge
            # Giles wrote the opinion…' (ca4).
            # Tested on the line AND on the wrapped pair — tenn breaks
            # 'Judgment of the Court of Appeals and / the Trial Court
            # Affirmed' across rows.
            for cand in (text, pair):
                low = cand.lower()
                if crit.disposition is None and len(cand) < 400 and (
                        "delivered the opinion" in low
                        or "wrote the opinion" in low
                        or ("opinion" in low and "filed by" in low)
                        or ("judgment" in low and any(
                            w in low for w in ("affirmed", "reversed",
                                               "vacated", "remanded",
                                               "modified", "denied")))):
                    from ..audit import strip_tags, unescape_xml
                    crit.disposition = unescape_xml(strip_tags(cand))
                    trace.event("criteria.disposition", f"p{pm.number}")
                    break
            # --- placement ---
            if in_caption and (pm.number > 1
                               or band[0] - 4 <= line.top <= band[1] + 4):
                caption_lines.append(line)
            elif _is_typed_rule_row(text):
                rule = m.Rule(prov=m.Prov(pm.number, (line.id,)), typed=True,
                              span="full" if line.width > pm.width * 0.4
                              else "left" if line.x1 < pm.width / 2
                              else "right" if line.x0 > pm.width / 2
                              else "full")
                result.items.append(rule)
                _positions[id(rule)] = (pm.number, line.top)
            else:
                # ADJACENT same-row pieces are one visual row ('Decided:'
                # + 'May 7, 2026' split at a zero gap — del): join them.
                if (_plain_rows and _plain_rows[-1][0] is pm
                        and abs(_plain_rows[-1][1].top - line.top) < 2
                        and -2 <= line.x0 - _plain_rows[-1][1].x1 <= 12):
                    prev_item = _plain_rows[-1][2]
                    from .footnotes import line_markup as _lm2
                    add = _lm2(line).strip()
                    if add:
                        prev_item.text = (prev_item.text.rstrip() + " "
                                          + add)
                        prev_item.prov = m.Prov(
                            pm.number,
                            tuple(prev_item.prov.line_ids) + (line.id,))
                        _plain_rows[-1] = (pm, line, prev_item)
                    continue
                # A WRAPPED row continues the SAME statement — same type
                # size, tight leading. Rendered as separate rows the block
                # comes out ragged (a full-measure first line reads
                # left-aligned beside its centered runover) when the page
                # sets one centered statement. Where the court prints its
                # caption at the head of each writing (scotus), these are
                # the rows that carry the parties and the court below.
                if caption_wraps and _plain_rows and _plain_rows[-1][0] is pm:
                    _pl, _pitem = _plain_rows[-1][1], _plain_rows[-1][2]
                    if (abs((line.size or 0) - (_pl.size or 0)) <= 0.4
                            and 0 < line.top - _pl.top
                                <= 1.5 * (line.size or 11.0)):
                        from .footnotes import line_markup as _lm5
                        add = _lm5(line).strip()
                        if add:
                            _pitem.text = _pitem.text.rstrip() + " " + add
                            _pitem.prov = m.Prov(
                                pm.number,
                                tuple(_pitem.prov.line_ids) + (line.id,))
                            if line_alignment(line, pm.width, geom) == "C":
                                _pitem.align = m.Align.CENTER
                            _plain_rows[-1] = (pm, line, _pitem)
                            continue
                result.items.append(_hm_line(line, pm, geom,
                                             indent_rel=True))
                _positions[id(result.items[-1])] = (pm.number, line.top)
                _plain_rows.append((pm, line, result.items[-1]))

    # A CaptionBlock exists only when the page actually DRAWS two columns:
    # a mid vertical, a glyph rail, whitespace two-column rows, or
    # flush-right status rows. A centered stacked caption (mont, ca1) is
    # styled rows, and the TYPED SANDWICH (ca8's centered caption between
    # '____' rules) is centered rows too — building columns there is
    # inventing layout.
    two_col = bool(sig.get("vmid") or sig.get("rail")
                   or sig.get("two_col_ws", 0) >= 2
                   or sig.get("flush_right", 0) >= 2)
    party_rows: list[str]
    if caption_lines and two_col:
        pm1 = pages[0][0]
        caption_items = _build_caption_items(caption_lines, sig, style_id,
                                             pm1, geom)
        for i, it in enumerate(caption_items):
            _positions[id(it)] = (1, band[0] + i * 0.01)
        result.items.extend(caption_items)
        # A CONSOLIDATED caption repeats each party (and its wrapped
        # halves) under every docket block — ca9's devas prints the same
        # three names three times; one party is one side.
        _seen_pr: set[str] = set()
        party_rows = []
        for _it in caption_items:
            if not isinstance(_it, m.CaptionBlock):
                continue
            for _r in _it.left:
                if not _r.text.strip():
                    continue
                _k = " ".join(str(_r.text).split()).rstrip(",.").lower()
                if _k in _seen_pr and _k not in (
                        "petitioner", "respondent", "and", "v.", "vs."):
                    continue
                _seen_pr.add(_k)
                party_rows.append(_r.text)
    else:
        # Centered/open caption: the rows stay styled rows in place; typed
        # rules render as the rules they are.
        _prev_cap: tuple | None = None   # (line, HmLine) — same-row join
        _cap_row_items: list = []
        for line in sorted(caption_lines,
                           key=lambda l: (l.page, l.top, l.x0)):
            if _is_typed_rule_row(line.plain.strip()):
                row = m.Rule(prov=m.Prov(pages[0][0].number, (line.id,)),
                             typed=True,
                             span="full" if line.width > pages[0][0].width * 0.4
                             else "left" if line.x1 < pages[0][0].width / 2
                             else "right" if line.x0 > pages[0][0].width / 2
                             else "full")
                _prev_cap = None
            else:
                # ADJACENT same-row pieces are one visual row ('Decided:'
                # + 'May 7, 2026' at a zero gap — del).
                if (_prev_cap is not None
                        and _prev_cap[0].page == line.page
                        and abs(_prev_cap[0].top - line.top) < 2
                        and -2 <= line.x0 - _prev_cap[0].x1 <= 12):
                    from .footnotes import line_markup as _lm3
                    add = _lm3(line).strip()
                    if add:
                        _prev_cap[1].text = (_prev_cap[1].text.rstrip()
                                             + " " + add)
                        _prev_cap[1].prov = m.Prov(
                            pages[0][0].number,
                            tuple(_prev_cap[1].prov.line_ids) + (line.id,))
                        _prev_cap = (line, _prev_cap[1])
                    continue
                # A WRAPPED row is the SAME statement: 'KALEY CHILES,
                # PETITIONER v. PATTY SALAZAR, IN' / 'HER OFFICIAL CAPACITY
                # AS EXECUTIVE DIRECTOR' / 'OF THE COLORADO DEPARTMENT OF' /
                # 'REGULATORY AGENCIES, ET AL.' is one party statement the
                # measure took four lines to set. Rendered as four rows it
                # comes out ragged — each line aligned on its own — when the
                # page shows one centered block. Same type SIZE and a tight
                # leading mark the wrap; a size change or a stand-off gap
                # ends the statement (see `_wrapped`).
                _psize = (_prev_cap[0].size if _prev_cap else 0) or 0
                if (caption_wraps and _prev_cap is not None
                        and _prev_cap[0].page == line.page
                        and abs((line.size or 0) - _psize) <= 0.4
                        and 0 < line.top - _prev_cap[0].top
                            <= 1.5 * (line.size or 11.0)):
                    from .footnotes import line_markup as _lm4
                    add = _lm4(line).strip()
                    if add:
                        _prev_cap[1].text = (_prev_cap[1].text.rstrip()
                                             + " " + add)
                        _prev_cap[1].prov = m.Prov(
                            pages[0][0].number,
                            tuple(_prev_cap[1].prov.line_ids) + (line.id,))
                        # the joined statement is centered when the page
                        # centered any of its lines
                        if line_alignment(line, pages[0][0].width,
                                          geom) == "C":
                            _prev_cap[1].align = m.Align.CENTER
                        _prev_cap = (line, _prev_cap[1])
                        continue
                row = _hm_line(line, pages[0][0], geom, indent_rel=True)
                _prev_cap = (line, row)
                _cap_row_items.append(row)
            _positions[id(row)] = (pages[0][0].number, line.top)
            result.items.append(row)
        # Parties come from the CAPTION BAND's own rows — the heading and
        # roster above it are apparatus (ca2's 'SUMMARY ORDER' + 'PRESENT:'
        # names were reading as a party side).
        # a consolidated caption repeats a party under each docket block
        # (ca9 devas) — the same row text is one party, not several
        # A CONSOLIDATED caption repeats each party (and its wrapped
        # halves) under every docket block — ca9's devas prints the same
        # three names three times. Drop a row whose text already appeared.
        _seen_rows: set[str] = set()
        party_rows = []
        for it in _cap_row_items:
            _k = " ".join(str(it.text).split()).rstrip(",.").lower()
            if not _k:
                continue
            if _k in _seen_rows and _k not in (
                    "petitioner", "respondent", "and", "v.", "vs."):
                continue
            _seen_rows.add(_k)
            party_rows.append(it.text)

    # CONSOLIDATED captions: a SECOND (third, …) caption box below the
    # primary band renders as interleaved plain rows with naked rail
    # glyphs (pasuperct stacks one colon-rail caption per docket). A rail
    # COLUMN among the leftover rows — three-plus ':' rows sharing a left
    # edge — is the evidence; rebuild each cluster as a CaptionBlock.
    _lead = geom.lead if geom else 16.0
    _by_page: dict[int, list] = {}
    for pm_, line_, item_ in _plain_rows:
        _by_page.setdefault(pm_.number, []).append((pm_, line_, item_))
    for _pgno, _rows in _by_page.items():
        _pm0 = _rows[0][0]
        _rails = [l for _, l, _ in _rows
                  if l.plain.strip()[:1] in (":", "§")]
        if len(_rails) < 3:
            continue
        _glyph = max(":§", key=lambda g: sum(
            1 for l in _rails if l.plain.strip()[:1] == g))
        _rails = [l for l in _rails if l.plain.strip()[:1] == _glyph]
        if len(_rails) < 3:
            continue
        _xs = sorted(l.x0 for l in _rails)
        _mid = _xs[len(_xs) // 2]
        _rails = sorted((l for l in _rails if abs(l.x0 - _mid) <= 5),
                        key=lambda l: l.top)
        if len(_rails) < 3:
            continue
        _clusters = [[_rails[0]]]
        for r in _rails[1:]:
            if r.top - _clusters[-1][-1].top <= 3 * _lead:
                _clusters[-1].append(r)
            else:
                _clusters.append([r])
        for _cl in _clusters:
            if len(_cl) < 3:
                continue
            t0 = min(l.top for l in _cl) - _lead - 2
            t1 = max(l.top for l in _cl) + _lead + 2
            # A caption CELL never CROSSES the rail: a centered 'Appeal
            # from…' row spanning it sits BETWEEN boxes, not inside one.
            _box = [(p_, l_, i_) for p_, l_, i_ in _rows
                    if t0 <= l_.top <= t1
                    and not (l_.x0 < _mid - 6 and l_.x1 > _mid + 6)]
            if len(_box) < 4:
                continue
            _blk = _paired_caption_block(
                [l_ for _, l_, _ in _box],
                {"rail": _glyph, "mid_x": _mid + 2}, None, _pm0, geom)
            for _, _, i_ in _box:
                if i_ in result.items:
                    result.items.remove(i_)
            result.items.append(_blk)
            _positions[id(_blk)] = (_pgno, min(l_.top for _, l_, _ in _box))

    # Drawn rules the page sets BETWEEN headmatter rows (ca4 fences each
    # section in ruled bands) render where the page drew them. Underlines
    # (a rule inside a row's own band) and caption-internal rules (the
    # caption items carry their own) are excluded.
    for pm, lines in pages:
        if not lines:
            continue
        last_top = max(l.top for l in lines)
        for r in pm.h_rules:
            # A SHORT CENTERED dash is a section separator the page draws
            # between headmatter blocks (cadc's 36pt '────'); anything
            # else under 60pt is noise.
            centered_dash = (18 <= r.width < 60
                             and abs((r.x0 + r.x1) / 2 - pm.width / 2) < 60)
            if r.width < 60 and not centered_dash:
                continue
            # A rule BELOW the last headmatter row still closes the block
            # when no text intervenes — ca1 rules under its filed date, and
            # a flat +10 window dropped that bottom border. Any content
            # between the row and the rule means the rule is the body's.
            if r.top > last_top + 10 and any(
                    last_top + 2 < l.top < r.top - 2 for l in pm.lines):
                continue
            if pm.number == 1 and band[0] - 6 <= r.top <= band[1] + 6 \
                    and not centered_dash and two_col:
                # In-band rules belong to the CaptionBlock ONLY when one
                # was built; a centered/open caption's drawn fences are
                # real rules (haw boxes its caption with full-measure
                # rules that vanished here).
                continue
            # Test against the PAGE's lines, not just the hm span: a rule
            # underlining a counsel column header (guam) still decorates
            # that row even after the row routed to attorneys.
            if any(abs(l.bottom - r.top) < 4.0 and l.x0 < r.x1 and l.x1 > r.x0
                   for l in pm.lines):
                continue  # an underline decorating a row
            rule = m.Rule(prov=m.Prov(pm.number),
                          span="center" if centered_dash else "full")
            _positions[id(rule)] = (pm.number, r.top)
            result.items.append(rule)

    result.items.sort(key=lambda it: _positions.get(id(it), (99, 1e9)))
    # A court whose caption grammar is its own decides its parties (scotus
    # wraps one caption statement across rows, so no row carries a pivot).
    from .evidence import NOTHING as _NOTHING, court_decides as _cd
    from ..audit import strip_tags as _st_p, unescape_xml as _ux_p
    _rows_all = [_clean(_ux_p(_st_p(getattr(it, "text", "") or "")))
                 for it in result.items if getattr(it, "text", None)]
    _court_parties = _cd("headmatter.parties", court_id, trace,
                         rows=_rows_all)
    crit.parties = (list(_court_parties) if _court_parties is not _NOTHING
                    else read_parties(party_rows, trace))
    return result


def _above_band(item: m.HmLine, band, pages) -> bool:
    """Was this page-1 row above the caption band? Recovered from its source
    line (items keep provenance line ids)."""
    pm1, lines1 = pages[0]
    by_id = {l.id: l for l in lines1}
    src = by_id.get(item.prov.line_ids[0]) if item.prov.line_ids else None
    return bool(src and src.top < band[0])


# --------------------------------------------------------------------------
# the cases a record decides
# --------------------------------------------------------------------------
# A CONSOLIDATED RECORD IS MORE THAN ONE CASE. Where a court reader already
# published the grouping (the district lane reads its box's compartments),
# this leaves it alone; where it did not, the grouping is still on the page —
# in the ORDER of the rows the reader tagged. ca5 prints 'No. 26-70004', that
# case's parties, 'consolidated with', 'No. 26-10354' and THAT case's parties;
# read as a flat row list the two weld into one (the user, 2026-08-23: 'has
# two consolidated cases and we recognized it in teh old parser … it would
# list case 1 and case 2').
_CONSOLIDATED_MARK = re.compile(
    r"^\(?\s*(?:and\s+)?consolidated(?:\s+with)?\b|^\(?\s*c/w\b", re.I)
# A NUMBER THE COURT BELOW GAVE IT is not a companion case, and courts print
# it in the same band ('USDC No. 4:09-CV-160', 'D.C. No. 1:22-cv-00776').
# Tagged as a docket it would open a second case and swallow the rows under
# it.
_BELOW_DOCKET = re.compile(
    r"\b(?:USDC|U\.?S\.?D\.?C|D\.?C\.?\s+No|District\s+Court|Superior|"
    r"Circuit\s+Court|Bankr|Tax\s+Court|Agency|BIA|Board)\b", re.I)
_PIVOT_ROW = re.compile(r"^(?:v\.?|vs\.?|versus|against)[\s,]*$", re.I)
_PARTY_STATUS = re.compile(
    r"^(?:plaintiffs?|defendants?|appellants?|appellees?|petitioners?|"
    r"respondents?|movants?|intervenors?|applicants?|claimants?|"
    r"cross-\w+|amici?\b|amicus\b|debtors?|creditors?|in\s+propria)"
    r"[\s\-—,.]*(?:$|[\-—])", re.I)


def _case_name_of(rows: list[str]) -> tuple[str, list[str]]:
    """A case name out of one case's own caption rows: the names either side
    of the pivot, apparatus dropped. Never a wholesale join — 'Petitioner—
    Appellant,' is a status, not a party."""
    left: list[str] = []
    right: list[str] = []
    side, seen = left, False
    for row in rows:
        flat = " ".join(row.split())
        if not flat or _PARTY_STATUS.match(flat):
            continue
        if _PIVOT_ROW.match(flat):
            side, seen = right, True
            continue
        head = flat.split(None, 1)
        if head and _PIVOT_ROW.match(head[0]):
            side, seen = right, True
            flat = " ".join(head[1].split()) if len(head) > 1 else ""
            if not flat or _PARTY_STATUS.match(flat):
                continue
        side.append(flat)
    a = " ".join(left).strip(" ,;")
    b = " ".join(right).strip(" ,;")
    if seen and a and b:
        return f"{a} v. {b}", [a, b]
    joined = " ".join(x for x in (a, b) if x).strip(" ,;")
    return joined, ([joined] if joined else [])


def read_consolidated_cases(doc) -> list:
    """The cases this record decides, read off the headmatter's own rows.

    Returns [] for the ordinary record — one case, already named by
    `docket_number` and `case_name`. A list means the page really does state
    more than one number, each with its own parties under it."""
    from ..audit import strip_tags, unescape_xml

    rows: list = []
    for item in doc.headmatter:
        if isinstance(item, m.HmLine):
            rows.append(item)
        elif isinstance(item, m.CaptionBlock):
            for pair in zip(item.left, item.right):
                rows.extend([r for r in pair if r is not None])

    cases: list = []                  # [(docket, prov, [caption rows])]
    for row in rows:
        text = unescape_xml(strip_tags(row.text or "")).strip()
        if not text:
            continue
        if row.role == "docket":
            if _CONSOLIDATED_MARK.match(text):
                continue              # the connector, not a number
            if _BELOW_DOCKET.search(text):
                continue              # the court below's own number
            if any(ch.isdigit() for ch in text):
                cases.append((text, row.prov, []))
                continue
        if row.role == "caption" and cases:
            cases[-1][2].append(text)

    # EVIDENCE, NOT SHAPE: two numbers each with their own parties under
    # them. One number with parties and a second with none is a docket
    # printed twice, not a consolidation.
    good = [c for c in cases if c[2]]
    if len(good) < 2:
        return []
    out = []
    for docket, prov, caption in good:
        name, parties = _case_name_of(caption)
        out.append(m.CaseRef(docket_number=docket, case_name=name,
                             parties=parties, caption=caption, prov=prov))
    return out
