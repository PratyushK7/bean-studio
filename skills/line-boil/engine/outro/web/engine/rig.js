// rig.js: characters, poses and acting.
// A character is makeChar({...design}); a performance is a list of pose keys in voiceover seconds;
// drawChar(char, poseAt(keys, t)) draws one drawing of it.
const D = 1 / 12;   // one drawing (24 fps on twos)

// ---------- design ----------
const SHAPES = {
  bean: { w: 50, h: 124, round: 2, bias: 0.1 },
  pear: { w: 54, h: 118, round: 2, bias: 0.26 },
  tall: { w: 36, h: 160, round: 2.2, bias: 0.06 },
  ball: { w: 58, h: 112, round: 2, bias: 0 },
  box: { w: 50, h: 120, round: 3.6, bias: 0.03 },
  wide: { w: 72, h: 100, round: 2.4, bias: 0.12 },
  tiny: { w: 28, h: 58, round: 2, bias: 0.08 },
};
// makeChar({shape, color, size, seed, eye, arm, legs, scarf, hat, ears, tail, hair, glasses, nose, cheeks, rays, spots, belly})
function makeChar(spec) {
  const c = Object.assign({ shape: 'bean', color: RED, size: 1, seed: 1, eye: 1, arm: 1, legs: true, feet: INK }, SHAPES[spec.shape || 'bean'], spec);
  c.seed = c.seed | 0 || 1;
  const pts = [], n = 14, ex = 2 / c.round;
  for (let i = 0; i < n; i++) {
    const a = i / n * TAU + 0.11, co = Math.cos(a), si = Math.sin(a), r = 1 + (hash(c.seed, i, 90) - .5) * 0.05;
    pts.push([
      Math.sign(co) * Math.pow(Math.abs(co), ex) * c.w * (1 + c.bias * si) * r,
      -c.h / 2 + Math.sign(si) * Math.pow(Math.abs(si), ex) * c.h / 2 * r,
    ]);
  }
  c.body = pts;
  return c;
}
function halfW(c, y) {
  const s = clamp((y + c.h / 2) / (c.h / 2), -1, 1);
  return c.w * Math.pow(Math.max(0, 1 - Math.pow(Math.abs(s), c.round)), 1 / c.round) * (1 + c.bias * s);
}

// ---------- poses ----------
const DEFAULT_POSE = {
  x: 270, y: 700, gy: null, size: 1, sx: 1, sy: 1, lean: 0, facing: 1,
  eyes: 'open', look: [2.5, 0.5], lookAt: null, brow: 0, browY: 0, mouth: 'smile',
  aL: -0.35, aR: 0.35, bend: -0.5, reach: 0.72, fL: 0, fR: 0,
  scarf: 6, smear: null, talk: false, fx: null, breathe: 1, blink: true, hide: false,
};
// arm presets: angles in radians, 0 = hanging down, + turns toward screen-right, PI = straight up
const ARMS = {
  down: { aL: -0.35, aR: 0.35, bend: -0.5, reach: 0.72 },
  up: { aL: -2.9, aR: 2.9, bend: 0.7, reach: 1 },
  out: { aL: -1.9, aR: 1.9, bend: 0.2, reach: 0.82 },
  back: { aL: -1.25, aR: -0.55, bend: -0.2, reach: 0.78 },
  fwd: { aL: 0.55, aR: 1.25, bend: 0.2, reach: 0.78 },
  hips: { aL: -1.0, aR: 1.0, bend: -1.6, reach: 0.62 },
  shrug: { aL: -1.2, aR: 1.2, bend: 1.4, reach: 0.7 },
  hug: { aL: 1.2, aR: -1.2, bend: 0.35, reach: 0.75 },
  chin: { aL: -0.35, aR: 0.5, bend: -2.6, reach: 0.58 },
  pointR: { aL: -0.35, aR: 1.62, bend: 0.05, reach: 1 },
  pointL: { aL: -1.62, aR: 0.35, bend: 0.05, reach: 1 },
  pointUpR: { aL: -0.35, aR: 2.45, bend: 0.05, reach: 1 },
  pointUpL: { aL: -2.45, aR: 0.35, bend: 0.05, reach: 1 },
  cheer: { aL: -2.5, aR: 2.5, bend: -0.3, reach: 1 },
  hold: { aL: -0.9, aR: 0.9, bend: 1.3, reach: 0.72 },   // carrying something in front at chest height
};
// expression presets: faces act. Put expr:'name' in a key; explicit props in the same key win.
const EXPR = {
  neutral: { eyes: 'open', mouth: 'smile', brow: 0, browY: 0 },
  happy: { eyes: 'happy', mouth: 'grin', brow: 0, browY: -3 },
  curious: { eyes: 'open', mouth: 'flat', brow: -0.3, browY: -5 },
  surprised: { eyes: 'wide', mouth: 'o', brow: 0, browY: -12 },
  shocked: { eyes: 'wide', mouth: 'wavy', brow: -0.6, browY: -14, fx: 'sweat' },
  determined: { eyes: 'squint', mouth: 'grit', brow: 1, browY: 3 },
  sad: { eyes: 'open', mouth: 'frown', brow: -1, browY: -2, look: [0, 3] },
  smug: { eyes: 'half', mouth: 'smirk', brow: 0.5, browY: 0 },
  scared: { eyes: 'wide', mouth: 'wavy', brow: -1, browY: -8, fx: 'sweat' },
  sleepy: { eyes: 'half', mouth: 'flat', brow: -0.2, browY: 2 },
  thinking: { eyes: 'open', mouth: 'wavy', brow: -0.5, browY: -4, look: [-3, -3.5] },
  angry: { eyes: 'squint', mouth: 'frown', brow: 1.2, browY: 4 },
  love: { eyes: 'happy', mouth: 'smile', brow: -0.3, browY: -4, fx: 'hearts' },
  dizzy: { eyes: 'squeeze', mouth: 'wavy', brow: -0.5, browY: -3 },
};
function expandKey(k) {
  let o = {};
  if (k.expr) Object.assign(o, EXPR[k.expr]);
  if (k.arms) Object.assign(o, ARMS[k.arms]);
  Object.assign(o, k);
  delete o.expr; delete o.arms;
  return o;
}
const _tracks = new WeakMap();
function buildTracks(keys) {
  const tr = {};
  keys.map(expandKey).sort((a, b) => a.t - b.t).forEach(k => {
    for (const p in k) {
      if (p === 't' || p === 'ease') continue;
      (tr[p] = tr[p] || []).push({ t: k.t, v: k[p], ease: k.ease || 'io' });
    }
  });
  return tr;
}
// track(keys, t, defaults): numbers and number arrays interpolate between the keys that set them
// (each key's ease shapes the move into it; ease:'hold' snaps on that key). Everything else switches on its key.
function track(keys, t, defaults = {}) {
  let tr = _tracks.get(keys);
  if (!tr) { tr = buildTracks(keys); _tracks.set(keys, tr); }
  const P = Object.assign({}, defaults);
  for (const p in tr) {
    const list = tr[p];
    let i = -1;
    for (let j = 0; j < list.length; j++) if (list[j].t <= t + 1e-6) i = j; else break;
    if (i < 0) { P[p] = list[0].v; continue; }
    const k0 = list[i], k1 = list[i + 1];
    const num = typeof k0.v === 'number' || (Array.isArray(k0.v) && typeof k0.v[0] === 'number');
    if (!k1 || !num || k1.ease === 'hold' || typeof k1.v !== typeof k0.v) { P[p] = k0.v; continue; }
    const u = EASE[k1.ease] ? EASE[k1.ease]((t - k0.t) / (k1.t - k0.t)) : (t - k0.t) / (k1.t - k0.t);
    P[p] = Array.isArray(k0.v) ? k0.v.map((v, n) => lerp(v, k1.v[n], u)) : lerp(k0.v, k1.v, u);
  }
  return P;
}
const poseAt = (keys, t) => track(keys, t, DEFAULT_POSE);

