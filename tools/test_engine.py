"""Tests for the 16:9 (long video) support in the line-boil engine: formats, pages, chapters, chunked word timing, scaffolding.

    .venv\\Scripts\\python tools\\test_engine.py            fast checks (no voice, no browser)
    set BEAN_SLOW=1 & <kit python> tools\\test_engine.py    also builds the shipped wide example end to end (about 2 minutes)
The slow part needs the animation kit's Python (it has numpy, Kokoro and Playwright).
"""
import importlib.util, json, os, subprocess, sys, tempfile, types
from pathlib import Path

ENGINE = Path.home() / ".claude" / "skills" / "line-boil" / "engine"
spec = importlib.util.spec_from_file_location("lbbuild", ENGINE / "build.py")
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)
TMP = Path(tempfile.mkdtemp(prefix="lb-test-"))
ok = lambda name: print("  ok  ", name)


def test_formats():
    assert lb.FORMATS["wide"]["canvas"] == (1920, 1080) and lb.FORMATS["wide"]["world"] == (960, 540) and lb.FORMATS["wide"]["thumb"] == (1280, 720)
    a, b, c = TMP / "a", TMP / "b", TMP / "c"
    for d in (a, b, c): d.mkdir()
    (a / "project.json").write_text('{"format": "wide"}'); (b / "project.json").write_text("{nope")
    assert lb.fmt_name(a) == "wide" and lb.fmt_name(b) == "short" and lb.fmt_name(c) == "short" and lb.fmt(a)["canvas"] == (1920, 1080)
    ok("formats: wide only when project.json says so; damaged or missing means a Short")


def test_pages():
    wide, short = TMP / "w", TMP / "s"
    for d in (wide, short): (d / "web" / "shots").mkdir(parents=True)
    (wide / "project.json").write_text('{"format": "wide"}')
    for n in ("ch02", "ch10", "ch01"): (wide / "web" / "shots" / f"{n}.js").write_text("//")
    lb.write_pages(wide)
    h = (wide / "web" / "index.html").read_text()
    assert "window.WORLD = [960, 540]" in h and 'width="1920" height="1080"' in h and "aspect-ratio: 16 / 9" in h
    order = [h.index(f'shots/{n}.js') for n in ("ch01", "ch02", "ch10")]
    assert order == sorted(order) and h.index('src="shots.js"') < order[0], "chapter files load in name order after shots.js"
    assert h.index("window.WORLD") < h.index('src="engine/ink.js"'), "the world size is set before ink.js reads it"
    t = (wide / "web" / "thumb.html").read_text()
    assert "thumb.js" in t and "shots/ch01.js" not in t and "window.WORLD" in t
    lb.write_pages(short)
    assert (short / "web" / "index.html").read_text() == (ENGINE / "web" / "index.html").read_text(), "a Short's page is the template, untouched"
    assert "window.WORLD" not in (short / "web" / "thumb.html").read_text()
    ok("pages: wide sets the world and the canvas, chapter files load in order; a Short's page is unchanged")


def test_new_wide():
    d = TMP / "newwide"
    lb.cmd_new(types.SimpleNamespace(project=str(d), example=False, wide=True))
    assert json.loads((d / "project.json").read_text())["format"] == "wide" and (d / "web" / "shots").is_dir()
    assert (d / "web" / "cast.example.js").exists() and (d / "web" / "shots.example.js").exists() and json.loads((d / "chapters.json").read_text())
    assert "window.WORLD" in (d / "web" / "index.html").read_text()
    s = TMP / "newshort"
    lb.cmd_new(types.SimpleNamespace(project=str(s), example=False, wide=False))
    assert not (s / "project.json").exists() and not (s / "chapters.json").exists()
    ok("new --wide: project.json, web/shots/, chapters.json, examples; a Short project gets none of them")


def chapters_project(name, words, chapters):
    d = TMP / name; (d / "audio").mkdir(parents=True)
    (d / "chapters.json").write_text(json.dumps(chapters)); (d / "audio" / "words.json").write_text(json.dumps(words))
    return d


