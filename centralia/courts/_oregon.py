"""Shared layout handling for the Oregon Reports (Supreme + Court of Appeals).

Both courts publish in the same reporter format — a narrow (~5.5") page (width
~396), NewCenturySchlbk body at 11pt with x0 ~45, a running header at the very
top of every page, and two kinds of footnotes:

  * star ('*' / '**') caption footnotes, set at 8pt below a short (~58pt)
    underscore-TEXT rule (a line of '_' characters, not a vector rule); and
  * numbered body footnotes ('1 …', '2 …') that have NO separator rule at all —
    the 8pt footnote block simply follows the 11pt body at the page foot.

This mixin carries the reporter-specific footnote detection/labelling, the
narrow-page margins, the styled headmatter, and the facet fingerprint. It is
mixed in BEFORE each court's byline base (AbbrevTitleSupreme for the Supreme
Court, StateAppellate for the Court of Appeals) so its overrides win and their
``super()`` calls fall through to that base.
"""

from __future__ import annotations

from ._abbrevtitle import _ABBREV


class OregonReports:
    # Oregon seats Senior Judges by designation, so a byline can read
    # 'WALTERS, S. J.' / 'WALTERS, S.J.' (Senior Judge) — not in the shared
    # abbreviated-title table. Extend it (spaced first, matching 'P. J.').
    abbrev_titles: tuple = (
        ("S. J.", "Senior Judge"),
        ("S.J.", "Senior Judge"),
    ) + _ABBREV

    # Narrow reporter page: body sits at x0 ~45, not the 72 of letter-size courts.
    body_baseline_x0 = 45.0
    # Drop the top-of-page running header (top ~36); body proper starts ~63.
    margin_top = 45.0
    # Star footnotes sit at 8pt below a short (~58pt) underscore-TEXT rule; width,
    # not length, is the gate (40pt clears the rule, rejects tiny stray fills).
    footnote_sep_text_min_width = 40.0

    def page_lines(self, page):
        lines = super().page_lines(page)
        out, index = [], 0
        while index < len(lines):
            line = lines[index]
            text = self.line_plain_text(line).strip()
            low = text.lower()
            if (
                index + 1 < len(lines)
                and ", j.," in low
                and low.endswith(("concurring", "dissenting"))
            ):
                nxt = lines[index + 1]
                tail = self.line_plain_text(nxt).strip()
                if tail.lower().startswith("in part"):
                    merged = dict(line)
                    lead_chars = list(line.get("chars") or [])
                    tail_chars = list(nxt.get("chars") or [])
                    spacer = dict(lead_chars[-1]) if lead_chars else {}
                    spacer.update({"text": " ", "x0": 0.0, "x1": 0.0})
                    merged["chars"] = lead_chars + [spacer] + tail_chars
                    merged["text"] = f"{text} {tail}"
                    merged["x1"] = max(line.get("x1", 0), nxt.get("x1", 0))
                    merged["bottom"] = max(
                        line.get("bottom", line.get("top", 0)),
                        nxt.get("bottom", nxt.get("top", 0)),
                    )
                    out.append(merged)
                    index += 2
                    continue
            out.append(line)
            index += 1
        return out

    # Style-preserving headmatter (the shared 'Florida look').
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    def find_footnote_separator(self, page):
        """Numbered body footnotes ('1 A civil compromise …') have NO separator
        rule — the 8pt footnote block simply follows the 11pt body at the page
        foot. Detect them by the font-size drop: the top of the run of small
        (<= body-2pt) lines that reaches the page bottom. The star ('*'/'**')
        caption footnotes keep their underscore-rule separator (the base path,
        tried first)."""
        base = super().find_footnote_separator(page)
        if base is not None:
            return base
        drawn = self._reporter_sep_rule(page)
        if drawn is not None:
            return drawn
        from collections import Counter
        from statistics import median

        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        body = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        fn_max = body - 2
        sep = None
        for ln in sorted(page.extract_text_lines(), key=lambda l: l["top"], reverse=True):
            szc = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
            if szc and median(szc) <= fn_max:
                sep = ln["top"]
            else:
                break
        # only a footnote block anchored low on the page
        return sep - 1 if sep is not None and sep > page.height * 0.45 else None

    @staticmethod
    def _page_measure(page):
        """The page's own text column — (left rail, right measure) — read from
        the x0/x1 that RECUR among its full-measure lines. Recurrence is what
        makes leftmost/rightmost safe: one outdented stray cannot move either
        edge. Returns (None, None) on a page too sparse to measure."""
        x0s, x1s = {}, {}
        for line in page.extract_text_lines():
            if line.get("x1", 0) - line.get("x0", 0) < page.width * 0.45:
                continue
            a, b = round(line.get("x0", 0)), round(line.get("x1", 0))
            x0s[a] = x0s.get(a, 0) + 1
            x1s[b] = x1s.get(b, 0) + 1
        left = [x for x, hits in x0s.items() if hits >= 2]
        right = [x for x, hits in x1s.items() if hits >= 2]
        return (
            float(min(left)) if left else None,
            float(max(right)) if right else None,
        )

    def _reporter_sep_rule(self, page):
        """The Oregon Reports separator, drawn as a vector line rather than
        typed as underscores.

        Measured over all 50 or documents (1,455 thin rules), the page draws
        exactly two kinds of rail-anchored rule and they do not overlap:

          * the RUNNING-HEADER rule — 302pt, spanning the full text measure,
            at the top of every page (996 of them, all at 0.1 of page height);
          * the FOOTNOTE separator — left-anchored but stopping well short of
            the measure: 58.5pt over a fresh note (366), or ~180pt where the
            zone opens with a footnote CONTINUED from the previous page (39),
            plus a handful at 151/162/248pt. 410 of those 413 carry
            footnote-size text or a raised label directly beneath.

        So the separator is 'anchored at the rail, short of the measure, with
        a note below' — no width floor and no page-position fence. Both of the
        shared finder's gates fail here: the 58.5pt rule is far under the 100pt
        minimum width, and a long footnote pushes its rule above mid-page
        (sheppard p24's continuation rule sits at 0.33 of the sheet).

        A rule that shares its y with another (the two-column statutory box in
        fernandez) is a box edge, not a separator, and is skipped."""
        rail, measure = self._page_measure(page)
        if rail is None or measure is None:
            return None
        rules = [
            r
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2.5 and (r["x1"] - r["x0"]) >= 20
        ]
        tops = []
        for r in rules:
            if abs(r["x0"] - rail) > 2 or r["x1"] >= measure - 8:
                continue
            if any(o is not r and abs(o["top"] - r["top"]) <= 2 for o in rules):
                continue
            if self._rule_over_footnotes(page, r["top"]) or self._labelled_note_below(
                page, r["top"]
            ):
                tops.append(r["top"])
        return min(tops) if tops else None

    def detect_footnote_label(self, line):
        """Oregon foot-marks are same-size '*' / '**' stars set flush with the
        8pt footnote text, not raised superscripts, so the base 'smaller char'
        test misses them. Read the leading star run as the label."""
        text = (line.get("text") or "").lstrip()
        if text.startswith("*"):
            return text[: len(text) - len(text.lstrip("*"))]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the leading star marker off the footnote text (it is the label,
        not prose — the base only strips raised <footnotemark> marks)."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and label != "?":
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip()
            if stripped.startswith(label):
                fn.paragraphs[0] = (tag, stripped[len(label) :].lstrip())
        return fn

    def _apply_or_facets(self, doc, pdf_path):
        """Attach the measured facet signature to the review fingerprint."""
        if doc.non_digital:
            return
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            doc.caption_box = dict(doc.caption_box or {})
            doc.caption_box["style_label"] = self._or_facets(pdf, doc)

    def _or_facets(self, pdf, doc) -> str:
        """Measured facet signature for the review fingerprint — body font/size,
        footnote size + separator-rule width, block-quote indent + size — the
        facets the reporter's grouping app compares. No style LETTER."""
        from collections import Counter
        from statistics import median

        pg = pdf.pages[min(2, len(pdf.pages) - 1)]
        body = [c for c in pg.chars if (c.get("text") or "").strip()]
        bsz = (
            Counter(round(c.get("size", 0)) for c in body).most_common(1)[0][0]
            if body
            else 11
        )
        has_fn = any(o.footnotes for o in doc.opinions) or bool(doc.headmatter_footnotes)
        # star rule width (an underscore band); numbered footnotes carry none
        rule = "none"
        for p in pdf.pages:
            for ln in p.extract_text_lines():
                t = (ln.get("text") or "").strip()
                if t and set(t) <= set("_ ") and 40 < (ln["x1"] - ln["x0"]) < 100:
                    rule = f"{round(ln['x1'] - ln['x0'])}rule"
                    break
            if rule != "none":
                break
        left = round(min((c["x0"] for c in body), default=45))
        right = pg.width - left
        qi, qs = [], []
        for p in pdf.pages:
            for ln in p.extract_text_lines():
                if (
                    left + 8 < ln["x0"] < left + 40
                    and ln["x1"] < right - 8
                    and ln["x1"] > left + 40
                ):
                    szc = [c["size"] for c in (ln.get("chars") or []) if c.get("size")]
                    if szc and median(szc) < bsz:
                        qi.append(ln["x0"] - left)
                        qs.append(median(szc))
        bq = f"bq {round(median(qi))}pt/{round(median(qs), 1)}pt" if qs else "no bq"
        fn = f"fn {'8' if has_fn else 'none'}pt/{rule}" if has_fn else "no fn"
        return f"OR · NewCentury {bsz}pt · {fn} · {bq}"
