---
name: line-boil
description: Makes a narrated, funny explainer video in a hand-drawn cartoon style with line boil, where the topic's own things (animals, places, objects, body parts, machines, people) are drawn as themselves and act, with beans only where they help (the channel is The Bean With Bad Ideas). Any subject that helps people learn something works, concrete or abstract: science, health, money, tech, history, psychology, how things work, everyday life. Output is an MP4 (Shorts are 9:16, 1080x1920, 30 to 60 s) with word-timed captions, a YouTube .srt, a free local voiceover, synthesised cartoon sound effects and a thumbnail. Variable-width ink lines, flat red, blue and yellow fills on off-white paper, 24 fps animation on twos, anticipation and smear frames, faces that act. Use this whenever the user asks for a video, reel, short, TikTok or animated explainer in the line-boil or hand-drawn cartoon style, says "make a video about X" after seeing this style, asks for a "Pip and the Star" style animation, or wants any topic explained as a cartoon, even if they don't name the style.
---

# line-boil

**The script base (owner's rule, 2026-11-20):** read `~/.claude/skills/script-base/SKILL.md` before writing, rewriting or rating the narration of any Short. Use it for: title first and the questions it raises, a 30-second hook that proves the click, points that rise in importance joined by open loops, somebody wanted, but, so, then, one call to action, and a read-aloud edit. Rate every script with its 10-point review (rewrite below 8/10). This skill adds what is specific to line-boil Shorts on top; where its structure rules conflict with script-base, script-base wins.

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
**Running commands.** Start every command with `python` and nothing before it: no `ENGINE=...` line or `&&`, no `cd`, no pipe, no `;`, no PowerShell, no `$ENGINE`. A command that starts any other way needs the user's approval, and an unattended run (Bean Studio) stops dead there. Pass the project as a bare name and run each command alone, e.g. `python ~/.claude/skills/line-boil/engine/build.py voice <project>`. **Never write scratch files** (no `pdftext.py`, no helper scripts in temp or `.claude` folders: those writes are refused in an unattended run). Run small helpers inline with `python -X utf8 -c "..."` (always `-X utf8`, never `-I`, which drops the UTF-8 setting and crashes on any non-ASCII text; never put `PYTHONUTF8=1` or any `VAR=` before `python`: that needs approval and stops the run). To read a PDF, try `fitz`, `PyPDF2` or `pdfminer` that way; if none is installed, use a text summary of the source instead and say so in `sources.md`.
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

## Genre: the mood of the topic decides the look
The style adapts. Before the script, name the topic's **genre** (one word: playful, curious, dark, eerie, nostalgic, calm, hype), because the genre
picks the theme, the sets, the music, the acting and the jokes. A topic like "What if we killed all the mosquitoes?" is *dark*: it must not look like
the bright default, with a sunny yellow room and a grinning bean. The voice, ink line and boil stay the same on every theme; that is what keeps it the channel.

| Genre (examples) | Theme | Sets and props | Music (`musicMood`) | Acting and jokes |
|---|---|---|---|---|
| **playful / curious** (most how-things-work, everyday life) | `classic` | `sunny`, `room`, `street`, `stage` | `curious`, `playful`, `upbeat` | big takes, bounce, a joke every 8 to 10 s |
| **dark / dread** (extinction, "what if we killed all X", crime, disasters, "the thing nobody warns you about") | `noir` | `night`, `space`, or a deep wall; empty ground; one lit object; a lot of INK background | `tense`, `mystery`, `serious`, and `silent` before the reveal | slow push-ins, `scared`/`worried`/`deadpan` faces, long holds, **dry** jokes (deadpan and understatement, never slapstick bounce), fewer bounces and sparkle sounds |
| **history / how it used to be** | `sepia` | `room`, `street`, `stage` with muted colours | `calm`, `mystery` | storyteller bean, wry |
| **calm / sleep / kindness** | `soft` | `sunny`, `room`, empty space | `calm` | slow, warm, gentle jokes |
| **money / hustle / contests / hype** | `hype` | `stage`, `desk`, `street` | `upbeat`, `playful`, `triumphant` | fast cuts, bold reactions |

How to apply it:
- **Pick one theme per video** and pass it at the start: `python ~/.claude/skills/line-boil/engine/build.py new <project> --theme noir` (themes: `classic`, `noir`, `sepia`, `soft`, `hype`).
  The theme swaps the five channel colours together and the sets use a deep background on a dark theme, so everything you draw keeps working: use `RED`, `BLUE`, `YEL`, `PAPER`, `INK` as always and never type a colour in.
  The thumbnail renders in the same theme, so it matches the video. To change the theme later, set `"theme"` in `project.json` and re-render.
- **A theme is a tone, not a licence to be grim or graphic.** A dark topic still teaches, stays honest, keeps the hook and the jokes, and does not show gore, violence on people or anything a young viewer should not see. Dark here means **dread and dry humour**: the quiet room, the one lit window, the bean who slowly understands.
- **Mixed topics:** use the theme of the *opening promise*. The mood can swing inside a video by changing the set, the music and the faces; the theme stays.
- **When unsure,** use `classic`: a wrong dark video is worse than a plain one.

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
   and draw it (see **Picture and cast**). Hard-to-draw words (numbers, names, jargon) get a prop, a label shape, a map or a
   scale comparison. The viewer should be able to repeat the point to a friend afterwards.
   **Write it like a script people repeat.** A strong Short has: (1) a hook that names the belief everyone holds and breaks it, or
   states a paradox the viewer has lived, in under 12 words, with a concrete image (a Monday meeting that lasts a year) and no
   throat-clearing; (2) sentence 2 that deepens it ("Same clock. So who's stealing your weekend?"); (3) a mechanism told through ONE
   drawable image per sentence, each sentence under 15 words, plain words, no jargon or hedged mush; (4) the re-hook; (5) the payoff
   in the viewer's own words ("you just stop counting"); (6) the payback joke. Read it aloud: if a line could be cut without losing a
   fact or a laugh, cut it. **Stay honest in the hook:** a contrarian hook must not contradict the evidence (do not say a popular
   saying is false if the research supports it; say "that's not quite it" and give the real reason), and anything uncertain is hedged
   ("scientists think"). hookscore.py rates most explainer hooks WEAK because it is tuned to creator advice, so use it to compare the
   five candidates and spot a formula, then choose by judgment (a Contrarian Flip, The Mistake or a paradox usually wins).
   **Funny.** The channel is dry-funny in every genre. Put a joke roughly every 8 to 10 seconds in a Short (10 to 15 in a long video), mostly in a character's reaction (the subject itself or a bean), a
   literal-minded image, or the last line, never in shouting. A running gag that comes back at the end is worth more than five
   one-offs. Funny never replaces correct: facts stay checked and honest.
   **Length.** A Short's length is variable: you decide it from the topic. The target counts the voiceover; a Short has no outro and ends 1.6 s after the last word (breath, iris close, black), so the voiceover is almost the whole video. Before writing, list the three things a viewer must leave knowing (the answer, why it is true, one surprising detail or number they can repeat), then write only the sentences that carry those: ONE core mechanism, no padding, and never cut a needed fact just to hit a number. That usually lands at 30 to 50 s of voiceover (about 95 to 155 words). Go up to 60 s only when every extra beat escalates (a bigger scale, a new consequence, as "What if you grew 1 cm every second?" did), never for more explanation. If the user names a duration (the Bean Studio Agent tab and Topics wizard pass it as "TARGET LENGTH: N seconds"), follow it instead. Kokoro reads about 3.1 words per second, so N seconds is about N x 3.1 words. Run `build.py voice <project> --target N` (N = the seconds you chose, or the user's) after writing; it prints `TARGET N s: OK`, or how many words to cut or add, and you repeat the read until it is within 4 s of the target. More than 60 s of voiceover is a long video (16:9, chapters): use the **line-boil-wide** skill instead, which runs on this same engine (`build.py new <project> --wide`).
