"""Supreme Court of South Dakota.

Byline is a plain (non-bold) ALL-CAPS surname over the full title word —
'KERN, Retired Justice' / 'SALTER, Justice' / 'JENSEN, Chief Justice' — at
the top of the opinion, above '[¶1.]'-numbered paragraphs. The cover page
carries the docket-and-disposition header ('#30782-aff in pt & rev in
pt-JMK', the authoring justice's initials trailing), the 'IN THE SUPREME
COURT / OF THE / STATE OF SOUTH DAKOTA' banner, '* * * *' rails, the parties,
the 'APPEAL FROM …' history, the trial judge, and counsel — all headmatter.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class SouthDakotaSupreme(StateSupreme):
    court_id = "sd"
    court_label = "Supreme Court of South Dakota."

    def extract(self, pdf_path):
        self._sd_footer = []
        doc = super().extract(pdf_path)
        doc.dropped = _dedupe(list(doc.dropped) + list(self._sd_footer))
        return doc

    def correct_page_geometry(self, page) -> None:
        """Strip Word's INVISIBLE footnote-anchor ghost.

        Some of the Court's opinions are typeset in Cambria via Word, which
        writes a sub-visible (~1pt) '0F' pair beside the real superscript
        footnote mark. It sits on its own baseline, so the line rebuild folds it
        into the body row ('a hypoxic brain injury0F1 from the administration')
        and every anchored sentence stopped matching its printed form. Drop the
        sub-visible chars from the page's object cache so the extractor and the
        audit (which reads through this same hook) both see the real superscript
        only."""
        super().correct_page_geometry(page)
        try:
            objs = page.objects.get("char")
        except Exception:
            objs = None
        if objs:
            objs[:] = [c for c in objs if (c.get("size") or 9.0) > 1.5]

    def page_lines(self, page):
        """Record the bottom-margin filing stamp before the margin filter drops
        it. The page foot carries the centered folio and, on page 1, the clerk's
        'OPINION FILED 11/25/25' stamp at the right — furniture, but it has to be
        surfaced in the Removed box rather than silently discarded."""
        for ln in page.extract_text_lines():
            if ln.get("top", 0) <= self.margin_bottom:
                continue
            text = (ln.get("text") or "").strip()
            if text and not self._is_page_number_text(text):
                self._sd_footer.append(text)
        return super().page_lines(page)

    # ------------------------------------------------------------- footnotes
    def detect_footnote_label(self, line):
        """South Dakota numbers its footnotes '1.', '2.', … set at BODY size and
        flush with the footnote block's left edge, not as a raised superscript —
        so the base 'smaller char' test cannot see them and every footnote on the
        page came back labelled '?', which merged the whole document's footnotes
        into one. A hanging number-dot at the block's left margin is the label;
        continuation lines are indented a step further in and cannot match."""
        if line.get("x0", 999) > self.body_baseline_x0 + 2:
            return super().detect_footnote_label(line)
        toks = (line.get("text") or "").split()
        if toks and toks[0].endswith(".") and toks[0][:-1].isdigit():
            return toks[0][:-1]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the hanging 'N.' marker off the footnote text — it is the label,
        which the renderer draws in its own column."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label.isdigit():
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            if stripped.startswith(label + "."):
                fn.paragraphs[0] = (tag, stripped[len(label) + 1 :].lstrip())
        return fn

    def _sweep_residual(self, doc, source_pages):
        # The sweep runs inside super().extract(), so the stamp has to reach
        # doc.dropped before it, not after.
        stamps = [t for t in getattr(self, "_sd_footer", None) or [] if t]
        if stamps:
            doc.dropped = _dedupe(list(doc.dropped) + stamps)
        super()._sweep_residual(doc, source_pages)


def _dedupe(rows):
    """Order-preserving de-duplication tolerant of unhashable rows."""
    seen, out = set(), []
    for r in rows:
        try:
            if r in seen:
                continue
            seen.add(r)
        except TypeError:  # image/dict rows are never repeated
            pass
        out.append(r)
    return out
