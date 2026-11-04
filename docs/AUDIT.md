# Bean Studio audit (3 Nov 2026)

What was found, what was fixed, what was simplified, and what could be added next. Every fix below has a test in
`tools/test_app.py` or `tools/test_ytdata.py` unless marked (UI).

## Bugs found and fixed

| # | Problem | Why it mattered | Fix |
|---|---|---|---|
| 1 | Two clicks on **Upload** (or two windows) could start two uploads of the same video; the log was written only after the upload finished | A duplicate public video | The server returns the already-running job for the same action; the uploader also holds an atomic lock file per video |
| 2 | **Save edits** in Analytics sent the whole table back | A sync that ran meanwhile was silently reverted until the next sync (up to 6 h) | The server now merges only the editable fields into the *current* data; a sync re-applies your edits to its fresh numbers; edits autosave (UI) |
| 3 | Saving **Settings** wrote every default into `config.json` | Later improvements to defaults (new channels, models, slots) never reached you | Only changed settings are stored; input is validated; the old file is kept as `.bak` |
| 4 | A damaged `config.json` made every request fail | Studio unusable until hand-fixed | Falls back to defaults and shows a warning |
| 5 | The Schedule tab returned 500 if the planner was missing or open in Excel | The whole tab, including the YouTube half, was dead | Planner problems are reported in a note; the YouTube data still shows |
| 6 | Job list and logs grew without limit | Memory grows while the studio runs for days | Logs keep the last 4,000 lines (offsets stay correct), finished jobs are pruned to 40 |
| 7 | Background polls raised `alert()` pop-ups; an unknown job after a restart spammed them forever | Blocking dialogs, endless loop | Toasts instead; polls are quiet and stop on error (UI) |
| 8 | Watching one job cancelled the watcher of another | The "Analyze" result stopped appearing if you looked at another log | One poller per log pane (UI) |
| 9 | "Today" and the default upload date used UTC | Between 00:00 and 05:30 IST the default date was today (in the past) | IST-based dates (UI) |
| 10 | Double-clicking **Make the video** started two agents with the same project name | Two agents writing into one folder | The button locks, and the server reserves the folder name |
| 11 | A bad number in the wizard crashed the request | HTTP 500 | Safe parsing with limits |
| 12 | The uploader had a hard-coded projects path and ignored Settings | Broke if you moved the folder | Uses the configured folder (`BEAN_PROJECTS_DIR`) |
| 13 | Several threads refreshed the Google token at once and re-read it on every status check | Race on `token.json`, wasted calls | One cached credentials object behind a lock |
| 14 | Two simultaneous "refresh from YouTube" calls both hit the API | Wasted quota | De-duplicated (5 s window) |
| 15 | Every sync refetched retention curves and countries for 40 videos | 80 API calls and about a minute per sync | Only for videos under 14 days old, never checked, or last checked 3+ days ago |
| 16 | Videos list was redrawn every 5 s while a video was being made | Flicker, scroll jumps | Redraws only when something changed (UI) |
| 17 | Starting the studio twice crashed on the busy port; an old copy kept serving old code | The "404 on /api/analytics" confusion | Opens the running copy and says if it is out of date; a banner appears in the page when code changes after start |
| 18 | Any web page could in theory call the local API (it can run the agent and upload) | Cross-site and DNS-rebinding risk | Requests must have a localhost Host and, for changes, a localhost Origin |
| 19 | Retired `import-csv` / `import-planner` endpoints and three copies of the planner reader | Dead code, three places to break | Removed; one cached reader (`planner.py`) |
| 20 | Dependencies added after the first run (for example yt-dlp) were missing on a fresh pull | ImportError on start | `start.bat` re-installs when `requirements.txt` changes |
| 21 | Video types and voices were typed in three places | Drift | One list on the server, loaded by the page |
| 22 | JSON files were written in place by several threads | A crash could leave half a file | Atomic writes (`store.py`) |

## Simplified without losing anything

- **Scheduling:** "⏭ Next free slot" fills the date and time for you from your slots and what is already live or scheduled on YouTube. The full time dropdown is still there.
- **Analytics edits save themselves**; there is no Save button to forget.
- **Settings:** you only ever store your own changes.
- **One code path** for reading the channel's videos (the list is shared by Schedule, Videos and Analytics; a sync reuses it instead of listing everything again).
- **Removed:** the "Upload status" button (the Schedule tab shows the real status), the CSV and planner import code.
- **`start.bat`** keeps its own environment up to date.

## Feature backlog, most useful first

1. **Fill the week:** one button that schedules every READY video into the next free slots (builds on Next free slot).
2. **Retention explorer:** a chart per video with the script line spoken at the biggest drop, so a weak hook points straight at the sentence to rewrite.
3. **Overnight batch:** queue 3 to 5 topics from the Topics tab and make them one after another; review in the morning.
4. **Comments inbox:** new comments in one place, replies drafted in the channel voice, questions collected as topic ideas.
5. **Notifications:** a desktop alert and sound when a video is finished, an upload goes live or a job fails.
6. **Reschedule and unschedule** videos that are already on YouTube (change the time, make public, make private).
7. **Weekly report:** the analyst agent runs every Monday and saves a report.
8. **Competitor alerts:** a badge when a tracked channel posts a new outlier (5x or more its median).
9. **A calendar in the studio** (drag a video onto a slot) to retire the Excel planner as a second source of truth.
10. **Thumbnail variants:** render three options and pick before uploading.
11. **Health check page:** Python, ffmpeg, the animation kit, the Google sign-in, both APIs enabled, quota used.
12. **Agent run ledger:** time and rough cost per video, so the cost of 2 Shorts a day is visible.
13. **Captions in other languages** (Hindi, Spanish) made by the agent and uploaded through the captions API.
14. **Long-form mode** for the weekly episode (the line-boil engine currently makes Shorts).
15. **Nightly backup** commit and push of the data folder.

## Added after the audit (4 Nov 2026)

- **Long-video topic research** in the Topics tab (own source pool, ideas with chapters and sources, researched picks) and the first
  researched pick: `research/long-form-topic/brief-money-bugs.md (and brief-mosquito.md)`.
- **Length option** in the Agent tab and both wizards, passed to the line-boil skill (`build.py voice --target N`).
- **Still to build for long videos:** a 16:9 mode in the line-boil engine (canvas, world size, captions, camera, thumbnail size),
  then the same wizard renders the video instead of stopping at the package.

- **Live agent view:** progress bar from real files, readable step feed, optional own Claude window, run ledger with cost,
  per-video Quality choice, one contact sheet of stills instead of ten image reads.
- **Thumbnails:** the skill now requires the subject object to be drawn large (subject test) and text that points at the topic or its
  stakes (text test); the gum, cola and nails thumbnails were redrawn.

## Known limits (not bugs)

- YouTube's API has no "Viewed vs swiped away" metric, so Engaged % (engaged views / views) stands in for it.
- The API cannot set the Education Type or Level, or pin a comment; the upload card reminds you.
- Analytics numbers run one to two days behind.
- Until Google approves the API audit, API uploads stay private (scheduling and Post now need the audit).
