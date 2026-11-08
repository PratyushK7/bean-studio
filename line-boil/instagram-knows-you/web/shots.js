// How Instagram knows what you want. Nine shots timed to the voiceover.

// 1. "You mention shoes once, and suddenly your whole feed is shoes."
{
  const sud = at('suddenly');
  const you = [
    { t: 0, x: 140, y: GY, expr: 'happy', look: [3, -2] },
    ...A.take(sud - 0.1, { hold: 0.5, eyes: 'wide', mouth: 'o' }),
    { t: at('shoes', 2) + 0.1, expr: 'scared', ease: 'hold' },
  ];
  cue(sud, 'zip'); cue(sud + 0.2, 'pop', 0.7); cue(sud + 0.4, 'pop', 0.7);
  shot(0, {
    cam: [{ t: 0, z: 1.04 }, { t: 3.3, z: 1 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      shoeFeed(390, 420, sud, t, 710);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 2. "Is Instagram listening? Instagram says no."
{
  const t0 = at('Is Instagram');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 700] },
    { t: at('listening'), expr: 'thinking', ease: 'hold' },
  ];
  const note = [
    { t: t0, x: 390, y: GY, expr: 'smug', arms: 'hips' },
    { t: at('listening') - 0.1, arms: 'pointUpL', expr: 'curious', ease: 'out' },
    ...A.shake(at('says'), 3),
    { t: at('no') + 0.2, arms: 'hips', expr: 'smug', ease: 'hold' },
  ];
  cue(at('no'), 'pop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 3, z: 1.06 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      drawChar(YOU, poseAt(you, t));
      drawChar(NOTE, poseAt(note, t));
    },
  });
}

// 3. "Instead, it's keeping score."
{
  const t0 = at('Instead');
  const note = [
    { t: t0, x: 270, y: GY, size: 1.1, expr: 'determined', arms: 'hold' },
    ...A.nod(at('keeping'), 2),
    { t: at('score'), expr: 'smug', ease: 'hold' },
  ];
  cue(at('score'), 'pop');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 2, z: 1.08, y: 520 }],
    draw(lt, t) {
      band(YEL, 0, 960, 702);
      ground(GY);
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 720, t > at('score') ? 3 : 0);
    },
  });
}

// 4. "Every like, save, share and comment is a point for that topic."
{
  const t0 = at('Every');
  const you = [
    { t: t0, x: 120, y: GY, expr: 'happy', arms: 'chin' },
    ...A.cheer(at('comment') + 0.1, GY, { height: 18 }),
  ];
  const note = [{ t: t0, x: 400, y: GY, expr: 'determined', arms: 'hold' }];
  const items = [
    [at('like'), 'heart'], [at('save'), 'plus'], [at('share', 1), 'star'], [at('comment'), 'drop'],
  ];
  items.forEach(([ti]) => cue(ti, 'pop', 0.8));
  cue(at('point'), 'ding');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.6, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      let n = 0;
      items.forEach(([ti, kind], i) => {
        const u = (t - ti) / 0.7;
        if (u < 0) return;
        const e = Math.min(1, u);
        const x = lerp(170, 380, e), y = lerp(520, 650, e) - Math.sin(e * Math.PI) * 120;
        if (u < 1) {
          const sx = 170 + 0, p = [x, y];
          if (kind === 'heart') heart(p[0], p[1], 24, 730 + i);
          else if (kind === 'plus') plus(p[0], p[1], 26, 730 + i);
          else if (kind === 'star') star(p[0], p[1], 22, 0, 730 + i);
          else drop(p[0], p[1], 22, 730 + i);
        } else n++;
      });
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 740, Math.min(4, n * 1 + (t > at('point') ? 0 : 0)));
    },
  });
}

