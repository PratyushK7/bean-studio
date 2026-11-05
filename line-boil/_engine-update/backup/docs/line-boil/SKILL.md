---
name: line-boil
description: Makes a narrated, funny explainer video in a hand-drawn cartoon style with line boil, told by a cast of different beans (the channel is The Bean With Bad Ideas). Any subject that helps people learn something works, concrete or abstract: science, health, money, tech, history, psychology, how things work, everyday life. Output is an MP4 (Shorts are 9:16, 1080x1920, 30 to 60 s) with word-timed captions, a YouTube .srt, a free local voiceover, synthesised cartoon sound effects and a thumbnail. Variable-width ink lines, flat red, blue and yellow fills on off-white paper, 24 fps animation on twos, anticipation and smear frames, faces that act. Use this whenever the user asks for a video, reel, short, TikTok or animated explainer in the line-boil or hand-drawn cartoon style, says "make a video about X" after seeing this style, asks for a "Pip and the Star" style animation, or wants any topic explained as a cartoon, even if they don't name the style.
---

# line-boil

A topic in, a finished `<project>/<project>.mp4` out. Every picture is drawn in code with an ink engine that makes
the whole frame boil. A worked example, "Why is the sky blue?", ships in `engine/example`. Its `web/shots.js` is
the best reference for how a reel is put together, so read it before writing your first shots.

```
ENGINE="<base directory of this skill>/engine"
python "$ENGINE/build.py" new    <project>               # make a project folder
python "$ENGINE/build.py" voice  <project>               # Kokoro voiceover + word times -> web/words.js
python "$ENGINE/build.py" check  <project>               # load the page, list shots, show errors and warnings
python "$ENGINE/build.py" stills <project> 1.2,4.5,9     # half-size stills to look at
python "$ENGINE/build.py" video  <project>               # render + sound + mux -> <project>/<project>.mp4
python "$ENGINE/build.py" sheet  <project>               # contact sheet of the finished video
python "$ENGINE/build.py" thumb  <project>               # web/thumb.js -> <project>/<project>-thumbnail.png
```
`build.py` finds the animation-skills kit for Playwright, the Kokoro voice and Parakeet word timing, and re-runs
itself under the kit's Python. If it reports the kit missing, tell the user to install the
`claude-animation-skills` plugin and run its `kit/setup.sh --voice` once. A full 40 s render takes well under a minute.

## Where videos go

Every project lives in **`C:\Users\praty\youtube\line-boil\<project>`**, and the finished video is
`C:\Users\praty\youtube\line-boil\<project>\<project>.mp4`. Everything the user uploads sits flat in that
folder, side by side: `<project>.mp4`, `<project>.srt`, `<project>-thumbnail.png` and `<project>-youtube.txt`.
Never put the thumbnail in a subfolder or a separate project. Give `build.py` just the project name, a short
lowercase slug of the topic like `cola-sweat` or `balloon-lift`: a name with no folder in it resolves to that
directory, from any working directory. Don't put projects anywhere else unless the user asks. (Setting the
`LINEBOIL_OUT` environment variable moves the default.)

## A project

- `script.json`: the voiceover, one sentence per entry.
- `web/cast.js`: the characters (`makeChar`) and any topic props and set helpers.
- `web/shots.js`: the shots, timed to the voice with `at('word')`.
- `web/thumb.js`: the thumbnail, one still shot drawn with the same cast (see step 9).
- Generated, don't edit: `web/words.js`, `web/engine/`, `web/index.html`, `web/thumb.html`, `cues.json`, `audio/`.
- Written last, for upload: `<project>-thumbnail.png` (step 9) and `<project>-youtube.txt` (step 10, `references/youtube.md`).

The API is in `references/api.md`. Read it before writing cast or shots. The style rules, which are what makes
this look hand-animated and not just "drawn in code", are in `references/style.md`. Read that too.

## Steps

