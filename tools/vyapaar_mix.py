"""Decoding Vyapaar sound step: voice + music + ambience + sound effects -> one mixed track (numpy and ffmpeg only).

    python tools/vyapaar_mix.py <project> [--voice voice.mp3] [--lines voice-lines.json] [--out mix.mp3] [--music-gain -20]

Reads <project>/script.json. Each line may carry (all optional, set from the beat sheet's feeling column):
    "music": "tense|warm|curious|sad|hopeful"   the mood starts on this line and holds until the next "music"
    "amb":   "crowd|fan|tv|flame|none"           a quiet looping bed, same rule
    "sfx":   "coin" or ["whoosh", "thud@1.5"]    effects placed at the line's start (+ an offset in seconds after @)
Timings come from --lines (voice-lines.json from vyapaar_voice.py, or preview-local-lines.json from preview.py).
Music: <project>/audio/music/<mood>.(mp3|wav) if present, else a synthesised placeholder (thin: replace it with a real track).
Effects: <project>/audio/sfx/<name>.(wav|mp3) if present, else the built-in synthesised one.
The music ducks under the voice (attack 0.15 s, release 0.7 s) and the sum is levelled to -14 LUFS, like the voice step.
"""
import argparse, json, subprocess, sys, wave
from pathlib import Path
try:
    import numpy as np
except ImportError:                      # re-run with the animation kit's Python, which has numpy
    py = Path.home() / ".claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit/.venv/Scripts/python.exe"
    if py.exists() and Path(sys.executable).resolve() != py.resolve(): sys.exit(subprocess.run([str(py), __file__, *sys.argv[1:]]).returncode)
    sys.exit("needs numpy")

SR = 48000
rng = np.random.default_rng(11)


def ff_decode(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    if r.returncode: sys.exit(f"ffmpeg could not read {path}: {r.stderr[-200:]!r}")
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def write_wav(path, x):
    x = np.clip(x, -1, 1); w = wave.open(str(path), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype("<i2").tobytes()); w.close()


# ---------- synthesised placeholders ----------
def T(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, d=None, r=0.05):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if d: e *= np.exp(-np.arange(n) / SR * d)
    nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr); return e
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = a * s + (1 - a) * x[i]; y[i] = s
    return y
def noise(d): return rng.standard_normal(int(d * SR))
def sweep(d, f0, f1):
    t = T(d); f = f0 * (f1 / f0) ** (t / d); return np.sin(2 * np.pi * np.cumsum(f) / SR)

SFX = {
    "whoosh": lambda: lowpass(noise(0.9), 2500) * np.sin(np.pi * T(0.9) / 0.9) ** 2 * 0.9,
    "whoosh_soft": lambda: lowpass(noise(0.7), 1200) * np.sin(np.pi * T(0.7) / 0.7) ** 2 * 0.6,
    "thud": lambda: np.sin(2 * np.pi * 52 * T(1.1)) * env(int(1.1 * SR), d=4.5, r=0.2) + np.pad(lowpass(noise(0.12), 400) * env(int(0.12 * SR), d=30), (0, int(1.1 * SR) - int(0.12 * SR))) * 0.6,
    "coin": lambda: (np.sin(2 * np.pi * 2700 * T(0.8)) + 0.6 * np.sin(2 * np.pi * 4100 * T(0.8))) * env(int(0.8 * SR), a=0.001, d=7, r=0.1) * 0.5,
    "page": lambda: lowpass(noise(0.35), 3500) * env(int(0.35 * SR), a=0.01, d=9, r=0.1) * 0.6,
    "tick": lambda: np.sin(2 * np.pi * 1800 * T(0.12)) * env(int(0.12 * SR), a=0.001, d=40, r=0.03) * 0.5,
    "scale_ping": lambda: (np.sin(2 * np.pi * 1300 * T(1.2)) + 0.5 * np.sin(2 * np.pi * 1950 * T(1.2))) * env(int(1.2 * SR), a=0.002, d=3.5, r=0.2) * 0.35,
    "door": lambda: lowpass(noise(0.4), 700) * env(int(0.4 * SR), a=0.02, d=7, r=0.1) * 0.9,
    "shutter": lambda: lowpass(noise(1.6), 2200) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * T(1.6))) * env(int(1.6 * SR), a=0.05, d=1.2, r=0.4) * 0.7,
    "riser": lambda: (sweep(3.0, 180, 1400) * 0.4 + lowpass(noise(3.0), 3000) * 0.3) * (T(3.0) / 3.0) ** 2 * env(int(3.0 * SR), a=0.1, r=0.05),
    "stinger": lambda: (sweep(1.6, 120, 40) * 0.9 + np.sin(2 * np.pi * 73.4 * T(1.6)) * 0.4) * env(int(1.6 * SR), a=0.004, d=2.2, r=0.3),
}
def bed_crowd(d):  # babble: band-passed noise with slow swell
    x = lowpass(noise(d), 1800) - lowpass(noise(d), 300) * 0.0
    x = lowpass(x, 1800); return x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * T(d)))
