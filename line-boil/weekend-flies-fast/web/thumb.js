// Thumbnail: a huge clock with a worried bean, calendar-style "Sat" and "Sun" tags racing past it.
// Subject test: a giant clock beside a stunned bean says "time". Text test: WEEKEND GONE? names the topic and the stakes.
CAP.on = false;

shot(0, {
  draw() {
    paper(BLUE);
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[300, 620], [300 + Math.cos(a0) * R, 620 + Math.sin(a0) * R], [300 + Math.cos(a1) * R, 620 + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#2e92d3');
    }
    gridSafe(() => {
      bigWord('WEEKEND', 270, 175, 112, YEL, 9400);
      bigWord('GONE?', 270, 295, 112, PAPER, 9410);
      // the giant clock, hands whirling, speed lines either side
      clockProp(320, 540, 190, 0.6, 3.6, 9100, 'o');
      speedLines(320, 540, [-1, 0], 90, 150, 9120);
      // the bean, big, take-face
      fillOnly(blobPts(135, 905, 120, 13, 9110, 10), INK, 9110);
      drawChar(YOU, poseAt([{ t: 0, x: 135, y: 895, size: 1.7, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -12, aR: -0.55, aL: 0.9, bend: -0.4,
        lookAt: [320, 540], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0), { t: 0, shadow: false });
      plus(480, 400, 20, 9240); plus(70, 470, 16, 9241);
    });
  },
});
