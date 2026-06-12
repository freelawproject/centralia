"""Command-line entry: PDF + court id -> extracted document.

    python -m restatement.cli <court_id> <path/to.pdf>          # criteria summary
    python -m restatement.cli <court_id> <path/to.pdf> --xml    # casebody XML
    python -m restatement.cli <court_id> <path/to.pdf> --html   # PDF + extraction
    python -m restatement.cli <court_id> <path/to.pdf> --json   # JSON criteria

The HTML view shows the source PDF and the extracted content side by side
for review. Add --output to write to output/<court_id>/<name>.<ext>,
--beside to write next to the source PDF, or -o/--out PATH for an explicit
path; otherwise output goes to stdout.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

from .audit import audit_coverage, format_report
from .registry import get_extractor
from .render import fingerprint, render_casebody, render_html, render_index


def _summary(doc) -> str:
    lines = [
        f"court:       {doc.court_id}  ({doc.court_label})",
        f"doc_type:    {doc.doc_type}",
        f"pages:       {doc.n_pages}",
        f"date filed:  {doc.decision_date}",
        f"docket:      {doc.docket_number}",
        f"panel:       {', '.join(doc.panel) or '-'}",
        f"disposition: {doc.disposition or '-'}",
        f"parties:     {len(doc.parties)} line(s)",
    ]
    for p in doc.parties:
        lines.append(f"  - {p}")
    lines.append(f"opinions:    {len(doc.opinions)} (in document order)")
    for i, op in enumerate(doc.opinions, 1):
        nblocks = len(op.blocks)
        nfn = len(op.footnotes)
        lines.append(
            f"  {i}. type={op.type}  author={op.author!r}  "
            f"blocks={nblocks} footnotes={nfn}"
        )
    if doc.headmatter_footnotes:
        lines.append(f"headmatter footnotes: {len(doc.headmatter_footnotes)}")
    if doc.warnings:
        lines.append("warnings:")
        for w in doc.warnings:
            lines.append(f"  ! {w}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="restatement")
    ap.add_argument("court_id")
    ap.add_argument("pdf_path")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--xml", action="store_true", help="emit casebody XML")
    g.add_argument(
        "--html",
        action="store_true",
        help="emit readable HTML (source PDF + extraction, " "side by side)",
    )
    g.add_argument("--json", action="store_true", help="emit JSON criteria")
    w = ap.add_mutually_exclusive_group()
    w.add_argument(
        "--output",
        nargs="?",
        const="output",
        metavar="DIR",
        help="write to DIR/<court_id>/<name>.<ext> (DIR defaults "
        "to 'output'); works for any format",
    )
    w.add_argument(
        "--beside",
        action="store_true",
        help="write next to the source PDF instead of stdout",
    )
    w.add_argument(
        "-o", "--out", metavar="PATH", help="write output to PATH instead of stdout"
    )
    ap.add_argument(
        "--index",
        action="store_true",
        help="in batch (--html --output) mode, also write an "
        "index.html grouping cases by type",
    )
    ap.add_argument(
        "--audit",
        action="store_true",
        help="completeness check: report any source-PDF line not "
        "accounted for anywhere in the extraction",
    )
    args = ap.parse_args(argv)

    extractor = get_extractor(args.court_id)

    src = Path(args.pdf_path)
    if src.is_dir():
        pdfs = sorted(src.glob("*.pdf"))
        if not pdfs:
            ap.error(f"no PDFs found in {src}")
        if not (args.output or args.beside or args.audit):
            ap.error("batch mode (a directory) needs --output, --beside, " "or --audit")
    else:
        pdfs = [src]

    if args.index and not (args.html and args.output):
        ap.error("--index requires --html and --output")

    if args.audit:
        tot = cov = 0
        for pdf in pdfs:
            try:
                r = audit_coverage(
                    extractor.extract(str(pdf)), str(pdf), extractor=extractor
                )
            except Exception as e:
                print(f"!! {pdf.name}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            tot += r.total
            cov += r.covered
            print(format_report(pdf.name, r, limit=8 if len(pdfs) > 1 else 60))
        if len(pdfs) > 1:
            pct = (100.0 * cov / tot) if tot else 100.0
            print(f"\nTOTAL: {cov}/{tot} lines accounted for ({pct:.1f}%)")
        return

    ext = _ext(args)
    entries = []
    n_ok = n_err = 0
    for pdf in pdfs:
        out_path = _dest(pdf, ext, args)
        try:
            doc = extractor.extract(str(pdf))
            text = _render(doc, args, pdf, out_path)
        except Exception as e:  # keep the batch going; report at the end
            n_err += 1
            print(f"!! {pdf.name}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        if out_path is not None:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
            n_ok += 1
            if args.index:
                entries.append(
                    {
                        "name": " ".join(doc.parties).strip() or pdf.stem,
                        "href": f"{pdf.stem}.html",
                        "fingerprint": fingerprint(doc),
                        "types": [op.type for op in doc.opinions],
                        "n_pages": doc.n_pages,
                        "doc_type": doc.doc_type,
                    }
                )
            if len(pdfs) == 1:
                print(f"wrote {out_path}")
        else:
            print(text)

    if args.index and entries:
        idx = Path(args.output) / args.court_id / "index.html"
        idx.write_text(
            render_index(args.court_id, extractor.court_label, entries),
            encoding="utf-8",
        )
        print(f"wrote {idx}")
    if len(pdfs) > 1:
        print(
            f"done: {n_ok} written, {n_err} failed -> "
            f"{args.output or 'beside source'}"
        )


def _ext(args) -> str:
    if args.xml:
        return "xml"
    if args.html:
        return "html"
    if args.json:
        return "json"
    return "txt"


def _render(doc, args, pdf: Path, out_path) -> str:
    if args.xml:
        return render_casebody(doc)
    if args.html:
        return render_html(doc, pdf_src=_relative_pdf(pdf, out_path))
    if args.json:
        return json.dumps(dataclasses.asdict(doc), indent=2, ensure_ascii=False)
    return _summary(doc)


def _relative_pdf(pdf: Path, out_path) -> str | None:
    """Path to ``pdf`` relative to the HTML's directory, so the iframe resolves
    when served/previewed. None (-> absolute file:// fallback) for stdout."""
    if out_path is None:
        return None
    try:
        return os.path.relpath(pdf.resolve(), Path(out_path).resolve().parent)
    except (ValueError, OSError):
        return None


def _dest(pdf: Path, ext: str, args):
    if args.out:
        return Path(args.out)
    if args.output:
        return Path(args.output) / args.court_id / f"{pdf.stem}.{ext}"
    if args.beside:
        return pdf.with_name(f"{pdf.stem}.{ext}")
    return None


if __name__ == "__main__":
    sys.exit(main())
