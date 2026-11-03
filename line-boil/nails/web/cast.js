// What if your fingernails never stopped growing? Cast and topic props.

// Kit: a blue bean in a red cap (the viewer's stand-in)
const KIT = makeChar({ shape: 'bean', color: BLUE, size: 1.3, seed: 3, hat: { kind: 'cap', color: RED }, cheeks: RED });
// the Root: a tiny red nail-maker that lives under the skin
const ROOT = makeChar({ shape: 'tiny', color: RED, legs: false, size: 1.3, seed: 6, eye: 0.9 });

const GY = 800;   // floor line

// a capsule outline from (x0,y0) to (x1,y1) with radius r
function capPts(x0, y0, x1, y1, r) {
  const a = Math.atan2(y1 - y0, x1 - x0), pts = [];
  for (let i = 0; i <= 6; i++) { const b = a - Math.PI / 2 + i / 6 * Math.PI; pts.push([x1 + Math.cos(b) * r, y1 + Math.sin(b) * r]); }
  for (let i = 0; i <= 6; i++) { const b = a + Math.PI / 2 + i / 6 * Math.PI; pts.push([x0 + Math.cos(b) * r, y0 + Math.sin(b) * r]); }
  return pts;
}

// the path of a growing nail: starts at (x,y) heading a0, length L.
// curl winds it into a spiral (tighter towards the end), sag bends it towards the floor.
function nailPath(x, y, a0, L, curl = 0, sag = 0, dir = 1) {
  const pts = [[x, y]];
  if (L < 3) return [[x, y], [x + Math.cos(a0) * 3, y + Math.sin(a0) * 3]];
  const n = Math.max(4, Math.ceil(L / 7)), ds = L / n, turns = curl * 5.2;
  let a = a0, px = x, py = y;
  for (let i = 1; i <= n; i++) {
    const u = i / n;
    a += dir * turns * 2 * u / n;
    const h = lerp(a, Math.PI / 2, clamp(sag * u, 0, 1));
    px += Math.cos(h) * ds; py += Math.sin(h) * ds;
    pts.push([px, py]);
  }
  return pts;
}
// a nail: a yellow tube along a path, with an optional face on its tip
function nail(pts, w, seed, face, fs = 0.6) {
  tube(pts, w, YEL, seed);
  if (face) { const h = pts[pts.length - 1]; miniFace(h[0], h[1] - 1, fs, 0, seed + 5, face); }
  return pts[pts.length - 1];
}
// a crack across a nail at point p
function crack(p, s, seed) {
  line([[p[0] - 9 * s, p[1] - 4 * s], [p[0] - 2 * s, p[1] + 3 * s], [p[0] + 3 * s, p[1] - 3 * s], [p[0] + 10 * s, p[1] + 4 * s]], 2.6, seed);
}

// the big close-up hand, back of the hand, fingers up. o: {ext, curl, sag, face, cuff}
// ext is nail length past the fingertip in hand units (a finger is about 80). Returns the nail tips.
const FINGERS = [[-42, 70, -1], [-14, 82, -1], [14, 78, 1], [42, 62, 1]];
function bigHand(cx, cy, s, o = {}) {
  const ext = o.ext || 0, by = cy - 50 * s, tips = [];
  FINGERS.forEach(([fx, len], i) => shape(capPts(cx + fx * s, by + 20 * s, cx + fx * s * 1.05, by - len * s, 13 * s), PAPER, 4.2, 900 + i));
  shape(capPts(cx - 55 * s, cy + 15 * s, cx - 92 * s, cy - 30 * s, 14 * s), PAPER, 4.2, 905);
  shape(blobPts(cx, cy + 4 * s, 64 * s, 66 * s, 906, 11, 0.04), PAPER, 4.4, 906);
  line([[cx - 30 * s, cy - 30 * s], [cx - 22 * s, cy - 34 * s]], 2.4, 907);
  line([[cx + 18 * s, cy - 33 * s], [cx + 26 * s, cy - 30 * s]], 2.4, 908);
  if (o.cuff !== false) shape(boxPts(cx - 60 * s, cy + 56 * s, 120 * s, 30 * s, 909), RED, 4, 909);
  FINGERS.forEach(([fx, len, dir], i) => {
    const tx = cx + fx * s * 1.05, ty = by - len * s;
    const L = ext * s * (1 - i * 0.04);
    const pts = nailPath(tx, ty - 4 * s, -Math.PI / 2, L, o.curl || 0, o.sag || 0, dir);
    const face = o.face ? (Array.isArray(o.face) ? o.face[i] : o.face) : null;
    if (L > 6) nail(pts, 13 * s, 910 + i * 10, face, 0.55 * s);
    shape(capPts(tx, ty + 14 * s, tx, ty - 3 * s, 9 * s), YEL, 3, 915 + i * 10);
    if (L <= 6 && face) miniFace(tx, ty + 5 * s, 0.42 * s, 0, 916 + i * 10, face);
    tips.push(pts);
  });
  return tips;
}

// Snip, the nail clippers: a red body, a paper lever, a face. open 0..1 lifts the lever.
function snip(x, y, s, rot, seed, face = 'smile', open = 0) {
  const c = Math.cos(rot), sn = Math.sin(rot), R = (px, py) => [x + (px * c - py * sn) * s, y + (px * sn + py * c) * s];
  const lv = -0.22 - open * 0.5, piv = [30, -12];
  const le = [piv[0] - Math.cos(lv) * 66, piv[1] + Math.sin(lv) * 66];
  shape(capPts(...R(-38, 0), ...R(38, 0), 10 * s), RED, 3.6, seed);
  line([R(-46, -4), R(-38, -4)], 3, seed + 1);
  shape(capPts(...R(...piv), ...R(...le), 6 * s), PAPER, 3.2, seed + 2);
  shape(blobPts(...R(...piv), 5.5 * s, 5.5 * s, seed + 3, 7), YEL, 2.6, seed + 3);
  miniFace(...R(4, 1), 0.62 * s, rot, seed + 4, face);
}

