#!/usr/bin/env python3
"""line-boil: build a hand-drawn line-boil cartoon reel (1080x1920, 24 fps on twos) from a project folder.

    python build.py new    <project> [--example]          make a project (the example is "Why is the sky blue?")
    python build.py voice  <project> [--voice af_heart] [--speed 1.0] [--file take.wav] [--target SECONDS]
                                                         voiceover from script.json + word times -> web/words.js
    python build.py check  <project>                      load the page, list shots and report errors
    python build.py stills <project> 1.5,4.2,9            stills/s_<t>.jpg at half size, to look at before a full render
    python build.py video  <project> [--workers 4]        render, mix the sound, write <project>/<name>.mp4
    python build.py sheet  <project>                      a contact sheet of the finished video -> sheet.jpg
    python build.py thumb  <project>                      render web/thumb.js -> <project>/<name>-thumbnail.png (1080x1920; 1280x720 for wide)
    python build.py new    <project> --wide               a long video: 16:9, 1920x1080, one web/shots/chNN.js file per chapter
    python build.py chapters <project>                    YouTube chapters from chapters.json and the real word times -> <name>-chapters.txt

The voice (Kokoro), word timing (Parakeet) and Playwright come from the animation-skills kit; this script
finds it and re-runs itself with the kit's Python when it needs to.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
# where projects live: a bare project name (no folder in it) goes here
OUT = Path(os.environ.get('LINEBOIL_OUT', r'C:\Users\praty\youtube\line-boil'))


def proj_path(name):
    p = Path(name)
    if not p.is_absolute() and len(p.parts) == 1:
        return (OUT / p).resolve()
    return p.resolve()
FPS = 24
# the two formats. A project is 'short' (9:16) unless its project.json says {"format": "wide"} (16:9, long video).
FORMATS = {
    'short': dict(world=(540, 960), canvas=(1080, 1920), thumb=(1080, 1920), tile=(270, 480)),
    'wide': dict(world=(960, 540), canvas=(1920, 1080), thumb=(1280, 720), tile=(480, 270)),
}


def fmt_name(proj):
    try:
        return json.loads((Path(proj) / 'project.json').read_text(encoding='utf-8')).get('format', 'short')
    except Exception:
        return 'short'


def fmt(proj):
    return FORMATS.get(fmt_name(proj), FORMATS['short'])


# ---------- the kit ----------
def find_kit():
    cands = []
    if os.environ.get('LINEBOIL_KIT'):
        cands.append(os.environ['LINEBOIL_KIT'])
    plug = Path.home() / '.claude' / 'plugins'
    cands += sorted(glob.glob(str(plug / 'cache' / 'claude-animation-skills' / '*' / '*' / 'kit')), reverse=True)
    cands += [str(plug / 'marketplaces' / 'claude-animation-skills' / 'kit')]
    for c in cands:
        if c and (Path(c) / 'node_modules' / 'playwright').exists():
            return Path(c)
    sys.exit('The animation-skills kit was not found (it supplies Playwright, the Kokoro voice and word timing).\n'
             'Install the claude-animation-skills plugin and run  bash <kit>/setup.sh --voice  once,\n'
             'or set LINEBOIL_KIT to a folder that has node_modules/playwright and models/.')


def kit_python(kit):
    for p in (kit / '.venv' / 'Scripts' / 'python.exe', kit / '.venv' / 'bin' / 'python'):
        if p.exists():
            return p
    return None


def ensure_kit_python(kit):
    """re-run under the kit's venv when numpy / kokoro / sherpa are not importable here"""
    try:
        import numpy  # noqa: F401
        import soundfile  # noqa: F401
        return
    except ImportError:
        pass
    py = kit_python(kit)
    if not py:
        sys.exit(f'The kit has no voice tools yet: run  bash "{kit}/setup.sh" --voice')
    if Path(sys.executable).resolve() == py.resolve():
        sys.exit(f'numpy/soundfile are missing from the kit venv: run  bash "{kit}/setup.sh" --voice')
    sys.exit(subprocess.run([str(py), __file__] + sys.argv[1:]).returncode)


