// Thumbnail (build.py thumb): the subject first. A huge cola can, Jo sweating the same dark fizz, wasps arriving.
// Subject test: the picture alone says "cola, sweat, wasps". Text test: WASP MAGNET! is the stake, and does not repeat the title.
CAP.on = false;
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(BLUE);
    const cx = 270, cy = 660;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#2a8fd0');
    }
    shape(blobPts(cx, cy, 235, 225, 9100, 18, 0.03), PAPER, 0, 9100);
    // the words
    bigWord('WASP', 270, 175, 118, PAPER, 9400);
    bigWord('MAGNET!', 270, 290, 104, YEL, 9410);
    // the can, big, on the right: it is what the video is about
    fillOnly(blobPts(400, 905, 105, 12, 9120, 10), INK, 9120);
    can(400, 905, 4.4, 9130);
    // Jo, sweating the same dark fizz
    const P = poseAt([{ t: 0, x: 175, y: 880, size: 1.45, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -14, arms: 'out', sy: 1.06, sx: 0.96, look: [4, -2], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(177, 886, 100, 12, 9110, 10), INK, 9110);
    drawChar(JO, P, { t: 0, shadow: false });
    patch(JO, P, [[-0.62, -0.55, 0.16], [-0.45, -0.16, 0.15], [0.7, -0.3, 0.14]], 1, 1510);
    patch(JO, P, STAINS, 1, 1600, false);
    // dark fizz spraying off Jo and the can
    [[60, 640, 12], [290, 590, 11], [95, 760, 10], [330, 700, 9], [215, 500, 9], [470, 600, 10], [60, 540, 8]].forEach(([x, y, r], i) => colaDrop(x, y, r, 9200 + i * 9));
    // wasps closing in
    [[110, 440, 2.2, 1], [440, 470, 2.0, -1]].forEach(([x, y, s, dir], i) => {
      speedLines(x - dir * 42 * s / 2, y, [dir, 0.15], 70, 12, 9300 + i * 10, 3);
      wasp(x, y, s, 9320 + i * 20, dir);
    });
  },
});
