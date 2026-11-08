"""CERTAIN-COAST (NATO SPS proposal): Letters of commitment (templates). A cover page (how to use, list of letters,
what makes them strong) and one-page templates: five end-users (water utility, water resources agency AMBU, port authority, Trans Adriatic Pipeline (TAP)
operator, civil protection), the partner-country Project Director's institution, and two optional letters (additional
NATO co-director, Albanian research partner). Placeholders are in square brackets and highlighted in yellow; each
organisation adapts the text to its real commitments, prints it on its letterhead and signs it.
Consistent with the Work Plan months, the Partnership (contents of a commitment letter), the Ethics and Data Management
Plan (restricted data, review of publications) and the Sustainability plan (maintenance agreement by Month 33).

usage: python build_letters.py OUT.docx"""
import re
import sys
import os

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para, heading, table  # noqa: E402
from docx.shared import RGBColor
from docx.oxml.ns import qn

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
ADDRESS = ['NATO Science for Peace and Security (SPS) Programme', 'NATO Headquarters', 'Boulevard Léopold III',
           '1110 Brussels, Belgium']


def run(p, text, bold=False, italic=False, size=11, color=None, hl=False):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name = 'Arial'; r.font.size = Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    if hl:
        r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return r


def ph(p, text, size=11, bold=False):
    """Text with [placeholders] highlighted and **bold** segments."""
    for part in re.split(r'(\[[^\]]+\])', text):
        if not part:
            continue
        if part.startswith('['):
            run(p, part, size=size, bold=bold, hl=True)
        else:
            for j, seg in enumerate(part.split('**')):
                if seg:
                    run(p, seg, size=size, bold=bold or j % 2 == 1)


COMMON_END = [
    'We are ready to co-sign the project\'s Intellectual Property Rights agreement for the clauses that concern the data we provide and restricted information about our site.',
    'We understand that the CERTAIN-COAST bulletins are advisory: operational decisions remain ours, and any warning to the public is issued only by the competent authorities.',
    'We understand that our participation creates no financial obligation; our contribution is in kind. Data we provide will be treated as restricted, used only under a data access agreement for the purposes of the project, and any publication that uses them will be sent to us for review of sensitive content [30] days before submission.',
]

