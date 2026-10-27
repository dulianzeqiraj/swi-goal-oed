'use strict';
// Word version of one diagram of the series, with large type: four A4 landscape pages.
//   page 1: title band and the schematic at full page width (a picture; its numbers 1-8 point to the panels)
//   page 2: the innovation, in large type
//   pages 3-4: the eight panels, four per page
// Every equation is a placeholder that omml.py turns into native, editable Word math (OMML).
// usage: node paradigms_word.js <diagram 1-6, order of export_content.py> draft.docx equations.json
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, VerticalAlign, TableLayoutType, PageOrientation, LineRuleType, PageBreak,
} = require('docx');

const K = Number(process.argv[2]);
const OUT = process.argv[3] || 'draft.docx', OUTEQ = process.argv[4] || 'equations.json';
const D = JSON.parse(fs.readFileSync(path.join(__dirname, 'content.json'), 'utf8'))[K - 1];
const SANS = 'Calibri';
const PAL = {   // base, deep, tint
  blue: ['2A78D6', '1B5FAE', 'EAF2FC'], purple: ['7D4FC9', '5D35A3', 'F1ECFA'], green: ['1BAF7A', '11805A', 'E6F6EF'],
  teal: ['0F8F9A', '0B6D75', 'E3F4F5'], orange: ['E4572E', 'B9471A', 'FDECE7'], amber: ['EDA100', '8F6200', 'FDF3DC'],
  pink: ['C2417A', '9B2C5E', 'FBEAF1'], brown: ['9C6B30', '7A5122', 'F6EFE6'],
};
const NAVY = '1F3864', INK = '1F2328', G0 = 'D97706', G1 = '92400E', G2 = 'FFF6E3', BR = '5A2A06';

// ---------------------------------------------------------------- equations and rich text
const EQS = [];
function matchBrace(s, i) {            // index of the brace closing the one at s[i]
  let depth = 0;
  for (let k = i; k < s.length; k++) {
    if (s[k] === '\\') { k++; continue; }
    if (s[k] === '{') depth++;
    else if (s[k] === '}' && --depth === 0) return k;
  }
  return -1;
}
function fixSup(tex) {                 // "sup" is a keyword of LibreOffice's formula language: write it as text
  let out = '', i = 0;
  while (i < tex.length) {
    const j = tex.indexOf('\\sup', i);
    if (j < 0 || /[a-zA-Z]/.test(tex[j + 4] || '')) { if (j < 0) { out += tex.slice(i); break; } out += tex.slice(i, j + 4); i = j + 4; continue; }
    out += tex.slice(i, j);
    let k = j + 4;
    while (tex[k] === ' ') k++;
    if (tex[k] === '_') {
      k++;
      while (tex[k] === ' ') k++;
      let sub, end;
      if (tex[k] === '{') { end = matchBrace(tex, k); sub = tex.slice(k + 1, end); end += 1; }
      else if (tex[k] === '\\') { const m = /^\\[a-zA-Z]+/.exec(tex.slice(k)); sub = m[0]; end = k + m[0].length; }
      else { sub = tex[k]; end = k + 1; }
      out += `\\underset{${sub}}{\\text{sup}}`;
      i = end;
    } else { out += '\\text{sup}\\,'; i = k; }
  }
  return out;
}
function clean(tex) {
  return fixSup(tex.replace(/\\textstyle\s*/g, '').replace(/\\tfrac/g, '\\frac').replace(/\\bar\{/g, '\\overline{'));
}
function eqRun(tex, display = false, size = null) {
  const id = EQS.length;
  EQS.push({ id, tex: clean(tex), display, size });
  return new TextRun(display ? `§§EQ${id}§§` : `§§IQ${id}§§`);
}
function rich(str, base = {}) {
  const runs = [];
  const re = /(\*\*[^*]+\*\*|\$[^$]+\$)/g;
  let last = 0, mo;
  while ((mo = re.exec(str)) !== null) {
    if (mo.index > last) runs.push(new TextRun({ text: str.slice(last, mo.index), ...base }));
    const t = mo[0];
    if (t.startsWith('$')) runs.push(eqRun(t.slice(1, -1), false, base.size ? base.size + 1 : null));
    else runs.push(...rich(t.slice(2, -2), { ...base, bold: true }));
    last = mo.index + t.length;
  }
  if (last < str.length) runs.push(new TextRun({ text: str.slice(last), ...base }));
  return runs;
}
const sp = (before, after, line = 252) => ({ before, after, line, lineRule: LineRuleType.AUTO });
const para = (str, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.LEFT, spacing: sp(o.before || 0, o.after ?? 40, o.line || 252),
  keepNext: !!o.keepNext,
  children: [...(o.lead || []), ...rich(str, { font: SANS, size: o.size || 22, color: o.color || INK, bold: o.bold })],
});
const eqp = (tex, o = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: sp(o.before ?? 40, o.after ?? 40),
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  run: { size: o.size || 24 },
  children: [eqRun(tex, true, o.size || 24)],
});
const chip = (text, fill, color = 'FFFFFF', size = 18) => new TextRun({ text: ` ${text} `, bold: true, color, size, font: SANS,
  shading: { type: ShadingType.CLEAR, fill, color: 'auto' } });
