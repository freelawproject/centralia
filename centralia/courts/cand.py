"""United States District Court, Northern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

The court's own letterhead is printed SIDEWAYS up the left pleading margin
('United States District Court' / 'Northern District of California'), one
rotated glyph per row. pdfplumber reports those glyphs as ``upright`` (their
text matrix is rotated, not their glyph box), so nothing upstream can filter
them: they are interleaved into the body rows a glyph at a time ('u o r o 13
After more than six years …'). They are removed by their ROTATED TEXT MATRIX in
``correct_page_geometry`` — the one hook the coverage sweep reads the page
through as well — and recorded in the Removed box.
"""

from __future__ import annotations

from ._district import DistrictBase


class NorthernDistrictOfCalifornia(DistrictBase):
    # 28-line pleading paper runs the last numbered line to top≈730-739, past
    # the 725 default — so the final line of EVERY page was being discarded as
    # footer, mid-sentence ('...its membership database does not have entry').
    # The page number sits at 750+ with an empty band between, so 745 keeps the
    # body whole and still drops the folio.
    margin_bottom = 745

    @staticmethod
    def _is_rotated(char) -> bool:
        """True when the glyph is drawn on a rotated baseline.

        An upright glyph's text matrix is (size, 0, 0, size, x, y); the
        sideways letterhead's is (0, 1, -1, 0, x, y). ``upright`` cannot be
        used — pdfplumber reports these glyphs as upright.
        """
        if char.get("upright", True) is False:
            return True
        matrix = char.get("matrix")
        if not matrix or len(matrix) < 4:
            return False
        return abs(matrix[1]) > 0.01 or abs(matrix[2]) > 0.01

    def correct_page_geometry(self, page) -> None:
        """Remove the sideways pleading-margin letterhead, then apply the base
        overstrike fix.

        The removal has to happen HERE: this is the hook the completeness
        sweep and the audit read the page through, so a glyph merely skipped
        during line building would still count as lost text.
        """
        chars = page.chars
        rotated = [i for i, char in enumerate(chars) if self._is_rotated(char)]
        if rotated:
            if getattr(self, "_cand_dropped", None) is None:
                self._cand_dropped = []
            # Group the glyph columns by x, each read bottom-to-top (the
            # baseline runs up the page), so the letterhead is recorded in
            # reading order rather than reversed.
            columns: dict = {}
            for i in rotated:
                char = chars[i]
                columns.setdefault(round(char["x0"] / 8), []).append(char)
            for _key, column in sorted(columns.items()):
                text = "".join(
                    (char.get("text") or "")
                    for char in sorted(column, key=lambda c: -c["top"])
                ).strip()
                if text:
                    self._cand_dropped.append(
                        "[sideways margin letterhead removed: " + text + "]"
                    )
            for i in reversed(rotated):
                del chars[i]
        super().correct_page_geometry(page)

    def page_lines(self, page):
        # The shared district base swaps in a FILTERED page to cut the
        # pleading-paper line-number gutter, and a filtered page's char list is
        # a COPY — geometry corrected on it never reaches the real page the
        # coverage sweep reads. So correct the real page first.
        self.correct_page_geometry(page)
        return super().page_lines(page)

    def extract(self, pdf_path: str):
        self._cand_dropped = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Record the removed letterhead BEFORE the completeness sweep runs —
        the sweep happens inside ``super().extract()``, so a later append to
        ``doc.dropped`` would leave the rows reading as unplaced content."""
        seen, extra = set(), []
        for text in getattr(self, "_cand_dropped", []) or []:
            if text not in seen:
                seen.add(text)
                extra.append(text)
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    court_id = "cand"
    court_label = "United States District Court, Northern District of California."