def node(kit, *args, **kw):
    cw, ch = fmt(args[0])['canvas'] if args else FORMATS['short']['canvas']
    env = dict(os.environ, NODE_PATH=str(kit / 'node_modules'), LB_W=str(cw), LB_H=str(ch))
    return subprocess.run(['node', str(ENGINE / 'tools' / 'render.js'), *map(str, args)], env=env, **kw)


def write_pages(proj):
    """index.html (the video) and thumb.html (the thumbnail) from the engine's template, for the project's format.
    A long video lists web/shots/*.js in name order after shots.js, so each chapter can be its own file."""
    web = proj / 'web'
    html = (ENGINE / 'web' / 'index.html').read_text(encoding='utf-8')
    if fmt_name(proj) == 'wide':
        (ww, wh), (cw, ch) = FORMATS['wide']['world'], FORMATS['wide']['canvas']
        html = html.replace('<canvas id="c" width="1080" height="1920"></canvas>', f'<canvas id="c" width="{cw}" height="{ch}"></canvas>')
        html = html.replace('<script src="words.js"></script>', f'<script>window.WORLD = [{ww}, {wh}]; window.CANVAS = [{cw}, {ch}];</script>\n<script src="words.js"></script>')
        html = html.replace('canvas { height: 100vh; width: auto; aspect-ratio: 9 / 16; display: block; }',
                            'canvas { width: 100vw; max-height: 100vh; height: auto; aspect-ratio: 16 / 9; display: block; }')
    thumb = html.replace('<script src="shots.js"></script>', '<script src="thumb.js"></script>')
    chapters = sorted((web / 'shots').glob('*.js')) if (web / 'shots').is_dir() else []
    html = html.replace('<script src="shots.js"></script>', '<script src="shots.js"></script>' + ''.join(f'\n<script src="shots/{f.name}"></script>' for f in chapters))
    (web / 'index.html').write_text(html, encoding='utf-8')
    (web / 'thumb.html').write_text(thumb, encoding='utf-8')


def sync_engine(proj):
    """copy the engine's page and scripts into the project so it always renders with the current engine"""
    web = proj / 'web'
    (web / 'engine').mkdir(parents=True, exist_ok=True)
    for f in ('ink.js', 'props.js', 'sets.js', 'rig.js', 'main.js', 'Poppins-Bold.ttf'):
        shutil.copy(ENGINE / 'web' / f, web / 'engine' / f)
    write_pages(proj)
    for f, stub in (('cast.js', '// characters and topic props\n'), ('shots.js', '// shots\n'),
                    ('words.js', 'const WORDS = []; const END = 4;\n')):
        if not (web / f).exists():
            (web / f).write_text(stub, encoding='utf-8')


# ---------- commands ----------
def cmd_new(a):
    proj = proj_path(a.project)
    if proj.exists() and any(proj.iterdir()):
        sys.exit(f'{proj} already exists and is not empty')
    wide = getattr(a, 'wide', False)
    ex = ENGINE / ('example-wide' if wide else 'example')
    if wide:
        (proj / 'web' / 'shots').mkdir(parents=True, exist_ok=True)       # one chNN.js per chapter goes here
        (proj / 'project.json').write_text('{"format": "wide"}\n', encoding='utf-8')
    if a.example:
        shutil.copytree(ex, proj, dirs_exist_ok=True)
    else:
        (proj / 'web').mkdir(parents=True, exist_ok=True)
        (proj / 'script.json').write_text('[\n  "First sentence of the voiceover.",\n  "Second sentence."\n]\n', encoding='utf-8')
        shutil.copy(ex / 'web' / 'cast.js', proj / 'web' / 'cast.example.js')
        shutil.copy(ex / 'web' / 'shots' / 'ch01.js' if wide else ex / 'web' / 'shots.js', proj / 'web' / 'shots.example.js')
        if wide:
            (proj / 'chapters.json').write_text(json.dumps([{'title': 'Intro', 'line': 0}], indent=2) + '\n', encoding='utf-8')
    sync_engine(proj)
    print(f'project ready: {proj}')


