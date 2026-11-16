"""Decoding Vyapaar renderer: ONE renderer for the style sample and the final cut, so the approved sample is exactly what the full video gets.

    python tools/vyapaar_render.py <project> sample [--segments 1-10,122-129,139-141] [--test-clips 5,7]   # Gate 2 sample (sample.mp4)
    python tools/vyapaar_render.py <project> full                                                        # the whole video (video.mp4)
      options: --script script.json --index images-index.json --plan visual-plan.json --lines voice-lines.json --voice voice.mp3
               --workers 4 --skip-gate (tests only) --out NAME.mp4

Every setting comes from channels/hindi/visual-bible.json `render` (resolution, fps, grade, camera limits, pacing, transitions, overlays,
audio mix, clip conform) and `graphics`. Nothing about the look lives in this file, and the sample and the full render share every code path.
  * Pictures: the 2x upscale in images-hd/ when it exists (only approved pictures are upscaled), else images/.
  * Camera: a move chosen from the picture's measured composition (faces and the subject mask, analysis/ from vyapaar_review.py) and the shot's
    planned size and purpose (visual-plan.json), or the plan's own `camera`. Moves: push to the subject, pull back, drift across, pan from one
    face to another, a near-hold for inserts. The same move never runs twice in a row; speed is capped (zoom and pan per second) and moves
    ease in and out. A line longer than pacing.split_over_s gets one motivated cut-in to the subject when the source has the pixels for it.
  * Transitions: a cut, unless the location changes (short dissolve), a chapter starts (dissolve) or a flashback begins or ends (long dissolve).
  * Graphics: vyapaar_graphics.py renders them (cached); still lines with `screen` text get the lower-third label, faded in and out.
  * Clips: only clips approved in clips/approved.json (vyapaar_clips.py), conformed to the output fps by frame repetition; after a clip the
    shot continues from its last frame with a camera move that starts at zoom 1.0, so there is no freeze.
  * One grade (bible render.grade) is applied in the encoder to every frame; flashback shots get the bible's flashback modifier first.
  * Audio: voice with the bible's voice EQ, real music from <project>/audio/music-map.json (mood -> file in audio/music) following the
    script's `music` moods, ducked under the voice, levelled to the bible's loudness.
A full render refuses to start unless Gate 1 is open (every picture approved) and Gate 2 approved a sample made with these exact settings.
Writes <out>-plan.json (every shot: time, source, move, transition) for vyapaar_qa.py.
"""
import argparse, hashlib, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vyapaar_visual as vv

VERSION = "render-1"


