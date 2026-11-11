// ink.js: the hand-drawn line. Every mark goes through here so it boils.
// World is 540 x 960 for a Short (drawn at 2x into the 1080 x 1920 canvas) and 960 x 540 for a long video (1920 x 1080).
// The page sets window.WORLD and window.CANVAS before this file loads; with neither, it is a Short.
// V is the boil variant (0..2). main.js sets it from the drawing number, so every line has exactly 3 jitter
// variants that cycle every drawing, even on held poses.
const _WORLD = (typeof window !== 'undefined' && window.WORLD) || [540, 960];
const _CANVAS = (typeof window !== 'undefined' && window.CANVAS) || [1080, 1920];
const W = _WORLD[0], H = _WORLD[1], CW = _CANVAS[0], CH = _CANVAS[1];
const WIDE = W > H;
// The channel palette. Five flat colours, and a THEME can swap all five at once so the mood fits the topic: the page sets window.THEME
// (build.py writes it from project.json) before this file loads. Each theme keeps the same roles (INK outlines, PAPER whites and base,
// RED the alarm, BLUE the cool body, YEL the light), so every prop, set and bean still reads; only the feeling changes.
const THEMES = {
  classic: { INK: '#1c1c1c', PAPER: '#fffaf0', RED: '#ff595e', BLUE: '#1982c4', YEL: '#ffca3a' },   // bright, friendly: the default
  noir:    { INK: '#0b0b12', PAPER: '#d8d0bd', RED: '#c0272d', BLUE: '#2c4a6e', YEL: '#d9a93a', DEEP: '#141a2c' },   // dark and dread: horror, extinction, crime, "what if it all goes wrong"
  sepia:   { INK: '#2b211a', PAPER: '#f1e4c8', RED: '#b8452f', BLUE: '#4f7a86', YEL: '#d49a3a' },   // old and warm: history, nostalgia, how it used to be
  soft:    { INK: '#2a2a33', PAPER: '#fff6ee', RED: '#f28b94', BLUE: '#7fb8d8', YEL: '#ffd98a' },   // gentle and pastel: sleep, kids, kindness, calm
  hype:    { INK: '#14101c', PAPER: '#fffdf2', RED: '#ff3b4a', BLUE: '#2563ff', YEL: '#ffe11a' },   // loud and saturated: money, hustle, contests, hype
};
const THEME_NAME = (typeof window !== 'undefined' && THEMES[window.THEME]) ? window.THEME : 'classic';
const { INK, PAPER, RED, BLUE, YEL } = THEMES[THEME_NAME];
const DEEP = THEMES[THEME_NAME].DEEP || null;   // a dark theme's room, sky and wall colour: sets use it instead of their bright default (see _dk in sets.js)
const TAU = Math.PI * 2;
let ctx = null;
let V = 0;

// ---------- numbers ----------
function hash(a, b, c) {
  let h = Math.imul(a | 0, 0x27d4eb2d) ^ Math.imul((b | 0) + 0x3c6ef372, 0x165667b1) ^ Math.imul((c | 0) + 0x5bd1e995, 0x9e3779b1);
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function vnoise(seed, x, period) {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  const i0 = period ? ((i % period) + period) % period : i;
  const i1 = period ? (i0 + 1) % period : i + 1;
  const a = hash(seed, i0, V + 31), b = hash(seed, i1, V + 31);
  return a + (b - a) * u;
}
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const EASE = {
  lin: t => t,
  io: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  out: t => 1 - Math.pow(1 - t, 3),
  in: t => t * t * t,
  back: t => { const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
};
// a stable 0..1 random for prop placement: rnd(seed, i)
const rnd = (seed, i = 0) => hash(seed, i, 4242);

// ---------- strokes ----------
function catmull(p, closed, sub) {
  const out = [], n = p.length;
  if (n < 2) return p.slice();
  const get = i => closed ? p[(i + n) % n] : p[Math.max(0, Math.min(n - 1, i))];
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    for (let s = 0; s < sub; s++) {
      const t = s / sub, t2 = t * t, t3 = t2 * t;
      const f = k => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3);
      out.push([f(0), f(1)]);
    }
  }
  if (!closed) out.push(p[n - 1]);
  return out;
}
// jitter the control points for this boil variant, then smooth them
function prep(pts, closed, seed, amp, sub) {
  const j = pts.map((p, i) => [
    p[0] + (hash(seed, i * 2, V + 7) - .5) * 2 * amp,
    p[1] + (hash(seed, i * 2 + 1, V + 7) - .5) * 2 * amp,
  ]);
  return catmull(j, closed, sub);
}
// a variable-width ink line, built as a filled ribbon. Open lines taper at both ends.
function ribbon(p, closed, w, seed, taper, color) {
  const n = p.length;
  if (n < 2) return;
  const L = [], R = [], per = closed ? 4 : 3;
  for (let i = 0; i < n; i++) {
    const a = closed ? p[(i - 1 + n) % n] : p[Math.max(0, i - 1)];
    const b = closed ? p[(i + 1) % n] : p[Math.min(n - 1, i + 1)];
    const tx = b[0] - a[0], ty = b[1] - a[1], l = Math.hypot(tx, ty) || 1;
    const nx = -ty / l, ny = tx / l;
    const t = closed ? i / n : i / (n - 1);
    let ww = w * (0.5 + 0.95 * vnoise(seed + 13, t * per, closed ? per : 0));
    if (!closed && taper) ww *= 0.18 + 0.82 * Math.pow(Math.sin(Math.PI * t), 0.55);
    L.push([p[i][0] + nx * ww / 2, p[i][1] + ny * ww / 2]);
    R.push([p[i][0] - nx * ww / 2, p[i][1] - ny * ww / 2]);
  }
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(L[0][0], L[0][1]);
  for (let i = 1; i < n; i++) ctx.lineTo(L[i][0], L[i][1]);
  if (closed) {
    ctx.closePath();
    ctx.moveTo(R[n - 1][0], R[n - 1][1]);
    for (let i = n - 2; i >= 0; i--) ctx.lineTo(R[i][0], R[i][1]);
  } else {
    for (let i = n - 1; i >= 0; i--) ctx.lineTo(R[i][0], R[i][1]);
  }
  ctx.closePath();
  ctx.fill('nonzero');
}
function fillDense(p, color, dx = 0, dy = 0) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(p[0][0] + dx, p[0][1] + dy);
  for (let i = 1; i < p.length; i++) ctx.lineTo(p[i][0] + dx, p[i][1] + dy);
  ctx.closePath();
  ctx.fill();
}

