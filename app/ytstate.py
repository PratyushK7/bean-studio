"""Live YouTube state for every tab: which videos are live, scheduled or private, read from YouTube itself.

register(app, ROOT, cfg) adds GET /api/youtube/videos[?refresh=1]. The Videos, Schedule and Analytics tabs all read this,
so what you see is what is on the channel, not what a spreadsheet says. Refreshed on tab open (at most every 45 s),
every 5 minutes in the background, and right after an upload.
"""
import difflib, json, re, threading, time
from pathlib import Path
from flask import jsonify, request

STATE = {"at": 0.0, "videos": [], "connected": False, "error": None, "last": None}
LOCK = threading.Lock()


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def match_title(title, videos, cutoff=0.8):
    """the YouTube video whose title is (nearly) this title, or None"""
    t = norm(title)
    if not t: return None
    best, score = None, 0
    for v in videos:
        r = difflib.SequenceMatcher(None, t, norm(v["title"])).ratio()
        if r > score: best, score = v, r
    return best if score >= cutoff else None


def badge_for(project_dir):
    """the live state of a project's video on YouTube: by the id the uploader logged, else by title"""
    vids = STATE["videos"]
    if not vids: return None
    up = Path(project_dir) / f"{Path(project_dir).name}-upload.json"
    v = None
    if up.exists():
        try:
            vid = json.loads(up.read_text(encoding="utf-8")).get("id")
            v = next((x for x in vids if x["id"] == vid), None)
        except Exception: pass
    if not v:
        sheet = Path(project_dir) / f"{Path(project_dir).name}-youtube.txt"
        if sheet.exists():
            m = re.search(r"== TITLE ==\s*\n(.+)", sheet.read_text(encoding="utf-8"))
            if m: v = match_title(m.group(1), vids, 0.9)
    return {k: v[k] for k in ("id", "state", "when", "views", "url", "studio")} if v else None


def register(app, ROOT, cfg):
    FILE = ROOT / "data" / "youtube-videos.json"
    if FILE.exists():
        try: STATE.update(json.loads(FILE.read_text(encoding="utf-8")))
        except Exception: pass

    def refresh(force=False):
        if not force and time.time() - STATE["at"] < 45: return
        import ytdata
        with LOCK:
            try:
                vids = ytdata.channel_videos(ROOT)
                STATE.update(videos=vids, at=time.time(), connected=True, error=None, last=time.strftime("%Y-%m-%dT%H:%M:%S"))
                FILE.parent.mkdir(exist_ok=True)
                FILE.write_text(json.dumps({"videos": vids, "last": STATE["last"]}), encoding="utf-8")
            except ytdata.NotConnected:
                STATE.update(connected=False, error=None)
            except Exception as e:
                STATE.update(error=ytdata.friendly(e))

    def loop():
        time.sleep(10)
        while True:
            refresh(force=True)
            time.sleep(300)
    threading.Thread(target=loop, daemon=True).start()

    @app.get("/api/youtube/videos")
    def youtube_videos():
        refresh(force=bool(request.args.get("refresh")))
        return jsonify(videos=STATE["videos"], connected=STATE["connected"], error=STATE["error"], last=STATE["last"])

    return refresh
