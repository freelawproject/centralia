"""United States District Court, Eastern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes
the author from the signature block and treats the whole ruling as one
opinion; the pleading line-number gutter and CM/ECF header band are dropped.

Body is double-spaced with a first-line paragraph indent, and section heads
are short BOLD standalone lines — a centered title ('Screening Order') or a
left enumerator ('I. Legal Standard' / 'II. Analysis'). Those head lines are
kept out of the surrounding paragraph (each stands alone) and rendered as
headings; the generic re-based indent split handles the body paragraphs.
"""

from __future__ import annotations

import re

from ._district import DistrictBase

_TAG = re.compile(r"<[^>]+>")
_ROMAN = set("IVXLC")


def _is_section_heading(t: str) -> bool:
    t = t.strip()
    if not t or len(t) > 60:
        return False
    head, _, rest = t.partition(" ")
    num = head.rstrip(".")
    if head.endswith(".") and rest and (
        all(c in _ROMAN for c in num)
        or (len(num) == 1 and num.isalpha())
        or num.isdigit()
    ):
        return True  # 'I. Legal Standard' / 'A. …' / '1. …'
    return (
        len(t.split()) <= 6
        and not t.endswith((".", ",", ";", ":"))
        and t[0].isupper()
    )  # 'Screening Order' / 'BACKGROUND'


