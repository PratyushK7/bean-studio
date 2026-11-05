// CHAPTER 3: "How caffeine blocks tiredness" (script lines 25 to 42). The trick: caffeine sits in the slot; the letters pile up.

musicMood(at('Enter caffeine') - 0.3, 'playful');      // a mistake being made, with a grin
musicMood(at('Meanwhile') - 0.2, 'tense');             // the pile grows
musicMood(at('And everything on hold') - 0.15, 'silent');   // the punchline lands on nothing

// the doorstep: a red wall with a door, a paper step, and the mailbox by the door
function doorstep(t) {
  paper(RED);
  doorway(150, 430, 150, 290, 3001, BLUE);
  fillOnly(blobPts(200, 300, 7, 7, 3002, 6), YEL, 3002);
  ground(430, 3003, { fill: PAPER, grass: false });
  return 430;
}
// a tiny double-ring "molecule shape" (a hexagon joined to a pentagon), the shape both beans share
function ringShape(x, y, r, seed, color = INK) {
  const hex = Array.from({ length: 6 }, (_, i) => [x + Math.cos(i / 6 * TAU) * r, y + Math.sin(i / 6 * TAU) * r]);
  shape(hex, null, 3.4, seed, 0.8, 2);
  const cx = x + r * 1.75, pen = Array.from({ length: 5 }, (_, i) => [cx + Math.cos(Math.PI + i / 5 * TAU) * r * 0.9, y + Math.sin(Math.PI + i / 5 * TAU) * r * 0.9]);
  shape(pen, null, 3.4, seed + 1, 0.8, 2);
}

// 1. "Enter caffeine. About fifteen to thirty minutes after your first sip, it starts to kick in."  A stage entrance.
{
  const t0 = at('Enter caffeine'), tl = t0 + 0.55, tk = at('kick in');
  const caf = [
    { t: t0, size: 2.0, look: [0, 1] },
    ...dropIn(tl, 480, 432, { expr: 'smug' }),
    { t: tl + 0.5, lean: 0.25, sy: 0.9, eyes: 'happy', mouth: 'grin', arms: 'out', ease: 'io' },
    { t: tl + 1.3, lean: 0, sy: 1, arms: 'hips', expr: 'smug', ease: 'io' },
    ...A.cheer(tk - 0.3, 432, { height: 40 }),
    { t: tk + 0.6, arms: 'hips', expr: 'smug', ease: 'hold' },
  ];
  cue(t0, 'drum', 0.9);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.05, y: 285 }, { t: 5, z: 1, y: 270 }],
    draw(lt, t) {
      setStage(t, { wall: BLUE });
      drawChar(CAF, poseAt(caf, t));
      popLabel(t, tl + 0.3, 'CAFFEINE', 480, 110, 34, { seed: 3110, fill: YEL });
      popLabel(t, at('fifteen'), '15 TO 30 MIN', 760, 200, 24, { seed: 3115, rot: 0.04 });
    },
  });
}

// 2. "Caffeine happens to be shaped a lot like adenosine."  Same ring shape on both their cards.
{
  const t0 = at('Caffeine happens'), tl = at('a lot like');
  const caf = [{ t: t0, x: 300, y: 432, size: 1.45, expr: 'smug', look: [4, 0] }, { t: tl, arms: 'pointR', ease: 'back' }];
  const ado = [{ t: t0, x: 680, y: 432, size: 1.3, expr: 'sleepy', look: [-4, 0] }, { t: tl + 0.4, expr: 'surprised', ease: 'hold' }, { t: tl + 1.2, expr: 'sleepy', ease: 'hold' }];
  cue(tl, 'pop');
  shot(t0, {
    draw(lt, t) {
      setStage(t, { wall: YEL });
      drawChar(CAF, poseAt(caf, t));
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      shape(boxPts(225, 70, 150, 90, 3201), PAPER, 3.4, 3201, 1); ringShape(270, 115, 22, 3205, INK);
      shape(boxPts(605, 70, 150, 90, 3211), PAPER, 3.4, 3211, 1); ringShape(650, 115, 22, 3215, INK);
      if (t > tl) { line(wavePts(455, 106, 525, 106, 1.5, 6), 6, 3220); line(wavePts(455, 130, 525, 130, 1.5, 6), 6, 3221); }
    },
  });
}

