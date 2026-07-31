"""United States District Court, Western District of North Carolina.

ncwd's segmentation lives here (not in the shared district base) — tuning
another district can't regress it. Two house styles, both identified by the
page-1 caption fingerprint:

  * 9/10: a Parenthetical Box / Banded Bracket — a stacked ')' rail down the
    middle of the caption (sometimes inside a drawn Word-table box), with the
    document title set INSIDE the caption's right column ('  )  MEMORANDUM /
    OF DECISION AND ORDER'). There is no heading line at all; the opinion
    opens directly below the rail with a bold-lead 'THIS MATTER is before
    the Court…' paragraph. The rail's y-extent (``rail_band`` from the
    fingerprint) marks where the caption — and the headmatter — ends.
  * 1/10: a bare whitespace two-column caption (parties left, docket right,
    nothing drawn), followed by a centered bold ALL-CAPS heading
    ('MEMORANDUM OPINION AND ORDER') — the generic heading scan handles it.

Rulings end 'Signed:' / 'ENTER:' + date and a signature IMAGE (the judge's
name and title are pixels inside the graphic, so there is no text to anchor
on) — the shared base harvests that pattern into the Signature section. The
date stamp is set in the STAMP font (10pt Times) inside an Arial/Century
ruling and is placed absolutely, so on many of these orders its baseline
lands a few points ABOVE the last decretal line ('IT IS SO ORDERED.') even
though it belongs to the signature block below it. It is lifted by font,
never by position.

Section heads in the body ('I. BACKGROUND', 'C. Deliberate Indifference…')
are fully-bold standalone lines — flipped to heading blocks for rendering.
A bold run that CLOSES a decretal sentence ('… are hereby DISMISSED WITH
PREJUDICE.') is set in bold on its own line too; it is rejoined to the
sentence it finishes, because the line above it ran to the right measure
(it wrapped). A heading never ends in a period in this court's house style.

Document styles in the corpus: memorandum of decision and order, order on a
motion, memorandum & recommendation (magistrate — signs mid-document and
then appends the 'Time for Objections' advisory, routed to the trailer),
pretrial order / case-management plan, consent judgment, and party BRIEFS
(a memorandum of law signed by a law firm, with tables of authorities and a
certificate of service). Only the court-signed styles are rulings; an
unsigned party filing is classified FILING.
"""

from __future__ import annotations

from ._district import DistrictBase

# The judge's e-signature date stamp is set in a different family and size
# from the ruling body (10pt Times inside a 13/14pt Arial or Century order),
# which is what identifies it — its baseline is not reliable.
_STAMP_FONT = "TimesNewRoman"
_STAMP_SIZE_MAX = 11.0
# The magistrate's report closes with the statutory objection advisory. It is
# procedural ending matter appended AFTER the signature, not recommendation.
_OBJECTIONS_HEAD = "TIME FOR OBJECTIONS"


