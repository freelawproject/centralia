"""Oregon Tax Court, Magistrate Division.

')'-rail caption under the 'IN THE OREGON TAX COURT / MAGISTRATE
DIVISION' banner, a centered decision heading ('DECISION' / 'DECISION OF
DISMISSAL' / 'ORDER …'), and a closing block 'This document was signed by
Magistrate Richard D. Davis and entered on <date>' that names the author.
A running footer ('ORDER TC-MD 250545R 6') sits in the bottom margin.
"""

from __future__ import annotations

from ._district import DistrictBase


class OregonTaxMagistrate(DistrictBase):
    court_id = "ortc"
    court_label = "Oregon Tax Court, Magistrate Division."

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        if not getattr(self, "_district_author", None):
            self._district_author = self._signed_by(all_segments)
        return out

    def _signed_by(self, all_segments):
        """Author from 'This document was signed by [Presiding] Magistrate
        Richard D. Davis and entered on <date>.'"""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for key in (
                    "signed by presiding magistrate ",
                    "signed by magistrate ",
                ):
                    ki = low.find(key)
                    if ki < 0:
                        continue
                    name = []
                    for tok in t[ki + len(key) :].split():
                        core = tok.strip(".,")
                        if tok.lower() in ("and", "on") or not core:
                            break
                        if core[0].isupper():
                            name.append(core + "." if len(core) == 1 else core)
                        else:
                            break
                    if name:
                        return " ".join(name)
        return None
