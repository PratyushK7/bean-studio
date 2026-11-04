"""Topic selector + video generator for Bean Studio, for Shorts and for long videos.

1. Finds what is working on other channels in the same category: public listings (yt-dlp, no login), each video scored as a
   multiple of its own channel's median views, so a big channel's normal day doesn't look like a hit. Shorts and long videos
   have separate pools and separate medians.
2. "Get 5 ideas": a sample of the best outliers goes to the agent, which adapts five of them into ORIGINAL topics for this
   channel (topic and format borrowed, never the script or title). "Re-roll" samples a fresh set, skipping sources already shown.
   data/picks.json holds hand-researched topics (with a brief file) that show above the generated ones.
3. A chosen topic + the answers from the form become one agent job. A Short goes all the way to a rendered video; a long video
   stops at the script package, because the line-boil engine renders 9:16 only.

length_instructions(seconds) is the one place that turns a duration into instructions for the skill; the Agent tab uses it too.
register(app, ROOT, cfg, start_job, JOBS) adds /api/topics*.
"""
import concurrent.futures as cf, datetime as dt, difflib, json, random, re, statistics, subprocess, sys, threading, time, uuid
from pathlib import Path
from flask import abort, jsonify, request

import planner, store
from ytstate import norm

TYPES = ["What if", "Myth test", "Why", "True story", "Versus", "Ranking", "Levels", "Paradox", "Puzzle",
         "How it works", "Superlative", "How many", "Map/scale", "Explainer"]
FMT = [("What if", r"^what if|^what would happen|^what happens"), ("How many", r"^how (many|much|long|far|big|fast|hot|cold|deep|high|old)"),
       ("Versus", r"\bvs\.?\b|versus"), ("Levels", r"\blevels?\b"), ("Paradox", r"paradox"), ("Ranking", r"ranking|ranked|top \d+|\bworst\b|^\d+ "),
       ("Puzzle", r"which .* (first|more|faster)|puzzle|riddle|can you (guess|solve)"),
       ("Explainer", r"explained|the science of|everything you need|\ball the\b"),
       ("How it works", r"^how (do|does|did|is|are|was|to)\b|how .* works?"), ("Why", r"^why\b|\bwhy\b"),
       ("Superlative", r"\b(most|deadliest|largest|biggest|smallest|fastest|strongest|oldest|longest|rarest|sharpest)\b"),
       ("Map/scale", r"further|bigger than|smaller than|size of|\bmap\b"),
       ("True story", r"\b(1[0-9]{3}|20[0-2][0-9])\b|\bstory\b|history|disaster|incident|what happened"),
       ("Myth test", r"^(is|are|can|could|does|do)\b|myth|actually|really|truth")]
OFF_BRAND = re.compile(r"soldier|military|bomber|\bwar\b|russia|ukrain|israel|taliban|\bgun\b|shot\b|kill|murder|suicide|\bsex|porn|terror|nazi|trump|biden", re.I)
STOP = set("what if you your the a an of to how would it take and is are do does why can could in on for with from at".split())
VOICES = [["af_heart", "Heart · warm female (channel default)"], ["am_michael", "Michael · male"], ["bf_emma", "Emma · British female"], ["bm_george", "George · British male"]]
VOICE_IDS = [v[0] for v in VOICES]
LENGTHS = {"short": [30, 40, 50, 60], "long": [300, 420, 540, 720]}       # seconds; the Agent tab and the wizards offer these
WORDS_PER_SECOND = 2.8                                                       # the Kokoro voice at speed 1.0
KINDS = ("short", "long")


def length_instructions(seconds):
    """what to tell the line-boil skill when the user picked a duration"""
    seconds = int(seconds)
    words = round(seconds * WORDS_PER_SECOND)
    head = f"TARGET LENGTH: {seconds} seconds of voiceover, about {words} words ({WORDS_PER_SECOND} words a second)."
    if seconds <= 60:
        return (head + f" Write the script to this length, run build.py voice <project> --target {seconds}, and rewrite until it prints TARGET {seconds}s: OK"
                " (within 4 seconds). It is a Short, so it renders as 9:16.")
    return (head + " This is long-form (over 60 seconds). The line-boil engine renders only 9:16 Shorts, so produce the script package"
            f" (script.json, sources, chapters from the real word times via build.py voice <project> --target {seconds}, shot list, upload sheet)"
            " and stop before building any video. Say so at the end.")


def classify(title):
    for name, pat in FMT:
        if re.search(pat, title, re.I): return name
    return "Other"


def too_close(title, others, cutoff=0.72):
    t = norm(title)
    return any(difflib.SequenceMatcher(None, t, norm(o)).ratio() >= cutoff for o in others)


