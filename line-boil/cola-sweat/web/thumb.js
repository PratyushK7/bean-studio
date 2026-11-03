// Thumbnail (build.py thumb): Jo mid-panic, spraying cola, wasps closing in. Text: WASP MAGNET!
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(BLUE);
    // paper sunburst behind Jo, so the yellow bean pops off the blue
    const cx = 270, cy = 640;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#2a8fd0');
    }
    shape(blobPts(cx, cy, 225, 225, 9100, 18, 0.03), PAPER, 0, 9100);
    // Jo, mid-panic
    const P = poseAt([{ t: 0, x: 270, y: 870, size: 1.5, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -14, arms: 'out', sy: 1.08, sx: 0.95, look: [-3, -2], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(272, 875, 108, 12, 9110, 10), INK, 9110);
    drawChar(JO, P, { t: 0, shadow: false });
    patch(JO, P, [[-0.62, -0.55, 0.16], [-0.45, -0.16, 0.15], [0.7, -0.3, 0.14]], 1, 1510);
    patch(JO, P, STAINS, 1, 1600, false);
    // cola spraying off in every direction
    [[125, 560, 12], [415, 540, 13], [95, 680, 10], [450, 670, 11], [175, 450, 9], [375, 440, 9], [490, 590, 8], [60, 600, 8]].forEach(([x, y, r], i) => colaDrop(x, y, r, 9200 + i * 9));
    // wasps closing in, with speed lines
    [[105, 420, 2.3, 1], [455, 470, 2.0, -1], [440, 330, 1.7, -1]].forEach(([x, y, s, dir], i) => {
      speedLines(x - dir * 42 * s / 2, y, [dir, 0.15], 70, 12, 9300 + i * 10, 3);
      wasp(x, y, s, 9320 + i * 20, dir);
    });
    // the words
    bigWord('WASP', 270, 175, 118, PAPER, 9400);
    bigWord('MAGNET!', 270, 290, 104, YEL, 9410);
  },
});
