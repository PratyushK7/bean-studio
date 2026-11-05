// CHAPTER 7: "Less sleep, less deep sleep" (script lines 87 to 98). Gardiner et al. 2023: 24 studies, -45 min, deep sleep down, the 8.8 h cut-off.

musicMood(at('One study is one') - 0.2, 'calm');            // the summary
musicMood(at('It also changed') - 0.2, 'serious');          // deep sleep, a hard fact
musicMood(at('For a pre-workout') - 0.2, 'playful');        // the gym joke
musicMood(at("It's an average") - 0.2, 'calm');             // the quiet takeaway

// the sea of sleep: a yellow sky, light-sleep water near the top, deep-sleep ink at the bottom
const SURF = 140, DEEP = 380;
function sea(t) {
  paper(YEL);
  const top = [], deep = [];
  for (let i = 0; i <= 16; i++) { const x = -30 + i * 64; top.push([x, SURF + Math.sin(i * 1.3 + t * 2) * 6]); deep.push([x, DEEP + Math.sin(i * 0.9 + t) * 8]); }
  fillOnly([...top, [1000, 600], [-30, 600]], BLUE, 7001);
  fillOnly([...deep, [1000, 600], [-30, 600]], INK, 7002);
  line(top, 3.6, 7003, INK, 1, false);
  ink('LIGHT SLEEP', 120, SURF + 40, 18, PAPER, 7004);
  ink('DEEP SLEEP', 110, DEEP + 40, 18, YEL, 7005);
}

// 1. "One study is one study, so here's the bigger picture. In 2023, a team pulled together 24 studies on caffeine and sleep."
{
  const t0 = at('One study is one'), ty = at('In 2023'), tp = at('pulled together');
  const sci = [{ t: t0, x: 760, y: 443, size: 1.1, expr: 'neutral', look: [-4, -1] }, { t: tp + 1.5, expr: 'surprised', ease: 'hold' }];
  for (let k = 0; k < 8; k++) cue(tp + k * 0.25, 'plop', 0.4);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, YEL); ground(443, 7101, { grass: false });
      const n = t < tp ? 1 : Math.min(24, 1 + Math.floor((t - tp) / 0.1));
      paperStack(400, 443, n, 7110, 1.6);
      label(String(n), 400, 443 - n * 11.2 - 40, 30, { seed: 7120 + n, fill: PAPER });
      popLabel(t, ty, '2023', 160, 120, 40, { seed: 7130, fill: PAPER, rot: -0.05 });
      if (t > tp + 2.4) popLabel(t, tp + 2.4, '24 STUDIES', 640, 130, 28, { seed: 7135, fill: RED, ink: PAPER });
      drawChar(SCI, poseAt(sci, t), { hold: clipboard });
    },
  });
}

// 2. "On average, caffeine cut total sleep by about 45 minutes. It added roughly nine minutes to falling asleep, and about twelve more minutes awake in the night."
{
  const t0 = at('On average, caffeine'), t45 = at('45 minutes'), t9 = at('nine minutes'), t12 = at('twelve more');
  const lie = [{ t: t0, x: 520, y: 362, size: 1.0, eyes: 'closed', mouth: 'smile', look: [0, -2] }, { t: t9, eyes: 'open', mouth: 'flat', ease: 'hold' }, { t: t12 + 1.5, eyes: 'half', ease: 'hold' }];
  cue(t45, 'slide_down', 0.6); cue(t9, 'pop', 0.6); cue(t12, 'pop', 0.6);
  shot(t0, {
    draw(lt, t) {
      setRoom(t, { wall: RED, floor: BLUE }); nightWindow(t);
      const top = bed(480, 443, 290, 7201);
      drawLying(YOU, poseAt(lie, t), { tilt: 0.25 });
      blanket(470, 625, top, 7210, YEL);
      popLabel(t, t45, 'ABOUT 45 MIN LESS SLEEP', 560, 70, 24, { seed: 7220, fill: YEL });
      popLabel(t, t9, '+9 MIN TO FALL ASLEEP', 780, 170, 20, { seed: 7225, fill: PAPER, rot: 0.03 });
      popLabel(t, t12, '+12 MIN AWAKE', 780, 225, 20, { seed: 7230, fill: PAPER, rot: -0.03 });
    },
  });
}

