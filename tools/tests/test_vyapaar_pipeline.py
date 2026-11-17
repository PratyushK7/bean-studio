"""Tests for the Decoding Vyapaar visual pipeline. Plain Python, no test framework needed:
    python tools/tests/test_vyapaar_pipeline.py      (the studio's own tests: .venv/Scripts/python.exe tools/tests/test_studio_pipeline.py, which needs Flask)
Uses throwaway projects in a temp folder; the real projects are only read. No paid calls, no browser automation.
"""
import filecmp, json, shutil, subprocess, sys, tempfile, traceback
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]; ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import vyapaar_visual as vv
import vyapaar_review as vr
import vyapaar_render as rn

JEW = ROOT / "channels" / "hindi" / "videos" / "jewellery-shop-economics"
PY = sys.executable
results = []


def test(fn):
    try: fn(); results.append((fn.__name__, "ok", ""))
    except Exception as e: results.append((fn.__name__, "FAIL", f"{e}\n{traceback.format_exc(limit=2)}"))
    return fn


def tmp_project(with_plan=True, images=()):
    d = Path(tempfile.mkdtemp(prefix="vyapaar-test-"))
    shutil.copy(JEW / "script.json", d / "script.json")
    shutil.copy(JEW / "jewellery-shop-economics-research.md", d / "x-research.md")
    if with_plan: shutil.copy(JEW / "visual-plan.json", d / "visual-plan.json")
    (d / "images").mkdir()
    for n in images: shutil.copy(next((JEW / "images").glob("001.*")), d / "images" / f"{n:03d}.png")
    return d


@test
def legacy_prompts_unchanged():
    """a project with no visual plan gets byte-identical prompt files from the new vyapaar_prompts.py and the original one"""
    a, b = tmp_project(False), tmp_project(False)
    shutil.copy(JEW / "v2" / "script-v2.json", a / "script.json"); shutil.copy(JEW / "v2" / "script-v2.json", b / "script.json")
    subprocess.run([PY, str(TOOLS / "vyapaar_prompts.py"), str(a)], check=True, capture_output=True)
    subprocess.run([PY, str(TOOLS / "_backup-visual-upgrade-2026-11-15" / "vyapaar_prompts.py"), str(b)], check=True, capture_output=True)
    for f in sorted((b / "prompts").glob("*.txt")):
        assert filecmp.cmp(f, a / "prompts" / f.name, shallow=False), f"{f.name} differs"
    assert json.loads((a / "images-index.json").read_text(encoding="utf-8")) == json.loads((b / "images-index.json").read_text(encoding="utf-8")), "index differs"


