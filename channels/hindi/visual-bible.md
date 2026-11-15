# Decoding Vyapaar visual bible

_Generated from `visual-bible.json` by `python tools/vyapaar_visual.py bible`. Edit the JSON, not this file._

## 1. Rendering style

Premium semi-realistic digital illustration for serious Hindi business documentaries: a painted film still, not a photo, not a cartoon.

Prompt words: Premium semi-realistic digital illustration, like a painted documentary film still: realistic proportions and anatomy, natural textures (wood, glass, metal, brass, gold, fabric, paper), refined soft shading with controlled highlights, rich but restrained colour.

Never: photorealistic photograph; cartoon or anime; plastic 3D render or waxy skin; oversaturated advertising colour; stock-photo grins; fantasy glow or lens-flare spectacle; mixed art styles within one video.

## 2. Colour palette

Rich but restrained. Warm wood, brass and cream carry the old world; cool teal-grey and white LED carry the new. Gold is a highlight, never a flood.

- Base: warm walnut brown #5A3B24, cream #EFE3CC, muted teal-grey #6F8C88, charcoal #26211C
- Accents: restrained gold #C9A23A, marigold orange #D9822B, vermilion #B5432F
- Cool: LED white #E8EEF0, steel blue-grey #5B6B78, night blue #1F2A3A
- One dominant temperature per scene, with at most one contrasting practical light.
- Gold appears as polished highlights on objects, never as a yellow wash over the frame.
- Skin stays natural brown with warm undertones in every look; never orange, never grey.

## 3. Lighting philosophy

Light comes from a source that exists in the scene (a shopfront, a tube light, a diya, a streetlamp, a desk lamp) and has a direction. The story's time and mood decide the light, never a global preset. Night is dark, with pools of practical light; day is soft, with real shadows; a memory is warm and faded.

| Look | Light | Target brightness (0 to 1) |
|---|---|---|
| `street_day` Market street, day | Late-morning light: high soft sun filtered through shop awnings, warm dappled shade on stone and painted plaster, a light haze down the lane. | 0.42 to 0.66 |
| `interior_day` Small interior, day | Soft daylight from the open shopfront on one side, warm tungsten spotlights inside the glass showcases, natural falloff into the back of the room, real shadows under the counter. | 0.38 to 0.62 |
| `interior_festive_night` Interior, festival night | Night during a festival: warm tungsten shop lights overhead and the flicker of diyas at the door, marigold strings, deep warm shadows, faces lit warmly from the side; no daylight anywhere. | 0.26 to 0.50 |
| `street_festive_night` Bazaar, festival night | A festival night in the bazaar: strings of warm bulbs and marigolds overhead, shop light spilling onto the crowd, deep warm shadows between pools of light; no daylight. | 0.24 to 0.50 |
| `interior_after_hours` Interior after closing | After closing: a single desk lamp or one tube light is the only source, the rest of the room falls into soft shadow, quiet and still. | 0.14 to 0.38 |
| `street_night` Lane at midnight | Midnight: one amber streetlamp and cool blue moonlit shadows, shutters down, empty stone lane, a few lit windows; dark overall, faces lit only by the nearest lamp. | 0.10 to 0.34 |
| `retail_modern` Modern showroom, inside | Even bright cool-white LED light, polished marble floor and glass counters with crisp reflections, gold under small focused spotlights, clean and expensive. | 0.48 to 0.72 |
| `retail_night_exterior` Showroom glowing at night | Night: the glass showroom glows white and gold from inside across a dark road, its light spilling on the pavement; everything around it is in deep blue shadow. | 0.14 to 0.40 |
| `rooftop_workshop` Rooftop goldsmith workshop | Rooftop workshop: hard late-morning sun and open sky, shade from a corrugated sheet roof, the small blue-orange flame of a blowpipe, soot, brass tools and worn wood. | 0.38 to 0.64 |
| `home_evening` Home at night | A middle-class dining room at night under one cool overhead tube light: flat, slightly harsh light, muted colours, plain walls, quiet. | 0.24 to 0.48 |
| `office_day` Bank or office | Institutional office: cool fluorescent light, beige files and steel cupboards, a glass partition, neutral and orderly. | 0.42 to 0.64 |
| `insert_neutral` Table-top insert | A table-top insert: one soft directional key light from the side, shallow depth of field, the surface texture sharp and the background softly out of focus. | 0.26 to 0.60 |
| `aerial_dusk` City from above, dusk | High view over a dense Indian city at dusk: a fading orange-blue sky, rooftops and water tanks, shop lights coming on along the main road. | 0.20 to 0.48 |
| `flashback` A memory (modifier) | Seen as a memory: warm faded colours, slightly lower contrast, soft highlights with a gentle film glow. | 0.34 to 0.64 |

## 4. Characters

- Every recurring person has a structured entry in the project's visual-plan.json (id, age, face, skin, hair, body, clothing, accessories, distinguishing features, reference sheet).
- A reference sheet is made first and approved before any scene shows that person; every scene with the person attaches the sheet.
- The scene prompt restates three to five identity details in the same words every time.
- Clothes change only when the story says so (a showroom uniform), and the plan says so on that shot.
- Expressions come from the shot, never a default smile.

