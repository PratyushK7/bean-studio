---
name: line-boil
description: Makes a narrated, funny explainer video in a hand-drawn cartoon style with line boil, told by a cast of different beans (the channel is The Bean With Bad Ideas). Any subject that helps people learn something works, concrete or abstract: science, health, money, tech, history, psychology, how things work, everyday life. Output is an MP4 (Shorts are 9:16, 1080x1920, 30 to 60 s) with word-timed captions, a YouTube .srt, a free local voiceover, synthesised cartoon sound effects and a thumbnail. Variable-width ink lines, flat red, blue and yellow fills on off-white paper, 24 fps animation on twos, anticipation and smear frames, faces that act. Use this whenever the user asks for a video, reel, short, TikTok or animated explainer in the line-boil or hand-drawn cartoon style, says "make a video about X" after seeing this style, asks for a "Pip and the Star" style animation, or wants any topic explained as a cartoon, even if they don't name the style.
---

# line-boil

A topic in, a finished `<project>/<project>.mp4` out. Every picture is drawn in code with an ink engine that makes
the whole frame boil. A worked example, "Why is the sky blue?", ships in `engine/example`. Its `web/shots.js` is
the best reference for how a reel is put together, so read it before writing your first shots.

```
python ~/.claude/skills/line-boil/engine/build.py new    <project>               # make a project folder
python ~/.claude/skills/line-boil/engine/build.py voice  <project>               # Kokoro voiceover + word times -> web/words.js
python ~/.claude/skills/line-boil/engine/build.py check  <project>               # load the page, list shots, show errors and warnings
python ~/.claude/skills/line-boil/engine/build.py stills <project> 1.2,4.5,9     # half-size stills to look at
python ~/.claude/skills/line-boil/engine/build.py video  <project>               # render + sound + mux -> <project>/<project>.mp4
python ~/.claude/skills/line-boil/engine/build.py sheet  <project>               # contact sheet of the finished video
python ~/.claude/skills/line-boil/engine/build.py thumb  <project>               # web/thumb.js -> <project>/<project>-thumbnail.png
```
**Running commands.** Start every command with `python` and nothing before it: no `ENGINE=...` line or `&&`, no `cd`, no pipe, no `;`, no PowerShell, no `$ENGINE`. A command that starts any other way needs the user's approval, and an unattended run (Bean Studio) stops dead there. Pass the project as a bare name and run each command alone, e.g. `python ~/.claude/skills/line-boil/engine/build.py voice <project>`.
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
- `<project>-hooks.txt`: the five candidate hooks with their hookscore panel and the choice (step 1).
- `<project>-sources.md`: every claim, its source and how far it was checked (step 2).
- `web/cast.js`: the characters (`makeChar`) and any topic props and set helpers.
- `web/shots.js`: the shots, timed to the voice with `at('word')`.
- `web/thumb.js`: the thumbnail, one still shot drawn with the same cast (see step 9).
- Generated, don't edit: `web/words.js`, `web/engine/`, `web/index.html`, `web/thumb.html`, `cues.json`, `audio/`.
- Written last, for upload: `<project>-thumbnail.png` (step 9) and `<project>-youtube.txt` (step 10, `references/youtube.md`).

The API is in `references/api.md`. Read it before writing cast or shots. The style rules, which are what makes
this look hand-animated and not just "drawn in code", are in `references/style.md`. Read that too.

## Steps

