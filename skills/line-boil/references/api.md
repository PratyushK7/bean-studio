# line-boil engine API

The world is **540 x 960** (y down), rendered at 2x. All times are **voiceover seconds** unless a field says it's
shot-local. The scripts load in order: `words.js`, `ink.js`, `props.js`, `rig.js`, `main.js`, then your `cast.js`
and `shots.js`, so everything below is a global.

## Contents
1. Timing: `at`, `end`, `D`, `NOW`
2. Shots and camera: `shot`
3. Characters: `makeChar`, `drawChar`, poses, `ARMS`, `EXPR`
4. Actions: `A.*`
5. Ink marks
6. Props and sets
7. Sound: `cue`
8. A minimal shots.js

## 1. Timing
- `at(phrase, nth)` returns the start time of the nth occurrence of a word or phrase in the voiceover.
  `end(phrase, nth)` returns its end time. Matching ignores case and punctuation. If the phrase occurs more than
  once, pass `nth` or more words, or you get the first match and a warning. Example: `at('blue light has')`
  or `at('blue', 3)`.
- `D` is one drawing (1/12 s). Use it for frame-exact keys: `t0 + 2 * D`.
- `NOW` is the current time, which draw functions also receive as `t`. `VO_END()` is the end of the video:
  the voice end + 1.0 s breath + 1.0 s iris close + 0.3 s on black. `IRIS_START()` is when the closing iris
  begins. Run held loops on the last shot to `VO_END()`.

## 2. Shots and camera
```js
shot(start, {
  draw(lt, t) { ... },                         // lt = seconds into the shot, t = voiceover seconds
  cam: [{ t: 0, x: 270, y: 480, z: 1 }, { t: 3, z: 1.08 }],   // shot-local keys; also r (radians), shake (px)
  tr: 'cut' | 'smear' | 'iris',                // how this shot ends; iris only on the last shot
  cap: 690 | 'top' | false,                   // optional: move this shot's captions (default centre band, y 500; 'top' = y 150; never below 720) or hide them
  iris: [x, y],                                // where the iris closes
});
```
A shot runs until the next shot's start. Wrap each shot in `{ ... }` so its `const`s don't collide. Build pose
keys outside `draw` (once), and only call `poseAt` and the draw functions inside it.

## 3. Characters
```js
const KIT = makeChar({
  shape: 'bean' | 'pear' | 'tall' | 'ball' | 'box' | 'wide' | 'tiny',
  color: RED, size: 1.5, seed: 3,              // seed changes the hand-drawn wobble; give each character its own
  eye: 1, arm: 1,                              // scale eyes / arm length
  legs: true,                                  // false = floats (no feet, no shadow)
  scarf: BLUE,
  hat: { kind: 'beanie' | 'cap' | 'top' | 'bow' | 'sprout' | 'crown', color: BLUE, pom: YEL, band: RED },
  ears: 'cat' | 'round' | 'bunny', earColor,
  tail: 'cat' | 'stub', tailColor,
  hair: 'tuft' | 'spikes', hairColor,
  glasses: true, nose: 'dot' | 'big', cheeks: RED, belly: PAPER, spots: YEL,
  rays: YEL,                                   // sun-like rays around the body
});
const anchors = drawChar(KIT, poseAt(keys, t), { hold(hands, P, A) { /* draw a held prop */ }, shadow: true });
// anchors: { hands: [[x,y],[x,y]], head, top, face, mouth, feet }  (use them to place props and effects)
```
Body sizes at `size` 1: bean 100x124, tall 72x160, ball 116x112, tiny 56x58. The feet sit at the pose's `(x, y)`.

**Pose keys** are `{ t, ...props, ease }`. Each prop interpolates between the keys that set it. `ease` on a key
shapes the move *into* it: `'io'` (default), `'lin'`, `'out'`, `'in'`, `'back'`, or `'hold'` to snap on that
drawing. Keys only need the props that change.

| prop | meaning |
|---|---|
| `x, y` | feet position. `gy` = ground y under a jump (for the shadow) |
| `size` | extra scale on top of the character's size |
| `sx, sy` | squash and stretch (keep `sx * sy` near 1) |
| `lean` | shear: + tips the top to screen-right |
| `facing` | 1 right, -1 left |
| `eyes` | `open wide squint half happy closed squeeze pinch dead` |
| `look` / `lookAt` | pupil offset `[x, y]` (about ±4), or a world point to look at |
| `brow, browY` | brow > 0 angry, < 0 worried; `browY` < 0 raises |
| `mouth` | `smile flat frown smirk wavy o sigh open grin grit` |
| `aL, aR, bend, reach` | arm angles (0 down, + toward screen-right, π up), elbow bend, arm length |
| `arms` | preset (see below), expands to the four arm props |
| `expr` | expression preset (see below); explicit props in the same key win |
| `fL, fR` | lift a foot |
| `scarf` | scarf tail lift (+ down, − flying up) |
| `smear` | `{dir: [x, y], k}` for one drawing; streaks are drawn automatically |
| `talk` | flap the mouth to the voice's words (for an on-screen speaker) |
| `fx` | `'take' 'dust0'..'dust3' 'burst' 'sweat' 'sparkle' 'hearts' 'think' 'zzz' 'anger'`, or an array |
| `breathe, blink` | idle life; `breathe: 0` or `blink: false` turns it off |
| `hide` | skip drawing |

**`ARMS`**: `down up out back fwd hips shrug hug chin pointR pointL pointUpR pointUpL cheer hold`

**`EXPR`**: `neutral happy curious surprised shocked determined sad smug scared sleepy thinking angry love dizzy`

