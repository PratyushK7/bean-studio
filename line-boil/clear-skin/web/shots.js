// What if your skin became transparent? Ten shots, timed to the voiceover with at('word').
// Pose keys are in voiceover seconds; camera keys are in seconds into the shot.

// the reflection: same pose, mirrored about the mirror's plane
const reflect = (P, ax) => Object.assign({}, P, { x: 2 * ax - P.x, facing: -P.facing, look: [P.look[0], P.look[1]], lookAt: null });

// 1. "Imagine looking in the mirror, and your skin has gone completely clear."  Mid-stretch, then the reflection.
{
  const jo = [
    { t: 0, x: 140, y: GY, arms: 'up', eyes: 'closed', mouth: 'o', sy: 1.06, sx: 0.95, breathe: 0 },
    { t: 0.5, arms: 'down', eyes: 'half', mouth: 'flat', sy: 1, sx: 1, breathe: 1 },
    { t: at('mirror', 1) - 0.1, expr: 'neutral', look: [4, 0] },
    { t: at('skin', 1) - 0.1, expr: 'curious', lean: 0.08, x: 155, look: [4, 0] },
    ...A.take(at('gone') - 0.05, { hold: 0.6, mouth: 'wavy', browY: -10, eyes: 'wide' }),
    { t: at('clear') + 0.1, expr: 'shocked', lean: -0.05, look: [4, 0], ease: 'hold' },
  ];
  cue(at('gone') + 0.1, 'sparkle', 0.6);
  shot(0, {
    cam: [{ t: 0, z: 1.15, x: 285, y: 640 }, { t: 3.6, z: 1.25, x: 300, y: 640 }],
    draw(lt, t) {
      ground(GY + 5, 220, { grass: false });
      mirror(320, 520, 180, 285, 330);
      const P = poseAt(jo, t);
      drawChar(JOC, reflect(P, 275), { hold: (h, Q) => insides(JOC, Q, t), shadow: false });
      drawChar(JO, P);
    },
  });
}

// 2. "You'd think you'd turn invisible, like a ghost."  Jo daydreams about being a ghost.
{
  const t0 = at("You'd", 1);
  const jo = [
    { t: t0, x: 150, y: GY, expr: 'thinking', fx: 'think', arms: 'chin' },
    { t: at('invisible') - 0.1, expr: 'happy', fx: 'think', arms: 'chin', ease: 'hold' },
    { t: at('ghost') - 0.1, eyes: 'happy', mouth: 'o', ease: 'hold' },
  ];
  cue(at('think', 1), 'pop', 0.6); cue(at('invisible'), 'slide_up', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.02, y: 560 }, { t: 2.4, z: 1.08, y: 540 }],
    draw(lt, t) {
      ground(GY);
      const b = pop(t, at('think', 1) - 0.05, 0.3);
      if (b > 0) {
        shape(blobPts(355, 390, 130 * b, 115 * b, 340, 12, 0.07), PAPER, 3.4, 340, 1.4);
        [[250, 540, 12], [225, 585, 8]].forEach(([x, y, r], i) => shape(blobPts(x, y, r * b, r * b, 342 + i, 7), PAPER, 2.8, 342 + i, 0.8));
        const g = pop(t, at('invisible') - 0.1, 0.35);
        if (g > 0) ghost(355, 400 + Math.sin(t * 4) * 8, 1.7 * g, t, 350, t > at('ghost') ? 'o' : 'happy');
      }
      drawChar(JO, poseAt(jo, t));
    },
  });
}

