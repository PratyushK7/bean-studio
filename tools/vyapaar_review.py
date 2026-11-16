"""Decoding Vyapaar Gate 1: review the pictures before anything is rendered or upscaled.

    python tools/vyapaar_review.py <project> analyze [--index images-index.json]   # measure every picture (cached in analysis/)
    python tools/vyapaar_review.py <project> sheets  [--index ...]                 # contact sheets by group in review/: sheets, establishing,
                                                                                   #   characters, closeups, graphics (candidates side by side)
    python tools/vyapaar_review.py <project> report  [--index ...]                 # review-report.md: automatic flags + the human checklist
    python tools/vyapaar_review.py <project> approve 1,2,5-9 [--note "..."]        # approve pictures (by picture number)
    python tools/vyapaar_review.py <project> reject 14 --note "two Ankits"         # moves images/014.* to images/_rejected/, so only it is remade
    python tools/vyapaar_review.py <project> pick 137 b                            # the second candidate wins (5137 -> 137; the old one -> images/_alt/)
    python tools/vyapaar_review.py <project> gate    [--index ...]                 # exit 0 only if every picture the script uses is approved
                                                                                   #   and no critical flag is open
    python tools/vyapaar_review.py <project> upscale                               # ESRGAN 2x (tools/video/ws_upscale.js) for APPROVED pictures only

What a machine can check is checked here (size, light against the planned look, saturation, blur, near-duplicates, face counts, prompts that
changed after the picture was made). What it cannot (the right person, hands, the picture matching the line) is a checklist a person answers
from the contact sheets. Nothing is approved automatically. Decisions live in review.json; originals are never deleted.
"""
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vyapaar_visual as vv

FONT = "C:/Windows/Fonts/segoeui.ttf"
GROUPS = ["sheets", "establishing", "characters", "closeups", "graphics"]
LOOK_HINTS = [(r"flashback", "flashback"), (r"midnight|at night\b|night,|dark lane|dark road", "street_night"), (r"dinner|dining", "home_evening"),
              (r"showroom", "retail_modern"), (r"rooftop", "rooftop_workshop"), (r"bank|office", "office_day"), (r"dusk|evening", "aerial_dusk")]


def parse_slots(s):
    out = []
    for part in str(s).split(","):
        if "-" in part: a, b = part.split("-"); out += range(int(a), int(b) + 1)
        elif part.strip(): out.append(int(part))
    return out


def load_index(proj, name):
    idx = vv.load_json(proj / name, [])
    for e in idx:                                       # an older index has no category or look: infer them so the checks still run
        if "category" not in e:
            p = e.get("prompt", "")
            e["category"] = "sheets" if e["type"] == "character" else "closeups" if re.match(r"(close-up|extreme close-up|insert)", p, re.I) else "characters" if re.search(r"\b(Ramesh|Ankit|Goyal|Nandu|Sharma)\b", p) else "establishing"
            e["look_inferred"] = True
        if not e.get("look") and e["type"] != "character":
            e["look"] = next((lk for pat, lk in LOOK_HINTS if re.search(pat, e.get("prompt", ""), re.I)), None)
    names = [x["name"].split()[0] for x in idx if x["type"] == "character"]
    for e in idx:                                       # an older index does not list who is in the picture: the named people in the prompt
        if e["type"] == "scene" and "characters" not in e:
            e["characters"] = [nm for nm in names if re.search(rf"{re.escape(nm)}(?!'s)", e.get("prompt", ""))]
    return idx


# ---------------------------------------------------------------- measuring
def dhash(im):
    g = np.asarray(im.convert("L").resize((9, 8), Image.LANCZOS), dtype=np.int16)
    return int("".join("1" if x else "0" for x in (g[:, 1:] > g[:, :-1]).flatten()), 2)


YUNET = Path(__file__).resolve().parent / "video" / "models" / "face_detection_yunet_2023mar.onnx"   # OpenCV's own models (opencv_zoo, MIT)
SFACE = Path(__file__).resolve().parent / "video" / "models" / "face_recognition_sface_2021dec.onnx"
TWIN_COS = 0.58        # calibrated on this channel's pictures: two Ankits in one frame 0.59, look-alike extras 0.66, different people 0.25 to 0.55
LIKENESS_COS = 0.55    # a planned person whose best face is below this against their sheet gets a note (own sheet: 0.67 to 0.81)
_m = {}


