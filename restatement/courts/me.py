"""Maine Supreme Judicial Court.

Standalone abbreviated-title byline, not bold: 'LIPEZ, J.' / 'MEAD, J.' /
'STANFILL, C.J.', with the opinion body on the following lines. The shared
abbreviated-title base handles it directly.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class MaineSupreme(AbbrevTitleSupreme):
    court_id = "me"
    court_label = "Maine Supreme Judicial Court."
