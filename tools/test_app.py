"""Tests for Bean Studio's fixes. No network, no sign-in, no real agent.   Run: .venv\\Scripts\\python tools\\test_app.py"""
import datetime as dt, json, os, sys, tempfile, time, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "app")); sys.path.insert(0, str(HERE))
import server, planner, analytics, store, ytstate

TMP = Path(tempfile.mkdtemp(prefix="bean-test-"))
server.CONFIG = TMP / "config.json"          # never touch the real settings
server._cfg.update(stamp="unset", val=None)
c = server.app.test_client()
H = {"Host": "127.0.0.1:5173"}
ok = lambda name: print("  ok  ", name)


def test_config():
    assert server.validate_config({"port": "x"}) and server.validate_config({"slots": {"A": "25:99"}}) and server.validate_config([]) and server.validate_config({"agent_command": []})
    assert not server.validate_config({"port": 5173, "slots": {"A": "12:00"}, "topic_channels": ["a"]})
    cur = c.get("/api/config").json
    cur["channel"] = "My Channel"; cur["port"] = server.DEFAULTS["port"]
    r = c.put("/api/config", json=cur); assert r.status_code == 200 and r.json["saved"] == 1, r.json
    assert json.loads(server.CONFIG.read_text()) == {"channel": "My Channel"}, "only the changed setting is stored"
    assert c.put("/api/config", json={"port": "nope"}).status_code == 400
    server.CONFIG.write_text("{not json")
    time.sleep(0.02); os.utime(server.CONFIG, (time.time() + 5, time.time() + 5))
    assert c.get("/api/config").json["channel"] == server.DEFAULTS["channel"] and server._cfg["problem"], "bad config falls back to defaults"
    server.CONFIG.unlink(); server._cfg.update(stamp="unset", val=None)
    ok("config: validated, only changes stored, damaged file tolerated")


def test_guard():
    assert c.get("/api/meta", headers={"Host": "evil.example"}).status_code == 403
    assert c.post("/api/agent", json={"prompt": "x"}, headers={"Origin": "http://evil.example"}).status_code == 403
    assert c.get("/api/meta", headers=H).status_code == 200
    ok("guard: foreign Host and cross-site POST refused")


def test_jobs():
    cmd = [sys.executable, "-c", "import time;print('x');time.sleep(1.2)"]
    a = server.start_job("t · same", cmd, str(TMP), unique=True); b = server.start_job("t · same", cmd, str(TMP), unique=True)
    assert a["id"] == b["id"], "double click must not start a second job"
    for _ in range(60):
        if a["done"]: break
        time.sleep(0.1)
    c2 = server.start_job("t · same", cmd, str(TMP), unique=True); assert c2["id"] != a["id"], "a finished job doesn't block a new one"
    big = server.start_job("t · big", [sys.executable, "-c", "print('\\n'.join(str(i) for i in range(5000)))"], str(TMP))
    for _ in range(100):
        if big["done"]: break
        time.sleep(0.1)
    r = c.get(f"/api/jobs/{big['id']}?since=0", headers=H).json
    assert len(big["log"]) <= server.MAX_LOG and r["n"] == 5000 and big["dropped"] > 0 and r["log"][-1] == "4999"
    assert c.get(f"/api/jobs/{big['id']}?since={r['n']}", headers=H).json["log"] == []
    assert c.post("/api/run", json={"action": "upload", "project": "x"}, headers=H).status_code == 400, "an upload needs a time"
    assert c.post("/api/run", json={"action": "rm -rf", "project": "x"}, headers=H).status_code == 400
    assert c.post("/api/run", data="nope", headers=H).status_code == 400
    ok("jobs: de-duplicated, log bounded with correct offsets, bad requests refused")


