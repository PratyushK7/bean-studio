// sets.js: ready-made backgrounds, so a long video can change scene with its script instead of repeating one sky and one ground.
// Every set draws the whole background (call it first in draw()), works in a Short (540 x 960) and a long video (960 x 540), uses only the
// channel palette, and RETURNS the ground y, so characters can be placed on it: const gy = setRoom(t, { wall: YEL }); drawChar(MO, poseAt([{ x: 300, y: gy }], t)).
//   setSunny(t)   a daytime outdoors: sky, drifting clouds, hills            the default "out in the world"
//   setNight(t)   dark sky, stars, a moon                                       late hours, worries, mystery, the unknown
//   setRoom(t)    a home: wall, window, picture, floor                          everyday life, habits, sleep, money at home
//   setStreet(t)  buildings, pavement and road                                  towns, shops, crowds, commuting, the economy
//   setStage(t)   curtains, a spotlight, a wooden stage                         a sketch, a demonstration, a verdict, a joke
//   setDesk(t)    a wall with a chart, a desk and a lamp                        work, data, evidence, "the numbers"
//   setSpace(t)   black space, stars, a ringed planet                           big scale, the universe, long odds
//   setBlank(t, color)  one flat colour with a faint sunburst                   diagrams, charts, a label shape and nothing else
// Options: { gy } moves the ground line; setRoom/setStage/setDesk take { wall }, setRoom { floor }, setDesk { chart: false }.
// setScene(name, t, opts) picks one by name. Add your own the same way: band(), ground(), hills(), cloud(), tree(), rock(), moon().

const SET_NAMES = ['sunny', 'night', 'room', 'street', 'stage', 'desk', 'space', 'blank'];
const _dk = c => DEEP || c;                          // a dark theme paints the big background areas deep; a bright theme keeps the set's own colour
function _tint(hex, k = 0.14) {                       // a slightly lighter (or, on dark colours, lighter still) flat tint of a base colour, for the sunburst rays
  const n = parseInt(hex.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255].map(v => Math.round(v + (255 - v) * k));
  return '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
}
const _burst = { [PAPER]: _tint(PAPER, -0.03), [INK]: _tint(INK, 0.1) };
const _floorFill = (y, color, seed) => fillDense(prep([[-30, y], [W + 30, y], [W + 30, H + 400], [-30, H + 400]], true, seed, 1.4, 4), color);

function setSunny(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.8;
  band(o.sky || _dk(BLUE), 0, gy - 40, 12001);
  cloud(W * 0.2 + t * 6, H * 0.17, W * 0.1, W * 0.04, 12011);
  cloud(W * 0.78 - t * 4, H * 0.11, W * 0.07, W * 0.03, 12012);
  hills(gy - 50, 12020);
  ground(gy, 12030);
  return gy;
}

function setNight(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.8;
  paper(INK);
  for (let i = 0; i < 28; i++) {
    if ((i + Math.floor(t * 2)) % 9 === 0) continue;                       // a few stars twinkle off
    const r = 1.5 + rnd(12103, i) * 2.5;
    fillOnly(blobPts(rnd(12101, i) * W, rnd(12102, i) * (gy - 40), r, r, 12110 + i, 6), PAPER, 12110 + i);
  }
  moon(W * 0.82, H * 0.2, Math.min(W, H) * 0.09, 12120);
  ground(gy, 12130, { fill: BLUE, grass: false });
  return gy;
}