LETTERS = [
    dict(key='utility', title='End-user: water utility of the Durrës wellfields',
         org='Shoqëria Rajonale Ujësjellës Kanalizime Durrës sh.a.', role='end-user (wellfields)',
         intro='Shoqëria Rajonale Ujësjellës Kanalizime Durrës sh.a. supplies drinking water to Durrës from the Fushë Kuqe and Fushë Milot wellfields. Seawater intrusion, land subsidence and the effects of earthquakes on groundwater are real risks to this supply. We therefore support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['access to our production and monitoring wells for the project\'s head, conductivity, temperature and barometric loggers, including a conductivity logger in at least one production well of each wellfield, from Month [4] (installed by Month 12);',
                  'our records of groundwater heads, chloride and pumping rates under a data access agreement to be signed by Month 3;',
                  'support for one campaign a year of laboratory chloride samples taken 1, 3 and 7 days apart at agreed wells (analysed at the project\'s cost);',
                  'staff time to agree the chloride threshold and the acceptable false-alarm rate (Months 13–15) and to develop a joint pumping rule (Months 24–33);',
                  'approval and operational support for a short campaign of safe pumping tests on existing wells, each stopped at an agreed chloride test limit (within Months 24–33);',
                  'participation of [number] staff in the workshops and in the operator training (Months 24–36).'],
         use='We intend to receive and use the certified intrusion bulletins, including the warning that chloride may cross its limit between two laboratory samples, during the twelve months of live operation (Months 23–34), to issue them ourselves in the final months, and to consider adopting an operating procedure for the system. We are willing to discuss an arrangement for its maintenance after the project.'),
    dict(key='port', title='End-user: Durrës Port Authority',
         org='Autoriteti Portual Durrës (Durrës Port Authority)', role='end-user (port)',
         intro='Autoriteti Portual Durrës (Durrës Port Authority) manages the main port of Albania on a subsiding coast exposed to earthquakes, liquefaction and extreme sea levels. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['access to agreed locations in the port for sensors (GNSS, corner reflectors, seismic stations, piezometers), under our port-facility security rules, from Month [4];',
                  'available geotechnical records (CPT and borehole logs) and design levels of the quays under a data access agreement to be signed by Month 3;',
                  'staff time to agree the liquefaction and water-level thresholds (Months 13–15) and to take part in the post-event protocol;',
                  'participation of [number] staff in the workshops and in the operator training (Months 24–36).'],
         use='We intend to receive and use the liquefaction and extreme-water-level bulletins for the port during the live operation (Months 23–34) and to consider adopting an operating procedure for the system. We are willing to discuss an arrangement for its maintenance after the project.'),
    dict(key='energy', title='End-user: Trans Adriatic Pipeline AG (TAP)',
         org='Trans Adriatic Pipeline AG (TAP), Albania Branch', role='end-user (TAP landfall near Fier)',
         intro='Trans Adriatic Pipeline AG (TAP) operates the Trans Adriatic Pipeline. Its landfall near Fier is where the pipeline leaves the Albanian shore for its 105 km offshore section across the Adriatic Sea to Italy. The stability of the landfall depends on the ground and on the sea level at the coast. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['access to agreed locations near the landfall for a small set of sensors (GNSS, corner reflectors, a seismic station and a water-table logger), under our security rules and with our escort, from Month [4];',
                  'the design levels and available geotechnical information needed for the stability checks, under a data access agreement to be signed by Month 3;',
                  'staff time to agree the thresholds for the landfall (Months 13–15);',
                  'participation of [number] staff in the workshops and in the operator training (Months 24–36).'],
         use='We intend to receive and use the stability bulletins for the landfall, combining shaking, liquefaction, water level and subsidence, during the live operation (Months 23–34), and to consider adopting an operating procedure. We are willing to discuss an arrangement for its maintenance after the project.'),
    dict(key='civil', title='End-user: National Civil Protection Agency',
         org='Agjencia Kombëtare e Mbrojtjes Civile (National Civil Protection Agency)', role='end-user (civil protection)',
         intro='Agjencia Kombëtare e Mbrojtjes Civile (National Civil Protection Agency) is responsible for preparedness and response to disasters in Albania. The Adriatic coast from Durrës to Fier, where the drinking-water wells and the main port of Durrës and the landfall of the Trans Adriatic Pipeline near Fier stand on soft, low and subsiding ground, is a priority for us since the earthquake of 26 November 2019. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['a representative on the project steering committee, meeting every six months;',
                  'the triggers for the post-event protocol (earthquake, shaking or water level) and participation in its design;',
                  'participation of [number] staff in the workshops, the operator training and the final demonstration.'],
         use='We intend to receive the bulletins and post-event reports during the live operation (Months 23–34) and to consider including the post-event protocol in our procedures. Any warning to the public will remain our responsibility and will be issued through our own channels.'),
    dict(key='ambu', title='End-user: Water Resources Management Agency (AMBU)',
         org='Agjencia e Menaxhimit të Burimeve Ujore (AMBU)', role='end-user (water resources)',
         intro='Agjencia e Menaxhimit të Burimeve Ujore (AMBU, Water Resources Management Agency) manages the water resources of Albania, including the Tiranë–Fushë Kuqe–Lezhë aquifer that supplies Durrës. Seawater intrusion, record droughts and land subsidence threaten this aquifer. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['access to monitoring wells under our control for the project\'s level and salinity sensors, bought by the project, using existing wells only (no new drilling), from Month [4];',
                  'our records of groundwater levels, chemistry and abstraction for the aquifer, under a data access agreement to be signed by Month 3;',
                  'staff time to agree the chloride warning threshold and the acceptable false-alarm rate (Months 13–15) and to review the pumping and drought rule (Months 24–33);',
                  'participation of [number] staff in the workshops and in the training on the open software (Months 24–36).'],
         use='We intend to use the monitoring design, the chloride early warning for each supply well and the pumping and drought rule in [our monitoring programme and water-use permits for this aquifer], and to consider applying the method to other aquifers of Albania. As agreed, our participation creates no obligations of procurement, ownership or maintenance for AMBU.'),
    dict(key='ppd', title='Partner-country Project Director\'s institution',
         org='[Partner-country university or research institute]', role='partner-country co-director',
         intro='[Partner-country university or research institute], in [eligible partner country], commits to take part in CERTAIN-COAST as the institution of the partner-country Project Director, [title and name], who is employed by us in [eligible partner country].',
         provide=['leadership of training, transfer and dissemination (WP6): two-month exchanges of our early-career researchers on the Durrës coast, a regional workshop and the open release of the results;',
                  'a transfer study of the method on a coast of [eligible partner country], carried out with the project\'s tools and the Albanian team, using open satellite data and available records;',
                  'a user-side review of the bulletins and operating procedures;',
                  'the salaries of our staff and the use of our facilities and computing, as an in-kind contribution;',
                  'participation of [number] early-career researchers in the project.'],
         use='We accept the terms of the NATO SPS Multi-Year Project Handbook and of the award, will sign the SPS MYP Agreement for Joint Research and the project\'s Intellectual Property Rights agreement, and will follow the project\'s data management plan, ethics measures and two-tier dissemination rules.',
         custom_end=True),
    dict(key='ncd', title='Optional: additional NATO co-director\'s institution',
         org='[Institution in a NATO member country]', role='additional NATO co-director',
         intro='[Institution in a NATO member country], in [NATO member country], commits to take part in CERTAIN-COAST as the institution of an additional co-director, [title and name].',
         provide=['expertise and supervision for InSAR time-series processing (WP1) and for seismic velocity monitoring with ambient noise (T4.4);',
                  'the salaries of our staff and the use of our facilities, as an in-kind contribution;',
                  'hosting of early-career researchers for training visits.'],
         use='We accept the terms of the NATO SPS Multi-Year Project Handbook and of the award, will sign the SPS MYP Agreement for Joint Research and the project\'s Intellectual Property Rights agreement, and will follow the project\'s data management plan, ethics measures and dissemination rules.',
         custom_end=True),
    dict(key='arp', title='Optional: Albanian research partner (data and stations)',
         org='[Albanian geoscience or seismological institute]', role='research partner',
         intro='[Albanian geoscience or seismological institute] supports the application of CERTAIN-COAST to the NATO SPS Programme and commits to take part as a research partner.',
         provide=['access to data from our [seismic, strong-motion and GNSS stations / hydrological and meteorological stations] on the Durrës coast under a data agreement to be signed by Month 3;',
                  'technical support for the installation and upkeep of the project\'s seismic and GNSS stations;',
                  'participation in the post-event protocol after strong earthquakes or storms.'],
         use='We intend to continue supporting the geodetic and seismic stations after the project, as foreseen in the sustainability plan, and will follow the project\'s data management plan and dissemination rules.',
         custom_end=True),
]

