"""Supreme Court of Guam.

Centered caption ('IN THE SUPREME COURT OF GUAM', parties, case numbers),
a centered 'OPINION' heading with 'Cite as: 2025 Guam 14', then the
abbreviated-title colon byline on the next page: 'TORRES, C.J.:' with the
body following. The shared abbreviated-title grammar handles it.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class GuamSupreme(AbbrevTitleSupreme):
    court_id = "guam"
    court_label = "Supreme Court of Guam."