def tts(proj, voice, speed, append=False):
    """Kokoro voiceover of script.json -> audio/vo.wav + audio/sentences.json. With append, the existing take is kept sample for sample
    and only the sentences after it are voiced (so every earlier word time stays put). Returns the index of the first new sentence."""
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro, EspeakConfig
    import espeakng_loader
    kit = find_kit()
    data = espeakng_loader.get_data_path()
    if len(data) > 100:   # espeak-ng fails on long data paths
        short = os.path.join(tempfile.gettempdir(), 'kokoro-espeak-ng-data')
        if not os.path.exists(os.path.join(short, 'phontab')):
            shutil.rmtree(short, ignore_errors=True)
            shutil.copytree(data, short)
        data = short
    k = Kokoro(str(kit / 'models' / 'kokoro-v1.0.onnx'), str(kit / 'models' / 'voices-v1.0.bin'),
               espeak_config=EspeakConfig(lib_path=espeakng_loader.get_library_path(), data_path=data))
    lines = json.loads((proj / 'script.json').read_text(encoding='utf-8'))
    out, sr, pos, bounds, first = [], 24000, 0, [], 0
    if append:
        old, sr = sf.read(str(proj / 'audio' / 'vo.wav'), dtype='float32')
        bounds = json.loads((proj / 'audio' / 'sentences.json').read_text(encoding='utf-8'))
        first = len(bounds)
        out.append(old)
        pos = len(old)
    for i, line in enumerate(lines):
        if i < first:
            continue
        # Kokoro reads "3 p.m." as two letters with a pause between them: say "PM" / "AM" so it runs together (the script text, captions and word lookups stay as written)
        said = re.sub(r'\b([ap])\.\s?m\b\.?', lambda m: m.group(1).upper() + 'M', line, flags=re.I)
        samples, sr = k.create(said, voice=voice, speed=speed, lang='en-us')
        idx = np.where(np.abs(samples) > 0.01)[0]
        samples = samples[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)].astype('float32')
        out.append(samples)
        bounds.append({'line': i, 's': round(pos / sr, 3), 'e': round((pos + len(samples)) / sr, 3)})
        pos += len(samples)
        gap = 0.16 + (0.14 if i == 0 or line.rstrip().endswith(('?', '!')) else 0)
        out.append(np.zeros(int(gap * sr), dtype='float32'))
        pos += len(out[-1])
    sf.write(str(proj / 'audio' / 'vo.wav'), np.concatenate(out), sr)
    (proj / 'audio' / 'sentences.json').write_text(json.dumps(bounds), encoding='utf-8')   # lets the word timing run in chunks
    return first


def word_timings(kitwords, proj, lines, first=0, prefix=None):
    """word start/end times for the voiceover. A long voiceover is timed in windows of about 40 s cut at sentence ends (the model
    fails past roughly 6.5 minutes), then joined. Without sentence bounds (your own recording) it is timed in one go.
    first/prefix (voice --append): only the sentences from `first` on are timed; `prefix` holds the earlier words, kept as they were."""
    wav = str(proj / 'audio' / 'vo.wav')
    sent = proj / 'audio' / 'sentences.json'
    a = kitwords.load(wav)
    dur = len(a) / kitwords.SR
    bounds = json.loads(sent.read_text(encoding='utf-8')) if sent.exists() else []
    if first and len(bounds) == len(lines):
        bounds = bounds[first:]
    elif dur <= 45 or len(bounds) != len(lines):
        if dur > 360:
            sys.exit(f'This voiceover is {dur / 60:.1f} minutes and has no sentence markers, so it cannot be timed in one go. '
                     'Let build.py make the voice (leave out --file), or record it in sections.')
        return kitwords.timings(wav, ' '.join(lines))
    rec = kitwords.recognizer()
    groups, cur = [], []
    for b in bounds:
        if cur and b['e'] - cur[0]['s'] > 40:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    heard_all = []
    for g in groups:
        t0, t1 = max(0.0, g[0]['s'] - 0.15), min(dur, g[-1]['e'] + 0.15)
        st = rec.create_stream()
        st.accept_waveform(kitwords.SR, a[int(t0 * kitwords.SR): int(t1 * kitwords.SR)])
        rec.decode_stream(st)
        words = []
        for tok, ts in zip(st.result.tokens, st.result.timestamps):
            if tok.startswith((' ', '\u2581')) or not words:
                words.append([tok.strip(' \u2581'), float(ts)])
            else:
                words[-1][0] += tok
        heard = [w for w in words if w[0]]
        for w, t in kitwords.follow_script(heard, ' '.join(lines[b['line']] for b in g)):
            heard_all.append([w, t + t0])
    out = []
    for i, (w, t) in enumerate(heard_all):
        e = heard_all[i + 1][1] if i + 1 < len(heard_all) else dur
        out.append({'w': w, 's': round(t, 3), 'e': round(min(e, t + 1.2), 3)})
    return (prefix or []) + out


