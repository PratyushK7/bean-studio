// What if you grew 1 cm every second? Seventeen shots, timed to the voiceover with at('word').

// 1. "What if you grew one centimetre every single second?"  Bo grows a hair while Pip watches.
{
  const you = [
    { t: 0, x: 330, y: GY, size: 1.0, expr: 'curious', look: [2, -3] },
    { t: at('every'), size: 1.0, ease: 'hold' },
    { t: at('second'), size: 1.08, expr: 'surprised', ease: 'back' },
  ];
  const pip = [{ t: 0, x: 120, y: GY, size: 1.1, expr: 'neutral', lookAt: [330, 700] }, ...A.shrug(at('single'))];
  cue(at('second'), 'pop');
  shot(0, {
    cam: [{ t: 0, z: 1.02 }, { t: 2.8, z: 1.07, y: 500 }],
    draw(lt, t) {
      dayScene(t);
      drawChar(PIP, poseAt(pip, t));
      drawChar(YOU, poseAt(you, t));
      if (t > at('second')) { arrow([450, 700], [450, 600], 11, RED, 0.1); plus(440, 570, 14, 12); }
    },
  });
}

// 2. "That sounds slow. A centimetre is about as wide as a fingernail."  A giant finger, a nail, a bracket.
{
  const t0 = at('That', 1), tn = at('fingernail');
  const pip = [
    { t: t0, x: 105, y: GY, size: 1.2, expr: 'sleepy', lookAt: [270, 500] },
    { t: tn - 0.1, expr: 'curious', ease: 'hold' },
  ];
  cue(at('centimetre', 2), 'zip', 0.6); cue(tn, 'sparkle', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 4, z: 1.06, y: 520 }],
    draw(lt, t) {
      band(YEL, 0, 520, 320);
      ground(GY);
      shape(blobPts(300, 700, 62, 330, 450, 12, 0.02), PAPER, 4, 450);
      shape(boxPts(272, 408, 56, 78, 451), BLUE, 3.4, 451);
      if (t > at('wide')) {
        arrow([300, 524], [330, 524], 452, RED, 0);
        arrow([300, 524], [270, 524], 453, RED, 0);
      }
      if (t > tn) plus(345, 400, 14, 454);
      drawChar(PIP, poseAt(pip, t));
    },
  });
}

// 3. "But watch the clock."  A worried clock ticks round fast; Bo does a take.
{
  const t0 = at('But', 1);
  const you = [{ t: t0, x: 270, y: GY, size: 1.0, expr: 'neutral' }, ...A.take(t0 + 0.2, { hold: 0.4 })];
  cue(t0 + 0.1, 'tick'); cue(t0 + 0.4, 'tick'); cue(t0 + 0.7, 'tick');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 1.1, z: 1.08 }],
    draw(lt, t) {
      dayScene(t);
      clockProp(270, 300, 120, -Math.PI / 2 + (t - t0) * TAU * 1.3);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 4. "After one minute, you're sixty centimetres taller. Your trousers, sadly, are not."
{
  const t0 = at('After', 1), tg = at('taller', 1);
  const you = [
    { t: t0, x: 270, y: GY, size: 1.0, expr: 'curious' },
    { t: t0 + 0.2, size: 1.0, ease: 'hold' },
    { t: tg + 0.1, size: 1.35, expr: 'surprised', ease: 'lin' },
    { t: at('trousers', 1) - 0.1, expr: 'worried', look: [0, 4], ease: 'hold' },
  ];
  const pip = [
    { t: t0, x: 95, y: GY, size: 1.1, expr: 'neutral', lookAt: [270, 600] },
    ...A.shrug(at('sadly') - 0.1, { hold: 0.8 }),
  ];
  for (let k = 0; k < 6; k++) cue(t0 + 0.4 + k * 0.28, 'tick', 0.5);
  cue(at('sadly'), 'slide_down', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4.5, z: 1.04, y: 520 }],
    draw(lt, t) {
      dayScene(t);
      drawChar(PIP, poseAt(pip, t));
      drawChar(YOU, poseAt(you, t));
      trousers(270, GY - 62, 1.05);
      if (t < tg + 0.4) arrow([430, 760], [430, 600], 13, RED, 0.1);
    },
  });
}

