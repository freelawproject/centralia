"""Court of Appeals of Georgia.

Two document families:

* Opinions: author byline at the opinion start ('MARKLE, Judge.' /
  'BARNES, Presiding Judge.'); the shared appellate base handles them.

* Orders: a script 'Court of Appeals / of the State of Georgia' letterhead,
  an 'ATLANTA, <date>' line typed over an underscore fill-in rule (the
  underscores interleave with the date glyphs and are dropped), the formula
  'The Court of Appeals hereby passes the following order:', an ALL-CAPS
  docket caption ('A26A2022. PARTY v. PARTY.'), then the unsigned order
  body, often ending in the clerk's certificate block. The body starts at
  the first segment after the docket caption; there is no author.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ..models import Block

_ORDER_FORMULA = "hereby passes the following order"


class CourtOfAppealsOfGeorgia(StateAppellate):
    court_id = "gactapp"
    court_label = "Court of Appeals of Georgia."
    fold_page_numbers = True
    # The order template uses ~22pt body leading.  Keep it just outside the
    # court's tighter quotation band (the generic 22pt boundary is too close
    # to PDF coordinate rounding and labels the order prose as a quotation).
    gap_single_max = 21.5
    # The reconsideration-deadline boilerplate box on opinions is 10pt small
    # print against a 14pt page — a notice, routed to ``dropped``.
    notice_max_size = 10.5

    def extract(self, pdf_path):
        self._order_start = None
        doc = super().extract(pdf_path)
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        # Orders close with the clerk's certification, seal, and signature.
        # It is ending matter, not a second opinion/body paragraph.  Keep the
        # original blocks (including images) so the facsimile is lossless.
        if doc.opinions:
            blocks = doc.opinions[-1].blocks
            cut = next(
                (
                    i
                    for i, block in enumerate(blocks)
                    if block.kind != "image"
                    and (
                        "clerk’s office, atlanta" in block.text.lower()
                        or "clerk's office, atlanta" in block.text.lower()
                        or "true extract from" in block.text.lower()
                    )
                ),
                None,
            )
            if cut is not None:
                doc.trailer = list(doc.trailer) + blocks[cut:]
                doc.opinions[-1].blocks = blocks[:cut]
        return doc

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # Current Georgia Court of Appeals opinions sometimes omit the drawn
        # rule entirely.  Their note begins at the hanging-note rail (36pt
        # inside the body) with a genuinely superscripted numeric label.  Use
        # those font and geometry facts as the separator; ordinary numbered
        # body paragraphs have a body-size first glyph and cannot match.
        candidates = []
        for line in self.page_lines(page):
            chars = line.get("chars") or []
            if len(chars) < 2 or line["top"] < page.height * 0.45:
                continue
            first = chars[0]
            if not (first.get("text") or "").isdigit():
                continue
            following = next(
                (c for c in chars[1:] if (c.get("text") or "").strip()), None
            )
            if following is None:
                continue
            if first.get("size", 0) > following.get("size", 0) - 4:
                continue
            if line["x0"] < self.body_baseline_x0 + 24:
                continue
            candidates.append(line["top"])
        return min(candidates) if candidates else None

    def page_lines(self, page):
        lines = super().page_lines(page)
        # The 'ATLANTA, <date>' line is typed over an underscore fill-in
        # rule, interleaving '_' glyphs with the date ('__M_a_y_ 2_2_').
        # Strip the underscores only when they INTERLEAVE with the text
        # (many _↔text transitions along the line); a blank-reporter cite
        # ('___ Ga. ___') has two contiguous runs and stays intact.
        for ln in lines:
            chars = ln.get("chars") or []
            flips = 0
            prev = None
            for c in sorted(chars, key=lambda c: c["x0"]):
                cur = c.get("text") == "_"
                if prev is not None and cur != prev:
                    flips += 1
                prev = cur
            if flips > 4:
                ln["chars"] = [c for c in chars if c.get("text") != "_"]
        self._mark_order_caption(lines)
        return lines

    def _mark_order_caption(self, lines) -> None:
        """Cut the order sheet open at its docket caption, whatever its length.

        The order template's three rows — the italic formula, the bold ALL-CAPS
        docket caption, the first body line — are set at the SAME 22pt leading,
        so nothing but the change in weight separates them. The shared
        segmenter only treats bold as a boundary when the line is bold
        throughout AND stops short of the right measure, because a bold case
        name filling a line of a string citation is prose, not a heading.

        A long party name defeats that: ``A27A0030. SABRINA MELTON v.
        JEFFERSON CAPITAL SYSTEMS, LLC.`` runs to x=539 on a 540pt measure, so
        the caption was not a boundary, the formula and the whole order body
        segmented as ONE segment, and ``find_authors``' order fallback — which
        reads the caption off a segment's FIRST line — found nothing. The
        document had no body and ``doc_type=unknown``.

        Position, not width, is what makes this row a heading: it is the row
        directly below the 'passes the following order' formula, and the body
        begins on the row after it. Mark both as structural breaks so the sheet
        segments exactly as the short-caption orders already do.
        """
        formula = next(
            (
                i
                for i, ln in enumerate(lines)
                if _ORDER_FORMULA in self.line_plain_text(ln).lower()
            ),
            None,
        )
        if formula is None:
            return
        for i in (formula + 1, formula + 2):
            if i < len(lines):
                lines[i]["_seg_break"] = True

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._order_start = None
        if starts:
            # Published opinions carry a division masthead above the notice:
            #   SECOND DIVISION
            #   DOYLE, P. J.,
            #   DAVIS, J., and SENIOR JUDGE FULLER
            # Those are panel rows, not opinion bylines. The authored opinion
            # begins below the court-name banner and docket caption.
            banner_at = next(
                (
                    i
                    for i, (_p, seg, _k) in enumerate(all_segments)
                    if any(
                        "court of appeals of georgia"
                        in self.line_plain_text(line).lower()
                        for line in seg
                    )
                ),
                None,
            )
            if banner_at is not None:
                starts = [i for i in starts if i > banner_at]
            if starts:
                return starts
        # An order: the body begins at the segment after the ALL-CAPS docket
        # caption that follows the 'hereby passes the following order'
        # formula.
        formula_at = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            for l in seg:
                if _ORDER_FORMULA in self.line_plain_text(l).lower():
                    formula_at = i
                    break
            if formula_at is not None:
                break
        if formula_at is None:
            return []
        for i in range(formula_at + 1, len(all_segments)):
            seg = all_segments[i][1]
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            # the docket caption row ('A26A2022. EDIE-JANE CLARKE v. ...')
            first = t.split()[0] if t.split() else ""
            if first.endswith(".") and first[:-1].isalnum() and any(
                c.isdigit() for c in first
            ):
                if i + 1 < len(all_segments):
                    self._order_start = i + 1
                    return [i + 1]
        return []

    def classify_paragraph(self, lines) -> str:
        if lines:
            text = (lines[0].get("text") or "").lstrip()
            close = text.find(")")
            enumerated_quote = (
                lines[0]["x0"] >= self.body_baseline_x0 + 28
                and text.startswith("(")
                and close in (2, 3)
                and text[1:close].isalpha()
            )
            if enumerated_quote:
                return "blockquote"
            # Orders use a conventional 36pt first-line paragraph indent.
            # A true inset quotation keeps every line at that rail; a normal
            # paragraph's wrapped lines return to the body rail.
            if (
                getattr(self, "_order_start", None) is not None
                and lines[0]["x0"] >= self.body_baseline_x0 + 28
                and any(
                    line["x0"] <= self.body_baseline_x0 + 5 for line in lines[1:]
                )
            ):
                return "p"
        return super().classify_paragraph(lines)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        merged = []
        for block in op.blocks:
            if (
                block.kind == "blockquote"
                and merged
                and merged[-1].kind == "blockquote"
                and block.page != merged[-1].page
                and block.text.lstrip()[:1].islower()
            ):
                marker = self.page_marker(block.page)
                merged[-1].text += (
                    (f" {marker}" if marker else "")
                    + f" {block.text}"
                )
            else:
                merged.append(block)
        op.blocks = merged
        return op

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            return "", [line]  # unsigned order; first segment is body
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)
