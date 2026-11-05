// CHAPTER 1: "A blue sky, and a puzzle" (script lines 0 to 3). One file per chapter; each shot starts at a word with at('word').

musicMood(0, 'curious');           // the music follows the script: a light, curious tune for the question

// 1. "Look up on a sunny day, and the sky is blue."  Mo points at the sky.
{
  const mo = [
    { t: 0, x: 330, y: GY, size: 1.15, look: [2, -4], expr: 'curious' },
    ...A.point(0.45, 'R', { ang: 2.45, mouth: 'open', after: 'grin' }),
    { t: at('sky', 1), expr: 'happy', ease: 'hold' },
  ];
  const sun = [{ t: 0, x: 790, y: 120, size: 0.8, expr: 'happy', arms: 'out' }];
  shot(0, {
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.05 }],
    draw(lt, t) { skyScene(t); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}

// 2. "But sunlight isn't blue at all."  The Sun shakes its head, Mo does a take.
{
  const t0 = at('But');
  const sun = [
    { t: t0, x: 560, y: 260, size: 1.7, expr: 'neutral', look: [-2, 1] },
    ...A.shake(at("isn't", 1)),
    { t: at('all') + 0.05, arms: 'hips', expr: 'smug', look: [-3, 2], ease: 'hold' },
  ];
  const mo = [
    { t: t0, x: 170, y: GY, size: 0.9, lookAt: [560, 260], expr: 'happy' },
    ...A.take(at("isn't", 1) + 0.1, { hold: 0.5, mouth: 'wavy', browY: -6 }),
  ];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) { band(PAPER, 0, GY, 300); ground(GY); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}

// 3. "It's every colour mixed together, travelling in waves."  The Sun flings out three waves.
{
  const t0 = at("It's", 1), tw = at('mixed') - 0.2;
  const sun = [{ t: t0, x: 170, y: 190, size: 1.3, expr: 'happy' }, ...A.cheer(at('every', 1) - 0.3, 190, { height: 20 })];
  cue(tw, 'zip');
  shot(t0, {
    draw(lt, t) {
      band(PAPER, 0, GY, 300); ground(GY);
      const L = Math.max(0, (t - tw) * 520), wob = t > at('travelling') ? 16 : 10;
      [[RED, -30, 'smile'], [YEL, 0, 'happy'], [BLUE, 30, 'o']].forEach(([col, off, face], i) => {
        const x0 = 270, y0 = 190 + off * 1.4;
        lightWave(x0, y0, x0 + Math.min(L, 640), y0 + Math.min(L, 640) * 0.22, col, 62, wob, -t * 9 + i, 400 + i * 10, face);
      });
      drawChar(SUN, poseAt(sun, t));
    },
  });
}

// 4. "Red light has long, lazy waves. Blue light has short, choppy ones."  Two lanes, two personalities.
{
  const t0 = at('Red', 1), tb = at('Blue light has');
  cue(t0, 'slide_up', 0.6); cue(tb, 'zip');
  shot(t0, {
    draw(lt, t) {
      band(PAPER, 0, GY, 300); ground(GY);
      lightWave(-60, 150, Math.min(900, -40 + (t - t0) * 520), 150, RED, 300, 48, -t * 2.2, 420, 'sleepy');
      if (t > at('long')) arrow([60, 235], [360, 235], 430, RED, 0.12);
      if (t > tb) {
        lightWave(-60, 330, Math.min(900, -40 + (t - tb) * 760), 330, BLUE, 50, 20, -t * 16, 440, 'o');
        if (t > at('short')) arrow([60, 400], [120, 400], 450, BLUE, 0.2);
      }
    },
  });
}