// 5. "It also tries to predict whether you'll linger on a post, so lingering is a clue too."
{
  const t0 = at('It also');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 420], arms: 'down' },
    { t: at('lingering'), expr: 'sleepy', ease: 'hold' },
  ];
  const note = [
    { t: t0, x: 400, y: GY, expr: 'curious', arms: 'hold', lookAt: [130, 700] },
    { t: at('clue') - 0.1, expr: 'smug', ease: 'hold' },
  ];
  cue(at('clue'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.04 }, { t: 4.8, z: 1 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      stopwatch(270, 380, 56, t - t0, 750);
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 751, 4 + (t > at('clue') ? 2 : 0));
    },
  });
}

// 6. "Then it spots what lots of people are loving right now, and tests it on you."
{
  const t0 = at('Then');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'neutral', look: [3, -1] },
    ...A.take(at('tests') - 0.1, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
  ];
  const fans = FANS.map((c, i) => [
    { t: t0, x: 270 + (i % 3) * 70 + (i > 2 ? 30 : 0), y: i > 2 ? 400 : 320, size: 0.8, expr: 'happy', arms: 'up', breathe: 2 },
    ...A.cheer(at('loving') + i * 0.12 - 0.3, i > 2 ? 400 : 320, { height: 14 }),
  ]);
  cue(at('loving'), 'sparkle', 0.7); cue(at('tests'), 'whoosh');
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 3.8, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      FANS.forEach((c, i) => { const P = poseAt(fans[i], t); P.y += Math.sin(t * 4 + i) * 4; drawChar(c, P); });
      sneaker(400, 190, 1.3, RED, 760);
      if (t > at('tests')) arrow([330, 440], [170, 620], 761, RED, 0.2);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 7. "Ads can even use your shopping on other sites, if those sites share it."
{
  const t0 = at('Ads');
  const note = [
    { t: t0, x: 130, y: GY, expr: 'curious', arms: 'hold' },
    ...A.nod(at('share', 2), 2),
  ];
  const sw = at('share', 2);
  cue(at('shopping'), 'zip');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 4, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      // a little shop sign on the right
      shape(boxPts(330, 560, 170, 240, 770), RED, 5, 770);
      shape(boxPts(345, 520, 140, 70, 771, 0.04), YEL, 4, 771);
      sneaker(415, 700, 1, BLUE, 772);
      if (t > at('shopping')) {
        const e = Math.min(1, (t - at('shopping')) / 1.0);
        const pts = wavePts(330, 650, lerp(330, 200, e), lerp(650, 700, e), 2, 14, -t * 3);
        if (t > sw) tube(wavePts(330, 650, 200, 700, 2, 14, -t * 3), 7, BLUE, 773);
        else tube(pts, 7, BLUE, 773);
      }
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 774, 6);
    },
  });
}

// 8. "So it's not a mind reader. It's a very patient note-taker."
{
  const t0 = at("So it's");
  const note = [
    { t: t0, x: 380, y: GY, expr: 'smug', arms: 'hold' },
    ...A.shake(at('mind'), 2),
    { t: at("It's", 3), expr: 'happy', ease: 'hold' },
    ...A.nod(at('patient'), 2),
  ];
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 700] },
    { t: at('patient'), expr: 'happy', ease: 'hold' },
  ];
  cue(at('note-taker'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.02 }, { t: 3.4, z: 1.08, x: 300 }],
    draw(lt, t) {
      band(YEL, 0, 960, 702);
      ground(GY);
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 780, 9);
    },
  });
}

// 9. "Makes you wonder what your thumb has been telling it."  Close on the viewer's face.
{
  const t0 = at('Makes');
  const you = [
    { t: t0, x: 270, y: GY, size: 1.1, expr: 'curious', look: [0, 3], arms: 'chin' },
    { t: at('thumb'), expr: 'thinking', ease: 'hold' },
    ...A.think(at('thumb'), VO_END()),
  ];
  shot(t0, {
    tr: 'iris', iris: [270, 690],
    cam: [{ t: 0, z: 1, y: 520 }, { t: 3, z: 1.12, y: 600 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      drawChar(YOU, poseAt(you, t));
    },
  });
}