// ---------- drawing ----------
function tp(c, P, px, py) {
  const s = c.size * P.size;
  const x = px * P.facing * s, y = py * s;
  let wx = x * P.sx + P.lean * (-y) * P.sy, wy = y * P.sy;
  if (P.smear) {   // stretch everything along the motion around the body's middle
    const cy = -c.h * s * P.sy / 2, [ux, uy] = P.smear.dir, k = P.smear.k;
    const rx = wx, ry = wy - cy, al = (rx * ux + ry * uy) * k, pe = (-rx * uy + ry * ux) / Math.sqrt(k);
    wx = al * ux - pe * uy; wy = cy + al * uy + pe * ux;
  }
  return [P.x + wx, P.y + wy];
}
const tpl = (c, P, pts) => pts.map(p => tp(c, P, p[0], p[1]));

// drawChar(char, pose, {t, hold(hands, P), shadow}) -> anchors {hands, head, face, mouth, feet}
function drawChar(c, P0, opt = {}) {
  if (P0.hide) return null;
  const t = opt.t !== undefined ? opt.t : NOW;
  const P = Object.assign({}, P0);
  const s = c.size * P.size, lw = Math.sqrt(s);
  const sd = c.seed * 100;
  // life on holds: breathing and blinking
  if (P.breathe && !P.smear) { const b = Math.sin(t * 5.5 + c.seed) * 0.022 * P.breathe; P.sy *= 1 + b; P.sx *= 1 - b * 0.9; }
  if (P.blink && P.eyes === 'open' && ((t + c.seed * 0.73) % 3.1) < D) P.eyes = 'closed';
  if (P.talk) P.mouth = talkMouth(t, c.seed) || P.mouth;
  const w = c.w, h = c.h;
  // shadow
  if (opt.shadow !== false && c.legs) {
    const gy = P.gy == null ? P.y : P.gy, air = Math.max(0, gy - P.y);
    fillOnly(blobPts(P.x + 3, gy + 5, w * 1.1 * s * Math.max(0.3, 1 - air / 220) * Math.sqrt(P.sx), 6.5 * s, sd + 1, 9, 0.08), opt.shadowColor || BLUE, sd + 1);
  }
  if (P.smear) smearStreaks(c, P, sd);
  // behind the body
  if (c.rays) drawRays(c, P, t, sd);
  if (c.tail) drawTail(c, P, sd);
  if (c.ears) drawEars(c, P, sd);
  // feet
  if (c.legs) {
    [-1, 1].forEach(side => {
      const lift = side < 0 ? P.fL : P.fR;
      const f = tp(c, P, side * w * 0.4 * P.facing, 0);
      const gy = P.gy == null ? P.y : P.gy;
      const inAir = gy - P.y > 8;
      fillOnly(blobPts(f[0] + side * 4 * s, f[1] - 3 * s + (inAir ? 9 * s : 0) - lift * s, 14 * s * Math.sqrt(P.sx), 7 * s, sd + 40 + side, 8, 0.1), c.feet, sd + 41 + side);
    });
  }
  // body
  shape(tpl(c, P, c.body), c.color, 4.6 * lw, sd + 2, 1.8, 6);
  if (c.belly) fillOnly(tpl(c, P, blobPts(w * 0.12, -h * 0.3, w * 0.55, h * 0.22, sd + 3, 9, 0.06)), c.belly, sd + 3);
  if (c.spots) [[-0.45, -0.3, 0.16], [0.35, -0.18, 0.12], [-0.1, -0.12, 0.09]].forEach(([fx, fy, r], i) =>
    fillOnly(tpl(c, P, blobPts(w * fx, h * fy, w * r * 1.3, w * r, sd + 5 + i, 7, 0.15)), c.spots, sd + 5 + i));
  line(tpl(c, P, [[-w * 0.64, -h * 0.84], [-w * 0.78, -h * 0.73], [-w * 0.82, -h * 0.61]]), 4.2 * lw, sd + 4, PAPER, 1);
  if (c.scarf) drawScarf(c, P, sd);
  if (c.hat) drawHat(c, P, sd);
  if (c.hair) drawHair(c, P, sd);
  // face
  const fx0 = w * 0.12, ey = -h * 0.68;
  let look = P.look;
  const fc = tp(c, P, fx0, ey);
  if (P.lookAt) { const vx = P.lookAt[0] - fc[0], vy = P.lookAt[1] - fc[1], l = Math.hypot(vx, vy) || 1; look = [vx / l * 4, vy / l * 4]; }
  else look = [look[0] * P.facing, look[1]];
  if (c.cheeks) [-1, 1].forEach(side => fillOnly(tpl(c, P, blobPts(fx0 + side * w * 0.42, ey + 17, 7, 4.5, sd + 60 + side, 7)), c.cheeks, sd + 60 + side));
  drawEye(c, P, fx0 - w * 0.28, ey, -P.facing, look, s, sd + 10);
  drawEye(c, P, fx0 + w * 0.28, ey, P.facing, look, s, sd + 20);
  if (c.glasses) [-1, 1].forEach(side => shape(tpl(c, P, blobPts(fx0 + side * w * 0.28, ey, 13 * c.eye, 13 * c.eye, sd + 70 + side, 9, 0.05)), null, 2.8 * lw, sd + 70 + side, 1));
  if (c.nose) { const n = c.nose === 'big' ? 7 : 3; fillOnly(tpl(c, P, blobPts(fx0 + w * 0.1, -h * 0.57, n, n * 0.85, sd + 75, 7)), c.nose === 'big' ? INK : INK, sd + 75); }
  drawMouth(c, P, fx0 + w * 0.02, -h * 0.47, s, sd + 30);
  // arms (and whatever the hands hold)
  const arms = [-1, 1].map(side => {
    const a = side < 0 ? P.aL : P.aR, a2 = a + side * P.bend, L = s * c.arm * P.reach;
    const sh = tp(c, P, side * w * 0.8 * P.facing, -h * 0.48);
    const e = [sh[0] + Math.sin(a) * 32 * L, sh[1] + Math.cos(a) * 32 * L];
    const hd = [e[0] + Math.sin(a2) * 30 * L, e[1] + Math.cos(a2) * 30 * L];
    return { s: sh, e, h: hd, side };
  });
  const A = { hands: arms.map(a => a.h), head: tp(c, P, 0, -h), face: fc, mouth: tp(c, P, fx0, -h * 0.47), feet: tp(c, P, 0, 0), top: tp(c, P, 0, -h * 1.05), P };
  if (opt.hold) opt.hold(A.hands, P, A);
  arms.forEach((a, i) => {
    line([a.s, a.e, a.h], 4.6 * lw, sd + 80 + i, INK, 1.4);
    shape(blobPts(a.h[0], a.h[1], 7.5 * lw, 7 * lw, sd + 84 + i, 7, 0.1), PAPER, 3 * lw, sd + 84 + i, 1);
  });
  if (P.fx) drawFx(c, P, A, t, sd);
  return A;
}

