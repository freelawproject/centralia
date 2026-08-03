"""Supreme Court of South Dakota.

Byline is a plain (non-bold) ALL-CAPS surname over the full title word —
'KERN, Retired Justice' / 'SALTER, Justice' / 'JENSEN, Chief Justice' — at
the top of the opinion, above '[¶1.]'-numbered paragraphs. The cover page
carries the docket-and-disposition header ('#30782-aff in pt & rev in
pt-JMK', the authoring justice's initials trailing), the 'IN THE SUPREME
COURT / OF THE / STATE OF SOUTH DAKOTA' banner, '* * * *' rails, the parties,
the 'APPEAL FROM …' history, the trial judge, and counsel — all headmatter.
"""

from __future__ import annotations

from ..models import DocType
from ._statesupreme import StateSupreme


class SouthDakotaSupreme(StateSupreme):
    court_id = "sd"
    court_label = "Supreme Court of South Dakota."

    def extract(self, pdf_path):
        self._sd_footer = []
        self._sd_header = []
        self._sd_advisory = False
        doc = super().extract(pdf_path)
        if self._sd_advisory and doc.opinions:
            blocks = doc.opinions[0].blocks
            if (
                len(blocks) >= 2
                and "AN OPINION REQUESTED BY " in blocks[0].text
                and "SOUTH DAKOTA CONSTITUTION" in blocks[1].text
            ):
                blocks[0].kind = "heading"
                blocks[0].text = blocks[0].text + " " + blocks[1].text
                del blocks[1]
        doc.dropped = _dedupe(
            list(doc.dropped) + list(self._sd_header) + list(self._sd_footer)
        )
        return doc

    def correct_page_geometry(self, page) -> None:
        """Strip Word's INVISIBLE footnote-anchor ghost.

        Some of the Court's opinions are typeset in Cambria via Word, which
        writes a sub-visible (~1pt) '0F' pair beside the real superscript
        footnote mark. It sits on its own baseline, so the line rebuild folds it
        into the body row ('a hypoxic brain injury0F1 from the administration')
        and every anchored sentence stopped matching its printed form. Drop the
        sub-visible chars from the page's object cache so the extractor and the
        audit (which reads through this same hook) both see the real superscript
        only."""
        super().correct_page_geometry(page)
        try:
            objs = page.objects.get("char")
        except Exception:
            objs = None
        if objs:
            objs[:] = [c for c in objs if (c.get("size") or 9.0) > 1.5]

    def page_lines(self, page):
        """Remove and surface SD's running docket/header and filing stamp.

        ``#30723`` is printed at the upper-left of every opinion page.  It is
        neither a paragraph nor part of a page-break continuation; leaving it
        in the line stream fused it into prose immediately after the generated
        page marker.  The centered copy inside the cover caption sits much
        lower and remains content.
        """
        for ln in page.extract_text_lines():
            if ln.get("top", 0) <= self.margin_bottom:
                continue
            text = (ln.get("text") or "").strip()
            if text and not self._is_page_number_text(text):
                self._sd_footer.append(text)
        lines = super().page_lines(page)
        kept = []
        for line in lines:
            text = self.line_plain_text(line).strip()
            if (
                line.get("top", 0) < 65
                and text.startswith("#")
                and text[1:].isdigit()
            ):
                self._sd_header.append(text)
                continue
            kept.append(line)
        return kept

    # ------------------------------------------------------ opinion structure
    @staticmethod
    def _paragraph_number(line) -> bool:
        text = (line.get("text") or "").strip()
        if not text.startswith("[¶"):
            return False
        close = text.find(".]")
        return close > 2 and text[2:close].isdigit()

    def split_body_paragraphs(self, segment) -> list:
        """Every ``[¶N.]`` line opens a paragraph, at any page or depth."""
        out = []
        for paragraph in super().split_body_paragraphs(segment):
            current = []
            for line in paragraph:
                if current and self._paragraph_number(line):
                    out.append(current)
                    current = []
                current.append(line)
            if current:
                out.append(current)
        return out

    def _begins_paragraph_block(self, lines) -> bool:
        return bool(lines and self._paragraph_number(lines[0]))

    def _issue_heading_start(self, line) -> bool:
        text = self.line_plain_text(line).strip()
        first = text.split(maxsplit=1)[0] if text else ""
        return bool(
            first.endswith(".")
            and first[:-1].isdigit()
            and line.get("x0", 0) >= self.body_baseline_x0 + 50
            and self._line_all_emphasized(line)
        )

    def segment_lines(self, lines, page_width) -> list:
        """Keep a tightly-led, wrapped numbered issue title in one segment."""
        segments = super().segment_lines(lines, page_width)
        out = []
        i = 0
        while i < len(segments):
            segment = segments[i]
            if not segment or not self._issue_heading_start(segment[0]):
                out.append(segment)
                i += 1
                continue
            merged = list(segment)
            j = i + 1
            while j < len(segments):
                candidate = segments[j]
                if not candidate:
                    break
                gap = candidate[0]["top"] - merged[-1]["top"]
                if (
                    not 0 < gap <= 18
                    or candidate[0].get("x0", 0) < self.body_baseline_x0 + 50
                    or not all(self._line_all_emphasized(line) for line in candidate)
                ):
                    break
                merged.extend(candidate)
                j += 1
            for line in merged:
                line["_sd_issue_heading"] = True
            out.append(merged)
            i = j
        return out

    def classify_segment(self, segment) -> str:
        if segment and all(line.get("_sd_issue_heading") for line in segment):
            return "single"
        text = self.line_plain_text(segment[0]).strip() if segment else ""
        if text.startswith("AN OPINION REQUESTED BY "):
            return "single"
        return super().classify_segment(segment)

    def classify_paragraph(self, lines) -> str:
        if lines and (
            all(line.get("_sd_issue_heading") for line in lines)
            or self.line_plain_text(lines[0]).strip().startswith(
                "AN OPINION REQUESTED BY "
            )
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def find_authors(self, all_segments) -> list:
        found = super().find_authors(all_segments)
        if found:
            return found
        for index, (_page, segment, _kind) in enumerate(all_segments):
            if segment and self.line_plain_text(segment[0]).strip().startswith(
                "AN OPINION REQUESTED BY "
            ):
                self._sd_advisory = True
                return [index]
        return []

    def split_author_line(self, line):
        if self.line_plain_text(line).strip().startswith("AN OPINION REQUESTED BY "):
            return "", [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_sd_advisory", False):
            return DocType.OPINION
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # ------------------------------------------------------------- footnotes
    def detect_footnote_label(self, line):
        """South Dakota numbers its footnotes '1.', '2.', … set at BODY size and
        flush with the footnote block's left edge, not as a raised superscript —
        so the base 'smaller char' test cannot see them and every footnote on the
        page came back labelled '?', which merged the whole document's footnotes
        into one. A hanging number-dot at the block's left margin is the label;
        continuation lines are indented a step further in and cannot match."""
        if line.get("x0", 999) > self.body_baseline_x0 + 2:
            return super().detect_footnote_label(line)
        toks = (line.get("text") or "").split()
        if toks and toks[0].endswith(".") and toks[0][:-1].isdigit():
            return toks[0][:-1]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the hanging 'N.' marker off the footnote text — it is the label,
        which the renderer draws in its own column."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label.isdigit():
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            if stripped.startswith(label + "."):
                fn.paragraphs[0] = (tag, stripped[len(label) + 1 :].lstrip())
        return fn

    def _sweep_residual(self, doc, source_pages):
        # The sweep runs inside super().extract(), so the stamp has to reach
        # doc.dropped before it, not after.
        headers = [t for t in getattr(self, "_sd_header", None) or [] if t]
        stamps = [t for t in getattr(self, "_sd_footer", None) or [] if t]
        if headers or stamps:
            doc.dropped = _dedupe(list(doc.dropped) + headers + stamps)
        super()._sweep_residual(doc, source_pages)


def _dedupe(rows):
    """Order-preserving de-duplication tolerant of unhashable rows."""
    seen, out = set(), []
    for r in rows:
        try:
            if r in seen:
                continue
            seen.add(r)
        except TypeError:  # image/dict rows are never repeated
            pass
        out.append(r)
    return out
