"""New York Family Court, published as 'NY Slip Op' (U).

Shares the NewYorkSlipOp cover-page + e-filed-decision format.
"""

from __future__ import annotations

from ._nyslipop import NewYorkSlipOp


class NewYorkFamilyCourt(NewYorkSlipOp):
    court_id = "nyfamct"
    court_label = "Family Court of the State of New York."

    def _sweep_residual(self, doc, source_pages) -> None:
        """Two furniture items were reading as unplaced content.

        ``NewYorkSlipOp`` collects the republication notice ('Cases posted with
        a "30000" identifier ... not selected for official publication.') while
        reading the pages, but only appends it to ``dropped`` after
        ``extract()`` returns — i.e. after the completeness sweep inside that
        call has already looked. Flush it first (and clear it, so the base's own
        append cannot double it).

        The pleading caption is then closed top and bottom by a TYPED rule — a
        row of hyphens capped with an 'x' at the corner ('----------x'), the
        typewriter-era stand-in for a drawn box edge. The body builder rightly
        declines to render it as text, but it was then silently gone; it is
        furniture, so surface it in the Removed box. Taken off the residual
        itself, so a rule the styled caption *does* render as a divider can
        never be doubled here."""
        pending = getattr(self, "_ny_dropped", None)
        if pending:
            seen, uniq = set(doc.dropped), []
            for t in pending:
                if t and t not in seen:
                    seen.add(t)
                    uniq.append(t)
            if uniq:
                doc.dropped = list(doc.dropped) + uniq
            self._ny_dropped = []
        super()._sweep_residual(doc, source_pages)
        self._drop_typed_rules(doc)

    def _drop_typed_rules(self, doc) -> None:
        rails = [
            r["text"]
            for r in doc.residual
            if self.is_rule_text((r.get("text") or "").strip())
        ]
        if not rails:
            return
        have = set(doc.dropped)
        doc.dropped = list(doc.dropped) + [
            t for t in dict.fromkeys(rails) if t not in have
        ]
        doc.residual = [
            r
            for r in doc.residual
            if not self.is_rule_text((r.get("text") or "").strip())
        ]
