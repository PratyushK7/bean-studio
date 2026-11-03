// Does swallowed gum stay in you for 7 years? Nine shots timed to the voiceover.

// 1. "You just swallowed your gum, and everyone says it will sit inside you for seven years."
{
  const you = [
    { t: 0, x: 250, y: GY, expr: 'curious', look: [3, -2] },
    { t: 0.55, sy: 0.9, sx: 1.08, mouth: 'o', ease: 'out' },
    { t: 0.8, sy: 1, sx: 1, mouth: 'sigh', expr: 'neutral' },
    { t: at('everyone') - 0.1, expr: 'scared', look: [0, -4], ease: 'hold' },
  ];
  const gum = [
    { t: 0, x: 400, y: 700, size: 1, expr: 'happy' },
    { t: 0.55, x: 262, y: 690, size: 0.8, ease: 'in' },
  ];
  cue(0.58, 'plop'); cue(at('seven', 1), 'zip'); cue(at('years', 1), 'thud', 0.6);
  shot(0, {
    cam: [{ t: 0, z: 1 }, { t: 4.6, z: 1.06 }],
    draw(lt, t) {
      ground(GY);
      if (t > at('sit')) {
        shape(boxPts(110, 130, 320, 150, 720), PAPER, 4, 720);
        const n = Math.min(7, Math.floor((t - at('seven', 1)) / 0.1) + 1);
        if (t > at('seven', 1)) for (let i = 0; i < n; i++) line([[150 + i * 38, 160], [152 + i * 38, 250]], 6, 730 + i);
      }
      drawChar(YOU, poseAt(you, t));
      if (t < 0.62) drawChar(GUM, poseAt(gum, t));
    },
  });
}

// 2. "But your gut doesn't work like that."  The Gut shakes its head.
{
  const t0 = at('But');
  const gut = [
    { t: t0, x: 300, y: 560, size: 1.3, expr: 'neutral', look: [-2, 1] },
    ...A.shake(at("doesn't") - 0.1),
    { t: at('like') + 0.05, arms: 'hips', expr: 'smug', ease: 'hold' },
  ];
  const you = [
    { t: t0, x: 100, y: GY, size: 0.8, lookAt: [300, 520], expr: 'scared' },
    ...A.take(t0 + 0.1, { hold: 0.5, mouth: 'wavy' }),
  ];
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 1.8, z: 1 }],
    draw(lt, t) { ground(GY); drawChar(GUT, poseAt(gut, t)); drawChar(YOU, poseAt(you, t)); },
  });
}

// 3. "Gum is mostly a rubbery lump that your body can't digest."  Drops bounce off the lump.
{
  const t0 = at('Gum is'), td = at('digest', 1) - 0.5;
  const gum = [
    { t: t0, x: 270, y: 700, size: 2, expr: 'smug', arms: 'hips' },
    ...A.cheer(at('rubbery', 1) - 0.3, 700, { height: 16 }),
    { t: at('body') , expr: 'smug', arms: 'hips', ease: 'hold' },
  ];
  cue(td, 'pop', 0.6); cue(td + 0.35, 'pop', 0.6); cue(td + 0.7, 'pop', 0.6);
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1.05 }, { t: 3.6, z: 1.12, y: 520 }],
    draw(lt, t) {
      ground(GY - 60);
      for (let k = 0; k < 3; k++) {
        const u = (t - td - k * 0.35) / 0.5;
        if (u > 0 && u < 1) {
          const bx = 140 + k * 130, dir = k % 2 ? 1 : -1;
          drop(bx + dir * 60 * Math.max(0, u - 0.5) * 2, 330 + 330 * Math.min(u, 0.5) * 2 - 120 * Math.max(0, u - 0.5), 12, 740 + k);
        }
      }
      drawChar(GUM, poseAt(gum, t));
    },
  });
}

// 4. "Can't digest isn't the same as can't leave."  Gum strolls off, You watches.
{
  const t0 = at("Can't digest isn't");
  const walk = A.walk(t0 + 0.3, 90, 330, GY, { speed: 1 });
  const gum = [
    { t: t0, x: 90, y: GY, size: 1.2, expr: 'smug', facing: 1 },
    ...walk,
    ...A.dash(at('leave') - 0.25, 330, 490, GY, { endExpr: 'happy' }),
  ];
  const you = [
    { t: t0, x: 170, y: GY, size: 0.8, facing: 1, expr: 'curious', lookAt: [330, 700] },
    { t: at('same'), expr: 'thinking', ease: 'hold' },
    { t: at('leave') + 0.05, expr: 'happy', ease: 'hold' },
  ];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 2.4, z: 1.04, x: 300 }],
    draw(lt, t) { ground(GY); drawChar(YOU, poseAt(you, t)); drawChar(GUM, poseAt(gum, t)); },
  });
}

// 5. "Your gut squeezes everything along, one slow wave at a time."  Gum rides the S-bend.
{
  const t0 = at('Your gut squeezes') - 0.1, t1 = at('time') + 0.5;
  const gp = [{ t: t0, size: 0.75, expr: 'happy', arms: 'up' }];
  cue(at('squeezes'), 'slide_up', 0.5);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.6, z: 1.04 }],
    draw(lt, t) {
      drawGut();
      const u = Math.min(0.62, Math.max(0, (t - t0) / (t1 - t0)) * 0.62);
      for (let k = 0; k < 3; k++) { const us = u - 0.05 - k * 0.17; if (us > 0.02) squeeze(us); }
      squeeze(u + 0.07);
      const p = gutPt(u), P = poseAt(gp, t);
      P.x = p[0]; P.y = p[1] + 24;
      drawChar(GUM, P);
      const f = gutPt(0.06); miniFace(f[0], f[1], 0.9, 0, 750, t > at('slow') ? 'sleepy' : 'smile');
    },
  });
}

