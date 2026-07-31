"""United States District Court, Northern District of Ohio.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

ohnd quirk — UNDERLINED CASE NAMES. Several judges here underline citations
instead of italicising them, so a single page of analysis draws a dozen thin
horizontal rules at the body margin, each as wide as the case name above it.
The generic separator scan looks for "a thin rule near the body margin in the
bottom half of the page with text below it" and takes the topmost — which on
these pages is an underline two-thirds of the way up. Everything below it is
then read as footnote flow, so whole paragraphs of analysis disappear from the
opinion and the real footnotes underneath the true separator are lost with
them (page 4 of 325029 lost seven consecutive lines this way).

The structural difference is unambiguous and needs no text: an underline is
drawn *inside* the vertical extent of the line it underlines (2.4pt above that
line's bottom, overlapping its x-span). A footnote separator has no text line
straddling it. ``find_footnote_separator`` hides the underlines and re-runs the
shared scan, so all the base's own discrimination still applies.
"""

from __future__ import annotations

from ._district import DistrictBase


class NorthernDistrictOfOhio(DistrictBase):
    court_id = "ohnd"
    court_label = "United States District Court, Northern District of Ohio."

    # A rule this far outside a text line's box still counts as that line's
    # underline; beyond it, the rule stands on its own.
    _UNDERLINE_SLACK = 1.0

    def _text_line_boxes(self, page):
        """(top, bottom, x0, x1) for every text line on ``page``, cached per
        page object so the underline test costs one layout pass."""
        cache = getattr(self, "_tl_cache", None)
        if cache is None:
            cache = self._tl_cache = {}
        key = id(page)
        if key not in cache:
            cache[key] = [
                (l["top"], l["bottom"], l["x0"], l["x1"])
                for l in page.extract_text_lines()
                if (l.get("text") or "").strip()
            ]
        return cache[key]

    def _straddled_by_text(self, page, top) -> bool:
        """True if a text line's own box encloses the height ``top`` — i.e. a
        rule drawn there is that line's underline, not a separator."""
        slack = self._UNDERLINE_SLACK
        return any(
            t - slack <= top <= b + slack
            for t, b, _x0, _x1 in self._text_line_boxes(page)
        )

    def _is_citation_underline(self, page, obj) -> bool:
        """True if ``obj`` is a thin horizontal rule drawn as the underline of a
        text line: it lies within that line's own vertical box and covers most
        of the rule's width horizontally."""
        if obj.get("object_type") not in ("rect", "line"):
            return False
        if abs(obj.get("height", 0)) >= 2.5:
            return False
        width = obj["x1"] - obj["x0"]
        if width <= 0:
            return False
        slack = self._UNDERLINE_SLACK
        for top, bottom, x0, x1 in self._text_line_boxes(page):
            if not (top - slack <= obj["top"] <= bottom + slack):
                continue
            if (min(obj["x1"], x1) - max(obj["x0"], x0)) > 0.5 * width:
                return True
        return False

    def find_footnote_separator(self, page):
        """The shared scan, re-run on a page whose citation underlines are
        hidden. Only re-runs when the scan's own answer *is* an underline, so a
        page whose separator the base already reads correctly is untouched."""
        sep = super().find_footnote_separator(page)
        if sep is None or not self._straddled_by_text(page, sep):
            return sep
        bare = page.filter(lambda o: not self._is_citation_underline(page, o))
        return super().find_footnote_separator(bare)