// 3. "It also changed the kind of sleep you get. There was a bit more light sleep, and about eleven minutes less deep sleep, the slow, heavy kind that's hardest to wake from."
{
  const t0 = at('It also changed'), tl = at('light sleep', 1), td = at('less deep'), th = at('hardest to wake');
  const you = [
    { t: t0, x: 470, y: 300, size: 1.0, expr: 'sleepy', arms: 'up', look: [0, 2] },
    { t: td - 0.1, y: 360, expr: 'determined', ease: 'io' },
    { t: td + 0.8, y: 290, expr: 'sad', ease: 'out' },
    { t: td + 1.6, y: 360, expr: 'determined', ease: 'io' },
    { t: td + 2.3, y: 292, expr: 'sad', ease: 'out' },
  ];
  const caf = [{ t: t0, x: 470, y: 160, size: 1.0, expr: 'smug', look: [0, 2], legs: false }];
  const deep = [{ t: t0, x: 770, y: 498, size: 1.4, eyes: 'closed', mouth: 'smile', breathe: 2 }];
  cue(td, 'slide_down', 0.5); cue(td + 0.8, 'boing', 0.5); cue(td + 2.3, 'boing', 0.5);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      sea(t);
      drawChar(SLEEPERS[6], poseAt(deep, t), { shadow: false });
      const Py = poseAt(you, t), Pc = poseAt(caf, t);
      Pc.y += bob(t, 1, 3); Py.y += bob(t, 1, 3);
      line([[Pc.x - 20, Pc.y - 40], [Py.x - 10, Py.y - 120]], 3, 7310); line([[Pc.x + 20, Pc.y - 40], [Py.x + 14, Py.y - 120]], 3, 7311);
      drawChar(YOU, Py, { shadow: false });
      drawChar(CAF, Pc, { shadow: false });
      popLabel(t, tl, 'A BIT MORE LIGHT SLEEP', 700, 210, 20, { seed: 7320, fill: PAPER });
      popLabel(t, td, 'ABOUT 11 MIN LESS DEEP SLEEP', 610, 330, 20, { seed: 7325, fill: YEL });
      popLabel(t, th, 'HARDEST TO WAKE FROM', 690, 450, 18, { seed: 7330, fill: PAPER });
    },
  });
}

// 4. "From their numbers, the authors suggested stopping coffee about nine hours before bed to avoid losing sleep time."  The clock fills nine hours.
{
  const t0 = at('From their numbers'), tn = at('nine hours before');
  const sci = [{ t: t0, x: 170, y: 443, size: 1.1, expr: 'neutral', look: [4, -2] }, ...A.point(tn - 0.3, 'R', { ang: 2.3, after: 'smile', hold: 2 })];
  cue(tn, 'slide_up', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 7, z: 1.05, y: 255 }],
    draw(lt, t) {
      setBlank(t, PAPER); ground(443, 7401, { grass: false });
      const w = t < tn ? 0 : lerp(0, 8.8, EASE.io(clamp((t - tn) / 1.6, 0, 1)));
      clockFace(520, 230, 150, 3 + w, 7410, { wedge: [3, 3 + w, YEL] });
      popLabel(t, tn + 0.3, 'ABOUT 9 HOURS', 780, 420, 26, { seed: 7420, fill: YEL });
      popLabel(t, t0 + 0.2, 'FOR A STANDARD COFFEE', 780, 60, 18, { seed: 7425, fill: PAPER });
      drawChar(SCI, poseAt(sci, t), { hold: clipboard });
    },
  });
}

// 5. "For a 3 p.m. cup, that means bed no earlier than about midnight."  3 P.M. on the left, the bed and MIDNIGHT on the right.
{
  const t0 = at('For a 3', 2), tm = at('about midnight');
  const you = [{ t: t0, x: 170, y: 443, size: 1.1, expr: 'happy', arms: 'hold', look: [4, 0] }, ...A.walk(t0 + 0.8, 170, 520, 443, { speed: 170 }), { t: tm, expr: 'sleepy', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setRoom(t, { wall: YEL, floor: RED });
      clockFace(560, 92, 34, hourAt(t, t0 + 0.6, 3, 11.8, 2.2), 7501);
      bed(760, 443, 220, 7510);
      drawChar(YOU, poseAt(you, t), { hold: h => mug(h[1][0] + 4, h[1][1] + 16, 0.85, 7520, { steam: true }) });
      popLabel(t, t0 + 0.1, '3 P.M.', 170, 230, 26, { seed: 7530, fill: PAPER });
      popLabel(t, tm, 'BED: ABOUT MIDNIGHT', 760, 250, 24, { seed: 7535, fill: BLUE, ink: PAPER });
    },
  });
}

