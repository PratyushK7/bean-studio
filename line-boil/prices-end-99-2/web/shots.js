// Why do prices end in .99? Twelve shots, timed to the voiceover with at('word').

musicMood(0, 'playful', 1);
musicMood(at('Turns out'), 'curious', 1);
musicMood(at('Studies'), 'calm', 1);
musicMood(at('But the lamp'), 'serious', 1);
musicMood(at('So read'), 'upbeat', 1);
musicMood(at('Now'), 'mystery', 1);

// 1. "Why does your brain think 3.99 is three dollars?"  Shopper stares at the tag, Brain thinks.
{
  const tag = [270, 300];
  const sh = [
    { t: 0, x: 140, y: GY, lookAt: tag, expr: 'curious' },
    ...A.take(at('three', 1) - 0.2, { hold: 0.5, mouth: 'o' }),
  ];
  const br = [
    { t: 0, x: 410, y: 640, expr: 'thinking', lookAt: tag, fx: 'think' },
    { t: at('three', 1) - 0.1, expr: 'smug', ease: 'hold' },
  ];
  shot(0, {
    cam: [{ t: 0, z: 1.04 }, { t: 3.3, z: 1 }],
    draw(lt, t) {
      shopSet(t);
      priceTag(tag[0], tag[1], '3', '.99', 50, { s: 1.15 });
      drawChar(SHOPPER, poseAt(sh, t));
      const P = poseAt(br, t); P.y += Math.sin(t * 3) * 6; drawChar(BRAIN, P);
    },
  });
}

// 2. "A shopkeeper prices a lamp at four dollars, and sells none."  Empty shop, SOLD 0.
{
  const t0 = at('A shopkeeper');
  const sk = [
    { t: t0, x: 440, y: GY, expr: 'neutral', lookAt: [130, 400] },
    { t: at('none') - 0.1, expr: 'sad', ease: 'hold' },
    ...A.sigh(at('none')),
  ];
  cue(t0 + 0.4, 'zip');
  shot(t0, {
    tr: 'cut',
    cam: [{ t: 0, z: 1 }, { t: 3.4, z: 1.06, x: 270, y: 500 }],
    draw(lt, t) {
      shopSet(t);
      lamp(150, GY - 6, 1.5, 60);
      priceTag(150, 300, '4', '.00', 61, { s: 0.95 });
      soldSign(380, 190, 0, 62);
      drawChar(SHOP, poseAt(sk, t));
    },
  });
}

// 3. "So he drops it one cent, to 3.99, and sells a pile."  The tag flips, the crowd arrives, SOLD 99.
{
  const t0 = at('So he drops'), tf = at('one cent', 1) + 0.65, ts = at('sells', 2);
  const sk = [
    { t: t0, x: 440, y: GY, expr: 'sad', lookAt: [130, 400] },
    { t: tf, expr: 'curious', ease: 'hold' },
    ...A.cheer(ts + 0.2, GY, { height: 24 }),
  ];
  const home = [[215, GY], [260, GY], [305, GY], [235, GY - 45], [280, GY - 45], [325, GY - 45]];
  const crowd = home.map(([x, y], i) => [
    { t: tf, x: 640 + i * 30, y, expr: 'happy', size: 0.95 },
    ...A.dash(tf + 0.3 + i * 0.1, 640 + i * 30, x, y, { endExpr: 'happy' }),
    { t: ts + 1.2, expr: 'love', ease: 'hold' },
  ]);
  cue(tf, 'pop'); cue(ts, 'zip'); cue(ts + 0.5, 'ding', 0.7);
  for (let i = 0; i < 4; i++) cue(ts + 0.8 + i * 0.12, 'pop', 0.4);
  shot(t0, {
    cam: [{ t: 0, z: 1.04 }, { t: 3.7, z: 1 }],
    draw(lt, t) {
      shopSet(t);
      lamp(150, GY - 6, 1.5, 60);
      const u = (t - tf) / 0.3, flip = Math.abs(u) < 1 ? Math.abs(u) : 1;
      const sx = t < tf - 0.3 ? 1 : (t > tf + 0.3 ? 1 : flip);
      const after = t >= tf;
      priceTag(150, 300, after ? '3' : '4', after ? '.99' : '.00', 61, { s: 0.95, sx: Math.max(0.05, sx) });
      soldSign(380, 190, t > ts + 0.5 ? 99 : 0, 62);
      crowd.forEach((k, i) => { if (t > tf) drawChar(CUST[i], poseAt(k, t)); });
      drawChar(SHOP, poseAt(sk, t));
    },
  });
}

