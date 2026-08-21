"""Supreme Court of Vermont.

Byline opens the first numbered paragraph: '¶ 1. EATON, J. Seventeen Burlington
...' / '¶ 1. REIBER, C.J. This appeal ...', with the opinion text inline after
the abbreviated title. Separate writings are numbered likewise ('¶ 50.
ROBINSON, J., concurring.'). The shared abbreviated-title base handles the
'NAME, J.' grammar once the leading '¶ N.' paragraph marker is stripped (kept
in the byline text). A trial-judge line ('Robert R. Bent, J. (Ret.)') is
title-case and a 'PRESENT: Reiber, C.J., ...' panel roster is not a clean
surname — neither is an opinion start.

The court also publishes three-justice ``ENTRY ORDER`` documents.  Those have
no authored byline: a centered clerk-entry direction ends the caption, the
ruling begins in the following body-width paragraph, and a right-column
``BY THE COURT`` roster closes the document.  Treating the roster's titled
names as ordinary bylines creates phantom opinions, so entry orders use that
layout sequence as their body boundary instead.
"""

from __future__ import annotations

from ..models import DocType
from ._abbrevtitle import AbbrevTitleSupreme


class VermontSupreme(AbbrevTitleSupreme):
    court_id = "vt"
    court_label = "Supreme Court of Vermont."
    strip_para_marker = True

    def extract(self, pdf_path):
        self._vt_entry_order = False
        self._vt_entry_author_line = None
        doc = super().extract(pdf_path)
        if self._vt_entry_order:
            self._harvest_entry_order_signature(doc)
        return doc

    def page_lines(self, page):
        """Remove only centered numeric folios in the bottom margin."""
        lines = super().page_lines(page)
        kept = []
        for line in lines:
            text = self.line_plain_text(line).strip()
            if (
                line.get("top", 0) > page.height - 75
                and self._is_page_number_text(text)
                and self.line_alignment(line, page.width) == "C"
            ):
                continue
            kept.append(line)
        return kept

    @staticmethod
    def _is_entry_title(text):
        return text.strip().upper() == "ENTRY ORDER"

    @staticmethod
    def _is_clerk_entry_line(text):
        folded = " ".join(text.strip().lower().split())
        return (
            folded.startswith("in the above-entitled cause")
            and folded.endswith("the clerk will enter:")
        )

    def find_authors(self, all_segments):
        """Use the clerk-entry boundary for an unbylined ENTRY ORDER."""
        is_entry = any(
            self._is_entry_title(line.get("text") or "")
            for _page, seg, _kind in all_segments
            for line in seg
        )
        if not is_entry:
            return super().find_authors(all_segments)

        self._vt_entry_order = True
        for i, (_page, seg, _kind) in enumerate(all_segments):
            if any(
                self._is_clerk_entry_line(line.get("text") or "") for line in seg
            ):
                # In the court's layout the centered clerk direction is its own
                # segment and the first body-width paragraph follows it.
                for j in range(i + 1, len(all_segments)):
                    candidate = all_segments[j][1]
                    if not candidate:
                        continue
                    text = (candidate[0].get("text") or "").strip()
                    if text and not self._is_page_number_text(text):
                        self._vt_entry_author_line = candidate[0]
                        return [j]
                break
        return []

    def split_author_line(self, line):
        if self._vt_entry_order and line is self._vt_entry_author_line:
            # The first ruling line is body text, not a printed byline.
            return "PER CURIAM", [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if self._vt_entry_order:
            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Route the advisories to Removed: the asterisk explainer, and the
        reargument notice every slip opinion opens with ('NOTICE: This
        opinion is subject to motions for reargument under V.R.A.P. 40 ...
        Readers are requested to notify the Reporter of Decisions ...') —
        publication furniture, not caption."""
        kept, notice = [], []
        for seg in headmatter_segs:
            text = " ".join(
                (line.get("text") or "").strip() for line in seg
            ).strip()
            folded = " ".join(text.lower().split())
            # One stray leading glyph is tolerated: in_re_o.r.g. fuses an
            # artifact 'F' onto the first line ('FNOTICE: This opinion ...'),
            # the only one of 50 documents whose notice missed the prefix.
            if folded.startswith(
                ("note: in the case title, an asterisk", "notice:")
            ) or folded[1:].startswith("notice:"):
                notice.append(text)
            else:
                kept.append(seg)
        result = super().extract_headmatter(kept, page1_rules=page1_rules)
        if notice:
            result["dropped"] = list(result.get("dropped") or []) + notice
        return result

    @staticmethod
    def _harvest_entry_order_signature(doc):
        """Lift the closing court roster out of the order body."""
        if not doc.opinions:
            return
        blocks = doc.opinions[-1].blocks
        start = None
        for i, block in enumerate(blocks):
            text = str(block.text or "").strip()
            if text.upper().startswith("BY THE COURT:"):
                start = i
                break
        if start is None:
            return

        first = str(blocks[start].text or "").strip()
        prefix, marker, tail = first.partition("BY THE COURT:")
        signature = [marker]
        if tail.strip():
            signature.append(tail.strip())
        signature.extend(
            str(block.text or "").strip()
            for block in blocks[start + 1 :]
            if str(block.text or "").strip()
        )
        if prefix.strip():
            blocks[start].text = prefix.strip()
            del blocks[start + 1 :]
        else:
            del blocks[start:]
        doc.signature = signature
