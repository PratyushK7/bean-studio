// What if you pooped a watermelon? Ten shots, timed to the voiceover with at('word').

const TX = 210, SIT = 704;   // toilet x; kid's (hidden) feet when sitting

// 1. "What if you sat on the toilet and pooped out a whole watermelon?"  Kid strains; a melon thuds down.
{
  const tl = at('whole', 1) + 0.1;
  const kid = [
    { t: 0, x: TX, y: SIT, expr: 'determined', arms: 'hips', sy: 0.94, sx: 1.05 },
    { t: 0.5, sy: 1.02, sx: 0.98, ease: 'hold' }, { t: 0.66, sy: 0.92, sx: 1.07, ease: 'hold' },
    { t: 0.83, sy: 1.02, sx: 0.98, ease: 'hold' }, { t: 1.0, sy: 0.92, sx: 1.07, fx: 'sweat', ease: 'hold' },
    { t: 1.5, expr: 'determined', sy: 0.88, sx: 1.1, ease: 'hold' },
    ...A.take(tl + 0.05, { hold: 0.6, mouth: 'wavy', browY: -8 }),
    { t: at('watermelon', 1) + 0.4, lookAt: [420, 700], expr: 'shocked', ease: 'hold' },
  ];
  cue(tl, 'thud'); cue(tl - 0.3, 'slide_down', 0.6);
  shot(0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.3, x: 300, y: 640 }, { t: 3.3, z: 1.2, x: 300, y: 620 }],
    draw(lt, t) {
      bathroom(TX);
      drawChar(KID, poseAt(kid, t), { shadow: false });
      bowl(TX);
      // the melon drops in from above and squashes on the floor
      const u = Math.min(1, Math.max(0, (t - (tl - 0.35)) / 0.35));
      if (t > tl - 0.35) {
        const land = t >= tl, dt = t - tl;
        const sq = !land ? { sx: 0.85, sy: 1.2 } : dt < D ? { sx: 1.35, sy: 0.65 } : dt < 2 * D ? { sx: 0.92, sy: 1.1 } : { sx: 1, sy: 1 };
        const r = 78, y = land ? GY - r * sq.sy : lerp(-120, GY - r, u * u);
        melon(420, y, r, 400, { ...sq, face: land && dt > 3 * D ? 'happy' : 'o' });
        if (land && dt < 3 * D) burst(420, GY - 20, 100, 130, 410, dt > D ? 1 : 0);
        if (!land) speedLines(420, y - r, [0, 1], 70, 40, 415);
      }
    },
  });
}

// 2. "Most people think the only problem is squeezing it out."  Melon jammed on a tiny exit; kid winces.
{
  const t0 = at('Most');
  const kid = [
    { t: t0, x: 90, y: 330, size: 0.55, expr: 'curious', lookAt: [300, 640] },
    { t: at('squeezing') - 0.1, expr: 'scared', ease: 'hold' },
  ];
  cue(at('squeezing'), 'deflate', 0.8); cue(at('out', 2), 'squeak', 0.7);
  shot(t0, {
    cam: [{ t: 0, z: 1, y: 480 }, { t: 3, z: 1.08, y: 520 }],
    draw(lt, t) {
      band(YEL, 0, 960, 350);
      fillOnly(boxPts(-40, 660, 620, 400, 351), RED, 351);
      line([[-40, 660], [240, 662]], 4.2, 352); line([[360, 662], [580, 660]], 4.2, 353);
      fillOnly(blobPts(300, 664, 58, 14, 354, 9), INK, 354);
      // push: squash and stretch in rhythm once "squeezing" lands
      const ts = at('squeezing'), k = t > ts ? Math.floor((t - ts) / (3 * D)) % 2 : 0;
      const sq = t > ts ? (k ? { sx: 0.8, sy: 1.25 } : { sx: 1.18, sy: 0.85 }) : { sx: 1.1, sy: 0.9 };
      const r = 110;
      melon(300, 660 - r * sq.sy * 0.9, r, 420, { ...sq, face: t > ts ? 'frown' : 'o' });
      if (t > ts) [[160, 560], [440, 560]].forEach(([x, y], i) => speedLines(x, y, [i ? 1 : -1, 0], 30, 16, 425 + i * 5, 3));
      drawChar(KID, poseAt(kid, t), { shadow: false });
    },
  });
}

