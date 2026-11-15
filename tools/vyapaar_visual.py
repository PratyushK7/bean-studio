"""Decoding Vyapaar visual planning: the visual bible, a project's visual plan, structured image prompts, character references.

    python tools/vyapaar_visual.py bible                          # channels/hindi/visual-bible.json -> visual-bible.md (the readable copy)
    python tools/vyapaar_visual.py draft <project>                # script.json -> visual-plan.draft.json, a starting point to art-direct
    python tools/vyapaar_visual.py prompts <project> [--batch 30] # visual-plan.json -> prompts/*.txt, images-index.json, prompts/REFS.md
    python tools/vyapaar_visual.py validate <project>             # continuity-report.md: characters, references, conflicts, graphics numbers
    python tools/vyapaar_visual.py show <project> S014            # one shot's prompt and its references

The visual plan (<project>/visual-plan.json) is written by the art director (the hindi-case-study skill, production step), not by regex:
    characters  id -> name, age, face, skin, hair, body, clothing, accessories, features, identity (the words every prompt repeats),
                sheet (an approved reference slot number, or omitted to make one), locations, props
    locations   id -> name, prompt (what the place looks like), look (its default lighting)
    shots       one entry per picture or graphic: id, lines, purpose, kind, location, look, size, angle, chars {id: expression and body},
                action, fg / mg / bg, placement, light, props, continuity, avoid, candidates, reuse (an existing image slot), same_as
                (another shot's picture), camera (a planned move for the renderer), motion (an image-to-video brief), graphic (for cards)
Slot numbers are stable: visual-slots.json remembers which picture number each shot owns, so re-running never renumbers existing
pictures, and only slots with no picture, a rejected picture or a changed prompt go into the prompt files.
"""
import argparse, hashlib, json, re, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIBLE = ROOT / "channels" / "hindi" / "visual-bible.json"
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
CAND_BASE = 5000                      # a second candidate for slot n is slot 5000 + n


# ---------------------------------------------------------------- loading
def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return out


def load_bible(proj=None):
    b = json.loads(BIBLE.read_text(encoding="utf-8"))
    if proj and (Path(proj) / "visual-bible.json").exists():
        b = merge(b, json.loads((Path(proj) / "visual-bible.json").read_text(encoding="utf-8")))
    return b


def load_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def script_lines(proj, script=None):
    s = load_json(Path(proj) / (script or "script.json"))
    return s["lines"] if isinstance(s, dict) else s


def image_for(proj, n):
    return next((f for f in (Path(proj) / "images").glob(f"{int(n):03d}.*") if f.suffix.lower() in IMG_EXT), None)


def have_images(proj):
    d = Path(proj) / "images"
    return {int(f.stem) for f in d.iterdir() if f.stem.isdigit() and f.suffix.lower() in IMG_EXT} if d.is_dir() else set()


def lines_of(shot):
    v = shot.get("lines", [])
    return [v] if isinstance(v, int) else list(v)


# ---------------------------------------------------------------- prompts
TIGHT = {"medium_close", "close", "extreme_close", "insert", "macro", "reaction"}
ANGLE_WORDS = re.compile(r"eye level|slightly (?:high|low) angle(?:, looking (?:down|up))?|top-down view")


def identity(c):
    """the face-and-hair words every prompt repeats (clothing is separate, so a costume can change it)"""
    return c.get("identity") or ", ".join(x for x in (c.get("age") and f"{c['age']} years old", c.get("face"), c.get("hair"), c.get("features")) if x)


def sheet_prompt(c, bible):
    if c.get("group"):                                               # a pair or a family on one sheet
        who = f"{c['name']}: {c.get('identity', '')}; {c.get('clothing', '')}".strip("; ")
    else:
        age = c.get("age") and (f"{c['age']} years old" if str(c["age"]).isdigit() else str(c["age"]))
        who = ", ".join(x for x in (c["name"], age, c.get("face"), c.get("skin") and c["skin"] + " skin", c.get("hair"), c.get("body"),
                                    c.get("clothing") and "wearing " + c["clothing"], c.get("accessories"), c.get("features")) if x)
    return " ".join([bible["characters"]["sheet_prompt"].format(who=who), bible["style"]["prompt"],
                     "No text, labels or colour swatches; " + (f"only these {c['group']} people." if c.get("group") else "only this one person.")])


