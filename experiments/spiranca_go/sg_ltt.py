"""What the fixed-sequence (Learn then Test) certificate of N2 costs on the safe yields of the assembled-system note:
reads experiments/montimi_go/res/qcrit_F_EVA.npz (critical rates of every layout on the complete assembly, 25
evaluation draws) and compares the order-statistic safe yield (Proposition G1 of that note) with the largest rate
certified at (alpha, delta). Output res/ltt.json"""
import os, sys, json
import numpy as np
from scipy.stats import binom
HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, '..', 'montimi_go')
sys.path.insert(0, MG)
import mg_setup as S

Q = np.load(os.path.join(MG, 'res', 'qcrit_F_EVA.npz'))['Q'][:len(S.EVA)]
assert np.all(np.isfinite(Q))
N, alpha = Q.shape[0], 0.10
names = [S.lay_name(L) for L in S.LAYOUTS]
value = lambda i, q: (1 - 0.2 * (S.LAYOUTS[i]['xs'] - S.XS[0]) / 1000) * q - (0.5 * S.QR if S.LAYOUTS[i]['xr'] is not None else 0)
qs = np.sort(Q, 0)
m = int(np.floor(alpha * N)) + 1
q_os = qs[m - 1]
v_os = np.array([value(i, q) for i, q in enumerate(q_os)])
out = dict(N=N, alpha=alpha, m=m, best_os=names[int(v_os.argmax())], q_os=float(q_os[v_os.argmax()]), v_os=float(v_os.max()), rows=[])
for delta in (0.10, 0.05):
    k = max([k for k in range(N) if binom.cdf(k, N, alpha) <= delta], default=-1)
    if k < 0:
        out['rows'].append(dict(delta=delta, allowed=-1, best=None, q=0.0, v=0.0, loss=1.0)); continue
    q_l = qs[k]
    v_l = np.array([value(i, q) for i, q in enumerate(q_l)])
    out['rows'].append(dict(delta=delta, allowed=k, best=names[int(v_l.argmax())], q=float(q_l[v_l.argmax()]), v=float(v_l.max()),
                            loss=float(1 - v_l.max() / v_os.max())))
out['draws_needed'] = []
for Nn in (25, 29, 50, 100, 200, 400):
    k = max([k for k in range(Nn) if binom.cdf(k, Nn, alpha) <= 0.10], default=-1)
    k5 = max([k for k in range(Nn) if binom.cdf(k, Nn, alpha) <= 0.05], default=-1)
    out['draws_needed'].append(dict(N=Nn, allowed_10=k, allowed_5=k5, order_stat=int(np.floor(alpha * Nn))))
json.dump(out, open(os.path.join(HERE, 'res', 'ltt.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
