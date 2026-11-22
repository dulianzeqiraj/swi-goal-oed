"""Crossref records of the context references of the review (not the thirty cards) -> res/refs_context.json"""
import json, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REFS = {
    'S1': '10.1111/j.1745-6584.1998.tb01099.x',      # Davis, Whittemore, Fabryka-Martin 1998, Cl/Br
    'S21': '10.1111/j.1745-6584.1998.tb01085.x',     # Sidauruk, Cheng, Ouazar 1998, source identification
    'S2': '10.1016/j.jhydrol.2008.06.028',           # Alcala & Custodio 2008, Cl/Br in Spain and Portugal
    'S3': '10.1016/j.advwatres.2012.03.004',         # Werner et al. 2013, seawater intrusion review
    'S4': '10.1007/s10040-009-0496-1',               # Custodio 2010, coastal aquifers of Europe
    'S5': '10.1201/9781439833544',                   # Appelo & Postma 2005, book
    'S6': '10.12681/bgsg.11772',                     # Cenameri & Beqiraj 2016, Fushe-Kuqe data
    'S7': '10.6028/jres.049.027',                    # Hoffman 1952
    'S8': '10.1002/nav.3800090303',                  # Charnes & Cooper 1962
    'S9': '10.1007/b97478',                          # Manski 2003, partial identification
    'S10': '10.1146/annurev.economics.050708.143401', # Tamer 2010
    'S11': '10.3982/ECTA8360',                       # Moon & Schorfheide 2012
    'S12': '10.1017/S0266466698144043',              # Poirier 1998
    'S13': '10.1017/S0962492910000061',              # Stuart 2010
    'S14': '10.1007/b138659',                        # Kaipio & Somersalo 2005
    'S15': '10.1007/978-94-009-1740-8',              # Engl, Hanke, Neubauer 1996
    'S16': '10.1007/b106715',                        # Vovk, Gammerman, Shafer 2005
    'S17': '10.1073/pnas.1912789117',                # Cranmer, Brehmer, Louppe 2020
    'S18': '10.1029/1999WR900190',                   # Neupauer & Wilson 1999
    'S19': '10.1109/MSP.2018.2877582',               # Fu, Huang, Sidiropoulos, Ma 2019, NMF identifiability
    'S20': '10.1016/B978-0-08-095975-7.00909-8',     # Vengosh 2014, salinization
    'S25': '10.1007/s00442-003-1218-3',              # Phillips & Gregg 2003, IsoSource
    'S26': '10.7717/peerj.5096',                     # Stock et al. 2018, MixSIAR
}
out = {}
for k, d in REFS.items():
    url = 'https://api.crossref.org/works/' + d
    req = urllib.request.Request(url, headers={'User-Agent': 'doc-builder/1.0'})
    for attempt in range(3):
        try:
            m = json.load(urllib.request.urlopen(req, timeout=40))['message']
            break
        except Exception as e:
            m = None; time.sleep(2)
    if m is None:
        print(k, d, 'NOT FOUND'); continue
    au = [dict(given=a.get('given', ''), family=a.get('family', a.get('name', ''))) for a in m.get('author', [])] or \
         [dict(given=a.get('given', ''), family=a.get('family', a.get('name', ''))) for a in m.get('editor', [])]
    y = (m.get('published-print') or m.get('published-online') or m.get('issued'))['date-parts'][0][0]
    out[k] = dict(doi=d, title=(m.get('title') or [''])[0], authors=au, year=y, journal=(m.get('container-title') or [''])[0],
                  volume=m.get('volume'), issue=m.get('issue'), page=m.get('page') or m.get('article-number'),
                  publisher=m.get('publisher'), type=m.get('type'))
    print(k, y, '|', '; '.join(a['family'] for a in au[:4]), '|', out[k]['title'][:90], '|', out[k]['journal'][:40], out[k]['volume'], out[k]['page'])
json.dump(out, open(os.path.join(HERE, 'res', 'refs_context.json'), 'w'), indent=1, ensure_ascii=False)