def bed_fan(d): return (np.sin(2 * np.pi * 42 * T(d)) * 0.25 + lowpass(noise(d), 400) * 0.5) * (0.85 + 0.15 * np.sin(2 * np.pi * 1.6 * T(d)))
def bed_tv(d): return lowpass(noise(d), 1500) * (0.5 + 0.5 * (np.sin(2 * np.pi * 2.3 * T(d)) > 0.2))
def bed_flame(d): return lowpass(noise(d), 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 5 * T(d))))
BEDS = {"crowd": bed_crowd, "fan": bed_fan, "tv": bed_tv, "flame": bed_flame}

MOODS = {  # root, chord intervals (semitones), pulse seconds (0 = none), brightness
    "tense": (146.83, [0, 3, 7, 10], 1.0, 0.5), "warm": (261.63, [0, 4, 7, 11], 0.0, 0.8), "curious": (220.0, [0, 3, 7, 14], 2.0, 0.7),
    "sad": (220.0, [0, 3, 7], 0.0, 0.35), "hopeful": (261.63, [0, 4, 7, 12], 0.0, 1.0)}
def music_loop(mood, d=48):
    root, ch, pulse, br = MOODS[mood]; t = T(d); x = np.zeros_like(t)
    for k, s in enumerate(ch):
        f = root * 2 ** (s / 12); lfo = 0.7 + 0.3 * np.sin(2 * np.pi * (0.05 + 0.013 * k) * t + k)
        x += (np.sin(2 * np.pi * f * t) + 0.35 * br * np.sin(2 * np.pi * 2 * f * t)) * lfo
    x += 0.5 * np.sin(2 * np.pi * (root / 2) * t)
    if pulse: x *= 0.7 + 0.3 * np.sin(np.pi * (t % pulse) / pulse) ** 2
    x /= np.max(np.abs(x)); fade = int(2 * SR); x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)   # seamless-ish loop
    return x * 0.8


def find_asset(proj, kind, name):
    for ext in ("wav", "mp3", "m4a", "ogg"):
        p = proj / "audio" / kind / f"{name}.{ext}"
        if p.exists(): return ff_decode(p)
    return None


def loop_to(x, n):
    if len(x) >= n: return x[:n]
    fade = int(1.5 * SR); out = np.zeros(n); pos = 0
    while pos < n:
        seg = x.copy()
        if pos: seg[:fade] *= np.linspace(0, 1, fade)
        if pos + len(seg) < n: seg[-fade:] *= np.linspace(1, 0, fade)
        m = min(len(seg), n - pos); out[pos:pos + m] += seg[:m]; pos += len(x) - fade
    return out


def sections(lines, times, key, total):
    """[(start_s, end_s, value)] where a line's value starts a section that holds until the next value"""
    pts = [(times[i][0], l[key]) for i, l in enumerate(lines) if l.get(key)]
    return [(a, (pts[k + 1][0] if k + 1 < len(pts) else total), v) for k, (a, v) in enumerate(pts)]


