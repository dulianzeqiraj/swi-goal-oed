"""The thirty paper cards of State of the art V (stakeholder decisions when the source of chloride is unknown):
twelve from Oxford, six from Caltech (with JPL), five from Harvard (one joint with MIT) and seven from MIT, 2020-2026.
Bibliographic data, affiliation strings and abstracts come from the Crossref records of each DOI (November 2026); the
'does' and 'sota' fields keep to the abstract, the other fields are our reading. None of the thirty is a card or a
reference of the earlier reviews in docs/literature (checked by DOI over all 72 documents; ten first choices were
replaced for that reason). Fields: id, inst, year, short, title, authors, venue, links, evidence, does, sota, gap,
source (lesson for diagnosing the source), demand (lesson for meeting the demands), stake (lesson for the stakeholders),
step (innovation step for our problem), comps (components C1-C5 of PREJARDHJA-GO that it informs)."""

_O1 = dict(id='O1', inst='Oxford', year=2023, short='Salinity hides behind coverage statistics',
     title='Hydrogeologic Constraints for Drinking Water Security in Southwest Coastal Bangladesh: Implications for '
           'Sustainable Development Goal 6.1',
     authors='Tanjila Akhter, Maheen Naz, Mashfiqus Salehin, Sharif Tanjim Arif, Sonia Ferdous Hoque, Robert Hope, '
             'Mohammad Rezaur Rahman',
     venue='Water 15(13), 2333 (2023)',
     links=[('doi:10.3390/w15132333', 'https://doi.org/10.3390/w15132333')],
     evidence='Crossref affiliation strings: Sonia Ferdous Hoque and Robert Hope — School of Geography and the '
              'Environment, University of Oxford.',
     does='**Result.** An in-depth field investigation of drinking-water security in southwest coastal Bangladesh. The '
          'rapid growth of groundwater technologies such as tube wells does not mean safe coverage: a complex '
          'hydrogeology gives a high spatial variability of groundwater salinity risk, which also shapes access, '
          'reliability and affordability across supply technologies. National estimates mislead because salinity '
          'substantially lowers the effective coverage (abstract).',
     sota='Field evidence that salinity, not the number of wells, sets the effective drinking-water coverage of a '
          'salinised coast, and that investment must rest on hydrogeologic heterogeneity and water-quality monitoring.',
     gap='It maps where the salinity is, not where it comes from: the source of the chloride and its response to '
         'pumping or drought are not separated, so it cannot say which intervention will work.',
     source='The spatial pattern is evidence: a laterally coherent rise (a seawater wedge) and a patchy one (local '
            'evaporation or return flow) leave different maps, so every supply point should be sampled, not a '
            'regional mean.',
     demand='Count demand as met only when the delivered water is below the limit; a well that turns brackish in the '
            'dry season adds capacity on paper only.',
     stake='Coverage figures that ignore salinity mislead the people who allocate the money; report the effective '
           'supply of each option under each source hypothesis.',
     step='Effective-coverage accounting under source ambiguity: credit each supply option only with the water it '
          'delivers below 250 mg/L under every source still in the plausible set $S(y)$ (C1), so an option counts '
          'only if it stays safe whichever source is true (C2), and publish this ledger to the stakeholders (C5).',
     comps=['C1', 'C2', 'C5'])

