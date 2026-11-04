// Thumbnail (build.py thumb): the subject first. Kit holds up two hands of huge curled yellow nails, the clipper is shown the door.
// Subject test: the picture alone says "enormous fingernails". Text test: CLAWS?! points at the stakes without repeating the title.
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(RED);
    const cx = 270, cy = 650;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ff7276');
    }
    shape(blobPts(cx, cy + 20, 250, 262, 9100, 18, 0.03), PAPER, 0, 9100);
    bigWord('CLAWS?!', 270, 215, 100, YEL, 9400);
    // Kit, both hands up, every finger a huge curled nail
    const P = poseAt([{ t: 0, x: 270, y: 880, size: 1.35, expr: 'shocked', eyes: 'wide', mouth: 'o', brow: -0.7, browY: -14,
      aL: -2.35, aR: 2.35, bend: 0.1, reach: 1, sy: 1.06, sx: 0.96, look: [0, -3], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(272, 886, 120, 13, 9110, 10), INK, 9110);
    drawChar(KIT, P, {
      t: 0, shadow: false,
      hold(hands) {
        hands.forEach((h, k) => {
          const side = k === 0 ? -1 : 1;
          [-0.45, 0.35].forEach((da, i) =>
            nail(nailPath(h[0] + side * 4, h[1] - 4, -Math.PI / 2 + side * (da - 0.05) * 1.0, 175 + i * 22, 0.95, 0, side), 30, 9200 + k * 40 + i * 10, null));
        });
      },
    });
    // the clipper, small and outraged at the side
    snip(425, 770, 2.0, 0.35, 9300, 'o', 0.6);
    // a red "no" over the clipper: never cutting them is the whole video
    const ring = blobPts(425, 760, 105, 105, 9320, 18, 0.01); ring.push(ring[0]);
    tube(ring, 16, RED, 9321);
    tube([[350, 835], [500, 685]], 16, RED, 9322);
    [[70, 560], [480, 470], [80, 760]].forEach(([x, y], i) => plus(x, y, 16, 9310 + i));
  },
});
