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


def _mode_x0(lines) -> float | None:
    """The x0 the flow RETURNS to: the most common left edge, ties toward the
    left. One measurement, used by the paragraph walk and by the quotation
    split, so the two cannot disagree about where the rail is. None when
    there is nothing to measure — never 0.0, which a caller would read as an
    edge (index 0 is falsy, and that trap has cost this project a day)."""
    xs: dict[float, int] = {}
    for l in lines:
        k = round(l.x0, 1)
        xs[k] = xs.get(k, 0) + 1
    if not xs:
        return None
    return max(xs.items(), key=lambda kv: (kv[1], -kv[0]))[0]


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
    paras: list[list[Line]] = []
    labels: dict[int, Line] = {}
    prev = None
    after_label = False
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
        opens = bool(paras) and not same_row and (
            _is_para_mark(line)
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
        if text:
            out.append(m.Paragraph(text=text, prov=_prov(lines)))
    return out


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
    # A label alone in its own segment never reaches the paragraph walk,
    # and the 'single' path types it by its LETTERS — so a lettered label
    # ('B') came out a heading while a numbered one ('1') came out a stray
    # digit paragraph beside it. Geometry, not case, decides.
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
        _cuts = [i for i in range(1, len(seg.lines))
                 if seg.lines[i].x0 - _qrail >= _qstep
                 and seg.lines[i - 1].x0 - _qrail < _qstep
                 and seg.lines[i - 1].x1 <= _qright - 12.0
                 and seg.lines[i].top - seg.lines[i - 1].top > 2.0]
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
                     vocab: set[str] | None) -> list[m.Footnote]:
    """Zone lines -> Footnote objects, split where a label opens a note."""
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
        out.append(m.Footnote(label=lab, blocks=[
            m.Paragraph(text=text, prov=_prov(lines))] if text else []))
    return out


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
             headmatter_claimed: bool = False) -> Assembled:
    result = Assembled()

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
        cuts = [j for j in range(1, len(seg.lines))
                if _line_opens_byline(seg.lines, j)
                and not _midsentence_tail(seg.lines[j - 1].plain)]
        bounds = [0, *cuts, len(seg.lines)]
        for a, b in zip(bounds, bounds[1:]):
            if seg.lines[a:b]:
                split_stream.append(Segment(seg.page, seg.lines[a:b], seg.kind))

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
    _ATTEST = re.compile(r"^(?:WE|I)\s+(?:CONCUR|CONCURRED|DISSENT)\b"
                         r"|^CONCUR(?:RED)?\s*:", re.I)

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
              and not (i > 0 and split_stream[i - 1].lines
                       and _midsentence_tail(
                           split_stream[i - 1].lines[-1].plain))]

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
            if (caption_band and line.page == 1
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
            elif (caption_band and line.page == 1
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
            starts = [_body0] + [x for x in starts if x > _body0]
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
                          para_indent_min=para_indent_min)
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
            byline_ids = [l.id for l in head_seg.lines[:max(consumed, 1)]]
            if head_line.row is not None:
                byline_ids += [l.id for l in head_seg.lines
                               if l.row == head_line.row
                               and l.page == head_line.page
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
            sig_author = conformed_signature_author(all_lines_text)
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
                    "hereby DENIED", "hereby GRANTED")):
                op_type = "order"
            author = sig_author or ""
            if terminal_author is not None:
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
            banner_at = next(
                (k for k, s in enumerate(writing_segs[:12])
                 if len(s.lines) == 1
                 and s.lines[0].plain.strip().upper().replace(" ", "")
                     in ("OPINION", "ORDER", "MEMORANDUMOPINION")),
                None)
            if banner_at is not None:
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
        notes = _group_footnotes(zlines, flush, vocab)
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
        op.blocks = _unweld_conformed(op.blocks, _by_id, vocab)
        cut = None

        def _is_sig(b):
            t = (getattr(b, "text", "") or "")
            t = t.replace("<strong>", "").replace("</strong>", "")
            return "/s/" in t[:20] or t.lower().startswith("/s ")

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
    return result
