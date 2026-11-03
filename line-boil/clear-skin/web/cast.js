// What if your skin became transparent? Cast and topic props.

// Jo: a yellow bean kid in a blue cap (the viewer's stand-in). JOC is Jo with clear skin.
const JO_SPEC = { shape: 'bean', color: YEL, size: 1.1, seed: 3, hat: { kind: 'cap', color: BLUE }, cheeks: RED };
const JO = makeChar(JO_SPEC);
const JOC = makeChar(Object.assign({}, JO_SPEC, { color: PAPER }));
// the glass frog: a wide, pale, big-eyed frog you can see into
const FROG = makeChar({ shape: 'wide', color: PAPER, size: 1.25, seed: 11, eye: 1.3, ears: 'round', cheeks: RED });
// the lab mouse: a little blue thing with round ears
const MOUSE = makeChar({ shape: 'tiny', color: BLUE, ears: 'round', tail: 'stub', size: 2.1, seed: 13, eye: 0.9 });
// the Sun, floating
const SUN = makeChar({ shape: 'ball', color: YEL, rays: YEL, cheeks: RED, legs: false, size: 0.8, seed: 5, eye: 1.1 });
// skin cells: pale floating blobs; pigment: inky blobs with a pale belly so the mouth reads
const CELLS = [21, 22, 23, 24].map(s => makeChar({ shape: 'tiny', color: PAPER, legs: false, size: 1.35, seed: s, eye: 0.8 }));
const PIGS = [31, 32, 33].map(s => makeChar({ shape: 'tiny', color: INK, belly: PAPER, legs: false, size: 1.3, seed: s, eye: 0.85 }));

const GY = 790;   // ground line

// ---------- helpers ----------
// point at fraction u along a polyline, and the polyline cut off at u
function polyLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
function polyCut(pts, u) {
  const L = polyLen(pts) * clamp(u, 0, 1), out = [pts[0]];
  let acc = 0;
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (acc + d >= L) { const k = d ? (L - acc) / d : 0; out.push([lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)]); return out; }
    acc += d; out.push(pts[i]);
  }
  return out;
}
const polyAt = (pts, u) => { const c = polyCut(pts, u); return c[c.length - 1]; };
// 0 -> 1 pop-in from t0 over dur (with a little overshoot)
const pop = (t, t0, dur = 0.25) => t < t0 ? 0 : EASE.back(clamp((t - t0) / dur, 0, 1));
// 1 -> 0 between t0 and t0 + dur
const fade = (t, t0, dur = 0.3) => 1 - clamp((t - t0) / dur, 0, 1);

