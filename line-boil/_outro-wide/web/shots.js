// The WIDE (16:9) channel outro, voiced (about 14.7 s). "Thanks for watching." The bean waves; the cracked bulb flickers on and pops into
// the title. "...give it a like and share it with a friend." LIKE and SHARE pop in on their words. "And subscribe..." the SUBSCRIBE
// button drops and the bell rings. "Your next video is right over here." LIKE and SHARE pop out, SUBSCRIBE slides left and the end-screen
// slot draws in on the right; the bean points at it and holds while YouTube's end-screen elements sit on top. World 960 x 540.
musicMood(0, 'upbeat');
{
  const GY = 450, tLike = at('like'), tShare = at('share'), tSub = at('subscribe'), tNext = at('Your next'), tHere = at('here');
  const tOn = 0.15, tPop = 0.75, tTitle = 0.85, tSlide = tNext - 0.1;
  const SLOT = [540, 205, 360, 202];
  const bean = [
    { t: 0, x: 178, y: GY, size: 0.95, expr: 'happy', look: [2, -1] },
    ...A.wave(0.1, 1.15, 'R'),
    { t: 1.2, expr: 'neutral', look: [4, -2], ease: 'hold' },
    ...A.point(tLike - 0.35, 'R', { ang: 1.85, mouth: 'open', after: 'grin' }),
    { t: tShare - 0.12, aR: 1.62, ease: 'out' },
    { t: tShare + 0.1, look: [4, -1], ease: 'hold' },
    { t: tSub - 0.1, arms: 'down', look: [4, 2], ease: 'io' },
    ...A.take(tSub + 0.25, { hold: 0.35, eyes: 'open', mouth: 'grin' }),
    { t: tSub + 0.9, expr: 'smug', look: [3, 1], ease: 'hold' },
    ...A.nod(at('finds you') - 0.1, 2),
    ...A.point(tNext - 0.3, 'R', { ang: 1.66, mouth: 'smirk', after: 'smirk' }),
    { t: tHere + 0.4, expr: 'smug', look: [1, 0], ease: 'hold' },
    { t: tHere + 1.6, look: [4, 0], ease: 'hold' },
  ];
  [0.15, 0.23, 0.31].forEach(t => cue(t, 'tick', 0.6));
  cue(tPop, 'pop'); cue(tPop + 0.05, 'sparkle', 0.8);
  cue(tLike, 'pop'); cue(tShare, 'pop');
  cue(tSub + 0.2, 'thud', 0.7); cue(tSub + 0.3, 'ding');
  cue(tSlide, 'whoosh', 0.7); cue(tNext + 0.1, 'zip', 0.8);
  shot(0, {
    tr: 'iris', iris: [178, GY - 145],
    draw(lt, t) {
      paper(BLUE);
      cloud(110, 95, 56, 20, 5001); cloud(880, 120, 46, 17, 5002);
      ground(GY, 5010, { fill: PAPER });
      // the bad idea: the bulb flickers on over the bean's head and pops into the title
      const flick = t >= tOn && t < 0.4 ? DRAWING % 2 : t >= 0.4 ? 1 : 0;
      if (t < tPop) badBulb(250, 150, 26, 5020, flick);
      else if (t < tPop + 3 * D) burst(250, 145, 30 + (t - tPop) * 300, 70 + (t - tPop) * 320, 5030, DRAWING % 2, 10);
      if (t >= tPop && t < tTitle + 0.35) for (let i = 0; i < 6; i++) {
        const u = clamp((t - tPop) / 0.4, 0, 1), tx = 440 + i * 64, ty = 110;
        plus(lerp(250, tx, EASE.out(u)), lerp(150, ty, EASE.out(u)) - Math.sin(u * Math.PI) * 40, 7 - u * 3, 5040 + i * 3);
      }
      // the title
      const pop = base => i => EASE.back(clamp((t - base - i * 0.035) / (3 * D), 0, 1));
      letters('THE BEAN WITH', 600, 78, 38, PAPER, 5100, pop(tTitle));
      letters('BAD IDEAS', 600, 152, 72, YEL, 5200, pop(tTitle + 0.2), 3);
      if (t > tTitle + 0.6) line([[420, 170], [600, 177], [780, 167]], 6, 5300, INK, 1.2);
      // LIKE and SHARE pop in on their words and out when the end screen arrives
      scaled(470, 290, popK(t, tLike - 0.05, tSlide), () => askButton('like', 470, 290, 1, 5500, { rot: -0.04 }));
      scaled(710, 290, popK(t, tShare - 0.05, tSlide + 0.05), () => askButton('share', 710, 290, 1, 5520, { rot: 0.04 }));
      // the end-screen slot (YouTube's "next video" element goes here)
      videoSlot(...SLOT, 5600, (t - tNext) / 0.3);
      // SUBSCRIBE drops, bounces, rings the bell, then slides left to make room for the slot
      if (t >= tSub) {
        const u = clamp((t - tSub) / 0.2, 0, 1), k = t - tSub - 0.2;
        const bx = lerp(640, 400, EASE.io(clamp((t - tSlide) / 0.35, 0, 1)));
        const y = lerp(-120, GY, EASE.in(u));
        const sq = k < 0 ? 1.1 : k < D ? 0.7 : k < 2 * D ? 1.12 : k < 3 * D ? 0.95 : 1;
        if (k < 0) speedLines(bx, y - 80, [0, 1], 70, 30, 5400, 4);
        scaled(bx, y, 1, () => { ctx.save(); ctx.translate(bx, y); ctx.scale(1 / Math.sqrt(sq), sq); ctx.translate(-bx, -y); askButton('sub', bx, y - 32, 1, 5410); ctx.restore(); });
        if (k >= 0 && k < 3 * D) [-1, 1].forEach((sx, i) => line([[bx + sx * 123, GY - 6], [bx + sx * 150, GY - 14]], 3, 5430 + i));
        const ring = k > 0.1 ? Math.sin((k - 0.1) * 30) * Math.max(0, 1 - (k - 0.1) * 1.6) * 0.5 : 0;
        bell(bx + 95, y - 100, 1.2, 5440, ring);
        if (Math.abs(ring) > 0.05) { line([[bx + 122, y - 124], [bx + 134, y - 134]], 2.6, 5450); line([[bx + 126, y - 104], [bx + 141, y - 106]], 2.6, 5451); }
      }
      drawChar(BEAN, poseAt(bean, t));
      // the iris opens at the start
      if (t < 0.4) iris(178, 330, lerp(0, 1000, EASE.in(t / 0.4)));
    },
  });
}
