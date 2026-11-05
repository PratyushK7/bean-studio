"""Patch line-boil's engine/build.py for the voiced channel outro. Every change is checked to apply exactly once; nothing is written if any fails.
  voice --append   voice only the sentences added at the end of script.json (earlier audio and word times kept sample for sample)
  voice --hold N   hold the last pose N s after the voice, before the iris (the outro uses it for YouTube end-screen time)
  video            the voiced outro's words go into the .srt, after the video's own
usage: python patch_build.py <build.py in> <build.py out>"""
import ast, sys

REP = [
("""def tts(proj, voice, speed):
    import numpy as np""",
"""def tts(proj, voice, speed, append=False):
    \"\"\"Kokoro voiceover of script.json -> audio/vo.wav + audio/sentences.json. With append, the existing take is kept sample for sample
    and only the sentences after it are voiced (so every earlier word time stays put). Returns the index of the first new sentence.\"\"\"
    import numpy as np"""),
("""    out, sr, pos, bounds = [], 24000, 0, []
    for i, line in enumerate(lines):
        samples, sr = k.create(line, voice=voice, speed=speed, lang='en-us')""",
"""    out, sr, pos, bounds, first = [], 24000, 0, [], 0
    if append:
        old, sr = sf.read(str(proj / 'audio' / 'vo.wav'), dtype='float32')
        bounds = json.loads((proj / 'audio' / 'sentences.json').read_text(encoding='utf-8'))
        first = len(bounds)
        out.append(old)
        pos = len(old)
    for i, line in enumerate(lines):
        if i < first:
            continue
        samples, sr = k.create(line, voice=voice, speed=speed, lang='en-us')"""),
("""        samples = samples[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        out.append(samples)""",
"""        samples = samples[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)].astype('float32')
        out.append(samples)"""),
("""        out.append(np.zeros(int(gap * sr), dtype=samples.dtype))""",
"""        out.append(np.zeros(int(gap * sr), dtype='float32'))"""),
("""    (proj / 'audio' / 'sentences.json').write_text(json.dumps(bounds), encoding='utf-8')   # lets the word timing run in chunks


def word_timings(kitwords, proj, lines):
    \"\"\"word start/end times for the voiceover. A long voiceover is timed in windows of about 40 s cut at sentence ends (the model
    fails past roughly 6.5 minutes), then joined. Without sentence bounds (your own recording) it is timed in one go.\"\"\"""",
"""    (proj / 'audio' / 'sentences.json').write_text(json.dumps(bounds), encoding='utf-8')   # lets the word timing run in chunks
    return first


def word_timings(kitwords, proj, lines, first=0, prefix=None):
    \"\"\"word start/end times for the voiceover. A long voiceover is timed in windows of about 40 s cut at sentence ends (the model
    fails past roughly 6.5 minutes), then joined. Without sentence bounds (your own recording) it is timed in one go.
    first/prefix (voice --append): only the sentences from `first` on are timed; `prefix` holds the earlier words, kept as they were.\"\"\""""),
("""    bounds = json.loads(sent.read_text(encoding='utf-8')) if sent.exists() else []
    if dur <= 45 or len(bounds) != len(lines):""",
"""    bounds = json.loads(sent.read_text(encoding='utf-8')) if sent.exists() else []
    if first and len(bounds) == len(lines):
        bounds = bounds[first:]
    elif dur <= 45 or len(bounds) != len(lines):"""),
("""        out.append({'w': w, 's': round(t, 3), 'e': round(min(e, t + 1.2), 3)})
    return out""",
"""        out.append({'w': w, 's': round(t, 3), 'e': round(min(e, t + 1.2), 3)})
    return (prefix or []) + out"""),
("""    if a.file:
        (proj / 'audio' / 'sentences.json').unlink(missing_ok=True)   # a recording has no sentence markers
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.file, '-ac', '1', '-ar', '44100', str(proj / 'audio' / 'vo.wav')], check=True)
    else:
        tts(proj, a.voice, a.speed)
    sys.path.insert(0, str(kit))
    import words as kitwords
    lines = json.loads((proj / 'script.json').read_text(encoding='utf-8'))
    ws = word_timings(kitwords, proj, lines)""",
"""    first, prefix = 0, None
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
    ws = word_timings(kitwords, proj, lines, first=first, prefix=prefix)"""),
("""    end = round(dur + 2.3, 2)   # main.js: 1.0 s breath + 1.0 s iris close + 0.3 s on black
    (proj / 'audio' / 'words.json').write_text(json.dumps(ws, indent=0), encoding='utf-8')
    sync_engine(proj)
    (proj / 'web' / 'words.js').write_text(f'const WORDS = {json.dumps(ws)};\\nconst VO_DUR = {round(dur, 3)};\\n', encoding='utf-8')""",
"""    end = round(dur + a.hold + 2.3, 2)   # main.js: 1.0 s breath + 1.0 s iris close + 0.3 s on black (after any --hold)
    (proj / 'audio' / 'words.json').write_text(json.dumps(ws, indent=0), encoding='utf-8')
    sync_engine(proj)
    # --hold N: the last pose holds N more seconds before the iris (the channel outro uses it so YouTube's end-screen elements have time)
    hold = f'  // the voice ends at {round(dur, 3)} s; +{a.hold} s held' if a.hold else ''
    (proj / 'web' / 'words.js').write_text(f'const WORDS = {json.dumps(ws)};\\nconst VO_DUR = {round(dur + a.hold, 3)};{hold}\\n', encoding='utf-8')"""),
("""    print(f'== picture: {total} frames ({total / FPS:.1f}s) on {a.workers} workers')""",
"""    print(f'== picture: {total} frames ({total / FPS:.1f}s) on {a.workers} workers')
    extra = []"""),
("""        main_part = proj / f'{name}.main.mp4'
        final.replace(main_part)""",
"""        main_part = proj / f'{name}.main.mp4'
        final.replace(main_part)
        main_dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(main_part)],
                                        capture_output=True, text=True, check=True).stdout)"""),
("""        main_part.unlink()
        print('   + channel outro')
    if (proj / 'audio' / 'words.json').exists():
        srt = write_srt(proj)""",
"""        main_part.unlink()
        print('   + channel outro')
        ow = outro.parent / 'audio' / 'words.json'   # the outro is voiced: its words go into the closed captions too
        if ow.exists():
            extra = [dict(w, s=round(w['s'] + main_dur, 3), e=round(w['e'] + main_dur, 3)) for w in json.loads(ow.read_text(encoding='utf-8'))]
    if (proj / 'audio' / 'words.json').exists():
        srt = write_srt(proj, extra)"""),
("""def write_srt(proj):
    \"\"\"closed captions for YouTube: <name>.srt, lines of up to 7 words / 42 characters, broken at punctuation\"\"\"
    ws = json.loads((proj / 'audio' / 'words.json').read_text(encoding='utf-8'))
    chunks, cur = [], []
    for w in ws:
        text = w['w']
        if cur and (len(cur) >= 7 or len(' '.join(x['w'] for x in cur)) + len(text) + 1 > 42):""",
"""def write_srt(proj, extra=()):
    \"\"\"closed captions for YouTube: <name>.srt, lines of up to 7 words / 42 characters, broken at punctuation. extra = the outro's
    words, already shifted to their time in the finished video (a caption line never runs across into them)\"\"\"
    ws = json.loads((proj / 'audio' / 'words.json').read_text(encoding='utf-8'))
    n_main, ws = len(ws), ws + list(extra)
    chunks, cur = [], []
    for k, w in enumerate(ws):
        text = w['w']
        if cur and (k == n_main or len(cur) >= 7 or len(' '.join(x['w'] for x in cur)) + len(text) + 1 > 42):"""),
("""    p.add_argument('--target', type=float, help='the length in seconds the user asked for; voice reports whether the read hits it')
    p.set_defaults(f=cmd_voice)""",
"""    p.add_argument('--target', type=float, help='the length in seconds the user asked for; voice reports whether the read hits it')
    p.add_argument('--append', action='store_true', help='voice only the sentences added at the end of script.json; earlier audio and word times are kept')
    p.add_argument('--hold', type=float, default=0.0, help='seconds to hold the last pose after the voice, before the iris (the outro: end-screen time)')
    p.set_defaults(f=cmd_voice)"""),
]

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
if 'def word_timings(kitwords, proj, lines, first=0' in s:
    sys.exit('already patched')
bad = [a.splitlines()[0][:90] for a, _ in REP if s.count(a) != 1]
if bad:
    sys.exit('these changes do not apply (build.py differs from the one this patch was written for):\n  ' + '\n  '.join(bad))
for a, b in REP:
    s = s.replace(a, b)
ast.parse(s)
open(dst, 'w', encoding='utf-8', newline='\n').write(s)
print(f'patched {len(REP)} places -> {dst}')
