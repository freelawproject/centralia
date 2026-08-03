"""Supreme Court of the State of Idaho.

Two-column `)`-delimited caption (like Alaska) but a standard byline-at-start
body ('MEYER, Justice.'), so the core pipeline handles the opinions.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, is_caps_name

# The abbreviated titles Idaho uses on a separate-writing byline.
_SEPARATE_TITLES = {"J": "Justice", "CJ": "Chief Justice"}


def _separate_byline(text: str):
    """Parse an in-body separate-writing byline — 'ZAHN, J., dissenting.' /
    'MEYER, J., specially concurring.' — into (name, title, kind), else None.

    The lead opinion signs itself with the full title ('BEVAN, Chief Justice.',
    handled by the shared base); a separate writing uses the ABBREVIATED title
    and names its kind. Three commas-separated fields, an ALL-CAPS surname and a
    'concurring'/'dissenting' kind together make this specific enough that
    ordinary prose and the 'Justices BRODY, MOELLER … concur.' roster line above
    it cannot match."""
    t = (text or "").strip()
    if not t.endswith("."):
        return None
    parts = [p.strip() for p in t[:-1].split(",")]
    if len(parts) < 2:
        return None
    title = _SEPARATE_TITLES.get(parts[1].replace(".", "").upper())
    if not title or not is_caps_name(parts[0]):
        return None
    if len(parts) == 2:
        return parts[0], title, None
    kind_text = " ".join(parts[2:]).lower()
    has_c, has_d = "concurring" in kind_text, "dissenting" in kind_text
    if has_c and has_d:
        kind = "concurring in part and dissenting in part"
    elif has_d:
        kind = "dissenting"
    elif has_c:
        kind = "concurring"
    else:
        return None
    return parts[0], title, kind


class IdahoSupreme(StateSupreme):
    court_id = "idaho"
    court_label = "Supreme Court of the State of Idaho."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers
    author_titles = ("Justice", "Chief Justice", "Pro Tem Justice",
                     # Court of Appeals opinions appear in the corpus
                     "Judge", "Chief Judge", "Judge Pro Tem")

    # Idaho sets the body at 1.5 leading (~21pt) and single-spaces block quotes
    # / footnotes at ~14pt. The default bands (single<22) read the 21pt body as
    # a block quote; shift them down so 14→single and 21→body (see idahoctapp).
    gap_tight_max = 11
    gap_single_max = 17

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is None or page.page_number != 1:
            return sep
        # A long Idaho caption/counsel block can put its bottom rule in the
        # lower half of page 1.  If a real judicial byline occurs below that
        # rule, the rule closes headmatter; it does not open footnotes.
        for line in page.extract_text_lines():
            if line.get("top", 0) <= sep:
                continue
            if self.parse_author_line((line.get("text") or "").strip()):
                return None
        return sep

    def find_authors(self, all_segments) -> list:
        """Idaho bylines may be in a tight segment classified as notice.

        They remain structurally unambiguous (``ZAHN, Justice.`` or the
        all-caps abbreviated ``ZAHN, J.``), so do not let the gap label hide
        the entire opinion in headmatter.
        """
        out = []
        for index, (_page, segment, _kind) in enumerate(all_segments):
            if segment and self.parse_author_line(
                self.line_plain_text(segment[0]).strip()
            ):
                out.append(index)
        return out

    # ------------------------------------------------- separate-writing byline
    def parse_author_line(self, text):
        sep = _separate_byline(text)
        if sep is not None:
            return sep
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if _separate_byline(text) is not None:
            # The byline stands alone on its row; no body text follows it.
            return text, ""
        return super()._byline_split(line)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Fold the ')'-railed caption (like Alaska) into a two-column block
        so the centered rail holds the party / docket columns apart."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d

    # Bullet glyphs Idaho uses to mark list items (hanging-indent lists).
    _BULLET_GLYPHS = "•▪◦‣●○"

    def correct_page_geometry(self, page) -> None:
        """Blank the bullet MARKER glyph and remember where it sat.

        A bulleted item prints its marker in a column one indent step inside
        the body margin (x0 90) with the item text hanging at 108. The marker
        is drawn furniture — the structured list the renderer draws supplies
        its own marker — so keeping the glyph in the item text would print it
        twice. Blanking the glyph *here* (rather than stripping it off the
        paragraph text later) means the coverage sweep and the audit read the
        page the same way the extractor does, so a list item no longer reads as
        an unplaced source line. The blank keeps the char in place, so the
        marker column still measures at x0 90 and the hanging-indent geometry
        the paragraph splitter relies on is untouched."""
        super().correct_page_geometry(page)
        try:
            chars = page.objects.get("char") or []
        except Exception:
            return
        tops = self._bullet_tops.setdefault(page.page_number, set())
        for c in chars:
            if (c.get("text") or "") in self._BULLET_GLYPHS:
                c["text"] = " "
                tops.add(round(c.get("top", 0.0), 1))

    # page number -> tops of the rows whose bullet marker was blanked
    _bullet_tops: dict = {}

    def prepare_document(self, pdf) -> None:
        # The extractor instance is reused across a corpus; the marker rows are
        # per document.
        self._bullet_tops = {}
        super().prepare_document(pdf)

    def page_lines(self, page):
        lines = super().page_lines(page)
        # A bullet glyph's box sits a couple of points below the row's cap
        # height, so tag the nearest row to each recorded marker rather than
        # keying on an exact top.
        for t in self._bullet_tops.get(page.page_number) or ():
            row = min(
                (l for l in lines if abs(l.get("top", 0.0) - t) <= 8.0),
                key=lambda l: abs(l.get("top", 0.0) - t),
                default=None,
            )
            if row is not None:
                row["_bullet_item"] = True
        return lines

    def _is_bullet_line(self, line) -> bool:
        return bool(line.get("_bullet_item"))

    def _is_numbered_list_line(self, line) -> bool:
        text = (line.get("text") or "").lstrip()
        marker = text.split(maxsplit=1)[0] if text else ""
        # Idaho list markers occupy a narrow column one indent-step inside the
        # body margin. This excludes paragraph-leading numbered citations and
        # numbered headings at other alignments.
        marker_column = (
            self.body_baseline_x0 + 12
            <= line["x0"]
            <= self.body_baseline_x0 + 30
        )
        return (
            marker_column
            and marker.endswith(".")
            and marker[:-1].isdigit()
        )

    def _is_list_line(self, line) -> bool:
        return self._is_bullet_line(line) or self._is_numbered_list_line(line)

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        # Tight leading and short list rows can otherwise alternate between
        # body, single, and blockquote. The marker-column geometry is the more
        # reliable structural signal.
        return "body" if any(self._is_list_line(line) for line in seg) else kind

    def classify_paragraph(self, lines) -> str:
        if lines and self._is_bullet_line(lines[0]):
            return "list-item"
        if lines and self._is_numbered_list_line(lines[0]):
            return "ordered-list-item"
        return super().classify_paragraph(lines)

    def paragraph_text(self, lines) -> str:
        text = super().paragraph_text(lines)
        if lines and self._is_bullet_line(lines[0]):
            # The structured renderer supplies the list marker. Keep the item
            # content, including its inline quotation/italic formatting.
            text = text.lstrip()
            if text and text[0] in self._BULLET_GLYPHS:
                text = text[1:].lstrip()
        return text

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # A numbered subsection label can occupy the same marker column as an
        # ordered list item. Lists form runs; an isolated numbered block does
        # not. Keep isolated labels as ordinary paragraphs, including their
        # printed number.
        i = 0
        while i < len(op.blocks):
            if op.blocks[i].kind != "ordered-list-item":
                i += 1
                continue
            end = i + 1
            while (
                end < len(op.blocks)
                and op.blocks[end].kind == "ordered-list-item"
            ):
                end += 1
            if end - i == 1:
                op.blocks[i].kind = "p"
            i = end
        return op

    def split_body_paragraphs(self, seg) -> list:
        """Bullet-aware paragraph splitting.

        Idaho sets bulleted lists with a hanging indent: the '•' marker sits a
        little in from the body margin (x0≈90) and each item's wrapped
        continuation lines sit deeper still (the text column, x0≈108). The
        default splitter reads the marker as *below* the paragraph-indent
        threshold (so it folds up into the preceding prose) and every
        continuation line as *above* it (so each becomes its own paragraph) —
        the list comes out scrambled. Here a '•' line opens a fresh list item,
        its indented continuations fold into that item, and a return to the
        body margin ends the item. Segments with no bullet fall back to the
        default behavior untouched."""
        if not seg or not any(self._is_list_line(l) for l in seg):
            return super().split_body_paragraphs(seg)
        seg_left = min(l["x0"] for l in seg)
        indent_min = max(self.body_baseline_x0, seg_left) + self.para_indent_min
        paras = [[seg[0]]]
        in_item = self._is_list_line(seg[0])
        for line in seg[1:]:
            x0 = line["x0"]
            if self._is_list_line(line):
                paras.append([line])
                in_item = True
            elif in_item:
                if x0 > seg_left + 6:  # wrapped continuation of the item
                    paras[-1].append(line)
                else:  # back at the body margin: the list item has ended
                    paras.append([line])
                    in_item = False
            elif x0 > indent_min:  # a first-line indent: new body paragraph
                paras.append([line])
            else:  # wrapped body continuation
                paras[-1].append(line)
        return paras
