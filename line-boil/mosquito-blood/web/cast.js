// How many mosquitoes would it take to drain all your blood? Cast and topic props.

// Kit: a blue bean kid in a red cap (the viewer's stand-in)
const KIT = makeChar({ shape: 'bean', color: BLUE, size: 1.3, seed: 3, hat: { kind: 'cap', color: RED }, cheeks: RED });
// Mozzie: a tiny yellow mosquito with a red bow (she's a she: only females bite). Floats; wings and nose drawn below.
const MOZ = makeChar({ shape: 'tiny', color: YEL, legs: false, size: 1, seed: 5, eye: 1.15, hat: { kind: 'bow', color: RED } });
// the swarm: smaller, plain mosquitoes, each with its own wobble
const SWARM = Array.from({ length: 6 }, (_, i) => makeChar({ shape: 'tiny', color: YEL, legs: false, size: 0.55, seed: 20 + i, eye: 1.1 }));

const GY = 800;   // ground line

// wings (behind) + Mozzie + legs and a long ink proboscis (in front). Flaps every drawing. Returns the nose tip.
function drawMoz(c, P, t, o = {}) {
  if (P.hide) return null;
  const s = c.size * P.size, f = P.facing, bx = P.x, by = P.y - c.h * s * 0.62;
  const flap = Math.floor(t * 12) % 2 ? 0.45 : -0.15;
  [-1, 1].forEach(k => {
    const a = -Math.PI / 2 - f * (0.7 + k * 0.35) + flap * (k > 0 ? 1 : -1) * 0.5;
    const r = 30 * s, cx = bx - f * 8 * s + Math.cos(a) * r, cy = by - 8 * s + Math.sin(a) * r;
    shape(blobPts(cx, cy, 26 * s, 11 * s, c.seed * 31 + k, 8, 0.05, a), PAPER, 2.6 * Math.sqrt(s), c.seed * 31 + k, 1);
  });
  // dangly legs
  for (let k = 0; k < 3; k++) {
    const lx = bx + (k - 1) * 12 * s, ly = P.y - 4 * s;
    line([[lx, ly], [lx - f * 6 * s, ly + 14 * s], [lx - f * 2 * s, ly + 24 * s]], 2.4 * Math.sqrt(s), c.seed * 37 + k);
  }
  const an = drawChar(c, P, o);
  // proboscis: from the face, forward and down
  const m = an.mouth, ang = o.noseAng ?? 0.55, L = 34 * s;
  const tip = [m[0] + f * Math.cos(ang) * L, m[1] + Math.sin(ang) * L];
  line([[m[0] + f * 4 * s, m[1] - 2 * s], tip], 3.2 * Math.sqrt(s), c.seed * 41);
  return tip;
}

// a quick, cheap mosquito for crowds: blob body, two wings, nose
function mini(x, y, s, seed, t, f = 1, face = 'smile') {
  const flap = (Math.floor(t * 12) + seed) % 2 ? 0.4 : -0.2;
  shape(blobPts(x - f * 8 * s, y - 20 * s, 15 * s, 7 * s, seed, 7, 0.05, -0.9 * f + flap), PAPER, 2.2, seed, 1);
  shape(blobPts(x + f * 2 * s, y - 22 * s, 15 * s, 7 * s, seed + 1, 7, 0.05, -1.4 * f - flap), PAPER, 2.2, seed + 1, 1);
  shape(blobPts(x, y, 13 * s, 11 * s, seed + 2, 8, 0.08), YEL, 2.8, seed + 2, 1.2);
  line([[x + f * 10 * s, y + 2 * s], [x + f * 28 * s, y + 14 * s]], 2.4, seed + 3);
  miniFace(x + f * 2 * s, y, 0.5 * s, 0, seed + 4, face);
}

// the Jug: a big paper jug holding `level` (0..1) of blood, with a face. (x, y) = bottom middle.
function jug(x, y, s, level, seed, face = 'smile', look = [0, 0]) {
  const w = 110 * s, h = 230 * s, top = y - h;
  // handle (behind)
  tube([[x + w * 0.9, top + h * 0.25], [x + w * 1.35, top + h * 0.3], [x + w * 1.38, top + h * 0.6], [x + w * 0.92, top + h * 0.7]], 16 * s, PAPER, seed + 1);
  const body = [[x - w, y - 8 * s], [x - w * 1.02, top + h * 0.3], [x - w * 0.8, top + h * 0.12], [x - w * 0.55, top],
    [x + w * 0.55, top], [x + w * 0.8, top + h * 0.12], [x + w * 1.02, top + h * 0.3], [x + w, y - 8 * s], [x + w * 0.8, y], [x - w * 0.8, y]];
  shape(body, PAPER, 4.4 * Math.sqrt(s), seed, 1.4, 4);
  if (level > 0.005) {
    const ly = lerp(y - 8 * s, top + h * 0.16, clamp(level, 0, 1)), k = (ly - top) / h;
    const half = k < 0.3 ? lerp(0.6, 0.97, k / 0.3) : 0.97;
    const wav = i => Math.sin(i * 1.7 + seed) * 3 * s;
    const pts = [[x - w * 0.95, y - 12 * s], [x - w * half, ly + wav(0)], [x - w * half * 0.3, ly + wav(1)], [x + w * half * 0.3, ly + wav(2)],
      [x + w * half, ly + wav(3)], [x + w * 0.95, y - 12 * s], [x + w * 0.78, y - 4 * s], [x - w * 0.78, y - 4 * s]];
    fillOnly(pts, RED, seed + 2);
    shape(body, null, 4.4 * Math.sqrt(s), seed, 1.4, 4);
  }
  // spout lip
  line([[x - w * 0.6, top + 2 * s], [x + w * 0.62, top - 2 * s], [x + w * 0.8, top - 14 * s]], 4 * Math.sqrt(s), seed + 3);
  miniFace(x, top + h * 0.5, 2.6 * s, 0, seed + 4, face, look);
  return { top: [x, top], mid: [x, top + h * 0.5], w, h };
}

// a grain of rice: a fat paper oval
function rice(x, y, s, seed) { shape(blobPts(x, y, 30 * s, 12 * s, seed, 9, 0.04, -0.25), PAPER, 3.2, seed, 1); }

// a hazard sign on a post: yellow triangle, red rim, ink "!"
function hazard(x, y, s, seed) {
  line([[x, y], [x + 1, y + 120 * s]], 5, seed);
  shape([[x, y - 70 * s], [x + 62 * s, y + 34 * s], [x - 62 * s, y + 34 * s]], YEL, 5, seed + 1, 1.2, 3);
  line([[x, y - 30 * s], [x + 1, y + 2 * s]], 7 * s, seed + 2);
  fillOnly(blobPts(x, y + 18 * s, 5 * s, 5 * s, seed + 3, 6), INK, seed + 3);
}

// the outdoor set: blue sky band, two clouds, grass
function park(t, o = {}) {
  band(BLUE, 0, o.skyY || 400, 301);
  cloud(110 + t * 5, 160, 52, 20, 311);
  cloud(420 - t * 4, 260, 38, 15, 312);
  ground(o.gy || GY);
}
