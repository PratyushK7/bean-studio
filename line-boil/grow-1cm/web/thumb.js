// Thumbnail (build.py thumb): Bo mid-growth, shocked, tiny trousers at his ankles, Pip unimpressed. Text: TOO TALL!
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(YEL);
    // sunburst behind Bo so the red bean pops off the yellow
    const cx = 270, cy = 620;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ffd965');
    }
    shape(blobPts(cx, cy, 230, 260, 9100, 18, 0.03), BLUE, 0, 9100);
    // Bo, mid-growth
    const P = poseAt([{ t: 0, x: 270, y: 900, size: 3.1, expr: 'shocked', eyes: 'wide', mouth: 'o', brow: -0.7, browY: -14, arms: 'up', look: [0, -4], fx: ['take'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(272, 905, 120, 12, 9110, 10), INK, 9110);
    drawChar(YOU, P, { t: 0, shadow: false });
    trousers(270, 850, 1.3, 9120);
    // growth arrows
    arrow([70, 760], [70, 460], 9130, RED, 0.1);
    arrow([470, 760], [470, 460], 9132, RED, -0.1);
    // Pip, unimpressed
    drawChar(PIP, poseAt([{ t: 0, x: 440, y: 900, size: 1.5, expr: 'smug', look: [-3, -3], breathe: 0, blink: false }], 0), { t: 0 });
    // the words
    bigWord('TOO', 270, 175, 118, PAPER, 9400);
    bigWord('TALL!', 270, 290, 118, RED, 9410);
  },
});
