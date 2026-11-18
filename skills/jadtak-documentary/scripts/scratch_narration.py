"""Free local scratch narration of a Jad Tak script.json (Kokoro on this PC; no API, no cost). A flat voice for judging order,
pacing and runtime, never the final delivery. Writes scratch/scratch-narration.mp3 and scratch/scratch-narration-lines.json
(the per-line timings that make_timeline.py, scriptcheck.py and render_script.py read).

Run with the animation kit's Python (it has kokoro_onnx):
  ~/.claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit/.venv/Scripts/python.exe scratch_narration.py <project folder>"""
import json, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

KIT = Path.home() / ".claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit"
P = Path(sys.argv[1]).resolve()
out = P / "scratch"; out.mkdir(exist_ok=True)
lines = json.loads((P / "script.json").read_text(encoding="utf-8"))["lines"]
k = Kokoro(str(KIT / "models/kokoro-v1.0.onnx"), str(KIT / "models/voices-v1.0.bin"))
SR, voice, speed = 24000, "hm_omega", 1.0
chunks, times, t, t0 = [], [], 0.0, time.time()
for i, l in enumerate(lines):
    spoken = l["text"].replace("।", ".")   # Kokoro reads the danda aloud ("purn viram"); a full stop gives the pause
    a, sr = k.create(spoken, voice=voice, speed=speed, lang="hi"); a = a.astype("float32"); assert sr == SR
    pause = 0.9 if l.get("chapter") and i else (0.45 if l["text"].rstrip().endswith(("?", "।", ".", "!")) else 0.3)
    times.append({"i": i + 1, "start": round(t, 2), "end": round(t + len(a) / SR, 2), "chapter": l.get("chapter", "")})
    chunks += [a, np.zeros(int(SR * pause), dtype="float32")]; t += len(a) / SR + pause
    if (i + 1) % 15 == 0: print(f"{i + 1}/{len(lines)} lines, {t / 60:.1f} min audio, {time.time() - t0:.0f}s elapsed", flush=True)
sf.write(out / "scratch-narration.wav", np.concatenate(chunks), SR)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out / "scratch-narration.wav"), "-b:a", "96k", str(out / "scratch-narration.mp3")], check=True)
(out / "scratch-narration-lines.json").write_text(json.dumps(times, indent=1), encoding="utf-8")
(out / "scratch-narration.wav").unlink()
print("done:", out / "scratch-narration.mp3", f"{t / 60:.1f} min")
for c in [x for x in times if x["chapter"]]: print(f"  {int(c['start'] // 60)}:{int(c['start'] % 60):02d}  {c['chapter']}")
