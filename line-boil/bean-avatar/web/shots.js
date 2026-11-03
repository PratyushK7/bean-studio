// three avatar backgrounds: blue, yellow, paper
const POSE = { x: 262, y: 610, scarf: -22, expr: 'smug', eyes: 'half', brow: 0.7, browY: -2, mouth: 'smirk', arms: 'chin', look: [2.5, -3.5], breathe: 0, blink: false };
const KEYS = [Object.assign({ t: 0 }, POSE)];
[[BLUE, PAPER], [YEL, PAPER], [PAPER, YEL]].forEach(([bg, glow], i) => {
  shot(i, {
    draw(lt, t) {
      paper(bg);
      if (bg !== BLUE) shape(blobPts(270, 370, 255, 255, 7000 + i, 18, 0.02), bg === PAPER ? BLUE : PAPER, 0, 7000 + i);
      fillOnly(blobPts(270, 616, 110, 13, 7010, 10), bg === BLUE ? INK : BLUE, 7010);
      drawChar(BEAN, poseAt(KEYS, t), { shadow: false });
      badBulb(300, 235, 38, 7020, glow === YEL && bg === PAPER ? PAPER : glow);
    },
  });
});
