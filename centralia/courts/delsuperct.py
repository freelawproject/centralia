"""Delaware Superior Court.

Trial court; single ruling by one judge, district-court model (the whole
ruling is one opinion). The author signs '/s/ Name' beside a state title
line ('Charles E. Butler, Resident Judge' / 'Judge Sonia Augusthy') the
federal title list doesn't know; some orders carry only a handwritten
signature image, in which case no text names the judge and the author
stays empty.

delsuperct quirk — INVISIBLE FOOTNOTE ANCHORS. Several of these orders are
produced by a word processor that emits, beside every footnote reference, a
1-POINT anchor glyph pair in a second face ('1F', '2F' in Cambria at size 1.0)
sitting on its own baseline a few points below the marked line. At 1pt it is
invisible on the page, but the line merger folds it into the body line beside
it and corrupts the text ('… run concurrently.' becomes '… run
concurrently.1F2'), after which the line matches nothing and the paragraph
reads as lost. The anchors are removed in ``correct_page_geometry`` so the
completeness audit reads the page exactly as the extractor does.
"""

from __future__ import annotations

from ._district import DistrictBase

# No readable text is set below this; anything smaller is a layout artifact.
_INVISIBLE_PT = 3.0


class DelawareSuperiorCourt(DistrictBase):
    court_id = "delsuperct"
    court_label = "Delaware Superior Court."

    def correct_page_geometry(self, page) -> None:
        """Drop the word processor's 1-point footnote-anchor glyphs before any
        line clustering — they carry no reading content and, left in place,
        merge into the body line beside them and corrupt it."""
        chars = page.chars
        for i in range(len(chars) - 1, -1, -1):
            if (chars[i].get("size") or 99) < _INVISIBLE_PT:
                del chars[i]
        super().correct_page_geometry(page)

    def _caption_char_runs(self, line):
        """Caption char runs split at the ')' GLYPH RAIL, not at wide word gaps.

        These captions are set on a typewriter grid and justified out to the
        rail, so a single party name can carry interior word gaps wider than the
        generic column-gap threshold ('MENA PEREZ, her Husband, and    as   )').
        Split there, the name was torn in half and its tail was filed in the
        docket column opposite ('… her Husband, and' | 'as'), where it matched
        nothing in the source and read as lost caption text.

        The rail is the column boundary the page actually draws, so split on the
        rail and leave ordinary word spacing alone. Gated on the caption
        fingerprint's rail glyph and its y-band, so a parenthesis in prose below
        the caption is never treated as a column edge.
        """
        sig = (getattr(self, "_caption_fp", None) or (None,))[0] or {}
        rail = sig.get("rail")
        band = sig.get("rail_band")
        chars = line.get("chars") or []
        if not rail or not chars:
            return super()._caption_char_runs(line)
        if band and not (band[0] - 6 <= line.get("top", 0) <= band[1] + 6):
            return super()._caption_char_runs(line)
        if not any((c.get("text") or "") == rail for c in chars):
            return super()._caption_char_runs(line)
        runs, cur = [], []
        for c in chars:
            if (c.get("text") or "") == rail:
                if cur:
                    runs.append(cur)
                runs.append([c])
                cur = []
            else:
                cur.append(c)
        if cur:
            runs.append(cur)
        trimmed = []
        for r in runs:
            while r and not (r[0].get("text") or "").strip():
                r.pop(0)
            while r and not (r[-1].get("text") or "").strip():
                r.pop()
            if r:
                trimmed.append(r)
        return trimmed

    def _pleading_gutter_by_numbers(self, page):
        """Right edge of a pleading-paper line-number gutter, or None.

        Delaware opinions cite in footnotes, so a busy page stacks eight-plus
        label numerals hard against the left margin down the footnote zone —
        the same shape the shared pleading-paper heuristic hunts for (a
        far-left run of ascending integers). Read as a line-number gutter it
        filtered away every glyph left of the labels' right edge, clipping the
        leading characters off EVERY body line on the page. A real rail is
        distinguished by three structural properties it always has and a
        footnote-label column never does:

        * it numbers every typed line, so it is DENSE (>= 14 numerals a page);
        * it runs the full text block, so it SPANS most of the sheet;
        * it is absolute, so it STARTS AT 1 (or 2, when the header eats one).
        """
        nums = [
            (int(w["text"]), w["x1"], w["top"])
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if len(nums) < 14:
            return None
        tops = [n[2] for n in nums]
        if (max(tops) - min(tops)) < page.height * 0.55:
            return None
        if min(n[0] for n in nums) > 2:
            return None
        return super()._pleading_gutter_by_numbers(page)

    def _signature_author(self, all_segments):
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            if not lines[i].lower().startswith("/s"):
                continue
            name = lines[i]
            for pre in ("/s/", "/S/", "/s", "/S"):
                if name.startswith(pre):
                    name = name[len(pre) :].strip()
                    break
            # Prefer the adjacent name+title line ('Paul R. Wallace, Judge');
            # a bare title line ('Resident Judge') combines with the /s/ name.
            for j in (i + 1, i - 1):
                if 0 <= j < len(lines):
                    t = lines[j]
                    if len(t) < 60 and any(
                        w in t.lower() for w in ("judge", "commissioner", "justice")
                    ):
                        title_words = {
                            "judge", "resident", "president", "commissioner",
                            "justice", "chief", "the", "honorable",
                        }
                        toks = [w.strip(".,").lower() for w in t.split()]
                        if toks and all(w in title_words for w in toks):
                            return f"{name}, {t}" if name else t
                        return t
            return name or None
        return super()._signature_author(all_segments)