_PART1 = [
    dict(id='O2', inst='Oxford', year=2021, short='Greater good versus greater need investments',
         title='Optimizing Rural Drinking Water Supply Infrastructure to Account for Spatial Variations in Groundwater '
               'Quality and Household Welfare in Coastal Bangladesh',
         authors='Orlando Roman, Sonia Ferdous Hoque, Lucinda Ford, Mashfiqus Salehin, Mohammad Monirul Alam, '
                 'Robert Hope, Jim W. Hall',
         venue='Water Resources Research 57(8), e2021WR029621 (2021)',
         links=[('doi:10.1029/2021wr029621', 'https://doi.org/10.1029/2021wr029621')],
         evidence='Crossref affiliation strings: Sonia Ferdous Hoque and Robert Hope — School of Geography and the '
                  'Environment and Smith School of Enterprise and the Environment, University of Oxford; Jim W. Hall — '
                  'School of Geography and the Environment, Environmental Change Institute, University of Oxford.',
         does='**Result.** A study of decisions to invest in drinking-water infrastructure in coastal Bangladesh, where '
              'increasing saline intrusion in aquifers meets high levels of poverty. Multi-objective optimisation '
              'explores the trade-off between maximising overall access to improved water supplies (the greater good) '
              'and maximising access for the population with the lowest welfare (the greater need). It uses '
              'groundwater salinity measurements, an extensive household survey and an audit of drinking-water '
              'infrastructure in one polder of nearly 60,000 people, quantifies the costs of supply options including '
              'deep tube wells, desalination plants and piped systems, and recommends sequences of investments '
              'optimised to specified locations within the polder (abstract).',
         sota='A multi-objective method that turns salinity data, household welfare and asset costs into located, '
              'sequenced investments and makes the trade-off between total access and access for the worst-off '
              'explicit; the authors present it as potentially scalable and transferable to SDG target 6.1.',
         gap='It uses salinity as measured, a map of where the water is saline; why it is saline, and how that will '
             'change once new wells pump, is not part of the optimisation, so a site that is optimal under one source '
             'of salt can fail under another.',
         source='A salinity map is a snapshot: optimising well sites on it assumes that fresh spots stay fresh once '
                'pumped. That holds for some sources and fails for others (upconing under a new deep well, a seawater '
                'front drawn inland), so each site needs its chloride response to pumping under each source hypothesis.',
         demand='Report demand met in two ways, in total and for the poorest households, who may be hit hardest when '
                'supply is rationed; a plan that maximises the first can leave the second short.',
         stake='How much total access to give up for the worst-off is a value choice for the regulator and the public, '
               'not an output of the optimiser; showing the whole trade-off curve lets them make it openly.',
         step='No-regret first investment: optimise a sequence of supply investments (another deep well at C, a second '
              'mobile desalination unit, a blending reservoir) for two objectives, total demand met and demand met '
              'for the poorest households, under the constraint of C2 for every source in $S(y)$. Recompute the '
              'sequence for each smaller set that C1 could return after the next round of tracers: an investment that '
              'comes first in all of them can be built now, and one that does not marks a choice that should wait '
              'for the tracers (C1, C2, C5).',
         comps=['C1', 'C2', 'C5']),

    dict(id='O3', inst='Oxford', year=2021, short='Users pay for reliability, not quality',
         title='Individual choices and universal rights for drinking water in rural Africa',
         authors='Rob Hope, Paola Ballon',
         venue='Proceedings of the National Academy of Sciences 118(40), e2105953118 (2021)',
         links=[('doi:10.1073/pnas.2105953118', 'https://doi.org/10.1073/pnas.2105953118')],
         evidence='Crossref affiliation strings: Rob Hope and Paola Ballon — School of Geography and the Environment, '
                  'University of Oxford, and Smith School of Enterprise and the Environment, University of Oxford.',
         does='**Result (from the significance statement only).** Crossref gives only the significance statement. '
              'Four out of five people without safe drinking water live in rural areas, and the human right to water '
              'identifies affordability, proximity, quality and reliability as attributes of drinking-water services; '
              "how these attributes match people's priorities in meeting the multibillion-dollar cost of maintaining "
              'rural services in Africa to 2030 was unknown. Evidence from Kenya indicates that improving reliability, '
              'by repairing waterpoint faults within 2 days, is the dominant attribute in securing user payments, '
              'while quality and proximity register less support and seem more suited to public funding (abstract).',
         sota='Evidence that user payments follow reliability (fast repair) rather than quality or proximity, which '
              'points to funding in which users pay for reliability and public money carries quality and proximity: '
              'common ground between universal rights and individual choices.',
         gap='From what the statement gives, quality is one attribute among four and earns little of the users\' '
             'payment; a quality failure whose cause is unknown, and who should pay to find the cause, are not '
             'addressed.',
         source='Knowing the source is a quality good, and users give quality little weight in what they pay for; the '
                "tracer programme should therefore be budgeted as a public good (by the regulator or in the utility's "
                'capital plan), not left to the tariff.',
         demand='Reliability is what users notice and pay for: interruptions in the peak season should carry a high '
                'weight in the cost of unmet demand, and a plan that keeps chloride safe by cutting supply will be '
                'judged by its outages.',
         stake='Households and tourism will back spending that prevents outages more readily than spending that lowers '
               'an exceedance probability; the regulator has to defend the chloride risk budget on public grounds.',
         step='Who pays for not knowing the source: split the extra cost of the robust allocation, over the allocation '
              'that would be chosen if the source were known, into the part that avoids outages (a reliability good, '
              'for the tariff) and the part that only keeps $P_k\\le\\alpha$ for every source in $S(y)$ (a quality '
              'good, for public funds), and enter both in the ledger (C2, C5). Test the split with a choice experiment '
              'among households and tourism operators: it holds if their stated payments respond to fewer outages '
              'but not to a lower exceedance probability.',
         comps=['C2', 'C5']),

    dict(id='O4', inst='Oxford', year=2024, short='Field test of a seasonal price cut',
         title='Maintaining groundwater collection over the rainy season with water ATM price reductions: a study in '
               'Kitui County, Kenya',
         authors='Will Ingram, Cliff Nyaga, Peter Mugo, Annah Kavata, Kate Gannon, Patrick Thomson',
         venue='Journal of Water, Sanitation and Hygiene for Development 14(9), 808–818 (2024)',
         links=[('doi:10.2166/washdev.2024.038', 'https://doi.org/10.2166/washdev.2024.038')],
         evidence='Crossref affiliation strings: Patrick Thomson — School of Geography and the Environment, University '
                  'of Oxford, and Department of Engineering Science, University of Oxford.',
         does='**Result.** In semi-arid Kitui County, the service provider FundiFix sees five to ten times less water '
              'collected from its rural water points in the rainy season, with revenues close to zero. Using water '
              'ATMs, which record the volumes dispensed and allow timely price changes, it cut the price from 3 to 1 '
              'KES per jerrycan at three piped schemes over the March–May 2023 rainy season, with a fourth scheme '
              'unchanged as control. This did little to nothing to keep collection at dry-season levels, at a cost of '
              'only 100 USD in lost revenue; price reductions need to be combined with a deeper understanding of user '
              'behaviour, and conditional transfers of water credit are discussed instead (abstract).',
         sota='A low-cost field test with a control, made possible by metered dispensers, showing that a price signal '
              'alone did not keep users at a clean groundwater source across the seasons.',
         gap='It tests a demand lever, not a diagnosis: the variable is price, the outcome is volume, and water quality '
             'and its causes are outside its scope. In our case the lever runs the other way (asking farmers at B, or '
             'users in the peak season, to take less), and behaviour may be just as hard to move.',
         source='Metering is part of the diagnosis: the hypotheses differ in how chloride responds to the volume '
                'pumped, so well-by-well volumes at A, B and C, logged when chloride is sampled, are tracer data, not '
                'just accounts.',
         demand='Do not count on a tariff change to move demand: if the plan needs less water in the peak season or '
                'less irrigation at B, test the lever on a small scale with a control before its effect enters the '
                'allocation.',
         stake='A small trial that fails is cheap and informative (here 100 USD); stakeholders can agree to try '
               'reversible, measured levers instead of arguing about them in the abstract.',
         step='Anytime-valid trial of conditional water credits: offer farmers in part of the farming area around B a '
              'credit, conditional on metered irrigation pumping staying below an agreed cap, keep a comparable group '
              'as control, and track the metered difference with an e-process that is read at every stakeholder '
              'meeting (the machinery of C4 applied to behaviour, not to sources). The credit enters C2 as a decision '
              "variable only once the e-value for a reduction exceeds 20 (a 5% error by Ville's inequality); if it "
              'never does by the agreed end, the trial stops at a small, known cost.',
         comps=['C2', 'C4']),

    dict(id='O5', inst='Oxford', year=2022, short='Short sensor campaigns localise drought warning',
         title='Localizing Hydrological Drought Early Warning Using In Situ Groundwater Sensors',
         authors='W. A. Veness, A. P. Butler, B. F. Ochoa‐Tocachi, S. Moulds, W. Buytaert',
         venue='Water Resources Research 58(8), e2022WR032165 (2022)',
         links=[('doi:10.1029/2022wr032165', 'https://doi.org/10.1029/2022wr032165')],
         evidence='Crossref affiliation strings: S. Moulds — School of Geography and the Environment, University of '
                  'Oxford.',
         does='**Result.** Drought early warning in groundwater-dependent arid zones usually infers exposure from '
              'coarse satellite indicators (rainfall anomalies, soil moisture, vegetation indices), which give a poor '
              'inference of local groundwater availability. In Somaliland, calibrating a lumped groundwater model with '
              'a short series of in situ groundwater-level observations substantially improves the quantification of '
              'local water availability compared with satellite-based indices. Varying the calibration length shows '
              'that a 5-week period capturing both wet- and dry-season conditions provides most of the calibration '
              'capacity, so relocatable sensors can characterise many wells and supplement continuous monitoring of '
              'strategic points (abstract).',
         sota='Shows that a few weeks of direct groundwater-level data, if they span wet and dry conditions, improve '
              'on satellite proxies for local water availability, and proposes relocatable sensors to build large '
              'monitoring systems whose output serves as early-warning evidence for financing and targeting early '
              'action.',
         gap='It measures water quantity (heads), not quality: a head-based drought index cannot say whether rising '
             'chloride is the drought itself or seawater drawn in by the lower heads that the drought causes.',
         source='The weeks that span a change of season carry most of the information; for the diagnosis, the '
                'wet-to-dry transition is when the hypotheses separate, since chloride from intrusion should follow '
                'pumping at A and the coastal head, while chloride from evapoconcentration should follow recharge at '
                'A and B but not at C.',
         demand='Well-by-well availability is a better basis for the drought part of the allocation than regional '
                'indices; a calibrated model of each wellfield gives its yield as the dry season advances.',
         stake='Early-warning evidence is meant to release money for early action; agreeing in advance which observed '
               'signal triggers which action, and who pays, turns monitoring into a decision tool.',
         step='A local drought index for the DRY hypothesis: calibrate a lumped groundwater model for each wellfield '
              'on about five weeks of logger data spanning the wet-to-dry transition, and let its simulated recharge '
              'deficit drive the chloride that DRY predicts, so that the likelihood of DRY in C1 rests on local heads '
              'rather than on a regional rainfall index. C3 chooses which wells receive the relocatable loggers; the '
              'test is whether, on the same tracer data, the local index separates DRY from SWI (excludes one of them '
              'from $S(y)$) more often than the regional index does.',
         comps=['C1', 'C3']),

    dict(id='O6', inst='Oxford', year=2020, short='Drought coincidence sets transfer length',
         title='The Spatial Dynamics of Droughts and Water Scarcity in England and Wales',
         authors='Barnaby Dobson, Gemma Coxon, Jim Freer, Helen Gavin, Mohammad Mortazavi‐Naeini, Jim W. Hall',
         venue='Water Resources Research 56(9), e2020WR027187 (2020)',
         links=[('doi:10.1029/2020wr027187', 'https://doi.org/10.1029/2020wr027187')],
         evidence='Crossref affiliation strings: Barnaby Dobson, Helen Gavin, Mohammad Mortazavi‐Naeini and Jim W. '
                  'Hall — Environmental Change Institute, University of Oxford; Helen Gavin also — Oxford Martin '
                  'School, University of Oxford.',
         does='**Result.** Climate, hydrological and water resource system models are combined at national scale '
              'across England and Wales (80 catchments, 70 water resource zones, 16 water utility companies, supply '
              'for over 50 million people) to explore how droughts and water scarcity interact in space. If a '
              "reservoir's storage is in its first percentile, there is on average a 40% chance that reservoirs in "
              'neighbouring catchments are also at or below their first percentile; the coincidence decays quickly '
              'and stabilises after about 100–150 km, so interbasin transfers meant to enhance drought resilience '
              'need to be at least this long. In a large ensemble of future climate simulations, extreme droughts in '
              'precipitation, streamflow and reservoir storage worsen in every catchment, and the probability of a '
              'year with water use restrictions doubles by 2050 and is four times worse by 2100 (abstract).',
         sota='A connected, national view of drought and scarcity that measures how far drought coincidence reaches '
              'in space, gives a minimum length for transfers that add resilience, and projects a rising probability '
              'of restrictions.',
         gap='It deals with water quantity (droughts in precipitation, streamflow and reservoir storage); groundwater '
             'quality, and a drought that at once raises chloride and weakens the back-up supply, are outside its '
             'scope.',
         source='A drought signal should be spatially coherent, as reservoir droughts are here up to about 100–150 km; a '
                'chloride rise that appears at the same time in distant inland wells with no seawater boundary or '
                'farming nearby points to DRY, and one confined to the coastal strip points to SWI.',
         demand='A back-up is worth only its independence from the shock: a transfer from a basin inside the same '
                'drought footprint may be short exactly when drought raises chloride at A and B.',
         stake='Because the chance of restrictions is projected to rise, a plan that meets the risk budget today will '
               'need costlier actions later to keep meeting it; stakeholders should see that cost path, not only '
               "today's plan.",
         step='Drought-correlated back-up in the chance constraint: in C2, draw the capacity of X jointly with the '
              'recharge scenario, so that under DRY a transfer is short in the same simulated years in which chloride '
              'is high at A and B, instead of taking a fixed capacity. Test by how much the fixed-capacity assumption '
              'understates the exceedance probability under DRY for a transfer from inside and from beyond the '
              'distance at which drought coincidence fades, and for mobile desalination, whose capacity does not '
              'depend on rainfall; the difference is part of what excluding DRY from $S(y)$ is worth (C1, C2).',
         comps=['C1', 'C2']),

    dict(id='O7', inst='Oxford', year=2021, short='Economy-wide drought losses guide reliability',
         title='An Integrated Framework for Risk‐Based Analysis of Economic Impacts of Drought and Water Scarcity in '
               'England and Wales',
         authors='Katie Jenkins, Barnaby Dobson, Christopher Decker, Jim W. Hall',
         venue='Water Resources Research 57(8), e2020WR027715 (2021)',
         links=[('doi:10.1029/2020wr027715', 'https://doi.org/10.1029/2020wr027715')],
         evidence='Crossref affiliation strings: Katie Jenkins and Jim W. Hall — Environmental Change Institute, '
                  'University of Oxford; Christopher Decker — Centre for Socio‐Legal Studies, University of Oxford.',
         does='**Result.** A large ensemble of simulated meteorological droughts is propagated through a national '
              'hydrological model and a water resource systems model to simulate water availability from reservoirs '
              'and groundwater in England and Wales; restrictions for several water-user categories are then passed '
              'to a static input–output model of the economy to estimate direct and indirect losses. Over an ensemble '
              'equivalent to 2,800 years of synthetic daily weather, the direct expected annual loss to water users '
              'is £11.7 million in the 2011 base year, and £30.2 million with indirect losses; the most severe '
              'simulated event costs £1.4 billion, 0.11% of GVA. The framework is offered for judging the '
              'economically efficient level of system reliability and for deciding on water management regulations '
              'and strategic investments (abstract).',
         sota='A risk-based chain from simulated droughts to economy-wide losses that expresses reliability as an '
              'expected annual loss, which can be weighed against the cost of investments and regulations.',
         gap='Losses come from shortages of quantity; a breach of a quality limit, and the cost of acting on the wrong '
             'cause, are not priced, so the efficient reliability for chloride compliance under source ambiguity '
             'remains open.',
         source='Knowing the source is worth the losses it avoids, and indirect losses can exceed direct ones, as they '
                "do in this study; the value of tracer tests is understated if only the utility's own costs are "
                'counted.',
         demand='Price unmet demand with its knock-on effects: a shortage for hotels in the tourist season costs more '
                'than the water not delivered, so the unmet-demand term of the social cost needs an indirect-loss '
                'multiplier for each user group.',
         stake='An expected annual loss gives the regulator a common unit for the accepted risk, so the question '
               'becomes whether a lower risk is worth its cost, rather than a risk fixed by convention.',
         step='Pricing the split of the risk budget: compute the expected social cost of the robust allocation on a '
              'grid of $(\\alpha,\\beta)$ with $\\alpha+\\beta=\\delta$, charging unmet demand at its direct loss '
              'plus the indirect loss from an input–output model of households, tourism and farming. Offer the '
              'regulator the split at which moving a little risk between $\\alpha$ and $\\beta$ no longer lowers the '
              'expected cost, and report how far that split moves when indirect losses are left out (C2, C5).',
         comps=['C2', 'C5']),

    dict(id='O8', inst='Oxford', year=2026, short='Licensed yields understate restriction days',
         title='Groundwater Representation in Water Resource Planning: The Spatial and Temporal Sensitivity of '
               'Groundwater Supplies in England',
         authors='Rachel Pugh, Anna Murgatroyd, Richard Rowan‐Robinson, Jim Hall',
         venue='Water and Environment Journal 40(4), 700–716 (2026)',
         links=[('doi:10.1111/wej.70064', 'https://doi.org/10.1111/wej.70064')],
         evidence='Crossref affiliation strings: Rachel Pugh and Jim Hall — Environmental Change Institute, School of '
                  'Geography and the Environment, University of Oxford.',
         does='**Result.** Large-scale water resource assessments often simplify the dynamics of groundwater '
              'availability. This study integrates an empirically based groundwater supply model with a '
              'national-scale water resource system simulation model for England and, with a large-ensemble climate '
              'dataset, compares dynamic and steady groundwater representation, showing the contribution of '
              'groundwater to system supply and performance and regional differences in response. The south-east is '
              'particularly sensitive to groundwater flow: in the far-future scenario the median number of days with '
              'restrictions rises '
              'by 40% with the dynamic groundwater model, compared with simulations based on licensed groundwater '
              'yields (abstract).',
         sota='National-scale evidence that a dynamic representation of groundwater supply, rather than licensed '
              'yields, changes the assessed reliability of public supply, with regional differences.',
         gap='Groundwater enters as a quantity that varies with climate; the quality of the pumped water, and yield '
             'lost because a well turns saline, are not part of the representation.',
         source='A steady, licensed yield hides the very response that separates the hypotheses: under SWI and UP the '
                'usable yield of A or C depends on how hard and how long they are pumped, under DRY on recharge, so '
                'the yield model itself must differ by source.',
         demand='Count restriction days, not annual yields: the gap between steady and dynamic representation shows '
                'up in how often supply must be cut, which is what households and tourism feel.',
         stake="Licences are the regulator's planning unit, but a licence is not a yield; reporting both for each "
               'wellfield shows stakeholders how much of the licensed water is at risk in a dry sequence.',
         step='Let the data choose the groundwater representation: split each source hypothesis into a steady variant '
              '(chloride and yield fixed by current pumping, as with licensed yields) and a dynamic variant (chloride '
              'and yield that respond to recharge and pumping history), and run C1 on the eight variants. C2 then '
              'protects every variant left in $S(y)$, so the bound $\\alpha+\\beta$ also covers the choice of model; '
              'the test is how many monthly samples (C4) it takes to exclude the steady variants and how much the '
              'robust allocation changes once they are excluded.',
         comps=['C1', 'C2', 'C4']),

    dict(id='O9', inst='Oxford', year=2020, short='Water productivity gains lower water stress',
         title='Water Stress and Productivity: An Empirical Analysis of Trends and Drivers',
         authors='Tess Doeffinger, Jim W. Hall',
         venue='Water Resources Research 56(3), e2019WR025925 (2020)',
         links=[('doi:10.1029/2019wr025925', 'https://doi.org/10.1029/2019wr025925')],
         evidence='Crossref affiliation strings: Tess Doeffinger and Jim W. Hall — Environmental Change Institute, '
                  'School of Geography and the Environment, University of Oxford.',
         does='**Result.** An econometric analysis at country level tests whether higher water productivity lowers '
              'water stress or, as evidence from other resource sectors suggests, leads to rebound effects. Within a '
              'country, a 1.0% increase in productivity is associated on average with a 0.81% decrease in water '
              'stress through time and accounts for 75% of the variance of stress; fixed-effects panel regressions '
              'relate population, cultivated land and political stability to stress within countries, while GDP and '
              'precipitation explain differences across countries. Stress is starting to fall in several developed '
              'countries and is low but rising in developing ones, so stress is likely to rise first as a country '
              'develops and could be mitigated if a "productivity transition" came sooner (abstract).',
         sota='Cross-country evidence that, on average, rising water productivity goes with falling water stress '
              'within countries rather than a rebound, with within-country and across-country drivers separated by '
              'panel methods.',
         gap='It works with national aggregates; one aquifer, water quality, and an irrigation-efficiency gain that '
             'changes both the volume pumped and the salt returned to the aquifer are beyond its scale.',
         source='The panel logic carries over to wells: compare each well with itself over time (fixed effects); '
                'differences between wells mix depth, distance to the coast and land use, while the within-well '
                'response to pumping and rainfall is closer to the mechanism that separates the hypotheses.',
         demand='Raising the water productivity of irrigation at B can free water for the utility, but whether it '
                'lowers pumping, rather than expanding the irrigated area, has to be checked locally; that is the '
                'rebound question at farm scale.',
         stake='For farmers, productivity gains are a way to give up water without giving up income; support for '
               'efficiency at B can be a more acceptable bargain than a cut in their abstraction.',
         step="Within-well elasticities as evidence for C1: from the utility's monthly records at every well of A, B "
              "and C, estimate with well fixed effects how chloride moves with the well's own pumping, with the "
              'recharge anomaly and with irrigation at B. Each source predicts a sign pattern (SWI: up with pumping '
              'at A; UP: up with pumping at C; DRY: up as recharge falls at A and B but not at C; ANT: up with '
              'irrigation at B), the fit of each pattern gives $p_k(y)$, and the test is whether these existing '
              'records alone remove a source from $S(y)$ before any new tracer is bought (C1, C3).',
         comps=['C1', 'C3']),

    dict(id='O10', inst='Oxford', year=2024, short='Upstream use raises downstream drought risk',
         title='The implications of further reservoir development on the Blue Nile in Ethiopia: trade-offs between '
               'hydropower, irrigation and transboundary water security',
         authors='Anna Murgatroyd, Kevin Wheeler, Jim W Hall, Dale Whittington',
         venue='Environmental Research Letters 19(9), 094055 (2024)',
         links=[('doi:10.1088/1748-9326/ad6887', 'https://doi.org/10.1088/1748-9326/ad6887')],
         evidence='Crossref affiliation strings: Kevin Wheeler and Jim W Hall — University of Oxford.',
         does='**Result.** An evaluation, for Ethiopia and Egypt, of two dams that could be built upstream of the Grand '
              'Ethiopian Renaissance Dam (GERD), combined with hypothetical Ethiopian irrigation schemes upstream of '
              'them. The two dams could raise average annual hydropower on the Blue and Main Nile, from Lake Tana to '
              'Aswan, by almost 50% (30.2 to 44.7 TWh per year), but a system-wide analysis of expected financial '
              'benefits finds little financial justification for substantial irrigation withdrawals upstream of the '
              'GERD: withdrawing 5 bcm per year would cut hydropower by 10.9% without the new dams and by 15.2% with '
              "them. Upstream withdrawals of 1 and 5 bcm per year would also reduce outflows from Sudan's Merowe and "
              "Egypt's High Aswan Dam reservoirs. The annual probability that High Aswan Dam storage falls below 60 "
              'bcm, invoking its drought management policy, is estimated at 0.085 now and would rise to 0.111 and '
              '0.452 under two scenarios of upstream withdrawals (abstract).',
         sota='A system-wide, probabilistic account of a transboundary trade-off that weighs upstream irrigation '
              'against hydropower and shows how upstream withdrawals change the probability of triggering a '
              'downstream drought policy.',
         gap="The trade-offs are between water quantities whose routing is known; in our aquifer, how farmers' "
             'pumping reaches the coast depends on the unknown source, so the size of the externality, and whether '
             'there is one at all, is uncertain.',
         source="The response to farmers' pumping is itself a signature: under SWI more pumping at B lowers the "
                'outflow that holds seawater back and raises chloride at A; under ANT the irrigation it feeds returns '
                'salt to B; under DRY or UP it should matter little.',
         demand="Upstream irrigation can cost more downstream than it earns; the farmers' use of B should be valued "
                "against what it does to the utility's supply, not only against the farmers' returns.",
         stake="A shared rule (here, a drought management policy at the High Aswan Dam) is triggered more often by "
               "others' upstream choices; in our case farmers' pumping changes how often the utility must cut supply "
               'or buy X, and the ledger should show it.',
         step="Source-dependent externality of farmers' pumping: for each source in $S(y)$, compute how much one more "
              'unit of irrigation pumping at B raises the probability that the blend exceeds 250 mg/L and the '
              'probability that the wetland springs at A fall below their target flow, as the Nile study does for the '
              'trigger of a downstream drought policy. Enter the smallest value over $S(y)$ in the ledger as the '
              'charge that can be defended now and the largest as the charge if the worst source is confirmed (C5); '
              "the gap between them is the farmers' stake in the tracer programme, which C3 can count when it values "
              'each test (C1, C3, C5).',
         comps=['C1', 'C3', 'C5']),

    dict(id='O11', inst='Oxford', year=2022, short='Keeping water in the system',
         title='Water Storage Decisions and Consumptive Use May Constrain Ecosystem Management under Severe Sustained '
               'Drought',
         authors='Lindsey A. Bruckerhoff, Kevin Wheeler, Kimberly L. Dibble, Bryce A. Mihalevich, Bethany T. Neilson, '
                 'Jian Wang, Charles B. Yackulic, John C. Schmidt',
         venue='JAWRA Journal of the American Water Resources Association 58(5), 654–672 (2022)',
         links=[('doi:10.1111/1752-1688.13020', 'https://doi.org/10.1111/1752-1688.13020')],
         evidence='Crossref affiliation strings: Kevin Wheeler — Environmental Change Institute and Oxford Martin '
                  'School, University of Oxford.',
         does='**Result.** Drought has affected the Colorado River basin for the past 20 years and is predicted to '
              'continue, so decisions on how much water to store in large reservoirs and how much to use '
              'consumptively will be needed. Using projected hydrology and river temperatures, the study compares '
              'current operations, or storage prioritised in Lake Mead or in Lake Powell, each with three levels of '
              'consumptive use, on ecosystem metrics for the Colorado River in Grand Canyon: the ability to implement '
              'designer flows, temperature suitability for fishes, and fragmentation. If consumptive use was not '
              'limited, projected reservoir levels limited environmental flow delivery and increased fragmentation '
              'wherever water was stored, and low reservoir levels are likely to bring warmer water that suits '
              'non-native species of concern such as smallmouth bass. Storage decisions gave variability and '
              'management flexibility but mattered less when less water was available, which highlights keeping '
              'water in the system (abstract).',
         sota='A scenario comparison that links water-supply decisions (where to store, how much to consume) to '
              'ecosystem outcomes, and finds that without limits on consumptive use the choice of where to store '
              'cannot protect environmental flows in a severe sustained drought.',
         gap='Water quality enters as river temperature, and the drought is the known driver; a decline whose cause '
             'is itself in doubt, with different causes calling for different operations, is outside its scope.',
         source='Quality follows storage (here, warmer water at low reservoir levels); in our aquifer falling heads '
                'raise chloride under SWI, UP and DRY alike, so a rise during a drought is weak evidence for any one '
                'source, and what separates them is a contrast, between depths or between wellfields, that the '
                'sources predict differently.',
         demand='Without a cap on total abstraction, moving pumping between A, B and C may not protect the wetland '
                'springs in a long drought; the cap, backed by X or by demand cuts, is the main lever and the split '
                'comes second.',
         stake="The environment agency's goal depends on how much water stays in the aquifer, which depends on "
               "everyone's use, farmers' wells included; its claim is on total abstraction, not only on the pumping "
               'at A.',
         step="Cap first, then split: make the total abstraction from A, B, C and the farmers' wells an explicit "
              'decision in C2, and test for each source in $S(y)$ whether the wetland-spring target at A and the '
              'chloride constraint can be met by moving pumping between wellfields alone. Where they cannot, the '
              'lowest feasible cap and its cost to households, tourism and farmers go into the ledger (C5). The water '
              'kept in the aquifer is also an option: compare the cost of the best allocation available at the '
              'meeting at which the monitoring of C4 first excludes a source, with and without the cap.',
         comps=['C2', 'C4', 'C5']),
]