def shot_prompt(shot, plan, bible):
    """the self-contained prompt for one picture, in order of what matters most to the image"""
    size = bible["shots"][shot["size"]]["prompt"]
    if shot.get("lens"): size = re.sub(r"\d+mm( macro)? lens", shot["lens"], size)
    if shot.get("angle"):
        ang = bible["angles"].get(shot["angle"], shot["angle"])
        size = ANGLE_WORDS.sub(ang, size) if ANGLE_WORDS.search(size) else f"{size}, {ang}"
    parts = [f"{size}. {shot['action'].rstrip('.')}."]
    chars = shot.get("chars") or {}
    for cid, how in chars.items():
        c = plan["characters"][cid]
        wear = (shot.get("costume") or {}).get(cid) or c.get("clothing")
        if re.match(r"\s*only\b", how or ""):                       # a hand or feet shot: no face words, only what is visible
            part = re.sub(r"\s+(are|is) visible$", "", re.sub(r"\b(his|her) ", "", how.split("only", 1)[1].strip().rstrip(".")))
            parts.append(f"Only {c['name']}'s {part} in the frame: {c.get('skin', 'natural brown')} skin, {wear}.")
            continue
        who = c.get("short") or identity(c)                          # the sheet carries the face: three to five details are enough
        parts.append(f"{c['name']}: {who}" + (f", wearing {wear}" if wear else "") + (f"; {how.rstrip('.')}." if how else "."))
    loc = plan.get("locations", {}).get(shot.get("location") or "", {})
    layers = "; ".join(f"{k} {shot[v]}" for k, v in (("foreground:", "fg"), ("middle ground:", "mg"), ("background:", "bg")) if shot.get(v))
    tight = shot["size"] in TIGHT and loc.get("short")             # a tight shot shows little of the room: a hint of the place is enough
    where = (cap(loc["short"]) + ".") if tight else (loc.get("prompt", "").rstrip(".") + "." if loc.get("prompt") else "")
    setting = " ".join(x for x in (where, (layers[0].upper() + layers[1:] + ".") if layers else "") if x)
    if setting: parts.append(setting)
    look = bible["looks"][shot.get("look") or loc.get("look") or "interior_day"]
    light = look["prompt"]
    if shot.get("flashback"): light += " " + bible["looks"]["flashback"]["prompt"]
    if shot.get("light"): light += " " + cap(shot["light"].rstrip(".")) + "."
    parts.append(light)
    pl = bible["composition"]["placements"].get(shot.get("placement", ""), shot.get("placement", ""))
    comp = " ".join(x for x in (pl and pl[0].upper() + pl[1:] + ".", shot.get("composition", "") and shot["composition"].rstrip(".") + ".") if x)
    if comp: parts.append(comp)
    if shot.get("props"): parts.append("Props: " + ", ".join(shot["props"]) + ".")
    if shot.get("continuity"): parts.append(shot["continuity"].rstrip(".") + ".")
    refs = [plan["characters"][c]["name"] for c, how in chars.items() if not re.match(r"\s*only\b", how or "")]
    part = [plan["characters"][c]["name"] for c, how in chars.items() if re.match(r"\s*only\b", how or "")]
    if refs:
        parts.append(f"Match the attached reference sheet{'s' if len(refs) > 1 else ''} for {', '.join(refs[:-1]) + ' and ' + refs[-1] if len(refs) > 1 else refs[0]} exactly "
                     f"(face, hair, glasses, clothes); {bible['negative']['people'][0].lower() + bible['negative']['people'][1:]}")
    if part:
        parts.append(f"Use the attached reference sheet only for {' and '.join(part)}'s skin tone and clothing; the face is not in the frame.")
    parts.append(bible["style"]["prompt"])
    avoid = [bible["negative"]["always"]]
    if shot.get("crowd"): avoid.append(bible["negative"]["crowd"])
    avoid += [cap(a.rstrip(".")) + "." for a in shot.get("avoid", [])]
    parts.append(" ".join(avoid))
    return " ".join(cap(p.strip()) for p in parts if p.strip())


def cap(t):
    return t[:1].upper() + t[1:]


def category(shot):
    if shot.get("kind") == "graphic": return "graphics"
    if shot["size"] in ("establishing", "wide") and not shot.get("chars"): return "establishing"
    if shot["size"] in ("insert", "macro", "extreme_close"): return "closeups"
    if shot["size"] in ("close", "reaction") : return "closeups"
    return "characters" if shot.get("chars") else "establishing"


