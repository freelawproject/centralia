"""Supreme Court of Arkansas."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class ArkansasSupreme(StateSupreme):
    court_id = "ark"
    court_label = "Supreme Court of Arkansas."
    author_titles = ("Justice", "Chief Justice", "Associate Justice")
    # Statutory and precedential quotations use a stable inset on both margins;
    # ordinary paragraphs merely indent their first line.  The shared detector
    # requires the former multi-line geometry.
    blockquote_by_indent = True

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Keep styled headmatter but fold the measured open caption columns.

        This is intentionally between a flattened text dump and a literal
        facsimile: banners retain the normal review styling, while only the
        parallel parties / appeal-from zone becomes a caption card with its
        source blank-row rhythm intact.
        """
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        result["summary"] = self._fold_open_caption(
            result.get("summary") or [], headmatter_segs
        )
        return result
