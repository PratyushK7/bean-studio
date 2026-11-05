// How Does Caffeine Steal Your Sleep? WIDE (16:9, 960 x 540): the cast, the props and the small helpers every chapter shares.
// The metaphor: tiredness is a sleepy mail carrier posting TIRED letters into the brain's mailboxes (adenosine receptors);
// caffeine is a small wired bean that sits in the slot wearing a CLOSED sign; the liver escorts caffeine out, half at a time.

const GY = 430;   // ground line for the plain sets

// Pose tracks: a property whose first key comes mid-performance (a take's squash and take lines, a zzz, a point's wind-up)
// would otherwise show that key's value from the very start of the shot. Hold the rest pose until just before it instead.
buildTracks = (orig => keys => {
  const tr = orig(keys), t0 = Math.min(...keys.map(k => k.t));
  ['fx', 'smear', 'sy', 'sx', 'lean', 'fL', 'fR', 'aL', 'aR', 'bend', 'reach', 'eyes', 'mouth', 'brow', 'browY'].forEach(p => {
    const list = tr[p];
    if (list && list[0].t > t0 + 1e-6) list.unshift({ t: Math.max(t0, list[0].t - 0.35), v: DEFAULT_POSE[p], ease: 'hold' });
  });
  return tr;
})(buildTracks);

// YOU: the viewer, a paper-white bean in a blue beanie that doubles as a nightcap
const YOU = makeChar({ shape: 'bean', color: PAPER, size: 1.05, seed: 11, cheeks: RED, hat: { kind: 'beanie', color: BLUE, pom: YEL } });
// TIREDNESS (adenosine): a wide, sleepy blue mail carrier in a red cap, with a yellow mail bag
const ADO = makeChar({ shape: 'wide', color: BLUE, size: 1.0, seed: 23, hat: { kind: 'cap', color: RED }, nose: 'dot' });
// CAFFEINE: a small red ball bean with spiky hair and big eyes that never relax
const CAF = makeChar({ shape: 'ball', color: RED, size: 0.75, seed: 37, hair: 'spikes', eye: 1.25 });
// a crowd of tiny caffeine beans (the half-life and the 3 p.m. maths)
const CAFS = [41, 42, 43, 44, 45, 46, 47, 48].map(s => makeChar({ shape: 'tiny', color: RED, size: 1.15, seed: s, hair: 'spikes', eye: 1.1 }));
// LIVER: a fussy yellow pear in a blue top hat and glasses
const LIV = makeChar({ shape: 'pear', color: YEL, size: 1.0, seed: 53, glasses: true, hat: { kind: 'top', color: BLUE, band: RED } });
// SCIENTIST: a tall red bean in a paper lab coat, glasses and a tuft
const SCI = makeChar({ shape: 'tall', color: RED, size: 1.0, seed: 61, glasses: true, belly: PAPER, hair: 'tuft' });
// SLEEPERS: tiny beans for the study (paper and blue, alternating)
const SLEEPERS = Array.from({ length: 12 }, (_, i) => makeChar({ shape: 'tiny', color: i % 2 ? BLUE : PAPER, size: 1.0, seed: 71 + i, eye: 0.9 }));
// GYM: a square yellow bean with a red towel (the pre-workout joke)
const GYMB = makeChar({ shape: 'box', color: YEL, size: 0.95, seed: 91, scarf: RED, hair: 'spikes' });