_PART2 = [
    dict(id='O12', inst='Oxford', year=2023, short='Engagement does not guarantee tool uptake',
         title='Stakeholder engagement does not guarantee impact: A co-productionist perspective on model-based '
               'drought research',
         authors='Catharina Landström, Eric Sarmiento, Sarah J Whatmore',
         venue='Social Studies of Science 54(2), 210–230 (2023)',
         links=[('doi:10.1177/03063127231199220', 'https://doi.org/10.1177/03063127231199220')],
         evidence='Crossref affiliation strings: Catharina Landström and Sarah J Whatmore — University of Oxford '
                  '(the strings name no unit).',
         does='**Result.** A study of model-based drought research in the UK through a modified concept of '
              'co-production. It casts doubt on the increasingly accepted view that more and better stakeholder '
              'involvement leads to the adoption of modelling tools: the freedom of stakeholder organisations to adopt '
              'new tools in their regular practices is circumscribed by the societal context, and relationships '
              'between actors in the drought governance space shape uptake. The analysis suggests why engagement with '
              'one project led stakeholders to adopt one output (data) while another (modelling tools) attracted no '
              'discernible interest (abstract).',
         sota='A co-productionist account of the limits of stakeholder engagement: the uptake of model-based research '
              'depends on what the governance context leaves stakeholder organisations free to adopt and on the '
              'relationships between actors, not on the amount of involvement alone.',
         gap='It explains why a tool was not taken up, not how to design one that will be: it does not say which '
             'outputs of a source diagnosis (data, a verdict, an allocation rule) a utility or a regulator could fit '
             'into its regular practices.',
         source='Data travel where models do not: tracer results (Br/Cl, isotopes, salinity depth profiles) and a '
                'plausible-source set computed from them by a published rule are more likely to be used than a model '
                'that only its authors can run.',
         demand='An allocation that does not fit the instruments the parties already use (permits, pumping schedules, '
                'drought plans) will not be applied in the next dry season; the demand plan has to be written in '
                'those instruments.',
         stake='Engagement is not uptake: before the outputs are designed, map which party has the mandate and the '
               'freedom to act on each of them (regulator, utility, environment agency, farmers).',
         step='Mandate-mapped release with an uptake test: release PREJARDHJA-GO as two separable products, a monthly '
              'data sheet with the tracer results, the e-values and $S(y)$ (C1, C4), and the allocation model (C2) '
              'attached to an act the regulator already owns, setting the risk budget $\\delta$ in the ledger (C5). '
              'Then record for one year which product each party cites in a formal decision (permit, pumping '
              'schedule, drought plan); the co-production reading predicts that the data sheet is cited first and the '
              'model only where it is attached to such an act.',
         comps=['C1', 'C4', 'C5']),

    dict(id='C1', inst='Caltech', year=2021, short='Drought cascade timed from satellites',
         title='Drought Cascade in the Terrestrial Water Cycle: Evidence From Remote Sensing',
         authors='Alireza Farahmand, J. T. Reager, Nima Madani',
         venue='Geophysical Research Letters 48(14), e2021GL093482 (2021)',
         links=[('doi:10.1029/2021gl093482', 'https://doi.org/10.1029/2021gl093482')],
         evidence='Crossref affiliation strings: Alireza Farahmand, J. T. Reager and Nima Madani — Jet Propulsion '
                  'Laboratory, California Institute of Technology.',
         does='**Result.** Droughts start in interactions between the atmosphere and the land surface and cascade, with '
              'delay, through soil moisture, surface water and groundwater. The paper uses satellite observations of '
              'vapour pressure deficit, precipitation and terrestrial water storage, with reanalysis-based column soil '
              'moisture, to characterise the cascade in four major US drought case studies. Mapping the time evolution '
              'through these variables shows large-scale behaviour generally consistent with theory and quantifies '
              'emergent patterns in the evolution of drought signals that may support improved predictability '
              '(abstract).',
         sota='The timing of drought cascades estimated quantitatively at large scale from primarily remote-sensing '
              'data, where earlier studies had observed the cascade only at selected in situ locations.',
         gap='It follows water quantity, not quality: it does not say how a drought cascade changes chloride in an '
             'aquifer, or how that change differs in timing from the response to pumping.',
         source='Timing is a signature: under DRY, chloride in the shallow wells A and B should follow the storage '
                'deficit with the delay of the cascade while C does not respond, whereas under SWI and UP it should '
                'follow pumping; a rise that comes before the storage deficit, or starts at C, argues against DRY.',
         demand='Drought reaches groundwater late and leaves it late: if the source is drought, relief also comes with '
                'the delay of the cascade, so the demand plan should keep its chloride margin for months after the '
                'rain returns.',
         stake='The end of a meteorological drought is not the end of the chloride problem; agree in advance that '
               'pumping limits are relaxed on groundwater indicators, not on rainfall.',
         step='Cascade lead time in the drought constraint: forecast the shallow storage deficit from the observed '
              'cascade (vapour pressure deficit and precipitation first, soil moisture and storage later) and use it '
              'to set $P_k$ for $k$ = DRY in C2 over the coming months, so that while DRY is in $S(y)$ the allocation, '
              'including how much of X to book, moves load away from A and B before drought chloride arrives, not '
              'after. Back-test on past dry spells, or in simulation: the exceedance rate and the social cost of '
              'allocations set with the cascade forecast against allocations set from current chloride only.',
         comps=['C2']),

    dict(id='C2', inst='Caltech', year=2023, short='Coastal salinity as a water-cycle bellwether',
         title='The Salinity of Coastal Waters as a Bellwether for Global Water Cycle Changes',
         authors='S. Fournier, J. T. Reager, H. A. Chandanpurkar, M. Pascolini‐Campbell, S. Jarugula',
         venue='Geophysical Research Letters 50(24), e2023GL106684 (2023)',
         links=[('doi:10.1029/2023gl106684', 'https://doi.org/10.1029/2023gl106684')],
         evidence='Crossref affiliation strings: S. Fournier, J. T. Reager, M. Pascolini‐Campbell and '
                  'S. Jarugula — Jet Propulsion Laboratory, California Institute of Technology.',
         does='**Result.** Using coastal satellite sea surface salinity (SSS), the paper shows that, in global '
              'aggregate, SSS variations near coasts are strongly correlated with global water-cycle variability '
              'driven by El Niño Southern Oscillation (ENSO), while open-ocean SSS is less sensitive to ENSO and to '
              'global water-cycle variability at interannual timescales. Aggregated coastal SSS could therefore serve '
              'as a proxy for detecting changes in the large-scale cycling of water between oceans and continents. '
              'The paper also identifies potential hotspots on land and in the coastal ocean that tend to drive global '
              'coastal salinity variability and may be most sensitive to future physical and biological impacts of '
              'water-cycle changes on the coastal oceans (abstract).',
         sota='Coastal sea surface salinity from satellites as an aggregate indicator of land–ocean water-cycle '
              'variability at interannual timescales, more sensitive than open-ocean salinity, with the hotspots that '
              'drive it identified.',
         gap='It works in global aggregate and on the sea side of the shore: it does not resolve the salinity of the '
             'water at a given aquifer boundary, nor link sea surface salinity to chloride in wells.',
         source='The sea end-member is not fixed: near-shore salinity varies with the water cycle, and in a dry year '
                'coastal water can turn saltier while recharge is concentrated, so SWI and DRY can rise together; '
                'timing alone will not separate them, and tracers that respond differently (water isotopes, salinity '
                'depth profiles) are needed.',
         demand='When coastal water is saltier, the same pumping at A carries more chloride if the source is SWI; plan '
                'the share of A with the coastal salinity observed in the season, not a long-term mean.',
         stake='A public indicator that the coast is in a salty phase lets the utility announce precautionary limits '
               'at A early, when they are easier to accept than after an exceedance.',
         step='Bellwether-triggered sampling: when the coastal salinity anomaly (satellite sea surface salinity or a '
              'near-shore probe) enters its upper quartile, sample the tracers at A fortnightly instead of monthly, '
              'and less often in fresh periods so that the annual cost is unchanged; the trigger level is chosen in C3 '
              'by its decision value. The e-process of C4 stays valid under any sampling schedule set from past data '
              'and external indicators, so the extra samples add power when an SWI signal should be strongest without '
              'inflating the error. Test in simulation: the months needed to drop a false source from $S(y)$, and the '
              'rate of dropping the true one (at most $\\beta$), against fixed monthly sampling.',
         comps=['C3', 'C4']),

    dict(id='C3', inst='Caltech', year=2021, short='Satellite turbidity maps for drought interventions',
         title='Assessing Fish Habitat and the Effects of an Emergency Drought Barrier on Estuarine Turbidity Using '
               'Satellite Remote Sensing',
         authors='Christiana Ade, Erin L. Hestir, Christine M. Lee',
         venue='JAWRA Journal of the American Water Resources Association 57(5), 752–770 (2021)',
         links=[('doi:10.1111/1752-1688.12925', 'https://doi.org/10.1111/1752-1688.12925')],
         evidence='Crossref affiliation string: Christine M. Lee — Terrestrial Hydrology, Earth Science Section, NASA '
                  'Jet Propulsion Laboratory, California Institute of Technology.',
         does='**Result.** The paper evaluates high-frequency, high-resolution satellite remote sensing in two '
              'management-relevant cases in the San Francisco Estuary and the Sacramento–San Joaquin River Delta. A '
              'time series of turbidity maps identified favourable turbidity conditions for the endangered delta smelt '
              'in the dry season of 2015, at the height of the great California drought, with several persistent '
              'turbidity refugia in the north and west Delta but infrequent connectivity. Ebb-tide images before and '
              'after an emergency saltwater intrusion barrier was installed showed a mean increase of 6.6 NTU in the '
              "San Joaquin River and 4 NTU in Fisherman's Cut, which supports earlier field-sample findings that the "
              'barrier may have increased turbidity near it and adds spatial context (abstract).',
         sota='Satellite turbidity maps as decision support for drought interventions in an estuary: they locate '
              'habitat refugia and measure the side effect of an emergency barrier against saltwater intrusion, '
              'adding spatial context to field samples.',
         gap='The barrier was judged after it was built, for one side effect, in an estuary where the salt is '
             'seawater; nothing here weighs such a measure against alternatives before the decision, or under rival '
             'explanations of the salinity.',
         source='An emergency measure is also a perturbation: chloride at A, B and C responds differently to a change '
                'in pumping under SWI, UP, DRY and ANT, so the before–after record of every emergency change is '
                'evidence on the source, if samples are matched in tidal phase as the images were.',
         demand='Measures against salt have side effects on other demands; cost each emergency option (cutting A, '
                'pumping more at B or C, starting X) with its effects on the wetland and the farmers, not only with '
                'its chloride benefit.',
         stake='Maps of where side effects fall give the environment agency evidence it can check; agree how side '
               'effects will be monitored before an emergency measure is taken, not after.',
         step='Sunset clause for source-specific emergency measures: in C2, tag each emergency measure with the '
              'sources it helps (a hydraulic barrier or a cut at A under SWI, a cut at C under UP, curbs on return '
              'flow at B under ANT). While $S(y)$ holds more than one source, such a measure may be used only with a '
              "sunset date, a before–after check of its side effects at matched tidal phase (wetland spring flow, "
              "farmers' supply) booked in the ledger (C5), and automatic removal once every source it helps has left "
              '$S(y)$; test in simulation over the four sources the expected social cost and exceedance of this rule '
              'against keeping each emergency measure once it is in place.',
         comps=['C2', 'C5']),

    dict(id='C4', inst='Caltech', year=2024, short='Lithology-informed GP groundwater maps',
         title="Modeling Groundwater Levels in California's Central Valley by Hierarchical Gaussian Process and "
               'Neural Network Regression',
         authors='Anshuman Pradhan, Kyra H. Adams, Venkat Chandrasekaran, Zhen Liu, John T. Reager, Andrew M. Stuart, '
                 'Michael J. Turmon',
         venue='Journal of Geophysical Research: Machine Learning and Computation 1(4), e2024JH000322 (2024)',
         links=[('doi:10.1029/2024jh000322', 'https://doi.org/10.1029/2024jh000322')],
         evidence='Crossref affiliation strings: Anshuman Pradhan, Venkat Chandrasekaran and Andrew M. Stuart — '
                  'Computing and Mathematical Sciences, California Institute of Technology (campus); Kyra H. Adams, '
                  'Zhen Liu, John T. Reager and Michael J. Turmon — Jet Propulsion Laboratory, California Institute '
                  'of Technology.',
         does="**Result.** Groundwater levels across California's Central Valley are hard to model continuously "
              'because well data are sparse and noisy in time and space. The paper combines deep neural networks and '
              'Gaussian processes hierarchically: the network learns a latent space informed by a 3D lithological '
              'texture model of the aquifer, and non-parametric Gaussian-process regression is performed in that '
              'space. The method models non-stationary features with fast uncertainty quantification that is '
              'statistically consistent with the data of 90 blind wells, and indicates that on average the 2017 and '
              '2019 wet years were largely ineffective in replenishing the groundwater lost in the previous drought '
              'years (abstract).',
         sota='Hierarchical Gaussian-process and neural-network regression that uses a lithological texture model to '
              'map groundwater levels between irregular wells, with fast uncertainty quantification checked against '
              'blind wells.',
         gap='It maps heads, not chloride, and gives one predictive distribution rather than one per rival source: '
             'its calibrated uncertainty is within a model, while the decision also needs the spread between source '
             'hypotheses.',
         source='Geology can carry the source signature: in a lithology-informed latent space each hypothesis predicts '
                'its own spatial pattern (SWI in permeable layers open to the sea, UP under pumping wells where '
                'aquitards are thin, ANT under irrigated fields), so sparse wells can borrow strength from one another.',
         demand='Wet years may not refill a drought deficit; the allocation should not assume that heads, and with '
                'them the margin against intrusion or upconing, recover after one wet season.',
         stake='A model checked on wells it never saw is one a regulator can accept for wells that were not sampled; '
               'publish the blind-well check with every forecast.',
         step='Blind-well calibration gate for $P_k$: model chloride under each source $k$ with a Gaussian process in '
              'a lithology-informed latent space, and let $P_k$ enter the chance constraint of C2 only if, in '
              'leave-one-well-out prediction, the number of wells above their $1-\\alpha$ bound is not significantly '
              'more than $\\alpha$ times the number of wells (one-sided binomial test). A model that fails, because it '
              'is wrong or because $k$ is false, is widened until it passes, which can only make the constraint '
              'stricter, so the $\\alpha$ share of the risk budget in the ledger (C5) means what it says.',
         comps=['C2', 'C5']),

    dict(id='C5', inst='Caltech', year=2021, short='InSAR subsidence screening for water agencies',
         title='Value of InSAR for Monitoring Land Subsidence to Support Water Management in the San Joaquin Valley, '
               'California',
         authors='Jeanine Jones, Cathleen E. Jones, David P.S. Bekaert',
         venue='JAWRA Journal of the American Water Resources Association 58(6), 995–1001 (2021)',
         links=[('doi:10.1111/1752-1688.12942', 'https://doi.org/10.1111/1752-1688.12942')],
         evidence='Crossref affiliation strings: Cathleen E. Jones and David P.S. Bekaert — Jet Propulsion '
                  'Laboratory, California Institute of Technology.',
         does="**Result.** During the 2012–2016 drought, the California Department of Water Resources sought NASA's "
              'assistance to monitor land subsidence from groundwater extraction in the San Joaquin Valley, where in '
              'situ monitoring had been limited, with satellite- and aircraft-based InSAR. InSAR cost-effectively gave '
              'the first synoptic measurement of subsidence over the whole valley, for screening and hotspot '
              'detection: drought subsidence rates ranked with the maximum historically observed, long-term subsidence '
              'had substantially reduced the conveyance capacity of sections of major canals, and new, rapidly '
              'emerging hotspots appeared next to critical water infrastructure. This success led the department to '
              'provide InSAR data as technical assistance to local agencies required to comply with recent state '
              'groundwater management legislation (abstract).',
         sota='InSAR as a cost-effective screen for groundwater-driven subsidence over a whole valley, proven in a '
              'drought response and then provided by a state agency to the local agencies that must comply with '
              'groundwater law.',
         gap='It screens for a physical impact of pumping where it occurs; it does not attribute a change in water '
             'quality to a cause, and deformation does not measure chloride.',
         source='Deformation shows where heads have fallen in compressible layers, which SWI (a landward gradient at '
                'the coast) and UP (deep drawdown under C) need and DRY and ANT do not; a cheap synoptic screen can '
                'say where each source is physically possible, not which one is present.',
         demand='Pumping that compacts the aquifer also damages the infrastructure that serves the demand; a share at '
                'A, B or C that is safe for chloride may still cost conveyance or well capacity in the long run.',
         stake='The monitoring proved its value in a drought and was then institutionalised by handing the data to the '
               'agencies that must comply with the law; source monitoring needs a named owner who keeps it running '
               'after the emergency that justified it.',
         step='Two-stage screen-then-sample design in C3: stage 1 uses synoptic, low-cost data (InSAR deformation as a '
              'proxy of head decline, with pumping records) to flag where the preconditions of SWI and UP hold; stage '
              '2 places the paid tracer samples (Br/Cl, isotopes, salinity depth profiles) by the decision-value rule '
              'in flagged hotspots and in unflagged controls. The screen decides only where to sample, never which '
              'source to keep, so the guarantee of C1 is untouched; a simulation over the four sources compares, at a '
              'fixed budget, the expected cost of the robust allocation (C2) after this design with that after the '
              'same number of samples spread evenly.',
         comps=['C3']),

    dict(id='C6', inst='Caltech', year=2021, short='Open GRACE groundwater tool for managers',
         title='An Open‐Source Web Application for Regional Analysis of GRACE Groundwater Data and Engaging '
               'Stakeholders in Groundwater Management',
         authors='Travis Clinton McStraw, Sarva T. Pulla, Norman L. Jones, Gustavious P. Williams, Cédric H. David, '
                 'James E. Nelson, Daniel P. Ames',
         venue='JAWRA Journal of the American Water Resources Association 58(6), 1002–1016 (2021)',
         links=[('doi:10.1111/1752-1688.12968', 'https://doi.org/10.1111/1752-1688.12968')],
         evidence='Crossref affiliation string: Cédric H. David — Jet Propulsion Laboratory, California Institute of '
                  'Technology.',
         does='**Result.** GRACE data on changes in total water storage are public, but viewing, manipulating and '
              'analysing them is difficult without skills in programming or geospatial software, particularly for '
              'water managers in developing countries. The authors built an open-source utility that subsets GRACE '
              'data to a selected region and packaged it in a web application for quick access and visualisation. '
              'For the region, data from the three Global Land Data Assimilation System land surface models (Noah, '
              'Variable Infiltration Capacity and the Catchment Land Surface Model) decompose total water storage '
              'into surface water, soil moisture and groundwater with associated uncertainty estimates, giving '
              'groundwater storage change over time; a case study from the Hindu-Kush Himalayan region demonstrates '
              'the uses for responding to drought and agricultural demand (abstract).',
         sota='Open, browser-based access to regional groundwater storage change from GRACE, decomposed with three land '
              'surface models and an uncertainty estimate, for managers without specialist software skills.',
         gap='Regional storage change at GRACE resolution says nothing at the scale of a wellfield or about salinity; '
             'its uncertainty spans land surface models, not the causes of chloride.',
         source='Showing several models side by side is an honest way to present uncertainty; a regional storage '
                'decline makes DRY plausible but does not separate it from SWI or UP, which also grow as storage falls.',
         demand='Storage trends tell the utility whether the aquifer can sustain the B and C shares over years, not '
                "only whether this month's blend is safe; drought and agricultural demand draw on the same storage.",
         stake='Engagement grows when stakeholders can open the evidence themselves; an open tool lets farmers and the '
               "environment agency check the case for a cut without relying on the utility's experts.",
         step='Open prior-entry tool for test selection: in an open-source browser application, each party enters '
              'its own planning prior over SWI, UP, DRY and ANT in the ledger (C5), with the regional '
              'groundwater-storage trend and its three-model spread shown as context, and C3 values every candidate '
              "tracer plan under every party's prior; the plan bought is the one whose lowest value across parties "
              'is highest. The planning prior enters only C3, so letting the parties bring their beliefs cannot '
              'weaken the guarantee of C2; test at a workshop whether all parties accept this max–min plan, and in '
              'simulation how much expected cost reduction it gives up against the plan that is best under a flat '
              'prior.',
         comps=['C3', 'C5']),

    dict(id='H1', inst='Harvard', year=2023, short='Irrigation-sensitive drought record from weather data',
         title='An Observational, Irrigation-Sensitive Agricultural Drought Record from Weather Data',
         authors='Lois I. Tang, Kaighin A. McColl',
         venue='Journal of Hydrometeorology 24(11), 2091–2103 (2023)',
         links=[('doi:10.1175/jhm-d-23-0026.1', 'https://doi.org/10.1175/jhm-d-23-0026.1')],
         evidence='Crossref affiliation strings: Lois I. Tang and Kaighin A. McColl — Department of Earth and '
                  'Planetary Sciences, Harvard University; Kaighin A. McColl also — School of Engineering and Applied '
                  'Sciences, Harvard University.',
         does='**Result.** Meteorological drought indices ignore irrigation and reanalyses largely neglect it, while '
              'estimates of the evaporative fraction (EF) that need satellite land surface temperature cannot reach '
              'back before the satellite era. The paper uses surface flux equilibrium (SFE) theory to estimate EF from '
              'near-surface air temperature and specific humidity, which have long historical records. Unlike EF from '
              'a reanalysis, the SFE-predicted EF is greater at irrigated than at non-irrigated sites during droughts, '
              'and its historical trends are typically consistent with the spatial distribution of irrigation growth; '
              'two sites where it rose without changes in irrigation are explained by increased flooding from river '
              'engineering and the expansion of fish hatcheries. The estimate is sensitive and specific to irrigation '
              'and extends the agricultural drought record back before the satellite era (abstract).',
         sota='A way to quantify agricultural drought before the satellite era from weather-station data, with an '
              'evaporative fraction that registers irrigation where a reanalysis does not.',
         gap='It records whether land is irrigated during drought, not what irrigation does to groundwater quality; '
             'the path from irrigation to return-flow chloride at B is outside its scope.',
         source='The contrast between an irrigation-blind index and an irrigation-sensitive one is a signal in itself: '
                'chloride at B that follows the irrigation signal points to ANT, while chloride that follows the '
                'meteorological drought at both A and B points to DRY. The two anomalous sites are a warning that '
                'other human interventions, such as flooding from river engineering, can mimic irrigation.',
         demand='Irrigation shields farmers from drought by drawing on the aquifer the utility shares at B; in a dry '
                "year the farmers' demand rises just when the utility would move pumping to B.",
         stake='A long, cheap record from weather stations lets farmers and the utility look at decades of irrigation '
               'and drought together, rather than argue from the last few years.',
         step='Weather-derived irrigation history for B, where farm wells are not metered: take the SFE evaporative '
              'fraction from air temperature and humidity at a station near B, minus a reanalysis value that neglects '
              'irrigation, as a decades-long proxy of irrigation intensity, checked against the few seasons with '
              'metered or surveyed irrigation. It drives ANT in C1 (chloride at B follows irrigation with a '
              'travel-time lag) against DRY (chloride at A and B follows the meteorological drought), fitted on the '
              'earlier record and evaluated on the later so that the ratio stays an e-value; test how many months it '
              'saves in separating ANT from DRY against the meteorological index alone, and let C3 reprice nitrate '
              'and boron analyses at B.',
         comps=['C1', 'C3']),

    dict(id='H2', inst='Harvard', year=2024, short='Uneven household water scarcity in Darjeeling',
         title='Ways of storing and using water: Experiences of uneven water scarcity in a water-rich region',
         authors='Rinan Shah',
         venue='Journal of Political Ecology 31(1) (2024)',
         links=[('doi:10.2458/jpe.5436', 'https://doi.org/10.2458/jpe.5436')],
         evidence='Crossref affiliation string: Rinan Shah — Harvard University, South Asia Institute.',
         does='**Result.** Communities in Darjeeling town have experienced and coped with water scarcity for decades; '
              'fragmented governance and inefficient infrastructural interventions have led to uneven access to '
              'water, defined by physical and political aspects at the household level. Drawing on urban political '
              'ecology, the essay examines the physical, political and infrastructural aspects of households in the '
              'production of unequal water scarcity, finds the inequalities reflected in coping behaviour and in the '
              'ways of storing and using water, and argues for adding altitude as a driving factor of water '
              'accessibility in urban studies in the mountains. It rests on fieldwork from 2014 to 2019: topic-guided '
              'and unstructured interviews, transect walks, document analysis and household questionnaires '
              '(abstract).',
         sota='An urban political ecology of household water scarcity in a water-rich region, which traces unequal '
              'access to physical, political and infrastructural factors, including altitude, and reads it in how '
              'households store and use water.',
         gap='It explains who goes short and why, not how a utility should share a shortfall it cannot avoid; water '
             'quality and the source of a quality problem are not part of it.',
         source='Household coping (storage, private wells, other sources) changes what is pumped where; private wells '
                'drilled in a shortage can add to intrusion or upconing, so a map of how households cope is also data '
                'on new, unmetered stresses on the aquifer.',
         demand='Demand met on average can hide households that go without: a shortfall from a chloride-driven cut '
                'falls first on households high up, at the end of the network or without storage.',
         stake='Households are not one stakeholder: report unmet demand by zone and by storage capacity, because a '
               'cost of not knowing the source that is small on average can be concentrated on a few.',
         step='Zone-level shortfall caps in the robust allocation: split unmet demand in C2 by supply zone and '
              'household type (high or end-of-network zones, households without storage) and require, for every $k$ '
              "in $S(y)$, that no zone's expected shortfall exceed an agreed cap; the ledger (C5) then reports the "
              'cost of not knowing the source by zone as well as by party. Test: compare the zone shortfalls of the '
              'capped and uncapped allocations under each source; the difference in social cost is the price of '
              'equity, which the stakeholders accept or reject in the open.',
         comps=['C2', 'C5']),

    dict(id='H3', inst='Harvard', year=2024, short='Robust causal effects with missing confounders',
         title='Robust causal inference for point exposures with missing confounders',
         authors='Alexander W. Levis, Rajarshi Mukherjee, Rui Wang, Sebastien Haneuse',
         venue='Canadian Journal of Statistics 53(2), e11832 (2024)',
         links=[('doi:10.1002/cjs.11832', 'https://doi.org/10.1002/cjs.11832')],
         evidence='Crossref affiliation strings: Rajarshi Mukherjee, Rui Wang and Sebastien Haneuse — Department of '
                  'Biostatistics, Harvard University; Rui Wang also — Department of Population Medicine, Harvard '
                  'Pilgrim Health Care Institute and Harvard Medical School.',
         does='**Result.** Large observational databases are often subject to missing data, so causal inference must '
              'handle confounding and missingness together. The paper proposes an efficient and robust estimator of '
              'the causal average treatment effect from cohort studies when confounders are missing at random, built '
              'on a new factorisation of the likelihood that allows flexible, machine-learning models of the nuisance '
              'functions while keeping nominal convergence rates for the final estimators. Simulated data derived '
              'from an electronic health record study of the long-term effects of bariatric surgery on weight verify '
              'the robustness in finite samples; the approach may serve as a theoretical benchmark for ad hoc methods '
              '(abstract).',
         sota='An efficient and robust estimator of an average treatment effect when confounders are missing at '
              'random, keeping nominal convergence rates while the nuisance functions are fitted with flexible '
              'machine-learning methods.',
         gap='It estimates one average effect of a point exposure; it does not choose between rival mechanisms, nor '
             'say how gaps in the data affect a test that must keep a guaranteed error rate.',
         source='Records go missing for reasons: wells are shut when they turn salty and costly analyses are bought '
                'for some samples only, so the complete cases are fresher than the aquifer; a diagnosis that drops '
                'the gaps without asking why can keep or exclude the wrong source.',
         demand='The allocation needs chloride responses to pumping adjusted for drought and irrigation; where those '
                'records are missing in some months, the response must be estimated in a way that stays valid under '
                'the gaps, or a cut at A may look more useful than it is.',
         stake='A published rule for which samples get which analyses, and a log of why any sample is missing, let '
               'farmers and the utility check that no one chose the data that favour their case.',
         step='Gaps that keep the guarantee: let C3 assign the costly analyses (isotopes, nitrate and boron) to each '
              "month's samples by a published rule with known probabilities that depend only on data already "
              'recorded, so the untested samples are missing at random by design and the observed-data likelihood '
              'ratios stay valid e-values (C1, C4). A sample lost because a well was shut for salty water is not '
              'dropped but entered as a censored observation, chloride above the shut-off level, with that '
              'probability under each source in the likelihood; test in simulation the coverage of $S(y)$ at '
              '$1-\\beta$ with complete-case analysis and with this treatment, under both kinds of gap.',
         comps=['C1', 'C3', 'C4']),
]