HOWTO = [
    '**Send each template** to the organisation named in it, with the project summary (Abstract) and the relevant section of the Partnership document.',
    '**The organisation adapts the text** to what it can really commit to, replaces every yellow placeholder, prints the letter on its own letterhead, and has it signed (and stamped, where usual) by a person authorised to commit it.',
    '**Do not sign on behalf of an organisation** and do not send unsigned letters as if they were signed; reviewers check that commitments are genuine.',
    '**Collect the signed letters as PDF and merge them into one file:** the platform (tab 9, End-Users) takes a single PDF with all end-user commitments; keep the originals.',
    '**What the call asks (2027-1):** "an end-user commitment letter for each of the project\'s end-users"; for governmental end-users the form accepts a letter of support from the ministry or agency. Letters go to NATO in English; an Albanian reading copy of the five end-user letters is in CERTAIN-COAST_Letters_of_Commitment_SQ.docx.',
]

STRONG = [
    '**Specific and checkable.** Each letter states what the organisation will provide and when, using the months of the Work Plan (access by Month 3, thresholds in Months 13–15, live operation in Months 23–34), so reviewers can see a real plan rather than general support.',
    '**Security conditions stated up front.** Each end-user letter sets the rules for access and data (restricted tier, review of publications), consistent with the Data Management Plan.',
    '**Responsibilities clear.** The letters say that the bulletins are advisory, that decisions remain with the operators, and that public warnings remain with the authorities.',
    '**Looking beyond the project.** End-users state their intention to use the system, adopt procedures and discuss its maintenance after the project, which supports the Sustainability plan.',
]


