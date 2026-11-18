"""Turn a YouTube json3 caption file into a timestamped transcript (one line per caption event, [mm:ss] at its start),
so a reference video can be studied and cited to the second. Also fetches the captions when given a video URL or id.
Free (yt-dlp, no API). Usage:
  python timed_transcript.py <video-url-or-id> <out-dir>        # fetch captions (manual Hindi first, else auto) and convert
  python timed_transcript.py <file.json3> <out.md>              # convert a caption file you already have
Output lines look like:  [03:41] यह सुनकर महाराज जी अचानक अपने स्थान से उठ गये।"""
import json, re, subprocess, sys
from pathlib import Path


def ts(ms):
    s = int(ms // 1000); h, m = divmod(s, 3600); m, s = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def convert(src, title=""):
    d = json.loads(Path(src).read_text(encoding="utf-8"))
    rows = []
    for e in d.get("events", []):
        if "segs" not in e: continue
        t = re.sub(r"\s+", " ", "".join(s.get("utf8", "") for s in e["segs"])).strip()
        if t: rows.append((e.get("tStartMs", 0), t))
    # auto captions repeat rolling lines; keep an event only if it adds text
    out, last = [], ""
    for ms, t in rows:
        if t == last or (last and t in last): continue
        out.append(f"[{ts(ms)}] {t}"); last = t
    head = [f"# {title}", ""] if title else []
    return "\n".join(head + out) + "\n"


def fetch(vid, outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    url = vid if vid.startswith("http") else f"https://www.youtube.com/watch?v={vid}"
    meta = json.loads(subprocess.run(["yt-dlp", "-J", "--skip-download", url], capture_output=True, text=True, encoding="utf-8").stdout)
    for flag in ("--write-subs", "--write-auto-subs"):
        subprocess.run(["yt-dlp", "--skip-download", flag, "--sub-langs", "hi,hi-orig,en", "--sub-format", "json3", "-o", str(outdir / "%(id)s.%(ext)s"), url], capture_output=True)
        files = sorted(outdir.glob(f"{meta['id']}*.json3"))
        if files: break
    if not files: sys.exit("no Hindi or English captions on this video")
    md = outdir / f"{meta['id']}.timed.md"
    head = f"{meta['title']}\n\n- channel: {meta.get('channel')}\n- link: {url}\n- duration: {meta.get('duration_string')}\n- views: {meta.get('view_count')}\n- captions: {files[0].name} ({'manual' if flag == '--write-subs' else 'auto'})"
    md.write_text(convert(files[0], head), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    if a.endswith(".json3"): Path(b).write_text(convert(a), encoding="utf-8"); print(b)
    else: fetch(a, b)
