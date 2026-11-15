"""Tests for the Decoding Vyapaar visual pipeline. Plain Python, no test framework needed:
    python tools/tests/test_vyapaar_pipeline.py
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
    assert all(len(vv.shot_prompt(s, plan, b).split()) < 290 for s in plan["shots"] if s.get("action"))


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


if __name__ == "__main__":
    for name, st, why in results: print(f"{st:4s} {name}" + (f"\n     {why}" if why else ""))
    bad = [r for r in results if r[1] != "ok"]
    print(f"\n{len(results) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