// ---------- what you'd see through clear skin ----------
// call from drawChar's hold() so it sits on the body, under the arms and clear of the face.
// o.muscle / o.fat / o.blood are 0..1 (they pop in and the veins grow)
function insides(c, P, t, o = {}) {
  const w = c.w, h = c.h, s = c.size * P.size, lw = Math.sqrt(s), sd = c.seed * 100 + 500;
  const mus = o.muscle ?? 1, fat = o.fat ?? 1, bl = o.blood ?? 1;
  // yellow fat at the hips and sides
  if (fat > 0) [[-0.6, -0.14, 0.22, 0.075], [0.62, -0.15, 0.2, 0.07], [0.02, -0.055, 0.42, 0.045]].forEach(([fx, fy, rx, ry], i) =>
    shape(tpl(c, P, blobPts(w * fx, h * fy, w * rx * fat, h * ry * fat, sd + i, 8, 0.15)), YEL, 2.4 * lw, sd + i, 1));
  // veins: grow out from the heart
  const hc = [w * 0.06, -h * 0.3];
  const veins = [
    [hc, [-w * 0.35, -h * 0.33], [-w * 0.7, -h * 0.4]],
    [hc, [w * 0.4, -h * 0.27], [w * 0.74, -h * 0.38]],
    [hc, [-w * 0.12, -h * 0.17], [-w * 0.4, -h * 0.02]],
    [hc, [w * 0.2, -h * 0.16], [w * 0.42, -h * 0.02]],
  ];
  if (bl > 0) veins.forEach((v, i) => tube(tpl(c, P, polyCut(v, bl)), 4 * lw, RED, sd + 10 + i));
  // muscles: two chest bands and a stack of abs, with fibre lines
  if (mus > 0) {
    [-1, 1].forEach((sg, i) => {
      shape(tpl(c, P, blobPts(w * 0.33 * sg, -h * 0.34, w * 0.26 * mus, h * 0.065 * mus, sd + 20 + i, 9, 0.08, sg * 0.18)), RED, 2.6 * lw, sd + 20 + i, 1);
      if (mus > 0.8) line(tpl(c, P, [[w * 0.18 * sg, -h * 0.35], [w * 0.46 * sg, -h * 0.325]]), 1.8 * lw, sd + 22 + i, INK, 0.6);
    });
    for (let r = 0; r < 3; r++) [-1, 1].forEach((sg, i) =>
      shape(tpl(c, P, blobPts(w * 0.15 * sg, -h * (0.245 - r * 0.062), w * 0.12 * mus, h * 0.024 * mus, sd + 30 + r * 2 + i, 7, 0.1)), RED, 2 * lw, sd + 30 + r * 2 + i, 0.8));
  }
  // the heart, beating about 1.5 times a second
  const beat = (Math.floor(t * 12) % 8) < 2 ? 1.2 : 1;
  const hp = tp(c, P, hc[0], hc[1]);
  heart(hp[0], hp[1], 10 * s * beat, sd + 40);
  // blood cells running along the veins
  if (bl > 0.6 && o.flow !== false) veins.forEach((v, i) => {
    for (let k = 0; k < 2; k++) {
      const u = ((t - (o.flowT ?? 0)) * 0.9 + k / 2 + i * 0.13) % 1, p = tp(c, P, ...polyAt(v, u));
      shape(blobPts(p[0], p[1], 3.6 * lw, 3.2 * lw, sd + 50 + i * 2 + k, 6), RED, 1.8 * lw, sd + 50 + i * 2 + k, 0.5);
    }
  });
}
// the glass frog's insides: a heart, a liver, and blood cells that pack into the liver as `sl` (sleep) goes 0 -> 1
function frogInsides(c, P, t, sl) {
  const w = c.w, h = c.h, s = c.size * P.size, lw = Math.sqrt(s), sd = 1400;
  const liver = [-w * 0.3, -h * 0.13];
  shape(tpl(c, P, blobPts(liver[0], liver[1], w * (0.2 + 0.08 * sl), h * (0.08 + 0.04 * sl), sd, 8, 0.12)), RED, 2.6 * lw, sd, 1);
  line(tpl(c, P, [[w * 0.0, -h * 0.07], [w * 0.3, -h * 0.1], [w * 0.55, -h * 0.07]]), 2.4 * lw, sd + 1, INK, 0.8);   // gut
  const hp = tp(c, P, w * 0.25, -h * 0.2), beat = (Math.floor(t * 12) % 8) < 2 ? 1.2 : 1;
  heart(hp[0], hp[1], 8 * s * beat * (1 - 0.3 * sl), sd + 2);
  for (let i = 0; i < 14; i++) {
    const home = [w * (rnd(sd, i) * 1.5 - 0.75), -h * (0.05 + rnd(sd + 1, i) * 0.24)];
    const jig = Math.sin(t * 6 + i) * 4 * (1 - sl);
    const k = EASE.io(clamp(sl * 1.3 - rnd(sd + 2, i) * 0.3, 0, 1));
    const lp = [liver[0] + (rnd(sd + 3, i) - 0.5) * w * 0.3, liver[1] + (rnd(sd + 4, i) - 0.5) * h * 0.1];
    const p = tp(c, P, lerp(home[0] + jig, lp[0], k), lerp(home[1], lp[1], k));
    shape(blobPts(p[0], p[1], 3.4 * lw, 3 * lw, sd + 10 + i, 6), RED, 1.8 * lw, sd + 10 + i, 0.5);
  }
}
// the mouse's belly window (k 0..1): pale patch with tiny organs
function mouseBelly(c, P, t, k) {
  if (k <= 0) return;
  const w = c.w, h = c.h, s = c.size * P.size, lw = Math.sqrt(s), sd = 1500;
  shape(tpl(c, P, blobPts(0, -h * 0.22, w * 0.62 * k, h * 0.17 * k, sd, 9, 0.06)), PAPER, 2.4 * lw, sd, 1);
  if (k < 0.6) return;
  const hp = tp(c, P, w * 0.15, -h * 0.29), beat = (Math.floor(t * 12) % 6) < 2 ? 1.25 : 1;
  heart(hp[0], hp[1], 4.5 * s * beat, sd + 1);
  shape(tpl(c, P, blobPts(-w * 0.25, -h * 0.25, w * 0.18, h * 0.05, sd + 2, 7)), RED, 1.8 * lw, sd + 2, 0.8);
  line(tpl(c, P, [[-w * 0.3, -h * 0.15], [-w * 0.05, -h * 0.12], [w * 0.1, -h * 0.17], [w * 0.3, -h * 0.13]]), 1.8 * lw, sd + 3, INK, 0.6);
}

