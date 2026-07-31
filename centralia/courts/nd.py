"""North Dakota Supreme Court.

Palatine-set opinions on a title page + body. The title page (page 1) carries the
banner ('IN THE SUPREME COURT / STATE OF NORTH DAKOTA'), the neutral citation
('2026 ND 70'), the caption, the docket ('No. 20250357'), the appeal-from line
and its trial judge ('Honorable James D. Gion, Judge.' — NOT the author), the
disposition, the announced author ('Opinion of the Court by Fair McEvers, Chief
Justice.'), and the counsel block. All of that stays in the headmatter.

The opinion proper opens on page 2 with a bold, name-first byline — a Title-Case
surname and a judicial title ('Fair McEvers, Chief Justice.', 'Bahr, Justice.')
or 'Per Curiam.' — and a running header above it (the bold case caption + docket,
'B.S., et al. v. Lopez-Rangel / No. 20250357') that is dropped as furniture. Body
paragraphs are numbered with bracketed pilcrows ('[¶1]', '[¶2]') and are
otherwise flush left, so they are split on the marker, not on indentation.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


def _dedupe(rows):
    """Order-preserving de-duplication tolerant of unhashable rows."""
    seen, out = set(), []
    for r in rows:
        try:
            if r in seen:
                continue
            seen.add(r)
        except TypeError:  # image/dict rows are never repeated
            pass
        out.append(r)
    return out


def _nd_name(s: str) -> bool:
    """A Title-Case surname byline name ('Bahr', 'Fair McEvers', "O'Brien"),
    1–4 tokens, each opening with a capital."""
    toks = s.split()
    if not toks or len(toks) > 4:
        return False
    for tok in toks:
        core = tok.rstrip(".").replace("'", "").replace("’", "").replace("-", "")
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class NorthDakotaSupreme(StateSupreme):
    court_id = "nd"
    court_label = "In the Supreme Court, State of North Dakota."

    # The opinion body is single-spaced (~19pt leading), so the default gap
    # bands read every flush-left body run as a block quote. Retune the bands
    # to the single-spaced rhythm — body ~19pt, indented quotes ~16pt — so the
    # body classifies as body and the tighter quote as a quote.
    gap_tight_max = 14
    gap_single_max = 17
    # Quotes indent one 36pt step (flush body x0=72 → quote x0=108). Both-
    # margins-indented runs are the geometric block-quote tell, and the smaller
    # indent step lets the segmenter split a 36pt quote indent off the body.
    blockquote_by_indent = True
    indent_step = 22

    # North Dakota's genuine tables are narrow (the fictitious-citation table in
    # city_of_dickinson has four columns). A JUSTIFIED block quote, though, is
    # set with wide inter-word gaps, and pdfplumber's whitespace-derived column
    # finder reads every gap as a column edge — a quoted standard-of-review
    # passage came back as a 46-column 'table' whose cells were mostly empty,
    # which swallowed the quote (and lost its closing line, whose final period
    # fell outside a cell). Cap the plausible column count.
    _max_table_cols = 8

    def extract(self, pdf_path):
        self._nd_dropped = []
        doc = super().extract(pdf_path)
        self._harvest_nd_signature(doc)
        # Record the dropped running headers (deduped) so they are accounted for
        # rather than silently lost. _sweep_residual already published them;
        # this collapses the repeat and catches any recorded after the sweep.
        doc.dropped = _dedupe(list(doc.dropped) + list(self._nd_dropped))
        return doc

    def _sweep_residual(self, doc, source_pages):
        """Publish the dropped page-2 running header BEFORE the completeness
        sweep reads ``doc.dropped`` — the sweep runs inside ``super().extract()``,
        so appending afterwards left the header ('Alber v. Rodin, et al.')
        reporting as unplaced content."""
        head = [t for t in getattr(self, "_nd_dropped", None) or [] if t]
        if head:
            doc.dropped = _dedupe(list(doc.dropped) + head)
        super()._sweep_residual(doc, source_pages)

    # ------------------------------------------------------ signature roster
    @staticmethod
    def _untag(text: str) -> str:
        import re as _re

        return _re.sub(r"<[^>]+>", "", text or "")

    def _strip_pilcrow(self, text: str) -> str:
        """Drop a leading '[¶N]' / '¶N' paragraph marker."""
        t = text.lstrip()
        if t.startswith("[¶"):
            i = t.find("]")
            if i != -1:
                return t[i + 1 :].lstrip()
        elif t.startswith("¶"):
            i = 1
            while i < len(t) and (t[i].isdigit() or t[i] == " "):
                i += 1
            return t[i:].lstrip()
        return text

    def _is_roster_line(self, text: str) -> bool:
        """A panel-roster line: a justice's full name, optionally closed by a
        judicial title ('Lisa Fair McEvers, C.J.' / plain 'Daniel J. Crothers').
        A middle initial ('J.') counts as a name token."""
        t = self._strip_pilcrow(self._untag(text)).strip()
        if not t:
            return False
        if "," in t:
            name, after = t.split(",", 1)
            low = after.lower()
            if "j." not in low and "justice" not in low:
                return False
            return _nd_name(name.strip())
        return _nd_name(t)

    def _is_stacked_roster(self, seg) -> bool:
        """A block-quote-classified segment that is really a stacked name roster
        — every line a roster name — so it is split one name per line rather
        than joined into a single quoted paragraph."""
        if len(seg) < 2:
            return False
        return all(
            self._is_roster_line(self.line_plain_text(l).strip()) for l in seg
        )

    def _harvest_nd_signature(self, doc) -> None:
        """Lift the trailing panel roster (the authoring justice's titled
        sign-off and the concurring justices, one name per line) off the last
        opinion into the Signature section so the names keep their line breaks.
        The roster must open with a titled sign-off (', C.J.' / ', Justice')."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        take = 0
        for b in reversed(blocks):
            if self._is_roster_line(b.text):
                take += 1
            else:
                break
        if take < 2:
            return
        sig = blocks[-take:]
        first = self._strip_pilcrow(self._untag(sig[0].text)).strip()
        if "," not in first:
            return  # not anchored on a titled sign-off — leave the body alone
        doc.signature = [str(b.text) for b in sig]
        op.blocks = blocks[:-take]

    # ------------------------------------------------------- running header
    def _maybe_drop_running_header(self, page, lines):
        """Drop the page furniture on continuation pages: the bold, CENTERED
        case-caption + docket band at the very top and the bottom-centered bare
        page number. The opinion opens right below that band with a bold but
        flush-left byline (a name-first justice line or 'Per Curiam.'), so
        keying on centering — not a bare top cutoff — keeps a byline that sits
        as high as ~top 104. Title page (page 1) is untouched; dropped lines
        are recorded."""
        if page.page_number <= 1:
            return lines
        kept = []
        for ln in lines:
            _size, _font, bold = self.line_meta(ln)
            t = self.line_plain_text(ln).strip()
            centered = ln.get("x0", 0) > 150
            if bold and centered and ln.get("top", 999) < 110:
                if t:
                    getattr(self, "_nd_dropped", []).append(t)
                continue
            if ln.get("top", 0) > 700 and self._is_page_number_text(t):
                if t:
                    getattr(self, "_nd_dropped", []).append(t)
                continue
            kept.append(ln)
        return kept

    # ------------------------------------------------------ table header band
    def extract_page_tables(self, page):
        """ND sets a table's column-header band at the foot of one page — two
        long vector rules with only sub-body text between them — and the grid
        body at the top of the next. find_tables misses the band (it has no
        vertical lines), so it leaks into the body as one merged paragraph.
        Detect it geometrically and emit it as its own one-row table block.

        Candidates with an implausible column count are discarded first: a
        JUSTIFIED block quote is set with wide inter-word gaps, and
        pdfplumber's whitespace-derived column finder reads every gap as a
        column edge, so a quoted standard-of-review passage came back as a
        47-column 'table' of mostly empty cells. That swallowed the quote and
        lost its closing line (whose final period fell outside every cell)."""
        tables = [
            t
            for t in super().extract_page_tables(page)
            if max((len(r) for r in t["rows"]), default=0) <= self._max_table_cols
        ]
        band = self._table_header_band(page, tables)
        if band:
            tables.append(band)
        return tables

    def _table_header_band(self, page, tables):
        body_size = 13.0
        rules = sorted(
            (ln["top"], min(ln["x0"], ln["x1"]), max(ln["x0"], ln["x1"]))
            for ln in page.lines
            if abs(ln.get("bottom", ln["top"]) - ln["top"]) <= 2
            and (max(ln["x0"], ln["x1"]) - min(ln["x0"], ln["x1"])) >= 400
            and ln["top"] > page.height * 0.5
        )
        text_lines = page.extract_text_lines()
        for (top1, rx0, rx1), (top2, _, _) in zip(rules, rules[1:]):
            if not 10 < top2 - top1 < 70:
                continue
            # never re-table a region find_tables already owns
            if any(
                t["bbox"][1] - 4 <= top1 and top2 <= t["bbox"][3] + 4
                for t in tables
            ):
                continue
            between = [
                ln for ln in text_lines if top1 + 1 < ln["top"] < top2 - 1
            ]
            below = [
                ln
                for ln in text_lines
                if ln["top"] > top2 + 1
                and not self._is_page_number_text((ln.get("text") or ""))
            ]
            if not between or below:
                continue  # band must close the page (table continues overleaf)
            sizes = [
                c["size"]
                for ln in between
                for c in (ln.get("chars") or [])
                if c.get("size")
            ]
            if not sizes or max(sizes) > body_size - 2:
                continue  # header bands are set below body size
            # Cluster the lines' runs into columns by x-overlap.
            runs = [
                r
                for ln in between
                for r in self._split_line_runs(ln)
                if (r.get("text") or "").strip()
            ]
            cols = []  # [(x0, x1, [runs])]
            for r in sorted(runs, key=lambda r: r["x0"]):
                for col in cols:
                    if r["x0"] < col[1] and r["x1"] > col[0]:
                        col[2].append(r)
                        col[0], col[1] = (
                            min(col[0], r["x0"]),
                            max(col[1], r["x1"]),
                        )
                        break
                else:
                    cols.append([r["x0"], r["x1"], [r]])
            if len(cols) < 2:
                continue
            row = [
                "\n".join(
                    (r.get("text") or "").strip()
                    for r in sorted(col[2], key=lambda r: r["top"])
                )
                for col in sorted(cols, key=lambda c: c[0])
            ]
            return {"bbox": (rx0, top1, rx1, top2), "rows": [row]}
        return None

    # ----------------------------------------------------- footnote separator
    def find_footnote_separator(self, page):
        """ND draws the footnote separator as a short (~143pt) left-anchored
        VECTOR line, not a rect, so the base rect scan misses it and the
        footnotes fall into the body. Scan ``page.lines`` for that rule; the
        width gate rejects full-measure (~470pt) vector lines, which are table
        borders rather than separators."""
        cutoff = page.height * 0.5
        best = None
        for ln in page.lines:
            x0, x1 = sorted((ln["x0"], ln["x1"]))
            top = ln["top"]
            if abs(ln.get("bottom", top) - top) > 2:
                continue  # horizontal rules only
            if top <= cutoff or x0 > self.body_baseline_x0 + 4:
                continue
            if not (100 <= (x1 - x0) <= 300):
                continue
            if not self._rule_over_footnotes(page, top):
                continue
            if best is None or top < best:
                best = top
        return best

    # --------------------------------------------------------------- byline
    def _byline_split(self, line):
        """A bold, name-first byline: a Title-Case surname + judicial title
        ('Fair McEvers, Chief Justice.'), or 'Per Curiam.'. Bold is the tell
        (the announcement 'Opinion of the Court by ...' and the trial-judge line
        are not bold), so the body half is always empty."""
        text = self.line_plain_text(line).strip()
        chars = line.get("chars") or []
        if not text or not chars:
            return None
        if "bold" not in (chars[0].get("fontname") or "").lower():
            return None
        if text.rstrip(".").lower() == "per curiam":
            return text, ""
        if "," not in text:
            return None
        name, after = text.split(",", 1)
        if not _nd_name(name.strip()):
            return None
        low = after.lower()
        if "justice" not in low and "judge" not in low:
            return None
        return text, ""

    # ------------------------------------------------- [¶N] body paragraphs
    def _split_on_pilcrow(self, seg):
        if not seg:
            return []
        paras = [[seg[0]]]
        for line in seg[1:]:
            if self.line_plain_text(line).lstrip().startswith(("[¶", "¶")):
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def _begins_paragraph_block(self, lines):
        """A [¶N]-numbered line always opens a fresh paragraph, so it must
        never be folded into the previous paragraph across a page break."""
        if not lines:
            return False
        return self.line_plain_text(lines[0]).lstrip().startswith(("[¶", "¶"))

    def split_body_paragraphs(self, seg):
        return self._split_on_pilcrow(seg)

    def split_blockquote_paragraphs(self, seg):
        # A trailing panel roster reads as a both-margins-indented block quote;
        # keep each stacked name on its own line instead of joining them.
        if self._is_stacked_roster(seg):
            return [[ln] for ln in seg]
        return self._split_on_pilcrow(seg)
