"""Tests for Bean Studio's Pipeline tab (app/pipeline.py and its endpoints). Needs Flask, which only the studio's .venv has:
    .venv/Scripts/python.exe tools/tests/test_studio_pipeline.py
Throwaway projects only; the real project is read, never changed, and no job is started."""
import json, shutil, sys, tempfile, traceback
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]; ROOT = TOOLS.parent
JEW = ROOT / "channels" / "hindi" / "videos" / "jewellery-shop-economics"
results = []


def test(fn):
    try: fn(); results.append((fn.__name__, "ok", ""))
    except Exception as e: results.append((fn.__name__, "FAIL", f"{e}\n{traceback.format_exc(limit=2)}"))
    return fn


def tmp_project(with_plan=True):
    d = Path(tempfile.mkdtemp(prefix="studio-test-")); shutil.copy(JEW / "script.json", d / "script.json")
    if with_plan: shutil.copy(JEW / "visual-plan.json", d / "visual-plan.json")
    (d / "images").mkdir()
    return d


@test
def studio_stage_status_comes_from_files_and_flags_stale_ones():
    sys.path.insert(0, str(ROOT / "app")); import pipeline as pl
    d = tmp_project(True)
    s = pl.summary(d, hindi=True)
    assert s["new"] and s["next_key"] == "prompts" and s["stages"][1]["state"].startswith("144 shots"), s["next_key"]
    (d / "voice.mp3").write_bytes(b"x"); (d / "voice-lines.json").write_text(json.dumps([{"i": 0}] * 3), encoding="utf-8")     # a voice made for a shorter, older script
    v = next(x for x in pl.summary(d, hindi=True)["stages"] if x["key"] == "voice")
    assert v["warn"] and "older script" in v["state"], v
    assert pl.summary(d, hindi=False)["new"], "a project with a visual plan always gets the documentary stages"
    plain = tmp_project(False)
    assert not pl.summary(plain, hindi=False)["new"], "an older project keeps the older stages"
    clips = next(x for x in pl.summary(JEW, hindi=True)["stages"] if x["key"] == "clips")
    assert not clips["state"] and "not made" in clips.get("note", ""), "planned clips are a note, not a finished step"


@test
def studio_endpoints_refuse_bad_requests_and_start_nothing():
    sys.path.insert(0, str(ROOT / "app")); import server
    c = server.app.test_client(); H = {"X-Channel": "hindi"}; name = JEW.name
    jobs_before = len(server.JOBS)
    assert c.post(f"/api/pipeline/{name}/step", headers=H, json={"step": "format-c"}).status_code == 400, "an unknown step"
    assert c.post(f"/api/pipeline/{name}/step", headers=H, json={"step": "voice-pro"}).status_code == 400, "a paid step needs the owner's OK"
    assert c.post(f"/api/pipeline/{name}/review", headers=H, json={"action": "approve", "numbers": "1; rm -rf"}).status_code == 400, "picture numbers are checked"
    assert c.get(f"/api/pipeline/{name}/asset/images/001.png", headers=H).status_code == 400, "only qa, review and graphics are served"
    assert len(server.JOBS) == jobs_before, "nothing may have started"


@test
def studio_shows_the_v_number_finals_with_their_qa():
    sys.path.insert(0, str(ROOT / "app")); import pipeline as pl
    d = tmp_project(True); (d / "qa").mkdir(); (d / "video.mp4").write_bytes(b"render")
    (d / "qa" / "video-qa.json").write_text(json.dumps({"verdict": "PASS", "issues": {"fail": [], "warn": []}}), encoding="utf-8")
    (d / "v1.mp4").write_bytes(b"render")                                   # the same bytes: the link to the checked render
    v = next(x for x in pl.summary(d, hindi=True)["stages"] if x["key"] == "video")
    assert v["state"].startswith("v1.mp4") and "pass" in v["state"], v


@test
def studio_cast_and_music_endpoints_read_the_project_and_refuse_bad_voices():
    sys.path.insert(0, str(ROOT / "app")); import server
    c = server.app.test_client(); H = {"X-Channel": "hindi"}; name = JEW.name
    cast = c.get(f"/api/pipeline/{name}/cast", headers=H).get_json()
    who = [x["who"] for x in cast["speakers"]]
    assert who[0] == "narrator" and {"ramesh", "ankit", "nandu"} <= set(who), who
    assert next(x for x in cast["speakers"] if x["who"] == "ankit")["lines"] >= 5 and "rohan" in cast["pool"]["sarvam"], "line counts and the tried pool"
    assert cast["problems"] == [], cast["problems"]
    m = c.get(f"/api/pipeline/{name}/music", headers=H).get_json()
    assert len(m["cues"]) >= 30 and {"silence", "dread", "flashback"} <= {x["mood"] for x in m["cues"]} and m["moods"]["sad"]["tracks"], "the plan and the tracks per mood"
    bad = c.post(f"/api/pipeline/{name}/cast", headers=H, json={"cast": {"ramesh": {"sarvam": {"speaker": "not-a-voice"}}}})
    assert bad.status_code == 400, "only voices that were actually tried are accepted"
    assert c.post(f"/api/pipeline/{name}/cast", headers=H, json={"cast": {"narrator": {}}}).status_code == 400, "the narrator is never reassigned"
    s = next(x for x in c.get("/api/pipeline", headers=H).get_json()["projects"] if x["name"] == name)
    assert [x["key"] for x in s["stages"] if x["key"] in ("music", "cast")] == ["music", "cast"]


