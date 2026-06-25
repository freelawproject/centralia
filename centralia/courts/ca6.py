"""United States Court of Appeals for the Sixth Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase

_BOX = {"│", "┐", "┘", "┌", "└", "├", "┤", "┬", "┴", "┼"}


class SixthCircuit(FederalCircuitBase):
    court_id = "ca6"
    court_label = "United States Court of Appeals for the Sixth Circuit."
    circuit_phrase = "sixth circuit"
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0

    def find_caption_divider(self, page):
        """CA6 draws the caption box with Unicode box-drawing chars."""
        cols = [c for c in page.chars if c.get("text") in _BOX]
        if len(cols) < 3:
            return super().find_caption_divider(page)
        from collections import Counter

        x, _ = Counter(round(c["x0"]) for c in cols).most_common(1)[0]
        column = [c for c in cols if abs(c["x0"] - x) < 3]
        if len(column) < 3:
            return super().find_caption_divider(page)
        return (
            float(x),
            min(c["top"] for c in column) - 2,
            max(c["bottom"] for c in column) + 2,
        )

    def skip_headmatter_segment(self, seg) -> bool:
        if seg:
            t = (seg[0].get("text") or "").strip().upper()
            if t.startswith(
                (
                    "RECOMMENDED FOR PUBLICATION",
                    "NOT RECOMMENDED FOR PUBLICATION",
                    "PURSUANT TO SIXTH CIRCUIT",
                    "FILE NAME:",
                )
            ):
                return True
        return super().skip_headmatter_segment(seg)
