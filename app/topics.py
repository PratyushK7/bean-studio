"""Topic selector + video generator for Bean Studio.

1. Finds what is working on other channels in the same category: public Shorts listings (yt-dlp, no login), each video scored
   as a multiple of its own channel's median views, so a big channel's normal day doesn't look like a hit.
2. "Get 5 ideas": a sample of the best outliers goes to the agent, which adapts five of them into ORIGINAL topics for this
   channel (topic and format borrowed, never the script or title). "Re-roll" samples a fresh set, skipping sources already shown.
3. A chosen topic + the answers from the form become one agent job that runs the whole line-boil pipeline.

register(app, ROOT, cfg, start_job, JOBS) adds /api/topics*.
"""
import concurrent.futures as cf, datetime as dt, difflib, json, random, re, statistics, subprocess, sys, threading, time, uuid
from pathlib import Path
from flask import abort, jsonify, request

TYPES = ["What if", "Myth test", "Why", "True story", "Versus", "Ranking", "Levels", "Paradox", "Puzzle",
         "How it works", "Superlative", "How many", "Map/scale"]
FMT = [("What if", r"^what if|^what would happen|^what happens"), ("How many", r"^how (many|much|long|far|big|fast|hot|cold|deep|high|old)"),
       ("Versus", r"\bvs\.?\b|versus"), ("Levels", r"\blevels?\b"), ("Paradox", r"paradox"), ("Ranking", r"ranking|ranked|top \d+|\bworst\b"),
       ("Puzzle", r"which .* (first|more|faster)|puzzle|riddle|can you (guess|solve)"),
       ("How it works", r"^how (do|does|did|is|are|was|to)\b|how .* works?"), ("Why", r"^why\b|\bwhy\b"),
       ("Superlative", r"\b(most|deadliest|largest|biggest|smallest|fastest|strongest|oldest|longest|rarest|sharpest)\b"),
       ("Map/scale", r"further|bigger than|smaller than|size of|\bmap\b"),
       ("True story", r"\b(1[0-9]{3}|20[0-2][0-9])\b|\bstory\b|history|disaster|incident|what happened"),
       ("Myth test", r"^(is|are|can|could|does|do)\b|myth|actually|really|truth")]
OFF_BRAND = re.compile(r"soldier|military|bomber|\bwar\b|russia|ukrain|israel|taliban|\bgun\b|shot\b|kill|murder|suicide|\bsex|porn|terror|nazi|trump|biden", re.I)
STOP = set("what if you your the a an of to how would it take and is are do does why can could in on for with from at".split())
VOICES = ["af_heart", "am_michael", "bf_emma", "bm_george"]


def classify(title):
    for name, pat in FMT:
        if re.search(pat, title, re.I): return name
    return "Other"


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def too_close(title, others, cutoff=0.72):
    t = norm(title)
    return any(difflib.SequenceMatcher(None, t, norm(o)).ratio() >= cutoff for o in others)


def clean(s, n=500):
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(s or "")).strip()[:n]


