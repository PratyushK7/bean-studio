// One shot, 3.5 s: iris opens on the bean thinking, the cracked bulb flickers on, the bean does a take,
// the bulb pops into the title, the SUBSCRIBE button drops in, the bean points at it, iris closes on the button.
{
  const GY = 700, BX = 400, tOn = 0.6, tPop = 1.25, tTitle = 1.4, tBtn = 1.85, tPoint = 2.2;
  const bean = [
    { t: 0, x: 175, y: GY, arms: 'chin', expr: 'thinking', look: [2, -4] },
    ...A.take(0.9, { hold: 0.15, eyes: 'open', mouth: 'grin', arms: 'chin' }),
    { t: 1.35, expr: 'smug', mouth: 'grin', look: [3, -3], arms: 'chin', ease: 'hold' },
    ...A.point(tPoint, 'R', { ang: 1.75, mouth: 'smirk', after: 'smirk' }),
    { t: tPoint + 0.6, expr: 'smug', look: [4, 1], ease: 'hold' },
  ];
  [0.6, 0.68, 0.76].forEach(t => cue(t, 'tick', 0.6));
  cue(tPop, 'pop'); cue(tPop + 0.05, 'sparkle', 0.8); cue(tBtn + 0.2, 'thud', 0.7); cue(tBtn + 0.3, 'ding');
  shot(0, {
    tr: 'iris', iris: [BX, GY - 32],
    draw(lt, t) {
      paper(BLUE);
      cloud(90, 120, 48, 18, 5001); cloud(470, 420, 40, 15, 5002);
      ground(GY, 5010, { fill: PAPER });
      // the bad idea
      const flick = t >= tOn && t < 0.85 ? DRAWING % 2 : t >= 0.85 ? 1 : 0;
      if (t < tPop) badBulb(212, 385, 30, 5020, flick);
      else if (t < tPop + 3 * D) burst(212, 380, 30 + (t - tPop) * 300, 70 + (t - tPop) * 320, 5030, DRAWING % 2, 10);
      // sparkles fly from the bulb to the title
      if (t >= tPop && t < tTitle + 0.35) for (let i = 0; i < 6; i++) {
        const u = clamp((t - tPop) / 0.4, 0, 1), tx = 90 + i * 72, ty = 290;
        plus(lerp(212, tx, EASE.out(u)), lerp(380, ty, EASE.out(u)) - Math.sin(u * Math.PI) * 50, 7 - u * 3, 5040 + i * 3);
      }
      // the title
      const pop = base => i => EASE.back(clamp((t - base - i * 0.035) / (3 * D), 0, 1));
      letters('THE BEAN WITH', 270, 215, 38, PAPER, 5100, pop(tTitle));
      letters('BAD IDEAS', 270, 300, 74, YEL, 5200, pop(tTitle + 0.2), 3);
      if (t > tTitle + 0.6) line([[70, 320], [270, 328], [470, 317]], 6, 5300, INK, 1.2);
      // the button drops and bounces
      if (t >= tBtn) {
        const u = clamp((t - tBtn) / 0.2, 0, 1), k = t - tBtn - 0.2;
        const y = lerp(-120, GY, EASE.in(u));
        const sq = k < 0 ? 1.1 : k < D ? 0.7 : k < 2 * D ? 1.12 : k < 3 * D ? 0.95 : 1;
        const w = 220 / Math.sqrt(sq), h = 64 * sq;
        if (k < 0) speedLines(BX, y - h - 10, [0, 1], 70, 30, 5400, 4);
        shape(boxPts(BX - w / 2, y - h, w, h, 5410), RED, 4.2, 5410, 1.2);
        ctx.save();
        ctx.translate(BX, y - h / 2 + 11 * sq);
        ctx.scale(1 / Math.sqrt(sq), sq);
        letters('SUBSCRIBE', 0, 0, 31, PAPER, 5420, () => 1, 1.5);
        ctx.restore();
        if (k >= 0 && k < 3 * D) [[-1, -1], [1, -1]].forEach(([sx], i) => line([[BX + sx * (w / 2 + 8), GY - 6], [BX + sx * (w / 2 + 34), GY - 14]], 3, 5430 + i));
        // the bell rings once it lands
        const ring = k > 0.1 ? Math.sin((k - 0.1) * 30) * Math.max(0, 1 - (k - 0.1) * 1.6) * 0.5 : 0;
        bell(BX + 100, y - h - 26, 1.2, 5440, ring);
        if (Math.abs(ring) > 0.05) { line([[BX + 128, y - h - 50], [BX + 140, y - h - 60]], 2.6, 5450); line([[BX + 132, y - h - 30], [BX + 147, y - h - 32]], 2.6, 5451); }
      }
      drawChar(BEAN, poseAt(bean, t));
      // the iris opens at the start
      if (t < 0.5) iris(212, 560, lerp(0, 720, EASE.in(t / 0.5)));
    },
  });
}
