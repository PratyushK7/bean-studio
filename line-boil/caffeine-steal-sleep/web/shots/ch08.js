// CHAPTER 8: "How caffeine steals your sleep" (script lines 99 to 112). The recap through the earlier sets, then the callback: the washed mug, the sign at midnight.

musicMood(at('So, how does caffeine') - 0.2, 'calm');               // the recap
musicMood(at("Tiredness doesn't get") - 0.2, 'triumphant');         // the answer
musicMood(at('The mug was empty') - 0.1, 'silent');                 // a beat of nothing
musicMood(at('The closed sign is still') - 0.05, 'triumphant');     // the callback
musicMood(at("But here's the question") - 0.1, 'mystery');          // the closing hook: a question left open
musicMood(at('Until then') - 0.1, 'upbeat');                        // the ask, into the channel outro

// 1. "So, how does caffeine steal your sleep? It never gave you energy in the first place."  YOU sits up in bed, thinking; ENERGY crossed out.
{
  const t0 = at('So, how does caffeine'), te = at('never gave you');
  const you = [{ t: t0, x: 580, y: 384, size: 1.0, expr: 'thinking', arms: 'chin', fx: 'think' }, { t: te, arms: 'down', fx: null, expr: 'neutral', look: [-3, -3], ease: 'hold' }];
  cue(te + 0.6, 'thud', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: YEL }); nightWindow(t);
      const top = bed(640, 443, 290, 8101);
      drawChar(YOU, poseAt(you, t));
      blanket(505, 785, top, 8110, RED);
      popLabel(t, te, 'ENERGY', 420, 330, 30, { seed: 8120, rot: -0.04 });
      if (t > te + 0.6) { line([[360, 310], [480, 350]], 7, 8121, RED); line([[360, 350], [480, 310]], 7, 8122, RED); }
    },
  });
}

// 2. "It sat in your brain's mailboxes, wearing a closed sign, while the tiredness letters piled up outside."  The doorstep, one more time.
{
  const t0 = at("It sat in your"), tp = at('piled up');
  const ado = [{ t: t0, x: 260, y: 430, size: 1.1, expr: 'sleepy', look: [3, -1] }];
  const caf = [{ t: t0, expr: 'smug', look: [-4, 0] }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      paper(RED); doorway(110, 430, 140, 280, 8201, BLUE); ground(430, 8202, { fill: PAPER, grass: false });
      const slot = mailbox(620, 430, 1.7, 8210, { face: 'o' });
      cafInSlot(slot, caf, t);
      letterPile(450, 430, 6 + Math.floor(clamp((t - t0) / 0.12, 0, 40)), 8220, 1.05);
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      popLabel(t, tp, 'PILED UP', 450, 110, 28, { seed: 8230, fill: YEL });
    },
  });
}

// 3. "Your liver cleared it slowly, half at a time, over many hours."  Four, then two, then one.
{
  const t0 = at('Your liver cleared'), th = at('half at a time');
  const liv = [{ t: t0, x: 200, y: 443, size: 1.2, expr: 'neutral', look: [4, 0] }, ...A.nod(th, 2)];
  const gone = i => i >= 2 ? th + (i - 2) * 0.1 : i === 1 ? th + 1.2 : Infinity;
  cue(th, 'pop', 0.6); cue(th + 1.2, 'pop', 0.6);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: RED, floor: YEL });
      clockFace(560, 120, 60, 3 + lt * 1.4, 8301);
      cafRow(t, [480, 580, 680, 780], 443, gone, 8310, [-3, 0]);
      drawChar(LIV, poseAt(liv, t));
    },
  });
}

// 4. "And for a 3 p.m. coffee, enough can still be there at midnight to keep a few slots shut."  The clock runs to midnight; two slots stay shut.
{
  const t0 = at('And for a 3'), tm = at('there at midnight');
  const cafs = [0, 1].map(i => [{ t: t0, expr: 'smug', look: [i ? -3 : 3, 0] }]);
  cue(tm, 'tick', 0.7);
  shot(t0, {
    draw(lt, t) {
      setNight(t);
      clockFace(150, 110, 50, hourAt(t, t0 + 0.3, 3, 12, tm - t0 - 0.3), 8401);
      popLabel(t, t0 + 0.1, t < tm ? '3PM' : 'MIDNIGHT', 150, 190, 20, { seed: 8405, fill: PAPER });
      [330, 480, 630, 780].forEach((x, i) => {
        const slot = mailbox(x, 432, 1.1, 8410 + i * 9, { face: i === 0 || i === 2 ? 'o' : 'sleepy' });
        if (i === 0 || i === 2) cafInSlot(slot, cafs[i ? 1 : 0], t, { k: 0.5 });
      });
      popLabel(t, at('few slots shut') - 0.05, 'A FEW SLOTS SHUT', 560, 120, 24, { seed: 8420, fill: YEL });
    },
  });
}

