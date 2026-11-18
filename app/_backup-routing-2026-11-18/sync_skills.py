"""Mirror the line-boil skills between ~/.claude/skills (what Claude reads) and ./skills (what git pushes).
  python tools/sync_skills.py out   copy the live skills into the repo, then commit and push
  python tools/sync_skills.py in    copy the repo's skills onto a new PC
"""
import shutil, sys
from pathlib import Path

NAMES = ["line-boil", "line-boil-wide", "line-boil-thumbnail-short", "line-boil-thumbnail-long", "hindi-case-study"]
LIVE, REPO = Path.home() / ".claude" / "skills", Path(__file__).resolve().parent.parent / "skills"
skip = shutil.ignore_patterns("__pycache__", "*.pyc")

def main():
    src, dst = (LIVE, REPO) if sys.argv[1:2] == ["out"] else (REPO, LIVE) if sys.argv[1:2] == ["in"] else (None, None)
    if not src:
        sys.exit(__doc__)
    for n in NAMES:
        shutil.copytree(src / n, dst / n, ignore=skip, dirs_exist_ok=True)
        print("copied", n)

main()
