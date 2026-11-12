"""Topic selector + video generator for Bean Studio, for Shorts and for long videos.

1. Finds what is working on other channels in the same category: public listings (yt-dlp, no login), each video scored as a
   multiple of its own channel's median views, so a big channel's normal day doesn't look like a hit. Shorts and long videos
   have separate pools and separate medians.
2. "Get 5 ideas": a sample of the best outliers goes to the agent, which adapts five of them into ORIGINAL topics for this
   channel (topic and format borrowed, never the script or title). "Re-roll" samples a fresh set, skipping sources already shown.
   data/picks.json holds hand-researched topics (with a brief file) that show above the generated ones.
3. A chosen topic + the answers from the form become one agent job. A Short is made with the line-boil skill (9:16); a long video with
   the line-boil-wide skill (16:9, chapters), both to a rendered video and upload sheet (a long video's thumbnail comes later, from the Better thumbnail button).

length_instructions(seconds) is the one place that turns a duration into instructions for the skill; the Agent tab uses it too.
register(app, ROOT, cfg, start_job, JOBS) adds /api/topics*.
"""
import concurrent.futures as cf, datetime as dt, difflib, json, random, re, statistics, subprocess, sys, threading, time, uuid
from pathlib import Path
from flask import abort, jsonify, request

import channels, planner, store
from ytstate import norm

HI_FORMATS = {"economics": "Economics of owning X", "story": "Company rise/split/fall", "person": "A person's story", "compare": "Two people, one decision"}
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
WORDS_PER_SECOND = 3.1                                                       # the Kokoro voice at speed 1.0 (measured: 3.05 to 3.3 on our scripts)
KINDS = ("short", "long")


SHORT_AUTO = ("LENGTH: you decide, from what THIS topic needs to teach. The count is the VOICEOVER ONLY, and a Short has no outro (it ends 1.6 seconds after the last word: breath, iris close, black), so the voiceover is almost the whole video. The LAST sentence is the payback: a joke or flip that answers the opening line (no extra open question or teaser tacked on). Write a script people repeat: a hook that names the belief everyone holds and breaks it (honestly), sentence 2 that deepens it, one drawable image per sentence under 15 words, a re-hook, a payoff in the viewer's own words. "
              "First list the three things a viewer must leave knowing (the answer, why it is true, one surprising detail or number they can repeat), "
              "then write only the sentences that carry those: one core mechanism, no padding, and never cut a needed fact just to hit a number. Stay between 30 and 50 seconds of voiceover "
              f"(about {round(30 * WORDS_PER_SECOND)} to {round(50 * WORDS_PER_SECOND)} words at {WORDS_PER_SECOND} words a second); go up to 60 only when every extra beat escalates, never for more explanation. Follow the skill retention rules: sentence 2 raises the stakes and never explains or gives the answer, a re-hook about halfway, a joke every 8 to 10 seconds, no shot over about 4 seconds. Once the script is written, state your chosen length, run build.py voice <project> --target <that many seconds>, "
              "and rewrite until it prints TARGET <seconds>s: OK (within 4 seconds). It is a Short, so it renders as 9:16 with the line-boil skill.")


def length_instructions(seconds):
    """what to tell the line-boil skill when the user picked a duration (None: a Short whose length the agent decides)"""
    if not seconds: return SHORT_AUTO
    seconds = int(seconds)
    words = round(seconds * WORDS_PER_SECOND)
    head = f"TARGET LENGTH: {seconds} seconds of voiceover, about {words} words ({WORDS_PER_SECOND} words a second)."
    if seconds <= 60:
        return (head + f" Write the script to this length, run build.py voice <project> --target {seconds}, and rewrite until it prints TARGET {seconds}s: OK"
                " (within 4 seconds). It is a Short, so it renders as 9:16 with the line-boil skill.")
    return (head + " This is a long video (over 60 seconds): use the line-boil-wide skill (16:9, 1920x1080, chapters), which runs on the same engine"
            f" (build.py new <project> --wide). Write the script to this length, run build.py voice <project> --target {seconds}, and rewrite until it"
            f" prints TARGET {seconds}s: OK. Plan 5 to 9 chapters of 45 to 90 seconds, write chapters.json, and make the video, chapter by chapter.")


MAKE_REQ = re.compile(r"^\s*(?:please\s+)?(?:make|create|build|produce)\s+(?:me\s+)?(?:a|an|another|the)?\s*(?:new\s+)?(short|long video|video|reel)\b(?P<rest>.*)", re.I | re.S)


def make_request(prompt, seconds=None):
    """an Agent-tab prompt that asks for a whole video ("Make a new Short ... about X"): {"topic", "long"}; None for any other request"""
    m = MAKE_REQ.match(prompt or "")
    if not m: return None
    low = (prompt or "").lower()
    long = m.group(1).lower() == "long video" or bool(seconds and seconds > 60) or "16:9" in low or bool(re.search(r"\b\d+\s*(?:-|\s)?minute", low))
    t = re.search(r"\babout\s+(.+?)(?:\.\s|\n|$)", m.group("rest"), re.S)
    topic = clean((t.group(1) if t else m.group("rest")).strip(" .\"'"), 60) or "new video"
    return {"topic": topic, "long": long}


