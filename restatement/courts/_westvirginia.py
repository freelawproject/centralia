"""Shared style for the West Virginia appellate courts (wva / wvactapp).

Both the Supreme Court of Appeals and the Intermediate Court of Appeals publish
two document shapes off the same template, handled here once:

  * a signed opinion with a reversed-title byline ('JUSTICE WOOTON delivered the
    Opinion of the Court.' / 'CHIEF JUDGE GREEAR delivered the Opinion of the
    Court.') or the bold all-caps colon form ('TRUMP, Justice:' / 'WHITE,
    Judge:'). The reversed-title base handles the verb form and inherits the
    colon form from the state-supreme base; both courts seat Justices and/or
    Judges, so 'Judge' is a valid author title; and

  * a per-curiam disposition — a 'MEMORANDUM DECISION' (the Intermediate Court's
    Rule 21 affirmance) or a clerk's 'DISMISSAL ORDER' / '... ORDER', set bold
    and centered — that carries no byline. The body opens at that bold centered
    header and is authored 'PER CURIAM'.

One layout fix shared by both: the title page carries a full-width rule between
the caption/counsel and the byline (or the centered disposition header). It sits
in the bottom half and is left-aligned, so the default footnote-separator finder
mistakes it for a footnote rule and drops everything beneath it — the byline and
counsel — and the opinion parses to nothing. It is instead found by footnote-
sized text directly under a rule (a real footnote), so the caption divider no
longer chops the opinion.
"""

from __future__ import annotations

from typing import Optional

# Both WV courts seat Justices and/or Judges, so the reversed byline may lead
# with either title ('JUSTICE WOOTON delivered ...' / 'CHIEF JUDGE GREEAR
# delivered ...'). Longest first so 'CHIEF JUDGE' wins over 'JUDGE'.
_WV_REV_TITLES = (
    "ASSOCIATE CHIEF JUSTICE",
    "VICE CHIEF JUSTICE",
    "CHIEF JUSTICE",
    "PRESIDING JUSTICE",
    "JUSTICE",
    "CHIEF JUDGE",
    "PRESIDING JUDGE",
    "JUDGE",
)


class WestVirginiaStyle:
    rev_titles = _WV_REV_TITLES

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)

    # ---------------------------------------------- per-curiam dispositions
    def extract(self, pdf_path):
        self._wv_order = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._wv_order = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        oi = self._wv_order_start(all_segments)
        if oi is not None:
            self._wv_order = oi
            return [oi]
        return []

    def _wv_order_start(self, all_segments):
        """Index of a bold, centered disposition header ('MEMORANDUM DECISION',
        'DISMISSAL ORDER', '... ORDER'), or None."""
        for i, (_p, seg, _k) in enumerate(all_segments):
            ln = seg[0]
            t = self.line_plain_text(ln).strip()
            up = t.upper()
            _size, _font, bold = self.line_meta(ln)
            if (
                bold
                and ln.get("x0", 0) > 180  # centered, not at the left margin
                and len(t) < 45
                and (up.endswith("ORDER") or up == "MEMORANDUM DECISION")
            ):
                return i
        return None

    def split_author_line(self, line):
        if getattr(self, "_wv_order", None) is not None:
            return "", [line]  # the disposition header opens the body; PER CURIAM
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_wv_order", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op
