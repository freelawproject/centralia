"""United States District Court, Western District of Kentucky.

KYWD uses the ordinary district-opinion layout plus two recurring structures:

* stand-alone ``ORDER ...`` rulings, which are orders even though the district
  family can find their body start and therefore otherwise calls them opinions;
* Adobe signature widgets.  Their appearance is an image inside an AcroForm
  annotation, not a page image or text object, so pdfplumber's normal page walk
  cannot see it.  The image is recovered from the widget's own appearance
  stream and surfaced in the Signature section.

The court also publishes the USDC KYWD variant of AO 245B criminal judgments.
Those are signed judgments on a form, not authored opinions, and the form uses
the page below the normal district bottom margin.
"""

from __future__ import annotations

import base64
from io import BytesIO

import pdfplumber
from pdfminer.pdftypes import PDFStream, resolve1
from PIL import Image

from ..models import DocType
from ._district import DistrictBase


_AO_HEAD_BOTTOM = 39.0
_AO_MARGIN_BOTTOM = 775.0


class WesternDistrictOfKentucky(DistrictBase):
    court_id = "kywd"
    court_label = "United States District Court, Western District of Kentucky."

    def extract(self, pdf_path: str):
        self._ao_form = False
        self._ao_heads: list[str] = []
        doc = super().extract(pdf_path)
        if doc.doc_type == DocType.ORDER:
            for opinion in doc.opinions:
                opinion.type = "order"
        self._harvest_kywd_signature(doc, pdf_path)
        return doc

    # ------------------------------------------------------- document style
    def prepare_document(self, pdf) -> None:
        super().prepare_document(pdf)
        try:
            page = pdf.pages[0]
        except Exception:
            return
        for line in page.extract_text_lines():
            if line.get("top", 0) >= _AO_HEAD_BOTTOM or line.get("x0", 0) > 60:
                continue
            text = (line.get("text") or "").strip()
            if (
                text.startswith(("USDC ", "AO "))
                and "245B" in text
                and "(Rev." in text
                and "Judgment in a Criminal Case" in text
            ):
                self._ao_form = True
                return

    def filter_margins(self, obj):
        if getattr(self, "_ao_form", False):
            if obj["top"] < _AO_HEAD_BOTTOM or obj["top"] > _AO_MARGIN_BOTTOM:
                return None
            return True
        return super().filter_margins(obj)

    def page_lines(self, page):
        if getattr(self, "_ao_form", False):
            for line in page.extract_text_lines():
                if line.get("top", 0) >= _AO_HEAD_BOTTOM:
                    continue
                text = (line.get("text") or "").strip()
                if text and text not in self._ao_heads:
                    self._ao_heads.append(text)
        return super().page_lines(page)

    def find_footnote_separator(self, page):
        # The signature/date rules on AO 245B are form rules, not footnote
        # separators.  Treating one as a separator routed "Date of Imposition
        # of Judgment" into a made-up '?' footnote.
        if getattr(self, "_ao_form", False):
            return None
        return super().find_footnote_separator(page)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_ao_form", False):
            return DocType.ORDER

        # A bare/compound ORDER title is a stand-alone order.  Deliberately do
        # not match "MEMORANDUM ... AND ORDER": KYWD uses that title for its
        # ordinary authored memorandum opinions.
        for _page, segment, _kind in all_segments[:30]:
            for line in segment:
                text = self.line_plain_text(line).strip().rstrip(":.")
                letters = "".join(ch for ch in text if ch.isalpha())
                if (
                    letters
                    and letters == letters.upper()
                    and (text == "ORDER" or text.startswith("ORDER "))
                    and len(text) <= 160
                ):
                    return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def _sweep_residual(self, doc, source_pages):
        if self._ao_heads:
            doc.dropped = list(doc.dropped) + [
                "[AO form running head removed: " + self._ao_heads[0] + "]",
                *self._ao_heads[1:],
            ]
        super()._sweep_residual(doc, source_pages)

    # ---------------------------------------------------------- signatures
    @staticmethod
    def _signature_sized(block) -> bool:
        if block.kind != "image":
            return False
        width = float(block.payload.get("width") or 0)
        height = float(block.payload.get("height") or 0)
        return 220 <= width <= 260 and 70 <= height <= 105

    def _harvest_kywd_signature(self, doc, pdf_path: str) -> None:
        """Lift KYWD's visible signature graphic out of opinion prose.

        Most files flatten the 240x90 signature widget into a page image.  A
        few retain it as an AcroForm widget; for those, recover the exact image
        bytes from the widget appearance stream.  No judge name is inferred or
        synthesized—the returned pixels are the pixels stored in the PDF.
        """
        if doc.signature:
            return

        for opinion in doc.opinions:
            for index, block in enumerate(opinion.blocks):
                if not self._signature_sized(block):
                    continue
                doc.signature = [{"__image__": True, **block.payload}]
                opinion.blocks = opinion.blocks[:index] + opinion.blocks[index + 1 :]
                return

        widget = self._widget_signature(pdf_path)
        if widget:
            doc.signature = widget

    @staticmethod
    def _widget_signature(pdf_path: str) -> list:
        """Return the image/date stored in a ``signatureButton`` widget."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in reversed(pdf.pages):
                    refs = page.page_obj.attrs.get("Annots")
                    for ref in (resolve1(refs) if refs else []) or []:
                        annot = resolve1(ref)
                        field = annot.get("T")
                        if isinstance(field, bytes):
                            field = field.decode("utf-8", "replace")
                        if field != "signatureButton":
                            continue
                        image = WesternDistrictOfKentucky._appearance_image(annot)
                        if image is None:
                            continue

                        out = [image]
                        # The adjacent dateText widget is part of the same
                        # visible sign-off but is absent from page.chars.
                        for date_ref in (resolve1(refs) if refs else []) or []:
                            date_annot = resolve1(date_ref)
                            date_field = date_annot.get("T")
                            if isinstance(date_field, bytes):
                                date_field = date_field.decode("utf-8", "replace")
                            if date_field != "dateText":
                                continue
                            value = date_annot.get("V")
                            if isinstance(value, bytes):
                                value = value.decode("utf-8", "replace")
                            if value:
                                out.append(str(value))
                            break
                        return out
        except Exception:
            return []
        return []

    @staticmethod
    def _appearance_image(annot) -> dict | None:
        try:
            appearance = resolve1(resolve1(annot["AP"])["N"])
            resources = resolve1(appearance.attrs["Resources"])
            xobjects = resolve1(resources["XObject"])
            stream = next(
                resolve1(value)
                for value in xobjects.values()
                if isinstance(resolve1(value), PDFStream)
                and str(resolve1(value).attrs.get("Subtype")) == "/'Image'"
            )
            width = int(stream.attrs["Width"])
            height = int(stream.attrs["Height"])
            image = Image.frombytes("RGB", (width, height), stream.get_data())
            smask_ref = stream.attrs.get("SMask")
            if smask_ref:
                smask = resolve1(smask_ref)
                alpha = Image.frombytes(
                    "L",
                    (int(smask.attrs["Width"]), int(smask.attrs["Height"])),
                    smask.get_data(),
                )
                image.putalpha(alpha)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            data = base64.b64encode(buffer.getvalue()).decode("ascii")
            bbox = resolve1(appearance.attrs.get("BBox")) or [0, 0, 240, 90]
            return {
                "__image__": True,
                "src": f"data:image/png;base64,{data}",
                "width": float(bbox[2]) - float(bbox[0]),
                "height": float(bbox[3]) - float(bbox[1]),
            }
        except Exception:
            return None
