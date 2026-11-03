// Thumbnail (build.py thumb): Kit mid-take as Mozzie sips from their arm. Text: JUST ONE SIP?
CAP.on = false;
shot(0, {
  draw(lt, t) {
    paper(RED);
    // darker-red sunburst behind the pair, then a paper blob so the blue bean and yellow mosquito pop
    const cx = 280, cy = 590;
    for (let i = 0; i < 16; i += 2) {
      const a0 = i / 16 * TAU, a1 = (i + 1) / 16 * TAU, R = 900;
      fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 9000 + i, 2, 2), '#ef4b51');
    }
    shape(blobPts(cx, cy, 240, 240, 9100, 18, 0.03), PAPER, 0, 9100);
    // Kit, shocked, arm held out
    const K = poseAt([{ t: 0, x: 165, y: 800, size: 1.6, expr: 'shocked', eyes: 'wide', mouth: 'wavy', brow: -0.7, browY: -14,
      aL: -0.7, aR: 1.95, bend: 0.1, reach: 1.05, sy: 1.06, sx: 0.96, lookAt: [400, 600], fx: ['take', 'sweat'], breathe: 0, blink: false }], 0);
    fillOnly(blobPts(168, 805, 105, 12, 9110, 10), INK, 9110);
    const an = drawChar(KIT, K, { t: 0, shadow: false }), hd = an.hands[1];
    // Mozzie on the hand, smug, nose in
    const M = poseAt([{ t: 0, size: 2.3, facing: -1, expr: 'smug', eyes: 'half', mouth: 'smirk', breathe: 0, blink: false }], 0);
    M.x = hd[0] + 50; M.y = hd[1] - 18;
    drawMoz(MOZ, M, 0, { t: 0, noseAng: 1.2 });
    // the one tiny sip
    drop(hd[0] - 25, hd[1] - 115, 13, 9200, RED);
    burst(hd[0] - 25, hd[1] - 120, 26, 46, 9210, 0);
    // the words
    bigWord('JUST ONE', 270, 180, 104, PAPER, 9400);
    bigWord('SIP?', 270, 300, 120, YEL, 9410);
  },
});
