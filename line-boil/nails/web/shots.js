// What if your fingernails never stopped growing? Nine shots, timed to the voiceover with at('word').

function room(t) {
  band(YEL, 0, 560, 301);
  ground(GY, 220, { grass: false });
}

// 1. "Imagine you threw away your nail clippers forever."  Kit flings Snip into the bin.
{
  const tr = at('threw') + D, tl = tr + 0.85;
  const kit = [
    { t: 0, x: 310, y: GY, expr: 'determined', aL: -0.5, aR: 0.7, bend: 0.4, reach: 0.8, sy: 0.92, sx: 1.08, lean: 0.04, smear: null, lookAt: [90, 640] },
    { t: tr - 2 * D, aR: 0.25, sy: 0.84, sx: 1.16, lean: 0.08, ease: 'io' },
    { t: tr - D, aR: 2.4, bend: 0.1, reach: 1, sy: 1.14, sx: 0.9, lean: -0.08, smear: { dir: [-0.3, -1], k: 1.7 }, ease: 'hold' },
    { t: tr, aR: 3.0, aL: -1.9, sy: 1.06, sx: 0.96, lean: -0.1, smear: null, expr: 'happy', ease: 'hold' },
    { t: tr + 3 * D, sy: 1, sx: 1, lean: -0.03 },
    { t: tl + 0.1, arms: 'hips', lean: 0, expr: 'smug', lookAt: null, look: [3, 0], ease: 'hold' },
    ...A.nod(at('forever'), 1),
  ];
  cue(tr - D, 'whoosh'); cue(tr + 0.15, 'squeak', 0.7); cue(tl, 'thud', 0.8); cue(tl + 0.05, 'plop', 0.6);
  shot(0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.06, x: 260, y: 560 }, { t: 2.7, z: 1, x: 270, y: 520 }],
    draw(lt, t) {
      room(t);
      // Snip flies in an arc from Kit's hand into the bin, and peeks out
      if (t >= tr) {
        const u = clamp((t - tr) / (tl - tr), 0, 1);
        const x = lerp(400, 90, u), y = lerp(600, 690, u) - 380 * u * (1 - u);
        if (u < 1) {
          snip(x, y, 1, (t - tr) * 13, 950, 'o', 0.6);
          if (u > 0.1) speedLines(x, y, [1, 0.4], 50, 26, 952, 3);
        }
      }
      if (t >= tl) {
        const bob = t < tl + 0.25 ? 12 : 0;
        snip(92, 700 + bob, 0.9, -0.5, 950, 'frown', 0);
      }
      bin(90, GY, 960);
      if (t >= tl && t < tl + 2 * D) burst(90, 690, 30, 56, 965, 0);
      drawChar(KIT, poseAt(kit, t), {
        hold(hands) { if (t < tr - D) snip(hands[1][0] + 8, hands[1][1] - 18, 1, -1.2, 950, 'o', 0.2); },
      });
    },
  });
}

// 2. "Most people think nails just sit there, like little shields."  Sleepy nails; a shield pops in.
{
  const t0 = at('Most'), tsh = at('shields') - 0.1;
  const kit = [
    { t: t0, x: 100, y: 805, size: 0.6, expr: 'smug', look: [3, -3] },
    ...A.shrug(at('sit') - 0.1, { hold: 0.9, after: 'smirk' }),
    { t: tsh, expr: 'smug', lookAt: [450, 300], ease: 'hold' },
  ];
  cue(tsh, 'pop'); cue(tsh + 0.05, 'zip', 0.5);
  shot(t0, {
    cam: [{ t: 0, z: 1, y: 480 }, { t: 3.2, z: 1.06, y: 470 }],
    draw(lt, t) {
      band(BLUE, 0, 700, 330);
      ground(700, 331, { fill: PAPER, grass: false });
      bigHand(280, 460, 1.7, { face: 'sleepy' });
      if (t > tsh) {
        const u = clamp((t - tsh) / (3 * D), 0, 1), r = 44 * (u < 1 ? EASE.out(u) * 1.15 : 1);
        shield(452, 280, r, 970);
        if (t < tsh + 4 * D) burst(452, 280, 50, 80, 975, 0);
        if (u >= 1) arrow([410, 330], [345, 330], 976, INK, -0.25);
      }
      drawChar(KIT, poseAt(kit, t));
    },
  });
}