// 6. "The sweet parts dissolve, and the rubbery lump rides out with the leftovers."
{
  const t0 = at('The sweet') - 0.1, td = at('dissolve'), tr = at('rides');
  const gum = [{ t: t0, x: 100, y: 390, size: 1.4, expr: 'happy' }, { t: td, expr: 'surprised', ease: 'hold' }, { t: tr - 0.1, expr: 'happy', arms: 'up', ease: 'hold' }];
  const bits = Array.from({ length: 6 }, (_, i) => [60 + rnd(760, i) * 80, rnd(761, i) * 80 - 90, 6 + rnd(762, i) * 5]);
  cue(td, 'sparkle', 0.7); cue(tr, 'slide_down', 0.8);
  shot(t0, {
    cam: [{ t: 0, z: 1.04, x: 280, y: 480 }, { t: 3.8, z: 1, x: 270, y: 500 }],
    draw(lt, t) {
      shape([[20, 330], [510, 700], [510, 750], [20, 380]], BLUE, 4, 770);
      for (let i = 0; i < 4; i++) fillOnly(blobPts(400 + i * 28, 690 + i * 4, 10, 8, 780 + i, 6), INK, 780 + i);
      const su = (t - td) / 0.8, s = su > 0 ? Math.max(0, 1 - su) : 1;
      const w = Math.min(1, Math.max(0, (t - tr) / 1.1)), x = 100 + 300 * EASE.in(w), y = 330 + (x - 20) * 0.757 + 8;
      const P = poseAt(gum, t); P.x = x; P.y = y - 4 + (w > 0 && w < 1 ? 0 : 0);
      if (s > 0 && w < 0.4) bits.forEach(([dx, dy, r], i) => fillOnly(blobPts(P.x + dx, P.y + dy - su * 20 * (su > 0 ? 1 : 0), r * s, r * s, 790 + i, 6), YEL, 790 + i));
      if (su > 0 && su < 1.2) plus(P.x + 50, P.y - 120, 12, 800);
      drawChar(GUM, P);
    },
  });
}

// 7. "Doctors say that usually takes a few days."  The Doctor points at a three-dot calendar.
{
  const t0 = at('Doctors');
  const doc = [
    { t: t0, x: 150, y: GY, expr: 'happy', look: [3, -2] },
    ...A.point(at('usually') - 0.1, 'R', { ang: 2.5, mouth: 'open', after: 'smile' }),
  ];
  cue(at('takes'), 'tick', 0.8); cue(at('takes') + 0.25, 'tick', 0.8); cue(at('takes') + 0.5, 'tick', 0.8);
  shot(t0, {
    cam: [{ t: 0, z: 1.03 }, { t: 2.5, z: 1 }],
    draw(lt, t) {
      ground(GY);
      const n = [0, 1, 2].filter(i => t > at('takes') + i * 0.25).length;
      calendar(290, 230, n, 810);
      drawChar(DOC, poseAt(doc, t));
    },
  });
}

// 8. "Swallowing lots of gum can, rarely, cause a blockage, so don't make a habit of it."
{
  const t0 = at('Swallowing'), tl = at('lots'), tb = at('blockage');
  const you = [
    { t: t0, x: 140, y: 400, size: 0.9, expr: 'curious', look: [3, 3] },
    { t: tb - 0.15, expr: 'scared', ease: 'hold' },
    ...A.shake(at('habit') - 0.3, 2),
    { t: at('habit') + 0.5 , expr: 'smug', ease: 'hold' },
  ];
  const gums = [0, 1, 2, 3].map(i => [{ t: tl + i * 0.3, x: 90 + i * 72, y: 665, size: 0.75, expr: i === 3 ? 'scared' : 'happy' }]);
  gums.forEach((g, i) => cue(tl + i * 0.3, 'plop', 0.7));
  cue(tb, 'thud');
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 4.7, z: 1.05, y: 520 }],
    draw(lt, t) {
      const sw = t > tb ? 8 * Math.sin((t - tb) * 12) * Math.max(0, 1 - (t - tb)) : 0;
      tube([[-20, 640], [280, 640 + sw], [560, 640]], 112, YEL, 820);
      gums.forEach((g, i) => { if (t >= tl + i * 0.3) drawChar(GUM, poseAt(g, t)); });
      if (t > tb) { burst(430, 640, 30, 54, 830, 0); line([[392, 604], [468, 676]], 12, 831, RED); line([[468, 604], [392, 676]], 12, 832, RED); }
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9. "So your gum isn't staying seven years. It's just taking the long way out."  Wave goodbye, iris out.
{
  const t0 = at('So your') - 0.1;
  const tw = at('taking');
  const walk = A.walk(tw, 380, 500, GY, { speed: 0.6 });
  const gum = [
    { t: t0, x: 380, y: GY, size: 1.1, expr: 'happy', facing: 1 },
    ...walk,
    ...A.wave(walk.end, VO_END(), 'R'),
  ];
  const you = [
    { t: t0, x: 170, y: GY, size: 1.3, expr: 'curious', look: [3, -1] },
    ...A.shake(at("isn't", 2) - 0.2, 2),
    { t: at('long') - 0.1, expr: 'smug', look: [2, 0], ease: 'hold' },
    ...A.wave(at('way'), VO_END(), 'R'),
  ];
  shot(t0, {
    tr: 'iris', iris: [180, 660],
    cam: [{ t: 0, z: 1 }, { t: 4.8, z: 1.08, y: 520 }],
    draw(lt, t) { ground(GY); drawChar(YOU, poseAt(you, t)); drawChar(GUM, poseAt(gum, t)); },
  });
}
