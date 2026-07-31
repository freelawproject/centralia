"""United States Court of Appeals for the Third Circuit."""

from __future__ import annotations

from collections import Counter
import re

import pdfplumber

from ..base import BaseExtractor
from ..models import Block
from ._circuit import FederalCircuitBase
from .generic import _is_name


class ThirdCircuit(FederalCircuitBase):
    court_id = "ca3"
    court_label = "United States Court of Appeals for the Third Circuit."
    circuit_phrase = "third circuit"
    # Published CA3 opinions use a narrow x≈144..468 body measure. The federal
    # default x≈72 makes ordinary prose appear deeply indented and therefore
    # quote-like.
    body_baseline_x0 = 144.0
    # The justified right measure, filled in per document by
    # ``_measure_body_template`` (the corpus runs at both x1≈468 and x1≈540).
    body_right_rail = None
    gap_tight_max = 12.0
    # Main text leads at ~17pt; genuinely single-spaced quotations are tighter.
    gap_single_max = 16.0
    gap_double_max = 38.0
    blockquote_by_indent = True
    # CA3 prints NO running header — not on any page of the corpus (no line
    # above 110pt repeats on even three continuation pages in any of the 50
    # fixtures). The family default drops everything above 95pt on pages 2+ to
    # clear the circuits that DO carry a centered 'No. <docket>' head; here that
    # band is body. CA3 sets two measures — a bound one whose continuation pages
    # open at ~146pt (the cutoff is harmless) and a slip one that opens at ~74pt
    # — and on the slip measure the cutoff silently ate the first two lines of
    # every page: body prose, section heads, panel rosters, and whole bylines
    # ('HARDIMAN, Circuit Judge.'). Lowered below ``margin_top`` (39) so the
    # page edge alone bounds the band.
    page2_header_cutoff = 30.0
    dedupe_footnote_labels = False

    _star_break = re.compile(
        r'^(?P<folio><pagenumber value="[^"]+"/>\s*)?'
        r'(?P<stars>\*\s+\*\s+\*)\s+(?P<body>.+)$'
    )

    def prepare_document(self, pdf):
        """Keep page-top prose when CA3 has no repeated running header.

        The circuit family reserves the first 95 points of continuation pages
        for a docket header.  Some CA3 opinions instead continue body text at
        the top of page 2; only the panel roster form is a reliable header
        signal for this corpus.
        """
        self._drop_page2_header = False
        if len(pdf.pages) > 1:
            top = [
                (line.get("text") or "").strip().lower()
                for line in pdf.pages[1].extract_text_lines()
                if line.get("top", 0) < self.page2_header_cutoff
            ]
            self._drop_page2_header = any(line.startswith("before:") for line in top)

    def filter_margins(self, obj):
        # CA3's nonprecedential-opinion marker may carry an asterisk footnote
        # below the normal bottom margin on page 1.
        if obj.get("page_number", 1) == 1 and obj.get("top", 0) > self.margin_bottom:
            return True
        if (
            obj.get("page_number", 1) > 1
            and obj.get("top", 0) < self.page2_header_cutoff
            and not getattr(self, "_drop_page2_header", False)
        ):
            return BaseExtractor.filter_margins(self, obj)
        return super().filter_margins(obj)

    def find_footnote_separator(self, page):
        """CA3's 144pt footnote rule is anchored at the body rail x≈144."""
        separator = self._sep_at(
            page, self.body_baseline_x0 - 4, self.body_baseline_x0 + 4
        )
        if separator is not None:
            return separator

        # Some CA3 opinions have no drawn rule. Their footnotes begin in the
        # lower half of the page with a superscript-sized label followed by
        # body-sized text; use the first such label as the zone boundary.
        candidates = []
        for line in page.extract_text_lines():
            if line.get("top", 0) <= page.height * 0.55:
                continue
            if self.detect_footnote_label(line) is not None:
                candidates.append(line["top"])
        return min(candidates) if candidates else None

    def matches_expected_layout(self, pdf):
        """Accept CA3's abbreviated first-page court banner.

        Some opinions spell out ``United States Court of Appeals`` while
        others use ``U.S. Court of Appeals`` and wrap ``CIRCUIT`` onto the
        next line.  The shared circuit check handles the former, but its
        same-line phrase check misses this valid CA3 variant.
        """
        if super().matches_expected_layout(pdf):
            return True
        if not pdf.pages:
            return False
        text = " ".join(
            (line.get("text") or "")
            for line in pdf.pages[0].extract_text_lines()
        ).lower()
        return "u.s. court of appeals" in text and "third" in text and "circuit" in text

    def detect_printed_folio(self, page, lines):
        """CA3 sets its folio just below the text block rather than down in the
        sheet's bottom margin — top≈667 on a 792pt page, and ≈621 once a
        separate writing starts (each writing is paginated as its own slip
        document and restarts at 1). Both sit well inside the shared detector's
        ``height - 85`` edge band, so the folio is never registered and the bare
        number falls through into the opinion body as a paragraph.

        Read it by structure instead of by distance from the paper's edge: the
        last line on the page, standing alone as a centered number, cut off from
        the text above it by a gap wider than the court's double space."""
        folio = super().detect_printed_folio(page, lines)
        if folio is not None:
            return folio
        try:
            raw = page.filter(
                lambda o: o.get("upright", True) is not False
            ).extract_text_lines()
        except Exception:
            return None
        if len(raw) < 2:
            return None
        last, above = raw[-1], raw[-2]
        if self._page_number_value((last.get("text") or "").strip()) is None:
            return None
        if self.line_alignment(last, page.width) != "C":
            return None
        if (last.get("top", 0) - above.get("top", 0)) < self.gap_double_max:
            return None
        return self._page_number_value((last.get("text") or "").strip())

    def page_lines(self, page):
        """Measure each line's top from its BODY glyphs, ignoring superscripts.

        A superscript footnote marker is set above the body baseline, so
        pdfplumber reports the whole line as starting ~1.5pt higher than its
        neighbours. At CA3's 13pt leading that is enough to drop the gap under
        ``gap_tight_max`` (11.4 against a 12.0 threshold), which reads as a
        single-spaced run: the paragraph splits at the marker, the two-line
        fragment classifies as a notice and is discarded from the body
        (rti_restoration p.31, 'under the MPPAA.1'). A footnote marker must
        never break a paragraph, so take the top from the line's dominant
        size and leave everything else — chars included — untouched."""
        lines = super().page_lines(page)
        for line in lines:
            chars = line.get("chars") or []
            if len(chars) < 2:
                continue
            size, _font, _bold = self.line_meta(line)
            body = [
                c
                for c in chars
                if abs(round(c.get("size", 0), 1) - size) < 0.6
                and (c.get("text") or "").strip()
            ]
            if not body or len(body) == len(chars):
                continue
            top = min(c["top"] for c in body)
            if 0 < top - line["top"] < 3:
                line["top"] = top
        return lines

    def classify_paragraph(self, lines):
        """Promote the court's short, fully-bold centered section rows."""
        if (
            len(lines) == 1
            and self.line_alignment(lines[0], getattr(self, "_page1_width", 612.0))
            == "C"
            and self._line_all_bold(lines[0])
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def _byline_split(self, line):
        """Accept CA3's all-caps, punctuation-free byline variant — and reject
        the closing 'BY THE COURT,' of an order, which is a SIGNATURE."""
        found = super()._byline_split(line)
        if found is not None:
            return None if self._is_signature_column(line) else found
        text = (line.get("text") or "").strip()
        if "," not in text:
            return None
        name, title = (part.strip() for part in text.split(",", 1))
        if _is_name(name) and title.upper() == "CIRCUIT JUDGE":
            return text, ""
        return None

    def _is_signature_column(self, line) -> bool:
        """True for a 'BY THE COURT,' / 'PER CURIAM' line set in the RIGHT-hand
        signature column rather than at the body rail.

        A byline OPENS a body: it starts at the left rail with the opinion's
        first sentence running on from it. CA3's orders close instead with a
        conformed signature stacked in the right half of the measure —
        'BY THE COURT,' over 's/ <Name>' over the bench title, above a drawn
        signature rule. Read as a byline it becomes the only 'opinion' in the
        document, and the order's actual text is stranded in the headmatter
        (schuster_1, jerome_brown, whittaker_clark_1)."""
        text = (line.get("text") or "").strip().lower()
        if not text.startswith(("by the court", "per curiam")):
            return False
        # A byline starts AT the body rail (or one indent in). The signature
        # column is tabbed a full inch or more right of it — x0≈288 on the
        # 72pt measure, ≈369 on the 108pt one.
        return line.get("x0", 0) > self.body_baseline_x0 + 72

    def _split_segments_at_bylines(self, all_segments):
        """Also cut a segment immediately AFTER a 'Present:' panel roster.

        An order sets its roster only ~35pt above the first line of the order
        itself — inside the court's double space — so the two arrive as one
        segment and the roster (headmatter) cannot be told from the order text
        (body). Splitting here lets ``_percuriam_start`` open the body at the
        line after the roster instead of at the signature further down."""
        out = []
        for page_no, seg, kind in super()._split_segments_at_bylines(all_segments):
            marks = (self._roster_end(seg), self._order_title_index(seg))
            cuts = sorted({m + 1 for m in marks if m is not None and m + 1 < len(seg)})
            if not cuts:
                out.append((page_no, seg, kind))
                continue
            bounds = [0] + cuts + [len(seg)]
            for a, b in zip(bounds, bounds[1:]):
                sub = seg[a:b]
                if sub:
                    out.append((page_no, sub, self.classify_segment(sub)))
        return out

    def _order_title_index(self, seg):
        """Index of a centered 'ORDER …' title inside a segment, or None.

        A clerk's order runs its title straight into its text with no extra
        space, so title and order arrive as one segment (and, on a one-page
        order, the caption's closing lines come with them). Cut on the turn
        from centered title to left-aligned text."""
        width = getattr(self, "_page1_width", None) or 612.0
        for j, line in enumerate(seg[:-1]):
            if not self.line_plain_text(line).strip().upper().startswith("ORDER"):
                continue
            if self.line_alignment(line, width) != "C":
                continue
            if self.line_alignment(seg[j + 1], width) == "C":
                continue
            return j
        return None

    def _roster_end(self, seg):
        """Index of the LAST line of a 'Present:' panel roster, or None.

        The roster opens 'Present:' and closes on the line that names the
        bench — 'Present: KRAUSE, MATEY, and SCIRICA, Circuit Judges' on a
        panel, wrapping to a second line on an en banc court ('Present:
        HARDIMAN, KRAUSE, … PHIPPS,' / 'FREEMAN, … and MASCOTT, Circuit
        Judges.'), which is why the bench title cannot be required on the
        opening line."""
        start = next(
            (
                j
                for j, line in enumerate(seg)
                if self.line_plain_text(line).strip().lower().startswith("present:")
            ),
            None,
        )
        if start is None:
            return None
        for j in range(start, min(len(seg), start + 4)):
            if "judge" in self.line_plain_text(seg[j]).strip().lower():
                return j
        return start

    def _order_body_start(self, all_segments, first_byline):
        """Index of the segment opening an unsigned ORDER's text, or None.

        CA3's unsigned orders name their panel with a 'Present:' roster where
        the family base knows only the argued-opinion form, 'Before: <judges>'.
        Without this the order's text belongs to no opinion and is left in the
        headmatter, while the 'BY THE COURT,' signature below it is mistaken
        for the byline (schuster_1, jerome_brown, khalil, whittaker_clark_1).
        On an en banc denial of rehearing the roster reverts to the same
        'Before:' the argued opinions use (adolph_michelin), so the roster
        alone cannot say "order". What can is the conformed signature that
        closes one — 'BY THE COURT,' set in the right-hand column. Requiring it
        between the roster and the first byline keeps an argued opinion's
        roster from ever being read as the head of an order.
        """
        # The roster's wrap can land in a segment of its own (khalil's en banc
        # court runs to two lines that segment apart), so track where the run
        # CLOSES — on the line naming the bench — not where it opens.
        panel, open_for = None, 0
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            for line in seg:
                text = self.line_plain_text(line).strip().lower()
                if text.startswith(("present:", "before:")):
                    panel, open_for = i, 0 if "judge" in text else 3
                elif open_for:
                    panel, open_for = i, 0 if "judge" in text else open_for - 1
        if panel is None:
            return self._titled_order_start(all_segments, first_byline)
        start = None
        for j in range(panel + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            start = j
            break
        if start is None or start >= first_byline:
            return None
        signed = any(
            self._is_signature_column(line)
            for _pno, seg, _kind in all_segments[start:first_byline]
            for line in seg
        )
        return start if signed else None

    def _titled_order_start(self, all_segments, first_byline):
        """Index of the body of a clerk's administrative order, or None.

        These carry no panel at all — a centered 'ORDER AMENDING OPINION'
        title over the order's text, closing 'For the Court,' over the Clerk's
        name (josue_sanchez). With nothing to mark a body, the whole order sat
        in the headmatter and the document returned no writing whatsoever.
        Only consulted for a document with no byline and no roster."""
        if first_byline < len(all_segments):
            return None
        width = getattr(self, "_page1_width", None) or 612.0
        title = next(
            (
                i
                for i, (_pno, seg, _kind) in enumerate(all_segments)
                if seg
                and self.line_plain_text(seg[-1]).strip().upper().startswith("ORDER")
                and self.line_alignment(seg[-1], width) == "C"
            ),
            None,
        )
        if title is None:
            return None
        for j in range(title + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def find_authors(self, all_segments):
        """Add what the strict form-based pass cannot see on its own: a byline
        whose kind clause WRAPS onto the next line, and the unsigned order that
        a panel roster opens."""
        self._order_start = None
        found = list(super().find_authors(all_segments))
        self._wrapped_starts = set(self._wrapped_byline_starts(all_segments))
        for i in self._wrapped_starts:
            if i not in found:
                found.append(i)
        # An order's text always precedes any separate writing attached to it
        # (khalil, michelin print the denial first and the dissents after).
        first = min(found) if found else len(all_segments)
        order = self._order_body_start(all_segments, first)
        if order is not None:
            self._order_start = order
            self._pc_starts.add(order)
            if order not in found:
                found.append(order)
        return sorted(found)

    def _wrapped_byline_starts(self, all_segments) -> list:
        """Segments opening with a byline that wraps over two lines.

        'KRAUSE, Circuit Judge, joined by RESTREPO and FREEMAN,' /
        'Circuit Judges, dissenting sur denial of rehearing en banc.'
        — the first line carries no kind, so on its own it parses as nothing
        and the whole separate writing goes undetected. Gated on the open
        comma that the wrap leaves behind, so an ordinary byline (which closes
        on its own line) is never re-parsed."""
        out = []
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if len(seg) < 2:
                continue
            first = self.line_plain_text(seg[0]).strip()
            if not first.endswith(","):
                continue
            joined = f"{first} {self.line_plain_text(seg[1]).strip()}"
            probe = {"text": joined, "x0": seg[0].get("x0", 0)}
            if self._byline_split(probe) is not None:
                out.append(i)
        return out

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """A 'Present:' roster with no byline is an ORDER, not an opinion —
        the family default calls anything with an opinion start an opinion."""
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def extract(self, pdf_path):
        self._counsel_lines = []
        self._order_start = None
        self._measure_body_template(pdf_path)
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Flush the harvested counsel addendum onto the document BEFORE the
        completeness sweep runs — appending it after ``extract`` returns would
        put it there after the sweep had already read the sections, so every
        counsel line would be reported unplaced while sitting in the trailer."""
        if self._counsel_lines:
            doc.trailer = list(doc.trailer) + self._counsel_lines
        super()._sweep_residual(doc, source_pages)

    def _measure_body_template(self, pdf_path):
        """Derive CA3's body rail, right measure and leading from the document
        itself."""
        x0s = Counter()
        x1s = Counter()
        page_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    lines = super().page_lines(page)
                    usable = [
                        line
                        for line in lines
                        if 75 < line.get("top", 0) < page.height - 75
                        and line.get("x0", 0) < page.width * 0.42
                        and line.get("x1", 0) > page.width * 0.55
                    ]
                    x0s.update(round(line["x0"]) for line in usable)
                    x1s.update(round(line["x1"]) for line in usable)
                    page_rows.append(usable)
        except Exception:
            return
        if not x0s:
            return
        baseline = float(x0s.most_common(1)[0][0])
        if x1s:
            # The justified right measure. Counsel appearances are set as a
            # list and never reach it — that is what separates them from body.
            self.body_right_rail = float(x1s.most_common(1)[0][0])
        gaps = Counter()
        for lines in page_rows:
            ordered = sorted(lines, key=lambda line: line["top"])
            for above, below in zip(ordered, ordered[1:]):
                gap = below["top"] - above["top"]
                if (
                    abs(above["x0"] - baseline) <= 4
                    and abs(below["x0"] - baseline) <= 4
                    and 10 <= gap <= 24
                ):
                    gaps[round(gap, 1)] += 1
        self.body_baseline_x0 = baseline
        if gaps:
            leading = gaps.most_common(1)[0][0]
            # Put the dominant body leading just inside the body band. Inset
            # quote geometry remains available independently.
            self.gap_single_max = max(self.gap_tight_max + 0.5, leading - 1.5)

    @staticmethod
    def _plain(text):
        out, inside = [], False
        for char in str(text or ""):
            if char == "<":
                inside = True
            elif char == ">":
                inside = False
            elif not inside:
                out.append(char)
        return "".join(out).strip()

    # ------------------------------------------------------ counsel addendum
    # CA3 prints the counsel appearances as an ADDENDUM, after the opinion they
    # belong to — at the end of the document when there is one writing, and
    # between the majority's disposition and the next byline when there is more
    # than one (kalshiex pp. 18-20 → ROTH's dissent p. 21; massey p. 27 → BOVE's
    # concurrence p. 28; energy_harbor p. 9 → SMITH's dissent p. 10).
    #
    # Cut it at the SEGMENT level, before paragraphs are built. Cutting blocks
    # afterwards cannot work: the page-break continuation join folds the first
    # appearance group onto the majority's closing paragraph ("… We will affirm.
    # Matthew J. Platkin Liza B. Fleming …"), and by then the geometry that
    # identifies the block is gone.
    def build_opinion(self, op_start, op_end, *, all_segments, **kwargs):
        if op_start in getattr(self, "_wrapped_starts", ()):
            all_segments = self._join_wrapped_byline(all_segments, op_start)
        cut = self._counsel_block_start(all_segments, op_start, op_end)
        if cut is not None:
            for _pno, seg, _kind in all_segments[cut:op_end]:
                for line in seg:
                    text = self.line_inline_text(line).strip()
                    if text:
                        self._counsel_lines.append(text)
            op_end = cut
        op = super().build_opinion(
            op_start, op_end, all_segments=all_segments, **kwargs
        )
        return self._split_star_breaks(op)

    def _join_wrapped_byline(self, all_segments, op_start):
        """Fold a two-line byline into one line before the opinion is built.

        The builder reads the byline off the segment's FIRST line only, so a
        byline that wraps leaves its own tail ('Circuit Judges, dissenting sur
        denial of rehearing en banc.') standing as the opening sentence of the
        body, and the author parses out of the half-clause above it. Join the
        pair — with an explicit spacer, since the second line's glyphs restart
        at the left rail and the gap-based text builder would otherwise run the
        two together ('FREEMAN,Circuit Judges')."""
        pno, seg, kind = all_segments[op_start]
        if len(seg) < 2:
            return all_segments
        head, tail = seg[0], seg[1]
        head_chars = list(head.get("chars") or [])
        tail_chars = list(tail.get("chars") or [])
        if not head_chars or not tail_chars:
            return all_segments
        edge = head_chars[-1]
        spacer = dict(edge)
        spacer["text"] = " "
        spacer["x0"] = edge["x1"] + 2
        spacer["x1"] = edge["x1"] + 3
        merged = self._rebuild_line(head, head_chars + [spacer] + tail_chars)
        merged["chars"] = head_chars + [spacer] + tail_chars
        merged["x0"], merged["x1"] = head.get("x0", 0), head.get("x1", 0)
        merged["text"] = (
            f"{self.line_plain_text(head).strip()} "
            f"{self.line_plain_text(tail).strip()}"
        )
        out = list(all_segments)
        out[op_start] = (pno, [merged] + list(seg[2:]), kind)
        return out

    def _split_star_breaks(self, op):
        """Keep CA3's centered ``* * *`` transitions as visible separators.

        The PDF text layer places the separator line immediately before the
        next paragraph, so the shared paragraph builder joins them. In the
        rendered review that makes the stars look like paragraph text instead
        of the standalone centered break the court printed."""
        blocks = []
        for block in op.blocks:
            match = self._star_break.match(block.text or "")
            if match and block.kind == "p":
                blocks.append(
                    Block(
                        kind="heading",
                        text=match.group("stars"),
                        page=block.page,
                    )
                )
                folio = match.group("folio") or ""
                block.text = folio + match.group("body")
            blocks.append(block)
        op.blocks = blocks
        return op

    def _counsel_block_start(self, all_segments, op_start, op_end):
        """Index of the segment opening the counsel addendum, or None.

        Anchored on the italic ``Counsel for …`` caption CA3 prints over every
        appearance group — then widened backwards over any name run set above
        its caption, because the court prints the caption BELOW its names in
        some opinions (kalshiex) and ABOVE them in others (massey,
        energy_harbor). The caption alone therefore does not bound the block.
        """
        cap = next(
            (
                i
                for i in range(op_start + 1, op_end)
                if self._has_counsel_caption(all_segments[i][1])
            ),
            None,
        )
        if cap is None:
            return None
        while cap - 1 > op_start and self._is_list_segment(all_segments[cap - 1][1]):
            cap -= 1
        return cap

    def _has_counsel_caption(self, seg) -> bool:
        """True if a segment carries an italic ``Counsel for …`` caption."""
        for line in seg:
            if not self._plain(line.get("text")).startswith("Counsel for"):
                continue
            if self._line_all_italic(line):
                return True
        return False

    def _is_list_segment(self, seg) -> bool:
        """A segment set as a LIST rather than as prose: no line reaches the
        justified right measure. Counsel names, firms and addresses are set
        ragged-right; body prose is justified to the rail on every line but its
        last, so a whole segment that never reaches it cannot be body."""
        rail = getattr(self, "body_right_rail", None)
        if not seg or rail is None:
            return False
        return max(line.get("x1", 0) for line in seg) < rail - 6

    @staticmethod
    def _line_all_italic(line) -> bool:
        """Every letter/digit on the line set in the italic face."""
        seen = False
        for c in line.get("chars") or []:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            fn = c.get("fontname") or ""
            if "Italic" not in fn and "Oblique" not in fn:
                return False
        return seen
