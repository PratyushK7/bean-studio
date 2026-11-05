// The Bean With Bad Ideas: the channel outro (voiced, appended to every video). Shared by the 16:9 and the 9:16 outro.
const PB = new FontFace('PoppinsB', 'url(Poppins-Bold.ttf)', { weight: '700' });
document.fonts.add(PB);
PB.load();

// the host: red bean, glasses, tuft, yellow scarf (same as the profile picture)
const BEAN = makeChar({ shape: 'bean', color: RED, size: 1.9, seed: 77, glasses: true, hair: 'tuft', scarf: YEL });

// a bad idea: a bulb with a crack. on = 0 (dark) .. 1 (lit, with glow rays)
function badBulb(x, y, r, seed, on) {
  if (on) for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU + 0.15, a1 = a - 0.09, a2 = a + 0.09, r0 = r * 1.35, r1 = r * (i % 2 ? 2.0 : 2.45);
    shape([[x + Math.cos(a1) * r0, y + Math.sin(a1) * r0], [x + Math.cos(a) * r1, y + Math.sin(a) * r1], [x + Math.cos(a2) * r0, y + Math.sin(a2) * r0]], PAPER, 2.6, seed + 40 + i, 1, 2);
  }
  shape(boxPts(x - r * 0.42, y + r * 0.75, r * 0.84, r * 0.5, seed + 2), PAPER, 3, seed + 2, 1);
  line([[x - r * 0.4, y + r * 1.0], [x + r * 0.4, y + r * 1.0]], 2.4, seed + 3);
  shape(blobPts(x, y - r * 0.2, r, r * 1.05, seed, 10, 0.04), on ? YEL : PAPER, 3.6, seed, 1.2);
  line([[x - r * 0.15, y - r * 1.1], [x + r * 0.05, y - r * 0.7], [x - r * 0.12, y - r * 0.45], [x + r * 0.12, y - r * 0.1]], 3, seed + 9, INK, 0.6, false);
  line([[x - r * 0.55, y - r * 0.6], [x - r * 0.62, y - r * 0.15]], 3, seed + 10, PAPER, 0.5);
}

// hand-lettered text: each letter tipped, bobbed and outlined. pop(i) = 0..1 scale for letter i
function letters(text, cx, y, size, fill, seed, pop = () => 1, track = 2) {
  ctx.save();
  ctx.font = `700 ${size}px PoppinsB, sans-serif`;
  ctx.lineJoin = 'round';
  const ws = [...text].map(ch => ctx.measureText(ch).width);
  let x = cx - (ws.reduce((a, b) => a + b, 0) + track * (ws.length - 1)) / 2;
  [...text].forEach((ch, i) => {
    const w = ws[i], s = pop(i);
    if (ch !== ' ' && s > 0) {
      const rot = (rnd(seed, i) - 0.5) * 0.16 + (hash(seed, i, V) - 0.5) * 0.04, dy = (rnd(seed, i + 50) - 0.5) * size * 0.08;
      ctx.save();
      ctx.translate(x + w / 2, y + dy);
      ctx.rotate(rot);
      ctx.scale(s, s);
      ctx.lineWidth = size * 0.16; ctx.strokeStyle = INK; ctx.strokeText(ch, -w / 2, 0);
      ctx.fillStyle = INK; ctx.fillText(ch, -w / 2 + size * 0.03, size * 0.04);
      ctx.fillStyle = fill; ctx.fillText(ch, -w / 2, 0);
      ctx.restore();
    }
    x += w + track;
  });
  ctx.restore();
}
function bell(x, y, s, seed, rot) {
  const c = Math.cos(rot), sn = Math.sin(rot), R = (px, py) => [x + (px * c - py * sn) * s, y + (px * sn + py * c) * s];
  shape([R(-16, 10), R(-13, -6), R(-7, -15), R(0, -17), R(7, -15), R(13, -6), R(16, 10), R(20, 14), R(-20, 14)], YEL, 3, seed, 0.8, 3);
  shape(blobPts(R(0, 18)[0], R(0, 18)[1], 5 * s, 5 * s, seed + 1, 6), YEL, 2.4, seed + 1, 0.5);
}

