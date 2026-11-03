// Thumbnail (build.py thumb): Kit in a take as three nails shoot up past their cap. Text: TALLER THAN ME
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(RED);
    // a lighter sunburst and a paper blob behind Kit, so the blue bean pops off the red
    const cx = 270, cy = 620;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ff7276');
    }
    shape(blobPts(cx, cy + 40, 245, 245, 9100, 18, 0.03), PAPER, 0, 9100);
    // Kit, mid-take, one hand up with the nails, the other holding a curl
    const P = poseAt([{ t: 0, x: 255, y: 850, size: 1.5, expr: 'shocked', eyes: 'wide', mouth: 'o', brow: -0.7, browY: -14,
      aL: -1.5, aR: 2.55, bend: 0.1, reach: 1, sy: 1.08, sx: 0.95, lookAt: [330, 300], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(257, 855, 130, 13, 9110, 10), INK, 9110);
    drawChar(KIT, P, {
      t: 0, shadow: false,
      hold(hands) {
        const h = hands[1];
        [-0.16, 0, 0.16].forEach((da, i) =>
          nail(nailPath(h[0], h[1] - 6, -Math.PI / 2 + da, 430 * (1 - Math.abs(i - 1) * 0.08), 0.14, 0, i - 1 || 1), 12, 9200 + i * 10, i === 1 ? 'o' : null, 0.9));
        const g = hands[0];
        nail(nailPath(g[0], g[1], Math.PI * 0.9, 120, 1, 0, -1), 10, 9240, null);
      },
    });
    // Snip gapes from the side
    snip(95, 470, 1.1, -0.5, 9300, 'o', 0.7);
    [[470, 620], [430, 760], [80, 650]].forEach(([x, y], i) => plus(x, y, 16, 9310 + i));
    // the words
    bigWord('TALLER', 270, 190, 120, YEL, 9400);
    bigWord('THAN ME', 270, 305, 104, PAPER, 9410);
  },
});
