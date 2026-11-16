"""The Pipeline tab: one video's path from topic to upload, as stages the page shows and buttons that run them (Decoding Vyapaar).

A project is a folder in the channel's projects_dir:
    script.json  <slug>-check.txt  prompts/*.txt  images/NNN.ext  assets/  voice.*  <slug>.mp4  <slug>-youtube.txt  pipeline.json

Stage status is read from which files exist, never stored, so it cannot go stale. pipeline.json only remembers when the
current ChatGPT batch started (the "since" time used to collect downloads).

Who does what (shown on the page, and the model a stage's agent run uses): Opus for the judgment steps, Haiku for the
mechanical ones. Images come from the user's own ChatGPT extension; the studio only collects the finished downloads.
register(app, ROOT, cfg, start_agent, JOBS, start_job) adds /api/pipeline*.
"""
import json, os, re, shutil, subprocess, time
from pathlib import Path
from flask import abort, jsonify, request, send_file

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
IMG = {".png", ".jpg", ".jpeg", ".webp"}
# Opus only where the decision matters (the story, the visual plan, judging pictures and the sample); Haiku runs the mechanical steps
MODELS = {"topic": "opus", "research": "opus", "script": "opus", "packaging": "opus", "visual_plan": "opus", "review": "opus",
          "prompts": "haiku", "images": "haiku", "upscale": "haiku", "shots": "haiku", "build": "haiku", "render": "haiku", "checks": "haiku"}
STAGES = [("script", "Script"), ("prompts", "Image prompts"), ("images", "Pictures"), ("voice", "Voice"), ("clips", "Clips"),
          ("sound", "Sound"), ("render", "Video"), ("sheet", "Upload sheet")]          # the older, simpler path: projects without a visual plan
# The art-directed documentary pipeline (references/production.md): a visual plan, pictures with a review gate, a sample with a second gate, then the full cut
NEW_STAGES = [("script", "Script"), ("plan", "Visual plan"), ("prompts", "Image prompts"), ("images", "Pictures"), ("review", "Check the pictures"),
              ("upscale", "Sharpen (upscale)"), ("voice", "Voice"), ("clips", "Hero clips"), ("sample", "Sample"), ("video", "Full video"), ("sheet", "Upload sheet")]
OPTIONAL = {"clips"}                                         # never the "next step": the video is complete without them
STEPS = {"plan-check", "prompts", "pictures", "check-pictures", "upscale", "voice-free", "voice-pro", "sample", "check-sample", "approve-sample", "full"}   # tools/vyapaar_steps.py
SYNC_STEPS = {"plan-check"}                                  # quick enough to answer on the spot
PAID_STEPS = {"voice-pro"}                                   # needs the owner's OK on the cost, sent as confirm_cost
SUBS = {"qa", "review", "graphics"}                          # project subfolders whose pictures the page may show
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


def _j(f, default=None):
    try: return json.loads(Path(f).read_text(encoding="utf-8"))
    except Exception: return default


def tools_python():
    """the vyapaar tools need numpy, OpenCV and Pillow, which the studio's own .venv does not have: use the system Python they were built on"""
    c = Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "python.exe"
    return str(c) if c.exists() else None


def _have_files(p):
    return {int(f.stem) for f in (p / "images").iterdir() if f.stem.isdigit() and f.suffix.lower() in IMG} if (p / "images").is_dir() else set()


