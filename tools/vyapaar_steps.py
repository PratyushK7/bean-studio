"""Decoding Vyapaar steps: one command per button in Bean Studio's Pipeline tab, so the studio and the terminal run exactly the same things.

    python tools/vyapaar_steps.py <project folder> <step>

steps (all free unless marked):
  plan-check      validate visual-plan.json against the bible and the script (coverage, people per shot, graphic numbers)
  prompts         visual-plan.json -> prompts/*.txt, images-index.json, prompts/REFS.md  (stable picture numbers: a re-run never renumbers)
  pictures        make the missing pictures in ChatGPT through BrowserOS neo (your ChatGPT plan; needs neo open), a second pass for glitches,
                  then measure them and build the Gate 1 contact sheets
  check-pictures  measure the pictures, build the contact sheets and the report (Gate 1 evidence)
  upscale         WaveSpeed's local ESRGAN 2x for the APPROVED pictures only
  voice-free      the free local voice (Kokoro): judges the story and pacing, never the delivery
  voice-pro       the channel's paid voice (Sarvam): needs the owner's OK on the cost
  sample          a Gate 2 sample (the hook, a graphics stretch, the ending) with whichever voice matches the current script
  check-sample    Gate 2 QA of sample.mp4 (frozen, black, jumps, loudness, camera limits, grade, text clipping)
  approve-sample  Gate 2: records the approval and the exact render settings
  full            the full video (refuses unless Gate 1 is open and Gate 2 approved a sample with these settings), then its QA

Model policy: none of these needs a model. The judgment (the visual plan, approving pictures, approving the sample) is Opus's or yours.
"""
import json, os, subprocess, sys, time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
PREVIEW = Path.home() / ".claude" / "skills" / "hindi-case-study" / "preview.py"


def run(*cmd, ok_codes=(0,)):
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], env=ENV)
    if r.returncode not in ok_codes: sys.exit(f"step failed (exit {r.returncode}): {cmd[1] if len(cmd) > 1 else cmd[0]}")
    return r.returncode


def jload(p, default=None):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return default


def voice_args(proj):
    """--lines/--voice for the renderer: the paid voice only when it matches THIS script (an old voice.mp3 from an earlier script is never used)"""
    n = len(jload(proj / "script.json", {}).get("lines", []))
    vl = jload(proj / "voice-lines.json")
    if vl and len(vl) == n and (proj / "voice.mp3").exists(): return ["--lines", "voice-lines.json", "--voice", "voice.mp3"], "Sarvam"
    pl = jload(proj / "preview-local-lines.json")
    if pl and len(pl) == n and (proj / "preview-local.mp3").exists(): return ["--lines", "preview-local-lines.json", "--voice", "preview-local.mp3"], "free (Kokoro)"
    sys.exit("make the voice first (the free voice is enough for a first cut): no voice matches the current script")


def write_srt(proj, lines_file):
    """<slug>.srt from the script and the voice's line times (at most 8 words a cue, split evenly); a separate file, never burned in"""
    L = jload(proj / "script.json", {}).get("lines", []); T = jload(proj / lines_file, [])
    if not L or len(L) != len(T): return
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    cues = []
    for l, t in zip(L, T):
        words = l["hi"].split(); n = max(1, -(-len(words) // 8)); size = -(-len(words) // n)
        chunks = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]; total = sum(len(c) for c in chunks); a = t["start"]; span = t["end"] - t["start"]
        for c in chunks: b = a + span * len(c) / total; cues.append((a, b, c)); a = b
    out = proj / f"{proj.name}.srt"
    out.write_text("".join(f"{k}\n{ts(a)} --> {ts(b)}\n{c}\n\n" for k, (a, b, c) in enumerate(cues, 1)), encoding="utf-8")
    print(f"wrote {out.name}: {len(cues)} cues (a separate file: subtitles are never burned in)")


def sample_segments(proj):
    """the hook, the stretch around the nearest graphic to the 55% mark, and the ending: what Gate 2 must see"""
    n = len(jload(proj / "script.json", {}).get("lines", []))
    plan = jload(proj / "visual-plan.json", {})
    g = [s["lines"][0] for s in plan.get("shots", []) if s.get("kind") == "graphic" and s.get("lines")]
    mid = min(g, key=lambda x: abs(x - 0.55 * n)) if g else int(0.55 * n)
    a, b = max(9, mid - 6), min(n - 10, mid + 10)
    return f"1-7,{a}-{b},{max(b + 1, n - 7)}-{n}"


def archive(proj, name):
    """back up a finished render before a new one takes its name"""
    f = proj / name
    if f.exists():
        stamp = time.strftime("%Y%m%d-%H%M", time.localtime(f.stat().st_mtime))
        f.rename(proj / f"{f.stem}-prev-{stamp}{f.suffix}")
        pj = proj / f"{f.stem}-plan.json"
        if pj.exists(): pj.rename(proj / f"{f.stem}-prev-{stamp}-plan.json")
        print(f"kept the earlier {name} as {f.stem}-prev-{stamp}{f.suffix}")


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    proj, step = Path(sys.argv[1]).resolve(), sys.argv[2]
    t = lambda x: str(TOOLS / x)
    if step == "plan-check": run(PY, t("vyapaar_visual.py"), "validate", proj)
    elif step == "prompts": run(PY, t("vyapaar_prompts.py"), proj)
    elif step == "check-pictures":
        for c in ("analyze", "sheets", "report"): run(PY, t("vyapaar_review.py"), proj, c)
    elif step == "pictures":
        run(PY, t("chatgpt_runner.py"), proj)
        run(PY, t("chatgpt_runner.py"), proj)                      # the second pass retries glitches ("send button missing"); finished pictures are skipped
        for c in ("analyze", "sheets", "report"): run(PY, t("vyapaar_review.py"), proj, c)
    elif step == "upscale": run(PY, t("vyapaar_review.py"), proj, "upscale")
    elif step == "voice-free":
        run(PY, PREVIEW, proj); write_srt(proj, "preview-local-lines.json")
    elif step == "voice-pro": run(PY, t("vyapaar_voice.py"), proj)
    elif step == "sample":
        va, kind = voice_args(proj); seg = sample_segments(proj); print(f"sample of lines {seg} with the {kind} voice", flush=True)
        run(PY, t("vyapaar_render.py"), proj, "sample", "--segments", seg, *va)
    elif step == "check-sample": run(PY, t("vyapaar_qa.py"), proj, "sample.mp4")
    elif step == "approve-sample": run(PY, t("vyapaar_qa.py"), proj, "approve", "sample.mp4")
    elif step == "full":
        va, kind = voice_args(proj); print(f"full video with the {kind} voice", flush=True)
        archive(proj, "video.mp4")
        run(PY, t("vyapaar_render.py"), proj, "full", *va)
        if kind != "Sarvam": write_srt(proj, "preview-local-lines.json")
        run(PY, t("vyapaar_qa.py"), proj, "video.mp4")
    else: sys.exit(f"unknown step {step!r}\n\n{__doc__}")


if __name__ == "__main__":
    main()
