"""U.S. Courts of Appeals — shared base for the numbered circuits + D.C. + Fed.

Ported from the proven ca1 ``circuit`` reference, re-expressed without regex.
Each circuit is its own subclass in its own file (ca1.py … cafc.py) with its
own column/gap/footnote tuning — circuits are non-monolithic.

Page-1 layout: centered banner 'United States Court of Appeals' / 'For the Nth
Circuit'; left docket 'No. 25-1160'; centered ALL-CAPS party block with role
lines; centered history 'APPEAL FROM THE UNITED STATES DISTRICT COURT ...';
bracketed trial-judge line; panel intro 'Before <judges>, Circuit Judges.';
attorneys; centered date. The opinion body opens INLINE with the author —
'AFRAME, Circuit Judge. This is an appeal...' (period form) or 'PAN, Circuit
Judge: ...' / 'Edith Brown Clement, Circuit Judge:' (colon form) or
'PER CURIAM. ...'. Federal bylines are NOT reliably bold, so detection is by
FORM: a name, a singular bench title (Circuit/District/Chief/Senior Judge),
then a '.'/':' terminator. The 'Before ... Judges.' roster (plural) is excluded.
"""

from __future__ import annotations

from typing import Optional

from .generic import GenericExtractor, _is_name

_BENCH = ("Judge", "Justice")
# Lines whose leading word is a headmatter label, never the author.
_NON_AUTHOR = (
    "FILED",
    "OPINION",
    "SUMMARY",
    "COUNSEL",
    "NOTICE",
    "CERTIFIED",
    "PUBLISH",
    "DO NOT PUBLISH",
    "AMENDED",
    "RECOMMENDED",
    "UNITED STATES",
    "BEFORE ",
    "APPEAL FROM",
)


