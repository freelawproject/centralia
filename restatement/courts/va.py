"""Supreme Court of Virginia.

The majority author is announced in the caption, not signed at the body. The
caption's right column carries 'OPINION BY' over a '[CHIEF/SENIOR ]JUSTICE
<NAME>' line (often merged into the record-number row, e.g. 'v. Record No. 250365
JUSTICE JUNIUS P. FULTON, III'), then the decision date. A centered 'FROM THE
COURT OF APPEALS ...' / 'FROM THE CIRCUIT COURT ...' line closes the caption, and
the opinion body opens immediately below it (an indented paragraph, no byline or
¶ marker). So, coloctapp-style: read the author off the caption, keep the whole
caption in the headmatter, and start the majority at the first segment after the
appeal-from block ('FROM THE COURT OF APPEALS ...', or an order's 'UPON AN APPEAL
FROM A JUDGMENT RENDERED BY THE COURT OF APPEALS ...'). An unsigned per-curiam
order — caption present but no 'OPINION BY' — is authored 'PER CURIAM'.

A separate writing is signed in-body, with an ALL-CAPS title byline that names
its joiners and its kind across one or two lines:

    CHIEF JUSTICE POWELL, with whom JUSTICE MANN and JUSTICE FULTON join,
    dissenting.

Those are detected as additional opinion starts (title + ALL-CAPS surname opening
a segment whose block carries 'dissenting'/'concurring'); the byline line is kept
as the writing's opening body line. A per-curiam order — no 'OPINION BY', no
appeal-from line — falls back to the default byline search.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name

# Longest-first so a compound title wins over the bare 'JUSTICE'.
_TITLES = ("ASSOCIATE JUSTICE", "SENIOR JUSTICE", "CHIEF JUSTICE", "JUSTICE")


class VirginiaSupreme(StateSupreme):
    court_id = "va"
    court_label = "Supreme Court of Virginia."

    def extract(self, pdf_path):
        self._va_meta = {}
        return super().extract(pdf_path)

    # ----------------------------------------------------------- opinion starts
    def find_authors(self, all_segments) -> list:
        self._va_meta = {}
        # The appeal-from block closes the caption: a centered 'FROM THE ...'
        # line (opinions) or an 'UPON AN APPEAL FROM ...' block (orders).
        from_idx = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if any(self._is_appeal_from(self.line_plain_text(ln)) for ln in seg):
                from_idx = i
                break

        starts, scan_from = [], 0
        if from_idx is not None:
            # The appeal-from source can run several right-aligned lines ('UPON AN
            # APPEAL FROM A / JUDGMENT RENDERED BY THE / COURT OF APPEALS ...');
            # skip them to the first left-aligned body paragraph.
            body = from_idx + 1
            while (
                body < len(all_segments)
                and all_segments[body][1][0]["x0"] >= 300
            ):
                body += 1
            if body < len(all_segments):
                # Announced author, or an unsigned per-curiam order.
                maj = self._va_author_in(all_segments[:body]) or "PER CURIAM"
                starts.append(body)
                self._va_meta[body] = (maj, "majority")
                scan_from = body

        # In-body separate writings (dissents / concurrences).
        for i in range(scan_from, len(all_segments)):
            if i in self._va_meta:
                continue
            info = self._va_separate(all_segments[i][1])
            if info:
                starts.append(i)
                self._va_meta[i] = info

        if not starts:
            # Per-curiam order (no announced author): default byline search.
            return super().find_authors(all_segments)
        return sorted(starts)

    @staticmethod
    def _is_appeal_from(text: str) -> bool:
        t = (text or "").strip().upper()
        return t.startswith("FROM THE ") or "APPEAL FROM" in t

    def _va_author_in(self, segments):
        """The announced majority author: the '[CHIEF/SENIOR ]JUSTICE <NAME>' run
        on a caption line (kept with its title, like coloctapp's 'JUDGE SCHUTZ').
        Taken from the title word to the line end, so a merged 'v. Record No.
        NNNN' lead is dropped."""
        for _p, seg, _k in segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                for title in _TITLES:
                    j = t.find(title + " ")
                    if j != -1:
                        return t[j:].strip()
        return None

    def _va_separate(self, seg):
        """If ``seg`` opens a separate writing, return (author, type); else None.
        The first line is a title + ALL-CAPS surname; the kind is read from the
        byline block (the disposition word can wrap onto the next line)."""
        author = self._va_title_name(self.line_plain_text(seg[0]).strip())
        if not author:
            return None
        blob = " ".join(self.line_plain_text(l) for l in seg[:3]).lower()
        if "dissent" in blob and "concur" in blob:
            return author, "concurring in part and dissenting in part"
        if "dissent" in blob:
            return author, "dissent"
        if "concur" in blob:
            return author, "concurrence"
        return None

    @staticmethod
    def _va_title_name(text):
        for title in _TITLES:
            if text.startswith(title + " "):
                name = text[len(title) + 1 :].split(",")[0].strip()
                if _is_byline_name(name):
                    return f"{title} {name}"
        return None

    # ------------------------------------------------------------ author / body
    def split_author_line(self, line):
        # Every Virginia opinion opens on text (the majority on its first body
        # paragraph, a separate writing on its byline line); keep it as the
        # opening body line and let build_opinion stamp the author/type.
        if getattr(self, "_va_meta", None):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        meta = getattr(self, "_va_meta", {}).get(op_start)
        if meta:
            op.author, op.type = meta
        return op
