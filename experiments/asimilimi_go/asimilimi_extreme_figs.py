"""Figure A3 of ASIMILIMI-GO (extreme events) from res/extreme.json and res/extreme_trace.json."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'res', 'extreme.json')))
T = json.load(open(os.path.join(HERE, 'res', 'extreme_trace.json')))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e3e6ea', 'grid.linewidth': 0.6, 'axes.edgecolor': '#9aa3ad'})
INK, MUTED = '#1f2328', '#5b6573'
S = J['E8_E11']
FIL = [('heads + gauge + spikes / Gaussian', 'Gaussian (best single model)', '#8a8f98'),
       ('heads + gauge + spikes / IMM', 'regimes, no spike model', '#eb6834'),
       ('heads + gauge + spikes / IMM + spike model', 'regimes + spike model', '#1baf7a'),
       ('heads + gauge / IMM', 'regimes, data without spikes', '#2a78d6')]
GR = [('sea anomaly', 'surge', 'sea level\n(surge days)'), ('head 50 m from the sea', 'surge', 'head 50 m from sea\n(surge days)'),
      ('recharge anomaly', 'drought', 'recharge\n(drought days)'), ('E', 'drought', 'pumping E\n(drought days)'),
      ('E', 'normal', 'pumping E\n(normal days)')]

fig, ax = plt.subplots(2, 2, figsize=(11.2, 7.8))
a = ax[0, 0]
w = 0.2
x = np.arange(len(GR))
for i, (k, lab, col) in enumerate(FIL):
    v = [S[k]['coverage'][g][p] for g, p, _ in GR]
    a.bar(x + (i - 1.5) * w, v, w * 0.92, color=col, edgecolor='white', linewidth=1.0, label=lab)
a.axhline(0.9, color=INK, lw=1, ls=':')
a.set_xticks(x); a.set_xticklabels([t for _, _, t in GR], fontsize=7.6)
a.set_ylim(0, 1.32); a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]); a.set_ylabel('coverage of 90% intervals (60 twins)')
a.set_title('(a) Calibration in extremes: heads, tide gauge and sensor spikes', loc='left', fontsize=9.5)
a.legend(frameon=False, fontsize=7.2, loc='upper center', ncol=2)

b = ax[0, 1]
for key, col, lab in (('heads', '#7d4fc9', 'four piezometers'), ('heads + gauge', '#2a78d6', 'piezometers + tide gauge')):
    rows = J['E10'][key]['rows']
    am = [r['amplitude'] for r in rows]
    b.plot(am, [r['predicted'] for r in rows], '-', color=col, lw=1.8, label=f'{lab}: Theorem 9')
    b.plot(am, [r['empirical'] for r in rows], 'o', color=col, ms=5, mfc='white', mew=1.6, label=f'{lab}: 4,000 twins')
b.axhline(0.001 * 6, color=MUTED, lw=0.8, ls=':')
b.text(0.05, 0.05, 'false-alarm level for 6 days', fontsize=7.5, color=MUTED)
b.set_xscale('log'); b.set_xlabel('surge amplitude a (m)'); b.set_ylabel('probability of an alarm within 6 days')
b.set_ylim(-0.03, 1.05)
b.set_title('(b) The alarm: power predicted before any data', loc='left', fontsize=9.5)
b.legend(frameon=False, fontsize=7.2, loc='center left', bbox_to_anchor=(0.16, 0.5))

t = np.arange(T['days'])
G_, I_ = T['filters']['heads + gauge + spikes / Gaussian'], T['filters']['heads + gauge + spikes / IMM + spike model']
ev = np.array(T['events']); amp = np.array(T['amps'])
ok = [(e, a_) for e, a_ in zip(ev, amp) if 15 <= e < T['days'] - 25 and not (T['d0'] - 5 <= e <= T['d1'] + 5)]
e0 = max(ok, key=lambda z: z[1])[0] if ok else ev[np.argmax(amp)]
lo, hi = e0 - 6, e0 + 18
c = ax[1, 0]
trh = np.array(T['truth']['head 50 m from the sea'])
c.axhspan(-1.645, 1.645, color='#e6f6ef', lw=0)
c.axhline(1.645, color=MUTED, lw=0.8, ls=':'); c.axhline(-1.645, color=MUTED, lw=0.8, ls=':')
for f, col, lab in ((G_, '#8a8f98', 'Gaussian'), (I_, '#1baf7a', 'regimes + spike model')):
    z = (np.array(f['h50']) - trh) / np.array(f['h50_sd'])
    c.plot(t[lo:hi], z[lo:hi], '-o', color=col, ms=3.2, lw=1.8, label=lab)
c.axvline(e0, color='#2a78d6', lw=1.0, ls='--', label='surge onset (%.2f m)' % float(amp[list(ev).index(e0)]))
sp = sorted({d for d, i in T['spikes'] if lo <= d < hi})
for k, d in enumerate(sp):
    c.axvline(d, color='#b9471a', lw=0.9, ls='--', label='a sensor spike' if k == 0 else None)
c.text(lo + 0.3, -2.15, '90% band of a calibrated filter (shaded)', fontsize=7.5, color='#11805a')
c.set_ylim(-2.45, 6.4)
c.set_xlabel('day'); c.set_ylabel('error / posterior standard deviation')
c.set_title('(c) One surge: error of the head 50 m from the sea (never measured)', loc='left', fontsize=9.5)
c.legend(frameon=False, fontsize=7.2, loc='upper right', ncol=2)

d = ax[1, 1]
trE = np.array(T['truth']['E'])
for f, col, lab in ((G_, '#8a8f98', 'Gaussian'), (I_, '#1baf7a', 'regimes + spike model')):
    m = np.array(f['E']); s = np.array(f['E_sd'])
    d.fill_between(t, m - 1.645 * s, m + 1.645 * s, color=col, alpha=0.18, lw=0)
    d.plot(t, m, color=col, lw=1.6, label=lab)
d.plot(t, trE, color=INK, lw=1.4, label='truth')
d.axvspan(T['d0'], T['d1'], color='#eda100', alpha=0.10, lw=0)
d.text((T['d0'] + T['d1']) / 2, d.get_ylim()[1] * 0.92 if d.get_ylim()[1] > 0 else 0, 'drought', ha='center', fontsize=8, color='#8f6200')
d.set_xlabel('day'); d.set_ylabel('unlicensed pumping E (m³/d per km)')
d.set_title('(d) A drought: E jumps by 300 and is found in about two weeks', loc='left', fontsize=9.5)
d.legend(frameon=False, fontsize=7.2, loc='upper left')
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'res', 'figA3_extreme.png'), dpi=200)
print('wrote res/figA3_extreme.png; surge shown at day', int(e0))
