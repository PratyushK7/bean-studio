"""Mechanical checks for a Jad Tak script.json, run before the two hand-scored evaluations (references/evaluation.md).
Hard fails exit with code 1. No API, no cost.

  python scriptcheck.py <project folder or script.json> [--ledger FILE ...] [--out report.md]

Reads the ledger named in script.json ("ledger"), plus any --ledger files, plus this skill's references/reference-claims.md
(so the reference-video ids RZ.., SM.., AG.. resolve). Times come from scratch/scratch-narration-lines.json when it matches the
script, otherwise from 160 words a minute."""
from collections import Counter
import json, re, sys, unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
WPM = 160
BANDS = {  # words, re-hook gap (s), a reveal must land by (s), most sections (script-base: few sections, one story)
    "short": {"words": (1600, 1900), "gap": 60, "reveal_by": 90, "chapters": 3},
    "standard": {"words": (2900, 3500), "gap": 90, "reveal_by": 180, "chapters": 5},
    "long": {"words": (5600, 6400), "gap": 120, "reveal_by": 240, "chapters": 7},
}
KINDS = {"still", "archive", "card", "map"}
PULLS = {"hook", "rehook", "reveal", "question", "handoff", "promise", "stamp"}
QUOTE_OK = {"established", "reported", "account", "verified"}
NOT_EVENTS = {"dramatized", "unsupported"}
ATTRIB = ["के मुताबिक़", "के मुताबिक", "के अनुसार", "लिखते हैं", "लिखती हैं", "लिखा है", "बताते हैं", "बताती हैं",
          "कहा जाता है", "माना जाता है", "सुनाते हैं", "सुनाई जाती है", "शोध-ग्रंथ", "रिपोर्ट के", "किताब में", "दावा"]
# one regex, longest phrase first, so "शोध-ग्रंथ के मुताबिक़" counts as two phrases and "के मुताबिक़" never as two
NFD = lambda t: unicodedata.normalize("NFD", t)  # क़ can be one code point or two; compare decomposed
ATTRIB_RE = re.compile("|".join(re.escape(NFD(x)) for x in sorted(set(ATTRIB), key=len, reverse=True)))
DISCLAIM = ["हमने नहीं देखा", "हमने नहीं देखी", "हमने नहीं सुना", "पुष्टि नहीं", "सत्यापित नहीं", "दावा किया जाता है",
            "प्रमाण नहीं", "कोई सबूत नहीं"]
FORMAL = ["निर्णय", "अवधारणा", "प्राप्त", "सदैव", "परन्तु", "किंतु", "तत्पश्चात", "उपरांत", "अत्यंत", "आवश्यकता",
          "एकत्र", "के माध्यम से", "प्रतीत", "इस प्रकार", "उल्लेख", "विस्तृत"]
PROMPT_BANNED = ["illustration", "artist's impression", "artist impression", "ai generated", "ai-generated", "approximate",
                 "not to scale", "reportedly", "as claimed", "legend says", "archival photo", "archive photo", "vintage photo",
                 "old photograph", "press photo", "newspaper clipping", "disclaimer", "claim", "चित्रण"]
CARD_BANNED = ["चित्रण", "लगभग", "दावा", "शोध-ग्रंथ", "के मुताबिक़", "के हवाले से", "वेबसाइट", "हमने नहीं"]
CTA_HARD = ["सब्सक्राइब", "लाइक", "शेयर"]
OPENING_BAN = ["आज हम", "इस वीडियो में", "दोस्तों"]


def ledger_rows(paths):
    """{id: status word} from every markdown table row whose first cell is an id like F12 or RZ07."""
    rows = {}
    for p in paths:
        if not p or not Path(p).exists(): continue
        status_col = None
        for raw in Path(p).read_text(encoding="utf-8").splitlines():
            if not raw.startswith("|"):
                m = re.match(r"^\s*-\s*\*\*([A-Z]{1,3}\d+)\b", raw)  # older research files list some facts as bullets
                if m and m.group(1) not in rows: rows[m.group(1)] = "unknown"
                status_col = None if not raw.strip() else status_col; continue
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            low = [c.lower() for c in cells]
            if "status" in " ".join(low) and not re.match(r"^[A-Z]{1,3}\d+$", cells[0]):
                status_col = next((i for i, c in enumerate(low) if c.startswith("status") or "verification" in c), None); continue
            if re.match(r"^[A-Z]{1,3}\d+$", cells[0]):
                st = cells[status_col] if status_col is not None and status_col < len(cells) else cells[-1]
                m = re.search(r"(established|reported|account|video-reported|conflicting|dramatized|unsupported|verified|disputed|legend|estimate)", st.lower())
                rows[cells[0]] = m.group(1) if m else st.lower()[:30]
    return rows



def said(l):
    """the words the narrator speaks: the Devanagari `say` of a Hinglish script, else `text`"""
    return l.get("say") or l.get("text", "")


