"""Supreme Court of Arkansas."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class ArkansasSupreme(StateSupreme):
    court_id = "ark"
    court_label = "Supreme Court of Arkansas."
    author_titles = ("Justice", "Chief Justice", "Associate Justice")
    # Statutory and precedential quotations use a stable inset on both margins;
    # ordinary paragraphs merely indent their first line.  The shared detector
    # requires the former multi-line geometry.
    blockquote_by_indent = True

    def find_footnote_separator(self, page):
        """Do not treat the bottom edge of Arkansas's page-1 caption as a
        footnote rule.

        The open caption is drawn as two horizontal half-rules around the
        vertical column divider. The shared separator detector only sees the
        left half (the right half is outside its normal footnote x-range), so
        on short first pages it can mistake that caption edge for a footnote
        boundary and remove the author byline from the body stream.
        """
        sep = super().find_footnote_separator(page)
        if sep is None or page.page_number != 1:
            return sep
        divider = self.find_caption_divider(page)
        if divider is not None and abs(sep - divider[2]) <= 8:
            return None
        return sep

    def segment_lines(self, lines, page_width):
        """Break a segment open at a bold byline that sits inside it.

        A separate writing is announced with a BOLD byline ('SHAWN A. WOMACK,
        Justice, concurring.') that usually opens its own segment because a blank
        line precedes it. When the disposition, the vote line and the byline run
        at the same body leading ('Affirmed.' / 'WOMACK, J., concurs.' / the
        byline), they segment together — and the opinion pipeline only reads a
        byline off a segment's FIRST line, so the concurrence went undetected and
        its footnotes, numbered from 1 again, collided with the majority's and
        were lost. The bold byline is a structural boundary; make it one."""
        out = []
        for seg in super().segment_lines(lines, page_width):
            cur = [seg[0]] if seg else []
            for line in seg[1:]:
                if self._byline_split(line) is not None:
                    out.append(cur)
                    cur = [line]
                else:
                    cur.append(line)
            if cur:
                out.append(cur)
        return out

    def _has_body_between(self, all_segments, start, end) -> bool:
        """Also accept a writing whose body shares the byline's own segment.

        Arkansas runs the separate writing's first sentence inline with its
        byline ('SHAWN A. WOMACK, Justice, concurring. I agree that the circuit
        court …') and the rest of the paragraph continues in the same segment.
        The shared base looks for the body in a LATER segment; when the writing
        is the last thing on the page (counsel and footnotes aside) there is
        none, so the byline read as a sign-off and the whole concurrence was
        folded into the majority."""
        if super()._has_body_between(all_segments, start, end):
            return True
        seg = all_segments[start][1] if start < len(all_segments) else []
        if not seg:
            return False
        text = self.line_plain_text(seg[0]).strip()
        split = self._byline_split(seg[0])
        # Only a byline that names its kind ('…, concurring.') can open a
        # writing this way; a BARE signature ('BARBARA W. WEBB, Justice') with
        # no following segment stays what it is — the author signing off.
        if self._is_bare_signature(text, split):
            return False
        return len(seg) > 1 or bool(split and split[1])

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Keep styled headmatter but fold the measured open caption columns.

        This is intentionally between a flattened text dump and a literal
        facsimile: banners retain the normal review styling, while only the
        parallel parties / appeal-from zone becomes a caption card with its
        source blank-row rhythm intact.
        """
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        result["summary"] = self._fold_open_caption(
            result.get("summary") or [], headmatter_segs
        )
        return result
