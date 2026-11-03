// How many balloons would it take to lift you into the sky? Cast and topic props.

// Ollie: a blue pear-shaped kid with glasses and a tuft (the viewer)
const OLLIE = makeChar({ shape: 'pear', color: BLUE, size: 1.3, seed: 41, glasses: true, hair: 'tuft' });
// the lawn-chair pilot: a red box of a man in a yellow cap
const PILOT = makeChar({ shape: 'box', color: RED, size: 0.85, seed: 43, hat: { kind: 'cap', color: YEL }, nose: 'big' });

const GY = 800;
const BCOLS = [RED, YEL, RED, BLUE, YEL, RED, PAPER];

// a balloon centred at (x, y): oval, knot, shine, optional face and string to a point
function balloon(x, y, r, color, seed, o = {}) {
  if (r < 1) return;
  const w = clamp(r * 0.09, 1.8, 3.6), by = y + r * 1.15;
  if (o.string) {
    const [sx, sy] = o.string, mx = (x + sx) / 2 + Math.sin(NOW * 3 + seed) * 8;
    line([[x, by + 6], [mx, (by + sy) / 2], [sx, sy]], 2, seed + 5, INK, 0.8, false);
  }
  shape(blobPts(x, y, r, r * 1.15, seed, 9, 0.04), color, w, seed, 1.2);
  shape([[x - r * 0.12, by + r * 0.16], [x, by - 2], [x + r * 0.12, by + r * 0.16]], color, w * 0.8, seed + 1, 0.5, 2);
  line([[x - r * 0.5, y - r * 0.6], [x - r * 0.64, y - r * 0.1]], Math.max(2, r * 0.11), seed + 2, color === PAPER ? BLUE : PAPER, 0.6);
  if (o.face) miniFace(x, y + r * 0.1, r / 30, 0, seed + 3, o.face, o.look || [0, 0]);
}
// a pop: burst lines and rubber shreds, for about 4 drawings after tp
function popFx(t, tp, x, y, r, color, seed) {
  const lt = t - tp;
  if (lt < 0 || lt > 4 * D) return;
  burst(x, y, r * 0.6 + lt * 200, r * 1.3 + lt * 260, seed, DRAWING % 2, 8);
  for (let i = 0; i < 4; i++) {
    const a = rnd(seed, i) * TAU, d = r * 0.5 + lt * 340;
    shape(blobPts(x + Math.cos(a) * d, y + Math.sin(a) * d + lt * 120, 7, 4, seed + 10 + i, 5, 0.3, a), color, 2, seed + 10 + i, 0.6);
  }
}
// a big bunch, packed in a sunflower spiral. o.born(i) = time balloon i appears, o.gone(i) = time it pops
function bunch(t, cx, cy, n, rad, hand, seed, o = {}) {
  const items = [];
  for (let i = 0; i < n; i++) {
    const rr = 13 * Math.sqrt(i) * rad / 20, a = i * 2.39996;
    items.push({ i, x: cx + Math.cos(a) * rr * 1.15, y: cy + Math.sin(a) * rr * 0.9 + Math.sin(t * 2 + i) * 2 });
  }
  const sw = o.swell || 1;
  const alive = b => (!o.born || t >= o.born(b.i)) && (!o.gone || t < o.gone(b.i));
  if (hand) items.filter(alive).sort((a, b) => b.y - a.y).slice(0, o.strings || 9).forEach((b, k) =>
    line([[b.x, b.y + rad * sw * 1.2], [(b.x + hand[0]) / 2 + (k - 4) * 3, (b.y + hand[1]) / 2], hand], 1.8, seed + 900 + k, INK, 0.6, false));
  items.sort((a, b) => a.y - b.y).forEach(b => {
    if (o.gone && t >= o.gone(b.i)) { popFx(t, o.gone(b.i), b.x, b.y, rad * sw, BCOLS[b.i % BCOLS.length], seed + 500 + b.i); return; }
    let s = 1;
    if (o.born) { const u = clamp((t - o.born(b.i)) / (2 * D), 0, 1); if (u <= 0) return; s = EASE.back(u); }
    const col = o.color || BCOLS[b.i % BCOLS.length];
    balloon(b.x, b.y, rad * s * sw, col, seed + b.i * 7, { face: b.i % 11 === 0 ? (o.face || 'smile') : null });
  });
  return items;
}
function airDots(t, n, seed, o = {}) {
  for (let i = 0; i < n; i++) {
    let x = 30 + rnd(seed, i) * 480, y = 30 + ((rnd(seed, i + 300) * 900 + (o.drift || 0) * t) % 900);
    if (o.push) [x, y] = o.push(x, y);
    if (!o.push || x > -100) fillOnly(blobPts(x, y, 4, 4, seed + i, 6), INK, seed + i, 0.6);
  }
}
function coin(x, y, seed) { shape(blobPts(x, y, 22, 7, seed, 8, 0.05), YEL, 3, seed, 0.6); }
function scale(x, y, ang, seed) {
  shape(boxPts(x - 72, y - 36, 144, 36, seed), PAPER, 3.6, seed, 1);
  line([[x + 70, y - 18], [x + 104, y - 40]], 3.4, seed + 3, INK, 0.6, false);
  shape(blobPts(x + 110, y - 70, 30, 28, seed + 1, 9), PAPER, 3.2, seed + 1, 0.8);
  line([[x + 110, y - 70], [x + 110 + Math.sin(ang) * 24, y - 70 - Math.cos(ang) * 24]], 3.6, seed + 2, RED, 0.3, false);
}
function bus(x, y, s, seed) {
  shape(boxPts(x, y - 92 * s, 220 * s, 78 * s, seed), YEL, 3.8, seed, 1.2);
  for (let k = 0; k < 4; k++) shape(boxPts(x + (14 + k * 46) * s, y - 82 * s, 34 * s, 26 * s, seed + 1 + k), PAPER, 2.6, seed + 1 + k, 0.8);
  line([[x + 4 * s, y - 40 * s], [x + 216 * s, y - 40 * s]], 3, seed + 6, INK, 0.8, false);
  [40, 175].forEach((dx, i) => shape(blobPts(x + dx * s, y - 12 * s, 16 * s, 16 * s, seed + 7 + i, 8), INK, 2, seed + 7 + i, 0.8));
}
function lawnChair(x, y, seed) {
  line([[x - 50, y], [x - 40, y - 44]], 3.4, seed, INK, 1, false);
  line([[x + 50, y], [x + 40, y - 44]], 3.4, seed + 1, INK, 1, false);
  line([[x + 40, y - 44], [x + 62, y - 120]], 3.4, seed + 2, INK, 1, false);
  for (let k = 0; k < 4; k++) shape(boxPts(x - 44 + k * 22, y - 54, 22, 12, seed + 3 + k), k % 2 ? BLUE : RED, 2.2, seed + 3 + k, 0.6);
  for (let k = 0; k < 4; k++) shape(boxPts(x + 36 + k * 5.5, y - 116 + k * 17, 18, 17, seed + 8 + k, -0.28), k % 2 ? BLUE : RED, 2.2, seed + 8 + k, 0.6);
}
function fence(y, seed) {
  for (let x = 20; x < 540; x += 34) line([[x, y], [x + 1, y - 80]], 3, seed + x, INK, 0.8, false);
  line([[0, y - 56], [540, y - 58]], 3, seed + 1, INK, 1, false);
  line([[0, y - 24], [540, y - 22]], 3, seed + 2, INK, 1, false);
}
function clouds(t, speed, seed, n = 4) {
  for (let i = 0; i < n; i++) {
    const x = 60 + rnd(seed, i) * 420, y = ((rnd(seed, i + 9) * 1100 + t * speed) % 1100 + 1100) % 1100 - 100;
    cloud(x, y, 44 + rnd(seed, i + 3) * 26, 18, seed + i);
  }
}
