"""Decoding Vyapaar edit-style samples: the same opening minute cut in four styles, to choose one before a full render.

    python tools/vyapaar_styles.py <project> prep            # subject masks (rembg) + text overlays (Hindi through headless Edge)
    python tools/vyapaar_styles.py <project> A|B|C|D         # render styles/style-X.mp4
    python tools/vyapaar_styles.py <project> compare         # styles/compare-all.mp4: each style after a title card

  A  documentary Ken Burns: one picture per line, one slow constant move aimed at the subject, 0.5 s dissolves, animated number cards
  B  A + 2.5D parallax on the people shots (subject cut out with rembg, background filled with OpenCV inpaint, layers move at different speeds)
  C  fast cuts (HinExp-like): a different picture every 1.5 to 2.5 s, hard cuts; pictures borrowed from later in the video stand in for new ones
  D  motion-graphics explainer: the picture in a framed panel, the key phrase set as type beside it, light theme
No AI video clips are used. Text is rendered by Microsoft Edge (Pillow on this machine cannot shape Devanagari). Voice only: no music yet.
"""
import json, math, subprocess, sys, functools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, FPS = 1920, 1080, 30
UNTIL = 61.0                                     # the sample: lines 1-12, ending on "nobody here knew the answer"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROJ = Path(sys.argv[1]).resolve(); OUT = PROJ / "styles"; TXT = OUT / "txt"; MASK = OUT / "masks"
LINES = json.loads((PROJ / "voice-lines.json").read_text(encoding="utf-8"))
INDEX = json.loads((PROJ / "images-index.json").read_text(encoding="utf-8"))
N_LINES = 12
PIC = {1: 6, 2: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 12, 10: 13, 11: 14, 12: 15}          # line -> picture slot
CARDS = {3: "duty", 9: "chart"}
MOVES_A = {1: "in", 2: "pan_r", 4: "out", 5: "in", 6: "pan_l", 7: "in", 8: "in", 10: "out", 11: "in", 12: "pan_r"}
PARALLAX = {5, 6, 7, 10}
C_SHOTS = {1: [6, 19, 24], 2: [7, 74, 79], 4: [8, 24], 5: [9, 8, "9c", 10], 6: [10, "10c"], 7: [11, 67, 80], 8: [12, 83],
           10: [13, 98, 112, 113], 11: [14, 41], 12: [15, 70, 82]}            # "9c" = a close-up of picture 9
D_TEXT = {1: '<b class=big>23 जुलाई 2024</b><br><span class=sub>बजट का दिन</span>', 2: 'हर दुकान में<br>टीवी चल रहा है',
          4: 'पूरा बाजार<br>उछल पड़ता है', 5: '“रमेश भाई,<br>मुंह मीठा करो!”', 6: 'पर रमेश जी का हाथ<br>नहीं उठता',
          7: 'नजर कोने वाली<br><g>तिजोरी</g> पर', 8: '<b class=big><g>2 किलो</g></b><br>सोना तिजोरी में',
          10: 'दुकान की<br><g>2 साल की कमाई</g><br>2 दिन में गायब', 11: 'सस्ता सोना,<br>बेचने वाले को ही<br>कैसे डुबो सकता है?',
          12: 'किसी को<br>जवाब नहीं पता था'}