const blank = (h = 120) => new Paragraph({ spacing: sp(0, 0, h), children: [new TextRun({ text: '', size: 8 })] });

// ---------------------------------------------------------------- cells and tables
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const NOB = { top: NONE, bottom: NONE, left: NONE, right: NONE };
const line = (color, size = 6) => ({ style: BorderStyle.SINGLE, size, color });
function cell(children, w, o = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, verticalAlign: o.va || VerticalAlign.TOP,
    margins: o.margins || { top: 90, bottom: 80, left: 160, right: 160 },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
    borders: o.borders || NOB, children,
  });
}
function table(rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    borders: { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE }, rows,
  });
}

// ---------------------------------------------------------------- page geometry: A4 landscape, 1.27 cm margins
const PW = 16838, PH = 11906, MA = 720;
const WU = PW - 2 * MA;                                    // 15398 DXA = 27.2 cm

function band(sub) {
  return table([new TableRow({ cantSplit: true, children: [cell([
    new Paragraph({ spacing: sp(0, 40), children: [new TextRun({ text: D.kicker.replace(/\s+·\s+/g, '  ·  '), bold: true, color: 'F6B73C', size: 20, font: SANS, characterSpacing: 20 })] }),
    new Paragraph({ spacing: sp(0, sub ? 60 : 0), children: rich(D.title, { font: SANS, size: 36, color: 'FFFFFF', bold: true }) }),
    ...(sub || []),
  ], WU, { fill: NAVY, margins: { top: 140, bottom: 140, left: 240, right: 240 } })] })], [WU]);
}

// page 1: title band and the schematic at full width
function page1() {
  const tags = D.tags.map(([t, x], i) => para(x, { size: 21, color: 'DBE6F5', after: i ? 0 : 30,
    lead: [chip(t, i ? 'F6B73C' : 'C9D3E0', '13284D', 17), new TextRun({ text: '  ', size: 21 })] }));
  const png = fs.readFileSync(path.join(__dirname, `hero${K}.png`));
  const wpx = Math.round(WU / 1440 * 96), hpx = Math.round(wpx * 1095 / 2361);
  return [band(tags), blank(140),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: sp(0, 60), children: [new ImageRun({ type: 'png', data: png, transformation: { width: wpx, height: hpx } })] }),
    para('The numbers 1–8 in the picture point to the eight panels on the next pages; the innovation follows on the next page.', { size: 19, color: '5B6573', align: AlignmentType.CENTER, after: 0 })];
}

