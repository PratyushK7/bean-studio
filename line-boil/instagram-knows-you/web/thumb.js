// Thumbnail: a giant phone full of shoes, the viewer shocked, the note-taker peeking.
CAP.on = false;
shot(0, {
  draw() {
    band(YEL, 0, 960, 901);
    burst(270, 520, 160, 520, 902, 0);
    gridSafe(() => {
      phone(270, 520, 300, 470, 910);
      [[-95, 'RED'], [0, 'YEL'], [95, 'BLU']].forEach(([dy, c], i) => sneaker(270, 520 + dy * 1.2, 2, [RED, YEL, BLUE][i], 920 + i));
      drawChar(YOU, poseAt([{ t: 0, x: 100, y: 800, size: 1.0, expr: 'shocked', fx: ['take'], arms: 'up' }], 0));
      bigWord('SO MANY', 270, 215, 105, PAPER, 930);
      bigWord('SHOES?', 270, 330, 118, YEL, 931);
    });
  },
});
