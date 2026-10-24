"""KUJTESA-GO, part (iv) of Proposition U: the value is slow, the pumping rule is fast.

The greedy pumping gain computed from a value matrix P is K(P) = gamma (R + gamma B^T P B)^{-1} B^T P A. To first order
its error is dK = gamma (R + gamma B^T P B)^{-1} B^T E A_cl, with E = P - P*. Pumping acts on the head only (B = -beta
e_h), so the slow clay mode reaches the gain through l_s^T B, the head component of its left eigenvector, which is small
when the slow mode is weakly controllable. This script measures, for the value-iteration errors E_k of part 1 (exact,
from P_0 = 0 and from the physics potential), the relative error of P_cc and of the greedy gain on each state, and the
modal weights. Writes kujtesa_policy.json and appends to kujtesa_policy.log.
"""
import json
import os

import numpy as np

import kujtesa as k

HERE = os.path.dirname(os.path.abspath(__file__))


def run():
    g = k.P['gamma']
    A, B, W, Q, R = k.system()
    K, Pric = k.lqr_discounted(A, B, Q, R, g)
    Acl = A - B @ K
    Qcl = Q + K.T @ R @ K
    Pv = k.value_matrix(Acl, Qcl, g)
    mu, V = k.modal(Acl)
    Vi = np.linalg.inv(V)
    left = np.real(Vi[0] / np.linalg.norm(Vi[0]))
    left = left * np.sign(left[3])
    right = np.real(V[:, 0] / np.linalg.norm(V[:, 0]))
    right = right * np.sign(right[3])
    # controllability of each mode through the head: |l_i^T B| with unit left eigenvectors
    ctrl = [float(abs(Vi[i] @ B[:, 0]) / np.linalg.norm(Vi[i])) for i in range(4)]
    A2 = A.copy(); A2[3, 3] = k.P['a_c'] - k.P['phys_err']
    Pphi = k.value_matrix(A2 - B @ K, Qcl, g)

    def greedy(Pm):
        return g * np.linalg.solve(R + g * B.T @ Pm @ B, B.T @ Pm @ A)[0]

    out = dict(left_slow=left.tolist(), right_slow=right.tolist(), ctrl=ctrl, K=K[0].tolist())
    for name, P0 in [('FVI', np.zeros_like(Pv)), ('FVI, physics shaping', Pphi)]:
        M = P0.copy(); pcc, gain = [], []
        for it in range(k.P['outer']):
            M = Qcl + g * Acl.T @ M @ Acl
            pcc.append(float(abs(M[3, 3] - Pv[3, 3]) / abs(Pv[3, 3])))
            gain.append((np.abs(greedy(M) - K[0]) / np.abs(K[0])).tolist())
        gain = np.array(gain)
        first = int(np.argmax(np.all(gain < 0.01, axis=1))) + 1
        out[name] = dict(pcc=pcc, gain=gain.tolist(), first_all_gains_1pct=first, pcc_at_first=pcc[first - 1],
                         gain_c_at_25=float(gain[24, 3]), pcc_at_25=pcc[24])
    json.dump(out, open(os.path.join(HERE, 'kujtesa_policy.json'), 'w'), indent=1)
    f = out['FVI']
    txt = (f'unit left eigenvector of the slow mode on (m, h, X, c): {np.round(left, 4)}; right: {np.round(right, 4)}\n'
           f'controllability through the head |l_i^T B| (unit left eigenvectors): {np.round(ctrl, 4)}\n'
           f'policy evaluation from zero: greedy gain within 1% on every state after {f["first_all_gains_1pct"]} updates, '
           f'when the relative error of P_cc is still {f["pcc_at_first"]:.3f}; at 25 updates P_cc error {f["pcc_at_25"]:.3f}, '
           f'gain error on c {f["gain_c_at_25"]:.4f}\n'
           f'with physics shaping: all gains within 1% after {out["FVI, physics shaping"]["first_all_gains_1pct"]} updates')
    open(os.path.join(HERE, 'kujtesa_policy.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
