"""Oregon Court of Appeals.

Intermediate appellate court in the same Oregon Reports layout as the Supreme
Court (narrow page, NewCenturySchlbk body, star + numbered footnotes — shared via
``OregonReports``). Author byline at the opinion start ('NAME, J.' / 'PER
CURIAM'); the appellate base reuses the abbreviated-title parser and drops the
trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._oregon import OregonReports


class OregonCourtOfAppeals(OregonReports, StateAppellate):
    court_id = "orctapp"
    court_label = "Oregon Court of Appeals."

    # The opinion opens with a BOLD byline ('TOOKEY, P. J.'). The roman
    # look-alikes above it — the trial judge appealed from ('Jay A. McAlpin,
    # Judge.') and the one-line disposition summary signed 'TOOKEY, P. J.' —
    # are headmatter, not opinion starts. ``require_bold_byline`` gates both the
    # byline split and (in the appellate base's ``find_authors``) detection, so
    # only the bold byline registers as an opinion start.
    require_bold_byline = True

    def find_authors(self, all_segments) -> list:
        """A nonprecedential memorandum sets its byline in ROMAN.

        ``require_bold_byline`` is there because the reporter prints a roman
        look-alike above the real byline — the trial judge appealed from, and the
        one-line disposition summary signed 'TOOKEY, P. J.' — and only the bold
        byline opens the opinion.

        A nonprecedential memorandum opinion has no bold byline to find. It IS
        the disposition summary: under the 'This is a nonprecedential memorandum
        opinion pursuant to ORAP 10.30' banner come the caption, counsel, the
        panel, a roman 'PER CURIAM', and a two-line holding — 'Reversed. Lopez v.
        Oregon State Hospital, 342 Or App 190, 196-99, 575 P3d 1061 (2025).' —
        and that is the whole document. With the bold gate on, nothing authored
        ``leckenby_v._oregon_state_hospital`` and it came out
        ``doc_type=unknown`` with its holding in the headmatter.

        Dropping the gate wholesale is wrong: the roman look-alikes are still
        there, and the FIRST of them is the trial judge ('Rebecca D. Guptill,
        Judge.'), so the memorandum's opinion opened on the counsel block under
        the wrong author. Only a roman PER CURIAM is admitted, and only when the
        bold search came up empty — a per curiam names no judge to mistake, and
        it sits below counsel and the panel where the writing really begins.
        """
        found = super().find_authors(all_segments)
        if found:
            return found
        return [
            i
            for i, (_page, seg, _kind) in enumerate(all_segments)
            if seg and self._is_per_curiam_line(seg[0])
        ][:1]

    def _is_per_curiam_line(self, line) -> bool:
        text = " ".join(self.line_plain_text(line).split()).rstrip(".").upper()
        return text == "PER CURIAM"

    def extract(self, pdf_path):
        self._or_running_head = []
        doc = super().extract(pdf_path)
        self._apply_or_facets(doc, pdf_path)
        doc.dropped = _dedupe(list(doc.dropped) + list(self._or_running_head))
        return doc

    def page_lines(self, page):
        """Record the reporter running head before the margin filter discards it.

        Every Oregon Reports page prints one running-head line above the body
        margin: the opening folio row ('608 July 22, 2026 No. 688'), the
        even-page citation ('Cite as 351 Or App 608 (2026) 609') or the odd-page
        short caption ('610 Dean v. Multnomah County'). ``margin_top`` drops the
        band but nothing recorded it, so a short opinion — where the citation
        form recurs on only two pages, under the sweep's
        repeated-in-the-margin threshold — reported its own running head as
        unplaced content. Capture it here and surface it in the Removed box."""
        for ln in page.extract_text_lines():
            if ln.get("top", 0) < self.margin_top:
                text = (ln.get("text") or "").strip()
                if text:
                    self._or_running_head.append(text)
        return super().page_lines(page)

    def _sweep_residual(self, doc, source_pages):
        # The sweep runs inside super().extract(), so the running head has to
        # reach doc.dropped before it, not after.
        head = [t for t in getattr(self, "_or_running_head", None) or [] if t]
        if head:
            doc.dropped = _dedupe(list(doc.dropped) + head)
        super()._sweep_residual(doc, source_pages)


def _dedupe(rows):
    """Order-preserving de-duplication tolerant of unhashable rows."""
    seen, out = set(), []
    for r in rows:
        try:
            if r in seen:
                continue
            seen.add(r)
        except TypeError:  # image/dict rows are never repeated
            pass
        out.append(r)
    return out
