"""Supreme Court of Maryland.

The author is named in the caption, not at the body: 'Opinion by Fader, C.J.'
/ 'Dissenting Opinion by Biran, J.' / 'Concurring Opinion by Gould, J.'
(title-case surname, abbreviated title). The opinion text follows. A 'Biran
and Gould, JJ., dissent.' line is a dissent-vote roster (its name is not a
clean surname) and the bold topical syllabus that precedes the opinion has no
byline — neither is an opinion start.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

# Longest-first so the compound prefixes win over the bare 'Opinion by'.
_PREFIXES = (
    ("Concurring and Dissenting Opinion by", "concurring and dissenting"),
    ("Concurring Opinion by", "concurring"),
    ("Dissenting Opinion by", "dissenting"),
    ("Opinion by", None),
)


class MarylandSupreme(AbbrevTitleSupreme):
    court_id = "md"
    court_label = "Supreme Court of Maryland."
    allow_titlecase_name = True

    def _md_strip(self, text: str):
        for prefix, kind in _PREFIXES:
            if text.startswith(prefix):
                return text[len(prefix) :].strip(), kind
        return None, None

    def parse_author_line(self, text):
        rest, kind = self._md_strip(text.strip())
        if rest is not None:
            r = self._abbrev_parse(rest)
            if r is not None:
                return r[0], r[1], (kind or r[2])
        # Deliberately NO fall-through to the bare abbreviated-title parser: a
        # 'Fader, C.J.' coram listing or a 'Killough' signature is not an
        # opinion byline here — only the caption's 'Opinion by ...' line is.
        return None

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        rest, _kind = self._md_strip(text)
        if rest is not None:
            return (text, "") if self._abbrev_parse(rest) is not None else None
        if text.upper().startswith("PER CURIAM"):
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        return None