MODEL_URLS = {YUNET: "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
              SFACE: "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"}


def fetch_models():
    """OpenCV's own face models (free, MIT), downloaded once on first use; they are not kept in git"""
    import urllib.request
    for path, url in MODEL_URLS.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True); print(f"downloading {path.name} from opencv_zoo (once)...", flush=True)
            try: urllib.request.urlretrieve(url, path)
            except Exception as e: print(f"  could not download {path.name}: {e}; face checks will be skipped"); path.unlink(missing_ok=True)


def face_models(w, h):
    import cv2
    if not YUNET.exists() or not SFACE.exists(): fetch_models()
    if not YUNET.exists() or not hasattr(cv2, "FaceDetectorYN"): return None, None
    if (w, h) not in _m: _m[(w, h)] = cv2.FaceDetectorYN.create(str(YUNET), "", (w, h), 0.75, 0.3, 50)
    if "rec" not in _m and SFACE.exists(): _m["rec"] = cv2.FaceRecognizerSF.create(str(SFACE), "")
    return _m[(w, h)], _m.get("rec")


def faces_and_ids(im):
    """face boxes as fractions of the picture [x, y, w, h, score] and one identity vector per face (SFace), found at 1280 px wide"""
    import cv2
    big = im.resize((1280, int(1280 * im.height / im.width)), Image.LANCZOS); a = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2BGR)
    det, rec = face_models(*big.size)
    if det is None: return [], np.zeros((0, 128), np.float32)
    _, found = det.detect(a); boxes, vecs = [], []
    for f in (found if found is not None else []):
        boxes.append([round(float(f[0]) / big.width, 4), round(float(f[1]) / big.height, 4), round(float(f[2]) / big.width, 4), round(float(f[3]) / big.height, 4), round(float(f[14]), 2)])
        vecs.append(rec.feature(rec.alignCrop(a, f)).flatten() if rec is not None else np.zeros(128, np.float32))
    return boxes, np.array(vecs, np.float32).reshape(-1, 128)


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def twins(boxes, vecs):
    """pairs of faces that look like the same person (a duplicated person, or a picture split into two panels); small background faces are skipped"""
    out = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if min(boxes[i][2], boxes[j][2]) < 0.04: continue
            c = cosine(vecs[i], vecs[j])
            if c >= TWIN_COS: out.append([i, j, round(c, 2)])
    return out