// 3. "But a watermelon would never make it that far."  Melon shakes its head; kid does a take.
{
  const t0 = at('But', 1);
  const kid = [
    { t: t0, x: 110, y: 760, size: 0.7, expr: 'scared', lookAt: [330, 440] },
    ...A.take(t0 + 0.05, { hold: 0.6, mouth: 'o', browY: -8 }),
    { t: at('far') - 0.1, expr: 'curious', lookAt: [330, 440], ease: 'hold' },
  ];
  cue(at('never'), 'tick', 0.6); cue(at('never') + 0.2, 'tick', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.05 }, { t: 2.6, z: 1 }],
    draw(lt, t) {
      band(YEL, 0, 960, 360);
      ground(760, 361, { fill: PAPER, grass: false });
      const tn = at('never'), tf = at('far');
      let rot = 0, face = 'smile';
      if (t > tn && t < tn + 0.7) { rot = (Math.floor((t - tn) / (2 * D)) % 2 ? 0.12 : -0.12); face = 'frown'; }
      if (t >= tn + 0.7) face = 'happy';
      melon(330, 470, 130, 430, { rot, face });
      drawChar(KID, poseAt(kid, t));
    },
  });
}

// 4. "Your food pipe is only as wide as a coin, so you'd have to eat it in bites."
{
  const t0 = at('Your', 1), tb = at('only', 2) + 0.1, tc = at('coin'), te = at('eat', 1), tbites = at('bites');
  const PX = 300, PW = 52;   // pipe x and width
  cue(tb, 'thud'); cue(tc, 'ding', 0.7); cue(te, 'pop'); cue(te + 0.2, 'pop', 0.7);
  for (let i = 0; i < 4; i++) cue(tbites + i * 0.17, 'plop', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1, y: 470 }, { t: 4.4, z: 1.06, y: 500 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 370);
      // the pipe: a long paper tube with a dark mouth
      fillOnly(boxPts(PX - PW / 2, 360, PW, 620, 371), YEL, 371);
      line([[PX - PW / 2, 350], [PX - PW / 2 + 2, 980]], 4.4, 372);
      line([[PX + PW / 2, 350], [PX + PW / 2 - 2, 980]], 4.4, 373);
      shape(blobPts(PX, 352, PW / 2 + 6, 9, 374, 9), INK, 3, 374);
      // the coin, side by side with the opening
      if (t > tc - 0.05) {
        const pop = t - tc < D ? 1.3 : 1;
        coin(PX - 120, 470, (PW / 2) * pop, 380);
        line([[PX - 146, 520], [PX - 94, 520]], 3, 383); line([[PX - 26, 520], [PX + 26, 520]], 3, 384);
      }
      // the melon: drops, bonks the opening, sits stuck, then bursts into bites
      if (t < te) {
        const r = 100, dt = t - tb;
        const y = t < tb ? lerp(-80, 352 - r, EASE.in(Math.min(1, (t - t0) / (tb - t0)))) : 352 - r * (dt < D ? 0.7 : 1);
        const sq = t >= tb && dt < D ? { sx: 1.3, sy: 0.7 } : {};
        melon(PX, y, r, 390, { ...sq, face: t > tb + 0.1 ? 'frown' : 'o', look: t > tc ? [-3, 1] : [0, 0] });
        if (t >= tb && dt < 2 * D) burst(PX, 352, 60, 90, 395, dt > D ? 1 : 0);
      } else {
        if (t - te < 2 * D) burst(PX, 260, 80, 130, 396, t - te > D ? 1 : 0);
        for (let i = 0; i < 6; i++) {
          const go = tbites + i * 0.17, hx = PX + (i - 2.5) * 46, hy = 230 + (i % 2) * 40;
          if (t < go) chunk(hx, hy, 34, 400 + i, 0.2 * (i % 3 - 1));
          else {
            const v = Math.min(1, (t - go) / 0.25), y = t - go < 0.25 ? lerp(hy, 340, v) : 340 + (t - go - 0.25) * 600;
            if (y < 1000) chunk(lerp(hx, PX, v), y, 30, 400 + i);
          }
        }
      }
    },
  });
}

