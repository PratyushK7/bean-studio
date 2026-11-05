# The YouTube upload sheet

Every finished video gets `<project>-youtube.txt` beside its MP4: everything the user pastes into YouTube Studio,
in upload order. It's built with the rules of the `yt-package` skill (title + thumbnail as one pairing) and the
`yt-seo` skill (description, tags, search queries). Read both skills' `SKILL.md` before writing the first sheet
in a session (`~/.claude/skills/yt-package`, `~/.claude/skills/yt-seo`).

## Before you write

1. Read `~/.claude/youtube/voice.md`, the channel's voice profile ("The Bean With Bad Ideas"). The sheet is
   in that voice: calm, dry, honest, no hype words, one or two emoji at most (🫘💡 are the channel's own).
2. Use only facts from the script and the sources you checked in step 2. Never invent a number or a source.

## How to fill it

- **Target queries.** Write the 3 searches this video should win, in the words a real person types
  ("how much blood does a mosquito drink"). The title and the first two description lines must contain
  the words of those queries. If they don't, fix the title.
- **Title.** Write 10, lint them all with the yt-package linter, keep the best:
  `python ~/.claude/skills/yt-package/title.py titles.txt --thumb "THUMB TEXT"` (write `titles.txt` to the
  scratchpad, not the project). Pick the top scorer that still sounds like the channel. Under 60 characters,
  subject in the first 40, a number where the script has an honest one. The channel's titles are the hook
  question ("How Many Balloons Would It Take to Lift You Into the Sky?"), so keep that shape when it lints well.
  List the runner-up two with their scores as alternates.
- **Thumbnail.** It's paired with the title. Use at most 3 words, none repeated from the title. Give it a brief:
  the character and expression (pick a real still from the video, give its time), the framing, and how the
  background keeps contrast at feed size (flat colour, so bold ink and one yellow word read).
  The picture must pass the **subject test** (cover the text: is the topic obvious from the object alone?) and the words the
  **text test** (cover the picture: do 3 words or fewer still point at the topic or its stakes?). Then render it (SKILL.md
  step 9): it lands as `<project>-thumbnail.png` in the project folder, next to the MP4.
- **Description.** The first two lines are all most people read and they're the search snippet: say what the
  video answers, in the query words. Then a blank line and the short answer with the real numbers, then
  "Sources:" with the URLs from the fact check, then 2 or 3 hashtags on the last line (`#shorts` first).
- **Tags.** Up to 15, used to disambiguate: the topic, spellings and plurals, the questions people type.
  No unrelated or trending tags.
- **Pinned comment.** One dry line that invites a reply, often the next "bad idea" ("What should we
  measure in mosquitoes next?").
- **Settings.** Fill in the checklist below. Leave anything that's the user's call marked as such.

No chapters: a Short is under 60 s, and YouTube shows no chapters on Shorts. For a video over 60 s, run the
`yt-chapters` rules and add a CHAPTERS section after the description.

## Format

Plain text, UTF-8, these headings in this order. Each pasteable block stands alone, with nothing extra
inside it, so the user can copy it straight in.

```
YOUTUBE UPLOAD SHEET: <project>
Video: <project>.mp4 (<length> s, 9:16 Short)    Captions: <project>.srt    Thumbnail: <project>-thumbnail.png

== TITLE ==
<the title>

Alternates:
- <title>  (score NN)
- <title>  (score NN)

== THUMBNAIL ==
File: <project>-thumbnail.png
Text: <1 to 3 words>
Still: <time> s, <what's in frame, the expression>
Brief: <framing, background, contrast>

== DESCRIPTION ==
<line 1>
<line 2>

<the short answer, 2 to 4 lines>

Sources:
- <url>
- <url>

#shorts #<topic> #<topic>

== TAGS ==
tag one, tag two, ...

== TARGET SEARCH QUERIES ==
1. ...
2. ...
3. ...

== PINNED COMMENT ==
<one line>

== SETTINGS ==
Audience: Not made for kids (the user's call; this is the usual choice for a general science Short)
Category: Education
Language / caption language: English
Subtitles: upload <project>.srt (Subtitles > Upload file > With timing)
Altered or synthetic content: No (an animated cartoon; the voice is TTS narration, not a real person)
Education fields (Studio only, the upload API can't set them): Type = Concept overview; Level = None; Exam, course or standard = None; Problems = empty
Visibility: <user's call>
```

Linting it isn't publishing it. The sheet is a draft the user copies. When you hand over, show the title,
thumbnail text and the first two description lines, and end with: **ship it, or change it?**