def _is_section_heading(text: str) -> bool:
    """A short fully-bold standalone section head: ALL-CAPS ('ORDER',
    'I. BACKGROUND'), or an enumerated title-case head ('C. Deliberate
    Indifference to a Serious Medical Need').

    A line that ends in a period is a SENTENCE, not a head: this court's
    heads never take terminal punctuation, while its decretal prose is set
    fully bold and does ('IT IS SO ORDERED.', 'DISMISSED WITH PREJUDICE.',
    'SO ORDERED, ADJUDGED AND DECREED.'). Those stay body text."""
    t = text.strip()
    if not t or len(t) > 90:
        return False
    if t.endswith("."):
        return False
    letters = [c for c in t if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return True
    head, _, rest = t.partition(" ")
    if not rest or not head.endswith("."):
        return False
    num = head.rstrip(".")
    return bool(num) and (
        all(c in "IVX" for c in num)
        or (len(num) == 1 and num.isalpha() and num.isupper())
    )


class WesternDistrictOfNorthCarolina(DistrictBase):
    court_id = "ncwd"
    court_label = (
        "United States District Court, Western District of North Carolina."
    )

    # ------------------------------------------------------------ opinion start
    def find_authors(self, all_segments) -> list:
        """Opinion start from the caption geometry: the first page-1 segment
        BELOW the ')' rail (the fingerprint's ``rail_band``). The title sits
        inside the caption column here, so the generic heading scan would
        run pages ahead to the decretal 'ORDER' section. Falls back to the
        generic path when there is no rail (the whitespace style opens with
        a real centered heading)."""
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        cap_bottom = None
        if sig and sig.get("rail_band"):
            cap_bottom = sig["rail_band"][1]
        if cap_bottom is not None:
            self._district_author = (
                self._signature_author(all_segments)
                or self._present_author(all_segments)
                or self._byline_author(all_segments)
                or self._caption_judge(all_segments)
            )
            for i, (pno, seg, _k) in enumerate(all_segments):
                if pno != 1:
                    break
                if seg and seg[0].get("top", 0) > cap_bottom + 4:
                    return [i]
        return super().find_authors(all_segments)

    # ------------------------------------------------------------- geometry
    def _measure_x1(self) -> float:
        """The right edge of the body measure. A line reaching it WRAPPED."""
        pw = getattr(self, "_page1_width", None) or 612.0
        return pw - self.body_baseline_x0

    def _wraps_to_measure(self, line) -> bool:
        """Whether ``line`` ran out to the right measure — i.e. it wrapped, so
        whatever follows on the next line continues it. The window is one
        character wide: a line that stops even a word short has ENDED, and
        the next line begins something new ('… close this case.' stops 24pt
        short of the measure, so 'IT IS SO ORDERED.' below it is not its
        continuation)."""
        return line.get("x1", 0.0) >= self._measure_x1() - 8.0

    @staticmethod
    def _all_bold_glyphs(line) -> bool:
        """Every letter/digit on the line is set bold — the boldness test on
        its own, without the shared helper's 'and it stops short of the right
        measure' clause. A bold section head long enough to fill the measure
        ('F. Breach of the Implied Covenant of Good Faith and Fair') fails
        that clause and reads as prose, which is exactly the case that has to
        be told apart from a bold sentence tail below."""
        seen = False
        for c in line.get("chars") or []:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            if "Bold" not in (c.get("fontname") or ""):
                return False
        return seen

    def _is_bold_head_line(self, line) -> bool:
        """A standalone fully-bold section head, judged on the LINE (so the
        test survives a page break, where the block text has already been
        joined to the paragraph above)."""
        return self._line_all_bold(line) and _is_section_heading(
            self.line_plain_text(line)
        )

    # ---------------------------------------------------------- segmentation
    def segment_lines(self, lines, page_width) -> list:
        """Rejoin a bold line to the line it continues.

        Two things get cut off by the shared segmenter's bold/alignment
        rules, and both are one logical unit with the line above:

        * a bold sentence TAIL — this court sets its dispositions fully bold,
          so '… and this action is DISMISSED / WITH PREJUDICE.' breaks at the
          line end and the closing words render as a stray block. Proof that
          it is a continuation: the line above ran out to the right measure
          (it wrapped) AND the bold line resumes at the very same left edge,
          as a wrapped line must. A real head sits at the paragraph indent or
          follows a line that stopped short, so it is never joined.
        * the second line of a WRAPPED bold head ('F. Breach of the Implied
          Covenant of Good Faith and Fair / Dealing'). Here the line above is
          itself bold throughout and filled the measure, so the head is one
          heading in two rows and must not split mid-phrase."""
        segs = super().segment_lines(lines, page_width)
        out: list = []
        for seg in segs:
            prev = out[-1][-1] if out and out[-1] else None
            if (
                prev is None
                or not seg
                or not self._all_bold_glyphs(seg[0])
                or self.is_separator_line(seg[0])
                or not self._wraps_to_measure(prev)
            ):
                out.append(list(seg))
                continue
            if self._all_bold_glyphs(prev):
                # A wrapped bold head — but only if the two rows together
                # still read as ONE head. Two full-measure bold rows also
                # occur in a brief's table of contents, where each row is a
                # complete entry closed by its dot leader and page number;
                # joined, those overrun any head's length.
                joined = " ".join(
                    (
                        self.line_plain_text(prev).strip(),
                        self.line_plain_text(seg[0]).strip(),
                    )
                )
                if _is_section_heading(joined):
                    out[-1].extend(seg)
                    continue
                out.append(list(seg))
                continue
            if abs(seg[0].get("x0", 0.0) - prev.get("x0", 0.0)) <= 3 and not (
                _is_section_heading(self.line_plain_text(seg[0]))
            ):
                out[-1].extend(seg)  # bold sentence tail
                continue
            out.append(list(seg))
        return out

    def _begins_paragraph_block(self, lines) -> bool:
        """A fully-bold section head that lands at the TOP of a page opens a
        new block; it is never the wrapped continuation of the paragraph that
        ended on the page before ('III. FACTUAL BACKGROUND' was being glued
        onto the tail of the standard-of-review paragraph)."""
        return bool(lines) and self._is_bold_head_line(lines[0])

    # ------------------------------------------------------- caption divider
    def _caption_char_runs(self, line) -> list:
        """Split the caption's closing underscore rule off the ')' rail glyph
        that abuts it.

        The last caption row is drawn '________________________)': the glyph
        rule that closes the party column, immediately followed by the rail
        glyph with no gap, so the shared run-splitter sees one run. That run
        is neither rule text (because of the ')') nor two-column (all of it
        sits left of mid-page), so it fell through to the glyph-row branch
        and was appended to the 'Defendants.' cell above it. Splitting the
        rail glyph into its own run restores both: the rail is recorded as
        the rail, the rule stays the left column's closing divider."""
        runs = super()._caption_char_runs(line)
        out = []
        for run in runs:
            printable = [c for c in run if (c.get("text") or "").strip()]
            if len(printable) > 4 and printable[-1].get("text") in ")]§|":
                body = [c for c in run if c is not printable[-1]]
                rule = "".join((c.get("text") or "") for c in body).strip()
                if rule and self.is_rule_text(rule, "_-—–=*"):
                    out.append(body)
                    out.append([printable[-1]])
                    continue
            out.append(run)
        return out

    # ------------------------------------------------------ footnote rule
    def find_footnote_separator(self, page):
        """This court UNDERLINES its case names with drawn rules at the body's
        left margin, and some of those underlines are as wide as (or wider
        than) the Word 2-inch footnote rule — one measured 144.6pt at x0=72,
        the exact signature of the separator. So neither width nor position
        can make the call on its own.

        Two structural tests do. First, an underline sits INSIDE the vertical
        band of the text line it decorates, while a separator stands clear in
        the leading between two lines. Second, what follows a real separator
        is footnote matter: a raised label, or a line set smaller than this
        page's body. The generic 'median size below < median above' scan gets
        this wrong here because the page number and the CM/ECF footer strip
        are themselves smaller than the 13/14pt body, so they drag the
        below-median down on EVERY page and every low underline reads as a
        footnote rule — which pushed real body text into the footnote flow.
        Candidates are walked top-down so an underline higher up the page
        cannot mask the separator below it."""
        text_lines = page.extract_text_lines()
        limit = self.body_baseline_x0 + 4
        cap_bot = None
        if page.page_number == 1:
            cap_bot = self._caption_band_bottom()
        cands = []
        for r in page.rects:
            if r["bottom"] - r["top"] >= 2.5:
                continue
            if (r["x1"] - r["x0"]) < 100 or r["x0"] > limit:
                continue
            top = r["top"]
            if top < page.height * 0.4:
                continue
            if cap_bot is not None and top <= cap_bot + 12:
                continue
            if any(
                tl["top"] - 1 <= top <= tl["bottom"] + 2
                and tl["x0"] < r["x1"]
                and tl["x1"] > r["x0"]
                for tl in text_lines
            ):
                continue  # an underline, not a separator
            cands.append(top)
        for top in sorted(cands):
            if self._opens_footnote_zone(page, top) or self._footnote_size_below(
                page, top, text_lines
            ):
                return top
        return None

    def _footnote_size_below(self, page, top, text_lines) -> bool:
        """Whether the first real line under ``top`` is set smaller than this
        page's body — the continuation of a footnote that wrapped from the
        page before, which carries no label to key on. The page number and
        the CM/ECF filing strip are furniture and are skipped: the strip is
        set in its own face (LiberationSans), and a page number is a line
        that is nothing but its own digits."""
        from statistics import median

        sizes = [
            round(c.get("size", 0))
            for c in page.chars
            if (c.get("text") or "").strip()
        ]
        if not sizes:
            return False
        body = max(set(sizes), key=sizes.count)
        for tl in sorted(text_lines, key=lambda t: t["top"]):
            if tl["top"] <= top + 1:
                continue
            chars = tl.get("chars") or []
            if not chars:
                continue
            if any("Liberation" in (c.get("fontname") or "") for c in chars):
                continue  # the CM/ECF filing strip
            txt = (tl.get("text") or "").strip()
            if self._is_page_number_text(txt):
                continue
            return median(c["size"] for c in chars if c.get("size")) <= body - 0.75
        return False

    # ------------------------------------------------------- section headings
    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            for b in op.blocks:
                # 'blockquote' too: a wrapped bold head is indented on its
                # second row, which is enough for the paragraph classifier to
                # call the joined head a quotation. What it IS is settled by
                # the boldness and the shape of the text, not by the indent.
                if b.kind not in ("p", "blockquote"):
                    continue
                t = str(b.text)
                if "<strong>" not in t:
                    continue
                inner = self._untag(t).strip()
                # fully bold: no printable text outside the <strong> spans
                outside, s = [], t
                while True:
                    i = s.find("<strong>")
                    if i < 0:
                        outside.append(s)
                        break
                    outside.append(s[:i])
                    j = s.find("</strong>", i)
                    if j < 0:
                        break
                    s = s[j + len("</strong>"):]
                bold_only = not any(
                    c.isalnum() for c in self._untag("".join(outside))
                )
                if bold_only and _is_section_heading(inner):
                    b.kind = "heading"
        self._route_objections_advisory(doc)
        self._lift_signature_stamp(doc)
        self._reclassify_party_filing(doc)
        return doc

    # ------------------------------------------------------ document style
    def _reclassify_party_filing(self, doc) -> None:
        """A party's brief is not a ruling.

        Three of this corpus's twenty documents are attorney filings — a
        memorandum of law in support of a motion — that sit on the docket
        beside the court's own orders. The opinion-start rule here is the
        caption rail, which every filing on this court's paper also has, so
        they were all coming out as OPINION. Two independent structural facts
        say otherwise, and both are required: the document carries NO judicial
        signature (no e-signature date stamp and nothing the signature
        harvester recognised), and it closes with a certificate of service —
        which a party files and a court never does."""
        from ..models import DocType

        if doc.doc_type != DocType.OPINION:
            return
        if doc.signature or self._date_stamps():
            return
        for op in doc.opinions:
            for b in op.blocks:
                t = self._untag(str(b.text)).strip().upper()
                if t.startswith("CERTIFICAT") and "OF SERVICE" in t:
                    doc.doc_type = DocType.FILING
                    return

    # ------------------------------------------------------- ending matter
    def _route_objections_advisory(self, doc) -> None:
        """A magistrate's memorandum & recommendation signs, and THEN prints
        the statutory 'Time for Objections' advisory. That advisory is
        procedural ending matter addressed to the parties, not part of the
        recommendation, so it is routed to the trailer — which also puts the
        signature back at the end of the body where the shared harvester can
        find it."""
        for op in doc.opinions:
            cut = None
            for i, b in enumerate(op.blocks):
                if b.kind not in ("p", "heading"):
                    continue
                if self._untag(str(b.text)).strip().upper().startswith(
                    _OBJECTIONS_HEAD
                ):
                    cut = i
                    break
            if cut is None:
                continue
            tail = [self._untag(str(b.text)).strip() for b in op.blocks[cut:]]
            op.blocks = op.blocks[:cut]
            doc.trailer = list(doc.trailer) + [t for t in tail if t]
            if not doc.signature:
                # With the advisory out of the way the signature is once again
                # the last thing in the body, so the shared harvester can lift
                # it (it only ever looks at the END of the ruling).
                self._harvest_signature(doc)
            return

    # ---------------------------------------------------------- signature
    def _lift_signature_stamp(self, doc) -> None:
        """Move the 'Signed: <date>' / 'ENTER: <date>' e-signature stamp out of
        the body and onto the front of the Signature section.

        The stamp is placed absolutely by CM/ECF, and on most of these orders
        it is laid down a few points ABOVE the last decretal line, so the
        shared harvester — which reads the block immediately before the
        signature image — sees 'IT IS SO ORDERED.' there instead and leaves
        the stamp behind in the body. The stamp is identified by its FONT: it
        is the only 10pt Times run in an Arial (or Century) ruling."""
        if not doc.opinions:
            return
        stamps = self._date_stamps()
        if not stamps:
            return
        for op in doc.opinions:
            keep, moved = [], []
            for b in op.blocks:
                if b.kind in ("p", "heading"):
                    t = self._untag(str(b.text)).strip()
                    if t in stamps:
                        moved.append(str(b.text))
                        continue
                keep.append(b)
            if not moved:
                continue
            op.blocks = keep
            sig = list(doc.signature or [])
            if sig and any(
                isinstance(s, str) and self._untag(s).strip() in stamps
                for s in sig
            ):
                continue
            doc.signature = moved + sig
            return

    def page_lines(self, page):
        """Record the page's stamp-font runs (10pt Times in an Arial/Century
        ruling) so the e-signature date stamp can be recognised by font later,
        wherever its absolute placement happens to have put it."""
        lines = super().page_lines(page)
        seen = getattr(self, "_stamp_texts", None)
        if seen is None:
            seen = self._stamp_texts = set()
        for line in lines:
            chars = [
                c for c in (line.get("chars") or []) if (c.get("text") or "").strip()
            ]
            if not chars:
                continue
            if all(
                _STAMP_FONT in (c.get("fontname") or "")
                and (c.get("size") or 99) <= _STAMP_SIZE_MAX
                for c in chars
            ):
                t = self.line_plain_text(line).strip()
                if t and len(t) <= 32:  # a date stamp, never a run of prose
                    seen.add(t)
        return lines

    def _date_stamps(self) -> set:
        """The stamp-font runs that really are e-signature date stamps. A
        Times-set ruling puts its footnotes in the same face and size as the
        stamp, so the font test alone also collects footnote lines; the stamp
        additionally announces itself ('Signed: …' / 'ENTER: …'), which is the
        same set of openers the shared signature harvester keys on."""
        return {
            t
            for t in (getattr(self, "_stamp_texts", None) or ())
            if t.lower().startswith(("signed", "enter", "entered", "dated", "date"))
        }

    def prepare_document(self, pdf) -> None:
        self._stamp_texts = set()
        return super().prepare_document(pdf)

    # ------------------------------------------------------ roman folios
    def _sweep_residual(self, doc, source_pages) -> None:
        """A brief's front matter (table of contents, table of authorities) is
        foliated in lowercase roman numerals fenced by dashes — '– i –', '– ii
        –' — in the bottom margin. That is a printed folio, page furniture
        like any other page number, but the shared folio test only recognises
        arabic digits, so it fell through as unplaced content. Record it as
        dropped before the completeness sweep reads the page."""
        extra = []
        for _pno, lines in source_pages:
            for raw in lines:
                t = raw.strip()
                core = t.strip("-–—— ").strip()
                if (
                    core
                    and core != t  # the dash fence is what makes it a folio
                    and len(core) <= 5
                    and set(core.lower()) <= set("ivxlcdm")
                ):
                    extra.append(t)
        if extra:
            doc.dropped = list(doc.dropped) + [
                t for t in extra if t not in doc.dropped
            ]
        super()._sweep_residual(doc, source_pages)
