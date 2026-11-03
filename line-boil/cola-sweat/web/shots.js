// What if your sweat was made of Coca-Cola? Nine shots, timed with at('word').

// 1. "Imagine a hot day, a hard run, and instead of sweat, you start leaking Coca-Cola."
{
  const tc = at('Coca-Cola');
  const jo = [
    ...jog(0, at('instead'), 220, GY),
    { t: at('instead') + D, expr: 'curious', look: [-3, 2], ease: 'hold' },
    ...A.take(at('leaking') - 0.1, { hold: 0.6, mouth: 'wavy', browY: -8 }),
    { t: tc + 0.5, expr: 'shocked', look: [-3, 1], ease: 'hold' },
  ];
  const sun = [{ t: 0, x: 440, y: 370, expr: 'smug', look: [-3, 2] }];
  cue(tc, 'plop'); cue(tc + 0.3, 'plop', 0.7);
  shot(0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 4.5, z: 1.1, x: 240, y: 560 }],
    draw(lt, t) {
      drawChar(SUN, poseAt(sun, t));
      [390, 430, 470].forEach((x, i) => wisp(x, 480, 40, 1200 + i, t, RED, 2.4));
      hills(GY - 70);
      ground(GY);
      // passing scenery while running
      if (t < at('instead')) [0, 1, 2].forEach(i => rock(((600 - (t * 260 + i * 210)) % 660 + 660) % 660 - 60, GY + 2, 0.6, 1210 + i));
      else [0, 1, 2].forEach(i => rock(((600 - (at('instead') * 260 + i * 210)) % 660 + 660) % 660 - 60, GY + 2, 0.6, 1210 + i));
      drawChar(JO, poseAt(jo, t));
      spray(t, tc, 225, 680, 1250, 18);
    },
  });
}

// 2. "Sweat is almost pure water, and it cools you by evaporating off your skin."  Close on the skin.
{
  const t0 = at('Sweat is', 1), te = at('evaporating');
  cue(at('water', 1), 'plop'); cue(te, 'slide_up', 0.6);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1.06 }, { t: 4, z: 1 }],
    draw(lt, t) {
      ground(600, 1300, { fill: YEL, grass: false });
      [[90, 700], [180, 820], [420, 690], [470, 860], [300, 900]].forEach(([x, y], i) => line([[x - 7, y], [x, y + 4], [x + 7, y]], 2.4, 1310 + i));
      const u = clamp((t - te) / 1.1, 0, 1);
      const r = lerp(38, 0, EASE.in(u)), y = lerp(590, 470, EASE.io(u));
      if (r > 2) sweatDrop(250, y - 4, r, 1320, t > at('cools') ? 'happy' : 'smile');
      if (t > te) for (let i = 0; i < 4; i++) wisp(200 + i * 34, 520 - u * 120 - i * 6, 70, 1330 + i, t, BLUE, 3);
      thermo(450, 470, t > te ? lerp(0.8, 0.35, clamp((t - te) / 0.8, 0, 1)) : 0.8, 1340);
    },
  });
}

// 3. "But cola is about one tenth sugar, and sugar doesn't evaporate."
{
  const t0 = at('But'), ts = at('tenth'), tn = at("doesn't");
  const cube = [
    { t: t0, x: 270, y: 600, size: 1, expr: 'happy', hide: true },
    { t: ts + 0.1, hide: false, ease: 'hold' },
    ...A.cheer(ts + 0.1, 600, { height: 14 }),
    ...A.shake(tn - 0.05, 3),
    { t: tn + 0.6, arms: 'hips', expr: 'smug', ease: 'hold' },
  ];
  cue(at('cola'), 'pop'); cue(ts + 0.1, 'pop'); cue(tn + 0.1, 'slide_up', 0.6);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1 }, { t: 3.5, z: 1.08, y: 500 }],
    draw(lt, t) {
      ground(600, 1300, { fill: YEL, grass: false });
      if (t < ts + 0.1) {
        const pop = clamp((t - at('cola')) / (3 * D), 0, 1);
        if (t >= at('cola')) colaDrop(270, 600 - 52 * EASE.back(pop), 52 * EASE.back(pop), 1400, 'smile');
      } else {
        // the drop splits: nine blue water drops and one sugar cube
        const u = clamp((t - tn) / 1.2, 0, 1);
        for (let i = 0; i < 9; i++) {
          const a = Math.PI + (i / 8) * Math.PI, rr = 120;
          const x = 270 + Math.cos(a) * rr, y0 = 560 + Math.sin(a) * rr * 0.75;
          const y = y0 - EASE.in(u) * 420, r = 16 * (1 - u * 0.8);
          sweatDrop(x, y, r, 1410 + i * 5, u > 0 ? 'happy' : 'smile');
          if (u > 0 && u < 1) wisp(x, y + 30, 40, 1460 + i, t, BLUE, 2);
        }
        if (t < ts + 0.1 + 2 * D) burst(270, 520, 40, 70, 1470, 0);
        drawChar(CUBE, poseAt(cube, t));
      }
    },
  });
}

