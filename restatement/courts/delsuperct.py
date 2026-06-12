"""Delaware Superior Court.

Trial court; single ruling by one judge, district-court model (the whole
ruling is one opinion). The author signs '/s/ Name' beside a state title
line ('Charles E. Butler, Resident Judge' / 'Judge Sonia Augusthy') the
federal title list doesn't know; some orders carry only a handwritten
signature image, in which case no text names the judge and the author
stays empty.
"""

from __future__ import annotations

from ._district import DistrictBase


class DelawareSuperiorCourt(DistrictBase):
    court_id = "delsuperct"
    court_label = "Delaware Superior Court."

    def _signature_author(self, all_segments):
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            if not lines[i].lower().startswith("/s"):
                continue
            name = lines[i]
            for pre in ("/s/", "/S/", "/s", "/S"):
                if name.startswith(pre):
                    name = name[len(pre) :].strip()
                    break
            # Prefer the adjacent name+title line ('Paul R. Wallace, Judge');
            # a bare title line ('Resident Judge') combines with the /s/ name.
            for j in (i + 1, i - 1):
                if 0 <= j < len(lines):
                    t = lines[j]
                    if len(t) < 60 and any(
                        w in t.lower() for w in ("judge", "commissioner", "justice")
                    ):
                        title_words = {
                            "judge", "resident", "president", "commissioner",
                            "justice", "chief", "the", "honorable",
                        }
                        toks = [w.strip(".,").lower() for w in t.split()]
                        if toks and all(w in title_words for w in toks):
                            return f"{name}, {t}" if name else t
                        return t
            return name or None
        return super()._signature_author(all_segments)
