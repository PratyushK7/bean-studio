// CHAPTER 5: "The 3 p.m. coffee math" (script lines 58 to 72). 100 mg, a 5-hour half-life: 50 at 8 p.m., about 29 at midnight, about 11 at 7 a.m.

musicMood(at("Let's run the numbers") - 0.2, 'curious');
musicMood(at('By midnight', 1) - 0.2, 'mystery');      // the surprise: still there at midnight
musicMood(at('And at 7') - 0.2, 'playful');            // the punchline

// the kitchen: a blue wall, a window whose sky follows the clock, and a red counter
function kitchen(t, sky = YEL) {
  paper(BLUE);
  shape(boxPts(760, 50, 160, 150, 5001), sky, 4, 5001, 1);
  if (sky === INK) { moon(860, 95, 18, 5002); fillOnly(blobPts(790, 150, 2.5, 2.5, 5003, 6), PAPER, 5003); fillOnly(blobPts(890, 170, 2.5, 2.5, 5004, 6), PAPER, 5004); }
  line([[840, 50], [840, 200]], 3.4, 5005, INK, 0.6); line([[760, 125], [920, 125]], 3.4, 5006, INK, 0.6);
  ground(410, 5007, { fill: RED, grass: false });
  return 410;
}
// the chart: 3 p.m. (h 0) to 7 a.m. (h 16), 0 to 100 mg
const CHART = { x: 70, y: 40, w: 620, h: 300 };
const chX = h => CHART.x + 70 + h / 16 * (CHART.w - 110);
const chY = mg => CHART.y + CHART.h - 50 - mg / 100 * (CHART.h - 90);
const mgAt = (h, half = 5, dose = 100) => dose * Math.pow(0.5, h / half);
function chartBoard() {
  shape(boxPts(CHART.x, CHART.y, CHART.w, CHART.h, 5010), PAPER, 4, 5010, 1);
  line([[chX(0), chY(105)], [chX(0), chY(0)]], 3.4, 5011, INK, 0.8, false);
  line([[chX(0), chY(0)], [chX(16.4), chY(0)]], 3.4, 5009, INK, 0.8, false);
  [[0, '3PM'], [5, '8PM'], [9, 'MIDNIGHT'], [16, '7AM']].forEach(([h, s], i) => { line([[chX(h), chY(0)], [chX(h), chY(0) + 8]], 3, 5012 + i); ink(s, chX(h), chY(0) + 22, 13, INK, 5016 + i); });
  [[100, '100'], [50, '50']].forEach(([mg, s], i) => { line([[chX(0) - 8, chY(mg)], [chX(0), chY(mg)]], 3, 5020 + i); ink(s, chX(0) - 30, chY(mg), 13, INK, 5022 + i); });
  ink('MG', chX(0) - 30, chY(100) - 26, 12, INK, 5024);
}
// draw the decay curve up to hour hmax
function decay(hmax, half, color, seed, dose = 100) {
  if (hmax <= 0) return;
  const pts = [];
  for (let h = 0; h <= hmax + 1e-6; h += 0.25) pts.push([chX(h), chY(mgAt(h, half, dose))]);
  if (pts.length > 1) line(pts, 5, seed, color, 0.8, false);
  const e = pts[pts.length - 1];
  shape(blobPts(e[0], e[1], 7, 7, seed + 1, 7), color, 2.6, seed + 1, 0.6);
}

