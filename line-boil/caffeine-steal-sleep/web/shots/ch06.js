// CHAPTER 6: "What a sleep study found" (script lines 73 to 86). Drake et al. 2013: 12 sleepers, 400 mg at 0, 3 or 6 h before bed.

musicMood(at('So does that leftover') - 0.2, 'serious');      // a study, a hard fact
musicMood(at("And here's the strange") - 0.1, 'silent');      // a pause before the surprise
musicMood(at('In their own sleep') - 0.1, 'mystery');         // the surprising result

// the scientist's clipboard (use as hold)
const clipboard = (hands) => {
  const [x, y] = hands[1];
  shape(boxPts(x - 4, y - 46, 46, 58, 6001, 0.08), PAPER, 3.2, 6001, 1);
  shape(boxPts(x + 10, y - 52, 18, 10, 6002, 0.08), INK, 2, 6002, 0.6);
  [0, 1, 2].forEach(i => line([[x + 4, y - 28 + i * 12], [x + 34, y - 26 + i * 12]], 2, 6003 + i, INK, 0.5, false));
};
// a blindfold across a character's eyes (use inside hold)
const blindfold = (c, P) => tube([tp(c, P, -c.w * 0.95, -c.h * 0.7), tp(c, P, c.w * 0.12, -c.h * 0.73), tp(c, P, c.w * 0.95, -c.h * 0.7)], 9, BLUE, 6010);
// a sleeper lying in a small bed, with a headband and a brain-wave trace over the head
function labBed(x, gy, i, t, o = {}) {
  const top = bed(x, gy, 170, 6100 + i * 10, { s: 0.75, frame: BLUE });
  const c = SLEEPERS[i], P = Object.assign(poseAt([{ t: 0 }], t), { x: x + 20, y: top - 4, size: 1.05, eyes: o.eyes || 'closed', mouth: o.mouth || 'smile', look: [0, -2], breathe: 2 });
  drawLying(c, P, { tilt: 0.2, hold: headband(c) });
  blanket(x - 10, x + 85, top + 6, 6105 + i * 10, o.blanket || RED, 0.7);
  if (o.wave !== false) {
    const pts = [];
    for (let k = 0; k <= 16; k++) pts.push([x - 70 + k * 8, top - 70 + Math.sin(k * 1.3 + t * 8 + i) * (o.flat ? 2 : 7)]);
    line(pts, 2.6, 6108 + i * 10, YEL, 0.4, false);
  }
}

// 1. "So does that leftover caffeine actually cost you sleep? In 2013, researchers led by Christopher Drake tested exactly that."
{
  const t0 = at('So does that leftover'), tY = at('In 2013'), td = at('Christopher Drake');
  const sci = [{ t: t0, size: 1.15 }, ...dropIn(tY + 0.1, 480, 432, { expr: 'neutral' }), ...A.nod(td + 0.2, 2), { t: td + 1.2, expr: 'determined', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setNight(t);
      if (t < tY) { ink('?', 480, 250, 140, YEL, 6201, 0.08, 14); }
      drawChar(SCI, poseAt(sci, t), { hold: clipboard });
      popLabel(t, tY + 0.2, '2013', 220, 150, 44, { seed: 6210, fill: YEL, rot: -0.05 });
      popLabel(t, td, 'DRAKE AND COLLEAGUES', 640, 250, 24, { seed: 6215, fill: PAPER, rot: 0.03 });
    },
  });
}

