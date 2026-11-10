"""Figures for OPERATORI-GO from operatori_results.json.

usage: python operatori_figs.py operatori_results.json OUTDIR"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

NAVY, BLUE, ORANGE, GREEN, GREY = '#1F3864', '#2E6DB4', '#D9822B', '#3A8F5C', '#6B7785'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titlesize': 9, 'axes.titleweight': 'bold'})


def fig1(r, out):
    c = r['check1']
    rows = [x for x in c['rows'] if x['modes_needed'] > 0]
    xs = [x['x'] for x in rows]
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 2.9))
    a = ax[0]
    a.semilogy(xs, [x['modes_needed'] for x in rows], 'o-', color=NAVY, label='needed (exact, KL basis)')
    a.semilogy(xs, [x['prop_a_modes'] for x in rows], 's--', color=ORANGE, label='Proposition A (sufficient)')
    a.axhline(c['d99_input_pca'], color=GREY, ls=':', label='usual PCA: 99 % of input variance')
    a.axvline(c['shell_width'], color=GREEN, lw=1)
    a.text(c['shell_width'] - 0.005, 2.0, 'edge of the\nstochastic shell', color=GREEN, ha='right', fontsize=7.5)
    a.set_xlabel('distance from the sea, x / L'); a.set_ylabel('boundary modes to keep')
    a.set_title('(a) Input dimension is set by the aquifer'); a.set_ylim(1, 3000)
    a.legend(frameon=False, fontsize=7, loc='lower left')
    b = ax[1]
    pr = c['shell_profile_ranks']
    lab = [f"{p['rms_tolerance']:g}" for p in pr]
    ix = range(len(pr))
    b.bar([i - 0.18 for i in ix], [p['input_kl_modes'] for p in pr], width=0.34, color=GREY, label='input PCA (KL) modes')
    b.bar([i + 0.18 for i in ix], [p['optimal_rank'] for p in pr], width=0.34, color=NAVY,
          label='operator-weighted modes (optimal)')
    for i, p in zip(ix, pr):
        b.text(i - 0.18, p['input_kl_modes'] * 1.08, str(p['input_kl_modes']), ha='center', fontsize=7)
        b.text(i + 0.18, p['optimal_rank'] * 1.08, str(p['optimal_rank']), ha='center', fontsize=7)
    b.set_yscale('log'); b.set_ylim(1, 600)
    b.set_xticks(list(ix)); b.set_xticklabels(lab); b.set_xlabel('RMS tolerance on the heads in the shell (× s)')
    b.set_ylabel('modes'); b.set_title('(b) Choose input modes by the operator')
    b.legend(frameon=False, fontsize=7, loc='upper left')
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def fig2(r, out):
    c2, c3 = r['check2'], r['check3']
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 2.9))
    a = ax[0]
    N = [x['N'] for x in c2['learned']]
    a.loglog(N, [x['rms_error'] for x in c2['learned']], 'o-', color=ORANGE, label='learned (PCA-Net, linear map)')
    a.axhline(c2['computed_rms_error'], color=NAVY, label=f"computed from {c2['computed_runs']} model runs")
    a.axvline(c2['du'], color=GREY, ls=':', lw=1)
    a.text(120, 0.3, f"dotted: N = {c2['du']},\nthe number of modes", color=GREY, fontsize=7)
    a.set_xlabel('training runs N'); a.set_ylabel('RMS head error, x ≥ 0.1 (× s)')
    a.set_title('(a) Linear boundary: compute, do not learn'); a.legend(frameon=False, fontsize=7)
    b = ax[1]
    st = {'linear (no cap)': ('-', 'linear boundary map'), 'capped recharge': ('--', 'capped recharge (kink)')}
    for name, (ls, lab) in st.items():
        rows = c3['results'][name]
        N = [x['N'] for x in rows]
        b.loglog(N, [x['linear_pca_net'] for x in rows], ls, marker='o', ms=3, color=BLUE, label=f'{lab}: linear PCA-Net')
        b.loglog(N, [x['relu_pca_net'] for x in rows], ls, marker='s', ms=3, color=ORANGE, label=f'{lab}: ReLU PCA-Net')
    n0 = 100
    e0 = c3['results']['capped recharge'][0]['relu_pca_net']
    b.loglog([n0, 20000], [e0, e0 * (20000 / n0)**-0.5], ':', color=GREY, label='N^(-1/2) reference')
    b.text(110, 0.0062, 'cap applied to the input, then the\nlinear operator: exact (error 0)', color=GREEN, fontsize=7)
    b.set_ylim(0.005, 1.5)
    b.set_xlabel('training runs N'); b.set_ylabel('relative error of the heads')
    b.set_title('(b) A kink slows learning'); b.legend(frameon=False, fontsize=6.3, loc='upper center', ncol=1)
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def main(res, outdir):
    r = json.load(open(res))
    os.makedirs(outdir, exist_ok=True)
    fig1(r, os.path.join(outdir, 'operatori_fig1.png'))
    fig2(r, os.path.join(outdir, 'operatori_fig2.png'))
    print('saved figures in', outdir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
