// How many mosquitoes would it take to drain all your blood? Nine shots, timed with at('word').
// Pose keys are in voiceover seconds; camera keys are in seconds into the shot.

// 1. "A mosquito lands on your arm. How many would it take to drain all your blood?"  Mozzie zips in and lands.
{
  const tl = at('lands') - 0.05;
  const kit = [
    { t: 0, x: 170, y: GY, expr: 'curious', aL: -0.35, aR: 1.25, bend: 0.1, reach: 1 },
    { t: tl + 0.1, eyes: 'wide', mouth: 'o', browY: -8, ease: 'hold' },
    { t: at('How') - 0.1, expr: 'thinking', fx: 'think', ease: 'hold' },
    { t: at('drain') - 0.1, expr: 'scared', ease: 'hold' },
  ];
  const moz = [
    { t: 0, size: 1.15, facing: -1, expr: 'happy' },
    { t: at('drain') - 0.1, expr: 'smug', ease: 'hold' },
  ];
  cue(0.05, 'zip'); cue(tl, 'plop');
  shot(0, {
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4, z: 1.12, x: 250, y: 600 }],
    draw(lt, t) {
      park(t);
      const K = poseAt(kit, t), M = poseAt(moz, t);
      // eyes follow Mozzie until the question starts
      const u = clamp(t / tl, 0, 1), from = [600, 140];
      let mx, my;
      const an = drawChar(KIT, Object.assign(K, t < at('How') ? { lookAt: [lerp(from[0], 290, u), lerp(from[1], 690, u)] } : {}));
      const hd = an.hands[1];
      if (t < tl) { const e = EASE.out(u); mx = lerp(from[0], hd[0] + 20, e); my = lerp(from[1], hd[1] - 6, e) - Math.sin(e * Math.PI * 3) * 40; M.smear = u < 0.6 ? { dir: [-0.7, 0.7], k: 1.5 } : null; }
      else { mx = hd[0] + 20; my = hd[1] - 6; }
      M.x = mx; M.y = my;
      drawMoz(MOZ, M, t, { noseAng: t > tl ? 1.25 : 0.6 });
    },
  });
}

// 2. "A big swarm sounds like it could do it."  A cloud of mosquitoes fills the sky; Kit does a take.
{
  const t0 = at('A big swarm');
  const kit = [
    { t: t0, x: 270, y: GY, size: 1.05, expr: 'curious', look: [0, -4] },
    ...A.take(at('swarm') + 0.05, { hold: 0.4, mouth: 'wavy', browY: -8 }),
    { t: at('sounds'), expr: 'scared', look: [0, -4], arms: 'hug', ease: 'hold' },
  ];
  cue(at('swarm'), 'drum', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.08, y: 470 }, { t: 1.8, z: 1, y: 480 }],
    draw(lt, t) {
      band(BLUE, 0, 470, 330);
      ground(GY);
      for (let i = 0; i < 16; i++) {
        const ax = 70 + rnd(340, i) * 400, ay = 110 + rnd(341, i) * 300;
        const k = clamp((t - t0 - i * 0.05) / 0.5, 0, 1), sx = lerp(ax + 380, ax, EASE.out(k)), sy = lerp(ay - 120, ay, EASE.out(k));
        mini(sx + Math.sin(t * 6 + i) * 8, sy + Math.cos(t * 7 + i * 2) * 6, 0.9 + rnd(342, i) * 0.4, 350 + i * 7, t, i % 3 ? -1 : 1, i % 2 ? 'smile' : 'happy');
      }
      drawChar(KIT, poseAt(kit, t));
    },
  });
}

// 3. "But each bite is tiny."  Close on Mozzie sipping from an arm: the sip is a speck.
{
  const t0 = at('But'), tt = at('tiny', 1) - 0.1;
  const moz = [
    { t: t0, x: 260, y: 640, size: 2.5, facing: 1, expr: 'happy' },
    ...A.take(t0 + 0.05, { hold: 0.3, mouth: 'smile' }),
    { t: tt, expr: 'smug', look: [3, -2], ease: 'hold' },
  ];
  cue(tt + 0.1, 'pop'); cue(tt + 0.1, 'sparkle', 0.6);
  shot(t0, {
    tr: 'cut',
    cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 1.4, z: 1.1, x: 300, y: 520 }],
    draw(lt, t) {
      band(RED, 0, 300, 360);
      tube([[-60, 700], [200, 690], [420, 694], [620, 680]], 110, BLUE, 361);
      const tip = drawMoz(MOZ, poseAt(moz, t), t, { noseAng: 1.15 });
      if (t > tt) {
        const k = clamp((t - tt) / (3 * D), 0, 1);
        drop(400, 470, 7 * k + 0.1, 362, RED);
        if (t < tt + 4 * D) burst(400, 466, 18, 34, 363, 0);
        arrow([480, 360], [416, 448], 364, INK, 0.2);
      }
    },
  });
}

