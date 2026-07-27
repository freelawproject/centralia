"""Colorado Court of Appeals.

Distinct layout, tuned directly here:

  * A front-matter page precedes the opinion. It opens with a publication
    notice ('The summaries of the Colorado Court of Appeals published opinions
    constitute no part of the opinion ...') followed by an official SUMMARY /
    headnote (announcement number '2025COA88', docket + case + subject tags,
    and a prose summary). The notice goes to ``dropped`` and the summary to the
    ``syllabus`` field — neither is opinion content. The real headmatter begins
    on the next page, which opens with the 'COLORADO COURT OF APPEALS' banner.

  * The author is announced, not signed: 'Opinion by JUDGE SCHUTZ' (with
    'Grove and Bernard, JJ., concur' beneath). The opinion body opens at the
    first numbered paragraph, '¶ 1'. So the author is read off the announcement
    and the opinion starts at '¶ 1' (the announcement / counsel block stays in
    the headmatter).
"""

from __future__ import annotations

from ._appellate import StateAppellate

_NOTICE_CUE = "constitute no part of the opinion"
_NOTICE_END = "language in the opinion"
# The caption page announces itself: the banner is its first line. Everything
# before it — however many pages the official summary runs to — is front matter.
_CAPTION_BANNER = "colorado court of appeals"


class ColoradoCourtOfAppeals(StateAppellate):
    court_id = "coloctapp"
    court_label = "Colorado Court of Appeals."

    # ---------------------------------------------------------- front matter
    def extract(self, pdf_path: str):
        self._front_notice = None
        self._front_syllabus = []
        self._in_front_notice = True
        self._colo_author = None
        doc = super().extract(pdf_path)
        if self._front_notice:
            doc.dropped = list(doc.dropped) + [self._front_notice]
        if self._front_syllabus:
            doc.syllabus = self._front_syllabus
        return doc

    def caption_page(self, pdf):
        """The first page whose opening line is the court banner. The official
        summary ahead of it runs to one page or two, so 'the page after the
        notice' is not reliable — the banner is.

        This is also where the caption's four full-measure rules live; measured
        on page 1 they are simply absent and the caption renders unruled."""
        for page in pdf.pages:
            try:
                lines = sorted(
                    page.extract_text_lines(), key=lambda l: l.get("top", 0)
                )
            except Exception:
                continue
            if lines and (lines[0].get("text") or "").strip().lower().startswith(
                _CAPTION_BANNER
            ):
                return page
        return pdf.pages[0] if pdf.pages else None

    def find_footnote_separator(self, page):
        """Colorado sets footnotes at the BODY size (14pt) and rules them off
        with a full-measure line — the same width as the four rules that
        divide the caption. Neither width nor type size can tell those apart,
        so the separator is found structurally instead, by the single-spaced
        matter beneath a rule that stands clear of any text line.

        On the CAPTION page that still isn't enough: its four dividers are
        full-measure rules with body text under them, and the last one would
        swallow the whole counsel block into a footnote. Colorado draws no
        footnote rule there at all — the starred assignment note under counsel
        has no divider — so the caption page simply has no separator."""
        if page.page_number == getattr(self, "_caption_pno", 1):
            return None
        return self._footnote_sep_structural(page)

    def page_lines(self, page):
        """Every page BEFORE the caption page is front matter: the publication
        notice -> dropped, the official summary after it -> syllabus. None of
        it reaches the opinion pipeline. The summary runs to a second page on
        longer cases, so the split is by position relative to the caption page,
        not by which page happens to carry the notice."""
        if page.page_number >= getattr(self, "_caption_pno", 1):
            return super().page_lines(page)
        notice, syl = [], []
        for l in sorted(page.extract_text_lines(), key=lambda l: l.get("top", 0)):
            t = (l.get("text") or "").strip()
            if not t:
                continue
            if self._in_front_notice:
                notice.append(t)
                if _NOTICE_END in t.lower():
                    self._in_front_notice = False
            else:
                syl.append(t)
        if notice:
            self._front_notice = " ".join(
                ([self._front_notice] if self._front_notice else []) + notice
            )
        self._front_syllabus = list(self._front_syllabus) + syl
        return []

    # ------------------------------------------------------ byline / ¶1 start
    def find_authors(self, all_segments) -> list:
        # Author is announced ('Opinion by JUDGE SCHUTZ'); read it off. The line
        # sits inside the centered disposition block, so scan every line.
        self._colo_author = None
        for _p, seg, _k in all_segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                if t.lower().startswith("opinion by "):
                    self._colo_author = t[len("opinion by ") :].strip()
                    break
            if self._colo_author:
                break
        # The opinion body opens at the first numbered paragraph.
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip()
            if t.startswith("¶ 1") or t.startswith("¶1"):
                return [i]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        # The opinion opens on body (¶ 1), not a byline — keep the line as body.
        if self.line_plain_text(line).strip().startswith("¶"):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if self._colo_author:
            op.author = self._colo_author
        return op