def short_label(prompt):
    """a readable name for an Agent-tab run: the first line, cut at a word, never in the middle of a quote"""
    first = re.sub(r"\s+", " ", (prompt or "").strip().split("\n")[0])
    if len(first) <= 50: return first
    cut = first[:50].rsplit(" ", 1)[0]
    if cut.count('"') % 2: cut = cut[:cut.rindex('"')]            # never end inside an opened quote
    return cut.rstrip(" ,;:\"'") + "…"


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


THEMES = ("classic", "noir", "sepia", "soft", "hype")      # the engine's colour themes (build.py new --theme)


def stage_notes(slug, long):
    """the two notes of a two-stage video: STAGE 1 (Opus plans) and STAGE 2 (Sonnet builds). slug may be a placeholder such as <project>"""
    unit = "chapter" if long else "shot"
    plan_note = f"""

STAGE 1 OF 2: THE PLAN. You are the writer and director. A second, separate run (a cheaper model) will code the shots from your files, so every creative decision must be made and written down by you, now.
Do these and then STOP: build.py new (with --theme <classic|noir|sepia|soft|hype> if the genre is not bright and playful, unless a Theme line above already says which: see Genre in the skill), the hook, the script, the fact-check, {'chapters.json, ' if long else ''}the cast concept, build.py voice (rewrite and re-run until it hits the length), and the sheet's text decisions (title with alternates, thumbnail words and brief, description, tags, sources) written to {slug}-youtube.txt.
Then write {slug}-shotplan.md. Its first two lines are `Genre: <one word>` and `Theme: <classic|noir|sepia|soft|hype>` (the theme build.py new was given; the build run reads them): the sets, music moods, faces and jokes in the plan must all fit that genre. Then ONE ROW PER SHOT, detailed enough that someone who has never seen the script can code it without making a single creative choice. For each shot give: the sentence numbers and the exact words to anchor on with at('...'), the set, place and colours, which beans are on screen and their expressions, the action beat by beat, the props, the camera move, the visual joke and where it lands, the sound cue and the music mood. Put a cast table at the top: each bean's shape, colour, hat, size and what it stands for (apply the Mindful details section of ~/.claude/skills/line-boil/references/style.md: a real brand, product or place keeps its own recognisable colours and symbol, never a random palette colour), and the list of props to build{' (and the per-chapter ' + unit + ' groups)' if long else ''}.{'' if long else ' Also write the THUMBNAIL BRIEF at the top (the Build run draws it exactly, following ~/.claude/skills/line-boil-thumbnail-short/SKILL.md): the 2 to 4 words, the one big topic object and why a stranger would know the topic from it at feed size (an abstract topic needs a symbol such as a giant clock for time zones), the bean and its expression, the video shot it matches, and the one-sentence accuracy check. If the user described the thumbnail (see the Thumbnail line above), the brief is their description, word for word.'}
Do NOT write web/cast.js or the shots files, and do NOT run build.py check, stills, video, sheet or thumb: ignore every later step in the list above. Finish by printing the plan's path and a two-line summary."""
    build_note = f"""

STAGE 2 OF 2: THE BUILD. The plan was done by a separate run; do not redo it. Already written for you: script.json, the voice and word timings (audio/), {slug}-hooks.txt, {slug}-sources.md, {slug}-youtube.txt and {slug}-shotplan.md, which holds every creative decision.
The look is already fixed: the theme is in project.json and the plan's first two lines name the genre. Do not change the theme, and write every colour as RED, BLUE, YEL, PAPER or INK, never a hex. Read those files ONCE. Do not rewrite or reorder the script, do not run build.py voice, do not redo the fact-check or the hook. If something in the plan cannot be done in the engine, take the closest option and note it at the end instead of redesigning it.
Now do the remaining steps in the list above: write web/cast.js and the shots exactly as the shot plan says{', one chapter at a time' if long else ''}, build.py check, stills (at most two rounds, fixing only real overlaps and clipped text), build.py video, build.py sheet{'' if long else ', the thumbnail exactly as the THUMBNAIL BRIEF in the plan says, with the thumbnail skill accuracy test'}, and finish {slug}-youtube.txt (the Video line with the real length and the thumbnail section with the real file). Do not upload anything and do not touch other projects."""
    return plan_note, build_note