// ---------- lettering on shapes (no burned-in captions in a long video: key words and numbers live on labels) ----------
function _font(size) { return `700 ${size}px CapFont, sans-serif`; }
function textW(text, size) { ctx.save(); ctx.font = _font(size); const w = ctx.measureText(text).width; ctx.restore(); return w; }
// one line of lettering that boils with the drawing
function ink(text, x, y, size, fill = INK, seed = 1, rot = 0, outline = 0) {
  ctx.save();
  ctx.font = _font(size); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.translate(x + (rnd(seed, V) - 0.5) * 1.2, y + (rnd(seed + 1, V) - 0.5) * 1.2);
  ctx.rotate(rot + (rnd(seed + 2, V) - 0.5) * 0.014);
  if (outline) { ctx.lineWidth = outline; ctx.strokeStyle = INK; ctx.strokeText(text, 0, 0); }
  ctx.fillStyle = fill; ctx.fillText(text, 0, 0);
  ctx.restore();
}
// a label shape: a card with lettering, slightly tilted. o: { fill, ink, rot, seed, pad }
function label(text, x, y, size = 26, o = {}) {
  const seed = o.seed ?? 500, rot = o.rot ?? 0, w = textW(text, size) + size * (o.pad ?? 0.9), h = size * 1.5;
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed, rot), o.fill ?? PAPER, 3.4, seed, 1);
  ink(text, x, y + size * 0.05, size, o.ink ?? INK, seed + 7, rot);
  return { w, h };
}
// a label that pops in at t0 (a 3-drawing overshoot)
function popLabel(t, t0, text, x, y, size, o = {}) {
  if (t < t0) return;
  const u = (t - t0) / D, k = u < 1 ? 0.6 : u < 2 ? 1.12 : 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y);
  label(text, x, y, size, o);
  ctx.restore();
}

