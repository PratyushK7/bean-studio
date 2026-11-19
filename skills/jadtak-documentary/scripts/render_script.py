"""Write the readable script and the voice text from script.json.

  python render_script.py <project folder>
    -> <slug>-script.md   title, question, answer, takeaway, then every chapter with timestamps and every line with its beat,
                          fact ids, visual, prompt, camera and sound
    -> <slug>-voice.txt   the narration only, one sentence a line (what the voice reads)
Times come from scratch/scratch-narration-lines.json when it matches, otherwise from 160 words a minute."""
import json, sys
from pathlib import Path

WPM = 160


def main():
    folder = Path(sys.argv[1]).resolve()
    doc = json.loads((folder / "script.json").read_text(encoding="utf-8"))
    lines, slug = doc["lines"], folder.name
    tfile = folder / "scratch/scratch-narration-lines.json"
    starts = None
    if tfile.exists():
        t = json.loads(tfile.read_text(encoding="utf-8"))
        if len(t) == len(lines): starts = [x["start"] for x in t]
    if not starts:
        starts, s = [], 0.0
        for l in lines: starts.append(s); s += len(l["text"].split()) / WPM * 60 + 0.35
    mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    words = sum(len(l["text"].split()) for l in lines)
    out = [f"# {doc['title']}", "",
           f"_Jad Tak · band: {doc.get('band', '?')} · {words:,} words · about {mmss(starts[-1] + 5 if starts else 0)} · status: {doc.get('status', 'draft')}_", "",
           "**Other titles:** " + " · ".join(doc.get("alt_titles", [])), "",
           f"**Central question:** {doc.get('question', '')}", "", f"**Honest answer:** {doc.get('answer', '')}", "",
           f"**Takeaway:** {doc.get('gain', '')}", "", f"**Ledger:** `{doc.get('ledger', '')}`", ""]
    for n, (l, t) in enumerate(zip(lines, starts), 1):
        if l.get("act"): out += ["", f"# {l['act']}"]
        if l.get("chapter"): out += ["", f"## {l['chapter']}  ({mmss(t)})", ""]
        meta = " ".join(x for x in [f"`{l['beat']}`" if l.get("beat") else "", f"[{', '.join(l['facts'])}]" if l.get("facts") else ""] if x)
        out.append(f"{n}. **{mmss(t)}** {l['text']} {meta}".rstrip())
        out.append(f"   - _{l['kind']}_: {l.get('visual', '')}")
        if l.get("card"): out.append(f"   - card: `{json.dumps(l['card'], ensure_ascii=False)}`")
        if l.get("prompt"): out.append(f"   - prompt: {l['prompt']}")
        cues = ", ".join(x for x in [l.get("camera", ""), l.get("sound", "")] if x)
        if cues: out.append(f"   - cues: {cues}")
    if doc.get("sources"): out += ["", "## Sources", ""] + [f"- {s}" for s in doc["sources"]]
    (folder / f"{slug}-script.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (folder / f"{slug}-voice.txt").write_text("\n".join(l.get("say") or l["text"] for l in lines) + "\n", encoding="utf-8")
    print(folder / f"{slug}-script.md"); print(folder / f"{slug}-voice.txt")


if __name__ == "__main__":
    main()
