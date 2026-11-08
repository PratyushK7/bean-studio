// Why does the weekend fly by faster? Shots timed to the voiceover.

// music: light and curious, dragging through the meeting, bright on Saturday, tense when Sunday night lands, playful again at the end
musicMood(0, 'curious', 0.9);
musicMood(at('Meanwhile'), 'serious', 0.8);
musicMood(at('On a'), 'upbeat', 0.9);
musicMood(at('Sunday'), 'tense', 0.8);
musicMood(at('Want'), 'playful', 0.9);

// 1a. "Your weekend is forty-eight hours long,"  You holds up a huge clock, hands crawling.
{
  const you = [
    { t: 0, x: 200, y: GY, size: 1.2, expr: 'curious', look: [3, -3], arms: 'up' },
    { t: at('hours') - 0.1, expr: 'happy', ease: 'hold' },
  ];
  cue(at('hours'), 'ding', 0.6);
  shot(0, {
    cam: [{ t: 0, z: 1.04 }, { t: 2.4, z: 1 }],
    draw(lt, t) {
      setSunny(t);
      const h = (t / 2.4) * 0.6;
      clockProp(330, 270, 120, h, h * 12, 3100, 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 1b. "so why does it feel like ten minutes?"  Hands whirl, You takes it badly.
{
  const t0 = at('so', 1);
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'happy' },
    ...A.take(at('feel') - 0.1, { hold: 0.6, mouth: 'wavy' }),
    { t: at('ten'), expr: 'sad', ease: 'hold' },
  ];
  cue(at('feel'), 'zip', 0.6); cue(at('ten'), 'slide_down', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 2.2, z: 1.06 }],
    draw(lt, t) {
      setSunny(t);
      const w = Math.max(0, t - at('feel')) * 14;
      clockProp(330, 270, 120, 0.9 + w * 0.1, 0.9 + w, 3100, t > at('feel') ? 'o' : 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 2a. "Meanwhile, a Monday meeting can last a year,"  Boss talks, You nods off, cobwebs grow.
{
  const t0 = at('Meanwhile') - 0.1, tw = at('Monday');
  const you = [
    { t: t0, x: 130, y: GY, size: 1.1, expr: 'neutral', facing: 1 },
    { t: at('last') - 0.2, expr: 'sleepy', fx: 'zzz', ease: 'hold' },
  ];
  const boss = [
    { t: t0, x: 400, y: GY, size: 1.1, expr: 'happy', facing: -1 },
    ...A.talk(t0, at('year') + 0.4),
  ];
  cue(tw, 'tick', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.05 }],
    draw(lt, t) {
      setRoom(t, {});
      const g = Math.min(1, Math.max(0, (t - at('last')) / 1.2));
      clockProp(270, 230, 70, 2.1, 0.4 + Math.floor(t * 0.5) * 0.03, 3200, g > 0.5 ? 'sleepy' : 'flat');
      if (g > 0) { line([[0, 0], [0, 120 * g], [90 * g, 0]], 3, 3210, INK, 0.5); line([[540, 0], [540 - 100 * g, 0], [540, 130 * g]], 3, 3211, INK, 0.5); }
      drawChar(YOU, poseAt(you, t));
      drawChar(BOSS, poseAt(boss, t));
    },
  });
}

// 2b. "and it's made of the exact same minutes."  Two identical clocks, same time.
{
  const t0 = at("it's made") - 0.1;
  const a = [{ t: t0, x: 130, y: GY, size: 0.9, expr: 'sleepy' }, { t: at('exact'), expr: 'curious', look: [3, -3], ease: 'hold' }];
  const b = [{ t: t0, x: 410, y: GY, size: 0.9, expr: 'happy' }, { t: at('exact'), expr: 'curious', look: [-3, -3], ease: 'hold' }];
  cue(at('same'), 'ding', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 2.2, z: 1.04 }],
    draw(lt, t) {
      setBlank(t, YEL);
      ground(GY);
      const k = Math.min(1, Math.max(0, (t - at('exact')) / 0.4));
      clockProp(150, 400, 90, 0, 0, 3300 + 0, null);
      clockProp(390, 400, 90, 0, 0, 3301, null);
      line([[150, 400], [150, 400 - 40]], 7, 3302); line([[390, 400], [390, 400 - 40]], 7, 3303);
      if (k > 0) { line([[240, 400], [300, 400]], 8, 3304, RED); line([[240, 380], [300, 380]], 8, 3305, RED); }
      drawChar(YOU, poseAt(a, t)); drawChar(YOU, poseAt(b, t));
    },
  });
}

