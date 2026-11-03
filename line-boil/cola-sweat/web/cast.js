// What if your sweat was made of Coca-Cola? Cast and topic props.

// Jo: a yellow bean in a red cap and a white tank top (the viewer)
const JO = makeChar({ shape: 'bean', color: YEL, size: 1.5, seed: 11, hat: { kind: 'cap', color: RED }, belly: PAPER });
// the Sun: hot red with yellow rays, floats
const SUN = makeChar({ shape: 'ball', color: RED, rays: YEL, legs: false, size: 0.7, seed: 13, eye: 1.1 });
// a sugar cube: white box, stubborn
const CUBE = makeChar({ shape: 'box', color: PAPER, size: 0.6, seed: 21 });
// skin bacteria: tiny floating blobs
const BUGS = [[31, RED], [32, BLUE], [33, RED], [34, BLUE]].map(([s, col]) => makeChar({ shape: 'tiny', color: col, legs: false, size: 0.6, seed: s, cheeks: col === RED ? YEL : RED, eye: 0.85 }));

const GY = 800;

// Jo's glaze patches and shirt stains, in Jo's own body coordinates (fractions of w and h)
const GLAZE = [[-0.6, -0.62, 0.17], [0.62, -0.78, 0.13], [-0.45, -0.16, 0.15], [0.66, -0.36, 0.14], [0.05, -0.9, 0.11]];
const STAINS = [[0.0, -0.32, 0.16], [0.32, -0.22, 0.12], [-0.22, -0.2, 0.1], [0.18, -0.4, 0.08]];
function patch(c, P, list, k, seed, shine = true) {
  if (k <= 0) return;
  list.forEach(([fx, fy, r], i) => {
    const kk = clamp(k * 1.6 - i * 0.15, 0, 1);
    if (kk <= 0) return;
    const p = tp(c, P, fx * c.w, fy * c.h), rr = r * c.w * c.size * P.size * kk;
    fillOnly(blobPts(p[0], p[1], rr * 1.25, rr, seed + i, 8, 0.2), INK, seed + i, 1);
    if (shine && kk > 0.6) line([[p[0] - rr * 0.6, p[1] - rr * 0.3], [p[0] - rr * 0.1, p[1] - rr * 0.65]], 2.2, seed + 20 + i, PAPER, 0.4);
  });
}

