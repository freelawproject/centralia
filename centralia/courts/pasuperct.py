"""Pennsylvania Superior Court.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.

The footnote zone is marked by a TYPED rule — a row of underscores set at
footnote size on the page's own left rail — so the separator is read from that
row's measured signature rather than from a drawn shape (see
``_footnote_sep_text``).
"""

from __future__ import annotations

from collections import Counter

from ._appellate import StateAppellate


class PennsylvaniaSuperiorCourt(StateAppellate):
    court_id = "pasuperct"
    court_label = "Pennsylvania Superior Court."

    def _footnote_sep_text(self, page):
        """The separator is TYPED, not drawn — a row of underscores set at
        footnote size on the page's own left rail.

        This court draws no rect and no vector line anywhere in its corpus, and
        it sets the notes themselves at BODY size with only the label digit
        raised, so neither a shape scan nor a type-size drop can find the zone.
        What it does print is one 44-character run of '_' at 8pt, flush on the
        rail, immediately above the notes. Measured over the whole corpus: 172
        underscore-only rows, and 171 of them are that row — 8.0pt, x0 = 72.0
        (the rail), 223.7-223.9pt wide. The single exception is
        com._v._solomon_i. page 1, a caption divider, and it differs on every
        facet at once: 12pt (the body size), 449.6pt wide, x0 = 77.4. The two
        populations do not overlap on size, width or rail, so the row's own
        signature is the evidence and no further corroboration is needed.

        The shared reader cannot use that signature. It fences the row to the
        bottom half of the page and, with no width configured, demands a raised
        label on the first line below it. Both fail here, and each failure
        costs whole footnotes:

          * the FENCE — a footnote long enough to fill the column pushes the
            row UP: com._v._holbrook_a. p7 sits at y=395.5 of 792, half a point
            above the line; p16 at 361.8; p21 at 278.9. 16 of the corpus's 172
            rows are at or above mid-page.
          * the LABEL — a zone carrying a footnote over from the previous page
            opens mid-sentence with no label at all: brown_p._v._brown_s. p4
            opens with the second half of footnote 3 (an indented block
            quotation) and only reaches footnote 4 nine lines later. 18 rows
            open that way, 15 of them with no label anywhere below.

        Measured against the size the PAGE sets most of, not a constant: the
        row has to be set below the body, which is what distinguishes it from
        the 12pt caption divider.
        """
        lines = [line for line in page.extract_text_lines() if line.get("chars")]
        if len(lines) < 2:
            return None
        sizes = [self._line_type_size(line["chars"]) for line in lines]
        body = Counter(round(size, 1) for size in sizes).most_common(1)[0][0]
        rail = self._page_text_rail(page)
        best = None
        for line, size in zip(lines, sizes):
            text = (line.get("text") or "").strip()
            if len(text) < 6 or any(ch != "_" for ch in text):
                continue
            if size > body - 1.0:
                continue
            if rail is not None and line["x0"] > rail + 4:
                continue
            if not any(other["top"] > line["top"] + 1 for other in lines):
                continue
            if best is None or line["top"] < best:
                best = line["top"]
        return best
