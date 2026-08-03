"""United States Court of Appeals for the Armed Forces ('armfor').

Title-first bylines ('Chief Judge OHLSON delivered the opinion of the
Court.' / 'Judge SPARKS, dissenting.') on the reversed-justice grammar
with Judge titles added.

Three structural quirks of the slip opinion, all handled here:

* The cover page (page 1) closes with an ANNOUNCEMENT of every writing
  in the case ('Judge SPARKS announced the judgment of the Court, in
  which Judge MAGGS joined. Judge HARDY filed a separate concurring
  opinion ...'), set in the same face and size as a real byline and
  followed by the front matter's closing underscore rule. It is a
  roster, not an opinion start.
* Every page after the cover carries a running head of two OR THREE
  lines — the italic case cite plus the writing label, which itself
  wraps ('Chief Judge OHLSON, with whom' / 'Judge HARDY joins,
  dissenting'). The head is set a point and a half smaller than the
  body; the wrapped second half parses as a byline, so left in the flow
  it births a phantom opinion per page.
* Real bylines always WRAP onto a second (occasionally third) line, and
  the break can fall mid-word ('... joins, con-' / 'curring in the
  judgment.'). Parsed line-by-line the byline either vanishes (so the
  writing is swallowed by the previous one, taking its footnotes with
  it) or resolves to the wrong judge.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme, _allcaps_token


class ArmedForcesCourt(ReversedJusticeSupreme):
    court_id = "armfor"
    court_label = "United States Court of Appeals for the Armed Forces."
    rev_titles = (
        "CHIEF JUDGE",
        "SENIOR JUDGE",
        "JUDGE",
    ) + ReversedJusticeSupreme.rev_titles
    # The running head is set below body size (10.6 or 11pt against a 12pt
    # body) at the very top of the sheet. Block quotations and bold section
    # headings are ALSO set at 11pt and can open a page, so size alone can't
    # carry the decision — see ``page_lines``.
    head_band_max_size = 11.9
    head_band_max_top = 110.0
    head_band_max_gap = 17.0

    # ------------------------------------------------------------------
    # page furniture
    # ------------------------------------------------------------------
    def page_lines(self, page):
        """Drop the running-head band from every page after the cover.

        The band is the contiguous run of lines from the very top of the
        sheet that are (a) set below body size and (b) either REPEAT at the
        top of another page — the head is by definition running furniture —
        or sit within one line's leading of the line above. A fixed y cut
        (the previous approach) let the third line of a wrapped writing
        label survive and become a phantom byline on every page of a
        dissent; a size-only test ate 11pt block quotations and bold
        section headings that happen to open a page."""
        if not hasattr(self, "_armfor_dropped"):
            self._armfor_dropped = []
        lines = super().page_lines(page)
        if page.page_number == getattr(self, "_caption_pno", 1):
            return lines
        repeats = getattr(self, "_armfor_head_text", set())
        kept = []
        prev_top = None
        for l in lines:
            if prev_top is not None or not kept:
                size = self.line_meta(l)[0]
                key = " ".join(self.line_plain_text(l).split()).lower()
                running = key in repeats
                near = prev_top is not None and (
                    l.get("top", 0) - prev_top <= self.head_band_max_gap
                )
                if (
                    l.get("top", 0) < self.head_band_max_top
                    and size
                    and size < self.head_band_max_size
                    # the cite line opens the sheet above any text measure
                    and (running or near or l.get("top", 0) < 50)
                ):
                    if key:
                        self._armfor_dropped.append(self.line_plain_text(l).strip())
                    prev_top = l.get("top", 0)
                    continue
                prev_top = None
            kept.append(l)
        return kept

    # ------------------------------------------------------------------
    # wrapped bylines
    # ------------------------------------------------------------------
    def _rev_title_head(self, text: str) -> bool:
        """True when ``text`` opens with this court's title + an ALL-CAPS
        surname — the shape of a byline's first line. Body prose that
        mentions a judge uses title case ('As Judge Sparks notes'), so the
        all-caps surname is the discriminator."""
        up = text.upper()
        title = next((t for t in self.rev_titles if up.startswith(t + " ")), None)
        if title is None:
            return False
        rest = text[len(title) + 1 :].split()
        return bool(rest) and _allcaps_token(rest[0])

    @staticmethod
    def _heal_wrap(text: str) -> str:
        """A byline broken mid-word rejoins across the wrap: '... con-
        curring' reads 'concurring'. Used for PARSING only — the emitted
        byline keeps the printed hyphen so the coverage audit still finds
        both source lines."""
        out = []
        for tok in text.split():
            if out and out[-1].endswith("-") and tok[:1].islower():
                out[-1] = out[-1][:-1] + tok
            else:
                out.append(tok)
        return " ".join(out)

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        healed = self._heal_wrap(text)
        if healed != text:
            return super().parse_author_line(healed)
        return None

    def line_plain_text(self, line):
        joined = line.get("_armfor_byline")
        if joined is not None:
            return joined
        return super().line_plain_text(line)

    def _join_wrapped_byline(self, seg):
        """Fold a byline's continuation line(s) into its first line so the
        byline grammar sees one complete sentence. A byline sentence ends
        at a period; anything before that is a wrap."""
        if len(seg) < 2:
            return seg
        first = super().line_plain_text(seg[0]).strip()
        if not self._rev_title_head(first):
            return seg
        if first.endswith((".", ":")):
            return seg  # already complete
        for n in range(2, min(len(seg), 4) + 1):
            joined = " ".join(
                super(ArmedForcesCourt, self).line_plain_text(l).strip()
                for l in seg[:n]
            )
            if not joined.rstrip().endswith((".", ":")):
                continue
            if self.parse_author_line(joined) is None:
                continue
            merged = dict(seg[0])
            merged["chars"] = [c for l in seg[:n] for c in (l.get("chars") or [])]
            merged["x0"] = min(l["x0"] for l in seg[:n])
            merged["x1"] = max(l["x1"] for l in seg[:n])
            merged["text"] = joined
            merged["_armfor_byline"] = joined
            return [merged] + list(seg[n:])
        return seg

    def segment_lines(self, lines, page_width) -> list:
        return [
            self._join_wrapped_byline(seg)
            for seg in super().segment_lines(lines, page_width)
        ]

    def split_author_line(self, line):
        """A folded byline is the whole line — never split it back apart on
        the interior period of its first sentence."""
        if line.get("_armfor_byline") is not None:
            return line["_armfor_byline"].strip(), []
        return super().split_author_line(line)

    # ------------------------------------------------------------------
    # the cover-page announcement is not an opinion start
    # ------------------------------------------------------------------
    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        cap = getattr(self, "_caption_pno", 1)
        close = getattr(self, "_cover_close_top", None)
        if close is None:
            return starts
        out = []
        for i in starts:
            pno, seg, _kind = all_segments[i]
            if pno == cap and seg and seg[0].get("top", 0) < close:
                continue  # front-matter announcement of the writings
            out.append(i)
        return out

    def prepare_document(self, pdf) -> None:
        super().prepare_document(pdf)
        # y of the underscore rule that closes the cover's front matter.
        self._cover_close_top = None
        page = pdf.pages[0]
        for line in page.extract_text_lines():
            if self._is_separator_text(line):
                top = line["top"]
                if self._cover_close_top is None or top > self._cover_close_top:
                    self._cover_close_top = top
        # Text that RECURS at the top of the sheet is running head furniture.
        counts = {}
        for p in pdf.pages[1:]:
            seen = set()
            for line in p.extract_text_lines():
                if line["top"] >= self.head_band_max_top:
                    continue
                key = " ".join((line.get("text") or "").split()).lower()
                if key and key not in seen:
                    seen.add(key)
                    counts[key] = counts.get(key, 0) + 1
        self._armfor_head_text = {k for k, n in counts.items() if n >= 2}

    # ------------------------------------------------------------------
    def extract(self, pdf_path: str):
        self._armfor_dropped = []
        self._cover_close_top = None
        doc = super().extract(pdf_path)
        # Some decisions devote the first lines of page 2 to a roster of all
        # writings, then repeat the actual majority byline at the start of the
        # opinion on page 3.  An interior ``Judge NAME`` in the roster's third
        # wrapped line can be mistaken for a new, empty opinion.  The first two
        # lines are already retained as headmatter; return the third there as
        # well and discard only the phantom boundary.
        hm_rows = [row for row in doc.summary if isinstance(row, dict)]
        roster_open = (
            len(hm_rows) >= 2
            and str(hm_rows[-2].get("html", "")).rstrip().endswith(", in")
            and str(hm_rows[-1].get("html", "")).rstrip().endswith("and")
        )
        opinions = []
        for opinion in doc.opinions:
            author_low = opinion.author.lower()
            is_roster_tail = (
                roster_open
                and not opinion.blocks
                and not opinion.footnotes
                and " joined. judge " in author_low
                and " filed a separate opinion" in author_low
            )
            if is_roster_tail:
                prior = hm_rows[-1]
                row = dict(prior)
                row["html"] = opinion.author
                row["top"] = float(prior.get("top", 0)) + 15.0
                doc.summary.append(row)
                continue
            opinions.append(opinion)
        doc.opinions = opinions
        if self._armfor_dropped:
            seen, extra = set(), []
            for t in self._armfor_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # The footnote rule is drawn as a text line of underscores/dashes.
        best = None
        for line in page.extract_text_lines():
            t = (line.get("text") or "").strip()
            if (
                len(t) >= 4
                and all(c in "—–-_" for c in t)
                and line["top"] > page.height * 0.5
                and line["x0"] < page.width * 0.4
            ):
                if best is None or line["top"] < best:
                    best = line["top"]
        return best
