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

    def _byline_split(self, line):
        # 'KERRIGAN, Judge: <body inline>' — non-bold colon byline
        text = self.line_plain_text(line).strip()
        ci = text.find(":")
        if ci > 0:
            head = text[:ci].strip()
            if self.parse_author_line(head) is not None:
                return head + ":", text[ci + 1 :].strip()
        return super()._byline_split(line)