def clean(s, n=500):
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(s or "")).strip()[:n]


def kind_of(v):
    return v if v in KINDS else "short"


def register(app, ROOT, cfg, start_job, JOBS, start_agent=None):
    DATA = ROOT / "data"

    def run_agent(label, prompt, model=None, mode="plain"):
        """the studio's start_agent (live feed / own window); a plain job when none is given (tests)"""
        if start_agent: return start_agent(label, prompt, model, mode)
        cmd = list(cfg()["agent_command"]) + (["--model", model] if model else [])
        return start_job(label, cmd + [prompt], cfg()["agent_cwd"])

    POOL = {"short": DATA / "topic-pool.json", "long": DATA / "topic-pool-long.json"}
    STATEF, PICKS = DATA / "topic-state.json", DATA / "picks.json"
    st = {k: {"refreshing": False, "progress": "", "error": None} for k in KINDS}
    st["batches"] = {}
    lock = threading.Lock()

    load_json, save_json = store.read, store.write

    # ---------- 1. the pool of outliers ----------
    def fetch_channel(handle, kind):
        short = kind == "short"
        url = f"https://www.youtube.com/@{handle.lstrip('@')}/{'shorts' if short else 'videos'}"
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "50" if short else "45", "--no-warnings", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150)
        d = json.loads(r.stdout)
        ents = [e for e in (d.get("entries") or []) if e and e.get("view_count")]
        if not short:                                 # long-form means an actual episode: 4 to 40 minutes, not a Short or a live stream
            ents = [e for e in ents if 240 <= (e.get("duration") or 0) <= 2400]
        if len(ents) < (8 if short else 6): return []
        med = statistics.median(e["view_count"] for e in ents)
        name = d.get("channel") or d.get("uploader") or handle
        out = []
        for e in ents:
            t = re.sub(r"\s*#\S+", "", e.get("title", "")).strip()
            out.append({"id": e["id"], "title": t, "channel": name, "views": e["view_count"], "multiple": round(e["view_count"] / med, 2),
                        "type": classify(t), "duration": e.get("duration"),
                        "url": f"https://www.youtube.com/{'shorts/' if short else 'watch?v='}{e['id']}"})
        return out

    def refresh_pool(kind):
        with lock:
            s = st[kind]
            s.update(refreshing=True, error=None, progress="starting")
            chans = cfg().get("topic_channels", [])
            vids, done, failed = [], 0, []
            try:
                with cf.ThreadPoolExecutor(6) as ex:
                    futs = {ex.submit(fetch_channel, h, kind): h for h in chans}
                    for f in cf.as_completed(futs):
                        done += 1; s["progress"] = f"{done}/{len(chans)} channels"
                        try: vids += f.result()
                        except Exception: failed.append(futs[f])
                if not vids: raise RuntimeError("no videos came back; check your internet connection or the channel handles in Settings")
                save_json(POOL[kind], {"fetched": dt.datetime.now().isoformat(timespec="seconds"), "videos": vids, "failed": failed})
            except Exception as e:
                s["error"] = str(e)[:300]
            finally:
                s.update(refreshing=False, progress="")

    # ---------- 2. five ideas, and re-roll ----------
    def already_made():
        c = cfg(); names = []
        for sheet in Path(c["projects_dir"]).glob("*/*-youtube.txt"):
            m = re.search(r"== TITLE ==\s*\n(.+)", sheet.read_text(encoding="utf-8"))
            if m: names.append(m.group(1).strip())
        names += [p.name.replace("-", " ") for p in Path(c["projects_dir"]).iterdir() if p.is_dir()]
        names += planner.titles(c["planner"])
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

    def strings(v, n, size):
        return [clean(x, size) for x in v[:n] if isinstance(x, str)] if isinstance(v, list) else []

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
            if isinstance(o, dict) and o.get("title") and isinstance(o.get("inspired_by"), dict):
                o["type"] = o.get("type") if o.get("type") in TYPES else "Other"
                for k in ("promise", "visual", "fact_note"): o[k] = clean(o.get(k), 300)
                o["fact_risk"] = o.get("fact_risk") if o.get("fact_risk") in ("low", "medium", "high") else "medium"
                if b["kind"] == "long":
                    o["chapters"] = strings(o.get("chapters"), 9, 80); o["reuse_shorts"] = strings(o.get("reuse_shorts"), 6, 80)
                    o["sources_to_check"] = strings(o.get("sources_to_check"), 6, 120)
                    try: o["runtime_min"] = int(min(15, max(4, float(o.get("runtime_min") or 7))))
                    except (TypeError, ValueError): o["runtime_min"] = 7
                o["adapted"] = True; good.append(o)
        if len(good) < 5:                         # fill up (or replace) with the raw outliers, clearly marked
            for c in b["candidates"]:
                if len(good) >= 5: break
                good.append({"title": c["title"], "type": c["type"], "promise": "", "visual": "", "fact_risk": "medium", "fact_note": "",
                             "inspired_by": {"title": c["title"], "channel": c["channel"], "multiple": c["multiple"], "url": c["url"]}, "adapted": False})
        for i, o in enumerate(good[:5]): o["n"] = i
        b["options"], b["status"] = good[:5], "ready"
        save_json(DATA / f"topic-last-{b['kind']}.json", {"options": good[:5], "when": dt.datetime.now().isoformat(timespec="seconds")})   # shown again on the next visit

    @app.get("/api/topics")
    def topics_get():
        kind = kind_of(request.args.get("kind"))
        pool = load_json(POOL[kind], None)
        s = st[kind]
        return jsonify(kind=kind, refreshing=s["refreshing"], progress=s["progress"], error=s["error"],
                       fetched=pool and pool["fetched"], videos=pool and len(pool["videos"]), failed=pool and pool.get("failed", []),
                       channels=cfg().get("topic_channels", []), category=cfg().get("topic_category", ""),
                       top=(pool and sorted(pool["videos"], key=lambda v: -v["multiple"])[:8]) or [])

    @app.get("/api/topics/picks")
    def topics_picks():
        """hand-researched topics (data/picks.json), shown above the generated ideas"""
        kind = kind_of(request.args.get("kind"))
        picks = (load_json(PICKS, {}) or {}).get(kind, [])
        last = load_json(DATA / f"topic-last-{kind}.json", {}) or {}
        return jsonify(picks=[dict(p, n=i, pick=True, adapted=True) for i, p in enumerate(picks)], last=last.get("options", []), last_when=last.get("when"))

    @app.post("/api/topics/refresh")
    def topics_refresh():
        kind = kind_of((request.get_json(silent=True) or {}).get("kind"))
        if not any(s["refreshing"] for k, s in st.items() if k in KINDS):
            threading.Thread(target=refresh_pool, args=(kind,), daemon=True).start()
        return jsonify(ok=True)

    @app.post("/api/topics/options")
    def topics_options():
        kind = kind_of((request.get_json(silent=True) or {}).get("kind"))
        pool = load_json(POOL[kind], None)
        if not pool: abort(400, "no source data yet: press 'Refresh sources' first")
        state = load_json(STATEF, {"seen": []})
        skey = "seen" if kind == "short" else "seen_long"
        seen = set(state.get(skey, [])); made = already_made()
        cands = pick_candidates(pool["videos"], seen, made)
        if len(cands) < 5: abort(400, f"only {len(cands)} usable source videos out of {len(pool['videos'])} (after removing topics you already made); refresh sources or add more channels in Settings")
        bid = uuid.uuid4().hex[:8]
        out = DATA / f"topic-options-{bid}.json"
        cfile = DATA / f"topic-candidates-{bid}.json"
        save_json(cfile, {"candidates": cands, "already_made_titles": made[:150], "types": TYPES})
        c = cfg()
        if kind == "short":
            what = ("hand-drawn cartoon explainer Shorts hosted by a red bean, 30 to 45 seconds, funny in a dry way, each teaching one concrete thing a viewer can use or repeat; any genre that helps people learn (science, health, money, tech, history, psychology, how things work, everyday life), not only science",
                    "recent Shorts", "answerable in about 100 words with a real number or scale",
                    '{"title": str, "type": one of the types, "promise": "one sentence on what the video shows and the answer it lands on", "visual": "one line: what we would draw", "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {"title": source title, "channel": source channel, "multiple": number, "url": source url}}')
        else:
            what = ("hand-drawn cartoon explainers hosted by a red bean, funny in a dry way and always teaching something real; any genre that helps people learn (science, health, money, tech, history, psychology, how things work, everyday life). This is for a LONG video of 6 to 9 minutes (landscape), built from a clear premise with 5 to 8 chapters and a payoff",
                    "recent long videos (4 to 40 minutes)", "able to carry 6 to 9 minutes with real sources (studies, reviews, official guidance) and a chapter structure",
                    '{"title": str, "type": one of the types, "promise": "one sentence: the premise and the answer it lands on", "visual": "one line: the running visual gag or set piece", "chapters": [5 to 8 short chapter titles in order], "runtime_min": 6 to 9, "reuse_shorts": [titles of OUR made or planned Shorts it could fold in or spin off, if any], "sources_to_check": [3 to 5 named studies, reviews or agencies that would back it], "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {"title": source title, "channel": source channel, "multiple": number, "url": source url}}')
        prompt = f"""You are the topic scout for the YouTube channel "{c['channel']}": {what[0]}. Category: {c.get('topic_category', 'science explainers')}.

Read {cfile}. "candidates" are {what[1]} from other channels that beat their own channel's median views by the "multiple" shown. "already_made_titles" are topics we have made or planned: never repeat or closely echo them.

Pick FIVE different candidates and adapt each into an ORIGINAL topic for our channel. Borrow the topic area and the video format only: never copy a title, a script or a distinctive phrase. Rules:
- 5 different video types (from {TYPES}); at most one "What if". Title in the channel voice: a plain question or claim, under 60 characters, no hype words, no all caps.
- Every topic must be tellable by a cast of different beans (one bean per idea or role, so abstract ideas are welcome), funny without being silly (the joke lives in the picture and the last line), and {what[2]}.
- Vary the GENRE across the five (do not make all five science), and prefer topics where the viewer learns something they can use or explain to a friend.
- "Bad ideas" is only the channel's name: do not force a bad-idea framing onto every topic.
- Only topics whose facts you are confident about, or flag the risk honestly.
- Prefer the highest "multiple", but variety beats ranking.

Write a JSON array of exactly 5 objects to {out} and nothing else on disk. Each object:
{what[3]}
Do not use any other tool than reading that file and writing that file. When done, also print the same JSON array as your final message."""
        j = run_agent(f"topics · 5 {kind} ideas", prompt, c.get("options_model") or None, "plain")
        b = {"id": bid, "kind": kind, "job": j["id"], "out": str(out), "status": "running", "candidates": cands, "options": [], "started": time.time()}
        st["batches"][bid] = b
        state[skey] = list(seen | {x["id"] for x in cands})[-400:]
        save_json(STATEF, state)
        return jsonify(batch=bid, job=j["id"])

    @app.get("/api/topics/batch/<bid>")
    def topics_batch(bid):
        b = st["batches"].get(bid) or abort(404, "unknown batch (server restarted?)")
        j = JOBS.get(b["job"])
        if b["status"] == "running" and j and j["done"]: finish_batch(b)
        return jsonify(status=b["status"], options=b["options"], seconds=int(time.time() - b["started"]),
                       log=(j["log"][-4:] if j and b["status"] == "running" else []))

    # ---------- 3. the form's answers -> the video (Short) or the script package (long) ----------
    def slug_for(title):
        words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP][:4] or ["video"]
        base = "-".join(words)[:40].strip("-") or "video"
        d, slug, n = Path(cfg()["projects_dir"]), base, 2
        while (d / slug).exists(): slug, n = f"{base}-{n}", n + 1
        return slug

    def number(v, default, lo, hi):
        try: return min(hi, max(lo, float(v)))
        except (TypeError, ValueError): return default

    @app.post("/api/topics/make")
    def topics_make():
        b = request.get_json(silent=True) or {}
        t, a, c = b.get("topic") or {}, b.get("answers") or {}, cfg()
        kind = kind_of(b.get("kind"))
        title = clean(t.get("title"), 120)
        if not title: abort(400, "no topic")
        voice = a.get("voice") if a.get("voice") in VOICE_IDS else "af_heart"
        speed = round(number(a.get("speed"), 1.0, 0.9, 1.15), 2)
        dur = int(number(a.get("minutes"), 7, 4, 15) * 60) if kind == "long" else int(number(a.get("duration"), 40, 25, 60))
        slug = slug_for(title)
        (Path(c["projects_dir"]) / slug).mkdir(parents=True, exist_ok=True)     # reserve the name: a second click can't pick it too
        src = t.get("inspired_by") or {}
        brief = ""
        if t.get("brief"):                                                       # a researched pick: the agent must follow its brief
            bp = (ROOT / str(t["brief"])).resolve()
            if ROOT.resolve() in bp.parents and bp.is_file(): brief = str(bp)
        common = f"""TOPIC: {title}
Video type: {clean(t.get('type'), 40)}
What it shows: {clean(t.get('promise'), 300)}
What we would draw: {clean(t.get('visual'), 200)}
Fact to check carefully: {clean(t.get('fact_note'), 200)}
Inspired by (topic and format only; do not reuse its script or title): "{clean(src.get('title'), 120)}" from {clean(src.get('channel'), 60)}
{('RESEARCH BRIEF (read it first and follow it; its notes on what to verify and what NOT to claim override your own assumptions): ' + brief) if brief else ''}
PROJECT NAME: {slug}   (create it with build.py new {slug}; it lands in {c['projects_dir']})

THE USER'S ANSWERS (follow them):
- {length_instructions(dur)}
- Voice: {voice}   Speed: {speed}  (build.py voice {slug} --voice {voice} --speed {speed} --target {dur})
- Tone: {clean(a.get('tone') or 'dry and deadpan, the channel default', 80)}
- Cast: {'reuse the red host bean (BEAN in the bean-avatar project) as the hero, with other beans for the other ideas' if a.get('cast') == 'host' else 'a new cast of different beans designed for this topic: one bean per idea or role, abstract ideas as costume beans (see "A cast of beans" in references/style.md)'}
- Ending: {clean(a.get('ending') or 'a punchy callback line', 80)}
- Background music: {'on' if a.get('music', True) else 'off (pass --no-music to build.py video)'}
- Channel outro: {'appended' if a.get('outro', True) else 'left off (pass --no-outro to build.py video)'}
- Thumbnail text: {clean(a.get('thumb_text'), 40) or 'you choose: at most 3 words, none repeated from the title'}
- Extra notes: {clean(a.get('notes'), 400) or 'none'}
"""
        if kind == "short":
            prompt = f"""Make a new Short with the line-boil skill. Read ~/.claude/skills/line-boil/SKILL.md and the files it points to (references/api.md, references/style.md, references/youtube.md) first, and ~/.claude/youtube/voice.md for the channel voice.

{common}
The user has already approved this topic and these settings, so do NOT stop to ask or to show a plan. Go straight through: script, fact-check (search the web; hedge anything uncertain; keep the sources for the sheet), cast, shots, build.py check, stills of every shot checked for overlaps and caption placement, build.py video, build.py sheet, the thumbnail (SKILL.md step 9) and the YouTube upload sheet (step 10). Do not upload anything and do not touch other projects. Finish by printing the project folder, the title and the thumbnail text."""
        else:
            structure = clean(a.get("structure") or "as in the research brief or the topic's chapters", 80)
            prompt = f"""Prepare a LONG-FORM video package ({dur // 60} minutes) for the channel with the line-boil skill's tools. Read ~/.claude/skills/line-boil/SKILL.md (especially "Length") and ~/.claude/youtube/voice.md for the channel voice, and the yt-chapters and yt-seo skills' rules.

{common}- Structure: {structure}

IMPORTANT: the line-boil engine renders 9:16 Shorts only, so do NOT run build.py check, stills, video, thumb or sheet and do not write shots.js. Produce the package, then stop:
1. build.py new {slug}, then script.json: one sentence per entry, written chapter by chapter, with a hook in the first 30 seconds and a payoff that calls back to the hook. Dry, calm, honest; no hype words.
2. Fact-check every claim with web searches of primary sources (the paper, the review, the agency page). Hedge anything uncertain, drop anything you cannot verify, and never invent a number. Write {slug}-sources.md: a table of claim, source link, and what you verified (full text, abstract only, or secondary report).
3. build.py voice {slug} --voice {voice} --speed {speed} --target {dur}; rewrite and re-run until it prints TARGET {dur}s: OK.
4. {slug}-chapters.txt: YouTube chapters taken from the REAL word times in audio/words.json (first at 0:00, at least 3, each at least 10 seconds long).
5. {slug}-shotlist.md: for each chapter, what to draw, the characters, props and the visual gag, staged for 16:9 landscape (the finished video will be 1920x1080).
6. {slug}-youtube.txt following references/youtube.md but for a long video: no #shorts, a CHAPTERS section, a description whose first two lines contain the target search queries, 6 to 8 sources, tags, a pinned comment and the thumbnail brief (1280x720, at most 3 words). Also list 3 to 4 Shorts that could be cut from it.
Do not upload anything and do not touch other projects. Finish by printing the folder, the real voiceover length, the chapters and anything that could not be verified."""
        (DATA / "make").mkdir(parents=True, exist_ok=True)
        save_json(DATA / "make" / f"{slug}.json", {"kind": kind, "topic": t, "answers": a, "when": dt.datetime.now().isoformat(timespec="seconds")})
        mode = "window" if (a.get("window") or c.get("agent_window")) else "feed"      # watch it live, or in its own Claude window
        model = a.get("model") if a.get("model") in ("opus", "sonnet", "haiku") else (c.get("video_model") or None)
        j = run_agent(f"make · {slug}", prompt, model, mode)
        return jsonify(job=j["id"], project=slug, title=title, kind=kind, mode=mode)