// 3. "Close enough to slide right into the mailbox slot. But it isn't a letter, so it doesn't deliver anything. It just sits there, wearing a sign that says closed."
{
  const t0 = at('Close enough'), ts = at('slide right') - 0.2, tn = at("isn't a letter"), tc = at('says closed');
  const S = 2.2, SX = 470, SY = 432 - 70 * S - 56 * S + 4 * S, k = 0.45, tot = S * k;
  const land = ts + 6 * D + 2 * D + 10 * D;
  const caf = [
    { t: t0, x: 800, y: 432, size: tot / CAF.size, expr: 'smug', look: [-4, -2] },
    ...A.jump(ts, [800, 432], [SX, SY + CAF.h * tot * 0.42], { height: 120, upExpr: 'happy', endExpr: 'smug' }),
  ];
  const inslot = [
    { t: t0, expr: 'smug', look: [3, 0] },
    ...A.shake(tn, 2),
    { t: tc - 0.2, expr: 'smug', look: [0, 0], ease: 'hold' },
  ];
  cue(land, 'zip'); cue(tc, 'pop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, x: 480, y: 270 }, { t: 8, z: 1.08, x: 470, y: 240 }],
    draw(lt, t) {
      setStage(t, { wall: BLUE });
      const slot = mailbox(SX, 432, S, 3310, { face: t > land ? 'o' : 'smile' });
      if (t < land) drawChar(CAF, poseAt(caf, t), { shadow: t < ts + 6 * D });
      else cafInSlot(slot, inslot, t, { k, sign: t > tc, swing: t < tc + 0.6 });
      if (t > tn && t < tc) { letter(700, 230, 1.6, 0.2, 3320, { face: 'o' }); line([[650, 190], [750, 270]], 7, 3321, RED); line([[650, 270], [750, 190]], 7, 3322, RED); }
    },
  });
}

// 4. "Now the tiredness letters arrive and find the slot taken. They can't get in, so your brain never gets the message that you're tired."
{
  const t0 = at('Now the tiredness'), tf = at('slot taken'), tc = at("can't get in");
  const ado = [
    { t: t0, x: 120, y: 430, size: 1.15, expr: 'sleepy' },
    ...A.walk(t0 + 0.1, 120, 330, 430, { speed: 150 }),
    { t: tf - 0.2, aR: 2.0, bend: 0.2, reach: 1, ease: 'out' },
    { t: tf + 0.2, aR: 2.1, ease: 'hold' }, { t: tf + 0.4, aR: 1.9, ease: 'hold' }, { t: tf + 0.6, aR: 2.1, ease: 'hold' },
    { t: tc + 0.2, arms: 'down', expr: 'sad', look: [3, -2], ease: 'io' },
  ];
  const caf = [{ t: t0, expr: 'smug', look: [-4, 0] }, { t: tf, eyes: 'squint', mouth: 'grit', ease: 'hold' }, { t: tc + 0.3, expr: 'smug', look: [-3, 1], ease: 'hold' }];
  cue(tf + 0.2, 'boing', 0.5); cue(tf + 0.6, 'boing', 0.5);
  shot(t0, {
    draw(lt, t) {
      doorstep(t);
      const slot = mailbox(560, 430, 1.7, 3410, { face: 'smile' });
      cafInSlot(slot, caf, t);
      let hand = [0, 0];
      drawChar(ADO, poseAt(ado, t), { hold: (h, P, A2) => { hand = h[1]; mailBag()(h, P, A2); } });
      if (t > tf - 0.2 && t < tc + 0.2) letter(Math.min(hand[0] + 20, slot.x - 50), Math.max(hand[1] - 10, slot.y - 10), 1.1, -0.3, 3420, { face: 'frown' });
      if (t > tc) { letter(380, 418, 1.1, 0.1, 3421, { face: 'frown' }); }
    },
  });
}