def page_break(doc):
    p = doc.add_paragraph(); p.add_run().add_break(WD_BREAK.PAGE)


def letter(doc, L):
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, '[LETTERHEAD OF ' + L['org'].strip('[]').upper() + ']', bold=True, size=10, hl=True)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, '[Place], [date]', size=10.5)
    for i, line in enumerate(ADDRESS):
        p = para(doc, 0 if i < len(ADDRESS) - 1 else 6); run(p, line, size=10.5)
    p = para(doc, 6)
    run(p, 'Subject: ', bold=True, size=10.5)
    run(p, f'Letter of commitment, {L["role"]}, for the NATO SPS Multi-Year Project application CERTAIN-COAST: {FULL}', bold=True, size=10.5)
    p = para(doc, 6); run(p, 'Dear Sir or Madam,', size=10.5)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, L['intro'], size=10.5)
    p = para(doc, 3); run(p, 'In particular, we will provide:', size=10.5)
    for t in L['provide']:
        q = para(doc, 2, 0.6); run(q, '• ', size=10.5); ph(q, t, size=10.5)
    p = para(doc, 6, before=4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, L['use'], size=10.5)
    if not L.get('custom_end'):
        for t in COMMON_END:
            p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, t, size=10.5)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ph(p, 'Our contact person for the project is [name, position, e-mail, telephone].', size=10.5)
    p = para(doc, 10); run(p, 'Yours faithfully,', size=10.5)
    for t in ('[Signature and stamp]', '[Name]', '[Position]', L['org']):
        p = para(doc, 0); ph(p, t, size=10.5)


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Letters of Commitment', bold=True, size=18, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Templates for the organisations to adapt, print on their letterhead and sign. Placeholders are ', italic=True, size=10, color='52606D')
    run(p, '[highlighted]', italic=True, size=10, hl=True); run(p, '.', italic=True, size=10, color='52606D')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ph(p, 'The NATO SPS call requires a commitment letter from each end-user of a Multi-Year Project. CERTAIN-COAST has five '
          'end-users (the water utility, the port authority, the Trans Adriatic Pipeline (TAP), civil protection and the Water '
          'Resources Management Agency, AMBU) and a partner-country co-director; two further letters are optional.')

    heading(doc, 'The letters', 13, before=4)
    rows = [[str(i), L['title'], L['org'].strip('[]'), 'Required' if i <= 6 else 'Optional', '[to send]']
            for i, L in enumerate(LETTERS, start=1)]
    t = table(doc, ['', 'Letter', 'Signed by', 'Status', 'Sent / received'], rows, [0.8, 5.6, 5.0, 2.0, 3.2], size=9.5)
    for r in t.rows[1:]:
        for par in r.cells[4].paragraphs:
            for rn in par.runs:
                rn.font.highlight_color = WD_COLOR_INDEX.YELLOW
    para(doc, 4)
    heading(doc, 'How to use these templates', 13, before=6)
    for i, x in enumerate(HOWTO, start=1):
        q = para(doc, 3, 0.5); run(q, f'{i}. ', bold=True); ph(q, x)
    heading(doc, 'What makes these letters strong', 13, before=6)
    for x in STRONG:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); ph(q, x)

    for i, L in enumerate(LETTERS, start=1):
        p = para(doc, 6); p.paragraph_format.page_break_before = True
        run(p, f'[Template {i} of {len(LETTERS)}: {L["title"]}. Delete this line before printing.]', italic=True, size=9, hl=True)
        letter(doc, L)
    doc.save(out)
    print('saved', out, '|', len(LETTERS), 'letters')


