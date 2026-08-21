"""Supreme Court of Illinois.

The lead author is declared in prose: 'JUSTICE ROCHFORD delivered the judgment
of the court, with opinion.'; separate opinions open 'JUSTICE X, specially
concurring' / 'JUSTICE X, dissenting'. The body itself is paragraph-numbered
('¶ 1 ...') after an 'OPINION' heading. Treating the prose line as the opinion
start lets the core pipeline split opinions; the authorship lines remain in the
body (nothing dropped).
"""

from __future__ import annotations

from ._illinois import IllinoisStyle
from ._statesupreme import StateSupreme, is_caps_name
from ..models import DocType


class IllinoisSupreme(IllinoisStyle, StateSupreme):
    court_id = "ill"
    court_label = "Supreme Court of Illinois."
    il_body_baseline = 108.0  # '¶' marker hangs at 62.6; wrapped text at 108

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """The court's one-page case SUMMARY is a notice, not an opinion.

        Alongside each opinion the court publishes a single-page synopsis:
        '(Docket No. 130988)', the caption, 'Opinion filed November 20, 2025.',
        'Justice Overstreet delivered the judgment of the court, with opinion.',
        and two paragraphs describing what the court held. It reads like an
        opinion and names the author, but it is prose ABOUT the opinion — the
        opinion itself is filed separately (``people_v._butler`` is the summary;
        ``people_v._butler_1`` is the 29-page opinion). So no opinion body is
        the correct outcome for it, and the summary's own text is not a body to
        be found.

        Two invariants of a real Illinois opinion are missing, and both are
        typographic rather than verbal:

        * the court sets a 16pt BOLD masthead ('IN THE / SUPREME COURT / OF /
          THE STATE OF ILLINOIS') over a 12pt body, and the bold public-domain
          citation ('2025 IL 130988') above that — the summary sheet has no bold
          text anywhere and no line larger than its body;
        * the body is PARAGRAPH-NUMBERED, every paragraph opening with a '¶'
          marker hanging out at x≈62.6 — the summary has none.

        Across all 50 documents in the corpus these three summaries are the only
        ones with neither, so the absence of both is what identifies the style.
        """
        if not author_indices and n_pages == 1:
            lines = [line for _page, seg, _kind in all_segments for line in seg]
            if lines and not any(
                self.line_meta(line)[2]
                or self.line_plain_text(line).lstrip().startswith("¶")
                for line in lines
            ):
                return DocType.NOTICE
        return super().classify_document_type(
            all_segments, author_indices, n_pages
        )

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip()
        up = t.upper()
        if up.startswith("CHIEF JUSTICE "):
            title, rest = "Chief Justice", t[len("Chief Justice ") :]
        elif up.startswith("JUSTICE "):
            title, rest = "Justice", t[len("Justice ") :]
        else:
            return None
        low = rest.lower()
        if " delivered " in low:
            name, kind = rest[: low.index(" delivered")].strip(), None
        elif "," in rest:
            name, kind = rest.split(",", 1)
            name, kind = name.strip(), kind.strip()
        else:
            return None
        if not is_caps_name(name):
            return None
        return name, title, kind
