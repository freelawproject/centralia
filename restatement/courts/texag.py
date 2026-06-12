"""Office of the Attorney General of Texas. ('texag') — AG letter/formal opinions on the shared AG base."""

from __future__ import annotations

from ._agletter import AGLetterBase


class TexasAttorneyGeneral(AGLetterBase):
    court_id = "texag"
    court_label = "Office of the Attorney General of Texas."