// 5. "Then your stomach squishes every bite into mush, finer than a grain of rice."
{
  const t0 = at('Then'), ts = at('squishes'), tm = at('mush'), tr = at('grain');
  cue(ts, 'deflate', 0.7); cue(ts + 0.35, 'deflate', 0.6); cue(tm, 'sparkle', 0.6); cue(tr, 'pop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, y: 470 }, { t: tm - t0, z: 1, y: 470 }, { t: tr - t0, z: 1.35, x: 290, y: 500 }, { t: 4.5, z: 1.4, x: 290, y: 500 }],
    draw(lt, t) {
      band(BLUE, 0, 960, 380);
      // the stomach: a yellow bag that clenches on "squishes"
      const k = t > ts && t < tm ? (Math.floor((t - ts) / (3 * D)) % 2 ? 0.86 : 1.1) : 1;
      tube([[120, 180], [140, 300], [150, 340]], 40, YEL, 501);
      tube([[400, 580], [450, 660], [520, 680]], 36, YEL, 502);
      shape(blobPts(270, 470, 190 * k, 160 / k, 500, 12, 0.08, -0.25), YEL, 5, 500);
      miniFace(330, 380, 2.2, 0, 503, t > ts && t < tm ? 'o' : 'happy');
      if (t > ts && t < tm) speedLines(490, 470, [1, 0], 40, 30, 505, 3);
      // contents: chunks before mush, specks after
      if (t < tm) for (let i = 0; i < 5; i++) chunk(200 + (i % 3) * 60 + Math.sin(t * 9 + i) * 4, 500 + Math.floor(i / 3) * 50, 30 * (t > ts ? 0.75 : 1), 510 + i, i * 0.4 + (t > ts ? t * 3 : 0));
      else for (let i = 0; i < 40; i++) fillOnly(blobPts(170 + rnd(520, i) * 220, 450 + rnd(521, i) * 110, 3.4, 3, 530 + i, 5), RED, 530 + i);
      if (t > tr) rice(400, 480, 50 * (t - tr < D ? 1.25 : 1), 590, 'o');
    },
  });
}

// 6. "Watermelon is mostly water, so your gut soaks it up into your blood."
{
  const t0 = at('Watermelon', 3), tw = at('water'), tsk = at('soaks');
  cue(tw, 'sparkle', 0.6); for (let i = 0; i < 5; i++) cue(tsk + i * 0.12, 'plop', 0.5);
  shot(t0, {
    cam: [{ t: 0, z: 1.05, y: 460 }, { t: 4, z: 1, y: 480 }],
    draw(lt, t) {
      const GT = 330;
      gut(GT, 600, YEL, 120);
      // the blood stream below, with drifting cells
      tube(wavePts(-60, 690, 600, 690, 1.6, 14, -t * 2, 30), 110, RED, 601);
      [[60, 690], [220, 680], [400, 700]].forEach(([x, y], i) => { const xx = ((x + t * 70) % 660) - 60; fillOnly(blobPts(xx, y, 18, 10, 602 + i, 8), PAPER, 602 + i); });
      // the slice rides in the gut and squeezes out its water
      const sx = 110 + (t - t0) * 25;
      slice(sx, gutY(sx, GT) - 40, 70, 610, { face: t > tw ? 'happy' : 'smile' });
      for (let i = 0; i < 5; i++) {
        const born = tw + i * 0.1, jump = tsk + i * 0.12;
        if (t < born) continue;
        const hx = 230 + i * 56, hy = gutY(hx, GT) - 10;
        let x = hx, y = hy;
        if (t > jump) { const u = Math.min(1, (t - jump) / 0.45); x = hx + u * 30 + (t - jump) * 40; y = lerp(hy, 680, u) - 120 * 4 * u * (1 - u); }
        dropGuy(x, y, 20, 620 + i * 5, t > jump + 0.45 ? 'happy' : 'smile');
      }
    },
  });
}

// 7. "The sugar becomes fuel for your muscles."  Sugar cubes zip into the kid, who flexes.
{
  const t0 = at('The sugar'), tf = at('fuel');
  const kid = [
    { t: t0, x: 300, y: GY, size: 1.15, expr: 'curious', lookAt: [100, 400] },
    { t: tf - 0.1, expr: 'surprised', ease: 'hold' },
    ...A.cheer(at('muscles') - 0.33, GY, { height: 30 }),
    { t: at('muscles') + 0.35, aL: -2.2, aR: 2.2, bend: -2.2, reach: 0.8, expr: 'smug', ease: 'hold' },
  ];
  cue(at('sugar'), 'zip');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1, y: 500 }, { t: 2.2, z: 1.08, y: 540 }],
    draw(lt, t) {
      band(YEL, 0, 640, 700);
      ground(GY, 701, { fill: PAPER, grass: false });
      drawChar(KID, poseAt(kid, t));
      for (let i = 0; i < 3; i++) {
        const st = at('sugar') + i * 0.18, u = Math.min(1, Math.max(0, (t - st) / (tf - st)));
        if (t < st || u >= 1) continue;
        const sx0 = -40, sy0 = 220 + i * 120, x = lerp(sx0, 300, EASE.in(u)), y = lerp(sy0, 620, EASE.in(u));
        sugar(x, y, 46, 710 + i * 5, 'happy');
        speedLines(x - 28, y, [1, 0.3], 40, 16, 730 + i, 3);
      }
      if (t > tf && t < tf + 4 * D) burst(300, 640, 90, 130, 740, t > tf + 2 * D ? 1 : 0);
      if (t > at('muscles')) { plus(170, 520, 12, 750); plus(430, 500, 10, 751); }
    },
  });
}

