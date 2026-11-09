"""CERTAIN-COAST (NATO SPS proposal): Letters of commitment (templates). A cover page (how to use, list of letters,
what makes them strong) and one-page templates: the end-user, the Albanian Geological Survey (SHGJSH), which administers the groundwater monitoring
network; the Water Resources Management Agency (AMBU), in a narrower in-kind role; the partner-country Project
Director's institution, and two optional letters (additional
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
    dict(key='shgjsh', title='End-user: Albanian Geological Survey (SHGJSH)',
         org='Shërbimi Gjeologjik Shqiptar (Albanian Geological Survey)', role='end-user (groundwater monitoring network and geological hazards)',
         status='Required',
         intro='Shërbimi Gjeologjik Shqiptar (Albanian Geological Survey) administers the groundwater monitoring network of Albania and produces its data, and works on the geological hazards of the country. The coastal plain from Durrës to Fushë Kuqe, with its aquifers, soft sediments, subsidence and active faults, is a priority for our work. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['access to existing monitoring wells of our network on the Durrës–Fushë Kuqe coast for the project\'s level, conductivity, temperature and barometric loggers, bought by the project and installed together with our staff, from Month [4];',
                  'the groundwater-level and chemistry records of our network and [geological and hydrogeological maps and borehole logs] for the coastal plain, under a data access agreement to be signed by Month 3;',
                  'staff time of [2] experts, about [10] working days a year, as an in-kind contribution: for the siting and installation of the sensors (Months 1–12), the agreement of the warning thresholds (Months 13–15) and the review of the bulletins during the live operation (Months 23–34);',
                  'participation of [number] staff in the workshops and in the training on the open software (Months 24–36).'],
         use='We intend to receive and use the certified groundwater and geological-hazard bulletins for the coastal plain during the live operation (Months 23–34), to use the open software and the monitoring design in our groundwater monitoring network, and to consider keeping the project\'s sensors in our network after the project.'),
    dict(key='ambu', title='End-user: Water Resources Management Agency (AMBU), staff time in kind',
         org='Agjencia e Menaxhimit të Burimeve Ujore (AMBU)', role='end-user (water resources)', status='Requested',
         intro='Agjencia e Menaxhimit të Burimeve Ujore (AMBU, Water Resources Management Agency) manages the water resources of Albania, including the Tiranë–Fushë Kuqe–Lezhë aquifer that supplies Durrës. Seawater intrusion, record droughts and land subsidence threaten this aquifer. We support the application of CERTAIN-COAST to the NATO SPS Programme and commit to take part as an end-user.',
         provide=['the data that we hold on water-use permits and abstraction for the Tiranë–Fushë Kuqe–Lezhë aquifer, under a data access agreement to be signed by Month 3; the groundwater-level and chemistry records of the national monitoring network, and access to its wells, are arranged with the Albanian Geological Survey, which administers that network;',
                  'staff time of [2] experts, about [5] working days a year, as an in-kind contribution: to agree the chloride warning threshold and the acceptable false-alarm rate (Months 13–15) and to review the pumping and drought rule against the water-use permits (Months 24–33);',
                  'participation of [2] staff in the workshops and in the training on the open software (Months 24–36).'],
         use='We intend to use the chloride early warning for each supply well and the pumping and drought rule in [our monitoring programme and water-use permits for this aquifer], and to consider applying the method to other aquifers of Albania. Our contribution is staff time in kind; it creates no financial obligation and no obligations of procurement, ownership or maintenance for AMBU.'),
    dict(key='ppd', title='Partner-country Project Director\'s institution (optional: Qatar University signed the Agreement for Joint Research on 5 November)', status='Optional',
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
    '**What the call asks (2027-1):** "an end-user commitment letter for each of the project\'s end-users"; for governmental end-users the form accepts a letter of support from the ministry or agency. Letters go to NATO in English; an Albanian reading copy of the letters of the Albanian organisations is in CERTAIN-COAST_Letters_of_Commitment_SQ.docx.',
]

STRONG = [
    '**Specific and checkable.** Each letter states what the organisation will provide and when, using the months of the Work Plan (access by Month 3, thresholds in Months 13–15, live operation in Months 23–34), so reviewers can see a real plan rather than general support.',
    '**Security conditions stated up front.** Each end-user letter sets the rules for access and data (restricted tier, review of publications), consistent with the Data Management Plan.',
    '**Responsibilities clear.** The letters say that the bulletins are advisory, that decisions remain with the users, and that public warnings remain with the authorities.',
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
    ph(p, 'The NATO SPS call requires a commitment letter from each end-user of a Multi-Year Project. The end-user of '
          'CERTAIN-COAST is the Albanian Geological Survey (SHGJSH), which administers the groundwater monitoring network on '
          'which the warnings are demonstrated; the Water Resources Management Agency (AMBU) has been asked for a narrower '
          'letter (data on water-use permits and staff time in kind, no access to wells). The port and the pipeline '
          'landfall are assessed from satellite and public data only, so no letter is needed from their owners. A letter from the institution of the partner-country co-director is '
          'required; two further letters are optional.')

    heading(doc, 'The letters', 13, before=4)
    rows = [[str(i), L['title'], L['org'].strip('[]'), L.get('status', 'Optional'), '[to send]']
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
SQ_ROLE = {'ambu': 'përdorues fundor (burimet ujore)',
           'shgjsh': 'përdorues fundor (rrjeti i monitorimit të ujërave nëntokësore dhe rreziqet gjeologjike)'}
SQ = {
    'ambu': dict(
        intro='Agjencia e Menaxhimit të Burimeve Ujore (AMBU) menaxhon burimet ujore të Shqipërisë, përfshirë akuiferin '
              'Tiranë–Fushë Kuqe–Lezhë që furnizon Durrësin. Depërtimi i ujit të detit, thatësirat rekord dhe ulja e tokës e '
              'kërcënojnë këtë akuifer. Mbështesim aplikimin e projektit CERTAIN-COAST në Programin NATO SPS dhe '
              'angazhohemi të marrim pjesë si përdorues fundor.',
        provide=['të dhënat që zotërojmë për lejet e përdorimit të ujit dhe për sasitë e ujit të nxjerrë nga akuiferi '
                 'Tiranë–Fushë Kuqe–Lezhë, sipas një marrëveshjeje për aksesin në të dhëna që nënshkruhet deri në Muajin 3; '
                 'të dhënat e nivelit dhe të kimisë së ujërave nga rrjeti kombëtar i monitorimit, si dhe aksesi në puset e '
                 'tij, sigurohen me Shërbimin Gjeologjik Shqiptar, që e administron këtë rrjet;',
                 'kohë të stafit, [2] specialistë, rreth [5] ditë pune në vit, si kontribut në natyrë: për të rënë dakord për '
                 'pragun e paralajmërimit për kloridin dhe shkallën e pranueshme të alarmeve të rreme (Muajt 13–15) dhe për '
                 'të shqyrtuar rregullin e pompimit dhe të thatësirës në raport me lejet e përdorimit të ujit (Muajt 24–33);',
                 'pjesëmarrjen e [2] punonjësve në seminare dhe në trajnimin për softuerin e hapur (Muajt 24–36).'],
        use='Synojmë të përdorim paralajmërimin e hershëm për kloridin për çdo pus furnizimi dhe rregullin e pompimit dhe '
            'të thatësirës në [programin tonë të monitorimit dhe në lejet e përdorimit të ujit për këtë akuifer], si dhe të '
            'shqyrtojmë zbatimin e metodës edhe në akuiferë të tjerë të Shqipërisë. Kontributi ynë është kohë e stafit, në '
            'natyrë; ai nuk krijon asnjë detyrim financiar dhe asnjë detyrim prokurimi, pronësie apo mirëmbajtjeje për '
            'AMBU-në.'),
    'shgjsh': dict(
        intro='Shërbimi Gjeologjik Shqiptar administron rrjetin e monitorimit të ujërave nëntokësore të Shqipërisë dhe '
              'prodhon të dhënat e tij, si dhe punon për rreziqet gjeologjike të vendit. Fusha bregdetare nga Durrësi në '
              'Fushë Kuqe, me akuiferët, sedimentet e buta, uljen e tokës dhe prishjet aktive, është përparësi për punën '
              'tonë. Mbështesim aplikimin e projektit CERTAIN-COAST në Programin NATO SPS dhe angazhohemi të marrim pjesë si '
              'përdorues fundor.',
        provide=['akses në puse ekzistuese të rrjetit tonë në bregun Durrës–Fushë Kuqe për regjistruesit e projektit për '
                 'nivelin, përçueshmërinë, temperaturën dhe presionin atmosferik, të blerë nga projekti dhe të instaluar '
                 'bashkë me stafin tonë, nga Muaji [4];',
                 'të dhënat e nivelit dhe të kimisë së ujërave nga rrjeti ynë dhe [hartat gjeologjike dhe hidrogjeologjike '
                 'dhe të dhënat e shpimeve] për fushën bregdetare, sipas një marrëveshjeje për aksesin në të dhëna që '
                 'nënshkruhet deri në Muajin 3;',
                 'kohë të stafit, [2] specialistë, rreth [10] ditë pune në vit, si kontribut në natyrë: për vendosjen dhe '
                 'instalimin e sensorëve (Muajt 1–12), për pragjet e paralajmërimit (Muajt 13–15) dhe për shqyrtimin e '
                 'buletineve gjatë operimit të drejtpërdrejtë (Muajt 23–34);',
                 'pjesëmarrjen e [numri] punonjësve në seminare dhe në trajnimin për softuerin e hapur (Muajt 24–36).'],
        use='Synojmë të marrim dhe të përdorim buletinet e certifikuara për ujërat nëntokësore dhe rreziqet gjeologjike të '
            'fushës bregdetare gjatë operimit të drejtpërdrejtë (Muajt 23–34), të përdorim softuerin e hapur dhe projektimin '
            'e rrjetit në rrjetin tonë të monitorimit, dhe të shqyrtojmë mbajtjen e sensorëve të projektit në rrjetin tonë '
            'pas projektit.'),
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
    run(p, 'Përkthim për lexim i letrave të institucioneve shqiptare, me të njëjtën përmbajtje si versioni në anglisht. Institucioni '
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
