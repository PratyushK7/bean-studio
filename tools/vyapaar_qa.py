"""Decoding Vyapaar Gate 2: technical and visual QA of a rendered sample or cut. A clean ffmpeg exit is not a good video, so this looks.

    python tools/vyapaar_qa.py <project> <video.mp4>              # qa/<video>-report.md, qa/<video>-shots.jpg, qa/<video>-strips.jpg
    python tools/vyapaar_qa.py <project> approve <sample.mp4> [--note "..."]   # Gate 2: records the approval and the exact render settings

Checks (each against the render plan <video>-plan.json that vyapaar_render.py writes):
  * frozen stretches (no visible change for over 1.5 s), black frames outside the planned fades, duplicated frames, unplanned cuts (jumps)
  * frame rate, resolution, audio and video lengths, loudness and true peak against the bible
  * camera: zoom and pan speed of every planned move against the bible's limits, the same move twice in a row, pushes per minute,
    a picture reused with no new framing
  * grade: each shot's brightness and saturation, measured on the video, against its planned look and its neighbours
  * text: graphics whose text overflowed its box or the safe area (graphics/report.json)
Contact sheets: one frame from the middle of every shot, and strips of the opening, the middle and the ending (one frame a second) to look at.
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vyapaar_visual as vv

FONT = "C:/Windows/Fonts/segoeui.ttf"


def probe(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration:format=duration", "-of", "json", str(v)], capture_output=True, text=True)
    return json.loads(r.stdout)


def frames_gray(v, fps, w=320):
    """decode the whole video at its own fps, small and grey, blurred a little so the film grain does not count as motion"""
    h = int(w * 9 / 16)
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(v), "-vf", f"scale={w}:{h},gblur=sigma=1.2,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    prev, diffs, means, k = None, [], [], 0
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h: break
        a = np.frombuffer(b, np.uint8).astype(np.float32)
        means.append(float(a.mean()))
        diffs.append(float(np.abs(a - prev).mean()) if prev is not None else 99.0); prev = a; k += 1
    return np.array(diffs), np.array(means)


def runs(mask, fps, min_s):
    out, start = [], None
    for i, m in enumerate(list(mask) + [False]):
        if m and start is None: start = i
        if not m and start is not None:
            if (i - start) / fps >= min_s: out.append((start / fps, i / fps))
            start = None
    return out


def loudness(v):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(v), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    return (float(i[-1]) if i else None), (float(tp[-1]) if tp else None)


def frame_at(v, t, w=1920):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe", "-c:v", "png", "-"], capture_output=True)
    from io import BytesIO
    return Image.open(BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def stats(im):
    a = np.asarray(im.resize((320, 180))).astype(np.float32) / 255
    luma = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean()
    mx, mn = a.max(2), a.min(2)
    return float(luma), float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())


def check(proj, video):
    proj = Path(proj); v = proj / video; plan = vv.load_json(v.with_name(v.stem + "-plan.json"))
    if not plan: sys.exit(f"no {v.stem}-plan.json: QA reads the render plan written by vyapaar_render.py")
    bible = vv.load_bible(proj); R = bible["render"]; fps = R["fps"]; shots = plan["shots"]
    qd = proj / "qa"; qd.mkdir(exist_ok=True)
    issues = {"fail": [], "warn": [], "info": []}
    # --- container
    pr = probe(v); vs = next(s for s in pr["streams"] if s["codec_type"] == "video"); au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
    num, den = map(int, vs["r_frame_rate"].split("/")); real_fps = num / den
    if (vs["width"], vs["height"]) != (R["width"], R["height"]): issues["fail"].append(f"resolution {vs['width']}x{vs['height']}, the bible says {R['width']}x{R['height']}")
    if abs(real_fps - fps) > 0.01: issues["fail"].append(f"frame rate {real_fps:.3f}, the bible says {fps}")
    vdur = float(vs.get("duration") or pr["format"]["duration"]); adur = float(au[0].get("duration") or 0) if au else 0
    if not au: issues["fail"].append("no audio track")
    elif abs(vdur - adur) > 0.15: issues["warn"].append(f"audio {adur:.2f} s and video {vdur:.2f} s differ by {abs(vdur - adur):.2f} s")
    if abs(vdur - plan["total"]) > 0.3: issues["warn"].append(f"video is {vdur:.2f} s, the plan says {plan['total']:.2f} s")
    # --- motion: freezes, duplicates, black, jumps
    d, means = frames_gray(v, fps)
    planned_static = []                                          # fades, sample gaps: allowed to be dark or still
    for k, s in enumerate(shots):
        if s["trans"][0] in ("fade_in", "gap"): planned_static.append((s["start"] - 0.7, s["start"] + 0.6))
    planned_static.append((plan["total"] - R["transitions"]["end_fade"] - 0.2, plan["total"] + 1))
    for s in plan.get("segments", [])[1:]: planned_static.append((s["out"] - 1.2, s["out"] + 0.6))
    allowed = lambda a, b: any(a >= x - 0.05 and b <= y + 0.05 for x, y in planned_static)
    still = d < 0.06
    for a, b in runs(still, fps, 1.5):
        if not allowed(a, b): issues["fail"].append(f"frozen for {b - a:.1f} s at {a:.1f} s")
    dup_runs = runs(d < 0.02, fps, 0.25)
    dups = [(a, b) for a, b in dup_runs if not allowed(a, b)]
    if dups: issues["warn"].append(f"{len(dups)} run(s) of repeated frames (at {', '.join(f'{a:.1f}s' for a, b in dups[:6])})")
    black = means < 8
    for a, b in runs(black, fps, 0.2):
        if not allowed(a, b): issues["fail"].append(f"black for {b - a:.2f} s at {a:.1f} s")
    planned_cuts = [s["start"] for s in shots if s["trans"][0] in ("cut",)] + [s["start"] for s in shots if s["trans"][0] == "dissolve"]
    jumps = [i / fps for i in range(1, len(d)) if d[i] > 18 and not any(abs(i / fps - c) < 0.12 for c in planned_cuts) and not allowed(i / fps - 0.01, i / fps + 0.01)]
    if jumps: issues["warn"].append(f"{len(jumps)} sudden change(s) that are not planned cuts (at {', '.join(f'{x:.1f}s' for x in jumps[:8])})")
    step = max(1, round(fps / 6))
    motion6 = float(np.mean([np.abs(means[i] - means[i - step]) for i in range(step, len(means), step)])) if len(means) > step else 0
    mean_diff = float(np.mean(d[1:])) if len(d) > 1 else 0
    # --- camera plan against the limits
    cam = R["camera"]; prev = None; pushes = 0; uses = {}
    for s in shots:
        if s["kind"] != "still" or not s.get("move"): prev = None; continue
        name, a0, a1 = s["move"][0], s["move"][1], s["move"][2]; dur = s["end"] - s["start"]
        zr = abs(a1[0] - a0[0]) / dur; pr_ = max(abs(a1[1] - a0[1]), abs(a1[2] - a0[2])) / dur
        if zr > cam["zoom_per_s"] * 1.6 + 1e-3: issues["warn"].append(f"line {s['line']}: zoom speed {zr:.3f}/s over the limit {cam['zoom_per_s']}/s")
        if pr_ > cam["pan_per_s"] * 2.2 + 1e-3 and name not in ("pan", "planned"): issues["warn"].append(f"line {s['line']}: pan speed {pr_:.3f}/s over the limit {cam['pan_per_s']}/s")
        if name == "pan" and pr_ > 0.12: issues["warn"].append(f"line {s['line']}: face-to-face pan at {pr_:.3f}/s is fast")
        if prev == name and name not in ("hold",): issues["warn"].append(f"line {s['line']}: the same move ({name}) twice in a row")
        pushes += name == "push"; prev = name
        key = s.get("pic")
        if key is not None:
            if key in uses and abs(uses[key][0] - s["start"]) > 1 and uses[key][1] == name and not s.get("cut_in"):
                issues["warn"].append(f"picture {key:03d} is used again at {s['start']:.0f} s with the same move ({name}): no new framing")
            uses[key] = (s["start"], name)
    ppm = pushes / max(plan["total"] / 60, 0.1)
    if ppm > 6: issues["warn"].append(f"{ppm:.1f} push-ins a minute (repetitive; aim for under 6)")
    # --- grade per shot, from the video itself
    looks = bible["looks"]; rows = []
    shot_imgs = []
    for k, s in enumerate(shots):
        t = (s["start"] + s["end"]) / 2; im = frame_at(v, t, 480)
        if im is None: continue
        lu, sa = stats(im); shot_imgs.append((im, s, lu, sa))
        lk = looks.get(s.get("look") or "")
        if lk and s["kind"] == "still":
            lo, hi = lk["luma"]
            if lu > hi + 0.08 or lu < lo - 0.08: issues["warn"].append(f"line {s['line']}: brightness {lu:.2f} in the video, outside its look '{s['look']}' ({lo:.2f} to {hi:.2f})")
        rows.append((s, lu, sa))
    for k in range(1, len(rows) - 1):
        s, lu, sa = rows[k]
        if s["kind"] != "still": continue
        nb = [r for r in (rows[k - 1], rows[k + 1]) if s.get("location") and r[0]["kind"] == "still" and r[0].get("location") == s.get("location") and r[0].get("look") == s.get("look")]
        if nb and abs(lu - np.mean([r[1] for r in nb])) > 0.16: issues["warn"].append(f"line {s['line']}: brightness jumps against the next shots in the same place ({lu:.2f} vs {np.mean([r[1] for r in nb]):.2f})")
        if nb and abs(sa - np.mean([r[2] for r in nb])) > 0.18: issues["warn"].append(f"line {s['line']}: saturation jumps against its neighbours ({sa:.2f})")
    # --- text clipping in the graphics used
    rep = {r["id"]: r for r in vv.load_json(proj / "graphics" / "report.json", [])}
    for s in shots:
        if s["kind"] == "graphic":
            gid = Path(s["src"]).stem.split("-")[0]; r = rep.get(gid, {})
            for x in r.get("overflow", []): issues["fail"].append(f"graphic {gid} (line {s['line']}): {x}")
    unrev = [s["line"] for s in shots if s.get("unreviewed")]
    if unrev: issues["warn"].append(f"unreviewed AI clips used for testing on lines {unrev}: not allowed in a full render")
    # --- audio
    I, TP = loudness(v); A = R["audio"]
    if I is not None and abs(I - A["loudness"]) > 1.5: issues["warn"].append(f"loudness {I:.1f} LUFS, the bible says {A['loudness']}")
    if TP is not None and TP > A["true_peak"] + 0.6: issues["warn"].append(f"true peak {TP:.1f} dBFS, over the bible's {A['true_peak']}")
    # --- contact sheets
    font = ImageFont.truetype(FONT, 15)
    cols = 6; tw, th = 320, 180
    sheet = Image.new("RGB", (cols * tw, -(-len(shot_imgs) // cols) * (th + 40)), (16, 14, 12)); dr = ImageDraw.Draw(sheet)
    for k, (im, s, lu, sa) in enumerate(shot_imgs):
        x, y = (k % cols) * tw, (k // cols) * (th + 40)
        sheet.paste(im.resize((tw - 4, th - 4)), (x + 2, y + 2))
        dr.text((x + 4, y + th), f"L{s['line']} {s['kind']} {(s.get('move') or ['-'])[0]} {s['trans'][0]}", font=font, fill=(240, 220, 170))
        dr.text((x + 4, y + th + 18), f"{s['start']:.1f}s  luma {lu:.2f} sat {sa:.2f}", font=font, fill=(170, 160, 150))
    sheet.save(qd / f"{v.stem}-shots.jpg", quality=88)
    T = plan["total"]; mid = (plan["segments"][len(plan["segments"]) // 2]["out"] + 2) if len(plan.get("segments", [])) > 1 else T / 2 - 6
    windows = [("opening", 0.6), ("middle", max(0.6, mid)), ("ending", max(0.6, T - 12.5))]
    strip = Image.new("RGB", (12 * 240, 3 * 160), (0, 0, 0)); ds = ImageDraw.Draw(strip)
    for r, (nm, t0) in enumerate(windows):
        for c in range(12):
            im = frame_at(v, min(T - 0.05, t0 + c), 240)
            if im: strip.paste(im.resize((236, 133)), (c * 240 + 2, r * 160 + 22))
        ds.text((6, r * 160 + 2), f"{nm}: {t0:.1f} s to {t0 + 11:.1f} s, one frame a second", font=font, fill=(240, 220, 170))
    strip.save(qd / f"{v.stem}-strips.jpg", quality=88)
    # --- report
    verdict = "FAIL" if issues["fail"] else ("PASS WITH WARNINGS" if issues["warn"] else "PASS")
    md = [f"# Gate 2 QA: {video}", "", f"**{verdict}** (technical). {len(shots)} shots, {T:.1f} s, {vs['width']}x{vs['height']} at {real_fps:g} fps; settings {plan['settings']} ({plan['version']}).", "",
          f"- Motion: mean frame-to-frame change {mean_diff:.2f} (0 to 255, grain blurred out); change over 1/6 s {motion6:.2f}. Push-ins: {ppm:.1f} a minute.",
          f"- Audio: {I} LUFS integrated, true peak {TP} dBFS; music: {', '.join(plan.get('music') or []) or 'none (voice only)'}.",
          f"- Moves used: " + ", ".join(f"{m} {sum(1 for s in shots if (s.get('move') or [s['kind']])[0] == m)}" for m in sorted({(s.get('move') or [s['kind']])[0] for s in shots})) + ".",
          f"- Transitions: " + ", ".join(f"{t} {sum(1 for s in shots if s['trans'][0] == t)}" for t in sorted({s['trans'][0] for s in shots})) + ".", "",
          "Look at the contact sheets before approving: a clean report does not mean the video is good.", f"- `qa/{v.stem}-shots.jpg`: one frame from the middle of every shot",
          f"- `qa/{v.stem}-strips.jpg`: the opening, the middle and the ending, one frame a second", ""]
    for lvl in ("fail", "warn", "info"):
        md.append(f"## {lvl.upper()} ({len(issues[lvl])})"); md += [f"- {x}" for x in issues[lvl]] or ["- none"]; md.append("")
    md += ["## What a person still has to judge", "", "- Does every camera move serve the line (no move for its own sake)?", "- Do the transitions feel motivated?",
           "- Are characters the same people from shot to shot?", "- Does the grade feel like one film across stills, graphics and clips?", "- Are any AI clips free of warping, flicker and identity drift?",
           "- Does the voice land with the pictures (cuts on breaths, graphics on the words)?"]
    (qd / f"{v.stem}-report.md").write_text("\n".join(md), encoding="utf-8")
    (qd / f"{v.stem}-qa.json").write_text(json.dumps({"verdict": verdict, "issues": issues, "settings": plan["settings"], "motion": motion6, "mean_diff": mean_diff,
                                                         "lufs": I, "true_peak": TP, "at": time.strftime("%Y-%m-%d %H:%M")}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{verdict}: {len(issues['fail'])} fail, {len(issues['warn'])} warnings -> {qd / (v.stem + '-report.md')}")
    for x in issues["fail"][:10]: print("  FAIL", x)
    for x in issues["warn"][:12]: print("  WARN", x)
    return verdict


def approve(proj, video, note):
    proj = Path(proj); v = proj / video; q = vv.load_json(proj / "qa" / f"{v.stem}-qa.json")
    plan = vv.load_json(v.with_name(v.stem + "-plan.json"))
    if not q: sys.exit("run the QA on this video first")
    if q["verdict"] == "FAIL": sys.exit("the QA failed: fix the failures and re-render before approving")
    if any(s.get("unreviewed") for s in plan["shots"]): sys.exit("this sample uses unreviewed test clips: approve those clips (vyapaar_clips.py) and re-render first")
    g = {"approved": True, "video": video, "settings": plan["settings"], "version": plan["version"], "at": time.strftime("%Y-%m-%d %H:%M"), "note": note, "qa": q["verdict"]}
    (proj / "gate2.json").write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gate 2 open for settings {plan['settings']}: a full render with these exact settings may start")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("a"); ap.add_argument("b", nargs="?"); ap.add_argument("--note", default="")
    x = ap.parse_args()
    if x.a == "approve": approve(x.project, x.b, x.note)
    else: check(x.project, x.a)


if __name__ == "__main__":
    main()
