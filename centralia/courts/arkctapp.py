"""Arkansas Court of Appeals.

Intermediate appellate court. The opinion byline is a centered full caps name +
title ('CINDY GRACE THYER, Judge' / 'WENDY SCHOLTENS WOOD, Judge'); the shared
appellate base's abbreviated-title parser already recognizes it.

Court-specific tuning lives here:

  * The caption is a two-column header (parties on the left, the 'Appeal from …'
    block on the right) closed by a pair of horizontal rules — a LEFT rule under
    the parties and a RIGHT rule under the appeal block, at the same height,
    near vertical center. The shared footnote-rule finder filters candidates to
    the left quarter of the page before pairing them, so it never sees the
    right-hand partner and mistakes the left caption rule for the footnote
    separator — which chops the byline and the entire opinion body beneath it.
    ``find_footnote_separator`` is overridden here to drop any rule that has a
    same-height partner to its right (a caption pair) before choosing the
    separator.
"""

from __future__ import annotations

from typing import Optional

from ._appellate import StateAppellate


class ArkansasCourtOfAppeals(StateAppellate):
    court_id = "arkctapp"
    court_label = "Arkansas Court of Appeals."

    def find_footnote_separator(self, page) -> Optional[float]:
        """Topmost thin horizontal rule in the lower half that is the real
        footnote separator — not a two-column caption-bottom rule (which comes
        as a left+right pair) and not a text underline."""
        cutoff = page.height * 0.5
        thin = [
            r
            for r in page.rects
            if r["height"] < 2 and (r["x1"] - r["x0"]) >= 80 and r["top"] > cutoff
        ]
        if not thin:
            return None
        text_lines = page.extract_text_lines()

        def has_right_partner(r):
            # A caption-bottom rule has a sibling rule at the same height set off
            # to its right (the other column). A lone footnote rule does not.
            for o in thin:
                if o is r:
                    continue
                if abs(o["top"] - r["top"]) < 3 and o["x0"] > r["x1"] - 5:
                    return True
            return False

        def is_underline(r):
            for tl in text_lines:
                if (
                    tl["top"] - 1 <= r["top"] <= tl["bottom"] + 5
                    and r["x0"] < tl["x1"]
                    and r["x1"] > tl["x0"]
                ):
                    return True
            return False

        cands = [
            r
            for r in thin
            if r["x0"] < page.width * 0.5
            and not has_right_partner(r)
            and not is_underline(r)
        ]
        if not cands:
            return None
        return min(cands, key=lambda r: r["top"])["top"]
