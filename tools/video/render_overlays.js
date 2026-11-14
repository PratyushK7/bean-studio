// node render_overlays.js <dir> : every <name>.html in dir -> transparent 1920x1080 <name>.png (skips ones already made). One browser, so it is fast.
const { chromium } = require('playwright-core'); const fs = require('fs'); const path = require('path'); const os = require('os');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const base = path.join(os.homedir(), 'AppData/Local/ms-playwright');
  const ver = fs.readdirSync(base).filter(d => /^chromium-\d+$/.test(d)).sort().pop();
  const exe = ['chrome-win64', 'chrome-win'].map(d => path.join(base, ver, d, 'chrome.exe')).find(fs.existsSync);
  const b = await chromium.launch({ executablePath: exe }); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  let n = 0;
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) {
    const out = path.join(dir, f.replace(/\.html$/, '.png'));
    if (fs.existsSync(out)) continue;
    await p.goto(require('url').pathToFileURL(path.join(dir, f)).href); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: out, omitBackground: true }); n++;
  }
  console.log('rendered', n); await b.close();
})();
