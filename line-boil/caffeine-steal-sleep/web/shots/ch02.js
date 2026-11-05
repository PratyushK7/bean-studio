// CHAPTER 2: "Where tiredness comes from" (script lines 12 to 24). Adenosine as the mail carrier; receptors as mailboxes; sleep pressure.

musicMood(at('Every hour') - 0.2, 'curious');
musicMood(at('That heavy') - 0.2, 'calm');

// a letter tossed along an arc from a to b, between t0 and t0 + dur
function tossLetter(t, t0, a, b, seed, s = 1, dur = 0.45, arc = 60) {
  const u = (t - t0) / dur;
  if (u < 0 || u > 1) return;
  letter(lerp(a[0], b[0], u), lerp(a[1], b[1], u) - arc * 4 * u * (1 - u), s * (1 - 0.3 * u), u * 4, seed);
}
// the mail carrier with his bag; returns the right hand so a toss can start from it
function drawCarrier(P, withLetter) {
  let hand = [P.x, P.y - 60];
  const bag = mailBag(withLetter);
  drawChar(ADO, P, { hold: (h, P2, A2) => { hand = h[1]; bag(h, P2, A2); } });
  return hand;
}

// 1. "Every hour you're awake, your brain cells burn through energy, and one of the leftovers is a molecule called adenosine."
{
  const t0 = at('Every hour'), tm = at('molecule') - 0.4;
  const ado = [
    { t: t0, x: 470, y: 200, hide: true, expr: 'sleepy' },
    { t: tm, hide: false, ease: 'hold' },
    ...A.jump(tm, [470, 200], [740, 443], { height: 120, upExpr: 'surprised', endExpr: 'sleepy' }),
    { t: at('adenosine', 1) + 0.3, eyes: 'half', mouth: 'flat', look: [-3, -1], ease: 'hold' },
  ];
  cue(at('burn'), 'sparkle', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1.04 }, { t: 7, z: 1 }],
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 2101, { grass: false });
      brain(320, 250, 190, 135, 2110);
      if (t > at('burn') - 0.2) for (let i = 0; i < 6; i++) {
        const on = (Math.floor(t * 6) + i) % 3 === 0, x = 200 + rnd(2120, i) * 240, y = 170 + rnd(2121, i) * 160;
        if (on) burst(x, y, 6, 16, 2130 + i, 0, 6);
      }
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      popLabel(t, at('adenosine', 1) - 0.05, 'ADENOSINE', 740, 150, 34, { seed: 2140, fill: YEL, rot: 0.03 });
    },
  });
}

// 2. "Think of adenosine as a mail carrier with one letter to deliver, over and over."  He walks the lane of mailboxes.
{
  const t0 = at('Think of'), tw = at('mail carrier', 1);
  const ado = [{ t: t0, x: 150, y: 432, expr: 'sleepy', facing: 1 }, ...A.walk(tw - 0.2, 150, 640, 432, { speed: 120 }), { t: at('over and over') + 0.3, expr: 'sleepy', eyes: 'half', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, x: 430, z: 1.02 }, { t: 5, x: 540, z: 1.02 }],
    draw(lt, t) {
      setSunny(t);
      [300, 520, 740, 900].forEach((x, i) => mailbox(x, 432, 0.95, 2210 + i * 10, { face: 'smile', flag: false }));
      drawCarrier(poseAt(ado, t), true);
    },
  });
}

// 3. "The letter says one word: tired. No return address, no small talk."  A close-up of the letter, then the deadpan.
{
  const t0 = at('The letter says'), tt = at('tired', 1), tn = at('No return');
  const ado = [
    { t: t0, x: 300, y: 470, size: 1.55, expr: 'sleepy', look: [3, -2], arms: 'hold' },
    { t: tn - 0.1, look: [0, 0], eyes: 'half', mouth: 'flat', brow: 0.3, ease: 'hold' },
  ];
  cue(tt, 'pop');
  shot(t0, {
    draw(lt, t) {
      setSunny(t, { sky: BLUE });
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      const s = t < tt ? 3.2 : 3.6;
      letter(640, 240, s, -0.06, 2310, { word: t > tt - 0.1 ? 'TIRED' : undefined, face: false });
      if (t > tn) { line([[560, 330], [720, 330]], 3, 2320, INK, 0.6); ink('FROM: ?', 640, 352, 16, INK, 2321); }
    },
  });
}

