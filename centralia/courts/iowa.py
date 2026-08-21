"""Supreme Court of Iowa.

Title-case byline ('Christensen, Chief Justice.' / 'Mansfield, Justice.'); the
shared state-supreme base handles it.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class IowaSupreme(StateSupreme):
    court_id = "iowa"
    court_label = "Supreme Court of Iowa."
    # Page numbers print as bare numbers between paragraphs — fold them into
    # page-break markers so the wrapped paragraphs rejoin.
    fold_page_numbers = True
    # Block quotes are indented on both margins and single-spaced at ~14pt —
    # below gap_tight_max, so the gap bands read them as 'notice'. Re-tag them
    # by their both-margins indent (the body is 1.5/double-spaced at ~24-28pt).
    blockquote_by_indent = True
    # Iowa's separator is a fixed ~2-inch rule (~144-155pt). Its long page-1
    # caption is bracketed by full-measure rules, and the lower one sits in the
    # bottom half — without this cap the finder takes that full-width divider
    # for the separator and shoves the disposition block into a phantom footnote.
    footnote_sep_max_width = 200.0

    def parse_author_line(self, text):
        if " ".join(text.strip().rstrip(".").split()).lower() == "per curiam":
            return "PER CURIAM", "per curiam", None
        return super().parse_author_line(text)

    def find_authors(self, all_segments) -> list:
        mixed_per_curiam = [
            index
            for index, (_page, segment, _kind) in enumerate(all_segments)
            if segment
            and " ".join(
                self.line_plain_text(segment[0]).strip().rstrip(".").split()
            ).lower() == "per curiam"
        ]
        # The title page can announce "Per curiam." before counsel; the last
        # occurrence is the actual byline immediately before opinion prose.
        if mixed_per_curiam:
            return [mixed_per_curiam[-1]]
        return super().find_authors(all_segments)

    def _order_fallback(self, all_segments) -> list:
        """An evenly divided court has no author to find.

        When the justices split 3-3 the appeal is 'affirmed by operation of law'
        under Iowa Code § 602.4107, and the court says so in an unsigned
        per-curiam disposition: below the caption's closing rule comes 'The
        court, Waterman, J., taking no part, being evenly divided, declares this
        case affirmed by operation of law.', then who would have affirmed and who
        would have reversed, then the clerk's 'Copies to:' service list.
        (``patty_a._thorington …``.) There is no byline anywhere, so the byline
        pass found nothing and all fourteen lines of the disposition stayed in
        the headmatter with ``doc_type=unknown``.

        The shared fallback anchors on a segment titled 'ORDER …', which this
        court never writes. Its template gives the boundary geometrically
        instead: the caption is a stack of CENTERED rows closed by a
        full-measure rule, and the body is the first left-aligned prose segment
        at the body rail below it. That is the same place a signed opinion puts
        its byline — which is why a signed opinion never reaches this fallback.
        """
        anchored = super()._order_fallback(all_segments)
        if anchored:
            return anchored
        start = next(
            (
                i
                for i, (_page, seg, kind) in enumerate(all_segments)
                if kind == "body"
                and min(line["x0"] for line in seg) <= self.body_baseline_x0 + 1
            ),
            None,
        )
        if start is None:
            return []
        self._order_start = start
        self._order_author = self._conformed_signature_author(all_segments)
        return [start]

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is None:
            return None
        try:
            if any(top - 2 <= sep <= bottom + 2 for _x0, top, _x1, bottom in (
                table.bbox for table in page.find_tables()
            )):
                return None
        except Exception:
            pass
        return sep
