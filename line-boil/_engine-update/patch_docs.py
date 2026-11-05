"""Patch the line-boil / line-boil-wide skill docs and the channel voice for the new ending: callback, closing hook, voiced channel
outro with the like / share / subscribe ask on every video, end-screen settings, and build.py voice --append / --hold.
Every change is checked to apply exactly once; nothing is written unless all of them apply.
usage: python patch_docs.py <out dir | --in-place>"""
import sys
from pathlib import Path

HOME = Path.home() / '.claude'
LB, LBW, VOICE = HOME / 'skills' / 'line-boil', HOME / 'skills' / 'line-boil-wide', HOME / 'youtube' / 'voice.md'

OUTRO = '''`build.py video` appends the channel outro to every video, voiced in af_heart, and adds the outro's words to the `.srt`:
- **Shorts:** `engine/outro/outro.mp4` (about 5.4 s). "Like, share, and subscribe for more bad ideas." LIKE and SHARE pop in on
  their words, SUBSCRIBE drops and the bell rings, the host bean cheers and waves, and the iris closes on its face.
- **Long videos:** `engine/outro-wide/outro-wide.mp4` (about 14.8 s). "Thanks for watching. If you learned something, give it a like
  and share it with a friend. And subscribe, so the next bad idea finds you. Your next video is right over here." LIKE, SHARE and
  SUBSCRIBE arrive on their words, then the frame turns into an end-screen layout (a drawn video frame on the right, SUBSCRIBE under the
  host) and holds about 6 s so YouTube's end-screen elements can sit on it (see `references/youtube.md`).

The outro is the channel's one ask, so the script itself never says like, share or subscribe. Videos end on the closing hook's `iris`,
so the outro's opening iris follows on cleanly. Pass `--no-outro` to leave it off. To change an outro, edit
`engine/outro-wide/script.json` and `web/shots.js` (or `engine/outro/...`), then voice and render it:
`python build.py voice "$ENGINE/outro-wide" --voice af_heart --hold 3` and `python build.py video "$ENGINE/outro-wide" --no-outro`
(the Shorts outro: the same with `"$ENGINE/outro"` and no `--hold`).'''

