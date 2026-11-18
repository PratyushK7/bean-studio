"""One Claude session per video. "+ New video" makes the project folder and opens a new, visible Claude window that works on
that video only; its session id is remembered, so the video's card can reopen the same conversation later (claude --resume).

The session runs interactively (you watch it and answer its questions), in the repo root so CLAUDE.md and the tools apply.
It is told to stop at Gate A (the owner approves the script) and to ask before anything paid.
register(app, ROOT, cfg, start_job, JOBS) adds /api/sessions*; data() is where sessions.json lives (the channel data folder).
"""
import datetime as dt, json, re, uuid
from pathlib import Path
from flask import abort, jsonify, request

import channels, store

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
HI_FORMATS = {"economics": "Economics of owning X", "story": "Company rise/split/fall", "person": "A person's story", "compare": "Two people, one decision"}
STOP = {"the", "a", "an", "of", "and", "to", "in", "on", "for", "how", "why", "what", "is", "are", "does", "do", "its", "it", "ka", "ki", "ke", "hai"}


def slugify(text):
    words = [w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP][:5]
    return "-".join(words)[:50].strip("-")


def clean(s, n):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def new_prompt(c, p, topic, fmt, notes):
    """the first message of a new video's session: what to make, where, and where to stop"""
    if (c.get("language") or "").lower() == "hindi":
        return (f'This Claude session makes one video for the channel "{c["channel"]}" and nothing else. Its project folder is {p} (it exists). '
                f"Topic: {topic}. Format: {fmt} ({HI_FORMATS[fmt]}). " + (f"Notes from the owner: {notes}. " if notes else "") +
                "Use the hindi-case-study skill (read ~/.claude/skills/hindi-case-study/SKILL.md, references/craft.md, references/study.md and ~/.claude/youtube/voice-hindi.md first). "
                "Start with the YouTube competitor research (SKILL.md step 2: the top five videos with python tools/yt_research.py, their claims checked independently, what they miss), "
                "then write the research, engine, beats and hooks files, script.json and <slug>-script.md (casecheck.py --md) in the project folder, run casecheck.py, "
                "run the editorial check (section 10) and fix only the weak areas, then give the hand-back and STOP at Gate A: the owner reads the script and hears the free preview before anything else. "
                "After the owner approves, continue the pipeline in this same session one step at a time (python tools/vyapaar_steps.py <project> <step>, the same steps as the Pipeline tab). "
                "Never start a paid step (the Sarvam voice, clips, any paid API) without the owner's OK on the cost, and never touch other projects.")
    return (f'This Claude session makes one video for the channel "{c["channel"]}" and nothing else. Its project folder is {p} (it exists). '
            f"Topic: {topic}. " + (f"Notes from the owner: {notes}. " if notes else "") +
            "Use the line-boil skill (read ~/.claude/skills/line-boil/SKILL.md first; line-boil-wide for a long video). "
            "Show the owner the script and hook before building, ask before anything paid, and never touch other projects.")


def resume_prompt(c, p):
    """the first message when a video that had no session yet gets one"""
    skill = "hindi-case-study" if (c.get("language") or "").lower() == "hindi" else "line-boil"
    return (f'This Claude session works on one existing video for the channel "{c["channel"]}" and nothing else: {p}. '
            f"Read its files (and ~/.claude/skills/{skill}/SKILL.md) to see how far it is, tell the owner in a few lines, and wait for what to do next. "
            "Never start a paid step without the owner's OK on the cost, and never touch other projects.")


def register(app, ROOT, cfg, start_job, JOBS, data=None):
    def book():
        return (data() if data else channels.data_for(ROOT)) / "sessions.json"

    def running(slug):
        cid = cfg()["channel_id"]
        return next((j for j in JOBS.values() if j["label"] == f"session · {slug}" and j["channel"] == cid and not j["done"]), None)

    def launch(slug, extra, prompt=None):
        c = cfg()
        cmd = [x for x in c["agent_command"] if x != "-p"] + extra + ([prompt] if prompt else [])   # interactive: no -p
        return start_job(f"session · {slug}", cmd, c["agent_cwd"], window=True)

    def remember(slug, sid, topic):
        f = book()
        with store.lock_for(f):
            s = store.read(f, {}) or {}
            s[slug] = {"session": sid, "topic": topic, "started": dt.datetime.now().isoformat(timespec="seconds")}
            store.write(f, s)

    @app.get("/api/sessions")
    def sessions_list():
        s = store.read(book(), {}) or {}
        return jsonify(sessions={k: {**v, "running": bool(running(k))} for k, v in s.items()})

    @app.post("/api/sessions/new")
    def sessions_new():
        b = request.get_json(silent=True) or {}
        c = cfg()
        topic, notes = clean(b.get("topic"), 300), clean(b.get("notes"), 800)
        if not topic: abort(400, "write what the video is about")
        slug = str(b.get("slug") or "").strip() or slugify(topic)
        if not SLUG.match(slug): abort(400, "give it a short name in English: lowercase letters, numbers and dashes (e.g. petrol-pump-economics)")
        fmt = b.get("format") if b.get("format") in HI_FORMATS else "economics"
        p = Path(c["projects_dir"]) / slug
        if p.exists(): abort(409, f"a video called {slug} already exists: open its session from its card, or pick another name")
        for sub in ("prompts", "images", "assets"): (p / sub).mkdir(parents=True)
        sid = str(uuid.uuid4())
        model = c.get("plan_model") or "opus"                          # the script is the judgment step
        j = launch(slug, ["--session-id", sid, "--name", f"video · {slug}", "--model", model], new_prompt(c, p, topic, fmt, notes))
        remember(slug, sid, topic)
        return jsonify(project=slug, session=sid, job=j["id"])

    @app.post("/api/sessions/<slug>/open")
    def sessions_open(slug):
        """reopen the video's own conversation; a video with none yet gets a new session that first looks at where it is"""
        c = cfg()
        if not SLUG.match(slug or ""): abort(400, "bad project name")
        p = Path(c["projects_dir"]) / slug
        if not p.is_dir(): abort(404, "no such video")
        if running(slug): abort(409, "its Claude window is already open")
        old = (store.read(book(), {}) or {}).get(slug)
        if old:
            j = launch(slug, ["--resume", old["session"]])
            return jsonify(project=slug, session=old["session"], job=j["id"], resumed=True)
        sid = str(uuid.uuid4())
        j = launch(slug, ["--session-id", sid, "--name", f"video · {slug}", "--model", c.get("plan_model") or "opus"], resume_prompt(c, p))
        remember(slug, sid, "")
        return jsonify(project=slug, session=sid, job=j["id"], resumed=False)
