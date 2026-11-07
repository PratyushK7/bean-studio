// props.js: scenery, props and effects drawn with the ink marks. Add topic props in the project's cast.js.

// ---------- small marks ----------
function plus(x, y, s, seed) {
  line([[x - s, y], [x + s, y + 1]], 2.6, seed);
  line([[x, y - s], [x + 1, y + s]], 2.6, seed + 1);
}
function burst(x, y, r0, r1, seed, phase = 0, n = 7) {
  for (let i = 0; i < n; i++) {
    const a = i / n * TAU + 0.3 + phase * 0.2, a0 = phase ? r0 * 1.2 : r0, a1 = phase ? r1 * 1.1 : r1;
    line([[x + Math.cos(a) * a0, y + Math.sin(a) * a0], [x + Math.cos(a) * a1, y + Math.sin(a) * a1]], 3, seed + i);
  }
}
function drop(x, y, r, seed, color = BLUE) {
  shape([[x, y - r * 1.9], [x + r * 0.9, y - r * 0.2], [x + r * 0.7, y + r * 0.7], [x, y + r], [x - r * 0.7, y + r * 0.7], [x - r * 0.9, y - r * 0.2]], color, 2.6, seed, 0.8, 4);
}
function heart(x, y, r, seed, color = RED) {
  shape([[x, y + r], [x - r * 1.1, y - r * 0.1], [x - r * 0.95, y - r * 0.85], [x - r * 0.35, y - r * 0.95], [x, y - r * 0.45], [x + r * 0.35, y - r * 0.95], [x + r * 0.95, y - r * 0.85], [x + r * 1.1, y - r * 0.1]], color, 2.8, seed, 0.8, 4);
}
// motion lines trailing behind something moving along dir
function speedLines(x, y, dir, len, spread, seed, n = 4) {
  const [ux, uy] = dir;
  for (let k = 0; k < n; k++) {
    const o = (k - (n - 1) / 2) * spread, ox = -uy * o, oy = ux * o, l = len * (0.6 + 0.4 * rnd(seed, k));
    line([[x + ox, y + oy], [x + ox - ux * l, y + oy - uy * l]], k % 2 ? 2.2 : 3, seed + k);
  }
}
// hand-drawn arrow from a to b, bowed by `bow`
function arrow(a, b, seed, color = INK, bow = 0.15) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
  const c = [mx - dy * bow, my + dx * bow];
  line([a, c, b], 4, seed, color);
  const ang = Math.atan2(b[1] - c[1], b[0] - c[0]);
  [0.5, -0.5].forEach((o, i) => line([[b[0] - Math.cos(ang + o) * 16, b[1] - Math.sin(ang + o) * 16], b], 4, seed + 1 + i, color, 1, false));
}

