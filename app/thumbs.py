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
    """2 to 6 words, upper case (the title's key words, topic named outright)"""
    return " ".join(re.findall(r"[A-Za-z0-9$%'?!+\u2192-]+", str(v or "").upper())[:6])


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

Read: {p / 'script.json'} (the whole voiceover), {p / (name + '-youtube.txt')} (title and current thumbnail brief; title now: "{title_of(p) or 'unknown'}"), {p / (name + '-sources.md')} if it exists, {p / 'web' / 'cast.js'} (the characters and props we can draw), {p / 'web' / 'thumb.js'} (the current thumbnail code) and, if it exists yet, look at the current picture {p / (name + '-thumbnail.png')} (a long video has none until this runs). Also read the thumbnail rules in {ENGINE_SKILL}/SKILL.md (step 9) and, for a long video, {ENGINE_SKILL.replace('line-boil', 'line-boil-wide')}/references/wide.md ("16:9 thumbnails").

First, in two lines, say honestly what is WRONG with the current thumbnail if there is one (does a stranger know what the video is about in one second? is there one clear subject? is there a reason to click?), or what the thumbnail must achieve for this topic if there is none. Then write FIVE different thumbnail ideas for a {size}.

The goal: a viewer scrolling at feed size (about 246 px wide) knows EXACTLY what the video is about in one second, and feels they want the answer. The model to copy is a TED-Ed thumbnail: big plain lettering "HOW DOES CAFFEINE KEEP US AWAKE?" with one big character yawning in a chair beside a mug. Nothing is cryptic. Rules:
- THE WORDS STATE THE TOPIC, OUTRIGHT. The on-image text is the title's key words in plain language, 2 to 6 words (a question is best), with the topic noun biggest and in the strongest colour. Repeating the title is wanted. Cover the picture: the words alone must say exactly what the video is about. A teaser that hides the topic ("3 PM TO MIDNIGHT", "NOPE", a bare number) is a FAIL.
- THE PICTURE SAYS THE SAME THING: ONE big character doing the topic's action (yawning, panicking, staring at it) beside the topic's own object, drawn large (at least a third of the frame). Cover the words: a stranger should still guess the topic. No second idea, no clutter.
- ONE strong, readable emotion on that character, exaggerated.
- Add the hook on top of the topic, never instead of it: phrase the words as the question the viewer wants answered, or add a short stake word ("...AT NIGHT?", "...WITHOUT KNOWING?"), but only a promise this video pays off honestly (no lies, no fake numbers).
- Flat high-contrast palette colours, a clean background, nothing important in the bottom-right corner (the duration badge) or in the bottom 15%.
- The five ideas differ in the picture and the hook angle, each on a DIFFERENT trigger from: {', '.join(TRIGGERS)}; all five name the topic in their words. At least one leans on fear or loss the video honestly delivers on, at least one on curiosity.

Be unbiased and strict: rank them by how likely a stranger is to click AND feel the video delivered, best first.

Write a JSON array of exactly 5 objects to {out} and nothing else on disk (no other file changes). Each object:
{{"name": "3 to 6 word label", "trigger": one of the triggers, "words": "the on-image text: the title's key words naming the topic, 2 to 6 words", "concept": "the whole picture in two sentences: what is drawn, where, doing what", "subject": "the one big object", "face": "which bean, what expression", "why": "one sentence: what makes a stranger click and why the video pays it off", "risk": "one sentence: how this could mislead or fail, and how it is avoided"}}
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
- Words on the image (the topic named outright, 2 to 6 words, big; repeating the title "{title}" is fine and wanted): {words or '(the title shortened to its key words, as a question)'}
- Why it should work: {clean(i.get('why'))}
- Watch out for: {clean(i.get('risk'))}

How:
1. Read {ENGINE_SKILL}/SKILL.md step 9 and {ENGINE_SKILL}/references/api.md, {p / 'web' / 'cast.js'} and the current {p / 'web' / 'thumb.js'}. If {p / (name + '-thumbnail.png')} exists, first copy it to {p / (name + '-thumbnail-prev.png')} (keep the old one); if web/thumb.js does not exist yet, create it.
2. Rewrite {p / 'web' / 'thumb.js'} (CAP.on = false, one still shot, flat high-contrast palette colours, {'1280x720: the words in the upper left or left third, faces in the middle and right, nothing important in the bottom 15% of the right 20% (duration badge)' if wide else '1080x1920: headline, subject and faces inside gridSafe'}). Draw the big subject large (at least a third of the frame, recognisable by silhouette); add props to cast.js if the subject does not exist yet.
3. Run: {py} {eng} thumb {name} and look at stills/thumb-crops.png (full, small feed size, and the badge corner). Judge the SMALL copy only:
   - Subject test: cover the words. Can a stranger name the topic from the picture alone (one big character doing the topic's action beside the topic's own object)?
   - Topic test: cover the picture. Do the words alone say exactly what the video is about (the topic noun is in them)? Compare with a TED-Ed style "HOW DOES CAFFEINE KEEP US AWAKE?".
   - Click test: is there one strong emotion, one unresolved thing, nothing cluttered, nothing in the badge corner?
   Fix and re-render until all three pass (at most 5 rounds). Be strict.
4. In {p / (name + '-youtube.txt')} update the THUMBNAIL section (File:, Text:, Still:, Brief:) to match what you drew (replace a "Not made yet" line); the title linter's "thumbnail repeats the title" flag is intentionally ignored. Change nothing else in that file.
5. Finish by printing the final text, what is drawn, and the result of each of the three tests, honestly (say so if one still fails)."""
        j = start_agent(f"thumb · {name}", prompt, model(), "feed")
        return jsonify(job=j["id"], project=name)
