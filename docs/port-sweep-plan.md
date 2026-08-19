# The port sweep: every remaining court, batched by caption family

Written 2026-08-19. Source data: `output/notes/port_families.json`, rebuilt by
reading each rendered file's caption-style chip.

## The leverage

**159 of the 194 unported courts belong to a family that already has a
finished reader.** Handing an agent its family's working reader measurably
halves the cost: three pairs measured on 2026-08-18 came in at 122-174k
tokens and 15-31 minutes against 240-320k and 25-80 minutes for a cold port,
and `alacivapp` (70% of its code verbatim from `ala.py`) needed ZERO
debugging iterations — 268/268 rows correct on the first run.

| family | unported | reader to hand the agent |
| --- | ---: | --- |
| UNCLASSIFIED | 82 | ala, ariz, cal, scotus (method only — see below) |
| parenthetical-box | 33 | alaska, idaho, mo, virginislands, wash |
| old-faithful | 15 | alaskactapp, bap9 |
| open-range | 13 | cadc |
| colon-rail | 11 | — none yet |
| typed-sandwich | 9 | fla, tenn, wva, alacivapp, cafc, ca3/5/7/8/11 |
| section-rail | 6 | — none yet |
| backwards-c | 4 | ca9 |
| upside-down-t | 3 | ark, arkctapp, bap10, ca10 |
| banded-bracket / asterisk-rail / i-beam / status-flush | 3 each | — none yet |
| twin-rail / old-faithful-open / double-box | 2 each | — none yet |

**Port one court in each reader-less family FIRST** (colon-rail, section-rail,
status-flush, banded-bracket, asterisk-rail, i-beam, twin-rail,
old-faithful-open, double-box — 9 cold ports), and the remaining 35 courts in
those families become cheap. `pa` is the natural colon-rail pilot; `del` for
section-rail.

## UNCLASSIFIED is not a family

82 courts whose caption matches nothing in `resolve/captions.py`'s matrix.
That is not a shared shape — it means the fingerprint is not their landmark.
It is also not a difficulty signal: ala, ariz, cal and scotus are all
unclassified and all ported cleanly, dispatching on masthead position, fence
pairs and page axis instead. Hand those agents ala.py and ariz.py as METHOD
references, not as templates.

## Rules the sweep must keep

- **A mis-tagged row is worse than an untagged one.** Untagged says "nobody
  read this" — true and measurable. Mis-tagged says "read, and it is a
  caption" — false and invisible. Returning NOTHING for an unrecognised
  layout is a correct answer; core's shared walk beats a confident misreading.
- **One court file per agent**, core defects REPORTED not patched, and a
  per-agent scratch directory. See [[parallel-court-porting-protocol]].
- **Apply the core queue before the sweep** — every port measures against
  core, and yesterday's rate was roughly one core defect per court.
- **Do not trust the grades to say when a port is done.** See
  `docs/` notes and the oracle blind spots: `v1diff` is structurally blind on
  221 of 239 courts, `authorless` misses unbylined writings, and a grade can
  get WORSE as a port gets better.
