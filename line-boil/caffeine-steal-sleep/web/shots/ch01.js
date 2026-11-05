// CHAPTER 1: "A coffee you can't feel" (script lines 0 to 11). The hook, the turn, and what the video will do.

musicMood(0, 'mystery');                         // the hook is a puzzle
musicMood(at("Here's the thing") - 0.2, 'curious');   // the turn: now we explain

// 1. "Why does a 3 p.m. coffee still cost you sleep at midnight, when you feel completely fine?"  YOU sips at the office; the clock jumps to midnight.
{
  const tm = at('midnight', 1), tf = at('completely fine');
  const you = [
    { t: 0, x: 430, y: 421, size: 1.1, arms: 'hold', expr: 'neutral', look: [3, -1] },
    { t: at('coffee', 1) - 0.1, aR: 1.55, bend: 1.4, eyes: 'happy', mouth: 'smile', ease: 'out' },
    { t: tm - 0.15, arms: 'hold', expr: 'curious', look: [4, -3] },
    { t: tf - 0.1, expr: 'happy', look: [1, 0] },
    { t: tf + 0.3, arms: 'hips', ease: 'back' },
  ];
  cue(0.05, 'tick', 0.5); cue(tm, 'slide_up', 0.6);
  shot(0, {
    cam: [{ t: 0, z: 1, x: 480, y: 270 }, { t: 5.5, z: 1.05, x: 500, y: 262 }],
    draw(lt, t) {
      setDesk(t, { wall: YEL });
      clockFace(780, 118, 46, hourAt(t, tm, 3, 12), 1101);
      popLabel(t, at('3 p.m.'), t < tm ? '3PM' : 'MIDNIGHT', 780, 196, 22, { seed: 1105, rot: -0.03 });
      drawChar(YOU, poseAt(you, t), { hold: h => mug(h[1][0] + 4, h[1][1] + 16, 0.78, 1110, { steam: true }) });
    },
  });
}

// 2. "You drank it hours ago. The mug is already washed and back in the cupboard."  The clean mug, smug on its shelf.
{
  const t0 = at('You drank'), tw = at('washed');
  const you = [
    { t: t0, x: 300, y: 443, size: 1.1, expr: 'neutral', look: [3, -2] },
    ...A.point(tw - 0.35, 'R', { ang: 2.25, after: 'smile', hold: 1.1 }),
    { t: at('cupboard'), expr: 'smug', look: [3, -3], ease: 'hold' },
  ];
  cue(tw + 0.1, 'sparkle');
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: BLUE });
      clockFace(560, 92, 34, hourAt(t, at('hours ago'), 3, 6.5), 1201);
      shelf(540, 235, 200, 1210);
      mug(500, 235, 0.95, 1220, { face: t > tw ? 'happy' : 'sleepy' });
      mug(585, 235, 0.95, 1225, { color: BLUE });
      if (t > tw && t < tw + 1.4) { plus(470, 175, 8, 1240); plus(530, 165, 5, 1241); plus(515, 200, 4, 1242); }
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 3. "You don't feel wired, you climb into bed on time, and you drift off more or less as usual."  Bedtime, no drama.
{
  const t0 = at("You don't feel"), tc = at('climb'), td = at('drift');
  const stand = [
    { t: t0, x: 330, y: 443, size: 1.05, expr: 'neutral', look: [3, 0] },
    ...A.shake(at('wired') - 0.1, 1),
    { t: tc - 0.4, expr: 'sleepy', ease: 'hold' },
  ];
  const lie = [
    { t: tc, x: 690, y: 372, size: 0.95, expr: 'sleepy', look: [0, -2], breathe: 2 },
    { t: td, eyes: 'closed', mouth: 'smile', ease: 'hold' },
  ];
  cue(tc + 0.05, 'plop'); cue(td + 0.3, 'slide_down', 0.4);
  shot(t0, {
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: YEL }); nightWindow(t);
      const top = bed(640, 443, 290, 1301);
      if (t < tc) drawChar(YOU, poseAt(stand, t));
      else { drawLying(YOU, poseAt(lie, t), { tilt: 0.25 }); blanket(632, 785, top, 1310, RED); }
      if (t > td) zzz(585, 292, t, 1320);
    },
  });
}

