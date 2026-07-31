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

    # CA6 prints a one-line running head on every continuation page —
    # 'No. 25-1802 Ross v. Robinson, Hoover & Fink Page 2' — and sets it at two
    # heights: top~55.8 in the published measure (body at ~97) and top~45.0 in
    # the slip measure (body at ~84). The family's blanket 95pt cutoff cleared
    # the head on the first but ate the FIRST LINE of every page on the second —
    # body prose, section heads ('II. DISCUSSION'), and a whole dissent byline
    # ('THAPAR, Circuit Judge, dissenting.'). Bound the head by the band it
    # actually occupies and record it as furniture; leave the cutoff at the page
    # edge so nothing else above the body is removed.
    page2_header_cutoff = 30.0
    running_head_max_top = 70.0

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        return self._drop_head_band(page, lines)

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
