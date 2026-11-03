# Bean Studio 🫘💡

The production desk for **The Bean With Bad Ideas**, a YouTube channel of hand-drawn line-boil cartoon
science Shorts. One local web page to build videos, check them, schedule uploads and ask the agent for help.

![Bean Studio](https://img.shields.io/badge/runs-localhost%20only-1982c4)

## Start it

Double-click **`start.bat`**. The first run creates `.venv` and installs everything (about a minute), then
the studio opens at **http://127.0.0.1:5173**. Close the window (or Ctrl+C) to stop it.

Needs: Python 3.10+, and for building videos the `line-boil` Claude Code skill plus the
`claude-animation-skills` kit. The Agent tab needs Claude Code (`claude` on your PATH).

## What's in the studio

| Tab | What it does |
|---|---|
| **Videos** | Every project with its thumbnail and a checklist (script, video, captions, thumbnail, upload sheet, uploaded). Open one to watch it, run the build steps (Voice → Check → Build video → Thumbnail), edit the script and upload sheet, and upload + schedule it to YouTube. |
| **Schedule** | The posting plan from `bean-planner.xlsx` (2 Shorts a day + 1 long-form a week), with an "Open in Excel" button. |
| **Agent** | Type a request and Claude Code runs it in this folder with the line-boil and yt-* skills. Quick buttons for a new Short, an upload sheet, a thumbnail, rebuilding an old Short, or an idea batch. |
| **Activity** | Live logs of everything running, with a Stop button. YouTube sign-in and upload status live here. |
| **Settings** | `config.json`: paths, posting slots, the agent command, the port, hidden folders. |

## Folder layout

```
youtube/
├── start.bat              double-click to run
├── app/                   the web studio (Flask + one HTML page)
├── tools/
│   ├── yt_upload.py       YouTube Data API uploader (see tools/yt_upload.md for one-time setup)
│   └── build_planner.py   rebuilds bean-planner.xlsx (overwrites it)
├── bean-planner.xlsx      schedule, idea bank, video types, analytics log
├── line-boil/<project>/   one folder per video: script, cast, shots, thumb.js, upload sheet
│                          (.mp4 / .png / audio stay on disk, not in git)
└── research/              channel studies (which video types beat their channel's median)
```

## Customize

- **Slots, paths, port**: the Settings tab, or create `config.json` with any keys from `DEFAULTS` in
  `app/server.py`. It's ignored by git, so it's yours.
- **Agent command**: `agent_command` in Settings. The default is
  `["claude", "-p", "--permission-mode", "acceptEdits"]`; the prompt is added as the last argument.
- **Quick prompts**: the `QUICK` list in `app/static/index.html`.
- **New build buttons**: add to `ACTIONS` in `app/server.py`.

## Safety

- The server listens on `127.0.0.1` only, so nothing else on your network can reach it.
- **Upload + schedule** asks for confirmation first, and the uploader refuses to upload the same project twice.
- YouTube OAuth secrets live in `tools/.secrets/` and are git-ignored. Never commit them.
- Until your Google API project passes YouTube's audit, API uploads are locked Private (see `tools/yt_upload.md`).
