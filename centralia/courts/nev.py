"""Supreme Court of the State of Nevada.

Byline leads with a 'By the Court,' tag, then an abbreviated-title surname and a
colon: 'By the Court, BELL, J.:' / 'By the Court, STIGLICH, J.:'. Strip the tag
and the rest is the abbreviated-title colon form the shared base handles. A
'Jennifer Schwartz, Judge.' line is the trial judge (title-case name) and a
'HERNDON, C.J., and STIGLICH ... ' line is a panel roster — neither is the
opinion author.

Document styles in the corpus:
  * ADVANCE OPINIONS — the born-digital slip: a '142 Nev., Advance Opinion NN'
    header, the banner, an Open-Range caption, counsel, 'BEFORE THE SUPREME
    COURT, …', then 'By the Court, <NAME>, J.:'. These are the parsed ones.
  * SCANS — a handful of files carry no text layer at all; ``is_non_digital``
    stops them so nothing is invented from a raster.
  * E-FILED filings set in Century Schoolbook with an 'Electronically Filed /
    <date> / <clerk> / Clerk of Supreme Court' stamp block and a 'Docket … /
    Document …' footer instead of the seal.

Page furniture, all of it stamped ON TOP of a full-page raster letterhead and
therefore riddled with OCR noise, so it can only be identified geometrically:
  * the printed seal and form number in the bottom-left margin ('SUPREME COURT
    / OF / NEVADA' over '(O) 1947A'), set in 4-8pt type — an order of magnitude
    smaller than the 12-15pt body — and trailed by scanner speckle that OCRs
    into a different string on every page ('(0) 1947A 44t"r.'), so it never
    reads as a repeated running footer;
  * the clerk's FILING STAMP in the upper-right of page 1 ('FILED', the date,
    the clerk's name, 'BY … DEPUTY CLERK') — set in a face and size unlike the
    body's, which is what separates it from the caption's docket number sitting
    in the same column;
  * the e-filing stamp and 'Docket …' footer of the e-filed style.

Removing the stamp matters for more than tidiness: it lands BETWEEN the caption
rows, so its baselines chain 'Appellant,' to 'vs.' and the two rows extract as
one scrambled row ('Avsp.pellant, FILED') with a caption line lost.
"""

from __future__ import annotations

from collections import Counter

from ._abbrevtitle import AbbrevTitleSupreme

_TAG = "By the Court, "


