"""Crossref records of the references of the WRR draft -> res/refs_wrr.json (bibliographic data from Crossref only)."""
import json, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
DOIS = {
 'phillips2003': '10.1007/s00442-003-1218-3', 'stock2018': '10.7717/peerj.5096', 'phillips2014': '10.1139/cjz-2014-0127',
 'christophersen1992': '10.1029/91WR02518', 'hooper2003': '10.1029/2002WR001528', 'genereux1998': '10.1029/98WR00010',
 'barthold2011': '10.1029/2011WR010604', 'parnell2010': '10.1371/journal.pone.0009672', 'moore2008': '10.1111/j.1461-0248.2008.01163.x',
 'davis1998': '10.1111/j.1745-6584.1998.tb01099.x', 'alcala2008': '10.1016/j.jhydrol.2008.06.028', 'werner2013': '10.1016/j.advwatres.2012.03.004',
 'vengosh2014': '10.1016/B978-0-08-095975-7.00909-8', 'panno2006': '10.1111/j.1745-6584.2005.00127.x', 'katz2011': '10.1016/j.jhydrol.2010.11.017',
 'land2004': '10.3133/sir20045067', 'vengosh2005': '10.1029/2004WR003344', 'piper1953': '10.3133/wsp1136', 'hem1985': '10.3133/wsp2254',
 'craig1961': '10.1126/science.133.3465.1702', 'dansgaard1964': '10.3402/tellusa.v16i4.8993', 'stark1992': '10.1029/92JB00739',
 'stark2015': '10.1137/130920721', 'oldenburg1983': '10.1029/JB088iB09p07387', 'manski2003': '10.1007/b97478',
 'tamer2010': '10.1146/annurev.economics.050708.143401', 'imbens2004': '10.1111/j.1468-0262.2004.00555.x',
 'poirier1998': '10.1017/S0266466698144043', 'moon2012': '10.3982/ECTA8360', 'gustafson2015': '10.1201/b18308',
 'charnes1962': '10.1002/nav.3800090303', 'hoffman1952': '10.6028/jres.049.027', 'farkas1902': '10.1515/crll.1902.124.1',
 'tarantola2005': '10.1137/1.9780898717921', 'stuart2010': '10.1017/S0962492910000061', 'neupauer1999': '10.1029/1999WR900190',
 'chaloner1995': '10.1214/ss/1177009939', 'zeqiraj2026': '10.1016/j.jhydrol.2026.136559', 'huangfu2018': '10.1007/s12532-017-0130-5',
 'virtanen2020': '10.1038/s41592-019-0686-2', 'izbicki1996': '10.3133/fs12596', 'post2013': '10.1038/nature12858',
}
out = {}
for k, d in DOIS.items():
    req = urllib.request.Request('https://api.crossref.org/works/' + d, headers={'User-Agent': 'doc-builder/1.0'})
    m = None
    for a in range(3):
        try:
            m = json.load(urllib.request.urlopen(req, timeout=40))['message']; break
        except Exception as e:
            err = str(e); time.sleep(1.5)
    if m is None:
        print('NOT FOUND', k, d, err); continue
    au = [dict(given=a.get('given', ''), family=a.get('family', a.get('name', ''))) for a in m.get('author', [])] or \
         [dict(given=a.get('given', ''), family=a.get('family', a.get('name', ''))) for a in m.get('editor', [])]
    y = (m.get('published-print') or m.get('published-online') or m.get('issued'))['date-parts'][0][0]
    out[k] = dict(doi=d, title=(m.get('title') or [''])[0], authors=au, year=y, journal=(m.get('container-title') or [''])[0],
                  volume=m.get('volume'), issue=m.get('issue'), page=m.get('page') or m.get('article-number'),
                  publisher=m.get('publisher'), type=m.get('type'))
    print(k, y, '|', '; '.join(a['family'] for a in au[:3]), '|', out[k]['title'][:80], '|', out[k]['journal'][:35], out[k]['volume'], out[k]['page'])
json.dump(out, open(os.path.join(HERE, 'res', 'refs_wrr.json'), 'w'), indent=1, ensure_ascii=False)