// 5. "In under two minutes, you're taller than the tallest human ever recorded."  Bo overtakes Wadlow.
{
  const t0 = at('In under'), tt = at('tallest', 1);
  const you = [
    { t: t0, x: 150, y: GY, size: 1.35, expr: 'happy' },
    { t: tt - 0.2, size: 2.2, expr: 'smug', ease: 'lin' },
    { t: at('recorded'), look: [3, 0], ease: 'hold' },
  ];
  const wad = [
    { t: t0, x: 400, y: GY, size: 1.6, expr: 'neutral', lookAt: [150, 400] },
    { t: tt + 0.1, expr: 'surprised', ease: 'hold' },
    ...A.take(at('human') + 0.1, { hold: 0.5 }),
  ];
  cue(t0 + 0.8, 'slide_up', 0.6); cue(tt + 0.2, 'ding', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 520 }, { t: 4, z: 1, y: 500 }],
    draw(lt, t) {
      dayScene(t);
      const hy = GY - 256;
      for (let i = 0; i < 10; i++) line([[20 + i * 52, hy], [42 + i * 52, hy]], 3.2, 460 + i, RED, 0.5, false);
      drawChar(WAD, poseAt(wad, t));
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 6. "That was Robert Wadlow, at two point seven two metres."  Wadlow takes a bow beside a tape measure.
{
  const t0 = at('That was');
  const wad = [
    { t: t0, x: 240, y: GY, size: 1.85, expr: 'happy', look: [2, 0] },
    ...A.nod(at('Robert'), 2),
  ];
  const top = GY - 160 * 1.9 * 1.0;
  cue(at('seven'), 'ding', 0.6);
  shot(t0, {
    cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 3.4, z: 1.06, y: 500 }],
    draw(lt, t) {
      band(YEL, 0, 520, 320);
      ground(GY);
      // tape measure
      line([[455, GY], [455, 330]], 6, 470, INK, 0.8, false);
      for (let i = 0; i <= 14; i++) line([[455, GY - i * 33.5], [455 + (i % 5 ? 14 : 28), GY - i * 33.5]], 3, 471 + i, INK, 0.5, false);
      if (t > at('point')) {
        arrow([380, 400], [450, GY - 296], 480, RED, 0.1);
      }
      drawChar(WAD, poseAt(wad, t));
    },
  });
}