def resume_note(slug, long, planned):
    """appended to the make prompt when a video that stopped is continued: keep every file, do only what is missing"""
    return f"""

CONTINUING A VIDEO THAT STOPPED (the Claude usage limit was reached, or the run crashed). Project {slug} already exists with the work done so far. Do NOT run build.py new again and do NOT start over or rewrite anything that is finished.
First list the project folder and read what is there: script.json, audio/ (if words.json exists the voice is done: do not re-run build.py voice), {slug}-hooks.txt, {slug}-sources.md, {slug}-shotplan.md{', chapters.json, ' + slug + '-plan.md' if long else ''}, web/cast.js, web/shots.js{' and web/shots/ch*.js' if long else ''}, stills/, the mp4, the thumbnail and {slug}-youtube.txt.
{'The plan is complete (script, voice and shot plan exist). Only the BUILD is left.' if planned else 'The plan is not finished: carry on from the last file that exists.'} A half-written shots or cast file may be cut off mid-way: re-read it, keep the finished shots, and finish or rewrite only the broken part. Then do every remaining step, skipping any whose output already exists and looks right, and finish as the original request says."""


def register(app, ROOT, cfg, start_job, JOBS, start_agent=None, start_staged=None):
    class _Data:                      # this channel's data folder, looked up each time it is used
        def __truediv__(self, name): return channels.data_for(ROOT) / name
    DATA = _Data()

    def run_agent(label, prompt, model=None, mode="plain"):
        """the studio's start_agent (live feed / own window); a plain job when none is given (tests)"""
        if start_agent: return start_agent(label, prompt, model, mode)
        cmd = list(cfg()["agent_command"]) + (["--model", model] if model else [])
        return start_job(label, cmd + [prompt], cfg()["agent_cwd"])

    def KIND(v):
        """the kind asked for, limited to what this channel makes (the Hindi channel makes long videos only)"""
        ks = cfg().get("kinds") or list(KINDS)
        return v if v in ks else ks[0]

    def hindi(): return (cfg().get("language") or "").lower() == "hindi"

    POOL = lambda kind: DATA / ("topic-pool.json" if kind == "short" else "topic-pool-long.json")
    STATEF, PICKS = lambda: DATA / "topic-state.json", lambda: DATA / "picks.json"
    st = channels.PerChannel(lambda cid: {**{k: {"refreshing": False, "progress": "", "error": None} for k in KINDS}, "batches": {}})
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
            lo, hi = (480, 3600) if hindi() else (240, 2400)           # the Hindi channel studies 8 to 60 minute documentaries
            ents = [e for e in ents if lo <= (e.get("duration") or 0) <= hi]
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
                save_json(POOL(kind), {"fetched": dt.datetime.now().isoformat(timespec="seconds"), "videos": vids, "failed": failed})
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
                o["type"] = o.get("type") if o.get("type") in TYPES + list(HI_FORMATS.values()) else "Other"
                for k in ("angle", "gap", "assumption"): o[k] = clean(o.get(k), 300)
                o["covered_by"] = strings(o.get("covered_by"), 5, 160)
                for k in ("promise", "visual", "fact_note"): o[k] = clean(o.get(k), 300)
                o["fact_risk"] = o.get("fact_risk") if o.get("fact_risk") in ("low", "medium", "high") else "medium"
                if b["kind"] == "long":
                    o["chapters"] = strings(o.get("chapters"), 9, 80); o["reuse_shorts"] = strings(o.get("reuse_shorts"), 6, 80)
                    o["sources_to_check"] = strings(o.get("sources_to_check"), 6, 120)
                    try: o["runtime_min"] = int(min(15, max(4, float(o.get("runtime_min") or 7))))
                    except (TypeError, ValueError): o["runtime_min"] = 7
                o["adapted"] = True; good.append(o)
        if len(good) < 3:                         # fill up (or replace) with the raw outliers, clearly marked
            for c in b["candidates"]:
                if len(good) >= 3: break
                good.append({"title": c["title"], "type": c["type"], "promise": "", "visual": "", "fact_risk": "medium", "fact_note": "",
                             "inspired_by": {"title": c["title"], "channel": c["channel"], "multiple": c["multiple"], "url": c["url"]}, "adapted": False})
        for i, o in enumerate(good[:3]): o["n"] = i
        b["options"], b["status"] = good[:3], "ready"
        save_json(DATA / f"topic-last-{b['kind']}.json", {"options": good[:3], "when": dt.datetime.now().isoformat(timespec="seconds")})   # shown again on the next visit

    @app.get("/api/topics")
    def topics_get():
        kind = KIND(request.args.get("kind"))
        pool = load_json(POOL(kind), None)
        s = st[kind]
        return jsonify(kind=kind, refreshing=s["refreshing"], progress=s["progress"], error=s["error"],
                       fetched=pool and pool["fetched"], videos=pool and len(pool["videos"]), failed=pool and pool.get("failed", []),
                       channels=cfg().get("topic_channels", []), category=cfg().get("topic_category", ""),
                       top=(pool and sorted(pool["videos"], key=lambda v: -v["multiple"])[:8]) or [])

    @app.get("/api/topics/picks")
    def topics_picks():
        """hand-researched topics (data/picks.json), shown above the generated ideas"""
        kind = KIND(request.args.get("kind"))
        picks = (load_json(PICKS(), {}) or {}).get(kind, [])
        for b in list(st["batches"].values()):       # a batch whose agent finished while nobody was watching (another tab, a reload): collect it now
            j = JOBS.get(b["job"])
            if b["kind"] == kind and b["status"] == "running" and j and j["done"]: finish_batch(b)
        running = next((b["id"] for b in st["batches"].values() if b["kind"] == kind and b["status"] == "running"), None)
        last = load_json(DATA / f"topic-last-{kind}.json", {}) or {}
        return jsonify(picks=[dict(p, n=i, pick=True, adapted=True) for i, p in enumerate(picks)], last=last.get("options", []), last_when=last.get("when"), running=running)

    @app.post("/api/topics/refresh")
    def topics_refresh():
        kind = KIND((request.get_json(silent=True) or {}).get("kind"))
        if not any(s["refreshing"] for k, s in st.items() if k in KINDS):
            threading.Thread(target=channels.bound(refresh_pool, cfg()["channel_id"]), args=(kind,), daemon=True).start()
        return jsonify(ok=True)

    @app.post("/api/topics/options")
    def topics_options():
        kind = KIND((request.get_json(silent=True) or {}).get("kind"))
        pool = load_json(POOL(kind), None)
        if not pool: abort(400, "no source data yet: press 'Refresh sources' first")
        state = load_json(STATEF(), {"seen": []})
        skey = "seen" if kind == "short" else "seen_long"
        seen = set(state.get(skey, [])); made = already_made()
        cands = pick_candidates(pool["videos"], seen, made)
        if len(cands) < 3: abort(400, f"only {len(cands)} usable source videos out of {len(pool['videos'])} (after removing topics you already made); refresh sources or add more channels in Settings")
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

