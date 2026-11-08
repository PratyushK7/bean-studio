// Does Instagram actually listen to you? Cast and props.
// YOU: a blue bean in a red beanie. NOTE: a yellow pear with glasses and a notebook (the patient note-taker).
const YOU = makeChar({ shape: 'bean', color: BLUE, size: 1.5, seed: 21, hat: { kind: 'beanie', color: RED, pom: YEL } });
const NOTE = makeChar({ shape: 'pear', color: YEL, size: 1.45, seed: 22, glasses: true, hair: 'tuft', hairColor: INK });
const FANS = [31, 32, 33, 34, 35].map((s, i) => makeChar({ shape: 'tiny', color: [RED, PAPER, BLUE, YEL, RED][i], size: 0.9, seed: s, eye: 0.9 }));

const GY = 800;

function phone(x, y, w, h, seed) {
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed), INK, 4, seed);
  shape(boxPts(x - w / 2 + 8, y - h / 2 + 14, w - 16, h - 28, seed + 1), PAPER, 3, seed + 1);
}
function sneaker(x, y, s, col, seed) {
  shape([[x - 40 * s, y + 18 * s], [x - 40 * s, y - 14 * s], [x - 8 * s, y - 22 * s], [x + 6 * s, y - 4 * s], [x + 42 * s, y + 4 * s], [x + 44 * s, y + 18 * s]], col, 4, seed);
  line([[x - 40 * s, y + 18 * s], [x + 44 * s, y + 18 * s]], 5, seed + 1, INK);
  line([[x - 4 * s, y - 14 * s], [x + 10 * s, y - 2 * s]], 3, seed + 2, INK);
}
function notebook(p, seed, ticks = 0) {
  const [x, y] = p;
  shape(boxPts(x - 30, y - 38, 60, 76, seed, -0.1), PAPER, 4, seed);
  for (let i = 0; i < ticks; i++) {
    const c = i % 3, r = Math.floor(i / 3);
    line([[x - 18 + c * 14, y - 24 + r * 12], [x - 18 + c * 14, y - 12 + r * 12]], 3.5, seed + 5 + i, INK);
  }
}
function stopwatch(x, y, r, t, seed) {
  shape(blobPts(x, y, r, r, seed, 12), PAPER, 5, seed);
  shape(boxPts(x - 8, y - r - 14, 16, 12, seed + 1), INK, 3, seed + 1);
  const a = t * 5;
  line([[x, y], [x + Math.sin(a) * r * 0.7, y - Math.cos(a) * r * 0.7]], 4, seed + 2, RED);
}
function shoeFeed(x, y, t0, t, seed) {
  phone(x, y, 190, 330, seed);
  [[0, -95], [0, 15], [0, 125]].forEach(([dx, dy], i) => {
    if (t > t0 + i * 0.2) sneaker(x + dx, y + dy, 1.3, [RED, YEL, BLUE][i], seed + 10 + i);
  });
}
// a microphone with an indicator dot that can light up red
function mic(x, y, s, seed, lit = false) {
  shape(blobPts(x, y - 20 * s, 26 * s, 38 * s, seed, 10), PAPER, 5, seed);
  line([[x - 14 * s, y - 28 * s], [x + 14 * s, y - 28 * s]], 3, seed + 1, INK);
  line([[x - 14 * s, y - 14 * s], [x + 14 * s, y - 14 * s]], 3, seed + 2, INK);
  line([[x - 40 * s, y - 6 * s], [x - 36 * s, y + 24 * s], [x, y + 36 * s], [x + 36 * s, y + 24 * s], [x + 40 * s, y - 6 * s]], 5, seed + 3, INK);
  line([[x, y + 36 * s], [x, y + 66 * s]], 5, seed + 4, INK);
  line([[x - 28 * s, y + 66 * s], [x + 28 * s, y + 66 * s]], 5, seed + 5, INK);
  if (lit) shape(blobPts(x + 54 * s, y - 70 * s, 14 * s, 14 * s, seed + 6, 8), RED, 4, seed + 6);
}
// a battery with a fill level 0..1
function battery(x, y, level, seed) {
  shape(boxPts(x - 70, y - 36, 140, 72, seed), PAPER, 5, seed);
  shape(boxPts(x + 70, y - 14, 14, 28, seed + 1), INK, 3, seed + 1);
  if (level > 0.03) shape(boxPts(x - 62, y - 28, 124 * level, 56, seed + 2), level > 0.35 ? YEL : RED, 3, seed + 2);
}
// a little ad card
function adCard(x, y, w, h, col, seed) {
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed, 0.03), PAPER, 4, seed);
  shape(blobPts(x, y - h * 0.1, w * 0.26, h * 0.24, seed + 1, 8), col, 3, seed + 1);
  line([[x - w * 0.3, y + h * 0.32], [x + w * 0.3, y + h * 0.32]], 3, seed + 2, INK);
}