function drawEye(c, P, ex, ey, side, look, s, seed) {
  const cc = tp(c, P, ex, ey), x = cc[0], y = cc[1];
  const sx = P.sx * s, sy = P.sy * s, k = c.eye, lw = Math.sqrt(s);
  const kind = P.eyes;
  if (kind === 'open' || kind === 'wide' || kind === 'squint' || kind === 'half') {
    const wide = kind === 'wide', lid = kind === 'squint' || kind === 'half';
    const rx = (wide ? 12.5 : 9) * k * sx, ry = (wide ? 16 : 12) * k * sy * (kind === 'squint' ? 0.5 : kind === 'half' ? 0.62 : 1);
    const cy = y + (lid ? 4 * sy : 0);
    shape(blobPts(x, cy, rx, ry, seed, 8, 0.07), PAPER, 3 * lw, seed, 1);
    const pr = (wide ? 3.6 : 4.8) * k * Math.sqrt(s);
    const lx = look[0] * (rx / 10), ly = lid ? Math.max(0, look[1]) * 0.3 : look[1] * (ry / 12);
    fillOnly(blobPts(x + lx, cy + ly, pr * Math.sqrt(P.sx), pr * 1.15 * Math.sqrt(P.sy), seed + 3, 7, 0.1), INK, seed + 3, 0.6);
    fillOnly(blobPts(x + lx - 1.6 * s, cy + ly - 2 * s, 1.5 * s, 1.5 * s, seed + 4, 5), PAPER, seed + 4, 0.3);
    if (lid) {
      const tilt = kind === 'squint' ? (side < 0 ? [-3, 3] : [3, -3]) : [0, 0];
      line([[x - rx - 3, cy - ry + tilt[0]], [x + rx + 3, cy - ry + tilt[1]]], 4.6 * lw, seed + 5, INK, 0.8);
    }
  } else if (kind === 'happy') {
    line([[x - 9 * k * sx, y + 3 * sy], [x, y - 6 * sy], [x + 9 * k * sx, y + 3 * sy]], 3.8 * lw, seed + 6, INK, 0.8);
  } else if (kind === 'closed') {
    line([[x - 9 * k * sx, y], [x, y + 3 * sy], [x + 9 * k * sx, y]], 3.6 * lw, seed + 7, INK, 0.8);
  } else if (kind === 'squeeze') {
    const f = side < 0 ? 1 : -1;
    line([[x - 8 * f * sx, y - 7 * sy], [x + 6 * f * sx, y], [x - 8 * f * sx, y + 7 * sy]], 3.8 * lw, seed + 8, INK, 0.6);
  } else if (kind === 'pinch') {
    fillOnly(blobPts(x + look[0] * 0.4, y, 2.6 * s, 2.6 * s, seed + 9, 6), INK, seed + 9, 0.4);
  } else if (kind === 'dead') {
    line([[x - 6 * sx, y - 6 * sy], [x + 6 * sx, y + 6 * sy]], 3.4 * lw, seed + 12, INK, 0.5);
    line([[x + 6 * sx, y - 6 * sy], [x - 6 * sx, y + 6 * sy]], 3.4 * lw, seed + 13, INK, 0.5);
  }
  // brows: brow > 0 angry (inner end down), brow < 0 worried (inner end up)
  if (kind !== 'squeeze') {
    const by = y - 20 * sy * k + P.browY * sy, kk = P.brow * 4.5;
    const inner = side < 0 ? 1 : -1;
    line([[x - 10 * sx, by + (inner < 0 ? kk : -kk)], [x + 10 * sx, by + (inner > 0 ? kk : -kk)]], 3.4 * lw, seed + 11, INK, 0.9);
  }
}

