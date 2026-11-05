"""Bean Studio: a better thumbnail for a finished video, in two steps, both on Opus (the thumbnail is the biggest lever on clicks).
  1. POST /api/thumbnail/ideas {project}   an agent reads the video's script, title and current thumbnail and writes FIVE different
                                           thumbnail ideas, each built on a different click trigger; GET /api/thumbnail/ideas/<project> reads them.
  2. POST /api/thumbnail/make {project, idea}   the picked idea is drawn (web/thumb.js), rendered, checked at feed size, fixed, and saved
                                           (the old one is kept as <project>-thumbnail-prev.png). Nothing is uploaded."""
import json, re, time
from pathlib import Path
from flask import abort, jsonify, request

TRIGGERS = ("Curiosity", "Fear", "Shock", "Stakes", "Mystery", "Before / after", "Absurd")
ENGINE_SKILL = "~/.claude/skills/line-boil"


def clean(v, n=300):
    return re.sub(r"\s+", " ", str(v or "")).strip()[:n]


def title_of(p):
    """the title from <project>-youtube.txt (the line under == TITLE ==), else ''"""
    f = p / f"{p.name}-youtube.txt"
    if f.exists():
        m = re.search(r"== TITLE ==\s*\n(.+)", f.read_text(encoding="utf-8", errors="replace"))
        if m: return m.group(1).strip()
    return ""


def words_of(v):
    """up to 3 words, upper case"""
    return " ".join(re.findall(r"[A-Za-z0-9$%'?!+\u2192-]+", str(v or "").upper())[:3])