// 4. "Only females bite, and each sips a drop smaller than a grain of rice."  Bow, hearts, then drop vs rice.
{
  const t0 = at('Only'), td = at('drop', 1), tr = at('grain');
  const moz = [
    { t: t0, x: 175, y: 600, size: 1.9, facing: 1, expr: 'neutral', look: [2, 0] },
    { t: at('females') - 0.1, expr: 'love', ease: 'hold' },
    ...A.cheer(at('females'), 600, { height: 30 }),
    { t: at('and', 1), expr: 'happy', fx: null, ease: 'hold' },
    { t: td - 0.1, lookAt: [360, 470], expr: 'curious', ease: 'hold' },
    { t: at('smaller') - 0.1, expr: 'smug', lookAt: [360, 470], ease: 'hold' },
  ];
  cue(td, 'plop'); cue(tr, 'pop'); cue(at('smaller'), 'tick');
  shot(t0, {
    tr: 'smear',
    cap: 'top',
    cam: [{ t: 0, z: 1, y: 480 }, { t: td - t0, z: 1 }, { t: td - t0 + 1.2, z: 1.1, x: 300, y: 500 }],
    draw(lt, t) {
      band(BLUE, 0, 250, 370);
      ground(760, 371, { grass: false });
      drawMoz(MOZ, poseAt(moz, t), t, { noseAng: 0.7 });
      if (t > td) { const k = clamp((t - td) / (3 * D), 0, 1); drop(340, 480 - (1 - k) * 30, 12, 372, RED); }
      if (t > tr) { const k = clamp((t - tr) / (3 * D), 0, 1); rice(430, 476, 0.5 + 0.8 * EASE.back(k), 373); }
      if (t > at('smaller')) {
        line([[320, 525], [480, 525]], 3, 374);
        line([[320, 512], [320, 528]], 3, 375); line([[480, 517], [480, 533]], 3, 376);
        plus(345, 445, 7, 377);
      }
    },
  });
}

// 5. "Your body holds about five litres of blood, roughly a big jug."  Kit checks themself; the Jug lands.
{
  const t0 = at('Your body'), tj = at('jug', 1) - 0.25;
  const kit = [
    { t: t0, x: 135, y: GY, size: 1.15, expr: 'curious', look: [0, 4] },
    { t: at('body') - 0.1, arms: 'hug', look: [1, 4], ease: 'hold' },
    { t: at('five') - 0.1, arms: 'shrug', expr: 'thinking', ease: 'hold' },
    { t: at('blood', 2) - 0.1, arms: 'down', expr: 'neutral', lookAt: [400, 600], ease: 'hold' },
    ...A.take(tj + 4 * D, { hold: 0.4, eyes: 'wide', mouth: 'o', browY: -10 }),
  ];
  cue(tj, 'whoosh'); cue(tj + 3 * D, 'thud');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.06, x: 230, y: 560 }, { t: tj - t0, z: 1.02, x: 250, y: 540 }, { t: tj - t0 + 3 * D, shake: 6 }, { t: tj - t0 + 6 * D, z: 1, x: 270, y: 500, shake: 0 }],
    draw(lt, t) {
      park(t);
      if (t > tj) {
        const k = clamp((t - tj) / (3 * D), 0, 1), y = lerp(-100, GY, EASE.in(k));
        if (k < 1) speedLines(375, y - 220, [0, 1], 90, 40, 380);
        jug(375, y, 1.05, 1, 381, t > tj + 0.5 ? 'happy' : 'o');
      }
      drawChar(KIT, poseAt(kit, t));
    },
  });
}

