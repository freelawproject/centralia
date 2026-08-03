"""Ohio Court of Appeals.

Intermediate appellate court; the corpus spans two district print shops:

  * 2nd District (Arial): a FINAL JUDGMENT ENTRY cover page — its own
    Colon-Rail caption ('DAVID DODD :' / ': C.A. No. 2025-CA-42'), a dotted
    '. . . .' divider, the mandate text, and a 'For the court' conformed
    signature — then the opinion proper opens on page 2 under an 'OPINION'
    banner with counsel lines and a NON-bold byline ('HANSEMAN, J.').
  * 6th District (Times): no cover page — an Open-Range caption (two columns
    held by whitespace: parties left, docket/decision-date right of the page
    middle), '* * * * *' star dividers around the counsel block, and a bold
    byline ('SULEK, J.,' / 'MAYLE, J.,').

Both districts number body paragraphs '{¶ N}', double-space the body, and
single-space block quotes one indent step in. Footnotes are set at BODY size
(only the label digit is raised) under a short left-anchored separator, so the
structural separator test is used. Real bylines are ALL-CAPS surnames; quoted
trial-transcript speech ('Additionally, Judge, the State would have shown …')
matches the loose byline grammar and must be rejected by case.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class OhioCourtOfAppeals(StateAppellate):
    court_id = "ohioctapp"
    court_label = "Ohio Court of Appeals."

    # Footnotes at body size with a raised label digit — the 'smaller text
    # below the rule' test never fires; use the structural separator test.
    footnote_sep_structural = True

    # Double-spaced body, single-spaced quotes one 36pt step in (x0 72 -> 108);
    # the lower indent_step lets the segmenter split the quote off the body.
    blockquote_by_indent = True
    indent_step = 24

    def _footnote_sep_structural(self, page):
        sep = super()._footnote_sep_structural(page)
        if sep is None:
            return None
        for line in page.extract_text_lines():
            if line.get("top", 0) > sep and self.parse_author_line(
                (line.get("text") or "").strip()
            ):
                return None
        return sep

    # ------------------------------------------------------ margin furniture
    def extract(self, pdf_path):
        self._oh_dropped = []
        doc = super().extract(pdf_path)
        if self._oh_dropped:
            seen = set()
            uniq = [
                t for t in self._oh_dropped if not (t in seen or seen.add(t))
            ]
            doc.dropped = list(doc.dropped) + uniq
        return doc

    def _maybe_drop_running_header(self, page, lines):
        """2nd-district opinion pages open with a centered bold 'OPINION'
        banner and the '<COUNTY> C.A. No. <docket>' line right under it at
        the very top — the margin band naming the writing, not headmatter or
        body. Drop the pair into the Removed box."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number <= 1 or not lines:
            return lines
        ordered = sorted(lines, key=lambda l: l.get("top", 0))
        first = ordered[0]
        if not (
            self.line_plain_text(first).strip().upper() == "OPINION"
            and first.get("top", 999) < 90
            and first.get("x0", 0) > 200
        ):
            return lines
        drop = {id(first)}
        texts = [self.line_plain_text(first).strip()]
        if len(ordered) > 1:
            nxt = ordered[1]
            # the centered docket line sits one tight step below the banner
            if nxt["top"] - first["top"] < 20 and nxt.get("x0", 0) > 150:
                drop.add(id(nxt))
                texts.append(self.line_plain_text(nxt).strip())
        getattr(self, "_oh_dropped", []).extend(t for t in texts if t)
        return [l for l in lines if id(l) not in drop]

    # --------------------------------------------------------------- byline
    def parse_author_line(self, text):
        """Real bylines are ALL-CAPS surnames + abbreviated title
        ('HANSEMAN, J.' / 'SULEK, J.,' / 'MAYLE, J., concurring') or PER
        CURIAM. Quoted transcript speech ('Additionally, Judge, the State
        would have shown …') satisfies the loose spelled-title grammar, so
        reject title-case names (a real McFARLAND/DeWINE keeps ≥2 capitals)
        and any remainder that isn't concur/dissent language."""
        parsed = super().parse_author_line(text)
        if not parsed:
            return None
        name = parsed[0] or ""
        if sum(1 for ch in name if ch.isupper()) < 2:
            return None
        rest = parsed[2] if len(parsed) > 2 else None
        if rest:
            low = rest.lower()
            if "concur" not in low and "dissent" not in low:
                return None
        return parsed

    # ------------------------------------------------------------- captions
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        d = super().extract_headmatter(headmatter_segs, page1_rules)
        # 2nd District: the Colon Rail — fold 'PARTY :' / ': No. …' rows into
        # the two-column caption block.
        folded = self._fold_rail_caption(d["summary"], ":")
        if any(isinstance(r, dict) and r.get("__caption__") for r in folded):
            d["summary"] = folded
        else:
            # 6th District: the Open Range — two columns held by whitespace.
            # The caption closes at the first '* * * * *' counsel divider, so
            # cap the shared fold there (the counsel block must not fold in).
            stars = [
                l["top"]
                for seg in headmatter_segs
                for l in seg
                if set((l.get("text") or "").split()) == {"*"}
            ]
            d["summary"] = self._fold_open_caption(
                d["summary"],
                headmatter_segs,
                limit=min(stars) if stars else None,
            )
        return d