1. **Script.** Its length is decided by what this topic needs to teach, not by a fixed number (see **Length** below). Write one idea per sentence and make every sentence
   something you can *show*. Captions repeat the words, but the picture still has to carry the meaning on its own. The shape:
   a hook in the first sentence (a question, a surprise or a "you've seen this"), then the mechanism in 2 or 3 escalating beats with a
   **re-hook about halfway** (a catch, a scale jump or a strange consequence that the first beat creates: "Here's the catch.", "Which
   should kill you. It doesn't."), then a payoff that answers the hook, ideally calling back to the opening image, then a **closing
   hook**. In a **Short** the closing hook is a **payback**: the last line, usually a joke, flips or answers the opening line (the
   hook said "time flies when you're having fun" and the last line says "Want a longer weekend? Stare at the clock. It works great, and
   ruins everything."). Do not tack on an extra open question or a teaser for another video: it dilutes the ending and viewers feel
   it is filler. In a **long video** the closing hook is two or three sentences (the open question, "that's a ... for another day",
   and a comment prompt). Never stop dead on a flat callback. The script never asks for likes, shares or subscribes (a long
   video's voiced outro does that; a Short has none, see **Captions, ending and outro**).
   **Sentence 2 is where Shorts lose people.** The channel's biggest drops sit at 4 to 8 s, on a "common belief" or textbook line
   ("A big swarm sounds like it could do it.", "Sweat is almost pure water…") or on a line that gives the answer away ("But your gut
   doesn't work like that."). Sentence 2 raises the stakes or deepens the question: it never explains, never sets up and never answers.
   A common belief worth correcting goes inside the hook ("Everyone says swallowed gum stays in you for seven years.") and is broken by
   the re-hook, not at second 5. Do not state the answer before about the halfway point.
   **Hook, with yt-script:** write five candidate first sentences (the 21 formulas are in `~/.claude/skills/yt-script/hooks.json`), put
   them one per line in `<project>-hooks.txt` in the project folder, score them with
   `PYTHONUTF8=1 python ~/.claude/skills/yt-script/hookscore.py <project>-hooks.txt`, append the scored panel and a line naming the winner
   and the runner-up (with their scores and formulas) to the same file so the user can see the choice, and open on the best. A score is a reason to look
   again, not a verdict. The first 15 seconds confirm the title's promise, open a question the viewer can't close, and prove the payoff exists.
   Any subject is fair game, abstract ones included (inflation, interest, a vaccine, procrastination, a market, a
   deadline): do not avoid them, and do not flatten them into something merely concrete. Turn the idea into a *metaphor you can draw*
   and give it a bean to play it (see **Cast**). Hard-to-draw words (numbers, names, jargon) get a prop, a label shape or a bean
   standing in for them. The viewer should be able to repeat the point to a friend afterwards.
   **Write it like a script people repeat.** A strong Short has: (1) a hook that names the belief everyone holds and breaks it, or
   states a paradox the viewer has lived, in under 12 words, with a concrete image (a Monday meeting that lasts a year) and no
   throat-clearing; (2) sentence 2 that deepens it ("Same clock. So who's stealing your weekend?"); (3) a mechanism told through ONE
   drawable image per sentence, each sentence under 15 words, plain words, no jargon or hedged mush; (4) the re-hook; (5) the payoff
   in the viewer's own words ("you just stop counting"); (6) the payback joke. Read it aloud: if a line could be cut without losing a
   fact or a laugh, cut it. **Stay honest in the hook:** a contrarian hook must not contradict the evidence (do not say a popular
   saying is false if the research supports it; say "that's not quite it" and give the real reason), and anything uncertain is hedged
   ("scientists think"). hookscore.py rates most explainer hooks WEAK because it is tuned to creator advice, so use it to compare the
   five candidates and spot a formula, then choose by judgment (a Contrarian Flip, The Mistake or a paradox usually wins).
   **Funny.** The channel is dry-funny in every genre. Put a joke roughly every 8 to 10 seconds in a Short (10 to 15 in a long video), mostly in a bean's reaction, a
   literal-minded image, or the last line, never in shouting. A running gag that comes back at the end is worth more than five
   one-offs. Funny never replaces correct: facts stay checked and honest.
   **Length.** A Short's length is variable: you decide it from the topic. The target counts the voiceover; a Short has no outro and ends 1.6 s after the last word (breath, iris close, black), so the voiceover is almost the whole video. Before writing, list the three things a viewer must leave knowing (the answer, why it is true, one surprising detail or number they can repeat), then write only the sentences that carry those: ONE core mechanism, no padding, and never cut a needed fact just to hit a number. That usually lands at 30 to 50 s of voiceover (about 95 to 155 words). Go up to 60 s only when every extra beat escalates (a bigger scale, a new consequence, as "What if you grew 1 cm every second?" did), never for more explanation. If the user names a duration (the Bean Studio Agent tab and Topics wizard pass it as "TARGET LENGTH: N seconds"), follow it instead. Kokoro reads about 3.1 words per second, so N seconds is about N x 3.1 words. Run `build.py voice <project> --target N` (N = the seconds you chose, or the user's) after writing; it prints `TARGET N s: OK`, or how many words to cut or add, and you repeat the read until it is within 4 s of the target. More than 60 s of voiceover is a long video (16:9, chapters): use the **line-boil-wide** skill instead, which runs on this same engine (`build.py new <project> --wide`).
2. **Facts.** Check every claim. If you can search, use reputable sources. Hedge contested ideas ("scientists think").
   Keep the simplification honest: simpler is fine, wrong is not. Verify every number in a primary source (the paper, the review, the
   agency page), never invent one, and drop what you cannot verify. Write `<project>-sources.md`: a table of claim, link, and how far you
   checked it (full text / abstract only / secondary report), plus a short "not claimed, on purpose" list. The YouTube sheet's Sources
   come from it.
3. **Cast.** The channel is The Bean With Bad Ideas, so the cast is **beans**: use *different beans* to explain the topic, one
   bean per idea or role (the viewer, the thing being explained, the force pushing against it, the sceptic, the crowd).
   Make them different at thumbnail size: body shape (`bean`, `pear`, `tall`, `ball`, `box`, `wide`, `tiny`), colour (RED, BLUE,
   YEL, PAPER), accessory (hat, glasses, scarf, tuft) and a habit of expression. Two to four beans is the sweet spot; a crowd of
   `tiny` beans can stand for a quantity. Abstract ideas get a bean with a *costume that shows what it does*, for example
   Inflation as a big red bean that keeps swelling and shrinking everyone's coins, Interest as a tiny yellow bean that
   duplicates itself, a Virus as a spiky bean, Procrastination as a sleepy bean on a sofa. See "A cast of beans" and "Mindful details" in
   `references/style.md`. Props stay props. Pick from the shapes, accessories and expressions in `references/api.md` before
   inventing new drawing code. The red host bean (glasses, tuft, yellow scarf, lit cracked bulb) may appear in any video as the
   narrator-in-frame, but is not required.
4. **Show the plan.** Before animating, give the user the script plus a one-line cast list and a one-line visual per
   sentence. Wait for an OK unless they asked you to go straight through.
5. **Project and voice.** Run `build.py new <project>` (just the slug; it lands in `C:\Users\praty\youtube\line-boil\<project>`), write `script.json`, then run `build.py voice <project>`.
   It prints every word with its start time, grouped by sentence. Those times are your timeline.
6. **Shots.** Write `web/cast.js` and `web/shots.js`. No shot runs longer than about 4 s, so plan about one shot per 3 to 4 s of
   voice (10 to 14 for a 40 s Short): split a long explainer sentence into two shots (a wide set-up, then a close-up on the prop or the
   reaction), and inside a shot change something on screen with `at()` about every 2 s. Time every action to the word that motivates it with `at()`. If a word
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
9. **Thumbnail.** Every Short gets one, at make time, rendered straight into the project folder. Follow `~/.claude/skills/line-boil-thumbnail-short/SKILL.md` (the original style: 2 to 4 words that name the topic, one big topic object, a face only when it helps, flat high-contrast background, and an accuracy test). It lands as `<project>/<project>-thumbnail.png`.
10. **YouTube sheet.** Write `<project>-youtube.txt` next to the MP4: the title (linted with `yt-package`'s
   `title.py`, with two alternates), the thumbnail text and brief, the description, tags, target search queries,
   a pinned comment and an upload-settings checklist, all in the channel voice from `~/.claude/youtube/voice.md`.
   Follow `references/youtube.md`, which brings in the `yt-package` and `yt-seo` rules. Do this for every new video.
11. **Hand over** the full path, `C:\Users\praty\youtube\line-boil\<project>\<project>.mp4`, plus the `.srt`,
   `<project>-thumbnail.png` and `<project>-youtube.txt` beside it, with the script, a short note on the cast, the winning hook with its
   score, the sheet's title, thumbnail text and first two description lines, and anything you could not verify. End with: ship it, or
   change it?

## Captions, ending and outro

**Captions and subtitles.** Every video gets burned-in captions in the channel lettering, with the spoken word
lit yellow. They sit in the centre band (y 500, about 52% down), where the eye naturally rests and well clear of
the Shorts overlay at the bottom. Compose so no face sits in y 475 to 530. When a close-up or a centred face
needs that space, move that shot's captions with `cap: 690` (below the subject), `cap: 420` (into a gap) or
`cap: 'top'`, and never put them below y 720. `build.py video` also writes `<project>.srt` next to the MP4, for
uploading to YouTube as closed captions (Subtitles → Upload file → With timing). Check one still per shot for
captions touching anything important. Details are in "Captions" in `references/style.md`.

**A Short ends smoothly, never instantly.** It has no outro, so after the last word the engine holds the final pose 0.6 s, closes
the iris over 0.8 s and sits on black 0.2 s (`VO_END()`; a long video uses 1.0 / 1.0 / 0.3). The last shot is the **closing hook** and
must be `tr: 'iris'`, centred on the hero's face, with its action landed before the last word ends and a held loop (a wave or a bob)
running to `VO_END()`. When checking, render a still about 0.4 s after the last word: the pose should be settled and alive, not
mid-move. See "The ending breathes" in `references/style.md`.

`build.py video` appends the channel outro to **long videos only**, voiced in af_heart, and adds the outro's words to the `.srt`
(`engine/outro/outro.mp4`, the old Shorts outro, is kept but no longer appended):
- **Long videos:** `engine/outro-wide/outro-wide.mp4` (about 14.8 s). "Thanks for watching. If you learned something, give it a like
  and share it with a friend. And subscribe, so the next bad idea finds you. Your next video is right over here." LIKE, SHARE and
  SUBSCRIBE arrive on their words, then the frame turns into an end-screen layout (a drawn video frame on the right, SUBSCRIBE under the
  host) and holds about 6 s so YouTube's end-screen elements can sit on it (see `references/youtube.md`).

The script itself never says like, share or subscribe. Long videos end on the closing hook's `iris`, so the outro's opening iris
follows on cleanly. Pass `--no-outro` to leave it off a long video. To change the outro, edit `engine/outro-wide/script.json` and
`web/shots.js`, then voice and render it: `python ~/.claude/skills/line-boil/engine/build.py voice ~/.claude/skills/line-boil/engine/outro-wide --voice af_heart --hold 3` and
`python ~/.claude/skills/line-boil/engine/build.py video ~/.claude/skills/line-boil/engine/outro-wide --no-outro`.

## When something goes wrong

- `check` prints `[error] ... is not in the voiceover`: a word passed to `at()` was mistyped or the script changed.
  The lookup ignores case and punctuation, so `at("isn't")` works.
- If you change the script, re-run `voice`. Shots timed with `at()` follow the new take automatically.
- If you only add sentences at the END of `script.json` (a closing hook, a new last line), run `build.py voice <project> --append`:
  it voices just the new sentences and keeps the earlier audio and every earlier word time exactly, so nothing before them moves. It
  refuses if an earlier sentence was edited.
- To use the user's own recording, run `build.py voice <project> --file take.wav`, where the take reads the
  script exactly. Other Kokoro voices can be picked with `--voice am_michael`, `bf_emma` or `bm_george`, and
  `--speed 1.1` speeds the read up.
- `--no-music` on `video` drops the underscore.
