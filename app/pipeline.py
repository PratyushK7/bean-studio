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
STAGES = [("script", "Script"), ("prompts", "Image prompts"), ("images", "Pictures"), ("voice", "Voice"), ("clips", "Clips"),
          ("sound", "Sound"), ("render", "Video"), ("sheet", "Upload sheet")]
BUILT = {"script", "prompts", "images", "voice", "sound"}        # steps with a working button; the rest say "coming next" instead of pretending
NEXT = {"script": "Write the script (Opus does it from your topic).",
        "prompts": "Make the image prompts from the script.",
        "images": "Run the prompt files in your ChatGPT extension, then collect the downloads.",
        "voice": "Make the Hindi voice (Sarvam, about 2 minutes, a few rupees).",
        "clips": "Animate the key shots (coming next: needs the xAI video step).",
        "sound": "Mix the music and sound effects under the voice.",
        "render": "Build the video (coming next).",
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
    chk = next(iter(_files(p, "*-check.txt")), None)
    fails = len(re.findall(r"^\s*FAIL\b", chk.read_text(encoding="utf-8", errors="replace"), re.M)) if chk else 0
    out["script"] = (f"{words} words" + (f" · {fails} FAIL" if fails else (" · checked" if chk else ""))) if words > 20 else None
    prompts = len({l.strip() for f in _files(p, "prompts/0*.txt") for l in f.read_text(encoding="utf-8").splitlines() if l.strip()})   # distinct: an all-in-one file repeats the others
    out["prompts"] = f"{prompts} prompts" if prompts else None
    imgs = [f for f in (p / "images").glob("*") if f.suffix.lower() in IMG and not f.name.startswith("_")] if (p / "images").is_dir() else []
    out["images"] = (f"{len(imgs)} of {prompts}" if prompts else f"{len(imgs)}") if imgs else None
    assets = [f for f in (p / "assets").rglob("*") if f.is_file()] if (p / "assets").is_dir() else []
    clips = [f for f in (p / "clips").glob("*.mp4")] if (p / "clips").is_dir() else []
    out["clips"] = f"{len(clips)} clips" if clips else None
    out["sound"] = "mixed" if any(_files(p, "mix*.mp3")) else None
    out["voice"] = ("ready · .srt" if any(_files(p, "*.srt")) else "ready") if (p / "voice.mp3").exists() else None
    out["render"] = "ready" if any(_files(p, "*.mp4")) else None
    out["sheet"] = "ready" if (p / f"{n}-youtube.txt").exists() else None
    return out


def summary(p):
    st = status(p)
    nxt = next((k for k, _ in STAGES if not st[k] or (k == "script" and "FAIL" in st[k])), None)
    hero = []
    try: hero = [l for l in json.loads((p / "script.json").read_text(encoding="utf-8")).get("lines", []) if l.get("kind") == "hero"]
    except Exception: pass
    secs = sum(max(2.0, min(5.0, len(str(l.get("hi", "")).split()) * 60 / 155 + 0.4)) for l in hero)
    return {"name": p.name, "stages": [{"key": k, "label": lab, "state": st[k], "built": k in BUILT} for k, lab in STAGES],
            "next": NEXT.get(nxt, "Everything is ready: upload it."), "next_key": nxt, "hero": len(hero), "hero_cost": round(secs * 0.032, 2),
            "modified": max((f.stat().st_mtime for f in p.rglob("*") if f.is_file()), default=p.stat().st_mtime)}


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

    @app.get("/api/pipeline/<name>/files")
    def pipeline_files(name):
        """the prompt files in run order with how many of their pictures are in (so the page can offer the next one)"""
        p = pdir(name); have = _have(p); idx = _index(p); out = []
        for f in _files(p, "prompts/0*.txt") + _files(p, "prompts/retry-*.txt"):
            ns = [e["n"] for e in idx if e.get("file") == f.name or f.name == "retry-" + e.get("file", "")]
            out.append({"file": f.name, "slots": len(ns) if not f.name.startswith("retry-") else len([l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]),
                        "done": sum(1 for n in ns if n in have) if not f.name.startswith("retry-") else 0, "retry": f.name.startswith("retry-")})
        return jsonify(files=out)

    @app.get("/api/pipeline/<name>/prompts")
    def pipeline_prompts(name):
        p = pdir(name)
        files = [{"file": f.name, "path": str(f), "lines": [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]} for f in _files(p, "prompts/0*.txt")]
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

    @app.post("/api/pipeline/<name>/make-prompts")
    def pipeline_make_prompts(name):
        """script.json -> prompts/*.txt and images-index.json (tools/vyapaar_prompts.py); quick, so it runs here and returns its summary"""
        p = pdir(name)
        if not (p / "script.json").exists(): abort(400, "this video has no script.json yet")
        r = subprocess.run([cfg()["python"], str(ROOT / "tools" / "vyapaar_prompts.py"), str(p)], capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONUTF8": "1"})
        if r.returncode: abort(500, (r.stderr or r.stdout)[-300:])
        return jsonify(ok=True, summary=r.stdout.strip())

    @app.post("/api/pipeline/<name>/sound")
    def pipeline_sound(name):
        """voice + music moods + ambience + sound effects -> mix.mp3 (tools/vyapaar_mix.py; synthesised placeholders unless real tracks are in audio/)"""
        p = pdir(name)
        if not (p / "voice.mp3").exists() or not (p / "voice-lines.json").exists(): abort(400, "make the voice first (the mix is timed from it)")
        return jsonify(start_job(f"sound · {name}", [cfg()["python"], str(ROOT / "tools" / "vyapaar_mix.py"), str(p)], str(ROOT), unique=True))

    def _index(p):
        f = p / "images-index.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []

    def _slots(p, fname):
        if fname.startswith("retry-"):                       # a retry file: the slots of the original file whose picture is still missing
            have = _have(p); return [e for e in _index(p) if e.get("file") == fname[6:] and e["n"] not in have]
        return [e for e in _index(p) if e.get("file") == fname]

    def _have(p):
        return {int(f.stem) for f in (p / "images").iterdir() if f.stem.isdigit() and f.suffix.lower() in IMG} if (p / "images").is_dir() else set()

    @app.post("/api/pipeline/<name>/batch")
    def pipeline_batch(name):
        """Pictures, matched per prompt file so a failed prompt cannot shift the rest.
        collect {file}: picks up the new downloads (everything since the prompts were made or the last collect) into images/_pending, then
            - the count equals the file's prompts: they are filed under the right picture numbers at once;
            - fewer: nothing is filed yet, the answer lists the slots so the user says which ones failed (assign);
            - more: the extra pictures are listed too (a double download): the user says which slots to skip, or removes files.
        assign {file, missing:[slot numbers in that file]}: files the pending pictures in order into the other slots and writes retry-<file> with the missing prompts.
        swap {a, b}: swaps two picture numbers (the extension finished two out of order)."""
        p = pdir(name)
        b = request.get_json(silent=True) or {}
        act = b.get("action")
        m = meta(p)
        (p / "images").mkdir(exist_ok=True); pend = p / "images" / "_pending"
        if act == "swap":
            x, y = int(b.get("a", 0)), int(b.get("b", 0))
            fx = next((f for f in (p / "images").iterdir() if f.stem == f"{x:03d}"), None); fy = next((f for f in (p / "images").iterdir() if f.stem == f"{y:03d}"), None)
            if not fx or not fy: abort(400, "both picture numbers must exist")
            tmp = fx.with_name("_swap" + fx.suffix); fx.rename(tmp)
            fx2 = fx.with_name(f"{y:03d}{fx.suffix}"); fy2 = fy.with_name(f"{x:03d}{fy.suffix}")
            fy.rename(fy2); tmp.rename(fx2)
            return jsonify(ok=True, swapped=[x, y])
        fname = str(b.get("file") or "")
        slots = _slots(p, fname)
        if not slots: abort(400, "pick which prompt file you just ran (the list shows the files)")
        if act == "collect":
            marker = p / "images-index.json"
            since = max(m.get("since") or 0, marker.stat().st_mtime if marker.exists() else 0)
            if not since: abort(400, "make the image prompts first")
            dl = _downloads()
            found = sorted((f for f in dl.iterdir() if f.is_file() and f.suffix.lower() in IMG and f.stat().st_mtime > since and f.stat().st_size > 60_000),
                           key=lambda f: f.stat().st_mtime) if dl.is_dir() else []
            if not found: return jsonify(ok=True, state="none", collected=0, expected=len(slots), total=len(_have(p)))
            pend.mkdir(exist_ok=True)
            for old in pend.iterdir(): old.unlink()                      # a new collect replaces an unresolved earlier one (the downloads are still in Downloads)
            for k, f in enumerate(found, 1): shutil.copy2(f, pend / f"p{k:03d}{f.suffix.lower()}")
            m["pending_max"] = max(f.stat().st_mtime for f in found); save_meta(p, m)       # "since" only moves when the pictures are filed, so a mismatch can be retried
            return _file_pending(p, name, fname, slots, m)
        if act == "assign":
            missing = {int(x) for x in b.get("missing", [])}
            todo = [e for e in slots if e["pos"] not in missing]
            pics = sorted(pend.iterdir()) if pend.is_dir() else []
            if len(pics) != len(todo): abort(400, f"{len(pics)} pictures for {len(todo)} slots: check the slot numbers you marked as failed")
            return _file_pending(p, name, fname, slots, m, [e["pos"] for e in slots if e["pos"] in missing], force=True)
        abort(400, "bad action")

    def _file_pending(p, name, fname, slots, m, missing=None, force=False):
        pend = p / "images" / "_pending"
        pics = sorted(pend.iterdir()) if pend.is_dir() else []
        missing = missing or []
        todo = [e for e in slots if e["pos"] not in missing]
        if len(pics) != len(todo) and not force:
            return jsonify(ok=True, state="mismatch", collected=len(pics), expected=len(slots), total=len(_have(p)),
                           slots=[{"pos": e["pos"], "n": e["n"], "text": re.sub(r"\s+", " ", e["prompt"])[:70]} for e in slots],
                           sheet=f"/media/{name}/{_pending_sheet(p, pics)}")
        for e, f in zip(todo, pics):
            for old in (p / "images").glob(f"{e['n']:03d}.*"): old.unlink()          # a redone picture replaces the earlier one
            shutil.move(str(f), p / "images" / f"{e['n']:03d}{f.suffix.lower()}")
        for f in pend.glob("*"): f.unlink()
        if m.get("pending_max"): m["since"] = m.pop("pending_max")
        retry = None
        if missing:
            retry = "retry-" + (fname[6:] if fname.startswith("retry-") else fname)
            (p / "prompts" / retry).write_text("\n".join(e["prompt"] for e in slots if e["pos"] in missing) + "\n", encoding="utf-8")
        m.setdefault("batches", []).append({"at": time.time(), "file": fname, "files": [f"{e['n']:03d}" for e in todo], "missing": missing}); save_meta(p, m)
        return jsonify(ok=True, state="filed", collected=len(todo), expected=len(slots), missing=missing, retry=retry, total=len(_have(p)))

    def _pending_sheet(p, pics):
        cols, tw, th = 6, 320, 180
        cmd = ["ffmpeg", "-y", "-v", "error"]
        for f in pics: cmd += ["-i", str(f)]
        filt = "".join(f"[{i}:v]scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=white,"
                       f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{i + 1}':x=6:y=4:fontsize=26:fontcolor=red:box=1:boxcolor=white@0.85[v{i}];" for i, f in enumerate(pics))
        layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(pics)))
        filt += ("[v0]null[o]" if len(pics) == 1 else "".join(f"[v{i}]" for i in range(len(pics))) + f"xstack=inputs={len(pics)}:layout={layout}:fill=white[o]")   # xstack needs two or more inputs
        out = p / "_pending-sheet.jpg"
        r = subprocess.run(cmd + ["-filter_complex", filt, "-map", "[o]", "-frames:v", "1", "-q:v", "3", str(out)], capture_output=True, text=True)
        if r.returncode: abort(500, "ffmpeg could not build the sheet: " + r.stderr[-300:])
        return out.name

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
        filt += ("[v0]null[o]" if len(chunk) == 1 else "".join(f"[v{i}]" for i in range(len(chunk))) + f"xstack=inputs={len(chunk)}:layout={layout}:fill=white[o]")   # xstack needs two or more inputs
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
