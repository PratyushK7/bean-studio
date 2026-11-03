"""Analytics for Bean Studio: your numbers in (by hand, Studio CSV export or the planner), the agent's report out.

register(app, ROOT, cfg, start_job) adds /api/analytics*, /api/reports* to the Flask app.
Data lives in data/analytics.json, reports in reports/analysis-<date>.md (both tracked in git, both private).
"""
import csv, datetime as dt, io, json, re, threading, time
from pathlib import Path
from flask import abort, jsonify, request

FIELDS = ["id", "project", "title", "posted", "duration_s", "slot", "type", "checked", "views", "engaged_pct", "viewed_pct", "avg_pct",
          "avd_s", "likes", "comments", "shares", "subs", "drop_s", "retention", "drop_note", "geo", "notes"]
NUMERIC = ("views", "engaged_pct", "viewed_pct", "avg_pct", "avd_s", "likes", "comments", "shares", "subs", "drop_s", "duration_s")

# YouTube Studio export headers -> our fields (matched by prefix, case-insensitive)
CSV_MAP = {
    "title": ("video title", "title", "content"),
    "views": ("views",),
    "avg_pct": ("average percentage viewed", "avg % viewed", "average view percentage"),
    "avd_s": ("average view duration", "avg view duration"),
    "likes": ("likes",),
    "comments": ("comments added", "comments"),
    "shares": ("shares",),
    "subs": ("subscribers gained", "subscribers"),
    "viewed_pct": ("viewed vs swiped away", "stayed to watch", "viewed"),
    "posted": ("video publish time", "publish time", "published", "date"),
}


def num(v):
    if v in (None, ""): return None
    try:
        s = str(v).replace(",", "").replace("%", "").strip()
        return float(s) if s not in ("", "-", "—") else None
    except ValueError:
        return None


def duration(v):
    s = str(v).strip()
    if ":" in s:
        return sum((num(x) or 0) * 60 ** i for i, x in enumerate(reversed(s.split(":"))))
    return num(s)


def summarize(rows):
    """per-slot and per-type averages, with the sample size next to each"""
    def agg(key):
        groups = {}
        for r in rows:
            if r.get("views") is None or not r.get(key): continue
            groups.setdefault(r[key], []).append(r)
        out = []
        for k, rs in groups.items():
            def avg(f):
                vals = [x[f] for x in rs if x.get(f) is not None]
                return round(sum(vals) / len(vals), 1) if vals else None
            out.append({key: k, "videos": len(rs), "avg_views": avg("views"), "avg_engaged_pct": avg("engaged_pct"),
                        "avg_viewed_pct": avg("viewed_pct"), "avg_pct_watched": avg("avg_pct"), "avg_subs": avg("subs")})
        return sorted(out, key=lambda x: -(x["avg_views"] or 0))
    return {"by_slot": agg("slot"), "by_type": agg("type")}


