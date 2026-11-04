// Thumbnail: the subject first. An X-ray bubble of the bean's belly holds a huge chewed gum wad, a stick of gum names it.
// Subject test: the picture alone says "gum in a stomach". Text test: STUCK INSIDE? points at the claim, without repeating the title.
CAP.on = false;

function gumWad(x, y, r, seed) {
  shape(blobPts(x, y, r, r * 0.84, seed, 11, 0.14), RED, 6, seed, 1.4);
  line([[x - r * 0.62, y - r * 0.02], [x - r * 0.3, y + r * 0.12], [x - r * 0.62, y + r * 0.3]], 5, seed + 1, INK, 0.6);   // bite marks
  line([[x - r * 0.62, y - r * 0.32], [x - r * 0.34, y - r * 0.2], [x - r * 0.62, y - r * 0.06]], 5, seed + 2, INK, 0.6);
  line([[x + r * 0.28, y - r * 0.55], [x + r * 0.56, y - r * 0.28]], 7, seed + 3, PAPER, 0.5);                            // shine
  miniFace(x + r * 0.12, y + r * 0.08, r / 36, 0, seed + 4, 'smile');                                                      // smug
}
function gumStick(x, y, w, h, rot, seed) {
  shape(boxPts(x - w / 2, y - h / 2, w, h, seed, rot), PAPER, 5, seed, 1.2);
  [-0.32, 0, 0.32].forEach((k, i) => {
    const c = Math.cos(rot), sn = Math.sin(rot);
    line([[x + k * w * c - h * 0.34 * -sn * -1, y + k * w * sn + h * 0.34 * c], [x + k * w * c + h * 0.34 * -sn * -1, y + k * w * sn - h * 0.34 * c]], 5, seed + 10 + i, YEL, 0.5);
  });
}

shot(0, {
  draw() {
    paper(YEL);
    // a lighter sunburst and a paper blob, so the bean and the bubble pop off the yellow
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[300, 600], [300 + Math.cos(a0) * R, 600 + Math.sin(a0) * R], [300 + Math.cos(a1) * R, 600 + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ffd966');
    }
    gridSafe(() => {
    // the words, top third: the stakes, not the title
    bigWord('STUCK', 270, 175, 124, PAPER, 9400);
    bigWord('INSIDE?', 270, 295, 108, RED, 9410);
    // the bean, big, hand on belly, staring at the bubble
    fillOnly(blobPts(130, 905, 120, 13, 9110, 10), BLUE, 9110);
    drawChar(YOU, poseAt([{ t: 0, x: 130, y: 895, size: 1.7, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -12, aR: -0.55, aL: 0.9, bend: -0.4,
      lookAt: [330, 560], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0), { t: 0, shadow: false });
    // the X-ray bubble from the belly
    line([[175, 700], [235, 585]], 6, 9200, INK, 0.5, false); line([[160, 760], [190, 690]], 6, 9201, INK, 0.5, false);
    shape(blobPts(330, 520, 180, 180, 9210, 20, 0.02), PAPER, 7, 9210, 1.2);
    gumWad(330, 525, 125, 9220);
    // a stick of gum, so there is no doubt what it is
    gumStick(440, 835, 150, 70, -0.35, 9230);
    plus(70, 460, 22, 9240); plus(490, 380, 18, 9241); plus(95, 590, 14, 9242);
    });
  },
});
