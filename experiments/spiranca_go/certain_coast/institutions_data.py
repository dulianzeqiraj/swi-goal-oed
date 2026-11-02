"""CERTAIN-COAST: content of the one-page institution overviews (used by build_institutions.py).

Roles, tasks and shares of time follow the Partnership section and the application form text. Facts about each
institution are written only from the sources listed on its page (official pages, registers, journals and, where
marked in the commit history, search-result excerpts checked on 1 November 2026); everything else is a [placeholder]
for the applicants (yellow in the Word file).

The Faculty of Geology and Mining and the Institute of Geosciences are units of one university (UPT). The form allows
no more than one page per institution, so UPT has one page with a column for each unit."""

UPT = dict(
    role='Institution of the NATO-country Project Director (NPD) · Albania · coordinator',
    name='Polytechnic University of Tirana (UPT)',
    local='Universiteti Politeknik i Tiranës · Sheshi "Nënë Tereza" Nr. 4, 1001 Tirana, Albania · <https://upt.edu.al>',
    intro='A public university (Statute, Article 1), institutionally accredited by ASCAL until January 2028. Its roots are '
          'in the Higher Polytechnic Institute founded in 1951; it became a university in 1991 and has seven faculties and '
          'the Institute of Geosciences. Its Faculty of Geology and Mining takes part, with the Institute of Geosciences as '
          'research partner [delete the right-hand column if the Institute does not take part].',
    units=[
        dict(title='Faculty of Geology and Mining (FGJM): faculty of the Project Director',
             sub='Fakulteti i Gjeologjisë dhe i Minierave · Rruga e Elbasanit, Tirana · <https://fgjm.edu.al>',
             lines=[
                 'Four departments: Earth Sciences; Applied Geology and Geoinformatics; Mineral Resources Engineering; '
                 'Energy Resources [confirm the official names].',
                 'Degrees in geological, geoinformatics and geoenvironmental engineering; MSc in Engineering Geology and '
                 'Hydrogeology and in Geoinformatics; PhD in Geology and Environment.',
                 'An aquifer that supplies Durrës: UPT researchers showed seawater advancing into the Fushë Kuqe aquifer, '
                 'up to 5.5% seawater in coastal sectors (Cenameri and Beqiraj, 2016), and analysed the hydrochemistry of '
                 'the Tirana–Fushë Kuqe aquifer (Raço et al., 2022).',
                 'Coastal hazards: doctoral theses on the geological risk of the Kryevidh–Golem coast with GIS (2021) and '
                 'on coastline change of the Shkumbin and Seman deltas from geospatial and geodetic data (2022).',
                 'Laboratories of the Energy Resources department include fluid mechanics in porous media and modelling '
                 'of reservoirs and aquifers; [geotechnical, hydrochemical and geophysical laboratories and field '
                 'equipment: confirm].',
                 'Networks: CEEPUS RS-0038 "EURO Geo-Sci"; EIT Deep Tech Talent pledger; organiser of the GENRE 2025 '
                 'international geoscience conference (Tirana, November 2025).',
             ]),
        dict(title='Institute of Geosciences (IGEO): research partner [if it takes part]',
             sub='Instituti i Gjeoshkencave · Rruga Don Bosko 60, Tirana · <https://www.geo.edu.al>',
             lines=[
                 'National research centre for geology, seismology, meteorology, hydrology and the environment; '
                 'formerly the Institute of Geosciences, Energy, Water and Environment (IGEWE).',
                 'Operates the Albanian Seismological Network (FDSN code AC): broadband stations in real time, ten '
                 'short-period stations added with the UNDP RESEAL programme, and a strong-motion network.',
                 'Permanent GNSS stations, two of them (KRYE, KULL) installed near the source of the 26 November 2019 '
                 'earthquake; a GNSS geodynamic monitoring centre equipped in 2025.',
                 'National hydrological network (105 manual and 25 automatic stations) with a daily hazard bulletin for '
                 'civil protection; national meteorological network, with observations at Durrës since 1868.',
                 'On the 2019 earthquake: strong-motion records of the mainshock at seven stations and an ambient-noise '
                 'survey of 76 sites in Durrës with ITSAK (February 2020). Also the 2021 seismic hazard maps of Albania.',
                 'NATO Science for Peace project BSHAP (SfP 983054), harmonized seismic hazard maps of the Western '
                 'Balkans; EMSC member, data contributor to ORFEUS and FDSN, CTBTO National Data Centre.',
             ]),
    ],
    glance=[
        ('Project Director', '[Name, position], FGJM; [30%] of working time on the project'),
        ('Team', '[FGJM members]; [IGEO members, 15%]; early-career researchers recruited by the project'),
        ('Research team page', '[link to the web page of the research team]'),
    ],
    role_text=[
        'FGJM coordinates the project, administers the NATO grant through UPT and chairs the steering committee (WP7). '
        'It leads coastal motion and relative sea level (WP1), the monitoring network (WP4) and the twelve months of live '
        'operation with the operators (WP5), and hosts early-career researchers (WP6).',
        'IGEO provides seismic, strong-motion, GNSS, hydrological and meteorological data for the Durrës coast under a data '
        'agreement by Month 3 (T7.2). It joins the monitoring network (WP4), where its 2020 ambient-noise survey is a '
        'baseline for the seismic-velocity work (T4.4), and the post-event protocol (T5.4).',
    ],
    projects=[
        'Key publications: Cenameri and Beqiraj (2016), Bulletin of the Geological Society of Greece 50(2), 665–670; '
        'Raço et al. (2022), Journal of Ecological Engineering 23(8), 327–340, doi:10.12911/22998993/151073; '
        '[3–5 publications of the project team, with DOI].',
        '[2–3 relevant projects of the team: title, funder, years, role]',
    ],
    new=[
        'One university brings both ends of the warning chain: FGJM\'s record of seawater intrusion and coastal hazards '
        'at Durrës, and IGEO\'s national seismic, geodetic and hydrometeorological networks. CERTAIN-COAST joins them into '
        'one warning service whose miss rates are stated in advance, verified live and run by the operators after the '
        'project.',
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
        ('IGEO', 'https://www.geo.edu.al/About/IGEO/'),
        ('seismic network', 'https://www.geo.edu.al/Research/Research_Infrastructure/Seismology_Network/'),
        ('FDSN AC', 'https://www.fdsn.org/networks/detail/AC/'),
        ('GNSS centre', 'https://www.geo.edu.al/About/News_and_Announcements/Modernizimi_i_Infrastruktur_s_Komb_tare_GNSS_p_r_Monitorim_Gjeodinamik.html'),
        ('hydrology network', 'https://www.geo.edu.al/Research/Research_Infrastructure/Hydrology_Network/'),
        ('meteorology network', 'https://www.geo.edu.al/Research/Research_Infrastructure/Meteorology_Network/'),
        ('2019 strong motion', 'https://jaguar.emsc-csem.org/Files/news/Earthquakes_reports/Short-Note_EMSC_31122019.pdf'),
        ('ITSAK–IGEWE survey', 'https://www.itsak.gr/uploads/news/earthquake_reports/Report_AmbientNoise_Durres_April2020.pdf'),
        ('hazard maps', 'https://geo.edu.al/Natural_Hazards/Geological_Seismic_Hazard/'),
        ('BSHAP', 'https://hrcak.srce.hr/186022'),
        ('collaborations', 'https://www.geo.edu.al/Collaborators/Department_of_Seismology/'),
        ('EMSC members', 'https://m.emsc-csem.org/about_us/who_we_are/'),
    ],
)

