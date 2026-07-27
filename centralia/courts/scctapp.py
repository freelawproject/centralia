"""South Carolina Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class SouthCarolinaCourtOfAppeals(StateAppellate):
    court_id = "scctapp"
    court_label = "South Carolina Court of Appeals."

    # Body prose and block quotations can share the same line pitch.  Ask the
    # base segmenter to fence transitions into and out of a sustained indent,
    # then confirm any spacing-based "blockquote" from the segment's geometry.
    blockquote_by_indent = True

    def find_footnote_separator(self, page):
        return self.footnote_sep_fixed_left_rule(page)

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        if kind == "blockquote" and not self._is_indented_blockquote(seg):
            return "body"
        return kind

    def split_body_paragraphs(self, seg) -> list:
        """Keep separately spaced bold headings in separate blocks.

        Wrapped headings retain the ordinary line pitch and remain together;
        distinct stacked headings have a paragraph-sized vertical gap.
        """
        out = []
        for para in super().split_body_paragraphs(seg):
            current = [para[0]]
            for line in para[1:]:
                gap = line["top"] - current[-1]["top"]
                if (
                    self._line_all_bold(current[-1])
                    and self._line_all_bold(line)
                    and gap > self.gap_single_max
                ):
                    out.append(current)
                    current = [line]
                else:
                    current.append(line)
            out.append(current)
        return out

    def classify_paragraph(self, lines) -> str:
        if lines and all(self._line_all_bold(line) for line in lines):
            return "heading"
        return super().classify_paragraph(lines)

    def _begins_paragraph_block(self, lines) -> bool:
        """A bold heading at page top cannot continue the prior paragraph."""
        return bool(lines) and all(self._line_all_bold(line) for line in lines)
