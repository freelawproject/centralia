"""Alaska Supreme Court."""

from __future__ import annotations

from typing import Optional

from ._alaska import BaseAlaskaExtractor


class AlaskaSupreme(BaseAlaskaExtractor):
    court_id = "alaska"
    court_label = "The Supreme Court of the State of Alaska."
    author_titles = ("Justice",)

    def find_footnote_separator(self, page) -> Optional[float]:
        """Recognize Alaska Supreme Court's two footnote-rule measures.

        Merits opinions use a rule spanning the full 468-point body measure;
        the compact order template uses a two-inch (144-point) rule. Caption
        closures occupy an intermediate half-column measure (about 229–237
        points) and must remain part of headmatter.
        """
        body_width = page.width - 2 * self.body_baseline_x0
        candidates = []
        for rect in page.rects:
            width = rect["x1"] - rect["x0"]
            full_measure = abs(width - body_width) <= 12
            short_measure = abs(width - 144) <= 18
            if (
                rect["height"] < 2
                and rect["x0"] < self.body_baseline_x0 + 6
                and (full_measure or short_measure)
            ):
                candidates.append(rect)
        if not candidates:
            return None
        return min(candidates, key=lambda rect: rect["top"])["top"]
