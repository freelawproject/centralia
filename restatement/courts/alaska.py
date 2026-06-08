"""Alaska Supreme Court."""

from __future__ import annotations

from ._alaska import BaseAlaskaExtractor


class AlaskaSupreme(BaseAlaskaExtractor):
    court_id = "alaska"
    court_label = "The Supreme Court of the State of Alaska."
    author_titles = ("Justice",)