def cmd_voice(a):
    kit = find_kit()
    ensure_kit_python(kit)
    proj = proj_path(a.project)
    (proj / 'audio').mkdir(exist_ok=True)
    first, prefix = 0, None
    if a.append:   # voice only the sentences added at the end of script.json; the earlier take and its word times stay exactly as they were
        sent, wj = proj / 'audio' / 'sentences.json', proj / 'audio' / 'words.json'
        if a.file or not sent.exists() or not wj.exists():
            sys.exit('--append needs an earlier build.py voice take of this project (not a --file recording)')
        prefix = json.loads(wj.read_text(encoding='utf-8'))
        lines = json.loads((proj / 'script.json').read_text(encoding='utf-8'))
        n_old = len(json.loads(sent.read_text(encoding='utf-8')))
        said = {}
        for w in prefix:
            said.setdefault(w['line'], []).append(w['w'])
        changed = [i for i in range(n_old) if ' '.join(said.get(i, [])) != ' '.join(lines[i].split())] if n_old <= len(lines) else [n_old]
        if changed:
            sys.exit(f'--append: sentence {changed[0]} changed since it was voiced; run  build.py voice  without --append')
        if n_old == len(lines):
            sys.exit('--append: no new sentences at the end of script.json')
    if a.file:
        (proj / 'audio' / 'sentences.json').unlink(missing_ok=True)   # a recording has no sentence markers
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.file, '-ac', '1', '-ar', '44100', str(proj / 'audio' / 'vo.wav')], check=True)
    else:
        first = tts(proj, a.voice, a.speed, append=a.append)
    sys.path.insert(0, str(kit))
    import words as kitwords
    lines = json.loads((proj / 'script.json').read_text(encoding='utf-8'))
    ws = word_timings(kitwords, proj, lines, first=first, prefix=prefix)
    li, count = 0, 0
    per_line = [len(L.split()) for L in lines]
    for w in ws:
        while li < len(per_line) - 1 and count >= per_line[li]:
            li += 1
            count = 0
        w['line'] = li
        count += 1
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                str(proj / 'audio' / 'vo.wav')], capture_output=True, text=True, check=True).stdout)
    # main.js TAIL: breath + iris close + black after the voice (after any --hold): 1.0 + 1.0 + 0.3 for a long video, 0.6 + 0.8 + 0.2 for a Short
    end = round(dur + a.hold + (2.3 if fmt_name(proj) == 'wide' else 1.6), 2)
    (proj / 'audio' / 'words.json').write_text(json.dumps(ws, indent=0), encoding='utf-8')
    sync_engine(proj)
    # --hold N: the last pose holds N more seconds before the iris (the channel outro uses it so YouTube's end-screen elements have time)
    hold = f'  // the voice ends at {round(dur, 3)} s; +{a.hold} s held' if a.hold else ''
    (proj / 'web' / 'words.js').write_text(f'const WORDS = {json.dumps(ws)};\nconst VO_DUR = {round(dur + a.hold, 3)};{hold}\n', encoding='utf-8')
    print(f'voiceover {dur:.2f}s, video {end:.2f}s, {len(ws)} words')
    if a.target:   # the length the user asked for: say plainly whether the script hits it, so it can be trimmed or extended
        off = dur - a.target
        if abs(off) <= 4: print(f'TARGET {a.target}s: OK ({off:+.1f}s)')
        else:
            per_s = len(ws) / dur
            print(f'TARGET {a.target}s: {"TOO LONG" if off > 0 else "TOO SHORT"} by {abs(off):.1f}s. '
                  f'{"Cut" if off > 0 else "Add"} about {round(abs(off) * per_s)} words, then run voice again.')
    if len(ws) > 400:   # a long video: the sentence starts are the timeline; at('some words') finds any word from web/words.js
        print('\nsentence starts (use at("a few words") in shots for exact word times):')
        seen = set()
        for w in ws:
            if w['line'] not in seen:
                seen.add(w['line'])
                print(f"  [{w['line']}] {w['s']:7.2f}s  {lines[w['line']][:70]}")
        return
    cur = None
    for w in ws:
        if w['line'] != cur:
            cur = w['line']
            print(f'\n[{cur}] ', end='')
        print(f"{w['w']}@{w['s']:.2f}", end=' ')
    print()


