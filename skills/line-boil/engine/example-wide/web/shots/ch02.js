// CHAPTER 2: "Why the sky is blue" (script lines 4 to 6)

musicMood(at('When'), 'mystery');     // the explanation opens as a puzzle
musicMood(at("That's"), 'upbeat');     // and resolves into the answer

// 5. "When sunlight hits the air, tiny gas molecules bounce the short blue waves around far more than the red ones."
{
  const t0 = at('When'), hit = at('bounce');
  const home = [[560, 260], [250, 170], [760, 150], [330, 350]];
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
    draw(lt, t) {
      band(PAPER, 0, GY, 300); ground(GY);
      const th = at('hits');
      if (t > th && t < hit + 0.25) lightWave(-60, 280, Math.min(home[0][0] - 28, -40 + (t - th) * 260), 280, BLUE, 50, 18, -t * 16, 460, 'o');
      scatter(t, hit + 0.1, home[0][0], home[0][1] - 40, 470, 6);
      scatter(t, at('around', 1), home[2][0], home[2][1] - 40, 480, 5);
      scatter(t, at('far'), home[3][0], home[3][1] - 40, 490, 5);
      MOLS.forEach((c, i) => { const P = poseAt(mols[i], t); P.y += Math.sin(t * 3 + i * 2) * 6; drawChar(c, P); });
      const tr = at('red', 2) - 0.6;
      if (t > tr) lightWave(-60, 400, Math.min(960, -40 + (t - tr) * 700), 400, RED, 300, 36, -t * 2.2, 500, 'sleepy');
    },
  });
}

// 6. "So blue light gets scattered across the whole sky, and reaches your eyes from every direction."
{
  const t0 = at('So blue');
  const mo = [
    { t: t0, x: 480, y: GY, size: 1.15, look: [0, -4], expr: 'curious' },
    ...A.take(at('eyes') - 0.1, { hold: 0.35, eyes: 'wide', mouth: 'o' }),
    { t: at('every', 2), look: [-4, -1], eyes: 'wide', ease: 'hold' },
    { t: at('direction'), look: [4, -1], ease: 'hold' },
    { t: at('direction') + 0.4, look: [0, -4], ease: 'hold' },
  ];
  const face = [492, GY - 0.68 * 184];
  shot(t0, {
    draw(lt, t) {
      skyScene(t);
      scatter(t, t0 + 0.2, 220, 150, 510, 5, 300);
      scatter(t, t0 + 0.6, 740, 120, 520, 5, 300);
      for (let i = 0; i < 12; i++) {
        const ts = t0 + 0.9 + i * 0.32, u = (t - ts) / 0.9;
        if (u <= 0 || u >= 1) continue;
        const a = -Math.PI + rnd(530, i) * Math.PI * 1.1 - 0.05, r = lerp(620, 30, EASE.in(u));
        bit(face[0], face[1], a, r + 46, 540 + i);
      }
      drawChar(MO, poseAt(mo, t));
    },
  });
}

// 7. "That's why, wherever you look, the sky is blue."
{
  const t0 = at("That's");
  const mo = [
    { t: t0, x: 250, y: GY, size: 1.15, expr: 'happy', look: [3, -2] },
    ...A.jump(t0 + 0.05, [250, GY], [640, GY], { height: 150, upExpr: 'happy' }),
  ];
  const sun = [{ t: t0, x: 790, y: 120, size: 0.8, expr: 'happy', arms: 'up' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) { skyScene(t); drawChar(SUN, poseAt(sun, t)); drawChar(MO, poseAt(mo, t)); },
  });
}
