"""United States District Court, Central District of Illinois.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

ilcd quirks:

  * THREE typefaces, one per authority. The ruling itself is set in BookAntiqua;
    CM/ECF stamps its bates line ('1:25-cv-01168-CRL # 20 Filed: 05/20/26 Page 1
    of 7') in LiberationSans across the top of every page; and the ILCD clerk
    stamps a three-row E-FILED block flush right on page 1 ('E-FILED' /
    'Wednesday, 20 May, 2026 11:54:47 AM' / 'Clerk, U.S. District Court, ILCD')
    in MyriadPro. Both stamps are furniture, and the face is what identifies
    them — the stamp's third row sits at top≈48, INSIDE the body margin, so it
    was being rendered as a caption row of the headmatter. Both are removed and
    surfaced in the Removed box.
  * Outline HEADS ARE NOT PARAGRAPH TAILS. The court sets its heads ('II.
    Amended Complaint', 'A. Screening Standard') in bold, short of the measure
    and without terminal punctuation, and body prose in roman. When such a head
    opened a page it was folded onto the tail of the roman paragraph that closed
    the page before ('… which he has timely filed. II. Amended Complaint') —
    see ``_begins_paragraph_block``.
"""

from __future__ import annotations

from ._district import DistrictBase

# The clerk's E-FILED stamp and the CM/ECF bates band are the only runs on the
# sheet not set in the court's body face; each has its own.
_STAMP_FACES = ("MyriadPro", "LiberationSans")
# The stamp block occupies the top inch of page 1; nothing of the ruling starts
# above the court name at top≈75.
_STAMP_BAND_BOTTOM = 60.0


def _faces(line_or_tl) -> set:
    return {
        (c.get("fontname") or "").split("+")[-1]
        for c in (line_or_tl.get("chars") or [])
    }


def _is_stamp(line) -> bool:
    """True when every glyph of the line is set in a court-stamp face and the
    line sits in the top stamp band — the CM/ECF bates line or the clerk's
    E-FILED block, never the ruling."""
    if line.get("top", 0) >= _STAMP_BAND_BOTTOM:
        return False
    faces = _faces(line)
    return bool(faces) and all(
        any(f.startswith(s) for s in _STAMP_FACES) for f in faces
    )


class CentralDistrictOfIllinois(DistrictBase):
    court_id = "ilcd"
    court_label = "United States District Court, Central District of Illinois."

    def extract(self, pdf_path):
        self._ecf_band: list[str] = []
        self._clerk_stamp: list[str] = []
        return super().extract(pdf_path)

    def page_lines(self, page):
        """Record every court-stamp line — including the E-FILED block's third
        row, which falls inside the body margin — and keep it out of the body.

        The two stamps are recorded apart because they repeat differently: the
        CM/ECF band is restamped on every page (noted once), the clerk's E-FILED
        block appears only on page 1."""
        band = getattr(self, "_ecf_band", None)
        if band is None:
            band = self._ecf_band = []
        stamp = getattr(self, "_clerk_stamp", None)
        if stamp is None:
            stamp = self._clerk_stamp = []
        try:
            for tl in page.extract_text_lines():
                if not _is_stamp(tl):
                    continue
                text = (tl.get("text") or "").strip()
                if not text:
                    continue
                bucket = (
                    band
                    if any(f.startswith("LiberationSans") for f in _faces(tl))
                    else stamp
                )
                if text not in bucket:
                    bucket.append(text)
        except Exception:
            pass
        return [l for l in super().page_lines(page) if not _is_stamp(l)]

    def _begins_paragraph_block(self, lines) -> bool:
        """Whether ``lines`` opens a block of its own rather than continuing the
        paragraph that ended the previous page.

        C.D. Ill. outline heads are bold, stop short of the measure and carry no
        terminal punctuation; body prose is roman and wraps to the full measure.
        A group with all three properties cannot be anybody's continuation, so a
        head landing at the top of a page must not be swallowed by the paragraph
        above it. A bold DECRETAL paragraph ('4) The Court GRANTS …') runs to the
        measure and closes with a period, so its own page-break continuation
        still folds correctly."""
        if not lines or not all(self._line_all_bold(l) for l in lines):
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        right_edge = pw - self.body_baseline_x0
        measure = right_edge - self.body_baseline_x0
        if any(l["x1"] > right_edge - 0.15 * measure for l in lines):
            return False
        tail = self.line_plain_text(lines[-1]).strip()
        return bool(tail) and not tail.endswith((".", "?", "!"))

    def _sweep_residual(self, doc, source_pages):
        # Before the completeness sweep, which skips anything already rendered
        # in the Removed box through doc.dropped.
        extra = []
        band = getattr(self, "_ecf_band", None) or []
        if band:
            extra.append(
                "[CM/ECF bates band removed from every page — " + band[0] + "]"
            )
            extra.extend(band[1:])
        stamp = getattr(self, "_clerk_stamp", None) or []
        if stamp:
            extra.append("[clerk's E-FILED stamp removed: " + " · ".join(stamp) + "]")
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)
