// Why does time fly on a weekend? Twelve shots, none over 4 s, timed to the voiceover.
// hook: "time flies when you're having fun. It doesn't."  re-hook (halfway): "Here's the catch."  payoff: you just stop counting.
// payback: the flying clock from shot 1 lands for good in shot 11, and the last joke turns it around.

musicMood(0, 'curious', 0.9);
musicMood(at("Monday's"), 'serious', 0.8);
musicMood(at('Scientists'), 'curious', 0.8);
musicMood(at("Here's"), 'upbeat', 0.9);
musicMood(at('Fewer'), 'calm', 0.8);
musicMood(at('Want'), 'playful', 0.9);

// a clock with little wings (the saying "time flies"); flap = 0..1 how hard they beat, fall = limp
function wingClock(x, y, r, flap, seed, mood) {
  const w = Math.sin(NOW * 22) * 18 * flap;
  [-1, 1].forEach((s, i) => {
    const base = [x + s * r * 0.95, y];
    shape([base, [x + s * (r + 62), y - 46 - w], [x + s * (r + 84), y - 8 - w * 0.5], [x + s * (r + 52), y + 26], [x + s * r * 0.95, y + 16]], PAPER, 5, seed + i);
  });
  clockProp(x, y, r, 1.1, 3.4, seed + 5, mood);
}

// 1. "Everyone says time flies when you're having fun."  A winged clock flaps off while You cheers.
{
  const you = [
    { t: 0, x: 160, y: GY, size: 1.2, expr: 'happy', look: [3, -3] },
    ...A.cheer(at('fun') - 0.5, GY, { height: 60 }),
  ];
  cue(at('flies'), 'whoosh', 0.6);
  shot(0, {
    cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 2.7, z: 1 }],
    draw(lt, t) {
      setSunny(t);
      const up = Math.max(0, t - at('flies')) * 50;
      wingClock(370, 560 - up, 70, 1, 3100, 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 2. "That's not quite it. Monday's meeting lasts a year."  The clock drops with a plop; then the meeting, cobwebs.
{
  const t0 = at("That's") - 0.1, tm = at("Monday's") - 0.1;
  const you = [
    { t: t0, x: 160, y: GY, size: 1.2, expr: 'neutral', look: [3, 0] },
    { t: at("That's"), expr: 'determined', ease: 'hold' },
  ];
  const you2 = [
    { t: tm, x: 130, y: GY, size: 1.1, expr: 'neutral', facing: 1 },
    { t: at('year') - 0.3, expr: 'sleepy', fx: 'zzz', ease: 'hold' },
  ];
  const boss = [{ t: tm, x: 400, y: GY, size: 1.1, expr: 'happy', facing: -1 }, ...A.talk(tm, at('year') + 0.2)];
  cue(at("That's") + 0.15, 'plop', 0.7); cue(at('lasts'), 'tick', 0.5);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1.05 }, { t: 2.6, z: 1 }],
    draw(lt, t) {
      if (t < tm) {
        setSunny(t);
        const fall = Math.min(1, (t - at("That's")) / 0.25);
        wingClock(370, fall > 0 ? 520 + (GY - 520 - 70) * EASE.in(Math.max(0, fall)) : 520, 70, fall > 0 ? 0 : 1, 3100, 'frown');
        drawChar(YOU, poseAt(you, t));
      } else {
        setRoom(t, {});
        const g = Math.min(1, Math.max(0, (t - at('lasts')) / 1.2));
        clockProp(270, 230, 70, 2.1, 0.4 + Math.floor(t * 0.5) * 0.03, 3200, g > 0.5 ? 'sleepy' : 'flat');
        if (g > 0) { line([[0, 0], [0, 120 * g], [90 * g, 0]], 3, 3210, INK, 0.5); line([[540, 0], [540 - 100 * g, 0], [540, 130 * g]], 3, 3211, INK, 0.5); }
        drawChar(YOU, poseAt(you2, t));
        drawChar(BOSS, poseAt(boss, t));
      }
    },
  });
}

