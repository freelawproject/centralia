"""THE footnote-zone subsystem — one file, evidence-chained.

This consumed ~25% of the old repo's commit history as scattered per-court
fixes; here every finder is a named evidence step and every page's zone
decision is a recorded Decision (including "no zone"). The ordered chain is
the old system's final, hard-won form (base.py find_footnote_separator steps
1–7), ported onto the shared PageModel:

  configured-rect > provider candidates > structural > rule-over-smaller-text
  > rule-over-labelled-note > typed-text-rule > zone-by-size (opt-in)
  > indented-rule > learned-signature > tighter-leading > no-zone (floor)

Core-owned vetoes, applied to every candidate regardless of source:
an underline is not a separator (unless the document's own signature proves
the shape); the caption shelf is not a separator; a box edge sharing its row
with another rule is not a separator. NOTHING may guess a zone without a
separator — zone-by-size stays off unless a profile opts in with
measurements.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from ..geometry import DocGeometry
from ..model import Prov
from ..pdfio.model import DrawnRule, Line, PageModel, PdfModel
from ..pdfio.rules import TYPED_SEP_ADMIT_GLYPHS, TYPED_SEP_GLYPHS, is_typed_rule
from .evidence import Decision, Evidence, Trace, providers_for
from .furniture import (furniture_key, gutter_column_ids, is_folio_text,
                        is_gutter_number, repeated_bottom_keys,
                        repeated_top_keys)

FOOTNOTE_LABEL_CHARS = set("0123456789*†‡§∗⁎﹡＊")
_LABEL_CANON = {"∗": "*", "⁎": "*", "﹡": "*", "＊": "*"}
# A SYMBOL FONT DOES NOT SPEAK UNICODE: SymbolMT encodes its star as 0xF000
# plus the font's own byte (0x2A -> U+F02A). Folded back by ARITHMETIC and
# self-limiting — accepted only when it lands on a known label character.
_PUA_LO, _PUA_HI = 0xF000, 0xF0FF


def canon_glyph(ch: str) -> str:
    if len(ch) == 1 and _PUA_LO <= ord(ch) <= _PUA_HI:
        plain = chr(ord(ch) - _PUA_LO)
        if plain in FOOTNOTE_LABEL_CHARS:
            return plain
    return _LABEL_CANON.get(ch, ch)


def canon_label(text: str) -> str:
    """One label per note, whatever glyph the producer reached for."""
    return "".join(canon_glyph(c) for c in text)


@dataclass(frozen=True)
class FootnoteConfig:
    """Court FACTS about footnotes — evidence config, never decisions."""

    sep_rect: tuple[float, float] | None = None   # exact (x0, x1) of the rule
    structural: bool = False       # body-size-note court: structural finder first
    reject_underlines: bool = True  # conn's genuine rule sits inside the band
    text_min_width: float | None = None   # typed-rule width when court fixes it
    zone_by_size: bool = False     # OFF: nothing may guess a zone (see lesson)
    dedupe_labels: bool = False    # assembly-time: collapse repeated labels


# --------------------------------------------------------------------------
# label detection (also the corroboration the separator chain leans on)
# --------------------------------------------------------------------------

def opens_with_raised_label(line: Line) -> bool:
    chars = [c for c in line.chars if (c.get("text") or "").strip()]
    if not chars:
        return False
    return (round(chars[0].get("size", 0), 1) <= line.size - 1.5
            and canon_glyph(chars[0].get("text") or "") in FOOTNOTE_LABEL_CHARS)


def _symbol_label_at_head(line: Line) -> str | None:
    """A SYMBOL label set at body size: leading */†/‡, a word space, a
    sentence opening. A compound label ('**') is set SOLID; symbols separated
    by word spaces are a DINKUS ('* * *') and never a label."""
    chars = [c for c in line.chars if (c.get("text") or "").strip()]
    if len(chars) < 3 or canon_glyph(chars[0].get("text") or "") not in "*†‡":
        return None
    size = line.size
    i = 1
    while i < len(chars) and chars[i]["text"] == chars[0]["text"]:
        if chars[i]["x0"] - chars[i - 1]["x1"] > size * 0.15:
            return None  # spaced repeats: the dinkus
        i += 1
    if i >= len(chars):
        return None
    gap = chars[i]["x0"] - chars[i - 1]["x1"]
    head = (chars[i].get("text") or "")[:1]
    if head == chars[0]["text"]:
        return None
    # An UPPERCASE head accepts the star even welded solid — SCOTUS sets
    # '*JUSTICE JACKSON says…' and '*The syllabus…' with no space at all.
    # A quote/bracket head still needs the word space to rule out prose.
    if head.isupper() or (gap >= size * 0.2 and head in "“”\"‘’'(["):
        return canon_label(chars[0]["text"] * i)
    return None


def detect_label(line: Line) -> str | None:
    """If ``line`` starts a new footnote, its label; else None. Three paths:
    a short label-only line, a raised (superscripted) label run, a body-size
    symbol label. (Body-size DIGIT labels are an assembly-time admission, not
    zone evidence.)"""
    chars = line.chars
    if not chars:
        return None
    plain = line.plain.strip()
    if plain and len(plain) <= 3 and all(
            canon_glyph(c) in FOOTNOTE_LABEL_CHARS for c in plain):
        return canon_label(plain)
    printable = [c for c in chars if (c.get("text") or "").strip()]
    if not printable:
        return None
    first = printable[0]
    if not (round(first.get("size", 0), 1) <= line.size - 1.5
            and canon_glyph(first.get("text") or "") in FOOTNOTE_LABEL_CHARS):
        return _symbol_label_at_head(line)
    out = []
    for c in printable:
        if (round(c.get("size", 0), 1) <= line.size - 1.5
                and canon_glyph(c.get("text") or "") in FOOTNOTE_LABEL_CHARS):
            out.append(canon_glyph(c.get("text") or ""))
        else:
            break
    return canon_label("".join(out)) or "?"


def mark_flags(line: Line) -> list[bool]:
    """Per-char: may this glyph be read as a footnote MARK? A mark is RAISED
    (a small glyph below the baseline is a subscript — a chemical formula's
    digits) and part of a SHORT run (1–3 label chars, no letters — caption
    small print 'Cir. Ct. No. 2024CV549' is not five marks)."""
    chars = line.chars
    if not chars:
        return []
    body_size = line.size
    full_tops = [c.get("top") for c in chars
                 if round(c.get("size", 0), 1) > body_size - 1.5
                 and (c.get("text") or "").strip() and c.get("top") is not None]
    base_top = min(full_tops) if full_tops else None
    small = [
        round(c.get("size", 0), 1) <= body_size - 1.5
        and bool((c.get("text") or "").strip())
        and (base_top is None or c.get("top") is None
             or c["top"] <= base_top + 1.0)
        for c in chars
    ]
    out = [False] * len(chars)
    i = 0
    while i < len(chars):
        if not small[i]:
            i += 1
            continue
        j = i
        while j < len(chars) and (small[j] or not (chars[j].get("text") or "").strip()):
            j += 1
        run = [c for c in chars[i:j] if (c.get("text") or "").strip()]
        labels = [c for c in run
                  if canon_glyph(c.get("text") or "") in FOOTNOTE_LABEL_CHARS]
        if labels and len(labels) <= 3 and not any(
                (c.get("text") or "").isalpha() for c in run):
            for k in range(i, j):
                out[k] = small[k]
        i = j
    return out


def line_marks(line: Line) -> list[str]:
    """Footnote MARKS a body line calls, as canonical label strings."""
    flags = mark_flags(line)
    out: list[str] = []
    current = ""
    for c, flagged in zip(line.chars, flags):
        t = (c.get("text") or "").strip()
        if flagged and t:
            current += canon_glyph(t)
        elif current:
            out.append(current)
            current = ""
    if current:
        out.append(current)
    # A mark set inside quoted material is BRACKETED ('.[3]'); the canonical
    # value is the numeral — bookkeeping that compares marks to labels must
    # never see the publisher's brackets.
    return [m.strip("[]()") or m for m in out]


def line_markup(line: Line) -> str:
    """The line's inline-markup rebuild (<em>/<strong>/<u>/<footnotemark>),
    fed by this subsystem's mark test so the two can never disagree about
    what is a reference."""
    from ..pdfio.text import inline_text
    return inline_text(line.chars, FOOTNOTE_LABEL_CHARS, canon_glyph,
                       mark_flags(line))


# --------------------------------------------------------------------------
# body-size ("flush") labels — shape is never proof; bookkeeping decides
# --------------------------------------------------------------------------

# How many digits a body-size label may run to. Two, because a wrapped
# citation opening on a year is four and a reporter page is three.
FLUSH_LABEL_MAX_DIGITS = 2


def flush_label_shape(line: Line, rail: float | None) -> tuple[str, str] | None:
    """The SHAPE of a BODY-SIZE label at the head of ``line`` as
    (label, printed_prefix), or None. Forms the corpus prints: '1. On appeal',
    '1.<tab>hanging', '1 For purposes', '1We note'. Digits only — a body-size
    '*' has no sequence for the bookkeeping to check."""
    chars = [c for c in line.chars if (c.get("text") or "").strip()]
    if len(chars) < 2:
        return None
    size = line.size
    if round(chars[0].get("size", 0), 1) <= size - 1.5:
        return None  # raised: the superscript path owns this line
    i = 0
    while i < len(chars) and (chars[i].get("text") or "").isdigit():
        # A real multi-digit label sets its digits ADJACENT; a gap means the
        # label ended ('1<tab>31 C.F.R.' is label 1, not 131).
        if i and (chars[i]["x0"] - chars[i - 1]["x1"]) > size * 0.5:
            break
        i += 1
    if not 1 <= i <= FLUSH_LABEL_MAX_DIGITS:
        return None
    if i == len(chars):
        return None  # a bare number is a folio, not a label
    label = "".join(chars[k]["text"] for k in range(i))
    prefix = label
    dotted = (chars[i].get("text") or "") == "."
    if dotted:
        prefix += "."
        i += 1
        if i == len(chars):
            return None
    gap = chars[i]["x0"] - chars[i - 1]["x1"]
    if gap >= size * 1.5:
        return label, prefix   # label, TAB, prose — a citation can't tab
    head = (chars[i].get("text") or "")[:1]
    if not (head.isupper() or head in "“”\"‘’'([‛„"):
        return None
    # The line's own word space (measured), floored by the old constant.
    word_gaps = [round(chars[k]["x0"] - chars[k - 1]["x1"], 2)
                 for k in range(1, len(chars))]
    word_gaps = [g for g in word_gaps if g > 0.5]
    if word_gaps:
        from collections import Counter
        space = Counter(word_gaps).most_common(1)[0][0]
        ceiling = max(size * (2.0 if dotted else 0.45), space * 2.0)
    else:
        ceiling = size * (2.0 if dotted else 0.45)
    if gap <= ceiling:
        return label, prefix
    # A HANGING label: prose resumes exactly on the zone's own rail, the
    # label hung out to its left (South Dakota: '1.' at 72, prose at 108).
    if (dotted and rail is not None and line.x0 < rail - 4
            and abs(chars[i]["x0"] - rail) <= 2):
        return label, prefix
    return None


def admit_flush_labels(zone_lines: list[Line],
                       owed: dict[int, int] | set[int]) -> dict[int, str]:
    """{line.id: label} for body-size labels the BOOKKEEPING admits. Gates:
    (1) the body calls that mark; (2) it is the number the zone owes NEXT —
    or a restart at the writing's lowest owed mark (a dissent's notes restart
    at 1), where EACH restart needs its own body reference: a document whose
    text references mark '1' once has one sequence, twice has two (carroll's
    majority and dissent), and a prose line shaped '1 Trump v. …' can never
    mint a third; (3) no raised label anywhere ahead claims it; (4) the line
    opens a paragraph — or is dotted with exactly the owed-next value. With
    no owed marks there is no evidence — the floor is refusal."""
    if isinstance(owed, set):
        owed = {v: 1 for v in owed}
    if not owed or not zone_lines:
        return {}
    from collections import Counter
    x1s = sorted(l.x1 for l in zone_lines)
    measure = x1s[int(0.9 * (len(x1s) - 1))]
    rail = Counter(round(l.x0, 1) for l in zone_lines).most_common(1)[0][0]

    raised_ahead: list[set[int]] = [set() for _ in range(len(zone_lines) + 1)]
    for i in range(len(zone_lines) - 1, -1, -1):
        raised_ahead[i] = set(raised_ahead[i + 1])
        lab = detect_label(zone_lines[i])
        if lab and lab.isdigit():
            raised_ahead[i].add(int(lab))

    admitted: dict[int, str] = {}
    highest: int | None = None
    prev: Line | None = None
    lowest_owed = min(owed)
    sequences_started = 1   # the first sequence is free; restarts are not
    for i, line in enumerate(zone_lines):
        lab = detect_label(line)
        if lab is not None:
            if lab.isdigit():
                v = int(lab)
                highest = v if highest is None else max(highest, v)
            prev = line
            continue
        shape = flush_label_shape(line, rail)
        if shape is None:
            prev = line
            continue
        size = line.size
        opens_para = (
            prev is None
            or line.x0 > rail + size * 0.5
            or prev.page != line.page
            or prev.x1 < measure - 2.5 * size
        )
        prev = line
        value = int(shape[0])
        expected = highest + 1 if highest is not None else lowest_owed
        # A DOTTED label ('2.') carrying exactly the owed-next value outranks
        # the opens-paragraph right-edge proxy: a carried tail can end
        # near-full-measure right above note 2 (utahctapp), and the citation
        # twins ('28 P.3d…', '5 U.S.C. §…') are never dotted.
        if not opens_para and not (shape[1].endswith(".") and value == expected):
            continue
        restart = (value == lowest_owed and value not in raised_ahead[i]
                   and highest is not None
                   and sequences_started < owed.get(lowest_owed, 0))
        if value != expected and not restart:
            continue
        if value not in owed or value in raised_ahead[i]:
            continue
        admitted[line.id] = shape[0]
        if restart:
            sequences_started += 1
        highest = value
    return admitted


# --------------------------------------------------------------------------
# the zone resolver
# --------------------------------------------------------------------------

class FootnoteZones:
    """Per-document state + per-page zone decisions."""

    def __init__(self, model: PdfModel, geom: DocGeometry | None,
                 config: FootnoteConfig, court_id: str, trace: Trace,
                 caption_pno: int = 1, is_byline=None):
        self.model = model
        self.geom = geom
        self.config = config
        self.court_id = court_id
        self.trace = trace
        self.caption_pno = caption_pno
        # The court's own byline grammar — the only thing that proves a
        # body-size line below the separator opens the NEXT WRITING
        # rather than being a body-size footnote (ca3 sets notes at body
        # size; ca9 sets a dissent byline under the rule).
        self.is_byline = is_byline or (lambda _t: False)
        self.bottom_keys = repeated_bottom_keys(model)
        self.body_x0 = geom.body_x0 if geom else 72.0
        self.body_size = geom.body_size if geom else 12.0
        self.top_keys = repeated_top_keys(model, self.body_size)
        self._gutters: dict[int, set[int]] = {}
        # Marks the document's own text calls (raised label glyphs anywhere)
        # — the owed set that lets a body-size flush label corroborate a rule
        # (utahctapp's '1. "In reviewing…"' at 12pt on a 12pt body).
        self.owed_marks: set[int] = set()
        for line in model.all_lines():
            for mark in line_marks(line):
                if mark.isdigit():
                    self.owed_marks.add(int(mark))
        self.sigs = self._learn_signatures()

    # ---- shared measurements -------------------------------------------

    def _sep_min_width(self, pm: PageModel) -> float:
        """Scaled to the sheet: a 396pt reporter page draws ~96pt separators
        that a flat 100pt floor silently lost."""
        return max(60.0, pm.width * 0.16)

    @staticmethod
    def _thin_rules(pm: PageModel) -> list[DrawnRule]:
        return pm.h_rules  # collection is already thin-only (h < 2.5)

    def _rule_underlines_text(self, pm: PageModel, rule: DrawnRule) -> bool:
        """A rule inside the LOWER half of a text line's band decorates that
        line. A rule at the TOP of a band is a separator drawn tight over its
        first note — not an underline."""
        for l in pm.lines:
            if ((l.top + l.bottom) / 2 <= rule.top <= l.bottom + 2
                    and l.x0 < rule.x1 and l.x1 > rule.x0):
                return True
        return False

    @staticmethod
    def _shares_row(rule: DrawnRule, pool: list[DrawnRule]) -> bool:
        """A second rule at the same height spanning a different part of the
        measure: a BOX EDGE (table cell, form grid), not a separator."""
        for o in pool:
            if o is rule or abs(o.top - rule.top) > 2:
                continue
            if abs(o.x0 - rule.x0) <= 2 and abs(o.x1 - rule.x1) <= 2:
                continue
            return True
        return False

    def _caption_shelf_bottom(self, pm: PageModel) -> float | None:
        """Bottom of a mid-page caption divider on THIS page, if drawn."""
        mids = [v for v in pm.v_rules
                if v.height >= 40 and pm.width * 0.3 < v.x < pm.width * 0.8]
        return max(v.bottom for v in mids) if mids else None

    def _page_rail(self, pm: PageModel) -> float | None:
        """The page's own left text rail — the leftmost x0 that RECURS among
        full-measure lines (one outdented stray cannot move it)."""
        xs: dict[int, int] = {}
        for l in pm.lines:
            if l.width < pm.width * 0.45:
                continue
            key = round(l.x0)
            xs[key] = xs.get(key, 0) + 1
        recurring = [x for x, hits in xs.items() if hits >= 2]
        return float(min(recurring)) if recurring else None

    def _first_text_top(self, pm: PageModel) -> float:
        tops = [c["top"] for l in pm.lines for c in l.chars
                if (c.get("text") or "").strip()]
        return min(tops) if tops else 0.0

    def _is_band_folio(self, pm: PageModel, line: Line) -> bool:
        """A printed folio: numeric-only, at BODY size (a standalone raised
        label is smaller), in the page's top or bottom band (Connecticut Law
        Journal prints its page number near the top corner)."""
        return (is_folio_text(line.plain)
                and line.size >= self.body_size - 1.5
                and (line.top < pm.height * 0.22 or line.top > pm.height * 0.88))

    def _gutter_ids(self, pm: PageModel) -> set[int]:
        if pm.number not in self._gutters:
            self._gutters[pm.number] = gutter_column_ids(pm)
        return self._gutters[pm.number]

    def _lines_below(self, pm: PageModel, top: float) -> list[Line]:
        """Text lines under ``top``, gutter line-numbers cut by geometry,
        band folios cut by shape+size+position, typed-rule lines dropped,
        trailing furniture popped: none of them may vouch for (or against) a
        separator.

        The boundary is top - 0.5, not top + 1: Connecticut draws its rule ON
        the first note's own band (rule 643.0, note 21's line at 643.1), and
        a +1 fence silently deleted that note."""
        gutters = self._gutter_ids(pm)
        below = sorted((l for l in pm.lines
                        if l.top > top - 0.5 and l.plain.strip()
                        and not is_typed_rule(l.plain.strip(), TYPED_SEP_GLYPHS)
                        and not is_gutter_number(l, self.body_x0, gutters)
                        and not self._is_band_folio(pm, l)),
                       key=lambda l: l.top)
        while below:
            text = below[-1].plain.strip()
            if is_folio_text(text) or (
                    below[-1].top > pm.height * 0.9
                    and furniture_key(text) in self.bottom_keys):
                below.pop()
            else:
                break
        return below

    @staticmethod
    def _line_pitches(lines: list[Line]) -> float | None:
        kept = [l for l in lines if not is_folio_text(l.plain)]
        gaps = [round(b.top - a.top, 2) for a, b in zip(kept, kept[1:])]
        gaps = [g for g in gaps if 2.0 < g < 80.0]
        return median(gaps) if len(gaps) >= 2 else None

    def _single_spaced(self, gap: float) -> bool:
        """Is this line-to-line pitch note-like (tight/single) for THIS
        document? Measured against the document's own body size."""
        return gap <= self.body_size * 1.6

    # ---- corroborators ---------------------------------------------------

    def _is_running_head(self, pm: PageModel, l: Line) -> bool:
        """A learned top-band running head — never evidence for a zone.
        Connecticut's reporter row ('354 Conn. 181   FEBRUARY, 2026   183',
        10.8pt) over its 8pt boxed case name reads as a perfect size drop
        at the head-box rule and swallowed whole syllabus pages."""
        return (l.top / pm.height <= 0.235
                and furniture_key(l.plain.strip()) in self.top_keys)

    def _rule_over_footnotes(self, pm: PageModel, top: float) -> bool:
        """Smaller text below the rule than above it (folio and running-head
        furniture excluded — the folio is set small and sits below every
        rule on the page; a running head proves nothing about notes)."""
        above, below = [], []
        for l in pm.lines:
            if not l.plain.strip() or is_folio_text(l.plain):
                continue
            if self._is_running_head(pm, l):
                continue
            sizes = [c["size"] for c in l.chars if c.get("size")]
            if not sizes:
                continue
            sz = median(sizes)
            if top - 120 <= l.top < top - 2:
                above.append(sz)
            elif top + 2 < l.top <= top + 200:
                below.append(sz)
        if not below:
            return False
        # A PANEL ROSTER right under the rule marks a CAPTION divider, not
        # a separator ('Before:  MALDONADO, P.J., …' — michctapp closes its
        # caption with the same rule shape it draws over footnotes).
        first_below = min(
            (l for l in pm.lines if l.plain.strip() and l.top > top + 2),
            key=lambda l: l.top, default=None)
        if first_below is not None and " ".join(
                first_below.plain.split()).lower().startswith(
                    ("before:", "before ")):
            return False
        if not above:
            # Nothing above the rule -> size proves NOTHING (there is nothing
            # to compare against). A ruled running head (conn prints 'State v.
            # Anthony V.' in 8pt under a page-top rule) satisfies 'smaller
            # below' on every page. A true endnote page opens on a LABEL, and
            # the label steps own that case.
            return False
        # And the text below must be smaller than the DOCUMENT BODY, not
        # merely smaller than what stands above: a caption's bottom divider
        # has 16pt caption above and the 14pt body below (texapp), and that
        # size drop is not a footnote.
        return (median(below) < median(above) - 0.75
                and median(below) < self.body_size - 0.75)

    def _labelled_note_below(self, pm: PageModel, top: float) -> bool:
        """First line under the rule opens a labelled note — or the label is
        drawn late, a raised glyph opening the SECOND line."""
        below = self._lines_below(pm, top)
        if not below:
            return False
        if detect_label(below[0]) is not None:
            return True
        return len(below) > 1 and opens_with_raised_label(below[1])

    def _raised_label_below(self, pm: PageModel, top: float) -> bool:
        """A RAISED label only: pleading-paper line numbers are short numeric
        lines that satisfy the label-only path; a superscripted first glyph
        has no such twin."""
        if not self._labelled_note_below(pm, top):
            return False
        below = self._lines_below(pm, top)
        if not below:
            return False
        return opens_with_raised_label(below[0]) or (
            len(below) > 1 and opens_with_raised_label(below[1]))

    def _flush_labelled_below(self, pm: PageModel, top: float) -> bool:
        """The first line under the rule opens with a BODY-SIZE label whose
        value the document's own text calls. Shape alone has twins ('5 U.S.C.
        § 552'); shape + an owed mark is evidence."""
        below = self._lines_below(pm, top)
        if not below:
            return False
        shape = flush_label_shape(below[0], None)
        return bool(shape and shape[0].isdigit()
                    and int(shape[0]) in self.owed_marks)

    def _outranked_by_signature(self, pm: PageModel, top: float) -> bool:
        """A rule this document has NOT proven as a separator loses to one it
        HAS, drawn lower on the same page and corroborated. bap10 sets its
        headmatter as a ladder of fences: the fence above the panel roster
        (drawn 180-432, or typed as underscores) has note 1 two lines below
        it, which reads as a late-labelled separator — while the shape the
        document proves on twenty pages, its 144pt rule at the body rail,
        stands 95pt further down the same page. Both records that came back
        with a '?' note put the roster or the byline inside a 'zone' that
        opened at a fence."""
        if not self.sigs:
            return False
        return any(r.top > top + 2
                   and (round(r.x0), round(r.width)) in self.sigs
                   and self._labelled_note_below(pm, r.top)
                   for r in self._thin_rules(pm))

    def _body_text_above(self, pm: PageModel, top: float) -> bool:
        """At least one BODY-SIZE text line stands above the rule. The same
        floor _rule_over_footnotes documents: with nothing above there is no
        comparison — a boxed running head (conn's two rules sandwiching an
        8pt case name at the page top) matches the separator's signature on
        geometry alone, and a raised glyph deep in the body below would
        otherwise vouch for a zone that swallows the whole page."""
        return any(l.top < top - 2 and l.plain.strip()
                   and not is_folio_text(l.plain)
                   and not self._is_running_head(pm, l)
                   and l.size >= self.body_size - 0.75
                   for l in pm.lines)

    def _labelled_note_after_carry(self, pm: PageModel, top: float,
                                   carried: bool = False) -> bool:
        """A labelled note below, past a carried-over tail: the tail sits at
        note leading (single-spaced against this document's body). The tail's
        indent proves nothing (it runs both ways across courts).

        ``carried`` says the PREVIOUS page had a zone, so a note was open and
        could run on. Only then may the tail turn its own paragraph — the
        same gate steps 8 and 9 keep. Without it, ca5's caption fence reads
        the roster, the byline and the opening paragraphs as one tail and
        swallows the writing's byline."""
        below = self._lines_below(pm, top)
        for i, line in enumerate(below):
            if detect_label(line) is None:
                shape = flush_label_shape(line, None)
                if not (shape and shape[0].isdigit()
                        and int(shape[0]) in self.owed_marks):
                    continue
            if i == 0:
                return True
            run = below[:i]
            if len(run) <= 1:
                return True
            # The tail keeps NOTE leading, but a carried note may turn its
            # OWN paragraph, and one break at the run's measured pitch is
            # not body spacing. Measuring the run beats a flat multiple of
            # the body size: bap10/irene_moden p11 carries note 27 across a
            # paragraph break of 20.9pt with the flat gate at 20.8, and two
            # labelled notes below it were read as body for want of 0.1pt.
            pitch = self._line_pitches(run) if carried else None
            gate = max(pitch * 1.5, self.body_size * 1.6) if pitch \
                else self.body_size * 1.6
            return all((b.top - a.top) <= gate for a, b in zip(run, run[1:]))
        return False

    # ---- learned signatures ---------------------------------------------

    def _learn_signatures(self) -> dict:
        """(rail, width) signatures THIS document proves are separators —
        seen corroborated on TWO OR MORE pages (measured: one page is not
        enough; pleading fill-in rules break worse than carried tails fix)."""
        sigs: dict[tuple[int, int], set[int]] = {}
        for pm in self.model.pages:
            rules = [r for r in pm.h_rules
                     if r.width >= 40 and r.x0 <= pm.width * 0.5]
            # A page ruled like a spreadsheet is a table; filled-cell boxes
            # count as ink too (uscfc's box-drawn table taught a 336pt
            # "separator" and minted phantom notes labelled '170').
            if len(pm.h_rules) + len(pm.v_rules) > 12:
                continue
            for r in rules:
                if self.config.reject_underlines and self._rule_underlines_text(pm, r):
                    continue
                ok = (self._rule_over_footnotes(pm, r.top)
                      or self._labelled_note_below(pm, r.top)
                      or self._flush_labelled_below(pm, r.top))
                if not ok:
                    continue
                sig = (round(r.x0), round(r.width))
                sigs.setdefault(sig, set()).add(pm.number)
        # …AND WHAT ONE PAGE PROVED IS STILL PROOF, for the one question
        # recurrence cannot answer. A note that runs onto the next page
        # carries NO LABEL and, where the court sets its notes at body size,
        # no size drop either — so the page that needs the signature is the
        # very page that cannot corroborate it, and the two-page floor
        # discards the evidence exactly when it is needed. Kept separately
        # and used only behind the carried-zone gate (step 8.5).
        self.proved = {sig for sig, pages in sigs.items() if pages}
        learned = {sig: pages for sig, pages in sigs.items() if len(pages) > 1}
        if learned:
            self.trace.event("footnote.signatures",
                             ", ".join(f"{w}@{x}×{len(p)}p"
                                       for (x, w), p in learned.items()))
        return learned

    # ---- the chain --------------------------------------------------------

    def page_zone(self, pm: PageModel, prev_had_zone: bool = False) -> Decision:
        point = f"footnote.separator@p{pm.number}"
        chain: list[Evidence] = []
        caption_page = pm.number == self.caption_pno
        x0_max = self.body_x0 + 4
        min_w = self._sep_min_width(pm)
        cap_bot = self._caption_shelf_bottom(pm)
        pool = self._thin_rules(pm)

        def veto(rule: DrawnRule, allow_signed_underline: bool = True) -> str | None:
            """Core vetoes. Returns the veto name or None."""
            if cap_bot is not None and abs(rule.top - cap_bot) <= 4:
                return "caption-shelf"
            if self._shares_row(rule, pool):
                return "box-edge"
            if self._rule_underlines_text(pm, rule):
                sig = (round(rule.x0), round(rule.width))
                if allow_signed_underline and sig in self.sigs:
                    return None  # the document proves this shape as a separator
                if self.config.reject_underlines:
                    return "underline"
            return None

        def decide(value, step: str) -> Decision:
            # BODY-SIZE lines below the separator are not notes: ca9 sets
            # the next writing's byline ('BUMATAY, Circuit Judge,
            # dissenting:') under the rule, above the notes. Footnotes are
            # set SMALLER — advance the zone past any body-size run so the
            # byline stays in the body.
            if value is not None:
                below = sorted((l for l in pm.lines
                                if l.top > value and l.plain.strip()),
                               key=lambda l: l.top)
                moved = value
                for l in below[:3]:
                    if (l.size and l.size >= self.body_size - 0.5
                            and self.is_byline(l.plain.strip())):
                        moved = l.bottom
                    else:
                        break
                if moved != value and any(
                        l.top > moved and l.plain.strip() for l in pm.lines):
                    value = moved
            chain.append(Evidence(step, "candidate", value,
                                  prov=Prov(pm.number)))
            return self.trace.decide(Decision(point, value, step, tuple(chain)))

        # 0 — configured rect (a court FACT: exact rule edges)
        if self.config.sep_rect is not None:
            sx0, sx1 = self.config.sep_rect
            for r in pool:
                if abs(r.x0 - sx0) <= 1 and abs(r.x1 - sx1) <= 1:
                    return decide(r.top, "configured-rect")
            return self.trace.decide(Decision(point, None, "no-zone",
                                              tuple(chain), floor_used=True))

        # 0.5 — court providers: candidates only, core vetoes + corroboration
        for fn in providers_for("footnote.separator", self.court_id):
            for ev in fn(pm=pm, zones=self):
                chain.append(ev)
                if ev.kind != "candidate":
                    continue
                rule = ev.value if isinstance(ev.value, DrawnRule) else None
                top = rule.top if rule else float(ev.value)
                if rule and veto(rule):
                    chain.append(Evidence("core-veto", "veto", ev.value,
                                          why=veto(rule) or ""))
                    continue
                if (self._rule_over_footnotes(pm, top)
                        or self._labelled_note_after_carry(
                            pm, top, prev_had_zone)):
                    return decide(top, f"provider:{ev.step}")

        # 1 — structural finder (body-size-note courts, config opt-in)
        if self.config.structural:
            top = self._structural(pm)
            if top is not None:
                return decide(top, "structural")

        # 2 — the rule, corroborated by SMALLER TEXT below it. The floor is a
        # property of the CAPTION PAGE; on a continuation page a rule is high
        # only because its own footnote is long.
        floor = pm.height * (0.55 if caption_page else 0.10)
        hits = [r for r in pool
                if r.width >= min_w and r.x0 <= x0_max and r.top > floor
                and not veto(r, allow_signed_underline=True)
                and self._rule_over_footnotes(pm, r.top)]
        if hits:
            return decide(min(h.top for h in hits), "rule-over-smaller-text")

        # 3 — the rule, corroborated by a RAISED LABEL below (survives
        # body-size footnotes); width and height floors relaxed on the
        # evidence of the label. Width as the share it always was (60/612).
        floor = (pm.height * 0.25 if caption_page
                 else self._first_text_top(pm))
        relaxed_w = min(min_w, pm.width * (60.0 / 612.0))
        hits = [r for r in pool
                if r.width >= relaxed_w and r.x0 <= x0_max and r.top > floor
                and not veto(r)
                and not self._outranked_by_signature(pm, r.top)
                and self._labelled_note_below(pm, r.top)]
        if hits:
            return decide(min(h.top for h in hits), "rule-over-labelled-note")

        # 3.5 — the rule over a BODY-SIZE flush label the body owes
        # (utahctapp: '1. "In reviewing…"' 12pt on 12pt under a rail rule —
        # no size drop, nothing raised; the owed mark is the evidence).
        hits = [r for r in pool
                if r.width >= relaxed_w and r.x0 <= x0_max and r.top > floor
                and not veto(r)
                and not self._outranked_by_signature(pm, r.top)
                and self._flush_labelled_below(pm, r.top)]
        if hits:
            return decide(min(h.top for h in hits), "rule-over-flush-label")

        # 4 — a separator TYPED as text (underscores / em-dashes; never bare
        # ASCII hyphens — that is how plain-text tables are drawn).
        top = self._typed_text_rule(pm, caption_page)
        if top is not None and not self._outranked_by_signature(pm, top):
            return decide(top, "typed-text-rule")

        # 4.5 — a RULELESS SYMBOL note at the page foot: the line opens on a
        # symbol label ('*This is not an opinion of the full Court…' — ca3
        # draws no rule for its IOP note), sits in the bottom quarter, and
        # stands clear of the text above by more than the page's own pitch.
        top = self._symbol_foot_note(pm)
        if top is not None:
            return decide(top, "symbol-foot-note")

        # 5 — zone by size (config opt-in ONLY; see docs/lessons — every cue
        # is equally true of a reduced-type block quotation).
        if self.config.zone_by_size:
            top = self._zone_by_size(pm, caption_page)
            if top is not None:
                return decide(top, "zone-by-size")

        # 6 — the rule drawn AT AN INDENT (the 2-inch Word default wherever
        # the template put it); a raised label below is the whole test.
        hits = [r for r in pool
                if r.width >= min_w and x0_max < r.x0 <= pm.width * 0.5
                and r.top > pm.height * 0.25
                and not veto(r)
                and not self._outranked_by_signature(pm, r.top)
                and self._raised_label_below(pm, r.top)]
        if hits:
            return decide(min(h.top for h in hits), "indented-rule")

        # 7 — the document's own signature; recurrence narrows, a labelled
        # note (past a carried tail) still confirms.
        if self.sigs:
            tops = [r.top for r in pool
                    if (round(r.x0), round(r.width)) in self.sigs
                    and not veto(r)
                    and self._body_text_above(pm, r.top)
                    and self._labelled_note_after_carry(
                        pm, r.top, prev_had_zone)]
            if tops:
                return decide(min(tops), "learned-signature")

        # 8 — the LEADING changes at the rule (a carried tail has no label
        # and no size drop). A tail can only be CARRIED from a page that had
        # a zone — without that, a caption-continuation page's spaced-out
        # rows over a single-spaced roster read as this exact pitch profile
        # (coloctapp p2 swallowed 250pt of headmatter this way).
        if not caption_page and prev_had_zone:
            top = self._tighter_leading(pm, min_w, x0_max)
            if top is not None:
                return decide(top, "tighter-leading")

        # 8.5 — THE DOCUMENT'S OWN SEPARATOR, drawn again on a page that
        # carries a note. A tail that merely FINISHES a note has no label and
        # no size drop, and the leading test above can be masked by whatever
        # the page sets between the body and the rule: gactapp's clerk prints
        # a certificate there, single-spaced at 11pt against a 14pt body, so
        # the six lines above the rule already read as note leading and the
        # change the tail proves is invisible (in_re_estate_of_tien_thi_davis:
        # note 1 came back with a LABEL AND NO TEXT, and its second half
        # rendered as a paragraph of the order — the user, 2026-08-20: 'the
        # footnote bleeds to page 2 but its not recognized as a footnote').
        #
        # What answers it is the rule itself: 143.9pt at the rail, the same
        # separator this document already proved on the page before. The
        # prev-zone gate is the one steps 8 and 9 keep — a note must be OPEN
        # for a tail to be carried into.
        if not caption_page and prev_had_zone and getattr(self, "proved", None):
            # AT THE RAIL, like every other step here. A separator is drawn
            # at the measure's left edge; a rule CENTRED on the page is a
            # band divider, and utah draws two of them (90pt at x0 261.0)
            # between its counsel block and its byline band. Matched without
            # the rail test, the higher one opened a zone at 0.25 of the page
            # and took the byline into it — anderson_v._hon._bates lost its
            # author and typed 'order'.
            tops = [r.top for r in pool
                    if r.x0 <= x0_max
                    and (round(r.x0), round(r.width)) in self.proved
                    and not veto(r)
                    and self._body_text_above(pm, r.top)
                    and any(l.top > r.top + 1 and l.plain.strip()
                            for l in pm.lines)]
            if tops:
                return decide(min(tops), "carried-tail-signature")

        # 9 — a RULELESS carried tail: the previous page had a zone, and this
        # page's foot carries a run of sub-body-size single-spaced lines set
        # clear below the body (tenn draws no separator when a note merely
        # finishes). The prev-zone gate is what keeps kan's reduced-type
        # block quotations out — those pages have no zone behind them.
        if not caption_page and prev_had_zone:
            top = self._trailing_small_run(pm)
            if top is not None:
                return decide(top, "carried-tail-size")

        # floor: no zone on this page — a recorded decision, not a fall-through
        return self.trace.decide(Decision(point, None, "no-zone",
                                          tuple(chain), floor_used=True))

    # ---- step implementations --------------------------------------------

    def _structural(self, pm: PageModel) -> float | None:
        """Thin rule at the body's left margin, clear of any text band, with
        footnote matter below: a raised label, or single-spaced text where
        the body is double-spaced."""
        cutoff = pm.height * 0.45
        good = []
        for r in pm.h_rules:
            if r.width < 60 or r.x0 >= pm.width * 0.35 or r.top <= cutoff:
                continue
            if any(l.top - 1 <= r.top <= l.bottom + 2
                   and l.x0 < r.x1 and l.x1 > r.x0 for l in pm.lines):
                continue
            below = self._lines_below(pm, r.top)[:4]
            if not below:
                continue
            first = [c for c in below[0].chars if (c.get("text") or "").strip()]
            label = first and round(first[0].get("size", 0)) <= round(self.body_size) - 3
            gaps = [b.top - a.top for a, b in zip(below, below[1:])]
            single = gaps and gaps[0] < self.body_size * 1.4
            if label or single:
                good.append(r.top)
        return min(good) if good else None

    def _typed_text_rule(self, pm: PageModel, caption_page: bool) -> float | None:
        cutoff = pm.height * (0.5 if caption_page else 0.10)
        configured = self.config.text_min_width
        best = None
        for l in pm.lines:
            t = l.plain.strip()
            if len(t) < 6 or not is_typed_rule(t, TYPED_SEP_ADMIT_GLYPHS):
                continue
            if l.top <= cutoff:
                continue
            if configured is not None:
                if l.width < configured:
                    continue
            elif not self._labelled_note_after_carry(pm, l.top):
                continue
            if best is None or l.top < best:
                best = l.top
        return best

    def _zone_by_size(self, pm: PageModel, caption_page: bool) -> float | None:
        """Type drops, first line carries a label, run reaches the page foot.
        OPT-IN with measurements — kan's 11pt block quotes satisfy every cue."""
        lines = sorted((l for l in pm.lines if l.plain.strip()),
                       key=lambda l: l.top)
        if len(lines) < 2:
            return None
        sizes = [l.size for l in lines]
        from collections import Counter
        common = Counter(sizes).most_common()
        top_hits = max((hits for _s, hits in common if hits >= 3), default=0)
        if not top_hits:
            return None
        body = max(s for s, hits in common if hits == top_hits)
        start = None
        for i in range(len(lines) - 1, -1, -1):
            if is_folio_text(lines[i].plain):
                continue
            if sizes[i] <= body - 0.5:
                start = i
            else:
                break
        if start is None or start == 0:
            return self._labelled_size_drop(lines, sizes)
        if detect_label(lines[start]) is None:
            if caption_page:
                return None
            last = max((l for l in lines[start:] if not is_folio_text(l.plain)),
                       key=lambda l: l.bottom, default=None)
            if last is None or last.bottom < pm.height * 0.82:
                return None
        return lines[start].top - 1

    def _labelled_size_drop(self, lines: list[Line],
                            sizes: list[float]) -> float | None:
        idx = [i for i in range(len(lines)) if not is_folio_text(lines[i].plain)]
        if len(idx) < 4:
            return None
        note = sizes[idx[-1]]
        start = None
        for i in reversed(idx):
            if sizes[i] <= note + 0.25:
                start = i
            else:
                break
        if start is None:
            return None
        above = [sizes[i] for i in idx if i < start]
        if len(above) < 3 or min(above) <= note + 0.5:
            return None
        if detect_label(lines[start]) is None:
            return None
        return lines[start].top - 1

    def _symbol_foot_note(self, pm: PageModel) -> float | None:
        """A symbol-labelled line in the page's bottom quarter with a gap
        above it exceeding the page's own pitch — a ruleless star note.
        Symbols only: digit labels have rule- and bookkeeping-backed steps,
        and a bare numeral at the foot is a folio's twin."""
        lines = sorted((l for l in pm.lines if l.plain.strip()
                        and not is_folio_text(l.plain)
                        and not self._is_band_folio(pm, l)),
                       key=lambda l: l.top)
        if len(lines) < 3:
            return None
        pitch = self._line_pitches(lines)
        if pitch is None:
            return None
        for i, l in enumerate(lines):
            if i == 0 or l.top < pm.height * 0.75:
                continue
            # The label must OPEN A NOTE ('*This is not an opinion…') — a
            # bare star is a dinkus piece, and detect_label's short-label
            # path would take it.
            if _symbol_label_at_head(l) is None:
                continue
            if l.top - lines[i - 1].top >= pitch * 1.3:
                return l.top - 1
        return None

    def _trailing_small_run(self, pm: PageModel) -> float | None:
        """Top of a trailing run of sub-body-size, single-spaced lines that
        reaches the page foot with body-size text standing clear above it —
        a carried footnote tail on a page whose court draws no rule for it."""
        lines = sorted((l for l in pm.lines if l.plain.strip()
                        and not is_folio_text(l.plain)
                        and not self._is_band_folio(pm, l)
                        and not is_gutter_number(l, self.body_x0,
                                                 self._gutter_ids(pm))),
                       key=lambda l: l.top)
        if len(lines) < 2:
            return None
        run: list[Line] = []
        for line in reversed(lines):
            if line.size <= self.body_size - 1.5:
                run.insert(0, line)
            else:
                break
        if not run or run is lines:
            return None
        if run[-1].bottom < pm.height * 0.8:
            return None                      # must reach the page foot
        above = [l for l in lines if l.top < run[0].top]
        if not above or above[-1].size <= self.body_size - 1.5:
            return None                      # body-size text must stand above
        if run[0].top - above[-1].top < self.body_size * 1.5:
            return None                      # set clear below the body
        if len(run) > 1 and not all(self._single_spaced(b.top - a.top)
                                    for a, b in zip(run, run[1:])):
            return None
        return run[0].top - 1

    def _tighter_leading(self, pm: PageModel, min_w: float,
                         x0_max: float) -> float | None:
        lines = sorted((l for l in pm.lines if l.plain.strip()),
                       key=lambda l: l.top)
        if len(lines) < 6:
            return None
        best = None
        for r in pm.h_rules:
            if r.width < min_w or r.x0 > x0_max or r.top < pm.height * 0.25:
                continue
            if self._rule_underlines_text(pm, r):
                continue
            above = self._line_pitches([l for l in lines if l.top < r.top - 1][-6:])
            below = self._line_pitches([l for l in lines if l.top > r.top + 1][:6])
            if above is None or below is None:
                continue
            if below <= above * 0.75 and (best is None or r.top < best):
                best = r.top
        return best