// ---------- props ----------
// a mug, (x, y) = bottom centre. o: { color, steam, face, word, t }
function mug(x, y, s, seed, o = {}) {
  const w = 34 * s, h = 40 * s, t = o.t ?? NOW;
  if (o.steam) for (let i = 0; i < 3; i++) {
    const sx = x - 10 * s + i * 10 * s;
    line(wavePts(sx, y - h - 6 * s, sx + 2 * s, y - h - 34 * s, 1.2, 3 * s, t * 5 + i * 2), 2.4, seed + 20 + i);
  }
  shape([[x + w * 0.45, y - h * 0.78], [x + w * 0.95, y - h * 0.72], [x + w * 0.9, y - h * 0.3], [x + w * 0.45, y - h * 0.26]], null, 4 * Math.sqrt(s), seed + 3, 1);
  shape([[x - w / 2, y - h], [x + w / 2, y - h], [x + w * 0.45, y], [x - w * 0.45, y]], o.color || RED, 3.6, seed, 1.2, 3);
  if (o.word) ink(o.word, x, y - h * 0.5, 9.5 * s, PAPER, seed + 5);
  else if (o.face) miniFace(x, y - h * 0.45, 0.7 * s, 0, seed + 6, o.face);
}
// a wall clock; hour may be fractional (3.5 = half past three)
function clockFace(x, y, r, hour, seed, o = {}) {
  shape(blobPts(x, y, r, r, seed, 14, 0.02), o.fill || PAPER, 3.6, seed, 1);
  if (o.wedge) {                                                    // a shaded span of hours [h0, h1, colour]
    const [h0, h1, col] = o.wedge, pts = [[x, y]];
    for (let k = 0; k <= 24; k++) { const a = lerp(h0, h1, k / 24) / 12 * TAU - Math.PI / 2; pts.push([x + Math.cos(a) * r * 0.9, y + Math.sin(a) * r * 0.9]); }
    fillOnly(pts, col || YEL, seed + 30);
  }
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU, r0 = r * (i % 3 ? 0.84 : 0.76);
    line([[x + Math.cos(a) * r0, y + Math.sin(a) * r0], [x + Math.cos(a) * r * 0.92, y + Math.sin(a) * r * 0.92]], i % 3 ? 2 : 3, seed + 1 + i, INK, 0.5, false);
  }
  const ah = (hour % 12) / 12 * TAU - Math.PI / 2, am = (hour % 1) * TAU - Math.PI / 2;
  line([[x, y], [x + Math.cos(ah) * r * 0.5, y + Math.sin(ah) * r * 0.5]], 5, seed + 20, INK, 0.6, false);
  line([[x, y], [x + Math.cos(am) * r * 0.74, y + Math.sin(am) * r * 0.74]], 3.4, seed + 21, o.hand || RED, 0.6, false);
  fillOnly(blobPts(x, y, 4, 4, seed + 22, 6), INK, seed + 22);
}
// an envelope. o: { word, face, fill }
function letter(x, y, s, rot, seed, o = {}) {
  const w = 40 * s, h = 26 * s, c = Math.cos(rot), sn = Math.sin(rot), R = (px, py) => [x + px * c - py * sn, y + px * sn + py * c];
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed, rot), o.fill || PAPER, 3 * Math.sqrt(s), seed, 0.8);
  line([R(-w / 2 + 2, -h / 2 + 2), R(0, h * 0.08), R(w / 2 - 2, -h / 2 + 2)], 2.4 * Math.sqrt(s), seed + 1, INK, 0.6, false);
  if (o.word) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ink(o.word, 0, h * 0.27, 7.5 * s, RED, seed + 2); ctx.restore(); }
  else if (o.face !== false) miniFace(R(0, h * 0.26)[0], R(0, h * 0.26)[1], 0.42 * s, rot, seed + 3, o.face || 'sleepy');
}
// a heap of n letters around (x, y), growing upward
function letterPile(x, y, n, seed, s = 1) {
  for (let i = 0; i < n; i++) {
    const row = Math.floor(Math.sqrt(i * 1.6)), across = (rnd(seed, i) - 0.5) * (130 - row * 9) * s;
    letter(x + across, y - 10 * s - row * 14 * s - rnd(seed, i + 50) * 6 * s, s, (rnd(seed, i + 90) - 0.5) * 0.9, seed + 10 + i * 3, { face: i % 3 ? 'sleepy' : false });
  }
}
// a mailbox on a post, (x, y) = foot of the post. o: { face, post: false, flag, fill }. Returns the slot { x, y, w } and the face point.
function mailbox(x, y, s, seed, o = {}) {
  const ph = o.post === false ? 0 : 70 * s, yb = y - ph, yt = yb - 56 * s, x0 = x - 42 * s, x1 = x + 42 * s;
  if (ph) tube([[x, y + 2], [x, yb + 4]], 9 * s, PAPER, seed + 1);
  if (o.flag !== undefined) {
    const up = o.flag;
    line([[x1 + 4 * s, yb - 12 * s], [x1 + 4 * s, yb - (up ? 64 : 28) * s]], 3, seed + 2);
    shape(up ? boxPts(x1 + 4 * s, yb - 64 * s, 20 * s, 13 * s, seed + 3) : boxPts(x1 + 4 * s, yb - 28 * s, 20 * s, 13 * s, seed + 3), RED, 2.8, seed + 3, 0.8);
  }
  shape([[x0, yb], [x0, yt], [x0 + 12 * s, yt - 15 * s], [x, yt - 22 * s], [x1 - 12 * s, yt - 15 * s], [x1, yt], [x1, yb]], o.fill || BLUE, 4 * Math.sqrt(s), seed, 1.2, 5);
  const sy = yt + 4 * s;
  shape(boxPts(x - 27 * s, sy - 5 * s, 54 * s, 10 * s, seed + 4), INK, 2.4, seed + 4, 0.6);
  if (o.face) miniFace(x, yb - 16 * s, 0.95 * s, 0, seed + 5, o.face, o.look || [0, 0]);
  return { x, y: sy, w: 54 * s, face: [x, yb - 16 * s], top: yt - 22 * s, s };
}
// caffeine sitting IN the slot: the bottom of the bean is hidden inside, the CLOSED sign hangs over the box front
function cafInSlot(slot, keys, t, o = {}) {
  const s = slot.s * (o.k ?? 0.45), P = poseAt(keys, t);   // keys may carry dy (shot-specific rise or sink) and any face props
  Object.assign(P, { x: slot.x + (P.dx || 0), y: slot.y + CAF.h * s * 0.42 + (P.dy || 0), size: s / CAF.size });
  ctx.save(); ctx.beginPath(); ctx.rect(-2000, -2000, 5000, slot.y + 2000 + 1); ctx.clip();
  const A = drawChar(CAF, P, { shadow: false });
  ctx.restore();
  line([[slot.x - slot.w / 2, slot.y + 1], [slot.x + slot.w / 2, slot.y + 2]], 4.6 * Math.sqrt(slot.s), 6001, INK, 0.6, false);
  if (o.sign !== false) closedSign(slot.x, slot.y + 6 * slot.s, slot.s * 0.95, 6010, o.swing ? Math.sin(t * 6) * 0.06 : 0.03);
  return A;
}
// the CLOSED sign, hung from a string at (x, y)
function closedSign(x, y, s, seed, rot = 0) {
  const w = 74 * s, h = 24 * s, cy = y + 12 * s + h / 2;
  line([[x - w * 0.3, cy - h / 2], [x, y], [x + w * 0.3, cy - h / 2]], 2.2, seed + 1, INK, 0.5, false);
  shape(boxPts(x - w / 2, cy - h / 2, w, h, seed, rot), YEL, 3.2, seed, 0.9);
  ink('CLOSED', x, cy + 1, 15 * s, INK, seed + 2, rot);
}
// the mail carrier's bag and strap (use as drawChar's hold), plus a letter in the right hand when asked
function mailBag(withLetter = false, word) {
  return (hands, P, A) => {
    const c = ADO, s = c.size * P.size;
    line([tp(c, P, -c.w * 0.62, -c.h * 0.78), tp(c, P, c.w * 0.25, -c.h * 0.45), tp(c, P, c.w * 0.82, -c.h * 0.28)], 4 * Math.sqrt(s), 2301);
    const b = tp(c, P, c.w * 0.86, -c.h * 0.2);
    letter(b[0] - 6 * s, b[1] - 16 * s, 0.6 * s, -0.3, 2310, { face: false });
    letter(b[0] + 8 * s, b[1] - 18 * s, 0.6 * s, 0.25, 2313, { face: false });
    shape(boxPts(b[0] - 22 * s, b[1] - 12 * s, 44 * s, 32 * s, 2302, 0.06), YEL, 3.4, 2302, 1);
    line([[b[0] - 22 * s, b[1] - 2 * s], [b[0], b[1] + 6 * s], [b[0] + 22 * s, b[1] - 2 * s]], 2.6, 2303, INK, 0.6, false);
    if (withLetter) letter(hands[1][0] + 8 * s, hands[1][1] - 6 * s, 0.9 * s, -0.2, 2320, { word: word || 'TIRED' });
  };
}
// a bed in side view, (x, y) = floor under the middle; returns the mattress top y
function bed(x, y, L, seed, o = {}) {
  const s = o.s ?? 1, top = y - 46 * s;
  shape(boxPts(x - L / 2 - 14, y - 118 * s, 18, 118 * s, seed), o.frame || RED, 3.4, seed, 1);
  shape(boxPts(x + L / 2 - 4, y - 74 * s, 16, 74 * s, seed + 1), o.frame || RED, 3.4, seed + 1, 1);
  shape(boxPts(x - L / 2, top, L, 26 * s, seed + 2), PAPER, 3.4, seed + 2, 1);
  shape(blobPts(x - L / 2 + 34 * s, top - 10 * s, 30 * s, 13 * s, seed + 3, 9, 0.05), PAPER, 3, seed + 3, 1);
  return top;
}
// the blanket, drawn over a sleeper from x0 to the foot of the bed
function blanket(x0, x1, top, seed, color = BLUE, s = 1) {
  shape([[x0, top - 34 * s], [x0 + 30 * s, top - 42 * s], [(x0 + x1) / 2, top - 38 * s], [x1, top - 30 * s], [x1 + 6, top + 22 * s], [x0 - 4, top + 22 * s]], color, 3.6, seed, 1.2, 5);
  line([[x0 + 16 * s, top - 30 * s], [x0 + 20 * s, top + 16 * s]], 2.4, seed + 1, INK, 0.8);
}
// draw a character lying down, head to the left, pivoting on its feet
function drawLying(c, P, opt = {}) {
  ctx.save(); ctx.translate(P.x, P.y); ctx.rotate(-Math.PI / 2 + (opt.tilt || 0)); ctx.translate(-P.x, -P.y);
  const A = drawChar(c, P, Object.assign({ shadow: false }, opt));
  ctx.restore();
  return A;
}
// a headband for the sleepers in the study (use as hold)
function headband(c) {
  return (hands, P) => { tube([tp(c, P, -c.w * 0.92, -c.h * 0.88), tp(c, P, 0, -c.h * 0.93), tp(c, P, c.w * 0.92, -c.h * 0.88)], 4, YEL, 7001); };
}
// a sleep-monitor screen with a brain-wave trace. o: { face, flat, color }
function monitor(x, y, w, h, t, seed, o = {}) {
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed), INK, 3.4, seed, 1);
  shape(boxPts(x - w / 2 + 8, y - h / 2 + 8, w - 16, h - 16, seed + 1), o.screen || BLUE, 2, seed + 1, 0.6);
  const pts = [];
  for (let i = 0; i <= 24; i++) {
    const u = i / 24, px = x - w / 2 + 16 + u * (w - 32);
    pts.push([px, y + Math.sin(u * 18 + t * 9) * (o.flat ? 3 : h * 0.16) * (0.6 + 0.4 * Math.sin(u * 5 + t * 2))]);
  }
  line(pts, 2.8, seed + 2, o.color || YEL, 0.4, false);
  line([[x, y + h / 2], [x, y + h / 2 + 18]], 5, seed + 3);
  if (o.face) miniFace(x + w / 2 - 22, y - h / 2 + 22, 0.9, 0, seed + 4, o.face);
}
// the brain: a paper cloud with folds, and little mailboxes along its edge if asked
function brain(cx, cy, rx, ry, seed, t = 0) {
  shape(cloudPts(cx, cy, rx, ry, seed), PAPER, 4.4, seed, 1.6);
  [[-0.5, -0.3, 0.3], [0.1, -0.45, 0.35], [-0.2, 0.1, 0.4], [0.45, 0.05, 0.3], [-0.6, 0.3, 0.2]].forEach(([fx, fy, l], i) =>
    line(wavePts(cx + fx * rx, cy + fy * ry, cx + (fx + l) * rx, cy + (fy + 0.08) * ry, 1.5, 7, i), 3, seed + 1 + i));
  line([[cx + rx * 0.02, cy - ry * 0.9], [cx - rx * 0.03, cy - ry * 0.3], [cx + rx * 0.04, cy + ry * 0.2]], 3, seed + 9);
}
// a stack of papers (the 24 studies)
function paperStack(x, y, n, seed, s = 1) {
  for (let i = 0; i < n; i++) {
    const r = (rnd(seed, i) - 0.5) * 0.12;
    shape(boxPts(x - 50 * s + (rnd(seed, i + 30) - 0.5) * 10, y - (i + 1) * 7 * s, 100 * s, 7 * s, seed + i * 2, r), PAPER, 2.4, seed + i * 2, 0.6);
  }
}
// a pill, centred at (x, y)
function pill(x, y, s, seed, color = RED, rot = 0) {
  const c = Math.cos(rot), sn = Math.sin(rot);
  shape(blobPts(x, y, 20 * s, 9 * s, seed, 10, 0.02, rot), PAPER, 3, seed, 0.8);
  fillOnly(blobPts(x + c * 9 * s, y + sn * 9 * s, 10 * s, 7.5 * s, seed + 1, 8, 0.02, rot), color, seed + 1);
  line([[x - sn * 8 * s, y + c * 8 * s], [x + sn * 8 * s, y - c * 8 * s]], 2.2, seed + 2, INK, 0.5, false);
}
// a dumbbell
function dumbbell(x, y, s, seed, rot = 0) {
  const c = Math.cos(rot) * 34 * s, sn = Math.sin(rot) * 34 * s;
  tube([[x - c, y - sn], [x + c, y + sn]], 6 * s, PAPER, seed);
  [[-1], [1]].forEach(([k], i) => shape(blobPts(x + k * c, y + k * sn, 13 * s, 20 * s, seed + 1 + i, 8, 0.05, rot), INK, 2, seed + 1 + i, 0.6));
}
// a shelf with things on it
function shelf(x, y, w, seed) {
  shape(boxPts(x - w / 2, y, w, 9, seed), RED, 3, seed, 0.8);
  line([[x - w * 0.35, y + 9], [x - w * 0.35, y + 26], [x - w * 0.25, y + 9]], 3, seed + 1);
  line([[x + w * 0.35, y + 9], [x + w * 0.35, y + 26], [x + w * 0.25, y + 9]], 3, seed + 2);
}
// a doorway on a wall: frame + dark opening, (x, y) = bottom centre
function doorway(x, y, w, h, seed, fill = INK) {
  shape(boxPts(x - w / 2, y - h, w, h, seed), fill, 4, seed, 1);
  line([[x - w / 2 - 8, y], [x - w / 2 - 8, y - h - 8], [x + w / 2 + 8, y - h - 8], [x + w / 2 + 8, y]], 5, seed + 1, INK, 1, false);
}
// a night window over setRoom's window (it is at 115, 70, 192 x 205 in the wide frame)
function nightWindow(t) {
  shape(boxPts(115, 70, 192, 205, 12210), INK, 4, 12210, 1);
  moon(250, 125, 26, 7301);
  [[150, 110], [180, 220], [270, 240], [140, 190], [290, 100]].forEach(([x, y], i) => { if ((i + Math.floor(t * 2)) % 5) fillOnly(blobPts(x, y, 3, 3, 7310 + i, 6), PAPER, 7310 + i); });
  line([[211, 70], [211, 275]], 3.4, 12211, INK, 0.6);
  line([[115, 172], [307, 172]], 3.4, 12212, INK, 0.6);
}
// a broom (the liver sweeps caffeine out), held at the hand, bristles on the ground at (bx, by)
function broom(hand, bx, by, seed) {
  line([hand, [bx, by - 20]], 5, seed, INK, 0.6, false);
  shape([[bx - 8, by - 24], [bx + 8, by - 24], [bx + 26, by + 2], [bx - 26, by + 2]], YEL, 3, seed + 1, 0.8, 3);
}
// midnight with a big full moon at (mx, my): ink on ink vanishes, so the moon sits behind whatever must read (caffeine's spiky hair)
function midnightSky(t, mx, my, mr) {
  paper(INK);
  for (let i = 0; i < 28; i++) {
    if ((i + Math.floor(t * 2)) % 9 === 0) continue;
    const r = 1.5 + rnd(12103, i) * 2.5;
    fillOnly(blobPts(rnd(12101, i) * W, rnd(12102, i) * (H * 0.8 - 40), r, r, 12110 + i, 6), PAPER, 12110 + i);
  }
  shape(blobPts(mx, my, mr, mr, 7401, 16, 0.02), YEL, 4, 7401, 1);
  ground(H * 0.8, 12130, { fill: BLUE, grass: false });
  return H * 0.8;
}
// a gentle bob for floating things
const bob = (t, k = 1, sp = 3) => Math.sin(t * sp + k) * 4;
// clock hands that spin from h0 to h1 starting at t0
const hourAt = (t, t0, h0, h1, dur = 0.7) => t < t0 ? h0 : lerp(h0, h1, EASE.io(clamp((t - t0) / dur, 0, 1)));
// pose keys for a bean dropping into frame and landing at (x, y) at t0
function dropIn(t0, x, y, o = {}) {
  cue(t0, 'thud', 0.7);
  return [
    { t: t0 - 0.36, x, y: -200, sy: 1.15, sx: 0.9, expr: o.upExpr || 'surprised', ease: 'hold' },
    { t: t0, y, ease: 'in' },
    { t: t0, sy: 0.65, sx: 1.35, fx: 'dust0', ease: 'hold' },
    { t: t0 + D, sy: 1.12, sx: 0.92, fx: 'dust1', ease: 'hold' },
    { t: t0 + 2 * D, sy: 0.97, sx: 1.02, fx: 'dust2', ease: 'hold' },
    { t: t0 + 3 * D, sy: 1, sx: 1, fx: null, expr: o.expr || 'neutral', ease: 'hold' },
  ];
}
// floating Zs (drawn in world space, so they stay upright next to a lying sleeper)
function zzz(x, y, t, seed, s = 1) {
  for (let i = 0; i < 3; i++) {
    const u = ((t * 0.6 + i / 3) % 1);
    ink('Z', x + i * 14 * s + u * 10 * s, y - u * 46 * s, (12 + i * 5) * s, INK, seed + i);
  }
}
// scale for something that pops in at t0 (overshoot) and, optionally, out at t1
function popK(t, t0, t1 = Infinity) {
  if (t < t0 || t > t1 + 3 * D) return 0;
  if (t > t1) return [0.8, 0.45, 0.15][Math.min(2, Math.floor((t - t1) / D))];
  const u = (t - t0) / D;
  return u < 1 ? 0.55 : u < 2 ? 1.18 : u < 3 ? 0.95 : 1;
}
// draw something scaled about (x, y)
function scaled(x, y, k, f) { if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y); f(); ctx.restore(); }
