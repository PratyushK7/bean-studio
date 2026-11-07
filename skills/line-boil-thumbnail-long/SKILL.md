---
name: line-boil-thumbnail-long
description: Draws the thumbnail for a line-boil-wide long video (16:9, 1280x720) with the topic named outright in the words (the title's key words, ideally 2 to 4), the topic's own object as one dominant focal point (a character only when it helps), and a click hook. Use for a long video's thumbnail, made now or from Bean Studio's Better thumbnail button (three ideas).
metadata:
  type: skill
---

# Long-video thumbnail (topic-first)

Use this for a long video (16:9, 1280x720). The Short style is in `line-boil-thumbnail-short`.

The thumbnail is the topic said plainly, so a stranger knows what the video is about in one second. The reference is TED-Ed's "HOW DOES CAFFEINE KEEP US AWAKE?".

## Principles (read first)

Before rendering, ask: **"Can someone understand, or become curious about, this specific video just by looking at the thumbnail?"** If not, change the concept, not the polish.

1. **Topic first.** Start from the video's actual topic, its central question and its most interesting takeaway (read `script.json` and the title), not from keywords. A generic illustration of a keyword fails.
2. **One scene.** One strong, instantly understandable scene that shows the subject or opens a curiosity gap the video pays off.
3. **Subject-driven.** Pick the strongest visual elements for this topic (its own object, place, symbol or situation). The Bean is optional: include it only when it improves the storytelling, the emotion or the channel identity, never by default.
4. **Simple.** One dominant focal point, strong contrast, a clear composition, and minimal text (ideally 2 to 4 words). It must read at mobile size (judge a 180 px copy).
5. **On brand.** Keep the hand-drawn line-boil look: imperfect outlines and the channel palette, without trading away topic relevance. Be mindful of recognisability: a real brand or product keeps its own colours and symbol (an Instagram phone gets the Instagram purple-magenta-orange, not plain yellow); see **Mindful details** in `~/.claude/skills/line-boil/references/style.md`.

## The words state the topic, outright
- The lettering is the title's key words in plain language, ideally 2 to 4 words (up to 6 only when a short question needs it). Repeating the title is wanted, not avoided.
- The topic noun is the biggest word and in the strongest colour.
- A teaser that hides the topic ("3 PM TO MIDNIGHT", "NOPE", a bare number) fails.
- Add the hook on top of the topic, never instead of it: phrase the words as the question the viewer wants answered, or add a short stake word ("...AT NIGHT?", "...WITHOUT KNOWING?"), but only a promise the video pays off honestly.

## The picture says the same thing
- The topic's own object, place or situation, drawn large (at least a third of the frame). Add ONE character doing the topic's action (yawning, panicking, staring at it) with ONE strong, readable emotion only when it improves the story; otherwise leave it out.
- No second idea, no clutter.

## Layout (1280x720)
- Words large and down the left third or top left.
- The main subject in the middle and right (with a character beside it if used).
- Flat high-contrast palette colours, a clean background.
- Nothing important in the bottom-right corner (the duration badge) or in the bottom 15%.

## Tests (judge a 180 px copy at feed size, redraw until all pass)
- **Subject test.** Cover the words. Can a stranger name the topic from the picture alone (the topic's own object, with a character doing the topic's action beside it if one is used)?
- **Topic test.** Cover the picture. Do the words alone say exactly what the video is about (the topic noun is in them)? Compare with "HOW DOES CAFFEINE KEEP US AWAKE?".
- **Click test.** Is there ONE dominant focal point (and ONE strong emotion if a face is used), ONE unresolved thing (a curiosity gap, or a stake the viewer may be suffering without knowing), and nothing cluttered? Pick the one of the ideas a stranger is most likely to click, and only use promises the video pays off honestly.

## Ideas (for the Better thumbnail button)
Write THREE ideas on three different triggers from: Curiosity, Fear, Shock, Stakes, Mystery, Before / after, Absurd. All three name the topic in their words. At least one leans on fear or loss the video honestly delivers on, and at least one on curiosity.

## Output
Draw with `web/thumb.js` (a single `shot(0, { draw() {...} })`, loading after `cast.js`), then run `build.py thumb <project>`, which writes `<project>/<project>-thumbnail.png` at 1280x720. Update the YouTube sheet's THUMBNAIL section (File:, Text:, Still:, Brief:) to match what you drew. Name the topic's words in the sheet's Text line.
