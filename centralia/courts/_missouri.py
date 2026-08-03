"""Shared byline parsing for the Missouri courts (Supreme + Court of Appeals).

The author is signed at the end of the opinion, centered, as 'NAME, Judge' — and
the surname casing varies: Title-Case in some ('Ginger K. Gooch, Judge', 'Zel M.
Fischer, Judge') and ALL-CAPS in others ('KELLY C. BRONIEC, JUDGE', 'EDWARD R.
ARDINI, JR., JUDGE'). The title can be 'Judge' / 'Chief Judge' / 'Presiding
Judge' / 'C.J.' / 'P.J.', also in either case. Match it case-insensitively so an
ALL-CAPS signature is recognized; the 'The Honorable ..., Judge' trial-judge line
and the 'Division Two: ...' panel line are still excluded (the first by the
shared non-author prefixes, the second because the name half holds a colon)."""

from __future__ import annotations

import html as _html


def _strip_tags(s: str) -> str:
    out, depth = [], 0
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return _html.unescape("".join(out)).strip()


_MO_TITLES = {
    "judge",
    "chief judge",
    "presiding judge",
    "senior judge",
    "special judge",
    "chief justice",
    "justice",
    "cj",
    "pj",
    "j",
}


def _mo_opinion_heading(text: str) -> str | None:
    """The centered heading that opens a *separate* writing — 'DISSENTING
    OPINION' / 'CONCURRING OPINION' / 'CONCURRING IN PART AND DISSENTING IN PART
    OPINION'. Returns the opinion type, or None."""
    u = " ".join(text.upper().split())
    if not u.endswith("OPINION"):
        return None
    has_d, has_c = "DISSENT" in u, "CONCUR" in u
    if has_d and has_c:
        return "concurring-in-part-and-dissenting-in-part"
    if has_d:
        return "dissent"
    if has_c:
        return "concurrence"
    return None


def _mo_is_vote_line(text: str) -> bool:
    """A panel member's concurrence/dissent vote — 'NAME, J., concurs.' /
    'NAME, C.J., concurs.' / 'NAME, J. – CONCURS' — which signals an authored
    opinion is present even when its author is signed only with a /s/ image."""
    low = " ".join(text.split()).rstrip(".").lower()
    return (
        "," in text
        and text[:1].isupper()
        and (low.endswith("concur") or low.endswith("concurs")
             or low.endswith("dissent") or low.endswith("dissents"))
    )


