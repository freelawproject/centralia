"""United States Court of International Trade.

'Slip Op. 26-46' cover, caption with an inline 'Before: Mark A. Barnett,
Chief Judge' line, a centered 'OPINION' / 'OPINION AND ORDER' heading,
then the title-case colon byline 'Barnett, Chief Judge: Plaintiff …' with
the body inline. Signed '/s/ Mark A. Barnett' at the end. Orders without
a byline fall back to the first body segment.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class CourtOfInternationalTrade(StateSupreme):
    court_id = "cit"
    court_label = "United States Court of International Trade."
    author_titles = ("Judge", "Chief Judge", "Senior Judge")
    drop_notice_in_body = False

    def _byline_split(self, line):
        # 'Barnett, Chief Judge: <body inline>' — title-case colon byline
        text = self.line_plain_text(line).strip()
        ci = text.find(":")
        if 0 < ci < 60:
            head = text[:ci].strip()
            if self.parse_author_line(head) is not None:
                return head + ":", text[ci + 1 :].strip()
        return super()._byline_split(line)

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        if out:
            return out
        for i, (_p, _seg, kind) in enumerate(all_segments):
            if kind == "body":
                return [i]
        return []

    def split_author_line(self, line):
        text = self.line_plain_text(line).strip()
        ci = text.find(":")
        if not (0 < ci < 60 and self.parse_author_line(text[:ci].strip())):
            return "", [line]  # body-fallback start (unsigned order)
        return super().split_author_line(line)