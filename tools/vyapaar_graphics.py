"""Decoding Vyapaar motion graphics: every card line and every on-screen label, drawn in one design system (channels/hindi/visual-bible.json
`graphics`) by tools/video/graphics.html in Chromium (so Devanagari shapes correctly), timed to the line it sits under.

    python tools/vyapaar_graphics.py <project> [--lines voice-lines.json] [--script script.json] [--plan visual-plan.json] [--only G003,G006]

Card lines get their spec from visual-plan.json (shot "graphic": number, bill, stack, bars, change, line, share, flow, title, triad); a script
with no plan falls back to a plain title card of the line's `screen` text. Still lines with `screen` text get a lower-third label (a transparent
PNG the renderer fades in). Outputs: graphics/G003-<hash>.mp4 and graphics/G003.jpg (a preview still), graphics/labels/L025-<hash>.png.
A graphic is re-rendered only when its spec, its length or the design tokens change. graphics/report.json lists any text that overflows.
Element timing: an element with a cue word appears when that word is said (its position in the line, a close estimate without word timings).
"""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vyapaar_visual as vv

JS = Path(__file__).resolve().parent / "video" / "render_graphics.js"


def durations(T, n_lines):
    """seconds each line holds on screen: from its start to the next line's start (the last one gets one extra second)"""
    out = []
    for i in range(n_lines):
        nxt = T[i + 1]["start"] if i + 1 < len(T) else T[i]["end"] + 1.0
        out.append(max(1.0, nxt - T[i]["start"]))
    return out


def cue_time(text, word, dur):
    words = re.findall(r"\S+", text or "")
    for k, w in enumerate(words):
        if word in w: return round(max(0.3, dur * k / max(len(words), 1) - 0.15), 2)
    return None


def spec_for(line, shot):
    if shot and shot.get("graphic"): return dict(shot["graphic"])
    s = (line.get("screen") or "").strip() or "…"                     # no plan: a plain title card of the screen text (older projects)
    return {"type": "title", "title": s}


def jobs_for(proj, L, T, plan, only=None, lines_only=None):
    bible = vv.load_bible(proj); tok = bible["graphics"]; fps = bible["render"]["fps"]
    tpl = hashlib.sha1((Path(__file__).resolve().parent / "video" / "graphics.html").read_bytes()).hexdigest()[:8]   # a template change re-renders
    gd = proj / "graphics"; (gd / "labels").mkdir(parents=True, exist_ok=True)
    D = durations(T, len(L)); by_line = {}
    for sh in (plan or {}).get("shots", []):
        for n in vv.lines_of(sh): by_line[n] = sh
    jobs, out = [], {"cards": {}, "labels": {}}
    for i, l in enumerate(L, 1):
        if lines_only and i not in lines_only: continue
        sh = by_line.get(i)
        is_card = l.get("kind") == "card" or (sh and (sh.get("kind") == "graphic" or sh.get("graphic")))
        if is_card:
            gid = sh["id"] if sh else f"G{i:03d}"
            if only and gid not in only: continue
            spec = spec_for(l, sh); dur = round(D[i - 1], 3)
            start = 0.0; lead = spec.pop("lead_in", None); sc = spec.pop("start_cue", None)
            if sc:                                                   # the graphic starts on this word; a picture carries the words before it
                start = cue_time(l.get("hi", ""), sc, dur) or 0.0
                start = start if start >= 1.0 and dur - start >= 2.5 else 0.0
                dur = round(dur - start, 3)
            cues = list(spec.pop("cues", []) or ([spec.pop("cue_to")] if spec.get("cue_to") else []))
            times = [None if cue_time(l.get("hi", ""), w, D[i - 1]) is None else max(0.3, cue_time(l.get("hi", ""), w, D[i - 1]) - start) for w in cues] if cues else None
            spec.pop("facts", None); spec.pop("allow", None); spec.pop("allow_reason", None)
            h = hashlib.sha1(json.dumps([spec, dur, tok, times, fps, tpl], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]
            alpha = (tok.get("backdrop") or {}).get("mode") == "picture"
            mp4 = gd / f"{gid}-{h}.{'mov' if alpha else 'mp4'}"
            out["cards"][i] = {"id": gid, "file": str(mp4), "dur": dur, "type": spec.get("type"), "start": start, "lead_in": lead}
            if not mp4.exists():
                jobs.append({"id": gid, "spec": spec, "dur": dur, "fps": fps, "tokens": tok, "times": times, "out": str(mp4), "alpha": alpha,
                             "preview": str(gd / f"{gid}.{'png' if alpha else 'jpg'}")})
        elif (l.get("screen") or "").strip():
            text = l["screen"].strip()
            spec = {"type": "label", "text": text}
            h = hashlib.sha1(json.dumps([spec, tok, tpl], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]
            png = gd / "labels" / f"L{i:03d}-{h}.png"
            out["labels"][i] = {"file": str(png), "text": text}
            if not png.exists() and not only: jobs.append({"id": f"L{i:03d}", "spec": spec, "tokens": tok, "png": str(png)})
    return jobs, out


def render(proj, script=None, lines="voice-lines.json", plan_name="visual-plan.json", only=None, lines_only=None):
    proj = Path(proj); L = vv.script_lines(proj, script)
    T = vv.load_json(proj / lines)
    if not T: sys.exit(f"no {lines}: the graphics are timed to the voice (or the free listen's preview-local-lines.json)")
    if len(T) != len(L): sys.exit(f"{lines} has {len(T)} lines but the script has {len(L)}: they belong to different versions")
    plan = vv.load_json(proj / plan_name) if plan_name else None
    jobs, out = jobs_for(proj, L, T, plan, only, lines_only)
    gd = proj / "graphics"
    if jobs:
        jf = gd / "jobs.json"; jf.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"rendering {len(jobs)} graphic(s) and label(s) in Chromium...", flush=True)
        subprocess.run(["node", str(JS), str(jf)], check=True)
        rep = vv.load_json(gd / "jobs-report.json", [])
        old = {r["id"]: r for r in vv.load_json(gd / "report.json", [])}
        for r in rep: old[r["id"]] = r
        (gd / "report.json").write_text(json.dumps(list(old.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    for f in gd.glob("G*.png"):                                  # alpha previews: show them on the dark tint, as they read over a darkened scene
        from PIL import Image
        im = Image.open(f).convert("RGBA"); bg = Image.new("RGBA", im.size, (23, 19, 15, 255)); bg.alpha_composite(im); bg.convert("RGB").save(f.with_suffix(".jpg"), quality=90)
    rep = vv.load_json(gd / "report.json", [])
    probs = [r for r in rep if r.get("overflow") or r.get("error")]
    for r in probs: print(f"  {r['id']}: {r.get('error') or '; '.join(r['overflow'])}")
    (gd / "manifest.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"graphics: {len(out['cards'])} cards, {len(out['labels'])} labels ({len(jobs)} newly rendered); {len(probs)} with text problems -> {gd}")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lines", default="voice-lines.json"); ap.add_argument("--script")
    ap.add_argument("--plan", default="visual-plan.json"); ap.add_argument("--only")
    a = ap.parse_args()
    render(a.project, a.script, a.lines, None if a.plan == "none" else a.plan, set(a.only.split(",")) if a.only else None)


if __name__ == "__main__":
    main()
