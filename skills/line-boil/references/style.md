# The line-boil style

This is a hand-drawn cartoon with line boil. The engine enforces most of it, and your job is the parts it can't:
acting, timing and staging.

## What the engine does for you

- **Palette.** Paper `PAPER` #fffaf0, ink `INK` #1c1c1c, and flat fills `RED` #ff595e, `BLUE` #1982c4 and `YEL` #ffca3a.
  Use only these (the one exception is a real brand's own colours: see **Mindful details**). The five roles stay fixed but a **theme** (`classic`, `noir`, `sepia`, `soft`, `hype`) swaps their values to fit the genre: always write `RED`, `BLUE`, `YEL`, `PAPER`, `INK`, never a hex, so every theme works (see **Genre** in SKILL.md). Paper doubles as "white" for eyes, gloves, clouds and molecules. Never add gradients, transparency
  or shading. A shadow is a flat blue blob.
- **Line.** Every mark goes through `shape`, `line`, `tube` or `fillOnly`. They give variable-width ink with tapered
  ends, slightly irregular geometry, and fills that sit a hair off the line. Don't call `ctx.arc`,
  `ctx.fillRect` or `ctx.stroke` for anything visible, or the drawing goes back to looking like perfect geometry.
- **Boil.** Each line has 3 jitter variants, cycled every drawing, so even a held pose is alive.
- **On twos.** Time is snapped to 12 drawings a second, played at 24 fps. Smooth sub-drawing motion doesn't
  exist here, so don't fight it.
- **Life on holds.** Characters breathe and blink on their own.

## Acting

- **Faces act on every beat.** Each sentence should change at least one face. Key a new `expr` on the word that
  motivates it, a beat *before* the word lands (`at('word') - 0.1`), because thought comes before speech.
- **Every big action gets anticipation.** `A.jump`, `A.cheer`, `A.dash` and `A.point` already have 4 to 6
  drawings of wind-up. If you hand-key a big move, add the wind-up yourself: squash down, move opposite to the
  action, brows down and squint (`expr: 'determined'`), then go.
- **Fast moves get a smear drawing.** It's one drawing stretched along the motion (`smear: {dir: [x, y], k: 1.8}`)
  with streak lines. The actions put one in for you. Use the `smear` transition between shots when the energy jumps.
- **Overshoot and settle.** Arrive past the pose, come back, then hold. Use squash on landing (`sy` 0.6,
  `sx` 1.4) and stretch on the way up.
- **Holds read.** After an action, hold the pose for at least 6 drawings (0.5 s) so the viewer sees it. Don't
  keep everything moving all the time.
- **A take** (`A.take`) is the reaction to a surprise: it squashes, then pops wide-eyed with take lines.
  Use it on the turn in the script ("But...") and on any reveal.
- **Look where it matters.** Use `lookAt: [x, y]` to aim the eyes at the thing being talked about. When
  characters look at a prop, the viewer looks at it too.

## The ending breathes

**A Short has no outro, so its ending is tighter:** 0.6 s of breath, 0.8 s of iris close and 0.2 s of black (1.6 s, not 2.3 s), so it
closes on the hero's face without sitting on a dead screen. It never ends on the last word, and it never ends on the callback: the last
line is the **payback**: a joke or flip that answers the opening line, never an extra open question or a teaser tacked on. The rest of this section describes the long video's longer tail; the same rules apply to a Short at the shorter timings.

A long video never ends on the last word. The engine adds 2.3 s after the voice ends:
- **1.0 s of breath:** the final pose holds on screen, still boiling and blinking.
- **1.0 s of iris close:** the ink iris closes from fully open to black, eased at both ends.
- **0.3 s on black:** then the channel outro opens out of that black.

Your job is to make that breath feel intentional:
- **Land the payoff action before the last word ends**, so the final pose is settled when the voice stops. A
  cheer, a wave or a smug look works well. Don't start a new action in the breath.
- **Keep the last shot alive through the tail.** Make the final pose a held loop that runs to `VO_END()`, such as
  `A.wave(t, VO_END())`, a gentle bob or the breathing, never a pose that freezes or a move cut off mid-way.
- **Close the iris on the character's face** (`iris: [x, y]` on the last shot) so the last thing the viewer sees
  is the expression.
- The last shot must use `tr: 'iris'`. A `cut` or `smear` there would jump straight into the outro.
- **The last shot is the closing line, and it carries the iris.** In a Short it is the payback joke (a flip of the opening line); in a
  long video the callback lands on a `cut` or `smear` and the closing hook (an open question or the next idea, and a comment prompt) follows. Ending on the callback with
  nothing after it feels like the video cut out (a Short too: its closing hook is the last shot). In a long video the channel outro
  then thanks the viewer and asks for the like, share and subscribe.

## Show what is said

The picture carries the sentence. A viewer with the sound and captions off should be able to say which sentence each shot is.

- **The real thing first.** The nouns in the sentence are on screen as themselves. "Dinosaurs vanished" shows dinosaurs vanishing.
  "A rock hit what's now Mexico" shows Mexico's coastline and the rock. "Plants died" shows plants wilting. Never replace a named thing
  with a bean, and never cover it with a caption-only shot.
- **The verb happens.** If the line says it hit, spread, shrank, starved or split, the shot shows that action, timed to the word with `at()`.
- **Recognisable at phone size.** Silhouette first, then the 2 or 3 features a stranger knows it by: a T. rex is a big head, tiny arms,
  a thick tail and two legs; a heart has its two lobes and the arteries on top; Earth has its continents. A blob with a label is a failure.
- **Real shapes for real places.** A named country, coast or continent is its own outline, simplified but true, not a yellow blob.
- **Scale and numbers become pictures.** "Wider than Everest is tall" puts the rock beside Everest. "Nothing over 25 kilos" shows a scale with a dog-sized animal on it.
  "Three in four species" is four silhouettes with three going dark.
- **Vary the shot.** Mix a wide scene, a close-up on the object, a map, a cutaway or diagram, a scale comparison, a montage and a reaction.
  Never the same set and framing three shots in a row.
- **The subject can act.** When the topic's thing should feel something (a nervous dinosaur, a smug asteroid), give it `face()`: the same
  eyes, brows and mouth a bean has. Keep its real body.

## Who is on screen (beans where they help)

Beans are the channel's characters, but a video is about its topic, and the topic's own things are the stars.

- **Use a bean for a role, not for a thing:** the viewer's stand-in ("you"), a reactor who says what the audience is thinking, a
  sceptic who is wrong the same way every time, the host bean as narrator-in-frame, or an idea with no real-world look (inflation as a
  swelling red bean, procrastination as a sleepy bean on a sofa, compounding as a tiny bean that splits in two every beat).
- **Never a bean for a real thing:** an animal, a place, an object, a body part, a machine, a person's job or a historical figure. Draw
  the real thing, and give it a face if it should act.
- **The mix:** in most shots the subject is the focus. A bean is the focus in at most about a third of the shots, often as a small
  reactor in a corner. Many shots need no character: a map, a cutaway, a close-up, a comparison.
- **Metaphor, when you use one,** is a drawable situation (a queue, a leaky bucket, a tug of war), and it still shows the real subject
  where the script names it. The same metaphor can carry the video and return in the last line.
- **Characters are different at a glance.** No two share both colour and shape. Keep one stable colour per role for the whole video.
- **Humour lives in the faces and the literal pictures:** a subject reacting to its own fate, a deadpan stare, an image that takes the
  sentence literally. Let the faces act on every beat (see Acting).
- **Numbers and names** get a label shape, a counter that ticks up, a map or a scale comparison, never a paragraph.
- **Two to four characters per shot** at most; a crowd or a herd is one object.

## Mindful details (recognisable on sight)

This file teaches a drawing style, and the same line-boil look applies to anything you draw (characters, objects, logos, places, screens, charts). Before drawing a thing, ask: **what would make a stranger recognise it instantly?**

- **A real thing looks like itself.** Anything that stands for a real brand, product, place or person keeps its identity cues (signature colours, shape, symbol), drawn in the line-boil way. Example: an Instagram phone or bean gets the camera glyph and the purple-magenta-orange sweep, not a random yellow.
- **Brand colours are the one palette exception.** Use them as flat fills with the usual ink outline, a gradient as 3 to 4 flat bands, on that one object only. Everything else stays RED, BLUE, YEL, PAPER, INK.
- **Details match the facts.** Colours, numbers, labels, times and places agree with the script.
- **Draw the specific thing the sentence names**, large enough to read, not a generic blob.
- **Check the quiet mistakes:** nothing clipped by an edge or the caption zone, readable at phone size, and it makes sense with the sound off.

## Staging

- Show one idea per shot, with one clear focal point. Keep the hero big: `size` 1 to 1.5 for close shots, and
  0.5 to 0.7 when they're a small reactor in the corner.
- Silhouettes should read in black: separate characters with space, and don't overlap a face with an arm or prop.
- Frame for vertical video. Keep faces, eyes and key props between y 110 and 750 and x 40 to 500 in world units
  (540 x 960). The bottom fifth and the top edge get covered by the platforms' buttons.
- Camera keys move slowly. Use a push-in (z 1 to 1.08) for curiosity, a pull-back for a reveal, and
  `shake: 4` for a moment on impact.
- Sets are flat colour bands (`band`) and a ground line. Keep backgrounds simple and few: 2 or 3 elements.

## Captions, and otherwise almost no text

**Burned-in captions are on by default.** The engine draws them from the voiceover's word times, in the channel
lettering:
- bold Poppins, uppercase, with a thick ink outline and a drop shadow
- each word slightly tilted and boiling
- 1 to 3 words at a time, never running across a pause
- the spoken word lit yellow and slightly larger, the others paper-white
- each chunk popping in

They sit in the **centre band (y 500, about 52% down)**. That's the sweet spot: the eye is already there, and it's
well above the Shorts overlay at the bottom (title, channel name, buttons, from about y 720 down). That makes the
centre band part of the layout:
- **Compose around it.** Keep faces out of y 475 to 530. A standing hero with feet on the ground at y 800 and
  `size` up to about 1.5 clears it: their head sits below the band. Props, bodies, strings and sky can pass
  behind the captions; the ink outline keeps them readable.
- **Close-ups and centred faces need a move.** When a face or a talking prop sits at the centre (a camera push-in
  past z 1.15, a big cutaway object with a face, a character mid-frame), move that shot's captions:
  - into open space below the subject, still above the overlay: `cap: 690`
  - into a gap: `cap: 420`
  - or to the top: `cap: 'top'` (y 150)
  - `cap: false` hides them, which you should almost never do.
- **Never go below y 720**, because the Shorts overlay covers it.
- Check a still of every shot. In the first two videos, about one shot in four needed its captions moved.

Captions don't replace the pictures. Every idea still has to be *shown* with props, arrows, side-by-side
comparisons (big vs small, long vs short), characters reacting, and symbols (`plus` sparkles, `heart`, `drop`,
`bulb`, `arrow`, `burst`). Apart from the captions, keep text almost absent. If one word or number is truly
essential in the picture, draw it as a prop, like a sign or a label shape. Never render paragraphs.

## Sound

The actions add their own cues: whoosh on smears, thud on landings, squeak on takes, pop on points, boing on cheers.
Add `cue(t, kind)` for props: zip when something appears, pop or plop for small hits, sparkle for magic or
insight, ding for an idea, slide_up or slide_down for rises and falls, drum for a build. Keep sound effects
sparse, one or two per sentence. The music underscore ducks under the voice automatically.