def start(i): return LINES[i - 1]["start"]
def end(i): return LINES[i]["start"] if i < N_LINES else UNTIL
def pic_path(n): return next((PROJ / "images").glob(f"{int(str(n).rstrip('c')):03d}.*"))
def ease(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
def env(t, a, b, fade=0.4):
    """opacity envelope: 0 before a, fades in over `fade`, holds, fades out before b"""
    return min(ease((t - a) / fade), ease((b - t) / fade))


# ---------- text overlays through headless Edge ----------
CSS = """<style>html,body{margin:0;width:1920px;height:1080px;background:transparent;overflow:hidden}
*{font-family:'Nirmala UI',sans-serif} .n{font-family:Bahnschrift,'Nirmala UI';font-weight:600} g{color:#d9a63a} .gD g{color:#a8741a}
.abs{position:absolute}</style>"""
OVERLAYS = {
    "date": '<div class=abs style="left:0;right:0;bottom:0;height:380px;background:linear-gradient(transparent,rgba(10,8,6,.62))"></div>'
            '<div class=abs style="left:110px;bottom:120px;border-left:8px solid #d9a63a;padding:6px 0 10px 30px;text-shadow:0 3px 18px rgba(0,0,0,.65)">'
            '<div style="font-size:74px;font-weight:700;color:#fff">23 जुलाई 2024</div><div style="font-size:44px;color:#f1e3c4">बजट का दिन</div></div>',
    "question": '<div class=abs style="left:0;right:0;bottom:0;height:420px;background:linear-gradient(transparent,rgba(10,8,6,.78))"></div>'
                '<div class=abs style="left:0;right:0;bottom:110px;text-align:center;font-size:72px;font-weight:700;color:#fff;line-height:1.35;text-shadow:0 3px 20px rgba(0,0,0,.6)">'
                'सस्ता सोना, सोना बेचने वाले को ही<br><g>कैसे डुबो सकता है?</g></div>',
}
for th, col, sub in (("", "#f6ead2", "#e9d8b4"), ("D", "#2a2420", "#6b5a45")):
    OVERLAYS["duty_label" + th] = f'<div class="abs gD" style="left:0;right:0;top:250px;text-align:center;font-size:68px;font-weight:700;color:{sub}">सोने पर कस्टम ड्यूटी</div>'
    OVERLAYS["duty_15" + th] = f'<div class="abs n" style="left:0;right:0;top:400px;text-align:center;font-size:300px;color:{col}">15%</div>'
    OVERLAYS["duty_15x" + th] = (f'<div class="abs n" style="left:330px;top:400px;width:620px;text-align:center;font-size:300px;color:{col};opacity:.45">15%</div>'
                                 '<div class=abs style="left:390px;top:600px;width:500px;height:16px;background:#d2463c;transform:rotate(-8deg);border-radius:8px"></div>')
    OVERLAYS["duty_6" + th] = (f'<div class="abs n" style="left:950px;top:470px;font-size:170px;color:{sub}">→</div>'
                               f'<div class="abs n" style="left:1150px;top:400px;font-size:300px;color:{"#e3b04b" if not th else "#a8741a"}">6%</div>')
    OVERLAYS["chart_label" + th] = (f'<div class=abs style="left:360px;top:250px;font-size:64px;font-weight:700;color:{col}">सोने का भाव</div>'
                                    f'<div class=abs style="left:360px;top:850px;font-size:44px;color:{sub}">बजट से पहले</div>'
                                    f'<div class=abs style="right:360px;top:850px;font-size:44px;color:{sub}">2 दिन बाद</div>')
    OVERLAYS["chart_7" + th] = '<div class="abs n" style="left:1590px;top:690px;font-size:120px;color:#e0574c;text-shadow:0 3px 18px rgba(0,0,0,.35)">−7%</div>'
for i, t in D_TEXT.items():
    OVERLAYS[f"d{i}"] = ('<style>.big{font-size:104px} .sub{font-size:56px;color:#6b5a45;font-weight:400}</style>'
                         f'<div class="abs gD" style="left:1320px;width:540px;top:0;bottom:0;display:flex;align-items:center;font-size:66px;font-weight:700;color:#2a2420;line-height:1.3">'
                         f'<div>{t}</div></div>')
OVERLAYS["d_tag"] = '<div class=abs style="left:90px;top:84px;font-size:38px;font-weight:700;color:#a8741a;letter-spacing:2px">अध्याय 1 &nbsp;·&nbsp; बजट का दिन</div>'
TITLES = {"A": ("A", "डॉक्यूमेंट्री Ken Burns", "one picture per line · slow moves · dissolves · animated numbers"),
          "B": ("B", "Ken Burns + 2.5D parallax", "people cut out from the background, layers move separately"),
          "C": ("C", "Fast cuts (HinExp-like)", "a new picture every 1.5–2.5 s · hard cuts · stand-in pictures"),
          "D": ("D", "Motion-graphics explainer", "framed picture + key phrase as type · light theme")}
for k, (a, b, c) in TITLES.items():
    OVERLAYS["title" + k] = (f'<div class=abs style="inset:0;background:#14110e"></div><div class=abs style="left:160px;top:330px;color:#fff">'
                             f'<div class=n style="font-size:200px;color:#d9a63a;line-height:1">Style {a}</div><div style="font-size:84px;font-weight:700;margin-top:30px">{b}</div>'
                             f'<div style="font-size:44px;color:#b9ad9a;margin-top:20px">{c}</div></div>')


def render_texts():
    """write every overlay as HTML, then render them all in one Chromium (tools/video/render_overlays.js)"""
    for name, body in OVERLAYS.items():
        page = TXT / f"{name}.html"; html = f"<!doctype html><meta charset=utf-8>{CSS}{body}"
        if not page.exists() or page.read_text(encoding="utf-8") != html:
            page.write_text(html, encoding="utf-8"); (TXT / f"{name}.png").unlink(missing_ok=True)
    subprocess.run(["node", str(Path(__file__).resolve().parent / "video" / "render_overlays.js"), str(TXT)], check=True)


def prep():
    TXT.mkdir(parents=True, exist_ok=True); MASK.mkdir(exist_ok=True)
    render_texts()
    print("text overlays:", len(list(TXT.glob("*.png"))), "of", len(OVERLAYS))
    from rembg import remove, new_session
    s = new_session("u2net")
    need = set(PIC.values()) | {int(str(x).rstrip("c")) for v in C_SHOTS.values() for x in v}
    for n in sorted(need):
        m = MASK / f"{n:03d}.png"
        if not m.exists(): remove(Image.open(pic_path(n)).convert("RGB"), session=s, only_mask=True).save(m)
    print("masks:", len(need))


# ---------- pictures ----------
@functools.lru_cache(maxsize=None)
def picture(n): return Image.open(pic_path(n)).convert("RGB")


@functools.lru_cache(maxsize=None)
def focus(n):
    """the subject's centre (fractions of the picture) from its mask; the centre of the frame if there is no clear subject"""
    mp = MASK / f"{int(str(n).rstrip('c')):03d}.png"
    if not mp.exists(): return 0.5, 0.45                                         # no mask yet: aim at the frame centre
    m = Image.open(mp).convert("L").point(lambda v: 255 if v > 128 else 0)
    box = m.getbbox()
    if not box or (box[2] - box[0]) * (box[3] - box[1]) > 0.8 * m.size[0] * m.size[1]: return 0.5, 0.45
    w, h = m.size
    return (box[0] + box[2]) / 2 / w, (box[1] + box[3] * 0.6) / 1.6 / h          # biased to the top of the subject (faces)


def crop(src, z, cx, cy, size=(W, H)):
    sw, sh = src.size; w, h = sw / z, sh / z
    x0 = min(max(cx * sw - w / 2, 0), sw - w); y0 = min(max(cy * sh - h / 2, 0), sh - h)
    return src.resize(size, Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))


