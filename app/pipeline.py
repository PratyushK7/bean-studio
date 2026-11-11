"""The Pipeline tab: one video's path from topic to upload, as stages the page shows and buttons that run them (Decoding Vyapaar).

A project is a folder in the channel's projects_dir:
    script.json  <slug>-check.txt  prompts/*.txt  images/NNN.ext  assets/  voice.*  <slug>.mp4  <slug>-youtube.txt  pipeline.json

Stage status is read from which files exist, never stored, so it cannot go stale. pipeline.json only remembers when the
current ChatGPT batch started (the "since" time used to collect downloads).

Who does what (shown on the page, and the model a stage's agent run uses): Opus for the judgment steps, Sonnet for the
mechanical ones. Images come from the user's own ChatGPT extension; the studio only collects the finished downloads.
register(app, ROOT, cfg, start_agent, JOBS, start_job) adds /api/pipeline*.
"""
import json, os, re, shutil, subprocess, time
from pathlib import Path
from flask import abort, jsonify, request

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
IMG = {".png", ".jpg", ".jpeg", ".webp"}
MODELS = {"topic": "opus", "research": "opus", "script": "opus", "packaging": "opus", "prompts": "sonnet", "shots": "sonnet",
          "build": "sonnet", "render": "sonnet", "checks": "haiku"}
STAGES = [("script", "Script"), ("check", "Checked"), ("prompts", "Prompts"), ("images", "Images"), ("assets", "Assets"),
          ("voice", "Voice"), ("render", "Video"), ("sheet", "Upload sheet")]
NEXT = {"script": "Write the script (the Script button runs it on Opus).",
        "check": "Run the script checker and fix every FAIL.",
        "prompts": "Make the ChatGPT prompt files (prompts/*.txt, one self-contained prompt per line).",
        "images": "Run the prompt files in your ChatGPT extension, then press Collect downloads.",
        "assets": "Cut the images apart and colour-match them into assets/.",
        "voice": "Make the Hindi voice with word timings.",
        "render": "Render the video.",
        "sheet": "Write the title, description and chapters, then upload from the Videos tab."}


def _files(p, pattern):
    return sorted(x for x in p.glob(pattern) if x.is_file())


def status(p):
    """{stage: detail or None}: None = not started, a short text = done / how far"""
    n = p.name
    out = {}
    sj = p / "script.json"
    words = 0
    if sj.exists():
        try: words = sum(len(str(l.get("hi", "")).split()) for l in json.loads(sj.read_text(encoding="utf-8")).get("lines", []))
        except Exception: words = 0
    out["script"] = f"{words} words" if words > 20 else None
    chk = next(iter(_files(p, "*-check.txt")), None)
    if chk:
        t = chk.read_text(encoding="utf-8", errors="replace")
        fails = len(re.findall(r"^\s*FAIL\b", t, re.M))
        out["check"] = "clean" if not fails else f"{fails} FAIL"
    else: out["check"] = None
    prompts = len({l.strip() for f in _files(p, "prompts/*.txt") for l in f.read_text(encoding="utf-8").splitlines() if l.strip()})   # distinct: an all-in-one file repeats the others
    out["prompts"] = f"{prompts} prompts" if prompts else None
    imgs = [f for f in (p / "images").glob("*") if f.suffix.lower() in IMG and not f.name.startswith("_")] if (p / "images").is_dir() else []
    out["images"] = (f"{len(imgs)} of {prompts}" if prompts else f"{len(imgs)}") if imgs else None
    assets = [f for f in (p / "assets").rglob("*") if f.is_file()] if (p / "assets").is_dir() else []
    out["assets"] = f"{len(assets)} files" if assets else None
    out["voice"] = ("ready · .srt" if any(_files(p, "*.srt")) else "ready") if any(_files(p, "voice.*")) or any(_files(p, "*.wav")) else None
    out["render"] = "ready" if any(_files(p, "*.mp4")) else None
    out["sheet"] = "ready" if (p / f"{n}-youtube.txt").exists() else None
    return out


def summary(p):
    st = status(p)
    nxt = next((k for k, _ in STAGES if not st[k] or (k == "check" and "FAIL" in st[k])), None)
    return {"name": p.name, "stages": [{"key": k, "label": lab, "state": st[k]} for k, lab in STAGES], "next": NEXT.get(nxt, "Everything is ready: upload it."),
            "next_key": nxt, "modified": max((f.stat().st_mtime for f in p.rglob("*") if f.is_file()), default=p.stat().st_mtime)}


