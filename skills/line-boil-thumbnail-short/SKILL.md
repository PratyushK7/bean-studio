---
name: line-boil-thumbnail-short
description: Draws the thumbnail for a line-boil Short (9:16, 1080x1920) at make time, in the original style (2 to 4 words that name the topic, one big topic object, a face only when it helps, flat high-contrast background) with an accuracy test that the picture matches the video. Use for every Short thumbnail, and for a Short's Better thumbnail ideas.
metadata:
  type: skill
---

# Short thumbnail (original style)

Use this for a Short (9:16, 1080x1920). The long-video style is in `line-boil-thumbnail-long`.

Steps 1 to 8 of the line-boil skill are done first. This skill is step 9: it renders `<project>/<project>-thumbnail.png` and
`stills/thumb-crops.png`.

## Principles (read first)

Before writing any code, ask: **"Can a stranger understand, or become curious about, this specific video just by looking at the
thumbnail?"** If not, fix the concept, not the polish.

1. **Topic first.** Start from the video's actual topic, its central question and its most interesting takeaway (read `script.json`
   and the title), not from keywords. A generic illustration of a keyword fails.
2. **One scene.** One strong, instantly understandable scene that shows the subject or opens a curiosity gap the video pays off.
3. **Subject-driven (the one-third rule).** Build it around the *one concrete object the title is about*, drawn large (at least a
   third of the frame) with a silhouette you know at once: the gum wad and stick in `gum-seven-years/web/thumb.js`, the sweating
   cola can in `cola-sweat/web/thumb.js`, a giant clipper and nails. An abstract topic gets the symbol a stranger would sketch if
   asked to "draw this": a giant clock or a globe of clocks for time zones, flag colours or a map shape for a country, a big coin or
   price tag for money, the thing itself for a habit. Anything under about 6% of the frame height vanishes at feed size and does not
   count as drawn (tiny watch faces, small icons, thin lines). If the video's own prop is too small, draw a big hero version in
   `cast.js` or `thumb.js`.
4. **The bean is optional.** A bean's expression is never enough on its own. Add ONE bean reacting (`fx: ['take']`, wide eyes)
   beside the object only when it sharpens the story or the emotion: never by default, and never two beans talking with no object.
5. **Simple.** One dominant focal point, strong contrast, a clear composition, no empty dead space.
6. **2 to 4 words with the topic noun.** The words carry the **topic's key noun plus the stakes or question** ("STUCK INSIDE?",
   "TIME ZONES?", "INSTAGRAM HEARD ME?"). Use the title's core noun when that is what makes the topic clear (this overrides the
   "none repeated from the title" note in `references/youtube.md`). Reaction filler that would fit any video ("NOPE", "WOW",
   "WHO WINS?") fails.
7. **On brand, and recognisable.** Keep the hand-drawn line-boil look and the channel palette, but never at the cost of
   recognisability: a real brand, app, flag or warning keeps its own colours and symbol (an Instagram phone gets the Instagram
   purple-magenta-orange, never flat yellow). See **Mindful details** in `~/.claude/skills/line-boil/references/style.md`.
8. **True to the video.** Use the objects and cast from the video's own key shot (write its time in the YouTube sheet's `Still:`
   line). Show the question's subject and stakes, never a random side gag, and never the answer or a number the video withholds
   until the payoff.

## Writing `web/thumb.js`

`web/thumb.js` loads after `cast.js`, so every character and prop is available.

1. Set `CAP.on = false;` at the top and write a single `shot(0, { draw() { ... } })`.
2. **Background, outside `gridSafe`:** a flat high-contrast colour (`paper(<colour>)`) plus a sunburst (`burst`) or a paper blob
   behind the focal point.
3. **Everything that matters, inside `gridSafe(() => { ... })`:** it shrinks the drawing about the centre so the marks survive the
   crops (Instagram's profile grid shows a 3:4 centre crop, a square tile shows y 210 to 750, and the YouTube Shorts shelf lays the
   title over the bottom of the card, from about y 720 down). The y values below are the ones you pass inside `gridSafe`:
   - **Headline:** `bigWord(text, cx, y, size, fill, seed)` in one or two lines between **y 150 and 320** (two lines: about y 175
     and 290), size 100 to 120 (down to about 84 for a long word), PAPER, YEL or RED fill against the background.
   - **Hero object and optional face:** in the band **y 330 to 760**, the object at least a third of the frame.
4. **Render:** `python "$ENGINE/build.py" thumb <project>`. It writes `<project>/<project>-thumbnail.png` (1080x1920) and
   `stills/thumb-crops.png`: the 9:16 feed, the 3:4 grid and the square side by side, each panel about feed size (270 px wide).

## Check: read `stills/thumb-crops.png` once

One image read covers feed size and both crops. Every thumbnail passes all four checks, or you edit `web/thumb.js` and re-render:

1. **Crops.** In the 3:4 and square panels, is any letter of the headline, the hero object or a face's eyes and mouth cut off? Is
   anything key low enough to sit under the Shorts shelf title?
2. **Subject test.** Cover the words. Could a stranger name the specific topic from the picture alone? If not, enlarge or clarify
   the object.
3. **Text test.** Cover the picture. Do the 2 to 4 words name the topic noun and its stakes ("STUCK FOR 7 YEARS?", not "NOPE")?
4. **Accuracy test.** From the feed-size panel, write one plain sentence of what a stranger would think the video is about and put
   it next to the title. If the two do not describe the same video, or the sentence needs a guess, redraw. Report the sentence in
   your final message.

The first gum thumbnail ("NOPE" and two beans, no gum) failed checks 2 and 3; `gum-seven-years/web/thumb.js` shows the fix.