function setRoom(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.82;
  paper(o.wall || _dk(YEL));
  _floorFill(gy, o.floor || BLUE, 12201);
  line([[-30, gy], [W / 2, gy + 2], [W + 30, gy - 1]], 4, 12202, INK, 1.2, false);
  const wx = W * 0.12, wy = H * 0.13, ww = Math.min(W * 0.2, H * 0.4), wh = Math.min(H * 0.38, W * 0.4);       // a window
  shape(boxPts(wx, wy, ww, wh, 12210), BLUE, 4, 12210, 1);
  line([[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], 3.4, 12211, INK, 0.6);
  line([[wx, wy + wh / 2], [wx + ww, wy + wh / 2]], 3.4, 12212, INK, 0.6);
  cloud(wx + ww * 0.3 + (t * 2) % 8, wy + wh * 0.26, ww * 0.18, wh * 0.07, 12213);
  const px = W * 0.74, py = H * 0.15, pw = Math.min(W * 0.12, H * 0.22), ph = pw * 1.25;                        // a picture on the wall
  shape(boxPts(px, py, pw, ph, 12220), PAPER, 4, 12220, 1);
  shape(blobPts(px + pw / 2, py + ph * 0.55, pw * 0.3, ph * 0.28, 12221, 8), RED, 2.6, 12221, 0.8);
  return gy;
}

function setStreet(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.72;
  band(_dk(BLUE), 0, gy, 12301);
  const cols = [RED, YEL, PAPER, RED, YEL], bw = W / 4.2;
  for (let i = 0; i < 5; i++) {
    const x = -W * 0.04 + i * bw * 0.98, h = H * (0.34 + 0.14 * rnd(12302, i)), y = gy - h, c = cols[i];
    shape(boxPts(x, y, bw * 0.92, h, 12310 + i), c, 4, 12310 + i, 1);
    for (let r = 0; r < 3; r++) for (let k = 0; k < 2; k++)
      shape(boxPts(x + bw * (0.14 + k * 0.38), y + h * (0.1 + r * 0.28), bw * 0.26, h * 0.16, 12330 + i * 10 + r * 2 + k), c === PAPER ? BLUE : PAPER, 2.6, 12330 + i * 10 + r * 2 + k, 0.8);
  }
  const sw = gy + H * 0.05;
  _floorFill(gy, PAPER, 12390);
  _floorFill(sw, INK, 12391);
  line([[-30, gy], [W / 2, gy + 2], [W + 30, gy]], 4, 12392, INK, 1.2, false);
  for (let x = 20 + ((t * 40) % 90); x < W; x += 90) line([[x, H * 0.91], [x + 44, H * 0.91]], 5, 12400 + (x | 0), PAPER, 0.5, false);
  return gy;
}

function setStage(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.8;
  paper(o.wall || _dk(BLUE));
  const cx = W / 2, cw = W * 0.3;
  fillOnly([[cx - 36, -10], [cx + 36, -10], [cx + cw, gy], [cx - cw, gy]], PAPER, 12501);                    // the spotlight
  ground(gy, 12510, { fill: YEL, grass: false });
  const cur = (s) => {
    const x0 = s < 0 ? -30 : W + 30, x1 = s < 0 ? W * 0.17 : W * 0.83, x2 = s < 0 ? W * 0.12 : W * 0.88;
    shape([[x0, -30], [x1, -30], [x2, gy], [x0, gy]], RED, 4, 12520 + (s < 0 ? 0 : 5), 1.2);
    [0.35, 0.65].forEach((k, i) => line([[x0 + (x1 - x0) * k, 0], [x0 + (x2 - x0) * k, gy]], 3, 12530 + i + (s < 0 ? 0 : 5), INK, 0.8));
  };
  cur(-1); cur(1);
  shape([[-30, -30], [W + 30, -30], [W + 30, H * 0.08], [W * 0.75, H * 0.1], [W * 0.5, H * 0.08], [W * 0.25, H * 0.1], [-30, H * 0.08]], RED, 4, 12540, 1.2);   // valance
  return gy;
}

function setDesk(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.78;
  paper(o.wall || _dk(PAPER));
  if (o.chart !== false) {                                                                                   // a chart on the wall
    const cx = W * 0.2, cy = H * 0.12, cw = Math.min(W * 0.24, H * 0.5), ch = cw * 0.7;
    shape(boxPts(cx, cy, cw, ch, 12601), PAPER, 4, 12601, 1);
    [[0.18, 0.4, BLUE], [0.43, 0.65, YEL], [0.68, 0.85, RED]].forEach(([fx, fh, col], i) => shape(boxPts(cx + cw * fx, cy + ch * (0.9 - fh * 0.8), cw * 0.18, ch * fh * 0.8, 12610 + i), col, 3, 12610 + i, 0.8));
  }
  ground(gy, 12620, { fill: RED, grass: false });                                                            // the desk top and front
  const lx = W * 0.8;                                                                                         // a lamp
  line([[lx, gy], [lx - 8, gy - H * 0.14], [lx + 22, gy - H * 0.26]], 6, 12630, INK, 0.8, false);
  shape([[lx + 4, gy - H * 0.3], [lx + 52, gy - H * 0.27], [lx + 34, gy - H * 0.21], [lx + 10, gy - H * 0.22]], YEL, 3.6, 12631, 1);
  shape(boxPts(W * 0.62, gy - H * 0.07, H * 0.07, H * 0.07, 12640), PAPER, 3.4, 12640, 0.8);                // a mug
  return gy;
}

function setSpace(t = 0, o = {}) {
  const gy = o.gy ?? H * 0.88;
  paper(INK);
  for (let i = 0; i < 34; i++) {
    const r = 1.2 + rnd(12703, i) * 2.4;
    if ((i + Math.floor(t * 1.5)) % 8 !== 0) fillOnly(blobPts(rnd(12701, i) * W, rnd(12702, i) * H, r, r, 12710 + i, 6), PAPER, 12710 + i);
  }
  const px = W * 0.78, py = H * 0.3, pr = Math.min(W, H) * 0.14;
  shape(blobPts(px, py, pr, pr, 12750, 14, 0.02), BLUE, 4, 12750, 1);                                         // a ringed planet
  line([[px - pr * 1.7, py + pr * 0.35], [px, py + pr * 0.1], [px + pr * 1.7, py - pr * 0.3]], 7, 12751, YEL, 0.8, false);
  shape(blobPts(W * 0.18, H * 0.2, pr * 0.28, pr * 0.28, 12752, 10, 0.03), YEL, 3, 12752, 1);
  return gy;
}

function setBlank(t = 0, color = _dk(BLUE)) {
  paper(color);
  const cx = W / 2, cy = H * 0.46, ray = _burst[color] || _tint(color);
  for (let i = 0; i < 24; i += 2) {
    const a0 = i / 24 * TAU, a1 = (i + 1) / 24 * TAU, R = Math.max(W, H) * 1.3;
    fillDense(prep([[cx, cy], [cx + Math.cos(a0) * R, cy + Math.sin(a0) * R], [cx + Math.cos(a1) * R, cy + Math.sin(a1) * R]], true, 12801 + i, 2, 2), ray);
  }
  return H * 0.82;
}

function setScene(name, t = 0, o = {}) {
  const f = { sunny: setSunny, night: setNight, room: setRoom, street: setStreet, stage: setStage, desk: setDesk, space: setSpace }[name];
  if (name === 'blank') return setBlank(t, o.color || o.wall || _dk(BLUE));
  if (!f) throw new Error(`unknown set "${name}": use one of ${SET_NAMES.join(', ')}`);
  return f(t, o);
}
