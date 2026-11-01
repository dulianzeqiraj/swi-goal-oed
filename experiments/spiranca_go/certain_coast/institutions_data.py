"""CERTAIN-COAST: content of the one-page institution overviews (used by build_institutions.py).

Roles, tasks and shares of time follow the Partnership section and the application form text. Facts about each
institution are written only from the sources listed on its page; everything else is a [placeholder] for the
applicants (highlighted in yellow in the Word file)."""

NPD = dict(
    role='Institution of the NATO-country Project Director (NPD) · Albania · coordinator',
    name='Faculty of Geology and Mining, Polytechnic University of Tirana [to confirm]',
    local='Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i Tiranës · [postal address], Tirana, Albania',
    glance=[
        ('Type', '[Faculty of a public university: confirm]'),
        ('Websites', '[faculty website]; [university website]'),
        ('Research team', '[web page of the research group or of the Project Director]'),
        ('Project Director', '[Name, position]; [30%] of working time on the project'),
        ('Team', '[names and positions of the faculty members in the project]; early-career researchers recruited by the project'),
        ('Role', 'Coordination (WP7); coastal motion (WP1); monitoring network (WP4); live demonstration (WP5)'),
    ],
    capabilities=[
        '[Hydrogeology and seawater intrusion: the department and staff involved, with 1–2 results on Albanian coastal aquifers]',
        '[Geodesy, GNSS and remote sensing (InSAR): staff and experience]',
        '[Geotechnics and engineering geology: soil testing, liquefaction assessment]',
        'Knowledge of the Durrës coast and working contacts with the water utility, the port, the energy landfall operator and civil protection [confirm and give examples].',
    ],
    resources=[
        '[Laboratories: e.g. geotechnical, hydrochemical, geophysical; main equipment]',
        '[Field equipment: sampling, piezometers, GNSS receivers, geophysical instruments]',
        '[Computing and GIS facilities]',
        'Administration of the NATO grant by the finance office of the institution [confirm].',
    ],
    projects=[
        '[2–3 relevant projects: title, funder, years, role]',
        '[3–5 key publications of the team, with DOI]',
    ],
    role_text=[
        'Coordinates the project, administers the NATO grant and chairs the steering committee (WP7).',
        'Leads the measurement of coastal motion and relative sea level at the assets (WP1) and the design, installation and operation of the monitoring network (WP4).',
        'Runs the twelve months of live operation with the water utility, the port, the energy landfall operator and civil protection (WP5), and hosts early-career researchers (WP6).',
    ],
    new=[
        'Turns field geoscience at the critical infrastructure of Durrës into an operating warning service whose miss rates are stated in advance and verified live, run by the operators after the project.',
    ],
    sources=[],
)

PPD = dict(
    role='Institution of the partner-country Project Director (PPD) · [eligible partner country]',
    name='[Name of the university or research institute]',
    local='[Name in the national language, if different] · [postal address, city, country]',
    glance=[
        ('Type', '[public university / research institute / other non-profit]'),
        ('Websites', '[institution website]; [web page of the research group]'),
        ('Project Director', '[Name, position]; employed and resident in [country]; [30%] of working time on the project'),
        ('Team', '[names and positions]; early-career researchers recruited by the project'),
        ('Role', 'Coupled model and certified surrogate (WP2); certified alarms (WP3); training and transfer (WP6)'),
    ],
    capabilities=[
        '[Numerical modelling of coastal groundwater: variable-density flow and transport; the codes the team uses; 1–2 examples]',
        '[Uncertainty quantification and statistics with guarantees (for example conformal prediction); 1–2 results]',
        '[Machine learning for physical systems: neural-operator or kernel surrogates]',
        '[The partner coast: subsidence, seawater intrusion, ports or energy at the coast, and the data available for the transfer test]',
    ],
    resources=[
        '[Computing: cluster or cloud allocation (cores, GPUs) available to the project]',
        '[Laboratories or field equipment, if any]',
        '[Coastal, groundwater or satellite data the team holds or can access]',
    ],
    projects=[
        '[2–3 relevant projects: title, funder, years, role]',
        '[3–5 key publications of the team, with DOI]',
    ],
    role_text=[
        'Leads the coupled model of the three hazards and its certified fast surrogate (WP2) and the certified multi-hazard alarm with its proofs and back-testing (WP3).',
        'Leads training, transfer and dissemination (WP6), including the test of the method on a second subsiding coast.',
    ],
    new=[
        'Brings the mathematics of certified prediction to a field site with critical infrastructure, and tests within the project whether the method transfers to [the partner coast].',
    ],
    sources=[],
)

ARP = dict(
    role='Albanian research partner (candidate) · data and stations',
    name='[Albanian research partner: e.g. a national geoscience or seismological institute]',
    local='[Name in Albanian] · [postal address]',
    glance=[
        ('Type', '[public research institute]'),
        ('Website', '[website]'),
        ('Team', '[names and positions]; [15%] of working time on the project'),
        ('Role', 'Seismic, sea-level and hydrometeorological data (WP1, WP4); post-event protocol (T5.4)'),
    ],
    capabilities=['[Monitoring networks operated: seismic, strong-motion, GNSS, hydrological, meteorological, sea level]'],
    resources=['[Stations on or near the Durrës coast and the data they provide]'],
    projects=['[relevant projects and reports, for example on the 26 November 2019 earthquake]'],
    role_text=[
        'Provides seismic, sea-level and hydrometeorological data from its stations on the Durrës coast under a data agreement signed by Month 3 (T7.2).',
        'Joins the work on coastal motion (WP1), the monitoring network (WP4) and the post-event protocol after strong earthquakes or surges (T5.4).',
    ],
    new=['Its station records become inputs to warnings with a stated miss rate, and the post-event protocol turns a strong earthquake or storm into new data for the model.'],
    sources=[],
)

EU = dict(
    role='End-users · Albania · in-kind contribution, commitment letters attached separately',
    name='End-user organisations',
    local='They set the thresholds, give site access and data, receive the bulletins and run the system after the project.',
    glance=[
        ('[Durrës water utility]', 'Agrees the chloride threshold and the joint pumping rule; gives access to wells and records and staff time; receives intrusion bulletins; gains certified intrusion warnings, a pumping rule and trained staff.'),
        ('[Durrës Port Authority]', 'Agrees liquefaction and water-level thresholds; gives site access for sensors and geotechnical records; receives bulletins for the port; gains liquefaction and water-level warnings and post-event reports.'),
        ('[Energy landfall operator]', 'Agrees thresholds for the landfall; gives site access under its security rules and design levels; receives bulletins; gains stability checks combining shaking, liquefaction and water level.'),
        ('[National Civil Protection Agency]', 'Co-designs the post-event protocol and receives one picture of water, port and energy after events; gains post-event reports, procedures and a policy brief.'),
    ],
    role_text=[
        'Each end-user names a contact person, takes part in setting the thresholds (T3.1), the dry run before live operation (MS4) and the twelve months of live bulletins (WP5), and co-signs the operational milestones.',
    ],
    new=['The users decide when the system is ready: they co-sign the network plan (MS1), the start of live bulletins (MS4), the bulletin log (MS6) and the hand-over (MS7).'],
    sources=[],
)

INST = [NPD, PPD, ARP, EU]