1. **Script.** About 95 to 120 words, which comes to 32 to 42 s, unless the user gave a length (see **Length** below). Write one idea per sentence and make every sentence
   something you can *show*. Captions repeat the words, but the picture still has to carry the meaning on its own. The shape:
   a hook in the first sentence (a question, a surprise or a "you've seen this"), the common belief, a turn ("But..."),
   the mechanism in 2 or 3 escalating beats, then a payoff that answers the hook, ideally calling back to the
   opening image. **Hook, with yt-script:** write five candidate first sentences (the 21 formulas are in `~/.claude/skills/yt-script/hooks.json`),
   score them with `PYTHONUTF8=1 python ~/.claude/skills/yt-script/hookscore.py hooks.txt` (one per line), and open on the best. A score is a reason to look
   again, not a verdict. The first 15 seconds confirm the title's promise, open a question the viewer can't close, and prove the payoff exists.
   Any subject is fair game, abstract ones included (inflation, interest, a vaccine, procrastination, a market, a
   deadline): do not avoid them, and do not flatten them into something merely concrete. Turn the idea into a *metaphor you can draw*
   and give it a bean to play it (see **Cast**). Hard-to-draw words (numbers, names, jargon) get a prop, a label shape or a bean
   standing in for them. The viewer should be able to repeat the point to a friend afterwards.
   **Funny.** The channel is dry-funny in every genre. Put a joke roughly every 10 to 15 seconds, mostly in a bean's reaction, a
   literal-minded image, or the last line, never in shouting. A running gag that comes back at the end is worth more than five
   one-offs. Funny never replaces correct: facts stay checked and honest.
   **Length.** The default is 32 to 42 s. If the user names a duration (the Bean Studio Agent tab and Topics wizard pass it as
   "TARGET LENGTH: N seconds"), write to it: the Kokoro voice reads about 3.1 words a second, so N seconds is about N x 3.1
   words. Run `build.py voice <project> --target N` after writing; it prints `TARGET N s: OK`, or how many words to cut or add,
   and you repeat until the read is within 4 s of the target. Up to 60 s is a Short and this engine renders it as 9:16.
   Anything longer than 60 seconds is a long video (16:9, with chapters): use the **line-boil-wide** skill instead. It runs on this
   same engine (`build.py new <project> --wide`).
2. **Facts.** Check every claim. If you can search, use reputable sources. Hedge contested ideas ("scientists think").
   Keep the simplification honest: simpler is fine, wrong is not.
3. **Cast.** The channel is The Bean With Bad Ideas, so the cast is **beans**: use *different beans* to explain the topic, one
   bean per idea or role (the viewer, the thing being explained, the force pushing against it, the sceptic, the crowd).
   Make them different at thumbnail size: body shape (`bean`, `pear`, `tall`, `ball`, `box`, `wide`, `tiny`), colour (RED, BLUE,
   YEL, PAPER), accessory (hat, glasses, scarf, tuft) and a habit of expression. Two to four beans is the sweet spot; a crowd of
   `tiny` beans can stand for a quantity. Abstract ideas get a bean with a *costume that shows what it does*, for example
   Inflation as a big red bean that keeps swelling and shrinking everyone's coins, Interest as a tiny yellow bean that
   duplicates itself, a Virus as a spiky bean, Procrastination as a sleepy bean on a sofa. See "A cast of beans" in
   `references/style.md`. Props stay props. Pick from the shapes, accessories and expressions in `references/api.md` before
   inventing new drawing code. The red host bean (glasses, tuft, yellow scarf, lit cracked bulb) may appear in any video as the
   narrator-in-frame, but is not required.
4. **Show the plan.** Before animating, give the user the script plus a one-line cast list and a one-line visual per
   sentence. Wait for an OK unless they asked you to go straight through.
5. **Project and voice.** Run `build.py new <project>` (just the slug; it lands in `C:\Users\praty\youtube\line-boil\<project>`), write `script.json`, then run `build.py voice <project>`.
   It prints every word with its start time, grouped by sentence. Those times are your timeline.
6. **Shots.** Write `web/cast.js` and `web/shots.js`. Use about one shot per sentence (8 to 12 in all), with an
   explainer beat allowed to run longer. Time every action to the word that motivates it with `at()`. If a word
   occurs more than once, pass `nth` or use a longer phrase. `check` warns you when you didn't. Start the first
   shot mid-action on frame 1. Keep faces and key props between y 110 and 750 (world units) so the platforms' UI
   doesn't cover them.
7. **Check.** Run `build.py check`. It must print the shot list with no `[error]` and no lookup warnings. Then
   render stills at the busiest moment of each shot with `build.py stills`. It also writes `stills/sheet.jpg`, ONE image of
   them all: read that single sheet first (an image read costs real tokens, one sheet is far cheaper than ten stills) and open an
   individual still only for a shot that looks wrong. You're looking for:
   - characters off-frame or overlapping
   - expressions that don't match the line
   - a prop that hasn't appeared yet
   Fix what you see, then render stills again for anything you changed.