def main():
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    target = Path(args[0]); folder = target if target.is_dir() else target.parent
    sj = target if target.suffix == ".json" else folder / "script.json"
    doc = json.loads(sj.read_text(encoding="utf-8")); lines = doc.get("lines", [])
    extra = [args[i + 1] for i, a in enumerate(args) if a == "--ledger"]
    out = next((args[i + 1] for i, a in enumerate(args) if a == "--out"), None)
    ledgers = [folder / doc["ledger"]] if doc.get("ledger") else sorted(folder.glob("*-ledger.md")) or sorted(folder.glob("*-research.md"))
    rows = ledger_rows(list(ledgers) + extra + [SKILL / "references/reference-claims.md"])
    band = BANDS.get(doc.get("band", "standard"), BANDS["standard"])
    hard, warn, info = [], [], []

    # timings: real scratch timings when they match, else 160 wpm
    tfile = folder / "scratch/scratch-narration-lines.json"
    times = None
    if tfile.exists():
        t = json.loads(tfile.read_text(encoding="utf-8"))
        if len(t) == len(lines): times = [(x["start"], x["end"]) for x in t]
    if not times:
        times, s = [], 0.0
        for l in lines:
            d = len(said(l).split()) / WPM * 60 + 0.35; times.append((s, s + d)); s += d
        info.append("timings estimated at 160 words a minute (no matching scratch narration)")
    total = times[-1][1] if times else 0
    mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    words = sum(len(said(l).split()) for l in lines)

    # H1b Hinglish scripts: `text` is shown (Latin), `say` is spoken (Devanagari); both must be the same sentences
    if any(l.get("say") for l in lines):
        for n, l in enumerate(lines, 1):
            t, v = l.get("text", ""), l.get("say", "")
            if not v: hard.append(f"L{n}: no 'say' (every line needs the Devanagari text when any line has one)"); continue
            if re.search(r"[ऀ-ॿ]", t): warn.append(f"L{n}: Devanagari in the shown Hinglish text")
            if len(re.findall(r"[.?!]+", t)) != len(re.findall(r"[।?!]+", v)):
                hard.append(f"L{n}: 'text' and 'say' have different sentence counts")
            if re.search(r"[ऀ-ॿ]", json.dumps(l.get("card", {}).get("props", {}), ensure_ascii=False)):
                warn.append(f"L{n}: Devanagari on a card in a Hinglish script")

    # H1 schema
    for n, l in enumerate(lines, 1):
        for k in ("text", "kind", "visual"):
            if not l.get(k): hard.append(f"L{n}: missing '{k}'")
        if l.get("kind") and l["kind"] not in KINDS: hard.append(f"L{n}: kind '{l['kind']}' is not one of {sorted(KINDS)}")

    # H2 to H4 facts, quotes, dramatized material
    for n, l in enumerate(lines, 1):
        ids = l.get("facts", [])
        for i in ids:
            if i not in rows: hard.append(f"L{n}: fact id {i} is not in the ledger")
        sts = [rows.get(i, "") for i in ids]
        text = said(l)
        if re.search(r'["“”]', text):
            if not any(s in QUOTE_OK for s in sts):
                hard.append(f"L{n}: quotation without a quotable ledger row (needs established/reported/account): {ids or 'no ids'}")
        if ids and all(s in NOT_EVENTS for s in sts):
            hard.append(f"L{n}: rests only on dramatized/unsupported claims {ids}")

    # H5 prompts
    for n, l in enumerate(lines, 1):
        p = l.get("prompt", "")
        if not p: continue
        if re.search(r"[ऀ-ॿ]", p): hard.append(f"L{n}: Devanagari in the image prompt")
        for b in PROMPT_BANNED:
            if b in p.lower(): hard.append(f"L{n}: prompt contains '{b}' (prompts describe the picture only)")

    # H5b no footnote-style labels on screen (owner's rule)
    for n, l in enumerate(lines, 1):
        shown = NFD(json.dumps(l.get("card", {}).get("props", {}), ensure_ascii=False))
        for b in CARD_BANNED:
            if NFD(b) in shown: hard.append(f"L{n}: on-screen label '{b}' in the card (no footnotes on screen)")

    # H6 opening
    first = " ".join(said(l) for l in lines[:2])
    for b in OPENING_BAN:
        if b in first: hard.append(f"opening: '{b}' in the first two lines (open inside a story)")
    if lines and lines[0].get("beat") in ("cta", "method"): hard.append("opening: the first line is a CTA or a method note")
    reveal_t = next((times[n][0] for n, l in enumerate(lines) if l.get("beat") in ("reveal", "promise")), None)
    if any(l.get("beat") for l in lines):
        if reveal_t is None or reveal_t > band["reveal_by"]:
            hard.append(f"opening: no reveal or promise by {mmss(band['reveal_by'])} (first at {mmss(reveal_t) if reveal_t is not None else 'never'})")
    else:
        warn.append("no 'beat' fields: re-hook spacing and the opening deadline could not be checked")

    # H7 loops
    opened = {}
    for n, l in enumerate(lines, 1):
        for x in l.get("opens", []): opened.setdefault(x, n)
        for x in l.get("closes", []):
            if x not in opened: warn.append(f"L{n}: closes loop {x} that was never opened")
            else: opened[x] = None
    for x, n in opened.items():
        if n is not None: hard.append(f"loop {x} opened at L{n} is never closed")

    # H8 attribution density, disclaimers
    hits = []
    for n, l in enumerate(lines):
        c = len(ATTRIB_RE.findall(NFD(said(l))))
        if c: hits += [times[n][0]] * c
    for i in range(len(hits)):
        win = [h for h in hits if hits[i] <= h < hits[i] + 30]
        if len(win) > 2:
            hard.append(f"attribution: {len(win)} source phrases within 30 s from {mmss(hits[i])} (limit 2)"); break
    if total and len(hits) / (total / 60) > 1.0: warn.append(f"attribution: {len(hits)} phrases in {mmss(total)} (more than one a minute)")
    disc = [(n + 1, d) for n, l in enumerate(lines) for d in DISCLAIM if d in said(l)]
    if len(disc) > 2: hard.append(f"disclaimers: {len(disc)} in the script (limit 2): " + ", ".join(f"L{n} '{d}'" for n, d in disc))

    # H9 CTA position
    for n, l in enumerate(lines):
        if times[n][0] < 0.9 * total:
            t = said(l)
            if any(c in t for c in CTA_HARD): hard.append(f"L{n + 1}: like/share/subscribe before the last 10% ({mmss(times[n][0])})")
            elif "कमेंट" in t:
                (warn if doc.get("band") == "long" else hard).append(f"L{n + 1}: comment prompt before the last 10% ({mmss(times[n][0])})")

    # warnings: length, sentences, words, rhythm
    lo, hi = band["words"]
    if not lo <= words <= hi: warn.append(f"length: {words} words for band '{doc.get('band', 'standard')}' ({lo} to {hi})")
    long_s = [(n, len(said(l).split())) for n, l in enumerate(lines, 1) if len(said(l).split()) > 22]
    for n, w in long_s: warn.append(f"L{n}: {w} words in one sentence (ceiling 22)")
    for n, l in enumerate(lines, 1):
        t = said(l)
        for f in FORMAL:
            if f in t: warn.append(f"L{n}: formal word '{f}'")
        if re.search(r"[A-Za-z]", t): warn.append(f"L{n}: Latin letters in narration (the voice reads Devanagari)")
        if re.search(r"[/%&()\[\]]|डॉ\.|किमी", t): warn.append(f"L{n}: symbol or abbreviation in narration")
        if l.get("kind") == "still" and not (l.get("frame") or l.get("prompt")): warn.append(f"L{n}: still with no frame and no prompt")
        if l.get("kind") in ("card", "map") and not l.get("card"): warn.append(f"L{n}: {l['kind']} with no card spec")
    if sum(said(l).count("दोस्तों") for l in lines) > 1: warn.append("'दोस्तों' more than once")
    qpm = sum(said(l).count("?") for l in lines) / max(total / 60, 1)
    if qpm > 2: warn.append(f"{qpm:.1f} questions a minute (aim for 2 or fewer)")
    pulls = [times[n][0] for n, l in enumerate(lines) if l.get("beat") in PULLS] + [total]
    prev = 0.0
    for t in pulls:
        if t - prev > band["gap"]: warn.append(f"re-hook gap {mmss(prev)} to {mmss(t)} ({int(t - prev)} s; band limit {band['gap']} s)")
        prev = t
    starts = [n for n, l in enumerate(lines) if l.get("chapter")]
    if len(starts) > band["chapters"]: warn.append(f"{len(starts)} chapters (band allows {band['chapters']}; each one breaks the story)")
    for b in starts[1:]:
        if lines[b - 1].get("beat") not in ("handoff", "rehook", "question", "reveal"):
            warn.append(f"L{b}: last line of a chapter is not a handoff/rehook/question/reveal")
    kinds = {k for l in lines[-4:] for k, ws in (("subscribe", CTA_HARD), ("comment", ["कमेंट"])) if any(w in said(l) for w in ws)}
    if len(kinds) > 1: hard.append("more than one call to action at the end (script-base: one, ideally the next video)")
    if not any(l.get("beat") == "cta" for l in lines[-4:]): warn.append("no call to action in the last lines")
    opens = Counter(said(l).split()[0].strip(",") for l in lines if said(l).split())
    for w, c in opens.items():
        if w in ("और", "लेकिन", "फिर") and c > len(lines) / 15:
            warn.append(f"{c} lines start with '{w}' (aim for at most {len(lines) // 15}; vary the openings)")

    rep = [f"# scriptcheck: {doc.get('title', sj.name)}", "",
           f"{len(lines)} lines · {words} words · about {mmss(total)} · band {doc.get('band', 'standard')} · ledger ids known: {len(rows)}", "",
           f"## Hard fails: {len(hard)}"] + [f"- {h}" for h in hard] + ["", f"## Warnings: {len(warn)}"] + [f"- {w}" for w in warn] + \
          ["", "## Notes"] + [f"- {i}" for i in info]
    text = "\n".join(rep) + "\n"
    sys.stdout.reconfigure(encoding="utf-8"); print(text)
    if out: Path(out).write_text(text, encoding="utf-8")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
