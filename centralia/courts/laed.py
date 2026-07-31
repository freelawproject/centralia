"""United States District Court, Eastern District of Louisiana.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Two things about this district's page 1 defeat the shared measurements:

* Its rulings carry *numbered footnotes on every page* — chambers style here
  cites almost entirely in footnotes — and the labels are set at the left text
  margin as a stack of plain integers ("4", "5", "6", …). That stack looks
  exactly like the line-number rail of California pleading paper to the shared
  scan, which then discards every glyph left of the stack's right edge and
  shears the opening characters off each full-measure body line ("complaint" ->
  "plaint"). ``_pleading_gutter_by_numbers`` re-tests the stack's extent.
* The caption is an Open Range (parties left, "CIVIL ACTION / CASE NO. /
  SECTION" right, held apart by whitespace alone) or an asterisk rail — never a
  parenthetical rail. But the body opens with a long string of corporate
  short-name definitions, and their closing parens stack up in one 8pt column
  ('("Mars"),' / '("Chevron"),' / '("LOCAP"),'), which the caption fingerprint
  reads as a ')' glyph rail running to mid-page. The caption band then swallows
  page 1, the opinion is made to start on page 2, and the whole first page of
  prose is rendered as caption rows. ``caption_page`` hides those parens from
  the fingerprint.
"""

from __future__ import annotations

from ._district import DistrictBase

# The glyphs the caption fingerprint will accept as a rail column. Kept in step
# with ``captionfp._RAIL_CHARS``; only these need the isolation test.
_RAIL_CHARS = frozenset(")]§:*}|(")


class EasternDistrictOfLouisiana(DistrictBase):
    court_id = "laed"
    court_label = "United States District Court, Eastern District of Louisiana."

    # ------------------------------------------------- caption fingerprint
    def caption_page(self, pdf):
        """The caption page as the fingerprint should see it: with rail glyphs
        that are *punctuation* rather than *furniture* hidden.

        A caption glyph rail is a column of lone characters — each one stands in
        white space, with the party name well to its left and the docket well to
        its right. A closing paren inside body prose touches the word it closes.
        Testing that gap is the structural difference between the two, and it is
        the only thing that separates this court's Open Range caption from a
        Parenthetical Box. Nothing is *removed from the document* here: this
        filtered page is used only to measure page-1 geometry (drawn rules,
        caption box, fingerprint), never to read text."""
        page = super().caption_page(pdf)
        if page is None:
            return None
        loose = self._isolated_rail_glyphs(page)

        def keep(obj):
            if obj.get("object_type") != "char":
                return True
            if (obj.get("text") or "") not in _RAIL_CHARS:
                return True
            return id(obj) in loose

        return page.filter(keep)

    @staticmethod
    def _isolated_rail_glyphs(page):
        """ids of the rail-candidate chars on ``page`` that stand alone — no
        inked glyph within 4pt to their left or right on the same baseline."""
        by_baseline = {}
        for c in page.chars:
            if (c.get("text") or "").strip():
                by_baseline.setdefault(round(c["top"] / 3), []).append(c)
        loose = set()
        for c in page.chars:
            if (c.get("text") or "") not in _RAIL_CHARS:
                continue
            key = round(c["top"] / 3)
            neighbours = (
                by_baseline.get(key - 1, [])
                + by_baseline.get(key, [])
                + by_baseline.get(key + 1, [])
            )
            touching = any(
                d is not c
                and abs(d["top"] - c["top"]) <= 3
                and (0 <= c["x0"] - d["x1"] < 4 or 0 <= d["x0"] - c["x1"] < 4)
                for d in neighbours
            )
            if not touching:
                loose.add(id(c))
        return loose

    def _pleading_gutter_by_numbers(self, page):
        """The shared no-rule fallback, gated on the number stack spanning the
        page the way a pleading rail does.

        A pleading rail is printed 1, 2, 3 … 28 from the top margin to the
        bottom, so its integers begin high on the sheet and span nearly its
        whole height. A footnote-label column begins *below the footnote
        separator* — the bottom quarter or third — and spans a couple of inches
        at most. Measuring the stack's extent tells the two apart without
        looking at any text."""
        gx = super()._pleading_gutter_by_numbers(page)
        if gx is None:
            return None
        tops = [
            w["top"]
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if not tops:
            return None
        starts_high = min(tops) < page.height * 0.35
        spans_page = (max(tops) - min(tops)) > page.height * 0.6
        return gx if (starts_high and spans_page) else None
