"""Alaska Court of Appeals."""

from __future__ import annotations

from ._alaska import BaseAlaskaExtractor


class AlaskaCourtOfAppeals(BaseAlaskaExtractor):
    court_id = "alaskactapp"
    court_label = "Court of Appeals of the State of Alaska."
    author_titles = ("Judge",)