function talkMouth(t, seed) {
  if (typeof WORDS === 'undefined') return null;
  const n = Math.floor(t * 12);
  for (let i = 0; i < WORDS.length; i++) {
    const w = WORDS[i];
    if (t >= w.s && t < w.e) return ['open', 'o', 'grin', 'open', 'flat'][Math.floor(hash(i, n, seed) * 5)];
  }
  return null;
}
function drawMouth(c, P, mx, my, s, seed) {
  const cc = tp(c, P, mx, my), sx = P.sx * s, sy = P.sy * s, lw = Math.sqrt(s);
  const m = (dx, dy) => [cc[0] + dx * sx * P.facing, cc[1] + dy * sy];
  switch (P.mouth) {
    case 'smile': line([m(-9, -2), m(0, 4), m(9, -2)], 3.4 * lw, seed, INK, 0.8); break;
    case 'flat': line([m(-7, 0), m(7, 1)], 3.2 * lw, seed + 1, INK, 0.8); break;
    case 'frown': line([m(-9, 4), m(0, -2), m(9, 4)], 3.4 * lw, seed + 2, INK, 0.8); break;
    case 'smirk': line([m(-8, 1), m(2, 2), m(10, -4)], 3.4 * lw, seed + 3, INK, 0.8); break;
    case 'wavy': line([m(-10, 1), m(-5, -2), m(0, 1), m(5, -2), m(10, 1)], 3.0 * lw, seed + 4, INK, 0.6); break;
    case 'o': fillOnly(blobPts(cc[0], cc[1] + 2 * sy, 6 * sx, 8 * sy, seed + 5, 7), INK, seed + 5, 0.7); break;
    case 'sigh': fillOnly(blobPts(cc[0], cc[1] + 1, 3.5 * sx, 4 * sy, seed + 6, 6), INK, seed + 6, 0.5); break;
    case 'open':
      shape([m(-10, -3), m(10, -3), m(7, 7), m(-7, 7)], INK, 2.4 * lw, seed + 7, 0.8, 4);
      fillOnly(blobPts(cc[0] + 1 * sx * P.facing, cc[1] + 4.5 * sy, 4.5 * sx, 2.2 * sy, seed + 8, 6), RED, seed + 8, 0.5);
      break;
    case 'grin':
      shape([m(-15, -4), m(15, -4), m(11, 8), m(0, 14), m(-11, 8)], INK, 2.6 * lw, seed + 9, 0.9, 4);
      fillOnly(blobPts(cc[0] + 2 * sx * P.facing, cc[1] + 8 * sy, 6 * sx, 3.5 * sy, seed + 10, 6), c.color === RED ? YEL : RED, seed + 10, 0.6);
      break;
    case 'grit':
      shape([m(-14, -6), m(14, -7), m(15, 6), m(-13, 7)], PAPER, 3.2 * lw, seed + 11, 0.9, 4);
      line([m(-12, 0), m(13, 0)], 2.4 * lw, seed + 12, INK, 0.6, false);
      line([m(-4, -6), m(-4, 6)], 2.2 * lw, seed + 13, INK, 0.5, false);
      line([m(5, -6), m(5, 6)], 2.2 * lw, seed + 14, INK, 0.5, false);
      break;
  }
}