// ---------- the four marks everything is made of ----------
// shape: a closed outline with a flat fill that sits slightly off the line (printed-cel misregistration)
function shape(pts, fill, w = 3.6, seed = 1, amp = 1.6, sub = 6) {
  const p = prep(pts, true, seed, amp, sub);
  if (fill) {
    const dx = (hash(seed, 1, V + 50) - .5) * 2.6, dy = (hash(seed, 2, V + 50) - .5) * 2.2;
    fillDense(p, fill, dx, dy);
  }
  if (w > 0) ribbon(p, true, w, seed, false, INK);
}
// fillOnly: a flat shape with no outline (pupils, shadows, cheeks)
function fillOnly(pts, color, seed = 1, amp = 1.3) {
  fillDense(prep(pts, true, seed, amp, 5), color);
}
// line: an open stroke that tapers at both ends
function line(pts, w = 3.4, seed = 1, color = INK, amp = 1.6, taper = true) {
  ribbon(prep(pts, false, seed, amp, 6), false, w, seed, taper, color);
}
// tube: a coloured stroke with ink edges (light rays, rivers, wires, tails, noodle limbs in colour)
function tube(pts, w, color, seed = 1, amp = 1.4) {
  const p = prep(pts, false, seed, amp, 6);
  ribbon(p, false, w + 5, seed, true, INK);
  ribbon(p, false, w, seed + 1, true, color);
}

// ---------- point generators ----------
function blobPts(cx, cy, rx, ry, seed = 1, n = 9, irr = 0.06, rot = 0) {
  const pts = [], c = Math.cos(rot), s = Math.sin(rot);
  for (let i = 0; i < n; i++) {
    const a = i / n * TAU + (hash(seed, i, 99) - .5) * 0.3;
    const r = 1 + (hash(seed, i, 98) - .5) * irr * 2;
    const x = Math.cos(a) * rx * r, y = Math.sin(a) * ry * r;
    pts.push([cx + x * c - y * s, cy + x * s + y * c]);
  }
  return pts;
}
// a box that is never quite a box
function boxPts(x, y, w, h, seed = 1, rot = 0) {
  const cx = x + w / 2, cy = y + h / 2, c = Math.cos(rot), s = Math.sin(rot);
  const raw = [[-w / 2, -h / 2], [0, -h / 2 - 1.5], [w / 2, -h / 2], [w / 2 + 1, 0], [w / 2, h / 2], [0, h / 2 + 1], [-w / 2, h / 2], [-w / 2 - 1, 0]];
  return raw.map(([px, py], i) => {
    const jx = px + (rnd(seed, i) - .5) * 3, jy = py + (rnd(seed, i + 9) - .5) * 3;
    return [cx + jx * c - jy * s, cy + jx * s + jy * c];
  });
}
// points along a sine squiggle from (x0,y0) to (x1,y1)
function wavePts(x0, y0, x1, y1, waves, amp, phase = 0, n = 0) {
  const len = Math.hypot(x1 - x0, y1 - y0), ux = (x1 - x0) / len, uy = (y1 - y0) / len;
  n = n || Math.max(6, Math.round(waves * 4));
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, o = Math.sin(t * waves * TAU + phase) * amp;
    pts.push([x0 + ux * len * t - uy * o, y0 + uy * len * t + ux * o]);
  }
  return pts;
}
