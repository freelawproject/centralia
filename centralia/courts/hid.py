"""United States District Court, District of Hawaii.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Hawaii's template has two quirks the base handles once nudged:

  * The document title is set INSIDE the caption's right column (bold, beside
    the party rows) rather than on its own line below the caption, so the
    opinion opens at the first body paragraph — the shared front-bounded
    heading scan already lands there.
  * Every order closes with an end-caption footer on the last page: below a
    full-width rule, the italic short case name and the bold document title
    repeated. It sits BELOW the signature, so it falls into the opinion body
    and blocks signature harvest. Lift it to the trailer, then re-harvest.
"""

from __future__ import annotations

from ._district import _JUDGE_TITLES, DistrictBase


class DistrictOfHawaii(DistrictBase):
    court_id = "hid"
    court_label = "United States District Court, District of Hawaii."

    def _is_judge_title(self, text: str) -> bool:
        low = self._untag(text).strip().rstrip(".").lower()
        return any(
            low == jt.rstrip(".") or low.endswith(" " + jt.rstrip("."))
            for jt in _JUDGE_TITLES
        )

    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        if not doc.opinions:
            return doc
        op = doc.opinions[-1]
        blocks = op.blocks
        # The signature's last line is the judge-title line; anything after it
        # is the end-caption footer (case name + repeated document title).
        title_i = next(
            (
                i
                for i in range(len(blocks) - 1, -1, -1)
                if self._is_judge_title(blocks[i].text)
            ),
            None,
        )
        if title_i is None or title_i == len(blocks) - 1:
            return doc
        footer = [
            self._untag(b.text).strip()
            for b in blocks[title_i + 1 :]
            if self._untag(b.text).strip()
        ]
        op.blocks = blocks[: title_i + 1]
        doc.trailer = list(doc.trailer) + footer
        # With the footer gone the signature is the block tail again — harvest it.
        self._harvest_signature(doc)
        # The e-signature is a two-part graphic (seal + signature strip); harvest
        # lifts only the topmost image, so sweep any signature image still left
        # at the body tail into the signature block, in reading order.
        tail_imgs = []
        while op.blocks and op.blocks[-1].kind == "image":
            tail_imgs.insert(0, {"__image__": True, **(op.blocks[-1].payload or {})})
            op.blocks = op.blocks[:-1]
        if tail_imgs:
            doc.signature = tail_imgs + list(doc.signature)
        return doc
