// Why is the sky blue? Ten shots, timed to the voiceover with at('word').
// Pose keys are in voiceover seconds; camera keys are in seconds into the shot.

// 1. "Look up on a sunny day, and the sky is blue."  Mo points at the sky.
{
  const mo = [
    { t: 0, x: 230, y: GY, look: [2, -4], expr: 'curious' },
    ...A.point(0.45, 'R', { ang: 2.45, mouth: 'open', after: 'grin' }),
    { t: at('sky', 1), expr: 'happy', ease: 'hold' },
  ];
  const sun = [{ t: 0, x: 455, y: 205, size: 0.55, expr: 'happy', arms: 'out' }];
  shot(0, {
    cam: [{ t: 0, z: 1, y: 520 }, { t: 2.7, z: 1.07, y: 500 }],
    draw(lt, t) { skyScene(t); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}

// 2. "But sunlight isn't blue at all."  The Sun shakes its head; Mo does a take.
{
  const t0 = at('But');
  const sun = [
    { t: t0, x: 280, y: 560, size: 1.3, expr: 'neutral', look: [-2, 1] },
    ...A.shake(at("isn't", 1)),
    { t: at('all') + 0.05, arms: 'hips', expr: 'smug', look: [-3, 2], ease: 'hold' },
  ];
  const mo = [
    { t: t0, x: 92, y: GY, size: 0.62, lookAt: [280, 420], expr: 'happy' },
    ...A.take(at("isn't", 1) + 0.1, { hold: 0.5, mouth: 'wavy', browY: -6 }),
  ];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.04 }, { t: 1.8, z: 1 }],
    draw(lt, t) { ground(GY); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}

// 3. "It's every colour mixed together, travelling in waves."  The Sun flings out three waves.
{
  const t0 = at("It's", 1), tw = at('mixed') - 0.2;
  const sun = [{ t: t0, x: 135, y: 330, size: 0.95, expr: 'happy' }, ...A.cheer(at('every', 1) - 0.3, 330, { height: 20 })];
  cue(tw, 'zip');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.05, x: 300, y: 500 }],
    draw(lt, t) {
      const L = Math.max(0, (t - tw) * 430), wob = t > at('travelling') ? 16 : 10;
      [[RED, -30, 'smile'], [YEL, 0, 'happy'], [BLUE, 30, 'o']].forEach(([col, off, face], i) => {
        const x0 = 175 + off * 0.7, y0 = 290 - off * 0.7, ux = 0.62, uy = 0.78;
        lightWave(x0, y0, x0 + ux * Math.min(L, 640), y0 + uy * Math.min(L, 640), col, 62, wob, -t * 9 + i, 400 + i * 10, face);
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
    cam: [{ t: 0, z: 1.02 }, { t: 4, z: 1 }],
    draw(lt, t) {
      const hr = Math.min(470, -40 + (t - t0) * 420);
      lightWave(-60, 300, hr, 300, RED, 240, 48, -t * 2.2, 420, 'sleepy');
      if (t > at('long')) arrow([40, 400], [280, 400], 430, RED, 0.12);
      if (t > tb) {
        const hb = Math.min(470, -40 + (t - tb) * 620);
        lightWave(-60, 640, hb, 640, BLUE, 44, 20, -t * 16, 440, 'o');
        if (t > at('short')) arrow([60, 715], [106, 715], 450, BLUE, 0.2);
      }
    },
  });
}

// 5. "When sunlight hits the air, tiny gas molecules bounce the short blue waves around far more than the red ones."
{
  const t0 = at('When'), hit = at('bounce');
  const home = [[300, 470], [120, 300], [430, 250], [150, 650]];
  const mols = MOLS.map((c, i) => [
    { t: t0, x: home[i][0], y: home[i][1], expr: 'neutral', look: [-3, 0], breathe: 2 },
    { t: at('tiny'), expr: 'happy', ease: 'hold' },
  ]);
  mols[0].push(...A.take(hit - 0.3, { hold: 0.2 }), ...A.cheer(hit + 0.15, home[0][1], { height: 16 }));
  mols[2].push(...A.cheer(at('around', 1) - 0.25, home[2][1], { height: 14 }));
  mols[3].push(...A.cheer(at('far') - 0.25, home[3][1], { height: 14 }));
  mols[1].push(...A.shrug(at('red', 2) - 0.1, { hold: 0.6 }));
  cue(at('hits'), 'zip'); cue(hit + 0.1, 'pop'); cue(at('around', 1), 'pop', 0.8); cue(at('far'), 'pop', 0.8); cue(hit + 0.1, 'sparkle', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.12, x: 280, y: 470 }, { t: 2.4, z: 1, x: 270, y: 480 }],
    draw(lt, t) {
      const th = at('hits');
      // blue wave runs into molecule 0 and stops there
      if (t > th) {
        const hb = Math.min(home[0][0] - 24, -40 + (t - th) * 140);
        if (t < hit + 0.25) lightWave(-60, 490, hb, 490, BLUE, 44, 18, -t * 16, 460, 'o');
      }
      scatter(t, hit + 0.1, home[0][0], home[0][1] - 40, 470, 6);
      scatter(t, at('around', 1), home[2][0], home[2][1] - 40, 480, 5);
      scatter(t, at('far'), home[3][0], home[3][1] - 40, 490, 5);
      MOLS.forEach((c, i) => {
        const P = poseAt(mols[i], t);
        P.y += Math.sin(t * 3 + i * 2) * 6;
        drawChar(c, P);
      });
      // the red wave just sails through
      const tr = at('red', 2) - 0.6;
      if (t > tr) lightWave(-60, 380, Math.min(600, -40 + (t - tr) * 520), 380, RED, 240, 40, -t * 2.2, 500, 'sleepy');
    },
  });
}

