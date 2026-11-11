"""Decoding Vyapaar voice step: script.json -> voice.mp3 (polished, -14 LUFS), voice-lines.json (start/end of every script line) and <slug>.srt.

    python tools/vyapaar_voice.py <project folder>

The locked voice (chosen by ear on 2026-11-10, test "T3"): Sarvam bulbul:v3, speaker aditya, pace 0.92, temperature 0.7.
The script is read in chunks of a few lines (so a sentence keeps the tone of the one before it), a chunk never crosses a chapter.
Sarvam returns audio without word times, so each line's time is found by matching the line lengths to the silences in the chunk.
Needs only ffmpeg and the standard library. The key is read from tools/.secrets/sarvam_key.txt and sent only to api.sarvam.ai.
"""
import base64, json, re, subprocess, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = {"speaker": "aditya", "pace": 0.92, "temperature": 0.7, "model": "bulbul:v3"}
CHUNK_CHARS = 800            # aim for this many characters per request (Sarvam takes more; shorter keeps the line matching reliable)
GAP, CHAPTER_GAP = 0.7, 1.2  # seconds between chunks (a chunk ends on a sentence); between chapters
POLISH = ("highpass=f=70,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=2,"
          "acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=7")


def ff(*args, **kw):
    return subprocess.run(["ffmpeg", "-hide_banner", "-y", *args], capture_output=True, **kw)


def duration(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)


def speak(text):
    key = (ROOT / "tools/.secrets/sarvam_key.txt").read_text(encoding="utf-8").strip()
    payload = {"text": text, "target_language_code": "hi-IN", **VOICE}
    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", json.dumps(payload).encode(),
                                 {"Content-Type": "application/json", "api-subscription-key": key})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=240).read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Sarvam refused the request ({e.code}): {e.read()[:300].decode('utf-8', 'replace')}")
    return b"".join(base64.b64decode(a) for a in r["audios"])


def silences(wav):
    """[(start, end)] of pauses of at least 0.15 s"""
    err = ff("-i", str(wav), "-af", "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-", text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(s, e))


def boundaries(lines, total, sil):
    """times where each line ends inside one chunk: the silences that best fit the lines' relative lengths (dynamic programming)"""
    n = len(lines)
    if n == 1: return [total]
    w = [max(1, len(re.sub(r"\s", "", l))) for l in lines]
    want = [sum(w[:i + 1]) / sum(w) * total for i in range(n - 1)]            # expected end of each line but the last
    cand = [(a + b) / 2 for a, b in sil if a > 0.3 and b < total - 0.1]         # a silence's middle
    if len(cand) < n - 1: return want + [total]                                # too few pauses: fall back to the proportional guess
    INF = 1e9
    best = [[INF] * len(cand) for _ in range(n - 1)]; prev = [[-1] * len(cand) for _ in range(n - 1)]
    for j, c in enumerate(cand): best[0][j] = abs(c - want[0])
    for i in range(1, n - 1):
        for j, c in enumerate(cand):
            for k in range(j):
                v = best[i - 1][k] + abs(c - want[i])
                if v < best[i][j]: best[i][j], prev[i][j] = v, k
    j = min(range(len(cand)), key=lambda j: best[n - 2][j]); out = []
    for i in range(n - 2, -1, -1): out.append(cand[j]); j = prev[i][j]
    out = out[::-1]
    tol = max(0.8, 0.08 * total)                                       # a pause far from where the line lengths say is a comma or a breath, not a sentence end
    out = [c if abs(c - w_) <= tol else w_ for c, w_ in zip(out, want)]
    for i in range(1, len(out)): out[i] = max(out[i], out[i - 1] + 0.3)  # boundaries stay in order
    return out + [total]


def srt_time(x):
    return "%02d:%02d:%02d,%03d" % (int(x // 3600), int(x % 3600 // 60), int(x % 60), round((x % 1) * 1000) % 1000)


def main():
    proj = Path(sys.argv[1]).resolve()
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    lines = script["lines"]
    # chunks: consecutive lines, never across a chapter start, about CHUNK_CHARS long
    chunks, cur = [], []
    for i, l in enumerate(lines):
        if cur and (l.get("chapter") or sum(len(lines[j]["hi"]) for j in cur) + len(l["hi"]) > CHUNK_CHARS):
            chunks.append(cur); cur = []
        cur.append(i)
    if cur: chunks.append(cur)
    print(f"{len(lines)} lines in {len(chunks)} chunks; voice {VOICE['speaker']} pace {VOICE['pace']} temperature {VOICE['temperature']}", flush=True)

    tmp = Path(tempfile.mkdtemp(prefix="vyapaar_voice_"))
    parts, times, t = [], [None] * len(lines), 0.0
    for ci, idx in enumerate(chunks):
        wav = tmp / f"c{ci:03d}.wav"
        wav.write_bytes(speak(" ".join(lines[i]["hi"] for i in idx)))
        d = duration(wav)
        ends = boundaries([lines[i]["hi"] for i in idx], d, silences(wav))
        start = 0.0
        for i, e in zip(idx, ends): times[i] = (t + start, t + e); start = e
        parts.append(wav); t += d
        gap = CHAPTER_GAP if ci + 1 < len(chunks) and lines[chunks[ci + 1][0]].get("chapter") else GAP
        if ci + 1 < len(chunks):
            sil = tmp / f"g{ci:03d}.wav"; ff("-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(gap), str(sil)); parts.append(sil); t += gap
        print(f"  chunk {ci + 1}/{len(chunks)}: {d:.1f} s", flush=True)

    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    raw = tmp / "raw.wav"; ff("-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "24000", "-ac", "1", str(raw))
    r = ff("-i", str(raw), "-af", POLISH, "-c:a", "libmp3lame", "-q:a", "2", str(proj / "voice.mp3"), text=True)
    if r.returncode: sys.exit("ffmpeg polish failed: " + r.stderr[-300:])
    # loudnorm only trims or lifts a little: the polished file has the same timeline as raw.wav
    json.dump([{"i": i, "start": round(a, 3), "end": round(b, 3), "chapter": lines[i].get("chapter")} for i, (a, b) in enumerate(times)],
              open(proj / "voice-lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # the .srt: each line split into cues of at most 9 words (never burned into the video), times shared by length
    cues = []
    for i, (a, b) in enumerate(times):
        groups, g = [], []
        for w in lines[i]["hi"].split():                       # break after a comma once a cue has 3+ words, and never past 9 words
            g.append(w)
            if len(g) >= 9 or (w.endswith(",") and len(g) >= 3): groups.append(g); g = []
        if g:
            if groups and len(g) <= 2: groups[-1] += g         # no cue of one or two words at the end
            else: groups.append(g)
        total = sum(len("".join(g)) for g in groups); pos = a
        for g in groups:
            span = (b - a) * len("".join(g)) / total; cues.append((pos, pos + span, " ".join(g))); pos += span
    (proj / f"{proj.name}.srt").write_text("".join(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n" for n, (a, b, txt) in enumerate(cues, 1)), encoding="utf-8")
    print(f"done: voice.mp3 {duration(proj / 'voice.mp3') / 60:.1f} min, {len(cues)} subtitle cues -> {proj / (proj.name + '.srt')}")


if __name__ == "__main__":
    main()
