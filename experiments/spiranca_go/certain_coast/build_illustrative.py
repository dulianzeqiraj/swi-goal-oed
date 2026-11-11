"""CERTAIN-COAST (NATO SPS proposal): illustrative figures, the optional PDF upload of the "Project plan" tab of the SPS
grant platform ("any file that might help to illustrate your project ... merge them into a single PDF file, and include
a table of contents at the start"). Six A4 pages: a table of contents and twelve figures taken from the proposal
documents and the preparatory reviews, each with its caption and its source. The figures are regenerated from the same
code and data as those documents, so the PDF cannot drift from them.

usage: python build_illustrative.py OUT.pdf"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
EXP = os.path.normpath(os.path.join(HERE, '..', '..'))

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
LIB = '/usr/share/fonts/truetype/liberation/'
FONT, FONT_B, FONT_I = LIB + 'LiberationSans-Regular.ttf', LIB + 'LiberationSans-Bold.ttf', LIB + 'LiberationSans-Italic.ttf'
SYMBOLS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'      # for the star, which Liberation Sans lacks
NAVY, GREY = HexColor('#1F3864'), HexColor('#52606D')
WIDTH = 17.0 * cm

# (key, title, caption, source, page); the page is checked after the build
FIGS = [
    ('system', 'The coast as one system',
     'Four drivers act through two shared variables, relative sea level R(t) = η(t) − u_z(t) and the water table, on three '
     'hazards at the three assets. Red arrows: the direction in which each shared variable changes a hazard. Pumping, the '
     'operators\' lever, lowers the water table: more intrusion and subsidence, less liquefaction.',
     'Introduction, Figure 1; State of the Art, Figure 1', 1),
    ('sec_chain', 'Critical assets, threats and NATO resilience',
     'The threats to each asset at Durrës, the NATO baseline requirements for resilience that the assets serve, and what '
     'CERTAIN-COAST adds. Land subsidence and sea-level rise drive all three assets at once.',
     'Security Relevance, Figure 1', 2),
    ('method', 'The method in one picture',
     'Data feed three pillars: (1) the inputs and boundaries nobody measures are reconstructed from rain and heads with '
     'guarantees that survive a wrong simulator, a wrong rain product and drift; (2) each sensor is valued by what it is '
     'guaranteed to buy before it is bought; (3) pumping effects, a drier climate and the safe operating window are '
     'computed with the hidden confounding removed and with stated error.',
     'Methodology for the NATO form, Figure 1', 2),
    ('innov', 'Where each innovation acts',
     'The sixteen technical innovations (M1–M10, P1–P5, V1) and three delivery innovations (O1–O3) placed in the warning '
     'chain, from observing the coast to verifying the warnings. <font name="SYM">★</font>: no direct precedent found in '
     'our search.',
     'Innovation, Figure 1', 3),
    ('gaps', 'The gaps the project closes',
     'What the 2020–2026 literature has done for each component, and the CERTAIN-COAST innovation that closes each gap '
     '(codes as in the Innovation document).',
     'State of the Art, Figure 2', 3),
    ('window', 'The certified safe operating window',
     'The certified safe window (green) in the plane of wellfield pumping and port dewatering, today and at two higher '
     'relative sea levels; it closes at R = 0.45 m. Red: the most dewatering before seawater reaches the wellfield (95%); '
     'blue: the least dewatering that keeps liquefaction within its limit (95%); dashed: the same limits without margins; '
     'dotted: the water demand. Synthetic transect with illustrative values.',
     'Methodology, Section 7', 4),
    ('sec_horizon', 'Single-hazard plans believe they have decades more',
     'Years of safe operation believed by plans that watch one hazard, against the certified joint horizon of 38 years; '
     'hatched: years believed safe that are not. Synthetic transect with illustrative values.',
     'Security Relevance, Figure 2; Methodology, Section 7.3', 4),
    ('evidence', 'A certified alarm margin, tested before the project',
     'Range over storylines of the share of seasons above the chloride limit: 4–9% with the extreme-aware margin of M1, '
     '13–21% with a static alarm. Tests on a synthetic coast, not results at Durrës.',
     'Innovation, Figure 2', 4),
    ('between', 'What happens between samples (review XI, PATH-GO)',
     'One simulated season with monthly samples: chloride crosses 250 mg/L between two samples that both look safe; the '
     'online forecast jumps at each sample and decays between them. In tests a crossing within the season was 34 times '
     'likelier than an exceedance on a sampling date; CERTAIN-COAST reports this chance as a certified band (M10).',
     'Review XI (PATH-GO), Figure 1, panel b', 5),
    ('network', 'A network that corrects its own sensors (review X, INTERVENTION-GO)',
     '(a) Worst-case information of the network against the number of sensors when air pressure, logger drift, cable '
     'cross-talk and model error correlate the errors: buying a barometer and hub reference channels with the piezometers '
     '(orange) is best at every budget, and the certified bound Ū shows how far any network can be from the best one. '
     '(b) On 14 candidates the greedy-plus-exchange design equals the exhaustive optimum. Synthetic test bed (M9).',
     'Review X (INTERVENTION-GO), Figures T34–T35', 5),
    ('ladder', 'Milestones and evidence gates',
     'Each milestone raises the claim the project can make by one rung; orange diamonds are the evidence gates (MS3, MS4, '
     'MS5) with thresholds fixed in advance; the shaded band is the twelve months of live operation; triangles mark the '
     'reports to the SPS Programme.',
     'Milestones, Figure 1', 6),
    ('pathway', 'Impact pathway',
     'From the work packages to outputs (deliverables), outcomes (what the users do differently) and impacts. Italic '
     'notes: the condition for each step.',
     'Impact, Figure 1', 6),
]


def make_figures(work):
    import build_introduction as BI
    import build_security as BS
    import build_nato_method as NM
    import build_innovation as BIN
    import build_sota as BSO
    import build_milestones as BMS
    import build_impact as BIM
    import method_figs as MF
    with open(os.path.join(HERE, 'method_window.json')) as fh:
        W = json.load(fh)
    p = {k: os.path.join(work, f'{k}.png') for k, *_ in FIGS}
    BI.fig_system(p['system'])
    BS.fig_chain(p['sec_chain']); BS.fig_horizon(p['sec_horizon'], W)
    NM.fig_chain(p['method'])
    BIN.fig_chain(p['innov']); BIN.fig_evidence(p['evidence'])
    BSO.fig_gaps(p['gaps'])
    MF.fig_window(p['window'], (0.0, 0.25, 0.45), ('Today (R = 0)', 'R = 0.25 m', 'R = 0.45 m'))
    BMS.fig_ladder(p['ladder'])
    BIM.fig_pathway(p['pathway'])
    # the two preparatory reviews, built by their own scripts (separate processes: separate module paths)
    for d, script in (('shtegu_go', 'shtegu_figs.py'), ('nderhyrja_go', 'nderhyrja_figs.py')):
        out = os.path.join(work, d)
        subprocess.run([sys.executable, os.path.join(EXP, d, script), out], check=True, capture_output=True)
    im = Image.open(os.path.join(work, 'shtegu_go', 'fig_scheme.png'))
    w, h = im.size
    panel = im.convert('RGB').crop((int(0.445 * w), int(0.10 * h), w, h))   # panel (b) only, without its panel title
    from PIL import ImageChops
    box = ImageChops.difference(panel, Image.new('RGB', panel.size, 'white')).getbbox()   # trim the white margins
    panel.crop((max(box[0] - 20, 0), max(box[1] - 20, 0), min(box[2] + 20, panel.size[0]),
                min(box[3] + 20, panel.size[1]))).save(p['between'])
    Image.open(os.path.join(work, 'nderhyrja_go', 'fig_t34.png')).save(p['network'])
    return p


def styles():
    pdfmetrics.registerFont(TTFont('DV', FONT)); pdfmetrics.registerFont(TTFont('DVB', FONT_B))
    pdfmetrics.registerFont(TTFont('DVI', FONT_I)); pdfmetrics.registerFont(TTFont('SYM', SYMBOLS))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily('DV', normal='DV', bold='DVB', italic='DVI', boldItalic='DVB')
    return dict(
        title=ParagraphStyle('t', fontName='DVB', fontSize=17, leading=21, textColor=NAVY, alignment=1, spaceAfter=4),
        sub=ParagraphStyle('s', fontName='DV', fontSize=10.5, leading=14, textColor=NAVY, alignment=1, spaceAfter=8),
        body=ParagraphStyle('b', fontName='DV', fontSize=9.5, leading=12.5, spaceAfter=6),
        h=ParagraphStyle('h', fontName='DVB', fontSize=11.5, leading=14, textColor=NAVY, spaceBefore=4, spaceAfter=4),
        fig=ParagraphStyle('f', fontName='DVB', fontSize=10.5, leading=13, textColor=NAVY, spaceAfter=3),
        cap=ParagraphStyle('c', fontName='DVI', fontSize=8.6, leading=11, textColor=GREY, spaceBefore=3),
        src=ParagraphStyle('r', fontName='DV', fontSize=7.8, leading=10, textColor=GREY, spaceAfter=10),
        toc=ParagraphStyle('o', fontName='DV', fontSize=9.2, leading=11.5),
    )


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('DV', 7.8); canvas.setFillColor(GREY)
    canvas.drawString(2.0 * cm, 1.1 * cm, 'CERTAIN-COAST — illustrative figures (optional upload, NATO SPS call 2027-1)')
    canvas.drawRightString(A4[0] - 2.0 * cm, 1.1 * cm, f'page {doc.page} of 6')
    canvas.restoreState()


def block(S, n, key, title, cap, src, path, max_h):
    w, h = Image.open(path).size
    width = WIDTH
    height = width * h / w
    if height > max_h:                       # keep the page budget: scale down very tall figures
        width, height = width * max_h / height, max_h
    return KeepTogether([Paragraph(f'Figure {n}. {title}', S['fig']), RLImage(path, width=width, height=height),
                         Paragraph(cap, S['cap']), Paragraph(f'Source: CERTAIN-COAST {src}.', S['src'])])


def main(out):
    S = styles()
    work = tempfile.mkdtemp()
    paths = make_figures(work)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.5 * cm,
                            bottomMargin=1.7 * cm, title='CERTAIN-COAST — illustrative figures',
                            author='CERTAIN-COAST applicants', subject=FULL)
    story = [Paragraph('CERTAIN-COAST — illustrative figures', S['title']), Paragraph(FULL, S['sub']),
             Paragraph('Optional upload of the "Project plan" tab of the SPS grant platform (NATO SPS call 2027-1). Twelve '
                       'figures from the proposal documents and the preparatory reviews of 2026. Results of synthetic tests '
                       'use illustrative values; they are not results at Durrës, which the project calibrates and verifies '
                       'on site.', S['body']),
             Paragraph('Contents', S['h'])]
    rows = [[f'Figure {i}', t, f'page {pg}'] for i, (_, t, _, _, pg) in enumerate(FIGS, start=1)]
    toc = Table([[Paragraph(c, S['toc']) for c in r] for r in rows], colWidths=[2.0 * cm, 13.0 * cm, 2.0 * cm])
    toc.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 0.3, HexColor('#D5DAE1')),
                             ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)]))
    story += [toc, Spacer(1, 0.4 * cm)]
    page = 1
    for i, (key, title, cap, src, pg) in enumerate(FIGS, start=1):
        if pg != page:
            story.append(PageBreak()); page = pg
        max_h = 9.6 * cm if pg == 1 else (6.6 * cm if pg == 4 else 10.4 * cm)
        story.append(block(S, i, key, title, cap, src, paths[key], max_h))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print('saved', out, '| figures', len(FIGS))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Illustrative_Figures.pdf')
