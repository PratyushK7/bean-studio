// node render_graphics.js <jobs.json> : renders Decoding Vyapaar motion graphics (tools/video/graphics.html) frame by frame in one Chromium.
// Each job: {id, spec, dur, fps, tokens, times, out: "x.mp4", preview: "x.jpg"} or, for a lower third, {id, spec: {type: "label"}, png: "x.png"}.
// Frames are JPEG screenshots piped straight into ffmpeg (no temp files). Writes <jobs>-report.json: frames and any text that overflows
// its box or the safe area (measured in the page, at 90% of the graphic, when everything is on screen).
const { chromium } = require('playwright-core'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { spawn } = require('child_process'); const { pathToFileURL } = require('url');
(async () => {
  const jobsFile = path.resolve(process.argv[2]); const jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8'));
  const base = path.join(os.homedir(), 'AppData/Local/ms-playwright');
  const ver = fs.readdirSync(base).filter(d => /^chromium-\d+$/.test(d)).sort().pop();
  const exe = ['chrome-win64', 'chrome-win'].map(d => path.join(base, ver, d, 'chrome.exe')).find(fs.existsSync);
  const b = await chromium.launch({ executablePath: exe }); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(pathToFileURL(path.join(__dirname, 'graphics.html')).href);
  const report = [];
  for (const j of jobs) {
    try {
      await p.evaluate(([s, d, t, tm]) => window.setup(s, d, t, tm), [j.spec, j.dur || 1, j.tokens, j.times || null]);
      if (j.spec.type === 'label') {
        await p.evaluate(() => window.seek(0)); await p.screenshot({ path: j.png, omitBackground: true });
        report.push({ id: j.id, overflow: await p.evaluate(() => window.overflow()) }); continue;
      }
      const enc = j.alpha ? ['-c:v', 'png', '-pix_fmt', 'rgba'] : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p'];
      const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(j.fps), '-c:v', j.alpha ? 'png' : 'mjpeg', '-i', '-',
        ...enc, '-r', String(j.fps), j.out]);
      const n = Math.max(1, Math.round(j.dur * j.fps)); let overflow = [];
      for (let f = 0; f < n; f++) {
        await p.evaluate(t => window.seek(t), f / j.fps);
        const buf = j.alpha ? await p.screenshot({ type: 'png', omitBackground: true }) : await p.screenshot({ type: 'jpeg', quality: 93 });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
        if (f === Math.round(n * 0.9) || (n < 3 && f === n - 1)) { overflow = await p.evaluate(() => window.overflow()); if (j.preview) fs.writeFileSync(j.preview, buf); }
      }
      ff.stdin.end(); const code = await new Promise(r => ff.on('close', r));
      report.push({ id: j.id, frames: n, overflow, ffmpeg: code });
    } catch (e) { report.push({ id: j.id, error: String(e).slice(0, 300) }); }
  }
  fs.writeFileSync(jobsFile.replace(/\.json$/, '-report.json'), JSON.stringify(report, null, 1));
  console.log('rendered', report.length, 'graphics;', report.filter(r => (r.overflow || []).length || r.error).length, 'with problems');
  await b.close();
})();