def cmd_check(a):
    kit = find_kit()
    proj = proj_path(a.project)
    sync_engine(proj)
    r = node(kit, proj, 'info', capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        sys.exit(r.returncode)
    try:
        info = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return
    if not info.get('shots'):
        sys.exit('[error] the video has no shots: write web/shots.js' + (' or web/shots/chNN.js' if fmt_name(proj) == 'wide' else ''))
    shots = info['shots']
    gaps = [(a0, b0) for (a0, _, _), (b0, _, _) in zip(shots, shots[1:]) if b0 - a0 > 20]
    if gaps:
        print('[warn] shots longer than 20 s (a long video needs a new picture at least every 6 to 12 s): ' + ', '.join(f'{a0:.0f}s' for a0, _ in gaps))
    if fmt_name(proj) == 'wide':   # the music should follow the script: say so when it does not
        tmp = proj / 'cues.check.json'
        node(kit, proj, 'cues', tmp, capture_output=True, text=True)
        try:
            cues = json.loads(tmp.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            cues = []
        finally:
            tmp.unlink(missing_ok=True)
        moods = [c['kind'][6:] for c in cues if str(c.get('kind', '')).startswith('music:')]
        distinct = {m for m in moods if m != 'silent'}
        if not moods:
            print('[warn] no musicMood() calls: the whole video plays one tune. Plan a mood per chapter (see "The scene and sound plan" in line-boil-wide/references/wide.md)')
        elif len(distinct) < 3 and info.get('seconds', 0) > 240:
            print(f'[warn] only {len(distinct)} different music mood(s) in {info["seconds"] / 60:.0f} minutes; aim for at least 4 that follow the script')


def cmd_stills(a):
    kit = find_kit()
    proj = proj_path(a.project)
    sync_engine(proj)
    r = node(kit, proj, 'stills', a.times, a.scale)
    if r.returncode == 0:
        # one contact sheet of all the stills: reading ONE image is far cheaper than reading ten
        files = [proj / 'stills' / f's_{float(t):.2f}.jpg' for t in a.times.split(',')]
        files = [f for f in files if f.exists()]
        if len(files) > 1:
            tw, th = fmt(proj)['tile']
            cols = min(4 if th > tw else 3, len(files))
            cmd = ['ffmpeg', '-v', 'error', '-y']
            for f in files: cmd += ['-i', str(f)]
            graph = ''.join(f'[{i}:v]scale={tw}:-1[s{i}];' for i in range(len(files))) + ''.join(f'[s{i}]' for i in range(len(files))) + f'xstack=inputs={len(files)}:fill=0xfffaf0:layout=' + \
                '|'.join(f'{(i % cols) * tw}_{(i // cols) * th}' for i in range(len(files))) + '[o]'
            subprocess.run(cmd + ['-filter_complex', graph, '-map', '[o]', str(proj / 'stills' / 'sheet.jpg')], check=False)
            print(f"sheet: {proj / 'stills' / 'sheet.jpg'}  (left to right, top to bottom: {', '.join(a.times.split(','))} s)")
    sys.exit(r.returncode)


def cmd_thumb(a):
    """render web/thumb.js to <project>/<project>-thumbnail.png (1080x1920 for a Short, 1280x720 for a long video), right next to the MP4"""
    kit = find_kit()
    proj = proj_path(a.project)
    sync_engine(proj)
    if not (proj / 'web' / 'thumb.js').exists():
        sys.exit(f'no {proj / "web" / "thumb.js"}: write the thumbnail shot first (see "Thumbnail" in SKILL.md)')
    f = fmt(proj)
    out = proj / f'{proj.name}-thumbnail.png'
    r = node(kit, proj, 'thumb', out)
    if r.returncode:
        sys.exit(r.returncode)
    prev = proj / 'stills'
    prev.mkdir(exist_ok=True)
    if f['thumb'] != f['canvas']:     # a long video: render at 1920x1080, publish at 1280x720 (YouTube's size, under its 2 MB limit)
        full = out.with_name(out.stem + '.full.png')
        out.replace(full)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(full), '-vf', f'scale={f["thumb"][0]}:{f["thumb"][1]}:flags=lanczos', str(out)], check=True)
        full.unlink()
        mb = out.stat().st_size / 1e6
        print(f'{out}  {f["thumb"][0]}x{f["thumb"][1]}, {mb:.2f} MB' + ('  WARNING: YouTube allows 2 MB; simplify the background' if mb > 1.95 else ''))
        # what a viewer sees: the full thumbnail, the small suggested-video size, and the corner the duration badge covers
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-filter_complex',
                        '[0]split=3[a][b][c];[a]scale=640:-1[a];[b]scale=246:-1[b];'
                        '[c]scale=640:-1,drawbox=x=iw*0.80:y=ih*0.84:w=iw*0.20:h=ih*0.16:color=red@0.55:t=fill[c];'
                        '[a][b][c]xstack=inputs=3:fill=0x1c1c1c:layout=0_0|0_370|650_0[o]', '-map', '[o]', str(prev / 'thumb-crops.png')], check=False)
        print(f"crops: {prev / 'thumb-crops.png'}  (full | small suggested-video size | the red corner is hidden by the duration badge): keep faces, words and the subject out of the red")
        return
    # a Short: what a feed, an Instagram grid (3:4 centre crop) and a square tile would show, side by side
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-filter_complex',
                    '[0]split=3[a][b][c];[a]scale=270:-1[a];[b]crop=1080:1440:0:240,scale=270:-1[b];[c]crop=1080:1080:0:420,scale=270:-1[c];'
                    '[a][b][c]xstack=inputs=3:fill=0x1c1c1c:layout=0_0|280_0|560_0[o]', '-map', '[o]', str(prev / 'thumb-crops.png')], check=False)
    print(f"crops: {prev / 'thumb-crops.png'}  (9:16 feed | 3:4 grid | square): key marks must survive all three")


