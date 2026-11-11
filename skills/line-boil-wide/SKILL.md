---
name: line-boil-wide
description: Makes a long, narrated, funny explainer video (16:9, 1920x1080, 4 to 15 minutes, MP4) in the channel's hand-drawn cartoon style with line boil, told by a cast of different beans (the channel is The Bean With Bad Ideas). It is the long-form sibling of the line-boil skill and uses the same engine, characters, props and sound, but plans a chaptered, sourced script with a scored hook, a scene and music plan that changes with the script, one shots file per chapter, YouTube chapters timed from the real voiceover, closed captions (no burned-in subtitles, the long-form standard) and a 1280x720 thumbnail. Any subject that teaches something works, concrete or abstract. Use this whenever the user asks for a long video, a long-form video, a landscape or 16:9 video, an episode, a "6 to 12 minute" explainer, or any video over 60 seconds in this style, including when the Bean Studio Topics tab or Agent tab asks for one. For Shorts (9:16, up to 60 seconds) use line-boil instead.
---

# line-boil-wide

A topic in, a finished `<project>/<project>.mp4` (1920x1080) plus its `.srt`, `-chapters.txt`, `-thumbnail.png` (1280x720) and
`-youtube.txt` out. It is **the same engine as line-boil**, in a 16:9 format. Read these first, because everything in them still applies
and this file only adds what is different for a long video:

- `~/.claude/skills/line-boil/SKILL.md` (workflow, voice, ending, sound)
- `~/.claude/skills/line-boil/references/api.md` and `style.md` (characters, props, acting, **"A cast of beans"**, **"Mindful details"**)
- `~/.claude/youtube/voice.md` (the channel voice)
- `references/wide.md` in this skill (staging for 16:9, pacing, chapters, **the scene and sound plan**, cost control)

The worked example is `engine/example-wide` (three chapters, ten shots, a chapter per file). Read its `web/cast.js` and
`web/shots/ch01.js` before writing your first shots.

```
python ~/.claude/skills/line-boil/engine/build.py new      <project> --wide [--theme noir]   # project folder with web/shots/ and chapters.json
python ~/.claude/skills/line-boil/engine/build.py voice    <project> --target 420  # Kokoro voiceover (any length), word times, and whether the length hits the target
python ~/.claude/skills/line-boil/engine/build.py voice    <project> --append      # voice only sentences added at the end; every earlier word time is kept
python ~/.claude/skills/line-boil/engine/build.py chapters <project>               # YouTube chapters from chapters.json + the real word times -> <project>-chapters.txt
python ~/.claude/skills/line-boil/engine/build.py check    <project>               # shot list; fails if there are no shots; warns about shots over 20 s
python ~/.claude/skills/line-boil/engine/build.py stills   <project> 5,40,95,...   # stills + ONE contact sheet (stills/sheet.jpg)
python ~/.claude/skills/line-boil/engine/build.py video    <project>               # render + sound + mux + wide outro -> <project>.mp4, <project>.srt
python ~/.claude/skills/line-boil/engine/build.py thumb    <project>               # web/thumb.js -> <project>-thumbnail.png (1280x720) + stills/thumb-crops.png
python ~/.claude/skills/line-boil/engine/build.py sheet    <project>               # contact sheet of the finished video
```
**Running commands.** Start every command with `python` and nothing before it: no `ENGINE=...` line or `&&`, no `cd`, no pipe, no `;`, no PowerShell, no `$ENGINE`. A command that starts any other way needs the user's approval, and an unattended run (Bean Studio) stops dead there. Pass the project as a bare name and run each command alone, e.g. `python ~/.claude/skills/line-boil/engine/build.py voice <project>`.
A 7-minute video renders in about 2.5 minutes on the user's computer (it is free; only you, the agent, use Claude). Projects live in
`C:\Users\praty\youtube\line-boil\<project>` like Shorts.

## The yt-* skills this uses (read each SKILL.md when its step comes up)

| Step | Skill | What you take from it |
|---|---|---|
| Hook and script shape | **yt-script** (`hooks.json`, `hookscore.py`) | five hooks scored, keep the best two; the first 15 seconds; the turn; no channel intro |
| Chapters | **yt-chapters** (`chapters.py`) | the three rules, 3 to 5 word titles that promise the section, a cross-check of your boundaries |
| Title and thumbnail words | **yt-package** (`title.py`) | the title linted as one pairing with the thumbnail |
| Description, tags, queries | **yt-seo** | the first two lines hold the queries; the query test |
| Spin-off Shorts | **yt-shorts** | which spans survive alone, a new scored first line, a loop point |

## Steps

1. **Length and shape.** The user gives minutes (the Bean Studio prompt says `TARGET LENGTH: N seconds`). The voice reads about 3.1 words
   a second, so 7 minutes is about 1,300 words. Plan 5 to 9 **chapters** of 45 to 90 seconds. Every chapter has one idea, one
   metaphor (a bean) and a one-line takeaway; the video ends on a callback to its opening image, never on a recap.
