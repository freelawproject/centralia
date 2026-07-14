"""Supreme Court of the State of Idaho.

Two-column `)`-delimited caption (like Alaska) but a standard byline-at-start
body ('MEYER, Justice.'), so the core pipeline handles the opinions.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


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

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Fold the ')'-railed caption (like Alaska) into a two-column block
        so the centered rail holds the party / docket columns apart."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d

    # Bullet glyphs Idaho uses to mark list items (hanging-indent lists).
    _BULLET_GLYPHS = "•▪◦‣●○"

    def _is_bullet_line(self, line) -> bool:
        t = (line.get("text") or "").lstrip()
        return bool(t) and t[0] in self._BULLET_GLYPHS

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
        if not seg or not any(self._is_bullet_line(l) for l in seg):
            return super().split_body_paragraphs(seg)
        seg_left = min(l["x0"] for l in seg)
        indent_min = max(self.body_baseline_x0, seg_left) + self.para_indent_min
        paras = [[seg[0]]]
        in_item = self._is_bullet_line(seg[0])
        for line in seg[1:]:
            x0 = line["x0"]
            if self._is_bullet_line(line):
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
