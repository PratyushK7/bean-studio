// Thumbnail: said sneakers, saw sneakers. A giant phone shows a red sneaker; a speech bubble from the bean holds the same sneaker.
// Subject test: phone + sneaker in a bubble = "I said it, my phone showed it". Text test: INSTAGRAM HEARD ME? asks, never answers.
CAP.on = false;

function bigSneaker(x, y, s, seed) {
  sneaker(x, y, s, RED, seed);
  line([[x - 38 * s, y + 24 * s], [x + 44 * s, y + 24 * s]], 6, seed + 5, PAPER, 0.6);   // white sole
}

shot(0, {
  draw() {
    paper(YEL);
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[300, 600], [300 + Math.cos(a0) * R, 600 + Math.sin(a0) * R], [300 + Math.cos(a1) * R, 600 + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ffd966');
    }
    gridSafe(() => {
      bigWord('INSTAGRAM', 270, 175, 84, PAPER, 9400);
      bigWord('HEARD ME?', 270, 285, 96, RED, 9410);
      // the giant phone with the shoe on its screen
      shape(boxPts(285, 345, 215, 420, 9300, 0.04), INK, 6, 9300, 1.2);
      shape(boxPts(294, 362, 197, 386, 9301, 0.04), PAPER, 4, 9301);
      bigSneaker(392, 555, 2.0, 9310);
      // speech bubble from the bean, same sneaker inside, dotted line to the phone
      line([[112, 475], [122, 575]], 6, 9320, INK, 0.5, false);
      shape(blobPts(100, 400, 78, 78, 9330, 20, 0.02), PAPER, 7, 9330, 1.2);
      bigSneaker(100, 402, 1.05, 9340);
            // the bean, shocked
      fillOnly(blobPts(130, 905, 120, 13, 9110, 10), BLUE, 9110);
      drawChar(YOU, poseAt([{ t: 0, x: 130, y: 895, size: 1.7, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -12, aR: -0.55, aL: 0.9, bend: -0.4,
        lookAt: [390, 560], fx: ['take'], breathe: 0, blink: false }], 0), { t: 0, shadow: false });
      plus(60, 420, 20, 9240); plus(500, 330, 16, 9241);
    });
  },
});
