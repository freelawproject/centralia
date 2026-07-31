"""Generate an ecosystem-wide structural audit, one Markdown file per court.

This is deliberately read-only with respect to parsers and source PDFs.  It
extracts every fixture, runs the losslessness audit, records structural quality
signals, and writes a review corpus under ``output/ecosystem-audit``.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .audit import audit_coverage
from .models import DocType
from .registry import EXTRACTORS, get_extractor


FEDERAL_APPELLATE = {
    "scotus", "ca1", "ca2", "ca3", "ca4", "ca5", "ca6", "ca7", "ca8",
    "ca9", "ca10", "ca11", "cadc", "cafc",
}
FEDERAL_SPECIAL = {
    "tax", "cit", "uscfc", "cavc", "bap1", "bap6", "bap8", "bap9",
    "bap10", "armfor", "acca", "afcca", "nmcca", "uscgcoca", "asbca",
    "bia", "mspb", "ttab", "olc",
}
TERRITORIAL = {"dc", "guam", "nmariana", "prsupreme", "prapp", "virginislands"}
STATE_AG = {"calag", "mdag", "minnag", "texag"}


@dataclass
class FileResult:
    court: str
    file: str
    pages: int = 0
    doc_type: str = ""
    non_digital: bool = False
    layout_ok: bool = True
    opinions: int = 0
    blocks: int = 0
    paragraphs: int = 0
    blockquotes: int = 0
    headings: int = 0
    footnotes: int = 0
    headmatter_footnotes: int = 0
    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    residual_content: int = 0
    warnings: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    error: str | None = None


def _inline_values(text: str, tag: str, attr: str) -> list[str]:
    values, pos = [], 0
    needle = f"<{tag} {attr}=\""
    while True:
        start = text.find(needle, pos)
        if start == -1:
            return values
        start += len(needle)
        end = text.find('"', start)
        if end == -1:
            return values
        values.append(text[start:end])
        pos = end + 1


def _footnote_marks(text: str) -> list[str]:
    values, pos = [], 0
    opening, closing = "<footnotemark>", "</footnotemark>"
    while True:
        start = text.find(opening, pos)
        if start == -1:
            return values
        start += len(opening)
        end = text.find(closing, start)
        if end == -1:
            return values
        value = text[start:end].strip()
        if value:
            values.append(value)
        pos = end + len(closing)


def _quoted_footnote_definitions(texts: list[str]) -> set[str]:
    """Labels defined inline inside material quoted from another opinion.

    A quoted opinion can carry its own mark and quoted note as consecutive
    blockquotes. Those are not footnotes of the document being extracted and
    should remain inside the quotation, but they still satisfy the quoted
    mark for structural-audit purposes.
    """
    labels = set()
    opening = "<footnotemark>"
    closing = "</footnotemark>"
    for text in texts:
        candidate = text.lstrip(" \t\r\n\"'“‘")
        if not candidate.startswith(opening):
            continue
        end = candidate.find(closing, len(opening))
        if end == -1:
            continue
        label = candidate[len(opening) : end].strip()
        if label:
            labels.add(label)
    return labels


def _explicit_quote_opener(text: str) -> bool:
    """Whether a block visibly opens quoted material rather than ordinary prose."""
    candidate = (text or "").lstrip()
    if candidate.startswith("<pagenumber "):
        end = candidate.find("/>")
        if end != -1:
            candidate = candidate[end + 2 :].lstrip()
    return candidate.startswith(("\"", "'", "“", "‘", "§"))


def _looks_like_running_furniture(text: str) -> bool:
    plain = (
        text.replace("<strong>", "").replace("</strong>", "")
        .replace("<em>", "").replace("</em>", "").strip()
    )
    upper = plain.upper()
    if upper.startswith(("CASE NO.:", "CASE NOS.:", "APPEAL NO.:")):
        return True
    words = plain.split()
    if len(words) == 2 and words[0].lower() == "page":
        return True
    if len(words) <= 3 and plain.strip("-–— ").isdigit():
        return True
    return False


def _indented_runs(path: Path) -> int:
    """Candidate block quotes in the SOURCE: runs of ≥3 consecutive lines set
    in from the page's own modal body column and ending short of it. Used to
    tell 'this court truly has no quotes' from 'the extractor returned none'."""
    import pdfplumber

    runs = 0
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                lines = [
                    l
                    for l in page.extract_text_lines()
                    if l["top"] > 90 and (l["text"] or "").strip()
                ]
                if len(lines) < 5:
                    continue
                body_x0 = Counter(round(l["x0"]) for l in lines).most_common(1)[0][0]
                run = 0
                for l in lines:
                    if round(l["x0"]) >= body_x0 + 15:
                        run += 1
                    else:
                        runs += run >= 3
                        run = 0
                runs += run >= 3
    except Exception:
        return 0
    return runs


def _category(court: str, extractor) -> str:
    if court in FEDERAL_APPELLATE:
        return "federal appellate"
    if court in FEDERAL_SPECIAL:
        return "federal specialized/administrative"
    mro_names = {cls.__name__ for cls in type(extractor).mro()}
    if "DistrictBase" in mro_names:
        return "federal district"
    if court in TERRITORIAL:
        return "territorial/D.C./Puerto Rico"
    if court in STATE_AG:
        return "state attorney general"
    return "state court"


def inspect_pdf(task: tuple[str, str]) -> dict:
    court, path_string = task
    path = Path(path_string)
    result = FileResult(court=court, file=path.name)
    try:
        extractor = get_extractor(court)
        doc = extractor.extract(str(path))
        result.pages = doc.n_pages
        result.doc_type = doc.doc_type
        result.non_digital = doc.non_digital
        result.layout_ok = doc.layout_ok
        result.opinions = len(doc.opinions)
        result.warnings = list(doc.warnings)
        result.headmatter_footnotes = len(doc.headmatter_footnotes)
        # A certificate of judgment is an administrative record, deliberately
        # classified but not parsed into an opinion body. Keep its residual
        # text available for losslessness/review, but do not treat that
        # intentionally unstructured material as a parser-quality failure.
        if doc.doc_type != DocType.CERTIFICATE:
            result.residual_content = sum(
                1
                for item in doc.residual
                if isinstance(item, dict) and item.get("kind") == "content"
            )

        body_texts = []
        blockquote_texts = []
        footnote_labels = []
        empty_authors = 0
        empty_opinions = 0
        leaked_furniture = 0
        for opinion in doc.opinions:
            if not opinion.author.strip():
                empty_authors += 1
            if not opinion.blocks:
                empty_opinions += 1
            footnote_labels.extend(fn.label for fn in opinion.footnotes)
            result.footnotes += len(opinion.footnotes)
            for block in opinion.blocks:
                result.blocks += 1
                if block.kind == "p":
                    result.paragraphs += 1
                elif block.kind == "blockquote":
                    result.blockquotes += 1
                    blockquote_texts.append(block.text or "")
                elif block.kind == "heading":
                    result.headings += 1
                if block.text:
                    body_texts.append(block.text)
                    if _looks_like_running_furniture(block.text):
                        leaked_furniture += 1

        body = " ".join(body_texts)
        marks = set(_footnote_marks(body))
        returned = set(footnote_labels)
        returned.update(_quoted_footnote_definitions(body_texts))
        unknown = sorted(label for label in returned if label == "?")
        missing_note_labels = sorted(
            label for label in marks - returned if label.isdigit()
        )

        if not doc.layout_ok:
            result.flags.append("layout-mismatch")
        if doc.doc_type == DocType.UNKNOWN:
            result.flags.append("unknown-document-type")
        if (
            not doc.non_digital
            and doc.doc_type == DocType.OPINION
            and not doc.opinions
        ):
            result.flags.append("no-opinion-returned")
        if empty_opinions:
            result.flags.append(f"empty-opinion:{empty_opinions}")
        if empty_authors:
            result.flags.append(f"authorless-opinion:{empty_authors}")
        if result.residual_content:
            result.flags.append(f"unresolved-content:{result.residual_content}")
        if unknown:
            result.flags.append("unknown-footnote-label")
        if missing_note_labels:
            result.flags.append(
                "unreturned-footnote-marks:" + ",".join(missing_note_labels[:8])
            )
        if leaked_furniture:
            result.flags.append(f"running-furniture-in-body:{leaked_furniture}")
        prose = result.paragraphs + result.blockquotes
        explicit_quotes = sum(
            _explicit_quote_opener(text) for text in blockquote_texts
        )
        quote_evidence = (
            explicit_quotes / result.blockquotes if result.blockquotes else 0
        )
        if (
            prose >= 12
            and result.blockquotes / prose >= 0.55
            and quote_evidence < 0.5
        ):
            result.flags.append(
                f"blockquote-dominant:{result.blockquotes}/{prose}"
            )
        if result.opinions > 1 and empty_authors:
            result.flags.append("suspicious-multi-opinion")
        # The inverse of blockquote-dominant: the extractor returned NO quotes
        # while the source itself shows indented multi-line runs. mass/conn
        # class of miss — the segmenter never splits the quote out of its
        # surrounding body segment.
        if prose >= 30 and result.blockquotes == 0 and not doc.non_digital:
            candidate_runs = _indented_runs(path)
            if candidate_runs >= 3:
                result.flags.append(
                    f"no-blockquotes-despite-indented-runs:{candidate_runs}"
                )
        # Page provenance: a multi-page opinion whose body carries no
        # <pagenumber/> markers at all has lost its page mapping (the
        # calctapp defect, corpus-wide).
        if (
            result.pages >= 3
            and result.blocks >= 10
            and not doc.non_digital
            and not _inline_values(body, "pagenumber", "value")
        ):
            result.flags.append("no-page-markers")
        # Fragmentation: paragraphs averaging a couple of lines' worth of
        # words mean wrapped lines are not being joined — output that "looks
        # complete" but reads broken.
        if result.paragraphs >= 10:
            body_words = sum(len((t or "").split()) for t in body_texts)
            avg = body_words / max(1, result.paragraphs)
            if avg < 22:
                result.flags.append(f"fragmented-paragraphs:avg{avg:.0f}w")
        # Headmatter sanity on real opinions.
        if doc.doc_type == DocType.OPINION and not doc.non_digital:
            if not doc.summary:
                result.flags.append("empty-headmatter")
            if not (doc.docket_number or doc.decision_date):
                result.flags.append("no-docket-no-date")

        coverage = audit_coverage(doc, str(path), extractor=extractor)
        result.total_lines = coverage.total
        result.covered_lines = coverage.covered
        result.missing_lines = len(coverage.missing)
        if result.missing_lines:
            result.flags.append(f"missing-source-lines:{result.missing_lines}")
    except Exception as exc:
        result.error = f"{type(exc).__name__}: {exc}"
        result.flags.append("extraction-error")
    return asdict(result)


def _severity(flag: str) -> str:
    if flag.startswith(
        (
            "extraction-error", "missing-source-lines", "unresolved-content",
            "no-opinion-returned", "empty-opinion", "layout-mismatch",
        )
    ):
        return "confirmed"
    return "review"


def _court_status(court: str, rows: list[dict], registered: bool) -> str:
    if not registered:
        return "hard failure"
    if any(row["error"] for row in rows):
        return "hard failure"
    flags = [flag for row in rows for flag in row["flags"]]
    if any(
        flag.startswith(("missing-source-lines", "layout-mismatch"))
        for flag in flags
    ):
        return "hard failure"
    if any(
        flag.startswith(
            ("unresolved-content", "no-opinion-returned", "empty-opinion")
        )
        for flag in flags
    ):
        return "structural gaps detected"
    if len(rows) < 5:
        return "insufficient evidence"
    if flags or any(row["non_digital"] for row in rows):
        return "needs review"
    return "provisionally complete"


def _examples(rows: list[dict], flag: str, limit: int = 8) -> list[str]:
    return [row["file"] for row in rows if flag in row["flags"]][:limit]


def _court_markdown(
    court: str,
    rows: list[dict],
    registered: bool,
    category: str,
    note_exists: bool,
) -> str:
    status = _court_status(court, rows, registered)
    flags = Counter(flag for row in rows for flag in row["flags"])
    errors = [row for row in rows if row["error"]]
    scans = [row for row in rows if row["non_digital"]]
    types = Counter(row["doc_type"] or "(error)" for row in rows)
    total_lines = sum(row["total_lines"] for row in rows)
    covered = sum(row["covered_lines"] for row in rows)
    opinions = sum(row["opinions"] for row in rows)
    footnotes = sum(row["footnotes"] + row["headmatter_footnotes"] for row in rows)
    blocks = sum(row["blocks"] for row in rows)
    pct = 100.0 * covered / total_lines if total_lines else 100.0

    out = [
        f"# {court} ecosystem audit",
        "",
        f"- **Status:** {status}",
        f"- **Category:** {category}",
        f"- **Registered extractor:** {'yes' if registered else 'no'}",
        f"- **Fixtures audited:** {len(rows)}",
        f"- **Born-digital / scans:** {len(rows) - len(scans)} / {len(scans)}",
        f"- **Coverage:** {covered:,}/{total_lines:,} lines ({pct:.2f}%)",
        f"- **Returned opinions / blocks / footnotes:** "
        f"{opinions:,} / {blocks:,} / {footnotes:,}",
        f"- **Existing hand notes:** {'yes' if note_exists else 'no'}",
        "",
        "## Assessment",
        "",
    ]
    if not registered:
        out.append(
            "This corpus has no registered court-specific extractor. The CLI "
            "falls back to the generic parser, so it is not considered complete."
        )
    elif status == "provisionally complete":
        out.append(
            "No automated losslessness or structural warning was found in the "
            "available fixtures. This is provisional: visual review remains the "
            "authority for geometry and semantic grouping."
        )
    elif status == "insufficient evidence":
        out.append(
            "The available corpus is too small to establish template coverage. "
            "The listed files may parse cleanly, but more representative PDFs "
            "are required before calling the court complete."
        )
    elif status == "needs review":
        out.append(
            "All source text may be accounted for, but one or more structural "
            "signals require visual review. Coverage alone does not establish "
            "correct paragraph, opinion, footnote, or furniture placement."
        )
    elif status == "hard failure":
        out.append(
            "The automated run found an extraction exception, source-line loss, "
            "layout mismatch, or missing court registration. This is the highest "
            "priority class and should remain in the repair queue."
        )
    else:
        out.append(
            "The source text is generally retained, but at least one document "
            "left content in the safety-net residual bucket, returned no opinion, "
            "or returned an empty opinion. This proves a structural placement gap, "
            "not necessarily visible text loss; inspect the named fixtures."
        )

    out += ["", "## Document mix", ""]
    for kind, count in sorted(types.items()):
        out.append(f"- {kind}: {count}")

    out += ["", "## Findings", ""]
    if not flags and not errors and not scans:
        out.append("- No automated findings.")
    for flag, count in flags.most_common():
        files = _examples(rows, flag)
        suffix = f" Examples: {', '.join(f'`{name}`' for name in files)}." if files else ""
        out.append(f"- `{flag}`: {count} file(s).{suffix}")
    if scans:
        out.append(
            f"- `non-digital/scan`: {len(scans)} file(s). Examples: "
            + ", ".join(f"`{row['file']}`" for row in scans[:8])
            + "."
        )
    if errors:
        out += ["", "### Extraction errors", ""]
        for row in errors[:20]:
            out.append(f"- `{row['file']}` — {row['error']}")

    out += [
        "",
        "## Review guidance",
        "",
        "- Inspect every example named above against its PDF.",
        "- For blockquote warnings, compare left and right rails rather than "
        "assuming single spacing means quotation.",
        "- For authorless/multi-opinion warnings, distinguish unsigned orders "
        "from missed bylines and panel announcements.",
        "- For footnote warnings, compare every separator-bearing page and "
        "label sequence, including cross-page continuations.",
        "- For thin corpora, add recent, long, short, multi-opinion, and order "
        "forms before changing the status.",
        "",
        "## Per-file metrics",
        "",
        "| File | Pages | Type | Opinions | Footnotes | Coverage | Flags |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for row in rows:
        coverage = (
            f"{row['covered_lines']}/{row['total_lines']}"
            if not row["error"]
            else "error"
        )
        row_flags = ", ".join(row["flags"]) or (
            "non-digital" if row["non_digital"] else "—"
        )
        out.append(
            f"| `{row['file']}` | {row['pages']} | {row['doc_type'] or '—'} | "
            f"{row['opinions']} | {row['footnotes'] + row['headmatter_footnotes']} | "
            f"{coverage} | {row_flags} |"
        )
    return "\n".join(out) + "\n"


def generate_reports(
    assets: Path, output: Path, workers: int, courts: list[str] | None = None
) -> None:
    court_dirs = sorted(path for path in assets.iterdir() if path.is_dir())
    if courts:
        wanted = set(courts)
        court_dirs = [path for path in court_dirs if path.name in wanted]
    tasks = [
        (court_dir.name, str(pdf))
        for court_dir in court_dirs
        for pdf in sorted(court_dir.glob("*.pdf"))
    ]
    by_court: dict[str, list[dict]] = defaultdict(list)
    completed = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(inspect_pdf, task): task for task in tasks}
        for future in as_completed(future_map):
            row = future.result()
            by_court[row["court"]].append(row)
            completed += 1
            if completed % 100 == 0 or completed == len(tasks):
                print(f"audited {completed}/{len(tasks)} PDFs", flush=True)

    # Merge with any earlier run so a filtered re-doctor of one court can't
    # clobber the corpus-wide results.
    results_path = output / "results.json"
    files: dict[str, list[dict]] = {}
    if courts and results_path.exists():
        files = json.loads(results_path.read_text(encoding="utf-8"))["files"]
    for court_dir in court_dirs:
        files[court_dir.name] = sorted(
            by_court.get(court_dir.name, []), key=lambda row: row["file"]
        )
    output.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps({"courts": [], "files": files}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    render_saved_results(output)


def _write_indexes(output: Path, summaries: list[dict]) -> None:
    order = {
        "hard failure": 0,
        "structural gaps detected": 1,
        "needs review": 2,
        "insufficient evidence": 3,
        "provisionally complete": 4,
    }
    summaries.sort(key=lambda row: (order[row["status"]], row["court"]))
    counts = Counter(row["status"] for row in summaries)
    total_pdfs = sum(row["fixtures"] for row in summaries)
    total_lines = sum(row["coverage_total"] for row in summaries)
    kept_lines = sum(row["coverage_kept"] for row in summaries)
    pct = 100.0 * kept_lines / total_lines if total_lines else 100.0
    lines = [
        "# Centralia ecosystem audit",
        "",
        "This is an automated structural audit of every PDF currently present "
        "under `assets/`. It is deliberately stricter than line coverage and "
        "does not claim visual perfection.",
        "",
        "Status meanings: **hard failure** means an exception, source-line loss, "
        "layout mismatch, or absent court registration; **structural gaps "
        "detected** means text was retained but some content remained in the "
        "safety-net residual bucket or an expected opinion was empty/missing; "
        "**needs review** contains geometry/semantic warnings only. A clean result "
        "is provisional, never a substitute for comparing the HTML to the PDF.",
        "",
        "Start with the [prioritized review plan](PRIORITIES.md), or use the "
        "[state](state.md) and [federal](federal.md) indexes.",
        "",
        f"- Courts: {len(summaries)}",
        f"- PDFs: {total_pdfs:,}",
        f"- Coverage: {kept_lines:,}/{total_lines:,} lines ({pct:.2f}%)",
    ]
    for status in order:
        lines.append(f"- {status.title()}: {counts[status]}")
    lines += [
        "",
        "## Court status",
        "",
        "| Court | Category | Status | PDFs | Scans | Errors | Missing lines | Flags |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| [{row['court']}](courts/{row['court']}.md) | "
            f"{row['category']} | {row['status']} | {row['fixtures']} | "
            f"{row['scans']} | {row['errors']} | {row['missing']} | "
            f"{row['flags']} |"
        )
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for family in ("state", "federal"):
        selected = [
            row
            for row in summaries
            if (row["category"].startswith("state")) == (family == "state")
            and (
                family == "state"
                or row["category"].startswith("federal")
            )
        ]
        family_lines = [
            f"# {family.title()} court audit",
            "",
            f"{len(selected)} court corpora.",
            "",
            "| Court | Category | Status | PDFs | Findings |",
            "|---|---|---|---:|---:|",
        ]
        for row in selected:
            family_lines.append(
                f"| [{row['court']}](courts/{row['court']}.md) | "
                f"{row['category']} | {row['status']} | {row['fixtures']} | "
                f"{row['flags']} |"
            )
        (output / f"{family}.md").write_text(
            "\n".join(family_lines) + "\n", encoding="utf-8"
        )


def render_saved_results(output: Path) -> None:
    """Re-render Markdown after report-language changes without re-extracting."""
    payload = json.loads((output / "results.json").read_text(encoding="utf-8"))
    by_court = payload["files"]
    summaries = []
    court_output = output / "courts"
    court_output.mkdir(parents=True, exist_ok=True)
    for court in sorted(by_court):
        rows = sorted(by_court[court], key=lambda row: row["file"])
        registered = court in EXTRACTORS
        category = _category(court, get_extractor(court))
        status = _court_status(court, rows, registered)
        (court_output / f"{court}.md").write_text(
            _court_markdown(
                court,
                rows,
                registered,
                category,
                (Path("output/notes") / f"{court}.md").exists(),
            ),
            encoding="utf-8",
        )
        summaries.append(
            {
                "court": court,
                "category": category,
                "status": status,
                "fixtures": len(rows),
                "scans": sum(row["non_digital"] for row in rows),
                "errors": sum(bool(row["error"]) for row in rows),
                "missing": sum(row["missing_lines"] for row in rows),
                "flags": sum(len(row["flags"]) for row in rows),
                "coverage_total": sum(row["total_lines"] for row in rows),
                "coverage_kept": sum(row["covered_lines"] for row in rows),
            }
        )
    payload["courts"] = summaries
    (output / "results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _write_indexes(output, summaries)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", default="assets")
    parser.add_argument("--output", default="output/ecosystem-audit")
    parser.add_argument(
        "--workers", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1))
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="re-render Markdown from an existing results.json",
    )
    parser.add_argument(
        "courts",
        nargs="*",
        help="limit the run to these court ids (results merge into the "
        "existing corpus-wide report)",
    )
    args = parser.parse_args(argv)
    if args.render_only:
        render_saved_results(Path(args.output))
    else:
        generate_reports(
            Path(args.assets), Path(args.output), args.workers, args.courts or None
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