// ---------- accessories ----------
function drawScarf(c, P, sd) {
  const w = c.w, h = c.h, tl = P.scarf, col = c.scarf;
  const y0 = -h * 0.31, y1 = -h * 0.17, hw0 = halfW(c, y0) + 1, hw1 = halfW(c, y1) + 1;
  shape(tpl(c, P, [[-hw0 * 0.85, y0 + 2], [-hw0 * 1.35, y0 + 6 + tl * 0.6], [-hw0 * 1.7, y1 + 3 + tl], [-hw0 * 1.58, y1 + 12 + tl], [-hw0 * 1.18, y1 + 7 + tl * 0.6], [-hw0 * 0.85, y1]]), col, 3.4, sd + 90, 1.4, 5);
  shape(tpl(c, P, [[-hw0, y0 - 2], [0, y0 + 5], [hw0, y0 - 2], [hw1, y1], [0, y1 + 7], [-hw1, y1]]), col, 3.6, sd + 91, 1.3, 5);
}
function drawHat(c, P, sd) {
  const w = c.w, h = c.h, k = c.hat.kind || 'beanie', col = c.hat.color || BLUE;
  if (k === 'beanie') {
    shape(tpl(c, P, [[-0.86 * w, -0.83 * h], [-0.66 * w, -0.99 * h], [0, -1.08 * h], [0.66 * w, -0.99 * h], [0.86 * w, -0.83 * h], [0, -0.8 * h]]), col, 3.6, sd + 92, 1.3, 5);
    shape(tpl(c, P, [[-0.92 * w, -0.86 * h], [0, -0.83 * h], [0.92 * w, -0.86 * h], [0.9 * w, -0.77 * h], [0, -0.74 * h], [-0.9 * w, -0.77 * h]]), PAPER, 3.2, sd + 93, 1.1, 5);
    shape(tpl(c, P, blobPts(0, -1.12 * h, 0.22 * w, 0.2 * w, sd + 94, 8, 0.15)), c.hat.pom || YEL, 3, sd + 94, 1);
  } else if (k === 'cap') {
    shape(tpl(c, P, [[-0.82 * w, -0.8 * h], [-0.6 * w, -0.98 * h], [0, -1.06 * h], [0.6 * w, -0.98 * h], [0.82 * w, -0.8 * h], [0, -0.82 * h]]), col, 3.6, sd + 92, 1.3, 5);
    shape(tpl(c, P, [[0.25 * w, -0.85 * h], [1.3 * w, -0.83 * h], [1.25 * w, -0.76 * h], [0.2 * w, -0.78 * h]]), col, 3.4, sd + 93, 1.1, 4);
  } else if (k === 'top') {
    shape(tpl(c, P, [[-0.55 * w, -0.9 * h], [-0.52 * w, -1.38 * h], [0.52 * w, -1.38 * h], [0.55 * w, -0.9 * h]]), col, 3.6, sd + 92, 1.2, 3);
    shape(tpl(c, P, [[-0.88 * w, -0.93 * h], [0.88 * w, -0.93 * h], [0.86 * w, -0.86 * h], [-0.86 * w, -0.86 * h]]), col, 3.4, sd + 93, 1, 3);
    shape(tpl(c, P, [[-0.53 * w, -1.0 * h], [0.53 * w, -1.0 * h], [0.53 * w, -0.94 * h], [-0.53 * w, -0.94 * h]]), c.hat.band || RED, 2.4, sd + 95, 0.8, 3);
  } else if (k === 'bow') {
    const bx = 0.45 * w, by = -0.98 * h;
    shape(tpl(c, P, [[bx, by], [bx - 0.42 * w, by - 0.2 * h], [bx - 0.4 * w, by + 0.12 * h]]), col, 3.2, sd + 92, 1, 4);
    shape(tpl(c, P, [[bx, by], [bx + 0.42 * w, by - 0.2 * h], [bx + 0.4 * w, by + 0.12 * h]]), col, 3.2, sd + 93, 1, 4);
    shape(tpl(c, P, blobPts(bx, by, 0.1 * w, 0.1 * w, sd + 94, 6)), col, 3, sd + 94, 0.8);
  } else if (k === 'sprout') {
    line(tpl(c, P, [[0, -h], [0.05 * w, -1.14 * h], [0.02 * w, -1.25 * h]]), 3.6, sd + 92);
    shape(tpl(c, P, [[0.03 * w, -1.22 * h], [0.4 * w, -1.36 * h], [0.62 * w, -1.25 * h], [0.32 * w, -1.16 * h]]), col, 3, sd + 93, 1, 5);
    shape(tpl(c, P, [[0.0 * w, -1.18 * h], [-0.36 * w, -1.3 * h], [-0.5 * w, -1.18 * h], [-0.24 * w, -1.12 * h]]), col, 3, sd + 94, 1, 5);
  } else if (k === 'crown') {
    shape(tpl(c, P, [[-0.55 * w, -0.9 * h], [-0.6 * w, -1.18 * h], [-0.3 * w, -1.03 * h], [0, -1.24 * h], [0.3 * w, -1.03 * h], [0.6 * w, -1.18 * h], [0.55 * w, -0.9 * h]]), col, 3.4, sd + 92, 1, 2);
  }
}
function drawHair(c, P, sd) {
  const w = c.w, h = c.h;
  if (c.hair === 'tuft') {
    line(tpl(c, P, [[-0.05 * w, -0.99 * h], [-0.15 * w, -1.12 * h], [-0.35 * w, -1.16 * h]]), 3.6, sd + 96);
    line(tpl(c, P, [[0.05 * w, -1.0 * h], [0.08 * w, -1.16 * h], [0.0, -1.25 * h]]), 3.6, sd + 97);
    line(tpl(c, P, [[0.12 * w, -0.99 * h], [0.3 * w, -1.1 * h], [0.42 * w, -1.08 * h]]), 3.6, sd + 98);
  } else if (c.hair === 'spikes') {
    shape(tpl(c, P, [[-0.8 * w, -0.8 * h], [-0.7 * w, -1.12 * h], [-0.35 * w, -0.96 * h], [-0.05 * w, -1.2 * h], [0.25 * w, -0.97 * h], [0.6 * w, -1.12 * h], [0.82 * w, -0.8 * h], [0, -0.9 * h]]), c.hairColor || INK, 3, sd + 96, 1.2, 3);
  }
}
function drawEars(c, P, sd) {
  const w = c.w, h = c.h, col = c.earColor || c.color;
  [-1, 1].forEach(side => {
    let pts;
    if (c.ears === 'cat') pts = [[side * 0.2 * w, -0.95 * h], [side * 0.72 * w, -1.16 * h], [side * 0.66 * w, -0.78 * h]];
    else if (c.ears === 'bunny') pts = blobPts(side * 0.36 * w, -1.22 * h, 0.17 * w, 0.32 * h, sd + 100 + side, 8, 0.05, side * 0.15);
    else pts = blobPts(side * 0.7 * w, -0.88 * h, 0.3 * w, 0.28 * w, sd + 100 + side, 8, 0.06);
    shape(tpl(c, P, pts), col, 3.6, sd + 101 + side, 1.2, c.ears === 'cat' ? 3 : 5);
  });
}
function drawTail(c, P, sd) {
  const w = c.w, h = c.h, sw = Math.sin(NOW * 4 + c.seed) * 0.12 * h;
  if (c.tail === 'stub') shape(tpl(c, P, blobPts(-1.0 * w, -0.22 * h, 0.22 * w, 0.2 * w, sd + 105)), c.tailColor || c.color, 3.4, sd + 105);
  else tube(tpl(c, P, [[-0.8 * w, -0.18 * h], [-1.35 * w, -0.25 * h], [-1.55 * w, -0.55 * h + sw], [-1.35 * w, -0.78 * h + sw]]), 7, c.tailColor || c.color, sd + 106);
}
function drawRays(c, P, t, sd) {
  const s = c.size * P.size, cx = P.x, cy = P.y - c.h * s * P.sy / 2, r0 = Math.max(c.w, c.h / 2) * s * 1.12, n = 10, rot = t * 0.35;
  for (let i = 0; i < n; i++) {
    const a = rot + i / n * TAU, a1 = a - 0.13, a2 = a + 0.13, r1 = r0 * (1.32 + 0.08 * Math.sin(t * 4 + i));
    shape([[cx + Math.cos(a1) * r0, cy + Math.sin(a1) * r0], [cx + Math.cos(a) * r1, cy + Math.sin(a) * r1], [cx + Math.cos(a2) * r0, cy + Math.sin(a2) * r0]], c.rays, 3, sd + 110 + i, 1.2, 2);
  }
}

