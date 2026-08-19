# Session state 2026-08-20 — restart point

Written mid-session because the user was switching networks. If the session
died, this is what to pick up.

## Committed (safe)

- `f282e37` **vt and wyo go live.** vt.py was written but never imported —
  inert outside its author's driver (867/867 rows once wired). wyo.py asked
  for `crit['docket_number']` one line ABOVE the `walk.finish()` that fills
  it, so all 50 files were refused by a correct 592-line reader:
  0/1232 -> 1204/1232. tenn came along at 1298/1302.
- `03e8652` **ill citation fix + ariz/ill/kan locked.** `2025 IL 130862` was
  role `docket`; now `citation`, with `docket='130862'`,
  `other=['130863']` on all 50. ariz/ill/kan marked complete in
  `output/notes/court_status.json` and pinned in `tests/fixtures/guard.json`.

## The state-supreme question, settled

Only **utah and wis** were genuinely unported. `colo`, `ny` and `okla` have
NO CORPUS AT ALL (Colorado has only coloctapp; New York has nyed/nysd/
nysupct/etc. but no `ny`; Oklahoma is absent) — nothing to port there. Do not
re-derive this.

## arizctapp is deliberately NOT complete

Guard showed 11 red sentinels on ariz+arizctapp. TEN are `opN_blocks` roughly
halving (129->67, 281->149, 220->109 …) with ops/hm/criteria/attorneys/
summary/syllabus/residual/status all holding — paragraph re-uniting,
representation-only, already re-signed. The ELEVENTH is real and is queued as
**core-patch-queue item 18**: `arizctapp/cervantes_v._state` lost a writing
(`H O W E, Chief Judge, specially concurring:` swallowed by Thumma's
majority, which now contains 'My concurrence'). Its pin is left FAILING on
purpose as a standing alarm — do not bless it.

## Eight agents were in flight (one court file each)

| court | task | file state at snapshot |
|---|---|---|
| utah | port from scratch (`parties` family, exemplar ala.py) | **utah.py present, 827 lines, wired** |
| wis  | port from scratch (`parties` family, exemplar ala.py)  | **wis.py present, 573 lines, wired** |
| va   | flat interleaved caption -> two-column CaptionBlock    | va.py modified |
| conn | second branch: CONNECTICUT LAW JOURNAL bound-reporter format (12 files at 0 rows, all `_1`/`_2` suffixes) | conn.py modified |
| ri   | trailing OPINION COVER SHEET -> endmatter (36 of 50 files, 0 currently reach it) | not yet modified |
| dc   | in_re_kester page-2 margin docket welded into prose; in_re_correa over-split into 3 writings | not yet modified |
| wash | reprinted stamp+caption leaking into the previous opinion's body (a_better_richland, schoenhals; +EN BANC on eyman_v._hobbs, mclellan_v._brown) | not yet modified |
| haw  | ORDER title + `(By: …)` bench line into headmatter; `DATED:`/`/s/` band into a structured trailing section | not yet modified |

All eight readers verified registered via `deciders_for('headmatter.read', …)`
at snapshot time. utah and wis each appended their own import line to
`courts/__init__.py` and BOTH landed — the one piece of shared state they
touched came out clean.

**On restart:** check each court file's mtime and claimed-row ratio before
relaunching an agent; several may have finished. Do not relaunch a court
whose file already changed without reading it first.

## Signature-band epic (swept this session, ranked per court)

`Document.signature` is used by NO court — `sig_blocks=0` corpus-wide — so
every `/s/` run is opinion body prose. Real data loss: **del 42/50 files**,
**md 32/50** (judges/panel/date all empty), **me 1 real file**. Cosmetic
only (court already captures judges+date from headmatter): michctapp, cadc,
virginislands. Full entry with examples in `docs/review-backlog.md`.

Negative result worth keeping: the ill citation-as-docket bug was swept
across all 82 readers and occurs NOWHERE else.

## Measuring claimed headmatter rows (get this right)

Strip the `hm-legend` block first — it carries one `data-role` per role as a
colour key — and allow a `style` attribute between `class="hmrow …"` and
`data-role=`:

    rows = re.findall(r'<div class="hmrow\b[^>]*>', html_without_legend)
    claimed = [r for r in rows if 'data-role=' in r]

A grep requiring adjacency under-reports badly: it showed ri at 63% and tenn
at 6% when both were above 99%.