// 5. "Not enough to feel. Just enough to cost you sleep you might never notice losing."  YOU sleeps, smiling; a small caffeine tiptoes off with the Zs.
{
  const t0 = at('Not enough to feel'), tj = at('Just enough');
  const caf = [{ t: t0, x: 470, y: 443, size: 0.95, expr: 'smug', look: [3, 0] }];
  for (let k = 0, tk = tj; tk < tj + 3.2; k++, tk += 0.45) caf.push({ t: tk, x: 470 + k * 34, y: 443 - (k % 2 ? 9 : 0), fL: k % 2 ? 8 : 0, fR: k % 2 ? 0 : 8, ease: 'io' });
  for (let k = 0; k < 7; k++) cue(tj + k * 0.45, 'tick', 0.22);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: YEL }); nightWindow(t);
      const top = bed(250, 443, 260, 8501);
      drawLying(YOU, Object.assign(poseAt([{ t: 0 }], t), { x: 290, y: top - 26, size: 0.95, eyes: 'closed', mouth: 'smile', breathe: 2 }), { tilt: 0.25 });
      blanket(235, 380, top, 8510, RED);
      zzz(215, 300, t, 8515);
      drawChar(CAF, poseAt(caf, t), { hold: h => { if (t > tj) { const b = [h[1][0] + 22, h[1][1] - 28]; shape(blobPts(b[0], b[1], 26, 30, 8520, 10, 0.1), PAPER, 3.2, 8520, 1); ink('ZZZ', b[0], b[1] + 5, 14, BLUE, 8521); } } });
      popLabel(t, t0 + 0.1, 'NOT ENOUGH TO FEEL', 640, 120, 22, { seed: 8530, fill: PAPER });
    },
  });
}

// 6. "Like the sleepers in that study, you'd wake up and swear you slept fine."  The morning again; the monitor still frowns.
{
  const t0 = at('Like the sleepers'), ts = at('swear', 2);
  const you = [{ t: t0, x: 580, y: 384, size: 1.0, expr: 'sleepy', look: [0, -2] }, { t: ts - 0.2, arms: 'up', expr: 'happy', ease: 'back' }, { t: ts + 1.4, arms: 'down', expr: 'smug', ease: 'io' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: BLUE });
      const top = bed(640, 443, 290, 8601);
      drawChar(YOU, poseAt(you, t));
      blanket(505, 785, top, 8610, RED);
      shape(boxPts(785, 318, 110, 14, 8620), RED, 3.2, 8620, 1);
      line([[800, 332], [800, 443]], 4, 8621); line([[880, 332], [880, 443]], 4, 8622);
      monitor(840, 262, 120, 84, t, 8630, { face: 'frown', screen: RED });
      popLabel(t, ts + 0.2, 'SLEPT FINE!', 330, 150, 28, { seed: 8640, fill: PAPER, rot: -0.04 });
    },
  });
}

// 7. "Tiredness doesn't get cancelled; it gets rescheduled."  CANCELLED is crossed out; RESCHEDULED gets stamped.
{
  const t0 = at("Tiredness doesn't get"), tr = at('rescheduled');
  const ado = [{ t: t0, x: 220, y: 443, size: 1.3, expr: 'sleepy', arms: 'hold' }, { t: tr - 0.25, aR: 2.6, bend: 0.3, expr: 'determined', ease: 'out' }, { t: tr, aR: 1.2, expr: 'happy', ease: 'hold' }];
  cue(t0 + 1.0, 'thud', 0.6); cue(tr + 0.05, 'thud');
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 8701, { grass: false });
      letter(600, 250, 6.0, -0.05, 8710, { face: false });
      if (t > t0 + 0.4) { ink('CANCELLED', 600, 210, 34, INK, 8720, -0.05); }
      if (t > t0 + 1.0) line([[480, 216], [720, 200]], 8, 8721, RED);
      if (t > tr) { ctx.save(); ctx.translate(600, 290); ctx.rotate(-0.12); const k = t < tr + D ? 1.3 : 1; ctx.scale(k, k); label('RESCHEDULED', 0, 0, 40, { seed: 8730, fill: RED, ink: PAPER }); ctx.restore(); }
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
    },
  });
}

