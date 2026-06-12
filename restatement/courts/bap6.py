"""Bankruptcy Appellate Panel of the Sixth Circuit.

'NOT RECOMMENDED FOR PUBLICATION' + 'File Name:' cover lines, a
box-drawing caption (┐ │ ┘ glyphs), 'Appeal from …', the panel roster
('Before: BAUKNIGHT, Chief Judge; GREGG, and MASHBURN, Bankruptcy
Appellate Panel Judges.'), a COUNSEL block, then a centered 'OPINION'
heading and the byline with the body inline: 'JOHN T. GREGG, Bankruptcy
Appellate Panel Judge. Doug Woods, the appellant …'.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_TITLES = (
    "Chief Bankruptcy Appellate Panel Judge",
    "Bankruptcy Appellate Panel Judge",
    "Circuit Judge",  # direct-appeal Sixth Circuit opinions in the corpus
    "Chief Judge",
    "Judge",
)


class SixthCircuitBAP(StateSupreme):
    court_id = "bap6"
    court_label = "Bankruptcy Appellate Panel of the Sixth Circuit."
    author_titles = _TITLES
    drop_notice_in_body = False

    def _byline_split(self, line):
        # 'JOHN T. GREGG, Bankruptcy Appellate Panel Judge. <body inline>'
        # — non-bold, period-terminated byline with the body following on
        # the same line. The panel roster ('Before: …; …, and …') never
        # matches: it starts with 'Before:' and names several judges.
        text = self.line_plain_text(line).strip()
        if text.startswith("Before"):
            return None
        for t in _TITLES:
            key = ", " + t + "."
            ki = text.find(key)
            if 0 < ki < 40:
                head = text[: ki + len(key) - 1]
                if self.parse_author_line(head) is not None:
                    return head + ".", text[ki + len(key) :].strip()
        if text.upper().startswith("PER CURIAM"):
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            if i == -1:
                return text, ""
            return text[: i + 1], text[i + 1 :].strip()
        return super()._byline_split(line)