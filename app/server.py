"""Bean Studio: a local web interface for The Bean With Bad Ideas pipeline.

    start.bat                 (or)    .venv\\Scripts\\python app\\server.py

Serves http://127.0.0.1:<port> (localhost only). Everything it does runs a command from config.json on this
machine: the line-boil build steps, the YouTube uploader and the Claude Code agent.
"""
import datetime as dt, json, os, re, subprocess, sys, threading, time, uuid, webbrowser
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort

ROOT = Path(__file__).resolve().parent.parent          # C:\Users\praty\youtube
CONFIG = ROOT / "config.json"
DEFAULTS = {
    "port": 5173,
    "open_browser": True,
    "projects_dir": str(ROOT / "line-boil"),
    "planner": str(ROOT / "bean-planner.xlsx"),
    "python": sys.executable,   # the .venv python: has the uploader libs; build.py re-runs itself under the kit
    "engine": str(Path.home() / ".claude" / "skills" / "line-boil" / "engine" / "build.py"),
    "uploader": str(ROOT / "tools" / "yt_upload.py"),
    "agent_command": ["claude", "-p", "--permission-mode", "acceptEdits"],
    "agent_cwd": str(ROOT),
    "slots": {"A": "12:00", "B": "06:30", "Long": "21:30"},
    "channel": "The Bean With Bad Ideas",
    "hide_projects": ["bean-avatar"],   # folders in projects_dir that aren't videos
}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")

def cfg():
    c = dict(DEFAULTS)
    if CONFIG.exists():
        c.update(json.loads(CONFIG.read_text(encoding="utf-8")))
    return c

app = Flask(__name__, static_folder="static", static_url_path="/static")

def proj_dir(name):
    if not SLUG.match(name or ""): abort(400, "bad project name")
    p = Path(cfg()["projects_dir"]) / name
    if not p.is_dir(): abort(404, "no such project")
    return p


# ---------- jobs: one background process each, log kept in memory ----------
JOBS = {}

def start_job(label, cmd, cwd):
    jid = uuid.uuid4().hex[:8]
    job = {"id": jid, "label": label, "cmd": cmd, "log": [], "done": False, "code": None, "started": time.time()}
    JOBS[jid] = job
    def run():
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 text=True, encoding="utf-8", errors="replace", env=env)
            job["pid"] = p.pid
            for line in p.stdout: job["log"].append(line.rstrip("\n"))
            job["code"] = p.wait()
        except Exception as e:
            job["log"].append(f"[could not start] {e}"); job["code"] = -1
        job["done"] = True
    threading.Thread(target=run, daemon=True).start()
    return job

@app.get("/api/jobs")
def jobs():
    return jsonify([{k: j[k] for k in ("id", "label", "done", "code", "started")} for j in sorted(JOBS.values(), key=lambda j: -j["started"])][:30])

@app.get("/api/jobs/<jid>")
def job(jid):
    j = JOBS.get(jid) or abort(404)
    since = int(request.args.get("since", 0))
    return jsonify({"id": jid, "label": j["label"], "done": j["done"], "code": j["code"], "log": j["log"][since:], "n": len(j["log"])})

@app.post("/api/jobs/<jid>/stop")
def stop(jid):
    j = JOBS.get(jid) or abort(404)
    if not j["done"] and j.get("pid"):
        subprocess.run(["taskkill", "/PID", str(j["pid"]), "/T", "/F"], capture_output=True)
    return jsonify(ok=True)


