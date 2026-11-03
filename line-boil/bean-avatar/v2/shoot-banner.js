// node shoot-banner.js [variant 0-2]  -> banner2-N.png (2560x1440)
const { chromium } = require('playwright'); const { pathToFileURL } = require('url'); const fs = require('fs'); const path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('[error]', e.message));
  await p.goto(pathToFileURL(path.join(__dirname, 'banner.html')).href);
  await p.waitForFunction(() => window.READY, null, { timeout: 20000 });
  const only = process.argv[2] ? [+process.argv[2]] : [0, 1, 2];
  for (const v of only) { const d = await p.evaluate(v => renderBanner(v), v); fs.writeFileSync(path.join(__dirname, `banner2-${v + 1}.png`), Buffer.from(d.split(',')[1], 'base64')); }
  await b.close(); console.log('ok');
})();