PPD = dict(
    role='Institution of the partner-country Project Director (PPD) · [eligible partner country]',
    name='[Name of the university or research institute]',
    local='[Name in the national language, if different] · [postal address, city, country] · [website]',
    glance=[
        ('Type', '[public university / research institute / other non-profit]'),
        ('Research team page', '[web page of the research group]'),
        ('Project Director', '[Name, position]; employed and resident in [country]; [20%] of working time on the project'),
        ('Team', '[names and positions]; early-career researchers recruited by the project'),
        ('Role', 'Training, transfer and dissemination (WP6), including a transfer study on [the partner coast]'),
    ],
    capabilities=[
        '[Coastal geoscience, hydrogeology or water management in your country: 1–2 examples]',
        '[Teaching and training: courses, schools, supervision of early-career researchers]',
        '[Links with operators or authorities in your country, for the regional workshop]',
    ],
    resources=[
        '[Data on a coast of your country that the team holds or can access: maps, wells, sea level, satellite]',
        '[Teaching rooms, GIS and computers for the transfer study]',
    ],
    projects=[
        '[2–3 relevant projects: title, funder, years, role]',
        '[3–5 key publications of the team, with DOI]',
    ],
    role_text=[
        'Leads training, transfer and dissemination (WP6): two-month exchanges of its early-career researchers in Durrës, a '
        'transfer study on [the partner coast] carried out with the project\'s tools and the Albanian team, a regional '
        'workshop, and a user-side review of the bulletins and operating procedures.',
        'The coupled model, its surrogate and the certified-alarm algorithm are built and run by the NATO-country team.',
    ],
    new=[
        'Tests within the project whether certified warnings transfer to [the partner coast], and brings the method home '
        'through trained young researchers and open software.',
    ],
    sources=[],
)