// 3. "Your weekend lasts ten minutes. Same clock."  Hands whirl, then two identical clocks.
{
  const t0 = at('Your', 1) - 0.1, ts = at('Same') - 0.05;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'happy' },
    ...A.take(at('ten') - 0.2, { hold: 0.6, mouth: 'wavy' }),
  ];
  const a = [{ t: ts, x: 130, y: GY, size: 0.9, expr: 'sleepy' }, { t: at('clock', 1) - 0.0, expr: 'curious', look: [3, -3], ease: 'hold' }];
  const b = [{ t: ts, x: 410, y: GY, size: 0.9, expr: 'happy' }, { t: at('clock', 1) - 0.0, expr: 'curious', look: [-3, -3], ease: 'hold' }];
  cue(at('ten'), 'zip', 0.6); cue(at('Same'), 'ding', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 2.6, z: 1.05 }],
    draw(lt, t) {
      if (t < ts) {
        setSunny(t);
        const w = Math.max(0, t - at('lasts', 2)) * 14;
        clockProp(330, 400, 110, 0.9 + w * 0.1, 0.9 + w, 3300, w > 0 ? 'o' : 'smile');
        drawChar(YOU, poseAt(you, t));
      } else {
        setBlank(t, YEL);
        ground(GY);
        clockProp(150, 400, 90, 0, 0, 3310, null); clockProp(390, 400, 90, 0, 0, 3311, null);
        line([[150, 400], [150, 360]], 7, 3312); line([[390, 400], [390, 360]], 7, 3313);
        line([[240, 400], [300, 400]], 8, 3314, RED); line([[240, 380], [300, 380]], 8, 3315, RED);
        drawChar(YOU, poseAt(a, t)); drawChar(YOU, poseAt(b, t));
      }
    },
  });
}

// 4. "So who's stealing your weekend?"  A sneaky Brain slides in and walks off with the WEEKEND tag.
{
  const t0 = at('So') - 0.1;
  const you = [
    { t: t0, x: 150, y: GY, size: 1.2, expr: 'curious', look: [3, -3] },
    { t: at('stealing'), look: [-3, 0], expr: 'surprised', ease: 'hold' },
  ];
  cue(at('stealing'), 'squeak', 0.6);
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 1.8, z: 1.05 }],
    draw(lt, t) {
      setBlank(t, BLUE);
      ground(GY);
      const k = EASE.out(Math.min(1, Math.max(0, (t - at("who's")) / 0.9)));
      const bx = 700 - 330 * k;
      const br = [{ t: 0, x: bx, y: 600, size: 1.1, expr: t > at('stealing') ? 'smug' : 'neutral', facing: -1 }];
      shape(boxPts(bx - 70, 690, 150, 56, 3400), YEL, 5, 3400);
      bigWord('WEEKEND', bx + 5, 724, 26, INK, 3410);
      drawChar(BRAIN, poseAt(br, t));
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 5. "Your brain, and it doesn't even own a clock."  The Brain shrugs, a crossed-out clock.
{
  const t0 = at('brain') - 0.4;
  const br = [
    { t: t0, x: 270, y: 480, size: 1.3, expr: 'smug' },
    ...A.shrug(at('even') - 0.1, { hold: 1.4 }),
  ];
  cue(at('even'), 'squeak', 0.6);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1.1 }, { t: 2.4, z: 1 }],
    draw(lt, t) {
      setBlank(t, BLUE);
      drawChar(BRAIN, poseAt(br, t));
      if (t > at('clock', 2) - 0.1) {
        const k = EASE.out(Math.min(1, (t - at('clock', 2)) / 0.3));
        clockProp(270, 240, 90 * k, null, null, 3500, null);
        miniFace(270, 245, 1.6 * k, 0, 3510, 'o');
        line([[200, 170], [340, 310]], 12, 3511, RED); line([[340, 170], [200, 310]], 12, 3512, RED);
      }
    },
  });
}