def phash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------- index + prompt files
def build(proj, batch=30, write=True):
    proj = Path(proj); bible = load_bible(proj); plan = load_json(proj / "visual-plan.json")
    if not plan: sys.exit("no visual-plan.json: write it first (python tools/vyapaar_visual.py draft <project> makes a starting point)")
    L = script_lines(proj, plan.get("script"))
    review = load_json(proj / "review.json", {})
    slots = load_json(proj / "visual-slots.json", {})
    have = have_images(proj)
    legacy = load_json(proj / "images-index.json", []) or []
    taken = set(have) | {v["n"] for v in slots.values()} | {e["n"] for e in legacy if isinstance(e.get("n"), int)}
    nxt = [max([x for x in taken if x < CAND_BASE] or [0]) + 1]

    def alloc(key, fixed=None):
        if fixed is not None: return fixed
        if key in slots: return slots[key]["n"]
        n = nxt[0]; nxt[0] += 1; return n

    index, problems = [], []
    # characters first (reference sheets)
    for cid, c in plan["characters"].items():
        p = sheet_prompt(c, bible); n = alloc("char:" + cid, c.get("sheet"))
        e = {"n": n, "type": "character", "name": c["name"], "id": cid, "lines": [], "kind": "ref", "category": "sheets", "prompt": p}
        e["status"] = state(proj, n, p, slots.get("char:" + cid), review, have, reused=c.get("sheet") is not None)
        slots["char:" + cid] = {"n": n, "hash": phash(p) if e["status"] != "reused" else slots.get("char:" + cid, {}).get("hash", "")}
        index.append(e)
    sheet_of = {cid: next(e["n"] for e in index if e.get("id") == cid) for cid in plan["characters"]}
    by_id = {}
    for sh in plan["shots"]:
        kind = sh.get("kind") or L[lines_of(sh)[0] - 1].get("kind", "still")
        if kind in ("card", "graphic"): continue
        if sh.get("same_as"):
            tgt = by_id.get(sh["same_as"])
            if not tgt: problems.append(f"{sh['id']}: same_as {sh['same_as']} is not an earlier picture shot"); continue
            tgt["lines"] += lines_of(sh); tgt.setdefault("also", []).append(sh["id"]); continue
        p = shot_prompt(sh, plan, bible)
        n = alloc(sh["id"], sh.get("reuse"))
        chars = list((sh.get("chars") or {}).keys())
        e = {"n": n, "type": "scene", "shot": sh["id"], "lines": lines_of(sh), "kind": kind if kind in ("still", "hero") else "still",
             "chapter": L[lines_of(sh)[0] - 1].get("chapter"), "category": category(sh), "size": sh["size"], "look": sh.get("look"),
             "characters": chars, "refs": [sheet_of[c] for c in chars], "prompt": p, "words": len(p.split())}
        if sh.get("reuse") is not None and not image_for(proj, n): problems.append(f"{sh['id']}: reuse {n} but images/{n:03d}.* does not exist")
        e["status"] = state(proj, n, p, slots.get(sh["id"]), review, have, reused=sh.get("reuse") is not None)
        slots[sh["id"]] = {"n": n, "hash": phash(p) if e["status"] != "reused" else ""}
        index.append(e); by_id[sh["id"]] = e
        if sh.get("candidates", 1) > 1:
            c = dict(e, n=CAND_BASE + n, type="candidate", candidate_of=n, status="needed" if not image_for(proj, CAND_BASE + n) and e["status"] in ("needed", "rejected", "stale") else ("have" if image_for(proj, CAND_BASE + n) else "skip"))
            index.append(c)
    if write: write_files(proj, index, slots, batch)
    return index, problems


def state(proj, n, prompt, prev, review, have, reused=False):
    r = (review.get(str(n)) or {}).get("status")
    if r == "rejected": return "rejected"
    if reused: return "reused" if n in have else "needed"
    if n not in have: return "needed"
    if prev and prev.get("hash") and prev["hash"] != phash(prompt): return "stale"
    return "have"