# ---------------------------------------------------------------- settings
def settings(proj):
    b = vv.load_bible(proj)
    code = [hashlib.sha1(f.read_bytes()).hexdigest() for f in (Path(__file__), Path(__file__).parent / "video" / "graphics.html")]   # the code is part of the look
    return b, hashlib.sha1(json.dumps([b["render"], b["graphics"], VERSION, code], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def ease_profile(u, dur, ease_s):
    """position 0..1 along a move of `dur` seconds at time fraction u: accelerate for ease_s, glide, decelerate (no stop-start at cuts)"""
    if dur <= 2 * ease_s: return u * u * (3 - 2 * u)
    e = ease_s / dur; v = 1 / (1 - e)                     # peak speed so the area is 1
    if u < e: return 0.5 * v * u * u / e
    if u > 1 - e: return 1 - 0.5 * v * (1 - u) ** 2 / e
    return 0.5 * v * e + v * (u - e)


# ---------------------------------------------------------------- composition and camera
def focus_of(a):
    """the point the camera should favour (fractions): the largest confident face, else the top third of the subject, else just above centre"""
    faces = [f for f in (a or {}).get("faces", []) if f[4] >= 0.8 and f[2] >= 0.03]
    if faces:
        f = max(faces, key=lambda f: f[2] * f[3]); return f[0] + f[2] / 2, f[1] + f[3] * 0.45, faces
    s = (a or {}).get("subject")
    if s and (s[2] - s[0]) * (s[3] - s[1]) < 0.8: return (s[0] + s[2]) / 2, s[1] + (s[3] - s[1]) * 0.3, faces
    return 0.5, 0.45, faces


def clampc(z, cx, cy):
    w = 1 / z
    return z, min(max(cx, w / 2), 1 - w / 2), min(max(cy, w / 2), 1 - w / 2)


def choose_move(meta, a, dur, prev, zmax, cam):
    """(name, start (z, cx, cy), end (z, cx, cy)) for one shot"""
    fx, fy, faces = focus_of(a)
    size, tag = meta.get("size") or "medium", meta.get("tag") or ""
    o = meta.get("camera")
    span_z = min(zmax - 1, max(cam["min_zoom_span"], cam["zoom_per_s"] * dur))
    def push(): return "push", clampc(1.0, 0.5, 0.5), clampc(1 + span_z, 0.5 + (fx - 0.5) * 0.85, 0.5 + (fy - 0.5) * 0.85)
    def pull(): s, e = push()[1:]; return "pull", e, s
    def hold(): z = 1 + min(0.05, span_z); return "hold", clampc(1.02, fx, fy), clampc(z + 0.02, fx, fy)
    def drift(direction):
        z = min(zmax, 1.1); room = (1 - 1 / z); span = min(room * 0.9, cam["pan_per_s"] * dur)
        a0, a1 = (0.5 - span / 2, 0.5 + span / 2) if direction > 0 else (0.5 + span / 2, 0.5 - span / 2)
        return ("drift_r" if direction > 0 else "drift_l"), clampc(z, a0, 0.5 + (fy - 0.5) * 0.3), clampc(z, a1, 0.5 + (fy - 0.5) * 0.5)
    def pan_faces():
        big = sorted([f for f in faces if f[2] >= 0.04], key=lambda f: f[0])
        if len(big) < 2 or (big[-1][0] - big[0][0]) < 0.28: return None
        A, B = big[0], big[-1]; z = min(zmax, 1.2)
        if prev and prev.startswith("pan"): A, B = B, A
        return "pan", clampc(z, A[0] + A[2] / 2, A[1] + A[3] / 2), clampc(z, B[0] + B[2] / 2, B[1] + B[3] / 2)
    if o:
        if o.get("from") and o.get("to"): return o.get("move", "planned"), clampc(*o["from"]), clampc(*o["to"])
        m = o.get("move")
        if m == "push": return push()
        if m == "pull": return pull()
        if m in ("drift_r", "drift_l"): return drift(1 if m == "drift_r" else -1)
        if m == "hold": return hold()
    if size in ("insert", "macro", "extreme_close"): mv = hold()
    elif tag in ("reveal", "reversal", "payoff") or "hook" in (meta.get("purpose") or ""): mv = push()
    elif size in ("establishing", "wide"): mv = (dur >= 4 and pan_faces()) or drift(1 if fx >= 0.5 else -1)
    elif size in ("two_shot", "ots") and dur >= 4: mv = pan_faces() or push()
    else: mv = push()
    if prev and mv[0] == prev:                                        # never the same move twice in a row
        if mv[0] == "push": mv = pull() if size in ("medium", "wide", "establishing", "two_shot", "ots", "pov") else hold()
        elif mv[0] == "pull": mv = push()
        elif mv[0].startswith("drift"): mv = drift(-1 if mv[0] == "drift_r" else 1)
        elif mv[0] == "hold" and size not in ("insert", "macro", "extreme_close"): mv = push()
    return mv


def cutin_move(a, zmax, dur, cam):
    """the second shot of a long line: a tighter framing on the subject (a real cut-in, not another push), only if the pixels allow it"""
    fx, fy, faces = focus_of(a)
    s = (a or {}).get("subject"); f = max(faces, key=lambda x: x[2] * x[3]) if faces else None
    if f: need = max(f[2] * 3.2, f[3] * 2.4)
    elif s: need = max((s[2] - s[0]) * 1.3, (s[3] - s[1]) * 1.2)
    else: return None
    z = min(zmax, max(1.25, 1 / max(need, 1e-3)))
    if z < 1.25: return None
    return "cutin", clampc(z, fx, fy), clampc(min(zmax, z + min(0.04, cam["zoom_per_s"] * dur)), fx, fy)


# ---------------------------------------------------------------- the timeline
def load_meta(proj, L, plan, idx):
    """per line: size, tag, purpose, camera, location, look, flashback, chapter (from the plan, or inferred for an older project)"""
    import vyapaar_review as vr
    by_line = {}
    for sh in (plan or {}).get("shots", []):
        for n in vv.lines_of(sh): by_line[n] = sh
    shots_by_id = {s["id"]: s for s in (plan or {}).get("shots", [])}
    cat = {}
    for e in idx:
        if e["type"] == "scene":
            for n in e["lines"]: cat[n] = e
    out, chapter = {}, None
    for i, l in enumerate(L, 1):
        chapter = l.get("chapter") or chapter
        sh = by_line.get(i) or {}
        if sh.get("same_as"): base = shots_by_id.get(sh["same_as"], {}); sh = {**base, **{k: v for k, v in sh.items() if k != "same_as"}}
        e = cat.get(i, {})
        size = sh.get("size") or {"closeups": "close", "establishing": "establishing", "characters": "medium"}.get(e.get("category") or "", "medium")
        if not sh and re.match(r"(close-up|extreme close-up)", l.get("visual", ""), re.I): size = "close"
        out[i] = {"size": size, "tag": l.get("tag"), "purpose": sh.get("purpose", ""), "camera": sh.get("camera"), "location": sh.get("location") or ("graphic" if l.get("kind") == "card" else None),
                  "look": sh.get("look"), "flashback": bool(sh.get("flashback")) or bool(re.match(r"flashback", l.get("visual", ""), re.I)),
                  "chapter": chapter, "chapter_start": bool(l.get("chapter")), "shot": sh.get("id")}
    return out


def pauses_from(voice):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(voice), "-af", "silencedetect=n=-34dB:d=0.14", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return [(x + y) / 2 for x, y in zip(st, en)]


def build(proj, args, bible, segments):
    L = vv.script_lines(proj, args.script); T = vv.load_json(proj / args.lines)
    if not T or len(T) != len(L): sys.exit(f"{args.lines} ({len(T or [])} lines) does not match the script ({len(L)} lines)")
    import vyapaar_review as vr
    idx = vr.load_index(proj, args.index)                      # infers sizes and looks for an older index
    plan = vv.load_json(proj / args.plan) if args.plan and (proj / args.plan).exists() else None
    meta = load_meta(proj, L, plan, idx)
    R = bible["render"]; cam = R["camera"]; fps = R["fps"]
    import vyapaar_graphics as vg
    wanted = {i for a, b in segments for i in range(a, b + 1)}
    gman = vg.render(proj, args.script, args.lines, args.plan if plan else None, lines_only=wanted)
    approved = vv.load_json(proj / "clips" / "approved.json", {}) or {}
    test_clips = set(int(x) for x in args.test_clips.split(",")) if args.test_clips else set()
    pauses = pauses_from(proj / args.voice) if (proj / args.voice).exists() else []
    slot = {}
    for e in idx:
        if e["type"] == "scene":
            for n in e["lines"]: slot.setdefault(n, e["n"])
    shots, segs, out_t, prev_move = [], [], 0.0, None
    for si, (a, b) in enumerate(segments):
        seg_start = T[a - 1]["start"]; seg_end = T[b]["start"] if b < len(T) else T[b - 1]["end"] + 1.0
        segs.append({"lines": [a, b], "src": [seg_start, seg_end], "out": out_t})
        for i in range(a, b + 1):
            l, m = L[i - 1], meta[i]
            t0 = T[i - 1]["start"]; t1 = T[i]["start"] if (i < len(T) and i < b) else (seg_end if i == b else T[i]["start"])
            o0 = out_t + (t0 - seg_start); dur = t1 - t0
            base = {"line": i, "chapter": m["chapter"], "chapter_start": m["chapter_start"], "location": m["location"], "flashback": m["flashback"], "shot": m["shot"], "look": m["look"]}
            if l.get("kind") == "card" or (gman["cards"].get(i) and m["location"] == "graphic"):
                g = gman["cards"].get(i)
                shots.append({**base, "kind": "graphic", "src": g["file"], "start": o0, "end": o0 + dur, "location": "graphic", "flashback": False}); prev_move = None; continue
            n = slot.get(i); pic = None
            if n is not None:
                hd = proj / cam["hd_dir"] / f"{n:03d}.png"; pic = hd if hd.exists() else vv.image_for(proj, n)
            if not pic:
                print(f"  line {i}: no picture, so its screen text is shown as a title card"); g = gman["cards"].get(i)
                if g: shots.append({**base, "kind": "graphic", "src": g["file"], "start": o0, "end": o0 + dur, "location": "graphic"}); continue
                sys.exit(f"line {i} has neither a picture nor a graphic")
            an = vv.load_json(proj / "analysis" / f"{n:03d}.json")
            if not an: print(f"  line {i}: picture {n:03d} has no analysis (run vyapaar_review.py analyze); the camera aims at the centre")
            zmax = cam["max_zoom_hd"] if Image.open(pic).width >= 1.5 * R["width"] else cam["max_zoom_sd"]
            label = gman["labels"].get(i)
            clip = approved.get(str(i))
            if clip and clip.get("vh") and clip["vh"] != clip_hash(l):      # approved for a different version of this line: not used
                print(f"  line {i}: the approved clip belongs to another version of this line, so it is not used"); clip = None
            if not clip and i in test_clips and (proj / "clips" / f"{i:03d}.mp4").exists(): clip = {"file": str(proj / "clips" / f"{i:03d}.mp4")}
            pieces = []
            if clip:
                cd = clip_duration(clip["file"])
                cl_end = min(dur, cd)
                pieces.append({"kind": "clip", "src": clip["file"], "start": o0, "end": o0 + cl_end, "unreviewed": i in test_clips and str(i) not in approved})
                if dur - cl_end > 0.6:
                    last = last_frame(proj, clip["file"], R)
                    mv = choose_move({**m, "camera": {"move": "push"}}, None, dur - cl_end, "clip", 1.15, cam)
                    pieces.append({"kind": "still", "src": str(last), "start": o0 + cl_end, "end": o0 + dur, "move": mv, "from_clip": True})
            else:
                split = None
                if dur > R["pacing"]["split_over_s"]:
                    mid = t0 + dur / 2
                    near = [p for p in pauses if t0 + R["pacing"]["min_shot_s"] < p < t1 - R["pacing"]["min_shot_s"]]
                    split = min(near, key=lambda p: abs(p - mid)) if near else mid
                    ci = cutin_move(an, zmax, t1 - split, cam)
                    if not ci: split = None
                if split:
                    mv1 = choose_move({**m, "size": "wide" if m["size"] in ("medium", "two_shot", "ots") else m["size"], "tag": None}, an, split - t0, prev_move, zmax, cam)
                    pieces.append({"kind": "still", "src": str(pic), "start": o0, "end": o0 + (split - t0), "move": mv1, "pic": n})
                    pieces.append({"kind": "still", "src": str(pic), "start": o0 + (split - t0), "end": o0 + dur, "move": ci, "pic": n, "cut_in": True})
                else:
                    mv = choose_move(m, an, dur, prev_move, zmax, cam)
                    pieces.append({"kind": "still", "src": str(pic), "start": o0, "end": o0 + dur, "move": mv, "pic": n})
            for k, p in enumerate(pieces):
                shots.append({**base, **p, "label": label["file"] if (label and k == 0) else None, "label_until": o0 + dur})
                prev_move = p.get("move", ["clip"])[0]
        out_t += (seg_end - seg_start) + (0.6 if si < len(segments) - 1 else 0)
    # transitions into each shot
    tr = R["transitions"]
    for k, s in enumerate(shots):
        if k == 0: s["trans"] = ["fade_in", tr["start_fade"]]; continue
        p = shots[k - 1]
        if abs(p["end"] - s["start"]) > 0.05: s["trans"] = ["gap", 0]; continue        # a sample boundary
        if s["flashback"] != p["flashback"]: s["trans"] = tr["flashback"]
        elif s["chapter_start"] and s["line"] != p["line"]: s["trans"] = tr["chapter"]
        elif s.get("from_clip") or s.get("cut_in") or (s["line"] == p["line"]): s["trans"] = ["cut", 0]
        elif s["location"] and p["location"] and s["location"] != p["location"]: s["trans"] = tr["location_change"]
        elif (s["location"] is None or p["location"] is None) and (s["kind"] == "graphic") != (p["kind"] == "graphic"): s["trans"] = tr["location_change"]
        else: s["trans"] = tr["same_location"]
    # a graphic sits on a blurred, darkened copy of the scene it interrupts (bible graphics.backdrop): the nearest still in its segment
    for k, s in enumerate(shots):
        if s["kind"] != "graphic": continue
        seg = lambda x: next(i for i, g in enumerate(segs) if g["out"] - 0.01 <= x["start"] < g["out"] + (g["src"][1] - g["src"][0]) + 0.01)
        near = [x for x in shots[:k][::-1] + shots[k + 1:] if x["kind"] == "still" and seg(x) == seg(s)]
        s["backdrop"] = near[0]["src"] if near else None
    return shots, segs, out_t, L, T


def clip_hash(line):
    return hashlib.sha1((line.get("visual", "") + "|" + line.get("hi", "")).encode("utf-8")).hexdigest()[:10]


def clip_duration(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def last_frame(proj, clip, R):
    out = proj / "render-cache" / f"{Path(clip).stem}-last.png"; out.parent.mkdir(exist_ok=True)
    if not out.exists():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-sseof", "-0.1", "-i", str(clip), "-frames:v", "1", "-vf", f"scale={R['width']}:{R['height']}:flags=lanczos", str(out)], check=True)
    return out


# ---------------------------------------------------------------- frames
class Stream:
    """frames of a video file at the output size and fps, read forward once; before the start it gives the first frame, after the end the last"""
    def __init__(self, path, W, H, fps, conform="repeat", alpha=False):
        vf = f"fps={fps}," if conform == "repeat" else (f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc," if conform == "mci" else "")
        self.mode, self.bpp = ("RGBA", 4) if alpha else ("RGB", 3)
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"{vf}scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgba" if alpha else "rgb24", "-"], stdout=subprocess.PIPE)
        self.W, self.H, self.k, self.last, self.first = W, H, -1, None, None
    def get(self, k):
        if k < 0: k = 0
        n = self.W * self.H * self.bpp
        while self.k < k:
            b = self.p.stdout.read(n)
            if len(b) < n: break
            self.last = b; self.k += 1
            if self.first is None: self.first = b
        return Image.frombytes(self.mode, (self.W, self.H), self.last if self.last else bytes(n))
    def close(self): self.p.kill()


def crop(src, z, cx, cy, W, H):
    sw, sh = src.size
    if sw / sh > W / H: h = sh / z; w = h * W / H                  # crop at the output's shape: a 3:2 or 4:3 picture is cropped, never squashed
    else: w = sw / z; h = w * H / W
    x0 = min(max(cx * sw - w / 2, 0), sw - w); y0 = min(max(cy * sh - h / 2, 0), sh - h)
    im = src.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=25, threshold=2)) if w < W * 0.95 else im