// 2. "Twelve healthy sleepers took a caffeine pill at bedtime, three hours before bed, or six hours before bed."  Twelve tiny beans, three groups.
{
  const t0 = at('Twelve healthy'), tb = at('at bedtime', 2), t3 = at('three hours before'), t6 = at('six hours before', 1);
  const xs = Array.from({ length: 12 }, (_, i) => 80 + i * 64 + Math.floor(i / 4) * 30);
  cue(tb, 'pop'); cue(t3, 'pop'); cue(t6, 'pop');
  shot(t0, {
    draw(lt, t) {
      setNight(t);
      xs.forEach((x, i) => {
        const c = SLEEPERS[i], P = Object.assign(poseAt([{ t: 0 }], t), { x, y: 432, size: 1.2, expr: 'neutral', look: [0, -2], arms: 'hold', breathe: 1.4 });
        if (t < t0 + 0.08 * i) return;
        drawChar(c, P, { hold: h => pill(h[1][0] + 2, h[1][1] - 2, 0.7, 6230 + i, RED, 0.4) });
      });
      popLabel(t, at('Twelve'), '12 SLEEPERS', 480, 90, 30, { seed: 6240, fill: YEL });
      popLabel(t, tb, 'AT BEDTIME', 176, 230, 20, { seed: 6241 });
      popLabel(t, t3, '3 H BEFORE', 462, 230, 20, { seed: 6242 });
      popLabel(t, t6, '6 H BEFORE', 748, 230, 20, { seed: 6243 });
    },
  });
}

// 3. "Each of them tried every version, plus a dummy pill, and nobody knew which night was which."  Four nights, four identical pills, blindfolds.
{
  const t0 = at('Each of them'), td = at('dummy pill'), tn = at('nobody knew');
  const sci = [{ t: t0, x: 820, y: 443, size: 1.05, expr: 'neutral', look: [-4, 0] }, { t: tn, expr: 'curious', look: [-3, -2], ease: 'hold' }];
  const sl = [{ t: t0, x: 110, y: 443, size: 1.5, expr: 'neutral', look: [3, 0] }, { t: tn + 0.1, mouth: 'wavy', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 6301, { grass: false });
      [0, 1, 2, 3].forEach(i => {
        const x = 245 + i * 135, show = t > t0 + 0.3 + i * 0.35;
        if (!show) return;
        shape(boxPts(x - 55, 120, 110, 150, 6310 + i), PAPER, 3.6, 6310 + i, 1);
        ink('NIGHT ' + (i + 1), x, 145, 16, INK, 6315 + i);
        pill(x, 200, 1.3, 6320 + i, RED, 0.3);
        if (t > tn) ink('?', x, 250, 34, BLUE, 6325 + i);
      });
      popLabel(t, td, 'ONE IS A DUMMY', 448, 320, 22, { seed: 6330, fill: YEL });
      drawChar(SCI, poseAt(sci, t), { hold: (h, P) => { clipboard(h); if (t > tn) blindfold(SCI, P); } });
      drawChar(SLEEPERS[0], poseAt(sl, t), { hold: (h, P) => { if (t > tn) blindfold(SLEEPERS[0], P); } });
    },
  });
}

// 4. "They went to bed at their usual time, at home, wearing a headband that recorded their brain waves."  Three beds, three headbands.
{
  const t0 = at('They went to bed'), th = at('headband', 1);
  shot(t0, {
    cam: [{ t: 0, z: 1.04, x: 480 }, { t: 5.5, z: 1, x: 480 }],
    draw(lt, t) {
      setNight(t);
      [180, 480, 780].forEach((x, i) => labBed(x, 432, i + 1, t, { wave: t > th + 0.3, blanket: [RED, YEL, RED][i] }));
      popLabel(t, at('at home'), 'AT HOME', 200, 120, 24, { seed: 6410, fill: PAPER, rot: -0.04 });
      popLabel(t, th, 'EEG HEADBAND', 560, 150, 24, { seed: 6415, fill: YEL, rot: 0.03 });
    },
  });
}

