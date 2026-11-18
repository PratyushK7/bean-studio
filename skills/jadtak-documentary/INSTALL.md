# Installing jadtak-documentary

## On this PC (already installed)

The live copy is `~/.claude/skills/jadtak-documentary/`; Claude Code loads it automatically. The repository mirror is
`skills/jadtak-documentary/` in the youtube repo, kept in step with:

```bash
python tools/sync_skills.py out    # live → repo, then commit and push
```

Bean Studio routes the Jad Tak channel (`jadtak`) to this skill (`app/server.py`, `"skill": "jadtak-documentary"`); "＋ New
video" on Jad Tak opens a Claude session that follows it.

## On another PC

```bash
git clone <the youtube repo> && cd youtube
python tools/sync_skills.py in     # repo → ~/.claude/skills (all channel skills, this one included)
```

Requirements:

| For | Needs |
|---|---|
| `scripts/timed_transcript.py` | Python 3.10+, `yt-dlp` on PATH |
| `scripts/scriptcheck.py`, `scripts/render_script.py` | Python 3.10+ (standard library only) |
| `scripts/scratch_narration.py` | the animation kit's Python (`kokoro_onnx`, `soundfile`, `numpy`) and `ffmpeg` |
| the edit | `channels/jadtak/remotion/` with `npm install` (Remotion 4) |

## Use

Say "make a Jad Tak documentary on <topic>" (optionally "standard length" or "35 minutes"), or use Bean Studio's ＋ New video
on the Jad Tak channel. The skill delivers `<slug>-plan.md`, `<slug>-ledger.md`, `script.json`, `<slug>-script.md`,
`<slug>-check.md`, `<slug>-eval.md` and a free scratch listen in `channels/jadtak/videos/<slug>/`, then stops for the owner.

## Files

```
jadtak-documentary/
  SKILL.md                         the workflow (ten steps), rules, files, hand-back
  INSTALL.md                       this file
  references/
    transcript-analysis.md         the three reference documentaries, measured and mapped
    reference-claims.md            their claims with timestamps and excerpts (a worked ledger)
    runtime-templates.md           10 to 12 / 18 to 22 / 35 to 40 minute blueprints
    hook-library.md                hooks and re-hooks in Hindi, 13 kinds
    anecdote-engine.md             the ten-step anecdote and its truth rules
    hindi-narration.md             spoken-Hindi rules, attribution limits, CTA
    chapter-architecture.md        question, story scores, sequencing, withholding, loops
    visual-direction.md            fields, prompts, Remotion cards, rhythm, sound
    evaluation.md                  storytelling + research scorecards, hard fails
  templates/
    research-ledger.md             the ledger
    plan.md                        the story plan
    script-schema.md               script.json fields and examples
  scripts/
    timed_transcript.py            YouTube captions → [mm:ss] transcript
    scriptcheck.py                 mechanical checks (exit 1 on a hard fail)
    render_script.py               script.json → readable script + voice text
    scratch_narration.py           free Kokoro scratch listen + per-line timings
```
