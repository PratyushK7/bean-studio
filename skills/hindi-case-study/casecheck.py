#!/usr/bin/env python3
"""casecheck.py - lint a Decoding Vyapaar script for the mechanical ways a script fails.

    python casecheck.py <project>/script.json            # the report: FAIL / WARN / PASS / INFO
    python casecheck.py <project>/script.json --md       # write <slug>-script.md, the readable script the owner reviews
    python casecheck.py <project>/script.json --voice    # print only the Devanagari narration (for TTS)
    python casecheck.py --transcript tx.json [--format story]   # check a real video's captions (calibration)

What it checks:
  structure  the engine and beat sheet exist; the loop ledger (open/close on lines) opens L1 in the hook and closes it at the end,
             every loop pays off, some loop is open at every moment; no long stretch without a re-hook, reveal or interrupt
  the ear    sentence length, numbers per sentence and per half minute, speech with no speaker named, repeated phrases,
             template and AI lines, meta orders to the viewer; the time anchors are listed (INFO) for the time-line pass
  honesty    sources, research ids on lines with numbers, no fiction disclaimer, sources read aloud
  the rules  no greeting, no ask before the close, a short close

What it cannot check: whether the story is any good. The v2 jewellery script passed the old checker with 0 FAIL and 0 WARN and still
"felt so off", because lines had been added to satisfy its phrase counts. Never add a line to satisfy a rule here; fix the script and
read the report again. The ear thresholds are rules of thumb, not measured on the hits; the craft is judged by SKILL.md section 8.
"""
import json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

WPM = 155

def norm(s):
    """drop the nukta so जरा/ज़रा and मोड/मोड़ match the same pattern"""
    return unicodedata.normalize("NFD", s or "").replace("़", "")

def rx(p): return re.compile(norm(p))

