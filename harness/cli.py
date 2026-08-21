"""On-demand harness CLI. Nothing here runs automatically — ever.

    python harness/cli.py freeze <court> [--force]   freeze old-system baseline
    python harness/cli.py truth [<court>]            truth-set statistics
    python harness/cli.py identity <court>           old-vs-old compare (must be clean)
    python harness/cli.py lines <court/stem> [-p N] [--rules]   the PDF lens
    python harness/cli.py notes [<court>...] [--json] [--open]   per-file notes

Added in later phases: extract / render / check / census / compare / trace / serve.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def cmd_freeze(args: list[str]) -> int:
    import baseline
    force = "--force" in args
    courts = [a for a in args if not a.startswith("-")]
    for court in courts:
        out = baseline.freeze(court, force=force)
        print(f"baseline: {out}")
    return 0


def cmd_truth(args: list[str]) -> int:
    import truth
    ft = truth.footnote_truth()
    if args:
        court = args[0]
        mine = truth.footnote_truth_for(court)
        print(f"{court}: {len(mine)} footnote-truth files")
        cm = truth.criteria_manifest()
        print(f"{court}: {len(cm.get(court, []))} criteria-manifest stems")
    else:
        courts = {k.split("/")[0] for k in ft}
        print(f"footnote truth: {len(ft)} files across {len(courts)} courts")
        cf = truth.criteria_fixtures()
        print(f"criteria fixtures: {len(cf)} snapshots")
    return 0


def cmd_identity(args: list[str]) -> int:
    """Sanity: compare a frozen baseline against itself; must be clean."""
    import baseline
    import compare
    court = args[0]
    files = baseline.load(court)["files"]
    result = compare.compare_courts(court, files, files)
    status = "clean" if result.clean else f"{len(result.diffs)} DIFFS (bug in compare)"
    print(f"identity {court}: {result.files_compared} files, {status}")
    return 0 if result.clean else 1


def cmd_lines(args: list[str]) -> int:
    """The PDF lens: per-line top/x0/x1/size/bold/col + drawn rules + events."""
    from centralia import geometry
    from centralia.pdfio import build_pdf
    from centralia.settings import resolve_pdf

    name = args[0]
    pages = None
    if "-p" in args:
        spec = args[args.index("-p") + 1]
        if "-" in spec:
            a, b = spec.split("-")
            pages = set(range(int(a), int(b) + 1))
        else:
            pages = {int(spec)}
    pdf = resolve_pdf(name)
    if pdf is None:
        print(f"cannot resolve {name!r}")
        return 1
    model = build_pdf(str(pdf))
    geom = geometry.measure(model)
    print(f"{pdf} — {model.n_pages} pages | geom: {geom}")
    for pm in model.pages:
        if pages and pm.number not in pages:
            continue
        print(f"\n== page {pm.number} ({pm.width:.0f}x{pm.height:.0f}) "
              f"ink={pm.ink_chars} cid={pm.cid_chars} img={pm.image_area:.2f}")
        if "--rules" in args:
            for r in pm.h_rules:
                print(f"  H top={r.top:7.1f} x={r.x0:6.1f}-{r.x1:6.1f} "
                      f"w={r.width:6.1f} {r.source} strokes={r.strokes}")
            for v in pm.v_rules:
                print(f"  V x={v.x:7.1f} y={v.top:6.1f}-{v.bottom:6.1f} "
                      f"h={v.height:6.1f} {v.source} strokes={v.strokes}")
        for l in pm.lines:
            align = geometry.line_alignment(l, pm.width, geom)
            flags = f"{'B' if l.bold else ' '}{align}{l.col or ' '}"
            print(f"  {l.top:7.1f} {l.x0:6.1f}-{l.x1:6.1f} {l.size:4.1f} "
                  f"{flags} {l.plain[:80]!r}")
        for quirk, detail in pm.events:
            print(f"  * {quirk}: {detail}")
    return 0


def cmd_footnotes(args: list[str]) -> int:
    """Validate footnote labels against the 2,124-file truth set.
    Usage: footnotes <court...> [--misses N]"""
    import truth as truth_mod
    from centralia import geometry
    from centralia.classify import triage
    from centralia.pdfio import build_pdf
    from centralia.resolve.evidence import Trace
    from centralia.resolve.footnotes import (FootnoteConfig, canon_label,
                                             document_labels)
    from centralia.settings import CORPUS_ROOT

    show = int(args[args.index("--misses") + 1]) if "--misses" in args else 3
    courts = [a for a in args if not a.startswith("-")
              and not a.isdigit()]
    # Court facts come from the profiles — the single declaration site.
    from centralia.courts import get_profile
    ft = truth_mod.footnote_truth()
    grand_ok = grand_total = 0
    for court in courts:
        keys = sorted(k for k in ft if k.startswith(court + "/"))
        ok = skip = err = 0
        misses = []
        for k in keys:
            stem = k.split("/", 1)[1]
            pdf = CORPUS_ROOT / court / f"{stem}.pdf"
            if not pdf.exists():
                skip += 1
                continue
            try:
                m = build_pdf(str(pdf))
                if triage(m):
                    got = []   # a scan yields no labels; truth should be []
                else:
                    cfg = get_profile(court).footnotes
                    got = document_labels(m, geometry.measure(m),
                                          cfg, court, Trace())
            except Exception as e:  # noqa: BLE001
                err += 1
                misses.append((stem, "ERROR", str(e)[:70]))
                continue
            want = [canon_label(x) for x in ft[k]]
            got = [canon_label(x) for x in got]
            if got == want:
                ok += 1
            else:
                misses.append((stem, want, got))
        total = len(keys) - skip
        grand_ok += ok
        grand_total += total
        rate = f"{ok}/{total}" if total else "n/a"
        print(f"{court:12s} {rate:9s} skip={skip} err={err}")
        for stem, want, got in misses[:show]:
            print(f"    {stem[:44]}")
            print(f"      want {want if isinstance(want, str) else want[:12]}")
            print(f"      got  {got if isinstance(got, str) else got[:12]}")
    if grand_total:
        print(f"TOTAL {grand_ok}/{grand_total} "
              f"({100.0 * grand_ok / grand_total:.1f}%)")
    return 0


def cmd_compare(args: list[str]) -> int:
    """A/B a court against its frozen old-system baseline.
    Usage: compare <court> [--limit N]"""
    import baseline
    import compare as cmp
    from centralia.pipeline import extract
    from centralia.settings import CORPUS_ROOT

    court = args[0]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    base = baseline.load(court)["files"]
    stems = sorted(base)[:limit] if limit else sorted(base)
    new_files = {}
    errors = {}
    for stem in stems:
        pdf = CORPUS_ROOT / court / f"{stem}.pdf"
        if not pdf.exists():
            continue
        try:
            new_files[stem] = cmp.new_record(extract(str(pdf), court))
        except Exception as e:  # noqa: BLE001
            errors[stem] = repr(e)
    result = cmp.compare_courts(court, {s: base[s] for s in stems}, new_files)
    print(f"{court}: {result.files_compared} compared, "
          f"{len(result.diffs)} diffs, {len(errors)} errors")
    from collections import Counter
    print("  by kind:", dict(Counter(d.kind for d in result.diffs)))
    for d in result.diffs[:15]:
        print(f"  {d.stem[:40]:42s} {d.kind:15s} {d.detail[:70]}")
    for s, e in list(errors.items())[:5]:
        print(f"  ERROR {s[:40]}: {e[:80]}")
    return 0


def cmd_extract(args: list[str]) -> int:
    """Extract one file and render review HTML.

    Usage: extract <court/stem> [--xml]
           extract /any/path/file.pdf --court ca9 [--xml]

    A file outside the corpus has no court id in its path, and without one the
    court's own reader never fires — the record comes back on core's generic
    walk, which is a different (and worse) reading. `--court` names it.
    """
    from centralia.pipeline import extract
    from centralia.render import render_casebody, render_html
    from centralia.settings import OUTPUT_DIR, resolve_pdf

    court = None
    if "--court" in args:
        _i = args.index("--court")
        if _i + 1 >= len(args):
            print("--court needs a court id (e.g. --court ca9)")
            return 1
        court = args[_i + 1]
        args = args[:_i] + args[_i + 2:]
    if not args:
        print("usage: extract <court/stem | path.pdf> [--court ID] [--xml]")
        return 1
    name = args[0]
    if court is None:
        court = name.split("/")[0] if "/" in name else "unknown"
        if court == "unknown":
            print("note: no court id given; using core's generic reader. "
                  "Pass --court <id> to use the court's own.")
    pdf = resolve_pdf(name)
    if pdf is None:
        print(f"cannot resolve {name!r}")
        return 1
    result = extract(str(pdf), court)
    doc = result.document
    out_dir = OUTPUT_DIR / court
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{pdf.stem}.html"
    out.write_text(render_html(doc))
    print(f"{result.status} | {doc.meta.doc_type} | "
          f"{len(doc.opinions)} opinions | -> {out}")
    print(f"  open it:  open {out}")
    if "--xml" in args:
        x = out_dir / f"{pdf.stem}.xml"
        x.write_text(render_casebody(doc))
        print(f"casebody -> {x}")
    for decision in result.trace.decisions:
        if decision.value is not None:
            print(f"  {decision.point}: {decision.fired}")
    return 0


def cmd_render(args: list[str]) -> int:
    """Render review HTML. Usage: render <court...> [--limit N]"""
    from centralia.pipeline import extract
    from centralia.render import render_html
    from centralia.settings import OUTPUT_DIR, court_pdfs

    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    only = args[args.index("--only") + 1] if "--only" in args else None
    courts = [a for a in args if not a.startswith("-")
              and not a.isdigit() and a != only]
    # RENDERING NOTHING IS NOT SUCCESS. `render` with no court printed the
    # usual summary and exited 0 having touched no file, which reads exactly
    # like a completed corpus re-render — a fix was reported as applied
    # corpus-wide when nothing had been rewritten.
    if not courts:
        print("render: name at least one court "
              "(e.g. `render ca3`, or `render $(ls output)`)")
        return 2
    for court in courts:
        out_dir = OUTPUT_DIR / court
        out_dir.mkdir(parents=True, exist_ok=True)
        pdfs = court_pdfs(court)
        if only:
            pdfs = [p for p in pdfs if p.stem == only]
        if limit:
            pdfs = pdfs[:limit]
        counts = {"valid": 0, "scanned": 0, "review": 0,
                  "failed": 0, "error": 0}
        for pdf in pdfs:
            try:
                result = extract(str(pdf), court)
                (out_dir / f"{pdf.stem}.html").write_text(
                    render_html(result.document))
                counts[result.status] += 1
            except Exception as e:  # noqa: BLE001
                counts["error"] += 1
                print(f"  ERROR {pdf.stem[:50]}: {e!r}")
        print(f"{court}: {counts}", flush=True)
    return 0


def cmd_fngaps(args: list[str]) -> int:
    """Footnote-integrity census: per court, count (a) numeric SEQUENCE GAPS
    within a writing, (b) UNRETURNED body marks (<footnotemark>N with no
    note N), (c) '?' notes (text without a label).
    Usage: fngaps <court...> [--files]"""
    import re
    from centralia.pipeline import extract
    from centralia.settings import court_pdfs

    show_files = "--files" in args
    courts = [a for a in args if not a.startswith("-")]
    mark_re = re.compile(r"<footnotemark>([^<]+)</footnotemark>")
    for court in courts:
        gaps = unreturned = unknown = affected = 0
        rows = []
        for pdf in court_pdfs(court):
            r = extract(str(pdf), court)
            doc = r.document
            f_gaps, f_unret, f_unk = [], [], 0
            for op in doc.opinions:
                labels = [f.label for f in op.footnotes]
                f_unk += sum(1 for lab in labels if lab == "?")
                nums = [int(x) for x in labels if x.isdigit()]
                if nums:
                    missing = sorted(set(range(min(nums), max(nums) + 1))
                                     - set(nums))
                    f_gaps += missing
                have = set(labels)
                marks = [m for b in op.blocks
                         for m in mark_re.findall(getattr(b, "text", ""))]
                f_unret += [m for m in dict.fromkeys(marks) if m not in have]
            if f_gaps or f_unret or f_unk:
                affected += 1
                gaps += len(f_gaps)
                unreturned += len(f_unret)
                unknown += f_unk
                if show_files and len(rows) < 8:
                    rows.append(f"    {pdf.stem[:44]:46s} gaps={f_gaps[:6]} "
                                f"unreturned={f_unret[:6]} ?={f_unk}")
        print(f"{court:7s} affected_files={affected:3d} seq_gaps={gaps:3d} "
              f"unreturned_marks={unreturned:3d} unlabeled={unknown:3d}")
        for row in rows:
            print(row)
    return 0


def cmd_audit(args: list[str]) -> int:
    """The two-axis audit: FOOTNOTE INTEGRITY (sequence gaps, unreturned
    body marks, '?' notes) and OPINION MATCHING (count vs frozen baseline,
    authorless writings, empty docs). Writes output/notes/_audit.md.
    Usage: audit <court...>"""
    import re
    import baseline as baseline_mod
    from centralia.pipeline import extract
    from centralia.settings import CORPUS_ROOT, OUTPUT_DIR, court_pdfs

    mark_re = re.compile(r"<footnotemark>([^<]+)</footnotemark>")
    courts = [a for a in args if not a.startswith("-")]
    lines_out = ["# Footnote & opinion-matching audit", ""]
    grand = {"files": 0, "fn_gap_files": 0, "unret_files": 0, "unk_files": 0,
             "op_mismatch": 0, "authorless": 0, "no_ops": 0}
    for court in courts:
        try:
            base = baseline_mod.load(court)["files"]
        except FileNotFoundError:
            base = {}
        rows = []
        for pdf in court_pdfs(court):
            r = extract(str(pdf), court)
            doc = r.document
            grand["files"] += 1
            issues = []
            # --- footnotes ---
            gaps, unret, unk = [], [], 0
            all_labels = set()
            for op in doc.opinions:
                labels = [f.label for f in op.footnotes]
                all_labels.update(labels)
                unk += sum(1 for lab in labels if lab == "?")
                nums = [int(x) for x in labels if x.isdigit()]
                if nums:
                    gaps += sorted(set(range(min(nums), max(nums) + 1))
                                   - set(nums))
            all_labels.update(f.label for f in doc.headmatter_footnotes)
            marks = [m for op in doc.opinions for b in op.blocks
                     for m in mark_re.findall(getattr(b, "text", ""))]
            unret = [m for m in dict.fromkeys(marks) if m not in all_labels]
            if gaps:
                grand["fn_gap_files"] += 1
                issues.append(f"fn-gaps {gaps[:8]}")
            if unret:
                grand["unret_files"] += 1
                issues.append(f"unreturned {unret[:8]}")
            if unk:
                grand["unk_files"] += 1
                issues.append(f"?-notes {unk}")
            # --- opinion matching ---
            old_rec = base.get(pdf.stem)
            n_new = len(doc.opinions)
            if old_rec is not None:
                n_old = len(old_rec.get("opinions", []))
                if n_new != n_old:
                    grand["op_mismatch"] += 1
                    olds = [(o.get("type"), (o.get("author") or "")[:24])
                            for o in old_rec.get("opinions", [])]
                    news = [(o.type, o.author[:24]) for o in doc.opinions]
                    issues.append(f"ops {n_old}->{n_new} old={olds} new={news}")
            authorless = [o for o in doc.opinions
                          if not o.author and o.type not in ("order",)]
            if authorless:
                grand["authorless"] += 1
                issues.append(f"authorless×{len(authorless)}")
            if (not doc.opinions
                    and str(doc.meta.doc_type) not in
                    ("scan", "notice", "filing", "certificate-of-judgment",
                     "judgment")):
                grand["no_ops"] += 1
                issues.append("NO OPINIONS")
            if issues:
                rows.append((pdf.stem, issues))
        lines_out.append(f"## {court} — {len(rows)} flagged")
        for stem, issues in rows:
            lines_out.append(f"- `{stem[:60]}`: " + "; ".join(issues))
        lines_out.append("")
        print(f"{court:7s} flagged={len(rows)}")
    report = OUTPUT_DIR / "notes" / "_audit.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    summary = (f"\nTOTALS: files={grand['files']} fn-gap files="
               f"{grand['fn_gap_files']} unreturned={grand['unret_files']} "
               f"?-notes={grand['unk_files']} op-count-mismatch="
               f"{grand['op_mismatch']} authorless={grand['authorless']} "
               f"no-opinions={grand['no_ops']}")
    lines_out.append(summary)
    report.write_text("\n".join(lines_out))
    print(summary)
    print(f"report -> {report}")
    return 0


def cmd_serve(args: list[str]) -> int:
    import viewer
    viewer.serve(int(args[0]) if args else 8002)
    return 0


def cmd_quality(args: list[str]) -> int:
    """Grade rendered output quality per file/court from mechanical signals.
    Usage: quality [court...]   (no args = whole corpus; writes
    output/notes/quality.json, served to the viewer at /api/quality)"""
    import quality
    return quality.main(args)


def cmd_v1diff(args: list[str]) -> int:
    """Diff v2 against the frozen v1 baselines; writes docs/v1-diff.md.
    Usage: v1diff [court...]"""
    import v1diff
    return v1diff.main(args)


def cmd_guard(args: list[str]) -> int:
    """Structural regression guard over the pinned sentinel files.
    Usage: guard [court...] | guard --bless | guard --add <court/stem>"""
    import guard
    return guard.main(args)


def cmd_coverage(args: list[str]) -> int:
    """Content-loss reconciliation vs the PDF text layer (pdftotext oracle).
    Usage: coverage [court...] [--floor 0.985]"""
    import coverage
    return coverage.main(args)


def cmd_notes(args: list[str]) -> int:
    """THE REVIEWER'S OWN WORDS, per file — the work list a mark cannot carry.

    Usage: notes [court...] [--json] [--open]

    A note says WHAT is wrong with a rendering; the mark says how bad. EVERY
    note is listed by default, each with its file's current mark: a note is
    hand labour, and hiding it because the mark has since gone to `yay` is
    how the sentence gets lost — a `yay` beside a note is exactly how you
    tell one that was ACTED ON from one that never was. `--open` narrows to
    the files still short of `yay`, which is the work list.
    """
    import json as _json
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import viewer  # noqa: PLC0415

    notes = viewer._load_notes()
    marks = viewer._load_marks()
    stale = viewer._stale_marks()
    qual = {}
    qpath = viewer.OUTPUT_DIR / "notes" / "quality.json"
    if qpath.exists():
        try:
            qual = _json.loads(qpath.read_text()).get("files", {})
        except Exception:  # noqa: BLE001
            qual = {}

    courts = [a for a in args if not a.startswith("-")]
    keys = sorted(k for k in notes
                  if (not courts or k.split("/")[0] in courts)
                  and ("--open" not in args or marks.get(k) != "yay"))
    if "--json" in args:
        print(_json.dumps([{"key": k, "note": notes[k],
                            "mark": marks.get(k),
                            "grade": (qual.get(k) or {}).get("g"),
                            "flags": (qual.get(k) or {}).get("f") or [],
                            "stale": stale.get(k)}
                           for k in keys], indent=1))
        return 0
    if not keys:
        print("no notes" + (" still open (drop --open to see all)"
                            if notes else ""))
        return 0
    court = None
    for k in keys:
        c = k.split("/")[0]
        if c != court:
            court = c
            n_all = sum(1 for x in notes if x.startswith(c + "/"))
            print(f"\n== {court}  ({n_all} noted)")
        q = qual.get(k) or {}
        bits = [f"[{marks.get(k) or '—'}]"]
        if q.get("g"):
            bits.append(q["g"] + (f" ({', '.join(q['f'])})" if q.get("f") else ""))
        if stale.get(k):
            bits.append(f"stale:{stale[k]}")
        print(f"  {k.split('/', 1)[1]}")
        print(f"      {' · '.join(bits)}")
        for line in notes[k].splitlines():
            print(f"      | {line}")
    print(f"\n{len(keys)} noted file(s)")
    return 0


COMMANDS = {"freeze": cmd_freeze, "truth": cmd_truth, "identity": cmd_identity,
            "lines": cmd_lines, "serve": cmd_serve, "footnotes": cmd_footnotes,
            "compare": cmd_compare, "extract": cmd_extract,
            "render": cmd_render, "fngaps": cmd_fngaps, "audit": cmd_audit,
            "quality": cmd_quality, "coverage": cmd_coverage,
            "guard": cmd_guard, "v1diff": cmd_v1diff,
            "notes": cmd_notes}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


def cmd_released(args: list[str]) -> int:
    """Which courts the public API will read, regenerated from the marks.

    Usage: released            # report
           released --write    # regenerate centralia/released.py
    A court is released when every record in its corpus directory has been
    reviewed and none is marked bad — the reviewer's judgement, which no
    mechanical grade substitutes for.
    """
    import datetime
    import glob
    import json
    import os

    from centralia.settings import CORPUS_ROOT, MARKS_DIR

    with open(MARKS_DIR / "marks.json") as fh:
        marks = json.load(fh)
    courts = sorted(os.path.basename(d) for d in glob.glob(str(CORPUS_ROOT / "*"))
                    if os.path.isdir(d))
    ready, held = [], {}
    for c in courts:
        n = len(glob.glob(str(CORPUS_ROOT / c / "*.pdf")))
        mk = {k: v for k, v in marks.items() if k.startswith(c + "/")}
        bad = sum(1 for v in mk.values() if v == "nay")
        if n and len(mk) >= n and bad == 0:
            ready.append(c)
        else:
            held[c] = (n, len(mk), bad)
    print(f"released {len(ready)} / held back {len(held)} of {len(courts)} courts")
    if "--write" not in args:
        for c, (n, seen, bad) in sorted(held.items(),
                                        key=lambda kv: -kv[1][2])[:15]:
            print(f"  held  {c:16s} {seen}/{n} reviewed, {bad} marked bad")
        print("\n(--write to regenerate centralia/released.py)")
        return 0
    out = [
        '"""Which courts are RELEASED through the public API — generated, '
        'not typed.\n',
        "Generated by `harness.cli released --write` from the reviewer's own\n"
        "marks: a court is released when EVERY record in its corpus directory\n"
        "has been reviewed and NONE is marked bad. That is a human judgement\n"
        "about whether the reading is right, which no grade here stands in for\n"
        "— `quality` measures mechanical signals and `status` only says that\n"
        "nothing went unaccounted for.\n",
        f"As of {datetime.date.today().isoformat()}: {len(ready)} released, "
        f"{len(held)} held back (of {len(courts)} courts).\n",
        "The extractor is NOT gated: `extract`, `render`, the guard and the\n"
        'viewer read every court. This gates `centralia.read` only.\n"""\n',
        "from __future__ import annotations\n",
        "RELEASED: frozenset[str] = frozenset({",
    ]
    out += [f'    "{c}",' for c in ready]
    out += ["})\n",
            "# court -> (records, reviewed, marked bad) for those held back.",
            "HELD_BACK: dict[str, tuple[int, int, int]] = {"]
    out += [f'    "{c}": ({n}, {seen}, {bad}),'
            for c, (n, seen, bad) in sorted(held.items())]
    out += ["}\n"]
    path = REPO_ROOT / "centralia" / "released.py"
    path.write_text("\n".join(out))
    print(f"wrote {path}")
    return 0


# Registered after its definition — `COMMANDS` above is built before this
# function exists, and the `__main__` guard must come last of all or a command
# added below it is never reachable when the module is run as a script.
COMMANDS["released"] = cmd_released


if __name__ == "__main__":
    raise SystemExit(main())