Pick THREE different candidates and adapt each into an ORIGINAL topic for our channel. Borrow the topic area and the video format only: never copy a title, a script or a distinctive phrase. Rules:
- 3 different video types (from {TYPES}); at most one "What if". Title in the channel voice: a plain question or claim, under 60 characters, no hype words, no all caps.
- Every topic must be tellable by a cast of different beans (one bean per idea or role, so abstract ideas are welcome), funny without being silly (the joke lives in the picture and the last line), and {what[2]}.
- Vary the GENRE across the three (do not make all three science), and prefer topics where the viewer learns something they can use or explain to a friend.
- "Bad ideas" is only the channel's name: do not force a bad-idea framing onto every topic.
- Only topics whose facts you are confident about, or flag the risk honestly.
- Prefer the highest "multiple", but variety beats ranking.

Write a JSON array of exactly 3 objects to {out} and nothing else on disk. Each object:
{what[3]}
Do not use any other tool than reading that file and writing that file. When done, also print the same JSON array as your final message."""
        if hindi(): prompt = hindi_options_prompt(c, cfile, out)
        j = run_agent(f"topics · 3 {kind} ideas", prompt, c.get("options_model") or None, "plain")
        b = {"id": bid, "kind": kind, "job": j["id"], "out": str(out), "status": "running", "candidates": cands, "options": [], "started": time.time()}
        st["batches"][bid] = b
        state[skey] = list(seen | {x["id"] for x in cands})[-400:]
        save_json(STATEF(), state)
        return jsonify(batch=bid, job=j["id"])

    @app.get("/api/topics/batch/<bid>")
    def topics_batch(bid):
        b = st["batches"].get(bid) or abort(404, "unknown batch (server restarted?)")
        j = JOBS.get(b["job"])
        if b["status"] == "running" and j and j["done"]: finish_batch(b)
        return jsonify(status=b["status"], options=b["options"], seconds=int(time.time() - b["started"]),
                       log=(j["log"][-4:] if j and b["status"] == "running" else []))

    # ---------- 3. the form's answers -> the finished video (Short 9:16, long 16:9) ----------
    def slug_for(title):
        words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP][:4] or ["video"]
        base = "-".join(words)[:40].strip("-") or "video"
        d, slug, n = Path(cfg()["projects_dir"]), base, 2
        while (d / slug).exists(): slug, n = f"{base}-{n}", n + 1
        return slug

    def number(v, default, lo, hi):
        try: return min(hi, max(lo, float(v)))
        except (TypeError, ValueError): return default


    def hindi_options_prompt(c, cfile, out):
        return f"""You are the topic scout for the Hindi YouTube channel "{c['channel']}": long (10 to 15 minute) faceless business case-study videos in the style of HinExp, ABFinDoc, HiddenOps and Shivanshu Agrawal. Category: {c.get('topic_category', '')}.

Read ~/.claude/skills/hindi-case-study/SKILL.md (section 1, Topic and format, including the rule for repeating a covered topic cleverly) and {cfile}. "candidates" are long videos from the reference channels that beat their own channel's median views by "multiple". "already_made_titles" are ours: never repeat them.

Pick THREE different candidates and turn each into a topic for us. A topic someone already covered is fine IF you give it a clearly different angle: a different question, the unit economics or contract nobody put on screen, a human on the other side, or a story shape the competitor does not use. Keep the proven title FORMULA, never the competitor's script. Each topic must pass the skill's three tests (the viewer can picture it in the first sentence; a gap between what everyone assumes and what is true; money math or a human conflict). Use three different formats among economics / story / person / compare. You may check competition with yt_dlp: C:/Users/praty/youtube/.venv/Scripts/python.exe -m yt_dlp "ytsearch8:<query>" --flat-playlist --print "%(view_count)s | %(channel)s | %(title)s". Never invent a view count: if you did not see it, leave it out.

