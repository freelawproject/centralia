"""United States District Court, Eastern District of Washington.

CM/ECF filing — a single ruling by one judge, on numbered pleading paper.

waed quirks:
  * a RED filing stamp sits top-right of page 1 ('FILED IN THE / U.S.
    DISTRICT COURT / EASTERN DISTRICT OF WASHINGTON / <date> / SEAN F.
    MCAVOY, CLERK') — furniture, dropped and surfaced;
  * the BLUE CM/ECF bates header ('Case 2:24-cv-00417-SAB ECF No. 36 filed
    04/07/26 PageID.615 Page 1 of 8') runs across the top of every page —
    also furniture, also surfaced;
  * BOTH ARE IDENTIFIED BY INK COLOUR, which is what makes them separable at
    all. Each stamp is applied over the sheet, so its glyphs land on the SAME
    BASELINES as the document's own text and the line clusterer merges them
    ('AO 245B (Rev. 11/25) Judgment in a Criminal Case U.S. DISTRICT COURT',
    'Eastern District of Washington SEAN F. MCAVOY, CLERK'). Cutting the merged
    line at a wide x-gap and discarding the right-hand run — the previous
    approach — also threw away real form headings that happen to sit right of
    centre ('UNITED STATES OF AMERICA JUDGMENT IN A CRIMINAL CASE' loses its
    'JUDGMENT IN A CRIMINAL CASE'). The stamps are the only non-grayscale ink
    on the sheet: pure red (1,0,0) for the clerk's stamp, pure blue (0,0,1) for
    the CM/ECF band. Removing them by colour is exact and leaves body text of
    any width untouched.
  * The removal happens in ``correct_page_geometry`` rather than in
    ``page_lines`` so the completeness audit reads the page the same way the
    extractor does — otherwise a merged stamp/text line matches neither the
    body nor the Removed box and reads as lost content.
  * the page-1 caption closes with a BOTH-SIDES horizontal rule meeting the
    mid vertical (y≈461); the generic separator scan can mistake that
    caption shelf for the footnote rule, which shoves the order's opening
    body into the footnote flow as a '?'-label footnote. The real separator
    is the classic ~144pt rule (y≈691) — caption-band rules are excluded
    via the page-1 fingerprint;
  * orders are signed with an INKED SIGNATURE IMAGE over 'DATED this …' —
    harvested to the Signature section by the shared base; the judge's name
    is pixels, so the author stays empty rather than guessed.
"""

from __future__ import annotations

from ..models import DocType
from ._district import DistrictBase

_RED = (1.0, 0.0, 0.0)
_BLUE = (0.0, 0.0, 1.0)

# An Administrative Office fill-in form ('AO 245B (Rev. 11/25) Judgment in a
# Criminal Case') prints its form number in the top-left corner of every sheet,
# with the sheet title under it. The form uses the WHOLE page — its text runs
# from y≈37 to y≈758, well outside the margins a typed ruling needs.
_AO_HEAD_BOTTOM = 62.0
_AO_MARGIN_BOTTOM = 775.0


def _ink(char) -> tuple | None:
    """The char's fill colour as a 3-tuple, or None when it is grayscale."""
    col = char.get("non_stroking_color")
    if isinstance(col, (list, tuple)) and len(col) == 3:
        return tuple(round(float(v), 3) for v in col)
    return None