// 3. "Your brain has no clock you can read."  The Brain shrugs, holding a blank clock.
{
  const t0 = at('brain') - 0.4;
  const br = [
    { t: t0, x: 270, y: 480, size: 1.3, expr: 'smug' },
    ...A.shrug(at('no') - 0.1, { hold: 1.4 }),
  ];
  cue(at('no'), 'squeak', 0.6);
  shot(t0, {
    cap: 690,
    cam: [{ t: 0, z: 1.1 }, { t: 2.6, z: 1 }],
    draw(lt, t) {
      setBlank(t, BLUE);
      drawChar(BRAIN, poseAt(br, t));
      if (t > at('clock', 1) - 0.1) {
        const k = EASE.out(Math.min(1, (t - at('clock', 1)) / 0.3));
        clockProp(270, 240, 90 * k, null, null, 3400, null);
        miniFace(270, 245, 1.6 * k, 0, 3410, 'o');
        line([[200, 170], [340, 310]], 12, 3411, RED); line([[340, 170], [200, 310]], 12, 3412, RED);
      }
    },
  });
}

// 4. "Scientists think it guesses, by counting how often you pay attention to time."
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
    cam: [{ t: 0, z: 1 }, { t: 4.4, z: 1.06 }],
    draw(lt, t) {
      setBlank(t, YEL);
      drawChar(BRAIN, poseAt(br, t));
      const n = Math.max(0, Math.min(6, Math.floor((t - tc - 0.2) / 0.35) + 1));
      tally(150, 190, n, 3500, INK);
      if (t > at('attention')) { const a = poseAt(br, t); miniFace(420, 250, 1.2, 0, 3510, 'o'); }
    },
  });
}

// 5. "At your desk, you check the clock again and again, so the seconds pile up."
{
  const t0 = at('At your') - 0.1, tp = at('seconds', 1);
  const you = [
    { t: t0, x: 130, y: GY, size: 1.1, expr: 'sad', lookAt: [400, 250] },
    { t: at('check'), look: [4, -4], ease: 'hold' },
    { t: at('again', 1), expr: 'sleepy', ease: 'hold' },
  ];
  cue(at('again', 1), 'tick', 0.6); cue(at('again', 2), 'tick', 0.6);
  shot(t0, {
    cap: 420,
    cam: [{ t: 0, z: 1 }, { t: 3.9, z: 1.05 }],
    draw(lt, t) {
      setRoom(t, {});
      const m = t * 0.2;
      clockProp(410, 230, 70, 1, m, 3600, 'flat');
      desk(30, 600, 280, 3610);
      drawChar(YOU, poseAt(you, t));
      const n = Math.max(0, Math.min(12, Math.floor((t - tp) / 0.12) + 1));
      for (let i = 0; i < n; i++) secondBlob(380 + (i % 4) * 34 - Math.floor(i / 4) * 6, 760 - Math.floor(i / 4) * 24, 16, 3620 + i);
    },
  });
}

// 6. "On a Saturday, you're busy, you forget to look, and the counting stops."
{
  const t0 = at('On a') - 0.1;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.2, expr: 'happy' },
    ...A.cheer(at("you're", 1) - 0.1, GY, { height: 60 }),
    ...A.cheer(at('forget') - 0.1, GY, { height: 60 }),
  ];
  cue(at('stops'), 'deflate', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.4, z: 1.05 }],
    draw(lt, t) {
      setSunny(t);
      // the clock lies forgotten on the ground, hands stuck
      shape(blobPts(440, 760, 52, 52, 3700, 14, 0.02), PAPER, 6, 3700);
      line([[440, 760], [440, 730]], 6, 3701); line([[440, 760], [465, 770]], 5, 3702);
      miniFace(440, 772, 1.1, 0, 3703, t > at('stops') ? 'sleepy' : 'frown');
      drawChar(YOU, poseAt(you, t));
      if (t > at('forget')) plus(110, 450, 18, 3710);
    },
  });
}

