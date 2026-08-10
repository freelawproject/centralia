"""Shared base for the U.S. district courts.

A district-court filing is one ruling by one judge, not the multi-opinion
byline-at-start shape of an appellate decision. So the model differs:

  * The author is taken from the **signature block** at the end — the line
    above a 'United States District Judge' / 'Magistrate Judge' title (the most
    universal signal across districts), or, failing that, from a 'Present: The
    Honorable NAME, ... JUDGE' minute-order line, a 'THE HONORABLE NAME, U.S.D.J.'
    heading, a caption 'Judge NAME' line, or a 'NAME, J.' byline.
  * The opinion begins at the document-type heading ('MEMORANDUM OPINION AND
    ORDER' / 'ORDER' / 'REPORT AND RECOMMENDATION' / ...) — the caption above it
    is headmatter — or, if there is no heading, at the first body paragraph.
  * The whole ruling is one opinion (docket orders included, per the project's
    'treat orders as opinions' rule).

The CM/ECF header band ('Case 1:23-cv-00358 Document #: 111 Filed: ... Page 1
of 16 PageID #:...') sits in the top margin and is already excluded by
``margin_top``; per-district subclasses add any court-specific stamp handling.
No regex (project rule); headings and titles are matched with string sets.
"""

from __future__ import annotations

from .generic import GenericExtractor
from ..models import Block

# Document-type headings that open a district ruling (lowercased, exact match
# after stripping trailing punctuation). Longest/most-specific are not needed —
# any match marks the opinion start.
_HEADINGS = frozenset(
    {
        "memorandum opinion and order",
        "memorandum opinion",
        "memorandum and order",
        "memorandum order",
        "memorandum decision and order",
        "memorandum decision",
        "memorandum ruling",
        "memorandum",
        "memorandum & order",
        "opinion and order",
        "order and opinion",
        "opinion",
        "order",
        "amended memorandum opinion and order",
        "amended memorandum opinion",
        "report and recommendation",
        "report & recommendation",
        "report and recommendation of the magistrate judge",
        "findings of fact and conclusions of law",
        "findings of fact",
        "decision and order",
        "ruling",
        "judgment",
        "final judgment",
        "order and reasons",
        "memorandum ruling and order",
        "ruling and order",
        "memorandum opinion & order",
    }
)

# Opening words of a compound ALL-CAPS document title ('ORDER ADOPTING …',
# 'MEMORANDUM OPINION GRANTING …'). A short ALL-CAPS line starting with one of
# these is the ruling's title, hence its start — not trailing headmatter.
_HEADING_STARTS = frozenset(
    {"order", "memorandum", "opinion", "findings", "judgment", "decision", "report"}
)

# Judicial titles that close a signature block; the line above carries the name.
_JUDGE_TITLES = (
    "united states district judge",
    "united states magistrate judge",
    "united states bankruptcy judge",
    "united states circuit judge",
    "senior united states district judge",
    "chief united states district judge",
    "senior united states magistrate judge",
    "u.s. district judge",
    "u.s. magistrate judge",
    "u.s.d.j.",
    "u.s.m.j.",
    "chief united states magistrate judge",
    "united states district court judge",
    "chief judge",
    "senior district judge",
    "district court judge",
    "district judge",
    "magistrate judge",
)
# Lines that sit in a signature block but are not the judge's name.
_SIG_SKIP = (
    "so ordered",
    "it is so ordered",
    "dated",
    "date",
    "entered",
    "signed",
    "s/",
    "/s/",
    "by the court",
)
# A date stamp ('Dated: …' / 'Signed: …') is part of the signature block — it
# sits between the conformed signature / image and the printed name, so the
# backward scan must include it and keep going (a 'so ordered' decretal does
# NOT, hence this is a strict subset of _SIG_SKIP).
_SIG_DATE = ("dated", "date", "signed", "entered")

# Headmatter-facsimile geometry.
_CAPTION_GAP = 8.0  # x-gap (pt) that separates caption runs / the divider
_CAPTION_CHAR_W = 6.0  # monospace column width
_CAPTION_LEFT = 72.0  # left text margin (column 0)


def _is_rule(text: str) -> bool:
    t = text.strip()
    return len(t) >= 3 and all(c in "_-–—" for c in t)


def _strip_sig_prefix(text: str) -> str:
    t = text.strip()
    for p in ("/s/", "s/"):
        if t.lower().startswith(p):
            return t[len(p) :].strip()
    return t


