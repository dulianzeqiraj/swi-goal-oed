"""Collect the paper cards of the CERTAIN-COAST state-of-the-art series, filled with their numbers, in one schema.

Each review of the series keeps its cards in experiments/<name>_go/cards_<name>.py; some card fields carry
placeholders (<<key>>) that the review's own text module fills from its results (res/*.json) when the review is
built. This module runs each review's blocks(...) with the same result files as its builder and takes the filled
cards from the blocks it returns, so the complete state of the art carries the same numbers as each review.

usage: python complete_sota_cards.py OUT.json"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, '..', '..'))
GAR = os.path.join(EXP, 'garancia_go', 'res')


def _load(path, name):
    d = os.path.dirname(path)
    if d not in sys.path:
        sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _json(*parts):
    with open(os.path.join(*parts), encoding='utf-8') as fh:
        return json.load(fh)


# review key -> (folder, text module, result files for blocks(...), roman label, title)
REVIEWS = [
    ('I', 'garancia_go', 'text_gar', lambda d: (_json(d, 'res', 'gar_exp.json'), _json(d, 'res', 'gar_rcps.json'),
                                                 _json(d, 'res', 'gar_rainc.json')),
     'Inputs, dispersion and boundary conditions from rain alone, with guarantees (GUARANTEE-GO)'),
    ('II', 'matja_go', 'text_matja', lambda d: (_json(d, 'res', 'matja.json'), _json(d, 'res', 'matja_spur.json'),
                                                 _json(GAR, 'gar_exp.json'), _json(GAR, 'gar_rcps.json')),
     'What a measurement is worth (MEASURE-GO)'),
    ('III', 'reshja_go', 'text_reshja', lambda d: (_json(d, 'res', 'reshja.json'), _json(GAR, 'gar_exp.json')),
     'Rain uncertainty (PRECIPITATION-GO)'),
    ('IV', 'ankora_go', 'text_ankora', lambda d: (_json(d, 'res', 'ankora.json'), _json(GAR, 'gar_exp.json')),
     'Simulator shift and anchors (MOORING-GO)'),
    ('V', 'prirja_go', 'text_prirja', lambda d: (_json(d, 'res', 'prirja.json'), _json(GAR, 'gar_exp.json')),
     'Drift and horizon guarantees (TREND-GO)'),
    ('VI', 'dyshemeja_go', 'text_dyshemeja', lambda d: (_json(d, 'res', 'dyshemeja.json'), _json(GAR, 'gar_exp.json')),
     'The floor of optimality (FLOOR-GO)'),
    ('VII', 'shkaku_go', 'text_shkaku', lambda d: (_json(d, 'res', 'shkaku.json'), _json(d, 'res', 'shkaku_sign.json')),
     'Counterfactuals and stochastic causality (CAUSE-GO)'),
    ('VIII', 'kripa_go', 'text_kripa', lambda d: (_json(d, 'res', 'kripa.json'),),
     'Salinity counterfactuals (SALT-GO)'),
    ('IX', 'fshehta_go', 'text_fshehta', lambda d: (_json(d, 'res', 'fshehta.json'),),
     'Hidden confounders of pumping and salinity (HIDDEN-GO)'),
    ('S', 'prejardhja_go', 'text_prejardhja', lambda d: (_json(d, 'res', 'prejardhja.json'),),
     'Stakeholder decisions when the source of the chloride is unknown (ORIGIN-GO)'),
]


def _cards_in(obj, out):
    if isinstance(obj, dict):
        if 'id' in obj and 'title' in obj and ('does' in obj or 'done' in obj):
            out.append(obj)
            return
        for v in obj.values():
            _cards_in(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _cards_in(v, out)


def collect():
    res = {}
    for key, folder, text_mod, args, title in REVIEWS:
        d = os.path.join(EXP, folder)
        try:
            m = _load(os.path.join(d, text_mod + '.py'), f'txt_{folder}')
            bl = m.blocks(*args(d))
            found = []
            _cards_in(bl, found)
            seen, cards = set(), []
            for c in found:
                if c['id'] in seen:
                    continue
                seen.add(c['id'])
                cards.append(c)
            how = 'filled by blocks()'
        except Exception as e:                       # fall back to the raw cards (placeholders stay marked)
            cm = [f for f in os.listdir(d) if f.startswith('cards_') and f.endswith('.py') and '_ox' not in f][0]
            cards = list(_load(os.path.join(d, cm), f'cards_{folder}').CARDS)
            how = f'raw cards ({type(e).__name__}: {str(e)[:80]})'
        left = sum(1 for c in cards for v in c.values() if isinstance(v, str) and '<<' in v)
        novelty = []
        try:
            for b in bl:
                if isinstance(b, (list, tuple)) and b and b[0] == 'box':
                    for x in b[1:]:
                        for y in ([x] if isinstance(x, str) else (x if isinstance(x, (list, tuple)) else [])):
                            if isinstance(y, str):
                                novelty.append(y)
        except NameError:
            pass
        res[key] = dict(title=title, folder=folder, how=how, cards=cards, novelty=novelty)
        print(f'{key:5s} {len(cards):3d} cards  {how}  | fields with placeholders left: {left}')
    return res


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'complete_sota_cards.json'
    R = collect()
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(R, fh, ensure_ascii=False, indent=0, default=str)
    print('saved', out)
