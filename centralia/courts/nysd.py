"""United States District Court, Southern District of New York.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from ._district import DistrictBase


class SouthernDistrictOfNewYork(DistrictBase):
    court_id = "nysd"
    court_label = "United States District Court, Southern District of New York."

    # The clerk's electronic-filing stamp — a boxed graphic reading 'USDC SDNY
    # / DOCUMENT / ELECTRONICALLY FILED / DOC #: / DATE FILED: ...' — is
    # applied to the top-right corner of page 1, clear of the caption. Only
    # the date inside it is live text; the rest is the graphic. It is filing
    # furniture, so both the graphic and that date are surfaced in the Removed
    # box rather than read as caption content.
    _STAMP_X0 = 0.6  # fraction of page width: the stamp's left edge
    _STAMP_BOTTOM = 135.0  # pt: nothing below this is the stamp

    def _filing_stamp_box(self, page):
        """The bbox of the page-1 filing stamp, or None. Taken from the
        largest image sitting in the top-right corner — the stamp's own box
        rule — so the nested 'DATE FILED' strip and the date text are located
        by geometry rather than guessed at."""
        if page.page_number != 1:
            return None
        best = None
        for im in page.images:
            if im["x0"] < page.width * self._STAMP_X0:
                continue
            if im["bottom"] > self._STAMP_BOTTOM:
                continue
            area = (im["x1"] - im["x0"]) * (im["bottom"] - im["top"])
            if best is None or area > best[0]:
                best = (area, (im["x0"], im["top"], im["x1"], im["bottom"]))
        if best is None:
            return None
        x0, top, x1, bottom = best[1]
        # The stamp is applied over the top margin, so its box can reach up
        # into the CM/ECF header band. That band is already dropped by
        # ``margin_top`` — clamp to it so the header's text is not collected
        # twice, once as margin furniture and once as the stamp.
        return (x0, max(top, float(self.margin_top)), x1, bottom)

    def extract_page_images(self, page):
        box = self._filing_stamp_box(page)
        images = super().extract_page_images(page)
        if box is None:
            return images
        x0, top, x1, bottom = box
        return [
            im
            for im in images
            if not (
                im["x0"] >= x0 - 2
                and im["x1"] <= x1 + 2
                and im["top"] >= top - 2
                and im["bottom"] <= bottom + 2
            )
        ]

    def _in_stamp(self, obj) -> bool:
        box = getattr(self, "_stamp_box", None)
        if box is None:
            return False
        x0, top, x1, bottom = box
        return (
            obj["x0"] >= x0 - 2
            and obj["x1"] <= x1 + 2
            and obj["top"] >= top - 2
            and obj["bottom"] <= bottom + 2
        )

    def filter_margins(self, obj):
        if super().filter_margins(obj) is None:
            return None
        return None if self._in_stamp(obj) else True

    def page_lines(self, page):
        """Take the stamp's date out at the CHARACTER level, before lines are
        clustered. The stamp sits at the banner's height, so pdfplumber reads
        'UNITED STATES DISTRICT COURT' and the stamped date as one line;
        filtering whole lines would either keep the date in the caption or
        take the banner out with it."""
        self._stamp_box = self._filing_stamp_box(page)
        if self._stamp_box is not None:
            inside = sorted(
                (c for c in page.chars if self._in_stamp(c)),
                key=lambda c: (round(c["top"], 1), c["x0"]),
            )
            text = "".join(c.get("text") or "" for c in inside).strip()
            if text:
                self._stamp_text.append(text)
        try:
            return super().page_lines(page)
        finally:
            self._stamp_box = None

    def extract(self, pdf_path):
        self._stamp_text = []
        doc = super().extract(pdf_path)
        if self._stamp_text:
            doc.dropped = list(doc.dropped) + [
                "USDC SDNY filing stamp: " + " ".join(self._stamp_text)
            ]
        return doc
