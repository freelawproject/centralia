"""Nevada Court of Appeals.

Same byline form as the Nevada Supreme Court (nev.py): 'By the Court,
WESTBROOK, J.:' — the tag is stripped and the abbreviated-title colon form
follows. Inherits the nev handling; only the identity differs. Half the
corpus is flatbed scans (no text layer) that honestly yield nothing.

The slips are born-digital text printed OVER a raster letterhead, and that
letterhead has a SEAL BLOCK in the bottom-left corner of every page — the
court name stacked in 5pt Helvetica over the printing-office form number
('COURT OF APPEALS / OF / NEVADA / (O) 1947B'). The raster's text layer reads
the form number as glyph soup ('«),I 194713', '(0) 1.44713'), a different
string on every page, so no repetition test can collapse it. It is identified
here by geometry — the seal band below the court's text frame — and surfaced in
the Removed box rather than left as unplaced content.
"""

from __future__ import annotations

from .nev import NevadaSupreme


class NevadaCourtOfAppeals(NevadaSupreme):
    court_id = "nevapp"
    court_label = "Nevada Court of Appeals."

    # The '141 Nev., Advance Opinion 35' citation banner can sit as high as
    # top~24 on the short-page slips; the inherited 32pt top margin cut it.
    margin_top = 18

    # A Nevada appellate authorship byline is ALWAYS the abbreviated form
    # ('By the Court, WESTBROOK, J.:'). 'Judge' is a TRIAL-court title here:
    # the headmatter's lower-court line wraps as '… Clark County; Bill /
    # Henderson, Judge.', and with 'Judge' in the byline grammar that orphaned
    # continuation opened a phantom second opinion.
    author_titles = tuple(t for t in NevadaSupreme.author_titles if "Judge" not in t)

    # Height of the letterhead seal band measured up from the page foot. The
    # court's text frame stops above it (the lowest body line seen in the
    # corpus is 1.5pt clear of this cut, so real prose is protected by the
    # body-line test below rather than by the band alone).
    _SEAL_BAND = 62.0

    def prepare_document(self, pdf) -> None:
        super().prepare_document(pdf)
        self._seal_lines = []

    def _is_seal(self, top: float, x0: float, size: float, text: str, height: float):
        """True if a line belongs to the bottom-left letterhead seal block (or
        the page-number/stamp artefacts printed beside it).

        Two conditions, both structural: the line sits in the seal band at the
        foot of the page, AND it is not a run of body text — body prose is set
        at body size, starts inside the text column, and runs long. The seal
        block fails all three (5–7pt, x0~11–40, a handful of characters)."""
        if top <= height - self._SEAL_BAND:
            return False
        is_body_prose = size >= 10.0 and x0 >= 100.0 and len(text) > 25
        return not is_body_prose

    def page_lines(self, page):
        lines = super().page_lines(page)
        height = page.height
        # Record the seal block from the RAW page: the inherited bottom margin
        # already discards part of it, and anything discarded silently would
        # read as unplaced content in the completeness sweep.
        seal = getattr(self, "_seal_lines", None)
        if seal is None:
            seal = self._seal_lines = []
        for ln in page.extract_text_lines(layout=False):
            text = (ln.get("text") or "").strip()
            if not text:
                continue
            chars = ln.get("chars") or []
            size = round(max((c.get("size", 0) for c in chars), default=0), 1)
            if self._is_seal(ln["top"], ln["x0"], size, text, height):
                if text not in seal:
                    seal.append(text)

        out = []
        for l in lines:
            text = self.line_plain_text(l).strip()
            size = self.line_meta(l)[0]
            if text and self._is_seal(
                l.get("top", 0.0), l.get("x0", 0.0), size, text, height
            ):
                continue
            out.append(l)
        return out

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the seal block in the Removed box BEFORE the completeness
        sweep runs, so the sweep can tell identified furniture from content."""
        for text in getattr(self, "_seal_lines", ()):
            if text not in doc.dropped:
                doc.dropped.append(text)
        super()._sweep_residual(doc, source_pages)
