# Visual direction

Every narration line carries production directions in **English**, in fields separate from the Hindi `text`. The edit is
built in Remotion (`channels/jadtak/remotion/`), so the fields below feed it directly through `make_timeline.py`.

## The fields on each script line

| Field | Required | What it holds |
|---|---|---|
| `kind` | yes | `still` (an illustration or photo), `archive` (real photograph, document or footage), `card` (a code-built graphic), `map` |
| `visual` | yes | One plain English sentence of what is on screen: subject, place, action, camera move. Written for an editor. |
| `prompt` | for AI stills | The image-generation prompt: the **visible composition only** (see "Prompts" below). |
| `frame` | when the picture exists | Path under the video's `art/` folder without extension, e.g. `frames/L012-barber-shop` (for `still` and `archive`). |
| `credit` | for `archive` | The on-screen credit, e.g. "फ़ोटो: <archive name>"; shown instead of the illustration tag. |
| `card` | for cards and maps | `{"type": ..., "props": {...}}` from the card catalogue below. |
| `camera` | optional | `push-in`, `pull-out`, `pan-left`, `pan-right`, `tilt-up`, `hold`, `parallax` (default: a slow push or pan chosen by the edit) |
| `sound` | optional | Music or effect cue for this line: `music: tension drone in`, `sfx: train whistle, far`, `silence 0.8s before reveal` |

## Picture sources, in order of preference

1. **Real archive**: photographs, documents, newspaper pages, footage, with rights or a clear licence. `kind: "archive"`.
   Credit on screen when the licence asks.