// 8. "None of this makes coffee a villain."  A mug with a painted-on moustache, wiped off.
{
  const t0 = at('None of this'), tv = at('villain');
  const you = [{ t: t0, x: 760, y: 443, size: 1.1, expr: 'neutral', look: [-4, -1] }, ...A.shake(tv - 0.1, 2)];
  shot(t0, {
    draw(lt, t) {
      setStage(t, { wall: YEL });
      mug(420, 432, 4.0, 8810, { face: t > tv + 0.6 ? 'happy' : 'frown' });
      if (t < tv + 0.6) { tube([[365, 330], [395, 318], [420, 326]], 6, INK, 8820); tube([[420, 326], [445, 318], [475, 330]], 6, INK, 8821); }
      popLabel(t, tv + 0.6, 'NOT A VILLAIN', 420, 120, 30, { seed: 8830, fill: PAPER });
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9. "It does exactly what it's built to do, just for much longer than the cup suggests. The cup and the caffeine simply keep very different hours."  Two clocks.
{
  const t0 = at('It does exactly'), tc = at('The cup and the');
  const caf = [{ t: t0, x: 680, y: 443, size: 1.3, expr: 'smug', arms: 'hips' }, { t: tc + 1.0, eyes: 'happy', mouth: 'grin', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 8, z: 1.04 }],
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 8901, { grass: false });
      const u = clamp((t - t0 - 0.3) / (tc + 2 - t0), 0, 1);
      clockFace(280, 170, 80, 3 + 0.17 * u, 8910, { wedge: [3, 3 + 0.17 * u, RED] });
      clockFace(680, 170, 80, 3 + 9 * u, 8920, { wedge: [3, 3 + 9 * u, YEL] });
      mug(280, 443, 2.2, 8930, { face: 'smile' });
      drawChar(CAF, poseAt(caf, t));
      if (t > tc) { popLabel(t, tc, 'THE CUP: 10 MIN', 280, 290, 20, { seed: 8940, fill: PAPER }); popLabel(t, tc + 0.4, 'THE CAFFEINE: HOURS', 680, 290, 20, { seed: 8945, fill: YEL }); }
    },
  });
}

// 10. "The mug was empty by four."  Silence. The clean mug on its shelf, and the clock at four.
{
  const t0 = at('The mug was empty');
  shot(t0, {
    cam: [{ t: 0, z: 1.12, x: 540, y: 230 }, { t: 1.6, z: 1.16, x: 540, y: 230 }],
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: BLUE });
      clockFace(560, 92, 34, 4, 9001);
      shelf(540, 235, 200, 9010);
      mug(500, 235, 0.95, 9020, { face: 'happy' });
      mug(585, 235, 0.95, 9025, { color: BLUE });
    },
  });
}

// 11. "The closed sign is still up at midnight."  The callback: the sign at midnight, caffeine waving.
{
  const t0 = at('The closed sign is still');
  const caf = [{ t: t0, expr: 'smug', look: [0, 0] }, { t: at('still up', 2) - 0.1, expr: 'happy', ease: 'hold' }, ...A.wave(at('still up', 2), at("But here's the question") - 0.1, 'R')];
  cue(t0 + 0.1, 'pop', 0.6);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      midnightSky(t, 480, 150, 120);
      clockFace(150, 110, 50, 12, 9101);
      label('MIDNIGHT', 150, 190, 20, { seed: 9105, fill: PAPER });
      letterPile(300, 432, 30, 9110, 1.1);
      const slot = mailbox(480, 432, 2.0, 9120, { face: 'o' });
      cafInSlot(slot, caf, t, { swing: true });
      drawChar(ADO, Object.assign(poseAt([{ t: 0 }], t), { x: 760, y: 432, size: 1.1, expr: 'sleepy', fx: 'zzz', look: [-4, -2] }), { hold: mailBag() });
    },
  });
}

