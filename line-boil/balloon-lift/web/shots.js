// How many balloons would it take to lift you into the sky? Nine shots, timed with at('word').
const HOLD = { aR: 2.5, bend: 0.2, reach: 0.9 };

// 1. "How many party balloons would it take to lift you into the sky?"  One balloon, no lift.
{
  const ol = [
    { t: 0, x: 240, y: GY, look: [3, -4], expr: 'curious', ...HOLD },
    { t: at('lift', 1) - 0.2, sy: 1.08, sx: 0.95, lean: 0.06, eyes: 'squint', mouth: 'grit', brow: 0.6 },
    { t: at('lift', 1) + 0.3, sy: 1.1, lean: 0.07 },
    { t: at('sky') - 0.1, sy: 1, sx: 1, lean: 0, expr: 'thinking', look: [3, -4], fx: 'think', ease: 'hold' },
  ];
  cue(0.1, 'squeak', 0.5);
  shot(0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.04, y: 520 }, { t: 3, z: 1.1, y: 540 }],
    draw(lt, t) {
      band(BLUE, 0, 380, 3001);
      clouds(t, 0, 3010, 3);
      hills(GY - 70);
      ground(GY);
      const A0 = drawChar(OLLIE, poseAt(ol, t));
      const tug = t > at('lift', 1) - 0.2 && t < at('sky') ? (DRAWING % 2 ? -6 : 0) : 0;
      balloon(335, 455 + Math.sin(t * 2.5) * 6 + tug, 44, RED, 3020, { face: tug ? 'o' : 'smile', string: A0.hands[1] });
    },
  });
}

// 2. "A balloon floats because helium is lighter than the air it pushes aside."  A cutaway.
{
  const t0 = at('A balloon floats'), tf = at('floats'), tp = at('pushes');
  cue(at('helium'), 'sparkle', 0.7); cue(tp, 'slide_up', 0.7);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1 }, { t: 4, z: 1.06 }],
    draw(lt, t) {
      const rise = Math.min(70, Math.max(0, t - tf) * 22), cx = 270, cy = 460 - rise, R = 115;
      const k = clamp((t - tp) / 0.4, 0, 1);
      airDots(t, 130, 3100, {
        push: (x, y) => {
          const dx = x - cx, dy = (y - cy) / 1.15, d = Math.hypot(dx, dy) || 1, edge = R + 14 + 50 * EASE.back(k);
          if (d < edge) { const s = edge / d; return [cx + dx * s, cy + dy * s * 1.15]; }
          return [x, y];
        },
      });
      balloon(cx, cy, R, RED, 3150, { face: t > at('lighter') ? 'happy' : 'smile' });
      for (let i = 0; i < 6; i++) {
        const a = i / 6 * TAU + t * 0.8, r = 30 + (i % 3) * 20;
        shape(blobPts(cx + Math.cos(a) * r, cy - 20 + Math.sin(a) * r * 0.8, 6, 6, 3160 + i, 6), PAPER, 2, 3160 + i, 0.5);
      }
      if (t > at('helium') && t < at('helium') + 0.6) { plus(cx - 70, cy - 90, 7, 3170); plus(cx + 80, cy - 60, 5, 3172); }
      if (t > tp && t < tp + 0.5) [[-1, 0], [1, 0], [0, 1]].forEach((d, i) => speedLines(cx + d[0] * (R + 90), cy + d[1] * (R * 1.2 + 60), d, 40, 10, 3180 + i * 5, 3));
    },
  });
}

// 3. "But one balloon only lifts about ten grams, about as much as two coins."
{
  const t0 = at('But'), c1 = at('ten'), c2 = at('two coins'), c3 = at('coins') + 0.35;
  const ol = [
    { t: t0, x: 440, y: GY, size: 0.7, lookAt: [270, 400], expr: 'curious' },
    ...A.take(at('only') - 0.05, { hold: 0.5, mouth: 'flat' }),
    { t: c3 + 0.2, expr: 'sad', ease: 'hold' },
  ];
  [c1, c2, c3].forEach(c => cue(c + 2 * D, 'plop')); cue(c3 + 0.1, 'slide_down', 0.8);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.08, y: 470 }, { t: 4, z: 1, y: 480 }],
    draw(lt, t) {
      ground(GY);
      const sink = t < c2 ? 0 : t < c3 ? 30 : 30 + EASE.io(clamp((t - c3) / 0.6, 0, 1)) * 230;
      const by = 250 + sink + Math.sin(t * 2.5) * 5, py = by + 190;
      // plate with coins on strings
      line([[270, by + 56], [272, py - 30]], 2, 3210, INK, 0.6, false);
      line([[272, py - 30], [225, py]], 1.8, 3211, INK, 0.5, false);
      line([[272, py - 30], [319, py]], 1.8, 3212, INK, 0.5, false);
      [c1, c2, c3].forEach((c, i) => {
        if (t < c) return;
        const u = clamp((t - c) / (2 * D), 0, 1);
        coin(272, lerp(py - 140, py - 7 - i * 12, u), 3220 + i * 5);
      });
      shape(blobPts(272, py + 3, 52, 8, 3215, 8, 0.04), PAPER, 3, 3215, 0.8);
      balloon(270, by, 48, YEL, 3230, { face: t > c3 ? 'frown' : t > c1 ? 'o' : 'smile' });
      drawChar(OLLIE, poseAt(ol, t));
    },
  });
}

