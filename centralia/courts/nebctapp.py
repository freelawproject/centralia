"""Nebraska Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.'
/ 'NAME, J.' / 'PER CURIAM'). Shares the Nebraska Advance Sheets reporter format
(running-header furniture dropped, numbered syllabus routed to the syllabus
field) via NebraskaReporterStyle.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._nebraska import NebraskaReporterStyle


class NebraskaCourtOfAppeals(NebraskaReporterStyle, StateAppellate):
    court_id = "nebctapp"
    court_label = "Nebraska Court of Appeals."

    def _sweep_residual(self, doc, source_pages):
        """Publish the running-header band to ``doc.dropped`` BEFORE the
        completeness sweep reads it.

        ``NebraskaReporterStyle`` collects the per-page reporter band while
        reading pages but only appends it to ``doc.dropped`` after
        ``extract()`` returns — and the sweep runs inside ``extract()``. The
        deepest band line ('Cite as 34 Neb. App. 205') also sits below the
        three-line margin window the sweep's repetition detector inspects, so
        without this it reports as unplaced content on every page."""
        band = [t for t in getattr(self, "_neb_dropped", None) or [] if t]
        if band:
            doc.dropped = _dedupe(list(doc.dropped) + band)
        super()._sweep_residual(doc, source_pages)

    def extract(self, pdf_path):
        # The mixin appends the same band again on the way out; collapse the
        # duplicates so the Removed box shows each header line once.
        doc = super().extract(pdf_path)
        doc.dropped = _dedupe(doc.dropped)
        return doc


def _dedupe(rows):
    """Order-preserving de-duplication tolerant of unhashable rows."""
    seen, out = set(), []
    for r in rows:
        try:
            if r in seen:
                continue
            seen.add(r)
        except TypeError:  # image/dict rows are never repeated
            pass
        out.append(r)
    return out
