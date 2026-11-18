"""YouTube competitor research for a new video: find the top videos on a topic, then save what each one actually says.

    python tools/yt_research.py search "<query>" ["<query 2>" ...] [--n 10]
        candidates from YouTube search: views | channel | title | duration | id (pick the top five from several queries)
    python tools/yt_research.py fetch <project> <id or url> [...] [--comments 30]
        for each video: title, channel, views, upload date, duration, link, chapters, description, the transcript
        (manual subtitles first, then auto captions; Hindi, then English) and the top comments, saved to
        <project>/research/competitors/<id>.md, and the table to <project>/research/competitors/competitors.json

Read-only and free (yt-dlp, no API key). It records only what YouTube returned, with the time it was fetched: a missing
transcript or comment list is written down as missing, with the reason, never filled in. If YouTube asks to sign in or to
prove you are not a bot, it stops and says so; it never works around that.
"""
import json, re, sys, time
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp is missing: pip install yt-dlp")

LANGS = ["hi", "hi-IN", "hi-orig", "en", "en-IN", "en-orig", "en-US"]
BLOCKED = re.compile(r"sign in to confirm|not a bot|captcha|429|too many requests", re.I)


def ydl(**opt):
    return yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noprogress": True, "skip_download": True, **opt})


def vid(x):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", x)
    return m.group(1) if m else x if re.fullmatch(r"[\w-]{11}", x) else sys.exit(f"not a YouTube id or link: {x}")


def search(queries, n):
    seen = {}
    with ydl(extract_flat=True) as y:
        for q in queries:
            for e in (y.extract_info(f"ytsearch{n}:{q}", download=False).get("entries") or []):
                if e and e.get("id") and e["id"] not in seen: seen[e["id"]] = e
    rows = sorted(seen.values(), key=lambda e: -(e.get("view_count") or 0))
    for e in rows:
        d = e.get("duration")
        print(f"{e.get('view_count') or '?':>10} | {e.get('channel') or e.get('uploader') or '?'} | {e.get('title')} | "
              f"{f'{int(d) // 60}:{int(d) % 60:02d}' if d else '?'} | {e['id']}")
    print(f"\n{len(rows)} videos from {len(queries)} queries. Views are as YouTube search showed them just now.")


def caption_text(url, info, tmp):
    """(text, which): one track, written by yt-dlp's own subtitle downloader (direct caption requests get rate-limited).
    Manual subtitles first (Hindi, then English), else the auto captions in the video's own language."""
    man, auto = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    orig = (info.get("language") or "hi").split("-")[0]
    pick = next((("manual", l) for l in LANGS if l in man), None) or            next((("auto", l) for l in (f"{orig}-orig", orig, "hi", "en") if l in auto), None)
    if not pick: return None, "no Hindi or English subtitles or captions on this video"
    kind, lang = pick
    tmp.mkdir(parents=True, exist_ok=True)
    with ydl(writesubtitles=kind == "manual", writeautomaticsub=kind == "auto", subtitleslangs=[lang], subtitlesformat="json3",
             outtmpl=str(tmp / "%(id)s.%(ext)s")) as y:
        y.download([url])
    f = next(iter(tmp.glob(f"{info['id']}*.json3")), None)
    if not f: return None, f"the {kind} {lang} track did not download"
    data = json.loads(f.read_text(encoding="utf-8")); f.unlink()
    parts = ["".join(seg.get("utf8", "") for seg in ev.get("segs") or []) for ev in data.get("events") or []]
    text = re.sub(r"\s+", " ", " ".join(x for x in parts if x.strip())).strip()
    return (text, f"{kind} {lang}") if text else (None, f"the {kind} {lang} track was empty")


def fetch(proj, ids, n_comments):
    out = Path(proj) / "research" / "competitors"; out.mkdir(parents=True, exist_ok=True)
    table_f = out / "competitors.json"
    table = json.loads(table_f.read_text(encoding="utf-8")) if table_f.exists() else {}
    for v in ids:
        url = f"https://www.youtube.com/watch?v={v}"
        try:
            with ydl(getcomments=n_comments > 0, extractor_args={"youtube": {"max_comments": [str(n_comments)], "comment_sort": ["top"]}}) as y:
                info = y.extract_info(url, download=False)
        except Exception as e:
            msg = str(e)
            if BLOCKED.search(msg): sys.exit(f"YouTube is asking for a sign-in or bot check ({msg[:160]}). Stopped; nothing was worked around.")
            print(f"{v}: could not read the video ({msg[:200]})"); continue
        try: text, which = caption_text(url, info, out / "_subs")
        except Exception as e: text, which = None, f"captions could not be fetched ({str(e)[:120]})"
        up = info.get("upload_date") or ""
        row = {"id": v, "link": url, "title": info.get("title"), "channel": info.get("channel") or info.get("uploader"),
               "views": info.get("view_count"), "likes": info.get("like_count"),
               "uploaded": f"{up[:4]}-{up[4:6]}-{up[6:]}" if len(up) == 8 else None, "duration": info.get("duration_string"),
               "transcript": which if text else f"missing: {which}", "fetched": time.strftime("%Y-%m-%d %H:%M")}
        table[v] = row
        chapters = info.get("chapters") or []
        cm = sorted(info.get("comments") or [], key=lambda c: -(c.get("like_count") or 0))[:n_comments]
        md = [f"# {row['title']}", "", f"- channel: {row['channel']}", f"- link: {url}", f"- views: {row['views']} · likes: {row['likes']}",
              f"- uploaded: {row['uploaded']} · duration: {row['duration']}", f"- fetched: {row['fetched']} (numbers are as of this time)", f"- transcript: {row['transcript']}", "",
              "## Chapters", ""] + ([f"- {int(c['start_time']) // 60}:{int(c['start_time']) % 60:02d} {c.get('title')}" for c in chapters] or ["(none)"]) + \
             ["", "## Description", "", (info.get("description") or "(none)").strip(), "", "## Transcript", "", text or f"(missing: {which})", "",
              "## Top comments", ""] + ([f"- ({c.get('like_count') or 0} likes) {re.sub(r'\s+', ' ', c.get('text') or '')}" for c in cm] or ["(none fetched)"])
        (out / f"{v}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"{v}: {row['views']} views · {row['channel']} · {row['title']} · transcript: {row['transcript']} · {len(cm)} comments")
    table_f.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nsaved to {out}")


def main():
    a = sys.argv[1:]
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    num = lambda flag, d: int(a[a.index(flag) + 1]) if flag in a else d
    args = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    if len(args) >= 2 and args[0] == "search": search(args[1:], num("--n", 10))
    elif len(args) >= 3 and args[0] == "fetch": fetch(args[1], [vid(x) for x in args[2:]], num("--comments", 30))
    else: sys.exit(__doc__)


if __name__ == "__main__":
    main()