// 4. "Your brain has mailboxes built just for those letters, called adenosine receptors."  The brain, ringed with little mailboxes.
{
  const t0 = at('Your brain has'), tr = at('receptors');
  const spots = [[150, 300], [230, 140], [380, 90], [530, 120], [620, 260], [480, 395], [270, 400]];
  cue(at('mailboxes', 1) + 0.1, 'pop', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, x: 480, z: 1 }, { t: 5, x: 450, z: 1.05 }],
    draw(lt, t) {
      setBlank(t, YEL);
      brain(390, 255, 230, 160, 2410);
      spots.forEach(([x, y], i) => { if (t > at('mailboxes', 1) + i * 0.12) mailbox(x, y + 28, 0.55, 2420 + i * 7, { post: false, face: 'smile' }); });
      popLabel(t, tr - 0.1, 'ADENOSINE RECEPTORS', 760, 470, 22, { seed: 2490, rot: -0.03 });
      if (t > tr) arrow([700, 445], [600, 330], 2495, INK, 0.2);
    },
  });
}

// 5. "Every time a letter drops in, the parts of your brain that keep you alert slow down a little."  A letter goes in; YOU's bulb dims.
{
  const t0 = at('Every time a letter'), tdrop = at('drops in') - 0.3, ts = at('slow down');
  const ado = [{ t: t0, x: 210, y: 432, size: 1.05, expr: 'sleepy', look: [3, -2] }, { t: tdrop - 0.2, aR: 2.2, bend: 0.3, reach: 1, ease: 'out' }, { t: tdrop + 0.5, arms: 'down', ease: 'io' }];
  const you = [{ t: t0, x: 760, y: 432, size: 1.05, expr: 'happy', look: [-3, 0] }, { t: at('alert') - 0.1, expr: 'neutral', ease: 'hold' }, { t: ts, eyes: 'half', mouth: 'flat', sy: 0.94, sx: 1.04, ease: 'io' }];
  cue(tdrop + 0.45, 'plop'); cue(ts, 'slide_down', 0.6);
  shot(t0, {
    draw(lt, t) {
      setSunny(t);
      const slot = mailbox(450, 432, 1.3, 2510, { face: t > tdrop + 0.45 ? 'sleepy' : 'smile', flag: false });
      const hand = drawCarrier(poseAt(ado, t), t < tdrop);
      tossLetter(t, tdrop, hand, [slot.x, slot.y], 2520, 1, 0.45, 50);
      const P = poseAt(you, t);
      drawChar(YOU, P);
      bulb(P.x + 8, 196, 22, 2530, t < ts + 0.2 || Math.floor(t * 12) % 4 === 0 && t < ts + 0.6);
    },
  });
}

