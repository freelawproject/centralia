"""United States Court of Appeals for the Seventh Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class SeventhCircuit(FederalCircuitBase):
    court_id = "ca7"
    court_label = "United States Court of Appeals for the Seventh Circuit."
    circuit_phrase = "seventh circuit"
    body_baseline_x0 = 144.0
    # A rehearing order sets its quoted amendment right down to y≈735, past the
    # shared 725 cutoff, which took a line of the quote with it. CA7 prints its
    # folio in the running HEAD, so there is no bottom furniture to protect —
    # nothing else in the corpus sits below 720.
    margin_bottom = 750.0
    gap_tight_max = 10.0
    gap_single_max = 14.0
    gap_double_max = 24.0

    # CA7's running header is a docket line with the folio at one end —
    # 'No. 24-2806 3' / 'Nos. 25-2878 & 25-2879 3' / 'No. 24-1630 Page 2' — and
    # it is set at two very different heights: top~104 in the bound measure
    # (body below it) and top~40-76 in the slip measure (body at ~72-108). A
    # blanket y cutoff cannot separate the two: at 95pt it left the bound header
    # in the body AND ate the first body lines of the slip pages. Identify the
    # header by its FORM instead (``is_docket_line``) and let the base sweep the
    # contiguous run at the top of the page; ``_drop_running_header`` records it.
    page2_header_cutoff = 30.0
    running_header_docket = True
    running_header_max_top = 110.0

    def is_docket_line(self, text) -> bool:
        toks = (text or "").split()
        if len(toks) < 2:
            return False
        if toks[0] in ("No.", "Nos."):
            # A trailing folio, bare ('… 24-2806 3') or labelled ('… Page 2').
            if toks[-1].isdigit():
                toks = toks[:-1]
                if toks and toks[-1].lower() == "page":
                    toks = toks[:-1]
        elif toks[0].isdigit() and len(toks) > 2 and toks[1] in ("No.", "Nos."):
            toks = toks[1:]  # a leading folio ('2 No. 24-2806')
        else:
            return False
        dockets = [t for t in toks[1:] if t not in ("&", "and")]
        if not dockets:
            return False
        return all(
            t.count("-") == 1 and all(p.isdigit() for p in t.strip(",;").split("-"))
            for t in dockets
        )

    def find_footnote_separator(self, page):
        return self._sep_at(page, 140, 150)
