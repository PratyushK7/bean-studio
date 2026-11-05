// The WIDE (16:9) channel outro, 3.5 s: the same beats as the vertical one. Iris opens on the bean thinking, the cracked bulb flickers on,
// the bean does a take, the bulb pops into the title, the SUBSCRIBE button drops and the bell rings, the bean points, iris closes on the button.
// World 960 x 540: the bean on the left, the title and button on the right.
{
  const GY = 450, BX = 650, tOn = 0.6, tPop = 1.25, tTitle = 1.4, tBtn = 1.85, tPoint = 2.2;
  const bean = [
    { t: 0, x: 215, y: GY, size: 1.15, arms: 'chin', expr: 'thinking', look: [2, -4] },
    ...A.take(0.9, { hold: 0.15, eyes: 'open', mouth: 'grin', arms: 'chin' }),
    { t: 1.35, expr: 'smug', mouth: 'grin', look: [3, -3], arms: 'chin', ease: 'hold' },
    ...A.point(tPoint, 'R', { ang: 1.5, mouth: 'smirk', after: 'smirk' }),
    { t: tPoint + 0.6, expr: 'smug', look: [4, 1], ease: 'hold' },
  ];
  [0.6, 0.68, 0.76].forEach(t => cue(t, 'tick', 0.6));
  cue(tPop, 'pop'); cue(tPop + 0.05, 'sparkle', 0.8); cue(tBtn + 0.2, 'thud', 0.7); cue(tBtn + 0.3, 'ding');
  shot(0, {
    tr: 'iris', iris: [BX, GY - 32],
    draw(lt, t) {
      paper(BLUE);
      cloud(130, 100, 56, 20, 5001); cloud(860, 130, 46, 17, 5002);
      ground(GY, 5010, { fill: PAPER });
      // the bad idea
      const flick = t >= tOn && t < 0.85 ? DRAWING % 2 : t >= 0.85 ? 1 : 0;
      if (t < tPop) badBulb(325, 245, 28, 5020, flick);
      else if (t < tPop + 3 * D) burst(325, 240, 30 + (t - tPop) * 300, 70 + (t - tPop) * 320, 5030, DRAWING % 2, 10);
      // sparkles fly from the bulb to the title
      if (t >= tPop && t < tTitle + 0.35) for (let i = 0; i < 6; i++) {
        const u = clamp((t - tPop) / 0.4, 0, 1), tx = 450 + i * 66, ty = 165;
        plus(lerp(325, tx, EASE.out(u)), lerp(245, ty, EASE.out(u)) - Math.sin(u * Math.PI) * 50, 7 - u * 3, 5040 + i * 3);
      }
      // the title
      const pop = base => i => EASE.back(clamp((t - base - i * 0.035) / (3 * D), 0, 1));
      letters('THE BEAN WITH', 650, 165, 40, PAPER, 5100, pop(tTitle));
      letters('BAD IDEAS', 650, 250, 80, YEL, 5200, pop(tTitle + 0.2), 3);
      if (t > tTitle + 0.6) line([[430, 270], [650, 278], [870, 267]], 6, 5300, INK, 1.2);
      // the button drops and bounces
      if (t >= tBtn) {
        const u = clamp((t - tBtn) / 0.2, 0, 1), k = t - tBtn - 0.2;
        const y = lerp(-120, GY, EASE.in(u));
        const sq = k < 0 ? 1.1 : k < D ? 0.7 : k < 2 * D ? 1.12 : k < 3 * D ? 0.95 : 1;
        const w = 240 / Math.sqrt(sq), h = 66 * sq;
        if (k < 0) speedLines(BX, y - h - 10, [0, 1], 70, 30, 5400, 4);
        shape(boxPts(BX - w / 2, y - h, w, h, 5410), RED, 4.2, 5410, 1.2);
        ctx.save();
        ctx.translate(BX, y - h / 2 + 11 * sq);
        ctx.scale(1 / Math.sqrt(sq), sq);
        letters('SUBSCRIBE', 0, 0, 33, PAPER, 5420, () => 1, 1.5);
        ctx.restore();
        if (k >= 0 && k < 3 * D) [[-1, -1], [1, -1]].forEach(([sx], i) => line([[BX + sx * (w / 2 + 8), GY - 6], [BX + sx * (w / 2 + 34), GY - 14]], 3, 5430 + i));
        // the bell rings once it lands
        const ring = k > 0.1 ? Math.sin((k - 0.1) * 30) * Math.max(0, 1 - (k - 0.1) * 1.6) * 0.5 : 0;
        bell(BX + 150, y - h - 26, 1.2, 5440, ring);
        if (Math.abs(ring) > 0.05) { line([[BX + 178, y - h - 50], [BX + 190, y - h - 60]], 2.6, 5450); line([[BX + 182, y - h - 30], [BX + 197, y - h - 32]], 2.6, 5451); }
      }
      drawChar(BEAN, poseAt(bean, t));
      // the iris opens at the start
      if (t < 0.5) iris(240, 380, lerp(0, 1000, EASE.in(t / 0.5)));
    },
  });
}
