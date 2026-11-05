// The 9:16 (Shorts) channel outro, voiced (about 5.4 s): "Like, share, and subscribe for more bad ideas." The title pops in, LIKE and SHARE
// pop in on their words, SUBSCRIBE drops and the bell rings, the bean cheers on "bad ideas" and waves while the iris closes on its face.
// No burned-in captions here: the buttons carry the words. World 540 x 960.
CAP.on = false;
musicMood(0, 'upbeat');
{
  const GY = 760, tLike = at('Like'), tShare = at('share'), tSub = at('subscribe'), tBad = at('bad ideas');
  const BX = 380;
  const bean = [
    { t: 0, x: 168, y: GY, size: 0.95, expr: 'happy', look: [4, -3] },
    ...A.point(Math.max(0.02, tLike - 0.3), 'R', { ang: 2.05, mouth: 'open', after: 'grin' }),
    { t: tShare - 0.1, aR: 1.85, look: [4, -1], ease: 'out' },
    { t: tSub, arms: 'down', look: [4, 2], ease: 'io' },
    ...A.cheer(tBad - 0.3, GY, { height: 30 }),
    { t: tBad + 0.4, expr: 'happy', arms: 'down', look: [0, 0], ease: 'hold' },
    ...A.wave(tBad + 0.45, VO_END(), 'R'),
  ];
  cue(tLike + 0.02, 'pop'); cue(tShare, 'pop'); cue(tSub + 0.2, 'thud', 0.7); cue(tSub + 0.3, 'ding');
  shot(0, {
    tr: 'iris', iris: [168, GY - 155],
    draw(lt, t) {
      paper(BLUE);
      cloud(90, 110, 48, 18, 5001); cloud(470, 380, 40, 15, 5002);
      ground(GY, 5010, { fill: PAPER });
      const pop = base => i => EASE.back(clamp((t - base - i * 0.035) / (3 * D), 0, 1));
      letters('THE BEAN WITH', 270, 205, 38, PAPER, 5100, pop(0.02));
      letters('BAD IDEAS', 270, 290, 74, YEL, 5200, pop(0.2), 3);
      if (t > 0.8) line([[70, 310], [270, 318], [470, 307]], 6, 5300, INK, 1.2);
      scaled(BX, 450, popK(t, tLike), () => askButton('like', BX, 450, 1, 5500, { rot: -0.04 }));
      scaled(BX, 545, popK(t, tShare - 0.05), () => askButton('share', BX, 545, 1, 5520, { rot: 0.04 }));
      if (t >= tSub) {
        const u = clamp((t - tSub) / 0.2, 0, 1), k = t - tSub - 0.2;
        const y = lerp(-120, GY, EASE.in(u));
        const sq = k < 0 ? 1.1 : k < D ? 0.7 : k < 2 * D ? 1.12 : k < 3 * D ? 0.95 : 1;
        if (k < 0) speedLines(BX, y - 80, [0, 1], 70, 30, 5400, 4);
        ctx.save(); ctx.translate(BX, y); ctx.scale(1 / Math.sqrt(sq), sq); ctx.translate(-BX, -y); askButton('sub', BX, y - 32, 0.92, 5410); ctx.restore();
        const ring = k > 0.1 ? Math.sin((k - 0.1) * 30) * Math.max(0, 1 - (k - 0.1) * 1.6) * 0.5 : 0;
        bell(BX + 80, y - 98, 1.2, 5440, ring);
      }
      drawChar(BEAN, poseAt(bean, t));
      if (t < 0.3) iris(168, 640, lerp(0, 1100, EASE.in(t / 0.3)));
    },
  });
}
