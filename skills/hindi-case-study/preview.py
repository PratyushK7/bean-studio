"""Free local listen of a script (Kokoro on this PC: no API, no cost):  python preview.py <project> [voice] [speed]   |   python preview.py <project> --cast-sample
Writes <project>/preview-local.mp3 (whole script; short pauses between lines, longer at chapter starts), preview-local-hook.mp3 (the first 45 s) and
preview-local-lines.json (each line's times, and who speaks in it), then prints the chapter times. Kokoro is flat and has no emotion: use it to judge the
story, the order and the pacing, never the delivery (the channel voice is Sarvam, a paid step). Re-runs itself with the animation kit's Python, which has
kokoro_onnx; about 10 minutes for a 13-minute script.

People speak in their own voices: a script line marked with `say` is read as the narrator's words and the person's words (tools/vyapaar_cast.py), each with the
Kokoro voice, speed and pitch from voice-cast.json (pitch above 1 is higher and younger, below 1 lower and older), levelled to the same loudness.
--cast-sample writes <project>/voices/cast-free.mp3: one real line per person, to choose voices by ear."""
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
sys.path.insert(0, str(Path(os.environ.get("VYAPAAR_TOOLS", r"C:\Users\praty\youtube\tools"))))
import vyapaar_cast as vc

args = [a for a in sys.argv[1:] if not a.startswith("--")]
proj = Path(args[0]); narr_voice = args[1] if len(args) > 1 else None; narr_speed = float(args[2]) if len(args) > 2 else None
lines = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]; cast = vc.load(proj)
bad = [x for x in vc.validate(proj) if x.startswith("line ")]
if bad: sys.exit("the dialogue marks do not match the script:\n  " + "\n  ".join(bad))
k = Kokoro(str(KIT / "models/kokoro-v1.0.onnx"), str(KIT / "models/voices-v1.0.bin"))
SR, TARGET_RMS = 24000, 0.07


def speak(who, text):
    cfg = vc.kokoro_cfg(cast, who)
    voice = (narr_voice if who == vc.NARRATOR and narr_voice else cfg.get("voice")) or "hm_omega"
    speed = (narr_speed if who == vc.NARRATOR and narr_speed else cfg.get("speed")) or 1.0
    a, sr = k.create(text, voice=voice, speed=speed, lang="hi"); a = a.astype("float32")
    f = float(cfg.get("pitch", 1.0))
    if abs(f - 1.0) > 0.01:                                  # a person's voice from the same speaker: pitch the whole thing up or down, then restore the tempo
        r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-af", f"asetrate={int(sr * f)},aresample={sr},atempo={1 / f:.4f}", "-f", "f32le", "-"],
                           input=a.tobytes(), capture_output=True)
        if r.stdout: a = np.frombuffer(r.stdout, dtype=np.float32).copy()
    rms = float(np.sqrt((a ** 2).mean())) or 1e-6
    return np.clip(a * (TARGET_RMS / rms), -0.98, 0.98).astype("float32"), sr


if "--cast-sample" in sys.argv:
    first = {}
    for l in lines:
        for who, text in vc.parts(l): first.setdefault(who, text)
    out, gap = [], None
    for who in [vc.NARRATOR] + [w for w in first if w != vc.NARRATOR]:
        text = first.get(who, "")
        if not text: continue
        a, sr = speak(who, text[:170].rsplit(" ", 1)[0] if len(text) > 170 else text); gap = np.zeros(int(sr * 1.0), dtype="float32"); out += [a, gap]
        print(f"  {who}: {vc.kokoro_cfg(cast, who)}", flush=True)
    (proj / "voices").mkdir(exist_ok=True); wav = proj / "voices" / "cast-free.wav"; sf.write(wav, np.concatenate(out), SR)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-b:a", "128k", str(wav.with_suffix(".mp3"))], check=True); wav.unlink()
    sys.exit(print(f"wrote {wav.with_suffix('.mp3')}"))

parts, t, marks, t0, sr, spans = [], 0.0, [], time.time(), SR, []
for i, l in enumerate(lines):
    start = t; pieces = vc.parts(l); who_here = []
    for n, (who, text) in enumerate(pieces):
        a, sr = speak(who, text); who_here.append(who)
        if n: parts.append(np.zeros(int(sr * 0.2), dtype="float32")); t += 0.2          # a beat between the narrator's tag and the person's words
        parts.append(a); t += len(a) / sr
    pause = 0.9 if l.get("chapter") and i else (0.45 if l["hi"].rstrip().endswith(("?", "।", ".", "!")) else 0.3)
    if l.get("chapter"): marks.append((start, l["chapter"]))
    spans.append({"i": i, "start": round(start, 3), "end": round(t, 3), "chapter": l.get("chapter"), "who": sorted(set(who_here))})
    parts.append(np.zeros(int(sr * pause), dtype="float32")); t += pause
    if i % 40 == 0: print(f"  {i}/{len(lines)} lines, {t:.0f} s of audio, {time.time() - t0:.0f} s", flush=True)
audio = np.concatenate(parts)
for name, seg in (("preview-local", audio), ("preview-local-hook", audio[: int(sr * 45)])):
    wav = proj / f"{name}.wav"; sf.write(wav, seg, sr)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "128k", str(proj / f"{name}.mp3")], check=True)
    wav.unlink()
json.dump(spans, open(proj / "preview-local-lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)   # per-line timings for the renderer, the graphics and the mix
print(f"wrote {proj / 'preview-local.mp3'} ({len(audio) / sr / 60:.1f} min) and preview-local-hook.mp3")
for s, c in marks: print(f"  {int(s // 60):02d}:{int(s % 60):02d}  {c}")
