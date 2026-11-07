// CHAPTER 3: "Why sunsets are red" (script lines 7 to 9). The last shot closes the iris, as in every video.

musicMood(at('At sunset'), 'calm');
musicMood(at('Only') - 0.25, 'silent');                 // a pause, so the line lands with nothing under it
musicMood(at('So the sky'), 'triumphant');              // the callback and the payoff

// 8. "At sunset, the light travels through so much air that most of the blue is bounced away before it reaches you."
{
  const t0 = at('At sunset'), HZ = GY - 10, tb = at('bounced');
  const sun = [{ t: t0, x: 760, y: 360, size: 1.4, expr: 'sleepy', arms: 'down', look: [-4, 1] }];
  const mo = [
    { t: t0, x: 150, y: GY, size: 1.05, facing: 1, look: [4, -1], expr: 'curious' },
    { t: at('reaches you'), expr: 'happy', ease: 'hold' },
  ];
  const motes = Array.from({ length: 22 }, (_, i) => [230 + rnd(600, i) * 420, 280 + rnd(601, i) * 130]);
  cue(tb, 'slide_up', 0.7); cue(tb + 0.1, 'pop', 0.6);
  shot(t0, {
    draw(lt, t) {
      band(YEL, 0, HZ, 320); band(RED, 0, 170, 321);
      drawChar(SUN, poseAt(sun, t));
      ground(HZ, 330, { fill: PAPER, grass: false });
      motes.forEach(([x, y], i) => fillOnly(blobPts(x, y, 4, 4, 610 + i, 6), INK, 610 + i));
      const L = Math.max(0, (t - at('light travels')) * 200);
      [[RED, -14, 'happy'], [YEL, 4, 'smile'], [BLUE, 22, 'o']].forEach(([col, off, f], i) => {
        const lim = col === BLUE ? Math.min(L, t > tb ? 0 : 300) : L;
        if (lim <= 0) return;
        const x0 = 700, y0 = 360 + off, dx = -0.97, dy = 0.24;
        lightWave(x0, y0, x0 + dx * Math.min(lim, 480), y0 + dy * Math.min(lim, 480), col, 58, 9, -t * 8 + i, 620 + i * 10, f);
      });
      for (let k = 0; k < 4; k++) scatter(t, tb + k * 0.12, 560 - k * 60, 380 + k * 12, 650 + k * 10, 3, 320);
      drawChar(MO, poseAt(mo, t));
    },
  });
}

// 9. "Only the reds and yellows make it through."  A close-up as the warm light arrives (captions moved to the top for it).
{
  const t0 = at('Only');
  const mo = [
    { t: t0, x: 480, y: GY + 20, size: 1.45, look: [4, -1], expr: 'curious' },
    { t: at('make'), expr: 'love', ease: 'hold' },
  ];
  cue(at('through', 2), 'sparkle');
  shot(t0, {
    tr: 'smear', cap: 'top',
    draw(lt, t) {
      band(YEL, 0, GY - 10, 340); ground(GY + 20, 341, { grass: false });
      const L = Math.max(0, (t - t0 - 0.1) * 420);
      [[RED, -14, 'happy'], [YEL, 14, 'smile']].forEach(([col, off, f], i) => {
        const x0 = 940, y0 = 190 + off, x1 = x0 - Math.min(L, 330), y1 = y0 + Math.min(L, 330) * 0.3;
        lightWave(x0, y0, x1, y1, col, 56, 8, -t * 8 + i, 700 + i * 10, f);
      });
      drawChar(MO, poseAt(mo, t));
    },
  });
}

// 10. "So the sky isn't painted blue. It's sunlight, bouncing around, just for you."  Wave goodbye, iris out.
{
  const t0 = at('So the sky');
  const mo = [
    { t: t0, x: 480, y: GY, size: 1.15, look: [0, -4], expr: 'curious' },
    ...A.shake(at('painted') - 0.15, 2),
    ...A.cheer(at('bouncing') - 0.3, GY, { height: 26 }),
    { t: at('just') - 0.1, look: [0, 1], expr: 'happy', ease: 'hold' },
    ...A.wave(at('just'), VO_END(), 'R'),
  ];
  const sun = [{ t: t0, x: 790, y: 120, size: 0.8, expr: 'happy', arms: 'out' }];
  const mols = [[170, 170], [480, 90], [330, 250]].map(([x, y]) => ({ x, y, keys: [{ t: t0, x, y, size: 0.8, expr: 'happy', breathe: 2 }] }));
  for (let k = 0; k < 6; k++) cue(at("It's", 2) + k * 0.45, 'pop', 0.45);
  shot(t0, {
    tr: 'iris', iris: [492, 290],
    draw(lt, t) {
      skyScene(t);
      drawChar(SUN, poseAt(sun, t));
      for (let k = 0; k < 6; k++) { const m = mols[k % 3]; scatter(t, at("It's", 2) + k * 0.45, m.x, m.y, 800 + k * 10, 4, 260); }
      mols.forEach((m, i) => { const P = poseAt(m.keys, t); P.y += Math.sin(t * 3 + i) * 5; drawChar(MOLS[i], P); });
      drawChar(MO, poseAt(mo, t));
    },
  });
}