# template lines: stock re-hooks that promise nothing (FAIL), and generic AI or channel-template phrasing (WARN)
BANNED = rx(r"कहानी यहीं (खत्म|ख़त्म) नहीं|आगे जो हुआ (वो|वह) (चौंकाने|हैरान)|(ये|यह) तो (बस|सिर्फ) शुरुआत (थी|है)[।?]|आइए जानते हैं|इस वीडियो में (हम )?(जानेंगे|बताएंगे|देखेंगे)")
AI = rx(r"क्या आपने कभी सोचा|आज के (इस )?दौर में|दिलचस्प बात (यह|ये) है|गौर करने (वाली|लायक) बात|गहराई से (समझ|जान)|(यह|ये|इस) सफर|अनसुनी दास्तान|चौंकाने वाला सच|हैरान रह जाएंगे|रोंगटे खड़े|महत्वपूर्ण भूमिका|न केवल|अंत में|तो दोस्तों|चलिए (अब )?आगे बढ़ते|अब बात करते हैं|उम्मीद है (आपको|ये)")
REFRAME = rx(r"सिर्फ [^।?]{1,40} नहीं (था|थी|थे|है|हैं)[,।]?\s*(ये|यह|वो|वह|बल्कि)")
META = rx(r"(लिख|नोट कर) (लीजिए|लो|लें|लीजिएगा)|याद रखि(ए|एगा)|याद रखना|वीडियो के (आखिर|अंत) (में|तक)")
TOLD = rx(r"सांस (एक पल को )?(रुक|थम)|चेहरे पर (एक )?(मुस्कान|चमक|खुशी) (आ|छा|दौड)|दिल (जोर से )?(धड़क|बैठ) (उठा|गया|जाता)|आंखें (चमक|भर) (उठीं|आईं|गईं)")
DISCLAIM = rx(r"किरदार|काल्पनिक|फिक्शन|कहानी (सच्ची|काल्पनिक) नहीं|ढूंढने मत निकल|(हमारी|ये|यह) (कहानी|किरदार)[^।]{0,30}(मनगढ़ंत|गढ़ी)")
# textbook Hindi people do not say today; each has the everyday word in SKILL.md ("The everyday word")
BOOKISH = rx(r"सर्राफ|बनवाई|ग्राहक|बिक्री|मुनाफा|ब्याज|मजदूरी|संगठित|शुद्धता|उपभोक्ता|व्यापारी|लेन-देन|पूंजी|आमदनी|विक्रेता|क्रेता|अनुमान|\bतथा\b|\bएवं\b|किंतु|परंतु|\bअतः|\bहेतु\b|द्वारा|अत्यंत|अत्यधिक|प्रतीत|पश्चात|उपरांत|आवश्यक|संभवतः|वर्तमान में")
SOURCED = rx(r"के मुताबिक|के अनुसार|रिपोर्ट (कहती|बताती)|का कहना है|ने खुद बताया|खुद मानती")
CATEGORY = re.compile(r"^\s*(intro(duction)?|investment|revenue|expenses?|costs?|profit|income|conclusion|summary|overview|background|basics|the business model)\b", re.I)
GREET = rx(r"नमस्ते|नमस्कार|स्वागत|हेलो|हैलो|दोस्तों|welcome")
CTA = rx(r"लाइक (जरूर|करें|करो|कीजिए|कर दो|कर दीजिए)|सब्सक्राइब|बेल आइकन|नोटिफिकेशन|कमेंट (में|करके)|शेयर (करें|करो|कीजिए)|(दोस्त|दोस्तों) (को|तक) [^।]{0,30}भेज|(ये|यह) वीडियो [^।]{0,30}भेज|Hype|हाइप")
NEXT = rx(r"अगल(ी|े) (वीडियो|कहानी|डॉक्यूमेंट्री|एपिसोड|डिकोड)")
# speech: a line that opens on an address ("पापा, ...", "गोयल जी, ...") or speaks in the first person or with तू is a character
# talking; the listener hears one narrator, so the speaker must be named in this line or the one before it
VOCATIVE = rx(r"^\s*(पापा|मम्मी|मां|बेटा|बेटी|दादा|दादी|दादाजी|नानी|बाबूजी|सेठ जी|सेठजी|भाई|भैया|दीदी|साहब|अंकल|आंटी|यार|सर|मैडम|\S+ (जी|भाई|दादा|साहब|बाबू))\s*[,!]")
FIRST_PERSON = rx(r"(^|\s)(मैं|मैंने|मेरा|मेरी|मेरे|मुझे|मुझसे|तू|तेरा|तेरी|तेरे|तुझे|तुझसे)(\s|[,।?!]|$)")
SPEECH = rx(r"कह(ते|ता|ती|ा|कर)|बोल(े|ा|ी|ते|ता|ती|कर)|पूछ(ते|ता|ती|ा|कर)|चिल्ला|फुसफुसा|जवाब (देते|देता|देती|दिया)|आवाज (आती|आई)|डांट|हंसकर|मुस्कुराकर|सवाल (छोड़|करता|करते)")
# numbers: a run of number words close together ("दो लाख साठ हजार पांच सौ अस्सी") counts as one number
MAG = rx(r"^(₹?\d[\d,.]*%?|करोड|करोडों|लाख|लाखों|हजार|हजारों|सौ|परसेंट|प्रतिशत|डेढ|ढाई|साढे|सवा|किलो|ग्राम|रुपये|रुपया|रुपयों)$")
MONEY = rx(r"₹|\d|करोड|लाख|हजार|परसेंट|प्रतिशत")
YEAR = re.compile(r"\b(1[89]|20)\d\d\b")
TIME_ANCHOR = rx(r"((उन्नीस|दो) हजार [^\s,।]+)|\b(1[89]|20)\d\d\b|(\S+ )?(जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर)|इस (साल|बार|धनतेरस|दिवाली|महीने)|पिछले (साल|महीने|हफ्ते)|अगले (साल|दिन)|अगली सुबह|उसी (रात|शाम|दिन)|उस रात|\S+ (साल|महीने|दिन) (पहले|बाद)")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
STOP = set(norm(w) for w in ("यह वह और है था थी थे हैं में से का की के को पर एक जो तो भी ही कि नहीं अपने अपनी उस इस उन इन कर रहे रहा "
                              "रही लिए साथ बाद अब हम आप वो ये ना है। हो गया गई गए जाता जाती जाते होता होती होते करते करता करती तक सब").split())
ASKQ = rx(r"(आप|आपके|आपकी|आपका)[^।]*\?|(आप )?बताइए|अगली बार [^।]{0,60}(देखिएगा|देखिए|पूछिए|पूछिएगा|चेक कीजिए|डालिए)")
DEVICE_TAGS = {"rehook", "interrupt", "reveal", "reversal", "payoff", "gain"}
KINDS = {"still", "card", "hero"}