// 3. "But skin is only a thin wrapper."  Jo shakes it off; the sweet unwraps to show what's inside.
{
  const t0 = at('But');
  const tw = at('wrapper') + 0.05;
  const jo = [
    { t: t0, x: 270, y: GY, expr: 'neutral', arms: 'hold', look: [0, 2] },
    ...A.shake(t0 + 0.05, 2),
    { t: at('thin') - 0.1, expr: 'smug', arms: 'hold', look: [0, 3], ease: 'hold' },
    { t: tw + 0.15, expr: 'happy', arms: 'hold', ease: 'hold' },
  ];
  cue(tw, 'pop'); cue(tw + 0.05, 'sparkle', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.25, x: 280, y: 610 }, { t: 1.7, z: 1.4, x: 285, y: 640 }],
    draw(lt, t) {
      ground(GY);
      const k = t < tw ? 0 : EASE.back(clamp((t - tw) / 0.3, 0, 1));
      drawChar(JO, poseAt(jo, t), {
        hold(h) {
          const cx = (h[0][0] + h[1][0]) / 2, cy = (h[0][1] + h[1][1]) / 2 - 8;
          candy(cx, cy, 0.9, k, 360);
          if (k > 0 && t < tw + 0.4) burst(cx, cy, 34, 56, 370, 0);
        },
      });
    },
  });
}

// 4. "Underneath, you'd see bright red muscles, yellow fat, and blood rushing through your veins."
{
  const t0 = at('Underneath');
  const jo = [
    { t: t0, x: 270, y: 830, size: 1.35, expr: 'surprised', look: [0, 4] },
    ...A.take(at('muscles') - 0.15, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
    { t: at('yellow', 1) - 0.1, expr: 'curious', look: [-3, 4], ease: 'hold' },
    { t: at('blood', 1) - 0.1, expr: 'surprised', look: [2, 4], ease: 'hold' },
    { t: at('rushing') + 0.1, expr: 'happy', ease: 'hold' },
    { t: at('veins') + 0.1, expr: 'love', ease: 'hold' },
  ];
  cue(at('muscles'), 'pop'); cue(at('fat'), 'plop'); cue(at('blood', 1), 'slide_up', 0.7); cue(at('rushing'), 'zip', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.2, x: 270, y: 630 }, { t: 4.8, z: 1.38, x: 270, y: 660 }],
    draw(lt, t) {
      band(BLUE, 0, 300, 380);
      ground(830, 381, { grass: false });
      drawChar(JOC, poseAt(jo, t), {
        hold: (h, Q) => insides(JOC, Q, t, {
          muscle: pop(t, at('muscles') - 0.05),
          fat: pop(t, at('fat') - 0.15),
          blood: clamp((t - at('blood', 1) + 0.1) / 0.5, 0, 1),
          flowT: at('rushing'),
        }),
      });
    },
  });
}