// 4. "So the water dries up, and the sugar stays behind, as a sticky, brown glaze."
{
  const t0 = at('So the water'), tg = at('stays'), tk = at('sticky');
  const jo = [
    { t: t0, x: 260, y: GY, size: 0.85, expr: 'curious', look: [3, 3] },
    { t: tg, look: [-3, 2], ease: 'hold' },
    { t: tk - 4 * D, aR: 0.35, bend: -0.5, reach: 0.72 },
    { t: tk, aR: 1.5, bend: 0.4, reach: 0.95, expr: 'scared', look: [4, 1], ease: 'out' },
    { t: at('glaze', 1), mouth: 'wavy', brow: -0.8, ease: 'hold' },
  ];
  cue(tg, 'plop', 0.7); cue(tk, 'squeak', 0.7); cue(at('glaze', 1), 'sparkle', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.05, y: 560 }, { t: 4.3, z: 1.18, y: 610 }],
    draw(lt, t) {
      ground(GY);
      const P = poseAt(jo, t);
      // water wisps leaving him
      if (t < tg + 0.5) [-50, -10, 40].forEach((dx, i) => wisp(P.x + dx, 620 - lt * 30, 50, 1500 + i, t, BLUE, 2.4));
      const A0 = drawChar(JO, P);
      patch(JO, P, GLAZE, clamp((t - tg) / 1.0, 0, 1), 1510);
      if (t > tk && A0) {
        // a string of goo from the patch to the hand
        const p = tp(JO, P, 0.66 * JO.w, -0.36 * JO.h), h = A0.hands[1];
        line([p, [(p[0] + h[0]) / 2, Math.max(p[1], h[1]) + 22], h], 3.4, 1530, INK, 0.8);
      }
      if (t > at('glaze', 1)) {
        const alt = DRAWING % 4 < 2;
        plus(P.x - 60, 600 + (alt ? 0 : 10), alt ? 6 : 4, 1540);
        plus(P.x + 70, 640 - (alt ? 8 : 0), alt ? 4 : 6, 1542);
      }
    },
  });
}

// 5. "Your shirt stains, your arms stick to your sides, and the glaze can slow your cooling."
{
  const t0 = at('Your shirt'), ta = at('arms'), tc = at('slow');
  const jo = [
    { t: t0, x: 230, y: GY, size: 0.9, expr: 'curious', look: [0, 4] },
    { t: at('stains'), expr: 'shocked', ease: 'hold' },
    { t: ta, aL: -0.06, aR: 0.06, bend: 0, reach: 0.72, expr: 'determined', ease: 'hold' },
  ];
  for (let i = 0; i < 12; i++) jo.push({ t: ta + 0.2 + i * 2 * D, lean: i % 2 ? 0.06 : -0.06, sy: i % 2 ? 1.03 : 0.97, ease: 'hold' });
  jo.push({ t: tc, lean: 0, sy: 1, expr: 'shocked', fx: 'sweat', ease: 'hold' });
  cue(at('stains'), 'plop'); cue(at('stains') + 0.15, 'plop', 0.6); cue(ta, 'thud', 0.6); cue(tc, 'slide_up', 0.8);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.1, x: 260, y: 600 }, { t: 4.5, z: 1.02, x: 280, y: 560 }],
    draw(lt, t) {
      ground(GY);
      const P = poseAt(jo, t);
      drawChar(JO, P);
      patch(JO, P, GLAZE, 1, 1510);
      patch(JO, P, STAINS, clamp((t - at('stains')) / 0.5, 0, 1), 1600, false);
      if (t > tc) [-30, 0, 30].forEach((dx, i) => wisp(P.x + dx + 10, 580, 50, 1620 + i, t, RED, 3));
      thermo(440, 690, t > tc ? lerp(0.35, 0.92, clamp((t - tc) / 0.7, 0, 1)) : 0.35, 1630);
    },
  });
}

