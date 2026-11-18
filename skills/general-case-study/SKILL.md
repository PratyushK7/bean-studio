---
name: general-case-study
description: >-
  Gated documentary script process (research, then three duration options, then an outline, each waiting for the owner's
  approval). Jad Tak itself now uses jadtak-documentary: use this skill only for a channel whose "skill" setting is
  general-case-study, or when the owner explicitly asks for the gated general-case-study process. It
  researches a subject properly (the top five YouTube videos on it, primary sources, the chronology, the conflicts and
  turning points), offers three duration options sized to the real material (concise, standard, deep dive, up to 45 to 90+
  minutes when the subject supports it), agrees a story outline, and only then writes one coherent, sourced narrative in the
  channel's own language and voice. Never invents facts, events or quotations, and marks reconstructions. Use it for any
  documentary on a channel set to it. Jad Tak documentaries use jadtak-documentary; business and economics videos for
  Decoding Vyapaar use hindi-case-study; cartoon explainers use line-boil.
---

# The gated documentary script architect

> **Jad Tak now uses `jadtak-documentary`** (19 Nov 2026), which writes the finished script without approval gates and
> treats YouTube documentaries as cited research sources. This skill remains for a channel whose `skill` setting is
> `general-case-study`, or when the owner asks for the gated process by name. Where this file says "Jad Tak", read "the
> channel".

Jad Tak (जड़ तक, "to the root") is the third channel in Bean Studio (`jadtak`), after The Bean With Bad Ideas and Decoding
Vyapaar. It tells true stories from the beginning to the root of the matter.

**Core principle: one video is one central question, one storyline and one takeaway, told as a true story.** Research broadly,
select carefully, explain simply. A long video is the same story told with more depth, never a longer list of facts.

**The test of every script:** a first-time viewer follows the story without effort, wants to keep watching, and leaves knowing
something true and worth remembering.

**The process has three stops for the owner** (Gates 1 to 3). Never skip one, and never write the script before Gate 2.

```
0 routing → 1 research → Gate 1: three durations → 2 outline → Gate 2: outline approved → 3 script → editorial check → Gate 3
```

## 0. Which channel, which skill (before anything else)

Channel identity decides the skill, not the topic. Work out the channel in this order and stop at the first that answers:

1. **The owner said so** ("for Jad Tak", "for Decoding Vyapaar").
2. **The project folder.** `channels/<id>/videos/<slug>/` belongs to channel `<id>`: `channels/jadtak/` is Jad Tak,
   `channels/hindi/` is Decoding Vyapaar, and `line-boil/` is The Bean With Bad Ideas.
3. **The studio's configuration.** Bean Studio says the channel in a session's first message. Each channel in `config.json`
   (`channels.<id>`) has a `skill` (Jad Tak: `general-case-study`; Decoding Vyapaar: `hindi-case-study`; Bean: `line-boil`),
   a `language` and a `voice_file`. Use the skill the channel names.
4. **Nothing says.** Then the topic routes: the economics of a business, a company's rise or fall, or a businessman's story →
   `hindi-case-study` (Decoding Vyapaar); a cartoon explainer → `line-boil`; any other documentary, biography, history,
   mystery, faith, place or event → `general-case-study`. If it is still unclear, ask one question.

| Request | Skill |
|---|---|
| "Economics of owning a jewellery shop" | `hindi-case-study` (business economics, Decoding Vyapaar) |
| "Story of Neem Karoli Baba" | `general-case-study` (a life story, Jad Tak) |

