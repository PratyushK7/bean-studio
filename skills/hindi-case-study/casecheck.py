#!/usr/bin/env python3
"""casecheck.py - lint a Hindi case-study script against what the top Hindi business channels actually do.

    python casecheck.py <project>/script.json            # the report
    python casecheck.py <project>/script.json --voice    # print only the Devanagari voiceover (for TTS)
    python casecheck.py --transcript tx.json             # check a real video's captions (calibration)

The thresholds come from the ten most-viewed videos of HinExp and ABFinDoc (750K to 2M views each, read in
references/study.md): every one of those passes the FAIL rules here. Hindi narration is timed at 155 words a
minute, the middle of the 145 to 183 the ten were measured at.

FAIL means the script breaks something all ten hits do. WARN means look again and decide; a WARN can be right.
"""
import json, re, sys, unicodedata

WPM = 155

def norm(s):
    """drop the nukta so जरा/ज़रा and मोड/मोड़ match the same pattern"""
    return unicodedata.normalize("NFD", s or "").replace("़", "")

def rx(p): return re.compile(norm(p))

STRONG = [rx(p) for p in [
    r"मोड", r"ध्यान से (सुनिए|सुनो|देखिए)", r"बहुत कम लोग", r"कोई (खुलकर )?नहीं (बताता|करता)", r"(किसी|लोगों) को (भी )?नहीं पता",
    r"किसे पता था", r"अंदाजा (भी )?नहीं (था|लगा)", r"सिक्के का दूसरा पहलू", r"असली (खेल|कहानी|झटका|वजह|सवाल|पिक्चर|कारण|गणित|ताकत)",
    r"सबसे (बडा|बडी|चौंकाने|दिलचस्प|खतरनाक|गहरा|गहरी|दर्दनाक|अहम|नाटकीय)", r"यहीं (से|इस)", r"ट्विस्ट", r"जगह (रखकर|रख कर|खुद को)",
    r"जरा (सोचिए|सोचो|इस|देखिए|सुनिए|गौर)", r"सवाल (यह|ये) (है|उठता)", r"सिर्फ शुरुआत", r"कहानी यहीं", r"छिपा|छिपी|छुपा|छुपी",
    r"(पहली|दूसरी|तीसरी|चौथी|पांचवीं|आखिरी) (दरार|वजह|गलती|चाल|बात|शर्त|चोट|वार)", r"लेकिन असल में", r"चौंकाने वाली",
    r"कहानी (का|की) (सबसे|एक और|दूसरा)", r"(वापस|लौटते) (चलते|आते) हैं", r"जिससे (हमने|यह) .{0,20}शुरु", r"विडंबना", r"परत",
    # what the hits use in the long stretches between the big twists: a setback, a callback, the overlooked part
    r"झटका", r"अनदेखा", r"(शुरुआत|शुरू) में (की|बताया|देखा)|जिसकी बात हमने", r"(यहां|वहां) भी (निराशा|बात)", r"बात नहीं बनी", r"रिजेक्ट|ठुकरा",
    r"(वो|वह) (पल|दिन|फैसला|गलती|रात) (जिस|जो)", r"हैरान", r"बदला|अपमान|हमला|जंग|युद्ध|धोखा",
]]
# a turn: a contrast word, a question, or the narrator talking straight to the viewer (समझो, सोचिए, मान लो)
TURN = rx(r"(^|[।?!,]\s*)(पर|फिर भी)\s|(^|\s)(लेकिन|मगर|तभी|हालांकि)\s|(^|\s)(समझो|समझिए|सुनो|सुनिए|देखो|देखिए|सोचो|सोचिए|मान लो|मान लीजिए)(\s|[।,])")
START = rx(r"चलिए (शुरू|देखते)|चलो शुरू|आइए (देखते|शुरू|समझते|जानते)|शुरू करते हैं")
GREET = rx(r"नमस्ते|नमस्कार|स्वागत|हेलो|हैलो|दोस्तों|welcome")
CTA = rx(r"लाइक (जरूर|करें|करो|कीजिए|कर दो|कर दीजिए)|चैनल को सब्सक्राइब|सब्सक्राइब (करना|कर लीजिए|कर लो|करें|करो|कीजिए)|बेल आइकन|नोटिफिकेशन|कमेंट में|शेयर (करें|करो|कीजिए)|(दोस्तों|दोस्त) (को|तक) .{0,30}भेज")
NEXT = rx(r"अगली (वीडियो|कहानी|डॉक्यूमेंट्री|बार|एपिसोड)")
SECOND_PERSON = rx(r"इमेजिन|कल्पना|सोचो|सोचिए|आप")
QWORD = rx(r"आखिर (क्या|कैसे|क्यों|कौन)|क्या सच में|कैसे एक")
LATIN_NAME = re.compile(r"\b[A-Z][a-zA-Z]{2,}")   # a brand or person named in Latin letters (Tavera, Volvo)
YEAR = re.compile(r"\b(1[89]|20)\d\d\b")
NUM = rx(r"₹?\d[\d,.]*%?|करोड|लाख|हजार|प्रतिशत|परसेंट|डेढ|ढाई|साढे|सवा")   # one hit per number, not per digit
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
STOP = set(norm(w) for w in "यह वह और है था थी थे हैं में से का की के को पर एक जो तो भी ही कि नहीं अपने अपनी उस इस उन इन कर रहे रहा रही लिए साथ बाद अब हम आप वो ये".split())