# ------------------------------------------------------------------------------------------------- Albanian copy
SQ_ROLE = {'utility': 'përdorues fundor (fushat e puseve)', 'port': 'përdorues fundor (porti)',
           'energy': 'përdorues fundor (pika e daljes në breg e TAP pranë Fierit)', 'civil': 'përdorues fundor (mbrojtja civile)',
           'ambu': 'përdorues fundor (burimet ujore)'}
SQ = {
    'utility': dict(
        intro='Shoqëria Rajonale Ujësjellës Kanalizime Durrës sh.a. furnizon Durrësin me ujë të pijshëm nga fushat e puseve '
              'të Fushë Kuqes dhe të Fushë Milotit. Depërtimi i ujit të detit, ulja e tokës dhe efektet e tërmeteve në '
              'ujërat nëntokësore janë rreziqe reale për këtë furnizim. Për këtë arsye mbështesim aplikimin e projektit '
              'CERTAIN-COAST në Programin NATO SPS dhe angazhohemi të marrim pjesë si përdorues fundor (end-user).',
        provide=['akses në puset tona të prodhimit dhe të monitorimit për regjistruesit (loggers) e projektit për '
                 'nivelin, përçueshmërinë, temperaturën dhe presionin atmosferik, përfshirë një regjistrues përçueshmërie '
                 'në të paktën një pus prodhimi të çdo fushe puseve, nga Muaji [4] (të instaluar deri në Muajin 12);',
                 'të dhënat tona për nivelet e ujërave nëntokësore, kloridin dhe prurjet e pompimit, sipas një marrëveshjeje '
                 'për aksesin në të dhëna që nënshkruhet deri në Muajin 3;',
                 'mbështetje për një fushatë në vit me kampione laboratorike kloridi të marra me 1, 3 dhe 7 ditë diferencë në '
                 'puse të rëna dakord (analizat paguhen nga projekti);',
                 'kohë të stafit për të rënë dakord për pragun e kloridit dhe shkallën e pranueshme të alarmeve të rreme '
                 '(Muajt 13–15) dhe për të hartuar një rregull të përbashkët pompimi (Muajt 24–33);',
                 'miratim dhe mbështetje operative për një fushatë të shkurtër provash të sigurta pompimi në puse '
                 'ekzistuese, ku secila provë ndalet në një kufi kloridi të rënë dakord (brenda Muajve 24–33);',
                 'pjesëmarrjen e [numri] punonjësve në seminare dhe në trajnimin e operatorëve (Muajt 24–36).'],
        use='Synojmë të marrim dhe të përdorim buletinet e certifikuara për depërtimin e ujit të detit, përfshirë '
            'paralajmërimin se kloridi mund të kalojë kufirin midis dy kampionimeve laboratorike, gjatë dymbëdhjetë muajve '
            'të operimit të drejtpërdrejtë (Muajt 23–34), t\'i lëshojmë vetë në muajt e fundit dhe të shqyrtojmë miratimin e '
            'një procedure operative për sistemin. Jemi të gatshëm të diskutojmë një marrëveshje për mirëmbajtjen e tij pas '
            'projektit.'),
    'port': dict(
        intro='Autoriteti Portual Durrës menaxhon portin kryesor të Shqipërisë, në një bregdet që po ulet dhe që është i '
              'ekspozuar ndaj tërmeteve, lëngëzimit të tokës dhe niveleve ekstreme të detit. Mbështesim aplikimin e projektit '
              'CERTAIN-COAST në Programin NATO SPS dhe angazhohemi të marrim pjesë si përdorues fundor.',
        provide=['akses në vende të rëna dakord brenda portit për sensorët (GNSS, reflektorë këndorë, stacione sizmike, '
                 'piezometra), sipas rregullave tona të sigurisë së portit, nga Muaji [4];',
                 'të dhënat gjeoteknike në dispozicion (prova CPT dhe regjistrime shpimesh) dhe nivelet e projektimit të '
                 'kalatave, sipas një marrëveshjeje për aksesin në të dhëna që nënshkruhet deri në Muajin 3;',
                 'kohë të stafit për të rënë dakord për pragjet e lëngëzimit dhe të nivelit të ujit (Muajt 13–15) dhe për të '
                 'marrë pjesë në protokollin pas ngjarjeve;',
                 'pjesëmarrjen e [numri] punonjësve në seminare dhe në trajnimin e operatorëve (Muajt 24–36).'],
        use='Synojmë të marrim dhe të përdorim buletinet për lëngëzimin dhe nivelet ekstreme të ujit për portin gjatë '
            'operimit të drejtpërdrejtë (Muajt 23–34) dhe të shqyrtojmë miratimin e një procedure operative për sistemin. '
            'Jemi të gatshëm të diskutojmë një marrëveshje për mirëmbajtjen e tij pas projektit.'),
    'energy': dict(
        intro='Trans Adriatic Pipeline AG (TAP) operon Gazsjellësin Trans-Adriatik. Pika e tij e daljes në breg (landfall) '
              'pranë Fierit është vendi ku gazsjellësi largohet nga bregu shqiptar për seksionin detar prej 105 km përmes '
              'Detit Adriatik drejt Italisë. Qëndrueshmëria e pikës së daljes në breg varet nga toka dhe nga niveli i detit '
              'në bregdet. Mbështesim aplikimin e projektit CERTAIN-COAST në Programin '
              'NATO SPS dhe angazhohemi të marrim pjesë si përdorues fundor.',
        provide=['akses në vende të rëna dakord pranë pikës së daljes në breg për një grup të vogël sensorësh (GNSS, '
                 'reflektorë këndorë, një stacion sizmik dhe një regjistrues i nivelit të ujit nëntokësor), sipas '
                 'rregullave tona të sigurisë dhe me shoqërimin tonë, nga Muaji [4];',
                 'nivelet e projektimit dhe të dhënat gjeoteknike në dispozicion që nevojiten për kontrollet e '
                 'qëndrueshmërisë, sipas një marrëveshjeje për aksesin në të dhëna që nënshkruhet deri në Muajin 3;',
                 'kohë të stafit për të rënë dakord për pragjet për pikën e daljes në breg (Muajt 13–15);',
                 'pjesëmarrjen e [numri] punonjësve në seminare dhe në trajnimin e operatorëve (Muajt 24–36).'],
        use='Synojmë të marrim dhe të përdorim buletinet e qëndrueshmërisë për pikën e daljes në breg, që bashkojnë '
            'lëkundjet sizmike, lëngëzimin, nivelin e ujit dhe uljen e tokës, gjatë operimit të drejtpërdrejtë (Muajt '
            '23–34), dhe të shqyrtojmë miratimin e një procedure operative. Jemi të gatshëm të diskutojmë një marrëveshje '
            'për mirëmbajtjen e sistemit pas projektit.'),
    'civil': dict(
        intro='Agjencia Kombëtare e Mbrojtjes Civile është përgjegjëse për gatishmërinë dhe reagimin ndaj fatkeqësive në '
              'Shqipëri. Bregdeti nga Durrësi në Fier, ku puset e ujit të pijshëm dhe porti kryesor i Durrësit dhe pika '
              'e daljes në breg e Gazsjellësit Trans-Adriatik pranë Fierit ndodhen në tokë të butë, të ulët dhe që po '
              'ulet, është përparësi për ne që nga tërmeti i 26 nëntorit '
              '2019. Mbështesim aplikimin e projektit CERTAIN-COAST në Programin NATO SPS dhe angazhohemi të marrim pjesë si '
              'përdorues fundor.',
        provide=['një përfaqësues në komitetin drejtues të projektit, që mblidhet çdo gjashtë muaj;',
                 'kushtet që aktivizojnë protokollin pas ngjarjeve (tërmet, lëkundje ose nivel uji) dhe pjesëmarrje në '
                 'hartimin e tij;',
                 'pjesëmarrjen e [numri] punonjësve në seminare, në trajnimin e operatorëve dhe në demonstrimin '
                 'përfundimtar.'],
        use='Synojmë të marrim buletinet dhe raportet pas ngjarjeve gjatë operimit të drejtpërdrejtë (Muajt 23–34) dhe të '
            'shqyrtojmë përfshirjen e protokollit pas ngjarjeve në procedurat tona. Çdo paralajmërim për publikun mbetet '
            'përgjegjësi jona dhe do të lëshohet përmes kanaleve tona.'),
    'ambu': dict(
        intro='Agjencia e Menaxhimit të Burimeve Ujore (AMBU) menaxhon burimet ujore të Shqipërisë, përfshirë akuiferin '
              'Tiranë–Fushë Kuqe–Lezhë që furnizon Durrësin. Depërtimi i ujit të detit, thatësirat rekord dhe ulja e tokës e '
              'kërcënojnë këtë akuifer. Mbështesim aplikimin e projektit CERTAIN-COAST në Programin NATO SPS dhe '
              'angazhohemi të marrim pjesë si përdorues fundor.',
        provide=['akses në puset e monitorimit nën administrimin tonë për sensorët e projektit për nivelin dhe kripësinë e '
                 'ujit, të blerë nga projekti, duke përdorur vetëm puse ekzistuese (pa shpime të reja), nga Muaji [4];',
                 'të dhënat tona për nivelet e ujërave nëntokësore, kiminë e ujit dhe sasitë e ujit të nxjerrë nga '
                 'akuiferi, sipas një marrëveshjeje për aksesin në të dhëna që nënshkruhet deri në Muajin 3;',
                 'kohë të stafit për të rënë dakord për pragun e paralajmërimit për kloridin dhe shkallën e pranueshme të '
                 'alarmeve të rreme (Muajt 13–15) dhe për të shqyrtuar rregullin e pompimit dhe të thatësirës (Muajt 24–33);',
                 'pjesëmarrjen e [numri] punonjësve në seminare dhe në trajnimin për softuerin e hapur (Muajt 24–36).'],
        use='Synojmë të përdorim projektimin e rrjetit të monitorimit, paralajmërimin e hershëm për kloridin për çdo pus '
            'furnizimi dhe rregullin e pompimit dhe të thatësirës në [programin tonë të monitorimit dhe në lejet e '
            'përdorimit të ujit për këtë akuifer], si dhe të shqyrtojmë zbatimin e metodës edhe në akuiferë të tjerë të '
            'Shqipërisë. Siç është rënë dakord, pjesëmarrja jonë nuk krijon për AMBU-në asnjë detyrim prokurimi, pronësie '
            'apo mirëmbajtjeje.'),
}
SQ_END = [
    'Jemi të gatshëm të bashkënënshkruajmë marrëveshjen e projektit për të drejtat e pronësisë intelektuale për nenet që '
    'lidhen me të dhënat që japim dhe me informacionin e kufizuar për objektin tonë.',
    'Kuptojmë se buletinet e CERTAIN-COAST janë këshilluese: vendimet operative mbeten tonat, dhe çdo paralajmërim për '
    'publikun lëshohet vetëm nga autoritetet kompetente.',
    'Kuptojmë se pjesëmarrja jonë nuk krijon asnjë detyrim financiar; kontributi ynë është në natyrë. Të dhënat që japim do '
    'të trajtohen si të kufizuara, do të përdoren vetëm sipas një marrëveshjeje për aksesin në të dhëna dhe vetëm për '
    'qëllimet e projektit, dhe çdo botim që i përdor do të na dërgohet për shqyrtim të përmbajtjes së ndjeshme [30] ditë '
    'para dorëzimit.',
]


