"""Supreme Court of Ohio.

Byline is a bold abbreviated-title line ('DEWINE, J.' / 'BRUNNER, J.,
concurring in judgment only.'). A non-bold authorship summary ('DEWINE, J.,
authored the opinion of the court, which ...') and a sitting-by-designation
line ('HENSAL, J., of the Ninth District Court of Appeals, sat for DETERS, J.')
both start with the bold surname but continue with a comma clause, so the
bold requirement plus the comma-continuation rule exclude them.

Page furniture and front matter, tuned here:
  * the top-margin running header ('Supreme Court of Ohio' / 'January Term,
    2026') and the bottom page number are dropped/folded out of the body;
  * two notices — the bracketed citation advisory ('[Until this opinion appears
    in the Ohio Official Reports ...]') and the 'NOTICE / This slip opinion is
    subject to formal revision ...' block — go to ``dropped``;
  * the official headnote (subject-matter summary + '(No. ... Submitted ...
    Decided ...)' + 'APPEAL from ...') is captured into the syllabus field;
  * the headmatter proper is the 'SLIP OPINION NO. ...' line and the case
    caption. Body paragraphs are '{¶ N}'-numbered.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

_TERMS = (
    "january term",
    "february term",
    "march term",
    "april term",
    "may term",
    "june term",
    "july term",
    "august term",
    "september term",
    "october term",
    "november term",
    "december term",
)


class OhioSupreme(AbbrevTitleSupreme):
    court_id = "ohio"
    court_label = "Supreme Court of Ohio."
    require_bold_byline = True
    fold_page_numbers = True

    # ------------------------------------------------------------- furniture
    def page_lines(self, page):
        """Drop the top-margin running header ('Supreme Court of Ohio' /
        'January Term, 2026') from the body."""
        out = []
        for l in super().page_lines(page):
            low = (l.get("text") or "").strip().lower()
            if low == "supreme court of ohio" or low.startswith(_TERMS):
                continue
            out.append(l)
        return out

    # --------------------------------------------------------- front matter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Partition the pre-opinion content: the two notices -> dropped, the
        headnote -> syllabus, the SLIP OPINION line + caption -> headmatter."""
        lines = [
            ln
            for seg in headmatter_segs
            for ln in seg
            if (ln.get("text") or "").strip()
        ]
        notice, headnote, hm = [], [], []
        phase = "notice"
        for ln in lines:
            t = (ln.get("text") or "").strip()
            low = t.lower()
            if phase == "notice":
                if low.startswith("slip opinion no"):
                    phase = "headmatter"
                    hm.append(ln)
                else:
                    notice.append(t)
            elif phase == "headmatter":
                if low.startswith("[until this opinion"):
                    phase = "headnote"
                    headnote.append(t)
                else:
                    hm.append(ln)
            elif phase == "headnote":
                if t and all(c in "_-—–" for c in t):  # divider ends headnote
                    phase = "trailer"
                else:
                    headnote.append(t)
            else:  # authorship/panel block
                hm.append(ln)

        items = [
            (round(ln["top"], 1), round(ln["x0"], 1), (ln.get("text") or "").strip())
            for ln in hm
        ]
        return {
            "court": self.court_label or self.court_id,
            "summary": self._layout_rows(items),
            "syllabus": headnote,
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [" ".join(notice)] if notice else [],
        }