@test
def new_video_opens_its_own_claude_session_and_its_card_reopens_it():
    sys.path.insert(0, str(ROOT / "app")); import sessions
    from flask import Flask
    d = Path(tempfile.mkdtemp(prefix="studio-sess-")); (d / "data").mkdir()
    c = {"channel_id": "hindi", "language": "Hindi", "channel": "Decoding Vyapaar", "projects_dir": str(d), "plan_model": "opus",
         "agent_command": ["claude", "-p", "--permission-mode", "acceptEdits"], "agent_cwd": str(ROOT)}
    started, JOBS = [], {}
    def fake_start(label, cmd, cwd, window=False, **k):                     # nothing is launched in a test
        started.append({"label": label, "cmd": cmd, "window": window}); return {"id": str(len(started))}
    app = Flask("t"); sessions.register(app, ROOT, lambda: c, fake_start, JOBS, data=lambda: d / "data"); cl = app.test_client()
    r = cl.post("/api/sessions/new", json={"topic": "Economics of a petrol pump", "format": "economics"})
    assert r.status_code == 200, r.get_data(as_text=True)
    slug = r.get_json()["project"]; cmd = started[-1]["cmd"]
    assert slug == "economics-petrol-pump" and (d / slug / "images").is_dir(), slug
    assert started[-1]["window"] and "-p" not in cmd and cmd[cmd.index("--session-id") + 1] == r.get_json()["session"], cmd
    assert "hindi-case-study" in cmd[-1] and "Gate A" in cmd[-1] and str(d / slug) in cmd[-1], "the first message names the skill, the folder and the stop"
    assert cl.post("/api/sessions/new", json={"topic": "Economics of a petrol pump"}).status_code == 409, "an existing video is never overwritten"
    assert cl.post("/api/sessions/new", json={"topic": "पेट्रोल पंप"}).status_code == 400, "a Devanagari topic needs an English folder name"
    o = cl.post(f"/api/sessions/{slug}/open").get_json()
    assert o["resumed"] and started[-1]["cmd"][-2:] == ["--resume", o["session"]], started[-1]["cmd"]
    JOBS["x"] = {"label": f"session · {slug}", "channel": "hindi", "done": False}
    assert cl.post(f"/api/sessions/{slug}/open").status_code == 409, "one window per video"
    (d / "old-video").mkdir()
    o = cl.post("/api/sessions/old-video/open").get_json()
    assert not o["resumed"] and "existing video" in started[-1]["cmd"][-1], "a video with no session gets one that first looks where it is"
    assert set(cl.get("/api/sessions").get_json()["sessions"]) == {slug, "old-video"}


@test
def show_buttons_return_what_each_step_made_and_serve_only_safe_files():
    sys.path.insert(0, str(ROOT / "app")); import server
    c = server.app.test_client(); H = {"X-Channel": "hindi"}; name = JEW.name
    kinds = {}
    for st in ("script", "plan", "prompts", "images", "review", "upscale", "music", "cast", "voice", "clips", "sample", "video", "sheet"):
        r = c.get(f"/api/pipeline/{name}/show/{st}", headers=H); assert r.status_code == 200, (st, r.status_code)
        kinds[st] = {b["type"] for b in r.get_json()["blocks"]}
    assert "text" in kinds["script"] and "table" in kinds["plan"] and "pics" in kinds["images"] and "audio" in kinds["voice"] and "video" in kinds["sample"], kinds
    assert c.get(f"/api/pipeline/{name}/show/nothing", headers=H).status_code == 400
    assert c.get(f"/api/pipeline/{name}/file/script.json", headers=H).status_code == 400, "only sound, video and pictures"
    assert c.get(f"/api/pipeline/{name}/file/..%2F..%2Fsecret.mp3", headers=H).status_code in (400, 404), "never outside the project"


if __name__ == "__main__":
    for name, st, why in results: print(f"{st:4s} {name}" + (f"\n     {why}" if why else ""))
    bad = [r for r in results if r[1] != "ok"]
    print(f"\n{len(results) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
