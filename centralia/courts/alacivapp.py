"""Alabama Court of Civil Appeals.

Same Alabama appellate template as the Supreme Court (see
``AlabamaAppellate``). The Court of Civil Appeals differs only in its docket
prefix (``CL``), its author titles (``Judge`` / ``Presiding Judge``), and the
``<court>`` label. The page-1 banner reads ``ALABAMA COURT OF CIVIL APPEALS``;
bylines look like ``BOWDEN, Judge.``.
"""

from __future__ import annotations

from ._alabama import AlabamaAppellate


class AlabamaCivilAppeals(AlabamaAppellate):
    court_id = "alacivapp"
    court_label = "Court of Civil Appeals of Alabama."
    docket_prefix = "CL"  # 'CL-YYYY-NNNN'
    author_titles = ("Judge", "Presiding Judge")
