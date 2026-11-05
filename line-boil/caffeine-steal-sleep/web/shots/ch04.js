// CHAPTER 4: "How long caffeine stays" (script lines 43 to 57). The liver, the half-life, and how much it wobbles.

musicMood(at('So how long does') - 0.2, 'calm');        // a clear explanation
musicMood(at("If that's you") - 0.2, 'playful');        // the doctor joke and the party guest

// the liver's workshop: a red room with a yellow floor and a big clock on the wall
function workshop(t, hour, o = {}) {
  const gy = setRoom(t, { wall: RED, floor: YEL });
  clockFace(o.cx ?? 560, o.cy ?? 120, o.r ?? 60, hour, 4001, { wedge: o.wedge });
  return gy;
}
// a row of tiny caffeine beans; `gone(i)` returns the time bean i pops out (or Infinity)
function cafRow(t, xs, y, gone, seed, look = [0, 0]) {
  xs.forEach((x, i) => {
    const tg = gone(i);
    if (t > tg + 0.25) return;
    const P = { x, y, size: 1, expr: t > tg ? 'surprised' : 'smug', look, breathe: 1.5 };
    drawChar(CAFS[i % CAFS.length], Object.assign(poseAt([{ t: 0 }], t), P, t > tg ? { sy: 1.3, sx: 0.8, y: y - 40 * (t - tg) / 0.25 } : {}));
    if (t > tg && t < tg + 0.25) burst(x, y - 40, 14, 30, seed + i, 0);
  });
}

// 1. "So how long does caffeine stay in the slot?"  Caffeine, settled in, glances at the clock.
{
  const t0 = at('So how long does');
  const caf = [{ t: t0, expr: 'smug', look: [3, -3] }, { t: at('stay in') , look: [0, -4], ease: 'hold' }];
  shot(t0, {
    cam: [{ t: 0, z: 1.06, y: 250 }, { t: 2.5, z: 1, y: 270 }],
    draw(lt, t) {
      workshop(t, 3 + lt * 0.5);
      const slot = mailbox(400, 443, 1.8, 4110, { face: 'smile' });
      cafInSlot(slot, caf, t);
      popLabel(t, t0 + 0.4, 'HOW LONG?', 760, 250, 30, { seed: 4120, fill: YEL, rot: 0.04 });
    },
  });
}

// 2. "That's up to your liver, which slowly breaks caffeine down and clears it out."  The liver sweeps tiny caffeine beans out of the door.
{
  const t0 = at("That's up to your"), tl = at('liver', 1), tb = at('breaks caffeine');
  const liv = [...dropIn(tl, 300, 443, { expr: 'neutral' }), { t: tl + 0.4, size: 1.2, ease: 'hold' }];
  for (let k = 0, tk = tb - 0.2; tk < at('clears it out') + 1.2; k++, tk += 0.5) liv.push({ t: tk, aR: 0.9, aL: -0.2, bend: 0.4, x: 300 + k * 12, ease: 'io' }, { t: tk + 0.25, aR: 0.4, aL: 0.3, ease: 'io' });
  liv.unshift({ t: t0, size: 1.2, glasses: true });
  const xs = [520, 590, 660, 730];
  cue(tb, 'slide_up', 0.4);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      workshop(t, 3.5 + lt * 0.3);
      doorway(880, 443, 110, 210, 4210, INK);
      const sweep = clamp((t - tb) * 30, 0, 140);
      xs.forEach((x, i) => drawChar(CAFS[i], Object.assign(poseAt([{ t: 0, expr: 'scared', look: [-3, 0] }], t), { x: x + sweep + Math.sin(t * 12 + i) * (t > tb ? 3 : 0), y: 443, size: 1 })));
      const P = poseAt(liv, t);
      let hand = [P.x + 60, P.y - 60];
      drawChar(LIV, P, { hold: h => { hand = h[1]; } });
      if (P.y > 0) broom(hand, hand[0] + 50, 443, 4220);
      popLabel(t, tl + 0.2, 'LIVER', 300, 470, 24, { seed: 4230, fill: PAPER });
    },
  });
}