def status_new(p):
    """{stage: (detail or None, warn)} for the documentary pipeline. Read from files, never stored, and a file made for an OLDER script says so."""
    base = status(p); out = {}
    script = _j(p / "script.json", {}); nlines = len(script.get("lines", []))
    out["script"] = (base["script"], "FAIL" in (base["script"] or ""))
    plan = _j(p / "visual-plan.json")
    out["plan"] = ((f"{len(plan.get('shots', []))} shots · {sum(1 for x in plan.get('shots', []) if x.get('kind') == 'graphic')} graphics", False) if plan else (None, False))
    idx = _j(p / "images-index.json", [])
    used = [e for e in idx if e.get("type") in ("scene", "character")]
    own = [e for e in used if e.get("status") not in ("skip", "reused")]
    out["prompts"] = ((f"{len(own)} prompts", False) if own else (base["prompts"], False))        # the plan's prompts, not just the ones still waiting
    have = _have_files(p)
    review = _j(p / "review.json", {})
    out["images"] = ((f"{sum(1 for e in own if e['n'] in have)} of {len(own)} made", False) if have else (None, False))
    appr = sum(1 for e in used if (review.get(str(e["n"])) or {}).get("status") == "approved")
    out["review"] = ((("Gate 1 open · " if used and appr == len(used) else "") + f"{appr} of {len(used)} approved", False) if review and used else (None, False))
    hd = sum(1 for e in used if (p / "images-hd" / f"{e['n']:03d}.png").exists())
    out["upscale"] = ((f"{hd} of {appr}", False) if appr else (None, False))
    vl, pl = _j(p / "voice-lines.json"), _j(p / "preview-local-lines.json")
    if vl and (p / "voice.mp3").exists() and len(vl) == nlines: out["voice"] = ("Sarvam voice ready", False)
    elif pl and (p / "preview-local.mp3").exists() and len(pl) == nlines: out["voice"] = ("free voice ready (Kokoro)", False)
    elif (p / "voice.mp3").exists() or (p / "preview-local.mp3").exists(): out["voice"] = ("voice is for an older script", True)
    else: out["voice"] = (None, False)
    cp, ca = _j(p / "clips-plan.json", {}), _j(p / "clips" / "approved.json", {})
    n_ok = len(ca.get("clips", ca) if isinstance(ca, dict) else ca) if ca else 0
    out["clips"] = ((f"{n_ok} approved", False) if n_ok else ((f"{len(cp.get('clips', []))} planned · about ${cp.get('cost_estimate', '?')} · not made", False) if cp.get("clips") else (None, False)))
    g2 = _j(p / "gate2.json", {})
    if g2.get("approved"): out["sample"] = (f"Gate 2 approved · {g2.get('at', '')}", False)
    elif (p / "sample.mp4").exists(): out["sample"] = ("made, not approved yet", False)
    else: out["sample"] = (None, False)
    vids = sorted((f for f in p.glob("video*.mp4") if "-prev-" not in f.name and "oldgraphics" not in f.name), key=lambda f: f.stat().st_mtime)
    if vids:
        v = vids[-1]; qa = _j(p / "qa" / f"{v.stem}-qa.json", {})
        old = (p / "script.json").exists() and v.stat().st_mtime < (p / "script.json").stat().st_mtime
        verdict = (qa.get("verdict") or "not checked yet").lower()
        out["video"] = ((f"{v.name} is older than the script" if old else f"{v.name} · {verdict}"), old or verdict.startswith("fail"))
    else: out["video"] = (None, False)
    out["sheet"] = (base["sheet"], False)
    return out


NEXT_NEW = {"script": "Write the script (Opus does it from your topic).",
            "plan": "Write the visual plan: who is in every shot, the light, the camera (Opus, from the script).",
            "prompts": "Make the picture prompts from the plan.",
            "images": "Make the pictures in ChatGPT (runs by itself through BrowserOS neo).",
            "review": "Check the pictures: approve the good ones, send the bad ones back.",
            "upscale": "Sharpen the approved pictures (free, on your graphics card).",
            "voice": "Make the voice: the free one first, the paid Sarvam one later.",
            "sample": "Make a short sample and check it before the full video.",
            "video": "Make the full video (free).",
            "sheet": "Write the title, description and chapters, then upload from the Videos tab."}


