// main.js: the clock, shots, camera, transitions and sound cues. Loaded last.
// 24 fps, animated on twos: every drawing is held for 2 frames and every line boils through 3 variants.
const FPS = 24;
let NOW = 0, DRAWING = 0;
const SHOTS = [];
const CUES = [];

// ---------- voiceover word times ----------
const _norm = w => String(w).toLowerCase().replace(/[^a-z0-9']/g, '').replace(/'/g, '');
// at('word' | 'two words', nth = 1): start time of the nth occurrence in the voiceover. end(...) gives its end.
// Matching ignores case and punctuation. A phrase that occurs more than once needs nth (or more words), or
// the first match is used with a warning: at('blue') would find "the sky is blue" long before "Blue light has".
function _find(phrase, nth) {
  const ws = phrase.split(/\s+/).map(_norm).filter(Boolean), hits = [];
  for (let i = 0; i + ws.length <= WORDS.length; i++) {
    if (ws.every((w, k) => _norm(WORDS[i + k].w) === w)) hits.push(i);
  }
  if (nth === undefined && hits.length > 1) console.warn(`at("${phrase}") occurs ${hits.length} times (at ${hits.map(i => WORDS[i].s.toFixed(2)).join(', ')}s); using the first. Pass nth or a longer phrase.`);
  const i = hits[(nth || 1) - 1];
  if (i === undefined) throw new Error(`"${phrase}" #${nth || 1} is not in the voiceover (web/words.js)`);
  return [i, i + ws.length - 1];
}
function at(phrase, nth) { return WORDS[_find(phrase, nth)[0]].s; }
function end(phrase, nth) { return WORDS[_find(phrase, nth)[1]].e; }
// The ending breathes: after the last word, hold the final pose (BREATH), close the iris (IRIS_CLOSE), then sit on black (IRIS_HOLD).
// A long video then opens the channel outro out of that black. A Short has no outro, so its tail is tighter (0.6 + 0.8 + 0.2 = 1.6 s,
// not 2.3 s): it still closes on the hero's face, but does not sit on a dead screen. VO_DUR comes from build.py voice.
const BREATH = WIDE ? 1.0 : 0.6, IRIS_CLOSE = WIDE ? 1.0 : 0.8, IRIS_HOLD = WIDE ? 0.3 : 0.2;
const TAIL = BREATH + IRIS_CLOSE + IRIS_HOLD;
const VO_END = () => (typeof VO_DUR !== 'undefined' ? VO_DUR + TAIL
  : typeof END !== 'undefined' ? END : (WORDS.length ? WORDS[WORDS.length - 1].e + TAIL : 4));
const IRIS_START = () => VO_END() - IRIS_CLOSE - IRIS_HOLD;

// ---------- captions ----------
// Burned-in captions in the channel lettering: 1 to 3 words at a time, the spoken word lit yellow, each chunk
// popping in. They sit in the centre band (y 500, about 52% down): where the eye already is, and clear of the
// Shorts overlay at the bottom. A shot can move them with cap: 'top' or a y value, or hide them with cap: false.
// A long video (16:9) has NO burned-in captions by default (the industry standard: viewers use YouTube's own closed captions, and the .srt
// is uploaded for that). Set CAP.on = true in cast.js to add them; they then sit in the bottom band (y H-64), smaller, up to 5 words.
const CAP = WIDE ? { on: false, y: H - 64, topY: 70, size: 30, max: 5, chars: 34, edge: 200 } : { on: true, y: 500, topY: 150, size: 37, max: 3, chars: 16, edge: 70 };
const CAPFONT = new FontFace('CapFont', 'url(engine/Poppins-Bold.ttf)', { weight: '700' });
document.fonts.add(CAPFONT);
CAPFONT.load().catch(() => {});
const capText = w => String(w).toUpperCase().replace(/[^A-Z0-9'%-]/g, '').replace(/^-+|-+$/g, '');
let _caps = null;
function captionChunks() {
  if (_caps) return _caps;
  _caps = [];
  if (typeof WORDS === 'undefined' || !WORDS.length) return _caps;
  let cur = [];
  const flush = () => { if (cur.length) _caps.push(cur); cur = []; };
  WORDS.forEach((w, i) => {
    const txt = capText(w.w);
    if (!txt) return;
    const len = cur.reduce((a, c) => a + c.txt.length + 1, 0) + txt.length;
    if (cur.length >= CAP.max || (cur.length && len > CAP.chars)) flush();
    cur.push({ txt, s: w.s, e: w.e, i });
    if (/[.,!?;:]["')]*$/.test(w.w)) flush();   // never run a chunk across a pause
  });
  flush();
  _caps.forEach((c, k) => {
    const nx = _caps[k + 1], last = c[c.length - 1];
    c.s = c[0].s;
    c.e = nx ? Math.min(nx[0].s, last.e + 0.45) : last.e + 0.45;
  });
  return _caps;
}
function drawCaptions(t, s) {
  if (!CAP.on || s.cap === false) return;
  const c = captionChunks().find(c => t >= c.s - 1e-6 && t < c.e);
  if (!c) return;
  const y = typeof s.cap === 'number' ? s.cap : s.cap === 'top' ? CAP.topY : CAP.y;
  const pop = EASE.back(clamp((t - c.s) / (2 * D) + 0.35, 0, 1));
  ctx.save();
  let size = CAP.size;
  ctx.font = `700 ${size}px CapFont, sans-serif`;
  // each word gets a slot 10% wider than itself (room to grow when spoken) plus a gap that never shrinks below 16
  const GROW = 1.1, gapOf = sz => Math.max(16, sz * 0.5);
  let ws = c.map(w => ctx.measureText(w.txt).width);
  let total = ws.reduce((a, b) => a + b * GROW, 0) + gapOf(size) * (c.length - 1);
  if (total > W - CAP.edge) {
    const k = (W - CAP.edge - 16 * (c.length - 1)) / (total - gapOf(size) * (c.length - 1));
    size *= k; ws = ws.map(v => v * k);
    ctx.font = `700 ${size}px CapFont, sans-serif`;
    total = ws.reduce((a, b) => a + b * GROW, 0) + gapOf(size) * (c.length - 1);
  }
  const gap = gapOf(size);
  ctx.lineJoin = 'round';
  let x = W / 2 - total / 2;
  c.forEach((w, k) => {
    const active = t >= w.s - 1e-6 && (k === c.length - 1 || t < c[k + 1].s);
    const rot = (rnd(w.i, 7) - 0.5) * 0.09 + (hash(w.i, V, 61) - 0.5) * 0.035;
    ctx.save();
    ctx.translate(x + ws[k] * GROW / 2, y + (rnd(w.i, 8) - 0.5) * 4);
    ctx.rotate(rot);
    ctx.scale(pop * (active ? 1.08 : 1), pop * (active ? 1.08 : 1));
    ctx.lineWidth = size * 0.2; ctx.strokeStyle = INK; ctx.strokeText(w.txt, -ws[k] / 2, size * 0.35);
    ctx.fillStyle = INK; ctx.fillText(w.txt, -ws[k] / 2 + size * 0.04, size * 0.4);
    ctx.fillStyle = active ? YEL : PAPER; ctx.fillText(w.txt, -ws[k] / 2, size * 0.35);
    ctx.restore();
    x += ws[k] * GROW + gap;
  });
  ctx.restore();
}

// ---------- sound ----------
// musicMood(t, mood, gain): the music follows the script. From second t the underscore changes to that mood (a 1 to 1.6 s crossfade) until the next
// musicMood call. Moods: curious (the default), playful, upbeat, calm, serious, tense, mystery, triumphant, silent. Call it at each chapter start and at
// each turn in the feeling; 'silent' for a pause or a punchline, then a mood again after it.
function musicMood(t, mood, gain = 1) { CUES.push({ t: Math.round(t * 1000) / 1000, kind: 'music:' + mood, gain }); }
// cue(t, kind, gain): kinds are whoosh boing pop thud squeak sparkle zip plop tick slide_up slide_down deflate ding drum
function cue(t, kind, gain = 1) { CUES.push({ t: Math.round(t * 1000) / 1000, kind, gain }); }

// ---------- shots ----------
// shot(start, {draw(lt, t), cam: [{t, x, y, z, r, shake}], tr: 'cut' | 'smear' | 'iris', iris: [x, y]})
// A shot runs until the next shot starts. lt = seconds into the shot, t = voiceover seconds. cam keys use lt.
function shot(start, def) { def.start = start; SHOTS.push(def); return def; }

const CAM0 = { x: W / 2, y: H / 2, z: 1, r: 0, shake: 0 };
function applyCam(s, lt) {
  const c = s.cam ? track(s.cam, lt, CAM0) : CAM0;
  let ox = 0, oy = 0;
  if (c.shake) { ox = (hash(DRAWING, 1, 5) - .5) * 2 * c.shake; oy = (hash(DRAWING, 2, 5) - .5) * 2 * c.shake; }
  ctx.translate(W / 2 + ox, H / 2 + oy);
  ctx.scale(c.z, c.z);
  ctx.rotate(c.r);
  ctx.translate(-c.x, -c.y);
}

// an iris that closes on a point, with a boiling hand-cut edge
function iris(x, y, r) {
  const pts = blobPts(x, y, Math.max(1, r), Math.max(1, r), 950, 16, 0.05);
  const p = prep(pts, true, 951, 2, 5);
  ctx.fillStyle = INK;
  ctx.beginPath();
  ctx.rect(-10, -10, W + 20, H + 20);
  ctx.moveTo(p[0][0], p[0][1]);
  for (let i = p.length - 1; i >= 0; i--) ctx.lineTo(p[i][0], p[i][1]);
  ctx.closePath();
  ctx.fill('evenodd');
}

let _sorted = false;
function prepareShots() {
  if (_sorted) return;
  SHOTS.sort((a, b) => a.start - b.start);
  SHOTS.forEach((s, i) => {
    s.end = i + 1 < SHOTS.length ? SHOTS[i + 1].start : VO_END();
    if (s.tr === 'smear') cue(s.end - D, 'whoosh', 0.8);
  });
  const last = SHOTS[SHOTS.length - 1];
  if (last && last.tr === 'iris') cue(IRIS_START() + 0.1, 'slide_down', 0.6);
  _sorted = true;
}

function renderFrame(f) {
  prepareShots();
  const n = Math.floor(f / 2);
  DRAWING = n;
  V = n % 3;
  NOW = n * 2 / FPS;
  const t = NOW;
  let i = SHOTS.findIndex((s, k) => t >= s.start && (k === SHOTS.length - 1 || t < SHOTS[k + 1].start));
  if (i < 0) i = 0;
  const s = SHOTS[i] || { start: 0, end: VO_END(), draw() {} }, lt = t - s.start;
  ctx.setTransform(CW / W, 0, 0, CH / H, 0, 0);
  ctx.fillStyle = PAPER;
  ctx.fillRect(0, 0, W, H);
  ctx.save();
  // smear transition: the last drawing of the shot slides out, the first of the next slides in
  let whip = 0;
  if (s.tr === 'smear' && t >= s.end - D - 1e-6) whip = -1;
  if (i > 0 && SHOTS[i - 1].tr === 'smear' && lt < D - 1e-6) whip = 1;
  if (whip) ctx.translate(whip * -70 * (W / 540), 0);
  applyCam(s, lt);
  if (s) s.draw(lt, t, s);
  ctx.restore();
  if (whip) for (let k = 0; k < 9; k++) {
    const y = (60 + k * 105 + rnd(n, k) * 40) * (H / 960), x = rnd(n, k + 20) * W;
    line([[x - 160, y], [x + 160, y + (rnd(n, k + 40) - .5) * 10]], 4 + rnd(n, k + 60) * 5, 970 + k, k % 3 === 0 ? INK : [RED, BLUE, YEL][k % 3], 2);
  }
  drawCaptions(t, s);
  if (s.tr === 'iris' && i === SHOTS.length - 1) {
    // close from fully open (past the farthest corner) down to black, slow at both ends
    const [ix, iy] = s.iris || [W / 2, H / 2];
    const r0 = Math.max(Math.hypot(ix, iy), Math.hypot(W - ix, iy), Math.hypot(ix, H - iy), Math.hypot(W - ix, H - iy)) + 30;
    const u = clamp((t - IRIS_START()) / IRIS_CLOSE, 0, 1);
    if (u >= 1) { ctx.setTransform(CW / W, 0, 0, CH / H, 0, 0); ctx.fillStyle = INK; ctx.fillRect(0, 0, W, H); return; }
    if (u > 0) iris(ix, iy, lerp(r0, 0, EASE.io(u)));
  }
  frameBorder();
}

function setup() {
  const cvs = document.getElementById('c');
  ctx = cvs.getContext('2d');
  window.TOTAL_FRAMES = Math.ceil(VO_END() * FPS / 2) * 2;
  prepareShots();
  window.renderFrame = renderFrame;
  window.grab = (q = 0.92, scale = 1) => {
    if (scale === 1) return cvs.toDataURL('image/jpeg', q);
    const o = document.createElement('canvas');
    o.width = CW * scale; o.height = CH * scale;
    o.getContext('2d').drawImage(cvs, 0, 0, o.width, o.height);
    return o.toDataURL('image/jpeg', q);
  };
  window.getCues = () => CUES.slice().sort((a, b) => a.t - b.t);
  window.READY = true;
  // opened in a normal browser: play it
  if (!navigator.webdriver) {
    let t0 = null;
    const loop = ts => {
      if (t0 === null) t0 = ts;
      renderFrame(Math.floor((ts - t0) / 1000 * FPS) % window.TOTAL_FRAMES);
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }
}
window.addEventListener('load', () => {
  try { setup(); }
  catch (e) { window.SETUP_ERROR = String(e && e.stack || e); console.error(e); }
});