class NevadaSupreme(AbbrevTitleSupreme):
    court_id = "nev"
    court_label = "Supreme Court of the State of Nevada."

    # Furniture geometry. The seal/form block is 4-8pt against a 12-15pt body,
    # so one size cap identifies it wherever it sits. The filing stamp is bound
    # to the right-hand third of the caption zone, and the e-filing footer to
    # the right-hand third of the bottom margin.
    furniture_max_size = 8.5
    left_margin_x = 100.0  # every body column in the corpus starts right of this
    stamp_zone_x = 0.55  # fraction of page width
    stamp_zone_top = (95.0, 350.0)
    bottom_band = 100.0  # points up from the page foot
    corner_band = 60.0  # bottom-left speckle band
    # Below the printed folio nothing is ever set: it is past the page's own
    # bottom margin, so anything there is scanner speckle off the raster.
    foot_band = 45.0

    def is_non_digital(self, pdf) -> bool:
        """Nevada slips print born-digital Times text OVER a full-page
        letterhead raster, so image cover alone misreads them as scans. A
        real scan in this corpus has NO text layer at all — require that."""
        if not super().is_non_digital(pdf):
            return False
        chars = sum(len(pg.chars) for pg in pdf.pages[:3])
        return chars < 100

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if not text.startswith(_TAG):
            return super()._byline_split(line)
        r = self._abbrev_parse(text[len(_TAG) :])
        if r is None:
            return None
        _name, _title, _kind, end = r
        # Keep the 'By the Court,' tag in the byline text (completeness — it
        # must still appear in the output); parse_author_line strips it for the
        # name/kind.
        full_end = len(_TAG) + end
        return text[:full_end], text[full_end:].lstrip(" —–")

    def parse_author_line(self, text):
        t = text.strip()
        if t.startswith(_TAG):
            t = t[len(_TAG) :]
            # The comma between surname and title is a typesetting convention,
            # not content, and the court drops it sometimes: 'By the Court,
            # PICKERING J.:' against the usual 'By the Court, BELL, J.:'. Once
            # the tag is off, whatever remains IS the byline, so an all-caps
            # surname followed by a bare abbreviated title is one — supply the
            # comma the printer left out rather than lose the whole opinion
            # (nev._health_and_bioscience: 19 pages, all of it headmatter).
            parts = t.split()
            if len(parts) == 2 and "," not in parts[0]:
                name, title = parts
                if name.isupper() and any(
                    title.startswith(ab) for ab, _full in self.abbrev_titles
                ):
                    t = f"{name}, {title}"
        return super().parse_author_line(t)

    # ------------------------------------------------------- page furniture
    @staticmethod
    def _font_key(char) -> tuple:
        name = (char.get("fontname") or "").split("+")[-1]
        return name, round(char.get("size") or 0)

    def _body_font(self, chars) -> tuple:
        counts = Counter(
            self._font_key(c) for c in chars if (c.get("text") or "").strip()
        )
        return counts.most_common(1)[0][0] if counts else ("", 0)

    def _is_furniture_char(self, char, page, body) -> bool:
        """True for a glyph belonging to the seal/form block or a clerk stamp.

        Purely geometric/typographic, in three parts:

        * the seal and form number are sub-9pt type in the LEFT margin, left of
          every body column in the corpus. Size alone would not do: a footnote
          reference mark is set at the same 8.5pt, but inside the body column;
        * scanner speckle OCR'd into the bottom-left margin is not always tiny,
          so anything in that corner in a non-body face goes too;
        * a clerk stamp is text in the clerk's columns — the right of page 1's
          caption zone, or the right of the bottom margin — in a face/size the
          body never uses. The caption's own docket number shares that column
          but IS body type, so it survives."""
        x0 = char.get("x0", 0)
        top = char.get("top", 0)
        if top >= page.height - self.foot_band:
            return True  # below the folio: speckle only
        margin_col = x0 < self.left_margin_x
        if margin_col and (char.get("size") or 0) <= self.furniture_max_size:
            return True
        if self._font_key(char) == body:
            return False
        if margin_col:
            return top >= page.height - self.corner_band
        if x0 < page.width * self.stamp_zone_x:
            return False
        lo, hi = self.stamp_zone_top
        if page.page_number == 1 and lo <= top <= hi:
            return True
        return top >= page.height - self.bottom_band

    def correct_page_geometry(self, page) -> None:
        """Lift the seal/form block and the clerk stamps off the page.

        Done here rather than in ``page_lines`` for two reasons: the stamp has
        to be gone BEFORE lines are clustered (its baselines otherwise chain
        two caption rows into one scrambled row), and this hook is the same one
        the coverage audit reads the page through, so the removal is honest —
        the text is recorded and surfaced in the Removed box instead of being
        quietly deleted from one side of the ledger only."""
        super().correct_page_geometry(page)
        try:
            objs = page.objects.get("char")
        except Exception:
            objs = None
        if not objs:
            return
        body = self._body_font(objs)
        keep, junk = [], []
        for c in objs:
            (junk if self._is_furniture_char(c, page, body) else keep).append(c)
        if not junk:
            return
        objs[:] = keep
        if not hasattr(self, "_nev_dropped"):
            self._nev_dropped = {}
        # accumulate: this hook can be invoked more than once for a page
        self._nev_dropped.setdefault(page.page_number, []).extend(
            self._stamp_rows(junk)
        )

    @staticmethod
    def _stamp_rows(chars) -> list:
        """Removed glyphs regrouped into readable rows, so the Removed box
        shows the stamp as it was printed rather than a glyph soup. Rows are
        grouped by baseline proximity rather than a fixed bucket, so a row that
        straddles a bucket edge is not split in half."""
        rows: list = []
        for c in sorted(chars, key=lambda c: (c.get("top", 0), c.get("x0", 0))):
            if rows and abs(c.get("top", 0) - rows[-1][0]) <= 3.0:
                rows[-1][1].append(c)
            else:
                rows.append((c.get("top", 0), [c]))
        out = []
        for _top, line in rows:
            prev, parts = None, []
            for c in sorted(line, key=lambda c: c.get("x0", 0)):
                if prev is not None and c.get("x0", 0) - prev > 1.5:
                    parts.append(" ")
                parts.append(c.get("text") or "")
                prev = c.get("x1", 0)
            text = "".join(parts).strip()
            if text:
                out.append(text)
        return out

    # ------------------------------------------------------------- extract
    def extract(self, pdf_path: str):
        self._nev_dropped = {}
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the removed stamps BEFORE the completeness sweep runs, so
        they are matched against ``doc.dropped`` rather than reported unplaced."""
        rows = [
            t
            for _pno in sorted(getattr(self, "_nev_dropped", {}))
            for t in self._nev_dropped[_pno]
        ]
        if rows:
            seen, extra = set(), []
            for t in rows:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)
