"""United States Court of Appeals for the Fifth Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class FifthCircuit(FederalCircuitBase):
    court_id = "ca5"
    court_label = "United States Court of Appeals for the Fifth Circuit."
    circuit_phrase = "fifth circuit"

    # Headmatter criteria: typed rules; docket shares its row with a calendar marker.
    parse_criteria_enabled = True
    # CA5's headmatter is a plain stack: the court's name, the docket numbers,
    # the origin, the roster — then the author and the opinion. It fences the
    # bands with typed rules but does not always keep a band to one row: the
    # origin can arrive on the end of the caption's last row, and the roster
    # after a rehearing label. It states its origin ONCE for a consolidated
    # record.
    roster_can_share_row = True
    history_can_share_row = True
    criteria_shared_tail = True
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 16.0
    gap_double_max = 28.0

    def _tail_kind(self, text):
        """CA5 DOES NOT PRINT APPEARANCES IN ITS HEADMATTER.

        Its bands are: the court's name, the docket numbers, the origin, the
        roster — then the author and the opinion. There is no counsel band, so
        there is nothing here for the shared reader to find, and anything it
        DID claim would by definition be something else wearing an appearance's
        clothes. The field stays absent."""
        return "summary"

    def filter_margins(self, obj):
        # CA5 page-1 right-column 'FILED <date> / Clerk' stamp.  It overlaps
        # the centered Old English court banner in X, so an x>=440 crop cuts
        # the final ``ls`` off ``Appeals`` and can attach ``Clerk`` to the
        # first party.  The stamp is consistently Arial; the authored slip
        # caption uses OldEnglish/Equity faces.  Filter on that structural font
        # distinction and preserve the complete banner underneath.
        # The stamp runs DEEPER than the banner it sits beside — the clerk's
        # name and title reach ~230pt while the caption's first docket is at
        # ~186 ('Lyle W. Cayce' / 'Clerk'). Bounded at 220 the last word
        # survived, landed on the end of a typed rule ('_____________ Clerk')
        # and opened the next case's name with it. Below the banner band, keep
        # the font test but scope it to the stamp's own right column.
        if obj.get("page_number", 1) == 1 and "arial" in (
            obj.get("fontname") or ""
        ).lower():
            top = obj.get("top", 0)
            if top <= 220 or (top <= 280 and obj.get("x0", 0) >= 440):
                return None
        return super().filter_margins(obj)

    def find_footnote_separator(self, page):
        """CA5 TYPES its footnote rule rather than drawing it.

        ``_sep_at`` searches ``page.rects``, so a separator set as a run of
        underscores in the text layer is invisible to it and the footnote below
        stayed in the body with its mark unresolved. Look for the drawn rule
        first, then for the typed one at the same anchor."""
        drawn = self._sep_at(page, 100, 150)
        if drawn is not None:
            return drawn
        best = None
        for line in self._text_lines(page):
            text = (line.get("text") or "").strip()
            if not text or set(text) != {"_"}:
                continue
            if not (100 <= line.get("x0", 0) <= 150):
                continue
            if line.get("top", 0) <= page.height * 0.30:
                continue
            if best is None or line["top"] < best:
                best = line["top"]
        return best