// 7. "Congratulations. You now need a new front door."  Bo is far too big for the door.
{
  const t0 = at('Congratulations');
  const you = [
    { t: t0, x: 150, y: GY, size: 2.4, expr: 'happy' },
    ...A.cheer(t0 + 0.1, GY, { height: 14 }),
    { t: at('You now'), expr: 'sad', arms: 'down', look: [4, 2], ease: 'hold' },
    ...A.sigh(at('door') - 0.3),
  ];
  const pip = [{ t: t0, x: 440, y: GY, size: 1.1, expr: 'smug', lookAt: [150, 400] }, ...A.shrug(at('need'), { hold: 0.7 })];
  cue(at('need'), 'slide_down', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 2.9, z: 1.04, y: 520 }],
    draw(lt, t) {
      dayScene(t);
      door(340, GY - 240, 120, 240);
      drawChar(PIP, poseAt(pip, t));
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 8. "After an hour, you're thirty-six metres taller, about a twelve-storey building."
{
  const t0 = at('After an hour');
  const you = [
    { t: t0, x: 135, y: GY, size: 2.4, expr: 'curious' },
    { t: at('hour'), size: 2.4, ease: 'hold' },
    { t: at('thirty-six'), size: 3.4, expr: 'surprised', ease: 'out' },
    { t: at('building'), expr: 'smug', ease: 'hold' },
  ];
  const pip = [{ t: t0, x: 290, y: GY, size: 1.0, expr: 'curious', lookAt: [135, 100] }, ...A.shake(at('building') - 0.3, 1)];
  cue(at('thirty-six'), 'slide_up', 0.7);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4.3, z: 1, y: 500 }],
    draw(lt, t) {
      dayScene(t);
      flats(330, GY - 540, 170, GY, 12);
      drawChar(PIP, poseAt(pip, t));
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9. "Here's the catch. Double your height and your weight multiplies by eight, but your bones only get four times stronger."
{
  const t0 = at("Here's"), tw = at('multiplies'), tb = at('bones', 1), ts = at('stronger');
  const CX = 270, CY = 650, HL = 215;
  const nW = (t) => Math.max(0, Math.min(8, Math.floor((t - tw) / 0.2) + 1)), nB = (t) => Math.max(0, Math.min(4, Math.floor((t - tb) / 0.25) + 1));
  const ang = (t) => {
    const a = -0.34 * Math.min(1, Math.max(0, (t - tw) / 1.2));
    return a + 0.14 * Math.min(1, Math.max(0, (t - (ts - 0.9)) / 0.9));
  };
  const you = [{ t: t0, x: 270, y: 330, size: 0.001, hide: true }];
  cue(tw, 'pop', 0.6);
  for (let i = 1; i < 8; i++) cue(tw + i * 0.2, 'pop', 0.5);
  for (let i = 0; i < 4; i++) cue(tb + i * 0.25, 'plop', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 6, z: 1.05, y: 500 }],
    draw(lt, t) {
      band(YEL, 0, 520, 320);
      ground(GY);
      const th = ang(t), c = Math.cos(th), s = Math.sin(th);
      shape([[CX - 50, GY], [CX + 50, GY], [CX, CY + 18]], BLUE, 3.4, 500);
      tube([[CX - HL * c, CY - HL * s], [CX + HL * c, CY + HL * s]], 13, RED === 0 ? YEL : YEL, 501);
      const place = (u, h) => [CX + u * c + h * s, CY + u * s - h * c - 6];
      for (let i = 0; i < nW(t); i++) {
        const [x, y] = place(-190 + (i % 4) * 46, i < 4 ? 0 : 44);
        drawChar(WGT, poseAt([{ t: 0, x, y, expr: 'scared', lean: -th * 0.6 }], t), { shadow: false });
      }
      for (let i = 0; i < nB(t); i++) {
        const [x, y] = place(60 + i * 46, 0);
        drawChar(BON, poseAt([{ t: 0, x, y, expr: 'determined', lean: -th * 0.6 }], t), { shadow: false });
      }
    },
  });
}

// 10. "So past three metres or so, you'd probably collapse."  Bo wobbles, then folds.
{
  const t0 = at('So past'), tc = at('collapse');
  const you = [
    { t: t0, x: 270, y: GY, size: 2.8, expr: 'determined', brow: 0.4 },
    { t: tc - 1.0, lean: 0.05, ease: 'io' },
    { t: tc - 0.7, lean: -0.07, expr: 'scared', ease: 'io' },
    { t: tc - 0.4, lean: 0.08, ease: 'io' },
    { t: tc - 0.1, lean: -0.04, sy: 0.96, ease: 'io' },
    { t: tc + 0.1, lean: 0, sy: 0.45, sx: 1.45, expr: 'dizzy', eyes: 'dead', fx: 'dust0', ease: 'in' },
    { t: tc + 0.4, sy: 0.5, sx: 1.4, fx: 'dust1', ease: 'out' },
  ];
  cue(tc + 0.1, 'thud'); cue(tc - 0.7, 'squeak', 0.5);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 2.6, z: 1, y: 520 }, { t: 3.0, shake: 5 }],
    draw(lt, t) {
      dayScene(t);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 11. "Your heart would also struggle to pump blood all the way up."  A tiny heart, a very long neck.
{
  const t0 = at('Your heart'), tp = at('pump');
  const you = [
    { t: t0, x: 270, y: GY, size: 4.0, expr: 'worried', look: [0, 3] },
    { t: at('way up'), expr: 'sad', ease: 'hold' },
  ];
  cue(tp, 'drum', 0.6);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 3.2, z: 1, y: 500 }],
    draw(lt, t) {
      dayScene(t);
      drawChar(YOU, poseAt(you, t));
      // heart in the chest, sweating, with blood that rises and falls back
      const beat = 1 + 0.18 * Math.abs(Math.sin((t - t0) * 6));
      heart(270, 640, 28 * beat, 510);
      miniFace(270, 646, 1.7, 0, 511, 'frown');
      if (t > tp) {
        line([[250, 610], [165, 560], [165, 300]], 3, 512, RED, 0.8, false);
        for (let i = 0; i < 4; i++) {
          const u = ((t - tp) * 0.9 + i * 0.25) % 1, y = 560 - 170 * Math.sin(u * Math.PI * 0.5) + (u > 0.6 ? (u - 0.6) * 220 : 0);
          drop(165, y, 7, 520 + i);
        }
      }
    },
  });
}

