"""State of the art and how the Action advances it: builds on -> what is missing (per decision) -> starting point
(preparatory results) -> advances that only a network can make. Content and references from the HALOMAR annex, 1.C.
Writes res/figS1_state_of_art.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
C_B, C_M, C_S, C_A = '#52606d', '#b03a3a', '#c27c12', '#1e8a5a'
FILL = {C_B: '#eceff3', C_M: '#fdecec', C_S: '#fff4e0', C_A: '#e6f5ee'}


def card(ax, x0, y0, w, h, title, body, col, fs=10.4, tfs=11.2, refs=None):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0.015,rounding_size=0.08', fc=FILL[col], ec=col, lw=1.5, zorder=1))
    ax.text(x0 + 0.12, y0 + h - 0.1, title, ha='left', va='top', fontsize=tfs, fontweight='bold', color=col, zorder=3)
    ax.text(x0 + 0.12, y0 + h - 0.42, body, ha='left', va='top', fontsize=fs, color=INK, zorder=3, linespacing=1.2)
    if refs:
        ax.text(x0 + 0.12, y0 + 0.08, refs, ha='left', va='bottom', fontsize=9.2, color=MUTED, style='italic', zorder=3, linespacing=1.15)


def main():
    W, H = 14.6, 10.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.32, 'State of the art: what the Action builds on, and how it advances it', ha='center', va='center', fontsize=16, fontweight='bold', color=INK)
    cols = [(0.2, 3.75, 'Builds on: mature, not re-done', C_B), (4.15, 2.95, 'What is missing', C_M),
            (7.35, 3.25, 'Starting point: preparatory\nresults at one aquifer', C_S), (10.85, 3.55, 'Advances only a\nnetwork can make', C_A)]
    for x0, w, t, c in cols:
        ax.add_patch(FancyBboxPatch((x0, 9.25), w, 0.7, boxstyle='round,pad=0.01,rounding_size=0.08', fc=c, ec='none'))
        ax.text(x0 + w / 2, 9.6, t, ha='center', va='center', fontsize=12, color='white', fontweight='bold', linespacing=1.1)

    # column 1: builds on
    top, gap = 9.1, 0.11
    items = [('Variable-density flow and transport', 'settled physics; community codes', 'Frind 1982; Huyakorn et al. 1987;\nDiersch & Kolditz 2002'),
             ('Optimal experimental design', 'A-, D- and goal-oriented design;\ngroundwater network design', 'Alexanderian et al. 2016; Nowak et al. 2010;\nHuan, Jagalur & Marzouk 2024'),
             ('Management of intrusion', 'simulation-optimisation;\nmanaged recharge standard', 'Kourakos & Mantoglou 2009;\nSreekanth & Datta 2010'),
             ('Hydrochemistry of intrusion', 'chloride tracer; cation exchange;\nreaction invariants', 'Appelo & Postma 2005; Lichtner 1985;\nRolle et al. 2013'),
             ('Learning control from data', 'how much data a learner needs;\nwhen logged data mislead', 'Ziemann & Sandberg 2021;\nRashidinejad et al. 2022'),
             ('European networks; COST Actions', 'harmonised observation;\nOFF-SOURCE, WATSON, SUSTAIN', 'CA21112, CA19120, CA22144;\nbuilds on COST 621')]
    hb = (top - 1.35 - gap * 5) / 6
    for k, (t, b, r) in enumerate(items):
        y0 = top - (k + 1) * hb - k * gap
        card(ax, 0.2, y0, 3.75, hb, t, b, C_B, fs=10.2, tfs=10.8, refs=r)

    # columns 2 and 3: per decision
    dec = [('Observing the front',
            'well rankings are approximations;\nno way to tell if two teams\nreally disagree',
            'one budget for monitoring and\nrecharge; a certificate bounds each\nwell; toe at 1 km, not 0.8 or 1.1'),
           ('Reading the chemistry',
            'model reactive chemistry or\nignore it, at an unknown cost',
            'chloride-only forecast: 15% less\nprecise, immune to chemistry\nerrors; coverage 72% → 98%'),
           ('Recharging',
            'heads cannot separate recharge\nfrom model error',
            '12 chosen samples cut chloride\nforecast error 17.7 → 4.1 mg/L;\nuncertainty split by source'),
           ('Pumping',
            'rules learned from records: years\nneeded unknown; records mislead',
            'about 21 years of records for a 1%\nmargin; half with toe records;\na recorded variation exposes errors'),
           ('Status',
            'intrusion test is a judgement; no\nprotocol tested for agreement',
            'no preparatory result: the\nprotocol and its blind test\nare new work (RC5)')]
    hd = (top - 1.35 - gap * 4) / 5
    for k, (t, miss, start) in enumerate(dec):
        y0 = top - (k + 1) * hd - k * gap
        card(ax, 4.15, y0, 2.95, hd, t, miss, C_M, fs=10.2, tfs=11)
        card(ax, 7.35, y0, 3.25, hd, t, start, C_S, fs=10.2, tfs=11)
        ax.annotate('', xy=(7.32, y0 + hd / 2), xytext=(7.12, y0 + hd / 2), arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=1.8, mutation_scale=15))

    # column 4: advances
    adv = [('1. Cross-site distributions', 'structure threshold, price of a\nchloride-only design, chemical leak,\nyears of records, across karst,\nalluvial and deltaic aquifers'),
           ('2. Refereed comparison', 'information-based siting against\nmulti-criteria practice, by\nindependent teams on the same\naquifers, scored on agreed goals'),
           ('3. Procedures authorities run', 'one per decision, each with a\nminimal version without adjoint\nsolvers or geochemical models,\nand a statement of its cost'),
           ('4. A status test that agrees', 'two authorities apply it\nindependently and must agree;\nthe test is reported whichever\nway it falls')]
    ha_ = (top - 1.35 - gap * 3) / 4
    for k, (t, b) in enumerate(adv):
        y0 = top - (k + 1) * ha_ - k * gap
        card(ax, 10.85, y0, 3.55, ha_, t, b, C_A, fs=10.4, tfs=11.2)
    # big arrows between column 1 -> 2 and 3 -> 4
    for xa, xb in ((3.97, 4.13), (10.62, 10.83)):
        ax.annotate('', xy=(xb, 5.2), xytext=(xa, 5.2), arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=3, mutation_scale=24))

    # bottom strip: what is not claimed
    ax.add_patch(FancyBboxPatch((0.2, 0.2), W - 0.4, 0.95, boxstyle='round,pad=0.015,rounding_size=0.1', fc='#1f3864', ec='none'))
    ax.text(W / 2, 0.675, 'Not claimed: a new information criterion, solver, geochemical model, learning algorithm or recharge technology.\n'
            'The advance is coupling the four decisions through common goals, transferability tested across sites, and procedures authorities can run.',
            ha='center', va='center', fontsize=11.5, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figS1_state_of_art.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
