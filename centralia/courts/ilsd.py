"""United States District Court, Southern District of Illinois.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

ilsd quirks — the ECF band WRAPS, and the body starts inside the default top
margin:

  * S.D. Ill. stamps a two-line bates band ('Case 3:25-cv-00520-MAB Document 29
    Filed 07/09/26 Page 1 of 10 Page ID' at top≈13, then the overflowed PageID
    '#122' centred on its own row at top≈25). The band is set in the CM/ECF
    sans face (LiberationSans) — the only sans-serif on a sheet otherwise set in
    BookAntiqua — which is how it is identified here; the wrapped '#122' tail
    carries no words at all and so cannot be recognised from its text.
  * The court's own body text runs high: a continuation page's first line sits
    at top≈31.7, ABOVE the 39pt default top margin, so the margin filter was
    eating the opening line of nine straight pages of a social-security review.
    The margin is lowered to 28 — below the band's second row, above the body.
"""

from __future__ import annotations

from ._district import DistrictBase


class SouthernDistrictOfIllinois(DistrictBase):
    court_id = "ilsd"
    court_label = "United States District Court, Southern District of Illinois."

    # The body's first line can sit at top≈31.7; the ECF band's wrapped PageID
    # row sits at top≈25. Cut between them, not above them.
    margin_top = 28.0

    def extract(self, pdf_path):
        self._ecf_band: list[str] = []
        return super().extract(pdf_path)

    def page_lines(self, page):
        """Note the CM/ECF bates band before the margin filter removes it, so
        both of its rows are surfaced in the Removed box rather than vanishing.
        Identified by FACE: the band is the page's only sans-serif run."""
        band = getattr(self, "_ecf_band", None)
        if band is None:
            band = self._ecf_band = []
        try:
            for tl in page.extract_text_lines():
                if tl["top"] >= self.margin_top:
                    continue
                faces = {
                    (c.get("fontname") or "").split("+")[-1] for c in tl["chars"]
                }
                if not faces or not all(
                    "Sans" in f or "Arial" in f or "Helvetica" in f for f in faces
                ):
                    continue
                text = (tl.get("text") or "").strip()
                if text and text not in band:
                    band.append(text)
        except Exception:
            pass
        return super().page_lines(page)

    def _sweep_residual(self, doc, source_pages):
        # Runs BEFORE the completeness sweep, which skips anything already
        # rendered in the Removed box via doc.dropped.
        band = getattr(self, "_ecf_band", None)
        if band:
            doc.dropped = (
                list(doc.dropped)
                + [
                    "[CM/ECF bates band removed from every page — "
                    + band[0]
                    + "]"
                ]
                + band[1:]
            )
        super()._sweep_residual(doc, source_pages)