// 3. "Scientists measure this with a half-life: the time it takes your body to get rid of half of it."  Eight beans, then four.
{
  const t0 = at('Scientists measure'), th = at('half-life', 1), tg = at('half of it', 1);
  const xs = [140, 230, 320, 410, 550, 640, 730, 820];
  cue(tg, 'pop'); cue(tg + 0.12, 'pop', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 4301, { grass: false });
      cafRow(t, xs, 443, i => i >= 4 ? tg + (i - 4) * 0.1 : Infinity, 4310, [0, -2]);
      popLabel(t, th - 0.05, 'HALF-LIFE', 480, 110, 40, { seed: 4320, fill: YEL });
      if (t > tg + 0.4) popLabel(t, tg + 0.4, 'HALF GONE', 685, 330, 24, { seed: 4330, rot: 0.04 });
    },
  });
}

// 4. "For a typical healthy adult, caffeine's half-life is around four to five hours on average."  The big clock fills in four to five hours.
{
  const t0 = at('For a typical'), tf = at('four to five');
  const you = [{ t: t0, x: 800, y: 443, size: 1.1, expr: 'neutral', look: [-4, -3] }, { t: tf + 0.6, expr: 'surprised', ease: 'hold' }];
  const liv = [{ t: t0, x: 200, y: 443, size: 1.15, expr: 'neutral', look: [4, -3] }, ...A.point(tf - 0.3, 'R', { ang: 2.4, after: 'smile' })];
  cue(tf, 'slide_up', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5, z: 1.04, y: 255 }],
    draw(lt, t) {
      const w = t < tf ? 0 : lerp(0, 4.5, EASE.io(clamp((t - tf) / 1.2, 0, 1)));
      workshop(t, w, { cx: 480, cy: 200, r: 130, wedge: [0, w, YEL] });
      drawChar(LIV, poseAt(liv, t));
      drawChar(YOU, poseAt(you, t));
      popLabel(t, tf + 0.9, '4 TO 5 HOURS', 480, 395, 30, { seed: 4410, fill: PAPER, rot: -0.03 });
      popLabel(t, at('on average') - 0.05, 'ON AVERAGE', 480, 460, 18, { seed: 4415, fill: YEL });
    },
  });
}

// 5. "That's a long time for something you finished in ten minutes."  YOU tips the empty mug; 10 MIN against 5 HOURS.
{
  const t0 = at("That's a long time"), tm = at('ten minutes');
  const you = [{ t: t0, x: 480, y: 443, size: 1.3, expr: 'neutral', look: [0, 0], arms: 'hold' }, { t: tm, aR: 2.4, bend: 0.6, ease: 'back' }, { t: tm + 0.6, eyes: 'half', mouth: 'flat', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 4501, { grass: false });
      drawChar(YOU, poseAt(you, t), { hold: h => { if (t > tm) { ctx.save(); ctx.translate(h[1][0] + 6, h[1][1] - 4); ctx.rotate(Math.PI); mug(0, 0, 1.0, 4510, {}); ctx.restore(); if (t > tm + 0.2 && t < tm + 0.9) drop(h[1][0] + 4, h[1][1] + 24, 5, 4515); } else mug(h[1][0] + 4, h[1][1] + 16, 1.0, 4510, {}); } });
      popLabel(t, t0 + 0.3, '5 HOURS', 760, 180, 36, { seed: 4520, fill: PAPER, rot: 0.04 });
      popLabel(t, tm, '10 MIN', 200, 180, 36, { seed: 4525, fill: PAPER, rot: -0.04 });
    },
  });
}