// ---------- props ----------
// a standing mirror: red frame, pale glass, a glint
function mirror(x, y, w, h, seed) {
  shape(boxPts(x, y, w, h, seed), RED, 4, seed, 1.2);
  shape(boxPts(x + 13, y + 13, w - 26, h - 26, seed + 1), PAPER, 3, seed + 1, 1);
  line([[x + w - 40, y + 30], [x + w - 26, y + 22]], 2.6, seed + 2);
  line([[x + w - 44, y + 46], [x + w - 26, y + 34]], 2.6, seed + 3);
}
// a ghost: round top, wavy hem, a face
function ghost(x, y, s, t, seed, face = 'o') {
  const pts = [], wob = Math.sin(t * 5) * 3;
  for (let i = 0; i <= 8; i++) { const a = Math.PI + i / 8 * Math.PI; pts.push([x + Math.cos(a) * 34 * s, y - 10 * s + Math.sin(a) * 40 * s]); }
  for (let i = 0; i <= 6; i++) pts.push([x + 34 * s - i / 6 * 68 * s, y + 40 * s + (i % 2 ? -8 : 6) * s + wob * (i % 2 ? 1 : -1)]);
  shape(pts, PAPER, 3.2, seed, 1.2);
  miniFace(x, y - 14 * s, 1.3 * s, 0, seed + 5, face);
}
// a sweet in a twist wrapper; k 0..1 pulls the two wrapper halves apart
function candy(x, y, s, k, seed) {
  shape(blobPts(x, y, 26 * s, 20 * s, seed, 9, 0.05), RED, 3, seed, 1);
  if (k > 0.5) miniFace(x, y, 1.1 * s, 0, seed + 1, 'happy');
  [-1, 1].forEach(sg => {
    const dx = sg * k * 70 * s, dy = -k * 40 * s, a = sg * k * 0.9, cx = x + sg * 6 * s, cy = y;
    const R = ([px, py]) => { const c = Math.cos(a), sn = Math.sin(a); return [cx + dx + px * c - py * sn, cy + dy + px * sn + py * c]; };
    const half = [[0, -24], [sg * 22, -22], [sg * 30, -10], [sg * 52, -24], [sg * 56, 0], [sg * 52, 24], [sg * 30, 10], [sg * 22, 22], [0, 24]].map(([px, py]) => R([px * s, py * s]));
    shape(half, YEL, 3, seed + 3 + sg, 1);
    line([R([sg * 30 * s, -10 * s]), R([sg * 30 * s, 10 * s])], 2.4, seed + 6 + sg);
  });
}
// a sun ray: a yellow squiggle with an optional face on its head; returns the head point
function ray(x0, y0, x1, y1, phase, seed, face, wl = 50, amp = 9) {
  const len = Math.hypot(x1 - x0, y1 - y0);
  if (len < 8) return [x1, y1];
  const pts = wavePts(x0, y0, x1, y1, len / wl, amp, phase, Math.max(8, Math.round(len / wl * 8)));
  tube(pts, 8, YEL, seed);
  const h = pts[pts.length - 1];
  if (face) { shape(blobPts(h[0], h[1], 13, 12, seed + 3, 8), YEL, 3, seed + 3, 1); miniFace(h[0], h[1], 0.6, 0, seed + 4, face); }
  return h;
}
// a ray that travels from a to b, starting at t0, `len` long, at `speed` px/s; gone once it arrives (unless keep)
function shoot(t, t0, a, b, seed, o = {}) {
  if (t < t0) return null;
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]), d = (t - t0) * (o.speed || 520);
  if (d > L + (o.keep ? 1e9 : 0)) return null;
  const head = Math.min(d, L), tail = Math.max(0, head - (o.len || 160));
  const ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L;
  return ray(a[0] + ux * tail, a[1] + uy * tail, a[0] + ux * head, a[1] + uy * head, -t * 10, seed, o.face);
}
// a short scrap of light flying away from (ox, oy), and a spray of them from t0
function bit(ox, oy, a, dist, seed, color = YEL) {
  const x1 = ox + Math.cos(a) * dist, y1 = oy + Math.sin(a) * dist, back = Math.min(dist, 40);
  tube(wavePts(x1 - Math.cos(a) * back, y1 - Math.sin(a) * back, x1, y1, 2.2, 5, seed), 6, color, seed);
}
function scatter(t, t0, ox, oy, seed, n = 5, speed = 300, color = YEL, a0 = 0, spread = TAU) {
  const lt = t - t0;
  if (lt < 0) return;
  for (let i = 0; i < n; i++) {
    const a = a0 + (rnd(seed, i) - (spread < TAU ? 0.5 : 0)) * spread, d = 24 + lt * speed * (0.7 + 0.5 * rnd(seed, i + 9));
    if (d < 700) bit(ox, oy, a, d, seed + i * 7, color);
  }
  if (lt < 2 * D) burst(ox, oy, 18, 36, seed + 50, 0);
}
// a parasol: scalloped red canopy and a handle, top at (x, y)
function parasol(x, y, r, seed) {
  const pts = [];
  for (let i = 0; i <= 10; i++) { const a = Math.PI + i / 10 * Math.PI; pts.push([x + Math.cos(a) * r, y + r * 0.62 + Math.sin(a) * r * 0.62]); }
  for (let i = 1; i < 5; i++) pts.push([x + r - i / 5 * 2 * r, y + r * 0.62 + (i % 2 ? 9 : 0)]);
  shape(pts, RED, 3.4, seed, 1.2);
  line([[x, y + r * 0.62], [x, y + r * 1.5], [x + 10, y + r * 1.6]], 3.6, seed + 1);
}
// a dropper: red rubber bulb, pale glass with yellow dye in it, tip at (x, y)
function dropper(x, y, seed) {
  shape([[x - 13, y - 150], [x + 13, y - 150], [x + 12, y - 30], [x + 3, y], [x - 3, y], [x - 12, y - 30]], PAPER, 3, seed, 1, 4);
  fillOnly([[x - 9, y - 90], [x + 9, y - 90], [x + 8, y - 32], [x + 2, y - 6], [x - 2, y - 6], [x - 8, y - 32]], YEL, seed + 1);
  shape(blobPts(x, y - 178, 20, 30, seed + 2, 9, 0.06), RED, 3.4, seed + 2, 1);
  line([[x - 14, y - 150], [x + 14, y - 150]], 4, seed + 3);
}
// a leaf: blue, with a midrib
function leaf(x0, x1, y, seed) {
  const pts = [], n = 10, cx = (x0 + x1) / 2, hw = (x1 - x0) / 2;
  for (let i = 0; i <= n; i++) { const u = i / n; pts.push([x0 + u * (x1 - x0), y - Math.sin(u * Math.PI) * 26]); }
  for (let i = n - 1; i > 0; i--) { const u = i / n; pts.push([x0 + u * (x1 - x0), y + Math.sin(u * Math.PI) * 30]); }
  shape(pts, BLUE, 3.6, seed, 1.2);
  line([[x0 + 10, y + 2], [cx, y - 3], [x1 - 6, y]], 2.6, seed + 1);
  line([[x0 - 4, y + 2], [x0 - 50, y + 40], [x0 - 70, y + 120]], 3.4, seed + 2);
}
