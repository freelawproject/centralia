"""The Business Court of Texas ('texbizct').

District-court model: one ruling by one judge. Page 1 carries the clerk's
e-filing stamp in the top-right corner ('FILED IN / BUSINESS COURT OF
TEXAS / <clerk>, CLERK / ENTERED / <date>' — dropped and recorded), the
neutral citation ('2026 Tex. Bus. 23'), the banner, a '§'-railed caption,
and a '══════' boxed doc-title heading ('MEMORANDUM OPINION AND ORDER
DENYING ...' — matched by prefix since the suffix is case-specific). The
judge signs an all-caps name over 'Judge of the Texas Business Court'.
"""

from __future__ import annotations

from ._district import DistrictBase


class TexasBusinessCourt(DistrictBase):
    # This court's separator decision is final. Overruled by the base chain's
    # retry, both synergy_thermogen filings lost their opinion outright (2091
    # body words -> 0) and five caption lines read as unplaced content. The four
    # documents that are 44-141 words short (kampmann, pradera_sfr, sri_shirdi,
    # westlake_longview) were ALREADY short before this flag and have their own
    # cause — measured, not assumed.
    footnote_sep_override_final = True


    court_id = "texbizct"
    court_label = "The Business Court of Texas."
    # The neutral cite ('2026 Tex. Bus. 23') can sit above the default top
    # margin, merged with a stamp row — the top band is handled here.
    margin_top = 2

    # A crowded footnote zone can contain eight or more consecutive,
    # superscript labels at x≈72.  DistrictBase's no-rule pleading-paper
    # fallback reads that stack as line numbers and strips labels 17–28.
    # Business Court slips never use pleading paper, so disable both gutter
    # detectors for this court.
    @staticmethod
    def _pleading_gutter_by_numbers(page):
        return None

    @staticmethod
    def _pleading_gutter_x(page):
        return None

    def extract(self, pdf_path):
        self._stamp_dropped = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Record the removed furniture BEFORE the completeness sweep runs.

        ``page_lines`` strips the clerk stamp and the appended e-filing
        certificate sheet; the sweep is what proves every source row landed
        somewhere, and it runs inside ``super().extract()``.  Adding to
        ``doc.dropped`` after that call is too late — the rows read as
        unplaced content — so the flush happens here.
        """
        extra = [t for t in dict.fromkeys(self._stamp_dropped) if t]
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    @staticmethod
    def _is_typed_double_rule(text) -> bool:
        """A typed '══════' row — the court's drawn-by-glyph title rule."""
        t = (text or "").strip()
        return bool(t) and all(ch in "═=" for ch in t) and len(t) >= 10

    def find_authors(self, all_segments):
        """Start below the closing rule of the front-matter title band.

        Every Business Court slip boxes its document title between two rules
        — a typed '══════' row (most templates) or a drawn double rule
        (DrinkPAK).  The row directly below the CLOSING rule opens the
        ruling.  A syllabus edition repeats the whole ruled caption/title on
        page 2, so the last title band on pages 1–2 is the operative one.
        The title itself stays between its rules in headmatter.
        """
        super().find_authors(all_segments)  # populate DistrictBase's signer
        self._texbiz_start_line = None

        # Candidate starts: the segment after one whose last line is a typed
        # rule.  ``page_lines`` marks the row below every such rule
        # ``_seg_break``, so a rule row always closes its segment.
        after_rule = [
            i + 1
            for i, (page, seg, _kind) in enumerate(all_segments)
            if page <= 2
            and seg
            and self._is_typed_double_rule(self.line_plain_text(seg[-1]))
        ]
        if after_rule:
            start = after_rule[-1]
        else:
            # No typed rule (DrinkPAK's title sits between DRAWN rules): fall
            # back to the last front-matter document title.
            titles = [
                i
                for i, (page, seg, _kind) in enumerate(all_segments)
                if page <= 2 and seg and self._is_heading(seg[0])
            ]
            if not titles:
                return []
            start = titles[-1] + 1

        for i in range(start, len(all_segments)):
            seg = all_segments[i][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if self._is_typed_double_rule(self.line_plain_text(seg[0])):
                continue
            self._texbiz_start_line = seg[0]
            return [i]
        return []

    def split_author_line(self, line):
        if line is getattr(self, "_texbiz_start_line", None):
            return getattr(self, "_district_author", None) or "", [line]
        return super().split_author_line(line)

    # ------------------------------------------------- wrapped bold headings
    # The court's section headings HANG: the first row sits at the section's
    # margin and every continuation is indented one step ('B. Plaintiffs have
    # not shown that either the church-autonomy doctrine or general /
    # principles of equity support their position.').  Both the generic
    # indented-first-line paragraph rule and the bold/alignment segment
    # boundary read that indent as something new and cut the heading
    # mid-phrase (CLAUDE.md principle 7).  The discriminator is the wrap: a
    # bold row that RAN TO the right measure must have continued, so the bold
    # row below it — never further left — is its continuation.  The far
    # commoner 'ANALYSIS' + 'A. …' pair, and 'PART TWO: …' + 'A. …', stop
    # short of the measure or step back out, and stay separate headings.
    @staticmethod
    def _is_bold_row(line) -> bool:
        """Every alphanumeric glyph on the row is bold (a heading row).

        ``_line_all_bold`` additionally requires the row to stop short of the
        measure, which is exactly what the FIRST row of a wrapped heading
        cannot do.
        """
        seen = False
        for char in line.get("chars") or []:
            text = char.get("text") or ""
            if not text.strip() or not text.isalnum():
                continue
            seen = True
            if "Bold" not in (char.get("fontname") or ""):
                return False
        return seen

    def _is_bold_wrap(self, prev, line) -> bool:
        """``line`` continues the wrapped bold heading row ``prev``."""
        if not (self._is_bold_row(prev) and self._is_bold_row(line)):
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        right_edge = pw - self.body_baseline_x0
        wrap_min = right_edge - 0.15 * (right_edge - self.body_baseline_x0)
        return (
            prev["x1"] >= wrap_min
            and line["x0"] >= prev["x0"] - 1
            and 0 < line["top"] - prev["top"] < 40
        )

    def segment_lines(self, lines, page_width) -> list:
        segments = super().segment_lines(lines, page_width)
        merged = []
        for seg in segments:
            if merged and seg and merged[-1] and self._is_bold_wrap(merged[-1][-1], seg[0]):
                merged[-1] = merged[-1] + seg
            else:
                merged.append(seg)
        return merged

    def classify_segment(self, seg) -> str:
        # A wrapped heading is single-spaced and indented on both margins, so
        # the geometric block-quote test claims it.  A run whose every row is
        # bold is a heading, not a quotation.
        if len(seg) > 1 and all(self._is_bold_row(line) for line in seg):
            return "body"
        return super().classify_segment(seg)

    def classify_paragraph(self, lines) -> str:
        tag = super().classify_paragraph(lines)
        # The hanging section headings are flush left, so the shared
        # centered-row heading test cannot see them.
        if tag == "p" and lines and all(self._is_bold_row(line) for line in lines):
            return "heading"
        return tag

    def split_body_paragraphs(self, seg) -> list:
        paras = super().split_body_paragraphs(seg)
        if len(paras) < 2:
            return paras
        merged = [paras[0]]
        for para in paras[1:]:
            if para and self._is_bold_wrap(merged[-1][-1], para[0]):
                merged[-1] = merged[-1] + para
            else:
                merged.append(para)
        return merged

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Separate the uncommon expressly labeled syllabus from headmatter."""
        syllabus, kept = [], []
        syllabus_page = None
        for seg in headmatter_segs:
            text = " ".join(
                self.line_plain_text(line).strip() for line in seg
            ).strip()
            chars = seg[0].get("chars") if seg else []
            page = (
                (chars or [{}])[0].get("page_number")
                if seg
                else None
            ) or (seg[0].get("page_number") if seg else None)
            if text.lower().startswith("syllabus"):
                syllabus_page = page
            if syllabus_page is not None and page == syllabus_page:
                syllabus.append(self.paragraph_text(seg))
            else:
                kept.append(seg)
        result = super().extract_headmatter(kept, page1_rules)
        if syllabus:
            result["syllabus"] = syllabus
        return result

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # Some Business Court templates omit the drawn two-inch rule.  The
        # footnote zone still has an unambiguous geometric opening: a raised
        # numeric label at the left text margin, followed by 10pt text below a
        # 13/14pt body.  Use that first label as the boundary.  If everything
        # above it is already footnote-sized, this is a continuation page and
        # the entire text column belongs to the carried footnote.
        lines = page.extract_text_lines()
        labelled = [
            (ln, self.detect_footnote_label(ln))
            for ln in lines
            if ln.get("top", 0) < self.margin_bottom
        ]
        # A footnote's own first line carries its prose beside the label.  A
        # raised marker INSIDE the body is frequently extracted onto its own
        # offset baseline out at the right edge, which also reads as a label —
        # anchoring the zone on that swallows the rest of the page's prose into
        # the footnote, so a bare label may not open the zone.
        labelled = [
            (ln, lab)
            for ln, lab in labelled
            if lab
            and lab.isdigit()
            and self.line_plain_text(ln).strip() != lab
        ]
        if not labelled:
            return None
        first = min(labelled, key=lambda pair: pair[0]["top"])[0]
        above_sizes = []
        for ln in lines:
            if not (self.margin_top <= ln.get("top", 0) < first["top"] - 2):
                continue
            chars = ln.get("chars") or []
            if chars:
                above_sizes.append(max(c.get("size", 0) for c in chars))
        if above_sizes and max(above_sizes) <= 10.6:
            return float(self.margin_top)
        return max(float(self.margin_top), first["top"] - 2)

    def page_lines(self, page):
        lines = super().page_lines(page)
        # The e-filing system appends its own certificate-of-service sheet
        # after the signed order.  It is administrative transmission
        # furniture, not part of the judicial writing.  Identify the sheet by
        # its invariant opening sentence, then retain every source row in the
        # explicit Removed bucket for coverage/review.
        # Read the sheet from the RAW page the way the coverage sweep does —
        # its service table runs past the bottom body margin, so the rows the
        # margin filter has already removed must be recorded too.
        raw = [
            t.strip()
            for t in (
                (
                    page.filter(
                        lambda o: o.get("upright", True) is not False
                    ).extract_text()
                    or ""
                ).splitlines()
            )
        ]
        if any(
            t.lower().startswith(
                "this automated certificate of service was created by the efiling system"
            )
            for t in raw[:4]
        ):
            if getattr(self, "_stamp_dropped", None) is None:
                self._stamp_dropped = []
            self._stamp_dropped.extend(t for t in raw if t)
            return []
        # A typed '══════' rule is a structural boundary just like a drawn one:
        # the row below it opens a new block (the title, then the ruling).
        # Without the break the closing rule and the opinion's first paragraph
        # share one segment and the opinion cannot start on that paragraph.
        for prev, ln in zip(lines, lines[1:]):
            if self._is_typed_double_rule(self.line_plain_text(prev)):
                ln["_seg_break"] = True
        if page.page_number != 1:
            return lines
        if getattr(self, "_stamp_dropped", None) is None:
            self._stamp_dropped = []
        kept = []
        for ln in lines:
            if ln["top"] >= 65:
                kept.append(ln)
                continue
            # Top band: the e-filing stamp owns the right half; the neutral
            # cite (left/center runs) stays. A row can merge both.
            keep_runs, drop_runs = [], []
            for run in self._caption_char_runs(ln):
                (drop_runs if run[0]["x0"] > page.width * 0.55 else keep_runs).append(
                    run
                )
            for run in drop_runs:
                txt = self.line_plain_text({"chars": run}).strip()
                if txt:
                    self._stamp_dropped.append(txt)
            if keep_runs:
                chars = [c for r in keep_runs for c in r]
                ln = dict(ln)
                ln["chars"] = chars
                ln["x0"] = min(c["x0"] for c in chars)
                ln["x1"] = max(c["x1"] for c in chars)
                kept.append(ln)
        return kept

    def _is_heading(self, line) -> bool:
        if super()._is_heading(line):
            return True
        low = self.line_plain_text(line).strip().lower()
        return low.startswith(
            ("memorandum opinion and order", "opinion and order", "order denying",
             "order granting")
        )

    # --------------------------------------------------------- signature block
    # The judge's title row closes the sign-off in three printed forms —
    # 'Judge of the Texas Business Court,', 'Judge, Texas Business Court,' and
    # a bare 'TEXAS BUSINESS COURT' under 'JUDGE <NAME>'.  All three name the
    # court on a SHORT row, which is what tells the title apart from body prose
    # that happens to mention the court ('Under the Business Court's statute
    # governing removal …').
    @classmethod
    def _is_sig_title(cls, text) -> bool:
        low = " ".join((text or "").split()).lower()
        if len(low) > 55 or "texas business court" not in low:
            return False
        return low.startswith("judge") or low.strip(" ,.") == "texas business court"

    @staticmethod
    def _is_sig_name(text) -> bool:
        """A printed judge name row: 2–5 capitalized tokens ('BRIAN STAGNER',
        'Hon. Melissa Andrews', 'JUDGE GRANT DORFMAN')."""
        toks = (text or "").strip().rstrip(",").split()
        if not 2 <= len(toks) <= 5:
            return False
        for tok in toks:
            core = tok.rstrip(".,").replace("-", "").replace("'", "")
            if not core or not core[0].isupper() or not core.isalpha():
                return False
        return True

    @classmethod
    def _sig_name_text(cls, text):
        """The judge's name from a printed name row, dropping a 'Judge' title
        prefix ('JUDGE GRANT DORFMAN' -> 'Grant Dorfman')."""
        name = " ".join((text or "").split()).rstrip(",")
        if not cls._is_sig_name(name):
            return None
        toks = name.split()
        if toks[0].rstrip(".,").lower() == "judge" and len(toks) >= 3:
            toks = toks[1:]
            name = " ".join(toks)
        if not name:
            return None
        return name.title() if name.isupper() else name

    def _signature_author(self, all_segments):
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, 0, -1):
            if self._is_sig_title(lines[i]):
                name = self._sig_name_text(lines[i - 1])
                if name:
                    return f"{name}, Judge"
        return super()._signature_author(all_segments)

    def _harvest_signature(self, doc):
        """Lift this court's sign-off block off the end of the ruling.

        The shared harvester anchors on the FEDERAL judicial titles, none of
        which a Texas Business Court judge signs under, so the whole block
        (signature graphic, printed name, title, division, date stamp) was
        being left in the opinion body.  The block's shape is invariant here:
        a run of short rows containing the court-naming title row, topped by
        the signature graphic.  The decretal line above it ('IT IS SO
        ORDERED.') is the ruling's last sentence and stays in the body.
        """
        super()._harvest_signature(doc)
        if doc.signature or not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        end = len(blocks)
        while end > 0 and blocks[end - 1].kind == "p" and self._is_page_number_text(
            self._untag(blocks[end - 1].text)
        ):
            end -= 1
        if end == 0:
            return

        def is_decretal(text):
            low = " ".join(self._untag(text or "").split()).lower()
            return low.rstrip(".").endswith("ordered") or low.startswith(
                ("it is so ordered", "so ordered")
            )

        picked, i = [], end - 1
        while i >= 0 and len(picked) < 8:
            b = blocks[i]
            if b.kind == "image":
                picked.append(i)  # the signature graphic tops the block
                i -= 1
                break
            if b.kind not in ("p", "blockquote", "heading"):
                break
            text = " ".join(self._untag(b.text or "").split())
            if not text or len(text) > 60 or is_decretal(text):
                break
            picked.append(i)
            i -= 1
        else:
            i = -1
        # A 'Date signed: …' row printed ABOVE the graphic belongs with it.
        if i >= 0 and blocks[i].kind in ("p", "blockquote"):
            above = " ".join(self._untag(blocks[i].text or "").split())
            if len(above) <= 60 and above.lower().startswith(
                ("date", "dated", "signed", "entered")
            ):
                picked.append(i)
                i -= 1
        # The graphic can be printed above the decretal line instead of below
        # it; take the graphic and leave the decretal in the body.
        if (
            i >= 1
            and blocks[i].kind in ("p", "blockquote", "heading")
            and is_decretal(blocks[i].text)
            and blocks[i - 1].kind == "image"
        ):
            picked.append(i - 1)
        if not any(
            self._is_sig_title(self._untag(blocks[j].text or "")) for j in picked
        ):
            return
        chosen = sorted(picked)
        doc.signature = [
            {"__image__": True, **(blocks[j].payload or {})}
            if blocks[j].kind == "image"
            else str(blocks[j].text)
            for j in chosen
        ]
        keep = set(chosen)
        op.blocks = [b for j, b in enumerate(blocks) if j not in keep]