def flashback(im, fb):
    a = np.asarray(im).astype(np.float32) / 255
    g = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    a = g + (a - g) * fb["saturation"]; a = a * np.array(fb["warm"], np.float32); a = fb["lift"] + a * (1 - fb["lift"])
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return out.filter(ImageFilter.GaussianBlur(fb["soften"])) if fb.get("soften") else out


class Renderer:
    def __init__(self, shots, bible):
        self.shots, self.R = shots, bible["render"]; self.W, self.H, self.fps = self.R["width"], self.R["height"], self.R["fps"]
        self.imgs, self.streams, self.labels, self.backs = {}, {}, {}, {}
        self.bd = bible["graphics"].get("backdrop") or {}
    def backdrop(self, p):
        """the scene behind a graphic: blurred and darkened toward the bible's tint"""
        if p not in self.backs:
            im = Image.open(p).convert("RGB").resize((int(self.W * 1.06), int(self.H * 1.06)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(self.bd.get("blur", 26)))
            tint = tuple(int(self.bd.get("tint", "#17130F")[i:i + 2], 16) for i in (1, 3, 5))
            self.backs[p] = Image.blend(im, Image.new("RGB", im.size, tint), self.bd.get("darken", 0.74))
        return self.backs[p]
    def image(self, p):
        if p not in self.imgs:
            if len(self.imgs) > 3: self.imgs.pop(next(iter(self.imgs)))
            self.imgs[p] = Image.open(p).convert("RGB")
        return self.imgs[p]
    def label(self, p, level):
        key = (p, level)
        if key not in self.labels:
            im = Image.open(p).convert("RGBA")
            if level < 16: im.putalpha(im.getchannel("A").point(lambda v: v * level // 16))
            self.labels[key] = im
        return self.labels[key]
    def shot_frame(self, k, t):
        s = self.shots[k]; d = s["end"] - s["start"]; u = (t - s["start"]) / d
        if s["kind"] == "still":
            mv = s["move"]; pos = ease_profile(min(max(u, 0), 1), d, self.R["camera"]["ease_s"])
            z0, x0, y0 = mv[1]; z1, x1, y1 = mv[2]
            im = crop(self.image(s["src"]), z0 + (z1 - z0) * pos, x0 + (x1 - x0) * pos, y0 + (y1 - y0) * pos, self.W, self.H)
        else:
            alpha = s["kind"] == "graphic" and str(s["src"]).endswith(".mov")
            if k not in self.streams:
                self.streams[k] = Stream(s["src"], self.W, self.H, self.fps, self.R["clips"]["conform"] if s["kind"] == "clip" else "none", alpha)
            im = self.streams[k].get(int(round((t - s["start"]) * self.fps)))
            if alpha:                                                # composite over the scene's backdrop, which drifts slowly too
                tint = tuple(int(self.bd.get("tint", "#17130F")[i:i + 2], 16) for i in (1, 3, 5))
                back = crop(self.backdrop(s["backdrop"]), 1.0 + 0.03 * min(max(u, 0), 1), 0.5, 0.5, self.W, self.H) if s.get("backdrop") else Image.new("RGB", (self.W, self.H), tint)
                back = back.convert("RGBA"); back.alpha_composite(im); im = back.convert("RGB")
        if s.get("flashback"): im = flashback(im, self.R["flashback"])
        if s.get("label"):
            ov = self.R["overlay"]; a_in = (t - s["start"] - 0.3) / ov["in_s"]; a_out = (s["label_until"] - 0.25 - t) / ov["in_s"]
            al = max(0.0, min(1.0, a_in, a_out))
            if al > 0.01:
                im = im.convert("RGBA"); im.alpha_composite(self.label(s["label"], max(1, round(al * 16)))); im = im.convert("RGB")
        return im
    def frame(self, t):
        sh = self.shots; k = max([j for j in range(len(sh)) if sh[j]["start"] <= t + 1e-6] or [0])
        if t >= sh[k]["end"] and (k + 1 >= len(sh) or sh[k + 1]["start"] > t):   # a gap between sample segments: black
            return Image.new("RGB", (self.W, self.H))
        im = self.shot_frame(k, t)
        nxt = sh[k + 1] if k + 1 < len(sh) else None
        if nxt and nxt["trans"][0] == "dissolve" and t > nxt["start"] - nxt["trans"][1] / 2:
            im = Image.blend(im, self.shot_frame(k + 1, t), smooth((t - (nxt["start"] - nxt["trans"][1] / 2)) / nxt["trans"][1]))
        elif sh[k]["trans"][0] == "dissolve" and k > 0 and t < sh[k]["start"] + sh[k]["trans"][1] / 2:
            im = Image.blend(self.shot_frame(k - 1, t), im, smooth((t - (sh[k]["start"] - sh[k]["trans"][1] / 2)) / sh[k]["trans"][1]))
        if sh[k]["trans"][0] in ("fade_in", "gap") and t < sh[k]["start"] + 0.5:
            im = Image.blend(Image.new("RGB", im.size), im, smooth((t - sh[k]["start"]) / 0.5))
        end_fade = self.R["transitions"]["end_fade"]
        if (nxt is None or nxt["trans"][0] == "gap") and t > sh[k]["end"] - (end_fade if nxt is None else 0.4):
            im = Image.blend(im, Image.new("RGB", im.size), smooth((t - (sh[k]["end"] - (end_fade if nxt is None else 0.4))) / (end_fade if nxt is None else 0.4)))
        return im
    def close(self):
        for s in self.streams.values(): s.close()


def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)


def render_chunk(job):
    shots, bible, f0, f1, out = job
    R = bible["render"]; r = Renderer(shots, bible)
    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R['width']}x{R['height']}", "-r", str(R["fps"]), "-i", "-",
                            "-vf", R["grade"], "-c:v", "libx264", "-preset", R["preset"], "-crf", str(R["crf"]), "-pix_fmt", "yuv420p", "-g", str(R["fps"] * 2), "-threads", "2", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        enc.stdin.write(r.frame(f / R["fps"]).tobytes())
    enc.stdin.close(); enc.wait(); r.close()
    return out


# ---------------------------------------------------------------- audio
def music_sections(L, T, lines_sel):
    out, cur = [], None
    for i in lines_sel:
        m = L[i - 1].get("music")
        if m and m != cur: out.append((i, m)); cur = m
    return out


def audio(proj, args, bible, segs, L, T, total, out_wav):
    A = bible["render"]["audio"]; mm = vv.load_json(proj / "audio" / "music-map.json", {}) or {}
    ins, fc, parts, mus, used = [], [], [], [], []
    voice = proj / args.voice
    for k, s in enumerate(segs):
        a, b = s["src"]; ins += ["-i", str(voice)]
        fc.append(f"[{len(ins) // 2 - 1}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,{A['voice_eq']},afade=t=in:d=0.05,afade=t=out:st={max(0, b - a - 0.3)}:d=0.3,adelay={int(s['out'] * 1000)}:all=1[v{k}]")
        parts.append(f"[v{k}]")
    # music: the script's moods, a real track per mood, crossfaded at each change, clipped to each segment
    cur_mood, mood_at = None, {}
    for i, l in enumerate(L, 1):
        cur_mood = l.get("music") or cur_mood; mood_at[i] = cur_mood
    for k, s in enumerate(segs):
        a, b = s["lines"]; i = a
        while i <= b:
            mood = mood_at.get(i); j = i
            while j + 1 <= b and mood_at.get(j + 1) == mood: j += 1
            f = mm.get(mood) if mood else None
            if f and (proj / "audio" / "music" / f).exists():
                st = T[i - 1]["start"]; en = T[j]["start"] if j < len(T) and j < b else s["src"][1]
                o = s["out"] + (st - s["src"][0]); d = en - st
                ins += ["-stream_loop", "-1", "-i", str(proj / "audio" / "music" / f)]
                fc.append(f"[{len(mus) + len(segs)}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:{d + 1.5},asetpts=PTS-STARTPTS,volume={A['music_gain']},"
                          f"afade=t=in:d=1.5,afade=t=out:st={max(0, d - 0.5)}:d=2.0,adelay={int(o * 1000)}:all=1[m{len(mus)}]")
                mus.append(f"[m{len(mus)}]"); used.append(f)
            i = j + 1
    fc.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0,aformat=sample_rates=44100:channel_layouts=stereo,asplit[v][sc]")
    if mus:
        fc.append("".join(mus) + f"amix=inputs={len(mus)}:normalize=0[m]")
        fc.append(f"[m][sc]{A['duck']}[md]"); fc.append(f"[v][md]amix=inputs=2:normalize=0,loudnorm=I={A['loudness']}:TP={A['true_peak']}:LRA=9,apad,atrim=0:{total}[a]")
    else:
        fc.append(f"[sc]anullsink"); fc.append(f"[v]loudnorm=I={A['loudness']}:TP={A['true_peak']}:LRA=9,apad,atrim=0:{total}[a]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[a]", "-ar", "48000", str(out_wav)], check=True)
    return sorted(set(used))


