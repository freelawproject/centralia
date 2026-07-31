"""North Carolina Business Court (Superior Court Division, Complex Business Cases).

Order-and-opinion filings: a two-column NC caption ('STATE OF NORTH CAROLINA /
... / SUPERIOR COURT DIVISION', parties left, 'ORDER AND OPINION ON ...' right),
an italic counsel block, then a numbered-paragraph opinion. The body opens with
'1. THIS MATTER is before the Court ...' (or a spelled 'Conrad, Judge.' byline),
and is signed at the end with '/s/ Name / Special Superior Court Judge for
Complex Business Cases'. Modeled on the district order shape (author from the
end signature; the whole ruling is one opinion).
"""

from __future__ import annotations

from ._district import DistrictBase, _looks_like_name, _strip_sig_prefix


class NCBusinessCourt(DistrictBase):
    court_id = "ncbizct"
    court_label = "North Carolina Business Court."

    # Every published NCBC order is headed by its own reporter CITATION line
    # ('Brock v. Kyryk, 2026 NCBC 62.'), set at body size at the left margin
    # roughly 28-43pt down — i.e. straddling the shared 39pt top margin, so the
    # district default clipped it (and clipped only the first of the two rows a
    # long case name wraps onto). It is the court's own citation, not page
    # furniture: opening the margin keeps it as the first headmatter row. These
    # filings carry no CM/ECF strip, so nothing else lives up there.
    margin_top: float = 24.0

    # ------------------------------------------------- reporter citation head
    def _citation_head(self, headmatter_segs):
        """Split the page-1 CITATION rows off the front of the headmatter.

        Every NCBC order opens with its own reporter citation ('Brock v.
        Kyryk, 2026 NCBC 62.') printed above the caption — one continuous run
        at the left margin, wrapping onto a second row when the case name is
        long. The caption proper starts at the first row the page sets in TWO
        columns (party | court, i.e. a row that splits at a wide x-gap), so
        every page-1 row above that row is citation. Returns
        ``(citation_lines, remaining_segments)``; keeping the citation out of
        ``_styled_caption_rows`` stops the caption block from swallowing it
        (and, on a wrapped citation, from splitting it across two containers).
        """
        flat = []
        for si, seg in enumerate(headmatter_segs):
            for li, line in enumerate(seg):
                chars = line.get("chars") or []
                pno = (chars[0].get("page_number") if chars else None) or 1
                flat.append((pno, line.get("top", 0.0), si, li, line))
        cut = None
        for pno, top, si, li, line in sorted(flat, key=lambda r: (r[0], r[1])):
            if pno != 1:
                break
            if not self.line_plain_text(line).strip():
                continue
            if len(self._caption_char_runs(line)) > 1:
                cut = top
                break
        if cut is None:
            return [], headmatter_segs
        cite = [r for r in flat if r[0] == 1 and r[1] < cut]
        if not cite:
            return [], headmatter_segs
        keep_ids = {id(r[4]) for r in cite}
        rest = []
        for seg in headmatter_segs:
            trimmed = [l for l in seg if id(l) not in keep_ids]
            if trimmed:
                rest.append(trimmed)
        return [r[4] for r in sorted(cite, key=lambda r: r[1])], rest

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Emit the reporter citation as the first headmatter row — joined into
        ONE row when it wraps — then the caption as usual."""
        cite, rest = self._citation_head(headmatter_segs)
        out = super().extract_headmatter(rest, page1_rules=page1_rules)
        if cite:
            html = " ".join(
                self.line_inline_text(l) for l in cite
            ).strip()
            if html:
                out["summary"] = [
                    {"__hm__": True, "html": html, "rel": 1.0, "align": "L"},
                    "",
                ] + list(out.get("summary") or [])
        return out

    @staticmethod
    def _numbered_marker_len(text) -> int:
        """Length of a leading 'N. ' paragraph marker (N = 1-3 digits), else 0.
        A 4-digit run (a year) or a bare number with no period is not a
        marker."""
        t = text.lstrip()
        i = 0
        while i < len(t) and t[i].isdigit():
            i += 1
        if 0 < i <= 3 and t[i : i + 2] == ". ":
            return i + 2
        return 0

    def _is_numbered_para(self, line) -> bool:
        return self._numbered_marker_len((line.get("text") or "")) > 0

    def split_body_paragraphs(self, seg) -> list:
        """NC Business Court numbers every opinion paragraph ('1.' … '51.') with
        a hanging indent; on some filings the marker sits left of the paragraph-
        indent threshold, so the default splitter folds '2.'/'3.' into the
        first paragraph. Start a fresh paragraph at each numbered marker; other
        segments fall back to the default."""
        if not seg or not any(self._is_numbered_para(l) for l in seg):
            return super().split_body_paragraphs(seg)
        paras = [[seg[0]]]
        for line in seg[1:]:
            if self._is_numbered_para(line):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def _opens_ncbc_opinion(self, seg) -> bool:
        """True if ``seg`` opens the order body: 'THIS MATTER is before …'
        (with or without a leading '1.'), any numbered paragraph, or a spelled
        judge byline ('Conrad, Judge.'). The caption/title rows and the italic
        counsel block match none of these, so the first match is the opinion
        start — counsel written above the opener stays in headmatter, counsel
        written below it (mid-order) stays in the body where the court put it."""
        t = self.line_plain_text(seg[0]).strip()
        if not t:
            return False
        body = t[self._numbered_marker_len(t) :].lstrip()
        if body[:11].lower() == "this matter":
            return True
        if self._numbered_marker_len(t) and body:  # a numbered paragraph
            return True
        return self.parse_author_line(t) is not None  # 'Conrad, Judge.'

    def find_authors(self, all_segments) -> list:
        """Start the order at its first opener (see ``_opens_ncbc_opinion``);
        the generic district scan otherwise splits an opening 'THIS MATTER'
        paragraph across the headmatter boundary or runs pages ahead to a
        decretal 'ORDER' heading. ``super()`` first, to set the author."""
        starts = super().find_authors(all_segments)
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._opens_ncbc_opinion(seg):
                return [i]
        return starts

    def _signature_author(self, all_segments):
        """NC Business Court signs '/s/ <Name>' above 'Special Superior Court
        Judge for Complex Business Cases' — a title the district set doesn't
        carry, so the default signature scan misses it. The conformed '/s/'
        name (last in the document) is the reliable author signal."""
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for t in reversed(lines):
            if t.lower().startswith(("/s/", "s/")):
                name = _strip_sig_prefix(t).rstrip(",")
                if _looks_like_name(name):
                    return name
        return super()._signature_author(all_segments)
