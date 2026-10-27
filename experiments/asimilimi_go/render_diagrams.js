// Render res/diagram_*.html to PNG (about 356 dpi at 17 cm width) and report text that leaves its box or the
// figure, and pairs of texts that overlap. Usage: node render_diagrams.js [scale]
const { chromium } = require('playwright');
const path = require('path');
const RES = path.join(__dirname, 'res');
(async () => {
  const b = await chromium.launch();
  let problems = 0;
  for (const name of ['diagram_bc', 'diagram_cycle']) {
    const p = await b.newPage({ viewport: { width: 1700, height: 2000 }, deviceScaleFactor: Number(process.argv[2] || 1.4) });
    await p.goto('file://' + path.join(RES, name + '.html'));
    await p.evaluate(() => document.fonts.ready);
    const bad = await p.evaluate(() => {
      const svg = document.querySelector('svg'); const W = svg.viewBox.baseVal.width; const H = svg.viewBox.baseVal.height;
      const T = [...document.querySelectorAll('text')].map((t) => { const bb = t.getBBox(); return { s: t.textContent, x0: bb.x, x1: bb.x + bb.width, y0: bb.y, y1: bb.y + bb.height, box: t.dataset.box }; });
      const out = [];
      for (const t of T) {
        if (t.x0 < 0 || t.x1 > W || t.y0 < 0 || t.y1 > H) out.push(['outside figure', t.s]);
        if (t.box) { const [a, c] = t.box.split(',').map(Number); if (t.x0 < a + 4 || t.x1 > c - 4) out.push(['outside box', t.s, Math.round(t.x1), c]); }
      }
      for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
        const a = T[i], c = T[j];
        const ox = Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0), oy = Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0);
        if (ox > 2 && oy > 4) out.push(['overlap', a.s, c.s]);
      }
      return out;
    });
    problems += bad.length;
    console.log(name + ': ' + (bad.length ? '\n  ' + bad.map((r) => r.join(' | ')).join('\n  ') : 'no text problems'));
    const el = await p.$('svg');
    await el.screenshot({ path: path.join(RES, name + '.png') });
    await p.close();
  }
  await b.close();
  process.exit(problems ? 1 : 0);
})();