// 5. "Skin looks solid because its cells bounce light around, like fog, and its pigment soaks some up."
{
  const t0 = at('Skin', 3), SK = 420;
  const home = [[150, 520], [300, 600], [430, 500], [210, 700]];
  const hits = [at('bounce'), at('light', 1), at('around')];
  const cells = CELLS.map((c, i) => [{ t: t0, x: home[i][0], y: home[i][1], expr: 'neutral', look: [-2, -3], breathe: 2 }]);
  cells[0].push(...A.take(hits[0] - 0.25, { hold: 0.15 }), { t: hits[0] + 0.3, expr: 'happy', ease: 'hold' });
  cells[1].push(...A.cheer(hits[1] - 0.25, home[1][1], { height: 14 }));
  cells[2].push(...A.cheer(hits[2] - 0.25, home[2][1], { height: 14 }));
  cells[3].push({ t: at('fog') - 0.1, expr: 'dizzy', ease: 'hold' });
  const tp0 = at('pigment', 1), ts = at('soaks');
  const pig = [
    { t: t0, x: 400, y: 720, size: 0, expr: 'neutral' },
    { t: tp0 - 0.1, size: 0, ease: 'hold' },
    { t: tp0 + 0.15, size: 1, expr: 'smug', ease: 'back' },
    { t: ts + 0.32, sy: 0.75, sx: 1.25, eyes: 'squeeze', mouth: 'o', ease: 'hold' },
    { t: ts + 0.5, sy: 1, sx: 1, expr: 'happy', mouth: 'grin' },
  ];
  hits.forEach((h, i) => cue(h, 'pop', 0.8)); cue(at('fog'), 'whoosh', 0.5); cue(tp0, 'plop'); cue(ts + 0.32, 'deflate', 0.8);
  shot(t0, {
    cam: [{ t: 0, z: 1.05, x: 280, y: 520 }, { t: 5.5, z: 1, x: 270, y: 530 }],
    draw(lt, t) {
      band(BLUE, 0, SK, 390);
      ground(SK, 391, { fill: YEL, grass: false });
      drawChar(SUN, poseAt([{ t: 0, x: 80, y: 190, size: 0.7, expr: 'happy', arms: 'out' }], t));
      // the incoming ray, then the pinball
      shoot(t, t0 + 0.1, [110, 200], home[0], 400, { speed: (Math.hypot(40, 320)) / Math.max(0.3, hits[0] - t0 - 0.1), len: 200, face: 'o' });
      scatter(t, hits[0], home[0][0], home[0][1] - 30, 410, 5, 260);
      scatter(t, hits[1], home[1][0], home[1][1] - 30, 420, 5, 260);
      scatter(t, hits[2], home[2][0], home[2][1] - 30, 430, 5, 260);
      // fog puffs drift across the skin
      const f = pop(t, at('fog') - 0.15, 0.35);
      if (f > 0) [[110, 470, 60], [300, 450, 75], [460, 580, 55]].forEach(([x, y, r], i) => cloud(x + (t - t0) * 8, y, r * f, r * 0.42 * f, 440 + i));
      CELLS.forEach((c, i) => { const P = poseAt(cells[i], t); P.y += Math.sin(t * 3 + i * 2) * 5; drawChar(c, P); });
      // one ray heads for the pigment and gets swallowed
      const pp = poseAt(pig, t);
      if (pp.size > 0.05) {
        shoot(t, ts - 0.2, [520, 430], [pp.x + 10, pp.y - 50], 450, { speed: 560, len: 150, face: 'o' });
        drawChar(PIGS[0], pp);
      }
    },
  });
}

// 6. "That pigment is your built-in sunscreen."  The pigment crew holds up a parasol; sun rays bounce off.
{
  const t0 = at('That'), SK = 720;
  const xs = [175, 270, 365];
  const pigs = PIGS.map((c, i) => [{ t: t0, x: xs[i], y: SK - 10, expr: 'determined', arms: i === 1 ? 'up' : 'hips', size: 1.2, look: [0, -4] }]);
  pigs[0].push(...A.cheer(at('sunscreen') - 0.25, SK - 10, { height: 18 }));
  pigs[2].push(...A.cheer(at('sunscreen') - 0.15, SK - 10, { height: 18 }));
  pigs[1].push({ t: at('sunscreen'), expr: 'happy', arms: 'up', ease: 'hold' });
  const sun = [{ t: t0, x: 440, y: 180, size: 0.9, expr: 'determined', arms: 'fwd' }, { t: at('sunscreen'), expr: 'surprised', ease: 'hold' }];
  const shots = [0.1, 0.5, 0.9, 1.3, 1.7].map(d => t0 + d);
  shots.forEach(s => cue(s + 0.45, 'pop', 0.5)); cue(at('sunscreen'), 'sparkle');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 2.3, z: 1.06, y: 520 }],
    draw(lt, t) {
      band(BLUE, 0, SK, 460);
      ground(SK, 461, { fill: YEL, grass: false });
      drawChar(SUN, poseAt(sun, t));
      const top = [270, 470];
      shots.forEach((s, i) => {
        shoot(t, s, [410, 230], [top[0] + 40 - i * 20, top[1] + 10], 470 + i * 5, { speed: 600, len: 120 });
        scatter(t, s + 0.45, top[0] + 40 - i * 20, top[1] + 10, 480 + i * 7, 3, 300, YEL, -Math.PI * 0.5, 2.2);
      });
      PIGS.forEach((c, i) => drawChar(c, poseAt(pigs[i], t), i === 1 ? {
        hold(h) { parasol((h[0][0] + h[1][0]) / 2, 470, 110, 490); },
      } : {}));
    },
  });
}

