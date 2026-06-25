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


class ColoradoCourtOfAppeals(StateAppellate):
    court_id = "coloctapp"
    court_label = "Colorado Court of Appeals."

    # ---------------------------------------------------------- front matter
    def extract(self, pdf_path: str):
        self._front_notice = None
        self._front_syllabus = []
        self._colo_author = None
        doc = super().extract(pdf_path)
        if self._front_notice:
            doc.dropped = list(doc.dropped) + [self._front_notice]
        if self._front_syllabus:
            doc.syllabus = self._front_syllabus
        return doc

    def page_lines(self, page):
        """The SUMMARY front-matter page (the one carrying the publication
        notice) is split out: the notice -> dropped, the rest -> syllabus. It
        contributes nothing to the opinion pipeline."""
        text = (page.extract_text() or "").lower()
        if _NOTICE_CUE in text:
            notice, syl, in_notice = [], [], True
            for l in sorted(page.extract_text_lines(), key=lambda l: l.get("top", 0)):
                t = (l.get("text") or "").strip()
                if not t:
                    continue
                if in_notice:
                    notice.append(t)
                    if _NOTICE_END in t.lower():
                        in_notice = False
                else:
                    syl.append(t)
            self._front_notice = " ".join(notice)
            self._front_syllabus = syl
            return []
        return super().page_lines(page)

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
