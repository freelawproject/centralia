"""Body assembly: segments + zones + bylines -> opinions, footnotes,
signature, trailer, residual.

Writings split at byline segments; footnotes attach to the writing that owns
their page (mark-based reattribution refines later). Paragraph text is the
measured plain rebuild for now — the inline-markup builder replaces it in the
render pass without changing any of this structure.
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field

from .. import model as m
from ..geometry import DocGeometry
from ..pdfio.model import Line
from .bylines import (_DELIVER_VERBS, BylineParser,
                      conformed_signature_author, normalize_opinion_type)
from .footnotes import (FootnoteZones, admit_flush_labels, detect_label,
                        line_marks)
from .segments import Segment, Segmenter


def _join(lines: list[Line], vocab: set[str] | None) -> str:
    """Join wrapped lines (inline markup preserved); rejoin a line-break
    hyphen only when the document's own vocabulary proves the unbroken word
    (never from the signal being disambiguated)."""
    from .footnotes import line_markup
    parts: list[str] = []
    _pg = None
    for line in lines:
        text = line_markup(line).strip()
        if not text:
            continue
        # A paragraph that CROSSES a page turn carries the turn INSIDE it:
        # ca1's page 3 opens 'son.  In November 2022…' mid-sentence, and a
        # marker placed at the next paragraph would misreport the page.
        if _pg is not None and line.page != _pg:
            parts.append(f'<pagenumber value="{line.page}"/>')
        _pg = line.page
        if parts and parts[-1].endswith("-") and vocab:
            head = parts[-1]
            word = []
            for ch in reversed(head[:-1]):
                if ch.isalpha() or ch in "’'":
                    word.append(ch)
                else:
                    break
            first = text.split()[0].strip("“”\"'’‘()[]{}.,;:!?").lower() if text.split() else ""
            joined = ("".join(reversed(word)) + first).lower()
            if word and joined in vocab:
                parts[-1] = head[:-1] + text.split()[0]
                rest = text.split(maxsplit=1)
                text = rest[1] if len(rest) > 1 else ""
                if not text:
                    continue
        # A line-break hyphen never earns a space: when the vocabulary
        # can't prove the unbroken word, keep the hyphen and WELD the wrap
        # ('non-' + 'compete' -> 'non-compete', never 'non- compete').
        if parts and parts[-1].endswith("-") and text:
            parts[-1] = parts[-1] + text
            continue
        parts.append(text)
    return " ".join(parts)


_SEAM = re.compile(r"(\s*)</(strong|em|u)>(\s*)<\2>(\s*)")


# THE PAPER NAMING ITSELF, in the closed set core already uses to find
# where an announcement byline's writing begins.
_DOC_BANNERS = ("OPINION", "ORDER", "MEMORANDUMOPINION")


def _mend_seams(markup: str) -> str:
    """Adjacent identical emphasis runs re-form as ONE run, keeping at most
    the single space the join put between them. A heading set as a
    column-split row ('III.' beside 'The Appeal') otherwise carries the
    label's own trailing space AND the join's: '<strong>III. </strong>
    <strong>The Appeal</strong>' — two spaces where the page prints one."""
    return _SEAM.sub(
        lambda mo: " " if (mo.group(1) or mo.group(3) or mo.group(4)) else "",
        markup)


def _prov(lines: list[Line]) -> m.Prov:
    return m.Prov(lines[0].page if lines else 1,
                  tuple(l.id for l in lines))


@dataclass
class Assembled:
    opinions: list[m.Opinion] = field(default_factory=list)
    consumed_ids: set = field(default_factory=set)   # separators etc.
    dropped: list = field(default_factory=list)      # m.Dropped (attestation)
    headmatter_segments: list[Segment] = field(default_factory=list)
    headmatter_footnotes: list[m.Footnote] = field(default_factory=list)
    signature: list = field(default_factory=list)
    trailer: list = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


_OUTLINE = re.compile(r"^(?:[IVXLCDM]{1,5}|[A-Za-z]|\d{1,2})\.?$")

# A BULLET IS AN OPENER AND ITS OWN ITEM. A court that sets a bulleted list
# indents the item's first line to the paragraph indent and its RUNOVERS
# deeper still — alnd/179841.412.0 rules its conclusion that way: the item
# opens at x0 122.4 over a body rail of 86.4, and runs over at 140.4. The
# indent test cannot see it: the row does not return to the rail on the next
# line (the runover is deeper), so no bullet opened anything and item ran
# into item — 'DENIES TVA's motion … on Plaintiffs' / claims (doc. 314); •
# DENIES WITHOUT PREJUDICE …' (the user, 2026-08-23: 'whitespace is also
# note respected in places? like these lists?'). The glyph is the landmark,
# and it is the same glyph in every court that prints one.
_BULLET = re.compile(r"^[\u2022\u25CF\u25AA\u2023\u25E6\u00B7\u2043]\s*\S")


_BULLET_LEAD = re.compile(
    r"^(?:<[^>]+>)*[\u2022\u25CF\u25AA\u2023\u25E6\u00B7\u2043]\s*")


def _is_bullet_row(line) -> bool:
    return bool(_BULLET.match(" ".join((line.plain or "").split())))


# A PARAGRAPH NUMBER OPENS A PARAGRAPH. A court that numbers its paragraphs
# sets the number at the RAIL and its first line of text indented beside it,
# which is the opposite of an indent — so the indent test below never fires
# and every numbered paragraph joined the one above it. Measured on miss:
# ¶ markers buried mid-paragraph on 41 of 50 records, up to 82 in one file.
# The glyph is the landmark and it is the same in every court that uses it
# ('¶1.', '¶ 2', '[¶4]'); a marker that is only part of a longer line is not
# matched, because there the page has already joined it to its own text.
# The mark may stand alone as its own piece ('¶1.' at x0 72 beside its text at
# 108) or open the line it belongs to ('¶10. When investigators asked…'),
# depending on how wide a gap pdfio saw. Both are the same thing to a reader,
# so the rule is 'the line BEGINS with the mark'.
_PARA_MARK = re.compile(r"^\[?\s*¶+\s*\d+\s*[.\)\]]?(?:\s|$)")


def _is_para_mark(line) -> bool:
    return bool(_PARA_MARK.match(" ".join((line.plain or "").split())))


def _is_outline_label(line, segmenter) -> bool:
    """An OUTLINE LABEL is a hierarchy mark, not prose: a lone 'I' /
    'A' / '1' / 'a' set centered on the page axis between paragraphs.
    It is what the page uses instead of a worded heading, and run into
    the text it renders as a stray digit ('I A' on one line where the
    page shows two centered rows). Geometry decides: one token,
    centered, a few points wide against a 300pt measure — page
    furniture at the head and foot is already gone by here, so a mark
    this small mid-measure is a label. The hierarchy runs
    I / A / 1 / a, so the fourth level is LOWER case and a label
    grammar stopping at 'A' loses it (scotus stacks '2' over 'a').
    """
    text = " ".join(line.plain.split()).strip()
    if not _OUTLINE.match(text):
        return False
    column = getattr(getattr(segmenter, "geom", None), "column", None)
    if (line.x1 - line.x0) > 0.12 * (column or 300.0):
        return False
    cx = (line.x0 + line.x1) / 2
    return abs(cx - segmenter.page_width / 2) < 25


# A HANGING INDENT. A court that numbers what it ORDERS sets the marker in
# its own column and the item's text out beside it, and the item's RUNOVERS
# come back to the body rail underneath both:
#
#     1.  Kelly's motion for new trial and for recusal of the undersigned
#     District Judge (doc. 5) is DENIED;                 <- the runover
#
# The marker is not flow: it never wraps, nothing returns to it, and counting
# it as a left edge moves the measured rail out to the marker's column — at
# which point every runover reads as a fresh paragraph and every item head
# reads as a quotation. Measured on almd, where the last page of a decretal
# order came back as five paragraphs broken mid-sentence.
# …AND A COURT MAY PUT THE NUMBER IN PARENTHESES. `_OUTLINE` is the OUTLINE
# hierarchy — 'I' over 'A' over '1' over 'a', centred between paragraphs — and
# a decretal list is a different thing set a different way: pamd/…145277.24.0
# numbers what it orders '(1)' '(2)' '(3)' at x108 with the item's text and
# its runovers at x144. Unmatched, each marker voted as a left edge and the
# consequence is the one written above: item (1) came out a QUOTATION and
# items (2) and (3) welded into one paragraph (the user, 2026-08-25: 'the
# whtieapce should be better rpsesented in teh body text'). The geometry
# tests below are what make the row a marker; this only has to spell the
# forms a court uses to write one.
_LIST_MARK = re.compile(r"^\(?(?:[IVXLCDM]{1,5}|[A-Za-z]|\d{1,2})[.)]?$", re.I)


def _is_list_marker(line, lines, i: int, left: float | None = None) -> bool:
    """Is ``line`` a lone list marker with its item's text beside it?

    A MARKER STANDS AT THE LEFT OF THE MEASURE. Without that bound the test
    matches a page FOLIO sitting beside its running head — utahctapp sets the
    page number at x 303 next to '2026 UT App 83' on every page, 47 of them
    in one opinion — and letting those vote (or rather, stopping them from
    voting) moved the measured rail and merged real paragraphs: five of six
    pinned records lost a ¶ each, and state_v._shay lost four."""
    text = " ".join((line.plain or "").split())
    if not _LIST_MARK.match(text):
        return False
    if left is not None and line.x0 > left + 60:
        return False
    nxt = lines[i + 1] if i + 1 < len(lines) else None
    return (nxt is not None and abs(nxt.top - line.top) < 2
            and nxt.page == line.page and nxt.x0 > line.x1)


# AN ITEM THAT CARRIES ITS OWN NUMBER. `_is_list_marker` reads the form where
# the court sets the number in a slot of its own with the item beside it; a
# district that types '1.' and the sentence on ONE row states the same thing
# and matched nothing, so consecutive items welded into a paragraph: flmd/
# …459104.10.0's four numbered directions came back as two blocks, and wiwd/
# …55879.12.0's as '2. All pending motions are DENIED as moot. 3. Petitioner
# is DENIED … 4. The clerk … shall enter judgment' (the user, 2026-08-25:
# 'this stuff needs to retain its spacing to retain meaning'). A wrapped line
# does not open on a number and a stop.
_INLINE_ITEM = re.compile(r"^(?:<[^>]+>)*\(?\d{1,2}[.)]\s+\S")

# WHAT A COURT SETS ON A LINE OF ITS OWN TO CLOSE. The date it signs under,
# the words it orders by, the clerk's entry line — each stands alone on the
# page and each was welded into the sentence above it, which finishes its own
# sentence and so passes every test the walk makes: pawd/…228376.1094.0 came
# back 'An appropriate order follows. Dated: July 8, 2026' and tned/
# …107949.169.0 ran '… [Doc. 123]. SO ORDERED.' together with 'ENTER:' (the
# user, 2026-08-25: 'the date needs to be its own line when its its own line
# at the end of the document'). Matched only at the HEAD of a row, so the
# same words inside a sentence are untouched.
_CLOSING_ROW = re.compile(
    r"^(?:<[^>]+>)*\s*(?:dated?\s*:|date\s*:|entered?\s*:|enter\s*:"
    r"|so\s+ordered|it\s+is\s+so\s+ordered|by\s+the\s+court)\b", re.I)

# HOW MUCH OF A GAP IS A BLANK LINE, in the run's own leading. One step is a
# wrap and two is a blank line, so the cut goes between them.
_AIR_OPENS = 1.5


