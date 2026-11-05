// Why is the sky blue? WIDE (16:9, 960 x 540) example: cast and props. The world is 960 wide, so characters are drawn a little
// larger than in a Short (Mo is about 1.1 here; the frame is only 540 high) and the ground sits at y 430, leaving the bottom band (y 476) for captions.

// Mo: a tall red bean in a blue beanie (the viewer's stand-in)
const MO = makeChar({ shape: 'tall', color: RED, size: 1.1, seed: 3, hat: { kind: 'beanie', color: BLUE, pom: YEL } });
// the Sun: a yellow ball bean with rays and red cheeks, no legs (it floats)
const SUN = makeChar({ shape: 'ball', color: YEL, rays: YEL, cheeks: RED, legs: false, size: 1.2, seed: 5, eye: 1.1 });
// air molecules: tiny paper-white beans, each a little different
const MOLS = [7, 8, 9, 10].map(s => makeChar({ shape: 'tiny', color: PAPER, legs: false, size: 1.5, seed: s, eye: 0.8 }));

const GY = 430;   // ground line

// a wave of light: a coloured tube squiggling from tail to head, with a face on its head. Returns the head point.
function lightWave(x0, y0, x1, y1, color, wl, amp, phase, seed, face) {
  const len = Math.hypot(x1 - x0, y1 - y0);
  if (len < 10) return [x1, y1];
  const pts = wavePts(x0, y0, x1, y1, len / wl, amp, phase, Math.max(8, Math.round(len / wl * 8)));
  tube(pts, 9, color, seed);
  const h = pts[pts.length - 1];
  if (face) { shape(blobPts(h[0], h[1], 14, 13, seed + 3, 8), color, 3, seed + 3, 1); miniFace(h[0], h[1], 0.62, 0, seed + 4, face); }
  return h;
}
// a short scrap of light flying away from (ox, oy)
function bit(ox, oy, a, dist, seed, color = BLUE) {
  const x1 = ox + Math.cos(a) * dist, y1 = oy + Math.sin(a) * dist, back = Math.min(dist, 46);
  tube(wavePts(x1 - Math.cos(a) * back, y1 - Math.sin(a) * back, x1, y1, 2.2, 5, seed), 6, color, seed);
}
// a spray of bits leaving a point from t0
function scatter(t, t0, ox, oy, seed, n = 5, speed = 300, color = BLUE) {
  const lt = t - t0;
  if (lt < 0) return;
  for (let i = 0; i < n; i++) {
    const a = rnd(seed, i) * TAU, d = 24 + lt * speed * (0.7 + 0.5 * rnd(seed, i + 9));
    if (d < 900) bit(ox, oy, a, d, seed + i * 7, color);
  }
  if (lt < 2 * D) burst(ox, oy, 18, 36, seed + 50, 0);
}
// the sunny-day set: sky band, two clouds, hills, ground
function skyScene(t, o = {}) {
  band(o.sky || BLUE, 0, o.skyY || GY - 40, 301);
  cloud(150 + t * 6, 110, 70, 26, 311);
  cloud(760 - t * 4, 80, 52, 20, 312);
  hills(GY - 50);
  ground(GY);
}