// 4. "One cent. That is the trick."  Two tags and one coin between them.
{
  const t0 = at('One cent', 2);
  const sk = [
    { t: t0, x: 270, y: GY, size: 0.95, expr: 'smug', lookAt: [270, 330] },
    ...A.nod(at('That is') , 1),
  ];
  cue(t0 + 0.4, 'ding', 0.8);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 2, z: 1.05, y: 480 }],
    draw(lt, t) {
      shopSet(t);
      priceTag(125, 300, '4', '.00', 70, { s: 0.76 });
      priceTag(415, 300, '3', '.99', 71, { s: 0.76 });
      const bob = Math.sin(t * 6) * 4;
      if (t > t0 + 0.2) { coin(270, 300 + bob, 30, 72); arrow([180, 395], [360, 395], 73, INK, 0.12); }
      drawChar(SHOP, poseAt(sk, t));
    },
  });
}

// 5. "Turns out, your brain reads a price left to right, and mostly stops at the first digit."
{
  const t0 = at('Turns out'), tl = at('left', 1), tr = at('right'), tf = at('first');
  const sh = [
    { t: t0, x: 150, y: GY, size: 0.95, expr: 'curious', lookAt: [300, 300] },
    { t: tl, lookAt: [270, 320], ease: 'hold' },
    { t: tl + 0.5, lookAt: [440, 320], ease: 'lin' },
    { t: tf, lookAt: [300, 300], expr: 'determined', ease: 'hold' },
  ];
  cue(tl, 'slide_up', 0.5); cue(tf, 'pop');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 4.2, z: 1.08, x: 300, y: 480 }],
    draw(lt, t) {
      shopSet(t);
      priceTag(360, 300, '3', '.99', 80, { s: 1.15, hi: t > tf });
      if (t > tl) arrow([250, 430], [Math.min(470, 250 + (t - tl) * 330), 430], 81, INK, 0.1);
      drawChar(SHOPPER, poseAt(sh, t));
    },
  });
}

// 6. "Four dollars looks like a four. Three ninety-nine looks like a three."
{
  const t0 = at('Four dollars', 2), t3 = at('three', 2);
  const sh = [
    { t: t0, x: 270, y: GY, size: 1.15, expr: 'neutral', lookAt: [130, 300] },
    { t: t3 - 0.1, lookAt: [410, 300], ease: 'hold' },
    { t: at('three', 3) , expr: 'curious', ease: 'hold' },
  ];
  cue(t0, 'pop', 0.6); cue(t3, 'pop', 0.6);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.02 }, { t: 4.2, z: 1 }],
    draw(lt, t) {
      shopSet(t);
      priceTag(130, 290, '4', '.00', 90, { s: 0.85, hi: t > t0 + 0.4 });
      priceTag(410, 290, '3', '.99', 91, { s: 0.85, hi: t > t3 + 0.2 });
      drawChar(SHOPPER, poseAt(sh, t));
    },
  });
}

// 7. "So your brain rounds it down, and the cheaper-feeling number wins."
{
  const t0 = at('So your brain'), tr = at('rounds'), tw = at('wins');
  const br = [
    { t: t0, x: 270, y: 690, size: 1.25, expr: 'thinking', lookAt: [270, 300] },
    ...A.take(tr - 0.25, { hold: 0.3, mouth: 'o' }),
    { t: tw - 0.1, expr: 'smug', eyes: 'half', ease: 'hold' },
  ];
  cue(tr + 0.1, 'slide_down', 0.8); cue(tw, 'sparkle');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.6, z: 1.06, y: 500 }],
    draw(lt, t) {
      shopSet(t);
      const k = t < tr ? 1 : Math.max(0, 1 - (t - tr) / 0.5);
      priceTag(270, 290, '3', '.99', 100, { s: 1.1, restK: k, hi: t > tr + 0.5 });
      priceTag(95, 400, '4', '.00', 101, { s: 0.42, rot: -0.2 });
      if (t > tr + 0.1 && t < tr + 0.6) arrow([300, 380], [300, 450], 102, INK, 0.1);
      const P = poseAt(br, t); P.y += Math.sin(t * 3) * 7; drawChar(BRAIN, P);
    },
  });
}

// 8. "Studies find that prices just under a round number tend to sell more than one cent should explain."
{
  const t0 = at('Studies'), tb = at('tend'), tc = at('cent', 3);
  const sc = [
    { t: t0, x: 110, y: GY, expr: 'curious', lookAt: [380, 600] },
    ...A.point(at('find'), 'R', { ang: 1.2, mouth: 'open' }),
    { t: tb, expr: 'happy', ease: 'hold' },
  ];
  cue(t0 + 0.2, 'zip'); cue(tb, 'slide_up', 0.8); cue(tc, 'pop');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 5.6, z: 1.04, x: 285 }],
    draw(lt, t) {
      shopSet(t);
      const h1 = Math.min(1, (t - t0 - 0.3) / 0.5), h2 = Math.max(0, Math.min(1, (t - tb) / 0.9));
      const base = 700;
      line([[240, base + 4], [500, base + 6]], 4, 110);
      line([[240, base + 4], [240, 330]], 4, 111);
      if (h1 > 0) shape(boxPts(275, base - 110 * h1, 70, 110 * h1, 112), BLUE, 3.5, 112);
      if (h2 > 0) shape(boxPts(375, base - 260 * h2, 70, 260 * h2, 113), RED, 3.5, 113);
      priceTag(310, 760, '4', '.00', 114, { s: 0.3 });
      priceTag(410, 760, '3', '.99', 115, { s: 0.3 });
      if (t > tc) coin(470, 345, 22, 116);
      drawChar(SCI, poseAt(sc, t));
    },
  });
}

