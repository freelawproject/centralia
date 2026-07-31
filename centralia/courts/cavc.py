"""United States Court of Appeals for Veterans Claims.

A CM/ECF-style header tops every page ('Case: 24-9605 Page: 1 of 10
Filed: 05/13/2026') — furniture, dropped and surfaced. The caption names
the panel ('Before ALLEN, Chief Judge, and BARTLEY and LAURER, Judges.');
orders are single-spaced (tight segments stay in the body) and close
'DATED: … PER CURIAM.' — the author when no byline names a judge.
"""

from __future__ import annotations

from ._district import DistrictBase


class VeteransClaimsCourt(DistrictBase):
    court_id = "cavc"
    court_label = "United States Court of Appeals for Veterans Claims."

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """No pleading-paper gutter exists in this court — and inferring one
        from a far-left column of small integers MISREADS this court's
        footnotes for it.

        The notes are set flush at the 72pt body margin with a plain
        (non-superscript) label, so a footnote-heavy page shows a stack of a
        dozen sequential integers at x0=72 — exactly the signature the
        district base uses for a line-number gutter. It then discarded every
        char left of the labels' right edge, shaving the first one or two
        LETTERS off every body line on the page ('passed away' -> 'assed
        away', 'entitlement' -> 'titlement'). That is what made this court
        'missing lots of text'."""
        return None

    # This court sets block quotations at TWO indents: a full two inches
    # (x0=144, which the generic 1.5-step threshold catches) and a half inch
    # (x0=108 — the same measure as a paragraph's first-line indent). The
    # shallow quotes therefore stayed in the body, and because none of their
    # lines reaches the right measure the line-stack splitter then emitted one
    # block PER LINE. Lower the threshold to the shallow indent: the base's
    # requirement that a deep line have a neighbour at the SAME left edge is
    # what keeps a lone first-line indent out, so no paragraph is affected.
    quote_indent = 36.0
    # The body is double-spaced (~27pt); a quotation is single-spaced (~14pt).
    quote_single_max = 20.0

    def _deep_indent_flags(self, lines) -> list:
        flags = list(super()._deep_indent_flags(lines))
        if not self.blockquote_by_indent:
            return flags
        deep = self.body_baseline_x0 + self.quote_indent
        raw = [
            l["x0"] >= deep - 1 and not self._begins_paragraph_block([l])
            for l in lines
        ]
        for i, d in enumerate(raw):
            if not d:
                continue
            # The neighbour must share the left edge AND sit a SINGLE line
            # away: two consecutive first-line indents ('Accordingly, it is' /
            # 'ORDERED that …') share an edge but are a double-space apart.
            if any(
                0 <= j < len(lines)
                and raw[j]
                and abs(lines[j]["x0"] - lines[i]["x0"]) <= 3
                and abs(lines[j]["top"] - lines[i]["top"]) <= self.quote_single_max
                for j in (i - 1, i + 1)
            ):
                flags[i] = True
        return flags

    def split_blockquote_paragraphs(self, seg) -> list:
        """Split a quotation on its paragraph gap only.

        A block quotation is set to its OWN, narrower measure, so the generic
        'no line in this group reached the page measure, therefore nothing
        wrapped' stack test is meaningless inside one — it shattered a quote
        continued across a page break into one block per line."""
        if not seg:
            return []
        from statistics import median

        gaps = [seg[i + 1]["top"] - seg[i]["top"] for i in range(len(seg) - 1)] or [0]
        med_gap = median(gaps)
        paras = [[seg[0]]]
        for i in range(1, len(seg)):
            if seg[i]["top"] - seg[i - 1]["top"] > med_gap * 1.4:
                paras.append([seg[i]])
            else:
                paras[-1].append(seg[i])
        return paras

    # ------------------------------------------------------------------
    # a separate writing appended to a per curiam order
    # ------------------------------------------------------------------
    def _separate_writing_byline(self, line):
        """(byline, inline body text) for a judge's separate writing appended
        below the per curiam close — 'JAQUITH, Judge, concurring: I concur
        fully in the per curiam opinion and …' — else None.

        The byline runs to the colon and the opinion text continues on the
        same line, so the district base (which expects one ruling with the
        author taken from the signature) folded the whole concurrence into
        the order's body."""
        text = self.line_plain_text(line).strip()
        ci = text.find(":")
        if ci == -1:
            return None
        head = text[:ci].strip()
        parsed = self.parse_author_line(head)
        if parsed is None or not parsed[2]:  # must carry a concur/dissent kind
            return None
        return head, text[ci + 1 :].strip()

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        if not starts:
            return starts
        for i in range(starts[-1] + 1, len(all_segments)):
            seg = all_segments[i][1]
            if seg and self._separate_writing_byline(seg[0]) is not None:
                starts = list(starts) + [i]
                break
        return starts

    def split_author_line(self, line):
        r = self._separate_writing_byline(line)
        if r is None:
            return super().split_author_line(line)
        byline, body = r
        if not body:
            return byline, []
        chars = line.get("chars") or []
        target = len("".join(self.line_plain_text(line).split())) - len(
            "".join(body.split())
        )
        cnt, idx = 0, len(chars)
        for k, c in enumerate(chars):
            if not (c.get("text") or "").isspace():
                cnt += 1
            if cnt >= target:
                idx = k + 1
                break
        body_chars = chars[idx:]
        body_line = dict(line)
        body_line["text"] = body
        body_line["chars"] = body_chars
        if body_chars:
            body_line["x0"] = body_chars[0]["x0"]
        return byline, [body_line]

    def page_lines(self, page):
        if not hasattr(self, "_cavc_dropped"):
            self._cavc_dropped = []
        lines = super().page_lines(page)
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) < 30 and t.lower().startswith("case:"):
                self._cavc_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._cavc_dropped = []
        doc = super().extract(pdf_path)
        if self._cavc_dropped:
            seen, extra = set(), []
            for t in self._cavc_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        # 'DATED: … PER CURIAM.' close — the Court speaks per curiam. The
        # 'Before ALLEN, …' panel roster is not an author.
        for o in doc.opinions:
            if (o.author or "").startswith("Before"):
                o.author = ""
        if doc.opinions and not doc.opinions[0].author:
            op = doc.opinions[-1]
            for b in op.blocks[-3:]:
                if "PER CURIAM" in self._untag(str(b.text)).upper():
                    for o in doc.opinions:
                        if not o.author:
                            o.author = "PER CURIAM"
                    break
        return doc