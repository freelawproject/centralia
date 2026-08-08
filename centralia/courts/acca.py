"""United States Army Court of Criminal Appeals. ('acca') — on the shared military CCA base."""

from __future__ import annotations

from ._military import MilitaryCCA


class ArmyCCA(MilitaryCCA):
    court_id = "acca"
    court_label = "United States Army Court of Criminal Appeals."

    def find_footnote_separator(self, page):
        """NOTHING IS DRAWN ON AN ARMY SLIP — the separator is the label.

        Alone among the four service CCAs, the Army's opinions reach us as a
        SCAN with an OCR text layer over it (afcca, nmcca and uscgcoca are
        born-digital and are all healthy).  The printed separator is part of
        the picture, so ``page.rects``, ``page.lines`` and ``page.curves`` are
        empty, and the OCR normalises the notes to the body's 12pt — every
        step of the shared chain looks for a shape or a drop in type size and
        finds neither.  All 20 documents produced ZERO footnotes; ten carried
        'footnote text left in the body'.

        What the OCR does preserve is the LABEL: it sets the opening digit
        smaller (7-9pt against a 12pt line) and puts it at the page's own left
        text rail, where the note's hanging indent starts.  That is the
        separator here, and the two populations are measured and disjoint.
        Over the corpus ``detect_footnote_label`` fires on 144 lines:

          * 69 sit at the rail (x0 - rail of -1, 0, +1 or +2pt).  Per document
            these form EXACTLY the sequence the opinion owes — 1..10 for
            captain_lamario, 1..14 for williams-clark, 1..7 for varlaro — with
            no extra, no repeat and no gap except where a page is an
            unrecoverable image (ayuso's 2 and 3, prajapati's 1, both already
            warned as 'scanned image, not text').
          * The other 75 are the printed folio, centred (x0 - rail of ~231),
            and body reference marks that pdfplumber split onto their own
            baseline mid-line (x0 - rail of 33 to 425).

        The nearest miss on either side of the rail band is 33pt, so no
        threshold is being tuned here.  No page-position fence: varlaro p6
        opens its zone at 0.38 of the page and nelson p9 at 0.42, both because
        the notes above them ran long.
        """
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        rail = self._page_text_rail(page)
        if rail is None:
            return None
        best = None
        for line in page.extract_text_lines():
            if not (-3.0 <= line["x0"] - rail <= 6.0):
                continue
            if self.detect_footnote_label(line) is None:
                continue
            if best is None or line["top"] < best:
                best = line["top"]
        return None if best is None else best - 1

    def build_footnote(self, label, lines):
        """Lift the note's own label out of the note's text.

        ``build_footnote`` strips a leading label only when
        ``line_inline_text`` wrapped it in ``<footnotemark>``, and that is
        proved by a RAISED BASELINE.  The OCR sets these labels on the body
        baseline — smaller, but level — so nothing was stripped and a note
        opened by repeating itself ('10 Appellant argues that his guilty
        finding is ambiguous …'), or by an empty ``<strong> </strong>`` left
        where the label had been styled.  31 of the 67 notes read that way.

        Only the characters ``detect_footnote_label`` already matched are
        removed, and only when they spell the label this note was given, so a
        note that genuinely opens on a numeral keeps it (varlaro's note 2 is
        the citation '86 M.J. 30 (C.A.A.F. 2025)')."""
        if len(lines) > 1 and self.line_plain_text(lines[0]).strip() == label:
            # The label was set on its own line and stayed there.
            lines = list(lines[1:])
        elif lines:
            head = lines[0]
            chars = head.get("chars") or []
            if chars and self.detect_footnote_label(head):
                size = self._line_type_size(chars)
                i = 0
                while (
                    i < len(chars)
                    and round(chars[i]["size"], 1) <= size - 1.5
                    and chars[i]["text"] in self.FOOTNOTE_LABEL_CHARS
                ):
                    i += 1
                if i and "".join(c["text"] for c in chars[:i]) == label:
                    j = i
                    while j < len(chars) and not chars[j]["text"].strip():
                        j += 1
                    if j < len(chars):
                        head = dict(head)
                        head["chars"] = chars[j:]
                        head["text"] = "".join(c["text"] for c in chars[j:])
                        head["x0"] = min(c["x0"] for c in chars[j:])
                        lines = [head] + list(lines[1:])
        return super().build_footnote(label, lines)