2. **Facts.** Check every claim. If you can search, use reputable sources. Hedge contested ideas inside the claim ("scientists
   think", "about", "can"), never in a separate disclaimer sentence.
   Keep the simplification honest: simpler is fine, wrong is not. Verify every number in a primary source (the paper, the review, the
   agency page), never invent one, and drop what you cannot verify. Write `<project>-sources.md`: a table of claim, link, and how far you
   checked it (full text / abstract only / secondary report), plus a short "not claimed, on purpose" list. The YouTube sheet's Sources
   come from it. Then do the **script review** (**Quality review** below): score it, and rewrite only the weak lines, before the voice.
3. **Picture and cast: show what is said.** (Choose the genre and theme first: see **Genre** above.) The topic's own things are
   the stars, drawn as themselves: a video about dinosaurs shows dinosaurs, one about the heart shows a heart, one about Mexico shows
   Mexico's shape. A sentence that names a thing shows that thing, recognisable at phone size (see **Show what is said** in
   `references/style.md`). Beans are a tool, not the default: use one only where it helps, and never in place of a real thing the
   script names.
   - **When a bean helps:** the viewer's stand-in ("you"), a reactor who says what the audience feels, a sceptic, the host bean as
     narrator-in-frame, or an abstract idea with no look of its own (inflation, procrastination, a deadline) played as a costume bean.
   - **When it does not:** an animal, a place, an object, a body part, a machine, a person's job or a historical figure. Draw the real
     thing. If it should act, it gets a face with `face()` (the same eyes, brows and mouth as a bean: a scared T. rex, a smug moon).
   - **The mix:** most shots have the subject as the focus. A bean is the focus in at most about a third of the shots, and often
     it is a small reactor in a corner. Many shots need no character at all: a map, a cutaway, a scale comparison, a close-up.
   - **Draw new things.** Writing a drawing function in `web/cast.js` for this topic's subjects is the normal job, not a last resort:
     build each from `shape`, `line`, `tube` and `blobPts`, silhouette first, with the 2 or 3 features that make it recognisable
     (see "Drawing the subject" in `references/api.md`). Reuse the props, sets and actions in `references/api.md` wherever they fit.
   - **Characters, when you use them,** are different at a glance (shape, colour, accessory) and keep one colour per role. The red
     host bean (glasses, tuft, yellow scarf, lit cracked bulb) is optional.
