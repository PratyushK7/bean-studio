"""Runs the Claude agent in stages, one after the other, as ONE Bean Studio job (one live feed, one stop button).

    python staged_agent.py <spec.json>

spec.json: {"command": [...the agent command...], "cwd": "...", "stages": [{"name", "model", "prompt", "expect": [paths]}]}

Each stage is a separate `claude -p` run, so a later stage starts with a fresh, small context instead of carrying the
earlier stage's whole history. A stage that fails, or that does not leave the files the next stage needs, stops the job
before the next (paid) stage starts. The agent's stream-json output is passed straight through to the studio's feed.
"""
import json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")      # the studio reads utf-8; a plain Windows console is cp1252
spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
stages = spec["stages"]
for i, st in enumerate(stages, 1):
    print(f"━━ Stage {i} of {len(stages)}: {st['name']} ({st.get('model') or 'default model'})", flush=True)
    cmd = list(spec["command"]) + (["--model", st["model"]] if st.get("model") else []) + ["--output-format", "stream-json", "--verbose", st["prompt"]]
    code = subprocess.run(cmd, cwd=spec["cwd"], stdin=subprocess.DEVNULL).returncode      # inherits stdout: the lines stream to the studio
    if code:
        print(f"[stage {i} failed with exit code {code}: the next stage was not started]", flush=True)
        sys.exit(code)
    missing = [x for x in st.get("expect", []) if not Path(x).exists()]
    if missing:
        print(f"[stage {i} did not leave {', '.join(Path(x).name for x in missing)}: the next stage was not started]", flush=True)
        sys.exit(3)
print("━━ All stages done", flush=True)