2. **Hook, with yt-script.** The first 15 seconds do three jobs or the video leaks: confirm the click the title promised, open a
   question the viewer cannot close, and prove the payoff exists. Write **five** candidate first lines (against the 21 formulas in
   `~/.claude/skills/yt-script/hooks.json`), put them one per line in `<project>-hooks.txt`, run
   `PYTHONUTF8=1 python ~/.claude/skills/yt-script/hookscore.py <project>-hooks.txt`, keep the top two and use the winner (append the scored panel to the same file so the user can see the choice).
   The score separates deliberately weak hooks from real ones well and a creator's own hits from misses barely at all (it rates most explainer hooks WEAK because it is tuned to creator advice): a low score is a reason to look again, not a verdict, so compare the five and choose by judgment.
   **The paradox, not the answer.** The first 30 seconds set up the paradox the viewer has lived (you drank a coffee at 3 p.m., felt
   fine, slept your usual hours, and still lost sleep) and then go straight into chapter 1. Never state the mechanism or the answer in
   the intro (the caffeine script gave it away at 0:19, "caffeine doesn't actually give you energy"), and never read out a table of
   contents: no "in this video", "we'll meet", "let's follow", "first ... then ... finally" (the caffeine roadmap at 0:29 is exactly
   where long videos leak before 0:40). **No channel intro, no "before we get started", no subscribe pitch** (the voiced outro asks for likes,
   shares and subscribes on every video; do not add another ask). **No recap.** The last chapter is
   the practical payoff or the wildest escalation (the caffeine video's 9-hour cutoff and its 6 p.m. pre-workout math), then the callback
   to the opening image in one or two sentences, then the closing hook. Never re-summarise the chapters ("So, how does caffeine steal
   your sleep? It never gave you energy... It sat in the mailboxes... Your liver cleared it slowly..."): the viewer just watched them, and
   a recap is where they leave. Then a **closing hook** of 2 or 3 sentences (10 to 15 s): one question the video leaves open or a tease of the next idea, a dry "that's a
   ... for another day", and a comment prompt the viewer can answer in a few words ("Until then, tell us in the comments: what time is
   your last coffee?"). Never end on the callback with nothing after it. Count the closing hook in the target length.
3. **Sources.** Long videos live or die on being right. Use the research brief if one is given (follow its "do not claim" list; it
   overrides your assumptions). Verify every figure in a primary source (the paper, the review, the agency page) with web searches.
   **Hedge inside the claim, never in a sentence of its own:** one word or phrase in the line that makes the claim ("about", "roughly", "typically", "can", "on average", "scientists think"). Never a standalone apology sentence about cup sizes, sample sizes, averages or "not a law": the caffeine script had four, each right after its best moment, and each one deflated it. The one exception is a real safety point for a group (pregnancy, a medication, a condition): ONE short line, once in the video, ideally with the channel's dry joke. Drop what you cannot verify. Never invent a number. Write `<project>-sources.md`: a table of claim,
   link, and how far you checked (full text / abstract only / secondary report).
4. **Script and chapters.** `script.json`, one sentence per entry (this is also how the voice is cut, so keep each sentence to about 25
   words or fewer), written chapter by chapter in the channel voice: dry and calm, funny in the pictures and the last line of each
   chapter, never hype. **Write it like a script people repeat:** a hook that names the belief everyone holds and breaks it (honestly:
   never say a popular idea is false when the evidence supports it, say "not quite" and give the real reason, and hedge inside
   the claim, see step 3), the second sentence deepening it rather than explaining, one drawable image per sentence, plain words, no padding (cut
   any line that carries no fact and no laugh). **Re-hook inside every chapter and at the middle of the video:** a catch, a scale jump
   or a strange consequence ("Here's the catch.") before the chapter's takeaway, so no stretch of more than about a minute is pure
   explanation. A joke or sight gag at least every 15 s. Long videos still end on the payback callback plus the closing hook below.
   Then `chapters.json`: `[{"title": "...", "line": N}, ...]`, N = the index of the sentence that opens the
   chapter (the first is 0). Titles follow yt-chapters: **3 to 5 words that promise what the section gives** ("Why the sky is blue"), not
   topic words; a section you cannot name in five words is two sections or filler. At least 3 chapters, each at least 10 seconds long.
5. **Project and voice.** Pick the genre and theme first (**Genre** in `~/.claude/skills/line-boil/SKILL.md`: a dark topic gets `--theme noir`, with deep sets, tense or mystery music and dry humour; a long video can move between moods by changing set, music and faces inside one theme). `build.py new <project> --wide [--theme noir]`, write `script.json` and `chapters.json`, then
   `build.py voice <project> --target <seconds>`. Rewrite and repeat until it prints `TARGET ...: OK` (within 4 seconds). It prints the
   start of every sentence; use `at('a few words')` in shots for exact word times. Then `build.py chapters <project>`; fix
   `NOT VALID FOR YOUTUBE` before moving on.
6. **Scene and sound plan (required, before any shot).** A long video that keeps one sky and one tune for seven minutes is a screensaver.
   Write `<project>-plan.md`: one row per chapter with **the location/set, the time of day, the dominant background colour, which beans
   are on screen, the props, the music mood and why, the sound or silence beat, and the joke**. The picture and the music must follow
   what the script is saying at that moment (the full guide, with every set and mood, is in `references/wide.md`):
   - **Scenes change with the script.** A new place or colour at least every chapter. `setScene(name, t, opts)` gives `sunny`, `night`,
     `room`, `street`, `stage`, `desk`, `space` and `blank` (flat colour for a diagram); build a story-specific place (a theatre box
     office, a gym, a lab) from `band`, `ground`, `shape` and the props when no set fits. Two neighbouring chapters never share both set and colour.
   - **Music changes with the feeling.** `musicMood(t, mood)` at every chapter start and at every turn in the feeling: `curious`,
     `playful`, `upbeat`, `calm`, `serious`, `tense`, `mystery`, `triumphant`, `silent`. At least four different moods in a 7-minute video;
     `silent` for a punchline or a pause, then a mood again after it. The moods are matched in loudness, and the voice always ducks them.
   - **Sound effects** (`cue(t, kind)`) only on the real beats, one or two a sentence at most.
7. **Shots, one file per chapter.** Write `web/shots/ch01.js`, `ch02.js`, ... (zero-padded; they load in name order after
   `web/shots.js`, if any; put shared helpers in `cast.js`). Do **one chapter at a time**: write it, render its stills, look at the
   contact sheet, fix, move on. Rules specific to a long video are in `references/wide.md`: the world is **960 x 540**, a new picture or
   beat at least every 6 to 12 seconds, 2 to 4 beans a shot. **No burned-in captions** (below). The callback lands on a `smear`; the
   closing-hook shots follow, and the last of them has `tr: 'iris'` on the speaker's face and a held loop to `VO_END()`, as in a Short.
8. **Check.** `build.py check` must list the shots with no `[error]`; for a long video it also warns when there is no `musicMood` or only
   one. `build.py stills <project> t1,t2,...` with 2 or 3 times per chapter writes one `stills/sheet.jpg`: read that one image, not every
   still. Look for overlaps, off-frame characters, expressions that don't match the line, a chapter that looks like the one before it.
9. **Build.** `build.py video <project>`, then `build.py sheet <project>` and look at the sheet once. Then, as a cross-check of your chapters,
   `python ~/.claude/skills/yt-chapters/chapters.py <project>.srt --target <number of chapters>`: if its boundaries are far from yours,
   ask whether one of your chapters is really two sections.
10. **Thumbnail.** Only when the job says "make the thumbnail now" (the user chose it in Bean Studio): follow `~/.claude/skills/line-boil-thumbnail-long/SKILL.md` (16:9, 1280x720, `web/thumb.js`, `build.py thumb <project>`), and check `stills/thumb-crops.png` (full, the small suggested-video size, and the corner the duration badge hides). Otherwise (the default, or the prompt says "do NOT make a thumbnail"), skip this step: the user makes it afterwards with the **Better thumbnail** button (three ideas, one picked, then drawn), and the YouTube sheet's THUMBNAIL section says "Not made yet".
11. **YouTube sheet.** `<project>-youtube.txt` following `~/.claude/skills/line-boil/references/youtube.md`, for a long video: no
    `#shorts`; the title linted with **yt-package**'s `title.py` against the thumbnail words; the description written with **yt-seo** (first two
    lines hold the target search queries, then the chapters from `<project>-chapters.txt`, then 6 to 8 sources from `<project>-sources.md`);
    tags; a pinned comment that echoes the closing hook's comment prompt; the settings checklist, with the end-screen timing (the
    outro's last 7 s are drawn for a Video and a Subscribe element).
12. **Hand over** the folder, the real length, the chapters, the title and thumbnail text, the winning hook with its score, anything you
    could not verify, and "ship it, or change it?". Do not upload anything; the user does that from Bean Studio. (Spin-off Shorts are a
    separate button in Bean Studio that runs **yt-shorts** on the finished video.)

## Captions: none burned in (the long-form standard)

Long videos from the big explainer channels do not burn subtitles into the picture. Viewers who want text turn on YouTube's captions, which
**the `.srt` this tool writes is uploaded for**. Burned-in, word-by-word captions are a Shorts and Reels habit (vertical, sound-off, autoplay).
So in a long video `CAP.on` is false: put numbers, names and key words on screen as **label shapes held by a bean**, not as subtitles. Only
if the user asks for burned-in captions set `CAP.on = true` at the top of `cast.js` (they sit in the bottom band).

## Cost control

Your tokens are the only cost. Read this skill and the two line-boil references once. Write each chapter's shots in one Write call.
Look at contact sheets, not single stills. Do not re-read files you just wrote. If you are on a cheaper model, keep each chapter to
5 to 9 shots with simple scenes; the picture can be simple as long as the beans act, the scene changes and the joke lands.