// 8. "Only the tough fibre and a few seeds keep sliding along."  Leftovers drift through the gut.
{
  const t0 = at('Only', 3);
  cue(at('fibre'), 'slide_up', 0.4); cue(at('seeds'), 'pop', 0.6); cue(at('sliding'), 'slide_down', 0.5);
  shot(t0, {
    cam: [{ t: 0, z: 1, x: 250 }, { t: 3.4, z: 1.04, x: 300 }],
    draw(lt, t) {
      band(RED, 0, 960, 800);
      const GT = 480;
      gut(GT, 801, YEL, 190);
      const drift = (t - t0) * 40;
      // fibre: lazy paper strings
      if (t > at('fibre') - 0.2) [[40, -30], [200, 20]].forEach(([x, dy], i) => {
        const x0 = x + drift;
        tube(wavePts(x0, gutY(x0, GT) + dy, x0 + 120, gutY(x0 + 120, GT) + dy, 2, 8, t * 2 + i, 16), 12, PAPER, 810 + i);
      });
      // seeds: sleepy until "keep", then wide awake as they slide
      if (t > at('seeds') - 0.1) [[130, 30], [300, -35], [420, 25]].forEach(([x, dy], i) => {
        const x0 = x + drift * (t > at('sliding') ? 1.6 : 1);
        seedGuy(x0, gutY(x0, GT) + dy, 26, 820 + i * 5, t < at('keep'));
      });
      if (t > at('sliding')) speedLines(60, GT, [1, 0], 60, 40, 840, 3);
    },
  });
}

// 9. "So you can eat a whole watermelon, but what comes out is just a normal poop."
{
  const t0 = at('So you'), tc = at('comes') + 0.15;
  const kid = [
    { t: t0, x: TX, y: SIT, expr: 'curious', lookAt: [420, 700], arms: 'down' },
    { t: at('but', 2) - 0.1, expr: 'determined', arms: 'hips', look: [0, 0], ease: 'hold' },
    { t: tc, expr: 'happy', arms: 'down', sy: 1.06, sx: 0.96, fx: 'sparkle', ease: 'hold' },
    { t: tc + 2 * D, sy: 1, sx: 1, ease: 'hold' },
    { t: at('normal') - 0.1, expr: 'love', ease: 'hold' },
  ];
  cue(tc, 'plop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.2, x: 290, y: 620 }, { t: 4.3, z: 1.28, x: 290, y: 640 }],
    draw(lt, t) {
      bathroom(TX);
      drawChar(KID, poseAt(kid, t), { shadow: false });
      bowl(TX);
      // a little splash out of the bowl
      if (t > tc && t < tc + 0.6) { const u = (t - tc) / 0.6; [[-1, 0], [1, 0.3], [0.3, 1]].forEach(([d], i) => drop(TX + d * (40 + u * 50), 680 - 80 * 4 * u * (1 - u), 9, 900 + i)); }
      // the melon slice, out on the floor, cheers
      slice(405, 712, 80, 910, { face: t > tc ? 'happy' : 'o', rot: t > tc ? Math.sin(t * 10) * 0.08 : 0 });
    },
  });
}

// 10. "And a whole lot of pee."  A queue of water drops marches to the toilet; kid squirms. Iris out on the face.
{
  const t0 = at('And a whole'), tp = end('pee');
  const kid = [
    { t: t0, x: TX, y: SIT, expr: 'love', look: [3, 0] },
    ...A.take(at('whole', 3) - 0.05, { hold: 0.35, mouth: 'wavy', browY: -8 }),
    { t: at('pee') - 0.1, expr: 'shocked', lookAt: [440, 700], ease: 'hold' },
  ];
  // held loop through the breath and the iris: a nervous squirm, sweat on
  for (let t = tp, i = 0; t < VO_END(); t += 3 * D, i++)
    kid.push({ t, lean: i % 2 ? 0.05 : -0.05, sy: i % 2 ? 0.97 : 1.02, ease: 'hold' });
  for (let i = 0; i < 5; i++) cue(at('lot') + i * 0.17, 'tick', 0.5);
  shot(t0, {
    tr: 'iris', iris: [TX, 600],
    cam: [{ t: 0, z: 1.3, x: 290, y: 640 }, { t: VO_END() - t0, z: 1.42, x: 270, y: 640 }],
    draw(lt, t) {
      bathroom(TX);
      drawChar(KID, poseAt(kid, t), { shadow: false });
      bowl(TX);
      for (let i = 0; i < 6; i++) {
        const st = t0 + 0.1 + i * 0.12, x = Math.max(350 + i * 34, 640 - (t - st) * 260), hop = Math.abs(Math.sin((t - st) * 9)) * 12;
        if (t > st) dropGuy(x, 760 - hop, 16, 950 + i * 5, 'happy');
      }
    },
  });
}
