// Thumbnail (1280 x 720): "9 HOURS LATER". The subject is the afternoon coffee, still awake at midnight: a huge white mug on a
// bedside table, empty and steamless (drunk hours ago), and the wired red caffeine bean peeking over its rim, eyes locked on YOU,
// asleep in bed below-left. A flat ink-black night with a big full moon behind the bean's spiky hair. The words sit in the
// upper left; nothing important goes in the bottom-right corner (the duration badge).
// On an ink sky every ink outline vanishes, so the mug, its handle and the Zs are drawn in paper with ink edges here,
// not with cast.js's mug() and zzz() (which the video shares and which stay as they are).
CAP.on = false;

// the caffeine bean, a touch bigger in the eye than in the video
const CAFT = makeChar({ shape: 'ball', color: RED, size: 0.75, seed: 37, hair: 'spikes', eye: 1.3 });

// a big empty mug seen from the front: (x, y) = bottom centre, h = height, rw = half-width at the rim
function nightMug(x, y, h, rw, seed) {
  const top = y - h, bw = rw * 0.9, e = rw * 0.17;
  const arc = (k0, k1, dy) => Array.from({ length: 13 }, (_, i) => { const a = lerp(k0, k1, i / 12); return [x + Math.cos(a) * rw, top + Math.sin(a) * e + dy]; });
  return {
    top, e, rw,
    back() {                                                        // the handle, then the far rim and the dark inside
      tube([[x + rw - 14, top + h * 0.2], [x + rw + h * 0.28, top + h * 0.2], [x + rw + h * 0.36, top + h * 0.48], [x + rw + h * 0.24, top + h * 0.74], [x + rw - 18, top + h * 0.76]], h * 0.11, PAPER, seed + 1);
      shape(blobPts(x, top, rw, e, seed + 2, 18, 0.01), PAPER, 4.2, seed + 2, 1);
      fillOnly(blobPts(x, top + 3, rw - 13, e - 6, seed + 3, 16, 0.02), INK, seed + 3);
    },
    front() {                                                       // the body, its top edge the near half of the rim
      shape([...arc(Math.PI, 0, 0), [x + bw, y - 16], [x + bw - 18, y], [x - bw + 18, y], [x - bw, y - 16]], PAPER, 4.6, seed, 1.2, 4);
      line(arc(Math.PI * 0.97, Math.PI * 0.03, 9), 3, seed + 4, INK, 0.6, false);
    },
  };
}

shot(0, {
  draw(lt, t) {
    paper(INK);
    for (let i = 0; i < 16; i++) { const r = 1.6 + rnd(9401, i) * 2.2; fillOnly(blobPts(30 + rnd(9402, i) * 900, 12 + rnd(9403, i) * 240, r, r, 9410 + i, 6), PAPER, 9410 + i); }
    shape(blobPts(684, 136, 156, 156, 9420, 18, 0.015), YEL, 4.4, 9420, 1);            // the full moon, behind the bean's hair
    ground(502, 9430, { fill: BLUE, grass: false });

    // YOU asleep, head on the pillow beside the table (the bed is drawn mirrored so its head end is on the right)
    ctx.save(); ctx.translate(600, 0); ctx.scale(-1, 1);
    const top = bed(300, 504, 400, 9440, { s: 1.4 });
    drawLying(YOU, Object.assign(poseAt([{ t: 0 }], 0), { x: 318, y: top - 34, size: 1.25, eyes: 'closed', mouth: 'smile', breathe: 0, blink: false }), { tilt: 0.22 });
    blanket(245, 480, top, 9450, BLUE, 1.3);
    ctx.restore();
    [[474, 318, 24], [494, 284, 31], [518, 244, 38]].forEach(([x, y, s], i) => ink('Z', x, y, s, PAPER, 9460 + i * 3, 0, 6));

    // the bedside table
    shape(boxPts(548, 414, 270, 92, 9470), RED, 4, 9470, 1);
    shape(boxPts(528, 398, 310, 20, 9471), RED, 4, 9471, 1);
    shape(boxPts(578, 430, 210, 34, 9472), RED, 3, 9472, 0.8);
    shape(blobPts(683, 447, 8, 8, 9473, 7), YEL, 2.6, 9473, 0.6);

    // the mug, and the caffeine bean in it, peering down at the sleeper
    const M = nightMug(680, 402, 216, 128, 9480);
    M.back();
    const P = Object.assign(poseAt([{ t: 0 }], 0), { x: 684, y: M.top + 72, size: 2.35, facing: -1, eyes: 'wide', mouth: 'none', brow: -0.3, browY: -14, look: [3.6, 5], breathe: 0, blink: false });
    const A = drawChar(CAFT, P, { shadow: false });
    // a tight, manic grin: a wide band of clenched teeth
    const [gx, gy] = [A.mouth[0], A.mouth[1] + 12];
    shape([[gx - 44, gy - 9], [gx, gy - 6], [gx + 44, gy - 9], [gx + 36, gy + 9], [gx, gy + 15], [gx - 36, gy + 9]], PAPER, 4, 9481, 0.8, 5);
    line([[gx - 40, gy - 1], [gx, gy + 3], [gx + 40, gy - 1]], 3, 9482, INK, 0.5, false);
    [-26, -9, 9, 26].forEach((dx, i) => line([[gx + dx, gy - 6], [gx + dx * 0.95, gy + 11]], 2.6, 9483 + i, INK, 0.4, false));
    // take lines, thick, on the moon around the head
    const hc = tp(CAFT, P, 0, -CAFT.h * 0.62);
    [-2.8, -2.2, -0.95, -0.35].forEach((a, i) => line([[hc[0] + Math.cos(a) * 114, hc[1] + Math.sin(a) * 118], [hc[0] + Math.cos(a) * 148, hc[1] + Math.sin(a) * 150]], 9, 9488 + i));
    M.front();
    // hands gripping the rim
    [[-1, 572, M.top + 14], [1, 788, M.top + 14]].forEach(([side, hx, hy], i) => {
      shape(blobPts(hx, hy, 14, 12, 9490 + i, 7, 0.08), PAPER, 3.6, 9490 + i, 1);
      [-6, 0, 6].forEach((dx, k) => line([[hx + dx, hy + 2], [hx + dx + side, hy + 13]], 2.6, 9492 + i * 4 + k, INK, 0.5, false));
    });

    // the words
    const fit = (txt, maxW, maxS) => Math.min(maxS, maxS * maxW / (textW(txt, maxS) * 1.12));
    bigWord('9 HOURS', 250, 88, fit('9 HOURS', 470, 130), YEL, 9500);
    bigWord('LATER', 232, 210, fit('LATER', 470, 130), PAPER, 9510);
  },
});
