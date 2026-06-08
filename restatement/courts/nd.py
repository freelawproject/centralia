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

    def extract(self, pdf_path):
        self._nd_dropped = []
        doc = super().extract(pdf_path)
        # Record the dropped running headers (deduped) so they are accounted for
        # rather than silently lost.
        seen, uniq = set(), []
        for t in self._nd_dropped:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        if uniq:
            doc.dropped = list(doc.dropped) + uniq
        return doc

    # ------------------------------------------------------- running header
    def _maybe_drop_running_header(self, page, lines):
        """Drop the page-2 running header — the bold case caption + docket band
        at the very top (the byline sits lower, ~top 118, so the cutoff keeps
        it). Title page (page 1) is untouched; dropped lines are recorded."""
        if page.page_number <= 1:
            return lines
        kept = []
        for ln in lines:
            _size, _font, bold = self.line_meta(ln)
            if bold and ln.get("top", 999) < 105:
                t = self.line_plain_text(ln).strip()
                if t:
                    getattr(self, "_nd_dropped", []).append(t)
                continue
            kept.append(ln)
        return kept

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

    def split_body_paragraphs(self, seg):
        return self._split_on_pilcrow(seg)

    def split_blockquote_paragraphs(self, seg):
        return self._split_on_pilcrow(seg)
