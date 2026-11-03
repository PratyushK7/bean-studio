"""Pulls the channel's numbers straight from YouTube: Data API v3 (the video list) + Analytics API v2 (the numbers),
using the same Google sign-in as tools/yt_upload.py. Read-only; nothing here writes to YouTube.

Needs two extra scopes on the token (yt_upload.py auth now asks for them) and the "YouTube Analytics API" enabled
in the Google Cloud project (see tools/yt_upload.md).
"""
import datetime as dt, difflib, json, re
from pathlib import Path

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NEED = {"https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"}
METRICS = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained"


class NotConnected(Exception):
    def __init__(self, missing):
        super().__init__("sign in again to allow analytics access")
        self.missing = missing


def credentials(ROOT):
    """creds with analytics scopes, or raises NotConnected"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    tp = ROOT / "tools" / ".secrets" / "token.json"
    if not tp.exists(): raise NotConnected(sorted(NEED))
    creds = Credentials.from_authorized_user_file(str(tp))          # keeps the scopes it was granted
    missing = sorted(NEED - set(creds.scopes or []))
    if missing: raise NotConnected(missing)
    if not creds.valid:
        creds.refresh(Request()); tp.write_text(creds.to_json())
    return creds


def connected(ROOT):
    try:
        credentials(ROOT); return True, None
    except NotConnected as e:
        return False, e.missing
    except Exception as e:                                           # expired/revoked token
        return False, [str(e)]


def seconds(iso):
    m = re.fullmatch(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m: return None
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def friendly(e):
    s = str(e)
    if "accessNotConfigured" in s or "has not been used" in s:
        return "Enable the YouTube Analytics API (and the YouTube Data API) in your Google Cloud project, then sync again."
    if "invalid_grant" in s or "Token has been expired" in s:
        return "The Google sign-in expired. Use Connect YouTube to sign in again."
    return s[:300]


def planner_types(planner):
    """working title -> video type from bean-planner.xlsx, to label videos the way the schedule did"""
    try:
        import openpyxl
        ws = openpyxl.load_workbook(planner, read_only=True, data_only=True)["Schedule"]
        head = [c.value for c in next(ws.iter_rows(min_row=3, max_row=3))]
        t, y = head.index("Working title"), head.index("Video type")
        return {str(r[t]).strip().lower(): r[y] for r in ws.iter_rows(min_row=4, values_only=True) if r[t] and r[y]}
    except Exception:
        return {}


def project_map(projects_dir):
    """video id / title -> project folder name, from the uploader's logs and the upload sheets"""
    byid, bytitle = {}, {}
    for log in Path(projects_dir).glob("*/*-upload.json"):
        try: byid[json.loads(log.read_text(encoding="utf-8"))["id"]] = log.parent.name
        except Exception: pass
    for sheet in Path(projects_dir).glob("*/*-youtube.txt"):
        m = re.search(r"== TITLE ==\s*\n(.+)", sheet.read_text(encoding="utf-8"))
        if m: bytitle[m.group(1).strip().lower()] = sheet.parent.name
    return byid, bytitle


def slot_for(published, duration_s, slots):
    """which posting slot a video went out in, from its publish time in IST (editable in the UI)"""
    if duration_s and duration_s > 180: return "Long"
    t = published.astimezone(IST)
    mins = t.hour * 60 + t.minute
    best, gap = None, 10 ** 9
    for name, hhmm in slots.items():
        if name == "Long": continue
        h, m = (int(x) for x in hhmm.split(":"))
        d = abs(mins - (h * 60 + m)); d = min(d, 1440 - d)
        if d < gap: best, gap = name, d
    return best if gap <= 120 else None


