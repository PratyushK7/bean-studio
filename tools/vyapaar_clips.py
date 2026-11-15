"""Decoding Vyapaar image-to-video clips: chosen for the story, briefed shot by shot, inspected before use. Paid steps never run by surprise.

    python tools/vyapaar_clips.py <project> select [--budget 2.0] [--seconds 4]   # pick the shots that earn motion -> clips-plan.json (free)
    python tools/vyapaar_clips.py <project> prompts                              # print each planned clip's motion brief (free)
    python tools/vyapaar_clips.py <project> make --approve-cost [--only 5,74]    # xAI image-to-video for planned clips (PAID: shows the cost first)
    python tools/vyapaar_clips.py <project> check [--only 5]                     # inspect clips: flicker, jumps, identity drift, softening -> clips/review/
    python tools/vyapaar_clips.py <project> approve 5,74 [--note ".."] | reject 5 --note ".."   # the renderer uses approved clips only
    python tools/vyapaar_clips.py <project> fps-test 5                           # repeat-to-30 vs motion interpolation, measured (free)
The older form (python tools/vyapaar_clips.py <project> --pick | --dry | --only ..) runs tools/vyapaar_clips_legacy.py, also cost-gated.

Selection weighs the story (the hook, reveals, reversals, payoffs, the plan's important shots, shots with a written motion brief) against what
image-to-video does badly (crowds morph, hands warp, papers and screens grow text). The picture must be approved in Gate 1 before it is animated.
The brief says where the shot starts and ends, what moves (one or two things), what must stay still, and that the face, clothes and painted
style must not change. Clips are kept at their native frame rate; the renderer conforms them (bible render.clips.conform), and fps-test shows
whether interpolation would actually be cleaner.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vyapaar_visual as vv

COST_PER_S = 0.032            # xAI grok-imagine-video 720p, as measured on the first 25 clips
FONT = "C:/Windows/Fonts/segoeui.ttf"
RULES = ("Keep the face, hair and clothes exactly as in the image, and the same painted illustration style. Motion is restrained and physically "
         "plausible; nothing new appears; no text; no morphing, no flicker, no sudden camera jumps; hands keep five natural fingers; the background stays stable.")


def plan_shots(proj):
    plan = vv.load_json(proj / "visual-plan.json"); L = vv.script_lines(proj, (plan or {}).get("script"))
    by_line = {}
    for sh in (plan or {}).get("shots", []):
        for n in vv.lines_of(sh): by_line.setdefault(n, sh)
    return plan, L, by_line


def brief(sh, plan, seconds):
    """the motion prompt: authored in the plan (`motion`), or a conservative default from the shot's size"""
    m = dict(sh.get("motion") or {}); names = [plan["characters"][c]["name"] for c in (sh.get("chars") or {}) if not str(sh["chars"][c]).startswith("only")]
    if not m:
        if sh.get("size") in ("close", "medium_close", "reaction"):
            m = {"start": "the framing of the image", "subject": "a slow breath and one natural blink", "camera": "a very slow push in", "intensity": "very low",
                 "end": "slightly closer, same expression", "still": "the background and everything behind the person"}
        elif sh.get("size") in ("establishing", "wide"):
            m = {"start": "the framing of the image", "environment": "light, natural movement in the background (a few passers-by, a flicker of light)",
                 "camera": "a slow lateral drift", "intensity": "low", "end": "the same place a little further along", "still": "the buildings and the main subject"}
        else:
            m = {"start": "the framing of the image", "subject": "a small natural movement", "camera": "a slow push in", "intensity": "low",
                 "end": "slightly closer", "still": "the background"}
    s = m.get("seconds", seconds)
    parts = [f"A {s}-second shot. Start: {m.get('start', 'the framing of the image')}."]
    for k in ("subject", "face", "environment"):
        if m.get(k): parts.append(m[k].rstrip(".")[:1].upper() + m[k].rstrip(".")[1:] + ".")
    parts.append(f"Camera: {m.get('camera', 'locked off')}. Motion intensity: {m.get('intensity', 'low')}.")
    if m.get("still"): parts.append(f"These stay still: {m['still']}.")
    parts.append(f"End on: {m.get('end', 'the same framing')}.")
    if names: parts.append(f"{' and '.join(names)} must look exactly like the image.")
    parts.append(RULES)
    return " ".join(parts), s


