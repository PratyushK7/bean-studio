// Ranking the worst planets to get lost on. Cast and topic props.

// Lost: a yellow bean in a blue beanie (the viewer, stranded)
const LOST = makeChar({ shape: 'bean', color: YEL, size: 1.3, seed: 41, hat: { kind: 'beanie', color: BLUE, pom: RED }, scarf: RED });
// the same bean without the hat, for the Neptune gag
const LOSTH = makeChar({ shape: 'bean', color: YEL, size: 1.3, seed: 41, scarf: RED });

const GY = 800;
function P_X(keys, t) { return poseAt(keys, t).x; }

// a planet with a face: body, optional bands, craters
function planet(x, y, r, color, seed, face = 'smile', kind = '') {
  shape(blobPts(x, y, r, r * 0.97, seed, 14, 0.04), color, 4, seed, 1);
  if (kind === 'craters') [[-0.4, -0.35, 0.16], [0.45, 0.3, 0.2], [-0.3, 0.5, 0.12]].forEach(([fx, fy, rr], i) =>
    shape(blobPts(x + fx * r, y + fy * r, rr * r, rr * r, seed + 5 + i, 8), PAPER, 2.4, seed + 5 + i, 0.6));
  if (kind === 'bands') [-0.5, -0.1, 0.35].forEach((fy, i) =>
    line(wavePts(x - r * 0.9, y + fy * r, x + r * 0.9, y + fy * r, 2, 5, i), 7, seed + 8 + i, RED, 0.5, false));
  if (kind === 'swirl') line(wavePts(x - r * 0.8, y + r * 0.45, x + r * 0.8, y + r * 0.45, 2, 6, 1), 5, seed + 9, PAPER, 0.5, false);
  if (kind === 'acid') [[-0.55, 0.45], [0.2, 0.62], [0.6, 0.2]].forEach(([fx, fy], i) =>
    shape(cloudPts(x + fx * r, y + fy * r, r * 0.3, r * 0.14, seed + 20 + i), PAPER, 2.4, seed + 20 + i, 0.6));
  miniFace(x, y - r * 0.12, r / 30, 0, seed + 2, face);
}

// a rocket flying off (points up-right)
function rocket(x, y, s, seed, t) {
  shape(boxPts(x - 14 * s, y - 22 * s, 28 * s, 54 * s, seed), PAPER, 3, seed, 1);
  shape([[x - 14 * s, y - 22 * s], [x, y - 52 * s], [x + 14 * s, y - 22 * s]], RED, 3, seed + 1, 0.8);
  shape(blobPts(x, y - 4 * s, 7 * s, 7 * s, seed + 2, 8), BLUE, 2.4, seed + 2, 0.6);
  shape([[x - 14 * s, y + 20 * s], [x - 26 * s, y + 40 * s], [x - 14 * s, y + 32 * s]], RED, 2.6, seed + 3, 0.7);
  shape([[x + 14 * s, y + 20 * s], [x + 26 * s, y + 40 * s], [x + 14 * s, y + 32 * s]], RED, 2.6, seed + 4, 0.7);
  const f = DRAWING % 2;
  shape([[x - 8 * s, y + 32 * s], [x, y + (66 + f * 14) * s], [x + 8 * s, y + 32 * s]], YEL, 2.4, seed + 5, 0.7);
}

// thermometer, level 0..1; hot = red mercury, cold = blue
function thermo(x, y, level, seed, color = RED) {
  shape(boxPts(x - 14, y - 220, 28, 220, seed), PAPER, 3.6, seed, 1);
  fillOnly(boxPts(x - 6, y - 14 - level * 190, 12, level * 190 + 16, seed + 1), color, seed + 1, 0.6);
  shape(blobPts(x, y + 12, 22, 22, seed + 2, 8), color, 3.6, seed + 2, 1);
  [0.25, 0.5, 0.75].forEach((f, i) => line([[x + 14, y - 14 - f * 190], [x + 26, y - 14 - f * 190]], 2.4, seed + 5 + i, INK, 0.5));
}

// a rising heat wisp / wind line
function wisp(x, y, len, seed, t, color = INK, w = 2.6) {
  line(wavePts(x, y, x + 4, y - len, 1.4, 6, -t * 9 + seed), w, seed, color, 0.8);
}
function icicles(x, y, n, seed) {
  for (let i = 0; i < n; i++) shape([[x + i * 16 - 6, y], [x + i * 16, y + 22 + (i % 2) * 10], [x + i * 16 + 6, y]], PAPER, 2.2, seed + i, 0.6);
}
// a flying beanie
function hatProp(x, y, rot, seed) {
  const c = Math.cos(rot), s = Math.sin(rot), R = (px, py) => [x + px * c - py * s, y + px * s + py * c];
  shape([R(-24, 0), R(-20, -22), R(0, -30), R(20, -22), R(24, 0)], BLUE, 3, seed, 0.8);
  shape(blobPts(...R(0, -34), 7, 7, seed + 1, 7), RED, 2.4, seed + 1, 0.6);
}
// a lead ingot that melts: k 0..1
function lead(x, y, k, seed) {
  const w = 70 + 50 * k, h = 40 * (1 - 0.8 * k);
  shape(boxPts(x - w / 2, y - h, w, h, seed), PAPER, 3.2, seed, 1);
  if (k < 0.1) line([[x - 16, y - h + 10], [x + 14, y - h + 10]], 2.4, seed + 1, INK, 0.4);
  if (k > 0.2) [0, 1].forEach(i => drop(x - 20 + i * 36, y + 8 + k * 16, 7, seed + 2 + i, PAPER));
}
