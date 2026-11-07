---
name: line-boil-thumbnail-short
description: Draws the thumbnail for a line-boil Short (9:16, 1080x1920) at make time, in the original style (2 to 4 words that name the topic, one big topic object, a face only when it helps, flat high-contrast background) with an accuracy test that the picture matches the video. Use for every Short thumbnail, and for a Short's Better thumbnail ideas.
metadata:
  type: skill
---

# Short thumbnail (original style)

Use this for a Short (9:16, 1080x1920). The long-video style is in `line-boil-thumbnail-long`.

Steps 1 to 4 of the line-boil skill are done first. This skill is the thumbnail step: it lands as `<project>/<project>-thumbnail.png`.

## Principles (read first)

Before rendering, ask: **"Can someone understand, or become curious about, this specific video just by looking at the thumbnail?"** If not, change the concept, not the polish.

1. **Topic first.** Start from the video's actual topic, its central question and its most interesting takeaway (read `script.json` and the title), not from keywords. A generic illustration of a keyword fails.
2. **One scene.** One strong, instantly understandable scene that shows the subject or opens a curiosity gap the video pays off.
3. **Subject-driven.** Pick the strongest visual elements for this topic (its own object, place, symbol or situation). The Bean is optional: include it only when it improves the storytelling, the emotion or the channel identity, never by default.
4. **Simple.** One dominant focal point, strong contrast, a clear composition, and minimal text (ideally 2 to 4 words). It must read at mobile size (judge a 180 px copy).
5. **On brand.** Keep the hand-drawn line-boil look: imperfect outlines and the channel palette, without trading away topic relevance. Be mindful of recognisability: a real brand or product keeps its own colours and symbol (an Instagram phone gets the Instagram purple-magenta-orange, not plain yellow); see **Mindful details** in `~/.claude/skills/line-boil/references/style.md`.

Settle the thumbnail text first (2 to 4 words that carry the topic's key noun, the title's own word if that is what makes the topic clear; see `~/.claude/skills/line-boil/references/youtube.md`), then write `web/thumb.js`:
   `CAP.on = false;` and a single `shot(0, { draw() {...} })` that shows the story's most extreme
   moment, with the topic's own object big and, if a character helps (see Principles), a big expression (`fx: ['take']`, wide eyes), a flat high-contrast
   background (a colour `paper()` plus a sunburst or a paper blob behind the character), and the words drawn with
   `bigWord(text, cx, y, size, fill, seed)` in the top third (y 150 to 320, size 100 to 120, PAPER or YEL fill).
   It loads after `cast.js`, so every character and prop is there. Keep the face in the middle band (y 350 to
   750) so it survives both the 9:16 Shorts frame and a centre-cropped square. Run `build.py thumb <project>`:
   it writes `<project>/<project>-thumbnail.png` at 1080x1920.
   **The subject comes first.** A thumbnail must make the topic obvious in one second, so build it around the *one object the
   title is about*, drawn large (at least a third of the frame) and recognisable by silhouette: a gum wad and a stick of gum, a
   cola can, a clipper and giant nails. Draw that prop in `cast.js` or `thumb.js` if the video has none; a bean's expression is
   never enough on its own. Then judge a 180 px copy of the PNG (feed size) with two tests, and redraw until both pass:
   - **Subject test.** Cover the text. Could a stranger name the topic from the picture alone? If not, the picture is random:
     add or enlarge the object.
   - **Text test.** Cover the picture. Do the words still point at the topic or its stakes, in 2 to 4 words, as a question,
     a number or a surprise, without repeating the title? Filler such as "NOPE" or "WOW" on its own fails; pair the reaction with
     the stakes ("STUCK INSIDE?"). Text that would fit any video fails.
   **Safe zone.** Profile grids crop the cover (Instagram shows a 3:4 centre crop of a 9:16 cover), so a headline at the very top is
   cut off. Draw the headline, subject and faces inside `gridSafe(() => { ... })` (it keeps them in y 155 to 830), the background
   outside it, and check `stills/thumb-crops.png`, which `build.py thumb` writes: nothing important may be cut in the 3:4 or the square.
   Then a flat high-contrast background and no empty areas; add a bean reacting to the stakes only if it improves the scene. The first gum thumbnail ("NOPE" and
   two beans, no gum) failed both tests; `gum-seven-years/web/thumb.js` shows the fix and `cola-sweat/web/thumb.js` another.

## Accuracy: the thumbnail must tell the truth about the video

A Short's thumbnail fails when a stranger cannot say what the video is about. Three rules, checked before you finish.

1. **The topic noun is in the words.** "TIME ZONES?" beats "WHO WINS?". If the title is a question, the words are that question, shortened. A word that would fit any video fails.
2. **The picture is the topic's own big object, drawn so it reads at feed size.** Judge the 180 px copy: anything smaller than about 6% of the frame height does not count as drawn (tiny watch faces, small icons, thin lines). An abstract topic needs a symbol a stranger would draw if asked to "draw this": time zones are a giant clock face or a globe with clocks (at least a third of the frame); a country is its flag colours or a big map-like shape, not just a bean in a hat; money is a big coin or tag; a habit is the thing itself. A character may react beside it when that helps, but is never the whole picture.
3. **It matches the video, not a different joke.** Use the objects and cast from the video's own key shot (write the shot's time in the sheet's `Still:` line), show the question's subject and not a random gag, and never show an answer or a number the video does not give. If the video withholds its answer until the end, the thumbnail asks the question and does not answer it.

**Accuracy test (do this last).** Look at the 180 px copy and write one sentence, as a stranger would, of what it is about. Put it next to the title. If the two do not describe the same video, or the sentence needs to guess, redraw. Report the sentence in your final message.
