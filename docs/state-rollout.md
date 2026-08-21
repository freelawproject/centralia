# Phase 7b — state supreme + intermediate appellate rollout

Scope: every state supreme and intermediate appellate court with PDFs in the
old corpus (`/Users/Palin/Code/centralia/assets/`). 97 courts, ~3,900 PDFs.
One state at a time, in chunks; per state: harvest old-repo knowledge if the
old extractor is nontrivial, register the profile, render, triage the fails,
fix at engine/profile level (never court code), freeze baseline, move on.

Corpus notes (checked against the old registry 2026-08-14):
- **No New York appellate corpus.** `ny` (Court of Appeals) and `nyappdiv`
  are absent. Only trial-level NY courts exist (nysupct 21, nycivct 4,
  nyfamct 1, nysurct 5). nysupct is parked in the judgment-call chunk.
- **No Oklahoma at all** (okla / oklacrimapp / oklaciv absent).
- **No Colorado Supreme** (`colo` absent); coloctapp is already registered.
- Pennsylvania's intermediates are `pasuperct` + `pacommwct` (names don't
  say "appeals" — don't lose them).
- Excluded as non-state: bap1/6/8/9/10, ttab, uscgcoca, AG offices,
  delch/delsuperct/delctcompl, ncbizct, texbizct, indtc, njtaxct, ortc,
  vtsuperct, mesuperct, ohioctcl (trial/specialty — separate decision later).

Already registered before this phase: ala, conn, mont, tenn, utah,
utahctapp, coloctapp (+ 13 circuits, scotus, akd).

## Chunks

Status: ☐ todo · ◐ in progress · ✅ rendered+triaged+baseline frozen

**2026-08-16: ALL CHUNKS RENDERED AND TRIAGED.** Census ≈99% valid across
~5,500 state-court files. Remaining tails (1–3 files each, ≈30 total —
Phase 8 stragglers): utah 1, ark 1, del 1, fladistctapp 1, gactapp 1,
la 2, nysupct 1, haw 3 (honest bar-notice reviews), me 2, michctapp 2,
mdctspecapp 1, missctapp 1, ohio 1, or 1, orctapp 2, pacommwct 1, va 2,
wva 1, wyo 1, texapp 2 (1 = unreadable CID), prsupreme 1.
No NY appellate / OK / colo-supreme corpora exist (see notes above).

- ✅ **1 — finish covered states**: alacivapp 30, alacrimapp 30, connappct 44,
  tennctapp 42, tenncrimapp 42 (siblings of validated courts; also render
  ala/utah/utahctapp/coloctapp so the viewer has them)
- ✅ **2 — AK/AZ**: alaska 50, alaskactapp 42, ariz 50, arizctapp 42
- ✅ **3 — AR/DE/DC**: ark 50, arkctapp 42, del 50, dc 30
- ✅ **4 — FL/GA**: fla 50, fladistctapp 42, ga 50, gactapp 42
- ✅ **5 — HI/ID**: haw 50, hawapp 30, idaho 50, idahoctapp 30
- ✅ **6 — IL/IN**: ill 50, illappct 42, ind 50, indctapp 42
- ✅ **7 — IA/KS**: iowa 50, iowactapp 30, kan 50, kanctapp 42
- ✅ **8 — KY/LA**: ky 50, kyctapp 42, la 50, lactapp 42
- ✅ **9 — ME/MD/MA**: me 50, md 50, mdctspecapp 30, mass 50, massappct 42
- ✅ **10 — MI/MN**: mich 50, michctapp 42, minn 50, minnctapp 30
- ✅ **11 — MS/MO**: miss 50, missctapp 30, mo 50, moctapp 27
- ✅ **12 — NE/NV/NH**: neb 50, nebctapp 42, nev 50, nevapp 31, nh 50
- ✅ **13 — NJ/NM**: nj 50, njsuperctappdiv 42, nm 50, nmctapp 21
- ✅ **14 — NC/ND**: nc 50, ncctapp 42, nd 50
- ✅ **15 — OH/OR**: ohio 50, ohioctapp 42, or 50, orctapp 42
- ✅ **16 — PA/RI**: pa 50, pasuperct 42, pacommwct 42, ri 50
- ✅ **17 — SC/SD**: sc 50, scctapp 28, sd 50
- ✅ **18 — TX**: tex 50, texapp 30, texcrimapp 42
- ✅ **19 — VT/VA**: vt 50, va 50, vactapp 30
- ✅ **20 — WA/WV**: wash 50, washctapp 42, wva 50, wvactapp 42
- ✅ **21 — WI/WY**: wis 49, wisctapp 30, wyo 50
- ◐ **22 — hard tail (Phase 8)**: cal 30, calctapp 42
- ✅ **23 — territories + judgment calls** (flag for user): guam 32,
  nmariana 32, prsupreme 31, prapp 42, virginislands 32, nysupct 21
  (trial-level; only NY corpus that exists)

## Per-chunk procedure

1. Skim old extractors (`/Users/Palin/Code/centralia/centralia/extractors/`)
   for each court: byline grammar, footnote hints, known junk, quirks worth
   harvesting. Record anything nontrivial in docs/harvest-states.md.
2. Register profiles in `centralia/courts/__init__.py` (data only).
3. Render the chunk; run the audit command over it.
4. Triage review/failed files in the viewer; fix at engine or profile level.
5. Footnote truth check if the court has truth rows in
   `output/notes/_footnotes_truth.json`.
6. Freeze baseline JSONs; tick the chunk here.
