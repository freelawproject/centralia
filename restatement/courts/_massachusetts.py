"""Shared front matter for the Massachusetts appellate courts (mass / massappct).

The Supreme Judicial Court and the Appeals Court print the same slip-opinion
front matter, so the handling lives here once and each court file just picks its
byline base (the SJC seats Justices; the Appeals Court seats Judges):

  * a publication NOTICE ('NOTICE: All slip opinions and orders are subject to
    formal revision ... SJCReporter@sjc.state.ma.us') -> dropped;
  * docket, caption, the argued/decided line and the 'Present: NAME, ... JJ.'
    panel -> headmatter;
  * the reporter HEADNOTES that follow the panel — a block of subject-matter
    topic phrases ('Obscenity, Dissemination of matter harmful to minor. Social
    Media. ...') — -> the ``syllabus`` field (a reporter summary, not part of
    the opinion);
  * the procedural history that follows the headnotes ('Indictments found and
    returned ...', 'The case was heard by ...') and the counsel block stay in
    the headmatter, before the byline.

A per-curiam order (single-justice or 'IN THE MATTER OF ...') has no authored
byline; its body opens just after the centered 'Supreme Judicial Court.' header
or, where there is none, at the first prose paragraph following the headnotes.
The top-right page number on continuation pages is folded out of the body.

The byline itself ('GAZIANO, J. This case ...' / 'NAME, Judge.') is recognized
by the abbreviated-title parser the byline bases already provide.
"""

from __future__ import annotations

# Opening of the procedural-history block (case-how-it-got-here) that follows the
# reporter headnotes — marks the end of the headnote run.
_PROC_MARKERS = (
    "civil action",
    "civil actions",
    "complaint",
    "complaints",
    "indictment",
    "indictments",
    "petition",
    "information",
    "the case was",
    "the cases were",
    "motion",
    "summons",
)
# Opening of a per-curiam order's body (no byline anchors it).
_ORDER_BODY_STARTS = (
    "the plaintiff",
    "the petitioner",
    "the defendant",
    "the commonwealth",
    "the appellant",
    "this case",
)


class MassachusettsStyle:
    fold_page_numbers = True

    # ------------------------------------------------------------- orders
    def extract(self, pdf_path):
        self._mass_order_start = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._mass_order_start = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # Per-curiam order (no byline): the body opens after the centered
        # 'Supreme Judicial Court.' header, or — when there is none — at the first
        # prose paragraph ('The plaintiff ...') following the headnotes.
        for i, (_p, seg, _k) in enumerate(all_segments):
            low = self.line_plain_text(seg[0]).strip().lower()
            if low.rstrip(".") == "supreme judicial court" and i + 1 < len(all_segments):
                self._mass_order_start = i + 1
                return [i + 1]
            if low.startswith(_ORDER_BODY_STARTS):
                self._mass_order_start = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_mass_order_start", None) is not None:
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_mass_order_start", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op

    # --------------------------------------------------------- front matter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        lines = [
            ln
            for seg in headmatter_segs
            for ln in seg
            if (ln.get("text") or "").strip()
        ]
        notice, headnote, hm = [], [], []
        phase, seen_panel = "pre", False
        for ln in lines:
            t = (ln.get("text") or "").strip()
            low = t.lower()
            chars = ln.get("chars") or []
            pno = (chars[0].get("page_number") if chars else 1) or 1
            size = self.line_meta(ln)[0]

            if phase == "pre":
                if low.startswith("notice:"):
                    phase = "notice"
                    notice.append(t)
                    continue
                phase = "hm"
            if phase == "notice":
                notice.append(t)
                if "sjcreporter@" in low or "@sjc.state.ma.us" in low:
                    phase = "hm"
                continue
            if phase == "hm":
                hm.append(ln)
                if low.startswith("present:"):
                    seen_panel = True
                if seen_panel and t.rstrip().endswith("JJ."):
                    phase = "headnote"
                continue
            if phase == "headnote":
                # Headnotes are topic phrases; they end at the procedural-history
                # block ('Indictments found ...') or the next page. A
                # footnote-sized line is a caption footnote, not a headnote.
                if pno > 1 or low.startswith(_PROC_MARKERS):
                    phase = "hm"
                    hm.append(ln)
                elif size >= 10:
                    headnote.append(t)
                continue

        styled = self._styled_headmatter([hm], page1_rules)
        styled["syllabus"] = headnote
        styled["dropped"] = [" ".join(notice)] if notice else []
        return styled