**If the channel and the topic disagree** (for example Decoding Vyapaar is active and the topic is a saint's life), do not
switch skills quietly: say the topic belongs to the other channel, and ask. Never mix channels: no Decoding Vyapaar
branding, narrator persona, voice file, cast, music or visual bible in this channel's work, and none of this channel's in theirs.

**This channel's voice.** Read the channel's `language` and `voice_file` from its configuration (Jad Tak: Hindi,
`~/.claude/youtube/voice-jadtak.md`). Write in that language and
register (Hindi, Hinglish, English or another). If the voice file is missing, ask the owner three things before Gate 1 (the
language and register, the narrator's persona, the audience) and save the answers to the `voice_file` path, or to
`~/.claude/youtube/voice-<channel id>.md` and the channel's `voice_file` setting. Jad Tak's voice is its own: not
Decoding Vyapaar's narrator, cast or `voice-hindi.md`.

## 1. Research: `<slug>-research.md`

All files go in the video's project folder. The research comes before any opinion about length or structure.

### The top five videos on the subject

```bash
python tools/yt_research.py search "<subject>" "<subject in the channel's language>" "<closest angle>"   # candidates by views
python tools/yt_research.py fetch <project> <id> <id> <id> <id> <id>     # chapters, description, transcript, top comments
```

1. **Pick five** by relevance first, then views, engagement and a credible creator. Copy the table into the research file
   under **"Top videos on this subject"**: title, channel, views, upload date, duration, link, and the date numbers were read.
2. **Study each**: how it opens, what it explains, its claims, its story shape and length, where it drags, and what the
   comments ask, doubt or correct (a repeated question is a gift; a correction is a lead to check).
3. **Under "What they do well, what they miss"**: what is covered well, and what is missing, oversimplified, wrong or left
   unanswered. Write our angle in one line: what this video adds that a viewer of all five would still not know.

Never copy a script, a distinctive phrase, a joke, a scene or a creator's own narrative structure, and never rewrite their
transcripts into ours. Their transcripts stay in `research/competitors/`, never next to the draft. If a transcript, comments
or views are unavailable, write the limitation down; never fill it in. If YouTube asks for a sign-in or a bot check, stop and
say so.

### The subject itself

Research beyond the videos: background, the **chronology** (a dated timeline table), the people and what each wanted, the
conflicts, the turning points, the consequences, and the lesser-known details that are documented. Prefer primary sources:
letters, the subject's own writings and recorded words, official records, court documents, contemporary newspapers,
archives, then scholarly books, then reputable journalism. Note where a popular account traces back to one source.

### The facts table

Columns: **id** (F1, F2...), claim, date, source (link or document, with page) and status:
- **verified**: a primary record, or two independent reputable sources
- **reported**: one reputable source
- **estimate**: a calculated or approximate figure; say so in the line
- **disputed**: reliable sources disagree; give both sides in the line, or leave it out
- **legend**: a story told about the subject with no record (miracles, folklore, anecdotes repeated by followers); say it is
  told, by whom, or leave it out

A story or person video needs at least five independent sources; a deep dive needs many more, spread across every act. A
claim that appears only in other YouTube videos is not verified by repetition.

**Faith and living people.** For a spiritual figure, report what devotees and witnesses say as their accounts ("his
followers tell...", "according to <book>"), neither endorsed nor mocked. For living people, be fair, and stick to the record
on anything that could harm a reputation. Quotes are the person's documented words only, with the source.

End the research file with **"Not in this video"**: good findings that do not serve the central question.

## Gate 1: three duration options: `<slug>-durations.md`

After the research, **do not write the script.** Size three options from the actual material and its storytelling potential,
then stop and wait for the owner's choice.

| Option | What it is |
|---|---|
| **Concise** | The essential story, with the context it cannot lose |
| **Standard** | More context, the people developed, the meaningful details |
| **Deep dive** | The full documentary treatment: 45 to 90+ minutes, or longer, only when the subject genuinely supports it |

For each option give: the estimated runtime (words ÷ the language's speaking rate: about 150 a minute in English, 155 in
Hindi), what it covers, what it leaves out, and its trade-offs (retention, production cost, research still needed). Then
recommend one and say why. If the material supports only one or two honest lengths, say so: never stretch the deep dive with
filler or shrink the concise one past the story. A length the material cannot fill is not an option.

## 2. The outline: `<slug>-outline.md`

After the owner picks a duration, write a concise outline of the whole video, then stop and wait for approval (Gate 2):

- **The opening hook** (a familiar situation, a surprising true fact or a dated scene) and **the central question**.
- **The story flow**, chronological unless a different order clearly serves the story, in chapters. For a deep dive, group
  chapters into **acts** (usually three to five), each with its own question that the act answers and that hands over to the
  next.
- **Per chapter, one line each:** what happens, the one new thing the viewer learns, the conflict or turning point, the facts it
  rests on (ids), and how it moves the central question forward. A chapter that does not advance the story is cut or merged.
- **The reveals** and where they land, and the **emotional progression** (where the viewer is curious, worried, moved, surprised).
- **The payoff**, the conclusion and **the takeaway** in one sentence.
- Who the main people are (only those the story needs) and any **reconstruction** the script will use, marked as such.

Show the runtime per act and in total so the owner sees how the chosen duration is spent.

## 3. The script

Write only after Gate 2, following the approved outline. Changes to the structure go back to the owner first.

**How it should read:**
- One coherent narrative with natural progression. Every scene answers a question the last one raised.
- One idea at a time: explain the hard thing with something the viewer already knows, then move on.
- Natural spoken language in the channel's configured language and voice: short sentences written for the ear, the everyday
  word over the formal one, numbers rounded the way people say them.
- Clarity first, then story, emotional connection and accuracy. Feel comes from specific true details, not adjectives.
- Curiosity comes from real open questions, not artificial suspense. No "what happened next will shock you", no teasing a
  reveal that is not there, no cliffhanger every minute.
- No filler, no repetition, no recap unless a long video needs one after a break in time, and no subplot that does not
  serve the central question.
- **Never invent** a fact, event, date, number or quotation. A reconstruction ("imagine the room that night...") or an
  illustrative scenario is said as one, in the line itself. Disputed and legendary material is labelled as such where it is
  said.

**Long videos (over about 30 minutes):** write act by act. Each act opens with its question, closes with a turn that hands
over to the next, and gets one short re-orientation at its start (where we are in time, what we now know). Vary the rhythm
across acts: scene, explanation, testimony, consequence. Check after each act that it still serves the central question.

### The files

`script.json` in the project folder:

```json
{
  "title": "...", "alt_titles": ["...", "..."], "channel": "<channel id>", "language": "<from the channel config>",
  "duration_option": "standard", "question": "...", "answer": "...", "gain": "the one takeaway",
  "sources": ["https://...", "Book, author, year, page"],
  "lines": [
    {"text": "...", "visual": "...", "kind": "still", "act": "Act 1: ...", "chapter": "The Night the Ashram Emptied", "facts": ["F3"]},
    {"text": "...", "visual": "...", "kind": "archive", "tag": "reconstruction"}
  ]
}
```

- `text`: the narration exactly as spoken, one sentence a line. (If this channel's production uses the Decoding Vyapaar
  pipeline tools, which read `hi`, write the narration as `hi` too.)
- `visual`: what is on screen, specific enough to make: a place, people, an action, an object. Real people are shown from
  real photographs or archive where possible; a drawn or generated likeness of a real person is a reconstruction.
- `kind`: `still`, `archive` (real photo, document or footage), `card` (a date, map, number or quote on screen) or `map`.
- `act` (deep dives) and `chapter` on their first line; chapter titles name an event, 3 to 5 words.
- `facts`: research ids on every line that states a fact. `tag` (optional): `reveal`, `reversal`, `payoff`, `gain`,
  `reconstruction`, `legend`, `disputed`. Tag what is there; never add a line to have something to tag.

Then write **`<slug>-script.md`** for the owner: the title options, the central question, answer and takeaway, the chosen
duration and the real runtime, then each act and chapter with timestamps (at the language's rate), each line with its visual
and fact ids, and a sources list at the end.

## The editorial check: `<slug>-score.md`

Change roles: you are an independent senior editor who did not write this. Score 1 to 10 with one line of evidence each, then
fix only what scores under 8, and re-score:

| Question | What 8+ looks like |
|---|---|
| Clarity | A first-time viewer never needs to rewind; every name and term is introduced once, plainly |
| Story focus | One central question; every chapter moves it; nothing is there only because it was researched |
| Pacing | No stretch over about 90 seconds without something new (a turn, a reveal, a consequence); the length matches the chosen option without padding |
| Engagement | The opening earns the first minute; reveals land where the outline put them; the ending pays off the question |
| Accuracy | Every fact line has an id; disputed, legendary and estimated material is labelled in the line; every reconstruction is marked; no invented quote |
| Takeaway | The viewer can say in one sentence what they learned, and it is the `gain` |

Also check against the research: no wording, scene or structure lifted from the five competitor videos.

## Gate 3: the hand-back

Give the owner, in a few lines: the top five videos and our angle; the chosen duration and the real runtime; the central
question, answer and takeaway; anything disputed, legendary or reconstructed and how the script labels it; what research is
still thin; and the files. Then stop. Production (voice, pictures, edit) starts only when the owner approves the script and
only with this channel's own voice, look and tools. Jad Tak has no production setup yet: Decoding Vyapaar's pipeline
(its visual bible, graphics, render settings and voice cast) is not used for Jad Tak until Jad Tak has its own. Nothing paid
without the owner's OK on the cost.
