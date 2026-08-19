# pages/ — the browser demo

`index.html` runs the real `centralia` wheel in the browser on
[Pyodide](https://pyodide.org) (CPython 3.14 compiled to WebAssembly). Drop a
court PDF in, pick a court reader, get the rendered HTML back. Nothing is
uploaded — the PDF is written to Pyodide's in-memory filesystem and parsed
client-side.

## Run it locally

It must be **served**, not opened as a file. Pyodide itself boots fine from
`file://` (it is imported from the CDN over https), but Chrome blocks
same-origin `fetch()` at a `file://` origin, so `wheels/manifest.json`, the
wheel, `courts.json` and the samples never load.

```sh
cd pages && python3 -m http.server 8765
open http://127.0.0.1:8765
```

On GitHub Pages there is nothing to run — it is already served over HTTPS.

## Rebuild after changing centralia/

The page fetches a committed wheel, so it does not track the source
automatically:

```sh
./pages/build.sh      # rebuilds the wheel + wheels/manifest.json
```

`pages/wheels/*.whl` is committed on purpose (Pages is static, the browser
fetches it directly). `pages/courts.json` is a copy of
`output/notes/court_status.json`, used only to group the court dropdown by
review status; regenerate it with:

```sh
python3 -c "import json;d=json.load(open('output/notes/court_status.json'));print(json.dumps(dict(sorted(d.items())),separators=(',',':')))" > pages/courts.json
```

## Known limits

- **No `to_image()`.** pdfplumber's rasteriser needs `pypdfium2`, a compiled
  wheel absent from Pyodide, so it is installed with `deps=False`. The three
  call sites in `pipeline.py` (masthead crops :1495, figures :1526, signature
  graphics :1587) are already inside `try/except`, so they skip silently —
  output is text-only. Seals and signature images do not appear.
- **URL fetch fails, and Python cannot route around it.** A static page can
  only `fetch()` a PDF if that server sends `Access-Control-Allow-Origin`.
  Measured: `storage.courtlistener.com`, `govinfo.gov`, and `ca1.uscourts.gov`
  all serve the PDF to `curl` and none sends the header.

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

  So: upload, or ship the PDF same-origin (anything in `samples/` is fetchable),
  or put a proxy in front that adds the header — a Cloudflare Worker with a
  domain allowlist, or a CORS policy on the `storage.courtlistener.com` bucket
  itself, which would fix this for every browser-side tool at once.
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
| centralia wheel | ~0.1s |
| **ready** | **~5.9s** |
| extract 1pp scotus | 240ms |
| extract 283pp cal | 27s |
