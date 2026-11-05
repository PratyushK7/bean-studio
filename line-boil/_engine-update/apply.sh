#!/usr/bin/env bash
# Install the voiced channel outros and the closing-hook rules into the line-boil skills.
# Backs up everything it replaces into _engine-update/backup/ first. Run from anywhere:  bash line-boil/_engine-update/apply.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LB="$(cd "$HERE/.." && pwd)"                       # C:\Users\praty\youtube\line-boil
SK="$HOME/.claude/skills"
ENGINE="$SK/line-boil/engine"
BK="$HERE/backup"

echo "== backing up to $BK"
mkdir -p "$BK/outro/web" "$BK/outro-wide/web" "$BK/docs/line-boil/references" "$BK/docs/line-boil-wide/references"
cp "$ENGINE/build.py" "$BK/"
for o in outro outro-wide; do
  cp "$ENGINE/$o/script.json" "$BK/$o/"
  cp "$ENGINE/$o/web/cast.js" "$ENGINE/$o/web/shots.js" "$ENGINE/$o/web/words.js" "$BK/$o/web/"
  cp "$ENGINE/$o/$o.mp4" "$BK/$o/"
done
cp "$SK/line-boil/SKILL.md" "$BK/docs/line-boil/"
cp "$SK/line-boil/references/style.md" "$SK/line-boil/references/youtube.md" "$BK/docs/line-boil/references/"
cp "$SK/line-boil-wide/SKILL.md" "$BK/docs/line-boil-wide/"
cp "$SK/line-boil-wide/references/wide.md" "$BK/docs/line-boil-wide/references/"
cp "$HOME/.claude/youtube/voice.md" "$BK/docs/"

echo "== patching build.py (voice --append, voice --hold, outro words in the .srt)"
python "$HERE/patch_build.py" "$ENGINE/build.py" "$ENGINE/build.py"

echo "== patching the skill docs and the channel voice"
python "$HERE/patch_docs.py" --in-place

echo "== installing the voiced outros"
install_outro () {   # $1 = staged project, $2 = engine outro folder
  local src="$LB/$1" dst="$ENGINE/$2"
  mkdir -p "$dst/audio"
  cp "$src/script.json" "$dst/"
  cp "$src/web/cast.js" "$src/web/shots.js" "$src/web/words.js" "$dst/web/"
  cp "$src/audio/vo.wav" "$src/audio/words.json" "$src/audio/sentences.json" "$dst/audio/"
  cp "$src/$1.mp4" "$dst/$2.mp4"
  echo "   $2 <- $1"
}
install_outro _outro-wide outro-wide
install_outro _outro-short outro
echo "done. Every new video now ends on the voiced outro. To undo, copy the files in $BK back."