// 6. "And that average hides a lot of wobble. Some people clear half of it in about two hours. For others, it takes eight hours or more."
{
  const t0 = at('And that average'), tw = at('wobble'), t2 = at('two hours'), t8 = at('eight hours', 1);
  cue(tw, 'boing', 0.6); cue(t2, 'pop'); cue(t8, 'pop');
  const bounce = (t, ts) => t > ts ? Math.max(0, Math.sin((t - ts) * 14) * 12 * Math.exp(-(t - ts) * 4)) : 0;
  shot(t0, {
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: RED });
      const wob = t > tw ? Math.sin(t * 9) * 0.06 * Math.exp(-(t - tw) * 1.2) : 0;
      [[200, 2, t2, '2 H'], [480, 4.5, tw, '~5 H'], [760, 8.3, t8, '8 H+']].forEach(([x, hr, ts, txt], i) => {
        ctx.save(); ctx.translate(x, 210); ctx.rotate(i === 1 ? wob : 0); ctx.translate(-x, -210);
        const fill = t > ts ? lerp(0, hr, EASE.io(clamp((t - ts) / 0.8, 0, 1))) : (i === 1 ? 4.5 : 0);
        clockFace(x, 210 - bounce(t, ts), 95, fill, 4610 + i * 10, { wedge: [0, fill, i === 1 ? YEL : i === 0 ? PAPER : RED], hand: INK });
        ctx.restore();
        if (t > ts || i === 1) label(txt, x, 345, 26, { seed: 4640 + i, fill: i === 1 ? YEL : PAPER });
      });
      popLabel(t, t2 + 0.2, 'SOME PEOPLE', 200, 400, 18, { seed: 4650 });
      popLabel(t, t8 + 0.2, 'OTHERS', 760, 400, 18, { seed: 4655 });
    },
  });
}

// 7. "Your speed depends on things like your genes, your age, whether you smoke, and even your diet."  The liver at a panel of dials.
{
  const t0 = at('Your speed'), words = [['genes', 'GENES'], ['your age', 'AGE'], ['smoke', 'SMOKING'], ['diet', 'DIET']];
  const liv = [{ t: t0, x: 170, y: 443, size: 1.2, expr: 'thinking', look: [4, -1] }];
  words.forEach(([w], i) => { const tw = at(w, 1); liv.push({ t: tw - 0.15, aR: 1.6, bend: 0.1, reach: 1, x: 170 + i * 4, ease: 'out' }, { t: tw + 0.3, arms: 'down', ease: 'io' }); cue(tw, 'tick', 0.7); });
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      workshop(t, 4 + lt * 0.2, { cx: 120, cy: 90, r: 40 });
      shape(boxPts(300, 150, 600, 250, 4710), PAPER, 4, 4710, 1);
      words.forEach(([w, txt], i) => {
        const x = 375 + i * 150, y = 250, tw = at(w, 1), a = t > tw ? -0.6 + Math.sin(t * 3 + i) * 0.4 : -2.4;
        shape(blobPts(x, y, 46, 46, 4720 + i, 12, 0.02), i % 2 ? YEL : BLUE, 3.4, 4720 + i, 1);
        line([[x, y], [x + Math.cos(a) * 36, y + Math.sin(a) * 36]], 5, 4730 + i, INK, 0.6, false);
        if (t > tw) label(txt, x, 345, 18, { seed: 4740 + i, fill: YEL });
      });
      drawChar(LIV, poseAt(liv, t));
    },
  });
}

// 8. "Pregnancy and some medicines can slow it down too. If that's you, the person to ask is your doctor, not a cartoon bean."
{
  const t0 = at('Pregnancy'), ts = at('slow it down'), ty = at("If that's you"), tc = at('cartoon bean');
  const liv = [{ t: t0, x: 260, y: 443, size: 1.2, expr: 'neutral', look: [3, -2] }, { t: ts, expr: 'sleepy', sy: 0.94, ease: 'io' }, { t: ty + 0.2, look: [0, 0], eyes: 'half', mouth: 'flat', sy: 1, ease: 'hold' }];
  const caf = [{ t: t0, x: 480, y: 443, size: 1.2, expr: 'smug', look: [-3, -1] }, { t: ty + 0.3, look: [0, 0], eyes: 'half', mouth: 'flat', ease: 'hold' }];
  const you = [{ t: t0, x: 700, y: 443, size: 1.1, expr: 'curious', look: [-3, -1] }, { t: ty + 0.4, look: [0, 0], eyes: 'half', mouth: 'flat', ease: 'hold' }];
  cue(tc, 'ding', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: ty - t0, z: 1 }, { t: ty - t0 + 0.3, z: 1.08, y: 300, ease: 'hold' }],
    draw(lt, t) {
      workshop(t, 5 + lt * 0.1, { cx: 820, cy: 100, r: 44 });
      popLabel(t, t0 + 0.05, 'PREGNANCY', 290, 120, 24, { seed: 4810, fill: YEL, rot: -0.04 });
      popLabel(t, at('some medicines'), 'SOME MEDICINES', 560, 120, 24, { seed: 4815, fill: YEL, rot: 0.03 });
      if (t > ts && t < ty) { const x = 200 + (t - ts) * 25; shape(blobPts(x, 430, 22, 10, 4820, 8), PAPER, 3, 4820, 1); shape(blobPts(x + 2, 412, 13, 13, 4821, 9), YEL, 3, 4821, 1); }
      drawChar(LIV, poseAt(liv, t)); drawChar(CAF, poseAt(caf, t)); drawChar(YOU, poseAt(you, t));
      popLabel(t, at('your doctor') - 0.05, 'ASK YOUR DOCTOR', 480, 200, 30, { seed: 4830, fill: PAPER });
    },
  });
}