// 5. "It checks the mailbox, finds nothing new, and decides you must be fine."  Inside: the brain at its desk, an empty in-tray.
{
  const t0 = at('It checks'), tn = at('nothing new'), tf = at('must be fine');
  cue(tn, 'tick', 0.6); cue(tf, 'thud', 0.8);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 4.4, z: 1.04 }],
    draw(lt, t) {
      setDesk(t, { wall: PAPER, chart: false });
      brain(380, 318, 150, 105, 3510);
      miniFace(385, 335, 4.2, 0, 3511, t > tn && t < tf ? 'o' : 'smile', [t < tn ? 3 * Math.sin(t * 6) : 0, 2]);
      shape(boxPts(560, 360, 150, 50, 3520), BLUE, 3.4, 3520, 1);
      ink('IN', 635, 386, 20, PAPER, 3521);
      popLabel(t, tn, 'NEW MAIL: 0', 640, 300, 22, { seed: 3530, rot: -0.03 });
      if (t > tf) { ctx.save(); ctx.translate(380, 120); ctx.rotate(-0.12); label('ALL FINE', 0, 0, 34, { seed: 3540, fill: YEL }); ctx.restore(); }
    },
  });
}

// 6. "That's the whole trick. Caffeine doesn't hand you fuel; a cup of black coffee has about two calories."  The mug, 2 CAL.
{
  const t0 = at("That's the whole"), tf = at('fuel'), tc = at('two calories');
  const caf = [{ t: t0, x: 700, y: 443, size: 1.35, expr: 'smug', arms: 'hips' }, ...A.shrug(tf - 0.1, { hold: 1.0, after: 'smirk' }), { t: tc, arms: 'pointL', expr: 'happy', ease: 'back' }];
  cue(tc, 'pop');
  shot(t0, {
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 3601, { grass: false });
      mug(330, 430, 4.2, 3610, { steam: true, face: 'smile' });
      popLabel(t, tc - 0.05, '2 CAL', 330, 190, 40, { seed: 3620, fill: PAPER, rot: -0.05 });
      if (t > tf && t < tc) { ink('FUEL?', 700, 210, 30, INK, 3630, 0.04); }
      drawChar(CAF, poseAt(caf, t));
    },
  });
}

// 7. "It just stops your brain from reading the bad news. At everyday doses, blocking adenosine is the main thing caffeine does in your brain."
{
  const t0 = at('It just stops'), tb = at('bad news'), te = at('everyday doses');
  const caf = [
    { t: t0, x: 640, y: 443, size: 1.3, expr: 'smug', look: [-4, -1] },
    { t: tb - 0.3, arms: 'up', ease: 'back' },
    { t: te + 0.4, arms: 'hips', expr: 'smug', ease: 'io' },
  ];
  cue(tb, 'whoosh', 0.5);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, RED); ground(443, 3701, { grass: false });
      brain(330, 270, 170, 125, 3710);
      miniFace(345, 300, 3.6, 0, 3711, 'smile', [3, 0]);
      letter(330, 150, 2.6, -0.08, 3712, { word: 'TIRED', face: false });
      if (t > tb) { shape(boxPts(220, 110, 220, 80, 3720, -0.06), YEL, 3.6, 3720, 1); ink('CLOSED', 330, 150, 34, INK, 3721, -0.06); }
      drawChar(CAF, poseAt(caf, t));
      popLabel(t, te + 0.5, 'MAIN JOB: BLOCKING', 660, 120, 22, { seed: 3730, rot: 0.03 });
    },
  });
}