// 6. "Scientists think it guesses the time by counting how often you check."  Tally marks pile up.
{
  const t0 = at('Scientists') - 0.1, tc = at('counting', 1);
  const br = [
    { t: t0, x: 270, y: 560, size: 1.3, expr: 'thinking', fx: 'think' },
    { t: at('guesses') - 0.1, expr: 'smug', ease: 'hold' },
    { t: tc, expr: 'determined', ease: 'hold' },
  ];
  for (let i = 0; i < 6; i++) cue(tc + 0.2 + i * 0.35, 'tick', 0.5);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1 }, { t: 3.9, z: 1.06 }],
    draw(lt, t) {
      setBlank(t, YEL);
      drawChar(BRAIN, poseAt(br, t));
      const n = Math.max(0, Math.min(6, Math.floor((t - tc - 0.2) / 0.35) + 1));
      tally(150, 190, n, 3600, INK);
      if (t > at('check', 1)) miniFace(420, 250, 1.2, 0, 3610, 'o');
    },
  });
}

// 7. "At your desk, you check constantly, so the seconds pile up."  You eyes the clock, seconds heap up.
{
  const t0 = at('At') - 0.1, tp = at('seconds', 1);
  const you = [
    { t: t0, x: 130, y: GY, size: 1.1, expr: 'sad', lookAt: [400, 250] },
    { t: at('check', 2), look: [4, -4], ease: 'hold' },
    { t: at('pile'), expr: 'sleepy', ease: 'hold' },
  ];
  cue(at('check', 2), 'tick', 0.6); cue(at('constantly'), 'tick', 0.6);
  shot(t0, {
    tr: 'smear', cap: 420,
    cam: [{ t: 0, z: 1 }, { t: 3.5, z: 1.05 }],
    draw(lt, t) {
      setRoom(t, {});
      clockProp(410, 230, 70, 1, t * 0.2, 3700, 'flat');
      desk(30, 600, 280, 3710);
      drawChar(YOU, poseAt(you, t));
      const n = Math.max(0, Math.min(12, Math.floor((t - tp) / 0.12) + 1));
      for (let i = 0; i < n; i++) secondBlob(380 + (i % 4) * 34 - Math.floor(i / 4) * 6, 760 - Math.floor(i / 4) * 24, 16, 3720 + i);
    },
  });
}

// 8. "Here's the catch. On a Saturday you're"  The re-hook: a flash, You spins round, happy.
{
  const t0 = at("Here's") - 0.1;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'curious', look: [3, -3] },
    ...A.take(at('catch') - 0.1, { hold: 0.5, mouth: 'wavy' }),
    { t: at('Saturday'), expr: 'happy', ease: 'hold' },
  ];
  cue(at('catch'), 'ding', 0.7);
  shot(t0, {
    cam: [{ t: 0, z: 1.1 }, { t: 2.3, z: 1 }],
    draw(lt, t) {
      setSunny(t);
      if (t > at('catch') - 0.1 && t < at('catch') + 0.7) burst(380, 380, 60 + (t - at('catch')) * 120, 130 + (t - at('catch')) * 120, 3800, V, 8);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9. "too busy to look, so the counting stops."  The clock lies forgotten on the ground, hands stuck.
{
  const t0 = at('busy') - 0.2;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'happy' },
    ...A.cheer(at('busy') - 0.1, GY, { height: 60 }),
    ...A.cheer(at('look') - 0.1, GY, { height: 60 }),
  ];
  cue(at('stops'), 'deflate', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 2.2, z: 1.05 }],
    draw(lt, t) {
      setSunny(t);
      shape(blobPts(440, 760, 52, 52, 3900, 14, 0.02), PAPER, 6, 3900);
      line([[440, 760], [440, 730]], 6, 3901); line([[440, 760], [465, 770]], 5, 3902);
      miniFace(440, 772, 1.1, 0, 3903, t > at('stops') ? 'sleepy' : 'frown');
      drawChar(YOU, poseAt(you, t));
      if (t > at('look')) plus(110, 450, 18, 3910);
    },
  });
}

