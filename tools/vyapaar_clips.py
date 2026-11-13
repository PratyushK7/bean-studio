"""Hero-shot clips for Decoding Vyapaar, made with xAI image-to-video from the ChatGPT pictures (standard library + ffmpeg).

    python tools/vyapaar_clips.py <project> --pick            # choose the hero lines (top moments), the rest become 'still' (code camera moves)
    python tools/vyapaar_clips.py <project> [--only 1,2] [--seconds 3] [--dry]   # make the clips, one at a time; finished ones are skipped

Each hero line uses the picture whose slot covers that line (images-index.json) and the line's `shot` text as the motion prompt.
Raw clip -> clips/NNN.mp4, smoothed to 48 fps (ffmpeg minterpolate) -> clips/NNN-48.mp4. NNN = script line number.
Cost is about $0.032 per second at 720p; --dry prints the count and the estimate without calling the API.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import xai_media

# the moments that earn motion: the hook, the reversals, the climax and the ending (script line numbers, 1-based)
HEROES = [1, 2, 5, 7, 8, 12, 15, 20, 28, 29, 36, 43, 58, 63, 67, 78, 93, 95, 103, 111, 122, 128, 134, 135, 136]
HINT = " Subtle natural motion only, steady camera, keep the same faces and clean semi-realistic illustration style, no text."


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--pick", action="store_true"); ap.add_argument("--only")
    ap.add_argument("--seconds", type=int, default=3); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); proj = Path(a.project); sp = proj / "script.json"
    s = json.loads(sp.read_text(encoding="utf-8")); L = s["lines"] if isinstance(s, dict) else s
    if a.pick:
        bak = proj / "script-all-hero.json"
        if not bak.exists(): shutil.copy(sp, bak)
        for i, l in enumerate(L):
            if l["kind"] == "hero" and (i + 1) not in HEROES: l["kind"] = "still"
        sp.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{sum(l['kind']=='hero' for l in L)} hero, {sum(l['kind']=='still' for l in L)} still, {sum(l['kind']=='card' for l in L)} card"); return
    index = json.loads((proj / "images-index.json").read_text(encoding="utf-8"))
    want = {int(x) for x in a.only.split(",")} if a.only else None
    todo = [i + 1 for i, l in enumerate(L) if l["kind"] == "hero" and (want is None or i + 1 in want)]
    out = proj / "clips"; out.mkdir(exist_ok=True)
    todo = [n for n in todo if not (out / f"{n:03d}-48.mp4").exists()]
    print(f"{len(todo)} clips to make, about ${len(todo) * a.seconds * 0.032:.2f}", flush=True)
    if a.dry: return
    for n in todo:
        slot = next((e for e in index if e["type"] == "scene" and n in e["lines"]), None)
        pic = next((proj / "images").glob(f"{slot['n']:03d}.*")) if slot else None
        if not pic: print(f"  line {n}: no picture covers it, skipped"); continue
        raw = out / f"{n:03d}.mp4"
        try:
            xai_media.video(str(pic), str(raw), L[n - 1]["shot"] + "." + HINT, a.seconds)
        except SystemExit as ex:
            print(f"  line {n} FAILED: {ex}", flush=True); continue
        r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-vf", "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", str(out / f"{n:03d}-48.mp4")])
        print(f"  line {n} ok (picture {slot['n']}), smoothing {'ok' if r.returncode == 0 else 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
