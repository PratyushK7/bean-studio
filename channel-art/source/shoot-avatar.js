const { chromium } = require('playwright'); const { pathToFileURL } = require('url'); const fs = require('fs'); const path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 800, height: 800 } });
  p.on('pageerror', e => console.log('[error]', e.message));
  await p.goto(pathToFileURL(path.join(__dirname, 'avatar.html')).href);
  await p.waitForFunction(() => window.READY);
  const only = process.argv[2] ? [+process.argv[2]] : [0, 1, 2];
  for (const v of only) { const d = await p.evaluate(v => renderAvatar(v), v); fs.writeFileSync(path.join(__dirname, `avatar2-${v + 1}.png`), Buffer.from(d.split(',')[1], 'base64')); }
  await b.close(); console.log('ok');
})();