8. **Build.** Run `build.py video <project>`, then `build.py sheet <project>` and look at the sheet once.
9. **Thumbnail.** Every video gets one, rendered straight into the project folder. Settle the thumbnail text
   first (at most 3 words, none repeated from the title; see `references/youtube.md`), then write `web/thumb.js`:
   `CAP.on = false;` and a single `shot(0, { draw() {...} })` that poses the hero at the story's most extreme
   moment with a big expression (`fx: ['take']`, wide eyes), the key props around them, a flat high-contrast
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
   - **Text test.** Cover the picture. Do the words still point at the topic or its stakes, in at most 3 words, as a question,
     a number or a surprise, without repeating the title? Filler such as "NOPE" or "WOW" on its own fails; pair the reaction with
     the stakes ("STUCK INSIDE?"). Text that would fit any video fails.
   **Safe zone.** Profile grids crop the cover (Instagram shows a 3:4 centre crop of a 9:16 cover), so a headline at the very top is
   cut off. Draw the headline, subject and faces inside `gridSafe(() => { ... })` (it keeps them in y 155 to 830), the background
   outside it, and check `stills/thumb-crops.png`, which `build.py thumb` writes: nothing important may be cut in the 3:4 or the square.
   Then one bean reacting to the stakes, a flat high-contrast background and no empty areas. The first gum thumbnail ("NOPE" and
   two beans, no gum) failed both tests; `gum-seven-years/web/thumb.js` shows the fix and `cola-sweat/web/thumb.js` another.
10. **YouTube sheet.** Write `<project>-youtube.txt` next to the MP4: the title (linted with `yt-package`'s
   `title.py`, with two alternates), the thumbnail text and brief, the description, tags, target search queries,
   a pinned comment and an upload-settings checklist, all in the channel voice from `~/.claude/youtube/voice.md`.
   Follow `references/youtube.md`, which brings in the `yt-package` and `yt-seo` rules. Do this for every new video.
11. **Hand over** the full path, `C:\Users\praty\youtube\line-boil\<project>\<project>.mp4`, plus the `.srt`,
   `<project>-thumbnail.png` and `<project>-youtube.txt` beside it, with the script, a short note on the cast, and the sheet's title, thumbnail
   text and first two description lines. End with: ship it, or change it?

## Channel outro

**Captions and subtitles.** Every video gets burned-in captions in the channel lettering, with the spoken word
lit yellow. They sit in the centre band (y 500, about 52% down), where the eye naturally rests and well clear of
the Shorts overlay at the bottom. Compose so no face sits in y 475 to 530. When a close-up or a centred face
needs that space, move that shot's captions with `cap: 690` (below the subject), `cap: 420` (into a gap) or
`cap: 'top'`, and never put them below y 720. `build.py video` also writes `<project>.srt` next to the MP4, for
uploading to YouTube as closed captions (Subtitles → Upload file → With timing). Check one still per shot for
captions touching anything important. Details are in "Captions" in `references/style.md`.

**End smoothly, never instantly.** After the last word the engine holds the final pose for 1.0 s, closes the iris
over 1.0 s and sits on black for 0.3 s, all built into `VO_END()`. The last shot must be `tr: 'iris'`, centred
on the hero's face, with its payoff action landed before the last word ends and a held loop (a wave or a bob)
running to `VO_END()`. When checking, render a still about 0.5 s after the last word: the pose should be settled
and alive, not mid-move. See "The ending breathes" in `references/style.md`.

`build.py video` appends `engine/outro/outro.mp4` to every video: the 3.5 s "The Bean With Bad Ideas"
sign-off, where the bulb pops, the title appears, the SUBSCRIBE button drops and the iris closes. Videos end on the
`iris` transition, so the outro's opening iris follows on cleanly. Pass `--no-outro` to leave it off. To change
the outro, edit `engine/outro/web/shots.js` and re-render it with
`python build.py video "$ENGINE/outro" --no-music --no-outro`.

## When something goes wrong

- `check` prints `[error] ... is not in the voiceover`: a word passed to `at()` was mistyped or the script changed.
  The lookup ignores case and punctuation, so `at("isn't")` works.
- If you change the script, re-run `voice`. Shots timed with `at()` follow the new take automatically.
- To use the user's own recording, run `build.py voice <project> --file take.wav`, where the take reads the
  script exactly. Other Kokoro voices can be picked with `--voice am_michael`, `bf_emma` or `bm_george`, and
  `--speed 1.1` speeds the read up.
- `--no-music` on `video` drops the underscore.
