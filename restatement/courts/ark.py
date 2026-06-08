"""Supreme Court of Arkansas."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class ArkansasSupreme(StateSupreme):
    court_id = "ark"
    court_label = "Supreme Court of Arkansas."
    author_titles = ("Justice", "Chief Justice", "Associate Justice")