// 6. "Then every wasp and ant nearby smells dessert."
{
  const t0 = at('Then'), tw = at('wasp'), tn = at('ant');
  const jo = [
    { t: t0, x: 290, y: GY, size: 0.85, expr: 'curious', look: [-3, -1] },
    ...A.take(tw + 0.15, { hold: 0.4, mouth: 'wavy' }),
    { t: at('smells'), expr: 'scared', look: [-3, 2], ease: 'hold' },
  ];
  const wasps = [[[600, 180], [400, 500], 1.9, -1], [[-80, 300], [150, 470], 2.1, 1], [[620, 660], [455, 640], 1.7, -1]];
  wasps.forEach((w, i) => cue(tw - 0.1 + i * 0.25, 'whoosh', 0.6));
  cue(tw + 0.5, 'drum', 0.4);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 2.6, z: 1.06, y: 520 }],
    draw(lt, t) {
      ground(GY);
      // ants march in from the left to Jo's feet
      for (let i = 0; i < 6; i++) {
        const x = Math.min(220 - i * 30, -40 - i * 36 + Math.max(0, t - tn + 0.3) * 150);
        ant(x, GY - 1, 1.7, 1700 + i * 20);
      }
      drawChar(JO, poseAt(jo, t));
      patch(JO, poseAt(jo, t), GLAZE, 1, 1510);
      wasps.forEach(([from, to, s, dir], i) => {
        const ts = tw - 0.1 + i * 0.25, u = clamp((t - ts) / 0.5, 0, 1);
        if (u <= 0) return;
        const x = lerp(from[0], to[0], EASE.out(u)), y = lerp(from[1], to[1], EASE.out(u)) + Math.sin(t * 9 + i) * 6;
        if (u < 0.5) speedLines(x - dir * 30, y, [dir, (to[1] - from[1]) / 400], 60, 10, 1750 + i * 10, 3);
        wasp(x, y, s, 1760 + i * 20, dir);
      });
    },
  });
}

// 7. "Skin bacteria would feast on it too, so you'd probably smell worse."
{
  const t0 = at('Skin bacteria'), tf = at('feast'), tw = at("so you'd");
  const jo = [
    { t: t0, x: 270, y: GY, size: 1.05, expr: 'curious', look: [0, 4] },
    { t: tw - 0.1, arms: 'chin', expr: 'dizzy', ease: 'hold' },
  ];
  const spots = [[-0.8, -0.5], [0.85, -0.3], [-0.5, -0.12], [0.42, -0.1]];
  BUGS.forEach((b, i) => cue(at('bacteria') + i * 0.18, 'pop', 0.5));
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1.25, y: 630 }, { t: 3.6, z: 1.08, y: 590 }],
    draw(lt, t) {
      ground(GY);
      const P = poseAt(jo, t);
      drawChar(JO, P);
      patch(JO, P, GLAZE, Math.max(0.35, 1 - Math.max(0, t - tf) * 0.4), 1510);
      BUGS.forEach((c, i) => {
        const tb = at('bacteria') + i * 0.18;
        if (t < tb) return;
        const p = tp(JO, P, spots[i][0] * JO.w, spots[i][1] * JO.h);
        const hop = Math.abs(Math.sin((t + i * 0.3) * 7)) * 10;
        const chomp = t > tf && DRAWING % 2;
        drawChar(c, Object.assign({}, DEFAULT_POSE, { x: p[0], y: p[1] + 14 - hop, eyes: 'happy', mouth: chomp ? 'open' : 'grin', arms: undefined, aL: -2.4, aR: 2.4, bend: 0.3, reach: 0.8, facing: i % 2 ? -1 : 1 }), { t });
      });
      if (t > tw) for (let i = 0; i < 5; i++) wisp(P.x - 90 + i * 45, 640 - (i % 2) * 30, 70, 1800 + i, t, INK, 2.4);
    },
  });
}

