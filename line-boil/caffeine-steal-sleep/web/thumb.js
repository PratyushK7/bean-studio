// Thumbnail (1280 x 720): "HOW DOES CAFFEINE STEAL YOUR SLEEP?", the title's own question, TED-Ed style. The subject is a giant
// steaming red coffee mug on a small yellow bedside table in the middle of a flat dark-blue night; just right of it YOU sits bolt
// upright in bed against the headboard, blanket bunched to its chest, eyes stretched huge with tiny pupils and dark bags.
// A big yellow moon top right. The words run down the left; nothing important goes in the bottom-right corner (the duration badge).
// The mug is drawn here, big and front-on, not with cast.js's mug() (which the video shares and which stays as it is).
CAP.on = false;

const NIGHT = '#123b66';   // the dark-blue night: the palette's blue, darkened, so the red mug, the paper steam and the bean pop

// a big mug seen from the front: (x, y) = bottom centre, h = height, rw = half-width at the rim, handle on the right
function bigMug(x, y, h, rw, seed) {
  const top = y - h, bw = rw * 0.96, e = rw * 0.2;
  const arc = (k0, k1, dy) => Array.from({ length: 13 }, (_, i) => { const a = lerp(k0, k1, i / 12); return [x + Math.cos(a) * rw, top + Math.sin(a) * e + dy]; });
  // the handle, a thick red loop behind the body's right edge
  tube([[x + rw - 16, top + h * 0.2], [x + rw + h * 0.15, top + h * 0.2], [x + rw + h * 0.21, top + h * 0.46], [x + rw + h * 0.13, top + h * 0.72], [x + bw - 14, top + h * 0.76]], h * 0.11, RED, seed + 1);
  // the body, its top edge the near half of the rim
  shape([...arc(Math.PI, 0, 0), [x + bw, y - 16], [x + bw - 18, y], [x - bw + 18, y], [x - bw, y - 16]], RED, 5, seed, 1.2, 4);
  // the rim and the coffee inside
  shape(blobPts(x, top, rw, e, seed + 2, 18, 0.01), RED, 4.6, seed + 2, 1);
  fillOnly(blobPts(x, top + 4, rw - 14, e - 7, seed + 3, 16, 0.02), INK, seed + 3);
  // a paper shine down the left side
  line([[x - rw * 0.66, top + h * 0.26], [x - rw * 0.7, top + h * 0.5], [x - rw * 0.64, top + h * 0.72]], 11, seed + 4, PAPER, 1, true);
  return { top, e };
}

// thick paper-white steam: an S-curl rising from (x, y), ending in a little hook
function steamCurl(x, y, len, dir, w, seed) {
  const pts = [];
  for (let i = 0; i <= 10; i++) { const u = i / 10; pts.push([x + Math.sin(u * TAU * 0.95) * 20 * dir + u * 8 * dir, y - u * len]); }
  const [ex, ey] = pts[pts.length - 1];
  pts.push([ex + 14 * dir, ey - 12], [ex + 24 * dir, ey + 2]);
  tube(pts, w, PAPER, seed);
}

// a bed seen from the front, (x, y) = floor under the middle, w = width: the tall arched headboard, the mattress and the pillow
// against the headboard. Returns the mattress top y.
function frontBed(x, y, w, seed) {
  const top = y - 74, x0 = x - w / 2, x1 = x + w / 2, hb = top - 170;
  // the headboard: an arched yellow panel between two posts with round knobs, framing the sitter's head
  shape([[x0 + 14, top], [x0 + 14, hb + 34], [x - w * 0.26, hb + 8], [x, hb], [x + w * 0.26, hb + 8], [x1 - 14, hb + 34], [x1 - 14, top]], YEL, 4.4, seed, 1.2, 5);
  [x0 + 4, x1 - 24].forEach((px, i) => {
    shape(boxPts(px, hb + 30, 20, y - hb - 30, seed + 1 + i), YEL, 4, seed + 1 + i, 1);
    shape(blobPts(px + 10, hb + 22, 14, 13, seed + 3 + i, 8, 0.05), YEL, 4, seed + 3 + i, 1);
  });
  // the mattress, its front edge toward us, and the pillow propped against the headboard
  shape(boxPts(x0 - 6, top, w + 12, 40, seed + 5), PAPER, 4, seed + 5, 1);
  shape(blobPts(x, top - 66, w * 0.44, 44, seed + 6, 12, 0.04), PAPER, 4.2, seed + 6, 1);
  return top;
}

// a word set flush left at x0 (bigWord centres its text)
function leftWord(text, x0, y, size, fill, seed) {
  const w = textW(text, size) + size * 0.02 * (text.length - 1);
  bigWord(text, x0 + w / 2, y, size, fill, seed);
}
// the biggest size at which text fits maxW, capped at maxS
const fit = (txt, maxW, maxS) => Math.min(maxS, maxS * maxW / (textW(txt, maxS) + maxS * 0.02 * (txt.length - 1)));