# --------------------------------------------------------------------------
# label-sequence extraction (assembly proper lands with the body builder;
# this is what the 2,124-file truth set validates)
# --------------------------------------------------------------------------

def document_labels(model: PdfModel, geom: DocGeometry | None,
                    config: FootnoteConfig, court_id: str,
                    trace: Trace, caption_pno: int = 1) -> list[str]:
    zones = FootnoteZones(model, geom, config, court_id, trace, caption_pno)

    # Zone lines per page (band folios / gutter numbers / trailing furniture
    # already cut by _lines_below), plus the body's own marks — the owed set
    # the flush-label bookkeeping needs.
    zone_lines: list[Line] = []
    zone_tops: dict[int, float] = {}
    prev_had = False
    for pm in model.pages:
        decision = zones.page_zone(pm, prev_had_zone=prev_had)
        prev_had = decision.value is not None
        if decision.value is None:
            continue
        zone_tops[pm.number] = decision.value
        zone_lines.extend(zones._lines_below(pm, decision.value))

    owed: dict[int, int] = {}
    for pm in model.pages:
        cut = zone_tops.get(pm.number)
        for line in pm.lines:
            if cut is not None and line.top > cut:
                continue
            for mark in line_marks(line):
                if mark.isdigit():
                    owed[int(mark)] = owed.get(int(mark), 0) + 1

    flush = admit_flush_labels(zone_lines, owed)

    labels: list[str] = []
    for line in zone_lines:
        lab = detect_label(line)
        if lab is None:
            lab = flush.get(line.id)
        if lab is not None:
            labels.append(lab)
    if config.dedupe_labels:
        out = []
        for lab in labels:
            if not out or out[-1] != lab:
                out.append(lab)
        labels = out
    return labels