// 12. THE CLOSING HOOK. "But here's the question we didn't answer: if caffeine only hides your tiredness, what happens when you drink it
// every single day?"  A week on the calendar fills with a coffee a day; the mail carrier is left with a question mark.
{
  const t0 = at("But here's the question"), th = at('hides your'), te = at('every single day');
  const caf = [
    { t: t0, x: 170, y: 443, size: 1.35, expr: 'smug', arms: 'hips', look: [4, -2] },
    { t: th - 0.1, look: [4, 1], eyes: 'half', mouth: 'smirk', ease: 'hold' },
    ...A.shrug(te + 0.6, { hold: 1.0, after: 'smirk' }),
  ];
  const ado = [
    { t: t0, x: 560, y: 443, size: 1.0, expr: 'sleepy', look: [-4, -1] },
    { t: at("didn't answer") - 0.1, arms: 'chin', expr: 'thinking', ease: 'hold' },
    { t: te, look: [2, -4], ease: 'hold' },
  ];
  for (let i = 0; i < 7; i++) cue(te + i * 0.13, 'plop', 0.5);
  cue(t0 + 0.4, 'pop', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 7, z: 1.04, y: 262 }],
    draw(lt, t) {
      setRoom(t, { wall: RED, floor: YEL });
      shape(boxPts(330, 60, 560, 250, 9201), PAPER, 4, 9201, 1);
      shape(boxPts(330, 60, 560, 50, 9202), BLUE, 3.4, 9202, 1);
      ink('EVERY SINGLE DAY?', 610, 87, 24, PAPER, 9203);
      ['M', 'T', 'W', 'T', 'F', 'S', 'S'].forEach((d, i) => {
        const x = 370 + i * 80;
        ink(d, x, 135, 20, INK, 9210 + i);
        if (i) line([[330 + i * 80, 112], [330 + i * 80, 300]], 2, 9220 + i, INK, 0.6, false);
        if (t > te + i * 0.13) mug(x, 285, 1.05, 9230 + i * 3, { face: 'smile' });
      });
      drawChar(CAF, poseAt(caf, t));
      const P = poseAt(ado, t);
      drawChar(ADO, P, { hold: mailBag() });
      if (t > t0 + 0.4) ink('?', 668, 352, 92, YEL, 9250, 0.12, 12);
    },
  });
}

// 13. "That's a mailbox for another day."  Morning: the mailbox flag goes up, the carrier tips his cap.
{
  const t0 = at("That's a mailbox");
  const ado = [{ t: t0, x: 700, y: 432, size: 1.05, expr: 'happy', look: [-4, -1] }, ...A.wave(t0 + 0.3, t0 + 1.6, 'R')];
  cue(t0 + 0.35, 'pop', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setSunny(t);
      mailbox(450, 432, 1.7, 9310, { face: 'happy', flag: t > t0 + 0.35 });
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      popLabel(t, t0 + 0.45, 'ANOTHER DAY', 450, 110, 30, { seed: 9320, fill: YEL, rot: 0.03 });
    },
  });
}

// 14. "Until then, tell us in the comments: what time is your last coffee?"  The last shot: YOU with a mug and a comment card; YOU raises
// the mug, waves, and the iris closes on its face. (The channel outro follows, with the like, share and subscribe ask.)
{
  const t0 = at('Until then'), tc = at('comments'), tl = at('last coffee');
  const you = [
    { t: t0, x: 250, y: 443, size: 1.15, expr: 'happy', arms: 'hold', look: [4, -1] },
    { t: tc - 0.1, aL: -1.75, bend: 0.05, reach: 1, mouth: 'open', ease: 'back' },
    { t: tl - 0.15, aL: -0.35, bend: -0.5, reach: 0.72, aR: 2.3, eyes: 'happy', mouth: 'grin', ease: 'back' },
    { t: tl + 0.5, look: [0, 0], ease: 'hold' },
    ...A.wave(tl + 0.6, VO_END(), 'L'),
  ];
  cue(tc, 'pop', 0.7); cue(tl, 'ding', 0.7);
  shot(t0, {
    tr: 'iris', iris: [257, 340],
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: BLUE });
      clockFace(560, 92, 34, 3 + (t - t0) * 0.6, 9401);
      const k = popK(t, tc - 0.05);
      scaled(690, 260, k, () => {
        shape(boxPts(470, 170, 440, 180, 9410), PAPER, 4.2, 9410, 1.2);
        shape(blobPts(518, 220, 26, 26, 9411, 10, 0.03), RED, 3, 9411, 1);
        miniFace(522, 222, 0.9, 0, 9412, 'smile');
        ink('COMMENTS', 640, 205, 22, INK, 9413);
        ink('MY LAST COFFEE:', 650, 262, 22, INK, 9414);
        const blink = Math.floor(t * 3) % 2 ? ' _' : '';
        clockFace(625, 312, 24, 3 + Math.max(0, t - tl) * 4, 9415);
        ink('?' + blink, 680, 314, 26, RED, 9416);
      });
      drawChar(YOU, poseAt(you, t), { hold: h => mug(h[1][0] + 4, h[1][1] + 16, 0.9, 9420, { steam: true }) });
    },
  });
}