// ---------- props ----------
function star(x, y, r, rot, seed, o = {}) {
  const pts = [];
  for (let i = 0; i < 10; i++) {
    const a = rot - Math.PI / 2 + i * Math.PI / 5, rr = (i % 2 ? r * 0.52 : r) * (1 + (hash(seed, i, 77) - .5) * 0.14);
    pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]);
  }
  shape(pts, o.color || YEL, 3.6, seed, 1.4, 3);
  if (o.face) miniFace(x, y, r / 27, rot, seed + 5, o.face);
}
// a tiny dot-eyed face for props that act: face = 'smile' | 'o' | 'frown' | 'happy' | 'sleepy'
function miniFace(x, y, s, rot, seed, face = 'smile', look = [0, 0]) {
  const c = Math.cos(rot), sn = Math.sin(rot), R = (px, py) => [x + (px * c - py * sn) * s, y + (px * sn + py * c) * s];
  const e1 = R(-6 + look[0], -2 + look[1]), e2 = R(6 + look[0], -2 + look[1]);
  if (face === 'happy') {
    line([R(-9, 0), R(-6, -4), R(-3, 0)], 2.4, seed, INK, 0.5);
    line([R(3, 0), R(6, -4), R(9, 0)], 2.4, seed + 1, INK, 0.5);
  } else if (face === 'sleepy') {
    line([R(-9, -1), R(-3, -1)], 2.4, seed, INK, 0.5);
    line([R(3, -1), R(9, -1)], 2.4, seed + 1, INK, 0.5);
  } else {
    fillOnly(blobPts(e1[0], e1[1], 2.6 * s, 3 * s, seed, 6), INK, seed, 0.5);
    fillOnly(blobPts(e2[0], e2[1], 2.6 * s, 3 * s, seed + 1, 6), INK, seed + 1, 0.5);
  }
  if (face === 'o') fillOnly(blobPts(R(0, 6)[0], R(0, 6)[1], 3 * s, 3.6 * s, seed + 2, 6), INK, seed + 2, 0.4);
  else if (face === 'frown') line([R(-4.5, 8), R(0, 5), R(4.5, 8)], 2.4, seed + 2, INK, 0.6);
  else line([R(-4.5, 4), R(0, 7.5), R(4.5, 4)], 2.4, seed + 2, INK, 0.6);
}
function cloudPts(cx, cy, rx, ry, seed) {
  const pts = [];
  for (let i = 0; i < 14; i++) {
    const a = i / 14 * TAU, r = (i % 2 ? 0.8 : 1.05) * (1 + (hash(seed, i, 3) - .5) * 0.15);
    pts.push([cx + Math.cos(a) * rx * r, cy + Math.sin(a) * ry * r * (Math.sin(a) > 0 ? 0.6 : 1)]);
  }
  return pts;
}
function cloud(x, y, rx, ry, seed, fill = PAPER) { shape(cloudPts(x, y, rx, ry, seed), fill, 2.8, seed, 1.4); }
function bulb(x, y, r, seed, on = true) {
  if (on) burst(x, y - r * 0.2, r * 1.35, r * 1.85, seed + 20, Math.floor(NOW * 12) % 2, 8);
  shape(blobPts(x, y - r * 0.2, r, r * 1.05, seed, 10, 0.04), on ? YEL : PAPER, 3.6, seed, 1.2);
  shape(boxPts(x - r * 0.42, y + r * 0.75, r * 0.84, r * 0.5, seed + 2), PAPER, 3, seed + 2, 1);
  line([[x - r * 0.4, y + r * 1.0], [x + r * 0.4, y + r * 1.0]], 2.4, seed + 3);
}
function tree(x, y, s, seed, fill = BLUE) {
  line([[x, y], [x - 2 * s, y - 40 * s], [x + 2 * s, y - 70 * s]], 8 * s, seed, INK, 1.2, false);
  shape(cloudPts(x, y - 95 * s, 46 * s, 40 * s, seed + 1), fill, 3.4, seed + 1, 1.6);
}
function rock(x, y, s, seed, fill = PAPER) {
  shape([[x - 22 * s, y], [x - 18 * s, y - 14 * s], [x - 4 * s, y - 22 * s], [x + 14 * s, y - 16 * s], [x + 22 * s, y]], fill, 3.2, seed, 1.2, 4);
}
function moon(x, y, r, seed) {
  shape([[x + r * 0.3, y - r], [x - r * 0.6, y - r * 0.6], [x - r, y + r * 0.1], [x - r * 0.5, y + r * 0.85], [x + r * 0.4, y + r], [x - r * 0.05, y + r * 0.35], [x - r * 0.12, y - r * 0.4]], YEL, 3.4, seed, 1.2, 5);
}