def register(app, ROOT, cfg, start_agent, proj_dir, JOBS):
    def model():
        return cfg().get("thumbnail_model") or "opus"

    def ideas_file(p): return p / f"{p.name}-thumb-ideas.json"          # the saved five (what the button shows)
    def new_file(p): return p / f"{p.name}-thumb-ideas-new.json"        # a reroll in progress: replaces the saved five only when it is done

    def label_of(name): return f"thumb ideas · {name}"

    def running_job(name):
        return next((j for j in JOBS.values() if j["label"] == label_of(name) and not j.get("done")), None)

    def load(path):
        try: return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        except Exception: return None

    def sanitise(raw):
        ideas = []
        for o in (raw if isinstance(raw, list) else []):
            if not isinstance(o, dict) or not clean(o.get("concept")): continue
            ideas.append({"name": clean(o.get("name"), 60) or "Idea", "trigger": o.get("trigger") if o.get("trigger") in TRIGGERS else "Curiosity",
                          "words": words_of(o.get("words")), "concept": clean(o.get("concept")), "subject": clean(o.get("subject"), 120),
                          "face": clean(o.get("face"), 120), "why": clean(o.get("why")), "risk": clean(o.get("risk"))})
        return ideas[:5]

    def harvest(p, jobs):
        """a finished batch that nobody collected (the window was closed): the agent's side file, else what it printed, else nothing"""
        ideas = sanitise(load(new_file(p)))
        for j in jobs:
            if ideas: break
            m = re.search(r"\[\s*\{.*\}\s*\]", "\n".join(j["log"]), re.S)
            try: ideas = sanitise(json.loads(m.group(0)) if m else None)
            except Exception: ideas = []
        if ideas:
            ideas_file(p).write_text(json.dumps(ideas, indent=1), encoding="utf-8"); new_file(p).unlink(missing_ok=True)
        return ideas

    @app.post("/api/thumbnail/ideas")
    def thumb_ideas():
        name = (request.get_json(silent=True) or {}).get("project", "")
        p = proj_dir(name)
        wide = (p / "project.json").exists() and "wide" in (p / "project.json").read_text(encoding="utf-8", errors="replace")
        if not (p / "script.json").exists(): abort(400, "this video has no script yet")
        busy = running_job(name)
        if busy: return jsonify(job=busy["id"], project=name, running=True)      # already analysing: reattach, don't pay for a second run
        out = new_file(p)
        out.unlink(missing_ok=True)                                              # never read a stale batch
        size = "1280x720 (16:9, web/thumb.js, one still shot)" if wide else "1080x1920 (9:16 cover, web/thumb.js, gridSafe)"
        prompt = f"""You are the thumbnail strategist for the YouTube channel "{cfg()['channel']}": hand-drawn cartoon explainers told by beans. The video is {name} in {p}.

Read: {p / 'script.json'} (the whole voiceover), {p / (name + '-youtube.txt')} (title and current thumbnail brief; title now: "{title_of(p) or 'unknown'}"), {p / (name + '-sources.md')} if it exists, {p / 'web' / 'cast.js'} (the characters and props we can draw), {p / 'web' / 'thumb.js'} (the current thumbnail code) and look at the current picture {p / (name + '-thumbnail.png')}. Also read the thumbnail rules in {ENGINE_SKILL}/SKILL.md (step 9) and, for a long video, {ENGINE_SKILL.replace('line-boil', 'line-boil-wide')}/references/wide.md ("16:9 thumbnails").

First, in two lines, say honestly what is WRONG with the current thumbnail (does a stranger know what the video is about in one second? is there one clear subject? is there a reason to click?). Then write FIVE different thumbnail ideas for a {size}.

The goal: a viewer scrolling at feed size (about 246 px wide) understands the topic in one second AND feels they must click to resolve something. Use real click psychology, but only promises this video actually pays off (no lies, no fake numbers, no hype the video cannot back):
- ONE huge subject that makes the topic obvious from the picture alone (cover the words: is it still clear?). A bean's face is never the subject on its own.
- ONE strong emotion on one face (shock, dread, smug, panic), exaggerated, with the eyes looking at the thing that matters.
- A curiosity gap or a stake: something unresolved that the video resolves (a loss the viewer might be suffering without knowing, a surprising contrast, a thing that looks wrong).
- At most 3 words, big, none repeated from the title, adding information the picture lacks (a number, a time, a stake, a question). Words and picture must be one message, not two.
- Flat high-contrast colours from the palette, a clean background, nothing important in the bottom-right corner (the duration badge) or in the bottom 15%.
- Each idea uses a DIFFERENT trigger from this list: {', '.join(TRIGGERS)}. At least one must be built on fear or loss that the video honestly delivers on (for example a hidden cost), and at least one on curiosity.

Be unbiased and strict: rank them by how likely a stranger is to click AND feel the video delivered, best first.

Write a JSON array of exactly 5 objects to {out} and nothing else on disk (no other file changes). Each object:
{{"name": "3 to 6 word label", "trigger": one of the triggers, "words": "the on-image text, up to 3 words", "concept": "the whole picture in two sentences: what is drawn, where, doing what", "subject": "the one big object", "face": "which bean, what expression", "why": "one sentence: what makes a stranger click and why the video pays it off", "risk": "one sentence: how this could mislead or fail, and how it is avoided"}}
Do not use any other tool than reading files and writing that one file. When done, print the same JSON array as your final message."""
        j = start_agent(label_of(name), prompt, model(), "plain")
        return jsonify(job=j["id"], project=name)

    @app.get("/api/thumbnail/ideas/<name>")
    def thumb_ideas_get(name):
        """What the button shows. Never starts a run. status: running | done | failed | none"""
        p = proj_dir(name)
        j = JOBS.get(request.args.get("job", "")) or running_job(name)
        if j and not j.get("done"):
            saved = sanitise(load(ideas_file(p)))
            return jsonify(status="running", ideas=[] if request.args.get("job") else saved, log=j["log"][-3:])
        finished = sorted((x for x in JOBS.values() if x["label"] == label_of(name) and x.get("done")), key=lambda x: x.get("started", 0), reverse=True)
        saved_at = ideas_file(p).stat().st_mtime if ideas_file(p).exists() else 0
        if request.args.get("job") or new_file(p).exists() or (finished and finished[0].get("started", 0) > saved_at):
            got = harvest(p, finished)                                           # a batch just finished (or finished unseen): it replaces the saved five
            if got: return jsonify(status="done", ideas=got)
            if request.args.get("job"): return jsonify(status="failed", ideas=sanitise(load(ideas_file(p))))
        saved = sanitise(load(ideas_file(p)))
        return jsonify(status="done" if saved else "none", ideas=saved)

    @app.post("/api/thumbnail/make")
    def thumb_make():
        b = request.get_json(silent=True) or {}
        p = proj_dir(b.get("project", "")); name = p.name
        i = b.get("idea") or {}
        concept = clean(i.get("concept"))
        if not concept: abort(400, "no idea picked")
        title = title_of(p)
        words = words_of(i.get("words"))
        wide = (p / "project.json").exists() and "wide" in (p / "project.json").read_text(encoding="utf-8", errors="replace")
        py, eng = cfg()["python"], cfg()["engine"]
        prompt = f"""Redraw the thumbnail for the video {name} in {p}, to this idea picked by the user. Nothing else changes: do not touch the video, script, chapters, other projects, and upload nothing.

THE IDEA ({clean(i.get('trigger'), 30)}): {clean(i.get('name'), 60)}
- Picture: {concept}
- The one big subject: {clean(i.get('subject'), 120)}
- Face: {clean(i.get('face'), 120)}
- Words on the image (at most 3, big, none repeated from the title "{title}"): {words or '(choose up to 3 that add a number, a stake or a question)'}
- Why it should work: {clean(i.get('why'))}
- Watch out for: {clean(i.get('risk'))}

How:
1. Read {ENGINE_SKILL}/SKILL.md step 9 and {ENGINE_SKILL}/references/api.md, {p / 'web' / 'cast.js'} and the current {p / 'web' / 'thumb.js'}. First copy the current picture {p / (name + '-thumbnail.png')} to {p / (name + '-thumbnail-prev.png')} (keep the old one).
2. Rewrite {p / 'web' / 'thumb.js'} (CAP.on = false, one still shot, flat high-contrast palette colours, {'1280x720: the words in the upper left or left third, faces in the middle and right, nothing important in the bottom 15% of the right 20% (duration badge)' if wide else '1080x1920: headline, subject and faces inside gridSafe'}). Draw the big subject large (at least a third of the frame, recognisable by silhouette); add props to cast.js if the subject does not exist yet.
3. Run: {py} {eng} thumb {name} and look at stills/thumb-crops.png (full, small feed size, and the badge corner). Judge the SMALL copy only:
   - Subject test: cover the words. Can a stranger name the topic from the picture alone?
   - Text test: cover the picture. Do the words alone point at the topic or its stakes, in at most 3 words, without repeating the title?
   - Click test: is there one strong emotion, one unresolved thing, nothing cluttered, nothing in the badge corner?
   Fix and re-render until all three pass (at most 5 rounds). Be strict.
4. In {p / (name + '-youtube.txt')} update the THUMBNAIL section (Text:, Still:, Brief:) to match what you drew; change nothing else in that file.
5. Finish by printing the final text, what is drawn, and the result of each of the three tests, honestly (say so if one still fails)."""
        j = start_agent(f"thumb · {name}", prompt, model(), "feed")
        return jsonify(job=j["id"], project=name)
