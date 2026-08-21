"""United States Tax Court.

'T.C. Memo. 2026-41' cover, centered caption, a 'MEMORANDUM FINDINGS OF
FACT AND OPINION' (or 'MEMORANDUM OPINION') heading, then the colon byline
'KERRIGAN, Judge: The Petition in this case was filed …' with the body
inline. The shared state-supreme grammar handles the byline once the colon
form is admitted.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class USTaxCourt(StateSupreme):
    court_id = "tax"
    court_label = "United States Tax Court."
    author_titles = ("Judge", "Chief Judge", "Special Trial Judge")
    # the body is single-spaced — keep tight segments in the body
    drop_notice_in_body = False

    # The reporter star page is printed as '[*14]' at the head of each page.
    _STAR_OPEN = "[*"
    _STAR_CLOSE = "]"

    def page_lines(self, page) -> list:
        """Keep the reporter's star-page marker off a row it does not belong to.

        Every page after the first opens with the star page ('[*14]'). Where a
        page opens with PROSE the marker leads that line and reads as part of
        it, but where a page opens with a HEADING or a TABLE it stands alone in
        the left margin, half a line above the first row's baseline and a whole
        column away from it. The line builder's interleave merge — which exists
        to reunite an italic run with its host row — reads the two as one visual
        row and hands back '[*14] Increase Determined': a row whose halves
        belong to different destinations, the marker to the page's own
        pagination and the header to the table's cell. Neither could hold the
        pair, so the row came out as unplaced content (scott_l._reed page 14),
        and on a heading page the marker also displaced the heading's centring.

        Split it back into the two rows the page prints, each free to land where
        it belongs. Only a marker separated from the rest of the row by a full
        column gap is split, so the ordinary inline marker is untouched."""
        out = []
        for line in super().page_lines(page):
            out.extend(self._split_star_marker_row(line))
        return out

    def _split_star_marker_row(self, line) -> list:
        """``[marker row, rest of row]``, or ``[line]`` if they are one row."""
        chars = [c for c in (line.get("chars") or []) if (c.get("text") or "").strip()]
        if len(chars) < 2:
            return [line]
        # The marker's own glyph run: '[', '*', digits, ']'.
        closes = [
            i for i, c in enumerate(chars) if (c.get("text") or "") == self._STAR_CLOSE
        ]
        if not closes:
            return [line]
        end = closes[0]
        marker = "".join((c.get("text") or "") for c in chars[: end + 1])
        if not (
            marker.startswith(self._STAR_OPEN)
            and marker.endswith(self._STAR_CLOSE)
            and marker[len(self._STAR_OPEN) : -1].isdigit()
        ):
            return [line]
        if end + 1 >= len(chars):
            return [line]  # the marker is already a row of its own
        # A column gap, not a word space: measured against the marker's own
        # glyph width so it scales with the type size.
        glyph = max(
            (c["x1"] - c["x0"] for c in chars[: end + 1] if c["x1"] > c["x0"]),
            default=6.0,
        )
        if chars[end + 1]["x0"] - chars[end]["x1"] < glyph * 4:
            return [line]
        return [
            self._line_from_chars(line, chars[: end + 1]),
            self._line_from_chars(line, chars[end + 1 :]),
        ]

    @staticmethod
    def _line_from_chars(line, chars) -> dict:
        out = dict(line)
        out["chars"] = chars
        out["text"] = "".join((c.get("text") or "") for c in chars)
        out["x0"] = min(c["x0"] for c in chars)
        out["x1"] = max(c["x1"] for c in chars)
        out["top"] = min(c["top"] for c in chars)
        out["bottom"] = max(c["bottom"] for c in chars)
        return out

    def _byline_split(self, line):
        # 'KERRIGAN, Judge: <body inline>' — non-bold colon byline
        text = self.line_plain_text(line).strip()
        ci = text.find(":")
        if ci > 0:
            head = text[:ci].strip()
            if self.parse_author_line(head) is not None:
                return head + ":", text[ci + 1 :].strip()
        return super()._byline_split(line)