// 5. "The dose was big: 400 milligrams, roughly four small cups of coffee. That's the most the FDA considers generally fine for a whole day, in a single pill."
{
  const t0 = at('The dose was big'), t4 = at('400'), tc = at('four small cups'), tf = at('the FDA'), ts = at('single pill');
  const sci = [{ t: t0, x: 120, y: 443, size: 1.1, expr: 'neutral', look: [4, -1] }, ...A.point(t4 - 0.3, 'R', { ang: 1.9, after: 'smile', hold: 1.5 }), { t: ts, expr: 'surprised', ease: 'hold' }];
  for (let i = 0; i < 4; i++) cue(tc + i * 0.2, 'plop', 0.6);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 6501, { grass: false });
      const squeeze = clamp((t - ts + 0.2) / 0.5, 0, 1);
      for (let i = 0; i < 4; i++) { if (t < tc + i * 0.2) continue; const x = lerp(330 + i * 120, 690, EASE.in(squeeze)), s = 1.8 * (1 - squeeze * 0.8); if (s > 0.4) mug(x, 443, s, 6510 + i, { face: 'smile' }); }
      pill(560, 170, 3.2 + squeeze * 0.8, 6520, RED, -0.15);
      popLabel(t, t4, '400 MG', 560, 90, 34, { seed: 6530, fill: PAPER });
      popLabel(t, tf, 'FDA: ABOUT 400 MG A DAY', 560, 290, 22, { seed: 6535, fill: PAPER, rot: 0.02 });
      if (t > ts) popLabel(t, ts, 'IN ONE GO', 760, 380, 26, { seed: 6540, fill: RED, ink: PAPER });
      drawChar(SCI, poseAt(sci, t), { hold: clipboard });
    },
  });
}

// 6. "Even when the pill came six hours before bed, they lost more than an hour of sleep."  A bar of sleep; a chunk falls off.
{
  const t0 = at('Even when the pill'), tl = at('lost more');
  cue(tl, 'thud'); cue(tl + 0.1, 'slide_down', 0.6);
  shot(t0, {
    draw(lt, t) {
      setNight(t);
      labBed(480, 432, 5, t, { eyes: t > tl ? 'open' : 'closed', mouth: t > tl ? 'flat' : 'smile' });
      const fall = t > tl ? (t - tl) : 0, bx = 180, by = 120, seg = 75;
      for (let k = 0; k < 8; k++) {
        const lost = k === 7, x = bx + k * seg, y = by + (lost ? fall * fall * 300 : 0), r = lost ? fall * 2 : 0;
        if (y > 600) continue;
        shape(boxPts(x, y, seg - 6, 44, 6610 + k, r), lost ? RED : BLUE, 3.2, 6610 + k, 0.8);
      }
      ink('SLEEP', 480, 96, 18, PAPER, 6620);
      popLabel(t, at('six hours before', 2), '6 H BEFORE BED', 230, 230, 22, { seed: 6630, fill: PAPER });
      if (t > tl) popLabel(t, tl + 0.2, 'MORE THAN 1 HOUR LOST', 650, 230, 22, { seed: 6635, fill: YEL });
    },
  });
}

// 7. "And here's the strange part."  Silence. The scientist looks up from the clipboard.
{
  const t0 = at("And here's the strange");
  const sci = [{ t: t0, x: 480, y: 500, size: 1.7, expr: 'neutral', look: [0, 3] }, ...A.take(t0 + 0.4, { hold: 0.6, mouth: 'flat', browY: -8 }), { t: t0 + 1.3, look: [0, 0], expr: 'curious', ease: 'hold' }];
  shot(t0, {
    draw(lt, t) { setBlank(t, RED); drawChar(SCI, poseAt(sci, t), { hold: clipboard }); },
  });
}