def cmd_video(a):
    kit = find_kit()
    ensure_kit_python(kit)
    proj = proj_path(a.project)
    sync_engine(proj)
    if not (proj / 'audio' / 'vo.wav').exists():
        sys.exit('no voiceover yet: run  build.py voice <project>  first')
    info = node(kit, proj, 'info', capture_output=True, text=True)
    if info.returncode:
        sys.exit(info.stdout)
    total = json.loads(info.stdout.strip().splitlines()[-1])['frames']
    print(f'== picture: {total} frames ({total / FPS:.1f}s) on {a.workers} workers')
    extra = []
    seg = proj / 'seg'
    shutil.rmtree(seg, ignore_errors=True)
    seg.mkdir()
    chunk = -(-total // a.workers)
    chunk += chunk % 2
    jobs, parts = [], []
    for i, f0 in enumerate(range(0, total, chunk)):
        out = seg / f'part_{i:02d}.mp4'
        parts.append(out)
        log = open(seg / f'log_{i:02d}.txt', 'w')
        env = dict(os.environ, NODE_PATH=str(kit / 'node_modules'), LB_W=str(fmt(proj)['canvas'][0]), LB_H=str(fmt(proj)['canvas'][1]))
        jobs.append(subprocess.Popen(['node', str(ENGINE / 'tools' / 'render.js'), str(proj), 'frames', str(f0), str(min(total, f0 + chunk)), str(out)],
                                     env=env, stdout=log, stderr=subprocess.STDOUT))
    codes = [j.wait() for j in jobs]
    if any(codes) or not all(p.exists() for p in parts):
        sys.exit(f'a render worker failed, see {seg}/log_*.txt')
    (seg / 'list.txt').write_text(''.join(f"file '{p.as_posix()}'\n" for p in parts), encoding='utf-8')
    silent = proj / 'silent.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(seg / 'list.txt'), '-c', 'copy', str(silent)], check=True)
    print('== sound')
    node(kit, proj, 'cues', proj / 'cues.json', check=True)
    sys.path.insert(0, str(ENGINE / 'tools'))
    import sound
    n = sound.mix(proj, total / FPS, music_gain=0 if a.no_music else 0.11, fade_out=2.0 if fmt_name(proj) == 'wide' else 1.4)
    print(f'   {n} sound cues')
    name = proj.name
    final = proj / f'{name}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(silent), '-i', str(proj / 'audio' / 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', str(final)], check=True)
    shutil.rmtree(seg, ignore_errors=True)
    # the channel outro (engine/outro-wide/outro-wide.mp4) goes on the end of every long video. Shorts have none: they end on the
    # closing line and loop (engine/outro/outro.mp4 is kept but no longer appended)
    wide = fmt_name(proj) == 'wide'
    outro = ENGINE / 'outro-wide' / 'outro-wide.mp4'
    if wide and not a.no_outro and outro.exists() and proj != (ENGINE / 'outro-wide').resolve():
        main_part = proj / f'{name}.main.mp4'
        final.replace(main_part)
        main_dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(main_part)],
                                        capture_output=True, text=True, check=True).stdout)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(main_part), '-i', str(outro), '-filter_complex',
                        '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '24',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(final)], check=True)
        main_part.unlink()
        print('   + channel outro')
        ow = outro.parent / 'audio' / 'words.json'   # the outro is voiced: its words go into the closed captions too
        if ow.exists():
            extra = [dict(w, s=round(w['s'] + main_dur, 3), e=round(w['e'] + main_dur, 3)) for w in json.loads(ow.read_text(encoding='utf-8'))]
    if (proj / 'audio' / 'words.json').exists():
        srt = write_srt(proj, extra)
        print(f'   subtitles: {srt}')
    print(f'done: {final}')


