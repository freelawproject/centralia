"""Supreme Court of New Hampshire.

Standalone abbreviated-title byline, not bold: 'MACDONALD, C.J.' /
'COUNTWAY, J.' / 'DONOVAN, J.', with the opinion body following. A
'DONOVAN, COUNTWAY, and GOULD, JJ., concurred.' line is a signature roster
(its continuation after the surname is another name, not a title), not a new
opinion. The shared abbreviated-title base handles all of this.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class NewHampshireSupreme(AbbrevTitleSupreme):
    court_id = "nh"
    court_label = "Supreme Court of New Hampshire."
