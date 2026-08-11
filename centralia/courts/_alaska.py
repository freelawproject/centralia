"""Alaska-specific layout overrides shared by Alaska Supreme and Ct of App.

No regex (see the project's no-regex preference): the parsing leans on font
style, position, and plain string patterns instead.

Page-1 structure (both Alaska courts):

  1. Notice  — a 'NOTICE' header + an italic correction block, at the very top.
  2. Court name banner ('IN THE COURT OF APPEALS OF THE STATE OF ALASKA' /
     'THE SUPREME COURT OF THE STATE OF ALASKA').
  3. Two-column case caption, split by a column of `)` chars at x≈306:
     LEFT = party names + roles, RIGHT = Supreme/Superior Court Nos.,
     'O P I N I O N', 'No. 7802 – Feb 20, 2026'.
  4. Single-column metadata (still caption): 'Appeal from ...' (history),
     'Appearances: ...' (attorneys), 'Before: ...' (judges).
  5. The opinion body, opening with an author byline.

The notice is everything before the court banner — dropped into the review
'Removed' bucket; everything from the banner on is returned verbatim.
"""

from __future__ import annotations

from typing import Optional

from ..base import BaseExtractor
from ..models import Block


# x0 < 250 => LEFT caption column (party names); >= 250 => RIGHT column
# (docket / opinion label / date). The `)` divider sits at x≈306.
_COLUMN_SPLIT_X = 250

_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Author title prefixes, longest first so "Chief Justice" wins over "Justice".
_TITLES = (
    "Chief Justice",
    "Senior Justice",
    "Presiding Justice",
    "Associate Justice",
    "Chief Judge",
    "Senior Judge",
    "Presiding Judge",
    "Justice",
    "Judge",
)

_DOCKET_PREFIXES = ("Supreme Court No.", "Court of Appeals No.")
_LOWER_PREFIXES = ("Superior Court No.", "Trial Court No.", "District Court No.")
_DASHES = "–—-"


