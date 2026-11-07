// node render.js <project> info
// node render.js <project> stills <t1,t2,...> [scale]     -> <project>/stills/s_<t>.jpg
// node render.js <project> frames <f0> <f1> <out.mp4>     -> frames f0..f1-1 at 24 fps (each drawing rendered once, held 2 frames)
// node render.js <project> cues <out.json>
// node render.js <project> thumb <out.png>                -> web/thumb.html, frame 0, full 1080x1920 PNG
// Playwright comes from the animation kit (build.py sets NODE_PATH).
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const { pathToFileURL } = require('url');
const fs = require('fs');
const path = require('path');

(async () => {
  const [proj, mode, a, b, c] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: +process.env.LB_W || 1080, height: +process.env.LB_H || 1920 } });   // the canvas size of the project's format
  const errors = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
  page.on('pageerror', e => { errors.push(e.message); console.log('[error]', e.message); });
  await page.goto(pathToFileURL(path.join(proj, 'web', mode === 'thumb' ? 'thumb.html' : 'index.html')).href);
  await page.waitForFunction(() => window.READY || window.SETUP_ERROR, null, { timeout: 30000 }).catch(() => {});
  await page.evaluate(() => document.fonts.ready);   // fonts a project adds with FontFace
  const setupErr = await page.evaluate(() => window.SETUP_ERROR || null);
  if (setupErr || errors.length) {
    console.log('the page failed to load:\n' + (setupErr || errors.join('\n')));
    await browser.close();
    process.exit(2);
  }
  const total = await page.evaluate(() => window.TOTAL_FRAMES);
  const frame = async (f, q, scale) => {
    const d = await page.evaluate(([f, q, s]) => { renderFrame(f); return grab(q, s); }, [f, q, scale]);
    if (errors.length) { console.log('render error at frame', f, ':', errors[0]); process.exit(3); }
    return Buffer.from(d.split(',')[1], 'base64');
  };

  if (mode === 'info') {
    const shots = await page.evaluate(() => SHOTS.map(s => [+s.start.toFixed(2), +s.end.toFixed(2), s.tr || 'cut']));
    console.log(JSON.stringify({ frames: total, seconds: total / 24, shots }));
  } else if (mode === 'stills') {
    const dir = path.join(proj, 'stills');
    fs.mkdirSync(dir, { recursive: true });
    const scale = parseFloat(b || '0.5');
    for (const t of a.split(',').map(Number)) {
      const f = Math.min(total - 1, Math.round(t * 24));
      const out = path.join(dir, `s_${t.toFixed(2)}.jpg`);
      fs.writeFileSync(out, await frame(f, 0.85, scale));
      console.log(out);
    }
  } else if (mode === 'frames') {
    const f0 = +a, f1 = Math.min(+b, total), out = c;
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '24', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '24', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const write = async buf => { if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); };
    for (let f = f0; f < f1; f += 2) {
      const buf = await frame(f, 0.94, 1);
      await write(buf);
      if (f + 1 < f1) await write(buf);   // on twos: the same drawing for two frames
    }
    ff.stdin.end();
    const code = await new Promise(r => ff.on('close', r));
    if (code !== 0) { console.log('ffmpeg failed on', out); process.exit(4); }
    console.log('rendered', out, f1 - f0, 'frames');
  } else if (mode === 'thumb') {
    const d = await page.evaluate(() => { renderFrame(0); return document.getElementById('c').toDataURL('image/png'); });
    if (errors.length) { console.log('render error in thumb.js:', errors[0]); process.exit(3); }
    fs.writeFileSync(a, Buffer.from(d.split(',')[1], 'base64'));
    console.log(a);
  } else if (mode === 'cues') {
    fs.writeFileSync(a, JSON.stringify(await page.evaluate(() => getCues()), null, 0));
  }
  await browser.close();
})();