// 1. "Let's run the numbers on that 3 p.m. coffee. Say it's a small cup with about a hundred milligrams of caffeine. Cups vary a lot, so this is just a round number."
{
  const t0 = at("Let's run the numbers"), th = at('hundred milligrams'), tv = at('Cups vary'), tr = at('round number');
  const you = [{ t: t0, x: 250, y: 410, size: 1.15, expr: 'curious', look: [4, 0] }, ...A.point(th - 0.4, 'R', { ang: 1.4, after: 'smile', hold: 1.2 }), ...A.shrug(tr - 0.2, { hold: 1.0 })];
  cue(tv + 0.1, 'pop', 0.7); cue(tv + 0.4, 'pop', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      kitchen(t, YEL);
      clockFace(840, 270, 38, 3, 5101);
      mug(470, 410, 2.4, 5110, { word: t > th ? '100 MG' : undefined, face: t > th ? undefined : 'smile', steam: true });
      if (t > tv) mug(610, 410, 1.4, 5111, { color: BLUE, face: 'o' });
      if (t > tv + 0.3) mug(720, 410, 3.6, 5112, { color: YEL, face: 'happy' });
      drawChar(YOU, poseAt(you, t));
      popLabel(t, th - 0.05, 'ABOUT 100 MG', 470, 120, 30, { seed: 5120, fill: YEL, rot: -0.03 });
      popLabel(t, tr, 'A ROUND NUMBER', 470, 175, 18, { seed: 5125, rot: 0.03 });
    },
  });
}

// 2. "And say your half-life is five hours, near the middle of the range. Here's what's still in you as the evening goes on."  A ruler of half-lives.
{
  const t0 = at('And say your'), tf = at('five hours', 1), th = at("Here's what's still");
  const liv = [{ t: t0, x: 820, y: 410, size: 1.1, expr: 'neutral', look: [-4, -2] }, ...A.point(tf - 0.3, 'L', { ang: -2.2, after: 'smile', hold: 1.5 })];
  const rx = h => 140 + (h - 2) / 7 * 520;
  cue(tf, 'ding', 0.6);
  shot(t0, {
    draw(lt, t) {
      kitchen(t, YEL);
      if (t < th) {
        shape(boxPts(110, 140, 580, 70, 5201), PAPER, 4, 5201, 1);
        for (let h = 2; h <= 9; h++) { line([[rx(h), 140], [rx(h), 160]], 3, 5210 + h); ink(h === 9 ? '9+' : String(h), rx(h), 180, 16, INK, 5220 + h); }
        ink('HOURS', 400, 240, 16, PAPER, 5230);
        if (t > tf) { const x = rx(5); shape([[x, 136], [x - 16, 100], [x + 16, 100]], RED, 3.4, 5231, 1); popLabel(t, tf + 0.1, 'SAY 5', x, 70, 26, { seed: 5232, fill: YEL }); }
      } else {
        chartBoard();
        decay(clamp((t - th) * 1.2, 0, 0.6), 5, RED, 5240);
      }
      drawChar(LIV, poseAt(liv, t));
    },
  });
}