// 6. "For a pre-workout powder, with about twice the caffeine, they suggested more than thirteen hours. So a 6 p.m. gym session would mean a bedtime around 7 the next morning."
{
  const t0 = at('For a pre-workout'), tt = at('twice the'), t13 = at('thirteen hours'), t6 = at('So a 6'), t7 = at('7 the next');
  const gym = [{ t: t0, x: 360, y: 430, size: 1.25, expr: 'determined', look: [3, -2], arms: 'up' }];
  for (let k = 0, tk = t0 + 0.2; tk < t6 + 1.2; k++, tk += 0.7) gym.push({ t: tk, aL: -2.9, aR: 2.9, bend: 0.7, sy: 1.04, ease: 'out' }, { t: tk + 0.35, aL: -1.6, aR: 1.6, bend: 1.8, sy: 0.96, ease: 'in' });
  gym.push({ t: t7 - 0.5, arms: 'down', expr: 'sleepy', sy: 0.9, sx: 1.08, fx: 'zzz', ease: 'io' });
  const tubPos = [690, 430];
  cue(t13, 'ding', 0.6); cue(t7, 'deflate', 0.5);
  shot(t0, {
    draw(lt, t) {
      paper(PAPER);
      shape(boxPts(-20, 260, 1000, 40, 7601), RED, 3, 7601, 1);
      ground(430, 7602, { fill: BLUE, grass: false });
      clockFace(820, 110, 48, t < t6 ? 6 : hourAt(t, t7 - 0.8, 6, 19, 1.4), 7603);
      shape(boxPts(tubPos[0] - 45, tubPos[1] - 110, 90, 110, 7610), YEL, 3.6, 7610, 1);
      shape(boxPts(tubPos[0] - 50, tubPos[1] - 126, 100, 20, 7611), RED, 3.4, 7611, 1);
      ink('PRE', tubPos[0], tubPos[1] - 72, 18, INK, 7612); ink('WORKOUT', tubPos[0], tubPos[1] - 50, 13, INK, 7613);
      drawChar(GYMB, poseAt(gym, t), { hold: h => { if (t < t7 - 0.5) { dumbbell(h[0][0] - 4, h[0][1], 0.7, 7620, 0.3); dumbbell(h[1][0] + 4, h[1][1], 0.7, 7625, -0.3); } } });
      popLabel(t, tt, 'ABOUT 2X THE CAFFEINE', 520, 70, 22, { seed: 7630, fill: YEL });
      popLabel(t, t13, 'MORE THAN 13 HOURS', 520, 125, 24, { seed: 7635, fill: PAPER });
      popLabel(t, t6, '6 P.M. WORKOUT', 180, 200, 20, { seed: 7640, fill: PAPER, rot: -0.04 });
      popLabel(t, t7, 'BEDTIME: 7 A.M.', 640, 220, 26, { seed: 7645, fill: BLUE, ink: PAPER, rot: 0.03 });
    },
  });
}

// 7. "It's an average, not a law, and some people are far more sensitive than others."  Three beans, one of them vibrating.
{
  const t0 = at("It's an average"), ts = at('far more sensitive');
  const a = [{ t: t0, x: 220, y: 443, size: 1.0, expr: 'neutral' }];
  const b = [{ t: t0, x: 480, y: 443, size: 1.0, expr: 'happy' }];
  const c = [{ t: t0, x: 740, y: 443, size: 1.0, expr: 'neutral' }, { t: ts, expr: 'shocked', ease: 'hold' }];
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setBlank(t, BLUE); ground(443, 7701, { grass: false });
      popLabel(t, t0 + 0.1, 'AN AVERAGE, NOT A LAW', 480, 110, 30, { seed: 7710, fill: YEL });
      const P = poseAt(c, t); if (t > ts) { P.x += Math.sin(t * 60) * 3; P.lean = Math.sin(t * 47) * 0.04; }
      drawChar(SLEEPERS[9], Object.assign(P, { size: 2.2 }));
      [a, b].forEach((k, i) => drawChar(SLEEPERS[7 + i], Object.assign(poseAt(k, t), { size: 2.2 })));
      if (t > ts) { speedLines(800, 330, [1, 0], 24, 14, 7720, 3); speedLines(680, 330, [-1, 0], 24, 14, 7725, 3); popLabel(t, ts + 0.1, 'MORE SENSITIVE', 740, 210, 20, { seed: 7730, fill: PAPER }); }
    },
  });
}

// 8. "But it explains why your afternoon coffee keeps showing up for the night shift."  Caffeine clocks in at night, lunchbox and all.
{
  const t0 = at('But it explains'), tn = at('night shift');
  const caf = [{ t: t0, x: 120, y: 432, size: 1.2, expr: 'happy', look: [3, 0] }, ...A.walk(t0 + 0.3, 120, 480, 432, { speed: 160 }), { t: tn - 0.2, arms: 'pointR', expr: 'smug', ease: 'back' }];
  cue(tn + 0.1, 'ding', 0.8);
  shot(t0, {
    tr: 'smear',
    draw(lt, t) {
      setNight(t);
      shape(boxPts(560, 230, 110, 150, 7801), PAPER, 4, 7801, 1);
      clockFace(615, 280, 34, 11 + (t - t0) * 0.1, 7802);
      shape(boxPts(590, 330, 50, 30, 7803), INK, 2.4, 7803, 0.6);
      line([[615, 380], [615, 432]], 6, 7804);
      drawChar(CAF, poseAt(caf, t), { hold: h => { shape(boxPts(h[0][0] - 22, h[0][1] - 4, 44, 30, 7810), BLUE, 3, 7810, 1); line([[h[0][0] - 10, h[0][1] - 4], [h[0][0] - 8, h[0][1] - 14], [h[0][0] + 8, h[0][1] - 14], [h[0][0] + 10, h[0][1] - 4]], 3, 7811, INK, 0.6, false); } });
      popLabel(t, tn, 'NIGHT SHIFT', 615, 160, 30, { seed: 7820, fill: YEL, rot: -0.04 });
    },
  });
}
