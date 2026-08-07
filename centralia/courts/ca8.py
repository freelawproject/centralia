"""United States Court of Appeals for the Eighth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class EighthCircuit(FederalCircuitBase):
    court_id = "ca8"
    court_label = "United States Court of Appeals for the Eighth Circuit."
    circuit_phrase = "eighth circuit"

    # Headmatter criteria: typed rules; Submitted/Filed dates on one row.
    parse_criteria_enabled = True
    # CA8 repeats docket-then-caption for a consolidated record and states the
    # court appealed from ONCE below the last of them ('No. 24-3265' / 'United
    # States of America v. Bailey Belt' / 'No. 24-3296' / 'United States of
    # America v. Theodora Belt' / 'Appeal from United States District Court
    # for the District of South Dakota'). Filed against whichever case was
    # still open, every case but the last showed no origin at all — 15 of the
    # 16 petitions consolidated in minnesota_telecom_alliance.
    criteria_shared_tail = True

    def filter_margins(self, obj):
        """INK THE PAGE DOES NOT SHOW IS NOT CONTENT.

        Some CA8 chambers space their headmatter with runs of white-filled
        letters — 84 lowercase 'l's across four bands of page 1 in
        kyle_hane, 42 in permanent_general_assurance, more in
        minnesota_telecom_alliance. They are invisible to the reader and are
        typography, not text, but pdfplumber returns them like any other
        glyph, so they arrived in the middle of party names and case
        captions.

        Keyed on the fill being white, which is what makes them invisible —
        not on the letter, which is an ordinary one."""
        if obj.get("non_stroking_color") == (1.0, 1.0, 1.0):
            return None
        return super().filter_margins(obj)
    gap_tight_max = 10.0
    gap_single_max = 17.0
    gap_double_max = 28.0

    # The Eighth prints NO running header: every continuation page opens with
    # real text at top~73-75 (and the second line at ~91-95), and the folio sits
    # in the bottom margin. The family's blanket 95pt page-2 cutoff therefore
    # deleted the first — often the first TWO — lines of every page after the
    # first, which is where nearly all of this circuit's unplaced text came from.
    page2_header_cutoff = 0.0
