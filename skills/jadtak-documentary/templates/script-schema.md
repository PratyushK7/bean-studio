# script.json: the production script

`script.json` in the video's project folder. One object per spoken sentence. It feeds the scratch narration, the
Remotion edit (`channels/jadtak/remotion/make_timeline.py`), `scripts/scriptcheck.py` and `scripts/render_script.py` (which
writes the readable `<slug>-script.md` and the voice text).

## Top level

```json
{
  "title": "नीम करोली बाबा: ...",
  "alt_titles": ["...", "..."],
  "channel": "jadtak",
  "language": "hi-Latn (Hinglish on screen, Devanagari to the voice)",
  "band": "standard",
  "target_minutes": 20,
  "question": "क्या ...?",
  "answer": "two sentences: what the record shows; what belief holds",
  "gain": "the one takeaway",
  "ledger": "<slug>-ledger.md",
  "references": ["RZ", "SM", "AG"],
  "status": "draft | evaluated | approved by the owner on <date>",
  "sources": ["Ram Dass, Miracle of Love, 1979, p. 12", "https://..."],
  "lines": []
}
```

## A line

| Field | Required | Notes |
|---|---|---|
| `text` | yes | The narration in Hinglish (Latin script), one sentence: what the script, the cards and the subtitles show. |
| `say` | yes | The same sentence in Devanagari, exactly as the voice speaks it. Same sentence count as `text` (the checker fails a mismatch). |
| `cont` | set by the build | `true` on every part of a split source line except the last, so the voice gives it a short inner pause. |
| `kind` | yes | `still`, `archive`, `card`, `map` |
| `visual` | yes | English, what is on screen (see `references/visual-direction.md`). |
| `prompt` | for a new AI still | composition only; no labels, disclaimers or Devanagari |
| `frame` | when the picture exists | path under `art/` without extension |
| `credit` | for `archive` | on-screen credit |
| `card` | for `card` and `map` | `{"type": ..., "props": {...}}` |
| `camera`, `sound` | optional | editing and sound cues |
| `chapter` | first line of each chapter | the on-screen chapter title, in Hinglish, 3 to 6 words |
| `act` | first line of each act (Long band) | "Act 3: …" (English, for the plan) |
| `facts` | every line that states a fact | ledger ids, e.g. `["F12", "RZ07"]` |
| `beat` | recommended | one of `hook`, `promise`, `name`, `question`, `stamp`, `setup`, `escalation`, `rehook`, `reveal`, `payoff`, `explainer`, `attribution`, `maxim`, `handoff`, `callback`, `method`, `cta` |
| `opens`, `closes` | when a line opens or closes a loop | loop ids from the plan, e.g. `["L2"]` |
| `anecdote` | optional | the inventory id, e.g. `"A3"` |

The checker uses `beat` to measure re-hook spacing (`hook`, `rehook`, `reveal`, `question`, `handoff`, `promise` count as
pulls), `opens`/`closes` for the loop audit, and `facts` against the ledger. Its narration rules (words, attribution,
sentence length) read `say`.

Card text is Hinglish too. Cards whose heading is a Hindi word take a `head` prop (`"head": "Kitab"` on a source card,
`"head": "Matlab"` on a define card). With `"language": "hi-Latn…"`, `make_timeline.py` sets the chapter labels to
"Shuruaat" and "Adhyay n".

## Example lines (the barber anecdote)

Older scripts were Devanagari-only (`text` only); new scripts add a Hinglish `text` and move the Devanagari to `say`, e.g.
`{"text": "Us aadmi ke chehre par saabun laga tha.", "say": "उस आदमी के चेहरे पर साबुन लगा था।", ...}`.

```json
[
  {"text": "भक्तों में यह कहानी सबसे ज़्यादा सुनाई जाती है।", "kind": "still", "beat": "attribution", "anecdote": "A2",
   "facts": ["AG13"], "visual": "A quiet village lane at dusk, a small barber shop with its lamp lit", "camera": "push-in",
   "sound": "music: single flute phrase (the motif)",
   "prompt": "Cinematic realistic still, 16:9, natural film colour, soft volumetric light, shallow depth of field, a quiet north Indian village lane at dusk in the mid twentieth century, a tiny open-fronted barber shop with a kerosene lamp glowing inside, a wooden chair and a small mirror visible, dust in the warm light, wide shot, eye level, calm and expectant"},
  {"text": "एक दिन बाबा एक नाई की दुकान पर दाढ़ी बनवा रहे थे।", "kind": "still", "beat": "setup", "facts": ["RZ07"],
   "visual": "The sadhu in the barber's chair, foam on his cheeks", "frame": "frames/L041-barber-chair"},
  {"text": "उस आदमी के चेहरे पर साबुन लगा था।", "kind": "still", "beat": "reveal", "facts": ["RZ07"], "closes": ["L3"],
   "visual": "Close on a weathered hand holding coins out to a young man at a rural bus stand", "sound": "silence 0.8s before; soft hit on 'साबुन'",
   "frame": "frames/L045-coins-hand"},
  {"text": "1967। नैनीताल से आगे, पहाड़ों में।", "kind": "card", "beat": "stamp", "chapter": "पहाड़ों में एक मोड़",
   "card": {"type": "date", "props": {"big": "1967", "sub": "कैंची, नैनीताल के पास"}}, "visual": "Date card over the blurred hills"},
  {"text": "रामदास अपनी किताब में लिखते हैं ...", "kind": "card", "beat": "attribution", "facts": ["F23"],
   "card": {"type": "source", "props": {"title": "Inside Out", "meta": "राम दास, 1976"}}, "visual": "Index card with the book's name"}
]
```
