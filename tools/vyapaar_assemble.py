"""Decoding Vyapaar assembler v2: pictures + hero clips + code cards + audio -> video.mp4 (1920x1080, 48 fps). No subtitles are burned in.

    python tools/vyapaar_assemble.py <project> [--limit 20] [--workers 4] [--audio voice.mp3]

Why v2: v1 cut one picture per script line (6.5 s on average) with ffmpeg zoompan and held 3 s clips frozen for the rest of long lines.
Measured on the first cut: 266 frozen stretches and a 6-second average shot, against the 1-4 s cuts of the reference channels.
Now every frame is computed here (Pillow, sub-pixel crop, eased camera) and piped straight into the encoder, so there are no segment seams:
  * every line is cut into shots of about 3 s (2-4 s); each shot is a different framing of the picture (push-in, pan, tighter push, pull-out), never a freeze;
  * a hero line plays its clip once at native speed, then continues from the clip's LAST frame (zoom starts at 1.0, so the join is invisible);
  * cards are drawn here and pushed in slowly;
  * the picture is never cropped tighter than 1.3x, so it stays sharp; a light unsharp mask is applied to every frame.
Frame counts come from cumulative times, so the picture cannot drift from the voice. The file is rendered in parallel chunks and joined with a stream copy.
"""
import argparse, json, os, random, subprocess
from multiprocessing import Pool
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 48
FONT, SYMFONT = "C:/Windows/Fonts/Nirmala.ttc", "C:/Windows/Fonts/seguisym.ttf"
SHOT_S = 3.0                                                     # target shot length in seconds
FRAME_BYTES = W * H * 3


def card(text, out):
    im = Image.new("RGB", (W, H), (244, 235, 217)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=(201, 150, 43)); d.rectangle([0, H - 18, W, H], fill=(201, 150, 43))
    size = 150
    while True:
        f = ImageFont.truetype(FONT, size, index=1); sym = ImageFont.truetype(SYMFONT, size)       # Nirmala has no arrow glyph
        fnt = lambda ch: sym if ch == "\u2192" else f
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
        for ch in ln:
            d.text((x, y), ch, font=fnt(ch), fill=(38, 34, 30)); x += d.textlength(ch, font=fnt(ch))
        y += size * 1.25
    im.save(out)


def ease(t):
    return t * t * (3 - 2 * t)


def framing(rng, k):
    """(z0, z1, cx0, cx1, cy) for shot k of a line; cx/cy are fractions of the picture, z is the zoom (never above 1.3)"""
    side = rng.choice([0.4, 0.6])
    if k == 0: return 1.0, 1.09, 0.5, 0.5, 0.5
    return [(1.18, 1.22, side, 1 - side, 0.46), (1.14, 1.28, 0.45 + 0.1 * rng.random(), 0.5, 0.46), (1.26, 1.05, 0.5, 0.5, 0.48)][(k - 1) % 3]


def crop_frame(src, z, cx, cy):
    sw, sh = src.size; w, h = sw / z, sh / z
    x0 = min(max(cx * sw - w / 2, 0), sw - w); y0 = min(max(cy * sh - h / 2, 0), sh - h)
    im = src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    return im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=35, threshold=2)) if z > 1.001 else im


def shots(src, F, rng, enc):
    """write F frames of `src`, cut into shots of about SHOT_S seconds"""
    parts = max(1, round(F / (SHOT_S * FPS)))
    bounds = [round(F * i / parts) for i in range(parts + 1)]
    for k in range(parts):
        m = bounds[k + 1] - bounds[k]
        z0, z1, a, b, cy = framing(rng, k)
        for f in range(m):
            t = ease(f / max(m - 1, 1))
            enc.stdin.write(crop_frame(src, z0 + (z1 - z0) * t, a + (b - a) * t, cy).tobytes())


def render_chunk(job):
    items, out = job
    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "96", "-threads", "2", out], stdin=subprocess.PIPE)
    cache = {}
    def load(p):
        if p not in cache:
            cache.clear(); cache[p] = Image.open(p).convert("RGB")
        return cache[p]
    for n, kind, F, pic, clip in items:
        rng = random.Random(n)
        if kind == "hero" and clip:
            dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", clip, "-vf", f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            last, got = None, 0
            while got < F:
                b = dec.stdout.read(FRAME_BYTES)
                if len(b) < FRAME_BYTES: break
                enc.stdin.write(b); last = b; got += 1
            dec.kill()
            if got < F and last: shots(Image.frombytes("RGB", (W, H), last), F - got, rng, enc)      # continue from the clip's last frame
        elif kind == "card":
            src = load(pic)
            for f in range(F): enc.stdin.write(crop_frame(src, 1 + 0.04 * ease(f / max(F - 1, 1)), 0.5, 0.5).tobytes())
        else:
            shots(load(pic), F, rng, enc)
    enc.stdin.close(); enc.wait()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, min(5, (os.cpu_count() or 4) - 1))); ap.add_argument("--audio", default="voice.mp3")
    a = ap.parse_args(); proj = Path(a.project)
    L = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    T = json.loads((proj / "voice-lines.json").read_text(encoding="utf-8"))
    index = json.loads((proj / "images-index.json").read_text(encoding="utf-8"))
    N = a.limit or len(L); (proj / "cards").mkdir(exist_ok=True); (proj / "chunks").mkdir(exist_ok=True); items = []
    for i in range(N):
        n = i + 1; f0 = round(T[i]["start"] * FPS)
        f1 = round(T[i + 1]["start"] * FPS) if i + 1 < len(L) else round(T[i]["end"] * FPS) + FPS
        k = L[i]["kind"]; pic = clip = None
        if k == "card":
            pic = str(proj / "cards" / f"{n:03d}.png"); card(L[i]["screen"], pic)
        else:
            slot = next((e for e in index if e["type"] == "scene" and n in e["lines"]), None)
            g = next((proj / "images").glob(f"{slot['n']:03d}.*"), None) if slot else None
            if g: pic = str(g)
            else:
                k = "card"; pic = str(proj / "cards" / f"{n:03d}.png"); card(L[i]["screen"] or "...", pic); print(f"line {n}: no picture, drew a card")
            c = proj / "clips" / f"{n:03d}-48.mp4"
            if k == "hero" and c.exists(): clip = str(c)
        items.append((n, k, f1 - f0, pic, clip))
    per = -(-len(items) // a.workers)
    jobs = [(items[c * per:(c + 1) * per], str(proj / "chunks" / f"{c}.mp4")) for c in range(a.workers) if items[c * per:(c + 1) * per]]
    with Pool(len(jobs)) as p: outs = p.map(render_chunk, jobs)
    lst = proj / "chunks.txt"; lst.write_text("".join(f"file 'chunks/{Path(o).name}'\n" for o in outs), encoding="utf-8")
    out = proj / ("preview.mp4" if a.limit else "video.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(proj / a.audio), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
