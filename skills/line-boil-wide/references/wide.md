# Long-form (16:9) staging, pacing, scenes, music and chapters

Everything in line-boil's `style.md` and `api.md` applies. These are the differences for a 1920x1080 video.

## The frame

- The world is **960 x 540** (drawn at 2x). `W` and `H` are 960 and 540; y runs down. A Short is 540 x 960.
- The frame is only 540 high, so characters are **smaller than in a Short**: a `tall` bean at size 1.1 is already a third of the
  height. Use `size` 0.9 to 1.4 for a hero, 0.5 to 0.8 for a reactor, 1.5 to 2 only for a close-up. `tiny` beans can go to 1.5.
- Put the **ground near y 430** (the `set*()` helpers return it). Keep faces and key props between y 60 and 430 and x 60 and 900.
- A wide frame has room for **two or three beans side by side** with space between them; a crowd is one object (a row of `tiny` beans).
- Camera moves are gentler than in a Short: `z` 1 to 1.06 over a shot, a pan of 40 to 80 px. A fast `smear` between chapters is fine.

## No burned-in captions

The industry standard for long explainers (Kurzgesagt, Veritasium, MinuteEarth, TED-Ed, Vox, Wendover, CGP Grey and others: checked on
frames from their videos) is **no subtitles in the picture**; closed captions are a track viewers switch on, and the `.srt` is uploaded for
that. `CAP.on` is false for a wide project. Show numbers, names and key terms as on-screen labels (a sign or a label shape held by a bean,
a counter that ticks up) for the second they matter. If the user asks for burned-in captions, `CAP.on = true` in `cast.js`: they then sit in
the bottom band (y 476), up to five words at a time, and a close-up can move them with `cap: 'top'` or `cap: false`.

## The scene and sound plan

Write `<project>-plan.md` before the first shot. One row per chapter:

| Chapter | Set and place | Time and colour | Beans | Props | Music mood | Sound / silence | The joke |
|---|---|---|---|---|---|---|---|

Then build the shots from it. The rules:

1. **The scene follows the script.** Where the sentence happens is where the picture is: a theatre in the sunk-cost chapter, a gym in the
   present-bias chapter, a night sky for the 3 a.m. worry, a stage for a verdict, a desk for the data. Change the place or the dominant
   colour at least every chapter, and again inside a long chapter when the idea turns. Two neighbouring chapters never share both set and colour.
2. **Use the set helpers**, then dress them with props and beans. They all work in this frame and return the ground y:

   | Set | Looks like | Use it for |
   |---|---|---|
   | `setSunny(t)` | blue sky, drifting clouds, hills, grass | the world outside, a fresh start, everyday science |
   | `setNight(t)` | black sky, twinkling stars, a moon | late hours, worry, sleep, mystery, the unknown |
   | `setRoom(t, {wall, floor})` | a home: window, picture, floor | habits, money at home, sleep, small daily choices |
   | `setStreet(t)` | buildings, pavement, a road with moving dashes | shops, towns, crowds, commuting, the economy |
   | `setStage(t, {wall})` | red curtains, a spotlight, a stage | a sketch, a demonstration, a verdict, a joke |
   | `setDesk(t, {wall, chart})` | wall chart, a desk, a lamp, a mug | work, data, evidence, "the numbers" |
   | `setSpace(t)` | black space, stars, a ringed planet | big scale, the universe, long odds |
   | `setBlank(t, color)` | one flat colour with a faint sunburst | a diagram, a chart, a label and nothing else |

   `setScene(name, t, opts)` picks one by name. When none fits, build the place from `band`, `ground`, `hills`, `shape` and the props.
   Palette only: RED, BLUE, YEL, PAPER, INK (the lighter sunburst tints are already in the helpers), except a real brand's own colours on that one object (see "Mindful details" in `style.md`).