def write_files(proj, index, slots, batch):
    pd = proj / "prompts"; pd.mkdir(exist_ok=True)
    old = list(pd.glob("*.txt")) + list(pd.glob("REFS.md")) + list(pd.glob("refs.csv"))
    if old:
        keep = pd / f"_old-{time.strftime('%Y%m%d-%H%M%S')}"; k = 1
        while keep.exists(): keep = pd / f"_old-{time.strftime('%Y%m%d-%H%M%S')}-{k}"; k += 1     # two runs in one second
        keep.mkdir()
        for f in old: shutil.move(str(f), keep / f.name)
    todo_c = [e for e in index if e["type"] == "character" and e["status"] in ("needed", "rejected")]
    todo_s = [e for e in index if e["type"] in ("scene", "candidate") and e["status"] in ("needed", "rejected", "stale")]
    files = []
    if todo_c: files.append(("01-characters.txt", todo_c))
    nb = (len(todo_s) + batch - 1) // batch
    for b in range(nb): files.append((f"{len(files) + 1:02d}-scenes-{b + 1}-of-{nb}.txt", todo_s[b * batch:(b + 1) * batch]))
    for e in index: e.pop("file", None); e.pop("pos", None)
    rows = ["| File | Pos | Picture | Shot | Lines | People | Attach these sheets |", "|---|---|---|---|---|---|---|"]
    csv = ["file,pos,picture,shot,lines,people,attach"]
    for fname, es in files:
        (pd / fname).write_text("\n".join(e["prompt"] for e in es) + "\n", encoding="utf-8")
        for k, e in enumerate(es, 1):
            e["file"], e["pos"] = fname, k
            att = [f"images/{r:03d}.png" for r in e.get("refs", [])]
            rows.append(f"| {fname} | {k} | {e['n']:03d} | {e.get('shot', e.get('name', ''))} | {','.join(map(str, e['lines']))} | {', '.join(e.get('characters', []))} | {' + '.join(att) or '(none)'} |")
            csv.append(f"{fname},{k},{e['n']},{e.get('shot', e.get('name', ''))},{' '.join(map(str, e['lines']))},{' '.join(e.get('characters', []))},{' '.join(att)}")
    (pd / "REFS.md").write_text("# Reference sheets to attach, prompt by prompt\n\nThe ChatGPT extension cannot attach sheets by itself: attach exactly these files "
                                "(the '+ Images' button) for each prompt. tools/chatgpt_runner.py attaches them automatically from images-index.json `refs`.\n"
                                "Make and approve 01-characters.txt first: no scene with a person may run before that person's sheet is approved.\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    (pd / "refs.csv").write_text("\n".join(csv) + "\n", encoding="utf-8")
    (pd / "README.txt").write_text(
        "Made by tools/vyapaar_visual.py from visual-plan.json. Only pictures that are missing, rejected or whose prompt changed are listed.\n"
        "Run the files in order in the ChatGPT extension (Prefix and Suffix empty, wide aspect, delay 5 to 7 s), or with tools/chatgpt_runner.py.\n"
        "  01-characters.txt first (if present). Approve the sheets (python tools/vyapaar_review.py <project> approve 1,2,...) before any scene file.\n"
        "  Then each scene file, attaching the sheets listed in REFS.md for every prompt that shows a person.\n"
        "Press Get my pictures in the studio after each file. Picture numbers follow images-index.json; existing pictures keep their numbers.\n", encoding="utf-8")
    (proj / "images-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    (proj / "visual-slots.json").write_text(json.dumps(slots, ensure_ascii=False, indent=1), encoding="utf-8")
    return files


# ---------------------------------------------------------------- validation
COLOURS = r"white|grey|gray|navy|blue|black|brown|cream|maroon|red|green|yellow|beige|khaki|orange|pink"
GARMENTS = r"shirt|kurta|sweater|jacket|saree|sari|safari suit|vest|lungi|uniform|suit|dhoti|blouse"
PAIR = re.compile(rf"\b({COLOURS})(?: [a-z-]+)? ({GARMENTS})\b", re.I)
HAIR = {"bald": re.compile(r"\bbald(ing)?\b", re.I), "full": re.compile(r"\b(short|thick|curly|wavy) (black|grey|white) hair\b", re.I)}


def attrs(text):
    return {g.lower(): c.lower().replace("gray", "grey") for c, g in PAIR.findall(text or "")}


def conflicts(c, text):
    out = []
    mine = attrs(" ".join(str(c.get(k, "")) for k in ("clothing", "hair", "features", "identity")))
    for g, col in attrs(text).items():
        if g in mine and mine[g] != col: out.append(f"{col} {g} (bible: {mine[g]} {g})")
    bible_hair = " ".join(str(c.get(k, "")) for k in ("hair", "identity"))
    if HAIR["bald"].search(text or "") and not HAIR["bald"].search(bible_hair): out.append("bald/balding (bible has hair)")
    if HAIR["bald"].search(bible_hair) and HAIR["full"].search(text or ""): out.append("full hair (bible: balding)")
    return out


NUM = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(crore|cr|lakh|k|%|x|करोड़|करोड|लाख|हजार)?", re.I)
ORDINAL = re.compile(r"^\s*\d+\.\s")                     # "1. गोयल जी" numbers a row, it is not data


def numbers(text):
    out = set()
    for v, unit in NUM.findall(text or ""):
        try: x = float(v.replace(",", ""))
        except ValueError: continue
        u = (unit or "").lower()
        x = x * 1e7 if u in ("crore", "cr", "करोड़", "करोड") else x * 1e5 if u in ("lakh", "लाख") else x * 1e3 if u in ("k", "हजार") else x
        out.add(round(x, 4))
    return out


def research_rows(proj):
    f = next(Path(proj).glob("*-research.md"), None)
    rows = {}
    if f:
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*([FM]\d+)\s*\|(.*)", line)
            if m: rows[m.group(1)] = m.group(2)
    return rows


def graphic_numbers(g):
    vals = []
    def walk(x, key=""):
        if isinstance(x, dict):
            for k, v in x.items():
                if k not in ("facts", "type", "style", "cue", "at", "highlight", "icon", "id"): walk(v, k)
        elif isinstance(x, list):
            for v in x: walk(v, key)
        elif isinstance(x, (int, float)) and key in ("value", "from", "to", "total", "of", "n", "points", "y", "values", "max") and key != "max":
            vals.append(abs(float(x)))
        elif isinstance(x, str):
            vals.extend(numbers(ORDINAL.sub("", x)))
    walk(g)
    return vals


def validate(proj):
    proj = Path(proj); bible = load_bible(proj); plan = load_json(proj / "visual-plan.json")
    if not plan: sys.exit("no visual-plan.json")
    L = script_lines(proj, plan.get("script")); index, problems = build(proj, write=False)
    have = have_images(proj); rows = research_rows(proj)
    issues = {"critical": list(problems), "warn": [], "info": []}
    covered = {}
    for sh in plan["shots"]:
        for n in lines_of(sh):
            if not 1 <= n <= len(L): issues["critical"].append(f"{sh['id']}: line {n} does not exist"); continue
            covered.setdefault(n, []).append(sh["id"])
        kind = sh.get("kind") or L[lines_of(sh)[0] - 1].get("kind")
        if kind not in ("card", "graphic"):
            for k in ("action", "size"):
                if not sh.get(k) and not sh.get("same_as"): issues["critical"].append(f"{sh['id']}: no {k}")
            if sh.get("size") and sh["size"] not in bible["shots"]: issues["critical"].append(f"{sh['id']}: unknown size {sh['size']}")
            lk = sh.get("look") or plan.get("locations", {}).get(sh.get("location", ""), {}).get("look")
            if lk and lk not in bible["looks"]: issues["critical"].append(f"{sh['id']}: unknown look {lk}")
            if not lk and not sh.get("same_as"): issues["warn"].append(f"{sh['id']}: no look and no location look (falls back to interior_day)")
    for i, l in enumerate(L, 1):
        if i not in covered: issues["critical"].append(f"line {i} ({l.get('kind')}) has no shot in the plan")
        elif len(covered[i]) > 1: issues["warn"].append(f"line {i} is covered by {', '.join(covered[i])}")
    # characters and references
    table = ["| Picture | Shot | Lines | People in the shot | Sheets attached | Missing | Conflicts with the bible |", "|---|---|---|---|---|---|---|"]
    names = {cid: [c["name"]] + c.get("aliases", []) for cid, c in plan["characters"].items()}
    shots = {s["id"]: s for s in plan["shots"]}
    for e in index:
        if e["type"] != "scene": continue
        sh = shots[e["shot"]]; text = " ".join(str(sh.get(k, "")) for k in ("action", "fg", "mg", "bg"))
        missing = [f"{c} (sheet {r:03d} not made yet)" for c, r in zip(e["characters"], e["refs"]) if r not in have]
        for cid, ns in names.items():
            if cid in e["characters"]: continue
            for nm in ns:
                if re.search(rf"\b{re.escape(nm)}\b(?!'s)", text):
                    issues["warn"].append(f"{e['shot']}: '{nm}' is named in the shot text but not listed in chars (no sheet will be attached)")
        conf = []
        for cid in e["characters"]:
            c = plan["characters"][cid]
            if (sh.get("costume") or {}).get(cid): continue                 # a planned costume change is not a conflict
            seg = " ".join(L[n - 1].get("visual", "") for n in e["lines"])
            m = re.search(rf"{re.escape(c['name'].split()[0])}[^()]*?\(([^()]+)\)", seg)
            for x in conflicts(c, (m.group(1) if m else "") + " " + text): conf.append(f"{c['name']}: {x}")
            if m and c.get("sheet") is not None:                     # an approved sheet, and the script's note describes the person differently
                extra = [f"{col} {g}" for g, col in attrs(m.group(1).split(",")[0]).items() if g not in attrs(c.get("clothing", "")) and g in ("sweater", "shirt", "kurta", "jacket", "suit", "uniform")]
                if extra: issues["info"].append(f"{e['shot']} (lines {','.join(map(str, e['lines']))}): the script note says '{m.group(1)[:70]}', the bible says '{c.get('clothing')}'; the prompt follows the bible")
        for x in conf: issues["warn"].append(f"{e['shot']}: {x}")
        table.append(f"| {e['n']:03d} | {e['shot']} | {','.join(map(str, e['lines']))} | {', '.join(e['characters']) or '-'} | "
                     f"{' '.join(f'{r:03d}' for r in e['refs']) or '-'} | {'; '.join(missing) or '-'} | {'; '.join(conf) or '-'} |")
    # the old character sheets against the bible (a sheet made from an older description)
    for cid, c in plan["characters"].items():
        if c.get("sheet") is not None:
            if c["sheet"] not in have: issues["critical"].append(f"{c['name']}: sheet {c['sheet']:03d} is named but the picture does not exist")
            old = c.get("sheet_prompt_was", "")
            for x in conflicts(c, old): issues["critical"].append(f"{c['name']}: the approved sheet shows {x}")
    # graphics: every number must trace to the line's screen text or the research rows it cites
    gtable = ["| Shot | Lines | Type | Numbers shown | Traced to | Unverified |", "|---|---|---|---|---|---|"]
    for sh in plan["shots"]:
        g = sh.get("graphic")
        if not g: continue
        shown = graphic_numbers(g)
        pool = set()
        for fid in g.get("facts", []):
            if fid not in rows: issues["critical"].append(f"{sh['id']}: fact {fid} is not in the research file")
            pool |= numbers(rows.get(fid, ""))
        for n in lines_of(sh): pool |= numbers(L[n - 1].get("screen", ""))
        pool |= set(float(x) for x in g.get("allow", []))
        base = [p for p in pool if p > 0]
        pool |= {a + b for a in base for b in base} | {abs(a - b) for a in base for b in base}      # a shown sum or difference of two cited numbers
        bad = [x for x in shown if not any(abs(x - p) <= max(0.03 * abs(p), 0.051) for p in pool)]
        if bad: issues["critical"].append(f"{sh['id']}: numbers {bad} trace to no cited fact or screen text")
        gtable.append(f"| {sh['id']} | {','.join(map(str, lines_of(sh)))} | {g.get('type')} | {', '.join(f'{x:g}' for x in shown) or '-'} | {', '.join(g.get('facts', [])) or 'screen'} | {', '.join(f'{x:g}' for x in bad) or '-'} |")
    # variety: sizes and long runs of one size
    sizes = [s.get("size") for s in plan["shots"] if s.get("size")]
    run, prev = 1, None
    for s in sizes:
        run = run + 1 if s == prev else 1; prev = s
        if run == 4: issues["warn"].append(f"four {s} shots in a row (vary the framing)")
    words = [e["words"] for e in index if e["type"] == "scene"]
    long = [e["shot"] for e in index if e["type"] == "scene" and e["words"] > 250]
    if long: issues["warn"].append(f"prompts over 250 words (trim the action or layers): {', '.join(long)}")
    dist = {k: sizes.count(k) for k in bible["shots"] if sizes.count(k)}
    st = {k: sum(1 for e in index if e.get("status") == k and e["type"] != "candidate") for k in ("needed", "have", "reused", "stale", "rejected")}
    md = [f"# Continuity and plan report: {proj.name}", "", f"{len(plan['shots'])} shots for {len(L)} lines; {len([e for e in index if e['type'] == 'scene'])} pictures, "
          f"{len(plan['characters'])} character sheets. Picture status: " + ", ".join(f"{v} {k}" for k, v in st.items() if v) + ".",
          f"Shot sizes: " + ", ".join(f"{k} {v}" for k, v in dist.items()) + f". Prompt length: {min(words, default=0)} to {max(words, default=0)} words.", ""]
    for lvl in ("critical", "warn", "info"):
        md.append(f"## {lvl.upper()} ({len(issues[lvl])})"); md += [f"- {x}" for x in issues[lvl]] or ["- none"]; md.append("")
    md += ["## Characters in each picture", "", *table, "", "## Graphics: where every number comes from", "", *gtable, ""]
    (proj / "continuity-report.md").write_text("\n".join(md), encoding="utf-8")
    (proj / "validate.json").write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
    return issues


# ---------------------------------------------------------------- draft (a starting point for a new project)
LOOK_HINTS = [(r"flashback", None), (r"midnight|at night|night\b", "street_night"), (r"dinner|dining", "home_evening"), (r"showroom", "retail_modern"),
              (r"rooftop|roof", "rooftop_workshop"), (r"bank|office", "office_day"), (r"dusk|evening", "aerial_dusk"), (r"bazaar|street|lane|road", "street_day")]
SIZE_HINTS = [(r"^extreme close-up", "extreme_close"), (r"^close-up", "close"), (r"^inside|^through", "wide"), (r"^\w+ (?:and|with) ", "two_shot")]


def draft(proj):
    proj = Path(proj); L = script_lines(proj); bible = load_bible(proj)
    person = re.compile(r"([A-Z][A-Za-z]+(?: (?:ji|dada))?) \(([^()]{20,240})\)")
    chars = {}
    for l in L:
        for name, desc in person.findall(l.get("visual", "")):
            cid = re.sub(r"\W+", "_", name.lower()).strip("_")
            chars.setdefault(cid, {"name": name, "identity": desc, "clothing": desc, "draft": True})
    shots = []
    for i, l in enumerate(L, 1):
        v = l.get("visual", ""); sid = f"S{i:03d}"
        if l.get("kind") == "card":
            shots.append({"id": sid, "lines": [i], "kind": "graphic", "graphic": {"type": "number", "label": l.get("screen", ""), "facts": l.get("facts", [])}, "draft": True}); continue
        clean = person.sub(lambda m: m.group(1), v)
        look = next((lk for pat, lk in LOOK_HINTS if re.search(pat, v, re.I) and lk), "interior_day")
        size = next((s for pat, s in SIZE_HINTS if re.search(pat, clean, re.I)), "medium")
        who = {cid: "" for cid, c in chars.items() if re.search(rf"\b{re.escape(c['name'])}\b(?!'s)", clean)}
        shots.append({"id": sid, "lines": [i], "size": size, "look": look, "flashback": bool(re.search("flashback", v, re.I)), "chars": who,
                      "action": re.sub(r"^(Close-up|Extreme close-up|Flashback)[^:]*:\s*", "", clean), "draft": True})
    out = proj / ("visual-plan.draft.json" if (proj / "visual-plan.json").exists() else "visual-plan.json")
    out.write_text(json.dumps({"version": 1, "draft": True, "characters": chars, "locations": {}, "shots": shots}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}: {len(chars)} characters, {len(shots)} shots. It is a draft: art-direct every shot (size, look, expression, layers) before making prompts.")


# ---------------------------------------------------------------- the readable bible
def bible_md():
    b = load_bible()
    md = [f"# {b['name']}", "", "_Generated from `visual-bible.json` by `python tools/vyapaar_visual.py bible`. Edit the JSON, not this file._", "",
          "## 1. Rendering style", "", b["style"]["summary"], "", f"Prompt words: {b['style']['prompt']}", "", "Never: " + "; ".join(b["style"]["never"]) + ".", "",
          "## 2. Colour palette", "", b["palette"]["summary"], "", "- Base: " + ", ".join(b["palette"]["base"]), "- Accents: " + ", ".join(b["palette"]["accents"]),
          "- Cool: " + ", ".join(b["palette"]["cool"]), *[f"- {r}" for r in b["palette"]["rules"]], "",
          "## 3. Lighting philosophy", "", b["lighting"]["philosophy"], "", "| Look | Light | Target brightness (0 to 1) |", "|---|---|---|",
          *[f"| `{k}` {v['label']} | {v['prompt']} | {v['luma'][0]:.2f} to {v['luma'][1]:.2f} |" for k, v in b["looks"].items()], "",
          "## 4. Characters", "", *[f"- {r}" for r in b["characters"]["rules"]], "", f"Sheet prompt: {b['characters']['sheet_prompt']}", "",
          "## 5. Environments and materials", "", "Every location is described once in the project's `visual-plan.json` (`locations`), with its default look, and repeated word for word. "
          "Materials are named so they render as materials: worn walnut, scratched glass, brushed steel, brass, polished marble, cotton, silk, plaster, corrugated sheet.", "",
          "## 6. Camera and composition", "", "| Shot | Prompt words | Use it for |", "|---|---|---|",
          *[f"| `{k}` | {v['prompt']} | {v['use']} |" for k, v in b["shots"].items()], "", *[f"- {r}" for r in b["composition"]["rules"]], "",
          "## 7. Colour grading", "", b["render"]["grade_notes"], "", f"`{b['render']['grade']}`", "", "Flashbacks add a modifier on top: " + json.dumps(b["render"]["flashback"]) + ".", "",
          "## 8. Aspect ratio and safe composition", "", f"{b['aspect']['ratio']}. {b['aspect']['safe']}", "",
          "## 9. Recurring characters and locations", "", "Stable ids in `visual-plan.json`; `visual-slots.json` keeps each shot's picture number; the reference manifest `prompts/REFS.md` "
          "says which sheets to attach to each prompt; `continuity-report.md` checks every shot against the bible.", "",
          "## Negative instructions (in every prompt)", "", b["negative"]["always"], "",
          "## Graphics system", "", b["graphics"]["summary"], "", *[f"- {r}" for r in b["graphics"]["rules"]], "",
          "## Render settings", "", f"{b['render']['width']}x{b['render']['height']} at {b['render']['fps']} fps. {b['render']['fps_reason']}", ""]
    out = BIBLE.with_suffix(".md"); out.write_text("\n".join(md), encoding="utf-8"); print("wrote", out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["bible", "draft", "prompts", "validate", "show"]); ap.add_argument("project", nargs="?")
    ap.add_argument("shot", nargs="?"); ap.add_argument("--batch", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "bible": return bible_md()
    if not a.project: sys.exit("give the project folder")
    if a.cmd == "draft": return draft(a.project)
    if a.cmd == "prompts":
        index, problems = build(a.project, a.batch)
        for p in problems: print("PROBLEM", p)
        st = {}
        for e in index: st[e.get("status")] = st.get(e.get("status"), 0) + 1
        files = sorted(f.name for f in (Path(a.project) / "prompts").glob("*.txt"))
        print(f"{sum(1 for e in index if e['type'] == 'character')} sheets, {sum(1 for e in index if e['type'] == 'scene')} pictures, "
              f"{sum(1 for e in index if e['type'] == 'candidate')} second candidates; status " + ", ".join(f"{v} {k}" for k, v in st.items()))
        print("prompt files:", ", ".join(files) or "none (every picture exists)"); return
    if a.cmd == "validate":
        iss = validate(a.project)
        print(f"{len(iss['critical'])} critical, {len(iss['warn'])} warnings -> {Path(a.project) / 'continuity-report.md'}")
        for x in iss["critical"][:20]: print("  CRITICAL", x)
        sys.exit(1 if iss["critical"] else 0)
    if a.cmd == "show":
        plan = load_json(Path(a.project) / "visual-plan.json"); bible = load_bible(a.project)
        sh = next(s for s in plan["shots"] if s["id"] == a.shot)
        print(shot_prompt(sh, plan, bible)); print(f"\n({len(shot_prompt(sh, plan, bible).split())} words)")


if __name__ == "__main__":
    main()