// 9. "But the lamp is still worth about four dollars."  Same lamp, four coins.
{
  const t0 = at('But the lamp');
  const cts = [at('worth', 1) + 0.05, at('about') + 0.05, at('four dollars', 3) - 0.05, at('four dollars', 3) + 0.4];
  cts.forEach(t => cue(t, 'pop', 0.7));
  cue(t0, 'squeak', 0.7);
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.05 }, { t: 2.6, z: 1, x: 270 }],
    draw(lt, t) {
      shopSet(t);
      lamp(150, GY - 6, 1.7, 120);
      priceTag(165, 250, '3', '.99', 121, { s: 0.7 });
      miniFace(150, GY - 6 - 1.7 * 150, 1.1, 0, 122, t < t0 + 0.6 ? 'o' : 'smile');
      cts.forEach((tc, i) => { if (t > tc) coin(400, GY - 40 - i * 52, 38, 123 + i); });
    },
  });
}

// 10. "So read the left digit, then ask what it is really worth."
{
  const t0 = at('So read'), tl = at('left', 2), ta = at('ask'), tw = at('worth', 2);
  const sh = [
    { t: t0, x: 130, y: GY, size: 1.2, expr: 'determined', lookAt: [390, 300] },
    ...A.point(tl - 0.2, 'R', { ang: 1.0, mouth: 'open' }),
    ...A.think(ta, tw - 0.1),
    { t: tw, expr: 'happy', lookAt: [400, 600], ease: 'hold' },
  ];
  cue(tl, 'ding', 0.8); cue(ta, 'pop'); cue(tw, 'sparkle');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.4, z: 1.06, x: 300 }],
    draw(lt, t) {
      shopSet(t);
      if (t < ta) {
        priceTag(390, 300, '3', '.99', 130, { s: 1.15, hi: t > tl });
        if (t > tl) arrow([300, 400], [300, 340], 131, YEL, 0.1);
      } else {
        priceTag(430, 220, '3', '.99', 130, { s: 0.55 });
        lamp(390, GY - 6, 1.2, 132);
        const n = Math.min(4, Math.floor((t - ta) / 0.4) + 1);
        for (let i = 0; i < n; i++) coin(490 - 0, GY - 40 - i * 40, 28, 133 + i);
        if (t > tw - 0.3) plus(330, 560, 14, 138);
      }
      drawChar(SHOPPER, poseAt(sh, t));
    },
  });
}

// 11. "The shopkeeper knows. He still sells lamps at 3.99."  Callback.
{
  const t0 = at('The shopkeeper'), tk = at('knows'), tl = at('lamps');
  const sk = [
    { t: t0, x: 280, y: GY, size: 1.3, expr: 'neutral' },
    { t: tk - 0.1, expr: 'smug', arms: 'hips', ease: 'hold' },
    ...A.nod(tl, 1),
  ];
  const cu = [
    { t: t0, x: 450, y: GY, expr: 'happy', lookAt: [280, 600] },
    ...A.cheer(tl - 0.1, GY, { height: 22 }),
  ];
  cue(tl, 'ding', 0.8);
  shot(t0, {
    tr: 'cut',
    cam: [{ t: 0, z: 1.02 }, { t: 3.5, z: 1 }],
    draw(lt, t) {
      shopSet(t);
      lamp(95, GY - 6, 1.3, 140);
      priceTag(95, 330, '3', '.99', 141, { s: 0.6 });
      drawChar(SHOP, poseAt(sk, t));
      drawChar(CUST[0], poseAt(cu, t));
    },
  });
}

// 12. "Now, what does a price ending in zero say?"  Closing hook; iris on the shopper.
{
  const t0 = at('Now');
  const sh = [
    { t: t0, x: 270, y: GY, size: 1.45, expr: 'curious', lookAt: [270, 300] },
    ...A.think(t0 + 0.2, VO_END()),
  ];
  const br = [{ t: t0, x: 450, y: 620, size: 1.1, expr: 'smug', lookAt: [270, 300] }];
  cue(t0 + 0.3, 'zip');
  shot(t0, {
    tr: 'iris', iris: [270, 690],
    cam: [{ t: 0, z: 1 }, { t: 3.4, z: 1.06, y: 500 }],
    draw(lt, t) {
      shopSet(t);
      priceTag(270, 280, '4', '.00', 150, { s: 1.15, rot: Math.sin(t * 2) * 0.03 });
      drawChar(SHOPPER, poseAt(sh, t));
      const P = poseAt(br, t); P.y += Math.sin(t * 3) * 6; drawChar(BRAIN, P);
    },
  });
}