// 6. "So blue light gets scattered across the whole sky, and reaches your eyes from every direction."
{
  const t0 = at('So blue');
  const mo = [
    { t: t0, x: 270, y: GY, size: 1, look: [0, -4], expr: 'curious' },
    ...A.take(at('eyes') - 0.1, { hold: 0.35, eyes: 'wide', mouth: 'o' }),
    { t: at('every', 2), look: [-4, -1], eyes: 'wide', ease: 'hold' },
    { t: at('direction'), look: [4, -1], ease: 'hold' },
    { t: at('direction') + 0.4, look: [0, -4], ease: 'hold' },
  ];
  const face = [282, GY - 0.68 * 240];
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5, z: 1.1, y: 520 }],
    draw(lt, t) {
      skyScene(t);
      scatter(t, t0 + 0.2, 150, 200, 510, 5, 260);
      scatter(t, t0 + 0.6, 400, 150, 520, 5, 260);
      // bits converge on Mo's eyes from all round
      for (let i = 0; i < 12; i++) {
        const ts = t0 + 0.9 + i * 0.32, u = (t - ts) / 0.9;
        if (u <= 0 || u >= 1) continue;
        const a = -Math.PI + rnd(530, i) * Math.PI * 1.1 - 0.05, r = lerp(560, 30, EASE.in(u));
        bit(face[0], face[1], a, r + 46, 540 + i);
      }
      drawChar(MO, poseAt(mo, t));
    },
  });
}

// 7. "That's why, wherever you look, the sky is blue."  The big jump.
{
  const t0 = at("That's");
  const mo = [
    { t: t0, x: 150, y: GY, size: 1, expr: 'happy', look: [3, -2] },
    ...A.jump(t0 + 0.05, [150, GY], [380, GY], { height: 170, upExpr: 'happy' }),
  ];
  const sun = [{ t: t0, x: 455, y: 205, size: 0.55, expr: 'happy', arms: 'up' }];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, x: 270 }, { t: 2, z: 1, x: 285 }],
    draw(lt, t) { skyScene(t); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}

