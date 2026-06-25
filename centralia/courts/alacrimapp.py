"""Alabama Court of Criminal Appeals.

Same Alabama appellate template as the Supreme Court (see
``AlabamaAppellate``). The Court of Criminal Appeals differs only in its docket
prefix (``CR``), its author titles (``Judge`` / ``Presiding Judge``), and the
``<court>`` label. The page-1 banner reads ``Alabama Court of Criminal
Appeals``; bylines look like ``WELCH, Judge.`` or ``PER CURIAM.``.
"""

from __future__ import annotations

from ._alabama import AlabamaAppellate


class AlabamaCriminalAppeals(AlabamaAppellate):
    court_id = "alacrimapp"
    court_label = "Court of Criminal Appeals of Alabama."
    docket_prefix = "CR"  # 'CR-YYYY-NNNN'
    author_titles = ("Judge", "Presiding Judge")
