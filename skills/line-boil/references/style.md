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

## A cast of beans

Every video is told by beans, and the channel's trick is *different beans for different ideas*. This is how an abstract topic
becomes something you can draw and something that is funny.

- **One bean per idea or role.** The viewer ("you"), the thing explained, what opposes it, the sceptic, the crowd. If you cannot
  say what a bean *wants* in one line, it should be a prop instead.
- **A costume that shows the idea.** Colour, shape and accessories carry the meaning so no label is needed: a swelling red `ball` for
  something inflating, a `tiny` yellow bean that splits in two every beat for compounding, a `tall` thin bean for a deadline, a
  spiky `rays` bean for a virus, a sleepy `wide` bean for procrastination, a `box` bean with a hat for an institution.
- **Metaphor first.** Choose the physical metaphor before writing the shots (a queue, a leaky bucket, a tug of war, a stage with a
  heckler), then cast the beans into it. The same metaphor should carry the whole video and return in the last line.
- **Different at a glance.** No two beans share both colour and shape. Keep one stable colour per role for the whole video.
- **Humour lives in the beans.** Reactions, deadpan stares, a bean that takes everything literally, a sceptic bean that is always
  wrong the same way. Let the faces act on every beat (see Acting).
- **Numbers and names** get a label shape held by a bean, a counter that ticks up, or a crowd of `tiny` beans, never a paragraph.
- **Two to four beans per shot** at most; a crowd is one object. The red host bean is available as narrator-in-frame.

## Mindful details (recognisable on sight)

This file teaches a drawing style. It is not limited to beans: the same line-boil look applies to anything you draw (characters, objects, logos, places, screens, charts). Before drawing a thing, ask: **what would make a stranger recognise it instantly?**

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
