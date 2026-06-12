"""United States Court of Appeals for the Second Circuit."""

from __future__ import annotations

from collections import Counter

from ._circuit import FederalCircuitBase


class SecondCircuit(FederalCircuitBase):
    court_id = "ca2"
    court_label = "United States Court of Appeals for the Second Circuit."
    circuit_phrase = "second circuit"
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0

    # CA2 sets its summary orders (and some opinions) on numbered paper: a left
    # column of sequential line numbers (x0≈44, the body at x0≈86) that, left in
    # place, pdfplumber merges onto each line ('10 PER CURIAM:', '8 DAVID JOHN
    # CAMPBELL,') — breaking byline, caption, and heading detection. There is no
    # margin rule, so the gutter is found by CONTENT: a far-left column of bare
    # integers. Gated on detection, so un-numbered filings are untouched.
    def page_lines(self, page):
        gx = self._linenum_gutter_x(page)
        if gx is not None:
            page = page.filter(lambda c: c.get("x0", 0) >= gx)
        return super().page_lines(page)

    @staticmethod
    def _linenum_gutter_x(page):
        """X just right of a left-margin line-number gutter, or None. The gutter
        is a vertical column of >=5 bare digit glyphs clustered at the far-left
        margin (x0 < 75). Cluster around the modal left edge so a stray body
        digit further right doesn't defeat detection (two-digit numbers span
        ~1.5 glyph widths, hence the 12pt window)."""
        digits = [
            c for c in page.chars if c.get("text", "").isdigit() and c.get("x0", 0) < 75
        ]
        if len(digits) < 5:
            return None
        mode = Counter(round(c["x0"]) for c in digits).most_common(1)[0][0]
        col = [c for c in digits if abs(c["x0"] - mode) <= 12]
        if len(col) < 5:
            return None
        return max(c["x1"] for c in col) + 2
