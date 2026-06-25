"""Delaware Court of Chancery ('delch').

Two document families:

* Memorandum opinions / Magistrate reports: a ')'-railed caption under the
  'IN THE COURT OF CHANCERY...' banner, a centered doc-title, Date
  Submitted/Decided, counsel paragraphs, then the byline that opens the
  body — spelled ('WILL, Vice Chancellor') or abbreviated ('LASTER, V.C.' /
  'WRIGHT, M.' — Magistrate in Chancery), both extending the shared tables.

* Letter rulings: a 'COURT OF CHANCERY / OF THE / STATE OF DELAWARE'
  letterhead naming the judicial officer (merged by column with the
  courthouse address), the 'Re:' block, a salutation ('Dear ...:' /
  'Counsel:') that opens the body, and an '/s/ Name' signature. The author
  is the signature name plus the letterhead title (the title is the first
  gap-separated run of its letterhead line). Typed as orders.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

_CHANCERY_TITLES = ("CHANCELLOR", "VICE CHANCELLOR", "JUDGE", "MAGISTRATE")


class DelawareChancery(AbbrevTitleSupreme):
    court_id = "delch"
    court_label = "Court of Chancery of the State of Delaware."
    hm_caption_footnotes = True
    author_titles = (
        "Chancellor",
        "Vice Chancellor",
        "Magistrate in Chancery",
        "Master in Chancery",
        "Master",
        "Justice",
        "Judge",
    )
    abbrev_titles = (
        ("V.C.", "Vice Chancellor"),
        ("M.", "Magistrate in Chancery"),
    ) + AbbrevTitleSupreme.abbrev_titles

    def extract(self, pdf_path):
        self._letter_start = None
        self._letter_author = None
        doc = super().extract(pdf_path)
        if self._letter_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        return doc

    # ------------------------------------------------------------- letters
    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._letter_start = None
        if starts:
            return starts
        # A letter ruling: the body opens at the salutation.
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            if t.rstrip(":").startswith("Dear ") or t == "Counsel:":
                self._letter_start = i
                self._letter_author = self._letter_signature(all_segments)
                if self.hm_caption_footnotes:
                    self._hm_super_labels = self._superscript_labels(
                        seg for _, seg, _ in all_segments[:i]
                    )
                return [i]
        return []

    def _letter_signature(self, all_segments):
        """'/s/ Name' plus the letterhead title — the title is the first
        gap-separated run of its letterhead line ('CHANCELLOR  500 N. KING
        STREET ...')."""
        name = None
        lines = [l for _p, seg, _k in all_segments for l in seg]
        for line in lines:
            t = self.line_plain_text(line).strip()
            if t.lower().startswith("/s/"):
                name = t[3:].strip()
                break
        title = None
        for line in lines:
            runs = self._split_line_runs(line)
            first = self.line_plain_text(runs[0]).strip() if runs else ""
            if first.upper() in _CHANCERY_TITLES:
                title = first.title() if first.isupper() else first
                break
        if name and title:
            return f"{name}, {title}"
        return name or None

    def split_author_line(self, line):
        if getattr(self, "_letter_start", None) is not None:
            # The salutation opens the letter body; the author signs at the
            # end.
            return (self._letter_author or ""), [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_letter_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # ---------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Styled headmatter with the ')'-railed caption folded into a
        two-column block (letter rulings have no rail and pass through)."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d
