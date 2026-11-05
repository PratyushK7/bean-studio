# Voiced outro and closing hook: engine and skill update (staged, not yet installed)

`~/.claude/skills` and `~/.claude/youtube` are blocked for edits in Claude Code's permission settings, so these changes are staged here.
Install them with `bash line-boil/_engine-update/apply.sh` (it backs up everything it replaces into `_engine-update/backup/` first).

What it installs:

| What | From | To |
|---|---|---|
| 16:9 outro, voiced, about 14.8 s, end-screen layout held about 6 s | `line-boil/_outro-wide/` | `engine/outro-wide/` (`outro-wide.mp4`) |
| 9:16 outro, voiced, about 5.4 s | `line-boil/_outro-short/` | `engine/outro/` (`outro.mp4`) |
| `build.py`: `voice --append` (voice only new last lines, keep every earlier word time), `voice --hold N` (end-screen time), the outro's words in the `.srt` | `patch_build.py` | `engine/build.py` |
| The rule: callback, then a closing hook, then the voiced like / share / subscribe outro; end-screen settings on the YouTube sheet | `patch_docs.py` | `line-boil/SKILL.md`, `references/style.md`, `references/youtube.md`, `line-boil-wide/SKILL.md`, `references/wide.md`, `~/.claude/youtube/voice.md` |

Both patch scripts check that every change applies exactly once and write nothing if one does not.