def _mo_name_ok(name: str) -> bool:
    name = name.strip()
    if not name or ":" in name:
        return False
    toks = name.replace(",", " ").split()
    if not (1 <= len(toks) <= 5):
        return False
    for tok in toks:
        core = tok.rstrip(".").replace("'", "").replace("’", "")
        if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
            continue
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class MissouriStyle:
    # Missouri double-spaces the body but single-spaces block quotes (and
    # footnotes) at a tight leading below gap_tight_max, so an indented quote
    # would read as a 'notice'. Re-tag it by its both-margins indent.
    blockquote_by_indent = True

    def parse_author_line(self, text):
        t = text.strip().rstrip(".")
        if t.upper() == "PER CURIAM":
            return "PER CURIAM", "per curiam", None
        if "," in t:
            name, title = t.rsplit(",", 1)
            tl = title.strip().lower().replace(".", "")
            if tl in _MO_TITLES and _mo_name_ok(name):
                return name.strip(), title.strip().title(), None
        return super().parse_author_line(text)

    def _mo_first_body(self, all_segments):
        """Where the Court's own writing starts — past ALL of the front matter.

        Missouri's caption is a ')' rail, and below it sits the trial-court
        block ('APPEAL FROM THE CIRCUIT COURT OF ST. LOUIS COUNTY' / 'The
        Honorable Kristine Kerr, Judge'), centered. Both are headmatter. But
        the caption's last party row is double-spaced away from the rail rows
        above it and lands in the same segment as the 'APPEAL FROM' line, so
        that segment measures as 'body' — and taking it as the opinion start
        pulled the closing party row and the whole trial-court block into the
        first paragraph, and left the rail a row short.

        Every front-matter row gives itself away: it carries the rail glyph, or
        it is centered on the page's axis and stops short of the measure. A
        paragraph of opinion prose cannot do that — however its first line is
        indented, the lines that follow run out to the right margin."""
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        right = max(
            (l["x1"] for _p, seg, _k in all_segments for l in seg), default=pw - 72
        )

        def is_front_matter(line) -> bool:
            if ")" in self.line_plain_text(line).split():
                return True
            centered = abs((line["x0"] + line["x1"]) / 2 - pw / 2) < 25
            return centered and line["x1"] < right - 20

        # The appeal line and named trial judge are the final caption rows;
        # Missouri then prints the opinion title immediately before its prose.
        for i, (_p, seg, _kind) in enumerate(all_segments[:-1]):
            text = " ".join(self.line_plain_text(l).strip() for l in seg).lower()
            if "the honorable" in text and "judge" in text:
                return i + 1

        first_body = None
        for i, (_p, seg, kind) in enumerate(all_segments):
            if kind != "body":
                continue
            if first_body is None:
                first_body = i
            if all(
                is_front_matter(l)
                for l in seg
                if self.line_plain_text(l).strip()
            ):
                continue  # still in the caption / trial-court block
            return i
        return first_body

    def find_authors(self, all_segments) -> list:
        """Missouri signs the author at the END of each opinion ('NAME, Judge',
        centered), not at the start. So the byline pipeline is inverted: each
        signature *closes* an opinion. The Court's opinion runs from the first
        body segment to the first signature; any later writing runs from its
        'DISSENTING/CONCURRING OPINION' heading to its own signature. Returns the
        opinion-START indices and records (start, author, type) for each."""
        self._mo_opinions = []
        sigs = []  # (segment index, author) for each end-of-opinion signature
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            txt = self.line_plain_text(seg[0]).strip()
            if self._mo_sig_role(txt) == "author":
                sigs.append((i, self.parse_author_line(txt)[0]))
        first_body = self._mo_first_body(all_segments)
        if not sigs:
            starts = super().find_authors(all_segments)
            if starts:
                return starts
            # No text author. Eastern District judges sign with a /s/ signature
            # IMAGE, so the only judge lines are the panel's concurrence votes —
            # the opinion is still authored and present. Emit it as one
            # author-unknown opinion rather than dumping the body into headmatter.
            votes = any(
                _mo_is_vote_line(self.line_plain_text(seg[0]).strip())
                for _p, seg, _k in all_segments
                if seg
            )
            if votes and first_body is not None:
                self._mo_opinions = [(first_body, "", "majority")]
                return [first_body]
            return []
        if first_body is None:
            first_body = 0
        starts = []
        prev = -1
        for k, (sidx, author) in enumerate(sigs):
            if k == 0:
                start, typ = first_body, "majority"
            else:
                # A later writing opens at its 'DISSENTING/CONCURRING OPINION'
                # heading; absent one, right after the previous signature.
                start, typ = prev + 1, "concurrence"
                for j in range(prev + 1, sidx):
                    ht = _mo_opinion_heading(self.line_plain_text(all_segments[j][1][0]).strip())
                    if ht:
                        start, typ = j, ht
                        break
            starts.append(start)
            self._mo_opinions.append((start, author, typ))
            prev = sidx
        return starts

    def extract(self, pdf_path):
        self._mo_logo = None
        return super().extract(pdf_path)

    def extract_page_images(self, page):
        """Missouri pages carry only furniture images: the court seal in the
        page-1 caption banner and the judges' /s/ signature graphics at the end.
        Neither is opinion content — capture the seal for the headmatter and
        drop the rest, so nothing image lands in the opinion body."""
        if page.page_number == 1 and getattr(self, "_mo_logo", None) is None:
            top = [
                im
                for im in super().extract_page_images(page)
                if im["top"] < page.height * 0.4
            ]
            if top:
                self._mo_logo = min(top, key=lambda im: im["top"])["data"]
        return []

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Style-preserving headmatter, with the parties/docket caption box
        folded into a clean two-column block and the court seal placed on top."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        # The shared rail fold, not the local one: it keeps ONE rail glyph per
        # printed row, including the rail-only rows the caption stacks between
        # party names, so the bracket keeps its true height and the two columns
        # stay opposite the rows they were printed on.
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        if getattr(self, "_mo_logo", None):
            d["summary"] = [{"__image__": True, "src": self._mo_logo}] + d["summary"]
        return d

    @staticmethod
    def _mo_fold_caption(rows: list) -> list:
        """Collapse the run of ')'-rail caption rows into one two-column
        ``__caption__`` block — parties on the left, docket + opinion-date on the
        right of the paren rail ('PARTY ) No. SC123' / 'PARTY )')."""
        out, left, right = [], [], []

        def flush():
            if left or right:
                out.append(
                    {
                        "__caption__": True,
                        "left": list(left),
                        "right": list(right),
                        "rail": ")",
                    }
                )
                left.clear()
                right.clear()

        for r in rows:
            if not (isinstance(r, dict) and r.get("__hm__")):
                flush()
                out.append(r)
                continue
            text = _strip_tags(r.get("html", ""))
            if " ) " in text:
                lpart, rpart = text.split(" ) ", 1)
                if lpart.strip():
                    left.append(lpart.strip())
                if rpart.strip():
                    right.append(rpart.strip())
            elif text.endswith(")"):
                rest = text[:-1].strip()
                if rest:
                    left.append(rest)
            elif text.startswith(")"):
                rest = text[1:].strip()
                if rest:
                    right.append(rest)
            elif text.strip() == ")":
                pass  # bare rail segment
            else:
                flush()
                out.append(r)
        flush()
        return out

    def _mo_sig_role(self, text: str):
        """Classify a candidate end-of-opinion signature: 'author' for a real
        opinion author ('NAME, Judge' / 'NAME, J. – OPINION AUTHOR'), 'vote' for
        a panel member's bare concurrence/dissent vote that opens no separate
        writing ('NAME, J. – CONCURS' / 'NAME, C.J., concurs.'), else None."""
        r = self.parse_author_line(text)
        if not (r and r[1]) or self._is_non_author_byline(text):
            return None
        low = text.lower()
        # A line naming TWO judges is the panel roster, not a signature — the
        # 'Before Division Three: Mark D. Pfeiffer, Presiding Judge, / Cynthia
        # L. Martin, Judge, and Janet Sutton, Judge' line wraps, and its second
        # row reads as 'NAME, Judge' exactly like a signed opinion. Taking it
        # closed an opinion that had not started, which handed the Court's
        # writing to the next judge who signed.
        if sum(low.count(t) for t in ("judge", "justice")) > 1:
            return None
        if "opinion author" in low:
            return "author"
        if "concur" in low or "dissent" in low:
            return "vote"
        return "author"

    def _mo_opinion_at(self, op_start):
        for start, author, typ in getattr(self, "_mo_opinions", []):
            if start == op_start:
                return author, typ
        return None

    def split_author_line(self, line):
        # Signature model: the opinion's opening line is body, not a byline.
        if getattr(self, "_mo_opinions", None):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        found = self._mo_opinion_at(op_start)
        if found:
            author, typ = found
            # justified signature lines carry word-spacing runs
            # ('KELLY  C.  BRONIEC') — collapse to single spaces
            op.author = " ".join(str(author or "").split())
            op.type = typ
        return op
