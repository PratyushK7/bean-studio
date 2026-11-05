---
name: line-boil-wide
description: Makes a long, narrated, funny explainer video (16:9, 1920x1080, 4 to 15 minutes, MP4) in the channel's hand-drawn cartoon style with line boil, told by a cast of different beans (the channel is The Bean With Bad Ideas). It is the long-form sibling of the line-boil skill and uses the same engine, characters, props and sound, but plans a chaptered, sourced script with a scored hook, a scene and music plan that changes with the script, one shots file per chapter, YouTube chapters timed from the real voiceover, closed captions (no burned-in subtitles, the long-form standard) and a 1280x720 thumbnail. Any subject that teaches something works, concrete or abstract. Use this whenever the user asks for a long video, a long-form video, a landscape or 16:9 video, an episode, a "6 to 12 minute" explainer, or any video over 60 seconds in this style, including when the Bean Studio Topics tab or Agent tab asks for one. For Shorts (9:16, up to 60 seconds) use line-boil instead.
---

# line-boil-wide

A topic in, a finished `<project>/<project>.mp4` (1920x1080) plus its `.srt`, `-chapters.txt`, `-thumbnail.png` (1280x720) and
`-youtube.txt` out. It is **the same engine as line-boil**, in a 16:9 format. Read these first, because everything in them still applies
and this file only adds what is different for a long video:

- `~/.claude/skills/line-boil/SKILL.md` (workflow, voice, ending, sound)
- `~/.claude/skills/line-boil/references/api.md` and `style.md` (characters, props, acting, **"A cast of beans"**)
- `~/.claude/youtube/voice.md` (the channel voice)
- `references/wide.md` in this skill (staging for 16:9, pacing, chapters, **the scene and sound plan**, cost control)

The worked example is `engine/example-wide` (three chapters, ten shots, a chapter per file). Read its `web/cast.js` and
`web/shots/ch01.js` before writing your first shots.

```
ENGINE="$HOME/.claude/skills/line-boil/engine"          # the same engine; a project is "wide" when it has project.json
python "$ENGINE/build.py" new      <project> --wide        # project folder with web/shots/ and chapters.json
python "$ENGINE/build.py" voice    <project> --target 420  # Kokoro voiceover (any length), word times, and whether the length hits the target
python "$ENGINE/build.py" chapters <project>               # YouTube chapters from chapters.json + the real word times -> <project>-chapters.txt
python "$ENGINE/build.py" check    <project>               # shot list; fails if there are no shots; warns about shots over 20 s
python "$ENGINE/build.py" stills   <project> 5,40,95,...   # stills + ONE contact sheet (stills/sheet.jpg)
python "$ENGINE/build.py" video    <project>               # render + sound + mux + wide outro -> <project>.mp4, <project>.srt
python "$ENGINE/build.py" thumb    <project>               # web/thumb.js -> <project>-thumbnail.png (1280x720) + stills/thumb-crops.png
python "$ENGINE/build.py" sheet    <project>               # contact sheet of the finished video
```
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
   metaphor (a bean) and a one-line takeaway; the video ends on a callback to its opening image.
2. **Hook, with yt-script.** The first 15 seconds do three jobs or the video leaks: confirm the click the title promised, open a
   question the viewer cannot close, and prove the payoff exists. Write **five** candidate first lines (against the 21 formulas in
   `~/.claude/skills/yt-script/hooks.json`), put them one per line in `<project>-hooks.txt`, run
   `PYTHONUTF8=1 python ~/.claude/skills/yt-script/hookscore.py <project>-hooks.txt`, keep the top two and use the winner (append the scored panel to the same file so the user can see the choice).
   The score separates deliberately weak hooks from real ones well and a creator's own hits from misses barely at all: a low score is a reason to look again, not a verdict. Then 0:15 to 0:45 is **the turn**: say what the video will do in one
   sentence and start doing it. **No channel intro, no "before we get started", no subscribe pitch** (the outro is the channel's one ask;
   do not add another). Deliver the payoff the hook promised explicitly, and end on the callback.
3. **Sources.** Long videos live or die on being right. Use the research brief if one is given (follow its "do not claim" list; it
   overrides your assumptions). Verify every figure in a primary source (the paper, the review, the agency page) with web searches.
   Hedge what is contested and drop what you cannot verify. Never invent a number. Write `<project>-sources.md`: a table of claim,
   link, and how far you checked (full text / abstract only / secondary report).
4. **Script and chapters.** `script.json`, one sentence per entry (this is also how the voice is cut, so keep each sentence to about 25
   words or fewer), written chapter by chapter in the channel voice: dry and calm, funny in the pictures and the last line of each
   chapter, never hype. Then `chapters.json`: `[{"title": "...", "line": N}, ...]`, N = the index of the sentence that opens the
   chapter (the first is 0). Titles follow yt-chapters: **3 to 5 words that promise what the section gives** ("Why the sky is blue"), not
   topic words; a section you cannot name in five words is two sections or filler. At least 3 chapters, each at least 10 seconds long.
5. **Project and voice.** `build.py new <project> --wide`, write `script.json` and `chapters.json`, then
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
   beat at least every 6 to 12 seconds, 2 to 4 beans a shot. **No burned-in captions** (below). The last shot has `tr: 'iris'` and a held
   loop to `VO_END()`, as in a Short.
8. **Check.** `build.py check` must list the shots with no `[error]`; for a long video it also warns when there is no `musicMood` or only
   one. `build.py stills <project> t1,t2,...` with 2 or 3 times per chapter writes one `stills/sheet.jpg`: read that one image, not every
   still. Look for overlaps, off-frame characters, expressions that don't match the line, a chapter that looks like the one before it.
9. **Build.** `build.py video <project>`, then `build.py sheet <project>` and look at the sheet once. Then, as a cross-check of your chapters,
   `python ~/.claude/skills/yt-chapters/chapters.py <project>.srt --target <number of chapters>`: if its boundaries are far from yours,
   ask whether one of your chapters is really two sections.
10. **Thumbnail.** 16:9, 1280x720, `web/thumb.js`, same rules as line-boil's step 9 (subject test, text test, at most 3 words, none
    repeated from the title) plus the 16:9 ones in `references/wide.md`. `build.py thumb <project>` writes the PNG and
    `stills/thumb-crops.png` (full, the small suggested-video size, and the corner the duration badge hides). Check that preview.
11. **YouTube sheet.** `<project>-youtube.txt` following `~/.claude/skills/line-boil/references/youtube.md`, for a long video: no
    `#shorts`; the title linted with **yt-package**'s `title.py` against the thumbnail words; the description written with **yt-seo** (first two
    lines hold the target search queries, then the chapters from `<project>-chapters.txt`, then 6 to 8 sources from `<project>-sources.md`);
    tags; a pinned comment; the settings checklist.
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