class BaseAlaskaExtractor(BaseExtractor):
    # Alaska body is more tightly spaced than Alabama's.
    gap_tight_max = 13.5
    gap_single_max = 18.0
    gap_double_max = 28.0
    # Alaska uses tightly set body text for statutory lists and quotations.
    # Those runs are content, not publication notices.
    drop_notice_in_body = False

    @staticmethod
    def _line_page(line) -> int:
        chars = line.get("chars") or []
        return (
            (chars[0].get("page_number") if chars else line.get("page_number"))
            or 1
        )

    # ---------------------------------------------------------------- pipeline
    def extract(self, pdf_path):
        """Base pipeline, then promote Alaska section headings (bold ALL-CAPS
        lines like 'FACTS AND PROCEEDINGS' and 'A. ...' subsections) from
        paragraphs to heading blocks. The big roman section numerals are
        decorative images and are left as the base produced them."""
        self._alaska_author_announcements = []
        doc = super().extract(pdf_path)
        if self._alaska_author_announcements:
            doc.summary = list(doc.summary) + list(self._alaska_author_announcements)
        for op in doc.opinions:
            op.blocks = [self._maybe_heading(b) for b in op.blocks]
            op.blocks = self._normalize_section_blocks(op.blocks)
        return doc

    @staticmethod
    def _merge_interleaved(lines):
        """Alaska's italic glyphs can sit about 1pt above roman glyphs on
        the same visual row.  The base merger's very strict overlap test then
        splits words such as ``Alaska`` into separate line objects."""
        if len(lines) < 2:
            return lines
        lines = sorted(lines, key=lambda l: (l["top"], l["x0"]))
        out = [lines[0]]
        for ln in lines[1:]:
            prev = out[-1]
            # The caption's two columns share a baseline but are NOT one line:
            # ``page_lines`` has just split them at the ')' rail, and merging
            # them back is what produced 'ANITA THORNE, ) Supreme Court No.
            # S-19231' as a single run with the rail glued mid-text.
            if prev.get("_caption_col") != ln.get("_caption_col"):
                out.append(ln)
                continue
            overlap = min(prev["bottom"], ln["bottom"]) - max(
                prev["top"], ln["top"]
            )
            min_h = max(
                min(prev["bottom"] - prev["top"], ln["bottom"] - ln["top"]),
                1.0,
            )
            chars = sorted(
                list(prev.get("chars") or []) + list(ln.get("chars") or []),
                key=lambda c: c["x0"],
            )
            if chars and overlap > 0.45 * min_h:
                union = max(c["x1"] for c in chars) - min(c["x0"] for c in chars)
                glyphs = sum(c["x1"] - c["x0"] for c in chars)
                if glyphs <= union * 1.16:
                    merged = dict(prev)
                    merged["chars"] = chars
                    merged["x0"] = min(prev["x0"], ln["x0"])
                    merged["x1"] = max(prev["x1"], ln["x1"])
                    merged["top"] = min(prev["top"], ln["top"])
                    merged["bottom"] = max(prev["bottom"], ln["bottom"])
                    merged["text"] = "".join(c["text"] for c in chars)
                    out[-1] = merged
                    continue
            out.append(ln)
        return out

    @staticmethod
    def _strong_runs(text):
        """Return strong-text runs when the whole block is heading markup."""
        t = text.strip()
        if t.startswith("<pagenumber "):
            end = t.find("/>")
            if end < 0:
                return None
            prefix, t = t[: end + 2], t[end + 2 :].strip()
        else:
            prefix = ""
        runs = []
        while t:
            if not t.startswith("<strong>"):
                return None
            end = t.find("</strong>")
            if end < 0:
                return None
            runs.append(t[8:end])
            t = t[end + 9 :].strip()
        return prefix, runs

    @classmethod
    def _heading_markup(cls, prefix, runs, number=None):
        parts = []
        if prefix:
            parts.append(prefix)
        if number is not None:
            runs = list(runs)
            runs[0] = f"{number}. {runs[0]}"
        parts.extend(f"<strong>{run}</strong>" for run in runs)
        return " ".join(parts)

    @classmethod
    def _normalize_section_blocks(cls, blocks):
        """Promote tiny Roman numeral figures into the section heading they
        precede, and recognize long all-bold headings that segmentation tagged
        as blockquotes."""
        out = []
        roman = 0
        for block in blocks:
            if block.kind == "image":
                width = (block.payload or {}).get("width", 0)
                height = (block.payload or {}).get("height", 0)
                if width <= 24 and height <= 16:
                    out.append(block)
                    continue
            runs = cls._strong_runs(block.text or "") if block.kind in ("p", "blockquote", "heading") else None
            if (
                runs
                and block.kind in ("p", "blockquote")
                and not cls._plain_inline(block.text or "").strip().startswith("(")
            ):
                block.kind = "heading"
            if out and out[-1].kind == "image" and runs:
                prev = out.pop()
                width = (prev.payload or {}).get("width", 0)
                height = (prev.payload or {}).get("height", 0)
                if width <= 24 and height <= 16:
                    roman += 1
                    prefix, strong = runs
                    numeral = [
                        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                    ][roman - 1] if roman <= 10 else None
                    block.text = cls._heading_markup(prefix, strong[:1], numeral)
                    out.append(block)
                    for extra in strong[1:]:
                        out.append(
                            Block(
                                kind="heading",
                                text=f"<strong>{extra}</strong>",
                                page=block.page,
                            )
                        )
                    continue
                else:
                    out.append(prev)
            if out and out[-1].kind == "heading" and block.kind == "p":
                plain = cls._plain_inline(block.text or "").strip()
                if plain.startswith("Law.") and cls._strong_runs(block.text or ""):
                    out[-1].text += " " + block.text
                    continue
            if out and out[-1].kind == "heading" and block.kind == "heading":
                plain = cls._plain_inline(block.text or "").strip()
                if plain == "Law.":
                    out[-1].text += " " + block.text
                    continue
            out.append(block)
        # NB: no numbered-item re-splitting here. Alaska prints statutory
        # factor lists as ONE flowing indented quotation (see the Evidence
        # Rule 803(6) quote in portfolio_recovery p32: '... testified that:
        # (1) The records ... ; and (2) the witness ...' runs continuously
        # across ten single-spaced lines). Cutting a block at '(n)' markers
        # invents layout the PDF never drew, and a marker-position slice
        # silently discards everything ahead of the first marker — which is
        # how the lead-in of that quotation, and whole footnote bodies that
        # merely cite '12(b)(6)' or 'AS 33.16.215(f)(2)', went missing.
        return out

    @staticmethod
    def _maybe_heading(block):
        if block.kind != "p" or not block.text:
            return block
        t = block.text.strip()
        plain = BaseAlaskaExtractor._plain_inline(t).strip()
        words = plain.split()
        caps = (
            plain.upper() == plain
            and any(c.isalpha() for c in plain)
            and 1 <= len(words) <= 7
            and not plain.endswith(".")
            and not plain.startswith("(")
        )
        sub = (
            len(plain) >= 3
            and "A" <= plain[0] <= "Z"
            and plain[1] == "."
            and plain[2:3] == " "
            and len(words) <= 10
        )
        if caps or sub:
            block.kind = "heading"
        return block

    # ---------------------------------------------------------------- author
    def find_authors(self, all_segments) -> list:
        """Author bylines, minus any with no opinion body before the next one —
        a 'Judge X, writing for the Court.' cover/summary byline repeated above
        the opinion proper would otherwise spawn an empty opinion.

        Alaska also prints adjacent authorship lines before the majority body:
        the first is the majority byline and later lines announce separate
        writings (``PATE, Justice.`` / ``CARNEY, Justice, dissenting.``). Keep
        the first author in such a run; the announced writing's real byline
        appears again where that writing actually begins."""
        cands = [
            i
            for i, (_p, seg, kind) in enumerate(all_segments)
            if kind != "notice"
            and seg
            and self.parse_author_line((seg[0].get("text") or "").strip())
        ]
        collapsed = []
        announcements = []
        for i in cands:
            if collapsed and i == collapsed[-1] + 1:
                announcements.append(
                    (all_segments[i][1][0].get("text") or "").strip()
                )
            else:
                collapsed.append(i)
        self._alaska_author_announcements = announcements
        cands = collapsed
        out = []
        for n, i in enumerate(cands):
            end = cands[n + 1] if n + 1 < len(cands) else len(all_segments)
            seg0 = all_segments[i][1]
            has_body = len(seg0) > 1 or any(
                all_segments[k][1] and not self._byline_at(all_segments[k][1][0])
                for k in range(i + 1, end)
            )
            if has_body:
                out.append(i)
        return out

    def build_opinion(self, op_start, op_end, **kwargs):
        opinion = super().build_opinion(op_start, op_end, **kwargs)
        announcements = set(getattr(self, "_alaska_author_announcements", []))
        if announcements:
            opinion.blocks = [
                block
                for block in opinion.blocks
                if not (
                    block.kind == "p"
                    and self._plain_inline(block.text).strip() in announcements
                )
            ]
        return opinion

    @staticmethod
    def _plain_inline(text: str) -> str:
        """Remove Centralia's small inline emphasis tags for exact comparison."""
        for tag in ("<strong>", "</strong>", "<em>", "</em>", "<u>", "</u>"):
            text = text.replace(tag, "")
        return text

    def parse_author_line(self, text):
        """Standard 'PATE, Justice.' (handled by the base) plus the reversed
        Alaska Court of Appeals form 'Judge HARBISON, writing for the Court.'."""
        result = super().parse_author_line(text)
        if result is not None:
            return result
        return self._parse_reversed_author(text)

    @staticmethod
    def _parse_reversed_author(text):
        t = text.strip()
        if t.endswith("."):
            t = t[:-1]
        for title in _TITLES:
            if not t.startswith(title + " "):
                continue
            rest = t[len(title) + 1 :].strip()
            if "," in rest:
                name, kind = rest.split(",", 1)
                name, kind = name.strip(), kind.strip()
            else:
                name, kind = rest.strip(), None
            if not _is_caps_name(name):
                return None
            if kind and "writing" in kind.lower():
                kind = None  # 'writing for the Court' = majority
            return name, title, kind
        return None

    # ---------------------------------------------------------------- caption
    def find_caption_divider(self, page):
        """(x, top, bottom) of the caption column divider, or None. A vertical
        rect/line (Ct of App) or a column of `)` chars (Supreme).

        A divider has to DIVIDE: it only counts when the caption sets text on
        both sides of it within its own vertical span. Without that test a bar
        drawn down the left margin qualified on height alone (x=76 on a 612pt
        page), and since every caption line then fell to its right the left
        column came out empty and the whole caption read as one column."""
        def divides(x, top, bottom):
            left = right = False
            for c in page.chars:
                if not (top - 2 <= c["top"] <= bottom + 2):
                    continue
                if not (c.get("text") or "").strip():
                    continue
                if c["x1"] <= x - 2:
                    left = True
                elif c["x0"] >= x + 2:
                    right = True
                if left and right:
                    return True
            return False

        for r in page.rects:
            if r["width"] < 2 and r["height"] > 30:
                if divides(r["x0"], r["top"], r["bottom"]):
                    self._alaska_rail = None  # drawn, not a glyph rail
                    return r["x0"], r["top"], r["bottom"]
        for ln in page.lines:
            x0 = ln["x0"]
            x1 = ln.get("x1", x0)
            if abs(x1 - x0) < 2 and (ln["bottom"] - ln["top"]) > 30:
                if divides(x0, ln["top"], ln["bottom"]):
                    self._alaska_rail = None
                    return x0, ln["top"], ln["bottom"]
        from collections import Counter

        paren_chars = [c for c in page.chars if c.get("text") == ")"]
        if len(paren_chars) < 3:
            return None
        buckets = Counter(round(c["x0"] / 2) * 2 for c in paren_chars)
        bucket_x, count = buckets.most_common(1)[0]
        if count < 3:
            return None
        matching = [c for c in paren_chars if abs(c["x0"] - bucket_x) < 2]
        top = min(c["top"] for c in matching)
        bottom = max(c["bottom"] for c in matching)
        if not divides(float(bucket_x), top, bottom):
            return None
        self._alaska_rail = ")"
        return float(bucket_x), top, bottom

    def page_lines(self, page):
        """Extract lines, column-splitting caption rows that span a vertical
        column divider."""
        self.correct_page_geometry(page)
        # Parenthesized statutory lists and quoted pleadings on later pages
        # can resemble the caption's ``)`` divider.  Only page 1 is caption
        # geometry; splitting later pages manufactures missing letters and
        # corrupts footnotes.
        divider = (
            self.find_caption_divider(page)
            if page.page_number == getattr(self, "_caption_pno", 1)
            else None
        )
        if divider is None:
            lines = self._text_lines(page.filter(self.filter_margins))
            lines = self._merge_interleaved(lines)
            self._tag_underlined_chars(page, lines)
            return self._maybe_drop_running_header(page, lines)

        div_x, div_top, div_bot = divider
        m_top, m_bot = self.margin_top, self.margin_bottom

        def in_body_margin(obj):
            return m_top <= obj["top"] <= m_bot

        def outside_caption(obj):
            return in_body_margin(obj) and not (div_top <= obj["top"] <= div_bot)

        def left_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x1"] <= div_x
            )

        def right_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x0"] >= div_x
            )

        # Remember the rail so ``extract_headmatter`` can rebuild the caption
        # as two real columns rather than as space-padded text.
        self._alaska_divider = divider

        lines = []
        lines += self._text_lines(page.filter(outside_caption))
        for ln in self._text_lines(page.filter(left_of_divider)):
            ln["_caption_col"] = "L"
            lines.append(ln)
        for ln in self._text_lines(page.filter(right_of_divider)):
            ln["_caption_col"] = "R"
            lines.append(ln)
        lines.sort(key=lambda l: (l["top"], l["x0"]))
        lines = self._merge_interleaved(lines)
        self._tag_underlined_chars(page, lines)
        return self._maybe_drop_running_header(page, lines)

    # ---------------------------------------------------------------- footnote
    def find_footnote_separator(self, page) -> Optional[float]:
        """Recognize the Alaska appellate template's two footnote-rule measures.

        Both Alaska courts draw the footnote rule left-anchored on the body
        baseline in one of exactly two widths: the full body measure (468pt on
        a 612pt page) for merits opinions, and a two-inch (144pt) rule for the
        Court of Appeals template and Supreme Court orders. The page-one
        caption closure is a half-column measure (about 229-237pt) and must
        stay in headmatter.

        The measure, not the vertical position, is the discriminator. A
        footnote-heavy page carries its rule high — james_clarke p5 rules at
        top=384 of 792, 48% down the page — so a "bottom 45% only" test loses
        the whole footnote zone and spills the notes into the body as
        paragraphs and blockquotes.
        """
        body_width = page.width - 2 * self.body_baseline_x0
        candidates = []
        # Read the FILLED-PATH form of the same rule too (``page.curves``): the
        # measure is the discriminator, and a producer that fills the rule
        # instead of stroking it draws the identical measure.
        for rect in list(page.rects) + list(getattr(page, "curves", None) or []):
            width = rect["x1"] - rect["x0"]
            full_measure = abs(width - body_width) <= 12
            short_measure = abs(width - 144) <= 18
            if (
                rect["height"] < 2
                and rect["x0"] < self.body_baseline_x0 + 6
                and (full_measure or short_measure)
            ):
                candidates.append(rect)
        if not candidates:
            return None
        return min(candidates, key=lambda rect: rect["top"])["top"]

    # ---------------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = {
            "decisiondate": None,
            "court": self.court_label,
            "docketnumber": None,
            "parties": [],
            "motion": None,
            "parentcase": None,
            "lowercourt": None,
            "history": None,
            "attorneys": None,
            "judges": None,
            "otherdocket": None,
        }
        # Measure this document's own glyph advance for the caption
        # reconstruction below (see ``_layout_rows``).
        # Measure the advance of the CAPTION's own face. Averaging every
        # headmatter line together answers the wrong question: the notice above
        # the banner is set 11pt italic (advance ~5.9) and the caption 13.6pt
        # (~8.4), so a single median lands on neither and the columns stay out
        # of true. Take the dominant size among the lines being laid out and
        # measure only those.
        sized = [
            (round(self.line_meta(ln)[0], 1), ln)
            for seg in headmatter_segs
            for ln in seg
            if (ln.get("text") or "").strip()
            and len((ln.get("text") or "").strip()) > 12
            and ln.get("x1") is not None
        ]
        if sized:
            from collections import Counter

            main = Counter(sz for sz, _ in sized).most_common(1)[0][0]
            widths = sorted(
                (ln["x1"] - ln["x0"]) / len((ln.get("text") or "").strip())
                for sz, ln in sized
                if sz == main
            )
            if widths:
                self._caption_char_w = widths[len(widths) // 2]

        party_lines = []
        summary_pos = []  # (page, top, x0, text) for layout-preserved summary
        notice_lines = []
        current_block = None  # in-progress labeled block: history/attorneys/judges

        # The notice sits before the court banner. If the banner is present,
        # everything before it is the notice; otherwise we drop nothing.
        has_banner = any(
            self._is_banner((ln.get("text") or "").strip())
            for seg in headmatter_segs
            for ln in seg
        )
        seen_banner = not has_banner

        for seg in headmatter_segs:
            for line in seg:
                text = (line.get("text") or "").strip()
                if not text:
                    continue

                col = line.get("_caption_col")
                if not seen_banner:
                    if self._is_banner(text):
                        seen_banner = True
                        summary_pos.append(
                            (
                                self._line_page(line),
                                round(line["top"]),
                                line["x0"],
                                text,
                                col,
                            )
                        )
                    else:
                        notice_lines.append(text)
                    continue

                summary_pos.append(
                    (
                        self._line_page(line),
                        round(line["top"]),
                        line["x0"],
                        text,
                        col,
                    )
                )
                x0 = line["x0"]

                if x0 >= _COLUMN_SPLIT_X:
                    self._extract_right_column(text, out)
                    continue

                lt = text.lower()
                if lt.startswith(("appeal from", "petition for hearing from")):
                    out["history"] = self._extend(out.get("history"), text)
                    current_block = "history"
                    continue
                if text.startswith("Appearances:"):
                    out["attorneys"] = self._extend(
                        out.get("attorneys"), text[len("Appearances:") :].strip()
                    )
                    current_block = "attorneys"
                    continue
                if text.startswith("Before:"):
                    out["judges"] = self._extend(
                        out.get("judges"), text[len("Before:") :].strip()
                    )
                    current_block = "judges"
                    continue
                if current_block is not None and 100 <= x0 < _COLUMN_SPLIT_X:
                    out[current_block] = self._extend(out.get(current_block), text)
                    continue

                cleaned = text.rstrip(") ").strip()
                if cleaned and cleaned != ")":
                    party_lines.append(cleaned)

        if out["decisiondate"] is None and out["otherdocket"]:
            d = self._find_date(out["otherdocket"])
            if d:
                out["decisiondate"] = d

        # The horizontal rule closing the party caption is headmatter
        # structure, not a footnote separator. Insert it at its real page-one
        # position so the rendered order matches the PDF.
        cap_page = getattr(self, "_caption_pno", 1)
        divider_tops = list(page1_rules or [])
        # The Supreme Court caption closes with a left half-width rule meeting
        # the ')' rail. The generic rule collector can mistake it for an
        # underline because it sits directly beneath the rail's final glyph;
        # recover it from the unfiltered page-one rule spans by its caption
        # measure and left anchor. Short opinion-label underlines and genuine
        # footnote rules occupy different width bands.
        # ... but never a rule that is part of a caption BOX. An order drawn in
        # a ruled box puts its top and bottom edges at exactly this measure and
        # left anchor, and recovering them added the box's own borders as
        # free-standing dividers above and below the caption.
        #
        # Only a DRAWN divider can belong to a box. Where the columns are held
        # by a ')' glyph rail there are no borders to confuse, and the rule the
        # recovery exists for sits directly under the rail's last glyph — so
        # excluding the rail's own span there deleted the caption's closing
        # rule instead.
        div = getattr(self, "_alaska_divider", None)
        boxed = div is not None and getattr(self, "_alaska_rail", None) is None
        for top, x0, x1 in getattr(self, "_p1_rule_spans", []):
            width = x1 - x0
            if boxed and div[1] - 2 <= top <= div[2] + 8:
                continue
            if x0 < 100 and page1_rules is not None and 200 <= width <= 270:
                if not any(abs(top - seen) < 3 for seen in divider_tops):
                    divider_tops.append(top)
        for top in sorted(divider_tops):
            summary_pos.append(
                (cap_page, round(top), 72.0, self.HEADMATTER_DIVIDER, None)
            )

        out["parties"] = party_lines
        out["summary"] = self._layout_rows(summary_pos)
        out["dropped"] = [" ".join(notice_lines)] if notice_lines else []
        return out

    @staticmethod
    def _is_banner(text: str) -> bool:
        """The court-name banner: an ALL-CAPS line naming the court/state."""
        u = text.upper()
        return text == u and "COURT" in u and "ALASKA" in u and len(text.split()) >= 4

    @staticmethod
    def _extend(prev, addition):
        return (prev + " " + addition) if prev else addition

    def _extract_right_column(self, text, out):
        """Right-column caption data — court numbers, opinion no., date. Plain
        string matching, no regex."""
        t = text.lstrip(") ").strip()

        for prefix in _DOCKET_PREFIXES:
            if prefix in t and out["docketnumber"] is None:
                out["docketnumber"] = t[t.index(prefix) :].strip()
                return
        for prefix in _LOWER_PREFIXES:
            if prefix in t:
                out["lowercourt"] = t[t.index(prefix) :].strip()
                return
        if "".join(t.split()).upper() == "OPINION":
            return  # decorative 'O P I N I O N'
        if t.startswith("No."):
            toks = t.split()
            if len(toks) >= 2:
                out["otherdocket"] = "No. " + toks[1]
            d = self._find_date(t)
            if d:
                out["decisiondate"] = d

    @staticmethod
    def _find_date(text: str) -> Optional[str]:
        """Return a 'Month D, YYYY' substring, or None. No regex."""
        words = text.split()
        for i, w in enumerate(words):
            if w.strip(",.") in _MONTHS and i + 1 < len(words):
                return " ".join(words[i:]).strip()
        return None

    def _layout_rows(self, items: list, char_w: float = None) -> list:
        """Emit the headmatter rows.

        The caption itself comes out as ONE ``__caption__`` block holding its
        two real columns and the ')' rail between them. It used to be rebuilt
        as space-padded plain text on a measured glyph advance — a positional
        facsimile, which the project's headmatter rule rejects — and because a
        proportional face never lines up on a character grid the columns drifted
        and the rail landed mid-word ('ALASKA DEMOCRATIC PARTY and)').

        Everything outside the caption zone (the banner above it, the appeal
        history / appearances / panel below it) stays a plain row: those run the
        full measure and have no column structure to keep."""
        if not items:
            return []
        items = [it if len(it) > 4 else (*it, None) for it in items]
        items.sort(key=lambda r: (r[0], r[1], r[2]))

        # The rail is what the page actually drew: ')' for a glyph rail, and
        # nothing for a divider drawn as a rect/line — claiming ')' for a drawn
        # divider put a paren rail between columns the page rules with a line.
        rail = getattr(self, "_alaska_rail", None) if getattr(
            self, "_alaska_divider", None
        ) else None
        out_rows = []
        pending_left, pending_right = [], []

        def flush_caption():
            if not (pending_left or pending_right):
                return
            out_rows.append(
                {
                    "__caption__": True,
                    "left": list(pending_left),
                    "right": list(pending_right),
                    "rail": rail,
                }
            )
            pending_left.clear()
            pending_right.clear()

        plain_items = []
        for page, top, x0, text, col in items:
            if col is None:
                # A caption row already open must close before this row, so the
                # banner above and the appeal history below stay in document
                # order around the block.
                if pending_left or pending_right:
                    plain_items.append(None)  # placeholder: caption sits here
                    flush_caption()
                plain_items.append((page, top, x0, text))
                continue
            body = text.strip()
            if col == "L":
                body = body.rstrip(") ").strip()
                if body:
                    pending_left.append(body)
            else:
                body = body.lstrip(") ").strip()
                if body:
                    pending_right.append(body)
        if pending_left or pending_right:
            plain_items.append(None)
            flush_caption()

        # Re-thread the plain rows around the caption block(s) in order.
        #
        # BY OWNERSHIP, NOT BY COUNT. ``_pad_rows`` packs items that share a
        # ``top`` onto ONE row, so it returns fewer rows than it was given —
        # and the old walk advanced one index per ITEM, guarded by
        # ``if ip < len(laid)``. Every merge therefore pushed the index past
        # the end and silently dropped a row off the TAIL of the headmatter.
        # Nine Alaska documents lost the second line of their justice roster
        # that way ('Henderson, and Pate, Justices.', '[Borghesan, Justice, not
        # participating.]'), which the completeness sweep then reported as
        # unplaced content. Ask each row which items it consumed instead.
        laid, counts = self._pad_rows(
            [it for it in plain_items if it is not None], char_w, with_counts=True
        )
        owner = []
        for ri, n in enumerate(counts):
            owner.extend([ri] * n)
        result, ic, k, emitted = [], 0, 0, -1

        def catch_up(upto):
            """Emit the rows that consume no items (the page-break blanks)."""
            for j in range(emitted + 1, upto):
                if counts[j] == 0:
                    result.append(laid[j])

        for it in plain_items:
            if it is None:
                if ic < len(out_rows):
                    result.append(out_rows[ic])
                    ic += 1
                continue
            ri = owner[k] if k < len(owner) else None
            k += 1
            if ri is None or ri == emitted:
                continue
            catch_up(ri)
            result.append(laid[ri])
            emitted = ri
        catch_up(len(laid))
        return result

    def _pad_rows(self, items: list, char_w: float = None, with_counts=False):
        """Lay out the NON-caption rows: lines sharing a ``top`` go on one text
        line at a column derived from their x0. Page number is the primary key;
        sorting by ``top`` alone moves a page-two continuation above page-one
        material."""
        if not items:
            return ([], []) if with_counts else []
        items = sorted(items, key=lambda r: (r[0], r[1], r[2]))
        # The glyph advance is MEASURED from the document, not assumed. The
        # caption is set in a proportional face, and a fixed 6.2pt estimate ran
        # 35% under this corpus's actual 8.4 — which put the ')' rail at column
        # 37 instead of 27 and pulled every column out of true, so the
        # reconstructed caption did not line up with the page.
        if not char_w:
            char_w = getattr(self, "_caption_char_w", None) or 6.2
        rows, segs, cur_page, cur_top = [], [], None, None
        # How many input items each emitted row consumed, so the caller can
        # re-thread rows around the caption block without assuming 1:1.
        counts: list = []

        def emit(parts):
            line = ""
            for x0, text in parts:
                col = max(len(line) + (1 if line else 0), int((x0 - 72) / char_w))
                line += " " * (col - len(line)) + text
            return line

        for page, top, x0, text in items:
            page_changed = cur_page is not None and page != cur_page
            # A DIVIDER IS ALWAYS ITS OWN ROW. Two rules drawn within a few
            # points of each other share a ``top`` band, and packing same-top
            # items onto one line emitted the marker twice on one row —
            # '__DIVIDER__ __DIVIDER__', which the renderer then showed
            # literally because it is no longer a row of its own.
            solo = text == self.HEADMATTER_DIVIDER
            if segs and (
                page_changed or solo or abs(top - (cur_top or top)) > 3
                or segs[-1][1] == self.HEADMATTER_DIVIDER
            ):
                rows.append(emit(segs))
                counts.append(len(segs))
                segs = []
                if page_changed:
                    rows.append("")
                    counts.append(0)
            segs.append((x0, text))
            cur_page, cur_top = page, top
        if segs:
            rows.append(emit(segs))
            counts.append(len(segs))
        return (rows, counts) if with_counts else rows


def _is_caps_name(name: str) -> bool:
    """True if ``name`` looks like an ALL-CAPS surname (optionally Mc/Mac),
    e.g. 'HARBISON', 'McCONAHY', 'TERRELL JOINS' is rejected via word count."""
    toks = name.split()
    if not toks or len(toks) > 2:
        return False
    for tok in toks:
        core = tok
        if core.startswith("Mc"):
            core = core[2:]
        elif core.startswith("Mac"):
            core = core[3:]
        if not (core and core.isalpha() and core.isupper()):
            return False
    return True