def sync(ROOT, cfg, existing):
    """returns (rows, info). Numbers are replaced; slot, type, project, notes you set by hand are kept."""
    from googleapiclient.discovery import build
    creds = credentials(ROOT)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    ya = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)

    ch = yt.channels().list(part="contentDetails,statistics,snippet", mine=True).execute()["items"][0]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"],
                                    maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token or len(ids) >= 300: break
    vids = []
    for i in range(0, len(ids), 50):
        vids += yt.videos().list(part="snippet,contentDetails,status", id=",".join(ids[i:i + 50])).execute()["items"]
    vids = [v for v in vids if v["status"]["privacyStatus"] == "public"]      # scheduled/private ones have no numbers yet

    today = dt.date.today().isoformat()
    pub = {v["id"]: dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")) for v in vids}
    nums = {}
    for i in range(0, len(vids), 100):
        batch = [v["id"] for v in vids[i:i + 100]]
        kw = dict(ids="channel==MINE", startDate=min(pub[b] for b in batch).date().isoformat(), endDate=today, dimensions="video",
                  filters="video==" + ",".join(batch), maxResults=200, sort="-views")
        try: r = ya.reports().query(metrics=METRICS, **kw).execute()
        except Exception as e:
            if "engagedViews" not in str(e) and "400" not in str(e): raise
            r = ya.reports().query(metrics=METRICS.replace("engagedViews,", ""), **kw).execute()
        cols = [h["name"] for h in r["columnHeaders"]]
        for row in r.get("rows", []):
            d = dict(zip(cols, row)); nums[d.pop("video")] = d

    byid, bytitle = project_map(cfg["projects_dir"])
    types = planner_types(cfg["planner"])
    old = {r.get("id"): r for r in existing if r.get("id")}
    old_by_title = {(r.get("title") or "").lower(): r for r in existing if not r.get("id")}
    rows, errors = [], []
    for v in sorted(vids, key=lambda v: pub[v["id"]], reverse=True):
        vid, title = v["id"], v["snippet"]["title"]
        n = nums.get(vid, {})
        dur = seconds(v["contentDetails"]["duration"])
        row = old.get(vid) or old_by_title.get(title.lower()) or {}
        views = n.get("views")
        row.update(id=vid, title=title, posted=pub[vid].astimezone(IST).date().isoformat(), duration_s=dur,
                   checked=today, views=views, avg_pct=n.get("averageViewPercentage"), avd_s=n.get("averageViewDuration"),
                   likes=n.get("likes"), comments=n.get("comments"), shares=n.get("shares"), subs=n.get("subscribersGained"),
                   engaged_pct=round(100 * n["engagedViews"] / views, 1) if n.get("engagedViews") is not None and views else None)
        row.setdefault("slot", None); row.setdefault("type", None); row.setdefault("project", None); row.setdefault("notes", None)
        if not row.get("slot"): row["slot"] = slot_for(pub[vid], dur, cfg["slots"])
        if not row.get("project"): row["project"] = byid.get(vid) or bytitle.get(title.lower())
        if not row.get("type"):
            hit = types.get(title.lower()) or next((types[k] for k in difflib.get_close_matches(title.lower(), types, n=1, cutoff=0.8)), None)
            row["type"] = hit
        rows.append(row)

    # retention curve + countries for the videos that have enough views (one query each; the API takes one video at a time)
    for row in [r for r in rows if (r.get("views") or 0) >= 20][:40]:
        vid, start = row["id"], row["posted"]
        try:
            r = ya.reports().query(ids="channel==MINE", startDate=start, endDate=today, metrics="audienceWatchRatio",
                                   dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}").execute()
            pts = sorted((p[0], p[1]) for p in r.get("rows", []))
            if pts and row.get("duration_s"):
                d = row["duration_s"]
                row["retention"] = [[round(p[0] * d, 1), round(100 * p[1], 1)] for p in pts[::max(1, len(pts) // 12)]]
                after = [(pts[i - 1][1] - pts[i][1], pts[i][0]) for i in range(1, len(pts)) if pts[i][0] >= 0.1]
                if after: row["drop_s"] = round(max(after)[1] * d, 1)
        except Exception as e:
            errors.append(f"retention {vid}: {str(e)[:80]}")
        try:
            r = ya.reports().query(ids="channel==MINE", startDate=start, endDate=today, metrics="views", dimensions="country",
                                   filters=f"video=={vid}", sort="-views", maxResults=3).execute()
            tot = row.get("views") or 1
            row["geo"] = ", ".join(f"{c} {round(100 * v / tot)}%" for c, v in r.get("rows", []))
        except Exception as e:
            errors.append(f"geo {vid}: {str(e)[:80]}")
    info = {"videos": len(rows), "channel": ch["snippet"]["title"], "subscribers": ch["statistics"].get("subscriberCount"), "warnings": errors[:5]}
    return rows, info


def channel_videos(ROOT):
    """every upload with its real state: live / scheduled / private / unlisted (Data API, read-only, 1 quota unit per 50 videos)"""
    from googleapiclient.discovery import build
    creds = credentials(ROOT)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"],
                                    maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token or len(ids) >= 400: break
    now = dt.datetime.now(dt.timezone.utc)
    out = []
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,contentDetails,status,statistics", id=",".join(ids[i:i + 50])).execute()["items"]:
            st, sn = v["status"], v["snippet"]
            publish_at = st.get("publishAt")
            parse = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
            if st["privacyStatus"] == "public": state, when = "live", sn["publishedAt"]
            elif publish_at and parse(publish_at) > now: state, when = "scheduled", publish_at
            else: state, when = st["privacyStatus"], sn["publishedAt"]          # private (or unlisted)
            stats = v.get("statistics", {})
            out.append({"id": v["id"], "title": sn["title"], "state": state, "when": parse(when).astimezone(IST).isoformat(timespec="minutes"),
                        "duration_s": seconds(v["contentDetails"]["duration"]), "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)), "comments": int(stats.get("commentCount", 0)),
                        "url": f"https://youtu.be/{v['id']}", "studio": f"https://studio.youtube.com/video/{v['id']}/edit"})
    return sorted(out, key=lambda v: v["when"], reverse=True)