def test_planner_and_schedule():
    rows, err = planner.rows(TMP / "missing.xlsx"); assert rows == [] and "no planner" in err
    real = HERE.parent / "bean-planner.xlsx"
    rows, err = planner.rows(real); assert err is None and rows and isinstance(rows[0]["date"], dt.date), err
    import openpyxl
    orig = openpyxl.load_workbook
    planner._cache["key"] = None
    openpyxl.load_workbook = lambda *a, **k: (_ for _ in ()).throw(PermissionError("locked"))
    try:
        r2, e2 = planner.rows(real); assert "locked" in e2
    finally: openpyxl.load_workbook = orig
    server.CONFIG.write_text(json.dumps({"planner": str(TMP / "gone.xlsx")})); os.utime(server.CONFIG, (time.time() + 9, time.time() + 9))
    r = c.get("/api/schedule", headers=H)
    assert r.status_code == 200 and "no planner" in r.json["planner_error"], "a missing planner must not break the YouTube half"
    server.CONFIG.unlink(); server._cfg.update(stamp="unset", val=None)
    ok("planner: missing and locked files are reported, not fatal")


def test_next_slot():
    now = dt.datetime.now(server.IST)
    server.CONFIG.write_text(json.dumps({"slots": {"A": "12:00", "B": "06:30", "Long": "21:30"}})); os.utime(server.CONFIG, (time.time() + 20, time.time() + 20))
    ytstate.STATE["videos"] = []
    first = c.get("/api/next-slot", headers=H).json
    t1 = dt.datetime.strptime(first["at"], "%Y-%m-%d %H:%M").replace(tzinfo=server.IST)
    assert t1 > now + dt.timedelta(minutes=34) and first["slot"] in ("A", "B")
    ytstate.STATE["videos"] = [{"state": "scheduled", "when": t1.isoformat(timespec="minutes")}]
    second = c.get("/api/next-slot", headers=H).json
    assert second["at"] != first["at"] and dt.datetime.strptime(second["at"], "%Y-%m-%d %H:%M") > dt.datetime.strptime(first["at"], "%Y-%m-%d %H:%M")
    ytstate.STATE["videos"] = []; server.CONFIG.unlink(); server._cfg.update(stamp="unset", val=None)
    ok(f"next slot: {first['at']} (slot {first['slot']}), then skips it once scheduled -> {second['at']}")


def test_analytics_merge():
    app2 = server.Flask("t2"); root = TMP / "root"; (root / "data").mkdir(parents=True)
    analytics.register(app2, root, server.cfg, server.start_job)
    c2 = app2.test_client()
    store.write(root / "data" / "analytics.json", [{"id": "v1", "title": "One", "views": 100, "slot": None, "type": None, "notes": None}])
    # the user edits an OLD copy of the table while a newer sync has already changed the numbers
    store.write(root / "data" / "analytics.json", [{"id": "v1", "title": "One", "views": 999, "slot": None, "type": None, "notes": None}])
    r = c2.put("/api/analytics", json={"rows": [{"id": "v1", "title": "One", "views": 100, "slot": "B", "type": "Why", "notes": "mine", "likes": 5}]}).json
    row = store.read(root / "data" / "analytics.json")[0]
    assert r["changed"] == 3 and row["views"] == 999 and row["slot"] == "B" and row["type"] == "Why" and "likes" not in row, row
    new = [{"id": "v1", "title": "One", "views": 1500, "slot": "A", "type": None}]
    out = analytics.apply_edits(new, store.read(root / "data" / "analytics.json"))
    assert out[0]["slot"] == "B" and out[0]["type"] == "Why" and out[0]["views"] == 1500, "a sync keeps hand-set fields and takes new numbers"
    assert c2.put("/api/analytics", json={"rows": "x"}).status_code == 400
    ok("analytics: saving edits never reverts newer numbers; sync keeps your edits")


def test_store_atomic():
    f = TMP / "s.json"; store.write(f, {"a": 1}); assert store.read(f) == {"a": 1} and not list(TMP.glob("s.json.tmp"))
    f.write_text("{broken"); assert store.read(f, "dflt") == "dflt"
    ok("store: atomic write, damaged file gives the default")


