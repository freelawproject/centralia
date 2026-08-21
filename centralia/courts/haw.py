"""Supreme Court of the State of Hawaiʻi.

Byline is an opinion-of-the-court heading: 'OPINION OF THE COURT BY GINOZA, J.'
/ 'CONCURRING OPINION BY X, J.' / 'DISSENTING OPINION BY X, J.'; a disposition
is an 'ORDER ...' header with a '(By: <panel>)' line (per curiam). The shared
HawaiiStyle restricts the author search to those forms and drops the 'FOR
PUBLICATION ...' banner and the red electronic-filing stamp.
"""

from __future__ import annotations

from collections import Counter

from ._hawaii import HawaiiStyle
from ._statesupreme import StateSupreme


class HawaiiSupreme(HawaiiStyle, StateSupreme):
    court_id = "haw"
    court_label = "Supreme Court of the State of Hawaiʻi."

    def page_lines(self, page):
        """Flag the text rows the court UNDERLINES with a drawn rule.

        Hawaiʻi rules its disposition title — 'ORDER REJECTING APPLICATION FOR
        WRIT OF CERTIORARI' — with a line drawn under the row (in strips, so
        span is measured rather than trusting any one strip). Nothing else in the
        caption is drawn: the court banner and the party block are divided by
        rows of TYPED underscores instead. Mark the row on the line itself, where
        the page is still in hand, so the segmenter and the author search can
        both read it.

        The rule sits at the BASELINE, inside the row's own box — 425.8 on a row
        spanning 417.4 to 431.2, because the title's footnote mark stretches the
        box down. So an underline is a rule below the row's midline and no
        further than a hair past its bottom; anything lower belongs to the row
        beneath, and the footnote separator (686.5, well clear of every row) is
        never in reach.
        """
        lines = super().page_lines(page)
        rules = [
            r
            for r in list(page.rects) + list(page.lines)
            if (r["x1"] - r["x0"]) > 30 and (r["bottom"] - r["top"]) < 3
        ]
        for line in lines:
            midline = (line["top"] + line["bottom"]) / 2
            if any(midline < r["top"] <= line["bottom"] + 4 for r in rules):
                line["_haw_ruled_title"] = self._is_title_row(line)
        return lines

    def _is_title_row(self, line) -> bool:
        """A ruled row is a TITLE row only if it is set in capitals.

        The other rule this court draws is the footnote separator, and on a full
        page the last body line can sit within an underline's reach of it. A
        title is upper-case throughout; body prose is not, so the case of the
        row keeps the two apart without measuring the page's footnote zone
        twice.
        """
        text = self.line_plain_text(line)
        letters = [c for c in text if c.isalpha()]
        return bool(letters) and all(c.isupper() for c in letters)

    def _byline_at(self, line) -> bool:
        # An underlined all-caps title opens a writing here even when the title
        # grammar cannot read it (see ``find_authors``), so it has to become a
        # segment of its own — otherwise it stays buried in the caption block.
        return bool(line.get("_haw_ruled_title")) or super()._byline_at(line)

    def split_author_line(self, line):
        # Keep the ruled title as the opening body line, exactly as the shared
        # style keeps a recognised 'ORDER …' header: the disposition's own title
        # is content, and the author it carries is the panel, not a name.
        if line.get("_haw_ruled_title"):
            return "", [line]
        return super().split_author_line(line)

    def find_authors(self, all_segments) -> list:
        """Fall back to the UNDERLINE when the order title is qualified.

        ``HawaiiStyle`` recognises a disposition from its title ('ORDER …' /
        '… ORDER' / 'SUMMARY DISPOSITION ORDER') plus the '(By: <panel>)'
        roster beneath it. An AMENDED order breaks the title test:
        ``pacific_hawaii_food_service_llc_v._yang`` heads its disposition
        'AMENDED¹ ORDER REJECTING APPLICATION FOR WRIT OF CERTIORARI' — the
        qualifier, with its footnote mark glued to it, comes first — so nothing
        authored the document, its order and its five conformed signatures
        stayed in the headmatter and it came out ``doc_type=unknown``.

        The court's own typography still marks the row: it is underlined and the
        panel roster follows it. Consulted only when the title grammar found no
        writing at all, so a document the shared rules already read is never
        re-anchored.
        """
        found = super().find_authors(all_segments)
        if found:
            return found
        for i, (_page_no, seg, _kind) in enumerate(all_segments):
            if not seg or not seg[0].get("_haw_ruled_title"):
                continue
            if not self._by_panel_near(all_segments, i):
                continue
            self._haw_order.add(i)
            return [i]
        return []

    def correct_page_geometry(self, page) -> None:
        """Put the ʻokina back on its own text row.

        Hawaiʻi's word processor sets the body in Courier but draws the ʻokina
        in ``HAWAIʻI`` / ``Toʻotoʻo`` / ``Kauaʻi`` from a substituted Times
        face whose declared bounding box sits ~4.5pt ABOVE the Courier row it
        belongs to, even though its text matrix carries the correct baseline.
        pdfplumber therefore emits the accent as a standalone line ('ʻ ʻ') and
        the caption/body line beside it reads 'HAWAI I'.

        The extractor's own baseline merge repairs its copy, but the
        completeness audit clusters the raw page itself — so the two disagreed
        and every ʻokina-bearing line (a caption banner, a party row, a
        citation, a conformed signature) reported as unplaced content.

        Fix it at the source, where both readers see it. A glyph's true row is
        given by the page's majority row constant (``top + matrix[5]`` is
        invariant per row for a correctly boxed font); a candidate is only
        moved when the corrected top lands on a row the page already draws
        text on, which is what proves the displacement is a boxing error
        rather than a genuinely separate line (the red e-filing stamp is also
        off-constant, but it occupies rows of its own and so is left alone).
        """
        super().correct_page_geometry(page)
        chars = page.chars
        if not chars:
            return
        # Row constant per (size, font); the page's body font supplies the
        # correct one for its size.
        counts: Counter = Counter()
        for c in chars:
            m = c.get("matrix")
            if m:
                counts[(round(c["size"], 1), round(c["top"] + m[5], 2))] += 1
        if not counts:
            return
        majority = {}
        for (size, const), n in counts.most_common():
            majority.setdefault(size, (const, n))

        for c in chars:
            m = c.get("matrix")
            if not m:
                continue
            size = round(c["size"], 1)
            ref = majority.get(size)
            if ref is None:
                continue
            const, n = ref
            if n < 20:  # too little text at this size to trust the row constant
                continue
            delta = (c["top"] + m[5]) - const
            if not 1.0 < abs(delta) < 8.0:
                continue
            new_top = c["top"] - delta
            # Only snap onto a row the page already sets text on.
            if any(
                abs(o["top"] - new_top) <= 0.5
                and abs((o.get("matrix") or (0,) * 6)[5] + o["top"] - const) < 0.5
                for o in chars
                if o is not c
            ):
                c["top"] = new_top
                c["y0"] = c["y0"] + delta
                c["y1"] = c["y1"] + delta
                c["doctop"] = c.get("doctop", new_top) - delta

    def _sweep_residual(self, doc, source_pages) -> None:
        """``HawaiiStyle`` collects the red electronic-filing stamp while
        reading the pages and appends it to ``dropped`` *after* ``extract()``
        returns — but the completeness sweep runs inside that call, so the
        stamp was still unplaced when the sweep looked. Flush it first."""
        pending = getattr(self, "_haw_dropped", None)
        if pending:
            seen, uniq = set(doc.dropped), []
            for t in pending:
                if t and t not in seen:
                    seen.add(t)
                    uniq.append(t)
            if uniq:
                doc.dropped = list(doc.dropped) + uniq
            self._haw_dropped = []
        super()._sweep_residual(doc, source_pages)