// 6. "Fill that jug one tiny drop at a time, and you'd need about a million mosquitoes."  The queue never ends.
{
  const t0 = at('Fill'), tm = at('million', 1) - 0.2;
  const q = k => [300 - k * 62, 420 - k * 34 + Math.sin(k * 1.3) * 26];
  const ndrops = 7;
  for (let i = 0; i < ndrops; i++) cue(t0 + 0.6 + i * 0.55 + 0.35, 'plop', 0.5);
  cue(tm, 'slide_up', 0.7);
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1, x: 300, y: 500 }, { t: tm - t0, z: 1, x: 290, y: 500 }, { t: tm - t0 + 1, z: 0.45, x: -20, y: 300, ease: 'io' }],
    draw(lt, t) {
      ground(760, 391, { grass: false });
      const fill = clamp((t - t0 - 0.9) * 0.0018, 0, 0.012);
      jug(390, 760, 1.0, fill, 392, t > tm ? 'o' : 'smile', t > tm ? [-3, -2] : [-2, -2]);
      // the queue shuffles forward every 0.55 s
      const ph = clamp(t - t0 - 0.6, 0, 99) / 0.55, step = ph - Math.floor(ph), base = Math.min(ndrops, Math.floor(ph));
      for (let k = 0; k < 60; k++) {
        const kk = k + (ph < ndrops ? EASE.io(clamp(1 - step * 2, 0, 1)) : 0);
        const [x, y] = q(kk);
        mini(x, y + Math.sin(t * 5 + k) * 4, 1.1, 400 + k * 5, t, 1, k === 0 ? 'happy' : 'smile');
      }
      // the front mosquito lets a drop fall into the jug
      if (ph < ndrops && step > 0.2) {
        const u = clamp((step - 0.2) / 0.6, 0, 1);
        if (u < 1) drop(330, lerp(440, 740, EASE.in(u)), 6, 700 + base, RED);
      }
    },
  });
}

// 7. "Real danger comes sooner: after around four hundred thousand bites, you'd lose enough blood to be in serious trouble."
{
  const t0 = at('Real'), tdn = at('danger') - 0.1, ta = at('after'), tb = end('bites', 1);
  const JX = 240, JY = 790, JS = 1.0;
  const lvl = t => lerp(1, 0.6, clamp((t - ta) / (tb - ta), 0, 1));
  const kit = [
    { t: t0, x: 455, y: GY, size: 0.8, expr: 'curious', lookAt: [JX, 600] },
    { t: tdn, expr: 'surprised', ease: 'hold' },
    { t: ta, expr: 'sad', lookAt: [JX, 600], ease: 'hold' },
    ...A.take(at('serious') - 0.15, { hold: 0.5, mouth: 'wavy', arms: 'hug' }),
    { t: at('trouble'), expr: 'scared', arms: 'hug', ease: 'hold' },
  ];
  cue(tdn, 'zip'); cue(ta, 'slide_down', 0.7);
  shot(t0, {
    tr: 'smear',
    cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 6.5, z: 1.08, x: 260, y: 540 }],
    draw(lt, t) {
      band(RED, 0, 260, 400);
      ground(GY, 401, { grass: false });
      if (t > tdn) hazard(70, 360, 0.75, 402);
      const L = lvl(t), face = t < tdn ? 'smile' : t < ta ? 'o' : 'frown';
      const J = jug(JX, JY, JS, L, 403, face, t > ta ? [2, -3] : [0, 0]);
      // the danger line, 40% down
      if (t > tdn) {
        const ly = lerp(JY - 8 * JS, J.top[1] + J.h * 0.16, 0.6);
        for (let i = 0; i < 5; i++) line([[JX - J.w + 8 + i * 46, ly], [JX - J.w + 30 + i * 46, ly]], 4, 404 + i);
      }
      if (t > ta + 1) for (let i = 0; i < 2; i++) drop(JX + 80 + i * 38, J.top[1] - 20 + ((t * 3 + i * 0.5) % 1) * 30, 7, 410 + i, BLUE);
      // a swarm sipping at the jug
      if (t > ta - 0.4) for (let i = 0; i < 7; i++) {
        const a = i / 7 * TAU + t * 1.1, r = 120 + 25 * Math.sin(t * 2 + i);
        mini(JX + Math.cos(a) * r, J.top[1] - 20 + Math.sin(a) * 40, 0.95, 420 + i * 6, t, Math.cos(a) > 0 ? -1 : 1, 'happy');
      }
      drawChar(KIT, poseAt(kit, t));
    },
  });
}