// ---------- effects attached to a character ----------
function smearStreaks(c, P, sd) {
  const s = c.size * P.size, [ux, uy] = P.smear.dir, mid = tp(c, P, 0, -c.h / 2);
  const len = c.h * s * P.smear.k * 0.9;
  for (let k = -2; k <= 2; k++) {
    const ox = -uy * k * c.w * s * 0.42, oy = ux * k * c.w * s * 0.42;
    const back = len * (0.7 + 0.3 * rnd(sd, k + 3));
    line([[mid[0] + ox - ux * len * 0.2, mid[1] + oy - uy * len * 0.2], [mid[0] + ox - ux * back * 1.4, mid[1] + oy - uy * back * 1.4]], k % 2 ? 2.4 : 3.2, sd + 120 + k);
  }
}
// fx: 'take' | 'dust0'..'dust3' | 'burst' | 'sweat' | 'sparkle' | 'hearts' | 'think' | 'zzz' | 'anger' or an array of them
function drawFx(c, P, A, t, sd) {
  const list = Array.isArray(P.fx) ? P.fx : [P.fx];
  const s = c.size * P.size, n = Math.floor(t * 12);
  list.forEach(fx => {
    if (fx === 'take') {
      const hc = A.top;
      [-2.4, -1.57, -0.75].forEach((a, i) => {
        const r0 = (n % 2 ? 10 : 18) * s, r1 = 34 * s;
        line([[hc[0] + Math.cos(a) * r0, hc[1] + Math.sin(a) * r0], [hc[0] + Math.cos(a) * r1, hc[1] + Math.sin(a) * r1]], 3.4, sd + 130 + i);
      });
      [-2.75, -0.4].forEach((a, i) => line([[A.face[0] + Math.cos(a) * 55 * s, A.face[1] + Math.sin(a) * 40 * s], [A.face[0] + Math.cos(a) * 72 * s, A.face[1] + Math.sin(a) * 52 * s]], 3, sd + 134 + i));
    } else if (/^dust\d$/.test(fx)) {
      const k = +fx[4], size = [10, 14, 10, 5][k] * s, gy = P.gy == null ? P.y : P.gy;
      [-1, 1].forEach(side => {
        shape(blobPts(P.x + side * (c.w * 1.05 * s + k * 20), gy - k * 7, size * 1.3, size, sd + 140 + side, 8, 0.2), PAPER, 2.8, sd + 141 + side, 1.2);
        if (k < 3) shape(blobPts(P.x + side * (c.w * 1.6 * s + k * 26), gy + 4 - k * 4, size * 0.8, size * 0.65, sd + 145 + side, 7, 0.2), PAPER, 2.4, sd + 146 + side, 1);
      });
      if (k === 0) [-1, 1].forEach(side => line([[P.x + side * c.w * 2.4 * s, gy + 3], [P.x + side * c.w * 1.8 * s, gy + 1]], 3, sd + 149 + side));
    } else if (fx === 'burst') {
      burst(A.head[0], A.head[1] - 10, 30 * s, 52 * s, sd + 150, n % 2);
    } else if (fx === 'sweat') {
      const p = tp(c, P, -c.w * 0.75, -c.h * 0.82), dy = (n % 4) * 3;
      drop(p[0], p[1] + dy, 7 * Math.sqrt(s), sd + 155);
    } else if (fx === 'sparkle') {
      const alt = n % 4 < 2;
      plus(A.head[0] + (alt ? 1 : -1) * c.w * 1.2 * s, A.head[1] + (alt ? 0 : 24), alt ? 7 : 5, sd + 160);
      plus(A.head[0] + (alt ? -1 : 1) * c.w * 1.0 * s, A.head[1] - 18, 4.5, sd + 162);
    } else if (fx === 'hearts') {
      const k = (n % 8) / 8;
      heart(A.head[0] + c.w * 0.9 * s, A.head[1] - 10 - k * 30, 9 + k * 4, sd + 165, RED);
      heart(A.head[0] - c.w * 0.8 * s, A.head[1] + 8 - ((k + 0.5) % 1) * 30, 7, sd + 166, RED);
    } else if (fx === 'think') {
      const b = A.top;
      [[18, -8, 4], [30, -24, 6.5], [46, -46, 9]].forEach(([dx, dy, r], i) => shape(blobPts(b[0] + dx * P.facing * s, b[1] + dy * s, r, r, sd + 170 + i, 7), PAPER, 2.6, sd + 170 + i, 0.8));
    } else if (fx === 'zzz') {
      const b = A.top, k = (n % 6) * 3;
      [[20, -10], [34, -30]].forEach(([dx, dy], i) => line([[b[0] + dx, b[1] + dy - k], [b[0] + dx + 10, b[1] + dy - k], [b[0] + dx, b[1] + dy + 10 - k], [b[0] + dx + 10, b[1] + dy + 10 - k]], 2.6, sd + 175 + i, INK, 0.6, false));
    } else if (fx === 'anger') {
      const p = A.top, o = n % 2 ? 2 : -2;
      [[-6, -6, 6, -1], [6, -6, 1, 6], [6, 6, -6, 1], [-6, 6, -1, -6]].forEach(([x0, y0, x1, y1], i) =>
        line([[p[0] + 30 + x0 + o, p[1] + y0], [p[0] + 30 + x1 + o, p[1] + y1]], 3.4, sd + 180 + i, RED, 0.6));
    }
  });
}

