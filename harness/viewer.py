"""The review server: stdlib only, no Django.

    python harness/cli.py serve [port]      (default 8002)

Serves the viewer shell, this repo's rendered pages under /out/, the OLD
repo's rendered pages under /old/ (the A/B toggle), and a small JSON API for
marks and per-court notes persisted under output/notes/ in THIS repo — the
old repo's marks are stale and are never touched.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import shutil
import threading
import sys
from html import escape
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import CORPUS_ROOT, MARKS_DIR, OLD_REPO, OUTPUT_DIR  # noqa: E402

VIEWER = Path(__file__).resolve().parent / "viewer.html"
OLD_OUTPUT = OLD_REPO / "output"
MARKS = MARKS_DIR / "marks.json"
_COURTS_DIR = Path(__file__).resolve().parent.parent / "centralia" / "courts"
TIERS = ("nay", "some", "good", "almost", "yay")
PAGEIMG_DIR = OUTPUT_DIR / ".pageimg"
_PAGE_COUNTS: dict[str, int] = {}


# A DEAD PANE FROM THE OLD REVIEW SHEET. Pages written before the current
# template embed the source PDF in a left pane of their own, by a path
# relative to the FILE ('../../assets/<court>/<stem>.pdf'). That resolved
# when the page was opened off disk; served from here it 404s, and a 404
# body is '{}' — so the pane renders as an empty grey column with two
# braces in it, beside the document (the user, 2026-08-23: 'remove the
# blank metadata column'). The viewer has its own PDF pane (p), so the old
# one is hidden WHERE IT IS SERVED rather than by rewriting thousands of
# generated files that a re-render will replace anyway.
_DEAD_PANE = b'class="review-pane pdf"'
_HIDE_PANE = (b"<style>.review-cols .review-pane.pdf{display:none}"
              b".review-cols .review-pane.doc{flex:1 1 100%}</style>")

# THE CL VIEW is rendered on demand, never as a build artifact. The review
# pages on disk go stale the moment the engine moves, and a second set of
# stale pages is worse than none — so this one is generated when it is asked
# for and cached only until the engine or the PDF is newer than the cache
# (the user, 2026-08-23: 'a toggle to render the CL view so i can see how
# things translate if they translate').
CLVIEW_DIR = OUTPUT_DIR / ".clview"
_CL_LOCK = threading.Lock()
_ENGINE_MTIME: list = [0.0, 0.0]        # [checked_at, value]

_RASTER_LOCK = threading.Lock()
_NOTES_LOCK = threading.Lock()
_STATUS_LOCK = threading.Lock()


def _engine_mtime() -> float:
    """The newest engine source. Re-measured at most once every few seconds —
    a rglob per request is wasted work, and the answer cannot change between
    two clicks in a way that matters."""
    now = time.time()
    if now - _ENGINE_MTIME[0] > 3.0:
        _ENGINE_MTIME[0] = now
        _ENGINE_MTIME[1] = max(
            (p.stat().st_mtime for p in (REPO_ROOT / "centralia").rglob("*.py")),
            default=0.0)
    return _ENGINE_MTIME[1]


def _cl_page(court: str, stem: str) -> Path | None:
    """This record as CourtListener would store it, rendered on demand."""
    pdf = CORPUS_ROOT / court / f"{stem}.pdf"
    if not pdf.is_file():
        return None
    out = CLVIEW_DIR / court / f"{stem}.html"
    if out.exists() and out.stat().st_mtime >= max(pdf.stat().st_mtime,
                                                   _engine_mtime()):
        return out
    with _CL_LOCK:                      # extraction is not thread-safe
        if out.exists() and out.stat().st_mtime >= max(pdf.stat().st_mtime,
                                                       _engine_mtime()):
            return out
        # A SEPARATE PROCESS, EVERY TIME. This server has been running since
        # before the last engine edit; rendering in-process would serve the
        # engine it imported at startup, which is exactly the staleness this
        # view exists to avoid.
        import subprocess
        try:
            r = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "cli.py"),
                 "clview", f"{court}/{stem}"],
                cwd=str(Path(__file__).parent.parent),
                capture_output=True, text=True, timeout=300)
        except Exception as e:          # noqa: BLE001
            return _cl_error(out, repr(e)[:400])
        if out.exists():
            return out
        # A FAILURE IS A FINDING, shown where the view would have been —
        # the alternative is an empty pane that says nothing.
        return _cl_error(out, ((r.stderr or r.stdout or "no output")
                               .strip()[-1200:]))


def _cl_error(out: Path, msg: str) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "<title>CL view — failed</title>"
        "<body style='font:14px system-ui;padding:2em;color:#7a2620'>"
        "<b>The engine raised on this record, so there is nothing to "
        f"translate.</b><pre>{escape(msg)}</pre>")
    return out


def _page_image(court: str, stem: str, page: int) -> Path | None:
    """Rasterize one source page on demand, cached to output/.pageimg/.

    ONE AT A TIME. pdfium is not thread-safe, and the browser lazy-loads a
    whole document's pages at once — concurrent rasterizing corrupted its
    state and pages came back 'Failed to load page', so SOME documents
    showed their pages and others silently did not. The cache hit above the
    lock keeps the common path free of contention."""
    out = PAGEIMG_DIR / court / stem / f"{page}.png"
    if out.exists():
        return out
    with _RASTER_LOCK:
        if out.exists():
            return out
        return _rasterize(court, stem, page, out)


def _rasterize(court: str, stem: str, page: int, out: Path) -> Path | None:
    pdf_path = CORPUS_ROOT / court / f"{stem}.pdf"
    if not pdf_path.is_file() or not pdf_path.resolve().is_relative_to(
            CORPUS_ROOT.resolve()):
        return None
    import pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            _PAGE_COUNTS[f"{court}/{stem}"] = len(pdf.pages)
            if not 1 <= page <= len(pdf.pages):
                return None
            im = pdf.pages[page - 1].to_image(resolution=110)
            out.parent.mkdir(parents=True, exist_ok=True)
            im.save(str(out))
    except Exception:
        # A silent `return None` here becomes a bare 404 in the browser: the
        # page images just do not appear, with nothing anywhere saying why.
        # Say why.
        import traceback, sys
        print(f"[pgimg] {court}/{stem} p{page} FAILED", file=sys.stderr)
        traceback.print_exc()
        sys.stderr.flush()
        return None
    return out


def _page_count(court: str, stem: str) -> int:
    key = f"{court}/{stem}"
    if key not in _PAGE_COUNTS:
        pdf_path = CORPUS_ROOT / court / f"{stem}.pdf"
        if not pdf_path.is_file():
            return 0
        import pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                _PAGE_COUNTS[key] = len(pdf.pages)
        except Exception:
            return 0
    return _PAGE_COUNTS.get(key, 0)


def _manifest() -> dict:
    out: dict[str, list[str]] = {}
    if OUTPUT_DIR.is_dir():
        for court_dir in sorted(OUTPUT_DIR.iterdir()):
            if not court_dir.is_dir() or court_dir.name == "notes":
                continue
            stems = sorted(p.stem for p in court_dir.glob("*.html")
                           if p.stem != "index")
            if stems:
                out[court_dir.name] = stems
    return out


MARKS_BAK = MARKS_DIR / "marks.json.bak"
# PER-FILE NOTES: what is wrong with THIS rendering, in the reviewer's own
# words, written while the file is on screen. The mark says how bad; the note
# says what — and a note outlives the mark, because the next person to work
# the file needs the sentence, not the tier.
NOTES = MARKS_DIR / "filenotes.json"
NOTES_BAK = MARKS_DIR / "filenotes.json.bak"
NOTES_LOG = MARKS_DIR / "filenotes.log"
MARKS_LOG = MARKS_DIR / "marks.log"
MARKS_SNAPS = MARKS_DIR / "marks-backups"
_MARKS_LOCK = threading.Lock()


# ---- court grouping -------------------------------------------------------
# The sidebar lists 238 courts. Grouped, it reads as a work plan; ungrouped it
# is an alphabet soup where 'nd' (North Dakota) sits beside 'ndd' (D.N.D.).
# The ambiguous pairs are exactly why the district set is ENUMERATED rather
# than matched on a trailing 'd': me/med, md/mdd, nc/nced, nd/ndd, sd/sdd,
# or/ord, va/vaed, vt/vtd, dc/dcd all collide under any suffix rule.
_FED_APPELLATE = ["scotus", "ca1", "ca2", "ca3", "ca4", "ca5", "ca6", "ca7",
                  "ca8", "ca9", "ca10", "ca11", "cadc", "cafc",
                  "bap1", "bap6", "bap8", "bap9", "bap10"]
_FED_DISTRICT = set("""
akd almd alnd alsd ared arwd azd cacd caed cand casd cod ctd dcd ded flmd
flnd flsd gamd gand gasd hid iand iasd idd ilcd ilnd ilsd innd insd ksd kyed
kywd laed lamd lawd mad mdd med mied miwd mnd moed mowd msnd mssd mtd nced
ncmd ncwd ndd ned nhd njd nmd nvd nyed nynd nysd nywd ohnd ohsd oked oknd
okwd ord paed pamd pawd rid scd sdd tned tnmd tnwd txed txnd txsd txwd utd
vaed vawd vtd waed wawd wied wiwd wvnd wvsd wyd
# THE TERRITORIAL DISTRICTS ARE FEDERAL DISTRICT COURTS. Guam, Puerto Rico
# and the Virgin Islands each have an Article IV district court that files on
# CM/ECF exactly as the fifty states' districts do — listed nowhere, they
# fell to the 'state' default and sat in the state lane, which is neither
# where they belong nor where their reader will be written (the user,
# 2026-08-23: 'GUD should be in the federal district catgegory with vid and
# prd'). `virginislands` and `prapp`/`prsupreme` are the TERRITORIES' OWN
# courts and stay where they are — a different thing entirely.
gud prd vid
""".split())
# Federal specialty, military and agency tribunals — neither a circuit nor a
# district, and not a state court either.
# Not courts of a state: military and Article I courts, boards, the
# ATTORNEY-GENERAL opinion series, and Delaware's Court of Common Pleas
# (delctcompl — the user's call, 2026-08-19).
# Originally:
# ATTORNEY-GENERAL opinion series (calag/mdag/minnag/texag alongside olc,
# the user's call 2026-08-19) — an AG opinion is not a state court's paper
# and listing it among them made the state group misread as unfinished.
# TERRITORIES AND TRIAL COURTS, the state lane's leftovers (the user's call,
# 2026-08-20: 'move the remaining state courts not done to the misc other
# tribunal category ... move virgin islands over there too'). Not one of them
# is a state's appellate court: New York's four trial courts (its appellate
# papers are nyappdiv and ny), Puerto Rico, the Northern Marianas and the
# Virgin Islands. Every other court in the state group now has a reader, so
# the group reads as the state lane's real progress instead of carrying
# courts that lane will never close.
_OTHER = set("""
acca afcca armfor nmcca uscgcoca asbca bia cavc cit uscfc tax ttab mspb
olc calag mdag minnag texag
delctcompl
nycivct nyfamct nysupct nysurct
prapp prsupreme nmariana virginislands
""".split())


def _court_group(cid: str) -> str:
    if cid in _FED_APPELLATE:
        return "fed-appellate"
    if cid in _FED_DISTRICT:
        return "fed-district"
    if cid in _OTHER:
        return "other"
    return "state"


_GROUP_ORDER = ["fed-appellate", "state", "other", "fed-district"]
_STATUS = MARKS_DIR / "court_status.json"


def _has_reader(court: str) -> bool:
    """Whether a court actually has a headmatter reader registered.

    DERIVED, not declared. `quality` measures render defects and says
    nothing about whether the headmatter was understood — fla graded A 0.17
    with every one of its 50 records completely unread. A court with no
    reader must not be able to look finished in the sidebar.

    Read from the FILESYSTEM, not from the import. `_DECIDERS` is populated
    when `centralia.courts` is first imported, so a viewer started before a
    port landed reports every new reader as absent for the life of the
    process — and this server runs for days. One file per court is the
    architecture's own invariant, so the file IS the signal, and it is fresh
    on every request."""
    if (_COURTS_DIR / f"{court}.py").exists():
        return True
    try:
        import centralia.courts  # noqa: F401  (registers the deciders)
        from centralia.resolve.evidence import _DECIDERS
        return ("headmatter.read", court) in _DECIDERS
    except Exception:
        return False


def _court_meta(courts: list[str]) -> dict:
    """Group + porting status for each court, and the group order the sidebar
    lays them out in."""
    try:
        status = json.loads(_STATUS.read_text()) if _STATUS.exists() else {}
    except Exception:
        status = {}
    meta = {c: {"group": _court_group(c), "status": status.get(c, ""),
                "reader": _has_reader(c)}
            for c in courts}
    order = {g: i for i, g in enumerate(_GROUP_ORDER)}
    fed_rank = {c: i for i, c in enumerate(_FED_APPELLATE)}
    ordered = sorted(courts, key=lambda c: (
        order[_court_group(c)], fed_rank.get(c, 999), c))
    return {"meta": meta, "order": ordered, "groups": _GROUP_ORDER}


def _load_marks() -> dict:
    """The marks are HAND LABOUR — hundreds of judgements that exist nowhere
    else. Read the live file; if it is unreadable (a truncated write, a
    crash mid-save) fall back to the previous good copy rather than
    returning {} and letting the next save overwrite everything with it."""
    for path in (MARKS, MARKS_BAK):
        try:
            if path.exists():
                with open(path) as f:
                    return json.load(f)
        except Exception:
            import sys, traceback
            print(f"[marks] {path} unreadable, falling back", file=sys.stderr)
            traceback.print_exc()
    return {}


def _save_marks(marks: dict) -> None:
    """Never truncate the only copy. Previous version kept as .bak, new one
    written to a temp file and fsynced, then swapped in with os.replace —
    which is atomic, so a crash leaves either the old file or the new one,
    never a half-written one. A dated snapshot is kept once per day."""
    MARKS_DIR.mkdir(parents=True, exist_ok=True)
    if MARKS.exists():
        try:
            shutil.copy2(MARKS, MARKS_BAK)
            MARKS_SNAPS.mkdir(parents=True, exist_ok=True)
            snap = MARKS_SNAPS / f"marks-{time.strftime('%Y%m%d')}.json"
            if not snap.exists():
                shutil.copy2(MARKS, snap)
        except Exception:
            pass
    tmp = MARKS.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(marks, f, indent=0, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, MARKS)


_STATUSES = ("complete", "active", "started", "")


def _save_status(court: str, status: str) -> None:
    """The per-court porting status the sidebar draws its ✓ from. Read since
    the sidebar existed and never writable: the file was edited by hand,
    which means the one judgement the reviewer is actually qualified to make
    — 'this court is done' — was the one thing the viewer could not record.
    Written atomically, previous copy kept, like the marks."""
    with _STATUS_LOCK:
        try:
            cur = json.loads(_STATUS.read_text()) if _STATUS.exists() else {}
        except Exception:
            cur = {}
        if status:
            cur[court] = status
        else:
            cur.pop(court, None)
        MARKS_DIR.mkdir(parents=True, exist_ok=True)
        if _STATUS.exists():
            try:
                shutil.copy2(_STATUS, _STATUS.with_suffix(".json.bak"))
            except Exception:
                pass
        tmp = _STATUS.with_suffix(".json.tmp")
        with open(tmp, "w") as f:
            json.dump(cur, f, indent=1, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, _STATUS)


def _load_notes() -> dict:
    """The notes are HAND LABOUR, like the marks — read the live file and
    fall back to the previous good copy rather than returning {} and letting
    the next save overwrite everything with it."""
    for path in (NOTES, NOTES_BAK):
        try:
            if path.exists():
                with open(path) as f:
                    return json.load(f)
        except Exception:
            print(f"[notes] {path} unreadable, falling back", file=sys.stderr)
    return {}


def _save_notes(notes: dict) -> None:
    """Never truncate the only copy: previous version to .bak, new one
    fsynced to a temp file and swapped in with os.replace."""
    MARKS_DIR.mkdir(parents=True, exist_ok=True)
    if NOTES.exists():
        try:
            shutil.copy2(NOTES, NOTES_BAK)
        except Exception:
            pass
    tmp = NOTES.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(notes, f, indent=0, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, NOTES)


def _log_note(key: str, text: str) -> None:
    """An APPEND-ONLY journal of every note ever written, including the ones
    later edited away — the sentence someone wrote about a file is evidence
    even after the file changes."""
    try:
        MARKS_DIR.mkdir(parents=True, exist_ok=True)
        with open(NOTES_LOG, "a") as f:
            f.write(json.dumps({"t": time.time(), "key": key, "text": text,
                                "sha": _render_digest(key)}) + "\n")
            f.flush()
    except Exception:
        pass


def _stale_marks() -> dict:
    """Keys whose FILE WAS RE-RENDERED AFTER the mark was set.

    A mark is a judgement about a particular rendering. Re-render the file
    and the judgement may no longer describe it — ca9 carried 45 nays whose
    every file had since been re-rendered, 35 of them mechanically clean by
    the time anyone looked. Nothing in the viewer said so, and a stale nay
    reads exactly like a live one. Marks set before the log existed are
    reported too: their time is unknown, so they cannot be vouched for."""
    times: dict[str, float] = {}
    shas: dict[str, str] = {}
    try:
        with open(MARKS_LOG) as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("key"):
                    times[e["key"]] = e.get("t") or 0.0
                    if e.get("sha"):
                        shas[e["key"]] = e["sha"]
    except OSError:
        pass
    out: dict[str, str] = {}
    for key in _load_marks():
        court, _, stem = key.partition("/")
        html = OUTPUT_DIR / court / f"{stem}.html"
        try:
            rendered = html.stat().st_mtime
        except OSError:
            continue
        sha = shas.get(key)
        if sha:                            # EXACT: the bytes are the proof
            if sha != _render_digest(key):
                out[key] = "changed"
            continue
        marked = times.get(key)
        if marked is None:
            out[key] = "unknown"          # predates the journal
        elif rendered > marked + 60:
            out[key] = "re-rendered"      # may or may not have changed
    return out


def _render_digest(key: str) -> str | None:
    """A short digest of the rendering a mark is about, so staleness can be
    answered exactly instead of by timestamp — re-running the same code
    rewrites the file and moves its mtime without changing a byte."""
    court, _, stem = key.partition("/")
    try:
        data = (OUTPUT_DIR / court / f"{stem}.html").read_bytes()
    except OSError:
        return None
    return hashlib.sha1(data).hexdigest()[:16]


def _log_mark(key: str, tier) -> None:
    """An APPEND-ONLY journal of every mark ever set, so the full history can
    be replayed even if every JSON copy is lost. Appending cannot truncate
    what is already there."""
    try:
        MARKS_DIR.mkdir(parents=True, exist_ok=True)
        with open(MARKS_LOG, "a") as f:
            f.write(json.dumps({"t": time.time(), "key": key,
                                "tier": tier,
                                "sha": _render_digest(key)}) + "\n")
            f.flush()
    except Exception:
        pass


def _safe_under(root: Path, rel: str) -> Path | None:
    p = (root / unquote(rel)).resolve()
    return p if p.is_file() and p.is_relative_to(root.resolve()) else None


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        ctype = {"html": "text/html", "xml": "text/xml", "json": "application/json",
                 "png": "image/png", "css": "text/css",
                 "pdf": "application/pdf"}.get(
                     path.suffix.lstrip("."), "text/plain")
        if ctype == "application/pdf":
            return self._send(200, path.read_bytes(), ctype)
        body = path.read_bytes()
        if ctype == "text/html" and _DEAD_PANE in body:
            body = (body.replace(b"</head>", _HIDE_PANE + b"</head>", 1)
                    if b"</head>" in body else _HIDE_PANE + body)
        self._send(200, body, f"{ctype}; charset=utf-8")

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            return self._send_file(VIEWER)
        if self.path == "/api/courtmeta":
            return self._send(200, json.dumps(
                _court_meta(list(_manifest()))).encode())
        if self.path == "/api/manifest":
            return self._send(200, json.dumps(_manifest()).encode())
        if self.path == "/api/marks":
            return self._send(200, json.dumps(_load_marks()).encode())
        if self.path == "/api/filenotes":
            return self._send(200, json.dumps(_load_notes()).encode())
        if self.path == "/api/stale":
            return self._send(200, json.dumps(_stale_marks()).encode())
        if self.path == "/api/quality":
            q = OUTPUT_DIR / "notes" / "quality.json"
            return self._send(200, q.read_bytes() if q.exists() else b"{}")
        if self.path.startswith("/api/notes/"):
            court = unquote(self.path.rsplit("/", 1)[1])
            p = MARKS_DIR / f"{court}.md"
            text = p.read_text() if p.exists() else ""
            return self._send(200, json.dumps({"text": text}).encode())
        if self.path.startswith("/out/"):
            p = _safe_under(OUTPUT_DIR, self.path[5:])
            return self._send_file(p) if p else self._send(404, b"{}")
        if self.path.startswith("/cl/"):
            court, _, stem = unquote(
                self.path[4:]).removesuffix(".html").partition("/")
            if not court.replace("_", "").replace("-", "").isalnum() \
                    or not stem or "/" in stem or ".." in stem:
                return self._send(404, b"{}")
            p = _cl_page(court, stem)
            return self._send_file(p) if p else self._send(404, b"{}")
        if self.path.startswith("/old/"):
            p = _safe_under(OLD_OUTPUT, self.path[5:])
            return self._send_file(p) if p else self._send(404, b"{}")
        if self.path.startswith("/pdf/"):
            p = _safe_under(CORPUS_ROOT, self.path[5:])
            if p and p.suffix == ".pdf":
                return self._send_file(p)
            return self._send(404, b"{}")
        if self.path.startswith("/pginfo/"):
            court, _, stem = unquote(self.path[8:]).partition("/")
            n = _page_count(court, stem)
            return self._send(200, json.dumps({"pages": n}).encode())
        if self.path.startswith("/pgimg/"):
            parts = unquote(self.path[7:]).split("/")
            if len(parts) == 3 and parts[2].removesuffix(".png").isdigit():
                court, stem, page = parts[0], parts[1], int(
                    parts[2].removesuffix(".png"))
                p = _page_image(court, stem, page)
                if p:
                    return self._send_file(p)
            return self._send(404, b"{}")
        return self._send(404, b"{}")

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        data = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/marks":
            key, tier = data.get("key"), data.get("tier")
            if not key or tier not in (*TIERS, None):
                return self._send(400, b'{"error":"bad mark"}')
            # ONE WRITER AT A TIME. This is read-modify-write on a shared
            # file, and the server is threaded — two marks landing together
            # would race, and the loser's mark would vanish.
            with _MARKS_LOCK:
                marks = _load_marks()
                if tier is None:
                    marks.pop(key, None)
                else:
                    marks[key] = tier
                _log_mark(key, tier)
                _save_marks(marks)
            return self._send(200, b'{"ok":true}')
        if self.path == "/api/filenotes":
            key = data.get("key")
            text = (data.get("text") or "").strip()
            if not key or "/" not in key:
                return self._send(400, b'{"error":"bad note"}')
            # ONE WRITER AT A TIME, for the same reason the marks take a
            # lock: this is read-modify-write on a shared file.
            with _NOTES_LOCK:
                notes = _load_notes()
                if text:
                    notes[key] = text
                else:
                    notes.pop(key, None)
                _log_note(key, text)
                _save_notes(notes)
            return self._send(200, b'{"ok":true}')
        if self.path == "/api/courtstatus":
            court = (data.get("court") or "").strip()
            status = (data.get("status") or "").strip()
            if not court.replace("_", "").replace("-", "").isalnum():
                return self._send(400, b'{"error":"bad court"}')
            if status not in _STATUSES:
                return self._send(400, b'{"error":"bad status"}')
            _save_status(court, status)
            return self._send(200, b'{"ok":true}')
        if self.path == "/api/render":
            # Re-run the engine on demand: one file, or a whole court. The
            # viewer serves output/ off disk, so a re-render is visible on
            # the next reload with no restart.
            import subprocess
            court = (data.get("court") or "").strip()
            stem = (data.get("stem") or "").strip()
            if not court.replace("_", "").replace("-", "").isalnum():
                return self._send(400, b'{"error":"bad court"}')
            cmd = [sys.executable, str(Path(__file__).parent / "cli.py"),
                   "render", court]
            if stem:
                cmd += ["--only", stem]
            try:
                r = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent),
                                   capture_output=True, text=True, timeout=900)
                out = (r.stdout or "").strip().splitlines()
                subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "cli.py"),
                     "quality", court],
                    cwd=str(Path(__file__).parent.parent),
                    capture_output=True, text=True, timeout=900)
                return self._send(200, json.dumps({
                    "ok": r.returncode == 0,
                    "msg": (out[-1] if out else "") or (r.stderr or "")[-200:],
                }).encode())
            except Exception as e:  # noqa: BLE001
                return self._send(200, json.dumps(
                    {"ok": False, "msg": repr(e)[:200]}).encode())
        if self.path.startswith("/api/notes/"):
            court = unquote(self.path.rsplit("/", 1)[1])
            if not court.replace("_", "").replace("-", "").isalnum():
                return self._send(400, b'{"error":"bad court"}')
            MARKS_DIR.mkdir(parents=True, exist_ok=True)
            (MARKS_DIR / f"{court}.md").write_text(data.get("text", ""))
            return self._send(200, b'{"ok":true}')
        return self._send(404, b"{}")


def serve(port: int = 8002) -> None:
    print(f"review viewer: http://localhost:{port}/  (out={OUTPUT_DIR}, old={OLD_OUTPUT})")
    # THREADING, not HTTPServer. `/api/render` shells out to a full court
    # render, and on a single-threaded server that one request blocks every
    # other — the site stops answering and the browser keeps showing the
    # PREVIOUS render, which reads as "the fix did not work".
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8002)