// 7a. "Fewer counted seconds feels like less time,"  A tall pile vs a short pile.
{
  const t0 = at('Fewer') - 0.1;
  const you = [
    { t: t0, x: 270, y: GY, size: 1.1, expr: 'curious', look: [-3, 0] },
    { t: at('less'), look: [3, 0], expr: 'thinking', ease: 'hold' },
  ];
  cue(at('Fewer'), 'plop', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3.4, z: 1.04 }],
    draw(lt, t) {
      setBlank(t, BLUE);
      ground(GY);
      const k = Math.min(1, (t - t0) / 1.5);
      const nA = Math.round(14 * k), nB = Math.round(4 * k);
      for (let i = 0; i < nA; i++) secondBlob(90 + (i % 2) * 26, 770 - i * 26, 16, 3800 + i);
      for (let i = 0; i < nB; i++) secondBlob(450 + (i % 2) * 26, 770 - i * 26, 16, 3830 + i);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 7b. "even though the real clock never slowed."  The clock ticks on, smug.
{
  const t0 = at('even though') - 0.1;
  const you = [{ t: t0, x: 140, y: GY, size: 1.1, expr: 'thinking' }, { t: at('never'), expr: 'surprised', ease: 'hold' }];
  cue(at('never'), 'ding', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1.05 }, { t: 2.4, z: 1 }],
    draw(lt, t) {
      setSunny(t);
      clockProp(370, 290, 110, t * 0.3, t * 3.6, 3900, 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 8. "Sunday night still arrives exactly on schedule."
{
  const t0 = at('Sunday') - 0.1;
  const you = [
    { t: t0, x: 170, y: GY, size: 1.2, expr: 'happy' },
    ...A.take(at('arrives') - 0.2, { hold: 0.6, mouth: 'wavy' }),
    { t: at('schedule'), expr: 'sad', ease: 'hold' },
  ];
  cue(at('night'), 'slide_down', 0.5);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 2.6, z: 1.06 }],
    draw(lt, t) {
      if (t < at('night') - 0.1) setSunny(t); else setNight(t);
      const k = Math.min(1, Math.max(0, (t - at('exactly')) / 0.3));
      clockProp(400, 330, 80, 0, 0, 4000, 'smile');
      line([[400, 330], [400, 330 - 60]], 7, 4001);
      if (k > 0) { clockProp(400, 330, 80, 6.28 * 0 + 3.14, 3.14 * 2, 4002, 'smug'); }
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9a. "Want a longer weekend? Try watching the clock."  You glares at the clock.
{
  const t0 = at('Want') - 0.1;
  const you = [
    { t: t0, x: 140, y: GY, size: 1.2, expr: 'curious', look: [3, -3] },
    { t: at('Try'), expr: 'determined', lookAt: [380, 400], ease: 'hold' },
  ];
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.06 }],
    draw(lt, t) {
      setSunny(t);
      clockProp(390, 400, 100, 0.3, t * 0.4, 4100, 'smug');
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9b. "It works great, and ruins everything."  Hands crawl, You wilts; held to the end.
{
  const t0 = at('works') - 0.3;
  const you = [
    { t: t0, x: 140, y: GY, size: 1.2, expr: 'determined', lookAt: [380, 400] },
    { t: at('ruins') - 0.1, expr: 'sad', ease: 'hold' },
    ...A.sigh(at('everything') - 0.2),
  ];
  cue(at('ruins'), 'deflate', 0.7);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1.04 }, { t: 3, z: 1.1 }],
    draw(lt, t) {
      setNight(t);
      clockProp(390, 400, 100, 0.3, 0.4 + (t - t0) * 0.15, 4100, t > at('ruins') ? 'smug' : 'smile');
      if (t > at('ruins')) { drawChar(YOU, poseAt(you, t)); } else drawChar(YOU, poseAt(you, t));
    },
  });
}

// 10. "And why does the first day of a holiday last forever?"  The closing hook: a slow, sunny clock, You looks up and the iris closes on the face.
{
  const t0 = at('And why') - 0.1;
  const you = [
    { t: t0, x: 200, y: GY, size: 1.25, expr: 'curious', lookAt: [380, 380] },
    { t: at('forever'), expr: 'surprised', ease: 'hold' },
    ...A.sigh(at('forever') + 0.5),
  ];
  cue(at('forever'), 'ding', 0.5);
  shot(t0, {
    tr: 'iris', iris: [200, 560], cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.08 }],
    draw(lt, t) {
      setSunny(t);
      clockProp(390, 380, 110, 0.5, 0.5 + (t - t0) * 0.12, 4200, 'smile');
      drawChar(YOU, poseAt(you, t));
    },
  });
}
