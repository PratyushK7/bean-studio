// Thumbnail: YOU, wide-eyed, next to a smug gum lump. Text: NOPE.
CAP.on = false;
{
  const you = [{ t: 0, x: 190, y: 840, size: 1.25, expr: 'shocked', eyes: 'wide', mouth: 'o', fx: ['take'], look: [4, 0] }];
  const gum = [{ t: 0, x: 410, y: 800, size: 1.55, expr: 'smug', arms: 'hips', facing: -1 }];
  shot(0, {
    draw() {
      paper(YEL);
      fillOnly(blobPts(270, 560, 250, 230, 901, 10, 0.12), PAPER, 901);
      bigWord('NOPE', 270, 260, 120, PAPER, 910);
      drawChar(YOU, poseAt(you, 0));
      drawChar(GUM, poseAt(gum, 0));
      plus(80, 420, 22, 920); plus(470, 400, 18, 921);
    },
  });
}
