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
    "the respondent",
    "the respondents",
    "this case",
)


class MassachusettsStyle:
    fold_page_numbers = True

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        # A caption footnote can sit in the middle of page 1, followed by the
        # counsel block and opinion byline.  The base model's footnote zone is
        # terminal, so treating that rule as a separator swallows the actual
        # opinion beneath it.  Keep mid-page caption notes in headmatter; true
        # opinion footnotes remain bottom-page zones.
        if page.page_number == 1 and sep is not None and sep < page.height * 0.6:
            return None
        return sep

    # ------------------------------------------------------------- orders
    def extract(self, pdf_path):
        self._mass_order_start = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._mass_order_start = None
        self._mass_advisory_start = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # Per-curiam order (no byline): the body opens after the centered
        # 'Supreme Judicial Court.' header, or — when there is none — at the first
        # prose paragraph ('The plaintiff ...') following the headnotes.
        seen_court_topic = False
        for i, (_p, seg, _k) in enumerate(all_segments):
            low = self.line_plain_text(seg[0]).strip().lower()
            # An ADVISORY opinion ('OPINION OF THE JUSTICES TO THE SENATE')
            # carries no byline at all: the Justices answer collectively and
            # subscribe as a list at the end. Its body opens on the salutation.
            # Without this the whole writing had no opinion start, so an
            # eleven-page response became 435 rows of headmatter and the
            # document classified as a notice.
            if low.startswith("to the honorable"):
                self._mass_advisory_start = i
                self._mass_order_start = i
                return [i]
            if low.rstrip(".") == "supreme judicial court" and i + 1 < len(all_segments):
                self._mass_order_start = i + 1
                return [i + 1]
            if low.startswith(_ORDER_BODY_STARTS):
                self._mass_order_start = i
                return [i]
            # Some single-justice orders have no author byline and begin after
            # a reporter topic headed ``Supreme Judicial Court, ...``.  Topic
            # labels are short single-line segments; the first wrapped prose
            # segment after them is the order body.
            if seen_court_topic and len(seg) >= 2:
                self._mass_order_start = i
                return [i]
            if low.startswith("supreme judicial court,"):
                seen_court_topic = True
        return []

    def split_author_line(self, line):
        if getattr(self, "_mass_order_start", None) is not None:
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_mass_advisory_start", None) == op_start:
            # The Justices answer collectively and subscribe as a list at the
            # end; there is no single author to name.
            op.author = "BY THE JUSTICES"
            op.type = "majority"
        elif getattr(self, "_mass_order_start", None) == op_start:
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
        # The NOTICE is the page's own first SEGMENT — a tightly-led block set
        # off from the caption below it by a full blank line. This used to end
        # at the SJC reporter's e-mail address, which is a token of one court's
        # notice rather than a property of notices: the Appeals Court's Rule
        # 23.0 notice closes 'See Chace v. Curran, 71 Mass. App. Ct. 258, 260
        # n.4 (2008).' and carries no address at all. The terminator therefore
        # never fired and every remaining line of the document — caption,
        # opinion, signature and all — was appended to the notice and dropped,
        # leaving seven summary decisions with no opinion body at all. The
        # segment boundary says the same thing for both courts: on the SJC it
        # closes on exactly the e-mail line the old test looked for.
        notice_lines = set()
        for seg in headmatter_segs:
            first = next((l for l in seg if (l.get("text") or "").strip()), None)
            if first is None:
                continue
            if self.line_plain_text(first).strip().lower().startswith("notice:"):
                notice_lines = {id(l) for l in seg}
            break

        notice, headnote, hm = [], [], []
        phase, seen_panel = "pre", False
        for ln in lines:
            t = (ln.get("text") or "").strip()
            low = t.lower()
            chars = ln.get("chars") or []
            pno = (chars[0].get("page_number") if chars else 1) or 1
            size = self.line_meta(ln)[0]

            if phase == "pre":
                if id(ln) in notice_lines:
                    phase = "notice"
                    notice.append(t)
                    continue
                phase = "hm"
            if phase == "notice":
                if id(ln) in notice_lines:
                    notice.append(t)
                    continue
                phase = "hm"
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