// 4. "A grown-up weighs around seventy kilograms."  Onto the scale; the needle swings round.
{
  const t0 = at('A grown-up');
  const j = A.jump(t0 + 0.02, [120, GY], [270, GY - 36], { height: 90, drawings: 8, endExpr: 'smug' });
  const ol = [{ t: t0, x: 120, y: GY, size: 1, expr: 'determined' }, ...j];
  cue(j.end - 4 * D + 0.25, 'ding', 0.7);
  shot(t0, {
    cam: [{ t: 0, z: 1.1, y: 620 }, { t: 2.4, z: 1.18, y: 640 }],
    draw(lt, t) {
      ground(GY);
      const u = clamp((t - (j.end - 4 * D)) / 0.35, 0, 1);
      scale(270, GY, lerp(-1.3, 1.5, EASE.back(u)), 3300);
      drawChar(OLLIE, poseAt(ol, t), { shadow: t < j.end - 5 * D });
    },
  });
}

// 5. "So you'd need roughly seven thousand balloons, a bunch bigger than a bus."
{
  const t0 = at("So you'd"), tb = at('bigger'), tl = at('bus') + 0.25, N = 140;
  const born = i => t0 + 0.15 + 2.1 * Math.pow(i / N, 0.5);
  const ol = [
    { t: t0, x: 190, y: GY, size: 1, expr: 'curious', look: [1, -4], ...HOLD },
    { t: at('seven') , expr: 'surprised', look: [1, -4], ease: 'hold' },
    { t: tl, gy: GY, ease: 'hold' },
    { t: tl + 0.1, expr: 'scared', ease: 'hold' },
  ];
  for (let k = 0; k < 6; k++) cue(born(k * 4), 'pop', 0.5);
  cue(born(60), 'drum', 0.5); cue(tb, 'whoosh'); cue(tl, 'slide_up', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.12, y: 560 }, { t: 2.4, z: 0.94, y: 500 }],
    draw(lt, t) {
      ground(GY);
      const lift = Math.max(0, t - tl) * 70;
      const bx = lerp(600, 320, EASE.out(clamp((t - tb) / 0.35, 0, 1)));
      if (t > tb) { if (t < tb + 0.2) speedLines(bx + 230, GY - 50, [-1, 0], 80, 16, 3400, 4); bus(bx, GY, 0.85, 3410); }
      const P = poseAt(ol, t);
      P.y -= lift;
      const A0 = drawChar(OLLIE, P);
      bunch(t, 200, 330 - lift, N, 19, A0.hands[1], 3500, { born });
    },
  });
}

// 6. "And as you rise, the air gets thinner and colder, and the balloons swell until they start to pop."
{
  const t0 = at('And as'), tc = at('colder'), ts = at('swell'), tp = at('pop');
  const ol = [
    { t: t0, x: 270, y: 780, size: 1, expr: 'happy', look: [0, -4], arms: 'up', fL: 6, fR: 2 },
    { t: tc, expr: 'scared', mouth: 'grit', ease: 'hold' },
    { t: tp - 0.1, expr: 'shocked', ease: 'hold' },
  ];
  cue(tc, 'squeak', 0.5); cue(ts, 'slide_up', 0.6); cue(tp + 0.1, 'pop'); cue(tp + 0.35, 'pop'); cue(tp + 0.55, 'pop', 0.8);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5.5, z: 1.05 }],
    draw(lt, t) {
      clouds(t, 160, 3610, 5);
      airDots(t, Math.round(lerp(70, 10, clamp((t - at('thinner')) / 1.4, 0, 1))), 3620, { drift: 160 });
      const P = poseAt(ol, t);
      if (t > tc) P.x += DRAWING % 2 ? 2.5 : -2.5;
      const A0 = drawChar(OLLIE, P, { shadow: false });
      const swell = 1 + 0.32 * EASE.io(clamp((t - ts) / 0.9, 0, 1));
      const hand = [(A0.hands[0][0] + A0.hands[1][0]) / 2, (A0.hands[0][1] + A0.hands[1][1]) / 2];
      const gone = i => i === 7 ? tp + 0.1 : i === 23 ? tp + 0.35 : i === 40 ? tp + 0.55 : 1e9;
      bunch(t, 270, 330, 60, 19, hand, 3700, { swell, gone, face: 'o' });
    },
  });
}

