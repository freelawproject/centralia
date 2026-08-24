# docs/ — the browser demo

`index.html` runs the real `centralia` release in the browser on
[Pyodide](https://pyodide.org) (CPython 3.14 compiled to WebAssembly). Drop a
court PDF in, or name one by URL, pick a court reader, get the rendered HTML
back. Nothing is uploaded — the PDF is written to Pyodide's in-memory
filesystem and parsed client-side.

## Run it locally

Serve it, do not open it as a file. Pyodide boots from `file://` (it is imported
from the CDN over https), `centralia` installs from `file://` too (PyPI sends
`Access-Control-Allow-Origin: *`), and the court list comes out of the installed
package — so a PDF you upload yourself reads fine there. The one thing that
still needs a same-origin `fetch()` is the bundled samples, and Chrome blocks
that at a `file://` origin, so those buttons do nothing.

```sh
cd docs && python3 -m http.server 8765
open http://127.0.0.1:8765
```

On GitHub Pages there is nothing to run — it is already served over HTTPS.

## Deploying to GitHub Pages

The page is static: no Actions, no build step, nothing server-side. Pyodide runs
in the visitor's browser. Verified working under a subpath (`/<repo>/`), which
is how Pages serves a project site.

This directory is named `docs/` precisely so Pages can publish it with no
workflow at all — **Deploy from a branch** offers only `/` (root) and `/docs`,
and the demo is not at the root. The design notes that used to live here were
renamed to `notes/` to free the name.

**Settings → Pages → Source: Deploy from a branch → `main` / `docs`.**

That is the whole deployment. Every push to `main` that touches this directory
redeploys it; there is nothing to run by hand.

`.nojekyll` is committed so Pages skips Jekyll entirely — without it Jekyll can
drop or rewrite files it does not recognise.

### One thing that will bite

**Private repos need a paid plan.** GitHub Pages on a private repo requires
Pro/Team. Making this repo public to get free Pages would publish all of
centralia, not just the demo. If you want the demo public and the source
private, push this directory to a separate public repo instead — only `docs/`
ever leaves:

```sh
git remote add demo git@github.com:<you>/centralia-demo.git
git subtree push --prefix docs demo main
```

## Keeping up with centralia/

The page installs `centralia` **from PyPI**, not from a wheel committed here:

```js
await micropip.install("centralia", deps=False)
```

So the demo follows the published release on its own. Ship a release and the
page picks it up; there is no build step to forget and no stale wheel to serve.
The cost is that unreleased work on `main` does not appear here until it ships —
if you need to demo something before shipping it, build a wheel into `wheels/`
with `./docs/build.sh` and point the install at it instead.

`deps=False` matches how `pdfplumber` is installed above it: centralia's one
dependency (`pdfplumber>=0.11.4`) is already in place, deliberately without
`pypdfium2`, which has no Pyodide wheel.

The court dropdown groups by `centralia.released.RELEASED`, read out of the
installed package at boot — there is no list to copy here and nothing to
regenerate. That list is itself generated from the reviewer's marks by
`harness.cli released --write`, so the page shows exactly what the running
release approves: 190 approved, 51 still in review, of 241 wired.

There used to be a `courts.json` copied in beside the page for this. It froze at
38 courts while 190 were signed off, which read as "these readers are not ready"
for work finished weeks earlier. A file that must be hand-copied to stay true
will eventually be false; the package cannot disagree with itself.

## Known limits

- **No `to_image()`.** pdfplumber's rasteriser needs `pypdfium2`, a compiled
  wheel absent from Pyodide, so it is installed with `deps=False`. The three
  call sites in `pipeline.py` (masthead crops :1495, figures :1526, signature
  graphics :1587) are already inside `try/except`, so they skip silently —
  output is text-only. Seals and signature images do not appear.
- **There is no "fetch by URL" box, and that is a host decision, not an
  oversight.** A static page can only `fetch()` a PDF if the server holding it
  sends `Access-Control-Allow-Origin`. A URL box was built and then taken out,
  because the host people would actually paste is the one that refuses:

  | host | `ACAO` | preflight | fetches? |
  |---|---|---|---|
  | `dev-com-courtlistener-storage.s3.amazonaws.com` | `*` | 200 | **yes** |
  | `storage.courtlistener.com` | absent | 403 | no |
  | `govinfo.gov`, `ca1.uscourts.gov` | absent | — | no |

  A box that works for an internal dev bucket and fails for every public
  CourtListener link is worse than no box: it reads as a broken page rather than
  as a policy the page does not control. Upload the PDF instead.

  Production is a bucket-policy change away from working — it is Free Law
  Project's own bucket, and the dev one already carries the config. Put this on
  `storage.courtlistener.com` and the URL box becomes worth restoring:

  ```json
  [{"AllowedOrigins": ["*"], "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"], "MaxAgeSeconds": 3000}]
  ```

  Fixing it there fixes every browser-side tool at once, not just this page.

  Doing it from Python does not help — verified in Chrome:

  | path | cross-origin |
  |---|---|
  | `pyodide.http.pyfetch` | `AbortError: Failed to fetch` |
  | `urllib.request.urlopen` | `RuntimeError: TLS not supported in this environment` |
  | `requests.get` | `ConnectionError: Failed to fetch` |
  | `requests` + `pyodide_http.patch_all()` | `NetworkError` on XHR `send` |
  | **same-origin** `requests.get` | **works** |

  Pyodide has no network of its own: `pyfetch` wraps JS `fetch`, `pyodide-http`
  wraps `XMLHttpRequest` (both CORS-checked), and `requests`/`urllib` want raw
  sockets that WASM does not have. CORS is enforced below Python, by design.

  So for a host that will not send the header: upload the file, or ship it
  same-origin (anything in `samples/` is fetchable), or put a proxy in front
  that adds it — a Cloudflare Worker with a domain allowlist. Note that a proxy
  means the PDF passes through it, so the "nothing is uploaded" promise at the
  top of this page stops holding for that path.
- **Pyodide runs on the main thread.** A 283-page opinion takes ~27s and the
  tab is frozen for the duration. Moving `run()` into a Web Worker is the fix
  if this becomes annoying.
- **`from centralia import extract` does not exist** — `__init__.py` still only
  promises it ("lands in Phase 6"). The page imports
  `centralia.pipeline.extract`.

## Measured (Chrome, warm CDN cache)

| stage | time |
|---|---|
| Pyodide boot | ~2.4s |
| pdfplumber + deps | ~2.3s |
| centralia from PyPI | ~0.6s |
| **ready** | **~5.9s** |
| extract 1pp scotus | 240ms |
| extract 283pp cal | 27s |