// 3. "By 8 p.m., about fifty milligrams are still on duty. By midnight, nine hours after the cup, you've still got roughly thirty."  The curve draws itself.
{
  const t0 = at('By 8'), t8 = at('fifty'), tm = at('By midnight', 1), t30 = at('roughly thirty');
  const you = [{ t: t0, x: 830, y: 410, size: 1.05, expr: 'curious', look: [-4, -3] }, { t: t30 + 0.3, expr: 'surprised', ease: 'hold' }, { t: t30 + 1.2, expr: 'sad', look: [-4, -3], ease: 'hold' }];
  const hAt = t => t < t8 ? lerp(0.6, 5, clamp((t - t0) / (t8 - t0), 0, 1)) : t < tm ? 5 : lerp(5, 9, EASE.io(clamp((t - tm) / (t30 - tm), 0, 1)));
  cue(t8, 'ding', 0.6); cue(tm, 'slide_down', 0.5); cue(t30, 'ding', 0.6);
  shot(t0, {
    draw(lt, t) {
      kitchen(t, t < tm ? RED : INK);
      chartBoard();
      decay(hAt(t), 5, RED, 5240);
      if (t > t8) popLabel(t, t8, '50 MG', chX(5) + 6, chY(50) - 40, 22, { seed: 5310, fill: YEL });
      if (t > t30) popLabel(t, t30, 'ABOUT 30 MG', chX(9) + 40, chY(29) - 46, 22, { seed: 5320, fill: YEL });
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 4. "That's more than a quarter of the cup, sitting in your mailboxes while you try to sleep."  In bed, the mug gauge at 29%, three slots closed.
{
  const t0 = at("That's more than a quarter"), tq = at('quarter'), ts = at('try to sleep');
  const lie = [{ t: t0, x: 700, y: 372, size: 0.95, expr: 'neutral', eyes: 'half', look: [0, -3] }, { t: ts, eyes: 'open', mouth: 'flat', look: [-2, -4], ease: 'hold' }];
  const cafk = [{ t: t0, expr: 'smug', look: [3, -1] }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: BLUE, floor: YEL }); nightWindow(t);
      const top = bed(650, 443, 290, 5401);
      drawLying(YOU, poseAt(lie, t), { tilt: 0.25 });
      blanket(642, 795, top, 5410, RED);
      // the gauge: a big mug outline filled to 29%
      const gx = 380, gy = 300, gw = 110, gh = 150, f = 0.29 * EASE.io(clamp((t - tq + 0.2) / 0.8, 0, 1));
      fillOnly([[gx - gw / 2 + 4, gy + gh - gh * f], [gx + gw / 2 - 4, gy + gh - gh * f], [gx + gw / 2 - 6, gy + gh], [gx - gw / 2 + 6, gy + gh]], RED, 5420);
      shape([[gx - gw / 2, gy], [gx + gw / 2, gy], [gx + gw / 2 - 4, gy + gh], [gx - gw / 2 + 4, gy + gh]], null, 4, 5421, 1, 3);
      shape([[gx + gw / 2, gy + 30], [gx + gw / 2 + 36, gy + 40], [gx + gw / 2 + 30, gy + 100], [gx + gw / 2 - 2, gy + 104]], null, 4, 5422, 1);
      popLabel(t, tq + 0.4, 'MORE THAN 1/4', gx, gy - 34, 22, { seed: 5430, fill: YEL });
      [[110, 0], [190, 1], [270, 0]].forEach(([x, k], i) => { const slot = mailbox(x - 50, 443, 0.75, 5440 + i * 9, { face: 'sleepy' }); if (k === 0) cafInSlot(slot, cafk, t, { k: 0.5 }); });
    },
  });
}

// 5. "If your half-life is closer to eight hours, it's nearer to half. And if you had a big coffee-shop cup, start with a bigger number."
{
  const t0 = at('If your half-life'), t8 = at('closer to eight'), tn = at('nearer to half'), tb = at('big coffee-shop');
  const big = [{ t: t0, x: 1100, y: 410, expr: 'smug' }, { t: tb - 0.1, x: 1100, ease: 'hold' }, { t: tb + 0.5, x: 830, ease: 'out' }];
  cue(tb, 'slide_up', 0.7);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      kitchen(t, INK);
      chartBoard();
      decay(9, 5, RED, 5240);
      decay(t < t8 ? 0 : lerp(0.2, 9, EASE.io(clamp((t - t8) / 1.4, 0, 1))), 8, BLUE, 5510);
      if (t > tn) popLabel(t, tn, 'NEARLY HALF', chX(9) + 30, chY(46) - 48, 22, { seed: 5520, fill: PAPER });
      if (t > tb - 0.1) { const x = poseAt(big, t).x; mug(x, 410, 5.4, 5530, { color: YEL, face: 'happy', steam: true }); }
      if (t > tb + 0.4) popLabel(t, tb + 0.4, 'BIGGER START', 830, 110, 22, { seed: 5540, fill: PAPER, rot: 0.04 });
    },
  });
}

