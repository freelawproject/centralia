"""Washington Supreme Court.

Byline abbreviates the title and runs inline after an em-dash, not bold:
'GONZÁLEZ, J.—Our constitutional system ...' / 'MUNGIA, J. — If a person ...' /
'STEPHENS, C.J. (concurring)'. The all-caps surname is the discriminator
(accented capitals like 'GONZÁLEZ' included).
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class WashingtonSupreme(AbbrevTitleSupreme):
    court_id = "wash"
    court_label = "Washington Supreme Court."
