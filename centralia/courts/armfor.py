"""United States Court of Appeals for the Armed Forces ('armfor').

Title-first bylines ('Chief Judge OHLSON delivered the opinion of the
Court.' / 'Judge SPARKS, dissenting.') on the reversed-justice grammar
with Judge titles added.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class ArmedForcesCourt(ReversedJusticeSupreme):
    court_id = "armfor"
    court_label = "United States Court of Appeals for the Armed Forces."
    rev_titles = (
        "CHIEF JUDGE",
        "SENIOR JUDGE",
        "JUDGE",
    ) + ReversedJusticeSupreme.rev_titles


    # Every page after the first carries a two-line running head — the
    # italic case cite ('United States v. Brown, No. 25-0181/AR') and the
    # writing label ('Opinion of the Court' / 'Chief Judge OHLSON,
    # concurring in the judgment'). The label parses as a byline, so left
    # in the flow it births a phantom opinion PER PAGE. Drop the head band.
    def page_lines(self, page):
        if not hasattr(self, "_armfor_dropped"):
            self._armfor_dropped = []
        lines = super().page_lines(page)
        if page.page_number == 1:
            return lines
        kept = []
        for l in lines:
            if l.get("top", 0) < 66:
                t = self.line_plain_text(l).strip()
                if t:
                    self._armfor_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._armfor_dropped = []
        doc = super().extract(pdf_path)
        # The cover page ANNOUNCES the lead byline ('Chief Judge OHLSON
        # delivered the opinion of the Court.') above counsel; the opinion
        # restates it where the body begins — producing a doubled writing.
        # Consecutive writings with the same byline are one writing: merge
        # (cover content precedes the body in the PDF, so prepend).
        merged = []
        for op in doc.opinions:
            prev = merged[-1] if merged else None
            if (
                prev is not None
                and prev.author == op.author
                and prev.type == op.type
            ):
                op.blocks = list(prev.blocks) + list(op.blocks)
                op.footnotes = list(prev.footnotes) + list(op.footnotes)
                merged[-1] = op
                continue
            merged.append(op)
        doc.opinions = merged
        if self._armfor_dropped:
            seen, extra = set(), []
            for t in self._armfor_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # The footnote rule is drawn as a text line of underscores/dashes.
        best = None
        for line in page.extract_text_lines():
            t = (line.get("text") or "").strip()
            if (
                len(t) >= 4
                and all(c in "—–-_" for c in t)
                and line["top"] > page.height * 0.5
                and line["x0"] < page.width * 0.4
            ):
                if best is None or line["top"] < best:
                    best = line["top"]
        return best
