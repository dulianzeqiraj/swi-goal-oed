"""Compact reference list for the e-COST References field (max 500 words): every work the Technical Annex cites,
without titles, journal abbreviations, up to three authors written out (as in the annex citations). Same verified data
as refs_data.py. Writes a Word file (Arial 11) and a plain-text copy, and prints the word count."""
import sys
from docx import Document
from docx.shared import Pt, Cm

SCI = [
    'Abarca E et al. (2007) Adv. Water Resour. 30, 913–926. doi:10.1016/j.advwatres.2006.08.005',
    'Alexanderian A, Gloor PJ, Ghattas O (2016a) Bayesian Anal. 11, 671–695. doi:10.1214/15-BA969',
    'Alexanderian A et al. (2016b) SIAM J. Sci. Comput. 38, A243–A272. doi:10.1137/140992564',
    'Alexanderian A (2021) Inverse Probl. 37, 043001. doi:10.1088/1361-6420/abe10c',
    'Appelo CAJ, Postma D (2005) Geochemistry, Groundwater and Pollution, 2nd ed. Balkema. doi:10.1201/9781439833544',
    'Attia A, Alexanderian A, Saibaba AK (2018) Inverse Probl. 34, 095009. doi:10.1088/1361-6420/aad210',
    'Barber D, Agakov F (2003) Adv. Neural Inf. Process. Syst. 16, 201–208.',
    'Boudreau BP, Meysman FJR, Middelburg JJ (2004) Earth Planet. Sci. Lett. 222, 653–666. doi:10.1016/j.epsl.2004.02.034',
    'Diersch H-JG, Kolditz O (2002) Adv. Water Resour. 25, 899–944. doi:10.1016/S0309-1708(02)00063-5',
    'Foster A et al. (2019) Adv. Neural Inf. Process. Syst. 32, 14036–14047.',
    'Frind EO (1982) Adv. Water Resour. 5, 73–88. doi:10.1016/0309-1708(82)90049-5',
    'Huan X, Jagalur J, Marzouk Y (2024) Acta Numer. 33, 715–840. doi:10.1017/S0962492924000023',
    'Huyakorn PS et al. (1987) Water Resour. Res. 23, 293–312. doi:10.1029/WR023i002p00293',
    'Kourakos G, Mantoglou A (2009) Adv. Water Resour. 32, 507–521. doi:10.1016/j.advwatres.2009.01.001',
    'Koval K, Herzog R, Scheichl R (2024) Inverse Probl. 40, 125002. doi:10.1088/1361-6420/ad8260',
    'Krause A, Singh A, Guestrin C (2008) J. Mach. Learn. Res. 9, 235–284.',
    'Lal A, Datta B (2019) Int. J. Environ. Res. Public Health 16, 4365. doi:10.3390/ijerph16224365',
    'Leube PC, Geiges A, Nowak W (2012) Water Resour. Res. 48, W02501. doi:10.1029/2010WR010137',
    'Lichtner PC (1985) Geochim. Cosmochim. Acta 49, 779–800. doi:10.1016/0016-7037(85)90172-3',
    'Lykkegaard MB, Dodwell TJ (2022) Adv. Water Resour. 164, 104219. doi:10.1016/j.advwatres.2022.104219',
    'Nemhauser GL, Wolsey LA, Fisher ML (1978) Math. Program. 14, 265–294. doi:10.1007/BF01588971',
    'Neuberger JN, Alexanderian A, van Bloemen Waanders B (2025) J. Sci. Comput. 105, 55. doi:10.1007/s10915-025-03073-y',
    'Nowak W, de Barros FPJ, Rubin Y (2010) Water Resour. Res. 46, W03535. doi:10.1029/2009WR008312',
    'Pauw PS et al. (2015) Hydrogeol. J. 23, 1415–1430. doi:10.1007/s10040-015-1264-z',
    'Plummer M (2015) Stat. Comput. 25, 37–43. doi:10.1007/s11222-014-9503-z',
    'Pool M, Carrera J (2010) Hydrogeol. J. 18, 95–105. doi:10.1007/s10040-009-0516-1',
    'Rainforth T et al. (2024) Stat. Sci. 39, 100–114. doi:10.1214/23-STS915',
    'Rashidinejad P et al. (2022) IEEE Trans. Inf. Theory 68, 8156–8196. doi:10.1109/TIT.2022.3185139',
    'Rolle M et al. (2013) Geochim. Cosmochim. Acta 120, 195–205. doi:10.1016/j.gca.2013.06.031',
    'Saaltink MW, Ayora C, Carrera J (1998) Water Resour. Res. 34, 1649–1656. doi:10.1029/98WR00552',
    'Simpson MJ, Clement TP (2004) Water Resour. Res. 40, W01504. doi:10.1029/2003WR002199',
    'Sreekanth J, Datta B (2010) J. Hydrol. 393, 245–256. doi:10.1016/j.jhydrol.2010.08.023',
    'Wagenmaker AJ, Simchowitz M, Jamieson K (2021) Proc. ICML, PMLR 139, 10641–10652.',
    'Wöhling T, Geiges A, Nowak W (2016) Groundwater 54, 861–870. doi:10.1111/gwat.12430',
    'Yoon S et al. (2020) Adv. Water Resour. 135, 103468. doi:10.1016/j.advwatres.2019.103468',
    'Ziemann I, Sandberg H (2021) Proc. L4DC, PMLR 144, 213–226.',
]
OTHER = [
    'Directive 2000/60/EC, OJ L 327, 22.12.2000.',
    'Directive (EU) 2026/805, OJ L 2026/805, 20.4.2026.',
    'European Commission (2025) European Water Resilience Strategy, COM(2025) 280 final.',
    'Directive 2007/2/EC (INSPIRE), OJ L 108, 25.4.2007.',
    'OGC (2017) GroundWaterML 2, OGC 16-032r2.',
    'IGRAC, Global Inventory of Managed Aquifer Recharge Schemes, ggis.un-igrac.org.',
    'COST Actions CA21112, CA19120, CA22144 and 621, cost.eu.',
]


def main(out='HALOMAR_References_500words.docx'):
    import re
    def compact(l):
        l = re.sub(r' doi:\S+$', '', l)                          # no DOI
        l = re.sub(r'^([^,(]+?), [^()]+? \((\d{4}[ab]?)\)', lambda m: (m.group(1) + ' et al. (' + m.group(2) + ')') if m.group(0).count(',') >= 2 else m.group(0), l)  # 3+ authors -> et al.
        l = re.sub(r'(\w+)–\w+\.$', r'\1.', l)                  # first page only
        return l
    lines = [compact(l) for l in SCI]
    words = sum(len(l.split()) for l in lines)
    text = '\n'.join(lines)
    strict = len(re.findall(r'\w+', text)); ecost = len(re.findall(r'[^\s/–\-:]+', text))
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(2.0)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    for l in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.6)
        r = p.add_run(l); r.font.name = 'Arial'; r.font.size = Pt(11)
    doc.save(out)
    open(out.replace('.docx', '.txt'), 'w').write('\n'.join(lines) + '\n')
    print('entries', len(lines), 'words (spaces)', words, '| e-COST-like', ecost, '| strictest', strict)


if __name__ == '__main__':
    main(*(sys.argv[1:2]))
