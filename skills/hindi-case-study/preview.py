"""Free local listen of a script (Kokoro on this PC: no API, no cost):  python preview.py <project> [voice] [speed]
Writes <project>/preview-local.mp3 (whole script; short pauses between lines, longer at chapter starts) and preview-local-hook.mp3
(the first 45 s), then prints the chapter times. Kokoro is flat and has no emotion: use it to judge the story, the order and the
pacing, never the delivery (the channel voice is Sarvam, a paid step). Re-runs itself with the animation kit's Python, which has
kokoro_onnx; about 10 minutes for a 13-minute script."""
import json, os, subprocess, sys, time
from pathlib import Path
KIT = Path.home() / ".claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit"
PY = KIT / ".venv/Scripts/python.exe"
try:
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
except ImportError:
    if PY.exists() and Path(sys.executable).resolve() != PY.resolve():
        sys.exit(subprocess.run([str(PY), __file__, *sys.argv[1:]]).returncode)
    sys.exit(f"needs kokoro_onnx: install the animation kit ({KIT}) or pip install kokoro-onnx soundfile numpy")

proj = Path(sys.argv[1]); voice = sys.argv[2] if len(sys.argv) > 2 else "hm_omega"; speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
lines = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
k = Kokoro(str(KIT / "models/kokoro-v1.0.onnx"), str(KIT / "models/voices-v1.0.bin"))
parts, t, marks, t0, sr = [], 0.0, [], time.time(), 24000
for i, l in enumerate(lines):
    a, sr = k.create(l["hi"], voice=voice, speed=speed, lang="hi")
    pause = 0.9 if l.get("chapter") and i else (0.45 if l["hi"].rstrip().endswith(("?", "।", ".", "!")) else 0.3)
    if l.get("chapter"): marks.append((t, l["chapter"]))
    parts += [a, np.zeros(int(sr * pause), dtype=a.dtype)]; t += len(a) / sr + pause
    if i % 40 == 0: print(f"  {i}/{len(lines)} lines, {t:.0f} s of audio, {time.time() - t0:.0f} s", flush=True)
audio = np.concatenate(parts)
for name, seg in (("preview-local", audio), ("preview-local-hook", audio[: int(sr * 45)])):
    wav = proj / f"{name}.wav"; sf.write(wav, seg, sr)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "128k", str(proj / f"{name}.mp3")], check=True)
    wav.unlink()
print(f"wrote {proj / 'preview-local.mp3'} ({len(audio) / sr / 60:.1f} min) and preview-local-hook.mp3")
for s, c in marks: print(f"  {int(s // 60):02d}:{int(s % 60):02d}  {c}")