def words(s): return [w for w in re.split(r"\s+", (s or "").strip()) if re.search(r"\w", w)]

FMT_ARG = None

def load(path, transcript=False):
    data = json.load(open(path, encoding="utf-8"))
    if transcript:     # captions: [{"t","d","x"}], re-cut into sentences on । and ?
        text = " ".join(r["x"] for r in data).replace("[संगीत]", " ")
        parts = [p.strip() for p in re.split(r"(?<=[।?!])\s+", text) if p.strip()]
        dur = (data[-1]["t"] + data[-1]["d"]) / 60
        wpm = len(words(text)) / dur          # time captions at the video's own pace
        return {"title": path, "format": FMT_ARG or "?", "sources": ["(captions)"] * 3, "lines": [{"hi": p} for p in parts], "wpm": wpm}
    if isinstance(data, list): data = {"lines": data}
    return data

def check(doc):
    lines = doc.get("lines") or []
    fmt = doc.get("format", "?")
    out = []          # (level, message)
    def say(level, msg): out.append((level, msg))
    if not lines:
        say("FAIL", "no lines"); return out, {}

    # timing: each line's start and end in seconds at WPM
    wpm = doc.get("wpm") or WPM
    t, times = 0.0, []
    for ln in lines:
        n = len(words(ln.get("hi")))
        times.append((t, t + n * 60 / wpm)); t += n * 60 / wpm
    total = t
    mins = total / 60
    txt = [norm(ln.get("hi")) for ln in lines]
    def mmss(s): return f"{int(s // 60):02d}:{int(s % 60):02d}"

    # 1. runtime
    lvl = "PASS" if 10 <= mins <= 25 else "WARN"
    say(lvl, f"runtime {mins:.1f} min at {wpm:.0f} wpm ({sum(len(words(l.get('hi'))) for l in lines)} words); the ten hits run 12.5 to 28 min, most 14 to 20")

    # 2. hook: ends at the 'let's start' line
    start_i = next((i for i, s in enumerate(txt) if START.search(s)), None)
    if start_i is None:
        say("WARN", "no 'चलिए शुरू करते हैं'-type line, so the hook has no clear end; the hits all mark it (at 60 to 110 s)")
        hook_end = min(len(lines), max(1, len(lines) // 12))
    else:
        hook_end = start_i + 1
        hs = times[start_i][1]
        lvl = "PASS" if 50 <= hs <= 120 else "WARN"
        say(lvl, f"hook ends at {mmss(hs)} (line {start_i + 1}); the hits end it between 01:00 and 01:50")
    hook = " ".join(txt[:hook_end])

    # 3. the first two lines put the viewer somewhere concrete
    first = " ".join(txt[:2])
    anchors = [k for k, ok in (("year/date", YEAR.search(first)), ("number", NUM.search(first)), ("second-person scene", SECOND_PERSON.search(first)),
                               ("named product/person", LATIN_NAME.search(" ".join(ln.get("hi", "") for ln in lines[:2])))) if ok]
    if anchors: say("PASS", f"opening anchor: {', '.join(anchors)}")
    else: say("FAIL", "the first two lines have no year, number, 'you' scene or famous name; every hit opens on one (a date and place, a price, 'imagine you...', or a product everyone knows)")

    # 4. hook contents
    if GREET.search(" ".join(txt[:3])): say("FAIL", "a greeting or channel intro in the first lines; none of the ten hits opens with one")
    if "?" not in hook and not QWORD.search(hook): say("WARN", "the hook asks no question; the hits end the hook on 1 to 3 open questions")
    if not TURN.search(hook) and not any(p.search(hook) for p in STRONG): say("WARN", "the hook has no turn (लेकिन/पर/the twist); it should break the belief it sets up")
    if CTA.search(hook): say("FAIL", "a like/subscribe/comment ask inside the hook")

    # 5. re-hooks through the body (hook end -> where the closing CTA starts)
    cta_i = next((i for i, s in enumerate(txt) if i >= hook_end and CTA.search(s)), len(lines))
    body_end_t = times[cta_i - 1][1] if cta_i > 0 else total
    hook_t = times[hook_end - 1][1]
    def is_strong(s):
        return any(p.search(s) for p in STRONG) or (fmt == "compare" and len(NUM.findall(s)) >= 2)   # in a compare video the running scoreboard is the re-hook
    strong = [(times[i][0], i) for i, s in enumerate(txt) if hook_end <= i < cta_i and is_strong(s)]
    turns = [times[i][0] for i, s in enumerate(txt) if hook_end <= i < cta_i and (TURN.search(s) or "?" in s or any(p.search(s) for p in STRONG))]
    def longest(points, a, b):
        pts = [a] + sorted(points) + [b]
        g = max(((pts[k + 1] - pts[k]), pts[k]) for k in range(len(pts) - 1))
        return g
    g, at = longest([p for p, _ in strong], hook_t, body_end_t)
    per = len(strong) / max(0.1, (body_end_t - hook_t) / 60)
    lvl = "PASS" if g <= 150 else "WARN" if g <= 300 else "FAIL"
    say(lvl, f"strong re-hooks: {len(strong)} in the body ({per:.1f}/min); longest gap {g:.0f} s from {mmss(at)}. Aim for one every 60 to 90 s; the hits never go past 4.3 min (FAIL over 5)")
    g2, at2 = longest(turns, hook_t, body_end_t)
    lvl = "PASS" if g2 <= 75 else "WARN"
    say(lvl, f"turns (लेकिन/पर/a question/a re-hook): longest gap {g2:.0f} s from {mmss(at2)}; aim for a turn every 20 to 40 s, never a minute and a quarter without one")
    mid = [p for p, _ in strong if 0.35 * total <= p <= 0.65 * total]
    say("PASS" if mid else "WARN", "a strong re-hook in the middle third" if mid else "no strong re-hook between 35% and 65% of the runtime; the hits put their biggest twist there")

    # 6. numbers
    nums = sum(len(NUM.findall(s)) for s in txt) / max(0.1, mins)
    want = {"economics": 3.5, "compare": 6.0, "story": 2.5, "person": 1.0}.get(fmt, 1.0)
    lvl = "PASS" if nums >= want else "WARN"
    say(lvl, f"numbers {nums:.1f}/min (want {want}+ for format '{fmt}'; the hits: economics 3.9 to 5.3, compare 8.7, story 3.1 to 3.4, person 1.1 to 6.9; years count)")

    # 7. ending
    if cta_i < len(lines) and times[cta_i][0] < 0.85 * total:
        say("WARN", f"the first like/subscribe/comment ask is at {mmss(times[cta_i][0])} ({times[cta_i][0] / total:.0%}); the hits keep every ask to the last 10%")
    if cta_i == len(lines): say("WARN", "no closing ask (like / send to a friend / comment question)")
    tail = " ".join(txt[int(len(txt) * 0.88):])
    if not NEXT.search(tail): say("WARN", "no tease of the next video in the close (the hits name the next topic, sometimes with 2 or 3 questions)")
    opening = set(w for w in words(" ".join(txt[:3])) if len(w) >= 4 and w not in STOP)
    back = opening & set(words(tail + " " + " ".join(txt[int(len(txt) * 0.6):int(len(txt) * 0.88)])))
    say("PASS" if len(back) >= 2 else "WARN", f"callback to the cold open: {len(back)} shared words" + ("" if len(back) >= 2 else " (the hits return to the opening scene near the end)"))

    # 8. honesty and production
    src = doc.get("sources") or []
    if fmt != "?" and len(src) == 0: say("FAIL", "no sources; a case study with real numbers and real people needs them in script.json and the research file")
    elif fmt != "?" and len(src) < 3: say("WARN", f"only {len(src)} sources")
    longl = [i + 1 for i, ln in enumerate(lines) if len(words(ln.get("hi"))) > 30]
    if longl: say("WARN", f"{len(longl)} lines over 30 words (lines {longl[:8]}); split them, the voice reads one line per breath")
    scr = [ln.get("screen") for ln in lines if ln.get("screen")]
    bad = [s for s in scr if DEVANAGARI.search(s) or len(words(s)) > 6]
    if bad: say("WARN", f"{len(bad)} on-screen texts are Devanagari or over 6 words (screen text is short Hinglish in Latin letters), e.g. {bad[0]!r}")
    if lines and len(scr) / len(lines) > 0.35: say("WARN", f"screen text on {len(scr) / len(lines):.0%} of lines; keep text rare (numbers, names, the one key word)")
    if any(ln.get("visual") for ln in lines):
        run, worst = 0, 0
        for ln in lines:
            run = 0 if ln.get("visual") else run + 1; worst = max(worst, run)
        if worst > 3: say("WARN", f"{worst} lines in a row with no visual; a new picture every 1 to 3 lines (5 to 10 s) keeps the screen alive")
    stats = {"minutes": round(mins, 1), "strong": [(mmss(p), i + 1) for p, i in strong]}
    return out, stats

def main():
    a = sys.argv[1:]
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    if not a: sys.exit(__doc__)
    tr = "--transcript" in a
    global FMT_ARG
    if "--format" in a: FMT_ARG = a[a.index("--format") + 1]; a = [x for x in a if x not in ("--format", FMT_ARG)]
    path = [x for x in a if not x.startswith("--")][0]
    doc = load(path, transcript=tr)
    if "--voice" in a:
        print("\n".join(ln.get("hi", "") for ln in doc["lines"])); return
    out, stats = check(doc)
    print(f"\n  {doc.get('title', path)}  [{doc.get('format', '?')}]")
    for lvl, msg in out: print(f"  {lvl:4}  {msg}")
    if stats.get("strong"): print("  re-hooks at: " + "  ".join(f"{m}(l{i})" for m, i in stats["strong"][:40]))
    fails = sum(1 for l, _ in out if l == "FAIL"); warns = sum(1 for l, _ in out if l == "WARN")
    print(f"\n  {fails} FAIL, {warns} WARN" + ("  - fix the FAILs before the voice" if fails else ""))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
