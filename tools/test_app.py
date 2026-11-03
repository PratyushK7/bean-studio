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