def write_srt(proj, extra=()):
    """closed captions for YouTube: <name>.srt, lines of up to 7 words / 42 characters, broken at punctuation. extra = the outro's
    words, already shifted to their time in the finished video (a caption line never runs across into them)"""
    ws = json.loads((proj / 'audio' / 'words.json').read_text(encoding='utf-8'))
    n_main, ws = len(ws), ws + list(extra)
    chunks, cur = [], []
    for k, w in enumerate(ws):
        text = w['w']
        if cur and (k == n_main or len(cur) >= 7 or len(' '.join(x['w'] for x in cur)) + len(text) + 1 > 42):
            chunks.append(cur); cur = []
        cur.append(w)
        if text.rstrip('"\')').endswith(('.', '?', '!', ',', ';', ':')):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    stamp = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}'  # noqa: E731
    out = []
    for k, c in enumerate(chunks):
        s = c[0]['s']
        e = min(chunks[k + 1][0]['s'], c[-1]['e'] + 0.4) if k + 1 < len(chunks) else c[-1]['e'] + 0.6
        out.append(f"{k + 1}\n{stamp(s)} --> {stamp(e)}\n{' '.join(x['w'] for x in c)}\n")
    path = proj / f'{proj.name}.srt'
    path.write_text('\n'.join(out), encoding='utf-8')
    return path


def cmd_sheet(a):
    proj = proj_path(a.project)
    vid = proj / f'{proj.name}.mp4'
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(vid)],
                               capture_output=True, text=True, check=True).stdout)
    n = a.n
    wide = fmt_name(proj) == 'wide'
    cols = 4 if wide else 6
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(vid), '-vf', f'fps={n}/{dur:.3f},scale={288 if wide else 216}:-1,tile={min(n, cols)}x{-(-n // cols)}',
                    '-frames:v', '1', str(proj / 'sheet.jpg')], check=True)
    print(proj / 'sheet.jpg')