4. **Show the plan.** Before animating, give the user the script with its review scores, plus the list of subjects and characters and a one-line visual per
   sentence (what is said, then what is shown). Wait for an OK unless they asked you to go straight through.
5. **Project and voice.** Run `build.py new <project>` (add `--theme noir` etc. for a non-classic genre; just the slug; it lands in `C:\Users\praty\youtube\line-boil\<project>`), write `script.json`, then run `build.py voice <project>`.
   It prints every word with its start time, grouped by sentence. Those times are your timeline.
6. **Shots.** Write `web/cast.js` (this topic's drawn subjects and any characters) and `web/shots.js`. Every shot passes the
   **picture test**: with the sound and captions off, a viewer could say which sentence it is. Vary the shot types (a wide scene, a close-up on the
   object, a map, a cutaway, a scale comparison, a reaction) and never use the same set and framing three shots in a row. No shot runs longer than about 4 s, so plan about one shot per 3 to 4 s of
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
8. **Build.** Run `build.py video <project>`, then `build.py sheet <project>` and look at the sheet once. Then do the **animation review** and the final score (**Quality review** below).
9. **Thumbnail.** Every Short gets one, at make time, rendered straight into the project folder. Follow `~/.claude/skills/line-boil-thumbnail-short/SKILL.md` (the original style: 2 to 4 words that name the topic, one big topic object, a face only when it helps, flat high-contrast background, and an accuracy test). It lands as `<project>/<project>-thumbnail.png`.
10. **YouTube sheet.** Write `<project>-youtube.txt` next to the MP4: the title (linted with `yt-package`'s
   `title.py`, with two alternates), the thumbnail text and brief, the description, tags, target search queries,
   a pinned comment and an upload-settings checklist, all in the channel voice from `~/.claude/youtube/voice.md`.
   Follow `references/youtube.md`, which brings in the `yt-package` and `yt-seo` rules. Do this for every new video.
11. **Hand over** the full path, `C:\Users\praty\youtube\line-boil\<project>\<project>.mp4`, plus the `.srt`,
   `<project>-thumbnail.png` and `<project>-youtube.txt` beside it, with the script, a short note on the subjects and characters, the winning hook with its
   score, the review's four scores and remaining issues, the sheet's title, thumbnail text and first two description lines, and anything you could not verify. End with: ship it, or
   change it?

## Quality review: score, then fix only what is weak

Twice per Short, before the voice (the script) and after the render (the animation), act as an independent YouTube Shorts editor who
did not write it. Write the review to `<project>-review.md` and put the scores in the hand-over. Never inflate a score, and never
change a line just to raise a number. The aim is a Short that is more entertaining, clearer and more memorable without breaking what already works.

**1. Score the script** after the fact-check and before `build.py voice`, so a rewrite costs no voice re-run. Give each dimension a
score out of 10 and quote the line you are judging next to it:

| Dimension | What 8 or more means |
|---|---|
| First-second hook | names a belief and breaks it, or a paradox the viewer has lived; under 12 words; a concrete image |
| Sentence 2 retention | deepens the question or raises the stakes; never explains, sets up or answers |
| Curiosity and intrigue | the main answer is held back until about halfway |
| Storytelling and clarity | one mechanism, one drawable image per sentence; a stranger could repeat the point |
| Re-hook effectiveness | a catch, a scale jump or a strange consequence about halfway |
| Humour and entertainment | a joke about every 8 to 10 s, on topic, dry, in the genre's style |
| Natural narration | reads aloud without a stumble; plain words; under 15 words a sentence |
| Pacing and concision | no line that carries neither a fact nor a laugh |
| Factual accuracy | every claim is in `<project>-sources.md`, hedged inside the claim |
| Ending and payoff | the payback flips or answers the hook; nothing tacked on after it |

The overall score is the mean, to one decimal. Whatever the mean, the script is not ready while the hook, sentence 2 or factual
accuracy is under 8.
Calibrate against the channel's own data, where three of four Shorts lost the most viewers at 4 to 8 s, on sentence 2:
- a sentence 2 that states a common belief or explains scores 5 at most
- an answer given before the halfway point caps curiosity at 5
- an ending that stops on a flat callback or adds a teaser caps the ending at 6
- one unverified number caps factual accuracy at 4

A first draft that scores 8 or more everywhere is unusual: before accepting that, re-read it as a viewer with a thumb over the swipe.

**2. Name the weaknesses.** List only the dimensions under 8. For each, quote the sentence, say exactly what is wrong, and label it
**writing** or **fact**. A fact problem is fixed from the sources (hedge it, correct it or drop the claim), never by rewording it to
sound safer.

**3. Rewrite only the weak lines.** Do one revision pass.
- Keep the strong hook, the jokes, the metaphors and the pictures, and keep the core idea and the length (the voice target still has to pass).
- Read the new lines aloud: they must sound natural, with no filler, no predictable explanation, and the answer still not given away early.
- Never rewrite the whole script to fix one line.

Then re-score and write both scores in the review.

**4. Review the animation** after `build.py video`. Use the sheet you look at in step 8 plus two stills: one at 0 s (the first frame)
and one just before the iris closes (the last picture). Read no other images. Score each out of 10:
- every shot shows what its sentence says, recognisably (a sentence about dinosaurs shows a dinosaur; a named place is its real shape)
- the topic's subject, not a stand-in bean, is the focus in most shots, and the shots vary (wide, close-up, map, cutaway, reaction)
- the faces act, fit the line, and are funny
- there is enough movement and variety: no two shots alike in a row, and something changes about every 2 s
- it is in sync: actions land on their words. Judge this from the `at()` anchors and `check`; stills cannot show sound, so say so rather than guess.
- the first frame grabs: mid-action, a face or the topic object, readable at feed size
- the last picture pays off: the hero's face on the payback line

Fix only the shots that are visibly weak, in at most one fix round and one re-render. Leave good animation alone.

**5. Final score.** In `<project>-review.md` and the hand-over, give:
- the original script score
- the revised script score
- the animation score (the mean of the seven)
- the final overall score (the mean of the revised script score and the animation score)
- the remaining issues, if any

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
