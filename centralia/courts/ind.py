"""Indiana Supreme Court.

Has a California-style authorship summary up top ('Opinion by Justice
Slaughter'), but the body opens with a standard byline ('Slaughter, Justice.'),
which the core pipeline detects.

The title page carries full-width decorative rules that divide the caption into
sections (parties | argued/appeal info | 'Opinion by ...'/concur). Those sit in
the bottom half of the page and are left-aligned with the body, so the default
footnote-separator finder mistakes the topmost one for a footnote rule and drops
the whole lower caption block (the 'Argued'/'Appeal from'/'Opinion by'/concur
lines) as orphaned footnotes. The separator is instead found by footnote-sized
text directly beneath the rule — a real Indiana footnote sits flush under its
rule, while a caption divider has a section gap below it — so the decorative
rules no longer chop the headmatter.
"""

from __future__ import annotations

from typing import Optional

from ._abbrevtitle import AbbrevTitleSupreme


class IndianaSupreme(AbbrevTitleSupreme):
    court_id = "ind"
    court_label = "Indiana Supreme Court."
    author_titles = ("Justice", "Chief Justice")
    # Separate writings sign 'Molter, J., concurring.' / 'Slaughter, J.,
    # dissenting.' — title-case surnames with the abbreviated title.
    allow_titlecase_name = True

    def prepare_document(self, pdf) -> None:
        """Detect PDFs whose font maps virtually every word space to NBSP.

        Shabazz contains 4,547 non-breaking-space glyphs and only seven
        ordinary spaces. Preserving those glyphs in justified HTML leaves the
        browser almost nowhere to wrap and makes the few legal break points
        expand across the line. A high document-level ratio distinguishes
        that broken encoding from occasional intentional NBSPs in other
        Indiana opinions.
        """
        super().prepare_document(pdf)
        nbsp = ordinary = 0
        for page in pdf.pages:
            for char in page.chars:
                text = char.get("text") or ""
                nbsp += text.count("\xa0")
                ordinary += text.count(" ")
        total = nbsp + ordinary
        self._normalize_dominant_nbsp = (
            nbsp >= 100 and total > 0 and nbsp / total >= 0.90
        )

    def correct_page_geometry(self, page) -> None:
        """Make a dominant NBSP encoding behave like ordinary word spaces."""
        if getattr(self, "_normalize_dominant_nbsp", False):
            for char in page.chars:
                if char.get("text") == "\xa0":
                    char["text"] = " "
        super().correct_page_geometry(page)

    @staticmethod
    def _outline_heading_start(text: str) -> bool:
        first = text.strip().split(maxsplit=1)[0] if text.strip() else ""
        return first in {
            "I.",
            "II.",
            "III.",
            "IV.",
            "V.",
            "A.",
            "B.",
            "C.",
            "D.",
            "E.",
        }

    def segment_lines(self, lines, page_width) -> list:
        """Keep tightly led wrapped outline headings in one segment."""
        segments = super().segment_lines(lines, page_width)
        out = []
        index = 0
        while index < len(segments):
            segment = segments[index]
            text = self.line_plain_text(segment[0]) if segment else ""
            if not segment or not self._outline_heading_start(text):
                out.append(segment)
                index += 1
                continue

            merged = list(segment)
            following = index + 1
            while following < len(segments):
                candidate = segments[following]
                if not candidate:
                    break
                gap = candidate[0]["top"] - merged[-1]["top"]
                candidate_text = self.line_plain_text(candidate[0])
                if (
                    not 0 < gap <= 28
                    or self._outline_heading_start(candidate_text)
                    or not all(
                        self._line_all_emphasized(line) for line in candidate
                    )
                ):
                    break
                merged.extend(candidate)
                following += 1
            out.append(merged)
            index = following
        return out

    def split_body_paragraphs(self, seg) -> list:
        """Split Indiana's shallow first-line indents from measured geometry.

        The current Indiana template sets continuation lines on the measured
        body rail (x=108) and paragraph openers only 14.4 points farther right.
        The shared 28-point threshold therefore joined every paragraph on a
        page.  Treat an offset between 2% and 8% of this document's measured
        text width as a first-line indent; deeper runs remain quotations or
        wrapped headings.
        """
        geom = getattr(self, "_doc_geom", None)
        if not seg or not geom:
            return super().split_body_paragraphs(seg)
        # A wrapped bold heading can increase its continuation indent for
        # centering.  It is one heading, not two shallow-indent paragraphs.
        if all(self._line_all_emphasized(line) for line in seg):
            return [seg]
        body_x0 = float(geom["body_x0"])
        measure = max(1.0, float(geom["right_x1"]) - body_x0)
        shallow_min = max(6.0, 0.02 * measure)
        shallow_max = max(24.0, 0.08 * measure)

        paragraphs = [[seg[0]]]
        for line in seg[1:]:
            offset = float(line["x0"]) - body_x0
            if shallow_min <= offset <= shallow_max:
                paragraphs.append([line])
            else:
                paragraphs[-1].append(line)
        paragraphs = self._explode_line_stacks(paragraphs)
        # Preserve the same measured shallow indent that proved each paragraph
        # boundary.  The base builder carries this private line annotation into
        # the block payload; only truly indented openers receive visual indent.
        for paragraph in paragraphs:
            if not paragraph:
                continue
            offset = float(paragraph[0]["x0"]) - body_x0
            if shallow_min <= offset <= shallow_max:
                paragraph[0]["_first_line_indent"] = round(offset, 1)
        return paragraphs

    def classify_paragraph(self, lines) -> str:
        """Indiana's short section headings are bold but left aligned."""
        if (
            lines
            and len(lines) <= 4
            and sum(len(self.line_plain_text(line).strip()) for line in lines) <= 220
            and all(self._line_all_emphasized(line) for line in lines)
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)

    def extract(self, pdf_path):
        self._footer_dropped = []
        doc = super().extract(pdf_path)
        self._harvest_attorney_tail(doc)
        extra = list(dict.fromkeys(self._footer_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    @staticmethod
    def _plain_tail_heading(text: str) -> str:
        """Normalize spaced/marked-up Indiana counsel headings."""
        for tag in ("<strong>", "</strong>", "<em>", "</em>"):
            text = text.replace(tag, "")
        return "".join(ch for ch in text.upper() if ch.isalpha())

    def _harvest_attorney_tail(self, doc) -> None:
        """Move the final Indiana counsel roster out of the opinion body."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        start = next(
            (
                i
                for i, block in enumerate(op.blocks)
                if (
                    "ATTORNEYFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                    or "ATTORNEYSFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                )
            ),
            None,
        )
        if start is None:
            return
        tail = op.blocks[start:]
        op.blocks = op.blocks[:start]
        doc.trailer = [
            str(block.text or "").strip()
            for block in tail
            if str(block.text or "").strip()
        ]

    def page_lines(self, page):
        lines = super().page_lines(page)
        if getattr(self, "_footer_dropped", None) is None:
            self._footer_dropped = []
        kept = []
        for ln in lines:
            t = self.line_plain_text(ln).strip()
            # Per-page footer ('Indiana Supreme Court | Case No. ... | Page
            # N of M') sits inside the text margins — furniture.
            if ln["top"] > 700 and t.startswith("Indiana Supreme Court"):
                self._footer_dropped.append(t)
                continue
            kept.append(ln)
        return kept

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        # Indiana types its per-curiam byline in title case ('Per curiam.'),
        # which the global ALL-CAPS matcher deliberately ignores.
        if " ".join(text.strip().rstrip(".").split()).lower() == "per curiam":
            return ("Per curiam", "per curiam", None)
        return None