# ---------------------------------------------------------------- main
def parse_segments(s, n):
    out = []
    for part in s.split(","):
        a, b = (part.split("-") + [part])[:2]; out.append((max(1, int(a)), min(n, int(b))))
    return out


def chunks(shots, nf, fps, workers):
    """frame ranges that start and end on a hard cut, so no dissolve crosses a chunk"""
    cuts = sorted({round(s["start"] * fps) for s in shots if s["trans"][0] in ("cut", "gap")} | {0})
    want = [round(nf * k / workers) for k in range(1, workers)]
    picks = sorted({min(cuts, key=lambda c: abs(c - w)) for w in want} - {0})
    edges = [0] + [p for p in picks if 0 < p < nf] + [nf]
    return [(edges[k], edges[k + 1]) for k in range(len(edges) - 1) if edges[k + 1] > edges[k]]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("mode", choices=["sample", "full"])
    ap.add_argument("--segments"); ap.add_argument("--script"); ap.add_argument("--index", default="images-index.json"); ap.add_argument("--plan", default="visual-plan.json")
    ap.add_argument("--lines", default="voice-lines.json"); ap.add_argument("--voice", default="voice.mp3"); ap.add_argument("--workers", type=int, default=max(1, min(5, (os.cpu_count() or 4) - 1)))
    ap.add_argument("--skip-gate", action="store_true"); ap.add_argument("--test-clips", help="unapproved clips allowed in a SAMPLE only, marked as unreviewed in the plan")
    ap.add_argument("--out")
    a = ap.parse_args(); proj = Path(a.project); bible, h = settings(proj); R = bible["render"]
    L = vv.script_lines(proj, a.script)
    if a.mode == "full":
        if a.test_clips: sys.exit("--test-clips is for samples only: approve the clips with vyapaar_clips.py")
        if not a.skip_gate:
            import vyapaar_review as vr
            if not vr.gate(proj, a.index): sys.exit("Gate 1 is closed: approve the pictures first (vyapaar_review.py)")
            g2 = vv.load_json(proj / "gate2.json", {})
            if not g2.get("approved"): sys.exit("Gate 2 is closed: render a sample, check it (vyapaar_qa.py), and approve it (vyapaar_qa.py <project> approve sample.mp4)")
            if g2.get("settings") != h: sys.exit(f"Gate 2 approved a sample made with other settings ({g2.get('settings')} vs {h}): render and approve a new sample")
        segments = [(1, len(L))]
    else:
        segments = parse_segments(a.segments, len(L)) if a.segments else [(1, min(len(L), 12))]
    shots, segs, total, L, T = build(proj, a, bible, segments)
    nf = int(round(total * R["fps"]))
    out = proj / (a.out or ("video.mp4" if a.mode == "full" else "sample.mp4"))
    cd = proj / "render-cache" / "chunks"; cd.mkdir(parents=True, exist_ok=True)
    for old in cd.glob("*.mp4"): old.unlink()
    parts = chunks(shots, nf, R["fps"], a.workers)
    print(f"{a.mode}: {len(shots)} shots, {total:.1f} s, {nf} frames at {R['fps']} fps in {len(parts)} chunk(s); settings {h}", flush=True)
    jobs = [(shots, bible, f0, f1, str(cd / f"{k:02d}.mp4")) for k, (f0, f1) in enumerate(parts)]
    with Pool(len(jobs)) as p: outs = p.map(render_chunk, jobs)
    lst = cd / "list.txt"; lst.write_text("".join(f"file '{Path(o).resolve().as_posix()}'\n" for o in outs), encoding="utf-8")
    wav = proj / "render-cache" / "audio.wav"
    tracks = audio(proj, a, bible, segs, L, T, total, wav)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    plan_out = {"mode": a.mode, "settings": h, "version": VERSION, "fps": R["fps"], "total": total, "segments": segs, "music": tracks,
                "shots": [{k: v for k, v in s.items()} for s in shots], "script": a.script or "script.json", "index": a.index}
    (out.with_name(out.stem + "-plan.json")).write_text(json.dumps(plan_out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} and {out.stem}-plan.json. Next: python tools/vyapaar_qa.py {proj} {out.name}")


if __name__ == "__main__":
    main()