def register(app, ROOT, cfg, start_job):
    DATA, REPORTS = ROOT / "data", ROOT / "reports"
    FILE = DATA / "analytics.json"

    def load():
        return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else []

    def save(rows):
        DATA.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    META = DATA / "analytics-meta.json"
    state = {"syncing": False, "error": None, "last_sync": None, "info": None}
    if META.exists():
        try: state.update(json.loads(META.read_text(encoding="utf-8")))
        except Exception: pass
    lock = threading.Lock()

    def do_sync():
        """pull everything from YouTube; keeps the slot/type/project/notes you set by hand"""
        import ytdata
        with lock:
            state["syncing"] = True
            try:
                rows, info = ytdata.sync(ROOT, cfg(), load())
                save(rows)
                state.update(error=None, last_sync=dt.datetime.now().isoformat(timespec="seconds"), info=info)
            except ytdata.NotConnected:
                state["error"] = "not connected"
            except Exception as e:
                state["error"] = ytdata.friendly(e)
            finally:
                state["syncing"] = False
                DATA.mkdir(exist_ok=True)
                META.write_text(json.dumps({k: state[k] for k in ("last_sync", "info")}), encoding="utf-8")
        return state["error"] is None

    def auto_sync():
        import ytdata
        time.sleep(15)
        while True:
            hours = float(cfg().get("analytics_sync_hours", 6))
            last = dt.datetime.fromisoformat(state["last_sync"]) if state.get("last_sync") else None
            if hours > 0 and (last is None or (dt.datetime.now() - last).total_seconds() > hours * 3600) and ytdata.connected(ROOT)[0]:
                do_sync()
            time.sleep(300)
    threading.Thread(target=auto_sync, daemon=True).start()

    def status():
        import ytdata
        ok, missing = ytdata.connected(ROOT)
        return {"connected": ok, "missing": missing, "syncing": state["syncing"], "error": state["error"],
                "last_sync": state["last_sync"], "info": state["info"], "auto_hours": cfg().get("analytics_sync_hours", 6)}

    @app.post("/api/analytics/sync")
    def analytics_sync():
        ok = do_sync()
        rows = load()
        return jsonify(ok=ok, rows=rows, summary=summarize(rows), status=status())

    @app.get("/api/analytics")
    def analytics_get():
        rows = load()
        return jsonify(rows=rows, fields=FIELDS, summary=summarize(rows), status=status())

    @app.put("/api/analytics")
    def analytics_put():
        clean = []
        for r in request.json.get("rows", []):
            c = {k: r.get(k) for k in FIELDS}
            for k in NUMERIC: c[k] = num(c[k])
            if c["title"] or c["project"]: clean.append(c)
        save(clean)
        return jsonify(ok=True, n=len(clean))

    @app.post("/api/analytics/import-csv")
    def analytics_csv():
        rdr = csv.DictReader(io.StringIO(request.json.get("text", "").lstrip("﻿")))
        if not rdr.fieldnames: abort(400, "no header row")
        low = {h: h.strip().lower() for h in rdr.fieldnames}
        pick = {f: next((h for h, l in low.items() if any(l.startswith(a) for a in alts)), None) for f, alts in CSV_MAP.items()}
        if not pick["title"] or not pick["views"]: abort(400, "need at least a title column and a Views column")
        have = {(r.get("title") or "").strip().lower(): r for r in load()}
        for rec in rdr:
            t = (rec.get(pick["title"]) or "").strip()
            if not t or t.lower() in ("total", "totals"): continue
            row = have.get(t.lower()) or {k: None for k in FIELDS}
            row["title"] = t
            for f in ("views", "avg_pct", "likes", "comments", "shares", "subs", "viewed_pct"):
                if pick[f] and num(rec.get(pick[f])) is not None: row[f] = num(rec[pick[f]])
            if pick["avd_s"] and rec.get(pick["avd_s"]): row["avd_s"] = duration(rec[pick["avd_s"]])
            if pick["posted"] and rec.get(pick["posted"]): row["posted"] = str(rec[pick["posted"]])[:10]
            row["checked"] = dt.date.today().isoformat()
            have[t.lower()] = row
        save(list(have.values()))
        return jsonify(ok=True, n=len(have), matched={k: v for k, v in pick.items() if v})

    @app.post("/api/analytics/import-planner")
    def analytics_planner():
        import openpyxl
        f = Path(cfg()["planner"])
        if not f.exists(): abort(404, "no planner file")
        ws = openpyxl.load_workbook(f, read_only=True, data_only=True)["Analytics"]
        head = [c.value for c in next(ws.iter_rows(min_row=3, max_row=3))]
        ix = {h: i for i, h in enumerate(head) if h}
        want = {"Title": "title", "Posted (IST)": "posted", "Slot": "slot", "Video type": "type", "Views": "views",
                "Viewed vs swiped %": "viewed_pct", "Avg % viewed": "avg_pct", "Avg view duration (s)": "avd_s", "Likes": "likes",
                "Comments": "comments", "Shares": "shares", "Subs gained": "subs", "Biggest drop at (s)": "drop_s",
                "Line / shot at the drop": "drop_note", "Notes": "notes"}
        have = {(r.get("title") or "").strip().lower(): r for r in load()}
        added = 0
        for r in ws.iter_rows(min_row=4, values_only=True):
            t = r[ix["Title"]] if "Title" in ix else None
            if not t or r[ix["Views"]] in (None, ""): continue
            key = str(t).strip().lower()
            row = have.get(key) or {k: None for k in FIELDS}
            for h, k in want.items():
                if h in ix and r[ix[h]] not in (None, ""):
                    v = r[ix[h]]
                    if isinstance(v, (dt.date, dt.datetime)): v = v.date().isoformat() if isinstance(v, dt.datetime) else v.isoformat()
                    if k in ("viewed_pct", "avg_pct") and isinstance(v, (int, float)) and v <= 1: v = v * 100
                    row[k] = v
            if key not in have: added += 1
            have[key] = row
        save(list(have.values()))
        return jsonify(ok=True, n=len(have), added=added)

    @app.post("/api/analytics/analyze")
    def analytics_analyze():
        rows = [r for r in load() if r.get("views") is not None]
        if len(rows) < 2: abort(400, "add numbers for at least 2 videos first")
        question = ((request.json or {}).get("question") or "").strip()
        REPORTS.mkdir(exist_ok=True)
        out = REPORTS / f"analysis-{dt.datetime.now():%Y-%m-%d-%H%M}.md"
        c = cfg()
        prompt = f"""You are the analyst for the YouTube channel "{c['channel']}" (hand-drawn cartoon science Shorts; 2 Shorts a day plus 1 long-form a week; slot A posts at {c['slots'].get('A')} IST, slot B at {c['slots'].get('B')} IST).
Analyze the channel's numbers and write a report to {out} (Markdown). Read {FILE} (every row, pulled from YouTube by the server: video type, slot, views, engaged_pct, average % watched, subs, top countries, the retention curve as [second, % still watching] pairs, and drop_s = the second with the biggest loss after the first 10%), {c['planner']} (the Schedule and Types tabs) and, for any video you want to explain, its folder under {c['projects_dir']} (script.json and <name>-youtube.txt). Also read ~/.claude/youtube/voice.md for the channel voice.

Summary the app computed (a cross-check; recompute anything that looks off):
{json.dumps(summarize(rows), indent=1)}
{('The user also asks: ' + question) if question else ''}

Rules:
- Never invent a number. Quote only what is in the data, and write "n = X" next to any average.
- Be honest about sample size: with fewer than about 5 videos in a group, or under about 1,000 views per video, call a pattern a hint, not a conclusion. Do not recommend big changes on thin data.
- For Shorts the useful signals are engaged_pct (engaged views / views, a proxy for the hook; YouTube's own "viewed vs swiped away" is not in the API, so viewed_pct is only filled if the user typed it from Studio), average % watched (retention and loop) and subs per 1,000 views. Raw views mostly reflect distribution.
- Use drop_s and the retention curve to say which line or shot lost people: read the project's web/words.js or script.json to see what was said at that second, and say what to change in the next script.
- Slot and type were inferred from publish time and the planner; if one looks wrong for a row, say so rather than trusting it.

Report structure:
# Analysis <date>
## What the data says (5 bullets max, each with the number)
## What is probably noise
## Slot A vs slot B (and India vs US if the geo column has data)
## Video types: keep / double / drop
## Hook and retention: fixes for the next scripts
## Decisions (max 3; each has the change, the number that justifies it, and how to test it)
## Next checkpoint (what to collect and when)
Only write the report. Do not edit the planner, the skills or any video. Finish by printing the Decisions section."""
        j = start_job("analyze · analytics", list(c["agent_command"]) + [prompt], c["agent_cwd"])
        return jsonify(id=j["id"], label=j["label"], report=out.name)

    @app.get("/api/reports")
    def reports_list():
        REPORTS.mkdir(exist_ok=True)
        return jsonify([{"name": f.name, "modified": f.stat().st_mtime} for f in sorted(REPORTS.glob("*.md"), key=lambda f: -f.stat().st_mtime)])

    @app.get("/api/reports/<name>")
    def report_get(name):
        if not re.match(r"^[\w.-]+\.md$", name): abort(400)
        f = REPORTS / name
        if not f.exists(): abort(404, "not written yet")
        return jsonify(name=name, text=f.read_text(encoding="utf-8"))
