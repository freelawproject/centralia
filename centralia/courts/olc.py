"""Office of Legal Counsel, U.S. Department of Justice.

Small slip pages (423x657). '(Slip Opinion)' header, the opinion title,
a headnote summary (all headmatter), then 'MEMORANDUM OPINION FOR THE
GENERAL COUNSEL …' opens the single opinion. Signed at the end with the
author's name over 'Deputy/Acting Assistant Attorney General / Office of
Legal Counsel' — lifted to the Signature section and used as the author.
"""

from __future__ import annotations

from .generic import GenericExtractor


class OfficeOfLegalCounsel(GenericExtractor):
    court_id = "olc"
    court_label = "Office of Legal Counsel, U.S. Department of Justice."

    # small page stock (423x657): the page number sits at ~595
    margin_top = 30
    margin_bottom = 588
    # OLC body is single-spaced small type — its tight line pitch reads as
    # 'notice' to the classifier; keep those segments in the body
    drop_notice_in_body = False

    def find_authors(self, all_segments) -> list:
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip().upper()
            if t.startswith(("MEMORANDUM OPINION", "MEMORANDUM FOR", "LETTER OPINION")):
                return [i]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        return (getattr(self, "_olc_author", None) or ""), [line]

    def extract(self, pdf_path: str):
        self._olc_author = None
        doc = super().extract(pdf_path)
        # signature: NAME over '… Assistant Attorney General' (+ office)
        if doc.opinions:
            op = doc.opinions[-1]
            blocks = op.blocks
            for k in range(len(blocks) - 1, max(-1, len(blocks) - 5), -1):
                t = self._plain(blocks[k].text).strip()
                if t.lower().endswith("attorney general") and k > 0:
                    name = self._plain(blocks[k - 1].text).strip()
                    if 2 <= len(name.split()) <= 5 and name == name.upper():
                        take = len(blocks) - (k - 1)
                        doc.signature = [str(b.text) for b in blocks[k - 1 :]]
                        op.blocks = blocks[: k - 1]
                        op.author = name.title()
                        break
        return doc

    @staticmethod
    def _plain(text: str) -> str:
        out, i, s = [], 0, str(text)
        while True:
            j = s.find("<", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            k = s.find(">", j)
            if k < 0:
                break
            i = k + 1
        return "".join(out)