// a mug, origin at its bottom-right corner so it tips over to the right
function cup(x, y, s, rot, seed, face = 'smile') {
  const c = Math.cos(rot), sn = Math.sin(rot), R = (px, py) => [x + (px * c - py * sn) * s, y + (px * sn + py * c) * s];
  line([R(-36, -36), R(-50, -30), R(-50, -14), R(-36, -10)], 5, seed + 1);
  shape([R(-36, -44), R(-18, -45), R(0, -44), R(-1, -2), R(-18, 0), R(-35, -2)], BLUE, 3.6, seed, 1.2, 4);
  miniFace(...R(-18, -22), 0.7 * s, rot, seed + 2, face);
}

// a wall calendar; page = how many pages have torn off (whole number), t for the flying page
function calendar(x, y, page, seed, flipT) {
  shape(boxPts(x - 46, y - 44, 92, 96, seed + page), PAPER, 3.4, seed + page);
  shape(boxPts(x - 46, y - 52, 92, 22, seed + 1), RED, 3.4, seed + 1);
  [-20, 20].forEach((dx, i) => line([[x + dx, y - 60], [x + dx, y - 44]], 3.4, seed + 2 + i));
  for (let r = 0; r < 3; r++) for (let k = 0; k < 3; k++)
    if (rnd(seed + page, r * 3 + k) > 0.3) line([[x - 28 + k * 26, y - 14 + r * 22], [x - 16 + k * 26, y - 14 + r * 22]], 2.4, seed + 10 + r * 3 + k);
  if (flipT !== undefined && flipT >= 0 && flipT < 1) {
    const u = flipT;
    shape(boxPts(x - 46 + u * 60, y - 44 - u * 120, 92 * (1 - 0.4 * u), 96 * (1 - 0.4 * u), seed + 40, -1.2 * u), PAPER, 3, seed + 40);
  }
}

// a shield
function shield(x, y, r, seed) {
  shape([[x - r, y - r], [x, y - r * 1.12], [x + r, y - r], [x + r * 0.95, y + r * 0.1], [x, y + r * 1.25], [x - r * 0.95, y + r * 0.1]], BLUE, 3.8, seed, 1.2, 5);
  tube([[x, y - r * 0.9], [x, y + r * 0.95]], 8, YEL, seed + 1);
  tube([[x - r * 0.8, y - r * 0.2], [x + r * 0.8, y - r * 0.2]], 8, YEL, seed + 2);
}

// a wastebin, feet at (x,y)
function bin(x, y, seed) {
  shape([[x - 40, y - 94], [x + 40, y - 94], [x + 32, y], [x - 32, y]], BLUE, 4, seed, 1.2, 4);
  [-14, 0, 14].forEach((dx, i) => line([[x + dx * 1.3, y - 80], [x + dx, y - 12]], 2.6, seed + 1 + i));
  shape(boxPts(x - 46, y - 104, 92, 14, seed + 5), PAPER, 3.6, seed + 5);
}

// a window that flips between day and night
function windowBox(x, y, night, seed) {
  shape(boxPts(x - 62, y - 62, 124, 124, seed), night ? INK : BLUE, 4, seed);
  if (night) moon(x - 18, y - 16, 20, seed + 1);
  else shape(blobPts(x - 18, y - 16, 20, 20, seed + 2, 9), YEL, 3, seed + 2);
  line([[x, y - 60], [x, y + 60]], 4, seed + 3, PAPER);
  line([[x - 60, y], [x + 60, y]], 4, seed + 4, PAPER);
}

// spiral nails on Kit's hands (inside a drawChar hold callback)
function kitNails(hands, P, L, curl, sag, seed, w = 7) {
  const tips = [];
  hands.forEach((h, i) => {
    const side = i ? 1 : -1, a = side < 0 ? P.aL : P.aR, a2 = a + side * P.bend;
    const ang = Math.atan2(Math.cos(a2), Math.sin(a2));
    [-0.35, 0, 0.35].forEach((da, k) => {
      const pts = nailPath(h[0] + Math.cos(ang + da) * 6, h[1] + Math.sin(ang + da) * 6, ang + da, L * (1 - k * 0.08), curl, sag, side);
      tube(pts, w, YEL, seed + i * 10 + k);
      tips.push(pts);
    });
  });
  return tips;
}

// the side cut-away of a giant fingertip (shots 3 and 4). ext = how far the nail sticks out past the tip.
function fingerSide(ext) {
  band(BLUE, 0, 960, 940);
  shape(capPts(-120, 570, 400, 570, 110), PAPER, 4.6, 941);
  // nail bed, under the plate
  line([[170, 470], [300, 474], [400, 470]], 2.4, 942, RED);
  // the nail plate
  const xe = 418 + ext;
  shape([[175, 446], [300, 440], [xe, 438], [xe + 8, 448], [xe, 460], [300, 462], [175, 466]], YEL, 3.6, 943, 1.2, 4);
  // the cuticle fold of skin
  shape(blobPts(160, 452, 46, 17, 944, 9, 0.05), PAPER, 3.6, 944);
  return xe;
}
