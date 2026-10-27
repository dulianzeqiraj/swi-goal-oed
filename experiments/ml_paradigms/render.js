// Render <name>.html to PNG and a vector PDF (one A3 landscape page) and check the layout:
// equations wider than their box are shrunk (an error below 18 px), cards and the innovation column must not overflow,
// the header title must not meet the tags, and hero labels (SVG text and HTML overlays) must not overlap each other,
// sit on a badge, leave the hero, or cross the edge of a stage panel. Usage: node render.js <name> [scale] [outdir]
const { chromium } = require('playwright');
const path = require('path');
const W = 2400, H = 1697;
const name = process.argv[2];
const OUT = process.argv[4] || __dirname;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: Number(process.argv[3] || 1.5) });
  await p.goto('file://' + path.join(__dirname, name + '.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const report = await p.evaluate(() => {
    const out = [];
    const label = (e) => (e.closest('.card') ? e.closest('.card').querySelector('.title').textContent : e.closest('#innov') ? 'innovation' : 'hero');
    for (const e of document.querySelectorAll('.eq, .item .e, .eqlab, .eqbare')) {
      let fs = parseFloat(getComputedStyle(e).fontSize);
      const start = fs;
      const box = e.classList.contains('eqlab') || e.classList.contains('eqbare') ? null : e;
      if (!box) continue;
      while (box.scrollWidth > box.clientWidth + 1 && fs > 12) { fs -= 0.5; box.style.fontSize = fs + 'px'; }
      if (fs < start) out.push(['shrunk equation', label(e), start + ' -> ' + fs]);
      if (fs < 18) out.push(['EQUATION TOO SMALL', label(e), fs]);
    }
    for (const c of document.querySelectorAll('.card')) {
      const used = [...c.children].reduce((s, k) => Math.max(s, k.getBoundingClientRect().bottom), 0) - c.getBoundingClientRect().top;
      const free = c.clientHeight - used;
      out.push([free < 4 ? 'CARD OVERFLOW' : 'card ok', c.querySelector('.title').textContent, 'free px ' + Math.round(free)]);
    }
    const inv = document.querySelector('#innov');
    if (inv) {
      const ib = inv.getBoundingClientRect();
      const kids = [...inv.children].filter((k) => !k.classList.contains('foot'));
      const bottom = Math.max(...kids.map((k) => k.getBoundingClientRect().bottom));
      const foot = inv.querySelector('.foot');
      const fb = foot ? foot.getBoundingClientRect() : null;
      const free = (fb ? fb.top : ib.bottom - 12) - bottom;
      out.push([free < 0 || (fb && fb.bottom > ib.bottom - 6) ? 'INNOVATION OVERFLOW' : 'innovation ok', 'free px ' + Math.round(free)]);
    }
    const t = document.querySelector('#band .title').getBoundingClientRect(), rows = document.querySelector('#band .rows').getBoundingClientRect();
    out.push([t.right > rows.left - 20 ? 'HEADER OVERLAP' : 'header ok', 'title ends ' + Math.round(t.right), 'tags start ' + Math.round(rows.left)]);
    const y1 = Number(document.querySelector('#page').dataset.heroY1);
    const svg = document.querySelector('#hero');
    const bx = (r) => ({ x0: r.x, x1: r.x + r.width, y0: r.y, y1: r.y + r.height });
    const hit = (a, c, m = 1) => Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0) > m && Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0) > m;
    const inside = (a, c, m = 2) => a.x0 >= c.x0 + m && a.x1 <= c.x1 - m && a.y0 >= c.y0 + m && a.y1 <= c.y1 - m;
    const L = [];
    for (const el of svg.querySelectorAll('text[data-svg]')) {
      if (el.dataset.own) continue;
      L.push({ s: el.textContent, ...bx(el.getBBox()) });
    }
    for (const el of document.querySelectorAll('.ovl')) L.push({ s: el.textContent.slice(0, 40), ...bx(el.getBoundingClientRect()) });
    const B = [...svg.querySelectorAll('circle[data-badge]')].map((el) => ({ ...bx(el.getBBox()), c: el.getAttribute('cx') + ',' + el.getAttribute('cy') }));
    const S = [...svg.querySelectorAll('[data-stage]')].map((el) => ({ n: el.dataset.stage, ...bx(el.getBBox()) }));
    const I = inv ? bx(inv.getBoundingClientRect()) : null;
    for (const a of L) {
      if (a.x0 < 0 || a.x1 > 2400 || a.y0 < 112 || a.y1 > y1) out.push(['LABEL OUTSIDE HERO', a.s]);
      for (const c of B) if (hit(a, c, 0)) out.push(['LABEL ON BADGE', a.s, c.c]);
      for (const s of S) if (hit(a, s, 0) && !inside(a, s)) out.push(['LABEL CROSSES PANEL EDGE', a.s, s.n]);
      if (I && hit(a, I, 0)) out.push(['LABEL ON INNOVATION', a.s]);
    }
    for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++) if (hit(L[i], L[j], 2)) out.push(['LABEL OVERLAP', L[i].s, L[j].s]);
    for (const c of B) if (I && hit(c, I, 0)) out.push(['BADGE ON INNOVATION', c.c]);
    for (let i = 0; i < B.length; i++) for (let j = i + 1; j < B.length; j++) if (hit(B[i], B[j], 0)) out.push(['BADGE OVERLAP', B[i].c, B[j].c]);
    return out;
  });
  const bad = report.filter((r) => /^[A-Z]{3}/.test(r[0]));
  console.log(report.map((r) => r.join(' | ')).join('\n'));
  console.log(bad.length ? `\n${bad.length} problem(s)` : '\nno layout problems');
  await (await p.$('#page')).screenshot({ path: path.join(OUT, name + '.png') });
  await p.pdf({ path: path.join(OUT, name + '.pdf'), width: '420mm', height: '297mm', printBackground: true, pageRanges: '1',
    margin: { top: 0, right: 0, bottom: 0, left: 0 }, scale: 420 / (W * 0.2645833) });
  await b.close();
  process.exit(bad.length ? 1 : 0);
})();