// 7. "Without it, sunlight could burn you far more easily."  Clear Jo, no pigment: the rays go straight in.
{
  const t0 = at('Without');
  const jo = [
    { t: t0, x: 270, y: GY, expr: 'happy', look: [-3, -3] },
    { t: at('sunlight') - 0.1, expr: 'curious', look: [-4, -3] },
    ...A.take(at('burn') - 0.1, { hold: 0.35, eyes: 'wide', mouth: 'wavy' }),
    { t: at('burn') + 0.45, expr: 'scared', fx: ['sweat', 'anger'], ease: 'hold' },
    ...A.dash(at('easily') - 0.1, 270, 640, GY, { endExpr: 'scared' }),
  ];
  const shots = [0.05, 0.35, 0.65, 0.95, 1.25, 1.55].map(d => at('sunlight') + d);
  cue(at('sunlight'), 'zip', 0.6); cue(at('burn'), 'drum', 0.7);
  shot(t0, {
    cam: [{ t: 0, z: 1.05, x: 270, y: 560 }, { t: 2.2, z: 1.12, x: 280, y: 580, shake: 0 }, { t: 2.3, shake: 3 }, { t: 2.7, shake: 0 }],
    draw(lt, t) {
      band(BLUE, 0, 520, 500);
      ground(GY, 501);
      drawChar(SUN, poseAt([{ t: t0, x: 105, y: 270, size: 0.75, expr: 'smug', arms: 'out' }], t));
      const P = poseAt(jo, t);
      shots.forEach((s, i) => shoot(t, s, [150, 300], [P.x - 6 + i * 5, P.y - 80 - (i % 3) * 18], 510 + i * 5, { speed: 650, len: 140 }));
      // heat wiggles once it burns
      if (t > at('burn')) [-1, 0, 1].forEach(k => line(wavePts(P.x + k * 48, P.y - 190, P.x + k * 48, P.y - 240 - (Math.floor(t * 12) % 2) * 6, 1.5, 5, t * 6), 3, 520 + k, RED));
      drawChar(JOC, P, { hold: (h, Q) => insides(JOC, Q, t) });
    },
  });
}

// 8. "Glass frogs live like this, and hide their blood in their liver when they sleep."
{
  const t0 = at('Glass'), LY = 650;
  const tsl = at('blood', 2) - 0.1, tz = at('sleep');
  const frog = [
    { t: t0, x: 275, y: LY - 8, expr: 'happy', look: [0, 0] },
    ...A.cheer(at('live') - 0.25, LY - 8, { height: 22 }),
    { t: at('hide') - 0.1, expr: 'smug', look: [-3, 3], ease: 'hold' },
    { t: at('liver') - 0.1, expr: 'sleepy', ease: 'hold' },
    { t: tz, eyes: 'closed', mouth: 'smile', fx: 'zzz', breathe: 2, ease: 'hold' },
  ];
  cue(at('hide'), 'slide_down', 0.6); cue(at('liver'), 'plop', 0.8);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.1, x: 270, y: 560 }, { t: 3.8, z: 1.25, x: 270, y: 560 }],
    draw(lt, t) {
      if (t > at('when', 1) - 0.1) { band(BLUE, 0, 330, 530); moon(415, 265, 34, 531); }
      leaf(110, 450, LY, 540);
      const sl = clamp((t - tsl) / (tz + 0.3 - tsl), 0, 1);
      drawChar(FROG, poseAt(frog, t), { hold: (h, Q) => frogInsides(FROG, Q, t, sl), shadow: false });
    },
  });
}