// 7. "In 1982, a man tied about forty weather balloons to a lawn chair."  A backyard launch.
{
  const t0 = at('In'), tr = at('lawn');
  const pi = [
    { t: t0, x: 262, y: GY - 56, expr: 'happy', look: [2, -4], arms: 'down' },
    ...A.wave(at('weather'), VO_END(), 'R'),
  ];
  cue(at('tied'), 'pop', 0.5); cue(tr, 'slide_up', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, y: 520 }, { t: 4.6, z: 1, y: 470 }],
    draw(lt, t) {
      band(BLUE, 0, 520, 3800);
      clouds(t, 0, 3810, 3);
      fence(GY, 3820);
      ground(GY);
      const lift = Math.max(0, t - tr) * 55;
      const seat = [270, GY - lift];
      const items = bunch(t, 275, 300 - lift, 16, 34, null, 3900, { color: PAPER, face: 'smile' });
      // strings from the balloons to the chair
      items.slice(0, 8).forEach((b, k) => line([[b.x, b.y + 40], [seat[0] + (k - 4) * 9, seat[1] - 120]], 1.8, 3950 + k, INK, 0.5, false));
      lawnChair(seat[0], seat[1], 3960);
      const P = poseAt(pi, t);
      P.y -= lift;
      drawChar(PILOT, P, { shadow: false });
      if (lift > 0) fillOnly(blobPts(270, GY + 5, 60 * Math.max(0.3, 1 - lift / 200), 6, 3970, 9), BLUE, 3970);
    },
  });
}

// 8. "He floated nearly five kilometres up, cold and scared, and came down by popping them, one by one."
{
  const t0 = at('He floated'), tp = at('popping');
  const pops = [0, 1, 2, 3, 4].map(k => tp + k * 0.28);
  const pi = [
    { t: t0, x: 262, y: 640, expr: 'happy', look: [-3, 3], arms: 'down' },
    { t: at('cold'), expr: 'scared', ease: 'hold' },
    { t: tp - 0.15, expr: 'determined', ease: 'hold' },
    ...A.sigh(at('one', 3)),
  ];
  pops.forEach(p => cue(p, 'pop'));
  shot(t0, {
    cap: 420,
    cam: [{ t: 0, z: 0.94, y: 500 }, { t: 6, z: 1.04, y: 480 }],
    draw(lt, t) {
      band(BLUE, 0, 2000, 4000);
      const fall = Math.max(0, t - tp) * 45;
      clouds(t < tp ? t : tp, 30, 4010, 5);
      clouds(0, 0, 4020, 3);
      const seat = [270, 640 + 56 + fall * 0.3];
      const gone = i => [5, 11, 2, 14, 8].indexOf(i) >= 0 ? pops[[5, 11, 2, 14, 8].indexOf(i)] : 1e9;
      const items = bunch(t, 275, 260 + fall * 0.3, 16, 34, null, 3900, { color: PAPER, gone, face: 'o' });
      items.filter(b => t < gone(b.i)).slice(0, 8).forEach((b, k) => line([[b.x, b.y + 40], [seat[0] + (k - 4) * 9, seat[1] - 120]], 1.8, 4050 + k, INK, 0.5, false));
      lawnChair(seat[0], seat[1], 3960);
      const P = poseAt(pi, t);
      P.y = seat[1] - 56;
      if (t > at('cold') && t < tp) P.x += DRAWING % 2 ? 2.5 : -2.5;
      drawChar(PILOT, P, { shadow: false });
    },
  });
}

// 9. "So yes, balloons can lift you. Getting down is the hard part."  Back to one balloon; let it go.
{
  const t0 = at('So yes'), tr = at('hard');
  const ol = [
    { t: t0, x: 255, y: GY, size: 1.3, expr: 'happy', ...HOLD },
    ...A.nod(at('yes'), 2),
    ...A.shrug(at('Getting') - 0.05, { hold: 0.5, after: 'smile' }),
    { t: tr - 0.05, ...HOLD, expr: 'happy', ease: 'hold' },
    { t: tr + 0.1, aR: 2.9, bend: 0.4, reach: 1, expr: 'surprised', lookAt: [360, 300], ease: 'hold' },
    ...A.wave(tr + 0.5, VO_END(), 'R'),
  ];
  cue(tr + 0.1, 'zip', 0.6);
  shot(t0, {
    tr: 'iris', iris: [268, 680],
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4.4, z: 1.08, y: 560 }],
    draw(lt, t) {
      band(BLUE, 0, 380, 4100);
      clouds(t, 0, 4110, 3);
      hills(GY - 70);
      ground(GY);
      const A0 = drawChar(OLLIE, poseAt(ol, t));
      const free = Math.max(0, t - tr - 0.1);
      const bx = 345 + free * 25 + Math.sin(t * 2) * 6, by = 450 + Math.sin(t * 2.5) * 6 - free * 150 - free * free * 40;
      balloon(bx, by, 44, RED, 3020, { face: free > 0 ? 'happy' : 'smile', string: free > 0 ? [bx - 6 + Math.sin(t * 4) * 8, by + 150] : A0.hands[1] });
    },
  });
}
