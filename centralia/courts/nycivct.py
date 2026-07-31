"""Civil Court of the City of New York, published as 'NY Slip Op' (U).

Shares the NewYorkSlipOp cover-page + e-filed-decision format.
"""

from __future__ import annotations

from collections import Counter

from ._nyslipop import NewYorkSlipOp


class NewYorkCivilCourt(NewYorkSlipOp):
    court_id = "nycivct"
    court_label = "Civil Court of the City of New York."

    _nyc_form: list = []

    def extract(self, pdf_path):
        self._nyc_form = []
        return super().extract(pdf_path)

    # --------------------------------------- the disposition checkbox form
    def correct_page_geometry(self, page) -> None:
        """Lift the court's disposition checkbox form off the foot of the page.

        The decision closes with the Civil Court's pre-printed tick-box form —
        'CHECK ONE: X CASE DISPOSED / NON-FINAL DISPOSITION', 'MOTION SEQ. #:
        GRANTED X DENIED ...', 'CHECK IF APPROPRIATE: SETTLE ORDER ...',
        'NOTES' — an administrative form, not part of the decision.

        It is set at 7pt against a 12pt body and its rows are packed tighter
        than one line, with a 40pt display glyph stamped through the middle of
        them; pdfplumber therefore collapses the whole form into a single
        character-interleaved row ('MOTION SSEQQ. #I#2:'). Left in, that row
        lands at the end of the opinion body as unreadable text and its two
        MOTION SEQ lines still report as unplaced.

        Identified by type size alone, never by wording: a *whole row* set at
        least 3.5pt below the page's own body size, of which the form has
        several in a run. Nothing else here is: the only other undersized
        glyphs in the corpus are superscript ordinals ('19th') and footnote
        markers, which are a couple of characters riding inside a body row.
        The removal then spans the block those rows bound, so the display glyph
        struck across them goes with the form it belongs to.

        Done at the geometry hook because the completeness sweep and the audit
        read the page through it too; the rows are recorded first so the form
        is surfaced in the Removed box rather than lost.
        """
        super().correct_page_geometry(page)
        ink = [c for c in page.chars if not c["text"].isspace()]
        if not ink:
            return
        body = Counter(round(c["size"], 1) for c in ink).most_common(1)[0][0]
        rows: dict = {}
        for c in page.chars:
            rows.setdefault(round(c["top"] / 2.0), []).append(c)
        small = []
        for r in rows.values():
            sized = [round(c["size"], 1) for c in r if not c["text"].isspace()]
            if len(sized) >= 8 and max(sized) <= body - 3.5:
                small.append(r)
        if len(small) < 2:
            return
        flat = [c for r in small for c in r]
        top = min(c["top"] for c in flat)
        bottom = max(c["bottom"] for c in flat)
        # Rebuilt from every glyph in the row, spaces included, so the recorded
        # entry reads as the form does rather than as one run-together word.
        for r in sorted(small, key=lambda r: min(c["top"] for c in r)):
            text = " ".join(
                "".join(c["text"] for c in sorted(r, key=lambda c: c["x0"])).split()
            )
            if text and text not in self._nyc_form:
                self._nyc_form = list(self._nyc_form) + [text]
        drop = {
            id(c)
            for c in page.chars
            if top - 0.5 <= c["top"] and c["bottom"] <= bottom + 0.5
        }
        page.chars[:] = [c for c in page.chars if id(c) not in drop]
        objs = page.objects.get("char")
        if objs is not None and objs is not page.chars:
            objs[:] = [c for c in objs if id(c) not in drop]

    def _sweep_residual(self, doc, source_pages) -> None:
        """See ``nyfamct`` — the shared NY base appends the republication notice
        to ``dropped`` only after ``extract()`` returns, i.e. after this sweep
        has already run, so the notice read as unplaced content in every file.
        Flush it (and the caption's typed corner rules, and the disposition
        form) first."""
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
        if self._nyc_form:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                t for t in self._nyc_form if t not in have
            ]
        super()._sweep_residual(doc, source_pages)
        # A caption closed by a typed rule capped with an 'x' ('---------x').
        rails = [
            r["text"]
            for r in doc.residual
            if self.is_rule_text((r.get("text") or "").strip())
        ]
        if rails:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                t for t in dict.fromkeys(rails) if t not in have
            ]
            doc.residual = [
                r
                for r in doc.residual
                if not self.is_rule_text((r.get("text") or "").strip())
            ]
