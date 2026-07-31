"""United States Navy-Marine Corps Court of Criminal Appeals. ('nmcca') — on the shared military CCA base.

Two structural quirks of the slip:

* The panel's majority signs with a spelled-out title ('HARRELL, Senior
  Judge:'), but a separate writing abbreviates it and parenthesizes the
  kind — 'McCOY, J. (dissenting):' — which the spelled-title table does
  not cover. Left unparsed the dissent is swallowed by the majority, and
  because its footnotes restart at 1 the label de-duplicator then discards
  every one of them (34 source lines lost in ``wenzel``).
* Every page after the cover carries a two-line running head: the italic
  case cite plus the writing label ('Opinion of the Court' /
  'McCoy, J. (dissenting)'). The cite falls just above the default top
  margin, but the label does not — and once the abbreviated byline parses,
  that label births a phantom dissent on every page of the dissent. The
  head is set at BODY size here, so it is identified as running furniture:
  the same text at the top of more than one sheet.
"""

from __future__ import annotations

from ._military import MilitaryCCA


class NavyMarineCCA(MilitaryCCA):
    court_id = "nmcca"
    court_label = "United States Navy-Marine Corps Court of Criminal Appeals."
    # 'McCOY, J. (dissenting):' — the abbreviated judge title. The base
    # already peels the trailing colon before matching.
    author_titles = MilitaryCCA.author_titles + ("J.",)
    head_band_max_top = 70.0

    def prepare_document(self, pdf) -> None:
        super().prepare_document(pdf)
        counts = {}
        for page in pdf.pages[1:]:
            seen = set()
            for line in page.extract_text_lines():
                if line["top"] >= self.head_band_max_top:
                    continue
                key = " ".join((line.get("text") or "").split()).lower()
                if key and key not in seen:
                    seen.add(key)
                    counts[key] = counts.get(key, 0) + 1
        self._nmcca_head_text = {k for k, n in counts.items() if n >= 2}

    def page_lines(self, page):
        """Drop the running-head band — the contiguous run of lines from the
        top of a continuation sheet whose text RECURS at the top of another
        sheet. Surfaced in ``dropped``, never silently discarded."""
        if not hasattr(self, "_nmcca_dropped"):
            self._nmcca_dropped = []
        lines = super().page_lines(page)
        if page.page_number == getattr(self, "_caption_pno", 1):
            return lines
        repeats = getattr(self, "_nmcca_head_text", set())
        kept, in_band = [], True
        for l in lines:
            if in_band and l.get("top", 0) < self.head_band_max_top:
                key = " ".join(self.line_plain_text(l).split()).lower()
                if key in repeats:
                    self._nmcca_dropped.append(self.line_plain_text(l).strip())
                    continue
            in_band = False
            kept.append(l)
        return kept

    def extract(self, pdf_path):
        self._nmcca_dropped = []
        self._nmcca_head_text = set()
        doc = super().extract(pdf_path)
        seen, extra = set(), []
        for t in self._nmcca_dropped:
            if t and t not in seen:
                seen.add(t)
                extra.append(t)
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc
