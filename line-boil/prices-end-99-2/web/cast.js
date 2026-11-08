// Why do prices end in .99? Cast and topic props.

// Shopkeeper: a wide blue bean in a yellow cap and glasses, deadpan
const SHOP = makeChar({ shape: 'wide', color: BLUE, size: 1.15, seed: 21, hat: { kind: 'cap', color: YEL }, glasses: true, belly: PAPER });
// Shopper: a plain red bean with a tuft, the viewer's stand-in
const SHOPPER = makeChar({ shape: 'bean', color: RED, size: 1.35, seed: 22, hair: 'tuft', hairColor: INK });
// Brain: a tiny paper bean with red spots and a sprout, floats, does the rounding
const BRAIN = makeChar({ shape: 'tiny', color: PAPER, spots: RED, size: 1.5, seed: 23, legs: false, eye: 1.1, hat: { kind: 'sprout', color: RED } });
// Scientist: a tall yellow bean with glasses (the studies)
const SCI = makeChar({ shape: 'tall', color: YEL, size: 1.2, seed: 24, glasses: true, cheeks: RED });
// customers: tiny blue beans, a crowd is one object
const CUST = [31, 32, 33, 34, 35, 36].map(s => makeChar({ shape: 'tiny', color: s % 2 ? BLUE : RED, size: 1.0, seed: s, eye: 0.9 }));

const GY = 800;

// a hanging price tag. first = left digit part, rest = the cents. o: s scale, hi lights the first digit,
// restK shrinks the cents (0 = gone), rot tilt, sx flip squash, fill tag colour
function priceTag(x, y, first, rest, seed, o = {}) {
  const s = o.s || 1, size = 74 * s, w = 250 * s, h = 124 * s;
  ctx.save();
  ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(o.sx == null ? 1 : o.sx, 1);
  line([[0, -h / 2], [4 * s, -h / 2 - 50 * s]], 3, seed + 1);
  shape(boxPts(-w / 2, -h / 2, w, h, seed), o.fill || BLUE, 4, seed + 2);
  fillOnly(blobPts(-w / 2 + 20 * s, 0, 7 * s, 7 * s, seed + 3, 8), PAPER, seed + 3);
  ctx.font = `700 ${size}px CapFont, sans-serif`;
  const wf = ctx.measureText(first).width, k = o.restK == null ? 1 : o.restK;
  const rs = size * 0.78 * k, wr = ctx.measureText(rest).width * 0.78 * k;
  const x0 = -(wf + wr) / 2 + 14 * s;
  bigWord(first, x0 + wf / 2, 26 * s, size, o.hi ? YEL : PAPER, seed + 4);
  if (k > 0.05) bigWord(rest, x0 + wf + wr / 2, 26 * s, rs, PAPER, seed + 5);
  ctx.restore();
}
// "SOLD n" board
function soldSign(x, y, n, seed) {
  shape(boxPts(x - 120, y - 40, 240, 80, seed), YEL, 4, seed);
  bigWord('SOLD ' + n, x, y + 17, 46, PAPER, seed + 1);
}
// a table lamp: yellow shade, blue stem, red base
function lamp(x, y, s, seed) {
  shape([[x - 8 * s, y - 120 * s], [x + 8 * s, y - 120 * s], [x + 9 * s, y], [x - 9 * s, y]], BLUE, 3, seed);
  shape([[x - 22 * s, y - 118 * s], [x + 22 * s, y - 118 * s], [x + 14 * s, y - 112 * s], [x - 14 * s, y - 112 * s]], PAPER, 2, seed + 1);
  shape([[x - 26 * s, y - 190 * s], [x + 26 * s, y - 190 * s], [x + 52 * s, y - 118 * s], [x - 52 * s, y - 118 * s]], YEL, 3.5, seed + 2);
  shape(blobPts(x, y - 6 * s, 40 * s, 12 * s, seed + 3, 10), RED, 3, seed + 3);
}
// a coin with a one on it
function coin(x, y, r, seed, face) {
  shape(blobPts(x, y, r, r, seed, 12), YEL, 3, seed);
  if (face) miniFace(x, y, r / 26, 0, seed + 2, face);
  else line([[x - r * 0.25, y - r * 0.35], [x + r * 0.05, y - r * 0.6], [x + r * 0.05, y + r * 0.55]], 3.5, seed + 2);
}
// the shop: a wall, a floor, a counter
function shopSet(t) {
  ground(GY, 402, { fill: PAPER, grass: false });
}