class EasternDistrictOfCalifornia(DistrictBase):
    court_id = "caed"
    styled_headmatter = True
    court_label = "United States District Court, Eastern District of California."

    def page_lines(self, page):
        """Mark the first line BELOW the page-1 caption band with
        ``_seg_break`` so the caption cannot share a segment with the ruling's
        opening paragraph.

        On this court's pleading paper the caption's last party-role row
        ('Defendants.') and the first line of the ruling are the same size,
        the same alignment and one double-spaced line apart, so the shared
        segmenter joins them. That merged segment straddles the caption band,
        which hides the fact that body prose has begun: the opinion-start scan
        then keeps looking and settles on the first bold section head several
        inches down the page, leaving the ruling's opening paragraph stranded
        in the headmatter. The caption band bottom is drawn geometry (the mid
        vertical and the shelf that closes into it), so breaking the segment
        there follows the page."""
        # Preserve the complete raw footer row before the pleading-gutter
        # filter separates its left law-firm letterhead from the right running
        # document title.  Both are furniture, but both must remain visible in
        # Removed for source accounting.
        if getattr(self, "_caed_footer", None) is not None:
            for line in page.extract_text_lines():
                if line.get("top", 0) > 730:
                    text = self.line_plain_text(line).strip()
                    if text:
                        self._caed_footer.append(text)

        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        cap_bottom = self._caption_band_bottom()
        if cap_bottom is None:
            return lines
        below = [l for l in lines if l.get("top", 0) > cap_bottom - 6]
        if below:
            min(below, key=lambda l: l["top"])["_seg_break"] = True
        return lines

    def _is_heading_line(self, line) -> bool:
        _sz, _fn, bold = self.line_meta(line)
        return bold and _is_section_heading(self.line_plain_text(line).strip())

    def _paragraph_ended(self, line) -> bool:
        """Whether ``line`` is the LAST line of its paragraph.

        This court sets its body flush left with no first-line indent, so x0
        cannot mark a paragraph start and the shared indent rule folds
        everything after a paragraph's short closing line into it — which is
        how 'DATED: January 13, 2026' ended up inside the decretal sentence
        above it. The measure does mark it: the text is ragged right, and a
        line that stops a fifth of the measure short of the right edge stopped
        because the paragraph did. Ordinary wrapped lines in this corpus come
        within 8% of the edge, so the window is wide enough not to cut prose."""
        pw = getattr(self, "_page1_width", None) or 612.0
        right = pw - self.body_baseline_x0
        return line.get("x1", 0.0) < right - 0.20 * (right - self.body_baseline_x0)

    def split_body_paragraphs(self, seg) -> list:
        # a bold heading line never merges into a body paragraph — it stands
        # alone, and the line after it begins a fresh paragraph
        paras = []
        run = []
        for line in seg:
            if self._is_heading_line(line):
                if run:
                    paras.extend(super().split_body_paragraphs(run))
                    run = []
                paras.append([line])
            elif run and self._paragraph_ended(run[-1]):
                paras.extend(super().split_body_paragraphs(run))
                run = [line]
            else:
                run.append(line)
        if run:
            paras.extend(super().split_body_paragraphs(run))
        return paras

    def extract(self, pdf_path: str):
        self._caed_footer = []
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind == "p" and "<strong>" in str(b.text):
                    inner = _TAG.sub("", str(b.text)).strip()
                    if self._all_bold(b.text) and _is_section_heading(inner):
                        b.kind = "heading"
        self._drop_pleading_filler(doc)
        self._harvest_graphic_signature(doc)
        self._reclassify_party_filing(doc)
        return doc

    def _sweep_residual(self, doc, source_pages):
        footer = list(dict.fromkeys(getattr(self, "_caed_footer", []) or []))
        if footer:
            doc.dropped = list(dict.fromkeys(list(doc.dropped) + footer))
        super()._sweep_residual(doc, source_pages)

    # --------------------------------------------------------- page filler
    def _drop_pleading_filler(self, doc) -> None:
        """'////' is the pleading-paper filler this court types down the unused
        line-numbered rows at the foot of a page so the numbering stays
        continuous. It is page furniture, not text, so it is surfaced in the
        Removed box rather than read as a paragraph."""
        for op in doc.opinions:
            keep, moved = [], []
            for b in op.blocks:
                if b.kind == "p":
                    t = _TAG.sub("", str(b.text)).strip()
                    if t and set(t) <= set("/ "):
                        moved.append(t)
                        continue
                keep.append(b)
            if moved:
                op.blocks = keep
                doc.dropped = list(doc.dropped) + moved

    # ---------------------------------------------------------- signature
    def _harvest_graphic_signature(self, doc) -> None:
        """Lift a trailing signature GRAPHIC (and the date stamp printed with
        it) into the Signature section.

        Judges here sign with a scanned graphic, so the name and title are
        pixels and there is no title line for the shared harvester to anchor
        on. This court also prints the 'DATED: <date>' stamp BELOW the
        graphic, where the shared image path — which reads the block directly
        above the image — cannot see it. Take the graphic plus a date stamp on
        either side of it, and nothing else."""
        if doc.signature or not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        end = len(blocks)
        while end > 0 and blocks[end - 1].kind == "p" and self._is_stamp(
            blocks[end - 1]
        ):
            end -= 1
        if end == 0 or blocks[end - 1].kind != "image":
            return
        first = end - 1
        if first > 0 and blocks[first - 1].kind == "p" and self._is_stamp(
            blocks[first - 1]
        ):
            first -= 1
        doc.signature = [
            {"__image__": True, **(b.payload or {})}
            if b.kind == "image"
            else str(b.text)
            for b in blocks[first:]
        ]
        op.blocks = blocks[:first]

    def _is_stamp(self, block) -> bool:
        """A short date stamp line ('DATED: January 13, 2026.') — the openers
        are the ones the shared signature harvester recognises."""
        t = _TAG.sub("", str(block.text)).strip()
        return len(t) <= 48 and t.lower().startswith(("dated", "date:", "signed"))

    # ------------------------------------------------------ document style
    def _reclassify_party_filing(self, doc) -> None:
        """A paper filed BY a party is not a ruling.

        This corpus mixes the court's own orders with an AO-458 appearance
        form, a habeas petition and a joint status report — all on the same
        pleading paper with the same caption, so nothing about the layout
        tells them apart. The signature does: a ruling closes with a judicial
        title line or the judge's signature graphic, while these close with
        counsel's conformed '/s/' signature and nothing else. All three
        conditions are required, so a graphic-signed order (whose title is
        pixels inside the image) is never swept up."""
        from ..models import DocType
        from ._district import _JUDGE_TITLES

        if doc.doc_type != DocType.OPINION:
            return
        titles = {jt.rstrip(".").lower() for jt in _JUDGE_TITLES}
        conformed = False
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind == "image":
                    return  # a signature graphic — the title is in the pixels
                t = _TAG.sub("", str(b.text)).strip()
                low = t.rstrip(".").lower()
                if low in titles or any(low.endswith(" " + jt) for jt in titles):
                    return
                if low.startswith(("/s/", "s/")) or " /s/ " in low:
                    conformed = True
        for s in list(doc.signature or []) + list(doc.trailer or []):
            if isinstance(s, dict):
                return
            low = _TAG.sub("", str(s)).strip().rstrip(".").lower()
            if low in titles or any(low.endswith(" " + jt) for jt in titles):
                return
            if low.startswith(("/s/", "s/")) or " /s/ " in low:
                conformed = True
        if conformed:
            doc.doc_type = DocType.FILING

    @staticmethod
    def _all_bold(html: str) -> bool:
        outside, s = [], str(html)
        while True:
            i = s.find("<strong>")
            if i < 0:
                outside.append(s)
                break
            outside.append(s[:i])
            j = s.find("</strong>", i)
            if j < 0:
                break
            s = s[j + len("</strong>"):]
        return not any(c.isalnum() for c in _TAG.sub("", "".join(outside)))
