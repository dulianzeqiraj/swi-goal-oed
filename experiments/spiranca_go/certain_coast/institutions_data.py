"""CERTAIN-COAST: content of the one-page institution overviews (used by build_institutions.py).

Roles, tasks and shares of time follow the Partnership section and the application form text. Facts about each
institution are written only from the sources listed on its page (official pages, registers, journals and, where
marked in the commit history, search-result excerpts checked on 1 November 2026); everything else is a [placeholder]
for the applicants (yellow in the Word file).

The Faculty of Geology and Mining (Department of Energy Resources) takes part for UPT. The form allows
no more than one page per institution, so UPT has one page with a column for each unit."""

UPT = dict(
    role='Institution of the NATO-country Project Director (NPD) · Albania · coordinator',
    name='Polytechnic University of Tirana (UPT)',
    local='Universiteti Politeknik i Tiranës · Sheshi "Nënë Tereza" Nr. 4, 1001 Tirana, Albania · <https://upt.edu.al>',
    intro='A public university (Statute, Article 1), institutionally accredited by ASCAL until January 2028. Its roots are '
          'in the Higher Polytechnic Institute founded in 1951; it became a university in 1991 and has seven faculties and '
          'the Institute of Geosciences. Its Faculty of Geology and Mining, through the Department of Energy Resources, takes '
          'part.',
    units=[
        dict(title='Faculty of Geology and Mining (FGJM): faculty of the Project Director',
             sub='Fakulteti i Gjeologjisë dhe i Minierave · Rruga e Elbasanit, Tirana · <https://fgjm.edu.al>',
             lines=[
                 'Four departments, among them the Department of Energy Resources of the Project Director.',
                 'Degrees in geological, geoinformatics and geoenvironmental engineering; MSc in Engineering Geology and '
                 'Hydrogeology and in Geoinformatics; PhD in Geology and Environment.',
                 'An aquifer that supplies Durrës: UPT researchers showed seawater advancing into the Fushë Kuqe aquifer, '
                 'up to 5.5% seawater in coastal sectors (Cenameri and Beqiraj, 2016), and analysed the hydrochemistry of '
                 'the Tirana–Fushë Kuqe aquifer (Raço et al., 2022).',
                 'Coastal hazards: doctoral theses on the geological risk of the Kryevidh–Golem coast with GIS (2021) and '
                 'on coastline change of the Shkumbin and Seman deltas from geospatial and geodetic data (2022).',
                 'Laboratories of the Energy Resources department include fluid mechanics in porous media and modelling '
                 'of reservoirs and aquifers.',
                 'Networks: CEEPUS RS-0038 "EURO Geo-Sci"; EIT Deep Tech Talent pledger; organiser of the GENRE 2025 '
                 'international geoscience conference (Tirana, November 2025).',
             ]),
    ],
    glance=[
        ('Project Director', 'Assoc. Prof. Dr. Dulian Zeqiraj, Department of Energy Resources, FGJM; ORCID '
                             '0000-0002-5305-3048'),
        ('Team', 'Prof. Dr. Arjan Beqiraj; Dr. Bardhosh Seitaj; Dr. Esmeralda Zeqo; MSc Aurela Jahja; laboratory '
                 'technician Sonata Pregja (FGJM); MSc Armida Brakaj, mathematician (Faculty of Mathematical Engineering and '
                 'Physics Engineering)'),
        ('Open code of the team', 'https://github.com/dulianzeqiraj/certain-coast (MATLAB and GNU Octave, Apache 2.0), '
                                  'archived on Zenodo, DOI 10.5281/zenodo.24148762'),
    ],
    role_text=[
        'FGJM coordinates the project, administers the NATO grant through UPT and chairs the steering committee (WP7). '
        'It leads coastal motion and relative sea level (WP1), the monitoring network (WP4) and the twelve months of live '
        'operation with the end-user (WP5), and hosts early-career researchers (WP6).',
    ],
    projects=[
        'Key publications: Cenameri and Beqiraj (2016), Bulletin of the Geological Society of Greece 50(2), 665–670; '
        'Raço et al. (2022), Journal of Ecological Engineering 23(8), 327–340, doi:10.12911/22998993/151073; '
        'Zeqiraj (2026), Journal of Hydrology 680, 136559, doi:10.1016/j.jhydrol.2026.136559; Zeqiraj and Beqiraj (2026), '
        'Journal of Contaminant Hydrology 283, 105086, doi:10.1016/j.jconhyd.2026.105086; Zeqiraj, Beqiraj, Jahja, Seitaj, '
        'Progni and Zeqo (2026), Journal of Hazardous Materials Advances 23, 101261, doi:10.1016/j.hazadv.2026.101261.',
        'Preparatory work (2026): eleven reviews with tested methods and a calibrated chloride model of the Fushë-Kuqe '
        'aquifer (technical annex, on request). Projects: modelling, simulation and optimisation of formation treatment '
        'in the carbonate reservoir of the Amonicë oil field, with Albpetrol (AKKSHI, 2025–2026; the NPD is principal '
        'investigator); reconstruction of the groundwater vulnerability map of Albania (UPT institutional project; the NPD '
        'is co-investigator).',
    ],
    new=[
        'FGJM brings its record of seawater intrusion and coastal hazards at Durrës; CERTAIN-COAST turns it into one '
        'warning service whose miss rates are stated in advance and verified live, and that the university keeps running '
        'after the project.',
    ],
    sources=[
        ('UPT history', 'https://upt.edu.al/university/history/?lang=en'),
        ('UPT statute', 'https://geo.edu.al/rc/doc/STATUTI_1_I_UPT_4982.pdf'),
        ('ASCAL register', 'https://www.ascal.al/sq/akreditimi/institucione-te-akredituara'),
        ('UPT units (2024)', 'https://upt.edu.al/emerohen-dekanet-e-rinj-ne-universitetin-politeknik-te-tiranes/'),
        ('FGJM contact', 'https://fgjm.edu.al/kontakt/'),
        ('departments', 'https://fgjm.edu.al/departamentet/'),
        ('bachelor', 'https://fgjm.edu.al/bachelor/'),
        ('master', 'https://fgjm.edu.al/master/'),
        ('PhD', 'https://fgjm.edu.al/doktorature/'),
        ('theses', 'https://fgjm.edu.al/disertacione/'),
        ('laboratories', 'https://fgjm.edu.al/programet-e-studimit-ne-dbe/'),
        ('CEEPUS', 'https://ceepus.rgf.bg.ac.rs/?page_id=39'),
        ('EIT pledge', 'https://www.eitdeeptechtalent.eu/the-pledge/meet-the-pledgers/polytechnic-university-of-tirana-faculty-of-geology-and-mining/'),
        ('GENRE 2025', 'https://genre.fgjm.edu.al/'),
        ('Cenameri and Beqiraj 2016', 'https://ejournals.epublishing.ekt.gr/index.php/geosociety/article/view/11772'),
        ('Raço et al. 2022', 'https://doi.org/10.12911/22998993/151073'),
        ('EMSC members', 'https://m.emsc-csem.org/about_us/who_we_are/'),
    ],
)