def fmt_clock(sec):
    sec = int(sec)
    return f'{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}' if sec >= 3600 else f'{sec // 60}:{sec % 60:02d}'


def cmd_chapters(a):
    """YouTube chapters from chapters.json ([{"title": "...", "line": N}], N = the sentence in script.json that opens the chapter)
    and the real word times from `voice`. Validated against YouTube's rules: starts at 0:00, at least 3, each at least 10 s."""
    proj = proj_path(a.project)
    try:
        chs = json.loads((proj / 'chapters.json').read_text(encoding='utf-8'))
        ws = json.loads((proj / 'audio' / 'words.json').read_text(encoding='utf-8'))
    except FileNotFoundError as e:
        sys.exit(f'missing {e.filename}: write chapters.json and run  build.py voice  first')
    start = {}
    for w in ws:
        start.setdefault(w['line'], w['s'])
    rows, problems = [], []
    for i, c in enumerate(chs):
        if c['line'] not in start:
            problems.append(f'chapter "{c["title"]}": sentence {c["line"]} is not in script.json')
            continue
        rows.append((0.0 if i == 0 else start[c['line']], str(c['title']).strip()))
    total = ws[-1]['e'] if ws else 0
    if len(rows) < 3:
        problems.append('YouTube needs at least 3 chapters')
    for (s0, t0), (s1, _) in zip(rows, rows[1:] + [(total, '')]):
        if s1 <= s0:
            problems.append(f'chapter "{t0}" is not in order')
        elif s1 - s0 < 10:
            problems.append(f'chapter "{t0}" is only {s1 - s0:.0f} s long (YouTube needs at least 10 s)')
    path = proj / f'{proj.name}-chapters.txt'
    path.write_text(''.join(f'{fmt_clock(s0)} {t}\n' for s0, t in rows), encoding='utf-8')
    print(path.read_text(encoding='utf-8'))
    if problems:
        sys.exit('NOT VALID FOR YOUTUBE: ' + '; '.join(problems))
    print(f'{len(rows)} chapters, valid. Total {fmt_clock(total)} of voiceover.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('new'); p.add_argument('project'); p.add_argument('--example', action='store_true')
    p.add_argument('--wide', action='store_true', help='a long video: 16:9, 1920x1080'); p.set_defaults(f=cmd_new)
    p = sub.add_parser('chapters'); p.add_argument('project'); p.set_defaults(f=cmd_chapters)
    p = sub.add_parser('voice'); p.add_argument('project'); p.add_argument('--voice', default='af_heart')
    p.add_argument('--speed', type=float, default=1.0); p.add_argument('--file')
    p.add_argument('--target', type=float, help='the length in seconds the user asked for; voice reports whether the read hits it')
    p.add_argument('--append', action='store_true', help='voice only the sentences added at the end of script.json; earlier audio and word times are kept')
    p.add_argument('--hold', type=float, default=0.0, help='seconds to hold the last pose after the voice, before the iris (the outro: end-screen time)')
    p.set_defaults(f=cmd_voice)
    p = sub.add_parser('check'); p.add_argument('project'); p.set_defaults(f=cmd_check)
    p = sub.add_parser('stills'); p.add_argument('project'); p.add_argument('times'); p.add_argument('--scale', default='0.5'); p.set_defaults(f=cmd_stills)
    p = sub.add_parser('video'); p.add_argument('project'); p.add_argument('--workers', type=int, default=max(2, min(6, (os.cpu_count() or 4) // 2)))
    p.add_argument('--no-music', action='store_true'); p.add_argument('--no-outro', action='store_true', help='a long video without the channel outro (Shorts never get one)'); p.set_defaults(f=cmd_video)
    p = sub.add_parser('thumb'); p.add_argument('project'); p.set_defaults(f=cmd_thumb)
    p = sub.add_parser('sheet'); p.add_argument('project'); p.add_argument('--n', type=int, default=12); p.set_defaults(f=cmd_sheet)
    a = ap.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