def _row_lead(lines) -> float:
    """The leading this run is set on: the SMALLEST step between its rows.

    NOT the median, and this is the whole difference. A decretal order sets
    each item as one or two rows with a blank line between — pamd/…145277.24.0
    steps 33.6, 16.9, 16.8, 33.6, 33.7 — so the median step IS the
    leading-plus-air and a median-based reader would find air nowhere on the
    page. A page cannot set two rows closer together than its leading, so the
    smallest real step is it. Steps under four fifths of the type size are
    not two rows at all (a superscript, a split piece) and do not vote.
    """
    sizes = sorted(l.size for l in lines if getattr(l, "size", 0))
    floor = (sizes[len(sizes) // 2] * 0.8) if sizes else 4.0
    tops: list = []
    for l in lines:
        if not tops or l.page != tops[-1][0] or l.top > tops[-1][1] + 2.0:
            tops.append((l.page, l.top))
    steps = [b[1] - a[1] for a, b in zip(tops, tops[1:])
             if a[0] == b[0] and b[1] - a[1] >= floor]
    return min(steps) if steps else 0.0


_SENTENCE_END = (".", ":", ";", "?", "!", "\u201d", '"', ")", "]")


def _finished(text: str) -> bool:
    """Has this row finished what it was saying?"""
    t = (text or "").strip()
    return not t or t.endswith(_SENTENCE_END)


def _weld_unspaced(segs: list, lead: float, parser=None) -> list:
    """Rejoin a segment the page never separated from the one above it.

    A CHANGE OF WEIGHT IS NOT A CHANGE OF BLOCK. pamd/…145277.24.0 closes the
    first thing it orders with one bold word — '… under the Social Security
    Act is' / 'AFFIRMED;' — and the weight alone cut the word into a segment
    of its own, where the short-bold-row test typed it a HEADING and the
    sentence lost its verb (the user, 2026-08-25: 'affirmed shouldnt be its
    own line! its part of hte sentetnece').
    Three things have to agree before a segment is welded back, and all three
    are the page's own: it stands one leading under the row above with no
    blank line between them, that row has not finished its sentence, and it
    opens on the same left edge the row above ran over to. A heading never
    completes the sentence above it, and the page never sets one flush with
    the prose it heads and no air around it.
    """
    if not lead:
        return segs

    def _pair_lead(prev) -> float:
        """The leading of the run being welded TO, where it states one.

        The document figure is the smallest step anywhere on the sheet, and
        a sheet has more than one leading: nmd/…562552.14.0 sets its body on
        32.2 while something in its front matter steps 16.1, so the
        document threshold came out 24.2 — below the body's own single
        spacing — and the weld could never fire on a body row at all. Its
        order ended '… is hereby' with 'continued to October 27, 2026.' cut
        off beneath it as a heading (the user, 2026-08-25: 'why is the last
        line here separated?'). A run of three rows or more has already
        said what leading it is set on.
        """
        _r: list = []
        for _l in prev.lines:
            if not _r or _l.page != _r[-1][0] or _l.top > _r[-1][1] + 2.0:
                _r.append((_l.page, _l.top))
        return _row_lead(prev.lines) if len(_r) >= 3 else lead

    out: list = []
    for seg in segs:
        prev = out[-1] if out else None
        _lead = _pair_lead(prev) if prev is not None and prev.lines else lead
        if (prev is not None and seg.lines and prev.lines
                and seg.kind not in ("table", "separator", "notice")
                and prev.kind not in ("table", "separator", "notice")
                and seg.lines[0].page == prev.lines[-1].page
                and 0 < seg.lines[0].top - prev.lines[-1].top < _lead * _AIR_OPENS
                and not _finished(prev.lines[-1].plain)
                and abs(seg.lines[0].x0 - prev.lines[-1].x0) <= 2.0
                # …BUT A BYLINE IS NEVER WELDED TO THE ROW ABOVE IT. This
                # pass runs before the bylines are read precisely so a stray
                # row cannot open a writing — but a row that NAMES A JUDGE
                # and states what they did is not stray, and the three tests
                # above are all satisfied by a running head: ca2's
                # havlish_v._taliban repeats '23-258 (L); 23-354 (L)' over
                # 'Havlish v. Taliban; Aliganga v. Taliban' at the head of
                # every sheet, which finishes no sentence and sets the same
                # left edge as the text beneath it. On page 5 that head
                # swallowed 'NARDINI, Circuit Judge, joined by LOHIER,
                # Circuit Judge, concurring in the denial of rehearing en
                # banc:' into one blockquote, the byline never opened a
                # writing, and the record came back three writings instead
                # of four — the concurrence gone (the user, 2026-08-25: 'did
                # lose a concurrence'). The segmenter had already cut it
                # correctly; this pass undid the cut.
                and not (parser is not None
                         and parser.parse(seg.lines[0].plain.strip()))):
            prev.lines.extend(seg.lines)
            continue
        out.append(seg)
    return out


def _mode_x0(lines) -> float | None:
    """The x0 the flow RETURNS to: the most common left edge, ties toward the
    left. One measurement, used by the paragraph walk and by the quotation
    split, so the two cannot disagree about where the rail is. None when
    there is nothing to measure — never 0.0, which a caller would read as an
    edge (index 0 is falsy, and that trap has cost this project a day)."""
    xs: dict[float, int] = {}
    _left = min((l.x0 for l in lines), default=None)
    for i, l in enumerate(lines):
        if _is_list_marker(l, lines, i, _left):
            continue                       # a marker is not flow
        k = round(l.x0, 1)
        xs[k] = xs.get(k, 0) + 1
    if not xs:
        return None
    return max(xs.items(), key=lambda kv: (kv[1], -kv[0]))[0]


# A LEADER TABLE IS A TABLE DRAWN WITH DOTS. A contents list, or the New
# York Surrogate's list of papers read, sets a label at the rail, a run of
# leader dots, and a number flush right — a two-column row whose rule is
# punctuation. `find_grids` cannot see it (nysurct/matter_of_levine_calleo
# reports 0 tables on the page that carries two of these lists), and because
# every row sits AT the rail with no indent, the paragraph builder read the
# whole list as one continuation: eleven rows and 1,100 leader dots welded
# into a single paragraph, and the court's own next sentence — 'The following
# papers were read in determining petitioner's motion filed on November 18,
# 2025:' — welded onto the end of it (the user, 2026-08-21).
#
# THE TRAILING NUMBER IS WHAT MAKES IT A ROW, not the dots. Measured over the
# corpus: 75 leader runs in 9 files, and they are two different things. Six
# files set label/dots/number — cadc's 'I. Background ……… 5', utd and iand's
# brief contents, nysupct's identical PAPERS list, sd's 'JENSEN, Chief Justice
# ……… 1'. The other two are not tables at all and MUST NOT be touched:
# fla/in_re_amendments prints leaders as a FILL-IN BLANK inside a form it is
# amending ('Florida Bar No. ....................', nothing after the dots),
# and prsupreme/de_la_cruz uses them as an ELLIPSIS OF OMITTED STATUTORY TEXT
# inside a quotation ('… debe responder. ........ Lo son igualmente'), where
# prose follows. Requiring a bare number after the dots admits the six and
# refuses the two.
#
# THE DOTS MAY BE SPACED. nj sets its Tables of Contents '. . . . . . . 5' and
# a solid-run pattern never saw them, so the majority of
# state_v._darryl_nieves opened on its own contents (the user, 2026-08-21).
# Widening to a spaced run is safe for the same reason the solid one was:
# measured, 82 spaced runs of 8+ dots live in 30 files, and outside nj's two
# contents pages NONE is a table — ohioctapp closes 16 opinions with
# '. . . . . . .' as an ornament after the disposition, pamd draws its
# pleading rail in dots, kanctapp's is a quotation ellipsis. Not one carries a
# trailing number, so the number test refuses them all. The 8-DOT FLOOR is
# what keeps a spaced ELLIPSIS ('. . .', which this very opinion uses) out.
# The same row found ANYWHERE in a joined string, so a paragraph that welded
# several of them can be taken apart. Two or more are required before a
# paragraph is split (see _leader_split): prsupreme's ellipsis produces
# exactly one match and must stay prose.
_LEADER_SCAN = re.compile(
    r"(?P<label>\S[^.]*?(?:\.[^.]+?)*?)\s*(?:\.[  ]?){8,}\s*"
    r"(?P<num>[0-9IVXivx]+(?:\s*[-–—]\s*[0-9IVXivx]+)?)(?=\s|$)")
_LEADER_ROW = re.compile(
    r"^(?P<label>.*?\S)\s*(?:\.[  ]?){8,}\s*"
    # The number may be a range ('3-4', '223-251') and it may be OCR'd:
    # levine_calleo's page 2 reads 'Petition ……… I' for 1, so a roman-looking
    # token counts. Bounded to 12 characters, which no sentence opener is.
    r"(?P<num>[0-9IVXivx]+(?:\s*[-–—]\s*[0-9IVXivx]+)?)\.?$")


def _leader_text_cells(text: str) -> tuple[str, str] | None:
    """``(label, number)`` when a string is one row of a leader table."""
    text = " ".join((text or "").split())
    got = _LEADER_ROW.match(text)
    if not got or len(got.group("num")) > 12:
        return None
    label = got.group("label").rstrip(".-– ")
    return (label, got.group("num")) if label else None


def _leader_split(text: str) -> tuple[list[tuple[str, str]], str] | None:
    """A paragraph that WELDED several leader rows -> its rows, plus whatever
    prose was welded on after them.

    Required because the leader rows of one list do not all reach the same
    builder: utd's brief contents folded 1 row of 14 and iand's 3 of 13 from
    the single-row test alone, the rest arriving already joined. Two or more
    rows must be found before a paragraph is taken apart — prsupreme's
    quotation ellipsis matches exactly once and stays prose — and the rows
    must account for most of the text, so a sentence that merely contains a
    leader run is never shredded."""
    text = " ".join((text or "").split())
    hits = [mm for mm in _LEADER_SCAN.finditer(text)
            if len(mm.group("num")) <= 12]
    if len(hits) < 2:
        return None
    covered = sum(mm.end() - mm.start() for mm in hits)
    if covered < 0.6 * len(text):
        return None
    # EVERY CHARACTER SURVIVES, BY CONSTRUCTION. Taking only the matched
    # spans would silently drop whatever sat BETWEEN two rows, and nothing
    # downstream could see it: the pieces inherit the parent's prov, so the
    # residual worklist still counts those lines as placed. So the text is
    # walked, and the gaps are emitted as pieces of their own.
    pieces: list[str] = []
    pos = 0
    for mm in hits:
        gap = text[pos:mm.start()].strip()
        if gap:
            pieces.append(gap)
        row = text[mm.start():mm.end()].strip()
        if not row:
            return None
        pieces.append(row)
        pos = mm.end()
    return pieces, text[pos:].strip()


# HOW MANY LEADER ROWS MAKE A CONTENTS LIST. Two: one row is an ornament or
# a quotation's ellipsis (see `_LEADER_SCAN`), a pair is a list.
_LEADER_SEG_MIN = 2


def _leader_cells(line) -> tuple[str, str] | None:
    """``(label, number)`` when a LINE is one row of a leader table."""
    return _leader_text_cells(line.plain or "")


def _split_leader_rows(blocks: list) -> list:
    """A Paragraph that WELDED several leader rows -> one Paragraph per row.

    THE LEADER DOTS STAY. An earlier cut of this pass folded the rows into a
    TableBlock; that was invention (the user, 2026-08-21). The page prints
    prose with leader dots, declares no table, and a TableBlock — which also
    reaches the casebody XML — asserts a two-column structure the document
    never made, on a guess about where the label ends and the number begins.
    The dots are the page's own ink and they say what the leader says: this
    label goes with that number. They are reproduced as printed.

    What was actually broken was WELDING, and that is all this fixes.
    nysurct/matter_of_levine_calleo ran eleven rows and some 1,100 leader dots
    into one paragraph and swallowed the court's own next sentence — 'The
    following papers were read in determining petitioner's motion filed on
    November 18, 2025:' — at the end of it. `_paragraph_blocks` keeps a leader
    row from joining its neighbours; this pass exists because the segmenter is
    not the only builder, and a row that stands alone between two zones
    arrives here already joined to its siblings."""
    out: list = []
    for b in blocks:
        if isinstance(b, m.Paragraph):
            split = _leader_split(getattr(b, "text", "") or "")
            if split is not None:
                rows, tail = split
                for row in rows:
                    out.append(m.Paragraph(text=row, prov=b.prov))
                if tail:
                    out.append(m.Paragraph(text=tail, prov=b.prov))
                continue
        out.append(b)
    return out


def _paragraph_blocks(seg: Segment, segmenter: Segmenter,
                      vocab: set[str] | None) -> list:
    """A body segment -> Paragraphs, split where a line leaves the RUNOVER
    edge — the x0 the flow returns to line after line. The edge is the MODE,
    not the minimum: a court may open a paragraph by OUTDENTING (scotus sets
    'Held:' 9pt to the LEFT of the syllabus runovers), and a minimum can
    never be exceeded from below, so a min-based rail is blind to half the
    openers a page prints."""
    step = getattr(segmenter, "para_indent_min", 12.0)
    _r = _mode_x0(seg.lines)
    rail = segmenter.rail if _r is None else _r
    # A run set out past TWICE the indent is a block QUOTATION, not a
    # paragraph — scotus sets quotations at body size on the body lead, so
    # the indent is the only thing that separates them, and a bulleted item
    # whose first line indents less than its own body would otherwise read
    # as one fresh paragraph per line.
    fence = rail + 2 * step
    # WHOSE LEADING? THIS RUN'S, where the run is long enough to state one.
    # A DOCUMENT HAS MORE THAN ONE LEADING and the smallest is rarely the
    # body's: ohnd/…323129.7.0 sets its caption on 13.8 and its prose on
    # 27.6, so a document-wide figure called every single body row 'air' and
    # the opinion came apart into one paragraph per line. A segment of three
    # rows or more has already said what leading it is set on — its own
    # smallest step — and only a gap wider than that is a blank line. Below
    # three rows there is no step to learn from (a two-row segment has
    # exactly one, which would always look like a wrap), and the document
    # figure stands in.
    _rows: list = []
    for _l in seg.lines:
        if not _rows or _l.page != _rows[-1][0] or _l.top > _rows[-1][1] + 2.0:
            _rows.append((_l.page, _l.top))
    lead = (_row_lead(seg.lines) if len(_rows) >= 3
            else getattr(segmenter, "body_lead", 0.0) or _row_lead(seg.lines))
    paras: list[list[Line]] = []
    labels: dict[int, Line] = {}
    prev = None
    after_label = False
    bullet_x0: float | None = None
    for i, line in enumerate(seg.lines):
        # a SAME-ROW piece continues its row whatever its x0 — ca1's
        # double sentence-spacing splits rows at sentence gaps and the
        # pieces are not paragraph openers
        same_row = prev is not None and abs(prev.top - line.top) < 2 \
            and line.page == prev.page
        # The line the flow RETURNS to is the next ROW, not the next piece
        # of this one: a row split at wide gaps ('CL-2025-0567' | '--' |
        # 'REVERSED' … — alacivapp) put a mid-measure piece here, so a real
        # opener read as a run that never returns and joined the paragraph
        # above it, costing the document its disposition.
        nxt = next((l for l in seg.lines[i + 1:]
                    if l.row is None or l.row != line.row), None)
        # A first line RETURNS to the edge on the next line; a run that
        # stays out is a quotation and opens nothing.
        returns = nxt is None or abs(nxt.x0 - rail) < step
        if _is_outline_label(line, segmenter):
            labels[len(paras)] = line
            paras.append([])
            prev = line
            after_label = True
            continue
        # A LEADER ROW OPENS ITS OWN BLOCK and closes it: it is a table row,
        # so nothing continues it and it continues nothing. See _LEADER_ROW.
        _leader = _leader_cells(line)
        if _leader is not None or (paras and paras[-1]
                                   and _leader_cells(paras[-1][-1])):
            paras.append([])
            paras[-1].append(line)
            prev = line
            after_label = False
            continue
        # A BULLETED ITEM IS ITS OWN BLOCK, and everything set in from it
        # is that item still running over.
        _bullet = _is_bullet_row(line)
        if _bullet:
            bullet_x0 = line.x0
        elif bullet_x0 is not None and not same_row:
            if line.x0 > bullet_x0 + 2.0:
                paras[-1].append(line) if paras else paras.append([line])
                prev = line
                after_label = False
                continue                   # a runover of the item above
            bullet_x0 = None               # back at the measure: list over
        # THE BLANK LINE THE COURT LEFT OPENS A BLOCK. Until now this walk
        # read the INDENT and nothing else, so a court that separates its
        # blocks by air alone was read as one running paragraph: pamd sets
        # 'In accordance with the accompanying Memorandum Opinion, it is' and
        # 'ORDERED that:' a blank line apart, and because the second row
        # OUTDENTS to the rail instead of indenting off it, the indent test
        # saw no opener and printed the two as one sentence. Its items (2)
        # and (3) welded the same way. The air is the page's own statement
        # that one thing has ended and another begun, and it is measured in
        # the run's own leading — see `_row_lead`.
        air = (bool(paras) and not same_row and prev is not None
               and line.page == prev.page and lead > 0
               and line.top - prev.top >= lead * _AIR_OPENS)
        opens = bool(paras) and not same_row and (
            air
            or _bullet
            or _is_para_mark(line)
            or _is_list_marker(line, seg.lines, i,
                               min((l.x0 for l in seg.lines), default=None))
            # …AND THE SAME ITEM WITH ITS NUMBER TYPED INLINE, standing at or
            # right of the run's own left edge — a runover returns TO that
            # edge and never opens on a numeral.
            or (_INLINE_ITEM.match(" ".join((line.plain or "").split()))
                and line.x0 >= min((l.x0 for l in seg.lines), default=line.x0))
            or _CLOSING_ROW.match(" ".join((line.plain or "").split()))
            or (abs(line.x0 - rail) >= step
                and (line.x0 < fence or returns)))
        # A label OPENS what follows it. Without this the next line joins
        # the label's own slot, and the slot renders as the heading alone —
        # its lines silently discarded (scotus 'a' after '2' came back as
        # residual content).
        if not paras or opens or after_label:
            paras.append([])
        after_label = False
        paras[-1].append(line)
        prev = line
    out = []
    for idx, lines in enumerate(paras):
        label = labels.get(idx)
        if label is not None:
            out.append(m.Heading(
                text=" ".join(label.plain.split()),
                prov=_prov([label])))
        text = _join(lines, vocab)
        if not text:
            continue
        if lines and _is_bullet_row(lines[0]):
            # The glyph is the list's own mark, not the item's words: it is
            # said again by rendering the item AS an item.
            out.append(m.ListItem(text=_BULLET_LEAD.sub("", text, count=1),
                                  prov=_prov(lines), ordered=False))
            continue
        out.append(m.Paragraph(text=text, prov=_prov(lines)))
    return out


def _grid_table(grid, lines: list[Line],
                vocab: set[str] | None) -> list:
    """The lines inside one drawn grid -> one TableBlock, cell by drawn cell.

    The cells are the court's own, blank ones included: the spacer rows
    ncctapp rules between its asset groups are part of how the table reads.
    A cell holding several lines is joined the way a paragraph is joined —
    a cell wraps. Row 0 is a header only when the page SETS it as one (all
    bold, all caps, or centred over its column): a table CONTINUED at the
    top of the next page opens mid-body, and calling its first row a header
    invents a heading the page never printed."""
    cells: dict[tuple[int, int], list[Line]] = {}
    for line in lines:
        mid_y = (line.top + line.bottom) / 2
        row = next((i for i, (a, b) in enumerate(
            zip(grid.row_edges, grid.row_edges[1:])) if a - 2.0 <= mid_y < b),
            None)
        col = next((i for i, (a, b) in enumerate(
            zip(grid.col_edges, grid.col_edges[1:]))
            if a <= line.x0 + 1.0 < b), None)
        if row is None or col is None:
            continue
        cells.setdefault((row, col), []).append(line)
    rows: list[list[str]] = []
    for r in range(grid.n_rows):
        row_cells = []
        for c in range(grid.n_cols):
            ls = sorted(cells.get((r, c), ()), key=lambda l: (l.top, l.x0))
            row_cells.append(_join(ls, vocab) if ls else "")
        rows.append(row_cells)
    while rows and not any(c.strip() for c in rows[-1]):
        rows.pop()
    if not rows:
        return []
    head = [l for l in lines if (l.top + l.bottom) / 2 < grid.row_edges[1]]
    letters = [ch for l in head for ch in l.plain if ch.isalpha()]

    def _centred(line) -> bool:
        """Set to the middle of its own cell — how a column head is set
        (delch centres 'Cruel Punishment Clause' over its column; the cell
        below it is justified to the cell's full measure)."""
        for a, b in zip(grid.col_edges, grid.col_edges[1:]):
            if a <= line.x0 + 1.0 < b:
                return (abs((line.x0 + line.x1) / 2 - (a + b) / 2) <= 8.0
                        and (line.x1 - line.x0) < 0.85 * (b - a))
        return False

    has_header = bool(head) and bool(letters) and (
        all(l.all_bold for l in head) or all(ch.isupper() for ch in letters)
        or (len([c for c in rows[0] if c.strip()]) >= 2
            and all(_centred(l) for l in head)))
    return [m.TableBlock(rows=rows, prov=_prov(lines),
                         has_header=has_header)]


def _table_blocks(seg: Segment, segmenter: Segmenter,
                  vocab: set[str] | None) -> list:
    """A drawn table segment -> its TableBlock.

    The grid comes from the page — pdfio read it off the drawn rules — so
    the segment carries no geometry of its own and cannot lose it to a
    later pass over the stream."""
    grid = next((g for g in (segmenter.tables.get(seg.page) or ())
                 if any(g.holds(l) for l in seg.lines)), None)
    if grid is None:                      # geometry lost: read it as prose
        return _paragraph_blocks(seg, segmenter, vocab)
    return _grid_table(grid, seg.lines, vocab)


def _is_dinkus_seg(seg: Segment) -> bool:
    """A '* * *' section break (possibly column-split into pieces)."""
    txt = "".join(l.plain for l in seg.lines)
    stars = txt.count("*")
    return stars >= 1 and set(txt) <= {"*", " "} and len(seg.lines) <= 5


def _merge_dinkus(stream: list[Segment]) -> list[Segment]:
    """Column-split star pieces on one visual row re-form into ONE break."""
    out: list[Segment] = []
    for seg in stream:
        if (out and _is_dinkus_seg(seg) and _is_dinkus_seg(out[-1])
                and seg.page == out[-1].page
                and abs(seg.lines[0].top - out[-1].lines[0].top) <= 2):
            out[-1].lines.extend(seg.lines)
        else:
            out.append(seg)
    return out


def _segment_blocks(seg: Segment, segmenter: Segmenter,
                    vocab: set[str] | None, inset_flow: bool = False) -> list:
    """``inset_flow``: the caller is filling a section the court sets INSET
    as a whole (a syllabus). There, an indented run is not a quotation — it
    is the section's own measure, and its paragraphs are marked by indent
    WITHIN that measure. Typing the whole run as one quote loses every
    paragraph the page prints (scotus sets a 27-line syllabus page as a
    single inset run; conn sets its entire syllabus that way)."""
    # THE PAPER'S OWN NAME IS A BLOCK OF ITS OWN. A court that leads its
    # opinion with 'OPINION' and sets the first section heading one leading
    # under it hands the segmenter two rows of one weight, and whichever
    # path took them printed the two as one — 'OPINION I. Facts', a
    # PARAGRAPH, on 9 of tenncrimapp's 42 records (the user, 2026-08-21:
    # 'opinion should be its own line'). Split before the typing runs, so
    # every path below sees the banner alone; the whole first row must BE
    # the banner, so a heading that merely contains the word is untouched.
    if (len(seg.lines) > 1
            and "".join(seg.lines[0].plain.split()).upper() in _DOC_BANNERS):
        # The banner is the writing's own HEADING, the way the 33 records
        # that segment it alone already render it — not a paragraph of one
        # word.
        rest = Segment(seg.page, seg.lines[1:], seg.kind)
        return ([m.Heading(text=" ".join(seg.lines[0].plain.split()),
                           prov=_prov(seg.lines[:1]))]
                + _segment_blocks(rest, segmenter, vocab, inset_flow))
    # A label alone in its own segment never reaches the paragraph walk,
    # and the 'single' path types it by its LETTERS — so a lettered label
    # ('B') came out a heading while a numbered one ('1') came out a stray
    # digit paragraph beside it. Geometry, not case, decides.
    if seg.kind == "table":
        return _table_blocks(seg, segmenter, vocab)
    # A CONTENTS PAGE IS NOT A QUOTATION. Every row of one is a leader row —
    # label, dot leader, page number — and `_paragraph_blocks` already knows
    # what to do with those: "a leader row opens its own block and closes
    # it". But a contents list INDENTS BY LEVEL (arwd/…74008.170.0 sets its
    # roman entries at 72, its lettered ones at 84 and its numbered ones at
    # 96 against a body rail of 72), so the segmenter reads the deeper levels
    # as quotations and the quotation path joins the rows into one block:
    # ten entries came out as a single blockquote, and three more welded into
    # one row — '1. Residency Requirement … 27 2. Domicile Requirement … 33
    # 3. Pay-Per-Signature/Commission Ban … 37' (the user, 2026-08-25: 'needs
    # better formating for table of contents the stuff that goes ..........').
    # THE DOTS STAY, and that is not an oversight — see `_split_leader_rows`,
    # where it was settled: the page prints prose with leader dots and
    # declares no table, so folding them into a TableBlock invents a
    # structure the document never made. `_split_leader_rows` takes apart a
    # PARAGRAPH that welded such rows; it never sees a Blockquote, which is
    # why this segment escaped it. The welding is the whole defect and the
    # whole fix: the rows are routed to the walk that keeps them apart.
    if (len(seg.lines) >= _LEADER_SEG_MIN
            and all(_leader_cells(l) is not None for l in seg.lines)):
        return _paragraph_blocks(seg, segmenter, vocab)
    if len(seg.lines) == 1 and _is_outline_label(seg.lines[0], segmenter):
        return [m.Heading(text=" ".join(seg.lines[0].plain.split()),
                          prov=_prov(seg.lines))]
    if inset_flow and seg.kind == "blockquote" and len(seg.lines) >= 3:
        return _paragraph_blocks(seg, segmenter, vocab)
    if _is_dinkus_seg(seg):
        stars = "".join(l.plain for l in seg.lines).count("*")
        return [m.Heading(text=" ".join("*" * 1 for _ in range(max(stars, 3))),
                          prov=_prov(seg.lines))]
    if seg.kind == "blockquote":
        text = _join(seg.lines, vocab)
        if not text:
            return []
        # A CENTERED heading indents from the margin and reads as a quote
        # to the segmenter — the same bold/caps test the 'single' path
        # applies must run here too ('II. STANDARD OF REVIEW' rendered as
        # a blockquote beside its h3 siblings — michctapp).
        plain = " ".join(l.plain.strip() for l in seg.lines).strip()
        letters = [c for c in plain if c.isalpha()]
        if (len(seg.lines) <= 2 and len(plain) < 80 and letters
                and (all(l.all_bold for l in seg.lines)
                     or all(c.isupper() for c in letters))):
            # THE PAPER'S OWN NAME IS A HEADING OF ITS OWN. A court that
            # leads its opinion with 'OPINION' and sets the first section
            # heading one leading under it gives the segmenter two rows of
            # the same weight, and joining them printed the two as one
            # ('OPINION I. Facts' — 9 of tenncrimapp's 42; the user,
            # 2026-08-21: 'opinion should be its own line'). The banner is
            # matched as the WHOLE first row, so a heading that merely
            # contains the word is untouched.
            if (len(seg.lines) == 2
                    and "".join(seg.lines[0].plain.split()).upper()
                    in _DOC_BANNERS):
                return [m.Heading(text=_mend_seams(
                            " ".join(seg.lines[0].plain.split())),
                            prov=_prov(seg.lines[:1])),
                        m.Heading(text=_mend_seams(
                            " ".join(seg.lines[1].plain.split())),
                            prov=_prov(seg.lines[1:]))]
            return [m.Heading(text=_mend_seams(text), prov=_prov(seg.lines))]
        # A QUOTATION SETS ITS OWN PARAGRAPHS, and it sets them the way the
        # page sets any paragraph: by indenting the first line off the
        # quote's own rail, with no extra space above it (arkctapp quotes a
        # five-paragraph Rule 37 petition at rail 108 with each opening line
        # at 144 on the same 31pt leading throughout, and one container for
        # the run welded all five into one block).
        #
        # The opener is an indented line whose predecessor sits at the rail
        # AND ENDED SHORT. Indentation alone is not enough, and neither is
        # 'the flow returns below it': a HANGING list inside a quote indents
        # its WRAPS instead ('1. Whether the district court erred …' at 90
        # with its runover at 108 — idaho/monson), and on a two-line item
        # that is locally the same shape as a first-line indent. What tells
        # them apart is the line ABOVE: a paragraph ends short of the
        # measure, a wrapped one runs to it.
        _qrail = _mode_x0(seg.lines)
        if _qrail is None:
            return [m.Blockquote(text=text, prov=_prov(seg.lines))]
        _qstep = getattr(segmenter, "para_indent_min", 12.0)
        _qright = max(l.x1 for l in seg.lines)
        # …AND AN ITEM THAT CARRIES ITS OWN NUMBER CUTS TOO. A quotation
        # splits on the indent its opener takes, and a numbered run inside
        # one takes no indent at all: wiwd/…55879.12.0 closes 'IT IS ORDERED
        # that:' with four directions, and items 2, 3 and 4 came back as one
        # block ('… DENIED as moot. 3. Petitioner is DENIED … 4. The clerk
        # …'). See `_INLINE_ITEM`.
        _cuts = [i for i in range(1, len(seg.lines))
                 if (seg.lines[i].x0 - _qrail >= _qstep
                     and seg.lines[i - 1].x0 - _qrail < _qstep
                     and seg.lines[i - 1].x1 <= _qright - 12.0
                     and seg.lines[i].top - seg.lines[i - 1].top > 2.0)
                 or _INLINE_ITEM.match(
                     " ".join((seg.lines[i].plain or "").split()))]
        if _cuts:
            out = []
            for a, b in zip([0] + _cuts, _cuts + [len(seg.lines)]):
                part = seg.lines[a:b]
                _t = _join(part, vocab)
                if _t:
                    out.append(m.Blockquote(text=_t, prov=_prov(part)))
            if len(out) > 1:
                return out
        return [m.Blockquote(text=text, prov=_prov(seg.lines))]
    if seg.kind == "single":
        # A 'single' may be a column-split VISUAL ROW ('¶ 2' at the margin
        # beside its paragraph's first line — ill; '4.' beside its heading
        # title — idahoctapp): every piece is content, never just lines[0].
        text = _join(seg.lines, vocab)
        if not text:
            return []
        plain = " ".join(l.plain.strip() for l in seg.lines).strip()
        letters = [c for c in plain if c.isalpha()]
        if (all(l.all_bold for l in seg.lines)
                or (letters and all(c.isupper() for c in letters))) \
                and len(plain) < 80:
            return [m.Heading(text=_mend_seams(text), prov=_prov(seg.lines))]
        return [m.Paragraph(text=text, prov=_prov(seg.lines))]
    if seg.kind == "separator":
        return []
    return _paragraph_blocks(seg, segmenter, vocab)


def _group_footnotes(zone_lines: list[Line], flush: dict[int, str],
                     vocab: set[str] | None,
                     grids: list | None = None) -> list[m.Footnote]:
    """Zone lines -> Footnote objects, split where a label opens a note.

    ``grids``: the drawn tables of this page. A NOTE MAY PRINT A TABLE —
    ind footnotes its lien chronology as a two-column ruled table that
    continues onto the next page (edgerock, p27) — and a note's zone lines
    are read the same way a writing's are: the lines inside a grid are its
    cells, the rest is the note's prose."""
    notes: list[tuple[str, list[Line]]] = []
    for line in zone_lines:
        lab = detect_label(line) or flush.get(line.id)
        if lab is not None:
            notes.append((lab, [line]))
        elif notes:
            notes[-1][1].append(line)
        else:
            notes.append(("?", [line]))   # carried tail with no home yet
    out = []
    for lab, lines in notes:
        held = [g for g in (grids or ())
                if any(g.holds(l) for l in lines)]
        if held:
            out.append(m.Footnote(label=lab, blocks=_note_with_tables(
                lab, lines, held, vocab)))
            continue
        # Strip the label glyphs off the note's own first line.
        first = lines[0].plain.strip()
        if lab != "?" and first.startswith(lab):
            first = first[len(lab):].lstrip(". ")
        elif lab != "?" and len(first) <= 3:
            first = ""
        body_lines = lines[1:]
        rest = _join(body_lines, vocab)
        if first.endswith("-") and rest:
            # The note's own first line wrapped on a hyphen: prove the
            # unbroken word from the document vocabulary, else weld —
            # never 'Ex- change'.
            head_word = []
            for ch in reversed(first[:-1]):
                if ch.isalpha() or ch in "’'":
                    head_word.append(ch)
                else:
                    break
            first_tok = rest.split()[0] if rest.split() else ""
            probe = ("".join(reversed(head_word))
                     + first_tok.strip("“”\"'’‘()[]{}.,;:!?")).lower()
            if head_word and vocab and probe in vocab:
                text = first[:-1] + rest
            else:
                text = first + rest
        else:
            text = " ".join(x for x in (first, rest) if x)
        out.append(m.Footnote(label=lab, blocks=_note_prose(lab, lines,
                                                             vocab)))
    return out


def _note_prose(lab: str, lines: list[Line],
                vocab: set[str] | None) -> list:
    """A note's prose run -> one Paragraph, its label glyphs stripped."""
    if not lines:
        return []
    first = lines[0].plain.strip()
    if lab != "?" and first.startswith(lab):
        first = first[len(lab):].lstrip(". ")
    elif lab != "?" and len(first) <= 3:
        first = ""
    rest = _join(lines[1:], vocab)
    if first.endswith("-") and rest:
        head_word = []
        for ch in reversed(first[:-1]):
            if ch.isalpha() or ch in "’'":
                head_word.append(ch)
            else:
                break
        first_tok = rest.split()[0] if rest.split() else ""
        probe = ("".join(reversed(head_word))
                 + first_tok.strip("“”\"'’‘()[]{}.,;:!?")).lower()
        text = (first[:-1] + rest) if (head_word and vocab and probe in vocab)\
            else (first + rest)
    else:
        text = " ".join(x for x in (first, rest) if x)
    return [m.Paragraph(text=text, prov=_prov(lines))] if text else []


def _note_with_tables(lab: str, lines: list[Line], grids: list,
                      vocab: set[str] | None) -> list:
    """A note that prints a drawn table: prose, table and prose in the
    order the note sets them, the label stripped off the first run only."""
    runs: list[tuple[object, list[Line]]] = []
    for line in lines:
        owner = next((g for g in grids if g.holds(line)), None)
        if runs and runs[-1][0] is owner:
            runs[-1][1].append(line)
        else:
            runs.append((owner, [line]))
    blocks: list = []
    first_prose = True
    for owner, run in runs:
        if owner is None:
            blocks.extend(_note_prose(lab if first_prose else "?", run,
                                      vocab))
            first_prose = False
        else:
            blocks.extend(_grid_table(owner, run, vocab))
    return blocks


# A STANDALONE DISPOSITION: the court's whole ruling in one printed line.
# For a rescript it TERMINATES the writing; for a writ ruling it IS the
# writing ('WRIT DENIED.' is the entire body of a lactapp supervisory
# writ). Either way the line is the court speaking, not apparatus.
_DISPO = ("so ordered", "judgment affirmed", "judgment reversed",
          "order affirmed", "order reversed", "petition denied",
          "appeal dismissed", "judgment vacated",
          "writ denied", "writ granted", "writ dismissed",
          "writ denied in part", "stay denied", "stay granted")


# A STACK the page newlined: a run of short lines at one left edge, closing a
# writing with its panel. Ink at most 45% of the measure (nd's roster names
# run 15.3-36.9%, its prose 93-100%); at least three rows, so a single short
# paragraph is never a stack; one indent STEP (30-42pt) admits the opening row
# that carries the paragraph marker.
_STACK_INK = 0.45
_STACK_ROWS = 3
_STACK_EDGE_TOL = 2.0
_STACK_STEP = (30.0, 42.0)


def _is_dispo_line(txt: str) -> bool:
    return " ".join(txt.split()).lower().rstrip(".").strip() in _DISPO


def _merge_heading_runs(blocks: list, by_id: dict) -> list:
    """One printed heading is ONE heading, however many rows it wraps over.

    A heading that wraps arrives as one Heading PER ROW, because the
    segmenter cut the rows apart: a page carrying two leadings (a
    double-spaced body over a single-spaced footnote block) has its bands
    measured off the tighter one, so every row of the page reads as its own
    segment. Prose survives that — `_flush_merge` rejoins a row that ends
    mid-sentence — but a heading has no mid-sentence cue, so it stayed in
    pieces: gud/…15303.118.0 printed a two-part heading as NINE centred
    blocks with a paragraph of air between each, and cand/…419089.7070.2
    printed the paper's own name as SIXTEEN (the user, 2026-08-23: 'why
    space separting text', 'we need to make sure we gorup stuff better',
    'its paragrpahs grouped together or section of table of contents').

    The rows the court set as one heading are the ones it set in ONE TYPE at
    ONE PITCH: same face, and a gap no wider than the run's own leading.
    Both are read off the rows themselves — nothing here spells a heading or
    guesses a distance. Measured over the corpus, 238 files carry a run of
    three or more consecutive headings.
    """
    if len(blocks) < 2:
        return blocks
    def rows(b):
        return [by_id[i] for i in getattr(b, "prov", None).line_ids
                if i in by_id] if getattr(b, "prov", None) else []
    def face(l):
        return (l.font or "", round(l.size or 0.0, 1), bool(l.all_bold))
    out: list = []
    for b in blocks:
        prev = out[-1] if out else None
        if not (isinstance(b, m.Heading) and isinstance(prev, m.Heading)):
            out.append(b)
            continue
        a_rows, b_rows = rows(prev), rows(b)
        if not a_rows or not b_rows:
            out.append(b)
            continue
        if a_rows[-1].page != b_rows[0].page:
            out.append(b)          # never weld across the sheet
            continue
        if {face(l) for l in a_rows} != {face(l) for l in b_rows}:
            out.append(b)          # a different type is a different heading
            continue
        # THE RUN'S OWN PITCH, not a constant: the gap between the rows of
        # one heading is its leading, and the gap to the next heading is
        # wider. With only two rows to go on the row's type size is the
        # measure available — one line of leading and no more.
        _sz = max((l.size or 12.0) for l in a_rows + b_rows)
        _gap = b_rows[0].top - a_rows[-1].top
        if not 0 < _gap <= _sz * 1.45:
            out.append(b)
            continue
        joined = prev.text.rstrip()
        tail = b.text.lstrip()
        out[-1] = m.Heading(
            text=f"{joined} {tail}" if joined and tail else joined or tail,
            prov=m.Prov(prev.prov.page,
                        tuple(prev.prov.line_ids) + tuple(b.prov.line_ids)))
    return out


def _unweld_conformed(blocks: list, by_id: dict, vocab: set[str] | None) -> list:
    """Re-split a paragraph that swallowed a conformed '/s/' run.

    `_paragraphs` opens a block only where the flow RETURNS to the rail, so
    a run set far right of the measure reads as a quotation continuation and
    welds into the paragraph above it. A court that signs en banc prints one
    conformed name per justice at one right-hand edge, and none of them
    returns: haw's five cost `bloch_v._bloch_1` its entire signature (the
    DATED line and all five signers in a single body paragraph, so the lift's
    `'/s/' in text[:20]` test never fired) and `fung_v._hoi` four of its
    five — only the last signer opened a block, because the last line of a
    segment returns by default.

    The run is re-split HERE, on the '/s/' GLYPH, and not by widening the
    stack rule's step window: haw signs on a 27pt lead and bloch on 20pt,
    while the printed rosters that window was measured for run 30-42pt, so
    the geometry that separates these is the court's, not the corpus's. The
    glyph is the landmark and it is the same in every court that uses it.
    """
    out: list = []
    for b in blocks:
        text = getattr(b, "text", "") or ""
        ids = getattr(getattr(b, "prov", None), "line_ids", ())
        lines = [by_id[i] for i in ids if i in by_id]
        if (not isinstance(b, m.Paragraph) or len(lines) < 2
                or "/s/" not in text
                or text.replace("<strong>", "").lstrip().startswith("/s/")):
            out.append(b)
            continue
        # ONE ELEMENT PER PRINTED LINE that opens with the glyph; everything
        # else keeps the run it was in.
        lines.sort(key=lambda l: (l.page, round(l.top, 1), l.x0))
        groups: list[tuple[str, list]] = []
        for line in lines:
            plain = " ".join(line.plain.split())
            # THE ATTESTATION THAT OPENS THE BLOCK breaks the run too. The
            # lift already knows a short 'DATED …' / 'BY THE COURT:' line
            # directly above the signers belongs to them, but it can only
            # claim it if it is a block of its own — welded into the body
            # paragraph it left fung_v._hoi reading '… costs is denied.
            # DATED: Honolulu, Hawaiʻi, May 20, 2026.' as one sentence.
            kind = "text"
            if plain.startswith("/s/"):
                kind = "sig"
            elif len(plain) < 120 and (
                    plain.upper().startswith("DATED")
                    or plain.upper().rstrip(":") in ("BY THE COURT",
                                                     "FOR THE COURT")):
                kind = "attest"
            if kind != "text" or not groups or groups[-1][0] != "text":
                groups.append((kind, [line]))
            else:
                groups[-1][1].append(line)
        if len(groups) < 2:
            out.append(b)
            continue
        for _kind, ls in groups:
            piece = _join(ls, vocab)
            if piece.strip():
                out.append(m.Paragraph(text=piece, prov=_prov(ls)))
    return out


def assemble(model, geom: DocGeometry | None, segments_by_page: dict,
             zones: FootnoteZones, zone_tops: dict, zone_lines_by_page: dict,
             parser: BylineParser, vocab: set[str] | None,
             trace, caption_band: tuple[float, float] | None = None,
             doc_type=None, syl_pages: set[int] | None = None,
             front_matter: tuple = (),
             para_indent_min: float = 12.0,
             headmatter_claimed: bool = False,
             writing_starts: dict[int, str] | None = None,
             tables: dict[int, list] | None = None) -> Assembled:
    result = Assembled()
    # The drawn tables of each page, as the caller resolved them (a caption
    # box is withheld upstream — it is headmatter, not a table).
    _tables: dict[int, list] = (tables if tables is not None
                                else {pm.number: pm.tables
                                      for pm in model.pages})

    # A byline can be column-split by pdfio ('LYNCH,' | 'Circuit Judge.  …');
    # byline tests read the rejoined VISUAL ROW, keyed to the row's first
    # piece so one row can only open one writing. Rows rebuild from CONTENT
    # lines only: a stationery line-number shares the byline's row ('19' |
    # 'KEARSE, Circuit Judge:'), and counting the cut furniture as the
    # row's first piece silenced the byline.
    content_ids = {l.id for segs in segments_by_page.values()
                   for s in segs for l in s.lines}
    row_text: dict[tuple[int, int], str] = {}
    row_first: dict[tuple[int, int], int] = {}
    for pm in model.pages:
        by_row: dict[int, list] = {}
        for line in pm.lines:
            if line.row is not None and line.id in content_ids:
                by_row.setdefault(line.row, []).append(line)
        for row, pieces in by_row.items():
            pieces.sort(key=lambda l: l.x0)
            row_text[(pm.number, row)] = " ".join(
                p.plain.strip() for p in pieces).strip()
            row_first[(pm.number, row)] = pieces[0].id

    def byline_text(line) -> str | None:
        """The text to test for a byline, or None when this piece can never
        open one (it is not its row's first piece)."""
        if line.row is None:
            return line.plain.strip()
        key = (line.page, line.row)
        if row_first.get(key) != line.id:
            return None
        return row_text.get(key, line.plain.strip())

    # A CONSOLIDATED caption may RUN ON past page 1 (ca9 stacks one docket
    # block per consolidated case): a following page whose rows are docket
    # cells, party names and status labels — with no body prose — is still
    # the caption, and its rows are headmatter, not the writing's body.
    def _caption_runon_pages() -> set[int]:
        from .headmatter import looks_like_docket as _ld
        out: set[int] = set()
        prev_ok = True
        for pm in model.pages[1:]:
            if not prev_ok:
                break
            txts = [" ".join(l.plain.split()) for l in pm.lines
                    if l.plain.strip()]
            if not txts or len(txts) > 26:
                break
            dockets = sum(1 for t in txts
                          if _ld(t) or t.lower().startswith("d.c. no"))
            status = sum(1 for t in txts if t.rstrip(",.").lower() in
                         ("petitioner", "respondent", "petitioners",
                          "respondents", "appellant", "appellee",
                          "appellants", "appellees", "and", "defendant",
                          "plaintiff"))
            longest = max((len(t) for t in txts), default=0)
            # A page that PRINTS A BYLINE has started its writing, however
            # much caption spilled onto it (ca11 runs a 2-page caption and
            # then 'PER CURIAM:' plus the whole opinion on page 2). The
            # court's own signal outranks the caption-shape evidence.
            if any(parser.parse(t) for t in txts):
                prev_ok = False
                continue
            if dockets >= 1 and status >= 1 and longest <= 90:
                out.add(pm.number)
            else:
                prev_ok = False
        return out

    _runon = _caption_runon_pages()

    # Reading-order segment stream, zone lines excluded (they're footnotes).
    stream: list[Segment] = []
    for pm in model.pages:
        cut = zone_tops.get(pm.number)
        for seg in segments_by_page.get(pm.number, []):
            lines = [l for l in seg.lines if cut is None or l.top < cut]
            if lines:
                stream.append(Segment(seg.page, lines, seg.kind))
    stream = _merge_dinkus(stream)

    _WRAP_TERMINALS = (".", ":", ";", "!", "?", "”", '"')
    # Words a byline clause never ENDS on — a tail ending here is a wrap
    # still mid-clause ('…concurring in part and concurring in'), while
    # 'dissenting from the denial of rehearing en banc' is complete though
    # unpunctuated.
    _MIDCLAUSE = frozenset({"and", "or", "in", "of", "the", "with", "whom",
                            "from", "to", "for", "a", "an", "part", "by",
                            "joined", "join", "joins", "denial",
                            "circuit", "district", "chief", "senior",
                            "justice", "justices", "judge", "judges"})

    def _joined_byline(lines, j, limit=4):
        """The byline opening at lines[j] — alone, or wrapped across up to
        ``limit`` lines ('JUSTICE JACKSON, with whom JUSTICE SOTOMAYOR and' /
        'JUSTICE KAGAN join, dissenting.' — the wrap can break on ANY word,
        not just a hyphen or comma). A candidate that parses KINDLESS keeps
        joining in case its kind clause wrapped ('JUSTICE KAVANAUGH,' /
        'concurring in part…'); a kinded parse wins, and a kinded parse that
        still ends mid-clause keeps joining for the full clause, falling
        back to the partial if the extension never parses. Returns
        (byline, byline_source_text, lines_consumed)."""
        t0 = byline_text(lines[j])
        if not t0:
            return None, None, 0
        cur = t0.strip()
        kinded = None
        kindless = None
        for n in range(1, limit + 1):
            b = parser.parse(cur)
            s = cur.rstrip()
            if b is not None:
                if b.kind is not None:
                    last = s.rsplit(" ", 1)[-1].strip(",.:;—–").lower()
                    # A comma-ending tail is ALWAYS mid-clause ('…joined by
                    # RESTREPO and FREEMAN,' — a joiner list of names no
                    # word-list can cover).
                    midclause = (s.endswith((",", "—", "–", "-"))
                                 or last in _MIDCLAUSE)
                    if s.endswith(_WRAP_TERMINALS) or not midclause:
                        return b, cur, n
                    kinded = (b, cur, n)
                elif kindless is None or b.end >= len(cur) - 1:
                    # Prefer the LONGEST full-line kindless parse: a
                    # delivered ANNOUNCEMENT wraps ('…in which J. STEVEN' /
                    # 'STAFFORD, P.J., … joined.') and the first-line parse
                    # severs it mid-name. Inline bylines (end < len) never
                    # extend.
                    kindless = (b, cur, n)
            if j + n >= len(lines) or s.endswith(_WRAP_TERMINALS):
                break
            nxt = lines[j + n].plain.strip()
            if not nxt:
                break
            cur = s[:-1] + nxt if s.endswith("-") else s + " " + nxt
        return kinded or kindless or (None, None, 0)

    def _line_opens_byline(lines, j) -> bool:
        """Does lines[j] open a byline — alone, or wrapped onward?"""
        return _joined_byline(lines, j)[0] is not None

    def _midsentence_tail(text: str) -> bool:
        """Does this text end MID-SENTENCE — so a byline-shaped line after
        it is a wrapped continuation ('Before LOURIE and HUGHES, Circuit
        Judges, and' / 'FREEMAN, District Judge.'), never a writing
        boundary?"""
        s = text.rstrip()
        if s.endswith((",", ";")):
            return True
        # An UNTERMINATED 'Before …' roster is still listing its panel —
        # the next line ('GILES, United States District Judge, sitting by'
        # — ca4 wraps mid-name) is its continuation, not a byline. A roster
        # closed on its own terminal — '.', or a parenthetical ')' ('BEFORE
        # THE ENTIRE BENCH (except THOMAS, J.)' — mich) — is complete.
        # a footnote MARK may ride the roster's terminal ('…Circuit
        # Judges.*' — ca5 stars its sitting-by-designation note)
        s = s.rstrip("*†‡∗⁎﹡＊0123456789") if s.rstrip().endswith(
            tuple("*†‡∗⁎﹡＊")) else s
        low = " ".join(s.split()).lower()
        if low.startswith(("before ", "before:")) \
                and not s.rstrip().endswith((".", ")", ":")) \
                and not low.endswith("bench"):
            # 'BEFORE THE ENTIRE BENCH' is a complete formula (mich), not
            # a list cut mid-name.
            return True
        return s.rsplit(" ", 1)[-1].lower() in ("and", "&", "or")

    # Split any segment at an interior byline so each writing opens cleanly.
    split_stream: list[Segment] = []
    for seg in stream:
        if seg.kind == "table":
            split_stream.append(seg)
            continue
        cuts = [j for j in range(1, len(seg.lines))
                if _line_opens_byline(seg.lines, j)
                and not _midsentence_tail(seg.lines[j - 1].plain)]
        bounds = [0, *cuts, len(seg.lines)]
        for a, b in zip(bounds, bounds[1:]):
            if seg.lines[a:b]:
                split_stream.append(Segment(seg.page, seg.lines[a:b], seg.kind))

    # A ROW THE PAGE NEVER SEPARATED IS NOT A SEGMENT — welded back BEFORE
    # the byline starts are read, because an unwelded one can open a WRITING.
    # pamd/…145277.24.0 sets 'AFFIRMED;' bold on the row under '… Act is',
    # and standing alone that row both opened a writing of its own and typed
    # as a heading. See `_weld_unspaced` for the three tests.
    _body_lead = _row_lead([_l for _s in stream for _l in _s.lines])
    split_stream = _weld_unspaced(split_stream, _body_lead, parser)

    def head_byline(seg):
        """(byline, byline_source_text, lines_consumed) for a segment head —
        retrying across a WRAPPED byline ('…JUSTICE THOMAS joins, dis-' /
        'senting from the denial…')."""
        return _joined_byline(seg.lines, 0)

    # Opinion starts. A segment head after a mid-sentence tail is a wrapped
    # continuation (the roster's second line), not a writing boundary. The
    # segment's KIND is no gate: a tight-set cover classifies as notice yet
    # its 'Opinión del Tribunal emitida por…' head is the byline (prsupreme)
    # — the grammar is the evidence.
    # A BYLINE SET RIGHT OF THE MEASURE IS A SIGNATURE, not a writing. A
    # writing's byline stands at the rail or on the page axis; a name pushed
    # into the right half of the sheet is the conformed signature that CLOSES
    # one. nm signs 'MICHAEL E. VIGIL, Justice' at x0=324 of 612 above its
    # 'WE CONCUR:' roster, and core opened a second majority on it in 41 of
    # nm's 50 records — a writing whose whole body was the roster beneath the
    # signature. Tested on the row's CENTRE and not its left edge, so a
    # centred byline ('PER CURIAM') is not caught: nm's signature centres at
    # 413 against a page centre of 306, while a centred row centres at 306.
    _SIG_OFF_AXIS = 40.0

    def _signature_flush(seg) -> bool:
        if not seg.lines:
            return False
        line = seg.lines[0]
        mid = (line.x0 + line.x1) / 2
        return mid > model.pages[0].width / 2 + _SIG_OFF_AXIS

    # …AND A BYLINE THAT SIGNS OFF IS A SIGNATURE TOO. nm sets the author's
    # conformed name at the rail on some records and flushed right on others,
    # but either way an ATTESTATION follows it — 'WE CONCUR:' over the roster
    # of justices who joined. A writing never opens its body with 'WE
    # CONCUR:'; that row is what closes the writing above. This catches the
    # 23 nm records where the signature is at the rail and the position test
    # cannot see it.
    # THE ATTESTATION IS A LABEL, NOT A SENTENCE, and the row must be the
    # whole of it. Unanchored, 'I concur in the majority's conclusion that
    # Reyes has failed to show the district court erred…' — the first line of
    # a specially concurring opinion's own body — read as an attestation, so
    # the byline above it was demoted to a signature and the writing was
    # never opened (idahoctapp/state_v._reyes; the user's call, 2026-08-20).
    # Measured over nm, nmctapp, idaho and idahoctapp: the attestation is the
    # 10-character 'WE CONCUR:' on all 71 occurrences, and that sentence is
    # the only other row the unanchored pattern matched.
    # …AND THE CLERK'S ATTESTATION IS THE OTHER FORM OF IT. 'FOR THE
    # COURT:' over the clerk's name is what a federal appellate clerk prints
    # to certify a paper, and the byline above it — cadc centres 'Per
    # Curiam' there — is that paper's attribution, not the opening of a new
    # one. Measured: the row occurs in 11 courts (vt 42, cadc 37, nmcca 36,
    # afcca 32, cafc 29, acca 13, ca2 8, lactapp 5, ilcd 2, washctapp 2,
    # nj 1) and it is a LABEL, never a sentence, so it is anchored whole
    # exactly as 'WE CONCUR:' is. On cadc it cost 7 of the 100 records a
    # phantom writing holding nothing but the clerk's signature block
    # (the user, 2026-08-21, on in_re_donald_trump_1: 'not tow opinions',
    # and on joe_neguse: 'too many opinions').
    _ATTEST = re.compile(
        r"^(?:WE|I)\s+(?:CONCUR|CONCURRED|DISSENT|DISSENTED)\s*[:.]?$"
        r"|^CONCUR(?:RED)?\s*:\s*$"
        r"|^FOR\s+THE\s+COURT\s*:$", re.I)

    def _signs_off(i: int) -> bool:
        """Is the byline at `i` followed by an attestation?

        The attestation may fall inside the byline's own segment or open the
        NEXT one — the segmenter breaks on the blank line the court leaves
        above 'WE CONCUR:' — so both are checked. Looking only inside the
        segment found nothing on any of nm's records.
        """
        seg = split_stream[i]
        tail = list(seg.lines[1:4])
        if i + 1 < len(split_stream):
            tail += list(split_stream[i + 1].lines[:2])
        for line in tail:
            text = " ".join((line.plain or "").split())
            if not text:
                continue
            if _ATTEST.match(text):
                return True
        return False

    starts = [i for i, seg in enumerate(split_stream)
              if head_byline(seg)[0]
              and not _signature_flush(seg)
              and not _signs_off(i)
              # a caption RUN-ON page carries no writing (ca9 devas)
              and seg.page not in _runon
              # …AND NEITHER DOES A SYLLABUS PAGE. The Clerk closes a
              # syllabus by naming who joined and who wrote separately —
              # 'CHIEF JUSTICE RABNER and JUSTICES PIERRE-LOUIS, WAINER
              # APTER, NORIEGA, and HOFFMAN join in JUSTICE PATTERSON's
              # opinion.' / 'JUSTICE FASCIALE filed a dissent.' — and both
              # rows parse as bylines in the reversed grammar. Anchored on,
              # they opened phantom writings at the foot of the syllabus and
              # the second of them ran on over the COVER, so the invariant
              # that a writing is never bisected then moved the whole
              # claimed headmatter inside it: nj's two 127- and 157-page
              # consolidated releases rendered four writings and NOT ONE
              # headmatter row. A page the court named as syllabus is not
              # where a writing opens -- the boundary rule below already
              # says so for the first segment; it holds for every anchor.
              and seg.page not in (syl_pages or ())
              and not (i > 0 and split_stream[i - 1].lines
                       and _midsentence_tail(
                           split_stream[i - 1].lines[-1].plain))]

    # THE VOTE BLOCK REPORTS THE WRITINGS; IT DOES NOT OPEN THEM. Texas's
    # Court of Criminal Appeals prints its whole vote under the caption:
    #
    #     PARKER, J., delivered the opinion of the Court in which
    #     RICHARDSON, NEWELL, WALKER, and MCCLURE, JJ., joined.
    #     MCCLURE, J., filed a concurring opinion in which WALKER, J.,
    #     joined.  KEEL, J., concurred.  YEARY, J., filed a dissenting
    #     opinion in which FINLEY, J., joined …
    #
    # Every clause parses as a byline. Anchored on the last of them, Yeary's
    # ANNOUNCEMENT took all 102 blocks of the opinion of the Court and
    # Parker's real byline kept none (texcrimapp/cuevas_2).
    #
    # The announcement cannot be refused in the grammar, because this court
    # issues each separate writing as its OWN slip and there the same
    # sentence IS that document's byline — 12 of its 42 records take their
    # author from one, and refusing it cost every one of them its author.
    # What tells the two apart is a judge already named as DELIVERING the
    # opinion: after that, the block is reporting the vote. Bounded to the
    # delivering byline's own page and the four segments following it, which
    # is as far as a vote block runs.
    def _announced_head(i: int) -> bool:
        head = " ".join((byline_text(split_stream[i].lines[0]) or ""
                         ).split()).lower()
        return any(f" {v} a " in head or f" {v} an " in head
                   for v in ("filed", "authored", "issued", "wrote"))

    if len(starts) > 1:
        _delivers = next(
            (i for i in starts
             if any(f" {v} the opinion" in " ".join(
                 (byline_text(split_stream[i].lines[0]) or "").split()).lower()
                 for v in _DELIVER_VERBS)), None)
        if _delivers is not None:
            starts = [i for i in starts
                      if not (_delivers < i <= _delivers + 4
                              and split_stream[i].page
                              == split_stream[_delivers].page
                              and _announced_head(i))]

    # A PANEL ROSTER set one judge per row (ca7's order form: 'FRANK H.
    # EASTERBROOK, Circuit Judge' × 3) is byline-shaped, row after row. Two
    # or more ADJACENT single-line KINDLESS byline segments with no body
    # between them are a roster, not writings — a real second writing always
    # follows its predecessor's body, and a real byline's kind clause
    # ('dissenting.') never appears in a roster row.
    def _kindless_pure(i: int) -> bool:
        seg = split_stream[i]
        if len(seg.lines) != 1:
            return False
        t = byline_text(seg.lines[0]) or ""
        b = parser.parse(t)
        return (b is not None and b.kind is None and b.name != "PER CURIAM"
                and b.end >= len(t.strip()) - 1)
    if len(starts) >= 2:
        roster: set[int] = set()
        run = [starts[0]] if _kindless_pure(starts[0]) else []
        for a, b in zip(starts, starts[1:]):
            # A roster prints TOGETHER: rows on different pages are two
            # writings (wvactapp's p1 'CHIEF JUDGE GREEAR delivered…'
            # announcement and p2 'GREEAR, Chief Judge:' byline).
            if (run and b - a == 1 and _kindless_pure(b)
                    and split_stream[a].page == split_stream[b].page):
                run.append(b)
            else:
                if len(run) >= 2:
                    roster.update(run)
                run = [b] if _kindless_pure(b) else []
        if len(run) >= 2:
            roster.update(run)
        starts = [i for i in starts if i not in roster]
    # A TERMINAL byline is a SIGNATURE, not a start: cadc's judgments run
    # caption > JUDGMENT heading > body > 'Per Curiam' near the end (with a
    # clerk block after it). Anchoring on it would put the whole body in
    # headmatter — demote it when it would leave almost nothing to the
    # writing AND an earlier heading anchor exists to own the body.
    terminal_author = None
    if len(starts) == 1:
        remaining = len(split_stream) - starts[0]
        # Measured in LINES too: a one-page announcement (ill's 'Justice
        # Overstreet delivered…' over 18 body lines in 2 segments) has few
        # SEGMENTS after its byline but plenty of body — that byline opens
        # the writing, it doesn't sign one.
        lines_after = sum(len(s.lines) for s in split_stream[starts[0] + 1:])
        # A signature FOLLOWS a body: demote only when substantial body
        # precedes the byline (cadc's judgment text before its trailing
        # 'Per Curiam'). A 'PER CURIAM' whose only predecessors are the
        # caption and an ORDER heading (pa) OPENS the writing.
        body_before = sum(
            len(s.lines) for s in split_stream[:starts[0]]
            if not (caption_band and s.page == 1
                    and s.lines[0].top <= caption_band[1] + 4))
        if body_before >= 10 and remaining <= max(4, 0.15 * len(split_stream)) \
                and lines_after <= 8:
            seg0 = split_stream[starts[0]]
            b0, t0, _c0 = head_byline(seg0)
            if b0 is not None and len(seg0.lines) <= 2:
                from ..classify import heading_doc_type as _hdt
                has_heading = any(
                    s.page <= 2 and any(
                        len(l.plain.strip()) < 80
                        and _hdt(l.plain.strip()) is not None
                        for l in s.lines)
                    for s in split_stream[:starts[0]])
                if has_heading:
                    terminal_author = (b0, t0)
                    starts = []

    # The END-SIGNATURE model (calctapp): the whole body precedes a CLUSTER
    # of short bylines ('CHUNG, J.' / 'WE CONCUR:' / 'EDMON, P. J.' /
    # 'ADAMS, J.') — every one is a signature; the first names the author.
    if starts:
        first = starts[0]
        _body_before = sum(
            len(s.lines) for s in split_stream[:first]
            if not (caption_band and s.page == 1
                    and s.lines[0].top <= caption_band[1] + 4))
        _tail_lines = sum(len(s.lines) for s in split_stream[first:])
        if (_body_before >= 10 and _tail_lines <= 12
                and all(len(split_stream[i].lines) <= 2 for i in starts)
                and all(len(" ".join(l.plain.split())) <= 40
                        for i in starts for l in split_stream[i].lines)):
            b0, t0, _c0 = head_byline(split_stream[first])
            if b0 is not None and terminal_author is None:
                terminal_author = (b0, t0)
                starts = []

    def _prose_anchor(j0: int, substantive: bool = False) -> int | None:
        """First BODY-PROSE segment at/after j0: ≥2 lines, not counsel or
        appeal-from apparatus, lowercase-majority text (a banner or roster
        is never a paragraph)."""
        for j in range(j0, len(split_stream)):
            s = split_stream[j]
            # ≥2 lines, or ONE full-measure prose line (ca3 sets its
            # rehearing order one line per segment)
            if len(s.lines) < 2 and not (
                    len(s.lines) == 1 and geom
                    and s.lines[0].width >= 0.75 * geom.column):
                continue
            txt = " ".join(l.plain.strip() for l in s.lines)
            if substantive and (len(txt.split()) < 12 or "§" in txt):
                # BODY PROSE has substance: a caption cell ('§ Petition
                # Nos. 23-08774 §' — del) never runs 12+ words. Only the
                # callers that anchor WITHOUT a band ask for this.
                continue
            low = txt.lower()
            _marks_n = sum(1 for mk in (
                "appeal from", "for plaintiff", "for defendant",
                "for appellant", "for respondent", "for petitioner",
                "attorney general", "on brief", "counsel for")
                if mk in low)
            # apparatus/counsel marks veto SHORT segments; a MULTI-marked
            # block of any length is a counsel roster (calctapp);
            # a body paragraph OPENING on the appeal-from recital is still
            # the body (ca2's 14-line 'Appeal… UPON DUE CONSIDERATION…').
            # …unless a COURT READER already claimed the headmatter. The
            # veto exists because an appeal-from recital sits in the front
            # matter; when the front matter has been claimed and removed,
            # what is left opens the body, and vetoing it strands the first
            # pages of the writing in the headmatter (hampton: 52 rows).
            if _marks_n and (len(s.lines) <= 6 or _marks_n >= 2) \
                    and not headmatter_claimed:
                continue
            # a BENCH ROSTER row is never the body ('CHUNG, BOVE, MASCOTT,
            # Circuit Judges and…' — ca3 splits its Before roster).
            if len(s.lines) <= 3 and (
                    low.startswith("before")
                    or any(t in low for t in
                           ("circuit judge", "district judge",
                            "chief judge", "justice"))):
                continue
            # a block UNDER a 'FOR <ROLE>:' opener is that party's counsel
            # (ca2 sets the opener as its own one-line segment)
            if j > 0:
                _pv = " ".join(x.plain.strip()
                               for x in split_stream[j - 1].lines).lower()
                if (_pv.startswith("for ") and _pv.rstrip().endswith(":")
                        and all(len(x.plain.strip()) <= 60
                                for x in s.lines)):
                    continue
            letters = [c for c in txt if c.isalpha()]
            if not letters or sum(
                    1 for c in letters if c.islower()) < 0.5 * len(letters):
                continue
            return j
        return None

    # A writing may PRECEDE the first byline: ca3 prints its rehearing
    # ORDER (and 'OPINION OF THE COURT' texts) before the dissent's byline.
    # Body-size prose below the caption — not a syllabus, not counsel —
    # anchors a leading writing, taking a doc-type heading just above it.
    if starts:
        _first = starts[0]
        _j0 = _prose_anchor(0)
        # A measured band may run to the page foot (ca2's en banc denial):
        # prose inside it is not automatically caption matter — step past
        # the band and look again rather than abandoning the search.
        while (_j0 is not None and _j0 < _first and caption_band
               and split_stream[_j0].page == 1
               and split_stream[_j0].lines[0].top <= caption_band[1] + 4):
            _nxt = _prose_anchor(_j0 + 1)
            if _nxt is None or _nxt == _j0:
                break
            _j0 = _nxt
        if _j0 is not None and _j0 < _first:
            _lead_segs = split_stream[_j0:_first]
            _n = sum(len(s.lines) for s in _lead_segs)
            _bsz = geom.body_size if geom else 12.0
            _on_syl = bool(syl_pages) and any(
                s.page in syl_pages for s in _lead_segs)
            _in_band = (caption_band
                        and split_stream[_j0].page == 1
                        and split_stream[_j0].lines[0].top
                            <= caption_band[1] + 4)
            _szs = sorted(l.size for s in _lead_segs for l in s.lines
                          if l.size)
            _subbody = bool(_szs) and _szs[len(_szs) // 2] < _bsz - 1.0
            if _n >= 6 and not _on_syl and not _in_band and not _subbody:
                from ..classify import heading_doc_type as _hdt3
                _j = _j0
                while _j > 0:
                    _s = split_stream[_j - 1]
                    _t = " ".join(l.plain.strip() for l in _s.lines)
                    if (len(_s.lines) == 1 and len(_t) < 80
                            and _hdt3(_t) is not None):
                        _j -= 1
                    else:
                        break
                # A LEADING writing must be ANNOUNCED: ca3 heads its
                # rehearing order 'SUR PETITION FOR REHEARING' (which may
                # sit ABOVE the caption band). Without a doc-type heading
                # anywhere before it, front prose below the caption is
                # apparatus (ca9's appeal-from + staff summary pages
                # precede a page-4 byline).
                _announced = _j < _j0
                # …or the court PRONOUNCES its disposition in that prose
                # ('the petitions for rehearing en banc are hereby
                # DENIED.' — ca2's en banc denial leads its separate
                # writings with no heading and no byline).
                if not _announced:
                    _lead_txt = " ".join(
                        l.plain.strip() for s3 in _lead_segs
                        for l in s3.lines)
                    _lt = " ".join(_lead_txt.split())
                    if any(cue in _lt for cue in (
                            "hereby DENIED", "hereby GRANTED",
                            "hereby ORDERED", "hereby AFFIRMED",
                            "hereby DISMISSED", "IT IS ORDERED",
                            "IT IS HEREBY ORDERED", "are DENIED",
                            "is DENIED", "is GRANTED")):
                        _announced = True
                if not _announced:
                    for _s2 in split_stream[:_j0]:
                        _t2 = " ".join(l.plain.strip() for l in _s2.lines)
                        if not (len(_s2.lines) == 1 and len(_t2) < 80
                                and _hdt3(_t2) is not None):
                            continue
                        # a BANNER heading spans the measure or sits
                        # outside the caption band; a caption CELL
                        # ('OPINION' in ca9's right column) is neither
                        _l2 = _s2.lines[0]
                        _in_cap = (caption_band and _s2.page == 1
                                   and caption_band[0] - 4 <= _l2.top
                                   <= caption_band[1] + 4)
                        _wide = (_l2.x1 - _l2.x0) >= 0.45 * (
                            model.pages[_s2.page - 1].width
                            - 2 * (geom.body_x0 if geom else 72.0))
                        if not _in_cap or _wide:
                            _announced = True
                            break
                if _announced:
                    starts = [_j] + starts

    # A DOC-TYPE HEADING immediately above the first start belongs to the
    # writing ('OPINION*' right over the byline — ca3), unless it sits in
    # the caption band (ca9 names the document inside its caption).
    # A TITLE LINE above the byline is the writing's heading, not its
    # author: ca9 prints 'OPINION' over 'NGUYEN, Circuit Judge:', cadc
    # 'Opinion for the Court filed by Circuit Judge RAO.', ca3 'OPINION OF
    # THE COURT'. Anchor the writing at the TITLE but keep reading the
    # byline beneath it, so the author is never lost.
    _title_lead: dict[int, int] = {}

    if starts:
        from ..classify import heading_doc_type as _hdt4
        while starts[0] > 0:
            _s = split_stream[starts[0] - 1]
            _t = " ".join(l.plain.strip() for l in _s.lines).rstrip("*†‡∗⁎﹡＊ ")
            _in_band = (caption_band and _s.page == 1
                        and _s.lines[0].top <= caption_band[1] + 4)
            if (len(_s.lines) == 1 and len(_t) < 80 and not _in_band
                    and _hdt4(_t) is not None):
                starts[0] -= 1
                _title_lead[starts[0]] = _title_lead.get(starts[0], 0) + 1
            else:
                break

    order_start = None
    if not starts:
        from ..classify import heading_doc_type
        from ..model import DocType as _DT
        found = None   # (segment index, line)
        for i, seg in enumerate(split_stream):
            if seg.page > 2:
                break
            for line in seg.lines:
                head = line.plain.strip()
                # A HEADING STOPS SHORT OF THE MEASURE. Applied to every
                # short line, this test reads PROSE as a heading — ca10's
                # 'judgment becomes final. See 28 U.S.C. § 2244(d)(1)(A);
                # Preston v. Gibson,' matches JUDGMENT, and 'order to
                # deflect from his threats to Rusk…' matches ORDER — and
                # then anchors the writing there, splitting one opinion in
                # two at the page break. `_heading_candidates` already
                # excludes prose exactly this way; this path did not.
                _col = (geom.right_x1 - geom.body_x0) if geom else 0.0
                _wide = _col > 100 and (line.x1 - line.x0) >= 0.8 * _col
                dt = (None if _wide or len(head) >= 80
                      else heading_doc_type(head))
                # A STANDALONE DISPOSITION CLOSES A WRITING, IT DOES NOT
                # TITLE ONE. 'Judgment affirmed.' classifies as a JUDGMENT
                # heading, so a per curiam rescript whose front matter a
                # court reader has already claimed got anchored at its own
                # ruling; the `headmatter_claimed` rule below then prepends
                # `_body0` and KEEPS that later start, splitting one
                # writing in two at the line that ends it (mass murray,
                # mass gorbatova). This module already reads the line the
                # other way — `_is_dispo_line` is documented as the line
                # that TERMINATES a rescript.
                # Confined to a CLAIMED headmatter, where the stream is
                # body-only and `_body0` already opens the writing, so
                # dropping this anchor can only ever merge the two starts
                # back into one. Where the ruling IS the writing (lactapp's
                # 'WRIT DENIED.') no reader claimed the front matter, the
                # stream still carries the caption above the ruling, and
                # this never fires.
                if (dt is not None and headmatter_claimed and i > 0
                        and _is_dispo_line(head)):
                    continue
                # A NOTICE heading (errata sheet, sealed placeholder) never
                # opens a body — there is no writing to own.
                if dt is not None and dt is not _DT.NOTICE:
                    found = (i, line)
                    break
            if found:
                break
        if found:
            i, line = found
            order_start = i
            # A title INSIDE the caption band (akd's 'ORDER OF DISMISSAL',
            # ca9's 'MEMORANDUM*' — both in the caption's right column)
            # names the document but does not start its body — the body is
            # the first segment BELOW the caption.
            #
            # …UNLESS A COURT READER ALREADY TOOK THE BAND. Both examples
            # are caption CELLS: the heading is a cell of a caption still
            # standing in the stream, which is why the body must be sought
            # below it. Where a reader has claimed the headmatter those rows
            # are gone, so a doc-type heading that SURVIVES inside the band's
            # coordinates is not a cell — it is the writing's own title, and
            # pushing past it walks over the writing. pacommwct measures its
            # band down to the announcement, so 'MEMORANDUM OPINION BY' was
            # read as a caption cell and the anchor moved to the first
            # segment of page 2: city_of_lancaster came back as a 3-block
            # 'majority' holding the announcement and one paragraph, with
            # the whole opinion following it as an 82-block 'order' opening
            # on 'I. BACKGROUND' (the user, 2026-08-21: 'splitting into tweo
            # opnions when it really shouldnt').
            if (caption_band and line.page == 1 and not headmatter_claimed
                    and caption_band[0] - 4 <= line.top <= caption_band[1] + 4):
                _j0 = next(
                    (j for j, s in enumerate(split_stream)
                     if j > i and (s.page > 1
                                   or s.lines[0].top > caption_band[1] + 4)),
                    None)
                # first PROSE below the band — never a counsel roster
                # ('For Plaintiffs-Appellants:' anchored ca2's order).
                order_start = (_prose_anchor(_j0)
                               if _j0 is not None else None)
                if order_start is None:
                    order_start = _j0
            # A COVER banner heading ABOVE the caption ('CERTIFIED FOR
            # PUBLICATION' — calctapp) names the document too; the body is
            # the first PROSE below the caption, past appeal-from/counsel.
            elif (caption_band and line.page == 1 and not headmatter_claimed
                    and line.top < caption_band[0] - 4):
                j0 = next(
                    (j for j, s in enumerate(split_stream)
                     if j > i and (s.page > 1
                                   or s.lines[0].top > caption_band[1] + 4)),
                    None)
                if j0 is not None:
                    order_start = _prose_anchor(j0)
                    if order_start is None:
                        order_start = j0
        if order_start is not None:
            # Walk BACK over the writing's own head: an ORDER heading and
            # a 'rules as follows:' preamble above the anchor belong to
            # the opinion, not headmatter (del opens '(1) A grand jury…'
            # under both).
            while order_start > 0:
                s_ = split_stream[order_start - 1]
                stxt = " ".join(l.plain.strip() for l in s_.lines)
                letters = [c for c in stxt if c.isalpha()]
                is_head = (len(s_.lines) == 1 and len(stxt) < 80
                           and heading_doc_type(stxt) is not None)
                is_preamble = (
                    len(s_.lines) <= 3 and stxt.rstrip().endswith(":")
                    and letters
                    and sum(1 for c in letters if c.islower())
                        >= 0.5 * len(letters))
                # a MID-CLAUSE tail belongs to the sentence the anchor
                # opens ('UPON DUE CONSIDERATION, IT IS HEREBY ORDERED,
                # ADJUDGED, AND' / 'DECREED that…' — ca2)
                _tail_word = stxt.rstrip().rsplit(" ", 1)[-1]                     .rstrip(",;").lower() if stxt.strip() else ""
                is_open_tail = (
                    len(s_.lines) <= 2 and bool(stxt.strip())
                    and (_tail_word in ("and", "or")
                         or stxt.rstrip().endswith((",", ";"))))
                if is_head or is_preamble or is_open_tail:
                    order_start -= 1
                else:
                    break
            starts = [order_start]

    # A CLAIMED HEADMATTER LEAVES A BODY-ONLY STREAM. If a court reader took
    # the front matter, whatever remains above the first writing is that
    # writing's own opening — not headmatter to be left behind. Applied after
    # every anchor path has run, since the start may come from a byline, a
    # doc-type heading or the prose walk (hampton stranded 52 rows —
    # 'Appeal from a judgment of the United States District Court for the
    # Western District of New York (Geraci, J.).' onward — above a majority
    # of 28 blocks).
    if headmatter_claimed and split_stream:
        # A claimed headmatter leaves a BODY-ONLY stream, so its first
        # segment opens the writing — whether an anchor was found deeper
        # (reorder it) or none was found at all (there is nothing else the
        # first segment could be). Without the second case a court reader
        # that succeeds on an unsigned document costs it every writing, and
        # the claim is withdrawn for want of an anchor it already implies.
        # …below the court's FRONT MATTER. A reader need not claim from the
        # first page: scotus claims the opinion's own cover, and the
        # Reporter's syllabus is printed above it — read as the writing's
        # opening, the syllabus came back as an unsigned 'order' and the
        # document lost its syllabus entirely. A page the court NAMED as
        # syllabus is never a writing's first segment.
        _body0 = next((i for i, s in enumerate(split_stream)
                       if s.page not in (syl_pages or ())), 0)
        # …and neither is the HEADING of a section the court publishes ahead
        # of its opinion. ca9 prints its staff summary between the roster —
        # the last row its reader claims — and the appearances, so the first
        # segment left is 'SUMMARY**'. Opening the writing there costs the
        # document that section AND hands it a phantom unsigned writing made
        # of the summary's own prose. The rule 25 lines below already knows
        # this case; it guards only the panel-line path, not this one.
        # Keyed on the SEGMENT, not the profile: keying on `front_matter`
        # alone breaks three scotus sentinels.
        _fm0 = bool(front_matter) and bool(split_stream[_body0].lines) and (
            " ".join(split_stream[_body0].lines[0].plain.split())
            .rstrip(" :*†‡∗⁎﹡＊").lower()
            in front_matter)
        if starts and starts[0] > _body0 and not _fm0:
            # …AND A WRITING NEVER OPENS MID-SENTENCE. Prepending the body's
            # first segment keeps the deeper anchor as a SECOND writing, and
            # where that anchor is only the same paragraph continuing over a
            # page break the document is handed a writing it never had: mo's
            # millstone broke at 'were sold to another entity. This' | 'also
            # received an assignment of developer rights', 1 block against
            # 57, and vernell_beach at 'issued a permanent writ' | 'first
            # entering a preliminary order in mandamus'. The byline path has
            # refused this since it was written (see `_midsentence_tail`
            # above); only the rescue paths never asked.
            # `_midsentence_tail` is not the test to use here: it asks
            # whether a ROSTER was cut mid-name, so it looks for a trailing
            # comma or 'and'. A paragraph broken by a page turn ends on an
            # ordinary word — 'were sold to another entity. This' — and that
            # is just as plainly unfinished.
            # BOTH HALVES OF THE BREAK HAVE TO SAY SO. An open sentence
            # alone is far too weak a test — a heading, a roster and a
            # caption cell all end without a terminal, and dropping every
            # anchor behind one cost 22 sentinels across 12 courts. What a
            # broken PARAGRAPH also shows is where it resumes: on a
            # lowercase word. A writing does not open on 'also received an
            # assignment of developer rights' or 'first entering a
            # preliminary order in mandamus'.
            def _paragraph_runs_on(prev, nxt) -> bool:
                if not prev.lines or not nxt.lines:
                    return False
                s = " ".join((prev.lines[-1].plain or "").split()).rstrip()
                s = s.rstrip("*†‡∗⁎﹡＊0123456789") if s.endswith(
                    tuple("*†‡∗⁎﹡＊0123456789")) else s
                if s.endswith((".", "?", "!", '"', "”", "’", ")", ":")):
                    return False
                head = " ".join((nxt.lines[0].plain or "").split())
                first = head.split(" ", 1)[0].lstrip("“\"'([")
                return bool(first) and first[:1].islower()

            starts = [_body0] + [
                x for x in starts
                if x > _body0 and not _paragraph_runs_on(
                    split_stream[x - 1], split_stream[x])]
        elif not starts and not _fm0:
            starts = [_body0]
    starts = [x for x in starts if 0 <= x < len(split_stream)]

    # THE PANEL LINE CLOSES THE HEADMATTER. When a document names itself
    # with a doc-type heading and then prints its bench roster ('ORDER AND
    # JUDGMENT*' / 'Before EID, EBEL, and FEDERICO, Circuit Judges.'),
    # everything after that roster is the writing — whether or not any
    # judge signs it. Recognizing the boundary matters more than naming
    # the author: without this the whole body renders as headmatter rows.
    # …and also when a LATER writing was found but the lead one was not:
    # ol_private's concurrence anchors while the majority (unsigned, under
    # 'ORDER AND JUDGMENT' + panel line) would otherwise stay headmatter.
    # (Courts that publish front matter print prose under the panel line
    # that is NOT the body — ca9's staff summary — so this boundary rule
    # applies only where the profile declares none.)
    _lifted_cells: list[Segment] = []
    if not front_matter:
        from ..classify import heading_doc_type as _hdt6
        _titled = None
        for _i, _s in enumerate(split_stream):
            if _s.page > 2:
                break
            for _l in _s.lines:
                _t = _l.plain.strip().rstrip("*†‡∗⁎﹡＊ ")
                if len(_t) < 80 and _hdt6(_t) is not None:
                    _titled = _i
                    break
            if _titled is not None:
                break
        # A roster with NO doc-type heading above it still closes the
        # headmatter — lactapp's writ rulings run caption / 'BEFORE: WOLFE,
        # STROMBERG, AND BALFOUR, JJ.' / 'WRIT DENIED. …' and name
        # themselves nowhere. Allowed only when nothing else found a
        # writing, so this can rescue a total miss but never move a
        # boundary that already works.
        if _titled is None and not starts:
            _titled = 0
        # `if _titled` discards the rescue: it sets _titled = 0, and zero is
        # falsy, so a document whose writing opens at the very first segment
        # (no doc-type heading, no byline — an unsigned order whose
        # headmatter a court reader has already claimed) came back with no
        # opinion at all.
        _named = _titled if _titled is not None else None
        _rostered = False
        if _titled is not None:
            for _j in range(_titled, min(len(split_stream), _titled + 12)):
                _tx = " ".join(l.plain.strip()
                               for l in split_stream[_j].lines)
                _low = " ".join(_tx.split()).lower()
                # 'Before' may stand ALONE on its own line with the panel
                # named beneath it (bap1 sets it that way), so an exact
                # match counts as much as a prefix.
                if not (_low.startswith(("before ", "before:", "present:",
                                         "panel:"))
                        or _low in ("before", "present", "panel")):
                    continue
                _rostered = True
                _after = _prose_anchor(_j + 1)
                if _after is None and not starts:
                    # The ruling may BE one line ('WRIT DENIED.'), which is
                    # never prose-shaped. The court still ruled.
                    for _d in range(_j + 1, len(split_stream)):
                        if any(_is_dispo_line(l.plain)
                               for l in split_stream[_d].lines):
                            _after = _d
                            break
                if _after is not None and (not starts or _after < starts[0]):
                    starts = [_after] + [x for x in starts if x > _after]
                    trace.event("body.panel-line-boundary",
                                f"start after roster @seg{_j}")
                break

        # A DOC-TYPE HEADING CLOSES THE HEADMATTER ON ITS OWN. A court that
        # prints 'ORDER' under its caption has begun the writing — no roster
        # required. del's single-justice orders have no panel line, so
        # without this the entire narrative ('On April 20, 2026, the Chief
        # Deputy Clerk sent a notice…') stayed in headmatter and only the
        # closing 'NOW, THEREFORE, IT IS ORDERED' paragraph became the body.
        # The heading is kept as the writing's own heading, matching the
        # del orders that already parse correctly via their roster.
        # This can only move the boundary EARLIER — it reclaims stranded
        # headmatter and never pushes a working start later.
        # …but ONLY when the writing that was found did not open on a
        # printed byline. If the court signs its opinion ('BLOCK, Circuit
        # Judge.'), that byline is the true opening and the heading above it
        # is its title — already handled by the title-skip below. Overriding
        # there split ca2/ca6/pa majorities in two.
        # A heading only closes the headmatter if HEADMATTER DOES NOT
        # FOLLOW IT. ca2 prints 'SUMMARY ORDER' at the top of the page,
        # above the caption and the counsel roster; treating that as the
        # body's start swallowed the whole headmatter (perez_v._porter lost
        # all 11 attorneys). del prints 'ORDER' with nothing but the writing
        # beneath it. Test by what comes after, not by the measured band —
        # del's band runs past its heading.
        if _named is not None:
            _apparatus = ("for appellant", "for appellee", "appearances",
                          "counsel for", "for plaintiff", "for defendant",
                          "attorney for", "for petitioner", "for respondent",
                          # a ROSTER or a party designation below the
                          # heading means the caption has not happened yet
                          # (ca2 sets 'SUMMARY ORDER' above 'PRESENT: …'
                          # and the whole party block)
                          "present:", "circuit judges", "plaintiff-appell",
                          "defendant-appell", "petitioner-appell",
                          "respondent-appell")
            # A bare CAPTION CELL below the heading means the heading sits
            # INSIDE the caption, not under it: azd prints 'ORDER' as the
            # caption's right-hand cell, so anchoring there split the
            # caption and pushed 'v. Teresa Hunter,' / 'Defendant.' into
            # the body with no parties left behind.
            _cells = ("plaintiff", "defendant", "plaintiffs", "defendants",
                      "petitioner", "respondent", "appellant", "appellee",
                      "real party in interest")
            _last_cell = None
            _cell_idx: list[int] = []
            for _q in range(_named + 1,
                            min(len(split_stream), _named + 10)):
                _qt = " ".join(" ".join(l.plain.split())
                               for l in split_stream[_q].lines).lower()
                _bare = _qt.strip(" .,;:")
                if any(k in _qt for k in _apparatus):
                    _named = None      # a cover page: the caption is below
                    break
                if (_bare in _cells
                        or _qt.startswith(("v. ", "vs. ", "v ."))
                        or set(_qt) <= {")", "(", ":", " "} and _qt.strip()):
                    _last_cell = _q    # still inside the caption
                    _cell_idx.append(_q)
            # The heading sat INSIDE the caption (azd prints 'ORDER' as the
            # caption's right-hand cell). LIFT the interleaved cells into
            # the headmatter where they belong, rather than stepping the
            # anchor past them — stepping past also skipped calctapp's
            # 'ORDER DENYING PETITION FOR REHEARING' heading, which is what
            # types that writing as an order rather than a majority.
            # …but never when a COURT READER already claimed the caption:
            # there are no interleaved cells left to lift, and lifting the
            # body's own first segment empties the anchor that was just
            # found (suhel: rescue anchors seg0, the lift removes it, and
            # the document comes back with no writing at all).
            if (_named is not None and _last_cell is not None
                    and not headmatter_claimed):
                _lift = {id(split_stream[_q]) for _q in _cell_idx}
                # deferred: headmatter_segments is reassigned below
                _lifted_cells.extend(split_stream[_q] for _q in _cell_idx)
                _keep = [s for s in split_stream if id(s) not in _lift]
                _pos2 = {id(s): i for i, s in enumerate(_keep)}
                _named = _pos2.get(id(split_stream[_named]), _named)
                starts = sorted({_pos2[i] for i in
                                 (id(split_stream[s]) for s in starts)
                                 if i in _pos2})
                split_stream = _keep
        # `<=`, not `<`: when a COURT READER has already claimed the
        # headmatter the doc-type heading IS the first segment left, so
        # _named == starts[0] and the rule that prunes the heuristic
        # anchors below it never fired — ala's certificate of judgment
        # came out as [majority 'CERTIFICATE OF JUDGMENT …'] plus a
        # phantom [order] opened at its second 'WHEREAS'.
        if (_named is not None and not _rostered
                and (not starts
                     or (_named <= starts[0]
                         and not head_byline(split_stream[starts[0]])[0]))):
            # Later starts survive only if the page PRINTS a byline there.
            # The others were heuristic anchors (the disposition
            # pronouncement) that found this same writing from its tail —
            # inside an already-open order, 'NOW, THEREFORE, IT IS ORDERED'
            # is the conclusion, not a second writing.
            starts = [_named] + [x for x in starts if x > _named
                                 and head_byline(split_stream[x])[0]]
            trace.event("body.doc-type-heading",
                        f"heading closes headmatter @seg{_named}")

    # A RESCRIPT (mass): an unsigned opinion with no byline anywhere whose
    # body closes 'So ordered.' — the court's own terminator vouches for a
    # writing even when nothing opens one.
    # The terminator is a STANDALONE disposition line ('So ordered.' /
    # 'Judgment affirmed.' / 'Petition denied.' — mass sets rescripts with
    # no byline at all).
    rescript = doc_type == m.DocType.UNKNOWN and any(
        " ".join(l.plain.split()).lower().rstrip(".") in _DISPO
        for s in split_stream for l in s.lines)
    # Trailing CONCUR VOTES prove a writing even when its author signs only
    # as a graphic ('John P. Torbitzky, C.J., concurs.' — moctapp).
    import re as _re
    votes = doc_type == m.DocType.UNKNOWN and any(
        _re.search(r",\s+(?:C\. ?J\.|P\. ?J\.|J\.|JJ\.),?\s+"
                   r"(?:concurs?|dissents?)\.?\s*$",
                   " ".join(l.plain.split()))
        or _re.search(r"[–—-]\s*(?:CONCURS?|DISSENTS?|OPINION AUTHOR)\s*$",
                      " ".join(l.plain.split()), _re.IGNORECASE)
        for s in split_stream[-4:] for l in s.lines)
    if not starts and (doc_type == m.DocType.ORDER or rescript or votes):
        # An ANNOUNCED order with neither byline nor banner ('The Court of
        # Appeals hereby passes the following order:' — gactapp): the
        # writing opens right after the announcement, past the docket
        # caption row ('A26D0635. BRANCH v. RAM PARTNERS…').
        cue_idx = None
        for j, s in enumerate(split_stream):
            low = " ".join(" ".join(l.plain.split()) for l in s.lines).lower()
            if ("hereby passes the following order" in low
                    or "hereby enters the following order" in low):
                cue_idx = j
                break
        if cue_idx is not None:
            k = cue_idx + 1
            while (k < len(split_stream)
                   and len(split_stream[k].lines) <= 3
                   and " V. " in " ".join(
                       l.plain for l in split_stream[k].lines).upper()):
                k += 1
            if k < len(split_stream):
                starts = [k]
        if not starts:
            for j, s in enumerate(split_stream):
                if len(s.lines) < 2:
                    continue
                if (caption_band and s.page == 1
                        and s.lines[0].top <= caption_band[1] + 4):
                    continue
                starts = [j]
                break

    # A demoted END-SIGNATURE names an author but may have no heading to
    # anchor the body (calctapp's unpublished covers) — the body itself is
    # the writing.
    # A CONFORMED SIGNATURE at the end proves the document IS a writing,
    # even with no heading and no byline: del closes its dismissal orders
    # 'BY THE COURT: / /s Abigail M. LeGrow / Justice'. The body is the
    # prose below the caption; the signer is its author.
    if not starts and terminal_author is None:
        _sig_name = conformed_signature_author(
            [l.plain for pm in model.pages for l in pm.lines])
        if _sig_name:
            # No band gate: a measured band may be the crude 55%-of-page
            # fallback (del) and would swallow the body. The prose test
            # already rejects caption cells — they are short, not
            # full-measure.
            _anchor = _prose_anchor(0, substantive=True)
            if _anchor is not None:
                starts = [_anchor]
                trace.event("body.conformed-signature",
                            f"{_sig_name[:40]!r} anchors body @seg{_anchor}")

    if not starts and terminal_author is not None:
        for j, s in enumerate(split_stream):
            if len(s.lines) < 2:
                continue
            if (caption_band and s.page == 1
                    and s.lines[0].top <= caption_band[1] + 4):
                continue
            # The anchor must be BODY PROSE — not the court banner, the
            # appeal-from line, or the counsel roster (calctapp's whole
            # front matter was swallowed into the writing here).
            txt = " ".join(l.plain.strip() for l in s.lines)
            low = txt.lower()
            _marks_n = sum(1 for mk in (
                "appeal from", "for plaintiff", "for defendant",
                "for appellant", "for respondent", "for petitioner",
                "attorney general", "on brief", "counsel for")
                if mk in low)
            # apparatus/counsel marks veto SHORT segments; a MULTI-marked
            # block of any length is a counsel roster (calctapp);
            # a body paragraph OPENING on the appeal-from recital is still
            # the body (ca2's 14-line 'Appeal… UPON DUE CONSIDERATION…').
            if _marks_n and (len(s.lines) <= 6 or _marks_n >= 2):
                continue
            # a BENCH ROSTER row is never the body ('CHUNG, BOVE, MASCOTT,
            # Circuit Judges and…' — ca3 splits its Before roster).
            if len(s.lines) <= 3 and (
                    low.startswith("before")
                    or any(t in low for t in
                           ("circuit judge", "district judge",
                            "chief judge", "justice"))):
                continue
            # a block UNDER a 'FOR <ROLE>:' opener is that party's counsel
            # (ca2 sets the opener as its own one-line segment)
            if j > 0:
                _pv = " ".join(x.plain.strip()
                               for x in split_stream[j - 1].lines).lower()
                if (_pv.startswith("for ") and _pv.rstrip().endswith(":")
                        and all(len(x.plain.strip()) <= 60
                                for x in s.lines)):
                    continue
            letters = [c for c in txt if c.isalpha()]
            if not letters or sum(
                    1 for c in letters if c.islower()) < 0.5 * len(letters):
                continue   # an all-caps banner, never a paragraph
            starts = [j]
            break

    # WRITINGS THE COURT DECLARES, because it prints a COVER for each one.
    # Every rule above finds a writing by its BYLINE. A court that heads each
    # separate paper with its full masthead — banner, caption, docket — and a
    # title, and then signs it only at the FOOT, states its boundaries
    # somewhere no byline test can look: mo prints 'DISSENTING OPINION' over
    # a fresh cover on page 11 and signs 'Paul C. Wilson, Judge' on page 28,
    # so all 13 of its records that carry a separate writing merged it into
    # the one before — 16 writings, and the majority credited to whoever
    # signed LAST (r.m.a.: 141 blocks under the dissenter's name).
    #
    # The court answers with the LINE its writing opens on and the KIND its
    # own title states; the phrase goes through `normalize_opinion_type` like
    # any byline's, so the vocabulary stays in one place. Placed here, before
    # the gate below, so the boundary survives every rebuild of `starts`
    # underneath it — and keyed by segment IDENTITY, which the rebuilds
    # preserve where indices do not. A court that declares nothing reaches
    # none of this.
    _declared: dict[int, str] = {}
    if writing_starts:
        _seg_of = {l.id: i for i, s in enumerate(split_stream)
                   for l in s.lines}
        for _lid, _kind in writing_starts.items():
            _i = _seg_of.get(_lid)
            # never BEFORE the first writing: a declaration is for a paper
            # stapled behind one, and an earlier index would take the
            # headmatter with it. AT the first writing is not before it —
            # the boundary does not move, and the court is naming the kind
            # of the paper that already opens there. Refusing that cost
            # pacommwct's passhe its type: the announcement is 'OPINION1'
            # (the court hangs a footnote mark on the paper's own name), so
            # `heading_doc_type` does not recognise it, the head goes
            # unsigned and an unsigned head types `order` — the lead
            # opinion of a 31-page en banc case came back an order.
            # …and index 0 is only 'before the first writing' while the
            # caption still stands there. Under a CLAIMED headmatter the
            # stream is body-only and segment 0 IS the first writing, which
            # is where passhe's announcement stands.
            if (_i is None or (starts and _i < starts[0])
                    or (_i == 0 and not headmatter_claimed)):
                continue
            starts.append(_i)
            _declared[id(split_stream[_i])] = _kind
        if _declared:
            starts = sorted(set(starts))
            trace.event("writing.covers",
                        f"{len(_declared)} declared: "
                        + ", ".join(sorted(_declared.values())))

    if not starts:
        result.headmatter_segments = split_stream
        result.warnings.append("no opinion start found")
        return result

    result.headmatter_segments = split_stream[:starts[0]]
    # caption cells lifted out of a heading-anchored writing (see above)
    result.headmatter_segments.extend(_lifted_cells)
    # caption run-on segments AFTER the first start are headmatter too
    # …and not when a court reader claimed the headmatter: it has already
    # taken the caption, run-on and all, so moving a whole page back into
    # the headmatter here takes the body's first segment with it and leaves
    # no writing at all (suhel's caption runs onto page 2, where its opinion
    # also begins).
    if _runon and not headmatter_claimed:
        _keep, _moved = [], []
        for _sg in split_stream[starts[0]:]:
            (_moved if _sg.page in _runon else _keep).append(_sg)
        if _moved:
            result.headmatter_segments.extend(_moved)
            _drop = {id(x) for x in _moved}
            # `starts` indexes the OLD stream; rebuild it against the new
            # one by identity, or the bounds below run off the end.
            _start_ids = [id(split_stream[s]) for s in starts]
            split_stream = (split_stream[:starts[0]]
                            + [x for x in split_stream[starts[0]:]
                               if id(x) not in _drop])
            _pos = {id(x): i for i, x in enumerate(split_stream)}
            starts = sorted({_pos[i] for i in _start_ids if i in _pos})
            if not starts:
                # every start got absorbed as caption: keep BOTH halves
                # (the already-extended _moved and what remains).
                result.headmatter_segments = (
                    result.headmatter_segments + split_stream)
                result.warnings.append("no opinion start found")
                return result

    # Build each writing. Every start must still address a segment: the
    # stream is rebuilt above (lifted caption cells, dropped run-ons), and a
    # court reader may claim the whole of it, which leaves the rescue anchor
    # pointing at nothing.
    starts = sorted({x for x in starts if 0 <= x < len(split_stream)})
    bounds = [*starts, len(split_stream)]
    # The writing's own segmenter carries the court's paragraph indent — the
    # body is split by the same fact as the front matter, or a court whose
    # indent is narrower than the default loses every break in its opinions.
    segmenter = Segmenter(geom, model.pages[0].width,
                          para_indent_min=para_indent_min,
                          tables=_tables)
    all_lines_text = [l.plain for pm in model.pages for l in pm.lines]
    for a, b in zip(bounds[:-1], bounds[1:]):
        head_seg = split_stream[a]
        head_line = head_seg.lines[0]
        byline, head_text, consumed = head_byline(head_seg)
        # The writing may OPEN on its title ('OPINION' / 'OPINION OF THE
        # COURT' / 'Opinion for the Court filed by Circuit Judge RAO.'):
        # the byline is the next segment — read it, keep the title as the
        # writing's heading, and never leave the author empty.
        _title_segs: list[Segment] = []
        _k = a
        while (byline is None and _k + 1 < b
               and len(split_stream[_k].lines) <= 2):
            _ttxt = " ".join(l.plain.strip()
                             for l in split_stream[_k].lines)
            from ..classify import heading_doc_type as _hdt5
            _is_title = (len(_ttxt) < 80
                         and (_hdt5(_ttxt) is not None
                              or _ttxt.lower().startswith(
                                  ("opinion by", "opinion for the court",
                                   "opinion of the court"))))
            if not _is_title:
                break
            _nb, _nt, _nc = head_byline(split_stream[_k + 1])
            if _nb is None:
                break
            _title_segs.append(split_stream[_k])
            _k += 1
            head_seg = split_stream[_k]
            head_line = head_seg.lines[0]
            byline, head_text, consumed = _nb, _nt, _nc
        if head_text is None:
            head_text = byline_text(head_line) or head_line.plain.strip()
        if byline is not None:
            author_text = head_text[:byline.end].strip()
            _taken = head_seg.lines[:max(consumed, 1)]
            byline_ids = [l.id for l in _taken]
            if head_line.row is not None:
                byline_ids += [l.id for l in head_seg.lines
                               if l.row == head_line.row
                               and l.page == head_line.page
                               and l.id not in byline_ids]
            # A WRAPPED HEADING'S ROW-MATE IS ON ITS LAST LINE, not its first.
            # pacommwct folds the heading over two rows and sets the filing
            # date flush right beside the SECOND — 'CONCURRING/DISSENTING
            # OPINION' / 'BY JUDGE COVEY   FILED: May 13, 2026'. The head
            # line's own row is None there, so the date was left behind and
            # opened the dissent as its first paragraph.
            _last = _taken[-1] if _taken else head_line
            byline_ids += [l.id for l in head_seg.lines
                           if l.page == _last.page
                           and abs(l.top - _last.top) < 2.0
                           and l.id not in byline_ids]
            op = m.Opinion(type=normalize_opinion_type(
                               byline.kind if byline.name != "PER CURIAM"
                               else "per curiam"),
                           author=author_text,
                           author_name=byline.name, author_title=byline.title,
                           author_prov=m.Prov(head_line.page, tuple(byline_ids)))
            # The TITLE line(s) we stepped over to reach the byline are the
            # writing's own heading — they belong to it, not to nowhere
            # (unplaced lines resurface as residual content).
            for _ts in _title_segs:
                op.blocks.append(m.Heading(
                    text=" ".join(l.plain.strip() for l in _ts.lines),
                    prov=_prov(_ts.lines)))
            body_segs = []
            inline_rest = head_text[byline.end:].strip()
            # Skip the consumed byline line(s) and any row-mates already
            # folded into head_text.
            rest_lines = [l for l in head_seg.lines[max(consumed, 1):]
                          if not (head_line.row is not None
                                  and l.row == head_line.row
                                  and l.page == head_line.page)]
            if inline_rest:
                combined = " ".join(x for x in (inline_rest,
                                                _join(rest_lines, vocab)) if x)
                op.blocks.append(m.Paragraph(
                    text=combined, prov=_prov(head_seg.lines)))
            elif rest_lines:
                body_segs.append(Segment(head_seg.page, rest_lines, "body"))
        else:
            from ..classify import heading_doc_type
            from ..model import DocType
            # A DOCUMENT OF DECLARED WRITINGS SIGNS EACH ONE SEPARATELY.
            # The conformed signature is read from the whole document, which
            # is right where there is one writing and wrong the moment there
            # are two: mo's d.j. carries Fischer's name on page 10 and
            # Wilson's on page 28, and the whole-document read returns the
            # LAST — so the principal opinion came back authored by the
            # dissenter. Where the court declared the boundaries it also
            # told us how far each writing reaches, so each one is signed
            # from its OWN lines. Scoped to declaring documents: everywhere
            # else this is the same call on the same text as before.
            sig_author = conformed_signature_author(
                [l.plain for _s6 in split_stream[a:b] for l in _s6.lines]
                if _declared else all_lines_text)
            dt = heading_doc_type(head_text[:80])
            # An unsigned MEMORANDUM disposition (ca9) is the court's opinion;
            # an unsigned ORDER stays an order. A demoted terminal byline
            # ('Per Curiam' at a judgment's end) names the author. A prose
            # head with no heading inherits the DOCUMENT's classification
            # ('CERTIFIED FOR PUBLICATION' — calctapp — is an opinion).
            if dt is None and doc_type == DocType.OPINION:
                dt = DocType.OPINION
            op_type = "order" if dt in (DocType.ORDER, None) else "majority"
            # An UNSIGNED writing that pronounces a disposition is an
            # ORDER whatever the document is overall (calctapp staples a
            # rehearing denial in front of the opinion it modifies).
            _head_txt = " ".join(
                " ".join(l.plain.split()) for s4 in [head_seg]
                for l in s4.lines)
            if any(cue in _head_txt for cue in (
                    "is DENIED", "are DENIED", "is GRANTED",
                    "IT IS ORDERED", "IT IS HEREBY ORDERED",
                    "hereby DENIED", "hereby GRANTED",
                    # …AND A COURT MAY SAY IT IN ORDINARY TYPE. The cues
                    # above are a court SHOUTING its disposition, which is
                    # the common form; calctapp staples a modification order
                    # in front of the opinion it modifies and opens it 'THE
                    # COURT: It is ordered that the opinion filed herein on
                    # July 20, 2026, be modified as follows', in sentence
                    # case. It typed as `order` only while the segment's rail
                    # was mismeasured at 312; with the rail measured right it
                    # fell through to `majority` — the front matter of
                    # calctapp/bates_v._city_of_temecula_ca41 is an order
                    # either way (guard, 2026-08-23). Only the ordering
                    # phrases are case-folded here: 'is denied' in sentence
                    # case is something an opinion says about an argument.
                    "It is ordered", "It is hereby ordered",
                    "it is ordered", "it is hereby ordered")):
                op_type = "order"
            # …AND THE KIND THE COURT'S OWN TITLE STATES WINS. Nothing else
            # here can name it: an unsigned head types `majority` or `order`
            # off the doc-type heading, and every one of mo's separate
            # papers is titled 'OPINION' — so a dissent and a concurrence
            # both came back `majority`. The phrase is normalised exactly as
            # a byline's kind clause is.
            _dec_kind = _declared.get(id(head_seg))
            if _dec_kind:
                op_type = normalize_opinion_type(_dec_kind)
            author = sig_author or ""
            # A terminal byline is the ONE document's sign-off, so it cannot
            # speak for a document of several papers — it would put the same
            # name on all of them. Where the court declared the boundaries,
            # each writing has already been signed from its own lines.
            if terminal_author is not None and not _declared:
                author = terminal_author[1][:terminal_author[0].end].strip()
                op_type = ("per-curiam"
                           if terminal_author[0].name == "PER CURIAM"
                           else op_type)
            op = m.Opinion(type=op_type, author=author)
            body_segs = [head_seg]
        writing_segs = body_segs + split_stream[a + 1:b]
        # A PROSE AUTHORSHIP byline ('BIVINS, J., delivered the opinion…',
        # tenn's accept_delivered form) names the author, but the WRITING
        # starts at its OPINION banner — the joined-roster tail and the
        # counsel paragraphs between them are front matter.
        if (byline is not None and parser.g.accept_delivered
                and byline.kind is None):
            # THE BANNER IS A LINE, NOT NECESSARILY A SEGMENT. Requiring
            # the segment to hold exactly one line missed every record whose
            # banner is tightly leaded above the heading under it: the two
            # rows segment TOGETHER, so the banner was neither isolated nor
            # found, and the writing opened on 'OPINION I. Facts' as one
            # welded heading — 9 of tenncrimapp's 42 (the user, 2026-08-21:
            # 'opinion should be its own line'). The test now reads the
            # segment's FIRST line and splits the segment there, which keeps
            # it just as tight: the line itself must be exactly the banner.
            banner_at = next(
                (k for k, s in enumerate(writing_segs[:12])
                 if s.lines
                 and s.lines[0].plain.strip().upper().replace(" ", "")
                     in ("OPINION", "ORDER", "MEMORANDUMOPINION")),
                None)
            if banner_at is not None:
                _bs = writing_segs[banner_at]
                if len(_bs.lines) > 1:
                    from .segments import Segment as _SegB
                    writing_segs[banner_at:banner_at + 1] = [
                        _SegB(_bs.page, _bs.lines[:1], _bs.kind),
                        _SegB(_bs.page, _bs.lines[1:], _bs.kind)]
                result.headmatter_segments.extend(writing_segs[:banner_at])
                # The banner itself is the writing's HEADING — keep it.
                writing_segs = writing_segs[banner_at:]
        def _flush_merge(blocks):
            """Rejoin a paragraph the PAGE BREAK split: the first half ends
            mid-sentence and the second half opens lowercase — one thought,
            two sheets."""
            from ..audit import strip_tags
            merged = []
            # The page the TAIL of merged[-1] currently sits on. The merged
            # paragraph keeps its FIRST page in `prov` (it starts there, and
            # that is what `data-pg` should say), so comparing the next
            # block against `prov.page` re-reports the same turn on every
            # further block of the new page: fla/kaczmar merged eight blocks
            # off page 88 onto a paragraph opening on 87 and printed '88'
            # eight times, welded into the prose at each line join.
            tail_pg: list[int] = []
            for b in blocks:
                prev_plain = (strip_tags(merged[-1].text).rstrip()
                              if merged and isinstance(merged[-1], m.Paragraph)
                              else "")
                # A continuation may come back MISCLASSIFIED as a blockquote
                # (an indented body rail reads as a quote) — a real quote
                # never opens lowercase mid-sentence.
                next_plain = (strip_tags(b.text).lstrip()
                              if isinstance(b, (m.Paragraph, m.Blockquote))
                              and b.text else "")
                if (prev_plain and next_plain
                        and prev_plain[-1:] not in ".!?:;\"”’"
                        and next_plain[:1].islower()):
                    prev = merged[-1]
                    joined = prev.text.rstrip()
                    # the turn happens HERE, inside the sentence — mark it
                    _mk = (f'<pagenumber value="{b.prov.page}"/>'
                           if b.prov.page != tail_pg[-1] else "")
                    if joined.endswith("-"):
                        joined = joined + _mk + b.text.lstrip()
                    else:
                        # The marker takes a space on BOTH sides. Welding it
                        # to the next word printed 'respective plans 5of
                        # reorganization' — v1 sets '… plans 5 of …' (bap1
                        # banco_popular, and ~62k times across the corpus).
                        joined = (joined + " " + _mk
                                  + (" " if _mk else "") + b.text.lstrip())
                    merged[-1] = m.Paragraph(
                        text=joined,
                        prov=m.Prov(prev.prov.page,
                                    tuple(prev.prov.line_ids)
                                    + tuple(b.prov.line_ids)))
                    tail_pg[-1] = b.prov.page
                else:
                    merged.append(b)
                    tail_pg.append(getattr(getattr(b, "prov", None),
                                           "page", 0))
            return merged

        # Lines the byline row already claimed must not render again: a
        # '¶ 1.' marker piece and its 'CARROLL, J. Landowner…' row-mate can
        # land in DIFFERENT segments, and the row-mate re-rendered its text
        # as a duplicate paragraph (vt/wis).
        _claimed = set(op.author_prov.line_ids) if byline is not None else set()
        if byline is not None and head_line.row is not None:
            _claimed |= {l.id for s in writing_segs for l in s.lines
                         if l.row == head_line.row
                         and l.page == head_line.page}
        result.consumed_ids.update(_claimed)
        attesting = False
        segmenter.body_lead = _body_lead
        writing_segs = _weld_unspaced(writing_segs, _body_lead, parser)
        for seg in writing_segs:
            if _claimed:
                kept_lines = [l for l in seg.lines if l.id not in _claimed]
                if not kept_lines:
                    continue
                if len(kept_lines) != len(seg.lines):
                    seg = Segment(seg.page, kept_lines, seg.kind)
            if seg.kind == "separator":
                result.consumed_ids.update(l.id for l in seg.lines)
                continue
            # The clerk's extract certificate closes an announced order
            # ("Clerk's Office, Atlanta… / I certify that the above is a
            # true extract… / Witness my signature and the seal… / , Clerk.")
            # — court furniture, never body.
            low = " ".join(l.plain for l in seg.lines).lower()
            hits = sum(1 for c in ("certify that the above is a true extract",
                                   "witness my signature", "seal of said court",
                                   "clerk’s office", "clerk's office", ", clerk")
                       if c in low)
            if hits >= 2 or (attesting and hits >= 1):
                attesting = True
                result.consumed_ids.update(l.id for l in seg.lines)
                # Deliberate removal, surfaced: the audit trail (and the
                # coverage oracle) must see WHERE the certificate went.
                result.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in seg.lines)[:1200],
                    prov=_prov(seg.lines), kind="attestation"))
                continue
            op.blocks.extend(_segment_blocks(seg, segmenter, vocab))
        op.blocks = _flush_merge(op.blocks)
        # An EMPTY block is never content (a consumed byline row can leave
        # one behind).
        op.blocks = [b for b in op.blocks
                     if (getattr(b, "text", None) is None
                         or str(getattr(b, "text", "")).strip())]
        result.opinions.append(op)

    # An en banc order ANNOUNCES each writing's byline right before the
    # writing prints with the same byline; the announcement instance owns
    # no body. Drop a bodyless writing whose author reappears later.
    def _op_key(op):
        # the parsed NAME, not the raw clause: an announcement's author
        # reads 'VICE CHIEF JUSTICE LOPEZ authored the opinion…' while its
        # twin's byline reads 'VICE CHIEF JUSTICE LOPEZ, Opinion of the
        # Court' (ariz) — same writing.
        nm = (getattr(op, "author_name", "") or op.author or "")
        nm = nm.split(",")[0].strip().casefold()
        for cut in (" authored ", " delivered ", " announced ", " wrote "):
            if cut in nm:
                nm = nm.split(cut)[0].strip()
        return (nm, op.type)
    def _announces(op, later) -> bool:
        # A short bodyless writing that NAMES a later writing's author is
        # that writing's announcement ('MURPHY, J., delivered the opinion
        # of the court in which…' over ca6's real 'MURPHY, Circuit Judge.')
        from ..audit import strip_tags as _sta
        txt = " ".join(_sta(getattr(b, "text", "") or "")
                       for b in op.blocks).lower()
        if not txt or not any(v in txt for v in _DELIVER_VERBS):
            return False
        # An ORDER that announces its separate writings INSIDE its own
        # body is still the order (ca10's rehearing denial says 'Judge
        # Hartz has filed a separate opinion…' and then denies the
        # petition). The court's own disposition pronouncement is the
        # difference between an announcement and a writing.
        if any(cue in " ".join(
                _sta(getattr(b, "text", "") or "") for b in op.blocks)
               for cue in ("is denied", "are denied", "is granted",
                           "IT IS ORDERED", "is DENIED", "are DENIED",
                           "is dismissed", "is affirmed")):
            return False
        import re as _rex
        for o2 in later:
            nm = (getattr(o2, "author_name", "") or "").strip().lower()
            if not nm:
                continue
            surname = nm.split()[-1]
            # WORD boundary, never substring: 'the above-entitled cases'
            # contains 'bove' and would name Judge BOVE (ca3).
            if _rex.search(rf"\b{_rex.escape(surname)}\b", txt):
                return True
        return False

    def _chars(op) -> int:
        return sum(len(getattr(b, "text", "") or "") for b in op.blocks)

    doomed = [k for k, op in enumerate(result.opinions)
              if (_chars(op) < 300
                  and any(_op_key(o2) == _op_key(op)
                          for o2 in result.opinions[k + 1:]))
              # an ANNOUNCEMENT may run long when it lists every joiner
              # ('…in which SUTTON, C.J., and GRIFFIN, KETHLEDGE, …
              # joined.' — ca6); it is still not a writing.
              or (_chars(op) < 900
                  and _announces(op, result.opinions[k + 1:]))]
    for k in reversed(doomed):
        dead = result.opinions[k]
        result.consumed_ids.update(dead.author_prov.line_ids)
        # The announcement instance owns no body — but blocks it DID
        # collect are real content (nd sets the counsel roster between the
        # p1 'Per Curiam.' and the ¶1 body): rehome them to the surviving
        # twin, never consume them.
        survivor = next((o2 for o2 in result.opinions[k + 1:]
                         if _op_key(o2) == _op_key(dead)), None)
        if survivor is not None and dead.blocks:
            survivor.blocks[:0] = dead.blocks
        elif dead.blocks:
            # An ANNOUNCEMENT with no twin to rehome into is still
            # accounted for: it belongs to the headmatter, not to nowhere
            # (unclaimed blocks resurface as residual content).
            for b in dead.blocks:
                result.consumed_ids.update(
                    getattr(getattr(b, "prov", None), "line_ids", ()))
        del result.opinions[k]
        del starts[k]

    # Footnotes attach by page ownership. With no writing there is nothing
    # to attach them to — a court reader that claimed the whole stream
    # leaves no start, and the caller decides what to do about that.
    if not starts or not split_stream:
        result.headmatter_segments = (result.headmatter_segments
                                      + split_stream)
        if not result.opinions:
            result.warnings.append("no opinion start found")
        return result
    first_op_page = split_stream[starts[0]].page
    op_page_start: list[int] = []
    for i in starts:
        op_page_start.append(split_stream[i].page)
    owed: dict[int, int] = {}
    for pm in model.pages:
        cut = zone_tops.get(pm.number)
        for line in pm.lines:
            if cut is not None and line.top > cut:
                continue
            for mark in line_marks(line):
                if mark.isdigit():
                    owed[int(mark)] = owed.get(int(mark), 0) + 1
    all_zone_lines = [l for pm in model.pages
                      for l in zone_lines_by_page.get(pm.number, [])]
    flush = admit_flush_labels(all_zone_lines, owed)
    for pm in model.pages:
        zlines = zone_lines_by_page.get(pm.number, [])
        if not zlines:
            continue
        notes = _group_footnotes(zlines, flush, vocab,
                                 grids=_tables.get(pm.number))
        if pm.number < first_op_page:
            result.headmatter_footnotes.extend(notes)
            continue
        owner = 0
        for k, start_page in enumerate(op_page_start):
            if start_page <= pm.number:
                owner = k
        target = result.opinions[owner] if result.opinions else None
        if target is not None:
            # A '?' tail at the top of a page continues the previous note.
            for note in notes:
                if note.label == "?" and target.footnotes:
                    target.footnotes[-1].blocks.extend(note.blocks)
                else:
                    target.footnotes.append(note)
        else:
            result.headmatter_footnotes.extend(notes)

    # A STACK THE PAGE NEWLINED IS NOT A PARAGRAPH. A court that closes a
    # writing with its panel — one name per line, no punctuation joining
    # them — sets a run of SHORT lines at one left edge, and paragraph
    # assembly joined them into prose ('[¶4] Lisa Fair McEvers, C.J.
    # Jerod E. Tufte Jon J. Jensen Douglas A. Bahr Mark A. Friese'), or, where
    # the stack is indented on both margins, classified it as a QUOTATION,
    # or tore one roster across a paragraph and a blockquote. 49 of nd's 50
    # records mangled it one of those three ways.
    #
    # The test is geometric and reads no word: inside one writing, a run of
    # >= _STACK_ROWS consecutive printed lines whose every line's INK is at
    # most _STACK_INK of the measure, standing at a SINGLE left edge, is a
    # stack. It is re-emitted one Paragraph per printed line, IN PLACE — the
    # writing keeps every line and the page keeps its order, so this takes
    # nothing out of an assembled writing.
    #
    # Measured on nd: every roster name sits at x0=108.0 with ink 15.3-36.9%
    # of the measure and the opening row one 36pt step out at the body rail
    # (240.7pt = 36.0%, identical on all 50 records); body prose runs 93-100%
    # of the measure on every line but its last.
    _by_id = {l.id: l for pm in model.pages for l in pm.lines}
    _measure = geom.column if (geom and geom.column > 100) else 468.0
    for op in result.opinions:
        _out, _run = [], []

        def _close(op=op, _out=_out, _run=_run):
            """The stack is the longest contiguous tail of the run at ONE x0,
            plus at most one opening line exactly one indent step to its left
            — which is where the paragraph marker sits. Without that bound a
            short closing sentence above the roster ('[¶13] We affirm the
            judgment.', 38.5% of the measure) joins the stack."""
            if not _run:
                return
            _flat = sorted((l for _b, _ls in _run for l in _ls),
                           key=lambda x: (x.page, x.top))
            _edge = _flat[-1].x0
            _i = len(_flat)
            while _i > 0 and abs(_flat[_i - 1].x0 - _edge) <= _STACK_EDGE_TOL:
                _i -= 1
            if len(_flat) - _i >= 2 and _i > 0:
                _step = _edge - _flat[_i - 1].x0
                if _STACK_STEP[0] <= _step <= _STACK_STEP[1]:
                    _i -= 1
            _stack = _flat[_i:]
            if len(_stack) < _STACK_ROWS:
                _out.extend(b for b, _ in _run)
                _run.clear()
                return
            # every line ABOVE the stack keeps its place, one row per line
            # where the block it came from straddles the boundary
            _above = {id(l) for l in _flat[:_i]}
            for _b, _ls in _run:
                if not any(id(l) in _above for l in _ls):
                    continue
                if all(id(l) in _above for l in _ls):
                    _out.append(_b)
                else:
                    _out.extend(m.Paragraph(
                        text=" ".join(l.plain.split()),
                        prov=m.Prov(l.page, (l.id,)))
                        for l in _ls if id(l) in _above)
            for _k, l in enumerate(_stack):
                _out.append(m.Paragraph(
                    text=" ".join(l.plain.split()),
                    prov=m.Prov(l.page, (l.id,)), continuation=_k > 0))
            _run.clear()
            trace.event("body.stack_unwelded",
                        f"{len(_stack)} rows at x0={_edge:.0f}")

        for _b in op.blocks:
            _ls = [_by_id[i] for i in
                   getattr(getattr(_b, "prov", None), "line_ids", ())
                   if i in _by_id]
            if (isinstance(_b, (m.Paragraph, m.Blockquote)) and _ls
                    and all((l.x1 - l.x0) / _measure <= _STACK_INK
                            for l in _ls)):
                _run.append((_b, _ls))
            else:
                _close()
                _out.append(_b)
        _close()
        op.blocks = _out

    # Signature lift: a conformed '/s/' block (with its DATED line and title
    # lines) at an opinion's end is the signature, not body prose.
    _by_id = {l.id: l for pm in model.pages for l in pm.lines}
    for op in result.opinions:
        # A WELDED RUN CANNOT BE LIFTED: the scan below reads the head of a
        # block, so a signature that is sitting inside a body paragraph is
        # invisible to it. Unweld first.
        op.blocks = _split_leader_rows(
            _unweld_conformed(op.blocks, _by_id, vocab))
        cut = None

        def _is_sig(b):
            t = (getattr(b, "text", "") or "")
            t = t.replace("<strong>", "").replace("</strong>", "")
            return "/s/" in t[:20] or t.lower().startswith("/s ")

        # A COURT MAY SIGN WITH ITS HAND. Washington scans the justices'
        # actual signatures into the page and sets the typed name under each
        # one, over a rule of underscores in the right half of the sheet:
        #
        #     [signature image]
        #                          Johnson, J.
        #     WE CONCUR:
        #     [signature image] [signature image] …
        #                          Yu, J.P.T.
        #
        # There is no '/s/' anywhere, so the lift above saw nothing and the
        # whole block stayed in the body — 36 of wash's 50 records end on a
        # run of dangling one-name paragraphs with the signature graphics
        # loose between them (the user, 2026-08-21: 'wash should remove the
        # signatures … its too many and everywhere at the end of opinions',
        # 'its signed with signature images'). The run is read by what it is
        # MADE OF, and it must contain a graphic to be read at all: a short
        # right-set line on its own proves nothing.
        _ATTEST = ("WE CONCUR", "I CONCUR", "WE DISSENT",
                   "BY THE COURT", "FOR THE COURT")

        def _sig_member(b) -> bool:
            if isinstance(b, m.ImageBlock):
                return True
            t = " ".join(((getattr(b, "text", "") or "")
                          .replace("<strong>", "")
                          .replace("</strong>", "")).split())
            if not t:
                return True
            if t.upper().rstrip(":.") in _ATTEST:
                return True
            if len(t) > 60:
                return False
            ids = getattr(getattr(b, "prov", None), "line_ids", ())
            xs = [_by_id[i].x0 for i in ids if i in _by_id]
            # RIGHT OF THE AXIS. At 0.42 a CENTRED row passes — ca3's
            # 'OPINION' banner opens at x0 279 on a 612pt sheet — and the
            # signing column this is looking for stands at 334-399.
            return bool(xs) and min(xs) > model.pages[0].width * 0.5

        def _signed_over(b) -> bool:
            """Is this row printed under a SIGNATURE — a typed rule of
            underscores, or the scan of a hand?

            Washington's justices sign twice over: the lead opinion's page
            carries the graphics with the typed name under each, and the
            separate writings close on a rule of underscores with the name
            beneath. Both are the same mark — a signature line — and the row
            under one is a signature, not the writing's last paragraph.
            """
            ids = getattr(getattr(b, "prov", None), "line_ids", ())
            here = [_by_id[i] for i in ids if i in _by_id]
            if not here:
                return False
            pgno, top = here[0].page, min(l.top for l in here)
            pm = next((q for q in model.pages if q.number == pgno), None)
            if pm is None:
                return False
            # The mark stands ABOVE the name, and the two are BOUNDED BY
            # NOTHING ELSE. A fixed window cannot do it — the graphic sits
            # 10pt above its typed name on one page and 77pt above it on
            # another, because the justice signs into whatever space the
            # page left. What makes the mark this row's is that no writing
            # stands between them: prose in the gap would make the image a
            # figure the opinion discusses, not a signature under it.
            def _clear(above: float) -> bool:
                for line in pm.lines:
                    if not (above < line.top < top):
                        continue
                    txt = " ".join((line.plain or "").split())
                    if not txt or set(txt) <= set("_/"):
                        continue
                    if txt.upper().rstrip(":.") in _ATTEST:
                        continue
                    if len(txt) <= 60 and line.x0 > pm.width * 0.42:
                        continue          # another signer's name
                    return False
                return True

            for line in pm.lines:
                txt = "".join((line.plain or "").split())
                if txt.count("_") >= 6 and set(txt) <= set("_/") \
                        and line.top < top and _clear(line.top):
                    return True
            return any(_i.bottom < top and _clear(_i.bottom)
                       for _i in getattr(pm, "images", ()))

        # A COURT THAT SIGNS EN BANC SIGNS ONCE PER JUSTICE. Scanning back
        # from the end and stopping at the first '/s/' takes only the LAST
        # signer: haw sets five conformed names at x0=324 on a 468pt
        # measure, and 34 of its 51 signature lines were left in the body
        # reading as dangling prose while only the closing name kept the
        # page's right position. The block is the whole contiguous RUN.
        # The window is 12, not 5, because the run itself can be that long.
        for i in range(len(op.blocks) - 1, max(len(op.blocks) - 13, -1), -1):
            b = op.blocks[i]
            text = getattr(b, "text", "") or ""
            plain = text.replace("<strong>", "").replace("</strong>", "")
            if "/s/" in plain[:20] or plain.lower().startswith("/s "):
                cut = i
                while cut > 0 and _is_sig(op.blocks[cut - 1]):
                    cut -= 1
                i = cut
                # A 'DATED this …' line directly above belongs to it — and
                # so does the attestation that OPENS the signature block
                # ('BY THE COURT:' — del closes nearly every order that
                # way; 'FOR THE COURT:'). Left in the body it reads as a
                # dangling last paragraph of the opinion.
                if cut > 0:
                    above = (getattr(op.blocks[cut - 1], "text", "") or "")
                    _ab = " ".join(above.split()).upper().rstrip(":")
                    if len(above) < 120 and (
                            _ab.startswith("DATED")
                            or _ab in ("BY THE COURT", "FOR THE COURT")):
                        cut = cut - 1
                break
        if cut is None and op.blocks:
            # …the HAND-SIGNED run, walked back from the last block.
            j = len(op.blocks)
            while j > 0 and _sig_member(op.blocks[j - 1]):
                j -= 1
            run = op.blocks[j:]
            named = [b for b in run if not isinstance(b, m.ImageBlock)
                     and (getattr(b, "text", "") or "").strip()]
            # …AND NEVER THE WHOLE WRITING. `j == 0` means every block the
            # writing has looked like signing, which is not a signature but
            # a misread: ca3 assembles a one-block writing holding just its
            # 'OPINION' banner, and lifting that left the writing empty and
            # the banner unclaimed — dropped from the output entirely.
            if 0 < j < len(op.blocks) and named \
                    and any(_signed_over(b) for b in named):
                # THE ATTESTATION THAT OPENS THE BLOCK COMES WITH IT. 'WE
                # CONCUR:' is set at the RAIL, not in the signers' column,
                # so the walk back stops on the row above it and leaves it
                # behind as the writing's last paragraph.
                while j > 0:
                    _a = " ".join(((getattr(op.blocks[j - 1], "text", "")
                                    or "").replace("<strong>", "")
                                   .replace("</strong>", "")
                                   ).split()).upper().rstrip(":.")
                    if _a not in _ATTEST:
                        break
                    j -= 1
                cut = j
        if cut is not None:
            tail = op.blocks[cut:]
            # Only short lines follow a signature (name, title, court).
            if all(len(getattr(b, "text", "") or "") < 200 for b in tail):
                # The page may set the signer block RIGHT of the measure
                # (haw signs at 53% width) — keep its position.
                for b in tail:
                    ids = getattr(getattr(b, "prov", None), "line_ids", ())
                    xs = [_by_id[i].x0 for i in ids if i in _by_id]
                    if xs and min(xs) > model.pages[0].width * 0.42 \
                            and isinstance(b, m.Paragraph):
                        b.align = "right"
                op.signature = tail
                op.blocks = op.blocks[:cut]

    # HEADING RUNS ARE JOINED LAST, once every pass that reads the HEAD of a
    # block has run. Placed before the signature lift it changed what that
    # scan sees, and a joined heading matched (or stopped matching) the
    # conformed-signature shape: 4 records across arwd, azd and kyed gained
    # a 'panel' row in their headmatter and fladistctapp gained a
    # 'disposition' criterion, none of which is a heading question at all
    # (guard, 2026-08-23). Joining rows into the heading the court printed
    # is a RENDERING fact and belongs after the structure is settled.
    for op in result.opinions:
        op.blocks = _merge_heading_runs(op.blocks, _by_id)
        op.signature = _merge_heading_runs(op.signature, _by_id)
    return result
