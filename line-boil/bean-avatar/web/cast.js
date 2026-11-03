// The Bean With Bad Ideas: the host
const BEAN = makeChar({ shape: 'bean', color: RED, size: 2.2, seed: 77, glasses: true, hair: 'tuft', scarf: YEL });

// a bad idea: a lit bulb with a crack and a spark
function badBulb(x, y, r, seed, glow) {
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU + 0.15, a1 = a - 0.09, a2 = a + 0.09, r0 = r * 1.35, r1 = r * (i % 2 ? 2.0 : 2.45);
    shape([[x + Math.cos(a1) * r0, y + Math.sin(a1) * r0], [x + Math.cos(a) * r1, y + Math.sin(a) * r1], [x + Math.cos(a2) * r0, y + Math.sin(a2) * r0]], glow, 2.6, seed + 40 + i, 1, 2);
  }
  bulb(x, y, r, seed, false);
  shape(blobPts(x, y - r * 0.2, r, r * 1.05, seed, 10, 0.04), YEL, 3.6, seed, 1.2);
  line([[x - r * 0.15, y - r * 1.1], [x + r * 0.05, y - r * 0.7], [x - r * 0.12, y - r * 0.45], [x + r * 0.12, y - r * 0.1]], 3, seed + 9, INK, 0.6, false);
  line([[x - r * 0.55, y - r * 0.6], [x - r * 0.62, y - r * 0.15]], 3, seed + 10, PAPER, 0.5);
  plus(x + r * 1.05, y - r * 1.05, 7, seed + 20);
}