// 3. "But they're growing right now, pushed out from a root hidden under your skin."  The cut-away.
// 4. "New cells fill with keratin, the same tough stuff as hair, then die and slide forward."
{
  const t0 = at('But'), t1 = at('New'), tg = at('growing'), tsl = at('slide');
  const extAt = t => clamp((t - tg) * 4, 0, 34) + clamp((t - tsl) * 60, 0, 26);
  const kit = [
    { t: t0, x: 62, y: 462, size: 0.55, expr: 'curious', lookAt: [420, 450] },
    ...A.take(at('But') + 0.05, { hold: 0.45, mouth: 'o' }),
    { t: at('right now'), expr: 'surprised', lookAt: [440, 450], ease: 'hold' },
    { t: at('hidden') - 0.1, expr: 'curious', lookAt: [170, 540], ease: 'hold' },
    { t: at('New') + 0.2, expr: 'happy', lookAt: [240, 450], ease: 'hold' },
    { t: at('die') - 0.1, expr: 'sad', lookAt: [300, 450], ease: 'hold' },
    ...A.cheer(tsl - 0.3, 462, { height: 22 }),
  ];
  const root = [
    { t: t0, x: 172, y: 548, facing: 1, expr: 'sleepy' },
    { t: at('pushed') - 0.15, expr: 'determined', arms: 'fwd', sx: 1.1, sy: 0.9 },
    { t: at('pushed') + 0.15, sx: 0.94, sy: 1.08, lean: 0.12, ease: 'out' },
    { t: at('root') - 0.1, sx: 1, sy: 1, lean: 0, expr: 'happy', arms: 'up', ease: 'hold' },
    { t: t1 + 0.1, expr: 'determined', arms: 'fwd', ease: 'hold' },
    { t: at('die'), expr: 'sleepy', arms: 'down', ease: 'hold' },
    { t: tsl - 0.1, expr: 'determined', arms: 'fwd', lean: 0.15, ease: 'hold' },
  ];
  cue(tg, 'slide_up', 0.5); cue(at('pushed'), 'drum', 0.6);
  // cells leave the root one by one
  const spawns = [0, 1, 2, 3, 4, 5, 6, 7].map(i => t1 + 0.1 + i * 0.42);
  spawns.slice(0, 3).forEach(s => cue(s, 'pop', 0.5));
  cue(at('keratin'), 'sparkle'); cue(at('hair'), 'zip'); cue(at('die'), 'slide_down', 0.6); cue(tsl, 'whoosh');
  const drawSet = (t, cells) => {
    const xe = fingerSide(extAt(t));
    if (cells) spawns.forEach((ts, i) => {
      if (t < ts) return;
      const u = clamp((t - ts) / 0.3, 0, 1);
      const x = Math.min(xe - 18, 196 + (t - ts) * 26 + clamp((t - tsl) * 60, 0, 26)), y = lerp(500, 451, EASE.out(u));
      const dead = t > at('die') + i * 0.04, full = clamp((t - at('keratin')) / 0.6, 0, 1);
      shape(blobPts(x, y, 13, 11, 980 + i, 8), dead ? PAPER : RED, 2.8, 980 + i, 1);
      if (!dead && full > 0) fillOnly(blobPts(x, y + 2, 9 * full, 7 * full, 990 + i, 7), YEL, 990 + i);
      miniFace(x, y - 1, 0.5, 0, 1000 + i, dead ? 'sleepy' : 'happy');
    });
    return xe;
  };
  shot(t0, {
    tr: 'cut', cap: 690,
    cam: [{ t: 0, z: 1.15, x: 250, y: 470 }, { t: 1.4, z: 1, x: 270, y: 480 }, { t: 2.6, z: 1.05, x: 250, y: 500 }],
    draw(lt, t) {
      const xe = drawSet(t, false);
      drawChar(ROOT, poseAt(root, t));
      if (t > at('pushed')) arrow([215, 410], [Math.min(xe, 200 + (t - at('pushed')) * 300), 410], 1010, RED, 0.12);
      drawChar(KIT, poseAt(kit, t));
    },
  });
  shot(t1, {
    tr: 'smear', cap: 690,
    cam: [{ t: 0, z: 1, x: 270, y: 480 }, { t: 1.0, z: 1.3, x: 235, y: 480 }, { t: 2.8, z: 1.3, x: 240, y: 470 }, { t: 3.4, z: 1.02, x: 280, y: 430 }],
    draw(lt, t) {
      const xe = drawSet(t, true);
      drawChar(ROOT, poseAt(root, t));
      // hair is made of the same stuff: a yellow strand pops up beside the nail
      const th = at('hair') - 0.1;
      if (t > th) {
        const u = clamp((t - th) / 0.25, 0, 1), top = lerp(330, 190, EASE.back ? EASE.back(u) : u);
        nail(wavePts(450, 340, 455, top, 2.2, 10, t * 3), 10, 1020, t > th + 0.4 ? 'happy' : 'o', 0.7);
        if (u >= 1) arrow([xe - 6, 420], [436, 352], 1025, INK, -0.3);
        if (t < th + 3 * D) burst(452, 260, 34, 60, 1026, 0);
      }
      drawChar(KIT, poseAt(kit, t));
    },
  });
}

