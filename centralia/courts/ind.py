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

from ._abbrevtitle import AbbrevTitleSupreme


class IndianaSupreme(AbbrevTitleSupreme):
    court_id = "ind"
    court_label = "Indiana Supreme Court."
    author_titles = ("Justice", "Chief Justice")
    # Separate writings sign 'Molter, J., concurring.' / 'Slaughter, J.,
    # dissenting.' — title-case surnames with the abbreviated title.
    allow_titlecase_name = True

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)

    def extract(self, pdf_path):
        self._footer_dropped = []
        doc = super().extract(pdf_path)
        self._harvest_attorney_tail(doc)
        extra = list(dict.fromkeys(self._footer_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    @staticmethod
    def _plain_tail_heading(text: str) -> str:
        """Normalize spaced/marked-up Indiana counsel headings."""
        for tag in ("<strong>", "</strong>", "<em>", "</em>"):
            text = text.replace(tag, "")
        return "".join(ch for ch in text.upper() if ch.isalpha())

    def _harvest_attorney_tail(self, doc) -> None:
        """Move the final Indiana counsel roster out of the opinion body."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        start = next(
            (
                i
                for i, block in enumerate(op.blocks)
                if (
                    "ATTORNEYFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                    or "ATTORNEYSFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                )
            ),
            None,
        )
        if start is None:
            return
        tail = op.blocks[start:]
        op.blocks = op.blocks[:start]
        doc.trailer = [
            str(block.text or "").strip()
            for block in tail
            if str(block.text or "").strip()
        ]

    def page_lines(self, page):
        lines = super().page_lines(page)
        if getattr(self, "_footer_dropped", None) is None:
            self._footer_dropped = []
        kept = []
        for ln in lines:
            t = self.line_plain_text(ln).strip()
            # Per-page footer ('Indiana Supreme Court | Case No. ... | Page
            # N of M') sits inside the text margins — furniture.
            if ln["top"] > 700 and t.startswith("Indiana Supreme Court"):
                self._footer_dropped.append(t)
                continue
            kept.append(ln)
        return kept

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        # Indiana types its per-curiam byline in title case ('Per curiam.'),
        # which the global ALL-CAPS matcher deliberately ignores.
        if " ".join(text.strip().rstrip(".").split()).lower() == "per curiam":
            return ("Per curiam", "per curiam", None)
        return None
