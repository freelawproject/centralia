"""Massachusetts Appeals Court.

Two document classes come out of this court.

A **published opinion** prints the same slip-opinion front matter as the Supreme
Judicial Court — the publication NOTICE, the 'Present: NAME, ... JJ.' panel, and
the reporter headnotes — so it reuses the shared :class:`MassachusettsStyle`
(NOTICE -> dropped, headnotes -> syllabus, per-curiam order handling, page-number
folding). The author byline opens each opinion ('NAME, J.' / 'NAME, Judge.'); the
appellate base reuses the abbreviated-title parser and drops the trial-judge /
panel-roster caption lines.

A **summary decision under M.A.C. Rule 23.0** (formerly rule 1:28) is a different
animal and needs the handling below. It is an unsigned panel memorandum: no
'Present:' panel, no reporter headnotes, and no author byline anywhere. Page one
runs caption straight into body at one uniform double-spaced pitch, so the shared
segmenter — which cuts on the gaps a page leaves — has nothing to cut on and
hands back the caption and the opening paragraphs as a single segment. The
opinion-start scan reads each segment's first line, sees 'COMMONWEALTH OF
MASSACHUSETTS', and finds no start at all; the whole decision then stayed in
headmatter. The page does draw the boundary the pitch withholds: the title
'MEMORANDUM AND ORDER PURSUANT TO RULE 23.0' is centered and underlined with a
drawn rule, and the body opens on the line beneath it.

The decision closes on a signature block set in its own right-hand column — the
disposition ('So ordered.' / 'Judgments affirmed.'), 'By the Court (NAME, NAME &
NAME, JJ.),' and 'Clerk' — followed by 'Entered: <date>.' back at the left
margin. That is a sign-off, not prose, so it is lifted into ``signature`` rather
than left to trail the opinion body.
"""

from __future__ import annotations

from html import unescape

from ._appellate import StateAppellate
from ._massachusetts import MassachusettsStyle

# The title of a summary decision, which is also the boundary between its
# caption and its body. Both the current rule and the one it replaced are
# spelled 'MEMORANDUM AND ORDER PURSUANT TO RULE <n>', so the anchor is the
# stem; the geometry (centered, fully underlined) carries the rest of the
# identification.
_RULE23_TITLE = "memorandum and order"

def _plain_words(text) -> list:
    """A block's words as the page set them: inline markup removed and
    entities resolved, so a built block can be compared against a source
    line."""
    out, depth = [], 0
    for ch in str(text or ""):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return unescape("".join(out)).split()