// ---------- the asks ----------
// scale for something that pops in at t0 and (optionally) pops out at t1: overshoot in, squash out
function popK(t, t0, t1 = Infinity) {
  if (t < t0 || t > t1 + 3 * D) return 0;
  if (t > t1) return [0.8, 0.45, 0.15][Math.min(2, Math.floor((t - t1) / D))];
  const u = (t - t0) / D;
  return u < 1 ? 0.55 : u < 2 ? 1.18 : u < 3 ? 0.95 : 1;
}
// draw something scaled about (x, y)
function scaled(x, y, k, f) { if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y); f(); ctx.restore(); }
// a thumbs-up, centred at (x, y)
function thumbUp(x, y, s, seed, fill = PAPER) {
  shape([[x - 13 * s, y - 2 * s], [x - 2 * s, y - 6 * s], [x + 2 * s, y - 22 * s], [x + 10 * s, y - 20 * s], [x + 9 * s, y - 6 * s],
    [x + 20 * s, y - 5 * s], [x + 18 * s, y + 16 * s], [x - 13 * s, y + 16 * s]], fill, 3, seed, 0.8, 3);
  shape(boxPts(x - 23 * s, y - 3 * s, 9 * s, 20 * s, seed + 1), fill, 3, seed + 1, 0.6);
}
// a share arrow (a curved arrow out of a box), centred at (x, y)
function shareIcon(x, y, s, seed, fill = PAPER) {
  shape([[x - 18 * s, y + 14 * s], [x - 16 * s, y - 4 * s], [x + 2 * s, y - 10 * s], [x + 2 * s, y - 20 * s], [x + 22 * s, y - 3 * s],
    [x + 2 * s, y + 14 * s], [x + 2 * s, y + 4 * s], [x - 8 * s, y + 4 * s]], fill, 3, seed, 0.8, 3);
}
// a pill-shaped button with an icon and a word. kind: 'like' | 'share' | 'sub'
function askButton(kind, x, y, s, seed, o = {}) {
  const word = { like: 'LIKE', share: 'SHARE', sub: 'SUBSCRIBE' }[kind], fill = o.fill || { like: YEL, share: PAPER, sub: RED }[kind];
  const iconW = kind === 'sub' ? 0 : 46 * s, w = (kind === 'sub' ? 230 : 190) * s, h = 64 * s;
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed, o.rot || 0), fill, 4.2, seed, 1.2);
  if (kind === 'like') thumbUp(x - w / 2 + 40 * s, y + 1 * s, 1.0 * s, seed + 5, PAPER);
  if (kind === 'share') shareIcon(x - w / 2 + 40 * s, y + 2 * s, 1.0 * s, seed + 5, YEL);
  letters(word, x + (kind === 'sub' ? 0 : iconW / 2 + 6 * s), y + 10 * s, (kind === 'sub' ? 32 : kind === 'share' ? 26 : 29) * s, kind === 'share' ? INK : PAPER, seed + 9, () => 1, 1.2);
  return { w, h };
}
// the end-screen slot: where YouTube's "next video" element sits. u = 0..1 draws the frame in
function videoSlot(x, y, w, h, seed, u = 1) {
  if (u <= 0) return;
  scaled(x + w / 2, y + h / 2, EASE.back(Math.min(1, u)), () => {
    shape(boxPts(x, y, w, h, seed), INK, 4.4, seed, 1.2);
    shape(boxPts(x + 10, y + 10, w - 20, h - 20, seed + 1), BLUE, 2.4, seed + 1, 0.8);
    const cx = x + w / 2, cy = y + h / 2, r = Math.min(w, h) * 0.18;
    shape([[cx - r * 0.7, cy - r], [cx + r, cy], [cx - r * 0.7, cy + r]], RED, 3.6, seed + 2, 0.8, 3);
  });
}