_PART3 = [
    dict(id='H4', inst='Harvard', year=2025, short='Causal graphs inside decision models',
         title='Directed Acyclic Graphs in Decision-Analytic Modeling: Bridging Causal Inference and Effective Model '
               'Design in Medical Decision Making',
         authors='Stijntje W. Dijk, Maurice Korf, Jeremy A. Labrecque, Ankur Pandya, Bart S. Ferket, '
                 'Lára R. Hallsson, John B. Wong, Uwe Siebert, M. G. Myriam Hunink',
         venue='Medical Decision Making 45(3), 223–231 (2025)',
         links=[('doi:10.1177/0272989x241310898', 'https://doi.org/10.1177/0272989x241310898')],
         evidence='Crossref affiliation strings: Ankur Pandya and M. G. Myriam Hunink — Center for Health Decision '
                  'Science, Harvard T.H. Chan School of Public Health; Uwe Siebert — Center for Health Decision '
                  'Science, Harvard T.H. Chan School of Public Health; Department of Epidemiology, Harvard T.H. Chan '
                  'School of Public Health; Institute for Technology Assessment and Department of Radiology, '
                  'Massachusetts General Hospital, Harvard Medical School.',
         does='**Result.** A methodological commentary arguing that directed acyclic graphs (DAGs), graphs of the '
              'assumed causal relations between variables, should be built into decision-analytic models in medical '
              'decision making and health economics. DAGs make a model more transparent and guide parameter '
              'selection and estimation by showing backdoor paths (potential biases in estimates) and clarifying '
              'frontdoor paths (the effect of the model structure on the outcome). Two applications, statins to '
              "prevent cardiovascular disease and mindfulness-based interventions for students' stress, show how "
              'DAGs can change model structure, parameter selection and conclusions on effectiveness and '
              'cost-effectiveness; '
              'simplicity, scope, unmeasured confounding, noncausal aspects and poor data remain challenges '
              '(abstract).',
         sota="A structured way to state a decision model's causal assumptions as a graph before building it, and to "
              'read from the graph which parameter estimates are biased (backdoor paths) and how the model structure '
              'carries effects to the outcome (frontdoor paths).',
         gap='It assumes one graph that the modeller can draw. Here the graph itself is unknown: the chloride source '
             'is a missing cause whose value decides which arrows into chloride exist, so a single DAG would hide '
             'the uncertainty that drives the decision.',
         source='Treat the source as a missing parent of chloride: the four hypotheses are four graphs over the same '
                'variables, and the samples worth taking are those of the variables on which the graphs disagree, '
                'not more chloride data.',
         demand='Demand sits on a backdoor path: dry summers raise both demand, hence pumping, and chloride, so a '
                'safe yield for A estimated from past pumping and chloride records is biased, and wrong in exactly '
                'the months when demand peaks.',
         stake="A drawn graph shows each stakeholder which arrow their position rests on (the farmers' on the "
               "absence of an arrow from irrigation at B, the environment agency's on the arrow from pumping at A "
               'to spring flow), so disputes turn on arrows that data can test.',
         step='Draw each hypothesis as a DAG over the same nodes (rainfall deficit R, demand D, pumping, irrigation, '
              'sea level, chloride and tracers), the unknown source being the missing parent that decides which '
              'arrows into chloride exist. A dry season opens the backdoor path '
              '$Q_A\\leftarrow D\\leftarrow R\\rightarrow \\text{Cl}_A$, so the chloride-response coefficients of '
              'C2 must be estimated with R and D adjusted for, and the likelihoods $p_k(y)$ of C1 must use the arrows '
              'that only one graph draws (isotope enrichment for DRY, nitrate and boron for ANT, depth profiles for '
              'UP). Test: under simulated DRY with demand peaking in dry months, the unadjusted slope of chloride on '
              '$Q_A$ should mimic seawater intrusion and the adjusted slope should be near zero.',
         comps=['C1', 'C2']),

    dict(id='H5', inst='Harvard', year=2020, short='Resilience districts as decision units',
         title='Theorizing the resilience district: Design-based decision making for coastal climate change '
               'adaptation',
         authors='Alan M. Berger, Michael Wilson, Jonah Susskind, Richard J. Zeckhauser',
         venue='Journal of Landscape Architecture 15(1), 6–17 (2020)',
         links=[('doi:10.1080/18626033.2020.1792648', 'https://doi.org/10.1080/18626033.2020.1792648')],
         evidence='Crossref affiliation strings: Alan M. Berger, Michael Wilson and Jonah Susskind — Department of '
                  'Urban Studies and Planning, Massachusetts Institute of Technology; Richard J. Zeckhauser — '
                  'Harvard Kennedy School, Harvard University. The paper is joint MIT–Harvard and is listed here '
                  'under Harvard.',
         does='**Result (from the catalogue abstract only).** Coastal cities face mounting pressure to plan for '
              'increased exposure to chronic flooding; metropolitan resilience districts are presented as the '
              'appropriate decision-making unit (DMU) to analyse, plan and implement resilience strategies, and the '
              'paper details a resilience districting strategy for the Greater Boston Metropolitan Area (catalogue '
              'abstract). A search summary of the same catalogue record adds that the investments needed are '
              'costly, uncertain and long-term, and that the paper treats landscape as a public safety service.',
         sota='It makes the choice of decision-making unit part of the adaptation problem, presenting the '
              'metropolitan resilience district, worked out for Greater Boston, as the unit that analyses, plans and '
              'implements coastal resilience strategies.',
         gap='As far as the excerpt shows, the district is drawn around a hazard of known cause. For chloride of '
             'unknown source the footprint is itself uncertain (the coast for SWI, the deep aquifer for UP, the '
             'recharge area for DRY, the farmland at B for ANT), so the unit cannot be fixed before the source is '
             'narrowed.',
         source='Each hypothesis has its own footprint, so the monitoring network has to cover all four (coastal '
                'strip, deep aquifer, recharge area, irrigated land), not only the coastal strip that a flood-style '
                'district would draw.',
         demand='Costly, long-lived supply options such as X or a new deep wellfield are investments for everyone '
                "who uses the aquifer; plan and finance them at that scale, so that meeting demand does not fall on "
                "one operator's tariff.",
         stake='If landscape is a public safety service, the wetland springs at A serve others and are not only a '
               'limit on pumping: the environment agency then has a claim in the cost split, and the loss of the '
               'wetland is counted in the ledger.',
         step='Make the decision unit depend on the plausible-source set: list the parties each hypothesis '
              'implicates, as drivers or as users whose supply it degrades (SWI: the utility at A, the wetland, '
              'tourism; UP: the utility at C; DRY: all users of the shallow aquifer at A and B; ANT: farmers, the '
              'wastewater operator and the utility at B), and convene their union over $S(y)$ (C1). A party leaves '
              'the table and the cost split (C5) only when every source implicating it is excluded, so the unit '
              'holds the parties of the true source with probability at least $1-\\beta$. Test: under each '
              'simulated true source, check this coverage at every planning round and count the parties shed as '
              'sources are excluded.',
         comps=['C1', 'C5']),

    dict(id='M1', inst='MIT', year=2020, short='Salinisation acts as an aridity enhancer',
         title='River basin salinization as a form of aridity',
         authors='Saverio Perri, Samir Suweis, Alex Holmes, Prashanth R. Marpu, Dara Entekhabi, Annalisa Molini',
         venue='Proceedings of the National Academy of Sciences 117(30), 17635–17642 (2020)',
         links=[('doi:10.1073/pnas.2005925117', 'https://doi.org/10.1073/pnas.2005925117')],
         evidence='Crossref affiliation string: Dara Entekhabi — Ralph M. Parsons Laboratory for Environmental '
                  'Science and Engineering, Massachusetts Institute of Technology.',
         does='**Result.** Combining observations and model results, the paper shows that soil salinisation affects '
              'the long-term soil–water balance of saline river basins and eventually acts as an aridity enhancer. '
              'The strength of this control depends on the ability of vegetation to cope with salt stress through '
              'functional traits, namely salt tolerance, and is key to vegetation–water relations in arid and '
              'transitional watersheds. The approach can also infer the salinisation level and vegetation salt '
              'tolerance of river basins, information needed for measures against catchment-scale aridity and '
              'salinisation based on salt-tolerant plant traits (abstract).',
         sota='Basin-scale evidence that soil salinisation acts as an aridity enhancer on the long-term water '
              "balance, with vegetation salt tolerance setting the strength of the effect, and a way to infer a "
              "basin's salinisation level and salt tolerance.",
         gap='It explains what salt does to the water balance, not where the salt comes from: salinisation by '
             'irrigation, by evaporation in a drought or by a shallow saline water table near the coast is not told '
             'apart, and pumping does not enter.',
         source='Salt that builds up in the soils of the recharge area is the pathway of both DRY and ANT, and a dry '
                'year adds to it; SWI and UP leave the soils untouched except where a saline water table lies close '
                'to the surface near the coast.',
         demand="Saline soils need extra water to leach the salt and, read through the paper's result, behave as "
                "drier land, so under ANT the farmers' claim on B is likely to grow with the salt: demand at B rises "
                'with the chloride problem itself.',
         stake='Salt-tolerant plants, which the paper points to as the basis of mitigation measures, give the farmers '
               'something to offer: a change of crop at B that needs less leaching water, credited to them in the '
               'ledger while ANT remains plausible.',
         step='Map soil salinisation over the recharge areas of A and B from vegetation salt stress, as the paper '
              "infers a basin's salinisation level and salt tolerance, and enter the footprint in y as a tracer with "
              'source-specific likelihoods (C1): salt on irrigated parcels at B for ANT, over the unirrigated '
              'recharge area of A and B for DRY, only on a coastal strip with a shallow saline water table for SWI, '
              'none for UP. The footprint can separate SWI from DRY, which Br/Cl alone may not since coastal '
              'recharge carries salt with a marine ratio, and C3 decides whether this cheap layer is worth buying '
              'before an isotope campaign. Test: on synthetic cases, compare the sources excluded per unit cost by '
              'the footprint, by Br/Cl and by both.',
         comps=['C1', 'C3']),

    dict(id='M2', inst='MIT', year=2023, short='Observed lags in the drought cascade',
         title='Propagation in the Drought Cascade: Observational Analysis Over the Continental US',
         authors='Dara Entekhabi',
         venue='Water Resources Research 59(9), e2022WR032608 (2023)',
         links=[('doi:10.1029/2022wr032608', 'https://doi.org/10.1029/2022wr032608')],
         evidence='Crossref affiliation string: Dara Entekhabi (sole author) — Ralph M. Parsons Laboratory for '
                  'Environmental Science and Engineering, Massachusetts Institute of Technology.',
         does='**Result.** Drought types, persistent deficits in meteorological, hydrological and ecological '
              'variables, are often linked in a cascade, here characterised over the continental US from remote '
              'sensing and in situ observations, with vegetation photosynthesis and above-ground biomass anomalies '
              'added to assess the role of the biosphere. Propagation between drought types is quantified as '
              'amplitude dampening and phase delays. Woody and herbaceous vegetation respond differently to '
              'prolonged soil-moisture deficit, traceable to their access to and storage of water and to water and '
              'light limitation. A prolonged precipitation deficit alone does not trigger intense soil-moisture and '
              'vegetation stress; excessive atmospheric evaporative demand must coincide with it (abstract).',
         sota='An observational, continental-scale measurement of how drought propagates from precipitation to soil '
              'moisture and vegetation, in amplitude and in time, usable both as a test of Earth System models and '
              'by practitioners concerned with drought impacts on water resources and ecosystem services.',
         gap='The cascade stops at soil moisture and vegetation; recharge, groundwater levels and the chloride of '
             'shallow wells, the links the DRY hypothesis needs, are not in it, so it cannot give the lag and '
             'damping with which a drought would reach the chloride at A and B.',
         source='Index droughts by the coincidence of precipitation deficit and high evaporative demand, not by '
                "rainfall alone: by the paper's finding, a dry spell without high evaporative demand may not stress "
                'the soil, and testing DRY against such events would wrongly weaken it.',
         demand='The compound condition that intensifies drought stress, low rain with high evaporative demand, is '
                'also when water demand peaks, so the allocation has to hold when drought-driven chloride and peak '
                'demand arrive together, not one at a time.',
         stake='Woody and herbaceous vegetation feel the same drought differently and on different time scales; by '
               'analogy the wetland at A and the crops at B bear their losses at different times, so the ledger '
               'should record when each party pays, not only how much.',
         step='Write the DRY likelihood as the next stage of the drought cascade: chloride at A and B is a damped, '
              'delayed response (gain and lag fitted on past droughts) to a compound index that is non-zero only '
              'when a precipitation deficit coincides with high evaporative demand, and deep C does not respond '
              '(C1). SWI predicts a drought response only at coastal A, through reduced outflow and with its own '
              'lag, and UP none, so each drought onset becomes a natural experiment for the monthly e-values (C4). '
              'Test: on simulated records, count the months after a drought onset until the false sources leave '
              '$S(y)$, with and without the evaporative-demand condition in the index.',
         comps=['C1', 'C4']),

    dict(id='M3', inst='MIT', year=2020, short='Climate adaptation as optimal control',
         title='Climate Adaptation as a Control Problem: Review and Perspectives on Dynamic Water Resources Planning '
               'Under Uncertainty',
         authors='Jonathan D. Herman, Julianne D. Quinn, Scott Steinschneider, Matteo Giuliani, Sarah Fletcher',
         venue='Water Resources Research 56(2), e24389 (2020)',
         links=[('doi:10.1029/2019wr025502', 'https://doi.org/10.1029/2019wr025502')],
         evidence='Crossref affiliation string: Sarah Fletcher — Department of Civil and Environmental Engineering, '
                  'Massachusetts Institute of Technology.',
         does='**Result.** A review that frames climate adaptation in water resources as an optimal control problem, '
              'with policies mapping future observations to actions, and classifies dynamic planning studies by '
              'uncertainty characterisation, policy structure and solution method. Characterising uncertainty is the '
              'central challenge that prevents an unambiguous use of control methods: exogenous uncertainty in '
              'forcing, model structure and parameters along chains of climate and hydrologic models, endogenous '
              'uncertainty in human–environmental dynamics, and sampling uncertainty from finite records and '
              'projections. Opportunities lie in uncertainty quantification and experimental design, out-of-sample '
              'validation and robustness of optimised policies, and monitoring and data assimilation (trend '
              'detection, Bayesian inference, indicator variable selection) (abstract).',
         sota='A classification of dynamic, observation-driven water planning under climate change as control '
              'problems, with an agenda that puts uncertainty characterisation, out-of-sample robustness and '
              'monitoring at the centre of adaptive policies.',
         gap='The uncertainty it classifies is mainly about climate forcing, models and records; a discrete unknown '
             'cause of degradation, with four rival sources each implying a different best action, cannot be '
             'resolved by waiting for the trigger variable, because rising chloride, the obvious trigger, looks '
             'the same under all four.',
         source='Treat the source as model-structure uncertainty and the tracer record as the monitoring signal of a '
                'control loop: the indicator to watch is not chloride, which rises under every hypothesis, but the '
                'variables whose trends differ by source (Br/Cl, isotopes, depth profiles, nitrate).',
         demand='A policy that maps observations to actions lets the utility commit now to a schedule of moves (for '
                'example, contract X when a threshold is crossed) instead of one fixed plan, so demand is met by '
                'agreed switches rather than emergency decisions.',
         stake='The negotiation moves from the action to the rule: stakeholders agree in advance which evidence '
               'triggers which move, which is easier in calm times than agreeing the move in a crisis, and the rule '
               'must be tested against how farmers and users respond to it.',
         step='Treat the plausible set as the state of a control policy: compute in advance the C2 allocation '
              '$x^*(S)$ for each of the 15 non-empty subsets S of {SWI, UP, DRY, ANT} and let the monthly e-values '
              '(C4) select the row in force; since the true source stays in $S(y)$ throughout with probability at '
              'least $1-\\beta$, monthly exceedance stays within $\\alpha+\\beta$ however often the policy switches. '
              "C3 then values a tracer test, the review's experimental-design question, by the cost the table saves "
              'over the horizon by reaching a smaller set earlier. Test out of sample, as the review recommends: on '
              'drought sequences and source mixtures not used to build the table, compare cost, switches and '
              'exceedance with a posterior-threshold policy.',
         comps=['C2', 'C3', 'C4']),

    dict(id='M4', inst='MIT', year=2026, short='From groundwater hazard to coastal risk',
         title="From Hydraulic Heads to Dollars and Decision: It's Time to Integrate Groundwater in Coastal Risk "
               'Assessment',
         authors='Daniel Gonzalez-Duque, Audrey H. Sawyer, Andrew J. Whittle, Michael V. Martello, Jason Cervenec, '
                 'Jayne Knott, David F. Boutt, Kelly Hereid',
         venue='Water Resources Research 62(5), e2025WR041035 (2026)',
         links=[('doi:10.1029/2025wr041035', 'https://doi.org/10.1029/2025wr041035')],
         evidence='Crossref affiliation strings: Andrew J. Whittle and Michael V. Martello — Department of Civil and '
                  'Environmental Engineering, Massachusetts Institute of Technology (MIT).',
         does='**Result.** A commentary on subsurface risk in coastal zones: sea-level rise brings rising groundwater '
              'tables, salinisation and subsurface flooding; shoaling groundwater inundates basements, tunnels and '
              'utility networks and mobilises contaminants, while salinisation accelerates corrosion and degrades '
              'water quality. Hydrogeologic studies increasingly assess these hazards, but few consider exposure and '
              'vulnerability to evaluate the overall risk that adaptation planning needs. The proposed path is '
              'local-scale risk analyses of specific infrastructure categories, scaling up through web-based coastal '
              'groundwater observatories and shared monitoring networks, and long-term digital twins combining '
              'real-time sensing, satellite data and machine learning to anticipate subsurface hazards at regional '
              'scale (abstract).',
         sota='An agenda that moves coastal groundwater science from hazard to risk, combining hazard with exposure '
              'and vulnerability, from hydraulic heads to dollars and decisions, delivered through local risk '
              'analyses, shared observatories and, later, digital twins.',
         gap='It treats salinisation as one hazard driven by sea-level rise; when chloride may also come from '
             'drought, upconing or return flow, the hazard is uncertain in kind, not only in size, and a single '
             'digital twin calibrated to one mechanism would report a precise but possibly wrong risk.',
         source='Log heads and salinity together at A, B and C and compare them with sea level, rainfall and '
                'pumping: each hypothesis predicts a different co-movement, while a network that records chloride '
                'alone cannot tell them apart.',
         demand='Count salinity damage to the supply system itself (corrosion of pumps, pipes and treatment, which '
                'the paper notes salinisation accelerates) as part of the cost of keeping A in service, not only '
                'the blend limit at the tap.',
         stake='Moving from heads to dollars gives each stakeholder a comparable figure: state the exceedance '
               'probability under each plausible source as an expected cost to the utility, households, farmers '
               'and the wetland, which is what the ledger of C5 needs.',
         step='Run the shared monitoring network the paper calls for as an evidence observatory: each data holder '
              "(the utility for A, B and C, the farmers' association for its wells at B, the environment agency for "
              'springs and piezometers at A) computes from its own data, with the four agreed source models and '
              'conditioning on all published data, a monthly e-value against each source, and the observatory '
              'publishes the merged evidence and $S(y)$ (C1, C5). Conditionally independent streams are merged by '
              'product, streams that may share water or errors by averaging their monthly factors, which stays '
              'valid under any dependence and keeps the anytime guarantee of C4. Test: on simulated correlated '
              'streams, averaging should keep the coverage of $S(y)$ at $1-\\beta$ where the naive product fails; '
              'measure the months of evidence it costs.',
         comps=['C1', 'C4', 'C5']),

    dict(id='M5', inst='MIT', year=2024, short='Legitimacy of self-made groundwater limits',
         title="Legitimacy in polycentric groundwater governance: Framework conditions identified in Nebraska's "
               'Natural Resource Districts',
         authors='Theresa Jedd, Gregory N. Sixt, Anthony Schutz, Mark Burbach',
         venue='Environmental Policy and Governance 35(2), 187–200 (2024)',
         links=[('doi:10.1002/eet.2132', 'https://doi.org/10.1002/eet.2132')],
         evidence='Crossref affiliation string: Gregory N. Sixt — Abdul Latif Jameel Water and Food Systems Lab, '
                  'Massachusetts Institute of Technology.',
         does='**Result.** The study asks how and why agricultural groundwater users would limit their own '
              'consumption, triangulating interviews, integrated management plans, workshop facilitation and '
              "recordings of legal proceedings on Nebraska's Natural Resources Districts. Voluntary arrangements "
              'rest on a legitimacy that stems from informal social processes: after decades of informal '
              'collaboration the districts first set voluntary extraction limits and later sanctioned '
              'over-consumption, and the rules are accepted because elected boards set them, leaders take part in a '
              'state-wide leadership training network and the state grants rule-making authority. Voluntary '
              'self-limiting can thus become the basis of binding legal requirements; social acceptance, inclusive '
              'membership, prior collaboration and understanding of self-made, context-specific rules are '
              'summarised in an evaluation framework (abstract).',
         sota='An evaluation framework, drawn from a case where voluntary irrigation limits became sanctioned rules, '
              'for testing whether authority in a polycentric groundwater arrangement is justified and accepted.',
         gap='In the case studied, limits were justified by water stress; here the farmers would be asked to cut '
             'pumping at B for a cause, return flow, that may not be the true one, and the framework does not say '
             'how legitimacy survives a contested diagnosis.',
         source='The farmers hold data the diagnosis needs (irrigation volumes, fertiliser practice, the chloride of '
                'their own wells at B) and are more likely to share it within a process they regard as legitimate; '
                'ANT cannot be tested well without them.',
         demand='Self-made rules can cost less than imposed ones: a cut the farmers design themselves, for example '
                'rotating which wells rest in the dry season, can free water at B at a lower loss to them than a '
                'uniform cut.',
         stake='Legitimacy is a design variable: the risk budget $\\delta$ and its split into $\\alpha$ and $\\beta$ '
               '(C5) should be set by a body that is elected, inclusive and understood, as the framework requires, '
               'not by the utility alone.',
         step="Let the farmers' board adopt in advance a three-stage rule tied to the plausible set: no limit at B "
              'once ANT is excluded ($E_{ANT}\\ge 1/\\beta$), a voluntary cut while ANT is one of several plausible '
              'sources, and a binding, sanctioned cut only when ANT is the only source left in $S(y)$ (C1, C5). '
              'Because the true source ever leaves $S(y)$ with probability at most $\\beta$ (C4), farmers are '
              'sanctioned under a false diagnosis, or released while ANT is true, with probability at most $\\beta$ '
              'each, a figure an elected board can understand and vote on. Test: simulate monthly records under '
              "each true source and compare wrongful sanctions and the farmers' expected loss with those of an "
              'unconditional cut at B.',
         comps=['C1', 'C4', 'C5']),

    dict(id='M6', inst='MIT', year=2024, short='Robust optimisation for yes/no uncertainty',
         title='Scenario-Based Robust Optimization for Two-Stage Decision Making Under Binary Uncertainty',
         authors='Kai Wang, Mehmet Aydemir, Alexandre Jacquillat',
         venue='INFORMS Journal on Optimization 6(2), 84–117 (2024)',
         links=[('doi:10.1287/ijoo.2020.0038', 'https://doi.org/10.1287/ijoo.2020.0038')],
         evidence='Crossref affiliation string: Alexandre Jacquillat — Sloan School of Management, Massachusetts '
                  'Institute of Technology.',
         does='**Result.** For two-stage optimisation under binary uncertainty, the paper defines a scenario-based '
              'robust optimisation (ScRO) formulation that combines probabilistic scenarios (stochastic optimisation) '
              'with protection against adversarial perturbations within discrete uncertainty sets (robust '
              'optimisation). A sparse row generation algorithm alternates a master problem (a lower bound from '
              'minimal uncertainty sets) and a history-based subproblem (an upper bound and updated sets); scenarios '
              'and sets come from element-wise probabilities (deviation likelihood) or historical samples (sample '
              'clustering). On public data sets the results suggest that the formulation, the generation methods '
              'and the algorithm outperform their benchmarks, and in a real-world ambulance dispatch case late '
              'responses can fall by more than 25% (abstract).',
         sota='A formulation between stochastic and robust optimisation for yes/no uncertainties, with probable '
              'scenarios each protected against adversarial deviations within a discrete set, a row-generation '
              'algorithm that bounds the optimum from below and above, and scenario sets built from probabilities '
              'or from historical samples.',
         gap='Its scenarios and sets come from given element-wise probabilities or past samples; nothing in it '
             'learns from new data which binary states remain plausible, and its protection holds against the '
             'chosen sets, not with a stated probability when those probabilities are wrong.',
         source='The four sources need not be exclusive: chloride at A can come from seawater and drought at once. '
                'Writing the source state as a yes/no vector of active sources, rather than one label, turns the '
                'diagnosis into the binary uncertainty this paper handles.',
         demand='The two-stage structure matches supply planning: contract X and drill or rest wells before the '
                'source is known (first stage), then set monthly pumping once monitoring results are in (second '
                'stage), sizing the first-stage commitment only for states still plausible.',
         stake='Report outcomes in the currency of the people affected, as the ambulance case counts late '
               'responses: here, the number of months with delivered chloride above 250 mg/L or with demand unmet.',
         step='Encode the source state as $z\\in\\{0,1\\}^4$ (SWI, UP, DRY, ANT active or not), with blend chloride '
              '$c_0(x)+\\sum_k z_k r_k(x)$ under allocation x, so mixtures such as SWI+DRY are allowed and C1 runs '
              'over the 15 composite hypotheses $z\\ne 0$; as chloride rises with each active source, the '
              'unrestricted worst case is all four at once. In a two-stage ScRO (first the X contract and well '
              'capacities, then monthly pumping once monitoring reveals z; C2), the planning prior only weights the '
              'scenario costs and the protected discrete set is $S(y)$, not a budget of $\\Gamma$ flips around a '
              'likely scenario. Test with mixtures and a deliberately wrong prior: the $\\Gamma$-budget plan can '
              'breach $\\alpha+\\beta$, the $S(y)$ plan should not, and their cost gap prices the prior-free '
              'guarantee.',
         comps=['C1', 'C2']),

    dict(id='M7', inst='MIT', year=2023, short='Uncertainty that depends on the decision',
         title='Robust Optimization with Continuous Decision-Dependent Uncertainty with applications to demand '
               'response management',
         authors='Hongfan (Kevin) Chen, Xu Andy Sun, Haoxiang Yang',
         venue='SIAM Journal on Optimization 33(3), 2406–2434 (2023)',
         links=[('doi:10.1137/22m1502082', 'https://doi.org/10.1137/22m1502082')],
         evidence='Crossref affiliation string: Xu Andy Sun (corresponding author) — Sloan School of Management, '
                  'Operations Research Center, Massachusetts Institute of Technology.',
         does='**Result.** The paper studies robust optimisation with continuous decision-dependent uncertainty '
              '(RO-CDDU): an uncertainty set that depends linearly on continuous decisions and a convex '
              'piecewise-linear objective. It proves the problem strongly NP-hard in general, reformulates it as an '
              'equivalent mixed-integer nonlinear program with a decomposable structure and, through the extreme '
              'points of the dual polyhedron of the uncertainty set, as a mixed-integer linear program, and proposes '
              'alternating-direction and column-generation algorithms. In robust demand-response management, where '
              "users' demand reduction is uncertain and depends on the planning decision, the algorithms perform "
              'well in speed and solution quality, and the results show how the magnitude of decision-dependent '
              'uncertainty affects the decision (abstract).',
         sota='Reformulations as an equivalent mixed-integer nonlinear program and then as a mixed-integer linear '
              'program through dual extreme points, two algorithms, and a strong NP-hardness proof, for robust '
              'problems whose uncertainty set moves linearly with continuous decisions.',
         gap='The set and its dependence on the decision are taken as known; in the aquifer, how chloride responds '
             'to pumping is exactly what differs between the source hypotheses, so the dependence itself is '
             'uncertain and has to be indexed by the source.',
         source='Pumping is both decision and discriminator: chloride at A rises with pumping at A under SWI, and at '
                "C with pumping at C under UP, while under DRY and ANT it does not follow the utility's pumping; the "
                'pumping–chloride slope, with drought held fixed, is a signature to estimate.',
         demand='Under DRY a cut in pumping buys no chloride reduction, so demand must be met by blending with C or '
                'by X; under SWI or UP the same cut buys a lot, so the cheapest way to meet demand depends on the '
                'source.',
         stake="Just as users' demand reduction in demand response is uncertain and depends on the planning "
               "decision, the farmers' response at B to a request to irrigate less depends on what they are "
               'offered; that response belongs inside the uncertainty set, not in a fixed parameter.',
         step='Take as uncertain the extra salt load $L_i$ each wellfield draws, so the blend limit '
              '$\\sum_i(c_iQ_i+L_i)\\le 250\\sum_iQ_i$ is linear, and give each $k\\in S(y)$ a set '
              '$U_k(x)=\\{L\\ge 0: A_kL\\le d_k+B_kx\\}$ in which pumping above a critical rate '
              '($s_A\\ge Q_A-q_A^*$, $s_C\\ge Q_C-q_C^*$, $s\\ge 0$) raises the load at A only under SWI and at C '
              "only under UP, while under DRY and ANT the load does not depend on the utility's pumping; pumping "
              'below $q^*$ thus switches SWI or UP off. With $P_k(L\\in U_k(x))\\ge 1-\\alpha$, robust feasibility '
              'implies the chance constraint of C2, and the problem has the RO-CDDU form (set linear in the '
              'decisions, convex piecewise-linear social cost) that the paper turns into a mixed-integer linear '
              "program via dual extreme points. Test: against a set fixed at today's pumping, measure the cost "
              'saved and the exceedances avoided, and trace how the optimal $Q_A$ rises when SWI leaves $S(y)$.',
         comps=['C2']),
]


ORDER = ['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9', 'O10', 'O11', 'O12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
         'H1', 'H2', 'H3', 'H4', 'H5', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
_ALL = {c['id']: c for c in [_O1] + _PART1 + _PART2 + _PART3}
CARDS = [_ALL[k] for k in ORDER]
for _c in CARDS:                                   # Crossref keeps U+2010 hyphens; the document uses plain ones
    for _k, _v in list(_c.items()):
        if isinstance(_v, str):
            _c[_k] = _v.replace('\u2010', '-')
INST_ORDER = ['Oxford', 'Caltech', 'Harvard', 'MIT']
