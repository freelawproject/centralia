"""Armed Services Board of Contract Appeals.

')'-rail caption ('Appeal of - )' / 'ASBCA No. 64204'), 'APPEARANCES FOR
…' counsel block, then a centered 'OPINION BY ADMINISTRATIVE JUDGE McNULTY'
heading that names the author and opens the single decision. Ends with the
judge's dated signature, 'I concur' co-signature blocks, and the Board
Recorder's certification.
"""

from __future__ import annotations

from ._district import DistrictBase


class ArmedServicesBCA(DistrictBase):
    court_id = "asbca"
    court_label = "Armed Services Board of Contract Appeals."

    def find_authors(self, all_segments) -> list:
        self._district_author = None
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip()
            up = t.upper()
            if up.startswith("OPINION BY ") or up.startswith(
                "MEMORANDUM OPINION BY "
            ):
                # 'OPINION BY ADMINISTRATIVE JUDGE MCNULTY' — the name is
                # the tail after the title words
                tail = t.split("JUDGE")[-1].strip(" .") if "JUDGE" in up else ""
                if tail:
                    self._district_author = tail.title() if tail.isupper() else tail
                return [i]
            if start is None and up.rstrip(".") in (
                "ORDER OF DISMISSAL",
                "ORDER",
                "DECISION",
            ):
                start = i
        if start is not None:
            # dismissal orders sign 'NAME / Administrative Judge' — take
            # the ALL-CAPS name directly above an 'Administrative Judge'
            # title line
            lines = [
                self.line_plain_text(l).strip()
                for _p, seg, _k in all_segments
                for l in seg
            ]
            lines = [t for t in lines if t]
            for j in range(len(lines) - 1, 0, -1):
                if lines[j].lower().startswith("administrative judge"):
                    cand = lines[j - 1]
                    toks = cand.split()
                    if 2 <= len(toks) <= 5 and all(
                        w[:1].isupper() for w in toks
                    ):
                        self._district_author = (
                            cand.title() if cand.isupper() else cand
                        )
                        break
            return [start]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        if getattr(self, "_district_author", None):
            return self._district_author, [line]
        return super().split_author_line(line)
