"""Shared style and helpers for the figures of the M-estimator review (white background, no black)."""
import json
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
FIG = os.path.join(HERE, 'figures')
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# Okabe-Ito, colour-blind safe; ink and rules in dark and mid grey instead of black
OI = dict(blue='#0072B2', vermillion='#D55E00', green='#009E73', purple='#CC79A7', orange='#E69F00',
          sky='#56B4E9', yellow='#F0E442')
INK = '#3a3f44'
MUTED = '#6b7178'
RULE = '#b9bec4'
GRID = '#e6e9ec'
MM = 1 / 25.4

mpl.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 7.2, 'axes.titlesize': 7.6, 'axes.labelsize': 7.2,
    'xtick.labelsize': 6.6, 'ytick.labelsize': 6.6, 'legend.fontsize': 6.4,
    'text.color': INK, 'axes.labelcolor': INK, 'axes.edgecolor': RULE, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.linewidth': 0.6, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'xtick.major.size': 2.5,
    'ytick.major.size': 2.5, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True,
    'grid.color': GRID, 'grid.linewidth': 0.5, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 'legend.frameon': False, 'lines.linewidth': 1.3, 'mathtext.fontset': 'dejavusans',
    'axes.titleweight': 'normal', 'axes.titlelocation': 'left', 'patch.edgecolor': 'white',
})


def panel(ax, letter, x=-0.14, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=8.6, fontweight='bold', color=INK, va='bottom', ha='left')


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(FIG, f'{name}.{ext}'), dpi=400 if ext == 'png' else None, bbox_inches='tight',
                    pad_inches=0.04)
    plt.close(fig)


def dump(obj, name):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(os.path.join(RES, name), 'w') as f:
        json.dump(obj, f, indent=1, default=conv)


def mc_band(p, n, z=1.96):
    """Wilson interval for a Monte Carlo proportion."""
    p = np.asarray(p, float)
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h
