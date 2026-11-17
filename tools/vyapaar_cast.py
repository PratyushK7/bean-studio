"""Decoding Vyapaar voice cast: who speaks which words, and which voice each person gets (Sarvam for the paid voice, Kokoro for the free one).

A script line stays ONE line (so the shots, the graphics and the timings keep their numbers). To give a person their own voice, mark the line:

    {"hi": "रमेश जी हंसकर कहते हैं, धनतेरस के एक दिन में तीस लाख बिका है, बेटा।", "say": {"who": "ramesh", "from": "धनतेरस के एक दिन"}}

`from`: where the person's words start (the narrator reads everything before it); `to` (optional): where they end (the narrator reads the rest).
No `from` means the whole line is the person's. A line may hold a list of such marks. A line with no `say` is the narrator's.

The cast: channels/<channel>/voice-cast.json (the narrator and the pool of voices) and <project>/voice-cast.json (the people of this video). Each entry:
    {"label": "Ramesh, 52, the shop owner", "sarvam": {"speaker": "rahul", "pace": 0.9, "temperature": 0.7}, "kokoro": {"voice": "hm_psi", "speed": 0.95, "pitch": 1.0}}
`pitch` (Kokoro only) is a factor applied after speaking: above 1 is higher and younger, below 1 is lower and older. Sarvam voices differ by speaker; there is no pitch dial.
Tools: vyapaar_voice.py (Sarvam, paid), preview.py (Kokoro, free) and Bean Studio's Voice cast panel all read this file.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NARRATOR = "narrator"


def channel_dir(proj):
    return Path(proj).resolve().parent.parent            # channels/hindi/videos/<slug> -> channels/hindi


def load(proj):
    """the channel's cast with the project's cast on top: {who: entry} plus the pool under "_pool" """
    out = {}
    for f in (channel_dir(proj) / "voice-cast.json", Path(proj) / "voice-cast.json"):
        if not f.exists(): continue
        try: d = json.loads(f.read_text(encoding="utf-8-sig"))                # -sig: a file saved with a byte-order mark still reads
        except Exception as e: raise SystemExit(f"{f} is not valid JSON ({e}): fix it, the cast would otherwise be ignored")
        for k, v in d.items():
            if k == "_pool": out["_pool"] = v
            elif not k.startswith("_"): out[k] = {**out.get(k, {}), **v}
    return out


def parts(line):
    """[(who, text)] for one script line, in order; the narrator for everything that is not marked"""
    t = line["hi"]; say = line.get("say")
    if not say: return [(NARRATOR, t)]
    items = say if isinstance(say, list) else [say]
    out, pos = [], 0
    for it in items:
        a = t.find(it["from"], pos) if it.get("from") else pos
        if a < 0: raise ValueError(f"'from' text not found in the line: {it['from']!r} in {t!r}")
        b = t.find(it["to"], a) if it.get("to") else len(t)
        if b < 0: raise ValueError(f"'to' text not found in the line: {it['to']!r} in {t!r}")
        if a > pos: out.append((NARRATOR, t[pos:a].strip()))
        out.append((it["who"], t[a:b].strip())); pos = b
    if pos < len(t): out.append((NARRATOR, t[pos:].strip()))
    return [(w, x) for w, x in out if x]


def speakers(lines):
    """{who: how many lines they speak in}"""
    n = {}
    for l in lines:
        for w, _ in parts(l):
            if w != NARRATOR: n[w] = n.get(w, 0) + 1
    return n


def sarvam_cfg(cast, who):
    base = cast.get(NARRATOR, {}).get("sarvam", {})
    return {**base, **cast.get(who, {}).get("sarvam", {})}


def kokoro_cfg(cast, who):
    base = cast.get(NARRATOR, {}).get("kokoro", {})
    return {**base, **cast.get(who, {}).get("kokoro", {})}


def validate(proj):
    """[problem] before any voice is made: a marked line whose words cannot be found, a person with no voice, a voice that is not in the pool"""
    proj = Path(proj); problems = []
    try: lines = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    except Exception as e: return [f"cannot read script.json: {e}"]
    cast = load(proj); pool = cast.get("_pool", {})
    for i, l in enumerate(lines, 1):
        try: parts(l)
        except Exception as e: problems.append(f"line {i}: {e}")
    for who, n in speakers(lines).items():
        if who not in cast: problems.append(f"{who} speaks in {n} line(s) but has no voice in voice-cast.json (they would be read by the narrator)")
    sp, kk = set(pool.get("sarvam", [])), set(pool.get("kokoro", []))
    for who, e in cast.items():
        if who.startswith("_"): continue
        if sp and e.get("sarvam", {}).get("speaker") and e["sarvam"]["speaker"] not in sp: problems.append(f"{who}: Sarvam speaker {e['sarvam']['speaker']!r} is not one of the tried voices {sorted(sp)}")
        if kk and e.get("kokoro", {}).get("voice") and e["kokoro"]["voice"] not in kk: problems.append(f"{who}: Kokoro voice {e['kokoro']['voice']!r} is not one of {sorted(kk)}")
    return problems