DOCS = {
LB / 'SKILL.md': [
("""the mechanism in 2 or 3 escalating beats, then a payoff that answers the hook, ideally calling back to the
   opening image.""",
"""the mechanism in 2 or 3 escalating beats, then a payoff that answers the hook, ideally calling back to the
   opening image, then a **closing hook**: one line that leaves a question open or teases the next idea (a Short), or two or three
   (a long video: the open question, "that's a ... for another day", and a comment prompt). Never stop dead on the callback. The script
   never asks for likes, shares or subscribes: the voiced channel outro does that on every video (see **Channel outro**)."""),
("""`build.py video` appends `engine/outro/outro.mp4` to every video: the 3.5 s "The Bean With Bad Ideas"
sign-off, where the bulb pops, the title appears, the SUBSCRIBE button drops and the iris closes. Videos end on the
`iris` transition, so the outro's opening iris follows on cleanly. Pass `--no-outro` to leave it off. To change
the outro, edit `engine/outro/web/shots.js` and re-render it with
`python build.py video "$ENGINE/outro" --no-music --no-outro`.""", OUTRO),
("""- If you change the script, re-run `voice`. Shots timed with `at()` follow the new take automatically.""",
"""- If you change the script, re-run `voice`. Shots timed with `at()` follow the new take automatically.
- If you only add sentences at the END of `script.json` (a closing hook, a new last line), run `build.py voice <project> --append`:
  it voices just the new sentences and keeps the earlier audio and every earlier word time exactly, so nothing before them moves. It
  refuses if an earlier sentence was edited."""),
],
LB / 'references' / 'style.md': [
("""- The last shot must use `tr: 'iris'`. A `cut` or `smear` there would jump straight into the outro.""",
"""- The last shot must use `tr: 'iris'`. A `cut` or `smear` there would jump straight into the outro.
- **The last shot is the closing hook, not the callback.** The callback lands on a `cut` or `smear`; then the closing hook (an open
  question or the next idea, and in a long video a comment prompt) plays, and its shot carries the iris. Ending on the callback with
  nothing after it feels like the video cut out. The channel outro then thanks the viewer and asks for the like, share and subscribe."""),
],
LB / 'references' / 'youtube.md': [
("""- **Pinned comment.** One dry line that invites a reply, often the next "bad idea" ("What should we
  measure in mosquitoes next?").""",
"""- **Pinned comment.** One dry line that invites a reply, often the next "bad idea" ("What should we
  measure in mosquitoes next?"). In a long video, echo the closing hook's comment prompt, so the question the video asked has a home."""),
("""Subtitles: upload <project>.srt (Subtitles > Upload file > With timing)""",
"""Subtitles: upload <project>.srt (Subtitles > Upload file > With timing)
End screen (long videos only; Editor > End screen): the voiced outro is drawn for one. Start the elements when it says "your next video
is right over here" (about 7.4 s into the outro, so the video's length minus about 7.3 s) and run them to the end: a Video element
("Most recent upload" or "Best for viewer") over the drawn frame on the right, and a Subscribe element. Keep both off the host bean."""),
],
LBW / 'SKILL.md': [
("""python "$ENGINE/build.py" voice    <project> --target 420  # Kokoro voiceover (any length), word times, and whether the length hits the target""",
"""python "$ENGINE/build.py" voice    <project> --target 420  # Kokoro voiceover (any length), word times, and whether the length hits the target
python "$ENGINE/build.py" voice    <project> --append      # voice only sentences added at the end; every earlier word time is kept"""),
("""   sentence and start doing it. **No channel intro, no "before we get started", no subscribe pitch** (the outro is the channel's one ask;
   do not add another). Deliver the payoff the hook promised explicitly, and end on the callback.""",
"""   sentence and start doing it. **No channel intro, no "before we get started", no subscribe pitch** (the voiced outro asks for likes,
   shares and subscribes on every video; do not add another ask). Deliver the payoff the hook promised explicitly and land the callback,
   then a **closing hook** of 2 or 3 sentences (10 to 15 s): one question the video leaves open or a tease of the next idea, a dry "that's a
   ... for another day", and a comment prompt the viewer can answer in a few words ("Until then, tell us in the comments: what time is
   your last coffee?"). Never end on the callback with nothing after it. Count the closing hook in the target length."""),
("""   beat at least every 6 to 12 seconds, 2 to 4 beans a shot. **No burned-in captions** (below). The last shot has `tr: 'iris'` and a held
   loop to `VO_END()`, as in a Short.""",
"""   beat at least every 6 to 12 seconds, 2 to 4 beans a shot. **No burned-in captions** (below). The callback lands on a `smear`; the
   closing-hook shots follow, and the last of them has `tr: 'iris'` on the speaker's face and a held loop to `VO_END()`, as in a Short."""),
("""    lines hold the target search queries, then the chapters from `<project>-chapters.txt`, then 6 to 8 sources from `<project>-sources.md`);
    tags; a pinned comment; the settings checklist.""",
"""    lines hold the target search queries, then the chapters from `<project>-chapters.txt`, then 6 to 8 sources from `<project>-sources.md`);
    tags; a pinned comment that echoes the closing hook's comment prompt; the settings checklist, with the end-screen timing (the
    outro's last 7 s are drawn for a Video and a Subscribe element)."""),
],
LBW / 'references' / 'wide.md': [
("""   Rules: **at least four different moods in a 7-minute video**; the hook is `curious` or `mystery`, the payoff `triumphant` or `calm`; put""",
"""   Rules: **at least four different moods in a 7-minute video**; the hook is `curious` or `mystery`, the payoff `triumphant` or `calm`,
   the closing hook `mystery` or `curious`, and the comment prompt `upbeat` (the outro plays `upbeat` too); put"""),
("""- 5 to 9 chapters of 45 to 90 s. Hook, the idea in three beats, the payoff, the callback.""",
"""- 5 to 9 chapters of 45 to 90 s. Hook, the idea in three beats, the payoff, the callback, the closing hook (in the last chapter).

## The ending (every long video)

1. **The callback**, the last line of the payoff, on a `cut` or `smear`.
2. **The closing hook**, 2 or 3 sentences, 10 to 15 s: the question the video leaves open (or the next idea), "that's a ... for another
   day", and a comment prompt the viewer can answer in a few words. Give it its own shots and a new set; it is a beat, not a footnote.
3. **The last shot**: `tr: 'iris'` on the speaker's face, a held loop to `VO_END()`.
4. **The channel outro** (automatic, about 14.8 s): voiced thanks, like, share, subscribe, then an end-screen layout held about 6 s.
   Its words go in the `.srt`. On the YouTube sheet, the end-screen elements start when it says "your next video is right over here"."""),
],
VOICE: [
("""- Ends on a punchy callback: "Salty water keeps you cool, not candied." / "Getting down is the hard part.\"""",
"""- Ends on a punchy callback: "Salty water keeps you cool, not candied." / "Getting down is the hard part."
- Then a closing hook, never a hard stop: one open question or a tease of the next idea, and in a long video a comment prompt
  ("...what happens when you drink it every single day? That's a mailbox for another day. Until then, tell us in the comments: what
  time is your last coffee?"). The script never asks for likes or subscribes itself.
- Every video then ends on the channel outro, voiced in af_heart. Long: "Thanks for watching. If you learned something, give it a like
  and share it with a friend. And subscribe, so the next bad idea finds you. Your next video is right over here." Shorts: "Like, share,
  and subscribe for more bad ideas." That is the channel's one ask."""),
],
}

out = sys.argv[1]
results, bad = {}, []
for path, reps in DOCS.items():
    s = path.read_text(encoding='utf-8')
    for a, b in reps:
        if s.count(a) != 1:
            bad.append(f'{path.name}: {a.splitlines()[0][:80]}')
        s = s.replace(a, b)
    results[path] = s
if bad:
    sys.exit('these changes do not apply:\n  ' + '\n  '.join(bad))
for path, s in results.items():
    dst = path if out == '--in-place' else Path(out) / path.relative_to(HOME)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(s, encoding='utf-8')
    print('wrote', dst)
