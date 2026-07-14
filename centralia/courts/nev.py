"""Supreme Court of the State of Nevada.

Byline leads with a 'By the Court,' tag, then an abbreviated-title surname and a
colon: 'By the Court, BELL, J.:' / 'By the Court, STIGLICH, J.:'. Strip the tag
and the rest is the abbreviated-title colon form the shared base handles. A
'Jennifer Schwartz, Judge.' line is the trial judge (title-case name) and a
'HERNDON, C.J., and STIGLICH ... ' line is a panel roster — neither is the
opinion author.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

_TAG = "By the Court, "


class NevadaSupreme(AbbrevTitleSupreme):
    court_id = "nev"
    court_label = "Supreme Court of the State of Nevada."

    def is_non_digital(self, pdf) -> bool:
        """Nevada slips print born-digital Times text OVER a full-page
        letterhead raster, so image cover alone misreads them as scans. A
        real scan in this corpus has NO text layer at all — require that."""
        if not super().is_non_digital(pdf):
            return False
        chars = sum(len(pg.chars) for pg in pdf.pages[:3])
        return chars < 100

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if not text.startswith(_TAG):
            return super()._byline_split(line)
        r = self._abbrev_parse(text[len(_TAG) :])
        if r is None:
            return None
        _name, _title, _kind, end = r
        # Keep the 'By the Court,' tag in the byline text (completeness — it
        # must still appear in the output); parse_author_line strips it for the
        # name/kind.
        full_end = len(_TAG) + end
        return text[:full_end], text[full_end:].lstrip(" —–")

    def parse_author_line(self, text):
        t = text.strip()
        if t.startswith(_TAG):
            t = t[len(_TAG) :]
        return super().parse_author_line(t)
