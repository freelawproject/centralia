"""Office of the Attorney General of Maryland. ('mdag') — AG letter/formal opinions on the shared AG base."""

from __future__ import annotations

from ._agletter import AGLetterBase


class MarylandAttorneyGeneral(AGLetterBase):
    court_id = "mdag"
    court_label = "Office of the Attorney General of Maryland."