class FederalCircuitBase(GenericExtractor):
    # Federal bodies are ~1.5-spaced. Per-circuit subclasses override these.
    gap_tight_max = 10.0
    gap_single_max = 22.0
    gap_double_max = 32.0
    body_baseline_x0 = 72.0
    circuit_phrase = ""

    author_titles = (
        "Chief Circuit Judge",
        "Senior Circuit Judge",
        "Circuit Judge",
        "District Judge",
        "Chief Judge",
        "Senior Judge",
        "Judge",
        "Circuit Justice",
        "Justice",
    )

    # Pages 2+ open with a centered 'No. <docket>' running header at top~75;
    # drop content above this. Subclasses with no such header lower it.
    page2_header_cutoff = 95.0

    # The clerk's e-filing stamp on page 1 (the top-right 'FILED / <court> /
    # <date> / <clerk name> / Clerk of Court' block) is furniture, not headmatter.
    # A circuit identifies it by FONT + SIZE: the stamp is set in a bold face at a
    # size the centered court banner does not use, so a (font, size) match drops
    # the stamp while leaving the banner — and splits the one line that merges
    # the banner's 'FOR THE TENTH CIRCUIT' (size 13) with the stamp's 'Clerk of
    # Court' (size 12). Left None on circuits not yet tuned (no drop). The match
    # is on the font-name SUFFIX so subset prefixes ('YRKGHW+...') still match.
    efile_stamp_font = None
    efile_stamp_size = None

    def extract(self, pdf_path):
        self._efile_stamp_dropped = []
        doc = super().extract(pdf_path)
        # de-dup, preserve first-seen order
        extra = list(dict.fromkeys(self._efile_stamp_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def _is_stamp_char(self, c) -> bool:
        if self.efile_stamp_font is None or self.efile_stamp_size is None:
            return False
        fn = c.get("fontname") or ""
        return fn.endswith(self.efile_stamp_font) and (
            abs(c.get("size", 0) - self.efile_stamp_size) < 0.1
        )

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number != 1 or self.efile_stamp_font is None:
            return lines
        if getattr(self, "_efile_stamp_dropped", None) is None:
            self._efile_stamp_dropped = []
        kept = []
        for ln in lines:
            chars = ln.get("chars") or []
            stamp = [c for c in chars if self._is_stamp_char(c)]
            if not stamp:
                kept.append(ln)
                continue
            dropped = self.line_plain_text({"chars": stamp}).strip()
            if dropped:
                self._efile_stamp_dropped.append(dropped)
            rest = [c for c in chars if not self._is_stamp_char(c)]
            if rest:  # a mixed line (banner + stamp tail): keep the banner part
                kept.append(self._rebuild_line(ln, rest))
        return kept

    @staticmethod
    def _rebuild_line(ln, chars):
        new = dict(ln)
        new["chars"] = chars
        new["x0"] = min(c["x0"] for c in chars)
        new["x1"] = max(c["x1"] for c in chars)
        new["top"] = min(c["top"] for c in chars)
        new["bottom"] = max(c["bottom"] for c in chars)
        new["text"] = "".join(c["text"] for c in sorted(chars, key=lambda c: c["x0"]))
        return new

    # ---------------------------------------------------------------- byline
    def find_authors(self, all_segments) -> list:
        # Detect opinion starts ONLY via the strict form-based byline (not the
        # permissive parse_author_line, which exists only to label kind). Drop a
        # byline with no opinion body before the next one — that is the
        # trial-judge history line ('..., District Judge.') sitting just above
        # the real author, not an opinion.
        self._pc_starts = set()
        cands = [
            i
            for i, (_p, seg, _k) in enumerate(all_segments)
            if seg and self._byline_split(seg[0]) is not None
        ]
        out = []
        for n, i in enumerate(cands):
            end = cands[n + 1] if n + 1 < len(cands) else len(all_segments)
            if self._opinion_has_body(all_segments, i, end):
                out.append(i)
        if out:
            return out
        # No signed byline and no PER CURIAM / BY THE COURT line: an UNSIGNED per
        # curiam opinion. It opens immediately after the panel roster ('Before:
        # <judges>, Circuit Judges.'); author is PER CURIAM. Without this the
        # whole opinion would fall into the headmatter.
        start = self._percuriam_start(all_segments)
        if start is not None:
            self._pc_starts.add(start)
            return [start]
        return []

    def _percuriam_start(self, all_segments):
        """Index of the first opinion-body segment after the panel roster, for an
        unsigned per curiam opinion, or None. The roster is a single line opening
        'Before' that names the bench ('Before: WALKER, SULLIVAN, and BIANCO,
        Circuit Judges.'). The body is the next non-divider, non-empty segment."""
        panel = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip()
            low = t.lower()
            if low.startswith("before") and ("judge" in low):
                panel = i
        if panel is None:
            return None
        for j in range(panel + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def build_opinion(self, op_start, op_end, **kwargs):
        # An unsigned per curiam start has no byline line; keep its first line as
        # body and label the author PER CURIAM (set via the _pc_now flag, which
        # split_author_line below reads while super() consumes the first line).
        self._pc_now = op_start in getattr(self, "_pc_starts", set())
        op = super().build_opinion(op_start, op_end, **kwargs)
        self._pc_now = False
        if op_start in getattr(self, "_pc_starts", set()):
            op.author = "PER CURIAM"
            op.type = self.normalize_opinion_type(None)
        return op

    def split_author_line(self, line):
        if getattr(self, "_pc_now", False):
            return "PER CURIAM", [line]  # no byline line — keep it as body
        return super().split_author_line(line)

    def _byline_at(self, line) -> bool:
        return self._byline_split(line) is not None

    def _byline_split(self, line):
        """Federal byline by FORM (not bold): '<Name>, <singular bench title>'
        immediately followed by '.'/':' (or end of line). Returns
        (byline_text, inline_body_text) or None. Excludes 'Before ... Judges.'
        rosters and headmatter labels."""
        text = (line.get("text") or "").strip()
        if not text:
            return None
        up = text.upper()
        for bad in _NON_AUTHOR:
            if up.startswith(bad):
                if up.startswith("PER CURIAM"):
                    break
                return None
        if up.startswith("PER CURIAM") or up.startswith("BY THE COURT"):
            i = text.find(".")
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        if "," not in text:
            return None
        comma = text.index(",")
        name = text[:comma].strip()
        if not _is_name(name):
            return None
        for kw in _BENCH:
            start = 0
            while True:
                idx = text.find(kw, start)
                if idx == -1:
                    break
                end = idx + len(kw)
                if end < len(text) and text[end] == "s":  # 'Judges' = panel
                    start = end
                    continue
                # Everything from the name's comma to the title keyword must be
                # title qualifiers (and a name suffix), not sentence text — else
                # this 'Judge' is incidental to a body line ('Moreover, ... must
                # be considered. Judge ...'), not a byline.
                if not self._is_title_run(text[comma + 1 : idx]):
                    start = end
                    continue
                j = end
                while j < len(text) and text[j] == " ":
                    j += 1
                if j >= len(text):
                    return text, ""
                if text[j] in ".:":
                    return text[: j + 1], text[j + 1 :].strip()
                start = end
        return None

    # Words that may sit between a judge's name and the bench title ('Senior
    # Circuit Judge', 'United States District Judge'), plus name suffixes
    # ('JAMES E. GRAVES, JR., Circuit Judge'). Anything else there means the
    # 'Judge' belongs to a sentence, not a byline.
    _TITLE_RUN_WORDS = frozenset(
        {
            "circuit", "senior", "chief", "district", "united", "states",
            "associate", "presiding", "acting", "supreme", "magistrate",
            "bankruptcy", "jr", "sr", "ii", "iii", "iv", "us",
        }
    )

    def _is_title_run(self, span: str) -> bool:
        for t in span.replace(",", " ").split():
            tl = t.strip(".").lower()
            if tl in self._TITLE_RUN_WORDS:
                continue
            if len(tl) == 1 and tl.isalpha():  # a 'J.' judicial / name initial
                continue
            return False
        return True

    def parse_author_line(self, text):
        """Parse a federal byline into (name, title, kind). Handles the period
        form via the base, plus the colon form ('PAN, Circuit Judge:') and a
        trailing kind ('..., concurring')."""
        r = super().parse_author_line(text)
        if r is not None:
            return r
        if not text:
            return None
        t = text.strip().rstrip(".:").strip()
        if t.upper().startswith("PER CURIAM"):
            return ("PER CURIAM", "per curiam", None)
        if t.upper().startswith("BY THE COURT"):
            return ("By the Court", "per curiam", None)
        if "," not in t:
            return None
        name, rest = t.split(",", 1)
        name, rest = name.strip(), rest.strip()
        # Guard against ordinary body lines ('Shortly after the officers entered
        # the residence, they found ...'): the name must look like a judge name
        # and the part after the comma must name a judicial office. Without this
        # every comma-bearing body line parsed as a byline, fragmenting the body.
        if not _is_name(name):
            return None
        if not any(w in rest for w in ("Judge", "Justice", "Chancellor")):
            return None
        low = rest.lower()
        kind = None
        for k in (
            "concurring in part and dissenting in part",
            "concurring in the judgment and dissenting in part",
            "concurring and dissenting",
            "concurring in the judgment",
            "concurring in part",
            "dissenting in part",
            "concurring",
            "dissenting",
        ):
            if k in low:
                kind = k
                break
        return (name.strip(), rest, kind)

    # ---------------------------------------------------------------- layout
    def filter_margins(self, obj):
        page_no = obj.get("page_number", 1)
        if page_no > 1 and obj.get("top", 0) < self.page2_header_cutoff:
            return None
        return super().filter_margins(obj)

    def split_body_paragraphs(self, seg):
        """New paragraph at a first-line indent (x0 > body_baseline_x0 + 12);
        baseline lines continue the prior paragraph."""
        if not seg:
            return []
        threshold = self.body_baseline_x0 + 12
        paras = [[seg[0]]]
        for i in range(1, len(seg)):
            indented = seg[i].get("x0", 0) >= threshold
            prev_indented = seg[i - 1].get("x0", 0) >= threshold
            if indented and not prev_indented:
                paras.append([seg[i]])
            else:
                paras[-1].append(seg[i])
        return paras

    def find_footnote_separator(self, page) -> Optional[float]:
        """~144pt hairline at x0~72 in the bottom 2/3. Reject candidates that
        share a y-band with other hairlines (citation underlines)."""
        return self._sep_at(page, 68, 80)

    def _sep_at(self, page, x_lo, x_hi):
        rects = [r for r in page.rects if r["height"] < 2]
        cands = []
        for r in rects:
            if not (
                120 <= (r["x1"] - r["x0"]) <= 170
                and x_lo <= r["x0"] <= x_hi
                and r["top"] > page.height * 0.30
            ):
                continue
            if any(o is not r and abs(o["top"] - r["top"]) <= 2 for o in rects):
                continue
            cands.append(r)
        return min(cands, key=lambda r: r["top"])["top"] if cands else None

    def matches_expected_layout(self, pdf) -> bool:
        if not pdf.pages:
            return False
        target = (self.circuit_phrase or "").lower()
        for line in pdf.pages[0].extract_text_lines():
            t = line.get("text") or ""
            if "United States Court of Appeals" in t:
                return True
            if target and target in t.lower():
                return True
        return False