// 8. "At sunset, the light travels through so much air that most of the blue is bounced away before it reaches you."
{
  const t0 = at('At sunset'), HZ = 640, tb = at('bounced');
  const sun = [{ t: t0, x: 440, y: 700, size: 1.0, expr: 'sleepy', arms: 'down', look: [-4, 1] }];
  const mo = [
    { t: t0, x: 105, y: 880, size: 0.8, facing: 1, look: [4, -1], expr: 'curious' },
    { t: at('reaches you'), expr: 'happy', ease: 'hold' },
  ];
  const motes = Array.from({ length: 16 }, (_, i) => [130 + rnd(600, i) * 300, 600 + rnd(601, i) * 160]);
  cue(tb, 'slide_up', 0.7); cue(tb + 0.1, 'pop', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1.1, x: 300, y: 640 }, { t: 6, z: 1, x: 270, y: 560 }],
    draw(lt, t) {
      band(YEL, 0, HZ, 320);
      band(RED, 0, 300, 321);
      drawChar(SUN, poseAt(sun, t));
      ground(HZ, 330, { fill: PAPER, grass: false });
      motes.forEach(([x, y], i) => fillOnly(blobPts(x, y, 4, 4, 610 + i, 6), INK, 610 + i));
      const L = Math.max(0, (t - at('light travels')) * 120);
      [[RED, -12, 'happy'], [YEL, 4, 'smile'], [BLUE, 20, 'o']].forEach(([col, off, f], i) => {
        const lim = col === BLUE ? Math.min(L, t > tb ? 0 : 230) : L;
        if (lim <= 0) return;
        const x0 = 400, y0 = 640 + off, dx = -0.94, dy = 0.34;
        lightWave(x0, y0, x0 + dx * Math.min(lim, 300), y0 + dy * Math.min(lim, 300), col, 58, 9, -t * 8 + i, 620 + i * 10, f);
      });
      for (let k = 0; k < 4; k++) scatter(t, tb + k * 0.12, 360 - k * 50, 660 + k * 18, 650 + k * 10, 3, 280);
      drawChar(MO, poseAt(mo, t));
    },
  });
}

// 9. "Only the reds and yellows make it through."  Close on Mo's face as the warm light arrives.
{
  const t0 = at('Only');
  const mo = [
    { t: t0, x: 290, y: 830, size: 1, look: [4, -1], expr: 'curious' },
    { t: at('make'), expr: 'love', ease: 'hold' },
  ];
  cue(at('through', 2), 'sparkle');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.45, x: 300, y: 640 }, { t: 2.2, z: 1.6, x: 300, y: 630 }],
    draw(lt, t) {
      band(YEL, 0, 760, 340);
      ground(830, 341, { grass: false });
      const L = Math.max(0, (t - t0 - 0.1) * 260);
      [[RED, -14, 'happy'], [YEL, 14, 'smile']].forEach(([col, off, f], i) => {
        const x0 = 580, y0 = 520 + off, x1 = x0 - Math.min(L, 220), y1 = y0 + Math.min(L, 220) * 0.42;
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
    { t: t0, x: 270, y: GY, size: 1, look: [0, -4], expr: 'curious' },
    ...A.shake(at('painted') - 0.15, 2),
    ...A.cheer(at('bouncing') - 0.3, GY, { height: 26 }),
    { t: at('just') - 0.1, look: [0, 1], expr: 'happy', ease: 'hold' },
    ...A.wave(at('just'), VO_END(), 'R'),
  ];
  const sun = [{ t: t0, x: 455, y: 205, size: 0.55, expr: 'happy', arms: 'out' }];
  const mols = [[110, 250], [300, 140], [230, 330]].map(([x, y], i) => ({ x, y, keys: [{ t: t0, x, y, size: 0.6, expr: 'happy', breathe: 2 }] }));
  for (let k = 0; k < 6; k++) cue(at("It's", 2) + k * 0.45, 'pop', 0.45);
  shot(t0, {
    tr: 'iris', iris: [282, 640],
    cam: [{ t: 0, z: 1, y: 480 }, { t: 5.5, z: 1.12, y: 560 }],
    draw(lt, t) {
      skyScene(t);
      drawChar(SUN, poseAt(sun, t));
      for (let k = 0; k < 6; k++) {
        const m = mols[k % 3];
        scatter(t, at("It's", 2) + k * 0.45, m.x, m.y, 800 + k * 10, 4, 220);
      }
      mols.forEach((m, i) => { const P = poseAt(m.keys, t); P.y += Math.sin(t * 3 + i) * 5; drawChar(MOLS[i], P); });
      drawChar(MO, poseAt(mo, t));
    },
  });
}