class MassachusettsAppealsCourt(MassachusettsStyle, StateAppellate):
    court_id = "massappct"
    court_label = "Massachusetts Appeals Court."
    # Class defaults so a caller that reaches ``page_lines`` without going
    # through ``extract`` still reads clean (``_district`` does the same).
    _rule23_body = None
    _sig_rows: dict = {}

    def extract(self, pdf_path):
        self._rule23_body = None
        self._sig_rows = {}
        doc = super().extract(pdf_path)
        if self._rule23_body is not None:
            self._harvest_panel_signature(doc)
        return doc

    # ------------------------------------------------- Rule 23.0 body start
    def _is_rule23_title(self, page, line, page_width) -> bool:
        """The centered, ruled 'MEMORANDUM AND ORDER ...' title.

        Three cues have to agree, because page one carries other underlined
        text: the notice underlines its citation ('Chace v. Curran') and the
        caption underlines 'vs.'. Only the title is centered AND ruled across
        its whole measure AND opens with the rule's own name.

        The rule is measured against the line's own vertical band rather than
        read off the ``_underline`` char tags, because those tags assume the
        text and the graphics are registered to each other and in this court
        they are not always: nancy_white and dicostanzo set their text 5.9pt
        lower than pena's while drawing the identical rule at the identical
        y, which puts it 5.4pt ABOVE the glyph bottoms instead of 0.5pt below.
        Every underline in both documents went untagged, so a test built on the
        tags found no title and left two summary decisions unparsed. What
        identifies the rule is that it spans this line and no other.
        """
        text = self.line_plain_text(line).strip()
        if not text.lower().startswith(_RULE23_TITLE):
            return False
        if self.line_alignment(line, page_width) != "C":
            return False
        chars = [c for c in (line.get("chars") or []) if (c.get("text") or "").strip()]
        if not chars:
            return False
        top = min(c["top"] for c in chars)
        bottom = max(c["bottom"] for c in chars)
        return any(
            abs(r.get("height", 0)) < 2
            and abs(r["x0"] - line["x0"]) <= 2
            and abs(r["x1"] - line["x1"]) <= 2
            and top <= r["top"] <= bottom + 3
            for r in list(page.rects) + list(page.lines)
        )

    def page_lines(self, page):
        """Break page one's single segment at the summary-decision title.

        The caption and the opening paragraph are the same size, the same
        leading and one double-spaced line apart, so the shared segmenter joins
        them and the opinion start disappears inside the segment. The rule under
        the title is drawn geometry, so cutting there follows the page rather
        than inventing a boundary. (``caed`` cuts its pleading caption on the
        same principle.)
        """
        lines = super().page_lines(page)
        width = getattr(page, "width", 612.0) or 612.0
        self._record_right_column(page.page_number, lines, width)
        if page.page_number != 1:
            return lines
        title = None
        for line in lines:
            if self._is_rule23_title(page, line, width):
                title = line
        if title is None:
            return lines
        # The break goes ABOVE the title, not below it: the title is the
        # decision's own heading and opens the opinion, exactly as 'ORDER' does
        # on a district ruling. Everything above it — court, docket, parties —
        # is the caption.
        title["_seg_break"] = True
        self._rule23_body = (page.page_number, round(title["top"], 1))
        return lines

    def _page1_rules(self, p1) -> list:
        """Keep the title's own rule out of the caption's dividers.

        That rule decorates the title, and the title opens the opinion, so it
        is not a divider in the caption at all. The shared collector already
        excludes text underlines, but it recognises one by the rule sitting
        0-5pt BELOW the line's bottom — the same registration assumption that
        defeated the char tags. In nancy_white and dicostanzo the rule lands
        inside the glyphs instead, so it survived the filter and both captions
        closed on a divider the page never drew (CLAUDE.md principle 5).
        """
        tops = super()._page1_rules(p1)
        width = getattr(p1, "width", 612.0) or 612.0
        for line in p1.extract_text_lines():
            if not self._is_rule23_title(p1, line, width):
                continue
            chars = [c for c in line["chars"] if (c.get("text") or "").strip()]
            top = min(c["top"] for c in chars)
            bottom = max(c["bottom"] for c in chars)
            tops = [t for t in tops if not (top <= t <= bottom + 3)]
        return tops

    def find_authors(self, all_segments) -> list:
        """A summary decision opens at the title's segment break.

        It is a panel memorandum with no byline of any kind, so the shared
        per-curiam path names it — ``build_opinion`` stamps PER CURIAM off
        ``_mass_order_start``.
        """
        anchor = getattr(self, "_rule23_body", None)
        if anchor is not None:
            for i, (pno, seg, _kind) in enumerate(all_segments):
                if pno == anchor[0] and seg and round(seg[0]["top"], 1) == anchor[1]:
                    self._mass_order_start = i
                    self._mass_advisory_start = None
                    return [i]
        return super().find_authors(all_segments)

    # ----------------------------------------------------------- sign-off
    def _record_right_column(self, pno, lines, page_width) -> None:
        """Remember the lines this page sets in the right half of the measure.

        A ``Block`` carries no x-position, so the column has to be measured
        here, while the lines still have one. Body prose is never set in the
        right half; on the closing page the only thing there is the sign-off.
        """
        rows = [
            " ".join(self.line_plain_text(l).split())
            for l in sorted(lines, key=lambda l: l["top"])
            if l["x0"] >= page_width * 0.5 and self.line_plain_text(l).strip()
        ]
        if rows:
            self._sig_rows[pno] = rows

    def _harvest_panel_signature(self, doc):
        """Lift the clerk's signature graphic, and the title under it, into
        ``doc.signature``.

        The graphic is the signature; the disposition ('So ordered.') and the
        panel roster ('By the Court (NAME, NAME & NAME, JJ.),') above it are the
        court's own words and stay in the opinion where they were printed. The
        title line beneath the graphic ('Clerk') comes with it — it names the
        signer — and is told from the 'Entered: <date>.' stamp below it by
        column: the title is set in the signature's right-hand column, the
        stamp returns to the left margin.
        """
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = list(op.blocks)
        idx = next(
            (i for i in reversed(range(len(blocks))) if blocks[i].kind == "image"),
            None,
        )
        if idx is None:
            return

        rows = (self._sig_rows or {}).get(blocks[idx].page) or []
        sig = [{"__image__": True, **(blocks[idx].payload or {})}]
        end = idx + 1
        while end < len(blocks):
            text = " ".join(_plain_words(blocks[end].text))
            if not text:
                end += 1
                continue
            if text not in rows:
                break
            sig.append(str(blocks[end].text))
            end += 1

        doc.signature = sig
        op.blocks = blocks[:idx] + blocks[end:]