class EasternDistrictOfWashington(DistrictBase):
    court_id = "waed"
    court_label = "United States District Court, Eastern District of Washington."

    # ------------------------------------------------------- page furniture
    def extract(self, pdf_path: str):
        self._red_stamp: list[str] = []
        self._blue_band: list[str] = []
        self._ao_head: list[str] = []
        self._ao_form = False
        return super().extract(pdf_path)

    # --------------------------------------------------- AO fill-in forms
    def prepare_document(self, pdf) -> None:
        """Recognise an Administrative Office fill-in form (the AO 245B
        criminal judgment) from its form-number head in the top-left corner of
        page 1. It is a different DOCUMENT STYLE from a typed ruling: a
        judgment on a printed form, with no opinion prose, and it fills the
        sheet edge to edge."""
        super().prepare_document(pdf)
        self._ao_form = False
        try:
            page = pdf.pages[0]
        except Exception:
            return
        for tl in page.extract_text_lines():
            if tl["top"] > _AO_HEAD_BOTTOM or tl["x0"] > 60:
                continue
            text = (tl.get("text") or "").strip()
            if text.startswith("AO ") and "(Rev." in text:
                self._ao_form = True
                return

    def filter_margins(self, obj):
        """An AO form's own text starts below its running head (y≈62) and runs
        to y≈758 — past the 725pt bottom margin a typed ruling wants, which was
        cutting the standard conditions of supervision off three sheets."""
        if getattr(self, "_ao_form", False):
            if obj["top"] < _AO_HEAD_BOTTOM or obj["top"] > _AO_MARGIN_BOTTOM:
                return None
            return True
        return super().filter_margins(obj)

    def page_lines(self, page):
        """Note the AO form's running head ('AO 245B (Rev. 11/25) Judgment in a
        Criminal Case Judgment -- Page 3 of 6' over 'Sheet 3 – Supervised
        Release') before the margin filter removes it, so the Removed box shows
        which sheet of the form each page is."""
        if getattr(self, "_ao_form", False):
            head = getattr(self, "_ao_head", None)
            if head is None:
                head = self._ao_head = []
            try:
                for tl in page.extract_text_lines():
                    if tl["top"] >= _AO_HEAD_BOTTOM:
                        continue
                    text = (tl.get("text") or "").strip()
                    if text and text not in head:
                        head.append(text)
            except Exception:
                pass
        return super().page_lines(page)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """An AO 245B is a JUDGMENT entered on a printed form — a signed
        disposition with no authored opinion — so it is an ORDER, not an
        opinion, however confidently the judge's signature block is read."""
        if getattr(self, "_ao_form", False):
            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def correct_page_geometry(self, page) -> None:
        """Record the two coloured stamps and take their glyphs off the page.

        Runs before any line clustering, so a stamp glyph can never be merged
        into the body line it was printed over; and because the audit reads the
        page through this hook too, the ground truth loses them as well."""
        red = getattr(self, "_red_stamp", None)
        if red is None:
            red = self._red_stamp = []
        blue = getattr(self, "_blue_band", None)
        if blue is None:
            blue = self._blue_band = []
        chars = page.chars
        if any(_ink(c) in (_RED, _BLUE) for c in chars):
            # Read the stamp's own text by clustering ONLY its glyphs, so the
            # note in the Removed box shows the stamp as it reads on the page.
            for bucket, colour in ((red, _RED), (blue, _BLUE)):
                try:
                    sub = page.filter(lambda o: _ink(o) == colour)
                    for tl in sub.extract_text_lines():
                        text = (tl.get("text") or "").strip()
                        if text and text not in bucket:
                            bucket.append(text)
                except Exception:
                    pass
            for i in range(len(chars) - 1, -1, -1):
                if _ink(chars[i]) in (_RED, _BLUE):
                    del chars[i]
        super().correct_page_geometry(page)

    def _sweep_residual(self, doc, source_pages):
        # Before the completeness sweep — it skips whatever doc.dropped already
        # renders in the Removed box.
        extra = []
        blue = getattr(self, "_blue_band", None) or []
        if blue:
            extra.append(
                "[blue CM/ECF bates header removed from every page — "
                + blue[0]
                + "]"
            )
            extra.extend(blue[1:])
        red = getattr(self, "_red_stamp", None) or []
        if red:
            extra.append(
                "[red clerk's FILED stamp removed: " + " · ".join(red) + "]"
            )
        head = getattr(self, "_ao_head", None) or []
        if head:
            extra.append("[AO form running head removed: " + head[0] + "]")
            extra.extend(head[1:])
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    # footnote separator: the caption-shelf exclusion now lives in
    # DistrictBase.find_footnote_separator (shared — wawd had the same bug).