def run_chapters(d):
    try:
        lb.cmd_chapters(types.SimpleNamespace(project=str(d))); return None
    except SystemExit as e:
        return str(e.code)


def test_chapters():
    words = [{"w": "w", "s": i * 1.0, "e": i * 1.0 + 0.8, "line": i // 10} for i in range(100)]     # 10 sentences of 10 s
    good = chapters_project("c1", words, [{"title": "One", "line": 0}, {"title": "Two", "line": 4}, {"title": "Three", "line": 7}])
    assert run_chapters(good) is None
    assert (good / "c1-chapters.txt").read_text() == "0:00 One\n0:40 Two\n1:10 Three\n"
    short = chapters_project("c2", words, [{"title": "A", "line": 0}, {"title": "B", "line": 1}])
    assert "at least 3" in run_chapters(short)
    tiny = chapters_project("c3", words, [{"title": "A", "line": 0}, {"title": "B", "line": 1}, {"title": "C", "line": 1}, {"title": "D", "line": 5}])
    err = run_chapters(tiny); assert "NOT VALID" in err and "is not in order" in err or "only" in err, err
    late = chapters_project("c4", words, [{"title": "Intro", "line": 1}, {"title": "B", "line": 4}, {"title": "C", "line": 7}])
    assert run_chapters(late) is None and (late / "c4-chapters.txt").read_text().startswith("0:00 Intro"), "the first chapter always starts at 0:00"
    bad = chapters_project("c5", words, [{"title": "A", "line": 0}, {"title": "B", "line": 4}, {"title": "C", "line": 99}])
    assert "not in script.json" in run_chapters(bad)
    assert lb.fmt_clock(65) == "1:05" and lb.fmt_clock(3725) == "1:02:05"
    ok("chapters: from real word times, 0:00 first, at least 3, at least 10 s each, clear errors")


def test_chunked_timing():
    class Res: pass
    class Stream:
        def __init__(s): s.n = 0
        def accept_waveform(s, sr, seg): s.n = len(seg)
    class Rec:
        def create_stream(s): return Stream()
        def decode_stream(s, st):
            st.result = Res(); k = max(1, int(st.n / 16000 / 0.5))      # one 'word' every half second of audio in the window
            st.result.tokens = [f" w{i}" for i in range(k)]; st.result.timestamps = [i * 0.5 for i in range(k)]
    calls = []
    class KW:
        SR = 16000
        @staticmethod
        def load(path): return [0.0] * (90 * 16000)
        @staticmethod
        def recognizer(): return Rec()
        @staticmethod
        def follow_script(heard, text): calls.append(text); return [[f"s{i}", t] for i, (_, t) in enumerate(heard)]
        @staticmethod
        def timings(path, text): raise AssertionError("a long voiceover must be timed in chunks")
    d = TMP / "chunk"; (d / "audio").mkdir(parents=True)
    (d / "audio" / "sentences.json").write_text(json.dumps([{"line": 0, "s": 0.0, "e": 30.0}, {"line": 1, "s": 30.3, "e": 60.0}, {"line": 2, "s": 60.3, "e": 89.9}]))
    ws = lb.word_timings(KW, d, ["one one", "two two", "three three"])
    assert len(calls) == 3 and calls[1] == "two two", "three windows, each timed against its own text"
    s = [w["s"] for w in ws]
    assert s == sorted(s) and s[0] == 0.0 and abs(s[60] - (30.3 - 0.15)) < 0.01, "each window's times are shifted to where it sits in the whole"
    assert all(w["e"] - w["s"] <= 1.2 + 1e-6 for w in ws) and abs(ws[-1]["e"] - 90.0) < 1.3
    long_no_marks = TMP / "nomarks"; (long_no_marks / "audio").mkdir(parents=True)
    KW.load = staticmethod(lambda path: [0.0] * (400 * 16000))
    try: lb.word_timings(KW, long_no_marks, ["x"]); assert False
    except SystemExit as e: assert "sentence markers" in str(e)
    ok("word timing: windows of about 40 s cut at sentence ends and joined; a long recording without markers is refused clearly")


def test_moving_average():
    try: import numpy as np
    except ImportError: print("  skip  moving average (numpy not in this Python)"); return
    sys.path.insert(0, str(ENGINE / "tools"))
    import sound, inspect
    src = inspect.getsource(sound.mix); assert "np.convolve(" not in src and "np.cumsum" in src
    rng = np.random.default_rng(2); env = np.abs(rng.normal(size=20000)); k = 3840
    old = np.convolve(env, np.ones(k) / k, mode="same")
    cs = np.concatenate(([0.0], np.cumsum(env))); idx = np.arange(len(env) + k - 1)
    new = ((cs[np.minimum(idx + 1, len(env))] - cs[np.maximum(idx + 1 - k, 0)]) / k)[(k - 1) // 2:(k - 1) // 2 + len(env)]
    assert float(np.abs(old - new).max()) < 1e-9
    ok("sound: the ducking filter is linear in length and equals the old one")


def test_shorts_unchanged():
    src = (ENGINE / "web" / "props.js").read_text()
    for needle in ("[[6, 14], [W / 2, 10], [W - 6, 13]]", "[[13, 6], [10, H / 2], [14, H - 6]]"): assert needle in src
    ink = (ENGINE / "web" / "ink.js").read_text()
    assert "|| [540, 960]" in ink and "|| [1080, 1920]" in ink, "with no WORLD the engine is a Short, exactly as before"
    ok("engine: defaults are the Short's 540x960 world and 1080x1920 canvas")


def test_captions_and_music_defaults():
    main = (ENGINE / "web" / "main.js").read_text(encoding="utf-8")
    assert "WIDE ? { on: false" in main and "{ on: true, y: 500" in main, "long videos have no burned-in captions by default; Shorts keep theirs"
    assert "function musicMood(" in main and "'music:' + mood" in main
    for f in ("web/sets.js", "tools/sound.py"): assert (ENGINE / f).exists()
    pages = TMP / "pg"; (pages / "web").mkdir(parents=True); lb.write_pages(pages)
    assert "engine/sets.js" in (pages / "web" / "index.html").read_text(), "the scene kit is loaded on every page"
    assert "sets.js" in (ENGINE / "build.py").read_text() and "'sets.js'" in (ENGINE / "build.py").read_text()
    sets = (ENGINE / "web" / "sets.js").read_text(encoding="utf-8")
    for name in ("setSunny", "setNight", "setRoom", "setStreet", "setStage", "setDesk", "setSpace", "setBlank", "setScene"): assert f"function {name}(" in sets, name
    ok("defaults: no burned-in captions in a long video, musicMood and the eight sets exist and are loaded")


def test_music_moods():
    try: import numpy as np
    except ImportError: print("  skip  music moods (numpy not in this Python)"); return
    sys.path.insert(0, str(ENGINE / "tools"))
    import sound
    assert set(sound.MOOD_NAMES) >= {"curious", "playful", "upbeat", "calm", "serious", "tense", "mystery", "triumphant", "silent"}
    ref = sound._rms(sound.music(20))
    cent = {}
    for name in sound.MOODS:
        x = sound._mood_section(name, 12, 5)
        assert not np.isnan(x).any() and sound._rms(x) > 0, name
        sec = x[int(2 * sound.SR):int(10 * sound.SR)]; S = np.abs(np.fft.rfft(sec * np.hanning(len(sec)))); f = np.fft.rfftfreq(len(sec), 1 / sound.SR)
        cent[name] = float((S * f).sum() / S.sum())
    assert max(cent.values()) > 2.5 * min(cent.values()), cent       # the moods really sound different (tense is bright, serious is low)
    plan = [{"t": 0, "mood": "calm"}, {"t": 6, "mood": "silent"}, {"t": 9, "mood": "tense"}, {"t": 14, "mood": "no-such-mood"}]
    y = sound.music_plan(20, plan)
    seg = lambda a, b: sound._rms(y[int(a * sound.SR):int(b * sound.SR)])
    assert len(y) == 20 * sound.SR and seg(8.0, 8.9) < 0.02 * seg(2, 5) and seg(10, 13) > 0.5 * ref and seg(15.5, 19) > 0.5 * ref, "silent is silent, an unknown mood falls back to curious"
    assert 0.6 * ref < seg(2, 5) < 1.4 * ref and 0.6 * ref < seg(10, 13) < 1.4 * ref, "moods are balanced to the same loudness"
    assert sound.music_plan(10, [{"t": 0, "mood": "silent"}]).max() == 0
    # the default path (no plan) is the old single underscore
    d = TMP / "mixd"; (d / "audio").mkdir(parents=True)
    sound.write_wav(d / "audio" / "vo.wav", np.zeros(sound.SR * 4)); (d / "cues.json").write_text(json.dumps([{"t": 1, "kind": "pop"}, {"t": 0, "kind": "music:tense"}]))
    assert sound.mix(d, 4) == 1, "music cues are not counted as sound effects"
    ok("music: nine moods, balanced loudness, distinct sound, silence and unknown-mood handling; music cues are read from cues.json")


def slow_end_to_end():
    """the shipped wide example: voice, chapters, stills, thumbnail, all at the right sizes"""
    kitpy = Path(sys.executable)
    d = TMP / "e2e"
    env = dict(os.environ, LINEBOIL_OUT=str(TMP))
    run = lambda *a: subprocess.run([str(kitpy), str(ENGINE / "build.py"), *a], capture_output=True, text=True, env=env, timeout=600)
    assert run("new", str(d), "--wide", "--example").returncode == 0
    r = run("voice", str(d), "--target", "40"); assert r.returncode == 0 and "TARGET 40.0s: OK" in r.stdout, r.stdout[-300:]
    r = run("chapters", str(d)); assert r.returncode == 0 and "3 chapters, valid" in r.stdout, r.stdout
    r = run("check", str(d)); assert r.returncode == 0 and '"shots":[[0' in r.stdout, r.stdout[-300:]
    r = run("stills", str(d), "3,20,35"); assert r.returncode == 0 and (d / "stills" / "sheet.jpg").exists(), r.stderr[-300:]
    w = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(d / "stills" / "s_3.00.jpg")], capture_output=True, text=True).stdout.strip()
    assert w == "960,540", w
    (d / "web" / "thumb.js").write_text("CAP.on = false;\nshot(0, { draw() { band(BLUE, 0, 540, 1); ground(450, 5, { fill: PAPER }); bigWord('WHY?', 480, 200, 120, YEL, 9); drawChar(MO, poseAt([{ t: 0, x: 480, y: 450, size: 1.3, expr: 'shocked' }], 0)); } });\n")
    r = run("thumb", str(d)); assert r.returncode == 0 and "1280x720" in r.stdout and (d / "stills" / "thumb-crops.png").exists(), r.stdout + r.stderr
    t = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(d / "e2e-thumbnail.png")], capture_output=True, text=True).stdout.strip()
    assert t == "1280,720" and (d / "e2e-thumbnail.png").stat().st_size < 2_000_000, t
    empty = TMP / "emptyvid"
    assert run("new", str(empty), "--wide").returncode == 0
    (empty / "audio").mkdir(exist_ok=True); (empty / "web" / "words.js").write_text("const WORDS = []; const END = 4;\n")
    r = run("check", str(empty)); assert r.returncode != 0 and "no shots" in (r.stdout + r.stderr), r.stdout
    ok("end to end (slow): the wide example voices, times, renders 960x540 stills, makes a 1280x720 thumbnail; an empty video is refused")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"): fn()
    if os.environ.get("BEAN_SLOW"): slow_end_to_end()
    print("all passed")