EU = dict(
    role='End-users · Albania · in-kind contribution; commitment letters attached separately',
    name='End-user organisations',
    local='They set the thresholds, give site access and data, receive the bulletins and run the system after the project.',
    glance=[
        ('Water utility',
         '**Shoqëria Rajonale Ujësjellës Kanalizime Durrës sh.a.**, the regional water supply and sewerage company of '
         'Durrës, licensed by the water regulator ERRU (Decision No. 6 of 22 February 2023); it took over the former '
         'Ujësjellës Kanalizime Durrës on 1 January 2023 and pumps from the Fushë Kuqe and Fushë Milot wellfields. '
         '<https://www.shuk.al/durres>\n'
         '**In CERTAIN-COAST:** agrees the chloride threshold and the joint pumping rule; gives access to wells, records '
         'and staff time; gains certified intrusion warnings, a pumping rule and trained staff.'),
        ('Port',
         '**Autoriteti Portual Durrës** (Durrës Port Authority), a public legal person under Law No. 9130 of 8 September '
         '2003 "On the Port Authority". Durrës handled 94.2% of Albania\'s sea freight in the second quarter of 2026 '
         '(INSTAT). <https://www.durresport.al>\n'
         '**In CERTAIN-COAST:** agrees liquefaction and water-level thresholds; gives site access and geotechnical '
         'records; gains liquefaction and water-level warnings and post-event reports.'),
        ('Energy landfall',
         '[Name of the energy landfall operator] at [location]. [website]\n'
         '**In CERTAIN-COAST:** agrees thresholds for the landfall; gives site access under its security rules and its '
         'design levels; gains stability checks combining shaking, liquefaction and water level.'),
        ('Civil protection',
         '**Agjencia Kombëtare e Mbrojtjes Civile** (National Civil Protection Agency), set up under Law No. 45/2019 '
         '"On Civil Protection" and listed among the structures under the Ministry of Defence; it already receives the '
         'daily hydrological hazard bulletin of the Institute of Geosciences. <https://akmc.gov.al>\n'
         '**In CERTAIN-COAST:** co-designs the post-event protocol; receives one picture of water, port and energy after '
         'events; gains post-event reports, procedures and a policy brief.'),
    ],
    role_text=[
        'Each end-user names a contact person, takes part in setting the thresholds (T3.1), in the dry run before live '
        'operation (MS4) and in the twelve months of live bulletins (WP5), and co-signs the operational milestones.',
    ],
    new=[
        'The users decide when the system is ready: they co-sign the network plan (MS1), the start of live bulletins (MS4), '
        'the bulletin log (MS6) and the hand-over (MS7).',
    ],
    sources=[
        ('ERRU licence', 'https://erru.al/2023/03/01/vendim-nr-6-per-licencimin-e-shoqerise-rajonale-ujesjelles-kanalizime-durres-sh-a/'),
        ('company register', 'https://opencorporates.al/sq/nipt/m22031502m'),
        ('take-over', 'https://durreslajm.al/krijohet-shoqeria-e-re-e-ujesjelles-kanalizime-durres/'),
        ('wellfields (2026)', 'https://www.bulevardnews.com/2026/03/04/durresi-neser-8-ore-pa-uje-shkaku-stacioni-i-pompave-ne-fushe-kuqe-dhe-fushe-milot-nuk-do-te-kene-energji-elektrike/'),
        ('Port Authority law', 'https://durresport.al/port-authority/legislation/'),
        ('INSTAT Q2 2026', 'https://www.instat.gov.al/media/44eas2r0/statistikat-e-transportiti-detar-tr-ii-2026_a.pdf'),
        ('AKMC', 'https://akmc.gov.al/en/about-akmc/'),
        ('Law 45/2019', 'https://akmc.gov.al/en/legislation/'),
        ('Ministry of Defence', 'https://www.mod.gov.al/ministria/strukturat-vartese'),
        ('IGEO hydrology bulletin', 'https://www.geo.edu.al/Services/Departament_of_Hydrology/'),
    ],
)

INST = [UPT, PPD, EU]
