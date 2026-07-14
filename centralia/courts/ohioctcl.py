"""Ohio Court of Claims.

Ohio-style: a '[Cite as …]' line above the banner (dropped + surfaced),
a whitespace caption that names the judge inline ('Requester    Judge
Lisa L. Sadler' / 'v.    DECISION AND ENTRY'), then '{¶1}'-numbered
paragraphs. Later pages carry a 'Case No. … -2- DECISION & ENTRY' running
head; the tail has 'Filed <date> / Sent to S.C. Reporter <date>' clerk
stamps — furniture, dropped and surfaced.
"""

from __future__ import annotations

from .generic import GenericExtractor


class OhioCourtOfClaims(GenericExtractor):
    court_id = "ohioctcl"
    court_label = "Ohio Court of Claims."

    # the '[Cite as …]' line sits at top≈38 — keep it in the flow so the
    # cite drop below can record it (default margin_top=39 ate it silently)
    margin_top = 30
    # exhibit-table rows are tightly pitched and read as 'notice' — keep
    # them in the body (completeness-first)
    drop_notice_in_body = False
    # The body is single-spaced at ~20.7pt leading — inside the default
    # blockquote band, so every paragraph rendered as a quote. Retune the
    # bands to the single-spaced rhythm; a genuinely indented quote is still
    # caught by geometry.
    gap_tight_max = 14
    gap_single_max = 18
    blockquote_by_indent = True
    # 'SARAH PIERCE / Special Master' sign-offs are short-line stacks; split
    # them one block per line (feeds the signature harvest below).
    split_line_stacks = True
    # Some files set the '{¶8}' pinpoint raised + small, so the digit reads
    # as a footnote reference and the marker renders mangled
    # ('{<footnotemark>¶8</footnotemark>}') — keep brace-wrapped digits inline.
    bracket_pinpoint = True
    # Footnotes are set at BODY size (only the label digit is raised, e.g.
    # ogle p5: 144pt rule, 6.5pt '3', 12pt text), so the 'smaller text below'
    # test rejects the real separator — use the structural test (shared with
    # washctapp / ohioctapp).
    footnote_sep_structural = True

    # ---------------------------------------------- {¶N} body paragraphs
    def _split_on_pinpoint(self, seg):
        """'{¶N}'-numbered paragraphs open on the marker; the leading is
        uniform, so the marker — not the gap — is the paragraph boundary."""
        if not seg:
            return []
        paras = [[seg[0]]]
        for line in seg[1:]:
            if self.line_plain_text(line).lstrip().startswith("{¶"):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def split_body_paragraphs(self, seg):
        return [p for grp in self._split_on_pinpoint(seg)
                for p in super().split_body_paragraphs(grp)]

    def split_blockquote_paragraphs(self, seg):
        return [p for grp in self._split_on_pinpoint(seg)
                for p in super().split_blockquote_paragraphs(grp)]

    def _begins_paragraph_block(self, lines):
        """A '{¶N}' line always opens a fresh paragraph — never fold it into
        the previous paragraph across a page break. An ALL-CAPS short heading
        ('APPENDIX A') opens its own block too — folding it onto the page-end
        signature produced 'Special Master <pagenumber/> APPENDIX A …'."""
        if not lines:
            return False
        t = self.line_plain_text(lines[0]).strip()
        if t.startswith("{¶"):
            return True
        return bool(t) and len(t) <= 40 and t.isupper()

    def extract_page_tables(self, page):
        # completeness-first (the district rule): exhibit tables stay as
        # body lines so their rows are never excluded
        return []

    def page_lines(self, page):
        if not hasattr(self, "_octcl_dropped"):
            self._octcl_dropped = []
        lines = super().page_lines(page)
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            low = t.lower()
            # cite line / running head / clerk stamps
            if t.startswith("[Cite as ") or (
                page.page_number > 1
                and l.get("top", 0) < 60
                and low.startswith("case no.")
            ) or low.startswith(("filed ", "sent to s.c. reporter")):
                if t:
                    self._octcl_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def find_authors(self, all_segments) -> list:
        # author: the caption's inline 'Judge NAME' / 'Magistrate NAME';
        # the opinion starts at the first '{¶' paragraph
        self._octcl_author = None
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            for l in seg:
                t = self.line_plain_text(l).strip()
                if self._octcl_author is None:
                    for key in ("Judge ", "Magistrate "):
                        ki = t.find(key)
                        if ki >= 0:
                            cand = t[ki + len(key) :].strip()
                            if 2 <= len(cand.split()) <= 4 and all(
                                w[:1].isupper() for w in cand.split()
                            ):
                                self._octcl_author = key + cand
                                break
            if start is None and seg and self.line_plain_text(seg[0]).lstrip().startswith(
                "{¶"
            ):
                start = i
        return [start] if start is not None else super().find_authors(all_segments)

    def split_author_line(self, line):
        return (getattr(self, "_octcl_author", None) or ""), [line]

    def extract(self, pdf_path: str):
        self._octcl_dropped = []
        doc = super().extract(pdf_path)
        self._harvest_octcl_signature(doc)
        if self._octcl_dropped:
            seen, extra = set(), []
            for t in self._octcl_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    # ------------------------------------------------------------ signature
    _SIG_TITLES = ("judge", "magistrate", "special master")

    def _harvest_octcl_signature(self, doc) -> None:
        """Lift the trailing conformed signature — the ALL-CAPS signer name
        over a judicial title ('LISA L. SADLER / Judge', 'SARAH PIERCE /
        Special Master') — off the last opinion into ``doc.signature`` so the
        name and title keep their own lines in the Signature box."""
        import re as _re

        if not doc.opinions:
            return
        op = doc.opinions[-1]
        if len(op.blocks) < 2:
            return
        untag = lambda s: _re.sub(r"<[^>]+>", "", s or "").strip()  # noqa: E731
        title = untag(op.blocks[-1].text)
        name = untag(op.blocks[-2].text)
        if title.lower() not in self._SIG_TITLES:
            return
        toks = name.split()
        if not (
            1 < len(toks) <= 5
            and all(t.rstrip(".,").isupper() for t in toks if t.rstrip(".,"))
        ):
            return
        doc.signature = [name, title]
        op.blocks = op.blocks[:-2]