2. **Real locations shot or licensed today** (the place as it is now). `kind: "still"`, `visual` says "present-day".
3. **AI illustrations** in the channel's cinematic realistic style (`kind: "still"` with a `prompt`). Used for scenes no
   camera recorded. **No label on screen** (the owner's rule: no "चित्रण" tag on frames). The disclosure is made once: in the
   video description ("दृश्य कलाकार की कल्पना से बनाए गए हैं") and with YouTube's "altered or synthetic content" setting at
   upload, which YouTube asks for when realistic generated images show real people or events.
4. **Code-built cards and maps** for dates, names, numbers, quotes, sources, lists, places.

**Never present an AI image as genuine archival photography.** Prompts never ask for "old photograph", "archival photo",
"1940s press photo", "vintage newspaper print", fake captions or fake stamps for real events or real people. Period setting
is fine ("a 1940s Indian village home, cinematic realistic still"); period *photography* is not.

Real people: a likeness is allowed where the owner has decided so (Jad Tak: the saint himself may be shown). Living and
recently living public figures (business leaders, actors, cricketers) are shown from licensed photos or as unidentifiable
figures (back view, silhouette, hands), never as generated faces.

**The same person looks the same in every picture (owner's rule, 2026-11-20).** In the Neem Karoli Baba video one still
(n38) showed "the Baba" as a long-haired, long-white-bearded sadhu in white, and another (n15) gave the young Baba an
unrelated face; the owner caught both after the render. So:
- Write one **look line** per recurring person and paste it word for word into every prompt that shows them (for the
  saint: bald or close-cropped, short white beard, round heavy build, checked woollen blanket). A prompt that names the
  person without the look line is a fail.
- An "old saint" or "guru" in a scene about him is him: never a generic sadhu, even far in the background.
- A younger version of the person (childhood, early years) is shown without a clear face: from behind, far away, hands,
  or the place alone. An invented young face reads as somebody else.
- **Before the timeline:** open a contact sheet of every still used, and check each face of each recurring person
  against their look line. Replace a mismatch with a picture that fits the line (or with no person) before rendering.

## Prompts: composition only

A prompt describes what a camera would see. **It never contains** labels, disclaimers, narration or editorial notes:

| Never in a prompt | Why |
|---|---|
| चित्रण, "illustration only", "artist's impression", "AI generated" | the edit adds the tag; the image model might paint the words |
| जगह लगभग, "approximate location", "not to scale" | a map note, not a picture |
| वेबसाइट का दावा, "as claimed", "reportedly", "legend says" | an evidence status, not a visual |
| Hindi narration or any Devanagari | text in the image |
| "not archival", "generic", "no faces" (unless a face must truly be hidden) | negative clutter |

**Prompt pattern** (one paragraph, 40 to 90 words): `[style] [subject + action] [setting + period] [light + time of day]
[camera: lens, angle, framing] [mood] [what must not appear, only if needed]`.

Channel style line (the owner-approved look; prefix every prompt): `Create an image. 16:9 cinematic realistic still for a Hindi
documentary. Style: realistic film still, 35mm lens, natural light, shallow depth of field, soft film grain, muted colour grade
with deep forest greens, earthy browns and warm cream highlights, one small warm amber light source. Quiet, respectful,
dignified documentary mood. No text, no letters, no logos, no watermark, no borders, no halo, no glowing effects, no added
religious symbols. Scene:` Name a real person the owner allows directly ("Neem Karoli Baba (Maharaj-ji), the Indian saint of
Kainchi Dham"); don't describe them generically.

Example (the barber anecdote):

```
Cinematic realistic still, 16:9, natural film colour, soft volumetric light, shallow depth of field, an elderly Indian sadhu
wrapped in a checked woollen blanket rising from a barber's wooden chair, shaving foam still on one half of his face, the
startled young barber holding a straight razor, a small open-fronted village barber shop in north India in the mid
twentieth century, late afternoon sun slanting through the doorway, eye-level 35mm, medium shot, quiet suspense, no text,
no signage
```

## Card catalogue (Remotion, `src/Cards.tsx` and `src/MapCard.tsx`)

| `card.type` | Use for | `props` |
|---|---|---|
| `title` | a film, book or name with a subtitle | `kicker`, `title`, `sub`, `highlight` (a word to glow) |
| `question` | the central question | `text` |
| `date` | a date stamp | `big`, `pre` (e.g. "करीब"), `sub` (place), `note` |
| `label` | a person, place or short heading | `kicker`, `text`, `sub`, `faded` |
| `source` | a book or document on an index card | `title`, `meta` (author, year) |
| `quote` | recorded words, on paper | `text`, `label` ("अनुवाद" for translations), `source` |
| `words` | 2 to 4 words arriving one by one | `items`, `vertical`, `blur` |
| `morph` | one name or word turning into another | `from`, `to` |
| `stamp` | a verdict stamp ("नहीं मिला") | `kicker`, `text` |
| `blanks` | struck-out claims | `items`, `note` |
| `flow` | A → B | `items`, `vertical` |
| `layers` | stacked layers of a memory or a process | `items`, `show` |
| `books` | several sources pointing to one idea | `items`, `target` |
| `define` | a word and its meaning | `word`, `meaning` |
| `list` | a list with one item lit | `items`, `lit`, `note`, `open` |
| `steps` | a numbered roadmap | `items`, `show`, `words` |
| `columns` | three pillars | `items`, `lit`, `fresh` |
| `figure` | a counting number | `num`, `unit`, `sub` |
| `split` | two sides of an answer | `left: [head, line]`, `right: [head, line]` |
| `statement` | a line of narration on screen (last resort) | `text` |
| `map` | places on a real map | `places: [[lon, lat, label]]`, `focus`, `zoom: [from, to]`, `bbox`, `ring: {at, km}`, `caption: {title, text}` |

Card text is short (2 to 8 words), comes from the narration or the ledger, and never introduces a fact the narration does
not say. Card text never carries a source tag, a status word or a disclaimer. Keep map crops inside regions whose borders are not disputed.

## Shots and editing rhythm by beat

| Beat | Picture | Cut length | Camera | Sound |
|---|---|---|---|---|
| Cold open | strongest illustrations, close and medium | 2 to 4 s | push-in | low drone, single instrument |
| Date-place stamp | `date` card or a wide establishing shot | 3 s | hold or slow push | one bell or a sting |
| Anecdote setup | wide → medium | 4 to 6 s | slow pan | ambient (village, rain, train) |
| Unusual act / escalation | medium → close on the object (soap, blanket, pill) | 3 to 4 s | push-in | music thins out |
| Before the reveal | hold on a face or object | 2 s + 0.5 to 1 s silence | hold | silence |
| Reveal | the image that carries the strangest fact | 3 s | slow pull-out | a single hit, then music returns |
| Explainer | `define`, `flow` or map card | 5 to 8 s | none | music low |
| Testimony / quote | `quote` or `source` card on paper | as long as the words take | none | quiet bed |
| Emotional beat | wide landscape, small figure | 8 to 12 s | very slow | strings or flute, sparse |
| Montage of names | `words` or `books` card, licensed photos | 1.5 to 2 s each | quick pushes | pulse |
| Chapter seam | chapter bumper + establishing shot | 3 s | hold | transition swell |
| Ending callback | the cold open's image again | 4 to 6 s | slow pull-out | the opening's motif, resolved |

Average shot length targets: Short 3 to 4 s, Standard 4 to 5 s, Long 4 to 6 s. One AI still may cover two or three lines
when the camera keeps moving; never more than 15 s on one image.

## Music and sound

- One **motif** per video (a flute phrase, a tanpura drone, a bell) introduced in the cold open and resolved at the callback.
- Mystery: drones and low pulses. Devotion: tanpura, bansuri, temple bells, distant bhajan textures. Outsiders: sparse
  piano or guitar. Legacy: warm strings.
- **Silence is a tool**: half a second to a second before a reveal, and after the most emotional line.
- Effects only for objects the story names (train, bells, rain, a crowd, a razor), never decoration.
- Licensed or generated-for-the-channel music only; note the source in the production notes.

## Honesty in pictures

- **Nothing on screen that reads like a footnote:** no "चित्रण", no "जगहें लगभग", no "वेबसाइट का दावा", no "(शोध-ग्रंथ के
  मुताबिक़)" or other source tags on cards, maps or frames. Evidence lives in the ledger; the narration carries any
  attribution the viewer needs.
- AI stills carry no tag (disclosed once, see above); real photos carry their credit; reconstructions never imitate archive.
- A map shows only places the ledger supports; an uncertain place is a ring or an area, not a pin, and needs no caption saying so.
- A quote card shows only recorded words; a translation is marked "अनुवाद".
- No invented documents, letters, newspaper headlines or signatures on screen.
