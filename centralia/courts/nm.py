"""Supreme Court of the State of New Mexico.

Pleading-paper layout: a line-number column (1–25) runs down the left margin
(x0 ~40–54) beside the body (x0 72). Those numbers are layout furniture, not
text, so they are dropped before line clustering. Bylines are the standard bold
all-caps form ('THOMSON, Justice.'); the joining justices sign a 'WE CONCUR:'
roster the shared base already folds out of the opinion list.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Body text starts at x0 72; the line-number gutter ends well left of it.
_GUTTER_X1 = 60.0


class NewMexicoSupreme(StateSupreme):
    court_id = "nm"
    court_label = "Supreme Court of the State of New Mexico."

    def filter_margins(self, obj):
        if super().filter_margins(obj) is None:
            return None
        # Drop the left-margin pleading line-number gutter; a char whose right
        # edge sits left of the body baseline is a line number, not content.
        if (
            obj.get("text") is not None
            and obj.get("x1", obj.get("x0", 0)) <= _GUTTER_X1
        ):
            return None
        return True
