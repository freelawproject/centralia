"""Supreme Court of Louisiana.

Two-part layout. Page 1 is a Clerk's news-release cover ('FOR IMMEDIATE NEWS
RELEASE ... FROM: CLERK OF SUPREME COURT OF LOUISIANA'), announcing the author in
a mixed-case 'BY McCallum, J.:' line and listing the docket, disposition, and any
separate writings ('Hughes, J., dissents ...'). The opinion proper begins on page
2 with a centered caption ('SUPREME COURT OF LOUISIANA / No. ... / parties / On
Writ of Certiorari ...') followed by the author byline.

That byline is an ALL-CAPS surname and an *abbreviated* title — 'MCCALLUM, J.',
'WEIMER, Chief Justice*', 'PENZATO, Justice Pro Tempore1' — often carrying a
footnote mark ('*' or a superscript digit) in place of the period. Two things
defeat the base byline parser here: the title is the abbreviated 'J.' rather than
the spelled-out 'Justice'/'Judge', and the bold face is encoded as an embedded
subset font ('CIDFont+F2', no 'Bold' in the name) so the base bold test misses
it. The override below recognises the byline structurally instead. The mixed-case
cover lines ('McCallum', 'Hughes') fail the ALL-CAPS name test, so the opinion
correctly starts at the page-2 byline and the cover + caption stay in headmatter.

Printed on legal-size paper (height 1008): the body and a half-width footnote
block (12pt text under an 8pt superscript number, set off by a thin left-aligned
rule) run down to ~937, with the centered page number lower still at ~945. The
default bottom margin would chop the lower quarter of every page, so it is raised
to keep all content while cutting the page number.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

from ._statesupreme import StateSupreme, _is_byline_name

# Louisiana sets the assignment footnote's asterisk in SymbolMT, whose glyphs
# arrive in the PDF's private use area: the star is U+F02A, not U+002A. It is
# the same mark on both ends of the link — the byline's trailing 'COLE, J.<U+F02A>'
# and the note's own label at the page foot — so a test for '*' saw neither, and
# the note came out labelled '?'.
_STAR = "\uf02a"


# Abbreviated Louisiana judicial titles that open an opinion byline. 'Justice Pro
# Tempore' and 'Chief Justice' precede the bare 'Justice'/'J.' so the longest
# match is tested first (startswith on a tuple matches any, but order documents
# intent).
_LA_TITLE_STARTS = (
    "Chief Justice",
    "Justice Pro Tempore",
    "Justice",
    "Judge",
    "C. J.",
    "C.J.",
    "J.",
    "A.H.J.",
)


class LouisianaSupreme(StateSupreme):
    court_id = "la"
    court_label = "Supreme Court of Louisiana."
    # Legal-size page: keep body + bottom footnotes (down to ~937), cut the
    # centered page number (~945).
    margin_bottom = 940.0

    def find_authors(self, all_segments) -> list:
        # Newer disciplinary opinions announce a title-case author on the
        # news-release cover (``BY Guidry, J.:``) and repeat that same
        # title-case byline on the opinion page.  Record the announced name so
        # only that exact title-case surname can pass the otherwise all-caps
        # Louisiana grammar.
        self._la_announced_names = set()
        for _p, seg, _kind in all_segments:
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip()
            if text.startswith("BY ") and "," in text:
                self._la_announced_names.add(text[3:].split(",", 1)[0].strip())
        starts = super().find_authors(all_segments)
        # A news-release cover can say ``PER CURIAM:`` before repeating the
        # actual per-curiam byline on the opinion page.  When both exist, the
        # cover announcement is metadata, not a first opinion.
        per = [
            i
            for i in starts
            if self._la_per_curiam(
                self.line_plain_text(all_segments[i][1][0]).strip()
            )
        ]
        if len(per) >= 2:
            later_pages = {all_segments[i][0] for i in per if all_segments[i][0] > 1}
            if later_pages:
                starts = [
                    i
                    for i in starts
                    if not (i in per and all_segments[i][0] == 1)
                ]
        return starts

    def _byline_split(self, line):
        """Louisiana byline: ALL-CAPS surname, comma, an abbreviated judicial
        title ('J.', 'Chief Justice', 'Justice Pro Tempore'), optionally trailed
        by a footnote mark ('*' or a superscript digit). The byline stands alone
        (the opinion body begins on the next line), so the body half is always
        empty. Recognised structurally — the bold face is a subset font the base
        'Bold'-in-fontname test cannot see, and the title is abbreviated.

        The byline is kept EXACTLY as printed, footnote mark included ('COLE,
        J.*', 'CRAIN, J.1'). The mark is not decoration: it anchors the
        assignment footnote at the page foot ('* Judge Allison H. Penzato …
        appointed Justice pro tempore'), and cleaning it off silently dropped
        the only printed link to that footnote — the byline row then matched
        nothing in the output and read as lost content."""
        text = self.line_plain_text(line).strip()
        if self._la_per_curiam(text):
            return text, ""
        parsed = self._la_byline(text)
        if parsed is None:
            return None
        return text, ""

    def _la_byline(self, text: str):
        """Parse a Louisiana author byline; return (cleaned, name, title) or None.
        ``cleaned`` is the byline with any trailing footnote mark stripped (so the
        stored author reads 'MCCALLUM, J.', not 'MCCALLUM, J.*'); a separate
        writing keeps its disposition clause so the kind can be read from it. Two
        comma placements occur: 'GRIFFIN, J., ...' (after the surname) and
        'GRIFFIN J., ...' (after the abbreviated title attached to the surname)."""
        text = (text or "").strip()
        if not text or "," not in text:
            return None
        head, after = text.split(",", 1)
        head, after = head.strip(), after.lstrip()
        # The trailing mark is the footnote star or digit; SymbolMT prints the
        # star as the private-use U+F02A, which has to come off the stored
        # author too or the byline reads 'COLE, J.' with a missing glyph.
        marks = "*0123456789 " + _STAR
        cleaned = text.rstrip(marks).rstrip()
        # Form A: 'SURNAME, <title>[, disposition]'.
        if _is_byline_name(head) or head in getattr(self, "_la_announced_names", set()):
            core = after.rstrip(marks).rstrip()
            if core.startswith(_LA_TITLE_STARTS):
                return cleaned, head, core.split(",")[0].strip()
        # Form B: the abbreviated title rides with the surname ('GRIFFIN J.,')
        # and the comma opens the disposition clause.
        toks = head.split()
        if len(toks) >= 2:
            name = " ".join(toks[:-1])
            tcore = toks[-1].replace(".", "").rstrip(marks).upper()
            if _is_byline_name(name) and tcore in ("J", "CJ", "PJ"):
                return cleaned, name, toks[-1]
        return None

    def parse_author_line(self, text):
        """Recover (name, title, kind) for a Louisiana byline the base regex
        grammar misses (abbreviated 'J.' title, footnote marks). The kind is read
        from the disposition clause of a separate writing so the opinion type is
        classified correctly; the bare main byline yields kind=None (majority)."""
        base = super().parse_author_line(text)
        if base is not None:
            return base
        if self._la_per_curiam(text):
            return "PER CURIAM", "per curiam", None
        parsed = self._la_byline(text)
        if parsed is None:
            return None
        byline, name, title = parsed
        low = byline.lower()
        kind = None
        if "concur" in low and "dissent" in low:
            kind = "concurring in part and dissenting in part"
        elif "dissent" in low:
            kind = "dissenting"
        elif "concur" in low and "result" in low:
            kind = "concurring in the result"
        elif "concur" in low:
            kind = "concurring"
        return name, title, kind

    @staticmethod
    def _la_per_curiam(text: str) -> bool:
        t = (text or "").strip().rstrip("0123456789*†‡:. ")
        return " ".join(t.split()).upper() == "PER CURIAM"

    # ------------------------------------------------------------- footnotes
    def detect_footnote_label(self, line):
        """The assignment footnote is marked with a '*' set at the SAME size as
        its 12pt text, not as a raised superscript, so the base 'smaller char'
        test cannot see it and the footnote came back labelled '?'. Read the
        leading star run as the label.

        Half the corpus prints that star from SymbolMT, where it arrives as the
        private-use U+F02A rather than U+002A; a literal '*' test matched
        nothing and ten documents labelled their assignment note '?'."""
        text = (line.get("text") or "").lstrip().replace(_STAR, "*")
        if text.startswith("*"):
            return text[: len(text) - len(text.lstrip("*"))]
        return super().detect_footnote_label(line)

    def build_footnote(self, label, lines):
        """Strip the leading star marker off the footnote text — it is the
        label, which the renderer draws in its own column."""
        fn = super().build_footnote(label, lines)
        if fn.paragraphs and label and set(label) == {"*"}:
            tag, txt = fn.paragraphs[0]
            stripped = txt.lstrip().replace(_STAR, "*", 1).lstrip()
            if stripped.startswith(label):
                fn.paragraphs[0] = (tag, stripped[len(label) :].lstrip())
        return fn

    # ------------------------------------------------- the footnote zone
    # Louisiana's footnote zone is marked two ways, and only these two. Both are
    # measured off the document rather than configured:
    #
    #   * a thin 2-inch rule drawn at the body's left rail (x0 = the measured
    #     body column, 350 of the corpus's 362 rail rules, every one 144pt), with
    #     the smaller footnote type directly beneath it; and
    #   * on the pages that draw no rule at all, the type dropping from the
    #     document's 14pt body to the 12pt note.
    #
    # What defeats the inherited chain is that both of its fallbacks read the
    # PAGE instead of the DOCUMENT:
    #
    #   * ``_fenceless_sep`` asks only for a 144±6pt rule at the rail with text
    #     below, and an underlined case name in a citation is exactly that —
    #     'of New Orleans v. Treen' underlines 139pt at x0=72 (gary_crockett
    #     p32), and the rest of the dissent's page became a footnote; and
    #   * ``_footnote_zone_by_size`` takes the page's LARGEST type with three
    #     hits as the body, so a page whose only heading matter is the 15pt
    #     caption reports body=15 and reads the 14pt opinion itself as a note
    #     (in_re_henry_l._klein p2 turned the opinion's opening paragraph into a
    #     footnote; monroe p26 swallowed Hughes's whole separate writing).
    #
    # The document's body type is one number, stable across every page, so it is
    # measured once and the size drop is read against it.
    def prepare_document(self, pdf) -> None:
        """Measure the document's body type size before the page loop."""
        super().prepare_document(pdf)
        self._la_body_size = None
        sizes: Counter = Counter()
        try:
            for page in pdf.pages:
                for line in page.extract_text_lines():
                    chars = line.get("chars") or []
                    if chars:
                        sizes[round(self._line_type_size(chars) * 2) / 2] += 1
                if sum(sizes.values()) >= 400:
                    break
        except Exception:
            return
        if sum(sizes.values()) >= 20:
            self._la_body_size = sizes.most_common(1)[0][0]

    def find_footnote_separator(self, page) -> Optional[float]:
        sep = self._la_rule_separator(page)
        if sep is not None:
            return sep
        return self._footnote_zone_by_size(page)

    def _la_rule_separator(self, page) -> Optional[float]:
        """The drawn separator: a thin rule at the body's left rail with the
        footnote's smaller type below it, standing clear of every text line.

        The 'clear of the text' test is what separates the separator from an
        underlined case name of the same width and at the same rail — the
        underline sits inside its line's own vertical band, the separator sits
        in the whitespace between two lines."""
        body = self._la_body()
        rail = self.body_baseline_x0
        geom = getattr(self, "_doc_geom", None) or {}
        if geom.get("body_x0"):
            rail = geom["body_x0"]
        text_lines = [
            l for l in page.extract_text_lines() if (l.get("chars") or [])
        ]
        best = None
        for r in list(page.rects) + list(page.lines):
            top = r["top"]
            if abs(r["bottom"] - top) >= 2:
                continue
            if abs(r["x0"] - rail) > 3 or (r["x1"] - r["x0"]) < 90:
                continue
            if any(
                tl["top"] - 1 <= top <= tl["bottom"] + 5
                and r["x0"] < tl["x1"]
                and r["x1"] > tl["x0"]
                for tl in text_lines
            ):
                continue  # an underline, drawn through its own line's band
            below = [tl for tl in text_lines if tl["top"] > top + 1]
            if not below:
                continue
            first = min(below, key=lambda l: l["top"])
            if not (
                (body is not None and self._line_type_size(first["chars"]) <= body - 0.5)
                or self.detect_footnote_label(first) is not None
            ):
                continue
            if best is None or top < best:
                best = top
        return best

    def _la_body(self) -> Optional[float]:
        return getattr(self, "_la_body_size", None)

    def _footnote_zone_by_size(self, page) -> Optional[float]:
        """The undrawn separator: the trailing run of type set smaller than the
        DOCUMENT's body, read against the measured body size rather than the
        page's own largest type (see the note above ``prepare_document``)."""
        body = self._la_body()
        if body is None:
            return super()._footnote_zone_by_size(page)
        lines = [l for l in page.extract_text_lines() if (l.get("chars") or [])]
        if len(lines) < 2:
            return None
        lines.sort(key=lambda l: l["top"])
        sizes = [self._line_type_size(l["chars"]) for l in lines]

        def is_folio(line):
            # The centred folio sits BELOW the notes at the same 12pt as they
            # are set, so it must not close the run before it opens.
            return self._page_number_value(self.line_plain_text(line)) is not None

        start = None
        for i in range(len(lines) - 1, -1, -1):
            if is_folio(lines[i]):
                continue
            if sizes[i] <= body - 0.5:
                start = i
            else:
                break
        if start is None or start == 0:
            return None
        # A zone that does not open on a label is a note CARRIED OVER from the
        # previous page; it is admitted on position instead — it has to run to
        # the foot of the page, which a mid-page run of small type never does.
        if self.detect_footnote_label(lines[start]) is None:
            last = max(
                (l for l in lines[start:] if not is_folio(l)),
                key=lambda l: l.get("bottom", l["top"]),
                default=None,
            )
            if last is None or last.get("bottom", last["top"]) < page.height * 0.82:
                return None
        return lines[start]["top"] - 1