// 6. "You probably won't feel thirty milligrams as a buzz. But it doesn't need to buzz to keep a few slots closed. The closed signs are smaller now, but they're still up at bedtime."
{
  const t0 = at('You probably'), tz = at('as a buzz'), tk = at('few slots closed'), ts = at('signs are smaller');
  const you = [{ t: t0, x: 120, y: 432, size: 1.0, expr: 'neutral', look: [3, 0] }, { t: tz, eyes: 'half', mouth: 'flat', ease: 'hold' }];
  const ado = [{ t: t0, x: 800, y: 432, size: 1.0, expr: 'sleepy', look: [-4, 0] }, { t: tk, expr: 'sad', look: [-4, -1], ease: 'hold' }];
  const cafs = [0, 1].map(i => [{ t: t0, expr: 'smug', look: [i ? -3 : 3, 0] }, { t: ts + 0.2 * i, eyes: 'happy', mouth: 'grin', ease: 'hold' }]);
  cue(tk, 'pop', 0.6); cue(tk + 0.2, 'pop', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1, x: 480 }, { t: 9, z: 1.05, x: 500 }],
    draw(lt, t) {
      setNight(t);
      shape(boxPts(70, 140, 120, 80, 5601), PAPER, 3.4, 5601, 1);
      ink('BUZZ', 130, 160, 16, INK, 5602);
      line([[90, 200], [170, 200]], 3, 5603); line([[100, 200], [100 + (t > tz ? 2 : 6), 186]], 4, 5604, RED);
      [260, 380, 500, 620].forEach((x, i) => {
        const slot = mailbox(x, 432, 1.0, 5610 + i * 9, { face: i === 1 || i === 3 ? 'o' : 'sleepy' });
        if (i === 1 || i === 3) cafInSlot(slot, cafs[i === 1 ? 0 : 1], t, { k: 0.5 });
      });
      if (t > tk) letterPile(800 - 60, 432, 6, 5650, 0.8);
      drawChar(YOU, poseAt(you, t));
      drawChar(ADO, poseAt(ado, t), { hold: mailBag() });
      popLabel(t, tk + 0.2, 'STILL CLOSED', 440, 120, 24, { seed: 5660, fill: YEL });
    },
  });
}

// 7. "And at 7 a.m., sixteen hours later, there's still about ten milligrams left. Just in time for the next coffee."
{
  const t0 = at('And at 7'), tt = at('ten milligrams'), tj = at('Just in time'), tn = at('next coffee');
  const you = [{ t: t0, x: 300, y: 410, size: 1.1, expr: 'sleepy', look: [3, 0], arms: 'down' }, { t: tj, arms: 'hold', eyes: 'happy', mouth: 'smile', ease: 'hold' }];
  const tiny = [{ t: t0, x: 520, y: 410, size: 0.65, expr: 'smug', look: [-3, 0] }, ...A.wave(tt + 0.2, tj - 0.1, 'L'), { t: tn, expr: 'surprised', look: [-4, -2], ease: 'hold' }];
  const fresh = [{ t: t0, x: 340, y: 360, hide: true, expr: 'happy' }, { t: tn - 0.1, hide: false, ease: 'hold' }, ...A.jump(tn - 0.1, [340, 360], [600, 410], { height: 120, upExpr: 'happy', endExpr: 'happy' }), ...A.cheer(tn + 1.2, 410, { height: 30 })];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      kitchen(t, PAPER);
      shape(blobPts(840, 175, 26, 26, 5701, 10), YEL, 3, 5701, 1);
      clockFace(840, 270, 38, 7, 5702);
      drawChar(YOU, poseAt(you, t), { hold: h => { if (t > tj) mug(h[1][0] + 4, h[1][1] + 16, 0.9, 5710, { steam: true }); } });
      drawChar(CAFS[3], poseAt(tiny, t));
      drawChar(CAF, poseAt(fresh, t));
      popLabel(t, tt, '7AM: ABOUT 10 MG', 480, 110, 26, { seed: 5720, fill: YEL });
    },
  });
}