// a cola drop: ink with a shine and yellow fizz bubbles; face uses paper eyes so it reads on ink
function colaDrop(x, y, r, seed, face) {
  drop(x, y, r, seed, INK);
  line([[x - r * 0.42, y - r * 0.7], [x - r * 0.55, y]], Math.max(1.6, r * 0.12), seed + 1, PAPER, 0.4);
  [[0.3, -0.25, 0.15], [0.1, 0.5, 0.11], [-0.25, 0.42, 0.09]].forEach(([fx, fy, rr], i) =>
    shape(blobPts(x + fx * r, y + fy * r, rr * r, rr * r, seed + 3 + i, 6), YEL, Math.max(1.2, r * 0.04), seed + 3 + i, 0.3));
  if (face) inkFace(x, y + r * 0.05, r / 40, seed + 9, face);
}
function inkFace(x, y, s, seed, mood = 'smile') {
  [-1, 1].forEach(side => {
    shape(blobPts(x + side * 11 * s, y - 6 * s, 7 * s, 9 * s, seed + side, 7), PAPER, 2 * Math.sqrt(s), seed + side, 0.6);
    fillOnly(blobPts(x + side * 11 * s + 1.5 * s, y - 5 * s, 3.2 * s, 3.8 * s, seed + 4 + side, 6), INK, seed + 4 + side, 0.3);
  });
  if (mood === 'o') shape(blobPts(x, y + 12 * s, 5 * s, 6 * s, seed + 8, 6), INK, 2, seed + 8, 0.4);
  else line([[x - 9 * s, y + 9 * s], [x, y + (mood === 'frown' ? 6 : 15) * s], [x + 9 * s, y + 9 * s]], 2.8 * Math.sqrt(s), seed + 9, PAPER, 0.5);
}
function sweatDrop(x, y, r, seed, face) {
  drop(x, y, r, seed, BLUE);
  line([[x - r * 0.42, y - r * 0.7], [x - r * 0.55, y]], Math.max(1.6, r * 0.12), seed + 1, PAPER, 0.4);
  if (face) miniFace(x, y + r * 0.1, r / 34, 0, seed + 2, face);
}
// drops thrown off a body: launched one after another from t0, falling under gravity
function spray(t, t0, ox, oy, seed, n, kind = 'cola', rate = 0.09) {
  for (let i = 0; i < n; i++) {
    const ts = t0 + i * rate, lt = t - ts;
    if (lt < 0) continue;
    const side = i % 2 ? 1 : -1, vx = side * (70 + rnd(seed, i) * 150), vy = -(160 + rnd(seed, i + 30) * 200);
    const x = ox + side * 30 + vx * lt, y = oy - 40 * rnd(seed, i + 60) + vy * lt + 450 * lt * lt;
    if (y > GY) continue;
    (kind === 'cola' ? colaDrop : sweatDrop)(x, y, 6 + rnd(seed, i + 90) * 3, seed + i * 5);
  }
}
// a rising wisp of evaporation / heat / stink
function wisp(x, y, len, seed, t, color = INK, w = 2.6) {
  line(wavePts(x, y, x + 4, y - len, 1.4, 6, -t * 9 + seed), w, seed, color, 0.8);
}
function wasp(x, y, s, seed, dir = 1, face = 'happy') {
  const flap = DRAWING % 2, X = dx => x + dx * s * dir;
  shape(blobPts(X(-4), y - 17 * s, 8 * s, (flap ? 14 : 7) * s, seed + 1, 7, 0.1, -0.4 * dir), PAPER, 2.4, seed + 1, 0.8);
  shape(blobPts(X(6), y - 18 * s, 7 * s, (flap ? 13 : 6) * s, seed + 2, 7, 0.1, 0.4 * dir), PAPER, 2.4, seed + 2, 0.8);
  line([[X(-19), y + 1 * s], [X(-30), y + 4 * s]], 2.8, seed + 5);
  shape(blobPts(x, y, 20 * s, 13 * s, seed, 9), YEL, 3, seed, 1);
  line([[X(-7), y - 12 * s], [X(-9), y + 12 * s]], 3.6, seed + 3, INK, 0.6);
  line([[X(3), y - 13 * s], [X(1), y + 12 * s]], 3.6, seed + 4, INK, 0.6);
  line([[X(16), y - 9 * s], [X(22), y - 20 * s]], 2, seed + 7, INK, 0.5);
  miniFace(X(12), y, 0.5 * s, 0, seed + 6, face);
}
function ant(x, y, s, seed) {
  const n = DRAWING % 2;
  [-10, 0, 11].forEach((dx, i) => fillOnly(blobPts(x + dx * s, y - 6 * s, (i === 1 ? 5 : 6.5) * s, 5 * s, seed + i, 6), INK, seed + i, 0.6));
  for (let k = 0; k < 3; k++) line([[x + (-5 + k * 5) * s, y - 6 * s], [x + (-8 + k * 5 + (n ? 3 : -3)) * s, y + 2 * s]], 1.8, seed + 10 + k, INK, 0.4);
  line([[x + 15 * s, y - 9 * s], [x + 21 * s, y - 18 * s]], 1.8, seed + 14, INK, 0.4);
}
function can(x, y, s, seed) {
  if (s <= 0.02) return;
  shape(boxPts(x - 18 * s, y - 52 * s, 36 * s, 52 * s, seed), RED, 3.4, seed, 1);
  line(wavePts(x - 17 * s, y - 26 * s, x + 17 * s, y - 28 * s, 1, 4 * s), 5 * s, seed + 1, PAPER, 0.6, false);
  shape(blobPts(x, y - 52 * s, 17 * s, 4.5 * s, seed + 2, 8, 0.05), PAPER, 2.6, seed + 2, 0.6);
}
function battery(x, y, level, seed) {
  shape(boxPts(x - 32, y - 120, 64, 124, seed), PAPER, 3.8, seed, 1.2);
  shape(boxPts(x - 12, y - 134, 24, 13, seed + 1), INK, 2.4, seed + 1, 0.8);
  for (let k = 0; k < level; k++) shape(boxPts(x - 22, y - 26 - k * 28, 44, 20, seed + 2 + k), level <= 1 ? RED : YEL, 2.6, seed + 2 + k, 0.8);
}
function thermo(x, y, level, seed) {
  shape(boxPts(x - 12, y - 160, 24, 160, seed), PAPER, 3.4, seed, 1);
  fillOnly(boxPts(x - 5, y - 12 - level * 140, 10, level * 140 + 14, seed + 1), RED, seed + 1, 0.6);
  shape(blobPts(x, y + 10, 19, 19, seed + 2, 8), RED, 3.4, seed + 2, 1);
  [0.25, 0.5, 0.75].forEach((f, i) => line([[x + 12, y - 12 - f * 140], [x + 22, y - 12 - f * 140]], 2.2, seed + 5 + i, INK, 0.5));
}
// jog in place: a bouncing run cycle every 4 drawings
function jog(t0, t1, x, y) {
  const keys = [];
  let i = 0;
  for (let t = t0; t < t1 - 1e-6; t += D, i++) {
    const ph = i % 4;
    keys.push({ t, x, y: y - [0, 12, 16, 6][ph], gy: y, sy: [0.9, 1.06, 1.03, 1][ph], sx: [1.08, 0.96, 0.98, 1][ph],
      fL: [0, 12, 6, 0][ph], fR: [6, 0, 0, 12][ph], aL: ph < 2 ? -0.9 : 0.1, aR: ph < 2 ? 0.1 : 0.9, bend: -1.3, reach: 0.68, lean: 0.08, ease: 'hold' });
    if (ph === 0) cue(t, 'tick', 0.3);
  }
  keys.push({ t: t1, y, sy: 1, sx: 1, fL: 0, fR: 0, lean: 0, arms: 'down', ease: 'hold' });
  return keys;
}
