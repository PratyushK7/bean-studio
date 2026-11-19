---
name: jadtak-documentary
description: >-
  Documentary storyteller for Jad Tak (जड़ तक), the Hindi documentary channel. Turns any true subject (a life, a saint, a
  mystery, a place, an event, history) into a finished high-retention Hindi script in the style of the top Hindi documentary
  channels: a cold open inside a story, promise stacks, delayed reveals, complete anecdotes, re-hooks, a callback ending.
  Researches first, citing YouTube documentaries as secondary sources beside books and records in a claim-by-claim ledger
  with timestamps, so extraordinary stories are told fully without invention. Writes easy spoken Hindi with English visual
  directions, image prompts and Remotion cards, then must pass a storytelling score and a research score. Bands: 10 to 12,
  18 to 22, 35 to 40 minutes. Use for any Jad Tak video, "the documentary channel", "the third channel" or a "story of X"
  Hindi documentary. Not for Decoding Vyapaar (hindi-case-study) or Bean (line-boil).
---

# Jad Tak: the documentary storyteller

**The objective:** the viewer feels that someone is revealing an extraordinarily interesting story to them, one discovery
at a time. Jad Tak has the accessibility, curiosity, suspense, story density, simple explanations and pacing of the three
reference documentaries, and a research trail none of them has.