Write a JSON array of exactly 3 objects to {out} and nothing else on disk. Each object:
{{"title": "English or Hinglish, under 80 characters, using a proven formula", "type": one of {list(HI_FORMATS.values())}, "format": one of {list(HI_FORMATS)}, "assumption": "what everyone assumes, one line", "gap": "what is actually true, one line", "angle": "how this differs from the covered versions, one sentence", "covered_by": ["Channel: title (views)", ...], "promise": "one sentence: the story and where it lands", "visual": "one line: the recurring characters and set", "chapters": [5 to 8 short English chapter titles], "runtime_min": 10 to 15, "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {{"title": source title, "channel": source channel, "multiple": number, "url": source url}}}}
When done, also print the same JSON array as your final message."""

    @app.post("/api/topics/analyze")
    def topics_analyze():
        """the topic analyzer (Hindi channel): one idea in, a verdict out: three tests, who covered it, the different angle, titles, chapters"""
        topic = clean((request.get_json(silent=True) or {}).get("topic"), 300)
        if not topic: abort(400, "write the topic first")
        if not hindi(): abort(400, "the topic analyzer is for the Hindi channel")
        aid = uuid.uuid4().hex[:8]; out = DATA / f"topic-analysis-{aid}.json"
        prompt = f"""You are the topic analyzer for the Hindi YouTube channel "{cfg()['channel']}" (long faceless business case-study videos, 10 to 15 minutes). Judge ONE topic: {topic}

Read ~/.claude/skills/hindi-case-study/SKILL.md section 1 (the three tests and the rule for repeating a covered topic cleverly). Then search YouTube for the topic: C:/Users/praty/youtube/.venv/Scripts/python.exe -m yt_dlp "ytsearch10:<query in English and Hinglish>" --flat-playlist --print "%(view_count)s | %(channel)s | %(title)s | %(duration_string)s | %(id)s" (two or three queries). Report only views you actually saw. Be honest: a verdict of "skip" is a fine answer.

Write ONE JSON object to {out} and nothing else on disk:
{{"topic": str, "verdict": "go"|"sharpen"|"skip", "verdict_line": "one plain sentence why", "tests": {{"picture": {{"ok": bool, "note": str}}, "gap": {{"ok": bool, "assumption": str, "truth": str}}, "money_or_conflict": {{"ok": bool, "note": str}}}}, "format": "economics"|"story"|"person"|"compare", "covered_by": [{{"channel": str, "title": str, "views": int or null, "url": str}}], "demand_note": "what the search shows about demand and the gap", "angle": "the different angle to take", "titles": [3 titles using a proven formula, under 80 characters], "thumbnail_words": [2 to 3 options of 2 to 4 words], "runtime_min": 10 to 15, "chapters": [5 to 8 short English chapter titles], "fact_risk": "low"|"medium"|"high", "facts_to_check": [up to 6]}}
When done, print the same JSON as your final message."""
        j = run_agent("topic analysis", prompt, "opus", "plain")
        st["batches"][aid] = {"id": aid, "kind": "analysis", "job": j["id"], "out": str(out), "status": "running", "started": time.time(), "topic": topic}
        return jsonify(analysis=aid, job=j["id"])

    def finish_analysis(b):
        a = None
        try: a = json.loads(Path(b["out"]).read_text(encoding="utf-8")) if Path(b["out"]).exists() else None
        except Exception: a = None
        if not a:
            j = JOBS.get(b["job"]); text = "\n".join(j["log"]) if j else ""
            m = re.search(r"\{.*\}", text, re.S)
            try: a = json.loads(m.group(0)) if m else None
            except Exception: a = None
        if not isinstance(a, dict) or not a.get("verdict"):
            b["status"], b["result"] = "failed", None; return
        a["verdict"] = a["verdict"] if a["verdict"] in ("go", "sharpen", "skip") else "sharpen"
        a["topic"] = clean(a.get("topic") or b.get("topic"), 300)
        for k in ("verdict_line", "demand_note", "angle"): a[k] = clean(a.get(k), 500)
        a["titles"] = strings(a.get("titles"), 3, 100); a["thumbnail_words"] = strings(a.get("thumbnail_words"), 3, 40)
        a["chapters"] = strings(a.get("chapters"), 9, 80); a["facts_to_check"] = strings(a.get("facts_to_check"), 6, 160)
        a["covered_by"] = [{"channel": clean(x.get("channel"), 80), "title": clean(x.get("title"), 140), "views": x.get("views") if isinstance(x.get("views"), int) else None,
                            "url": clean(x.get("url"), 200)} for x in (a.get("covered_by") or [])[:8] if isinstance(x, dict)]
        try: a["runtime_min"] = int(min(15, max(8, float(a.get("runtime_min") or 12))))
        except (TypeError, ValueError): a["runtime_min"] = 12
        a["format"] = a.get("format") if a.get("format") in HI_FORMATS else "economics"
        a["when"] = dt.datetime.now().isoformat(timespec="seconds"); a["id"] = b["id"]
        b["status"], b["result"] = "ready", a
        hist = (load_json(DATA / "topic-analyses.json", []) or [])[:7]
        save_json(DATA / "topic-analyses.json", [a] + hist)

    @app.get("/api/topics/analysis/<aid>")
    def topics_analysis(aid):
        b = st["batches"].get(aid) or abort(404, "unknown analysis (server restarted?)")
        j = JOBS.get(b["job"])
        if b["status"] == "running" and j and j["done"]: finish_analysis(b)
        return jsonify(status=b["status"], result=b.get("result"), seconds=int(time.time() - b["started"]))

    @app.get("/api/topics/analyses")
    def topics_analyses():
        return jsonify(analyses=load_json(DATA / "topic-analyses.json", []) or [])

    def make_hindi(t, a, title):
        """a chosen or analysed topic -> a new Pipeline project and the script, written by Opus with the hindi-case-study skill"""
        c = cfg(); slug = slug_for(title); p = Path(c["projects_dir"]) / slug
        for sub in ("prompts", "images", "assets"): (p / sub).mkdir(parents=True, exist_ok=True)
        mins = int(number(a.get("minutes"), 12, 10, 15))
        fmt = a.get("format") if a.get("format") in HI_FORMATS else (t.get("format") if t.get("format") in HI_FORMATS else "economics")
        facts = "\n".join(f"- {k}: {clean(t.get(k), 400)}" for k in ("assumption", "gap", "angle", "promise", "visual") if t.get(k))
        covered = "; ".join(strings(t.get("covered_by"), 5, 160))
        prompt = f"""Use the hindi-case-study skill (read ~/.claude/skills/hindi-case-study/SKILL.md, references/study.md and ~/.claude/youtube/voice-hindi.md) for the channel "{c['channel']}". Write the script for this video.
Title: {title}
Format: {fmt} ({HI_FORMATS[fmt]}). Target runtime: {mins} minutes (about {int(mins * 155 * 0.97)} Hindi words).
{facts}
{('Already covered by: ' + covered + '. Take the different angle above; never retell their script.') if covered else ''}
{('Chapters suggested: ' + ', '.join(strings(t.get('chapters'), 9, 80))) if t.get('chapters') else ''}
{('Extra notes from the user: ' + clean(a.get('notes'), 800)) if a.get('notes') else ''}
The project folder is {p} (it exists). Write script.json (with the per-line kind and shot plan from the skill), the research file, the check output and the voice text there. Run casecheck.py, fix every FAIL, and finish with the hand-back (including the shot counts and the estimated xAI cost). Do not generate images, video or voice and do not touch other projects."""
        j = run_agent(f"script · {slug}", prompt, "opus", "feed")
        (DATA / "make").mkdir(parents=True, exist_ok=True)
        save_json(DATA / "make" / f"{slug}.json", {"kind": "long", "topic": t, "answers": a, "when": dt.datetime.now().isoformat(timespec="seconds")})
        return jsonify(job=j["id"], project=slug, title=title, kind="long", mode="feed", staged=False)

    @app.post("/api/topics/make")
    def topics_make():
        b = request.get_json(silent=True) or {}
        resume = re.sub(r"[^\w.-]", "", str(b.get("resume") or ""))[:80]        # continue a video that stopped (usage limit, a crash): same project, same answers
        if resume:
            if hindi(): abort(400, "continuing is for the line-boil videos")
            saved = load_json(DATA / "make" / f"{resume}.json", None)
            if not saved or not (Path(cfg()["projects_dir"]) / resume).is_dir(): abort(404, "nothing to continue: that video was not started from the studio")
            if any(j["label"] == f"make · {resume}" and not j["done"] for j in JOBS.values()): abort(409, "that video is still being made")
            b = {"kind": saved.get("kind"), "topic": saved.get("topic"), "answers": saved.get("answers")}
        t, a, c = b.get("topic") or {}, b.get("answers") or {}, cfg()
        kind = KIND(b.get("kind"))
        title = clean(t.get("title"), 120)
        if not title: abort(400, "no topic")
        if hindi(): return make_hindi(t, a, title)
        voice = a.get("voice") if a.get("voice") in VOICE_IDS else "af_heart"
        speed = round(number(a.get("speed"), 1.0, 0.9, 1.15), 2)
        dur = int(number(a.get("minutes"), 7, 4, 15) * 60) if kind == "long" else (int(number(a.get("duration"), 40, 25, 60)) if a.get("duration") else None)      # a Short with no duration: the agent decides
        slug = resume or slug_for(title)
        (Path(c["projects_dir"]) / slug).mkdir(parents=True, exist_ok=True)     # reserve the name: a second click can't pick it too
        src = t.get("inspired_by") or {}
        brief = ""
        if t.get("brief"):                                                       # a researched pick: the agent must follow its brief
            bp = (ROOT / str(t["brief"])).resolve()
            if ROOT.resolve() in bp.parents and bp.is_file(): brief = str(bp)
        desc = clean(a.get('thumb_desc'), 1200)
        user_desc = (' THE USER DESCRIBED THE THUMBNAIL THEY WANT, in their own words. Draw exactly this (it wins over the skill style rules; the skill tests still apply and you report honestly if one fails): "' + desc + '"') if desc else ''
        thumb_now = kind == 'long' and bool(a.get('thumb_now') or desc)      # a described thumbnail is drawn now
        if kind == 'short':
            thumb_line = 'make it at make time, like every Short: follow ~/.claude/skills/line-boil-thumbnail-short/SKILL.md (step 9).' + user_desc
        elif thumb_now:
            thumb_line = 'the user chose to draw it NOW, after the video: follow ~/.claude/skills/line-boil-thumbnail-long/SKILL.md (step 6 below).' + user_desc
        else:
            thumb_line = 'do NOT make one at make time: a long video gets its own from the Better thumbnail button (three ideas, the user picks one)'
        old6_text = f'6. NO thumbnail: do not write web/thumb.js, do not run build.py thumb, do not create a thumbnail file. Write {slug}-youtube.txt for a long video (references/youtube.md, but its THUMBNAIL section is the single line "Not made yet: use the Better thumbnail button in Bean Studio", and lint the title with title.py without --thumb: no #shorts, chapters from {slug}-chapters.txt, 6 to 8 sources, tags, a pinned comment, no list of spin-off Shorts: the user has a separate button for that).'
        step6 = (f"6. Thumbnail: draw it now, following ~/.claude/skills/line-boil-thumbnail-long/SKILL.md (line-boil-wide step 10): web/thumb.js, build.py thumb {slug}, check stills/thumb-crops.png, and the YouTube sheet's THUMBNAIL section with the real File, Text, Still and Brief. Then {slug}-youtube.txt (references/youtube.md, no #shorts, chapters from {slug}-chapters.txt, 6 to 8 sources, tags, and lint the title with title.py --thumb \"<the thumbnail words>\")."
                 if thumb_now else old6_text)
        theme = a.get("theme") if a.get("theme") in THEMES else None
        theme_line = (f"{theme} (the user chose it): create the project with build.py new {slug}{' --wide' if kind == 'long' else ''} --theme {theme}" if theme else
                      f"AUTO: name the topic's genre, then pick the theme from the Genre section of the skill (a dark or dread topic such as extinction, disasters or 'what if we killed all X' is noir, history is sepia, calm is soft, money or contests is hype, most others classic), and create the project with build.py new {slug}{' --wide' if kind == 'long' else ''} --theme <that theme> (omit it for classic)")
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
- Voice: {voice}   Speed: {speed}  (build.py voice {slug} --voice {voice} --speed {speed} --target {dur or "<the seconds you chose>"})
- Tone: {clean(a.get('tone') or 'dry and deadpan, the channel default', 80)}
- Theme: {theme_line}
- Cast: {'reuse the red host bean (BEAN in the bean-avatar project) as the hero, with other beans for the other ideas' if a.get('cast') == 'host' else 'a new cast of different beans designed for this topic: one bean per idea or role, abstract ideas as costume beans (see "A cast of beans" in references/style.md)'}
- Ending: {clean(a.get('ending') or 'a punchy callback line', 80)}
- Background music: {'on, and it follows the script: musicMood() changes the mood with the feeling (see the skill)' if a.get('music', True) else 'off (pass --no-music to build.py video)'}
- Channel outro: {('appended' if a.get('outro', True) else 'left off (pass --no-outro to build.py video)') if kind == 'long' else 'none: a Short ends on its closing-hook line, then the iris closes (build.py never appends an outro to a Short)'}
- Thumbnail: {thumb_line}.
- Extra notes: {clean(a.get('notes'), 400) or 'none'}
"""
        if kind == "short":
            prompt = f"""Make a new Short with the line-boil skill. Read ~/.claude/skills/line-boil/SKILL.md and the files it points to (references/api.md, references/style.md, references/youtube.md) first, and {c['voice_file']} for the channel voice.

{common}
The user has already approved this topic and these settings, so do NOT stop to ask or to show a plan. Go straight through, and keep it lean (a typical Short is about 30 tool calls): read each reference file once and do not re-read it; score the five candidate first lines in ONE hookscore.py call (the yt-script skill, as the line-boil skill says); at most 6 web searches or fetches in total; write each file with one Write, not many small edits; check the stills in at most two rounds; then script, fact-check (search the web; hedge anything uncertain; keep the sources for the sheet), cast, shots, build.py check, stills of every shot checked for overlaps and caption placement, build.py video, build.py sheet, the thumbnail (SKILL.md step 9) and the YouTube upload sheet (step 10). Do not upload anything and do not touch other projects. Finish by printing the project folder, the title and the thumbnail text."""
        else:
            structure = clean(a.get("structure") or "as in the research brief or the topic's chapters", 80)
            prompt = f"""Make a LONG video ({dur // 60} minutes, 16:9) for the channel with the line-boil-wide skill. Read ~/.claude/skills/line-boil-wide/SKILL.md and references/wide.md, then the files they point to in ~/.claude/skills/line-boil (SKILL.md, references/api.md, references/style.md, references/youtube.md), and {c['voice_file']} for the channel voice. Use the yt-chapters, yt-seo and yt-package skills' rules for the chapters, description and title.

{common}- Structure: {structure}

The user has already approved this topic and these settings, so do NOT stop to ask or to show a plan. Go straight through, in this order:
1. build.py new {slug} --wide (it lands in {c['projects_dir']}). The HOOK first, with the yt-script skill: five candidate opening lines scored with its hookscore.py, kept in {slug}-hooks.txt with the scores, the best one used; then only the paradox in the first 30 seconds (never the answer, never a roadmap such as 'in this video'), straight into chapter 1, no channel intro and no subscribe pitch. script.json: one sentence per entry, written chapter by chapter; the last chapter is a NEW payoff (practical, or the wildest escalation), then a one- or two-sentence callback to the opening image, never a recap of the chapters. Dry, calm, honest, funny in the pictures and the last line of each chapter; no hype words.
2. Fact-check every claim with web searches of primary sources (the paper, the review, the agency page). Hedge inside the claim (about, can, typically, scientists think), never in a separate disclaimer sentence (one short safety line at most, once), drop what you cannot verify, never invent a number. Write {slug}-sources.md: claim, link, and how far you verified it (full text, abstract only, secondary report).
3. chapters.json (5 to 9 chapters, [{{"title", "line"}}], titles of 3 to 5 words that promise what the section gives, as the yt-chapters skill says), then build.py voice {slug} --voice {voice} --speed {speed} --target {dur}; rewrite and re-run until it prints TARGET {dur}s: OK; then build.py chapters {slug} until it prints "valid".
4. The SCENE AND SOUND PLAN: {slug}-plan.md, one row per chapter with the set and place, time of day and colour, the beans on screen, props, the music mood and why, the sound or silence beat and the joke (the scenes and the music must change with what the script says: see references/wide.md). Then a cast of different beans (see "A cast of beans" in references/style.md) in web/cast.js, then web/shots/ch01.js, ch02.js, ... ONE CHAPTER AT A TIME: write the chapter's shots, render 2 or 3 stills per chapter with build.py stills (read the single stills/sheet.jpg it writes), fix what is wrong, then the next chapter. build.py check must show no [error], no shot over 20 s and no music warning (use setScene() sets and musicMood() moods, at least 4 moods).
   Burned-in captions: {'ON (set CAP.on = true at the top of cast.js)' if a.get('captions') else 'OFF, the long-form standard: the .srt is uploaded as YouTube captions; put numbers and key words on screen as label shapes'}.
5. build.py video {slug}{'' if a.get('music', True) else ' --no-music'}{'' if a.get('outro', True) else ' --no-outro'}, then build.py sheet {slug} and look at the sheet once.
6. {step6}
Do not upload anything and do not touch other projects. Finish by printing the project folder, the real length, the chapters, the title, and anything you could not verify (the thumbnail is made afterwards from the Better thumbnail button)."""
        proj = Path(c["projects_dir"]) / slug
        planned = bool(resume) and (proj / "script.json").exists() and (proj / f"{slug}-shotplan.md").exists() and (proj / "audio" / "words.json").exists()
        if resume: prompt += resume_note(slug, kind == "long", planned)
        (DATA / "make").mkdir(parents=True, exist_ok=True)
        save_json(DATA / "make" / f"{slug}.json", {"kind": kind, "topic": t, "answers": a, "when": dt.datetime.now().isoformat(timespec="seconds")})
        mode = "window" if (a.get("window") or c.get("agent_window")) else "feed"      # watch it live, or in its own Claude window
        model = a.get("model") if a.get("model") in ("opus", "sonnet", "haiku") else (c.get("plan_model") or None)      # one run (own window, or staging off): the polished model
        staged = bool(start_staged) and bool(c.get("staged_make", True)) and mode != "window" and not a.get("model")      # a model picked in the form means one run on that model
        if staged:
            plan_note, build_note = stage_notes(slug, kind == "long")
            stages = [{"name": "Plan: script, hook and shot plan", "model": c.get("plan_model") or None, "prompt": prompt + plan_note,
                       "expect": [str(proj / "script.json"), str(proj / f"{slug}-shotplan.md")]},
                      {"name": "Build: code, render and sheet", "model": c.get("build_model") or None, "prompt": prompt + build_note, "expect": []}]
            j = start_staged(f"make · {slug}", stages[1:] if planned else stages)       # the plan is finished and saved: only the build is left, so the paid plan does not run twice
        else:
            j = run_agent(f"make · {slug}", prompt, model, mode)
        return jsonify(job=j["id"], project=slug, title=title, kind=kind, mode=mode, staged=staged)