def measure(path, mask_dir, session=None):
    im = Image.open(path).convert("RGB"); w, h = im.size
    small = im.resize((640, int(640 * h / w)), Image.LANCZOS); a = np.asarray(small).astype(np.float32) / 255
    luma = float((0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean())
    mx, mn = a.max(axis=2), a.min(axis=2); sat = float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
    import cv2
    g = cv2.cvtColor((a * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
    clip_hi = float((g > 250).mean()); clip_lo = float((g < 5).mean())
    out = {"w": w, "h": h, "luma": round(luma, 3), "sat": round(sat, 3), "sharp": round(sharp, 1), "clip_hi": round(clip_hi, 4), "clip_lo": round(clip_lo, 4),
           "hash": dhash(im), "mtime": path.stat().st_mtime}
    out["faces"], vecs = faces_and_ids(im); np.save(mask_dir / f"{path.stem}-faces.npy", vecs)
    out["twins"] = twins(out["faces"], vecs); out["fv"] = 2
    if session is not None:                             # the subject: rembg's mask, used by the renderer to aim camera moves
        from rembg import remove
        m = remove(small, session=session, only_mask=True).point(lambda v: 255 if v > 128 else 0)
        m.save(mask_dir / f"{path.stem}-mask.png")
        box = m.getbbox()
        out["subject"] = [round(box[0] / small.width, 3), round(box[1] / small.height, 3), round(box[2] / small.width, 3), round(box[3] / small.height, 3)] if box else None
        out["subject_area"] = round(float(np.asarray(m).mean() / 255), 3)
    return out


def analyze(proj, index_name, masks=True):
    ad = proj / "analysis"; ad.mkdir(exist_ok=True)
    idx = load_index(proj, index_name); session = None; done = 0
    for e in idx:
        p = vv.image_for(proj, e["n"])
        if not p: continue
        f = ad / f"{e['n']:03d}.json"
        old = vv.load_json(f)
        if old and old.get("mtime") == p.stat().st_mtime and (old.get("subject") is not None or not masks or "subject" in old):
            if old.get("fv") != 2:                       # faces were added later: redo them without redoing the masks
                old["faces"], vecs = faces_and_ids(Image.open(p).convert("RGB")); np.save(ad / f"{p.stem}-faces.npy", vecs)
                old["twins"] = twins(old["faces"], vecs); old["fv"] = 2; f.write_text(json.dumps(old), encoding="utf-8"); done += 1
            continue
        if masks and session is None:
            from rembg import new_session
            session = new_session("u2net")
        f.write_text(json.dumps(measure(p, ad, session if masks else None)), encoding="utf-8"); done += 1
    print(f"analysed {done} picture(s) (the rest were cached) -> {ad}")


# ---------------------------------------------------------------- flags
def flags(proj, index_name):
    bible = vv.load_bible(proj); idx = load_index(proj, index_name); ad = proj / "analysis"
    m = {e["n"]: vv.load_json(ad / f"{e['n']:03d}.json") for e in idx}
    sharp = sorted(x["sharp"] for x in m.values() if x)
    sheet_vecs = {}                                    # identity vectors of every character sheet, keyed by character id (or first name for an older index)
    for e in idx:
        if e["type"] == "character" and (ad / f"{e['n']:03d}-faces.npy").exists():
            v = np.load(ad / f"{e['n']:03d}-faces.npy")
            if len(v): sheet_vecs[e.get("id") or e["name"].split()[0]] = v
    med = sharp[len(sharp) // 2] if sharp else 0
    out = {}
    for e in idx:
        n, a, fl = e["n"], m.get(e["n"]), []
        if e.get("status") == "stale": fl.append(("warn", "the prompt changed after this picture was made"))
        if not a:
            out[n] = [("pending", "no picture yet")] if e.get("status") not in ("skip",) else []; continue
        if a["w"] < 1200: fl.append(("critical", f"too small to use: {a['w']}x{a['h']}"))
        elif a["w"] < bible["review"]["min_width"] and e["type"] != "character": fl.append(("info", f"{a['w']}x{a['h']}: fine after the 2x upscale"))
        if abs(a["w"] / a["h"] - 16 / 9) > 0.03 and e["type"] != "character":
            fl.append(("warn", f"not 16:9 ({a['w']}x{a['h']}): the renderer crops {100 - round(100 * (a['w'] * 9 / 16) / a['h'])}% of the height; check heads and key objects survive"))
        look = bible["looks"].get(e.get("look") or "")
        if look and e["type"] == "scene":
            lo, hi = look["luma"]
            if a["luma"] > hi + 0.05: fl.append(("warn", f"lighting: too bright for '{e['look']}' (brightness {a['luma']:.2f}, the look wants {lo:.2f} to {hi:.2f})"))
            if a["luma"] < lo - 0.05: fl.append(("warn", f"lighting: too dark for '{e['look']}' (brightness {a['luma']:.2f}, the look wants {lo:.2f} to {hi:.2f})"))
            if a["sat"] > look["sat"][1] + 0.06: fl.append(("warn", f"colour: oversaturated for '{e['look']}' (saturation {a['sat']:.2f}, max {look['sat'][1]:.2f})"))
        if a["clip_hi"] > 0.06: fl.append(("warn", f"blown highlights on {a['clip_hi'] * 100:.0f}% of the frame"))
        if med and a["sharp"] < 0.25 * med and e.get("category") not in ("sheets",): fl.append(("warn", f"soft or blurred (sharpness {a['sharp']:.0f}, the set's median {med:.0f})"))
        want = len(e.get("characters", [])) if "characters" in e else None
        nf = len(a.get("faces", []))
        if want is not None and e["type"] == "scene":
            if want and nf == 0 and e.get("category") == "characters": fl.append(("info", f"no face detected though {want} person(s) are planned: check they are there"))
            if want and nf > want + 1 and not re.search(r"crowd|families|jewellers|customers|salesm[ae]n|staff|helpers|guard|couple|family", e.get("prompt", ""), re.I) and e.get("category") != "establishing":
                fl.append(("warn", f"{nf} faces detected for {want} planned: check for duplicate or extra people"))
        tw = a.get("twins", []) if e["type"] == "scene" else []            # a character sheet shows one person many times on purpose
        if tw and sheet_vecs and (ad / f"{n:03d}-faces.npy").exists():      # two different named people who simply look alike in this style
            fv = np.load(ad / f"{n:03d}-faces.npy")
            def who(k):
                sc = sorted(((max(cosine(fv[k], v) for v in vs), nm) for nm, vs in sheet_vecs.items()), reverse=True)
                return sc[0][1] if sc and sc[0][0] >= 0.6 and sc[0][0] - (sc[1][0] if len(sc) > 1 else 0) >= 0.04 else None
            tw = [t for t in tw if not (who(t[0]) and who(t[1]) and who(t[0]) != who(t[1]))]
        if tw:
            top = max(x[2] for x in tw)
            fl.append(("warn", f"{len(tw)} pair(s) of faces look like the same person (identity similarity up to {top:.2f}): a duplicated person, a look-alike extra or a split frame"))
        if e["type"] == "scene" and e.get("category") in ("characters", "closeups") and sheet_vecs:
            here = np.load(ad / f"{n:03d}-faces.npy") if (ad / f"{n:03d}-faces.npy").exists() else np.zeros((0, 128))
            for who in e.get("characters", []):
                sv = sheet_vecs.get(who)
                if sv is None or not len(here): continue
                best = max(cosine(f, s2) for f in here for s2 in sv)
                if best < LIKENESS_COS: fl.append(("info", f"weak likeness to {who}'s sheet (best {best:.2f}): check it is the same person"))
        out[n] = fl
    # near-duplicates across different shots: visual repetition
    hs = [(e["n"], m[e["n"]]["hash"]) for e in idx if m.get(e["n"]) and e["type"] in ("scene",)]
    lim = bible["review"]["duplicate_hash_distance"]
    for i, (n1, h1) in enumerate(hs):
        for n2, h2 in hs[i + 1:]:
            d = bin(h1 ^ h2).count("1")
            if d <= lim:
                out[n1].append(("warn", f"looks almost the same as picture {n2:03d} (distance {d}): visual repetition"))
                out[n2].append(("warn", f"looks almost the same as picture {n1:03d} (distance {d})"))
    return idx, out, m


# ---------------------------------------------------------------- contact sheets
def sheets(proj, index_name):
    idx, fl, m = flags(proj, index_name); rd = proj / "review"; rd.mkdir(exist_ok=True)
    review = vv.load_json(proj / "review.json", {})
    font = ImageFont.truetype(FONT, 17); small = ImageFont.truetype(FONT, 14)
    made = []
    gfx = sorted((proj / "graphics").glob("G*.png")) if (proj / "graphics").is_dir() else []
    for g in GROUPS:
        items = [e for e in idx if e.get("category") == g and e["type"] in ("scene", "character")]
        if g == "graphics": items = [{"n": None, "png": p, "label": p.stem} for p in gfx]
        if not items: continue
        cols, tw = 4, 460; th = int(tw * 9 / 16); cap = 64
        cands = {e["candidate_of"]: e for e in idx if e["type"] == "candidate"}
        cells = []
        for e in items:
            if e.get("png"): cells.append((e["png"], e["label"], [])); continue
            p = vv.image_for(proj, e["n"]); st = (review.get(str(e["n"])) or {}).get("status", "pending")
            label = f"{e['n']:03d} {e.get('shot', e.get('name', ''))} L{','.join(map(str, e.get('lines', [])))[:14]} {e.get('size', '')} · {st}"
            cells.append((p, label, fl.get(e["n"], [])))
            c = cands.get(e["n"])
            if c and vv.image_for(proj, c["n"]): cells.append((vv.image_for(proj, c["n"]), f"{c['n']} candidate b of {e['n']:03d}", fl.get(c["n"], [])))
        for page in range(0, len(cells), 24):
            chunk = cells[page:page + 24]; rows = -(-len(chunk) // cols)
            sheet = Image.new("RGB", (cols * tw, rows * (th + cap)), (18, 16, 14)); d = ImageDraw.Draw(sheet)
            for k, (p, label, f) in enumerate(chunk):
                x, y = (k % cols) * tw, (k // cols) * (th + cap)
                if p and Path(p).exists():
                    im = Image.open(p).convert("RGB"); im.thumbnail((tw - 8, th - 6)); sheet.paste(im, (x + 4, y + 3))
                else:
                    d.rectangle([x + 4, y + 3, x + tw - 4, y + th - 3], outline=(90, 80, 70)); d.text((x + 20, y + th // 2), "not made yet", font=font, fill=(160, 150, 140))
                d.text((x + 6, y + th + 2), label, font=font, fill=(240, 220, 170))
                worst = next((t for lvl in ("critical", "warn", "info") for l2, t in f if l2 == lvl), "")
                lvl = next((l2 for l2, _ in f if l2 in ("critical", "warn")), "info")
                if worst: d.text((x + 6, y + th + 24), worst[:62], font=small, fill=(235, 95, 80) if lvl in ("critical", "warn") else (150, 190, 160))
            out = rd / f"{g}-{page // 24 + 1}.jpg"; sheet.save(out, quality=88); made.append(out)
    print("contact sheets:", ", ".join(p.name for p in made), "in", rd)
    return made


# ---------------------------------------------------------------- decisions
def save_review(proj, r): (proj / "review.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")


def decide(proj, slots, status, note=""):
    r = vv.load_json(proj / "review.json", {})
    for n in slots:
        p = vv.image_for(proj, n)
        if status == "approved" and not p: print(f"  {n:03d}: no picture to approve"); continue
        if status == "rejected" and p:
            keep = proj / "images" / "_rejected"; keep.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), keep / f"{p.stem}-{time.strftime('%Y%m%d-%H%M%S')}{p.suffix}")
            hd = proj / "images-hd" / f"{n:03d}.png"
            if hd.exists(): shutil.move(str(hd), keep / f"{n:03d}-hd-{time.strftime('%Y%m%d-%H%M%S')}.png")
        r[str(n)] = {"status": status, "note": note, "at": time.strftime("%Y-%m-%d %H:%M")}
        print(f"  {n:03d}: {status}{' (' + note + ')' if note else ''}")
    save_review(proj, r)
    if status == "rejected": print("Remake only these: python tools/vyapaar_prompts.py <project> (rejected slots go into the new prompt files), then run that file.")


def pick(proj, n, which):
    if which != "b": sys.exit("only 'b' (the second candidate) can be picked; 'a' is already the main picture")
    c = vv.image_for(proj, vv.CAND_BASE + n); a = vv.image_for(proj, n)
    if not c: sys.exit(f"no candidate b for {n:03d} (images/{vv.CAND_BASE + n}.*)")
    alt = proj / "images" / "_alt"; alt.mkdir(parents=True, exist_ok=True)
    if a: shutil.move(str(a), alt / f"{a.stem}-a-{time.strftime('%Y%m%d-%H%M%S')}{a.suffix}")
    shutil.move(str(c), proj / "images" / f"{n:03d}{c.suffix}")
    r = vv.load_json(proj / "review.json", {}); r[str(n)] = {"status": "pending", "note": "candidate b picked; approve it after a look", "at": time.strftime("%Y-%m-%d %H:%M")}
    save_review(proj, r); print(f"{n:03d}: candidate b is now the picture (the old one is in images/_alt/)")


# ---------------------------------------------------------------- report and gate
def report(proj, index_name):
    idx, fl, m = flags(proj, index_name); review = vv.load_json(proj / "review.json", {})
    used = [e for e in idx if e["type"] in ("scene", "character")]
    st = {k: 0 for k in ("approved", "rejected", "pending")}
    def status_of(n):
        s0 = (review.get(str(n)) or {}).get("status", "pending")
        return "pending" if s0 == "rejected" and vv.image_for(proj, n) else s0     # a remade picture waits for a fresh look
    for e in used: st[status_of(e["n"])] += 1
    crit = [(e["n"], t) for e in used for l, t in fl.get(e["n"], []) if l == "critical"]
    warn = [(e["n"], t) for e in used for l, t in fl.get(e["n"], []) if l == "warn"]
    info = [(e["n"], t) for e in used for l, t in fl.get(e["n"], []) if l == "info"]
    pend = [e["n"] for e in used if fl.get(e["n"]) and fl[e["n"]][0][0] == "pending"]
    bible = vv.load_bible(proj)
    md = [f"# Gate 1, picture review: {proj.name}", "", f"Index: `{index_name}`. {len(used)} pictures: {st['approved']} approved, {st['rejected']} rejected, {st['pending']} pending "
          f"({len(pend)} not made yet). Automatic flags: {len(crit)} critical, {len(warn)} warnings, {len(info)} notes.", "",
          "The render refuses to start until every picture the script uses is approved and no critical flag is open "
          "(`python tools/vyapaar_review.py <project> gate`).", "", "## What a person must check on the contact sheets (review/*.jpg)", "",
          *[f"{i}. {c}" for i, c in enumerate(bible["review"]["checks"], 1)], "", f"## Critical ({len(crit)})", ""] + ([f"- {n:03d}: {t}" for n, t in crit] or ["- none"]) + \
         ["", f"## Warnings ({len(warn)})", ""] + ([f"- {n:03d}: {t}" for n, t in warn] or ["- none"]) + ["", f"## Notes ({len(info)})", ""] + ([f"- {n:03d}: {t}" for n, t in info] or ["- none"])
    md += ["", "## Every picture", "", "| Picture | Shot | Lines | Group | Look | Brightness | Saturation | Faces | Status | Flags |", "|---|---|---|---|---|---|---|---|---|---|"]
    for e in used:
        a = m.get(e["n"]) or {}
        md.append(f"| {e['n']:03d} | {e.get('shot', e.get('name', ''))} | {','.join(map(str, e.get('lines', [])))[:20]} | {e.get('category')} | {e.get('look') or '-'}"
                  f"{' (inferred)' if e.get('look_inferred') and e.get('look') else ''} | {a.get('luma', '-')} | {a.get('sat', '-')} | {len(a.get('faces', [])) if a else '-'} | "
                  f"{status_of(e['n'])} | {'; '.join(t for _, t in fl.get(e['n'], []))[:160] or '-'} |")
    out = proj / ("review-report.md" if index_name == "images-index.json" else f"review-report-{Path(index_name).stem}.md")
    out.write_text("\n".join(md), encoding="utf-8"); print(f"{out}: {st}, {len(crit)} critical, {len(warn)} warnings")
    return st, crit


def gate(proj, index_name):
    idx, fl, m = flags(proj, index_name); review = vv.load_json(proj / "review.json", {})
    used = [e for e in idx if e["type"] in ("scene", "character")]
    bad = [e["n"] for e in used if (review.get(str(e["n"])) or {}).get("status") != "approved"]
    crit = [(e["n"], t) for e in used for l, t in fl.get(e["n"], []) if l == "critical"]
    if bad or crit:
        print(f"GATE 1 CLOSED: {len(bad)} picture(s) not approved{(' (' + ', '.join(f'{x:03d}' for x in bad[:15]) + ('...' if len(bad) > 15 else '') + ')') if bad else ''}; "
              f"{len(crit)} critical flag(s)"); return False
    print("GATE 1 OPEN: every picture is approved and no critical flag is open"); return True


def upscale(proj):
    review = vv.load_json(proj / "review.json", {})
    ok = sorted(int(k) for k, v in review.items() if v.get("status") == "approved" and not (proj / "images-hd" / f"{int(k):03d}.png").exists() and vv.image_for(proj, int(k)))
    if not ok: print("nothing to upscale: every approved picture already has its HD copy (or nothing is approved yet)"); return
    js = Path(__file__).resolve().parent / "video" / "ws_upscale.js"
    print(f"upscaling {len(ok)} approved picture(s), about 90 s each on this PC's GPU")
    subprocess.run(["node", str(js), str(proj / "images"), str(proj / "images-hd"), "--only", ",".join(map(str, ok))], check=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("cmd", choices=["analyze", "sheets", "report", "approve", "reject", "pick", "gate", "upscale"])
    ap.add_argument("arg", nargs="?"); ap.add_argument("arg2", nargs="?"); ap.add_argument("--note", default=""); ap.add_argument("--index", default="images-index.json")
    ap.add_argument("--no-masks", action="store_true")
    a = ap.parse_args(); proj = Path(a.project)
    if a.cmd == "analyze": analyze(proj, a.index, not a.no_masks)
    elif a.cmd == "sheets": sheets(proj, a.index)
    elif a.cmd == "report": report(proj, a.index)
    elif a.cmd == "approve": decide(proj, parse_slots(a.arg), "approved", a.note)
    elif a.cmd == "reject": decide(proj, parse_slots(a.arg), "rejected", a.note)
    elif a.cmd == "pick": pick(proj, int(a.arg), a.arg2 or "b")
    elif a.cmd == "gate": sys.exit(0 if gate(proj, a.index) else 1)
    elif a.cmd == "upscale": upscale(proj)


if __name__ == "__main__":
    main()