// page 2: the innovation in large type
function page2() {
  const I = D.innov;
  const kids = [
    new Paragraph({ spacing: sp(0, 40), children: [new TextRun({ text: 'INNOVATION   ', bold: true, color: G1, size: 24, font: SANS, characterSpacing: 30 }),
      ...rich(I.name, { font: SANS, size: 40, bold: true, color: BR })] }),
    para(I.sub, { size: 26, color: '6B4A2A', after: 80 }),
  ];
  I.items.forEach((it, i) => {
    kids.push(para(it.t, { size: 30, bold: true, color: BR, before: 160, after: 60, keepNext: true, lead: [chip(String(i + 1), G0, 'FFFFFF', 30), new TextRun({ text: '  ', size: 30 })] }));
    it.eqs.forEach((e) => kids.push(eqp(e, { fill: 'FFFDF8', size: 30, before: 40, after: 60 })));
    kids.push(para(it.x, { size: 26, color: '3D2B1A', after: 30 }));
    if (it.kv) kids.push(para(`**${it.kv}**   ${it.kc.toLowerCase()}`, { size: 26, color: G1, align: AlignmentType.RIGHT, after: 20 }));
  });
  if (I.foot) kids.push(para(I.foot, { size: 24, color: '6B4A2A', before: 120, after: 0 }));
  const gold = line(G0, 24);
  return [new Paragraph({ children: [new PageBreak()], spacing: sp(0, 0) }),
    table([new TableRow({ cantSplit: true, children: [cell(kids, WU, { fill: G2, borders: { top: gold, bottom: gold, left: gold, right: gold }, margins: { top: 180, bottom: 160, left: 280, right: 280 } })] })], [WU])];
}

// pages 3-4: the panels, two rows of two per page
const GAP = 240, WC = Math.floor((WU - GAP) / 2), WC2 = WU - GAP - WC;
function card(c, n, wc) {
  const [base, deep, tint] = PAL[c.color];
  const kids = [
    para(c.t, { size: 30, bold: true, color: deep, after: 80, line: 240, lead: [chip(String(n), base, 'FFFFFF', 30), new TextRun({ text: '  ', size: 30 })] }),
    para(c.idea, { size: 24, after: 80, lead: [chip('IDEA', '8A93A0', 'FFFFFF', 18), new TextRun({ text: ' ', size: 24 })] }),
    ...c.eqs.map((e, i) => eqp(e, { fill: tint, size: 26, before: i ? 0 : 30, after: i === c.eqs.length - 1 ? 100 : 0 })),
    para(c.land, { size: 22, color: '3A4350', after: 0, lead: [chip(c.pill || '2020–2026', deep, 'FFFFFF', 18), new TextRun({ text: ' ', size: 22 })] }),
  ];
  const thin = line('D0D7DE', 6);
  return cell(kids, wc, { fill: 'FFFFFF', borders: { top: line(base, 36), bottom: thin, left: thin, right: thin }, margins: { top: 110, bottom: 110, left: 170, right: 170 } });
}
function panels(first) {
  const widths = [WC, GAP, WC2];
  const gapCell = () => cell([new Paragraph({ children: [] })], GAP, { margins: { top: 0, bottom: 0, left: 0, right: 0 } });
  const row = (k) => new TableRow({ cantSplit: true, children: [card(D.cards[k], k + 1, WC), gapCell(), card(D.cards[k + 1], k + 2, WC2)] });
  const spacer = new TableRow({ cantSplit: true, children: widths.map((w) => cell([blank(160)], w, { margins: { top: 0, bottom: 0, left: 0, right: 0 } })) });
  return [new Paragraph({ children: [new PageBreak()], spacing: sp(0, 0) }),
    para(`${D.title.split(':')[0]} · panels ${first + 1}–${first + 4}`, { size: 20, bold: true, color: NAVY, after: 100 }),
    table([row(first), spacer, row(first + 2)], widths)];
}

const doc = new Document({
  creator: 'swi-goal-oed', title: D.title.replace(/\*\*/g, ''),
  styles: { default: { document: { run: { font: SANS, size: 22 } } } },
  sections: [{
    properties: { page: { size: { width: PH, height: PW, orientation: PageOrientation.LANDSCAPE }, margin: { top: MA, bottom: MA, left: MA, right: MA, header: 0, footer: 0 } } },
    children: [...page1(), ...page2(), ...panels(0), ...panels(4)],
  }],
});
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  fs.writeFileSync(OUTEQ, JSON.stringify(EQS, null, 1));
  console.log(`wrote ${OUT} with ${EQS.length} equations`);
});