def letter_sq(doc, L, S):
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.page_break_before = True
    run(p, 'PËRKTHIM PËR LEXIM. Letra që firmoset dhe i dërgohet NATO-s është versioni në anglisht '
           '(CERTAIN-COAST_Letters_of_Commitment.docx).', italic=True, size=9, color='52606D')
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, '[LETTERHEAD I ' + L['org'].strip('[]').upper() + ']', bold=True, size=10, hl=True)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, '[Vendi], [data]', size=10)
    for i, line in enumerate(ADDRESS):
        p = para(doc, 0 if i < len(ADDRESS) - 1 else 6); run(p, line, size=10)
    p = para(doc, 6)
    run(p, 'Lënda: ', bold=True, size=10)
    run(p, f'Letër angazhimi, {SQ_ROLE[L["key"]]}, për aplikimin e projektit shumëvjeçar NATO SPS CERTAIN-COAST: {FULL}',
        bold=True, size=10)
    p = para(doc, 6); run(p, 'Të nderuar zonja dhe zotërinj,', size=10)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, S['intro'], size=10)
    p = para(doc, 3); run(p, 'Në veçanti, do të ofrojmë:', size=10)
    for x in S['provide']:
        q = para(doc, 2, 0.6); run(q, '• ', size=10); ph(q, x, size=10)
    p = para(doc, 6, before=4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, S['use'], size=10)
    for x in SQ_END:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, x, size=10)
    p = para(doc, 6); ph(p, 'Personi ynë i kontaktit për projektin është [emri, pozicioni, e-mail, telefoni].', size=10)
    p = para(doc, 10); run(p, 'Me respekt,', size=10)
    for x in ('[Firma dhe vula]', '[Emri]', '[Pozicioni]', L['org']):
        p = para(doc, 0); ph(p, x, size=10)


def main_sq(out):
    assert len(SQ_END) == len(COMMON_END)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — Letrat e angazhimit të përdoruesve fundorë (kopje në shqip)', bold=True, size=16, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Përkthim për lexim i pesë letrave të end-users, me të njëjtën përmbajtje si versioni në anglisht. Institucioni '
           'firmos letrën në anglisht në letrën e vet zyrtare; fushat e verdha plotësohen prej tij.', italic=True, size=10,
        color='52606D')
    for L in [x for x in LETTERS if x['key'] in SQ]:
        letter_sq(doc, L, SQ[L['key']])
    doc.save(out)
    print('saved', out, '|', len(SQ), 'letters in Albanian')


def single(out, key, albanian=True):
    """One end-user's letter alone (English, to sign), followed by its Albanian reading copy when there is one, for
    sending by e-mail."""
    L = next(x for x in LETTERS if x['key'] == key)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    letter(doc, L)
    if albanian and key in SQ:
        letter_sq(doc, L, SQ[key])
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] in ('--single', '--single-en'):
        single(sys.argv[3], sys.argv[2], albanian=sys.argv[1] == '--single')
        sys.exit(0)
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Letters_of_Commitment.docx')
    if len(sys.argv) > 2:
        main_sq(sys.argv[2])