// 9. "And scientists have already made a mouse's skin see-through, for a little while, using yellow food dye."
{
  const t0 = at('And scientists'), MY = 780;
  const td1 = at('made', 1) - 0.1, tst = at('see-through'), tw = at('while'), td2 = at('food') - 0.2, tdye = at('dye');
  const mouse = [
    { t: t0, x: 270, y: MY, expr: 'curious', look: [0, -4] },
    { t: td1 + 0.5, expr: 'surprised', look: [0, 3], ease: 'hold' },
    ...A.take(tst, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
    { t: tst + 0.6, expr: 'happy', look: [0, 3], ease: 'hold' },
    { t: tw + 0.1, expr: 'sad', ease: 'hold' },
    { t: td2, expr: 'curious', look: [0, -4], ease: 'hold' },
    ...A.cheer(tdye + 0.1, MY, { height: 30 }),
  ];
  cue(td1 + 0.35, 'plop'); cue(tst, 'sparkle', 0.8); cue(tw + 0.1, 'slide_down', 0.6); cue(td2 + 0.35, 'plop'); cue(tdye + 0.2, 'sparkle');
  // drop falls from the tip (270, 470) to the mouse's belly over 0.35 s
  const dropAt = (t, td) => { const u = (t - td) / 0.35; if (u > 0 && u < 1) drop(270, lerp(480, 700, EASE.in(u)), 9, 560, YEL); };
  shot(t0, {
    cam: [{ t: 0, z: 1.15, x: 270, y: 590 }, { t: 3.3, z: 1.2, x: 270, y: 600 }, { t: 4.2, z: 1.35, x: 270, y: 560 }, { t: 5.8, z: 1.35, x: 270, y: 560 }],
    draw(lt, t) {
      ground(MY, 550, { grass: false });
      const dy = lerp(-200, 0, EASE.out(clamp((t - t0) / 0.6, 0, 1)));
      dropper(270, 470 + dy, 570);
      dropAt(t, td1); dropAt(t, td2);
      const k = Math.min(pop(t, tst - 0.05, 0.3), 1 - clamp((t - tw - 0.1) / 0.4, 0, 1)) + pop(t, td2 + 0.35, 0.3);
      drawChar(MOUSE, poseAt(mouse, t), { hold: (h, Q) => mouseBelly(MOUSE, Q, t, clamp(k, 0, 1.1)) });
    },
  });
}

// 10. "So in the mirror, you wouldn't vanish. You'd see everything you're made of."  Back at the mirror, clear and proud.
{
  const t0 = at('So in the');
  const jo = [
    { t: t0, x: 150, y: GY, expr: 'curious', look: [4, 0] },
    ...A.shake(at("wouldn't") - 0.1, 2),
    { t: at('vanish') + 0.2, expr: 'smug', look: [4, 0], ease: 'hold' },
    ...A.cheer(at('everything') - 0.3, GY, { height: 26 }),
    { t: at('made', 2) - 0.1, expr: 'happy', look: [4, 0], ease: 'hold' },
    ...A.wave(at('made', 2), VO_END(), 'R'),
  ];
  cue(at('everything'), 'sparkle');
  shot(t0, {
    tr: 'iris', iris: [157, 692],
    cam: [{ t: 0, z: 1.1, x: 290, y: 620 }, { t: 4.4, z: 1.22, x: 300, y: 640 }],
    draw(lt, t) {
      ground(GY + 5, 220, { grass: false });
      mirror(320, 520, 180, 285, 330);
      const P = poseAt(jo, t);
      drawChar(JOC, reflect(P, 280), { hold: (h, Q) => insides(JOC, Q, t), shadow: false });
      drawChar(JOC, P, { hold: (h, Q) => insides(JOC, Q, t) });
      if (t > at('everything')) { const n = Math.floor(t * 12) % 4 < 2; plus(n ? 90 : 230, n ? 560 : 540, 8, 600); plus(n ? 250 : 80, n ? 600 : 610, 6, 601); }
    },
  });
}
