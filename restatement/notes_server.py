"""Tiny local server that persists the review viewer's per-court notes to disk.

The review viewer (``output/viewer.html``) is a static page, so on its own it
can only keep notes in the browser's localStorage. Run this server alongside it
and the notes panel reads/writes ``output/notes/<court>.md`` directly — so notes
survive across sessions and are readable from the repo before reprocessing a
court.

It serves ``output/`` as static files (so you can also browse the viewer at
http://127.0.0.1:8000/viewer.html) and exposes a small notes API with CORS
enabled, so the viewer works whether it's opened from this server or straight
from ``file://``:

    GET  /api/notes            -> {court: markdown, ...}   (live from disk)
    PUT  /api/notes/<court>    body = markdown             -> writes the .md

Run:  uv run python -m restatement.notes_server [port]
"""

from __future__ import annotations

import json
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path("output")
NOTES = ROOT / "notes"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    # -- CORS so a file:// viewer (origin "null") can call the API ----------
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _all_notes(self) -> dict:
        data = {}
        if NOTES.is_dir():
            for md in sorted(NOTES.glob("*.md")):
                data[md.stem] = md.read_text(encoding="utf-8")
        return data

    # 'done' = courts Claude has finished addressing the notes for, so the
    # reviewer can see what's claimed complete. Persisted to notes/_done.json.
    def _done(self) -> dict:
        f = NOTES / "_done.json"
        if f.is_file():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    # Review marks, persisted to disk so they survive refreshes / machines and
    # can be read back to focus on the ~/✗ courts and learn from the ✓ ones:
    #   _marks.json      per-court verdict   {court: "yay"|"almost"|"nay"}
    #   _filemarks.json  per-PDF rating      {"court/stem": "yay"|"almost"|"nay"}
    def _store(self, name: str) -> dict:
        f = NOTES / name
        if f.is_file():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _write_store(self, name: str, data: dict):
        NOTES.mkdir(parents=True, exist_ok=True)
        (NOTES / name).write_text(
            json.dumps(data, indent=0, sort_keys=True), encoding="utf-8"
        )

    def do_GET(self):
        if self.path == "/api/notes":
            self._json(self._all_notes())
            return
        if self.path == "/api/done":
            self._json(self._done())
            return
        if self.path == "/api/marks":
            self._json(self._store("_marks.json"))
            return
        if self.path == "/api/filemarks":
            self._json(self._store("_filemarks.json"))
            return
        super().do_GET()

    def _bad_court(self, court):
        return not court or "/" in court or "\\" in court or court.startswith(".")

    def do_PUT(self):
        if self.path.startswith("/api/notes/"):
            court = urllib.parse.unquote(self.path[len("/api/notes/") :]).strip()
            if self._bad_court(court):
                self._json({"error": "bad court id"}, status=400)
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else ""
            NOTES.mkdir(parents=True, exist_ok=True)
            (NOTES / f"{court}.md").write_text(body, encoding="utf-8")
            self._json({"ok": True, "court": court})
            return
        if self.path.startswith("/api/done/"):
            court = urllib.parse.unquote(self.path[len("/api/done/") :]).strip()
            if self._bad_court(court):
                self._json({"error": "bad court id"}, status=400)
                return
            length = int(self.headers.get("Content-Length", 0))
            val = (self.rfile.read(length).decode("utf-8") if length else "").strip()
            done = self._done()
            if val.lower() in ("false", "0", ""):
                done.pop(court, None)
            else:
                done[court] = True
            NOTES.mkdir(parents=True, exist_ok=True)
            (NOTES / "_done.json").write_text(
                json.dumps(done, indent=0, sort_keys=True), encoding="utf-8"
            )
            self._json({"ok": True, "court": court, "done": court in done})
            return
        # Bulk replace of a marks store (the viewer sends the whole dict, mirroring
        # localStorage). Only "yay"/"almost"/"nay" values are kept.
        for path, name in (("/api/marks", "_marks.json"),
                           ("/api/filemarks", "_filemarks.json")):
            if self.path == path:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                try:
                    data = json.loads(raw)
                except Exception:
                    self._json({"error": "bad json"}, status=400)
                    return
                clean = {
                    k: v for k, v in (data or {}).items()
                    if v in ("yay", "almost", "nay")
                }
                self._write_store(name, clean)
                self._json({"ok": True, "count": len(clean)})
                return
        self.send_error(404)

    def log_message(self, *a):
        pass


def main(port: int = 8077):
    if not ROOT.is_dir():
        print(f"error: {ROOT}/ not found — run from the repo root", file=sys.stderr)
        raise SystemExit(1)
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"notes server on http://127.0.0.1:{port}")
        print(f"  viewer:  http://127.0.0.1:{port}/viewer.html")
        print(
            f"  notes -> {NOTES}/<court>.md  (GET /api/notes, PUT /api/notes/<court>)"
        )
        print("Ctrl-C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8077)
