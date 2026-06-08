"""Supreme Court of the State of Idaho.

Two-column `)`-delimited caption (like Alaska) but a standard byline-at-start
body ('MEYER, Justice.'), so the core pipeline handles the opinions.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class IdahoSupreme(StateSupreme):
    court_id = "idaho"
    court_label = "Supreme Court of the State of Idaho."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers
    author_titles = ("Justice", "Chief Justice", "Pro Tem Justice")