// ---------- scenery ----------
function paper(color = PAPER) { ctx.fillStyle = color; ctx.fillRect(-W, -H, W * 3, H * 3); }
// a flat colour band (sky, sea, wall) with a boiling hand-cut lower edge
function band(color, y0, y1, seed = 300) {
  const pts = [[-40, y0 - 400]];
  for (let i = 0; i <= 8; i++) pts.push([-40 + (W + 80) * i / 8, y1 + (rnd(seed, i) - .5) * 8]);
  pts.push([W + 40, y0 - 400]);
  fillDense(prep(pts, true, seed, 1.6, 4), color);
}
function ground(y, seed = 220, o = {}) {
  const pts = [];
  for (let i = 0; i <= 8; i++) pts.push([-30 + (W + 60) * i / 8, y + (rnd(seed, i) - .5) * 4]);
  if (o.fill) fillDense(prep([...pts, [W + 30, H + 400], [-30, H + 400]], true, seed + 1, 1.4, 4), o.fill);
  line(pts, 3.8, seed, INK, 1.4, false);
  if (o.grass !== false) [0.12, 0.3, 0.68, 0.88].forEach((fx, i) => {
    const x = fx * W + (rnd(seed, i + 20) - .5) * 30;
    line([[x - 6, y + 1], [x - 9, y - 12]], 2.4, seed + 30 + i * 3);
    line([[x, y + 1], [x + 1, y - 16]], 2.4, seed + 31 + i * 3);
    line([[x + 6, y + 1], [x + 10, y - 10]], 2.4, seed + 32 + i * 3);
  });
}
function hills(y, seed = 200) {
  line([[-20, y + 60], [60, y - 10], [150, y - 36], [240, y - 6], [300, y + 60]], 2.8, seed);
  line([[250, y + 60], [330, y - 20], [420, y - 44], [500, y - 24], [560, y + 20]], 2.8, seed + 1);
  [[90, y], [118, y - 8], [380, y - 12], [410, y - 20]].forEach(([x, yy], i) => line([[x, yy + 10], [x + 9, yy]], 2, seed + 10 + i));
}
// the sketchy border, in screen space (main.js draws it on top of every drawing)
function frameBorder() {
  line([[6, 14], [W / 2, 10], [W - 6, 13]], 3, 901, INK, 1.2);
  line([[8, H - 12], [W / 2, H - 9], [W - 8, H - 13]], 3, 902, INK, 1.2);
  line([[13, 6], [10, H / 2], [14, H - 6]], 3, 903, INK, 1.2);
  line([[W - 12, 5], [W - 9, H / 2], [W - 13, H - 7]], 3, 904, INK, 1.2);
}

// Thumbnail lettering: one big word, each letter tilted and nudged, thick ink outline and a drop shadow.
// Uses the caption font (CapFont, loaded by main.js). For thumb.js only; videos keep text to the captions.
function bigWord(text, cx, y, size, fill, seed) {
  ctx.save();
  ctx.font = `700 ${size}px CapFont, sans-serif`;
  ctx.lineJoin = 'round';
  const ws = [...text].map(ch => ctx.measureText(ch).width), track = size * 0.02;
  let x = cx - (ws.reduce((a, b) => a + b, 0) + track * (ws.length - 1)) / 2;
  [...text].forEach((ch, i) => {
    const rot = (rnd(seed, i) - 0.5) * 0.14, dy = (rnd(seed, i + 40) - 0.5) * size * 0.1;
    ctx.save();
    ctx.translate(x + ws[i] / 2, y + dy);
    ctx.rotate(rot);
    ctx.lineWidth = size * 0.2; ctx.strokeStyle = INK; ctx.strokeText(ch, -ws[i] / 2, 0);
    ctx.fillStyle = INK; ctx.fillText(ch, -ws[i] / 2 + size * 0.05, size * 0.06);
    ctx.fillStyle = fill; ctx.fillText(ch, -ws[i] / 2, 0);
    ctx.restore();
    x += ws[i] + track;
  });
  ctx.restore();
}

// Thumbnails: a profile grid (Instagram shows a 3:4 centre crop of a 9:16 cover) cuts about an eighth off the top and bottom.
// Draw the headline, the subject and the faces inside gridSafe(() => {...}): they shrink about the centre so every key mark
// sits in y 130 to 830, which survives both the 9:16 feed and the 3:4 grid. Draw the background (paper, sunburst) outside it.
function gridSafe(draw, k = 0.82) {
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.translate(-W / 2, -H / 2);
  draw();
  ctx.restore();
}
