// Ranking the worst planets to get lost on. Ten shots, timed with at('word').

// 1. "Your spaceship just left without you, and you're lost on a planet."
{
  const tl = at('lost', 1);
  const me = [
    { t: 0, x: 200, y: GY, expr: 'happy', look: [3, -3], lookAt: [400, 200] },
    { t: at('left') - 0.1, expr: 'curious', look: [4, -4], ease: 'hold' },
    ...A.take(tl - 0.1, { hold: 0.5, mouth: 'wavy' }),
    { t: at('planet'), expr: 'scared', look: [-3, 1], ease: 'hold' },
  ];
  cue(at('left'), 'whoosh');
  shot(0, {
    tr: 'cut',
    cam: [{ t: 0, z: 1 }, { t: 3.6, z: 1.06 }],
    draw(lt, t) {
      setSpace(t, { gy: GY });
      const u = clamp((t - 0.3) / 2.4, 0, 1);
      rocket(lerp(330, 560, EASE.in(u)), lerp(330, -60, EASE.in(u)), 1.5, 101, t);
      if (u > 0 && u < 1) speedLines(lerp(300, 530, EASE.in(u)), lerp(400, 10, EASE.in(u)), [0.5, -1], 60, 10, 105, 3);
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 2. "Let's rank four, worst last."
{
  const t0 = at("Let's");
  const me = [
    { t: t0, x: 140, y: GY, expr: 'curious', look: [3, -3] },
    ...A.point(at('four', 1), 'R'),
    { t: at('worst') - 0.1, expr: 'determined', ease: 'hold' },
  ];
  const rows = [['Mercury', 90, PAPER], ['Jupiter', 200, YEL], ['Neptune', 320, BLUE], ['Venus', 440, RED]];
  const sizes = [30, 46, 38, 34];
  cue(at('four', 1), 'pop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 2, z: 1.04 }],
    draw(lt, t) {
      setSpace(t, { gy: GY });
      rows.forEach(([n, x, col], i) => {
        const tt = t0 + 0.4 + i * 0.25, k = EASE.back(clamp((t - tt) / (3 * D), 0, 1));
        if (k > 0) planet(x + 10, 260 + (i % 2) * 70 + Math.sin(t * 2 + i) * 4, sizes[i] * k, col, 110 + i * 10, 'smile', ['craters', 'bands', 'swirl', 'acid'][i]);
      });
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 3. "Number four: Mercury. With no real atmosphere, the day side hits eight hundred degrees Fahrenheit."
{
  const t0 = at('Number', 1), th = at('eight', 1), tm = at('Mercury');
  const me = [
    { t: t0, x: 190, y: GY, expr: 'curious', look: [3, -2] },
    { t: th, expr: 'worried', ease: 'hold' },
    { t: at('Fahrenheit', 1) - 0.4, expr: 'shocked', fx: 'sweat', ease: 'hold' },
  ];
  cue(tm, 'pop'); cue(th, 'slide_up', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 5.5, z: 1.08, y: 520 }],
    draw(lt, t) {
      band(YEL, 0, 760, 120);
      ground(GY, 121, { fill: PAPER, grass: false });
      const k = EASE.back(clamp((t - tm + 0.3) / (3 * D), 0, 1));
      planet(380, 230, 80 * k, PAPER, 125, t > th ? 'o' : 'smile', 'craters');
      burst(380, 230, 95, 130 + Math.sin(t * 10) * 6, 130, 0);
      thermo(70, 560, t > th ? lerp(0.3, 0.97, EASE.out(clamp((t - th) / 1.2, 0, 1))) : 0.3, 140);
      if (t > th) [-40, 0, 40].forEach((dx, i) => wisp(P_X(me, t) + dx, 680, 60, 150 + i, t, RED, 3));
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 4. "Then at night, it drops to about minus two hundred ninety. You'd be cooked, then frozen, with no air to complain about it."
{
  const t0 = at('Then at'), tc = at('cooked'), tf = at('frozen');
  const me = [
    { t: t0, x: 190, y: GY, expr: 'shocked', fx: 'sweat' },
    { t: at('minus'), expr: 'scared', ease: 'hold' },
    ...[0, 1, 2, 3, 4, 5, 6, 7].map(i => ({ t: at('ninety') + i * D, lean: i % 2 ? 0.05 : -0.05, ease: 'hold' })),
    { t: tc - 0.1, lean: 0, expr: 'dizzy', ease: 'hold' },
    { t: tf, expr: 'squeeze', mouth: 'grit', ease: 'hold' },
    ...[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => ({ t: tf + 0.3 + i * D, lean: i % 2 ? 0.05 : -0.05, ease: 'hold' })),
    { t: at('complain'), lean: 0, expr: 'sigh', mouth: 'sigh', ease: 'hold' },
  ];
  cue(at('night'), 'slide_down', 0.7); cue(tf, 'tick', 0.7);
  shot(t0, {
    tr: 'cut',
    cap: 420,
    cam: [{ t: 0, z: 1.05 }, { t: 6.5, z: 1.1, y: 540 }],
    draw(lt, t) {
      band(BLUE, 0, 760, 160);
      ground(GY, 161, { fill: PAPER, grass: false });
      planet(400, 230, 70, PAPER, 165, t > tf ? 'frown' : 'o', 'craters');
      const k = clamp((t - t0) / 1.4, 0, 1);
      thermo(70, 560, t < tc ? lerp(0.97, 0.05, EASE.io(k)) : 0.05, 170, t < at('night') + 0.4 ? RED : BLUE);
      if (t > tf) icicles(150, 700, 7, 175);
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 5. "Number three: Jupiter. Jupiter has no ground at all, only swirling gas and liquid, getting denser as you sink."
{
  const t0 = at('Number', 2), tj = at('Jupiter', 1), ts = at('sink');
  const me = [
    { t: t0, x: 270, y: 640, expr: 'curious', look: [0, 3] },
    { t: at('ground', 1), expr: 'surprised', look: [0, 4], ease: 'hold' },
    { t: at('swirling'), y: 650, ease: 'io' },
    { t: ts, y: 730, sy: 0.96, expr: 'worried', ease: 'io' },
  ];
  cue(tj, 'pop'); cue(at('swirling'), 'slide_down', 0.5);
  shot(t0, {
    tr: 'smear',
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 6, z: 1.06, y: 540 }],
    draw(lt, t) {
      band(YEL, 0, 960, 200);
      [0, 1, 2, 3, 4].forEach(i => line(wavePts(-20, 160 + i * 190, 560, 150 + i * 190, 2, 9, t * 3 + i), 14, 210 + i, i % 2 ? RED : PAPER, 0.5, false));
      const k = EASE.back(clamp((t - tj) / (3 * D), 0, 1));
      planet(430, 140, 90 * k, YEL, 220, t > at('ground', 1) ? 'o' : 'smile', 'bands');
      drawChar(LOST, poseAt(me, t), { shadow: false });
    },
  });
}

// 6. "You can't land. You just fall, and the pressure climbs."
{
  const t0 = at("can't"), tf = at('fall'), tp0 = at('pressure');
  const me = [
    { t: t0, x: 270, y: 330, expr: 'scared', look: [0, 4], arms: 'up' },
    { t: tf + 0.3, y: 520, sy: 1.04, sx: 0.97, ease: 'in' },
    { t: tp0, y: 560, sy: 1, sx: 1, ease: 'io' },
    { t: at('climbs') - 0.2, y: 570, sy: 0.7, sx: 1.25, expr: 'pinch', ease: 'hold' },
  ];
  cue(tf, 'slide_down', 0.8); cue(tp0, 'drum', 0.4);
  shot(t0, {
    tr: 'cut',
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.1 }],
    draw(lt, t) {
      band(RED, 0, 960, 230);
      [0, 1, 2, 3].forEach(i => line(wavePts(-20, 140 + i * 230, 560, 150 + i * 230, 2, 9, t * 3 + i), 16, 240 + i, YEL, 0.5, false));
      if (t < tp0 + 1) speedLines(270, 450, [0, -1], 80, 40, 250, 5);
      drawChar(LOST, poseAt(me, t), { shadow: false });
      if (t > tp0) [[100, 640, 1], [440, 640, -1]].forEach(([x, y, d], i) => arrow([x, y - 40 + (DRAWING % 2) * 6], [x + d * 70, y - 40 + (DRAWING % 2) * 6], 260 + i, INK, 0));
      if (t > tp0) [[100, 480, 1], [440, 480, -1]].forEach(([x, y, d], i) => arrow([x, y], [x + d * 70, y], 270 + i, INK, 0));
    },
  });
}

// 7. "Number two: Neptune. Neptune has no surface either, and it's the windiest world in the solar system."
{
  const t0 = at('Number', 3), tn = at('Neptune', 1);
  const me = [
    { t: t0, x: 220, y: GY, expr: 'curious', look: [3, -2] },
    { t: at('windiest') - 0.1, lean: 0.12, expr: 'scared', ease: 'out' },
    { t: at('windiest') + 0.6, x: 250, lean: 0.16, ease: 'io' },
  ];
  cue(tn, 'pop'); cue(at('windiest'), 'whoosh', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 4.5, z: 1.06 }],
    draw(lt, t) {
      setSpace(t, { gy: GY });
      const k = EASE.back(clamp((t - tn + 0.2) / (3 * D), 0, 1));
      planet(380, 220, 85 * k, BLUE, 300, t > at('windiest') ? 'o' : 'smile', 'swirl');
      if (t > at('surface')) [0, 1, 2, 3, 4].forEach(i => speedLines(((t * 700 + i * 170) % 700) - 80, 330 + i * 90, [-1, 0], 90, 8, 310 + i, 2));
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 8. "Its winds top twelve hundred miles an hour, about nine times Earth's. Your hat would not survive."
{
  const t0 = at('Its winds'), tw = at('hat'), tg = at('survive');
  const me = [
    { t: t0, x: 220, y: GY, lean: 0.16, expr: 'scared', look: [3, 0] },
    { t: at('Earth\'s'), expr: 'worried', ease: 'hold' },
    { t: tw, expr: 'surprised', lean: 0.2, look: [4, -3], ease: 'hold' },
    { t: tg, expr: 'sad', lean: 0.1, look: [4, -2], ease: 'hold' },
  ];
  cue(tw, 'whoosh', 0.8); cue(tg, 'slide_down', 0.6);
  shot(t0, {
    tr: 'cut',
    cap: 420,
    cam: [{ t: 0, z: 1.05 }, { t: 4.5, z: 1.1, y: 540 }],
    draw(lt, t) {
      band(BLUE, 0, 760, 330);
      ground(GY, 331, { fill: PAPER, grass: false });
      [0, 1, 2, 3, 4, 5].forEach(i => speedLines(((t * 800 + i * 140) % 700) - 90, 150 + i * 105, [-1, 0], 100, 8, 340 + i, 2));
      const P = poseAt(me, t);
      const an = drawChar(LOSTH, P);
      if (t < tw) hatProp(an.top[0], an.top[1] + 4, 0.1, 350);
      else {
        const u = t - tw;
        hatProp(an.top[0] - u * 500, an.top[1] - u * 180 + u * u * 300, -u * 9, 350);
      }
    },
  });
}

// 9. "Number one: Venus. Venus has an actual ground, which sounds nice, until you stand on it."
{
  const t0 = at('Number', 4), tv = at('Venus', 1), ts = at('stand');
  const me = [
    { t: t0, x: 220, y: GY, expr: 'curious', look: [3, -2] },
    { t: at('nice'), expr: 'happy', ease: 'hold' },
    ...A.jump(ts - 0.1, [220, GY], [220, GY], { height: 50 }),
    { t: ts + 0.5, expr: 'shocked', fx: 'sweat', ease: 'hold' },
  ];
  for (let i = 0; i < 8; i++) me.push({ t: ts + 0.7 + i * 2 * D, y: GY - (i % 2 ? 0 : 14), fL: i % 2 ? 0 : 12, fR: i % 2 ? 12 : 0, ease: 'hold' });
  cue(tv, 'pop'); cue(ts, 'squeak', 0.7);
  shot(t0, {
    tr: 'smear',
    cap: 420,
    cam: [{ t: 0, z: 1 }, { t: 5.5, z: 1.08, y: 540 }],
    draw(lt, t) {
      band(RED, 0, 760, 400);
      const k = EASE.back(clamp((t - tv + 0.2) / (3 * D), 0, 1));
      planet(390, 220, 80 * k, YEL, 405, t > ts ? 'o' : 'smile', 'acid');
      ground(GY, 401, { fill: t > ts ? YEL : PAPER, grass: false });
      if (t > ts) [-50, 0, 50].forEach((dx, i) => wisp(P_X(me, t) + dx, 820, 50, 410 + i, t, INK, 3));
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 10. "It's about eight hundred seventy degrees Fahrenheit, hot enough to melt lead."
{
  const t0 = at("It's about"), th = at('eight', 2), tm = at('melt');
  const me = [
    { t: t0, x: 160, y: GY, expr: 'shocked', fx: 'sweat' },
    { t: tm - 0.1, expr: 'surprised', look: [4, 2], ease: 'hold' },
  ];
  cue(th, 'slide_up', 0.7); cue(tm, 'plop');
  shot(t0, {
    tr: 'cut',
    cap: 'top',
    cam: [{ t: 0, z: 1 }, { t: 4, z: 1.06 }],
    draw(lt, t) {
      band(RED, 0, 760, 420);
      ground(GY, 421, { fill: YEL, grass: false });
      thermo(450, 620, lerp(0.5, 1, EASE.out(clamp((t - th) / 1.4, 0, 1))), 430);
      lead(320, GY - 6, EASE.io(clamp((t - tm) / 1.2, 0, 1)), 435);
      burst(450, 420, 24, 40 + Math.sin(t * 10) * 4, 440, 0);
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 11. "The air presses on you ninety-three times harder than on Earth, like a kilometer underwater, under sulfuric acid clouds."
{
  const t0 = at('The air'), tn = at('ninety-three'), tk = at('kilometer'), tc = at('clouds');
  const me = [
    { t: t0, x: 270, y: GY, expr: 'worried', look: [0, -3] },
    { t: tn, y: GY, sy: 0.9, sx: 1.08, expr: 'pinch', ease: 'out' },
    { t: tk, sy: 0.78, sx: 1.18, expr: 'squeeze', ease: 'io' },
    { t: at('acid'), sy: 0.75, sx: 1.2, expr: 'scared', look: [0, -4], ease: 'hold' },
  ];
  cue(tn, 'drum', 0.5); cue(tk, 'slide_down', 0.6); cue(tc, 'plop', 0.6);
  shot(t0, {
    tr: 'smear',
    cap: 420,
    cam: [{ t: 0, z: 1 }, { t: 7, z: 1.08, y: 540 }],
    draw(lt, t) {
      band(BLUE, 0, 960, 450);
      band(RED, 0, 220, 451);
      [90, 270, 450].forEach((x, i) => shape(cloudPts(x, 150 + (i % 2) * 20, 70, 28, 455 + i), YEL, 3, 455 + i, 0.8));
      if (t > tc) [60, 200, 330, 470].forEach((x, i) => drop(x, 260 + ((t * 300 + i * 90) % 400), 8, 460 + i, YEL));
      line(wavePts(-20, 330, 560, 330, 4, 6, t * 2), 5, 470, PAPER, 0.5, false);
      [[90, 1], [450, -1]].forEach(([x, d], i) => arrow([x, 420 + (t > tn ? (DRAWING % 2) * 6 : 0)], [x + d * 80, 420], 480 + i, INK, 0));
      drawChar(LOST, poseAt(me, t));
    },
  });
}

// 12. "So where would you rather get lost? Please say Earth."
{
  const t0 = at('So where'), te = at('Earth', 2);
  const me = [
    { t: t0, x: 200, y: GY, expr: 'curious', look: [3, -2] },
    ...A.shrug(at('rather') - 0.1, { hold: 0.4 }),
    { t: at('Please') - 0.1, expr: 'sad', arms: 'hug', ease: 'hold' },
    ...A.cheer(te - 0.1, GY, { height: 14 }),
    ...A.wave(te + 0.6, VO_END(), 'R'),
  ];
  cue(te, 'sparkle', 0.7);
  shot(t0, {
    tr: 'iris', iris: [200, 700],
    cam: [{ t: 0, z: 1 }, { t: 4, z: 1.1, y: 560 }],
    draw(lt, t) {
      setSpace(t, { gy: GY });
      const k = EASE.back(clamp((t - at('Please')) / (3 * D), 0, 1));
      if (k > 0) {
        planet(380, 260, 90 * k, BLUE, 500, t > te ? 'happy' : 'smile', 'swirl');
        if (t > te) { const alt = DRAWING % 4 < 2; plus(300, 180 + (alt ? 0 : 8), alt ? 7 : 5, 510); plus(470, 190, alt ? 5 : 7, 512); }
      }
      drawChar(LOST, poseAt(me, t));
    },
  });
}