def _looks_like_name(text: str) -> bool:
    """A judge name in a signature block: 2–5 tokens, each capitalized
    (all-caps 'ROY K. ALTMAN' or title-case 'Shalina D. Kumar'), allowing
    initials, 'Jr.'/'III', hyphens."""
    t = _strip_sig_prefix(text).rstrip(",")
    toks = t.split()
    if not (2 <= len(toks) <= 6):
        return False
    for tok in toks:
        core = tok.rstrip(".,").replace("-", "").replace("'", "")
        if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
            continue
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class DistrictBase(GenericExtractor):
    drop_notice_in_body = False
    # District filings double-space the body but single-space block quotes at a
    # tight leading (Courier/Times ~13-15pt) — below gap_tight_max — so an
    # indented quote reads as a 'notice'. Re-tag it by its both-margins indent.
    blockquote_by_indent = True
    # A paragraph that is nothing but a page number is the page's folio, never
    # body text — fold it out and let the residual sweep surface it in the
    # Removed box.
    fold_page_numbers = True
    # A district ruling closes on a STACK of short lines — signature rule,
    # printed name, title, court, date, place — none of which reaches the
    # right measure, so none of them wrapped and none of them is a
    # continuation of the line above. Joining them produces run-ons
    # ('ELIZABETH A. WOLFORD Chief Judge United States District Court') and
    # hides the title line the signature block is anchored on. Body prose is
    # untouched: a real wrapped paragraph always has full-measure lines.
    split_line_stacks = True
    # CM/ECF header-band captures (see page_lines); class defaults so a court
    # whose pipeline never routes page 1 through page_lines still reads clean.
    _ecf_docket = None
    _ecf_filed = None

    def extract(self, pdf_path):
        self._hm_super_labels = set()
        # A body-sized footnote can continue under an unlabeled separator on
        # the next page.  ``find_footnote_separator`` is called in page order,
        # so retain only the measured shape of a footnote that geometrically
        # runs through the bottom of the preceding page.
        self._footnote_carry_geometry = None
        doc = super().extract(pdf_path)
        labels = getattr(self, "_hm_super_labels", set())
        if labels and doc.opinions:
            op = doc.opinions[0]
            moved = [f for f in op.footnotes if f.label in labels]
            if moved:
                op.footnotes = [f for f in op.footnotes if f.label not in labels]
                doc.headmatter_footnotes = list(doc.headmatter_footnotes) + moved
        self._harvest_signature(doc)
        self._lift_district_date(doc)
        return doc

    def _lift_district_date(self, doc) -> None:
        """Populate decision_date, family-wide.

        The typed date stamp in the signature block ('Signed: May 18, 2026' /
        'Dated: …' / 'DATED this 3rd day of …') is authoritative when present;
        otherwise the CM/ECF header band's 'Filed 05/11/26' — printed on every
        filing — read off in page_lines before margin_top discards it."""
        if doc.decision_date:
            return
        rows = [str(s) for s in (doc.signature or [])]
        if doc.trailer:
            rows.extend(str(t) for t in doc.trailer)
        for op in doc.opinions:
            rows.extend(str(b.text or "") for b in op.blocks[-4:])
        for row in rows:
            text = self._untag(row).strip()
            for label in ("Signed:", "Dated:", "DATED:", "Entered:", "ENTERED:", "Date:"):
                at = text.find(label)
                if at != -1:
                    tail = text[at + len(label) :].strip()
                    if tail and any(ch.isdigit() for ch in tail):
                        doc.decision_date = tail
                        return
        if getattr(self, "_ecf_filed", None):
            doc.decision_date = self._ecf_filed

    @staticmethod
    def _untag(text: str) -> str:
        """Plain text of a block's inline-HTML string (no markup)."""
        out, i = [], 0
        s = str(text)
        while True:
            j = s.find("<", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            k = s.find(">", j)
            if k < 0:
                break
            i = k + 1
        return "".join(out)

    def _caption_band_bottom(self):
        """The y of the page-1 caption's bottom edge, as the fingerprint
        measured it — or None when the caption's shape was not recognised.

        The three structures that close a caption, most specific first: a
        glyph rail column (')' / ':' / '§'), a drawn mid vertical, and a pair
        of TYPED rules (the New York districts' '--------x'). Everything that
        needs to know where the caption ends — the opinion start, the footnote
        separator, the page-1 shelf test — reads it from here, so they cannot
        disagree about the caption's extent."""
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        if not sig:
            return None
        rail_band = sig.get("rail_band")
        if rail_band:
            return rail_band[1]
        if sig.get("vmid") and sig.get("band"):
            return sig["band"][1]
        typed_band = sig.get("typed_band")
        if typed_band:
            return typed_band[1]
        return None

    def _harvest_signature(self, doc):
        """Lift the signature block off the END of the last opinion into
        ``doc.signature``: the '/s/' conformed signature (or the underscore
        signature rule), the printed name, and the signer's title line.
        Fires only when the very last body block is a judge-title line, so
        ordinary prose endings are never touched."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        if not blocks:
            return

        def is_title(t):
            low = t.strip().rstrip(".").lower()
            return any(
                low == jt.rstrip(".") or low.endswith(" " + jt.rstrip("."))
                for jt in _JUDGE_TITLES
            )

        # An image-signed order: 'Signed: <date>' / 'ENTER: <date>' followed
        # by a signature GRAPHIC (the name + title live inside the image, so
        # there is no title text line to anchor on). The date line and the
        # image together are the signature block. A trailing bare page
        # number after the image is ignored when anchoring.
        end = len(blocks)
        while end > 0 and blocks[end - 1].kind == "p" and (
            self._is_page_number_text(self._untag(blocks[end - 1].text))
        ):
            end -= 1
        if end >= 2 and blocks[end - 1].kind == "image":
            prev = self._untag(blocks[end - 2].text).strip().lower()
            # a date stamp ('Signed:' / 'ENTER:' / 'Dated:') belongs WITH
            # the signature; decretal prose ('IT IS SO ORDERED.') stays in
            # the body — only the image moves.
            if any(
                prev.startswith(sk)
                for sk in ("signed", "dated", "date", "enter", "entered")
            ):
                doc.signature = [
                    str(blocks[end - 2].text),
                    {"__image__": True, **(blocks[end - 1].payload or {})},
                ]
                op.blocks = blocks[: end - 2] + blocks[end:]
            elif any(prev.startswith(sk) for sk in _SIG_SKIP):
                doc.signature = [
                    {"__image__": True, **(blocks[end - 1].payload or {})}
                ]
                op.blocks = blocks[: end - 1] + blocks[end:]
            return
        # Otherwise the block is the trailing run of SIGN-OFF lines: the
        # conformed signature or its rule, the printed name, the title, the
        # court, and the date/place stamp — in whatever order the district
        # prints them (E.D.N.Y. puts 'Dated: …' / 'Brooklyn, New York' BELOW
        # the title; W.D.N.Y. puts them below the court line). They are all
        # short, none of them closes a sentence, and the run stops the moment
        # real prose appears above it ('SO ORDERED.'). The run only counts as
        # a signature if it names a judicial title, so an ordinary short
        # closing line can never be lifted out of the body.
        run: list[int] = []
        i = end - 1
        while i >= 0 and len(run) < 7:
            b = blocks[i]
            if b.kind == "image":
                run.append(i)  # the signature graphic tops the block
                break
            # 'p' or 'blockquote' — a tightly-led, indented sign-off is
            # tagged as a quote by the paragraph classifier, which says
            # nothing about whether it is one.
            if b.kind not in ("p", "blockquote"):
                break
            t = self._untag(b.text).strip()
            low = t.lower()
            if not t:
                break
            if low.startswith("/s/") or low.startswith("s/"):
                run.append(i)  # the conformed signature tops the block
                break
            if len(t) >= 4 and set(t) <= {"_"}:
                run.append(i)  # the typed signature rule tops the block
                break
            if not (
                is_title(t)
                or any(low.startswith(sk) for sk in _SIG_DATE)
                or (
                    len(t) <= 48
                    and not t.endswith(".")
                    and not any(low.startswith(sk) for sk in _SIG_SKIP)
                )
            ):
                break
            run.append(i)
            i -= 1
        if len(run) < 2:
            return
        if not any(
            blocks[j].kind in ("p", "blockquote")
            and is_title(self._untag(blocks[j].text))
            for j in run
        ):
            return
        first = min(run)
        doc.signature = [
            {"__image__": True, **(b.payload or {})}
            if b.kind == "image"
            else str(b.text)
            for b in blocks[first:end]
        ]
        op.blocks = blocks[:first] + blocks[end:]

    # ----------------------------------------- pleading-paper line numbers
    def page_lines(self, page):
        """On pleading paper (California etc.), a left gutter carries the
        sequential line numbers 1-28, set off from the body by a vertical margin
        rule; pdfplumber merges each number onto its line ('1 However ...'). When
        that rule is present, drop the chars left of it so the body reads cleanly
        without the line numbers. Gated on the rule (or, when no rule is drawn,
        on the number column itself), so ordinary CM/ECF filings are untouched."""
        gx = self._pleading_gutter_x(page)
        if gx is None:
            gx = self._pleading_gutter_by_numbers(page)
        if gx is not None:
            page = page.filter(lambda c: c["x0"] >= gx - 1)
        # The CM/ECF header band ('Case 3:25-cv-00691-wmc Document #: 22 …')
        # is furniture cut by margin_top before lines are built — but it is
        # also the one place EVERY filing prints its case number, including
        # documents whose caption shows it bare or not at all. Read the token
        # off before the band disappears.
        if page.page_number == 1:
            # per-document; instances are reused across a batch
            self._ecf_docket = None
            self._ecf_filed = None
        if getattr(self, "_ecf_docket", None) is None or (
            getattr(self, "_ecf_filed", None) is None
        ):
            # The stamp prints at the top on most districts and at the BOTTOM
            # on others (ncwd, akd); flsd words it 'Entered on FLSD Docket
            # 04/22/2026' instead of 'Filed 05/11/26'.
            band = page.filter(
                lambda c: c["top"] < self.margin_top + 6
                or c["top"] > self.margin_bottom - 6
            )
            words = band.extract_words()
            for i, word in enumerate(words):
                token = (word.get("text") or "").rstrip(",;)")
                if self._ecf_docket is None and self._is_ecf_case_token(token):
                    self._ecf_docket = token
                if (
                    self._ecf_filed is None
                    and token.rstrip(":").lower() in ("filed", "docket")
                    and i + 1 < len(words)
                ):
                    nxt = (words[i + 1].get("text") or "").strip()
                    if "/" in nxt and any(ch.isdigit() for ch in nxt):
                        self._ecf_filed = nxt
        return super().page_lines(page)

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """Gutter right-edge x inferred from the line-number column when NO
        margin rule is drawn: a far-left stack of pure integers running roughly
        1, 2, 3, … down the page. Returns the numbers' right edge (chars left of
        it are the gutter), or None. Requires a long, mostly-sequential run so an
        ordinary filing's stray leading digits never trip it."""
        nums = [
            (int(w["text"]), w["x1"], w["top"])
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if len(nums) < 8:
            return None
        # The gutter is ONE narrow column, so its numbers share a right edge to
        # within a digit's width. Cluster on that edge and keep the biggest
        # cluster before measuring anything.
        #
        # Taking the max over the raw candidate set is what made this wrong: a
        # body line that opens on a small integer — a citation like '27 I&N
        # Dec. 509' or '28 U.S.C. § 2243' — qualifies as a candidate too, and
        # sits far to the right of the real column. One such citation dragged
        # the cut past the body's own left margin, so the char filter below ate
        # the first word of every full-width line on the page ("1 Opp'n at 1,
        # 2." came out as "at 1, 2."). Structural loss, invisible in the text.
        edges = sorted(n[1] for n in nums)
        best: list[float] = []
        cluster: list[float] = []
        for e in edges:
            if cluster and e - cluster[0] > 8:
                if len(cluster) > len(best):
                    best = cluster
                cluster = []
            cluster.append(e)
        if len(cluster) > len(best):
            best = cluster
        lo, hi = best[0], best[-1]
        column = [n for n in nums if lo <= n[1] <= hi]
        if len(column) < 8:
            return None
        column.sort(key=lambda n: n[2])  # top-to-bottom
        vals = [n[0] for n in column]
        runs = sum(1 for a, b in zip(vals, vals[1:]) if b == a + 1)
        if runs < 6:
            return None
        # A gutter sits BESIDE the body, never inside it: nothing but the
        # numbers themselves may lie to the left of the cut. Count the words
        # that would be sacrificed and refuse the cut if there are more than a
        # stray one or two.
        #
        # Without this gate the run test alone was satisfied on filings that
        # are not pleading paper at all — a footnote block's stacked markers
        # read as a sequential column at x≈78 on a body whose left margin is
        # x=72, and the char filter then shaved the first LETTER off every line
        # ('hearing.' → 'earing.', 'Court.' → 'ourt.').
        #
        # Measuring intruders rather than the page's modal text column is what
        # makes this hold on a SPARSE page: on a caption or signature page the
        # line-number column is itself the most common x0 on the page, so a
        # modal test rejects the gutter exactly where it is real and dumps all
        # 28 line numbers into the body as standalone blocks.
        intruders = sum(
            1
            for w in page.extract_words()
            if w["x0"] < hi - 1
            and not (
                w["text"].isdigit() and w["x1"] <= hi + 1 and w["x0"] < 90
            )
        )
        if intruders > 2:
            return None
        return hi

    @staticmethod
    def _pleading_gutter_x(page):
        """X of the pleading margin rule that separates the line-number gutter
        from the body, or None. A tall, thin vertical rule in the left gutter
        zone (x≈50-130) spanning most of the page."""
        tall = page.height * 0.6
        xs = [
            r["x0"]
            for r in page.rects
            if (r["x1"] - r["x0"]) < 3
            and (r["bottom"] - r["top"]) > tall
            and 45 < r["x0"] < 130
        ]
        xs += [
            l["x0"]
            for l in page.lines
            if abs(l["x1"] - l["x0"]) < 3
            and abs(l["bottom"] - l["top"]) > tall
            and 45 < l["x0"] < 130
        ]
        return max(xs) if xs else None

    def _numbered_decretal_start(self, line) -> bool:
        """A district-order list marker such as ``1)`` at an indented rail.

        A wrapped citation can begin a physical line with text such as
        ``99) Orozco ...`` (the tail of ``PageID.198–99)``).  Lexically that
        resembles a list item, but geometrically it remains flush with the
        body column.  Decretal lists sit on their own modestly indented rail;
        require that rail and the usual single-digit order-item marker before
        allowing the renderer to consume the marker and synthesize numbering.
        """
        text = self.line_plain_text(line).strip()
        marker, space, rest = text.partition(" ")
        return bool(
            space
            and rest
            and marker.endswith(")")
            and marker[:-1].isdigit()
            and len(marker[:-1]) == 1
            and line["x0"] >= self.body_baseline_x0 + 6
        )

    def segment_lines(self, lines, page_width) -> list:
        """Keep a styled hanging continuation with its numbered order item."""
        segments = super().segment_lines(lines, page_width)
        joined = []
        for seg in segments:
            if joined and len(seg) == 1 and joined[-1]:
                opener = joined[-1][-1]
                continuation = seg[0]
                gap = continuation["top"] - opener["top"]
                if (
                    self._numbered_decretal_start(opener)
                    and continuation["x0"] >= opener["x0"] + 6
                    and 0 < gap <= self.gap_double_max
                ):
                    joined[-1].extend(seg)
                    continue
            joined.append(seg)
        return joined

    def split_body_paragraphs(self, seg) -> list:
        """Split consecutive numbered decretal items by their visual markers."""
        out = []
        for paragraph in super().split_body_paragraphs(seg):
            current = []
            for line in paragraph:
                if current and self._numbered_decretal_start(line):
                    out.append(current)
                    current = []
                current.append(line)
            if current:
                out.append(current)
        return out

    def classify_paragraph(self, lines) -> str:
        if lines and self._numbered_decretal_start(lines[0]):
            return "ordered-list-item"
        return super().classify_paragraph(lines)

    def find_footnote_separator(self, page):
        """The page-1 caption's closing shelf — a left rule meeting the mid
        vertical (Old Faithful) — sits past the half-page cutoff on long
        captions and the generic scan takes it for the footnote rule, which
        shoves the ruling's opening body into the footnote flow (seen on
        waed, wawd; wash has the state-court version). The page-1 caption
        fingerprint knows the caption's bottom; a 'separator' at that height
        is the shelf, so rescan strictly below it."""
        sep = super().find_footnote_separator(page)
        if sep is None:
            # Pleading paper offsets the body text column — and with it the
            # footnote rule — to the right of the page margin by the
            # line-number gutter. The base scan anchors at the nominal margin
            # and so misses the rule; re-scan anchored at the gutter (the
            # rule sits a few points right of the gutter, at the text column).
            gx = self._pleading_gutter_x(page)
            if gx is not None:
                sep = self._gutter_footnote_rule(page, gx)
        if sep is None:
            # Body-sized footnotes (12pt, same as the body) under the common
            # 2-inch left-margin rule — the small-text-below scan can't see the
            # boundary (ohnd and other CM/ECF PDFs). A 2-inch rule at the margin
            # is not unique in these filings (a 'NOT FOR PUBLICATION' underline,
            # a mid-body redaction rule), so confirm the rule really opens a
            # footnote zone: the first line beneath it must carry a footnote
            # label (a raised marker '4' — the court's own label test).
            cand = self.footnote_sep_fixed_left_rule(page)
            if cand is not None and (
                self._opens_footnote_zone(page, cand)
                or self._opens_continued_footnote_zone(page, cand)
            ):
                sep = cand
        if sep is None or page.page_number != 1:
            return self._remember_footnote_carry(page, sep)
        cap_bottom = self._caption_band_bottom()
        if cap_bottom is None or sep > cap_bottom + 12:
            return self._remember_footnote_carry(page, sep)
        gx = self._pleading_gutter_x(page)
        x0_hi = (gx + 30) if gx is not None else (self.body_baseline_x0 + 4)
        x0_lo = (gx - 2) if gx is not None else 0
        cands = [
            r["top"]
            for r in page.rects
            if r["bottom"] - r["top"] < 2.5
            and (r["x1"] - r["x0"]) >= 90
            and x0_lo <= r["x0"] <= x0_hi
            and r["top"] > cap_bottom + 12
        ]
        sep = min(cands) if cands else None
        return self._remember_footnote_carry(page, sep)

    @staticmethod
    def _footnote_zone_lines(page, sep_top):
        """Substantive text below a separator, excluding the bottom folio."""
        return sorted(
            (
                line
                for line in page.extract_text_lines()
                if line.get("top", 0) > sep_top + 1
                and line.get("bottom", line.get("top", 0)) < page.height - 45
                and (line.get("text") or "").strip()
            ),
            key=lambda line: line["top"],
        )

    def _remember_footnote_carry(self, page, sep_top):
        """Remember a wrapped footnote line that reaches the page bottom.

        The remembered values are geometry only: left edge and line leading.
        A completed short line or flush-left citation clears the state, so an
        unrelated 2-inch signature/redaction rule on the next page cannot be
        mistaken for a continued footnote.
        """
        carry = None
        if sep_top is not None:
            lines = self._footnote_zone_lines(page, sep_top)
            if len(lines) == 1:
                # A ONE-LINE zone carries no leading to measure, so the carry
                # was abandoned entirely — and with it the only evidence that
                # the next page opens with a continuation. cod 252728 sets a
                # single line of footnote 1 at the foot of page 4; page 5 then
                # opened with 17 lines of that footnote under a rule whose
                # footnotes are BODY-sized, so neither the size test nor the
                # label test could confirm it and footnote 2 was lost with it.
                # Remember the left edge alone and let the continuation test
                # match on that.
                only = lines[0]
                if only["bottom"] >= page.height - 120:
                    carry = {"x0": only["x0"], "lead": None}
            elif len(lines) >= 2:
                last, prev = lines[-1], lines[-2]
                same_indent = abs(last["x0"] - prev["x0"]) <= 4
                lead = last["top"] - prev["top"]
                # Compare with the contiguous trailing run, not every line at
                # that inset.  An introductory footnote line can share x0 but
                # use the wider ordinary measure above an inset quotation.
                trailing_run = [last]
                for prior in reversed(lines[:-1]):
                    gap = trailing_run[-1]["top"] - prior["top"]
                    if (
                        abs(prior["x0"] - last["x0"]) > 4
                        or not 8 <= gap <= self.gap_single_max
                    ):
                        break
                    trailing_run.append(prior)
                run_right = max(line["x1"] for line in trailing_run)
                near_bottom = (
                    last.get("bottom", last["top"]) >= page.height - 90
                )
                fills_run = run_right - last["x1"] <= 12
                if same_indent and 8 <= lead <= self.gap_single_max and near_bottom and fills_run:
                    carry = {"x0": last["x0"], "lead": lead}
        self._footnote_carry_geometry = carry
        return sep_top

    def _opens_continued_footnote_zone(self, page, sep_top) -> bool:
        """True when an unlabeled zone continues the prior page's footnote.

        Continuation is proved by matching the prior page's trailing inset and
        single-spaced leading immediately below the same fixed-width rule.
        """
        carry = getattr(self, "_footnote_carry_geometry", None)
        if not carry:
            return False
        lines = self._footnote_zone_lines(page, sep_top)
        if len(lines) < 2:
            return False
        first, second = lines[:2]
        if abs(first["x0"] - carry["x0"]) > 4 or abs(second["x0"] - carry["x0"]) > 4:
            return False
        if carry["lead"] is None:
            # Carried over from a one-line zone, so there is no leading to
            # compare. The left edge plus a zone that runs single-spaced to the
            # foot of the page is what remains, and a stray rule over body text
            # does not produce that.
            lead = second["top"] - first["top"]
            return (
                8 <= lead <= self.gap_single_max
                and lines[-1]["bottom"] >= page.height - 120
            )
        return abs((second["top"] - first["top"]) - carry["lead"]) <= 3

    def _gutter_footnote_rule(self, page, gx):
        """A footnote separator on pleading paper: a thin, left-anchored
        horizontal rule low on the page whose left edge sits at the body text
        column (a few points right of the line-number gutter). A page-1
        caption's closing shelf at the caption-band bottom is excluded."""
        cutoff = page.height * (0.55 if page.page_number == 1 else 0.10)
        cap_bottom = (
            self._caption_band_bottom() if page.page_number == 1 else None
        )
        cands = []
        for r in page.rects:
            if not (
                r["height"] < 2
                and (r["x1"] - r["x0"]) >= 90
                and gx - 2 <= r["x0"] <= gx + 30
                and r["top"] > cutoff
            ):
                continue
            if cap_bottom is not None and r["top"] <= cap_bottom + 12:
                continue
            cands.append(r["top"])
        return min(cands) if cands else None

    def _opens_footnote_zone(self, page, sep_top) -> bool:
        """True if the first non-empty line below ``sep_top`` starts a footnote
        (carries a raised label) — the structural proof that a fixed 2-inch rule
        is a footnote separator and not a header underline or a mid-body rule."""
        below = [
            ln
            for ln in page.extract_text_lines()
            if ln.get("top", 0) > sep_top + 1 and (ln.get("text") or "").strip()
        ]
        if not below:
            return False
        first = min(below, key=lambda ln: ln["top"])
        return self.detect_footnote_label(first) is not None

    def extract_page_images(self, page):
        """Drop pleading-paper rule furniture drawn as images — the tall, narrow
        left/right margin rules, the caption-box verticals, and the thin line-
        number ticks all render as embedded images on some California filings. A
        rule is thin in one dimension; a real figure (an exhibit, a signature
        graphic) is substantial in both, so keep only images thicker than the
        rule threshold in their smaller dimension."""
        return [
            im
            for im in super().extract_page_images(page)
            if min(im["width"], im["height"]) > 10
        ]

    def extract_page_tables(self, page):
        """Lift only tables proved by the shared, conservative validator.

        The base detector rejects the common false positive here (an indented
        quotation read as a two-column table): a candidate needs at least
        three rows and at least two columns populated in a majority of rows.
        Keeping a blanket district-court opt-out flattened genuine schedules
        and deadline grids even though that validation already distinguished
        them from prose.
        """
        return super().extract_page_tables(page)

    # NOTE: removal of page furniture (running footers, bates) and footnote /
    # opinion-start tuning are intentionally NOT in this shared base — they are
    # per-court, so tuning one district can't regress another. A court that
    # needs them defines them in its own file (see ``akd.py`` for the model).

    # ----------------------------------------------- headmatter facsimile
    # District captions put parties on the left and case numbers on the right,
    # usually separated by a stacked column of punctuation (')' / ']' / ':') or
    # just whitespace. Render the headmatter as a whitespace-preserved facsimile
    # — each line's runs placed at their real x — so those columns line up.
    # Splitting is by x-gap, so any divider glyph works; every glyph is kept
    # (each row is one positioned string), so coverage is unaffected. Not every
    # district has a column caption, but where it does this is a clear win and
    # it is harmless (a single-column caption just renders at its x) elsewhere.
    # Styled headmatter is the default (matching the state-court families):
    # centered banner rows with bold/relative sizes and the whitespace-
    # separated caption columns folded into a two-column '__caption__' block
    # (parties left, docket/doc-title right). A court can opt back out to
    # the monospace grid with ``styled_headmatter = False``.
    styled_headmatter = True

    def _lift_district_docket(self, out, headmatter_segs) -> None:
        """Populate the docket field from the caption's case-number line.

        Every district caption prints its number in the right column ('Case
        No. 3:24-cv-00170-jdp', 'No. 2:24-cv-01234', 'CIVIL ACTION NO.
        24-1234', 'Case 1:24-cv-00612 Document 47'), but the field was never
        filled family-wide — the number rendered in the facsimile and nowhere
        else. Anchor on the 'No.' label; the number is the token that follows."""
        if out.get("docketnumber"):
            return
        for seg in headmatter_segs:
            for line in seg:
                text = self.line_plain_text(line)
                low = text.lower()
                for label in ("case no", "civil action no", "case number", "no."):
                    at = low.find(label)
                    if at == -1:
                        continue
                    tail = text[at + len(label) :].lstrip(".:# ")
                    token = tail.split()[0].rstrip(",;)") if tail.split() else ""
                    # A docket token has digits and internal punctuation
                    # ('3:24-cv-00170-jdp'); a prose 'No.' ('No. 2 pencil')
                    # does not.
                    if (
                        any(ch.isdigit() for ch in token)
                        and any(ch in "-:" for ch in token)
                        and len(token) >= 5
                    ):
                        out["docketnumber"] = token
                        return
        # No label: some courts print the number bare in the right column
        # ('25-cv-1012-wmc', ncmd's '1:24CV948'), and every ECF page stamps
        # 'Case <no.> Document N Filed …'. A CM/ECF case token is
        # self-identifying: a cv/cr office code flanked by digits.
        for seg in headmatter_segs:
            for line in seg:
                for token in self.line_plain_text(line).split():
                    token = token.rstrip(",;)")
                    if self._is_ecf_case_token(token):
                        out["docketnumber"] = token
                        return
        # Last resort: the CM/ECF header band read off in page_lines.
        if getattr(self, "_ecf_docket", None):
            out["docketnumber"] = self._ecf_docket

    @staticmethod
    def _is_ecf_case_token(token: str) -> bool:
        """'3:25-cv-00691-wmc', '1:24CV948', '23-CR-2061-SAB-1' — a cv/cr
        office code flanked by digits (allowing the '-' separators), inside a
        token that carries a ':' or '-'. Prose 'cv' ('cv.' in a citation)
        never sits digit-to-digit."""
        low = token.lower()
        if len(token) < 6 or not any(ch in ":-" for ch in token):
            return False
        for code in ("cv", "cr"):
            at = low.find(code)
            while at != -1:
                before = low[at - 1 : at]
                after = low[at + 2 : at + 3]
                if before in ("-",) or before.isdigit():
                    if after in ("-",) or after.isdigit():
                        # strip separators and confirm digits on both sides
                        left = low[:at].rstrip("-")
                        right = low[at + 2 :].lstrip("-")
                        if left[-1:].isdigit() and right[:1].isdigit():
                            return True
                at = low.find(code, at + 1)
        return False

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        self._lift_district_docket(out, headmatter_segs)
        if self.styled_headmatter:
            rows = self._styled_caption_rows(headmatter_segs)
            if rows:
                out["summary"] = rows
            return out
        items = []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                continue
            for line in seg:
                if not self.line_plain_text(line).strip():
                    continue
                top = round(line.get("top", 0), 1)
                for x0, text in self._caption_runs(line):
                    items.append((top, x0, text))
        rows = self._layout_rows(items)
        if rows:
            out["summary"] = rows
        return out

    def _styled_caption_rows(self, headmatter_segs) -> list:
        """Styled headmatter rows. Runs are regrouped into VISUAL rows by
        (page, top) — page-line building sometimes splits a caption row into
        separate line objects — then a row with material on both sides of
        mid-page is a caption row (left = party, right = docket/doc-title),
        and adjacent narrow one-sided rows join their open side ('vs.',
        wrapped party names, a right-column doc-title wrap). Everything else
        is a styled row — centered when midpoint-centered, with inline
        bold/italic and relative size; underscore runs are dividers."""
        from collections import Counter

        pw = getattr(self, "_page1_width", 612.0) or 612.0
        mid = pw * 0.45
        wide = (pw - 2 * self.body_baseline_x0) * 0.7

        items = []  # (page, top, run-chars)
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                continue
            for line in seg:
                if not self.line_plain_text(line).strip():
                    continue
                chars = line.get("chars") or []
                pno = (chars[0].get("page_number") if chars else None) or 1
                for run in self._caption_char_runs(line):
                    items.append((pno, round(line["top"], 1), run))
        if not items:
            return []
        # Pleading paper offsets the text column right of the gutter, so
        # "centered" means centered on the CONTENT column, not the page.
        col_x0 = min(r[0]["x0"] for _p, _t, r in items)
        col_x1 = max(r[-1]["x1"] for _p, _t, r in items)
        col_mid = (col_x0 + col_x1) / 2
        col_w = col_x1 - col_x0
        items.sort(key=lambda r: (r[0], r[1], r[2][0]["x0"]))
        rows, cur = [], None
        for pno, top, run in items:
            if cur is not None and (pno != cur[0] or abs(top - cur[1]) > 2):
                rows.append(cur)
                cur = None
            if cur is None:
                cur = (pno, top, [])
            cur[2].append(run)
        rows.append(cur)

        sizes = [
            round(c.get("size", 0))
            for _p, _t, runs in rows
            for r in runs
            for c in r
            if (c.get("text") or "").strip()
        ]
        base = float(Counter(sizes).most_common(1)[0][0]) if sizes else 12.0

        def run_text(r):
            return self.line_plain_text({"chars": r}).strip()

        # Drawn caption-box geometry (see /captions), measured BEFORE the
        # column test: a drawn mid vertical makes every row in its y-band a
        # caption row split at the rule — a row whose runs all sit on one
        # side (a party block with no docket opposite, the lone 'Case No.'
        # line) still belongs to its column. Without the rule, two-column
        # means material on both sides of mid-page.
        box = getattr(self, "_hm_caption_box", None) or {}
        drawn_v = box.get("vx")
        verts = [v for v in box.get("verts", []) or [] if v[2] - v[1] >= 40]
        vxs = sorted({v[0] for v in verts})
        fp_sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        if fp_sig:
            # The fingerprint's verticals are gutter-filtered, so pleading
            # margin rails at the page edges can't masquerade as box sides.
            boxes = bool(
                fp_sig["vleft"] and fp_sig["vmid"] and fp_sig["vright"]
            )
        else:
            boxes = (
                len(vxs) >= 3
                and vxs[0] < pw * 0.25
                and vxs[-1] > pw * 0.7
                and any(pw * 0.4 < x < pw * 0.75 for x in vxs)
            )
        box_band = (
            (min(v[1] for v in verts), max(v[2] for v in verts)) if verts else None
        )
        v_band = None
        if drawn_v is not None:
            spans = [v for v in verts if abs(v[0] - drawn_v) < 2]
            if spans:
                v_band = (
                    min(v[1] for v in spans) - 6,
                    max(v[2] for v in spans) + 6,
                )

        two_col, row_split = [], []
        for _p, _t, runs in rows:
            in_band = (
                v_band is not None and _p == 1 and v_band[0] <= _t <= v_band[1]
            )
            split = drawn_v if (in_band and drawn_v is not None) else mid
            lefts = [r for r in runs if r[0]["x0"] < split]
            rights = [r for r in runs if r[0]["x0"] >= split]
            two_col.append((bool(lefts) and bool(rights)) or in_band)
            row_split.append(split)

        def near_caption(i) -> bool:
            lo, hi = max(0, i - 6), min(len(rows), i + 7)
            return any(two_col[j] for j in range(lo, hi))

        # Vertical rhythm: a row gap well past the page's median line pitch
        # becomes a blank row (median-adaptive, so double-spaced pleading
        # paper doesn't gap between every line).
        deltas = sorted(
            b[1] - a[1]
            for a, b in zip(rows, rows[1:])
            if a[0] == b[0] and b[1] > a[1]
        )
        med = deltas[len(deltas) // 2] if deltas else 14.0
        gap_min = med * 1.6

        # The Flush-Right Status draws nothing — its structure is per-ROW
        # alignment (party at the left margin, status label pinned at the
        # right margin, docket floating between them on the 'v.' line), so
        # stacked columns would unpair the rows. Render it as three-zone
        # rows instead of a caption block.
        fp = getattr(self, "_caption_fp", (None, None, None))
        if fp and fp[1] == "status-flush":
            return self._flush_right_rows(rows, gap_min)

        # 'Old Faithful': one mid-page vertical + a half-rule closing into
        # it at the corner. 'The Double Box': tall verticals at BOTH content
        # edges and the middle, closed top and bottom. An hrule with a text
        # line directly above it is an UNDERLINE, not a rule, and never
        # becomes a divider.
        def _is_underline(h):
            htop, hx0, hx1 = h
            for _p2, t2, runs2 in rows:
                if 0 < htop - t2 < 16:
                    rx0 = min(r[0]["x0"] for r in runs2)
                    rx1 = max(r[-1]["x1"] for r in runs2)
                    ov = min(hx1, rx1) - max(hx0, rx0)
                    if ov > 0.7 * (hx1 - hx0):
                        return True
            return False

        closing, pending_hrules, shelf_ys = False, [], []
        for h in box.get("hrules", []) or []:
            if _is_underline(h):
                continue
            if boxes and box_band and (
                abs(h[0] - box_band[0]) < 6 or abs(h[0] - box_band[1]) < 6
            ):
                continue  # the box's own top/bottom edges
            if drawn_v is not None and abs(h[2] - drawn_v) < 8:
                closing = True  # the half-rule meeting the vertical
                shelf_ys.append(h[0])
            else:
                pending_hrules.append(h[0])
        pending_hrules.sort()
        # An INTERIOR shelf (a closing rule with caption rows still below it
        # — consolidated cases stack two captions on one vertical) splits the
        # caption into stacked blocks, one per case.
        shelf_ys.sort()
        if shelf_ys and v_band is not None and shelf_ys[-1] >= v_band[1] - 12:
            shelf_ys.pop()  # the bottom close isn't an interior shelf

        out, left, right = [], [], []
        state = {"open": False, "rail": None, "rail_rows": 0}
        fp_rail = ((getattr(self, "_caption_fp", None) or ({},))[0]
                   or {}).get("rail")

        def strip_rail(run):
            """Drop a leading/trailing rail glyph that joined a text run
            (') MEMORANDUM') when it matches the caption's known rail."""
            railg = state["rail"] or fp_rail
            chars = list(run)
            while chars and not (chars[0].get("text") or "").strip():
                chars.pop(0)
            if railg and chars and (chars[0].get("text") or "") == railg:
                state["rail"] = railg
                chars.pop(0)
                while chars and not (chars[0].get("text") or "").strip():
                    chars.pop(0)
            while chars and not (chars[-1].get("text") or "").strip():
                chars.pop()
            if railg and chars and (chars[-1].get("text") or "") == railg:
                # A ')' is both the common caption rail and meaningful docket
                # punctuation.  Strip it only when it is unmatched in this
                # run (``Defendant. )`` or ``(official capacity) )``), never
                # when it closes a real value such as ``(WO)`` or ``(KAD)``.
                plain = "".join(c.get("text") or "" for c in chars)
                unmatched = railg != ")" or plain.count(")") > plain.count("(")
                if unmatched:
                    state["rail"] = railg
                    chars.pop()
                    while chars and not (chars[-1].get("text") or "").strip():
                        chars.pop()
            return chars

        def push(side, html, x0, top):
            """Append a cell line; a vertical gap past the caption's line
            pitch becomes a blank spacer row (double-spaced captions keep
            their air)."""
            if (
                side
                and isinstance(side[-1], dict)
                and top - side[-1]["top"] > gap_min
            ):
                side.append("")
            side.append({"h": html, "x0": round(x0, 1), "top": top})

        def cellify_pair(l_side, r_side):
            """Final PARALLEL cell arrays: the two columns merged onto one
            row grid by baseline, so a right cell renders beside the left
            row it shares on the page ('v. | Civ. Action No. …'), never
            packed to the top of its column. Indents are relative to each
            cell's own left edge, so 'Plaintiff,' sits indented under the
            party name exactly as printed; a vertical gap past the caption's
            line pitch keeps its blank spacer row on both sides."""
            ents = [("L", e) for e in l_side if isinstance(e, dict)] + [
                ("R", e) for e in r_side if isinstance(e, dict)
            ]
            ents.sort(key=lambda t: t[1]["top"])
            rows = []  # [top, left-cell, right-cell]
            for side, e in ents:
                if (
                    rows
                    and abs(e["top"] - rows[-1][0]) <= 4
                    and (rows[-1][1] if side == "L" else rows[-1][2]) is None
                ):
                    if side == "L":
                        rows[-1][1] = e
                    else:
                        rows[-1][2] = e
                else:
                    rows.append(
                        [e["top"],
                         e if side == "L" else None,
                         e if side == "R" else None]
                    )
            minx = {}
            for key, cells in (("L", [r[1] for r in rows]),
                               ("R", [r[2] for r in rows])):
                xs = [c["x0"] for c in cells if c]
                minx[key] = min(xs) if xs else 0.0

            def cell(e, key):
                if not e:
                    return ""
                return {"h": e["h"], "ind": round(e["x0"] - minx[key], 1)}

            out_l, out_r, prev = [], [], None
            for top, lc, rc in rows:
                if prev is not None and top - prev > gap_min:
                    out_l.append("")
                    out_r.append("")
                prev = top
                out_l.append(cell(lc, "L"))
                out_r.append(cell(rc, "R"))
            return out_l, out_r

        def flush():
            if left or right:
                rail = state["rail"]
                if rail is None and drawn_v is not None and not boxes:
                    rail = "|"  # a DRAWN vertical rule divides the columns
                cells_l, cells_r = cellify_pair(left, right)
                cap = {
                    "__caption__": True,
                    "left": cells_l,
                    "right": cells_r,
                    "rail": rail,
                }
                # the glyph rail is drawn once per SOURCE row that bore it —
                # render exactly that many, never one-per-cell (which would
                # invent glyphs for banner/blank rows). 0 → fall back at render.
                if state.get("rail_rows"):
                    cap["rail_rows"] = state["rail_rows"]
                state["rail_rows"] = 0
                fp = getattr(self, "_caption_fp", (None, None, None))
                if fp and fp[1] in (
                    "double-box", "old-faithful", "upside-down-t", "i-beam",
                    "backwards-c", "twin-rail", "x-capped-box", "status-flush",
                ):
                    cap["shape"] = fp[1]
                if boxes:
                    cap["boxes"] = True  # The Double Box
                elif closing and rail == "|":
                    cap["corner"] = True  # Old Faithful ┘ close
                out.append(cap)
                left.clear()
                right.clear()
            state["open"] = False
            state["rail"] = None

        prev_row = None
        for i, (_pno, _top, runs) in enumerate(rows):
            # A drawn horizontal rule above this row becomes a FULL-WIDTH
            # rule row at its position.
            while pending_hrules and _pno == 1 and _top > pending_hrules[0]:
                flush()
                if not out or out[-1] != "__RULE__":
                    out.append("__RULE__")
                pending_hrules.pop(0)
            # Passing an interior shelf closes the current stacked caption.
            while shelf_ys and _pno == 1 and _top > shelf_ys[0] + 2:
                flush()
                shelf_ys.pop(0)
            if (
                prev_row is not None
                and not (left or right)
                and (prev_row[0] != _pno or (_top - prev_row[1]) > gap_min)
                and out
                and out[-1] != ""
            ):
                out.append("")
            prev_row = (_pno, _top)
            texts = [run_text(r) for r in runs]
            joined = " ".join(t for t in texts if t)
            x0 = min(r[0]["x0"] for r in runs)
            x1 = max(r[-1]["x1"] for r in runs)
            # one rail glyph is drawn per source row that contains it — count
            # those rows so the renderer draws exactly that many (not one per
            # cell, which would invent glyphs for the banner / blank rows).
            _railg = state["rail"] or fp_rail
            if _railg and _railg in joined:
                state["rail_rows"] += 1
            if self.is_rule_text(joined, "_-—–=*"):
                flush()
                out.append("__DIVIDER__")
                continue
            if two_col[i]:
                # A run that is nothing but rail glyphs IS the column divider
                # (')' / '§' / ':' stacked down the caption) — record it for
                # the renderer, keep it out of the cells.
                cell_runs = []
                for r in runs:
                    t = run_text(r)
                    if t and all(c in ")]§|(: " for c in t):
                        state["rail"] = t[:1]
                        continue
                    cell_runs.append(r)

                for side, keep in (
                    (left, lambda r: r[0]["x0"] < row_split[i]),
                    (right, lambda r: r[0]["x0"] >= row_split[i]),
                ):
                    sruns = [strip_rail(r) for r in cell_runs if keep(r)]
                    sruns = [r for r in sruns if r]
                    if not sruns:
                        continue
                    html = " ".join(
                        self.line_inline_text({"chars": r}) for r in sruns
                    ).strip()
                    if html:
                        push(side, html, sruns[0][0]["x0"], _top)
                state["open"] = True
                continue
            # A glyph-only row (a stray ',' from interleaved caption lines)
            # never stands alone — it joins the open caption side or the
            # previous row. Rail glyphs ARE the divider, not cell text.
            if joined and not any(c.isalnum() for c in joined):
                if all(c in ")]§|(: " for c in joined):
                    state["rail"] = joined.strip()[:1]
                    continue
                if left or right:
                    side = left if x0 < row_split[i] else right
                    if side and isinstance(side[-1], dict):
                        side[-1]["h"] = (side[-1]["h"] + " " + joined).strip()
                    else:
                        push(side, joined, x0, _top)
                elif out and isinstance(out[-1], dict) and out[-1].get("__hm__"):
                    out[-1]["html"] += " " + joined
                continue
            # ±40 / 0.8: pleading-paper banners center sloppily and run wide
            # within the column; caption party rows sit 60pt+ off-center.
            # A caption role row ('Plaintiffs,' / 'Defendant.') belongs to
            # the open caption even when it sits near the column center.
            role_words = {
                "plaintiff", "plaintiffs", "defendant", "defendants",
                "petitioner", "petitioners", "respondent", "respondents",
                "appellant", "appellants", "appellee", "appellees",
            }
            if (state["open"] or near_caption(i)) and joined.rstrip(
                ".,"
            ).lower() in role_words:
                push(
                    left,
                    self.line_inline_text(
                        {"chars": [c for r in runs for c in r]}
                    ),
                    x0,
                    _top,
                )
                state["open"] = True
                continue
            # Centered on the column OR on the PAGE — a court banner ('IN THE
            # UNITED STATES DISTRICT COURT') is page-centered but the column
            # midpoint is skewed by the banner's own width, so test both; this
            # keeps the banner out of the rail caption (where it would inflate
            # the rail-glyph count with lines the PDF never drew a rail on).
            cx = (x0 + x1) / 2
            centered = (
                abs(cx - col_mid) <= 40 and (x1 - x0) < col_w * 0.8
            ) or (
                # page-centered banner: width capped against the PAGE, not the
                # column — a narrow caption column would otherwise reject the
                # wider of two banner lines and fold it into the caption
                abs(cx - pw / 2) <= 30 and (x1 - x0) < pw * 0.65
            )
            narrow = (x1 - x0) <= wide
            if (state["open"] or near_caption(i)) and narrow and not centered:
                sruns = [strip_rail(r) for r in runs]
                sruns = [r for r in sruns if r]
                if sruns:
                    push(
                        left if x0 < row_split[i] else right,
                        " ".join(
                            self.line_inline_text({"chars": r})
                            for r in sruns
                        ).strip(),
                        sruns[0][0]["x0"],
                        _top,
                    )
                state["open"] = True
                continue
            flush()
            all_chars = [c for r in runs for c in r]
            printable = [
                round(c.get("size", 0))
                for c in all_chars
                if (c.get("text") or "").strip()
            ]
            size = float(Counter(printable).most_common(1)[0][0]) if printable else base
            # A narrow caption line that sits clearly right of the content
            # midpoint is the caption's right column ('DECISION AND ORDER', the
            # docket) — staggered onto its own rows, so it never paired with a
            # left run and the two-column detector didn't catch it. Right-align
            # it so it renders on the right, not collapsed into the left column.
            right_aligned = not centered and narrow and x0 > col_mid + 20
            out.append(
                {
                    "__hm__": True,
                    "html": self.line_inline_text({"chars": all_chars}),
                    "rel": round(size / base, 3) if base else 1.0,
                    "align": "C" if centered else ("R" if right_aligned else "L"),
                    "page": _pno,
                    "top": round(_top, 1),
                }
            )
        flush()
        return out


    def _flush_right_rows(self, rows, gap_min) -> list:
        """Three-zone rows for The Flush-Right Status: each visual row keeps
        its own left / center / right runs paired (PLAINTIFF stays on the
        party's row, the docket floats centered on the 'v.' line). Inline
        bold/italic is preserved per run. One-zone rows stay ordinary styled
        rows so banners render exactly like every other court's."""
        xs = [r for _p, _t, runs in rows for r in runs]
        lmargin = min(r[0]["x0"] for r in xs)
        rmargin = max(r[-1]["x1"] for r in xs)
        out, prev = [], None
        for pno, top, runs in rows:
            if (
                prev is not None
                and (pno != prev[0] or top - prev[1] > gap_min)
                and out
                and out[-1] != ""
            ):
                out.append("")
            prev = (pno, top)
            cells = {"l": [], "c": [], "r": []}
            for r in runs:
                if r[-1]["x1"] > rmargin - 15 and r[0]["x0"] > lmargin + 30:
                    k = "r"
                elif r[0]["x0"] < lmargin + 30:
                    k = "l"
                else:
                    k = "c"
                cells[k].append(self.line_inline_text({"chars": r}))
            filled = [k for k in ("l", "c", "r") if cells[k]]
            if len(filled) == 1:
                k = filled[0]
                out.append({
                    "__hm__": True,
                    "html": " ".join(cells[k]),
                    "rel": 1.0,
                    "align": {"l": "L", "c": "C", "r": "R"}[k],
                    "page": pno,
                    "top": round(top, 1),
                })
            else:
                out.append({
                    "__hmrow__": True,
                    "l": " ".join(cells["l"]),
                    "c": " ".join(cells["c"]),
                    "r": " ".join(cells["r"]),
                })
        return out

    def _caption_char_runs(self, line) -> list:
        """Char runs split at the wide x-gaps that separate caption columns.
        Typewriter-set captions fill the column gap with literal space
        glyphs instead of leaving it empty, so spaces are buffered and the
        gap is measured between printable neighbors — a wide run of spaces
        splits just like a wide empty gap (the padding spaces are dropped)."""
        chars = line.get("chars") or []
        runs, cur, spaces = [], [], []
        for c in chars:
            if not (c.get("text") or "").strip():
                if cur:
                    spaces.append(c)
                continue
            if cur and c["x0"] - cur[-1]["x1"] > _CAPTION_GAP:
                runs.append(cur)
                cur = [c]
            else:
                cur.extend(spaces)
                cur.append(c)
            spaces = []
        if cur:
            runs.append(cur)
        return runs

    def _caption_runs(self, line):
        """(x0, text) runs at the wide x-gaps that separate caption columns,
        leaving ordinary word spacing within a run intact."""
        out = []
        for run in self._caption_char_runs(line):
            text = self.line_plain_text({"chars": run}).strip()
            if text:
                out.append((round(run[0]["x0"], 1), text))
        return out

    @staticmethod
    def _layout_rows(items):
        """Place runs that share a row (same top) on one line, positioned by x0
        in a monospace grid, so vertical columns (the divider) line up."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1]))
        rows, segs, cur_top = [], [], None

        def emit(parts):
            line = ""
            for x0, text in sorted(parts, key=lambda p: p[0]):
                col = max(
                    len(line) + (1 if line else 0),
                    int((x0 - _CAPTION_LEFT) / _CAPTION_CHAR_W),
                )
                line += " " * (col - len(line)) + text
            return line

        for top, x0, text in items:
            if cur_top is not None and abs(top - cur_top) > 3:
                rows.append(emit(segs))
                segs = []
            segs.append((x0, text))
            cur_top = top
        if segs:
            rows.append(emit(segs))
        return rows

    # ---------------------------------------------------------------- author
    def _signature_author(self, all_segments):
        """The judge named just above a 'United States District Judge' (etc.)
        title line — scanning from the end, where the signature block sits."""
        lines = [
            self.line_plain_text(l).strip() for _p, seg, _k in all_segments for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            low = lines[i].lower().strip().rstrip(".")
            # A signature TITLE line is short ('UNITED STATES DISTRICT
            # JUDGE', 'Thomas S. Kleeh, Chief Judge'); a body sentence that
            # merely ENDS in a title phrase ('…consent to jurisdiction of
            # the Magistrate Judge') is long — cap the endswith match so
            # decree text above it ('DISMISSED WITH PREJUDICE.') can't be
            # taken for the judge's name.
            title = next(
                (
                    t
                    for t in _JUDGE_TITLES
                    if low == t.rstrip(".")
                    or (
                        len(lines[i]) <= 52
                        and low.endswith(" " + t.rstrip("."))
                    )
                ),
                None,
            )
            if title is None:
                continue
            # name + title on ONE line ('THOMAS S. KLEEH, CHIEF JUDGE'):
            # the part before the title is the name — take it directly
            # rather than walking back into unrelated text above.
            head = lines[i][: len(lines[i]) - len(title.rstrip("."))]
            head = head.rstrip(" .").rstrip(",").strip()
            if (
                head
                and _looks_like_name(head)
                and not any(
                    w in head.lower().split()
                    for w in ("court", "courts", "division", "states", "district")
                )
            ):
                return _strip_sig_prefix(head).rstrip(",")
            # Walk back over rules / 'SO ORDERED' / 'Dated:' to the name line.
            for j in range(i - 1, max(-1, i - 5), -1):
                cand = lines[j]
                clow = cand.lower()
                if _is_rule(cand) or any(clow.startswith(s) for s in _SIG_SKIP):
                    if clow.startswith(("s/", "/s/")) and _looks_like_name(cand):
                        return _strip_sig_prefix(cand).rstrip(",")
                    continue
                if _looks_like_name(cand):
                    return _strip_sig_prefix(cand).rstrip(",")
            # Title on the same line as the name ('Dated: ... District Judge')?
        return None

    def _present_author(self, all_segments):
        """Minute-order author: 'Present: The Honorable NAME, ... JUDGE'."""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                key = "the honorable "
                if "present:" in low and key in low and "judge" in low:
                    after = t[low.find(key) + len(key) :]
                    name = after.split(",")[0].strip()
                    if name:
                        return name
        return None

    # A surname + abbreviated/spelled-out judge title that opens the opinion
    # ('Rufe, J.' / 'Smith, Chief Judge.').
    _BYLINE_TITLES = (
        "Chief Judge",
        "Senior Judge",
        "District Judge",
        "Magistrate Judge",
        "Circuit Judge",
        "Judge",
        "C.J.",
        "J.",
        "U.S.D.J.",
        "U.S.M.J.",
    )

    _ABBREV_TITLES = ("J.", "C.J.", "P.J.", "U.S.D.J.", "U.S.M.J.")

    def _byline_author(self, all_segments, limit=12):
        """A 'NAME, <title>' byline near the top (e.g. Pennsylvania-E 'Rufe, J.
        February 27, 2026'). Scans only the opening segments so a mid-opinion
        citation can't masquerade as the author."""
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                if "," not in t or len(t) > 60:
                    continue
                name, rest = t.split(",", 1)
                name, rest = name.strip(), rest.strip()
                toks = name.replace("-", " ").split()
                if not (
                    1 <= len(toks) <= 3
                    and all(w[:1].isupper() and w.rstrip(".").isalpha() for w in toks)
                ):
                    continue
                first = rest.split()[0] if rest.split() else ""
                # 'Rufe, J.' / 'Rufe, J. <date>' or a spelled-out judge title.
                if (
                    first in self._ABBREV_TITLES
                    or rest.rstrip(".") in self._BYLINE_TITLES
                    or any(
                        rest.startswith(tt)
                        for tt in self._BYLINE_TITLES
                        if tt[0].isalpha() and len(tt) > 3
                    )
                ):
                    return name
        return None

    def _judge_byline_name(self, line):
        """The judge named by an opening BYLINE — 'ERIC KOMITEE, United States
        District Judge:' — the form the New York districts print immediately
        below the caption's closing rule. Returns the name, or None.

        This is a byline, not a signature: it opens the ruling, so the line
        itself is consumed by the opinion's ``author`` (see
        ``split_author_line``) rather than rendered as caption text."""
        t = self.line_plain_text(line).strip()
        if "," not in t or len(t) > 70:
            return None
        name, rest = t.split(",", 1)
        rest = rest.strip().rstrip(":.").lower()
        if rest not in _JUDGE_TITLES:
            return None
        name = name.strip()
        return name if _looks_like_name(name) else None

    def _split_segments_at_bylines(self, all_segments) -> list:
        """Also isolate a judge BYLINE onto its own segment.

        The New York districts set the byline at the body margin one
        double-space above the first paragraph — the same pitch as the body —
        so no gap/font/alignment cue separates them and the byline arrives
        glued to the front of the opening body segment. Cutting around it lets
        it be recognised as the opinion start and consumed as the author
        instead of read as the first sentence."""
        out = []
        for page_no, seg, kind in super()._split_segments_at_bylines(all_segments):
            cuts = sorted(
                {
                    j
                    for i, line in enumerate(seg)
                    if self._judge_byline_name(line)
                    for j in (i, i + 1)
                    if 0 < j < len(seg)
                }
            )
            if not cuts:
                out.append((page_no, seg, kind))
                continue
            for a, b in zip([0] + cuts, cuts + [len(seg)]):
                sub = seg[a:b]
                if sub:
                    out.append((page_no, sub, self.classify_segment(sub)))
        return out

    def _caption_judge(self, all_segments, limit=14):
        """A caption author tag: 'Judge NAME' / 'Hon. NAME' / 'Honorable NAME'
        sitting in the caption column."""
        tags = ("judge ", "hon. ", "honorable ")
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for tag in tags:
                    if low.startswith(tag):
                        name = t[len(tag) :].split(",")[0].strip()
                        if _looks_like_name(name):
                            return name
        return None

    # ------------------------------------------------------------- opinion start
    def _is_heading(self, line) -> bool:
        """True if ``line`` is a document-type heading — an exact phrase
        ('MEMORANDUM OPINION AND ORDER' / 'ORDER' / ...; letter-spaced 'O RDER'
        matches with spaces removed), OR a compound ALL-CAPS title that opens
        with a doc-type word ('ORDER ADOPTING MEMORANDUM AND RECOMMENDATION',
        'ORDER GRANTING DEFENDANT'S MOTION …'). The compound title is the
        opinion's start, not the last line of the headmatter."""
        plain = self.line_plain_text(line).strip()
        low = plain.rstrip(".:").lower()
        if low in _HEADINGS:
            return True
        squeezed = low.replace(" ", "")
        if squeezed in {h.replace(" ", "") for h in _HEADINGS}:
            return True
        if plain and plain == plain.upper() and len(plain) < 90:
            head = low.split()
            if head and head[0].strip(",") in _HEADING_STARTS:
                return True
        return False

    def find_authors(self, all_segments) -> list:
        # Author, in order of reliability: signature block, minute-order
        # 'Present:' line, a 'NAME, J.' opening byline, a caption 'Judge NAME'.
        # Keep the SOURCE as well as the name: which signal produced the judge
        # is what tells a ruling from a paper filed with the court (see
        # ``classify_document_type``).
        self._district_author = self._district_author_source = None
        for src, finder in (
            ("signature", self._signature_author),
            ("present", self._present_author),
            ("byline", self._byline_author),
            ("caption", self._caption_judge),
        ):
            name = finder(all_segments)
            if name:
                self._district_author, self._district_author_source = name, src
                break
        # Opinion start: the document-type heading; else the first body segment.
        # (Courts whose ruling opens differently — e.g. an ALL-CAPS heading after
        # a ruled caption box, or a title set INSIDE the caption column with the
        # body opening 'THIS MATTER is before…' — override this in their own
        # file; see akd.py and ncwd.py.)
        # Caption band bottom (page 1) — bounds the heading scan below, and is
        # reused further down to keep the start from landing above the caption.
        cap_bottom = self._caption_band_bottom()

        # Bound the heading scan to the FRONT of the ruling. Once real body
        # prose has begun — a later page, or below the page-1 caption band — the
        # opinion has already started, so a heading-table match further down is a
        # running footer that repeats the caption's document title ('ORDER
        # REMANDING DECISION …' at the foot of page 8), not the opinion start.
        def _body_started(pno, seg, kind):
            if kind != "body" or not seg:
                return False
            if pno > 1:
                return True
            return (
                cap_bottom is not None
                and seg[0].get("top", 0) >= cap_bottom - 6
            )

        start = None
        for i, (pno, seg, kind) in enumerate(all_segments):
            if seg and self._is_heading(seg[0]):
                start = i
                break
            if _body_started(pno, seg, kind):
                break
        if start is None:
            for i, (_p, seg, kind) in enumerate(all_segments):
                if kind == "body":
                    start = i
                    break
        # Last resorts — a district doc always has a ruling, so an empty
        # result is always wrong: (1) a compound ALL-CAPS heading the exact
        # phrase table doesn't list ('ORDER DENYING PLAINTIFF'S MOTION TO
        # ALTER OR AMEND JUDGMENT'); (2) the first multi-line prose segment
        # when the court's line pitch classifies body as blockquote.
        if start is None:
            for i, (_p, seg, _k) in enumerate(all_segments):
                if seg and len(seg) <= 2:
                    t = self.line_plain_text(seg[0]).strip()
                    if (
                        t
                        and t == t.upper()
                        and len(t) < 90
                        and any(
                            t.startswith(w)
                            for w in (
                                "ORDER", "MEMORANDUM", "OPINION", "FINDINGS",
                                "JUDGMENT", "DECISION", "REPORT AND",
                            )
                        )
                    ):
                        start = i
                        break
        if start is None:
            for i, (_p, seg, kind) in enumerate(all_segments):
                if kind == "blockquote" and len(seg) >= 2:
                    start = i
                    break
        if start is None:
            return []
        # The opinion can never start ABOVE the page-1 caption: when the
        # fingerprint drew a caption band (mid vertical or glyph rail) and
        # the chosen start sits inside/above it (a double-spaced caption
        # classifying as 'body' pulls the fallback to the banner), advance
        # to the first segment below the band (cap_bottom computed above).
        if cap_bottom is not None:
            pno0, seg0, _k0 = all_segments[start]
            if pno0 == 1 and seg0 and seg0[0].get("top", 0) < cap_bottom - 4:
                # The first body line often sits flush at the band bottom
                # (the divider rule ends exactly where the prose begins), so
                # land on a segment AT the band bottom — a true caption role
                # row that slips through is swept up by the role-row scan below.
                for i, (pno, seg, _k) in enumerate(all_segments):
                    if pno == 1 and seg and seg[0].get("top", 0) > cap_bottom - 6:
                        start = i
                        break
                    if pno > 1 and seg:
                        start = i
                        break
        # A doc-title heading can sit INSIDE the caption (in the right
        # column, above 'Defendants.'); the body then starts after the
        # caption's last party-role row. The scan stops at the first wide
        # single-run line (real body text), so a body sentence that happens
        # to end '... Defendants.' can never trigger it.
        roles = {
            "plaintiff", "plaintiffs", "defendant", "defendants",
            "respondent", "respondents", "petitioner", "petitioners",
            "appellant", "appellants", "appellee", "appellees",
            "intervenor", "intervenors",
        }
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        wide = (pw - 2 * self.body_baseline_x0) * 0.7
        start_page = all_segments[start][0]
        last_role = None
        # The fallback start segment may itself BE caption rows ('C. Perez,
        # et al.,' / 'Defendants') — scan it too, not just what follows.
        for j in range(start, len(all_segments)):
            pno, seg, _k2 = all_segments[j]
            if pno != start_page:
                break
            stop = False
            for l in seg:
                runs = self._caption_char_runs(l)
                if len(runs) == 1 and (l["x1"] - l["x0"]) > wide:
                    stop = True
                    break
                t = self.line_plain_text(l).strip()
                # Role rows may be compounds ('Plaintiff/Third-Party
                # Defendant,' / 'Third-Party Plaintiffs.') — a short,
                # punctuation-terminated caption row containing a role word.
                low = t.rstrip(".,").lower()
                if low in roles or (
                    len(t) <= 45
                    and t[-1:] in ".,"
                    and any(
                        w in low.replace("/", " ").replace("-", " ").split()
                        for w in roles
                    )
                ):
                    last_role = j
            if stop:
                break
        if last_role is not None and last_role + 1 < len(all_segments):
            start = last_role + 1
        # The caption's closing rule is caption furniture, never the ruling's
        # first line — step over it so it renders as the caption's divider
        # (the New York districts close the caption with a typed '------x').
        while (
            start + 1 < len(all_segments)
            and all_segments[start][1]
            and self.is_separator_line(all_segments[start][1][0])
        ):
            start += 1
        # A judge BYLINE below the caption ('ERIC KOMITEE, United States
        # District Judge:') opens the ruling. Start there — that lifts it out
        # of the caption, and ``split_author_line`` consumes it as the author.
        for i in range(min(start + 1, len(all_segments))):
            seg = all_segments[i][1]
            if not seg or len(seg) > 1:
                continue
            if self._judge_byline_name(seg[0]):
                start = i
                break
        # A footnote referenced from the CAPTION (a superscript on a party
        # or title row) belongs to the headmatter — record its label so
        # ``extract`` can move it. A footnote must never go missing.
        labels = set()
        for _p3, seg3, _k3 in all_segments[:start]:
            for line in seg3:
                chars = line.get("chars") or []
                sizes = [
                    round(c.get("size", 0), 1)
                    for c in chars
                    if (c.get("text") or "").strip()
                ]
                if not sizes:
                    continue
                dom = max(set(sizes), key=sizes.count)
                run = ""
                for c in chars:
                    t3 = c.get("text") or ""
                    if t3.isdigit() and c.get("size", 0) < dom * 0.8:
                        run += t3
                    elif run:
                        labels.add(run)
                        run = ""
                if run:
                    labels.add(run)
        # Group what belongs together: a section heading directly ABOVE the
        # chosen start belongs to the ruling, not to headmatter. When page 1
        # is a scanned caption (cacd 996274), the digital text opens
        # 'II. LEGAL STANDARD' on page 2 and the body-segment fallback landed
        # on the paragraph BELOW it — the heading was orphaned into an
        # otherwise-empty headmatter. Walk back over short heading-like
        # segments that sit on the start's own page, outside any caption band.
        while start > 0:
            prev_pno, prev_seg, _pk = all_segments[start - 1]
            cur_pno, cur_seg, _ck = all_segments[start]
            if not prev_seg or prev_pno != cur_pno or len(prev_seg) > 2:
                break
            # On page 1 the segment above the start is almost always caption
            # material. Walk back only when a measured caption band PROVES the
            # heading sits below it — with no band drawn (txwd's typed-rail
            # captions), a bold 'Plaintiffs,' role row is indistinguishable
            # from a heading by geometry alone, and walking back swallows the
            # caption into the body.
            if prev_pno == 1 and (
                cap_bottom is None
                or prev_seg[0].get("top", 0) < cap_bottom - 4
            ):
                break
            text = self.line_plain_text(prev_seg[0]).strip()
            # Heading geometry: short of the measure and either bold or
            # set in caps — never a wrapped prose line.
            if not text or (prev_seg[0]["x1"] - prev_seg[0]["x0"]) > wide:
                break
            _sz, _font, bold = self.line_meta(prev_seg[0])
            if not (bold or text == text.upper()):
                break
            start -= 1
        self._hm_super_labels = labels
        return [start]

    def split_author_line(self, line):
        """The opinion-start line is a heading, not a byline; the author comes
        from the signature block / minute line. Return (author, [heading-as-body]).
        When no structured author was found, leave it empty — guessing from the
        opening line would grab the caption banner ('UNITED STATES DISTRICT
        COURT') on a signature-less order.

        A judge byline is the exception: it *is* the author line, so it is
        consumed here rather than kept as the opinion's opening paragraph."""
        author = getattr(self, "_district_author", None)
        byline = self._judge_byline_name(line)
        if byline:
            return (author or byline, [])
        return (author or "", [line])

    def build_opinion(self, op_start, op_end, **kwargs):
        """Retain an exact printed opening byline without changing author ID.

        ``Opinion.author`` remains the concise name used by grouping and XML
        consumers.  The role-marked caption block is the visible, source-exact
        form (judicial title, honorific, punctuation and footnote marks).
        """
        op = super().build_opinion(op_start, op_end, **kwargs)
        page_no, seg, _kind = kwargs["all_segments"][op_start]
        if seg and self._judge_byline_name(seg[0]):
            exact = self.line_inline_text(seg[0]).strip()
            if exact:
                op.caption.insert(
                    0,
                    Block(
                        kind="p",
                        text=exact,
                        page=page_no,
                        payload={"role": "byline"},
                    ),
                )
        return op

    def classify_document_type(self, all_segments, author_indices, n_pages):
        from ..models import DocType

        # A LETTER to the court is a paper filed WITH the court, not a ruling
        # BY it, and must not enter the case law. Its shape is an addressee
        # block ('The Honorable NAME' over the court's address) followed by a
        # salutation ('Dear Judge NAME:'). Both are required, so a ruling that
        # merely names a judge is never mistaken for one — and no ruling opens
        # with a salutation. The judicial title inside that addressee block is
        # also what fools the signature scan into reading the addressee as the
        # author, so this check cannot be gated on where the author came from.
        addressed = salutation = False
        for _p, seg, _k in all_segments[:40]:
            for line in seg:
                t = self.line_plain_text(line).strip()
                low = t.lower()
                if low.startswith(("the honorable ", "honorable ", "hon. ")):
                    addressed = True
                elif low.startswith("dear ") and t.endswith(":"):
                    salutation = True
        if addressed and salutation:
            return DocType.FILING
        if author_indices:
            return DocType.OPINION
        return super().classify_document_type(all_segments, author_indices, n_pages)