// 12. "Let's pretend your bones, heart and lungs all keep up."  A thumbs-up from a very large bean.
{
  const t0 = at("Let's");
  const you = [
    { t: t0, x: 200, y: GY, size: 2.2, expr: 'smug', arms: 'hips' },
    ...A.nod(at('bones', 2), 2),
    { t: at('keep') - 0.1, expr: 'happy', ease: 'hold' },
  ];
  const pip = [{ t: t0, x: 430, y: GY, size: 1.3, expr: 'sigh' }, { t: t0 + 0.4, lookAt: [200, 400], ease: 'hold' }, ...A.shrug(at('lungs') - 0.1, { hold: 0.8 })];
  cue(at('keep'), 'sparkle', 0.7);
  shot(t0, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 3.4, z: 1.05, y: 520 }],
    draw(lt, t) {
      dayScene(t);
      drawChar(PIP, poseAt(pip, t));
      drawChar(YOU, poseAt(you, t));
      if (t > at('bones', 2)) plus(80, 360, 14, 530);
      if (t > at('heart', 2)) plus(330, 300, 12, 531);
      if (t > at('lungs')) plus(130, 220, 16, 532);
    },
  });
}

// 13. "In a day, you'd be taller than the Burj Khalifa."
{
  const t0 = at('In a day');
  const you = [
    { t: t0, x: 150, y: GY, size: 4.5, expr: 'smug', look: [3, 2] },
    { t: at('Burj'), expr: 'happy', ease: 'hold' },
  ];
  cue(t0 + 0.1, 'slide_up', 0.6);
  shot(t0, {
    tr: 'smear', cap: 690,
    cam: [{ t: 0, z: 1, y: 500 }, { t: 2.8, z: 1, y: 480 }],
    draw(lt, t) {
      dayScene(t);
      // stepped tower and spire
      shape([[370, GY], [400, GY - 380], [420, GY - 380], [430, GY - 500], [445, GY - 500], [450, GY - 560], [452, GY - 650], [458, GY - 650], [460, GY - 560], [465, GY - 500], [480, GY - 500], [490, GY - 380], [520, GY - 380], [545, GY]], BLUE, 3.6, 540, 1, 4);
      for (let i = 0; i < 6; i++) line([[410 + i * 4, GY - 20 - i * 60], [498 - i * 4, GY - 20 - i * 60]], 2.2, 541 + i, PAPER, 0.6, false);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 14. "In ten days, you'd tower over Everest, with your head in air too thin to breathe."
{
  const t0 = at('In ten'), tt = at('thin');
  const you = [
    { t: t0, x: 190, y: 880, size: 4.8, expr: 'smug' },
    { t: tt - 0.3, expr: 'scared', mouth: 'o', ease: 'hold' },
    { t: tt + 0.3, expr: 'dizzy', fx: 'sweat', ease: 'hold' },
  ];
  cue(at('Everest'), 'ding', 0.5); cue(tt, 'deflate', 0.7);
  shot(t0, {
    tr: 'smear', cap: 690,
    cam: [{ t: 0, z: 1, y: 500 }, { t: 4.4, z: 1, y: 480 }],
    draw(lt, t) {
      band(BLUE, 0, 640, 301);
      cloud(380, 150, 50, 18, 311);
      cloud(110, 230, 40, 14, 312);
      ground(880);
      shape([[300, 880], [420, 540], [450, 560], [480, 620], [570, 880]], INK, 3.6, 550, 1, 4);
      shape([[330, 800], [420, 548], [450, 566], [470, 610], [500, 700]], PAPER, 3.6, 551, 1, 4);
      shape([[400, 590], [420, 540], [450, 560], [462, 592], [440, 600], [425, 590]], PAPER, 3.2, 552, 1, 4);
      drawChar(YOU, poseAt(you, t));
      if (t > tt - 0.3) for (let i = 0; i < 5; i++) fillOnly(blobPts(110 + rnd(560, i) * 330, 100 + rnd(561, i) * 220, 4, 4, 570 + i, 6), PAPER, 570 + i);
    },
  });
}

// 15. "In four months, your head pokes into space."
{
  const t0 = at('In four'), ts = at('space');
  const you = [
    { t: t0, x: 270, y: 890, size: 4.2, expr: 'scared', mouth: 'o', look: [0, -4] },
    { t: ts - 0.1, expr: 'surprised', eyes: 'wide', ease: 'hold' },
  ];
  cue(ts - 0.1, 'sparkle', 0.7); cue(t0, 'slide_up', 0.6);
  shot(t0, {
    tr: 'smear', cap: 690,
    cam: [{ t: 0, z: 1, y: 560 }, { t: 2.4, z: 1, y: 480 }],
    draw(lt, t) {
      spaceScene(t);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 16. "And in about twelve hundred years, you'd finally touch the Moon."  One fingertip, one startled Moon.
{
  const t0 = at('And in about'), tm = at('Moon');
  const you = [
    { t: t0, x: 240, y: 890, size: 4.2, expr: 'determined', look: [3, -4] },
    { t: at('touch') - 0.2, expr: 'curious', look: [3, -4], ease: 'hold' },
    { t: tm, expr: 'love', ease: 'hold' },
  ];
  cue(tm - 0.1, 'plop', 0.8); cue(tm, 'squeak', 0.6);
  shot(t0, {
    tr: 'smear', cap: 690,
    cam: [{ t: 0, z: 1, y: 500 }, { t: 3.4, z: 1, y: 480 }],
    draw(lt, t) {
      spaceScene(t);
      const k = Math.min(1, Math.max(0, (t - (at('finally') + 0.1)) / (tm - at('finally') - 0.1)));
      const mx = lerp(440, 350, EASE.io(k)), my = lerp(140, 205, EASE.io(k));
      moon(mx, my, 56, 580);
      miniFace(mx - 8, my + 4, 2.4, 0, 581, t > tm ? 'o' : 'smile');
      drawChar(YOU, poseAt(you, t));
      if (t > tm) plus(mx + 70, my - 70, 14, 582);
    },
  });
}

// 17. "The hardest part would still be finding trousers."  Pip holds up the trousers; Bo shrugs and waves.
{
  const t0 = at('The hardest'), tt = at('trousers', 2);
  const you = [
    { t: t0, x: 270, y: 890, size: 4.2, expr: 'smug', look: [-1, 4] },
    ...A.shrug(tt - 0.6, { hold: 0.6 }),
    { t: tt + 0.1, expr: 'happy', ease: 'hold' },
    ...A.wave(tt + 0.5, VO_END(), 'R'),
  ];
  const pip = [
    { t: t0, x: 455, y: 890, size: 1.1, expr: 'smug', arms: 'up', lookAt: [270, 400] },
    { t: tt - 0.4, arms: 'up', expr: 'happy', ease: 'hold' },
  ];
  cue(tt, 'ding', 0.6);
  shot(t0, {
    tr: 'iris', iris: [270, 400], cap: 690,
    cam: [{ t: 0, z: 1, y: 500 }, { t: 6, z: 1.04, y: 480 }],
    draw(lt, t) {
      spaceScene(t);
      moon(420, 215, 62, 580);
      miniFace(412, 219, 2.4, 0, 581, 'happy');
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(PIP, poseAt(pip, t));
      trousers(a.top ? a.top[0] : 90, (a.top ? a.top[1] : 790) - 95, 0.9, 590);
    },
  });
}
