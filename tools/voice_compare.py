"""Voice comparison for Decoding Vyapaar: the same opening passage read by several voices, to choose by ear.

    python tools/voice_compare.py <project> [--lines 1-8]

Writes <project>/voices/NN-<name>.mp3 and voices/all-voices.mp3 (each voice after a short beep, in the order of voices/order.txt).
  * Sarvam bulbul:v3: several speakers (a few rupees in total); the current speaker also in two finishes (current polish vs soft polish)
  * Microsoft Edge neural Hindi (edge-tts, free): Madhur, Swara
  * Kokoro (local, free): the Hindi voices
Every voice gets the same soft finish so the voice is compared, not the processing. The Sarvam key is read from tools/.secrets and sent only to api.sarvam.ai.
"""
import argparse, asyncio, base64, json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SARVAM = ["aditya", "rahul", "rohan", "amit", "kabir", "varun", "ritu", "priya", "neha", "kavya"]
EDGE = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]
KOKORO = ["hm_omega", "hm_psi", "hf_alpha", "hf_beta"]
CURRENT = ("highpass=f=70,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=2,"
           "acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=7")
SOFT = ("highpass=f=60,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.5:g=-1.5,equalizer=f=7000:t=q:w=1:g=-2,"   # warmer, less presence and hiss
        "acompressor=threshold=-24dB:ratio=2:attack=15:release=200:makeup=2,"
        "aecho=0.8:0.85:22:0.07,loudnorm=I=-16:TP=-1.5:LRA=9")                                                            # a hint of room, a calmer level


def ff(*a): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)


def sarvam(text, speaker, out):
    key = (ROOT / "tools/.secrets/sarvam_key.txt").read_text(encoding="utf-8").strip()
    p = {"text": text, "target_language_code": "hi-IN", "speaker": speaker, "pace": 0.92, "temperature": 0.7, "model": "bulbul:v3"}
    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", json.dumps(p).encode(), {"Content-Type": "application/json", "api-subscription-key": key})
    try: r = json.loads(urllib.request.urlopen(req, timeout=240).read())
    except urllib.error.HTTPError as e: print(f"  sarvam {speaker}: refused ({e.code}) {e.read()[:120]!r}"); return False
    out.write_bytes(b"".join(base64.b64decode(a) for a in r["audios"])); return True


def edge(text, voice, out):
    import edge_tts
    asyncio.run(edge_tts.Communicate(text, voice, rate="-6%").save(str(out))); return True


def kokoro(text, voice, out):
    kit = Path.home() / ".claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit"
    py = kit / ".venv/Scripts/python.exe"
    code = ("import sys,soundfile as sf;from kokoro_onnx import Kokoro;k=Kokoro(sys.argv[1],sys.argv[2]);"
            "a,sr=k.create(open(sys.argv[3],encoding='utf-8').read(),voice=sys.argv[4],speed=0.95,lang='hi');sf.write(sys.argv[5],a,sr)")
    t = out.with_suffix(".txt"); t.write_text(text, encoding="utf-8")
    r = subprocess.run([str(py), "-c", code, str(kit / "models/kokoro-v1.0.onnx"), str(kit / "models/voices-v1.0.bin"), str(t), voice, str(out)], capture_output=True, text=True)
    t.unlink()
    if r.returncode: print(f"  kokoro {voice}: {r.stderr[-160:]}"); return False
    return True


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lines", default="1-8")
    a = ap.parse_args(); proj = Path(a.project); out = proj / "voices"; out.mkdir(exist_ok=True); raw = out / "raw"; raw.mkdir(exist_ok=True)
    L = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    lo, hi = map(int, a.lines.split("-")); text = " ".join(l["hi"] for l in L[lo - 1:hi])
    jobs = [(f"sarvam-{s}", lambda o, s=s: sarvam(text, s, o), ".wav") for s in SARVAM]
    jobs += [(f"edge-{v.split('-')[2].replace('Neural', '').lower()}", lambda o, v=v: edge(text, v, o), ".mp3") for v in EDGE]
    jobs += [(f"kokoro-{v}", lambda o, v=v: kokoro(text, v, o), ".wav") for v in KOKORO]
    made = []
    for name, fn, ext in jobs:
        r = raw / f"{name}{ext}"
        if r.exists() or fn(r): made.append((name, r)); print("  ok", name, flush=True)
    order, parts = [], []
    beep = out / "beep.wav"; ff("-f", "lavfi", "-i", "sine=f=880:d=0.18", "-af", "volume=0.25,afade=t=out:st=0.12:d=0.06", "-ar", "44100", "-ac", "1", str(beep))
    gap = out / "gap.wav"; ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.9", str(gap))
    for k, (name, r) in enumerate([("sarvam-aditya-CURRENT-FINISH", made[0][1])] + made if made and made[0][0] == "sarvam-aditya" else made, 1):
        f = out / f"{k:02d}-{name}.wav"
        ff("-i", str(r), "-af", CURRENT if "CURRENT" in name else SOFT, "-ar", "44100", "-ac", "1", str(f))
        order.append(f"{k:02d}  {name}"); parts += [beep, gap, f, gap]
    (out / "order.txt").write_text("\n".join(order) + "\n", encoding="utf-8")
    lst = out / "list.txt"; lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame", "-q:a", "2", str(out / "all-voices.mp3"))
    print("\n".join(order)); print("wrote", out / "all-voices.mp3")


if __name__ == "__main__":
    main()