Sheet prompt: Character reference sheet of {who}: front view and three-quarter view, standing relaxed, full body, plus one head-and-shoulders close-up, on a plain warm grey background, even soft studio light.

## 5. Environments and materials

Every location is described once in the project's `visual-plan.json` (`locations`), with its default look, and repeated word for word. Materials are named so they render as materials: worn walnut, scratched glass, brushed steel, brass, polished marble, cotton, silk, plaster, corrugated sheet.

## 6. Camera and composition

| Shot | Prompt words | Use it for |
|---|---|---|
| `establishing` | Establishing wide shot, slightly high angle, 24mm lens | a new place or time; the first shot of a chapter or location |
| `wide` | Wide shot, eye level, 28mm lens | a person in their environment; crowds; movement through space |
| `medium` | Medium shot from the waist up, eye level, 40mm lens | a person doing something; dialogue setups |
| `medium_close` | Medium close-up from the chest up, eye level, 50mm lens, background softly out of focus | a line of dialogue; listening; a decision |
| `close` | Close-up of the face, 85mm lens, shallow depth of field | an emotional beat; a reaction; a realisation |
| `extreme_close` | Extreme close-up, 100mm macro lens, very shallow depth of field | eyes, fingers, a tiny engraved mark |
| `insert` | Insert shot of the object, 60mm lens, shallow depth of field | an object that carries the story: a bill, a scale, a safe dial |
| `macro` | Macro detail, 100mm macro lens, razor-thin focus | texture and process: solder, gold dust, a hallmark |
| `ots` | Over-the-shoulder shot, 50mm lens, the near shoulder soft in the foreground | one person facing another; what someone sees across a counter |
| `pov` | Point-of-view shot through the character's eyes, 35mm lens | what a character looks at: the showroom across the road, the safe |
| `reaction` | Reaction close-up of the listener, 85mm lens | the face of the person hearing the line, not the speaker |
| `two_shot` | Two-shot of both people in one frame, 40mm lens, both faces clearly visible | a relationship; two people on one step; father and son |

- Place the subject on a third, eyes on the upper third, with room in the direction of the gaze or movement.
- Build depth in three layers: a foreground element (a counter edge, a doorway, showcase glass), the subject in the middle ground, and the setting behind.
- Separate the subject from the background with light and value, not with outlines.
- Keep faces and key objects inside the central 80% of the width and above the lower 18%, so camera moves and graphics never cut them.
- Centre a subject only on purpose (a formal, still, or lonely moment).
- One idea per frame: the line's moment, not a collage.

## 7. Colour grading

One grade for stills, clips and graphics alike: a touch of contrast, saturation slightly down so gold never floods, shadows warm, highlights a little cool, a light vignette and fine grain. It is applied once, in the encoder.

`eq=contrast=1.06:brightness=-0.02:saturation=0.92:gamma=0.98,colorbalance=rs=0.025:gs=0.005:bs=-0.03:rh=-0.01:bh=0.015,vignette=angle=PI/7:mode=forward,noise=alls=2:allf=t`

Flashbacks add a modifier on top: {"saturation": 0.72, "warm": [1.06, 1.0, 0.9], "lift": 0.05, "soften": 0.8}.

## 8. Aspect ratio and safe composition

16:9. Action-safe 5% on every side; title-safe 10%. Camera moves crop up to 1.3x, so the subject must sit inside the central 75% of a still.

## 9. Recurring characters and locations

Stable ids in `visual-plan.json`; `visual-slots.json` keeps each shot's picture number; the reference manifest `prompts/REFS.md` says which sheets to attach to each prompt; `continuity-report.md` checks every shot against the bible.

## Negative instructions (in every prompt)

No readable text, logos or watermarks; signs, screens and papers are blank or illegible. Natural anatomy, five fingers per hand, no duplicate people, no distorted faces, no floating objects, plausible jewellery and tools, straight consistent architecture.

## Graphics system

Numbers, ledgers, comparisons and timelines are drawn as motion graphics, never generated as pictures. One design system for every video.

- Every number on a graphic comes from the line or the research file, and the graphic lists its fact ids.
- One message per graphic; at most five rows or bars.
- Hindi in Devanagari through Chromium (Nirmala UI); numerals in Bahnschrift.
- Elements enter in the order the narration says them; nothing decorative moves.
- A graphic sits on the blurred, darkened scene it interrupts (backdrop); rows already shown appear at once, only the new row counts up; a result appears after the rows that make it.

## Render settings

1920x1080 at 30 fps. 30 fps divides evenly into 60 Hz screens, where most viewers watch, so slow camera moves stay smooth; 24 fps on 60 Hz shows 3:2 judder exactly on slow pans. Clips made at 24 fps are conformed by frame repetition unless a measured test shows motion interpolation is cleaner (vyapaar_clips.py fps-test).