def words(s): return [w for w in re.split(r"\s+", (s or "").strip()) if re.search(r"\w", w)]
def sentences(s): return [x for x in re.split(r"(?<=[।?!])\s+", s or "") if x.strip()] or [""]
def is_speech(s): return bool(FIRST_PERSON.search(s) or any(VOCATIVE.search(x) for x in sentences(s)))
def as_list(v): return [] if not v else [v] if isinstance(v, str) else list(v)
def mmss(s): return f"{int(s // 60):02d}:{int(s % 60):02d}"

def numbers(s):
    """spoken numbers in a line, a close run of number words counted once"""
    toks = [re.sub(r"[,।?!:;\"'“”‘’]", "", w) for w in norm(s).split()]
    hits = [i for i, t in enumerate(toks) if t and MAG.match(t)]
    runs, last = 0, -9
    for i in hits:
        if i - last > 2: runs += 1
        last = i
    return runs

FMT_ARG = None

def load(path, transcript=False):
    data = json.load(open(path, encoding="utf-8"))
    if transcript:     # captions: [{"t","d","x"}], re-cut into sentences on । and ?
        text = " ".join(r["x"] for r in data).replace("[संगीत]", " ")
        parts = [p.strip() for p in re.split(r"(?<=[।?!])\s+", text) if p.strip()]
        dur = (data[-1]["t"] + data[-1]["d"]) / 60
        return {"title": path, "format": FMT_ARG or "?", "sources": ["(captions)"] * 3, "lines": [{"hi": p} for p in parts],
                "wpm": len(words(text)) / dur, "transcript": True}
    if isinstance(data, list): data = {"lines": data}
    return data

def timing(doc):
    wpm = doc.get("wpm") or WPM
    t, times = 0.0, []
    for ln in doc["lines"]:
        d = len(words(ln.get("hi"))) * 60 / wpm
        times.append((t, t + d)); t += d
    return times, t