// 6. "The longer you're awake, the more letters arrive. By the end of a long day, the mail carrier is shoving them through with both hands."
{
  const t0 = at("The longer you're"), te = at('end of a long'), tb = at('both hands');
  const ado = [{ t: t0, x: 250, y: 432, size: 1.05, expr: 'sleepy' }];
  for (let k = 0, tk = t0 + 0.4; tk < at('That heavy') - 0.2; k++, tk += tk > te ? 0.28 : 0.7) {
    const side = k % 2 ? 'aL' : 'aR', sg = k % 2 ? -1 : 1;
    ado.push({ t: tk, [side]: sg * 2.6, bend: 0.2, reach: 1, ease: 'hold', expr: tk > te ? 'determined' : 'sleepy' }, { t: tk + 0.14, [side]: sg * 0.6, ease: 'hold' });
  }
  const tosses = ado.filter((k, i) => i > 0 && i % 2 === 1).map(k => k.t);
  tosses.forEach((tk, i) => cue(tk + 0.32, 'plop', i % 2 ? 0.5 : 0.7));
  const you = [{ t: t0, x: 780, y: 432, size: 1.0, expr: 'neutral', look: [-3, 0] }, { t: te, eyes: 'half', mouth: 'flat', sy: 0.9, sx: 1.06 }, { t: tb, expr: 'sleepy', sy: 0.84, sx: 1.12, mouth: 'o' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setSunny(t, { sky: t > te ? YEL : BLUE });
      if (t > te) shape(blobPts(860, 150, 42, 42, 2601, 12, 0.02), RED, 3.4, 2601, 1);
      const slot = mailbox(480, 432, 1.3, 2610, { face: t > te ? 'o' : 'sleepy', flag: false });
      const P = poseAt(ado, t);
      let hands = [[P.x - 50, P.y - 60], [P.x + 50, P.y - 60]];
      drawChar(ADO, P, { hold: (h, P2, A2) => { hands = h; mailBag()(h, P2, A2); } });
      tosses.forEach((tk, i) => tossLetter(t, tk, hands[i % 2 ? 0 : 1], [slot.x, slot.y], 2620 + i * 3, 0.9, 0.32, 40));
      drawChar(YOU, poseAt(you, t));
    },
  });
}
// 7. "That heavy, yawning feeling is what scientists call sleep pressure. Adenosine isn't the only thing behind it, but scientists think it's one of the big ones."
{
  const t0 = at('That heavy'), tp0 = at('sleep pressure'), ti = at("isn't the only");
  const you = [
    { t: t0, x: 420, y: 443, size: 1.15, expr: 'sleepy', sy: 0.86, sx: 1.1, arms: 'up', look: [0, -3] },
    { t: at('yawning'), mouth: 'o', eyes: 'closed', ease: 'hold' },
    { t: at('yawning') + 0.8, mouth: 'flat', eyes: 'half', ease: 'hold' },
    { t: ti + 0.4, look: [4, 0], ease: 'hold' },
  ];
  cue(t0 + 0.1, 'thud', 0.8); cue(ti + 0.2, 'pop', 0.5); cue(ti + 0.5, 'pop', 0.5);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 8, z: 1.05, y: 280 }],
    draw(lt, t) {
      setBlank(t, RED); ground(443, 2701, { grass: false });
      const P = poseAt(you, t);
      drawChar(YOU, P, { hold: h => letter((h[0][0] + h[1][0]) / 2, Math.min(h[0][1], h[1][1]) - 40, 4.2, 0.03, 2710, { word: 'TIRED', face: false }) });
      popLabel(t, tp0 - 0.1, 'SLEEP PRESSURE', 420, 70, 30, { seed: 2720, fill: YEL });
      if (t > ti) [[690, 400, 0.9], [790, 410, 0.7], [870, 415, 0.55]].forEach(([x, y, s], i) => {
        if (t < ti + 0.3 * i) return;
        shape(boxPts(x - 34 * s, y - 50 * s, 68 * s, 56 * s, 2730 + i), INK, 3, 2730 + i, 1);
        ink('?', x, y - 22 * s, 34 * s, PAPER, 2735 + i);
      });
      popLabel(t, at('one of the big') - 0.1, 'ONE OF THE BIG ONES', 700, 150, 20, { seed: 2740, rot: 0.04 });
    },
  });
}