// 5. "Skip trimming for a year, and they'd stick out half as long as your fingers."  Calendar flips, nails grow.
// 6. "And they wouldn't grow straight. They'd curl and twist into spirals."
{
  const t0 = at('Skip'), ty = at('year'), t6 = at('And they');
  const flips = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(i => at('trimming') + i * 0.11);
  flips.forEach((f, i) => { if (i % 2 === 0) cue(f, 'tick', 0.5); });
  cue(at('stick'), 'slide_up', 0.7);
  const growE = t => 40 * EASE.io(clamp((t - at('trimming')) / (at('half') - at('trimming')), 0, 1));
  const kit5 = [
    { t: t0, x: 92, y: 805, size: 0.6, expr: 'curious', lookAt: [280, 300] },
    ...A.take(at('stick') - 0.05, { hold: 0.6, mouth: 'wavy', eyes: 'wide' }),
    { t: at('fingers') - 0.1, expr: 'shocked', lookAt: [280, 220], ease: 'hold' },
  ];
  const H = [300, 540, 1.6];
  shot(t0, {
    cam: [{ t: 0, z: 1.04, y: 470 }, { t: 3.6, z: 1, y: 480 }],
    draw(lt, t) {
      band(BLUE, 0, 700, 330);
      ground(700, 331, { fill: PAPER, grass: false });
      const page = flips.filter(f => t >= f).length;
      const fl = flips.findIndex(f => t < f + 0.11 && t >= f);
      calendar(95, 170, page, 1100, fl >= 0 ? (t - flips[fl]) / 0.22 : undefined);
      const e = growE(t);
      bigHand(...H, { ext: e, face: e > 4 ? (t > at('fingers') ? 'happy' : 'o') : 'sleepy' });
      // half a finger: two brackets beside the pinky, the nail one half as long
      if (t > at('half')) {
        const s = H[2], x = H[0] + 42 * s * 1.05 + 30, ty0 = H[1] - 50 * s - 62 * s;
        tube([[x, H[1] - 50 * s + 10], [x, ty0]], 6, RED, 1110);
        tube([[x, ty0 - 8], [x, ty0 - 8 - 36 * s]], 6, YEL, 1112);
      }
      drawChar(KIT, poseAt(kit5, t));
    },
  });

  const kit6 = [
    { t: t6, x: 92, y: 805, size: 0.6, expr: 'curious', lookAt: [260, 260] },
    ...A.shake(at("wouldn't") - 0.05, 2),
    { t: at('curl') - 0.1, expr: 'surprised', lookAt: [260, 200], ease: 'hold' },
    { t: at('spirals') - 0.1, expr: 'dizzy', fx: 'think', ease: 'hold' },
  ];
  const curlU = t => EASE.io(clamp((t - at('curl')) / (at('spirals') + 0.3 - at('curl')), 0, 1));
  cue(at('curl'), 'slide_up', 0.6); cue(at('twist'), 'boing', 0.7); cue(at('spirals'), 'sparkle', 0.6);
  shot(t6, {
    tr: 'smear', cap: 'top',
    cam: [{ t: 0, z: 1, y: 480 }, { t: 3.4, z: 0.96, y: 470 }],
    draw(lt, t) {
      band(BLUE, 0, 700, 330);
      ground(700, 331, { fill: PAPER, grass: false });
      calendar(80, 290, 11, 1100);
      const u = curlU(t);
      bigHand(300, 600, 1.35, { ext: 47 + 75 * u + (t - t6) * 3, curl: u, face: u > 0.5 ? 'happy' : 'o' });
      drawChar(KIT, poseAt(kit6, t));
    },
  });
}