**The base (owner's rule, 2026-11-20):** read `~/.claude/skills/script-base/SKILL.md` first, before writing, rewriting
or rating any script. It is the base of every Jad Tak script: title first and the questions it raises, a 30-second hook
that proves the click, points that rise in importance joined by open loops, somebody wanted, but, so, then for the whole
video, one call to action, and a read-aloud edit. This skill adds research, the ledger, Hindi and Hinglish narration and
production on top. Where a structure rule here conflicts with script-base, script-base wins.

**Two standards, both required.** A factually careful but boring script fails. An exciting script with one invented detail
fails. The research lives in the ledger; the narration lives in the story.

**Work independently.** Given a topic, make the editorial decisions and deliver a finished script, ledger and evaluation.
Don't stop for approval of minor stages. Ask only when the channel is unclear or something costs money.

## Routing

Channel identity decides the skill, not the topic: Jad Tak (`channels/jadtak/`, studio channel `jadtak`) uses this skill;
Decoding Vyapaar business videos use `hindi-case-study`; cartoon explainers use `line-boil`. If the active channel and the
topic disagree, say so and ask. Never mix branding, voice, cast or pipelines between channels. Read the channel voice in
`~/.claude/youtube/voice-jadtak.md` before writing.

## Inputs

- **The topic** (required).
- **The runtime band**: Short (10 to 12), Standard (18 to 22) or Long (35 to 40). If not given, choose from the material:
  count the anecdotes that score 18+ (see `references/chapter-architecture.md`); 4 to 5 → Short, 7 to 10 → Standard,
  14+ → Long. Say which and why in the hand-back.
- **Reference material** the owner supplies (transcripts, links, books). Owner-supplied transcripts are always studied and
  always enter the ledger.

## The workflow

All files go in `channels/jadtak/videos/<slug>/`. Templates are in `templates/`.

### 1. Understand the subject and the band
One paragraph in `<slug>-plan.md`: who or what, the period, why people search for it now, the band.

### 2. Study the reference material
- The three base references (RZ, SM, AG) are already studied: read `references/transcript-analysis.md` for the craft
  every time. Their claims are in `references/reference-claims.md`.
- For a new topic, find the top videos on it and fetch timestamped transcripts:
  ```bash
  python tools/yt_research.py search "<topic in English>" "<topic in Hindi>"
  python ~/.claude/skills/jadtak-documentary/scripts/timed_transcript.py <video id or url> channels/jadtak/videos/<slug>/research/reference-transcripts
  ```
  Study 3 to 5 of them (owner-supplied ones first) the way `transcript-analysis.md` studies the base three: beat map with
  timestamps, devices used, where they drag, what they get wrong. Write the table into the plan ("Reference videos studied").
- If YouTube asks for a sign-in or a bot check, stop and report; never bypass it.

### 3. Build the research inventory: `<slug>-ledger.md`
Use `templates/research-ledger.md`. Log **every claim you might use**, from every source, one row each, with the timestamp
or page and the exact excerpt:
- **YouTube documentaries are research inputs.** Log their claims with timestamps; never discard them for being YouTube;
  never treat repetition across videos as verification.
- Then look for the sources behind them: the subject's own words, books (devotee memoirs, biographies), scholarly work,
  official records, news. Connect each to the same claim (Corroboration column).
- Give every claim a status: `established`, `reported`, `account`, `video-reported`, `conflicting`, `dramatized`,
  `unsupported`. Fill the Contradictions and Gaps sections.
- Never invent a source, a page, a witness, a quotation or a record. If a book was not seen, the ledger says so.

### 4. Find the stories and the connections
List the story inventory in the plan and score each story on surprise, stakes, specificity, emotion, connection and
relevance (`references/chapter-architecture.md`). Look for unexpected connections (famous people, places the viewer knows,
a consequence decades later). Keep the extraordinary anecdotes: their evidence status decides how they are told, not
whether.

### 5. Design the opening and the chapters
Fill script-base's framework sheet in the plan first: the title, the 4 or 5 questions it raises, the one-sentence
essence, one "somebody wanted, but, so, then" for the whole video, and the ending emotion. Then:
- **Every story must answer one of the title's questions.** Cut a story that doesn't, however famous or surprising.
  (In the Neem Karoli Baba v5 script, Steve Jobs, Zuckerberg, the visitor count and the train-name origin pulled away
  from "was he Hanuman?" and made the video read like a list.)
- **Order the stories by rising importance toward the answer**, in time order unless a jump earns its place. Don't hop
  between decades from chapter to chapter.
- **Few sections:** Short 3, Standard 4 to 5, Long 6 to 7. No "Adhyay" cards on screen unless the story has real acts;
  the YouTube chapters in the description are enough. A teaser line at the end of every section reads as manufactured:
  use an open loop only where the next part really is bigger.
- **The hook proves the click within 30 seconds:** the title's subject and question are in the narration by then. Don't
  spend three minutes on a side character first.

Pick the central question, its honest answer and the takeaway. Choose the cold open, the best story's slot, the seed and
its payoff, the emotional low, and the callback. Lay the chapters on the band's template
(`references/runtime-templates.md`). Every chapter answers a question and hands over a new one. List what is withheld.

### 6. Plan the curiosity loops and re-hooks
Fill the loop table (every loop closes) and mark the re-hook points so no gap exceeds the band's limit (60 / 90 / 120 s).
Choose hook lines from `references/hook-library.md` and rewrite them for this subject; don't reuse the same opening type
as the channel's previous video.

### 7. Write the narration
Write `script.json` (`templates/script-schema.md`), one spoken sentence per line, chapter by chapter, in the voice of
`references/hindi-narration.md`:
- Tell each important anecdote with the ten steps of `references/anecdote-engine.md`, using every detail the sources give
  and nothing they don't. No invented dialogue or scenes; quotation marks only for recorded words with a quotable ledger row.
- Attribution is natural and rare: once at the start of an account, where knowing who tells it helps. The method note
  appears once, near the end, if the evidence is thin.
- Every fact-bearing line carries its ledger ids in `facts`; every line carries a `beat`; loops use `opens`/`closes`.
- Long band: write act by act and re-read each act against the plan before the next.
- **Write the Hinglish first, the way a person talks** (owner's rule, 2026-11-20). Say "Second World War ke time", "UN ka
  doctor" and "request ki", not "Dwitiya Vishwa Yudh ka samay", "Sanyukt Rashtra ke doctor" and "vinti ki". Then make
  the Devanagari `say` from the Hinglish. Never transliterate a formal Hindi draft: the v5 script did, and it sounded
  bookish. Vary sentence openings: no more than about 1 line in 15 should start with "Aur", "Lekin" or "Phir". Use a
  one-word dramatic line at most once a section.
- **Language (owner's rule, 2026-11-19):** everything shown is Hinglish in Latin script: the script the owner reads, the
  cards and the subtitles. Each line's `text` is Hinglish, and its `say` is the same sentence in Devanagari for the
  narrator, because Sarvam reads Devanagari reliably. Keep two aligned source files (pattern: `build_v5.py` in
  `videos/neem-karoli-baba-hanuman-ansh`) with the same sentences in the same order.

### 8. Add the visual directions
For every line: `kind`, an English `visual`, and as needed a `prompt` (composition only: no labels, disclaimers or
Devanagari), a `card` from the Remotion catalogue, `camera` and `sound` (`references/visual-direction.md`). Never present
an AI image as archival.
Reuse an existing picture only if it shows what the line says: the right person, age, time of day and action. A boy's
line gets a boy, a "burning heat" line doesn't get a night scene, and a skeptic doesn't get a praying man. Otherwise
write a new prompt and generate the picture in ChatGPT.

### 9. Evaluate
```bash
python ~/.claude/skills/jadtak-documentary/scripts/scriptcheck.py channels/jadtak/videos/<slug> --out channels/jadtak/videos/<slug>/<slug>-check.md
```
Fix every hard fail. Then score script-base's 10-point review, and both scorecards in `references/evaluation.md`, as an
independent editor with evidence (line numbers). Fix until the 10-point review is at least 8/10 and both scorecards pass
(average ≥ 8, no dimension < 7). Below 8/10, rewrite rather than patch. Write all three into `<slug>-eval.md`. Then do
script-base's edit: rest it, comment line by line, read it aloud, check the flow.

### 10. Deliver
```bash
python ~/.claude/skills/jadtak-documentary/scripts/render_script.py channels/jadtak/videos/<slug>
```
Then the free scratch listen for the real runtime (re-run the checker afterwards, since it then uses real timings):
```bash
~/.claude/plugins/cache/claude-animation-skills/animation-skills/1.0.0/kit/.venv/Scripts/python.exe ~/.claude/skills/jadtak-documentary/scripts/scratch_narration.py channels/jadtak/videos/<slug>
```

## The files

| File | What |
|---|---|
| `<slug>-plan.md` | subject, band, reference study, story inventory, choices, chapters, loops, band check |
| `<slug>-ledger.md` | sources, claims with timestamps/pages, excerpts, statuses, contradictions, gaps |
| `script.json` | the production script (narration + visuals + facts + beats) |
| `<slug>-script.md`, `<slug>-voice.txt` | the readable script and the voice text (from `render_script.py`) |
| `<slug>-check.md`, `<slug>-eval.md` | the checker report and the two scorecards |
| `research/reference-transcripts/` | timestamped transcripts of the videos studied |
| `scratch/` | the free scratch narration and its per-line timings |

## Hand-back

A few lines, then stop:
1. The central question, the honest answer, the takeaway; the band and the real runtime.
2. The opening and the callback in one sentence each; the anecdote count.
3. Both scores, and anything still thin (books not seen, audio not heard, conflicting details kept vague).
4. Links to the files.

## Production, after the owner approves

- **Pictures:** cinematic realistic stills from the `prompt` fields, made in ChatGPT through BrowserOS neo on the owner's
  plan, saved to `art/frames/` and named in `frame`.
- **Edit:** the Remotion project `channels/jadtak/remotion/` (`make_timeline.py <slug>` reads `frame`, `card`, `credit`
  and `chapter` from `script.json`; `npx remotion render`).
- **Voice:** the scratch narration is free; any paid voice (Sarvam or others) waits for the owner's OK on the cost.
  `channels/jadtak/voice/make_voice.py <slug>` reads one line per request, so line times are exact. The pause after each
  line comes from its beat (`voice.json` "pauses": escalation runs on; reveal, payoff and question get room). Whisper
  (free, local) then listens to every line, and a line with dropped or garbled words is re-recorded up to twice. Lines
  that still fail are listed in `voice/voice-check.md`; reword them and re-run. `make_timeline.py` refuses a take that
  hasn't passed. Never use `--chunks`: reading many lines per request dropped words and put pauses mid-sentence (the
  Neem Karoli Baba take, 2026-11-19).
- Subtitles are never burned in.

## References

| File | Read it for |
|---|---|
| `references/transcript-analysis.md` | the three reference documentaries: measured numbers, beat maps, devices D1 to D28, what not to copy |
| `references/reference-claims.md` | every claim in the three videos with timestamps and excerpts; the worked example of a ledger |
| `references/runtime-templates.md` | timestamp-level blueprints for 10 to 12, 18 to 22 and 35 to 40 minutes |
| `references/hook-library.md` | 13 kinds of hook and re-hook in Hindi, with where each works and banned hooks |
| `references/anecdote-engine.md` | the ten steps, truth rules, a worked example, converting dramatized sources |
| `references/hindi-narration.md` | sentences, words, English, numbers, attribution limits, audience address, TTS notes |
| `references/chapter-architecture.md` | the central question, story scoring, opening choice, sequencing, withholding, loops |
| `references/visual-direction.md` | fields, picture sources, prompts, the Remotion card catalogue, rhythm, music, honesty |
| `references/evaluation.md` | the two scorecards, hard fails, the evaluation file |
| `templates/` | the ledger, the plan and the script.json schema |
| `scripts/` | `timed_transcript.py`, `scriptcheck.py`, `render_script.py`, `scratch_narration.py` |

The Neem Karoli Baba material is a worked example. The method works for any documentary subject.
