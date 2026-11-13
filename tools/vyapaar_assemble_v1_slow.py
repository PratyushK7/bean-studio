"""Decoding Vyapaar final assembler: pictures + hero clips + code-drawn cards + voice/sound mix -> video.mp4 (1920x1080, 48 fps), no burned-in subtitles.

    python tools/vyapaar_assemble.py <project> [--limit 12] [--workers 3]      # --limit renders only the first N lines (a quick check, writes preview.mp4)

Per script line, timed by voice-lines.json: hero -> clips/NNN-48.mp4 (held on its last frame if the line runs longer);
still -> the picture whose slot covers the line, with a code camera move (push-in, pull-out, pan, rise) that changes line to line;
card -> a graphic drawn here (Pillow) from the line's `screen` text with a slow push-in.
Frame counts come from cumulative times, so rounding never drifts the picture away from the voice. Mixed audio is mix.mp3 (vyapaar_mix.py).
"""
import argparse, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 48
FONT = "C:/Windows/Fonts/Nirmala.ttc"
SYMFONT = "C:/Windows/Fonts/seguisym.ttf"
MOVES = ["in", "out", "left", "right", "rise", "in", "right", "left"]      # cycled with a per-line offset so neighbours differ


def card(text, out):
    im = Image.new("RGB", (W, H), (244, 235, 217)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=(201, 150, 43)); d.rectangle([0, H - 18, W, H], fill=(201, 150, 43))
    size = 150
    while True:
        f = ImageFont.truetype(FONT, size, index=1)                              # Nirmala UI Bold
        sym = ImageFont.truetype(SYMFONT, size)                                  # Nirmala has no arrow glyph
        fnt = lambda ch: sym if ch == "→" else f
        width = lambda t: sum(d.textlength(ch, font=fnt(ch)) for ch in t)
        words, lines, cur = text.split(" "), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if width(t) <= W - 300: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) * size * 1.25 <= H - 300 or size <= 70: break
        size -= 10
    y = (H - len(lines) * size * 1.25) / 2
    for ln in lines:
        x = (W - width(ln)) / 2
        for ch in ln: d.text((x, y), ch, font=fnt(ch), fill=(38, 34, 30)); x += d.textlength(ch, font=fnt(ch))
        y += size * 1.25
    im.save(out)


def zoompan(n, move, d):
    z = {"in": "1+0.12*on/%d" % d, "out": "1.12-0.12*on/%d" % d, "left": "1.1", "right": "1.1", "rise": "1.1"}[move]
    x = {"left": "(iw-iw/zoom)*(1-on/%d)" % d, "right": "(iw-iw/zoom)*on/%d" % d}.get(move, "iw/2-(iw/zoom/2)")
    y = {"rise": "(ih-ih/zoom)*(1-on/%d)" % d}.get(move, "ih/2-(ih/zoom/2)")
    return f"scale=3840:2160,zoompan=z='{z}':x='{x}':y='{y}':d={d}:s={W}x{H}:fps={FPS}"


def run(cmd):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *cmd], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-300:])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(); proj = Path(a.project)
    L = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    T = json.loads((proj / "voice-lines.json").read_text(encoding="utf-8"))
    index = json.loads((proj / "images-index.json").read_text(encoding="utf-8"))
    n_lines = a.limit or len(L); seg = proj / "segs"; seg.mkdir(exist_ok=True); (proj / "cards").mkdir(exist_ok=True)
    jobs = []
    for i in range(n_lines):
        n = i + 1; f0, f1 = round(T[i]["start"] * FPS), round(T[i]["end"] * FPS)
        if i == len(L) - 1: f1 += FPS                                            # a beat of picture after the last word
        fr = max(f1 - f0, 2); out = seg / f"{n:03d}.mp4"; k = L[i]["kind"]
        enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(fr), "-an", str(out)]
        if k == "hero" and (proj / "clips" / f"{n:03d}-48.mp4").exists():
            cmd = ["-i", str(proj / "clips" / f"{n:03d}-48.mp4"), "-vf", f"scale={W}:{H},tpad=stop_mode=clone:stop={fr},fps={FPS}", *enc]
        else:
            if k == "card":
                pic = proj / "cards" / f"{n:03d}.png"; card(L[i]["screen"], pic); move = "in"
            else:
                slot = next((e for e in index if e["type"] == "scene" and n in e["lines"]), None)
                pic = next((proj / "images").glob(f"{slot['n']:03d}.*")) if slot else None
                if not pic: print(f"line {n}: no picture, using a card"); pic = proj / "cards" / f"{n:03d}.png"; card(L[i]["screen"] or "…", pic)
                move = MOVES[(i * 3 + len(jobs)) % len(MOVES)]
            cmd = ["-loop", "1", "-framerate", str(FPS), "-i", str(pic), "-vf", zoompan(n, move, fr), *enc]
        jobs.append((n, cmd))
    done = 0
    def one(j):
        run(j[1]); return j[0]
    with ThreadPoolExecutor(a.workers) as ex:
        for n in ex.map(one, jobs):
            done += 1
            if done % 10 == 0 or done == len(jobs): print(f"  {done}/{len(jobs)} segments", flush=True)
    lst = proj / "segs.txt"; lst.write_text("".join(f"file 'segs/{n:03d}.mp4'\n" for n, _ in jobs), encoding="utf-8")
    out = proj / ("preview.mp4" if a.limit else "video.mp4")
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(proj / "mix.mp3"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    print("wrote", out)


if __name__ == "__main__":
    main()
