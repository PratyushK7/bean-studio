// Does Instagram actually listen to you? Twelve shots timed to the voiceover.

// 1. "You say the word sneakers out loud, and ten minutes later your whole feed is sneakers."
{
  const later = at('later');
  const you = [
    { t: 0, x: 140, y: GY, expr: 'happy', look: [3, -2], arms: 'chin' },
    ...A.take(later - 0.1, { hold: 0.5, eyes: 'wide', mouth: 'o' }),
    { t: at('feed'), expr: 'scared', ease: 'hold' },
  ];
  cue(at('sneakers', 1), 'pop', 0.6);
  cue(later, 'zip'); cue(later + 0.3, 'pop', 0.7); cue(later + 0.5, 'pop', 0.7);
  shot(0, {
    cam: [{ t: 0, z: 1.04 }, { t: 4.8, z: 1 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      shoeFeed(390, 420, later, t, 710);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 2. "So, is Instagram listening to you?" / "Instagram says no."
{
  const t0 = at('So, is');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 700] },
    { t: at('listening'), expr: 'thinking', ease: 'hold' },
  ];
  const note = [
    { t: t0, x: 390, y: GY, expr: 'smug', arms: 'hips' },
    { t: at('listening') - 0.1, arms: 'pointUpL', expr: 'curious', ease: 'out' },
    ...A.shake(at('says no'), 3),
    { t: at('no', 1) + 0.2, arms: 'hips', expr: 'smug', ease: 'hold' },
  ];
  cue(at('no', 1), 'pop');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 3.5, z: 1.06 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      drawChar(YOU, poseAt(you, t));
      drawChar(NOTE, poseAt(note, t));
    },
  });
}

// 3. "Its boss, Adam Mosseri, said in 2025 that secretly recording everyone would drain your battery and light up your microphone indicator."
{
  const t0 = at('Its boss');
  const boss = makeChar({ shape: 'tall', color: RED, size: 1.2, seed: 41, glasses: true, scarf: YEL });
  const note = [
    { t: t0, x: 130, y: GY, expr: 'neutral', arms: 'hold' },
    ...A.take(at('drain') - 0.1, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
  ];
  const b = [
    { t: t0, x: 420, y: GY, expr: 'smug', arms: 'hips' },
    ...A.nod(at('secretly'), 2),
    { t: at('drain'), arms: 'pointUpL', expr: 'determined', ease: 'out' },
  ];
  cue(at('drain'), 'deflate'); cue(at('indicator'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 9, z: 1.06 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      const lvl = t < at('drain') ? 1 : Math.max(0.05, 1 - (t - at('drain')) / 1.0);
      battery(270, 200, lvl, 810);
      mic(270, 350, 0.9, 820, t > at('indicator'));
      drawChar(NOTE, poseAt(note, t));
      drawChar(boss, poseAt(b, t));
    },
  });
}

// 4. "And honestly, it doesn't need to."
{
  const t0 = at('And honestly,');
  const note = [
    { t: t0, x: 270, y: GY, size: 1.1, expr: 'smug', arms: 'hips' },
    ...A.shrug(at("doesn't")),
  ];
  cue(at('need'), 'pop');
  shot(t0, {
    cam: [{ t: 0, z: 1, y: 520 }, { t: 2, z: 1.1, y: 560 }],
    draw(lt, t) {
      band(YEL, 0, 960, 702);
      ground(GY);
      drawChar(NOTE, poseAt(note, t));
    },
  });
}

// 5. "Every like, save, share and comment tells Instagram what you're into."
{
  const t0 = at('Every');
  const you = [
    { t: t0, x: 120, y: GY, expr: 'happy', arms: 'chin' },
    ...A.cheer(at('comment') + 0.1, GY, { height: 18 }),
  ];
  const note = [{ t: t0, x: 400, y: GY, expr: 'determined', arms: 'hold' }];
  const items = [
    [at('like, save'), 'heart'], [at('save,'), 'plus'], [at('share', 1), 'star'], [at('comment'), 'drop'],
  ];
  items.forEach(([ti]) => cue(ti, 'pop', 0.8));
  cue(at('into'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 3.8, z: 1.05 }],
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
          if (kind === 'heart') heart(x, y, 24, 830 + i);
          else if (kind === 'plus') plus(x, y, 26, 830 + i);
          else if (kind === 'star') star(x, y, 22, 0, 830 + i);
          else drop(x, y, 22, 830 + i);
        } else n++;
      });
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 840, Math.min(4, n));
    },
  });
}

// 6. "Instagram says there isn't one single algorithm, just lots of small systems, each one guessing what you'll like."
{
  const t0 = at('Instagram says there');
  const cols = [RED, BLUE, YEL, PAPER];
  const you = [
    { t: t0, x: 270, y: GY, expr: 'curious', lookAt: [270, 400] },
    { t: at('guessing'), expr: 'thinking', ease: 'hold' },
  ];
  cue(at('lots of small'), 'sparkle', 0.6);
  shot(t0, {
    cam: [{ t: 0, z: 1 }, { t: 6.8, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      cols.forEach((c, i) => {
        const on = t > at('lots of small') + i * 0.25;
        if (!on) return;
        const x = 100 + i * 113, y = 330 + Math.sin(t * 3 + i) * 8 + (i % 2) * 70;
        shape(boxPts(x - 38, y - 38, 76, 76, 850 + i, 0.05 * (i % 2 ? 1 : -1)), c, 4, 850 + i);
        miniFace(x, y, 0.8, 0, 860 + i, t > at('guessing') ? 'o' : 'smile', [Math.sin(t + i) * 3, 2]);
      });
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 7. "One of them even predicts whether you'll stop and stare at a post for a few seconds."
{
  const t0 = at('One of them');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 420], arms: 'down' },
    { t: at('stare'), expr: 'sleepy', ease: 'hold' },
  ];
  const note = [
    { t: t0, x: 400, y: GY, expr: 'curious', arms: 'hold', lookAt: [130, 700] },
    { t: at('seconds') - 0.1, expr: 'smug', ease: 'hold' },
  ];
  cue(at('seconds'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.04 }, { t: 4.4, z: 1 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      stopwatch(270, 380, 56, t - t0, 870);
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 871, 4 + (t > at('seconds') ? 2 : 0));
    },
  });
}

