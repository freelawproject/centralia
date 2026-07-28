"""United States Court of Appeals for the Third Circuit."""

from __future__ import annotations

from collections import Counter

import pdfplumber

from ._circuit import FederalCircuitBase


class ThirdCircuit(FederalCircuitBase):
    court_id = "ca3"
    court_label = "United States Court of Appeals for the Third Circuit."
    circuit_phrase = "third circuit"
    # Published CA3 opinions use a narrow x≈144..468 body measure. The federal
    # default x≈72 makes ordinary prose appear deeply indented and therefore
    # quote-like.
    body_baseline_x0 = 144.0
    gap_tight_max = 12.0
    # Main text leads at ~17pt; genuinely single-spaced quotations are tighter.
    gap_single_max = 16.0
    gap_double_max = 38.0
    blockquote_by_indent = True

    def find_footnote_separator(self, page):
        """CA3's 144pt footnote rule is anchored at the body rail x≈144."""
        return self._sep_at(
            page, self.body_baseline_x0 - 4, self.body_baseline_x0 + 4
        )

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

    def extract(self, pdf_path):
        self._measure_body_template(pdf_path)
        doc = super().extract(pdf_path)
        self._harvest_counsel_endnote(doc)
        return doc

    def _measure_body_template(self, pdf_path):
        """Derive CA3's body rail and leading from the document itself."""
        x0s = Counter()
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
                    page_rows.append(usable)
        except Exception:
            return
        if not x0s:
            return
        baseline = float(x0s.most_common(1)[0][0])
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

    def _harvest_counsel_endnote(self, doc):
        """Move the recurring post-disposition ``Counsel for …`` list out."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        cut = next(
            (
                i
                for i, block in enumerate(op.blocks)
                if self._plain(block.text).lower().startswith("counsel for ")
            ),
            None,
        )
        if cut is None:
            return
        doc.trailer = list(doc.trailer) + [
            str(block.text or "").strip()
            for block in op.blocks[cut:]
            if str(block.text or "").strip()
        ]
        del op.blocks[cut:]
