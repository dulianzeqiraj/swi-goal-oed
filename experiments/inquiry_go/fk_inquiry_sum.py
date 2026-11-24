"""Outcome sets and decisive shares of the Fushe-Kuqe run of INQUIRY-GO.
usage: python fk_inquiry_sum.py      res/fk_inquiry_raw.json -> res/fk_inquiry.json   (field results, not committed)"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
K = 2.5
SD = {'cl': (0.05, 1.0), 'br': (0.05, 0.005)}          # relative and absolute error
FLOOR = {'cl': 1.0, 'br': 0.005}                       # mg/L, lower end of the logarithmic axis
SRC = {'MS': 'the sea', 'RS': 'legacy salinity', 'DB': 'deep water', 'SQ': 'the squeeze of the cover'}


def consistent(kind, lo, hi):
    rel, ab = SD[kind]
    return (lo - K * ab) / (1.0 + K * rel), (hi + K * ab) / (1.0 - K * rel)


def merge(iv):
    iv = sorted((a, b) for a, b in iv if b > a)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def inter(A, B):
    out = []
    for a, b in A:
        for c, d in B:
            lo, hi = max(a, c), min(b, d)
            if hi > lo:
                out.append([lo, hi])
    return merge(out)


def diff(A, B):
    out = []
    for a, b in A:
        cur = a
        for c, d in B:
            if d <= cur or c >= b:
                continue
            if c > cur:
                out.append([cur, c])
            cur = max(cur, d)
        if cur < b:
            out.append([cur, b])
    return merge(out)


def length(A):
    return float(sum(b - a for a, b in A))


def main():
    tag = '7' if os.environ.get('FK_SEVEN', '0') == '1' else ''
    raw = json.load(open(os.path.join(HERE, 'res', f'fk_inquiry{tag}_raw.json')))
    Q, runs = raw['questions'], raw['raw']
    out = dict(n=len(runs), questions=Q, verdicts={}, nan=int(sum(r['nan'] for r in runs)),
               seconds=float(sum(r['sec'] for r in runs)))
    for wn, src in raw['verdicts']:
        key = f'{wn}:{src}'
        fy = [r['v'][key]['feas']['yes'] for r in runs]; fn = [r['v'][key]['feas']['no'] for r in runs]
        V = dict(well=wn, source=src, n_yes_only=int(sum(a and not b for a, b in zip(fy, fn))),
                 n_no_only=int(sum(b and not a for a, b in zip(fy, fn))), n_both=int(sum(a and b for a, b in zip(fy, fn))),
                 q=[])
        for iq, q in enumerate(Q):
            kind = 'br' if q['kind'] == 'br' else 'cl'
            fl = FLOOR[kind]
            O = {'yes': [], 'no': []}
            for r in runs:
                for c, iv in r['v'][key]['rng'][iq].items():
                    a, b = consistent(kind, iv[0], iv[1])
                    O[c].append([np.log10(max(a, fl)), np.log10(max(b, fl * 1.0001))])
            Y, N = merge(O['yes']), merge(O['no'])
            U, B = merge(Y + N), inter(Y, N)
            d = (1.0 - length(B) / length(U)) if (Y and N and length(U) > 0) else None
            back = lambda A: [[float(10 ** a), float(10 ** b)] for a, b in A]  # noqa: E731
            V['q'].append(dict(delta=(None if d is None else float(d)), yes=back(Y), no=back(N), only_yes=back(diff(Y, N)), only_no=back(diff(N, Y)),
                               both=back(B), n_yes=len(O['yes']), n_no=len(O['no'])))
        V['open'] = bool(any(fy) and any(fn))
        if V['open']:
            new = [v['delta'] for v, q in zip(V['q'], Q) if q['kind'] == 'new']
            V['mean_new'] = float(np.mean(new)); V['best'] = int(np.argmax([v['delta'] for v in V['q']]))
        out['verdicts'][key] = V
    json.dump(out, open(os.path.join(HERE, 'res', f'fk_inquiry{tag}.json'), 'w'), indent=1)
    return out


def show(out):
    Q = out['questions']
    print('simulations', out['n'], '| programmes not finished', out['nan'], '| cpu %.0f s' % out['seconds'])
    for key, V in out['verdicts'].items():
        print(f"\n== {key}: yes only {V['n_yes_only']}, no only {V['n_no_only']}, both {V['n_both']}, open {V['open']}"
              + (f", mean decisive share of a new sample {V['mean_new']:.2f}" if V['open'] else ''))
        if not V['open']:
            continue
        order = np.argsort([-v['delta'] for v in V['q']])
        for i in order[:7]:
            v = V['q'][i]
            f = lambda A: ' + '.join(f'{a:.3g}-{b:.3g}' for a, b in A) or '-'  # noqa: E731
            print(f"   {v['delta']:.2f}  {Q[i]['label']:42s} yes-only {f(v['only_yes'])} | no-only {f(v['only_no'])} | both {f(v['both'])}")


if __name__ == '__main__':
    show(main())
