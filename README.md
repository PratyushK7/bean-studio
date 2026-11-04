# Bean Studio 🫘💡

The production desk for **The Bean With Bad Ideas**, a YouTube channel of hand-drawn line-boil cartoon
science Shorts. One local web page to build videos, check them, schedule uploads and ask the agent for help.

![Bean Studio](https://img.shields.io/badge/runs-localhost%20only-1982c4)

## Start it

Double-click **`start.bat`**. The first run creates `.venv` and installs everything (about a minute), then
the studio opens at **http://127.0.0.1:5173**. Close the window (or Ctrl+C) to stop it.

Needs: Python 3.10+, and for building videos the `line-boil` Claude Code skill plus the
`claude-animation-skills` kit. The Agent tab needs Claude Code (`claude` on your PATH).

## What the channel is

*The Bean With Bad Ideas* is a funny animated explainer channel about anything that helps people learn something (science, health,
money, tech, history, psychology, how things work, everyday life), told by a cast of **different beans**, one per idea or role
(abstract ideas get a costume bean). The name is a brand, not a limit. The line-boil skill, the topic scout and the voice profile
(`~/.claude/youtube/voice.md`) all follow this.

## What's in the studio

| Tab | What it does |
|---|---|
| **Videos** | Every project with its thumbnail, its live YouTube state (LIVE / SCHEDULED / PRIVATE) and a checklist (script, video, captions, thumbnail, upload sheet, uploaded). Open one to watch it, run the build steps (Voice → Check → Build video → Thumbnail), edit the script and upload sheet, and upload it to YouTube: pick any date and any time (15-minute steps, IST, with the US time shown) and **Upload + schedule**, or **⚡ Post now** to publish immediately. **🗑 Delete** removes a video's folder from the disk (not from YouTube). |
| **✨ Topics** | A **Shorts / Long videos** switch. Studies what is beating its own channel's median on other channels in your category (`topic_channels` in Settings; public data, no login; separate pools and medians for Shorts and for 4 to 40 minute videos), then has the agent adapt the best into **5 original ideas** (topic and format borrowed, never the script or title). Long-video ideas also carry chapters, a runtime, Shorts of yours they build on, and sources to check. **🎲 Re-roll** gives 5 new ones from sources not shown yet. **⭐ Researched picks** (`data/picks.json`, each with a brief) sit on top. Click an idea and answer a few questions (length, voice, pace, tone, cast, ending, music, outro, thumbnail text, notes). A Short is made end to end; a **long video** is prepared as a script package (script, sources table, chapters timed from the real voiceover, shot list, upload sheet) because the line-boil engine renders 9:16 only. |
| **Schedule** | What is really on YouTube (live, scheduled, private), read from the channel itself, plus the planner rows that are not on YouTube yet. Refreshes on open, every 5 minutes and after an upload. |
| **Analytics** | Pulls your numbers **straight from YouTube** (Data API + Analytics API, same Google sign-in as the uploader): views, engaged %, average % watched, view duration, likes, comments, shares, subscribers, the second where the retention curve falls hardest, and top countries. It refreshes itself every 6 hours (`analytics_sync_hours` in Settings) or on **Sync now**; slot and type are filled in automatically from the publish time and the planner, and your edits are kept. Per-slot and per-type averages sit underneath (⚠️ = under 5 videos). **Analyze & recommend** hands everything to the agent, which writes `reports/analysis-<date>.md` with what worked, what's noise and up to 3 decisions; it never edits the planner or videos. First time: **Connect YouTube** (see `tools/yt_upload.md`). |
| **Agent** | Type a request and Claude Code runs it in this folder with the line-boil and yt-* skills. A **Length** option (30 to 60 s, or 5 to 12 min) is passed to the skill as a target length, with the rule for hitting it (`build.py voice --target`). Quick buttons for a new Short, an upload sheet, a thumbnail, rebuilding an old Short, or an idea batch. |
| **Activity** | Live logs of everything running, with a Stop button. YouTube sign-in and upload status live here. |
| **Settings** | `config.json`: paths, posting slots, the agent command, the port, hidden folders. |

## Watching the agent, and what it costs

- **A video being made shows a progress bar** on its card in Videos: the percentage comes from the files the agent has really
  produced (script, voiceover, shots, stills, video, captions, thumbnail, sheet), plus the stage, the time so far and the agent's
  latest step in plain words ("Recording the voiceover", "Searching the web: ..."). **Watch every step live** opens the full feed in Activity.
- **Own window:** tick **🪟 Open in its own Claude window** in the wizard or the Agent tab (or set `agent_window` in Settings) and the
  agent runs as a normal interactive Claude Code session you can read and answer. The progress bar still works.
- **What uses Claude, and what doesn't:** the agent that writes the script, fact-checks, writes the drawing code and checks the pictures
  uses Claude. Everything else (voice, word timing, drawing and rendering the frames, ffmpeg, yt-dlp, YouTube's API) runs on your computer
  for free. Activity keeps a ledger of agent runs with Claude's own cost estimate at API prices (on a subscription it counts against your
  plan's usage instead of being billed). Pick **Quality** per video (Sonnet is lighter, Opus strongest). Stills are checked from one contact
  sheet instead of ten separate images.

## Folder layout

```
youtube/
├── start.bat              double-click to run
├── app/                   the web studio (Flask + one HTML page)
│   ├── server.py          routes, jobs, settings        ytstate.py / ytdata.py   live YouTube data
│   ├── analytics.py       numbers + the analyst agent   topics.py                topic scout + video wizard
│   └── store.py / planner.py   safe JSON files, one cached planner reader
├── tools/
│   ├── yt_upload.py       YouTube Data API uploader (see tools/yt_upload.md for one-time setup)
│   ├── build_planner.py   rebuilds bean-planner.xlsx (overwrites it)
│   └── test_app.py, test_ytdata.py   tests (no network): .venv\Scripts\python tools\test_app.py
├── docs/AUDIT.md          bugs found and fixed, simplifications, and the feature backlog
├── bean-planner.xlsx      schedule, idea bank, video types, analytics log
├── line-boil/<project>/   one folder per video: script, cast, shots, thumb.js, upload sheet
│                          (.mp4 / .png / audio stay on disk, not in git)
└── research/              channel studies (which video types beat their channel's median)
```

## Customize

- **Slots, paths, port, models, source channels**: the Settings tab (validated; a `.bak` of the old file is kept).
  Only the settings you change are stored in `config.json` (ignored by git), so new defaults in updates still reach you.
- **Agent command**: `agent_command` in Settings. The default is
  `["claude", "-p", "--permission-mode", "acceptEdits"]`; the prompt is added as the last argument.
- **Quick prompts**: the `QUICK` list in `app/static/index.html`.
- **New build buttons**: add to `ACTIONS` in `app/server.py`.

## Safety

- The server listens on `127.0.0.1` only, and also refuses requests whose Host or Origin isn't localhost, so a web page
  you visit can't drive it (DNS rebinding / cross-site requests).
- Running a job twice (double click) returns the running one, and the uploader holds a lock per video, so nothing posts twice.
- If code changes while Bean Studio is running, a yellow banner tells you to restart it; starting it twice opens the running copy.
- **Upload + schedule** and **Post now** ask for confirmation first, and the uploader refuses to upload the same project twice.
- YouTube OAuth secrets live in `tools/.secrets/` and are git-ignored. Never commit them.
- Until your Google API project passes YouTube's audit, API uploads are locked Private (see `tools/yt_upload.md`).