def move(kind, p, n, rate=1.0):
    """(zoom, cx, cy) at progress p (0-1) of a constant-speed Ken Burns move"""
    fx, fy = focus(n); dz = 0.10 * rate
    cx_f, cy_f = 0.5 + (fx - 0.5) * 0.6, 0.5 + (fy - 0.5) * 0.6                 # drift towards the subject, never all the way
    if kind == "in": return 1.0 + dz * p, 0.5 + (cx_f - 0.5) * p, 0.5 + (cy_f - 0.5) * p
    if kind == "out": return 1.0 + dz * (1 - p), 0.5 + (cx_f - 0.5) * (1 - p), 0.5 + (cy_f - 0.5) * (1 - p)
    if kind == "close": return 1.28 + 0.04 * p, fx, fy
    a, b = (0.42, 0.58) if kind == "pan_r" else (0.58, 0.42)
    return 1.12, a + (b - a) * p, 0.5


# ---------- parallax layers (style B) ----------
@functools.lru_cache(maxsize=None)
def layers(n):
    import cv2, numpy as np
    img = picture(n); m = Image.open(MASK / f"{n:03d}.png").convert("L")
    fg = img.copy(); fg.putalpha(m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6)))
    a = np.array(img); mk = np.array(m.point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(31)))
    small = cv2.resize(a, (a.shape[1] // 2, a.shape[0] // 2)); smk = cv2.resize(mk, (a.shape[1] // 2, a.shape[0] // 2))
    fill = cv2.resize(cv2.inpaint(small, smk, 9, cv2.INPAINT_TELEA), (a.shape[1], a.shape[0]))
    bg = np.where(mk[..., None] > 0, fill, a)
    return Image.fromarray(bg).filter(ImageFilter.GaussianBlur(0.6)), fg


def parallax_frame(n, p, kind):
    bg, fg = layers(n); fx, fy = focus(n)
    zb = 1.04 + 0.04 * p; zf = 1.04 + 0.12 * p
    dx = (0.5 - p) * 0.03 * (1 if kind != "pan_l" else -1)
    frame = crop(bg, zb, 0.5 + dx, 0.5).convert("RGBA")
    frame.alpha_composite(crop(fg, zf, 0.5 - dx * 1.5 + (fx - 0.5) * 0.25 * p, 0.5 + (fy - 0.5) * 0.25 * p))
    return frame.convert("RGB")


# ---------- overlays and cards ----------
@functools.lru_cache(maxsize=None)
def overlay(name, level):
    im = Image.open(TXT / f"{name}.png").convert("RGBA")
    if level < 16: im.putalpha(im.getchannel("A").point(lambda v: v * level // 16))
    return im


def put(frame, name, alpha, dy=0):
    if alpha <= 0.01: return frame
    frame = frame.convert("RGBA"); frame.alpha_composite(overlay(name, max(1, round(alpha * 16))), dest=(0, int(dy)))
    return frame


@functools.lru_cache(maxsize=None)
def card_bg(kind, theme):
    if theme == "D": return Image.new("RGB", (W, H), (244, 236, 223))
    src = crop(picture(7 if kind == "duty" else 12), 1.0, 0.5, 0.5).filter(ImageFilter.GaussianBlur(34))
    return Image.blend(src, Image.new("RGB", (W, H), (22, 17, 12)), 0.68)


@functools.lru_cache(maxsize=None)
def chart_line(theme):
    S = 2; im = Image.new("RGBA", (W * S, H * S)); d = ImageDraw.Draw(im)
    pts = []
    for k in range(121):
        u = k / 120
        y = 0.12 + 0.015 * math.sin(u * 37) if u < 0.32 else 0.12 + 0.72 * ease((u - 0.32) / 0.68) + 0.02 * math.sin(u * 29) * (1 - u)
        pts.append(((360 + 1200 * u) * S, (380 + 440 * y) * S))
    d.line([(360 * S, 820 * S), (1560 * S, 820 * S)], fill=(150, 130, 105, 150), width=3 * S)
    d.line(pts, fill=(227, 176, 75, 255) if theme != "D" else (168, 116, 26, 255), width=9 * S, joint="curve")
    return im.resize((W, H), Image.LANCZOS), [(x / S, y / S) for x, y in pts]


def card(kind, t, dur, theme=""):
    frame = crop(card_bg(kind, theme), 1.0 + 0.03 * t / dur, 0.5, 0.5) if theme != "D" else card_bg(kind, theme).copy()
    if kind == "duty":
        t15, t6 = dur * 0.52, dur * 0.80                                          # when "पंद्रह" and "छह" are said
        frame = put(frame, "duty_label" + theme, env(t, 0.3, dur + 1))
        frame = put(frame, "duty_15" + theme, env(t, t15 - 0.2, t6 + 0.15, 0.3), dy=20 * (1 - ease((t - t15 + 0.2) / 0.4)))
        frame = put(frame, "duty_15x" + theme, ease((t - t6) / 0.3))
        frame = put(frame, "duty_6" + theme, ease((t - t6) / 0.35), dy=24 * (1 - ease((t - t6) / 0.4)))
    else:
        line, pts = chart_line(theme)
        frame = put(frame, "chart_label" + theme, env(t, 0.1, dur + 1))
        q = ease((t - 0.4) / (dur * 0.6)); x = 360 + 1200 * q
        if q > 0:
            frame = frame.convert("RGBA"); part = line.crop((0, 0, int(x) + 1, H)); frame.alpha_composite(part)
            px, py = pts[min(int(q * 120), 120)]; ImageDraw.Draw(frame).ellipse((px - 13, py - 13, px + 13, py + 13), fill=(240, 90, 76, 255))
        frame = put(frame, "chart_7" + theme, ease((t - 0.4 - dur * 0.6) / 0.35))
    return frame.convert("RGB")


# ---------- styles ----------
def shots_for(style):
    """list of (t0, t1, draw(t_local, dur) -> Image)"""
    out = []
    for i in range(1, N_LINES + 1):
        a, b = start(i), end(i)
        if i in CARDS:
            out.append((a, b, lambda t, d, k=CARDS[i]: card(k, t, d, "D" if style == "D" else ""), True)); continue
        n = PIC[i]
        if style == "C":
            seq = C_SHOTS[i]; k = len(seq)
            for j, s in enumerate(seq):
                kind = "close" if str(s).endswith("c") else ["in", "pan_r", "out", "pan_l"][(i + j) % 4]
                out.append((a + (b - a) * j / k, a + (b - a) * (j + 1) / k,
                            lambda t, d, s=s, kind=kind: crop(picture(int(str(s).rstrip("c"))), *move(kind, t / d, s, 0.6)), False))
        elif style == "B" and n in PARALLAX and i in PARALLAX_LINES:
            out.append((a, b, lambda t, d, n=n, kind=MOVES_A[i]: parallax_frame(n, t / d, kind), False))
        else:
            out.append((a, b, lambda t, d, n=n, kind=MOVES_A[i]: crop(picture(n), *move(kind, t / d, n, min(1.2, d / 5))), False))
    return out


PARALLAX_LINES = {5, 6, 7, 10}
PIC_PARALLAX = {PIC[i] for i in PARALLAX_LINES}
PARALLAX = PIC_PARALLAX


@functools.lru_cache(maxsize=None)
def d_base():
    bg = Image.new("RGB", (W, H), (244, 236, 223))
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((90, 228, 1250, 880), 30, fill=110)
    bg.paste((90, 70, 40), (0, 0), sh.filter(ImageFilter.GaussianBlur(26)))
    return put(bg, "d_tag", 1).convert("RGB")


@functools.lru_cache(maxsize=None)
def d_mask():
    m = Image.new("L", (1160, 652), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 1159, 651), 28, fill=255); return m


def render(style):
    sh = shots_for(style)
    dis = {"A": 0.5, "B": 0.5, "C": 0.0, "D": 0.35}[style]
    total = UNTIL + 0.7; nf = round(total * FPS)
    out = OUT / f"style-{style}-video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)

    def shot_img(k, t):
        a, b, f, is_card = sh[k]; lo, hi = a - dis / 2, b + dis / 2
        img = f(min(max(t - lo, 0), hi - lo), hi - lo)
        if style == "D" and not is_card:
            base = d_base().copy(); base.paste(img.resize((1160, 652), Image.LANCZOS), (90, 228), d_mask()); img = base
        return img

    for fi in range(nf):
        t = fi / FPS
        k = max(j for j in range(len(sh)) if sh[j][0] <= min(t, UNTIL - 1e-6))
        img = shot_img(k, t)
        if dis and k + 1 < len(sh) and t > sh[k][1] - dis / 2:
            img = Image.blend(img, shot_img(k + 1, t), ease((t - (sh[k][1] - dis / 2)) / dis))
        elif dis and k > 0 and t < sh[k][0] + dis / 2:
            img = Image.blend(shot_img(k - 1, t), img, ease((t - (sh[k][0] - dis / 2)) / dis))
        if style == "D":
            for i in D_TEXT:
                if start(i) - 0.2 < t < end(i) + 0.3:
                    img = put(img, f"d{i}", env(t, start(i) + 0.1, end(i) + 0.1, 0.35), dy=26 * (1 - ease((t - start(i) - 0.1) / 0.45)))
        else:
            img = put(img, "date", env(t, 0.5, 4.3, 0.5), dy=0)
            img = put(img, "question", env(t, start(11) + 0.2, end(11) - 0.1, 0.4))
        if t < 0.5: img = Image.blend(Image.new("RGB", (W, H)), img.convert("RGB"), ease(t / 0.5))
        if t > UNTIL: img = Image.blend(img.convert("RGB"), Image.new("RGB", (W, H)), ease((t - UNTIL) / 0.6))
        enc.stdin.write(img.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    final = OUT / f"style-{style}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out), "-i", str(PROJ / "voice.mp3"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", f"afade=t=out:st={UNTIL - 0.2}:d=0.8", "-c:a", "aac", "-b:a", "192k", "-t", f"{total}", str(final)], check=True)
    out.unlink(); print("wrote", final)


def compare():
    parts = []
    for k in "ABCD":
        tc = OUT / f"title-{k}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", "2.5", "-i", str(TXT / f"title{k}.png"),
                        "-f", "lavfi", "-t", "2.5", "-i", "anullsrc=r=44100:cl=stereo", "-vf", f"scale={W}:{H},format=yuv420p,fade=t=in:d=0.3,fade=t=out:st=2.1:d=0.4",
                        "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", str(tc)], check=True)
        parts += [tc, OUT / f"style-{k}.mp4"]
    inputs = sum((["-i", str(p)] for p in parts), [])
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", str(OUT / "compare-all.mp4")], check=True)
    print("wrote", OUT / "compare-all.mp4")


if __name__ == "__main__":
    cmd = sys.argv[2]
    if cmd == "prep": prep()
    elif cmd == "compare": compare()
    elif cmd == "texts": TXT.mkdir(parents=True, exist_ok=True); render_texts()
    else: render(cmd)
