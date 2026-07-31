"""Alaska Supreme Court."""

from __future__ import annotations

from ._alaska import BaseAlaskaExtractor


class AlaskaSupreme(BaseAlaskaExtractor):
    court_id = "alaska"
    court_label = "The Supreme Court of the State of Alaska."
    author_titles = ("Justice",)

    # The footnote-rule measures (full body measure / two-inch order rule) and
    # the page-one caption-closure exclusion now live in
    # :class:`BaseAlaskaExtractor`: the Court of Appeals prints the identical
    # template and needs the identical discriminator.