// 4. "In the morning, you'd swear you slept fine. But a sleep monitor might disagree."  YOU stretches; the monitor frowns.
{
  const t0 = at('In the morning'), tdis = at('disagree');
  const you = [
    { t: t0, x: 580, y: 384, size: 1.0, expr: 'sleepy', arms: 'down', look: [0, -2] },
    { t: at('swear', 1) - 0.2, arms: 'up', expr: 'happy', ease: 'back' },
    { t: at('slept fine', 1) + 0.3, arms: 'down', expr: 'smug', ease: 'io' },
    ...A.take(at('monitor') - 0.05, { hold: 0.5, mouth: 'wavy' }),
    { t: tdis, look: [4, -1], expr: 'curious', ease: 'hold' },
  ];
  cue(tdis, 'tick', 0.8); cue(tdis + 0.25, 'tick', 0.8); cue(tdis + 0.5, 'tick', 0.8);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: BLUE });
      const top = bed(640, 443, 290, 1401);
      drawChar(YOU, poseAt(you, t));
      blanket(505, 785, top, 1410, RED);
      shape(boxPts(785, 318, 110, 14, 1420), RED, 3.2, 1420, 1);
      line([[800, 332], [800, 443]], 4, 1421); line([[880, 332], [880, 443]], 4, 1422);
      monitor(840, 262, 120, 84, t, 1430, { face: t > tdis ? 'frown' : 'smile', screen: t > tdis ? RED : BLUE });
    },
  });
}

// 5. "Here's the thing most people get backwards: caffeine doesn't actually give you energy."  Caffeine hops out of the mug; ENERGY gets crossed out.
{
  const t0 = at("Here's the thing"), tj = at("caffeine doesn't", 1) - 0.5, te = at('energy', 1);
  const you = [
    { t: t0, x: 240, y: 443, size: 1.15, arms: 'hold', expr: 'neutral', look: [3, -1] },
    { t: at('backwards') - 0.1, expr: 'curious', look: [3, 2] },
    ...A.take(tj + 0.5, { hold: 0.7, arms: 'hold', mouth: 'o' }),
    { t: te + 0.4, expr: 'sad', look: [4, -3], arms: 'hold', ease: 'hold' },
  ];
  const caf = [
    { t: t0, x: 300, y: 382, hide: true, expr: 'smug' },
    { t: tj, hide: false, ease: 'hold' },
    ...A.jump(tj, [300, 382], [600, 443], { height: 170, upExpr: 'happy', endExpr: 'smug' }),
    ...A.shrug(at('actually give') - 0.1, { hold: 1.2, after: 'smirk' }),
  ];
  cue(te + 0.35, 'thud');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5, z: 1.04 }],
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 1501, { grass: false });
      popLabel(t, te - 0.1, 'ENERGY', 600, 190, 34, { seed: 1510, rot: -0.04 });
      if (t > te + 0.35) { line([[515, 160], [690, 222]], 9, 1520, RED, 1); line([[515, 222], [690, 160]], 9, 1521, RED, 1); }
      drawChar(YOU, poseAt(you, t), { hold: h => mug(h[1][0] + 4, h[1][1] + 16, 0.82, 1530, { steam: t < tj }) });
      drawChar(CAF, poseAt(caf, t));
    },
  });
}

