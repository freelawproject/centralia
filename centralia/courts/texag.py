"""Office of the Attorney General of Texas. ('texag') — AG letter/formal opinions on the shared AG base."""

from __future__ import annotations

from ._agletter import AGLetterBase


class TexasAttorneyGeneral(AGLetterBase):
    court_id = "texag"
    court_label = "Office of the Attorney General of Texas."

    def find_footnote_separator(self, page):
        """Texas uses a fixed two-inch rule at the left text margin.

        Long notes can push that rule above the generic bottom-half cutoff
        (KP-0505 page 52), so identify the invariant rule geometry wherever it
        occurs on the page.
        """
        fixed = self.footnote_sep_fixed_left_rule(page)
        return fixed if fixed is not None else super().find_footnote_separator(page)

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # Some releases have a scanned letterhead/addressee first page with no
        # usable text layer.  The born-digital opinion then opens on page 2
        # with a bold, centered Roman section heading.  This is a structural
        # body boundary, not a filename exception.
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        for i, (pno, seg, _kind) in enumerate(all_segments):
            if pno <= 1 or not seg:
                continue
            text = " ".join(
                self.line_plain_text(line).strip() for line in seg[:2]
            ).strip()
            first = self.line_plain_text(seg[0]).strip()
            roman = first.split(".", 1)[0]
            centered = abs(
                (seg[0]["x0"] + seg[0]["x1"]) / 2 - pw / 2
            ) <= 30
            bold = all(
                bool(ch.get("bold"))
                or "bold" in str(ch.get("fontname", "")).lower()
                for ch in (seg[0].get("chars") or [])
            )
            if (
                text
                and centered
                and bold
                and roman
                and all(c in "IVXLCDM" for c in roman)
                and first[len(roman):].startswith(".")
            ):
                self._letter_start = i
                self._letter_author = self._signature_author(all_segments)
                return [i]
        return []

    def classify_paragraph(self, lines) -> str:
        if not lines:
            return "p"
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        text = " ".join(self.line_plain_text(line).strip() for line in lines)
        chars = [ch for line in lines for ch in (line.get("chars") or [])]
        bold = bool(chars) and all(
            bool(ch.get("bold"))
            or "bold" in str(ch.get("fontname", "")).lower()
            for ch in chars
            if (ch.get("text") or "").strip()
        )
        if bold and (
            len(text) <= 140
            or all(self.line_alignment(line, pw) == "C" for line in lines)
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        # A wrapped bold heading is often segmented one visual line at a time
        # because each centered line has a different indent.  Rejoin adjacent
        # all-bold heading blocks on the same page; their typography and
        # adjacency are the printed structure.
        for op in doc.opinions:
            merged = []
            for block in op.blocks:
                all_strong = (
                    block.text.startswith("<strong>")
                    and block.text.endswith("</strong>")
                )
                if block.kind == "p" and all_strong:
                    block.kind = "heading"
                if (
                    block.kind == "heading"
                    and merged
                    and merged[-1].kind == "heading"
                    and merged[-1].page == block.page
                ):
                    merged[-1].text += " " + block.text
                else:
                    merged.append(block)
            op.blocks = merged
        return doc