// 8. "Then there's the crowd. If lots of people are loving something right now, Instagram can test it on you too, especially in Explore."
{
  const t0 = at("Then there's");
  const you = [
    { t: t0, x: 130, y: GY, expr: 'neutral', look: [3, -1] },
    ...A.take(at('test') - 0.1, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
  ];
  const fans = FANS.map((c, i) => [
    { t: t0, x: 270 + (i % 3) * 70 + (i > 2 ? 30 : 0), y: i > 2 ? 400 : 320, size: 0.8, expr: 'happy', arms: 'up', breathe: 2 },
    ...A.cheer(at('loving') + i * 0.12 - 0.3, i > 2 ? 400 : 320, { height: 14 }),
  ]);
  cue(at('crowd'), 'pop'); cue(at('loving'), 'sparkle', 0.7); cue(at('test'), 'whoosh');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 7.5, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      FANS.forEach((c, i) => { const P = poseAt(fans[i], t); P.y += Math.sin(t * 4 + i) * 4; drawChar(c, P); });
      sneaker(400, 190, 1.3, RED, 880);
      if (t > at('test')) arrow([330, 440], [170, 620], 881, RED, 0.2);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 9. "Advertisers can also share which of their websites you visited, so that shoe shop you browsed last week follows you home."
{
  const t0 = at('Advertisers');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'happy', look: [3, 0] },
    { t: at('follows'), expr: 'sad', ease: 'hold' },
    { t: at('home'), expr: 'scared', ease: 'hold' },
  ];
  const note = [
    { t: t0, x: 270, y: GY, expr: 'curious', arms: 'hold' },
    ...A.nod(at('share', 2), 2),
  ];
  cue(at('visited,'), 'zip'); cue(at('follows'), 'slide_up');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 7, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      shape(boxPts(370, 500, 140, 230, 890), RED, 5, 890);
      shape(boxPts(380, 462, 120, 60, 891, 0.04), YEL, 4, 891);
      sneaker(440, 640, 0.9, BLUE, 892);
      if (t > at('visited,')) tube(wavePts(370, 600, 200, 700, 2, 14, -t * 3), 7, BLUE, 893);
      if (t > at('follows')) {
        const e = Math.min(1, (t - at('follows')) / 1.2);
        sneaker(lerp(440, 170, e), lerp(640, 720, e), 0.9, BLUE, 894);
      }
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 895, 6);
    },
  });
}

// 10. "And your memory helps: you scroll past a hundred ads, then only remember the one that matched your chat."
{
  const t0 = at('And your');
  const you = [
    { t: t0, x: 130, y: GY, expr: 'neutral', look: [3, -2] },
    { t: at('only'), expr: 'curious', ease: 'out' },
    ...A.take(at('matched') - 0.1, { hold: 0.4, eyes: 'wide', mouth: 'o' }),
  ];
  cue(at('hundred'), 'tick'); cue(at('matched'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1 }, { t: 5.8, z: 1.05 }],
    draw(lt, t) {
      band(PAPER, 0, 960, 701);
      ground(GY);
      const cols = [PAPER, BLUE, YEL, PAPER, BLUE, YEL];
      cols.forEach((c, i) => {
        const x = 270 + (i % 3 - 1) * 120, y = 300 + Math.floor(i / 3) * 150;
        const pick = i === 4 && t > at('matched');
        adCard(x, y - (pick ? 12 : 0), pick ? 110 : 90, pick ? 130 : 110, pick ? RED : c, 900 + i);
      });
      if (t > at('matched')) plus(400, 360, 26, 910);
      drawChar(YOU, poseAt(you, t));
    },
  });
}

// 11. "So no, it's not a mind reader. It's a very patient note-taker."
{
  const t0 = at('So no,');
  const note = [
    { t: t0, x: 380, y: GY, expr: 'smug', arms: 'hold' },
    ...A.shake(at('mind'), 2),
    { t: at("It's", 2), expr: 'happy', ease: 'hold' },
    ...A.nod(at('patient'), 2),
  ];
  const you = [
    { t: t0, x: 130, y: GY, expr: 'curious', lookAt: [380, 700] },
    { t: at('patient'), expr: 'happy', ease: 'hold' },
  ];
  cue(at('note-taker'), 'ding');
  shot(t0, {
    tr: 'smear',
    cam: [{ t: 0, z: 1.02 }, { t: 3.8, z: 1.08, x: 300 }],
    draw(lt, t) {
      band(YEL, 0, 960, 702);
      ground(GY);
      drawChar(YOU, poseAt(you, t));
      const a = drawChar(NOTE, poseAt(note, t));
      notebook([a.hands[0][0], a.hands[0][1] - 50], 920, 9);
    },
  });
}

// 12. "Which makes you wonder what your thumb has been saying all day."  Close on the viewer's face.
{
  const t0 = at('Which makes');
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