## 4. Actions
Each returns pose keys with `.end` (the time it finishes) and registers its sound cues. Spread them into a key list:
`const keys = [{ t: 0, x: 200, y: 800, expr: 'curious' }, ...A.take(at('But')), ...A.jump(at('jump'), [200, 800], [380, 800])];`

| action | what it does |
|---|---|
| `A.take(t, {hold, eyes, mouth, arms})` | pinch, then pop wide-eyed with take lines, then settle |
| `A.antic(t, {dir, drawings, hold, x, deep})` | squash wind-up, 6 drawings + a trembling hold |
| `A.jump(t, [x, y], [x, y], {height, drawings, upExpr, downExpr, endExpr})` | wind-up, smear, arc, squash landing, dust |
| `A.dash(t, fromX, toX, y, {endExpr})` | lean back, smear across, overshoot on arrival |
| `A.point(t, 'R' \| 'L', {ang, mouth, after, hold})` | pull back 4 drawings, snap past the target, settle |
| `A.cheer(t, y, {height})` | wind-up, hop with both arms up, land |
| `A.shrug(t, {hold})`, `A.sigh(t)`, `A.nod(t, n)`, `A.shake(t, n)` | small acting beats |
| `A.think(t0, t1)`, `A.wave(t0, t1, 'R')`, `A.talk(t0, t1)` | held business between two times |
| `A.walk(t, fromX, toX, y, {speed})` | a bouncing walk |

Actions set absolute `x`/`y` only where they move the character, so put a base key with `x, y` first.

## 5. Ink marks
- `shape(pts, fill, w, seed)` is a closed outline with a flat fill. Pass `fill: null` for a line only.
- `line(pts, w, seed, color)` is an open tapered stroke, smoothed through the points.
- `tube(pts, w, color, seed)` is a coloured stroke with ink edges (rays, rivers, wires, coloured limbs).
- `fillOnly(pts, color, seed)` is a flat shape with no outline.
- `blobPts(cx, cy, rx, ry, seed, n, irr, rot)`, `boxPts(x, y, w, h, seed, rot)`, `wavePts(x0, y0, x1, y1, waves, amp, phase)`,
  and `cloudPts(cx, cy, rx, ry, seed)` generate point lists.
- `rnd(seed, i)` is a stable 0..1 random for placing things. Never use `Math.random()`: frames render in parallel,
  out of order, and every drawing must be repeatable.
- Give every mark its own `seed`, and keep it constant over time. The engine supplies the boil, so a seed that
  changes per frame makes noise, not boil. Colours: `PAPER INK RED BLUE YEL`.

## 6. Props and sets
- Scenery: `band(color, y0, y1, seed)` is a flat colour band from the top down to a hand-cut edge at y1 (sky,
  wall, sea). `ground(y, seed, {fill, grass})`, `hills(y)`, `cloud(x, y, rx, ry, seed)`, `tree(x, y, s, seed)`,
  `rock(x, y, s, seed)`, `moon(x, y, r, seed)`.
- Props: `star(x, y, r, rot, seed, {face})`, `bulb(x, y, r, seed, on)`, `heart(x, y, r, seed)`, `drop(x, y, r, seed)`,
  `arrow([x, y], [x, y], seed, color, bow)`.
- Effects: `burst(x, y, r0, r1, seed, phase)`, `plus(x, y, s, seed)` (sparkle), `speedLines(x, y, [dx, dy], len, spread, seed)`.
- `miniFace(x, y, scale, rot, seed, 'smile' | 'o' | 'frown' | 'happy' | 'sleepy', look)` puts a face on any prop.
  Props that act are this style's secret weapon.
- `gridSafe(() => {...}, k = 0.76)` (thumb.js only) shrinks what you draw inside it about the centre so key marks stay in y 130 to 830, safe for a 3:4 grid crop.
- Thumbnail lettering (`web/thumb.js` only): `bigWord(text, cx, y, size, fill, seed)` draws one big word in the caption
  font with tilted letters, a thick ink outline and a drop shadow. `build.py thumb` renders frame 0 of `thumb.js`.
- Make new props in `cast.js` from the ink marks. The example's `lightWave`, `bit` and `scatter` show the pattern.

## 6b. Sets: ready-made scenes
`setSunny(t)`, `setNight(t)`, `setRoom(t, {wall, floor})`, `setStreet(t)`, `setStage(t, {wall})`, `setDesk(t, {wall, chart})`, `setSpace(t)` and
`setBlank(t, color)` draw a whole background, work in a Short and in a long video, and return the ground y. `setScene(name, t, opts)` picks one by
name. Call one first in `draw()`, then draw the beans and props. See `line-boil-wide/references/wide.md` for what each is for.

## 7. Sound
`musicMood(t, mood, gain)` changes the underscore from second `t` (a crossfade): `curious` (default), `playful`, `upbeat`, `calm`, `serious`, `tense`,
`mystery`, `triumphant`, `silent`. With no calls the whole video plays the `curious` tune. A long video should follow its script with several moods.
`cue(t, kind, gain)`. The kinds are `whoosh boing pop thud squeak sparkle zip plop tick slide_up slide_down deflate ding drum`.
Call it at load time (outside `draw`), next to the keys it belongs with.

## 8. A minimal shots.js
```js
{
  const t0 = 0;
  const kid = [
    { t: 0, x: 200, y: 800, expr: 'curious', look: [3, -3] },
    ...A.take(at('But', 1)),
    ...A.jump(at('jump'), [200, 800], [360, 800], { height: 150 }),
  ];
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.06 }],
    draw(lt, t) {
      band(BLUE, 0, 420, 301);
      ground(800);
      drawChar(KID, poseAt(kid, t));
    },
  });
}
```
