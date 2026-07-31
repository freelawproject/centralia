"""Court of Appeals of Virginia.

The author is announced near the foot of the caption, after the panel ('Present:
Judges ...'), the appeal-from line, the trial judge, and the counsel block:

    [PUBLISHED|UNPUBLISHED] OPINION BY
    JUDGE RANDOLPH A. BEALES

then the opinion body. So the byline is the bold '[CHIEF/SENIOR ]JUDGE <ALL-CAPS
NAME>' announcement line; the opinion starts at the segment after it, and the
whole caption stays in the headmatter. The ALL-CAPS 'JUDGE NAME' distinguishes
the author from the 'Present: Judges ...' panel and the 'NAME, Judge' trial-court
line (both mixed-case). A separate writing is signed in-body ('JUDGE X, with whom
JUDGE Y joins, dissenting.'); a per-curiam order with no announcement falls back
to the default search.
"""

from __future__ import annotations

from ..models import DocType
from ._appellate import StateAppellate
from ._statesupreme import _is_byline_name

# Longest-first so a compound title wins over the bare 'JUDGE'.
_VAC_TITLES = ("ASSOCIATE JUDGE", "SENIOR JUDGE", "CHIEF JUDGE", "JUDGE")


class CourtOfAppealsOfVirginia(StateAppellate):
    court_id = "vactapp"
    court_label = "Court of Appeals of Virginia."
    # The body is double-spaced at the 72pt margin; a quotation is set single
    # spaced (~13.8pt leading) two steps in at x0=144 and stops well short of
    # the right measure. That tight leading falls in the 'notice' band, so the
    # quote reads as ordinary prose unless the both-margins geometry is used.
    blockquote_by_indent = True

    def extract(self, pdf_path):
        self._vac_meta = {}
        return super().extract(pdf_path)

    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """The corpus holds one document that is not a ruling at all: the
        clerk's dated list of published opinions appealed on to the Supreme
        Court. It carries no announcement and, unlike every opinion and every
        rehearing order, does not open on the court's banner — so it is a
        notice, not an unclassifiable document."""
        if not author_indices and all_segments and all_segments[0][1]:
            head = self.line_plain_text(all_segments[0][1][0]).strip().upper()
            if "COURT OF APPEALS OF VIRGINIA" not in head:
                return DocType.NOTICE
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def find_footnote_separator(self, page):
        """Virginia rules its footnotes off with the 2-inch rect at the body's
        left margin, and sets the footnote text at BODY size — so neither the
        size of the text below nor the page position distinguishes it.

        It also strokes two FULL-MEASURE shelves on the caption page, above and
        below the 'PUBLISHED OPINION BY / JUDGE NAME' announcement. Those are
        vector lines rather than rects, so the default finder only reaches them
        when the page carries no 2-inch rule — and then the lower shelf reads
        as the separator and swallows the byline and the opinion's opening
        paragraph into the footnote zone (the author was lost and the trial
        judge's caption line was taken as the byline instead). Keying on the
        court's own 2-inch separator rect removes the ambiguity."""
        return self.footnote_sep_fixed_left_rule(page)

    def find_authors(self, all_segments) -> list:
        self._vac_meta = {}
        # Every announced author: a bold '[CHIEF/SENIOR ]JUDGE <NAME>' line.
        # There can be more than one in a filing — an opinion granted on
        # rehearing is published together with the rehearing order and the
        # withdrawn original opinion, each with its own announcement.
        announced = []
        for i, (_p, seg, _k) in enumerate(all_segments):
            for ln in seg:
                a = self._vac_title_name(self.line_plain_text(ln).strip())
                if a:
                    announced.append((i, a))
                    break
        announced = [(i, a) for i, a in announced if i + 1 < len(all_segments)]
        if not announced:
            return super().find_authors(all_segments)
        starts = []
        for i, author in announced:
            body = i + 1
            if body in self._vac_meta:
                continue
            starts.append(body)
            self._vac_meta[body] = (author, "majority")
        first = starts[0]
        for i in range(first, len(all_segments)):
            if i in self._vac_meta:
                continue
            sep = self._vac_separate(all_segments[i][1])
            if sep:
                starts.append(i)
                self._vac_meta[i] = sep
        return sorted(starts)

    @staticmethod
    def _vac_title_name(text):
        for title in _VAC_TITLES:
            if text.startswith(title + " "):
                name = text[len(title) + 1 :].split(",")[0].strip()
                if _is_byline_name(name):
                    return f"{title} {name}"
        return None

    def _vac_separate(self, seg):
        text = self.line_plain_text(seg[0]).strip()
        author = self._vac_title_name(text)
        if author:
            blob = " ".join(self.line_plain_text(l) for l in seg[:3]).lower()
            if "dissent" in blob and "concur" in blob:
                return author, "concurring in part and dissenting in part"
            if "dissent" in blob:
                return author, "dissent"
            if "concur" in blob:
                return author, "concurrence"
            return None
        # A separate writing may instead be signed in the reporter's short
        # form on a line of its own at the body margin ('Causey, J.,
        # dissenting.'). The shared grammar rejects the title-case surname on
        # purpose — that is how a trial judge's caption line ('Cheryl V.
        # Higgins, Judge') is kept out — so the short form is read here.
        if seg[0].get("x0", 0) > self.body_baseline_x0 + 4:
            return None
        parsed = self._vac_short_byline(text)
        if not parsed:
            return None
        seg[0]["_vac_byline"] = text
        return text, self.normalize_opinion_type(parsed[1])

    @staticmethod
    def _vac_short_byline(text):
        """('Causey, J.', 'dissenting') for the short in-body byline, else None.

        Three commas' worth of structure carries it: a bare surname, an
        abbreviated title, and a lowercase participle naming the writing. A
        citation to another court's separate opinion always has the byline
        inside parentheses and other words ahead of it, so its head is never a
        lone capitalized surname."""
        t = " ".join(text.split())
        if not t.endswith(".") or t.count(",") < 2:
            return None
        head, title, tail = (p.strip() for p in t.rstrip(".").split(",", 2))
        if not head or " " in head or not head[:1].isupper():
            return None
        if not head.replace("'", "").replace("-", "").isalpha():
            return None
        # 'J.' / 'C.J.' / 'P.J.' — the abbreviated bench title, nothing else.
        bare = title.replace(".", "")
        if not title.endswith(".") or not bare.isupper() or not 1 <= len(bare) <= 3:
            return None
        low = tail.lower()
        if not tail[:1].islower():
            return None
        if "concur" not in low and "dissent" not in low:
            return None
        return f"{head}, {title}", tail

    def split_author_line(self, line):
        # A short-form in-body byline IS the byline line and is consumed as
        # such; the announced form sits in the caption above the body, so the
        # opinion's own first line is body text and must be kept.
        if line.get("_vac_byline"):
            return line["_vac_byline"], []
        if getattr(self, "_vac_meta", None):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        meta = getattr(self, "_vac_meta", {}).get(op_start)
        if meta:
            op.author, op.type = meta
        return op
