// What if you grew 1 cm every second? Cast and topic props.

// Bo: the viewer's stand-in, a tall red bean with a tuft and a yellow scarf. Grows by keying `size`.
const YOU = makeChar({ shape: 'tall', color: RED, size: 1, seed: 3, hair: 'tuft', hairColor: INK, scarf: YEL });
// Pip: the sceptic, a tiny blue bean in glasses who is never impressed
const PIP = makeChar({ shape: 'tiny', color: BLUE, size: 1.1, seed: 7, glasses: true, eye: 1.1 });
// Wadlow: a tall yellow bean in a top hat, the tallest human
const WAD = makeChar({ shape: 'tall', color: YEL, size: 1.6, seed: 11, hat: { kind: 'top', color: BLUE, band: RED }, cheeks: RED });
// scale pieces: red = weight, paper = bone strength
const WGT = makeChar({ shape: 'tiny', color: RED, size: 0.7, seed: 21, legs: true });
const BON = makeChar({ shape: 'tiny', color: PAPER, size: 0.7, seed: 22, legs: true });

const GY = 800;

function dayScene(t) {
  band(BLUE, 0, 470, 301);
  cloud(110 + t * 5, 150, 56, 22, 311);
  cloud(430 - t * 3, 95, 40, 16, 312);
  ground(GY);
}

// a pair of trousers that do NOT grow: waist at (cx, cy), width ~70 * s
function trousers(cx, cy, s = 1, seed = 400) {
  const w = 35 * s, h = 50 * s;
  shape([[cx - w, cy], [cx + w, cy], [cx + w * 1.04, cy + h], [cx + w * 0.14, cy + h], [cx, cy + h * 0.45], [cx - w * 0.14, cy + h], [cx - w * 1.04, cy + h]], BLUE, 3.2, seed, 1, 4);
  shape(boxPts(cx - w, cy, w * 2, 8 * s, seed + 1), YEL, 2.6, seed + 1);
}

// a front door, a bit small for the viewer
function door(x, y, w, h, seed = 410) {
  shape(boxPts(x, y, w, h, seed), BLUE, 3.6, seed);
  shape(boxPts(x + 8, y + 12, w - 16, h * 0.4, seed + 1), PAPER, 2.6, seed + 1);
  fillOnly(blobPts(x + w - 16, y + h * 0.55, 6, 6, seed + 2, 7), YEL, seed + 2);
}

// a tall block of flats: `rows` storeys, two windows each
function flats(x, yTop, w, yBase, rows, seed = 420) {
  shape(boxPts(x, yTop, w, yBase - yTop, seed), PAPER, 3.6, seed);
  const rh = (yBase - yTop) / rows;
  for (let r = 0; r < rows; r++) for (let c = 0; c < 2; c++) {
    shape(boxPts(x + 18 + c * (w - 62), yTop + r * rh + 8, 26, rh - 18, seed + 1 + r * 3 + c), r % 2 ? YEL : BLUE, 2.2, seed + 1 + r * 3 + c);
  }
}

// a wall clock with a fast second hand and a worried face
function clockProp(cx, cy, r, ang, seed = 430) {
  shape(blobPts(cx, cy, r, r, seed, 14, 0.02), PAPER, 4, seed);
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU - Math.PI / 2;
    line([[cx + Math.cos(a) * r * 0.82, cy + Math.sin(a) * r * 0.82], [cx + Math.cos(a) * r * 0.94, cy + Math.sin(a) * r * 0.94]], 3, seed + 1 + i);
  }
  miniFace(cx, cy + r * 0.28, 2.2, 0, seed + 20, 'o');
  line([[cx, cy], [cx + Math.cos(-1.1) * r * 0.5, cy + Math.sin(-1.1) * r * 0.5]], 5, seed + 30);
  line([[cx, cy], [cx + Math.cos(ang) * r * 0.85, cy + Math.sin(ang) * r * 0.85]], 3, seed + 31, RED);
  fillOnly(blobPts(cx, cy, 6, 6, seed + 32, 6), INK, seed + 32);
}

// the sky above and the Earth below, for the head-in-space shots
function spaceScene(t) {
  paper(INK);
  [[60, 110, 9], [200, 70, 7], [330, 150, 8], [480, 90, 10], [90, 260, 6], [500, 300, 7], [40, 400, 6], [230, 230, 5]].forEach(([x, y, r], i) =>
    star(x, y + Math.sin(t * 2 + i) * 3, r, i, 440 + i, { color: i % 2 ? PAPER : YEL }));
  fillOnly(boxPts(-40, 600, 620, 500, 450), BLUE, 450);
  line([[-20, 600], [140, 596], [300, 603], [560, 598]], 3.4, 451, PAPER, 1.2, false);
  ground(890, 460, { fill: PAPER, grass: false });
}
