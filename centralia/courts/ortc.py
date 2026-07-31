"""Oregon Tax Court, Magistrate Division.

')'-rail caption under the 'IN THE OREGON TAX COURT / MAGISTRATE
DIVISION' banner, a centered decision heading ('DECISION' / 'DECISION OF
DISMISSAL' / 'ORDER …'), and a closing block 'This document was signed by
Magistrate Richard D. Davis and entered on <date>' that names the author.
A running footer ('ORDER TC-MD 250545R 6') sits in the bottom margin.
"""

from __future__ import annotations

from ._district import DistrictBase


class OregonTaxMagistrate(DistrictBase):
    court_id = "ortc"
    court_label = "Oregon Tax Court, Magistrate Division."

    # Quoted statutes are single-spaced at ~14pt but indented on the LEFT only
    # (they run to the full right margin), so the both-margins ``blockquote_by_
    # indent`` test misses them and their ~14pt leading falls below the default
    # gap_tight_max (16) into the 'notice' band. Lower the tight threshold so a
    # single-spaced run lands in the blockquote band (body stays double-spaced
    # at ~28pt).
    gap_tight_max = 12

    def extract(self, pdf_path):
        self._ortc_band = {}
        return super().extract(pdf_path)

    def page_lines(self, page):
        """Record the Oregon Tax Reports running head before the margin filter
        discards it.

        The corpus holds two document styles. Magistrate Division DECISIONs are
        letter-size (612pt) CM/ECF filings with nothing in the top margin.
        Regular Division opinions are the REPORTER setting on a narrow 396pt
        sheet, and every page of those carries exactly one running-head line in
        the top margin — 'No. 9 October 28, 2022 173' on the opening page, then
        alternating '<folio> <case name>' and 'Cite as 25 OTR 173 (2022)
        <folio>'. It is page furniture, but it has to be SURFACED rather than
        silently clipped, so stash it here for ``_sweep_residual`` to publish to
        the Removed box."""
        band = [
            l
            for l in self._text_lines(page.filter(lambda o: o["top"] < self.margin_top))
            if (l.get("text") or "").strip()
        ]
        if band:
            stash = getattr(self, "_ortc_band", None)
            if stash is None:
                stash = self._ortc_band = {}
            stash[page.page_number] = [
                (l.get("text") or "").strip() for l in band
            ]
        return super().page_lines(page)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Publish the reporter running head to ``doc.dropped`` BEFORE the
        completeness sweep reads it — the sweep runs inside ``extract()``."""
        stash = getattr(self, "_ortc_band", None) or {}
        rows, seen = list(doc.dropped), set(doc.dropped)
        for pno in sorted(stash):
            for t in stash[pno]:
                if t not in seen:
                    seen.add(t)
                    rows.append(t)
        doc.dropped = rows
        super()._sweep_residual(doc, source_pages)

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        if not getattr(self, "_district_author", None):
            self._district_author = self._signed_by(all_segments)
        return out

    @staticmethod
    def _is_fully_bold(text) -> bool:
        """A block whose entire content is bold (bold or bold-italic). The
        appeal-rights boilerplate and the 'signed by … entered on' line are set
        this way; regular-Roman body prose and italic-only lead-in terms
        ('<em>Webster's</em> defines …') are not."""
        s = str(text).strip()
        return s.startswith("<strong>") and s.endswith("</strong>")

    def _harvest_signature(self, doc):
        """Peel the trailing bold notices (appeal-rights advisory, 'This
        document was signed by … entered on <date>') off the opinion into
        ``doc.dropped`` — keyed on font/style, not wording — then let the
        district signature harvest run on what remains."""
        if doc.opinions:
            op = doc.opinions[-1]
            blocks = op.blocks
            peeled = []
            while blocks and self._is_fully_bold(blocks[-1].text):
                peeled.append(self._untag(blocks[-1].text).strip())
                blocks = blocks[:-1]
            if peeled:
                op.blocks = blocks
                doc.dropped = list(doc.dropped or []) + list(reversed(peeled))
        super()._harvest_signature(doc)

    def _signed_by(self, all_segments):
        """Author from 'This document was signed by [Presiding] Magistrate
        Richard D. Davis and entered on <date>.'"""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for key in (
                    "signed by presiding magistrate ",
                    "signed by magistrate ",
                ):
                    ki = low.find(key)
                    if ki < 0:
                        continue
                    name = []
                    for tok in t[ki + len(key) :].split():
                        core = tok.strip(".,")
                        if tok.lower() in ("and", "on") or not core:
                            break
                        if core[0].isupper():
                            name.append(core + "." if len(core) == 1 else core)
                        else:
                            break
                    if name:
                        return " ".join(name)
        return None