PPD = dict(
    role='Institution of the partner-country Project Director (PPD) · Qatar (NATO partner country, Istanbul Cooperation Initiative)',
    name='Environmental Science Center (ESC), Qatar University',
    local='مركز العلوم البيئية – جامعة قطر · P.O. Box 2713, Doha, Qatar · <https://esc.qu.edu.qa>',
    glance=[
        ('Type', 'University: a research center of Qatar University'),
        ('Research team page', '<https://esc.qu.edu.qa>'),
        ('Project Director', 'Prof. Jassim Al-Khayat, Research Professor and Manager of the research vessel Janan; employed '
                             'and resident in Qatar; 20% of working time on the project'),
        ('Team', 'Prof. Fares AlMomani (Acting Director of the Center), Dr. Oguz Yigiterhan and Dr. Bruno Welter Giraldes '
                 '(Research Associate Professors), 5% each; early-career researchers recruited by the project'),
        ('Role', 'Training, transfer and dissemination (WP6), including a transfer study on the east coast of Qatar'),
    ],
    capabilities=[
        'Research groups in physical and chemical oceanography, earth sciences, and marine and terrestrial ecology: '
        'sea-level rise, waves, currents, sediment transport, groundwater resources, GIS, coastal pollution and hazard '
        'risks, remote sensing and coastal monitoring.',
        'Water quality, water resource management, groundwater protection and salinity impacts (Prof. AlMomani); '
        'oceanography and biogeochemistry of the central Arabian Gulf (Dr. Yigiterhan); coastal ecology, mangroves and '
        'ecosystem restoration (Prof. Al-Khayat, Dr. Welter Giraldes).',
        'UNESCO Chair in Marine Sciences at Qatar University: oceanography of the Arabian Gulf, including sea-level rise, '
        'with capacity building (2021–2024, renewed to 2028).',
    ],
    resources=[
        'Chemical and sediment analysis laboratories; a Remote Sensing and GIS Laboratory; the research vessel RV Janan with '
        'oceanographic instruments.',
        'For the transfer site on the east coast of Qatar: maps, hydrography, sea level, satellite data and reports.',
    ],
    projects=[
        'Monitoring shoreline changes and assessment of coastal resources between Al Arish and Al Ghariyah, Qatar, with '
        'remote sensing and GIS (QUCG-ESC-25/26-659, 2025–2027); high-resolution wind and wave modelling for the EEZ of '
        'Qatar (QUCG-ESC-25/26-650, 2025–2027).',
        'Backer, S. A., et al. (2026). The shoreline shifts: a comprehensive review of change analysis focusing Arabian Gulf '
        'within global context. Regional Studies in Marine Science 102, 105433. <https://doi.org/10.1016/j.rsma.2026.105433>',
        'Al-Ansari, E. S., et al. (2022). Seasonal variability of hydrography of the east coast of Qatar, central Arabian '
        'Gulf. Arabian Journal of Geosciences 15, 1659. <https://doi.org/10.1007/s12517-022-10927-4>',
    ],
    role_text=[
        'Leads training, transfer and dissemination (WP6): two-month exchanges of its early-career researchers in Durrës, a '
        'transfer study on the east coast of Qatar carried out with the project\'s tools and the Albanian team, a regional '
        'workshop, and a user-side review of the bulletins and operating procedures.',
        'The coupled model, its surrogate and the certified-alarm algorithm are built and run by the NATO-country team.',
    ],
    new=[
        'Tests within the project whether certified warnings transfer to the east coast of Qatar, a low coast whose ports, '
        'industries and energy facilities face seawater intrusion, coastal flooding and erosion, and brings the method home '
        'through trained young researchers and open software.',
    ],
    sources=[],   # facts from the partner form of 9 November 2026, written by the Qatar team
)