def check(doc, research_text=None):
    lines = doc.get("lines") or []
    fmt, tr = doc.get("format", "?"), doc.get("transcript", False)
    out = []
    def say(level, msg): out.append((level, msg))
    if not lines:
        say("FAIL", "no lines"); return out
    times, total = timing(doc)
    mins = total / 60
    txt = [norm(ln.get("hi")) for ln in lines]
    def at(i): return f"{mmss(times[i][0])} (line {i + 1})"
    def first_lines(idx, n=8): return ", ".join(str(i + 1) for i in idx[:n]) + (" ..." if len(idx) > n else "")

    # --- runtime and the hook
    say("PASS" if 10 <= mins <= 25 else "WARN", f"runtime {mins:.1f} min at {doc.get('wpm') or WPM:.0f} wpm ({sum(len(words(l.get('hi'))) for l in lines)} words); aim for 14 to 18 min (10 to 15 for a short topic)")
    chap_i = [i for i, ln in enumerate(lines) if ln.get("chapter")]
    hook_end = chap_i[1] if len(chap_i) > 1 else max(1, len(lines) // 12)
    hook_t = times[hook_end - 1][1]
    if not tr:
        say("PASS" if 20 <= hook_t <= 120 else "WARN", f"the hook (up to the second chapter) ends at {mmss(hook_t)}; the hits end it at 00:25 to 00:40 (short hook) or 01:00 to 01:50 (long hook)")
    if GREET.search(" ".join(txt[:3])): say("FAIL", "a greeting or channel intro in the first lines (the channel's rule)")
    hook = " ".join(txt[:hook_end])
    if CTA.search(hook): say("FAIL", "a like/subscribe/comment ask inside the hook (the channel's rule)")
    if "?" not in hook: say("WARN", "the hook asks no question; L1 should be asked in it, as a guess where there is money")

    # --- the loop ledger and the device rhythm
    close_i = next((i for i, s in enumerate(txt) if i >= hook_end and CTA.search(s)), len(lines))
    body_end_t = times[close_i - 1][1] if close_i > 0 else total
    if not tr:
        opens, closes = {}, {}
        for i, ln in enumerate(lines):
            for L in as_list(ln.get("open")): opens.setdefault(L, i)
            for L in as_list(ln.get("close")): closes[L] = i
        if not opens:
            say("FAIL", "no loop ledger: mark the line that opens each loop (\"open\": \"L1\") and the line that pays it (\"close\": \"L1\"); L1 is the central question (SKILL.md steps 5 and 9)")
        else:
            never = [L for L in opens if L not in closes]
            if never: say("FAIL", f"loops opened and never paid: {never} (a broken promise; pay it or cut the opening)")
            stray = [L for L in closes if L not in opens or closes[L] < opens[L]]
            if stray: say("WARN", f"loops closed with no earlier opening: {stray}")
            if "L1" not in opens: say("WARN", "no L1: the central question should be loop L1")
            else:
                o, c = opens["L1"], closes.get("L1")
                say("PASS" if times[o][0] <= max(60, hook_t) else "WARN", f"L1 opens at {at(o)}" + ("" if times[o][0] <= max(60, hook_t) else "; the central question belongs in the hook"))
                if c is not None:
                    share = times[c][0] / total
                    say("PASS" if share >= 0.82 else "WARN", f"L1 is answered at {at(c)}, {share:.0%} of the runtime" + ("" if share >= 0.82 else "; once the central question is answered the reason to stay is gone, so answer it in the last 10 to 15%"))
            quick = [L for L in opens if L in closes and times[closes[L]][0] - times[opens[L]][0] < 15]
            if quick: say("WARN", f"loops closed within 15 s of opening: {quick} (a question answered at once is not a loop)")
            # what is open at each moment of the body
            dead, worst_open, run_start = [], 0, None
            for i in range(hook_end, close_i):
                n_open = sum(1 for L in opens if opens[L] <= i and (L not in closes or closes[L] > i))
                worst_open = max(worst_open, n_open)
                if n_open == 0 and run_start is None: run_start = i
                if n_open and run_start is not None:
                    if times[i][0] - times[run_start][0] > 20: dead.append(run_start)
                    run_start = None
            if run_start is not None and body_end_t - times[run_start][0] > 20: dead.append(run_start)
            if dead: say("WARN", f"no loop open from {', '.join(at(i) for i in dead[:4])}: nothing pulls the viewer forward there (open the next loop before closing the last)")
            elif opens: say("PASS", "a loop is open at every moment of the body")
            if worst_open > 4: say("WARN", f"{worst_open} loops open at once somewhere; more than four and the viewer loses track")
            undescribed = [L for L in opens if L not in (doc.get("loops") or {})]
            if undescribed: say("WARN", f"loops with no question written in the top-level \"loops\": {undescribed[:6]}")
        # the rhythm: any device event (a loop opening or closing, a tagged line)
        ev = sorted(times[i][0] for i, ln in enumerate(lines) if hook_end <= i < close_i and (ln.get("open") or ln.get("close") or set(as_list(ln.get("tag"))) & DEVICE_TAGS))
        def longest(points, a, b):
            pts = [a] + sorted(points) + [b]
            return max((pts[k + 1] - pts[k], pts[k]) for k in range(len(pts) - 1))
        g, g_at = longest(ev, hook_t, body_end_t)
        say("PASS" if g <= 120 else "WARN", f"longest stretch with no re-hook, reveal, interrupt or loop event: {g:.0f} s from {mmss(g_at)} (aim: something every 45 to 120 s)")
        rh = [times[i][0] for i, ln in enumerate(lines) if hook_end <= i < close_i and set(as_list(ln.get("tag"))) & {"rehook", "reveal"}]
        g2, g2_at = longest(rh, hook_t, body_end_t)
        say("PASS" if g2 <= 150 else "WARN", f"{len(rh)} re-hooks and reveals in the body; longest gap {g2:.0f} s from {mmss(g2_at)} (never more than 2.5 min)")
        mid = [p for p in rh if 0.35 * total <= p <= 0.65 * total]
        if not mid: say("WARN", "no re-hook or reveal tagged in the middle third (35 to 65%); the biggest twist belongs there")
        ints = [times[i][0] for i, ln in enumerate(lines) if "interrupt" in as_list(ln.get("tag"))]
        say("INFO", f"{len(ints)} pattern interrupts tagged ({len(ints) / max(.1, mins):.1f}/min; the toolkit asks for one every 45 to 90 s, varied)")
        gain_i = [i for i, ln in enumerate(lines) if "gain" in as_list(ln.get("tag"))]
        if not doc.get("gain") or not gain_i: say("WARN", "no viewer's gain: set the top-level \"gain\" and tag the line that promises it (\"tag\": \"gain\")")
        elif times[gain_i[0]][0] > 75: say("WARN", f"the viewer's gain is promised at {at(gain_i[0])}; promise it in the first minute")

    # --- the ear
    longl = [i for i, s in enumerate(txt) if max(len(words(x)) for x in sentences(s)) > 22]
    if longl: say("WARN", f"{len(longl)} lines with a sentence over 22 words (lines {first_lines(longl)}); split them, one idea per sentence")
    heavy = [i for i, s in enumerate(txt) if numbers(s) > 2]
    if heavy: say("WARN", f"{len(heavy)} lines with three or more numbers (lines {first_lines(heavy)}); the ear holds one number at a time")
    dense, k = [], 0
    for i in range(len(lines)):
        while times[i][0] - times[k][0] > 30: k += 1
        n = sum(numbers(txt[j]) for j in range(k, i + 1))
        if n > 6 and (not dense or times[i][0] - times[dense[-1]][0] > 30): dense.append(i)
    if dense: say("WARN", f"more than six numbers inside half a minute around {', '.join(mmss(times[i][0]) for i in dense[:6])}; keep the three payoff numbers and make the rest felt, not counted")
    npm = sum(numbers(s) for s in txt) / max(0.1, mins)
    say("INFO", f"numbers {npm:.1f}/min (the hits: economics 3.9 to 5.3, compare 8.7, story 3.1 to 3.4, person 1.1 to 6.9)")
    untagged, chain, run = [], [], 0
    for i, s in enumerate(txt):
        speech = is_speech(s)
        tag_before = i and SPEECH.search(txt[i - 1]) and not is_speech(txt[i - 1])   # a tag line ("फिर वो धीरे से कहते हैं।") licenses the next quote
        if speech and not SPEECH.search(s) and not tag_before: untagged.append(i)
        run = run + 1 if speech else 0
        if run == 3: chain.append(i - 2)
    if untagged: say("WARN", f"{len(untagged)} lines of speech with no speaker named in them or just before (lines {first_lines(untagged)}); one narrator's voice cannot show who is talking, so name the speaker first")
    if chain: say("WARN", f"three or more speech lines in a row at lines {first_lines(chain)}; after two turns the narrator speaks again")
    toks = [[w for w in re.sub(r"[,।?!:;\"'“”‘’]", " ", s).split()] for s in txt]
    freq = Counter(w for t in toks for w in t if w not in STOP and len(w) > 1)
    common = {w for w, _ in freq.most_common(8)}    # names and the topic noun repeat by nature
    grams = Counter()
    for t in toks:
        for j in range(len(t) - 2):
            g3 = tuple(t[j:j + 3])
            if sum(1 for w in g3 if w not in STOP) >= 2 and not (set(g3) & common): grams[g3] += 1
    rep = [(" ".join(g), n) for g, n in grams.most_common() if n >= 3]
    if rep: say("WARN", "phrases said three or more times: " + "; ".join(f"\"{g}\" x{n}" for g, n in rep[:8]) + " (fine only as a deliberate callback)")
    for name, pat, limit in (("AI or template phrasing", AI, 0), ("meta orders to the viewer", META, 1), ("the 'सिर्फ X नहीं, Y' reframe", REFRAME, 1)):
        hit = [i for i, s in enumerate(txt) if pat.search(s)]
        if len(hit) > limit: say("WARN", f"{name} at lines {first_lines(hit)} (allowed: {limit})")
    narr_q = [i for i, s in enumerate(txt) if hook_end <= i < close_i and s.rstrip().endswith("?") and not is_speech(s)]
    qpm = len(narr_q) / max(0.1, (body_end_t - hook_t) / 60)
    if qpm > 1.5: say("WARN", f"{len(narr_q)} narrator questions in the body ({qpm:.1f}/min); a question after every scene sounds like a template, so let the scene carry its own tension")
    if not tr:
        anchors = []
        for i, s in enumerate(txt):
            for m in TIME_ANCHOR.finditer(s): anchors.append(f"{mmss(times[i][0])} {m.group(0).strip()}")
        if anchors: say("INFO", "time anchors, for the time-line pass: " + " | ".join(anchors[:24]))

    # --- the close
    if close_i < len(lines) and times[close_i][0] < 0.85 * total:
        say("WARN", f"the first ask is at {at(close_i)} ({times[close_i][0] / total:.0%}); keep every ask to the last 90 seconds")
    if close_i == len(lines): say("WARN", "no closing ask (one comment question or one 'send it to a friend')")
    else:
        end = [i for i in range(len(lines)) if times[i][0] >= min(times[close_i][0], total - 90)]
        asks = [i for i in end if CTA.search(txt[i]) or NEXT.search(txt[i]) or ASKQ.search(txt[i])]
        say("PASS" if len(asks) <= 3 else "WARN", f"{len(asks)} asks in the close (lines {first_lines(asks)})" + ("" if len(asks) <= 3 else "; keep one comment question, one ask and the next video, then the sign-off"))
    tail = " ".join(txt[int(len(txt) * 0.88):])
    if not NEXT.search(tail): say("WARN", "no next video named in the close")
    opening = set(w for w in words(" ".join(txt[:3])) if len(w) >= 4 and w not in STOP)
    back = opening & set(words(" ".join(txt[int(len(txt) * 0.6):])))
    say("PASS" if len(back) >= 2 else "WARN", f"callback to the opening scene: {len(back)} shared words" + ("" if len(back) >= 2 else " (the hits end back in the opening scene)"))

    # --- honesty
    src = doc.get("sources") or []
    if fmt != "?" and not src: say("FAIL", "no sources in script.json")
    elif fmt != "?" and len(src) < 3: say("WARN", f"only {len(src)} sources")
    if not tr:
        nofact = [i for i, (ln, s) in enumerate(zip(lines, txt)) if MONEY.search(s) and not ln.get("facts")]
        if nofact: say("WARN", f"{len(nofact)} lines state a number with no research id in \"facts\" (lines {first_lines(nofact)}); link each to its F or M row")
        if research_text is not None:
            known = set(re.findall(r"\b[FM]\d+\b", research_text))
            used = {f for ln in lines for f in as_list(ln.get("facts"))}
            missing = sorted(used - known)
            if known and missing: say("WARN", f"research ids used in script.json but not in the research file: {missing[:10]}")
            if not known and used: say("WARN", "the research file has no F/M ids yet; number its rows so the fact links can be checked")
    srcd = [i for i, s in enumerate(txt) if SOURCED.search(s)]
    if len(srcd) > 2: say("WARN", f"sources read aloud {len(srcd)} times (lines {first_lines(srcd)}); keep them in the research file, two authority lines at most")
    dis = [i for i, s in enumerate(txt) if DISCLAIM.search(s)]
    if dis: say("FAIL", f"a line saying the characters or story are made up (lines {first_lines(dis)}); tell it straight")
    told = [i for i, s in enumerate(txt) if TOLD.search(s)]
    if told: say("WARN", f"feelings told instead of caused at lines {first_lines(told)}")
    book = [i for i, s in enumerate(txt) if BOOKISH.search(s)]
    if len(book) > 2: say("WARN", f"textbook Hindi in {len(book)} lines (lines {first_lines(book)}); use the everyday word")
    ban = [i for i, s in enumerate(txt) if BANNED.search(s)]
    if ban: say("FAIL", f"stock lines that promise nothing at lines {first_lines(ban)}; name the specific thing coming instead")

    # --- chapters and the shot plan
    chaps = [ln.get("chapter") for ln in lines if ln.get("chapter")]
    cat = [c for c in chaps if CATEGORY.match(c)]
    if cat: say("FAIL", f"chapters named for a category, not for what happens: {cat[:4]}")
    elif chaps: say("PASS", f"{len(chaps)} chapters, named for events")
    if not tr:
        nokind = [i for i, ln in enumerate(lines) if ln.get("kind") not in KINDS]
        if nokind: say("WARN", f"{len(nokind)} lines without a valid kind (still, card, hero): lines {first_lines(nokind)}")
        cards = [i for i, ln in enumerate(lines) if ln.get("kind") == "card"]
        twin = [i for i in cards if i - 1 in cards]
        if twin: say("WARN", f"two cards in a row at lines {first_lines(twin)}")
        scr = [ln.get("screen") for ln in lines if ln.get("screen")]
        bad = [s for s in scr if DEVANAGARI.search(s) or len(words(s)) > 6]
        if bad: say("WARN", f"{len(bad)} screen texts are Devanagari or over 6 words, e.g. {bad[0]!r}")
        if len(scr) / len(lines) > 0.35: say("WARN", f"screen text on {len(scr) / len(lines):.0%} of lines; keep it rare")
        run, worst = 0, 0
        for ln in lines:
            run = 0 if ln.get("visual") else run + 1; worst = max(worst, run)
        if worst > 3: say("WARN", f"{worst} lines in a row with no visual; a new picture every one to three lines")
    return out

def write_md(doc, path):
    """the readable script: what the owner reviews before anything is voiced or drawn"""
    lines = doc["lines"]; times, total = timing(doc)
    opens, closes = {}, {}
    for i, ln in enumerate(lines):
        for L in as_list(ln.get("open")): opens.setdefault(L, i)
        for L in as_list(ln.get("close")): closes[L] = i
    n_words = sum(len(words(l.get("hi"))) for l in lines)
    o = [f"# {doc.get('title', 'Untitled')}", ""]
    if doc.get("alt_titles"): o.append("**Other titles:** " + " · ".join(doc["alt_titles"]) + "  ")
    if doc.get("thumbnail"): o.append(f"**Thumbnail words:** {doc['thumbnail']}  ")
    o.append(f"**Format:** {doc.get('format', '?')} · **Runtime:** about {total / 60:.1f} min ({n_words} words at {WPM} wpm)  ")
    if doc.get("question"): o.append(f"**The central question (L1):** {doc['question']}  ")
    if doc.get("answer"): o.append(f"**The answer:** {doc['answer']}  ")
    if doc.get("gain"): o.append(f"**What the viewer walks away able to do:** {doc['gain']}  ")
    if opens:
        o += ["", "## Open loops", "", "| Loop | The viewer's question | Opens | Pays off |", "|---|---|---|---|"]
        for L in sorted(opens, key=lambda x: opens[x]):
            q = (doc.get("loops") or {}).get(L, "")
            c = closes.get(L)
            o.append(f"| {L} | {q} | {mmss(times[opens[L]][0])} (line {opens[L] + 1}) | " + (f"{mmss(times[c][0])} (line {c + 1})" if c is not None else "**never**") + " |")
    o += ["", "---"]
    for i, ln in enumerate(lines):
        if ln.get("chapter"): o += ["", f"## {mmss(times[i][0])} · {ln['chapter']}", ""]
        marks = [f"opens {L}" for L in as_list(ln.get("open"))] + [f"pays {L}" for L in as_list(ln.get("close"))] + as_list(ln.get("tag"))
        m = (" **[" + ", ".join(marks) + "]**") if marks else ""
        o.append(f"`{mmss(times[i][0])}` {ln.get('hi', '')}{m}  ")
        bits = [b for b in (ln.get("kind"), ln.get("visual"), ("screen: " + ln["screen"]) if ln.get("screen") else None) if b]
        if bits: o.append(f"<sub>{' · '.join(bits)}</sub>")
        o.append("")
    if doc.get("sources"):
        o += ["---", "", "## Sources", ""] + [f"- {s}" for s in doc["sources"]]
    Path(path).write_text("\n".join(o) + "\n", encoding="utf-8")

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
    proj = Path(path).resolve().parent
    if "--md" in a:
        out = proj / f"{proj.name}-script.md"; write_md(doc, out); print("wrote", out); return
    research = next(iter(sorted(proj.glob("*-research.md"))), None) if not tr else None
    out = check(doc, research.read_text(encoding="utf-8") if research else None)
    if not tr:                              # a project script: the engine and the beat sheet come first (SKILL.md steps 4 and 5)
        for kind, step in (("engine", 4), ("beats", 5)):
            if not list(proj.glob(f"*-{kind}.md")): out.insert(0, ("FAIL", f"no <slug>-{kind}.md: write the {kind} before the lines (SKILL.md step {step})"))
    print(f"\n  {doc.get('title', path)}  [{doc.get('format', '?')}]")
    for lvl, msg in out: print(f"  {lvl:4}  {msg}")
    fails = sum(1 for l, _ in out if l == "FAIL"); warns = sum(1 for l, _ in out if l == "WARN")
    print(f"\n  {fails} FAIL, {warns} WARN" + ("  - fix the FAILs before the voice" if fails else ""))
    print("  The checker finds mechanical faults only. Never add a line to satisfy it; the story is judged by the revision passes.")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
