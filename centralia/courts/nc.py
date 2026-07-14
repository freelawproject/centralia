"""Supreme Court of North Carolina.

Standard bold all-caps byline ('DIETZ, Justice.' / 'EARLS, Justice.' /
'PER CURIAM.'); the shared state-supreme base handles it directly.
"""

from __future__ import annotations

from statistics import median

from ._statesupreme import StateSupreme


class NorthCarolinaSupreme(StateSupreme):
    court_id = "nc"
    court_label = "Supreme Court of North Carolina."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers
    # Block quotes are indented on both margins and single-spaced at ~13-14pt —
    # below gap_tight_max, so the gap bands read them as 'notice'. Re-tag them
    # by their both-margins indent (the body is double-spaced at ~28pt).
    blockquote_by_indent = True

    # Separate writings use a title-first byline ('Justice BERGER concurring.'
    # / 'Chief Justice NEWBY dissenting.'); the majority/per-curiam name-first
    # form ('NEWBY, Chief Justice.' / 'PER CURIAM.') is handled by the base.
    _reversed_titles = ("Chief Justice", "Justice")

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r:
            return r
        t = text.strip()
        if self.strip_author_trailing_mark:
            t = self._strip_trailing_author_mark(t)
        t = t.rstrip(".")
        for title in self._reversed_titles:
            if not t.startswith(title + " "):
                continue
            toks = t[len(title) + 1 :].split()
            if len(toks) < 2:
                return None
            name = toks[0].rstrip(",")
            if not (name.isupper() and name.replace("-", "").isalpha() and len(name) >= 2):
                return None
            # The word directly after the name must be the concur/dissent
            # participle — a byline. 'Justice EARLS joins in this concurring …
            # opinion.' is a JOINDER (verb 'joins'), not a separate writing.
            verb = toks[1].lower().rstrip(",")
            if not (verb.startswith("concurr") or verb.startswith("dissent")):
                return None
            kind = " ".join(toks[1:]).strip(" ,")
            return (name, title, kind)
        return None

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Group wrapped headmatter lines into paragraphs: the procedural
        block ('On discretionary review …') and each counsel entry read as one
        flowing paragraph instead of one row per source line. Centered caption
        rows (court name, docket, filed date, case name) and dividers stay as
        their own rows. Reuses the base for the caption box and notice routing."""
        d = super().extract_headmatter(headmatter_segs, page1_rules)
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        # Re-derive the line stream (same order/notice rules as the base).
        from collections import Counter as _C

        hm_sizes = _C(
            round(self.line_meta(l)[0])
            for seg in headmatter_segs
            for l in seg
            if (l.get("text") or "").strip()
        )
        dominant = hm_sizes.most_common(1)[0][0] if hm_sizes else 12
        items = []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                size = self.line_meta(line)[0]
                if (
                    self.notice_max_size is not None
                    and size <= self.notice_max_size
                    and round(size) < dominant
                ):
                    continue  # a small-print notice — routed to dropped by base
                chars = line.get("chars") or []
                pno = (chars[0].get("page_number") if chars else line.get("page_number")) or 1
                items.append((pno, round(line["top"], 1), line, size, t))
        items.sort(key=lambda r: (r[0], r[1], r[2]["x0"]))
        base = dominant or 12
        just_x1 = pw - 72 - 12  # a wrapped (justified) line reaches ~the right margin

        summary, buf = [], []

        def flush():
            if not buf:
                return
            html = " ".join(self.line_inline_text(l) for _, _, l, _, _ in buf)
            sz = buf[0][3]
            summary.append(
                {"__hm__": True, "html": html, "rel": round(sz / base, 3), "align": "L"}
            )
            buf.clear()

        prev_pno = prev_bottom = None
        for pno, top, line, size, t in items:
            align = self.line_alignment(line, pw)
            gapped = prev_bottom is not None and (
                pno != prev_pno or (top - prev_bottom) > 1.8 * max(base, 9)
            )
            is_div = all(c in "_-—–" for c in t)
            left_para = align == "L" and not is_div
            # A left line continues the current paragraph only when the prior
            # buffered line was justified (ran to the right margin); otherwise it
            # opens a new one.
            if left_para and buf and buf[-1][2]["x1"] >= just_x1:
                buf.append((pno, top, line, size, t))
            else:
                flush()
                if gapped and summary and summary[-1] != "":
                    summary.append("")
                if is_div:
                    summary.append("__DIVIDER__")
                elif left_para:
                    buf.append((pno, top, line, size, t))
                else:  # centered / right caption row — its own row
                    summary.append(
                        {
                            "__hm__": True,
                            "html": self.line_inline_text(line),
                            "rel": round(size / base, 3),
                            "align": align,
                        }
                    )
            prev_pno, prev_bottom = pno, top
        flush()
        d["summary"] = summary
        return d

    def _maybe_drop_running_header(self, page, lines):
        """Continuation pages carry a two-line running header at the very top —
        the case short-name ('HOKE CNTY. BD. OF EDUC. V. STATE') and the
        'Opinion of the Court' subtitle — set in a font smaller than the 12pt
        body. Drop the contiguous smaller-than-body lines from the top so the
        header stops repeating through the opinion (footnotes are smaller too
        but sit at the page bottom, past this header zone). Page 1 has the real
        caption and no running header."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number == 1 or not lines:
            return lines
        drop = set()
        for ln in sorted(lines, key=lambda l: l.get("top", 0)):
            if ln.get("top", 0) > 100:
                break
            sizes = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
            if sizes and median(sizes) < 11.5:
                drop.add(id(ln))
            else:
                break
        return [l for l in lines if id(l) not in drop]
