// What if you pooped a watermelon? Cast and topic props.

// Kid: a red bean in a blue cap (the viewer's stand-in)
const KID = makeChar({ shape: 'bean', color: RED, size: 1.2, seed: 3, hat: { kind: 'cap', color: BLUE } });

const GY = 800;   // floor line

// a whole watermelon with a face: blue rind, ink stripes. (x, y) is its centre.
function melon(x, y, r, seed, o = {}) {
  const rx = r * 1.18 * (o.sx || 1), ry = r * (o.sy || 1), rot = o.rot || 0;
  const c = Math.cos(rot), s = Math.sin(rot), R = (px, py) => [x + px * c - py * s, y + px * s + py * c];
  shape(blobPts(x, y, rx, ry, seed, 12, 0.03, rot), BLUE, 4.4, seed);
  [-0.62, -0.22, 0.22, 0.62].forEach((u, k) => {
    const pts = [];
    for (let i = 0; i <= 8; i++) {
      const v = -0.86 + 1.72 * i / 8;
      pts.push(R(rx * u * Math.sqrt(1 - v * v) + (i % 2 ? 4 : -4), ry * v));
    }
    line(pts, 3, seed + 10 + k);
  });
  // a pale belly patch so the face reads on the blue
  fillOnly(blobPts(...R(0, ry * 0.12), rx * 0.42, ry * 0.36, seed + 20, 9, 0.05, rot), PAPER, seed + 20);
  miniFace(...R(0, ry * 0.12), r / 26, rot, seed + 21, o.face || 'smile', o.look || [0, 0]);
}

// a half-moon slice of watermelon: flat top at (x, y), curved rind below. Red flesh, paper rind, blue skin, ink seeds.
function slice(x, y, r, seed, o = {}) {
  const rot = o.rot || 0, c = Math.cos(rot), s = Math.sin(rot), R = (px, py) => [x + px * c - py * s, y + px * s + py * c];
  const half = (rr) => { const p = []; for (let i = 0; i <= 10; i++) { const a = Math.PI * i / 10; p.push(R(Math.cos(a) * rr * 1.15, Math.sin(a) * rr)); } return p; };
  shape(half(r), BLUE, 3.8, seed);
  fillOnly(half(r * 0.88), PAPER, seed + 1);
  shape(half(r * 0.76), RED, 3, seed + 2);
  [[-0.5, 0.18], [0.5, 0.18], [-0.3, 0.5], [0.3, 0.5], [0, 0.62]].forEach(([fx, fy], i) =>
    fillOnly(blobPts(...R(fx * r, fy * r), r * 0.04, r * 0.07, seed + 5 + i, 6), INK, seed + 5 + i));
  if (o.face) miniFace(...R(0, r * 0.24), r / 26, rot, seed + 12, o.face);
}

// a bite-sized chunk of red melon
function chunk(x, y, s, seed, rot = 0) { shape(boxPts(x - s / 2, y - s / 2, s, s, seed, rot), RED, 3, seed); }

// a water drop with a face
function dropGuy(x, y, r, seed, face = 'happy') {
  drop(x, y, r, seed, BLUE);
  fillOnly(blobPts(x, y + r * 0.1, r * 0.55, r * 0.45, seed + 1, 7), PAPER, seed + 1);
  miniFace(x, y + r * 0.1, r / 24, 0, seed + 2, face);
}

// a sugar cube with a face
function sugar(x, y, s, seed, face = 'happy') {
  shape(boxPts(x - s / 2, y - s / 2, s, s, seed, 0.1), PAPER, 3.2, seed);
  line([[x - s * 0.5, y - s * 0.2], [x - s * 0.2, y - s * 0.5]], 2, seed + 1);
  miniFace(x, y + s * 0.08, s / 34, 0, seed + 2, face);
}

// a seed: an ink teardrop with two paper eyes
function seedGuy(x, y, s, sd, sleepy = true) {
  shape([[x - s, y], [x - s * 0.4, y - s * 0.55], [x + s * 0.7, y - s * 0.4], [x + s * 1.2, y], [x + s * 0.7, y + s * 0.4], [x - s * 0.4, y + s * 0.55]], INK, 2.4, sd, 0.8, 4);
  if (sleepy) { line([[x - s * 0.3, y - s * 0.1], [x + s * 0.0, y - s * 0.1]], 2, sd + 1, PAPER, 0.4); line([[x + s * 0.3, y - s * 0.1], [x + s * 0.6, y - s * 0.1]], 2, sd + 2, PAPER, 0.4); }
  else [[-0.15, -0.1], [0.45, -0.1]].forEach(([fx, fy], i) => fillOnly(blobPts(x + fx * s, y + fy * s, s * 0.12, s * 0.15, sd + 1 + i, 6), PAPER, sd + 1 + i));
}

// a coin: yellow disc with a rim
function coin(x, y, r, seed) {
  shape(blobPts(x, y, r, r, seed, 10, 0.02), YEL, 3.6, seed);
  line(blobPts(x, y, r * 0.7, r * 0.7, seed + 1, 10, 0.03).concat([[x + r * 0.7, y]]), 2.2, seed + 1);
}

// a grain of rice, drawn big, with a face
function rice(x, y, s, seed, face = 'o') {
  shape(blobPts(x, y, s, s * 0.45, seed, 10, 0.04, -0.3), PAPER, 3.2, seed);
  miniFace(x, y, s / 34, -0.3, seed + 1, face);
}

// a gut tube running across the frame; returns nothing. Food rides along its centreline.
function gut(y, seed, color = YEL, w = 90) {
  const pts = wavePts(-60, y, 600, y, 2.2, 22, 0.6, 40);
  tube(pts, w, color, seed);
}
function gutY(x, y) { return y + Math.sin(((x + 60) / 660) * 2.2 * TAU + 0.6) * 22; }

// the bathroom: blue wall, tiles, floor; then the toilet tank (behind the kid)
function bathroom(tx) {
  band(BLUE, 0, 560, 301);
  [[100, 300], [390, 270], [450, 420]].forEach(([x, y], i) => shape(boxPts(x, y, 46, 46, 310 + i, 0.05), BLUE, 2.4, 310 + i));
  ground(GY, 320, { fill: PAPER, grass: false });
  shape(boxPts(tx - 78, 520, 156, 120, 330), PAPER, 4, 330);
  shape(boxPts(tx - 86, 506, 172, 22, 331), PAPER, 3.6, 331);
  line([[tx + 46, 545], [tx + 66, 545]], 4, 332);
}
// the toilet bowl, drawn in front of the kid so it hides their legs
function bowl(tx) {
  shape([[tx - 98, 690], [tx + 98, 690], [tx + 78, 752], [tx + 40, 776], [tx + 44, GY], [tx - 44, GY], [tx - 40, 776], [tx - 78, 752]], PAPER, 4.2, 340);
  shape(blobPts(tx, 690, 104, 20, 341, 10, 0.03), PAPER, 4, 341);
}
