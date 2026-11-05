// Thumbnail (1280 x 720): the subject is the coffee and the caffeine in it. A wired red caffeine bean peeks out of a big white mug that
// wears the CLOSED sign, against a full moon and a clock at midnight, on a flat blue night. The words, "3 PM -> MIDNIGHT", sit in the
// left third; nothing important goes in the bottom-right corner (the duration badge).
CAP.on = false;

shot(0, {
  draw(lt, t) {
    paper(BLUE);
    for (let i = 0; i < 22; i++) { const r = 1.8 + rnd(9401, i) * 2.4; fillOnly(blobPts(rnd(9402, i) * W, rnd(9403, i) * H * 0.9, r, r, 9410 + i, 6), PAPER, 9410 + i); }
    shape(blobPts(660, 170, 135, 135, 9420, 16, 0.02), YEL, 4.4, 9420, 1);          // the full moon behind the bean
    clockFace(885, 95, 60, 12, 9430);
    for (let i = 0; i < 3; i++) line(wavePts(560 + i * 100, 250, 572 + i * 100, 150, 1.2, 9, i * 2), 5, 9440 + i, PAPER);
    // the bean in the mug: the bean first, then the mug's front over its lower half
    drawChar(CAF, Object.assign(poseAt([{ t: 0 }], 0), { x: 660, y: 302, size: 2.35, eyes: 'wide', mouth: 'grin', brow: -0.4, browY: -10, look: [-3, 0], arms: 'up', fx: 'take', breathe: 0, blink: false }), { shadow: false });
    mug(660, 500, 6.0, 9450, { color: PAPER });
    closedSign(660, 330, 2.2, 9460, -0.05);
    // the words: 3 PM, an arrow down, MIDNIGHT
    bigWord('3 PM', 205, 150, 128, YEL, 9470);
    tube([[205, 205], [210, 250], [205, 292]], 10, PAPER, 9480);
    line([[172, 258], [205, 300], [238, 258]], 11, 9481, INK, 1, false);
    bigWord('MIDNIGHT', 230, 395, 86, PAPER, 9490);
  },
});
