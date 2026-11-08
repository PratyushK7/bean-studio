// Why does the weekend fly by faster? Cast and topic props.

// You: a blue bean in a yellow beanie (the viewer's stand-in)
const YOU = makeChar({ shape: 'bean', color: BLUE, size: 1.4, seed: 31, hat: { kind: 'beanie', color: YEL, pom: RED } });
// Brain: a floating red wide bean with glasses, the sceptic who only guesses
const BRAIN = makeChar({ shape: 'wide', color: RED, legs: false, size: 1.2, seed: 32, glasses: true, cheeks: PAPER });
// Boss: a tall yellow bean who loves meetings
const BOSS = makeChar({ shape: 'tall', color: YEL, size: 1.2, seed: 33, nose: 'big', hair: 'spikes', hairColor: INK });

const GY = 800;   // ground line

// a clock with a face. h and m are hand angles in radians (0 = twelve, clockwise).
function clockProp(x, y, r, h, m, seed, mood) {
  shape(blobPts(x, y, r, r, seed, 14, 0.02), PAPER, 6, seed);
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU, s = Math.sin(a), c = -Math.cos(a);
    line([[x + s * r * 0.78, y + c * r * 0.78], [x + s * r * 0.9, y + c * r * 0.9]], 4, seed + 1 + i);
  }
  if (h !== null) {
    line([[x, y], [x + Math.sin(h) * r * 0.5, y - Math.cos(h) * r * 0.5]], 7, seed + 20);
    line([[x, y], [x + Math.sin(m) * r * 0.75, y - Math.cos(m) * r * 0.75]], 5, seed + 21);
  }
  if (mood) miniFace(x, y + r * 0.38, r / 40, 0, seed + 30, mood);
}

// tally marks: n strokes in groups of five, starting at (x, y)
function tally(x, y, n, seed, color) {
  for (let i = 0; i < n; i++) {
    const g = Math.floor(i / 5), k = i % 5;
    if (k < 4) line([[x + g * 62 + k * 12, y], [x + g * 62 + k * 12 + 2, y + 40]], 5, seed + i, color);
    else line([[x + g * 62 - 6, y + 34], [x + g * 62 + 52, y + 6]], 5, seed + i, color);
  }
}

// a small yellow "second": a pill with a tick on it
function secondBlob(x, y, r, seed) {
  shape(blobPts(x, y, r, r * 0.8, seed, 8, 0.1), YEL, 4, seed);
  line([[x, y - r * 0.5], [x, y]], 3, seed + 1);
}

// a desk
function desk(x, y, w, seed) {
  shape(boxPts(x, y, w, 26, seed), BLUE, 5, seed);
  line([[x + 24, y + 26], [x + 24, y + 150]], 8, seed + 1);
  line([[x + w - 24, y + 26], [x + w - 24, y + 150]], 8, seed + 2);
}