def register(app, ROOT, cfg, start_job, JOBS):
    DATA = ROOT / "data"
    POOL, STATEF = DATA / "topic-pool.json", DATA / "topic-state.json"
    st = {"refreshing": False, "progress": "", "error": None, "batches": {}}
    lock = threading.Lock()

    def load_json(p, default):
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: return default

    def save_json(p, obj):
        DATA.mkdir(exist_ok=True); p.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---------- 1. the pool of outliers ----------
    def fetch_channel(handle):
        url = f"https://www.youtube.com/@{handle.lstrip('@')}/shorts"
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "50", "--no-warnings", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        d = json.loads(r.stdout)
        ents = [e for e in (d.get("entries") or []) if e and e.get("view_count")]
        if len(ents) < 8: return []
        med = statistics.median(e["view_count"] for e in ents)
        name = d.get("channel") or d.get("uploader") or handle
        out = []
        for e in ents:
            t = re.sub(r"\s*#\S+", "", e.get("title", "")).strip()
            out.append({"id": e["id"], "title": t, "channel": name, "views": e["view_count"], "multiple": round(e["view_count"] / med, 2),
                        "type": classify(t), "duration": e.get("duration"), "url": f"https://www.youtube.com/shorts/{e['id']}"})
        return out

    def refresh_pool():
        with lock:
            st.update(refreshing=True, error=None, progress="starting")
            chans = cfg().get("topic_channels", [])
            vids, done, failed = [], 0, []
            try:
                with cf.ThreadPoolExecutor(6) as ex:
                    futs = {ex.submit(fetch_channel, h): h for h in chans}
                    for f in cf.as_completed(futs):
                        done += 1; st["progress"] = f"{done}/{len(chans)} channels"
                        try: vids += f.result()
                        except Exception: failed.append(futs[f])
                if not vids: raise RuntimeError("no videos came back; check your internet connection or the channel handles in Settings")
                save_json(POOL, {"fetched": dt.datetime.now().isoformat(timespec="seconds"), "videos": vids, "failed": failed})
            except Exception as e:
                st["error"] = str(e)[:300]
            finally:
                st.update(refreshing=False, progress="")

    # ---------- 2. five ideas, and re-roll ----------
    def already_made():
        c = cfg(); names = []
        for sheet in Path(c["projects_dir"]).glob("*/*-youtube.txt"):
            m = re.search(r"== TITLE ==\s*\n(.+)", sheet.read_text(encoding="utf-8"))
            if m: names.append(m.group(1).strip())
        names += [p.name.replace("-", " ") for p in Path(c["projects_dir"]).iterdir() if p.is_dir()]
        try:
            import openpyxl
            ws = openpyxl.load_workbook(c["planner"], read_only=True, data_only=True)["Schedule"]
            head = [x.value for x in next(ws.iter_rows(min_row=3, max_row=3))]
            ti = head.index("Working title")
            names += [str(r[ti]) for r in ws.iter_rows(min_row=4, values_only=True) if r[ti]]
        except Exception: pass
        try:
            import ytstate
            names += [v["title"] for v in ytstate.STATE["videos"]]
        except Exception: pass
        return names

    def pick_candidates(pool, seen, made, k=14):
        def ok(v, floor):
            return v["multiple"] >= floor and not OFF_BRAND.search(v["title"]) and not too_close(v["title"], made)
        for floor in (1.5, 1.2, 1.0):            # relax if the pool is small (few channels)
            cands = [v for v in pool if ok(v, floor) and v["id"] not in seen]
            if len(cands) < 8:                   # shown everything good at this level: start over
                cands = [v for v in pool if ok(v, floor)]
                seen.clear()
            if len(cands) >= 5: break
        cands.sort(key=lambda v: -v["multiple"] * random.uniform(0.6, 1.4))
        chosen, per_type = [], {}
        for v in cands[:80]:
            cap = 6 if v["type"] == "Other" else 3
            if per_type.get(v["type"], 0) >= cap: continue
            per_type[v["type"]] = per_type.get(v["type"], 0) + 1; chosen.append(v)
            if len(chosen) >= k: break
        if len(chosen) < 10:                     # too few types in the pool for the per-type cap: top up without it
            chosen += [v for v in cands if v not in chosen][:10 - len(chosen)]
        return chosen

    def finish_batch(b):
        """read the agent's answer; fall back to the raw best outliers if it didn't produce one"""
        opts = None
        try:
            opts = json.loads(Path(b["out"]).read_text(encoding="utf-8")) if Path(b["out"]).exists() else None
        except Exception: opts = None
        if not opts:
            j = JOBS.get(b["job"]); text = "\n".join(j["log"]) if j else ""
            m = re.search(r"\[\s*\{.*\}\s*\]", text, re.S)
            try: opts = json.loads(m.group(0)) if m else None
            except Exception: opts = None
        good = []
        for o in (opts or []):
            if isinstance(o, dict) and o.get("title"):
                o["type"] = o.get("type") if o.get("type") in TYPES else "Other"
                for k in ("promise", "visual", "fact_note"): o[k] = clean(o.get(k), 300)
                o["fact_risk"] = o.get("fact_risk") if o.get("fact_risk") in ("low", "medium", "high") else "medium"
                o["adapted"] = True; good.append(o)
        if len(good) < 5:                         # fill up (or replace) with the raw outliers, clearly marked
            for c in b["candidates"]:
                if len(good) >= 5: break
                good.append({"title": c["title"], "type": c["type"], "promise": "", "visual": "", "fact_risk": "medium", "fact_note": "",
                             "inspired_by": {"title": c["title"], "channel": c["channel"], "multiple": c["multiple"], "url": c["url"]}, "adapted": False})
        for i, o in enumerate(good[:5]): o["n"] = i
        b["options"], b["status"] = good[:5], "ready"

    @app.get("/api/topics")
    def topics_get():
        pool = load_json(POOL, None)
        return jsonify(refreshing=st["refreshing"], progress=st["progress"], error=st["error"],
                       fetched=pool and pool["fetched"], videos=pool and len(pool["videos"]), failed=pool and pool.get("failed", []),
                       channels=cfg().get("topic_channels", []), category=cfg().get("topic_category", ""),
                       top=(pool and sorted(pool["videos"], key=lambda v: -v["multiple"])[:8]) or [])

    @app.post("/api/topics/refresh")
    def topics_refresh():
        if not st["refreshing"]: threading.Thread(target=refresh_pool, daemon=True).start()
        return jsonify(ok=True)

    @app.post("/api/topics/options")
    def topics_options():
        pool = load_json(POOL, None)
        if not pool: abort(400, "no source data yet: press 'Refresh sources' first")
        state = load_json(STATEF, {"seen": []})
        seen = set(state["seen"]); made = already_made()
        cands = pick_candidates(pool["videos"], seen, made)
        if len(cands) < 5: abort(400, f"only {len(cands)} usable source videos out of {len(pool['videos'])} (after removing topics you already made); refresh sources or add more channels in Settings")
        bid = uuid.uuid4().hex[:8]
        out = DATA / f"topic-options-{bid}.json"
        cfile = DATA / f"topic-candidates-{bid}.json"
        save_json(cfile, {"candidates": cands, "already_made_titles": made[:150], "types": TYPES})
        c = cfg()
        prompt = f"""You are the topic scout for the YouTube channel "{c['channel']}": hand-drawn cartoon science Shorts hosted by a red bean, 30 to 45 seconds, each answering one concrete, drawable science question. Category: {c.get('topic_category', 'science explainers')}.

Read {cfile}. "candidates" are recent Shorts from other channels that beat their own channel's median views by the "multiple" shown. "already_made_titles" are topics we have made or planned: never repeat or closely echo them.

Pick FIVE different candidates and adapt each into an ORIGINAL topic for our channel. Borrow the topic area and the video format only: never copy a title, a script or a distinctive phrase. Rules:
- 5 different video types (from {TYPES}); at most one "What if". Title in the channel voice: a plain question or claim, under 60 characters, no hype words, no all caps.
- Every topic must be drawable as a cartoon with props and faces, and answerable in about 100 words with a real number or scale.
- Only topics whose facts you are confident about, or flag the risk honestly.
- Prefer the highest "multiple", but variety beats ranking.

Write a JSON array of exactly 5 objects to {out} and nothing else on disk. Each object:
{{"title": str, "type": one of the types, "promise": "one sentence on what the video shows and the answer it lands on", "visual": "one line: what we would draw", "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {{"title": source title, "channel": source channel, "multiple": number, "url": source url}}}}
Do not use any other tool than reading that file and writing that file. When done, also print the same JSON array as your final message."""
        cmd = list(c["agent_command"])
        if c.get("options_model"): cmd += ["--model", c["options_model"]]
        j = start_job("topics · 5 ideas", cmd + [prompt], c["agent_cwd"])
        b = {"id": bid, "job": j["id"], "out": str(out), "status": "running", "candidates": cands, "options": [], "started": time.time()}
        st["batches"][bid] = b
        state["seen"] = list(seen | {x["id"] for x in cands})[-400:]
        save_json(STATEF, state)
        return jsonify(batch=bid, job=j["id"])

    @app.get("/api/topics/batch/<bid>")
    def topics_batch(bid):
        b = st["batches"].get(bid) or abort(404, "unknown batch (server restarted?)")
        j = JOBS.get(b["job"])
        if b["status"] == "running" and j and j["done"]: finish_batch(b)
        return jsonify(status=b["status"], options=b["options"], seconds=int(time.time() - b["started"]),
                       log=(j["log"][-4:] if j and b["status"] == "running" else []))

    # ---------- 3. the form's answers -> the whole video ----------
    def slug_for(title):
        words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP][:4] or ["short"]
        base = "-".join(words)[:40].strip("-") or "short"
        d, slug, n = Path(cfg()["projects_dir"]), base, 2
        while (d / slug).exists(): slug, n = f"{base}-{n}", n + 1
        return slug

    @app.post("/api/topics/make")
    def topics_make():
        b = request.json or {}
        t, a, c = b.get("topic") or {}, b.get("answers") or {}, cfg()
        title = clean(t.get("title"), 120)
        if not title: abort(400, "no topic")
        dur = min(60, max(25, int(a.get("duration") or 40)))
        words = round(dur * 2.8)
        voice = a.get("voice") if a.get("voice") in VOICES else "af_heart"
        speed = min(1.15, max(0.9, float(a.get("speed") or 1.0)))
        slug = slug_for(title)
        src = t.get("inspired_by") or {}
        prompt = f"""Make a new Short with the line-boil skill. Read ~/.claude/skills/line-boil/SKILL.md and the files it points to (references/api.md, references/style.md, references/youtube.md) first, and ~/.claude/youtube/voice.md for the channel voice.

TOPIC: {title}
Video type: {clean(t.get('type'), 40)}
What it shows: {clean(t.get('promise'), 300)}
What we would draw: {clean(t.get('visual'), 200)}
Fact to check carefully: {clean(t.get('fact_note'), 200)}
Inspired by (topic and format only; do not reuse its script or title): "{clean(src.get('title'), 120)}" from {clean(src.get('channel'), 60)}

PROJECT NAME: {slug}   (create it with build.py new {slug}; it lands in {c['projects_dir']})

THE USER'S ANSWERS (follow them):
- Length: about {dur} seconds of voiceover, which is about {words} words. Write the script to that length, run build.py voice, and adjust the script if the real length is more than 4 seconds off.
- Voice: {voice}   Speed: {speed}  (build.py voice {slug} --voice {voice} --speed {speed})
- Tone: {clean(a.get('tone') or 'dry and deadpan, the channel default', 80)}
- Cast: {'reuse the red host bean (BEAN in the bean-avatar project) as the hero' if a.get('cast') == 'host' else 'a new cast designed for this topic'}
- Ending: {clean(a.get('ending') or 'a punchy callback line', 80)}
- Background music: {'on' if a.get('music', True) else 'off (pass --no-music to build.py video)'}
- Channel outro: {'appended' if a.get('outro', True) else 'left off (pass --no-outro to build.py video)'}
- Thumbnail text: {clean(a.get('thumb_text'), 40) or 'you choose: at most 3 words, none repeated from the title'}
- Extra notes: {clean(a.get('notes'), 400) or 'none'}

The user has already approved this topic and these settings, so do NOT stop to ask or to show a plan. Go straight through: script, fact-check (search the web; hedge anything uncertain; keep the sources for the sheet), cast, shots, build.py check, stills of every shot checked for overlaps and caption placement, build.py video, build.py sheet, the thumbnail (SKILL.md step 9) and the YouTube upload sheet (step 10). Do not upload anything and do not touch other projects. Finish by printing the project folder, the title and the thumbnail text."""
        (DATA / "make").mkdir(parents=True, exist_ok=True)
        (DATA / "make" / f"{slug}.json").write_text(json.dumps({"topic": t, "answers": a, "when": dt.datetime.now().isoformat(timespec="seconds")}, indent=1, ensure_ascii=False), encoding="utf-8")
        cmd = list(c["agent_command"])
        if c.get("video_model"): cmd += ["--model", c["video_model"]]
        j = start_job(f"make · {slug}", cmd + [prompt], c["agent_cwd"])
        return jsonify(job=j["id"], project=slug, title=title)