// 9. "Either way, caffeine never leaves all at once. After one half-life, half of it is gone. After another, half of what's left."  8, 4, 2.
{
  const t0 = at('Either way'), t1 = at('half of it is gone'), t2 = at("half of what's left");
  const xs = [130, 220, 310, 400, 560, 650, 740, 830];
  for (let i = 0; i < 4; i++) cue(t1 + i * 0.1, 'pop', 0.6);
  cue(t2, 'pop', 0.7); cue(t2 + 0.1, 'pop', 0.7);
  const gone = i => i >= 4 ? t1 + (i - 4) * 0.1 : i >= 2 ? t2 + (i - 2) * 0.1 : Infinity;
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 4901, { grass: false });
      clockFace(480, 120, 60, t < t1 ? 0 : t < t2 ? 5 : 10, 4910, { wedge: [0, t < t1 ? 0 : t < t2 ? 5 : 10, YEL] });
      cafRow(t, xs, 443, gone, 4920, [0, -2]);
      const n = t < t1 ? 8 : t < t2 ? 4 : 2;
      label(String(n), 820, 120, 54, { seed: 4930 + n, fill: PAPER });
      if (t > t1) popLabel(t, t1 + 0.1, '1 HALF-LIFE', 170, 120, 22, { seed: 4940, fill: YEL });
      if (t > t2) popLabel(t, t2 + 0.1, '2 HALF-LIVES', 170, 170, 22, { seed: 4945, fill: YEL });
    },
  });
}

// 10. "It leaves the way a guest leaves a party: slowly, and saying goodbye several times."  Caffeine in the doorway, waving, again.
{
  const t0 = at('It leaves the way'), tg = at('goodbye');
  const caf = [{ t: t0, x: 620, y: 443, size: 1.4, expr: 'happy', look: [-3, 0] }];
  [0, 1.1, 2.2, 3.3].forEach((d, k) => { const tw = t0 + 0.6 + d; caf.push(...A.wave(tw, tw + 0.7, 'R'), { t: tw + 0.75, x: 620 + (k % 2 ? 25 : -10), ease: 'io' }); });
  const liv = [{ t: t0, x: 250, y: 443, size: 1.2, expr: 'neutral', look: [4, 0] }, ...A.sigh(tg + 0.2), { t: tg + 1.2, arms: 'hips', expr: 'angry', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: RED });
      [[60, 40, 260, 70, RED], [300, 60, 520, 40, BLUE], [560, 40, 900, 75, RED]].forEach(([x0, y0, x1, y1, c], i) => tube(wavePts(x0, y0, x1, y1, 2, 10), 6, c, 4990 + i));
      doorway(640, 443, 150, 260, 4995, INK);
      drawChar(CAF, poseAt(caf, t));
      drawChar(LIV, poseAt(liv, t));
      popLabel(t, t0 + 0.4, 'BYE!', 700, 140, 28, { seed: 4998, fill: PAPER, rot: 0.06 });
      if (t > t0 + 2) popLabel(t, t0 + 2, 'BYE!!', 760, 190, 24, { seed: 4999, fill: PAPER, rot: -0.05 });
    },
  });
}