// 6. "It blocks the message that says you're tired. And that message doesn't go away just because you stopped hearing it."
{
  const t0 = at('It blocks'), tb = at('message', 1) + 0.1, tm = at('And that message'), th = at('stopped hearing');
  const caf = [{ t: t0, expr: 'smug', look: [-4, 0] }, ...A.take(tb - 0.1, { hold: 0.3, mouth: 'smirk' }), { t: tb + 0.6, expr: 'smug', look: [-4, 1] }];
  const you = [
    { t: t0, x: 830, y: 443, size: 0.8, expr: 'neutral', look: [-3, 0] },
    { t: th - 0.25, aL: -2.75, aR: 2.75, bend: 2.1, reach: 0.6, eyes: 'closed', mouth: 'flat', ease: 'back' },
  ];
  cue(tb, 'boing'); cue(tb + 0.55, 'plop');
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 1601, { grass: false });
      const slot = mailbox(470, 443, 2.0, 1610, { face: 'smile' });
      cafInSlot(slot, caf, t, { k: 0.45 });
      // the letter flies in, bounces off the closed slot, lands, and waits
      let lx, ly, lr = 0;
      if (t < tb) { const u = clamp((t - t0) / (tb - t0), 0, 1); lx = lerp(-40, 400, u); ly = lerp(160, slot.y - 30, u) - 60 * 4 * u * (1 - u); lr = -0.2; }
      else { const u = clamp((t - tb) / 0.55, 0, 1); lx = lerp(400, 270, u); ly = lerp(slot.y - 30, 428, u) - 70 * 4 * u * (1 - u); lr = u < 1 ? u * 6 : 0; }
      letter(lx, ly, 1.5, lr, 1620, { face: t > tm ? 'frown' : t > tb ? 'o' : 'sleepy' });
      if (t > tb && t < tb + 0.25) burst(410, slot.y - 20, 18, 34, 1630, 0);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 7. "In this video we'll meet the messenger, the bean that blocks it, and the clock that decides how long it stays blocked."  A police line-up.
{
  const t0 = at('In this video'), ta = at('messenger'), tc = at('bean that blocks'), tl = at('clock that decides');
  const ado = [{ t: t0, size: 1.5 }, ...dropIn(ta, 210, 430, { expr: 'sleepy' }), { t: ta + 0.6, eyes: 'half', mouth: 'flat', look: [2, 1], ease: 'hold' }];
  const caf = [{ t: t0, size: 1.6 }, ...dropIn(tc, 480, 430, { expr: 'smug' }), { t: tc + 0.5, look: [-3, 0], ease: 'hold' }];
  const liv = [{ t: t0, size: 1.4 }, ...dropIn(tl, 750, 430, { expr: 'neutral' }), ...A.nod(tl + 0.5, 2)];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      paper(PAPER);
      for (let k = 0; k < 5; k++) { const y = 110 + k * 64; line([[24, y], [936, y + 2]], 2.2, 1701 + k, INK, 0.8, false); ink(String(7 - k), 46, y - 14, 18, INK, 1710 + k); }
      ground(430, 1720, { fill: BLUE, grass: false });
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      drawChar(CAF, poseAt(caf, t), { hold: (h, P) => closedSign(P.x, P.y - 112, 1.1, 1730, 0.04) });
      drawChar(LIV, poseAt(liv, t), { hold: h => clockFace(h[1][0] + 16, h[1][1] - 6, 21, 3 + t * 0.4, 1740) });
      popLabel(t, ta + 0.25, 'THE MESSENGER', 210, 486, 20, { seed: 1750, fill: YEL });
      popLabel(t, tc + 0.25, 'THE BLOCKER', 480, 486, 20, { seed: 1755, fill: YEL });
      popLabel(t, tl + 0.25, 'THE CLOCK', 750, 486, 20, { seed: 1760, fill: YEL });
    },
  });
}

// 8. "So let's follow the message, from the moment it's written to the moment it finally gets delivered."
{
  const t0 = at("So let's follow"), tw = at('written'), td = at('finally gets');
  const ado = [
    { t: t0, x: 230, y: 430, expr: 'sleepy', look: [2, 1] },
    { t: tw, arms: 'hold', eyes: 'half', mouth: 'smile', ease: 'hold' },
    ...A.walk(td - 0.6, 230, 560, 430, { speed: 160 }),
    { t: td + 1.6, expr: 'sleepy', ease: 'hold' },
  ];
  cue(tw, 'pop');
  shot(t0, {
    cam: [{ t: 0, x: 480, z: 1 }, { t: 6, x: 520, z: 1.03 }],
    draw(lt, t) {
      setBlank(t, RED); ground(430, 1801, { grass: false });
      mailbox(760, 430, 1.4, 1810, { face: 'smile', flag: false });
      drawChar(ADO, poseAt(ado, t), { hold: mailBag(t > tw) });
      if (t > tw && t < tw + 0.3) burst(330, 300, 16, 30, 1820, 0);
    },
  });
}

// 9. "For a 3 p.m. coffee, that can be well after you've gone to bed."  Night. The carrier waits; the slot is still closed.
{
  const t0 = at('For a 3', 1), tw = at('well after');
  const ado = [
    { t: t0, x: 360, y: 432, expr: 'sleepy', arms: 'hold', look: [3, -1] },
    { t: tw, sy: 0.82, sx: 1.12, eyes: 'half', mouth: 'sigh', fx: 'zzz', ease: 'io' },
  ];
  const caf = [{ t: t0, expr: 'smug', look: [-4, 0] }];
  cue(tw, 'deflate', 0.5);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      midnightSky(t, 620, 190, 100);
      clockFace(150, 110, 40, hourAt(t, tw - 0.3, 3, 11.95, 1.2), 1901);
      const slot = mailbox(620, 432, 1.6, 1910, { face: 'sleepy' });
      cafInSlot(slot, caf, t, { k: 0.45 });
      drawChar(ADO, poseAt(ado, t), { hold: mailBag(true) });
    },
  });
}