def register(app, ROOT, cfg, start_agent, JOBS, start_job):
    def pdir(name):
        if not SLUG.match(name or ""): abort(400, "bad project name")
        p = Path(cfg()["projects_dir"]) / name
        if not p.is_dir(): abort(404, "no such project")
        return p

    def meta(p):
        try: return json.loads((p / "pipeline.json").read_text(encoding="utf-8"))
        except Exception: return {}

    def save_meta(p, m):
        (p / "pipeline.json").write_text(json.dumps(m, indent=1), encoding="utf-8")

    @app.get("/api/pipeline")
    def pipeline_list():
        d = Path(cfg()["projects_dir"])
        rows = [summary(p) for p in d.iterdir() if p.is_dir() and not p.name.startswith("_")] if d.exists() else []
        return jsonify(projects=sorted(rows, key=lambda r: -r["modified"]), models=MODELS, downloads=str(_downloads()))

    def _downloads():
        return Path(cfg().get("downloads_dir") or Path.home() / "Downloads")

    @app.post("/api/pipeline")
    def pipeline_new():
        slug = str((request.get_json(silent=True) or {}).get("slug", "")).strip()
        if not SLUG.match(slug): abort(400, "use lowercase letters, numbers and dashes")
        p = Path(cfg()["projects_dir"]) / slug
        if p.exists(): abort(400, "that project already exists")
        for sub in ("prompts", "images", "assets"): (p / sub).mkdir(parents=True)
        return jsonify(ok=True, name=slug)

    @app.get("/api/pipeline/<name>/prompts")
    def pipeline_prompts(name):
        p = pdir(name)
        files = [{"file": f.name, "path": str(f), "lines": [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]} for f in _files(p, "prompts/*.txt")]
        return jsonify(files=files, folder=str(p / "prompts"))

    @app.post("/api/pipeline/<name>/script")
    def pipeline_script(name):
        p = pdir(name)
        topic = str((request.get_json(silent=True) or {}).get("topic", "")).strip()
        if not topic: abort(400, "write the topic first")
        c = cfg()
        prompt = (f'Use the hindi-case-study skill (read ~/.claude/skills/hindi-case-study/SKILL.md) for the channel "{c["channel"]}". Topic: {topic}. '
                  f"The project folder is {p} (it exists; write script.json, the research file, the hooks file, the check output and the voice text there). "
                  "Run casecheck.py, fix every FAIL, and finish with the hand-back. Do not render anything and do not touch other projects.")
        return jsonify(start_agent(f"script · {name}", prompt, MODELS["script"], "feed"))

    @app.post("/api/pipeline/<name>/voice")
    def pipeline_voice(name):
        """the locked channel voice (Sarvam aditya, pace 0.92): script.json -> voice.mp3, voice-lines.json and <slug>.srt"""
        p = pdir(name)
        if not (p / "script.json").exists(): abort(400, "this video has no script.json yet")
        return jsonify(start_job(f"voice · {name}", [cfg()["python"], str(ROOT / "tools" / "vyapaar_voice.py"), str(p)], str(ROOT), unique=True))

    @app.post("/api/pipeline/<name>/batch")
    def pipeline_batch(name):
        """start: remember now. collect: copy every image that ChatGPT's extension downloaded since then into images/NNN.ext (copies; Downloads is left as it is)"""
        p = pdir(name)
        act = (request.get_json(silent=True) or {}).get("action")
        m = meta(p)
        if act == "start":
            m["since"] = time.time(); save_meta(p, m)
            return jsonify(ok=True, since=m["since"])
        if act != "collect": abort(400, "bad action")
        if not m.get("since"): abort(400, "press Start batch before you run the prompts in ChatGPT")
        dl = _downloads()
        found = sorted((f for f in dl.iterdir() if f.is_file() and f.suffix.lower() in IMG and f.stat().st_mtime >= m["since"] and f.stat().st_size > 60_000),
                       key=lambda f: f.stat().st_mtime) if dl.is_dir() else []
        (p / "images").mkdir(exist_ok=True)
        have = [f for f in (p / "images").iterdir() if f.stem.isdigit()]
        n = max([int(f.stem) for f in have], default=0)
        names = []
        for f in found:
            n += 1
            dest = p / "images" / f"{n:03d}{f.suffix.lower()}"
            shutil.copy2(f, dest); names.append(dest.name)
        m.setdefault("batches", []).append({"at": time.time(), "from": str(dl), "files": names}); save_meta(p, m)
        return jsonify(ok=True, collected=len(names), first=names[:1], last=names[-1:], downloads=str(dl))

    @app.post("/api/pipeline/<name>/contact")
    def pipeline_contact(name):
        """a numbered contact sheet of images/ (ffmpeg, 6 columns, up to 36 images) so a batch can be checked at a glance"""
        p = pdir(name)
        imgs = sorted(f for f in (p / "images").glob("*") if f.suffix.lower() in IMG and f.stem.isdigit()) if (p / "images").is_dir() else []
        if not imgs: abort(400, "no images collected yet")
        page = int((request.get_json(silent=True) or {}).get("page", 0))
        chunk = imgs[page * 36:(page + 1) * 36]
        if not chunk: abort(400, "no more images")
        cols, tw, th = 6, 320, 180
        cmd = ["ffmpeg", "-y", "-v", "error"]
        for f in chunk: cmd += ["-i", str(f)]
        filt = "".join(f"[{i}:v]scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=white,"
                       f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{f.stem}':x=6:y=4:fontsize=22:fontcolor=red:box=1:boxcolor=white@0.8[v{i}];" for i, f in enumerate(chunk))
        layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(chunk)))
        filt += "".join(f"[v{i}]" for i in range(len(chunk))) + f"xstack=inputs={len(chunk)}:layout={layout}:fill=white[o]"
        out = p / f"_contact-{page + 1}.jpg"       # in the project root: /media serves flat file names only
        r = subprocess.run(cmd + ["-filter_complex", filt, "-map", "[o]", "-frames:v", "1", "-q:v", "3", str(out)], capture_output=True, text=True)
        if r.returncode: abort(500, "ffmpeg could not build the sheet: " + r.stderr[-300:])
        return jsonify(ok=True, url=f"/media/{name}/{out.name}", pages=(len(imgs) + 35) // 36, count=len(imgs))

    @app.post("/api/pipeline/<name>/open")
    def pipeline_open(name):
        sub = str((request.get_json(silent=True) or {}).get("sub", "")).strip()
        target = (pdir(name) / sub).resolve()
        if pdir(name).resolve() not in (target, *target.parents): abort(400, "bad folder")
        if not target.is_dir(): abort(404, "no such folder")
        os.startfile(str(target))
        return jsonify(ok=True)
