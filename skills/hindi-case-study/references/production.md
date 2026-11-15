# Production: from an approved script to a finished cut

The script skill stops at Gate A (the owner approves `<slug>-script.md` and the free listen). This file keeps what the
later steps learned, so the visual notes and the shot plan in `script.json` make them possible. The tools live in
`C:\Users\praty\youtube\tools\` (`vyapaar_voice.py`, `vyapaar_prompts.py`, `vyapaar_assemble.py`, `vyapaar_styles.py`,
`vyapaar_mix.py`, `video/ws_upscale.js`, `video/render_overlays.js`).

## What the references do (measured on downloaded winners)

HinExp Dhaba and Dumper, AB FinDoc Big Bull, Money Code Biryani:
- HinExp's average shot is 1.7 s (Dhaba) and 4.1 s (Dumper).
- All four have 0% near-still time.
- AB FinDoc and Money Code move mostly by dissolves and animation.
- HinExp, ABFinDoc and Finance In Minutes animate 88 to 99% of the time, in 1 to 4 s shots.
- Money Code is the hybrid: 3 to 4 s shots, about half of them moving.
- HiddenOps cuts under 1 s in the hook, then 3 to 6 s.

## The shot plan in script.json

- `still`: an illustration with a planned camera move. Each still is cut into shots of about 2 to 3.4 s, each a different
  framing (push-in, pan, tighter push, pull-out). A still is never held on one framing.
- `card`: a code graphic for a number, a ledger, a bar, a map or a flow arrow, in clean Hinglish. It is free. Every
  money-math line gets one, and two cards never come in a row.
- `hero`: an AI image-to-video clip of 2 to 5 s, at $0.032 a second on xAI. It is on hold: the owner judged the first 25 clips
  poor in quality and prompts, so it waits until the channel earns.
- Pictures: a new one every one to three lines. Recurring characters and places keep the same description word for word, so
  the image tool keeps them consistent. Showing the same place again from a new angle or at a new moment is how the cost stays
  low without the video feeling repetitive.
- **The picture must match the line.** A picture of Ramesh holding out sweets on a line saying that his hand does not rise is
  a mismatch the viewer notices. Write `visual` for the exact moment the line describes.

## Edit and render rules

These are learned from the first jewellery render, which the owner rejected as jerky, frozen and amateur.

What went wrong, measured:
- one picture per line, held 6.5 s on average
- 3 s clips frozen on 4 to 12 s lines (266 frozen stretches)
- ffmpeg `zoompan`, which jitters, and per-line segment files, which leave seams
- synthetic placeholder music

The rules that fixed it:
1. **No shot over about 4 s.** Never freeze a clip. After a clip ends, continue from its last frame with a camera move that
   starts at zoom 1.0, so the join is invisible.
2. **Never `zoompan`.** Compute every frame with a sub-pixel crop (Pillow, box resize) and a smooth move. Pipe the raw frames
   into one encoder: no per-line segments and no concat seams, so no black or duplicated frames. Never crop tighter than 1.3x.
3. **Test before the full render.** Render a short opening (`--limit 14`, or the 60 s style sample), then run `freezedetect`,
   `blackframe` and the 6 fps frame-difference motion check (ours was 5.4 against HinExp's 6.9 to 8.3). Fix problems before
   spending 15 minutes on the whole video.
4. **Pace.** Shots of about 1.5 to 2.1 s in the first 45 s and 2 to 3.4 s after that. Snap every cut to a pause in the voice
   (silencedetect). Put one grade over stills, clips and cards so they look like one film, and fade card text in.
5. **The chosen direction (Nov 2026): Ken Burns, sample K** (`tools/vyapaar_styles.py <project> K`):
   - hand-planned start and end framings per picture
   - linear moves and 0.6 s dissolves
   - the film grade (`GRADE_K`: slightly warm, a little contrast, a soft vignette, light grain)
   - pictures upscaled 2x by WaveSpeed Desktop's local ESRGAN (`tools/video/ws_upscale.js`, free, on the RX 6700 XT)
   - Hindi text rendered as HTML to transparent PNGs in Chromium, because this machine's Pillow has no raqm and breaks
     Devanagari

   The owner called it "okay but not yet professional". Raise the quality before scaling it to a full video.
6. **Sound.** Synthetic music and effects sound cheap. Use only real tracks in `<project>/audio/music` and `audio/sfx`.
   - Duck the music under the voice (`sidechaincompress`) and level the mix to -14 LUFS (`loudnorm`).
   - Use effects sparingly: a low thud on a reveal, never a whoosh on every cut.
   - Kevin MacLeod tracks are CC BY 4.0, so the credit goes in the description.
7. **The voice.** Sarvam bulbul:v3 aditya at pace 0.92 was the first choice, and the owner finds it not soothing.
   - The softer finish is `VOICE_SOFT` in `vyapaar_styles.py`.
   - The 17-voice comparison is `tools/voice_compare.py`.
   - Choose by ear, on a 60 s sample of the hook, before paying for a full voice.
8. **Subtitles** are a separate `.srt`, never burned in.

## The sound plan fields

- `music`: `tense`, `warm`, `curious`, `sad` or `hopeful`, set on the line where a mood starts; it holds until the next one.
  Use one mood per chapter, plus changes at the big turns.
- `amb`: a quiet looping bed (`crowd`, `fan`, `tv`, `flame`, or `none` to end it).
- `sfx`: a name or a list at the start of a line (`"coin@1.0"` means one second later): `whoosh`, `whoosh_soft`, `thud`,
  `coin`, `page`, `tick`, `scale_ping`, `door`, `shutter`, `riser`, `stinger`. Only on money moments, reveals and scene
  changes.
- Mix with `python tools/vyapaar_mix.py <project>`. Its placeholders are for timing tests only, never for a delivered cut.