// 10. "Fewer counted seconds, less time. The real clock never slowed."  A tall pile and a short pile; then the clock ticks on, smug.
{
  const t0 = at('Fewer') - 0.1, tr = at('real') - 0.1;
  const you = [
    { t: t0, x: 270, y: GY, size: 1.1, expr: 'curious', look: [-3, 0] },
    { t: at('less'), look: [3, 0], expr: 'thinking', ease: 'hold' },
  ];
  const you2 = [{ t: tr, x: 140, y: GY, size: 1.1, expr: 'thinking' }, { t: at('never'), expr: 'surprised', ease: 'hold' }];
  cue(at('Fewer'), 'plop', 0.6); cue(at('never'), 'ding', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3.8, z: 1.04 }],
    draw(lt, t) {
      if (t < tr) {
        setBlank(t, BLUE);
        ground(GY);
        const k = Math.min(1, (t - t0) / 1.4);
        const nA = Math.round(14 * k), nB = Math.round(4 * k);
        for (let i = 0; i < nA; i++) secondBlob(90 + (i % 2) * 26, 770 - i * 26, 16, 4000 + i);
        for (let i = 0; i < nB; i++) secondBlob(450 + (i % 2) * 26, 770 - i * 26, 16, 4030 + i);
        drawChar(YOU, poseAt(you, t));
      } else {
        setSunny(t);
        clockProp(370, 380, 100, t * 0.3, t * 3.6, 4100, 'smile');
        drawChar(YOU, poseAt(you2, t));
      }
    },
  });
}

// 11. "So time flies when you stop counting. Fun just helps you forget."  The payback: the winged clock from shot 1 sits on the ground, wings limp.
{
  const t0 = at('So', 4) - 0.2, tf = at('flies', 2);
  const you = [
    { t: t0, x: 170, y: GY, size: 1.2, expr: 'happy' },
    ...A.cheer(at('Fun', 2) - 0.2, GY, { height: 50 }),
    { t: at('forget'), expr: 'smug', ease: 'hold' },
  ];
  cue(tf, 'squeak', 0.5);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 3.8, z: 1 }],
    draw(lt, t) {
      setSunny(t);
      // it tries to take off at "fly" and flops straight back down
      const hop = Math.max(0, Math.sin((t - tf) * 5)) * (t > tf && t < tf + 0.6 ? 24 : 0);
      wingClock(380, GY - 74 - hop, 74, t > tf && t < tf + 0.6 ? 0.8 : 0.05, 4200, t > at('forget') ? 'smile' : 'frown');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 12a. "Want a longer weekend? Stare at the clock."  You glares at the clock.
{
  const t0 = at('Want') - 0.1;
  const you = [
    { t: t0, x: 140, y: GY, size: 1.2, expr: 'curious', look: [3, -3] },
    { t: at('Stare'), expr: 'determined', lookAt: [380, 400], ease: 'hold' },
  ];
  cue(at('Stare'), 'tick', 0.5);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.06 }],
    draw(lt, t) {
      setSunny(t);
      clockProp(390, 400, 100, 0.3, t * 0.4, 4300, 'smug');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 12b. "It works great, and ruins everything."  Hands crawl, You wilts; held to the end, the iris closes on the face.
{
  const t0 = at('works') - 0.3;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'determined', lookAt: [380, 400] },
    { t: at('ruins') - 0.1, expr: 'sad', ease: 'hold' },
    ...A.sigh(at('everything') - 0.2),
  ];
  cue(at('ruins'), 'deflate', 0.7);
  shot(t0, {
    tr: 'iris', iris: [200, 560], cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 4, z: 1.1 }],
    draw(lt, t) {
      setNight(t);
      clockProp(390, 400, 100, 0.3, 0.4 + (t - t0) * 0.15, 4400, t > at('ruins') ? 'smug' : 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}
