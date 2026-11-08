// Thumbnail: WHY PRICES END IN .99, a giant 3.99 tag and a shopper doing a take.
CAP.on = false;
shot(0, {
  draw() {
    band(YEL, 0, 960, 500);
    burst(270, 480, 120, 700, 501, 0);
    gridSafe(() => {
      bigWord('WHY PRICES', 270, 230, 92, PAPER, 510);
      bigWord('END IN .99?', 270, 330, 92, PAPER, 520);
      priceTag(270, 520, '3', '.99', 530, { s: 1.5, fill: RED, hi: true, rot: -0.05 });
      drawChar(SHOPPER, poseAt([{ t: 0, x: 270, y: 800, size: 1.1, expr: 'shocked', eyes: 'wide', mouth: 'o', fx: ['take'], lookAt: [270, 520] }], 0));
    });
  },
});
