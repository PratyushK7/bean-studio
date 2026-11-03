// node shoot.js  -> banner-1.png .. banner-3.png (2560x1440) and safe-area previews
const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
const fs = require('fs');
const path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('[error]', e.message));
  await p.goto(pathToFileURL(path.join(__dirname, 'banner.html')).href);
  await p.waitForFunction(() => window.READY, null, { timeout: 20000 });
  for (let v = 0; v < 3; v++) {
    const d = await p.evaluate(v => renderBanner(v), v);
    fs.writeFileSync(path.join(__dirname, '..', `banner-${v + 1}.png`), Buffer.from(d.split(',')[1], 'base64'));
  }
  await b.close();
  console.log('ok');
})();