# ---------- projects ----------
def sheet_title(p):
    f = p / f"{p.name}-youtube.txt"
    if not f.exists(): return None
    m = re.search(r"== TITLE ==\s*\n(.+)", f.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None

def summary(p):
    n = p.name
    has = lambda s: (p / f"{n}{s}").exists()
    up = p / f"{n}-upload.json"
    upinfo = json.loads(up.read_text(encoding="utf-8")) if up.exists() else None
    script = p / "script.json"
    words = len(" ".join(json.loads(script.read_text(encoding="utf-8"))).split()) if script.exists() else 0
    steps = {"script": words > 20, "video": has(".mp4"), "srt": has(".srt"), "thumbnail": has("-thumbnail.png"),
             "sheet": has("-youtube.txt"), "uploaded": bool(upinfo)}
    return {"name": n, "title": sheet_title(p), "words": words, "steps": steps, "upload": upinfo,
            "ready": all(steps[k] for k in ("video", "srt", "thumbnail", "sheet")),
            "modified": max((f.stat().st_mtime for f in p.iterdir()), default=0)}

@app.get("/api/projects")
def projects():
    d = Path(cfg()["projects_dir"])
    hide = set(cfg().get("hide_projects", []))
    out = [summary(p) for p in d.iterdir() if p.is_dir() and p.name not in hide and (p / "script.json").exists()] if d.exists() else []
    return jsonify(sorted(out, key=lambda s: -s["modified"]))

@app.get("/api/projects/<name>")
def project(name):
    p = proj_dir(name)
    s = summary(p)
    read = lambda f: (p / f).read_text(encoding="utf-8") if (p / f).exists() else ""
    s["sheet_text"] = read(f"{name}-youtube.txt")
    s["script"] = json.loads(read("script.json") or "[]")
    return jsonify(s)

@app.put("/api/projects/<name>/sheet")
def save_sheet(name):
    p = proj_dir(name)
    (p / f"{name}-youtube.txt").write_text(request.json["text"], encoding="utf-8")
    return jsonify(ok=True)

@app.put("/api/projects/<name>/script")
def save_script(name):
    p = proj_dir(name)
    lines = [s.strip() for s in request.json["sentences"] if s.strip()]
    (p / "script.json").write_text(json.dumps(lines, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return jsonify(ok=True)

@app.get("/media/<name>/<path:fname>")
def media(name, fname):
    p = proj_dir(name)
    if not re.match(r"^[\w.-]+\.(mp4|png|jpg|srt)$", fname): abort(400)
    return send_from_directory(p, fname)

ACTIONS = {   # what the buttons run: engine steps and uploader commands
    "voice": ("engine", ["voice"]), "check": ("engine", ["check"]), "video": ("engine", ["video"]),
    "thumb": ("engine", ["thumb"]), "sheet": ("engine", ["sheet"]), "new": ("engine", ["new"]),
    "upload-dry": ("uploader", ["upload", "--dry-run"]), "upload": ("uploader", ["upload"]), "comment": ("uploader", ["comment"]),
}

@app.post("/api/run")
def run():
    c, b = cfg(), request.json
    act, name = b.get("action"), b.get("project", "")
    if act == "auth":
        return jsonify(start_job("YouTube sign-in", [c["python"], c["uploader"], "auth"], str(ROOT)))
    if act == "status":
        return jsonify(start_job("Upload status", [c["python"], c["uploader"], "status"], str(ROOT)))
    if act not in ACTIONS or not SLUG.match(name): abort(400, "bad action or project")
    tool, args = ACTIONS[act]
    cmd = [c["python"], c[tool], args[0], name] + args[1:]
    if tool == "uploader" and act != "comment":
        if b.get("at"): cmd += ["--at", b["at"]]
        else: cmd += ["--slot", b.get("slot", "A"), "--date", b.get("date", "")]
    if act == "video" and b.get("no_music"): cmd.append("--no-music")
    return jsonify(start_job(f"{act} · {name}", cmd, str(ROOT)))

@app.post("/api/agent")
def agent():
    c = cfg()
    prompt = (request.json or {}).get("prompt", "").strip()
    if not prompt: abort(400, "empty prompt")
    return jsonify(start_job("agent · " + prompt[:50], list(c["agent_command"]) + [prompt], c["agent_cwd"]))


# ---------- schedule (read-only view of the planner) ----------
@app.get("/api/schedule")
def schedule():
    import openpyxl
    f = Path(cfg()["planner"])
    if not f.exists(): return jsonify(rows=[], error=f"no planner at {f}")
    ws = openpyxl.load_workbook(f, read_only=True, data_only=False)["Schedule"]
    head = [c.value for c in next(ws.iter_rows(min_row=3, max_row=3))]
    col = {h: i for i, h in enumerate(head) if h}
    rows, today = [], dt.date.today()
    for r in ws.iter_rows(min_row=4, values_only=True):
        d = r[col["Post date (IST)"]]
        if not isinstance(d, (dt.date, dt.datetime)): continue
        d = d.date() if isinstance(d, dt.datetime) else d
        if d < today - dt.timedelta(days=1): continue
        g = lambda h: r[col[h]] if h in col else None
        rows.append({"date": d.isoformat(), "day": d.strftime("%a"), "slot": g("Slot"), "time": g("Post time (IST)"),
                     "format": g("Format"), "type": g("Video type"), "title": g("Working title"), "status": g("Status"),
                     "notes": g("Notes")})
    return jsonify(rows=rows[:60])

@app.post("/api/open-planner")
def open_planner():
    os.startfile(cfg()["planner"])
    return jsonify(ok=True)


# ---------- settings ----------
@app.get("/api/config")
def get_config():
    return jsonify(cfg())

@app.put("/api/config")
def put_config():
    new = request.json
    if not isinstance(new, dict): abort(400)
    CONFIG.write_text(json.dumps(new, indent=2), encoding="utf-8")
    return jsonify(ok=True, note="restart the server to apply a new port")

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    c = cfg()
    url = f"http://127.0.0.1:{c['port']}"
    print(f"Bean Studio on {url}  (Ctrl+C to stop)")
    if c.get("open_browser"): threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=c["port"], debug=False, threaded=True)
