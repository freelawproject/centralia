"""Supreme Court of Florida.

The byline comes in two forms: an unsigned ``PER CURIAM.`` opinion, or a signed
abbreviated-title byline with an all-caps surname (``GROSSHANS, J.`` /
``FRANCIS, J.`` / ``TANENBAUM, J., concurring.``). The abbreviated-title base
handles both — plain ``StateSupreme`` only recognized the spelled-out ``Justice``
title and PER CURIAM, so signed opinions came back with zero opinions (the body
then looked like it 'started on a later page')."""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class FloridaSupreme(AbbrevTitleSupreme):
    court_id = "fla"
    court_label = "Supreme Court of Florida."
    author_titles = ("Justice", "Chief Justice")

    # Style-preserving headmatter (the large banner, bold party names, italic
    # posture lines, section rules) — the shared 'Florida look' helper.
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    # Announcement lines that sit above the separate writings ('TANENBAUM, J.,
    # dissents with an opinion.' / 'GROSSHANS, J., concurs with an opinion.' /
    # 'TANENBAUM, J., did not participate.') are not opinion starts — the real
    # writing opens with the participle ('... dissenting.' / '... concurring.').
    @staticmethod
    def _is_announcement(text: str) -> bool:
        low = text.lower()
        return "with an opinion" in low or "did not participate" in low

    def parse_author_line(self, text):
        if self._is_announcement(text):
            return None
        return super().parse_author_line(text)

    def _byline_split(self, line):
        if self._is_announcement(self.line_plain_text(line)):
            return None
        return super()._byline_split(line)
