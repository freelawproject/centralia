"""United States Court of Appeals for the Sixth Circuit."""

from __future__ import annotations

from ._circuit import (
    FederalCircuitBase,
    _plain,
)

_BOX = {"│", "┐", "┘", "┌", "└", "├", "┤", "┬", "┴", "┼"}
# The '>' the published template sets at the docket cell is part of the same
# drawn rail, and arrives HTML-escaped in the cell text.
_RAIL_LEAD = ("&gt;", ">")




def _strip_rail(text: str, glyph: str) -> str:
    """Remove a leading/trailing rail glyph from one caption cell, leaving the
    cell's own text. Only the glyph itself is shed — a ')' that closes real
    text ('(18-8010),') is never touched because it is not leading or
    trailing on its own."""
    t = text.strip()
    # A rail-only cell arrives wrapped in its own markup
    # ('<centered>)</centered>'), so the glyph is not at the string's edges.
    # Judge emptiness on the TEXT, not the markup.
    plain = _plain(t).strip()
    for lead in _RAIL_LEAD:
        if plain.startswith(lead):
            plain = plain[len(lead):].strip()
    # Shed EVERY box-drawing glyph, not only the one the divider matched: the
    # rail's corners ('┐' at the top, '┘' at the bottom) are the same drawn
    # bracket as the '│' between them, and were surviving in the column.
    if not plain.strip(glyph + "".join(_BOX) + " "):
        return ""
    for lead in _RAIL_LEAD:
        if t.startswith(lead):
            t = t[len(lead):].strip()
    while t.startswith(glyph):
        t = t[len(glyph):].strip()
    while t.endswith(glyph):
        t = t[: -len(glyph)].strip()
    return t


class SixthCircuit(FederalCircuitBase):
    court_id = "ca6"
    court_label = "United States Court of Appeals for the Sixth Circuit."
    circuit_phrase = "sixth circuit"

    # Headmatter criteria: drawn divider then a caption BLOCK; COUNSEL under its own heading.
    parse_criteria_enabled = True

    def _is_disposition(self, text):
        """CA6 states who wrote what in a row of its own under the roster:

            CLAY, J., delivered the opinion of the court in which COLE, J.,
            concurred.  THAPAR, J. (pp. 16–17), delivered a separate
            dissenting opinion.

        It reads like a byline and names judges like a roster, so without a
        field of its own it was left out of the criteria entirely. The court's
        formula is always 'delivered' — the opinion of the court, or a
        separate one."""
        low = " ".join(text.split()).lower()
        return "delivered the opinion" in low or "delivered a separate" in low
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0

    # CA6 prints a one-line running head on every continuation page —
    # 'No. 25-1802 Ross v. Robinson, Hoover & Fink Page 2' — and sets it at two
    # heights: top~55.8 in the published measure (body at ~97) and top~45.0 in
    # the slip measure (body at ~84). The family's blanket 95pt cutoff cleared
    # the head on the first but ate the FIRST LINE of every page on the second —
    # body prose, section heads ('II. DISCUSSION'), and a whole dissent byline
    # ('THAPAR, Circuit Judge, dissenting.'). Bound the head by the band it
    # actually occupies and record it as furniture; leave the cutoff at the page
    # edge so nothing else above the body is removed.
    page2_header_cutoff = 30.0
    running_head_max_top = 70.0

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        return self._drop_head_band(page, lines)

    def find_caption_divider(self, page):
        """CA6 draws the caption box with Unicode box-drawing chars — or, on
        part of the corpus, with a stacked ')' glyph rail instead.

        Both are the same structure and only the glyph differs, so try the box
        characters first and fall back to the paren rail. Without the fallback
        the paren-railed captions got no divider at all, so their two columns
        were never split and ``extract_text`` merged them onto single rows
        ('Petitioner, ) ) ON PETITION FOR REVIEW v. ) FROM THE UNITED STATES')."""
        from collections import Counter

        def rail(chars, floor):
            if len(chars) < floor:
                return None
            x, _ = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
            column = [c for c in chars if abs(c["x0"] - x) < 3]
            if len(column) < floor:
                return None
            top = min(c["top"] for c in column)
            bottom = max(c["bottom"] for c in column)
            return float(x), top - 2, bottom + 2

        box = [c for c in page.chars if c.get("text") in _BOX]
        found = rail(box, 3)
        if found is not None:
            self._ca6_rail = "│"
            return found
        # A paren rail needs a taller floor than the box glyphs: ')' occurs in
        # ordinary prose, so require a real stack before treating it as the
        # caption's divider.
        found = rail([c for c in page.chars if c.get("text") == ")"], 6)
        if found is not None:
            self._ca6_rail = ")"
            return found
        # Deliberately NOT cleared here: this runs per page, and only the
        # caption page carries a rail. Clearing on a later page wiped what
        # page 1 found. Reset per document in ``extract`` instead.
        return super().find_caption_divider(page)

    def extract(self, pdf_path):
        self._ca6_rail = None
        return super().extract(pdf_path)


    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Record the rail the caption is actually drawn with, and take its
        glyphs out of the column cells.

        Whether a rail glyph fell inside a cell was pure accident: the column
        split keeps chars left of the divider or right of it, so a glyph whose
        x0 landed exactly on the divider went to the right column while an
        identical one a hair left of it did not. The same corpus therefore had
        captions with ')' repeated down the right column and captions with
        none. The glyph is the drawn divider, so it belongs in ``rail`` — which
        was never set at all, leaving the renderer no way to reproduce a rail
        the page really draws."""
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        glyph = getattr(self, "_ca6_rail", None)
        if not glyph:
            return result

        def clean(cell):
            if isinstance(cell, dict):
                out = dict(cell)
                out["h"] = _strip_rail(str(cell.get("h", "")), glyph)
                return out
            return _strip_rail(str(cell), glyph)

        rows = []
        for row in result.get("summary", []):
            if isinstance(row, dict) and row.get("__caption__"):
                row = dict(row)
                row["rail"] = glyph
                for side in ("left", "right"):
                    row[side] = [clean(c) for c in (row.get(side) or [])]
                # Once the rail glyphs are gone, the rows that held nothing but
                # the bracket's lower run are empty on BOTH sides. They are not
                # the caption's own vertical rhythm — they are what the rail
                # occupied — so trailing empties would render as phantom blank
                # rows below the parties.
                left, right = row.get("left") or [], row.get("right") or []
                width = max(len(left), len(right))
                left += [""] * (width - len(left))
                right += [""] * (width - len(right))

                def _blank(cell):
                    text = cell.get("h", "") if isinstance(cell, dict) else cell
                    return not _plain(text).strip()

                while left and _blank(left[-1]) and _blank(right[-1]):
                    left.pop()
                    right.pop()
                row["left"] = self._join_column(left, headmatter_segs, "L")
                row["right"] = right
            rows.append(row)
        result["summary"] = rows
        return result



    def skip_headmatter_segment(self, seg) -> bool:
        if seg:
            t = (seg[0].get("text") or "").strip().upper()
            if t.startswith(
                (
                    "RECOMMENDED FOR PUBLICATION",
                    "NOT RECOMMENDED FOR PUBLICATION",
                    "PURSUANT TO SIXTH CIRCUIT",
                    "FILE NAME:",
                )
            ):
                return True
        return super().skip_headmatter_segment(seg)
