---
name: line-boil-thumbnail-long
description: Draws the thumbnail for a line-boil-wide long video (16:9, 1280x720) that works as a pair with the title (2 to 4 big words that share at most one noun with the title and add the stakes or the twist), the topic's own object as one dominant focal point (a character only when it helps), and a click hook. Use for a long video's thumbnail, made now or from Bean Studio's Better thumbnail button (three ideas).
metadata:
  type: skill
---

# Long-video thumbnail (topic-first)

Use this for a long video (16:9, 1280x720). The Short style is in `line-boil-thumbnail-short`.

A 16:9 thumbnail always sits next to its title, so the two work as a pair: the title asks the question in the words people search,
and the thumbnail shows the topic's object and adds what the title does not say (the stakes or the twist). Together a stranger knows
the topic in one second and has a reason to click.

## Principles (read first)

Before rendering, ask: **"Can someone understand, or become curious about, this specific video just by looking at the thumbnail?"** If not, change the concept, not the polish.

1. **Topic first.** Start from the video's actual topic, its central question and its most interesting takeaway (read `script.json` and the title), not from keywords. A generic illustration of a keyword fails.
2. **One scene.** One strong, instantly understandable scene that shows the subject or opens a curiosity gap the video pays off.
3. **Subject-driven.** Pick the strongest visual elements for this topic (its own object, place, symbol or situation). The Bean is optional: include it only when it improves the storytelling, the emotion or the channel identity, never by default.
4. **Simple.** One dominant focal point, strong contrast, a clear composition, and minimal text (ideally 2 to 4 words). It must read at mobile size (judge a 180 px copy).
5. **On brand.** Keep the hand-drawn line-boil look: imperfect outlines and the channel palette (the video's theme applies by itself: write `RED`/`BLUE`/`YEL`/`PAPER`/`INK`, never hex; a `noir` video's thumbnail is dark, with the words still high-contrast), without trading away topic relevance. Be mindful of recognisability: a real brand or product keeps its own colours and symbol (an Instagram phone gets the Instagram purple-magenta-orange, not plain yellow); see **Mindful details** in `~/.claude/skills/line-boil/references/style.md`.

## The words add the stakes, not the title again
- **2 to 4 words, big:** one or two lines, the main word about 100 to 130 tall in world units (the 960x540 frame), so they read at
  246 px wide. The caffeine thumbnail's six words in five lines ("HOW DOES CAFFEINE STEAL YOUR SLEEP?") were too small and repeated the
  title word for word: that fails.
- **Share at most ONE noun with the title**, usually the topic noun (COFFEE, CAFFEINE), so the topic stays obvious; the rest states the
  stakes or the twist ("STILL IN YOU AT 12" next to "Why Your 3 PM Coffee Still Costs You Sleep").
- **Honest:** only a promise the video pays off. "3 PM = NO SLEEP" fails for a video that says you still fall asleep as usual.
- Filler that hides the topic and fits any video ("NOPE", "WOW", a bare number with no noun nearby) fails.

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
- **Pair test.** Read the title, then the words. Do they share at most one noun, and do the words add something the title does not say
  (the stakes or the twist)? Together, do they say exactly what the video is about?
- **Click test.** Is there ONE dominant focal point (and ONE strong emotion if a face is used), ONE unresolved thing (a curiosity gap, or a stake the viewer may be suffering without knowing), and nothing cluttered? Pick the one of the ideas a stranger is most likely to click, and only use promises the video pays off honestly.

## Ideas (for the Better thumbnail button)
Write THREE ideas on three different triggers from: Curiosity, Fear, Shock, Stakes, Mystery, Before / after, Absurd. All three keep the topic clear (its object in the picture, at most one noun shared with the title) and put the stakes or the twist in the words. At least one leans on fear or loss the video honestly delivers on, and at least one on curiosity.

## Output
Draw with `web/thumb.js` (a single `shot(0, { draw() {...} })`, loading after `cast.js`), then run `build.py thumb <project>`, which writes `<project>/<project>-thumbnail.png` at 1280x720. Update the YouTube sheet's THUMBNAIL section (File:, Text:, Still:, Brief:) to match what you drew. Put the words in the sheet's Text line and lint the title with `title.py --thumb "<the words>"`: it flags every shared word, so a "repeats the title" warning naming the ONE shared topic noun is expected; two or more shared words fail.
