"""United States Court of Appeals for the District of Columbia Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class DCCircuit(FederalCircuitBase):
    court_id = "cadc"
    court_label = (
        "United States Court of Appeals for the District of " "Columbia Circuit."
    )
    circuit_phrase = "district of columbia circuit"
    body_baseline_x0 = 156.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    # The D.C. Circuit prints NO running header on continuation pages. Most of
    # its opinions set a deep top margin (nothing above ~130pt), but its
    # unpublished dispositions and its bound opinions open real text at top~73-75
    # — a '* * *' section break, a body paragraph, an 'A' subheading — and the
    # family's blanket 95pt cutoff deleted it. Where a page 2+ DOES carry the
    # 'United States Court of Appeals / FOR THE DISTRICT OF COLUMBIA CIRCUIT'
    # banner from top~39, that is a second order's COVER page, i.e. content, not
    # furniture. Lower the cutoff to the page edge and let ``margin_top`` bound it.
    page2_header_cutoff = 30.0

    def find_footnote_separator(self, page):
        return self._sep_at(page, 150, 165)

    def extract_page_tables(self, page):
        """Reject a three-line prose false positive in dense footnotes.

        pdfplumber can interpret word gaps in a fully justified D.C. Circuit
        footnote as eight or nine narrow columns.  A real table with that many
        columns is not only three prose baselines tall; retaining this guard at
        the court boundary avoids weakening table support elsewhere.
        """
        out = []
        for table in super().extract_page_tables(page):
            rows = table.get("rows") or []
            n_cols = max((len(row) for row in rows), default=0)
            if len(rows) <= 3 and n_cols >= 8:
                continue
            out.append(table)
        return out