// 8. "Then you sleep, the letters get cleared away overnight, and you wake up with empty mailboxes."  The letters float off into the night.
{
  const t0 = at('Then you sleep'), tc = at('cleared away'), tw = at('wake up', 1);
  const slotLetters = 7;
  cue(tc, 'whoosh', 0.6); cue(tw, 'ding', 0.6);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      if (t < tw) setNight(t); else setSunny(t);
      const slot = mailbox(480, 432, 1.6, 2810, { face: t < tw ? 'sleepy' : 'happy', flag: false });
      if (t < tw) for (let i = 0; i < slotLetters; i++) {
        const u = clamp((t - tc - i * 0.18) / 1.6, 0, 1);
        if (u <= 0 || u >= 1) { if (u <= 0) letter(slot.x - 30 + i * 10, slot.y - 6 - (i % 3) * 5, 0.8, (i - 3) * 0.2, 2820 + i * 3); continue; }
        letter(slot.x + Math.sin(u * 6 + i) * 40 + (i - 3) * 20 * u, slot.y - u * 360, 0.8 * (1 - 0.5 * u), Math.sin(u * 8 + i) * 0.5, 2820 + i * 3, { face: 'happy' });
      }
      if (t < tw) zzz(560, 200, t, 2850, 1.3);
      if (t > tw) { plus(slot.x - 70, slot.y - 60, 8, 2860); plus(slot.x + 80, slot.y - 40, 6, 2861); }
    },
  });
}

// 9. "Sleep is, among other things, your brain doing its paperwork."  YOU, asleep at a desk, stamping letters DONE.
{
  const t0 = at('Sleep is, among'), tp = at('paperwork');
  const you = [{ t: t0, x: 420, y: 421, size: 1.1, expr: 'sleepy', eyes: 'closed', mouth: 'smile', arms: 'down' }];
  for (let k = 0, tk = t0 + 0.3; tk < t0 + 6; k++, tk += 0.6) { you.push({ t: tk, aR: 1.9, bend: 0.4, ease: 'hold' }, { t: tk + 0.2, aR: 0.9, bend: 0.4, ease: 'hold' }); cue(tk + 0.2, 'thud', 0.35); }
  shot(t0, {
    draw(lt, t) {
      setDesk(t, { wall: BLUE, chart: false });
      const n = Math.floor(clamp((t - t0 - 0.3) / 0.6, 0, 9));
      for (let i = 0; i < 6 - Math.min(5, n); i++) letter(250, 410 - i * 9, 1.2, 0.05 * (i % 2 ? 1 : -1), 2910 + i * 3, { face: false });
      for (let i = 0; i < Math.min(8, n); i++) letter(620, 410 - i * 9, 1.2, 0.04 * (i % 2 ? -1 : 1), 2940 + i * 3, { face: false, word: i === Math.min(8, n) - 1 ? 'DONE' : undefined });
      drawChar(YOU, poseAt(you, t));
      zzz(460, 250, t, 2970);
      popLabel(t, tp - 0.1, 'PAPERWORK', 250, 110, 26, { seed: 2980, fill: YEL, rot: -0.04 });
    },
  });
}

// 10. "It's a tidy system, right up until someone tampers with the mail."  A tidy row of mailboxes, and a red shadow behind one.
{
  const t0 = at("It's a tidy"), tt = at('tampers');
  const ado = [{ t: t0, x: 200, y: 432, expr: 'happy', look: [3, -1] }, ...A.nod(t0 + 0.3, 2), { t: tt + 0.2, expr: 'curious', look: [4, 0], ease: 'hold' }];
  const caf = [{ t: t0, x: 770, y: 432, hide: true, expr: 'smug', look: [-4, 0] }, { t: tt - 0.1, hide: false, ease: 'hold' }, ...A.take(tt + 0.05, { hold: 0.2, mouth: 'smirk' }), { t: tt + 0.5, expr: 'smug', look: [-4, 0], ease: 'hold' }];
  cue(tt + 0.05, 'ding', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setSunny(t);
      drawChar(CAF, poseAt(caf, t));
      [400, 560, 720].forEach((x, i) => mailbox(x, 432, 1.0, 3010 + i * 10, { face: 'smile', flag: false }));
      drawCarrier(poseAt(ado, t), false);
    },
  });
}