// 8. "Meanwhile, you're still awake, so adenosine keeps being made. The mail carrier knocks, waits, and leaves another letter on the step."
{
  const t0 = at('Meanwhile'), tk = at('knocks'), tw = at('waits'), tl = at('leaves another');
  const ado = [
    { t: t0, x: -60, y: 430, size: 1.15, expr: 'sleepy' },
    ...A.walk(t0 + 0.2, -60, 350, 430, { speed: 140 }),
    { t: tk - 0.15, aR: 2.4, bend: -0.6, reach: 0.9, ease: 'out' }, { t: tk + 0.1, aR: 1.9, ease: 'hold' }, { t: tk + 0.25, aR: 2.4, ease: 'hold' }, { t: tk + 0.4, aR: 1.9, ease: 'hold' },
    { t: tw - 0.1, arms: 'down', look: [0, 0], eyes: 'half', mouth: 'flat', ease: 'hold' },
    { t: tl, sy: 0.85, sx: 1.1, aR: 0.9, ease: 'io' }, { t: tl + 0.5, sy: 1, sx: 1, arms: 'down', look: [-3, 0], ease: 'io' },
  ];
  cue(tk + 0.1, 'thud', 0.6); cue(tk + 0.4, 'thud', 0.6); cue(tl + 0.35, 'plop');
  const caf = [{ t: t0, expr: 'smug', look: [-4, 0] }, { t: tw, eyes: 'closed', mouth: 'smirk', ease: 'hold' }];
  shot(t0, {
    cam: [{ t: 0, x: 480, z: 1 }, { t: 7, x: 450, z: 1.03 }],
    draw(lt, t) {
      doorstep(t);
      const slot = mailbox(560, 430, 1.7, 3410, { face: 'smile' });
      cafInSlot(slot, caf, t);
      letterPile(470, 430, t > tl + 0.35 ? 3 : 2, 3810, 1.0);
      drawChar(ADO, poseAt(ado, t), { hold: mailBag(t < tl + 0.3) });
    },
  });
}

// 9. "The letters don't vanish; they stack up outside the door. Caffeine doesn't cancel your tiredness, it puts it on hold."  The pile climbs.
{
  const t0 = at("The letters don't"), th = at('on hold', 1);
  const ado = [{ t: t0, x: 300, y: 430, size: 1.15, expr: 'sleepy' }];
  for (let k = 0, tk = t0 + 0.3; tk < at('And everything on hold') - 0.3; k++, tk += 0.45) ado.push({ t: tk, aR: 2.3, bend: 0.2, ease: 'hold' }, { t: tk + 0.15, aR: 0.6, ease: 'hold' });
  const caf = [{ t: t0, expr: 'smug', look: [-4, -2] }, { t: th, look: [-3, -4], ease: 'hold' }];
  for (let k = 0; k < 10; k++) cue(t0 + 0.45 + k * 0.6, 'plop', 0.45);
  shot(t0, {
    tr: 'cut',
    draw(lt, t) {
      doorstep(t);
      const slot = mailbox(600, 430, 1.7, 3410, { face: 'o' });
      cafInSlot(slot, caf, t);
      const n = 3 + Math.floor(clamp((t - t0) / 0.18, 0, 40));
      letterPile(450, 430, n, 3910, 1.0);
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      popLabel(t, th - 0.05, 'ON HOLD', 450, 120, 30, { seed: 3920, fill: YEL, rot: -0.04 });
    },
  });
}

// 10. "And everything on hold gets delivered eventually."  Silence. The pile towers over the mailbox; caffeine looks up.
{
  const t0 = at('And everything on hold'), te = at('eventually');
  const caf = [{ t: t0, expr: 'smug', look: [-2, -4] }, ...A.take(te - 0.1, { hold: 0.6, mouth: 'wavy' }), { t: te + 0.8, expr: 'scared', look: [-2, -4], ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, x: 520, y: 270, z: 1 }, { t: 3, x: 540, y: 240, z: 1.1 }],
    draw(lt, t) {
      doorstep(t);
      const slot = mailbox(640, 430, 1.7, 3410, { face: 'o' });
      ctx.save(); ctx.translate(470, 430); ctx.rotate(Math.sin(t * 3) * 0.02); ctx.translate(-470, -430);
      letterPile(470, 430, 90, 3910, 1.35);
      ctx.restore();
      cafInSlot(slot, caf, t);
    },
  });
}