def summary(p, hindi=False):
    if hindi or (p / "visual-plan.json").exists():
        st = status_new(p)
        stages = [{"key": k, "label": lab, "state": st[k][0], "warn": st[k][1], "built": True, "optional": k in OPTIONAL} for k, lab in NEW_STAGES]
        for x in stages:                                       # an optional step that is only planned is a note, not a finished step
            if x["optional"] and x["state"] and "not made" in x["state"]: x["note"], x["state"] = x["state"], None
        nxt = next((x["key"] for x in stages if not x["optional"] and (not x["state"] or x["warn"])), None)
        return {"name": p.name, "new": True, "stages": stages, "next_key": nxt, "next": NEXT_NEW.get(nxt, "Everything is ready: upload it."), "hero": 0, "hero_cost": 0,
                "modified": max((f.stat().st_mtime for f in p.rglob("*") if f.is_file() and "render-cache" not in f.parts and "images-hd" not in f.parts), default=p.stat().st_mtime)}
    st = status(p)
    nxt = next((k for k, _ in STAGES if not st[k] or (k == "script" and "FAIL" in st[k])), None)
    hero = []
    try: hero = [l for l in json.loads((p / "script.json").read_text(encoding="utf-8")).get("lines", []) if l.get("kind") == "hero"]
    except Exception: pass
    secs = sum(max(2.0, min(5.0, len(str(l.get("hi", "")).split()) * 60 / 155 + 0.4)) for l in hero)
    return {"name": p.name, "new": False, "stages": [{"key": k, "label": lab, "state": st[k], "built": k in BUILT} for k, lab in STAGES],
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
        hindi = cfg().get("language") == "Hindi"
        rows = [summary(p, hindi) for p in d.iterdir() if p.is_dir() and not p.name.startswith("_")] if d.exists() else []
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
                  f"The project folder is {p} (it exists; write the research, engine, beats and hooks files, script.json with its loop ledger and fact ids, the check output, "
                  "the voice text and the readable <slug>-script.md (casecheck.py --md) there). "
                  "Run casecheck.py, fix every FAIL, never add a line only to satisfy the checker, run the independent editor's score (step 10, <slug>-score.md) "
                  "and fix only the weak areas, and finish with the hand-back. Do not render anything and do not touch other projects.")
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

    # ---------------------------------------------------------------- the documentary pipeline (tools/vyapaar_steps.py and friends)
    def _tools_py():
        py = tools_python()
        if not py: abort(500, "the vyapaar tools need the system Python 3.12 with numpy and OpenCV (not found)")
        return py

    @app.post("/api/pipeline/<name>/step")
    def pipeline_step(name):
        """one button = one tools/vyapaar_steps.py step, run as a background job (follow it in the Activity tab). Paid steps need confirm_cost."""
        p = pdir(name); b = request.get_json(silent=True) or {}; step = str(b.get("step") or "")
        if step not in STEPS: abort(400, "unknown step")
        if step in PAID_STEPS and not b.get("confirm_cost"): abort(400, "this step is paid: say OK to the cost first")
        cmd = [_tools_py(), str(ROOT / "tools" / "vyapaar_steps.py"), str(p), step]
        if step in SYNC_STEPS:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT), env={**os.environ, "PYTHONUTF8": "1"}, timeout=300)
            return jsonify(ok=r.returncode == 0, output=(r.stdout + r.stderr).strip()[-1800:])
        return jsonify(start_job(f"{step} · {name}", cmd, str(ROOT), unique=True))

    @app.post("/api/pipeline/<name>/plan")
    def pipeline_plan(name):
        """Opus writes visual-plan.json from the approved script (the art director's job): the one judgment step before any picture exists"""
        p = pdir(name)
        if not (p / "script.json").exists(): abort(400, "this video has no script.json yet")
        c = cfg()
        prompt = (f'Use the hindi-case-study skill (read ~/.claude/skills/hindi-case-study/SKILL.md and references/production.md, "1. The visual plan") for the channel "{c["channel"]}". '
                  f"The project folder is {p}. Write visual-plan.json against the channel's visual-bible.json (copy the structure of an existing project's build_visual_plan.py if one exists): "
                  "characters with sheets, locations, and one shot per picture or graphic, with the light following the story's clock, a face on every share-taker, the hook spending the strongest pictures, "
                  "and every graphic number traced to a research row. Then run `python tools/vyapaar_steps.py <project> plan-check` and fix every critical issue. "
                  "Do not make any pictures, do not run ChatGPT, and do not touch other projects.")
        return jsonify(start_agent(f"visual plan · {name}", prompt, MODELS["visual_plan"], "feed"))

    @app.get("/api/pipeline/<name>/review")
    def pipeline_review(name):
        """Gate 1 for the page: counts, whether the gate is open, and every picture still waiting for a decision with its flags and script line"""
        p = pdir(name)
        r = subprocess.run([_tools_py(), str(ROOT / "tools" / "vyapaar_review.py"), str(p), "status"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           cwd=str(ROOT), env={**os.environ, "PYTHONUTF8": "1"}, timeout=240)
        line = next((l for l in reversed(r.stdout.splitlines()) if l.startswith("{")), "")
        if not line: abort(500, "could not read the review state: " + (r.stderr or r.stdout)[-300:])
        return jsonify(json.loads(line))

    @app.post("/api/pipeline/<name>/review")
    def pipeline_review_act(name):
        """approve / reject / pick, exactly as vyapaar_review.py does them (a rejected picture is kept in images/_rejected and only that slot is remade)"""
        p = pdir(name); b = request.get_json(silent=True) or {}; act = b.get("action"); nums = str(b.get("numbers") or "").strip()
        if act not in ("approve", "reject", "pick") or not re.fullmatch(r"[0-9, \-]+", nums): abort(400, "say approve, reject or pick and the picture numbers, like 12 or 3,5-9")
        cmd = [_tools_py(), str(ROOT / "tools" / "vyapaar_review.py"), str(p), act, nums.replace(" ", "")]
        if act == "pick": cmd.append(str(b.get("which") or "b")[:1])
        note = str(b.get("note") or "").strip()[:300]
        if note and act != "pick": cmd += ["--note", note]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT), env={**os.environ, "PYTHONUTF8": "1"}, timeout=120)
        if r.returncode: abort(500, (r.stderr or r.stdout)[-300:])
        return jsonify(ok=True, output=r.stdout.strip()[-600:])

    @app.get("/api/pipeline/<name>/pic/<int:n>")
    def pipeline_pic(name, n):
        """a 960 px preview of images/NNN.* (the originals are 2 MB each; the page shows many at once)"""
        p = pdir(name)
        src = next((f for f in (p / "images").glob(f"{n:03d}.*") if f.suffix.lower() in IMG), None)
        if not src: abort(404, "no such picture")
        out = p / "review" / "thumbs" / f"{n:03d}.jpg"
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            out.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=960:-2", "-q:v", "4", str(out)], capture_output=True, text=True)
            if r.returncode: abort(500, "could not make the preview: " + r.stderr[-200:])
        return send_file(out, mimetype="image/jpeg")

    @app.get("/api/pipeline/<name>/asset/<sub>/<fname>")
    def pipeline_asset(name, sub, fname):
        """a picture from qa/, review/ or graphics/ (contact sheets, shot sheets, graphic previews)"""
        p = pdir(name)
        if sub not in SUBS or not re.fullmatch(r"[\w.-]+\.(jpg|png)", fname): abort(400)
        f = p / sub / fname
        if not f.is_file(): abort(404)
        return send_file(f)

    @app.get("/api/pipeline/<name>/outputs")
    def pipeline_outputs(name):
        """what to look at: the sample and the full video (played through /media), the QA verdicts and sheets, the review contact sheets, the gates"""
        p = pdir(name); out = {"videos": [], "sheets": [], "review_sheets": []}
        for f in sorted(p.glob("*.mp4"), key=lambda f: -f.stat().st_mtime):
            if "-prev-" in f.name or "oldgraphics" in f.name or f.name.startswith(("test-", "sample-v")): continue
            qa = _j(p / "qa" / f"{f.stem}-qa.json", {}); issues = qa.get("issues", {})
            sj = p / "script.json"
            out["videos"].append({"file": f.name, "url": f"/media/{name}/{f.name}", "mb": round(f.stat().st_size / 1e6), "verdict": qa.get("verdict"),
                                  "stale": sj.exists() and f.stat().st_mtime < sj.stat().st_mtime,
                                  "fail": issues.get("fail", []), "warn": issues.get("warn", []),
                                  "shots": f"/api/pipeline/{name}/asset/qa/{f.stem}-shots.jpg" if (p / "qa" / f"{f.stem}-shots.jpg").exists() else None,
                                  "strips": f"/api/pipeline/{name}/asset/qa/{f.stem}-strips.jpg" if (p / "qa" / f"{f.stem}-strips.jpg").exists() else None})
        rv = p / "review"
        out["review_sheets"] = [{"file": f.name, "url": f"/api/pipeline/{name}/asset/review/{f.name}"} for f in sorted(rv.glob("*.jpg"))] if rv.is_dir() else []
        out["gate2"] = _j(p / "gate2.json", {})
        out["srt"] = [f.name for f in p.glob("*.srt")]
        return jsonify(out)

    @app.post("/api/pipeline/<name>/open")
    def pipeline_open(name):
        sub = str((request.get_json(silent=True) or {}).get("sub", "")).strip()
        target = (pdir(name) / sub).resolve()
        if pdir(name).resolve() not in (target, *target.parents): abort(400, "bad folder")
        if not target.is_dir(): abort(404, "no such folder")
        os.startfile(str(target))
        return jsonify(ok=True)
