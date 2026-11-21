"""Fetches the Crossref record of every reference of the review and writes res/refs.json (key -> record).
usage: python fetch_refs.py     (needs network access to api.crossref.org; the stored file is used by text_kaos.py)"""
import html
import json
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'res', 'refs.json')
DOIS = dict(
    A1='10.1126/sciadv.abj2619', A2='10.1017/jfm.2020.122', A3='10.1017/jfm.2023.337', A4='10.1073/pnas.2320962121',
    A5='10.1103/PhysRevFluids.6.033304',
    S1='10.1007/BF01036523', S2='10.3233/ASY-1989-2302', S3='10.1017/S0022112091001258', S4='10.1007/978-94-009-6175-3_4',
    S5='10.1017/S002211209700671X', S6='10.1016/j.compfluid.2016.05.030', S7='10.1146/annurev-fluid-010719-060317',
    S8='10.1017/jfm.2015.9', S9='10.1103/PhysRevLett.111.174101', S10='10.1016/j.advwatres.2016.09.007',
    S11='10.1073/pnas.2002858117', S12='10.1017/jfm.2020.113', S13='10.1103/PhysRevLett.126.034505',
    S14='10.1017/jfm.2025.10477', S15='10.1017/jfm.2025.10551', S16='10.1029/2018WR023864', S17='10.1029/2019WR025982',
    S18='10.1007/s11242-022-01852-x', S19='10.1073/pnas.2111651118', S20='10.1103/PhysRevLett.124.164501',
    S21='10.1103/PhysRevFluids.5.013801', S22='10.3389/frwa.2021.671399', S23='10.1103/PhysRevE.104.035106',
    S24='10.1029/2023GL104473', S25='10.1038/s42005-022-00826-1', S26='10.1103/PhysRevResearch.7.L012032',
    S27='10.1103/PhysRevLett.132.188301', S28='10.1098/rspa.2020.0111', S29='10.1140/epje/s10189-023-00390-8',
    S30='10.1017/S0022112099007545', S31='10.1007/s00440-020-00983-w', S32='10.1002/nla.2296', S33='10.1214/10-AOP571',
    S34='10.1143/JPSJ.12.570', S35='10.1063/5.0112998', S36='10.1214/09-AOS735', S37='10.1214/24-AOS2408',
    S38='10.1214/23-AOS2276', S39='10.3402/tellusa.v52i5.12283', S40='10.1090/cams/10', S41='10.1098/rspa.2020.1004',
    S42='10.1073/pnas.2101784118', S43='10.1137/24M1692393', S44='10.1061/TACEAT.0006033', S45='10.1007/s10040-015-1312-8',
    S46='10.1016/0301-9322(82)90029-5', S47='10.1103/PhysRevE.65.046308', S48='10.4208/cicp.2008.v3.p427',
    S49='10.1007/BF02128236', S50='10.1007/s11242-012-0070-5', S51='10.1103/PhysRevE.94.053118', S52='10.3390/e18110409',
    S53='10.1029/2020WR028100', S54='10.1007/s11242-021-01586-2', S55='10.1038/s41598-021-83065-8',
    S56='10.1007/s11242-023-02012-5', S57='10.1002/2015GL065423', S58='10.1038/s41467-022-31552-5',
    S59='10.1093/biomet/62.1.57', S60='10.1214/ss/1177009939', S61='10.1111/j.1467-9868.2010.00740.x',
)


def fetch(doi):
    for _ in range(5):
        r = subprocess.run(['curl', '-sS', '--max-time', '60', '-A', 'doc-builder/1.0', 'https://api.crossref.org/works/' + doi],
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout)['message']
        except Exception:
            time.sleep(3)
    return None


def main():
    refs = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for key, doi in DOIS.items():
        if key in refs and refs[key].get('doi', '').lower() == doi.lower():
            continue
        m = fetch(doi)
        if not m:
            print('FAILED', key, doi); continue
        au = [dict(family=a.get('family') or a.get('name') or '?', given=a.get('given', '')) for a in m.get('author', [])]
        year = None
        for f in ('published-print', 'issued', 'published-online', 'published'):
            dp = (m.get(f) or {}).get('date-parts', [[None]])[0]
            if dp and dp[0]:
                year = dp[0]; break
        title = html.unescape(re.sub(r'<[^>]+>', '', (m.get('title') or ['?'])[0])); title = ' '.join(title.split())
        refs[key] = dict(doi=m['DOI'], authors=au, year=year, title=title,
                         journal=html.unescape((m.get('container-title') or [''])[0]), volume=m.get('volume'),
                         issue=m.get('issue'), page=m.get('page') or m.get('article-number'), type=m.get('type'),
                         publisher=m.get('publisher'))
        print(key, year, refs[key]['journal'][:40], '|', title[:70], '|', len(au), 'authors')
        json.dump(refs, open(OUT, 'w'), ensure_ascii=False, indent=1)
        time.sleep(0.25)
    print(len(refs), 'records')


if __name__ == '__main__':
    main()
