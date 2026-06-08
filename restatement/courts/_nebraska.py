"""Shared format for the Nebraska Advance Sheets (Supreme Court + Court of
Appeals). Both reporter-typeset their opinions identically:

  * a red online-library stamp at the very top (above the margin, already
    dropped) and a five-line running header on every page — the reporter page
    ('- 235 -'), 'Nebraska ... Advance Sheets', the volume ('34 Nebraska
    Appellate Reports'), the running case name ('DUNHAM v. DUNHAM'), and 'Cite
    as 34 Neb. App. 235' — which is furniture and is dropped (recorded);
  * a numbered 'Syllabus by the Court' set in small (~9pt) type after the
    caption/filing line, routed to the syllabus field;
  * the rest of the headmatter (caption, the trial-court/counsel block, and the
    panel) set larger, rendered in the style-preserving form.

The author byline ('Bishop, Judge.' / 'Papik, J.') is handled by the court's
abbreviated-title base.
"""

from __future__ import annotations


class NebraskaReporterStyle:
    # Font-size window (pt) of the numbered syllabus/headnote type.
    _headnote_size = (8.6, 9.6)

    def extract(self, pdf_path):
        self._neb_dropped = []
        doc = super().extract(pdf_path)
        seen, uniq = set(), []
        for t in self._neb_dropped:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        if uniq:
            doc.dropped = list(doc.dropped) + uniq
        return doc

    def page_lines(self, page):
        """Drop the per-page running-header band: everything from the top of the
        page through the 'Cite as ...' line."""
        lines = super().page_lines(page)
        cut = -1
        for i, l in enumerate(lines):
            t = (l.get("text") or "").strip().lower()
            if l.get("top", 999) < 135 and t.startswith("cite as"):
                cut = i
        if cut < 0:
            return lines
        for l in lines[: cut + 1]:
            t = (l.get("text") or "").strip()
            if t:
                getattr(self, "_neb_dropped", []).append(t)
        return lines[cut + 1 :]

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Route the small-type numbered syllabus to the syllabus field; the rest
        is styled headmatter."""
        lo, hi = self._headnote_size
        headnote, hm = [], []
        for seg in headmatter_segs:
            for ln in seg:
                t = (ln.get("text") or "").strip()
                if not t:
                    continue
                size = self.line_meta(ln)[0]
                if lo <= size <= hi:
                    headnote.append(t)
                else:
                    hm.append(ln)
        styled = self._styled_headmatter([hm], page1_rules)
        styled["syllabus"] = headnote
        return styled