// 8. "Luckily, you'd swat, scratch and run long before that."  Swat, scratch, dash off.
{
  const t0 = at('Luckily'), ts = at('swat'), tc = at('scratch'), tr = at('run');
  const kit = [
    { t: t0, x: 180, y: GY, size: 1.15, expr: 'smug', look: [3, -3] },
    // swat: wind up, smear down
    { t: ts - 4 * D, aR: 2.2, bend: 0.4, reach: 0.9, sy: 0.92, sx: 1.06, expr: 'determined', ease: 'lin' },
    { t: ts - 2 * D, aR: 2.95, lean: -0.08, ease: 'lin' },
    { t: ts, aR: 1.2, lean: 0.12, smear: { dir: [0.5, 0.85], k: 1.7 }, sy: 1.05, sx: 0.96, ease: 'hold' },
    { t: ts + D, aR: 0.9, smear: null, lean: 0.04, eyes: 'squeeze', mouth: 'grit', ease: 'hold' },
    { t: ts + 2 * D, aR: 1.0, lean: 0, ease: 'hold' },
    // scratch: rub the left arm, fast
    { t: tc - D, aR: 0.35, expr: 'angry', ease: 'hold' },
  ];
  for (let i = 0; i < 6; i++) kit.push({ t: tc + i * D, aR: i % 2 ? -0.3 : 0.1, bend: -1.4, reach: 0.7, aL: -0.4, lean: (i % 2 ? 0.03 : -0.03), ease: 'hold' });
  kit.push(...A.dash(tr - 0.05, 180, 640, GY, { endExpr: 'happy' }));
  const moz = [
    { t: t0, x: 300, y: 560, size: 0.9, facing: -1, expr: 'happy' },
    { t: ts - 0.1, x: 300, y: 560, ease: 'hold' },
    { t: ts + 2 * D, x: 380, y: 420, expr: 'shocked', smear: { dir: [0.5, -0.85], k: 1.6 }, ease: 'hold' },
    { t: ts + 3 * D, x: 400, y: 400, smear: null, ease: 'hold' },
    { t: tr + 0.6, expr: 'sad', lookAt: [600, 700], ease: 'hold' },
  ];
  cue(ts, 'whoosh'); cue(ts + D, 'pop'); for (let i = 0; i < 3; i++) cue(tc + i * 2 * D, 'tick', 0.6);
  shot(t0, {
    tr: 'smear',
    cap: 'top',
    cam: [{ t: 0, z: 1.05, x: 260, y: 540 }, { t: 1.5, z: 1.05, x: 260, y: 540, shake: 0 }, { t: ts - t0 + D, shake: 5 }, { t: ts - t0 + 4 * D, shake: 0 }],
    draw(lt, t) {
      park(t);
      if (t > ts && t < ts + 3 * D) burst(300, 600, 24, 54, 430, 0);
      drawChar(KIT, poseAt(kit, t));
      drawMoz(MOZ, poseAt(moz, t), t);
      if (t > tc && t < tr) for (let i = 0; i < 3; i++) line([[110 + i * 10, 690 - i * 14], [128 + i * 10, 684 - i * 14]], 3, 440 + i);
    },
  });
}

// 9. "So next time one bites you, relax. It's just one sip out of a million."  Calm Kit waves; one tiny sip; iris on Kit.
{
  const t0 = at('So'), tl = at('one', 2) - 0.1;
  const kit = [
    { t: t0, x: 165, y: GY, size: 1.25, expr: 'curious', aL: -0.35, aR: 1.25, bend: 0.1, reach: 1 },
    { t: tl + 0.3, lookAt: [300, 700], eyes: 'wide', mouth: 'o', ease: 'hold' },
    ...A.sigh(at('relax')),
    { t: at('relax') + 0.4, eyes: 'happy', mouth: 'smile', brow: -0.3, browY: -2, look: [2, 2], ease: 'hold' },
    // payoff: a wave with the free hand, landed before the last word and looping through the breath
    ...A.wave(at('just'), VO_END(), 'L'),
  ];
  const moz = [
    { t: t0, size: 1.1, facing: -1, expr: 'happy' },
    { t: at('sip') - 0.1, eyes: 'happy', mouth: 'o', ease: 'hold' },
    { t: at('million', 2) - 0.1, expr: 'love', ease: 'hold' },
  ];
  cue(tl + 0.2, 'plop'); cue(at('sip'), 'sparkle');
  shot(t0, {
    tr: 'iris', iris: [175, 690],   // close on Kit's face
    cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4.5, z: 1.14, x: 280, y: 600 }],
    draw(lt, t) {
      park(t);
      jug(445, GY, 0.68, 1, 450, t > at('million', 2) ? 'happy' : 'smile', [-2, 0]);
      const an = drawChar(KIT, poseAt(kit, t)), hd = an.hands[1];
      const M = poseAt(moz, t), u = clamp((t - (tl - 0.6)) / 0.6, 0, 1), e = EASE.out(u);
      M.x = lerp(560, hd[0] + 20, e); M.y = lerp(300, hd[1] - 6, e) - Math.sin(e * Math.PI * 2) * 30;
      drawMoz(MOZ, M, t, { noseAng: u >= 1 ? 1.25 : 0.6 });
      if (t > at('sip')) { const k = clamp((t - at('sip')) / 0.3, 0, 1); plus(hd[0] + 200, hd[1] - 80 - k * 10, 8, 460); }
    },
  });
}