@test
def structured_prompts_and_stable_slots():
    d = tmp_project(True, images=[1, 2, 3, 4, 5])
    idx1, probs = vv.build(d)
    assert not probs, probs
    scenes = [e for e in idx1 if e["type"] == "scene"]
    assert len(scenes) == 117 and all(e["refs"] == [r for r in e["refs"]] for e in scenes)
    assert min(e["n"] for e in scenes) > 5, "new pictures must not take the numbers of existing ones"
    first = {e["shot"]: e["n"] for e in scenes}
    idx2, _ = vv.build(d)                                         # a re-run keeps every number
    assert {e["shot"]: e["n"] for e in idx2 if e["type"] == "scene"} == first
    s = next(e for e in idx2 if e.get("shot") == "S005")
    shutil.copy(next((JEW / "images").glob("001.*")), d / "images" / f"{s['n']:03d}.png")
    idx3, _ = vv.build(d)
    assert next(e for e in idx3 if e.get("shot") == "S005")["status"] == "have"
    plan = json.loads((d / "visual-plan.json").read_text(encoding="utf-8"))
    next(x for x in plan["shots"] if x["id"] == "S005")["action"] += " (changed)"
    (d / "visual-plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    idx4, _ = vv.build(d)
    assert next(e for e in idx4 if e.get("shot") == "S005")["status"] == "stale", "a changed prompt must mark the picture stale"
    files = "".join(f.read_text(encoding="utf-8") for f in (d / "prompts").glob("0*.txt"))
    assert "(changed)" in files, "a stale picture goes back into the prompt files"


@test
def prompts_are_scene_specific():
    plan = json.loads((JEW / "visual-plan.json").read_text(encoding="utf-8")); b = vv.load_bible(JEW)
    sh = {s["id"]: s for s in plan["shots"]}
    night = vv.shot_prompt(sh["S074"], plan, b); day = vv.shot_prompt(sh["S021"], plan, b); hand = vv.shot_prompt(sh["S020"], plan, b)
    assert "Midnight" in night and "streetlamp" in night and "daylight from the open shopfront" not in night
    assert "early sun" in day
    assert "Only Ramesh's hand" in hand and "short grey hair" not in hand, "a hand-only shot must not describe the face"
    assert "Cinematic composition" not in night, "no empty 'cinematic composition' filler"
    # a three-person shot needs three identities: 300 words is the ceiling (the validator already warns above 250)
    assert all(len(vv.shot_prompt(s, plan, b).split()) < 300 for s in plan["shots"] if s.get("action"))


@test
def validator_catches_bad_numbers_and_gaps():
    d = tmp_project(True)
    plan = json.loads((d / "visual-plan.json").read_text(encoding="utf-8"))
    g = next(x for x in plan["shots"] if x["id"] == "G067"); g["graphic"]["value"] = 1900000      # ₹19 lakh is in no cited row
    plan["shots"] = [x for x in plan["shots"] if x["id"] != "S010"]                               # line 10 loses its shot
    (d / "visual-plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    iss = vv.validate(d)
    assert any("G067" in x and "trace" in x for x in iss["critical"]), iss["critical"]
    assert any("line 10" in x for x in iss["critical"]), iss["critical"]


@test
def number_parsing():
    assert 3000000.0 in vv.numbers("₹30 लाख") and 52000000.0 in vv.numbers("₹5.2 करोड़") and 91.0 in vv.numbers("91%")
    assert 260000.0 in vv.numbers("₹2,60,000")


@test
def review_decisions_and_gate():
    d = tmp_project(True, images=[1, 2, 3, 4, 5])
    vv.build(d)
    assert not vr.gate(d, "images-index.json"), "the gate is closed while pictures are missing or pending"
    vr.decide(d, [1], "approved")
    vr.decide(d, [2], "rejected", "test")
    assert not (d / "images" / "002.png").exists() and list((d / "images" / "_rejected").glob("002-*.png")), "a rejected picture is kept, out of the way"
    r = json.loads((d / "review.json").read_text(encoding="utf-8")); assert r["1"]["status"] == "approved" and r["2"]["status"] == "rejected"
    idx, _ = vv.build(d)
    assert next(e for e in idx if e["n"] == 2)["status"] == "rejected" and "01-characters.txt" in {e.get("file") for e in idx if e["n"] == 2}


@test
def camera_rules():
    cam = vv.load_bible()["render"]["camera"]
    a = {"faces": [[0.2, 0.2, 0.08, 0.12, 0.9], [0.7, 0.25, 0.08, 0.12, 0.9]], "subject": [0.1, 0.1, 0.9, 0.9]}
    prev = None; names = []
    for k in range(12):
        mv = rn.choose_move({"size": ["medium", "wide", "close", "insert"][k % 4]}, a, 5.0, prev, 1.55, cam)
        assert mv[0] != prev or mv[0] == "hold", f"the same move twice: {mv[0]}"
        for z, cx, cy in (mv[1], mv[2]):
            w = 1 / z; assert w / 2 - 1e-9 <= cx <= 1 - w / 2 + 1e-9 and 1.0 <= z <= 1.55 + 1e-9
        prev = mv[0]; names.append(mv[0])
    assert len(set(names)) >= 3, names
    xs = [rn.ease_profile(u / 100, 6.0, 0.6) for u in range(101)]
    assert abs(xs[-1] - 1) < 1e-6 and all(b >= a - 1e-9 for a, b in zip(xs, xs[1:])), "eased moves must be monotonic and land exactly"


@test
def chunks_split_only_at_cuts():
    shots = [{"start": 0, "trans": ["fade_in", .5]}, {"start": 3, "trans": ["cut", 0]}, {"start": 6, "trans": ["dissolve", .4]}, {"start": 9, "trans": ["cut", 0]}]
    parts = rn.chunks(shots, 360, 30, 3)
    cut_frames = {0, 90, 270}
    assert all(p[0] in cut_frames for p in parts), parts
    assert parts[-1][1] == 360 and sum(b - a for a, b in parts) == 360


@test
def clips_cost_gate():
    r = subprocess.run([PY, str(TOOLS / "vyapaar_clips.py"), str(JEW), "make"], capture_output=True, text=True)
    assert "paid step" in r.stdout and "Nothing was generated" in r.stdout, r.stdout
    r2 = subprocess.run([PY, str(TOOLS / "vyapaar_clips.py"), str(JEW), "--seconds", "3"], capture_output=True, text=True)
    assert "--approve-cost" in r2.stdout or "approve" in r2.stdout.lower(), r2.stdout + r2.stderr


@test
def line_boil_untouched():
    out = subprocess.run(["git", "status", "--porcelain", "skills/line-boil", "line-boil/engine"], cwd=ROOT, capture_output=True, text=True).stdout
    assert not out.strip(), f"line-boil files changed: {out}"


@test
def steps_never_use_a_voice_from_an_older_script():
    """a stale voice.mp3 (made for another script) must never be picked: the free voice that matches the script is used, and with none the step stops"""
    import vyapaar_steps as st
    d = tmp_project(True); n = len(json.loads((d / "script.json").read_text(encoding="utf-8"))["lines"])
    (d / "voice.mp3").write_bytes(b"x"); (d / "voice-lines.json").write_text(json.dumps([{"i": 0, "start": 0, "end": 1}] * (n - 5)), encoding="utf-8")     # an older, shorter script
    try: st.voice_args(d); raise AssertionError("a stale voice was accepted")
    except SystemExit: pass
    (d / "preview-local.mp3").write_bytes(b"x"); (d / "preview-local-lines.json").write_text(json.dumps([{"i": i, "start": i, "end": i + 1} for i in range(n)]), encoding="utf-8")
    args, kind = st.voice_args(d); assert kind.startswith("free") and "preview-local.mp3" in args, (args, kind)
    (d / "voice-lines.json").write_text(json.dumps([{"i": i, "start": i, "end": i + 1} for i in range(n)]), encoding="utf-8")
    assert st.voice_args(d)[1] == "Sarvam", "a voice that matches the script wins"


@test
def steps_sample_covers_hook_a_graphic_and_the_ending():
    import vyapaar_steps as st
    d = tmp_project(True); n = len(json.loads((d / "script.json").read_text(encoding="utf-8"))["lines"])
    segs = [tuple(map(int, x.split("-"))) for x in st.sample_segments(d).split(",")]
    assert segs[0][0] == 1 and segs[-1][1] == n and all(a <= b for a, b in segs) and all(segs[i][1] < segs[i + 1][0] for i in range(len(segs) - 1)), segs
    plan = json.loads((d / "visual-plan.json").read_text(encoding="utf-8"))
    gl = [s["lines"][0] for s in plan["shots"] if s.get("kind") == "graphic"]
    assert any(segs[1][0] <= g <= segs[1][1] for g in gl), "the middle stretch must contain a graphic"


@test
def steps_write_an_srt_that_is_a_separate_file():
    import vyapaar_steps as st
    d = tmp_project(True); n = len(json.loads((d / "script.json").read_text(encoding="utf-8"))["lines"])
    (d / "preview-local-lines.json").write_text(json.dumps([{"i": i, "start": i * 3.0, "end": i * 3.0 + 2.5} for i in range(n)]), encoding="utf-8")
    st.write_srt(d, "preview-local-lines.json"); t = (d / f"{d.name}.srt").read_text(encoding="utf-8")
    assert t.startswith("1" + chr(10) + "00:00:00,000 --> ") and t.count("-->") >= n
    assert all(len(c.split()) <= 8 for blk in t.split(chr(10) * 2) if blk for c in blk.splitlines()[2:]), "at most 8 words a cue"


@test
def review_status_lists_pictures_waiting_with_their_script_line():
    d = tmp_project(True, images=[6]); vv.build(d)
    idx = json.loads((d / "images-index.json").read_text(encoding="utf-8")); n = next(e["n"] for e in idx if e["type"] == "scene")
    shutil.copy(next((JEW / "images").glob("001.*")), d / "images" / f"{n:03d}.png")
    r = subprocess.run([PY, str(TOOLS / "vyapaar_review.py"), str(d), "status"], capture_output=True, text=True, encoding="utf-8")
    st = json.loads(next(l for l in reversed(r.stdout.splitlines()) if l.startswith("{")))
    it = next(i for i in st["items"] if i["n"] == n)
    assert st["counts"]["pending"] >= 1 and not st["gate_open"] and it["text"], st
    assert any("not measured yet" in f[1] for f in it["flags"]), "an unmeasured picture must say so"


@test
def steps_save_each_finished_video_as_the_next_v_number():
    import vyapaar_steps as st
    d = tmp_project(False); (d / "video.mp4").write_bytes(b"first")
    assert st.publish_version(d).name == "v1.mp4"
    (d / "video.mp4").unlink(); (d / "video.mp4").write_bytes(b"second render")
    assert st.publish_version(d).name == "v2.mp4" and (d / "v1.mp4").read_bytes() == b"first", "an earlier final is never overwritten"
    (d / "v10.mp4").write_bytes(b"x"); assert st.publish_version(d).name == "v11.mp4", "numbers are compared as numbers"


@test
def cast_splits_a_line_into_the_narrators_words_and_the_persons():
    import vyapaar_cast as vc
    line = {"hi": "रमेश जी हंसकर कहते हैं, धनतेरस के एक दिन में तीस लाख बिका है, बेटा।", "say": {"who": "ramesh", "from": "धनतेरस के एक दिन"}}
    assert vc.parts(line) == [("narrator", "रमेश जी हंसकर कहते हैं,"), ("ramesh", "धनतेरस के एक दिन में तीस लाख बिका है, बेटा।")]
    assert vc.parts({"hi": "पापा, तिजोरी में दो करोड़ लगे हैं।", "say": {"who": "ankit"}}) == [("ankit", "पापा, तिजोरी में दो करोड़ लगे हैं।")], "no `from`: the whole line"
    both = {"hi": "वो बोले, ठीक है। फिर चुप हो गए।", "say": {"who": "goyal", "from": "ठीक है", "to": "फिर चुप"}}
    assert [w for w, _ in vc.parts(both)] == ["narrator", "goyal", "narrator"], "`to` hands the rest back to the narrator"
    assert vc.parts({"hi": "सिर्फ narration।"}) == [("narrator", "सिर्फ narration।")]
    try: vc.parts({"hi": "कुछ और।", "say": {"who": "x", "from": "यह है ही नहीं"}}); raise AssertionError("a missing `from` was accepted")
    except ValueError: pass
    assert vc.validate(JEW) == [], vc.validate(JEW)


@test
def cast_file_with_a_byte_order_mark_still_loads_and_a_broken_one_is_refused():
    import vyapaar_cast as vc
    d = tmp_project(False); (d / "voice-cast.json").write_bytes(b"\xef\xbb\xbf" + json.dumps({"ramesh": {"sarvam": {"speaker": "rahul"}}}).encode())
    assert vc.load(d)["ramesh"]["sarvam"]["speaker"] == "rahul"
    (d / "voice-cast.json").write_text("{not json", encoding="utf-8")
    try: vc.load(d); raise AssertionError("a broken cast file was ignored")
    except SystemExit: pass


@test
def sarvam_voice_gives_each_person_their_own_speaker_and_keeps_line_times():
    """the Sarvam tool with a fake voice (no call, no cost): a person's words are spoken with their speaker, the narrator's with the narrator's, and every line gets a time"""
    import vyapaar_voice as vv_
    d = tmp_project(False); shutil.copy(JEW / "voice-cast.json", d / "voice-cast.json")
    calls = []
    def fake(text, cfg=None):
        calls.append((text, dict(cfg or {})))
        out = Path(tempfile.mkdtemp()) / "f.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=f=220:d={max(0.6, len(text) * 0.05):.2f}", "-ar", "24000", "-ac", "1", str(out)], check=True)
        return out.read_bytes()
    vv_.speak = fake
    old = sys.argv; sys.argv = ["vyapaar_voice.py", str(d)]
    try: vv_.main()
    finally: sys.argv = old
    lines = json.loads((d / "script.json").read_text(encoding="utf-8"))["lines"]; vl = json.loads((d / "voice-lines.json").read_text(encoding="utf-8"))
    assert len(vl) == len(lines) and all(vl[i]["start"] < vl[i]["end"] <= vl[i + 1]["start"] + 1e-6 for i in range(len(vl) - 1)), "every line has an ordered time"
    assert vl[22]["who"] == ["goyal", "narrator"] and vl[0]["who"] == ["narrator"], (vl[22], vl[0])
    quote = lines[22]["hi"][lines[22]["hi"].index("सेठ जी, कल"):]
    got = next(c for c in calls if c[0].startswith(quote)); assert got[1].get("speaker") == "kabir" and got[1].get("pace") == 0.98, got[1]
    assert not any("वो कहते हैं," in c[0] and c[1].get("speaker") == "kabir" for c in calls), "the narrator's tag is never read in the person's voice"
    assert (d / f"{d.name}.srt").exists()


if __name__ == "__main__":
    for name, st, why in results: print(f"{st:4s} {name}" + (f"\n     {why}" if why else ""))
    bad = [r for r in results if r[1] != "ok"]
    print(f"\n{len(results) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