// ---------- actions: return pose keys (absolute seconds) and register their sound cues ----------
// Every big action has 4 to 6 drawings of anticipation and a smear drawing on the fast move.
// Each returns an array with .end = the time the action finishes.
function _keys(list, end) { list.end = end; return list; }
const A = {
  // a take: one drawing of pinched eyes, then wide-eyed stretch with take lines, then settle
  take(t0, o = {}) {
    const hold = o.hold ?? 0.7;
    cue(t0 + D, o.sound || 'squeak');
    return _keys([
      { t: t0, sy: 0.9, sx: 1.08, eyes: 'pinch', browY: 5, mouth: 'flat', ease: 'hold' },
      { t: t0 + D, sy: 1.2, sx: 0.91, expr: 'surprised', arms: 'out', fx: 'take', ease: 'hold' },
      { t: t0 + 2 * D, sy: 1.1, sx: 0.95, browY: -11 },
      { t: t0 + 3 * D, sy: 1.04, sx: 0.98, browY: -9, fx: null, ease: 'hold' },
      { t: t0 + 3 * D + hold, sy: 1, sx: 1, eyes: o.eyes || 'open', mouth: o.mouth || 'flat', browY: o.browY ?? -4, arms: o.arms || 'down' },
    ], t0 + 3 * D + hold);
  },
  // the squash-and-wind-up: 6 drawings down, then n held drawings with a tremble
  antic(t0, o = {}) {
    const dir = o.dir ?? 0, n = o.drawings ?? 6, holdN = o.hold ?? 2, x = o.x, deep = o.deep ?? 1;
    const keys = [];
    for (let i = 1; i <= n; i++) {
      const u = EASE.io(i / n);
      keys.push({ t: t0 + (i - 1) * D, sy: lerp(1.02, 1 - 0.38 * deep, u), sx: lerp(1, 1 + 0.3 * deep, u), lean: lerp(0, -0.14 * (dir || 1) * (dir ? 1 : 0.7), u),
        aL: lerp(-0.4, -1.25 * (dir >= 0 ? 1 : -0.4), u), aR: lerp(0.3, dir >= 0 ? -0.55 : 1.25, u), bend: -0.2, reach: 0.78,
        expr: 'determined', ease: 'lin' });
    }
    for (let j = 0; j < holdN; j++) keys.push({ t: t0 + (n + j) * D, x: x !== undefined ? x + (j % 2 ? 1.8 : -1.8) : undefined, ease: 'hold' });
    keys.forEach(k => { if (k.x === undefined) delete k.x; });
    return _keys(keys, t0 + (n + holdN) * D);
  },
  // jump from [x,y] to [x,y] with an arc `height` high
  jump(t0, from, to, o = {}) {
    const height = o.height ?? 120, N = o.drawings ?? 10, dirX = Math.sign(to[0] - from[0]);
    const keys = [{ t: t0 - D, x: from[0], y: from[1], gy: from[1], ease: 'hold' }];
    const an = A.antic(t0, { dir: dirX, x: from[0], deep: o.deep });
    keys.push(...an);
    const ta = an.end;
    const pos = u => [lerp(from[0], to[0], u), lerp(from[1], to[1], u) - height * 4 * u * (1 - u)];
    for (let i = 1; i <= N; i++) {
      const u = i / N, p = pos(u - 0.5 / N), q = pos(Math.min(1, u + 0.5 / N));
      const vx = q[0] - p[0], vy = q[1] - p[1], l = Math.hypot(vx, vy) || 1;
      const speed = l / (Math.hypot(to[0] - from[0], height * 2) / N);
      const [x, y] = i === 1 ? pos(0.16) : pos(u - 0.04);
      const k = i === 1 ? 1.95 : 1 + 0.32 * Math.min(1, speed);
      keys.push({ t: ta + (i - 1) * D, x, y, gy: lerp(from[1], to[1], u), smear: { dir: [vx / l, vy / l], k }, arms: 'up', lean: 0,
        sx: 1, sy: 1, fx: null, expr: i < N / 2 ? (o.upExpr || 'surprised') : (o.downExpr || 'happy'), ease: 'hold' });
    }
    const tl = ta + N * D;
    cue(ta, 'whoosh'); cue(tl, 'thud');
    keys.push(
      { t: tl, x: to[0], y: to[1], gy: to[1], smear: null, sy: 0.6, sx: 1.4, eyes: 'squeeze', mouth: 'grin', fx: 'dust0', ease: 'hold' },
      { t: tl + D, sy: 1.14, sx: 0.9, eyes: 'happy', fx: 'dust1', ease: 'hold' },
      { t: tl + 2 * D, sy: 0.96, sx: 1.03, fx: 'dust2', ease: 'hold' },
      { t: tl + 3 * D, sy: 1, sx: 1, fx: 'dust3', ease: 'hold' },
      { t: tl + 4 * D, fx: null, expr: o.endExpr || 'happy', arms: o.endArms || 'down', ease: 'hold' },
    );
    return _keys(keys, tl + 4 * D);
  },
  // dash sideways: lean back, smear across, overshoot on arrival
  dash(t0, fromX, toX, y, o = {}) {
    const dir = Math.sign(toX - fromX), keys = [{ t: t0 - D, x: fromX, y, facing: dir, ease: 'hold' }];
    for (let i = 1; i <= 5; i++) {
      const u = EASE.io(i / 5);
      keys.push({ t: t0 + (i - 1) * D, lean: -0.24 * dir * u, sy: lerp(1, 0.84, u), sx: lerp(1, 1.12, u), arms: 'back', expr: 'determined', fL: 6 * u, ease: 'lin' });
    }
    const ts = t0 + 5 * D;
    cue(ts, 'whoosh');
    keys.push(
      { t: ts, x: lerp(fromX, toX, 0.45), smear: { dir: [dir, 0], k: 2.3 }, lean: 0.1 * dir, sy: 1, sx: 1, fL: 0, ease: 'hold' },
      { t: ts + D, x: lerp(fromX, toX, 0.93), smear: { dir: [dir, 0], k: 1.3 }, ease: 'hold' },
      { t: ts + 2 * D, x: toX, smear: null, lean: 0.22 * dir, sy: 0.92, sx: 1.06, fx: 'dust1', expr: o.endExpr || 'happy', arms: 'out', ease: 'hold' },
      { t: ts + 3 * D, lean: -0.08 * dir, sy: 1.04, sx: 0.97, fx: 'dust2', ease: 'hold' },
      { t: ts + 4 * D, lean: 0.03 * dir, sy: 1, sx: 1, fx: null, arms: 'down', ease: 'hold' },
      { t: ts + 6 * D, lean: 0 },
    );
    return _keys(keys, ts + 6 * D);
  },
  // point: pull the arm back for 4 drawings, then snap past the target and settle
  point(t0, side = 'R', o = {}) {
    const ang = o.ang ?? (side === 'R' ? 1.62 : -1.62), key = side === 'R' ? 'aR' : 'aL', other = side === 'R' ? 'aL' : 'aR';
    const sg = side === 'R' ? 1 : -1, keys = [];
    for (let i = 1; i <= 4; i++) {
      const u = EASE.io(i / 4);
      keys.push({ t: t0 + (i - 1) * D, [key]: lerp(sg * 0.35, -sg * 0.5, u), [other]: -sg * 0.35, lean: -0.05 * sg * u, bend: -0.5, reach: 0.72, ease: 'lin' });
    }
    const ts = t0 + 4 * D;
    cue(ts, 'pop', 0.7);
    keys.push(
      { t: ts, [key]: ang + 0.25 * sg, bend: 0.05, reach: 1.05, lean: 0.07 * sg, eyes: 'open', mouth: o.mouth || 'open', browY: -6, ease: 'hold' },
      { t: ts + D, [key]: ang - 0.06 * sg, reach: 0.98, lean: 0.02 * sg, ease: 'hold' },
      { t: ts + 2 * D, [key]: ang, reach: 1, lean: 0, mouth: o.after || 'smile', ease: 'hold' },
    );
    if (o.hold !== undefined) keys.push({ t: ts + 2 * D + o.hold, arms: 'down', browY: 0 });
    return _keys(keys, ts + 2 * D + (o.hold || 0));
  },
  // cheer: wind up, hop with both arms up, land
  cheer(t0, y, o = {}) {
    const hop = o.height ?? 34, keys = [];
    for (let i = 1; i <= 4; i++) {
      const u = EASE.io(i / 4);
      keys.push({ t: t0 + (i - 1) * D, sy: lerp(1, 0.78, u), sx: lerp(1, 1.18, u), arms: 'back', eyes: 'squeeze', mouth: 'grin', ease: 'lin' });
    }
    const ts = t0 + 4 * D;
    cue(ts, 'boing');
    [[-0.55, 1.22, 0.86], [-0.92, 1.08, 0.95], [-1, 1.02, 1], [-0.75, 1.04, 0.98], [0, 0.72, 1.3], [0, 1.1, 0.93], [0, 1, 1]].forEach(([h, sy, sx], i) =>
      keys.push({ t: ts + i * D, y: y + h * hop, gy: y, sy, sx, arms: i < 4 ? 'cheer' : 'up', expr: 'happy', fx: i < 4 ? 'sparkle' : i === 4 ? 'dust1' : null, ease: 'hold' }));
    return _keys(keys, ts + 7 * D);
  },
  shrug(t0, o = {}) {
    const hold = o.hold ?? 0.8;
    return _keys([
      { t: t0, sy: 0.96, ease: 'hold' },
      { t: t0 + D, sy: 1.06, sx: 0.97, arms: 'shrug', brow: -1, browY: -6, mouth: 'wavy', eyes: 'open', look: [-3, -1], ease: 'hold' },
      { t: t0 + 2 * D, sy: 1.03, ease: 'hold' },
      { t: t0 + 2 * D + hold, sy: 1, sx: 1, arms: 'down', brow: 0, browY: 0, mouth: o.after || 'flat', look: [2.5, 0.5] },
    ], t0 + 2 * D + hold);
  },
  sigh(t0) {
    cue(t0 + D, 'deflate', 0.6);
    return _keys([
      { t: t0, sy: 1.05, eyes: 'open', ease: 'hold' },
      { t: t0 + 2 * D, sy: 0.9, sx: 1.08, eyes: 'closed', mouth: 'sigh', brow: -0.8, arms: 'down' },
      { t: t0 + 6 * D, sy: 0.96, sx: 1.03, eyes: 'half', mouth: 'flat' },
    ], t0 + 6 * D);
  },
  nod(t0, n = 2) {
    const keys = [];
    for (let i = 0; i < n; i++) keys.push({ t: t0 + i * 4 * D, lean: 0.07, sy: 0.96, look: [2, 3], eyes: 'closed', ease: 'hold' }, { t: t0 + (i * 4 + 2) * D, lean: -0.02, sy: 1.02, look: [2, 0], eyes: 'open', ease: 'hold' });
    keys.push({ t: t0 + n * 4 * D, lean: 0, sy: 1 });
    return _keys(keys, t0 + n * 4 * D);
  },
  shake(t0, n = 3) {
    const keys = [];
    for (let i = 0; i < n * 2; i++) keys.push({ t: t0 + i * 2 * D, lean: i % 2 ? 0.05 : -0.05, look: [i % 2 ? 4 : -4, 0], eyes: 'closed', mouth: 'frown', ease: 'hold' });
    keys.push({ t: t0 + n * 4 * D, lean: 0, eyes: 'open', mouth: 'flat', look: [2.5, 0.5], ease: 'hold' });
    return _keys(keys, t0 + n * 4 * D);
  },
  think(t0, t1) {
    return _keys([
      { t: t0, arms: 'chin', expr: 'thinking', fx: 'think', ease: 'hold' },
      { t: t1, arms: 'down', expr: 'neutral', fx: null, ease: 'hold' },
    ], t1);
  },
  wave(t0, t1, side = 'R') {
    const key = side === 'R' ? 'aR' : 'aL', sg = side === 'R' ? 1 : -1, keys = [{ t: t0, [key]: sg * 2.6, bend: 0.4, reach: 0.95, expr: 'happy', ease: 'hold' }];
    for (let t = t0 + 2 * D, i = 0; t < t1; t += 2 * D, i++) keys.push({ t, [key]: sg * (i % 2 ? 2.45 : 2.85), bend: i % 2 ? 0.7 : -0.1, ease: 'hold' });
    keys.push({ t: t1, arms: 'down', expr: 'neutral', ease: 'hold' });
    return _keys(keys, t1);
  },
  talk(t0, t1) { return _keys([{ t: t0, talk: true, ease: 'hold' }, { t: t1, talk: false, ease: 'hold' }], t1); },
  // walk: a bouncing step every 4 drawings, arms swinging
  walk(t0, fromX, toX, y, o = {}) {
    const dir = Math.sign(toX - fromX), speed = o.speed ?? 90, dur = Math.abs(toX - fromX) / speed, keys = [];
    const n = Math.max(4, Math.round(dur / D));
    for (let i = 0; i <= n; i++) {
      const ph = i % 4, u = i / n, sw = (Math.floor(i / 4) % 2 ? 1 : -1);
      keys.push({ t: t0 + i * D, x: lerp(fromX, toX, u), y: y - [0, 5, 7, 3][ph], gy: y, sy: [0.95, 1.04, 1.02, 1][ph], facing: dir,
        fL: sw > 0 ? [0, 6, 8, 3][ph] : 0, fR: sw < 0 ? [0, 6, 8, 3][ph] : 0, aL: -0.35 + sw * 0.35, aR: 0.35 + sw * 0.35, lean: 0.04 * dir, ease: 'hold' });
      if (ph === 0 && i > 0) cue(t0 + i * D, 'tick', 0.35);
    }
    keys.push({ t: t0 + (n + 1) * D, fL: 0, fR: 0, lean: 0, sy: 1, arms: 'down', ease: 'hold' });
    return _keys(keys, t0 + (n + 1) * D);
  },
};
