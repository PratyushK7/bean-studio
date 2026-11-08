// Thumbnail (build.py thumb): the subject first. A huge Venus with a face, a melting lead ingot, Lost sweating.
// Subject test: the picture alone says "hot planet, melting metal, one stranded bean". Text test: MELTS LEAD! is the stake and does not repeat the title.
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(BLUE);
    const cx = 270, cy = 620;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#2a8fd0');
    }
    gridSafe(() => {
      bigWord('MELTS', 270, 175, 118, PAPER, 9400);
      bigWord('LEAD!', 270, 290, 104, YEL, 9410);
      // Venus, huge, with a heat burst
      burst(340, 590, 215, 262, 9100, 0);
      planet(340, 590, 205, RED, 9110, 'o', 'acid');
      // the lead ingot, sagging into a puddle
      lead(380, 905, 0.55, 9120);
      // Lost, sweating
      const P = poseAt([{ t: 0, x: 140, y: 880, size: 1.45, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -14, arms: 'out', sy: 1.06, sx: 0.96, look: [4, -2], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
      fillOnly(blobPts(142, 886, 90, 11, 9130, 10), INK, 9130);
      drawChar(LOST, P, { t: 0, shadow: false });
      [[60, 560, 1], [470, 420, -1]].forEach(([x, y], i) => wisp(x, y, 70, 9140 + i, 0, YEL, 4));
    });
  },
});
