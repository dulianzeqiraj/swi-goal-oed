"""MONTIMI-GO analysis: margins, safe yields, the chosen layouts and how they fare on the full assembly.
Reads res/stage1.json, res/qcrit_*.npz, res/calib.npz, res/stage4.json; writes res/montimi.json (all numbers quoted
in the note)."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S

RES = os.path.join(HERE, 'res')
BETA = 0.10
LAMBDA_C = 0.20      # value lost per km of conveyance inland of 2 km (relative to a cubic metre delivered at 2 km)
LAMBDA_R = 0.50      # price of a cubic metre of recharged water, in the same units
NAMES = [S.lay_name(L) for L in S.LAYOUTS]


def value(li, Q, lc=LAMBDA_C, lr=LAMBDA_R):
    L = S.LAYOUTS[li]
    return (1.0 - lc * (L['xs'] - S.XS[0]) / 1000.0) * Q - (lr * S.QR if L['xr'] is not None else 0.0)


def qstar(Q, alpha=S.ALPHA):
    """safe yield per layout: the m-th smallest critical rate over the draws (Proposition G1)."""
    out = []
    for col in Q.T:
        v = np.sort(col[np.isfinite(col)])
        m = int(np.floor(alpha * len(v))) + 1
        out.append(float(v[m - 1]))
    return np.array(out)


def conformal(r, beta=BETA):
    r = np.sort(np.asarray(r))
    k = int(np.ceil((1 - beta) * (len(r) + 1)))
    return float(r[min(k, len(r)) - 1])


def main():
    out = dict(beta=BETA, lambda_c=LAMBDA_C, lambda_r=LAMBDA_R, alpha=S.ALPHA, layouts=NAMES)
    st1 = json.load(open(os.path.join(RES, 'stage1.json')))
    out['stage1'] = st1
    QF = np.load(os.path.join(RES, 'qcrit_F_EVA.npz'))
    QFe = QF['Q'][:len(S.EVA)]; ok = np.all(np.isfinite(QFe), axis=1); QFe = QFe[ok]
    out['n_eval'] = int(QFe.shape[0])
    QsF = qstar(QFe)
    vF = np.array([value(i, q) for i, q in enumerate(QsF)])
    iF = int(np.argmax(vF))
    out['F'] = dict(qstar=QsF.tolist(), value=vF.tolist(), best=NAMES[iF], best_q=float(QsF[iF]), best_value=float(vF[iF]),
                    cpu_per_draw=float(np.median(QF['cpu'][QF['cpu'] > 0])), runs_per_qcrit=float(np.mean(QF['nev'][:len(S.EVA)][ok])))
    cal = np.load(os.path.join(RES, 'calib.npz')) if os.path.exists(os.path.join(RES, 'calib.npz')) else None
    out['assemblies'] = {}
    for A in ('G', 'U', 'S', 'N'):
        fn = os.path.join(RES, f'qcrit_{A}_DES.npz')
        if not os.path.exists(fn):
            continue
        D = np.load(fn)
        QA = D['Q'][:len(S.DES)]; okA = np.all(np.isfinite(QA), axis=1)
        QA = QA[okA]
        r = None; m = 0.0
        if cal is not None:
            Qfull = np.load(fn)['Q']
            inr = cal['draw'] < Qfull.shape[0]
            QAc = np.where(inr, Qfull[np.minimum(cal['draw'], Qfull.shape[0] - 1), cal['layout']], np.nan)
            good = np.isfinite(QAc) & np.isfinite(cal['QF'])
            r = (QAc - cal['QF'])[good]
            m = conformal(r)
        res = {}
        for tag, marg in (('nomargin', 0.0), ('withmargin', m if r is not None else 0.0)):
            Qs = np.maximum(qstar(QA) - marg, 0.0)
            vA = np.array([value(i, q) for i, q in enumerate(Qs)])
            i = int(np.argmax(vA))
            risk = float(np.mean(QFe[:, i] < Qs[i] - 1e-9))
            res[tag] = dict(qstar=Qs.tolist(), best=NAMES[i], best_q=float(Qs[i]), value_promised=float(vA[i]),
                            realised_risk=risk, F_safe_q_of_choice=float(QsF[i]), F_value_of_choice=float(vF[i]),
                            layout_loss=float(vF[iF] - vF[i]), overpump=float(Qs[i] - QsF[i]),
                            safe_on_F=bool(risk <= S.ALPHA + 1e-9))
            # sweep of the conveyance price: does the assembly choose the full assembly's layout?
            agree = []
            for lc in (0.0, 0.1, 0.2, 0.3, 0.4):
                vFl = np.array([value(k, q, lc) for k, q in enumerate(QsF)])
                vAl = np.array([value(k, q, lc) for k, q in enumerate(Qs)])
                agree.append(dict(lambda_c=lc, F=NAMES[int(np.argmax(vFl))], A=NAMES[int(np.argmax(vAl))],
                                  risk=float(np.mean(QFe[:, int(np.argmax(vAl))] < Qs[int(np.argmax(vAl))] - 1e-9)),
                                  loss=float(vFl.max() - vFl[int(np.argmax(vAl))])))
            res[tag]['sweep'] = agree
        rank_corr = float(np.corrcoef(np.argsort(np.argsort(qstar(QA))), np.argsort(np.argsort(QsF)))[0, 1])
        res.update(margin=m, residuals=(r.tolist() if r is not None else None), n_design=int(QA.shape[0]),
                   cpu_per_draw=float(np.median(D['cpu'][D['cpu'] > 0])), runs_per_qcrit=float(np.mean(D['nev'][:len(S.DES)][okA])),
                   rank_corr_qstar=rank_corr, mean_abs_diff_qstar=float(np.mean(np.abs(qstar(QA) - QsF))))
        out['assemblies'][A] = res
        print(A, 'margin %.3f' % m, {t: (res[t]['best'], round(res[t]['best_q'], 2), round(res[t]['realised_risk'], 3)) for t in ('nomargin', 'withmargin')})
    print('F best', out['F']['best'], round(out['F']['best_q'], 2))
    if os.path.exists(os.path.join(RES, 'stage4.json')):
        st4 = json.load(open(os.path.join(RES, 'stage4.json')))
        out['stage4'] = st4
        toe = st4['toe']
        # toe as a proxy: per layout, threshold on the toe tuned to the same exceedance frequency as the screen event
        tp = {}
        for name in sorted(set(t['layout'] for t in toe)):
            rows = [t for t in toe if t['layout'] == name]
            ev = np.array([t['J'] > M.EPS_LIM for t in rows]); X = np.array([t['toeH'] for t in rows])
            k = max(int(ev.sum()), 1)
            thr = np.sort(X)[::-1][k - 1]
            pred = X >= thr
            tp[name] = dict(freq=float(ev.mean()), toe_thr=float(thr), agree=float(np.mean(pred == ev)),
                            hits=int(np.sum(pred & ev)), events=int(ev.sum()),
                            corr_toe_J=float(np.corrcoef(X, [t['J'] for t in rows])[0, 1]),
                            tau_median=float(np.median([t['tau_yr'] for t in rows if np.isfinite(t['tau_yr'])])),
                            gamma_median=float(np.median([t['gamma'] for t in rows if t['gamma'] is not None])),
                            r2_median=float(np.median([t['r2'] for t in rows])), law_err_median=float(np.median([t['toe_law_err_m'] for t in rows])),
                            toeH_median=float(np.median(X)), toe0_median=float(np.median([t['toe0'] for t in rows])))
        out['toe_proxy'] = tp
    json.dump(out, open(os.path.join(RES, 'montimi.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
