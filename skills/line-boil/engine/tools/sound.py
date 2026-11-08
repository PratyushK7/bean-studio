"""Cartoon sound effects and a plucked underscore, all synthesised, then mixed under the voiceover.

mix(project) reads audio/vo.wav, cues.json (written by the renderer from the cue() calls) and optional sfx.json
(extra cues [{"t": 3.2, "kind": "pop", "gain": 1}]), and writes audio/mix.wav.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.004, r=None, d=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if d:
        e *= np.exp(-np.arange(n) / SR * d)
    if r:
        nr = min(n, int(r * SR))
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def _glide(f0, f1, d, wave=np.sin, curve=1.0):
    t = _t(d)
    f = f0 + (f1 - f0) * (t / d) ** curve
    ph = 2 * np.pi * np.cumsum(f) / SR
    return wave(ph)


def _tri(ph):
    return 2 / np.pi * np.arcsin(np.sin(ph))


def _noise(d):
    return rng.standard_normal(int(d * SR))


def _lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def _bandsweep(d, f0, f1):
    # cheap swept band of noise: difference of two moving one-pole lowpasses
    x = _noise(d)
    n = len(x)
    out = np.empty(n)
    lo = hi = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * (i / n)
        a1 = np.exp(-2 * np.pi * f * 1.6 / SR)
        a2 = np.exp(-2 * np.pi * f * 0.6 / SR)
        hi = (1 - a1) * x[i] + a1 * hi
        lo = (1 - a2) * x[i] + a2 * lo
        out[i] = hi - lo
    return out / (np.abs(out).max() + 1e-9)


def whoosh():
    d = 0.32
    x = _bandsweep(d, 500, 3200)
    e = np.sin(np.linspace(0, np.pi, len(x))) ** 1.6
    return 0.8 * x * e


def boing():
    d = 0.55
    t = _t(d)
    f = 180 + 160 * np.exp(-t * 6) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return 0.7 * np.sin(ph) * _env(len(t), d=5.5, r=0.05)


def pop():
    d = 0.09
    x = _glide(1100, 260, d, curve=0.5)
    return 0.8 * x * _env(len(x), a=0.001, d=30)


def thud():
    d = 0.28
    x = _glide(120, 45, d, curve=0.6) * _env(int(d * SR), a=0.002, d=14)
    n = _lowpass(_noise(d), 400) * _env(int(d * SR), a=0.001, d=40) * 3
    return 0.9 * (x + n)


def squeak():
    d = 0.14
    x = _glide(1300, 2100, d, wave=_tri, curve=0.7)
    return 0.45 * x * _env(len(x), a=0.005, r=0.03)


def sparkle():
    out = np.zeros(int(0.6 * SR))
    for i, f in enumerate([2637, 3136, 3951, 4699]):
        s = int(i * 0.07 * SR)
        x = np.sin(2 * np.pi * f * _t(0.35)) * _env(int(0.35 * SR), a=0.001, d=14)
        out[s:s + len(x)] += x[:len(out) - s] * 0.28
    return out


def zip_():
    d = 0.16
    x = _glide(300, 1600, d, wave=_tri, curve=1.4)
    return 0.4 * x * _env(len(x), a=0.003, r=0.03)


def plop():
    d = 0.13
    x = _glide(520, 150, d, curve=0.5)
    return 0.7 * x * _env(len(x), a=0.002, d=18)


def tick():
    d = 0.03
    return 0.5 * _lowpass(_noise(d), 3000) * _env(int(d * SR), a=0.0005, d=180)


def slide_up():
    d = 0.42
    x = _glide(320, 1250, d, curve=1.2)
    return 0.45 * x * _env(len(x), a=0.01, r=0.06)


def slide_down():
    d = 0.5
    x = _glide(1200, 260, d, curve=0.8)
    return 0.45 * x * _env(len(x), a=0.01, r=0.08)


def deflate():
    d = 0.45
    x = _lowpass(_noise(d), 900) * 2 + 0.3 * _glide(240, 120, d)
    return 0.45 * x * _env(int(d * SR), a=0.02, r=0.2)


def ding():
    t = _t(1.0)
    x = np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 3136 * t) + 0.2 * np.sin(2 * np.pi * 4704 * t)
    return 0.35 * x * _env(len(t), a=0.001, d=4)


def drum():
    out = np.zeros(int(0.5 * SR))
    for i in range(6):
        s = int(i * 0.05 * SR)
        x = _lowpass(_noise(0.06), 1800) * _env(int(0.06 * SR), a=0.001, d=60) * 2.4
        out[s:s + len(x)] += x
    return out * 0.6


SFX = {'whoosh': whoosh, 'boing': boing, 'pop': pop, 'thud': thud, 'squeak': squeak, 'sparkle': sparkle,
       'zip': zip_, 'plop': plop, 'tick': tick, 'slide_up': slide_up, 'slide_down': slide_down,
       'deflate': deflate, 'ding': ding, 'drum': drum}


def pluck(f, d, bright=1.0):
    t = _t(d)
    x = np.sin(2 * np.pi * f * t) + 0.35 * bright * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 9) \
        + 0.15 * bright * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 16)
    return x * _env(len(t), a=0.003, d=7)


def music(dur, bpm=104, seed=3):
    """a light plucked underscore: I-vi-IV-V in C, bass on 1 and 3, an offbeat arpeggio on top"""
    r = np.random.default_rng(seed)
    beat = 60 / bpm
    out = np.zeros(int((dur + 2) * SR))
    chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    b, t = 0, 0.0
    while t < dur:
        ch = chords[(b // 4) % 4]
        if b % 2 == 0:
            x = pluck(hz(ch[0] - 12), beat * 1.8, 0.5) * 0.55
            s = int(t * SR); out[s:s + len(x)] += x[:len(out) - s]
        for half in (0.5,):
            note = ch[r.integers(0, 3)] + 12 * r.integers(0, 2)
            x = pluck(hz(note), beat * 1.2) * (0.22 + 0.08 * r.random())
            s = int((t + half * beat) * SR); out[s:s + len(x)] += x[:len(out) - s]
        if b % 8 == 7 and r.random() < 0.6:
            x = pluck(hz(ch[2] + 12), beat * 0.8) * 0.18
            s = int((t + 0.75 * beat) * SR); out[s:s + len(x)] += x[:len(out) - s]
        b += 1
        t += beat
    # a little closing chord
    for m in chords[0]:
        x = pluck(hz(m + 12), 1.6) * 0.18
        s = int(max(0, dur - 1.0) * SR); out[s:s + len(x)] += x[:len(out) - s]
    return out[:int(dur * SR)]


# ---------- moods: music that follows the script ----------
# musicMood(t, 'calm') in a shots file starts that mood at second t and ends the one before (a 1 to 1.6 s crossfade). The default, with no
# musicMood calls at all, is the single 'curious' underscore above. 'silent' stops the music (a dramatic pause, a punchline). Every mood is
# scaled to the same loudness, so changing mood changes feeling, not volume.
def _hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def pad(f, d, bright=1.0):
    t = _t(d)
    x = np.sin(2 * np.pi * f * t) + 0.7 * np.sin(2 * np.pi * f * 1.004 * t) + 0.7 * np.sin(2 * np.pi * f * 0.996 * t) \
        + 0.25 * bright * np.sin(2 * np.pi * 2 * f * t)
    return x * _env(len(t), a=min(0.5, d / 3), r=min(0.9, d / 2)) / 2.6


def bell(f, d=2.4):
    t = _t(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4.5) \
        + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 8)
    return x * _env(len(t), a=0.002)


# bpm, pattern, four chords (MIDI), loudness factor. Keys and feelings: C major curious, G major playful, F major calm, D minor serious,
# A minor tense, E minor mystery (open, unresolved), D major triumphant.
MOODS = {
    'curious': dict(bpm=104, pat='pluck', chords=[[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], level=1.0),
    'playful': dict(bpm=128, pat='march', chords=[[55, 59, 62], [62, 66, 69], [52, 55, 59], [60, 64, 67]], level=0.95),
    'upbeat': dict(bpm=132, pat='march', chords=[[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]], level=1.0),
    'calm': dict(bpm=72, pat='pad', chords=[[53, 57, 60], [57, 60, 64], [58, 62, 65], [53, 57, 60]], level=1.0),
    'serious': dict(bpm=66, pat='pad', chords=[[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]], level=1.0, bells=False),
    'tense': dict(bpm=100, pat='pulse', chords=[[45, 48, 52], [41, 45, 48], [50, 53, 57], [52, 56, 59]], level=1.0),
    'mystery': dict(bpm=76, pat='pad', chords=[[52, 55, 59, 62], [48, 52, 55, 59], [50, 53, 57, 60], [51, 55, 58, 62]], level=1.0),
    'triumphant': dict(bpm=112, pat='padarp', chords=[[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]], level=1.0),
}
MOOD_NAMES = list(MOODS) + ['silent']


def _mood_section(mood, dur, seed):
    """one section of a mood, starting on its first beat, `dur` seconds long"""
    m = MOODS[mood]
    if mood == 'curious':
        return music(dur, seed=seed)
    r = np.random.default_rng(seed)
    beat = 60 / m['bpm']
    out = np.zeros(int((dur + 3) * SR))

    def put(x, t):
        s = int(t * SR)
        if 0 <= s < len(out):
            out[s:s + len(x)] += x[:len(out) - s]

    b, t = 0, 0.0
    while t < dur:
        ch = m['chords'][(b // 4) % 4]
        root = ch[0]
        if m['pat'] == 'march':
            if b % 2 == 0:
                put(pluck(_hz(root - 12), beat * 0.9, 0.6) * 0.6, t)
            for k, n in enumerate(ch):                                         # chord stabs on the off-beat
                put(pluck(_hz(n), beat * 0.45, 1.2) * 0.16, t + beat * 0.5 + k * 0.012)
            if b % 4 == 3 and r.random() < 0.7:
                put(pluck(_hz(ch[2] + 12), beat * 0.5) * 0.2, t + beat * 0.75)
        elif m['pat'] in ('pad', 'padarp'):
            if b % 4 == 0:
                for n in ch:
                    put(pad(_hz(n), beat * 4.6), t)
                put(pad(_hz(root - 12), beat * 4.6) * 0.9, t)
            if m['pat'] == 'pad' and m.get('bells', True) and b % 2 == 0 and r.random() < 0.6:
                put(bell(_hz(ch[r.integers(0, len(ch))] + 12 * r.integers(1, 3))) * 0.22, t + beat * 0.5)
            if m['pat'] == 'padarp':
                put(pluck(_hz(ch[b % 3] + 12), beat * 0.9) * 0.22, t)
                put(pluck(_hz(ch[(b + 1) % 3] + 24), beat * 0.6, 0.8) * 0.12, t + beat * 0.5)
        elif m['pat'] == 'pulse':
            if b % 4 == 0:                                                      # a low drone on the root and the fifth
                put(pad(_hz(root - 12), beat * 4.6) * 1.1, t)
                put(pad(_hz(root - 5), beat * 4.6) * 0.7, t)
            for k in range(2):                                                  # quiet ticks on the eighths, an accent on the beat
                put(pluck(_hz(root + 36), 0.09, 0.25) * (0.28 if k == 0 else 0.14), t + k * beat * 0.5)
            if b % 8 == 7 and r.random() < 0.7:
                put(pluck(_hz(root - 12), beat * 1.4, 0.5) * 0.45, t + beat * 0.5)
        b += 1
        t += beat
    return out[:int(dur * SR)]


def _rms(x):
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0


def music_plan(total, plan, seed=3):
    """plan: [{'t': seconds, 'mood': name, 'gain': 1}]; each mood runs until the next entry (or the end)"""
    plan = sorted(plan, key=lambda p: p['t'])
    out = np.zeros(int((total + 3) * SR))
    ref = _rms(music(20, seed=seed))                                            # every mood is brought to this loudness
    for i, p in enumerate(plan):
        mood = p['mood']
        if mood == 'silent':
            continue
        if mood not in MOODS:
            print(f"unknown music mood '{mood}' (use {', '.join(MOOD_NAMES)}) - played as 'curious'")
            mood = 'curious'
        t0 = max(0.0, p['t'])
        t1 = plan[i + 1]['t'] if i + 1 < len(plan) else total
        dur = t1 - t0
        if dur < 0.3:
            continue
        body = _mood_section(mood, dur + 1.6, seed + 11 * i)
        r = _rms(body)
        if r > 0:
            body = body * (ref / r) * MOODS[mood]['level'] * p.get('gain', 1)
        n = len(body)
        fi, fo = min(int(1.0 * SR), n // 3), min(int(1.6 * SR), n // 3)
        body[:fi] *= np.linspace(0, 1, fi)
        body[-fo:] *= np.linspace(1, 0, fo)
        s = int(t0 * SR)
        out[s:s + n] += body[:len(out) - s]
    return out[:int(total * SR)]


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def write_wav(path, x):
    import soundfile as sf
    sf.write(str(path), x.astype(np.float32), SR)


def mix(project, total_seconds, music_gain=0.11, sfx_gain=0.38, fade_out=2.0):
    p = Path(project)
    vo = load(p / 'audio' / 'vo.wav')
    n = int(total_seconds * SR)
    out = np.zeros(n)
    out[:min(n, len(vo))] += vo[:n]
    cues = []
    for f in (p / 'cues.json', p / 'sfx.json'):
        if f.exists():
            cues += json.loads(f.read_text())
    plan = [{'t': c['t'], 'mood': c['kind'][6:], 'gain': c.get('gain', 1)} for c in cues if str(c.get('kind', '')).startswith('music:')]
    cues = [c for c in cues if not str(c.get('kind', '')).startswith('music:')]
    sfx = np.zeros(n)
    cache = {}
    for c in cues:
        k = c['kind']
        if k not in SFX:
            print('unknown sound', k, '- skipped')
            continue
        if k not in cache:
            cache[k] = SFX[k]()
        x = cache[k] * c.get('gain', 1)
        s = int(max(0, c['t']) * SR)
        if s >= n:
            continue
        sfx[s:s + len(x)] += x[:n - s]
    out += sfx * sfx_gain
    if music_gain > 0:
        m = music_plan(total_seconds, plan) if plan else music(total_seconds)
        # duck under the voice
        env = np.abs(np.pad(vo, (0, max(0, n - len(vo))))[:n])
        k = int(0.08 * SR)
        # a moving average: cumulative sums make it linear in the length (np.convolve is quadratic, minutes for 8 minutes of audio)
        cs = np.concatenate(([0.0], np.cumsum(env)))
        idx = np.arange(len(env) + k - 1)
        full = (cs[np.minimum(idx + 1, len(env))] - cs[np.maximum(idx + 1 - k, 0)]) / k
        env = full[(k - 1) // 2:(k - 1) // 2 + len(env)]
        duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1)
        fade = np.ones(n)
        nf = int(min(fade_out, total_seconds / 3) * SR)   # ease out across the breath and the iris (a Short: its 0.4 s tail)
        fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
        fade[-nf:] = np.linspace(1, 0, nf)
        out += m[:n] * duck * fade * music_gain / 0.3
    peak = np.abs(out).max() or 1
    out *= 0.89 / peak
    write_wav(p / 'audio' / 'mix.wav', out)
    return len(cues)