def select(proj, budget, seconds):
    plan, L, by_line = plan_shots(proj)
    if not plan: sys.exit("select needs visual-plan.json (the plan says which shots matter); the older --pick flow is in vyapaar_clips_legacy.py")
    T = vv.load_json(proj / "voice-lines.json") or vv.load_json(proj / "preview-local-lines.json")
    idx = {e.get("shot"): e for e in vv.load_json(proj / "images-index.json", []) if e.get("shot")}
    rows = []
    for i, l in enumerate(L, 1):
        sh = by_line.get(i)
        if not sh or sh.get("kind") == "graphic" or l.get("kind") == "card" or sh.get("same_as"): continue
        text = " ".join(str(sh.get(k, "")) for k in ("action", "fg", "mg", "bg"))
        score, why = 0, []
        if i <= 3 or "hook" in sh.get("purpose", ""): score += 3; why.append("hook")
        if l.get("tag") in ("reveal", "reversal", "payoff"): score += 2; why.append(l["tag"])
        if l.get("chapter"): score += 1; why.append("chapter start")
        if sh.get("candidates", 1) > 1: score += 1; why.append("important shot")
        if sh.get("motion"): score += 3; why.append("motion brief written")
        people = [c for c, h in (sh.get("chars") or {}).items() if not str(h).startswith("only")]
        if sh.get("size") in ("close", "medium_close", "medium", "two_shot") and 1 <= len(people) <= 2: score += 1; why.append("faces animate well")
        if sh.get("crowd"): score -= 2; why.append("crowd: morph risk")
        if sh.get("size") in ("insert", "macro", "extreme_close") and "hand" in text: score -= 1; why.append("hands: warp risk")
        if any(w in text.lower() for w in ("bill", "paper", "phone", "screen", "ledger", "card", "document", "board")): score -= 3; why.append("paper or screen: text risk")
        t = T[i - 1]["start"] if T and len(T) == len(L) else i * 6.0
        rows.append({"line": i, "shot": sh["id"], "score": score, "why": why, "t": t, "picture": (idx.get(sh["id"]) or {}).get("n")})
    rows.sort(key=lambda r: -r["score"])
    per = seconds * COST_PER_S; n_max = int(budget // per); chosen = []
    for r in rows:
        if len(chosen) >= n_max or r["score"] < 3: break
        if any(abs(r["t"] - c["t"]) < 45 for c in chosen): continue                 # spread the motion through the video
        p, s = brief(by_line[r["line"]], plan, seconds); chosen.append({**r, "seconds": s, "prompt": p})
    chosen.sort(key=lambda r: r["line"])
    cost = sum(c["seconds"] for c in chosen) * COST_PER_S
    out = {"budget": budget, "cost_estimate": round(cost, 2), "cost_per_second": COST_PER_S, "clips": chosen, "made": time.strftime("%Y-%m-%d %H:%M")}
    (proj / "clips-plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(chosen)} clips planned (lines {', '.join(str(c['line']) for c in chosen)}), about ${cost:.2f} if made. Nothing was generated.")
    for c in chosen: print(f"  line {c['line']:3d} {c['shot']} score {c['score']}: {', '.join(c['why'])}")


def make(proj, approve_cost, only):
    cp = vv.load_json(proj / "clips-plan.json")
    if not cp: sys.exit("run select first")
    review = vv.load_json(proj / "review.json", {})
    todo = [c for c in cp["clips"] if (not only or c["line"] in only) and not (proj / "clips" / f"{c['shot']}.mp4").exists()]       # keyed by shot: line numbers change between script versions
    cost = sum(c["seconds"] for c in todo) * COST_PER_S
    print(f"{len(todo)} clip(s) to make, about ${cost:.2f} on xAI.")
    if not approve_cost: print("This is a paid step: re-run with --approve-cost once the owner has OK'd the cost. Nothing was generated."); return
    import xai_media
    (proj / "clips").mkdir(exist_ok=True)
    for c in todo:
        n = c.get("picture")
        if n is None or (review.get(str(n)) or {}).get("status") != "approved": print(f"  line {c['line']}: picture {n} is not approved in Gate 1, skipped"); continue
        hd = proj / "images-hd" / f"{n:03d}.png"; pic = hd if hd.exists() else vv.image_for(proj, n)
        try: xai_media.video(str(pic), str(proj / "clips" / f"{c['shot']}.mp4"), c["prompt"], c["seconds"])
        except SystemExit as ex: print(f"  line {c['line']} FAILED: {ex}"); continue
        print(f"  line {c['line']} made: check it before use (python tools/vyapaar_clips.py <project> check --only {c['line']})")


# ---------------------------------------------------------------- inspection
def decode(path, w=320):
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    info = json.loads(pr.stdout); st = info["streams"][0]; num, den = map(int, st["r_frame_rate"].split("/"))
    h = int(w * st["height"] / st["width"]) // 2 * 2
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    fr = np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, 3)
    return fr, num / den, st["width"], st["height"], float(info["format"]["duration"])


