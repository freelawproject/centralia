"""Indiana Supreme Court.

Has a California-style authorship summary up top ('Opinion by Justice
Slaughter'), but the body opens with a standard byline ('Slaughter, Justice.'),
which the core pipeline detects.

The title page carries full-width decorative rules that divide the caption into
sections (parties | argued/appeal info | 'Opinion by ...'/concur). Those sit in
the bottom half of the page and are left-aligned with the body, so the default
footnote-separator finder mistakes the topmost one for a footnote rule and drops
the whole lower caption block (the 'Argued'/'Appeal from'/'Opinion by'/concur
lines) as orphaned footnotes. The separator is instead found by footnote-sized
text directly beneath the rule — a real Indiana footnote sits flush under its
rule, while a caption divider has a section gap below it — so the decorative
rules no longer chop the headmatter.
"""

from __future__ import annotations

from typing import Optional

from ._statesupreme import StateSupreme


class IndianaSupreme(StateSupreme):
    court_id = "ind"
    court_label = "Indiana Supreme Court."
    author_titles = ("Justice", "Chief Justice")

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)