// 7. "They'd turn heavy and brittle, and picking up a cup would be a struggle."
{
  const t0 = at("they'd turn"), tb = at('brittle'), tc = at('struggle') + 0.05;
  const kit = [
    { t: t0, x: 200, y: GY, expr: 'curious', arms: 'out', lookAt: [120, 620] },
    { t: at('heavy') - 0.1, aL: -0.7, aR: 0.7, bend: -0.1, reach: 0.9, sy: 0.88, sx: 1.12, expr: 'determined', fx: 'sweat', lookAt: [200, 950] },
    { t: at('heavy') + 0.3, sy: 0.94, sx: 1.06, ease: 'out' },
    ...A.take(tb + 0.05, { hold: 0.3, mouth: 'wavy', arms: 'down' }),
    ...A.walk(at('picking') - 0.1, 200, 270, GY, { speed: 170 }),
    { t: at('cup') - 0.05, aR: 1.5, bend: 0.1, reach: 1, expr: 'determined', lookAt: [450, 680], ease: 'io' },
    { t: tc, expr: 'scared', ease: 'hold' },
    { t: tc + 0.5, expr: 'sad', aR: 0.5, bend: -0.4, reach: 0.8, lookAt: [460, 700] },
  ];
  cue(tb + 0.05, 'tick'); cue(tc, 'slide_down', 0.6); cue(tc + 0.25, 'plop');
  shot(t0, {
    cam: [{ t: 0, z: 1.08, x: 250, y: 600 }, { t: 3.5, z: 1.02, x: 280, y: 560 }],
    draw(lt, t) {
      room(t);
      // table and cup
      shape(boxPts(370, 712, 150, 14, 1200), PAPER, 3.6, 1200);
      line([[390, 726], [392, GY]], 4, 1201); line([[500, 726], [498, GY]], 4, 1202);
      const tip = clamp((t - tc) / 0.25, 0, 1);
      cup(482, 712, 1, EASE.in(tip) * Math.PI / 2, 1210, tip > 0 ? 'o' : 'smile');
      if (t > tc + 0.25) [0, 1, 2].forEach(i => drop(470 - i * 22, 708 - (i % 2) * 6, 7 - i, 1220 + i));
      const sag = clamp((t - at('heavy') + 0.2) / 0.4, 0, 1) * 0.55;
      let tips = null;
      drawChar(KIT, poseAt(kit, t), { hold(hands, P) { tips = kitNails(hands, P, 70, 0.7, sag, 1230); } });
      // a nail cracks and a chip falls off
      if (tips && t > tb) {
        const p = tips[1][Math.floor(tips[1].length * 0.6)];
        crack(p, 1, 1240);
        const u = t - tb;
        if (u < 0.8) shape(blobPts(p[0] - 4 + u * 20, p[1] + 12 + 900 * u * u, 6, 4, 1241, 6), YEL, 2.4, 1241);
      }
    },
  });
}

