"""CERTAIN-COAST (NATO SPS proposal): State of the Art. Builds a Word document (Arial, large type, clickable links):
the coupled hazard chain, state of the art per pillar, gap table, mathematical and physical innovations, and 30
annotated papers 2020-2026 (Caltech, MIT, Harvard, Oxford). Content in sota_data.py."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sota_data as D  # noqa: E402

FONT = 'Arial'


def run(p, text, bold=False, italic=False, size=11, color=None):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name = FONT; r.font.size = Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def link(p, url, text, size=11):
    rid = p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rid)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    f = OxmlElement('w:rFonts'); f.set(qn('w:ascii'), FONT); f.set(qn('w:hAnsi'), FONT); rpr.append(f)
    c = OxmlElement('w:color'); c.set(qn('w:val'), '1F5FBF'); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); r.append(t)
    h.append(r); p._p.append(h)


def para(doc, after=4, indent=0, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    return p


def heading(doc, text, size=14, color='1F3864', before=10):
    p = para(doc, 6, before=before); run(p, text, bold=True, size=size, color=color)
    p.paragraph_format.keep_with_next = True
    return p


def rich(p, text, size=11):
    """Text with [n] references kept as plain text; **bold** segments supported."""
    parts = text.split('**')
    for i, seg in enumerate(parts):
        if seg:
            run(p, seg, bold=(i % 2 == 1), size=size)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
    tcPr.append(sh)


def table(doc, header, rows, widths, size=10):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(header):
        c = t.rows[0].cells[j]; c.text = ''
        run(c.paragraphs[0], h, bold=True, size=size, color='FFFFFF'); shade(c, '1F3864')
    for r_ in rows:
        cells = t.add_row().cells
        for j, v in enumerate(r_):
            cells[j].text = ''
            rich(cells[j].paragraphs[0], v, size=size)
    t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    grid = t._tbl.tblGrid
    for j, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[j] * 567)))
    for j, w in enumerate(widths):
        t.columns[j].width = Cm(w)
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit'); trPr.append(cs)
    return t


INST_COL = {'Caltech': '#B45309', 'MIT': '#B03A3A', 'Harvard': '#6a4fb3', 'Oxford': '#1F3864'}
CAPS = ['Measured', 'Modelled', 'Coupled to\nthe other\nhazards', 'Sensors\ndesigned for\nthe warning', 'Warning with\na stated\nmiss rate']
# component -> literature state per capability (2 done, 1 partial, 0 not done) and the innovation that closes it
GAPS = [
    ('Seawater intrusion', [2, 2, 0, 1, 0], ['', '', 'P1, P3', 'M3, M6', 'M1']),
    ('Subsidence, land motion', [2, 2, 0, 0, 1], ['', '', 'P1', 'M3', 'P4']),
    ('Extreme sea levels', [2, 2, 1, 0, 0], ['', '', 'P1, M5', 'M3', 'M1']),
    ('Liquefaction', [2, 2, 0, 0, 0], ['', '', 'P2', 'M3, P5', 'M1']),
    ('Port and landfall\nfoundations', [1, 2, 0, 0, 0], ['P5', '', 'P2', 'M3', 'M1']),
    ('Groundwater sensing\n(noise, fibre)', [2, 1, 0, 0, 0], ['', 'P5', 'P5', 'M3', 'P5']),
]


def inst_of(it):
    return next(k for k in INST_COL if it['inst'].startswith(k))


def fig_evidence(path):
    import re
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    groups = D.GROUPS
    fig, ax = plt.subplots(figsize=(6.7, 4.1), dpi=300)
    counts = {}
    for gi, (g, items) in enumerate(groups):
        y = len(groups) - 1 - gi
        by_year = {}
        for it in items:
            yr = int(re.search(r'\((\d{4})\)', it['cite']).group(1))
            by_year.setdefault(yr, []).append(it)
        for yr, its in by_year.items():
            k = len(its); nrow = (k + 2) // 3
            for j, it in enumerate(its):
                r, c = divmod(j, 3)
                in_row = min(3, k - 3 * r)
                x = yr + (c - (in_row - 1) / 2) * 0.34
                yy = y + (r - (nrow - 1) / 2) * 0.40
                inst = inst_of(it); counts[inst] = counts.get(inst, 0) + 1
                ax.scatter(x, yy, s=200, color=INST_COL[inst], zorder=3, edgecolor='white', linewidth=0.8)
                ax.text(x, yy, str(it['n']), ha='center', va='center', fontsize=7.2, color='white', fontweight='bold', zorder=4)
        if gi % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color='#F4F6F8', zorder=0)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g.split('. ', 1)[1].replace(', compound flooding and ports', ', ports').replace(' and the foundations of port and landfall', ', foundations')
                        for g, _ in reversed(groups)], fontsize=8.8)
    ax.set_xticks(range(2020, 2027)); ax.set_xticklabels([str(y) for y in range(2020, 2027)], fontsize=9)
    ax.set_xlim(2019.4, 2026.6); ax.set_ylim(-0.6, len(groups) - 0.4)
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis='y', length=0)
    h = [plt.Line2D([], [], marker='o', ls='', ms=9, color=c, label=f'{k} ({counts.get(k, 0)})') for k, c in INST_COL.items()]
    ax.legend(handles=h, loc='upper center', bbox_to_anchor=(0.42, -0.1), ncol=4, frameon=False, fontsize=8.8)
    fig.tight_layout(); fig.savefig(path, dpi=300); plt.close(fig)


def fig_gaps(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fill = {2: '#2E6DB4', 1: '#A9C4E8', 0: '#FFFFFF'}
    fig, ax = plt.subplots(figsize=(6.7, 3.9), dpi=300)
    n = len(GAPS)
    for i, (name, st, code) in enumerate(GAPS):
        y = n - 1 - i
        for j, v in enumerate(st):
            ax.add_patch(Rectangle((j + 0.04, y - 0.44), 0.92, 0.88, fc=fill[v], ec='#B03A3A' if v == 0 else '#9aa3ad',
                                   lw=1.3 if v == 0 else 0.8))
            if code[j]:
                ax.text(j + 0.5, y, code[j], ha='center', va='center', fontsize=8.8, fontweight='bold',
                        color='#1E6B47', bbox=dict(boxstyle='round,pad=0.15', fc='#E6F4EC', ec='#1E8A5A', lw=0.8))
    ax.set_xlim(0, len(CAPS)); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([j + 0.5 for j in range(len(CAPS))]); ax.set_xticklabels(CAPS, fontsize=8.6)
    ax.xaxis.tick_top()
    ax.set_yticks(range(n)); ax.set_yticklabels([g[0] for g in reversed(GAPS)], fontsize=8.8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    h = [Rectangle((0, 0), 1, 1, fc=fill[2], ec='#9aa3ad', label='done in the literature'),
         Rectangle((0, 0), 1, 1, fc=fill[1], ec='#9aa3ad', label='partly done'),
         Rectangle((0, 0), 1, 1, fc=fill[0], ec='#B03A3A', label='not done'),
         Rectangle((0, 0), 1, 1, fc='#E6F4EC', ec='#1E8A5A', label='closed by (innovation)')]
    ax.legend(handles=h, loc='upper center', bbox_to_anchor=(0.4, -0.02), ncol=4, frameon=False, fontsize=8.6,
              handlelength=1.2, columnspacing=1.2)
    fig.tight_layout(); fig.savefig(path, dpi=300); plt.close(fig)


def figure(doc, path, width, caption):
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    p = para(doc, 6); run(p, caption, italic=True, size=9.5, color='52606D')


def main(out):
    import tempfile
    import build_introduction as BI
    work = tempfile.mkdtemp()
    f_sys = os.path.join(work, 'fig_system.png'); BI.fig_system(f_sys)
    f_gap = os.path.join(work, 'fig_gaps.png'); fig_gaps(f_gap)
    f_ev = os.path.join(work, 'fig_evidence.png'); fig_evidence(f_ev)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.TITLE, bold=True, size=18, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.FULL_TITLE, bold=True, size=12, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.SUBTITLE, italic=True, size=11, color='52606D')

    for si, (sec_title, blocks) in enumerate(D.SECTIONS):
        heading(doc, sec_title, 14)
        for kind, content in blocks:
            if kind == 'p':
                p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, content)
            elif kind == 'h':
                h = heading(doc, content, 12, color='2E6DB4', before=6); h.paragraph_format.keep_with_next = True
            elif kind == 'b':
                p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, content)
            elif kind == 'table':
                header, rows, widths = content
                t = table(doc, header, rows, widths)
                t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
                para(doc, 6)
        if si == 0:
            figure(doc, f_sys, 15.5, 'Figure 1. The coast as one system: four drivers act through two shared variables, relative sea '
                                     'level and the water table, on the three hazards at the three assets.')
        if si == 2:
            figure(doc, f_gap, 16.0, 'Figure 2. Gap matrix: what the 2020–2026 literature has done for each component, and the '
                                     'CERTAIN-COAST innovation that closes each gap (codes as in Section 4). Assessment from the '
                                     'papers in Section 5 and the table above.')

    h = heading(doc, D.PAPERS_TITLE, 14); h.paragraph_format.page_break_before = True
    p = para(doc, 6); rich(p, D.PAPERS_INTRO)
    figure(doc, f_ev, 16.0, 'Figure 3. The 30 key papers by topic and year; colour: university (number of papers). Numbers '
                            'are the reference numbers used throughout the proposal.')
    for grp, items in D.GROUPS:
        heading(doc, grp, 12.5, color='2E6DB4', before=6)
        for it in items:
            p = para(doc, 2); p.paragraph_format.keep_with_next = True
            run(p, f"[{it['n']}] ", bold=True, size=11, color='1F3864'); run(p, it['cite'], bold=True, size=10.5)
            p = para(doc, 2, 0.5); p.paragraph_format.keep_with_next = True
            run(p, it['inst'] + '   ', size=10, color='52606D', italic=True)
            link(p, it['doi'], it['doi'].replace('https://', ''), 10)
            if it.get('free'):
                run(p, '   |   free: ', size=10); link(p, it['free'], it['free_label'], 10)
            else:
                run(p, '   |   ' + it.get('free_note', 'paywalled'), italic=True, size=10, color='52606D')
            p = para(doc, 2, 0.5); p.paragraph_format.keep_with_next = True
            run(p, 'Done: ', bold=True, size=10.5); run(p, it['done'], size=10.5)
            p = para(doc, 8, 0.5); run(p, 'Beyond it in CERTAIN-COAST: ', bold=True, size=10.5, color='1E8A5A'); run(p, it['beyond'], size=10.5)

    heading(doc, 'Local study (not from the four universities)', 12.5, color='2E6DB4', before=6)
    for code, cite, url in D.LOCAL:
        p = para(doc, 3); run(p, f'[{code}] ', bold=True, size=11, color='1F3864'); run(p, cite + '  ', size=10.5); link(p, url, url.replace('https://', ''), 10)
    heading(doc, 'Other references cited (V1, M4, M6)', 12.5, color='2E6DB4', before=6)
    for code, cite, url in D.OTHER:
        p = para(doc, 3); run(p, f'[{code}] ', bold=True, size=11, color='1F3864'); run(p, cite + ('  ' if url else ''), size=10.5)
        if url:
            link(p, url, url.replace('https://', ''), 10)
    if getattr(D, 'NOTE', None):
        p = para(doc, 4, before=8); run(p, D.NOTE, italic=True, size=9.5, color='52606D')
    h = heading(doc, '6. What is new in this review', 14, before=10); h.paragraph_format.keep_with_next = True
    for i, x in enumerate(D.WHAT_NEW):
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, x)
        if i < len(D.WHAT_NEW) - 1:
            p.paragraph_format.keep_with_next = True
    doc.save(out)
    print('saved', out, sum(len(i) for _, i in D.GROUPS), 'papers')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_State_of_the_Art.docx')