shot(0, {
  draw(lt, t) {
    paper(NIGHT);
    // a few stars, kept off the words, the mug and the moon
    [[470, 40], [650, 70], [724, 26], [700, 150], [462, 128], [770, 96]].forEach(([x, y], i) => {
      const r = 2 + rnd(9402, i) * 2; fillOnly(blobPts(x, y, r, r, 9410 + i, 6), PAPER, 9410 + i);
    });
    shape(blobPts(906, 62, 84, 84, 9420, 18, 0.015), YEL, 4.6, 9420, 1);                  // the big moon, top right
    ground(478, 9430, { fill: INK, grass: false });

    // the bed, seen from the front, just right of the table
    const top = frontBed(836, 478, 256, 9440);

    // YOU, bolt upright against the headboard, fists clutching the blanket: drawn without eyes or mouth, then given huge ones
    const P = Object.assign(poseAt([{ t: 0 }], 0), {
      x: 836, y: top + 8, size: 1.75, facing: -1, eyes: 'none', brow: 0, browY: 22, mouth: 'none',
      aL: -0.15, aR: 0.15, bend: -1.35, reach: 0.62, breathe: 0, blink: false,
    });
    const s = YOU.size * P.size, fx0 = YOU.w * 0.12, fy = -YOU.h * 0.64;
    const A = drawChar(YOU, P, { shadow: false });
    const fc = tp(YOU, P, fx0, fy);
    [-1, 1].forEach((side, i) => {
      const [ex, ey] = tp(YOU, P, fx0 + side * YOU.w * 0.3, fy), rx = 12 * s, ry = 15 * s;
      // dark bags: a night-blue crescent and an ink crease under each eye
      fillOnly([[ex - rx * 0.95, ey + ry * 0.55], [ex, ey + ry * 1.32], [ex + rx * 0.95, ey + ry * 0.55], [ex, ey + ry * 0.95]], NIGHT, 9500 + i);
      line([[ex - rx * 0.85, ey + ry * 1.0], [ex, ey + ry * 1.42], [ex + rx * 0.85, ey + ry * 1.0]], 3.6, 9502 + i, INK, 0.6);
      // the stretched eye and a tiny pupil, glancing at the mug
      shape(blobPts(ex, ey, rx, ry, 9504 + i, 10, 0.05), PAPER, 4.4, 9504 + i, 1);
      fillOnly(blobPts(ex - rx * 0.32, ey - ry * 0.05, 3.4, 3.8, 9506 + i, 7), INK, 9506 + i, 0.4);
      // worried brows: the inner end (toward the middle of the face) high
      const by = ey - ry - 12, k = Math.sign(fc[0] - ex);
      line([[ex - k * rx * 0.9, by + 6], [ex + k * rx * 0.9, by - 10]], 7, 9508 + i, INK, 0.6);
    });
    // a tight, wobbly worried mouth
    const [mx, my] = tp(YOU, P, fx0, -YOU.h * 0.42);
    line([[mx - 22, my + 2], [mx - 11, my - 5], [mx, my + 2], [mx + 11, my - 5], [mx + 22, my + 2]], 5, 9512, INK, 0.5);
    // a bead of sweat at the far temple
    const [sx, sy] = tp(YOU, P, -YOU.w * 0.86, -YOU.h * 0.72);
    drop(sx + 4, sy, 9, 9514);

    // the blanket, bunched up to the chest under the fists and draped over the front of the mattress
    const [hL, hR] = A.hands, hy = (hL[1] + hR[1]) / 2, bx = P.x;
    shape([[bx - 124, top + 30], [bx - 120, top - 6], [bx - 96, hy + 20], [hL[0] - 14, hy + 6], [hL[0] + 20, hy + 10], [bx + 6, hy + 2],
      [hR[0] - 18, hy + 10], [hR[0] + 14, hy + 6], [bx + 98, hy + 20], [bx + 122, top - 6], [bx + 126, top + 30], [bx + 60, top + 34], [bx, top + 28], [bx - 64, top + 34]],
      BLUE, 4.4, 9520, 1.2, 5);
    [[hL[0] - 2, hy + 22, hL[0] - 14, top + 22], [bx + 4, hy + 16, bx + 2, top + 18], [hR[0] + 2, hy + 22, hR[0] + 16, top + 22]].forEach(([x0, y0, x1, y1], i) =>
      line([[x0, y0], [(x0 + x1) / 2 + 5, (y0 + y1) / 2], [x1, y1]], 3.2, 9522 + i, INK, 0.8));
    // two fists clutching its top edge
    [hL, hR].forEach(([x, y], i) => {
      shape(blobPts(x, y + 2, 15, 13, 9530 + i, 8, 0.08), PAPER, 4, 9530 + i, 1);
      [-6, 1, 8].forEach((dx, k) => line([[x + dx - 1, y + 3], [x + dx + 1, y + 13]], 2.8, 9532 + i * 4 + k, INK, 0.5, false));
    });

    // the small bedside table
    shape(boxPts(436, 400, 208, 18, 9540), YEL, 4, 9540, 1);
    shape(boxPts(450, 418, 180, 60, 9541), YEL, 4, 9541, 1);
    shape(boxPts(468, 428, 144, 34, 9542), YEL, 3, 9542, 0.8);
    shape(blobPts(540, 445, 6, 6, 9543, 7), RED, 2.6, 9543, 0.6);

    // the subject: the giant mug, steaming
    const M = bigMug(540, 402, 238, 104, 9550);
    steamCurl(498, M.top - 8, 100, -1, 15, 9560);
    steamCurl(542, M.top - 12, 122, 1, 17, 9562);
    steamCurl(586, M.top - 8, 94, -1, 14, 9564);

    // the words: the title's own question, the topic nouns biggest and yellow
    const x0 = 22, cw = 390;
    leftWord('HOW DOES', x0, 92, fit('HOW DOES', cw * 0.9, 74), PAPER, 9600);
    leftWord('CAFFEINE', x0, 196, fit('CAFFEINE', cw, 104), YEL, 9610);
    leftWord('STEAL YOUR', x0, 282, fit('STEAL YOUR', cw * 0.95, 74), PAPER, 9620);
    leftWord('SLEEP?', x0, 400, fit('SLEEP?', cw, 124), YEL, 9630);
  },
});
