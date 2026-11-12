"""Decoding Vyapaar image prompts: script.json -> prompts/*.txt (one self-contained prompt per line, for the ChatGPT bulk extension) + images-index.json

    python tools/vyapaar_prompts.py <project> [--batch 30] [--style hinexp]

Order of the images the extension makes (the studio's Collect step numbers downloads in arrival order, so this order IS the file number):
    1..k   one character sheet per recurring person (found from "Name (description)" in the visual notes), so you can attach a sheet to every
           later prompt of that person with the extension's "+ Images" button
    k+1..  one picture per hero or still line (a card line is drawn by code and needs none); identical visual notes share one picture
images-index.json maps each image number to the script lines it serves, its kind and its prompt, so the assembler knows which picture is which.
prompts/ is rewritten every run (the old files are moved to prompts/_old-<time>/).
"""
import argparse, json, re, shutil, time
from pathlib import Path

STYLES = {
    "hinexp": ("Clean semi-realistic digital illustration for a Hindi business-documentary explainer channel: realistic proportions, smooth clean shading with gentle cel-like face rendering, "
               "bright airy natural daylight, fresh clear colours (sky blue, mint grey-green, cream, warm wood, soft gold), tidy detailed environment, cinematic composition, 16:9 widescreen. "
               "No readable text, letters, numbers or logos anywhere; any signboards are blank."),
}
PERSON = re.compile(r"([A-Z][A-Za-z]+(?: (?:ji|dada))?) \(([^()]{20,220})\)")   # Ramesh (a 52-year-old ... jacket)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--batch", type=int, default=30); ap.add_argument("--style", default="hinexp")
    a = ap.parse_args(); proj = Path(a.project); style = STYLES[a.style]
    lines = json.loads((proj / "script.json").read_text(encoding="utf-8"))["lines"]
    # characters: the first full description of each name in the visual notes
    people = {}
    for l in lines:
        for name, desc in PERSON.findall(l.get("visual", "")):
            people.setdefault(name, desc.strip())
    index, prompts = [], []
    for name, desc in people.items():
        p = (f"Character sheet of {name}, {desc}: front view and three-quarter view, standing relaxed, full body, on a plain warm grey background. {style}")
        index.append({"n": len(index) + 1, "type": "character", "name": name, "lines": [], "kind": "ref", "prompt": p}); prompts.append(p)
    seen = {}
    for i, l in enumerate(lines):
        if l.get("kind") not in ("hero", "still"): continue
        v = l.get("visual", "").strip()
        if not v: continue
        if v in seen: index[seen[v]]["lines"].append(i + 1); continue
        p = f"{v.rstrip(' .')}. Cinematic composition. {style}"
        index.append({"n": len(index) + 1, "type": "scene", "lines": [i + 1], "kind": l["kind"], "chapter": l.get("chapter"), "prompt": p}); prompts.append(p)
        seen[v] = len(index) - 1
    pd = proj / "prompts"; pd.mkdir(exist_ok=True)
    old = [f for f in pd.glob("*.txt")]
    if old:
        keep = pd / f"_old-{time.strftime('%H%M%S')}"; keep.mkdir()
        for f in old: shutil.move(str(f), keep / f.name)
    k = len(people)
    (pd / "01-characters.txt").write_text("\n".join(prompts[:k]) + "\n", encoding="utf-8")
    scenes = prompts[k:]; nb = (len(scenes) + a.batch - 1) // a.batch
    for b in range(nb):
        (pd / f"{b + 2:02d}-scenes-{b + 1}-of-{nb}.txt").write_text("\n".join(scenes[b * a.batch:(b + 1) * a.batch]) + "\n", encoding="utf-8")
    for e in index[:k]: e["file"] = "01-characters.txt"; e["pos"] = e["n"]
    for j, e in enumerate(index[k:]): e["file"] = f"{j // a.batch + 2:02d}-scenes-{j // a.batch + 1}-of-{nb}.txt"; e["pos"] = j % a.batch + 1
    (proj / "images-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    (pd / "README.txt").write_text(
        "Run the files in this order in the ChatGPT extension (Prefix and Suffix empty, wide aspect, delay 5 to 7 s):\n"
        "  01-characters.txt first. Check the sheets, then attach each person's sheet with '+ Images' for the scene files that show them.\n"
        "  02-... onwards: one file per sitting (about 30 pictures each, so plan limits are not hit).\n"
        "Run one file, then press Get my pictures in the studio (no Start button). Image numbers follow this order (see images-index.json).\n", encoding="utf-8")
    cards = sum(1 for l in lines if l.get("kind") == "card")
    print(f"{len(lines)} script lines: {k} character sheets + {len(scenes)} scene pictures ({sum(len(x['lines']) for x in index[k:])} lines served; {cards} card lines are drawn by code)")
    print(f"wrote {nb + 1} files in {pd}: 01-characters.txt, {nb} scene file(s) of up to {a.batch}; images-index.json")


if __name__ == "__main__":
    main()