def sharp(fr):
    import cv2
    return float(cv2.Laplacian(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var())


def face_vec(img):
    import vyapaar_review as vr
    boxes, vecs = vr.faces_and_ids(img)
    if not boxes: return None
    k = max(range(len(boxes)), key=lambda i: boxes[i][2] * boxes[i][3]); return vecs[k]


def check(proj, only):
    import vyapaar_review as vr
    rd = proj / "clips" / "review"; rd.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in list((proj / "clips").glob("[0-9][0-9][0-9].mp4")) + list((proj / "clips").glob("S[0-9][0-9][0-9].mp4"))
                   if not only or int(f.stem.lstrip("S")) in only)
    res = vv.load_json(proj / "clips-review.json", {}) or {}
    font = ImageFont.truetype(FONT, 16)
    for f in files:
        fr, fps, W, H, dur = decode(f)
        g = fr.mean(axis=3)
        diffs = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2)) if len(g) > 1 else np.zeros(1)
        means = g.mean(axis=(1, 2))
        flicker = float(np.std(np.diff(means))) if len(means) > 2 else 0
        med = float(np.median(diffs)) or 0.01; jump = float(diffs.max() / med) if len(diffs) else 0
        s0, s1 = sharp(fr[0]), sharp(fr[-1])
        big = decode(f, 1280)[0]; b0, f0 = vr.faces_and_ids(Image.fromarray(big[0])); b1, f1 = vr.faces_and_ids(Image.fromarray(big[-1]))
        main = max(range(len(b0)), key=lambda k: b0[k][2] * b0[k][3]) if b0 else None
        ident = max((vr.cosine(f0[main], v) for v in f1), default=None) if main is not None and len(f1) else None
        v0, v1 = (f0[main] if main is not None else None), (f1[0] if len(f1) else None)
        flags = []
        if flicker > 1.2: flags.append(f"flicker: brightness wobbles (std {flicker:.2f})")
        if jump > 8 and diffs.max() > 10: flags.append(f"a sudden jump ({jump:.0f}x the clip's typical change)")
        if s1 < 0.6 * s0: flags.append(f"softens over the clip (sharpness {s0:.0f} -> {s1:.0f}): warping or blur")
        if ident is not None and ident < 0.5 and len(b1) >= len(b0): flags.append(f"identity drift: the main face is still there but matches the start at only {ident:.2f}")
        elif ident is not None and ident < 0.5: flags.append(f"note: the main face turns away or leaves the frame (best match {ident:.2f}); check it is intended")
        if v0 is not None and v1 is None: flags.append("note: no face is visible in the last frame")
        if float(diffs.mean()) < 0.25: flags.append("almost no motion: a still would do")
        res[f.stem] = {"fps": round(fps, 3), "size": [W, H], "seconds": round(dur, 2), "flicker": round(flicker, 2), "jump": round(jump, 1),
                       "sharp_first": round(s0), "sharp_last": round(s1), "identity": None if ident is None else round(ident, 2), "motion": round(float(diffs.mean()), 2), "flags": flags}
        strip = Image.new("RGB", (8 * 300, 210), (14, 12, 10)); dr = ImageDraw.Draw(strip)
        for k in range(8):
            j = min(len(fr) - 1, round(k * (len(fr) - 1) / 7))
            strip.paste(Image.fromarray(fr[j]).resize((296, 167)), (k * 300 + 2, 2))
        dr.text((6, 176), f"{f.stem} | {fps:g} fps {W}x{H} {dur:.1f}s | " + ("; ".join(flags) or "no automatic flags: still look at it"), font=font, fill=(240, 200, 140) if flags else (170, 210, 170))
        strip.save(rd / f"{f.stem}.jpg", quality=88)
        print(f"  {f.stem}: {'; '.join(flags) or 'no automatic flags'}")
    (proj / "clips-review.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"strips in {rd}; a person must still look at every clip before approving it")


def visual_hash(line):
    import hashlib
    return hashlib.sha1((line.get("visual", "") + "|" + line.get("hi", "")).encode("utf-8")).hexdigest()[:10]


def decide(proj, lines, status, note, script=None):
    ap = proj / "clips" / "approved.json"; a = vv.load_json(ap, {}) or {}
    plan, L, by_line = plan_shots(proj) if not script else (None, vv.script_lines(proj, script), {})
    for n in lines:
        sh = by_line.get(n); f = proj / "clips" / (f"{sh['id']}.mp4" if sh and (proj / "clips" / f"{sh['id']}.mp4").exists() else f"{n:03d}.mp4")
        if status == "approved":
            if not f.exists(): print(f"  line {n}: no clip"); continue
            a[str(n)] = {"file": str(f), "shot": sh["id"] if sh else None, "vh": visual_hash(L[n - 1]), "note": note, "at": time.strftime("%Y-%m-%d %H:%M")}
        else: a.pop(str(n), None)
        print(f"  line {n}: {status}")
    ap.parent.mkdir(exist_ok=True); ap.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")


def fps_test(proj, line, fps=30):
    """measure, do not assume: repeating frames to reach 30 fps against motion-compensated interpolation"""
    f = proj / "clips" / (f"{line}.mp4" if str(line).startswith("S") else f"{int(line):03d}.mp4")
    src, sfps, *_ = decode(f, 640)
    out = {}
    for mode, vf in (("repeat", f"fps={fps}"), ("mci", f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc")):
        tmp = proj / "render-cache" / f"fps-{line}-{mode}.mp4"; tmp.parent.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(f), "-vf", vf, "-c:v", "libx264", "-crf", "12", str(tmp)], check=True)
        fr, ofps, *_ = decode(tmp, 640)
        d = np.abs(np.diff(fr.mean(axis=3), axis=0)).mean(axis=(1, 2))
        sh = np.array([sharp(x) for x in fr]); base = np.median([sharp(x) for x in src])
        out[mode] = {"frames": len(fr), "repeated_frames": int((d < 0.05).sum()), "cadence_cv": round(float(np.std(d[d >= 0.05]) / (np.mean(d[d >= 0.05]) + 1e-6)), 3),
                     "sharpness_vs_source_median": round(float(np.median(sh) / base), 3), "sharpness_vs_source_min": round(float(sh.min() / base), 3),
                     "soft_frames": int((sh < 0.85 * base).sum())}
    rec = "mci" if out["mci"]["soft_frames"] == 0 and out["mci"]["sharpness_vs_source_min"] >= 0.95 and out["mci"]["cadence_cv"] < out["repeat"]["cadence_cv"] else "repeat"
    out["source_fps"] = sfps; out["recommend"] = rec
    print(json.dumps(out, indent=1))
    print(f"recommendation: {rec} ({'interpolated frames stay as sharp as the source and the motion is more even' if rec == 'mci' else 'interpolation softens or warps some frames; repeating frames keeps every frame a real one'})")
    return out


def main():
    if len(sys.argv) > 2 and sys.argv[2].startswith("--") or (len(sys.argv) == 2):
        sys.exit(subprocess.run([sys.executable, str(Path(__file__).with_name("vyapaar_clips_legacy.py")), *sys.argv[1:]]).returncode)
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("cmd", choices=["select", "prompts", "make", "check", "approve", "reject", "fps-test"])
    ap.add_argument("arg", nargs="?"); ap.add_argument("--budget", type=float, default=2.0); ap.add_argument("--seconds", type=int, default=4)
    ap.add_argument("--only"); ap.add_argument("--approve-cost", action="store_true"); ap.add_argument("--note", default=""); ap.add_argument("--script")
    a = ap.parse_args(); proj = Path(a.project); only = {int(x) for x in a.only.split(",")} if a.only else None
    if a.cmd == "select": select(proj, a.budget, a.seconds)
    elif a.cmd == "prompts":
        for c in (vv.load_json(proj / "clips-plan.json", {}) or {}).get("clips", []): print(f"line {c['line']} ({c['seconds']} s):\n  {c['prompt']}\n")
    elif a.cmd == "make": make(proj, a.approve_cost, only)
    elif a.cmd == "check": check(proj, only)
    elif a.cmd in ("approve", "reject"): decide(proj, [int(x) for x in a.arg.split(",")], "approved" if a.cmd == "approve" else "rejected", a.note, a.script)
    elif a.cmd == "fps-test": fps_test(proj, a.arg)


if __name__ == "__main__":
    main()
