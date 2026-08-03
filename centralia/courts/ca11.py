"""United States Court of Appeals for the Eleventh Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class EleventhCircuit(FederalCircuitBase):
    court_id = "ca11"
    court_label = "United States Court of Appeals for the Eleventh Circuit."
    circuit_phrase = "eleventh circuit"

    # ca11 sets the opinion in a NARROW column (DanteMTPro 14pt) whose left
    # margin is x0≈126, not the federal default of 72. The baseline drives
    # indent / wrap / centering, so it must match the real column.
    body_baseline_x0 = 126.0

    # ca11's body is single-spaced at ~19pt (14pt type), not the ~1.5-spaced
    # ~27pt of a Times circuit. The inherited bands (single<22, double<32) read
    # that 19pt body as a blockquote, mislabeling nearly every paragraph. Retune
    # so 19pt lands in the body band; a genuinely tighter run is the blockquote.
    gap_tight_max = 10.0
    gap_single_max = 16.0
    gap_double_max = 30.0
    fold_page_numbers = True

    def extract(self, pdf_path):
        self._ca11_dropped_headers = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        headers = list(dict.fromkeys(getattr(self, "_ca11_dropped_headers", [])))
        if headers:
            doc.dropped = list(doc.dropped) + [
                text for text in headers if text not in doc.dropped
            ]
        super()._sweep_residual(doc, source_pages)

    def detect_printed_folio(self, page, lines):
        """Read the folio embedded at either end of the running header."""
        for line in lines:
            text = self.line_plain_text(line).strip()
            if not self._running_header_name(text):
                continue
            tokens = text.split()
            if tokens and tokens[0].isdigit():
                return tokens[0]
            elif tokens and tokens[-1].isdigit():
                return tokens[-1]
        return super().detect_printed_folio(page, lines)

    # Pages 2+ carry a running header just below the bates stamp that names the
    # current opinion and resets its page count — an alternating
    #   '24-13309 Opinion of the Court 3' / '3 Opinion of the Court 24-13309'
    #   '25-14065 LAGOA, J., Dissenting 1' / '2 ABUDU, J., Concurring 25-11375'
    # The header is both furniture (must not land in the body) AND the opinion
    # map: its name ('Opinion of the Court' / '<SURNAME>, J., Concurring|
    # Dissenting') says which opinion the page belongs to, so a change of name
    # marks a new opinion. ``_running_header_name`` parses it; the segmenter
    # uses it for boundaries and drops the line from the body.

    @staticmethod
    def _running_header_name(text: str):
        """If ``text`` is a page-2+ running header, return its opinion-name
        ('Opinion of the Court' / 'ABUDU, J., Concurring' / 'LAGOA, J.,
        Dissenting'); else None. A bare page number flanks one end and one OR
        MORE docket tokens flank the other (consolidated appeals print every
        docket, e.g. '24-11398; 25-11185'), so strip a page number off one end
        and a run of dockets off the other."""
        toks = (text or "").split()
        if len(toks) < 3:
            return None

        def is_docket(t):
            # Tolerate trailing punctuation joining consolidated dockets
            # ('24-11398;' between '24-11398' and '25-11185').
            t = t.strip(";:,.")
            return t.count("-") == 1 and all(p.isdigit() for p in t.split("-"))

        # STRICT form: a bare page number on one end and a docket run on the
        # other, flanking the name. Requiring BOTH a page number and a docket —
        # on opposite ends — rejects body lines that merely quote
        # '(Gorsuch, J., concurring)' or 'the dissenting opinion'.
        lo, hi = 0, len(toks)
        if toks[0].isdigit():            # page number leads, dockets trail
            lo += 1
            while lo < hi and is_docket(toks[hi - 1]):
                hi -= 1
            saw_docket = hi < len(toks)
        elif toks[-1].isdigit():         # dockets lead, page number trails
            hi -= 1
            while lo < hi and is_docket(toks[lo]):
                lo += 1
            saw_docket = lo > 0
        else:
            return None
        if not saw_docket or lo >= hi:
            return None
        name = " ".join(toks[lo:hi]).strip()
        low = name.lower()
        if "opinion of the court" in low or "concurring" in low or "dissenting" in low:
            return name
        return None

    def find_footnote_separator(self, page):
        """ca11's footnote hairline sits at the narrow body margin (x0≈126),
        not the federal x0≈72, so point the base detector at this column."""
        return self._sep_at(page, 122, 130)

    def classify_segment(self, seg):
        """The running header is its own one-line segment. Tag it 'notice' so it
        drops from the body (drop_notice_in_body) — and so the cross-page
        paragraph merge spans the gap and inserts a <pagenumber> marker."""
        if seg and self._running_header_name(self.line_plain_text(seg[0])):
            text = self.line_plain_text(seg[0]).strip()
            if text:
                self._ca11_dropped_headers.append(text)
            return "notice"
        return super().classify_segment(seg)

    def find_authors(self, all_segments) -> list:
        """The running header names the current opinion; a change of name marks
        a new opinion. Keep the base's first-opinion (majority) detection, then
        add a start at every header-name change, recording the judge + kind from
        the header so build_opinion can label it (ca11 bylines aren't bold and
        wrap, so the header is the reliable signal)."""
        starts = list(super().find_authors(all_segments))
        self._hdr_author = {}
        cur = None
        for i, (_pno, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            name = self._running_header_name(self.line_plain_text(seg[0]))
            if name is None:
                continue
            key = name.lower()
            if cur is None:
                cur = key  # first header = the majority ('Opinion of the Court')
                continue
            if key == cur:
                continue
            cur = key
            start = self._first_content_after(all_segments, i)
            if start is not None and start not in starts:
                self._hdr_author[start] = self._header_author_type(name)
                starts.append(start)
        return sorted(set(starts))

    def _first_content_after(self, all_segments, i):
        """Index of the first real content segment after header index ``i`` —
        skipping further header lines, blanks, and separators (the opinion's
        byline / first paragraph)."""
        for j in range(i + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            if not t or self.is_separator_line(seg[0]):
                continue
            if self._running_header_name(t):
                continue
            return j
        return None

    def _header_author_type(self, name: str):
        """(author, type) from a header opinion-name like 'ABUDU, J.,
        Concurring' / 'LAGOA, J., Dissenting'."""
        surname = name.split(",")[0].strip()
        kind = "dissenting" if "dissent" in name.lower() else "concurring"
        return f"{surname}, Circuit Judge, {kind}", self.normalize_opinion_type(kind)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        at = getattr(self, "_hdr_author", {}).get(op_start)
        if at:
            op.author, op.type = at
        return op