3. **The music follows the feeling.** `musicMood(t, mood, gain)` changes the underscore at second `t` (a 1 to 1.6 s crossfade) until the next
   call. Call it at every chapter start and at every turn:

   | Mood | Feels like | Use it when the script is |
   |---|---|---|
   | `curious` | light plucks, C major (the default) | introducing an idea, asking a question |
   | `playful` | bouncy, G major, 128 bpm | a joke, a silly example, a mistake being made |
   | `upbeat` | brighter, C major, 132 bpm | a fast montage, a win, "here is the good news" |
   | `calm` | slow pads and soft bells, F major | a clear explanation, the quiet takeaway, a recap |
   | `serious` | low slow pads, D minor | the stakes, a warning, a hard fact, a study |
   | `tense` | low drone with ticks, A minor | a problem getting worse, "but here is the catch", a countdown |
   | `mystery` | open, unresolved pads and bells, E minor | an unanswered question, a surprising result, "so why?" |
   | `triumphant` | pads with a rising arpeggio, D major | the payoff, the answer, the callback |
   | `silent` | nothing | the punchline, a dramatic pause, a fact that needs no help |

   Rules: **at least four different moods in a 7-minute video**; the hook is `curious` or `mystery`, the payoff `triumphant` or `calm`,
   the closing hook `mystery` or `curious`, and the comment prompt `upbeat` (the outro plays `upbeat` too); put
   a `silent` beat before or on one punchline and set a mood again right after it; do not change mood faster than every 10 s except for a
   deliberate joke. Every mood is balanced to the same loudness and the voice always ducks the music, so a mood changes the feeling, not the volume.
4. **Sound effects** on real beats only (`cue(t, 'pop')`, `ding`, `thud`, `whoosh`...), one or two a sentence at most, and a `drum` for a build.

## Pacing

- A **new picture or a clear beat at least every 6 to 12 seconds**. A shot of 20 s or more is a warning in `build.py check`.
- About **one shot per sentence or two**, so roughly 40 to 70 shots in 7 minutes. Reuse a set with a different pose and framing
  rather than building a new set every time, but change the set when the idea changes.
- A joke every 10 to 15 seconds, in the beans' faces and the last line of a chapter. A running gag that returns.
- Open every chapter with a clear signal (a bean walking in with a label shape: "1", "Bug 2", "Chapter 3") so a viewer who scrubs
  knows where they are. `bigWord(text, cx, y, size, fill, seed)` is available for a short title card.
- Close every chapter with a one-line takeaway, then a quick beat to reset. Vary the rhythm: a fast montage after a slow explanation.
- Hold a face on the punchline for at least 6 drawings (0.5 s).

## Chapters

- 5 to 9 chapters of 45 to 90 s. Hook (the paradox only), the idea in three beats, the payoff, the callback, the closing hook (in the last
  chapter). No recap chapter and no summary of earlier chapters anywhere.

## The ending (every long video)

1. **The callback**, one or two sentences back to the opening image, right after the last chapter's new payoff (practical, or the
   wildest escalation; never a recap), on a `cut` or `smear`.
2. **The closing hook**, 2 or 3 sentences, 10 to 15 s: the question the video leaves open (or the next idea), "that's a ... for another
   day", and a comment prompt the viewer can answer in a few words. Give it its own shots and a new set; it is a beat, not a footnote.
3. **The last shot**: `tr: 'iris'` on the speaker's face, a held loop to `VO_END()`.
4. **The channel outro** (automatic, about 14.8 s): voiced thanks, like, share, subscribe, then an end-screen layout held about 6 s.
   Its words go in the `.srt`. On the YouTube sheet, the end-screen elements start when it says "your next video is right over here".
- Titles are **3 to 5 words that promise what the section gives**, in the channel voice (yt-chapters).
- `chapters.json` lists each chapter's opening sentence; `build.py chapters` turns them into YouTube timestamps from the real word
  times: `0:00` first, at least three, each at least ten seconds, in order.

## 16:9 thumbnails (1280 x 720)

- Same subject test and click test as a Short, but the words follow `line-boil-thumbnail-long`: 2 to 4 big words that share at most
  one noun with the title and add the stakes or the twist (a 16:9 thumbnail always sits next to its title, so repeating it wastes it). The words go in the upper left or the left third; faces in the middle
  and the right.
- The **bottom-right corner is hidden by the duration badge**: keep nothing important in the bottom 15% of the right 20%.
- It is shown very small next to other videos (about 246 px wide), so one big object, one big face, a few big words.
- The renderer draws at 1920x1080 and publishes 1280x720 under YouTube's 2 MB limit; `build.py thumb` warns if it is larger.
  There is no `gridSafe` for 16:9.

## Example

`engine/example-wide/` is a complete three-chapter video: `script.json`, `chapters.json`, `web/cast.js`, `web/shots/ch01.js`, `ch02.js`,
`ch03.js`. `build.py new <project> --wide --example` copies it, and `build.py new <project> --wide` puts `cast.example.js` and
`shots.example.js` in `web/` as a reference.
