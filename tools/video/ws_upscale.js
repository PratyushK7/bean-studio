// Upscale pictures with WaveSpeed Desktop's own local upscaler (ESRGAN via UpscalerJS/TensorFlow.js, WebGL on this PC's GPU).
//   node ws_upscale.js <in dir> <out dir> [--model thick|medium|slim] [--scale 2x] [--only 6,7,8]
// The worker file is copied from the installed app (resources/app.asar, out/renderer/assets/upscaler.worker-*.js) into tools/video/ws/.
// Models download once from jsdelivr (about 29 MB for thick 2x) and are cached in the browser profile. Finished files are skipped.
const { chromium } = require('playwright-core'); const fs = require('fs'); const path = require('path'); const os = require('os'); const http = require('http');
const args = process.argv.slice(2); const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const IN = path.resolve(args[0]), OUT = path.resolve(args[1]); fs.mkdirSync(OUT, { recursive: true });
const model = opt('model', 'thick'), scale = opt('scale', '2x'), only = opt('only') ? new Set(opt('only').split(',').map(Number)) : null;
const WS = path.join(__dirname, 'ws');
const todo = fs.readdirSync(IN).filter(f => /^\d{3}\.png$/.test(f)).filter(f => !only || only.has(Number(f.slice(0, 3)))).filter(f => !fs.existsSync(path.join(OUT, f)));
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  if (req.method === 'POST' && u.startsWith('/save/')) {
    const chunks = []; req.on('data', c => chunks.push(c)); req.on('end', () => { fs.writeFileSync(path.join(OUT, path.basename(u)), Buffer.concat(chunks)); res.end('ok'); }); return;
  }
  const f = u.startsWith('/img/') ? path.join(IN, path.basename(u)) : path.join(WS, path.basename(u === '/' ? 'index.html' : u));
  if (!fs.existsSync(f)) { res.statusCode = 404; return res.end(); }
  res.setHeader('Content-Type', f.endsWith('.js') ? 'text/javascript' : f.endsWith('.png') ? 'image/png' : 'text/html'); fs.createReadStream(f).pipe(res);
});
fs.writeFileSync(path.join(WS, 'index.html'), `<!doctype html><meta charset=utf-8><script>
const w = new Worker('upscaler.worker.js', { type: 'module' }); let waiting = null;
w.onmessage = e => { const m = e.data; if (m.type === 'loaded' || m.type === 'result' || m.type === 'error') { const r = waiting; waiting = null; r && r(m); } };
const ask = (type, payload) => new Promise(r => { waiting = r; w.postMessage({ type, payload }); });
window.load = (model, scale) => ask('load', { model, scale, id: 1 });
window.up = async name => {
  const bmp = await createImageBitmap(await (await fetch('/img/' + name)).blob());
  const c = new OffscreenCanvas(bmp.width, bmp.height); const x = c.getContext('2d'); x.drawImage(bmp, 0, 0);
  const m = await ask('upscale', { imageData: x.getImageData(0, 0, bmp.width, bmp.height), id: 2 });
  if (m.type !== 'result') return 'error: ' + m.payload;
  await fetch('/save/' + name, { method: 'POST', body: m.payload.blob }); return m.payload.width + 'x' + m.payload.height;
};
</script>`);
(async () => {
  if (!todo.length) { console.log('nothing to upscale'); return; }
  await new Promise(r => server.listen(9471, '127.0.0.1', r));
  const base = path.join(os.homedir(), 'AppData/Local/ms-playwright');
  const ver = fs.readdirSync(base).filter(d => /^chromium-\d+$/.test(d)).sort().pop();
  const ctx = await chromium.launchPersistentContext(path.join(WS, 'profile'), {
    executablePath: path.join(base, ver, 'chrome-win64', 'chrome.exe'), headless: process.env.WS_HEADLESS !== '0',
    args: (process.env.WS_ARGS ?? '--use-angle=d3d11 --enable-gpu --ignore-gpu-blocklist').split(' ').filter(Boolean)
  });
  const p = ctx.pages()[0] || await ctx.newPage(); p.setDefaultTimeout(0); p.on('console', m => process.env.WS_DEBUG && console.log('page:', m.text())); p.on('pageerror', e => console.log('pageerror:', e.message));
  await p.goto('http://127.0.0.1:9471/');
  console.log('gpu:', await p.evaluate(() => { const g = document.createElement('canvas').getContext('webgl2'); const d = g && g.getExtension('WEBGL_debug_renderer_info'); return d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'none'; }));
  const l = await p.evaluate(([m, s]) => window.load(m, s), [model, scale]); if (l.type !== 'loaded') throw new Error('model: ' + JSON.stringify(l.payload));
  console.log(`${todo.length} pictures, ESRGAN ${model} ${scale}`);
  for (const f of todo) {
    const t = Date.now(); const r = await p.evaluate(n => window.up(n), f);
    console.log(`  ${f}: ${r} (${((Date.now() - t) / 1000).toFixed(0)} s)`);
  }
  await ctx.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
