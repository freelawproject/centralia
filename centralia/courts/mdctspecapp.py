"""Appellate Court of Maryland (formerly the Court of Special Appeals).

Same caption byline as the Supreme Court of Maryland — 'Opinion by Arthur, J.'
/ 'Opinion by Ripken, J.' — so it reuses that court's parser.
"""

from __future__ import annotations

from .md import MarylandSupreme


class AppellateCourtOfMaryland(MarylandSupreme):
    court_id = "mdctspecapp"
    court_label = "Appellate Court of Maryland."
