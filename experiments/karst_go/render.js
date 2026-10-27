// Render karst_diagram.html to PNG and to a vector PDF (A3 landscape), shrink any equation that is wider than its card,
// and report text that overlaps, touches a badge or a card it does not belong to, or leaves its box.
// Usage: node render.js [scale] [outdir]
const { chromium } = require('playwright');
const path = require('path');
const W = 2400, H = 1697;
const OUT = process.argv[3] || __dirname;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: Number(process.argv[2] || 1.5) });
  await p.goto('file://' + path.join(__dirname, 'karst_diagram.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const report = await p.evaluate(() => {
    const out = [];
    // 1. equations: shrink until they fit their box
    for (const e of document.querySelectorAll('.eq')) {
      let fs = parseFloat(getComputedStyle(e).fontSize);
      const start = fs;
      while (e.scrollWidth > e.clientWidth + 1 && fs > 14) { fs -= 0.5; e.style.fontSize = fs + 'px'; }
      if (fs < start) out.push(['shrunk equation', e.closest('.card').querySelector('.title').textContent, start + ' -> ' + fs]);
      if (fs < 19) out.push(['EQUATION TOO SMALL', e.closest('.card').querySelector('.title').textContent, fs]);
    }
    // 2. cards and the innovation band must not overflow
    for (const c of document.querySelectorAll('.card')) {
      const used = [...c.children].reduce((s, k) => Math.max(s, k.getBoundingClientRect().bottom), 0) - c.getBoundingClientRect().top;
      const free = c.clientHeight - used;
      out.push([free < 4 ? 'CARD OVERFLOW' : 'card ok', c.querySelector('.title').textContent, 'free px ' + Math.round(free)]);
    }
    const inv = document.querySelector('#innov'), span = inv.querySelector('span').getBoundingClientRect(), ib = inv.getBoundingClientRect();
    out.push([span.bottom > ib.bottom - 4 || span.top < ib.top + 4 ? 'INNOVATION OVERFLOW' : 'innovation ok', Math.round(span.height), Math.round(ib.height)]);
    const t = document.querySelector('#band .title').getBoundingClientRect(), rows = document.querySelector('#band .rows').getBoundingClientRect();
    out.push([t.right > rows.left - 20 ? 'HEADER OVERLAP' : 'header ok', 'title ends ' + Math.round(t.right), 'rows start ' + Math.round(rows.left)]);
    // 3. SVG labels: overlaps, badges, inset cards, leaving the section
    const svg = document.querySelector('#hero');
    const box = (bb) => ({ x0: bb.x, x1: bb.x + bb.width, y0: bb.y, y1: bb.y + bb.height });
    const hit = (a, c, mx = 1, my = 3) => Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0) > mx && Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0) > my;
    const T = [...svg.querySelectorAll('text[data-svg]')].map((el) => ({ el, s: el.textContent, ...box(el.getBBox()) }));
    const B = [...svg.querySelectorAll('circle[data-badge]')].map((el) => ({ ...box(el.getBBox()), cx: +el.getAttribute('cx'), cy: +el.getAttribute('cy') }));
    const P = [...svg.querySelectorAll('g[data-panel]')].map((el) => ({ el, name: el.dataset.panel, ...box(el.getBBox()) }));
    for (const a of T) {
      if (a.x0 < 0 || a.x1 > 2400 || a.y0 < 112 || a.y1 > 866) out.push(['LABEL OUTSIDE SECTION', a.s, Math.round(a.x0), Math.round(a.y0)]);
      for (const c of B) {
        const own = Math.abs((a.x0 + a.x1) / 2 - c.cx) < 8 && Math.abs((a.y0 + a.y1) / 2 - c.cy) < 14;
        if (!own && hit(a, c, 0, 0)) out.push(['LABEL ON BADGE', a.s, Math.round(c.cx) + ',' + Math.round(c.cy)]);
      }
      for (const c of P) if (!c.el.contains(a.el) && hit(a, c, 0, 0)) out.push(['LABEL ON ' + c.name.toUpperCase(), a.s]);
    }
    for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) if (hit(T[i], T[j])) out.push(['LABEL OVERLAP', T[i].s, T[j].s]);
    for (let i = 0; i < B.length; i++) for (let j = 0; j < P.length; j++) if (hit(B[i], P[j], 0, 0)) out.push(['BADGE ON ' + P[j].name.toUpperCase(), B[i].cx + ',' + B[i].cy]);
    return out;
  });
  const bad = report.filter((r) => /^[A-Z]{3}/.test(r[0]));
  console.log(report.map((r) => r.join(' | ')).join('\n'));
  console.log(bad.length ? `\n${bad.length} problem(s)` : '\nno layout problems');
  await (await p.$('#page')).screenshot({ path: path.join(OUT, 'karst_diagram.png') });
  // vector PDF, one A3 landscape page (420 x 297 mm); 1 CSS px = 0.2645833 mm
  await p.pdf({ path: path.join(OUT, 'karst_diagram.pdf'), width: '420mm', height: '297mm', printBackground: true, pageRanges: '1',
    margin: { top: 0, right: 0, bottom: 0, left: 0 }, scale: 420 / (W * 0.2645833) });
  await b.close();
  process.exit(bad.length ? 1 : 0);
})();