EU = dict(
    role='End-user · Albania · in-kind contribution; letter of support and end-user commitment attached separately',
    name='Institute of Geosciences (IGJEO), Polytechnic University of Tirana',
    local='Instituti i Gjeoshkencave (IGJEO), Universiteti Politeknik i Tiranës, Rruga Don Bosko 60, Tirana.',
    glance=[
        ('Institute of Geosciences (IGJEO)',
         '**Instituti i Gjeoshkencave** (Institute of Geosciences, IGJEO), a research and development institution and a '
         'main unit of the Polytechnic University of Tirana, formerly the Institute of Geosciences, Energy, Water and '
         'Environment (IGJEUM), with departments of hydrology, geology, meteorology and seismology. Head: Prof. Dr. Ylber '
         'Muceku. <https://www.geo.edu.al>\n'
         '**In CERTAIN-COAST:** the end-user. It designates a contact person and a small team for the steering committee, '
         'agrees the warning thresholds for earthquakes and extreme sea levels, reviews the live bulletins and shares the '
         'data of its stations under a data agreement; its staff are trained and it receives the software and the '
         'operating procedures at the hand-over. Staff time and data in kind; no SPS funds.'),
        ('Port and energy landfall',
         'The Port of Durrës and the landfall of the Trans Adriatic Pipeline near Fier are assessed from satellite radar, '
         'GNSS and public data only; no access or data from their owners is needed.'),
    ],
    role_text=[
        'The end-user names a contact person and takes part in setting the thresholds (T3.1), reviews the live bulletins '
        '(WP5), shares station data under a data agreement and receives the software and the procedures at the hand-over '
        '(MS7).',
    ],
    new=[
        'The monitoring network is drilled by the project on public land and stays in Albania with the Polytechnic '
        'University of Tirana, which keeps the bulletins running for the end-user after the project.',
    ],
    sources=[('Institute of Geosciences (IGJEO)', 'https://www.geo.edu.al/Rreth_nesh/IGJEO/'),
             ('Prof. Dr. Ylber Muceku', 'https://www.geo.edu.al/Rreth_nesh/Drejtoria/Ylber_MUCEKU.html')],
    checked='12 November 2026',
)

INST = [UPT, PPD, EU]