// 8. "In their own sleep diaries, the six-hour nights didn't clearly stand out. The headband noticed; the sleepers mostly didn't."
{
  const t0 = at('In their own sleep'), th = at('headband noticed');
  const sl = [{ t: t0, x: 200, y: 443, size: 1.6, expr: 'happy', look: [3, -1] }, { t: at('mostly') , expr: 'smug', ease: 'hold' }];
  cue(th, 'tick', 0.8); cue(th + 0.25, 'tick', 0.8);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 6801, { grass: false });
      shape(boxPts(300, 110, 200, 240, 6810, -0.04), PAPER, 4, 6810, 1);
      line([[310, 140], [490, 132]], 3, 6811); ink('DIARY', 400, 128, 18, INK, 6812, -0.04);
      ink('SLEPT', 400, 210, 30, BLUE, 6813, -0.04); ink('FINE', 400, 250, 30, BLUE, 6814, -0.04);
      miniFace(400, 300, 1.6, -0.04, 6815, 'happy');
      if (t > th) {
        monitor(710, 230, 260, 170, t, 6820, { face: 'frown', screen: BLUE, color: YEL });
        popLabel(t, th + 0.1, 'HEADBAND: LESS SLEEP', 710, 380, 20, { seed: 6830, fill: YEL });
      }
      drawChar(SLEEPERS[2], poseAt(sl, t));
    },
  });
}

// 9. "It was a small study with a large dose, so it's not the final word."  Honest caveats, on cards.
{
  const t0 = at('It was a small'), tf = at('final word');
  const sci = [{ t: t0, x: 480, y: 432, size: 1.15, expr: 'neutral', look: [0, -2] }, ...A.shrug(tf - 0.2, { hold: 1.2 })];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setNight(t);
      popLabel(t, at('small study'), 'ONLY 12 PEOPLE', 220, 200, 24, { seed: 6910, fill: PAPER, rot: -0.04 });
      popLabel(t, at('large dose'), 'A BIG DOSE', 740, 200, 24, { seed: 6915, fill: PAPER, rot: 0.04 });
      popLabel(t, tf, 'NOT THE FINAL WORD', 480, 100, 26, { seed: 6920, fill: YEL });
      drawChar(SCI, poseAt(sci, t), { hold: clipboard });
    },
  });
}

// 10. "But it showed caffeine can take sleep quietly, without you feeling robbed. Which is the most polite kind of theft."  A tiptoeing burglar with a sack of Zs.
{
  const t0 = at('But it showed'), tq = at('quietly'), tp = at('most polite');
  const caf = [{ t: t0, x: 360, y: 443, size: 1.2, expr: 'smug', look: [3, 0], facing: 1 }];
  for (let k = 0, tk = t0 + 0.3; tk < tp - 0.2; k++, tk += 0.5) caf.push({ t: tk, x: 360 + k * 28, y: 443 - (k % 2 ? 10 : 0), fL: k % 2 ? 8 : 0, fR: k % 2 ? 0 : 8, ease: 'io' });
  caf.push({ t: tp - 0.1, look: [0, 0], fL: 0, fR: 0, y: 443, expr: 'smug', ease: 'hold' }, { t: tp + 0.3, lean: 0.25, sy: 0.92, eyes: 'happy', mouth: 'smirk', ease: 'io' }, { t: tp + 1.0, lean: 0, sy: 1, ease: 'io' });
  for (let k = 0; k < 8; k++) cue(t0 + 0.3 + k * 0.5, 'tick', 0.25);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: YEL }); nightWindow(t);
      const top = bed(250, 443, 260, 6950);
      drawLying(YOU, Object.assign(poseAt([{ t: 0 }], t), { x: 290, y: top - 26, size: 0.95, eyes: 'closed', mouth: 'smile', breathe: 2 }), { tilt: 0.25 });
      blanket(235, 380, top, 6960, RED);
      const P = poseAt(caf, t);
      drawChar(CAF, P, { hold: (h, P2) => {
        const b = [h[1][0] + 24, h[1][1] - 30];
        shape(blobPts(b[0], b[1], 30, 34, 6971, 10, 0.1), PAPER, 3.4, 6971, 1);
        ink('ZZZ', b[0], b[1] + 6, 16, BLUE, 6972);
      } });
      popLabel(t, tp, 'POLITE THEFT', 600, 120, 26, { seed: 6980, fill: YEL, rot: 0.04 });
    },
  });
}