// 8. "And a hard workout would sweat out nearly three cans of sugar an hour, draining your energy."
{
  const t0 = at('And a hard'), td = at('draining');
  const jo = [
    ...jog(t0, td, 150, GY),
    { t: td + D, size: 1, ease: 'hold' },
    ...A.sigh(td + 0.15),
    { t: td + 0.8, expr: 'sleepy', sy: 0.9, sx: 1.06, ease: 'hold' },
  ];
  jo.unshift({ t: t0, size: 1 });
  const cans = [[300, 300, at('nearly')], [380, 300, at('three')], [460, 300, at('cans')]];
  cans.forEach(c => cue(c[2], 'pop'));
  [0, 1, 2].forEach(k => cue(td + 0.2 + k * 0.28, 'deflate', 0.5));
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5, z: 1.04 }],
    draw(lt, t) {
      ground(GY);
      cans.forEach(([x, y, tc], i) => can(x, y, EASE.back(clamp((t - tc) / (3 * D), 0, 1)) * 1.15, 1900 + i * 10));
      const lvl = t < td + 0.2 ? 4 : Math.max(1, 4 - Math.floor((t - td - 0.2) / 0.28) - 1);
      battery(400, 620, lvl, 1940);
      drawChar(JO, poseAt(jo, t));
      spray(t, t0 + 0.2, 150, 640, 1960, Math.round((Math.min(t, td) - t0) / 0.12) + 1, 'cola', 0.12);
    },
  });
}

// 9. "So be glad your sweat is boring. Salty water keeps you cool, not candied."
{
  const t0 = at('So be');
  const jo = [
    { t: t0, x: 270, y: GY, size: 1, expr: 'happy' },
    ...A.shrug(at('boring') - 0.1, { hold: 0.5, after: 'smile' }),
    ...A.cheer(at('cool') - 0.3, GY, { height: 30 }),
    ...A.wave(at('candied'), VO_END(), 'R'),
  ];
  const cube = [{ t: t0, x: 70, y: GY, size: 0.8, expr: 'neutral', look: [3, 0] }, ...A.shrug(at('candied'), { hold: 1.0 }), { t: at('candied') + 0.2, expr: 'sad', ease: 'hold' }];
  const sun = [{ t: t0, x: 450, y: 360, expr: 'happy', look: [-3, 2] }];
  cue(at('Salty'), 'sparkle', 0.6);
  shot(t0, {
    tr: 'iris', iris: [280, 672],
    cam: [{ t: 0, z: 1, y: 500 }, { t: 5, z: 1.1, y: 560 }],
    draw(lt, t) {
      band(BLUE, 0, 420, 2001);
      cloud(120 + t * 5, 160, 50, 20, 2002);
      drawChar(SUN, poseAt(sun, t));
      hills(GY - 70);
      ground(GY);
      drawChar(CUBE, poseAt(cube, t));
      const P = poseAt(jo, t);
      drawChar(JO, P);
      // clean blue sweat beads, sliding slowly
      [[-0.62, -0.7], [0.6, -0.8], [0.7, -0.45]].forEach(([fx, fy], i) => {
        const p = tp(JO, P, fx * JO.w, fy * JO.h + ((t * 14 + i * 9) % 26));
        sweatDrop(p[0], p[1], 7, 2010 + i * 5);
      });
      if (t > at('Salty')) { const alt = DRAWING % 4 < 2; plus(P.x - 80, 600 + (alt ? 0 : 8), alt ? 6 : 4, 2030); plus(P.x + 85, 560, alt ? 4 : 6, 2032); }
    },
  });
}
