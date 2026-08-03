"""Tax Court of New Jersey.

A 'NOT FOR PUBLICATION WITHOUT APPROVAL OF THE TAX COURT COMMITTEE ON
OPINIONS' notice tops page 1 (dropped + surfaced). The caption is a
':'-rail pleading box capped with a dashed '------x' rule; the right
column carries 'TAX COURT OF NEW JERSEY / DOCKET NO / OPINION'. The
byline is the abbreviated title 'CIMINO, J.T.C.' below the caption.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class NewJerseyTaxCourt(AbbrevTitleSupreme):
    court_id = "njtaxct"
    court_label = "Tax Court of New Jersey."
    abbrev_titles = (
        ("P.J.T.C.", "Presiding Judge of the Tax Court"),
        ("J.T.C.", "Judge of the Tax Court"),
    ) + AbbrevTitleSupreme.abbrev_titles

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is None:
            return None
        try:
            if any(top - 2 <= sep <= bottom + 2 for _x0, top, _x1, bottom in (
                table.bbox for table in page.find_tables()
            )):
                return None
        except Exception:
            pass
        return sep

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        if out:
            return out
        # LETTER opinions: the judge is the letterhead ('MALA SUNDAR /
        # PRESIDING JUDGE', the address column merged onto the same rows);
        # the ruling reads as a letter to counsel ('Dear …:').
        self._njtax_letter_author = None
        head = []
        for _p, seg, _k in all_segments[:8]:
            for l in seg:
                head.append(self.line_plain_text(l).strip())
        for i, t in enumerate(head[:14]):
            first = t.split()
            if not first:
                continue
            lead = " ".join(first[:2]).rstrip(":").upper()
            if lead.startswith(("JUDGE", "PRESIDING JUDGE")) and i > 0:
                # leading ALL-CAPS run of the line above = the name
                name = []
                for tok in head[i - 1].split():
                    core = tok.strip(".,")
                    if core and core.isupper() and (
                        core.isalpha() or len(core) <= 2
                    ):
                        name.append(tok.rstrip(","))
                    else:
                        break
                if len(name) >= 2:
                    self._njtax_letter_author = " ".join(name).title()
                    break
        start = None
        for i, (_p, seg, kind) in enumerate(all_segments):
            if seg and self.line_plain_text(seg[0]).strip().startswith("Dear "):
                start = i
                break
        if start is None:
            for i, (_p, _seg, kind) in enumerate(all_segments):
                if kind == "body":
                    start = i
                    break
        return [start] if start is not None else []

    def split_author_line(self, line):
        a = getattr(self, "_njtax_letter_author", None)
        if a:
            return a, [line]
        return super().split_author_line(line)

    def page_lines(self, page):
        if not hasattr(self, "_njtax_dropped"):
            self._njtax_dropped = []
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) < 100 and (
                t.upper().startswith("NOT FOR PUBLICATION")
                or t.upper().startswith("THE TAX COURT COMMITTEE")
            ):
                self._njtax_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._njtax_dropped = []
        doc = super().extract(pdf_path)
        if self._njtax_dropped:
            seen, extra = set(), []
            for t in self._njtax_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc
