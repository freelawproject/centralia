"""Supreme Court of Puerto Rico (Tribunal Supremo de Puerto Rico).

Spanish-language slip opinions on legal-size paper (612x1008):

  * page 1 is a COVER: the 'EN EL TRIBUNAL SUPREMO DE PUERTO RICO' banner,
    parties with roles (Recurrido / Peticionario), the citation block
    ('2026 TSPR 48' / '218 DPR ___'), 'Número del Caso:', 'Fecha:', the
    courts below, counsel, and 'Materia: …' — all headmatter — ending with
    a compilation notice ('Este documento está sujeto a los cambios y
    correcciones …') which is dropped and surfaced;
  * each WRITING restarts with its own repeated caption page (banner +
    parties + docket) — kept as headmatter for the first writing, dropped
    as furniture before the rest;
  * writing starts: a centered heading ('RESOLUCIÓN' / 'SENTENCIA' /
    'OPINIÓN' / 'PER CURIAM'), or a byline ('La Jueza Presidenta ORONOZ
    RODRÍGUEZ emitió una Opinión de conformidad', 'Voto Particular
    Disidente emitido por el Juez Asociado señor COLÓN PÉREZ, al cual se
    une …'). The ALL-CAPS surname run is the author; 'disidente' →
    dissent, 'conformidad'/'concurrente' → concurrence. Mid-paragraph
    references ('el foro de instancia emitió una Sentencia') never start
    with the El Juez/La Jueza + emitió shape and are not bylines.
"""

from __future__ import annotations

from ..models import DocType
from ._statesupreme import StateSupreme

_HEADINGS = {"RESOLUCIÓN", "SENTENCIA", "OPINIÓN", "PER CURIAM"}
_HEAD_TYPES = {
    "RESOLUCIÓN": "order",
    "SENTENCIA": "judgment",
    "OPINIÓN": "majority",
    "PER CURIAM": "majority",
}
_CAPS_EXTRA = "ÁÉÍÓÚÜÑ"


def _caps_run(text: str) -> str:
    """The first run of consecutive ALL-CAPS tokens (accented capitals
    included) — the justice's surname(s) in a Spanish byline."""
    run = []
    for tok in text.replace(",", " ").split():
        core = tok.strip(".;:()")
        iscaps = (
            len(core) >= 2
            and all(c.isupper() or c in _CAPS_EXTRA for c in core if c.isalpha())
            and any(c.isalpha() for c in core)
        )
        if iscaps and core.upper() not in ("TSPR", "DPR", "LLC", "INC"):
            run.append(core)
        elif run:
            break
    return " ".join(run)


class PuertoRicoSupreme(StateSupreme):
    court_id = "prsupreme"
    court_label = "Supreme Court of Puerto Rico."

    # legal-size paper (612x1008) — the letter-size default (725) would
    # margin-filter the bottom third of every page
    margin_bottom = 975

    # the body is monospace Courier; the court bolds dates and times inline
    # ('20 de mayo de 2025.', '10:28 p.m. del 20 de junio de 2025') — emphasis,
    # not structure. Don't let a bold line break the paragraph (headings are
    # centered/short and still separate by alignment + gap).
    bold_breaks_segment = False

    # Every writing closes with a two-line sign-off stack — the clerk's
    # printed name over his title ('Javier O. Sepúlveda Rodríguez' /
    # 'Secretario del Tribunal Supremo'), a justice's over hers ('Ángel Colón
    # Pérez' / 'Juez Asociado') — set short and right of the body column.
    # Joined as if wrapped they read as one run-on name-and-title; nothing in
    # the Spanish prose here is short enough on BOTH lines to be caught by the
    # same test, so the stack splitter is safe to switch on. It also keeps the
    # court's quoted statutory fragments ('[…]', '(i) Actos lascivos …',
    # '(ii) …') as the separate lines the source sets.
    split_line_stacks = True

    # every continuation page tops with a docket-number running header —
    # 'CC-2025-0671 2' / 'AB-2023-135 2' (PR docket + page number). Drop it as
    # furniture; left in the body it also lands mid-paragraph when the
    # cross-page merge spans the page break.
    running_header_docket = True

    def find_footnote_separator(self, page):
        """PR footnotes use a two-inch rule at the body margin.

        Consolidated-case caption boxes also draw long horizontal shelves in
        the lower half of a legal-size page.  The generic ``>=100pt`` rule
        detector can mistake those shelves for footnote separators and swallow
        the writing below them.  Match the invariant 144pt footnote rule.
        """
        return self.footnote_sep_fixed_left_rule(page, x0_max=132)

    def _byline_at(self, line) -> bool:
        """PR writing markers are Spanish prose bylines or centered writing
        headings, not the English ``NAME, Justice`` form understood by the
        shared splitter.

        Detecting them at the line level is important: on legal-size pages a
        repeated caption and the byline can occupy one loose segment.  Split
        there before ``find_authors`` so the caption remains headmatter and the
        complete writing becomes body.
        """
        return self._start_kind(self.line_plain_text(line).strip()) is not None

    def is_docket_line(self, text) -> bool:
        """A PR docket running header: one '<LL>-<YYYY>-<n>' token (a 2–3 letter
        prefix, 4-digit year, number) optionally flanked by a bare page
        number — and nothing else."""
        toks = (text or "").split()
        if not (1 <= len(toks) <= 2):
            return False
        if len(toks) == 2:  # strip an optional page number off either end
            if toks[-1].isdigit():
                toks = toks[:1]
            elif toks[0].isdigit():
                toks = toks[1:]
            else:
                return False
        parts = toks[0].split("-")
        if len(parts) != 3:
            return False
        pref, year, num = parts
        return (
            pref.isalpha()
            and pref.isupper()
            and len(pref) <= 3
            and len(year) == 4
            and year.isdigit()
            and num.isdigit()
        )

    # ------------------------------------------------------- writing starts
    @classmethod
    def _start_kind(cls, text: str):
        """(author, type) if ``text`` opens a writing, else None."""
        t = text.strip()
        up = t.upper().rstrip(".")
        # the real headings print in ALL CAPS ('RESOLUCIÓN'); a wrapped
        # sentence fragment ('… emitió una / Opinión.') must not match
        if up in _HEADINGS and t.rstrip(".") == t.rstrip(".").upper():
            return ("PER CURIAM" if up == "PER CURIAM" else ""), _HEAD_TYPES[up]
        low = t.lower()

        def kind_of(default):
            if "disidente" in low:
                return "dissent"
            if "conformidad" in low or "concurrente" in low:
                return "concurrence"
            return default

        # 'Voto Particular Disidente emitido por el Juez Asociado señor …'
        if low.startswith(("voto particular", "voto explicativo")) and (
            "emitido por" in low or "emitida por" in low
        ):
            return cls._byline_name(t), kind_of("voto-particular")
        # 'Opinión del Tribunal emitida por la Jueza Asociada Rivera Pérez.'
        # / 'Opinión de conformidad emitida por …'
        if low.startswith(("opinión", "opinion")) and (
            "emitida por" in low or "emitido por" in low
        ):
            return cls._byline_name(t), kind_of("majority")
        # 'La Jueza Presidenta ORONOZ RODRÍGUEZ emitió una Opinión de …'
        if low.startswith(("el juez", "la jueza")) and (
            "emitió" in low or "emitio" in low
        ):
            if any(w in low for w in ("opinión", "opinion", "voto", "sentencia")):
                return cls._byline_name(t), kind_of("majority")
        # The same byline in the PRESENT tense ('La Jueza Presidenta ORONOZ
        # RODRÍGUEZ emite una Opinión de conformidad'). The certification
        # paragraph that closes every writing announces the separate writings
        # with the same words ('… El Juez Asociado señor Colón Pérez emite
        # Opinión Disidente.'), and that sentence must NOT open a writing — so
        # require the ALL-CAPS surname the court reserves for a real byline.
        # The announcement always sets the name in title case.
        if low.startswith(("el juez", "la jueza")) and "emite" in low:
            if any(w in low for w in ("opinión", "opinion", "voto", "sentencia")):
                caps = _caps_run(t)
                if caps:
                    return caps, kind_of("majority")
        return None

    @staticmethod
    def _byline_name(t: str) -> str:
        """The justice's name from a byline: the ALL-CAPS surname run
        ('ORONOZ RODRÍGUEZ'), or the title-case name after the honorific
        ('… emitida por la Jueza Asociada Rivera Pérez.' → 'Rivera Pérez')."""
        name = _caps_run(t)
        if name:
            return name
        low = t.lower()
        i = max(low.find(" por "), low.rfind(" por la "), low.rfind(" por el "))
        # 'El Juez Asociado Señor Candelario López emitió la Opinión' — the
        # title-first shape, where the name precedes the verb and there is no
        # 'por' to key on. Read from the head of the line instead: the
        # honorific run, then the name, then the lowercase verb ends it.
        rest = t[i + 5 :] if i >= 0 else t
        skip = {
            "la", "el", "jueza", "juez", "asociada", "asociado",
            "presidenta", "presidente", "señor", "señora", "sr", "sra",
            "don", "doña", "interina", "interino",
        }
        out = []
        for tok in rest.split():
            core = tok.strip(".,;:()")
            if not core:
                break
            if core.lower() in skip and not out:
                continue
            if core[0].isupper() and any(c.isalpha() for c in core):
                out.append(core)
                if tok.endswith((".", ",")):
                    break
            else:
                break
        return " ".join(out)

    def find_authors(self, all_segments) -> list:
        self._pr_meta = {}
        out = []
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip()
            r = self._start_kind(text)
            if r is None:
                continue
            author, kind = r
            # a wrapped byline carries the name onto the next line — a
            # trailing surname ('… señor COLÓN / PÉREZ, al cual …') or the
            # WHOLE name ('… la Jueza Asociada señora / Pabón Charneco.')
            if len(seg) > 1 and not text.rstrip().endswith("."):
                nxt = self.line_plain_text(seg[1]).strip()
                toks = nxt.split()
                if author:
                    first = toks[0].strip(",.") if toks else ""
                    if (
                        first
                        and first[0].isupper()
                        and all(c.isalpha() for c in first)
                        and first.lower() not in ("en", "el", "la", "al")
                    ):
                        author = author + " " + first
                else:
                    cont = _caps_run(nxt)
                    if not cont:
                        parts = []
                        for tok in toks:
                            core = tok.strip(".,;:")
                            if (
                                core
                                and core[0].isupper()
                                and any(c.isalpha() for c in core)
                                and core.lower() not in ("en", "san")
                            ):
                                parts.append(core)
                                if tok.endswith("."):
                                    break
                            else:
                                break
                        cont = " ".join(parts)
                    author = cont
            # the kind word can sit on the wrapped second line ('… emitió
            # una Opinión de / conformidad') — re-test with both lines
            if len(seg) > 1:
                both = (text + " " + self.line_plain_text(seg[1])).lower()
                if "disidente" in both:
                    kind = "dissent"
                elif "conformidad" in both or "concurrente" in both:
                    kind = "concurrence"
            self._pr_meta[i] = (author, kind)
            out.append(i)
        return out

    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """This court publishes two distinct styles and the corpus holds both.

        An OPINION carries a named author ('la Jueza Asociada señora Pabón
        Charneco emitió la Opinión del Tribunal', 'PER CURIAM') and closes
        with its own SENTENCIA. A RESOLUCIÓN — the administrative and
        disciplinary docket: the summer-session assignments, the inactive-status
        approvals, the appointment of the executive director, a denied
        certiorari — is issued by the Court as a body and has no author at all.
        Eight of the twenty fixtures are that second style.

        Both reach ``find_authors`` because a centered writing heading opens a
        writing either way, so the shared 'a byline means an opinion' rule
        reported all twenty as opinions. The lead writing is the document's
        style: an unauthored 'order' writing in front means a resolución, even
        when a justice dissents from it.
        """
        kinds = getattr(self, "_pr_meta", {})
        if author_indices:
            lead = kinds.get(author_indices[0])
            if lead is not None:
                author, kind = lead
                if kind == "order" and not author:
                    return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def split_body_paragraphs(self, seg):
        """Keep stacked centered outline labels as separate headings.

        The ordinary paragraph splitter quite reasonably treats consecutive
        lines at the same deep indent as one indented block.  PR instead uses
        that exact geometry for two successive outline labels (``II`` / ``i.``),
        which must not become the synthetic text ``II i.``.
        """
        # Cut around short centered labels *before* the generic splitter.  If
        # they remain in a larger prose group, the group's overall geometry
        # masks their centered alignment.
        pw = getattr(self, "_page1_width", None) or 612.0
        chunks, cur = [], []
        for line in seg:
            text = self.line_plain_text(line).strip()
            is_label = (
                text
                and len(text) <= 12
                # The opinion column is x≈122–547, centered at ≈335 rather
                # than at the physical legal-size page center (306).
                and abs((line["x0"] + line["x1"]) / 2 - 335) <= 35
            )
            if is_label:
                if cur:
                    chunks.append(cur)
                    cur = []
                chunks.append([line])
            else:
                cur.append(line)
        if cur:
            chunks.append(cur)
        paras = [
            para
            for chunk in chunks
            for para in super().split_body_paragraphs(chunk)
        ]
        out = []
        for para in paras:
            if (
                len(para) > 1
                and all(
                    len(self.line_plain_text(line).strip()) <= 8
                    and self.line_alignment(line, pw) == "C"
                    for line in para
                )
            ):
                out.extend([[line] for line in para])
            else:
                out.append(para)
        return out

    def classify_paragraph(self, lines) -> str:
        """Classify PR outline headings and indented quotations by geometry."""
        if not lines:
            return "p"
        pw = getattr(self, "_page1_width", None) or 612.0
        texts = [self.line_plain_text(line).strip() for line in lines]
        joined = " ".join(texts)
        marker = joined.rstrip(".")
        outline = (
            bool(marker)
            and (
                all(c in "IVXLCDM" for c in marker)
                or all(c in "ivxlcdm" for c in marker)
                or (len(marker) == 1 and marker.isalpha())
            )
        )
        if (
            joined
            and (
                outline
                or joined.upper().rstrip(".") in _HEADINGS
                or joined == "Se dictará Sentencia en conformidad."
            )
            and all(
                abs((line["x0"] + line["x1"]) / 2 - 335) <= 35
                for line in lines
            )
        ):
            return "heading"
        return "p"

    def split_author_line(self, line):
        # the byline/heading line is the start marker; keep it as body text
        # so nothing is lost — the author comes from the start metadata
        return "", [line]

    def extract(self, pdf_path: str):
        self._pr_dropped = []
        self._pr_seen_start = False
        doc = super().extract(pdf_path)
        # type + author from the start markers, in order
        metas = [self._pr_meta[k] for k in sorted(getattr(self, "_pr_meta", {}))]
        for op, (author, kind) in zip(doc.opinions, metas):
            op.author = author
            op.type = kind
        return doc

    def _sweep_residual(self, doc, source_pages) -> None:
        """Flush the cover notice and the repeated caption pages onto the
        document BEFORE the completeness sweep.

        The sweep runs INSIDE ``super().extract()``, so adding this furniture
        to ``doc.dropped`` after that call returned was too late: the four
        lines of the cover's compilation notice ('Este documento está sujeto a
        los cambios y correcciones …') were reported unplaced on every one of
        the 17 fixtures that carries one — 68 lines — while sitting in the
        Removed box the whole time.
        """
        extra = list(dict.fromkeys(getattr(self, "_pr_dropped", []) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    # ------------------------------------------------------- page furniture
    def page_lines(self, page):
        if not hasattr(self, "_pr_dropped"):
            self._pr_dropped = []
        if not hasattr(self, "_pr_seen_start"):
            self._pr_seen_start = False
        lines = super().page_lines(page)
        # the cover's compilation notice: from 'Este documento está sujeto'
        # to the end of page 1 — dropped, surfaced
        if page.page_number == 1:
            out, in_notice = [], False
            for l in lines:
                t = self.line_plain_text(l).strip()
                if t.lower().startswith("este documento está sujeto"):
                    in_notice = True
                if in_notice:
                    if t:
                        self._pr_dropped.append(t)
                else:
                    out.append(l)
            return out
        # a repeated caption page tops every LATER writing: banner + parties
        # + docket above the writing-start line — furniture once the first
        # writing has begun
        start_idx = None
        for i, l in enumerate(lines):
            if self._start_kind(self.line_plain_text(l).strip()) is not None:
                start_idx = i
                break
        if start_idx is not None:
            if self._pr_seen_start and start_idx > 0:
                for l in lines[:start_idx]:
                    t = self.line_plain_text(l).strip()
                    if t:
                        self._pr_dropped.append(t)
                lines = lines[start_idx:]
            self._pr_seen_start = True
        return lines