def duck_curve(voice, depth_db=-9.0):
    hop = int(0.02 * SR); n = len(voice) // hop
    rms = np.sqrt(np.mean(voice[:n * hop].reshape(n, hop) ** 2, axis=1)); active = (rms > 10 ** (-45 / 20)).astype(float)
    a_att, a_rel = np.exp(-0.02 / 0.15), np.exp(-0.02 / 0.7); g = np.empty(n); s = 0.0
    for i in range(n):
        a = a_att if active[i] > s else a_rel; s = a * s + (1 - a) * active[i]; g[i] = s
    return np.interp(np.arange(len(voice)), np.arange(n) * hop + hop / 2, 10 ** (depth_db * g / 20))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--voice", default="voice.mp3"); ap.add_argument("--lines", default="voice-lines.json")
    ap.add_argument("--out", default="mix.mp3"); ap.add_argument("--music-gain", type=float, default=-20.0, help="music level in dB relative to the voice when nobody speaks")
    a = ap.parse_args(); proj = Path(a.project)
    lines = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    t = json.loads((proj / a.lines).read_text(encoding="utf-8")); times = [(x["start"], x["end"]) for x in t]
    if len(times) != len(lines): sys.exit(f"{a.lines} has {len(times)} lines but script.json has {len(lines)}: make the voice again from the current script")
    voice = ff_decode(proj / a.voice); total = len(voice) / SR + 2.0; n = int(total * SR)
    mix = np.zeros(n); mix[:len(voice)] += voice
    # music
    music = np.zeros(n); made = []
    for s0, s1, mood in sections(lines, times, "music", total):
        if mood in ("none", ""): continue
        src = find_asset(proj, "music", mood)
        if src is None:
            if mood not in MOODS: print(f"  unknown mood {mood!r}, skipped"); continue
            src = music_loop(mood); made.append(mood)
        i0, i1 = int(s0 * SR), min(n, int((s1 + 2.5) * SR)); seg = loop_to(src, i1 - i0)
        x = 2.5 * SR; m = len(seg); w = np.ones(m); fi = min(int(x), m); w[:fi] *= np.linspace(0, 1, fi); w[-fi:] *= np.linspace(1, 0, fi)
        music[i0:i1] += seg * w
    music *= 10 ** (a.music_gain / 20) / max(np.max(np.abs(music)), 1e-9) * 0.9 * np.max(np.abs(voice)) if np.any(music) else 0
    mix += music * duck_curve(np.pad(voice, (0, n - len(voice))))
    # ambience beds (quiet, ducked a little)
    for s0, s1, name in sections(lines, times, "amb", total):
        if name in ("none", "") or name not in BEDS: continue
        bed = find_asset(proj, "sfx", "bed-" + name)
        bed = BEDS[name](max(1.0, s1 - s0 + 2.0)) if bed is None else loop_to(bed, int((s1 - s0 + 2.0) * SR))
        bed = bed / max(np.max(np.abs(bed)), 1e-9) * 10 ** (-32 / 20); i0 = int(s0 * SR); k = min(len(bed), n - i0)
        f = min(int(1.5 * SR), k // 2); bed[:f] *= np.linspace(0, 1, f); bed[k - f:k] *= np.linspace(1, 0, f); mix[i0:i0 + k] += bed[:k]
    # sound effects
    placed = 0
    for i, l in enumerate(lines):
        cues = l.get("sfx") or []; cues = [cues] if isinstance(cues, str) else cues
        for c in cues:
            name, _, off = c.partition("@"); at = times[i][0] + (float(off) if off else 0.0)
            x = find_asset(proj, "sfx", name)
            if x is None:
                if name not in SFX: print(f"  unknown sfx {name!r} at line {i + 1}, skipped"); continue
                x = SFX[name]()
            x = x / max(np.max(np.abs(x)), 1e-9) * 10 ** (-14 / 20); i0 = int(at * SR); k = min(len(x), n - i0)
            if k > 0: mix[i0:i0 + k] += x[:k]; placed += 1
    mix = np.clip(mix, -1.5, 1.5); raw = proj / "_mix_raw.wav"; write_wav(raw, mix / max(1.0, np.max(np.abs(mix))))
    out = proj / a.out
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-b:a", "192k", str(out)], check=True); raw.unlink()
    print(f"wrote {out} ({total / 60:.1f} min): {len(sections(lines, times, 'music', total))} music sections ({'placeholder synth: ' + ', '.join(sorted(set(made))) if made else 'your tracks'}), {placed} effects")


if __name__ == "__main__":
    main()