def test_upload_lock():
    sys.path.insert(0, str(HERE.parent / "tools"))
    import yt_upload as yu
    proj = TMP / "proj" / "demo"; proj.mkdir(parents=True)
    (proj / "demo.mp4").write_bytes(b"0" * 2048); (proj / "demo.srt").write_text("1\n"); (proj / "demo-thumbnail.png").write_bytes(b"\x89PNG")
    (proj / "demo-youtube.txt").write_text("== TITLE ==\nDemo?\n\n== DESCRIPTION ==\nLine one.\n\n== TAGS ==\na, b\n\n== SETTINGS ==\nAudience: Not made for kids\n")
    yu.ROOT = TMP / "proj"
    calls = []
    class Req:
        def __init__(s, v=None): s.v = v
        def next_chunk(s): return None, {"id": "VID1"}
        def execute(s): return s.v or {}
    class YT:
        def videos(s): return s
        def insert(s, **kw): calls.append(("insert", kw["body"]["status"])); return Req()
        def list(s, **kw): return Req({"items": [{"status": {"privacyStatus": "public"}}]})
        def thumbnails(s): return s
        def captions(s): return s
        def set(s, **kw): return Req()
    yu.service = lambda: YT()
    args = lambda **k: types.SimpleNamespace(**{"project": "demo", "now": False, "at": None, "slot": None, "date": None, "dry_run": False, "force": False, **k})
    lock = proj / "demo-upload.lock"; lock.write_text("1")
    try: yu.cmd_upload(args(now=True)); assert False
    except SystemExit as e: assert "already running" in str(e)
    lock.unlink()
    yu.cmd_upload(args(now=True))
    assert not lock.exists() and (proj / "demo-upload.json").exists() and calls[-1][1]["privacyStatus"] == "public" and "publishAt" not in calls[-1][1]
    try: yu.cmd_upload(args(now=True)); assert False
    except SystemExit as e: assert "already uploaded" in str(e)
    (proj / "demo-upload.json").unlink()
    when = (dt.datetime.now(server.IST) + dt.timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
    yu.cmd_upload(args(at=when)); assert calls[-1][1]["privacyStatus"] == "private" and calls[-1][1]["publishAt"].endswith("Z")
    ok("uploader: lock refuses a second upload, releases itself, now=public, scheduled=private+publishAt")


def test_agent_duration():
    seen, orig = [], server.start_job
    server.start_job = lambda label, cmd, cwd, unique=False, **kw: seen.append(cmd[-1]) or {"id": "x", "label": label}
    try:
        assert c.post("/api/agent", json={"prompt": "Make a Short about onions", "duration": 50}, headers=H).status_code == 200
        p = seen[-1]
        assert "TARGET LENGTH: 50 seconds" in p and "--target 50" in p and "about 155 words" in p and "Short about onions" in p
        c.post("/api/agent", json={"prompt": "x", "duration": 420}, headers=H)
        assert "long video" in seen[-1] and "line-boil-wide" in seen[-1] and "--wide" in seen[-1] and "--target 420" in seen[-1] and "about 1302 words" in seen[-1]
        c.post("/api/agent", json={"prompt": "no length"}, headers=H); assert "TARGET LENGTH" not in seen[-1]
        assert c.post("/api/agent", json={"prompt": "x", "duration": 5}, headers=H).status_code == 400
        assert c.post("/api/agent", json={"prompt": "x", "duration": "abc"}, headers=H).status_code == 400
        meta = c.get("/api/meta", headers=H).json
        assert meta["lengths"]["short"] == [30, 40, 50, 60] and meta["lengths"]["long"][0] == 300
    finally: server.start_job = orig
    ok("agent: the chosen duration reaches the skill (Short rule or long-form rule), bad values refused")


def test_long_topics():
    import topics
    root = TMP / "troot"; (root / "data").mkdir(parents=True); (root / "research").mkdir(); (root / "proj").mkdir()
    (root / "research" / "brief.md").write_text("brief")
    store.write(root / "data" / "picks.json", {"long": [{"title": "Pick A", "type": "Ranking", "brief": "research/brief.md",
                                                       "inspired_by": {"channel": "c", "title": "t"}}], "short": []})
    cfgd = dict(server.cfg()); cfgd["projects_dir"] = str(root / "proj")
    JOBS, launched = {}, []
    def fake(label, cmd, cwd, unique=False):
        j = {"id": f"j{len(JOBS)}", "label": label, "log": [], "done": False, "code": None, "started": time.time()}
        JOBS[j["id"]] = j; launched.append(cmd); return j
    app3 = server.Flask("t3"); topics.register(app3, root, lambda: cfgd, fake, JOBS); c3 = app3.test_client()
    assert c3.get("/api/topics/picks?kind=long").json["picks"][0]["pick"] and c3.get("/api/topics/picks?kind=short").json["picks"] == []
    store.write(root / "data" / "topic-pool-long.json", {"fetched": "2026-11-04T00:00:00", "videos": [
        {"id": f"v{i}", "title": f"Thing {i} explained", "channel": "Ch", "views": 1000 * i, "multiple": 2 + i / 10, "type": "Explainer", "duration": 500, "url": "u"} for i in range(1, 16)]})
    assert c3.get("/api/topics?kind=long").json["videos"] == 15 and c3.get("/api/topics?kind=short").json["videos"] is None
    assert c3.post("/api/topics/options", json={"kind": "short"}).status_code == 400, "the Shorts pool is separate"
    r = c3.post("/api/topics/options", json={"kind": "long"}).json
    prompt = launched[-1][-1]
    assert "LONG video" in prompt and "chapters" in prompt and "runtime_min" in prompt and "sources_to_check" in prompt
    out = root / "data" / f"topic-options-{r['batch']}.json"
    out.write_text(json.dumps([{"title": f"Idea {i}", "type": ["Ranking", "Why", "Nope", "Myth test", "Explainer"][i], "fact_risk": "wild" if i == 0 else "low",
                                "runtime_min": "abc" if i == 0 else 99 if i == 1 else 8, "chapters": [f"c{k}" for k in range(20)], "reuse_shorts": "not a list",
                                "inspired_by": {"channel": "c", "title": "t", "multiple": 3}} for i in range(5)]))
    JOBS[r["job"]]["done"] = True
    o = c3.get(f"/api/topics/batch/{r['batch']}").json["options"]
    assert len(o) == 5 and o[0]["runtime_min"] == 7 and o[1]["runtime_min"] == 15 and o[0]["fact_risk"] == "medium" and o[2]["type"] == "Other"
    assert len(o[0]["chapters"]) == 9 and o[0]["reuse_shorts"] == []
    last = c3.get("/api/topics/picks?kind=long").json
    assert [x["title"] for x in last["last"]] == [x["title"] for x in o] and last["last_when"], "the last five ideas persist for the next visit"
    assert c3.get("/api/topics/picks?kind=short").json["last"] == []
    pick = c3.get("/api/topics/picks?kind=long").json["picks"][0]
    m = c3.post("/api/topics/make", json={"kind": "long", "topic": pick, "answers": {"minutes": 7, "voice": "bf_emma", "structure": "ranked", "speed": "x"}}).json
    mp = launched[-1][-1]
    assert m["kind"] == "long" and (root / "proj" / m["project"]).is_dir(), "the folder is reserved straight away"
    assert "LONG video (7 minutes, 16:9)" in mp and "line-boil-wide skill" in mp and "TARGET LENGTH: 420 seconds" in mp and "--target 420" in mp
    assert "RESEARCH BRIEF" in mp and str(root / "research" / "brief.md") in mp and "build.py new " in mp and " --wide" in mp and "build.py video " in mp and "ONE CHAPTER AT A TIME" in mp and "1280x720" in mp and "--voice bf_emma --speed 1.0" in mp
    evil = c3.post("/api/topics/make", json={"kind": "long", "topic": dict(pick, brief="../../outside.md"), "answers": {}}).json
    assert "RESEARCH BRIEF" not in launched[-1][-1], "a brief path outside the studio folder is ignored"
    s = c3.post("/api/topics/make", json={"kind": "short", "topic": {"title": "A short idea"}, "answers": {"duration": 50}}).json
    sp = launched[-1][-1]
    assert "Make a new Short" in sp and "TARGET LENGTH: 50 seconds" in sp and "build.py video" in sp
    assert json.loads((root / "data" / "make" / f"{m['project']}.json").read_text())["kind"] == "long"
    # the Videos tab sees a long project as a package, with its own checklist and documents
    pdir = root / "proj" / m["project"]; (pdir / "script.json").write_text(json.dumps(["word " * 40]))
    (pdir / f"{m['project']}-sources.md").write_text("claim | link"); (pdir / f"{m['project']}-youtube.txt").write_text("== TITLE ==\nA long title\n")
    old_root, old_cfg = server.ROOT, server.CONFIG
    server.ROOT = root; server.CONFIG = TMP / "cfg-long.json"; server.CONFIG.write_text(json.dumps({"projects_dir": str(root / "proj")})); server._cfg.update(stamp="unset", val=None)
    try:
        pj = c.get(f"/api/projects/{m['project']}", headers=H).json
        assert pj["kind"] == "long" and list(pj["steps"]) == ["script", "sources", "chapters", "video", "srt", "thumbnail", "sheet", "uploaded"] and pj["steps"]["sources"] and not pj["steps"]["video"] and not pj["ready"], pj
        assert "sources" in pj["docs"] and "chapters" not in pj["docs"]
        sj = c.get(f"/api/projects/{s['project']}", headers=H)
        assert sj.status_code == 404 or sj.json["kind"] == "short"
    finally:
        server.ROOT, server.CONFIG = old_root, old_cfg; server._cfg.update(stamp="unset", val=None)
    ok("topics (long): separate pool, picks with brief, sanitised ideas, package prompt, safe brief path, long project view")


def test_live_feed_and_progress():
    import agentlog
    job, ev = {}, lambda **k: json.dumps(k)
    assert "Agent started" in agentlog.parse(ev(type="system", subtype="init", model="claude-sonnet-5-5"), job)[0]
    out = agentlog.parse(ev(type="assistant", message={"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python build.py voice demo --target 40"}}]}), job)
    assert out == ["▸ Recording the voiceover and timing every word"] and job["steps"] == 1 and job["activity"].startswith("Recording")
    assert agentlog.parse(ev(type="assistant", message={"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "C:\\x\\SKILL.md"}}]}), job) == ["▸ Reading SKILL.md"]
    assert agentlog.parse(ev(type="assistant", message={"content": [{"type": "text", "text": "Writing the   script now"}]}), job) == ["💬 Writing the script now"]
    assert agentlog.parse(ev(type="user", message={"content": [{"type": "tool_result", "is_error": True, "content": "boom"}]}), job) == ["✗ boom"]
    res = agentlog.parse(ev(type="result", is_error=False, duration_ms=125000, num_turns=20, total_cost_usd=0.1234, result="All done", usage={"output_tokens": 900}), job)
    assert "Finished after 2 min 5 s and 20 turns, about $0.12" in res[0] and res[1] == "All done" and job["cost"] == 0.1234
    assert agentlog.parse("plain text line", job) == ["plain text line"] and agentlog.parse("   ", job) == []
    proj = TMP / "prog" / "vid"; assert agentlog.make_progress(proj)["pct"] == 0
    proj.mkdir(parents=True); (proj / "web").mkdir(); (proj / "audio").mkdir()
    (proj / "script.json").write_text(json.dumps(["word " * 40])); g = agentlog.make_progress(proj)
    assert g["pct"] == 10 and g["stage"] == "Recording the voiceover"
    (proj / "audio" / "words.json").write_text("[]"); (proj / "web" / "shots.js").write_text("x" * 900); (proj / "web" / "cast.js").write_text("y" * 400)
    assert agentlog.make_progress(proj)["pct"] == 50 and agentlog.make_progress(proj)["stage"] == "Checking the pictures"
    for f in ("vid.mp4", "vid.srt", "vid-thumbnail.png", "vid-youtube.txt"): (proj / f).write_text("z")
    g = agentlog.make_progress(proj); assert g["pct"] == 100 and g["stage"] == "All done", g     # no stills folder: still reaches 100
    lp = TMP / "prog" / "lng"; lp.mkdir(); (lp / "script.json").write_text(json.dumps(["word " * 80]))
    assert agentlog.make_progress(lp, "long")["pct"] == 8
    (lp / "chapters.json").write_text(json.dumps([{"title": "a", "line": 0}] * 4)); (lp / "web" / "shots").mkdir(parents=True); (lp / "web" / "shots" / "ch01.js").write_text("x"); (lp / "web" / "shots" / "ch02.js").write_text("x")
    g = agentlog.make_progress(lp, "long"); assert g["stage"].startswith("Recording the voiceover") or "Drawing the chapters (50%)" in g["stage"] or g["pct"] > 8, g
    ok("agent feed: steps in plain words, cost captured; progress comes from real files and skipped stages don't stall it")


def test_agent_modes_and_runs():
    import agentlog
    calls, orig = [], server.start_job
    server.start_job = lambda label, cmd, cwd, unique=False, parser=None, window=False: calls.append((cmd, parser, window)) or {"id": "x", "label": label}
    try:
        server.start_agent("t", "PROMPT", "opus", "feed"); cmd, parser, window = calls[-1]
        assert cmd[-1] == "PROMPT" and "-p" in cmd and cmd[cmd.index("--model") + 1] == "opus" and cmd[-4:-1] == ["--output-format", "stream-json", "--verbose"] and parser is agentlog.parse and not window
        server.start_agent("t", "PROMPT", None, "window"); cmd, parser, window = calls[-1]
        assert window and "-p" not in cmd and cmd[-1] == "PROMPT" and "--model" not in cmd and "--permission-mode" in cmd
        server.start_agent("t", "PROMPT", "sonnet", "plain"); cmd, parser, window = calls[-1]
        assert parser is None and "--output-format" not in cmd and cmd[-1] == "PROMPT"
    finally: server.start_job = orig
    # a finished run lands in the ledger with its cost
    old_root = server.ROOT; server.ROOT = TMP / "ledger"
    try:
        script = ("import json;print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','name':'WebSearch','input':{'query':'x'}}]}}));"
                  "print(json.dumps({'type':'result','is_error':False,'duration_ms':3000,'num_turns':3,'total_cost_usd':0.05,'result':'ok','usage':{'output_tokens':321}}))")
        j = server.start_job("make · vid", [sys.executable, "-c", script], str(TMP), parser=agentlog.parse)
        for _ in range(60):
            if j["done"]: break
            time.sleep(0.1)
        assert j["activity"] == "Finished" and j["steps"] == 1 and j["log"][0] == "▸ Searching the web: x"
        r = c.get("/api/runs", headers=H).json
        assert r["count"] == 1 and r["runs"][0]["cost"] == 0.05 and r["runs"][0]["turns"] == 3 and r["runs"][0]["output_tokens"] == 321 and r["total"] == 0.05
        # the jobs list shows a video being made with its progress
        server.CONFIG = TMP / "cfg-prog.json"; server.CONFIG.write_text(json.dumps({"projects_dir": str(TMP / "prog")})); server._cfg.update(stamp="unset", val=None)
        sj = server.start_job("make · vid", [sys.executable, "-c", "import time;time.sleep(1.5)"], str(TMP))
        v = next(x for x in c.get("/api/jobs", headers=H).json if x["id"] == sj["id"])
        assert v["progress"]["pct"] == 100 and v["kind"] == "short" and "elapsed" in v and v["window"] is False
    finally:
        server.ROOT = old_root; server._cfg.update(stamp="unset", val=None)
    ok("agent modes: feed / own window / plain command lines; the run ledger records cost; the jobs list carries progress")


def test_delete_and_media():
    d = Path(server.cfg()["projects_dir"]) / "zz-bean-test"; (d / "web").mkdir(parents=True, exist_ok=True)
    (d / "script.json").write_text('["x"]'); (d / "web" / "a.js").write_text("1"); os.chmod(d / "web" / "a.js", 0o444)
    assert c.delete("/api/projects/zz-bean-test", headers=H).json["ok"] and not d.exists()
    assert c.delete("/api/projects/..%2Fx", headers=H).status_code in (400, 404)
    ok("delete: read-only files removed, bad names refused")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"): fn()
    print("all passed")