// 8. "If they never snapped, after a lifetime each nail could be longer than you are tall."
// 9. "So that little click of the clippers? It's keeping your hands working."
{
  const t0 = at('If'), t9 = at('So that'), tk = at('click') + 0.05;
  const lenAt = t => 40 + 330 * EASE.io(clamp((t - at('after')) / (at('longer') + 0.3 - at('after')), 0, 1));
  const kit = [
    { t: t0, x: 200, y: GY, expr: 'scared', aR: 2.4, bend: 0.05, reach: 1, lookAt: [300, 560] },
    { t: at('lifetime') - 0.1, expr: 'curious', lookAt: [300, 300], ease: 'hold' },
    ...A.take(at('longer') - 0.1, { hold: 0.8, mouth: 'o', eyes: 'wide', arms: 'down' }),
    { t: at('longer') + 3 * D, aR: 2.4, bend: 0.05, reach: 1, lookAt: [300, 220], ease: 'hold' },
    { t: at('tall'), expr: 'shocked', ease: 'hold' },
    { t: t9 + 0.1, expr: 'curious', lookAt: [100, 650], ease: 'hold' },
    { t: tk - 0.25, lookAt: [300, 600], ease: 'hold' },
    ...A.take(tk + D, { hold: 0.35, mouth: 'grin', eyes: 'wide', arms: 'down' }),
    ...A.cheer(at('keeping') - 0.3, GY, { height: 30 }),
    { t: at('hands') - 0.1, expr: 'happy', lookAt: null, look: [2, 0], ease: 'hold' },
    ...A.wave(at('hands'), VO_END(), 'R'),
  ];
  const nights = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => at('after') + i * 0.24);
  cue(at('after'), 'drum', 0.7); cue(at('longer'), 'slide_up', 0.8);
  cue(t9 + 0.05, 'boing'); cue(tk, 'tick'); cue(tk + 0.02, 'pop'); cue(tk + 0.6, 'thud', 0.7);
  // where the hand was at the cut, to drop the cut-off nail from there
  const cutAt = [287, 670];
  const set = (t) => {
    band(YEL, 0, 560, 301);
    const k = nights.filter(n => t >= n).length;
    windowBox(410, 180, k % 2 === 1 && t < at('longer'), 1300);
    ground(GY, 220, { grass: false });
    bin(70, GY, 960);
  };
  const nailsUp = (h, L, seed) => [-0.14, 0, 0.14].map((da, i) =>
    nailPath(h[0], h[1] - 6, -Math.PI / 2 + da, L * (1 - Math.abs(i - 1) * 0.07), 0.12, 0, i - 1 || 1));
  shot(t0, {
    cap: 420,
    cam: [{ t: 0, z: 1.3, x: 240, y: 640 }, { t: 1.5, z: 1.25, x: 240, y: 610 }, { t: 4.1, z: 1, x: 270, y: 480 }],
    draw(lt, t) {
      set(t);
      const L = lenAt(t);
      drawChar(KIT, poseAt(kit, t), { hold(hands) { nailsUp(hands[1], L, 1310).forEach((p, i) => nail(p, 9, 1310 + i * 10, i === 1 ? (t > at('tall') ? 'happy' : 'o') : null)); } });
      // the height check: a dashed line at the top of Kit's cap
      if (t > at('longer') + 0.2) for (let x = 120; x < 470; x += 26) line([[x, 618], [x + 14, 618]], 2.6, 1330 + x);
      if (t > at('tall')) tube([[120, GY - 4], [120, 624]], 6, RED, 1340);
    },
  });
  shot(t9, {
    tr: 'iris', iris: [215, 700], cap: 420,
    cam: [{ t: 0, z: 1, x: 270, y: 480 }, { t: 1.2, z: 1.05, x: 250, y: 560 }, { t: 3.5, z: 1.15, x: 230, y: 640 }],
    draw(lt, t) {
      set(t);
      let hand = [280, 690];
      const A1 = drawChar(KIT, poseAt(kit, t), {
        hold(hands) {
          hand = hands[1];
          if (t < tk) nailsUp(hands[1], 370, 1310).forEach((p, i) => nail(p, 9, 1310 + i * 10, i === 1 ? 'o' : null));
          else nailsUp(hands[1], 5, 1310).forEach((p, i) => nail(p, 9, 1310 + i * 10, null));
        },
      });
      // the cut-off nails fall away
      if (t >= tk) {
        const u = t - tk, c = cutAt;
        if (u < 1.2) {
          const rot = Math.min(1.5, u * 3.2), dx = u * 160, dy = 700 * u * u;
          nailsUp(c, 360, 1310).forEach((p, i) => {
            const q = p.slice(1).map(([x, y]) => {
              const rx = x - c[0], ry = y - c[1];
              return [c[0] + rx * Math.cos(rot) - ry * Math.sin(rot) + dx, c[1] + rx * Math.sin(rot) + ry * Math.cos(rot) + dy];
            });
            if (q.length > 1) tube(q, 9, YEL, 1350 + i);
          });
        }
        if (u < 2 * D) burst(c[0], c[1], 16, 34, 1360, 0);
      }
      // Snip boings out of the bin, clicks, then hovers beside Kit
      const ts = t9 + 0.05, sx = 70, sy = 690;
      const target = [hand[0] - 30, hand[1] + 6];
      let px, py, rot = -0.4, face = 'happy', open = 0;
      if (t < ts) { px = sx; py = sy + 10; face = 'frown'; }
      else if (t < tk - 0.08) {
        const u = clamp((t - ts) / (tk - 0.08 - ts), 0, 1);
        px = lerp(sx, target[0], u); py = lerp(sy, target[1], u) - 220 * 4 * u * (1 - u);
        rot = lerp(-0.4, 0.3, u) + Math.sin(u * 9) * 0.3; open = 1; face = 'o';
      } else if (t < tk + 0.6) { px = target[0]; py = target[1]; rot = 0.3; open = t < tk ? 1 : 0; face = t < tk ? 'o' : 'happy'; }
      else {
        const u = clamp((t - tk - 0.6) / 0.4, 0, 1);
        px = lerp(target[0], 420, EASE.io(u)); py = lerp(target[1], 650, EASE.io(u)) + Math.sin(t * 4) * 6; rot = lerp(0.3, -0.2, u);
      }
      if (t < ts) { snip(px, py, 0.9, rot, 950, face, 0); bin(70, GY, 960); }
      else snip(px, py, 0.9, rot, 950, face, open);
      if (t >= at('keeping')) {
        [[330, 520], [470, 470], [120, 520]].forEach(([x, y], i) => { if (((t * 3 + i) % 1) < 0.6) plus(x, y, 12, 1370 + i); });
      }
    },
  });
}
