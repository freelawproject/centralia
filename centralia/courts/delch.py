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

    _MONTHS = (
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December",
    )

    def extract(self, pdf_path):
        self._letter_start = None
        self._letter_author = None
        doc = super().extract(pdf_path)
        if self._letter_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
        self._lift_chancery_metadata(doc)
        return doc

    def _lift_chancery_metadata(self, doc):
        """Docket and decision date are printed in the headmatter but were
        never lifted into the document fields: memorandum opinions carry
        'C.A. No. …' in the caption and a 'Date Decided:' row; letter rulings
        put 'C.A. No. …' in the 'Re:' block and the date as a standalone
        centered letterhead row."""
        from ..audit import _strip_tags

        texts = []
        for row in doc.summary:
            if isinstance(row, dict):
                if row.get("__hm__"):
                    texts.append(_strip_tags(str(row.get("html", ""))))
                elif row.get("__caption__"):
                    texts.extend(row.get("left") or [])
                    texts.extend(row.get("right") or [])
            elif isinstance(row, str):
                texts.append(row)
        for t in texts:
            t = t.strip()
            if not doc.docket_number and "C.A. No" in t:
                tail = t.split("C.A. No", 1)[1].lstrip(". ").strip()
                if tail:
                    doc.docket_number = f"C.A. No. {tail}"
            if not doc.decision_date:
                if t.startswith(("Date Decided", "Decided")) or (
                    # A magistrate report is dated by its 'Report:' row —
                    # 'Report: July 02, 2026', 'Final Report: …'.
                    t.split(":", 1)[0].endswith("Report") and ":" in t
                ):
                    doc.decision_date = t.split(":", 1)[-1].strip()
                else:
                    # A standalone letterhead date: 'May 14, 2026'.
                    words = t.replace(",", "").split()
                    if (
                        len(words) == 3
                        and words[0] in self._MONTHS
                        and words[1].isdigit()
                        and len(words[2]) == 4
                        and words[2].isdigit()
                    ):
                        doc.decision_date = t
        if not doc.decision_date and doc.opinions:
            # Orders date themselves at the conformed signature:
            # 'Dated: July 2, 2026'.
            for block in doc.opinions[-1].blocks[-4:]:
                text = _strip_tags(str(block.text or ""))
                marker = text.find("Dated:")
                if marker != -1:
                    doc.decision_date = text[marker + len("Dated:") :].strip()
                    break

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
