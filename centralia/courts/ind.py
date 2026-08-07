"""Indiana Supreme Court.

Has a California-style authorship summary up top ('Opinion by Justice
Slaughter'), but the body opens with a standard byline ('Slaughter, Justice.'),
which the core pipeline detects.

The title page carries full-width decorative rules that divide the caption into
sections (parties | argued/appeal info | 'Opinion by ...'/concur). Those sit in
the bottom half of the page and are left-aligned with the body, so the default
footnote-separator finder mistakes the topmost one for a footnote rule and drops
the whole lower caption block (the 'Argued'/'Appeal from'/'Opinion by'/concur
lines) as orphaned footnotes. The separator is instead found by footnote-sized
text directly beneath the rule — a real Indiana footnote sits flush under its
rule, while a caption divider has a section gap below it — so the decorative
rules no longer chop the headmatter.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

from ._abbrevtitle import AbbrevTitleSupreme


class IndianaSupreme(AbbrevTitleSupreme):
    court_id = "ind"
    court_label = "Indiana Supreme Court."
    author_titles = ("Justice", "Chief Justice")
    # Separate writings sign 'Molter, J., concurring.' / 'Slaughter, J.,
    # dissenting.' — title-case surnames with the abbreviated title.
    allow_titlecase_name = True

    def prepare_document(self, pdf) -> None:
        """Detect PDFs whose font maps virtually every word space to NBSP.

        Shabazz contains 4,547 non-breaking-space glyphs and only seven
        ordinary spaces. Preserving those glyphs in justified HTML leaves the
        browser almost nowhere to wrap and makes the few legal break points
        expand across the line. A high document-level ratio distinguishes
        that broken encoding from occasional intentional NBSPs in other
        Indiana opinions.
        """
        super().prepare_document(pdf)
        nbsp = ordinary = 0
        sizes: Counter = Counter()
        for page in pdf.pages:
            for char in page.chars:
                text = char.get("text") or ""
                nbsp += text.count("\xa0")
                ordinary += text.count(" ")
                if text and not text.isspace():
                    sizes[round(char.get("size") or 0.0, 1)] += 1
        total = nbsp + ordinary
        self._normalize_dominant_nbsp = (
            nbsp >= 100 and total > 0 and nbsp / total >= 0.90
        )
        # The document's body type size, measured once over every glyph in the
        # file rather than page by page (see find_footnote_separator).
        self._doc_type_size = (
            float(sizes.most_common(1)[0][0]) if sizes else None
        )

    def correct_page_geometry(self, page) -> None:
        """Make a dominant NBSP encoding behave like ordinary word spaces."""
        if getattr(self, "_normalize_dominant_nbsp", False):
            for char in page.chars:
                if char.get("text") == "\xa0":
                    char["text"] = " "
        super().correct_page_geometry(page)

    @staticmethod
    def _outline_heading_start(text: str) -> bool:
        first = text.strip().split(maxsplit=1)[0] if text.strip() else ""
        return first in {
            "I.",
            "II.",
            "III.",
            "IV.",
            "V.",
            "A.",
            "B.",
            "C.",
            "D.",
            "E.",
        }

    def segment_lines(self, lines, page_width) -> list:
        """Keep tightly led wrapped outline headings in one segment."""
        segments = super().segment_lines(lines, page_width)
        out = []
        index = 0
        while index < len(segments):
            segment = segments[index]
            text = self.line_plain_text(segment[0]) if segment else ""
            if not segment or not self._outline_heading_start(text):
                out.append(segment)
                index += 1
                continue

            merged = list(segment)
            following = index + 1
            while following < len(segments):
                candidate = segments[following]
                if not candidate:
                    break
                gap = candidate[0]["top"] - merged[-1]["top"]
                candidate_text = self.line_plain_text(candidate[0])
                if (
                    not 0 < gap <= 28
                    or self._outline_heading_start(candidate_text)
                    or not all(
                        self._line_all_emphasized(line) for line in candidate
                    )
                ):
                    break
                merged.extend(candidate)
                following += 1
            out.append(merged)
            index = following
        return out

    def split_body_paragraphs(self, seg) -> list:
        """Split Indiana's shallow first-line indents from measured geometry.

        The current Indiana template sets continuation lines on the measured
        body rail (x=108) and paragraph openers only 14.4 points farther right.
        The shared 28-point threshold therefore joined every paragraph on a
        page.  Treat an offset between 2% and 8% of this document's measured
        text width as a first-line indent; deeper runs remain quotations or
        wrapped headings.
        """
        geom = getattr(self, "_doc_geom", None)
        if not seg or not geom:
            return super().split_body_paragraphs(seg)
        # A wrapped bold heading can increase its continuation indent for
        # centering.  It is one heading, not two shallow-indent paragraphs.
        if all(self._line_all_emphasized(line) for line in seg):
            return [seg]
        body_x0 = float(geom["body_x0"])
        measure = max(1.0, float(geom["right_x1"]) - body_x0)
        shallow_min = max(6.0, 0.02 * measure)
        shallow_max = max(24.0, 0.08 * measure)

        paragraphs = [[seg[0]]]
        for line in seg[1:]:
            offset = float(line["x0"]) - body_x0
            if shallow_min <= offset <= shallow_max:
                paragraphs.append([line])
            else:
                paragraphs[-1].append(line)
        paragraphs = self._explode_line_stacks(paragraphs)
        # Preserve the same measured shallow indent that proved each paragraph
        # boundary.  The base builder carries this private line annotation into
        # the block payload; only truly indented openers receive visual indent.
        for paragraph in paragraphs:
            if not paragraph:
                continue
            offset = float(paragraph[0]["x0"]) - body_x0
            if shallow_min <= offset <= shallow_max:
                paragraph[0]["_first_line_indent"] = round(offset, 1)
        return paragraphs

    def classify_paragraph(self, lines) -> str:
        """Indiana's short section headings are bold but left aligned."""
        if (
            lines
            and len(lines) <= 4
            and sum(len(self.line_plain_text(line).strip()) for line in lines) <= 220
            and all(self._line_all_emphasized(line) for line in lines)
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def find_footnote_separator(self, page) -> Optional[float]:
        """Indiana's separator, told from a caption divider by the TYPE under it.

        The shared ``_footnote_sep_small_text_below`` gets the idea right and
        the two measurements wrong, and both failures are visible in this
        corpus (13 rules across 10 of the 50 documents, every footnote on those
        pages lost to the body):

        * It compares the type below the rule against **the page's** modal
          glyph size. On a page carrying a long footnote the footnote type IS
          the mode — south_bend p19 is 375 glyphs at 9.5pt against 95 at 12pt —
          so the page reports a 9.5pt body and its own 9.5pt footnote reads as
          full size. The body size is a fact about the document, not a page:
          measured over every glyph in the file it is 12.0pt in all 50
          documents, and in all 239 rules here (``_doc_type_size``).
        * It fences the rule into the bottom 60% of the page. A footnote long
          enough to fill a page pushes its own rule up — edgerock's footnote 7
          rule sits at y=284 of 792 — and the fence rejects it. Position is not
          what makes a rule a separator; what makes it one is that the zone
          beneath it is TERMINAL: footnote-sized text directly under the rule
          and no body-sized text anywhere below it, all the way to the foot.
          A caption divider fails that on both counts, since the caption's next
          band is body-sized and there is more body below it still.

        Measured over the whole corpus, the two populations do not overlap:
        129 rules have footnote type under them and a terminal zone (every one
        the 144pt separator at the body rail), 11 have body type under them and
        body type below them (the title page's caption dividers and the
        in-text rules of edgerock/elzey), and 99 have no text within 22pt below
        (page furniture). No rule falls in between.
        """
        body = getattr(self, "_doc_type_size", None)
        if not body:
            return self._footnote_sep_small_text_below(page)
        # A footnote's type sits a clear step below the body's: the smallest
        # footnote type measured here is 9.96pt against a 12.0pt body, the
        # largest non-footnote type under a rule is 11.04pt. 1.5pt is the
        # midpoint of that gap and the same step ``_footnote_mark_chars`` uses
        # to call a glyph a footnote marker.
        limit = body - 1.5
        chars = [c for c in page.chars if not (c.get("text") or "").isspace()]
        if not chars:
            return None
        cands = []
        for rule in page.rects:
            if not (
                abs(rule.get("height") or 0.0) < 2.5
                and (rule["x1"] - rule["x0"]) >= 80
            ):
                continue
            band = [
                c
                for c in chars
                if rule["top"] < c["top"] < rule["top"] + self._fnsep_band
            ]
            if not band:
                continue
            # The line directly under the rule must be footnote-sized...
            if min(band, key=lambda c: c["top"]).get("size", 99.0) > limit:
                continue
            # ...and nothing body-sized may follow it down the page.
            if any(
                c["top"] > rule["top"] + 1 and (c.get("size") or 0.0) > limit
                for c in chars
            ):
                continue
            cands.append(rule["top"])
        return min(cands) if cands else None

    def extract(self, pdf_path):
        self._footer_dropped = []
        doc = super().extract(pdf_path)
        self._harvest_attorney_tail(doc)
        extra = list(dict.fromkeys(self._footer_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    @staticmethod
    def _plain_tail_heading(text: str) -> str:
        """Normalize spaced/marked-up Indiana counsel headings."""
        for tag in ("<strong>", "</strong>", "<em>", "</em>"):
            text = text.replace(tag, "")
        return "".join(ch for ch in text.upper() if ch.isalpha())

    def _harvest_attorney_tail(self, doc) -> None:
        """Move the final Indiana counsel roster out of the opinion body."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        start = next(
            (
                i
                for i, block in enumerate(op.blocks)
                if (
                    "ATTORNEYFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                    or "ATTORNEYSFOR"
                    in self._plain_tail_heading(str(block.text or ""))
                )
            ),
            None,
        )
        if start is None:
            return
        tail = op.blocks[start:]
        op.blocks = op.blocks[:start]
        doc.trailer = [
            str(block.text or "").strip()
            for block in tail
            if str(block.text or "").strip()
        ]

    def page_lines(self, page):
        lines = super().page_lines(page)
        if getattr(self, "_footer_dropped", None) is None:
            self._footer_dropped = []
        kept = []
        for ln in lines:
            t = self.line_plain_text(ln).strip()
            # Per-page footer ('Indiana Supreme Court | Case No. ... | Page
            # N of M') sits inside the text margins — furniture.
            if ln["top"] > 700 and t.startswith("Indiana Supreme Court"):
                self._footer_dropped.append(t)
                continue
            kept.append(ln)
        return kept

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        # Indiana types its per-curiam byline in title case ('Per curiam.'),
        # which the global ALL-CAPS matcher deliberately ignores.
        if " ".join(text.strip().rstrip(".").split()).lower() == "per curiam":
            return ("Per curiam", "per curiam", None)
        return None
